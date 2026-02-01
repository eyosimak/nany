// NANY v0.1 - Frontend Logic
// Handles step navigation, API calls, and state management

const API_BASE = '';  // Same origin

// State
let userId = localStorage.getItem('nany_user_id');
let currentStep = 1;

// ============================================================
// Initialization
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Create user if none exists
    if (!userId) {
        await createUser();
    }

    // Check for existing profile
    try {
        const profile = await fetch(`${API_BASE}/users/${userId}/profile`);
        if (profile.ok) {
            // User has profile, could skip to step 2
            // But for simplicity, always start at step 1
        }
    } catch (e) {
        // No profile yet, that's fine
    }

    // Setup form handlers
    setupFormHandlers();

    // Show first step
    goToStep(1);
});

// ============================================================
// User Management
// ============================================================

async function createUser() {
    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Failed to create user');

        const data = await response.json();
        userId = data.id;
        localStorage.setItem('nany_user_id', userId);
        console.log('Created user:', userId);
    } catch (error) {
        console.error('Error creating user:', error);
        showError('Failed to initialize. Please refresh the page.');
    }
}

// ============================================================
// Step Navigation
// ============================================================

function goToStep(step) {
    currentStep = step;

    // Update content visibility
    document.querySelectorAll('.step-content').forEach(el => {
        el.classList.remove('active');
    });
    document.getElementById(`step-${step}`).classList.add('active');

    // Update progress indicator
    document.querySelectorAll('.progress .step').forEach(el => {
        const stepNum = parseInt(el.dataset.step);
        el.classList.remove('active', 'completed');

        if (stepNum === step) {
            el.classList.add('active');
        } else if (stepNum < step) {
            el.classList.add('completed');
        }
    });
}

// ============================================================
// Form Handlers
// ============================================================

function setupFormHandlers() {
    // Profile form
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            initiation_friction: document.getElementById('initiation_friction').value,
            attention_span: document.getElementById('attention_span').value,
            reward_sensitivity: document.getElementById('reward_sensitivity').value,
            time_blindness: document.getElementById('time_blindness').value,
            stress_response: document.getElementById('stress_response').value
        };

        try {
            const response = await fetch(`${API_BASE}/users/${userId}/profile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Failed to save profile');

            goToStep(2);
        } catch (error) {
            console.error('Error saving profile:', error);
            showError('Failed to save profile. Please try again.');
        }
    });

    // Environment form
    document.getElementById('environment-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            time_available_minutes: parseInt(document.getElementById('time_available_minutes').value),
            energy_level: parseInt(document.getElementById('energy_level').value),
            context: document.getElementById('context').value,
            external_pressure: document.getElementById('external_pressure').value
        };

        try {
            const response = await fetch(`${API_BASE}/users/${userId}/environment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Failed to save environment');

            goToStep(3);
        } catch (error) {
            console.error('Error saving environment:', error);
            showError('Failed to save context. Please try again.');
        }
    });

    // Goal form
    document.getElementById('goal-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            description: document.getElementById('goal_description').value,
            priority: document.getElementById('priority').value,
            time_horizon: document.getElementById('time_horizon').value
        };

        try {
            // Save goal
            const goalResponse = await fetch(`${API_BASE}/users/${userId}/goal`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!goalResponse.ok) throw new Error('Failed to save goal');

            // Navigate to recommendation step
            goToStep(4);

            // Get recommendation
            await getRecommendation();
        } catch (error) {
            console.error('Error saving goal:', error);
            showError('Failed to save goal. Please try again.');
        }
    });
}

// ============================================================
// Recommendation
// ============================================================

async function getRecommendation() {
    const display = document.getElementById('recommendation-display');
    const result = document.getElementById('recommendation-result');

    display.style.display = 'block';
    result.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/users/${userId}/recommend`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get recommendation');
        }

        const data = await response.json();

        // Display recommendation
        document.getElementById('main-action').textContent = data.recommended_action;
        document.getElementById('action-time').textContent = `${data.estimated_time_minutes} min`;
        document.getElementById('action-difficulty').textContent = data.difficulty;
        document.getElementById('action-why').textContent = data.why_this_action;
        document.getElementById('fallback-action').textContent = data.fallback_action;

        display.style.display = 'none';
        result.style.display = 'block';
    } catch (error) {
        console.error('Error getting recommendation:', error);
        display.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

// ============================================================
// Feedback
// ============================================================

async function submitFeedback(completed) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action_completed: completed })
        });

        if (!response.ok) throw new Error('Failed to save feedback');

        // Show result
        const form = document.getElementById('feedback-form');
        const result = document.getElementById('feedback-result');
        const message = document.getElementById('feedback-message');

        form.style.display = 'none';
        result.style.display = 'block';

        if (completed) {
            message.textContent = "Great. You did it. That's what matters.";
            message.style.color = 'var(--success)';
        } else {
            message.textContent = "That's data, not failure. Try a different goal.";
            message.style.color = 'var(--text-muted)';
        }
    } catch (error) {
        console.error('Error saving feedback:', error);
        showError('Failed to save feedback. Please try again.');
    }
}

// ============================================================
// Utility
// ============================================================

function startOver() {
    // Reset feedback form visibility
    document.getElementById('feedback-form').style.display = 'block';
    document.getElementById('feedback-result').style.display = 'none';

    // Clear goal form
    document.getElementById('goal_description').value = '';
    document.getElementById('priority').value = '';
    document.getElementById('time_horizon').value = '';

    // Go to environment step (profile stays)
    goToStep(2);
}

function showError(message) {
    // Simple alert for now
    alert(message);
}

// Make functions available globally
window.goToStep = goToStep;
window.submitFeedback = submitFeedback;
window.startOver = startOver;
