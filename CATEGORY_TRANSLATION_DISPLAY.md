# Отображение категорий на выбранном языке

## Дата: 4 ноября 2025 г.

## Описание изменений

Реализована полная поддержка отображения категорий запчастей на выбранном языке интерфейса (русский, английский, иврит) во всех частях системы.

## Что было изменено

### 1. Модель Category (models.py)

#### Обновлён метод `to_dict(lang=None)`
```python
def to_dict(self, lang=None):
    """Преобразовать в словарь для API"""
    # Базовые данные со всеми языками
    data = {
        'id': self.id,
        'name': self.name,
        'name_en': self.name_en,
        'name_he': self.name_he,
        'name_ru': self.name_ru,
        # ... другие поля
    }
    
    # Если указан язык, добавляем локализованное имя
    if lang:
        data['name'] = self.get_name(lang)
    
    return data
```

**Преимущества:**
- Всегда возвращает все языки (для админ-панели)
- При указании языка поле `name` содержит переведённое название
- Обратная совместимость сохранена

### 2. Модель Order (models.py)

#### Обновлён метод `to_dict(include_mechanic=False, lang=None)`
```python
def to_dict(self, include_mechanic=False, lang=None):
    """Преобразовать в словарь для API"""
    category_name = self.category
    
    # Если указан язык, пытаемся найти перевод категории
    if lang:
        category_obj = Category.query.filter_by(name=self.category).first()
        if category_obj:
            category_name = category_obj.get_name(lang)
    
    data = {
        # ...
        'category': category_name,  # Переведённое название
        # ...
    }
```

**Что это даёт:**
- Заказы отображаются с переведёнными названиями категорий
- Оригинальное название сохраняется в БД
- Поддержка fallback на оригинальное название

### 3. API Endpoints (app.py)

#### `/api/categories` - Список категорий
```python
@app.route('/api/categories', methods=['GET'])
def get_categories_api():
    lang = request.args.get('lang', 'ru')
    categories = query.order_by(Category.sort_order, Category.name).all()
    return jsonify([cat.to_dict(lang=lang) for cat in categories])
```

**Использование:**
```javascript
fetch('/api/categories?lang=en')
```

#### `/api/parts/categories` - Категории для механиков
```python
@app.route('/api/parts/categories', methods=['GET'])
def get_parts_categories():
    lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
    categories = Category.query.filter_by(is_active=True).order_by(...).all()
    return jsonify([cat.get_name(lang) for cat in categories])
```

**Что возвращает:**
- Массив переведённых названий категорий
- Только активные категории
- Учитывает порядок сортировки

#### `/api/parts/catalog` - Каталог запчастей
```python
@app.route('/api/parts/catalog', methods=['GET'])
def get_parts_catalog():
    lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
    
    # Получаем категории для перевода
    categories = {cat.name: cat for cat in Category.query.all()}
    
    # Группируем по категориям с переводами
    catalog = {}
    for part in parts:
        category_obj = categories.get(part.category)
        if category_obj:
            category_name = category_obj.get_name(lang)
        else:
            category_name = part.category
        
        if category_name not in catalog:
            catalog[category_name] = []
        catalog[category_name].append(part.get_name(lang))
```

**Результат:**
```json
{
  "Brakes": ["Brake Pads", "Brake Discs"],
  "Engine": ["Oil Filter", "Air Filter"]
}
```

#### `/api/mechanic/orders` - Заказы механика
```python
@app.route('/api/mechanic/orders', methods=['GET'])
@mechanic_required
def get_mechanic_orders():
    lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict(lang=lang) for order in orders])
```

### 4. Context Processor (app.py)

Добавлена функция для использования в Jinja2 шаблонах:

```python
@app.context_processor
def inject_category_translator():
    """Добавляем функцию для перевода категорий в шаблоны"""
    def get_category_name(category_name, lang=None):
        """Получить переведённое название категории"""
        if lang is None:
            lang = g.locale if hasattr(g, 'locale') else 'ru'
        
        category = Category.query.filter_by(name=category_name).first()
        if category:
            return category.get_name(lang)
        return category_name
    
    return dict(get_category_name=get_category_name)
```

**Использование в шаблонах:**
```html
{{ get_category_name(order.category) }}
```

### 5. Frontend (JavaScript)

#### parts-manager.js
```javascript
async function loadCategories() {
    const lang = getCurrentLanguage ? getCurrentLanguage() : 'ru';
    const response = await fetch(`/api/categories?lang=${lang}`);
    // ...
}
```

### 6. Templates

#### mechanic/orders.html
```html
<!-- Было -->
{{ order.category }}

<!-- Стало -->
{{ get_category_name(order.category) }}
```

## Поддерживаемые языки

- **ru** - Русский (по умолчанию)
- **en** - English
- **he** - עברית (иврит)

## Где применяется перевод

### ✅ Админ-панель
- Список категорий (таблица)
- Модальное окно редактирования
- Все названия на всех языках доступны

### ✅ Интерфейс механика
- Форма создания заказа (`/mechanic/orders/new`)
  - Выпадающий список категорий
  - Названия запчастей по категориям
- Список заказов (`/mechanic/orders`)
  - Отображение категории в карточке заказа

### ✅ API
- `/api/categories?lang={lang}` - список категорий
- `/api/parts/categories?lang={lang}` - категории для механиков
- `/api/parts/catalog?lang={lang}` - каталог с переводами
- `/api/mechanic/orders?lang={lang}` - заказы с переводами

## Примеры использования

### JavaScript (Frontend)
```javascript
// Получить текущий язык
const lang = getCurrentLanguage(); // 'ru', 'en', или 'he'

// Загрузить категории на нужном языке
const response = await fetch(`/api/categories?lang=${lang}`);
const categories = await response.json();

// Загрузить каталог на нужном языке
const catalog = await fetch(`/api/parts/catalog?lang=${lang}`);
```

### Python (Backend)
```python
# В шаблоне
{{ get_category_name('Тормоза') }}  # Вернёт "Brakes" для en, "בלמים" для he

# В коде
category = Category.query.filter_by(name='Тормоза').first()
name_en = category.get_name('en')  # "Brakes"
name_he = category.get_name('he')  # "בלמים"
name_ru = category.get_name('ru')  # "Тормоза"
```

## Автоматическое определение языка

Система автоматически определяет язык из:
1. **Параметра URL** `?lang=en`
2. **Сессии пользователя** `session['language']`
3. **Настроек механика** `current_user.language`
4. **Accept-Language заголовка** браузера
5. **По умолчанию** - русский

## Fallback стратегия

Если перевод отсутствует:
1. Пытается вернуть русское название (`name_ru`)
2. Если нет - возвращает основное поле (`name`)
3. Если нет - возвращает оригинальную строку

## Тестирование

### Проверка в интерфейсе:
1. Откройте форму заказа: `http://localhost:8000/mechanic/orders/new`
2. Переключите язык на English 🇬🇧
3. Категории должны отображаться на английском
4. Переключите на עברית 🇮🇱
5. Категории должны отображаться на иврите

### Проверка через API:
```bash
# Русский
curl "http://localhost:8000/api/categories?lang=ru"

# Английский
curl "http://localhost:8000/api/categories?lang=en"

# Иврит
curl "http://localhost:8000/api/categories?lang=he"
```

## Производительность

**Оптимизации:**
- Категории кэшируются при загрузке каталога
- Используется один запрос для получения всех категорий
- Перевод выполняется на уровне модели (in-memory)

**Рекомендации:**
- Для больших каталогов рассмотреть кэширование на уровне Redis
- Использовать eager loading для связанных данных

## Обратная совместимость

✅ Все существующие API работают без изменений  
✅ Если `lang` не указан, возвращаются данные на русском  
✅ Старые клиенты продолжают работать  
✅ База данных не требует миграций (поля уже существуют)

## Связанные файлы

- `models.py` - модели Category и Order
- `app.py` - API endpoints и context processor
- `static/js/parts-manager.js` - управление категориями в админке
- `templates/mechanic/order_form.html` - форма заказа
- `templates/mechanic/orders.html` - список заказов
- `migrations/add_category_translations.py` - миграция (уже выполнена)

## Следующие шаги

Рекомендуется:
1. ✅ Заполнить переводы для всех существующих категорий
2. ✅ Протестировать на всех языках
3. 📝 Обновить документацию API
4. 🔄 Настроить автоматическую синхронизацию переводов

---

**Автор:** GitHub Copilot  
**Дата:** 4 ноября 2025 г.
