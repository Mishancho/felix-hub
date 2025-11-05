#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт обновления переводов категорий
Добавляет отсутствующие переводы на английский и иврит
"""

import os
from app import app, db
from models import Category

def update_category_translations():
    """Обновить переводы категорий"""
    
    with app.app_context():
        print("=" * 60)
        print("🔄 Обновление переводов категорий")
        print("=" * 60)
        
        # Маппинг переводов для категорий
        translations = {
            'тормоза': {
                'name_ru': 'Тормоза',
                'name_en': 'Brakes',
                'name_he': 'בלמים'
            },
            'типуль': {
                'name_ru': 'Типуль',
                'name_en': 'Maintenance',
                'name_he': 'טיפול'
            },
            'жидкости\\масла': {
                'name_ru': 'Жидкости\\Масла',
                'name_en': 'Fluids\\Oils',
                'name_he': 'נוזלים\\שמנים'
            },
            'типуль\\кузов': {
                'name_ru': 'Типуль\\Кузов',
                'name_en': 'Maintenance\\Body',
                'name_he': 'טיפול\\מרכב'
            },
            'жидкости\\масла\\химия': {
                'name_ru': 'Жидкости\\Масла\\Химия',
                'name_en': 'Fluids\\Oils\\Chemistry',
                'name_he': 'נוזלים\\שמנים\\כימיה'
            }
        }
        
        # Получаем все категории
        categories = Category.query.all()
        updated_count = 0
        
        for category in categories:
            # Проверяем, нужно ли обновление
            needs_update = False
            
            # Нормализуем название для поиска
            cat_name_lower = category.name.lower()
            
            # Ищем подходящий перевод
            translation = None
            for key, trans in translations.items():
                if key in cat_name_lower or cat_name_lower in key:
                    translation = trans
                    break
            
            if translation:
                # Обновляем только если поля пустые
                if not category.name_ru or category.name_ru == category.name:
                    category.name_ru = translation['name_ru']
                    needs_update = True
                
                if not category.name_en:
                    category.name_en = translation['name_en']
                    needs_update = True
                
                if not category.name_he:
                    category.name_he = translation['name_he']
                    needs_update = True
                
                if needs_update:
                    print(f"✅ Обновлена категория: {category.name}")
                    print(f"   RU: {category.name_ru}")
                    print(f"   EN: {category.name_en}")
                    print(f"   HE: {category.name_he}")
                    updated_count += 1
        
        # Сохраняем изменения
        if updated_count > 0:
            db.session.commit()
            print("=" * 60)
            print(f"✅ Обновлено категорий: {updated_count}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("ℹ️  Все категории уже имеют переводы")
            print("=" * 60)

if __name__ == '__main__':
    update_category_translations()
