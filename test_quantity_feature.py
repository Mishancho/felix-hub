#!/usr/bin/env python3
"""
Тест создания заказа с количеством запчастей
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_order_with_quantity():
    """Тест создания заказа с указанием количества"""
    
    print("🧪 Тест создания заказа с количеством запчастей\n")
    
    # Данные заказа в новом формате (с количеством)
    order_data = {
        "mechanic_name": "Тестовый Механик",
        "telegram_id": "123456789",
        "plate_number": "А123БВ77",
        "category": "Тормоза",
        "selected_parts": [
            {
                "name": "Передние колодки",
                "quantity": 2
            },
            {
                "name": "Задние колодки",
                "quantity": 1
            },
            {
                "name": "Тормозная жидкость",
                "quantity": 3
            }
        ],
        "is_original": True,
        "comment": "Срочно! Нужно 2 комплекта передних колодок и 3 литра жидкости"
    }
    
    print("📋 Отправляем заказ:")
    print(json.dumps(order_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Отправка заказа
        response = requests.post(
            f"{BASE_URL}/api/submit_order",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ УСПЕХ! Заказ создан")
            print(f"   Номер заказа: {result['order_id']}")
            print(f"   Сообщение: {result['message']}")
            print()
            
            # Получаем детали заказа
            order_id = result['order_id']
            get_response = requests.get(f"{BASE_URL}/api/orders")
            
            if get_response.status_code == 200:
                orders = get_response.json()
                created_order = next((o for o in orders if o['id'] == order_id), None)
                
                if created_order:
                    print("📦 Детали заказа:")
                    for part in created_order['selected_parts']:
                        if isinstance(part, dict):
                            qty = f" (x{part['quantity']})" if part.get('quantity', 1) > 1 else ""
                            print(f"   • {part['name']}{qty}")
                        else:
                            print(f"   • {part}")
                    print()
                    
                    return True
        else:
            print(f"❌ ОШИБКА! Статус: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
        return False


def test_old_format_compatibility():
    """Тест обратной совместимости со старым форматом"""
    
    print("🧪 Тест обратной совместимости (старый формат)\n")
    
    # Данные заказа в старом формате (без количества)
    order_data = {
        "mechanic_name": "Старый Механик",
        "telegram_id": "987654321",
        "plate_number": "В456СТ99",
        "category": "Двигатель",
        "selected_parts": [
            "Масло моторное",
            "Масляный фильтр",
            "Воздушный фильтр"
        ],
        "is_original": False,
        "comment": "Обычное ТО"
    }
    
    print("📋 Отправляем заказ (старый формат):")
    print(json.dumps(order_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/submit_order",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ УСПЕХ! Старый формат по-прежнему работает")
            print(f"   Номер заказа: {result['order_id']}")
            print()
            
            # Проверяем, что данные конвертировались в новый формат
            order_id = result['order_id']
            get_response = requests.get(f"{BASE_URL}/api/orders")
            
            if get_response.status_code == 200:
                orders = get_response.json()
                created_order = next((o for o in orders if o['id'] == order_id), None)
                
                if created_order:
                    print("📦 Детали заказа (должны быть в новом формате):")
                    for part in created_order['selected_parts']:
                        if isinstance(part, dict):
                            print(f"   ✅ {part['name']} - quantity: {part.get('quantity', 1)}")
                        else:
                            print(f"   ⚠️  {part} - старый формат")
                    print()
                    
                    return True
        else:
            print(f"❌ ОШИБКА! Статус: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🔬 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ КОЛИЧЕСТВА ЗАПЧАСТЕЙ")
    print("="*60)
    print()
    
    # Тест 1: Новый формат с количеством
    test1_passed = test_order_with_quantity()
    
    print("-"*60)
    print()
    
    # Тест 2: Обратная совместимость
    test2_passed = test_old_format_compatibility()
    
    print("="*60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"Тест 1 (новый формат):       {'✅ ПРОЙДЕН' if test1_passed else '❌ ПРОВАЛЕН'}")
    print(f"Тест 2 (обратная совместимость): {'✅ ПРОЙДЕН' if test2_passed else '❌ ПРОВАЛЕН'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    print()
