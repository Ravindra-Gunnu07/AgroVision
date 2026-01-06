/**
 * AgroVision Enhanced Utilities
 * Handles Accessibility, UI Enhancements, and User Preferences
 * Optimized with error handling and performance improvements
 */

const AgroVisionUtils = (function() {
    'use strict';

    // Configuration
    const Config = {
        keys: {
            highContrast: 'highContrast',
            lang: 'selectedLanguage',
            preferences: 'userPreferences'
        },
        selectors: {
            offline: 'offlineIndicator',
            navbar: 'navbar',
            greeting: 'dynamicGreeting',
            gaugeContainer: 'confidenceGauge'
        },
        greeting: {
            updateInterval: 60000,
            timeRanges: {
                morning: { start: 5, end: 12, text: 'Good Morning', icon: '🌅' },
                afternoon: { start: 12, end: 17, text: 'Good Afternoon', icon: '☀️' },
                evening: { start: 17, end: 21, text: 'Good Evening', icon: '🌆' },
                night: { start: 21, end: 5, text: 'Good Night', icon: '🌙' }
            }
        }
    };

    // State management
    const State = {
        preferences: null,
        greetingInterval: null,
        
        loadPreferences() {
            try {
                const stored = localStorage.getItem(Config.keys.preferences);
                this.preferences = stored ? JSON.parse(stored) : {};
            } catch (error) {
                console.warn('Failed to load preferences:', error);
                this.preferences = {};
            }
        },

        savePreferences() {
            try {
                localStorage.setItem(Config.keys.preferences, JSON.stringify(this.preferences));
            } catch (error) {
                console.error('Failed to save preferences:', error);
            }
        },

        setPreference(key, value) {
            this.preferences[key] = value;
            this.savePreferences();
        },

        getPreference(key, defaultValue = null) {
            return this.preferences[key] !== undefined ? this.preferences[key] : defaultValue;
        }
    };

    // --- 1. ACCESSIBILITY MODULE ---
    const Accessibility = {
        state: {
            highContrast: false,
            speechSupported: 'speechSynthesis' in window
        },

        init() {
            try {
                State.loadPreferences();
                
                // Load high contrast preference
                const isContrast = localStorage.getItem(Config.keys.highContrast) === 'true';
                this.state.highContrast = isContrast;
                
                if (isContrast) {
                    document.body.classList.add('high-contrast');
                }

                // Setup keyboard shortcuts
                this.setupKeyboardShortcuts();
                
                console.log('✓ Accessibility module initialized');
            } catch (error) {
                console.error('Accessibility init failed:', error);
            }
        },

        toggleHighContrast() {
            try {
                const isEnabled = document.body.classList.toggle('high-contrast');
                this.state.highContrast = isEnabled;
                localStorage.setItem(Config.keys.highContrast, isEnabled);
                State.setPreference('highContrast', isEnabled);
                
                const message = isEnabled ? 'High Contrast Enabled' : 'High Contrast Disabled';
                this.announceToScreenReader(message);
                
                // Show visual feedback
                if (window.AgroVisionApp && window.AgroVisionApp._modules.UIManager) {
                    window.AgroVisionApp._modules.UIManager.showToast(message, 'success');
                }

                // Dispatch event for other components
                window.dispatchEvent(new CustomEvent('accessibilityChanged', {
                    detail: { highContrast: isEnabled }
                }));
            } catch (error) {
                console.error('Failed to toggle high contrast:', error);
            }
        },

        speakText(text) {
            if (!this.state.speechSupported) {
                this.showSpeechNotSupported();
                return;
            }

            if (!text || typeof text !== 'string' || text.trim() === '') {
                console.warn('Invalid text provided for speech synthesis');
                return;
            }

            const synth = window.speechSynthesis;
            
            // Cancel existing speech
            if (synth.speaking) {
                synth.cancel();
            }

            const utterance = new SpeechSynthesisUtterance(text.trim());
            
            // Configure speech parameters
            utterance.rate = State.getPreference('speechRate', 0.9);
            utterance.pitch = State.getPreference('speechPitch', 1.0);
            utterance.volume = State.getPreference('speechVolume', 1.0);

            // Voice selection with error handling
            this.selectVoice(utterance, synth);

            // Event handlers
            utterance.onstart = () => {
                console.log('Speech started');
            };

            utterance.onend = () => {
                console.log('Speech completed');
            };

            utterance.onerror = (event) => {
                if (event.error !== 'canceled') {
                    console.error('Speech synthesis error:', event.error);
                    this.showSpeechError();
                }
            };

            synth.speak(utterance);
        },

        selectVoice(utterance, synth) {
            const setVoice = () => {
                try {
                    const voices = synth.getVoices();
                    if (voices.length === 0) return;

                    const prefLang = localStorage.getItem(Config.keys.lang) || 'en';
                    
                    // Map language codes to full locale codes
                    const langMap = {
                        'hi': 'hi-IN',
                        'te': 'te-IN',
                        'en': 'en-US'
                    };
                    
                    const targetLang = langMap[prefLang] || 'en-US';

                    // Find exact match or language family match
                    let selectedVoice = voices.find(v => v.lang === targetLang);
                    
                    if (!selectedVoice) {
                        const langBase = targetLang.split('-')[0];
                        selectedVoice = voices.find(v => v.lang.startsWith(langBase));
                    }

                    // Prefer local voices for better quality
                    if (selectedVoice) {
                        utterance.voice = selectedVoice;
                    }
                } catch (error) {
                    console.warn('Voice selection failed:', error);
                }
            };

            if (synth.getVoices().length !== 0) {
                setVoice();
            } else {
                synth.onvoiceschanged = setVoice;
            }
        },

        showSpeechNotSupported() {
            const message = 'Text-to-speech is not supported in this browser.';
            if (window.AgroVisionApp && window.AgroVisionApp._modules.UIManager) {
                window.AgroVisionApp._modules.UIManager.showToast(message, 'error');
            } else {
                alert(message);
            }
        },

        showSpeechError() {
            if (window.AgroVisionApp && window.AgroVisionApp._modules.UIManager) {
                window.AgroVisionApp._modules.UIManager.showToast('Speech failed. Please try again.', 'error');
            }
        },

        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Alt + C: Toggle high contrast
                if (e.altKey && e.key === 'c') {
                    e.preventDefault();
                    this.toggleHighContrast();
                }

                // Alt + S: Stop speech
                if (e.altKey && e.key === 's') {
                    e.preventDefault();
                    if (window.speechSynthesis && window.speechSynthesis.speaking) {
                        window.speechSynthesis.cancel();
                    }
                }
            });
        },

        announceToScreenReader(message) {
            // Create live region for screen readers
            let liveRegion = document.getElementById('sr-live-region');
            
            if (!liveRegion) {
                liveRegion = document.createElement('div');
                liveRegion.id = 'sr-live-region';
                liveRegion.setAttribute('aria-live', 'polite');
                liveRegion.setAttribute('aria-atomic', 'true');
                liveRegion.style.cssText = `
                    position: absolute;
                    left: -10000px;
                    width: 1px;
                    height: 1px;
                    overflow: hidden;
                `;
                document.body.appendChild(liveRegion);
            }

            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    };

    // --- 2. UI ENHANCEMENTS MODULE ---
    const UI = {
        init() {
            try {
                this.updateGreeting();
                this.setupGreetingUpdates();
                console.log('✓ UI enhancements initialized');
            } catch (error) {
                console.error('UI init failed:', error);
            }
        },

        updateGreeting() {
            const greetingEl = document.getElementById(Config.selectors.greeting) || 
                              document.querySelector('[data-greeting]');
            
            if (!greetingEl) return;

            const hour = new Date().getHours();
            const { timeRanges } = Config.greeting;
            
            let greetingData = timeRanges.night; // Default

            if (hour >= timeRanges.morning.start && hour < timeRanges.morning.end) {
                greetingData = timeRanges.morning;
            } else if (hour >= timeRanges.afternoon.start && hour < timeRanges.afternoon.end) {
                greetingData = timeRanges.afternoon;
            } else if (hour >= timeRanges.evening.start && hour < timeRanges.evening.end) {
                greetingData = timeRanges.evening;
            }

            greetingEl.innerHTML = `
                <span class="greeting-icon" role="img" aria-label="${greetingData.text}">${greetingData.icon}</span>
                <span class="greeting-text">${greetingData.text}</span>
            `;
        },

        setupGreetingUpdates() {
            // Update greeting every minute
            State.greetingInterval = setInterval(() => {
                this.updateGreeting();
            }, Config.greeting.updateInterval);
        },

        toggleFilter(element, category) {
            if (!element || !category) return;

            try {
                // Toggle active state
                const isActive = element.classList.toggle('active');
                
                // Show/hide related content
                const items = document.querySelectorAll(`[data-category="${category}"]`);
                
                items.forEach(item => {
                    if (isActive) {
                        item.style.display = 'block';
                        item.classList.add('fade-in');
                    } else {
                        item.style.display = 'none';
                        item.classList.remove('fade-in');
                    }
                });

                // Announce to screen readers
                Accessibility.announceToScreenReader(
                    `${category} filter ${isActive ? 'activated' : 'deactivated'}`
                );
            } catch (error) {
                console.error('Filter toggle failed:', error);
            }
        },

        drawGauge(percentage, elementId) {
            // Validate inputs
            if (typeof percentage !== 'number' || percentage < 0 || percentage > 100) {
                console.error('Invalid percentage for gauge:', percentage);
                return;
            }

            const container = document.getElementById(elementId);
            if (!container) {
                console.warn(`Gauge container not found: ${elementId}`);
                return;
            }

            const radius = 54;
            const circumference = 2 * Math.PI * radius;
            const strokeWidth = 8;
            
            // Determine color based on confidence level
            let color = '#ef4444'; // Red (low)
            if (percentage >= 70) color = '#10b981'; // Green (high)
            else if (percentage >= 50) color = '#f59e0b'; // Yellow (medium)

            // Create SVG structure
            container.innerHTML = `
                <svg width="140" height="140" viewBox="0 0 140 140" class="gauge-svg" role="img" aria-label="Confidence: ${percentage}%">
                    <circle cx="70" cy="70" r="${radius}" 
                            fill="none" 
                            stroke="#e5e7eb" 
                            stroke-width="${strokeWidth}"/>
                    <circle cx="70" cy="70" r="${radius}" 
                            fill="none" 
                            stroke="${color}" 
                            stroke-width="${strokeWidth}" 
                            stroke-dasharray="${circumference}" 
                            stroke-dashoffset="${circumference}" 
                            stroke-linecap="round" 
                            transform="rotate(-90 70 70)" 
                            class="gauge-progress" 
                            data-target="${circumference * (1 - percentage / 100)}"/>
                    <text x="70" y="70" 
                          text-anchor="middle" 
                          dominant-baseline="middle" 
                          font-size="24" 
                          font-weight="bold" 
                          fill="currentColor" 
                          class="gauge-text">${percentage}%</text>
                </svg>
            `;

            // Animate gauge using requestAnimationFrame
            this.animateGauge(container.querySelector('.gauge-progress'), circumference, percentage);
        },

        animateGauge(circle, circumference, targetPercentage) {
            const targetOffset = circumference * (1 - targetPercentage / 100);
            const startOffset = circumference;
            const duration = 1500; // Animation duration in ms
            const startTime = performance.now();

            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function (ease-out cubic)
                const eased = 1 - Math.pow(1 - progress, 3);
                
                const currentOffset = startOffset - (startOffset - targetOffset) * eased;
                circle.style.strokeDashoffset = currentOffset;

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };

            requestAnimationFrame(animate);
        },

        cleanup() {
            if (State.greetingInterval) {
                clearInterval(State.greetingInterval);
                State.greetingInterval = null;
            }
        }
    };

    // --- INITIALIZATION ---
    function init() {
        try {
            Accessibility.init();
            UI.init();
            
            // Expose functions globally for HTML onclick attributes
            window.toggleHighContrast = () => Accessibility.toggleHighContrast();
            window.speakText = (text) => Accessibility.speakText(text);
            window.toggleFilter = (el, cat) => UI.toggleFilter(el, cat);
            window.drawGauge = (percent, id) => UI.drawGauge(percent, id);
            
            console.log('✓ AgroVision Utils Initialized');
            
            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('utilsReady'));
        } catch (error) {
            console.error('Failed to initialize AgroVision Utils:', error);
        }
    }

    function cleanup() {
        UI.cleanup();
        console.log('AgroVision Utils cleaned up');
    }

    // Public API
    return {
        init,
        cleanup,
        State,
        // Expose modules
        _modules: { Accessibility, UI }
    };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AgroVisionUtils.init);
} else {
    AgroVisionUtils.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (AgroVisionUtils.cleanup) AgroVisionUtils.cleanup();
});
