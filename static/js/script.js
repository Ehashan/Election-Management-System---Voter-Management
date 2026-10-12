// ===================================
// Election Management System - JavaScript
// ===================================

// ===== Password Visibility Toggle =====
const SVG_EYE = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-icon" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
const SVG_EYE_OFF = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="eye-icon" aria-hidden="true"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';

function initPasswordToggles() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(field => {
        // Skip if already wrapped
        if (field.parentElement.classList.contains('password-wrapper')) {
            return;
        }
        
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'password-wrapper';
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = SVG_EYE;
        toggleBtn.setAttribute('aria-label', 'Show password');
        toggleBtn.setAttribute('title', 'Show password');
        
        // Add click event
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (field.type === 'password') {
                field.type = 'text';
                toggleBtn.innerHTML = SVG_EYE_OFF;
                toggleBtn.setAttribute('aria-label', 'Hide password');
                toggleBtn.setAttribute('title', 'Hide password');
            } else {
                field.type = 'password';
                toggleBtn.innerHTML = SVG_EYE;
                toggleBtn.setAttribute('aria-label', 'Show password');
                toggleBtn.setAttribute('title', 'Show password');
            }
        });
        
        wrapper.appendChild(toggleBtn);
    });
}

// ===== NIC Validation =====
function validateNIC(nic) {
    // Sri Lankan NIC validation
    // Old format: 9 digits + V (e.g., 123456789V)
    // New format: 12 digits (e.g., 199912345678)
    
    const oldFormat = /^[0-9]{9}[vVxX]$/;
    const newFormat = /^[0-9]{12}$/;
    
    return oldFormat.test(nic) || newFormat.test(nic);
}

// ===== Mobile Number Validation =====
function validateMobileNumber(mobile) {
    // Sri Lankan mobile format: +94XXXXXXXXX or 0XXXXXXXXX
    const pattern = /^(\+94|0)?[0-9]{9}$/;
    return pattern.test(mobile.replace(/\s/g, ''));
}

// ===== Format Mobile Number =====
function formatMobileNumber(input) {
    let value = input.value.replace(/\s/g, '');
    
    // Remove non-digits except +
    value = value.replace(/[^\d+]/g, '');
    
    // Format: +94 XX XXX XXXX or 0XX XXX XXXX
    if (value.startsWith('+94')) {
        value = value.slice(0, 12);
        if (value.length > 3) {
            value = value.slice(0, 3) + ' ' + value.slice(3);
        }
        if (value.length > 6) {
            value = value.slice(0, 6) + ' ' + value.slice(6);
        }
        if (value.length > 10) {
            value = value.slice(0, 10) + ' ' + value.slice(10);
        }
    } else if (value.startsWith('0')) {
        value = value.slice(0, 10);
        if (value.length > 3) {
            value = value.slice(0, 3) + ' ' + value.slice(3);
        }
        if (value.length > 7) {
            value = value.slice(0, 7) + ' ' + value.slice(7);
        }
    }
    
    input.value = value;
}

// ===== Real-time Form Validation =====
function initFormValidation() {
    // NIC validation
    const nicInput = document.querySelector('input[name="nic"]');
    if (nicInput) {
        nicInput.addEventListener('blur', function() {
            const val = this.value.trim();
            if (!val) {
                clearFieldError(this);
                return;
            }
            if (!validateNIC(val)) {
                showFieldError(this, 'Invalid NIC format. Use 9 digits + V or 12 digits.');
                return;
            }
            
            // Check with server temp_nic database
            fetch('/check-nic/?nic=' + encodeURIComponent(val))
                .then(response => response.json())
                .then(data => {
                    if (!data.valid) {
                        showFieldError(nicInput, data.message);
                    } else {
                        clearFieldError(nicInput);
                        showFieldSuccess(nicInput, '✓ ' + data.message);
                    }
                })
                .catch(err => {
                    console.error('Error checking NIC:', err);
                });
        });
    }
    
    // Mobile number validation and formatting
    const mobileInput = document.querySelector('input[name="mobile_number"]');
    if (mobileInput) {
        mobileInput.addEventListener('input', function() {
            formatMobileNumber(this);
        });
        
        mobileInput.addEventListener('blur', function() {
            if (this.value && !validateMobileNumber(this.value)) {
                showFieldError(this, 'Invalid mobile number format.');
            } else {
                clearFieldError(this);
            }
        });
    }
    
    // Password match validation
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');
    
    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('blur', function() {
            if (this.value && this.value !== passwordInput.value) {
                showFieldError(this, 'Passwords do not match.');
            } else {
                clearFieldError(this);
            }
        });
    }
}

// ===== Show Field Error =====
function showFieldError(input, message) {
    clearFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error field-error';
    errorDiv.textContent = message;
    
    input.parentElement.appendChild(errorDiv);
    input.style.borderColor = '#ef4444';
}

// ===== Show Field Success =====
function showFieldSuccess(input, message) {
    clearFieldError(input);
    
    const successDiv = document.createElement('div');
    successDiv.className = 'field-success';
    successDiv.style.color = '#10b981';
    successDiv.style.fontSize = '12px';
    successDiv.style.marginTop = '4px';
    successDiv.style.fontWeight = '500';
    successDiv.textContent = message;
    
    input.parentElement.appendChild(successDiv);
    input.style.borderColor = '#10b981';
}

// ===== Clear Field Error & Success =====
function clearFieldError(input) {
    const existingError = input.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    const existingSuccess = input.parentElement.querySelector('.field-success');
    if (existingSuccess) {
        existingSuccess.remove();
    }
    input.style.borderColor = '';
}

// ===== Auto-populate Username from NIC =====
function initUsernameAutofill() {
    const nicInput = document.querySelector('input[name="nic"]');
    const usernameDisplay = document.querySelector('input[value][readonly]');
    
    if (nicInput && usernameDisplay) {
        nicInput.addEventListener('input', function() {
            usernameDisplay.value = this.value;
        });
    }
}

// ===== Enhanced Camera Functionality =====
function initCamera() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const photo = document.getElementById('photo');
    const snapButton = document.getElementById('snap');
    const faceImageData = document.getElementById('face_image_data');
    
    if (!video || !canvas || !photo || !snapButton) {
        return; // Not on a page with camera
    }
    
    let stream = null;
    
    // Start camera
    navigator.mediaDevices.getUserMedia({ 
        video: { 
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
        } 
    })
    .then(function(mediaStream) {
        stream = mediaStream;
        video.srcObject = mediaStream;
        video.play();
    })
    .catch(function(err) {
        console.error("Camera error:", err);
        alert("Camera access denied or not available. Please enable camera permissions.");
    });
    
    // Capture photo
    snapButton.addEventListener('click', function() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const data = canvas.toDataURL('image/jpeg', 0.8);
        photo.setAttribute('src', data);
        photo.style.display = 'block';
        video.style.display = 'none';
        
        faceImageData.value = data;
        
        // Add retake button
        if (!document.getElementById('retake')) {
            const retakeBtn = document.createElement('button');
            retakeBtn.type = 'button';
            retakeBtn.id = 'retake';
            retakeBtn.className = 'btn btn-secondary';
            retakeBtn.style.margin = '10px';
            retakeBtn.innerHTML = '🔄 Retake Photo';
            retakeBtn.addEventListener('click', function() {
                video.style.display = 'block';
                photo.style.display = 'none';
                faceImageData.value = '';
                this.remove();
            });
            snapButton.parentNode.insertBefore(retakeBtn, snapButton.nextSibling);
        }
    });
    
    // Stop camera when leaving page
    window.addEventListener('beforeunload', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
}

// ===== Verification Code Timer =====
function initVerificationTimer() {
    const timerElement = document.getElementById('code-timer');
    const resendButton = document.getElementById('resend-code');
    
    if (!timerElement) return;
    
    let timeLeft = 300; // 5 minutes
    
    const countdown = setInterval(function() {
        timeLeft--;
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = 'Code expired';
            timerElement.style.color = '#ef4444';
            
            if (resendButton) {
                resendButton.disabled = false;
            }
        }
    }, 1000);
}

// ===== Resend Code with Cooldown =====
function initResendCode() {
    const resendButton = document.getElementById('resend-code');
    
    if (!resendButton) return;
    
    resendButton.addEventListener('click', function() {
        this.disabled = true;
        let cooldown = 60;
        const originalText = this.textContent;
        
        const countdown = setInterval(() => {
            this.textContent = `Resend in ${cooldown}s`;
            cooldown--;
            
            if (cooldown < 0) {
                clearInterval(countdown);
                this.textContent = originalText;
                this.disabled = false;
            }
        }, 1000);
        
        // Make AJAX request to resend code
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'resend=true'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Verification code resent!');
            }
        })
        .catch(error => console.error('Error:', error));
    });
}

// ===== Get CSRF Token =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== Loading State =====
function showLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.innerHTML = '<span class="spinner"></span> Loading...';
}

function hideLoading(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText;
}

// ===== Form Submit with Loading =====
function initFormSubmit() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                showLoading(submitButton);
            }
        });
    });
}

// ===== Initialize Everything on Page Load =====
document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggles();
    initFormValidation();
    initUsernameAutofill();
    initCamera();
    initVerificationTimer();
    initResendCode();
    initFormSubmit();
    
    console.log('EMS JavaScript initialized');
});
