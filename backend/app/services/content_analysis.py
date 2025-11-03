"""
Content Analysis Service for the Dynamic Compression Algorithms backend.

This service provides comprehensive content analysis including type detection,
entropy calculation, pattern recognition, and compression suitability assessment.
"""

import re
import math
import hashlib
from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime

# Optional dependencies - handle gracefully if not available
try:
    import chardet
except ImportError:
    chardet = None

try:
    import langdetect
except ImportError:
    langdetect = None

class ContentAnalysisService:
    """Service for analyzing content characteristics and compression suitability."""
    
    def __init__(self):
        self.content_type_patterns = {
            'text': [
                r'^[a-zA-Z\s\.,!?;:\'"-]+$',
                r'^[a-zA-Z0-9\s\.,!?;:\'"-]+$'
            ],
            'json': [
                r'^\s*[\{\[].*[\}\]]\s*$',
                r'^\s*\{.*\}\s*$',
                r'^\s*\[.*\]\s*$'
            ],
            'xml': [
                r'^\s*<[^>]+>.*</[^>]+>\s*$',
                r'^\s*<\?xml.*\?>\s*$'
            ],
            'csv': [
                r'^[^,\n]+(,[^,\n]+)+$',
                r'^[^,\n]+(,[^,\n]+)*\n[^,\n]+(,[^,\n]+)+$'
            ],
            'code': [
                r'^\s*(function|def|class|import|from|var|let|const|if|for|while)\s+',
                r'^\s*#.*$',
                r'^\s*//.*$',
                r'^\s*/\*.*\*/$'
            ],
            'log': [
                r'^\d{4}-\d{2}-\d{2}.*$',
                r'^\d{2}:\d{2}:\d{2}.*$',
                r'^\[.*\]\s+.*$'
            ]
        }
        
        self.compression_patterns = {
            'repetitive': r'(.)\1{3,}',
            'structured': r'^\s*[\{\[<].*[\}\]>]\s*$',
            'tabular': r'^[^,\n]+(,[^,\n]+)+$',
            'sequential': r'^\d+\.\s+.*$',
            'key_value': r'^[^:]+:\s*.*$'
        }
    
    async def analyze_content(self, content: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive content analysis.
        
        Args:
            content: The content to analyze
            options: Analysis options
            
        Returns:
            Dictionary containing analysis results
        """
        if not content:
            raise ValueError("Content cannot be empty")
        
        options = options or {}
        
        # Basic content information
        content_size = len(content)
        encoding = self._detect_encoding(content)
        language = self._detect_language(content)
        
        # Content type detection
        content_type = self._detect_content_type(content)
        
        # Entropy and redundancy analysis
        entropy = self._calculate_entropy(content)
        redundancy = self._calculate_redundancy(content)
        
        # Pattern detection
        patterns = []
        if options.get('include_patterns', True):
            patterns = self._detect_patterns(content)
        
        # Compressibility assessment
        compressibility = self._assess_compressibility(content, entropy, redundancy, patterns)
        
        # Quality metrics
        quality_metrics = {}
        if options.get('include_quality', True):
            quality_metrics = self._assess_quality(content, content_type)
        
        # Performance predictions
        predictions = {}
        if options.get('include_predictions', True):
            predictions = self._predict_performance(content_type, entropy, redundancy, patterns)
        
        return {
            'content_type': content_type,
            'content_size': content_size,
            'encoding': encoding,
            'language': language,
            'entropy': entropy,
            'redundancy': redundancy,
            'structure': self._analyze_structure(content),
            'patterns': patterns,
            'compressibility': compressibility,
            'quality_metrics': quality_metrics,
            'predictions': predictions
        }
    
    def _detect_encoding(self, content: str) -> str:
        """Detect content encoding."""
        if chardet is None:
            return 'utf-8'
        
        try:
            # Try to detect encoding from bytes
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            result = chardet.detect(content_bytes)
            return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'
    
    def _detect_language(self, content: str) -> str:
        """Detect content language."""
        if langdetect is None:
            return 'unknown'
        
        try:
            # Use first 1000 characters for language detection
            sample = content[:1000] if len(content) > 1000 else content
            return langdetect.detect(sample)
        except:
            return 'unknown'
    
    def _detect_content_type(self, content: str) -> Dict[str, Any]:
        """Detect content type with confidence score."""
        content_lower = content.lower().strip()
        
        # Check each content type pattern
        type_scores = {}
        for content_type, patterns in self.content_type_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                    score += 1
            
            if score > 0:
                type_scores[content_type] = score / len(patterns)
        
        # Determine primary and secondary types
        if type_scores:
            sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
            primary_type = sorted_types[0][0]
            primary_confidence = sorted_types[0][1]
            
            secondary_type = sorted_types[1][0] if len(sorted_types) > 1 else primary_type
            secondary_confidence = sorted_types[1][1] if len(sorted_types) > 1 else 0
            
            return {
                'primary': primary_type,
                'secondary': secondary_type,
                'confidence': primary_confidence
            }
        else:
            return {
                'primary': 'text',
                'secondary': 'unknown',
                'confidence': 0.5
            }
    
    def _calculate_entropy(self, content: str) -> float:
        """Calculate Shannon entropy of the content."""
        if not content:
            return 0.0
        
        # Count character frequencies
        char_counts = Counter(content)
        total_chars = len(content)
        
        # Calculate entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_redundancy(self, content: str) -> float:
        """Calculate content redundancy (repetitive patterns)."""
        if not content:
            return 0.0
        
        # Look for repetitive patterns
        redundancy_score = 0.0
        
        # Check for repeated characters
        char_repeats = len(re.findall(r'(.)\1{2,}', content))
        redundancy_score += char_repeats / len(content)
        
        # Check for repeated words
        words = content.split()
        if words:
            word_counts = Counter(words)
            repeated_words = sum(1 for count in word_counts.values() if count > 1)
            redundancy_score += repeated_words / len(word_counts)
        
        # Check for repeated phrases (2-3 words)
        for phrase_length in [2, 3]:
            phrases = []
            for i in range(len(words) - phrase_length + 1):
                phrase = ' '.join(words[i:i + phrase_length])
                phrases.append(phrase)
            
            if phrases:
                phrase_counts = Counter(phrases)
                repeated_phrases = sum(1 for count in phrase_counts.values() if count > 1)
                redundancy_score += repeated_phrases / len(phrase_counts)
        
        return min(redundancy_score, 1.0)
    
    def _detect_patterns(self, content: str) -> List[str]:
        """Detect compression-relevant patterns in content."""
        patterns = []
        
        for pattern_name, pattern_regex in self.compression_patterns.items():
            if re.search(pattern_regex, content, re.MULTILINE | re.DOTALL):
                patterns.append(pattern_name)
        
        # Additional pattern detection
        if re.search(r'^\s*[\{\[<]', content, re.MULTILINE):
            patterns.append('structured')
        
        if re.search(r'^\d+\.\s+', content, re.MULTILINE):
            patterns.append('numbered_list')
        
        if re.search(r'^[A-Z][a-z]+:\s*', content, re.MULTILINE):
            patterns.append('key_value_pairs')
        
        return patterns
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure."""
        lines = content.split('\n')
        
        return {
            'type': 'hierarchical' if any(re.search(r'^\s+', line) for line in lines) else 'flat',
            'complexity': self._calculate_structure_complexity(content),
            'patterns': self._detect_patterns(content)
        }
    
    def _calculate_structure_complexity(self, content: str) -> float:
        """Calculate structural complexity score."""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        # Calculate indentation complexity
        indentation_levels = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indentation_levels.append(indent)
        
        if indentation_levels:
            complexity = len(set(indentation_levels)) / max(indentation_levels) if max(indentation_levels) > 0 else 0
        else:
            complexity = 0
        
        # Factor in line length variation
        line_lengths = [len(line) for line in lines if line.strip()]
        if line_lengths:
            length_variation = max(line_lengths) - min(line_lengths)
            complexity += length_variation / max(line_lengths) if max(line_lengths) > 0 else 0
        
        return min(complexity, 1.0)
    
    def _assess_compressibility(self, content: str, entropy: float, redundancy: float, patterns: List[str]) -> float:
        """Assess how well the content can be compressed (0-10 scale)."""
        score = 5.0  # Base score
        
        # Entropy factor (lower entropy = more compressible)
        if entropy < 3.0:
            score += 2.0
        elif entropy < 4.0:
            score += 1.0
        elif entropy > 6.0:
            score -= 2.0
        
        # Redundancy factor (higher redundancy = more compressible)
        score += redundancy * 3.0
        
        # Pattern factor
        pattern_bonus = 0
        for pattern in patterns:
            if pattern in ['repetitive', 'structured', 'tabular']:
                pattern_bonus += 0.5
            elif pattern in ['sequential', 'key_value']:
                pattern_bonus += 0.3
        
        score += pattern_bonus
        
        # Content type factor
        content_type = self._detect_content_type(content)
        if content_type['primary'] in ['text', 'json', 'xml']:
            score += 1.0
        elif content_type['primary'] in ['code', 'log']:
            score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def _assess_quality(self, content: str, content_type: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content quality metrics."""
        quality_metrics = {
            'readability': 0.8,  # Default value
            'integrity': 1.0,    # Default value
            'validation': 'passed'
        }
        
        # Readability assessment
        if content_type['primary'] == 'text':
            quality_metrics['readability'] = self._assess_readability(content)
        
        # Integrity check
        quality_metrics['integrity'] = self._check_integrity(content, content_type)
        
        # Validation
        if quality_metrics['integrity'] < 0.8:
            quality_metrics['validation'] = 'warning'
        elif quality_metrics['integrity'] < 0.6:
            quality_metrics['validation'] = 'failed'
        
        return quality_metrics
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability (0-1 scale)."""
        if not content:
            return 0.0
        
        # Simple readability metrics
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability score (inverse relationship with complexity)
        readability = 1.0 - (avg_sentence_length / 20.0) - (avg_word_length / 10.0)
        
        return max(0.0, min(1.0, readability))
    
    def _check_integrity(self, content: str, content_type: Dict[str, Any]) -> float:
        """Check content integrity based on type."""
        if not content:
            return 0.0
        
        integrity_score = 1.0
        
        # JSON integrity
        if content_type['primary'] == 'json':
            try:
                import json
                json.loads(content)
            except:
                integrity_score -= 0.5
        
        # XML integrity
        elif content_type['primary'] == 'xml':
            try:
                import xml.etree.ElementTree as ET
                ET.fromstring(content)
            except:
                integrity_score -= 0.5
        
        # General text integrity
        elif content_type['primary'] == 'text':
            # Check for encoding issues
            try:
                content.encode('utf-8').decode('utf-8')
            except:
                integrity_score -= 0.3
        
        return max(0.0, min(1.0, integrity_score))
    
    def _predict_performance(self, content_type: Dict[str, Any], entropy: float, 
                           redundancy: float, patterns: List[str]) -> Dict[str, Any]:
        """Predict compression performance."""
        # Algorithm recommendations based on content characteristics
        optimal_algorithms = []
        
        if content_type['primary'] == 'text':
            if redundancy > 0.3:
                optimal_algorithms.extend(['gzip', 'zstd'])
            else:
                optimal_algorithms.extend(['zstd', 'brotli'])
        elif content_type['primary'] == 'json':
            optimal_algorithms.extend(['zstd', 'gzip'])
        elif content_type['primary'] == 'xml':
            optimal_algorithms.extend(['gzip', 'zstd'])
        elif content_type['primary'] == 'code':
            optimal_algorithms.extend(['gzip', 'lz4'])
        else:
            optimal_algorithms.extend(['gzip', 'zstd', 'brotli'])
        
        # Expected compression ratio
        base_ratio = 2.0
        if redundancy > 0.5:
            base_ratio += 1.0
        if entropy < 4.0:
            base_ratio += 0.5
        if 'structured' in patterns:
            base_ratio += 0.3
        
        expected_compression_ratio = min(base_ratio, 5.0)
        
        # Confidence in predictions
        confidence = 0.7
        if content_type['confidence'] > 0.8:
            confidence += 0.1
        if redundancy > 0.3:
            confidence += 0.1
        
        return {
            'optimal_algorithms': optimal_algorithms[:3],  # Top 3
            'expected_compression_ratio': expected_compression_ratio,
            'confidence': min(confidence, 1.0)
        }
