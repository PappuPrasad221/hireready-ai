import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, List, Tuple
import time
from datetime import datetime

class BehaviorTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks indices
        self.left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.right_eye_indices = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        # Face orientation landmarks
        self.face_orientation_indices = [1, 33, 263, 61, 291]  # Nose tip, left eye, right eye, left mouth, right mouth
        
        # Tracking state
        self.tracking_data = {
            'eye_contact_percentage': 0,
            'attention_percentage': 0,
            'face_detected': False,
            'head_position': 'center',
            'engagement_level': 0,
            'distraction_events': [],
            'tracking_duration': 0
        }
        
        # Metrics history
        self.metrics_history = []
        self.start_time = None
    
    async def analyze_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavior data from various sources"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'eye_contact': 0,
            'attention': 0,
            'engagement': 0,
            'face_detected': False,
            'head_position': 'center',
            'confidence_level': 0,
            'recommendations': []
        }
        
        # Process different types of behavior data
        if 'video_frame' in behavior_data:
            video_analysis = await self._analyze_video_frame(behavior_data['video_frame'])
            analysis.update(video_analysis)
        
        if 'audio_data' in behavior_data:
            audio_analysis = await self._analyze_audio_features(behavior_data['audio_data'])
            analysis.update(audio_analysis)
        
        if 'interaction_data' in behavior_data:
            interaction_analysis = await self._analyze_interaction_patterns(behavior_data['interaction_data'])
            analysis.update(interaction_analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_behavior_recommendations(analysis)
        
        return analysis
    
    async def _analyze_video_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """Analyze video frame for facial expressions and eye contact"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {'face_detected': False, 'error': 'Invalid frame data'}
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            analysis = {
                'face_detected': results.multi_face_landmarks is not None,
                'eye_contact': 0,
                'head_position': 'center',
                'facial_expressions': {}
            }
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # Analyze eye contact
                eye_contact = self._calculate_eye_contact(landmarks)
                analysis['eye_contact'] = eye_contact
                
                # Analyze head position
                head_position = self._calculate_head_position(landmarks)
                analysis['head_position'] = head_position
                
                # Analyze facial expressions
                expressions = self._analyze_facial_expressions(landmarks)
                analysis['facial_expressions'] = expressions
                
                # Calculate attention based on eye contact and head position
                attention = self._calculate_attention(eye_contact, head_position)
                analysis['attention'] = attention
            
            return analysis
            
        except Exception as e:
            return {'face_detected': False, 'error': str(e)}
    
    def _calculate_eye_contact(self, landmarks) -> float:
        """Calculate eye contact percentage based on eye landmarks"""
        try:
            # Get eye landmarks
            left_eye = [landmarks.landmark[i] for i in self.left_eye_indices]
            right_eye = [landmarks.landmark[i] for i in self.right_eye_indices]
            
            # Calculate eye openness (simple approximation)
            left_eye_openness = self._calculate_eye_openness(left_eye)
            right_eye_openness = self._calculate_eye_openness(right_eye)
            
            # Average eye openness
            avg_openness = (left_eye_openness + right_eye_openness) / 2
            
            # Estimate gaze direction (simplified - would need more sophisticated approach)
            gaze_direction = self._estimate_gaze_direction(left_eye, right_eye)
            
            # Combine factors for eye contact score
            eye_contact_score = (avg_openness * 0.6 + gaze_direction * 0.4) * 100
            
            return min(max(eye_contact_score, 0), 100)
            
        except Exception:
            return 0
    
    def _calculate_eye_openness(self, eye_landmarks: List) -> float:
        """Calculate how open the eye is"""
        try:
            # Simple calculation using vertical distance between eye landmarks
            top_points = eye_landmarks[1:3]  # Upper eye landmarks
            bottom_points = eye_landmarks[4:6]  # Lower eye landmarks
            
            if len(top_points) >= 2 and len(bottom_points) >= 2:
                top_y = (top_points[0].y + top_points[1].y) / 2
                bottom_y = (bottom_points[0].y + bottom_points[1].y) / 2
                openness = abs(top_y - bottom_y)
                
                # Normalize to 0-1 range
                return min(openness * 10, 1.0)
            
            return 0.5  # Default if calculation fails
            
        except Exception:
            return 0.5
    
    def _estimate_gaze_direction(self, left_eye: List, right_eye: List) -> float:
        """Estimate if user is looking at camera (simplified)"""
        try:
            # Calculate eye centers
            left_center = self._calculate_eye_center(left_eye)
            right_center = self._calculate_eye_center(right_eye)
            
            # Check if eyes are roughly centered and facing forward
            # This is a very simplified approach
            center_x = (left_center[0] + right_center[0]) / 2
            
            # Assuming camera is at center (x=0.5)
            distance_from_center = abs(center_x - 0.5)
            
            # Convert to 0-1 scale (closer to center = better)
            gaze_score = 1.0 - min(distance_from_center * 2, 1.0)
            
            return gaze_score
            
        except Exception:
            return 0.5
    
    def _calculate_eye_center(self, eye_landmarks: List) -> Tuple[float, float]:
        """Calculate the center point of an eye"""
        if len(eye_landmarks) >= 4:
            avg_x = sum(landmark.x for landmark in eye_landmarks[:4]) / 4
            avg_y = sum(landmark.y for landmark in eye_landmarks[:4]) / 4
            return (avg_x, avg_y)
        return (0.5, 0.5)
    
    def _calculate_head_position(self, landmarks) -> str:
        """Calculate head position based on facial landmarks"""
        try:
            # Get key facial landmarks for head position
            nose_tip = landmarks.landmark[1]
            left_eye = landmarks.landmark[33]
            right_eye = landmarks.landmark[263]
            
            # Calculate head tilt and rotation
            eye_center_x = (left_eye.x + right_eye.x) / 2
            nose_offset_x = nose_tip.x - eye_center_x
            
            # Determine position based on offsets
            if abs(nose_offset_x) < 0.05:
                return 'center'
            elif nose_offset_x > 0:
                return 'right'
            else:
                return 'left'
                
        except Exception:
            return 'center'
    
    def _analyze_facial_expressions(self, landmarks) -> Dict[str, float]:
        """Analyze basic facial expressions"""
        expressions = {
            'smiling': 0.0,
            'confused': 0.0,
            'engaged': 0.0,
            'neutral': 0.0
        }
        
        try:
            # Get mouth landmarks for smile detection
            mouth_left = landmarks.landmark[61]
            mouth_right = landmarks.landmark[291]
            mouth_top = landmarks.landmark[13]
            mouth_bottom = landmarks.landmark[14]
            
            # Calculate mouth curvature (simplified smile detection)
            mouth_width = abs(mouth_right.x - mouth_left.x)
            mouth_height = abs(mouth_bottom.y - mouth_top.y)
            
            if mouth_height > 0.02 and mouth_width > 0.15:
                expressions['smiling'] = min(mouth_height * 20, 1.0)
            else:
                expressions['neutral'] = 0.8
            
            # Get eyebrow landmarks for engagement/confusion
            left_eyebrow = landmarks.landmark[70]
            right_eyebrow = landmarks.landmark[300]
            
            # Simple engagement based on eyebrow position
            avg_eyebrow_y = (left_eyebrow.y + right_eyebrow.y) / 2
            if avg_eyebrow_y < 0.2:  # Raised eyebrows
                expressions['engaged'] = 0.7
            elif avg_eyebrow_y > 0.3:  # Lowered eyebrows
                expressions['confused'] = 0.5
            
        except Exception:
            pass
        
        return expressions
    
    def _calculate_attention(self, eye_contact: float, head_position: str) -> float:
        """Calculate overall attention score"""
        base_attention = eye_contact
        
        # Adjust based on head position
        if head_position == 'center':
            position_bonus = 10
        elif head_position in ['left', 'right']:
            position_bonus = -5
        else:
            position_bonus = 0
        
        attention_score = base_attention + position_bonus
        return min(max(attention_score, 0), 100)
    
    async def _analyze_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio for speaking patterns and confidence"""
        analysis = {
            'speaking_pace': 0,
            'voice_clarity': 0,
            'confidence_indicators': {},
            'filler_words': 0
        }
        
        try:
            # This would require audio processing libraries
            # For now, return mock values
            analysis['speaking_pace'] = 145  # words per minute
            analysis['voice_clarity'] = 0.8
            analysis['confidence_indicators'] = {
                'steady_pace': 0.8,
                'clear_volume': 0.7,
                'minimal_fillers': 0.6
            }
            analysis['filler_words'] = 3
            
        except Exception:
            pass
        
        return analysis
    
    async def _analyze_interaction_patterns(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        analysis = {
            'response_time': 0,
            'engagement_level': 0,
            'participation_score': 0
        }
        
        try:
            # Analyze response time
            if 'response_start_time' in interaction_data and 'question_time' in interaction_data:
                response_time = interaction_data['response_start_time'] - interaction_data['question_time']
                analysis['response_time'] = response_time
            
            # Calculate engagement based on various factors
            engagement_factors = [
                interaction_data.get('answered_questions', 0) / 5,  # Assuming 5 questions
                1.0 if interaction_data.get('no_interruptions', True) else 0.5,
                min(interaction_data.get('answer_length', 100) / 50, 1.0)
            ]
            
            analysis['engagement_level'] = sum(engagement_factors) / len(engagement_factors) * 100
            analysis['participation_score'] = analysis['engagement_level']
            
        except Exception:
            pass
        
        return analysis
    
    def _generate_behavior_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on behavior analysis"""
        recommendations = []
        
        # Eye contact recommendations
        if analysis.get('eye_contact', 0) < 60:
            recommendations.append("Try to maintain more eye contact by looking directly at the camera")
        
        # Attention recommendations
        if analysis.get('attention', 0) < 70:
            recommendations.append("Stay focused and avoid looking away during the interview")
        
        # Head position recommendations
        if analysis.get('head_position') != 'center':
            recommendations.append("Keep your head centered and facing the camera")
        
        # Facial expression recommendations
        expressions = analysis.get('facial_expressions', {})
        if expressions.get('smiling', 0) < 0.3:
            recommendations.append("Show more positive facial expressions and smile when appropriate")
        
        # Speaking recommendations
        if 'confidence_indicators' in analysis:
            confidence = analysis['confidence_indicators']
            if confidence.get('steady_pace', 0) < 0.6:
                recommendations.append("Speak at a steady, confident pace")
            if confidence.get('clear_volume', 0) < 0.6:
                recommendations.append("Speak clearly and project your voice")
        
        return recommendations
    
    def start_tracking_session(self):
        """Start a new behavior tracking session"""
        self.start_time = time.time()
        self.metrics_history = []
        self.tracking_data = {
            'eye_contact_percentage': 0,
            'attention_percentage': 0,
            'face_detected': False,
            'head_position': 'center',
            'engagement_level': 0,
            'distraction_events': [],
            'tracking_duration': 0
        }
    
    def end_tracking_session(self) -> Dict[str, Any]:
        """End tracking session and return summary"""
        if self.start_time:
            self.tracking_data['tracking_duration'] = time.time() - self.start_time
        
        # Calculate averages from history
        if self.metrics_history:
            avg_eye_contact = sum(m.get('eye_contact', 0) for m in self.metrics_history) / len(self.metrics_history)
            avg_attention = sum(m.get('attention', 0) for m in self.metrics_history) / len(self.metrics_history)
            
            self.tracking_data['eye_contact_percentage'] = avg_eye_contact
            self.tracking_data['attention_percentage'] = avg_attention
        
        return self.tracking_data
    
    def add_metrics_sample(self, metrics: Dict[str, Any]):
        """Add a metrics sample to the history"""
        metrics['timestamp'] = time.time()
        self.metrics_history.append(metrics)
        
        # Keep only last 100 samples
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
