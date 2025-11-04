#!/usr/bin/env python3
"""
Тестовый скрипт для проверки добавления запчасти
"""

import requests
import json

# URL приложения
BASE_URL = "http://127.0.0.1:8000"

# Данные для входа админа (используйте свои учетные данные)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_add_part():
    """Тест добавления запчасти"""
    
    # Создаем сессию
    session = requests.Session()
    
    # 1. Авторизуемся как админ
    print("🔐 Авторизация как админ...")
    login_response = session.post(
        f"{BASE_URL}/admin/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        },
        allow_redirects=False
    )
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Ошибка авторизации: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("✅ Авторизация успешна")
    
    # 2. Добавляем запчасть
    print("\n📝 Добавление запчасти в категорию 'Типуль'...")
    part_data = {
        "name_en": "Test Air Filter",
        "name_he": "פִּילְטֶר אווִיר טֶסט",
        "name_ru": "Тестовый фильтр воздушный",
        "description_en": "Test description EN",
        "description_he": "תיאור מבחן",
        "description_ru": "Тестовое описание",
        "category": "Типуль",
        "is_active": True,
        "sort_order": 0
    }
    
    add_response = session.post(
        f"{BASE_URL}/api/admin/parts",
        json=part_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Статус ответа: {add_response.status_code}")
    
    try:
        response_json = add_response.json()
        print(f"Ответ сервера: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        if add_response.status_code == 201:
            print("\n✅ Запчасть успешно добавлена!")
            print(f"ID запчасти: {response_json.get('part', {}).get('id')}")
        else:
            print(f"\n❌ Ошибка при добавлении запчасти")
            
    except Exception as e:
        print(f"❌ Ошибка обработки ответа: {e}")
        print(f"Текст ответа: {add_response.text}")

if __name__ == "__main__":
    test_add_part()
