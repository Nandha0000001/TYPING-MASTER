# TYPING-MASTER

AI-driven Typing Speed Predictor and Practice Platform developed using Python and Flask. The platform enhances typing skills by offering real-time performance tracking, personalized feedback, and engaging practice modules. It leverages Machine Learning, specifically linear regression, to predict Words Per Minute (WPM) based on historical and live typing data. Natural Language Processing (NLP) is used to evaluate typing accuracy by identifying errors at both the word and character levels. Additionally, the system incorporates keystroke dynamics analysis to understand user typing patterns. It stores and visualizes user progress, providing insights into accuracy trends and common mistakes. this platform provides a comprehensive solution for improving typing speed and accuracy through AIML technologies


System Architecture Overview
Frontend (UI): HTML/CSS + JavaScript for user interaction and test visualization.
Backend (Flask App): Handles routing, test logic, ML prediction, data storage, and NLP evaluation.
Data Persistence: Pickle-based storage of user history, progress, and error statistics.

Typing Test 
Text Generation: Predefined text pools based on difficulty (easy, medium, hard).
Keystroke Logging: Captures keypress and release timestamps for keystroke dynamics.
Live WPM Prediction: Real-time prediction using linear regression on partial input data.


ML & NLP Integration
ML Model (Linear Regression): Predicts WPM using historical data and real-time test behavior.
NLP Accuracy Evaluation: Compares typed and reference texts at token and character level, identifies:
Insertions, deletions, substitutions
Most common character mistakes
Error Analysis: Tracks frequent errors and character patterns to personalize feedback.

User Progress 
Typing History Tracking: Records WPM, accuracy, difficulty, and timestamp for every test.
Graph Data Generation: JSON APIs for WPM and accuracy trends over time.
Suggestion Engine: Recommends lessons based on frequent user errors.




Hardware
Computer/Laptop:
Required for development, testing, and running the application.
Keyboard:
Essential for typing tests and keystroke dynamics analysis.







Software
Python:
The primary programming language used to develop the project.
Flask:
Micro web framework for building the web application and handling API requests.
Machine Learning Libraries:
scikit-learn: Used for implementing linear regression for WPM prediction.
pandas: For data manipulation and storing user progress data.
numpy: For numerical operations and handling data arrays.
Natural Language Processing (NLP):
nltk (Natural Language Toolkit): Used for text analysis and error statistics.
Database:
Pickle & sqlite: For data persistence and saving user progress (since it’s a lightweight project without heavy database needs).



![image](https://github.com/user-attachments/assets/c8f92d06-c832-461a-a028-88085346e50f)
![image](https://github.com/user-attachments/assets/16a75fd0-d581-4c66-996f-2eeae48f8485)
![image](https://github.com/user-attachments/assets/51e0e877-77f0-44db-8b0f-c8215052e7f2)

