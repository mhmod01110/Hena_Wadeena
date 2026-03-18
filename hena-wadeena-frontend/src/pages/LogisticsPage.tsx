import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { Search, MapPin, Clock, ArrowLeft, Bus, Car } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { logisticsAPI, type TransportRoute, type Station, type Carpool } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { PageHero } from "@/components/layout/PageHero";
import heroLogistics from "@/assets/hero-logistics.jpg";
import { useI18n } from "@/i18n/I18nProvider";

const LogisticsPage = () => {
  const { language, isRTL } = useI18n();
  const navigate = useNavigate();
  const [searchFrom, setSearchFrom] = useState("");
  const [searchTo, setSearchTo] = useState("");
  const [routes, setRoutes] = useState<TransportRoute[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [carpoolTrips, setCarpoolTrips] = useState<Carpool[]>([]);
  const [loading, setLoading] = useState(true);

  const copy =
    language === "ar"
      ? {
          heroAlt: "اللوجستيات والتنقل",
          badge: "اللوجستيات والتنقل",
          title: "اللوجستيات والتنقل",
          subtitle: "ابحث عن خطوط المواصلات، المحطات، أو شارك رحلتك مع الآخرين",
          fromPlaceholder: "من أين؟",
          toPlaceholder: "إلى أين؟",
          search: "بحث",
          tabs: { routes: "خطوط المواصلات", stations: "المحطات", carpool: "مشاركة الرحلات" },
          schedule: "المواعيد",
          bookNow: "احجز الآن",
          routesCount: "خطوط",
          viewDetails: "عرض التفاصيل",
          availableTrips: "الرحلات المتاحة",
          addTrip: "أضف رحلتك",
          seatsAvailable: "مقاعد متاحة",
          bookSeat: "احجز مقعد",
          egp: "جنيه",
        }
      : {
          heroAlt: "Logistics and Transport",
          badge: "Logistics and Transport",
          title: "Logistics and Transport",
          subtitle: "Find routes and stations, or share your trip with others",
          fromPlaceholder: "From where?",
          toPlaceholder: "To where?",
          search: "Search",
          tabs: { routes: "Routes", stations: "Stations", carpool: "Carpool" },
          schedule: "Schedule",
          bookNow: "Book Now",
          routesCount: "Routes",
          viewDetails: "View Details",
          availableTrips: "Available Trips",
          addTrip: "Add Trip",
          seatsAvailable: "Seats available",
          bookSeat: "Book Seat",
          egp: "EGP",
        };

  useEffect(() => {
    Promise.all([
      logisticsAPI.getRoutes().then((r) => setRoutes(r.data)),
      logisticsAPI.getStations().then((r) => setStations(r.data)),
      logisticsAPI.getCarpools().then((r) => setCarpoolTrips(r.data)),
    ]).finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <PageTransition>
        <PageHero image={heroLogistics} alt={copy.heroAlt}>
          <SR>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
              <Bus className="h-5 w-5 text-accent" />
              <span className="text-sm font-semibold text-card">{copy.badge}</span>
            </div>
          </SR>
          <SR delay={100}>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-card mb-5">{copy.title}</h1>
          </SR>
          <SR delay={200}>
            <p className="text-lg md:text-xl text-card/90 mb-10">{copy.subtitle}</p>
          </SR>

          <SR delay={300}>
            <div className="glass rounded-2xl p-5 md:p-7 shadow-2xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="relative">
                  <MapPin className={`absolute top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
                  <Input placeholder={copy.fromPlaceholder} value={searchFrom} onChange={(e) => setSearchFrom(e.target.value)} className={`h-14 rounded-xl text-base ${isRTL ? "pr-12" : "pl-12"}`} />
                </div>
                <div className="relative">
                  <MapPin className={`absolute top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
                  <Input placeholder={copy.toPlaceholder} value={searchTo} onChange={(e) => setSearchTo(e.target.value)} className={`h-14 rounded-xl text-base ${isRTL ? "pr-12" : "pl-12"}`} />
                </div>
                <Button size="lg" className="h-14 rounded-xl text-base hover:scale-[1.02] transition-transform">
                  <Search className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />{copy.search}
                </Button>
              </div>
            </div>
          </SR>
        </PageHero>

        <section className="py-14">
          <div className="container px-4">
            <Tabs defaultValue="routes" className="w-full">
              <SR>
                <TabsList className="grid w-full max-w-md mx-auto grid-cols-3 mb-10 h-12 rounded-xl">
                  <TabsTrigger value="routes" className="rounded-lg text-sm font-semibold">{copy.tabs.routes}</TabsTrigger>
                  <TabsTrigger value="stations" className="rounded-lg text-sm font-semibold">{copy.tabs.stations}</TabsTrigger>
                  <TabsTrigger value="carpool" className="rounded-lg text-sm font-semibold">{copy.tabs.carpool}</TabsTrigger>
                </TabsList>
              </SR>

              <TabsContent value="routes" className="space-y-5">
                {loading ? (
                  [1, 2, 3].map((i) => <Skeleton key={i} h="h-32" className="rounded-2xl" />)
                ) : (
                  routes.map((route, idx) => (
                    <SR key={route.id} delay={idx * 60}>
                      <Card className="border-border/50 hover:border-primary/40 hover-lift rounded-2xl">
                        <CardContent className="p-5 md:p-7">
                          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-3">
                                <Badge variant="secondary" className="gap-1.5 px-3 py-1">
                                  <Bus className="h-4 w-4" />{route.type}
                                </Badge>
                                <span className="text-sm text-muted-foreground">{route.operator}</span>
                              </div>
                              <div className="flex items-center gap-3 text-xl font-bold text-foreground">
                                <span>{route.from}</span>
                                <ArrowLeft className="h-6 w-6 text-primary" />
                                <span>{route.to}</span>
                              </div>
                              <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1.5"><Clock className="h-4 w-4" />{route.duration}</div>
                                <div>{copy.schedule}: {route.departures.join(" - ")}</div>
                              </div>
                            </div>
                            <div className="flex items-center justify-between md:flex-col md:items-end gap-3">
                              <div className="text-3xl font-bold text-primary">{route.price} <span className="text-sm font-normal">{copy.egp}</span></div>
                              <Button className="hover:scale-[1.03] transition-transform" onClick={() => navigate(`/logistics/route/${route.id}`)}>{copy.bookNow}</Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </SR>
                  ))
                )}
              </TabsContent>

              <TabsContent value="stations" className="space-y-4">
                {loading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {[1, 2, 3, 4].map((i) => <Skeleton key={i} h="h-36" className="rounded-2xl" />)}
                  </div>
                ) : (
                  <SR stagger>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      {stations.map((station) => (
                        <Card key={station.id} className="border-border/50 hover:border-primary/40 hover-lift rounded-2xl">
                          <CardContent className="p-6">
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="text-lg font-bold text-foreground mb-1">{station.name}</h3>
                                <div className="flex items-center gap-1.5 text-muted-foreground">
                                  <MapPin className="h-4 w-4" />{station.city}
                                </div>
                              </div>
                              <Badge variant="outline" className="text-sm">{station.routes} {copy.routesCount}</Badge>
                            </div>
                            <Button variant="outline" className="w-full mt-5 hover:scale-[1.01] transition-transform" onClick={() => navigate(`/logistics/station/${station.id}`)}>{copy.viewDetails}</Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </SR>
                )}
              </TabsContent>

              <TabsContent value="carpool" className="space-y-5">
                <SR>
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-2xl font-bold text-foreground">{copy.availableTrips}</h3>
                    <Button className="hover:scale-[1.03] transition-transform" onClick={() => navigate("/logistics/create-trip")}>
                      <Car className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />{copy.addTrip}
                    </Button>
                  </div>
                </SR>
                {loading ? (
                  [1, 2, 3].map((i) => <Skeleton key={i} h="h-28" className="rounded-2xl" />)
                ) : (
                  carpoolTrips.map((trip, idx) => (
                    <SR key={trip.id} delay={idx * 60}>
                      <Card className="border-border/50 hover:border-primary/40 hover-lift rounded-2xl">
                        <CardContent className="p-5 md:p-7">
                          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 text-xl font-bold text-foreground mb-2">
                                <span>{trip.from}</span>
                                <ArrowLeft className="h-6 w-6 text-primary" />
                                <span>{trip.to}</span>
                              </div>
                              <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                                <div>{trip.date}</div>
                                <div className="flex items-center gap-1.5"><Clock className="h-4 w-4" />{trip.time}</div>
                                <div className="flex items-center gap-1.5"><span className="text-primary font-medium">{trip.rating}</span><span>• {trip.driver}</span></div>
                              </div>
                            </div>
                            <div className="flex items-center justify-between md:flex-col md:items-end gap-2">
                              <div>
                                <div className="text-3xl font-bold text-primary">{trip.price} <span className="text-sm font-normal">{copy.egp}</span></div>
                                <div className="text-sm text-muted-foreground">{trip.seats} {copy.seatsAvailable}</div>
                              </div>
                              <Button className="hover:scale-[1.03] transition-transform" onClick={() => navigate(`/logistics/book/${trip.id}`)}>{copy.bookSeat}</Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </SR>
                  ))
                )}
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default LogisticsPage;