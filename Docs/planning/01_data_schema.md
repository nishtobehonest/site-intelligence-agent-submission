# Data Schema — Drone Inspection Domain
**Phase 2 · Finalized before ingest is built**

---

## Three Chroma Collections

| Collection | Source | What It Contains |
|------------|--------|-----------------|
| `inspection_records` | `generate_drone_data.py` output | Per-flight anomaly records with spatial metadata |
| `compliance_docs` | OSHA PDFs | Regulatory standards (1910.147 + 1926 Subpart Q) |
| `historical_baselines` | `generate_drone_data.py` output | What normal looks like per zone + equipment type |

---

## inspection_records Schema

Each record represents one anomaly observation from one drone flight.

```json
{
  "record_id": "INS-001",
  "site_id": "SITE-AUSTIN-01",
  "zone_id": "Zone-C",
  "flight_date": "2025-08-15",
  "equipment_type": "rooftop-hvac",
  "anomaly_type": "thermal-hotspot",
  "severity": "HIGH",
  "coordinates": "30.2672° N, 97.7431° W",
  "inspector_notes": "...",
  "compliance_flag": true,
  "resolution_status": "pending"
}
```

### Field Notes

**`zone_id`** — Must be one of: Zone-A, Zone-B, Zone-C, Zone-D, Zone-E
Stored as both text in `page_content` AND as Chroma metadata field. The metadata field is what enables `where_filter` queries.

**`flight_date`** — ISO 8601 format (YYYY-MM-DD). Stored as Chroma metadata for temporal filtering.

**`severity`** — Exactly one of: HIGH, MEDIUM, LOW. Stored as Chroma metadata.

**`inspector_notes`** — The primary field that gets embedded. Must be 4-6 sentences describing:
1. What was observed (specific anomaly description)
2. Location detail (which part of the equipment/structure)
3. Comparison to last inspection (if applicable)
4. Safety/compliance implication
5. Recommended next action

Short inspector_notes (< 2 sentences) produce weak retrieval signal. Enforce length in generation prompt.

**`coordinates`** — Plain text for now (Phase 2). Phase 3 adds map layer that uses real lat/lng floats.

### Chroma Metadata Fields (must be stored separately, not just in page_content)

```python
metadata = {
    "zone_id": record["zone_id"],         # enables filter: {"zone_id": {"$eq": "Zone-C"}}
    "flight_date": record["flight_date"],  # enables filter: {"flight_date": {"$gte": "2025-07-01"}}
    "severity": record["severity"],        # enables filter: {"severity": {"$eq": "HIGH"}}
    "site_id": record["site_id"],
    "source": "inspection_records",
    "record_id": record["record_id"]
}
```

---

## historical_baselines Schema

Each record represents the known-normal baseline for a zone + equipment type combination.

```json
{
  "baseline_id": "BASE-ZONE-C-HVAC-01",
  "zone_id": "Zone-C",
  "equipment_type": "rooftop-hvac",
  "normal_temperature_range": "68-82°F",
  "typical_anomaly_rate": "0-1 per quarter",
  "last_major_maintenance": "2025-03-01",
  "baseline_notes": "...",
  "established_date": "2024-06-01"
}
```

**`baseline_notes`** — 3-4 sentences describing what "normal" looks like for this zone/equipment:
- Typical sensor readings
- Expected maintenance schedule
- Historical anomaly patterns
- What triggers an escalation above baseline

### Chroma Metadata Fields

```python
metadata = {
    "zone_id": record["zone_id"],
    "equipment_type": record["equipment_type"],
    "source": "historical_baselines"
}
```

---

## compliance_docs Schema

OSHA documents — same as Phase 1 ingest but new collection name and different source files.

| Document | File | Collection |
|----------|------|------------|
| OSHA 29 CFR 1910.147 | Already in `data/raw/osha/` | `compliance_docs` |
| OSHA 29 CFR 1926 Subpart Q | Download from osha.gov | `compliance_docs` |

No special metadata beyond source filename. Compliance queries retrieve by semantic similarity only.

---

## Synthetic Data Generation Targets

| Collection | Records | Coverage |
|------------|---------|----------|
| inspection_records | 50 records | 5 zones × 5 equipment types × 2 sites, varied dates Aug 2024 – Dec 2025 |
| historical_baselines | 25 records | 5 zones × 5 equipment types (one baseline per combination) |

**Zone distribution for inspection_records:**
- Zone-A: 8 records
- Zone-B: 10 records
- Zone-C: 12 records (most active — makes demo queries reliable)
- Zone-D: 12 records
- Zone-E: 8 records

**Severity distribution:**
- HIGH: 15 records (30%)
- MEDIUM: 20 records (40%)
- LOW: 15 records (30%)

**Date spread:** Aug 2024 – Dec 2025. Ensures "last month" queries work relative to demo date.

---

## Sites and Zones

```
SITE-AUSTIN-01:  Zone-A, Zone-B, Zone-C
SITE-DENVER-01:  Zone-C, Zone-D, Zone-E
```

Zone-C exists at both sites — enables cross-site comparison queries in later phases.

---

## Equipment Types

- `rooftop-hvac` — thermal anomalies, refrigerant leaks
- `structural-panel` — corrosion, physical damage, missing fasteners
- `drainage-system` — blockages, moisture intrusion
- `electrical-conduit` — insulation damage, overheating
- `solar-array` — hotspots, panel damage, connection issues
