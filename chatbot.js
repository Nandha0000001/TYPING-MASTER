// Chatbot Module for Typing Queries
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const messagesDiv = document.getElementById('chat-messages');
    const questionsList = document.getElementById('suggested-questions');
    
    // Suggested questions
    const suggestedQuestions = [
        "How can I improve my typing speed?",
        "What is a good typing speed?",
        "How to measure typing accuracy?",
        "What is touch typing?",
        "How should I position my hands on the keyboard?",
        "What typing exercises do you recommend?",
        "What are common keyboard shortcuts?",
        "How do I type without looking at the keyboard?",
        "What is the proper typing posture?",
        "How can I reduce typing fatigue?"
    ];
    
    // Initialize the chatbot module
    function initialize() {
        // Add event listeners
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
        
        if (messageInput) {
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
        
        // Show welcome message
        addMessage("bot", "Hello! I'm your typing assistant. Ask me anything about typing skills, techniques, or how to improve your speed and accuracy.");
        
        // Display suggested questions
        displaySuggestedQuestions();
    }
    
    // Display list of suggested questions
    function displaySuggestedQuestions() {
        if (!questionsList) return;
        
        questionsList.innerHTML = '';
        
        suggestedQuestions.forEach(question => {
            const questionBtn = document.createElement('button');
            questionBtn.className = 'list-group-item list-group-item-action text-start';
            questionBtn.textContent = question;
            questionBtn.addEventListener('click', function() {
                messageInput.value = question;
                sendMessage();
            });
            
            questionsList.appendChild(questionBtn);
        });
    }
    
    // Send a message to the chatbot
    function sendMessage() {
        if (!messageInput || !messageInput.value.trim()) return;
        
        const query = messageInput.value.trim();
        
        // Add user message to chat
        addMessage("user", query);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        const typingIndicator = addMessage("bot", "Typing...", "typing-indicator");
        
        // Send query to backend
        fetch('/api/chatbot-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            if (typingIndicator) {
                messagesDiv.removeChild(typingIndicator);
            }
            
            // Display bot response
            addMessage("bot", data.response);
        })
        .catch(error => {
            console.error('Error fetching chatbot response:', error);
            
            // Remove typing indicator
            if (typingIndicator) {
                messagesDiv.removeChild(typingIndicator);
            }
            
            // Display error message
            addMessage("bot", "Sorry, I encountered an error processing your request. Please try again.");
        });
    }
    
    // Add a message to the chat
    function addMessage(sender, text, extraClass = "") {
        if (!messagesDiv) return null;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message ${extraClass}`;
        
        if (sender === "bot" && extraClass === "typing-indicator") {
            // Create typing indicator dots
            messageDiv.innerHTML = `
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
        } else {
            // Format the text content with line breaks and links
            const formattedText = formatMessageText(text);
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${formattedText}
                </div>
            `;
        }
        
        messagesDiv.appendChild(messageDiv);
        
        // Scroll to the bottom
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        return messageDiv;
    }
    
    // Format message text with line breaks and links
    function formatMessageText(text) {
        // Convert line breaks
        let formattedText = text.replace(/\n/g, '<br>');
        
        // Convert numbered lists
        formattedText = formattedText.replace(/(\d+\))\s(.*?)(?=<br>|$)/g, '<strong>$1</strong> $2');
        
        // Add bullet points for numbered steps
        formattedText = formattedText.replace(/(\d+\))/g, '• $1');
        
        // Make headings bold
        formattedText = formattedText.replace(/(^|\<br\>)([\w\s]+):(?=\s)/g, '$1<strong>$2:</strong>');
        
        return formattedText;
    }
    
    // Initialize the module
    initialize();
});
