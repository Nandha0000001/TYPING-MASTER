import os
import json 
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.types import TypeDecorator
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Custom JSON type for SQLite
class JSONEncodedDict(TypeDecorator):
    """Represents a JSON structure as a text-based column."""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

# Initialize SQLAlchemy
db = SQLAlchemy()

class TypingTest(db.Model):
    """Model for storing typing test data."""
    __tablename__ = 'typing_tests'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('user_profiles.user_id'))
    original_text = Column(Text)
    typed_text = Column(Text)
    wpm = Column(Float)
    accuracy = Column(Float)
    time_taken = Column(Float)  # in seconds
    difficulty = Column(String(20))
    timestamp = Column(DateTime, default=datetime.now)
    error_details = Column(MutableDict.as_mutable(JSONEncodedDict), default={})
    keystroke_data = Column(MutableList.as_mutable(JSONEncodedDict), default=[])

class GameResult(db.Model):
    """Model for storing game results."""
    __tablename__ = 'game_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('user_profiles.user_id'))
    score = Column(Integer)
    words_typed = Column(Integer)
    accuracy = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)
    difficulty = Column(String(20))

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))
    registered_on = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # One-to-one relationship with UserProfile
    profile_id = Column(String(36), ForeignKey('user_profiles.user_id'), unique=True)
    profile = relationship("UserProfile", backref=db.backref("user", uselist=False))
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the ID for Flask-Login."""
        return str(self.id)


class LessonProgress(db.Model):
    """Model for storing lesson progress."""
    __tablename__ = 'lesson_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('user_profiles.user_id'))
    lesson_id = Column(String(10))
    completed = Column(Integer, default=0)  # 0=False, 1=True
    attempts = Column(Integer, default=0)
    best_score = Column(Float, default=0)

class UserProfile(db.Model):
    """Model for storing user profile data."""
    __tablename__ = 'user_profiles'
    
    user_id = Column(String(36), primary_key=True)
    error_statistics = Column(MutableDict.as_mutable(JSONEncodedDict), default={})
    
    # Relationships
    tests = relationship("TypingTest", backref="user", lazy=True)
    game_results = relationship("GameResult", backref="user", lazy=True)
    lesson_progresses = relationship("LessonProgress", backref="user", lazy=True)
    
    def add_test(self, test: TypingTest) -> None:
        """Add a new typing test to the user profile."""
        # No need to append manually, SQLAlchemy handles the relationship
        db.session.add(test)
        db.session.commit()
    
    def add_game_result(self, game_data: Dict[str, Any]) -> None:
        """Add a new game result to the user profile."""
        game_result = GameResult(
            user_id=self.user_id,
            score=game_data.get('score', 0),
            words_typed=game_data.get('words_typed', 0),
            accuracy=game_data.get('accuracy', 0),
            difficulty=game_data.get('difficulty', 'medium')
        )
        db.session.add(game_result)
        db.session.commit()
    
    def update_lesson_progress(self, lesson_id: str, completed: bool, score: Optional[float] = None) -> None:
        """Update progress for a specific lesson."""
        # Find existing lesson progress or create new
        lesson_progress = LessonProgress.query.filter_by(
            user_id=self.user_id, 
            lesson_id=lesson_id
        ).first()
        
        if not lesson_progress:
            lesson_progress = LessonProgress(
                user_id=self.user_id,
                lesson_id=lesson_id,
                completed=0,
                attempts=0,
                best_score=0
            )
            db.session.add(lesson_progress)
        
        # Update values
        lesson_progress.attempts += 1
        
        if completed:
            lesson_progress.completed = 1
        
        if score and (score > lesson_progress.best_score):
            lesson_progress.best_score = score
        
        db.session.commit()
    
    def update_error_statistics(self, error_data: Dict[str, Any]) -> None:
        """Update error statistics based on new typing test data."""
        # Initialize error statistics if not present
        if not self.error_statistics:
            self.error_statistics = {
                'character_errors': {},
                'word_errors': [],
                'most_common_errors': {},
                'total_errors': 0,
                'total_characters': 0
            }
        
        # Update character error counts
        for char, count in error_data.get('character_errors', {}).items():
            if char in self.error_statistics['character_errors']:
                self.error_statistics['character_errors'][char] += count
            else:
                self.error_statistics['character_errors'][char] = count
        
        # Add word errors
        self.error_statistics['word_errors'].extend(error_data.get('word_errors', []))
        
        # Update total error and character counts
        self.error_statistics['total_errors'] += error_data.get('total_errors', 0)
        self.error_statistics['total_characters'] += error_data.get('total_characters', 0)
        
        # Recalculate most common errors
        char_errors = self.error_statistics['character_errors']
        self.error_statistics['most_common_errors'] = dict(
            sorted(char_errors.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Save changes to database
        db.session.commit()
    
    def get_average_wpm(self) -> float:
        """Calculate the average WPM across all tests."""
        from sqlalchemy import func
        avg_wpm = db.session.query(func.avg(TypingTest.wpm)).filter(TypingTest.user_id == self.user_id).scalar()
        return round(avg_wpm or 0.0, 2)
    
    def get_average_accuracy(self) -> float:
        """Calculate the average accuracy across all tests."""
        from sqlalchemy import func
        avg_accuracy = db.session.query(func.avg(TypingTest.accuracy)).filter(TypingTest.user_id == self.user_id).scalar()
        return round(avg_accuracy or 0.0, 2)
    
    def get_historical_wpm(self) -> List[Dict[str, Any]]:
        """Get historical WPM data for visualization."""
        tests = TypingTest.query.filter_by(user_id=self.user_id).order_by(TypingTest.timestamp).all()
        return [
            {'timestamp': test.timestamp.isoformat(), 'wpm': test.wpm}
            for test in tests
        ]
    
    def get_historical_accuracy(self) -> List[Dict[str, Any]]:
        """Get historical accuracy data for visualization."""
        tests = TypingTest.query.filter_by(user_id=self.user_id).order_by(TypingTest.timestamp).all()
        return [
            {'timestamp': test.timestamp.isoformat(), 'accuracy': test.accuracy}
            for test in tests
        ]
