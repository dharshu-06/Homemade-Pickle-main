/**
 * Main JavaScript - Interactive Features
 * Homemade Pickles & Snacks
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeAnimations();
    initializeFormValidation();
});

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.product-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                showValidationErrors(form);
            }
            form.classList.add('was-validated');
        });
    });
}

function showValidationErrors(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
        }
    });
}

function addToCartAnimation(event) {
    const button = event.currentTarget;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check"></i> Added!';
    button.disabled = true;
    button.style.backgroundColor = '#28a745';
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
        button.style.backgroundColor = '';
    }, 2000);
}

const productSearch = document.querySelector('input[placeholder*="Search"]');
if (productSearch) {
    productSearch.addEventListener('input', debounce(function(e) {
        // Can be extended for dynamic search suggestions
    }, 300));
}

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

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function updateCartCount() {
    const cartItems = document.querySelectorAll('.cart-item');
    const cartCount = cartItems.length;
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = cartCount;
        cartBadge.style.display = cartCount > 0 ? 'inline' : 'none';
    }
}

function validateQuantity(input) {
    const min = parseInt(input.min) || 1;
    const max = parseInt(input.max) || 999;
    let value = parseInt(input.value) || min;
    if (value < min) value = min;
    if (value > max) value = max;
    input.value = value;
}

function previewImage(event) {
    const file = event.target.files[0];
    const preview = document.querySelector('.image-preview');
    if (file && preview) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

function confirmDelete(itemName = 'this item') {
    return confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`);
}

function printOrder() {
    window.print();
}

function shareOrder(orderId) {
    const text = `Check out my order #${orderId} from Homemade Pickles & Snacks!`;
    const url = window.location.href;
    if (navigator.share) {
        navigator.share({ title: 'My Order', text: text, url: url });
    } else {
        navigator.clipboard.writeText(`${text} ${url}`);
        alert('Copied to clipboard!');
    }
}

document.querySelectorAll('input[type="number"][min]').forEach(input => {
    input.addEventListener('change', function() {
        validateQuantity(this);
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
});

document.querySelectorAll('.alert').forEach(alert => {
    if (alert.classList.contains('alert-success')) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
});
