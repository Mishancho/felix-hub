#!/usr/bin/env python3
"""
Экстренное исправление БД: добавление колонок многоязычности
Запуск: python fix_db_quick.py
"""

import os
import sys
from app import app, db
from sqlalchemy import text

def quick_fix():
    """Быстрое исправление: добавление недостающих колонок"""
    with app.app_context():
        print("🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ БД")
        print("="*60)
        
        try:
            with db.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    # Добавляем колонки для категорий
                    print("\n📋 Добавление колонок для categories...")
                    conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_en VARCHAR(120)"))
                    conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_he VARCHAR(120)"))
                    conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_ru VARCHAR(120)"))
                    print("  ✓ Колонки categories добавлены")
                    
                    # Добавляем колонки для запчастей
                    print("\n📋 Добавление колонок для parts...")
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_en VARCHAR(250)"))
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_he VARCHAR(250)"))
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS name_ru VARCHAR(250)"))
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_en TEXT"))
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_he TEXT"))
                    conn.execute(text("ALTER TABLE parts ADD COLUMN IF NOT EXISTS description_ru TEXT"))
                    print("  ✓ Колонки parts добавлены")
                    
                    # Обновляем переводы категорий
                    print("\n📁 Обновление переводов категорий...")
                    translations = [
                        ("UPDATE categories SET name_ru = 'Тормоза', name_en = 'Brakes', name_he = 'בלמים' WHERE name = 'Тормоза'"),
                        ("UPDATE categories SET name_ru = 'Двигатель', name_en = 'Engine', name_he = 'מנוע' WHERE name = 'Двигатель'"),
                        ("UPDATE categories SET name_ru = 'Подвеска', name_en = 'Suspension', name_he = 'מתלים' WHERE name = 'Подвеска'"),
                        ("UPDATE categories SET name_ru = 'Электрика', name_en = 'Electrical', name_he = 'חשמל' WHERE name = 'Электрика'"),
                        ("UPDATE categories SET name_ru = 'Расходники', name_en = 'Consumables', name_he = 'מתכלים' WHERE name = 'Расходники'"),
                        ("UPDATE categories SET name_ru = 'Добавки', name_en = 'Additives', name_he = 'תוספים' WHERE name = 'Добавки'"),
                        ("UPDATE categories SET name_ru = 'Типуль', name_en = 'Maintenance', name_he = 'טיפול' WHERE name = 'Типуль'")
                    ]
                    
                    for sql in translations:
                        conn.execute(text(sql))
                    
                    print("  ✓ Переводы обновлены")
                    
                    trans.commit()
                    
                    print("\n" + "="*60)
                    print("✅ ИСПРАВЛЕНИЕ УСПЕШНО ЗАВЕРШЕНО!")
                    print("="*60)
                    print("\n📝 Теперь можно импортировать каталог запчастей")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"\n❌ Ошибка при выполнении SQL: {e}")
                    raise
                    
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    quick_fix()
