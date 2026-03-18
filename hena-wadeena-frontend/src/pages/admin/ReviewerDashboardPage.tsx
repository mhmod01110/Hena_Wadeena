import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { adminAPI, getCurrentUser, type AdminModerationItem } from "@/services/api";
import { toast } from "sonner";
import { useI18n } from "@/i18n/I18nProvider";

const allowedRoles = ["moderator", "reviewer", "admin", "super_admin"];

const ReviewerDashboardPage = () => {
  const { language } = useI18n();
  const navigate = useNavigate();
  const [user] = useState(() => getCurrentUser());
  const [items, setItems] = useState<AdminModerationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [resourceType, setResourceType] = useState("");

  const copy =
    language === "ar"
      ? {
          title: "لوحة المراجع",
          queueFilters: "مرشحات الطابور",
          resourceType: "نوع المورد",
          apply: "تطبيق",
          loading: "جارٍ التحميل...",
          queue: "طابور المراجعة",
          noItems: "لا توجد عناصر معلقة.",
          submittedBy: "مقدم بواسطة",
          subject: "العنوان",
          approve: "قبول",
          reject: "رفض",
          loadFail: "تعذر تحميل طابور المراجعة",
        }
      : {
          title: "Reviewer Dashboard",
          queueFilters: "Queue Filters",
          resourceType: "Resource Type",
          apply: "Apply",
          loading: "Loading...",
          queue: "Moderation Queue",
          noItems: "No pending moderation items.",
          submittedBy: "submitted by",
          subject: "Subject",
          approve: "Approve",
          reject: "Reject",
          loadFail: "Failed to load moderation queue",
        };

  const loadQueue = async () => {
    const res = await adminAPI.getModerationQueue({ page: 1, page_size: 50, status: "pending", resource_type: resourceType || undefined });
    setItems(res.data);
  };

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    if (!allowedRoles.includes(user.role)) {
      navigate("/");
      return;
    }

    loadQueue()
      .catch((err: Error) => toast.error(err.message || copy.loadFail))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const applyFilter = async () => {
    setLoading(true);
    try {
      await loadQueue();
    } catch (err: any) {
      toast.error(err.message || copy.loadFail);
    } finally {
      setLoading(false);
    }
  };

  const review = async (item: AdminModerationItem, status: "approved" | "rejected") => {
    setBusyId(item.id);
    try {
      const res = await adminAPI.reviewModerationItem(item.id, status, `Reviewed by ${user?.role || "reviewer"}`);
      setItems((prev) => prev.filter((i) => i.id !== item.id));
      toast.success(language === "ar" ? "تم تحديث الحالة" : `Item ${res.data.status}`);
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر تحديث الحالة" : "Failed to update moderation item"));
    } finally {
      setBusyId(null);
    }
  };

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
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

          <Card>
            <CardHeader>
              <CardTitle>{copy.queueFilters}</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="space-y-2 md:col-span-3">
                <Label>{copy.resourceType}</Label>
                <Input
                  placeholder="listing / guide / investment / provider"
                  value={resourceType}
                  onChange={(e) => setResourceType(e.target.value)}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={applyFilter} className="w-full" disabled={loading}>
                  {loading ? copy.loading : copy.apply}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{copy.queue}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {loading && <p className="text-sm text-muted-foreground">{copy.loading}</p>}
              {!loading && items.length === 0 && <p className="text-sm text-muted-foreground">{copy.noItems}</p>}
              {items.map((item) => (
                <div key={item.id} className="border rounded p-4 space-y-2">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold">{item.resource_type} / {item.resource_id}</p>
                      <p className="text-xs text-muted-foreground">{copy.submittedBy} {item.submitted_by}</p>
                    </div>
                    <Badge>{item.status}</Badge>
                  </div>
                  {item.subject_title && <p className="text-sm">{copy.subject}: {item.subject_title}</p>}
                  <p className="text-sm">{item.reason}</p>
                  <div className="flex gap-2 pt-1">
                    <Button size="sm" onClick={() => review(item, "approved")} disabled={busyId === item.id}>{copy.approve}</Button>
                    <Button size="sm" variant="destructive" onClick={() => review(item, "rejected")} disabled={busyId === item.id}>{copy.reject}</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  );
};

export default ReviewerDashboardPage;
