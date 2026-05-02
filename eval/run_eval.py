"""
run_eval.py
-----------
Evaluation runner. Tests the assistant against three eval sets:
  - ground_truth.json   : 50 curated query-answer pairs
  - adversarial.json    : 20 queries with no correct answer (should escalate)
  - contradictions.json : 15 contradiction scenarios (should surface conflict)

Outputs a metrics table and saves results to eval_results.csv.

Usage: python eval/run_eval.py
"""

import sys
import os
import json
import csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant import FieldServiceAssistant

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = "eval_results.csv"


def load_json(filename: str) -> list:
    path = os.path.join(EVAL_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARN] Eval file not found: {path}")
        return []
    with open(path) as f:
        return json.load(f)


def run_ground_truth(assistant, records: list) -> dict:
    """
    Ground truth: system should return HIGH or PARTIAL confidence.
    LOW confidence on a known question = failure.
    """
    results = []
    correct = 0
    for r in records:
        result = assistant.ask(r["query"])
        passed = result["confidence_level"] != "LOW"
        if passed:
            correct += 1
        results.append({
            "set": "ground_truth",
            "query": r["query"],
            "expected_confidence": "HIGH or PARTIAL",
            "actual_confidence": result["confidence_level"],
            "passed": passed,
            "top_score": result["top_score"]
        })
    return {"results": results, "passed": correct, "total": len(records)}


def run_adversarial(assistant, records: list) -> dict:
    """
    Adversarial: system should return LOW confidence (escalate), NOT hallucinate.
    Confident answer on an adversarial query = hallucination failure.
    """
    results = []
    correct = 0
    for r in records:
        result = assistant.ask(r["query"])
        passed = result["confidence_level"] == "LOW"
        if passed:
            correct += 1
        results.append({
            "set": "adversarial",
            "query": r["query"],
            "expected_confidence": "LOW",
            "actual_confidence": result["confidence_level"],
            "passed": passed,
            "top_score": result["top_score"]
        })
    return {"results": results, "passed": correct, "total": len(records)}


def run_contradictions(assistant, records: list) -> dict:
    """
    Contradictions: system should return PARTIAL confidence (conflict detected).
    HIGH or LOW = failure to surface the conflict.
    """
    results = []
    correct = 0
    for r in records:
        result = assistant.ask(r["query"])
        passed = result["confidence_level"] == "PARTIAL"
        if passed:
            correct += 1
        results.append({
            "set": "contradictions",
            "query": r["query"],
            "expected_confidence": "PARTIAL",
            "actual_confidence": result["confidence_level"],
            "passed": passed,
            "top_score": result["top_score"]
        })
    return {"results": results, "passed": correct, "total": len(records)}


def print_summary(label: str, stats: dict):
    pct = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    print(f"  {label}: {stats['passed']}/{stats['total']} passed ({pct:.1f}%)")


def main():
    print("=== Site Intelligence Agent: Evaluation Run ===\n")
    assistant = FieldServiceAssistant()

    ground_truth = load_json("ground_truth.json")
    adversarial = load_json("adversarial.json")
    contradictions = load_json("contradictions.json")

    all_results = []

    print("Running ground truth eval...")
    gt_stats = run_ground_truth(assistant, ground_truth) if ground_truth else {"results": [], "passed": 0, "total": 0}
    all_results.extend(gt_stats["results"])

    print("Running adversarial eval...")
    adv_stats = run_adversarial(assistant, adversarial) if adversarial else {"results": [], "passed": 0, "total": 0}
    all_results.extend(adv_stats["results"])

    print("Running contradiction eval...")
    con_stats = run_contradictions(assistant, contradictions) if contradictions else {"results": [], "passed": 0, "total": 0}
    all_results.extend(con_stats["results"])

    # Print summary
    print("\n=== RESULTS SUMMARY ===")
    print_summary("Ground truth (should NOT escalate)", gt_stats)
    print_summary("Adversarial  (should escalate = LOW)", adv_stats)
    print_summary("Contradictions (should flag PARTIAL)", con_stats)

    total_passed = gt_stats["passed"] + adv_stats["passed"] + con_stats["passed"]
    total_all = gt_stats["total"] + adv_stats["total"] + con_stats["total"]
    overall_pct = (total_passed / total_all * 100) if total_all > 0 else 0
    print(f"\n  OVERALL: {total_passed}/{total_all} ({overall_pct:.1f}%)")

    # Save to CSV
    if all_results:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nDetailed results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
