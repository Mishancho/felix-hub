#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки добавленных запчастей
"""

from app import app, db
from models import Part, Category

def verify_parts():
    """Проверить добавленные запчасти"""
    with app.app_context():
        print("=" * 70)
        print("🔍 Проверка добавленных запчастей")
        print("=" * 70)
        
        # Список категорий для проверки
        categories_to_check = [
            "Лампочки",
            "типуль",
            "жидкости\\масла",
            "тормоза",
            "типуль\\кузов"
        ]
        
        total_parts = 0
        
        for cat_name in categories_to_check:
            parts = Part.query.filter_by(category=cat_name, is_active=True).all()
            print(f"\n📁 Категория: {cat_name}")
            print(f"   Количество запчастей: {len(parts)}")
            
            if parts:
                print(f"   Примеры:")
                for part in parts[:3]:  # Показываем первые 3
                    print(f"   • {part.name_ru}")
                    print(f"     EN: {part.name_en}")
                    print(f"     HE: {part.name_he}")
                
                if len(parts) > 3:
                    print(f"   ... и ещё {len(parts) - 3} запчастей")
            
            total_parts += len(parts)
        
        print("\n" + "=" * 70)
        print(f"✅ Всего проверено: {total_parts} активных запчастей")
        print("=" * 70)
        
        # Проверка многоязычности
        print("\n🌐 Проверка многоязычности (первая запчасть):")
        first_part = Part.query.filter_by(is_active=True).first()
        if first_part:
            print(f"   RU: {first_part.get_name('ru')}")
            print(f"   EN: {first_part.get_name('en')}")
            print(f"   HE: {first_part.get_name('he')}")

if __name__ == "__main__":
    verify_parts()
