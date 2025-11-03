"""
Content analysis engine for the Dynamic Compression Algorithms backend.

This module implements the content profiling system described in the documentation,
including entropy calculation, language complexity analysis, code structure detection,
and pattern recognition.
"""

import math
import re
# import numpy as np  # Removed for compatibility
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import hashlib

from app.models.compression import ContentType
from app.models.file import FileMetadata


class ContentAnalyzer:
    """
    Content analysis engine that implements multi-dimensional content profiling.
    
    Based on the mathematical framework from the documentation:
    P = [p₁, p₂, p₃, p₄, p₅, p₆, p₇, p₈]
    where each pᵢ represents different content characteristics.
    """
    
    def __init__(self):
        """Initialize the content analyzer."""
        self.language_patterns = {
            'python': [r'def\s+\w+', r'import\s+\w+', r'class\s+\w+', r'if\s+__name__'],
            'javascript': [r'function\s+\w+', r'const\s+\w+', r'let\s+\w+', r'var\s+\w+'],
            'java': [r'public\s+class', r'private\s+\w+', r'public\s+static', r'import\s+java'],
            'cpp': [r'#include\s*<', r'int\s+main', r'class\s+\w+', r'std::'],
            'html': [r'<[^>]+>', r'<!DOCTYPE', r'<html', r'<head'],
            'css': [r'\{[^}]*\}', r'@media', r'@import', r'\.\w+'],
            'sql': [r'SELECT\s+', r'INSERT\s+INTO', r'UPDATE\s+', r'CREATE\s+TABLE'],
            'json': [r'\{[^}]*\}', r'\[[^\]]*\]', r'"[^"]*"\s*:', r'true|false|null'],
            'xml': [r'<[^>]+>', r'<\?xml', r'<!\[CDATA\[', r'</[^>]+>'],
            'yaml': [r'^\s*[\w-]+:', r'^\s*-\s+', r'^\s*#', r'^\s*---'],
        }
        
        self.structure_patterns = {
            'function_def': r'def\s+\w+\s*\([^)]*\)\s*:',
            'class_def': r'class\s+\w+',
            'import_stmt': r'import\s+\w+',
            'comment': r'#.*$',
            'string_literal': r'"[^"]*"',
            'number': r'\b\d+\.?\d*\b',
            'variable': r'\b[a-zA-Z_]\w*\b',
        }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive multi-dimensional content analysis.
        
        Analysis dimensions:
        1. Shannon Entropy: Information density measurement (0-8 bits)
        2. Language Complexity: Vocabulary richness, sentence structure
        3. Code Structure: Function/class density, nesting depth
        4. Redundancy Ratio: Repetition and pattern frequency
        5. Semantic Density: Meaningful content vs. total size
        6. Pattern Detection: Sliding window pattern analysis (2-16 bytes)
        7. Compression Potential: Estimated compressibility (0-1)
        8. Content Classification: Type detection with confidence score
        
        The analysis produces an 8-dimensional profile vector P used for:
        - Algorithm selection (hierarchical decision tree)
        - Parameter optimization strategy selection
        - Compression potential estimation
        - Protocol-specific content splitting decisions
        
        Args:
            content: The content to analyze
            
        Returns:
            Dictionary containing all analysis results and profile vector
        """
        if not content:
            return self._empty_analysis()
        
        analysis = {
            'entropy': self._calculate_entropy(content),
            'language_complexity': self._calculate_language_complexity(content),
            'code_structure': self._analyze_code_structure(content),
            'redundancy_ratio': self._calculate_redundancy_ratio(content),
            'semantic_density': self._calculate_semantic_density(content),
            'pattern_frequency': self._detect_patterns(content),
            'compression_potential': self._estimate_compression_potential(content),
            'content_type_score': self._classify_content_type(content),
            'locality_score': self._calculate_locality_score(content),
            'temporal_score': self._calculate_temporal_score(content),
        }
        
        # Calculate overall content profile vector
        analysis['content_profile'] = self._calculate_content_profile(analysis)
        
        return analysis
    
    def _calculate_entropy(self, content: str) -> float:
        """
        Calculate Shannon entropy - fundamental measure of information content.
        
        H(S) = -Σ p(x) log₂ p(x)
        
        Where:
        - p(x) is the probability of character x appearing
        - Result ranges from 0 (uniform) to 8 (maximum for 8-bit data)
        - Lower entropy indicates more compressible content
        
        Used for:
        - Primary compression potential indicator
        - Algorithm family selection (LZ77 for low, LZ78 for high)
        - Determining if content is already compressed
        """
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
    
    def _calculate_language_complexity(self, content: str) -> float:
        """
        Calculate language complexity using multiple metrics.
        
        Language_Complexity(S) = Σ wᵢ × freq(wᵢ) / |S|
        """
        if not content:
            return 0.0
        
        # Tokenize content
        tokens = self._tokenize_content(content)
        if not tokens:
            return 0.0
        
        # Calculate various complexity metrics
        avg_word_length = sum(len(token) for token in tokens) / len(tokens)
        vocabulary_richness = len(set(tokens)) / len(tokens)
        sentence_complexity = self._calculate_sentence_complexity(content)
        syntactic_complexity = self._calculate_syntactic_complexity(content)
        semantic_complexity = self._calculate_semantic_complexity(content)
        
        # Combine metrics with weights
        complexity_score = (
            avg_word_length * 0.2 +
            vocabulary_richness * 0.3 +
            sentence_complexity * 0.2 +
            syntactic_complexity * 0.2 +
            semantic_complexity * 0.1
        )
        
        return complexity_score
    
    def _analyze_code_structure(self, content: str) -> float:
        """
        Analyze code structure and complexity.
        
        Code_Structure(S) = Σ syntax_patterns / |S|
        """
        if not content:
            return 0.0
        
        # Count structural elements
        structure_counts = {}
        for pattern_name, pattern in self.structure_patterns.items():
            matches = len(re.findall(pattern, content, re.MULTILINE))
            structure_counts[pattern_name] = matches
        
        # Calculate structure score
        total_patterns = sum(structure_counts.values())
        structure_score = total_patterns / len(content) if len(content) > 0 else 0
        
        # Add complexity factors
        nesting_depth = self._calculate_nesting_depth(content)
        function_count = structure_counts.get('function_def', 0)
        class_count = structure_counts.get('class_def', 0)
        
        # Normalize and combine
        normalized_score = (
            structure_score * 0.4 +
            (nesting_depth / 10) * 0.3 +
            (function_count / 100) * 0.2 +
            (class_count / 50) * 0.1
        )
        
        return min(normalized_score, 1.0)
    
    def _calculate_redundancy_ratio(self, content: str) -> float:
        """
        Calculate redundancy ratio.
        
        Redundancy_Ratio(S) = 1 - |unique_symbols| / |total_symbols|
        """
        if not content:
            return 0.0
        
        unique_chars = len(set(content))
        total_chars = len(content)
        
        return 1 - (unique_chars / total_chars)
    
    def _calculate_semantic_density(self, content: str) -> float:
        """
        Calculate semantic density.
        
        Semantic_Density(S) = semantic_units / total_units
        """
        if not content:
            return 0.0
        
        # Count semantic units (words, meaningful tokens)
        tokens = self._tokenize_content(content)
        semantic_units = len([t for t in tokens if len(t) > 2])  # Filter out short tokens
        
        total_units = len(content)
        
        return semantic_units / total_units if total_units > 0 else 0.0
    
    def _detect_patterns(self, content: str) -> Dict[str, Any]:
        """
        Detect repeating patterns using multi-scale sliding window analysis.
        
        Pattern_Frequency(S) = Σ pattern_count / |S|
        
        Pattern detection strategy:
        - Window sizes: [2, 3, 4, 8, 16] bytes
        - Identifies local (short-range) and global (long-range) patterns
        - Tracks pattern frequency and distribution
        
        Critical for:
        - LZ77/LZSS algorithm effectiveness prediction
        - Dictionary-based compression potential
        - Content splitting boundaries identification
        - Determining optimal window/dictionary sizes
        
        Future enhancement:
        - Variable-length pattern detection
        - Semantic pattern recognition for text
        - Protocol-specific pattern templates
        """
        if not content:
            return {'patterns': {}, 'frequency': 0.0}
        
        patterns = {}
        pattern_lengths = [2, 3, 4, 8, 16]
        
        for length in pattern_lengths:
            pattern_counts = {}
            
            # Slide window over content
            for i in range(len(content) - length + 1):
                pattern = content[i:i+length]
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            # Filter significant patterns
            significant_patterns = {
                pattern: count for pattern, count in pattern_counts.items()
                if count > 1 and len(pattern) > 1
            }
            
            patterns[f'length_{length}'] = significant_patterns
        
        # Calculate overall pattern frequency
        total_patterns = sum(len(patterns[f'length_{l}']) for l in pattern_lengths)
        pattern_frequency = total_patterns / len(content) if len(content) > 0 else 0
        
        return {
            'patterns': patterns,
            'frequency': pattern_frequency,
            'total_patterns': total_patterns
        }
    
    def _estimate_compression_potential(self, content: str) -> float:
        """
        Estimate compression potential using multiple heuristics.
        """
        if not content:
            return 0.0
        
        # Get analysis results
        entropy = self._calculate_entropy(content)
        redundancy = self._calculate_redundancy_ratio(content)
        pattern_data = self._detect_patterns(content)
        pattern_density = pattern_data['frequency']
        
        # Normalize values
        normalized_entropy = entropy / 8.0  # Max entropy for 8-bit data
        normalized_redundancy = redundancy
        normalized_pattern_density = min(pattern_density * 100, 1.0)
        
        # Weighted combination
        compression_potential = (
            normalized_entropy * 0.4 +
            normalized_redundancy * 0.4 +
            normalized_pattern_density * 0.2
        )
        
        return min(compression_potential, 1.0)
    
    def _classify_content_type(self, content: str) -> Dict[str, Any]:
        """
        Classify content type using pattern matching and heuristics.
        
        Classification strategy:
        1. Language Detection: Regex patterns for 10+ programming languages
        2. Structure Detection: JSON, XML, YAML, CSV formats
        3. Binary Detection: Null bytes and control character analysis
        4. Text Classification: Natural language vs. structured text
        
        Content types determine:
        - Algorithm family preferences
        - Optimal compression parameters
        - Quality metric weighting
        - Potential for LLM-based symbolic compression
        
        Future enhancements:
        - ML-based classification model
        - MIME type integration
        - Protocol-specific content detection
        - Multi-format content handling
        """
        if not content:
            return {'type': ContentType.TEXT, 'language': None, 'confidence': 0.0}
        
        # Detect programming language
        language_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
                score += matches
            language_scores[lang] = score
        
        # Find best language match
        best_language = max(language_scores.items(), key=lambda x: x[1])
        
        # Determine content type
        if best_language[1] > 5:  # Strong code indicators
            content_type = ContentType.CODE
            confidence = min(best_language[1] / 20, 1.0)
        elif self._is_structured_content(content):
            content_type = ContentType.STRUCTURED
            confidence = 0.8
        elif self._is_binary_content(content):
            content_type = ContentType.BINARY
            confidence = 0.9
        else:
            content_type = ContentType.TEXT
            confidence = 0.7
        
        return {
            'type': content_type,
            'language': best_language[0] if best_language[1] > 0 else None,
            'confidence': confidence,
            'language_scores': language_scores
        }
    
    def _calculate_locality_score(self, content: str) -> float:
        """
        Calculate spatial locality score.
        """
        if not content:
            return 0.0
        
        # Analyze character repetition patterns
        locality_score = 0.0
        window_size = 100
        
        for i in range(0, len(content) - window_size, window_size // 2):
            window = content[i:i+window_size]
            unique_chars = len(set(window))
            locality_score += unique_chars / window_size
        
        return locality_score / max(1, (len(content) - window_size) // (window_size // 2))
    
    def _calculate_temporal_score(self, content: str) -> float:
        """
        Calculate temporal redundancy score.
        """
        if not content:
            return 0.0
        
        # Analyze temporal patterns (repetition over distance)
        temporal_score = 0.0
        max_distance = min(1000, len(content) // 2)
        
        for distance in range(1, max_distance, 10):
            matches = 0
            for i in range(len(content) - distance):
                if content[i] == content[i + distance]:
                    matches += 1
            
            if len(content) - distance > 0:
                temporal_score += matches / (len(content) - distance)
        
        return temporal_score / (max_distance // 10) if max_distance > 10 else 0.0
    
    def _calculate_content_profile(self, analysis: Dict[str, Any]) -> List[float]:
        """
        Calculate the 8-dimensional content profile vector for ML-based decisions.
        
        Profile Vector: P = [p₁, p₂, p₃, p₄, p₅, p₆, p₇, p₈]
        
        Dimensions:
        - p₁: Entropy (0-8) - Information density
        - p₂: Language Complexity (0-1) - Structural complexity
        - p₃: Code Structure (0-1) - Programming construct density
        - p₄: Redundancy Ratio (0-1) - Repetition level
        - p₅: Semantic Density (0-1) - Meaningful content ratio
        - p₆: Pattern Frequency (0-1) - Pattern occurrence rate
        - p₇: Compression Potential (0-1) - Estimated compressibility
        - p₈: Content Confidence (0-1) - Classification certainty
        
        This vector feeds into:
        - Neural network models for algorithm prediction
        - Clustering algorithms for content similarity
        - Optimization strategy selection
        - Performance prediction models
        """
        return [
            analysis['entropy'],
            analysis['language_complexity'],
            analysis['code_structure'],
            analysis['redundancy_ratio'],
            analysis['semantic_density'],
            analysis['pattern_frequency']['frequency'],
            analysis['compression_potential'],
            analysis['content_type_score']['confidence']
        ]
    
    def _tokenize_content(self, content: str) -> List[str]:
        """Tokenize content into words/tokens."""
        # Simple tokenization - can be enhanced
        tokens = re.findall(r'\b\w+\b', content.lower())
        return [token for token in tokens if len(token) > 1]
    
    def _calculate_sentence_complexity(self, content: str) -> float:
        """Calculate sentence complexity."""
        sentences = re.split(r'[.!?]+', content)
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        return min(avg_sentence_length / 20, 1.0)  # Normalize
    
    def _calculate_syntactic_complexity(self, content: str) -> float:
        """Calculate syntactic complexity."""
        # Count syntactic elements
        syntactic_elements = len(re.findall(r'[{}()\[\]]', content))
        return min(syntactic_elements / len(content), 1.0) if content else 0.0
    
    def _calculate_semantic_complexity(self, content: str) -> float:
        """Calculate semantic complexity."""
        # Simple semantic complexity based on unique words
        tokens = self._tokenize_content(content)
        if not tokens:
            return 0.0
        
        unique_ratio = len(set(tokens)) / len(tokens)
        return unique_ratio
    
    def _calculate_nesting_depth(self, content: str) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        
        for char in content:
            if char in '{([<':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '})]>':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _is_structured_content(self, content: str) -> bool:
        """Check if content is structured (JSON, XML, etc.)."""
        # Check for JSON structure
        if content.strip().startswith('{') and content.strip().endswith('}'):
            return True
        
        # Check for XML structure
        if re.search(r'<\?xml|<[^>]+>', content):
            return True
        
        # Check for CSV structure
        lines = content.split('\n')
        if len(lines) > 1 and ',' in lines[0]:
            return True
        
        return False
    
    def _is_binary_content(self, content: str) -> bool:
        """Check if content appears to be binary."""
        # Check for null bytes and control characters
        null_bytes = content.count('\x00')
        control_chars = sum(1 for c in content if ord(c) < 32 and c not in '\n\r\t')
        
        return null_bytes > 0 or control_chars > len(content) * 0.1
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis results."""
        return {
            'entropy': 0.0,
            'language_complexity': 0.0,
            'code_structure': 0.0,
            'redundancy_ratio': 0.0,
            'semantic_density': 0.0,
            'pattern_frequency': {'patterns': {}, 'frequency': 0.0, 'total_patterns': 0},
            'compression_potential': 0.0,
            'content_type_score': {'type': ContentType.TEXT, 'language': None, 'confidence': 0.0},
            'locality_score': 0.0,
            'temporal_score': 0.0,
            'content_profile': [0.0] * 8
        }






