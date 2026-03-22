import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Bookmark, BriefcaseBusiness, CircleCheckBig, Clock3, TrendingUp } from "lucide-react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { investmentAPI, getCurrentUser, type InvestorDashboard } from "@/services/api";
import { Skeleton } from "@/components/motion/Skeleton";
import { toast } from "sonner";

const statusIcons: Record<string, JSX.Element> = {
  submitted: <Clock3 className="h-4 w-4 text-primary" />,
  under_review: <TrendingUp className="h-4 w-4 text-primary" />,
  accepted: <CircleCheckBig className="h-4 w-4 text-primary" />,
  rejected: <BriefcaseBusiness className="h-4 w-4 text-primary" />,
};

const InvestorDashboardPage = () => {
  const navigate = useNavigate();
  const user = getCurrentUser();
  const [dashboard, setDashboard] = useState<InvestorDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    investmentAPI
      .getDashboard()
      .then((response) => setDashboard(response.data))
      .catch((error: Error) => {
        toast.error(error.message || "Failed to load investor dashboard");
        navigate("/investment");
      })
      .finally(() => setLoading(false));
  }, [navigate, user]);

  const statusEntries = Object.entries(dashboard?.status_counts || {});

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container px-4">
          <Button variant="ghost" onClick={() => navigate("/investment")} className="mb-6">
            <ArrowRight className="mr-2 h-4 w-4" />
            Back to investments
          </Button>

          <div className="mb-8 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Investor Dashboard</h1>
              <p className="text-muted-foreground">Track your active interests, saved opportunities, and recommended deals.</p>
            </div>
            <Button onClick={() => navigate("/investment")}>Browse opportunities</Button>
          </div>

          {loading ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
                {[1, 2, 3, 4].map((item) => (
                  <Skeleton key={item} h="h-28" className="rounded-2xl" />
                ))}
              </div>
              <Skeleton h="h-80" className="rounded-2xl" />
            </div>
          ) : dashboard ? (
            <div className="space-y-8">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
                {(statusEntries.length ? statusEntries : [["submitted", 0], ["under_review", 0], ["accepted", 0], ["rejected", 0]]).map(
                  ([status, count]) => (
                    <Card key={status} className="rounded-2xl border-border/50">
                      <CardContent className="flex items-center justify-between p-5">
                        <div>
                          <p className="text-sm capitalize text-muted-foreground">{String(status).replace(/_/g, " ")}</p>
                          <p className="mt-1 text-2xl font-bold text-foreground">{count}</p>
                        </div>
                        <div className="rounded-full bg-primary/10 p-3">{statusIcons[status] || <TrendingUp className="h-4 w-4 text-primary" />}</div>
                      </CardContent>
                    </Card>
                  ),
                )}
              </div>

              <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
                <Card className="rounded-2xl border-border/50 xl:col-span-2">
                  <CardHeader>
                    <CardTitle>Recent interests</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {dashboard.recent_interests.length ? (
                      dashboard.recent_interests.map((interest) => (
                        <div key={interest.id} className="rounded-2xl border border-border/60 p-4">
                          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                            <div>
                              <h3 className="font-semibold text-foreground">{interest.opportunity_title || "Opportunity"}</h3>
                              <p className="text-sm text-muted-foreground">
                                {interest.opportunity_category || "General"} • {interest.opportunity_location || "New Valley"}
                              </p>
                            </div>
                            <Badge variant="secondary">{interest.status}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{interest.message}</p>
                          {interest.owner_notes ? (
                            <p className="mt-2 text-sm text-foreground">
                              <span className="font-medium">Owner note:</span> {interest.owner_notes}
                            </p>
                          ) : null}
                        </div>
                      ))
                    ) : (
                      <div className="rounded-2xl border border-dashed p-6 text-center text-muted-foreground">
                        No interests submitted yet.
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card className="rounded-2xl border-border/50">
                  <CardHeader>
                    <CardTitle>Watchlist</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {dashboard.watchlist.length ? (
                      dashboard.watchlist.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => navigate(`/investment/opportunity/${item.id}`)}
                          className="w-full rounded-2xl border border-border/60 p-4 text-left transition-colors hover:bg-muted/40"
                        >
                          <div className="mb-2 flex items-center justify-between gap-2">
                            <div className="font-semibold text-foreground">{item.title}</div>
                            <Bookmark className="h-4 w-4 text-primary" />
                          </div>
                          <p className="text-sm text-muted-foreground">{item.location}</p>
                          <p className="mt-2 text-sm text-foreground">{item.investment}</p>
                        </button>
                      ))
                    ) : (
                      <div className="rounded-2xl border border-dashed p-6 text-center text-muted-foreground">
                        Your watchlist is empty.
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <Card className="rounded-2xl border-border/50">
                <CardHeader>
                  <CardTitle>Recommended opportunities</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {dashboard.recommended.length ? (
                    dashboard.recommended.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => navigate(`/investment/opportunity/${item.id}`)}
                        className="rounded-2xl border border-border/60 p-4 text-left transition-colors hover:bg-muted/40"
                      >
                        <div className="mb-2 flex items-center justify-between gap-2">
                          <Badge variant="outline">{item.category}</Badge>
                          {item.is_verified ? <Badge variant="secondary">Verified</Badge> : null}
                        </div>
                        <h3 className="font-semibold text-foreground">{item.title}</h3>
                        <p className="mt-2 text-sm text-muted-foreground">{item.location}</p>
                        <p className="mt-3 text-sm text-foreground">{item.investment}</p>
                      </button>
                    ))
                  ) : (
                    <div className="col-span-full rounded-2xl border border-dashed p-6 text-center text-muted-foreground">
                      We will recommend more opportunities as you save and review deals.
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : null}
        </div>
      </section>
    </Layout>
  );
};

export default InvestorDashboardPage;
