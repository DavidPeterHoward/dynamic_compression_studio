"""
Intelligent Decompression System with Auto-Algorithm Detection.

This module provides advanced decompression capabilities with automatic
algorithm detection using multiple strategies:
1. Magic byte signature detection
2. Brute-force algorithm testing
3. Content validation through text analysis
4. Entropy-based verification
"""

import asyncio
import logging
import math
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

from .compression_engine import CompressionEngine
from ..models.compression import CompressionAlgorithm

logger = logging.getLogger(__name__)


@dataclass
class DecompressionResult:
    """Result of decompression attempt."""
    success: bool
    algorithm: Optional[CompressionAlgorithm]
    decompressed_data: Optional[bytes]
    confidence_score: float  # 0.0 to 1.0
    validation_metrics: Dict[str, Any]
    error_message: Optional[str] = None


class IntelligentDecompressor:
    """
    Intelligent decompression system with automatic algorithm detection.

    Features:
    - Magic byte signature detection
    - Brute-force algorithm testing
    - Text analysis and validation
    - Language detection
    - Structure validation (JSON, XML, etc.)
    - Entropy-based verification
    """

    # Magic byte signatures for common compression formats
    MAGIC_BYTES = {
        CompressionAlgorithm.GZIP: [b'\x1f\x8b'],
        CompressionAlgorithm.BZIP2: [b'BZ', b'BZh'],
        CompressionAlgorithm.LZMA: [b'\xfd7zXZ\x00', b'\x5d\x00\x00'],
        CompressionAlgorithm.ZSTD: [b'\x28\xb5\x2f\xfd'],
        # LZ4 doesn't have a standard magic byte
    }

    # Common words for English text validation
    COMMON_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what'
    }

    def __init__(self):
        """Initialize the intelligent decompressor."""
        self.compression_engine = CompressionEngine()
        logger.info("IntelligentDecompressor initialized")

    async def decompress_auto(self, compressed_data: bytes) -> DecompressionResult:
        """
        Automatically detect algorithm and decompress data.

        Args:
            compressed_data: Compressed data to decompress

        Returns:
            DecompressionResult with algorithm and decompressed data
        """
        try:
            # Step 1: Try magic byte detection
            detected_algorithm = self._detect_by_magic_bytes(compressed_data)
            if detected_algorithm:
                logger.info(f"Magic bytes detected algorithm: {detected_algorithm}")
                result = await self._try_decompress(compressed_data, detected_algorithm)
                if result.success:
                    return result

            # Step 2: Brute force all algorithms
            logger.info("Trying brute-force algorithm detection")
            return await self._brute_force_decompress(compressed_data)

        except Exception as e:
            logger.error(f"Auto-decompression failed: {e}")
            return DecompressionResult(
                success=False,
                algorithm=None,
                decompressed_data=None,
                confidence_score=0.0,
                validation_metrics={},
                error_message=f"Decompression failed: {str(e)}"
            )

    def _detect_by_magic_bytes(self, data: bytes) -> Optional[CompressionAlgorithm]:
        """
        Detect compression algorithm by magic bytes.

        Args:
            data: Compressed data

        Returns:
            Detected algorithm or None
        """
        for algorithm, signatures in self.MAGIC_BYTES.items():
            for signature in signatures:
                if data.startswith(signature):
                    return algorithm
        return None

    async def _brute_force_decompress(self, compressed_data: bytes) -> DecompressionResult:
        """
        Try all algorithms and return the best result.

        Args:
            compressed_data: Compressed data

        Returns:
            Best decompression result
        """
        algorithms_to_try = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZMA,
        ]

        results = []

        for algorithm in algorithms_to_try:
            result = await self._try_decompress(compressed_data, algorithm)
            if result.success:
                results.append(result)

        if not results:
            return DecompressionResult(
                success=False,
                algorithm=None,
                decompressed_data=None,
                confidence_score=0.0,
                validation_metrics={},
                error_message="No algorithm successfully decompressed the data"
            )

        # Return result with highest confidence
        best_result = max(results, key=lambda r: r.confidence_score)
        return best_result

    async def _try_decompress(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm
    ) -> DecompressionResult:
        """
        Try to decompress with specific algorithm and validate result.

        Args:
            compressed_data: Compressed data
            algorithm: Algorithm to try

        Returns:
            DecompressionResult
        """
        try:
            # Attempt decompression
            decompressed_data = await self.compression_engine.decompress(
                compressed_data,
                algorithm
            )

            # Validate the decompressed data
            validation_metrics = self._validate_decompressed_data(decompressed_data)
            confidence_score = self._calculate_confidence_score(validation_metrics)

            return DecompressionResult(
                success=True,
                algorithm=algorithm,
                decompressed_data=decompressed_data,
                confidence_score=confidence_score,
                validation_metrics=validation_metrics
            )

        except Exception as e:
            logger.debug(f"Decompression with {algorithm} failed: {e}")
            return DecompressionResult(
                success=False,
                algorithm=algorithm,
                decompressed_data=None,
                confidence_score=0.0,
                validation_metrics={},
                error_message=str(e)
            )

    def _validate_decompressed_data(self, data: bytes) -> Dict[str, Any]:
        """
        Validate decompressed data quality.

        Args:
            data: Decompressed data

        Returns:
            Validation metrics
        """
        metrics = {}

        try:
            # Try to decode as text
            try:
                text = data.decode('utf-8')
                metrics['is_valid_utf8'] = True
                metrics['text_length'] = len(text)

                # Text analysis
                metrics.update(self._analyze_text(text))
            except UnicodeDecodeError:
                metrics['is_valid_utf8'] = False
                metrics['text_length'] = 0

            # Binary analysis
            metrics['data_size'] = len(data)
            metrics['entropy'] = self._calculate_entropy(data)
            metrics['null_byte_ratio'] = data.count(b'\x00') / len(data) if len(data) > 0 else 0

            # Structure detection
            metrics['detected_structure'] = self._detect_structure(data)

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            metrics['validation_error'] = str(e)

        return metrics

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for validation.

        Args:
            text: Text to analyze

        Returns:
            Text analysis metrics
        """
        metrics = {}

        # Word analysis
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if words:
            metrics['word_count'] = len(words)
            metrics['unique_words'] = len(set(words))

            # Check for common English words
            common_word_count = sum(1 for word in words if word in self.COMMON_WORDS)
            metrics['common_word_ratio'] = common_word_count / len(words) if words else 0
        else:
            metrics['word_count'] = 0
            metrics['unique_words'] = 0
            metrics['common_word_ratio'] = 0

        # Printable character ratio
        printable_count = sum(1 for char in text if char.isprintable())
        metrics['printable_ratio'] = printable_count / len(text) if text else 0

        # Line analysis
        lines = text.split('\n')
        metrics['line_count'] = len(lines)
        metrics['avg_line_length'] = sum(len(line) for line in lines) / len(lines) if lines else 0

        return metrics

    def _calculate_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy of data.

        Args:
            data: Data to analyze

        Returns:
            Entropy value (0-8 bits per byte)
        """
        if not data:
            return 0.0

        # Count byte frequencies
        byte_counts = Counter(data)
        total_bytes = len(data)

        # Calculate entropy
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / total_bytes
            entropy -= probability * math.log2(probability)

        return entropy

    def _detect_structure(self, data: bytes) -> Optional[str]:
        """
        Detect structured data formats.

        Args:
            data: Data to analyze

        Returns:
            Detected structure type or None
        """
        try:
            text = data.decode('utf-8')

            # JSON detection
            if text.strip().startswith(('{', '[')):
                try:
                    import json
                    json.loads(text)
                    return 'json'
                except:
                    pass

            # XML detection
            if text.strip().startswith('<?xml') or text.strip().startswith('<'):
                return 'xml'

            # CSV detection
            if ',' in text and '\n' in text:
                lines = text.strip().split('\n')
                if len(lines) > 1:
                    first_line_commas = lines[0].count(',')
                    if all(line.count(',') == first_line_commas for line in lines[:5]):
                        return 'csv'

            # Log file detection
            if any(pattern in text for pattern in ['ERROR', 'WARNING', 'INFO', 'DEBUG']):
                return 'log'

            # Code detection
            if any(keyword in text for keyword in ['function', 'class', 'def ', 'import ', 'const ', 'var ']):
                return 'code'

        except:
            pass

        return 'binary'

    def _calculate_confidence_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate confidence score for decompression result.

        Args:
            metrics: Validation metrics

        Returns:
            Confidence score (0.0 to 1.0)
        """
        score = 0.0

        # Valid UTF-8 is a good sign
        if metrics.get('is_valid_utf8', False):
            score += 0.3

            # High common word ratio indicates readable text
            common_word_ratio = metrics.get('common_word_ratio', 0)
            score += common_word_ratio * 0.3

            # High printable ratio is good
            printable_ratio = metrics.get('printable_ratio', 0)
            score += printable_ratio * 0.2

        # Detected structure is good
        if metrics.get('detected_structure') != 'binary':
            score += 0.2

        # Reasonable entropy (not too high, not too low)
        entropy = metrics.get('entropy', 8.0)
        if 1.0 <= entropy <= 6.0:
            score += 0.1

        # Low null byte ratio for text
        null_byte_ratio = metrics.get('null_byte_ratio', 0)
        if null_byte_ratio < 0.1:
            score += 0.1

        return min(score, 1.0)
