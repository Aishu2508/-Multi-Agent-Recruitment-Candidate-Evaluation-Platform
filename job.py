from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from pydantic import BaseModel, ConfigDict
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), default="Engineering")
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)  # Mandatory skills
    nice_to_have_skills = Column(JSON, default=list)
    min_experience_years = Column(Integer, default=0)
    min_score_threshold = Column(Float, default=70.0)
    primary_language = Column(String(50), default="Python")  # Python, Java, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class JobCreate(BaseModel):
    title: str
    department: Optional[str] = "Engineering"
    description: str
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    min_experience_years: int = 0
    min_score_threshold: float = 70.0
    primary_language: str = "Python"

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    department: str
    description: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    min_experience_years: int
    min_score_threshold: float
    primary_language: str
    created_at: datetime
