#!/usr/bin/env python3
"""
Comprehensive E2E Test for All Compression Algorithms
Tests all 5 compression algorithms (GZIP, BZIP2, LZ4, ZSTD, LZMA) via API
"""

import requests
import json
import time
import base64
from typing import Dict, List, Any

class CompressionAlgorithmTester:
    def __init__(self, base_url: str = "http://localhost:8443"):
        self.base_url = base_url
        self.algorithms = ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma']
        self.test_cases = [
            {
                "name": "Short Text",
                "content": "This is a short test string for compression testing."
            },
            {
                "name": "Long Text",
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 50
            },
            {
                "name": "Repetitive Content",
                "content": "The quick brown fox jumps over the lazy dog. " * 30
            },
            {
                "name": "JSON Data",
                "content": json.dumps({
                    "users": [{"id": i, "name": f"User {i}", "email": f"user{i}@example.com"} 
                             for i in range(100)]
                })
            },
            {
                "name": "Random Data",
                "content": "".join([chr(65 + (i % 26)) for i in range(1000)])
            }
        ]
    
    def test_algorithm(self, algorithm: str, content: str, level: int = 6) -> Dict[str, Any]:
        """Test a single algorithm with given content"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/compression/compress",
                json={
                    "content": content,
                    "parameters": {
                        "algorithm": algorithm,
                        "level": level
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('compressed_content'):
                    return {
                        "success": True,
                        "algorithm": algorithm,
                        "original_size": result['result']['original_size'],
                        "compressed_size": result['result']['compressed_size'],
                        "compression_ratio": result['result']['compression_ratio'],
                        "compression_percentage": result['result']['compression_percentage'],
                        "compression_time": result['result']['compression_time'],
                        "compressed_content": result['compressed_content'][:50] + "...",
                        "debug_info": result.get('debug_info', {}),
                        "test_field": result.get('test_field', 'N/A')
                    }
                else:
                    return {"success": False, "error": "Invalid response format"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_test(self):
        """Run comprehensive tests for all algorithms"""
        print("🧪 COMPREHENSIVE COMPRESSION ALGORITHMS E2E TEST")
        print("=" * 60)
        
        all_results = []
        
        for test_case in self.test_cases:
            print(f"\n📋 Testing: {test_case['name']}")
            print(f"Content length: {len(test_case['content'])} characters")
            print("-" * 40)
            
            case_results = []
            
            for algorithm in self.algorithms:
                print(f"Testing {algorithm.upper()}...", end=" ")
                
                start_time = time.time()
                result = self.test_algorithm(algorithm, test_case['content'])
                end_time = time.time()
                
                if result['success']:
                    print(f"✅ Success")
                    print(f"  Original: {result['original_size']} bytes")
                    print(f"  Compressed: {result['compressed_size']} bytes")
                    print(f"  Ratio: {result['compression_ratio']:.2f}x")
                    print(f"  Percentage: {result['compression_percentage']:.1f}%")
                    print(f"  Time: {result['compression_time']:.3f}s")
                    print(f"  API Time: {end_time - start_time:.3f}s")
                    print(f"  Debug: {result['debug_info'].get('source', 'N/A')}")
                    print(f"  Test Field: {result['test_field']}")
                else:
                    print(f"❌ Failed: {result['error']}")
                
                case_results.append({
                    "algorithm": algorithm,
                    "test_case": test_case['name'],
                    **result
                })
            
            all_results.extend(case_results)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = [r for r in all_results if r['success']]
        failed_tests = [r for r in all_results if not r['success']]
        
        print(f"✅ Successful tests: {len(successful_tests)}")
        print(f"❌ Failed tests: {len(failed_tests)}")
        print(f"📈 Success rate: {len(successful_tests) / len(all_results) * 100:.1f}%")
        
        if successful_tests:
            print("\n🏆 ALGORITHM PERFORMANCE COMPARISON")
            print("-" * 40)
            
            # Group by algorithm
            algorithm_stats = {}
            for result in successful_tests:
                alg = result['algorithm']
                if alg not in algorithm_stats:
                    algorithm_stats[alg] = []
                algorithm_stats[alg].append(result)
            
            for algorithm, results in algorithm_stats.items():
                avg_ratio = sum(r['compression_ratio'] for r in results) / len(results)
                avg_time = sum(r['compression_time'] for r in results) / len(results)
                print(f"{algorithm.upper():>6}: Avg Ratio: {avg_ratio:.2f}x, Avg Time: {avg_time:.3f}s")
        
        if failed_tests:
            print("\n❌ FAILED TESTS")
            print("-" * 20)
            for result in failed_tests:
                print(f"{result['algorithm']} - {result['test_case']}: {result['error']}")
        
        return all_results

def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Compression Algorithms E2E Test")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8443/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend service is running")
        else:
            print("⚠️  Backend service responded with non-200 status")
    except Exception as e:
        print(f"❌ Backend service is not accessible: {e}")
        return
    
    # Run comprehensive tests
    tester = CompressionAlgorithmTester()
    results = tester.run_comprehensive_test()
    
    print("\n🎉 Comprehensive E2E Test Completed!")
    print(f"Total tests executed: {len(results)}")
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("📁 Results saved to test_results.json")

if __name__ == "__main__":
    main()

