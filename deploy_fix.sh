#!/bin/bash

# ===================================================================
# СКРИПТ БЫСТРОГО ДЕПЛОЯ НА RENDER
# Использование: bash deploy_fix.sh
# ===================================================================

echo "=========================================="
echo "🚀 Felix Hub - Деплой исправлений на Render"
echo "=========================================="
echo ""

# Проверка что мы в правильной директории
if [ ! -f "app.py" ]; then
    echo "❌ Ошибка: файл app.py не найден!"
    echo "   Убедитесь что вы в директории felix-hub-2.1"
    exit 1
fi

# Показываем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Текущая ветка: $CURRENT_BRANCH"
echo ""

# Проверяем статус git
echo "🔍 Проверка изменений..."
git status --short
echo ""

# Показываем измененные файлы
echo "📝 Файлы для коммита:"
echo "   - app.py (ProxyFix + Cache Busting)"
echo "   - RENDER_DISPLAY_FIX.md (полная документация)"
echo "   - QUICK_FIX_RENDER_DISPLAY.md (краткое руководство)"
echo "   - RENDER_FIX_SUMMARY.md (резюме)"
echo "   - diagnose_render.py (диагностика)"
echo "   - UPDATE_TEMPLATES_CACHE_BUSTING.md (опциональное)"
echo "   - deploy_fix.sh (этот скрипт)"
echo ""

# Запрос подтверждения
read -p "❓ Продолжить коммит и деплой? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Деплой отменён"
    exit 0
fi

echo ""
echo "📦 Добавление файлов в git..."
git add app.py \
        RENDER_DISPLAY_FIX.md \
        QUICK_FIX_RENDER_DISPLAY.md \
        RENDER_FIX_SUMMARY.md \
        diagnose_render.py \
        UPDATE_TEMPLATES_CACHE_BUSTING.md \
        deploy_fix.sh

echo "✅ Файлы добавлены"
echo ""

echo "💾 Создание коммита..."
git commit -m "fix: Add ProxyFix middleware and cache busting for Render deployment

- Add ProxyFix to handle nginx reverse proxy correctly
- Configure static file caching for production
- Add cache busting for automatic version management
- Add diagnostic script for troubleshooting
- Add comprehensive documentation

Fixes: Issue with incorrect display on Render production
Testing: Verified with diagnose_render.py script"

if [ $? -eq 0 ]; then
    echo "✅ Коммит создан"
else
    echo "❌ Ошибка при создании коммита"
    exit 1
fi

echo ""
echo "🚀 Отправка на GitHub..."
git push origin $CURRENT_BRANCH

if [ $? -eq 0 ]; then
    echo "✅ Изменения отправлены на GitHub"
else
    echo "❌ Ошибка при отправке на GitHub"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ ДЕПЛОЙ ИНИЦИИРОВАН"
echo "=========================================="
echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1. 🌐 Откройте Render Dashboard:"
echo "   https://dashboard.render.com"
echo ""
echo "2. 🔍 Найдите сервис 'felix-hub'"
echo ""
echo "3. ⏳ Дождитесь статуса 'Live' (2-5 минут)"
echo ""
echo "4. 🧹 Очистите кэш браузера:"
echo "   - Chrome/Edge: Ctrl+Shift+Delete"
echo "   - Safari: Cmd+Option+E"
echo "   - Firefox: Ctrl+Shift+Delete"
echo ""
echo "5. 🔄 Жесткая перезагрузка страницы:"
echo "   - Windows: Ctrl+Shift+R"
echo "   - Mac: Cmd+Shift+R"
echo ""
echo "6. ✅ Проверьте сайт:"
echo "   https://felix-hub.onrender.com"
echo ""
echo "=========================================="
echo "📖 Документация:"
echo "   - RENDER_FIX_SUMMARY.md (начните отсюда)"
echo "   - RENDER_DISPLAY_FIX.md (полное руководство)"
echo "   - QUICK_FIX_RENDER_DISPLAY.md (быстрый старт)"
echo ""
echo "🔧 Диагностика:"
echo "   python3 diagnose_render.py"
echo ""
echo "=========================================="
echo "🎉 Готово!"
echo "=========================================="
