"""
Миграция: Добавление многоязычной поддержки для запчастей

Добавляет поля для хранения названий и описаний на трех языках:
- name_en, name_he, name_ru
- description_en, description_he, description_ru
"""

import os
import sys

# Добавляем родительскую директорию в путь для импорта моделей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Part
from sqlalchemy import text

def run_migration():
    """Выполнить миграцию для добавления многоязычной поддержки"""
    with app.app_context():
        try:
            print("🔄 Начало миграции: добавление многоязычной поддержки...")
            
            # Проверяем тип базы данных
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_postgres = db_url.startswith('postgresql://')
            
            print(f"📊 База данных: {'PostgreSQL' if is_postgres else 'SQLite'}")
            
            # Добавляем новые колонки
            with db.engine.connect() as conn:
                # Начинаем транзакцию
                trans = conn.begin()
                
                try:
                    print("➕ Добавление колонок для английского языка...")
                    conn.execute(text('ALTER TABLE parts ADD COLUMN name_en VARCHAR(250)'))
                    conn.execute(text('ALTER TABLE parts ADD COLUMN description_en TEXT'))
                    
                    print("➕ Добавление колонок для иврита...")
                    conn.execute(text('ALTER TABLE parts ADD COLUMN name_he VARCHAR(250)'))
                    conn.execute(text('ALTER TABLE parts ADD COLUMN description_he TEXT'))
                    
                    print("➕ Добавление колонок для русского языка...")
                    conn.execute(text('ALTER TABLE parts ADD COLUMN name_ru VARCHAR(250)'))
                    conn.execute(text('ALTER TABLE parts ADD COLUMN description_ru TEXT'))
                    
                    print("🔄 Копирование существующих данных в поле name_ru...")
                    conn.execute(text('UPDATE parts SET name_ru = name WHERE name_ru IS NULL'))
                    
                    print("✅ Колонки успешно добавлены!")
                    
                    # Коммитим транзакцию
                    trans.commit()
                    
                except Exception as e:
                    print(f"❌ Ошибка при добавлении колонок: {e}")
                    trans.rollback()
                    raise
            
            # Получаем статистику
            parts_count = Part.query.count()
            print(f"\n📊 Статистика:")
            print(f"   Всего запчастей: {parts_count}")
            
            if parts_count > 0:
                with_russian = Part.query.filter(Part.name_ru.isnot(None)).count()
                print(f"   С русским названием: {with_russian}")
                print(f"\n⚠️  Внимание: Необходимо заполнить названия на английском и иврите для всех запчастей!")
                print(f"   Используйте административную панель для редактирования запчастей.")
            
            print("\n✅ Миграция успешно завершена!")
            print("\n📝 Следующие шаги:")
            print("   1. Перезапустите приложение")
            print("   2. Зайдите в админ-панель: /admin/parts")
            print("   3. Отредактируйте каждую запчасть и добавьте переводы")
            
        except Exception as e:
            print(f"\n❌ Ошибка выполнения миграции: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    print("="*60)
    print("   МИГРАЦИЯ: Многоязычная поддержка запчастей")
    print("="*60)
    print()
    
    response = input("⚠️  Эта операция изменит структуру таблицы 'parts'. Продолжить? (yes/no): ")
    
    if response.lower() in ['yes', 'y', 'да', 'д']:
        run_migration()
    else:
        print("❌ Миграция отменена пользователем")
