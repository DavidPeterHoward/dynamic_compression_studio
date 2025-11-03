"""
GZIP Compression Algorithm Family

GZIP implements the DEFLATE algorithm (RFC 1951), combining LZ77 and Huffman coding.

Mathematical Foundation:
-----------------------
DEFLATE = LZ77 + Huffman

1. LZ77 Phase:
   - Sliding window dictionary compression
   - Replaces repeated sequences with (distance, length) pairs
   - Window size W, lookahead buffer L
   - Compression ratio: ρ_LZ77 = n / (k * log(W) + m * log(L))
   
2. Huffman Phase:
   - Variable-length prefix-free codes
   - Optimal for known symbol frequencies
   - Average code length: L = Σ p_i * l_i ≈ H(S)

Overall compression: ρ_GZIP ≈ ρ_LZ77 * ρ_Huffman

References:
- Ziv, J. & Lempel, A. (1977). "A Universal Algorithm for Sequential Data Compression"
- Huffman, D.A. (1952). "A Method for the Construction of Minimum-Redundancy Codes"
- Deutsch, P. (1996). "DEFLATE Compressed Data Format Specification" (RFC 1951)
"""

from .versions.v1_basic import GzipBasic
from .versions.v2_strategy import GzipStrategy
from .versions.v3_decorator import GzipDecorator
from .versions.v4_adaptive import GzipAdaptive
from .versions.v5_metarecursive import GzipMetaRecursive

__all__ = [
    'GzipBasic',
    'GzipStrategy',
    'GzipDecorator',
    'GzipAdaptive',
    'GzipMetaRecursive'
]

# Algorithm family metadata
FAMILY_INFO = {
    'name': 'GZIP',
    'type': 'LZ77 + Huffman',
    'best_for': ['text', 'source code', 'structured data'],
    'compression_ratio': '2-10x typical',
    'speed': 'fast',
    'memory': 'low (32KB window)',
    'patent_status': 'expired',
    'standardized': 'RFC 1951, RFC 1952'
}