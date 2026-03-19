import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { useParams, useNavigate } from "react-router-dom";
import { Star, Clock, Users, Shield } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { guidesAPI, type GuideProfile as GuideProfileType, type TourPackage, type Review } from "@/services/api";
import { useI18n } from "@/i18n/I18nProvider";

const GuideProfilePage = () => {
  const { language } = useI18n();
  const { id } = useParams();
  const navigate = useNavigate();
  const [guide, setGuide] = useState<GuideProfileType | null>(null);
  const [packages, setPackages] = useState<TourPackage[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);

  const copy =
    language === "ar"
      ? {
          loading: "جاري التحميل...",
          verified: "مرخص",
          reviewCount: (count: number) => `${count} تقييم`,
          pricePerDay: "جنيه/يوم",
          packages: "الرحلات المتاحة",
          hours: "ساعة",
          upToPeople: (count: number) => `حتى ${count} أفراد`,
          currencyPerPerson: "جنيه/فرد",
          bookNow: "احجز الآن",
          bookCustom: "احجز رحلة مخصصة",
          reviews: "التقييمات",
          noPackages: "لا توجد باقات متاحة حاليا.",
          noReviews: "لا توجد تقييمات بعد.",
          guideReply: "رد المرشد:",
        }
      : {
          loading: "Loading...",
          verified: "Verified",
          reviewCount: (count: number) => `${count} reviews`,
          pricePerDay: "EGP/day",
          packages: "Available Tours",
          hours: "hrs",
          upToPeople: (count: number) => `Up to ${count} people`,
          currencyPerPerson: "EGP/person",
          bookNow: "Book Now",
          bookCustom: "Book Custom Tour",
          reviews: "Reviews",
          noPackages: "No active packages yet.",
          noReviews: "No reviews yet.",
          guideReply: "Guide reply:",
        };

  useEffect(() => {
    const gid = String(id || "");
    guidesAPI.getGuide(gid).then((r) => setGuide(r.data)).catch(() => {});
    guidesAPI.getPackages(gid).then((r) => setPackages(r.data)).catch(() => {});
    guidesAPI.getReviews(gid).then((r) => setReviews(r.data)).catch(() => {});
  }, [id]);

  if (!guide) {
    return (
      <Layout>
        <div className="container py-20 text-center">{copy.loading}</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <section className="py-12 md:py-20">
        <div className="container px-4 max-w-4xl space-y-8">
          <Card className="overflow-hidden">
            <div className="bg-gradient-to-br from-primary/10 to-accent/10 p-8">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <img src={guide.image} alt={guide.name} className="h-32 w-32 rounded-full object-cover border-4 border-white shadow-lg" />
                <div className="text-center md:text-start flex-1">
                  <h1 className="text-3xl font-bold mb-2">{guide.name}</h1>
                  <p className="text-muted-foreground mb-3">{guide.bio_ar}</p>
                  <div className="flex flex-wrap justify-center md:justify-start gap-2">
                    {guide.license_verified && (
                      <Badge className="bg-green-500 text-white">
                        <Shield className="h-3 w-3 me-1" />
                        {copy.verified}
                      </Badge>
                    )}
                    {guide.languages.map((l) => (
                      <Badge key={l} variant="outline">
                        {l}
                      </Badge>
                    ))}
                    {guide.specialties.map((s) => (
                      <Badge key={s} variant="secondary">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="text-center p-4 bg-white/50 rounded-xl border">
                  <div className="flex items-center gap-1 justify-center mb-1">
                    <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                    <span className="text-2xl font-bold">{guide.rating_avg}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{copy.reviewCount(guide.rating_count)}</p>
                  <p className="text-lg font-bold text-primary mt-2">
                    {guide.base_price} {copy.pricePerDay}
                  </p>
                  <Button className="mt-3" size="sm" onClick={() => navigate(`/tourism/guide-booking/${guide.id}`)}>
                    {copy.bookCustom}
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          <div>
            <h2 className="text-2xl font-bold mb-4">{copy.packages}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {packages.map((pkg) => (
                <Card key={pkg.id} className="hover:shadow-lg transition-all">
                  <CardContent className="p-0">
                    {pkg.images[0] && <img src={pkg.images[0]} alt="" className="w-full h-40 object-cover rounded-t-lg" />}
                    <div className="p-5 space-y-3">
                      <h3 className="text-lg font-bold">{pkg.title_ar}</h3>
                      <p className="text-sm text-muted-foreground">{pkg.description}</p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {pkg.duration_hrs} {copy.hours}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {copy.upToPeople(pkg.max_people)}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {pkg.includes.map((i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {i}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center justify-between pt-3 border-t">
                        <span className="text-2xl font-bold text-primary">
                          {pkg.price} <span className="text-sm font-normal">{copy.currencyPerPerson}</span>
                        </span>
                        <Button onClick={() => navigate(`/tourism/guide-booking/${guide.id}?packageId=${pkg.id}`)}>{copy.bookNow}</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {!packages.length && (
              <Card>
                <CardContent className="p-5 text-sm text-muted-foreground">{copy.noPackages}</CardContent>
              </Card>
            )}
          </div>

          <div>
            <h2 className="text-2xl font-bold mb-4">{copy.reviews}</h2>
            <div className="space-y-3">
              {reviews.map((r) => (
                <Card key={r.id}>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary">
                        {r.tourist_name[0]}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold">{r.tourist_name}</p>
                        <p className="text-xs text-muted-foreground">{r.created_at}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        {Array.from({ length: r.rating }, (_, i) => (
                          <Star key={i} className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm">{r.comment}</p>
                    {r.guide_reply && (
                      <div className="mt-3 p-3 bg-muted/30 rounded-lg">
                        <p className="text-xs font-semibold text-primary mb-1">{copy.guideReply}</p>
                        <p className="text-sm">{r.guide_reply}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
            {!reviews.length && (
              <Card>
                <CardContent className="p-5 text-sm text-muted-foreground">{copy.noReviews}</CardContent>
              </Card>
            )}
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default GuideProfilePage;
