"""Mock tourism endpoints with rich Arabic dummy data."""

from fastapi import APIRouter, HTTPException

router = APIRouter()

ATTRACTIONS = [
    {
        "id": 1,
        "title": "واحة الخارجة",
        "description": "أكبر واحات الوادي الجديد، تضم آثاراً فرعونية ورومانية فريدة من معبد هيبس ومقابر البجوات",
        "long_description": "تعد واحة الخارجة أكبر واحات الوادي الجديد وعاصمة المحافظة، وتضم مجموعة فريدة من المعالم الأثرية التي تعود للعصور الفرعونية والرومانية. يتصدرها معبد هيبس الذي يعد الوحيد الباقي من العصر الصاوي، ومقابر البجوات التي تعتبر من أقدم المقابر المسيحية في العالم. كما تتميز بينابيعها الحارة وبساتين النخيل الممتدة.",
        "image": "https://images.unsplash.com/photo-1539768942893-daf53e448371?w=800",
        "images": [
            "https://images.unsplash.com/photo-1539768942893-daf53e448371?w=800",
            "https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=800",
            "https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=800",
        ],
        "rating": 4.8,
        "reviews_count": 234,
        "duration": "يوم كامل",
        "type": "أثري",
        "location": "الخارجة، الوادي الجديد",
        "coordinates": {"lat": 25.4410, "lng": 30.5534},
        "featured": True,
        "opening_hours": "٨:٠٠ ص - ٥:٠٠ م",
        "ticket_price": 80,
        "highlights": ["معبد هيبس", "مقابر البجوات", "متحف الآثار", "العين الحارة"],
    },
    {
        "id": 2,
        "title": "الصحراء البيضاء",
        "description": "تشكيلات صخرية بيضاء ساحرة تحت سماء مليئة بالنجوم",
        "long_description": "تقع الصحراء البيضاء شمال واحة الفرافرة وتعتبر من أجمل المناطق الطبيعية في مصر والعالم. تتميز بتشكيلات صخرية بيضاء ناصعة نحتتها الرياح عبر ملايين السنين لتخلق أشكالاً فريدة تشبه الفطر والأعمدة. تعد من أفضل أماكن التخييم في العالم حيث يمكنك الاستمتاع بسماء صافية مليئة بالنجوم.",
        "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800",
        "images": [
            "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800",
            "https://images.unsplash.com/photo-1542401886-65d6c61db217?w=800",
        ],
        "rating": 4.9,
        "reviews_count": 567,
        "duration": "٢-٣ أيام",
        "type": "طبيعي",
        "location": "الفرافرة، الوادي الجديد",
        "coordinates": {"lat": 27.2956, "lng": 28.0567},
        "featured": True,
        "opening_hours": "مفتوح ٢٤ ساعة",
        "ticket_price": 50,
        "highlights": ["تخييم تحت النجوم", "تشكيلات الفطر الصخرية", "سفاري صحراوي", "غروب الشمس"],
    },
    {
        "id": 3,
        "title": "عين السبيل",
        "description": "عين مياه ساخنة طبيعية للاسترخاء والعلاج",
        "long_description": "عين السبيل هي واحدة من أشهر العيون الحارة في الوادي الجديد، تتميز بمياهها المعدنية الساخنة التي تصل حرارتها إلى 43 درجة مئوية. يقصدها الزوار للاستشفاء من أمراض الروماتيزم والجلد والعظام.",
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800",
        "images": [
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800",
        ],
        "rating": 4.6,
        "reviews_count": 189,
        "duration": "نصف يوم",
        "type": "استشفائي",
        "location": "الخارجة، الوادي الجديد",
        "coordinates": {"lat": 25.4500, "lng": 30.5600},
        "featured": True,
        "opening_hours": "٧:٠٠ ص - ٩:٠٠ م",
        "ticket_price": 30,
        "highlights": ["مياه معدنية ساخنة", "علاج طبيعي", "حمامات خاصة"],
    },
    {
        "id": 4,
        "title": "واحة الداخلة",
        "description": "واحة خضراء تضم قرى طينية أثرية ومناظر طبيعية خلابة",
        "long_description": "تعد واحة الداخلة من أجمل واحات الوادي الجديد، تتميز بقراها الطينية التقليدية مثل قرية القصر والقرية القديمة بموط. تضم آثاراً من مختلف العصور ومناظر طبيعية بديعة من بساتين النخيل والكثبان الرملية.",
        "image": "https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=800",
        "images": [],
        "rating": 4.5,
        "reviews_count": 156,
        "duration": "٣ ساعات",
        "type": "أثري",
        "location": "الداخلة، الوادي الجديد",
        "coordinates": {"lat": 25.4888, "lng": 29.0000},
        "featured": False,
        "opening_hours": "٨:٠٠ ص - ٥:٠٠ م",
        "ticket_price": 60,
        "highlights": ["قرية القصر", "مقابر المزوقة", "حصن الدير"],
    },
]

GUIDES = [
    {
        "id": 1,
        "name": "أحمد السيد",
        "languages": ["العربية", "الإنجليزية"],
        "specialties": ["سفاري صحراوي", "مواقع أثرية"],
        "rating": 4.9,
        "reviews": 87,
        "price_per_day": 800,
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
        "bio": "مرشد سياحي معتمد بخبرة أكثر من 10 سنوات في رحلات السفاري الصحراوي والمواقع الأثرية بالوادي الجديد.",
        "available": True,
    },
    {
        "id": 2,
        "name": "فاطمة حسن",
        "languages": ["العربية", "الإنجليزية", "الفرنسية"],
        "specialties": ["سياحة علاجية", "واحات"],
        "rating": 4.7,
        "reviews": 45,
        "price_per_day": 650,
        "image": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200",
        "bio": "متخصصة في السياحة العلاجية والاستشفائية في واحات الوادي الجديد.",
        "available": True,
    },
    {
        "id": 3,
        "name": "محمد عبدالله",
        "languages": ["العربية", "الإنجليزية"],
        "specialties": ["تخييم", "تصوير فوتوغرافي"],
        "rating": 4.8,
        "reviews": 62,
        "price_per_day": 750,
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200",
        "bio": "مرشد متخصص في رحلات التخييم وتصوير المناظر الطبيعية في الصحراء البيضاء.",
        "available": False,
    },
]

ACCOMMODATIONS = [
    {
        "id": 1,
        "title": "شقة مفروشة - الخارجة",
        "type": "شقة",
        "price": 1500,
        "price_unit": "شهرياً",
        "rooms": 2,
        "location": "حي الزهور، الخارجة",
        "amenities": ["مكيف", "واي فاي", "مطبخ مجهز", "غسالة"],
        "for_students": True,
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400",
        "rating": 4.3,
    },
    {
        "id": 2,
        "title": "غرفة مشتركة - وسط البلد",
        "type": "غرفة مشتركة",
        "price": 500,
        "price_unit": "شهرياً",
        "rooms": 1,
        "location": "وسط البلد، الخارجة",
        "amenities": ["مكيف مشترك", "مطبخ مشترك"],
        "for_students": True,
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400",
        "rating": 3.9,
    },
    {
        "id": 3,
        "title": "فندق واحة الخارجة",
        "type": "فندق",
        "price": 350,
        "price_unit": "لليلة",
        "rooms": 1,
        "location": "شارع الجمهورية، الخارجة",
        "amenities": ["مكيف", "واي فاي", "إفطار", "حمام سباحة"],
        "for_students": False,
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
        "rating": 4.5,
    },
]


@router.get("/attractions")
def get_attractions():
    return {"success": True, "data": ATTRACTIONS}


@router.get("/attractions/featured")
def get_featured():
    return {"success": True, "data": [a for a in ATTRACTIONS if a["featured"]]}


@router.get("/attractions/{attraction_id}")
def get_attraction(attraction_id: int):
    for a in ATTRACTIONS:
        if a["id"] == attraction_id:
            return {"success": True, "data": a}
    raise HTTPException(404, "Attraction not found")


@router.get("/guides")
def get_guides():
    return {"success": True, "data": GUIDES}


@router.get("/accommodations")
def get_accommodations():
    return {"success": True, "data": ACCOMMODATIONS}
