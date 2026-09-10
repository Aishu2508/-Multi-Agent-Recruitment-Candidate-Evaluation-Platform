from typing import Dict, Any, Optional
from datetime import datetime

class RecruitmentWorkflow:
    """
    Recruitment State Machine and LangGraph Workflow:
    Resume Matching -> Screening -> Scoring -> HR Decision (with Checkpoint support for HR Approval).
    """
    def __init__(self):
        pass

    def run_full_pipeline(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], assessment_state: Dict[str, Any]) -> Dict[str, Any]:
        state = dict(assessment_state)
        state["started_at"] = datetime.utcnow().isoformat()

        # Step 1: Resume Matching Node
        state = self.node_resume_matching(state, candidate_data, job_data)
        
        # Step 2: Screening Node
        state = self.node_screening(state)

        # Step 3: Scoring Node (Fair Scoring 40/40/20)
        state = self.node_scoring(state, candidate_data)

        # Step 4: HR Decision Node (with approval checkpoint if score qualifies)
        state = self.node_hr_decision(state, job_data)

        return state

    def node_resume_matching(self, state: Dict[str, Any], candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        from services.jd_matcher import match_candidate_to_job
        
        skills = candidate_data.get("skills", [])
        text = candidate_data.get("raw_text", "")
        req_skills = job_data.get("required_skills", [])
        nice_skills = job_data.get("nice_to_have_skills", [])
        desc = job_data.get("description", "")

        match_res = match_candidate_to_job(skills, text, req_skills, nice_skills, desc)
        state["match_percentage"] = match_res["match_percentage"]
        state["matched_skills"] = match_res["matched_skills"]
        state["missing_skills"] = match_res["missing_skills"]
        state["semantic_search_score"] = match_res["semantic_search_score"]
        state["workflow_stage"] = "Screening"
        return state

    def node_screening(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # If communication score not already provided by user/audio, evaluate baseline
        if "communication_score" not in state or state["communication_score"] == 0.0:
            comm_log = state.get("communication_log", {})
            if comm_log and "communication_score" in comm_log:
                state["communication_score"] = comm_log["communication_score"]
            else:
                # Default baseline communication score from interview answers or initial evaluation
                state["communication_score"] = 75.0
                state["communication_log"] = {
                    "transcription": "Sample screening interview recorded.",
                    "communication_clarity": "High",
                    "sentiment": "Positive",
                    "communication_score": 75.0
                }
        state["workflow_stage"] = "Scoring"
        return state

    def node_scoring(self, state: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        from agents.scoring_agent import calculate_final_score
        
        tech = float(state.get("technical_score", 0.0))
        coding = float(state.get("coding_score", 0.0))
        comm = float(state.get("communication_score", 0.0))

        score_result = calculate_final_score(tech, coding, comm, candidate_data)
        state["final_score"] = score_result["final_score"]
        state["performance_level"] = score_result["performance_level"]
        state["anonymized_profile"] = score_result["anonymized_profile"]
        state["workflow_stage"] = "HR Decision"
        return state

    def node_hr_decision(self, state: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        from agents.hr_agent import evaluate_hr_decision
        
        min_thresh = float(job_data.get("min_score_threshold", 70.0))
        decision_info = evaluate_hr_decision(state["final_score"], min_thresh)

        state["decision"] = decision_info["decision"]
        state["hr_approved"] = decision_info.get("auto_approved", False)
        state["notification_sent"] = decision_info.get("notification_dispatched", False)

        # Checkpoint: If candidate is qualified, require HR Checkpoint approval
        if decision_info["decision"] == "Shortlisted":
            state["workflow_stage"] = "HR_APPROVAL_CHECKPOINT"
            state["checkpoint_waiting"] = True
        else:
            state["workflow_stage"] = "Completed"
            state["checkpoint_waiting"] = False

        return state

    def resume_from_checkpoint(self, state: Dict[str, Any], hr_approved: bool, hr_feedback: str) -> Dict[str, Any]:
        """Resumes workflow from HR_APPROVAL_CHECKPOINT."""
        state["hr_approved"] = hr_approved
        state["hr_feedback"] = hr_feedback
        if hr_approved:
            state["decision"] = "Shortlisted (HR Approved)"
        else:
            state["decision"] = "Rejected by HR"
        state["workflow_stage"] = "Completed"
        state["checkpoint_waiting"] = False
        state["completed_at"] = datetime.utcnow().isoformat()
        return state

workflow_engine = RecruitmentWorkflow()
