import { useEffect, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  adminAPI,
  analyticsAPI,
  getCurrentUser,
  type AdminAnnouncement,
  type AdminModerationItem,
  type AdminUserRow,
  type AnalyticsKpis,
  type AnalyticsOverview,
  type FeatureFlag,
} from "@/services/api";
import { toast } from "sonner";
import { useI18n } from "@/i18n/I18nProvider";

const AdminDashboardPage = () => {
  const { language } = useI18n();
  const navigate = useNavigate();
  const [user] = useState(() => getCurrentUser());

  const copy =
    language === "ar"
      ? {
          title: "لوحة الإدارة",
          activeUsers: "المستخدمون النشطون",
          newUsers: "مستخدمون جدد",
          revenue: "الإيراد (جنيه)",
          pendingModeration: "مراجعات معلقة",
          platformOverview: "نظرة عامة على المنصة",
          totalEvents: "إجمالي الأحداث",
          listingsCreated: "قوائم تم إنشاؤها",
          bookingsCompleted: "حجوزات مكتملة",
          bookingCompletionRate: "معدل اكتمال الحجوزات",
          pendingQueue: "طابور المراجعة المعلق",
          noPending: "لا توجد عناصر معلقة.",
          approve: "قبول",
          reject: "رفض",
          users: "المستخدمون",
          verified: "موثق",
          unverified: "غير موثق",
          suspended: "موقوف",
          verify: "توثيق",
          suspend: "إيقاف",
          unsuspend: "رفع الإيقاف",
          announcements: "إعلانات المنصة",
          annTitle: "العنوان",
          annAudience: "الفئة",
          annBody: "المحتوى",
          createAnn: "إنشاء إعلان",
          creating: "جارٍ الإنشاء...",
          flags: "أعلام الميزات (Super Admin)",
          noFlags: "لا توجد أعلام ميزات.",
          disable: "تعطيل",
          enable: "تفعيل",
          loadFail: "تعذر تحميل لوحة الإدارة",
        }
      : {
          title: "Admin Dashboard",
          activeUsers: "Active Users",
          newUsers: "New Users",
          revenue: "Revenue (EGP)",
          pendingModeration: "Pending Moderation",
          platformOverview: "Platform Overview",
          totalEvents: "Total Events",
          listingsCreated: "Listings Created",
          bookingsCompleted: "Bookings Completed",
          bookingCompletionRate: "Booking Completion Rate",
          pendingQueue: "Pending Moderation Queue",
          noPending: "No pending items.",
          approve: "Approve",
          reject: "Reject",
          users: "Users",
          verified: "verified",
          unverified: "unverified",
          suspended: "Suspended",
          verify: "Verify",
          suspend: "Suspend",
          unsuspend: "Unsuspend",
          announcements: "Platform Announcements",
          annTitle: "Title",
          annAudience: "Audience",
          annBody: "Body",
          createAnn: "Create Announcement",
          creating: "Creating...",
          flags: "Feature Flags (Super Admin)",
          noFlags: "No feature flags found.",
          disable: "Disable",
          enable: "Enable",
          loadFail: "Failed to load admin dashboard",
        };

  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [kpis, setKpis] = useState<AnalyticsKpis | null>(null);
  const [users, setUsers] = useState<AdminUserRow[]>([]);
  const [moderation, setModeration] = useState<AdminModerationItem[]>([]);
  const [announcements, setAnnouncements] = useState<AdminAnnouncement[]>([]);
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);
  const [busyModerationId, setBusyModerationId] = useState<string | null>(null);
  const [creatingAnnouncement, setCreatingAnnouncement] = useState(false);
  const [announcementForm, setAnnouncementForm] = useState({
    title: "",
    body: "",
    audience: "all",
    priority: "normal" as "low" | "normal" | "high" | "urgent",
  });

  const isSuperAdmin = user?.role === "super_admin";

  const refresh = async () => {
    const tasks: Promise<unknown>[] = [
      analyticsAPI.getOverview().then((r) => setOverview(r.data)),
      analyticsAPI.getKpis().then((r) => setKpis(r.data)),
      adminAPI.getUsers({ page: 1, page_size: 20 }).then((r) => setUsers(r.data)),
      adminAPI.getModerationQueue({ status: "pending", page: 1, page_size: 10 }).then((r) => setModeration(r.data)),
      adminAPI.getAnnouncements({ page: 1, page_size: 10 }).then((r) => setAnnouncements(r.data)),
    ];

    if (isSuperAdmin) {
      tasks.push(adminAPI.getFlags().then((r) => setFlags(r.data)));
    }

    await Promise.all(tasks);
  };

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    if (!["admin", "super_admin"].includes(user.role)) {
      navigate("/");
      return;
    }

    refresh()
      .catch((err: Error) => toast.error(err.message || copy.loadFail))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const pendingCount = useMemo(() => moderation.filter((m) => m.status === "pending").length, [moderation]);

  const suspendUser = async (target: AdminUserRow) => {
    setBusyUserId(target.id);
    try {
      const res = await adminAPI.suspendUser(target.id, "Suspended from admin dashboard");
      setUsers((prev) => prev.map((u) => (u.id === target.id ? res.data : u)));
      toast.success(language === "ar" ? "تم إيقاف المستخدم" : "User suspended");
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر إيقاف المستخدم" : "Failed to suspend user"));
    } finally {
      setBusyUserId(null);
    }
  };

  const unsuspendUser = async (target: AdminUserRow) => {
    setBusyUserId(target.id);
    try {
      const res = await adminAPI.unsuspendUser(target.id);
      setUsers((prev) => prev.map((u) => (u.id === target.id ? res.data : u)));
      toast.success(language === "ar" ? "تم رفع الإيقاف" : "User unsuspended");
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر رفع الإيقاف" : "Failed to unsuspend user"));
    } finally {
      setBusyUserId(null);
    }
  };

  const verifyUser = async (target: AdminUserRow) => {
    setBusyUserId(target.id);
    try {
      const res = await adminAPI.verifyUser(target.id);
      setUsers((prev) => prev.map((u) => (u.id === target.id ? res.data : u)));
      toast.success(language === "ar" ? "تم توثيق المستخدم" : "User verified");
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر توثيق المستخدم" : "Failed to verify user"));
    } finally {
      setBusyUserId(null);
    }
  };

  const reviewModeration = async (item: AdminModerationItem, status: "approved" | "rejected") => {
    setBusyModerationId(item.id);
    try {
      await adminAPI.reviewModerationItem(item.id, status, `Reviewed by ${user?.role || "admin"}`);
      setModeration((prev) => prev.filter((m) => m.id !== item.id));
      toast.success(language === "ar" ? "تم تحديث المراجعة" : `Moderation item ${status}`);
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر تحديث المراجعة" : "Failed to review moderation item"));
    } finally {
      setBusyModerationId(null);
    }
  };

  const toggleFlag = async (flag: FeatureFlag) => {
    try {
      const res = await adminAPI.updateFlag(flag.key, {
        enabled: !flag.enabled,
        description: flag.description || undefined,
        rollout_percentage: flag.rollout_percentage,
        owner_group: flag.owner_group || undefined,
      });
      setFlags((prev) => prev.map((f) => (f.key === flag.key ? res.data : f)));
      toast.success(language === "ar" ? "تم تحديث الإعداد" : `Flag ${flag.key} updated`);
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر تحديث الإعداد" : "Failed to update feature flag"));
    }
  };

  const createAnnouncement = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingAnnouncement(true);
    try {
      const res = await adminAPI.createAnnouncement({
        title: announcementForm.title,
        body: announcementForm.body,
        audience: announcementForm.audience,
        priority: announcementForm.priority,
        status: "active",
      });
      setAnnouncements((prev) => [res.data, ...prev]);
      setAnnouncementForm({ title: "", body: "", audience: "all", priority: "normal" });
      toast.success(language === "ar" ? "تم إنشاء الإعلان" : "Announcement created");
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر إنشاء الإعلان" : "Failed to create announcement"));
    } finally {
      setCreatingAnnouncement(false);
    }
  };

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!["admin", "super_admin"].includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return (
    <Layout>
      <section className="py-10">
        <div className="container px-4 space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">{copy.title}</h1>
            <Badge>{user.role}</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader><CardTitle className="text-sm">{copy.activeUsers}</CardTitle></CardHeader>
              <CardContent><p className="text-3xl font-bold">{loading ? "..." : (kpis?.active_users ?? 0)}</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">{copy.newUsers}</CardTitle></CardHeader>
              <CardContent><p className="text-3xl font-bold">{loading ? "..." : (kpis?.new_users ?? 0)}</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">{copy.revenue}</CardTitle></CardHeader>
              <CardContent><p className="text-3xl font-bold">{loading ? "..." : (kpis?.revenue_total ?? 0).toLocaleString()}</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">{copy.pendingModeration}</CardTitle></CardHeader>
              <CardContent><p className="text-3xl font-bold">{loading ? "..." : pendingCount}</p></CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader><CardTitle>{copy.platformOverview}</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>{copy.totalEvents}: <strong>{overview?.total_events ?? 0}</strong></p>
                <p>{copy.listingsCreated}: <strong>{overview?.listings.created ?? 0}</strong></p>
                <p>{copy.bookingsCompleted}: <strong>{overview?.bookings.completed ?? 0}</strong></p>
                <p>{copy.bookingCompletionRate}: <strong>{kpis?.booking_completion_rate ?? 0}%</strong></p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>{copy.pendingQueue}</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {moderation.length === 0 && <p className="text-sm text-muted-foreground">{copy.noPending}</p>}
                {moderation.slice(0, 5).map((item) => (
                  <div key={item.id} className="border rounded p-3 text-sm space-y-2">
                    <p className="font-medium">{item.resource_type} / {item.resource_id}</p>
                    {item.subject_title && <p className="text-muted-foreground">{item.subject_title}</p>}
                    <p className="text-muted-foreground">{item.reason}</p>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => reviewModeration(item, "approved")} disabled={busyModerationId === item.id}>{copy.approve}</Button>
                      <Button size="sm" variant="destructive" onClick={() => reviewModeration(item, "rejected")} disabled={busyModerationId === item.id}>{copy.reject}</Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader><CardTitle>{copy.users}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {users.map((u) => (
                <div key={u.id} className="flex items-center justify-between gap-3 border rounded p-3">
                  <div>
                    <p className="font-medium">{u.display_name || u.email || u.id}</p>
                    <p className="text-xs text-muted-foreground">{u.role} {u.is_verified ? `• ${copy.verified}` : `• ${copy.unverified}`}</p>
                    {u.is_suspended && u.suspended_reason && (
                      <p className="text-xs text-red-600">{copy.suspended}: {u.suspended_reason}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {!u.is_verified && (
                      <Button size="sm" variant="outline" onClick={() => verifyUser(u)} disabled={busyUserId === u.id}>
                        {copy.verify}
                      </Button>
                    )}
                    {u.is_suspended ? (
                      isSuperAdmin && (
                        <Button size="sm" onClick={() => unsuspendUser(u)} disabled={busyUserId === u.id}>
                          {copy.unsuspend}
                        </Button>
                      )
                    ) : (
                      <Button size="sm" variant="destructive" onClick={() => suspendUser(u)} disabled={busyUserId === u.id}>
                        {copy.suspend}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>{copy.announcements}</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={createAnnouncement} className="space-y-3 border rounded p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="space-y-1 md:col-span-2">
                    <Label>{copy.annTitle}</Label>
                    <Input
                      value={announcementForm.title}
                      onChange={(e) => setAnnouncementForm((prev) => ({ ...prev, title: e.target.value }))}
                      placeholder={language === "ar" ? "تحديث خدمة" : "Service update"}
                      required
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>{copy.annAudience}</Label>
                    <Input
                      value={announcementForm.audience}
                      onChange={(e) => setAnnouncementForm((prev) => ({ ...prev, audience: e.target.value }))}
                      placeholder="all"
                      required
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label>{copy.annBody}</Label>
                  <Textarea
                    value={announcementForm.body}
                    onChange={(e) => setAnnouncementForm((prev) => ({ ...prev, body: e.target.value }))}
                    rows={3}
                    required
                  />
                </div>
                <Button type="submit" disabled={creatingAnnouncement}>
                  {creatingAnnouncement ? copy.creating : copy.createAnn}
                </Button>
              </form>

              <div className="space-y-2">
                {announcements.slice(0, 8).map((ann) => (
                  <div key={ann.id} className="border rounded p-3">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">{ann.title}</p>
                      <Badge variant="outline">{ann.status}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{ann.body}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {isSuperAdmin && (
            <Card>
              <CardHeader><CardTitle>{copy.flags}</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {flags.length === 0 && <p className="text-sm text-muted-foreground">{copy.noFlags}</p>}
                {flags.map((flag) => (
                  <div key={flag.key} className="flex items-center justify-between gap-3 border rounded p-3">
                    <div>
                      <p className="font-medium">{flag.key}</p>
                      <p className="text-xs text-muted-foreground">
                        rollout {flag.rollout_percentage}% {flag.owner_group ? `• ${flag.owner_group}` : ""}
                      </p>
                    </div>
                    <Button size="sm" variant={flag.enabled ? "destructive" : "default"} onClick={() => toggleFlag(flag)}>
                      {flag.enabled ? copy.disable : copy.enable}
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </Layout>
  );
};

export default AdminDashboardPage;
