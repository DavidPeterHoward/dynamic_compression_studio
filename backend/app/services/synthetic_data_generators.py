"""
Synthetic Data Generators for All Content Types

Generates synthetic test data for text, data, video, audio, and image
content types with controlled characteristics for compression testing.
"""

import io
import json
import random
import string
import struct
import wave
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import logging

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image generation will be limited")

logger = logging.getLogger(__name__)


class SyntheticTextGenerator:
    """Generate synthetic text content with controlled characteristics."""
    
    @staticmethod
    def generate_repetitive_text(size_kb: int = 10, repetition_factor: float = 0.8) -> bytes:
        """
        Generate highly repetitive text (good compression potential).
        
        Args:
            size_kb: Target size in kilobytes
            repetition_factor: 0.0-1.0, higher = more repetitive
        
        Returns:
            Generated text as bytes
        """
        base_phrases = [
            "The quick brown fox jumps over the lazy dog. ",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
            "Compression algorithms work by finding patterns in data. ",
            "Machine learning can optimize compression parameters. "
        ]
        
        target_size = size_kb * 1024
        content = []
        current_size = 0
        
        # Generate repetitive content
        while current_size < target_size:
            if random.random() < repetition_factor:
                # Repeat phrases
                phrase = random.choice(base_phrases)
                repeats = random.randint(2, 10)
                content.append(phrase * repeats)
            else:
                # Add some variation
                phrase = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=50))
                content.append(phrase + ". ")
            
            current_size = len(''.join(content).encode('utf-8'))
        
        return ''.join(content)[:target_size].encode('utf-8')
    
    @staticmethod
    def generate_random_text(size_kb: int = 10) -> bytes:
        """
        Generate random text (poor compression potential).
        
        Args:
            size_kb: Target size in kilobytes
        
        Returns:
            Generated text as bytes
        """
        target_size = size_kb * 1024
        chars = string.ascii_letters + string.digits + string.punctuation + ' \n'
        return ''.join(random.choices(chars, k=target_size)).encode('utf-8')
    
    @staticmethod
    def generate_structured_text(size_kb: int = 10, format_type: str = 'json') -> bytes:
        """
        Generate structured text (JSON, XML, CSV).
        
        Args:
            size_kb: Target size in kilobytes
            format_type: 'json', 'xml', or 'csv'
        
        Returns:
            Generated structured data as bytes
        """
        target_size = size_kb * 1024
        
        if format_type == 'json':
            data = []
            while len(json.dumps(data).encode('utf-8')) < target_size:
                data.append({
                    'id': len(data) + 1,
                    'timestamp': datetime.utcnow().isoformat(),
                    'value': random.uniform(0, 100),
                    'status': random.choice(['active', 'inactive', 'pending']),
                    'data': ''.join(random.choices(string.ascii_letters, k=50))
                })
            return json.dumps(data, indent=2).encode('utf-8')[:target_size]
        
        elif format_type == 'xml':
            lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<root>']
            while len('\n'.join(lines).encode('utf-8')) < target_size:
                lines.append(f'  <item id="{len(lines)-1}">')
                lines.append(f'    <value>{random.uniform(0, 100):.2f}</value>')
                lines.append(f'    <status>{random.choice(["active", "inactive"])}</status>')
                lines.append('  </item>')
            lines.append('</root>')
            return '\n'.join(lines).encode('utf-8')[:target_size]
        
        else:  # CSV
            lines = ['id,timestamp,value,status']
            while len('\n'.join(lines).encode('utf-8')) < target_size:
                lines.append(f'{len(lines)},{datetime.utcnow().isoformat()},{random.uniform(0, 100):.2f},{random.choice(["active", "inactive"])}')
            return '\n'.join(lines).encode('utf-8')[:target_size]
    
    @staticmethod
    def generate_log_data(size_kb: int = 10, log_level_distribution: Optional[Dict[str, float]] = None) -> bytes:
        """
        Generate synthetic log data.
        
        Args:
            size_kb: Target size in kilobytes
            log_level_distribution: Distribution of log levels (e.g., {'INFO': 0.7, 'ERROR': 0.2, 'DEBUG': 0.1})
        
        Returns:
            Generated log data as bytes
        """
        if log_level_distribution is None:
            log_level_distribution = {'INFO': 0.6, 'WARN': 0.2, 'ERROR': 0.15, 'DEBUG': 0.05}
        
        levels = list(log_level_distribution.keys())
        weights = list(log_level_distribution.values())
        
        messages = [
            "Request processed successfully",
            "Database connection established",
            "Cache hit for key",
            "Authentication successful",
            "File upload completed",
            "Connection timeout",
            "Invalid parameter provided",
            "Resource not found",
            "Permission denied"
        ]
        
        target_size = size_kb * 1024
        lines = []
        current_size = 0
        
        while current_size < target_size:
            timestamp = datetime.utcnow().isoformat()
            level = random.choices(levels, weights=weights)[0]
            message = random.choice(messages)
            line = f"[{timestamp}] {level:5} - {message} (duration: {random.randint(1, 1000)}ms)\n"
            lines.append(line)
            current_size = len(''.join(lines).encode('utf-8'))
        
        return ''.join(lines).encode('utf-8')[:target_size]


class SyntheticAudioGenerator:
    """Generate synthetic audio content for testing."""
    
    @staticmethod
    def generate_silence(duration_seconds: float = 1.0, sample_rate: int = 44100, channels: int = 2) -> bytes:
        """
        Generate silence (highly compressible).
        
        Args:
            duration_seconds: Duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
        
        Returns:
            WAV audio data as bytes
        """
        num_samples = int(duration_seconds * sample_rate)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            
            # Write silence
            for _ in range(num_samples):
                for _ in range(channels):
                    wav.writeframes(struct.pack('<h', 0))
        
        return buffer.getvalue()
    
    @staticmethod
    def generate_tone(frequency: float = 440.0, duration_seconds: float = 1.0,
                     sample_rate: int = 44100, channels: int = 2) -> bytes:
        """
        Generate pure tone (moderately compressible).
        
        Args:
            frequency: Frequency in Hz
            duration_seconds: Duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
        
        Returns:
            WAV audio data as bytes
        """
        import math
        num_samples = int(duration_seconds * sample_rate)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            for i in range(num_samples):
                sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                for _ in range(channels):
                    wav.writeframes(struct.pack('<h', sample))
        
        return buffer.getvalue()
    
    @staticmethod
    def generate_white_noise(duration_seconds: float = 1.0, sample_rate: int = 44100,
                            channels: int = 2) -> bytes:
        """
        Generate white noise (poorly compressible).
        
        Args:
            duration_seconds: Duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
        
        Returns:
            WAV audio data as bytes
        """
        num_samples = int(duration_seconds * sample_rate)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            for _ in range(num_samples):
                sample = random.randint(-32768, 32767)
                for _ in range(channels):
                    wav.writeframes(struct.pack('<h', sample))
        
        return buffer.getvalue()


class SyntheticImageGenerator:
    """Generate synthetic image content for testing."""
    
    @staticmethod
    def generate_solid_color(width: int = 800, height: int = 600, color: Tuple[int, int, int] = (128, 128, 128)) -> bytes:
        """
        Generate solid color image (highly compressible).
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            color: RGB color tuple
        
        Returns:
            PNG image data as bytes
        """
        if not PIL_AVAILABLE:
            # Generate simple bitmap header without PIL
            return SyntheticImageGenerator._generate_simple_bitmap(width, height, color)
        
        img = Image.new('RGB', (width, height), color)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def generate_gradient(width: int = 800, height: int = 600) -> bytes:
        """
        Generate gradient image (moderately compressible).
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
        
        Returns:
            PNG image data as bytes
        """
        if not PIL_AVAILABLE:
            return SyntheticImageGenerator._generate_simple_bitmap(width, height, (128, 128, 128))
        
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        for y in range(height):
            color_value = int(255 * y / height)
            draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def generate_noise(width: int = 800, height: int = 600) -> bytes:
        """
        Generate noise image (poorly compressible).
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
        
        Returns:
            PNG image data as bytes
        """
        if not PIL_AVAILABLE:
            return SyntheticImageGenerator._generate_simple_bitmap(width, height, (128, 128, 128))
        
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def generate_pattern(width: int = 800, height: int = 600, pattern_type: str = 'checkerboard') -> bytes:
        """
        Generate patterned image.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            pattern_type: 'checkerboard', 'stripes', or 'grid'
        
        Returns:
            PNG image data as bytes
        """
        if not PIL_AVAILABLE:
            return SyntheticImageGenerator._generate_simple_bitmap(width, height, (128, 128, 128))
        
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        if pattern_type == 'checkerboard':
            square_size = 50
            for y in range(0, height, square_size):
                for x in range(0, width, square_size):
                    if (x // square_size + y // square_size) % 2 == 0:
                        draw.rectangle([x, y, x + square_size, y + square_size], fill=(0, 0, 0))
        
        elif pattern_type == 'stripes':
            stripe_width = 50
            for x in range(0, width, stripe_width * 2):
                draw.rectangle([x, 0, x + stripe_width, height], fill=(0, 0, 0))
        
        elif pattern_type == 'grid':
            grid_size = 50
            for x in range(0, width, grid_size):
                draw.line([(x, 0), (x, height)], fill=(0, 0, 0), width=2)
            for y in range(0, height, grid_size):
                draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=2)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @staticmethod
    def _generate_simple_bitmap(width: int, height: int, color: Tuple[int, int, int]) -> bytes:
        """Generate simple BMP without PIL (fallback)."""
        # BMP header
        file_size = 54 + (width * height * 3)
        header = bytearray(54)
        header[0:2] = b'BM'
        header[2:6] = struct.pack('<I', file_size)
        header[10:14] = struct.pack('<I', 54)
        header[14:18] = struct.pack('<I', 40)
        header[18:22] = struct.pack('<i', width)
        header[22:26] = struct.pack('<i', height)
        header[26:28] = struct.pack('<H', 1)
        header[28:30] = struct.pack('<H', 24)
        
        # Pixel data
        pixels = bytearray()
        for _ in range(height):
            for _ in range(width):
                pixels.extend([color[2], color[1], color[0]])  # BGR format
            # Padding
            while len(pixels) % 4 != 0:
                pixels.append(0)
        
        return bytes(header + pixels)


class SyntheticVideoGenerator:
    """Generate synthetic video metadata (actual video generation would be too large)."""
    
    @staticmethod
    def generate_video_metadata(duration_seconds: float = 10.0, resolution: str = "1920x1080",
                               fps: int = 30, codec: str = "h264") -> Dict[str, Any]:
        """
        Generate video metadata for testing.
        
        Args:
            duration_seconds: Video duration in seconds
            resolution: Resolution string (e.g., "1920x1080")
            fps: Frames per second
            codec: Video codec
        
        Returns:
            Video metadata dictionary
        """
        width, height = map(int, resolution.split('x'))
        total_frames = int(duration_seconds * fps)
        
        # Estimate sizes
        bits_per_pixel = 12  # Typical for H.264
        uncompressed_size = width * height * total_frames * 3  # RGB
        compressed_size = int(width * height * total_frames * bits_per_pixel / 8)
        
        return {
            'duration_seconds': duration_seconds,
            'resolution': resolution,
            'width': width,
            'height': height,
            'fps': fps,
            'total_frames': total_frames,
            'codec': codec,
            'bitrate': int((compressed_size * 8) / duration_seconds),
            'uncompressed_size': uncompressed_size,
            'estimated_compressed_size': compressed_size,
            'color_space': 'yuv420p',
            'format': 'mp4'
        }


class SyntheticDataGenerator:
    """Main generator coordinating all content types."""
    
    def __init__(self):
        self.text_gen = SyntheticTextGenerator()
        self.audio_gen = SyntheticAudioGenerator()
        self.image_gen = SyntheticImageGenerator()
        self.video_gen = SyntheticVideoGenerator()
    
    def generate_test_suite(self, content_types: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Generate comprehensive test suite across all content types.
        
        Args:
            content_types: List of content types to generate (or None for all)
        
        Returns:
            Dictionary mapping test names to test data
        """
        if content_types is None:
            content_types = ['text', 'audio', 'image']
        
        test_suite = {}
        
        if 'text' in content_types:
            test_suite.update({
                'text_repetitive_1kb': {
                    'content': self.text_gen.generate_repetitive_text(1, 0.9),
                    'category': 'text',
                    'type': 'plain_text',
                    'characteristics': 'highly_repetitive'
                },
                'text_random_1kb': {
                    'content': self.text_gen.generate_random_text(1),
                    'category': 'text',
                    'type': 'plain_text',
                    'characteristics': 'random'
                },
                'text_json_1kb': {
                    'content': self.text_gen.generate_structured_text(1, 'json'),
                    'category': 'data',
                    'type': 'json',
                    'characteristics': 'structured'
                },
                'text_log_1kb': {
                    'content': self.text_gen.generate_log_data(1),
                    'category': 'text',
                    'type': 'log',
                    'characteristics': 'log_format'
                }
            })
        
        if 'audio' in content_types:
            test_suite.update({
                'audio_silence': {
                    'content': self.audio_gen.generate_silence(0.5),
                    'category': 'audio',
                    'type': 'wav',
                    'characteristics': 'silence'
                },
                'audio_tone': {
                    'content': self.audio_gen.generate_tone(440, 0.5),
                    'category': 'audio',
                    'type': 'wav',
                    'characteristics': 'pure_tone'
                },
                'audio_noise': {
                    'content': self.audio_gen.generate_white_noise(0.5),
                    'category': 'audio',
                    'type': 'wav',
                    'characteristics': 'white_noise'
                }
            })
        
        if 'image' in content_types and PIL_AVAILABLE:
            test_suite.update({
                'image_solid': {
                    'content': self.image_gen.generate_solid_color(400, 300),
                    'category': 'image',
                    'type': 'png',
                    'characteristics': 'solid_color'
                },
                'image_gradient': {
                    'content': self.image_gen.generate_gradient(400, 300),
                    'category': 'image',
                    'type': 'png',
                    'characteristics': 'gradient'
                },
                'image_noise': {
                    'content': self.image_gen.generate_noise(400, 300),
                    'category': 'image',
                    'type': 'png',
                    'characteristics': 'noise'
                },
                'image_checkerboard': {
                    'content': self.image_gen.generate_pattern(400, 300, 'checkerboard'),
                    'category': 'image',
                    'type': 'png',
                    'characteristics': 'pattern'
                }
            })
        
        return test_suite
    
    def compute_content_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()
    
    def analyze_content_characteristics(self, content: bytes) -> Dict[str, float]:
        """
        Analyze content to determine compression characteristics.
        
        Returns:
            Dictionary with entropy, redundancy, and complexity scores
        """
        if len(content) == 0:
            return {'entropy': 0.0, 'redundancy': 0.0, 'pattern_complexity': 0.0}
        
        # Calculate byte frequency
        byte_counts = {}
        for byte in content:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # Calculate entropy
        total_bytes = len(content)
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / total_bytes
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)
        
        # Normalize entropy to 0-1 range
        max_entropy = 8.0  # Maximum entropy for bytes
        normalized_entropy = entropy / max_entropy
        
        # Estimate redundancy (inverse of entropy)
        redundancy = 1.0 - normalized_entropy
        
        # Estimate pattern complexity (simple heuristic)
        unique_bytes = len(byte_counts)
        pattern_complexity = unique_bytes / 256.0
        
        return {
            'entropy': round(normalized_entropy, 4),
            'redundancy': round(redundancy, 4),
            'pattern_complexity': round(pattern_complexity, 4)
        }

