import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate, Link } from "react-router-dom";
import { Mail, Lock, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { authAPI, persistAuthSession } from "@/services/api";
import { PageTransition, GradientMesh } from "@/components/motion/PageTransition";
import { SR } from "@/components/motion/ScrollReveal";
import { useI18n } from "@/i18n/I18nProvider";

const LoginPage = () => {
  const { t, isRTL } = useI18n();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await authAPI.login({ email: formData.email, password: formData.password });
      persistAuthSession(res.data);
      toast.success(res.message);
      navigate("/");
    } catch (err: any) {
      toast.error(err.message || t("login.failed"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <PageTransition>
        <section className="relative py-14 md:py-24 overflow-hidden">
          <GradientMesh />
          <div className="container relative px-4 max-w-md">
            <SR>
              <Card className="border-border/50 rounded-2xl shadow-xl overflow-hidden">
                <CardHeader className="text-center pb-2 pt-10">
                  <div className="mx-auto h-20 w-20 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-5 shadow-lg">
                    <LogIn className="h-10 w-10 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">{t("login.title")}</CardTitle>
                  <p className="text-muted-foreground mt-2">{t("login.subtitle")}</p>
                </CardHeader>

                <CardContent className="pt-8 pb-10 px-8">
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                      <Label htmlFor="email">{t("login.email")}</Label>
                      <div className="relative">
                        <Mail className={`absolute ${isRTL ? "right-4" : "left-4"} top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground`} />
                        <Input
                          id="email"
                          type="email"
                          placeholder={t("login.emailPlaceholder")}
                          value={formData.email}
                          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                          className={`${isRTL ? "pr-12" : "pl-12"} h-13 rounded-xl text-base`}
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password">{t("login.password")}</Label>
                      <div className="relative">
                        <Lock className={`absolute ${isRTL ? "right-4" : "left-4"} top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground`} />
                        <Input
                          id="password"
                          type="password"
                          placeholder={t("login.passwordPlaceholder")}
                          value={formData.password}
                          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                          className={`${isRTL ? "pr-12" : "pl-12"} h-13 rounded-xl text-base`}
                          required
                        />
                      </div>
                    </div>

                    <Button type="submit" className="w-full h-14 rounded-xl text-base hover:scale-[1.02] transition-transform" size="lg" disabled={isLoading}>
                      {isLoading ? t("login.loading") : t("login.submit")}
                    </Button>

                    <p className="text-center text-sm text-muted-foreground pt-2">
                      {t("login.noAccount")} {" "}
                      <Link to="/register" className="text-primary hover:underline font-semibold">
                        {t("login.registerNow")}
                      </Link>
                    </p>
                  </form>
                </CardContent>
              </Card>
            </SR>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default LoginPage;
