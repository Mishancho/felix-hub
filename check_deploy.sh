#!/bin/bash

echo "🔍 Проверка статуса деплоя Felix Hub на Render"
echo "=============================================="
echo ""

echo "📊 Коммиты отправлены:"
git log --oneline -3

echo ""
echo "🌐 Проверка доступности приложения..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://felix-hub.onrender.com)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Приложение доступно (HTTP $HTTP_STATUS)"
else
    echo "⏳ Приложение недоступно или деплоится (HTTP $HTTP_STATUS)"
fi

echo ""
echo "📝 Следующие шаги:"
echo "1. Откройте Render Dashboard: https://dashboard.render.com"
echo "2. Выберите сервис 'felix-hub'"
echo "3. Перейдите на вкладку 'Events' для мониторинга деплоя"
echo "4. Проверьте 'Logs' на наличие сообщения '✅ Таблицы созданы'"
echo ""
echo "🔗 Полезные ссылки:"
echo "   • Приложение: https://felix-hub.onrender.com"
echo "   • Админ-панель: https://felix-hub.onrender.com/admin/login"
echo "   • Dashboard: https://dashboard.render.com"
