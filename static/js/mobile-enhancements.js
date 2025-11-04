/**
 * FELIX HUB - MOBILE ENHANCEMENTS
 * Улучшения UX для мобильных устройств
 */

(function() {
    'use strict';
    
    // Определяем мобильное устройство
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTablet = /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768;
    
    // Добавляем класс к body
    if (isMobile) {
        document.body.classList.add('is-mobile');
    }
    if (isTablet) {
        document.body.classList.add('is-tablet');
    }
    
    /**
     * 1. BURGER MENU для навигации
     */
    function initBurgerMenu() {
        const nav = document.querySelector('.nav');
        if (!nav || window.innerWidth > 768) return;
        
        // Проверяем количество пунктов меню
        const navItems = nav.querySelectorAll('a');
        if (navItems.length <= 4) return; // Не нужен бургер для малого количества
        
        // Создаем бургер кнопку с улучшенным дизайном
        const burgerBtn = document.createElement('button');
        burgerBtn.className = 'nav-toggle';
        burgerBtn.innerHTML = '<span>Меню</span>';
        burgerBtn.setAttribute('aria-label', 'Toggle navigation');
        burgerBtn.setAttribute('aria-expanded', 'false');
        
        // Оборачиваем навигацию
        const navWrapper = document.createElement('div');
        navWrapper.className = 'nav-large';
        nav.parentNode.insertBefore(navWrapper, nav);
        navWrapper.appendChild(burgerBtn);
        
        const navItemsContainer = document.createElement('div');
        navItemsContainer.className = 'nav-items';
        navItems.forEach(item => {
            const clone = item.cloneNode(true);
            navItemsContainer.appendChild(clone);
        });
        navWrapper.appendChild(navItemsContainer);
        
        nav.remove();
        
        // Обработчик клика с анимацией
        burgerBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isExpanded = this.classList.toggle('active');
            navItemsContainer.classList.toggle('active');
            this.setAttribute('aria-expanded', isExpanded);
            
            // Анимация иконки
            if (isExpanded) {
                this.querySelector('span').textContent = 'Закрыть';
            } else {
                this.querySelector('span').textContent = 'Меню';
            }
        });
        
        // Закрытие при клике вне меню
        document.addEventListener('click', function(e) {
            if (!navWrapper.contains(e.target)) {
                burgerBtn.classList.remove('active');
                navItemsContainer.classList.remove('active');
                burgerBtn.setAttribute('aria-expanded', 'false');
                burgerBtn.querySelector('span').textContent = 'Меню';
            }
        });
        
        // Закрытие при клике на пункт меню
        navItemsContainer.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                burgerBtn.classList.remove('active');
                navItemsContainer.classList.remove('active');
                burgerBtn.setAttribute('aria-expanded', 'false');
                burgerBtn.querySelector('span').textContent = 'Меню';
            });
        });
    }
    
    /**
     * 2. ТАБЛИЦЫ - преобразование в карточки на мобильных
     */
    function makeTablesResponsive() {
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            // Не применяем к уже обработанным таблицам
            if (table.classList.contains('table-cards')) return;
            
            // Добавляем обертку для скролла
            if (!table.parentElement.classList.contains('table-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-wrapper';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
            
            // На мобильных преобразуем в карточки
            if (window.innerWidth <= 640) {
                table.classList.add('table-cards');
                
                // Добавляем data-label к ячейкам
                const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            cell.setAttribute('data-label', headers[index]);
                        }
                    });
                });
            }
        });
    }
    
    /**
     * 3. TOUCH FEEDBACK для кнопок
     */
    function addTouchFeedback() {
        const buttons = document.querySelectorAll('button, .btn, a.btn');
        
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.95)';
            }, { passive: true });
            
            button.addEventListener('touchend', function() {
                this.style.transform = '';
            }, { passive: true });
        });
    }
    
    /**
     * 4. ВИРТУАЛЬНАЯ КЛАВИАТУРА - подстройка viewport
     */
    function handleVirtualKeyboard() {
        const inputs = document.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                // Скроллим элемент в видимую область
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            });
        });
    }
    
    /**
     * 5. SWIPE для модальных окон (закрытие свайпом вниз)
     */
    function addSwipeToClose() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            let startY = 0;
            let currentY = 0;
            
            const modalContent = modal.querySelector('.modal-content');
            if (!modalContent) return;
            
            modalContent.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
            }, { passive: true });
            
            modalContent.addEventListener('touchmove', function(e) {
                currentY = e.touches[0].clientY;
                const diff = currentY - startY;
                
                // Только если свайп вниз и мы в начале скролла
                if (diff > 0 && modalContent.scrollTop === 0) {
                    e.preventDefault();
                    modalContent.style.transform = `translateY(${diff}px)`;
                }
            });
            
            modalContent.addEventListener('touchend', function() {
                const diff = currentY - startY;
                
                // Если свайп больше 100px - закрываем
                if (diff > 100) {
                    modal.classList.remove('active');
                }
                
                // Сбрасываем transform
                modalContent.style.transform = '';
                startY = 0;
                currentY = 0;
            }, { passive: true });
        });
    }
    
    /**
     * 6. ОПТИМИЗАЦИЯ СКРОЛЛА
     */
    function optimizeScroll() {
        // Passive event listeners для скролла
        let scrollTimeout;
        
        window.addEventListener('scroll', function() {
            // Добавляем класс при скролле
            document.body.classList.add('is-scrolling');
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(function() {
                document.body.classList.remove('is-scrolling');
            }, 150);
        }, { passive: true });
    }
    
    /**
     * 7. PULL TO REFRESH (опционально)
     */
    function initPullToRefresh() {
        if (!isMobile || window.innerWidth > 768) return;
        
        let startY = 0;
        let pulling = false;
        
        document.addEventListener('touchstart', function(e) {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            if (window.scrollY === 0) {
                const currentY = e.touches[0].clientY;
                const diff = currentY - startY;
                
                if (diff > 100 && !pulling) {
                    pulling = true;
                    // Можно добавить индикатор загрузки
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', function() {
            if (pulling) {
                pulling = false;
                // Опционально: перезагрузить страницу
                // window.location.reload();
            }
        }, { passive: true });
    }
    
    /**
     * 8. ORIENTATION CHANGE HANDLER
     */
    function handleOrientationChange() {
        let previousOrientation = window.orientation;
        
        window.addEventListener('orientationchange', function() {
            // Небольшая задержка для правильного пересчета размеров
            setTimeout(function() {
                // Пересчитываем таблицы
                makeTablesResponsive();
                
                // Закрываем модальные окна при повороте
                const openModals = document.querySelectorAll('.modal.active');
                openModals.forEach(modal => {
                    if (window.innerWidth < 768) {
                        // Опционально можно закрыть
                        // modal.classList.remove('active');
                    }
                });
                
                previousOrientation = window.orientation;
            }, 200);
        });
    }
    
    /**
     * 9. DEBOUNCE для resize
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * 10. WINDOW RESIZE HANDLER
     */
    const handleResize = debounce(function() {
        // Пересчитываем таблицы
        makeTablesResponsive();
        
        // Проверяем нужность бургер-меню
        if (window.innerWidth > 768) {
            const navToggle = document.querySelector('.nav-toggle');
            if (navToggle) {
                navToggle.classList.remove('active');
                const navItems = document.querySelector('.nav-items');
                if (navItems) navItems.classList.remove('active');
            }
        }
    }, 250);
    
    /**
     * 11. PREVENT ZOOM ON INPUT FOCUS (iOS)
     */
    function preventZoomOnFocus() {
        if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
            const viewportMeta = document.querySelector('meta[name="viewport"]');
            if (viewportMeta) {
                let content = viewportMeta.getAttribute('content');
                
                document.addEventListener('focusin', function() {
                    viewportMeta.setAttribute('content', content + ', user-scalable=no');
                });
                
                document.addEventListener('focusout', function() {
                    viewportMeta.setAttribute('content', content);
                });
            }
        }
    }
    
    /**
     * 12. SMOOTH SCROLL POLYFILL
     */
    function initSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    /**
     * 13. DETECT STANDALONE MODE (PWA)
     */
    function detectStandalone() {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                           window.navigator.standalone ||
                           document.referrer.includes('android-app://');
        
        if (isStandalone) {
            document.body.classList.add('is-standalone');
        }
    }
    
    /**
     * ИНИЦИАЛИЗАЦИЯ ВСЕХ ФУНКЦИЙ
     */
    function init() {
        // Ждем загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', runInit);
        } else {
            runInit();
        }
    }
    
    function runInit() {
        console.log('Felix Hub: Initializing mobile enhancements...');
        
        // Определяем окружение
        detectStandalone();
        
        // Инициализируем функции
        if (window.innerWidth <= 768) {
            initBurgerMenu();
        }
        
        makeTablesResponsive();
        addTouchFeedback();
        handleVirtualKeyboard();
        addSwipeToClose();
        optimizeScroll();
        handleOrientationChange();
        preventZoomOnFocus();
        initSmoothScroll();
        
        // Опционально
        // initPullToRefresh();
        
        // Обработчик resize
        window.addEventListener('resize', handleResize);
        
        console.log('Felix Hub: Mobile enhancements loaded!');
    }
    
    // Запускаем инициализацию
    init();
    
    // Экспортируем функции для использования в других скриптах
    window.FelixMobile = {
        isMobile: isMobile,
        isTablet: isTablet,
        makeTablesResponsive: makeTablesResponsive,
        initBurgerMenu: initBurgerMenu
    };
    
})();
