from typing import Dict, Any
from config import settings
from services.notification import send_shortlist_notification

class HRAgent:
    """Agent that delivers automated recruitment decisions and dispatches HR alerts."""

    def make_decision(
        self,
        final_score: float,
        candidate_name: str = "Candidate",
        candidate_id: int = 0,
        job_title: str = "Software Engineer",
        min_threshold: float = None
    ) -> Dict[str, Any]:
        threshold = min_threshold if min_threshold is not None else settings.SHORTLIST_THRESHOLD
        review_threshold = settings.REVIEW_THRESHOLD

        notification = None
        if final_score >= threshold:
            decision = "Shortlisted"
            rationale = f"Candidate scored {final_score:.1f}%, surpassing the requirement threshold of {threshold:.1f}%."
            notification = send_shortlist_notification(candidate_name, candidate_id, job_title, final_score)
        elif final_score >= review_threshold:
            decision = "Under Review"
            rationale = f"Candidate scored {final_score:.1f}%. Met review criteria ({review_threshold:.1f}%), requires human hiring manager review."
        else:
            decision = "Not Shortlisted"
            rationale = f"Candidate scored {final_score:.1f}%, below the required threshold of {review_threshold:.1f}%."

        return {
            "decision": decision,
            "final_score": final_score,
            "threshold_used": threshold,
            "rationale": rationale,
            "notification_dispatched": notification is not None,
            "notification": notification
        }

hr_agent = HRAgent()

def evaluate_hr_decision(final_score: float, threshold: float = 70.0) -> Dict[str, Any]:
    return hr_agent.make_decision(final_score=final_score, min_threshold=threshold)
