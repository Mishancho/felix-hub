# 🚀 Правильные настройки Start Command для Render

## ⚠️ ВАЖНО
Render может игнорировать `render.yaml` если настройки уже были заданы в Dashboard вручную!

## ✅ Правильная команда запуска

### Вариант 1: Прямая команда (РЕКОМЕНДУЕТСЯ)
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --log-level info --access-logfile - --error-logfile -
```

### Вариант 2: С конфигурационным файлом
```bash
gunicorn -c gunicorn.conf.py app:app
```

## 🔧 Как исправить в Render Dashboard

### Шаг 1: Зайдите в настройки сервиса
1. Откройте [Render Dashboard](https://dashboard.render.com/)
2. Выберите ваш сервис `felix-hub`
3. Перейдите в раздел **Settings**

### Шаг 2: Найдите "Build & Deploy"
Прокрутите до секции **Build & Deploy**

### Шаг 3: Обновите Start Command
Найдите поле **Start Command** и вставьте:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --log-level info --access-logfile - --error-logfile -
```

### Шаг 4: Сохраните изменения
Нажмите **Save Changes** внизу страницы

### Шаг 5: Переразвёртывание
1. Вернитесь в раздел **Manual Deploy**
2. Нажмите **Clear build cache & deploy**

## 📋 Объяснение параметров

| Параметр | Значение | Описание |
|----------|----------|----------|
| `app:app` | - | Flask приложение (модуль:объект) |
| `--bind 0.0.0.0:$PORT` | Обязательно! | Привязка к порту Render |
| `--workers 1` | 1 | Количество worker процессов (для free tier) |
| `--threads 2` | 2 | Количество потоков на worker |
| `--timeout 120` | 120 сек | Таймаут для долгих запросов |
| `--log-level info` | info | Уровень логирования |
| `--access-logfile -` | stdout | Логи доступа в консоль |
| `--error-logfile -` | stderr | Логи ошибок в консоль |

## ✅ Что должно быть в логах после исправления

После правильной настройки вы должны увидеть:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000 (1)
[INFO] Using worker: sync
[INFO] Booting worker with pid: 1
==> Deployed successfully 🎉
```

## 🔍 Проверка

После деплоя проверьте:
- [ ] В логах видно `Listening at: http://0.0.0.0:XXXXX`
- [ ] Сообщение `Deployed successfully 🎉`
- [ ] Приложение доступно по URL
- [ ] Нет ошибок "No open ports detected"

## 🆘 Если не помогло

1. **Очистите build cache**: Settings → Clear build cache & deploy
2. **Проверьте переменные окружения**: Settings → Environment → убедитесь что DATABASE_URL настроена
3. **Проверьте логи**: Events → смотрите полный вывод

## 📸 Скриншот настроек

```
Render Dashboard → felix-hub → Settings

Build & Deploy
┌─────────────────────────────────────────────────┐
│ Build Command                                    │
│ pip install -r requirements.txt && python       │
│ init_render_db.py                               │
├─────────────────────────────────────────────────┤
│ Start Command                                    │
│ gunicorn app:app --bind 0.0.0.0:$PORT          │
│ --workers 1 --threads 2 --timeout 120          │
│ --log-level info --access-logfile -            │
│ --error-logfile -                               │
└─────────────────────────────────────────────────┘

[Save Changes]
```

## 💡 Почему это важно

`$PORT` - это специальная переменная окружения, которую Render устанавливает динамически. Без правильной привязки к ней:
- ❌ Render не может обнаружить, что приложение запущено
- ❌ Health checks не проходят
- ❌ Приложение не доступно извне

С правильной привязкой:
- ✅ Render видит открытый порт
- ✅ Health checks работают
- ✅ Приложение доступно по публичному URL
