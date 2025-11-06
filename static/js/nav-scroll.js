// Добавление эффекта при скролле к навигационному меню
document.addEventListener('DOMContentLoaded', function() {
    const nav = document.querySelector('.nav');
    
    if (nav) {
        let lastScrollTop = 0;
        
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Добавляем класс scrolled при прокрутке вниз
            if (scrollTop > 10) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
            
            lastScrollTop = scrollTop;
        });
    }
});
