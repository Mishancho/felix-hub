#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для экспорта запчастей из локальной БД в формат для импорта на Render
"""

import os
import sys
from datetime import datetime

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Part, Category

def export_parts():
    """Экспортировать все запчасти из локальной БД"""
    with app.app_context():
        # Получаем все запчасти
        parts = Part.query.order_by(Part.category, Part.sort_order).all()
        
        if not parts:
            print("❌ Нет запчастей для экспорта")
            return
        
        print(f"✅ Найдено {len(parts)} запчастей")
        print("\n" + "="*80)
        
        # Группируем по категориям
        categories = {}
        for part in parts:
            if part.category not in categories:
                categories[part.category] = []
            categories[part.category].append(part)
        
        # Создаем SQL INSERT запросы для Render
        sql_file = "import_parts_to_render.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write("-- SQL скрипт для импорта запчастей на Render\n")
            f.write(f"-- Создано: {datetime.now()}\n\n")
            
            for category, parts_list in categories.items():
                f.write(f"\n-- Категория: {category}\n")
                for part in parts_list:
                    # Экранируем одинарные кавычки
                    name = part.name.replace("'", "''") if part.name else None
                    name_ru = part.name_ru.replace("'", "''") if part.name_ru else None
                    name_en = part.name_en.replace("'", "''") if part.name_en else None
                    name_he = part.name_he.replace("'", "''") if part.name_he else None
                    desc_ru = part.description_ru.replace("'", "''") if part.description_ru else None
                    desc_en = part.description_en.replace("'", "''") if part.description_en else None
                    desc_he = part.description_he.replace("'", "''") if part.description_he else None
                    category_name = part.category.replace("'", "''") if part.category else None
                    
                    f.write(f"INSERT INTO parts (name, name_ru, name_en, name_he, description_ru, description_en, description_he, category, is_active, sort_order, created_at, updated_at) VALUES ")
                    f.write(f"('{name}', '{name_ru}', ")
                    f.write(f"'{name_en}' IF name_en else 'NULL', ")
                    f.write(f"'{name_he}' IF name_he else 'NULL', ")
                    f.write(f"'{desc_ru}' IF desc_ru else 'NULL', ")
                    f.write(f"'{desc_en}' IF desc_en else 'NULL', ")
                    f.write(f"'{desc_he}' IF desc_he else 'NULL', ")
                    f.write(f"'{category_name}', {part.is_active}, {part.sort_order}, NOW(), NOW());\n")
        
        print(f"\n✅ SQL скрипт создан: {sql_file}")
        print("\nТеперь можно использовать этот SQL для импорта на Render")

if __name__ == '__main__':
    export_parts()
