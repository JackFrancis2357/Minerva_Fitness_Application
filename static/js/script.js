// Daily Workout Planner JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize duration slider and input synchronization
    initializeDurationControls();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize equipment selection logic
    initializeEquipmentSelection();
    
    // Initialize print functionality
    initializePrintButton();
    
    // Initialize plan type selection
    initializePlanTypeSelection();
    
    // Initialize weekly goal selection
    initializeWeeklyGoalSelection();
});

/**
 * Initialize duration slider and input field synchronization
 */
function initializeDurationControls() {
    const durationSlider = document.getElementById('durationSlider');
    const durationInput = document.getElementById('durationInput');
    
    if (durationSlider && durationInput) {
        // Sync slider to input
        durationSlider.addEventListener('input', function() {
            durationInput.value = this.value;
        });
        
        // Sync input to slider
        durationInput.addEventListener('input', function() {
            let value = parseInt(this.value);
            
            // Validate range
            if (value < 15) {
                value = 15;
                this.value = 15;
            } else if (value > 90) {
                value = 90;
                this.value = 90;
            }
            
            durationSlider.value = value;
        });
        
        // Prevent invalid characters
        durationInput.addEventListener('keypress', function(e) {
            if (!/[0-9]/.test(e.key) && !['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const workoutForm = document.getElementById('workoutForm');
    
    if (workoutForm) {
        workoutForm.addEventListener('submit', function(e) {
            const equipmentChecked = document.querySelectorAll('input[name="equipment"]:checked');
            const durationValue = document.getElementById('durationSlider').value;
            const planType = document.querySelector('input[name="plan_type"]:checked')?.value;
            const weeklyGoalSelect = document.getElementById('weekly_goal');
            const customGoalText = document.getElementById('custom_goal_text');
            
            // Check if at least one equipment is selected
            if (equipmentChecked.length === 0) {
                e.preventDefault();
                showAlert('Please select at least one equipment option.', 'error');
                return false;
            }
            
            // Check duration range
            if (durationValue < 15 || durationValue > 90) {
                e.preventDefault();
                showAlert('Please select a duration between 15 and 90 minutes.', 'error');
                return false;
            }
            
            // Check weekly plan requirements
            if (planType === 'weekly') {
                let goalValue = weeklyGoalSelect?.value || '';
                
                if (goalValue === 'custom') {
                    const customValue = customGoalText?.value?.trim() || '';
                    if (!customValue) {
                        e.preventDefault();
                        showAlert('Please describe your custom fitness goal.', 'error');
                        return false;
                    }
                } else if (!goalValue) {
                    e.preventDefault();
                    showAlert('Please select your weekly workout goal.', 'error');
                    return false;
                }
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                if (planType === 'weekly') {
                    submitButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating Weekly Plan...';
                } else {
                    submitButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating Workout...';
                }
            }
            
            return true;
        });
    }
}

/**
 * Initialize equipment selection logic
 */
function initializeEquipmentSelection() {
    const equipmentCheckboxes = document.querySelectorAll('input[name="equipment"]');
    
    equipmentCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Visual feedback for selection
            const label = this.nextElementSibling;
            if (this.checked) {
                label.classList.add('fw-bold');
            } else {
                label.classList.remove('fw-bold');
            }
            
            // Update equipment count
            updateEquipmentCount();
        });
    });
    
    // Initial count update
    updateEquipmentCount();
}

/**
 * Update equipment selection count
 */
function updateEquipmentCount() {
    const checkedEquipment = document.querySelectorAll('input[name="equipment"]:checked');
    const count = checkedEquipment.length;
    
    // You can add a counter display if needed
    console.log(`Equipment selected: ${count}`);
}

/**
 * Initialize print button functionality
 */
function initializePrintButton() {
    const printButton = document.querySelector('button[onclick="window.print()"]');
    
    if (printButton) {
        printButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Add print-specific styling
            document.body.classList.add('printing');
            
            // Print the page
            window.print();
            
            // Remove print styling after print dialog closes
            setTimeout(() => {
                document.body.classList.remove('printing');
            }, 1000);
        });
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alertDiv = document.createElement('div');
    
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of the container
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Smooth scrolling for anchor links
 */
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Form field animations
 */
function animateFormFields() {
    const formFields = document.querySelectorAll('.form-control, .form-check-input');
    
    formFields.forEach(field => {
        field.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        field.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

/**
 * Workout timer functionality (for future enhancement)
 */
function createWorkoutTimer() {
    // This could be expanded to include a workout timer
    // that tracks rest periods and exercise duration
    console.log('Workout timer ready for future implementation');
}

/**
 * Local storage for user preferences (for future enhancement)
 */
function saveUserPreferences() {
    const equipmentChecked = Array.from(document.querySelectorAll('input[name="equipment"]:checked'))
        .map(checkbox => checkbox.value);
    const duration = document.getElementById('durationSlider')?.value;
    
    if (equipmentChecked.length > 0 && duration) {
        localStorage.setItem('workoutPreferences', JSON.stringify({
            equipment: equipmentChecked,
            duration: duration,
            timestamp: new Date().toISOString()
        }));
    }
}

/**
 * Load user preferences from local storage
 */
function loadUserPreferences() {
    const preferences = localStorage.getItem('workoutPreferences');
    
    if (preferences) {
        try {
            const data = JSON.parse(preferences);
            
            // Only load if preferences are recent (within 30 days)
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            
            if (new Date(data.timestamp) > thirtyDaysAgo) {
                // Restore equipment selection
                data.equipment.forEach(eq => {
                    const checkbox = document.getElementById(eq);
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                });
                
                // Restore duration
                if (data.duration) {
                    const slider = document.getElementById('durationSlider');
                    const input = document.getElementById('durationInput');
                    
                    if (slider && input) {
                        slider.value = data.duration;
                        input.value = data.duration;
                    }
                }
            }
        } catch (e) {
            console.log('Error loading preferences:', e);
        }
    }
}

/**
 * Initialize plan type selection logic
 */
function initializePlanTypeSelection() {
    const dailyRadio = document.getElementById('plan_daily');
    const weeklyRadio = document.getElementById('plan_weekly');
    const weeklyGoalSection = document.getElementById('weeklyGoalSection');
    const durationLabel = document.getElementById('durationLabel');
    const durationDescription = document.getElementById('durationDescription');
    const buttonText = document.getElementById('buttonText');
    
    if (dailyRadio && weeklyRadio && weeklyGoalSection) {
        // Handle plan type changes
        function updatePlanType() {
            if (weeklyRadio.checked) {
                weeklyGoalSection.style.display = 'block';
                if (durationLabel) durationLabel.textContent = 'Daily Session Duration';
                if (durationDescription) durationDescription.textContent = 'Duration for each workout day (15-90 minutes)';
                if (buttonText) buttonText.textContent = 'Generate Weekly Plan';
            } else {
                weeklyGoalSection.style.display = 'none';
                if (durationLabel) durationLabel.textContent = 'Workout Duration';
                if (durationDescription) durationDescription.textContent = 'Choose your desired workout length (15-90 minutes)';
                if (buttonText) buttonText.textContent = 'Generate My Workout';
            }
        }
        
        dailyRadio.addEventListener('change', updatePlanType);
        weeklyRadio.addEventListener('change', updatePlanType);
        
        // Initial state
        updatePlanType();
    }
}

/**
 * Initialize weekly goal selection logic
 */
function initializeWeeklyGoalSelection() {
    const weeklyGoalSelect = document.getElementById('weekly_goal');
    const customGoalInput = document.getElementById('customGoalInput');
    const customGoalText = document.getElementById('custom_goal_text');
    
    if (weeklyGoalSelect && customGoalInput) {
        weeklyGoalSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customGoalInput.style.display = 'block';
                if (customGoalText) {
                    customGoalText.focus();
                }
            } else {
                customGoalInput.style.display = 'none';
            }
        });
        
        // Update the hidden input with custom goal when needed
        if (customGoalText) {
            customGoalText.addEventListener('input', function() {
                if (weeklyGoalSelect.value === 'custom') {
                    weeklyGoalSelect.setAttribute('data-custom-value', this.value);
                }
            });
        }
    }
}

// Initialize preference loading on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUserPreferences();
});

// Save preferences when form is submitted
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('workoutForm');
    if (form) {
        form.addEventListener('submit', saveUserPreferences);
    }
});
