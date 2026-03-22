import { useCallback, useEffect, useRef, useState } from "react";
import { AlertCircle, Bot, MessageCircle, Plus, RotateCcw, Send, Trash2, User, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { aiAPI, getCurrentUser } from "@/services/api";
import { useI18n } from "@/i18n/I18nProvider";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status?: "pending" | "failed" | "sent";
}

const SESSION_STORAGE_KEY = "hw_ai_chat_session_id";
const HISTORY_PAGE_SIZE = 50;

const makeId = (prefix: string) => `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
const getSessionStorageKey = () => {
  const userId = getCurrentUser()?.id ?? "guest";
  return `${SESSION_STORAGE_KEY}:${userId}`;
};

export function ChatWidget() {
  const { language, direction } = useI18n();

  const copy =
    language === "ar"
      ? {
          greeting: "مرحبا! أنا مساعدك الذكي في هنا وادينا. كيف يمكنني مساعدتك؟",
          error: "عذرا، حدث خطأ. حاول مرة أخرى.",
          prepare: "جاري تجهيز المحادثة...",
          aria: "مساعد ذكي",
          title: "المساعد الذكي",
          subtitle: "هنا وادينا",
          placeholder: "اكتب سؤالك...",
          newChat: "محادثة جديدة",
          endChat: "إنهاء",
          retry: "إعادة المحاولة",
          failedSend: "فشل الإرسال",
          confirmEnd: "هل تريد إنهاء المحادثة الحالية ومسحها؟",
        }
      : {
          greeting: "Hi! I am your smart assistant in Hena Wadeena. How can I help you?",
          error: "Sorry, something went wrong. Please try again.",
          prepare: "Preparing chat session...",
          aria: "AI assistant",
          title: "AI Assistant",
          subtitle: "Hena Wadeena",
          placeholder: "Type your question...",
          newChat: "New Chat",
          endChat: "End",
          retry: "Retry",
          failedSend: "Failed to send",
          confirmEnd: "Do you want to end and clear the current chat session?",
        };

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(() => {
    try {
      return localStorage.getItem(getSessionStorageKey());
    } catch {
      return null;
    }
  });
  const endRef = useRef<HTMLDivElement>(null);

  const persistSession = (id: string) => {
    setSessionId(id);
    try {
      localStorage.setItem(getSessionStorageKey(), id);
    } catch {
      // Ignore local storage errors and keep in-memory session.
    }
  };

  const clearSessionLocal = () => {
    setSessionId(null);
    try {
      localStorage.removeItem(getSessionStorageKey());
    } catch {
      // Ignore local storage errors.
    }
  };

  const sessionMessageToUi = useCallback((id: string, role: string, content: string): ChatMessage => {
    return {
      id,
      role: role === "user" ? "user" : "assistant",
      content,
      status: "sent",
    };
  }, []);

  const createSession = useCallback(
    async (seedGreeting = false) => {
      const user = getCurrentUser();
      const res = await aiAPI.createSession({
        user_id: user?.id ?? null,
        language_preference: language === "ar" ? "ar" : "en",
        metadata: { source: "frontend-widget" },
      });
      persistSession(res.data.session_id);

      if (seedGreeting) {
        const welcome = res.data.welcome_message?.trim() || copy.greeting;
        setMessages([sessionMessageToUi(makeId("welcome"), "assistant", welcome)]);
      }

      return res.data.session_id;
    },
    [copy.greeting, language, sessionMessageToUi]
  );

  const hydrateSession = useCallback(
    async (id: string) => {
      const res = await aiAPI.getSession(id, 1, HISTORY_PAGE_SIZE);
      const history = res.data.messages.map((msg) => sessionMessageToUi(msg.message_id, msg.role, msg.content));
      setMessages(
        history.length ? history : [sessionMessageToUi(makeId("greeting"), "assistant", copy.greeting)]
      );
      return true;
    },
    [copy.greeting, sessionMessageToUi]
  );

  const initializeChat = useCallback(async () => {
    if (initializing) return;
    setInitializing(true);

    try {
      if (sessionId) {
        try {
          await hydrateSession(sessionId);
          return;
        } catch {
          clearSessionLocal();
          setMessages([]);
        }
      }

      await createSession(true);
    } catch {
      setMessages([sessionMessageToUi(makeId("init-error"), "assistant", copy.error)]);
    } finally {
      setInitializing(false);
    }
  }, [copy.error, createSession, hydrateSession, initializing, sessionId, sessionMessageToUi]);

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId;
    return createSession();
  }, [createSession, sessionId]);

  const sendMessage = useCallback(
    async (retryMessageId?: string, retryText?: string) => {
      if (sending || initializing) return;

      const value = (retryText ?? input).trim();
      if (!value) return;

      if (!retryMessageId) {
        setInput("");
      }

      const userMessageId = retryMessageId ?? makeId("user");
      if (retryMessageId) {
        setMessages((prev) =>
          prev.map((msg) => (msg.id === retryMessageId ? { ...msg, status: "pending" } : msg))
        );
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: userMessageId,
            role: "user",
            content: value,
            status: "pending" as const,
          },
        ]);
      }

      setSending(true);
      try {
        const activeSessionId = await ensureSession();
        const res = await aiAPI.sendMessage(activeSessionId, {
          content: value,
          language: language === "ar" ? "ar" : "en",
        });

        setMessages((prev) => {
          const withConfirmedUser = prev.map((msg) =>
            msg.id === userMessageId ? { ...msg, status: "sent" as const } : msg
          );
          return [
            ...withConfirmedUser,
            {
              id: res.data.message_id,
              role: "assistant",
              content: res.data.content,
              status: "sent" as const,
            },
          ];
        });
      } catch {
        setMessages((prev) =>
          prev.map((msg) => (msg.id === userMessageId ? { ...msg, status: "failed" as const } : msg))
        );
      } finally {
        setSending(false);
      }
    },
    [ensureSession, initializing, input, language, sending]
  );

  const closeActiveSession = useCallback(async () => {
    const activeId = sessionId;
    clearSessionLocal();
    setMessages([]);
    setInput("");

    if (!activeId) return;
    try {
      await aiAPI.closeSession(activeId);
    } catch {
      // Session cleanup is best-effort and can fail if already closed.
    }
  }, [sessionId]);

  const handleNewChat = useCallback(async () => {
    if (sending || initializing) return;
    setInitializing(true);
    const previousSessionId = sessionId;
    clearSessionLocal();
    setMessages([]);
    setInput("");

    try {
      if (previousSessionId) {
        await aiAPI.closeSession(previousSessionId);
      }
    } catch {
      // Ignore close errors and continue creating a fresh session.
    }

    try {
      await createSession(true);
    } catch {
      setMessages([sessionMessageToUi(makeId("new-chat-error"), "assistant", copy.error)]);
    } finally {
      setInitializing(false);
    }
  }, [copy.error, createSession, initializing, sending, sessionId, sessionMessageToUi]);

  const handleEndChat = useCallback(async () => {
    if (!window.confirm(copy.confirmEnd)) return;
    await closeActiveSession();
    setOpen(false);
  }, [closeActiveSession, copy.confirmEnd]);

  useEffect(() => {
    if (!open) return;
    if (messages.length > 0 || initializing) return;
    void initializeChat();
  }, [initializeChat, initializing, messages.length, open]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending, initializing]);

  return (
    <>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="fixed bottom-6 left-6 z-50 h-14 w-14 rounded-full bg-primary text-white shadow-xl transition-all hover:scale-110 hover:bg-primary/90"
        aria-label={copy.aria}
      >
        <span className="flex h-full w-full items-center justify-center">
          {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
        </span>
      </button>

      {open && (
        <div className="fixed bottom-24 left-6 z-50 flex max-h-[540px] w-[360px] flex-col overflow-hidden rounded-2xl border border-border/50 bg-background shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="flex items-center justify-between gap-2 bg-gradient-to-l from-primary to-primary/80 px-4 py-3 text-white">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <div>
                <p className="text-sm font-bold">{copy.title}</p>
                <p className="text-xs text-white/70">{copy.subtitle}</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                type="button"
                size="icon"
                variant="ghost"
                onClick={handleNewChat}
                disabled={sending || initializing}
                className="h-8 w-8 text-white hover:bg-white/20 hover:text-white"
                aria-label={copy.newChat}
                title={copy.newChat}
              >
                <Plus className="h-4 w-4" />
              </Button>
              <Button
                type="button"
                size="icon"
                variant="ghost"
                onClick={handleEndChat}
                disabled={sending || initializing}
                className="h-8 w-8 text-white hover:bg-white/20 hover:text-white"
                aria-label={copy.endChat}
                title={copy.endChat}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="max-h-[330px] flex-1 space-y-3 overflow-y-auto p-4" dir={direction}>
            {initializing && messages.length === 0 && (
              <div className="rounded-xl bg-muted px-3 py-2 text-sm text-muted-foreground">{copy.prepare}</div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                <div
                  className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${
                    msg.role === "user" ? "bg-primary/10" : "bg-accent/30"
                  }`}
                >
                  {msg.role === "user" ? (
                    <User className="h-4 w-4 text-primary" />
                  ) : (
                    <Bot className="h-4 w-4 text-accent-foreground" />
                  )}
                </div>

                <div className="max-w-[78%]">
                  <div
                    className={`whitespace-pre-line rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-primary text-white rounded-tr-none"
                        : "bg-muted rounded-tl-none"
                    } ${msg.status === "failed" ? "ring-1 ring-destructive/50" : ""}`}
                  >
                    {msg.content}
                  </div>

                  {msg.status === "failed" && (
                    <div className={`mt-1 flex items-center gap-2 ${msg.role === "user" ? "justify-end" : ""}`}>
                      <span className="inline-flex items-center gap-1 text-xs text-destructive">
                        <AlertCircle className="h-3 w-3" />
                        {copy.failedSend}
                      </span>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => void sendMessage(msg.id, msg.content)}
                        disabled={sending || initializing}
                      >
                        <RotateCcw className="mr-1 h-3 w-3" />
                        {copy.retry}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {sending && (
              <div className="flex gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-accent/30">
                  <Bot className="h-4 w-4 text-accent-foreground" />
                </div>
                <div className="rounded-2xl rounded-tl-none bg-muted px-4 py-3">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40" />
                    <span
                      className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40"
                      style={{ animationDelay: "150ms" }}
                    />
                    <span
                      className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              </div>
            )}

            <div ref={endRef} />
          </div>

          <div className="border-t p-3">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void sendMessage();
              }}
              className="flex gap-2"
              dir={direction}
            >
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={copy.placeholder}
                className="h-10 flex-1"
                disabled={sending || initializing}
              />
              <Button
                type="submit"
                size="icon"
                className="h-10 w-10"
                disabled={sending || initializing || !input.trim()}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
