import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { translations, type AppLanguage } from "./translations";

const STORAGE_KEY = "app_language";

function resolveMessage(source: unknown, path: string): unknown {
  return path.split(".").reduce<unknown>((acc, part) => {
    if (acc && typeof acc === "object" && part in (acc as Record<string, unknown>)) {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, source);
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  return template.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, key: string) => String(params[key] ?? ""));
}

interface I18nContextValue {
  language: AppLanguage;
  isRTL: boolean;
  direction: "ltr" | "rtl";
  setLanguage: (language: AppLanguage) => void;
  toggleLanguage: () => void;
  t: (key: string, params?: Record<string, string | number>, fallback?: string) => string;
  tm: <T>(key: string, fallback?: T) => T;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<AppLanguage>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "en" || stored === "ar" ? stored : "ar";
  });

  const setLanguage = useCallback((next: AppLanguage) => {
    setLanguageState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const toggleLanguage = useCallback(() => {
    setLanguage(language === "ar" ? "en" : "ar");
  }, [language, setLanguage]);

  const direction = language === "ar" ? "rtl" : "ltr";
  const isRTL = direction === "rtl";

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = direction;
    document.body.dir = direction;
  }, [direction, language]);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>, fallback?: string) => {
      const message = resolveMessage(translations[language], key);
      if (typeof message === "string") {
        return interpolate(message, params);
      }
      return fallback ?? key;
    },
    [language],
  );

  const tm = useCallback(
    <T,>(key: string, fallback?: T) => {
      const message = resolveMessage(translations[language], key);
      return (message as T) ?? (fallback as T);
    },
    [language],
  );

  const value = useMemo<I18nContextValue>(
    () => ({ language, isRTL, direction, setLanguage, toggleLanguage, t, tm }),
    [direction, isRTL, language, setLanguage, t, tm, toggleLanguage],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return context;
}
