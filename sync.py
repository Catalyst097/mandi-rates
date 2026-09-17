#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Production National Daily Mandi Sync & Shield Pipeline
---------------------------------------------------------------------
Coordinates fetching, data cleaning, anomaly detection (including ₹/kg
Scenario 2 auto-unit correction), and pre-commit integrity validation.
"""

import os
import sys
import json
from datetime import datetime
from fetcher import MandiDataFetcher
from cleaner import DataCleaner
from validator import AnomalyDetector, PayloadIntegrityGate


def run_pipeline():
    print("==================================================")
    print("   BHARATMANDI NATIONAL DATA PIPELINE & SHIELD   ")
    print("==================================================")

    # 1. Fetch raw national records
    raw_records = MandiDataFetcher.fetch_all()
    if not raw_records:
        print("[CRITICAL] No raw records fetched from any source. Aborting to protect existing data.")
        sys.exit(1)

    print(f"[INFO] Processing {len(raw_records)} raw records through Cleaner & Anomaly Shield...")

    today_str = datetime.now().strftime("%d-%m-%Y")
    cleaned_records = []
    unit_corrected_count = 0
    rejected_count = 0

    for i, raw in enumerate(raw_records):
        # Step 1: Clean and standardize names
        std = DataCleaner.clean_record(raw)

        # Record original price to check if unit auto-correction triggered
        orig_modal = float(raw.get("modal_price", 0) or 0)

        # Step 2: Pass through Zero-Error Anomaly Detector
        validated = AnomalyDetector.validate_and_normalize_record(std)

        if not validated:
            rejected_count += 1
            continue

        # Check if Scenario 2 unit bug correction occurred
        if orig_modal > 0 and orig_modal < 300 and validated["modal_price"] >= orig_modal * 50:
            unit_corrected_count += 1

        validated["id"] = raw.get("id") or f"mandi_{i+1:04d}"
        validated["arrival_date"] = raw.get("arrival_date") or today_str
        validated["trend"] = raw.get("trend") or "stable"
        validated["change_amount"] = raw.get("change_amount", 0)
        cleaned_records.append(validated)

    print(f"[SHIELD STATS] Cleaned & Validated: {len(cleaned_records)} records.")
    print(f"[SHIELD STATS] Unit-Bug Auto-Corrected: {unit_corrected_count} records.")
    print(f"[SHIELD STATS] Anomalies Quarantined/Rejected: {rejected_count} records.")

    # Step 3: Pre-Commit Payload Integrity Gate
    is_valid, reason = PayloadIntegrityGate.verify_payload(cleaned_records, min_expected=30)
    if not is_valid:
        print(f"[PRE-COMMIT GATE FAILED] {reason}")
        print("[ABORT] Refusing to overwrite today.json with questionable data.")
        sys.exit(1)

    # Step 4: Write clean, verified today.json
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "today.json")

    payload = {
        "records": cleaned_records,
        "generated_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "total": len(cleaned_records),
        "states_covered": len(set(r["state"] for r in cleaned_records)),
        "mandis_covered": len(set(r["market"] for r in cleaned_records)),
        "commodities_covered": len(set(r["commodity"] for r in cleaned_records))
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Published {out_file}:")
    print(f"  • Total Records: {payload['total']}")
    print(f"  • States: {payload['states_covered']}")
    print(f"  • Mandis: {payload['mandis_covered']}")
    print(f"  • Commodities: {payload['commodities_covered']}")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()
