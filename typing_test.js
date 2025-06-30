// Typing Test Module
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const textDisplay = document.getElementById('text-display');
    const userInput = document.getElementById('user-input');
    const timerDisplay = document.getElementById('timer');
    const wpmDisplay = document.getElementById('wpm-display');
    const accuracyDisplay = document.getElementById('accuracy-display');
    const difficultySelector = document.getElementById('difficulty');
    const startButton = document.getElementById('start-btn');
    const endButton = document.getElementById('end-btn');
    const resultsSection = document.getElementById('results-section');
    const predictedWpmDisplay = document.getElementById('predicted-wpm');
    const errorDetails = document.getElementById('error-details');
    const suggestionsList = document.getElementById('suggestions-list');
    
    // Test state
    let testActive = false;
    let startTime;
    let originalText = '';
    let timerInterval;
    let keystrokeData = [];
    let lastPredictionTime = 0;
    let testDifficulty = 'medium';
    
    // Initialize the test
    function initialize() {
        // Event listeners
        startButton.addEventListener('click', startTest);
        endButton.addEventListener('click', endTest);
        difficultySelector.addEventListener('change', function() {
            testDifficulty = this.value;
        });
        
        userInput.addEventListener('input', handleInput);
        userInput.addEventListener('keydown', recordKeystroke);
        
        // Disable input field initially
        userInput.disabled = true;
        
        // Hide results section initially
        resultsSection.style.display = 'none';
        
        // Hide end button initially
        endButton.style.display = 'none';
    }
    
    // Fetch a random text based on selected difficulty
    function fetchText() {
        return fetch(`/api/get-text?difficulty=${testDifficulty}`)
            .then(response => response.json())
            .then(data => {
                originalText = data.text;
                textDisplay.textContent = originalText;
                return data.text;
            })
            .catch(error => {
                console.error('Error fetching text:', error);
                textDisplay.textContent = 'Error loading text. Please try again.';
            });
    }
    
    // Start the typing test
    function startTest() {
        // Reset state
        testActive = false;
        userInput.value = '';
        wpmDisplay.textContent = '0';
        accuracyDisplay.textContent = '100%';
        predictedWpmDisplay.textContent = 'Calculating...';
        errorDetails.innerHTML = '';
        suggestionsList.innerHTML = '';
        resultsSection.style.display = 'none';
        keystrokeData = [];
        
        // Fetch new text and set up test
        fetchText().then(() => {
            userInput.disabled = false;
            userInput.focus();
            startTime = new Date().getTime();
            testActive = true;
            
            // Start timer
            clearInterval(timerInterval);
            updateTimer();
            timerInterval = setInterval(updateTimer, 1000);
            
            // Change button text
            startButton.textContent = 'Restart Test';
            
            // Show end test button
            endButton.style.display = 'inline-block';
        });
    }
    
    // Update the timer display
    function updateTimer() {
        if (!testActive) return;
        
        const currentTime = new Date().getTime();
        const elapsedTime = Math.floor((currentTime - startTime) / 1000); // in seconds
        
        const minutes = Math.floor(elapsedTime / 60);
        const seconds = elapsedTime % 60;
        
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Update live WPM calculation
        updateLiveWPM(elapsedTime);
        
        // Periodically predict WPM
        if (elapsedTime > 5 && currentTime - lastPredictionTime > 5000) { // Every 5 seconds after first 5 seconds
            predictWPM(elapsedTime);
            lastPredictionTime = currentTime;
        }
    }
    
    // Handle user input
    function handleInput(e) {
        if (!testActive) return;
        
        const typedText = userInput.value;
        const currentTime = new Date().getTime();
        const elapsedTimeInSeconds = (currentTime - startTime) / 1000;
        
        // Calculate current WPM for display
        updateLiveWPM(elapsedTimeInSeconds);
        
        // Check if test is complete
        if (typedText.length >= originalText.length) {
            endTest();
        }
    }
    
    // Record keystroke data for analysis
    function recordKeystroke(e) {
        if (!testActive) return;
        
        // Don't record modifier keys
        if (e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt' || 
            e.key === 'Meta' || e.key === 'CapsLock' || e.key === 'Tab') {
            return;
        }
        
        keystrokeData.push({
            key: e.key,
            keyCode: e.keyCode,
            timestamp: new Date().getTime() - startTime, // ms since test start
            shiftKey: e.shiftKey,
            position: userInput.value.length
        });
    }
    
    // Update the live WPM display
    function updateLiveWPM(elapsedTimeInSeconds) {
        if (elapsedTimeInSeconds <= 0) return;
        
        const typedText = userInput.value;
        const wordsTyped = typedText.length / 5; // standard: 5 chars = 1 word
        const minutes = elapsedTimeInSeconds / 60;
        
        // Calculate WPM
        const currentWPM = Math.round(wordsTyped / minutes);
        wpmDisplay.textContent = currentWPM;
        
        // Calculate basic accuracy
        let correctChars = 0;
        for (let i = 0; i < typedText.length && i < originalText.length; i++) {
            if (typedText[i] === originalText[i]) {
                correctChars++;
            }
        }
        
        const currentAccuracy = Math.round((correctChars / Math.max(1, typedText.length)) * 100);
        accuracyDisplay.textContent = `${currentAccuracy}%`;
    }
    
    // Predict final WPM based on current progress
    function predictWPM(elapsedTimeInSeconds) {
        if (elapsedTimeInSeconds < 5) return; // Need at least 5 seconds of data
        
        const typedText = userInput.value;
        
        // Send data to backend for prediction
        fetch('/api/predict-wpm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                partial_text: typedText,
                time_elapsed: elapsedTimeInSeconds,
                keystroke_data: keystrokeData
            })
        })
        .then(response => response.json())
        .then(data => {
            predictedWpmDisplay.textContent = `${Math.round(data.predicted_wpm)} WPM`;
        })
        .catch(error => {
            console.error('Error predicting WPM:', error);
            predictedWpmDisplay.textContent = 'Prediction unavailable';
        });
    }
    
    // End the typing test
    function endTest() {
        testActive = false;
        clearInterval(timerInterval);
        userInput.disabled = true;
        
        const endTime = new Date().getTime();
        const elapsedTimeInSeconds = (endTime - startTime) / 1000;
        
        // Display results section
        resultsSection.style.display = 'block';
        
        // Hide end test button
        endButton.style.display = 'none';
        
        // Submit results to backend
        submitResults(elapsedTimeInSeconds);
    }
    
    // Submit test results to the backend
    function submitResults(timeTaken) {
        const typedText = userInput.value;
        
        fetch('/api/submit-test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original_text: originalText,
                typed_text: typedText,
                time_taken: timeTaken,
                keystroke_data: keystrokeData,
                difficulty: testDifficulty
            })
        })
        .then(response => response.json())
        .then(data => {
            // Update detailed results
            wpmDisplay.textContent = data.wpm;
            accuracyDisplay.textContent = `${data.accuracy}%`;
            
            // Display error details
            displayErrorAnalysis(data.error_analysis);
            
            // Display suggestions
            displaySuggestions(data.suggestions);
            
            // Show prediction
            if (data.prediction && data.prediction.status === 'success') {
                const predictionElem = document.createElement('div');
                predictionElem.innerHTML = `
                    <h4>Performance Prediction</h4>
                    <p>Your current average: <strong>${data.prediction.current_avg} WPM</strong></p>
                    <p>Predicted future speed: <strong>${data.prediction.predicted} WPM</strong></p>
                    <p>Potential improvement: <strong>${data.prediction.improvement}%</strong></p>
                `;
                resultsSection.appendChild(predictionElem);
            }
        })
        .catch(error => {
            console.error('Error submitting results:', error);
            errorDetails.innerHTML = '<p>Error analyzing your test results. Please try again.</p>';
        });
    }
    
    // Display error analysis
    function displayErrorAnalysis(errorAnalysis) {
        if (!errorAnalysis) return;
        
        let errorHTML = `<h4>Error Analysis</h4>`;
        
        // Common errors
        if (errorAnalysis.common_errors && errorAnalysis.common_errors.length > 0) {
            errorHTML += '<p><strong>Most Common Errors:</strong></p><ul>';
            errorAnalysis.common_errors.forEach(error => {
                const [errorPattern, count] = error;
                errorHTML += `<li>${errorPattern} (${count} times)</li>`;
            });
            errorHTML += '</ul>';
        }
        
        // Word errors
        if (errorAnalysis.word_errors && errorAnalysis.word_errors.length > 0) {
            errorHTML += '<p><strong>Word Errors:</strong></p><ul>';
            const maxDisplayErrors = Math.min(5, errorAnalysis.word_errors.length);
            for (let i = 0; i < maxDisplayErrors; i++) {
                const error = errorAnalysis.word_errors[i];
                errorHTML += `<li>Typed "${error.typed}" instead of "${error.original}"</li>`;
            }
            errorHTML += '</ul>';
        }
        
        errorDetails.innerHTML = errorHTML;
    }
    
    // Display typing suggestions
    function displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            suggestionsList.innerHTML = '<p>No specific suggestions available. Keep practicing!</p>';
            return;
        }
        
        let suggestionsHTML = '<h4>Suggestions for Improvement</h4><ul>';
        suggestions.forEach(suggestion => {
            suggestionsHTML += `<li>${suggestion}</li>`;
        });
        suggestionsHTML += '</ul>';
        
        suggestionsList.innerHTML = suggestionsHTML;
    }
    
    // Initialize the typing test module
    initialize();
});
