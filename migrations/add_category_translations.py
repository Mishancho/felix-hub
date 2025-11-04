"""
Миграция: Добавление полей переводов для категорий
Версия: 2.2.4
Дата: 04.11.2024
"""

import os
import sys

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Category
from dotenv import load_dotenv
from sqlalchemy import text

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


def add_translation_columns():
    """Добавляет колонки для переводов в таблицу categories"""
    print("📋 Добавление колонок для переводов...")
    
    try:
        with db.engine.connect() as conn:
            # Проверяем, существуют ли уже колонки
            result = conn.execute(text("PRAGMA table_info(categories)"))
            columns = [row[1] for row in result]
            
            if 'name_en' not in columns:
                conn.execute(text("ALTER TABLE categories ADD COLUMN name_en VARCHAR(120)"))
                print("  ✓ Добавлена колонка name_en")
            else:
                print("  ℹ️  Колонка name_en уже существует")
            
            if 'name_he' not in columns:
                conn.execute(text("ALTER TABLE categories ADD COLUMN name_he VARCHAR(120)"))
                print("  ✓ Добавлена колонка name_he")
            else:
                print("  ℹ️  Колонка name_he уже существует")
            
            if 'name_ru' not in columns:
                conn.execute(text("ALTER TABLE categories ADD COLUMN name_ru VARCHAR(120)"))
                print("  ✓ Добавлена колонка name_ru")
            else:
                print("  ℹ️  Колонка name_ru уже существует")
            
            conn.commit()
        
        print("✅ Колонки успешно добавлены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка добавления колонок: {e}")
        return False


def update_category_translations():
    """Обновляет переводы для существующих категорий"""
    print("\n📁 Обновление переводов категорий...")
    updated = 0
    
    for ru_name, translations in CATEGORY_TRANSLATIONS.items():
        category = Category.query.filter_by(name=ru_name).first()
        
        if category:
            # Обновляем переводы через raw SQL, так как модель может не иметь этих полей
            try:
                with db.engine.connect() as conn:
                    conn.execute(
                        text("""
                            UPDATE categories 
                            SET name_ru = :name_ru,
                                name_en = :name_en,
                                name_he = :name_he
                            WHERE id = :id
                        """),
                        {
                            'id': category.id,
                            'name_ru': ru_name,
                            'name_en': translations['en'],
                            'name_he': translations['he']
                        }
                    )
                    conn.commit()
                
                updated += 1
                print(f"  ✓ {ru_name}")
                print(f"    EN: {translations['en']}")
                print(f"    HE: {translations['he']}")
                
            except Exception as e:
                print(f"  ❌ Ошибка обновления {ru_name}: {e}")
        else:
            print(f"  ⚠️  Категория не найдена: {ru_name}")
    
    print(f"\n✅ Обновлено: {updated} категорий")
    return updated


def show_statistics():
    """Показывает статистику по категориям"""
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА ПО КАТЕГОРИЯМ")
    print("="*60)
    
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                name_ru,
                name_en,
                name_he,
                is_active
            FROM categories
            ORDER BY sort_order, name
        """))
        
        categories = result.fetchall()
        
        print(f"\nВсего категорий: {len(categories)}")
        print("\nДетали:")
        print("-" * 60)
        
        for cat in categories:
            print(f"\n#{cat[0]}: {cat[1]}")
            print(f"  RU: {cat[2] or 'не указано'}")
            print(f"  EN: {cat[3] or 'не указано'}")
            print(f"  HE: {cat[4] or 'не указано'}")
            print(f"  Активна: {'Да' if cat[5] else 'Нет'}")


def migrate():
    """Запуск миграции"""
    with app.app_context():
        try:
            print("🚀 МИГРАЦИЯ: Добавление многоязычности для категорий")
            print("="*60)
            
            # 1. Добавление колонок
            if not add_translation_columns():
                print("❌ Не удалось добавить колонки")
                return
            
            # 2. Обновление переводов
            update_category_translations()
            
            # 3. Статистика
            show_statistics()
            
            print("\n" + "="*60)
            print("✅ МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Ошибка миграции: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    migrate()
