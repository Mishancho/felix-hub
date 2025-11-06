#!/usr/bin/env python3
"""
Скрипт диагностики проблем с отображением на Render
Проверяет конфигурацию и выводит полезную информацию
"""

import os
import sys

def check_environment():
    """Проверка переменных окружения"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 60)
    
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    optional_vars = ['ALLOW_ANONYMOUS_ORDERS', 'PORT']
    
    print("\n✅ Обязательные переменные:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Скрываем чувствительные данные
            if var == 'SECRET_KEY':
                display = value[:5] + "..." if len(value) > 5 else "SET"
            elif var == 'DATABASE_URL':
                display = "postgresql://***" if value.startswith('postgresql://') else "SET"
            else:
                display = value
            print(f"   ✓ {var}: {display}")
        else:
            print(f"   ✗ {var}: НЕ УСТАНОВЛЕНА")
    
    print("\n📋 Опциональные переменные:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✓ {var}: {value}")
        else:
            print(f"   - {var}: не установлена (используется значение по умолчанию)")


def check_static_files():
    """Проверка наличия статических файлов"""
    print("\n" + "=" * 60)
    print("📁 ПРОВЕРКА СТАТИЧЕСКИХ ФАЙЛОВ")
    print("=" * 60)
    
    static_files = [
        'static/css/mobile-responsive.css',
        'static/css/language-switcher.css',
        'static/css/fixed-header-nav.css',
        'static/js/language.js',
        'static/js/mobile-enhancements.js',
        'static/js/nav-scroll.js',
    ]
    
    all_exist = True
    for filepath in static_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✓ {filepath} ({size} bytes)")
        else:
            print(f"   ✗ {filepath} - НЕ НАЙДЕН!")
            all_exist = False
    
    if all_exist:
        print("\n✅ Все статические файлы на месте")
    else:
        print("\n❌ Некоторые файлы отсутствуют!")


def check_app_config():
    """Проверка конфигурации приложения"""
    print("\n" + "=" * 60)
    print("⚙️  ПРОВЕРКА КОНФИГУРАЦИИ ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    try:
        from app import app
        
        print(f"\n✓ DEBUG режим: {app.debug}")
        print(f"✓ SECRET_KEY установлен: {'Да' if app.config.get('SECRET_KEY') else 'Нет'}")
        print(f"✓ DATABASE_URL установлен: {'Да' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Нет'}")
        print(f"✓ UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
        print(f"✓ Языки: {', '.join(app.config.get('LANGUAGES', {}).keys())}")
        
        # Проверка ProxyFix
        if hasattr(app, 'wsgi_app'):
            wsgi_class = app.wsgi_app.__class__.__name__
            if 'ProxyFix' in wsgi_class:
                print(f"✓ ProxyFix: УСТАНОВЛЕН")
            else:
                print(f"⚠️  ProxyFix: НЕ НАЙДЕН (могут быть проблемы на Render)")
        
        # Проверка cache busting
        try:
            from flask import Flask
            test_app = Flask(__name__)
            with test_app.app_context():
                if hasattr(app, '_static_version') or 'static_url' in dir(app):
                    print(f"✓ Cache busting: НАСТРОЕН")
                else:
                    print(f"⚠️  Cache busting: НЕ НАСТРОЕН")
        except:
            print(f"⚠️  Cache busting: НЕ УДАЛОСЬ ПРОВЕРИТЬ")
        
        print("\n✅ Конфигурация приложения проверена")
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке конфигурации: {e}")


def check_database():
    """Проверка подключения к базе данных"""
    print("\n" + "=" * 60)
    print("🗄️  ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    try:
        from app import app, db
        from models import Mechanic, Order, Part, Category
        
        with app.app_context():
            # Проверка подключения
            try:
                db.session.execute('SELECT 1')
                print("\n✓ Подключение к БД: УСПЕШНО")
            except Exception as e:
                print(f"\n✗ Подключение к БД: ОШИБКА - {e}")
                return
            
            # Проверка таблиц
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"✓ Найдено таблиц: {len(tables)}")
            
            expected_tables = ['mechanics', 'orders', 'parts', 'categories']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"⚠️  Отсутствующие таблицы: {', '.join(missing_tables)}")
            else:
                print(f"✓ Все основные таблицы присутствуют")
            
            # Проверка данных
            try:
                mechanic_count = Mechanic.query.count()
                order_count = Order.query.count()
                part_count = Part.query.count()
                category_count = Category.query.count()
                
                print(f"\n📊 Статистика данных:")
                print(f"   Механиков: {mechanic_count}")
                print(f"   Заказов: {order_count}")
                print(f"   Деталей: {part_count}")
                print(f"   Категорий: {category_count}")
                
            except Exception as e:
                print(f"\n⚠️  Ошибка при проверке данных: {e}")
        
        print("\n✅ База данных проверена")
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке БД: {e}")


def generate_test_urls():
    """Генерация тестовых URL для проверки"""
    print("\n" + "=" * 60)
    print("🔗 ТЕСТОВЫЕ URL ДЛЯ ПРОВЕРКИ")
    print("=" * 60)
    
    base_url = os.getenv('RENDER_EXTERNAL_URL', 'https://felix-hub.onrender.com')
    
    test_urls = [
        ('Главная страница', '/'),
        ('Админ панель', '/admin/login'),
        ('Механик вход', '/mechanic/login'),
        ('CSS: Mobile', '/static/css/mobile-responsive.css'),
        ('CSS: Language', '/static/css/language-switcher.css'),
        ('CSS: Header', '/static/css/fixed-header-nav.css'),
        ('JS: Language', '/static/js/language.js'),
        ('JS: Mobile', '/static/js/mobile-enhancements.js'),
    ]
    
    print(f"\nБазовый URL: {base_url}\n")
    for name, path in test_urls:
        full_url = base_url + path
        print(f"   {name}:")
        print(f"   {full_url}\n")


def print_troubleshooting():
    """Вывод советов по устранению проблем"""
    print("=" * 60)
    print("🔧 СОВЕТЫ ПО УСТРАНЕНИЮ ПРОБЛЕМ")
    print("=" * 60)
    
    print("""
1. ЕСЛИ СТИЛИ НЕ ПРИМЕНЯЮТСЯ:
   - Очистите кэш браузера (Ctrl+Shift+Delete)
   - Жесткая перезагрузка (Ctrl+Shift+R или Cmd+Shift+R)
   - Откройте в режиме Инкогнито
   - Проверьте DevTools → Network (статус файлов должен быть 200)

2. ЕСЛИ ФАЙЛЫ НЕ ЗАГРУЖАЮТСЯ (404):
   - Убедитесь что все файлы закоммичены в git
   - Проверьте .gitignore (не игнорируется ли папка static/)
   - Перезапустите деплой на Render

3. ЕСЛИ ПРОБЛЕМЫ С HTTPS:
   - Проверьте что ProxyFix установлен (см. выше)
   - Убедитесь что все url_for() используются правильно
   - Проверьте заголовки в DevTools → Network

4. ЕСЛИ НИЧЕГО НЕ ПОМОГЛО:
   - Проверьте логи на Render Dashboard
   - Сделайте скриншот DevTools (Console + Network)
   - Сравните HTML исходный код локальной и продакшен версий
   
5. ЭКСТРЕННОЕ РЕШЕНИЕ:
   - В Render Dashboard → Settings
   - Нажмите "Clear build cache & deploy"
   - Дождитесь завершения деплоя
   - Очистите кэш браузера
   
📖 Полная документация: RENDER_DISPLAY_FIX.md
""")


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 FELIX HUB - ДИАГНОСТИКА RENDER")
    print("=" * 60)
    
    # Проверки
    check_environment()
    check_static_files()
    check_app_config()
    check_database()
    generate_test_urls()
    print_troubleshooting()
    
    print("\n" + "=" * 60)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
