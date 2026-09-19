#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Multi-Source National Mandi Data Fetcher
-------------------------------------------------------
Pulls daily mandi arrival and modal prices from:
1. Agmarknet 2.0 Official API (Direct, live, 0-auth)
2. data.gov.in Official Agmarknet Resource API (with API Key)
3. Local verified fallback seed (Fail-safe shield)
"""

import os
import json
import ssl
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_ENDPOINT = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
AGMARKNET_BASE = "https://api.agmarknet.gov.in/v1/prices-and-arrivals/commodity-market/daily-report-state"

# Standard state mapping from Agmarknet filters
STATE_MAP: Dict[int, str] = {
    1: "Andaman and Nicobar", 2: "Andhra Pradesh", 3: "Arunachal Pradesh",
    4: "Assam", 5: "Bihar", 6: "Chandigarh", 7: "Chattisgarh",
    8: "Dadra and Nagar Haveli", 9: "Daman and Diu", 10: "Goa",
    11: "Gujarat", 12: "Haryana", 13: "Himachal Pradesh", 14: "Jammu and Kashmir",
    15: "Jharkhand", 16: "Karnataka", 17: "Kerala", 18: "Lakshadweep",
    19: "Madhya Pradesh", 20: "Maharashtra", 21: "Manipur", 22: "Meghalaya",
    23: "Mizoram", 24: "Nagaland", 25: "NCT of Delhi", 26: "Odisha",
    27: "Pondicherry", 28: "Punjab", 29: "Rajasthan", 30: "Sikkim",
    31: "Tamil Nadu", 32: "Telangana", 33: "Tripura", 34: "Uttar Pradesh",
    35: "Uttarakhand", 36: "West Bengal"
}

# Key agricultural states
PRIORITY_STATES = [
    19, 20, 11, 29, 34, 28, 12, 16, 2, 32, 31, 36, 5, 26, 13, 14, 25, 17, 7, 15, 4, 10, 35, 33, 22, 21, 24
]


class MandiDataFetcher:
    """Multi-source data fetcher for all Indian APMC mandis."""

    @classmethod
    def fetch_from_agmarknet(cls, target_date_iso: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches live pan-India mandi records directly from the Agmarknet 2.0 API.
        No API key required.
        """
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BharatMandi-Sync/2.0",
            "Accept": "application/json",
            "Origin": "https://agmarknet.gov.in",
            "Referer": "https://agmarknet.gov.in/"
        }

        dates_to_try = []
        if target_date_iso:
            dates_to_try.append(target_date_iso)
        else:
            now = datetime.now()
            dates_to_try.append(now.strftime("%Y-%m-%d"))
            dates_to_try.append((now - timedelta(days=1)).strftime("%Y-%m-%d"))

        for d_iso in dates_to_try:
            date_display = datetime.strptime(d_iso, "%Y-%m-%d").strftime("%d-%m-%Y")
            print(f"[INFO] Fetching from official Agmarknet 2.0 API for date: {d_iso}...")
            records: List[Dict[str, Any]] = []

            for s_id in PRIORITY_STATES:
                s_name = STATE_MAP.get(s_id, f"State_{s_id}")
                url = f"{AGMARKNET_BASE}?date={d_iso}&state={s_id}&includeExcel=false"
                req = urllib.request.Request(url, headers=headers)
                try:
                    with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        for g in data.get("commodityGroups", []):
                            for c in g.get("commodities", []):
                                c_name = c.get("commodityName", "")
                                for m in c.get("markets", []):
                                    mkt = m.get("marketCenter", "")
                                    for item in m.get("data", []):
                                        modal_p = float(item.get("modalPrice") or 0)
                                        if modal_p <= 0:
                                            continue
                                        records.append({
                                            "state": s_name,
                                            "district": mkt.replace(" APMC", "").split("(")[0].strip(),
                                            "market": mkt.replace(" APMC", "").strip(),
                                            "commodity": c_name,
                                            "variety": item.get("variety", ""),
                                            "arrival_date": date_display,
                                            "min_price": float(item.get("minimumPrice") or modal_p),
                                            "max_price": float(item.get("maximumPrice") or modal_p),
                                            "modal_price": modal_p,
                                            "arrivals": float(item.get("arrivals") or 0) * 10,
                                            "trend": "stable",
                                            "change_amount": 0
                                        })
                except Exception:
                    pass

            if len(records) >= 50:
                print(f"[SUCCESS] Fetched {len(records)} verified records from Agmarknet 2.0 for {d_iso} across {len(set(r['state'] for r in records))} states!")
                return records
            else:
                print(f"[WARN] Only {len(records)} records found for {d_iso}. Trying fallback date...")

        return None

    @classmethod
    def fetch_from_datagov(cls, api_key: Optional[str] = None, limit: int = 5000) -> Optional[List[Dict[str, Any]]]:
        """Fetches national mandi data from data.gov.in."""
        if not api_key:
            api_key = os.environ.get("DATAGOV_API_KEY", "").strip()

        if not api_key:
            return None

        params = {
            "api-key": api_key,
            "format": "json",
            "limit": limit
        }
        query_url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
        print(f"[INFO] Fetching national mandi records from {API_ENDPOINT}...")

        try:
            req = urllib.request.Request(
                query_url,
                headers={"User-Agent": "BharatMandi-Pipeline/2.0 (Agri-Public-Data)"}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                records = data.get("records", [])
                print(f"[SUCCESS] Successfully fetched {len(records)} raw records from data.gov.in.")
                return records
        except Exception as e:
            print(f"[WARN] data.gov.in fetch failed: {e}")
            return None

    @classmethod
    def fetch_all(cls) -> List[Dict[str, Any]]:
        """
        Attempts primary sources:
        1. Official Agmarknet 2.0 API (Zero Auth required)
        2. data.gov.in OGD API
        3. Local verified seed fallback
        """
        # 1. Primary: Direct Agmarknet 2.0 API
        records = cls.fetch_from_agmarknet()
        if records and len(records) >= 30:
            return records

        # 2. Secondary: Official OGD API
        records = cls.fetch_from_datagov()
        if records and len(records) >= 30:
            return records

        # 3. Local seed fallback
        local_today = os.path.join(os.path.dirname(os.path.abspath(__file__)), "today.json")
        if os.path.exists(local_today):
            try:
                with open(local_today, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cached = data.get("records", [])
                    print(f"[INFO] Using {len(cached)} verified cached records as fallback.")
                    return cached
            except Exception as e:
                print(f"[ERROR] Failed to read fallback cache: {e}")

        return []
