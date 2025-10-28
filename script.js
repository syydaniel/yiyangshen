// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initNavigation();
    initScrollEffects();
    initPublicationFilters();
    initContactForm();
    initAnimations();
    initMobileMenu();
    initBackToTop();
    initWorldMap();
    initEasterEggs();
    initAdvancedInteractions();
    initScrollAnimations();
    initLoadingStates();
});

// 导航栏功能
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id]');
    const navbar = document.querySelector('.navbar');
    
    // 平滑滚动到指定部分
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // 考虑导航栏高度
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
            
            // 关闭移动端菜单
            const navMenu = document.querySelector('.nav-menu');
            const hamburger = document.querySelector('.hamburger');
            if (navMenu && hamburger) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    });
    
    // 高亮当前部分对应的导航链接
    function highlightNavLink() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }
    
    // 滚动时改变导航栏样式
    function handleScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        highlightNavLink();
    }
    
    window.addEventListener('scroll', handleScroll);
}

// 滚动效果
function initScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('loaded');
            }
        });
    }, observerOptions);
    
    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.research-card, .publication-item, .timeline-item, .contact-item');
    animatedElements.forEach(el => {
        el.classList.add('loading');
        observer.observe(el);
    });
}

// 学术成果筛选功能
function initPublicationFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const publicationItems = document.querySelectorAll('.publication-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有按钮的active类
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // 添加当前按钮的active类
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            publicationItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'grid';
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

// 联系表单功能
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(this);
            const name = formData.get('name');
            const email = formData.get('email');
            const subject = formData.get('subject');
            const message = formData.get('message');
            
            // Simple form validation
            if (!name || !email || !subject || !message) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address', 'error');
                return;
            }
            
            // Simulate sending email
            showNotification('Message sent successfully! I will reply to you soon.', 'success');
            this.reset();
        });
    }
}

// 邮箱验证
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 动画效果
function initAnimations() {
    // 数字计数动画
    const statNumbers = document.querySelectorAll('.stat-number');
    const numberObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumber(entry.target);
                numberObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(number => {
        numberObserver.observe(number);
    });
    
    // 鼠标悬停效果
    const cards = document.querySelectorAll('.research-card, .publication-item, .contact-item');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// 数字计数动画
function animateNumber(element) {
    const target = parseInt(element.textContent);
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + '+';
    }, 16);
}

// 移动端菜单
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
        
        // 点击外部区域关闭菜单
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
        
        // 窗口大小改变时关闭菜单
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    }
}

// 页面加载完成后的初始化
window.addEventListener('load', function() {
    // 添加页面加载完成的类
    document.body.classList.add('loaded');
    
    // 预加载图片（如果有的话）
    preloadImages();
});

// 预加载图片
function preloadImages() {
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
        img.src = img.getAttribute('data-src');
        img.removeAttribute('data-src');
    });
}

// 滚动到顶部功能
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// 键盘导航支持
document.addEventListener('keydown', function(e) {
    // ESC键关闭移动端菜单
    if (e.key === 'Escape') {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        if (navMenu && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    }
});

// 窗口大小改变时的处理
window.addEventListener('resize', function() {
    // 如果窗口变大，关闭移动端菜单
    if (window.innerWidth > 768) {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        if (navMenu && hamburger) {
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    }
});

// 性能优化：防抖函数
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

// 搜索功能

// 回到顶部功能
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}


// 使用防抖优化滚动事件
const debouncedScrollHandler = debounce(function() {
    // 这里可以添加需要防抖的滚动处理逻辑
}, 10);

window.addEventListener('scroll', debouncedScrollHandler);


// 彩蛋功能
function initEasterEggs() {
    initKonamiCode();
    initClickCounter();
    initScrollCounter();
    initSecretMessages();
    initHoverEffects();
}

// Konami Code 彩蛋
function initKonamiCode() {
    let konamiCode = [];
    const konamiSequence = [
        'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
        'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
        'KeyB', 'KeyA'
    ];
    
    document.addEventListener('keydown', function(e) {
        konamiCode.push(e.code);
        if (konamiCode.length > konamiSequence.length) {
            konamiCode.shift();
        }
        
        if (konamiCode.join(',') === konamiSequence.join(',')) {
            showEasterEgg('konamiCode');
            konamiCode = [];
        }
    });
}

// 点击计数器彩蛋
function initClickCounter() {
    let clickCount = 0;
    
    document.addEventListener('click', function(e) {
        clickCount++;
        
        if (clickCount === 50) {
            document.getElementById('clickCount').textContent = clickCount;
            showEasterEgg('clickCounter');
        }
    });
}

// 滚动距离彩蛋
function initScrollCounter() {
    let maxScrollDistance = 0;
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.scrollY;
        if (currentScroll > maxScrollDistance) {
            maxScrollDistance = currentScroll;
        }
        
        if (maxScrollDistance > 3000 && maxScrollDistance % 1000 === 0) {
            document.getElementById('scrollDistance').textContent = maxScrollDistance;
            showEasterEgg('scrollMaster');
        }
    });
}

// 秘密消息彩蛋
function initSecretMessages() {
    const secretMessages = document.querySelectorAll('.secret-message');
    
    secretMessages.forEach(message => {
        message.addEventListener('click', function() {
            const msg = this.getAttribute('data-message');
            showNotification(msg, 'success');
        });
    });
}

// 特殊hover效果
function initHoverEffects() {
    // 在页面加载时随机放置秘密消息
    const secretMessages = document.querySelectorAll('.secret-message');
    secretMessages.forEach((message, index) => {
        const randomX = Math.random() * (window.innerWidth - 50);
        const randomY = Math.random() * (window.innerHeight - 50);
        message.style.left = randomX + 'px';
        message.style.top = randomY + 'px';
        message.style.position = 'fixed';
        message.style.opacity = '0.1';
        message.style.pointerEvents = 'auto';
    });
}

// 显示彩蛋
function showEasterEgg(eggId) {
    const egg = document.getElementById(eggId);
    if (egg) {
        egg.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

// 关闭彩蛋
function closeEasterEgg() {
    const eggs = document.querySelectorAll('.easter-egg');
    eggs.forEach(egg => {
        egg.classList.add('hidden');
    });
    document.body.style.overflow = 'auto';
}

// 世界地图交互功能
function initWorldMap() {
    const locationGroups = document.querySelectorAll('.location-group');
    const locationItems = document.querySelectorAll('.location-item');
    
    // 为每个地图点组添加点击事件
    locationGroups.forEach((group, index) => {
        group.setAttribute('tabindex', '0');
        group.setAttribute('role', 'button');
        group.setAttribute('aria-label', `Research location ${index + 1}`);
        
        group.addEventListener('click', function() {
            const locationClass = this.classList[1]; // 获取国家类名
            showLocationDetails(locationClass);
        });
        
        // 键盘导航支持
        group.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const locationClass = this.classList[1];
                showLocationDetails(locationClass);
            }
        });
        
        // 添加悬停效果
        group.addEventListener('mouseenter', function() {
            const locationClass = this.classList[1];
            highlightLocationItem(locationClass);
        });
        
        group.addEventListener('mouseleave', function() {
            clearLocationHighlights();
        });
    });
    
    // 为每个位置详情卡片添加悬停效果
    locationItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const locationClass = this.dataset.location;
            highlightMapLocation(locationClass);
        });
        
        item.addEventListener('mouseleave', function() {
            clearMapHighlights();
        });
    });
}

function showLocationDetails(locationClass) {
    // 滚动到项目部分
    const projectsSection = document.getElementById('projects');
    if (projectsSection) {
        projectsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    // 根据国家筛选项目（如果需要的话）
    filterProjectsByLocation(locationClass);
}

function highlightLocationItem(locationClass) {
    const locationItem = document.querySelector(`[data-location="${locationClass}"]`);
    if (locationItem) {
        locationItem.style.transform = 'translateY(-5px)';
        locationItem.style.background = 'var(--card-bg)';
        locationItem.style.borderColor = 'var(--primary-color)';
        locationItem.style.boxShadow = 'var(--shadow-hover)';
    }
}

function highlightMapLocation(locationClass) {
    const locationGroup = document.querySelector(`.location-group.${locationClass}`);
    if (locationGroup) {
        const researchLocation = locationGroup.querySelector('.research-location');
        const locationLabel = locationGroup.querySelector('.location-label');
        
        if (researchLocation) {
            researchLocation.style.fill = '#7ED321';
            researchLocation.style.stroke = '#4A90E2';
            researchLocation.style.strokeWidth = '3';
            researchLocation.style.transform = 'scale(1.2)';
        }
        
        if (locationLabel) {
            locationLabel.style.opacity = '1';
            locationLabel.style.transform = 'translateY(-5px)';
        }
    }
}

function clearLocationHighlights() {
    const locationItems = document.querySelectorAll('.location-item');
    locationItems.forEach(item => {
        item.style.transform = '';
        item.style.background = '';
        item.style.borderColor = '';
        item.style.boxShadow = '';
    });
}

function clearMapHighlights() {
    const locationGroups = document.querySelectorAll('.location-group');
    locationGroups.forEach(group => {
        const researchLocation = group.querySelector('.research-location');
        const locationLabel = group.querySelector('.location-label');
        
        if (researchLocation) {
            researchLocation.style.fill = '#4A90E2';
            researchLocation.style.stroke = '#fff';
            researchLocation.style.strokeWidth = '2';
            researchLocation.style.transform = 'scale(1)';
        }
        
        if (locationLabel) {
            locationLabel.style.opacity = '0';
            locationLabel.style.transform = 'translateY(0)';
        }
    });
}

function filterProjectsByLocation(locationClass) {
    // 根据国家筛选项目
    const projectCategories = document.querySelectorAll('.project-category');
    
    projectCategories.forEach(category => {
        const projects = category.querySelectorAll('.project-card');
        projects.forEach(project => {
            const description = project.querySelector('.project-description').textContent.toLowerCase();
            let shouldShow = false;
            
            switch(locationClass) {
                case 'china':
                    shouldShow = description.includes('zhejiang') || description.includes('china') || description.includes('microorganism');
                    break;
                case 'canada':
                    shouldShow = description.includes('ubc') || description.includes('vancouver') || description.includes('canada') || description.includes('surrey');
                    break;
                case 'finland':
                    shouldShow = description.includes('finland') || description.includes('lapland') || description.includes('kemi') || description.includes('doc');
                    break;
                case 'netherlands':
                    shouldShow = description.includes('wageningen') || description.includes('wur') || description.includes('marina') || description.includes('plastic');
                    break;
            }
            
            if (shouldShow) {
                project.style.opacity = '1';
                project.style.transform = 'scale(1)';
            } else {
                project.style.opacity = '0.3';
                project.style.transform = 'scale(0.95)';
            }
        });
    });
    
    // 3秒后恢复所有项目
    setTimeout(() => {
        const allProjects = document.querySelectorAll('.project-card');
        allProjects.forEach(project => {
            project.style.opacity = '1';
            project.style.transform = 'scale(1)';
        });
    }, 3000);
}

// 高级交互功能
function initAdvancedInteractions() {
    // 为所有卡片添加悬停效果
    const cards = document.querySelectorAll('.project-card, .education-item, .timeline-item, .location-item');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = 'var(--shadow-hover)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'var(--shadow-light)';
        });
    });
    
    // 为按钮添加点击波纹效果
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // 为浮动卡片添加点击交互
    const floatingCards = document.querySelectorAll('.floating-card');
    floatingCards.forEach(card => {
        card.addEventListener('click', function() {
            const cardType = this.classList[1].replace('-card', '');
            scrollToSection(cardType);
        });
    });
}

// 滚动动画
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // 观察所有需要动画的元素
    const animatedElements = document.querySelectorAll('.section-header, .project-card, .education-item, .timeline-item, .location-item');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// 加载状态
function initLoadingStates() {
    // 页面加载完成后的动画
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
        
        // 为hero元素添加延迟动画
        const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-description, .hero-buttons, .hero-quick-stats');
        heroElements.forEach((el, index) => {
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 200);
        });
    });
}

// 滚动到指定部分
function scrollToSection(sectionType) {
    let targetSection;
    
    switch(sectionType) {
        case 'research':
            targetSection = document.getElementById('projects');
            break;
        case 'education':
            targetSection = document.getElementById('education');
            break;
        case 'experience':
            targetSection = document.getElementById('experience');
            break;
        default:
            targetSection = document.getElementById('about');
    }
    
    if (targetSection) {
        targetSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 添加CSS动画类
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .animate-in {
        animation: slideInUp 0.6s ease-out forwards;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .loaded .hero-badge,
    .loaded .hero-title,
    .loaded .hero-subtitle,
    .loaded .hero-description,
    .loaded .hero-buttons,
    .loaded .hero-quick-stats {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .floating-card {
        cursor: pointer;
    }
    
    .floating-card:hover {
        animation-play-state: paused;
    }
`;
document.head.appendChild(style);

// 全局函数
window.closeEasterEgg = closeEasterEgg;
