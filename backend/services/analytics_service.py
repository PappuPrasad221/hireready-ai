from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

class AnalyticsService:
    def __init__(self):
        # Mock database - in production, this would connect to a real database
        self.mock_data = {
            'user_sessions': {},
            'performance_metrics': {},
            'leaderboard_data': []
        }
        
        # Initialize with some mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock analytics data for testing"""
        # Mock user performance data
        user_id = "user_123"
        self.mock_data['performance_metrics'][user_id] = {
            'overall_scores': [72, 75, 78, 80, 82, 85, 82],
            'category_scores': {
                'technical': [70, 73, 76, 78, 80, 83, 85],
                'communication': [75, 77, 79, 81, 82, 84, 78],
                'behavioral': [68, 72, 75, 77, 80, 82, 88],
                'problem_solving': [74, 76, 78, 82, 85, 87, 82]
            },
            'session_dates': [
                '2024-01-10', '2024-01-11', '2024-01-12', '2024-01-13', 
                '2024-01-14', '2024-01-15', '2024-01-16'
            ],
            'interviews_completed': 12,
            'total_practice_time': 480,  # minutes
            'skills_progress': {
                'React': [60, 65, 70, 75, 80, 85, 88],
                'Python': [70, 72, 75, 78, 80, 82, 85],
                'Communication': [65, 68, 72, 75, 78, 80, 78]
            }
        }
        
        # Mock leaderboard data
        self.mock_data['leaderboard_data'] = [
            {'user_id': 'user_001', 'name': 'Alice Chen', 'score': 92, 'interviews': 15},
            {'user_id': 'user_002', 'name': 'Bob Smith', 'score': 88, 'interviews': 12},
            {'user_id': 'user_003', 'name': 'Carol Davis', 'score': 85, 'interviews': 18},
            {'user_id': 'user_123', 'name': 'Current User', 'score': 82, 'interviews': 12},
            {'user_id': 'user_004', 'name': 'David Wilson', 'score': 78, 'interviews': 8}
        ]
    
    async def get_dashboard_data(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return self._get_empty_dashboard_data()
            
            # Filter data based on period
            filtered_data = self._filter_data_by_period(user_metrics, period)
            
            dashboard_data = {
                'overall_score': filtered_data.get('current_score', 0),
                'interviews_completed': filtered_data.get('interviews_completed', 0),
                'average_improvement': filtered_data.get('improvement', 0),
                'total_practice_time': filtered_data.get('practice_time', 0),
                'progress_over_time': filtered_data.get('progress_data', []),
                'score_breakdown': filtered_data.get('category_breakdown', []),
                'recent_interviews': filtered_data.get('recent_sessions', []),
                'strengths': filtered_data.get('strengths', []),
                'areas_to_improve': filtered_data.get('weaknesses', [])
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return self._get_empty_dashboard_data()
    
    def _filter_data_by_period(self, user_metrics: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Filter user metrics based on time period"""
        # For mock data, we'll just return recent data
        overall_scores = user_metrics.get('overall_scores', [])
        category_scores = user_metrics.get('category_scores', {})
        
        # Get current score (latest)
        current_score = overall_scores[-1] if overall_scores else 0
        
        # Calculate improvement
        improvement = 0
        if len(overall_scores) >= 2:
            improvement = overall_scores[-1] - overall_scores[0]
        
        # Get category breakdown
        category_breakdown = []
        for category, scores in category_scores.items():
            latest_score = scores[-1] if scores else 0
            category_breakdown.append({
                'subject': category.replace('_', ' ').title(),
                'A': latest_score,
                'fullMark': 100
            })
        
        # Generate progress data
        progress_data = []
        dates = user_metrics.get('session_dates', [])
        for i, score in enumerate(overall_scores[-7:]):  # Last 7 sessions
            date_label = dates[i] if i < len(dates) else f"Day {i+1}"
            progress_data.append({
                'date': date_label[-3:],  # Last 3 characters of date
                'score': score
            })
        
        # Get recent sessions
        recent_sessions = []
        companies = ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple']
        roles = ['Software Engineer', 'Frontend Developer', 'Full Stack Developer', 'Backend Developer']
        
        for i in range(min(4, len(overall_scores))):
            recent_sessions.append({
                'company': companies[i % len(companies)],
                'role': roles[i % len(roles)],
                'score': overall_scores[-(i+1)],
                'date': dates[-(i+1)] if i < len(dates) else f"2024-01-{16-i:02d}",
                'improvement': f"+{i+2}%" if i > 0 else "+5%"
            })
        
        # Get strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for category, scores in category_scores.items():
            latest_score = scores[-1] if scores else 0
            category_name = category.replace('_', ' ').title()
            
            if latest_score >= 80:
                strengths.append({
                    'name': category_name,
                    'value': latest_score
                })
            elif latest_score < 70:
                weaknesses.append({
                    'name': category_name,
                    'value': latest_score
                })
        
        return {
            'current_score': current_score,
            'interviews_completed': user_metrics.get('interviews_completed', 0),
            'improvement': improvement,
            'practice_time': user_metrics.get('total_practice_time', 0),
            'progress_data': progress_data,
            'category_breakdown': category_breakdown,
            'recent_sessions': recent_sessions,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data for new users"""
        return {
            'overall_score': 0,
            'interviews_completed': 0,
            'average_improvement': 0,
            'total_practice_time': 0,
            'progress_over_time': [],
            'score_breakdown': [],
            'recent_interviews': [],
            'strengths': [],
            'areas_to_improve': []
        }
    
    async def get_performance_trends(self, user_id: str, period: str = "week") -> List[Dict[str, Any]]:
        """Get performance trends over time"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return []
            
            trends = []
            overall_scores = user_metrics.get('overall_scores', [])
            dates = user_metrics.get('session_dates', [])
            
            for i, score in enumerate(overall_scores):
                trends.append({
                    'date': dates[i] if i < len(dates) else f"2024-01-{10+i:02d}",
                    'score': score,
                    'session_number': i + 1
                })
            
            return trends
            
        except Exception as e:
            print(f"Error getting performance trends: {e}")
            return []
    
    async def get_skills_breakdown(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """Get detailed skills breakdown"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return {}
            
            skills_progress = user_metrics.get('skills_progress', {})
            
            breakdown = {}
            for skill, scores in skills_progress.items():
                current_score = scores[-1] if scores else 0
                improvement = scores[-1] - scores[0] if len(scores) >= 2 else 0
                
                breakdown[skill] = {
                    'current_score': current_score,
                    'improvement': improvement,
                    'trend': 'improving' if improvement > 0 else 'stable' if improvement == 0 else 'declining',
                    'history': scores
                }
            
            return breakdown
            
        except Exception as e:
            print(f"Error getting skills breakdown: {e}")
            return {}
    
    async def get_peer_comparison(self, user_id: str) -> Dict[str, Any]:
        """Compare user performance with peers"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return {}
            
            user_score = user_metrics.get('overall_scores', [])[-1] if user_metrics.get('overall_scores') else 0
            
            # Get all peer scores
            all_scores = []
            for user_data in self.mock_data['performance_metrics'].values():
                if user_data.get('overall_scores'):
                    all_scores.append(user_data['overall_scores'][-1])
            
            if not all_scores:
                return {}
            
            # Calculate percentiles
            sorted_scores = sorted(all_scores)
            user_percentile = (sorted_scores.index(user_score) / len(sorted_scores)) * 100 if user_score in sorted_scores else 50
            
            # Calculate averages
            avg_score = statistics.mean(all_scores)
            median_score = statistics.median(all_scores)
            
            return {
                'user_score': user_score,
                'peer_average': avg_score,
                'peer_median': median_score,
                'user_percentile': user_percentile,
                'total_peers': len(all_scores),
                'ranking': sorted_scores.index(user_score) + 1 if user_score in sorted_scores else len(all_scores) // 2
            }
            
        except Exception as e:
            print(f"Error getting peer comparison: {e}")
            return {}
    
    async def record_performance(self, metrics: Dict[str, Any]) -> bool:
        """Record performance metrics for a session"""
        try:
            user_id = metrics.get('user_id')
            if not user_id:
                return False
            
            # Initialize user data if not exists
            if user_id not in self.mock_data['performance_metrics']:
                self.mock_data['performance_metrics'][user_id] = {
                    'overall_scores': [],
                    'category_scores': defaultdict(list),
                    'session_dates': [],
                    'interviews_completed': 0,
                    'total_practice_time': 0
                }
            
            user_data = self.mock_data['performance_metrics'][user_id]
            
            # Record overall score
            overall_score = metrics.get('overall_score', 0)
            user_data['overall_scores'].append(overall_score)
            
            # Record category scores
            detailed_scores = metrics.get('detailed_scores', {})
            for category, score in detailed_scores.items():
                user_data['category_scores'][category].append(score)
            
            # Record session date
            user_data['session_dates'].append(datetime.now().strftime('%Y-%m-%d'))
            
            # Update counters
            user_data['interviews_completed'] += 1
            user_data['total_practice_time'] += metrics.get('completion_time', 0) // 60  # Convert to minutes
            
            return True
            
        except Exception as e:
            print(f"Error recording performance: {e}")
            return False
    
    async def get_leaderboard(self, limit: int = 10, time_period: str = "week") -> List[Dict[str, Any]]:
        """Get performance leaderboard"""
        try:
            # Sort mock leaderboard data by score
            leaderboard = sorted(
                self.mock_data['leaderboard_data'],
                key=lambda x: x['score'],
                reverse=True
            )
            
            return leaderboard[:limit]
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return {}
            
            overall_scores = user_metrics.get('overall_scores', [])
            
            stats = {
                'total_interviews': len(overall_scores),
                'average_score': statistics.mean(overall_scores) if overall_scores else 0,
                'highest_score': max(overall_scores) if overall_scores else 0,
                'lowest_score': min(overall_scores) if overall_scores else 0,
                'total_practice_time': user_metrics.get('total_practice_time', 0),
                'improvement_rate': self._calculate_improvement_rate(overall_scores),
                'consistency_score': self._calculate_consistency_score(overall_scores),
                'last_session_date': user_metrics.get('session_dates', [])[-1] if user_metrics.get('session_dates') else None
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {}
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate the rate of improvement over time"""
        if len(scores) < 2:
            return 0.0
        
        # Simple linear regression to calculate trend
        n = len(scores)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(scores)
        
        numerator = sum((x_values[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope * 10  # Scale for readability
    
    def _calculate_consistency_score(self, scores: List[float]) -> float:
        """Calculate how consistent the user's performance is"""
        if len(scores) < 2:
            return 100.0
        
        # Lower standard deviation = higher consistency
        std_dev = statistics.stdev(scores)
        mean_score = statistics.mean(scores)
        
        # Normalize consistency score (inverse of coefficient of variation)
        if mean_score == 0:
            return 0.0
        
        cv = std_dev / mean_score
        consistency_score = max(0, 100 - (cv * 100))
        
        return consistency_score
    
    async def export_user_data(self, user_id: str, period: str = "all") -> Dict[str, Any]:
        """Export user performance data"""
        try:
            user_metrics = self.mock_data['performance_metrics'].get(user_id, {})
            
            if not user_metrics:
                return {}
            
            export_data = {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'period': period,
                'performance_metrics': user_metrics,
                'analytics_summary': await self.get_user_statistics(user_id),
                'peer_comparison': await self.get_peer_comparison(user_id)
            }
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return {}
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR compliance)"""
        try:
            if user_id in self.mock_data['performance_metrics']:
                del self.mock_data['performance_metrics'][user_id]
            
            # Remove from leaderboard
            self.mock_data['leaderboard_data'] = [
                entry for entry in self.mock_data['leaderboard_data']
                if entry.get('user_id') != user_id
            ]
            
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def _generate_recommendations(self, overall_score: float, skills_progress: Dict[str, Any], category_scores: Dict[str, List[float]]) -> List[str]:
        """Generate personalized recommendations based on performance"""
        recommendations = []
        
        # Overall score based recommendations
        if overall_score < 60:
            recommendations.append("Focus on improving technical fundamentals through practice and learning")
        elif overall_score < 75:
            recommendations.append("Good performance! Consider advanced topics and real-world projects")
        else:
            recommendations.append("Excellent performance! Focus on leadership and mentoring opportunities")
        
        # Skills-based recommendations
        weak_skills = []
        for skill, scores in skills_progress.items():
            if scores and len(scores) >= 2:
                recent_scores = scores[-3:]
                if recent_scores[-1] < recent_scores[-2]:
                    weak_skills.append(skill)
        
        for skill in weak_skills:
            recommendations.append(f"Practice more {skill} exercises to improve consistency")
        
        # Category-specific recommendations
        if category_scores.get('technical', [0])[-1] < 70:
            recommendations.append("Review core computer science fundamentals")
        
        if category_scores.get('communication', [0])[-1] < 75:
            recommendations.append("Practice explaining technical concepts clearly")
        
        return recommendations[:10]  # Limit to top 10 recommendations
