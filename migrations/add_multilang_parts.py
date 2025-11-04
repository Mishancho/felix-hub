"""
Миграция: Добавление переводов для категорий и запчастей
Версия: 2.2.3
Дата: 04.11.2024
"""

import os
import sys

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Category, Part
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Переводы категорий
CATEGORY_TRANSLATIONS = {
    'Тормоза': {
        'en': 'Brakes',
        'he': 'בלמים'
    },
    'Двигатель': {
        'en': 'Engine',
        'he': 'מנוע'
    },
    'Подвеска': {
        'en': 'Suspension',
        'he': 'מתלים'
    },
    'Электрика': {
        'en': 'Electrical',
        'he': 'חשמל'
    },
    'Расходники': {
        'en': 'Consumables',
        'he': 'מתכלים'
    },
    'Добавки': {
        'en': 'Additives',
        'he': 'תוספים'
    },
    'Типуль': {
        'en': 'Maintenance',
        'he': 'טיפול'
    }
}

# Переводы запчастей
PARTS_TRANSLATIONS = {
    # Тормоза / Brakes / בלמים
    'Передние колодки': {
        'en': 'Front Brake Pads',
        'he': 'רפידות בלם קדמיות',
        'category': 'Тормоза'
    },
    'Задние колодки': {
        'en': 'Rear Brake Pads',
        'he': 'רפידות בלם אחוריות',
        'category': 'Тормоза'
    },
    'Диски передние': {
        'en': 'Front Brake Discs',
        'he': 'דיסקי בלם קדמיים',
        'category': 'Тормоза'
    },
    'Диски задние': {
        'en': 'Rear Brake Discs',
        'he': 'דיסקי בלם אחוריים',
        'category': 'Тормоза'
    },
    'Тормозная жидкость': {
        'en': 'Brake Fluid',
        'he': 'נוזל בלמים',
        'category': 'Тормоза'
    },
    
    # Двигатель / Engine / מנוע
    'Масло моторное': {
        'en': 'Engine Oil',
        'he': 'שמן מנוע',
        'category': 'Двигатель'
    },
    'Масляный фильтр': {
        'en': 'Oil Filter',
        'he': 'פילטר שמן',
        'category': 'Двигатель'
    },
    'Воздушный фильтр': {
        'en': 'Air Filter',
        'he': 'פילטר אוויר',
        'category': 'Двигатель'
    },
    'Свечи зажигания': {
        'en': 'Spark Plugs',
        'he': 'מצתים',
        'category': 'Двигатель'
    },
    'Ремень ГРМ': {
        'en': 'Timing Belt',
        'he': 'רצועת טיימינג',
        'category': 'Двигатель'
    },
    'Прокладка ГБЦ': {
        'en': 'Cylinder Head Gasket',
        'he': 'אטם ראש צילינדר',
        'category': 'Двигатель'
    },
    'Помпа водяная': {
        'en': 'Water Pump',
        'he': 'משאבת מים',
        'category': 'Двигатель'
    },
    'Термостат': {
        'en': 'Thermostat',
        'he': 'תרמוסטט',
        'category': 'Двигатель'
    },
    'Топливный фильтр': {
        'en': 'Fuel Filter',
        'he': 'פילטר דלק',
        'category': 'Двигатель'
    },
    'Радиатор': {
        'en': 'Radiator',
        'he': 'רדיאטור',
        'category': 'Двигатель'
    },
    
    # Подвеска / Suspension / מתלים
    'Амортизаторы передние': {
        'en': 'Front Shock Absorbers',
        'he': 'בולמי זעזועים קדמיים',
        'category': 'Подвеска'
    },
    'Амортизаторы задние': {
        'en': 'Rear Shock Absorbers',
        'he': 'בולמי זעזועים אחוריים',
        'category': 'Подвеска'
    },
    'Пружины': {
        'en': 'Springs',
        'he': 'קפיצים',
        'category': 'Подвеска'
    },
    'Стойки стабилизатора': {
        'en': 'Stabilizer Links',
        'he': 'מוטות מייצב',
        'category': 'Подвеска'
    },
    'Рычаги': {
        'en': 'Control Arms',
        'he': 'זרועות מתלים',
        'category': 'Подвеска'
    },
    'Сайлентблоки': {
        'en': 'Bushings',
        'he': 'סיילנטבלוקים',
        'category': 'Подвеска'
    },
    'Шаровые опоры': {
        'en': 'Ball Joints',
        'he': 'כדוריות',
        'category': 'Подвеска'
    },
    'Рулевые наконечники': {
        'en': 'Tie Rod Ends',
        'he': 'ראשי מוט הגה',
        'category': 'Подвеска'
    },
    'Рулевые тяги': {
        'en': 'Tie Rods',
        'he': 'מוטות הגה',
        'category': 'Подвеска'
    },
    'Опорные подшипники': {
        'en': 'Strut Mount Bearings',
        'he': 'מסבי תמיכה',
        'category': 'Подвеска'
    },
    
    # Электрика / Electrical / חשמל
    'Аккумулятор': {
        'en': 'Battery',
        'he': 'מצבר',
        'category': 'Электрика'
    },
    'Генератор': {
        'en': 'Alternator',
        'he': 'אלטרנטור',
        'category': 'Электрика'
    },
    'Стартер': {
        'en': 'Starter',
        'he': 'סטרטר',
        'category': 'Электрика'
    },
    'Лампы': {
        'en': 'Bulbs',
        'he': 'נורות',
        'category': 'Электрика'
    },
    'Датчики': {
        'en': 'Sensors',
        'he': 'חיישנים',
        'category': 'Электрика'
    },
    'Предохранители': {
        'en': 'Fuses',
        'he': 'נתיכים',
        'category': 'Электрика'
    },
    'Реле': {
        'en': 'Relays',
        'he': 'ממסרים',
        'category': 'Электрика'
    },
    'Катушки зажигания': {
        'en': 'Ignition Coils',
        'he': 'סלילי הצתה',
        'category': 'Электрика'
    },
    'Датчик кислорода': {
        'en': 'Oxygen Sensor',
        'he': 'חיישן חמצן',
        'category': 'Электрика'
    },
    'Датчик АБС': {
        'en': 'ABS Sensor',
        'he': 'חיישן ABS',
        'category': 'Электрика'
    },
    
    # Расходники / Consumables / מתכלים
    'Антифриз': {
        'en': 'Antifreeze',
        'he': 'נוזל קירור',
        'category': 'Расходники'
    },
    'Омывайка': {
        'en': 'Windshield Washer Fluid',
        'he': 'נוזל שמשות',
        'category': 'Расходники'
    },
    'Салонный фильтр': {
        'en': 'Cabin Air Filter',
        'he': 'פילטר אוויר תא נוסעים',
        'category': 'Расходники'
    },
    'Щётки стеклоочистителя': {
        'en': 'Wiper Blades',
        'he': 'להבי מגב',
        'category': 'Расходники'
    },
    'Технические жидкости': {
        'en': 'Technical Fluids',
        'he': 'נוזלים טכניים',
        'category': 'Расходники'
    },
    'Тормозная жидкость DOT 4': {
        'en': 'Brake Fluid DOT 4',
        'he': 'נוזל בלמים DOT 4',
        'category': 'Расходники'
    },
    'Масло трансмиссионное': {
        'en': 'Transmission Oil',
        'he': 'שמן תיבת הילוכים',
        'category': 'Расходники'
    },
    'Жидкость ГУР': {
        'en': 'Power Steering Fluid',
        'he': 'נוזל הגה כוח',
        'category': 'Расходники'
    },
    'Очиститель карбюратора': {
        'en': 'Carburetor Cleaner',
        'he': 'מנקה קרבורטור',
        'category': 'Расходники'
    },
    'WD-40': {
        'en': 'WD-40',
        'he': 'WD-40',
        'category': 'Расходники'
    }
}


def add_category_translations():
    """Добавляет переводы для категорий (если нужна такая функция в будущем)"""
    print("\n📁 Обновление переводов категорий...")
    updated = 0
    
    for ru_name, translations in CATEGORY_TRANSLATIONS.items():
        # Примечание: В текущей модели Category нет полей для переводов
        # Категория хранится как строка в запчасти
        # Это просто справочная информация для будущего расширения
        print(f"  {ru_name}: {translations['en']} / {translations['he']}")
        updated += 1
    
    print(f"✅ Обработано {updated} категорий")
    return updated


def add_parts_translations():
    """Добавляет переводы для существующих запчастей"""
    print("\n🔧 Обновление переводов запчастей...")
    updated = 0
    not_found = []
    
    for ru_name, data in PARTS_TRANSLATIONS.items():
        # Ищем запчасть по русскому названию
        part = Part.query.filter_by(name_ru=ru_name).first()
        
        if not part:
            # Попробуем найти по старому полю name
            part = Part.query.filter_by(name=ru_name).first()
        
        if part:
            # Обновляем переводы
            part.name_en = data['en']
            part.name_he = data['he']
            
            # Обновляем name_ru, если его не было
            if not part.name_ru:
                part.name_ru = ru_name
            
            updated += 1
            print(f"  ✓ {ru_name}")
            print(f"    EN: {data['en']}")
            print(f"    HE: {data['he']}")
        else:
            not_found.append(ru_name)
            print(f"  ⚠️  Не найдено: {ru_name}")
    
    db.session.commit()
    
    print(f"\n✅ Обновлено: {updated} запчастей")
    if not_found:
        print(f"⚠️  Не найдено: {len(not_found)} запчастей")
        print("   Список не найденных:")
        for name in not_found:
            print(f"   - {name}")
    
    return updated, not_found


def create_missing_parts():
    """Создает запчасти, которых нет в базе"""
    print("\n📦 Создание недостающих запчастей...")
    created = 0
    
    existing_names = {p.name_ru for p in Part.query.all()}
    existing_names.update({p.name for p in Part.query.all() if p.name})
    
    for ru_name, data in PARTS_TRANSLATIONS.items():
        if ru_name not in existing_names:
            # Создаем новую запчасть
            part = Part(
                name_ru=ru_name,
                name_en=data['en'],
                name_he=data['he'],
                name=ru_name,  # для обратной совместимости
                category=data['category'],
                is_active=True,
                sort_order=0
            )
            db.session.add(part)
            created += 1
            print(f"  ➕ {ru_name}")
            print(f"    EN: {data['en']}")
            print(f"    HE: {data['he']}")
            print(f"    Категория: {data['category']}")
    
    if created > 0:
        db.session.commit()
        print(f"\n✅ Создано {created} новых запчастей")
    else:
        print("\nℹ️  Все запчасти уже существуют в базе")
    
    return created


def show_statistics():
    """Показывает статистику по запчастям"""
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА ПО ЗАПЧАСТЯМ")
    print("="*60)
    
    total_parts = Part.query.count()
    parts_with_en = Part.query.filter(Part.name_en.isnot(None)).count()
    parts_with_he = Part.query.filter(Part.name_he.isnot(None)).count()
    parts_with_both = Part.query.filter(
        Part.name_en.isnot(None),
        Part.name_he.isnot(None)
    ).count()
    
    print(f"\nВсего запчастей: {total_parts}")
    print(f"С переводом на английский: {parts_with_en} ({parts_with_en*100//total_parts if total_parts > 0 else 0}%)")
    print(f"С переводом на иврит: {parts_with_he} ({parts_with_he*100//total_parts if total_parts > 0 else 0}%)")
    print(f"С обоими переводами: {parts_with_both} ({parts_with_both*100//total_parts if total_parts > 0 else 0}%)")
    
    print("\n📁 По категориям:")
    categories = db.session.query(Part.category).distinct().all()
    for cat_tuple in categories:
        cat = cat_tuple[0]
        total = Part.query.filter_by(category=cat).count()
        with_en = Part.query.filter_by(category=cat).filter(Part.name_en.isnot(None)).count()
        with_he = Part.query.filter_by(category=cat).filter(Part.name_he.isnot(None)).count()
        
        cat_en = CATEGORY_TRANSLATIONS.get(cat, {}).get('en', '?')
        cat_he = CATEGORY_TRANSLATIONS.get(cat, {}).get('he', '?')
        
        print(f"\n  {cat} / {cat_en} / {cat_he}")
        print(f"    Всего: {total}")
        print(f"    EN: {with_en}/{total}")
        print(f"    HE: {with_he}/{total}")


def migrate():
    """Запуск миграции"""
    with app.app_context():
        try:
            print("🚀 МИГРАЦИЯ: Добавление многоязычности для запчастей")
            print("="*60)
            
            # 1. Информация о категориях
            add_category_translations()
            
            # 2. Обновление переводов существующих запчастей
            updated, not_found = add_parts_translations()
            
            # 3. Создание недостающих запчастей
            created = create_missing_parts()
            
            # 4. Статистика
            show_statistics()
            
            print("\n" + "="*60)
            print("✅ МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            print("="*60)
            print(f"\n📈 Итоги:")
            print(f"  • Обновлено переводов: {updated}")
            print(f"  • Создано новых запчастей: {created}")
            if not_found:
                print(f"  • Не найдено в БД: {len(not_found)}")
            
        except Exception as e:
            print(f"\n❌ Ошибка миграции: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    migrate()
