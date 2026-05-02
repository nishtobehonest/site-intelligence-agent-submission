"""
generate_drone_data.py
----------------------
Generates synthetic drone inspection data for Phase 2.

Output:
  data/raw/drone/inspection_records.json   — 50 anomaly records with spatial metadata
  data/raw/drone/historical_baselines.json — 25 zone/equipment baseline records

Usage: python src/generate_drone_data.py
"""

import os
import json
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from src import llm

load_dotenv()

INSPECTION_OUTPUT = "./data/raw/drone/inspection_records.json"
BASELINES_OUTPUT = "./data/raw/drone/historical_baselines.json"

EQUIPMENT_TYPES = [
    "rooftop-hvac",
    "structural-panel",
    "drainage-system",
    "electrical-conduit",
    "solar-array",
]

ANOMALY_TYPES_BY_EQUIPMENT = {
    "rooftop-hvac": ["thermal-hotspot", "refrigerant-leak", "compressor-vibration", "condenser-blockage"],
    "structural-panel": ["corrosion", "physical-damage", "missing-fasteners", "surface-delamination"],
    "drainage-system": ["blockage", "moisture-intrusion", "pipe-separation", "sediment-buildup"],
    "electrical-conduit": ["insulation-damage", "overheating", "exposed-wiring", "conduit-breach"],
    "solar-array": ["panel-hotspot", "cell-damage", "connection-failure", "soiling-pattern"],
}

SITES = {
    "SITE-AUSTIN-01": ["Zone-A", "Zone-B", "Zone-C"],
    "SITE-DENVER-01": ["Zone-C", "Zone-D", "Zone-E"],
}

ZONE_DISTRIBUTION = {
    "Zone-A": 8,
    "Zone-B": 10,
    "Zone-C": 12,
    "Zone-D": 12,
    "Zone-E": 8,
}

SEVERITY_POOL = ["HIGH"] * 15 + ["MEDIUM"] * 20 + ["LOW"] * 15

NOTES_PROMPT = """You are a drone inspection AI writing a field report entry.
Generate realistic inspector_notes for a drone anomaly observation. Return ONLY the notes text, no JSON, no labels.
The notes must be 4-6 sentences covering:
1. What was observed (specific anomaly description with measurements or visual detail)
2. Location within the equipment/structure (e.g. "north-facing panel", "unit compressor bay")
3. Comparison to last inspection (improved, worsened, new finding)
4. Safety or compliance implication
5. Recommended next action

Site: {site_id}
Zone: {zone_id}
Equipment: {equipment_type}
Anomaly: {anomaly_type}
Severity: {severity}
Flight date: {flight_date}"""

BASELINE_PROMPT = """You are a drone inspection AI writing a historical baseline record.
Generate realistic baseline_notes for a zone/equipment combination. Return ONLY the notes text, no JSON, no labels.
The notes must be 3-4 sentences covering:
1. Typical sensor readings and visual condition under normal operation
2. Expected maintenance schedule and last major service
3. Historical anomaly frequency and typical patterns
4. Threshold that would trigger escalation above baseline

Zone: {zone_id}
Equipment: {equipment_type}"""


def random_flight_date() -> str:
    start = date(2024, 8, 1)
    end = date(2025, 12, 31)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def site_for_zone(zone_id: str) -> str:
    for site, zones in SITES.items():
        if zone_id in zones:
            candidates = [s for s, zs in SITES.items() if zone_id in zs]
            return random.choice(candidates)
    return "SITE-AUSTIN-01"


def generate_inspection_records() -> list[dict]:
    records = []
    severity_pool = SEVERITY_POOL.copy()
    random.shuffle(severity_pool)
    severity_iter = iter(severity_pool)

    record_num = 1
    for zone_id, count in ZONE_DISTRIBUTION.items():
        for _ in range(count):
            equipment_type = random.choice(EQUIPMENT_TYPES)
            anomaly_type = random.choice(ANOMALY_TYPES_BY_EQUIPMENT[equipment_type])
            severity = next(severity_iter)
            flight_date = random_flight_date()
            site_id = site_for_zone(zone_id)

            prompt = NOTES_PROMPT.format(
                site_id=site_id,
                zone_id=zone_id,
                equipment_type=equipment_type,
                anomaly_type=anomaly_type,
                severity=severity,
                flight_date=flight_date,
            )
            inspector_notes = llm.generate(prompt).strip()

            record = {
                "record_id": f"INS-{record_num:03d}",
                "site_id": site_id,
                "zone_id": zone_id,
                "flight_date": flight_date,
                "equipment_type": equipment_type,
                "anomaly_type": anomaly_type,
                "severity": severity,
                "coordinates": _coords_for_site(site_id, zone_id),
                "inspector_notes": inspector_notes,
                "compliance_flag": severity == "HIGH",
                "resolution_status": random.choice(["pending", "in-progress", "resolved"]),
            }
            records.append(record)
            print(f"  [OK] INS-{record_num:03d} | {zone_id} | {equipment_type} | {severity}")
            record_num += 1

    return records


def generate_historical_baselines() -> list[dict]:
    baselines = []
    num = 1
    for zone_id in ZONE_DISTRIBUTION:
        for equipment_type in EQUIPMENT_TYPES:
            prompt = BASELINE_PROMPT.format(zone_id=zone_id, equipment_type=equipment_type)
            baseline_notes = llm.generate(prompt).strip()

            baseline = {
                "baseline_id": f"BASE-{zone_id.replace('-', '')}-{equipment_type.upper().replace('-', '')}-{num:02d}",
                "zone_id": zone_id,
                "equipment_type": equipment_type,
                "normal_temperature_range": _temp_range(equipment_type),
                "typical_anomaly_rate": _anomaly_rate(equipment_type),
                "last_major_maintenance": _last_maintenance(),
                "baseline_notes": baseline_notes,
                "established_date": "2024-06-01",
            }
            baselines.append(baseline)
            print(f"  [OK] Baseline | {zone_id} | {equipment_type}")
            num += 1

    return baselines


def _coords_for_site(site_id: str, zone_id: str) -> str:
    base = {
        "SITE-AUSTIN-01": (30.2672, -97.7431),
        "SITE-DENVER-01": (39.7392, -104.9903),
    }
    lat, lng = base.get(site_id, (30.2672, -97.7431))
    offset = {"Zone-A": 0.001, "Zone-B": 0.002, "Zone-C": 0.003, "Zone-D": 0.004, "Zone-E": 0.005}
    lat += offset.get(zone_id, 0)
    return f"{lat:.4f}° N, {abs(lng):.4f}° W"


def _temp_range(equipment_type: str) -> str:
    ranges = {
        "rooftop-hvac": "68-82°F",
        "structural-panel": "60-95°F",
        "drainage-system": "55-80°F",
        "electrical-conduit": "65-90°F",
        "solar-array": "70-110°F",
    }
    return ranges.get(equipment_type, "65-85°F")


def _anomaly_rate(equipment_type: str) -> str:
    rates = {
        "rooftop-hvac": "0-1 per quarter",
        "structural-panel": "0-2 per year",
        "drainage-system": "1-2 per year",
        "electrical-conduit": "0-1 per year",
        "solar-array": "0-1 per quarter",
    }
    return rates.get(equipment_type, "0-1 per year")


def _last_maintenance() -> str:
    dates = ["2024-03-01", "2024-06-15", "2024-09-01", "2025-01-10", "2025-04-01"]
    return random.choice(dates)


def main():
    os.makedirs(os.path.dirname(INSPECTION_OUTPUT), exist_ok=True)

    print("=== Generating drone inspection records (50) ===")
    records = generate_inspection_records()
    with open(INSPECTION_OUTPUT, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Saved {len(records)} records to {INSPECTION_OUTPUT}\n")

    print("=== Generating historical baselines (25) ===")
    baselines = generate_historical_baselines()
    with open(BASELINES_OUTPUT, "w") as f:
        json.dump(baselines, f, indent=2)
    print(f"Saved {len(baselines)} baselines to {BASELINES_OUTPUT}\n")

    print("Done. Next: python src/ingest.py --domain drone")


if __name__ == "__main__":
    main()
