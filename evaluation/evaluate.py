# PYTHONPATH=. python3 evaluation/evaluate.py
import json
import re
import time

from src.services.ai_service import generate_response  # adjust to your module path
from src.services.ollama_client import ask_ollama

JUDGE_SYSTEM = """
You are a strict QA evaluator for a Helsinki tourist assistant app.
You will be given a user input, a description of the expected behavior,
and the app's actual response.

Decide how well the actual response satisfies the expected behavior.
Judge only against the expected behavior. Do not reward length or politeness
on their own.

Verdicts:
- PASS: the response satisfies all parts of the expected behavior.
- PARTIAL: the response satisfies some parts of the expected behavior but
  misses or gets wrong at least one other part.
- FAIL: the response does not satisfy the expected behavior, or invents facts
  the app could not know (such as opening hours or prices).

Score from 0 to 10, where 10 means fully correct and 0 means completely wrong.
PASS should score 8-10, PARTIAL 4-7, FAIL 0-3.

Reply in exactly this format and nothing else:
VERDICT: PASS or PARTIAL or FAIL
SCORE: a whole number from 0 to 10
MISSING: what is missing or wrong, or "none"
REASON: one short sentence
"""

VERDICT_RE = re.compile(r"VERDICT:\s*(PASS|PARTIAL|FAIL)", re.IGNORECASE)
SCORE_RE = re.compile(r"SCORE:\s*(\d{1,2})", re.IGNORECASE)
MISSING_RE = re.compile(r"MISSING:\s*(.+?)(?:\n|$)", re.IGNORECASE)
REASON_RE = re.compile(r"REASON:\s*(.+)", re.IGNORECASE | re.DOTALL)

VERDICT_TO_SCORE_RANGE = {
    "PASS": (8, 10),
    "PARTIAL": (4, 7),
    "FAIL": (0, 3),
}


def parse_judge_output(raw):
    verdict_match = VERDICT_RE.search(raw)
    if not verdict_match:
        return None

    verdict = verdict_match.group(1).upper()

    score_match = SCORE_RE.search(raw)
    score = min(int(score_match.group(1)), 10) if score_match else None

    # If the score contradicts the verdict, trust the verdict and clamp the score
    if score is not None:
        low, high = VERDICT_TO_SCORE_RANGE[verdict]
        score = max(low, min(score, high))

    missing_match = MISSING_RE.search(raw)
    reason_match = REASON_RE.search(raw)

    return {
        "verdict": verdict,
        "score": score,
        "missing": missing_match.group(1).strip() if missing_match else "",
        "reason": reason_match.group(1).strip() if reason_match else "",
    }


def judge(case, actual, retries=2):
    prompt = (
        f"USER INPUT:\n{case['input']!r}\n\n"
        f"EXPECTED BEHAVIOR:\n{case['expected_behavior']}\n\n"
        f"ACTUAL RESPONSE:\n{actual}\n\n"
        "How well does the actual response satisfy the expected behavior?"
    )

    raw = ""
    for _ in range(retries + 1):
        raw = ask_ollama(prompt=prompt, system_message=JUDGE_SYSTEM).strip()
        parsed = parse_judge_output(raw)
        if parsed:
            parsed["raw"] = raw
            return parsed

    return {
        "verdict": "ERROR",
        "score": None,
        "missing": "",
        "reason": "Judge output could not be parsed",
        "raw": raw,
    }


def main(path="evaluation/test_cases.json", out_path="results.json"):
    with open(path, encoding="utf-8") as f:
        cases = json.load(f)

    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "ERROR": 0}
    scores = []

    for case in cases:
        started = time.time()

        try:
            actual = generate_response(case["input"])
        except Exception as e:
            actual = f"<EXCEPTION: {e}>"

        result = judge(case, actual)
        verdict = result["verdict"]

        case["actual_result"] = actual
        case["status"] = verdict.lower()
        case["judge_score"] = result["score"]
        case["judge_missing"] = result["missing"]
        case["judge_reason"] = result["reason"]
        case["judge_raw"] = result["raw"]

        counts[verdict] += 1
        if result["score"] is not None:
            scores.append(result["score"])

        score_text = f"{result['score']}/10" if result["score"] is not None else "n/a"
        print(
            f"{case['id']:8} {case['category']:16} {verdict:8} {score_text:6} "
            f"({time.time() - started:.1f}s)  {result['reason']}"
        )

    total = len(cases)
    avg = sum(scores) / len(scores) if scores else 0
    print(
        f"\n{counts['PASS']} pass, {counts['PARTIAL']} partial, "
        f"{counts['FAIL']} fail, {counts['ERROR']} judge errors "
        f"(of {total})"
    )
    print(f"Average score: {avg:.1f}/10")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()