import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from database import SessionLocal, init_db
from models import Candidate, Job, Assessment
from services import (
    parse_resume_text, match_candidate_to_job, vector_store,
    evaluate_submission, get_coding_challenge, anonymize_candidate,
    workflow_engine
)
from agents import (
    tech_agent, screening_agent, scoring_agent, hr_agent
)

class TestAIRecruitmentSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_resume_parsing(self):
        sample_text = """
        Alex Mercer
        Email: alex.mercer@techcorp.io
        Phone: +1 555-0199
        Education:
        B.S. in Computer Science, University of California, Berkeley, 2020
        Experience:
        Senior Python Engineer at CloudScale (4 years of experience)
        Built scalable microservices using FastAPI, PostgreSQL, Docker, and Redis.
        Projects:
        Developed real-time RAG question answering pipeline using vector embeddings.
        Skills: Python, FastAPI, Docker, PostgreSQL, Redis, RAG, REST API
        """
        parsed = parse_resume_text(sample_text)
        self.assertIn("Python", parsed["skills"])
        self.assertIn("FastAPI", parsed["skills"])
        self.assertEqual(parsed["email"], "alex.mercer@techcorp.io")
        self.assertTrue(parsed["experience_years"] >= 3)
        self.assertEqual(parsed["graduation_year"], 2020)

    def test_02_jd_matching(self):
        cand_skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "Redis"]
        cand_text = "Proficient in Python, FastAPI, Docker, and PostgreSQL databases."
        req_skills = ["Python", "FastAPI", "PostgreSQL"]
        nice_skills = ["Docker", "Kubernetes"]
        jd_desc = "Seeking a Senior Backend Engineer proficient in Python, FastAPI, and PostgreSQL."

        result = match_candidate_to_job(cand_skills, cand_text, req_skills, nice_skills, jd_desc)
        self.assertEqual(len(result["missing_skills"]), 0)
        self.assertIn("Python", result["matched_skills"])
        self.assertGreaterEqual(result["match_percentage"], 100.0)
        self.assertGreater(result["semantic_search_score"], 0.0)

    def test_03_rag_vector_search(self):
        candidate_id = 999
        resume_text = "Specialized in Python distributed systems, Kafka streaming, and high concurrency."
        metadata = {"name": "Test Candidate", "skills": ["Python", "Kafka"]}
        
        vector_store.index_resume(candidate_id, resume_text, metadata)
        results = vector_store.search_resumes(query="distributed systems and Python")
        self.assertTrue(len(results) > 0)
        top_match = results[0]
        self.assertEqual(top_match["candidate_id"], candidate_id)

    def test_04_adaptive_tech_interview(self):
        skills = ["Python", "FastAPI"]
        questions = tech_agent.generate_questions(skills, count=2)
        self.assertTrue(len(questions) >= 2)

        # Evaluate Answer
        sample_answer = "The GIL in Python prevents multiple native threads from executing bytecode simultaneously. To bypass this, we use multiprocessing or process pools for CPU-bound tasks."
        eval_res = tech_agent.evaluate_answer(questions[0]["question"], sample_answer, questions[0].get("expected_concepts"))
        self.assertGreater(eval_res["score"], 50.0)
        self.assertTrue(len(eval_res["concepts_covered"]) > 0)

        # Follow-up generation
        follow_up = tech_agent.generate_follow_up(questions[0]["question"], sample_answer, "Python")
        self.assertTrue(len(follow_up["follow_up_question"]) > 10)

    def test_05_code_executor(self):
        # Test Two Sum solution in Python
        code = """def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []
"""
        eval_res = evaluate_submission(challenge_id="py_two_sum", code=code, language="python")
        self.assertEqual(eval_res["score"], 100.0)
        self.assertEqual(eval_res["passed_tests"], eval_res["total_tests"])
        self.assertEqual(eval_res["detected_time_complexity"], "O(N)")

    def test_06_communication_screening(self):
        sample_speech = "In my last team, we successfully optimized latency by forty percent and collaborated closely with product managers."
        screen_res = screening_agent.analyze_communication(sample_speech)
        self.assertEqual(screen_res["sentiment"], "Positive")
        self.assertGreaterEqual(screen_res["communication_score"], 70.0)

    def test_07_fair_scoring_and_hr_decision(self):
        cand_data = {
            "id": 12,
            "anonymized_id": "CAND-99AB",
            "name": "Jordan Smith",
            "email": "jordan@example.com",
            "gender": "Female",
            "location": "San Francisco, CA",
            "graduation_year": 2018,
            "education": ["B.S. Stanford University, 2018"],
            "skills": ["Python", "FastAPI"]
        }
        anon = anonymize_candidate(cand_data)
        self.assertEqual(anon["name"], "Candidate CAND-99AB")
        self.assertEqual(anon["email"], "[ANONYMIZED]")
        self.assertIsNone(anon["graduation_year"])

        # Final score calculation: Tech 80, Coding 90, Comm 85
        # Expected: 80*0.4 + 90*0.4 + 85*0.2 = 32 + 36 + 17 = 85.0
        score_res = scoring_agent.compute_assessment(80.0, 90.0, 85.0, cand_data)
        self.assertEqual(score_res["final_score"], 85.0)
        self.assertEqual(score_res["performance_level"], "Exceptional")

        # HR Decision
        hr_decision = hr_agent.make_decision(final_score=85.0, candidate_name="Jordan", min_threshold=70.0)
        self.assertEqual(hr_decision["decision"], "Shortlisted")
        self.assertTrue(hr_decision["notification_dispatched"])

    def test_08_fastapi_endpoints(self):
        # 1. Seed data endpoint
        seed_resp = self.client.post("/api/seed-data")
        self.assertIn(seed_resp.status_code, [200, 201])

        # 2. Get jobs
        jobs_resp = self.client.get("/api/jobs")
        self.assertEqual(jobs_resp.status_code, 200)
        jobs = jobs_resp.json()
        self.assertGreater(len(jobs), 0)

        # 3. Get candidates
        cands_resp = self.client.get("/api/candidates")
        self.assertEqual(cands_resp.status_code, 200)
        cands = cands_resp.json()
        self.assertGreater(len(cands), 0)

        # 4. Get Dashboard stats
        stats_resp = self.client.get("/api/dashboard/stats")
        self.assertEqual(stats_resp.status_code, 200)
        stats = stats_resp.json()
        self.assertIn("python_candidates", stats)
        self.assertIn("java_candidates", stats)

        # 5. Coding challenge endpoint
        challenge_resp = self.client.get("/api/assessment/coding-challenge?language=python")
        self.assertEqual(challenge_resp.status_code, 200)
        self.assertEqual(challenge_resp.json()["id"], "py_two_sum")

if __name__ == "__main__":
    unittest.main()
