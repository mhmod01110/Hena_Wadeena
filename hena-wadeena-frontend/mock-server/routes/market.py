"""Mock market/marketplace endpoints."""

from fastapi import APIRouter, HTTPException

router = APIRouter()

PRICE_DATA = [
    {"id": 1, "name": "قمح", "price": 1250, "change": 2.5, "unit": "طن", "category": "حبوب"},
    {"id": 2, "name": "تمر سيوي", "price": 45, "change": -1.2, "unit": "كجم", "category": "فواكه"},
    {"id": 3, "name": "زيتون", "price": 28, "change": 0, "unit": "كجم", "category": "فواكه"},
    {"id": 4, "name": "برسيم", "price": 800, "change": 3.1, "unit": "طن", "category": "أعلاف"},
    {"id": 5, "name": "أرز", "price": 22, "change": -0.5, "unit": "كجم", "category": "حبوب"},
    {"id": 6, "name": "فول سوداني", "price": 55, "change": 1.8, "unit": "كجم", "category": "حبوب"},
    {"id": 7, "name": "بطاطس", "price": 8, "change": 0.5, "unit": "كجم", "category": "خضروات"},
    {"id": 8, "name": "بصل", "price": 6, "change": -1.0, "unit": "كجم", "category": "خضروات"},
    {"id": 9, "name": "طماطم", "price": 12, "change": 2.0, "unit": "كجم", "category": "خضروات"},
    {"id": 10, "name": "عنب", "price": 35, "change": -0.3, "unit": "كجم", "category": "فواكه"},
]

SUPPLIERS = [
    {
        "id": 1,
        "name": "مزارع الوادي الأخضر",
        "specialties": ["تمور", "زيتون", "عنب"],
        "city": "الخارجة",
        "rating": 4.8,
        "reviews": 124,
        "verified": True,
        "description": "مزرعة متكاملة متخصصة في زراعة وتصدير التمور والزيتون بأعلى معايير الجودة. نعمل منذ أكثر من 20 عاماً في الوادي الجديد.",
        "phone": "01012345678",
        "email": "info@green-valley.com",
        "image": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=400",
        "products": [
            {"name": "تمر سيوي فاخر", "price": 55, "unit": "كجم"},
            {"name": "زيتون أخضر", "price": 30, "unit": "كجم"},
            {"name": "زيت زيتون بكر", "price": 120, "unit": "لتر"},
        ],
    },
    {
        "id": 2,
        "name": "شركة النخيل الذهبي",
        "specialties": ["تمور", "نخيل"],
        "city": "الداخلة",
        "rating": 4.6,
        "reviews": 89,
        "verified": True,
        "description": "أكبر منتج تمور في واحة الداخلة. نقدم أجود أنواع التمور المصرية للسوق المحلي والتصدير.",
        "phone": "01098765432",
        "email": "sales@golden-palm.com",
        "image": "https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?w=400",
        "products": [
            {"name": "تمر مجدول", "price": 80, "unit": "كجم"},
            {"name": "تمر عجوة", "price": 65, "unit": "كجم"},
        ],
    },
    {
        "id": 3,
        "name": "مزارع الفرافرة العضوية",
        "specialties": ["خضروات عضوية", "أعشاب"],
        "city": "الفرافرة",
        "rating": 4.9,
        "reviews": 56,
        "verified": True,
        "description": "مزرعة عضوية معتمدة في واحة الفرافرة، متخصصة في الزراعة العضوية والمنتجات الطبيعية.",
        "phone": "01155667788",
        "email": "organic@farafra-farms.com",
        "image": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400",
        "products": [
            {"name": "طماطم عضوية", "price": 18, "unit": "كجم"},
            {"name": "خيار عضوي", "price": 15, "unit": "كجم"},
        ],
    },
    {
        "id": 4,
        "name": "جمعية المزارعين التعاونية",
        "specialties": ["خضروات", "فواكه"],
        "city": "باريس",
        "rating": 4.4,
        "reviews": 67,
        "verified": False,
        "description": "جمعية تعاونية تجمع منتجات صغار المزارعين في منطقة باريس وتسوقها بأسعار عادلة.",
        "phone": "01234567890",
        "email": "coop@paris-farmers.com",
        "image": "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=400",
        "products": [
            {"name": "بطاطس", "price": 8, "unit": "كجم"},
            {"name": "بصل", "price": 6, "unit": "كجم"},
        ],
    },
]


@router.get("/prices")
def get_prices():
    return {"success": True, "data": PRICE_DATA}


@router.get("/suppliers")
def get_suppliers():
    return {"success": True, "data": SUPPLIERS}


@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: int):
    for s in SUPPLIERS:
        if s["id"] == supplier_id:
            return {"success": True, "data": s}
    raise HTTPException(404, "Supplier not found")
