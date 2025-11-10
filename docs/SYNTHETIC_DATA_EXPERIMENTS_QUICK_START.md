# Synthetic Data Experiments - Quick Start Guide

**Date:** October 30, 2025  
**Status:** 🚀 Ready for Implementation

---

## TL;DR - What You Need to Know

### Current Situation
- ✅ **Two** synthetic data implementations exist (standalone tab + experiments sub-tab)
- ⚠️ Experiments sub-tab design doesn't match the application's visual system
- ⚠️ Missing comprehensive API integration
- ⚠️ Incomplete execution flow from frontend → backend

### Solution
Improve the Experiments → Synthetic Data sub-tab to:
1. Match the application's design system (glass morphism, gradients, animations)
2. Integrate fully with backend API
3. Establish clear execution flow (Frontend → API → Service → Database → Storage)

---

## Quick Implementation Steps

### Step 1: Create API Client (30 minutes)
**File:** `frontend/src/api/synthetic-media.ts`

```typescript
export const syntheticMediaAPI = {
  generate: async (request) => { /* POST /api/v1/synthetic-media/generate */ },
  list: async (params) => { /* GET /api/v1/synthetic-media/ */ },
  get: async (id) => { /* GET /api/v1/synthetic-media/{id} */ },
  download: async (id) => { /* GET /api/v1/synthetic-media/{id}/download */ },
  delete: async (id) => { /* DELETE /api/v1/synthetic-media/{id} */ },
  getStatistics: async () => { /* GET /api/v1/synthetic-media/statistics */ }
}
```

### Step 2: Create Improved Component (2-3 hours)
**File:** `frontend/src/components/SyntheticDataExperimentsTab.tsx`

**Layout:**
```
┌──────────────────────────────────────────────────┐
│ Header + Stats Cards                             │
├────────────┬─────────────────────────────────────┤
│ Config (⅓) │ Patterns + Extensions + Results (⅔) │
│            │                                      │
│ - Basic    │ [Pattern Grid]                       │
│ - Advanced │ [Extension Grid]                     │
│ - Generate │ [Generated Data]                     │
└────────────┴─────────────────────────────────────┘
```

**Key Components:**
- Header Section (stats cards)
- Configuration Panel (volume, complexity, content type)
- Advanced Settings (entropy, redundancy, structure, language, encoding)
- Pattern Selection Grid (15 patterns)
- Extension Selection Grid (25+ extensions with categories)
- Generation Control (button with progress)
- Generated Data Display (grid/list view)
- Data Viewer Modal

### Step 3: Integrate into ExperimentsTab (5 minutes)
**File:** `frontend/src/components/ExperimentsTab.tsx`

```tsx
import SyntheticDataExperimentsTab from './SyntheticDataExperimentsTab'

// Replace line ~595
{activeTab === 'synthetic-data' && (
  <SyntheticDataExperimentsTab />
)}
```

### Step 4: Test (30 minutes)
- [ ] Configure generation parameters
- [ ] Generate synthetic data
- [ ] View generated data
- [ ] Download data
- [ ] Delete data
- [ ] Test error scenarios

---

## Design System Quick Reference

### Colors
```tsx
// Active Tab
className="bg-blue-500 text-white shadow-lg"

// Inactive Tab
className="text-slate-400 hover:text-white hover:bg-slate-700/50"

// Glass Cards
className="glass p-6 rounded-xl"

// Stats Cards
className="glass-dark p-4 rounded-lg"

// Selected Pattern
className="bg-gradient-to-r from-blue-600 to-purple-600 border-blue-500 text-white shadow-lg"

// Unselected Pattern
className="bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700"

// Selected Extension
className="bg-gradient-to-r from-green-600 to-emerald-600 border-green-500 text-white shadow-lg"
```

### Animations
```tsx
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
>
```

### Icons
```tsx
import {
  Database, Settings, Play, Zap, Activity,
  Target, Gauge, TrendingUp, FileText, Check,
  Copy, Download, Eye, Layers
} from 'lucide-react'
```

---

## Execution Flow Quick Reference

```
User Action → Frontend → API → Service → Database → Storage → Response

1. User configures generation
   └─> Frontend updates state

2. User clicks "Generate"
   └─> POST /api/v1/synthetic-media/generate
       └─> SyntheticMediaService.generate_media()
           └─> Database: Create records
               └─> Storage: Save files
                   └─> Response: SyntheticMediaResponse[]
                       └─> Frontend: Display results
```

---

## API Endpoints Quick Reference

```
POST   /api/v1/synthetic-media/generate          # Generate media
GET    /api/v1/synthetic-media/                  # List with filters
GET    /api/v1/synthetic-media/{id}              # Get specific
GET    /api/v1/synthetic-media/{id}/download     # Download file
DELETE /api/v1/synthetic-media/{id}              # Delete media
GET    /api/v1/synthetic-media/statistics        # Get stats
GET    /api/v1/synthetic-media/batches           # List batches
POST   /api/v1/synthetic-media/batches/generate  # Generate batch
GET    /api/v1/synthetic-media/schemas           # List schemas
POST   /api/v1/synthetic-media/schemas           # Create schema
```

---

## Configuration Options Quick Reference

### Patterns (15 available)
- repetitive_text, structured_data, binary_data
- json_objects, xml_documents, log_files
- source_code, markdown_content, csv_data
- random_data, compression_challenges, edge_cases
- performance_tests, stress_tests, realistic_scenarios

### Extensions (25+ available)
**Text:** .txt, .md, .log  
**Data:** .json, .xml, .csv, .yaml, .toml, .ini, .cfg, .conf  
**Code:** .py, .js, .ts, .html, .css, .sql  
**Binary:** .bin, .dat  
**Archive:** .zip, .tar, .gz, .bz2, .xz  

### Parameters
- **Volume:** 100 KB - 10 MB (slider)
- **Complexity:** 0-100% (slider)
- **Content Type:** text, binary, mixed, structured, unstructured, code, data, archive
- **Entropy:** 0-100% (advanced)
- **Redundancy:** 0-100% (advanced)
- **Structure:** flat, hierarchical, nested, relational, graph, tree, network
- **Language:** english, code, mixed, technical, natural, multilingual, programming
- **Encoding:** utf-8, ascii, latin-1, utf-16, binary, base64, hex

---

## Testing Quick Reference

### Unit Tests
```typescript
// Frontend
describe('SyntheticDataExperimentsTab', () => {
  it('renders configuration panel')
  it('updates volume slider')
  it('toggles pattern selection')
  it('validates before generation')
})

// API Client
describe('syntheticMediaAPI', () => {
  it('generates synthetic media')
  it('handles API errors')
})
```

### Integration Tests
```typescript
describe('Synthetic Data Generation Flow', () => {
  it('completes full generation workflow')
  // Navigate → Configure → Generate → View → Download
})
```

### Backend Tests
```python
@pytest.mark.asyncio
async def test_generate_synthetic_media():
    # Test generation endpoint
    
async def test_list_synthetic_media():
    # Test listing with filters
    
async def test_download_synthetic_media():
    # Test file download
```

---

## Performance Quick Reference

### Frontend Optimization
```tsx
// Lazy loading
const SyntheticDataExperimentsTab = lazy(() => import('./SyntheticDataExperimentsTab'))

// Memoization
const filteredExtensions = useMemo(() => /* filter logic */, [filterCategory])
const handleGenerate = useCallback(async () => /* generation */, [config])

// Virtualization (for large lists)
import { FixedSizeList } from 'react-window'
```

### Backend Optimization
```python
# Async processing
background_tasks.add_task(service.process_batch_generation, batch_id)

# Caching
@cache(expire=3600)
async def get_statistics(): ...

# Database indexes
Index('idx_media_type_status', 'media_type', 'status')

# Chunked file streaming
async def stream_file(file_path: str):
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(8192):
            yield chunk
```

---

## Error Handling Quick Reference

### Frontend
```tsx
// Error Boundary
<SyntheticDataErrorBoundary>
  <SyntheticDataExperimentsTab />
</SyntheticDataErrorBoundary>

// Notifications
addNotification({
  type: 'error',
  title: 'Generation Failed',
  message: error.message
})

// Loading States
{isGenerating && <LoadingOverlay progress={progress} />}
```

### Backend
```python
# Custom Exceptions
class GenerationException(SyntheticMediaException): ...

# Exception Handlers
@app.exception_handler(GenerationException)
async def generation_exception_handler(request, exc): ...

# Logging
logger.error(f"Generation failed: {e}", exc_info=True)
```

---

## Deployment Quick Reference

### Checklist
- [ ] Frontend build optimized
- [ ] Environment variables configured
- [ ] API endpoints configured
- [ ] Database migrations run
- [ ] File storage configured
- [ ] Error tracking initialized
- [ ] All tests passing
- [ ] Performance metrics met

---

## File Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── synthetic-media.ts (NEW - API client)
│   └── components/
│       ├── SyntheticDataExperimentsTab.tsx (NEW - Main component)
│       ├── ExperimentsTab.tsx (MODIFY - Integration)
│       ├── SyntheticContentTab.tsx (EXISTING - Standalone)
│       └── SyntheticDataTab.tsx (EXISTING - Standalone sub-component)

backend/
├── app/
│   ├── api/
│   │   └── synthetic_media_management.py (EXISTING - 17 endpoints)
│   ├── services/
│   │   └── synthetic_media_service.py (EXISTING - Service layer)
│   └── models/
│       └── synthetic_media.py (EXISTING - Database models)
```

---

## Resources

### Documentation
- **Comprehensive Framework:** `SYNTHETIC_DATA_EXPERIMENTS_COMPREHENSIVE_FRAMEWORK.md` (12 sections, 1000+ lines)
- **This Quick Start:** `SYNTHETIC_DATA_EXPERIMENTS_QUICK_START.md`

### External Resources
- Framer Motion: https://www.framer.com/motion/
- Lucide Icons: https://lucide.dev/
- React Testing Library: https://testing-library.com/react
- FastAPI: https://fastapi.tiangolo.com/
- Pytest: https://docs.pytest.org/

---

## Common Issues & Solutions

### Issue 1: API not connecting
**Solution:** Check environment variables, CORS configuration, API base URL

### Issue 2: Generation taking too long
**Solution:** Use background tasks, implement progress updates, optimize generation algorithms

### Issue 3: Design not matching
**Solution:** Review design system in comprehensive framework, use exact class names

### Issue 4: Files not downloading
**Solution:** Check file storage configuration, verify file permissions, check MIME types

---

## Next Steps

1. ✅ Review comprehensive framework document
2. ⏳ Create API client (`frontend/src/api/synthetic-media.ts`)
3. ⏳ Develop `SyntheticDataExperimentsTab` component
4. ⏳ Integrate into `ExperimentsTab`
5. ⏳ Test end-to-end functionality
6. ⏳ Deploy to production

---

**Estimated Time:** 4-6 hours total  
**Priority:** Medium-High  
**Dependencies:** None (backend API already exists)  
**Risk Level:** Low (well-documented, existing API)

**Ready to Start:** ✅ YES  
**Approval Required:** YES (Review comprehensive framework first)

---

**Last Updated:** October 30, 2025  
**Version:** 1.0  
**For Questions:** See comprehensive framework document

