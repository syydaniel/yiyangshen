// ========================================
// 主要功能
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initSmoothScrolling();
    initMobileMenu();
    initWorldMap();
    initAnimations();
    initContactForm();
});

// ========================================
// 导航功能
// ========================================
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');
    
    // 滚动时更新活动链接
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// ========================================
// 平滑滚动
// ========================================
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ========================================
// 移动端菜单
// ========================================
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
        
        // 点击链接时关闭菜单
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            });
        });
        
        // 点击外部区域关闭菜单
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    }
}

// ========================================
// 世界地图交互
// ========================================
function initWorldMap() {
    const locations = document.querySelectorAll('.location');
    
    locations.forEach(location => {
        location.addEventListener('click', function() {
            const locationName = this.classList[1];
            showLocationInfo(locationName);
        });
        
        location.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        
        location.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

function showLocationInfo(locationName) {
    const locationData = {
        canada: {
            name: 'Vancouver, Canada',
            university: 'University of British Columbia',
            period: '2020-2024',
            research: 'Environmental Science studies and urban sustainability research'
        },
        netherlands: {
            name: 'Wageningen, Netherlands',
            university: 'Wageningen University & Research',
            period: '2024-2026',
            research: 'Current Master\'s program in Urban Environmental Management'
        },
        finland: {
            name: 'Joensuu, Finland',
            university: 'University of Eastern Finland',
            period: '2023-2024',
            research: 'Forest ecosystem research and climate change studies'
        },
        china: {
            name: 'Hangzhou, China',
            university: 'Zhejiang University',
            period: '2022-2023',
            research: 'Urban environmental assessment and sustainable development'
        }
    };
    
    const data = locationData[locationName];
    if (data) {
        alert(`${data.name}\n${data.university}\n${data.period}\n${data.research}`);
    }
}

// ========================================
// 动画效果
// ========================================
function initAnimations() {
    // 滚动动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.education-item, .experience-item, .project-card, .contact-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // 统计数字动画
    animateCounters();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current);
        }, 16);
    });
}

// ========================================
// 联系表单
// ========================================
function initContactForm() {
    const form = document.querySelector('.contact-form form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(form);
            const name = form.querySelector('input[type="text"]').value;
            const email = form.querySelector('input[type="email"]').value;
            const subject = form.querySelectorAll('input[type="text"]')[1].value;
            const message = form.querySelector('textarea').value;
            
            // 简单验证
            if (!name || !email || !subject || !message) {
                alert('Please fill in all fields.');
                return;
            }
            
            // 模拟发送
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                alert('Thank you for your message! I will get back to you soon.');
                form.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
}

// ========================================
// 工具函数
// ========================================

// 防抖函数
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

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ========================================
// 页面加载完成后的初始化
// ========================================
window.addEventListener('load', function() {
    // 添加加载完成的类
    document.body.classList.add('loaded');
    
    // 初始化所有动画
    const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-description, .hero-buttons, .hero-stats');
    heroElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
});

// ========================================
// 错误处理
// ========================================
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// ========================================
// 性能监控
// ========================================
if ('performance' in window) {
    window.addEventListener('load', function() {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
    });
}