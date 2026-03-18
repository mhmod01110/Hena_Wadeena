import { useEffect, useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { User, Mail, Phone, MapPin, Edit2, Camera, Shield, Building2, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { type AuthUser, clearAuthSession, userAPI } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition, GradientMesh } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { useI18n } from "@/i18n/I18nProvider";

const emptyForm = {
  full_name: "",
  email: "",
  phone: "",
  city: "",
  organization: "",
  language: "ar" as "ar" | "en",
};

const toFormData = (user: AuthUser) => ({
  full_name: user.full_name || "",
  email: user.email || "",
  phone: user.phone || "",
  city: user.city || "",
  organization: user.organization || "",
  language: (user.language === "en" ? "en" : "ar") as "ar" | "en",
});

const ProfilePage = () => {
  const { language: appLanguage } = useI18n();
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [editing, setEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState(emptyForm);

  const copy =
    appLanguage === "ar"
      ? {
          active: "نشط",
          suspended: "معلّق",
          fullName: "الاسم الكامل",
          email: "البريد الإلكتروني",
          phone: "رقم الهاتف",
          city: "المدينة",
          organization: "المؤسسة",
          language: "اللغة",
          save: "حفظ التغييرات",
          saving: "جاري الحفظ...",
          cancel: "إلغاء",
          editProfile: "تعديل الملف الشخصي",
          unspecified: "غير محددة",
          none: "لا توجد",
          updated: "تم تحديث الملف الشخصي بنجاح",
          updateFailed: "تعذر تحديث الملف الشخصي",
          arabic: "العربية",
          english: "English",
        }
      : {
          active: "Active",
          suspended: "Suspended",
          fullName: "Full Name",
          email: "Email",
          phone: "Phone",
          city: "City",
          organization: "Organization",
          language: "Language",
          save: "Save Changes",
          saving: "Saving...",
          cancel: "Cancel",
          editProfile: "Edit Profile",
          unspecified: "Not specified",
          none: "None",
          updated: "Profile updated successfully",
          updateFailed: "Failed to update profile",
          arabic: "Arabic",
          english: "English",
        };

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) {
      const parsed = JSON.parse(stored) as AuthUser;
      setUser(parsed);
      setFormData(toFormData(parsed));
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      if (!stored) {
        navigate("/login");
      }
      return;
    }

    userAPI.getMe()
      .then((profile) => {
        setUser(profile);
        setFormData(toFormData(profile));
        localStorage.setItem("user", JSON.stringify(profile));
      })
      .catch(() => {
        clearAuthSession();
        navigate("/login");
      });
  }, [navigate]);

  const roleLabels: Record<string, string> =
    appLanguage === "ar"
      ? {
          admin: "مدير",
          tourist: "سائح",
          investor: "مستثمر",
          farmer: "مزارع",
          guide: "مرشد سياحي",
          student: "طالب",
          driver: "سائق",
          citizen: "مواطن",
        }
      : {
          admin: "Admin",
          tourist: "Tourist",
          investor: "Investor",
          farmer: "Farmer",
          guide: "Tour Guide",
          student: "Student",
          driver: "Driver",
          citizen: "Citizen",
        };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await userAPI.updateMe({
        full_name: formData.full_name.trim() || undefined,
        email: formData.email.trim() || undefined,
        phone: formData.phone.trim() || undefined,
        city: formData.city.trim() || undefined,
        organization: formData.organization.trim() || undefined,
        language: formData.language,
      });
      localStorage.setItem("user", JSON.stringify(updated));
      setUser(updated);
      setFormData(toFormData(updated));
      setEditing(false);
      toast.success(copy.updated);
    } catch (err: any) {
      toast.error(err.message || copy.updateFailed);
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return (
      <Layout>
        <div className="container py-20 max-w-2xl space-y-6">
          <Skeleton h="h-64" className="rounded-2xl" />
          <Skeleton h="h-48" className="rounded-2xl" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <PageTransition>
        <section className="relative py-14 md:py-20 overflow-hidden">
          <GradientMesh />
          <div className="container relative px-4 max-w-2xl">
            <SR>
              <Card className="border-border/50 overflow-hidden rounded-2xl shadow-lg">
                <div className="bg-gradient-to-br from-primary/15 via-accent/10 to-background p-10 text-center relative">
                  <div className="mx-auto h-28 w-28 rounded-2xl bg-primary/20 flex items-center justify-center mb-5 relative shadow-xl group">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt="" className="h-28 w-28 rounded-2xl object-cover" />
                    ) : (
                      <User className="h-14 w-14 text-primary" />
                    )}
                    <button className="absolute -bottom-2 -left-2 h-10 w-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg hover:scale-110 transition-transform" type="button">
                      <Camera className="h-5 w-5" />
                    </button>
                  </div>
                  <h2 className="text-2xl font-bold text-foreground">{user.full_name}</h2>
                  <div className="flex items-center justify-center gap-2 mt-3">
                    <Badge variant="secondary" className="text-sm px-3 py-1">
                      <Shield className="h-3.5 w-3.5 ml-1" />
                      {roleLabels[user.role] || user.role}
                    </Badge>
                    <Badge variant={user.status === "active" ? "default" : "destructive"} className="text-sm px-3 py-1">
                      {user.status === "active" ? copy.active : copy.suspended}
                    </Badge>
                  </div>
                </div>

                <CardContent className="p-7 space-y-5">
                  {editing ? (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">{copy.fullName}</Label>
                        <Input id="name" className="h-12 rounded-xl" value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="email">{copy.email}</Label>
                          <Input id="email" type="email" className="h-12 rounded-xl" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone">{copy.phone}</Label>
                          <Input id="phone" className="h-12 rounded-xl" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="city">{copy.city}</Label>
                          <Input id="city" className="h-12 rounded-xl" value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="organization">{copy.organization}</Label>
                          <Input id="organization" className="h-12 rounded-xl" value={formData.organization} onChange={(e) => setFormData({ ...formData, organization: e.target.value })} />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>{copy.language}</Label>
                        <Select value={formData.language} onValueChange={(value) => setFormData({ ...formData, language: value as "ar" | "en" })}>
                          <SelectTrigger className="h-12 rounded-xl">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="ar">{copy.arabic}</SelectItem>
                            <SelectItem value="en">{copy.english}</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex gap-3">
                        <Button onClick={handleSave} disabled={isSaving} className="hover:scale-[1.02] transition-transform">{isSaving ? copy.saving : copy.save}</Button>
                        <Button variant="outline" onClick={() => { setEditing(false); setFormData(toFormData(user)); }}>{copy.cancel}</Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {[
                        { icon: Mail, label: copy.email, value: user.email || "-" },
                        { icon: Phone, label: copy.phone, value: user.phone || "-" },
                        { icon: MapPin, label: copy.city, value: user.city || copy.unspecified },
                        { icon: Building2, label: copy.organization, value: user.organization || copy.none },
                        { icon: Languages, label: copy.language, value: user.language === "ar" ? copy.arabic : copy.english },
                      ].map(({ icon: Icon, label, value }) => (
                        <div key={label} className="flex items-center gap-4 p-4 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors duration-200">
                          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                            <Icon className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">{label}</p>
                            <p className="font-semibold">{value}</p>
                          </div>
                        </div>
                      ))}
                      <Button onClick={() => setEditing(true)} className="w-full mt-4 h-12 hover:scale-[1.01] transition-transform" variant="outline">
                        <Edit2 className="h-4 w-4 ml-2" />{copy.editProfile}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </SR>
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default ProfilePage;