import re
from pathlib import Path
from typing import Dict, Any, List

COMMON_SKILLS = [
    # Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash", "shell",
    # Frameworks & Libraries
    "fastapi", "flask", "django", "spring boot", "spring", "react", "next.js", "vue", "angular", "node.js", "express", "pytorch", "tensorflow", "scikit-learn", "keras", "pandas", "numpy", "celery", "langchain", "langgraph", "litellm",
    # Databases & Cloud
    "postgresql", "mysql", "mongodb", "redis", "qdrant", "elasticsearch", "sqlite", "docker", "kubernetes", "aws", "azure", "gcp", "git", "ci/cd", "linux",
    # Concepts
    "rest api", "graphql", "microservices", "rag", "vector search", "nlp", "machine learning", "deep learning", "agile", "tdd"
]

DEGREE_PATTERNS = [
    r"(?i)\b(ph\.?d|doctorate)\b.*",
    r"(?i)\b(m\.?s\.?|master|m\.?tech|mca|mba)\b.*",
    r"(?i)\b(b\.?s\.?|bachelor|b\.?tech|b\.?e\.?|bca|bsc)\b.*"
]

def extract_text_from_file(file_path: Path) -> str:
    """Extracts raw text from PDF, DOCX, or TXT file."""
    ext = file_path.suffix.lower()
    text = ""
    
    if ext == ".pdf":
        try:
            # Try PyMuPDF fitz first if available
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
        except Exception:
            # Fallback to pypdf
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                text = f"Error reading PDF: {e}"
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(str(file_path))
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            text = f"Error reading DOCX: {e}"
    else:
        # Plain text
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            text = f"Error reading text: {e}"
            
    return text.strip()

def parse_resume_text(text: str) -> Dict[str, Any]:
    """Extracts structured entities (name, email, phone, skills, education, projects, experience) from raw text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Email Extraction
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0) if email_match else None
    
    # 2. Phone Extraction
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else None
    
    # 3. Name Extraction (Heuristic: first non-empty line or capitalized line before contact info)
    name = None
    for line in lines[:6]:
        clean_line = re.sub(r"[^\w\s]", "", line).strip()
        if clean_line and len(clean_line.split()) in (2, 3, 4) and not re.search(r"(resume|curriculum|vitae|email|phone|github|linkedin)", clean_line, re.IGNORECASE):
            name = clean_line
            break
    if not name and lines:
        name = lines[0][:40]

    # 4. Skills Extraction
    CANONICAL_SKILLS = {
        "fastapi": "FastAPI",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "rest api": "REST API",
        "graphql": "GraphQL",
        "rag": "RAG",
        "nlp": "NLP",
        "ai": "AI",
        "ci/cd": "CI/CD",
        "sql": "SQL",
        "aws": "AWS",
        "gcp": "GCP",
        "css": "CSS",
        "html": "HTML",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "microservices": "Microservices"
    }
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            canonical = CANONICAL_SKILLS.get(skill.lower(), skill.title() if len(skill) > 3 else skill.upper())
            found_skills.append(canonical)

    # 5. Education Extraction
    education = []
    for line in lines:
        for deg_pat in DEGREE_PATTERNS:
            if re.search(deg_pat, line):
                education.append(line)
                break
    if not education:
        # Fallback search
        for line in lines:
            if any(k in line.lower() for k in ["university", "college", "institute", "bachelor", "master", "degree"]):
                education.append(line)

    # 6. Graduation Year Extraction
    grad_year = None
    year_matches = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    if year_matches:
        valid_years = [int(y) for y in year_matches if 1990 <= int(y) <= 2030]
        if valid_years:
            grad_year = max(valid_years)

    # 7. Experience Extraction
    exp_years = 0
    exp_matches = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience", text, re.IGNORECASE)
    if exp_matches:
        exp_years = max([int(y) for y in exp_matches])
    else:
        # Count year ranges like 2019-2023
        ranges = re.findall(r"\b(20\d{2})\s*[-–to]+\s*(20\d{2}|present)\b", text, re.IGNORECASE)
        total_span = 0
        for start, end in ranges:
            start_yr = int(start)
            end_yr = 2026 if "present" in end.lower() else int(end)
            if end_yr >= start_yr:
                total_span += (end_yr - start_yr)
        exp_years = min(total_span, 30)

    # 8. Projects Extraction
    projects = []
    in_projects_sec = False
    for line in lines:
        if re.search(r"(?i)^(projects|personal projects|key projects|academic projects)", line):
            in_projects_sec = True
            continue
        elif in_projects_sec and re.search(r"(?i)^(experience|work history|skills|education|certifications)", line):
            in_projects_sec = False
            break
        elif in_projects_sec:
            if len(line) > 10:
                projects.append(line)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": list(set(found_skills)),
        "education": education[:4],
        "experience_years": exp_years,
        "experience": [line for line in lines if any(k in line.lower() for k in ["engineer", "developer", "lead", "architect", "intern"])][:5],
        "projects": projects[:5],
        "graduation_year": grad_year,
        "raw_text": text
    }
