// 高级主题管理器
class ThemeManager {
    constructor() {
        this.themes = {
            'light': {
                name: 'Light',
                bg: '#F9FAFB',
                card: '#FFFFFF',
                accent: '#8ED7F8',
                accent2: '#64B1D9',
                text: '#2E3440',
                textMute: '#59606F',
                outline: '#D2D6DC'
            },
            'dark': {
                name: 'Soft Slate',
                bg: '#12161C',
                card: '#1A1F27',
                accent: '#4E9CFF',
                accent2: '#7AB5FF',
                text: '#E8ECEF',
                textMute: '#8F9CA8',
                outline: '#333C47'
            },
            'moss-night': {
                name: 'Moss Night',
                bg: '#0E1110',
                card: '#171A18',
                accent: '#5FB97C',
                accent2: '#9FD8B0',
                text: '#E5EDE6',
                textMute: '#9BAC9F',
                outline: '#2B322D'
            },
            'latte-dark': {
                name: 'Latte Dark',
                bg: '#1B1A17',
                card: '#242321',
                accent: '#D0A962',
                accent2: '#E1C792',
                text: '#F5F4EF',
                textMute: '#B8B2A7',
                outline: '#3A3732'
            }
        };
        
        this.currentTheme = 'light';
        this.init();
    }
    
    init() {
        this.loadSavedTheme();
        this.setupEventListeners();
        this.setupSystemThemeDetection();
    }
    
    loadSavedTheme() {
        const saved = localStorage.getItem('waxinci-theme');
        if (saved && this.themes[saved]) {
            this.setTheme(saved);
        } else {
            // 如果没有保存的主题，设置默认的浅色主题
            this.setTheme('light');
        }
    }
    
    setTheme(themeId) {
        if (!this.themes[themeId]) return;
        
        this.currentTheme = themeId;
        const theme = this.themes[themeId];
        
        // 方法1：使用CSS变量（推荐）
        document.body.setAttribute('data-theme', themeId);
        
        // 方法2：动态设置CSS变量（可选）
        this.applyThemeVariables(theme);
        
        // 更新按钮状态
        this.updateButtonStates();
        
        // 保存偏好
        localStorage.setItem('waxinci-theme', themeId);
        
        // 触发主题变化事件
        this.dispatchThemeChangeEvent(themeId, theme);
    }
    
    applyThemeVariables(theme) {
        const root = document.documentElement;
        Object.entries(theme).forEach(([key, value]) => {
            if (key !== 'name') {
                const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase();
                root.style.setProperty(`--${cssVar}`, value);
            }
        });
    }
    
    updateButtonStates() {
        // 按钮状态通过CSS的data-theme属性自动更新
        // 这里预留空间用于额外的状态更新逻辑
    }
    
    setupEventListeners() {
        // 单按钮切换
        document.addEventListener('click', (e) => {
            if (e.target.id === 'themeToggle' || e.target.closest('#themeToggle')) {
                this.toggleTheme();
            }
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }
    
    setupSystemThemeDetection() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                if (!localStorage.getItem('waxinci-theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
    
    toggleTheme() {
        // 在light和dark之间切换
        const nextTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(nextTheme);
    }

    cycleTheme() {
        // 保留原有的循环方法，但改为调用toggleTheme
        this.toggleTheme();
    }
    
    dispatchThemeChangeEvent(themeId, theme) {
        const event = new CustomEvent('themeChange', {
            detail: { themeId, theme }
        });
        document.dispatchEvent(event);
    }
    
    // 一键全局改色函数
    createCustomTheme(colors) {
        const customTheme = {
            name: 'Custom',
            bg: colors.bg || '#12161C',
            card: colors.card || '#1A1F27',
            accent: colors.accent || '#4E9CFF',
            accent2: colors.accent2 || '#7AB5FF',
            text: colors.text || '#E8ECEF',
            textMute: colors.textMute || '#8F9CA8',
            outline: colors.outline || '#333C47'
        };
        
        this.themes['custom'] = customTheme;
        this.setTheme('custom');
        
        return customTheme;
    }
}

// 可选功能模块
class OptionalFeatures {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupSparklines();
        this.setupTooltips();
        this.setupAnimations();
    }
    
    // 流量图/趋势线
    setupSparklines() {
        // 为每个卡片添加简单的趋势线
        const addSparkline = (card, data) => {
            const sparkline = document.createElement('div');
            sparkline.className = 'sparkline';
            sparkline.innerHTML = this.generateSparklineHTML(data);
            card.appendChild(sparkline);
        };
        
        // 监听卡片创建事件
        document.addEventListener('cardCreated', (e) => {
            const { card, data } = e.detail;
            addSparkline(card, data);
        });
    }
    
    generateSparklineHTML(data) {
        const points = data.rising.slice(0, 10).map((item, index) => {
            const x = (index / 9) * 100;
            const y = 100 - (item.value / 500) * 100;
            return `${x},${y}`;
        }).join(' ');
        
        return `
            <div class="sparkline-container">
                <svg width="100%" height="24" viewBox="0 0 100 100" class="sparkline-svg">
                    <polyline
                        points="${points}"
                        fill="none"
                        stroke="var(--accent)"
                        stroke-width="2"
                        opacity="0.6"
                    />
                </svg>
            </div>
        `;
    }
    
    // 增强工具提示
    setupTooltips() {
        const style = document.createElement('style');
        style.textContent = `
            .enhanced-tooltip {
                position: relative;
                cursor: help;
            }
            
            .enhanced-tooltip::before {
                content: attr(data-tooltip);
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: var(--text);
                color: var(--card);
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity .2s ease;
                z-index: 1000;
                box-shadow: var(--shadow-lg);
            }
            
            .enhanced-tooltip:hover::before {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    }
    
    // 微交互动画
    setupAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            .card {
                animation: fadeInUp 0.6s ease-out;
            }
            
            .card:nth-child(odd) {
                animation-delay: 0.1s;
            }
            
            .card:nth-child(even) {
                animation-delay: 0.2s;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .progress {
                animation: progressFill 1s ease-out;
            }
            
            @keyframes progressFill {
                from {
                    width: 0;
                }
                to {
                    width: var(--ratio);
                }
            }
            
            .sparkline-container {
                margin-top: 12px;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }
            
            .card:hover .sparkline-container {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    }
}

// 确保DOM加载完成后再初始化
document.addEventListener('DOMContentLoaded', () => {
    const themeManager = new ThemeManager();
    const optionalFeatures = new OptionalFeatures();
    
    // 导出供全局使用
    window.ThemeManager = ThemeManager;
    window.themeManager = themeManager;
    window.optionalFeatures = optionalFeatures;
    
    // 便捷函数
    window.setTheme = (colors) => themeManager.createCustomTheme(colors);
    
    // 预设主题切换函数
    window.switchToMossNight = () => {
        themeManager.setTheme('moss-night');
    };
    
    window.switchToLatteDark = () => {
        themeManager.setTheme('latte-dark');
    };
    
    window.switchToSoftSlate = () => {
        themeManager.setTheme('dark');
    };
}); 