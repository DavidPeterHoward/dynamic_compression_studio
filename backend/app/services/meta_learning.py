"""
Meta-Learning Service for the Dynamic Compression Algorithms backend.

This service provides meta-learning capabilities including user behavior analysis,
preference learning, and adaptive algorithm recommendations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import math
from collections import defaultdict, deque

class MetaLearningService:
    """Service for meta-learning and adaptive recommendations."""
    
    def __init__(self):
        self.user_data = defaultdict(lambda: {
            'preferences': {
                'speed_vs_compression': 0.5,
                'quality_vs_size': 0.5,
                'compatibility_vs_performance': 0.5
            },
            'behavior_history': deque(maxlen=1000),
            'algorithm_performance': defaultdict(lambda: {
                'success_count': 0,
                'total_count': 0,
                'avg_satisfaction': 0.0,
                'avg_compression_ratio': 0.0,
                'avg_processing_time': 0.0
            }),
            'content_patterns': defaultdict(int),
            'learning_insights': [],
            'last_updated': datetime.utcnow()
        })
        
        self.global_patterns = defaultdict(int)
        self.algorithm_effectiveness = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.01
        self.adaptation_speed = 1.0
    
    async def get_insights(self, user_id: Optional[str] = None, 
                          content_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get meta-learning insights for a user."""
        if not user_id:
            return self._get_global_insights()
        
        user_data = self.user_data[user_id]
        
        # Analyze user patterns
        user_patterns = self._analyze_user_patterns(user_id)
        content_patterns = self._analyze_content_patterns(user_id)
        
        # Generate insights
        insights = {
            'user_pattern': self._identify_user_pattern(user_data),
            'content_pattern': self._identify_content_pattern(user_data),
            'success_rate': self._calculate_success_rate(user_data),
            'improvement_suggestions': self._generate_improvement_suggestions(user_data)
        }
        
        return insights
    
    async def get_user_insights(self, user_id: str, include_patterns: bool = True,
                               include_recommendations: bool = True) -> Dict[str, Any]:
        """Get comprehensive user insights."""
        user_data = self.user_data[user_id]
        
        insights = {
            'user_id': user_id,
            'preferences': user_data['preferences'].copy(),
            'behavior_patterns': {},
            'learning_progress': {},
            'content_patterns': {},
            'recommendations': {}
        }
        
        if include_patterns:
            insights['behavior_patterns'] = self._analyze_user_patterns(user_id)
            insights['content_patterns'] = self._analyze_content_patterns(user_id)
        
        if include_recommendations:
            insights['recommendations'] = self._generate_user_recommendations(user_id)
        
        # Learning progress
        insights['learning_progress'] = {
            'iterations': len(user_data['behavior_history']),
            'accuracy_improvement': self._calculate_accuracy_improvement(user_id),
            'recommendation_success_rate': self._calculate_recommendation_success_rate(user_id)
        }
        
        return insights
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any],
                                feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences and learning model."""
        user_data = self.user_data[user_id]
        
        # Update preferences with learning
        old_preferences = user_data['preferences'].copy()
        
        for key, value in preferences.items():
            if key in user_data['preferences']:
                # Apply learning rate to preference updates
                current_value = user_data['preferences'][key]
                new_value = current_value + self.learning_rate * (value - current_value)
                user_data['preferences'][key] = max(0.0, min(1.0, new_value))
        
        # Record feedback
        if feedback:
            user_data['behavior_history'].append({
                'timestamp': datetime.utcnow(),
                'preferences': preferences,
                'feedback': feedback,
                'type': 'preference_update'
            })
        
        # Update learning model
        model_update = {
            'model_updated': True,
            'accuracy_improvement': self._calculate_accuracy_improvement(user_id),
            'new_insights': self._generate_new_insights(user_id, preferences, feedback)
        }
        
        user_data['last_updated'] = datetime.utcnow()
        
        return model_update
    
    async def update_learning_model(self, content_analysis: Dict[str, Any],
                                   algorithm: Dict[str, Any], result: Dict[str, Any]):
        """Update the learning model with compression results."""
        # Extract key information
        algorithm_name = algorithm.get('name', 'unknown')
        compression_ratio = result.get('compression_ratio', 0)
        processing_time = result.get('processing_time', 0)
        
        # Update global patterns
        content_type = content_analysis.get('content_type', {}).get('primary', 'unknown')
        self.global_patterns[f"{content_type}_{algorithm_name}"] += 1
        
        # Update algorithm effectiveness
        effectiveness_score = self._calculate_effectiveness_score(
            compression_ratio, processing_time, content_analysis
        )
        
        self.algorithm_effectiveness[content_type][algorithm_name] = (
            self.algorithm_effectiveness[content_type][algorithm_name] * 0.9 + 
            effectiveness_score * 0.1
        )
    
    def _analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        user_data = self.user_data[user_id]
        history = user_data['behavior_history']
        
        if not history:
            return {
                'frequent_content_types': [],
                'preferred_algorithms': [],
                'success_rate': 0.0,
                'average_compression_ratio': 0.0
            }
        
        # Analyze content types
        content_types = defaultdict(int)
        algorithms = defaultdict(int)
        compression_ratios = []
        success_count = 0
        
        for entry in history:
            if entry.get('type') == 'compression':
                content_type = entry.get('content_analysis', {}).get('content_type', {}).get('primary', 'unknown')
                content_types[content_type] += 1
                
                algorithm = entry.get('algorithm', 'unknown')
                algorithms[algorithm] += 1
                
                ratio = entry.get('result', {}).get('compression_ratio', 0)
                compression_ratios.append(ratio)
                
                satisfaction = entry.get('feedback', {}).get('satisfaction', 0)
                if satisfaction > 0.7:
                    success_count += 1
        
        # Calculate patterns
        total_entries = len([e for e in history if e.get('type') == 'compression'])
        
        return {
            'frequent_content_types': sorted(content_types.items(), key=lambda x: x[1], reverse=True)[:3],
            'preferred_algorithms': sorted(algorithms.items(), key=lambda x: x[1], reverse=True)[:3],
            'success_rate': success_count / max(total_entries, 1),
            'average_compression_ratio': sum(compression_ratios) / max(len(compression_ratios), 1)
        }
    
    def _analyze_content_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze content patterns for a user."""
        user_data = self.user_data[user_id]
        content_patterns = user_data['content_patterns']
        
        if not content_patterns:
            return {
                'text_content': {'frequency': 0.0, 'optimal_algorithms': [], 'average_compression_ratio': 0.0},
                'structured_content': {'frequency': 0.0, 'optimal_algorithms': [], 'average_compression_ratio': 0.0}
            }
        
        total_patterns = sum(content_patterns.values())
        
        # Analyze patterns
        pattern_analysis = {}
        for pattern, count in content_patterns.items():
            frequency = count / total_patterns
            
            # Get optimal algorithms for this pattern
            optimal_algorithms = self._get_optimal_algorithms_for_pattern(pattern)
            
            pattern_analysis[pattern] = {
                'frequency': frequency,
                'optimal_algorithms': optimal_algorithms,
                'average_compression_ratio': self._get_average_compression_ratio(pattern)
            }
        
        return pattern_analysis
    
    def _identify_user_pattern(self, user_data: Dict[str, Any]) -> str:
        """Identify the user's behavior pattern."""
        preferences = user_data['preferences']
        
        if preferences['speed_vs_compression'] > 0.7:
            return "Prefers speed over compression"
        elif preferences['speed_vs_compression'] < 0.3:
            return "Prefers compression over speed"
        else:
            return "Prefers balanced algorithms"
    
    def _identify_content_pattern(self, user_data: Dict[str, Any]) -> str:
        """Identify the user's content pattern."""
        content_patterns = user_data['content_patterns']
        
        if not content_patterns:
            return "No content pattern detected"
        
        most_frequent = max(content_patterns.items(), key=lambda x: x[1])
        return f"Frequently processes {most_frequent[0]} content"
    
    def _calculate_success_rate(self, user_data: Dict[str, Any]) -> float:
        """Calculate user's success rate."""
        algorithm_performance = user_data['algorithm_performance']
        
        if not algorithm_performance:
            return 0.0
        
        total_success = sum(perf['success_count'] for perf in algorithm_performance.values())
        total_attempts = sum(perf['total_count'] for perf in algorithm_performance.values())
        
        return total_success / max(total_attempts, 1)
    
    def _generate_improvement_suggestions(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions for the user."""
        suggestions = []
        
        # Analyze algorithm performance
        algorithm_performance = user_data['algorithm_performance']
        
        if algorithm_performance:
            # Find underperforming algorithms
            for algo, perf in algorithm_performance.items():
                if perf['total_count'] > 5 and perf['success_count'] / perf['total_count'] < 0.7:
                    suggestions.append(f"Consider alternatives to {algo} for better results")
            
            # Find high-performing algorithms
            best_algo = max(algorithm_performance.items(), 
                          key=lambda x: x[1]['success_count'] / max(x[1]['total_count'], 1))
            if best_algo[1]['total_count'] > 3:
                suggestions.append(f"Continue using {best_algo[0]} - it's working well for you")
        
        # Analyze preferences
        preferences = user_data['preferences']
        if preferences['speed_vs_compression'] > 0.8:
            suggestions.append("Consider zstd for better compression with minimal speed impact")
        elif preferences['speed_vs_compression'] < 0.2:
            suggestions.append("Consider lz4 for faster processing when compression ratio is less critical")
        
        return suggestions
    
    def _generate_user_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized recommendations for the user."""
        user_data = self.user_data[user_id]
        algorithm_performance = user_data['algorithm_performance']
        
        recommendations = {
            'algorithm_suggestions': [],
            'preference_adjustments': []
        }
        
        # Algorithm suggestions
        if algorithm_performance:
            # Find best performing algorithm
            best_algo = max(algorithm_performance.items(),
                          key=lambda x: x[1]['success_count'] / max(x[1]['total_count'], 1))
            
            if best_algo[1]['total_count'] > 3:
                recommendations['algorithm_suggestions'].append({
                    'algorithm': best_algo[0],
                    'reason': 'High success rate in your usage',
                    'confidence': best_algo[1]['success_count'] / best_algo[1]['total_count']
                })
        
        # Preference adjustments
        preferences = user_data['preferences']
        
        # Analyze if user frequently prioritizes quality over size
        if preferences['quality_vs_size'] > 0.8:
            recommendations['preference_adjustments'].append({
                'preference': 'quality_vs_size',
                'suggested_value': 0.7,
                'reason': 'User frequently prioritizes quality over size'
            })
        
        return recommendations
    
    def _calculate_accuracy_improvement(self, user_id: str) -> float:
        """Calculate accuracy improvement over time."""
        user_data = self.user_data[user_id]
        history = user_data['behavior_history']
        
        if len(history) < 10:
            return 0.0
        
        # Calculate accuracy for recent vs older entries
        recent_entries = history[-10:]
        older_entries = history[-20:-10] if len(history) >= 20 else history[:-10]
        
        recent_accuracy = self._calculate_accuracy_for_entries(recent_entries)
        older_accuracy = self._calculate_accuracy_for_entries(older_entries)
        
        return recent_accuracy - older_accuracy
    
    def _calculate_accuracy_for_entries(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate accuracy for a set of entries."""
        if not entries:
            return 0.0
        
        successful_predictions = 0
        total_predictions = 0
        
        for entry in entries:
            if entry.get('type') == 'compression':
                satisfaction = entry.get('feedback', {}).get('satisfaction', 0)
                if satisfaction > 0.7:
                    successful_predictions += 1
                total_predictions += 1
        
        return successful_predictions / max(total_predictions, 1)
    
    def _calculate_recommendation_success_rate(self, user_id: str) -> float:
        """Calculate success rate of recommendations."""
        user_data = self.user_data[user_id]
        history = user_data['behavior_history']
        
        if not history:
            return 0.0
        
        successful_recommendations = 0
        total_recommendations = 0
        
        for entry in history:
            if entry.get('type') == 'recommendation':
                satisfaction = entry.get('feedback', {}).get('satisfaction', 0)
                if satisfaction > 0.7:
                    successful_recommendations += 1
                total_recommendations += 1
        
        return successful_recommendations / max(total_recommendations, 1)
    
    def _get_optimal_algorithms_for_pattern(self, pattern: str) -> List[str]:
        """Get optimal algorithms for a content pattern."""
        pattern_algorithm_map = {
            'text': ['gzip', 'zstd', 'brotli'],
            'json': ['zstd', 'gzip', 'content_aware'],
            'xml': ['gzip', 'zstd', 'content_aware'],
            'code': ['gzip', 'lz4', 'zstd'],
            'log': ['gzip', 'lz4', 'zstd']
        }
        
        return pattern_algorithm_map.get(pattern, ['gzip', 'zstd'])
    
    def _get_average_compression_ratio(self, pattern: str) -> float:
        """Get average compression ratio for a pattern."""
        pattern_ratios = {
            'text': 2.8,
            'json': 3.2,
            'xml': 2.9,
            'code': 2.5,
            'log': 2.7
        }
        
        return pattern_ratios.get(pattern, 2.5)
    
    def _calculate_effectiveness_score(self, compression_ratio: float, 
                                     processing_time: float,
                                     content_analysis: Dict[str, Any]) -> float:
        """Calculate effectiveness score for an algorithm."""
        # Base score from compression ratio
        ratio_score = min(compression_ratio / 5.0, 1.0)
        
        # Time score (inverse relationship)
        time_score = max(0, 1.0 - processing_time / 1.0)
        
        # Content type bonus
        content_type = content_analysis.get('content_type', {}).get('primary', 'text')
        type_bonus = 0.1 if content_type in ['text', 'json', 'xml'] else 0.0
        
        return (ratio_score * 0.6 + time_score * 0.3 + type_bonus)
    
    def _generate_new_insights(self, user_id: str, preferences: Dict[str, Any],
                              feedback: Dict[str, Any]) -> List[str]:
        """Generate new insights based on user updates."""
        insights = []
        
        # Analyze preference changes
        user_data = self.user_data[user_id]
        old_preferences = user_data['preferences']
        
        for key, new_value in preferences.items():
            if key in old_preferences:
                old_value = old_preferences[key]
                if abs(new_value - old_value) > 0.1:
                    if new_value > old_value:
                        insights.append(f"User increased preference for {key}")
                    else:
                        insights.append(f"User decreased preference for {key}")
        
        # Analyze feedback
        if feedback:
            satisfaction = feedback.get('satisfaction', 0)
            if satisfaction > 0.8:
                insights.append("User highly satisfied with recent compression")
            elif satisfaction < 0.4:
                insights.append("User dissatisfied with recent compression")
        
        return insights
    
    def _get_global_insights(self) -> Dict[str, Any]:
        """Get global insights across all users."""
        return {
            'user_pattern': 'Global analysis',
            'content_pattern': 'Mixed content types',
            'success_rate': 0.85,  # Mock global success rate
            'improvement_suggestions': [
                'Consider zstd for better compression',
                'Use lz4 for speed-critical applications'
            ]
        }
    
    def record_preference_update(self, user_id: str, preferences: Dict[str, Any],
                                feedback: Dict[str, Any]):
        """Record preference update for learning."""
        user_data = self.user_data[user_id]
        
        user_data['behavior_history'].append({
            'timestamp': datetime.utcnow(),
            'preferences': preferences,
            'feedback': feedback,
            'type': 'preference_update'
        })
        
        user_data['last_updated'] = datetime.utcnow()
