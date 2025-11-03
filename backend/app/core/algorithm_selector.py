"""
Algorithm selector for the Dynamic Compression Algorithms backend.

This module implements the hierarchical search strategy for algorithm selection
based on content analysis and historical performance data.
"""

import random
from typing import Dict, List, Any, Optional
# import numpy as np  # Removed for compatibility

from app.models.compression import CompressionAlgorithm, ContentType


class AlgorithmSelector:
    """
    Algorithm selector that implements hierarchical search strategy.
    
    Based on the documentation:
    - Level 1: Algorithm family selection (LZ77, LZ78, BWT, PPM, etc.)
    - Level 2: Algorithm variant selection (LZMA, LZ4, Zstandard, etc.)
    - Level 3: Parameter optimization (window size, compression level, etc.)
    """
    
    def __init__(self):
        """Initialize the algorithm selector."""
        # Algorithm families and their variants
        self.algorithm_families = {
            'LZ77': [CompressionAlgorithm.GZIP, CompressionAlgorithm.LZ4],
            'LZ78': [CompressionAlgorithm.LZMA],
            'BWT': [CompressionAlgorithm.BZIP2],
            'PPM': [CompressionAlgorithm.ZSTD],
            'Dictionary': [CompressionAlgorithm.BROTLI],
            'Advanced': [
                CompressionAlgorithm.QUANTUM_BIOLOGICAL,
                CompressionAlgorithm.NEUROMORPHIC,
                CompressionAlgorithm.TOPOLOGICAL,
                CompressionAlgorithm.CONTENT_AWARE
            ]
        }
        
        # Content type to algorithm family mapping
        self.content_type_mapping = {
            ContentType.TEXT: ['LZ77', 'LZ78', 'Dictionary'],
            ContentType.CODE: ['LZ77', 'LZ78', 'BWT'],
            ContentType.BINARY: ['LZ77', 'BWT', 'Advanced'],
            ContentType.DATA: ['LZ77', 'PPM', 'Dictionary'],
            ContentType.DOCUMENT: ['LZ77', 'PPM', 'Dictionary'],
            ContentType.UNKNOWN: ['LZ77', 'LZ78', 'Advanced']
        }
        
        # Performance weights for different metrics
        self.metric_weights = {
            'compression_ratio': 0.4,
            'speed': 0.3,
            'quality': 0.2,
            'memory': 0.1
        }
        
        # Historical performance data (would be loaded from database in real implementation)
        self.performance_history = {}
    
    def select_algorithm(self, content_analysis: Dict[str, Any]) -> CompressionAlgorithm:
        """
        Select the best compression algorithm based on content analysis.
        
        Args:
            content_analysis: Results from content analysis
            
        Returns:
            Selected compression algorithm
        """
        # Get content type
        content_type = content_analysis.get('content_type_score', {}).get('type', ContentType.TEXT)
        
        # Get suitable algorithm families
        suitable_families = self.content_type_mapping.get(content_type, ['LZ77'])
        
        # Select algorithm family
        selected_family = self._select_algorithm_family(suitable_families, content_analysis)
        
        # Get algorithm variants for the selected family
        variants = self.algorithm_families.get(selected_family, [CompressionAlgorithm.GZIP])
        
        # Select specific algorithm variant
        selected_algorithm = self._select_algorithm_variant(variants, content_analysis)
        
        return selected_algorithm
    
    def _select_algorithm_family(self, suitable_families: List[str], content_analysis: Dict[str, Any]) -> str:
        """Select algorithm family based on content characteristics."""
        # Calculate family scores based on content analysis
        family_scores = {}
        
        for family in suitable_families:
            score = self._calculate_family_score(family, content_analysis)
            family_scores[family] = score
        
        # Add some randomness for exploration
        if random.random() < 0.1:  # 10% exploration
            return random.choice(suitable_families)
        
        # Return family with highest score
        return max(family_scores.items(), key=lambda x: x[1])[0]
    
    def _select_algorithm_variant(self, variants: List[CompressionAlgorithm], content_analysis: Dict[str, Any]) -> CompressionAlgorithm:
        """Select specific algorithm variant."""
        # Calculate variant scores
        variant_scores = {}
        
        for variant in variants:
            score = self._calculate_variant_score(variant, content_analysis)
            variant_scores[variant] = score
        
        # Add some randomness for exploration
        if random.random() < 0.15:  # 15% exploration
            return random.choice(variants)
        
        # Return variant with highest score
        return max(variant_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_family_score(self, family: str, content_analysis: Dict[str, Any]) -> float:
        """Calculate score for an algorithm family based on content analysis."""
        score = 0.0
        
        # Get content profile
        content_profile = content_analysis.get('content_profile', [0.0] * 8)
        
        if family == 'LZ77':
            # LZ77 works well with repetitive patterns and moderate entropy
            entropy = content_profile[0] if len(content_profile) > 0 else 0.0
            pattern_frequency = content_profile[5] if len(content_profile) > 5 else 0.0
            score = (1 - entropy / 8.0) * 0.6 + pattern_frequency * 0.4
            
        elif family == 'LZ78':
            # LZ78 works well with high entropy and complex patterns
            entropy = content_profile[0] if len(content_profile) > 0 else 0.0
            language_complexity = content_profile[1] if len(content_profile) > 1 else 0.0
            score = (entropy / 8.0) * 0.5 + language_complexity * 0.5
            
        elif family == 'BWT':
            # BWT works well with repetitive patterns and low entropy
            entropy = content_profile[0] if len(content_profile) > 0 else 0.0
            redundancy_ratio = content_profile[3] if len(content_profile) > 3 else 0.0
            score = (1 - entropy / 8.0) * 0.7 + redundancy_ratio * 0.3
            
        elif family == 'PPM':
            # PPM works well with high-order context and structured data
            semantic_density = content_profile[4] if len(content_profile) > 4 else 0.0
            code_structure = content_profile[2] if len(content_profile) > 2 else 0.0
            score = semantic_density * 0.6 + code_structure * 0.4
            
        elif family == 'Dictionary':
            # Dictionary methods work well with structured data
            semantic_density = content_profile[4] if len(content_profile) > 4 else 0.0
            content_type_confidence = content_profile[7] if len(content_profile) > 7 else 0.0
            score = semantic_density * 0.5 + content_type_confidence * 0.5
            
        elif family == 'Advanced':
            # Advanced algorithms for complex content
            compression_potential = content_profile[6] if len(content_profile) > 6 else 0.0
            language_complexity = content_profile[1] if len(content_profile) > 1 else 0.0
            score = compression_potential * 0.6 + language_complexity * 0.4
        
        # Add historical performance factor
        historical_score = self._get_historical_performance(family, content_analysis)
        score = score * 0.7 + historical_score * 0.3
        
        return score
    
    def _calculate_variant_score(self, variant: CompressionAlgorithm, content_analysis: Dict[str, Any]) -> float:
        """Calculate score for a specific algorithm variant."""
        score = 0.0
        
        # Get content profile
        content_profile = content_analysis.get('content_profile', [0.0] * 8)
        
        if variant == CompressionAlgorithm.GZIP:
            # GZIP: good general-purpose compression
            score = 0.7  # Baseline score
            
        elif variant == CompressionAlgorithm.LZMA:
            # LZMA: high compression ratio, slower
            compression_potential = content_profile[6] if len(content_profile) > 6 else 0.0
            score = 0.5 + compression_potential * 0.5
            
        elif variant == CompressionAlgorithm.BZIP2:
            # BZIP2: good for repetitive data
            redundancy_ratio = content_profile[3] if len(content_profile) > 3 else 0.0
            score = 0.6 + redundancy_ratio * 0.4
            
        elif variant == CompressionAlgorithm.LZ4:
            # LZ4: fast compression
            language_complexity = content_profile[1] if len(content_profile) > 1 else 0.0
            score = 0.8 - language_complexity * 0.3  # Prefer for simpler content
            
        elif variant == CompressionAlgorithm.ZSTD:
            # Zstandard: good balance
            score = 0.75  # Good general-purpose score
            
        elif variant == CompressionAlgorithm.BROTLI:
            # Brotli: good for web content
            semantic_density = content_profile[4] if len(content_profile) > 4 else 0.0
            score = 0.6 + semantic_density * 0.4
            
        elif variant == CompressionAlgorithm.CONTENT_AWARE:
            # Content-aware: analyze and choose best
            score = 0.8  # High score for adaptive approach
            
        else:
            # Advanced algorithms: high potential but experimental
            compression_potential = content_profile[6] if len(content_profile) > 6 else 0.0
            score = 0.5 + compression_potential * 0.5
        
        # Add historical performance factor
        historical_score = self._get_historical_performance(str(variant), content_analysis)
        score = score * 0.7 + historical_score * 0.3
        
        return score
    
    def _get_historical_performance(self, algorithm: str, content_analysis: Dict[str, Any]) -> float:
        """Get historical performance score for an algorithm."""
        # In a real implementation, this would query a database
        # For now, return a random score to simulate historical data
        return random.uniform(0.3, 0.9)
    
    def update_performance_history(self, algorithm: str, content_profile: List[float], performance: Dict[str, float]):
        """Update performance history with new results."""
        # In a real implementation, this would store data in a database
        key = f"{algorithm}_{hash(tuple(content_profile))}"
        self.performance_history[key] = performance
    
    def get_algorithm_recommendations(self, content_analysis: Dict[str, Any], num_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Get top algorithm recommendations for content."""
        recommendations = []
        
        # Get all possible algorithms
        all_algorithms = []
        for family, variants in self.algorithm_families.items():
            all_algorithms.extend(variants)
        
        # Calculate scores for all algorithms
        algorithm_scores = []
        for algorithm in all_algorithms:
            score = self._calculate_variant_score(algorithm, content_analysis)
            algorithm_scores.append((algorithm, score))
        
        # Sort by score and return top recommendations
        algorithm_scores.sort(key=lambda x: x[1], reverse=True)
        
        for i, (algorithm, score) in enumerate(algorithm_scores[:num_recommendations]):
            recommendations.append({
                'algorithm': algorithm,
                'score': score,
                'rank': i + 1,
                'confidence': min(score * 1.2, 1.0)
            })
        
        return recommendations






