# System Metrics Verification Guide

Complete guide to verify every datapoint in the System Metrics tab is showing **real, live information**.

## Table of Contents
1. [Quick Start - Running Tests](#quick-start)
2. [Docker on Windows 10 Setup](#docker-windows-10)
3. [Verifying Each Metric](#verifying-each-metric)
4. [Automated Testing](#automated-testing)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start - Running Tests {#quick-start}

### Option 1: Automated Test Script (Recommended)

```bash
# From project root
cd backend
python scripts/test_all_metrics.py
```

This will:
- ✅ Test all metrics endpoints
- ✅ Compare API data with actual system metrics
- ✅ Validate data ranges and accuracy
- ✅ Generate detailed test report

### Option 2: Manual Verification

```bash
# Start the backend
cd backend
python main.py

# In another terminal, run the metrics test
pytest tests/test_metrics_accuracy.py -v
```

---

## Docker on Windows 10 Setup {#docker-windows-10}

### Prerequisites
- Docker Desktop for Windows 10
- WSL 2 backend enabled
- At least 4GB RAM allocated to Docker

### Step 1: Build and Start Containers

```bash
# Build the containers
docker-compose build

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 2: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Step 3: Run Tests in Docker

```bash
# Run automated tests inside the container
docker-compose exec backend python scripts/test_all_metrics.py

# Or run pytest
docker-compose exec backend pytest tests/test_metrics_accuracy.py -v
```

### Docker-Specific Metrics Notes

**Important**: When running in Docker on Windows, some metrics behave differently:

1. **CPU/Memory/Disk**: Show Docker container resources (not host Windows system)
2. **Processes**: Count processes inside the container only
3. **Network**: Container's virtual network interface
4. **Temperature**: Usually not available in containers (will show 0)

To see **host system metrics** instead:
```bash
# Add host network mode in docker-compose.yml (see below)
```

---

## Verifying Each Metric {#verifying-each-metric}

### Core System Metrics

#### 1. **CPU Usage** (%)
**Expected**: 0-100% showing real CPU utilization

**Verify Manually:**
```bash
# In Docker container:
docker-compose exec backend python -c "import psutil; print(f'CPU: {psutil.cpu_percent(interval=1)}%')"

# On Windows host:
# Open Task Manager > Performance > CPU
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.cpu_usage'
```

**Test Code:**
```python
import psutil
import requests

api_cpu = requests.get('http://localhost:8000/api/v1/metrics/system/comprehensive').json()['cpu_usage']
actual_cpu = psutil.cpu_percent(interval=1)
print(f"API: {api_cpu}%, Actual: {actual_cpu}%")
assert abs(api_cpu - actual_cpu) < 20, "CPU metric differs too much"
```

---

#### 2. **Memory Usage** (%)
**Expected**: 0-100% showing real memory utilization

**Verify Manually:**
```bash
# In Docker:
docker-compose exec backend python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# On Windows:
# Task Manager > Performance > Memory
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.memory_usage'
```

---

#### 3. **Disk Usage** (%)
**Expected**: 0-100% showing disk space used

**Verify Manually:**
```bash
# In Docker:
docker-compose exec backend python -c "import psutil; print(f'Disk: {psutil.disk_usage(\"/\").percent}%')"

# On Windows:
# File Explorer > This PC > Check C: drive
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.disk_usage'
```

---

#### 4. **Processes** Count
**Expected**: Real number of running processes (in container or on host)

**THIS WAS PREVIOUSLY MOCKED (100-300 random values)**  
**NOW SHOWS REAL DATA**

**Verify Manually:**
```bash
# In Docker container:
docker-compose exec backend python -c "import psutil; print(f'Processes: {len(psutil.pids())}')"

# On Windows host:
# Task Manager > Details tab > Count processes
# Or PowerShell:
(Get-Process).Count
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.processes'
```

**Typical Values:**
- Docker container: 20-50 processes
- Windows host: 200-400 processes
- Linux host: 100-300 processes

---

#### 5. **Threads** Count
**Expected**: Real number of threads

**Verify Manually:**
```bash
docker-compose exec backend python -c "import psutil; print(f'Threads: {sum([p.num_threads() for p in psutil.process_iter([\"num_threads\"]) if p.info.get(\"num_threads\")])}')"
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.threads'
```

---

#### 6. **Uptime** (seconds)
**Expected**: Real system/container uptime in seconds

**PREVIOUSLY MOCKED - NOW SHOWS REAL DATA**

**Verify Manually:**
```bash
# In Docker:
docker-compose exec backend python -c "import psutil, time; print(f'Uptime: {int(time.time() - psutil.boot_time())}s')"

# On Windows:
# Task Manager > Performance > CPU > Up time
# Or PowerShell:
(Get-Date) - (Get-CimInstance -Class Win32_OperatingSystem).LastBootUpTime
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.uptime'
```

**Convert to readable format:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.uptime' | awk '{print int($1/3600)"h "int(($1%3600)/60)"m"}'
```

---

#### 7. **Network Connections**
**Expected**: Real count of network connections

**Verify Manually:**
```bash
docker-compose exec backend python -c "import psutil; print(f'Connections: {len(psutil.net_connections())}')"

# Windows PowerShell:
(Get-NetTCPConnection).Count
```

**Verify via API:**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.network_connections'
```

---

### Detailed Hardware Metrics

#### 8. **CPU Details**
```bash
# Get detailed CPU info
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.cpu_details'
```

**Fields:**
- `cores`: Physical CPU cores
- `threads`: Logical processors  
- `frequency`: Current CPU frequency (MHz)
- `temperature`: CPU temp (°C) - may be 0 in Docker
- `usage_per_cpu`: Per-core usage percentages
- `load`: Load average [1min, 5min, 15min]

**Verify:**
```bash
docker-compose exec backend python -c "import psutil; print(f'Cores: {psutil.cpu_count(logical=False)}, Threads: {psutil.cpu_count()}')"
```

---

#### 9. **Memory Details**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.memory_details'
```

**Fields:**
- `total`: Total RAM (bytes)
- `available`: Available RAM (bytes)
- `used`: Used RAM (bytes)
- `free`: Free RAM (bytes)
- `cached`: Cached memory (bytes)
- `buffers`: Buffer memory (bytes)
- `swap_*`: Swap memory details

**Verify:**
```bash
docker-compose exec backend python -c "import psutil; mem=psutil.virtual_memory(); print(f'Total: {mem.total/(1024**3):.2f}GB, Used: {mem.used/(1024**3):.2f}GB')"
```

---

#### 10. **Network Details**
```bash
curl http://localhost:8000/api/v1/metrics/system/comprehensive | jq '.network_details'
```

**Fields:**
- `bytes_sent`: Total bytes sent
- `bytes_recv`: Total bytes received
- `packets_sent`: Total packets sent
- `packets_recv`: Total packets received
- `errors_in/out`: Network errors
- `drops_in/out`: Dropped packets
- `interfaces`: Per-interface statistics

**Verify:**
```bash
docker-compose exec backend python -c "import psutil; net=psutil.net_io_counters(); print(f'Sent: {net.bytes_sent/(1024**2):.2f}MB, Received: {net.bytes_recv/(1024**2):.2f}MB')"
```

---

### Compression Metrics

These come from actual compression operations in your application:

#### 11. **Throughput** (MB/s)
**Source**: Real compression operations per second × 100

#### 12. **Success Rate** (%)
**Source**: (Successful compressions / Total compressions) × 100

#### 13. **Compression Efficiency** (%)
**Source**: (Average compression ratio / 3.0) × 100

#### 14. **Response Time** (ms)
**Source**: Average time to complete compression requests

**Verify these by performing compressions:**
```bash
# Perform a compression
curl -X POST http://localhost:8000/api/v1/compression/compress \
  -H "Content-Type: application/json" \
  -d '{"content": "test data", "algorithm": "gzip"}'

# Check updated metrics
curl http://localhost:8000/api/v1/metrics/dashboard | jq '.overview'
```

---

## Automated Testing {#automated-testing}

### Run Full Test Suite

```bash
# From backend directory
python scripts/test_all_metrics.py --url http://localhost:8000
```

**Output Example:**
```
================================================================================
Testing: Comprehensive System Metrics
Endpoint: GET /api/v1/metrics/system/comprehensive
================================================================================
✓ Endpoint accessible
✓ Response received (HTTP 200)
CPU Usage: 45.2% (actual: 43.8%)
Memory Usage: 62.5% (actual: 61.2%)
Processes: 156 (actual: 152)
Uptime: 86420s (24.0h) (actual: 86418s)
...

✓ Comprehensive System Metrics PASSED
```

### Run Pytest Suite

```bash
# Run specific test
pytest tests/test_metrics_accuracy.py::TestMetricsAccuracy::test_cpu_usage_accuracy -v

# Run all metrics tests
pytest tests/test_metrics_accuracy.py -v

# Generate HTML report
pytest tests/test_metrics_accuracy.py --html=metrics_test_report.html
```

---

## Comparison: Mocked vs Real Data {#comparison}

### Previously Mocked Data (OLD)
| Metric | Old Behavior | Type |
|--------|--------------|------|
| Processes | `100 + random() * 200` | ❌ MOCKED |
| Threads | `500 + random() * 1000` | ❌ MOCKED |
| Uptime | `86400 + random() * 86400` | ❌ MOCKED |
| Temperature | `45 + random() * 20` | ❌ MOCKED |
| Open Files | `1000 + random() * 5000` | ❌ MOCKED |
| Network Latency | `20 + random() * 30` | ❌ MOCKED |
| Load Average | `[random(), random(), random()]` | ❌ MOCKED |

### Current Real Data (NEW)
| Metric | New Behavior | Type |
|--------|--------------|------|
| Processes | `len(psutil.pids())` | ✅ REAL |
| Threads | Sum of all thread counts | ✅ REAL |
| Uptime | `time.time() - psutil.boot_time()` | ✅ REAL |
| Temperature | `psutil.sensors_temperatures()` | ✅ REAL (or 0 if unavailable) |
| Open Files | Count from all processes | ✅ REAL |
| Network Latency | 0 (not available from psutil) | ✅ HONEST ZERO |
| Load Average | `psutil.getloadavg()` | ✅ REAL |

---

## Windows 10 Docker Specific Instructions {#docker-windows-10}

### Getting Host System Metrics in Docker

By default, Docker containers show **container metrics**, not host metrics. To access host system metrics:

#### Option 1: Use Host Network Mode
```yaml
# docker-compose.yml
services:
  backend:
    network_mode: "host"
    privileged: true  # Required for some system metrics
```

#### Option 2: Mount Host Proc Filesystem (Linux only)
```yaml
services:
  backend:
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
```

#### Option 3: Run Tests on Host
```bash
# Install dependencies on Windows
pip install -r backend/requirements.txt

# Run backend directly
cd backend
python main.py

# Run tests
python scripts/test_all_metrics.py
```

### Viewing Container vs Host Metrics

**Container Metrics (default):**
```bash
docker-compose exec backend python -c "import psutil; print(f'Container Processes: {len(psutil.pids())}')"
```

**Host Metrics (PowerShell on Windows):**
```powershell
# Processes
(Get-Process).Count

# CPU Usage
Get-Counter '\Processor(_Total)\% Processor Time'

# Memory
$os = Get-CimInstance Win32_OperatingSystem
$totalMem = $os.TotalVisibleMemorySize
$freeMem = $os.FreePhysicalMemory
[math]::Round((($totalMem - $freeMem) / $totalMem) * 100, 2)
```

---

## Troubleshooting {#troubleshooting}

### Issue: All Metrics Show Zero

**Cause**: Backend not running or API not accessible

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Docker containers
docker-compose ps

# View backend logs
docker-compose logs backend

# Restart services
docker-compose restart
```

### Issue: Temperature Always Zero

**Cause**: Temperature sensors not available in Docker containers or unsupported hardware

**Solution**: This is normal in Docker. Temperature is only available:
- On physical Linux systems with sensor drivers
- Some Windows systems with HWiNFO/OpenHardwareMonitor
- Not typically available in VMs or containers

### Issue: Process Count Lower Than Expected

**Cause**: Running in Docker container (only shows container processes)

**Solution**: This is expected. Container has fewer processes than host. To verify:
```bash
# Container processes (Docker)
docker-compose exec backend python -c "import psutil; print(len(psutil.pids()))"

# Host processes (Windows)
(Get-Process).Count  # PowerShell
```

### Issue: Tests Fail with "Connection Refused"

**Cause**: Backend not accessible on localhost:8000

**Solution**:
```bash
# Check Docker port mapping
docker-compose ps

# Verify port 8000 is exposed
docker-compose logs backend | grep "Uvicorn running"

# Test direct connection
curl -v http://localhost:8000/health
```

---

## Continuous Verification {#continuous}

### Setup Automated Monitoring

Create a cron job or scheduled task to run tests regularly:

**Linux/WSL:**
```bash
# Add to crontab
0 * * * * cd /path/to/project && docker-compose exec -T backend python scripts/test_all_metrics.py
```

**Windows Task Scheduler:**
```powershell
# Create scheduled task to run daily
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-File C:\path\to\run_metrics_tests.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MetricsValidation"
```

---

## Summary Checklist

✅ All metrics endpoints accessible  
✅ CPU, Memory, Disk show real percentages  
✅ **Processes show real count (not 100-300 random)**  
✅ **Uptime shows real system uptime**  
✅ Threads count is real  
✅ Network connections are real  
✅ Detailed metrics (CPU/Memory/Network) populated  
✅ Compression metrics based on actual operations  
✅ No mocked/random data (zeros mean "not available")  
✅ Tests pass in Docker on Windows 10  
✅ API responses match psutil readings  

---

## Need Help?

1. Check logs: `docker-compose logs backend`
2. Run diagnostics: `python scripts/test_all_metrics.py`
3. Verify psutil works: `python -c "import psutil; psutil.cpu_percent()"`
4. Check API docs: http://localhost:8000/docs

