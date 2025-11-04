# Исправление ошибки NOT NULL constraint failed: parts.name

## Проблема

При добавлении запчасти в любую категорию возникала ошибка:
```
sqlite3.IntegrityError: NOT NULL constraint failed: parts.name
```

## Причина

В модели `Part` существует два набора полей для имен:
- Новые многоязычные поля: `name_en`, `name_he`, `name_ru`
- Старое поле для обратной совместимости: `name`

При добавлении запчасти через API устанавливались только многоязычные поля, но поле `name` оставалось `NULL`, хотя в схеме базы данных оно было определено как `NOT NULL`.

## Решение

### 1. Обновлен код создания запчасти (`app.py`, функция `create_part`)
Добавлена строка для установки старого поля `name`:
```python
part = Part(
    name_ru=data['name_ru'].strip(),
    name_en=data.get('name_en', '').strip() if data.get('name_en') else None,
    name_he=data.get('name_he', '').strip() if data.get('name_he') else None,
    # ... другие поля ...
    name=data['name_ru'].strip(),  # ← ДОБАВЛЕНО: устанавливаем старое поле
    category=data['category'].strip(),
    # ...
)
```

### 2. Обновлен код обновления запчасти (`app.py`, функция `update_part`)
При обновлении `name_ru` теперь также обновляется `name`:
```python
if 'name_ru' in data:
    # ... проверка на дубликаты ...
    part.name_ru = data['name_ru'].strip()
    part.name = data['name_ru'].strip()  # ← ДОБАВЛЕНО
```

### 3. Обновлен код массового создания запчастей (`app.py`, функция `bulk_create_parts`)
Добавлена поддержка как новых, так и старых форматов данных:
```python
name_ru = item.get('name_ru', item.get('name', '')).strip()

part = Part(
    name_ru=name_ru,
    name_en=item.get('name_en', '').strip() if item.get('name_en') else None,
    name_he=item.get('name_he', '').strip() if item.get('name_he') else None,
    # ... описания ...
    name=name_ru,  # ← ДОБАВЛЕНО
    category=item['category'].strip(),
    # ...
)
```

### 4. Обновлен код импорта дефолтного каталога (`app.py`, функция `import_default_catalog`)
```python
part = Part(
    name_ru=part_name,
    name=part_name,  # ← ДОБАВЛЕНО
    category=category,
    is_active=True,
    sort_order=idx
)
```

### 5. Создана миграция для исправления существующих записей
Файл: `migrations/fix_parts_name_field.py`

Миграция проверяет все записи в таблице `parts` и заполняет поле `name` значением из `name_ru`:
```bash
python migrations/fix_parts_name_field.py
```

## Результат

✅ Запчасти теперь можно добавлять без ошибок
✅ Все существующие записи исправлены миграцией
✅ Обратная совместимость сохранена
✅ Поддержка многоязычности работает корректно

## Тестирование

Создан тестовый скрипт `test_part_direct.py` для проверки:
```bash
python test_part_direct.py
```

Результат теста:
```
✅ Запчасть успешно добавлена! ID: 50
   Название (RU): Прямой тестовый фильтр
   Название (старое поле): Прямой тестовый фильтр
   Категория: Типуль
```

## Файлы, которые были изменены

1. `/Users/mishavorokhovsky/felix-hub-2.1/app.py` - исправлены функции:
   - `create_part()` (строка ~1039)
   - `update_part()` (строка ~1095)
   - `bulk_create_parts()` (строка ~1195)
   - `import_default_catalog()` (строка ~1262)

2. `/Users/mishavorokhovsky/felix-hub-2.1/migrations/fix_parts_name_field.py` - создана миграция

## Дата исправления
4 ноября 2025 г.
