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
    initScrollEffects();
    initNameRotation();
});

// ========================================
// 滚动效果
// ========================================
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ========================================
// 名字自动切换
// ========================================
function initNameRotation() {
    const nameElement = document.querySelector('.name-text');
    if (!nameElement) return;
    
    const names = JSON.parse(nameElement.dataset.names);
    let currentIndex = 0;
    
    function rotateName() {
        // 淡出效果
        nameElement.classList.add('fade-out');
        
        setTimeout(() => {
            // 更新名字
            currentIndex = (currentIndex + 1) % names.length;
            nameElement.textContent = names[currentIndex];
            
            // 淡入效果
            nameElement.classList.remove('fade-out');
            nameElement.classList.add('fade-in');
            
            setTimeout(() => {
                nameElement.classList.remove('fade-in');
            }, 500);
        }, 500);
    }
    
    // 每3秒切换一次
    setInterval(rotateName, 3000);
}

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
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
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
        
        // 窗口大小改变时关闭菜单
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
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
    const locationGroups = document.querySelectorAll('.location-group');
    
    locationGroups.forEach(group => {
        // 添加点击事件
        group.addEventListener('click', function(e) {
            e.preventDefault();
            const locationName = this.classList[1];
            showLocationInfo(locationName);
        });
        
        // 添加键盘支持
        group.setAttribute('tabindex', '0');
        group.setAttribute('role', 'button');
        
        group.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const locationName = this.classList[1];
                showLocationInfo(locationName);
            }
        });
        
        // 悬停效果
        group.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.zIndex = '10';
        });
        
        group.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.zIndex = '1';
        });
    });
}

function showLocationInfo(locationName) {
    const locationData = {
        canada: {
            name: 'Vancouver, Canada',
            university: 'University of British Columbia',
            period: 'Sep 2021 - May 2024',
            research: 'Bachelor of Urban Forestry (Green Space Management)',
            details: 'Completed Bachelor\'s degree with GPA 83.7/100. Supervisor: Prof. Andrew Almas. Graduated with Honors. Focus on urban forestry, green space management, and environmental sustainability.'
        },
        netherlands: {
            name: 'Wageningen, Netherlands',
            university: 'Wageningen University & Research',
            period: 'Sep 2024 - Jun 2026',
            research: 'Master of Urban Environmental Management (Water System and Global Change)',
            details: 'Currently pursuing Master\'s degree. Supervisor: Prof. Maryna Strokal. Focus on water systems, global change, and sustainable urban development. Future thesis topic: water, urban, BGI, NBS (to be confirmed Sep 2025).'
        },
        finland: {
            name: 'Joensuu, Finland',
            university: 'Eastern Finland University',
            period: 'May 2025 - Sep 2025',
            research: 'Research Assistant (Internship)',
            details: 'Department of Environmental and Biological Sciences. Supervisor: Prof. Frank Berninger. Will conduct field samplings in Lapland including soil water collection, perform spectral measurements in boreal forest, and analyze field samples using GIS.'
        },
        china: {
            name: 'Zhejiang, China',
            university: 'Zhejiang Agriculture and Forestry University',
            period: 'Sep 2019 - Jun 2024',
            research: 'Bachelor of Forestry',
            details: 'Completed Bachelor\'s degree with GPA 87.7/100. Supervisors: Prof. Yeqing Ying & Prof. Wenhui Shi. State Key Laboratory of Subtropical Silviculture. Research on phosphorus-solubilizing microorganisms and plant-microbe interactions.'
        }
    };
    
    const data = locationData[locationName];
    if (data) {
        // 创建模态框显示详细信息
        showLocationModal(data);
    }
}

function showLocationModal(data) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'location-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${data.name}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="location-info">
                        <div class="info-item">
                            <strong>University:</strong> ${data.university}
                        </div>
                        <div class="info-item">
                            <strong>Period:</strong> ${data.period}
                        </div>
                        <div class="info-item">
                            <strong>Research Focus:</strong> ${data.research}
                        </div>
                        <div class="info-item">
                            <strong>Details:</strong> ${data.details}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .location-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-4);
        }
        
        .modal-overlay {
            background: rgba(0, 0, 0, 0.8);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }
        
        .modal-content {
            background: var(--bg-primary);
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-color);
            max-width: 500px;
            width: 100%;
            position: relative;
            z-index: 1001;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-6);
            border-bottom: 1px solid var(--border-color);
        }
        
        .modal-header h3 {
            color: var(--primary-color);
            font-size: var(--text-xl);
        }
        
        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: var(--text-2xl);
            cursor: pointer;
            padding: var(--space-2);
            line-height: 1;
        }
        
        .modal-body {
            padding: var(--space-6);
        }
        
        .location-info {
            display: flex;
            flex-direction: column;
            gap: var(--space-4);
        }
        
        .info-item {
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        .info-item strong {
            color: var(--text-primary);
            display: block;
            margin-bottom: var(--space-1);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // 关闭模态框
    const closeModal = () => {
        document.body.removeChild(modal);
        document.head.removeChild(style);
    };
    
    modal.querySelector('.modal-close').addEventListener('click', closeModal);
    modal.querySelector('.modal-overlay').addEventListener('click', closeModal);
    
    // ESC键关闭
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
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
            const inputs = form.querySelectorAll('input, textarea');
            const formData = {};
            let isValid = true;
            
            inputs.forEach(input => {
                const value = input.value.trim();
                formData[input.type || 'text'] = value;
                
                // 验证必填字段
                if (!value) {
                    input.style.borderColor = '#ef4444';
                    isValid = false;
                } else {
                    input.style.borderColor = '';
                }
                
                // 验证邮箱格式
                if (input.type === 'email' && value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        input.style.borderColor = '#ef4444';
                        isValid = false;
                    }
                }
            });
            
            if (!isValid) {
                showNotification('Please fill in all fields correctly.', 'error');
                return;
            }
            
            // 模拟发送
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            // 模拟网络延迟
            setTimeout(() => {
                showNotification('Thank you for your message! I will get back to you soon.', 'success');
                form.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                
                // 重置所有输入框样式
                inputs.forEach(input => {
                    input.style.borderColor = '';
                });
            }, 2000);
        });
        
        // 实时验证
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value.trim()) {
                    this.style.borderColor = '#22c55e';
                } else {
                    this.style.borderColor = '';
                }
            });
        });
    }
}

// 通知系统
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: var(--space-4) var(--space-6);
            border-radius: var(--radius-lg);
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .notification-success {
            background: #22c55e;
        }
        
        .notification-error {
            background: #ef4444;
        }
        
        .notification-info {
            background: var(--primary-color);
        }
        
        .notification.show {
            transform: translateX(0);
        }
    `;
    
    if (!document.querySelector('#notification-styles')) {
        style.id = 'notification-styles';
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => notification.classList.add('show'), 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
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