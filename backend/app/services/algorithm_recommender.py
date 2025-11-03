"""
Algorithm Recommendation Service for the Dynamic Compression Algorithms backend.

This service provides intelligent algorithm recommendations based on content analysis,
user preferences, and meta-learning insights.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import math

class AlgorithmRecommender:
    """Service for recommending optimal compression algorithms."""
    
    def __init__(self):
        self.algorithms = {
            'gzip': {
                'name': 'gzip',
                'description': 'General-purpose compression algorithm based on DEFLATE',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'fast',
                    'compression': 'good',
                    'memory_usage': 'low',
                    'compatibility': 'excellent'
                },
                'best_for': ['text', 'log files', 'web content', 'general purpose'],
                'parameters': {
                    'level': {'type': 'int', 'range': [1, 9], 'default': 6, 'description': 'Compression level (1=fast, 9=best)'},
                    'window_size': {'type': 'int', 'range': [1024, 65536], 'default': 32768, 'description': 'Window size in bytes'}
                }
            },
            'lzma': {
                'name': 'lzma',
                'description': 'High-compression algorithm with slower speed',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'slow',
                    'compression': 'excellent',
                    'memory_usage': 'high',
                    'compatibility': 'good'
                },
                'best_for': ['archives', 'backups', 'high-compression needs'],
                'parameters': {
                    'level': {'type': 'int', 'range': [0, 9], 'default': 6, 'description': 'Compression level'},
                    'dict_size': {'type': 'int', 'range': [4096, 1073741824], 'default': 67108864, 'description': 'Dictionary size'}
                }
            },
            'bzip2': {
                'name': 'bzip2',
                'description': 'Block-sorting compression algorithm',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'medium',
                    'compression': 'good',
                    'memory_usage': 'medium',
                    'compatibility': 'good'
                },
                'best_for': ['text', 'source code', 'log files'],
                'parameters': {
                    'level': {'type': 'int', 'range': [1, 9], 'default': 6, 'description': 'Compression level'},
                    'block_size': {'type': 'int', 'range': [1, 9], 'default': 6, 'description': 'Block size'}
                }
            },
            'lz4': {
                'name': 'lz4',
                'description': 'Extremely fast compression algorithm',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'very fast',
                    'compression': 'moderate',
                    'memory_usage': 'very low',
                    'compatibility': 'good'
                },
                'best_for': ['real-time', 'streaming', 'speed-critical applications'],
                'parameters': {
                    'level': {'type': 'int', 'range': [1, 9], 'default': 6, 'description': 'Compression level'},
                    'acceleration': {'type': 'int', 'range': [1, 65537], 'default': 1, 'description': 'Acceleration factor'}
                }
            },
            'zstd': {
                'name': 'zstd',
                'description': 'Zstandard compression algorithm',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'fast',
                    'compression': 'excellent',
                    'memory_usage': 'low',
                    'compatibility': 'good'
                },
                'best_for': ['general purpose', 'web content', 'databases'],
                'parameters': {
                    'level': {'type': 'int', 'range': [1, 22], 'default': 6, 'description': 'Compression level'},
                    'window_log': {'type': 'int', 'range': [10, 30], 'default': 22, 'description': 'Window size (log2)'}
                }
            },
            'brotli': {
                'name': 'brotli',
                'description': 'Brotli compression algorithm',
                'category': 'traditional',
                'characteristics': {
                    'speed': 'medium',
                    'compression': 'excellent',
                    'memory_usage': 'medium',
                    'compatibility': 'good'
                },
                'best_for': ['web content', 'text', 'HTTP responses'],
                'parameters': {
                    'level': {'type': 'int', 'range': [0, 11], 'default': 6, 'description': 'Compression level'},
                    'window_size': {'type': 'int', 'range': [10, 24], 'default': 22, 'description': 'Window size (log2)'}
                }
            },
            'content_aware': {
                'name': 'content_aware',
                'description': 'AI-powered algorithm that adapts to content type',
                'category': 'advanced',
                'characteristics': {
                    'speed': 'adaptive',
                    'compression': 'excellent',
                    'memory_usage': 'medium',
                    'compatibility': 'good'
                },
                'best_for': ['mixed content', 'unknown content types', 'adaptive compression'],
                'parameters': {
                    'level': {'type': 'string', 'options': ['fast', 'balanced', 'optimal', 'maximum'], 'default': 'balanced', 'description': 'Compression level'},
                    'optimization_target': {'type': 'string', 'options': ['ratio', 'speed', 'quality'], 'default': 'ratio', 'description': 'Optimization target'}
                }
            }
        }
        
        self.performance_history = {}
        self.user_preferences_cache = {}
    
    async def get_recommendations(self, content_analysis: Dict[str, Any], 
                                user_preferences: Dict[str, Any],
                                meta_learning_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate algorithm recommendations based on content analysis and user preferences.
        
        Args:
            content_analysis: Results from content analysis
            user_preferences: User's compression preferences
            meta_learning_context: Context for meta-learning
            
        Returns:
            List of algorithm recommendations with confidence scores
        """
        recommendations = []
        
        # Get base recommendations from content analysis
        base_recommendations = self._get_base_recommendations(content_analysis)
        
        # Apply user preferences
        user_adjusted_recommendations = self._apply_user_preferences(
            base_recommendations, user_preferences
        )
        
        # Apply meta-learning insights
        meta_learning_recommendations = await self._apply_meta_learning(
            user_adjusted_recommendations, meta_learning_context, content_analysis
        )
        
        # Calculate final scores and sort
        for algo_name in meta_learning_recommendations:
            if algo_name in self.algorithms:
                recommendation = self._create_recommendation(
                    algo_name, content_analysis, user_preferences, meta_learning_context
                )
                recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_base_recommendations(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Get base algorithm recommendations from content analysis."""
        content_type = content_analysis.get('content_type', {}).get('primary', 'text')
        entropy = content_analysis.get('entropy', 0)
        redundancy = content_analysis.get('redundancy', 0)
        patterns = content_analysis.get('patterns', [])
        compressibility = content_analysis.get('compressibility', 5.0)
        
        recommendations = []
        
        # Content type based recommendations
        if content_type == 'text':
            if redundancy > 0.3:
                recommendations.extend(['gzip', 'zstd', 'brotli'])
            else:
                recommendations.extend(['zstd', 'brotli', 'gzip'])
        elif content_type == 'json':
            recommendations.extend(['zstd', 'gzip', 'content_aware'])
        elif content_type == 'xml':
            recommendations.extend(['gzip', 'zstd', 'content_aware'])
        elif content_type == 'code':
            recommendations.extend(['gzip', 'lz4', 'zstd'])
        elif content_type == 'log':
            recommendations.extend(['gzip', 'lz4', 'zstd'])
        else:
            recommendations.extend(['content_aware', 'zstd', 'gzip'])
        
        # Entropy based adjustments
        if entropy < 3.0:  # Low entropy, high redundancy
            recommendations = ['gzip', 'zstd', 'brotli'] + recommendations
        elif entropy > 6.0:  # High entropy, low redundancy
            recommendations = ['lz4', 'gzip', 'zstd'] + recommendations
        
        # Pattern based adjustments
        if 'repetitive' in patterns:
            recommendations = ['gzip', 'zstd', 'brotli'] + recommendations
        if 'structured' in patterns:
            recommendations = ['zstd', 'gzip', 'content_aware'] + recommendations
        if 'tabular' in patterns:
            recommendations = ['gzip', 'zstd', 'brotli'] + recommendations
        
        # Compressibility based adjustments
        if compressibility > 7.0:  # Highly compressible
            recommendations = ['lzma', 'zstd', 'brotli'] + recommendations
        elif compressibility < 3.0:  # Low compressibility
            recommendations = ['lz4', 'gzip', 'zstd'] + recommendations
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _apply_user_preferences(self, base_recommendations: List[str], 
                              user_preferences: Dict[str, Any]) -> List[str]:
        """Apply user preferences to base recommendations."""
        speed_vs_compression = user_preferences.get('speed_vs_compression', 0.5)
        quality_vs_size = user_preferences.get('quality_vs_size', 0.5)
        compatibility_vs_performance = user_preferences.get('compatibility_vs_performance', 0.5)
        
        # Algorithm scoring based on user preferences
        algorithm_scores = {}
        
        for algo_name in base_recommendations:
            if algo_name in self.algorithms:
                algo = self.algorithms[algo_name]
                characteristics = algo['characteristics']
                
                score = 0.0
                
                # Speed vs Compression preference
                if speed_vs_compression > 0.7:  # Prefer speed
                    if characteristics['speed'] in ['very fast', 'fast']:
                        score += 2.0
                    elif characteristics['speed'] == 'medium':
                        score += 1.0
                elif speed_vs_compression < 0.3:  # Prefer compression
                    if characteristics['compression'] in ['excellent', 'good']:
                        score += 2.0
                    elif characteristics['compression'] == 'moderate':
                        score += 1.0
                else:  # Balanced
                    if characteristics['speed'] in ['fast', 'medium'] and characteristics['compression'] in ['good', 'excellent']:
                        score += 2.0
                
                # Quality vs Size preference
                if quality_vs_size > 0.7:  # Prefer quality
                    if characteristics['compression'] in ['excellent', 'good']:
                        score += 1.5
                elif quality_vs_size < 0.3:  # Prefer size reduction
                    if characteristics['compression'] in ['excellent', 'good']:
                        score += 1.5
                
                # Compatibility vs Performance preference
                if compatibility_vs_performance > 0.7:  # Prefer compatibility
                    if characteristics['compatibility'] in ['excellent', 'good']:
                        score += 1.0
                elif compatibility_vs_performance < 0.3:  # Prefer performance
                    if characteristics['speed'] in ['very fast', 'fast']:
                        score += 1.0
                
                algorithm_scores[algo_name] = score
        
        # Sort by score
        sorted_algorithms = sorted(algorithm_scores.items(), key=lambda x: x[1], reverse=True)
        return [algo for algo, score in sorted_algorithms]
    
    async def _apply_meta_learning(self, recommendations: List[str], 
                                 meta_learning_context: Dict[str, Any],
                                 content_analysis: Dict[str, Any]) -> List[str]:
        """Apply meta-learning insights to recommendations."""
        user_id = meta_learning_context.get('user_id')
        
        if not user_id:
            return recommendations
        
        # Get user's historical performance data
        user_history = self.performance_history.get(user_id, {})
        
        if not user_history:
            return recommendations
        
        # Adjust recommendations based on user's success patterns
        adjusted_recommendations = []
        
        for algo_name in recommendations:
            if algo_name in user_history:
                success_rate = user_history[algo_name].get('success_rate', 0.5)
                avg_satisfaction = user_history[algo_name].get('avg_satisfaction', 0.5)
                
                # Boost algorithms with high success rate and satisfaction
                if success_rate > 0.8 and avg_satisfaction > 0.7:
                    adjusted_recommendations.insert(0, algo_name)
                elif success_rate > 0.6 and avg_satisfaction > 0.6:
                    adjusted_recommendations.append(algo_name)
            else:
                adjusted_recommendations.append(algo_name)
        
        return adjusted_recommendations
    
    def _create_recommendation(self, algo_name: str, content_analysis: Dict[str, Any],
                             user_preferences: Dict[str, Any], 
                             meta_learning_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed recommendation for an algorithm."""
        algo = self.algorithms[algo_name]
        
        # Calculate confidence score
        confidence = self._calculate_confidence(algo_name, content_analysis, user_preferences)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(algo_name, content_analysis, user_preferences)
        
        # Predict performance
        expected_performance = self._predict_performance(algo_name, content_analysis)
        
        # Generate use case description
        use_case = self._generate_use_case(algo_name, content_analysis)
        
        # Analyze tradeoffs
        tradeoffs = self._analyze_tradeoffs(algo_name)
        
        return {
            'algorithm': {
                'name': algo['name'],
                'description': algo['description'],
                'category': algo['category'],
                'parameters': algo['parameters']
            },
            'confidence': confidence,
            'reasoning': reasoning,
            'expected_performance': expected_performance,
            'use_case': use_case,
            'tradeoffs': tradeoffs
        }
    
    def _calculate_confidence(self, algo_name: str, content_analysis: Dict[str, Any],
                            user_preferences: Dict[str, Any]) -> float:
        """Calculate confidence score for algorithm recommendation."""
        confidence = 0.5  # Base confidence
        
        # Content type match
        content_type = content_analysis.get('content_type', {}).get('primary', 'text')
        algo = self.algorithms[algo_name]
        
        if content_type in algo['best_for']:
            confidence += 0.2
        
        # Entropy and redundancy match
        entropy = content_analysis.get('entropy', 0)
        redundancy = content_analysis.get('redundancy', 0)
        
        if algo_name == 'gzip' and redundancy > 0.3:
            confidence += 0.15
        elif algo_name == 'zstd' and entropy < 5.0:
            confidence += 0.15
        elif algo_name == 'lz4' and entropy > 5.0:
            confidence += 0.15
        
        # User preferences match
        speed_vs_compression = user_preferences.get('speed_vs_compression', 0.5)
        characteristics = algo['characteristics']
        
        if speed_vs_compression > 0.7 and characteristics['speed'] in ['very fast', 'fast']:
            confidence += 0.1
        elif speed_vs_compression < 0.3 and characteristics['compression'] in ['excellent', 'good']:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, algo_name: str, content_analysis: Dict[str, Any],
                          user_preferences: Dict[str, Any]) -> List[str]:
        """Generate reasoning for algorithm recommendation."""
        reasoning = []
        
        content_type = content_analysis.get('content_type', {}).get('primary', 'text')
        entropy = content_analysis.get('entropy', 0)
        redundancy = content_analysis.get('redundancy', 0)
        patterns = content_analysis.get('patterns', [])
        
        # Content type reasoning
        if content_type in self.algorithms[algo_name]['best_for']:
            reasoning.append(f"Optimal for {content_type} content")
        
        # Entropy reasoning
        if algo_name == 'gzip' and redundancy > 0.3:
            reasoning.append("High redundancy in content")
        elif algo_name == 'zstd' and entropy < 5.0:
            reasoning.append("Low entropy content")
        elif algo_name == 'lz4' and entropy > 5.0:
            reasoning.append("High entropy content")
        
        # Pattern reasoning
        if 'repetitive' in patterns and algo_name in ['gzip', 'zstd']:
            reasoning.append("Detected repetitive patterns")
        if 'structured' in patterns and algo_name in ['zstd', 'content_aware']:
            reasoning.append("Structured content detected")
        
        # User preference reasoning
        speed_vs_compression = user_preferences.get('speed_vs_compression', 0.5)
        if speed_vs_compression > 0.7 and self.algorithms[algo_name]['characteristics']['speed'] in ['very fast', 'fast']:
            reasoning.append("User prefers speed over compression")
        elif speed_vs_compression < 0.3 and self.algorithms[algo_name]['characteristics']['compression'] in ['excellent', 'good']:
            reasoning.append("User prefers compression over speed")
        else:
            reasoning.append("User prefers balanced approach")
        
        return reasoning
    
    def _predict_performance(self, algo_name: str, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance for the algorithm."""
        entropy = content_analysis.get('entropy', 0)
        redundancy = content_analysis.get('redundancy', 0)
        compressibility = content_analysis.get('compressibility', 5.0)
        
        # Base performance predictions
        base_predictions = {
            'gzip': {'compression_ratio': 2.5, 'processing_time': 0.045, 'memory_usage': 16.5, 'quality': 0.95},
            'lzma': {'compression_ratio': 3.5, 'processing_time': 0.120, 'memory_usage': 64.0, 'quality': 0.98},
            'bzip2': {'compression_ratio': 2.8, 'processing_time': 0.080, 'memory_usage': 32.0, 'quality': 0.96},
            'lz4': {'compression_ratio': 2.0, 'processing_time': 0.020, 'memory_usage': 8.0, 'quality': 0.92},
            'zstd': {'compression_ratio': 3.0, 'processing_time': 0.050, 'memory_usage': 20.0, 'quality': 0.97},
            'brotli': {'compression_ratio': 3.2, 'processing_time': 0.070, 'memory_usage': 24.0, 'quality': 0.96},
            'content_aware': {'compression_ratio': 3.1, 'processing_time': 0.060, 'memory_usage': 22.0, 'quality': 0.97}
        }
        
        prediction = base_predictions.get(algo_name, base_predictions['gzip']).copy()
        
        # Adjust based on content characteristics
        if redundancy > 0.5:
            prediction['compression_ratio'] *= 1.2
        if entropy > 6.0:
            prediction['compression_ratio'] *= 0.8
        if compressibility > 7.0:
            prediction['compression_ratio'] *= 1.1
        
        # Confidence in prediction
        confidence = 0.8
        if entropy < 4.0 or entropy > 6.0:
            confidence -= 0.1
        if redundancy > 0.5:
            confidence += 0.1
        
        prediction['confidence'] = min(confidence, 1.0)
        
        return prediction
    
    def _generate_use_case(self, algo_name: str, content_analysis: Dict[str, Any]) -> str:
        """Generate use case description for the algorithm."""
        content_type = content_analysis.get('content_type', {}).get('primary', 'text')
        entropy = content_analysis.get('entropy', 0)
        redundancy = content_analysis.get('redundancy', 0)
        
        use_cases = {
            'gzip': f"Best for {content_type} content with high redundancy",
            'lzma': "Best for maximum compression when speed is not critical",
            'bzip2': f"Good for {content_type} content with moderate compression needs",
            'lz4': "Best for real-time applications requiring maximum speed",
            'zstd': f"Excellent balance for {content_type} content",
            'brotli': f"Optimal for web content and {content_type} with high quality requirements",
            'content_aware': f"Adaptive compression for {content_type} content with unknown characteristics"
        }
        
        return use_cases.get(algo_name, f"Good general-purpose choice for {content_type} content")
    
    def _analyze_tradeoffs(self, algo_name: str) -> Dict[str, List[str]]:
        """Analyze tradeoffs for the algorithm."""
        algo = self.algorithms[algo_name]
        characteristics = algo['characteristics']
        
        pros = []
        cons = []
        
        # Speed characteristics
        if characteristics['speed'] in ['very fast', 'fast']:
            pros.append("Fast processing")
        elif characteristics['speed'] == 'slow':
            cons.append("Slow processing")
        
        # Compression characteristics
        if characteristics['compression'] in ['excellent', 'good']:
            pros.append("Good compression ratio")
        elif characteristics['compression'] == 'moderate':
            cons.append("Moderate compression ratio")
        
        # Memory usage
        if characteristics['memory_usage'] == 'low':
            pros.append("Low memory usage")
        elif characteristics['memory_usage'] == 'high':
            cons.append("High memory usage")
        
        # Compatibility
        if characteristics['compatibility'] == 'excellent':
            pros.append("Wide compatibility")
        elif characteristics['compatibility'] == 'limited':
            cons.append("Limited compatibility")
        
        # Algorithm-specific tradeoffs
        if algo_name == 'gzip':
            pros.extend(["Wide support", "Good balance"])
            cons.append("Not optimal for binary data")
        elif algo_name == 'lzma':
            pros.extend(["Maximum compression", "High quality"])
            cons.extend(["Slow processing", "High memory usage"])
        elif algo_name == 'lz4':
            pros.extend(["Extremely fast", "Low memory usage"])
            cons.append("Lower compression ratio")
        elif algo_name == 'zstd':
            pros.extend(["Excellent balance", "Good compression"])
            cons.append("Newer algorithm, less widespread support")
        elif algo_name == 'brotli':
            pros.extend(["Excellent compression", "Good for web"])
            cons.append("Higher memory usage")
        elif algo_name == 'content_aware':
            pros.extend(["Adaptive", "AI-powered optimization"])
            cons.append("More complex, requires analysis")
        
        return {
            'pros': pros,
            'cons': cons
        }
    
    async def get_best_algorithm(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get the best algorithm for content analysis."""
        recommendations = await self.get_recommendations(
            content_analysis=content_analysis,
            user_preferences={'speed_vs_compression': 0.5, 'quality_vs_size': 0.5, 'compatibility_vs_performance': 0.5},
            meta_learning_context={}
        )
        
        if recommendations:
            best_rec = recommendations[0]
            return {
                'name': best_rec['algorithm']['name'],
                'parameters': best_rec['algorithm']['parameters']
            }
        else:
            return {
                'name': 'gzip',
                'parameters': {'level': 6}
            }
    
    def update_performance_history(self, user_id: str, algorithm: str, 
                                 compression_ratio: float, processing_time: float,
                                 user_satisfaction: float):
        """Update performance history for meta-learning."""
        if user_id not in self.performance_history:
            self.performance_history[user_id] = {}
        
        if algorithm not in self.performance_history[user_id]:
            self.performance_history[user_id][algorithm] = {
                'success_rate': 0.0,
                'avg_satisfaction': 0.0,
                'avg_compression_ratio': 0.0,
                'avg_processing_time': 0.0,
                'usage_count': 0
            }
        
        history = self.performance_history[user_id][algorithm]
        history['usage_count'] += 1
        
        # Update averages
        history['avg_compression_ratio'] = (
            (history['avg_compression_ratio'] * (history['usage_count'] - 1) + compression_ratio) / 
            history['usage_count']
        )
        history['avg_processing_time'] = (
            (history['avg_processing_time'] * (history['usage_count'] - 1) + processing_time) / 
            history['usage_count']
        )
        history['avg_satisfaction'] = (
            (history['avg_satisfaction'] * (history['usage_count'] - 1) + user_satisfaction) / 
            history['usage_count']
        )
        
        # Update success rate (assuming satisfaction > 0.7 is success)
        if user_satisfaction > 0.7:
            history['success_rate'] = (
                (history['success_rate'] * (history['usage_count'] - 1) + 1.0) / 
                history['usage_count']
            )
        else:
            history['success_rate'] = (
                (history['success_rate'] * (history['usage_count'] - 1) + 0.0) / 
                history['usage_count']
            )
