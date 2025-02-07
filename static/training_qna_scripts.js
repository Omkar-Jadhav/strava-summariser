console.log("JavaScript file loaded!");
const questions = [
        'goalQuestion', 'dateQuestion', 'availabilityQuestion', 
        'fitnessQuestion', 'performanceQuestion',
        'strengthQuestion', 'timeQuestion', 'additionalQuestion'
    ];

let currentQuestion = 0;
let selectedGoalType = null;
let originalSelectedGoalType = null; // Track initial selection

// Function to select a goal type (visual selection only)
function selectGoal(newType) {
    const cards = document.querySelectorAll('.goal-card');
    cards.forEach(card => card.classList.remove('selected'));
    
    const selectedCard = newType === 'standard' ? document.querySelector('#standardGoal').parentElement :
                        newType === 'custom' ? document.getElementById('customGoalCard') :
                        document.getElementById('specificEventCard');
    
    selectedCard.classList.add('selected');
    selectedGoalType = newType;
}

// Function to show the current question
function showQuestion(index) {
    // Track original selection when entering goal question
    if (questions[index] === 'goalQuestion') {
        originalSelectedGoalType = selectedGoalType;
    }
    
    document.querySelectorAll('.question-card').forEach(card => {
        card.style.display = 'none';
    });
    const currentCard = document.getElementById(questions[index]);
    currentCard.style.display = 'block';
    currentCard.style.animation = 'popIn 0.3s ease-out forwards';
    
    const progress = ((index + 1) / questions.length) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
    
    document.getElementById('prevButton').disabled = index === 0;
    document.getElementById('nextButton').style.display = index < questions.length - 1 ? 'block' : 'none';
    document.getElementById('generateButton').style.display = index === questions.length - 1 ? 'block' : 'none';
}

// Function to move to the next question
function nextQuestion() {
    // Validate only when leaving goal question
    if (questions[currentQuestion] === 'goalQuestion') {
        if (!selectedGoalType) {
            alert("Please select a goal type!");
            return;
        }
        
        const goals = ['standardGoal', 'specificEvent'];
        const filledGoals = goals.filter(goal => document.getElementById(goal).value !== '');
        if (filledGoals.length > 1) {
            alert("You can select only one goal type. Clear one of the goal types.");
            return;
        }

    }
    // Add validation for other questions
    if (questions[currentQuestion] === 'dateQuestion' && !document.getElementById('targetDate').value) {
        alert("Please select a target date!");
        return;
    }
    if (questions[currentQuestion] === 'availabilityQuestion' && !document.getElementById('trainingDays').value) {
        alert("Please select your training days!");
        return;
    }
    if (questions[currentQuestion] === 'fitnessQuestion' && !document.getElementById('fitnessLevel').value) {
        alert("Please select your fitness level!");
        return;
    }
    if (questions[currentQuestion] === 'performanceQuestion' && !document.getElementById('recentPerformance').value) {
        alert("Please enter your recent performance!");
        return;
    }
    if (questions[currentQuestion] === 'longestRunQuestion' && !document.getElementById('longestRun').value) {
        alert("Please enter your longest run!");
        return;
    }


    if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        showQuestion(currentQuestion);
    }
}

// Function to move to the previous question
function prevQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        showQuestion(currentQuestion);
    }
}

// Helper function to check if the current goal has data
function checkCurrentGoalData() {
    if (!selectedGoalType) return false;
    switch(selectedGoalType) {
        case 'standard': return document.getElementById('standardGoal').value !== '';
        case 'custom': return document.getElementById('customGoal').value.trim() !== '';
        case 'specific': return document.getElementById('specificEvent').value.trim() !== '';
    }
    return false;
}

// Helper function to clear data for the current goal
function clearCurrentGoalData() {
    switch(selectedGoalType) {
        case 'standard': 
            clearStandardGoal();
            break;
        case 'custom': 
            document.getElementById('customGoal').value = '';
            validateCustomGoal();
            break;
        case 'specific': 
            document.getElementById('specificEvent').value = '';
            validateSpecificEvent();
            break;
    }
}

// Function to clear standard goal data
function clearStandardGoal() {
    document.getElementById('standardGoal').value = '';
    document.getElementById('paceTimeSection').style.display = 'none';
    document.querySelectorAll('#paceTimeSection input').forEach(input => input.value = '');
    document.getElementById('paceTimeResult').innerText = '';
}

// Function to update the standard goal section
function updateStandardGoal() {
    const standardGoal = document.getElementById('standardGoal').value;
    if (standardGoal) {
        document.getElementById('paceTimeSection').style.display = 'block';
    } else {
        document.getElementById('paceTimeSection').style.display = 'none';
    }
}

// Function to validate custom goal input
function validateCustomGoal() {
    const input = document.getElementById('customGoal');
    const error = document.getElementById('customGoalError');
    if (input.value.trim() === '') {
        error.style.display = 'block';
        return false;
    }
    error.style.display = 'none';
    return true;
}

// Function to validate specific event input
function validateSpecificEvent() {
    const input = document.getElementById('specificEvent');
    const error = document.getElementById('specificEventError');
    if (input.value.trim() === '') {
        error.style.display = 'block';
        return false;
    }
    error.style.display = 'none';
    return true;
}

// Function to select an option (e.g., training days, fitness level)
function selectOption(field, value) {
    const group = document.getElementById(`${field}`);
    document.getElementById(`${field}`).value=value;
    group.querySelectorAll('.option-button').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
    window[field] = value;
}

const loadingMessages = [
    "Extracting athlete details...",
    "Extracting Strava activities...",
    "Analyzing goals...",
    "Generating workout plan..."
];

let currentStep = 0;

function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'flex'; // Make it visible
    document.getElementById('loadingMessage').innerText = loadingMessages[currentStep]; 
}

function updateLoadingMessage() {
    if (currentStep < loadingMessages.length) {
        document.getElementById('loadingMessage').innerText = loadingMessages[currentStep];
        console.log(`Step ${currentStep + 1}: ${loadingMessages[currentStep]}`); // Debugging log
        currentStep++;
    }
}

function hideLoadingOverlay() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function generatePlan() {
    const formData = {
        goalType: selectedGoalType,
        goal: selectedGoalType === 'standard' ? document.getElementById('standardGoal').value :
                selectedGoalType === 'specific' ? document.getElementById('specificEvent').value : '',
        targetDate: document.getElementById('targetDate').value,
        trainingDays: document.getElementById('trainingDays').value,
        fitnessLevel: document.getElementById('fitnessLevel').value,
        recentPerformance: document.getElementById('recentPerformance').value,
        strengthSessions: document.getElementById('strengthSessions').value,
        timeCommitment: document.getElementById('timeCommitment').value,
        injuries: document.getElementById('injuries').value,
        preferences: document.getElementById('preferences').value,
        specialConditions: document.getElementById('specialConditions').value,
        otherInfo: document.getElementById('otherInfo').value,
        athlete_id: document.getElementById('athlete_id').value,
        athlete_name: document.getElementById('athlete_name').value
    };

    console.log('Form Data:', formData);

    showLoadingOverlay(); // Show loading only when generating plan

    // Allow UI to update before starting fetch requests
    requestAnimationFrame(() => {
        setTimeout(() => {
            executeStep('/generatePlan/checkAthleteStatus', formData);
        }, 100); // Small delay to ensure UI renders
    });
}

function executeStep(url, data = null) {
    updateLoadingMessage(); // Update loading text before fetch

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            if (result.next_step) {
                executeStep(result.next_step);
            } else if (result.redirect_url) {
                window.location.href = result.redirect_url;
            } else {
                hideLoadingOverlay();
            }
        } else {
            alert(result.error || 'Failed to generate plan. Please try again.');
            hideLoadingOverlay();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        hideLoadingOverlay();
    });
}
document.getElementById('targetDate').min = new Date().toISOString().split('T')[0];
showQuestion(0);

// Function to calculate pace from finish time
function calculateFromTime() {
    const hours = parseInt(document.getElementById('hours').value) || 0;
    const minutes = parseInt(document.getElementById('minutes').value) || 0;
    const seconds = parseInt(document.getElementById('seconds').value) || 0;
    
    const totalSeconds = (hours * 3600) + (minutes * 60) + seconds;
    updatePaceFromTime(totalSeconds);
}

// Function to calculate finish time from pace
function calculateFromPace() {
    const paceMins = parseInt(document.getElementById('paceMinutes').value) || 0;
    const paceSecs = parseInt(document.getElementById('paceSeconds').value) || 0;
    
    const totalSeconds = (paceMins * 60) + paceSecs;
    updateTimeFromPace(totalSeconds);
}

// Function to update pace based on finish time
function updatePaceFromTime(totalSeconds) {
    const distance = getDistanceInKm(document.getElementById('standardGoal').value);
    if (!distance) return;

    const paceTotalSeconds = totalSeconds / distance;
    const paceMins = Math.floor(paceTotalSeconds / 60);
    const paceSecs = Math.round(paceTotalSeconds % 60);

    document.getElementById('paceMinutes').value = paceMins;
    document.getElementById('paceSeconds').value = paceSecs.toString().padStart(2, '0');
    updateResultDisplay(totalSeconds, paceTotalSeconds);
}

// Function to update finish time based on pace
function updateTimeFromPace(paceTotalSeconds) {
    const distance = getDistanceInKm(document.getElementById('standardGoal').value);
    if (!distance) return;

    const totalSeconds = paceTotalSeconds * distance;
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = Math.round(totalSeconds % 60);

    document.getElementById('hours').value = hours;
    document.getElementById('minutes').value = minutes;
    document.getElementById('seconds').value = seconds.toString().padStart(2, '0');
    updateResultDisplay(totalSeconds, paceTotalSeconds);
}

// Function to update the result display
function updateResultDisplay(totalSeconds, paceTotalSeconds) {
    const resultDiv = document.getElementById('paceTimeResult');
    const paceMins = Math.floor(paceTotalSeconds / 60);
    const paceSecs = Math.round(paceTotalSeconds % 60);
    
    resultDiv.innerHTML = `
        Projected Finish Time: ${formatTime(totalSeconds)}<br>
        Projected Pace: ${paceMins}:${paceSecs.toString().padStart(2, '0')} min/km
    `;
}

// Function to format time as HH:MM:SS
function formatTime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = Math.round(totalSeconds % 60);
    return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        seconds.toString().padStart(2, '0')
    ].join(':');
}

// Function to get distance in kilometers based on goal
function getDistanceInKm(goal) {
    switch (goal) {
        case '5k': return 5;
        case '10k': return 10;
        case 'half': return 21.0975;
        case 'marathon': return 42.195;
        case 'ultra': return 50;
        default: return 0;
    }
}

// Input validation for time inputs
document.querySelectorAll('.time-inputs input').forEach(input => {
    input.addEventListener('change', function() {
        if (this.value < parseInt(this.min)) this.value = this.min;
        if (this.value > parseInt(this.max)) this.value = this.max;
    });
});

