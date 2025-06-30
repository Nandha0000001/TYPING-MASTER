// Typing Lessons Module
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const lessonTitle = document.getElementById('lesson-title');
    const lessonDescription = document.getElementById('lesson-description');
    const lessonContent = document.getElementById('lesson-content');
    const lessonInput = document.getElementById('lesson-input');
    const lessonProgress = document.getElementById('lesson-progress');
    const lessonSelector = document.getElementById('lesson-selector');
    const startLessonBtn = document.getElementById('start-lesson-btn');
    const lessonResultsSection = document.getElementById('lesson-results');
    const lessonAccuracyDisplay = document.getElementById('lesson-accuracy');
    const lessonWpmDisplay = document.getElementById('lesson-wpm');
    const lessonCompletionMessage = document.getElementById('lesson-completion');
    
    // Lesson state
    let currentLesson = null;
    let lessonActive = false;
    let startTime = null;
    let originalText = '';
    let completedChars = 0;
    let errorCount = 0;
    
    // Initialize the lesson module
    function initialize() {
        // Event listeners
        if (lessonSelector) {
            lessonSelector.addEventListener('change', selectLesson);
        }
        
        if (startLessonBtn) {
            startLessonBtn.addEventListener('click', startLesson);
        }
        
        if (lessonInput) {
            lessonInput.addEventListener('input', checkLessonInput);
            lessonInput.disabled = true;
        }
        
        // Hide results section initially
        if (lessonResultsSection) {
            lessonResultsSection.style.display = 'none';
        }
        
        // Load the first lesson by default
        loadLesson('1');
    }
    
    // Load a lesson by ID
    function loadLesson(lessonId) {
        fetch(`/api/get-lesson?lesson_id=${lessonId}`)
            .then(response => response.json())
            .then(data => {
                currentLesson = data;
                displayLessonDetails();
            })
            .catch(error => {
                console.error('Error loading lesson:', error);
                lessonContent.textContent = 'Error loading lesson. Please try again.';
            });
    }
    
    // Display lesson details in the UI
    function displayLessonDetails() {
        if (!currentLesson) return;
        
        lessonTitle.textContent = currentLesson.title;
        lessonDescription.textContent = currentLesson.description;
        lessonContent.textContent = currentLesson.content;
        
        // Reset lesson state
        lessonActive = false;
        lessonInput.value = '';
        lessonInput.disabled = true;
        startLessonBtn.textContent = 'Start Lesson';
        
        // Hide results
        if (lessonResultsSection) {
            lessonResultsSection.style.display = 'none';
        }
        
        // Reset progress bar
        updateProgressBar(0);
    }
    
    // Handle lesson selection
    function selectLesson() {
        const lessonId = lessonSelector.value;
        loadLesson(lessonId);
    }
    
    // Start the current lesson
    function startLesson() {
        if (!currentLesson) return;
        
        if (lessonActive) {
            // If lesson is already active, this acts as a restart
            displayLessonDetails();
            return;
        }
        
        // Initialize lesson state
        originalText = currentLesson.content;
        lessonActive = true;
        startTime = new Date().getTime();
        completedChars = 0;
        errorCount = 0;
        
        // Enable input and focus
        lessonInput.disabled = false;
        lessonInput.focus();
        
        // Change button text
        startLessonBtn.textContent = 'Restart Lesson';
        
        // Hide results if visible
        if (lessonResultsSection) {
            lessonResultsSection.style.display = 'none';
        }
        
        // Reset progress bar
        updateProgressBar(0);
    }
    
    // Check user input against the lesson text
    function checkLessonInput() {
        if (!lessonActive) return;
        
        const typedText = lessonInput.value;
        let correct = true;
        
        // Compare typed text with original text character by character
        for (let i = 0; i < typedText.length; i++) {
            if (i >= originalText.length || typedText[i] !== originalText[i]) {
                correct = false;
                break;
            }
        }
        
        // Update UI based on correctness
        if (correct) {
            lessonInput.classList.remove('is-invalid');
            lessonInput.classList.add('is-valid');
            completedChars = typedText.length;
        } else {
            lessonInput.classList.remove('is-valid');
            lessonInput.classList.add('is-invalid');
            errorCount++;
        }
        
        // Update progress
        const progressPercentage = (completedChars / originalText.length) * 100;
        updateProgressBar(progressPercentage);
        
        // Check if lesson is complete
        if (typedText.length >= originalText.length && correct) {
            completeLesson();
        }
    }
    
    // Update the progress bar
    function updateProgressBar(percentage) {
        if (lessonProgress) {
            lessonProgress.style.width = `${percentage}%`;
            lessonProgress.setAttribute('aria-valuenow', percentage);
        }
    }
    
    // Complete the current lesson
    function completeLesson() {
        lessonActive = false;
        lessonInput.disabled = true;
        
        // Calculate stats
        const endTime = new Date().getTime();
        const timeTaken = (endTime - startTime) / 1000; // in seconds
        const accuracy = Math.max(0, 100 - ((errorCount / originalText.length) * 100));
        const wpm = ((originalText.length / 5) / (timeTaken / 60)); // characters/5 per minute
        
        // Display results
        if (lessonResultsSection) {
            lessonResultsSection.style.display = 'block';
            lessonAccuracyDisplay.textContent = `${Math.round(accuracy)}%`;
            lessonWpmDisplay.textContent = Math.round(wpm);
            lessonCompletionMessage.textContent = 'Lesson completed successfully!';
        }
        
        // Submit lesson completion to server
        submitLessonCompletion(accuracy, wpm);
    }
    
    // Submit lesson completion to the server
    function submitLessonCompletion(accuracy, wpm) {
        if (!currentLesson) return;
        
        fetch('/api/update-lesson-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lesson_id: currentLesson.id,
                completed: true,
                score: wpm,
                accuracy: accuracy
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Lesson progress updated successfully');
        })
        .catch(error => {
            console.error('Error updating lesson progress:', error);
        });
    }
    
    // Initialize the module
    initialize();
});
