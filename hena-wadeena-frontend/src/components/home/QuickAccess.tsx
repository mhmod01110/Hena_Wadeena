import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { User, Wallet, Bell, CalendarCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { notificationsAPI } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { useI18n } from "@/i18n/I18nProvider";

export function QuickAccess() {
  const { t } = useI18n();
  const [user, setUser] = useState<any>(null);
  const [unreadCount, setUnreadCount] = useState(0);

  const quickLinks = [
    { icon: User, label: t("quickAccess.profile"), href: "/profile", gradient: "from-blue-500 to-blue-600" },
    { icon: Wallet, label: t("quickAccess.wallet"), href: "/wallet", gradient: "from-green-500 to-emerald-600" },
    { icon: CalendarCheck, label: t("quickAccess.bookings"), href: "/bookings", gradient: "from-purple-500 to-violet-600" },
    { icon: Bell, label: t("quickAccess.notifications"), href: "/notifications", gradient: "from-red-500 to-rose-600" },
  ];

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) {
      setUser(JSON.parse(stored));
      notificationsAPI
        .getUnreadCount()
        .then((r) => setUnreadCount(r.data.count))
        .catch(() => {});
    }
  }, []);

  if (!user) return null;

  return (
    <section className="py-14 bg-gradient-to-b from-background to-muted/30">
      <SR direction="up" className="container px-4">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold">{t("quickAccess.greeting", { name: user.full_name })}</h2>
          <p className="text-muted-foreground mt-2 text-lg">{t("quickAccess.subtitle")}</p>
        </div>

        <SR stagger className="grid grid-cols-2 md:grid-cols-4 gap-5 max-w-3xl mx-auto">
          {quickLinks.map((link) => {
            const Icon = link.icon;
            const isNotif = link.href === "/notifications";
            return (
              <Link key={link.href} to={link.href}>
                <Card className="hover-lift hover:border-primary/30 text-center rounded-2xl group transition-all duration-400">
                  <CardContent className="p-5 flex flex-col items-center gap-3 relative">
                    <div className={`h-16 w-16 rounded-2xl flex items-center justify-center bg-gradient-to-br ${link.gradient} shadow-lg icon-hover`}>
                      <Icon className="h-8 w-8 text-primary-foreground" strokeWidth={1.8} />
                    </div>
                    {isNotif && unreadCount > 0 && (
                      <Badge className="absolute top-2 right-2 bg-destructive text-destructive-foreground text-[10px] h-5 w-5 p-0 flex items-center justify-center animate-pulse">
                        {unreadCount}
                      </Badge>
                    )}
                    <span className="text-sm font-semibold text-foreground">{link.label}</span>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </SR>
      </SR>
    </section>
  );
}
