"""
demo.py
-------
CLI demo for live presentation.
Shows all three graceful degradation routing paths.

Usage: python demo/demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant import FieldServiceAssistant

DIVIDER = "\n" + "=" * 70 + "\n"

# Three demo queries — one per routing path
DEMO_QUERIES = [
    {
        "label": "DEMO 1: HIGH CONFIDENCE",
        "description": "Clear question with a well-documented answer in the corpus.",
        "query": "What are the steps for the lockout tagout energy control procedure?"
    },
    {
        "label": "DEMO 2: PARTIAL CONFIDENCE (conflict)",
        "description": "Question where two sources may return different guidance.",
        "query": "What is the recommended refrigerant charge pressure for a Carrier rooftop unit?"
    },
    {
        "label": "DEMO 3: LOW CONFIDENCE (escalation)",
        "description": "Question about equipment not covered in the corpus — triggers escalation.",
        "query": "What are the repair procedures for a Daikin VRV system model DX300?"
    }
]


def print_result(result: dict):
    print(f"\nQuery: {result['query']}")
    print(f"Confidence: {result['confidence_level']} (top score: {result['top_score']:.2f})")
    print(f"Route: {result['route_type']} | Escalate: {result['escalate']}")
    print(f"\nResponse:\n{result['response']}")


def run_interactive(assistant: FieldServiceAssistant):
    print("\nInteractive mode. Type your question or 'quit' to exit.\n")
    while True:
        query = input("Technician query: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue
        result = assistant.ask(query)
        print_result(result)
        print(DIVIDER)


def main():
    print(DIVIDER)
    print("SITE INTELLIGENCE AGENT")
    print("Site Intelligence Agent | April 2026")
    print(DIVIDER)

    print("Loading assistant...")
    assistant = FieldServiceAssistant()
    print("Ready.\n")

    mode = input("Run [D]emo queries or [I]nteractive mode? (D/I): ").strip().upper()

    if mode == "I":
        run_interactive(assistant)
        return

    # Demo mode: run all three preset queries
    for demo in DEMO_QUERIES:
        print(DIVIDER)
        print(f">>> {demo['label']}")
        print(f"    {demo['description']}")
        result = assistant.ask(demo["query"])
        print_result(result)
        input("\n[Press Enter for next demo]")

    print(DIVIDER)
    print("Demo complete.")


if __name__ == "__main__":
    main()
