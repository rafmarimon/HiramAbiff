/**
 * HiramAbiff Yield Dashboard
 * Common JavaScript Utilities
 */

// Format a number with commas and fixed decimal places
function formatNumber(number, decimals = 2) {
    return parseFloat(number).toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Format a percentage value with + sign for positive values
function formatPercentage(number, decimals = 2) {
    const value = parseFloat(number);
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(decimals) + '%';
}

// Format a date string to a more readable format
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format a date and time string
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Truncate a string with ellipsis
function truncateString(str, maxLength = 20) {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength - 3) + '...';
}

// Truncate an address (e.g., wallet address)
function truncateAddress(address, startChars = 6, endChars = 4) {
    if (!address) return '';
    if (address.length <= startChars + endChars) return address;
    return address.substring(0, startChars) + '...' + address.substring(address.length - endChars);
}

// Convert a value to a human-readable format (e.g., 1.5M, 2.3K)
function toHumanReadable(value, decimals = 1) {
    const num = parseFloat(value);
    if (isNaN(num)) return '0';
    
    if (Math.abs(num) >= 1000000000) {
        return (num / 1000000000).toFixed(decimals) + 'B';
    }
    if (Math.abs(num) >= 1000000) {
        return (num / 1000000).toFixed(decimals) + 'M';
    }
    if (Math.abs(num) >= 1000) {
        return (num / 1000).toFixed(decimals) + 'K';
    }
    
    return num.toFixed(decimals);
}

// Get a color based on value (e.g., red for negative, green for positive)
function getValueColor(value, reverse = false) {
    const num = parseFloat(value);
    if (isNaN(num)) return 'text-muted';
    
    if (!reverse) {
        return num >= 0 ? 'text-success' : 'text-danger';
    } else {
        return num >= 0 ? 'text-danger' : 'text-success';
    }
}

// Get an icon based on value trend
function getValueIcon(value, reverse = false) {
    const num = parseFloat(value);
    if (isNaN(num)) return 'fa-minus';
    
    if (!reverse) {
        return num > 0 ? 'fa-caret-up' : num < 0 ? 'fa-caret-down' : 'fa-minus';
    } else {
        return num > 0 ? 'fa-caret-down' : num < 0 ? 'fa-caret-up' : 'fa-minus';
    }
}

// Create a loading spinner element
function createLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    return spinner;
}

// Show a loading overlay in a container
function showLoading(container) {
    // Clear container
    container.innerHTML = '';
    
    // Create loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'text-center py-5';
    loadingDiv.innerHTML = `
        <div class="loading-spinner mb-3"></div>
        <p class="text-muted">Loading data...</p>
    `;
    
    container.appendChild(loadingDiv);
}

// Show an error message in a container
function showError(container, message = 'Error loading data. Please try again.') {
    // Clear container
    container.innerHTML = '';
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-center py-5';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
        <p class="text-danger">${message}</p>
        <button class="btn btn-outline-primary btn-sm mt-3 retry-btn">
            <i class="fas fa-sync-alt me-1"></i>Retry
        </button>
    `;
    
    container.appendChild(errorDiv);
    
    // Add event listener to retry button
    const retryBtn = container.querySelector('.retry-btn');
    if (retryBtn && container.dataset.retryFunction) {
        const retryFunction = window[container.dataset.retryFunction];
        if (typeof retryFunction === 'function') {
            retryBtn.addEventListener('click', retryFunction);
        }
    }
}

// Show an empty state message in a container
function showEmptyState(container, message = 'No data available.', icon = 'fa-info-circle') {
    // Clear container
    container.innerHTML = '';
    
    // Create empty state message
    const emptyDiv = document.createElement('div');
    emptyDiv.className = 'text-center py-5';
    emptyDiv.innerHTML = `
        <i class="fas ${icon} text-muted fa-3x mb-3"></i>
        <p class="text-muted">${message}</p>
    `;
    
    container.appendChild(emptyDiv);
}

// Convert a hex color to RGB
function hexToRgb(hex) {
    // Remove # if present
    hex = hex.replace('#', '');
    
    // Parse the hex values
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    
    return { r, g, b };
}

// Get a rgba color string with specified opacity
function rgbaColor(hexColor, opacity = 1) {
    const rgb = hexToRgb(hexColor);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`;
}

// Format time from seconds (e.g., 65 -> "1:05")
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Format time duration in a human-readable way
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        const mins = Math.floor(seconds / 60);
        return `${mins}m`;
    } else if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        return `${hours}h`;
    } else {
        const days = Math.floor(seconds / 86400);
        return `${days}d`;
    }
}

// Copy text to clipboard
function copyToClipboard(text) {
    const el = document.createElement('textarea');
    el.value = text;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

// Create a copy button for a text element
function createCopyButton(text, successMessage = 'Copied!') {
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-link text-muted p-0 ms-2';
    btn.innerHTML = '<i class="fas fa-copy"></i>';
    btn.title = 'Copy to clipboard';
    
    btn.addEventListener('click', function() {
        copyToClipboard(text);
        
        // Change icon temporarily
        const icon = btn.querySelector('i');
        icon.className = 'fas fa-check text-success';
        
        // Reset icon after a delay
        setTimeout(() => {
            icon.className = 'fas fa-copy';
        }, 2000);
        
        // Show success message if toast is available
        if (typeof showToast === 'function') {
            showToast('Success', successMessage, 'success');
        }
    });
    
    return btn;
}

// Show a toast notification
function showToast(title, message, type = 'info') {
    // Create toast container if not exists
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong>: ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Remove toast when hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Generate a random color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Generate a color palette with n colors
function generateColorPalette(n, saturation = 100, lightness = 50) {
    const colors = [];
    const hueDelta = 360 / n;
    
    for (let i = 0; i < n; i++) {
        const hue = i * hueDelta;
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
    }
    
    return colors;
}

// Debounce function to limit function calls
function debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Throttle function to limit function calls
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Get a parameter from the URL
function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// Set multiple URL parameters
function setUrlParameters(params) {
    const url = new URL(window.location);
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    window.history.replaceState({}, '', url);
}

// Get a cookie value by name
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

// Set a cookie
function setCookie(name, value, days = 7) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

// Delete a cookie
function deleteCookie(name) {
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
}

// Document ready function
function ready(fn) {
    if (document.readyState !== 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
} 