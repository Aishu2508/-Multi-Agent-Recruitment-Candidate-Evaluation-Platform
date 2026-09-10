import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("recruitment.notifications")

# In-memory store for HR notifications
NOTIFICATION_HISTORY: List[Dict[str, Any]] = []

def send_shortlist_notification(candidate_name: str, candidate_id: int, job_title: str, final_score: float) -> Dict[str, Any]:
    """Generates an automated notification for HR when a candidate qualifies for shortlisting."""
    notification = {
        "id": len(NOTIFICATION_HISTORY) + 1,
        "type": "SHORTLIST_ALERT",
        "title": f"Candidate Shortlisted: {candidate_name}",
        "message": f"{candidate_name} scored {final_score:.1f}% on assessment for position '{job_title}' and has been auto-shortlisted.",
        "candidate_id": candidate_id,
        "job_title": job_title,
        "final_score": final_score,
        "status": "UNREAD",
        "timestamp": datetime.utcnow().isoformat()
    }
    NOTIFICATION_HISTORY.insert(0, notification)
    logger.info(f"HR Notification dispatched: {notification['title']}")
    return notification

def get_hr_notifications(limit: int = 20) -> List[Dict[str, Any]]:
    return NOTIFICATION_HISTORY[:limit]
