/**
 * Language Management Module - Felix Hub
 * Управление языками и переводами интерфейса
 */

// Объект с переводами UI элементов
const translations = {
    ru: {
        // Заголовки и навигация
        'parts_management': 'Управление запчастями',
        'parts': 'Запчасти',
        'categories': 'Категории',
        'logout': 'Выйти',
        
        // Статистика
        'total_categories': 'Всего категорий',
        'total_parts': 'Всего запчастей',
        'active_parts': 'Активных',
        
        // Кнопки
        'add_category': 'Добавить категорию',
        'add_part': 'Добавить запчасть',
        'import_catalog': 'Импортировать каталог',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'edit': 'Редактировать',
        'delete': 'Удалить',
        'toggle_status': 'Изменить статус',
        
        // Фильтры
        'search_placeholder': 'Поиск по названию или категории...',
        'all_categories': 'Все категории',
        'all_parts': 'Все запчасти',
        'active_only': 'Только активные',
        'inactive_only': 'Только неактивные',
        
        // Статусы
        'active': 'Активна',
        'inactive': 'Неактивна',
        
        // Модальные окна - Категории
        'add_category_title': 'Добавить категорию',
        'edit_category_title': 'Редактировать категорию',
        'category_name': 'Название категории',
        'sort_order': 'Порядок сортировки',
        'is_active': 'Активна',
        
        // Модальные окна - Запчасти
        'add_part_title': 'Добавить запчасть',
        'edit_part_title': 'Редактировать запчасть',
        'part_name_ru': 'Название (Русский)',
        'part_name_en': 'Название (English)',
        'part_name_he': 'Название (עברית)',
        'part_desc_ru': 'Описание (Русский)',
        'part_desc_en': 'Описание (English)',
        'part_desc_he': 'Описание (עברית)',
        'part_category': 'Категория',
        'choose_category': 'Выберите категорию',
        
        // Сообщения
        'category_added': 'Категория добавлена',
        'category_updated': 'Категория обновлена',
        'category_deleted': 'Категория удалена',
        'category_status_changed': 'Статус категории изменен',
        'part_added': 'Запчасть добавлена',
        'part_updated': 'Запчасть обновлена',
        'part_deleted': 'Запчасть удалена',
        'part_status_changed': 'Статус запчасти изменен',
        'catalog_imported': 'Каталог импортирован',
        
        // Ошибки
        'error_loading_categories': 'Ошибка загрузки категорий',
        'error_loading_parts': 'Ошибка загрузки запчастей',
        'error_loading_category': 'Ошибка загрузки категории',
        'error_loading_part': 'Ошибка загрузки запчасти',
        'error_saving': 'Ошибка сохранения',
        'error_deleting': 'Ошибка удаления',
        'error': 'Ошибка',
        
        // Подтверждения
        'confirm_delete_category': 'Удалить категорию? Это возможно только если в ней нет запчастей.',
        'confirm_delete_part': 'Удалить запчасть?',
        'confirm_import_catalog': 'Импортировать дефолтный каталог? Существующие записи не будут затронуты.',
        
        // Пустые состояния
        'no_categories': 'Категорий нет',
        'no_categories_desc': 'Добавьте первую категорию или импортируйте каталог',
        'no_parts': 'Запчасти не найдены',
        'no_parts_desc': 'Попробуйте изменить фильтры',
        
        // Таблицы
        'table_id': 'ID',
        'table_name': 'Название',
        'table_category': 'Категория',
        'table_parts_count': 'Запчастей',
        'table_active_count': 'Активных',
        'table_sort_order': 'Порядок',
        'table_status': 'Статус',
        'table_actions': 'Действия'
    },
    
    en: {
        // Headers and navigation
        'parts_management': 'Parts Management',
        'parts': 'Parts',
        'categories': 'Categories',
        'logout': 'Logout',
        
        // Statistics
        'total_categories': 'Total Categories',
        'total_parts': 'Total Parts',
        'active_parts': 'Active',
        
        // Buttons
        'add_category': 'Add Category',
        'add_part': 'Add Part',
        'import_catalog': 'Import Catalog',
        'save': 'Save',
        'cancel': 'Cancel',
        'edit': 'Edit',
        'delete': 'Delete',
        'toggle_status': 'Toggle Status',
        
        // Filters
        'search_placeholder': 'Search by name or category...',
        'all_categories': 'All Categories',
        'all_parts': 'All Parts',
        'active_only': 'Active Only',
        'inactive_only': 'Inactive Only',
        
        // Statuses
        'active': 'Active',
        'inactive': 'Inactive',
        
        // Modal windows - Categories
        'add_category_title': 'Add Category',
        'edit_category_title': 'Edit Category',
        'category_name': 'Category Name',
        'sort_order': 'Sort Order',
        'is_active': 'Active',
        
        // Modal windows - Parts
        'add_part_title': 'Add Part',
        'edit_part_title': 'Edit Part',
        'part_name_ru': 'Name (Russian)',
        'part_name_en': 'Name (English)',
        'part_name_he': 'Name (Hebrew)',
        'part_desc_ru': 'Description (Russian)',
        'part_desc_en': 'Description (English)',
        'part_desc_he': 'Description (Hebrew)',
        'part_category': 'Category',
        'choose_category': 'Choose Category',
        
        // Messages
        'category_added': 'Category Added',
        'category_updated': 'Category Updated',
        'category_deleted': 'Category Deleted',
        'category_status_changed': 'Category Status Changed',
        'part_added': 'Part Added',
        'part_updated': 'Part Updated',
        'part_deleted': 'Part Deleted',
        'part_status_changed': 'Part Status Changed',
        'catalog_imported': 'Catalog Imported',
        
        // Errors
        'error_loading_categories': 'Error Loading Categories',
        'error_loading_parts': 'Error Loading Parts',
        'error_loading_category': 'Error Loading Category',
        'error_loading_part': 'Error Loading Part',
        'error_saving': 'Error Saving',
        'error_deleting': 'Error Deleting',
        'error': 'Error',
        
        // Confirmations
        'confirm_delete_category': 'Delete category? Only possible if it has no parts.',
        'confirm_delete_part': 'Delete part?',
        'confirm_import_catalog': 'Import default catalog? Existing records will not be affected.',
        
        // Empty states
        'no_categories': 'No Categories',
        'no_categories_desc': 'Add first category or import catalog',
        'no_parts': 'No Parts Found',
        'no_parts_desc': 'Try changing filters',
        
        // Tables
        'table_id': 'ID',
        'table_name': 'Name',
        'table_category': 'Category',
        'table_parts_count': 'Parts',
        'table_active_count': 'Active',
        'table_sort_order': 'Order',
        'table_status': 'Status',
        'table_actions': 'Actions'
    },
    
    he: {
        // כותרות וניווט
        'parts_management': 'ניהול חלפים',
        'parts': 'חלפים',
        'categories': 'קטגוריות',
        'logout': 'התנתק',
        
        // סטטיסטיקה
        'total_categories': 'סה"כ קטגוריות',
        'total_parts': 'סה"כ חלפים',
        'active_parts': 'פעילים',
        
        // כפתורים
        'add_category': 'הוסף קטגוריה',
        'add_part': 'הוסף חלק',
        'import_catalog': 'ייבא קטלוג',
        'save': 'שמור',
        'cancel': 'בטל',
        'edit': 'ערוך',
        'delete': 'מחק',
        'toggle_status': 'שנה סטטוס',
        
        // מסננים
        'search_placeholder': 'חפש לפי שם או קטגוריה...',
        'all_categories': 'כל הקטגוריות',
        'all_parts': 'כל החלפים',
        'active_only': 'פעילים בלבד',
        'inactive_only': 'לא פעילים בלבד',
        
        // סטטוסים
        'active': 'פעיל',
        'inactive': 'לא פעיל',
        
        // חלונות מודאליים - קטגוריות
        'add_category_title': 'הוסף קטגוריה',
        'edit_category_title': 'ערוך קטגוריה',
        'category_name': 'שם קטגוריה',
        'sort_order': 'סדר מיון',
        'is_active': 'פעיל',
        
        // חלונות מודאליים - חלפים
        'add_part_title': 'הוסף חלק',
        'edit_part_title': 'ערוך חלק',
        'part_name_ru': 'שם (רוסית)',
        'part_name_en': 'שם (אנגלית)',
        'part_name_he': 'שם (עברית)',
        'part_desc_ru': 'תיאור (רוסית)',
        'part_desc_en': 'תיאור (אנגלית)',
        'part_desc_he': 'תיאור (עברית)',
        'part_category': 'קטגוריה',
        'choose_category': 'בחר קטגוריה',
        
        // הודעות
        'category_added': 'קטגוריה נוספה',
        'category_updated': 'קטגוריה עודכנה',
        'category_deleted': 'קטגוריה נמחקה',
        'category_status_changed': 'סטטוס קטגוריה שונה',
        'part_added': 'חלק נוסף',
        'part_updated': 'חלק עודכן',
        'part_deleted': 'חלק נמחק',
        'part_status_changed': 'סטטוס חלק שונה',
        'catalog_imported': 'קטלוג יובא',
        
        // שגיאות
        'error_loading_categories': 'שגיאה בטעינת קטגוריות',
        'error_loading_parts': 'שגיאה בטעינת חלפים',
        'error_loading_category': 'שגיאה בטעינת קטגוריה',
        'error_loading_part': 'שגיאה בטעינת חלק',
        'error_saving': 'שגיאה בשמירה',
        'error_deleting': 'שגיאה במחיקה',
        'error': 'שגיאה',
        
        // אישורים
        'confirm_delete_category': 'למחוק קטגוריה? אפשרי רק אם אין בה חלפים.',
        'confirm_delete_part': 'למחוק חלק?',
        'confirm_import_catalog': 'לייבא קטלוג ברירת מחדל? רשומות קיימות לא יושפעו.',
        
        // מצבים ריקים
        'no_categories': 'אין קטגוריות',
        'no_categories_desc': 'הוסף קטגוריה ראשונה או ייבא קטלוג',
        'no_parts': 'לא נמצאו חלפים',
        'no_parts_desc': 'נסה לשנות מסננים',
        
        // טבלאות
        'table_id': 'מזהה',
        'table_name': 'שם',
        'table_category': 'קטגוריה',
        'table_parts_count': 'חלפים',
        'table_active_count': 'פעילים',
        'table_sort_order': 'סדר',
        'table_status': 'סטטוס',
        'table_actions': 'פעולות'
    }
};

/**
 * Получить текущий язык из localStorage
 * @returns {string} Код языка (ru, en, he)
 */
function getCurrentLanguage() {
    return localStorage.getItem('language') || 'ru';
}

/**
 * Установить новый язык
 * @param {string} lang - Код языка (ru, en, he)
 */
async function setLanguage(lang) {
    if (!['ru', 'en', 'he'].includes(lang)) {
        console.error('Invalid language:', lang);
        return;
    }
    
    try {
        // Сохраняем в localStorage
        localStorage.setItem('language', lang);
        
        // Отправляем на сервер для сохранения в session/БД
        const response = await fetch(`/set_language/${lang}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            console.error('Error setting language on server');
        }
        
        // Применяем язык к интерфейсу
        applyLanguage(lang);
        
        // Перезагружаем данные с новым языком
        if (typeof loadParts === 'function') {
            loadParts();
        }
        if (typeof loadCategories === 'function') {
            loadCategories();
        }
        
        return true;
    } catch (error) {
        console.error('Error setting language:', error);
        return false;
    }
}

/**
 * Получить перевод текста
 * @param {string} key - Ключ перевода
 * @param {string} lang - Язык (необязательно, берется текущий)
 * @returns {string} Переведенный текст или ключ, если перевод не найден
 */
function t(key, lang = null) {
    const currentLang = lang || getCurrentLanguage();
    
    if (translations[currentLang] && translations[currentLang][key]) {
        return translations[currentLang][key];
    }
    
    // Fallback на русский
    if (currentLang !== 'ru' && translations.ru[key]) {
        return translations.ru[key];
    }
    
    // Если перевод не найден, возвращаем ключ
    console.warn(`Translation not found: ${key} (${currentLang})`);
    return key;
}

/**
 * Применить язык к элементам с data-i18n атрибутом
 * @param {string} lang - Код языка
 */
function applyLanguage(lang) {
    // Устанавливаем dir="rtl" для иврита
    document.documentElement.setAttribute('dir', lang === 'he' ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', lang);
    
    // Обновляем все элементы с data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key, lang);
        
        // Обновляем текст или placeholder
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else {
                element.value = translation;
            }
        } else {
            element.textContent = translation;
        }
    });
}

/**
 * Инициализация при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', () => {
    const currentLang = getCurrentLanguage();
    applyLanguage(currentLang);
    
    // Слушаем событие смены языка от language-switcher.js
    window.addEventListener('languageChanged', (event) => {
        const newLang = event.detail.language;
        applyLanguage(newLang);
    });
});

// Экспорт функций для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCurrentLanguage,
        setLanguage,
        t,
        applyLanguage,
        translations
    };
}
