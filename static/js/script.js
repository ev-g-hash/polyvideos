// Общие функции для всех страниц

// Scroll progress bar
function initScrollProgress() {
    window.addEventListener('scroll', () => {
        const scrollProgress = document.getElementById('scrollProgress');
        if (scrollProgress) {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const progress = (scrollTop / scrollHeight) * 100;
            scrollProgress.style.width = progress + '%';
        }
    });
}

// Create floating particles
function initParticles() {
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        const particleCount = particlesContainer.closest('body').querySelector('.video-grid') ? 50 : 30;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.setProperty('--tx', (Math.random() - 0.5) * 200 + 'px');
            particle.style.setProperty('--ty', (Math.random() - 0.5) * 200 + 'px');
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
            particlesContainer.appendChild(particle);
        }
    }
}

// Функции для галереи
function initGallery() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const videoCards = document.querySelectorAll('.video-card');

    if (filterTabs.length > 0 && videoCards.length > 0) {
        filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                filterTabs.forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                tab.classList.add('active');

                const category = tab.textContent;
                
                // Filter videos (for demo, just animate)
                videoCards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            });
        });

        // Video card click functionality
        videoCards.forEach(card => {
            card.addEventListener('click', () => {
                const videoTitle = card.querySelector('h3').textContent;
                alert(`Открываем видео: "${videoTitle}"\n\nВ будущем здесь будет плеер! 🎬`);
            });
        });
    }
}

// Функции для админ панели
function initAdmin() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const username = loginForm.querySelector('input[type="text"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;
            
            // Простая демо-проверка
            if (username === 'admin' && password === 'admin123') {
                alert('Добро пожаловать в админ панель!\n\nЗдесь будет интерфейс для управления видео.');
                // В реальном приложении здесь был бы переход в админ-панель
            } else {
                alert('Неверный логин или пароль!\n\nДемо данные:\nЛогин: admin\nПароль: admin123');
            }
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initScrollProgress();
    initParticles();
    
    // Инициализация функций в зависимости от страницы
    if (document.querySelector('.video-grid')) {
        initGallery();
    }
    
    if (document.getElementById('loginForm')) {
        initAdmin();
    }
});