import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Bookmark, BookmarkCheck, CalendarDays, DollarSign, MapPin, Send, TrendingUp } from "lucide-react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { investmentAPI, getCurrentUser, type Opportunity } from "@/services/api";
import { Skeleton } from "@/components/motion/Skeleton";
import { toast } from "sonner";
import { useI18n } from "@/i18n/I18nProvider";

const OpportunityDetailsPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { language, isRTL } = useI18n();
  const currentUser = getCurrentUser();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [watchlistBusy, setWatchlistBusy] = useState(false);

  useEffect(() => {
    if (!id) {
      navigate("/investment");
      return;
    }

    setLoading(true);
    investmentAPI
      .getOpportunity(id)
      .then((response) => setOpportunity(response.data))
      .catch((error: Error) => {
        toast.error(error.message || "Failed to load opportunity");
        navigate("/investment");
      })
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const toggleWatchlist = async () => {
    if (!opportunity) return;
    if (currentUser?.role !== "investor") {
      toast.error(language === "ar" ? "سجل الدخول كمستثمر أولاً" : "Please log in as an investor first");
      return;
    }

    setWatchlistBusy(true);
    try {
      if (opportunity.is_watchlisted) {
        await investmentAPI.removeWatchlist(opportunity.id);
        setOpportunity({ ...opportunity, is_watchlisted: false });
        toast.success(language === "ar" ? "تمت إزالة الفرصة من المتابعة" : "Removed from watchlist");
      } else {
        await investmentAPI.addWatchlist(opportunity.id);
        setOpportunity({ ...opportunity, is_watchlisted: true });
        toast.success(language === "ar" ? "تمت إضافة الفرصة للمتابعة" : "Added to watchlist");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to update watchlist");
    } finally {
      setWatchlistBusy(false);
    }
  };

  const createdDate = opportunity
    ? new Date(opportunity.created_at).toLocaleDateString(language === "ar" ? "ar-EG" : "en-US")
    : "";

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container px-4">
          <Button variant="ghost" onClick={() => navigate("/investment")} className="mb-6">
            <ArrowRight className={`h-4 w-4 ${isRTL ? "ml-2" : "mr-2"}`} />
            {language === "ar" ? "العودة للاستثمار" : "Back to investments"}
          </Button>

          {loading ? (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <Skeleton h="h-40" className="rounded-2xl" />
                <Skeleton h="h-72" className="rounded-2xl" />
              </div>
              <Skeleton h="h-80" className="rounded-2xl" />
            </div>
          ) : opportunity ? (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <Card className="rounded-2xl border-border/50">
                  <CardContent className="p-6">
                    <div className="mb-4 flex flex-wrap items-center gap-2">
                      <Badge className="bg-primary">{opportunity.status}</Badge>
                      <Badge variant="outline">{opportunity.category}</Badge>
                      <Badge variant="secondary">{opportunity.opportunity_type}</Badge>
                      {opportunity.is_verified ? <Badge variant="secondary">Verified</Badge> : null}
                    </div>

                    <h1 className="mb-4 text-2xl font-bold text-foreground md:text-3xl">{opportunity.title}</h1>

                    <div className="flex flex-wrap gap-4 text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-primary" />
                        <span>{opportunity.location}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-primary" />
                        <span>{language === "ar" ? "العائد المتوقع" : "Expected ROI"}: {opportunity.roi}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CalendarDays className="h-5 w-5 text-primary" />
                        <span>{language === "ar" ? "تاريخ الإضافة" : "Listed"}: {createdDate}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="rounded-2xl border-border/50">
                  <CardHeader>
                    <CardTitle>{language === "ar" ? "وصف الفرصة" : "Opportunity overview"}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 text-muted-foreground">
                    <p className="whitespace-pre-line leading-relaxed">{opportunity.description}</p>
                    <div className="grid grid-cols-1 gap-4 rounded-2xl bg-muted/40 p-4 md:grid-cols-3">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">
                          {language === "ar" ? "الحد الأدنى" : "Minimum"}
                        </p>
                        <p className="mt-1 font-semibold text-foreground">
                          {opportunity.min_investment.toLocaleString()} EGP
                        </p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">
                          {language === "ar" ? "الحد الأقصى" : "Maximum"}
                        </p>
                        <p className="mt-1 font-semibold text-foreground">
                          {opportunity.max_investment.toLocaleString()} EGP
                        </p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">
                          {language === "ar" ? "عدد الاهتمامات" : "Interest count"}
                        </p>
                        <p className="mt-1 font-semibold text-foreground">{opportunity.interest_count}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card className="sticky top-4 rounded-2xl border-border/50">
                  <CardHeader>
                    <CardTitle>{language === "ar" ? "ملخص الاستثمار" : "Investment summary"}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-2xl bg-primary/5 p-4">
                      <p className="mb-1 text-sm text-muted-foreground">
                        {language === "ar" ? "النطاق الاستثماري" : "Investment range"}
                      </p>
                      <p className="text-xl font-bold text-primary">{opportunity.investment}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="rounded-xl bg-muted/50 p-3">
                        <p className="text-xs text-muted-foreground">{language === "ar" ? "العائد" : "ROI"}</p>
                        <p className="font-semibold text-primary">{opportunity.roi}</p>
                      </div>
                      <div className="rounded-xl bg-muted/50 p-3">
                        <p className="text-xs text-muted-foreground">{language === "ar" ? "الحالة" : "Status"}</p>
                        <p className="font-semibold">{opportunity.status}</p>
                      </div>
                    </div>

                    <Button className="w-full" size="lg" onClick={() => navigate(`/investment/contact/${opportunity.id}`)}>
                      <Send className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />
                      {language === "ar" ? "إبداء اهتمام" : "Express interest"}
                    </Button>

                    {currentUser?.role === "investor" ? (
                      <Button variant="outline" className="w-full" disabled={watchlistBusy} onClick={toggleWatchlist}>
                        {opportunity.is_watchlisted ? (
                          <BookmarkCheck className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />
                        ) : (
                          <Bookmark className={`h-5 w-5 ${isRTL ? "ml-2" : "mr-2"}`} />
                        )}
                        {opportunity.is_watchlisted
                          ? language === "ar"
                            ? "إزالة من المتابعة"
                            : "Remove from watchlist"
                          : language === "ar"
                            ? "إضافة للمتابعة"
                            : "Add to watchlist"}
                      </Button>
                    ) : null}

                    <div className="rounded-xl bg-muted/40 p-4 text-sm text-muted-foreground">
                      <div className="mb-2 flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-primary" />
                        <span>{language === "ar" ? "تمت تهيئة هذه الصفحة من بيانات فعلية عبر الخدمة الجديدة." : "This page is now powered by real investment-service data."}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </Layout>
  );
};

export default OpportunityDetailsPage;
