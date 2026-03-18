"""Mock search endpoint — unified search across all content."""

from fastapi import APIRouter

router = APIRouter()

SEARCH_INDEX = [
    {"id": "poi-1", "type": "poi", "title": "معبد هيبس", "description": "أقدم معبد في الواحات", "location": "الخارجة", "url": "/tourism/attraction/1"},
    {"id": "poi-2", "type": "poi", "title": "مقابر البجوات", "description": "من أقدم المقابر المسيحية في العالم", "location": "الخارجة", "url": "/tourism/attraction/4"},
    {"id": "att-1", "type": "attraction", "title": "واحة الخارجة", "description": "أكبر واحات الوادي الجديد", "location": "الخارجة", "url": "/tourism/attraction/1"},
    {"id": "att-2", "type": "attraction", "title": "الصحراء البيضاء", "description": "تشكيلات صخرية بيضاء ساحرة", "location": "الفرافرة", "url": "/tourism/attraction/2"},
    {"id": "guide-1", "type": "guide", "title": "أحمد السيد", "description": "مرشد سياحي — سفاري صحراوي", "location": "الخارجة", "url": "/guides/1"},
    {"id": "guide-2", "type": "guide", "title": "فاطمة حسن", "description": "مرشدة — سياحة علاجية", "location": "الخارجة", "url": "/guides/2"},
    {"id": "sup-1", "type": "supplier", "title": "مزارع الوادي الأخضر", "description": "تمور وزيتون وعنب", "location": "الخارجة", "url": "/marketplace/supplier/1"},
    {"id": "inv-1", "type": "investment", "title": "مشروع زراعي متكامل", "description": "100 فدان تمور وزيتون", "location": "الداخلة", "url": "/investment/opportunity/1"},
    {"id": "inv-2", "type": "investment", "title": "مجمع سياحي صحراوي", "description": "30 شاليه ومخيم نجوم", "location": "الفرافرة", "url": "/investment/opportunity/2"},
    {"id": "route-1", "type": "transport", "title": "الخارجة → الداخلة", "description": "باص — 3 ساعات — 80 جنيه", "location": "الخارجة", "url": "/logistics"},
]


@router.get("")
def search(q: str = "", type: str = None):
    results = SEARCH_INDEX
    if q:
        results = [r for r in results if q in r["title"] or q in r["description"]]
    if type:
        results = [r for r in results if r["type"] == type]
    return {"success": True, "data": results, "total": len(results), "query": q}
