from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from pydantic import BaseModel, ConfigDict
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    anonymized_id = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    gender = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    
    education = Column(JSON, default=list)  # List of education details
    experience_years = Column(Integer, default=0)
    experience = Column(JSON, default=list)  # Roles, companies, responsibilities
    skills = Column(JSON, default=list)  # List of skill strings
    projects = Column(JSON, default=list)  # List of project summaries
    
    resume_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Schemas
class CandidateCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    graduation_year: Optional[int] = None
    education: List[Any] = []
    experience_years: int = 0
    experience: List[Any] = []
    skills: List[str] = []
    projects: List[Any] = []
    raw_text: Optional[str] = None
    resume_filename: Optional[str] = None

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anonymized_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    graduation_year: Optional[int] = None
    education: List[Any] = []
    experience_years: int = 0
    experience: List[Any] = []
    skills: List[str] = []
    projects: List[Any] = []
    resume_filename: Optional[str] = None
    created_at: datetime

class CandidateAnonymized(BaseModel):
    id: int
    anonymized_id: str
    education: List[Any] = []
    experience_years: int = 0
    experience: List[Any] = []
    skills: List[str] = []
    projects: List[Any] = []
