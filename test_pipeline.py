#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Pipeline & Anomaly Shield Unit Tests
---------------------------------------------------
Verifies that all shields (Scenario 2 Unit Bug, Anomaly Rejection,
Data Cleaning, and Payload Integrity) function with zero errors.
"""

import unittest
from validator import AnomalyDetector, PayloadIntegrityGate
from cleaner import DataCleaner


class TestAnomalyDetector(unittest.TestCase):

    def test_scenario_2_unit_bug_auto_correction(self):
        """Tests that clerical errors entering ₹/kg instead of ₹/quintal are auto-scaled."""
        # Wheat at ₹25/kg should auto-scale to ₹2,500/quintal
        raw_wheat = {
            "commodity": "Wheat",
            "state": "Madhya Pradesh",
            "market": "Neemuch",
            "district": "Neemuch",
            "min_price": 22,
            "max_price": 27,
            "modal_price": 25,
            "arrivals": 500
        }
        clean = AnomalyDetector.validate_and_normalize_record(raw_wheat)
        self.assertIsNotNone(clean)
        self.assertEqual(clean["modal_price"], 2500)
        self.assertEqual(clean["min_price"], 2200)
        self.assertEqual(clean["max_price"], 2700)

        # Soyabean at ₹46/kg should auto-scale to ₹4,600/quintal
        raw_soya = {
            "commodity": "Soyabean",
            "state": "Maharashtra",
            "market": "Latur",
            "district": "Latur",
            "min_price": 44,
            "max_price": 48,
            "modal_price": 46,
            "arrivals": 1200
        }
        clean_soya = AnomalyDetector.validate_and_normalize_record(raw_soya)
        self.assertIsNotNone(clean_soya)
        self.assertEqual(clean_soya["modal_price"], 4600)

        # Garlic at ₹180/kg should auto-scale to ₹18,000/quintal
        raw_garlic = {
            "commodity": "Garlic",
            "state": "Madhya Pradesh",
            "market": "Mandsaur",
            "district": "Mandsaur",
            "min_price": 120,
            "max_price": 240,
            "modal_price": 180,
            "arrivals": 3000
        }
        clean_garlic = AnomalyDetector.validate_and_normalize_record(raw_garlic)
        self.assertIsNotNone(clean_garlic)
        self.assertEqual(clean_garlic["modal_price"], 18000)

        # Onion at ₹18/kg should auto-scale to ₹1,800/quintal
        raw_onion = {
            "commodity": "Onion",
            "state": "Maharashtra",
            "market": "Lasalgaon",
            "district": "Nashik",
            "min_price": 12,
            "max_price": 24,
            "modal_price": 18,
            "arrivals": 15000
        }
        clean_onion = AnomalyDetector.validate_and_normalize_record(raw_onion)
        self.assertIsNotNone(clean_onion)
        self.assertEqual(clean_onion["modal_price"], 1800)

    def test_price_inversion_swap(self):
        """Tests that if min_price > max_price, the shield swaps them safely."""
        inverted = {
            "commodity": "Wheat",
            "state": "Haryana",
            "market": "Karnal",
            "district": "Karnal",
            "min_price": 2800,
            "max_price": 2400,
            "modal_price": 2600,
            "arrivals": 400
        }
        clean = AnomalyDetector.validate_and_normalize_record(inverted)
        self.assertIsNotNone(clean)
        self.assertTrue(clean["min_price"] <= clean["modal_price"] <= clean["max_price"])
        self.assertEqual(clean["min_price"], 2400)
        self.assertEqual(clean["max_price"], 2800)

    def test_out_of_bounds_anomaly_rejection(self):
        """Tests that absurd prices are rejected from entering the dataset."""
        # Wheat at ₹90,000/quintal (impossible typo)
        insane_wheat = {
            "commodity": "Wheat",
            "state": "Punjab",
            "market": "Ludhiana",
            "district": "Ludhiana",
            "min_price": 85000,
            "max_price": 95000,
            "modal_price": 90000,
            "arrivals": 100
        }
        self.assertIsNone(AnomalyDetector.validate_and_normalize_record(insane_wheat))

        # Record with all 0 prices
        zero_prices = {
            "commodity": "Wheat",
            "state": "Punjab",
            "market": "Ludhiana",
            "district": "Ludhiana",
            "min_price": 0,
            "max_price": 0,
            "modal_price": 0,
            "arrivals": 0
        }
        self.assertIsNone(AnomalyDetector.validate_and_normalize_record(zero_prices))


class TestDataCleaner(unittest.TestCase):

    def test_commodity_normalization(self):
        """Tests that raw government crop strings are standardized."""
        self.assertEqual(DataCleaner.clean_commodity("Arhar (Tur/Red Gram)(Whole)"), "Arhar (Tur)")
        self.assertEqual(DataCleaner.clean_commodity("Wheat(Husked)"), "Wheat")
        self.assertEqual(DataCleaner.clean_commodity("Mustard(Black)"), "Mustard")
        self.assertEqual(DataCleaner.clean_commodity("Cotton(Unginned)"), "Cotton")
        self.assertEqual(DataCleaner.clean_commodity("Onion(Red)"), "Onion")

    def test_market_normalization(self):
        """Tests that noisy market yard suffixes are stripped."""
        self.assertEqual(DataCleaner.clean_market("Lasalgaon (Niphad Yard)"), "Lasalgaon")
        self.assertEqual(DataCleaner.clean_market("Kalyan (APMC)"), "Kalyan")
        self.assertEqual(DataCleaner.clean_market("Indore(F&V)"), "Indore")


class TestPayloadIntegrityGate(unittest.TestCase):

    def test_empty_payload_fails_gate(self):
        valid, msg = PayloadIntegrityGate.verify_payload([], min_expected=10)
        self.assertFalse(valid)

    def test_valid_payload_passes_gate(self):
        sample = [
            {
                "id": f"m_{i}",
                "state": "Madhya Pradesh",
                "district": "Neemuch",
                "market": "Neemuch",
                "commodity": "Garlic",
                "modal_price": 18000,
                "arrival_date": "17-09-2026"
            } for i in range(35)
        ]
        valid, msg = PayloadIntegrityGate.verify_payload(sample, min_expected=30)
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
