import os
import io
import zipfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from config import settings
from database import get_db, init_db
from models.candidate import Candidate, CandidateCreate, CandidateResponse, CandidateAnonymized
from models.job import Job, JobCreate, JobResponse
from models.assessment import (
    Assessment, AssessmentCreate, AssessmentResponse,
    TechInterviewAnswer, CodingSubmitRequest, ScreeningUploadRequest
)
from agents import (
    parsing_agent, matching_agent, tech_agent, screening_agent,
    scoring_agent, hr_agent
)
from services import (
    vector_store, rank_candidates, evaluate_submission,
    get_coding_challenge, anonymize_candidate, get_hr_notifications,
    workflow_engine
)

# Initialize database schema
init_db()

# Ordered OpenAPI Tags for Swagger UI Documentation
tags_metadata = [
    {
        "name": "1. Job Management",
        "description": "Create, list, and manage job requisitions and required skills."
    },
    {
        "name": "2. Candidate Ingestion & Resume Parsing",
        "description": "Upload resumes (PDF/DOCX/TXT), extract entities via Parsing Agent, and view candidate profiles."
    },
    {
        "name": "3. Matching & RAG Vector Search",
        "description": "Compare candidate qualifications against Job Descriptions and perform semantic vector search."
    },
    {
        "name": "4. Technical & Coding Assessment",
        "description": "Generate adaptive technical questions, dynamic follow-ups, and execute code in an isolated sandbox."
    },
    {
        "name": "5. Audio & Communication Screening",
        "description": "Evaluate speech-to-text transcription, communication clarity, sentiment, and filler-word frequency."
    },
    {
        "name": "6. LangGraph Workflow & HR Checkpoints",
        "description": "Execute the end-to-end recruitment state machine and manage human-in-the-loop HR approval checkpoints."
    },
    {
        "name": "7. Dashboard Analytics & Seed Data",
        "description": "Retrieve HR metrics, Python vs Java candidate distribution charts, and populate sample test data."
    }
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Recruitment Assessment System with multi-agent evaluation, RAG vector search, and LangGraph workflow.",
    openapi_tags=tags_metadata
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for frontend HR Dashboard
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")

# ==============================================================================
# 1. Job Management Endpoints
# ==============================================================================
@app.post("/api/jobs", response_model=JobResponse, tags=["1. Job Management"], summary="Create Job Requisition")
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Creates a new job requisition with required and nice-to-have skills."""
    job = Job(**job_in.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/api/jobs", response_model=List[JobResponse], tags=["1. Job Management"], summary="List All Jobs")
def list_jobs(db: Session = Depends(get_db)):
    """Returns all active job requisitions ordered by most recent."""
    return db.query(Job).order_by(Job.id.desc()).all()

@app.get("/api/jobs/{job_id}", response_model=JobResponse, tags=["1. Job Management"], summary="Get Job by ID")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Retrieves full specification for a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# ==============================================================================
# 2. Candidate Ingestion & Resume Parsing Endpoints
# ==============================================================================
@app.post("/api/candidates/upload", tags=["2. Candidate Ingestion & Resume Parsing"], summary="Upload & Parse Candidate Resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a resume file (PDF, DOCX, TXT), runs the Parsing Agent, and indexes it in vector storage."""
    upload_path = settings.UPLOAD_DIR / file.filename
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingest through Parsing Agent
    parsed = parsing_agent.process_resume(upload_path)

    # Save candidate in database
    candidate = Candidate(
        anonymized_id=parsed["anonymized_id"],
        name=parsed.get("name") or "Unknown Candidate",
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        education=parsed.get("education", []),
        experience_years=parsed.get("experience_years", 0),
        experience=parsed.get("experience", []),
        skills=parsed.get("skills", []),
        projects=parsed.get("projects", []),
        resume_filename=file.filename,
        raw_text=parsed.get("raw_text", ""),
        graduation_year=parsed.get("graduation_year")
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Index in RAG / vector store
    parsing_agent.index_parsed_resume(candidate.id, parsed)

    return {
        "status": "success",
        "candidate": candidate,
        "parsed_summary": {
            "name": candidate.name,
            "skills": candidate.skills,
            "experience_years": candidate.experience_years,
            "education": candidate.education
        }
    }

@app.get("/api/candidates", response_model=List[CandidateResponse], tags=["2. Candidate Ingestion & Resume Parsing"], summary="List Candidates")
def list_candidates(anonymized: bool = False, db: Session = Depends(get_db)):
    """Lists all candidates. If anonymized is enabled, masks PII for fair evaluation."""
    candidates = db.query(Candidate).order_by(Candidate.id.desc()).all()
    if anonymized or settings.FAIRNESS_MODE:
        return [CandidateResponse(**anonymize_candidate(c.__dict__)) for c in candidates]
    return candidates

@app.get("/api/candidates/{candidate_id}", tags=["2. Candidate Ingestion & Resume Parsing"], summary="Get Candidate Details")
def get_candidate(candidate_id: int, anonymized: bool = False, db: Session = Depends(get_db)):
    """Retrieves specific candidate profile."""
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if anonymized or settings.FAIRNESS_MODE:
        return anonymize_candidate(cand.__dict__)
    return cand

# ==============================================================================
# 3. Matching & RAG Vector Search Endpoints
# ==============================================================================
@app.post("/api/matching/match", tags=["3. Matching & RAG Vector Search"], summary="Match Candidate with Job")
def match_candidate(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    """Computes exact skills match, missing skills, and semantic search score."""
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not cand or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")

    result = matching_agent.evaluate_fit(
        candidate_skills=cand.skills or [],
        candidate_text=cand.raw_text or "",
        job_required_skills=job.required_skills or [],
        job_nice_to_have=job.nice_to_have_skills or [],
        job_description=job.description or ""
    )
    return result

@app.post("/api/matching/search-resumes", tags=["3. Matching & RAG Vector Search"], summary="Semantic Vector Search (RAG)")
def search_resumes_rag(query: str):
    """Searches indexed resume vector embeddings using cosine similarity."""
    return vector_store.search_resumes(query=query, top_k=5)

# ==============================================================================
# 4. Technical & Coding Assessment Endpoints
# ==============================================================================
@app.post("/api/assessment/start", response_model=AssessmentResponse, tags=["4. Technical & Coding Assessment"], summary="Start Candidate Assessment")
def start_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    """Initializes a new assessment tracking session for a candidate against a job."""
    cand = db.query(Candidate).filter(Candidate.id == payload.candidate_id).first()
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not cand or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found")

    match_data = matching_agent.evaluate_fit(
        candidate_skills=cand.skills or [],
        candidate_text=cand.raw_text or "",
        job_required_skills=job.required_skills or [],
        job_nice_to_have=job.nice_to_have_skills or [],
        job_description=job.description or ""
    )

    assessment = Assessment(
        candidate_id=cand.id,
        job_id=job.id,
        match_percentage=match_data["match_percentage"],
        matched_skills=match_data["matched_skills"],
        missing_skills=match_data["missing_skills"],
        semantic_search_score=match_data["semantic_search_score"],
        workflow_stage="Screening"
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@app.get("/api/assessment/coding-challenge", tags=["4. Technical & Coding Assessment"], summary="Get Coding Challenge")
def get_code_challenge(language: str = "python"):
    """Fetches coding problem, starter code, test suites, and expected time complexity."""
    return get_coding_challenge(language=language)

@app.post("/api/assessment/coding-submit", tags=["4. Technical & Coding Assessment"], summary="Submit & Execute Code")
def submit_coding_solution(payload: CodingSubmitRequest, db: Session = Depends(get_db)):
    """Executes candidate code in an isolated sandbox, tests outputs, and analyzes time complexity."""
    ass = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")

    eval_result = evaluate_submission(
        challenge_id=payload.challenge_id or "py_two_sum",
        code=payload.code,
        language=payload.language
    )

    ass.coding_submission = eval_result
    ass.coding_score = eval_result["score"]
    db.commit()

    return eval_result

@app.get("/api/assessment/{assessment_id}/tech-questions", tags=["4. Technical & Coding Assessment"], summary="Generate Technical Questions")
def get_technical_questions(assessment_id: int, db: Session = Depends(get_db)):
    """Generates adaptive technical questions tailored to the candidate's detected skill set."""
    ass = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")
    cand = db.query(Candidate).filter(Candidate.id == ass.candidate_id).first()
    
    questions = tech_agent.generate_questions(cand.skills or [], count=3)
    return {"questions": questions}

@app.post("/api/assessment/tech-answer", tags=["4. Technical & Coding Assessment"], summary="Submit Technical Answer & Follow-up")
def submit_tech_answer(payload: TechInterviewAnswer, db: Session = Depends(get_db)):
    """Evaluates candidate response and dynamically generates a follow-up probing trade-offs."""
    ass = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")

    eval_res = tech_agent.evaluate_answer(payload.question, payload.answer)
    follow_up = tech_agent.generate_follow_up(payload.question, payload.answer)

    log = list(ass.interview_log or [])
    log.append({
        "question": payload.question,
        "answer": payload.answer,
        "score": eval_res["score"],
        "feedback": eval_res["feedback"],
        "follow_up": follow_up
    })
    ass.interview_log = log
    
    scores = [item["score"] for item in log if "score" in item]
    ass.technical_score = round(sum(scores) / max(len(scores), 1), 1)
    db.commit()

    return {
        "evaluation": eval_res,
        "follow_up": follow_up,
        "current_technical_score": ass.technical_score
    }

@app.get("/api/assessment/{assessment_id}", response_model=AssessmentResponse, tags=["4. Technical & Coding Assessment"], summary="Get Assessment Status")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Retrieves full assessment state, logs, and score breakdown."""
    ass = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return ass

# ==============================================================================
# 5. Audio & Communication Screening Endpoints
# ==============================================================================
@app.post("/api/assessment/screening", tags=["5. Audio & Communication Screening"], summary="Evaluate Speech Screening")
def submit_screening(payload: ScreeningUploadRequest, db: Session = Depends(get_db)):
    """Screens candidate communication clarity, filler words, sentiment, and communication rating."""
    ass = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")

    transcript = payload.transcript or "I collaborated with engineering teams to optimize microservices architecture and deliver high-performance APIs."
    screening_eval = screening_agent.analyze_communication(transcript)

    ass.communication_log = screening_eval
    ass.communication_score = screening_eval["communication_score"]
    db.commit()

    return screening_eval

# ==============================================================================
# 6. LangGraph Workflow & HR Checkpoints Endpoints
# ==============================================================================
@app.post("/api/assessment/run-pipeline/{assessment_id}", tags=["6. LangGraph Workflow & HR Checkpoints"], summary="Execute LangGraph Workflow")
def run_pipeline(assessment_id: int, db: Session = Depends(get_db)):
    """Executes the complete multi-stage recruitment workflow: Matching -> Screening -> Fair Scoring -> HR Decision."""
    ass = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")
    cand = db.query(Candidate).filter(Candidate.id == ass.candidate_id).first()
    job = db.query(Job).filter(Job.id == ass.job_id).first()

    pipeline_state = workflow_engine.run_full_pipeline(
        candidate_data=cand.__dict__,
        job_data=job.__dict__,
        assessment_state=ass.__dict__
    )

    ass.match_percentage = pipeline_state["match_percentage"]
    ass.matched_skills = pipeline_state["matched_skills"]
    ass.missing_skills = pipeline_state["missing_skills"]
    ass.semantic_search_score = pipeline_state["semantic_search_score"]
    ass.technical_score = pipeline_state.get("technical_score", 0.0)
    ass.coding_score = pipeline_state.get("coding_score", 0.0)
    ass.communication_score = pipeline_state.get("communication_score", 0.0)
    ass.final_score = pipeline_state["final_score"]
    ass.performance_level = pipeline_state["performance_level"]
    ass.decision = pipeline_state["decision"]
    ass.workflow_stage = pipeline_state["workflow_stage"]
    ass.notification_sent = pipeline_state.get("notification_sent", False)

    db.commit()
    db.refresh(ass)
    return ass

@app.post("/api/assessment/hr-checkpoint/{assessment_id}", tags=["6. LangGraph Workflow & HR Checkpoints"], summary="HR Human-in-the-Loop Checkpoint")
def hr_approval_checkpoint(assessment_id: int, approved: bool, feedback: Optional[str] = None, db: Session = Depends(get_db)):
    """Resumes paused workflow from HR_APPROVAL_CHECKPOINT with human HR approval or rejection."""
    ass = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")

    updated_state = workflow_engine.resume_from_checkpoint(ass.__dict__, hr_approved=approved, hr_feedback=feedback or "")
    ass.hr_approved = approved
    ass.hr_feedback = feedback
    ass.decision = updated_state["decision"]
    ass.workflow_stage = "Completed"
    db.commit()

    return {"status": "success", "assessment": ass}

# ==============================================================================
# 7. Dashboard Analytics & Seed Data Endpoints
# ==============================================================================
@app.get("/api/dashboard/stats", tags=["7. Dashboard Analytics & Seed Data"], summary="Get HR Analytics & Chart Data")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Returns aggregated stats: total candidates, Python vs Java counts, decisions, and average scores."""
    total_candidates = db.query(Candidate).count()
    assessments = db.query(Assessment).all()
    
    shortlisted = sum(1 for a in assessments if "Shortlisted" in (a.decision or ""))
    under_review = sum(1 for a in assessments if "Under Review" in (a.decision or ""))
    not_shortlisted = sum(1 for a in assessments if "Not Shortlisted" in (a.decision or "") or "Rejected" in (a.decision or ""))

    candidates = db.query(Candidate).all()
    python_count = 0
    java_count = 0
    for c in candidates:
        skills = [s.lower() for s in (c.skills or [])]
        if "python" in skills:
            python_count += 1
        if "java" in skills:
            java_count += 1

    avg_score = round(sum(a.final_score for a in assessments) / max(len(assessments), 1), 1)

    return {
        "total_candidates": total_candidates,
        "total_assessments": len(assessments),
        "shortlisted": shortlisted,
        "under_review": under_review,
        "not_shortlisted": not_shortlisted,
        "python_candidates": python_count,
        "java_candidates": java_count,
        "average_final_score": avg_score
    }

@app.get("/api/dashboard/ranked-candidates/{job_id}", tags=["7. Dashboard Analytics & Seed Data"], summary="Get Ranked Candidate Pipeline")
def get_ranked_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    """Computes percentile rankings and composite scores for all candidates assessed for a job."""
    assessments = db.query(Assessment).filter(Assessment.job_id == job_id).all()
    records = []
    for a in assessments:
        cand = db.query(Candidate).filter(Candidate.id == a.candidate_id).first()
        records.append({
            "assessment_id": a.id,
            "candidate_id": a.candidate_id,
            "candidate_name": cand.name if not settings.FAIRNESS_MODE else f"Candidate {cand.anonymized_id}",
            "anonymized_id": cand.anonymized_id,
            "match_percentage": a.match_percentage,
            "technical_score": a.technical_score,
            "coding_score": a.coding_score,
            "communication_score": a.communication_score,
            "final_score": a.final_score,
            "performance_level": a.performance_level,
            "decision": a.decision,
            "hr_approved": a.hr_approved,
            "workflow_stage": a.workflow_stage
        })
    return rank_candidates(records)

@app.get("/api/dashboard/notifications", tags=["7. Dashboard Analytics & Seed Data"], summary="Get HR Alerts Feed")
def get_notifications():
    """Returns the latest automated shortlisting notifications for HR."""
    return get_hr_notifications(limit=15)

@app.post("/api/seed-data", tags=["7. Dashboard Analytics & Seed Data"], summary="Seed Sample Recruitment Data")
def seed_sample_data(db: Session = Depends(get_db)):
    """Seeds sample jobs and candidates (Python & Java) for immediate dashboard exploration."""
    if db.query(Job).count() > 0:
        return {"message": "Data already seeded"}

    # Job 1: Python
    job_py = Job(
        title="Senior Python / AI Backend Engineer",
        department="Engineering",
        description="Looking for an experienced Python engineer skilled in FastAPI, PostgreSQL, RAG, and LangGraph.",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
        nice_to_have_skills=["RAG", "Redis", "LangGraph", "Celery"],
        min_experience_years=3,
        min_score_threshold=70.0,
        primary_language="Python"
    )
    # Job 2: Java
    job_java = Job(
        title="Senior Java Microservices Engineer",
        department="Platform",
        description="Looking for a Java backend engineer skilled in Spring Boot, Microservices, and SQL optimization.",
        required_skills=["Java", "Spring Boot", "SQL", "Docker", "Microservices"],
        nice_to_have_skills=["Kubernetes", "AWS", "Kafka"],
        min_experience_years=4,
        min_score_threshold=70.0,
        primary_language="Java"
    )
    db.add(job_py)
    db.add(job_java)
    db.commit()
    db.refresh(job_py)
    db.refresh(job_java)

    # Sample Candidates
    cands_data = [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@example.com",
            "phone": "+1 555-0192",
            "education": ["B.S. in Computer Science, Stanford University, 2021"],
            "experience_years": 4,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "RAG", "Redis", "REST API"],
            "projects": ["Built distributed LLM ingestion pipeline handling 100k queries/day"],
            "raw_text": "Experienced Python Backend developer with 4 years building FastAPI services, Docker containers, and PostgreSQL databases."
        },
        {
            "name": "Marcus Rodriguez",
            "email": "marcus.r@example.com",
            "phone": "+1 555-0144",
            "education": ["M.S. in Software Engineering, Carnegie Mellon, 2019"],
            "experience_years": 6,
            "skills": ["Java", "Spring Boot", "SQL", "Docker", "Microservices", "Kubernetes"],
            "projects": ["Architected high-throughput payment processing engine in Spring Boot"],
            "raw_text": "Senior Java engineer specializing in Spring Boot microservices, high-concurrency transaction handling, and Docker."
        },
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+1 555-0178",
            "education": ["B.Tech in Information Technology, IIT Bombay, 2022"],
            "experience_years": 3,
            "skills": ["Python", "FastAPI", "SQL", "Machine Learning", "Docker"],
            "projects": ["Customer churn prediction model with FastAPI inference gateway"],
            "raw_text": "Machine learning and Python developer with strong backend API skills using FastAPI and Docker."
        }
    ]

    for cd in cands_data:
        parsed = parsing_agent.process_resume(Path(f"sample_{cd['name'].replace(' ', '_')}.txt"))
        cand = Candidate(
            anonymized_id=parsed["anonymized_id"],
            name=cd["name"],
            email=cd["email"],
            phone=cd["phone"],
            education=cd["education"],
            experience_years=cd["experience_years"],
            skills=cd["skills"],
            projects=cd["projects"],
            raw_text=cd["raw_text"]
        )
        db.add(cand)
        db.commit()
        db.refresh(cand)

        # Index in vector store
        parsing_agent.index_parsed_resume(cand.id, cand.__dict__)

        # Assessments
        if "Python" in cand.skills:
            ass = Assessment(
                candidate_id=cand.id,
                job_id=job_py.id,
                match_percentage=85.0,
                matched_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
                missing_skills=[],
                semantic_search_score=88.5,
                technical_score=85.0,
                coding_score=90.0,
                communication_score=80.0,
                final_score=86.0,
                performance_level="Exceptional",
                decision="Shortlisted",
                workflow_stage="HR_APPROVAL_CHECKPOINT",
                notification_sent=True
            )
            db.add(ass)
            db.commit()
        else:
            ass = Assessment(
                candidate_id=cand.id,
                job_id=job_java.id,
                match_percentage=90.0,
                matched_skills=["Java", "Spring Boot", "SQL", "Docker", "Microservices"],
                missing_skills=[],
                semantic_search_score=91.0,
                technical_score=88.0,
                coding_score=85.0,
                communication_score=85.0,
                final_score=86.2,
                performance_level="Exceptional",
                decision="Shortlisted",
                workflow_stage="Completed",
                hr_approved=True,
                notification_sent=True
            )
            db.add(ass)
            db.commit()

    return {"status": "success", "message": "Successfully seeded jobs, candidates, and initial assessments!"}
