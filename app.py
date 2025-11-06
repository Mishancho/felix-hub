import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, g
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext, lazy_gettext as _l
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
from migrate_parts_translations import find_translation

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Настройки Babel для многоязычности
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['LANGUAGES'] = {
    'en': 'English',
    'he': 'עברית',
    'ru': 'Русский'
}

# Создаем экземпляр Babel (инициализация позже)
babel = Babel()

# Исправление DATABASE_URL для PostgreSQL (Render использует postgres://, SQLAlchemy требует postgresql://)
database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/felix_hub.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Режим обратной совместимости (анонимные заказы)
app.config['ALLOW_ANONYMOUS_ORDERS'] = os.getenv('ALLOW_ANONYMOUS_ORDERS', 'true').lower() == 'true'

# Создание папки для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Импорт моделей и авторизации
from models import db, Mechanic, Order, Part, Category
from auth import login_manager, admin_required, mechanic_required, should_notify_mechanic

# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)

# Функция для определения языка пользователя
def get_locale():
    """Определить текущий язык интерфейса"""
    # 1. Проверяем параметр URL
    lang = request.args.get('lang')
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        return lang
    
    # 2. Проверяем сессию
    if 'language' in session:
        return session.get('language')
    
    # 3. Проверяем язык механика (если авторизован)
    if current_user.is_authenticated and hasattr(current_user, 'language'):
        return current_user.language
    
    # 4. Определяем по заголовкам браузера
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

# Регистрируем функцию определения локали
babel.init_app(app, locale_selector=get_locale)

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

@app.before_request
def before_request():
    """Выполняется перед каждым запросом"""
    g.locale = get_locale()
    
    # Определяем направление текста (RTL для иврита)
    g.text_direction = 'rtl' if g.locale == 'he' else 'ltr'

# Маршрут для смены языка
@app.route('/set_language/<lang>', methods=['GET', 'POST'])
def set_language(lang):
    """Установить язык интерфейса"""
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        
        # Если механик авторизован, сохраняем его предпочтение
        if current_user.is_authenticated and hasattr(current_user, 'language'):
            current_user.language = lang
            db.session.commit()
        
        # Если есть параметр redirect, перенаправляем туда
        redirect_url = request.args.get('redirect')
        if redirect_url:
            return redirect(redirect_url)
        
        # Для AJAX запросов возвращаем JSON
        if request.is_json or request.method == 'POST':
            return jsonify({'success': True, 'language': lang})
        
        # По умолчанию редирект на главную
        return redirect(request.referrer or url_for('index'))
    
    return jsonify({'success': False, 'error': 'Unsupported language'}), 400

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# Справочник категорий и запчастей
PARTS_CATALOG = {
    'Лампочки': [
        'Лампа, один контакт',
        'Лампа, два контакта',
        'Лампа без корпуса (без патрона)',
        'Лампа H7',
        'Лампа H4',
        'Лампа H1',
        'Лампа «банан» (фестон)',
        'Лампа средняя (типоразмер средний)',
        'Лампа с корпусом (с патроном)'
    ],
    'типуль': [
        'Тормозная жидкость',
        'Спрей для тормозов (очиститель)',
        'Пробка поддона двигателя (сливной болт)',
        'Присадка для омывателя стёкол',
        'Масло (двигателя)',
        'Фильтр масляный',
        'Фильтр воздушный',
        'Фильтр кондиционера (салонный)',
        'Фильтр топливный (бензин)',
        'Фильтр дизельный (солярки)',
        'Свечи зажигания',
        'Ремень ГРМ',
        'Натяжитель ремня ГРМ',
        'Ремень генератора'
    ],
    'жидкости\\масла\\': [
        'Масло для заднего моста',
        'Масло для МКПП',
        'Масло для АКПП',
        'Жидкость ГУР (рулевого управления)',
        'Очиститель нагара/декарбонизатор',
        'Вода дистиллированная',
        'G13'
    ],
    'тормоза': [
        'Передние тормозные колодки',
        'Задние тормозные колодки',
        'Тормозной диск (ротора) передний',
        'Тормозной диск (ротора) задний',
        'Датчик/провод износа колодок передний',
        'Датчик/провод износа колодок задний'
    ],
    'типуль\\кузов': [
        'Щётки стеклоочистителя перед',
        'Щётки стеклоочистителя зад'
    ]
}

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПЕРЕВОДАМИ
# ============================================================================

def apply_auto_translations(part, part_name_ru):
    """
    Автоматически применить переводы к запчасти, если они не указаны.
    
    Args:
        part: Объект Part
        part_name_ru: Название запчасти на русском языке
    
    Returns:
        bool: True если переводы были применены, False в противном случае
    """
    if not part.name_en or not part.name_he:
        translation = find_translation(part_name_ru)
        if translation:
            if not part.name_en:
                part.name_en = translation.get('en')
            if not part.name_he:
                part.name_he = translation.get('he')
            
            app.logger.info(
                f"✅ Автоматически добавлен перевод для '{part_name_ru}': "
                f"EN='{part.name_en}', HE='{part.name_he}'"
            )
            return True
    return False

# ============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С TELEGRAM
# ============================================================================

# Функции для работы с Telegram
def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram bot token не настроен")
        return False
    
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

def notify_admin_new_order(order):
    """Уведомление администратору о новом заказе"""
    if not TELEGRAM_ADMIN_CHAT_ID:
        return
    
    # Формируем список деталей с количеством на русском языке
    parts_list = []
    for part in order.selected_parts:
        if isinstance(part, dict):
            # Новый формат с количеством и опционально part_id
            part_id = part.get('part_id')
            quantity = part.get('quantity', 1)
            
            # Если есть part_id, получаем название на русском
            if part_id:
                part_obj = Part.query.get(part_id)
                name = part_obj.get_name('ru') if part_obj else part.get('name', '')
            else:
                name = part.get('name', '')
            
            if quantity > 1:
                parts_list.append(f"• {name} <b>(x{quantity})</b>")
            else:
                parts_list.append(f"• {name}")
        else:
            # Старый формат (просто строка)
            parts_list.append(f"• {part}")
    
    parts_text = '\n'.join(parts_list)
    
    # Получаем переведенное название категории на русском
    category_name = order.category
    category_obj = Category.query.filter_by(name=order.category).first()
    if category_obj:
        category_name = category_obj.get_name('ru')
    
    message = f"""🔔 <b>Новый заказ от {order.mechanic_name}</b>

📋 Заказ №{order.id}
🚗 Гос номер: <b>{order.plate_number}</b>
📦 Категория: {category_name}

<b>Детали:</b>
{parts_text}

{'🔧 Оригинал' if order.is_original else '💰 Аналог'}
⏰ {order.created_at.strftime('%d.%m.%Y %H:%M')}
"""
    
    if order.comment:
        message += f"\n💬 Комментарий: {order.comment}"
    
    send_telegram_message(TELEGRAM_ADMIN_CHAT_ID, message)

def notify_mechanic_order_ready(order):
    """Уведомление механику о готовности заказа"""
    # Проверяем настройки уведомлений через auth.py
    if not should_notify_mechanic(order, 'ready'):
        return
    
    # Используем telegram_id механика или из заказа (для старых заказов)
    telegram_id = order.mechanic.telegram_id if order.mechanic else order.telegram_id
    
    if not telegram_id:
        return
    
    message = f"""✅ <b>Заказ №{order.id} готов!</b>

🚗 Авто: <b>{order.plate_number}</b>
📦 Категория: {order.category}

Забери детали у кладовщика 📦"""
    
    send_telegram_message(telegram_id, message)

def validate_plate_number(plate_number):
    """Валидация формата гос номера"""
    # Примеры допустимых форматов: 123-45-678, A123BC77, В456СТ199
    if not plate_number or len(plate_number) < 5:
        return False
    
    # Убираем пробелы и приводим к верхнему регистру
    plate_number = plate_number.strip().upper()
    
    # Базовая проверка: есть буквы или цифры
    if not re.search(r'[A-ZА-Я0-9]', plate_number):
        return False
    
    return True

def print_receipt(order):
    """Печать чека (симуляция - можно заменить на реальную печать)"""
    # Получаем переведенное название категории на русском
    category_name = order.category
    category_obj = Category.query.filter_by(name=order.category).first()
    if category_obj:
        category_name = category_obj.get_name('ru')
    
    receipt = f"""
{'='*40}
СТО Felix
{'='*40}
Заказ №{order.id}
Механик: {order.mechanic_name}
Гос номер: {order.plate_number}
Категория: {category_name}
{'='*40}
Детали:
"""
    # Выводим детали на русском языке
    for part in order.selected_parts:
        if isinstance(part, dict):
            # Новый формат с количеством и опционально part_id
            part_id = part.get('part_id')
            quantity = part.get('quantity', 1)
            
            # Если есть part_id, получаем название на русском
            if part_id:
                part_obj = Part.query.get(part_id)
                name = part_obj.get_name('ru') if part_obj else part.get('name', '')
            else:
                name = part.get('name', '')
            
            if quantity > 1:
                receipt += f"- {name} (x{quantity})\n"
            else:
                receipt += f"- {name}\n"
        else:
            # Старый формат (просто строка)
            receipt += f"- {part}\n"
    
    receipt += f"""{'='*40}
Статус: {order.status}
Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}
{'='*40}
"""
    
    print(receipt)  # В продакшене здесь будет вызов принтера
    return receipt

# Маршруты приложения

@app.route('/health')
def health():
    """Health check endpoint для Render"""
    return 'OK', 200

@app.route('/admin/run-migrations-manually')
@login_required
def run_migrations_manually():
    """Ручной запуск миграций БД (только для админов)"""
    if not current_user.is_authenticated or current_user.username != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Импортируем функцию миграций
        from init_render_db import run_migrations
        
        # Запускаем миграции
        run_migrations()
        
        return jsonify({
            'success': True,
            'message': 'Миграции успешно выполнены!'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """Главная страница - выбор языка"""
    return render_template('index.html')

@app.route('/mechanic')
def mechanic():
    """Интерфейс механика - перенаправление на вход или dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('mechanic_dashboard'))
    
    # Если разрешены анонимные заказы, показываем старую форму
    if app.config['ALLOW_ANONYMOUS_ORDERS']:
        lang = request.args.get('lang', 'ru')
        return render_template('mechanic.html', catalog=PARTS_CATALOG, lang=lang)
    
    # Иначе перенаправляем на вход
    return redirect(url_for('mechanic_login'))


# ============================================================================
# НОВЫЕ МАРШРУТЫ ДЛЯ СИСТЕМЫ АВТОРИЗАЦИИ МЕХАНИКОВ (v2.2)
# ============================================================================

@app.route('/mechanic/login', methods=['GET', 'POST'])
def mechanic_login():
    """Вход механика в систему"""
    # Если уже авторизован, перенаправляем в dashboard
    if current_user.is_authenticated:
        return redirect(url_for('mechanic_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        mechanic = Mechanic.query.filter_by(username=username).first()
        
        if mechanic and mechanic.check_password(password):
            if not mechanic.is_active:
                flash('Ваш аккаунт деактивирован. Обратитесь к администратору', 'error')
                return redirect(url_for('mechanic_login'))
            
            login_user(mechanic, remember=remember)
            mechanic.update_last_login()
            
            flash(f'Добро пожаловать, {mechanic.full_name}!', 'success')
            
            # Перенаправление на запрошенную страницу или на dashboard
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('mechanic_dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('mechanic/login.html')


@app.route('/mechanic/logout')
@login_required
def mechanic_logout():
    """Выход механика"""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('mechanic_login'))


@app.route('/mechanic/dashboard')
@mechanic_required
def mechanic_dashboard():
    """Личный кабинет механика"""
    stats = current_user.get_order_stats()
    
    # Последние 5 заказов
    recent_orders = Order.query.filter_by(mechanic_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .limit(5)\
        .all()
    
    return render_template('mechanic/dashboard.html', 
                         stats=stats, 
                         recent_orders=recent_orders)


@app.route('/mechanic/orders')
@mechanic_required
def mechanic_orders():
    """Список заказов механика"""
    status = request.args.get('status', 'все')
    plate_number = request.args.get('plate_number', '')
    
    query = Order.query.filter_by(mechanic_id=current_user.id)
    
    if status and status != 'все':
        query = query.filter_by(status=status)
    
    if plate_number:
        query = query.filter(Order.plate_number.ilike(f'%{plate_number}%'))
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return render_template('mechanic/orders.html', orders=orders)


@app.route('/mechanic/orders/new')
@mechanic_required
def mechanic_new_order():
    """Форма создания нового заказа"""
    return render_template('mechanic/order_form.html')


@app.route('/mechanic/profile')
@mechanic_required
def mechanic_profile():
    """Профиль механика"""
    return render_template('mechanic/profile.html')


@app.route('/mechanic/settings')
@mechanic_required
def mechanic_settings():
    """Настройки механика"""
    return render_template('mechanic/settings.html')

@app.route('/api/submit_order', methods=['POST'])
def submit_order():
    """API для создания нового заказа"""
    try:
        data = request.get_json()
        
        # Определяем, создается ли заказ авторизованным механиком
        if current_user.is_authenticated:
            # Заказ от авторизованного механика
            mechanic_id = current_user.id
            mechanic_name = current_user.full_name
            telegram_id = current_user.telegram_id
        else:
            # Анонимный заказ (обратная совместимость)
            if not app.config['ALLOW_ANONYMOUS_ORDERS']:
                return jsonify({'error': 'Требуется авторизация'}), 401
            
            mechanic_id = None
            mechanic_name = data.get('mechanic_name')
            telegram_id = data.get('telegram_id')
            
            if not mechanic_name:
                return jsonify({'error': 'Имя механика обязательно'}), 400
        
        # Валидация обязательных полей
        if not data.get('plate_number'):
            return jsonify({'error': 'Гос номер обязателен'}), 400
        
        if not validate_plate_number(data['plate_number']):
            return jsonify({'error': 'Неверный формат гос номера'}), 400
        
        if not data.get('category'):
            return jsonify({'error': 'Категория обязательна'}), 400
        
        if not data.get('selected_parts') or len(data['selected_parts']) == 0:
            return jsonify({'error': 'Выберите хотя бы одну деталь'}), 400
        
        # Нормализация формата selected_parts
        # Поддерживаем как старый формат (массив строк), так и новый (массив объектов с количеством и part_id)
        selected_parts = data['selected_parts']
        normalized_parts = []
        
        for part in selected_parts:
            if isinstance(part, str):
                # Старый формат: просто строка (для обратной совместимости)
                normalized_parts.append({
                    'name': part,
                    'quantity': 1
                })
            elif isinstance(part, dict):
                # Новый формат: объект с name, quantity и опционально part_id
                part_entry = {
                    'name': part.get('name', ''),
                    'quantity': int(part.get('quantity', 1))
                }
                
                # Если передан part_id, сохраняем его для последующего перевода
                if 'part_id' in part:
                    part_entry['part_id'] = part['part_id']
                
                normalized_parts.append(part_entry)
        
        # Создание нового заказа
        order = Order(
            mechanic_id=mechanic_id,
            mechanic_name=mechanic_name,
            telegram_id=telegram_id,
            category=data['category'],
            plate_number=data['plate_number'].strip().upper(),
            selected_parts=normalized_parts,  # Сохраняем в новом формате
            is_original=data.get('is_original', False),
            photo_url=data.get('photo_url'),
            comment=data.get('comment'),
            status='новый'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Отправка уведомления администратору
        notify_admin_new_order(order)
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'message': 'Заказ успешно создан'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка создания заказа: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
@admin_required
def admin():
    """Панель администратора"""
    return render_template('admin.html')

@app.route('/admin/mechanics')
@admin_required
def admin_mechanics():
    """Панель управления механиками"""
    return render_template('admin/mechanics.html')

@app.route('/admin/parts')
@admin_required
def admin_parts():
    """Панель управления запчастями"""
    return render_template('admin/parts.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Вход администратора"""
    if request.method == 'POST':
        # Простая проверка (в продакшене использовать хеши паролей)
        if request.form.get('password') == 'felix2025':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='Неверный пароль')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Выход администратора"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/api/orders')
def get_orders():
    """API для получения списка заказов"""
    try:
        # Фильтрация
        status = request.args.get('status')
        plate_number = request.args.get('plate_number')
        mechanic = request.args.get('mechanic')
        
        query = Order.query
        
        if status and status != 'все':
            query = query.filter_by(status=status)
        
        if plate_number:
            query = query.filter(Order.plate_number.ilike(f'%{plate_number}%'))
        
        if mechanic:
            query = query.filter(Order.mechanic_name.ilike(f'%{mechanic}%'))
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Админ всегда получает данные на русском языке
        return jsonify([order.to_dict(lang='ru') for order in orders])
    except Exception as e:
        error_msg = str(e)
        
        # Специальная обработка ошибок БД
        if 'does not exist' in error_msg:
            error_msg = 'База данных не инициализирована. Выполните: python init_render_db.py'
        
        print(f"❌ Ошибка получения заказов: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': error_msg,
            'details': 'Проверьте логи сервера для подробностей'
        }), 500

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """API для обновления заказа"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        old_status = order.status
        new_status = data.get('status')
        
        if new_status:
            order.status = new_status
        
        if 'printed' in data:
            order.printed = data['printed']
        
        db.session.commit()
        
        # Если статус изменён на "готово", отправить уведомление механику
        if old_status != 'готово' and new_status == 'готово':
            notify_mechanic_order_ready(order)
            
            # Автоматическая печать чека
            if not order.printed:
                print_receipt(order)
                order.printed = True
                db.session.commit()
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/print', methods=['POST'])
def print_order(order_id):
    """API для печати чека"""
    try:
        order = Order.query.get_or_404(order_id)
        receipt = print_receipt(order)
        
        order.printed = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'receipt': receipt
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """API для удаления заказа"""
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ДЛЯ ЛИЧНОГО КАБИНЕТА МЕХАНИКА (v2.2)
# ============================================================================

@app.route('/api/mechanic/profile', methods=['GET'])
@mechanic_required
def get_mechanic_profile():
    """Получить профиль текущего механика"""
    return jsonify(current_user.to_dict(include_stats=True))


@app.route('/api/mechanic/profile', methods=['PUT'])
@mechanic_required
def update_mechanic_profile():
    """Обновить профиль механика"""
    try:
        data = request.get_json()
        
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        
        if 'telegram_id' in data:
            current_user.telegram_id = data['telegram_id']
        
        if 'phone' in data:
            current_user.phone = data['phone']
        
        if 'email' in data:
            current_user.email = data['email']
        
        if 'language' in data:
            current_user.language = data['language']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile': current_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/mechanic/password', methods=['PUT'])
@mechanic_required
def update_mechanic_password():
    """Сменить пароль механика"""
    try:
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Требуются оба пароля'}), 400
        
        if not current_user.check_password(old_password):
            return jsonify({'error': 'Неверный текущий пароль'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Пароль должен быть не менее 6 символов'}), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Пароль успешно изменен'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/mechanic/settings', methods=['PUT'])
@mechanic_required
def update_mechanic_settings():
    """Обновить настройки уведомлений механика"""
    try:
        data = request.get_json()
        
        if 'notify_on_ready' in data:
            current_user.notify_on_ready = data['notify_on_ready']
        
        if 'notify_on_processing' in data:
            current_user.notify_on_processing = data['notify_on_processing']
        
        if 'notify_on_cancelled' in data:
            current_user.notify_on_cancelled = data['notify_on_cancelled']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'settings': {
                'notify_on_ready': current_user.notify_on_ready,
                'notify_on_processing': current_user.notify_on_processing,
                'notify_on_cancelled': current_user.notify_on_cancelled
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/mechanic/orders', methods=['GET'])
@mechanic_required
def get_mechanic_orders():
    """Получить заказы текущего механика"""
    status = request.args.get('status')
    plate_number = request.args.get('plate_number')
    lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
    
    query = Order.query.filter_by(mechanic_id=current_user.id)
    
    if status and status != 'все':
        query = query.filter_by(status=status)
    
    if plate_number:
        query = query.filter(Order.plate_number.ilike(f'%{plate_number}%'))
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return jsonify([order.to_dict(lang=lang) for order in orders])


@app.route('/api/mechanic/stats', methods=['GET'])
@mechanic_required
def get_mechanic_stats():
    """Получить статистику механика"""
    return jsonify(current_user.get_order_stats())


# ============================================================================
# API ДЛЯ АДМИНА: УПРАВЛЕНИЕ МЕХАНИКАМИ (v2.2)
# ============================================================================

@app.route('/api/admin/mechanics', methods=['GET'])
@admin_required
def get_mechanics():
    """Получить список всех механиков"""
    try:
        mechanics = Mechanic.query.order_by(Mechanic.created_at.desc()).all()
        return jsonify([m.to_dict(include_stats=True) for m in mechanics])
    except Exception as e:
        error_msg = str(e)
        
        # Специальная обработка ошибок БД
        if 'does not exist' in error_msg:
            error_msg = 'База данных не инициализирована. Выполните: python init_render_db.py'
        
        print(f"❌ Ошибка получения механиков: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': error_msg,
            'details': 'Проверьте логи сервера для подробностей'
        }), 500


@app.route('/api/admin/mechanics', methods=['POST'])
@admin_required
def create_mechanic():
    """Создать нового механика"""
    try:
        data = request.get_json()
        
        # Валидация
        if not data.get('username'):
            return jsonify({'error': 'Username обязателен'}), 400
        
        if not data.get('full_name'):
            return jsonify({'error': 'Полное имя обязательно'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'Пароль обязателен'}), 400
        
        # Проверка уникальности username
        if Mechanic.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username уже занят'}), 400
        
        # Проверка уникальности telegram_id
        if data.get('telegram_id'):
            if Mechanic.query.filter_by(telegram_id=data['telegram_id']).first():
                return jsonify({'error': 'Telegram ID уже используется'}), 400
        
        # Создание механика
        mechanic = Mechanic(
            username=data['username'],
            full_name=data['full_name'],
            telegram_id=data.get('telegram_id'),
            phone=data.get('phone'),
            email=data.get('email'),
            is_active=data.get('is_active', True),
            notify_on_ready=data.get('notify_on_ready', True),
            notify_on_processing=data.get('notify_on_processing', False),
            notify_on_cancelled=data.get('notify_on_cancelled', False),
            language=data.get('language', 'ru')
        )
        
        mechanic.set_password(data['password'])
        
        db.session.add(mechanic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mechanic': mechanic.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Специальная обработка ошибок БД
        if 'does not exist' in error_msg:
            error_msg = 'База данных не инициализирована. Выполните: python init_render_db.py'
        
        print(f"❌ Ошибка создания механика: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': error_msg,
            'details': 'Проверьте логи сервера для подробностей'
        }), 500


@app.route('/api/admin/mechanics/<int:mechanic_id>', methods=['GET'])
@admin_required
def get_mechanic(mechanic_id):
    """Получить данные механика"""
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return jsonify(mechanic.to_dict(include_stats=True))


@app.route('/api/admin/mechanics/<int:mechanic_id>', methods=['PUT'])
@admin_required
def update_mechanic(mechanic_id):
    """Обновить данные механика"""
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        data = request.get_json()
        
        if 'username' in data and data['username'] != mechanic.username:
            if Mechanic.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username уже занят'}), 400
            mechanic.username = data['username']
        
        if 'full_name' in data:
            mechanic.full_name = data['full_name']
        
        if 'telegram_id' in data:
            if data['telegram_id'] != mechanic.telegram_id:
                if Mechanic.query.filter_by(telegram_id=data['telegram_id']).first():
                    return jsonify({'error': 'Telegram ID уже используется'}), 400
            mechanic.telegram_id = data['telegram_id']
        
        if 'phone' in data:
            mechanic.phone = data['phone']
        
        if 'email' in data:
            mechanic.email = data['email']
        
        if 'is_active' in data:
            mechanic.is_active = data['is_active']
        
        if 'notify_on_ready' in data:
            mechanic.notify_on_ready = data['notify_on_ready']
        
        if 'notify_on_processing' in data:
            mechanic.notify_on_processing = data['notify_on_processing']
        
        if 'notify_on_cancelled' in data:
            mechanic.notify_on_cancelled = data['notify_on_cancelled']
        
        if 'language' in data:
            mechanic.language = data['language']
        
        if 'password' in data and data['password']:
            mechanic.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mechanic': mechanic.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/mechanics/<int:mechanic_id>', methods=['DELETE'])
@admin_required
def delete_mechanic(mechanic_id):
    """Удалить механика"""
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        # Проверяем, есть ли у механика заказы
        orders_count = Order.query.filter_by(mechanic_id=mechanic_id).count()
        if orders_count > 0:
            return jsonify({
                'error': f'Невозможно удалить механика с заказами ({orders_count}). Сначала деактивируйте его.'
            }), 400
        
        db.session.delete(mechanic)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/mechanics/<int:mechanic_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_mechanic_active(mechanic_id):
    """Активировать/деактивировать механика"""
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        mechanic.is_active = not mechanic.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': mechanic.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ДЛЯ УПРАВЛЕНИЯ СПРАВОЧНИКОМ ЗАПЧАСТЕЙ
# ============================================================================

@app.route('/api/parts', methods=['GET'])
def get_parts():
    """Получить список всех запчастей (доступно всем)"""
    try:
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
        
        query = Part.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        parts = query.order_by(Part.category, Part.sort_order, Part.name_ru).all()
        
        return jsonify([part.to_dict(lang=lang) for part in parts])
        
    except Exception as e:
        print(f"❌ Ошибка получения запчастей: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/parts/categories', methods=['GET'])
def get_parts_categories():
    """Получить список всех категорий с переводами"""
    try:
        lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
        
        # Получаем категории из таблицы Category
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order, Category.name).all()
        
        if categories:
            # Возвращаем список с переведёнными названиями
            return jsonify([cat.get_name(lang) for cat in categories])
        
        # Если категорий нет в таблице, получаем уникальные категории из запчастей
        parts_categories = db.session.query(Part.category).distinct().order_by(Part.category).all()
        parts_categories = [cat[0] for cat in parts_categories]
        
        return jsonify(parts_categories)
        
    except Exception as e:
        print(f"❌ Ошибка получения категорий: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/parts/catalog', methods=['GET'])
def get_parts_catalog():
    """Получить весь каталог в формате {категория: [запчасти с ID]}"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        lang = request.args.get('lang', g.locale if hasattr(g, 'locale') else 'ru')
        
        query = Part.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        parts = query.order_by(Part.category, Part.sort_order, Part.name_ru).all()
        
        # Получаем категории для перевода
        categories = {cat.name: cat for cat in Category.query.all()}
        
        # Группируем по категориям с переводами и ID
        catalog = {}
        for part in parts:
            # Получаем переведённое название категории
            category_obj = categories.get(part.category)
            if category_obj:
                category_name = category_obj.get_name(lang)
            else:
                category_name = part.category  # Fallback на оригинальное название
            
            if category_name not in catalog:
                catalog[category_name] = []
            
            # Добавляем запчасть с ID и переведённым названием
            catalog[category_name].append({
                'id': part.id,
                'name': part.get_name(lang)
            })
        
        return jsonify(catalog)
        
    except Exception as e:
        print(f"❌ Ошибка получения каталога: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts', methods=['POST'])
@admin_required
def create_part():
    """Создать новую запчасть"""
    try:
        data = request.get_json()
        
        # Валидация - хотя бы русское название обязательно
        if not data.get('name_ru'):
            return jsonify({'error': 'Название на русском обязательно'}), 400
        
        if not data.get('category'):
            return jsonify({'error': 'Категория обязательна'}), 400
        
        # Создание запчасти (разрешаем дубликаты)
        part = Part(
            name_ru=data['name_ru'].strip(),
            name_en=data.get('name_en', '').strip() if data.get('name_en') else None,
            name_he=data.get('name_he', '').strip() if data.get('name_he') else None,
            description_ru=data.get('description_ru', '').strip() if data.get('description_ru') else None,
            description_en=data.get('description_en', '').strip() if data.get('description_en') else None,
            description_he=data.get('description_he', '').strip() if data.get('description_he') else None,
            name=data['name_ru'].strip(),  # Устанавливаем старое поле для обратной совместимости
            category=data['category'].strip(),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        # Автоматически добавляем переводы, если их нет
        apply_auto_translations(part, data['name_ru'])
        
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'part': part.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка создания запчасти: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts/<int:part_id>', methods=['GET'])
@admin_required
def get_part(part_id):
    """Получить данные запчасти"""
    part = Part.query.get_or_404(part_id)
    return jsonify(part.to_dict())


@app.route('/api/admin/parts/<int:part_id>', methods=['PUT'])
@admin_required
def update_part(part_id):
    """Обновить запчасть"""
    try:
        part = Part.query.get_or_404(part_id)
        data = request.get_json()
        
        if 'name_ru' in data:
            part.name_ru = data['name_ru'].strip()
            part.name = data['name_ru'].strip()  # Обновляем старое поле для обратной совместимости
        
        if 'name_en' in data:
            part.name_en = data['name_en'].strip() if data['name_en'] else None
        
        if 'name_he' in data:
            part.name_he = data['name_he'].strip() if data['name_he'] else None
        
        if 'description_ru' in data:
            part.description_ru = data['description_ru'].strip() if data['description_ru'] else None
        
        if 'description_en' in data:
            part.description_en = data['description_en'].strip() if data['description_en'] else None
        
        if 'description_he' in data:
            part.description_he = data['description_he'].strip() if data['description_he'] else None
        
        if 'category' in data:
            part.category = data['category'].strip()
        
        if 'is_active' in data:
            part.is_active = data['is_active']
        
        if 'sort_order' in data:
            part.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'part': part.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка обновления запчасти: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts/<int:part_id>', methods=['DELETE'])
@admin_required
def delete_part(part_id):
    """Удалить запчасть"""
    try:
        part = Part.query.get_or_404(part_id)
        
        db.session.delete(part)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка удаления запчасти: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts/<int:part_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_part_active(part_id):
    """Активировать/деактивировать запчасть"""
    try:
        part = Part.query.get_or_404(part_id)
        part.is_active = not part.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': part.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка переключения активности запчасти: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts/bulk-create', methods=['POST'])
@admin_required
def bulk_create_parts():
    """Массовое создание запчастей"""
    try:
        data = request.get_json()
        parts_data = data.get('parts', [])
        
        if not parts_data:
            return jsonify({'error': 'Список запчастей пуст'}), 400
        
        created = []
        errors = []
        
        for item in parts_data:
            try:
                name_ru = item.get('name_ru', item.get('name', '')).strip()
                
                part = Part(
                    name_ru=name_ru,
                    name_en=item.get('name_en', '').strip() if item.get('name_en') else None,
                    name_he=item.get('name_he', '').strip() if item.get('name_he') else None,
                    description_ru=item.get('description_ru', '').strip() if item.get('description_ru') else None,
                    description_en=item.get('description_en', '').strip() if item.get('description_en') else None,
                    description_he=item.get('description_he', '').strip() if item.get('description_he') else None,
                    name=name_ru,  # Старое поле для обратной совместимости
                    category=item['category'].strip(),
                    is_active=item.get('is_active', True),
                    sort_order=item.get('sort_order', 0)
                )
                
                # Автоматически добавляем переводы, если их нет
                apply_auto_translations(part, name_ru)
                
                db.session.add(part)
                created.append(part)
                
            except Exception as e:
                errors.append(f"Ошибка создания '{item.get('name', 'unknown')}': {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'created': len(created),
            'errors': errors,
            'parts': [p.to_dict() for p in created]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка массового создания запчастей: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/parts/import-default', methods=['POST'])
@admin_required
def import_default_catalog():
    """Импорт дефолтного каталога запчастей в БД"""
    try:
        created = []
        skipped = []
        
        for category, parts in PARTS_CATALOG.items():
            # Создаем категорию, если её нет
            existing_cat = Category.query.filter_by(name=category).first()
            if not existing_cat:
                cat = Category(
                    name=category,
                    is_active=True,
                    sort_order=len(Category.query.all())
                )
                db.session.add(cat)
            
            for idx, part_name in enumerate(parts):
                part = Part(
                    name_ru=part_name,
                    name=part_name,  # Старое поле для обратной совместимости
                    category=category,
                    is_active=True,
                    sort_order=idx
                )
                
                # Автоматически добавляем переводы, если их нет
                apply_auto_translations(part, part_name)
                
                db.session.add(part)
                created.append(part)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'created': len(created),
            'skipped': len(skipped),
            'message': f'Импортировано {len(created)} запчастей, пропущено {len(skipped)} (уже существуют)'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка импорта каталога: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ДЛЯ УПРАВЛЕНИЯ КАТЕГОРИЯМИ
# ============================================================================

@app.route('/api/categories', methods=['GET'])
def get_categories_api():
    """Получить список всех категорий"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        lang = request.args.get('lang', 'ru')  # Получаем язык из параметра
        
        query = Category.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        categories = query.order_by(Category.sort_order, Category.name).all()
        
        # Возвращаем данные с учётом языка
        return jsonify([cat.to_dict(lang=lang) for cat in categories])
        
    except Exception as e:
        print(f"❌ Ошибка получения категорий: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/categories', methods=['POST'])
@admin_required
def create_category():
    """Создать новую категорию"""
    try:
        data = request.get_json()
        
        # Валидация
        if not data.get('name'):
            return jsonify({'error': 'Название категории обязательно'}), 400
        
        # Проверка уникальности
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Категория с таким именем уже существует'}), 400
        
        # Создание категории с многоязычными полями
        category = Category(
            name=data['name'].strip(),
            name_ru=data.get('name_ru', data['name']).strip(),
            name_en=data.get('name_en', '').strip() if data.get('name_en') else None,
            name_he=data.get('name_he', '').strip() if data.get('name_he') else None,
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка создания категории: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/categories/<int:category_id>', methods=['GET'])
@admin_required
def get_category(category_id):
    """Получить данные категории"""
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict())


@app.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Обновить категорию"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        old_name = category.name
        
        if 'name' in data:
            # Проверка на уникальность при изменении имени
            if data['name'] != category.name:
                existing = Category.query.filter_by(name=data['name']).first()
                if existing:
                    return jsonify({'error': 'Категория с таким именем уже существует'}), 400
            
            new_name = data['name'].strip()
            
            # Обновляем категорию у всех запчастей
            Part.query.filter_by(category=old_name).update({'category': new_name})
            
            category.name = new_name
        
        # Обновляем многоязычные поля
        if 'name_ru' in data:
            category.name_ru = data['name_ru'].strip() if data['name_ru'] else None
        
        if 'name_en' in data:
            category.name_en = data['name_en'].strip() if data['name_en'] else None
        
        if 'name_he' in data:
            category.name_he = data['name_he'].strip() if data['name_he'] else None
        
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка обновления категории: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Удалить категорию"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Проверяем, есть ли запчасти в этой категории
        parts_count = Part.query.filter_by(category=category.name).count()
        if parts_count > 0:
            return jsonify({
                'error': f'Невозможно удалить категорию с запчастями ({parts_count}). Сначала удалите или переместите запчасти.'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка удаления категории: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/categories/<int:category_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_category_active(category_id):
    """Активировать/деактивировать категорию"""
    try:
        category = Category.query.get_or_404(category_id)
        category.is_active = not category.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': category.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка переключения активности категории: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

# Инициализация базы данных
def init_db():
    """Инициализация базы данных с обработкой ошибок"""
    with app.app_context():
        try:
            # Попытка создать все таблицы
            db.create_all()
            print("✅ База данных инициализирована")
            
            # Проверка наличия таблиц
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Найдено таблиц: {len(tables)}")
            print(f"📋 Таблицы: {', '.join(tables)}")
            
            # МИГРАЦИИ УБРАНЫ! Они выполняются через отдельный скрипт run_migrations.py
            # Это предотвращает блокировку при запуске на Render
            
            # Проверка наличия механиков
            mechanic_count = Mechanic.query.count()
            print(f"👥 Механиков в базе: {mechanic_count}")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            print("⚠️  Приложение продолжит работу, но функционал может быть ограничен")
            import traceback
            traceback.print_exc()



# Инициализация при запуске через Gunicorn (НЕ БЛОКИРУЮЩАЯ!)
# БД создается через init_render_db.py в buildCommand
# Миграции выполняются через run_migrations.py после деплоя

# Автоматические миграции при старте (для Render)
try:
    from migrations_auto import run_auto_migrations
    run_auto_migrations(app)
except Exception as e:
    print(f"⚠️  Автоматические миграции пропущены: {e}")

print("="*60)
print("🚀 Felix Hub готов к запуску")
print("="*60)

# НЕ вызываем init_db() при импорте - это может заблокировать запуск!
# БД уже инициализирована через init_render_db.py в процессе сборки

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

