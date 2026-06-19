/**
 * NeuroApt - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Add focus visible class for accessibility
    handleFocusVisible();
    
    // Add smooth scrolling
    enableSmoothScrolling();
    
    // Check for saved theme preference
    applyThemePreference();

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Test timer functionality (if on test page)
    if (document.querySelector('.test-timer')) {
        startTestTimer();
    }

    // Enhance form validation
    enhanceFormValidation();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    // Check if jQuery and Bootstrap are available
    if (typeof $ !== 'undefined' && typeof $.fn.tooltip !== 'undefined') {
        $('[data-toggle="tooltip"]').tooltip();
    }
}

/**
 * Handle focus visible for keyboard navigation
 */
function handleFocusVisible() {
    // Add .focus-visible class to elements when they receive focus via keyboard
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    // Remove the class when mouse is used
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
}

/**
 * Enable smooth scrolling for anchor links
 */
function enableSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Apply saved theme preference
 */
function applyThemePreference() {
    // Check for saved theme preference in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // Listen for theme changes and save to localStorage
    document.addEventListener('themeChanged', function(e) {
        if (e.detail && e.detail.theme) {
            localStorage.setItem('theme', e.detail.theme);
        }
    });
}

// Test timer functionality
function startTestTimer() {
    const timerElement = document.querySelector('.test-timer');
    let timeLeft = parseInt(timerElement.dataset.timeLimit) || 300; // Default 5 minutes
    
    const timerInterval = setInterval(function() {
        timeLeft--;
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            document.querySelector('form').submit(); // Auto-submit when time's up
        }
    }, 1000);
}

// Enhanced form validation
function enhanceFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Radio button enhancement for test options
document.addEventListener('click', function(e) {
    if (e.target.closest('.list-group-item')) {
        const item = e.target.closest('.list-group-item');
        const radio = item.querySelector('input[type="radio"]');
        
        if (radio) {
            radio.checked = true;
            
            // Remove active class from all items
            const items = item.parentElement.querySelectorAll('.list-group-item');
            items.forEach(i => i.classList.remove('active'));
            
            // Add active class to selected item
            item.classList.add('active');
        }
    }
}); 