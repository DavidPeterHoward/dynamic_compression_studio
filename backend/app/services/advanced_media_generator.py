"""
Advanced Multi-Dimensional Synthetic Media Generator
Supports extensive variety of generation techniques for comprehensive compression testing
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
from pathlib import Path
from typing import Literal, Dict, Any, List, Tuple, Optional
import logging
import hashlib
import math

logger = logging.getLogger(__name__)

# Media storage paths
MEDIA_DIR = Path("/app/media")
VIDEOS_DIR = MEDIA_DIR / "videos"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"
THUMBNAILS_DIR = MEDIA_DIR / "thumbnails"


class AdvancedPatternGenerator:
    """Advanced pattern generation with multi-dimensional parameters"""

    # ========================================================================
    # FRACTAL PATTERNS (Multiple Types)
    # ========================================================================

    @staticmethod
    def mandelbrot(width: int, height: int, max_iter: int = 100, zoom: float = 1.0,
                   offset_x: float = 0, offset_y: float = 0) -> np.ndarray:
        """Classic Mandelbrot set"""
        x_min, x_max = -2.5/zoom + offset_x, 1.5/zoom + offset_x
        y_min, y_max = -1.5/zoom + offset_y, 1.5/zoom + offset_y

        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        Z = np.zeros_like(C)
        M = np.zeros(C.shape)

        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            M[mask] = i

        return (M / max_iter * 255).astype(np.uint8)

    @staticmethod
    def julia_set(width: int, height: int, c_real: float = -0.7, c_imag: float = 0.27,
                  max_iter: int = 100) -> np.ndarray:
        """Julia set fractal"""
        x = np.linspace(-1.5, 1.5, width)
        y = np.linspace(-1.5, 1.5, height)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        C = complex(c_real, c_imag)

        M = np.zeros(Z.shape)
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C
            M[mask] = i

        return (M / max_iter * 255).astype(np.uint8)

    @staticmethod
    def burning_ship(width: int, height: int, max_iter: int = 100) -> np.ndarray:
        """Burning Ship fractal"""
        x = np.linspace(-2, 1, width)
        y = np.linspace(-2, 1, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        Z = np.zeros_like(C)
        M = np.zeros(C.shape)

        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            # Key difference: use absolute values before squaring
            Z[mask] = (np.abs(np.real(Z[mask])) + 1j * np.abs(np.imag(Z[mask])))**2 + C[mask]
            M[mask] = i

        return (M / max_iter * 255).astype(np.uint8)

    @staticmethod
    def sierpinski_triangle(width: int, height: int, iterations: int = 8) -> np.ndarray:
        """Sierpinski triangle fractal"""
        img = np.zeros((height, width), dtype=np.uint8)

        # Start with a triangle
        points = [(width//2, 10), (10, height-10), (width-10, height-10)]

        # Current point
        x, y = width//2, height//2

        for _ in range(iterations * 10000):
            # Pick random vertex
            target = points[np.random.randint(0, 3)]
            # Move halfway to it
            x = (x + target[0]) // 2
            y = (y + target[1]) // 2
            if 0 <= x < width and 0 <= y < height:
                img[y, x] = 255

        return img

    # ========================================================================
    # NOISE PATTERNS (Multiple Types)
    # ========================================================================

    @staticmethod
    def gaussian_noise(width: int, height: int, mean: float = 128, std: float = 50) -> np.ndarray:
        """Gaussian/normal distribution noise"""
        return np.random.normal(mean, std, (height, width)).clip(0, 255).astype(np.uint8)

    @staticmethod
    def uniform_noise(width: int, height: int) -> np.ndarray:
        """Uniform random noise"""
        return np.random.randint(0, 256, (height, width), dtype=np.uint8)

    @staticmethod
    def salt_pepper_noise(width: int, height: int, salt_prob: float = 0.05,
                          pepper_prob: float = 0.05) -> np.ndarray:
        """Salt and pepper noise"""
        img = np.ones((height, width), dtype=np.uint8) * 128
        # Salt (white pixels)
        salt_mask = np.random.random((height, width)) < salt_prob
        img[salt_mask] = 255
        # Pepper (black pixels)
        pepper_mask = np.random.random((height, width)) < pepper_prob
        img[pepper_mask] = 0
        return img

    @staticmethod
    def perlin_noise(width: int, height: int, scale: float = 10.0, octaves: int = 4) -> np.ndarray:
        """Multi-octave Perlin-like noise"""
        noise = np.zeros((height, width))

        for octave in range(octaves):
            freq = 2 ** octave
            amp = 1 / freq

            x = np.linspace(0, scale * freq, width)
            y = np.linspace(0, scale * freq, height)
            X, Y = np.meshgrid(x, y)

            # Simple noise using sine waves
            noise += amp * (np.sin(X) * np.cos(Y) + np.sin(X + Y) * 0.5)

        # Normalize
        noise = (noise - noise.min()) / (noise.max() - noise.min()) * 255
        return noise.astype(np.uint8)

    @staticmethod
    def worley_noise(width: int, height: int, num_points: int = 20) -> np.ndarray:
        """Worley/Voronoi noise (cellular pattern)"""
        # Generate random points
        points = np.random.rand(num_points, 2)
        points[:, 0] *= width
        points[:, 1] *= height

        img = np.zeros((height, width), dtype=np.uint8)

        for y in range(height):
            for x in range(width):
                # Find distance to nearest point
                distances = np.sqrt((points[:, 0] - x)**2 + (points[:, 1] - y)**2)
                min_dist = np.min(distances)
                img[y, x] = int(min_dist / np.sqrt(width**2 + height**2) * 255)

        return img

    # ========================================================================
    # GEOMETRIC PATTERNS (Many Variations)
    # ========================================================================

    @staticmethod
    def checkerboard(width: int, height: int, square_size: int = 32) -> np.ndarray:
        """Checkerboard pattern"""
        img = np.zeros((height, width), dtype=np.uint8)
        for i in range(0, height, square_size):
            for j in range(0, width, square_size):
                if ((i // square_size) + (j // square_size)) % 2 == 0:
                    img[i:i+square_size, j:j+square_size] = 255
        return img

    @staticmethod
    def stripes(width: int, height: int, stripe_width: int = 20,
                vertical: bool = True) -> np.ndarray:
        """Striped pattern"""
        img = np.zeros((height, width), dtype=np.uint8)
        if vertical:
            for i in range(0, width, stripe_width * 2):
                img[:, i:i+stripe_width] = 255
        else:
            for i in range(0, height, stripe_width * 2):
                img[i:i+stripe_width, :] = 255
        return img

    @staticmethod
    def concentric_circles(width: int, height: int, num_circles: int = 10) -> np.ndarray:
        """Concentric circles from center"""
        img = np.zeros((height, width), dtype=np.uint8)
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2

        for y in range(height):
            for x in range(width):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                circle_index = int(dist / max_radius * num_circles)
                if circle_index % 2 == 0:
                    img[y, x] = 255
        return img

    @staticmethod
    def spiral(width: int, height: int, num_turns: int = 5) -> np.ndarray:
        """Logarithmic spiral"""
        img = np.zeros((height, width), dtype=np.uint8)
        center_x, center_y = width // 2, height // 2

        for y in range(height):
            for x in range(width):
                dx, dy = x - center_x, y - center_y
                angle = np.arctan2(dy, dx)
                radius = np.sqrt(dx**2 + dy**2)

                # Logarithmic spiral equation
                if radius > 0:
                    spiral_val = np.log(radius + 1) + angle / (2 * np.pi) * num_turns
                    if int(spiral_val) % 2 == 0:
                        img[y, x] = 255
        return img

    @staticmethod
    def hexagonal_grid(width: int, height: int, hex_size: int = 30) -> np.ndarray:
        """Hexagonal grid pattern"""
        img = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(img)

        hex_width = hex_size * np.sqrt(3)
        hex_height = hex_size * 2

        for row in range(-1, int(height / hex_height) + 2):
            for col in range(-1, int(width / hex_width) + 2):
                x = col * hex_width
                if row % 2 == 1:
                    x += hex_width / 2
                y = row * hex_height * 0.75

                # Draw hexagon
                points = []
                for i in range(6):
                    angle = i * np.pi / 3
                    px = x + hex_size * np.cos(angle)
                    py = y + hex_size * np.sin(angle)
                    points.append((px, py))

                draw.polygon(points, outline=255)

        return np.array(img)

    @staticmethod
    def wave_interference(width: int, height: int, num_sources: int = 3,
                          wavelength: float = 20.0) -> np.ndarray:
        """Wave interference pattern"""
        # Random wave sources
        sources = np.random.rand(num_sources, 2)
        sources[:, 0] *= width
        sources[:, 1] *= height

        img = np.zeros((height, width), dtype=np.float32)

        for y in range(height):
            for x in range(width):
                wave_sum = 0
                for source in sources:
                    dist = np.sqrt((x - source[0])**2 + (y - source[1])**2)
                    wave_sum += np.sin(2 * np.pi * dist / wavelength)
                img[y, x] = wave_sum

        # Normalize
        img = (img - img.min()) / (img.max() - img.min()) * 255
        return img.astype(np.uint8)

    # ========================================================================
    # ADVANCED PATTERNS
    # ========================================================================

    @staticmethod
    def lissajous(width: int, height: int, a: float = 3, b: float = 2,
                  delta: float = np.pi/2) -> np.ndarray:
        """Lissajous curve"""
        img = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(img)

        points = []
        for t in np.linspace(0, 2*np.pi, 1000):
            x = int(width/2 + width/3 * np.sin(a * t + delta))
            y = int(height/2 + height/3 * np.sin(b * t))
            points.append((x, y))

        draw.line(points, fill=255, width=2)
        return np.array(img)

    @staticmethod
    def moire_pattern(width: int, height: int, line_spacing: int = 10,
                      angle1: float = 0, angle2: float = np.pi/12) -> np.ndarray:
        """Moiré pattern from overlapping grids"""
        img1 = np.zeros((height, width), dtype=np.uint8)
        img2 = np.zeros((height, width), dtype=np.uint8)

        # First set of lines
        for i in range(0, max(width, height), line_spacing):
            x1 = int(i * np.cos(angle1))
            y1 = int(i * np.sin(angle1))
            x2 = int(i * np.cos(angle1) + height * np.sin(angle1 + np.pi/2))
            y2 = int(i * np.sin(angle1) + height * np.cos(angle1 + np.pi/2))

            img_temp = Image.fromarray(img1)
            draw = ImageDraw.Draw(img_temp)
            draw.line([(x1, y1), (x2, y2)], fill=255, width=2)
            img1 = np.array(img_temp)

        # Second set of lines
        for i in range(0, max(width, height), line_spacing):
            x1 = int(i * np.cos(angle2))
            y1 = int(i * np.sin(angle2))
            x2 = int(i * np.cos(angle2) + height * np.sin(angle2 + np.pi/2))
            y2 = int(i * np.sin(angle2) + height * np.cos(angle2 + np.pi/2))

            img_temp = Image.fromarray(img2)
            draw = ImageDraw.Draw(img_temp)
            draw.line([(x1, y1), (x2, y2)], fill=255, width=2)
            img2 = np.array(img_temp)

        # Combine with AND
        return ((img1 > 0) & (img2 > 0)).astype(np.uint8) * 255

    @staticmethod
    def gradient(width: int, height: int, gradient_type: str = 'linear',
                 angle: float = 0) -> np.ndarray:
        """Various gradient types"""
        if gradient_type == 'linear':
            if angle == 0:  # Horizontal
                gradient = np.linspace(0, 255, width, dtype=np.uint8)
                return np.tile(gradient, (height, 1))
            else:  # Rotated
                x = np.arange(width)
                y = np.arange(height)
                X, Y = np.meshgrid(x, y)
                rotated = X * np.cos(angle) + Y * np.sin(angle)
                rotated = (rotated - rotated.min()) / (rotated.max() - rotated.min()) * 255
                return rotated.astype(np.uint8)

        elif gradient_type == 'radial':
            center_x, center_y = width // 2, height // 2
            max_dist = np.sqrt(center_x**2 + center_y**2)

            y, x = np.ogrid[:height, :width]
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            gradient = (dist / max_dist * 255).clip(0, 255).astype(np.uint8)
            return gradient

        elif gradient_type == 'angular':
            center_x, center_y = width // 2, height // 2
            y, x = np.ogrid[:height, :width]
            angle_map = np.arctan2(y - center_y, x - center_x)
            gradient = ((angle_map + np.pi) / (2 * np.pi) * 255).astype(np.uint8)
            return gradient

        return np.zeros((height, width), dtype=np.uint8)

    # ========================================================================
    # TEXTURE PATTERNS
    # ========================================================================

    @staticmethod
    def wood_grain(width: int, height: int, ring_spacing: float = 0.1) -> np.ndarray:
        """Wood grain texture"""
        x = np.arange(width) / width
        y = np.arange(height) / height
        X, Y = np.meshgrid(x, y)

        # Distance from center with noise
        dist = np.sqrt((X - 0.5)**2 + (Y - 0.5)**2)
        noise = AdvancedPatternGenerator.perlin_noise(width, height, scale=5) / 255 * 0.1

        rings = np.sin(dist / ring_spacing * 2 * np.pi + noise * 10) * 0.5 + 0.5
        return (rings * 255).astype(np.uint8)

    @staticmethod
    def marble(width: int, height: int, vein_scale: float = 20.0) -> np.ndarray:
        """Marble texture"""
        perlin = AdvancedPatternGenerator.perlin_noise(width, height, scale=vein_scale)
        x = np.arange(width) / width
        y = np.arange(height) / height
        X, Y = np.meshgrid(x, y)

        marble_val = np.sin((X + perlin / 255 * 0.5) * 2 * np.pi * 5) * 0.5 + 0.5
        return (marble_val * 255).astype(np.uint8)

    @staticmethod
    def cellular(width: int, height: int, cell_size: int = 20) -> np.ndarray:
        """Cellular/organic pattern"""
        # Create grid of cells
        num_x = width // cell_size + 1
        num_y = height // cell_size + 1

        cells = np.random.rand(num_y, num_x) * 255

        # Resize to full size with smooth interpolation
        from PIL import Image
        cell_img = Image.fromarray(cells.astype(np.uint8))
        cell_img = cell_img.resize((width, height), Image.Resampling.BILINEAR)

        return np.array(cell_img)


class AdvancedMediaGenerator:
    """Advanced media generation with extensive variety"""

    @classmethod
    def generate_pattern(cls, width: int, height: int, pattern_type: str,
                        **params) -> np.ndarray:
        """Universal pattern generator dispatcher"""

        pg = AdvancedPatternGenerator()

        # Fractal patterns
        if pattern_type == 'mandelbrot':
            return pg.mandelbrot(width, height, **params)
        elif pattern_type == 'julia':
            return pg.julia_set(width, height, **params)
        elif pattern_type == 'burning_ship':
            return pg.burning_ship(width, height, **params)
        elif pattern_type == 'sierpinski':
            return pg.sierpinski_triangle(width, height, **params)

        # Noise patterns
        elif pattern_type == 'gaussian_noise':
            return pg.gaussian_noise(width, height, **params)
        elif pattern_type == 'uniform_noise':
            return pg.uniform_noise(width, height)
        elif pattern_type == 'salt_pepper':
            return pg.salt_pepper_noise(width, height, **params)
        elif pattern_type == 'perlin':
            return pg.perlin_noise(width, height, **params)
        elif pattern_type == 'worley':
            return pg.worley_noise(width, height, **params)

        # Geometric patterns
        elif pattern_type == 'checkerboard':
            return pg.checkerboard(width, height, **params)
        elif pattern_type == 'stripes':
            return pg.stripes(width, height, **params)
        elif pattern_type == 'circles':
            return pg.concentric_circles(width, height, **params)
        elif pattern_type == 'spiral':
            return pg.spiral(width, height, **params)
        elif pattern_type == 'hexagonal':
            return pg.hexagonal_grid(width, height, **params)
        elif pattern_type == 'waves':
            return pg.wave_interference(width, height, **params)

        # Advanced patterns
        elif pattern_type == 'lissajous':
            return pg.lissajous(width, height, **params)
        elif pattern_type == 'moire':
            return pg.moire_pattern(width, height, **params)
        elif pattern_type == 'gradient':
            return pg.gradient(width, height, **params)

        # Texture patterns
        elif pattern_type == 'wood':
            return pg.wood_grain(width, height, **params)
        elif pattern_type == 'marble':
            return pg.marble(width, height, **params)
        elif pattern_type == 'cellular':
            return pg.cellular(width, height, **params)

        # Default
        else:
            return pg.perlin_noise(width, height)

    @classmethod
    def get_pattern_library(cls) -> Dict[str, Dict[str, Any]]:
        """Get library of all available patterns with their parameters"""
        return {
            "fractals": {
                "mandelbrot": {"params": ["max_iter", "zoom", "offset_x", "offset_y"]},
                "julia": {"params": ["c_real", "c_imag", "max_iter"]},
                "burning_ship": {"params": ["max_iter"]},
                "sierpinski": {"params": ["iterations"]}
            },
            "noise": {
                "gaussian_noise": {"params": ["mean", "std"]},
                "uniform_noise": {"params": []},
                "salt_pepper": {"params": ["salt_prob", "pepper_prob"]},
                "perlin": {"params": ["scale", "octaves"]},
                "worley": {"params": ["num_points"]}
            },
            "geometric": {
                "checkerboard": {"params": ["square_size"]},
                "stripes": {"params": ["stripe_width", "vertical"]},
                "circles": {"params": ["num_circles"]},
                "spiral": {"params": ["num_turns"]},
                "hexagonal": {"params": ["hex_size"]},
                "waves": {"params": ["num_sources", "wavelength"]}
            },
            "advanced": {
                "lissajous": {"params": ["a", "b", "delta"]},
                "moire": {"params": ["line_spacing", "angle1", "angle2"]},
                "gradient": {"params": ["gradient_type", "angle"]}
            },
            "textures": {
                "wood": {"params": ["ring_spacing"]},
                "marble": {"params": ["vein_scale"]},
                "cellular": {"params": ["cell_size"]}
            }
        }
