#!/usr/bin/env python3
"""
Прямое тестирование добавления запчасти в базу
"""

from app import app, db
from models import Part

def test_add_part_direct():
    """Тест добавления запчасти напрямую в базу"""
    with app.app_context():
        try:
            print("📝 Создание тестовой запчасти...")
            
            part = Part(
                name_en="Direct Test Air Filter",
                name_he="פִּילְטֶר אווִיר טֶסט ישיר",
                name_ru="Прямой тестовый фильтр",
                description_ru="Тестовое описание",
                name="Прямой тестовый фильтр",  # Старое поле
                category="Типуль",
                is_active=True,
                sort_order=0
            )
            
            db.session.add(part)
            db.session.commit()
            
            print(f"✅ Запчасть успешно добавлена! ID: {part.id}")
            print(f"   Название (RU): {part.name_ru}")
            print(f"   Название (старое поле): {part.name}")
            print(f"   Категория: {part.category}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_add_part_direct()
