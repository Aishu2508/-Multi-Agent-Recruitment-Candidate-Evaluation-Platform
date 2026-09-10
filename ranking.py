from typing import List, Dict, Any

def rank_candidates(assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks a list of candidate assessments based on composite performance:
    - Technical Score: 35%
    - Coding Score: 35%
    - Communication Score: 15%
    - Job Match %: 15%
    """
    ranked_list = []
    
    for a in assessments:
        tech = float(a.get("technical_score", 0.0))
        code = float(a.get("coding_score", 0.0))
        comm = float(a.get("communication_score", 0.0))
        match_pct = float(a.get("match_percentage", 0.0))

        composite_score = round(
            (tech * 0.35) + (code * 0.35) + (comm * 0.15) + (match_pct * 0.15),
            2
        )
        item = dict(a)
        item["composite_score"] = composite_score
        ranked_list.append(item)

    # Sort descending by composite score
    ranked_list.sort(key=lambda x: x["composite_score"], reverse=True)

    # Assign ranks
    total = len(ranked_list)
    for idx, item in enumerate(ranked_list):
        item["rank"] = idx + 1
        item["percentile"] = round(((total - idx) / max(total, 1)) * 100.0, 1)

    return ranked_list
