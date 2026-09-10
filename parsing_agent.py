import uuid
from pathlib import Path
from typing import Dict, Any
from services.resume_parser import extract_text_from_file, parse_resume_text
from services.rag_service import vector_store

class ParsingAgent:
    """Agent responsible for parsing resumes, extracting key structured entities, and indexing."""
    
    def process_resume(self, file_path: Path) -> Dict[str, Any]:
        raw_text = extract_text_from_file(file_path)
        parsed_data = parse_resume_text(raw_text)
        
        # Generate unique anonymized ID for fairness
        anonymized_id = f"CAND-{uuid.uuid4().hex[:6].upper()}"
        parsed_data["anonymized_id"] = anonymized_id
        parsed_data["resume_filename"] = file_path.name
        
        return parsed_data

    def index_parsed_resume(self, candidate_id: int, parsed_data: Dict[str, Any]):
        """Indexes parsed resume chunks into vector store / Qdrant."""
        metadata = {
            "name": parsed_data.get("name"),
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0),
            "anonymized_id": parsed_data.get("anonymized_id")
        }
        vector_store.index_resume(candidate_id, parsed_data.get("raw_text", ""), metadata)

parsing_agent = ParsingAgent()
