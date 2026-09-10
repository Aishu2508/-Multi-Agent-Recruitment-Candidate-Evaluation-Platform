# AI RECRUITMENT ASSESSMENT SYSTEM
## Official OpenAPI 3.1 Specification & API Technical Documentation

| Attribute | Value |
|---|---|
| **Project Title** | AI Recruitment Assessment System |
| **API Version** | 1.0.0 |
| **OpenAPI Specification** | OAS 3.1 |
| **Backend Framework** | FastAPI (Python 3.14) |
| **Database** | PostgreSQL / SQLite (via SQLAlchemy 2.0) |
| **Vector Database & RAG** | Qdrant / Embedded Vectors (`all-MiniLM-L6-v2`) |
| **Workflow Orchestration** | LangGraph State Machine with Human Checkpoints |
| **Server Base URL** | `http://localhost:8000` |
| **Interactive Swagger UI** | `http://localhost:8000/docs` |
| **Raw OpenAPI JSON Spec** | `http://localhost:8000/openapi.json` |

---

## 1. System Architecture & Workflow

The system provides an automated, unbiased candidate evaluation pipeline across seven functional modules:

```text
[ 1. Job Creation ]
       │
       ▼
[ 2. Resume Ingestion & Parsing ] ──▶ [ PII Anonymization (Fairness) ]
       │                                         │
       ▼                                         ▼
[ 3. Skill & RAG Vector Matching ] ◄─────────────┘
       │
       ▼
[ 4. Technical & Coding Assessment ]
       ├─ Adaptive Questions & Probing Follow-ups
       └─ Sandboxed Python/Java Code Runner (Time Complexity O(N))
       │
       ▼
[ 5. Audio & Communication Screening ]
       └─ Faster-Whisper Speech-to-Text & Clarity / Sentiment
       │
       ▼
[ 6. LangGraph Workflow & Scoring ]
       ├─ Fair Scoring Formula: Tech (40%) + Coding (40%) + Comm (20%)
       └─ HR Approval Checkpoint (Human-in-the-Loop)
       │
       ▼
[ 7. HR Dashboard & Realtime Notifications ]
       ├─ Python vs. Java Candidate Distribution Charts (Chart.js)
       ├─ Candidate Percentile Rankings
       └─ Shortlisting Alert Notifications
```

---

## 2. API Endpoints Directory (Organized by Tag)

```text
1. Job Management
   ├── POST /api/jobs                                 Create Job Requisition
   ├── GET  /api/jobs                                 List All Jobs
   └── GET  /api/jobs/{job_id}                        Get Job by ID

2. Candidate Ingestion & Resume Parsing
   ├── POST /api/candidates/upload                    Upload & Parse Resume (PDF/DOCX)
   ├── GET  /api/candidates                           List Candidates (Supports Fairness Anonymization)
   └── GET  /api/candidates/{candidate_id}            Get Candidate Profile

3. Matching & RAG Vector Search
   ├── POST /api/matching/match                       Match Candidate with Job Description
   └── POST /api/matching/search-resumes              Semantic Vector Search (RAG)

4. Technical & Coding Assessment
   ├── POST /api/assessment/start                     Initialize Assessment Session
   ├── GET  /api/assessment/coding-challenge          Get Coding Challenge (Python/Java)
   ├── POST /api/assessment/coding-submit             Submit & Execute Code in Sandbox
   ├── GET  /api/assessment/{id}/tech-questions       Generate Adaptive Tech Questions
   ├── POST /api/assessment/tech-answer               Submit Tech Answer & Receive Follow-up
   └── GET  /api/assessment/{id}                      Get Complete Assessment Audit Trail

5. Audio & Communication Screening
   └── POST /api/assessment/screening                 Evaluate Speech Clarity, Sentiment & Fillers

6. LangGraph Workflow & HR Checkpoints
   ├── POST /api/assessment/run-pipeline/{id}         Execute Multi-Stage LangGraph Pipeline
   └── POST /api/assessment/hr-checkpoint/{id}        HR Human-in-the-Loop Approval Checkpoint

7. Dashboard Analytics & Seed Data
   ├── GET  /api/dashboard/stats                      Retrieve Aggregated Recruitment Metrics
   ├── GET  /api/dashboard/ranked-candidates/{job_id} Get Candidate Ranking Pipeline
   ├── GET  /api/dashboard/notifications              Get Real-time HR Alerts Feed
   └── POST /api/seed-data                            Seed Sample Jobs and Candidates
```

---

## 3. Detailed Endpoint Specifications

### Section 1: Job Management

#### `POST /api/jobs`
- **Summary**: Create Job Requisition
- **Tag**: `1. Job Management`
- **Request Body** (`application/json`):
```json
{
  "title": "Senior Python AI Backend Engineer",
  "department": "Engineering",
  "description": "We are looking for an experienced Python backend engineer to build AI-powered recruitment systems using FastAPI, PostgreSQL, RAG, LangGraph, Docker, and REST APIs.",
  "required_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "REST API"
  ],
  "nice_to_have_skills": [
    "RAG",
    "LangGraph",
    "Redis",
    "Celery"
  ],
  "min_experience_years": 3,
  "min_score_threshold": 70.0,
  "primary_language": "Python"
}
```
- **Response 200 OK**:
```json
{
  "id": 3,
  "title": "Senior Python AI Backend Engineer",
  "department": "Engineering",
  "description": "We are looking for an experienced Python backend engineer to build AI-powered recruitment systems...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
  "nice_to_have_skills": ["RAG", "LangGraph", "Redis", "Celery"],
  "min_experience_years": 3,
  "min_score_threshold": 70.0,
  "primary_language": "Python",
  "created_at": "2026-09-10T15:20:00.000000"
}
```

#### `GET /api/jobs`
- **Summary**: List All Jobs
- **Tag**: `1. Job Management`
- **Response 200 OK**: Array of `JobResponse` objects.

#### `GET /api/jobs/{job_id}`
- **Summary**: Get Job by ID
- **Tag**: `1. Job Management`
- **Path Parameter**: `job_id` (integer, required)
- **Response 200 OK**: Single `JobResponse` object.

---

### Section 2: Candidate Ingestion & Resume Parsing

#### `POST /api/candidates/upload`
- **Summary**: Upload & Parse Candidate Resume
- **Tag**: `2. Candidate Ingestion & Resume Parsing`
- **Request Type**: `multipart/form-data`
- **Form Field**: `file` (Binary file: `.pdf`, `.docx`, or `.txt`)
- **Response 200 OK**:
```json
{
  "status": "success",
  "candidate": {
    "id": 5,
    "anonymized_id": "CAND-BFE650",
    "name": "Rahul Kumar",
    "email": "rahul.kumar@example.com",
    "phone": "+1 555-0199",
    "education": [
      "B.Tech in Computer Science, 2021"
    ],
    "experience_years": 5,
    "skills": [
      "Python", "FastAPI", "PostgreSQL", "Docker", "REST API",
      "Redis", "RAG", "LangGraph", "Celery", "AWS", "Kubernetes", "Microservices"
    ],
    "projects": [
      "Built distributed AI microservices"
    ],
    "resume_filename": "RAHUL KUMAR.docx",
    "graduation_year": 2021,
    "created_at": "2026-09-10T15:21:00.000000"
  },
  "parsed_summary": {
    "name": "Rahul Kumar",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Redis", "RAG", "LangGraph", "Celery", "AWS", "Kubernetes", "Microservices"],
    "experience_years": 5,
    "education": ["B.Tech in Computer Science, 2021"]
  }
}
```

#### `GET /api/candidates`
- **Summary**: List All Candidates
- **Tag**: `2. Candidate Ingestion & Resume Parsing`
- **Query Parameter**: `anonymized` (boolean, default: `false`). When `true`, strips PII (Name, Email, Phone, Gender, Location, Graduation Year).
- **Response 200 OK**: Array of `CandidateResponse` objects.

#### `GET /api/candidates/{candidate_id}`
- **Summary**: Get Candidate Profile
- **Tag**: `2. Candidate Ingestion & Resume Parsing`
- **Path Parameter**: `candidate_id` (integer, required)
- **Response 200 OK**: Single `CandidateResponse` object.

---

### Section 3: Matching & RAG Vector Search

#### `POST /api/matching/match`
- **Summary**: Match Candidate with Job Description
- **Tag**: `3. Matching & RAG Vector Search`
- **Query Parameters**:
  - `candidate_id` (integer, required): e.g. `5`
  - `job_id` (integer, required): e.g. `3`
- **Response 200 OK**:
```json
{
  "matched_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "REST API"
  ],
  "missing_skills": [],
  "match_percentage": 100.0,
  "semantic_search_score": 51.91
}
```

#### `POST /api/matching/search-resumes`
- **Summary**: Semantic Vector Search (RAG)
- **Tag**: `3. Matching & RAG Vector Search`
- **Query Parameter**: `query` (string, required): e.g. `Python FastAPI RAG LangGraph backend engineer`
- **Response 200 OK**:
```json
[
  {
    "candidate_id": 5,
    "chunk": "Experienced Python backend developer skilled in FastAPI, PostgreSQL, and LangGraph.",
    "similarity": 87.4,
    "metadata": {
      "name": "Rahul Kumar",
      "skills": ["Python", "FastAPI", "RAG"]
    }
  }
]
```

---

### Section 4: Technical & Coding Assessment

#### `POST /api/assessment/start`
- **Summary**: Initialize Assessment Session
- **Tag**: `4. Technical & Coding Assessment`
- **Request Body** (`application/json`):
```json
{
  "candidate_id": 5,
  "job_id": 3
}
```
- **Response 200 OK**:
```json
{
  "id": 4,
  "candidate_id": 5,
  "job_id": 3,
  "match_percentage": 100.0,
  "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
  "missing_skills": [],
  "semantic_search_score": 51.91,
  "technical_score": 0.0,
  "coding_score": 0.0,
  "communication_score": 0.0,
  "final_score": 0.0,
  "performance_level": "Pending",
  "decision": "Under Review",
  "hr_approved": false,
  "notification_sent": false,
  "workflow_stage": "Screening",
  "interview_log": [],
  "coding_submission": {},
  "communication_log": {},
  "created_at": "2026-09-10T15:22:00.000000"
}
```

#### `GET /api/assessment/coding-challenge`
- **Summary**: Get Coding Challenge
- **Tag**: `4. Technical & Coding Assessment`
- **Query Parameter**: `language` (string, default: `"python"`, options: `"python"`, `"java"`)
- **Response 200 OK**:
```json
{
  "id": "py_two_sum",
  "title": "Two Sum Target Finder",
  "difficulty": "Medium",
  "skill": "Python",
  "description": "Given a list of integers nums and an integer target, return the indices of the two numbers such that they add up to target.",
  "expected_time_complexity": "O(N)",
  "edge_cases": [
    "Empty array",
    "Duplicate elements",
    "Negative numbers"
  ]
}
```

#### `POST /api/assessment/coding-submit`
- **Summary**: Submit & Execute Code in Sandbox
- **Tag**: `4. Technical & Coding Assessment`
- **Request Body** (`application/json`):
```json
{
  "assessment_id": 4,
  "language": "python",
  "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []",
  "challenge_id": "py_two_sum"
}
```
- **Response 200 OK**:
```json
{
  "challenge_id": "py_two_sum",
  "challenge_title": "Two Sum Target Finder",
  "language": "python",
  "score": 100.0,
  "passed_tests": 4,
  "total_tests": 4,
  "test_details": [
    {"test": "two_sum([2, 7, 11, 15], 9)", "expected": "[0, 1]", "actual": "[0, 1]", "passed": true},
    {"test": "two_sum([3, 2, 4], 6)", "expected": "[1, 2]", "actual": "[1, 2]", "passed": true},
    {"test": "two_sum([3, 3], 6)", "expected": "[0, 1]", "actual": "[0, 1]", "passed": true},
    {"test": "two_sum([], 5)", "expected": "[]", "actual": "[]", "passed": true}
  ],
  "detected_time_complexity": "O(N)",
  "expected_time_complexity": "O(N)",
  "edge_case_suggestions": ["Empty array", "Duplicate elements", "Negative numbers"],
  "stdout": "",
  "stderr": ""
}
```

#### `GET /api/assessment/{assessment_id}/tech-questions`
- **Summary**: Generate Adaptive Tech Questions
- **Tag**: `4. Technical & Coding Assessment`
- **Path Parameter**: `assessment_id` (integer, required)
- **Response 200 OK**:
```json
{
  "questions": [
    {
      "id": 101,
      "skill": "Python",
      "question": "How does Python's Global Interpreter Lock (GIL) impact CPU-bound multi-threading, and how can you achieve true concurrency?",
      "difficulty": "Intermediate"
    },
    {
      "id": 201,
      "skill": "FastAPI",
      "question": "How does FastAPI leverage Pydantic and async/await for request validation and high-throughput async endpoints?",
      "difficulty": "Advanced"
    }
  ]
}
```

#### `POST /api/assessment/tech-answer`
- **Summary**: Submit Tech Answer & Receive Dynamic Follow-up
- **Tag**: `4. Technical & Coding Assessment`
- **Request Body** (`application/json`):
```json
{
  "assessment_id": 4,
  "question_id": 101,
  "question": "How does Python's Global Interpreter Lock (GIL) impact CPU-bound multi-threading, and how can you achieve true concurrency?",
  "answer": "The GIL ensures only one thread executes Python bytecode at a time. For CPU-bound concurrency, we use multiprocessing or process pools instead of threads."
}
```
- **Response 200 OK**:
```json
{
  "evaluation": {
    "score": 90.0,
    "feedback": "Strong coverage of: gil, thread, multiprocessing, cpu.",
    "concepts_covered": ["gil", "thread", "multiprocessing", "cpu"],
    "concepts_missed": ["asyncio", "concurrency"]
  },
  "follow_up": {
    "follow_up_question": "How would you handle race conditions or process synchronization in this approach under high concurrency?",
    "focus_area": "Concurrency & Edge Cases"
  },
  "current_technical_score": 90.0
}
```

#### `GET /api/assessment/{assessment_id}`
- **Summary**: Get Assessment Status & Audit
- **Tag**: `4. Technical & Coding Assessment`
- **Path Parameter**: `assessment_id` (integer, required)
- **Response 200 OK**: Full `AssessmentResponse` object with all logs.

---

### Section 5: Audio & Communication Screening

#### `POST /api/assessment/screening`
- **Summary**: Evaluate Speech Screening
- **Tag**: `5. Audio & Communication Screening`
- **Request Body** (`application/json`):
```json
{
  "assessment_id": 4,
  "transcript": "Interviewer: Tell me about your Python experience.\nCandidate: I have 5 years of experience working with Python. I have built backend applications, REST APIs, and AI-powered services.\n\nInterviewer: What experience do you have with FastAPI?\nCandidate: I have used FastAPI to build production REST APIs and backend microservices, including PostgreSQL integration and asynchronous endpoints.\n\nInterviewer: Explain your experience with RAG.\nCandidate: I have built RAG pipelines using document chunking, embeddings, vector search, and LLM-based generation.\n\nInterviewer: Have you worked with LangGraph?\nCandidate: Yes. I have built AI workflows and multi-agent systems using LangGraph, including state management and conditional routing.\n\nInterviewer: How do you handle databases?\nCandidate: I have worked extensively with PostgreSQL, database design, SQL queries, and integrating PostgreSQL with Python backend applications."
}
```
- **Response 200 OK**:
```json
{
  "transcription": "Interviewer: Tell me about your Python experience...",
  "communication_clarity": "High",
  "filler_word_count": 0,
  "sentiment": "Constructive / Neutral",
  "communication_score": 86.0,
  "feedback": "Demonstrated high clarity with constructive / neutral tone. Used 0 filler words across 108 words spoken."
}
```

---

### Section 6: LangGraph Workflow & HR Checkpoints

#### `POST /api/assessment/run-pipeline/{assessment_id}`
- **Summary**: Execute Multi-Stage LangGraph Pipeline
- **Tag**: `6. LangGraph Workflow & HR Checkpoints`
- **Path Parameter**: `assessment_id` (integer, required)
- **Pipeline Stages**:
  $$\text{Matching} \longrightarrow \text{Screening} \longrightarrow \text{Fair Scoring} \longrightarrow \text{HR Decision}$$
- **Scoring Engine**:
  $$\text{Final Score} = (0.40 \times \text{Tech}) + (0.40 \times \text{Coding}) + (0.20 \times \text{Communication})$$
- **Response 200 OK**:
```json
{
  "id": 4,
  "candidate_id": 5,
  "job_id": 3,
  "match_percentage": 100.0,
  "technical_score": 90.0,
  "coding_score": 100.0,
  "communication_score": 86.0,
  "final_score": 93.2,
  "performance_level": "Exceptional",
  "decision": "Shortlisted",
  "workflow_stage": "HR_APPROVAL_CHECKPOINT",
  "notification_sent": true
}
```

#### `POST /api/assessment/hr-checkpoint/{assessment_id}`
- **Summary**: HR Human-in-the-Loop Checkpoint
- **Tag**: `6. LangGraph Workflow & HR Checkpoints`
- **Path Parameter**: `assessment_id` (integer, required)
- **Query Parameters**:
  - `approved` (boolean, required): `true` to approve, `false` to reject
  - `feedback` (string, optional): e.g. `Candidate approved for offer`
- **Example**: `POST /api/assessment/hr-checkpoint/4?approved=true&feedback=Approved%20by%20Hiring%20Lead`
- **Response 200 OK**:
```json
{
  "status": "success",
  "assessment": {
    "id": 4,
    "hr_approved": true,
    "hr_feedback": "Approved by Hiring Lead",
    "decision": "Shortlisted (HR Approved)",
    "workflow_stage": "Completed"
  }
}
```

---

### Section 7: Dashboard Analytics & Seed Data

#### `GET /api/dashboard/stats`
- **Summary**: Retrieve Aggregated Recruitment Metrics
- **Tag**: `7. Dashboard Analytics & Seed Data`
- **Response 200 OK**:
```json
{
  "total_candidates": 5,
  "total_assessments": 4,
  "shortlisted": 2,
  "under_review": 2,
  "not_shortlisted": 0,
  "python_candidates": 4,
  "java_candidates": 2,
  "average_final_score": 55.9
}
```

#### `GET /api/dashboard/ranked-candidates/{job_id}`
- **Summary**: Get Candidate Ranking Pipeline
- **Tag**: `7. Dashboard Analytics & Seed Data`
- **Path Parameter**: `job_id` (integer, required): e.g. `3`
- **Response 200 OK**:
```json
[
  {
    "rank": 1,
    "percentile": 100.0,
    "composite_score": 94.4,
    "assessment_id": 4,
    "candidate_id": 5,
    "candidate_name": "Rahul Kumar",
    "anonymized_id": "CAND-BFE650",
    "match_percentage": 100.0,
    "technical_score": 90.0,
    "coding_score": 100.0,
    "communication_score": 86.0,
    "final_score": 93.2,
    "performance_level": "Exceptional",
    "decision": "Shortlisted (HR Approved)",
    "hr_approved": true,
    "workflow_stage": "Completed"
  }
]
```

#### `GET /api/dashboard/notifications`
- **Summary**: Get Real-time HR Alerts Feed
- **Tag**: `7. Dashboard Analytics & Seed Data`
- **Response 200 OK**:
```json
[
  {
    "id": 1,
    "type": "SHORTLIST_ALERT",
    "title": "Candidate Shortlisted: Rahul Kumar",
    "message": "Rahul Kumar scored 93.2% on assessment for position 'Senior Python AI Backend Engineer' and has been auto-shortlisted.",
    "candidate_id": 5,
    "job_title": "Senior Python AI Backend Engineer",
    "final_score": 93.2,
    "status": "UNREAD",
    "timestamp": "2026-09-10T15:23:45.000000"
  }
]
```

#### `POST /api/seed-data`
- **Summary**: Seed Sample Jobs and Candidates
- **Tag**: `7. Dashboard Analytics & Seed Data`
- **Response 200 OK**:
```json
{
  "status": "success",
  "message": "Successfully seeded jobs, candidates, and initial assessments!"
}
```

---

## 4. Key Implementation & Testing Guidelines

### A. ID Types and Validation
All ID fields (`candidate_id`, `job_id`, `assessment_id`) are strict integers.
- ✅ Correct: `4`
- ❌ Incorrect: `"4"`, `assessment-4`

### B. Coding Challenge Function Name
The coding evaluation runner expects the function name specified by the challenge. For `py_two_sum`, the submission must define:
```python
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []
```

### C. RAG Query Input
The `query` parameter for `/api/matching/search-resumes` is a URL-encoded plain text string:
- ✅ Correct: `/api/matching/search-resumes?query=Python%20FastAPI%20RAG`
- ❌ Incorrect: `{"query": "Python FastAPI RAG"}`

---

## 5. Summary Status

| Category | Endpoints Count | Verification Status |
|---|---|---|
| **1. Job Management** | 3 | ✅ Verified |
| **2. Candidate Parsing & Ingestion** | 3 | ✅ Verified |
| **3. Matching & RAG Vector Search** | 2 | ✅ Verified |
| **4. Technical & Coding Assessment** | 6 | ✅ Verified |
| **5. Audio & Communication Screening** | 1 | ✅ Verified |
| **6. LangGraph Workflow & HR Checkpoints** | 2 | ✅ Verified |
| **7. Dashboard Analytics & Seed Data** | 4 | ✅ Verified |
| **TOTAL** | **21 Endpoints** | **100% Operational** |
