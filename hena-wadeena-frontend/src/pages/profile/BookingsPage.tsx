import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Calendar, Clock, Users, CalendarCheck, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { guidesAPI, getCurrentUser, type Booking } from "@/services/api";
import { SR } from "@/components/motion/ScrollReveal";
import { PageTransition, GradientMesh } from "@/components/motion/PageTransition";
import { Skeleton } from "@/components/motion/Skeleton";
import { useI18n } from "@/i18n/I18nProvider";
import { toast } from "sonner";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-500/10 text-yellow-700",
  confirmed: "bg-green-500/10 text-green-700",
  in_progress: "bg-sky-500/10 text-sky-700",
  completed: "bg-blue-500/10 text-blue-700",
  cancelled_tourist: "bg-red-500/10 text-red-700",
  cancelled_guide: "bg-red-500/10 text-red-700",
  no_show: "bg-orange-500/10 text-orange-700",
};

const statusLabels: Record<string, { en: string; ar: string }> = {
  pending: { en: "Pending", ar: "قيد الانتظار" },
  confirmed: { en: "Confirmed", ar: "مؤكد" },
  in_progress: { en: "In Progress", ar: "قيد التنفيذ" },
  completed: { en: "Completed", ar: "مكتمل" },
  cancelled_tourist: { en: "Cancelled by Tourist", ar: "أُلغي بواسطة السائح" },
  cancelled_guide: { en: "Cancelled by Guide", ar: "أُلغي بواسطة المرشد" },
  no_show: { en: "No Show", ar: "عدم حضور" },
};

type ReviewDraft = { rating: number; comment: string };

const GUIDE_ROLES = new Set(["guide", "admin", "super_admin", "reviewer"]);

const BookingsPage = () => {
  const { language } = useI18n();
  const navigate = useNavigate();
  const user = useMemo(() => getCurrentUser(), []);

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionBookingId, setActionBookingId] = useState<string | null>(null);
  const [reviewBookingId, setReviewBookingId] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, ReviewDraft>>({});

  const isGuideView = GUIDE_ROLES.has((user?.role || "tourist").toLowerCase());

  const copy =
    language === "ar"
      ? {
          title: isGuideView ? "الحجوزات الواردة" : "حجوزاتي",
          empty: "لا توجد حجوزات بعد.",
          withGuide: "مع",
          people: "أشخاص",
          currency: "جنيه",
          reviewTitle: "إضافة تقييم",
          reviewDone: "تم إرسال التقييم",
        }
      : {
          title: isGuideView ? "Incoming Bookings" : "My Bookings",
          empty: "No bookings yet.",
          withGuide: "with",
          people: "people",
          currency: "EGP",
          reviewTitle: "Submit Review",
          reviewDone: "Review submitted",
        };

  const loadBookings = useCallback(async () => {
    try {
      const res = await guidesAPI.getMyBookings();
      setBookings(res.data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load bookings");
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    loadBookings().finally(() => setLoading(false));
  }, [loadBookings, navigate]);

  const patchDraft = (bookingId: string, changes: Partial<ReviewDraft>) => {
    setDrafts((prev) => ({
      ...prev,
      [bookingId]: {
        rating: prev[bookingId]?.rating || 5,
        comment: prev[bookingId]?.comment || "",
        ...changes,
      },
    }));
  };

  const handleGuideAction = async (booking: Booking, action: "confirm" | "start" | "complete" | "no_show" | "cancel") => {
    setActionBookingId(booking.id);
    try {
      if (action === "confirm") {
        await guidesAPI.confirmBooking(booking.id);
      } else if (action === "start") {
        await guidesAPI.startBooking(booking.id);
      } else if (action === "complete") {
        await guidesAPI.completeBooking(booking.id);
      } else if (action === "no_show") {
        await guidesAPI.markNoShow(booking.id);
      } else {
        const reason = window.prompt("Cancellation reason (optional)") || undefined;
        await guidesAPI.cancelBooking(booking.id, reason);
      }
      await loadBookings();
    } catch (err: any) {
      toast.error(err.message || "Failed to update booking");
    } finally {
      setActionBookingId(null);
    }
  };

  const handleTouristCancel = async (booking: Booking) => {
    setActionBookingId(booking.id);
    try {
      const reason = window.prompt("Cancellation reason (optional)") || undefined;
      await guidesAPI.updateBookingStatus(booking.id, "cancelled", reason);
      await loadBookings();
    } catch (err: any) {
      toast.error(err.message || "Failed to cancel booking");
    } finally {
      setActionBookingId(null);
    }
  };

  const handleSubmitReview = async (booking: Booking) => {
    const draft = drafts[booking.id] || { rating: 5, comment: "" };
    if (!draft.comment.trim()) {
      toast.error("Please write a review comment");
      return;
    }

    setReviewBookingId(booking.id);
    try {
      await guidesAPI.createReview(booking.id, { rating: draft.rating, comment: draft.comment.trim() });
      toast.success("Review submitted");
      await loadBookings();
    } catch (err: any) {
      toast.error(err.message || "Failed to submit review");
    } finally {
      setReviewBookingId(null);
    }
  };

  return (
    <Layout>
      <PageTransition>
        <section className="relative py-14 md:py-20 overflow-hidden">
          <GradientMesh />
          <div className="container relative px-4 max-w-4xl">
            <SR>
              <div className="flex items-center gap-4 mb-10">
                <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <CalendarCheck className="h-7 w-7 text-primary" />
                </div>
                <h1 className="text-3xl md:text-4xl font-bold">{copy.title}</h1>
              </div>
            </SR>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} h="h-32" className="rounded-2xl" />
                ))}
              </div>
            ) : bookings.length === 0 ? (
              <SR>
                <Card className="rounded-2xl">
                  <CardContent className="p-14 text-center text-muted-foreground text-lg">{copy.empty}</CardContent>
                </Card>
              </SR>
            ) : (
              <div className="space-y-5">
                {bookings.map((b, idx) => {
                  const isTouristView = !isGuideView;
                  const canTouristCancel = isTouristView && ["pending", "confirmed", "in_progress"].includes(b.status);
                  const canSubmitReview = isTouristView && b.status === "completed" && !b.review_submitted;
                  const draft = drafts[b.id] || { rating: 5, comment: "" };

                  return (
                    <SR key={b.id} delay={idx * 60}>
                      <Card className="hover-lift rounded-2xl border-border/50">
                        <CardContent className="p-7 space-y-5">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="text-lg font-bold">{b.package_title}</h3>
                              <p className="text-sm text-muted-foreground mt-1">
                                {copy.withGuide} {b.guide_name}
                              </p>
                            </div>
                            <Badge className={`${statusColors[b.status] || ""} px-3 py-1`}>
                              {statusLabels[b.status]?.[language] || b.status}
                            </Badge>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                            <div className="flex items-center gap-2.5 text-muted-foreground">
                              <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center">
                                <Calendar className="h-4 w-4" />
                              </div>
                              {b.booking_date}
                            </div>
                            <div className="flex items-center gap-2.5 text-muted-foreground">
                              <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center">
                                <Clock className="h-4 w-4" />
                              </div>
                              {b.start_time}
                            </div>
                            <div className="flex items-center gap-2.5 text-muted-foreground">
                              <div className="h-8 w-8 rounded-lg bg-muted/50 flex items-center justify-center">
                                <Users className="h-4 w-4" />
                              </div>
                              {b.people_count} {copy.people}
                            </div>
                            <div className="text-muted-foreground">{b.duration_hrs} hrs</div>
                            <div className="font-bold text-primary text-left text-lg">
                              {b.total_price.toLocaleString()} {copy.currency}
                            </div>
                          </div>

                          {(b.cancellation_actor || b.cancellation_refund_percent !== null || b.guide_penalty) && (
                            <div className="rounded-lg border border-border p-3 text-sm text-muted-foreground">
                              {b.cancellation_actor && <div>Cancelled by: {b.cancellation_actor}</div>}
                              {typeof b.cancellation_refund_percent === "number" && (
                                <div>Refund: {b.cancellation_refund_percent}%</div>
                              )}
                              {b.guide_penalty && <div>Guide penalty applied</div>}
                              {b.cancelled_reason && <div>Reason: {b.cancelled_reason}</div>}
                            </div>
                          )}

                          {isGuideView && (
                            <div className="flex flex-wrap gap-2">
                              {b.status === "pending" && (
                                <Button
                                  size="sm"
                                  onClick={() => handleGuideAction(b, "confirm")}
                                  disabled={actionBookingId === b.id}
                                >
                                  Confirm
                                </Button>
                              )}
                              {b.status === "confirmed" && (
                                <>
                                  <Button
                                    size="sm"
                                    onClick={() => handleGuideAction(b, "start")}
                                    disabled={actionBookingId === b.id}
                                  >
                                    Start
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleGuideAction(b, "cancel")}
                                    disabled={actionBookingId === b.id}
                                  >
                                    Cancel
                                  </Button>
                                </>
                              )}
                              {b.status === "in_progress" && (
                                <>
                                  <Button
                                    size="sm"
                                    onClick={() => handleGuideAction(b, "complete")}
                                    disabled={actionBookingId === b.id}
                                  >
                                    Complete
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="secondary"
                                    onClick={() => handleGuideAction(b, "no_show")}
                                    disabled={actionBookingId === b.id}
                                  >
                                    Mark No-show
                                  </Button>
                                </>
                              )}
                            </div>
                          )}

                          {canTouristCancel && (
                            <div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleTouristCancel(b)}
                                disabled={actionBookingId === b.id}
                              >
                                Cancel Booking
                              </Button>
                            </div>
                          )}

                          {canSubmitReview && (
                            <div className="rounded-xl border border-border p-4 space-y-3">
                              <h4 className="font-semibold">{copy.reviewTitle}</h4>
                              <div className="grid grid-cols-1 md:grid-cols-5 gap-2 items-center">
                                <div className="md:col-span-2 text-sm text-muted-foreground inline-flex items-center gap-2">
                                  <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" /> Rating (1-5)
                                </div>
                                <Input
                                  type="number"
                                  min={1}
                                  max={5}
                                  value={draft.rating}
                                  onChange={(e) => patchDraft(b.id, { rating: Number(e.target.value || 5) })}
                                />
                              </div>
                              <Textarea
                                rows={3}
                                placeholder="Share your experience"
                                value={draft.comment}
                                onChange={(e) => patchDraft(b.id, { comment: e.target.value })}
                              />
                              <Button
                                size="sm"
                                onClick={() => handleSubmitReview(b)}
                                disabled={reviewBookingId === b.id}
                              >
                                {reviewBookingId === b.id ? "Submitting..." : "Submit Review"}
                              </Button>
                            </div>
                          )}

                          {isTouristView && b.status === "completed" && b.review_submitted && (
                            <div className="text-sm text-green-700">{copy.reviewDone}</div>
                          )}
                        </CardContent>
                      </Card>
                    </SR>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      </PageTransition>
    </Layout>
  );
};

export default BookingsPage;
