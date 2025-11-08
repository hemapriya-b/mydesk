// Theme toggle functionality
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    
    // Save theme preference
    localStorage.setItem('theme', newTheme);
}

// Update units dropdown based on subject selection
function updateUnits() {
    const subjectId = document.getElementById('subject_id').value;
    const unitSelect = document.getElementById('unit_id');
    
    if (subjectId) {
        unitSelect.innerHTML = '<option value="">Loading units...</option>';
        unitSelect.disabled = true;
        
        fetch(`/get_units/${subjectId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(units => {
                unitSelect.innerHTML = '<option value="">Select Unit</option>';
                units.forEach(unit => {
                    unitSelect.innerHTML += `<option value="${unit.id}">${unit.name}</option>`;
                });
                unitSelect.disabled = false;
                
                // Set unit_id from URL parameter if present
                const urlParams = new URLSearchParams(window.location.search);
                const presetUnitId = urlParams.get('unit_id');
                if (presetUnitId) {
                    unitSelect.value = presetUnitId;
                }
            })
            .catch(error => {
                console.error('Error fetching units:', error);
                unitSelect.innerHTML = '<option value="">Error loading units</option>';
            });
    } else {
        unitSelect.innerHTML = '<option value="">Select a subject first</option>';
        unitSelect.disabled = true;
    }
}

// File upload preview
function previewFile(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const preview = document.getElementById('file-preview');
        const fileName = document.getElementById('file-name');
        
        fileName.textContent = file.name;
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-height: 200px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            const icon = getFileIcon(file.name);
            preview.innerHTML = `<div class="text-center"><i class="${icon} fa-3x"></i><p class="mt-2">${file.name}</p></div>`;
        }
    }
}

// Get appropriate file icon based on file extension
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'fas fa-file-pdf text-danger',
        'doc': 'fas fa-file-word text-primary',
        'docx': 'fas fa-file-word text-primary',
        'txt': 'fas fa-file-alt text-secondary',
        'jpg': 'fas fa-file-image text-success',
        'png': 'fas fa-file-image text-success',
        'jpeg': 'fas fa-file-image text-success',
        'gif': 'fas fa-file-image text-success'
    };
    return iconMap[ext] || 'fas fa-file text-warning';
}

// Confirm before deleting
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Auto-dismiss alerts after 5 seconds
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Password strength checker
function checkPasswordStrength(password) {
    const strength = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong"
    };

    let score = 0;
    
    // Check password length
    if (password.length >= 8) score++;
    
    // Check for lowercase letters
    if (/[a-z]/.test(password)) score++;
    
    // Check for uppercase letters
    if (/[A-Z]/.test(password)) score++;
    
    // Check for numbers
    if (/[0-9]/.test(password)) score++;
    
    // Check for special characters
    if (/[^A-Za-z0-9]/.test(password)) score++;

    return {
        score: score,
        text: strength[score]
    };
}

// Real-time password strength indicator
function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    const strengthIndicator = document.getElementById('password-strength');

    if (passwordInput && strengthIndicator) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = checkPasswordStrength(password);
            
            strengthIndicator.textContent = `Password Strength: ${strength.text}`;
            strengthIndicator.className = 'form-text';
            
            switch(strength.score) {
                case 0:
                case 1:
                    strengthIndicator.classList.add('text-danger');
                    break;
                case 2:
                    strengthIndicator.classList.add('text-warning');
                    break;
                case 3:
                    strengthIndicator.classList.add('text-info');
                    break;
                case 4:
                    strengthIndicator.classList.add('text-success');
                    break;
            }
        });
    }
}

// File size validator
function validateFileSize(input, maxSizeMB = 16) {
    if (input.files && input.files[0]) {
        const fileSize = input.files[0].size / 1024 / 1024; // MB
        if (fileSize > maxSizeMB) {
            alert(`File size must be less than ${maxSizeMB}MB`);
            input.value = '';
            return false;
        }
    }
    return true;
}

// Character counter for textareas
function initCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[data-max-length]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('data-max-length');
        const counterId = textarea.id + '-counter';
        
        // Create counter element if it doesn't exist
        if (!document.getElementById(counterId)) {
            const counter = document.createElement('div');
            counter.id = counterId;
            counter.className = 'form-text text-end';
            textarea.parentNode.appendChild(counter);
        }
        
        const updateCounter = () => {
            const counter = document.getElementById(counterId);
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength}/${maxLength} characters`;
            
            if (currentLength > maxLength) {
                counter.classList.add('text-danger');
                textarea.classList.add('is-invalid');
            } else {
                counter.classList.remove('text-danger');
                textarea.classList.remove('is-invalid');
            }
        };
        
        textarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });
}

// Smooth scrolling for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Loading spinner helper
function showLoading() {
    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    spinner.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
    `;
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'alert alert-success alert-dismissible fade show position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i> Copied to clipboard!
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    // Initialize units dropdown if on add_note page
    if (document.getElementById('subject_id')) {
        updateUnits();
    }
    
    // Initialize file input preview if on add_note page
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            validateFileSize(this);
            previewFile(this);
        });
    }
    
    // Initialize form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this.id)) {
                e.preventDefault();
                // Scroll to first invalid field
                const firstInvalid = this.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            }
        });
    });
    
    // Initialize auto-dismiss alerts
    autoDismissAlerts();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize password strength indicator
    initPasswordStrength();
    
    // Initialize character counters
    initCharacterCounters();
    
    // Initialize smooth scroll
    initSmoothScroll();
    
    // Add loading state to buttons on form submission
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Add confirmation to delete buttons
    const deleteButtons = document.querySelectorAll('a[href*="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirmDelete()) {
                e.preventDefault();
            }
        });
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Responsive table helper
function makeTableResponsive() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Export functions for global use
window.NotesApp = {
    toggleTheme,
    updateUnits,
    previewFile,
    getFileIcon,
    confirmDelete,
    validateForm,
    checkPasswordStrength,
    validateFileSize,
    showLoading,
    hideLoading,
    copyToClipboard
};