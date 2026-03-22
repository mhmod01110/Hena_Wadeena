import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Building2, DollarSign, LayoutDashboard, MapPin, Search, Send, TrendingUp } from "lucide-react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { investmentAPI, getCurrentUser, type Opportunity, type Startup } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { PageHero } from "@/components/layout/PageHero";
import heroInvestment from "@/assets/hero-investment.jpg";
import { useI18n } from "@/i18n/I18nProvider";
import { toast } from "sonner";

const isAvailableStatus = (status: string) => status.trim().toLowerCase() === "open";

const InvestmentPage = () => {
  const { language, isRTL } = useI18n();
  const navigate = useNavigate();
  const currentUser = getCurrentUser();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [startups, setStartups] = useState<Startup[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  const copy =
    language === "ar"
      ? {
          heroAlt: "فرص الاستثمار",
          badge: "فرص الاستثمار",
          title: "فرص الاستثمار",
          subtitle: "اكتشف الفرص الواعدة في الوادي الجديد وتابع الشركات الناشئة من نفس المنصة.",
          searchPlaceholder: "ابحث عن فرصة أو شركة ناشئة...",
          tabs: { opportunities: "الفرص", startups: "الشركات الناشئة" },
          dashboard: "لوحة المستثمر",
          expectedRoi: "العائد المتوقع",
          details: "التفاصيل",
          inquire: "إبداء اهتمام",
          contact: "تواصل",
          team: "أعضاء",
          available: "متاح",
          pending: "قيد المراجعة",
          empty: "لا توجد نتائج مطابقة حالياً.",
        }
      : {
          heroAlt: "Investment Opportunities",
          badge: "Investment Opportunities",
          title: "Investment Opportunities",
          subtitle: "Discover strong opportunities in New Valley and explore startup deals from the same marketplace.",
          searchPlaceholder: "Search for an opportunity or startup...",
          tabs: { opportunities: "Opportunities", startups: "Startups" },
          dashboard: "Investor Dashboard",
          expectedRoi: "Expected ROI",
          details: "Details",
          inquire: "Express Interest",
          contact: "Contact",
          team: "Members",
          available: "Open",
          pending: "Pending review",
          empty: "No matching results right now.",
        };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      investmentAPI.getOpportunities().then((response) => setOpportunities(response.data)),
      investmentAPI.getStartups().then((response) => setStartups(response.data)),
    ])
      .catch((error: Error) => {
        toast.error(error.message || "Failed to load investment data");
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredOpportunities = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const source = opportunities.filter((opportunity) => opportunity.opportunity_type !== "startup");
    if (!needle) return source;
    return source.filter((opportunity) =>
      [opportunity.title, opportunity.category, opportunity.location, opportunity.description]
        .join(" ")
        .toLowerCase()
        .includes(needle),
    );
  }, [opportunities, query]);

  const filteredStartups = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return startups;
    return startups.filter((startup) =>
      [startup.name, startup.sector, startup.location, startup.description].join(" ").toLowerCase().includes(needle),
    );
  }, [startups, query]);

  return (
    <Layout>
      <PageTransition>
        <PageHero image={heroInvestment} alt={copy.heroAlt}>
          <SR>
            <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-2">
              <TrendingUp className="h-5 w-5 text-accent" />
              <span className="text-sm font-semibold text-card">{copy.badge}</span>
            </div>
          </SR>
          <SR delay={100}>
            <h1 className="mb-5 text-4xl font-bold text-card md:text-5xl lg:text-6xl">{copy.title}</h1>
          </SR>
          <SR delay={200}>
            <p className="mb-10 text-lg text-card/90 md:text-xl">{copy.subtitle}</p>
          </SR>
          <SR delay={300}>
            <div className="mx-auto flex max-w-4xl flex-col gap-4 md:flex-row">
              <div className="relative flex-1">
                <Search className={`absolute top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
                <Input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder={copy.searchPlaceholder}
                  className={`h-14 rounded-2xl border-0 bg-card/90 text-lg backdrop-blur-sm ${isRTL ? "pr-12" : "pl-12"}`}
                />
              </div>
              {currentUser?.role === "investor" ? (
                <Button size="lg" className="h-14 rounded-2xl px-6" onClick={() => navigate("/investment/dashboard")}>
                  <LayoutDashboard className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />
                  {copy.dashboard}
                </Button>
              ) : null}
            </div>
          </SR>
        </PageHero>

        <section className="py-14">
          <div className="container px-4">
            <Tabs defaultValue="opportunities" className="w-full">
              <SR>
                <TabsList className="mx-auto mb-10 grid h-12 w-full max-w-md grid-cols-2 rounded-xl">
                  <TabsTrigger value="opportunities" className="rounded-lg text-sm font-semibold">
                    {copy.tabs.opportunities}
                  </TabsTrigger>
                  <TabsTrigger value="startups" className="rounded-lg text-sm font-semibold">
                    {copy.tabs.startups}
                  </TabsTrigger>
                </TabsList>
              </SR>

              <TabsContent value="opportunities" className="space-y-6">
                {loading ? (
                  <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    {[1, 2, 3, 4].map((item) => (
                      <Skeleton key={item} h="h-64" className="rounded-2xl" />
                    ))}
                  </div>
                ) : filteredOpportunities.length ? (
                  <SR stagger>
                    <div className="grid grid-cols-1 gap-7 lg:grid-cols-2">
                      {filteredOpportunities.map((opportunity) => (
                        <Card key={opportunity.id} className="hover-lift rounded-2xl border-border/50 hover:border-primary/40">
                          <CardContent className="p-7">
                            <div className="mb-5 flex items-start justify-between gap-3">
                              <Badge
                                variant={isAvailableStatus(opportunity.status) ? "default" : "secondary"}
                                className={isAvailableStatus(opportunity.status) ? "bg-primary px-3 py-1" : "px-3 py-1"}
                              >
                                {isAvailableStatus(opportunity.status) ? copy.available : copy.pending}
                              </Badge>
                              <div className="flex flex-wrap justify-end gap-2">
                                <Badge variant="outline" className="px-3 py-1">
                                  {opportunity.category}
                                </Badge>
                                {opportunity.is_verified ? <Badge variant="secondary">Verified</Badge> : null}
                              </div>
                            </div>
                            <h3 className="mb-3 text-xl font-bold text-foreground">{opportunity.title}</h3>
                            <p className="mb-5 line-clamp-2 text-muted-foreground">{opportunity.description}</p>
                            <div className="mb-5 grid grid-cols-2 gap-4">
                              <div className="flex items-center gap-2.5 text-sm">
                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                                  <MapPin className="h-5 w-5 text-primary" />
                                </div>
                                <span className="text-muted-foreground">{opportunity.location}</span>
                              </div>
                              <div className="flex items-center gap-2.5 text-sm">
                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                                  <DollarSign className="h-5 w-5 text-primary" />
                                </div>
                                <span className="text-muted-foreground">{opportunity.investment}</span>
                              </div>
                              <div className="col-span-2 flex items-center gap-2.5 text-sm">
                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                                  <TrendingUp className="h-5 w-5 text-primary" />
                                </div>
                                <span className="text-muted-foreground">
                                  {copy.expectedRoi}: {opportunity.roi} • {opportunity.interest_count} interests
                                </span>
                              </div>
                            </div>
                            <div className="flex gap-3">
                              <Button variant="outline" className="flex-1" onClick={() => navigate(`/investment/opportunity/${opportunity.id}`)}>
                                {copy.details}
                                <ArrowLeft className={`h-4 w-4 ${isRTL ? "mr-2" : "ml-2"}`} />
                              </Button>
                              <Button className="flex-1" onClick={() => navigate(`/investment/contact/${opportunity.id}`)}>
                                <Send className={`h-4 w-4 ${isRTL ? "ml-2" : "mr-2"}`} />
                                {copy.inquire}
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </SR>
                ) : (
                  <Card className="rounded-2xl border-dashed">
                    <CardContent className="p-8 text-center text-muted-foreground">{copy.empty}</CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="startups" className="space-y-6">
                {loading ? (
                  <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {[1, 2, 3].map((item) => (
                      <Skeleton key={item} h="h-56" className="rounded-2xl" />
                    ))}
                  </div>
                ) : filteredStartups.length ? (
                  <SR stagger>
                    <div className="grid grid-cols-1 gap-7 md:grid-cols-2 lg:grid-cols-3">
                      {filteredStartups.map((startup) => (
                        <Card key={startup.id} className="hover-lift rounded-2xl border-border/50 hover:border-primary/40">
                          <CardContent className="p-7">
                            <div className="mb-5 flex items-center gap-4">
                              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 shadow-md">
                                <Building2 className="h-8 w-8 text-primary" />
                              </div>
                              <div>
                                <h3 className="text-lg font-bold text-foreground">{startup.name}</h3>
                                <Badge variant="secondary" className="mt-1">
                                  {startup.stage}
                                </Badge>
                              </div>
                            </div>
                            <p className="mb-5 line-clamp-3 text-muted-foreground">{startup.description}</p>
                            <div className="mb-5 flex flex-wrap gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1.5">
                                <MapPin className="h-4 w-4" />
                                {startup.location}
                              </div>
                              <div>{startup.sector}</div>
                              <div>
                                {startup.team} {copy.team}
                              </div>
                            </div>
                            <Button className="w-full" onClick={() => navigate(`/investment/contact/${startup.id}`)}>
                              <Send className={`h-4 w-4 ${isRTL ? "ml-2" : "mr-2"}`} />
                              {copy.contact}
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </SR>
                ) : (
                  <Card className="rounded-2xl border-dashed">
                    <CardContent className="p-8 text-center text-muted-foreground">{copy.empty}</CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default InvestmentPage;
