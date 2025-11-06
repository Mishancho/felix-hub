# Обновление шаблонов для Cache Busting

## Опциональное обновление

Для максимальной эффективности cache busting можно обновить все шаблоны, заменив `url_for('static', ...)` на `static_url(...)`.

Это НЕ обязательно - ProxyFix уже должен решить основные проблемы. Но для полной уверенности можно сделать это обновление.

## Текущий способ (работает, но может кэшироваться)

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/mobile-responsive.css') }}">
<script src="{{ url_for('static', filename='js/language.js') }}"></script>
```

Генерирует:
```html
<link rel="stylesheet" href="/static/css/mobile-responsive.css">
```

## Новый способ (с версионированием)

```html
<link rel="stylesheet" href="{{ static_url('css/mobile-responsive.css') }}">
<script src="{{ static_url('js/language.js') }}"></script>
```

Генерирует:
```html
<link rel="stylesheet" href="/static/css/mobile-responsive.css?v=1699276800">
```

## Где обновить

### Файлы требующие обновления (опционально):

1. `templates/mechanic/order_form.html`
2. `templates/mechanic/orders.html`
3. `templates/mechanic/dashboard.html`
4. `templates/mechanic/profile.html`
5. `templates/admin/dashboard.html`
6. И другие шаблоны с `<link>` или `<script>` тегами

### Пример обновления

#### Было:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/mobile-responsive.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/language-switcher.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/fixed-header-nav.css') }}">
<script src="{{ url_for('static', filename='js/language.js') }}"></script>
```

#### Стало:
```html
<link rel="stylesheet" href="{{ static_url('css/mobile-responsive.css') }}">
<link rel="stylesheet" href="{{ static_url('css/language-switcher.css') }}">
<link rel="stylesheet" href="{{ static_url('css/fixed-header-nav.css') }}">
<script src="{{ static_url('js/language.js') }}"></script>
```

## Важно!

**Это обновление НЕ обязательно для исправления проблемы с Render.**

ProxyFix уже решает основную проблему. Cache busting - это дополнительная оптимизация для предотвращения проблем с кэшем в будущем.

## Когда это полезно?

1. **После обновления CSS/JS файлов** - пользователи сразу увидят изменения
2. **При частых обновлениях** - не нужно просить пользователей очищать кэш
3. **Для CDN** - если в будущем добавите CDN

## Альтернативный подход

Вместо обновления всех шаблонов можно просто:
1. Попросить пользователей очистить кэш после деплоя
2. Использовать жесткую перезагрузку (Ctrl+Shift+R)
3. Добавить мета-тег в шаблон:
   ```html
   <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
   ```

Но эти методы менее надежны, чем cache busting.
