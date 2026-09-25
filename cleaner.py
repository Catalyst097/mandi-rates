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

    # Fruits, Spices & Others
    "apple": "Apple",
    "seb": "Apple",
    "ginger": "Ginger(Green)",
    "ginger(green)": "Ginger(Green)",
    "adrak": "Ginger(Green)",
    "turmeric": "Turmeric",
    "haldi": "Turmeric",
    "red chilli": "Red Chilli",
    "chilli(red)": "Red Chilli",
    "mirchi": "Red Chilli",
    "chili red": "Red Chilli",
    "chilli red": "Red Chilli",
    "dry chillies": "Red Chilli",
    "dry chilli": "Red Chilli",
    "dry chillies(red)": "Red Chilli",
    "chilli": "Red Chilli",
    "chili": "Red Chilli",
    "lal mirch": "Red Chilli",
    "green chilli": "Green Chilli",
    "green chili": "Green Chilli",
    "hari mirch": "Green Chilli",
}

STATE_MAPPING: Dict[str, str] = {
    "chhattishgarh": "Chhattisgarh",
    "chattisgarh": "Chhattisgarh",
    "nct of delhi": "Delhi",
    "delhi": "Delhi",
    "orissa": "Odisha",
    "pondicherry": "Puducherry",
    "jammu and kashmir": "Jammu and Kashmir",
    "jammu & kashmir": "Jammu and Kashmir",
    "andaman & nicobar": "Andaman and Nicobar",
    "andaman and nicobar islands": "Andaman and Nicobar",
    "dadra and nagar haveli": "Dadra and Nagar Haveli",
    "daman and diu": "Daman and Diu",
}

TALUKA_TO_DISTRICT_MAPPING: Dict[str, str] = {
    # Thane
    "murbad": "Thane",
    "kalyan": "Thane",
    "ulhasnagar": "Thane",
    "shahapur": "Thane",
    "bhiwandi": "Thane",
    "ambarnath": "Thane",
    # Nashik
    "lasalgaon": "Nashik",
    "pimpalgaon baswant": "Nashik",
    "malegaon": "Nashik",
    "sinner": "Nashik",
    "yeola": "Nashik",
    "kalvan": "Nashik",
    "chandwad": "Nashik",
    "nampur": "Nashik",
    "dindori": "Nashik",
    "ghoti": "Nashik",
    # Pune
    "baramati": "Pune",
    "junnar": "Pune",
    "khed": "Pune",
    "manchar": "Pune",
    "nira": "Pune",
    # Ahilyanagar (Ahmednagar)
    "kopargaon": "Ahilyanagar",
    "rahata": "Ahilyanagar",
    "rahuri": "Ahilyanagar",
    "sangamner": "Ahilyanagar",
    "shrirampur": "Ahilyanagar",
    "shevgaon": "Ahilyanagar",
    "newasa": "Ahilyanagar",
    "jamkhed": "Ahilyanagar",
    # Satara
    "karad": "Satara",
    "vaduj": "Satara",
    # Solapur
    "pandharpur": "Solapur",
    "barshi": "Solapur",
    "sangola": "Solapur",
    "karmala": "Solapur",
    "dudhani": "Solapur",
    # Sangli
    "tasgaon": "Sangli",
    "vita": "Sangli",
    "palus": "Sangli",
    # Raigad
    "panvel": "Raigad",
    "alibagh": "Raigad",
    "pen": "Raigad",
    "mangaon": "Raigad",
    "roha": "Raigad",
    "murud": "Raigad",
    # Palghar
    "vasai": "Palghar",
    "palghar": "Palghar",
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
        """Strips noisy market prefixes (APMC, KUMS) and suffixes like (Grain Market), (Niphad Yard), (F&V)."""
        if not raw_market:
            return ""
        # Remove parenthetical content
        cleaned = re.sub(r'\(.*?\)', '', raw_market)
        # Remove extra punctuation and whitespace
        cleaned = re.sub(r'[\/\\#\-]', ' ', cleaned)
        cleaned = " ".join(cleaned.split()).strip()

        # Universally strip bureaucratic prefixes (case-insensitive)
        cleaned = re.sub(r'^(apmc|kums|krishi\s+upaj\s+mandi\s+samiti)\s+', '', cleaned, flags=re.I)
        # Universally strip yard/market suffixes
        cleaned = re.sub(r'\s+(sub\s+yard|market\s+yard|grain\s+market|yard|market)$', '', cleaned, flags=re.I)

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

        # Normalize known talukas/mandis to their true administrative districts (e.g. Murbad -> Thane, Lasalgaon -> Nashik)
        dist_key = cleaned["district"].strip().lower()
        market_key = cleaned["market"].strip().lower()
        if dist_key in TALUKA_TO_DISTRICT_MAPPING:
            cleaned["district"] = TALUKA_TO_DISTRICT_MAPPING[dist_key]
        elif market_key in TALUKA_TO_DISTRICT_MAPPING:
            cleaned["district"] = TALUKA_TO_DISTRICT_MAPPING[market_key]

        # Multi-key defensive price parsing
        for price_key in ["min_price", "max_price", "modal_price"]:
            val = cleaned.get(price_key)
            if val is not None:
                try:
                    num = int(float(str(val).replace(",", "").replace("₹", "").strip()))
                    cleaned[price_key] = max(0, num)
                except (ValueError, TypeError):
                    cleaned[price_key] = 0

        return cleaned
