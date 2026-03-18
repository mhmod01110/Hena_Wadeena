"""Mock notification endpoints."""

from fastapi import APIRouter

router = APIRouter()

NOTIFICATIONS = [
    {
        "id": "n-001", "type": "booking_confirmed", "read_at": None,
        "title_ar": "تم تأكيد حجزك ✅", "body_ar": "رحلتك مع أحمد السيد في 15 مارس مؤكدة",
        "data": {"booking_id": "bk-001"}, "channel": ["push", "in_app"],
        "created_at": "2026-03-07T10:30:00",
    },
    {
        "id": "n-002", "type": "payment_received", "read_at": None,
        "title_ar": "تم استلام الدفعة 💰", "body_ar": "تم خصم 1,600 جنيه من محفظتك لحجز جولة آثار الخارجة",
        "data": {"transaction_id": "tx-002", "amount": 1600}, "channel": ["push", "email", "in_app"],
        "created_at": "2026-03-05T14:30:00",
    },
    {
        "id": "n-003", "type": "new_review", "read_at": "2026-03-06T08:00:00",
        "title_ar": "تقييم جديد ⭐", "body_ar": "سارة أحمد أعطتك تقييم 5 نجوم",
        "data": {"review_id": "rv-001", "rating": 5}, "channel": ["push", "in_app"],
        "created_at": "2026-03-04T16:00:00",
    },
    {
        "id": "n-004", "type": "kyc_approved", "read_at": "2026-03-03T12:00:00",
        "title_ar": "تم التحقق من هويتك ✅", "body_ar": "تم قبول وثائق التحقق الخاصة بك. يمكنك الآن استخدام جميع خدمات المنصة.",
        "data": {}, "channel": ["push", "email", "in_app"],
        "created_at": "2026-03-03T10:00:00",
    },
    {
        "id": "n-005", "type": "system", "read_at": None,
        "title_ar": "مرحباً بك في هنا وادينا! 🎉", "body_ar": "اكتشف أجمل معالم الوادي الجديد واستمتع بتجربة فريدة",
        "data": {}, "channel": ["in_app"],
        "created_at": "2026-03-01T08:00:00",
    },
]


@router.get("")
def get_notifications():
    return {"success": True, "data": NOTIFICATIONS}


@router.get("/unread-count")
def unread_count():
    count = sum(1 for n in NOTIFICATIONS if n["read_at"] is None)
    return {"success": True, "data": {"count": count}}


@router.put("/{notification_id}/read")
def mark_read(notification_id: str):
    for n in NOTIFICATIONS:
        if n["id"] == notification_id:
            n["read_at"] = "2026-03-07T15:00:00"
            return {"success": True, "message": "تم القراءة"}
    return {"success": False, "message": "Not found"}
