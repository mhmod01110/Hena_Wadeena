import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  CalendarCheck,
  ChevronDown,
  Languages,
  LogOut,
  MapPin,
  Menu,
  Moon,
  Settings,
  Sun,
  User,
  Wallet,
} from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { authAPI, clearAuthSession, notificationsAPI } from "@/services/api";
import { useI18n } from "@/i18n/I18nProvider";

interface AppUser {
  id: string;
  full_name: string;
  email?: string;
  avatar_url?: string;
  role?: string;
}

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const { t } = useI18n();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <Button variant="ghost" size="icon" className="text-muted-foreground" aria-label={t("header.toggleTheme")}>
        <Sun className="h-5 w-5" />
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      className="text-muted-foreground hover:text-foreground"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label={t("header.toggleTheme")}
    >
      {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </Button>
  );
}

function LanguageToggle() {
  const { language, setLanguage, t } = useI18n();

  return (
    <Button
      variant="ghost"
      size="sm"
      className="text-muted-foreground hover:text-foreground gap-2"
      onClick={() => setLanguage(language === "ar" ? "en" : "ar")}
      aria-label={language === "ar" ? t("common.switchToEnglish") : t("common.switchToArabic")}
    >
      <Languages className="h-4 w-4" />
      <span className="text-xs font-semibold">{language === "ar" ? "EN" : "AR"}</span>
    </Button>
  );
}

export function Header() {
  const { t, isRTL } = useI18n();
  const location = useLocation();
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [user, setUser] = useState<AppUser | null>(null);

  const navigation = [
    { name: t("header.nav.home"), href: "/" },
    { name: t("header.nav.tourism"), href: "/tourism" },
    { name: t("header.nav.guides"), href: "/guides" },
    { name: t("header.nav.marketplace"), href: "/marketplace" },
    { name: t("header.nav.logistics"), href: "/logistics" },
    { name: t("header.nav.investment"), href: "/investment" },
  ];

  useEffect(() => {
    const stored = localStorage.getItem("user");
    setUser(stored ? (JSON.parse(stored) as AppUser) : null);
  }, [location.pathname]);

  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      return;
    }

    const refreshUnread = () => notificationsAPI.getUnreadCount().then((r) => setUnreadCount(r.data.count)).catch(() => {});
    refreshUnread();
    const interval = setInterval(refreshUnread, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const isActive = (path: string) => (path === "/" ? location.pathname === "/" : location.pathname.startsWith(path));

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch {
      // token may already be invalid; always clear local state.
    }

    clearAuthSession();
    setUser(null);
    setProfileOpen(false);
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
      <div className="container flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <MapPin className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground">{t("common.appName")}</span>
        </Link>

        <nav className="hidden lg:flex items-center gap-1">
          {navigation.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-1">
          <ThemeToggle />
          <LanguageToggle />

          {user ? (
            <>
              <Link to="/notifications" className="relative">
                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
                  <Bell className="h-5 w-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -end-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-card animate-pulse">
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </span>
                  )}
                </Button>
              </Link>

              <Link to="/wallet">
                <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground gap-1.5">
                  <Wallet className="h-4 w-4" />
                  <span className="text-xs font-semibold">{t("header.wallet")}</span>
                </Button>
              </Link>

              <div className="relative">
                <button
                  onClick={() => setProfileOpen((prev) => !prev)}
                  className="flex items-center gap-2 p-1.5 rounded-full hover:bg-muted transition-colors"
                >
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt={user.full_name} className="h-8 w-8 rounded-full object-cover" />
                    ) : (
                      <User className="h-4 w-4 text-primary" />
                    )}
                  </div>
                  <ChevronDown className="h-3 w-3 text-muted-foreground" />
                </button>

                {profileOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setProfileOpen(false)} />
                    <div
                      className={`absolute ${isRTL ? "left-0" : "right-0"} top-full mt-2 w-56 rounded-xl border border-border bg-card shadow-xl z-50 py-2 animate-in fade-in slide-in-from-top-2 duration-200`}
                    >
                      <div className="px-4 py-3 border-b border-border">
                        <p className="font-semibold text-sm truncate">{user.full_name}</p>
                        <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                      </div>

                      <div className="py-1">
                        <Link to="/profile" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors">
                          <User className="h-4 w-4 text-muted-foreground" /> {t("header.profile")}
                        </Link>
                        <Link to="/bookings" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors">
                          <CalendarCheck className="h-4 w-4 text-muted-foreground" /> {t("header.bookings")}
                        </Link>
                        <Link to="/wallet" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors">
                          <Wallet className="h-4 w-4 text-muted-foreground" /> {t("header.wallet")}
                        </Link>
                        <Link to="/notifications" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors">
                          <Bell className="h-4 w-4 text-muted-foreground" />
                          {t("header.notifications")}
                          {unreadCount > 0 && (
                            <span className="ms-auto bg-red-500 text-white text-[10px] font-bold rounded-full h-5 w-5 flex items-center justify-center">
                              {unreadCount}
                            </span>
                          )}
                        </Link>
                        {["admin", "super_admin"].includes(user.role || "") && (
                          <Link
                            to="/admin/dashboard"
                            onClick={() => setProfileOpen(false)}
                            className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors"
                          >
                            <Settings className="h-4 w-4 text-muted-foreground" /> {t("header.adminDashboard")}
                          </Link>
                        )}
                        {["moderator", "reviewer", "admin", "super_admin"].includes(user.role || "") && (
                          <Link
                            to="/moderator/dashboard"
                            onClick={() => setProfileOpen(false)}
                            className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors"
                          >
                            <Settings className="h-4 w-4 text-muted-foreground" /> {t("header.moderatorDashboard")}
                          </Link>
                        )}
                        {["reviewer", "admin", "super_admin"].includes(user.role || "") && (
                          <Link
                            to="/reviewer/dashboard"
                            onClick={() => setProfileOpen(false)}
                            className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors"
                          >
                            <Settings className="h-4 w-4 text-muted-foreground" /> {t("header.reviewerDashboard")}
                          </Link>
                        )}
                      </div>

                      <div className="border-t border-border pt-1">
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                        >
                          <LogOut className="h-4 w-4" /> {t("header.logout")}
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <User className="h-4 w-4" />
                  {t("header.login")}
                </Button>
              </Link>
              <Link to="/register">
                <Button size="sm">{t("header.register")}</Button>
              </Link>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 md:hidden">
          <LanguageToggle />
          {user && (
            <Link to="/notifications" className="relative">
              <Button variant="ghost" size="icon" className="text-muted-foreground">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -end-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-card animate-pulse">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Button>
            </Link>
          )}

          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
            <SheetContent side={isRTL ? "right" : "left"} className="w-80">
              <div className="flex flex-col gap-6 mt-8">
                {user && (
                  <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/10">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <p className="font-bold text-sm">{user.full_name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                )}

                <nav className="flex flex-col gap-1">
                  {navigation.map((item) => (
                    <Link
                      key={item.href}
                      to={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                        isActive(item.href)
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted"
                      }`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </nav>

                {user ? (
                  <div className="border-t border-border pt-4 flex flex-col gap-1">
                    <Link to="/profile" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                      <User className="h-5 w-5 text-muted-foreground" /> {t("header.profile")}
                    </Link>
                    <Link to="/bookings" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                      <CalendarCheck className="h-5 w-5 text-muted-foreground" /> {t("header.bookings")}
                    </Link>
                    <Link to="/wallet" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                      <Wallet className="h-5 w-5 text-muted-foreground" /> {t("header.wallet")}
                    </Link>
                    <Link to="/notifications" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                      <Bell className="h-5 w-5 text-muted-foreground" /> {t("header.notifications")}
                      {unreadCount > 0 && (
                        <span className="ms-auto bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                          {unreadCount}
                        </span>
                      )}
                    </Link>
                    {["admin", "super_admin"].includes(user.role || "") && (
                      <Link to="/admin/dashboard" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                        <Settings className="h-5 w-5 text-muted-foreground" /> {t("header.adminDashboard")}
                      </Link>
                    )}
                    {["moderator", "reviewer", "admin", "super_admin"].includes(user.role || "") && (
                      <Link to="/moderator/dashboard" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                        <Settings className="h-5 w-5 text-muted-foreground" /> {t("header.moderatorDashboard")}
                      </Link>
                    )}
                    {["reviewer", "admin", "super_admin"].includes(user.role || "") && (
                      <Link to="/reviewer/dashboard" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-muted transition-colors">
                        <Settings className="h-5 w-5 text-muted-foreground" /> {t("header.reviewerDashboard")}
                      </Link>
                    )}
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsOpen(false);
                      }}
                      className="flex items-center gap-3 px-4 py-3 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut className="h-5 w-5" /> {t("header.logout")}
                    </button>
                  </div>
                ) : (
                  <div className="border-t border-border pt-4 flex flex-col gap-2">
                    <Link to="/login" onClick={() => setIsOpen(false)}>
                      <Button className="w-full" variant="outline">
                        <User className="h-4 w-4" />
                        {t("header.login")}
                      </Button>
                    </Link>
                    <Link to="/register" onClick={() => setIsOpen(false)}>
                      <Button className="w-full">{t("header.register")}</Button>
                    </Link>
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}


