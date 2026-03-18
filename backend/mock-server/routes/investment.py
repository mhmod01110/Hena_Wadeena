"""Mock investment endpoints."""

from fastapi import APIRouter, HTTPException

router = APIRouter()

OPPORTUNITIES = [
    {
        "id": 1,
        "title": "مشروع زراعي متكامل - 100 فدان",
        "category": "زراعة",
        "location": "الداخلة",
        "investment": "5-10 مليون جنيه",
        "min_investment": 5000000,
        "max_investment": 10000000,
        "roi": "18-22%",
        "status": "متاح",
        "description": "مشروع زراعي متكامل على مساحة 100 فدان لزراعة التمور والزيتون مع نظام ري حديث بالتنقيط ومحطة تعبئة وتغليف.",
        "details": "يشمل المشروع إنشاء بئر مياه جوفية، شبكة ري بالتنقيط، زراعة 5000 نخلة و2000 شجرة زيتون، مخزن مبرد، ومحطة تعبئة. العائد المتوقع يبدأ من السنة الثالثة.",
        "image": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800",
    },
    {
        "id": 2,
        "title": "مجمع سياحي - الصحراء البيضاء",
        "category": "سياحة",
        "location": "الفرافرة",
        "investment": "15-25 مليون جنيه",
        "min_investment": 15000000,
        "max_investment": 25000000,
        "roi": "20-25%",
        "status": "متاح",
        "description": "مجمع سياحي بيئي يضم 30 شاليه صحراوي ومخيم نجوم ومطعم ومركز سفاري.",
        "details": "المشروع مصمم ليكون صديقاً للبيئة بالكامل مع استخدام الطاقة الشمسية ومواد بناء محلية. يستهدف السياحة الدولية والمحلية.",
        "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800",
    },
    {
        "id": 3,
        "title": "مصنع تعبئة تمور للتصدير",
        "category": "صناعة",
        "location": "الخارجة",
        "investment": "3-5 مليون جنيه",
        "min_investment": 3000000,
        "max_investment": 5000000,
        "roi": "25-30%",
        "status": "متاح",
        "description": "مصنع لتعبئة وتغليف التمور للتصدير مع خطوط إنتاج حديثة ومخازن مبردة.",
        "details": "مصنع بطاقة إنتاجية 5000 طن سنوياً مع شهادات جودة دولية للتصدير لأسواق الخليج وأوروبا.",
        "image": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800",
    },
    {
        "id": 4,
        "title": "محطة طاقة شمسية",
        "category": "طاقة",
        "location": "باريس",
        "investment": "50-100 مليون جنيه",
        "min_investment": 50000000,
        "max_investment": 100000000,
        "roi": "12-15%",
        "status": "قيد الدراسة",
        "description": "مشروع محطة طاقة شمسية بقدرة 50 ميجاوات للاستفادة من الإشعاع الشمسي العالي.",
        "details": "المنطقة تتمتع بأعلى معدلات إشعاع شمسي في مصر. المشروع بالتعاون مع هيئة الطاقة الجديدة والمتجددة.",
        "image": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?w=800",
    },
]

STARTUPS = [
    {
        "id": 1,
        "name": "واحة تك",
        "sector": "تكنولوجيا زراعية",
        "stage": "مرحلة النمو",
        "location": "الخارجة",
        "team": 8,
        "description": "منصة تكنولوجية لإدارة المزارع واستخدام الذكاء الاصطناعي في التنبؤ بالمحاصيل.",
        "funding_needed": "2 مليون جنيه",
        "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400",
    },
    {
        "id": 2,
        "name": "تمور أونلاين",
        "sector": "تجارة إلكترونية",
        "stage": "مرحلة النمو",
        "location": "الخارجة",
        "team": 12,
        "description": "منصة لبيع التمور والمنتجات المحلية عبر الإنترنت للسوق المحلي والدولي.",
        "funding_needed": "3 مليون جنيه",
        "image": "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=400",
    },
    {
        "id": 3,
        "name": "سولار وادي",
        "sector": "طاقة متجددة",
        "stage": "مرحلة التأسيس",
        "location": "باريس",
        "team": 5,
        "description": "شركة ناشئة متخصصة في تركيب وصيانة أنظمة الطاقة الشمسية الصغيرة للمنازل والمزارع.",
        "funding_needed": "1 مليون جنيه",
        "image": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?w=400",
    },
]


@router.get("/opportunities")
def get_opportunities():
    return {"success": True, "data": OPPORTUNITIES}


@router.get("/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: int):
    for o in OPPORTUNITIES:
        if o["id"] == opportunity_id:
            return {"success": True, "data": o}
    raise HTTPException(404, "Opportunity not found")


@router.get("/startups")
def get_startups():
    return {"success": True, "data": STARTUPS}
