"""
Content analysis service for the Dynamic Compression Algorithms backend.
"""

import logging
import math
import re
import chardet
from typing import Dict, List, Any, Optional
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


class ContentAnalysisService:
    """Service for analyzing content characteristics and patterns."""
    
    @staticmethod
    async def analyze_content(content_data: bytes) -> Dict[str, Any]:
        """
        Analyze content data for characteristics and patterns.
        
        Args:
            content_data: Content data to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            analysis_result = {
                'content_type': 'unknown',
                'content_size': len(content_data),
                'patterns': [],
                'entropy': 0.0,
                'redundancy': 0.0,
                'structure': 'unknown',
                'language': 'unknown',
                'encoding': 'unknown',
                'byte_frequency': {},
                'pattern_frequency': {},
                'compression_potential': 0.0,
                'metadata': {}
            }
            
            if not content_data:
                return analysis_result
            
            # Analyze byte frequency and entropy
            byte_freq = Counter(content_data)
            analysis_result['byte_frequency'] = {str(k): v for k, v in byte_freq.items()}
            analysis_result['entropy'] = ContentAnalysisService._calculate_entropy(byte_freq, len(content_data))
            
            # Detect encoding
            encoding_result = chardet.detect(content_data)
            analysis_result['encoding'] = encoding_result.get('encoding', 'unknown')
            analysis_result['encoding_confidence'] = encoding_result.get('confidence', 0.0)
            
            # Try to decode as text for further analysis
            try:
                if analysis_result['encoding'] and analysis_result['encoding'] != 'unknown':
                    text_content = content_data.decode(analysis_result['encoding'])
                    text_analysis = ContentAnalysisService._analyze_text_content(text_content)
                    analysis_result.update(text_analysis)
                else:
                    # Try common encodings
                    for encoding in ['utf-8', 'latin-1', 'ascii']:
                        try:
                            text_content = content_data.decode(encoding)
                            analysis_result['encoding'] = encoding
                            text_analysis = ContentAnalysisService._analyze_text_content(text_content)
                            analysis_result.update(text_analysis)
                            break
                        except UnicodeDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"Could not decode content as text: {e}")
            
            # Analyze patterns
            patterns = ContentAnalysisService._detect_patterns(content_data)
            analysis_result['patterns'] = patterns
            
            # Calculate pattern frequency
            pattern_freq = ContentAnalysisService._calculate_pattern_frequency(content_data, patterns)
            analysis_result['pattern_frequency'] = pattern_freq
            
            # Calculate redundancy
            analysis_result['redundancy'] = ContentAnalysisService._calculate_redundancy(byte_freq, len(content_data))
            
            # Determine content type
            analysis_result['content_type'] = ContentAnalysisService._determine_content_type(
                content_data, analysis_result
            )
            
            # Calculate compression potential
            analysis_result['compression_potential'] = ContentAnalysisService._calculate_compression_potential(
                analysis_result
            )
            
            # Add metadata
            analysis_result['metadata'] = {
                'unique_bytes': len(byte_freq),
                'most_common_byte': max(byte_freq.items(), key=lambda x: x[1])[0] if byte_freq else None,
                'least_common_byte': min(byte_freq.items(), key=lambda x: x[1])[0] if byte_freq else None,
                'pattern_count': len(patterns),
                'analysis_timestamp': '2024-01-01T00:00:00Z'  # Would be actual timestamp
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {
                'content_type': 'error',
                'error': str(e),
                'content_size': len(content_data) if content_data else 0
            }
    
    @staticmethod
    def _calculate_entropy(byte_freq: Counter, total_bytes: int) -> float:
        """
        Calculate Shannon entropy of the content.
        
        Args:
            byte_freq: Byte frequency counter
            total_bytes: Total number of bytes
            
        Returns:
            float: Entropy value (0-8 bits per byte)
        """
        if total_bytes == 0:
            return 0.0
        
        entropy = 0.0
        for count in byte_freq.values():
            if count > 0:
                probability = count / total_bytes
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def _calculate_redundancy(byte_freq: Counter, total_bytes: int) -> float:
        """
        Calculate redundancy of the content.
        
        Args:
            byte_freq: Byte frequency counter
            total_bytes: Total number of bytes
            
        Returns:
            float: Redundancy value (0-1)
        """
        if total_bytes == 0:
            return 0.0
        
        # Calculate redundancy as 1 - (entropy / max_entropy)
        entropy = ContentAnalysisService._calculate_entropy(byte_freq, total_bytes)
        max_entropy = 8.0  # Maximum entropy for 8-bit bytes
        redundancy = 1.0 - (entropy / max_entropy)
        
        return max(0.0, min(1.0, redundancy))
    
    @staticmethod
    def _detect_patterns(content_data: bytes) -> List[str]:
        """
        Detect patterns in the content.
        
        Args:
            content_data: Content data to analyze
            
        Returns:
            List[str]: List of detected patterns
        """
        patterns = []
        
        if len(content_data) < 4:
            return patterns
        
        # Detect repeated sequences
        for length in range(2, min(21, len(content_data) // 2)):
            pattern_counts = Counter()
            
            for i in range(len(content_data) - length + 1):
                pattern = content_data[i:i + length]
                pattern_counts[pattern] += 1
            
            # Find patterns that appear multiple times
            for pattern, count in pattern_counts.items():
                if count >= 2:
                    pattern_str = f"repeated_{length}_byte_sequence"
                    if pattern_str not in patterns:
                        patterns.append(pattern_str)
        
        # Detect common file signatures
        file_signatures = {
            b'\x89PNG\r\n\x1a\n': 'png_signature',
            b'\xff\xd8\xff': 'jpeg_signature',
            b'GIF87a': 'gif_signature',
            b'GIF89a': 'gif_signature',
            b'%PDF': 'pdf_signature',
            b'PK\x03\x04': 'zip_signature',
            b'\x1f\x8b\x08': 'gzip_signature',
            b'BZh': 'bzip_signature',
            b'\x28\xb5\x2f\xfd': 'zstd_signature'
        }
        
        for signature, pattern_name in file_signatures.items():
            if content_data.startswith(signature):
                patterns.append(pattern_name)
        
        # Detect text patterns
        try:
            text_content = content_data.decode('utf-8', errors='ignore')
            
            # Detect common text patterns
            if re.search(r'[a-zA-Z]{3,}', text_content):
                patterns.append('text_content')
            
            if re.search(r'\d+', text_content):
                patterns.append('numeric_content')
            
            if re.search(r'[^\x00-\x7F]', text_content):
                patterns.append('unicode_content')
            
            # Detect structured data patterns
            if text_content.strip().startswith('{') and text_content.strip().endswith('}'):
                patterns.append('json_like')
            
            if text_content.strip().startswith('<') and text_content.strip().endswith('>'):
                patterns.append('xml_like')
            
            if re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=', text_content, re.MULTILINE):
                patterns.append('key_value_pairs')
                
        except UnicodeDecodeError:
            pass
        
        # Detect binary patterns
        null_bytes = content_data.count(b'\x00')
        if null_bytes > len(content_data) * 0.1:
            patterns.append('null_padded')
        
        # Detect compressed data patterns
        if ContentAnalysisService._is_likely_compressed(content_data):
            patterns.append('compressed_data')
        
        return patterns
    
    @staticmethod
    def _calculate_pattern_frequency(content_data: bytes, patterns: List[str]) -> Dict[str, int]:
        """
        Calculate frequency of detected patterns.
        
        Args:
            content_data: Content data
            patterns: List of detected patterns
            
        Returns:
            Dict[str, int]: Pattern frequency counts
        """
        pattern_freq = {}
        
        for pattern in patterns:
            if pattern == 'text_content':
                try:
                    text_content = content_data.decode('utf-8', errors='ignore')
                    pattern_freq[pattern] = len(re.findall(r'[a-zA-Z]{3,}', text_content))
                except UnicodeDecodeError:
                    pattern_freq[pattern] = 0
            
            elif pattern == 'numeric_content':
                try:
                    text_content = content_data.decode('utf-8', errors='ignore')
                    pattern_freq[pattern] = len(re.findall(r'\d+', text_content))
                except UnicodeDecodeError:
                    pattern_freq[pattern] = 0
            
            elif pattern == 'null_padded':
                pattern_freq[pattern] = content_data.count(b'\x00')
            
            elif pattern.startswith('repeated_'):
                # Extract length from pattern name
                try:
                    length = int(pattern.split('_')[1])
                    pattern_counts = Counter()
                    
                    for i in range(len(content_data) - length + 1):
                        pattern_bytes = content_data[i:i + length]
                        pattern_counts[pattern_bytes] += 1
                    
                    # Count patterns that appear multiple times
                    repeated_count = sum(1 for count in pattern_counts.values() if count >= 2)
                    pattern_freq[pattern] = repeated_count
                except (ValueError, IndexError):
                    pattern_freq[pattern] = 0
            
            else:
                pattern_freq[pattern] = 1
        
        return pattern_freq
    
    @staticmethod
    def _analyze_text_content(text_content: str) -> Dict[str, Any]:
        """
        Analyze text content for language and structure.
        
        Args:
            text_content: Text content to analyze
            
        Returns:
            Dict[str, Any]: Text analysis results
        """
        analysis = {
            'language': 'unknown',
            'structure': 'unknown',
            'text_characteristics': {}
        }
        
        if not text_content:
            return analysis
        
        # Basic text characteristics
        analysis['text_characteristics'] = {
            'length': len(text_content),
            'word_count': len(text_content.split()),
            'line_count': len(text_content.splitlines()),
            'character_frequency': dict(Counter(text_content.lower())),
            'average_word_length': np.mean([len(word) for word in text_content.split()]) if text_content.split() else 0
        }
        
        # Detect language (basic detection)
        analysis['language'] = ContentAnalysisService._detect_language(text_content)
        
        # Detect structure
        analysis['structure'] = ContentAnalysisService._detect_text_structure(text_content)
        
        return analysis
    
    @staticmethod
    def _detect_language(text_content: str) -> str:
        """
        Basic language detection.
        
        Args:
            text_content: Text content
            
        Returns:
            str: Detected language
        """
        # Simple character-based language detection
        text_lower = text_content.lower()
        
        # Common language patterns
        if re.search(r'[а-яё]', text_lower):
            return 'russian'
        elif re.search(r'[一-龯]', text_lower):
            return 'chinese'
        elif re.search(r'[あ-ん]', text_lower):
            return 'japanese'
        elif re.search(r'[가-힣]', text_lower):
            return 'korean'
        elif re.search(r'[ا-ي]', text_lower):
            return 'arabic'
        elif re.search(r'[α-ω]', text_lower):
            return 'greek'
        elif re.search(r'[a-z]', text_lower):
            return 'english'
        else:
            return 'unknown'
    
    @staticmethod
    def _detect_text_structure(text_content: str) -> str:
        """
        Detect text structure.
        
        Args:
            text_content: Text content
            
        Returns:
            str: Detected structure
        """
        lines = text_content.splitlines()
        
        if not lines:
            return 'unknown'
        
        # Check for JSON structure
        try:
            import json
            json.loads(text_content)
            return 'json'
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Check for XML structure
        if text_content.strip().startswith('<') and text_content.strip().endswith('>'):
            return 'xml'
        
        # Check for CSV structure
        if ',' in text_content and '\n' in text_content:
            first_line = lines[0]
            if first_line.count(',') >= 2:
                return 'csv'
        
        # Check for key-value pairs
        if re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[:=]\s*', text_content, re.MULTILINE):
            return 'key_value'
        
        # Check for code structure
        if any(keyword in text_content.lower() for keyword in ['def ', 'function ', 'class ', 'import ', 'from ']):
            return 'code'
        
        # Check for markdown
        if re.search(r'^#+\s+', text_content, re.MULTILINE) or re.search(r'\*\*.*\*\*', text_content):
            return 'markdown'
        
        # Check for plain text
        if len(lines) > 1 and any(len(line.strip()) > 50 for line in lines):
            return 'prose'
        
        return 'unknown'
    
    @staticmethod
    def _is_likely_compressed(content_data: bytes) -> bool:
        """
        Check if content is likely already compressed.
        
        Args:
            content_data: Content data
            
        Returns:
            bool: True if likely compressed
        """
        if len(content_data) < 100:
            return False
        
        # Check entropy - compressed data typically has high entropy
        byte_freq = Counter(content_data)
        entropy = ContentAnalysisService._calculate_entropy(byte_freq, len(content_data))
        
        # High entropy (>7.5) suggests compressed data
        if entropy > 7.5:
            return True
        
        # Check for compression signatures
        compression_signatures = [
            b'\x1f\x8b\x08',  # gzip
            b'BZh',           # bzip2
            b'\x28\xb5\x2f\xfd',  # zstd
            b'PK\x03\x04',    # zip
            b'\x50\x4b\x03\x04'  # zip (alternative)
        ]
        
        for signature in compression_signatures:
            if content_data.startswith(signature):
                return True
        
        return False
    
    @staticmethod
    def _determine_content_type(content_data: bytes, analysis_result: Dict[str, Any]) -> str:
        """
        Determine the content type based on analysis.
        
        Args:
            content_data: Content data
            analysis_result: Analysis results
            
        Returns:
            str: Content type
        """
        patterns = analysis_result.get('patterns', [])
        
        # Check for specific file types
        if 'png_signature' in patterns:
            return 'image/png'
        elif 'jpeg_signature' in patterns:
            return 'image/jpeg'
        elif 'gif_signature' in patterns:
            return 'image/gif'
        elif 'pdf_signature' in patterns:
            return 'application/pdf'
        elif 'zip_signature' in patterns:
            return 'application/zip'
        elif 'gzip_signature' in patterns:
            return 'application/gzip'
        elif 'bzip_signature' in patterns:
            return 'application/bzip2'
        elif 'zstd_signature' in patterns:
            return 'application/zstd'
        
        # Check for text content
        if 'text_content' in patterns:
            structure = analysis_result.get('structure', 'unknown')
            if structure == 'json':
                return 'application/json'
            elif structure == 'xml':
                return 'application/xml'
            elif structure == 'csv':
                return 'text/csv'
            elif structure == 'markdown':
                return 'text/markdown'
            elif structure == 'code':
                return 'text/plain'
            else:
                return 'text/plain'
        
        # Check for binary content
        if 'compressed_data' in patterns:
            return 'application/octet-stream'
        
        # Default to binary if no specific type detected
        return 'application/octet-stream'
    
    @staticmethod
    def _calculate_compression_potential(analysis_result: Dict[str, Any]) -> float:
        """
        Calculate compression potential based on analysis.
        
        Args:
            analysis_result: Analysis results
            
        Returns:
            float: Compression potential (0-1)
        """
        potential = 0.0
        
        # High redundancy indicates good compression potential
        redundancy = analysis_result.get('redundancy', 0.0)
        potential += redundancy * 0.4
        
        # Low entropy indicates good compression potential
        entropy = analysis_result.get('entropy', 0.0)
        entropy_factor = max(0, (8.0 - entropy) / 8.0)
        potential += entropy_factor * 0.3
        
        # Repeated patterns indicate good compression potential
        patterns = analysis_result.get('patterns', [])
        pattern_count = len([p for p in patterns if p.startswith('repeated_')])
        pattern_factor = min(1.0, pattern_count / 10.0)
        potential += pattern_factor * 0.2
        
        # Text content generally compresses well
        if 'text_content' in patterns:
            potential += 0.1
        
        # Already compressed data has low potential
        if 'compressed_data' in patterns:
            potential *= 0.1
        
        return min(1.0, max(0.0, potential))
    
    @staticmethod
    async def analyze_content_batch(content_list: List[bytes]) -> List[Dict[str, Any]]:
        """
        Analyze multiple content items in batch.
        
        Args:
            content_list: List of content data to analyze
            
        Returns:
            List[Dict[str, Any]]: List of analysis results
        """
        results = []
        
        for content_data in content_list:
            try:
                analysis = await ContentAnalysisService.analyze_content(content_data)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing content in batch: {e}")
                results.append({
                    'content_type': 'error',
                    'error': str(e),
                    'content_size': len(content_data) if content_data else 0
                })
        
        return results
    
    @staticmethod
    async def compare_content_analysis(analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two content analyses.
        
        Args:
            analysis1: First analysis result
            analysis2: Second analysis result
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        comparison = {
            'similarity_score': 0.0,
            'differences': [],
            'common_characteristics': []
        }
        
        try:
            # Compare content types
            if analysis1.get('content_type') == analysis2.get('content_type'):
                comparison['common_characteristics'].append('same_content_type')
                comparison['similarity_score'] += 0.2
            else:
                comparison['differences'].append('different_content_types')
            
            # Compare entropy
            entropy1 = analysis1.get('entropy', 0.0)
            entropy2 = analysis2.get('entropy', 0.0)
            entropy_diff = abs(entropy1 - entropy2)
            
            if entropy_diff < 0.5:
                comparison['common_characteristics'].append('similar_entropy')
                comparison['similarity_score'] += 0.2
            else:
                comparison['differences'].append(f'entropy_difference_{entropy_diff:.2f}')
            
            # Compare patterns
            patterns1 = set(analysis1.get('patterns', []))
            patterns2 = set(analysis2.get('patterns', []))
            
            common_patterns = patterns1.intersection(patterns2)
            if common_patterns:
                comparison['common_characteristics'].append(f'common_patterns_{len(common_patterns)}')
                comparison['similarity_score'] += 0.3 * (len(common_patterns) / max(len(patterns1), len(patterns2), 1))
            
            unique_patterns = patterns1.symmetric_difference(patterns2)
            if unique_patterns:
                comparison['differences'].append(f'unique_patterns_{len(unique_patterns)}')
            
            # Compare compression potential
            potential1 = analysis1.get('compression_potential', 0.0)
            potential2 = analysis2.get('compression_potential', 0.0)
            potential_diff = abs(potential1 - potential2)
            
            if potential_diff < 0.1:
                comparison['common_characteristics'].append('similar_compression_potential')
                comparison['similarity_score'] += 0.2
            else:
                comparison['differences'].append(f'compression_potential_difference_{potential_diff:.2f}')
            
            # Normalize similarity score
            comparison['similarity_score'] = min(1.0, comparison['similarity_score'])
            
        except Exception as e:
            logger.error(f"Error comparing content analyses: {e}")
            comparison['error'] = str(e)
        
        return comparison
