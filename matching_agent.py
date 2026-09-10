from typing import List, Dict, Any
from services.jd_matcher import match_candidate_to_job

class MatchingAgent:
    """Agent that analyzes candidate qualifications against Job Description requirements."""

    def evaluate_fit(
        self,
        candidate_skills: List[str],
        candidate_text: str,
        job_required_skills: List[str],
        job_nice_to_have: List[str],
        job_description: str
    ) -> Dict[str, Any]:
        result = match_candidate_to_job(
            candidate_skills=candidate_skills,
            candidate_text=candidate_text,
            job_required_skills=job_required_skills,
            job_nice_to_have=job_nice_to_have,
            job_description=job_description
        )
        return {
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "match_percentage": result["match_percentage"],
            "semantic_search_score": result["semantic_search_score"]
        }

matching_agent = MatchingAgent()
