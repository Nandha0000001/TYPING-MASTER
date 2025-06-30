import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

class WPMPredictor:
    """Class for predicting typing speed (WPM) using machine learning."""
    
    def __init__(self):
        """Initialize the WPM predictor."""
        self.model = LinearRegression()
        self.is_trained = False
    
    def _prepare_training_data(self, historical_wpm: List[Dict[str, Any]]) -> np.ndarray:
        """
        Prepare training data from historical WPM data.
        
        Args:
            historical_wpm: List of dictionaries with 'timestamp' and 'wpm' keys
            
        Returns:
            X: Feature array for training
            y: Target array for training
        """
        if not historical_wpm or len(historical_wpm) < 3:
            return None, None
        
        # For simplicity, we'll use the index as a feature
        # In a real application, we might use more features
        X = np.array(range(len(historical_wpm))).reshape(-1, 1)
        y = np.array([entry['wpm'] for entry in historical_wpm])
        
        return X, y
    
    def train(self, historical_wpm: List[Dict[str, Any]]) -> bool:
        """
        Train the WPM prediction model with historical data.
        
        Args:
            historical_wpm: List of dictionaries with 'timestamp' and 'wpm' keys
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        X, y = self._prepare_training_data(historical_wpm)
        
        if X is None or len(X) < 3:
            self.is_trained = False
            return False
        
        try:
            self.model.fit(X, y)
            self.is_trained = True
            return True
        except Exception as e:
            logger.error(f"Error training WPM model: {e}")
            self.is_trained = False
            return False
    
    def predict_future_wpm(self, historical_wpm: List[Dict[str, Any]], 
                          time_ahead: int = 5) -> Dict[str, Any]:
        """
        Predict future WPM based on historical data.
        
        Args:
            historical_wpm: List of dictionaries with 'timestamp' and 'wpm' keys
            time_ahead: Number of future tests to predict
            
        Returns:
            Dict with prediction results
        """
        if not historical_wpm:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough historical data for prediction',
                'current_avg': 0,
                'predicted': 0
            }
        
        # Calculate current average WPM
        recent_wpm = [entry['wpm'] for entry in historical_wpm[-5:]] if len(historical_wpm) >= 5 else [entry['wpm'] for entry in historical_wpm]
        current_avg = sum(recent_wpm) / len(recent_wpm)
        
        # Try to train the model if we have enough data
        if self.train(historical_wpm):
            X, _ = self._prepare_training_data(historical_wpm)
            next_point = np.array([[len(X) + time_ahead - 1]])
            predicted_wpm = self.model.predict(next_point)[0]
            
            # Calculate improvement percentage
            improvement = ((predicted_wpm - current_avg) / current_avg) * 100 if current_avg > 0 else 0
            
            return {
                'status': 'success',
                'current_avg': round(current_avg, 2),
                'predicted': round(predicted_wpm, 2),
                'improvement': round(improvement, 2),
                'confidence': self._calculate_confidence(historical_wpm)
            }
        else:
            # If we can't train a model, use simple averaging
            return {
                'status': 'simple_prediction',
                'message': 'Using simple prediction (not enough data for ML)',
                'current_avg': round(current_avg, 2),
                'predicted': round(current_avg, 2),
                'improvement': 0,
                'confidence': 0.5
            }
    
    def predict_current_test_wpm(self, current_wpm: float, 
                               keystroke_data: List[Dict[str, Any]],
                               historical_wpm: List[Dict[str, Any]]) -> float:
        """
        Predict WPM for the current typing test based on partial data.
        
        Args:
            current_wpm: Current WPM based on partial typing
            keystroke_data: List of keystroke timing data
            historical_wpm: List of historical WPM data
            
        Returns:
            Predicted final WPM for the current test
        """
        # Simple approach: start with current pace
        predicted_wpm = current_wpm
        
        # Factor 1: Typing pattern from keystroke data
        if keystroke_data and len(keystroke_data) > 10:
            # Calculate if the user is slowing down or speeding up
            timestamps = [k.get('timestamp', 0) for k in keystroke_data if k.get('timestamp')]
            if len(timestamps) >= 10:
                first_half = timestamps[:len(timestamps)//2]
                second_half = timestamps[len(timestamps)//2:]
                
                if first_half and second_half:
                    first_avg_interval = sum(first_half[i+1] - first_half[i] for i in range(len(first_half)-1)) / (len(first_half)-1)
                    second_avg_interval = sum(second_half[i+1] - second_half[i] for i in range(len(second_half)-1)) / (len(second_half)-1)
                    
                    if first_avg_interval > 0 and second_avg_interval > 0:
                        # If intervals are decreasing (faster typing), adjust prediction up
                        interval_ratio = first_avg_interval / second_avg_interval
                        predicted_wpm *= min(1.5, interval_ratio)
        
        # Factor 2: Historical performance patterns
        if historical_wpm and len(historical_wpm) >= 3:
            # Use historical average completion pattern
            historical_avg = sum(entry['wpm'] for entry in historical_wpm) / len(historical_wpm)
            
            # Blend predictions (70% current pace, 30% historical pattern)
            predicted_wpm = (0.7 * predicted_wpm) + (0.3 * historical_avg)
        
        return round(predicted_wpm, 2)
    
    def _calculate_confidence(self, historical_wpm: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence level for the prediction.
        
        Args:
            historical_wpm: List of historical WPM data
            
        Returns:
            Confidence score between 0 and 1
        """
        if not self.is_trained or not historical_wpm:
            return 0.0
        
        # More data points = higher confidence, up to a point
        data_points = min(len(historical_wpm) / 10, 1.0)
        
        # Check consistency of historical data
        wpm_values = [entry['wpm'] for entry in historical_wpm]
        if len(wpm_values) >= 3:
            mean_wpm = sum(wpm_values) / len(wpm_values)
            variance = sum((x - mean_wpm) ** 2 for x in wpm_values) / len(wpm_values)
            std_dev = variance ** 0.5
            
            # Lower variance = higher confidence
            # Normalize by mean to get coefficient of variation
            consistency = 1.0 - min(1.0, (std_dev / mean_wpm)) if mean_wpm > 0 else 0.0
        else:
            consistency = 0.5  # Neutral consistency for little data
        
        # Overall confidence is a weighted combination
        confidence = (0.7 * data_points) + (0.3 * consistency)
        
        return round(confidence, 2)


class KeystrokeDynamicsAnalyzer:
    """Class for analyzing keystroke dynamics patterns."""
    
    def __init__(self):
        """Initialize the keystroke dynamics analyzer."""
        self.baseline_intervals = {}  # Average intervals per key
        self.baseline_established = False
    
    def analyze(self, keystroke_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze keystroke dynamics from typing test data.
        
        Args:
            keystroke_data: List of keystroke events with timestamps and keys
            
        Returns:
            Dict with keystroke dynamics analysis
        """
        if not keystroke_data or len(keystroke_data) < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough keystroke data for analysis'
            }
        
        # Calculate intervals between keystrokes
        intervals = []
        key_intervals = {}
        
        for i in range(1, len(keystroke_data)):
            prev = keystroke_data[i-1]
            curr = keystroke_data[i]
            
            if prev.get('timestamp') and curr.get('timestamp'):
                interval = curr['timestamp'] - prev['timestamp']
                key = curr.get('key', '')
                
                # Filter out extremely long pauses (e.g., user took a break)
                if interval < 5000:  # 5 seconds max
                    intervals.append(interval)
                    
                    if key:
                        if key not in key_intervals:
                            key_intervals[key] = []
                        key_intervals[key].append(interval)
        
        # Update baseline if needed
        if not self.baseline_established and len(keystroke_data) > 50:
            self._update_baseline(key_intervals)
        
        # Calculate average interval
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Find keys with slow typing
        slow_keys = []
        for key, key_times in key_intervals.items():
            if len(key_times) >= 3:  # Only consider keys with enough data
                avg_key_time = sum(key_times) / len(key_times)
                if avg_key_time > (avg_interval * 1.5):  # If 50% slower than average
                    slow_keys.append(key)
        
        # Calculate typing rhythm consistency
        rhythm_consistency = self._calculate_rhythm_consistency(intervals)
        
        # Detect fatigue patterns
        fatigue_detected, fatigue_point = self._detect_fatigue(intervals)
        
        return {
            'status': 'success',
            'avg_interval': round(avg_interval, 2),
            'rhythm_consistency': round(rhythm_consistency, 2),
            'slow_keys': slow_keys[:5],  # Top 5 slowest keys
            'fatigue_detected': fatigue_detected,
            'fatigue_point': fatigue_point if fatigue_detected else None,
            'total_keystrokes': len(keystroke_data)
        }
    
    def _update_baseline(self, key_intervals: Dict[str, List[float]]) -> None:
        """
        Update baseline intervals for each key.
        
        Args:
            key_intervals: Dict mapping keys to their timing intervals
        """
        for key, intervals in key_intervals.items():
            if len(intervals) >= 5:  # Only establish baseline with enough samples
                self.baseline_intervals[key] = sum(intervals) / len(intervals)
        
        if len(self.baseline_intervals) >= 10:  # Need baselines for at least 10 keys
            self.baseline_established = True
    
    def _calculate_rhythm_consistency(self, intervals: List[float]) -> float:
        """
        Calculate typing rhythm consistency based on interval variance.
        
        Args:
            intervals: List of time intervals between keystrokes
            
        Returns:
            Consistency score between 0 and 100
        """
        if not intervals or len(intervals) < 5:
            return 50.0  # Neutral score for insufficient data
        
        mean = sum(intervals) / len(intervals)
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # Calculate coefficient of variation (normalized standard deviation)
        cv = std_dev / mean if mean > 0 else 1.0
        
        # Convert to consistency score (0-100)
        # Lower CV means higher consistency
        consistency = max(0, min(100, 100 - (cv * 50)))
        
        return consistency
    
    def _detect_fatigue(self, intervals: List[float]) -> tuple:
        """
        Detect signs of typing fatigue based on interval patterns.
        
        Args:
            intervals: List of time intervals between keystrokes
            
        Returns:
            Tuple of (fatigue_detected, fatigue_point)
        """
        if not intervals or len(intervals) < 20:
            return False, None
        
        # Use moving average to smooth the data
        window_size = min(10, len(intervals) // 5)
        moving_avgs = []
        
        for i in range(len(intervals) - window_size + 1):
            window = intervals[i:i+window_size]
            moving_avgs.append(sum(window) / window_size)
        
        # Check if intervals are consistently increasing (sign of fatigue)
        fatigue_threshold = 1.3  # 30% increase in typing interval
        
        # Compare first quarter with last quarter
        first_quarter = moving_avgs[:len(moving_avgs)//4]
        last_quarter = moving_avgs[-len(moving_avgs)//4:]
        
        if first_quarter and last_quarter:
            first_avg = sum(first_quarter) / len(first_quarter)
            last_avg = sum(last_quarter) / len(last_quarter)
            
            if last_avg > (first_avg * fatigue_threshold):
                # Find approximate point where fatigue begins
                fatigue_point = None
                
                for i in range(len(moving_avgs) // 2, len(moving_avgs)):
                    if moving_avgs[i] > (first_avg * fatigue_threshold):
                        fatigue_point = i / len(moving_avgs)  # As percentage through the test
                        break
                
                return True, fatigue_point
        
        return False, None
