// HiramAbiff Dashboard JavaScript

// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('HiramAbiff Dashboard initialized');
    
    // Initialize animations for cards
    initializeCardAnimations();
    
    // Add copy functionality for wallet addresses
    initializeWalletAddressCopy();
    
    // Add tooltips
    initializeTooltips();
});

// Function to initialize card animations
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });
}

// Function to add copy functionality for wallet addresses
function initializeWalletAddressCopy() {
    const walletAddresses = document.querySelectorAll('.wallet-address');
    
    walletAddresses.forEach(address => {
        address.addEventListener('click', function() {
            const textToCopy = this.innerText;
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    // Create and show a temporary tooltip
                    const tooltip = document.createElement('div');
                    tooltip.textContent = 'Copied!';
                    tooltip.style.position = 'absolute';
                    tooltip.style.backgroundColor = 'var(--accent-color)';
                    tooltip.style.color = 'black';
                    tooltip.style.padding = '5px 10px';
                    tooltip.style.borderRadius = '4px';
                    tooltip.style.fontSize = '12px';
                    tooltip.style.fontWeight = 'bold';
                    tooltip.style.zIndex = '1000';
                    tooltip.style.opacity = '0';
                    tooltip.style.transition = 'opacity 0.3s ease';
                    
                    // Position the tooltip
                    const rect = this.getBoundingClientRect();
                    tooltip.style.left = `${rect.left + rect.width / 2 - 30}px`;
                    tooltip.style.top = `${rect.top - 30}px`;
                    
                    // Add tooltip to the DOM and show it
                    document.body.appendChild(tooltip);
                    setTimeout(() => { tooltip.style.opacity = '1'; }, 10);
                    
                    // Remove the tooltip after a delay
                    setTimeout(() => {
                        tooltip.style.opacity = '0';
                        setTimeout(() => { document.body.removeChild(tooltip); }, 300);
                    }, 1500);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                });
        });
        
        // Add visual cue that it's clickable
        address.style.cursor = 'pointer';
        if (!address.getAttribute('title')) {
            address.setAttribute('title', 'Click to copy address');
        }
    });
}

// Function to initialize tooltips
function initializeTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });
}

// Add live timestamp updates
setInterval(() => {
    const timestampElements = document.querySelectorAll('.live-timestamp');
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();
    
    timestampElements.forEach(element => {
        element.textContent = `${dateString} ${timeString}`;
    });
}, 1000);

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId !== "#") {
            document.querySelector(targetId).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Add dark/light mode toggle functionality (for future implementation)
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    // Save preference to localStorage
    const isDarkMode = !document.body.classList.contains('light-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Animate numbers when they come into view
function animateNumbers() {
    const numberElements = document.querySelectorAll('.animate-number');
    
    numberElements.forEach(element => {
        const targetValue = parseFloat(element.getAttribute('data-target'));
        const duration = parseInt(element.getAttribute('data-duration')) || 1000;
        const startValue = 0;
        const increment = targetValue / (duration / 16); // 60fps
        
        let currentValue = startValue;
        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                clearInterval(counter);
                currentValue = targetValue;
            }
            
            // Format the number with commas and decimals as needed
            let formattedValue = currentValue.toFixed(2);
            if (element.getAttribute('data-format') === 'currency') {
                formattedValue = '$' + formattedValue.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            }
            
            element.textContent = formattedValue;
        }, 16);
    });
}

// Create intersection observer for animation triggers
const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            if (entry.target.classList.contains('animate-on-scroll')) {
                entry.target.classList.add('animated');
            }
            
            if (entry.target.classList.contains('animate-number-container')) {
                animateNumbers();
            }
            
            // Unobserve after animating
            animationObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

// Observe elements with animation classes
document.querySelectorAll('.animate-on-scroll, .animate-number-container').forEach(el => {
    animationObserver.observe(el);
}); 