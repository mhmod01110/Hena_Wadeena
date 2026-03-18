import { useEffect, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { adminAPI, getCurrentUser, type AdminModerationItem } from "@/services/api";
import { toast } from "sonner";
import { useI18n } from "@/i18n/I18nProvider";

const allowedRoles = ["moderator", "reviewer", "admin", "super_admin"];

const ModeratorDashboardPage = () => {
  const { language } = useI18n();
  const navigate = useNavigate();
  const [user] = useState(() => getCurrentUser());

  const [items, setItems] = useState<AdminModerationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<"pending" | "approved" | "rejected">("pending");
  const [resourceType, setResourceType] = useState("");
  const [reporting, setReporting] = useState(false);
  const [reportForm, setReportForm] = useState({
    resource_type: "listing",
    resource_id: "",
    reason: "",
    subject_title: "",
    subject_category: "",
    source_service: "",
  });

  const copy =
    language === "ar"
      ? {
          title: "لوحة المشرف",
          queueFilters: "مرشحات الطابور",
          status: "الحالة",
          resourceType: "نوع المورد",
          apply: "تطبيق",
          loading: "جارٍ التحميل...",
          queue: "طابور المراجعة",
          noItems: "لا توجد عناصر لهذه المرشحات.",
          submittedBy: "مقدم بواسطة",
          subject: "العنوان",
          approve: "قبول",
          reject: "رفض",
          createReport: "إنشاء بلاغ مراجعة",
          reportResourceType: "نوع المورد",
          reportResourceId: "معرف المورد",
          reportSubjectTitle: "عنوان المورد",
          reportSubjectCategory: "تصنيف المورد",
          reportSourceService: "الخدمة المصدر",
          reportReason: "السبب",
          submitReport: "إرسال البلاغ",
          submitting: "جارٍ الإرسال...",
          loadFail: "تعذر تحميل طابور المراجعة",
        }
      : {
          title: "Moderator Dashboard",
          queueFilters: "Queue Filters",
          status: "Status",
          resourceType: "Resource Type",
          apply: "Apply",
          loading: "Loading...",
          queue: "Moderation Queue",
          noItems: "No items found for this filter.",
          submittedBy: "submitted by",
          subject: "Subject",
          approve: "Approve",
          reject: "Reject",
          createReport: "Create Moderation Report",
          reportResourceType: "Resource Type",
          reportResourceId: "Resource ID",
          reportSubjectTitle: "Subject Title",
          reportSubjectCategory: "Subject Category",
          reportSourceService: "Source Service",
          reportReason: "Reason",
          submitReport: "Submit Report",
          submitting: "Submitting...",
          loadFail: "Failed to load moderation queue",
        };

  const loadQueue = async () => {
    const res = await adminAPI.getModerationQueue({
      page: 1,
      page_size: 50,
      status: statusFilter,
      resource_type: resourceType || undefined,
    });
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

  const filteredCount = useMemo(() => items.length, [items]);

  const applyFilters = async () => {
    setLoading(true);
    try {
      await loadQueue();
    } catch (err: any) {
      toast.error(err.message || copy.loadFail);
    } finally {
      setLoading(false);
    }
  };

  const reviewItem = async (item: AdminModerationItem, status: "approved" | "rejected") => {
    setBusyId(item.id);
    try {
      await adminAPI.reviewModerationItem(item.id, status, `Reviewed by ${user?.role || "moderator"}`);
      setItems((prev) => prev.filter((x) => x.id !== item.id));
      toast.success(language === "ar" ? "تم تحديث الحالة" : `Item ${status}`);
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر تحديث الحالة" : "Failed to update moderation item"));
    } finally {
      setBusyId(null);
    }
  };

  const submitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setReporting(true);
    try {
      await adminAPI.reportContent({
        resource_type: reportForm.resource_type,
        resource_id: reportForm.resource_id,
        reason: reportForm.reason,
        subject_title: reportForm.subject_title || undefined,
        subject_category: reportForm.subject_category || undefined,
        source_service: reportForm.source_service || undefined,
      });
      toast.success(language === "ar" ? "تم إرسال البلاغ" : "Report submitted to moderation queue");
      setReportForm((prev) => ({ ...prev, resource_id: "", reason: "", subject_title: "", subject_category: "", source_service: "" }));
      await applyFilters();
    } catch (err: any) {
      toast.error(err.message || (language === "ar" ? "تعذر إرسال البلاغ" : "Failed to submit report"));
    } finally {
      setReporting(false);
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
              <div className="space-y-2">
                <Label>{copy.status}</Label>
                <select
                  className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as "pending" | "approved" | "rejected")}
                >
                  <option value="pending">pending</option>
                  <option value="approved">approved</option>
                  <option value="rejected">rejected</option>
                </select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>{copy.resourceType}</Label>
                <Input
                  placeholder="listing / guide / investment / provider"
                  value={resourceType}
                  onChange={(e) => setResourceType(e.target.value)}
                />
              </div>
              <div className="flex items-end">
                <Button className="w-full" onClick={applyFilters} disabled={loading}>
                  {loading ? copy.loading : `${copy.apply} (${filteredCount})`}
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
                    <Button
                      size="sm"
                      onClick={() => reviewItem(item, "approved")}
                      disabled={busyId === item.id || item.status !== "pending"}
                    >
                      {copy.approve}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => reviewItem(item, "rejected")}
                      disabled={busyId === item.id || item.status !== "pending"}
                    >
                      {copy.reject}
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{copy.createReport}</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={submitReport} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label>{copy.reportResourceType}</Label>
                    <Input
                      value={reportForm.resource_type}
                      onChange={(e) => setReportForm((prev) => ({ ...prev, resource_type: e.target.value }))}
                      placeholder="listing"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{copy.reportResourceId}</Label>
                    <Input
                      value={reportForm.resource_id}
                      onChange={(e) => setReportForm((prev) => ({ ...prev, resource_id: e.target.value }))}
                      placeholder="UUID or entity id"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="space-y-2">
                    <Label>{copy.reportSubjectTitle}</Label>
                    <Input
                      value={reportForm.subject_title}
                      onChange={(e) => setReportForm((prev) => ({ ...prev, subject_title: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{copy.reportSubjectCategory}</Label>
                    <Input
                      value={reportForm.subject_category}
                      onChange={(e) => setReportForm((prev) => ({ ...prev, subject_category: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{copy.reportSourceService}</Label>
                    <Input
                      value={reportForm.source_service}
                      onChange={(e) => setReportForm((prev) => ({ ...prev, source_service: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>{copy.reportReason}</Label>
                  <Textarea
                    value={reportForm.reason}
                    onChange={(e) => setReportForm((prev) => ({ ...prev, reason: e.target.value }))}
                    rows={4}
                    required
                  />
                </div>

                <Button type="submit" disabled={reporting}>
                  {reporting ? copy.submitting : copy.submitReport}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  );
};

export default ModeratorDashboardPage;
