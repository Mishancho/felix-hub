#!/usr/bin/env python3
"""
Скрипт для выполнения миграций БД Felix Hub

Запускать ПОСЛЕ успешного деплоя на Render:
    python run_migrations.py

Или в Render Shell:
    python run_migrations.py
"""

import os
import sys
from app import app, db
from models import Category, Part
from sqlalchemy import inspect, text


def column_exists(table_name, column_name):
    """Проверка существования колонки"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def run_migrations():
    """Выполнение всех миграций"""
    with app.app_context():
        print("="*60)
        print("🔄 Запуск миграций БД...")
        print("="*60)
        
        # Миграция 1: Многоязычность для категорий
        if 'categories' in inspect(db.engine).get_table_names():
            if not column_exists('categories', 'name_en'):
                print("\n📋 Миграция 1: Добавление многоязычности для категорий...")
                with db.engine.connect() as conn:
                    trans = conn.begin()
                    try:
                        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_en VARCHAR(120)"))
                        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_he VARCHAR(120)"))
                        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_ru VARCHAR(120)"))
                        trans.commit()
                        print("  ✅ Колонки для категорий добавлены")
                        
                        # Обновление переводов
                        update_category_translations()
                    except Exception as e:
                        trans.rollback()
                        print(f"  ❌ Ошибка: {e}")
                        return False
            else:
                print("\n✓ Миграция 1: Многоязычность категорий уже настроена")
        
        # Миграция 2: Многоязычность для запчастей
        if 'parts' in inspect(db.engine).get_table_names():
            if not column_exists('parts', 'name_ru'):
                print("\n📋 Миграция 2: Добавление многоязычности для запчастей...")
                with db.engine.connect() as conn:
                    trans = conn.begin()
                    try:
                        # Добавляем все колонки для многоязычности
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_en VARCHAR(250)"))
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_he VARCHAR(250)"))
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_ru VARCHAR(250)"))
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_en TEXT"))
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_he TEXT"))
                        conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_ru TEXT"))
                        trans.commit()
                        print("  ✅ Колонки для запчастей добавлены")
                    except Exception as e:
                        trans.rollback()
                        print(f"  ❌ Ошибка: {e}")
                        return False
            else:
                print("\n✓ Миграция 2: Многоязычность запчастей уже настроена")
        
        print("\n" + "="*60)
        print("✅ Все миграции успешно выполнены!")
        print("="*60)
        return True


def update_category_translations():
    """Обновление переводов для стандартных категорий"""
    print("  📝 Обновление переводов категорий...")
    
    translations = {
        'Тормоза': {'en': 'Brakes', 'he': 'בלמים'},
        'Двигатель': {'en': 'Engine', 'he': 'מנוע'},
        'Подвеска': {'en': 'Suspension', 'he': 'מתלים'},
        'Электрика': {'en': 'Electrical', 'he': 'חשמל'},
        'Расходники': {'en': 'Consumables', 'he': 'מתכלים'},
        'Добавки': {'en': 'Additives', 'he': 'תוספים'},
        'Типуль': {'en': 'Maintenance', 'he': 'טיפול'}
    }
    
    updated = 0
    for ru_name, trans in translations.items():
        category = Category.query.filter_by(name=ru_name).first()
        if category:
            with db.engine.connect() as conn:
                trans_db = conn.begin()
                try:
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
                            'name_en': trans['en'],
                            'name_he': trans['he']
                        }
                    )
                    trans_db.commit()
                    updated += 1
                except Exception as e:
                    trans_db.rollback()
                    print(f"    ⚠️  Не удалось обновить {ru_name}: {e}")
    
    if updated > 0:
        print(f"  ✅ Обновлено переводов: {updated}")


if __name__ == '__main__':
    try:
        success = run_migrations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
