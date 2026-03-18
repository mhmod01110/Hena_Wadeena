"""Mock guide service endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

GUIDES = [
    {
        "id": 1, "user_id": "g1", "name": "أحمد السيد",
        "bio_ar": "مرشد سياحي معتمد بخبرة 10+ سنوات في رحلات السفاري الصحراوي والمواقع الأثرية بالوادي الجديد.",
        "languages": ["العربية", "الإنجليزية"], "specialties": ["سفاري صحراوي", "مواقع أثرية"],
        "license_number": "GD-2020-001", "license_verified": True,
        "base_price": 800, "rating_avg": 4.9, "rating_count": 87, "active": True,
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
    },
    {
        "id": 2, "user_id": "g2", "name": "فاطمة حسن",
        "bio_ar": "متخصصة في السياحة العلاجية والاستشفائية في واحات الوادي الجديد. خبرة 7 سنوات.",
        "languages": ["العربية", "الإنجليزية", "الفرنسية"], "specialties": ["سياحة علاجية", "واحات"],
        "license_number": "GD-2021-015", "license_verified": True,
        "base_price": 650, "rating_avg": 4.7, "rating_count": 45, "active": True,
        "image": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200",
    },
    {
        "id": 3, "user_id": "g3", "name": "محمد عبدالله",
        "bio_ar": "مرشد متخصص في رحلات التخييم وتصوير المناظر الطبيعية في الصحراء البيضاء والسوداء.",
        "languages": ["العربية", "الإنجليزية"], "specialties": ["تخييم", "تصوير فوتوغرافي"],
        "license_number": "GD-2019-042", "license_verified": True,
        "base_price": 750, "rating_avg": 4.8, "rating_count": 62, "active": True,
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200",
    },
]

PACKAGES = [
    {
        "id": 1, "guide_id": 1, "title_ar": "سفاري الصحراء البيضاء — 3 أيام",
        "description": "رحلة تخييم كاملة في الصحراء البيضاء تشمل نقل وأكل وتخييم تحت النجوم.",
        "duration_hrs": 72, "max_people": 8, "price": 3500,
        "includes": ["نقل من الخارجة", "وجبات", "خيمة", "دليل", "معدات تخييم"],
        "images": ["https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600"],
        "status": "active",
    },
    {
        "id": 2, "guide_id": 1, "title_ar": "جولة آثار الخارجة — يوم كامل",
        "description": "زيارة معبد هيبس ومقابر البجوات ومتحف الآثار مع شرح تفصيلي.",
        "duration_hrs": 8, "max_people": 12, "price": 800,
        "includes": ["نقل داخلي", "تذاكر دخول", "دليل", "مياه"],
        "images": ["https://images.unsplash.com/photo-1539768942893-daf53e448371?w=600"],
        "status": "active",
    },
    {
        "id": 3, "guide_id": 2, "title_ar": "رحلة استشفاء العيون الحارة",
        "description": "يوم كامل في العيون الحارة مع برنامج استرخاء وعلاج طبيعي.",
        "duration_hrs": 6, "max_people": 6, "price": 600,
        "includes": ["نقل", "حمام حار", "غداء صحي", "تدليك"],
        "images": ["https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600"],
        "status": "active",
    },
]

BOOKINGS = [
    {
        "id": "bk-001", "package_id": 1, "guide_id": 1, "guide_name": "أحمد السيد",
        "tourist_id": "b2c3d4e5", "package_title": "سفاري الصحراء البيضاء — 3 أيام",
        "booking_date": "2026-03-15", "start_time": "07:00",
        "people_count": 4, "total_price": 14000, "status": "confirmed",
        "created_at": "2026-03-07T10:00:00",
    },
    {
        "id": "bk-002", "package_id": 2, "guide_id": 1, "guide_name": "أحمد السيد",
        "tourist_id": "b2c3d4e5", "package_title": "جولة آثار الخارجة — يوم كامل",
        "booking_date": "2026-03-20", "start_time": "08:00",
        "people_count": 2, "total_price": 1600, "status": "pending",
        "created_at": "2026-03-07T12:00:00",
    },
]

REVIEWS = [
    {
        "id": "rv-001", "guide_id": 1, "tourist_id": "t1", "tourist_name": "سارة أحمد",
        "rating": 5, "comment": "رحلة رائعة! أحمد مرشد ممتاز ويعرف كل شيء عن الصحراء.",
        "guide_reply": "شكراً جزيلاً! سعيد إنك استمتعتي بالرحلة 🙏",
        "created_at": "2026-02-20",
    },
    {
        "id": "rv-002", "guide_id": 1, "tourist_id": "t2", "tourist_name": "محمد خالد",
        "rating": 5, "comment": "تجربة لا تُنسى في الصحراء البيضاء. التنظيم ممتاز والأكل لذيذ.",
        "guide_reply": None, "created_at": "2026-02-15",
    },
    {
        "id": "rv-003", "guide_id": 2, "tourist_id": "t3", "tourist_name": "ليلى حسين",
        "rating": 4, "comment": "تجربة العيون الحارة كانت مريحة جداً. أنصح بها بشدة.",
        "guide_reply": "شكراً ليلى! نتمنى نشوفك مرة تانية 💆‍♀️",
        "created_at": "2026-02-10",
    },
]


class BookingCreate(BaseModel):
    package_id: int
    guide_id: int
    booking_date: str
    start_time: str = "08:00"
    people_count: int = 1
    notes: Optional[str] = None


class ReviewCreate(BaseModel):
    rating: int
    comment: str


@router.get("")
def list_guides():
    return {"success": True, "data": GUIDES}


@router.get("/{guide_id}")
def get_guide(guide_id: int):
    for g in GUIDES:
        if g["id"] == guide_id:
            return {"success": True, "data": g}
    raise HTTPException(404, "Guide not found")


@router.get("/{guide_id}/packages")
def get_packages(guide_id: int):
    pkgs = [p for p in PACKAGES if p["guide_id"] == guide_id]
    return {"success": True, "data": pkgs}


@router.get("/{guide_id}/reviews")
def get_reviews(guide_id: int):
    revs = [r for r in REVIEWS if r["guide_id"] == guide_id]
    return {"success": True, "data": revs}


@router.post("/{guide_id}/reviews", status_code=201)
def create_review(guide_id: int, body: ReviewCreate):
    review = {
        "id": f"rv-{len(REVIEWS)+1:03d}", "guide_id": guide_id,
        "tourist_id": "current-user", "tourist_name": "أنت",
        "rating": body.rating, "comment": body.comment,
        "guide_reply": None, "created_at": "2026-03-07",
    }
    REVIEWS.append(review)
    return {"success": True, "data": review}


@router.post("/bookings", status_code=201)
def create_booking(body: BookingCreate):
    guide = next((g for g in GUIDES if g["id"] == body.guide_id), None)
    pkg = next((p for p in PACKAGES if p["id"] == body.package_id), None)
    booking = {
        "id": f"bk-{len(BOOKINGS)+1:03d}",
        "package_id": body.package_id, "guide_id": body.guide_id,
        "guide_name": guide["name"] if guide else "Unknown",
        "tourist_id": "current-user",
        "package_title": pkg["title_ar"] if pkg else "Unknown",
        "booking_date": body.booking_date, "start_time": body.start_time,
        "people_count": body.people_count,
        "total_price": (pkg["price"] if pkg else 0) * body.people_count,
        "status": "pending", "created_at": "2026-03-07T14:00:00",
    }
    BOOKINGS.append(booking)
    return {"success": True, "message": "تم إنشاء الحجز بنجاح", "data": booking}


@router.get("/bookings/my")
def my_bookings():
    return {"success": True, "data": BOOKINGS}
