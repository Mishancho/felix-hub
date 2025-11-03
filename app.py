import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

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
from models import db, Mechanic, Order
from auth import login_manager, admin_required, mechanic_required, should_notify_mechanic

# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# Справочник категорий и запчастей
PARTS_CATALOG = {
    'Тормоза': ['Передние колодки', 'Задние колодки', 'Диски передние', 'Диски задние', 'Тормозная жидкость'],
    'Двигатель': ['Масло моторное', 'Масляный фильтр', 'Воздушный фильтр', 'Свечи зажигания', 'Ремень ГРМ'],
    'Подвеска': ['Амортизаторы передние', 'Амортизаторы задние', 'Пружины', 'Стойки стабилизатора', 'Рычаги'],
    'Электрика': ['Аккумулятор', 'Генератор', 'Стартер', 'Лампы', 'Датчики'],
    'Расходники': ['Антифриз', 'Омывайка', 'Салонный фильтр', 'Щётки стеклоочистителя', 'Технические жидкости']
}

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
    
    parts_list = '\n'.join([f"• {part}" for part in order.selected_parts])
    
    message = f"""🔔 <b>Новый заказ от {order.mechanic_name}</b>

📋 Заказ №{order.id}
🚗 Гос номер: <b>{order.plate_number}</b>
📦 Категория: {order.category}

<b>Детали:</b>
{parts_list}

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
    receipt = f"""
{'='*40}
СТО Felix
{'='*40}
Заказ №{order.id}
Механик: {order.mechanic_name}
Гос номер: {order.plate_number}
Категория: {order.category}
{'='*40}
Детали:
"""
    for part in order.selected_parts:
        receipt += f"- {part}\n"
    
    receipt += f"""{'='*40}
Статус: {order.status}
Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}
{'='*40}
"""
    
    print(receipt)  # В продакшене здесь будет вызов принтера
    return receipt

# Маршруты приложения

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
    return render_template('mechanic/order_form.html', catalog=PARTS_CATALOG)


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
        
        # Создание нового заказа
        order = Order(
            mechanic_id=mechanic_id,
            mechanic_name=mechanic_name,
            telegram_id=telegram_id,
            category=data['category'],
            plate_number=data['plate_number'].strip().upper(),
            selected_parts=data['selected_parts'],
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
    
    return jsonify([order.to_dict() for order in orders])

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
    
    query = Order.query.filter_by(mechanic_id=current_user.id)
    
    if status and status != 'все':
        query = query.filter_by(status=status)
    
    if plate_number:
        query = query.filter(Order.plate_number.ilike(f'%{plate_number}%'))
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return jsonify([order.to_dict() for order in orders])


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
    mechanics = Mechanic.query.order_by(Mechanic.created_at.desc()).all()
    return jsonify([m.to_dict(include_stats=True) for m in mechanics])


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
        return jsonify({'error': str(e)}), 500


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
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

# Инициализация базы данных
def init_db():
    with app.app_context():
        db.create_all()
        print("✅ База данных инициализирована")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
