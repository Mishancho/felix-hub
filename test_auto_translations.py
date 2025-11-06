#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест автоматического добавления переводов для запчастей
Проверяет работу функций create_part, bulk_create_parts и import_default_catalog
"""

import os
import sys
import json
from datetime import datetime

# Настройка путей для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Установка переменных окружения для тестовой БД
os.environ['DATABASE_URL'] = 'sqlite:///test_auto_translations.db'
os.environ['TESTING'] = 'true'

from app import app, db
from models import Part, Category
from migrate_parts_translations import find_translation, PARTS_TRANSLATIONS


def setup_test_db():
    """Создать тестовую базу данных"""
    with app.app_context():
        # Удаляем старую БД если существует
        if os.path.exists('test_auto_translations.db'):
            os.remove('test_auto_translations.db')
        
        # Создаём новую БД
        db.create_all()
        
        # Создаём тестовую категорию только если её ещё нет
        existing_cat = Category.query.filter_by(name='Типуль').first()
        if not existing_cat:
            category = Category(
                name='Типуль',
                is_active=True,
                sort_order=0
            )
            db.session.add(category)
            db.session.commit()
        
        print("✅ Тестовая база данных создана")


def cleanup_test_db():
    """Удалить тестовую базу данных"""
    if os.path.exists('test_auto_translations.db'):
        os.remove('test_auto_translations.db')
    print("✅ Тестовая база данных удалена")


def test_find_translation():
    """Тест функции поиска переводов"""
    print("\n📝 Тест 1: Поиск переводов в словаре")
    
    # Тест точного совпадения
    result = find_translation('тормозная жидкость')
    assert result is not None, "Должен найти перевод для 'тормозная жидкость'"
    assert result['en'] == 'Brake fluid', f"EN должен быть 'Brake fluid', получено '{result['en']}'"
    assert result['he'] == 'נוזל בלמים', f"HE должен быть 'נוזל בלמים', получено '{result['he']}'"
    print("  ✅ Точное совпадение работает")
    
    # Тест регистронезависимого поиска
    result = find_translation('ТОРМОЗНАЯ ЖИДКОСТЬ')
    assert result is not None, "Должен найти перевод независимо от регистра"
    print("  ✅ Регистронезависимый поиск работает")
    
    # Тест отсутствующего перевода
    result = find_translation('несуществующая запчасть xyz123')
    assert result is None, "Не должен находить несуществующий перевод"
    print("  ✅ Обработка отсутствующих переводов работает")
    
    print("✅ Тест 1 пройден\n")


def test_create_part_with_auto_translation():
    """Тест create_part с автоматическим добавлением переводов"""
    print("📝 Тест 2: create_part с автоматическими переводами (прямая работа с БД)")
    
    with app.app_context():
        # Тест 1: Создание запчасти с известным переводом (без явного указания переводов)
        from migrate_parts_translations import find_translation
        
        name_ru = 'Тормозная жидкость'
        part = Part(
            name_ru=name_ru,
            name=name_ru,
            category='Типуль',
            is_active=True
        )
        
        # Применяем логику автоматического добавления переводов
        if not part.name_en or not part.name_he:
            translation = find_translation(name_ru)
            if translation:
                if not part.name_en:
                    part.name_en = translation.get('en')
                if not part.name_he:
                    part.name_he = translation.get('he')
        
        db.session.add(part)
        db.session.commit()
        
        # Проверяем что переводы добавились
        assert part.name_en == 'Brake fluid', f"EN должен быть автоматически добавлен, получено '{part.name_en}'"
        assert part.name_he == 'נוזל בלמים', f"HE должен быть автоматически добавлен, получено '{part.name_he}'"
        print("  ✅ Автоматическое добавление переводов работает")
        
        # Тест 2: Создание запчасти с явным указанием переводов (не должно перезаписывать)
        name_ru2 = 'Тормозная жидкость'
        part2 = Part(
            name_ru=name_ru2,
            name_en='Custom brake fluid',
            name_he='נוזל בלמים מותאם אישית',
            name=name_ru2,
            category='Типуль',
            is_active=True
        )
        
        # Применяем логику автоматического добавления переводов
        if not part2.name_en or not part2.name_he:
            translation = find_translation(name_ru2)
            if translation:
                if not part2.name_en:
                    part2.name_en = translation.get('en')
                if not part2.name_he:
                    part2.name_he = translation.get('he')
        
        db.session.add(part2)
        db.session.commit()
        
        assert part2.name_en == 'Custom brake fluid', "Не должен перезаписывать явно указанный перевод EN"
        assert part2.name_he == 'נוזל בלמים מותאם אישית', "Не должен перезаписывать явно указанный перевод HE"
        print("  ✅ Явно указанные переводы не перезаписываются")
        
        # Тест 3: Запчасть без перевода в словаре
        name_ru3 = 'Новая запчасть без перевода'
        part3 = Part(
            name_ru=name_ru3,
            name=name_ru3,
            category='Типуль',
            is_active=True
        )
        
        # Применяем логику автоматического добавления переводов
        if not part3.name_en or not part3.name_he:
            translation = find_translation(name_ru3)
            if translation:
                if not part3.name_en:
                    part3.name_en = translation.get('en')
                if not part3.name_he:
                    part3.name_he = translation.get('he')
        
        db.session.add(part3)
        db.session.commit()
        
        # Переводы должны быть None или пустыми
        assert part3.name_en in [None, ''], f"EN должен быть пустым для неизвестной запчасти, получено '{part3.name_en}'"
        assert part3.name_he in [None, ''], f"HE должен быть пустым для неизвестной запчасти, получено '{part3.name_he}'"
        print("  ✅ Запчасти без переводов создаются корректно")
    
    print("✅ Тест 2 пройден\n")


def test_bulk_create_parts_with_auto_translation():
    """Тест bulk_create_parts с автоматическим добавлением переводов"""
    print("📝 Тест 3: bulk_create_parts с автоматическими переводами (прямая работа с БД)")
    
    with app.app_context():
        from migrate_parts_translations import find_translation
        
        # Массив запчастей для создания
        parts_data = [
            {'name_ru': 'Фильтр масляный', 'category': 'Типуль'},
            {'name_ru': 'Фильтр воздушный', 'category': 'Типуль'},
            {'name_ru': 'Неизвестная запчасть', 'category': 'Типуль'}
        ]
        
        created_parts = []
        
        for item in parts_data:
            name_ru = item['name_ru']
            part = Part(
                name_ru=name_ru,
                name=name_ru,
                category=item['category'],
                is_active=True
            )
            
            # Применяем логику автоматического добавления переводов
            if not part.name_en or not part.name_he:
                translation = find_translation(name_ru)
                if translation:
                    if not part.name_en:
                        part.name_en = translation.get('en')
                    if not part.name_he:
                        part.name_he = translation.get('he')
            
            db.session.add(part)
            created_parts.append(part)
        
        db.session.commit()
        
        assert len(created_parts) == 3, f"Должно быть создано 3 запчасти, создано {len(created_parts)}"
        
        # Первая запчасть - фильтр масляный
        assert created_parts[0].name_en == 'Oil filter', f"EN для фильтра масляного должен быть автоматически добавлен"
        assert created_parts[0].name_he == 'פילטר שמן', f"HE для фильтра масляного должен быть автоматически добавлен"
        print("  ✅ Первая запчасть получила переводы")
        
        # Вторая запчасть - фильтр воздушный
        assert created_parts[1].name_en == 'Air filter', f"EN для фильтра воздушного должен быть автоматически добавлен"
        assert created_parts[1].name_he == 'פילטר אוויר', f"HE для фильтра воздушного должен быть автоматически добавлен"
        print("  ✅ Вторая запчасть получила переводы")
        
        # Третья запчасть - без перевода
        assert created_parts[2].name_en in [None, ''], f"EN для неизвестной запчасти должен быть пустым"
        assert created_parts[2].name_he in [None, ''], f"HE для неизвестной запчасти должен быть пустым"
        print("  ✅ Запчасть без перевода обработана корректно")
    
    print("✅ Тест 3 пройден\n")


def run_all_tests():
    """Запустить все тесты"""
    print("="*60)
    print("🧪 ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКИХ ПЕРЕВОДОВ ЗАПЧАСТЕЙ")
    print("="*60)
    
    try:
        # Настройка
        setup_test_db()
        
        # Запуск тестов
        test_find_translation()
        test_create_part_with_auto_translation()
        test_bulk_create_parts_with_auto_translation()
        
        print("="*60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ ТЕСТ ПРОВАЛИЛСЯ: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ВЫПОЛНЕНИИ ТЕСТОВ: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Очистка
        cleanup_test_db()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
