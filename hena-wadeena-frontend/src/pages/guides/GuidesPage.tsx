import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { Search, Star, Users } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { guidesAPI, type GuideProfile } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition } from "@/components/motion/PageTransition";
import { CardSkeleton } from "@/components/motion/Skeleton";
import { PageHero } from "@/components/layout/PageHero";
import heroGuides from "@/assets/hero-guides.jpg";
import { useI18n } from "@/i18n/I18nProvider";

const containsArabic = (value: string) => /[\u0600-\u06FF]/.test(value);

const GuidesPage = () => {
  const { language, isRTL } = useI18n();
  const navigate = useNavigate();
  const [guides, setGuides] = useState<GuideProfile[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const copy =
    language === "ar"
      ? {
          heroAlt: "المرشدين السياحيين",
          badge: "المرشدين السياحيين",
          title: "المرشدين السياحيين",
          subtitle: "اختر مرشدك واحجز رحلة مميزة في الوادي الجديد",
          searchPlaceholder: "ابحث بالاسم أو التخصص...",
          licensed: "مرخّص",
          perDay: "جنيه/يوم",
          reviews: "تقييم",
          bioFallback: "مرشد سياحي معتمد في الوادي الجديد",
        }
      : {
          heroAlt: "Tour Guides",
          badge: "Tour Guides",
          title: "Tour Guides",
          subtitle: "Choose your guide and book a memorable trip in New Valley",
          searchPlaceholder: "Search by name or specialty...",
          licensed: "Licensed",
          perDay: "EGP/day",
          reviews: "reviews",
          bioFallback: "Certified local tour guide in New Valley",
        };

  useEffect(() => {
    guidesAPI.getGuides().then((r) => setGuides(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const normalizedSearch = search.trim().toLowerCase();
  const filtered = guides.filter((g) => {
    if (!normalizedSearch) return true;
    const haystack = [g.name, ...g.specialties, g.bio_ar].join(" ").toLowerCase();
    return haystack.includes(normalizedSearch);
  });

  return (
    <Layout>
      <PageTransition>
        <PageHero image={heroGuides} alt={copy.heroAlt}>
          <SR>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
              <Users className="h-5 w-5 text-accent" />
              <span className="text-sm font-semibold text-card">{copy.badge}</span>
            </div>
          </SR>
          <SR delay={100}>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-5 text-card">{copy.title}</h1>
          </SR>
          <SR delay={200}>
            <p className="text-lg md:text-xl text-card/90 mb-10">{copy.subtitle}</p>
          </SR>
          <SR delay={300}>
            <div className="relative max-w-xl mx-auto">
              <Search className={`absolute top-1/2 -translate-y-1/2 h-6 w-6 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
              <Input
                placeholder={copy.searchPlaceholder}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className={`h-16 text-lg rounded-2xl shadow-lg border-0 bg-card/90 backdrop-blur-sm ${isRTL ? "pr-14" : "pl-14"}`}
              />
            </div>
          </SR>
        </PageHero>

        <section className="py-14">
          <div className="container px-4">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
                {[1, 2, 3, 4, 5, 6].map((i) => <CardSkeleton key={i} />)}
              </div>
            ) : (
              <SR stagger>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
                  {filtered.map((guide) => (
                    <Card key={guide.id} className="hover-lift cursor-pointer group overflow-hidden rounded-2xl border-border/50 hover:border-primary/40" onClick={() => navigate(`/guides/${guide.id}`)}>
                      <CardContent className="p-0">
                        <div className="relative overflow-hidden">
                          <img src={guide.image} alt={guide.name} className="w-full h-52 object-cover group-hover:scale-110 transition-transform duration-700" />
                          {guide.license_verified && (
                            <Badge className="absolute top-3 left-3 bg-green-500 text-white shadow-lg">✓ {copy.licensed}</Badge>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-foreground/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        </div>
                        <div className="p-6 space-y-3">
                          <h3 className="text-xl font-bold group-hover:text-primary transition-colors duration-250">{guide.name}</h3>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {language === "en" && containsArabic(guide.bio_ar) ? copy.bioFallback : guide.bio_ar}
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {guide.specialties.map((s) => (<Badge key={s} variant="outline" className="text-xs">{s}</Badge>))}
                          </div>
                          <div className="flex items-center justify-between pt-4 border-t">
                            <div className="flex items-center gap-1.5">
                              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                              <span className="font-bold text-base">{guide.rating_avg}</span>
                              <span className="text-sm text-muted-foreground">({guide.rating_count} {copy.reviews})</span>
                            </div>
                            <div>
                              <span className="text-xl font-bold text-primary">{guide.base_price}</span>
                              <span className="text-sm text-muted-foreground ms-1">{copy.perDay}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </SR>
            )}
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default GuidesPage;