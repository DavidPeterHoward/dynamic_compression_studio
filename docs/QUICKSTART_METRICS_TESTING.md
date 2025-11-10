# Quick Start: Verify All Metrics Are Real

## 🚀 Fastest Way to Test (Windows 10)

```powershell
# Run this command from project root:
.\test_metrics_windows.ps1
```

This script will:
1. ✅ Verify Docker is running
2. ✅ Start containers if needed
3. ✅ Run automated tests
4. ✅ Compare container vs host metrics
5. ✅ Validate all datapoints are real

---

## 🐧 Linux / macOS

```bash
# Start services
docker-compose up -d

# Run tests
docker-compose exec backend python scripts/test_all_metrics.py
```

---

## 🧪 What Gets Tested

### System Metrics (All REAL data)
- [x] CPU Usage (%)
- [x] Memory Usage (%)
- [x] Disk Usage (%)
- [x] Network Usage (%)
- [x] **Processes** (was mocked, now REAL)
- [x] **Threads** (was mocked, now REAL)
- [x] **Uptime** (was mocked, now REAL)
- [x] Open Files
- [x] Network Connections

### Hardware Details (All REAL data)
- [x] CPU cores, threads, frequency
- [x] Memory total, used, free, cached
- [x] Disk total, used, free
- [x] Network bytes sent/received
- [x] Load average

### Compression Metrics (From actual operations)
- [x] Throughput (MB/s)
- [x] Success Rate (%)
- [x] Compression Efficiency (%)
- [x] Response Time (ms)
- [x] Algorithm Performance

---

## 📊 Expected Output

```
================================================================================
COMPREHENSIVE METRICS VALIDATION SUITE
Testing API at: http://localhost:8000
================================================================================

✓ API is accessible and healthy

================================================================================
Testing: Comprehensive System Metrics
================================================================================
✓ Endpoint accessible
✓ Response received (HTTP 200)
CPU Usage: 45.2% (actual: 43.8%)
Memory Usage: 62.5% (actual: 61.2%)
Disk Usage: 78.3% (actual: 78.1%)
Processes: 156 (actual: 152)
Threads: 842 (actual: 838)
Uptime: 86420s (24.0h) (actual: 86418s)
Network Connections: 234
CPU Cores: 8
Total Memory: 15.89 GB
Bytes Sent: 1245.67 MB

✓ Comprehensive System Metrics PASSED

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 3
✓ Passed: 3
✗ Failed: 0
Success Rate: 100.0%
```

---

## ✅ Key Improvements Made

| Metric | Before | After |
|--------|--------|-------|
| **Processes** | ❌ `100 + random()*200` | ✅ `len(psutil.pids())` |
| **Threads** | ❌ `500 + random()*1000` | ✅ Real count from all processes |
| **Uptime** | ❌ `86400 + random()*86400` | ✅ `time.time() - psutil.boot_time()` |
| **Temperature** | ❌ `45 + random()*20` | ✅ Real (or 0 if unavailable) |
| **Open Files** | ❌ `1000 + random()*5000` | ✅ Real count from processes |
| **Load Average** | ❌ Random array | ✅ `psutil.getloadavg()` |
| **Memory Details** | ❌ Random values | ✅ Real from `psutil.virtual_memory()` |
| **CPU Details** | ❌ Random values | ✅ Real from `psutil.cpu_*()` |
| **Network Details** | ❌ Random values | ✅ Real from `psutil.net_*()` |

---

## 📖 Full Documentation

See [METRICS_VERIFICATION_GUIDE.md](METRICS_VERIFICATION_GUIDE.md) for:
- Detailed verification procedures
- How to test each individual metric
- Docker on Windows 10 specific instructions
- Troubleshooting guide
- Continuous monitoring setup

---

## 🔍 Manual Verification Examples

### Check Processes (Docker container)
```bash
docker-compose exec backend python -c "import psutil; print(f'Processes: {len(psutil.pids())}')"
```

### Check Uptime (Docker container)
```bash
docker-compose exec backend python -c "import psutil, time; print(f'Uptime: {int(time.time() - psutil.boot_time())}s')"
```

### Check via API
```bash
# Get all metrics
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq

# Get specific value
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.processes'
```

### Check on Windows Host
```powershell
# Processes
(Get-Process).Count

# Uptime
$os = Get-CimInstance Win32_OperatingSystem
$uptime = (Get-Date) - $os.LastBootUpTime
$uptime.TotalSeconds
```

---

## 🐛 Troubleshooting

### "Docker is not running"
```powershell
# Start Docker Desktop and wait for it to be ready
```

### "Cannot access API"
```bash
# Check if backend is running
docker-compose ps

# View logs
docker-compose logs backend

# Restart
docker-compose restart backend
```

### "All metrics show 0"
```bash
# Backend might not be fully started
docker-compose logs backend | grep "Uvicorn running"

# Wait 10 seconds after startup
Start-Sleep -Seconds 10
```

---

## 📝 Test Results Location

After running tests, results are saved to:
- `backend/metrics_test_results_YYYYMMDD_HHMMSS.json`

---

## 🎯 Success Criteria

✅ **ALL metrics must show real data or 0 (not random values)**  
✅ **Processes must be actual count (not 100-300 random)**  
✅ **Uptime must match system uptime**  
✅ **API values should match psutil within tolerance**  
✅ **Tests pass with 100% success rate**  

---

## Questions?

1. Run the tests: `.\test_metrics_windows.ps1`
2. Check the guide: [METRICS_VERIFICATION_GUIDE.md](METRICS_VERIFICATION_GUIDE.md)
3. View API docs: http://localhost:8000/docs
4. Check test results JSON file

