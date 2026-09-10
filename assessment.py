from datetime import datetime
from typing import List, Optional, Any, Dict
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # 1. Matching Results
    match_percentage = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    semantic_search_score = Column(Float, default=0.0)

    # 2. Stage Scores
    technical_score = Column(Float, default=0.0)
    coding_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)

    # 3. Decision & HR Approval
    performance_level = Column(String(50), default="Pending")
    decision = Column(String(50), default="Under Review")  # Shortlisted, Under Review, Not Shortlisted
    hr_approved = Column(Boolean, default=False)
    hr_feedback = Column(Text, nullable=True)
    notification_sent = Column(Boolean, default=False)
    workflow_stage = Column(String(50), default="Initiated")  # Matching -> Screening -> Scoring -> HR Decision -> Completed

    # Detailed Logs
    interview_log = Column(JSON, default=list)
    coding_submission = Column(JSON, default=dict)
    communication_log = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", backref="assessments")
    job = relationship("Job", backref="assessments")

class AssessmentCreate(BaseModel):
    candidate_id: int
    job_id: int

class TechInterviewAnswer(BaseModel):
    assessment_id: int
    question_id: int
    question: str
    answer: str

class CodingSubmitRequest(BaseModel):
    assessment_id: int
    language: str  # "python" or "java"
    code: str
    challenge_id: Optional[str] = None

class ScreeningUploadRequest(BaseModel):
    assessment_id: int
    transcript: Optional[str] = None

class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    job_id: int
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    semantic_search_score: float
    technical_score: float
    coding_score: float
    communication_score: float
    final_score: float
    performance_level: str
    decision: str
    hr_approved: bool
    hr_feedback: Optional[str] = None
    notification_sent: bool
    workflow_stage: str
    interview_log: List[Any]
    coding_submission: Dict[str, Any]
    communication_log: Dict[str, Any]
    created_at: datetime
