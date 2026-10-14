import json
import re

def evaluate_verdict(raw_judge_output: str) -> dict:
    """
    Parses and enforces the quantitative judge scorecard.
    Guarantees that a discovery only passes if total >= 0.80 
    and no single metric drops below 0.60.
    """
    # Clean possible markdown block formatting
    cleaned = raw_judge_output.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        scorecard = json.loads(cleaned)
    except Exception as e:
        return {
            "verdict": "REJECTED",
            "total_score": 0.0,
            "reason": f"Failed to parse Judge JSON output: {e}",
            "raw": raw_judge_output
        }

    falsifiability = float(scorecard.get("falsifiability_score", 0.0))
    math_consistency = float(scorecard.get("math_consistency_score", 0.0))
    novelty = float(scorecard.get("novelty_score", 0.0))
    grounding = float(scorecard.get("grounding_score", 0.0))

    # Recalculate explicitly in Python to prevent hallucinated averages
    total = (
        (0.35 * falsifiability)
        + (0.25 * math_consistency)
        + (0.25 * novelty)
        + (0.15 * grounding)
    )

    passed_subscores = (
        falsifiability >= 0.60
        and math_consistency >= 0.60
        and novelty >= 0.60
        and grounding >= 0.60
    )

    is_accepted = (total >= 0.80) and passed_subscores

    return {
        "verdict": "ACCEPTED" if is_accepted else "REJECTED",
        "total_score": round(total, 3),
        "subscores": {
            "falsifiability": falsifiability,
            "math_consistency": math_consistency,
            "novelty": novelty,
            "grounding": grounding
        },
        "critical_flaw": scorecard.get("critical_flaw", "Subscore or threshold gate failed"),
        "kill_condition": scorecard.get("kill_condition_analyzed", "None specified"),
        "summary": scorecard.get("review_summary", "")
    }