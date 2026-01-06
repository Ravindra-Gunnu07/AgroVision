/* ===================================
   AgroVision - Advanced Animations & Effects
   Performance optimized with robust error handling
   =================================== */

const AgroVisionAnimations = (function() {
    'use strict';

    // Configuration
    const Config = {
        debounceDelay: 300,
        animationObserverOptions: {
            root: null,
            threshold: 0.15,
            rootMargin: '0px 0px -100px 0px'
        },
        parallax: {
            enabled: window.innerWidth > 768,
            factor: 0.5
        },
        form: {
            maxFileSize: 5 * 1024 * 1024, // 5MB
            allowedImageTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        },
        greeting: {
            updateInterval: 60000, // Update every minute
            transitions: { morning: 5, afternoon: 12, evening: 17, night: 21 }
        }
    };

    // Performance monitoring utility
    const Performance = {
        metrics: new Map(),
        mark(name) {
            if ('performance' in window && performance.mark) {
                performance.mark(`${name}-start`);
            }
            this.metrics.set(name, performance.now());
        },
        measure(name) {
            const start = this.metrics.get(name);
            if (start) {
                const duration = performance.now() - start;
                if (performance.measure) {
                    try {
                        performance.measure(name, `${name}-start`);
                    } catch (e) {}
                }
                this.metrics.delete(name);
                return duration;
            }
        }
    };

    // DOM Cache for better performance
    const DOMCache = {
        elements: new Map(),
        get(selector) {
            if (!this.elements.has(selector)) {
                const el = document.querySelector(selector);
                if (el) this.elements.set(selector, el);
            }
            return this.elements.get(selector);
        },
        clear() {
            this.elements.clear();
        }
    };

    // --- 1. ANIMATION CONTROLLER ---
    const AnimationController = {
        observer: null,
        rafId: null,
        scrollY: 0,

        init() {
            try {
                this.setupScrollAnimations();
                if (Config.parallax.enabled) {
                    this.setupParallax();
                }
                this.setupSmoothScroll();
                
                // Re-initialize parallax on resize
                window.addEventListener('resize', this.debounce(() => {
                    Config.parallax.enabled = window.innerWidth > 768;
                    if (this.rafId) {
                        cancelAnimationFrame(this.rafId);
                        this.rafId = null;
                    }
                    if (Config.parallax.enabled) {
                        this.setupParallax();
                    }
                }, 250));
            } catch (error) {
                console.error('AnimationController init failed:', error);
            }
        },

        setupScrollAnimations() {
            if (!('IntersectionObserver' in window)) {
                console.warn('IntersectionObserver not supported');
                return;
            }

            Performance.mark('scroll-observer-init');

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const delay = entry.target.dataset.animDelay || 0;
                        
                        setTimeout(() => {
                            entry.target.classList.add('animate');
                        }, parseInt(delay));

                        // Stop observing after animation triggers
                        this.observer.unobserve(entry.target);
                    }
                });
            }, Config.animationObserverOptions);

            // Observe all animated elements
            document.querySelectorAll('.fade-in, .slide-up, .scale-in, [data-animate]')
                .forEach(el => this.observer.observe(el));

            Performance.measure('scroll-observer-init');
        },

        setupParallax() {
            const parallaxElements = document.querySelectorAll('.parallax');
            if (parallaxElements.length === 0) return;

            const updateParallax = () => {
                this.scrollY = window.pageYOffset;
                
                parallaxElements.forEach(el => {
                    if (this.isInViewport(el)) {
                        const speed = parseFloat(el.dataset.speed) || Config.parallax.factor;
                        const yPos = -(this.scrollY * speed);
                        el.style.transform = `translate3d(0, ${yPos}px, 0)`;
                    }
                });

                this.rafId = requestAnimationFrame(updateParallax);
            };

            this.rafId = requestAnimationFrame(updateParallax);
        },

        setupSmoothScroll() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const targetId = anchor.getAttribute('href');
                    if (targetId === '#') return;

                    const target = document.querySelector(targetId);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            });
        },

        isInViewport(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top < window.innerHeight &&
                rect.bottom > 0
            );
        },

        debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },

        cleanup() {
            if (this.observer) {
                this.observer.disconnect();
            }
            if (this.rafId) {
                cancelAnimationFrame(this.rafId);
            }
        }
    };

    // --- 2. FORM HANDLER ---
    const FormHandler = {
        init() {
            this.setupImagePreview();
            this.setupFormValidation();
        },

        setupImagePreview() {
            const imageInput = document.getElementById('imageInput');
            const preview = document.getElementById('imagePreview');
            
            if (!imageInput || !preview) return;

            imageInput.addEventListener('change', (e) => {
                this.handleImageSelection(e, preview);
            });

            // Drag and drop support
            this.setupDragAndDrop(imageInput, preview);
        },

        handleImageSelection(event, preview) {
            const file = event.target.files[0];
            
            if (!file) {
                this.clearPreview(preview);
                return;
            }

            // Validate file
            const validation = this.validateImageFile(file);
            if (!validation.valid) {
                this.showValidationError(validation.error);
                this.clearPreview(preview);
                event.target.value = '';
                return;
            }

            // Show preview with loading state
            this.showImagePreview(file, preview);
        },

        validateImageFile(file) {
            // Check file type
            if (!Config.form.allowedImageTypes.includes(file.type)) {
                return {
                    valid: false,
                    error: `Invalid file type. Allowed: ${Config.form.allowedImageTypes.map(t => t.split('/')[1]).join(', ')}`
                };
            }

            // Check file size
            if (file.size > Config.form.maxFileSize) {
                const maxSizeMB = (Config.form.maxFileSize / (1024 * 1024)).toFixed(1);
                return {
                    valid: false,
                    error: `File too large. Maximum size: ${maxSizeMB}MB`
                };
            }

            return { valid: true };
        },

        showImagePreview(file, preview) {
            const reader = new FileReader();
            
            preview.innerHTML = '<div class="loading">Loading preview...</div>';
            preview.style.display = 'block';

            reader.onload = (e) => {
                const img = new Image();
                
                img.onload = () => {
                    // Create preview with image info
                    const fileSize = (file.size / 1024).toFixed(1);
                    preview.innerHTML = `
                        <div class="image-preview-container">
                            <img src="${e.target.result}" alt="Preview" style="max-width:100%; border-radius:10px;">
                            <div class="image-info" style="margin-top:10px; font-size:0.9rem; color:#666;">
                                <span><strong>File:</strong> ${file.name}</span><br>
                                <span><strong>Size:</strong> ${fileSize} KB</span><br>
                                <span><strong>Dimensions:</strong> ${img.width} × ${img.height}px</span>
                            </div>
                        </div>
                    `;
                };

                img.onerror = () => {
                    this.showValidationError('Failed to load image preview');
                    this.clearPreview(preview);
                };

                img.src = e.target.result;
            };

            reader.onerror = () => {
                this.showValidationError('Failed to read file');
                this.clearPreview(preview);
            };

            reader.readAsDataURL(file);
        },

        clearPreview(preview) {
            preview.style.display = 'none';
            preview.innerHTML = '';
        },

        showValidationError(message) {
            if (window.AgroVisionApp && window.AgroVisionApp._modules.UIManager) {
                window.AgroVisionApp._modules.UIManager.showToast(message, 'error');
            } else {
                alert(message);
            }
        },

        setupDragAndDrop(input, preview) {
            const dropZone = input.closest('.upload-section') || input.parentElement;
            
            if (!dropZone) return;

            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    dropZone.classList.add('drag-over');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    dropZone.classList.remove('drag-over');
                });
            });

            dropZone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    const event = new Event('change', { bubbles: true });
                    input.dispatchEvent(event);
                }
            });
        },

        setupFormValidation() {
            const forms = document.querySelectorAll('form[data-validate]');
            
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!this.validateForm(form)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                });
            });
        },

        validateForm(form) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    this.showFieldError(field, 'This field is required');
                } else {
                    field.classList.remove('error');
                    this.clearFieldError(field);
                }
            });

            return isValid;
        },

        showFieldError(field, message) {
            const existingError = field.parentElement.querySelector('.field-error');
            if (existingError) {
                existingError.textContent = message;
                return;
            }

            const errorMsg = document.createElement('div');
            errorMsg.className = 'field-error';
            errorMsg.textContent = message;
            errorMsg.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 5px;';
            field.parentElement.appendChild(errorMsg);
        },

        clearFieldError(field) {
            const error = field.parentElement.querySelector('.field-error');
            if (error) error.remove();
        }
    };

    // --- 3. APP FEATURES ---
    const AppFeatures = {
        searchTimeout: null,
        greetingInterval: null,

        init() {
            this.setupSearch();
            this.setupGreeting();
        },

        setupSearch() {
            const searchInput = document.getElementById('plantSearch');
            if (!searchInput) return;

            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        },

        handleSearch(query) {
            clearTimeout(this.searchTimeout);

            this.searchTimeout = setTimeout(() => {
                if (query.length < 2) return;

                Performance.mark('search-execution');
                
                // Placeholder for actual search logic
                console.log('Searching for:', query);
                
                Performance.measure('search-execution');
            }, Config.debounceDelay);
        },

        setupGreeting() {
            this.updateGreeting();
            
            // Update greeting every minute
            this.greetingInterval = setInterval(() => {
                this.updateGreeting();
            }, Config.greeting.updateInterval);
        },

        updateGreeting() {
            const greetingEl = document.querySelector('[data-greeting]');
            if (!greetingEl) return;

            const hour = new Date().getHours();
            const { transitions } = Config.greeting;
            
            let greeting = 'Good Night';
            let icon = '🌙';

            if (hour >= transitions.morning && hour < transitions.afternoon) {
                greeting = 'Good Morning';
                icon = '🌅';
            } else if (hour >= transitions.afternoon && hour < transitions.evening) {
                greeting = 'Good Afternoon';
                icon = '☀️';
            } else if (hour >= transitions.evening && hour < transitions.night) {
                greeting = 'Good Evening';
                icon = '🌆';
            }

            greetingEl.innerHTML = `<span class="greeting-icon">${icon}</span> ${greeting}`;
        },

        cleanup() {
            if (this.searchTimeout) clearTimeout(this.searchTimeout);
            if (this.greetingInterval) clearInterval(this.greetingInterval);
        }
    };

    // --- INITIALIZATION ---
    function init() {
        try {
            Performance.mark('animations-init');
            
            AnimationController.init();
            FormHandler.init();
            AppFeatures.init();
            
            Performance.measure('animations-init');
            console.log('✓ AgroVision Animations Initialized');

            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('animationsReady'));
        } catch (error) {
            console.error('Failed to initialize animations:', error);
        }
    }

    function cleanup() {
        AnimationController.cleanup();
        AppFeatures.cleanup();
        DOMCache.clear();
        console.log('AgroVision Animations cleaned up');
    }

    // Public API
    return {
        init,
        cleanup,
        Performance,
        // Expose modules for testing/debugging
        _modules: { AnimationController, FormHandler, AppFeatures }
    };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AgroVisionAnimations.init);
} else {
    AgroVisionAnimations.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (AgroVisionAnimations.cleanup) AgroVisionAnimations.cleanup();
});
