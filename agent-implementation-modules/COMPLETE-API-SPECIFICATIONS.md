# COMPLETE API SPECIFICATIONS
## Exhaustive REST API & WebSocket Specifications

**Document Purpose:** Complete API specifications with all parameters, schemas, examples  
**Date:** 2025-10-30  
**API Version:** v1  
**Base URL:** `http://localhost:8000/api/v1`  
**Coverage:** All endpoints with request/response schemas, validation, error handling  

---

## 📋 TABLE OF CONTENTS

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Request/Response Format](#requestresponse-format)
4. [Tasks Endpoints](#tasks-endpoints)
5. [Agents Endpoints](#agents-endpoints)
6. [Metrics Endpoints](#metrics-endpoints)
7. [WebSocket API](#websocket-api)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Examples & Code Samples](#examples--code-samples)

---

## API OVERVIEW

### Base Information

**Protocol:** HTTP/1.1, HTTP/2  
**Format:** JSON (application/json)  
**Character Encoding:** UTF-8  
**Date Format:** ISO 8601 (YYYY-MM-DDTHH:MM:SS.sssZ)  
**Time Zone:** UTC  

**Headers (Required):**
```http
Content-Type: application/json
Accept: application/json
```

**Headers (Optional):**
```http
Authorization: Bearer <token>  (Phase 2)
X-Request-ID: <uuid>          (for tracking)
X-Client-Version: <version>   (for compatibility)
```

---

## TASKS ENDPOINTS

### POST /api/v1/tasks

**Purpose:** Create a new task for execution

**HTTP Method:** POST  
**URL:** `/api/v1/tasks`  
**Authentication:** None (MVP) | Bearer Token (Phase 2)  
**Rate Limit:** 100 requests/minute per IP  

#### Request Specification

**Headers:**
```http
POST /api/v1/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Content-Length: <length>
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Request Body Schema:**
```typescript
interface CreateTaskRequest {
    // REQUIRED FIELDS
    type: string;              // Task type identifier
    input: object;             // Task input data
    
    // OPTIONAL FIELDS
    priority?: number;         // 1-10, default: 5
    max_retries?: number;      // 0-10, default: 3
    parameters?: object;       // Task-specific parameters
    metadata?: object;         // Custom metadata
    parent_task_id?: string;   // UUID of parent task
}
```

**Field Specifications:**

**Field: type**
- **Type:** string
- **Required:** YES
- **Nullable:** NO
- **Constraints:**
  - Length: 3-50 characters
  - Pattern: `^[a-z0-9_]+$`
  - Must exist in task_types registry
- **Valid Values:**
  ```
  text_analysis, text_generation, translation,
  code_generation, code_analysis, code_optimization,
  data_processing, data_analysis, data_visualization,
  research, summarization, multi_step, pipeline
  ```
- **Examples:**
  - Valid: `"text_analysis"`, `"code_generation"`, `"data_processing"`
  - Invalid: `"TextAnalysis"` (uppercase), `"text-analysis"` (hyphen), `"xyz"` (not registered)

**Field: input**
- **Type:** object
- **Required:** YES
- **Nullable:** NO
- **Constraints:**
  - Must be valid JSON object
  - Cannot be empty object `{}`
  - Size limit: 1MB
  - Required keys depend on task type
- **Schema by Task Type:**

  **For type="text_analysis":**
  ```typescript
  {
    text: string;                    // REQUIRED: Text to analyze
    analysis_types?: string[];       // Optional: ["sentiment", "entities", "keywords"]
    language?: string;               // Optional: "en", "es", etc. Default: "en"
    confidence_threshold?: number;   // Optional: 0.0-1.0, Default: 0.8
  }
  ```

  **For type="code_generation":**
  ```typescript
  {
    specification: string;           // REQUIRED: What to generate
    language: string;                // REQUIRED: "python", "javascript", etc.
    include_tests?: boolean;         // Optional: Generate tests, Default: false
    style_guide?: string;            // Optional: "PEP8", "airbnb", etc.
    max_lines?: number;              // Optional: Max lines of code
  }
  ```

  **For type="data_processing":**
  ```typescript
  {
    data: any[] | object;            // REQUIRED: Data to process
    operations: string[];            // REQUIRED: ["normalize", "filter", etc.]
    output_format?: string;          // Optional: "json", "csv", Default: "json"
    filters?: object;                // Optional: Filtering criteria
  }
  ```

**Field: priority**
- **Type:** integer
- **Required:** NO
- **Default:** 5
- **Nullable:** NO
- **Constraints:**
  - Range: 1-10 (1=highest priority, 10=lowest)
  - Must be integer
- **Priority Levels:**
  ```
  1-2:  Critical (SLA: < 10s)
  3-4:  High     (SLA: < 30s)
  5-6:  Normal   (SLA: < 60s)
  7-8:  Low      (SLA: < 300s)
  9-10: Background (SLA: < 3600s)
  ```
- **Examples:**
  - Critical task: `"priority": 1`
  - Normal task: `"priority": 5` or omit
  - Background task: `"priority": 9`

**Field: max_retries**
- **Type:** integer
- **Required:** NO
- **Default:** 3
- **Nullable:** NO
- **Constraints:**
  - Range: 0-10
  - Must be integer
- **Retry Strategy:**
  - Attempt 0: Immediate execution
  - Attempt 1: Retry after 1 second
  - Attempt 2: Retry after 2 seconds
  - Attempt 3: Retry after 4 seconds
  - Attempt N: Retry after 2^(N-1) seconds (exponential backoff)
- **Examples:**
  - No retries: `"max_retries": 0`
  - Default: `"max_retries": 3` or omit
  - Maximum: `"max_retries": 10`

**Complete Request Examples:**

**Example 1: Text Analysis (Minimal)**
```json
{
  "type": "text_analysis",
  "input": {
    "text": "This product is amazing! I love it."
  }
}
```

**Example 2: Text Analysis (Complete)**
```json
{
  "type": "text_analysis",
  "input": {
    "text": "This product is amazing! I love it.",
    "analysis_types": ["sentiment", "entities", "keywords"],
    "language": "en",
    "confidence_threshold": 0.85
  },
  "priority": 3,
  "max_retries": 5,
  "metadata": {
    "user_id": "user_12345",
    "source": "product_reviews",
    "batch_id": "batch_001"
  }
}
```

**Example 3: Code Generation**
```json
{
  "type": "code_generation",
  "input": {
    "specification": "Create a function to calculate fibonacci numbers using memoization",
    "language": "python",
    "include_tests": true,
    "style_guide": "PEP8",
    "max_lines": 100
  },
  "priority": 4,
  "parameters": {
    "optimization_level": "high",
    "add_docstrings": true,
    "type_hints": true
  }
}
```

**Example 4: Data Processing with Parent**
```json
{
  "type": "data_processing",
  "input": {
    "data": [
      {"id": 1, "value": 10},
      {"id": 2, "value": 20},
      {"id": 3, "value": 30}
    ],
    "operations": ["normalize", "filter_outliers"],
    "output_format": "json"
  },
  "priority": 5,
  "parent_task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response Specification

**Success Response (201 Created):**

**Status Code:** 201 Created  
**Headers:**
```http
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Location: /api/v1/tasks/c4c8f8d0-1234-5678-90ab-cdef12345678
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time-Ms: 45
```

**Response Body Schema:**
```typescript
interface CreateTaskResponse {
    // Task Identification
    id: string;                    // UUID of created task
    type: string;                  // Task type (echoed)
    status: string;                // Current status (always "pending")
    
    // Execution Details
    priority: number;              // Execution priority (1-10)
    max_retries: number;           // Maximum retry attempts
    retry_count: number;           // Current retry count (always 0)
    
    // Data (as provided)
    input: object;                 // Task input (echoed)
    parameters: object | null;     // Task parameters (echoed)
    metadata: object;              // Task metadata (echoed)
    
    // Relationships
    agent_id: string | null;       // Assigned agent (null initially)
    parent_task_id: string | null; // Parent task UUID or null
    
    // Timestamps
    created_at: string;            // ISO 8601 timestamp (UTC)
    updated_at: string;            // ISO 8601 timestamp (UTC)
    started_at: string | null;     // null (not started yet)
    completed_at: string | null;   // null (not completed yet)
    
    // Computed
    execution_time: number | null; // null (not executed yet)
    wait_time: number | null;      // null (not started yet)
    
    // API Metadata
    _links: {
        self: string;              // Link to this task
        parent?: string;           // Link to parent task (if exists)
    }
}
```

**Response Example:**
```json
{
  "id": "c4c8f8d0-1234-5678-90ab-cdef12345678",
  "type": "text_analysis",
  "status": "pending",
  "priority": 3,
  "max_retries": 5,
  "retry_count": 0,
  "input": {
    "text": "This product is amazing! I love it.",
    "analysis_types": ["sentiment", "entities", "keywords"],
    "language": "en",
    "confidence_threshold": 0.85
  },
  "parameters": null,
  "metadata": {
    "user_id": "user_12345",
    "source": "product_reviews",
    "batch_id": "batch_001"
  },
  "agent_id": null,
  "parent_task_id": null,
  "created_at": "2025-10-30T12:34:56.789Z",
  "updated_at": "2025-10-30T12:34:56.789Z",
  "started_at": null,
  "completed_at": null,
  "execution_time": null,
  "wait_time": null,
  "_links": {
    "self": "/api/v1/tasks/c4c8f8d0-1234-5678-90ab-cdef12345678"
  }
}
```

#### Error Responses

**400 Bad Request - Invalid Input:**
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed for request body",
    "details": [
      {
        "field": "type",
        "message": "Task type 'invalid_type' is not registered",
        "constraint": "Must be one of: text_analysis, text_generation, ..."
      },
      {
        "field": "input",
        "message": "Required field 'text' is missing for task type 'text_analysis'",
        "constraint": "input must include: text"
      },
      {
        "field": "priority",
        "message": "Priority must be between 1 and 10, got 15",
        "constraint": "1 <= priority <= 10"
      }
    ],
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**400 Bad Request - Invalid JSON:**
```json
{
  "error": {
    "code": "INVALID_JSON",
    "message": "Failed to parse request body as JSON",
    "details": "Unexpected token } in JSON at position 45",
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**404 Not Found - Parent Task:**
```json
{
  "error": {
    "code": "PARENT_NOT_FOUND",
    "message": "Parent task not found",
    "details": {
      "parent_task_id": "nonexistent-uuid",
      "suggestion": "Verify parent_task_id is correct and parent task exists"
    },
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**413 Payload Too Large:**
```json
{
  "error": {
    "code": "PAYLOAD_TOO_LARGE",
    "message": "Request body exceeds maximum size",
    "details": {
      "max_size_bytes": 1048576,
      "actual_size_bytes": 2097152,
      "max_size_human": "1 MB",
      "actual_size_human": "2 MB"
    },
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**429 Too Many Requests:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    },
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal server error occurred",
    "details": "Contact support with request_id if issue persists",
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

### GET /api/v1/tasks/{id}

**Purpose:** Retrieve task details by ID

**HTTP Method:** GET  
**URL:** `/api/v1/tasks/{id}`  
**Authentication:** None (MVP) | Bearer Token (Phase 2)  
**Rate Limit:** 1000 requests/minute per IP  

#### Request Specification

**Path Parameters:**

**Parameter: id**
- **Type:** string (UUID)
- **Required:** YES
- **Format:** UUID v4 (8-4-4-4-12 hexadecimal)
- **Example:** `c4c8f8d0-1234-5678-90ab-cdef12345678`
- **Validation:**
  ```typescript
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    throw new Error("Invalid UUID format");
  }
  ```

**Query Parameters:**

**Parameter: include**
- **Type:** string (comma-separated)
- **Required:** NO
- **Default:** none
- **Options:**
  - `dependencies`: Include dependency tasks
  - `subtasks`: Include child tasks
  - `agent`: Include agent details
  - `metrics`: Include execution metrics
- **Examples:**
  - Single: `?include=dependencies`
  - Multiple: `?include=dependencies,subtasks,agent`

**Headers:**
```http
GET /api/v1/tasks/c4c8f8d0-1234-5678-90ab-cdef12345678?include=agent,metrics HTTP/1.1
Host: localhost:8000
Accept: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

#### Response Specification

**Success Response (200 OK):**

**Status Code:** 200 OK  
**Headers:**
```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Cache-Control: private, max-age=10
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time-Ms: 12
```

**Response Body Schema:**
```typescript
interface GetTaskResponse {
    // Same as CreateTaskResponse, but with updated fields
    id: string;
    type: string;
    status: string;              // May be different from "pending"
    priority: number;
    max_retries: number;
    retry_count: number;
    input: object;
    output: object | null;       // Task output (if completed)
    parameters: object | null;
    metadata: object;
    error_message: string | null; // Error message (if failed)
    error_details: object | null; // Detailed error info
    agent_id: string | null;      // Assigned agent ID (if assigned)
    parent_task_id: string | null;
    created_at: string;
    updated_at: string;
    started_at: string | null;    // When execution started
    completed_at: string | null;  // When execution completed
    execution_time: number | null; // Seconds (if completed)
    wait_time: number | null;      // Seconds (if started)
    
    // Included data (based on ?include parameter)
    _embedded?: {
        dependencies?: GetTaskResponse[];
        subtasks?: GetTaskResponse[];
        agent?: AgentResponse;
        metrics?: TaskMetricsResponse;
    };
    
    _links: {
        self: string;
        parent?: string;
        dependencies?: string;
        subtasks?: string;
    };
}
```

**Response Example (Completed Task):**
```json
{
  "id": "c4c8f8d0-1234-5678-90ab-cdef12345678",
  "type": "text_analysis",
  "status": "completed",
  "priority": 3,
  "max_retries": 5,
  "retry_count": 0,
  "input": {
    "text": "This product is amazing! I love it.",
    "analysis_types": ["sentiment", "entities", "keywords"],
    "language": "en",
    "confidence_threshold": 0.85
  },
  "output": {
    "sentiment": {
      "label": "positive",
      "score": 0.98,
      "confidence": 0.95
    },
    "entities": [
      {"text": "product", "type": "PRODUCT", "confidence": 0.87}
    ],
    "keywords": ["amazing", "love", "product"],
    "summary": "Highly positive sentiment detected with high confidence"
  },
  "parameters": null,
  "metadata": {
    "user_id": "user_12345",
    "source": "product_reviews",
    "batch_id": "batch_001"
  },
  "error_message": null,
  "error_details": null,
  "agent_id": "nlp_agent_001",
  "parent_task_id": null,
  "created_at": "2025-10-30T12:34:56.789Z",
  "updated_at": "2025-10-30T12:35:02.456Z",
  "started_at": "2025-10-30T12:34:57.123Z",
  "completed_at": "2025-10-30T12:35:02.456Z",
  "execution_time": 5.33,
  "wait_time": 0.33,
  "_embedded": {
    "agent": {
      "id": "nlp_agent_001",
      "name": "NLP Agent 1",
      "type": "NLPAgent",
      "status": "idle",
      "capabilities": [
        {"skill": "text_analysis", "proficiency": 0.95}
      ]
    }
  },
  "_links": {
    "self": "/api/v1/tasks/c4c8f8d0-1234-5678-90ab-cdef12345678"
  }
}
```

#### Error Responses

**404 Not Found:**
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task not found",
    "details": {
      "task_id": "c4c8f8d0-1234-5678-90ab-cdef12345678",
      "suggestion": "Verify task ID is correct"
    },
    "timestamp": "2025-10-30T12:34:56.789Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

**[Continuing with more endpoints: GET /tasks (list), PATCH /tasks/{id}, DELETE /tasks/{id}, etc.]**

This API specification document will continue with:
- All remaining task endpoints
- All agent endpoints
- All metrics endpoints
- Complete WebSocket API specification
- Error handling details
- Rate limiting specifications
- Complete code examples in multiple languages

Should I continue expanding this document, or would you like me to create additional specification documents for other components?

The complete API specifications would be approximately 10,000+ lines covering all endpoints in this level of detail.

