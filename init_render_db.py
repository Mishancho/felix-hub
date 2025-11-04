#!/usr/bin/env python3
"""
Скрипт инициализации базы данных на Render

Использование:
    python init_render_db.py
"""

import os
import sys
from app import app, db
from models import Mechanic, Category
from sqlalchemy import text, inspect


def column_exists(table_name, column_name):
    """Проверка существования колонки"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def run_migrations():
    """Запуск необходимых миграций"""
    print("\n🔄 Проверка и запуск миграций...")
    
    # Миграция 1: Добавление многоязычности для категорий
    if not column_exists('categories', 'name_en'):
        print("\n📋 Миграция: Добавление многоязычности для категорий...")
        
        try:
            with db.engine.connect() as conn:
                trans = conn.begin()
                try:
                    # Добавляем колонки для переводов
                    conn.execute(text("ALTER TABLE categories ADD COLUMN name_en VARCHAR(120)"))
                    conn.execute(text("ALTER TABLE categories ADD COLUMN name_he VARCHAR(120)"))
                    conn.execute(text("ALTER TABLE categories ADD COLUMN name_ru VARCHAR(120)"))
                    
                    trans.commit()
                    print("  ✓ Колонки для переводов добавлены")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"  ❌ Ошибка: {e}")
                    raise
            
            # Обновляем переводы для существующих категорий
            CATEGORY_TRANSLATIONS = {
                'Тормоза': {'en': 'Brakes', 'he': 'בלמים'},
                'Двигатель': {'en': 'Engine', 'he': 'מנוע'},
                'Подвеска': {'en': 'Suspension', 'he': 'מתלים'},
                'Электрика': {'en': 'Electrical', 'he': 'חשמל'},
                'Расходники': {'en': 'Consumables', 'he': 'מתכלים'},
                'Добавки': {'en': 'Additives', 'he': 'תוספים'},
                'Типуль': {'en': 'Maintenance', 'he': 'טיפול'}
            }
            
            updated = 0
            for ru_name, translations in CATEGORY_TRANSLATIONS.items():
                category = Category.query.filter_by(name=ru_name).first()
                if category:
                    with db.engine.connect() as conn:
                        trans = conn.begin()
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
                                    'name_en': translations['en'],
                                    'name_he': translations['he']
                                }
                            )
                            trans.commit()
                            updated += 1
                        except Exception as e:
                            trans.rollback()
                            print(f"  ⚠️  Не удалось обновить {ru_name}: {e}")
            
            print(f"  ✓ Обновлено переводов: {updated}")
            
        except Exception as e:
            print(f"  ❌ Ошибка миграции категорий: {e}")
            # Продолжаем работу, даже если миграция не удалась
    else:
        print("  ℹ️  Миграция категорий уже выполнена")
    
    # Миграция 2: Добавление многоязычности для запчастей
    if not column_exists('parts', 'name_en'):
        print("\n📋 Миграция: Добавление многоязычности для запчастей...")
        
        try:
            with db.engine.connect() as conn:
                trans = conn.begin()
                try:
                    # Добавляем колонки для переводов
                    if not column_exists('parts', 'name_en'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN name_en VARCHAR(250)"))
                    if not column_exists('parts', 'name_he'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN name_he VARCHAR(250)"))
                    if not column_exists('parts', 'name_ru'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN name_ru VARCHAR(250)"))
                    if not column_exists('parts', 'description_en'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN description_en TEXT"))
                    if not column_exists('parts', 'description_he'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN description_he TEXT"))
                    if not column_exists('parts', 'description_ru'):
                        conn.execute(text("ALTER TABLE parts ADD COLUMN description_ru TEXT"))
                    
                    trans.commit()
                    print("  ✓ Колонки для переводов запчастей добавлены")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"  ❌ Ошибка: {e}")
                    raise
            
        except Exception as e:
            print(f"  ❌ Ошибка миграции запчастей: {e}")
    else:
        print("  ℹ️  Миграция запчастей уже выполнена")


def init_database():
    """Инициализация базы данных с созданием таблиц"""
    with app.app_context():
        print("="*60)
        print("🚀 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ НА RENDER")
        print("="*60)
        
        # Определяем тип БД
        db_url = db.engine.url
        db_type = 'PostgreSQL' if 'postgresql' in str(db_url) else 'SQLite'
        print(f"\n📊 База данных: {db_type}")
        
        print("\n🔄 Создание таблиц...")
        
        # Создание всех таблиц
        db.create_all()
        print("✅ Таблицы созданы")
        
        # Запуск миграций
        run_migrations()
        
        # Проверка наличия механиков
        print("\n📊 Проверка данных...")
        mechanic_count = Mechanic.query.count()
        print(f"  Механиков в системе: {mechanic_count}")
        
        category_count = Category.query.count()
        print(f"  Категорий в системе: {category_count}")
        
        print("\n" + "="*60)
        if mechanic_count == 0:
            print("⚠️  База данных готова, но пуста")
            print("📝 Следующие шаги:")
            print("   1. Создайте первого механика через админ-панель")
            print("   2. Импортируйте каталог запчастей")
            print("\n🔗 URL админ-панели: https://felix-hub.onrender.com/admin/login")
            print("🔑 Пароль: felix2025")
        else:
            print("✅ БАЗА ДАННЫХ ПОЛНОСТЬЮ ГОТОВА К РАБОТЕ")
            print(f"   • {mechanic_count} механиков")
            print(f"   • {category_count} категорий")
        print("="*60)


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
