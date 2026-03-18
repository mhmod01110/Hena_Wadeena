import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { Search, TrendingUp, TrendingDown, Minus, MapPin, Star, Phone, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { marketAPI, type PriceItem, type Supplier } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { PageHero } from "@/components/layout/PageHero";
import heroMarketplace from "@/assets/hero-marketplace.jpg";
import { useI18n } from "@/i18n/I18nProvider";

const MarketplacePage = () => {
  const { language, isRTL } = useI18n();
  const navigate = useNavigate();
  const [selectedCity, setSelectedCity] = useState("kharga");
  const [searchQuery, setSearchQuery] = useState("");
  const [priceData, setPriceData] = useState<PriceItem[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);

  const copy =
    language === "ar"
      ? {
          heroAlt: "البورصة والأسعار",
          badge: "البورصة والأسعار",
          title: "البورصة والأسعار",
          subtitle: "أسعار المنتجات المحلية، دليل الموردين، والتواصل المباشر",
          tabs: { prices: "لوحة الأسعار", suppliers: "دليل الموردين" },
          chooseCity: "اختر المدينة",
          searchProduct: "ابحث عن منتج...",
          pricesIn: "أسعار",
          lastUpdate: "آخر تحديث: اليوم 10:30 ص",
          table: { product: "المنتج", category: "التصنيف", price: "السعر", change: "التغير" },
          currencyPer: "جنيه/{{unit}}",
          searchSupplier: "ابحث عن مورد...",
          verified: "موثق",
          viewProfile: "عرض الملف",
          contact: "تواصل",
          contactAlert: (name: string) => `للتواصل مع ${name}: اتصل أو أرسل واتساب`,
        }
      : {
          heroAlt: "Marketplace and Prices",
          badge: "Marketplace and Prices",
          title: "Marketplace and Prices",
          subtitle: "Local product prices, supplier directory, and direct contact",
          tabs: { prices: "Price Board", suppliers: "Supplier Directory" },
          chooseCity: "Choose city",
          searchProduct: "Search products...",
          pricesIn: "Prices in",
          lastUpdate: "Last update: Today 10:30 AM",
          table: { product: "Product", category: "Category", price: "Price", change: "Change" },
          currencyPer: "EGP/{{unit}}",
          searchSupplier: "Search suppliers...",
          verified: "Verified",
          viewProfile: "View Profile",
          contact: "Contact",
          contactAlert: (name: string) => `Contact ${name}: call or send WhatsApp`,
        };

  const cities =
    language === "ar"
      ? [
          { id: "kharga", name: "الخارجة" },
          { id: "dakhla", name: "الداخلة" },
          { id: "farafra", name: "الفرافرة" },
          { id: "paris", name: "باريس" },
        ]
      : [
          { id: "kharga", name: "Kharga" },
          { id: "dakhla", name: "Dakhla" },
          { id: "farafra", name: "Farafra" },
          { id: "paris", name: "Paris" },
        ];

  useEffect(() => {
    Promise.all([
      marketAPI.getPrices().then((r) => setPriceData(r.data)),
      marketAPI.getSuppliers().then((r) => setSuppliers(r.data)),
    ]).finally(() => setLoading(false));
  }, []);

  const normalizedQuery = searchQuery.trim().toLowerCase();
  const filteredProducts = priceData.filter((p) => {
    if (!normalizedQuery) return true;
    return p.name.toLowerCase().includes(normalizedQuery) || p.category.toLowerCase().includes(normalizedQuery);
  });

  return (
    <Layout>
      <PageTransition>
        <PageHero image={heroMarketplace} alt={copy.heroAlt}>
          <SR>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
              <BarChart3 className="h-5 w-5 text-accent" />
              <span className="text-sm font-semibold text-card">{copy.badge}</span>
            </div>
          </SR>
          <SR delay={100}>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-card mb-5">{copy.title}</h1>
          </SR>
          <SR delay={200}>
            <p className="text-lg md:text-xl text-card/90 mb-8">{copy.subtitle}</p>
          </SR>
        </PageHero>

        <section className="py-14">
          <div className="container px-4">
            <Tabs defaultValue="prices" className="w-full">
              <SR>
                <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-10 h-12 rounded-xl">
                  <TabsTrigger value="prices" className="rounded-lg text-sm font-semibold">{copy.tabs.prices}</TabsTrigger>
                  <TabsTrigger value="suppliers" className="rounded-lg text-sm font-semibold">{copy.tabs.suppliers}</TabsTrigger>
                </TabsList>
              </SR>

              <TabsContent value="prices" className="space-y-6">
                <SR>
                  <div className="flex flex-col md:flex-row gap-4">
                    <Select value={selectedCity} onValueChange={setSelectedCity}>
                      <SelectTrigger className="w-full md:w-48 h-12 rounded-xl"><SelectValue placeholder={copy.chooseCity} /></SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (<SelectItem key={city.id} value={city.id}>{city.name}</SelectItem>))}
                      </SelectContent>
                    </Select>
                    <div className="relative flex-1">
                      <Search className={`absolute top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
                      <Input
                        placeholder={copy.searchProduct}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className={`h-12 rounded-xl ${isRTL ? "pr-12" : "pl-12"}`}
                      />
                    </div>
                  </div>
                </SR>

                <SR delay={150}>
                  <Card className="border-border/50 overflow-hidden rounded-2xl shadow-lg">
                    <div className="bg-primary/5 px-6 py-5 border-b border-border">
                      <div className="flex items-center justify-between">
                        <h3 className="font-bold text-foreground text-lg">{copy.pricesIn} {cities.find((c) => c.id === selectedCity)?.name}</h3>
                        <span className="text-sm text-muted-foreground">{copy.lastUpdate}</span>
                      </div>
                    </div>
                    <CardContent className="p-0">
                      {loading ? (
                        <div className="p-6 space-y-4">{[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} h="h-12" />)}</div>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="border-b border-border bg-muted/30">
                                <th className="text-start py-5 px-6 text-sm font-semibold text-muted-foreground">{copy.table.product}</th>
                                <th className="text-start py-5 px-6 text-sm font-semibold text-muted-foreground">{copy.table.category}</th>
                                <th className="text-start py-5 px-6 text-sm font-semibold text-muted-foreground">{copy.table.price}</th>
                                <th className="text-start py-5 px-6 text-sm font-semibold text-muted-foreground">{copy.table.change}</th>
                              </tr>
                            </thead>
                            <tbody>
                              {filteredProducts.map((item, index) => (
                                <tr key={item.id || item.name} className={`hover:bg-muted/20 transition-colors duration-200 ${index !== filteredProducts.length - 1 ? "border-b border-border/50" : ""}`}>
                                  <td className="py-5 px-6"><span className="font-semibold text-foreground">{item.name}</span></td>
                                  <td className="py-5 px-6"><Badge variant="outline">{item.category}</Badge></td>
                                  <td className="py-5 px-6">
                                    <span className="font-bold text-lg text-foreground">{item.price}</span>
                                    <span className="text-sm text-muted-foreground ms-1">{copy.currencyPer.replace("{{unit}}", item.unit)}</span>
                                  </td>
                                  <td className="py-5 px-6">
                                    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold ${item.change > 0 ? "bg-primary/10 text-primary" : item.change < 0 ? "bg-destructive/10 text-destructive" : "bg-muted text-muted-foreground"}`}>
                                      {item.change > 0 ? <TrendingUp className="h-4 w-4" /> : item.change < 0 ? <TrendingDown className="h-4 w-4" /> : <Minus className="h-4 w-4" />}
                                      {Math.abs(item.change)}%
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </SR>
              </TabsContent>

              <TabsContent value="suppliers" className="space-y-6">
                <SR>
                  <div className="relative max-w-md">
                    <Search className={`absolute top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground ${isRTL ? "right-4" : "left-4"}`} />
                    <Input placeholder={copy.searchSupplier} className={`h-12 rounded-xl ${isRTL ? "pr-12" : "pl-12"}`} />
                  </div>
                </SR>

                {loading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[1, 2, 3, 4].map((i) => <Skeleton key={i} h="h-56" className="rounded-2xl" />)}
                  </div>
                ) : (
                  <SR stagger>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
                      {suppliers.map((supplier) => (
                        <Card key={supplier.id} className="border-border/50 hover:border-primary/40 hover-lift rounded-2xl">
                          <CardContent className="p-7">
                            <div className="flex items-start justify-between mb-5">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <h3 className="text-lg font-bold text-foreground">{supplier.name}</h3>
                                  {supplier.verified && (<Badge className="bg-primary/10 text-primary">{copy.verified}</Badge>)}
                                </div>
                                <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                  <MapPin className="h-4 w-4" />{supplier.city}
                                </div>
                              </div>
                              <div className="flex items-center gap-1.5 text-accent">
                                <Star className="h-5 w-5 fill-current" />
                                <span className="font-bold text-base">{supplier.rating}</span>
                                <span className="text-sm text-muted-foreground">({supplier.reviews})</span>
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-1.5 mb-5">
                              {supplier.specialties.map((specialty) => (<Badge key={specialty} variant="secondary">{specialty}</Badge>))}
                            </div>
                            <div className="flex gap-3">
                              <Button variant="outline" className="flex-1 hover:scale-[1.02] transition-transform" onClick={() => navigate(`/marketplace/supplier/${supplier.id}`)}>{copy.viewProfile}</Button>
                              <Button className="flex-1 hover:scale-[1.02] transition-transform" onClick={() => alert(copy.contactAlert(supplier.name))}>
                                <Phone className={`h-4 w-4 ${isRTL ? "ml-2" : "mr-2"}`} />{copy.contact}
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </SR>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default MarketplacePage;