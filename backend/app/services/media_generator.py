"""
Synthetic Media Generation Service
Generates actual images and videos with various patterns for compression testing
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import io
import os
from pathlib import Path
from typing import Literal, Dict, Any, List
import logging
import hashlib

logger = logging.getLogger(__name__)

# Media storage paths
MEDIA_DIR = Path("/app/media")
VIDEOS_DIR = MEDIA_DIR / "videos"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"
THUMBNAILS_DIR = MEDIA_DIR / "thumbnails"

# Ensure directories exist
for directory in [VIDEOS_DIR, IMAGES_DIR, AUDIO_DIR, THUMBNAILS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class SyntheticMediaGenerator:
    """Generate synthetic media with various compression characteristics"""

    @staticmethod
    def generate_fractal_pattern(width: int, height: int, complexity: float, iterations: int = 100) -> np.ndarray:
        """Generate Mandelbrot fractal pattern"""
        try:
            x = np.linspace(-2.5, 1.5, width)
            y = np.linspace(-1.5, 1.5, height)
            X, Y = np.meshgrid(x, y)
            C = X + 1j * Y

            Z = np.zeros_like(C)
            M = np.zeros(C.shape)

            max_iter = int(iterations * complexity)

            for i in range(max_iter):
                mask = np.abs(Z) <= 2
                Z[mask] = Z[mask]**2 + C[mask]
                M[mask] = i

            # Normalize to 0-255
            M = (M / max_iter * 255).astype(np.uint8)
            return M
        except Exception as e:
            logger.error(f"Fractal generation error: {e}")
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)

    @staticmethod
    def generate_noise_pattern(width: int, height: int, noise_type: str = 'gaussian') -> np.ndarray:
        """Generate various noise patterns"""
        if noise_type == 'gaussian':
            return np.random.normal(128, 50, (height, width)).clip(0, 255).astype(np.uint8)
        elif noise_type == 'uniform':
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)
        elif noise_type == 'perlin':
            # Simplified Perlin-like noise
            scale = 10
            noise = np.zeros((height, width))
            for octave in range(4):
                freq = 2 ** octave
                amp = 1 / freq
                x = np.linspace(0, scale * freq, width)
                y = np.linspace(0, scale * freq, height)
                X, Y = np.meshgrid(x, y)
                noise += amp * np.sin(X) * np.cos(Y)
            return ((noise - noise.min()) / (noise.max() - noise.min()) * 255).astype(np.uint8)
        else:
            return np.random.randint(0, 256, (height, width), dtype=np.uint8)

    @staticmethod
    def generate_geometric_pattern(width: int, height: int, pattern_type: str = 'checkerboard') -> np.ndarray:
        """Generate geometric patterns"""
        img_array = np.zeros((height, width), dtype=np.uint8)

        if pattern_type == 'checkerboard':
            square_size = max(width, height) // 16
            for i in range(0, height, square_size):
                for j in range(0, width, square_size):
                    if ((i // square_size) + (j // square_size)) % 2 == 0:
                        img_array[i:i+square_size, j:j+square_size] = 255

        elif pattern_type == 'stripes':
            stripe_width = width // 20
            for i in range(0, width, stripe_width * 2):
                img_array[:, i:i+stripe_width] = 255

        elif pattern_type == 'circles':
            img = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(img)
            num_circles = 20
            for _ in range(num_circles):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                r = np.random.randint(10, min(width, height) // 4)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=255)
            img_array = np.array(img)

        elif pattern_type == 'gradient':
            img_array = np.linspace(0, 255, width, dtype=np.uint8)
            img_array = np.tile(img_array, (height, 1))

        return img_array

    @staticmethod
    def mix_patterns(patterns: List[np.ndarray], weights: List[float] = None) -> np.ndarray:
        """Mix multiple patterns with optional weights"""
        if not patterns:
            raise ValueError("No patterns provided")

        if weights is None:
            weights = [1.0 / len(patterns)] * len(patterns)

        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()

        result = np.zeros_like(patterns[0], dtype=np.float32)
        for pattern, weight in zip(patterns, weights):
            result += pattern.astype(np.float32) * weight

        return result.clip(0, 255).astype(np.uint8)

    @classmethod
    def generate_image(
        cls,
        width: int,
        height: int,
        structure_type: str,
        complexity: float,
        entropy: float,
        redundancy: float,
        format: str = 'png',
        color_space: str = 'rgb',
        pattern_params: Dict[str, Any] = None
    ) -> tuple[bytes, bytes, Dict[str, Any]]:
        """
        Generate a synthetic image with specified characteristics

        Returns: (image_data, thumbnail_data, metadata)
        """
        try:
            from app.services.advanced_media_generator import AdvancedPatternGenerator

            logger.info(f"Generating {width}x{height} {structure_type} image")

            pattern_params = pattern_params or {}

            # Generate base pattern based on structure type using advanced generators
            if structure_type == 'fractal':
                pattern = cls.generate_fractal_pattern(width, height, complexity)
            elif structure_type == 'mandelbrot':
                max_iter = int(pattern_params.get('max_iter', 100) * (1 + complexity))
                zoom = pattern_params.get('zoom', 1.0)
                pattern = AdvancedPatternGenerator.mandelbrot(width, height, max_iter, zoom)
            elif structure_type == 'julia':
                c_real = pattern_params.get('c_real', -0.7)
                c_imag = pattern_params.get('c_imag', 0.27)
                max_iter = int(pattern_params.get('max_iter', 100) * (1 + complexity))
                pattern = AdvancedPatternGenerator.julia_set(width, height, c_real, c_imag, max_iter)
            elif structure_type == 'burning_ship':
                max_iter = int(pattern_params.get('max_iter', 100) * (1 + complexity))
                pattern = AdvancedPatternGenerator.burning_ship(width, height, max_iter)
            elif structure_type == 'sierpinski':
                iterations = int(pattern_params.get('iterations', 8) * (1 + complexity))
                pattern = AdvancedPatternGenerator.sierpinski_triangle(width, height, iterations)
            elif structure_type == 'noise':
                pattern = cls.generate_noise_pattern(width, height, 'gaussian')
            elif structure_type == 'perlin':
                scale = pattern_params.get('scale', 10.0)
                octaves = int(pattern_params.get('octaves', 4) * (1 + complexity))
                pattern = AdvancedPatternGenerator.perlin_noise(width, height, scale, octaves)
            elif structure_type == 'worley':
                num_points = int(pattern_params.get('num_points', 20) * (1 + complexity))
                pattern = AdvancedPatternGenerator.worley_noise(width, height, num_points)
            elif structure_type == 'geometric':
                pattern = cls.generate_geometric_pattern(width, height, 'checkerboard')
            elif structure_type == 'checkerboard':
                square_size = pattern_params.get('square_size', max(width, height) // 16)
                pattern = AdvancedPatternGenerator.checkerboard(width, height, square_size)
            elif structure_type == 'stripes':
                stripe_width = pattern_params.get('stripe_width', width // 20)
                vertical = pattern_params.get('vertical', False)
                pattern = AdvancedPatternGenerator.stripes(width, height, stripe_width, vertical)
            elif structure_type == 'circles':
                num_circles = int(pattern_params.get('num_circles', 10) * (1 + complexity))
                pattern = AdvancedPatternGenerator.concentric_circles(width, height, num_circles)
            elif structure_type == 'spiral':
                num_turns = int(pattern_params.get('num_turns', 5) * (1 + complexity))
                pattern = AdvancedPatternGenerator.spiral(width, height, num_turns)
            elif structure_type == 'hexagonal':
                hex_size = pattern_params.get('hex_size', 30)
                pattern = AdvancedPatternGenerator.hexagonal_grid(width, height, hex_size)
            elif structure_type == 'wave_interference':
                num_sources = int(pattern_params.get('num_sources', 3) * (1 + complexity))
                wavelength = pattern_params.get('wavelength', 20.0)
                pattern = AdvancedPatternGenerator.wave_interference(width, height, num_sources, wavelength)
            elif structure_type == 'lissajous':
                a = pattern_params.get('a', 3)
                b = pattern_params.get('b', 5)
                delta = pattern_params.get('delta', np.pi/4)
                pattern = AdvancedPatternGenerator.lissajous(width, height, a, b, delta)
            elif structure_type == 'moire':
                line_spacing = pattern_params.get('line_spacing', 10)
                angle1 = pattern_params.get('angle1', 0)
                angle2 = pattern_params.get('angle2', np.pi/12)
                pattern = AdvancedPatternGenerator.moire_pattern(width, height, line_spacing, angle1, angle2)
            elif structure_type == 'gradient':
                gradient_type = pattern_params.get('gradient_type', 'linear')
                angle = pattern_params.get('angle', 0)
                pattern = AdvancedPatternGenerator.gradient(width, height, gradient_type, angle)
            elif structure_type == 'wood':
                ring_spacing = pattern_params.get('ring_spacing', 0.1)
                pattern = AdvancedPatternGenerator.wood_grain(width, height, ring_spacing)
            elif structure_type == 'marble':
                vein_scale = pattern_params.get('vein_scale', 10.0)
                pattern = AdvancedPatternGenerator.marble(width, height, vein_scale)
            elif structure_type == 'cellular':
                cell_size = pattern_params.get('cell_size', 20)
                pattern = AdvancedPatternGenerator.cellular(width, height, cell_size)
            elif structure_type == 'mixed':
                # Mix multiple patterns
                fractal = cls.generate_fractal_pattern(width, height, complexity)
                noise = cls.generate_noise_pattern(width, height, 'perlin')
                geometric = cls.generate_geometric_pattern(width, height, 'circles')
                pattern = cls.mix_patterns([fractal, noise, geometric], [0.5, 0.3, 0.2])
            else:
                # Default to mixed patterns
                fractal = cls.generate_fractal_pattern(width, height, complexity)
                noise = cls.generate_noise_pattern(width, height, 'gaussian')
                pattern = cls.mix_patterns([fractal, noise], [0.7, 0.3])

            # Add entropy variation
            if entropy > 0.5:
                noise_layer = cls.generate_noise_pattern(width, height, 'uniform')
                pattern = cls.mix_patterns([pattern, noise_layer], [1 - entropy * 0.5, entropy * 0.5])

            # Add redundancy (repeated patterns)
            if redundancy > 0.3:
                tile_size = max(32, int(min(width, height) * (1 - redundancy)))
                tile = pattern[:tile_size, :tile_size]
                pattern = np.tile(tile, (height // tile_size + 1, width // tile_size + 1))[:height, :width]

            # Convert to PIL Image
            if color_space == 'rgb':
                # Create RGB image with color variation based on pattern
                # Use different color channels to create colorful output
                r_channel = (pattern * (0.8 + complexity * 0.4)).clip(0, 255).astype(np.uint8)
                g_channel = (pattern * (0.9 + entropy * 0.3)).clip(0, 255).astype(np.uint8)
                b_channel = (pattern * (0.7 + redundancy * 0.5)).clip(0, 255).astype(np.uint8)

                # Stack channels to create RGB image
                img_array = np.stack([r_channel, g_channel, b_channel], axis=-1)
                img = Image.fromarray(img_array, mode='RGB')
            elif color_space == 'rgba':
                img = Image.fromarray(pattern, mode='L')
                img = img.convert('RGBA')
            elif color_space == 'grayscale':
                img = Image.fromarray(pattern, mode='L')
            else:
                img = Image.fromarray(pattern, mode='L').convert('RGB')

            # Apply filters based on complexity
            if complexity > 0.7:
                img = img.filter(ImageFilter.DETAIL)
            elif complexity < 0.3:
                img = img.filter(ImageFilter.SMOOTH)

            # Generate main image
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=format.upper())
            img_data = img_buffer.getvalue()

            # Generate thumbnail
            thumb = img.copy()
            thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
            thumb_buffer = io.BytesIO()
            thumb.save(thumb_buffer, format=format.upper())
            thumb_data = thumb_buffer.getvalue()

            # Calculate actual file size
            file_size = len(img_data)

            metadata = {
                "width": width,
                "height": height,
                "format": format,
                "fileSize": file_size,
                "colorSpace": color_space,
                "structure_type": structure_type,
                "actual_complexity": float(np.std(pattern) / 128),  # Normalized std dev
                "actual_entropy": float(-np.sum((pattern / 255) * np.log2((pattern / 255) + 1e-10)) / (width * height)),
            }

            logger.info(f"Generated image: {file_size} bytes")
            return img_data, thumb_data, metadata

        except Exception as e:
            logger.error(f"Image generation failed: {e}", exc_info=True)
            raise

    @classmethod
    def generate_video_frame(
        cls,
        width: int,
        height: int,
        frame_num: int,
        total_frames: int,
        layer_type: str,
        complexity: float,
        temporal_coherence: float
    ) -> np.ndarray:
        """Generate a single video frame"""
        t = frame_num / total_frames

        if layer_type == 'fractal':
            # Animated fractal with time-based zoom
            zoom = 1 + t * temporal_coherence
            pattern = cls.generate_fractal_pattern(
                int(width * zoom),
                int(height * zoom),
                complexity,
                iterations=50
            )
            # Center crop to original size
            start_h = (pattern.shape[0] - height) // 2
            start_w = (pattern.shape[1] - width) // 2
            pattern = pattern[start_h:start_h+height, start_w:start_w+width]

        elif layer_type == 'noise':
            # Animated noise
            pattern = cls.generate_noise_pattern(width, height, 'perlin')
            # Add time-based variation
            pattern = (pattern + frame_num * 5) % 256

        elif layer_type == 'geometric':
            # Rotating geometric patterns
            types = ['checkerboard', 'stripes', 'circles', 'gradient']
            pattern_type = types[frame_num % len(types)]
            pattern = cls.generate_geometric_pattern(width, height, pattern_type)

        else:
            # Mixed animated pattern
            fractal = cls.generate_fractal_pattern(width, height, complexity + t * 0.2)
            noise = cls.generate_noise_pattern(width, height, 'perlin')
            pattern = cls.mix_patterns([fractal, noise], [0.7, 0.3])

        return pattern

    @classmethod
    def generate_video(
        cls,
        width: int,
        height: int,
        duration: float,
        frame_rate: int,
        codec: str,
        layers: List[Dict[str, Any]],
        complexity: float,
        temporal_coherence: float
    ) -> tuple[bytes, bytes, Dict[str, Any]]:
        """
        Generate a synthetic video

        Returns: (video_data, thumbnail_data, metadata)
        """
        try:
            import imageio

            logger.info(f"Generating {width}x{height} video at {frame_rate}fps for {duration}s")

            total_frames = int(duration * frame_rate)
            frames = []

            for frame_num in range(total_frames):
                # Generate frames for each layer
                layer_frames = []
                for layer in layers:
                    layer_type = layer.get('type', 'fractal')
                    frame = cls.generate_video_frame(
                        width, height, frame_num, total_frames,
                        layer_type, complexity, temporal_coherence
                    )
                    layer_frames.append(frame)

                # Mix layers
                if len(layer_frames) > 1:
                    weights = [layer.get('opacity', 1.0) for layer in layers]
                    combined_frame = cls.mix_patterns(layer_frames, weights)
                else:
                    combined_frame = layer_frames[0]

                # Convert to RGB with color variation for visual interest
                r_channel = (combined_frame * (0.9 + complexity * 0.2)).clip(0, 255).astype(np.uint8)
                g_channel = (combined_frame * (0.8 + temporal_coherence * 0.3)).clip(0, 255).astype(np.uint8)
                b_channel = (combined_frame * (1.0 + frame_num / total_frames * 0.2)).clip(0, 255).astype(np.uint8)

                frame_rgb = np.stack([r_channel, g_channel, b_channel], axis=-1)
                frames.append(frame_rgb.astype(np.uint8))

            # Save video to buffer
            video_buffer = io.BytesIO()
            imageio.mimsave(
                video_buffer,
                frames,
                format='mp4',
                fps=frame_rate,
                codec='libx264',
                pixelformat='yuv420p',
                output_params=['-preset', 'ultrafast']
            )
            video_data = video_buffer.getvalue()

            # Generate thumbnail from middle frame
            mid_frame = frames[len(frames) // 2]
            thumb_img = Image.fromarray(mid_frame, mode='RGB')
            thumb_img.thumbnail((256, 144), Image.Resampling.LANCZOS)
            thumb_buffer = io.BytesIO()
            thumb_img.save(thumb_buffer, format='JPEG', quality=85)
            thumb_data = thumb_buffer.getvalue()

            file_size = len(video_data)

            metadata = {
                "width": width,
                "height": height,
                "duration": duration,
                "frameRate": frame_rate,
                "fileSize": file_size,
                "codec": codec,
                "totalFrames": total_frames
            }

            logger.info(f"Generated video: {file_size} bytes, {total_frames} frames")
            return video_data, thumb_data, metadata

        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            raise

    @staticmethod
    def save_media(data: bytes, filename: str, media_type: str) -> str:
        """Save media file and return the path"""
        if media_type == 'video':
            filepath = VIDEOS_DIR / filename
        elif media_type == 'image':
            filepath = IMAGES_DIR / filename
        elif media_type == 'audio':
            filepath = AUDIO_DIR / filename
        elif media_type == 'thumbnail':
            filepath = THUMBNAILS_DIR / filename
        else:
            raise ValueError(f"Unknown media type: {media_type}")

        with open(filepath, 'wb') as f:
            f.write(data)

        logger.info(f"Saved {media_type}: {filepath} ({len(data)} bytes)")
        return str(filepath)

    @classmethod
    def generate_and_save_image(cls, **kwargs) -> Dict[str, Any]:
        """Generate image and save to disk"""
        # Extract image_id before passing to generate_image
        image_id = kwargs.pop('image_id', None)

        image_data, thumb_data, metadata = cls.generate_image(**kwargs)

        # Create filename
        format_ext = kwargs.get('format', 'png')
        if image_id is None:
            image_id = hashlib.md5(image_data[:1024]).hexdigest()[:12]
        image_filename = f"{image_id}.{format_ext}"
        thumb_filename = f"{image_id}_thumb.{format_ext}"

        # Save files
        image_path = cls.save_media(image_data, image_filename, 'image')
        thumb_path = cls.save_media(thumb_data, thumb_filename, 'thumbnail')

        return {
            "image_url": f"/media/images/{image_filename}",
            "thumbnail_url": f"/media/thumbnails/{thumb_filename}",
            "metadata": metadata
        }

    @classmethod
    def generate_and_save_video(cls, **kwargs) -> Dict[str, Any]:
        """Generate video and save to disk"""
        # Extract video_id before passing to generate_video
        video_id = kwargs.pop('video_id', None)

        video_data, thumb_data, metadata = cls.generate_video(**kwargs)

        # Create filename
        if video_id is None:
            video_id = hashlib.md5(video_data[:1024]).hexdigest()[:12]
        video_filename = f"{video_id}.mp4"
        thumb_filename = f"{video_id}_thumb.jpg"

        # Save files
        video_path = cls.save_media(video_data, video_filename, 'video')
        thumb_path = cls.save_media(thumb_data, thumb_filename, 'thumbnail')

        return {
            "video_url": f"/media/videos/{video_filename}",
            "thumbnail_url": f"/media/thumbnails/{thumb_filename}",
            "metadata": metadata
        }
