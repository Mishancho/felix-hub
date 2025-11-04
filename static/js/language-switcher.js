// Language Switcher for Felix Hub
// Управление языком интерфейса

class LanguageSwitcher {
    constructor() {
        this.currentLang = this.getStoredLanguage() || 'ru';
        this.translations = {};
        this.init();
    }
    
    init() {
        // Создаем UI переключателя
        this.createSwitcher();
        
        // Применяем текущий язык
        this.applyLanguage(this.currentLang);
        
        // Загружаем переводы
        this.loadTranslations();
    }
    
    createSwitcher() {
        // Создаем контейнер если его еще нет
        if (document.getElementById('languageSwitcher')) {
            return;
        }
        
        const switcher = document.createElement('div');
        switcher.id = 'languageSwitcher';
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <div class="lang-selector">
                <span class="lang-icon">🌍</span>
                <select id="langSelect" class="lang-select">
                    <option value="ru" ${this.currentLang === 'ru' ? 'selected' : ''}>🇷🇺 Русский</option>
                    <option value="en" ${this.currentLang === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                    <option value="he" ${this.currentLang === 'he' ? 'selected' : ''}>🇮🇱 עברית</option>
                </select>
            </div>
        `;
        
        document.body.appendChild(switcher);
        
        // Обработчик смены языка
        document.getElementById('langSelect').addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });
    }
    
    async changeLanguage(lang) {
        if (!['ru', 'en', 'he'].includes(lang)) {
            console.error('Unsupported language:', lang);
            return;
        }
        
        this.currentLang = lang;
        this.storeLanguage(lang);
        this.applyLanguage(lang);
        
        // Отправляем на сервер
        try {
            await fetch(`/set_language/${lang}`, { method: 'POST' });
            console.log(`✅ Язык изменен на: ${lang}`);
            
            // Перезагружаем данные если функции доступны
            if (typeof loadParts === 'function') {
                loadParts();
            }
            if (typeof loadCategories === 'function') {
                loadCategories();
            }
            
            // Показываем уведомление
            this.showNotification(lang);
            
        } catch (err) {
            console.error('❌ Ошибка смены языка:', err);
        }
    }
    
    applyLanguage(lang) {
        // Устанавливаем направление текста
        const direction = lang === 'he' ? 'rtl' : 'ltr';
        document.documentElement.setAttribute('dir', direction);
        document.documentElement.setAttribute('lang', lang);
        document.body.setAttribute('dir', direction);
        
        // Сохраняем в глобальной переменной
        window.currentLanguage = lang;
        
        // Обновляем атрибут для CSS
        document.body.classList.remove('lang-ru', 'lang-en', 'lang-he');
        document.body.classList.add(`lang-${lang}`);
    }
    
    getStoredLanguage() {
        return localStorage.getItem('felix_hub_language') || sessionStorage.getItem('felix_hub_language');
    }
    
    storeLanguage(lang) {
        localStorage.setItem('felix_hub_language', lang);
        sessionStorage.setItem('felix_hub_language', lang);
    }
    
    async loadTranslations() {
        try {
            const response = await fetch(`/static/translations/${this.currentLang}.json`);
            if (response.ok) {
                this.translations = await response.json();
            }
        } catch (err) {
            console.warn('Не удалось загрузить переводы:', err);
        }
    }
    
    translate(key) {
        return this.translations[key] || key;
    }
    
    showNotification(lang) {
        const messages = {
            ru: 'Язык изменен на русский',
            en: 'Language changed to English',
            he: 'השפה שונתה לעברית'
        };
        
        if (typeof showAlert === 'function') {
            showAlert(messages[lang], 'success');
        }
    }
}

// Хелпер функции для использования в других скриптах
function getCurrentLanguage() {
    return window.currentLanguage || localStorage.getItem('felix_hub_language') || 'ru';
}

function getTranslation(key) {
    if (window.languageSwitcher) {
        return window.languageSwitcher.translate(key);
    }
    return key;
}

// Алиас для краткости
const t = getTranslation;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.languageSwitcher = new LanguageSwitcher();
    console.log(`🌍 Language Switcher initialized. Current language: ${getCurrentLanguage()}`);
});
