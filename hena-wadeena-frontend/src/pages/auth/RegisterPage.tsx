import { useMemo, useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate, Link } from "react-router-dom";
import { User, Mail, Lock, Phone, Building2, Check, ArrowRight, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DocumentUpload } from "@/components/auth/DocumentUpload";
import { toast } from "sonner";
import { authAPI, persistAuthSession } from "@/services/api";
import { PageTransition, GradientMesh } from "@/components/motion/PageTransition";
import { SR } from "@/components/motion/ScrollReveal";
import { useI18n } from "@/i18n/I18nProvider";

interface UploadedDocuments {
  national_id?: File;
  license?: File;
  certificate?: File;
}

const roleValues = ["tourist", "student", "investor", "local_citizen", "guide", "merchant"] as const;
type RoleValue = (typeof roleValues)[number];

const RegisterPage = () => {
  const { t, isRTL } = useI18n();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    role: "",
    city: "",
    organization: "",
  });

  const [documents, setDocuments] = useState<UploadedDocuments>({});

  const roles = useMemo(
    () =>
      roleValues.map((value) => ({
        value,
        label: t(`register.roles.${value}.label`),
        description: t(`register.roles.${value}.description`),
      })),
    [t],
  );

  const handleDocUpload = (docType: keyof UploadedDocuments, file: File) => {
    setDocuments((prev) => ({ ...prev, [docType]: file }));
  };

  const buildRegistrationDocuments = () =>
    Object.entries(documents)
      .filter((entry): entry is [string, File] => Boolean(entry[1]))
      .map(([doc_type, file]) => ({
        doc_type,
        file_name: file.name,
        mime_type: file.type,
        size_bytes: file.size,
      }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error(t("register.errors.passwordMismatch"));
      return;
    }

    setIsLoading(true);
    try {
      const res = await authAPI.register({
        email: formData.email,
        phone: formData.phone,
        full_name: formData.fullName,
        password: formData.password,
        role: (formData.role as RoleValue) || "tourist",
        city: formData.city || undefined,
        organization: formData.organization || undefined,
        documents: buildRegistrationDocuments(),
      });
      persistAuthSession(res.data);
      toast.success(res.message || t("register.create"));
      navigate("/");
    } catch (err: any) {
      toast.error(err.message || t("register.errors.registrationFailed"));
    } finally {
      setIsLoading(false);
    }
  };

  const nextStep = () => {
    if (step === 1) {
      if (!formData.fullName || !formData.email || !formData.phone || !formData.password) {
        toast.error(t("register.errors.fillRequired"));
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        toast.error(t("register.errors.passwordMismatch"));
        return;
      }
    }

    if (step === 2 && !formData.role) {
      toast.error(t("register.errors.chooseRole"));
      return;
    }

    setStep((prev) => prev + 1);
  };

  return (
    <Layout>
      <PageTransition>
        <section className="relative py-10 md:py-14 overflow-hidden">
          <GradientMesh />
          <div className="container relative px-4 max-w-xl">
            <SR>
              <div className="flex items-center justify-center gap-4 mb-10">
                {[1, 2, 3].map((s) => (
                  <div key={s} className="flex items-center gap-2">
                    <div
                      className={`h-10 w-10 rounded-xl flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                        step > s
                          ? "bg-primary text-primary-foreground shadow-lg"
                          : step === s
                            ? "bg-primary text-primary-foreground shadow-lg scale-110"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {step > s ? <Check className="h-5 w-5" /> : s}
                    </div>
                    <span className="text-sm font-semibold hidden sm:inline">
                      {s === 1 ? t("register.steps.personal") : s === 2 ? t("register.steps.role") : t("register.steps.documents")}
                    </span>
                    {s < 3 && <div className="h-px w-10 bg-border" />}
                  </div>
                ))}
              </div>
            </SR>

            <SR delay={100}>
              <Card className="border-border/50 rounded-2xl shadow-xl overflow-hidden">
                <CardHeader className="text-center pb-6 bg-gradient-to-b from-muted/50 to-transparent">
                  <CardTitle className="text-2xl font-bold">{t("register.title")}</CardTitle>
                  <p className="text-muted-foreground">{t("register.subtitle")}</p>
                </CardHeader>

                <CardContent className="p-6">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {step === 1 && (
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="fullName">{t("register.fullName")}</Label>
                          <div className="relative mt-1">
                            <User className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="fullName" placeholder={t("register.fullNamePlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.fullName} onChange={(e) => setFormData({ ...formData, fullName: e.target.value })} />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="email">{t("register.email")}</Label>
                          <div className="relative mt-1">
                            <Mail className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="email" type="email" placeholder={t("register.email")} className={isRTL ? "pr-10" : "pl-10"} value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="phone">{t("register.phone")}</Label>
                          <div className="relative mt-1">
                            <Phone className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="phone" placeholder={t("register.phonePlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="password">{t("register.password")}</Label>
                          <div className="relative mt-1">
                            <Lock className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="password" type="password" placeholder={t("register.passwordPlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="confirmPassword">{t("register.confirmPassword")}</Label>
                          <div className="relative mt-1">
                            <Lock className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="confirmPassword" type="password" placeholder={t("register.confirmPasswordPlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.confirmPassword} onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })} />
                          </div>
                        </div>

                        <Button type="button" className="w-full" onClick={nextStep}>
                          {t("register.next")}
                          <ArrowLeft className={`h-4 w-4 ${isRTL ? "ml-2" : "ml-2 rotate-180"}`} />
                        </Button>
                      </div>
                    )}

                    {step === 2 && (
                      <div className="space-y-4">
                        <div>
                          <Label>{t("register.accountType")}</Label>
                          <Select value={formData.role} onValueChange={(role) => setFormData({ ...formData, role })}>
                            <SelectTrigger className="mt-1">
                              <SelectValue placeholder={t("register.selectRole")} />
                            </SelectTrigger>
                            <SelectContent>
                              {roles.map((role) => (
                                <SelectItem key={role.value} value={role.value}>
                                  {role.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          {formData.role && (
                            <p className="text-sm text-muted-foreground mt-2">{roles.find((r) => r.value === formData.role)?.description}</p>
                          )}
                        </div>

                        <div>
                          <Label htmlFor="city">{t("register.city")}</Label>
                          <div className="relative mt-1">
                            <Building2 className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="city" placeholder={t("register.cityPlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} />
                          </div>
                        </div>

                        <div>
                          <Label htmlFor="organization">{t("register.organization")}</Label>
                          <div className="relative mt-1">
                            <Building2 className={`absolute ${isRTL ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground`} />
                            <Input id="organization" placeholder={t("register.organizationPlaceholder")} className={isRTL ? "pr-10" : "pl-10"} value={formData.organization} onChange={(e) => setFormData({ ...formData, organization: e.target.value })} />
                          </div>
                        </div>

                        <div className="flex gap-3">
                          <Button type="button" variant="outline" className="flex-1" onClick={() => setStep(1)}>
                            <ArrowRight className={`h-4 w-4 ${isRTL ? "mr-2" : "mr-2 rotate-180"}`} />
                            {t("register.back")}
                          </Button>
                          <Button type="button" className="flex-1" onClick={nextStep}>
                            {t("register.next")}
                            <ArrowLeft className={`h-4 w-4 ${isRTL ? "ml-2" : "ml-2 rotate-180"}`} />
                          </Button>
                        </div>
                      </div>
                    )}

                    {step === 3 && (
                      <div className="space-y-4">
                        <DocumentUpload docType="national_id" label={t("register.docs.nationalId")} uploadedFile={documents.national_id} onUpload={(file) => handleDocUpload("national_id", file)} />

                        {formData.role === "guide" && (
                          <DocumentUpload docType="license" label={t("register.docs.guideLicense")} uploadedFile={documents.license} onUpload={(file) => handleDocUpload("license", file)} />
                        )}

                        {["student", "investor", "merchant"].includes(formData.role) && (
                          <DocumentUpload docType="certificate" label={t("register.docs.supportingCertificate")} uploadedFile={documents.certificate} onUpload={(file) => handleDocUpload("certificate", file)} />
                        )}

                        <div className="bg-muted/50 rounded-lg p-4 space-y-2">
                          <h4 className="font-semibold mb-3">{t("register.summary")}</h4>
                          <div className="flex justify-between text-sm"><span className="text-muted-foreground">{t("register.summaryName")}</span><span>{formData.fullName}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-muted-foreground">{t("register.summaryEmail")}</span><span>{formData.email}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-muted-foreground">{t("register.summaryPhone")}</span><span>{formData.phone}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-muted-foreground">{t("register.summaryRole")}</span><span>{roles.find((r) => r.value === formData.role)?.label || roles[0].label}</span></div>
                        </div>

                        <div className="flex gap-3">
                          <Button type="button" variant="outline" className="flex-1" onClick={() => setStep(2)}>
                            <ArrowRight className={`h-4 w-4 ${isRTL ? "mr-2" : "mr-2 rotate-180"}`} />
                            {t("register.back")}
                          </Button>
                          <Button type="submit" className="flex-1" size="lg" disabled={isLoading}>
                            {isLoading ? t("register.creating") : t("register.create")}
                          </Button>
                        </div>
                      </div>
                    )}
                  </form>

                  <p className="text-center text-sm text-muted-foreground mt-6">
                    {t("register.alreadyHave")} {" "}
                    <Link to="/login" className="text-primary font-semibold hover:underline">
                      {t("register.signIn")}
                    </Link>
                  </p>
                </CardContent>
              </Card>
            </SR>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default RegisterPage;
