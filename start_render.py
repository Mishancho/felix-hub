#!/usr/bin/env python3
"""
Скрипт запуска Felix Hub на Render
Просто запускает Gunicorn без блокирующих операций
"""

import os
import sys

def main():
    port = os.getenv('PORT', '8000')
    
    print("="*60)
    print(f"🚀 Запуск Felix Hub на порту {port}")
    print("="*60)
    
    # Диагностическая информация
    print(f"📂 CWD: {os.getcwd()}")
    print(f"🐍 PYTHON: {sys.executable}")
    print(f"🔌 PORT: {port}")
    print("="*60)
    
    # Запускаем Gunicorn напрямую
    # БД уже создана через init_render_db.py в buildCommand
    # Миграции выполняются через run_migrations.py после деплоя (если нужно)
    
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'app:app',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--threads', '2',
        '--timeout', '120',
        '--log-level', 'info',
        '--access-logfile', '-',
        '--error-logfile', '-'
    ]
    
    print(f"🚀 Команда: {' '.join(cmd)}")
    print("="*60)
    
    # Запускаем Gunicorn (exec заменяет текущий процесс)
    os.execvp(cmd[0], cmd)

if __name__ == '__main__':
    main()

