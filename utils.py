import re
import difflib
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def calculate_wpm(original_text: str, typed_text: str, time_taken_seconds: float) -> float:
    """
    Calculate words per minute (WPM) based on the typed text and time taken.
    
    WPM is calculated as (characters typed / 5) / (time taken in minutes)
    where 5 is the average word length.
    
    Args:
        original_text: The original text that was to be typed
        typed_text: The text that was actually typed
        time_taken_seconds: Time taken to type the text in seconds
        
    Returns:
        float: The calculated WPM
    """
    if time_taken_seconds <= 0:
        return 0.0
    
    # Convert time to minutes
    time_taken_minutes = time_taken_seconds / 60.0
    
    # Use typed_text length for WPM calculation
    char_count = len(typed_text)
    
    # Calculate WPM (characters / 5) / minutes
    # 5 is the standard word length used in typing tests
    wpm = (char_count / 5) / time_taken_minutes
    
    return round(wpm, 2)

def analyze_errors(original_text: str, typed_text: str) -> Dict[str, Any]:
    """
    Analyze typing errors by comparing original text with typed text.
    
    Args:
        original_text: The original text that was to be typed
        typed_text: The text that was actually typed
        
    Returns:
        Dict containing error analysis including:
        - accuracy: Overall accuracy percentage
        - error_count: Total number of errors
        - word_errors: List of incorrectly typed words
        - character_errors: Dict of character-level errors
        - error_positions: List of error positions in the text
    """
    # Tokenize into words using simple split (avoids NLTK tokenization issues)
    original_words = original_text.split()
    typed_words = typed_text.split()
    
    # Initialize error tracking
    total_chars = len(original_text)
    error_count = 0
    word_errors = []
    character_errors = {}
    error_positions = []
    
    # Compare word by word
    for i, (orig_word, typed_word) in enumerate(zip(original_words, typed_words)):
        if orig_word != typed_word:
            word_errors.append({
                'original': orig_word,
                'typed': typed_word,
                'position': i
            })
            
            # Character-level analysis using difflib
            matcher = difflib.SequenceMatcher(None, orig_word, typed_word)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag != 'equal':
                    error_count += max(i2 - i1, j2 - j1)
                    
                    # Track specific character errors
                    if tag == 'replace':
                        for o_idx, t_idx in zip(range(i1, i2), range(j1, j2)):
                            if o_idx < len(orig_word) and t_idx < len(typed_word):
                                error_char = f"{orig_word[o_idx]}->{typed_word[t_idx]}"
                                character_errors[error_char] = character_errors.get(error_char, 0) + 1
                    elif tag == 'delete':
                        for o_idx in range(i1, i2):
                            if o_idx < len(orig_word):
                                error_char = f"{orig_word[o_idx]}->∅"  # missing character
                                character_errors[error_char] = character_errors.get(error_char, 0) + 1
                    elif tag == 'insert':
                        for t_idx in range(j1, j2):
                            if t_idx < len(typed_word):
                                error_char = f"∅->{typed_word[t_idx]}"  # extra character
                                character_errors[error_char] = character_errors.get(error_char, 0) + 1
    
    # Add additional errors for length difference
    len_diff = abs(len(original_words) - len(typed_words))
    if len_diff > 0:
        error_count += len_diff
    
    # Calculate accuracy
    accuracy = max(0, (1 - (error_count / max(1, total_chars))) * 100)
    
    # Common error patterns analysis
    common_errors = sorted(character_errors.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'accuracy': round(accuracy, 2),
        'error_count': error_count,
        'word_errors': word_errors,
        'character_errors': character_errors,
        'common_errors': common_errors,
        'error_positions': error_positions,
        'total_characters': total_chars
    }

def generate_personalized_suggestions(error_analysis: Dict[str, Any], 
                                     keystroke_analysis: Dict[str, Any],
                                     error_statistics: Dict[str, Any]) -> List[str]:
    """
    Generate personalized typing improvement suggestions based on error analysis.
    
    Args:
        error_analysis: Dict containing the current error analysis
        keystroke_analysis: Dict containing keystroke timing analysis
        error_statistics: Dict containing historical error statistics
        
    Returns:
        List of personalized suggestions
    """
    suggestions = []
    
    # Analyze character-specific errors
    if error_analysis.get('character_errors'):
        common_errors = error_analysis.get('common_errors', [])
        if common_errors:
            error_chars = [err[0].split('->')[0] for err in common_errors if '->' in err[0]]
            error_chars = [c for c in error_chars if c != '∅']  # Filter out missing character placeholder
            
            if error_chars:
                suggestions.append(f"Practice keys: {', '.join(error_chars)}")
        
    # Analyze keystroke timing
    if keystroke_analysis.get('slow_keys'):
        slow_keys = keystroke_analysis.get('slow_keys', [])
        if slow_keys:
            suggestions.append(f"Work on speed for keys: {', '.join(slow_keys)}")
    
    # Analyze accuracy issues
    accuracy = error_analysis.get('accuracy', 0)
    if accuracy < 95:
        suggestions.append("Focus on accuracy over speed - slow down and type correctly")
    elif accuracy < 85:
        suggestions.append("Consider practicing with easier texts until accuracy improves")
    
    # Look at historical patterns
    if error_statistics:
        if error_statistics.get('most_common_errors'):
            historical_errors = list(error_statistics.get('most_common_errors', {}).keys())[:3]
            if historical_errors:
                readable_errors = []
                for err in historical_errors:
                    parts = err.split('->')
                    if len(parts) == 2:
                        orig, typed = parts
                        if orig == '∅':
                            readable_errors.append(f"adding '{typed}'")
                        elif typed == '∅':
                            readable_errors.append(f"missing '{orig}'")
                        else:
                            readable_errors.append(f"typing '{typed}' instead of '{orig}'")
                
                if readable_errors:
                    suggestions.append(f"Common mistakes to watch for: {', '.join(readable_errors)}")
    
    # Add general suggestions if few specific ones were generated
    if len(suggestions) < 2:
        suggestions.append("Practice touch typing to avoid looking at the keyboard")
        suggestions.append("Take breaks to prevent fatigue during long typing sessions")
    
    return suggestions

def analyze_keystroke_dynamics(keystroke_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze keystroke dynamics from timing data.
    
    Args:
        keystroke_data: List of keystroke events with timestamps
        
    Returns:
        Dict with keystroke dynamics analysis
    """
    if not keystroke_data or len(keystroke_data) < 2:
        return {'status': 'insufficient_data'}
    
    # Calculate time between keystrokes
    intervals = []
    key_intervals = {}
    
    for i in range(1, len(keystroke_data)):
        prev = keystroke_data[i-1]
        curr = keystroke_data[i]
        
        if prev.get('timestamp') and curr.get('timestamp'):
            interval = curr['timestamp'] - prev['timestamp']
            key = curr.get('key', '')
            
            intervals.append(interval)
            
            if key:
                if key not in key_intervals:
                    key_intervals[key] = []
                key_intervals[key].append(interval)
    
    # Calculate average interval
    avg_interval = sum(intervals) / len(intervals) if intervals else 0
    
    # Find keys with slow typing
    slow_keys = []
    for key, key_times in key_intervals.items():
        if len(key_times) >= 3:  # Only consider keys with enough data
            avg_key_time = sum(key_times) / len(key_times)
            if avg_key_time > (avg_interval * 1.5):  # If 50% slower than average
                slow_keys.append(key)
    
    # Calculate consistency (standard deviation of intervals)
    consistency = 0
    if intervals:
        mean = avg_interval
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        consistency = (1 / (1 + (variance ** 0.5))) * 100  # Higher is more consistent
    
    return {
        'avg_interval': avg_interval,
        'consistency': round(consistency, 2),
        'slow_keys': slow_keys[:5],  # Top 5 slowest keys
        'total_keystrokes': len(keystroke_data)
    }
