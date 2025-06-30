import os
import pickle
import uuid
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import UserProfile, TypingTest
from text_data import (
    EASY_TEXTS, MEDIUM_TEXTS, HARD_TEXTS,
    EASY_WORDS, MEDIUM_WORDS, HARD_WORDS,
    LESSONS, CHATBOT_RESPONSES
)

logger = logging.getLogger(__name__)

class DataManager:
    """
    Class for managing application data, including user profiles, texts, and lessons.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the DataManager.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.users = {}  # In-memory cache of user profiles
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_user_file_path(self, user_id: str) -> str:
        """
        Get the file path for a user's data file.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            File path for the user's data
        """
        return os.path.join(self.data_dir, f"user_{user_id}.pkl")
    
    def _save_user(self, user_id: str) -> None:
        """
        Save a user's profile to disk.
        
        Args:
            user_id: Unique user identifier
        """
        if user_id in self.users:
            file_path = self._get_user_file_path(user_id)
            with open(file_path, 'wb') as f:
                pickle.dump(self.users[user_id], f)
    
    def _load_user(self, user_id: str) -> Optional[UserProfile]:
        """
        Load a user's profile from disk.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            UserProfile if found, None otherwise
        """
        file_path = self._get_user_file_path(user_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading user profile: {e}")
                return None
        return None
    
    def get_user(self, user_id: str) -> UserProfile:
        """
        Get a user's profile, loading it from disk if necessary.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            UserProfile for the user
        """
        if user_id not in self.users:
            profile = self._load_user(user_id)
            if profile:
                self.users[user_id] = profile
            else:
                self.users[user_id] = UserProfile(user_id=user_id)
        
        return self.users[user_id]
    
    def initialize_user(self, user_id: str) -> None:
        """
        Initialize a new user profile.
        
        Args:
            user_id: Unique user identifier
        """
        if user_id not in self.users:
            self.users[user_id] = UserProfile(user_id=user_id)
            self._save_user(user_id)
            logger.debug(f"Initialized new user profile: {user_id}")
    
    def get_random_text(self, difficulty: str = "medium") -> str:
        """
        Get a random typing test text based on difficulty.
        
        Args:
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Random text for typing test
        """
        if difficulty.lower() == "easy":
            return random.choice(EASY_TEXTS)
        elif difficulty.lower() == "hard":
            return random.choice(HARD_TEXTS)
        else:  # Default to medium
            return random.choice(MEDIUM_TEXTS)
    
    def get_random_words(self, count: int = 10, difficulty: str = "medium") -> List[str]:
        """
        Get random words for typing game based on difficulty.
        
        Args:
            count: Number of words to return
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of random words
        """
        if difficulty.lower() == "easy":
            word_list = EASY_WORDS
        elif difficulty.lower() == "hard":
            word_list = HARD_WORDS
        else:  # Default to medium
            word_list = MEDIUM_WORDS
        
        return random.sample(word_list, min(count, len(word_list)))
    
    def get_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """
        Get a typing lesson by ID.
        
        Args:
            lesson_id: Lesson identifier
            
        Returns:
            Lesson data dictionary
        """
        if lesson_id in LESSONS:
            return LESSONS[lesson_id]
        else:
            return {
                "id": "0",
                "title": "Lesson Not Found",
                "description": "The requested lesson could not be found.",
                "content": "Please select a valid lesson.",
                "difficulty": "N/A"
            }
    
    def save_test_result(self, user_id: str, test_data: Dict[str, Any]) -> None:
        """
        Save a typing test result for a user.
        
        Args:
            user_id: Unique user identifier
            test_data: Dictionary with test results
        """
        user = self.get_user(user_id)
        
        # Create a TypingTest object
        test_id = str(uuid.uuid4())
        test = TypingTest(
            id=test_id,
            user_id=user_id,
            original_text=test_data.get('original_text', ''),
            typed_text=test_data.get('typed_text', ''),
            wpm=test_data.get('wpm', 0),
            accuracy=test_data.get('accuracy', 0),
            time_taken=test_data.get('time_taken', 0),
            difficulty=test_data.get('difficulty', 'medium'),
            error_details=test_data.get('error_analysis', {}),
            keystroke_data=test_data.get('keystroke_data', [])
        )
        
        # Add test to user profile
        user.add_test(test)
        
        # Update error statistics
        if 'error_analysis' in test_data:
            user.update_error_statistics(test_data['error_analysis'])
        
        # Save user profile
        self._save_user(user_id)
        logger.debug(f"Saved test result for user {user_id}: WPM={test.wpm}, Accuracy={test.accuracy}")
    
    def save_game_result(self, user_id: str, game_data: Dict[str, Any]) -> None:
        """
        Save a typing game result for a user.
        
        Args:
            user_id: Unique user identifier
            game_data: Dictionary with game results
        """
        user = self.get_user(user_id)
        
        # Add timestamp to game data
        game_data['timestamp'] = datetime.now().isoformat()
        
        # Add game result to user profile
        user.add_game_result(game_data)
        
        # Save user profile
        self._save_user(user_id)
        logger.debug(f"Saved game result for user {user_id}: Score={game_data.get('score', 0)}")
    
    def update_lesson_progress(self, user_id: str, lesson_id: str, 
                              completed: bool, score: Optional[float] = None) -> None:
        """
        Update a user's progress on a typing lesson.
        
        Args:
            user_id: Unique user identifier
            lesson_id: Lesson identifier
            completed: Whether the lesson was completed
            score: Optional score for the lesson
        """
        user = self.get_user(user_id)
        
        # Update lesson progress
        user.update_lesson_progress(lesson_id, completed, score)
        
        # Save user profile
        self._save_user(user_id)
        logger.debug(f"Updated lesson progress for user {user_id}, lesson {lesson_id}")
    
    def get_historical_wpm(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get historical WPM data for a user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            List of historical WPM data points
        """
        user = self.get_user(user_id)
        return user.get_historical_wpm()
    
    def get_historical_accuracy(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get historical accuracy data for a user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            List of historical accuracy data points
        """
        user = self.get_user(user_id)
        return user.get_historical_accuracy()
    
    def get_user_error_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get error statistics for a user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary with error statistics
        """
        user = self.get_user(user_id)
        return user.error_statistics
    
    def get_chatbot_response(self, query: str) -> str:
        """
        Get a chatbot response for a typing-related query.
        
        Args:
            query: User's query text
            
        Returns:
            Chatbot response text
        """
        query = query.lower()
        
        # Check for exact matches first
        for pattern, response in CHATBOT_RESPONSES.items():
            if pattern.lower() in query:
                return response
        
        # Default response if no match
        return "I'm not sure how to help with that. Try asking about typing speed, accuracy, or how to improve your typing skills."
