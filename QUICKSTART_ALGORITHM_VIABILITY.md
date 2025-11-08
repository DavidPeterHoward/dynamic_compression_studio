# Quick Start Guide: Algorithm Viability Analysis

## 🚀 Quick Start (5 Minutes)

### Option 1: Run Comprehensive Test Suite

```bash
# Navigate to backend
cd backend

# Run the complete algorithm viability test suite
python tests/run_comprehensive_algorithm_viability_tests.py
```

**What This Does**:
- ✅ Generates 14+ synthetic test cases (text, JSON, XML, logs, code, CSV, etc.)
- ✅ Tests all 10 compression algorithms (GZIP, LZMA, BZIP2, LZ4, ZSTD, Brotli, Content-Aware, + 3 experimental)
- ✅ Records all results to meta-learning database
- ✅ Generates comprehensive JSON report
- ✅ Displays rankings and recommendations

**Expected Output**:
```
================================================================================
COMPREHENSIVE ALGORITHM VIABILITY TEST RUNNER
================================================================================
Test Run ID: 550e8400-e29b-41d4-a716-446655440000

Step 1: Generating Synthetic Test Data
--------------------------------------------------------------------------------
Generated 14 test cases
Total size: 143,360 bytes

Step 2: Testing Compression Algorithms
--------------------------------------------------------------------------------
Testing: GZIP ✓ (14/14 successful)
Testing: LZMA ✓ (14/14 successful)
...

Top 5 Algorithms by Average Compression Ratio:
1. LZMA: 4.87x (100.0% success)
2. BZIP2: 4.12x (100.0% success)
3. ZSTD: 3.91x (100.0% success)
```

**Output Files**:
- Report: `backend/tests/test_results/viability_report_[UUID].json`
- Database: `data/meta_learning.db` (updated)

---

### Option 2: Run Integrated Workflow

```bash
# Navigate to backend
cd backend

# Run the integrated synthetic data + testing workflow
python tests/integration_synthetic_data_workflow.py
```

**What This Does**:
- ✅ Generates synthetic data for specific content types
- ✅ Tests selected algorithms
- ✅ Records to database
- ✅ Generates insights (best algorithms, tradeoffs, rankings)
- ✅ Exports frontend-compatible JSON

**Expected Output**:
```
================================================================================
SYNTHETIC DATA + ALGORITHM VIABILITY INTEGRATION WORKFLOW
================================================================================
Workflow ID: 7a3b2c1d...

STEP 1: Generating Synthetic Test Data
✓ Generated 9 synthetic test cases

STEP 2: Running Algorithm Viability Tests
  Testing: GZIP... ✓ (9/9 successful)
  Testing: LZMA... ✓ (9/9 successful)
  ...

STEP 4: Generating Insights and Recommendations
✓ Generated 5 learning insights

Key Insights:
  1. GZIP performs best on text content with 3.42x compression
  2. Speed/compression tradeoff: LZ4 fastest (0.5ms), LZMA best ratio (5.2x)
  ...
```

**Output Files**:
- Export: `backend/tests/test_results/frontend_export_[UUID].json`
- Database: `data/meta_learning.db` (updated)

---

### Option 3: Run Pytest Unit Tests

```bash
# Navigate to backend
cd backend

# Run unit tests for all algorithms
pytest tests/test_algorithm_viability_complete.py -v

# Or run specific test
pytest tests/test_algorithm_viability_complete.py::TestAlgorithmViability::test_gzip_algorithm_viability -v

# Or run comprehensive analysis only
pytest tests/test_algorithm_viability_complete.py -k "comprehensive" -v
```

**What This Does**:
- ✅ Runs individual algorithm tests
- ✅ Validates performance against expected ranges
- ✅ Generates detailed test report
- ✅ Records to database

---

### Option 4: Use Frontend UI

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access UI**:
   - Open browser: `http://localhost:3000`
   - Click "Algorithm Viability" in navigation
   - Enter test content or generate synthetic data
   - Click "Run Viability Test"
   - View comprehensive results!

---

### Option 5: Use API Directly

```bash
# Test algorithm viability via API
curl -X POST "http://localhost:8000/api/v1/compression/algorithm-viability/test" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is test content for compression analysis. It contains repeated patterns and various structures to test algorithm performance.",
    "include_experimental": false
  }'

# Get algorithm capabilities
curl "http://localhost:8000/api/v1/compression/algorithm-viability/capabilities"

# Get recommendations
curl "http://localhost:8000/api/v1/compression/algorithm-viability/recommendations?content_size=1024&content_type=text&priority=balanced"
```

---

## 📊 View Results

### 1. View Generated Reports

```bash
# View latest test report
cd backend/tests/test_results
ls -lt viability_report_*.json | head -1
cat [filename]
```

### 2. Query Meta-Learning Database

```python
from app.services.meta_learning_service import get_meta_learning_service

service = get_meta_learning_service()

# Get database statistics
stats = service.get_database_statistics()
print(f"Total tests: {stats['total_tests']}")
print(f"Success rate: {stats['success_rate']:.1f}%")

# Get algorithm performance
gzip_stats = service.get_algorithm_statistics(algorithm='gzip')
print(f"GZIP average ratio: {gzip_stats[0]['avg_compression_ratio']:.2f}x")

# Get recent tests
recent = service.get_recent_tests(limit=10, success_only=True)
for test in recent:
    print(f"{test['algorithm']}: {test['compression_ratio']:.2f}x on {test['content_type']}")
```

### 3. View in Frontend

Navigate to: **Algorithm Viability** tab → **Results** view

View:
- ✅ Best compression ratio
- ✅ Fastest algorithm  
- ✅ Best balanced performer
- ✅ Detailed results table
- ✅ Viability ratings
- ✅ Recommendations

---

## 🧪 Test Specific Scenarios

### Test Specific Content Type

```python
# Create custom test
from test_data.mock_compression_data import MockDataGenerator

generator = MockDataGenerator()

# Test JSON compression
json_data = generator.generate_json_data(size_kb=50)

# Test with GZIP
from app.core.compression_engine import CompressionEngine
from app.models.compression import CompressionRequest, CompressionParameters, CompressionAlgorithm

engine = CompressionEngine()
request = CompressionRequest(
    content=json_data.content,
    parameters=CompressionParameters(algorithm=CompressionAlgorithm.GZIP, level=6)
)

response = await engine.compress(request)
print(f"Compression ratio: {response.result.compression_ratio:.2f}x")
```

### Test Specific Algorithm

```bash
# Test only GZIP
pytest tests/test_algorithm_viability_complete.py::TestAlgorithmViability::test_gzip_algorithm_viability -v

# Test only LZMA
pytest tests/test_algorithm_viability_complete.py::TestAlgorithmViability::test_lzma_algorithm_viability -v
```

### Test Different Complexity Levels

```python
# Generate different complexity levels
generator = MockDataGenerator()

minimal = generator.generate_highly_repetitive_text(10)
high = generator.generate_high_entropy_data(10)

# Test both
# ... compression code ...
```

---

## 📈 Monitor Meta-Learning Progress

### Check Database Growth

```python
from app.services.meta_learning_service import get_meta_learning_service

service = get_meta_learning_service()

# Get statistics
stats = service.get_database_statistics()

print(f"""
Meta-Learning Database Statistics:
- Total compression tests: {stats['total_tests']:,}
- Successful tests: {stats['successful_tests']:,}
- Success rate: {stats['success_rate']:.1f}%
- Unique algorithms: {stats['unique_algorithms']}
- Unique content types: {stats['unique_content_types']}
- Total viability analyses: {stats['total_viability_analyses']}
- Total learning insights: {stats['total_learning_insights']}
""")
```

### View Learning Insights

```python
# Algorithm performance by content type
text_stats = service.get_algorithm_statistics(content_type='text')
json_stats = service.get_algorithm_statistics(content_type='json')

print("Best algorithm for text:", max(text_stats, key=lambda x: x['avg_compression_ratio'])['algorithm'])
print("Best algorithm for JSON:", max(json_stats, key=lambda x: x['avg_compression_ratio'])['algorithm'])
```

---

## 🔍 Troubleshooting

### Issue: Tests fail with "module not found"

**Solution**:
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python tests/run_comprehensive_algorithm_viability_tests.py
```

### Issue: Database locked

**Solution**:
```bash
# Stop all running processes
# Wait a few seconds
# Retry the test
```

### Issue: Frontend can't connect to API

**Solution**:
```bash
# Ensure backend is running
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ensure frontend proxy is configured (should be automatic)
cd frontend
npm run dev
```

### Issue: Experimental algorithms fail

**Expected Behavior**: Experimental algorithms (quantum_biological, neuromorphic, topological) may have lower success rates. This is normal - they're research-grade implementations.

---

## 📚 Next Steps

After running the tests:

1. ✅ **Review Reports**: Check generated JSON reports in `backend/tests/test_results/`
2. ✅ **Query Database**: Use meta-learning service to analyze trends
3. ✅ **View Frontend**: See visualizations in Algorithm Viability tab
4. ✅ **Run More Tests**: Add your own content and test patterns
5. ✅ **Monitor Learning**: Watch as the system improves over time

---

## 🎯 Success Criteria

You'll know everything is working when you see:

✅ All tests pass (or only experimental ones fail)  
✅ Reports generated in `test_results/` directory  
✅ Database file `data/meta_learning.db` created and populated  
✅ Frontend tab displays without errors  
✅ API endpoints return valid JSON responses  
✅ Rankings show LZMA/BZIP2 highest for repetitive data  
✅ Rankings show LZ4 fastest  
✅ Meta-learning statistics show growing dataset  

---

## 💡 Tips

- **First Run**: Takes ~30-60 seconds to test all algorithms
- **Subsequent Runs**: Faster with warmed-up cache
- **Large Content**: Use smaller test cases for faster iteration
- **Custom Data**: Modify `mock_compression_data.py` to add new patterns
- **Frontend**: Use "Generate Synthetic Data" button for quick testing

---

## 🎉 You're All Set!

Start with:
```bash
cd backend
python tests/run_comprehensive_algorithm_viability_tests.py
```

Then explore the frontend and API!

**Questions?** Check `ALGORITHM_VIABILITY_ANALYSIS_README.md` for detailed documentation.

