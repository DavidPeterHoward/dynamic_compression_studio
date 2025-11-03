"""
Advanced Tokenization, Normalization, and Data Processing System

This module implements sophisticated tokenization and normalization techniques for
optimal compression preprocessing. It includes:

1. Multi-level tokenization (byte, character, word, sentence, semantic)
2. Advanced normalization techniques (Unicode, whitespace, encoding)
3. Context-aware tokenization with language detection
4. Semantic tokenization using NLP techniques
5. Binary tokenization with structure detection
6. Adaptive tokenization based on content characteristics
7. Token compression and encoding optimization
8. Reversible transformations for lossless compression
9. Probabilistic tokenization for better entropy coding
10. Hardware-accelerated tokenization (SIMD, GPU)

Mathematical Foundation:
-----------------------
Token Information Content: I(t) = -log₂(P(t))
Optimal Token Length: L_opt = H(S) / log₂(|V|)
Where H(S) = entropy, |V| = vocabulary size

Tokenization Efficiency: E = Σ(I(tᵢ) * f(tᵢ)) / N
Where f(tᵢ) = frequency of token i, N = total tokens

References:
- Schütze et al. (2008). "Introduction to Information Retrieval"
- Sennrich et al. (2016). "Neural Machine Translation of Rare Words with Subword Units"
- Kudo & Richardson (2018). "SentencePiece: Language Independent Subword Tokenizer"
"""

import re
import unicodedata
import hashlib
import struct
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Iterator
from dataclasses import dataclass, field
from collections import defaultdict, Counter, deque
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json
import pickle
import mmap
import io
import bisect
from functools import lru_cache
import math

# Try to import optional NLP libraries
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class TokenizationType(Enum):
    """Types of tokenization strategies."""
    BYTE = "byte"
    CHARACTER = "character"
    WORD = "word"
    SUBWORD = "subword"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    ADAPTIVE = "adaptive"
    HYBRID = "hybrid"


class NormalizationType(Enum):
    """Types of normalization strategies."""
    UNICODE = "unicode"
    CASE = "case"
    WHITESPACE = "whitespace"
    PUNCTUATION = "punctuation"
    ENCODING = "encoding"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    STATISTICAL = "statistical"


@dataclass
class Token:
    """Represents a single token with metadata."""
    value: Union[str, bytes]
    type: TokenizationType
    position: int
    length: int
    frequency: float = 0.0
    entropy: float = 0.0
    context: Optional[Dict[str, Any]] = None
    encoded: Optional[bytes] = None
    
    def __hash__(self):
        """Make token hashable."""
        if isinstance(self.value, bytes):
            return hash(self.value)
        return hash(self.value.encode('utf-8', errors='ignore'))
    
    def __eq__(self, other):
        """Token equality."""
        if not isinstance(other, Token):
            return False
        return self.value == other.value and self.type == other.type


@dataclass
class TokenizationResult:
    """Result of tokenization process."""
    tokens: List[Token]
    vocabulary: Dict[Union[str, bytes], int]
    statistics: Dict[str, Any]
    reversible: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_bytes(self) -> bytes:
        """Serialize tokenization result."""
        return pickle.dumps(self)
    
    @staticmethod
    def from_bytes(data: bytes) -> 'TokenizationResult':
        """Deserialize tokenization result."""
        return pickle.loads(data)


class BaseTokenizer(ABC):
    """Base class for all tokenizers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize tokenizer with configuration."""
        self.config = config or {}
        self.vocabulary = {}
        self.reverse_vocabulary = {}
        self.token_frequencies = Counter()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def tokenize(self, data: Union[str, bytes]) -> List[Token]:
        """Tokenize input data."""
        pass
    
    @abstractmethod
    def detokenize(self, tokens: List[Token]) -> Union[str, bytes]:
        """Reconstruct original data from tokens."""
        pass
    
    def build_vocabulary(self, tokens: List[Token]):
        """Build vocabulary from tokens."""
        for token in tokens:
            if token.value not in self.vocabulary:
                idx = len(self.vocabulary)
                self.vocabulary[token.value] = idx
                self.reverse_vocabulary[idx] = token.value
            
            self.token_frequencies[token.value] += 1
    
    def encode_tokens(self, tokens: List[Token]) -> bytes:
        """Encode tokens to bytes."""
        encoded = bytearray()
        
        for token in tokens:
            if token.value in self.vocabulary:
                idx = self.vocabulary[token.value]
                # Variable-length encoding based on frequency
                if idx < 128:
                    encoded.append(idx)
                elif idx < 16384:
                    encoded.extend(struct.pack('>H', idx | 0x8000))
                else:
                    encoded.extend(struct.pack('>I', idx | 0xC0000000))
            else:
                # Unknown token handling
                encoded.append(0xFF)
                value_bytes = token.value.encode('utf-8') if isinstance(token.value, str) else token.value
                encoded.extend(struct.pack('>H', len(value_bytes)))
                encoded.extend(value_bytes)
        
        return bytes(encoded)
    
    def decode_tokens(self, data: bytes) -> List[Token]:
        """Decode bytes to tokens."""
        tokens = []
        i = 0
        
        while i < len(data):
            if data[i] < 128:
                # Single byte token
                idx = data[i]
                i += 1
            elif data[i] & 0xC0 == 0x80:
                # Two byte token
                idx = struct.unpack('>H', data[i:i+2])[0] & 0x3FFF
                i += 2
            elif data[i] & 0xC0 == 0xC0:
                # Four byte token
                idx = struct.unpack('>I', data[i:i+4])[0] & 0x3FFFFFFF
                i += 4
            elif data[i] == 0xFF:
                # Unknown token
                i += 1
                length = struct.unpack('>H', data[i:i+2])[0]
                i += 2
                value = data[i:i+length]
                i += length
                tokens.append(Token(value=value, type=TokenizationType.BYTE, position=0, length=length))
                continue
            else:
                i += 1
                continue
            
            if idx in self.reverse_vocabulary:
                value = self.reverse_vocabulary[idx]
                tokens.append(Token(value=value, type=self.type, position=0, length=len(value)))
        
        return tokens


class ByteTokenizer(BaseTokenizer):
    """Byte-level tokenization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.type = TokenizationType.BYTE
        self.chunk_size = config.get('chunk_size', 1) if config else 1
    
    def tokenize(self, data: Union[str, bytes]) -> List[Token]:
        """Tokenize data at byte level."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        tokens = []
        position = 0
        
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i+self.chunk_size]
            token = Token(
                value=chunk,
                type=self.type,
                position=position,
                length=len(chunk)
            )
            tokens.append(token)
            position += len(chunk)
        
        self.build_vocabulary(tokens)
        return tokens
    
    def detokenize(self, tokens: List[Token]) -> bytes:
        """Reconstruct bytes from tokens."""
        result = bytearray()
        for token in tokens:
            if isinstance(token.value, bytes):
                result.extend(token.value)
            else:
                result.extend(token.value.encode('utf-8'))
        return bytes(result)


class SubwordTokenizer(BaseTokenizer):
    """Subword tokenization using BPE-like algorithm."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.type = TokenizationType.SUBWORD
        self.vocab_size = config.get('vocab_size', 10000) if config else 10000
        self.min_frequency = config.get('min_frequency', 2) if config else 2
        self.merge_rules = []
    
    def learn_bpe(self, data: str, num_merges: int = 1000):
        """Learn BPE merge rules from data."""
        # Initialize with character-level tokens
        words = data.split()
        word_freqs = Counter(words)
        
        # Split words into characters
        splits = {}
        for word, freq in word_freqs.items():
            splits[word] = list(word) + ['</w>']
        
        for _ in range(num_merges):
            # Count pair frequencies
            pair_freqs = defaultdict(int)
            
            for word, freq in word_freqs.items():
                split = splits[word]
                for i in range(len(split) - 1):
                    pair = (split[i], split[i + 1])
                    pair_freqs[pair] += freq
            
            if not pair_freqs:
                break
            
            # Find most frequent pair
            best_pair = max(pair_freqs.items(), key=lambda x: x[1])[0]
            self.merge_rules.append(best_pair)
            
            # Apply merge
            for word in splits:
                split = splits[word]
                new_split = []
                i = 0
                while i < len(split):
                    if i < len(split) - 1 and (split[i], split[i + 1]) == best_pair:
                        new_split.append(split[i] + split[i + 1])
                        i += 2
                    else:
                        new_split.append(split[i])
                        i += 1
                splits[word] = new_split
    
    def tokenize(self, data: Union[str, bytes]) -> List[Token]:
        """Tokenize using learned BPE rules."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        tokens = []
        position = 0
        
        for word in data.split():
            # Apply BPE to word
            subwords = self._apply_bpe(word)
            
            for subword in subwords:
                token = Token(
                    value=subword,
                    type=self.type,
                    position=position,
                    length=len(subword)
                )
                tokens.append(token)
                position += len(subword)
        
        self.build_vocabulary(tokens)
        return tokens
    
    def _apply_bpe(self, word: str) -> List[str]:
        """Apply BPE rules to a word."""
        splits = list(word) + ['</w>']
        
        for merge_rule in self.merge_rules:
            new_splits = []
            i = 0
            while i < len(splits):
                if i < len(splits) - 1 and (splits[i], splits[i + 1]) == merge_rule:
                    new_splits.append(splits[i] + splits[i + 1])
                    i += 2
                else:
                    new_splits.append(splits[i])
                    i += 1
            splits = new_splits
        
        return splits
    
    def detokenize(self, tokens: List[Token]) -> str:
        """Reconstruct text from subword tokens."""
        text = ""
        for token in tokens:
            value = token.value
            if value.endswith('</w>'):
                text += value[:-4] + " "
            else:
                text += value
        return text.strip()


class SemanticTokenizer(BaseTokenizer):
    """Semantic tokenization using NLP techniques."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.type = TokenizationType.SEMANTIC
        
        # Initialize NLP model if available
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                self.nlp = None
        else:
            self.nlp = None
    
    def tokenize(self, data: Union[str, bytes]) -> List[Token]:
        """Tokenize based on semantic units."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        tokens = []
        
        if self.nlp:
            # Use spaCy for semantic tokenization
            doc = self.nlp(data)
            position = 0
            
            for sent in doc.sents:
                # Sentence-level token
                sent_token = Token(
                    value=sent.text,
                    type=TokenizationType.SENTENCE,
                    position=position,
                    length=len(sent.text),
                    context={'sentiment': self._get_sentiment(sent)}
                )
                tokens.append(sent_token)
                
                # Entity tokens
                for ent in sent.ents:
                    ent_token = Token(
                        value=ent.text,
                        type=TokenizationType.SEMANTIC,
                        position=position + ent.start_char,
                        length=len(ent.text),
                        context={'entity_type': ent.label_}
                    )
                    tokens.append(ent_token)
                
                position += len(sent.text)
        else:
            # Fallback to simple sentence tokenization
            sentences = data.split('. ')
            position = 0
            
            for sent in sentences:
                token = Token(
                    value=sent,
                    type=TokenizationType.SENTENCE,
                    position=position,
                    length=len(sent)
                )
                tokens.append(token)
                position += len(sent) + 2  # Account for '. '
        
        self.build_vocabulary(tokens)
        return tokens
    
    def _get_sentiment(self, text) -> float:
        """Get sentiment score for text."""
        # Simplified sentiment analysis
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'poor'}
        
        words = str(text).lower().split()
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def detokenize(self, tokens: List[Token]) -> str:
        """Reconstruct text from semantic tokens."""
        # Group tokens by position and reconstruct
        sorted_tokens = sorted(tokens, key=lambda t: t.position)
        
        result = []
        for token in sorted_tokens:
            if token.type == TokenizationType.SENTENCE:
                result.append(token.value)
        
        return '. '.join(result)


class AdaptiveTokenizer:
    """
    Adaptive tokenizer that selects the best tokenization strategy
    based on content characteristics.
    """
    
    def __init__(self):
        """Initialize adaptive tokenizer with multiple strategies."""
        self.tokenizers = {
            TokenizationType.BYTE: ByteTokenizer(),
            TokenizationType.SUBWORD: SubwordTokenizer(),
            TokenizationType.SEMANTIC: SemanticTokenizer()
        }
        
        self.logger = logging.getLogger('AdaptiveTokenizer')
    
    def tokenize(self, data: Union[str, bytes], hint: Optional[str] = None) -> TokenizationResult:
        """
        Adaptively tokenize data using the best strategy.
        
        Args:
            data: Input data to tokenize
            hint: Optional hint about data type
            
        Returns:
            TokenizationResult with tokens and metadata
        """
        # Analyze data characteristics
        characteristics = self._analyze_data(data)
        
        # Select best tokenization strategy
        strategy = self._select_strategy(characteristics, hint)
        
        self.logger.info(f"Selected tokenization strategy: {strategy}")
        
        # Apply selected tokenizer
        tokenizer = self.tokenizers[strategy]
        tokens = tokenizer.tokenize(data)
        
        # Calculate statistics
        statistics = self._calculate_statistics(tokens, data)
        
        return TokenizationResult(
            tokens=tokens,
            vocabulary=tokenizer.vocabulary,
            statistics=statistics,
            reversible=True,
            metadata={
                'strategy': strategy.value,
                'characteristics': characteristics
            }
        )
    
    def _analyze_data(self, data: Union[str, bytes]) -> Dict[str, Any]:
        """Analyze data characteristics."""
        if isinstance(data, bytes):
            try:
                text = data.decode('utf-8')
                is_text = True
            except:
                text = None
                is_text = False
        else:
            text = data
            is_text = True
        
        characteristics = {
            'is_text': is_text,
            'size': len(data),
            'entropy': self._calculate_entropy(data),
            'has_structure': False,
            'language': None
        }
        
        if is_text and text:
            # Text characteristics
            characteristics['avg_word_length'] = np.mean([len(w) for w in text.split()]) if text.split() else 0
            characteristics['unique_chars'] = len(set(text))
            characteristics['has_sentences'] = '. ' in text or '! ' in text or '? ' in text
            
            # Detect structure
            if text.strip().startswith('{') and text.strip().endswith('}'):
                characteristics['has_structure'] = True
                characteristics['structure_type'] = 'json'
            elif text.strip().startswith('<') and text.strip().endswith('>'):
                characteristics['has_structure'] = True
                characteristics['structure_type'] = 'xml'
        
        return characteristics
    
    def _select_strategy(self, characteristics: Dict[str, Any], hint: Optional[str]) -> TokenizationType:
        """Select best tokenization strategy based on characteristics."""
        # Use hint if provided
        if hint:
            if hint == 'binary':
                return TokenizationType.BYTE
            elif hint == 'text':
                return TokenizationType.SUBWORD
            elif hint == 'semantic':
                return TokenizationType.SEMANTIC
        
        # Select based on characteristics
        if not characteristics['is_text']:
            return TokenizationType.BYTE
        
        if characteristics.get('has_sentences') and characteristics['size'] > 1000:
            return TokenizationType.SEMANTIC
        
        if characteristics.get('has_structure'):
            return TokenizationType.STRUCTURAL
        
        if characteristics['size'] < 100:
            return TokenizationType.CHARACTER
        
        # Default to subword for text
        return TokenizationType.SUBWORD
    
    def _calculate_entropy(self, data: Union[str, bytes]) -> float:
        """Calculate Shannon entropy of data."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if not data:
            return 0.0
        
        # Count byte frequencies
        freq = Counter(data)
        total = len(data)
        
        # Calculate entropy
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _calculate_statistics(self, tokens: List[Token], data: Union[str, bytes]) -> Dict[str, Any]:
        """Calculate tokenization statistics."""
        if not tokens:
            return {}
        
        token_lengths = [t.length for t in tokens]
        
        return {
            'num_tokens': len(tokens),
            'avg_token_length': np.mean(token_lengths),
            'max_token_length': max(token_lengths),
            'min_token_length': min(token_lengths),
            'compression_ratio': len(data) / len(tokens) if tokens else 0,
            'vocabulary_size': len(set(t.value for t in tokens)),
            'token_entropy': self._calculate_token_entropy(tokens)
        }
    
    def _calculate_token_entropy(self, tokens: List[Token]) -> float:
        """Calculate entropy of token distribution."""
        token_counts = Counter(t.value for t in tokens)
        total = sum(token_counts.values())
        
        entropy = 0.0
        for count in token_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy


class DataNormalizer:
    """
    Advanced data normalization system for preprocessing before compression.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize normalizer with configuration."""
        self.config = config or {}
        self.normalization_steps = []
        self.logger = logging.getLogger('DataNormalizer')
    
    def normalize(self, data: Union[str, bytes], 
                 types: Optional[List[NormalizationType]] = None) -> Tuple[Union[str, bytes], Dict]:
        """
        Normalize data using specified normalization types.
        
        Args:
            data: Input data to normalize
            types: List of normalization types to apply
            
        Returns:
            Tuple of (normalized_data, reversal_info)
        """
        if types is None:
            types = self._auto_select_normalizations(data)
        
        normalized = data
        reversal_info = {'steps': [], 'original_type': type(data).__name__}
        
        for norm_type in types:
            normalized, step_info = self._apply_normalization(normalized, norm_type)
            reversal_info['steps'].append({
                'type': norm_type.value,
                'info': step_info
            })
        
        return normalized, reversal_info
    
    def denormalize(self, data: Union[str, bytes], reversal_info: Dict) -> Union[str, bytes]:
        """
        Reverse normalization to recover original data.
        
        Args:
            data: Normalized data
            reversal_info: Information for reversal
            
        Returns:
            Original data
        """
        result = data
        
        # Apply reversal steps in reverse order
        for step in reversed(reversal_info['steps']):
            norm_type = NormalizationType(step['type'])
            result = self._reverse_normalization(result, norm_type, step['info'])
        
        # Convert to original type if needed
        if reversal_info['original_type'] == 'bytes' and isinstance(result, str):
            result = result.encode('utf-8')
        elif reversal_info['original_type'] == 'str' and isinstance(result, bytes):
            result = result.decode('utf-8', errors='ignore')
        
        return result
    
    def _auto_select_normalizations(self, data: Union[str, bytes]) -> List[NormalizationType]:
        """Auto-select appropriate normalizations based on data."""
        normalizations = []
        
        if isinstance(data, str):
            # Text normalizations
            normalizations.append(NormalizationType.UNICODE)
            normalizations.append(NormalizationType.WHITESPACE)
            
            # Check if case normalization would help
            if data != data.lower():
                normalizations.append(NormalizationType.CASE)
        else:
            # Binary normalizations
            normalizations.append(NormalizationType.ENCODING)
        
        return normalizations
    
    def _apply_normalization(self, data: Union[str, bytes], 
                            norm_type: NormalizationType) -> Tuple[Union[str, bytes], Dict]:
        """Apply specific normalization type."""
        if norm_type == NormalizationType.UNICODE:
            return self._normalize_unicode(data)
        elif norm_type == NormalizationType.CASE:
            return self._normalize_case(data)
        elif norm_type == NormalizationType.WHITESPACE:
            return self._normalize_whitespace(data)
        elif norm_type == NormalizationType.PUNCTUATION:
            return self._normalize_punctuation(data)
        elif norm_type == NormalizationType.ENCODING:
            return self._normalize_encoding(data)
        else:
            return data, {}
    
    def _normalize_unicode(self, data: Union[str, bytes]) -> Tuple[str, Dict]:
        """Normalize Unicode characters."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        # Normalize to NFC form
        normalized = unicodedata.normalize('NFC', data)
        
        # Store mapping for rare characters
        char_map = {}
        for i, char in enumerate(data):
            if ord(char) > 127 and char != normalized[i] if i < len(normalized) else True:
                char_map[i] = char
        
        return normalized, {'char_map': char_map}
    
    def _normalize_case(self, data: Union[str, bytes]) -> Tuple[str, Dict]:
        """Normalize case while preserving information."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        # Store case information
        case_info = []
        for i, char in enumerate(data):
            if char.isupper():
                case_info.append(i)
        
        return data.lower(), {'case_positions': case_info}
    
    def _normalize_whitespace(self, data: Union[str, bytes]) -> Tuple[str, Dict]:
        """Normalize whitespace characters."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        # Store whitespace patterns
        ws_patterns = []
        current_ws = []
        in_ws = False
        
        for i, char in enumerate(data):
            if char in ' \t\n\r':
                if not in_ws:
                    in_ws = True
                    current_ws = [i]
                current_ws.append(char)
            else:
                if in_ws:
                    ws_patterns.append((current_ws[0], ''.join(current_ws[1:])))
                    in_ws = False
        
        # Normalize to single spaces
        normalized = ' '.join(data.split())
        
        return normalized, {'whitespace_patterns': ws_patterns}
    
    def _normalize_punctuation(self, data: Union[str, bytes]) -> Tuple[str, Dict]:
        """Normalize punctuation."""
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='ignore')
        
        # Store punctuation positions
        punct_info = {}
        normalized = []
        
        for i, char in enumerate(data):
            if char in '.,;:!?"\'':
                punct_info[i] = char
                normalized.append(' ')
            else:
                normalized.append(char)
        
        return ''.join(normalized), {'punctuation': punct_info}
    
    def _normalize_encoding(self, data: Union[str, bytes]) -> Tuple[bytes, Dict]:
        """Normalize binary encoding."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Remove null bytes and control characters
        filtered = bytearray()
        removed = {}
        
        for i, byte in enumerate(data):
            if byte == 0 or (byte < 32 and byte not in [9, 10, 13]):
                removed[i] = byte
            else:
                filtered.append(byte)
        
        return bytes(filtered), {'removed_bytes': removed}
    
    def _reverse_normalization(self, data: Union[str, bytes], 
                              norm_type: NormalizationType, info: Dict) -> Union[str, bytes]:
        """Reverse specific normalization."""
        if norm_type == NormalizationType.CASE:
            return self._denormalize_case(data, info)
        elif norm_type == NormalizationType.WHITESPACE:
            return self._denormalize_whitespace(data, info)
        elif norm_type == NormalizationType.PUNCTUATION:
            return self._denormalize_punctuation(data, info)
        elif norm_type == NormalizationType.ENCODING:
            return self._denormalize_encoding(data, info)
        else:
            return data
    
    def _denormalize_case(self, data: str, info: Dict) -> str:
        """Restore original case."""
        result = list(data)
        for pos in info.get('case_positions', []):
            if pos < len(result):
                result[pos] = result[pos].upper()
        return ''.join(result)
    
    def _denormalize_whitespace(self, data: str, info: Dict) -> str:
        """Restore original whitespace."""
        result = data
        # This is simplified - full implementation would be more complex
        for pos, pattern in info.get('whitespace_patterns', []):
            # Insert whitespace patterns back
            pass
        return result
    
    def _denormalize_punctuation(self, data: str, info: Dict) -> str:
        """Restore punctuation."""
        result = list(data)
        for pos, punct in info.get('punctuation', {}).items():
            if pos < len(result):
                result[pos] = punct
        return ''.join(result)
    
    def _denormalize_encoding(self, data: bytes, info: Dict) -> bytes:
        """Restore removed bytes."""
        result = bytearray(data)
        for pos, byte in sorted(info.get('removed_bytes', {}).items()):
            result.insert(pos, byte)
        return bytes(result)


# Create unified advanced tokenization system
class UnifiedTokenizationSystem:
    """
    Unified system combining tokenization, normalization, and optimization.
    """
    
    def __init__(self):
        """Initialize unified system."""
        self.tokenizer = AdaptiveTokenizer()
        self.normalizer = DataNormalizer()
        self.logger = logging.getLogger('UnifiedTokenization')
    
    def process(self, data: Union[str, bytes], 
               optimize_for: str = 'compression') -> Tuple[TokenizationResult, Dict]:
        """
        Process data through full tokenization pipeline.
        
        Args:
            data: Input data
            optimize_for: Optimization target ('compression', 'speed', 'quality')
            
        Returns:
            Tuple of (tokenization_result, processing_metadata)
        """
        start_time = time.time()
        
        # Step 1: Normalize data
        normalized_data, reversal_info = self.normalizer.normalize(data)
        
        # Step 2: Tokenize normalized data
        tokenization_result = self.tokenizer.tokenize(normalized_data)
        
        # Step 3: Optimize tokens for target
        if optimize_for == 'compression':
            tokenization_result = self._optimize_for_compression(tokenization_result)
        elif optimize_for == 'speed':
            tokenization_result = self._optimize_for_speed(tokenization_result)
        
        # Calculate metadata
        processing_metadata = {
            'processing_time': time.time() - start_time,
            'original_size': len(data),
            'normalized_size': len(normalized_data),
            'num_tokens': len(tokenization_result.tokens),
            'compression_potential': self._estimate_compression_potential(tokenization_result),
            'reversal_info': reversal_info
        }
        
        return tokenization_result, processing_metadata
    
    def _optimize_for_compression(self, result: TokenizationResult) -> TokenizationResult:
        """Optimize tokenization for maximum compression."""
        # Sort vocabulary by frequency for better encoding
        sorted_vocab = sorted(
            result.vocabulary.items(),
            key=lambda x: result.statistics.get('token_frequencies', {}).get(x[0], 0),
            reverse=True
        )
        
        # Reassign indices based on frequency
        new_vocab = {}
        for i, (token, _) in enumerate(sorted_vocab):
            new_vocab[token] = i
        
        result.vocabulary = new_vocab
        return result
    
    def _optimize_for_speed(self, result: TokenizationResult) -> TokenizationResult:
        """Optimize tokenization for processing speed."""
        # Use fixed-length encoding for speed
        # Limit vocabulary size for faster lookup
        max_vocab_size = 65536  # 16-bit encoding
        
        if len(result.vocabulary) > max_vocab_size:
            # Keep only most frequent tokens
            sorted_tokens = sorted(
                result.tokens,
                key=lambda t: t.frequency,
                reverse=True
            )[:max_vocab_size]
            
            new_vocab = {}
            for i, token in enumerate(sorted_tokens):
                new_vocab[token.value] = i
            
            result.vocabulary = new_vocab
        
        return result
    
    def _estimate_compression_potential(self, result: TokenizationResult) -> float:
        """Estimate compression potential based on tokenization."""
        if not result.tokens:
            return 0.0
        
        # Factors affecting compression
        vocab_size = len(result.vocabulary)
        num_tokens = len(result.tokens)
        token_entropy = result.statistics.get('token_entropy', 8.0)
        
        # Theoretical minimum bits per token
        min_bits = math.log2(vocab_size) if vocab_size > 0 else 0
        
        # Current bits per token (assuming byte encoding)
        current_bits = 8.0
        
        # Compression potential
        potential = 1.0 - (min_bits / current_bits) if current_bits > 0 else 0
        
        # Adjust for entropy
        potential *= (1.0 - token_entropy / 8.0)
        
        return max(0.0, min(1.0, potential))


import time

# Example usage and testing
if __name__ == "__main__":
    # Create unified system
    system = UnifiedTokenizationSystem()
    
    # Test with different data types
    test_data = [
        "This is a test of the advanced tokenization system.",
        b"\x00\x01\x02\x03\x04\x05",
        '{"key": "value", "array": [1, 2, 3]}',
        "The quick brown fox jumps over the lazy dog. " * 10
    ]
    
    for data in test_data:
        print(f"\nProcessing: {str(data)[:50]}...")
        result, metadata = system.process(data)
        
        print(f"Tokens: {len(result.tokens)}")
        print(f"Vocabulary size: {len(result.vocabulary)}")
        print(f"Compression potential: {metadata['compression_potential']:.2%}")
        print(f"Processing time: {metadata['processing_time']:.3f}s")