// Typing Game Module
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const gameContainer = document.getElementById('game-container');
    const wordDisplay = document.getElementById('word-display');
    const userInput = document.getElementById('game-input');
    const scoreDisplay = document.getElementById('score-display');
    const timeDisplay = document.getElementById('time-display');
    const difficultySelector = document.getElementById('game-difficulty');
    const startButton = document.getElementById('game-start-btn');
    const gameOverModal = document.getElementById('game-over-modal');
    const finalScoreDisplay = document.getElementById('final-score');
    const finalAccuracyDisplay = document.getElementById('final-accuracy');
    const finalWpmDisplay = document.getElementById('final-wpm');
    const playAgainButton = document.getElementById('play-again-btn');
    
    // Game state
    let gameActive = false;
    let score = 0;
    let timeLeft = 60; // 60 seconds game
    let currentWord = '';
    let words = [];
    let correctWords = 0;
    let incorrectWords = 0;
    let startTime;
    let timerInterval;
    let totalKeystrokes = 0;
    let correctKeystrokes = 0;
    let gameDifficulty = 'medium';
    
    // Initialize the game
    function initialize() {
        // Event listeners
        startButton.addEventListener('click', startGame);
        userInput.addEventListener('input', checkInput);
        playAgainButton.addEventListener('click', startGame);
        difficultySelector.addEventListener('change', function() {
            gameDifficulty = this.value;
        });
        
        // Disable input field initially
        userInput.disabled = true;
        
        // Hide game over modal initially
        if (gameOverModal) {
            gameOverModal.style.display = 'none';
        }
    }
    
    // Fetch random words based on difficulty
    function fetchWords() {
        return fetch(`/api/game-words?count=50&difficulty=${gameDifficulty}`)
            .then(response => response.json())
            .then(data => {
                words = data.words;
                return words;
            })
            .catch(error => {
                console.error('Error fetching words:', error);
                words = ['error', 'loading', 'words', 'please', 'refresh'];
                return words;
            });
    }
    
    // Start the game
    function startGame() {
        // Reset game state
        score = 0;
        timeLeft = 60;
        correctWords = 0;
        incorrectWords = 0;
        totalKeystrokes = 0;
        correctKeystrokes = 0;
        
        // Update display
        scoreDisplay.textContent = score;
        timeDisplay.textContent = timeLeft;
        userInput.value = '';
        
        // Hide game over modal if visible
        if (gameOverModal) {
            gameOverModal.style.display = 'none';
        }
        
        // Fetch words and set up game
        fetchWords().then(() => {
            userInput.disabled = false;
            userInput.focus();
            gameActive = true;
            startTime = new Date().getTime();
            
            // Start timer
            clearInterval(timerInterval);
            timerInterval = setInterval(updateTimer, 1000);
            
            // Set first word
            nextWord();
        });
    }
    
    // Update the timer display and check for game end
    function updateTimer() {
        if (!gameActive) return;
        
        timeLeft--;
        timeDisplay.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            endGame();
        }
    }
    
    // Display the next word to type
    function nextWord() {
        if (words.length === 0) {
            fetchWords(); // Refill words if we run out
            return;
        }
        
        const randomIndex = Math.floor(Math.random() * words.length);
        currentWord = words[randomIndex];
        
        // Remove the used word
        words.splice(randomIndex, 1);
        
        // Display the word
        wordDisplay.textContent = currentWord;
        userInput.value = '';
    }
    
    // Check the user's input against the current word
    function checkInput() {
        if (!gameActive) return;
        
        const userWord = userInput.value.trim();
        
        // Track keystrokes for accuracy calculation
        totalKeystrokes += 1;
        
        // Check if the input matches the current word prefix
        if (currentWord.startsWith(userWord)) {
            correctKeystrokes += 1;
            wordDisplay.classList.remove('text-danger');
        } else {
            wordDisplay.classList.add('text-danger');
        }
        
        // Check if word is complete
        if (userWord === currentWord) {
            // Award points (more points for longer/harder words)
            const points = Math.max(1, Math.floor(currentWord.length / 3));
            score += points;
            scoreDisplay.textContent = score;
            
            correctWords++;
            nextWord();
        }
    }
    
    // End the game
    function endGame() {
        gameActive = false;
        clearInterval(timerInterval);
        userInput.disabled = true;
        
        // Calculate final statistics
        const accuracy = totalKeystrokes > 0 ? Math.round((correctKeystrokes / totalKeystrokes) * 100) : 0;
        const totalTime = (new Date().getTime() - startTime) / 1000; // in seconds
        const wpm = Math.round((correctWords * 60) / totalTime); // words per minute
        
        // Display game over screen
        if (gameOverModal) {
            finalScoreDisplay.textContent = score;
            finalAccuracyDisplay.textContent = `${accuracy}%`;
            finalWpmDisplay.textContent = wpm;
            gameOverModal.style.display = 'block';
        }
        
        // Submit game results to server
        submitGameResults(accuracy, wpm);
    }
    
    // Submit game results to the server
    function submitGameResults(accuracy, wpm) {
        fetch('/api/submit-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                score: score,
                words_typed: correctWords + incorrectWords,
                correct_words: correctWords,
                accuracy: accuracy,
                wpm: wpm,
                difficulty: gameDifficulty
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Game results submitted successfully');
        })
        .catch(error => {
            console.error('Error submitting game results:', error);
        });
    }
    
    // Initialize the game module
    initialize();
});
