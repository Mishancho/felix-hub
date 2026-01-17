"""
Модели данных для Felix Hub v2.2

Изменения в v2.2:
- Добавлена модель Mechanic для управления механиками
- Order теперь связан с Mechanic через внешний ключ
- Сохранена обратная совместимость через поле mechanic_name
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Mechanic(UserMixin, db.Model):
    """
    Модель механика с системой аутентификации
    """
    __tablename__ = 'mechanics'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Статус и настройки
    is_active = db.Column(db.Boolean, default=True, index=True)
    notify_on_ready = db.Column(db.Boolean, default=True)
    notify_on_processing = db.Column(db.Boolean, default=False)
    notify_on_cancelled = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(5), default='ru')
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Связь с заказами (один механик - много заказов)
    orders = db.relationship('Order', backref='mechanic', lazy='dynamic')
    
    def set_password(self, password):
        """Установить хешированный пароль"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Обновить время последнего входа"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_order_stats(self):
        """Получить статистику заказов механика"""
        total_orders = self.orders.count()
        new_orders = self.orders.filter_by(status='новый').count()
        processing_orders = self.orders.filter_by(status='в работе').count()
        ready_orders = self.orders.filter_by(status='готово').count()
        completed_orders = self.orders.filter_by(status='выдано').count()
        
        return {
            'total': total_orders,
            'new': new_orders,
            'processing': processing_orders,
            'ready': ready_orders,
            'completed': completed_orders
        }
    
    def to_dict(self, include_stats=False):
        """Преобразовать в словарь для API"""
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'telegram_id': self.telegram_id,
            'phone': self.phone,
            'email': self.email,
            'is_active': self.is_active,
            'notify_on_ready': self.notify_on_ready,
            'notify_on_processing': self.notify_on_processing,
            'notify_on_cancelled': self.notify_on_cancelled,
            'language': self.language,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
        
        if include_stats:
            data['stats'] = self.get_order_stats()
        
        return data
    
    def __repr__(self):
        return f'<Mechanic {self.username}>'


class Category(db.Model):
    """
    Модель категории запчастей с многоязычной поддержкой
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Названия на трех языках
    name_en = db.Column(db.String(120))
    name_he = db.Column(db.String(120))
    name_ru = db.Column(db.String(120))
    
    is_active = db.Column(db.Boolean, default=True, index=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_name(self, lang='ru'):
        """Получить название на указанном языке"""
        if lang == 'en' and self.name_en:
            return self.name_en
        elif lang == 'he' and self.name_he:
            return self.name_he
        elif lang == 'ru' and self.name_ru:
            return self.name_ru
        # Fallback на основное имя
        return self.name
    
    def to_dict(self, lang=None):
        """Преобразовать в словарь для API"""
        # Подсчитываем количество запчастей в категории
        parts_count = Part.query.filter_by(category=self.name).count()
        active_parts_count = Part.query.filter_by(category=self.name, is_active=True).count()
        
        # Базовые данные со всеми языками
        data = {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'name_he': self.name_he,
            'name_ru': self.name_ru,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'parts_count': parts_count,
            'active_parts_count': active_parts_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Если указан язык, добавляем локализованное имя
        if lang:
            data['name'] = self.get_name(lang)
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Part(db.Model):
    """
    Модель запчасти в справочнике с многоязычной поддержкой
    """
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Название на трех языках
    name_en = db.Column(db.String(250))
    name_he = db.Column(db.String(250))
    name_ru = db.Column(db.String(250), nullable=False)
    
    # Описание на трех языках
    description_en = db.Column(db.Text)
    description_he = db.Column(db.Text)
    description_ru = db.Column(db.Text)
    
    # Старое поле для обратной совместимости
    name = db.Column(db.String(250))
    
    category = db.Column(db.String(120), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_name(self, lang='ru'):
        """Получить название на указанном языке"""
        if lang == 'en' and self.name_en:
            return self.name_en
        elif lang == 'he' and self.name_he:
            return self.name_he
        elif lang == 'ru' and self.name_ru:
            return self.name_ru
        # Fallback на русский
        return self.name_ru or self.name or 'N/A'
    
    def get_description(self, lang='ru'):
        """Получить описание на указанном языке"""
        if lang == 'en' and self.description_en:
            return self.description_en
        elif lang == 'he' and self.description_he:
            return self.description_he
        elif lang == 'ru' and self.description_ru:
            return self.description_ru
        # Fallback на русский
        return self.description_ru or ''
    
    def to_dict(self, lang=None):
        """Преобразовать в словарь для API"""
        if lang:
            # Возвращаем данные на конкретном языке
            return {
                'id': self.id,
                'name': self.get_name(lang),
                'description': self.get_description(lang),
                'category': self.category,
                'is_active': self.is_active,
                'sort_order': self.sort_order,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            # Возвращаем все языки (для админа)
            return {
                'id': self.id,
                'name_en': self.name_en,
                'name_he': self.name_he,
                'name_ru': self.name_ru,
                'description_en': self.description_en,
                'description_he': self.description_he,
                'description_ru': self.description_ru,
                'category': self.category,
                'is_active': self.is_active,
                'sort_order': self.sort_order,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def __repr__(self):
        return f'<Part {self.name_ru or self.name}>'


class Order(db.Model):
    """
    Модель заказа запчастей
    
    v2.2: Добавлена связь с Mechanic
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Связь с механиком (новое в v2.2)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), index=True)
    
    # Старое поле для обратной совместимости
    mechanic_name = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(50))
    
    # Данные заказа
    category = db.Column(db.String(120), nullable=False)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    selected_parts = db.Column(db.JSON)
    is_original = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(250))
    comment = db.Column(db.Text)
    
    # Статус и метаданные
    status = db.Column(db.String(50), default='новый', index=True)
    printed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_mechanic=False, lang=None):
        """Преобразовать в словарь для API"""
        category_name = self.category
        category_obj = Category.query.filter(
            (Category.name == self.category) |
            (Category.name_ru == self.category) |
            (Category.name_en == self.category) |
            (Category.name_he == self.category)
        ).first()
        category_raw = category_obj.name if category_obj else self.category

        if lang and category_obj:
            category_name = category_obj.get_name(lang)
        
        def translate_no_additives(target_lang):
            if target_lang == 'he':
                return 'ללא תוספים'
            if target_lang == 'en':
                return 'NO ADDITIVES'
            return 'БЕЗ ПРИСАДОК'

        no_additives_aliases_cf = {
            'no_additives',
            'без присадок',
            'без добавок',
            'no additives',
            'ללא תוספים',
        }

        # Обработка selected_parts с переводом
        selected_parts_translated = []
        for part in (self.selected_parts or []):
            if isinstance(part, dict):
                part_id = part.get('part_id')
                quantity = part.get('quantity', 1)
                added_flag = part.get('added_by_mechanic')
                added_at = part.get('added_at')
                
                # Если есть part_id, получаем название на нужном языке
                if part_id:
                    part_obj = Part.query.get(part_id)
                    if part_obj:
                        part_name = part_obj.get_name(lang) if lang else part_obj.get_name('ru')
                        item = {
                            'part_id': part_id,
                            'name': part_name,
                            'quantity': quantity
                        }
                        if added_flag is not None:
                            item['added_by_mechanic'] = added_flag
                        if added_at:
                            item['added_at'] = added_at
                        selected_parts_translated.append(item)
                    else:
                        # Если запчасть не найдена, используем старое название
                        item = {
                            'name': part.get('name', 'Unknown'),
                            'quantity': quantity
                        }
                        if added_flag is not None:
                            item['added_by_mechanic'] = added_flag
                        if added_at:
                            item['added_at'] = added_at
                        selected_parts_translated.append(item)
                else:
                    # Старый формат без part_id
                    if isinstance(part, dict):
                        raw_name = part.get('name', '')
                        name = raw_name
                        if isinstance(raw_name, str) and (raw_name.strip() == 'no_additives' or raw_name.strip().casefold() in no_additives_aliases_cf):
                            name = translate_no_additives(lang)
                        item = {
                            'name': name,
                            'quantity': quantity
                        }
                        if added_flag is not None:
                            item['added_by_mechanic'] = added_flag
                        if added_at:
                            item['added_at'] = added_at
                        selected_parts_translated.append(item)
                    else:
                        selected_parts_translated.append(part)
            else:
                # Совсем старый формат (просто строка)
                if isinstance(part, str) and (part.strip() == 'no_additives' or part.strip().casefold() in no_additives_aliases_cf):
                    selected_parts_translated.append(translate_no_additives(lang))
                else:
                    selected_parts_translated.append(part)

        # Сортировка по порядковому номеру из БД
        try:
            parts_in_category = Part.query.filter_by(category=category_raw).all()
            id_to_order = {p.id: (p.sort_order if p.sort_order is not None else 0) for p in parts_in_category}
            name_to_order = {}
            for p in parts_in_category:
                for nm in [p.name_ru, p.name_en, p.name_he, p.name]:
                    if nm:
                        name_to_order[nm] = (p.sort_order if p.sort_order is not None else 0)
            max_order = max([o for o in id_to_order.values()] + [0])
            def sort_key(item, idx):
                if isinstance(item, dict):
                    pid = item.get('part_id')
                    nm = item.get('name')
                    if isinstance(pid, str) and pid.isdigit():
                        pid = int(pid)
                    if pid in id_to_order:
                        return (id_to_order[pid], idx)
                    if nm in name_to_order:
                        return (name_to_order[nm], idx)
                    return (max_order + 1, idx)
                else:
                    if item in name_to_order:
                        return (name_to_order[item], idx)
                    return (max_order + 1, idx)
            selected_parts_translated = [x for _, x in sorted([(sort_key(it, i), it) for i, it in enumerate(selected_parts_translated)], key=lambda t: t[0])]
        except Exception:
            pass
        
        data = {
            'id': self.id,
            'mechanic_name': self.mechanic_name,
            'telegram_id': self.telegram_id,
            'category': category_name,
            'category_raw': category_raw,
            'plate_number': self.plate_number,
            'selected_parts': selected_parts_translated,
            'is_original': self.is_original,
            'photo_url': self.photo_url,
            'comment': self.comment,
            'status': self.status,
            'printed': self.printed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Добавить информацию о механике, если он есть
        if include_mechanic and self.mechanic:
            data['mechanic'] = {
                'id': self.mechanic.id,
                'username': self.mechanic.username,
                'full_name': self.mechanic.full_name
            }
        
        return data
    
    def __repr__(self):
        return f'<Order {self.id} - {self.mechanic_name}>'
