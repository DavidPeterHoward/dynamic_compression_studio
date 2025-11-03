"""
Mock data generator for comprehensive compression algorithm testing.

This module generates diverse synthetic data patterns to test all compression
algorithms across various content types, complexities, and characteristics.
"""

import random
import string
import json
import base64
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ContentComplexity(str, Enum):
    """Content complexity levels for synthetic data generation."""
    MINIMAL = "minimal"  # Highly repetitive, easy to compress
    LOW = "low"  # Some patterns, good compression
    MEDIUM = "medium"  # Mixed patterns, moderate compression
    HIGH = "high"  # High entropy, difficult to compress
    MAXIMUM = "maximum"  # Near-random, minimal compression


@dataclass
class MockCompressionData:
    """Mock data structure for compression testing."""
    
    content: str
    content_type: str
    expected_compression_ratio_range: Tuple[float, float]
    complexity: ContentComplexity
    size_bytes: int
    characteristics: Dict[str, Any]
    description: str
    optimal_algorithms: List[str]
    suboptimal_algorithms: List[str]


class MockDataGenerator:
    """
    Advanced mock data generator for compression algorithm testing.
    
    Generates synthetic data with controlled characteristics to test
    compression algorithms under various scenarios.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        self.generated_data: List[MockCompressionData] = []
    
    def generate_highly_repetitive_text(self, size_kb: int = 10) -> MockCompressionData:
        """
        Generate highly repetitive text - optimal for all compression algorithms.
        
        Expected compression ratios:
        - GZIP: 15x-50x
        - LZMA: 20x-100x
        - BZIP2: 18x-80x
        - LZ4: 10x-30x
        - ZSTD: 15x-60x
        """
        pattern = "The quick brown fox jumps over the lazy dog. "
        repetitions = (size_kb * 1024) // len(pattern)
        content = pattern * repetitions
        
        return MockCompressionData(
            content=content,
            content_type="text",
            expected_compression_ratio_range=(10.0, 100.0),
            complexity=ContentComplexity.MINIMAL,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.2,
                "redundancy": 0.95,
                "pattern_frequency": 0.98,
                "uniqueness": 0.05
            },
            description="Highly repetitive text with single repeating pattern",
            optimal_algorithms=["lzma", "bzip2", "gzip", "zstd"],
            suboptimal_algorithms=["lz4"]
        )
    
    def generate_natural_language_text(self, size_kb: int = 10) -> MockCompressionData:
        """
        Generate natural language-like text with realistic patterns.
        
        Expected compression ratios:
        - GZIP: 2x-4x
        - LZMA: 2.5x-5x
        - BZIP2: 2.3x-4.5x
        - LZ4: 1.5x-2.5x
        - ZSTD: 2.2x-4x
        """
        words = [
            "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
            "compression", "algorithm", "data", "processing", "efficient",
            "performance", "optimization", "analysis", "system", "implementation",
            "testing", "validation", "metrics", "evaluation", "benchmark"
        ]
        
        sentences = []
        target_size = size_kb * 1024
        current_size = 0
        
        while current_size < target_size:
            sentence_length = random.randint(5, 15)
            sentence = " ".join(random.choice(words) for _ in range(sentence_length))
            sentence = sentence.capitalize() + ". "
            sentences.append(sentence)
            current_size += len(sentence)
        
        content = "".join(sentences)
        
        return MockCompressionData(
            content=content,
            content_type="text",
            expected_compression_ratio_range=(1.5, 5.0),
            complexity=ContentComplexity.LOW,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.5,
                "redundancy": 0.6,
                "pattern_frequency": 0.7,
                "uniqueness": 0.3
            },
            description="Natural language text with realistic word patterns",
            optimal_algorithms=["gzip", "zstd", "brotli", "lzma"],
            suboptimal_algorithms=[]
        )
    
    def generate_json_data(self, size_kb: int = 10) -> MockCompressionData:
        """
        Generate structured JSON data - good for dictionary-based compression.
        
        Expected compression ratios:
        - GZIP: 3x-6x
        - LZMA: 4x-8x
        - BZIP2: 3.5x-7x
        - ZSTD: 3.5x-7x (with dictionary)
        - BROTLI: 4x-8x
        """
        records = []
        target_size = size_kb * 1024
        current_size = 0
        
        while current_size < target_size:
            record = {
                "id": random.randint(1000, 9999),
                "name": f"User{random.randint(1, 1000)}",
                "email": f"user{random.randint(1, 1000)}@example.com",
                "age": random.randint(18, 80),
                "city": random.choice(["New York", "London", "Tokyo", "Paris", "Berlin"]),
                "status": random.choice(["active", "inactive", "pending"]),
                "score": round(random.uniform(0, 100), 2),
                "tags": random.sample(["python", "java", "javascript", "go", "rust"], k=random.randint(1, 3))
            }
            records.append(record)
            current_size = len(json.dumps(records, indent=2))
        
        content = json.dumps(records, indent=2)
        
        return MockCompressionData(
            content=content,
            content_type="json",
            expected_compression_ratio_range=(3.0, 8.0),
            complexity=ContentComplexity.MEDIUM,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.6,
                "redundancy": 0.5,
                "pattern_frequency": 0.75,
                "uniqueness": 0.4,
                "structure": "hierarchical"
            },
            description="Structured JSON data with repeated keys and patterns",
            optimal_algorithms=["zstd", "brotli", "lzma", "gzip"],
            suboptimal_algorithms=[]
        )
    
    def generate_xml_data(self, size_kb: int = 10) -> MockCompressionData:
        """Generate XML data with nested structure."""
        records = []
        target_size = size_kb * 1024
        current_size = 0
        
        while current_size < target_size:
            xml_record = f"""
            <record>
                <id>{random.randint(1000, 9999)}</id>
                <name>User{random.randint(1, 1000)}</name>
                <email>user{random.randint(1, 1000)}@example.com</email>
                <details>
                    <age>{random.randint(18, 80)}</age>
                    <city>{random.choice(["New York", "London", "Tokyo"])}</city>
                    <status>{random.choice(["active", "inactive"])}</status>
                </details>
            </record>
            """
            records.append(xml_record)
            current_size = len("".join(records))
        
        content = f'<?xml version="1.0" encoding="UTF-8"?><records>{"".join(records)}</records>'
        
        return MockCompressionData(
            content=content,
            content_type="xml",
            expected_compression_ratio_range=(4.0, 10.0),
            complexity=ContentComplexity.MEDIUM,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.55,
                "redundancy": 0.6,
                "pattern_frequency": 0.8,
                "uniqueness": 0.3,
                "structure": "hierarchical"
            },
            description="Structured XML with heavy tag repetition",
            optimal_algorithms=["lzma", "bzip2", "gzip", "zstd"],
            suboptimal_algorithms=["lz4"]
        )
    
    def generate_log_data(self, size_kb: int = 10) -> MockCompressionData:
        """Generate log file data with timestamps and repeated patterns."""
        log_levels = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
        modules = ["auth", "database", "api", "cache", "worker"]
        messages = [
            "Request processed successfully",
            "Database connection established",
            "Cache hit for key",
            "User authentication successful",
            "API request received",
            "Worker task completed",
            "Configuration loaded",
            "Service started"
        ]
        
        logs = []
        target_size = size_kb * 1024
        current_size = 0
        
        timestamp = 1609459200  # Start timestamp
        
        while current_size < target_size:
            log_entry = f"[{timestamp}] [{random.choice(log_levels)}] [{random.choice(modules)}] {random.choice(messages)} - ID:{random.randint(1000, 9999)}\n"
            logs.append(log_entry)
            current_size += len(log_entry)
            timestamp += random.randint(1, 10)
        
        content = "".join(logs)
        
        return MockCompressionData(
            content=content,
            content_type="log",
            expected_compression_ratio_range=(3.0, 7.0),
            complexity=ContentComplexity.LOW,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.55,
                "redundancy": 0.65,
                "pattern_frequency": 0.75,
                "uniqueness": 0.3,
                "temporal_patterns": True
            },
            description="Log file with repeated patterns and timestamps",
            optimal_algorithms=["gzip", "zstd", "lzma"],
            suboptimal_algorithms=[]
        )
    
    def generate_source_code(self, size_kb: int = 10) -> MockCompressionData:
        """Generate source code with realistic structure."""
        code_templates = [
            "def function_{n}(param1, param2):\n    result = param1 + param2\n    return result\n\n",
            "class Class{n}:\n    def __init__(self):\n        self.value = {n}\n    def process(self):\n        return self.value * 2\n\n",
            "for i in range({n}):\n    print(f'Iteration {{i}}')\n    process_data(i)\n\n",
            "if condition_{n}:\n    execute_action()\nelse:\n    handle_error()\n\n"
        ]
        
        code_lines = []
        target_size = size_kb * 1024
        current_size = 0
        
        while current_size < target_size:
            template = random.choice(code_templates)
            code = template.format(n=random.randint(1, 100))
            code_lines.append(code)
            current_size += len(code)
        
        content = "".join(code_lines)
        
        return MockCompressionData(
            content=content,
            content_type="code",
            expected_compression_ratio_range=(2.5, 5.0),
            complexity=ContentComplexity.MEDIUM,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.6,
                "redundancy": 0.55,
                "pattern_frequency": 0.7,
                "uniqueness": 0.4,
                "structural_patterns": True
            },
            description="Source code with typical programming patterns",
            optimal_algorithms=["gzip", "zstd", "brotli"],
            suboptimal_algorithms=[]
        )
    
    def generate_high_entropy_data(self, size_kb: int = 10) -> MockCompressionData:
        """
        Generate high-entropy data - difficult to compress.
        
        Expected compression ratios:
        - All algorithms: 1.0x-1.2x (minimal compression)
        """
        # Generate pseudo-random data
        content = "".join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(size_kb * 1024)
        )
        
        return MockCompressionData(
            content=content,
            content_type="random",
            expected_compression_ratio_range=(1.0, 1.2),
            complexity=ContentComplexity.MAXIMUM,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.95,
                "redundancy": 0.05,
                "pattern_frequency": 0.1,
                "uniqueness": 0.9
            },
            description="High-entropy pseudo-random data with minimal compressibility",
            optimal_algorithms=["lz4"],  # LZ4 for speed when compression is futile
            suboptimal_algorithms=["lzma", "bzip2"]  # Slow with no benefit
        )
    
    def generate_mixed_content(self, size_kb: int = 10) -> MockCompressionData:
        """Generate mixed content combining different types."""
        sections = []
        target_size = size_kb * 1024
        current_size = 0
        
        generators = [
            self.generate_natural_language_text,
            self.generate_json_data,
            self.generate_log_data
        ]
        
        while current_size < target_size:
            generator = random.choice(generators)
            section_data = generator(size_kb=1)  # Generate 1KB sections
            sections.append(f"\n--- {section_data.content_type.upper()} SECTION ---\n")
            sections.append(section_data.content[:1024])  # Use first 1KB
            current_size = sum(len(s) for s in sections)
        
        content = "".join(sections)
        
        return MockCompressionData(
            content=content,
            content_type="mixed",
            expected_compression_ratio_range=(2.0, 4.0),
            complexity=ContentComplexity.HIGH,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.7,
                "redundancy": 0.4,
                "pattern_frequency": 0.6,
                "uniqueness": 0.5,
                "heterogeneous": True
            },
            description="Mixed content combining multiple data types",
            optimal_algorithms=["content_aware", "zstd", "gzip"],
            suboptimal_algorithms=[]
        )
    
    def generate_numeric_data(self, size_kb: int = 10) -> MockCompressionData:
        """Generate numeric/CSV data."""
        headers = ["timestamp", "value1", "value2", "value3", "category"]
        rows = [",".join(headers)]
        
        target_size = size_kb * 1024
        current_size = len(rows[0])
        
        timestamp = 1609459200
        while current_size < target_size:
            row = f"{timestamp},{random.uniform(0, 100):.2f},{random.uniform(0, 100):.2f},{random.uniform(0, 100):.2f},{random.choice(['A', 'B', 'C'])}"
            rows.append(row)
            current_size += len(row) + 1  # +1 for newline
            timestamp += 60
        
        content = "\n".join(rows)
        
        return MockCompressionData(
            content=content,
            content_type="csv",
            expected_compression_ratio_range=(2.0, 4.0),
            complexity=ContentComplexity.MEDIUM,
            size_bytes=len(content),
            characteristics={
                "entropy": 0.6,
                "redundancy": 0.5,
                "pattern_frequency": 0.65,
                "uniqueness": 0.4,
                "columnar_structure": True
            },
            description="Numeric CSV data with repeated structure",
            optimal_algorithms=["gzip", "zstd", "lzma"],
            suboptimal_algorithms=[]
        )
    
    def generate_all_test_cases(self) -> List[MockCompressionData]:
        """Generate comprehensive test suite with all data types."""
        test_cases = [
            self.generate_highly_repetitive_text(10),
            self.generate_natural_language_text(10),
            self.generate_json_data(10),
            self.generate_xml_data(10),
            self.generate_log_data(10),
            self.generate_source_code(10),
            self.generate_high_entropy_data(10),
            self.generate_mixed_content(10),
            self.generate_numeric_data(10),
            
            # Larger test cases
            self.generate_natural_language_text(100),
            self.generate_json_data(100),
            self.generate_log_data(100),
            
            # Smaller test cases
            self.generate_natural_language_text(1),
            self.generate_json_data(1),
        ]
        
        self.generated_data = test_cases
        return test_cases
    
    def get_test_case_summary(self) -> Dict[str, Any]:
        """Get summary statistics of generated test cases."""
        if not self.generated_data:
            self.generate_all_test_cases()
        
        return {
            "total_cases": len(self.generated_data),
            "total_size_bytes": sum(d.size_bytes for d in self.generated_data),
            "complexity_distribution": {
                complexity.value: sum(1 for d in self.generated_data if d.complexity == complexity)
                for complexity in ContentComplexity
            },
            "content_type_distribution": {
                ct: sum(1 for d in self.generated_data if d.content_type == ct)
                for ct in set(d.content_type for d in self.generated_data)
            },
            "size_ranges": {
                "small_1kb": sum(1 for d in self.generated_data if d.size_bytes < 2048),
                "medium_10kb": sum(1 for d in self.generated_data if 2048 <= d.size_bytes < 20480),
                "large_100kb": sum(1 for d in self.generated_data if d.size_bytes >= 20480)
            }
        }


# Singleton instance for easy import
mock_data_generator = MockDataGenerator()

if __name__ == "__main__":
    # Generate and display test cases
    generator = MockDataGenerator()
    test_cases = generator.generate_all_test_cases()
    summary = generator.get_test_case_summary()
    
    print("=" * 80)
    print("MOCK COMPRESSION DATA GENERATOR - TEST SUITE SUMMARY")
    print("=" * 80)
    print(json.dumps(summary, indent=2))
    print(f"\nGenerated {len(test_cases)} test cases")
    print(f"Total size: {summary['total_size_bytes']:,} bytes")
    
    print("\n" + "=" * 80)
    print("SAMPLE TEST CASES")
    print("=" * 80)
    for i, case in enumerate(test_cases[:3], 1):
        print(f"\n{i}. {case.description}")
        print(f"   Type: {case.content_type}, Complexity: {case.complexity.value}")
        print(f"   Size: {case.size_bytes:,} bytes")
        print(f"   Expected ratio: {case.expected_compression_ratio_range[0]:.1f}x - {case.expected_compression_ratio_range[1]:.1f}x")
        print(f"   Optimal algorithms: {', '.join(case.optimal_algorithms)}")
        print(f"   Characteristics: {case.characteristics}")

