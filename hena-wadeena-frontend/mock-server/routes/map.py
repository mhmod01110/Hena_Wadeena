"""Mock map/POI endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

POIS = [
    {
        "id": 1, "name_ar": "معبد هيبس", "name_en": "Hibis Temple",
        "category": "landmark", "description": "أقدم معبد في الواحات، يعود للعصر الصاوي",
        "address": "الخارجة، الوادي الجديد", "lat": 25.4510, "lng": 30.5434,
        "phone": "092-7921111", "rating_avg": 4.8, "rating_count": 234,
        "images": ["https://images.unsplash.com/photo-1539768942893-daf53e448371?w=400"],
        "status": "approved",
    },
    {
        "id": 2, "name_ar": "مستشفى الخارجة العام", "name_en": "Kharga General Hospital",
        "category": "government", "description": "المستشفى الرئيسي في مدينة الخارجة",
        "address": "شارع الجمهورية، الخارجة", "lat": 25.4400, "lng": 30.5500,
        "phone": "092-7922222", "rating_avg": 3.5, "rating_count": 89,
        "images": [], "status": "approved",
    },
    {
        "id": 3, "name_ar": "فندق بايونير", "name_en": "Pioneers Hotel",
        "category": "hotel", "description": "فندق 4 نجوم في قلب الخارجة",
        "address": "شارع عبد الناصر، الخارجة", "lat": 25.4450, "lng": 30.5520,
        "phone": "092-7923333", "rating_avg": 4.2, "rating_count": 156,
        "images": ["https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"],
        "status": "approved",
    },
    {
        "id": 4, "name_ar": "مطعم الواحة", "name_en": "Al-Waha Restaurant",
        "category": "restaurant", "description": "مطعم شعبي يقدم أكلات محلية أصيلة",
        "address": "وسط البلد، الخارجة", "lat": 25.4420, "lng": 30.5510,
        "phone": "01012345678", "rating_avg": 4.5, "rating_count": 312,
        "images": [], "status": "approved",
    },
    {
        "id": 5, "name_ar": "مقابر البجوات", "name_en": "Bagawat Necropolis",
        "category": "landmark", "description": "من أقدم المقابر المسيحية في العالم",
        "address": "شمال الخارجة", "lat": 25.4600, "lng": 30.5400,
        "phone": None, "rating_avg": 4.7, "rating_count": 198,
        "images": ["https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=400"],
        "status": "approved",
    },
    {
        "id": 6, "name_ar": "سوق الخارجة", "name_en": "Kharga Market",
        "category": "shopping", "description": "السوق الرئيسي للمنتجات المحلية والتمور",
        "address": "وسط البلد، الخارجة", "lat": 25.4430, "lng": 30.5515,
        "phone": None, "rating_avg": 4.0, "rating_count": 245,
        "images": [], "status": "approved",
    },
]

CARPOOL_RIDES = [
    {
        "id": 1, "driver_id": "a1b2c3d4", "driver_name": "خالد محمود",
        "origin_name": "الخارجة", "destination_name": "أسيوط",
        "origin": {"lat": 25.4410, "lng": 30.5534},
        "destination": {"lat": 27.1809, "lng": 31.1837},
        "departure_time": "2026-03-10T07:00:00", "seats_total": 4, "seats_taken": 1,
        "price_per_seat": 100, "notes": "سيارة مكيفة، رحلة مباشرة",
        "status": "open", "car_model": "تويوتا كورولا 2022", "rating": 4.8,
    },
    {
        "id": 2, "driver_id": "b2c3d4e5", "driver_name": "محمود علي",
        "origin_name": "الداخلة", "destination_name": "أسيوط",
        "origin": {"lat": 25.4888, "lng": 29.0000},
        "destination": {"lat": 27.1809, "lng": 31.1837},
        "departure_time": "2026-03-10T06:00:00", "seats_total": 3, "seats_taken": 0,
        "price_per_seat": 120, "notes": "مساحة للأمتعة",
        "status": "open", "car_model": "هيونداي النترا 2021", "rating": 4.5,
    },
    {
        "id": 3, "driver_id": "c3d4e5f6", "driver_name": "أحمد سمير",
        "origin_name": "الخارجة", "destination_name": "القاهرة",
        "origin": {"lat": 25.4410, "lng": 30.5534},
        "destination": {"lat": 30.0444, "lng": 31.2357},
        "departure_time": "2026-03-11T05:00:00", "seats_total": 3, "seats_taken": 2,
        "price_per_seat": 250, "notes": "رحلة مريحة مع استراحة واحدة",
        "status": "open", "car_model": "كيا سيراتو 2023", "rating": 4.9,
    },
]


class CarpoolCreate(BaseModel):
    origin_name: str
    destination_name: str
    departure_time: str
    seats_total: int
    price_per_seat: float
    notes: Optional[str] = None


@router.get("/pois")
def get_pois(category: str = None):
    if category:
        filtered = [p for p in POIS if p["category"] == category]
        return {"success": True, "data": filtered}
    return {"success": True, "data": POIS}


@router.get("/pois/{poi_id}")
def get_poi(poi_id: int):
    for p in POIS:
        if p["id"] == poi_id:
            return {"success": True, "data": p}
    raise HTTPException(404, "POI not found")


@router.get("/carpool/rides")
def get_rides():
    return {"success": True, "data": CARPOOL_RIDES}


@router.post("/carpool/rides", status_code=201)
def create_ride(body: CarpoolCreate):
    new_ride = {
        "id": len(CARPOOL_RIDES) + 1,
        "driver_id": "current-user", "driver_name": "أنت",
        "origin_name": body.origin_name, "destination_name": body.destination_name,
        "departure_time": body.departure_time,
        "seats_total": body.seats_total, "seats_taken": 0,
        "price_per_seat": body.price_per_seat, "notes": body.notes,
        "status": "open",
    }
    CARPOOL_RIDES.append(new_ride)
    return {"success": True, "data": new_ride}
