#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Zero-Error Data Validator & Anomaly Shield
---------------------------------------------------------
Protects against:
1. Scenario 2 Unit Bugs: Auto-detects and corrects ₹/kg to ₹/quintal clerical errors.
2. Price Inversion: Ensures min_price <= modal_price <= max_price.
3. Impossible Outliers: Discards typos (e.g. Wheat at ₹80,000 or ₹0).
4. Pre-Commit Payload Gate: Aborts if incoming data is corrupted or too sparse.
"""

from typing import Dict, Any, Optional, Tuple, List

# Realistic market sanity price bounds (in ₹/quintal)
# Format: (per_kg_threshold, min_valid_quintal, max_valid_quintal)
CROP_PRICE_BOUNDS: Dict[str, Tuple[float, float, float]] = {
    # Grains
    "Wheat": (150.0, 800.0, 8000.0),
    "Paddy(Dhan)": (150.0, 1000.0, 9000.0),
    "Basmati Rice": (250.0, 2000.0, 16000.0),
    "Maize": (120.0, 700.0, 6000.0),
    "Bajra": (120.0, 700.0, 5500.0),
    "Barley (Jau)": (120.0, 700.0, 5500.0),

    # Oilseeds
    "Soyabean": (200.0, 1500.0, 12000.0),
    "Mustard": (200.0, 2000.0, 14000.0),
    "Groundnut": (250.0, 2500.0, 18000.0),
    "Castor Seed": (200.0, 2000.0, 12000.0),
    "Sesame(Til)": (350.0, 4000.0, 25000.0),

    # Commercial / Cash
    "Cotton": (250.0, 3000.0, 16000.0),

    # Pulses
    "Bengal Gram(Gram)": (200.0, 2500.0, 14000.0),
    "Kabuli Chana": (300.0, 3500.0, 22000.0),
    "Arhar (Tur)": (250.0, 3000.0, 18000.0),
    "Moong(Green Gram)": (250.0, 3000.0, 18000.0),
    "Urad(Black Gram)": (250.0, 3000.0, 18000.0),
    "Masoor": (200.0, 2500.0, 14000.0),

    # Spices & Others
    "Garlic": (250.0, 1500.0, 45000.0),
    "Cumin Seed(Jeera)": (600.0, 8000.0, 80000.0),
    "Coriander(Seed)": (250.0, 2500.0, 25000.0),
    "Turmeric": (250.0, 3000.0, 28000.0),
    "Red Chilli": (350.0, 4000.0, 45000.0),
    "Ginger(Green)": (150.0, 1500.0, 25000.0),

    # Fruits & Vegetables
    "Apple": (150.0, 1000.0, 30000.0),
    "Onion": (80.0, 200.0, 12000.0),
    "Potato": (80.0, 200.0, 8000.0),
    "Tomato": (80.0, 200.0, 12000.0),
}

# Generic fallback for unlisted crops
DEFAULT_BOUNDS = (100.0, 200.0, 100000.0)


class AnomalyDetector:
    """Detects and fixes price unit bugs and clerical anomalies."""

    @staticmethod
    def validate_and_normalize_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validates and fixes a single mandi price record.
        Returns cleaned record, or None if the record is irrecoverably corrupt.
        """
        commodity = record.get("commodity", "").strip()
        state = record.get("state", "").strip()
        market = record.get("market", "").strip()

        if not commodity or not state or not market:
            return None

        try:
            min_p = float(record.get("min_price", 0) or 0)
            max_p = float(record.get("max_price", 0) or 0)
            modal_p = float(record.get("modal_price", 0) or 0)
            arrivals = int(float(record.get("arrivals", 0) or 0))
        except (ValueError, TypeError):
            return None

        # Fix zero modal price if min and max exist
        if modal_p <= 0:
            if max_p > 0:
                modal_p = (min_p + max_p) / 2
            elif min_p > 0:
                modal_p = min_p
            else:
                return None  # All prices are zero, discard

        # Fix missing min or max
        if min_p <= 0:
            min_p = modal_p * 0.9
        if max_p <= 0:
            max_p = modal_p * 1.1

        # Fix inverted prices: if min > max, swap them
        if min_p > max_p:
            min_p, max_p = max_p, min_p

        # Ensure modal_p stays within [min_p, max_p]
        modal_p = max(min_p, min(modal_p, max_p))

        # --- SHIELD: SCENARIO 2 UNIT BUG CORRECTION (₹/kg -> ₹/quintal) ---
        bounds = CROP_PRICE_BOUNDS.get(commodity, DEFAULT_BOUNDS)
        per_kg_threshold, min_valid, max_valid = bounds

        if modal_p < per_kg_threshold:
            # The government feed likely entered ₹/kg instead of ₹/quintal!
            # E.g. Wheat at ₹25/kg -> auto-scale by 100 -> ₹2,500/quintal
            modal_p *= 100
            min_p *= 100
            max_p *= 100

        # --- SHIELD: HARD SANITY BOUNDS CHECK ---
        if modal_p < min_valid or modal_p > max_valid:
            # Beyond any reasonable biological/economic limit, reject anomaly
            return None

        clean_record = dict(record)
        clean_record["min_price"] = int(round(min_p))
        clean_record["max_price"] = int(round(max_p))
        clean_record["modal_price"] = int(round(modal_p))
        clean_record["arrivals"] = max(0, arrivals)
        return clean_record


class PayloadIntegrityGate:
    """Pre-commit verification to prevent corrupted data from overwriting today.json."""

    @staticmethod
    def verify_payload(records: List[Dict[str, Any]], min_expected: int = 30) -> Tuple[bool, str]:
        """
        Verifies the full payload meets quality standards.
        Returns (is_valid, reason).
        """
        if not records or len(records) < min_expected:
            return False, f"Record count ({len(records) if records else 0}) is below minimum threshold ({min_expected})."

        required_keys = {"id", "state", "district", "market", "commodity", "modal_price", "arrival_date"}
        for idx, r in enumerate(records):
            missing = required_keys - set(r.keys())
            if missing:
                return False, f"Record at index {idx} ({r.get('id', 'unknown')}) is missing required keys: {missing}"

            if r.get("modal_price", 0) <= 0:
                return False, f"Record at index {idx} has invalid modal_price <= 0"

        return True, f"Payload verified successfully with {len(records)} records."
