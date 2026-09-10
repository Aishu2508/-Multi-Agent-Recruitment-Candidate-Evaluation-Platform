# -Multi-Agent-Recruitment-Candidate-Evaluation-Platform
================================================================================
AI RECRUITMENT ASSESSMENT SYSTEM
Intelligent Multi-Agent Recruitment & Candidate Evaluation Platform
================================================================================

OVERVIEW
--------------------------------------------------------------------------------
The AI Recruitment Assessment System is a production-grade Python application 
developed using FastAPI, SQLAlchemy (PostgreSQL & SQLite), and Qdrant/vector 
search. It automates candidate evaluation through multi-agent collaboration, 
adaptive technical interviewing, isolated code execution, speech screening, 
fair scoring, and LangGraph workflow orchestration with human-in-the-loop 
HR checkpoints.


KEY FEATURES
--------------------------------------------------------------------------------
1. Parsing Agent
   - Extracts Name, Email, Phone, Education, Experience, Skills, and Projects.
   - Parses PDF resumes via PyMuPDF (fitz) and PyPDF, as well as DOCX and TXT.
   - Generates unique anonymized candidate IDs (e.g., CAND-BFE650).

2. Matching Agent
   - Compares candidate skills against Job Description requirements.
   - Calculates exact matched skills, missing skills, and match percentage.
   - Computes semantic relevance scores using cosine similarity.

3. RAG and Vector Search
   - Uses SentenceTransformer (all-MiniLM-L6-v2) for 384-dimensional embeddings.
   - Integrates with Qdrant vector database and persistent embedded vector store.
   - Enables semantic resume search over candidate work experience chunks.

4. Adaptive Technical Interview
   - Generates skill-specific technical questions tailored to the candidate.
   - Dynamically generates probing follow-up questions evaluating trade-offs,
     concurrency, and architectural depth.

5. Sandboxed Coding Evaluation
   - Supports Python and Java algorithm challenges (e.g., Two Sum, Palindrome).
   - Isolated execution sandbox with strict execution timeouts and memory limits.
   - Automatic test case verification, edge-case recommendations, and AST-based
     algorithmic time complexity analysis (e.g., O(N)).
   - Cloud sandbox integration support via E2B Code Interpreter.

6. Audio and Video Screening
   - Faster-Whisper integration for speech-to-text audio transcription.
   - Analyzes communication clarity, filler word frequency, and sentiment tone.
   - Generates normalized communication scores (0 - 100).

7. Fair Scoring & Anonymization
   - Removes PII (Name, Gender, Location, Graduation Year) prior to evaluation.
   - Eliminates unconscious bias and focuses solely on technical competence.

8. Weighted Final Scoring Model
   - Technical Score:      40%
   - Coding Score:         40%
   - Communication Score:  20%
   - Classifies candidates into performance tiers:
     Exceptional (>=85%), Strong Hire (>=70%), Needs Review (>=50%), Not Recommended (<50%).

9. Automated HR Decision & Checkpoints
   - Automates initial recommendations: Shortlisted, Under Review, Not Shortlisted.
   - LangGraph checkpoint support: pauses qualified candidates for human HR sign-off.

10. Automated HR Notifications
    - Dispatches real-time alerts when candidates exceed shortlisting thresholds.

11. LangGraph Recruitment Workflow
    - State machine pipeline:
      Resume Matching -> Screening -> Fair Scoring -> HR Approval Checkpoint

12. Asynchronous Task Queue
    - Celery and Redis integration for heavy background processing.
    - Synchronous fallback runner when Redis is not running.


TECH STACK
--------------------------------------------------------------------------------
Backend:               Python 3.10+ (FastAPI, Uvicorn, Pydantic, SQLAlchemy)
Database:              PostgreSQL / SQLite
AI / NLP:              SentenceTransformers, Faster-Whisper, Qdrant, LangGraph, LiteLLM
Code Execution:        Isolated Subprocess Sandbox / E2B Code Interpreter
Background Processing: Celery, Redis
Resume Processing:     PyMuPDF, PyPDF, python-docx
Frontend:              HTML5, Tailwind CSS, JavaScript, Chart.js


PROJECT STRUCTURE
--------------------------------------------------------------------------------
AI-Recruitment-Assessment-System/
├── agents/
│   ├── __init__.py
│   ├── parsing_agent.py          # Resume parsing & PII anonymization
│   ├── matching_agent.py         # JD skill overlap & gap analysis
│   ├── tech_agent.py             # Adaptive Q&A and dynamic follow-ups
│   ├── screening_agent.py        # Speech transcription & clarity analysis
│   ├── scoring_agent.py          # 40/40/20 weighted fair scoring
│   └── hr_agent.py               # Shortlist decisions & HR alerts
│
├── models/
│   ├── __init__.py
│   ├── candidate.py              # Candidate SQLAlchemy & Pydantic models
│   ├── job.py                    # Job requisition schemas & models
│   └── assessment.py             # Assessment logs, scores & checkpoints
│
├── services/
│   ├── __init__.py
│   ├── resume_parser.py          # Multi-format text extraction
│   ├── jd_matcher.py             # Keyword & TF-IDF similarity matcher
│   ├── rag_service.py            # Qdrant & embedded vector store
│   ├── ranking.py                # Multi-candidate percentile ranking
│   ├── code_executor.py          # Python/Java code execution sandbox
│   ├── fairness.py               # PII masking engine
│   ├── notification.py           # Automated HR alert dispatch
│   ├── tasks.py                  # Celery background tasks
│   └── workflow.py               # LangGraph state machine pipeline
│
├── static/
│   ├── index.html                # HR Dashboard with Chart.js analytics
│   └── AI-Recruitment-Assessment-System.zip
│
├── uploads/                      # Uploaded candidate resume files
├── qdrant_storage/               # Vector index storage
├── config.py                     # Configuration & environment settings
├── database.py                   # SQLAlchemy engine & session management
├── main.py                       # FastAPI application & REST endpoints
├── openapi.json                  # OpenAPI 3.1 specification export
├── requirements.txt              # Project dependencies
├── test_system.py                # Automated system test suite (8 tests)
├── SWAGGER_API_DOCUMENTATION.md  # Official technical API documentation
├── API_DOCUMENTATION.md          # End-to-end testing report
└── README.txt                    # This documentation file


INSTALLATION & QUICKSTART
--------------------------------------------------------------------------------
1. Clone the repository:
   git clone https://github.com/your-username/AI-Recruitment-Assessment-System.git
   cd AI-Recruitment-Assessment-System

2. Create and activate a virtual environment (optional but recommended):
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

3. Install required dependencies:
   pip install -r requirements.txt

4. Start the FastAPI application:
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

5. Open your web browser:
   - HR Dashboard:     http://localhost:8000
   - Swagger UI Docs:  http://localhost:8000/docs
   - OpenAPI Schema:   http://localhost:8000/openapi.json


HOW TO USE THE HR DASHBOARD
--------------------------------------------------------------------------------
1. Seed Sample Data:
   Click "Seed Sample Data" on the top navigation bar to populate realistic
   candidates and render the Python vs. Java distribution doughnut chart.

2. Upload Real Resumes:
   Click "Upload Resume" to upload any PDF, DOCX, or TXT resume. The Parsing
   Agent will automatically extract skills, contact details, and experience.

3. Candidate Assessment Studio:
   Click "Assess" next to any candidate:
   - Tab 1 (Resume & Matching): View matched/missing skills & RAG similarity score.
   - Tab 2 (Adaptive Tech Interview): Generate questions and dynamic follow-ups.
   - Tab 3 (Coding Sandbox): Test Python/Java code with live test suite & O(N) complexity.
   - Tab 4 (Audio Screening): Analyze speech clarity, sentiment, and filler words.
   - Tab 5 (LangGraph Pipeline & HR): Run full pipeline and submit HR approval.


RUNNING TESTS
--------------------------------------------------------------------------------
Execute the automated test suite:
python test_system.py

Expected output:
Ran 8 tests in 33.052s
OK


API ENDPOINTS SUMMARY
--------------------------------------------------------------------------------
1. Job Management:
   - POST /api/jobs                               Create Job Requisition
   - GET  /api/jobs                               List All Jobs
   - GET  /api/jobs/{job_id}                      Get Job by ID

2. Candidate Ingestion:
   - POST /api/candidates/upload                  Upload & Parse Resume
   - GET  /api/candidates                         List Candidates
   - GET  /api/candidates/{candidate_id}          Get Candidate Details

3. Matching & RAG:
   - POST /api/matching/match                     Match Candidate with Job
   - POST /api/matching/search-resumes            Semantic Vector Search

4. Technical & Coding:
   - POST /api/assessment/start                   Start Assessment Session
   - GET  /api/assessment/coding-challenge        Get Coding Challenge
   - POST /api/assessment/coding-submit           Execute Code in Sandbox
   - GET  /api/assessment/{id}/tech-questions     Generate Tech Questions
   - POST /api/assessment/tech-answer             Submit Answer & Follow-up
   - GET  /api/assessment/{id}                    Get Full Assessment Audit

5. Screening:
   - POST /api/assessment/screening               Submit Communication Speech

6. LangGraph Workflow:
   - POST /api/assessment/run-pipeline/{id}       Execute Multi-Stage Pipeline
   - POST /api/assessment/hr-checkpoint/{id}      HR Approval Checkpoint

7. Dashboard & Analytics:
   - GET  /api/dashboard/stats                    HR Metrics & Chart Data
   - GET  /api/dashboard/ranked-candidates/{id}   Ranked Candidate Pipeline
   - GET  /api/dashboard/notifications            Realtime HR Alerts
   - POST /api/seed-data                          Seed Sample Data


