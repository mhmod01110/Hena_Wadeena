"""Mock logistics endpoints."""

from fastapi import APIRouter, HTTPException

router = APIRouter()

ROUTES = [
    {
        "id": 1, "from": "الخارجة", "to": "الداخلة", "type": "باص",
        "duration": "3 ساعات", "price": 80,
        "departures": ["6:00 ص", "10:00 ص", "2:00 م", "6:00 م"],
        "operator": "شركة غرب الدلتا",
    },
    {
        "id": 2, "from": "الخارجة", "to": "أسيوط", "type": "باص",
        "duration": "4 ساعات", "price": 120,
        "departures": ["7:00 ص", "3:00 م"],
        "operator": "شركة الوادي للنقل",
    },
    {
        "id": 3, "from": "الداخلة", "to": "الفرافرة", "type": "ميكروباص",
        "duration": "2.5 ساعة", "price": 60,
        "departures": ["8:00 ص", "12:00 م"],
        "operator": "نقل محلي",
    },
    {
        "id": 4, "from": "الخارجة", "to": "الأقصر", "type": "باص",
        "duration": "6 ساعات", "price": 180,
        "departures": ["5:00 ص", "1:00 م"],
        "operator": "شركة الوادي للنقل",
    },
]

STATIONS = [
    {
        "id": 1, "name": "محطة الخارجة المركزية", "city": "الخارجة", "routes": 8,
        "address": "شارع الجمهورية، الخارجة",
        "phone": "092-7921234",
        "facilities": ["قاعة انتظار مكيفة", "كافيتريا", "دورات مياه", "موقف سيارات"],
        "operating_hours": "٥:٠٠ ص - ١٠:٠٠ م",
    },
    {
        "id": 2, "name": "محطة الداخلة", "city": "الداخلة", "routes": 5,
        "address": "موط، الداخلة",
        "phone": "092-7851234",
        "facilities": ["قاعة انتظار", "دورات مياه"],
        "operating_hours": "٦:٠٠ ص - ٨:٠٠ م",
    },
    {
        "id": 3, "name": "محطة الفرافرة", "city": "الفرافرة", "routes": 3,
        "address": "وسط الفرافرة",
        "phone": "092-7731234",
        "facilities": ["استراحة"],
        "operating_hours": "٧:٠٠ ص - ٦:٠٠ م",
    },
]

CARPOOLS = [
    {
        "id": 1, "from": "الخارجة", "to": "أسيوط",
        "date": "26 يناير 2024", "time": "7:00 ص",
        "seats": 2, "price": 100,
        "driver": "خالد محمود", "rating": 4.8,
        "car_model": "تويوتا كورولا 2022",
    },
    {
        "id": 2, "from": "الداخلة", "to": "أسيوط",
        "date": "26 يناير 2024", "time": "6:00 ص",
        "seats": 3, "price": 120,
        "driver": "محمود علي", "rating": 4.5,
        "car_model": "هيونداي النترا 2021",
    },
    {
        "id": 3, "from": "الخارجة", "to": "القاهرة",
        "date": "27 يناير 2024", "time": "5:00 ص",
        "seats": 1, "price": 250,
        "driver": "أحمد سمير", "rating": 4.9,
        "car_model": "كيا سيراتو 2023",
    },
]


@router.get("/routes")
def get_routes():
    return {"success": True, "data": ROUTES}


@router.get("/stations")
def get_stations():
    return {"success": True, "data": STATIONS}


@router.get("/stations/{station_id}")
def get_station(station_id: int):
    for s in STATIONS:
        if s["id"] == station_id:
            return {"success": True, "data": s}
    raise HTTPException(404, "Station not found")


@router.get("/carpools")
def get_carpools():
    return {"success": True, "data": CARPOOLS}
