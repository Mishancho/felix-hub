#!/usr/bin/env python3
"""
Миграция для исправления поля name в таблице parts

Эта миграция:
1. Заполняет поле name значением из name_ru для существующих записей
2. Делает поле name nullable для новых записей (если используется SQLite, это сложно, поэтому просто заполняем)
"""

import os
import sys

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Part

def run_migration():
    """Запустить миграцию"""
    with app.app_context():
        try:
            print("🔄 Начало миграции fix_parts_name_field...")
            
            # Получаем все запчасти где name = NULL
            parts_to_fix = Part.query.filter(
                (Part.name == None) | (Part.name == '')
            ).all()
            
            if not parts_to_fix:
                print("✅ Все записи уже имеют значение в поле name")
                return
            
            print(f"📝 Найдено {len(parts_to_fix)} записей для обновления")
            
            # Обновляем каждую запчасть
            for part in parts_to_fix:
                if part.name_ru:
                    part.name = part.name_ru
                    print(f"  ✓ Обновлена запчасть ID {part.id}: name = '{part.name_ru}'")
                else:
                    # Если даже name_ru пустое, устанавливаем заглушку
                    part.name = 'N/A'
                    print(f"  ⚠️ Запчасть ID {part.id} не имеет name_ru, установлено 'N/A'")
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"✅ Миграция завершена успешно! Обновлено {len(parts_to_fix)} записей")
            
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_migration()
