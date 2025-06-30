import os
import logging
import uuid
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import nltk
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data_manager import DataManager
from ml_models import WPMPredictor, KeystrokeDynamicsAnalyzer
from utils import calculate_wpm, analyze_errors, generate_personalized_suggestions
from models import db, UserProfile, TypingTest, GameResult, LessonProgress, User
from forms import LoginForm, RegistrationForm

# Download NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///typemaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 30}}  # Increase timeout to 30 seconds

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load a user for Flask-Login."""
    return User.query.get(int(user_id))

with app.app_context():
    # Create all database tables
    db.create_all()

# Initialize data manager and ML models
data_manager = DataManager()
wpm_predictor = WPMPredictor()
keystroke_analyzer = KeystrokeDynamicsAnalyzer()


@app.before_request
def check_user_session():
    """Ensure each user has a unique session ID for tracking."""
    # If user is logged in, use their profile_id for the session
    if current_user.is_authenticated and current_user.profile:
        # If session already has the correct user_id, no need to do anything
        if 'user_id' in session and session['user_id'] == current_user.profile.user_id:
            return
        
        # Otherwise, set the session user_id to the user's profile_id
        session['user_id'] = current_user.profile.user_id
        logger.debug(f"Set session user_id to authenticated user's profile_id: {session['user_id']}")
        
    # For anonymous users or users without a session ID, create a temporary one
    elif 'user_id' not in session:
        # Create a new session ID
        session['user_id'] = str(uuid.uuid4())
        logger.debug(f"Created new anonymous session with ID: {session['user_id']}")
        
        # Check if user exists in database, if not create a new profile
        user = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not user:
            user = UserProfile(user_id=session['user_id'], error_statistics={})
            db.session.add(user)
            db.session.commit()
            logger.debug(f"Created new user profile in database: {session['user_id']}")
        
        # Initialize user data in data_manager
        data_manager.initialize_user(session['user_id'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        # Log the user in and remember them if requested
        login_user(user, remember=form.remember_me.data)
        
        # If there was a page the user was trying to access, redirect there
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        # Connect session to user profile
        if user.profile:
            session['user_id'] = user.profile.user_id
            logger.debug(f"Connected session to user profile: {user.profile.user_id}")
        
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """Log out the current user."""
    # Keep the existing session ID for continuity (anonymous browsing)
    session_id = session.get('user_id', str(uuid.uuid4()))
    
    # Log the user out from Flask-Login
    logout_user()
    
    # Assign a new session ID if we don't have one
    if 'user_id' not in session:
        session['user_id'] = session_id
        logger.debug(f"Maintained session ID after logout: {session_id}")
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        # Create a user profile and link it to the user
        profile_id = str(uuid.uuid4())
        profile = UserProfile(user_id=profile_id, error_statistics={})
        
        # Add to database and link
        db.session.add(profile)
        db.session.add(user)
        user.profile = profile
        
        # Commit changes
        db.session.commit()
        
        # Initialize in data manager
        data_manager.initialize_user(profile_id)
        
        # Show success message and redirect to login
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/typing-test')
@login_required
def typing_test():
    """Render the typing test page."""
    return render_template('typing_test.html')


@app.route('/typing-game')
@login_required
def typing_game():
    """Render the typing game page."""
    return render_template('typing_game.html')


@app.route('/lessons')
@login_required
def lessons():
    """Render the typing lessons page."""
    return render_template('lessons.html')


@app.route('/progress')
@login_required
def progress():
    """Render the progress tracking page."""
    return render_template('progress.html')


@app.route('/chatbot')
@login_required
def chatbot():
    """Render the chatbot page for typing-related queries."""
    return render_template('chatbot.html')


# API Endpoints


@app.route('/api/get-text', methods=['GET'])
@login_required
def get_text():
    """Get a typing test text based on difficulty level."""
    difficulty = request.args.get('difficulty', 'medium')
    text = data_manager.get_random_text(difficulty)
    return jsonify({'text': text})


@app.route('/api/get-lesson', methods=['GET'])
@login_required
def get_lesson():
    """Get a typing lesson based on lesson number."""
    lesson_id = request.args.get('lesson_id', '1')
    lesson = data_manager.get_lesson(lesson_id)
    return jsonify(lesson)


@app.route('/api/submit-test', methods=['POST'])
@login_required
def submit_test():
    """Submit typing test results and get analysis."""
    data = request.json
    original_text = data.get('original_text', '')
    typed_text = data.get('typed_text', '')
    time_taken = data.get('time_taken', 0)  # in seconds
    keystroke_data = data.get('keystroke_data', [])

    # Calculate WPM and analyze errors
    wpm = calculate_wpm(original_text, typed_text, time_taken)
    error_analysis = analyze_errors(original_text, typed_text)
    accuracy = error_analysis['accuracy']

    # Save the test results
    user_id = session['user_id']
    difficulty = data.get('difficulty', 'medium')
    
    # Get user profile from database
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id, error_statistics={})
        db.session.add(user_profile)
        db.session.commit()
    
    # Create a new typing test record
    test_id = str(uuid.uuid4())
    typing_test = TypingTest(
        id=test_id,
        user_id=user_id,
        original_text=original_text,
        typed_text=typed_text,
        wpm=wpm,
        accuracy=accuracy,
        time_taken=time_taken,
        difficulty=difficulty,
        error_details=error_analysis,
        keystroke_data=keystroke_data
    )
    
    # Add to database
    db.session.add(typing_test)
    db.session.commit()
    
    # Update error statistics
    user_profile.update_error_statistics(error_analysis)
    
    # For backwards compatibility, also use the data manager
    test_data = {
        'wpm': wpm,
        'accuracy': accuracy,
        'error_analysis': error_analysis,
        'difficulty': difficulty,
        'keystroke_data': keystroke_data
    }
    data_manager.save_test_result(user_id, test_data)

    # Analyze keystroke dynamics
    keystroke_analysis = keystroke_analyzer.analyze(keystroke_data)

    # Get performance prediction
    prediction = wpm_predictor.predict_future_wpm(
        data_manager.get_historical_wpm(user_id))

    # Generate personalized suggestions
    suggestions = generate_personalized_suggestions(
        error_analysis, keystroke_analysis,
        data_manager.get_user_error_statistics(user_id))

    return jsonify({
        'wpm': wpm,
        'accuracy': accuracy,
        'error_analysis': error_analysis,
        'keystroke_analysis': keystroke_analysis,
        'prediction': prediction,
        'suggestions': suggestions
    })


@app.route('/api/predict-wpm', methods=['POST'])
@login_required
def predict_wpm():
    """Predict WPM based on partial typing test data."""
    data = request.json
    partial_text = data.get('partial_text', '')
    time_elapsed = data.get('time_elapsed', 0)
    keystroke_data = data.get('keystroke_data', [])

    # Simple prediction based on current pace
    current_wpm = calculate_wpm("", partial_text, time_elapsed)

    # Advanced prediction using ML model
    user_id = session['user_id']
    historical_data = data_manager.get_historical_wpm(user_id)
    predicted_wpm = wpm_predictor.predict_current_test_wpm(
        current_wpm, keystroke_data, historical_data)

    return jsonify({
        'current_wpm': current_wpm,
        'predicted_wpm': predicted_wpm
    })


@app.route('/api/user-progress', methods=['GET'])
@login_required
def user_progress():
    """Get user's progress data for visualization."""
    user_id = session['user_id']
    
    # Get user from database
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if user_profile:
        # Get data from database models
        wpm_history = user_profile.get_historical_wpm()
        accuracy_history = user_profile.get_historical_accuracy()
        error_statistics = user_profile.error_statistics
    else:
        # Fallback to data manager if user not found in database
        wpm_history = data_manager.get_historical_wpm(user_id)
        accuracy_history = data_manager.get_historical_accuracy(user_id)
        error_statistics = data_manager.get_user_error_statistics(user_id)

    return jsonify({
        'wpm_history': wpm_history,
        'accuracy_history': accuracy_history,
        'error_statistics': error_statistics
    })


@app.route('/api/game-words', methods=['GET'])
@login_required
def game_words():
    """Get random words for the typing game."""
    count = int(request.args.get('count', '10'))
    difficulty = request.args.get('difficulty', 'medium')
    words = data_manager.get_random_words(count, difficulty)
    return jsonify({'words': words})


@app.route('/api/submit-game', methods=['POST'])
@login_required
def submit_game():
    """Submit typing game results."""
    data = request.json
    user_id = session['user_id']
    score = data.get('score', 0)
    words_typed = data.get('words_typed', 0)
    accuracy = data.get('accuracy', 0)
    difficulty = data.get('difficulty', 'medium')

    # Get user profile from database
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id, error_statistics={})
        db.session.add(user_profile)
        db.session.commit()

    # Create a new game result
    game_result = GameResult(
        user_id=user_id,
        score=score,
        words_typed=words_typed,
        accuracy=accuracy,
        difficulty=difficulty
    )
    
    # Add to database
    db.session.add(game_result)
    db.session.commit()

    # For backwards compatibility, also use the data manager
    game_data = {
        'score': score,
        'words_typed': words_typed,
        'accuracy': accuracy,
        'difficulty': difficulty
    }
    data_manager.save_game_result(user_id, game_data)

    return jsonify({'status': 'success'})


@app.route('/api/chatbot-query', methods=['POST'])
@login_required
def chatbot_query():
    """Handle chatbot queries related to typing."""
    data = request.json
    query = data.get('query', '')

    # Simple rule-based responses
    response = data_manager.get_chatbot_response(query)

    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
