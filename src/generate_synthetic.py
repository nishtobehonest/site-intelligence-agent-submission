"""
generate_synthetic.py
---------------------
Generates synthetic job history records using the Claude API.
Output: data/raw/job_history/synthetic_jobs.json

Run once to populate the job history corpus.
Usage: python src/generate_synthetic.py --count 50
"""

import os
import json
import argparse
from dotenv import load_dotenv
from src import llm

load_dotenv()

OUTPUT_PATH = "./data/raw/job_history/synthetic_jobs.json"

EQUIPMENT_TYPES = [
    "Carrier RTU-48XL (rooftop HVAC unit)",
    "Trane XR15 (split system heat pump)",
    "Lennox SL280V (gas furnace)",
    "York YZV (variable capacity heat pump)",
    "Daikin DX13SA (central air conditioner)"
]

JOB_TYPES = ["preventive_maintenance", "emergency_repair", "inspection", "installation", "compliance_check"]
SITES = ["SITE-CHICAGO-01", "SITE-CHICAGO-02", "SITE-DALLAS-01", "SITE-NYC-01", "SITE-HOUSTON-01"]

GENERATION_PROMPT = """Generate a realistic field service job history record for an HVAC technician. 
Return ONLY valid JSON with this exact schema, no other text:

{{
  "job_id": "JOB-{job_num:03d}",
  "date": "2024-{month:02d}-{day:02d}",
  "equipment_id": "{equipment_id}",
  "equipment_type": "{equipment_type}",
  "job_type": "{job_type}",
  "site_id": "{site_id}",
  "technician_notes": "detailed notes about what was found and done (2-4 sentences)",
  "anomalies_flagged": ["list of any issues found, empty list if none"],
  "resolution": "what was done to resolve the issue or complete the job",
  "parts_replaced": ["list of any parts replaced, empty list if none"],
  "compliance_notes": "any compliance or safety notes relevant to this job",
  "follow_up_required": true or false,
  "job_duration_hours": a number between 0.5 and 8
}}

Equipment: {equipment_type}
Job type: {job_type}
Site: {site_id}
Make the technician notes realistic and specific to the equipment type and job."""


def generate_record(job_num: int) -> dict:
    import random
    equipment_type = random.choice(EQUIPMENT_TYPES)
    equipment_id = equipment_type.split("(")[0].strip().upper().replace(" ", "-")
    job_type = random.choice(JOB_TYPES)
    site_id = random.choice(SITES)
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    prompt = GENERATION_PROMPT.format(
        job_num=job_num,
        month=month,
        day=day,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        job_type=job_type,
        site_id=site_id
    )

    text = llm.generate(prompt).strip()
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50, help="Number of records to generate")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    records = []
    print(f"Generating {args.count} synthetic job history records...")

    for i in range(1, args.count + 1):
        try:
            record = generate_record(i)
            records.append(record)
            print(f"  [OK] Record {i}/{args.count}: {record.get('job_id')} - {record.get('job_type')}")
        except Exception as e:
            print(f"  [ERR] Record {i} failed: {e}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"\nDone. {len(records)} records saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
