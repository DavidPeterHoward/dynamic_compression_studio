"""
LZMA (Lempel-Ziv-Markov chain Algorithm) Compression Family

LZMA uses a dictionary compression scheme similar to LZ77 but with significant improvements:
- Larger dictionary sizes (up to 4GB)
- Advanced binary range encoding instead of Huffman
- Markov chain modeling for probability estimation
- Sophisticated match finding algorithms

Mathematical Foundation:
-----------------------
LZMA = LZ77-variant + Range Encoding + Markov Chains

1. Dictionary Compression:
   - Dictionary size D (typically 2^n where n ∈ [12, 30])
   - Maximum match length L = 273
   - Sliding window with binary search trees

2. Range Encoding:
   - Arithmetic coding variant with better performance
   - Probability model: P(symbol|context)
   - Range: [low, high) subdivided by symbol probabilities
   - Output: shortest binary fraction in final range

3. Markov Chain Context Modeling:
   - State machine with contexts
   - Probability estimation using adaptive models
   - Binary decision trees for literal/match decisions

Compression Ratio:
ρ = n / (Σ -log₂(P(sᵢ|contextᵢ)))

Where P(sᵢ|contextᵢ) is probability of symbol sᵢ given its context.

References:
- Pavlov, I. (2019). "LZMA SDK" (7-Zip)
- Mahoney, M. (2013). "Data Compression Explained"
- Salomon, D. (2007). "Data Compression: The Complete Reference"
"""

from .versions.v1_basic import LzmaBasic
from .versions.v2_range_optimized import LzmaRangeOptimized
from .versions.v3_markov_enhanced import LzmaMarkovEnhanced
from .versions.v4_adaptive import LzmaAdaptive
from .versions.v5_quantum_inspired import LzmaQuantumInspired

__all__ = [
    'LzmaBasic',
    'LzmaRangeOptimized',
    'LzmaMarkovEnhanced',
    'LzmaAdaptive',
    'LzmaQuantumInspired'
]

# Algorithm family metadata
FAMILY_INFO = {
    'name': 'LZMA',
    'type': 'Dictionary + Range Encoding',
    'best_for': ['archives', 'software distribution', 'maximum compression'],
    'compression_ratio': '5-20x typical',
    'speed': 'slow compression, moderate decompression',
    'memory': 'high (dictionary size + work memory)',
    'patent_status': 'public domain',
    'standardized': 'Used in 7z, XZ formats'
}