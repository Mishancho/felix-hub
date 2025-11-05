#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для массового добавления запчастей в базу данных Felix Hub
"""

from app import app, db
from models import Part, Category

# Список запчастей для добавления
PARTS_DATA = [
    # Лампочки
    {"name_ru": "Лампа, один контакт", "name_en": "Single-contact bulb", "name_he": "נורה מגע אחד", "category": "Лампочки"},
    {"name_ru": "Лампа, два контакта", "name_en": "Dual-contact bulb", "name_he": "נורה שני מגעים", "category": "Лампочки"},
    {"name_ru": "Лампа без корпуса (без патрона)", "name_en": "Bulb without holder/housing", "name_he": "נורה בלי בית", "category": "Лампочки"},
    {"name_ru": "Лампа H7", "name_en": "H7 bulb", "name_he": "נורה H7", "category": "Лампочки"},
    {"name_ru": "Лампа H4", "name_en": "H4 bulb", "name_he": "נורה H4", "category": "Лампочки"},
    {"name_ru": "Лампа H1", "name_en": "H1 bulb", "name_he": "נורה H1", "category": "Лампочки"},
    {"name_ru": "Лампа «банан» (фестон)", "name_en": "Festoon bulb", "name_he": "נורת בננה", "category": "Лампочки"},
    {"name_ru": "Лампа средняя (типоразмер средний)", "name_en": "Medium-size bulb", "name_he": "נורה בינונית", "category": "Лампочки"},
    {"name_ru": "Лампа с корпусом (с патроном)", "name_en": "Bulb with holder/housing", "name_he": "נורה עם בית", "category": "Лампочки"},
    
    # типуль
    {"name_ru": "Тормозная жидкость", "name_en": "Brake fluid", "name_he": "נוזל בלמים", "category": "типуль"},
    {"name_ru": "Спрей для тормозов (очиститель)", "name_en": "Brake cleaner spray", "name_he": "ספריי ברקסים", "category": "типуль"},
    {"name_ru": "Пробка поддона двигателя (сливной болт)", "name_en": "Engine oil drain plug", "name_he": "בורג לאגן שמן מנוע", "category": "типуль"},
    {"name_ru": "Присадка для омывателя стёкол", "name_en": "Windshield washer additive", "name_he": "תוסף לניקוי שמשות", "category": "типуль"},
    {"name_ru": "Масло (двигателя)", "name_en": "Engine oil", "name_he": "שמן", "category": "типуль"},
    {"name_ru": "Фильтр масляный", "name_en": "Oil filter", "name_he": "מסנן שמן", "category": "типуль"},
    {"name_ru": "Фильтр воздушный", "name_en": "Air filter", "name_he": "מסנן אויר", "category": "типуль"},
    {"name_ru": "Фильтр кондиционера (салонный)", "name_en": "A/C (cabin) filter", "name_he": "מסנן מזגן", "category": "типуль"},
    {"name_ru": "Фильтр топливный (бензин)", "name_en": "Fuel filter (petrol)", "name_he": "מסנן דלק", "category": "типуль"},
    {"name_ru": "Фильтр дизельный (солярки)", "name_en": "Diesel fuel filter", "name_he": "מסנן סולר", "category": "типуль"},
    {"name_ru": "Свечи зажигания", "name_en": "Spark plugs", "name_he": "מצתים", "category": "типуль"},
    {"name_ru": "Ремень ГРМ", "name_en": "Timing belt", "name_he": "רצועת תזמון", "category": "типуль"},
    {"name_ru": "Натяжитель ремня ГРМ", "name_en": "Timing belt tensioner", "name_he": "מותחן לרצועת תזמון", "category": "типуль"},
    {"name_ru": "Ремень генератора", "name_en": "Alternator belt", "name_he": "רצועת אלטרנטור", "category": "типуль"},
    
    # жидкости\масла
    {"name_ru": "Масло для заднего моста", "name_en": "Rear axle oil", "name_he": "שמן לסרן אחורי", "category": "жидкости\\масла"},
    {"name_ru": "Масло для МКПП", "name_en": "Manual gearbox oil", "name_he": "שמן לגיר ידני", "category": "жидкости\\масла"},
    {"name_ru": "Масло для АКПП", "name_en": "Automatic transmission oil", "name_he": "שמן לגיר אוטומט", "category": "жидкости\\масла"},
    {"name_ru": "Жидкость ГУР (рулевого управления)", "name_en": "Power steering fluid", "name_he": "שמן הגה", "category": "жидкости\\масла"},
    {"name_ru": "Очиститель нагара/декарбонизатор", "name_en": "Carbon deposit remover", "name_he": "מסיר פיח", "category": "жидкости\\масла"},
    {"name_ru": "Вода дистиллированная", "name_en": "Distilled water", "name_he": "מים מזוקקים", "category": "жидкости\\масла"},
    {"name_ru": "G13", "name_en": "G13", "name_he": "G13", "category": "жидкости\\масла"},
    
    # тормоза
    {"name_ru": "Передние тормозные колодки", "name_en": "Front brake pads", "name_he": "דיסק ברקס קדמי", "category": "тормоза"},
    {"name_ru": "Задние тормозные колодки", "name_en": "Rear brake pads", "name_he": "דיסק ברקס אחורי", "category": "тормоза"},
    {"name_ru": "Тормозной диск (ротора) передний", "name_en": "Front rotor (disc)", "name_he": "צלחות קדמי", "category": "тормоза"},
    {"name_ru": "Тормозной диск (ротора) задний", "name_en": "Rear rotor (disc)", "name_he": "צלחות אחורי", "category": "тормоза"},
    {"name_ru": "Датчик/провод износа колодок передний", "name_en": "Front brake wear sensor wire", "name_he": "חוטים לברקס קדמי", "category": "тормоза"},
    {"name_ru": "Датчик/провод износа колодок задний", "name_en": "Rear brake wear sensor wire", "name_he": "חוטים לברקס אחורי", "category": "тормоза"},
    
    # типуль\кузов
    {"name_ru": "Щётки стеклоочистителя перед", "name_en": "Wiper blades front", "name_he": "מגבים קדמי", "category": "типуль\\кузов"},
    {"name_ru": "Щётки стеклоочистителя зад", "name_en": "Wiper blades back", "name_he": "מגבים אחורי", "category": "типуль\\кузов"},
]

def ensure_categories_exist():
    """Убедиться, что все необходимые категории существуют"""
    categories_needed = set()
    for part in PARTS_DATA:
        categories_needed.add(part["category"])
    
    print(f"\n📂 Проверка категорий...")
    print(f"   Необходимо категорий: {len(categories_needed)}")
    
    for cat_name in categories_needed:
        category = Category.query.filter_by(name=cat_name).first()
        if not category:
            print(f"   ⚠️  Категория '{cat_name}' не найдена, создаём...")
            category = Category(
                name=cat_name,
                name_ru=cat_name,
                is_active=True
            )
            db.session.add(category)
        else:
            print(f"   ✅ Категория '{cat_name}' существует")
    
    db.session.commit()
    print("   ✅ Все категории готовы")

def add_parts():
    """Добавить все запчасти из списка"""
    with app.app_context():
        print("=" * 70)
        print("🚀 Массовое добавление запчастей в Felix Hub")
        print("=" * 70)
        
        # Проверяем категории
        ensure_categories_exist()
        
        print(f"\n📦 Начинаем добавление {len(PARTS_DATA)} запчастей...")
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, part_data in enumerate(PARTS_DATA, 1):
            try:
                # Проверяем, существует ли уже такая запчасть
                existing_part = Part.query.filter_by(
                    name_ru=part_data["name_ru"],
                    category=part_data["category"]
                ).first()
                
                if existing_part:
                    print(f"   [{i}/{len(PARTS_DATA)}] ⏭️  '{part_data['name_ru']}' - уже существует")
                    skipped_count += 1
                    continue
                
                # Создаём новую запчасть
                new_part = Part(
                    name_ru=part_data["name_ru"],
                    name_en=part_data["name_en"],
                    name_he=part_data["name_he"],
                    name=part_data["name_ru"],  # для обратной совместимости
                    category=part_data["category"],
                    is_active=True,
                    sort_order=0
                )
                
                db.session.add(new_part)
                db.session.commit()
                
                print(f"   [{i}/{len(PARTS_DATA)}] ✅ '{part_data['name_ru']}' - добавлена (ID: {new_part.id})")
                added_count += 1
                
            except Exception as e:
                print(f"   [{i}/{len(PARTS_DATA)}] ❌ '{part_data['name_ru']}' - ошибка: {e}")
                error_count += 1
                db.session.rollback()
        
        print("\n" + "=" * 70)
        print("📊 ИТОГИ:")
        print(f"   ✅ Добавлено:   {added_count}")
        print(f"   ⏭️  Пропущено:  {skipped_count}")
        print(f"   ❌ Ошибки:      {error_count}")
        print(f"   📦 Всего:       {len(PARTS_DATA)}")
        print("=" * 70)
        
        if added_count > 0:
            print("\n🎉 Запчасти успешно добавлены в базу данных!")
        elif skipped_count == len(PARTS_DATA):
            print("\n✅ Все запчасти уже присутствуют в базе данных")
        
        # Выводим статистику по категориям
        print("\n📈 Статистика по категориям:")
        categories = db.session.query(Part.category, db.func.count(Part.id)).group_by(Part.category).all()
        for cat_name, count in sorted(categories, key=lambda x: x[1], reverse=True):
            print(f"   • {cat_name}: {count} запчастей")

if __name__ == "__main__":
    add_parts()
