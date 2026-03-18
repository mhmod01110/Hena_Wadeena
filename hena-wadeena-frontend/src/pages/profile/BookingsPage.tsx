import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Calendar, Clock, Users, CalendarCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { guidesAPI, type Booking } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition, GradientMesh } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { useI18n } from "@/i18n/I18nProvider";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-500/10 text-yellow-600",
  confirmed: "bg-green-500/10 text-green-600",
  completed: "bg-blue-500/10 text-blue-600",
  cancelled: "bg-red-500/10 text-red-600",
};

const BookingsPage = () => {
  const { language } = useI18n();
  const navigate = useNavigate();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  const copy =
    language === "ar"
      ? {
          title: "حجوزاتي",
          empty: "لا توجد حجوزات حتى الآن. ابدأ باستكشاف المرشدين السياحيين!",
          withGuide: "مع",
          people: "أشخاص",
          currency: "جنيه",
          status: {
            pending: "في الانتظار",
            confirmed: "مؤكد",
            completed: "مكتمل",
            cancelled: "ملغى",
            in_progress: "جاري",
          },
        }
      : {
          title: "My Bookings",
          empty: "No bookings yet. Start exploring tour guides!",
          withGuide: "with",
          people: "people",
          currency: "EGP",
          status: {
            pending: "Pending",
            confirmed: "Confirmed",
            completed: "Completed",
            cancelled: "Cancelled",
            in_progress: "In Progress",
          },
        };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    guidesAPI.getMyBookings().then((r) => setBookings(r.data)).catch(console.error).finally(() => setLoading(false));
  }, [navigate]);

  return (
    <Layout>
      <PageTransition>
        <section className="relative py-14 md:py-20 overflow-hidden">
          <GradientMesh />
          <div className="container relative px-4 max-w-3xl">
            <SR>
              <div className="flex items-center gap-4 mb-10">
                <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <CalendarCheck className="h-7 w-7 text-primary" />
                </div>
                <h1 className="text-3xl md:text-4xl font-bold">{copy.title}</h1>
              </div>
            </SR>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => <Skeleton key={i} h="h-32" className="rounded-2xl" />)}
              </div>
            ) : bookings.length === 0 ? (
              <SR>
                <Card className="rounded-2xl"><CardContent className="p-14 text-center text-muted-foreground text-lg">{copy.empty}</CardContent></Card>
              </SR>
            ) : (
              <div className="space-y-5">
                {bookings.map((b, idx) => (
                  <SR key={b.id} delay={idx * 60}>
                    <Card className="hover-lift rounded-2xl border-border/50">
                      <CardContent className="p-7">
                        <div className="flex items-start justify-between mb-5">
                          <div>
                            <h3 className="text-lg font-bold">{b.package_title}</h3>
                            <p className="text-sm text-muted-foreground mt-1">{copy.withGuide} {b.guide_name}</p>
                          </div>
                          <Badge className={`${statusColors[b.status] || ""} px-3 py-1`}>{copy.status[b.status as keyof typeof copy.status] || b.status}</Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2.5 text-muted-foreground">
                            <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center"><Calendar className="h-4 w-4" /></div>
                            {b.booking_date}
                          </div>
                          <div className="flex items-center gap-2.5 text-muted-foreground">
                            <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center"><Clock className="h-4 w-4" /></div>
                            {b.start_time}
                          </div>
                          <div className="flex items-center gap-2.5 text-muted-foreground">
                            <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center"><Users className="h-4 w-4" /></div>
                            {b.people_count} {copy.people}
                          </div>
                          <div className="font-bold text-primary text-left text-lg">
                            {b.total_price.toLocaleString()} {copy.currency}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </SR>
                ))}
              </div>
            )}
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default BookingsPage;