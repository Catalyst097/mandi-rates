#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Commodity & Market Name Normalizer
-------------------------------------------------
Cleans messy government strings from Agmarknet into clean,
standardized names that match our app's search engine and dictionary.
"""

import re
from typing import Dict, Any, Optional

COMMODITY_MAPPING: Dict[str, str] = {
    # Wheat
    "wheat": "Wheat",
    "wheat(husked)": "Wheat",
    "sharbati": "Wheat",
    "dara": "Wheat",

    # Soyabean
    "soyabean": "Soyabean",
    "soyabean(yellow)": "Soyabean",
    "soya": "Soyabean",

    # Onion
    "onion": "Onion",
    "onion(red)": "Onion",
    "onion(white)": "Onion",
    "onion (small)": "Onion",

    # Garlic
    "garlic": "Garlic",
    "garlic(local)": "Garlic",
    "lahsun": "Garlic",

    # Mustard
    "mustard": "Mustard",
    "mustard(black)": "Mustard",
    "mustard seed": "Mustard",
    "sarson": "Mustard",
    "rai": "Mustard",

    # Cotton
    "cotton": "Cotton",
    "cotton(unginned)": "Cotton",
    "cotton(ginned)": "Cotton",
    "narma": "Cotton",
    "kapas": "Cotton",

    # Paddy / Rice
    "paddy(dhan)": "Paddy(Dhan)",
    "paddy(dhan)(common)": "Paddy(Dhan)",
    "paddy(dhan)(basmati)": "Paddy(Dhan)",
    "basmati rice": "Basmati Rice",
    "paddy": "Paddy(Dhan)",
    "rice": "Paddy(Dhan)",

    # Chana / Gram
    "bengal gram(gram)": "Bengal Gram(Gram)",
    "bengal gram(gram)(whole)": "Bengal Gram(Gram)",
    "gram": "Bengal Gram(Gram)",
    "chana": "Bengal Gram(Gram)",
    "kabuli chana": "Kabuli Chana",
    "kabuli chana(chickpeas-white)": "Kabuli Chana",

    # Cumin / Jeera
    "cumin seed(jeera)": "Cumin Seed(Jeera)",
    "cumin": "Cumin Seed(Jeera)",
    "jeera": "Cumin Seed(Jeera)",

    # Maize
    "maize": "Maize",
    "maize(hybrid)": "Maize",
    "makka": "Maize",

    # Potato
    "potato": "Potato",
    "potato(desi)": "Potato",
    "aloo": "Potato",

    # Tomato
    "tomato": "Tomato",
    "tomato(local)": "Tomato",
    "tomato(hybrid)": "Tomato",

    # Coriander
    "coriander(seed)": "Coriander(Seed)",
    "coriander": "Coriander(Seed)",
    "dhaniya": "Coriander(Seed)",

    # Groundnut
    "groundnut": "Groundnut",
    "groundnut(pods)": "Groundnut",
    "groundnut(split)": "Groundnut",
    "peanut": "Groundnut",

    # Pulses
    "arhar (tur)": "Arhar (Tur)",
    "arhar (tur/red gram)(whole)": "Arhar (Tur)",
    "tur": "Arhar (Tur)",
    "moong(green gram)": "Moong(Green Gram)",
    "moong": "Moong(Green Gram)",
    "urad(black gram)": "Urad(Black Gram)",
    "urad": "Urad(Black Gram)",
    "masoor": "Masoor",
}

STATE_MAPPING: Dict[str, str] = {
    "chhattishgarh": "Chhattisgarh",
    "nct of delhi": "Delhi",
    "orissa": "Odisha",
    "pondicherry": "Puducherry",
}


class DataCleaner:
    """Cleans and standardizes raw Agmarknet records."""

    @staticmethod
    def clean_commodity(raw_crop: str) -> str:
        """Normalizes noisy commodity strings."""
        if not raw_crop:
            return ""
        norm = raw_crop.strip().lower()
        # Direct lookup
        if norm in COMMODITY_MAPPING:
            return COMMODITY_MAPPING[norm]

        # Strip noisy descriptors like (Whole), (Local), (Desi), (F&V)
        simplified = re.sub(r'\(.*?\)', '', norm).strip()
        if simplified in COMMODITY_MAPPING:
            return COMMODITY_MAPPING[simplified]

        # Partial matching for key staples
        for key, canonical in COMMODITY_MAPPING.items():
            if key in norm or norm in key:
                return canonical

        # Fallback to title-cased stripped name
        return raw_crop.strip().title()

    @staticmethod
    def clean_market(raw_market: str) -> str:
        """Strips noisy market suffixes like (Grain Market), (Niphad Yard), (F&V)."""
        if not raw_market:
            return ""
        # Remove parenthetical content
        cleaned = re.sub(r'\(.*?\)', '', raw_market)
        # Remove extra punctuation and whitespace
        cleaned = re.sub(r'[\/\\#\-]', ' ', cleaned)
        return " ".join(cleaned.split()).strip().title()

    @staticmethod
    def clean_state(raw_state: str) -> str:
        """Standardizes state spelling."""
        if not raw_state:
            return ""
        norm = raw_state.strip().lower()
        if norm in STATE_MAPPING:
            return STATE_MAPPING[norm]
        return " ".join(raw_state.split()).strip().title()

    @classmethod
    def clean_record(cls, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Cleans a single raw record."""
        cleaned = dict(raw_record)
        cleaned["commodity"] = cls.clean_commodity(raw_record.get("commodity", ""))
        cleaned["market"] = cls.clean_market(raw_record.get("market", ""))
        cleaned["district"] = cls.clean_market(raw_record.get("district", ""))
        cleaned["state"] = cls.clean_state(raw_record.get("state", ""))
        return cleaned
