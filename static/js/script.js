/* ===================================
   AgroVision - Main Application Logic
   Enhanced with performance optimization and error handling
   =================================== */

const AgroVisionApp = (function() {
    'use strict';

    // --- CONFIGURATION ---
    const Config = {
        storageKeys: {
            contrast: 'highContrast',
            lang: 'selectedLanguage'
        },
        dom: {
            offline: 'offlineIndicator',
            navbar: 'navbar',
            gauge: 'confidenceGauge'
        },
        defaults: {
            toastDuration: 3000,
            animationDelay: 100,
            gaugeAnimDuration: 1500
        }
    };

    // DOM Cache for performance
    const DOMCache = {
        elements: new Map(),
        get(id) {
            if (!this.elements.has(id)) {
                const el = document.getElementById(id);
                if (el) this.elements.set(id, el);
            }
            return this.elements.get(id);
        },
        clear() {
            this.elements.clear();
        }
    };

    // --- 1. THEME MANAGER ---
    const ThemeManager = {
        state: {
            highContrast: false
        },

        init() {
            try {
                const isContrast = localStorage.getItem(Config.storageKeys.contrast) === 'true';
                this.state.highContrast = isContrast;
                if (isContrast) {
                    document.body.classList.add('high-contrast');
                }
            } catch (error) {
                console.warn('Failed to load theme preference:', error);
            }
        },

        toggle() {
            try {
                const isEnabled = document.body.classList.toggle('high-contrast');
                this.state.highContrast = isEnabled;
                localStorage.setItem(Config.storageKeys.contrast, isEnabled);
                
                const message = isEnabled 
                    ? 'High Contrast Mode Enabled' 
                    : 'Standard Mode Enabled';
                UIManager.showToast(message, 'success');
                
                // Dispatch custom event for other components
                window.dispatchEvent(new CustomEvent('themeChanged', { 
                    detail: { highContrast: isEnabled } 
                }));
            } catch (error) {
                console.error('Failed to toggle theme:', error);
                UIManager.showToast('Failed to change theme', 'error');
            }
        }
    };

    // --- 2. NETWORK MANAGER ---
    const NetworkManager = {
        state: {
            online: true,
            connectionType: 'unknown'
        },

        init() {
            // Check initial state
            this.state.online = navigator.onLine;
            if (!this.state.online) {
                this.updateState(true);
            }

            // Listen for online/offline events
            window.addEventListener('offline', () => this.handleOffline());
            window.addEventListener('online', () => this.handleOnline());

            // Monitor connection type if available
            if ('connection' in navigator) {
                this.updateConnectionType();
                navigator.connection.addEventListener('change', () => {
                    this.updateConnectionType();
                });
            }
        },

        handleOffline() {
            this.state.online = false;
            this.updateState(true);
        },

        handleOnline() {
            this.state.online = true;
            this.updateState(false);
        },

        updateConnectionType() {
            if ('connection' in navigator && navigator.connection) {
                this.state.connectionType = navigator.connection.effectiveType || 'unknown';
            }
        },

        updateState(isOffline) {
            const indicator = DOMCache.get(Config.dom.offline);
            const navbar = DOMCache.get(Config.dom.navbar);

            requestAnimationFrame(() => {
                if (isOffline) {
                    indicator?.classList.add('show');
                    navbar?.classList.add('offline');
                    UIManager.showToast('You are currently offline', 'error');
                } else {
                    indicator?.classList.remove('show');
                    navbar?.classList.remove('offline');
                    UIManager.showToast('Connection restored', 'success');
                }
            });

            // Dispatch event for other components
            window.dispatchEvent(new CustomEvent('networkStatusChanged', {
                detail: { online: !isOffline, type: this.state.connectionType }
            }));
        },

        isOnline() {
            return this.state.online;
        }
    };

    // --- 3. VOICE MANAGER (TTS) ---
    const VoiceManager = {
        state: {
            speaking: false,
            voices: [],
            supported: 'speechSynthesis' in window
        },

        init() {
            if (!this.state.supported) return;
            
            const synth = window.speechSynthesis;
            
            // Preload voices
            const loadVoices = () => {
                this.state.voices = synth.getVoices();
            };

            if (synth.getVoices().length !== 0) {
                loadVoices();
            } else {
                synth.onvoiceschanged = loadVoices;
            }
        },

        speak(text) {
            if (!this.state.supported) {
                UIManager.showToast('Text-to-speech is not supported in this browser', 'error');
                return;
            }

            if (!text || typeof text !== 'string') {
                console.warn('Invalid text provided to speak()');
                return;
            }

            const synth = window.speechSynthesis;
            
            // Cancel any ongoing speech
            if (synth.speaking) {
                synth.cancel();
                this.state.speaking = false;
            }

            const utterance = new SpeechSynthesisUtterance(text.trim());
            
            // Set speech parameters
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            // Voice selection with fallback
            const setVoice = () => {
                try {
                    const voices = synth.getVoices();
                    if (voices.length === 0) return;

                    const currentLang = localStorage.getItem(Config.storageKeys.lang) || 'en';
                    const langMap = { 'en': 'en-US', 'hi': 'hi-IN', 'te': 'te-IN' };
                    const targetLocale = langMap[currentLang] || 'en-US';

                    // Find exact match or closest match
                    let selectedVoice = voices.find(v => v.lang === targetLocale);
                    
                    if (!selectedVoice) {
                        // Fallback to language family (e.g., 'en' for 'en-US')
                        const langBase = targetLocale.split('-')[0];
                        selectedVoice = voices.find(v => v.lang.startsWith(langBase));
                    }

                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                } catch (error) {
                    console.warn('Voice selection failed:', error);
                }

                // Event handlers
                utterance.onstart = () => {
                    this.state.speaking = true;
                };

                utterance.onend = () => {
                    this.state.speaking = false;
                };

                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event.error);
                    this.state.speaking = false;
                    if (event.error !== 'canceled') {
                        UIManager.showToast('Speech failed. Please try again.', 'error');
                    }
                };

                synth.speak(utterance);
            };

            if (synth.getVoices().length !== 0) {
                setVoice();
            } else {
                synth.onvoiceschanged = setVoice;
            }
        },

        stop() {
            if (this.state.supported && window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                this.state.speaking = false;
            }
        },

        isSpeaking() {
            return this.state.speaking;
        }
    };

    // --- 4. UI MANAGER ---
    const UIManager = {
        // Dynamic Gauge Animation with performance optimization
        drawGauge(percentage, elementId) {
            // Validate input
            if (typeof percentage !== 'number' || percentage < 0 || percentage > 100) {
                console.error('Invalid percentage for gauge:', percentage);
                return;
            }

            const container = DOMCache.get(elementId);
            if (!container) {
                console.warn(`Gauge container not found: ${elementId}`);
                return;
            }

            const radius = 54;
            const circumference = 2 * Math.PI * radius;
            
            // Render SVG structure
            container.innerHTML = `
                <svg width="120" height="120" class="gauge-svg">
                    <circle cx="60" cy="60" r="${radius}" fill="none" stroke="#e0e0e0" stroke-width="8"></circle>
                    <circle class="gauge-fill" cx="60" cy="60" r="${radius}" 
                            fill="none" stroke="var(--primary-color)" stroke-width="8"
                            stroke-dasharray="${circumference}" 
                            stroke-dashoffset="${circumference}"
                            stroke-linecap="round"
                            style="transform: rotate(-90deg); transform-origin: 50% 50%; transition: stroke-dashoffset 1.5s ease-out;">
                    </circle>
                </svg>
                <div class="confidence-value" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">0%</div>
            `;

            // Animate values
            setTimeout(() => {
                const fill = container.querySelector('.gauge-fill');
                const text = container.querySelector('.confidence-value');
                const offset = circumference - (percentage / 100) * circumference;
                
                if(fill) fill.style.strokeDashoffset = offset;
                
                // Count up animation
                let count = 0;
                const interval = setInterval(() => {
                    if (count >= percentage) clearInterval(interval);
                    else {
                        count++;
                        if(text) text.textContent = `${count}%`;
                    }
                }, 1000 / percentage);
            }, 100);
        },

        // Toast Notifications with queue management
        toastQueue: [],
        showingToast: false,

        showToast(message, type = 'info', duration = Config.defaults.toastDuration) {
            if (!message) return;

            this.toastQueue.push({ message, type, duration });
            this.processToastQueue();
        },

        processToastQueue() {
            if (this.showingToast || this.toastQueue.length === 0) return;

            this.showingToast = true;
            const { message, type, duration } = this.toastQueue.shift();
            
            const container = DOMCache.get('toast-container') || this.createToastContainer();
            const toast = document.createElement('div');
            
            toast.className = `toast ${type}`;
            const icons = { success: '✓', error: '⚠️', info: 'ℹ️' };
            
            // Sanitize message to prevent XSS
            const sanitizedMessage = message.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            
            toast.innerHTML = `
                <div class="toast-icon">${icons[type] || 'ℹ️'}</div>
                <div class="toast-msg">${sanitizedMessage}</div>
            `;

            container.appendChild(toast);

            // Trigger Animation with RAF for better performance
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    toast.classList.add('show');
                });
            });

            // Auto Remove with cleanup
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    toast.remove();
                    this.showingToast = false;
                    this.processToastQueue(); // Process next in queue
                }, 300);
            }, duration);
        },

        createToastContainer() {
            const div = document.createElement('div');
            div.id = 'toast-container';
            div.style.cssText = "position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;";
            document.body.appendChild(div);
            return div;
        },

        // Filter Pills Logic
        toggleFilter(element, category) {
            if(!element) return;
            const siblings = element.parentElement.querySelectorAll('.filter-pill');
            siblings.forEach(el => el.classList.remove('active'));
            element.classList.add('active');
            
            // Dispatch event for page-specific logic to handle
            window.dispatchEvent(new CustomEvent('agroFilter', { detail: { category } }));
        }
    };

    // --- INITIALIZATION ---
    function init() {
        try {
            // Initialize core modules
            ThemeManager.init();
            NetworkManager.init();
            VoiceManager.init();
            
            // Expose safe global functions for HTML onclick attributes
            window.toggleHighContrast = () => ThemeManager.toggle();
            window.speakText = (text) => VoiceManager.speak(text);
            window.toggleFilter = (element, category) => UIManager.toggleFilter(element, category);
            window.drawGauge = (percentage, elementId) => UIManager.drawGauge(percentage, elementId);
            window.showToast = (message, type, duration) => UIManager.showToast(message, type, duration);
            
            console.log('✓ AgroVision App Initialized Successfully');
            
            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('agroVisionReady'));
        } catch (error) {
            console.error('Failed to initialize AgroVision App:', error);
            // Show user-friendly error
            if (typeof UIManager !== 'undefined' && UIManager.showToast) {
                UIManager.showToast('App initialization failed. Please refresh the page.', 'error');
            }
        }
    }

    function cleanup() {
        // Clean up resources
        DOMCache.clear();
        VoiceManager.stop();
        console.log('AgroVision App cleaned up');
    }

    return { 
        init,
        cleanup,
        // Expose modules for testing/debugging
        _modules: { ThemeManager, NetworkManager, VoiceManager, UIManager }
    };
})();

// Start App when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AgroVisionApp.init);
} else {
    // DOM already loaded
    AgroVisionApp.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (AgroVisionApp.cleanup) AgroVisionApp.cleanup();
});