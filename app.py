import streamlit as st
import re
from typing import List, Dict, Any

# =============================
# USE CASE DERIVATION (FIXED)
# =============================
def derive_use_case(p: Dict[str, Any]) -> str:
    if p["ram"] >= 8 and p["storage"] >= 128:
        return "gaming"
    if p["brand"] == "google" or p["price"] >= 40000:
        return "camera"
    if p["price"] <= 20000:
        return "budget"
    if p["price"] >= 60000:
        return "premium"
    return "everyday"

# =============================
# PRODUCT CATALOGUE
# =============================
RAW_CATALOGUE: List[Dict[str, Any]] = [
    {"name": "Samsung Galaxy S23", "brand": "samsung", "category": "mobile", "price": 74999, "ram": 8, "storage": 256},
    {"name": "Samsung Galaxy A54", "brand": "samsung", "category": "mobile", "price": 33499, "ram": 8, "storage": 128},
    {"name": "Samsung Galaxy M34", "brand": "samsung", "category": "mobile", "price": 18999, "ram": 6, "storage": 128},
    {"name": "OnePlus Nord 3", "brand": "oneplus", "category": "mobile", "price": 28999, "ram": 8, "storage": 128},
    {"name": "OnePlus 11", "brand": "oneplus", "category": "mobile", "price": 56999, "ram": 8, "storage": 256},
    {"name": "Google Pixel 7a", "brand": "google", "category": "mobile", "price": 39999, "ram": 8, "storage": 128},
]

# Enrich catalogue with use_case
CATALOGUE: List[Dict[str, Any]] = []
for p in RAW_CATALOGUE:
    cp = p.copy()
    cp["use_case"] = derive_use_case(cp)
    CATALOGUE.append(cp)

BRANDS = {p["brand"] for p in CATALOGUE}

# =============================
# QUERY PARSER (STRICT)
# =============================
def parse_query(q: str) -> Dict[str, Any]:
    q = q.lower()

    filters = {
        "is_mobile": False,
        "brand": None,
        "ram": None,
        "storage": None,
        "price_max": None,
        "price_min": None,
        "use_case": None,
    }

    if re.search(r"\bmobile|mobiles|phone|phones\b", q):
        filters["is_mobile"] = True

    for b in BRANDS:
        if re.search(rf"\b{b}\b", q):
            filters["brand"] = b

    m = re.search(r'(\d+)\s*gb\s*ram', q)
    if m:
        filters["ram"] = int(m.group(1))

    m = re.search(r'(\d+)\s*gb\s*storage', q)
    if m:
        filters["storage"] = int(m.group(1))

    m = re.search(r'under\s*(\d+)\s*k', q)
    if m:
        filters["price_max"] = int(m.group(1)) * 1000

    m = re.search(r'under\s*(\d{4,6})', q)
    if m:
        filters["price_max"] = int(m.group(1))

    m = re.search(r'above\s*(\d+)\s*k', q)
    if m:
        filters["price_min"] = int(m.group(1)) * 1000

    if "gaming" in q:
        filters["use_case"] = "gaming"
    elif "camera" in q:
        filters["use_case"] = "camera"
    elif "budget" in q:
        filters["use_case"] = "budget"
    elif "premium" in q:
        filters["use_case"] = "premium"

    return filters

# =============================
# VALIDATION
# =============================
def has_real_filter(f: Dict[str, Any]) -> bool:
    return any([
        f["is_mobile"],
        f["brand"],
        f["ram"],
        f["storage"],
        f["price_max"],
        f["price_min"],
        f["use_case"],
    ])

# =============================
# MATCH (PURE AND)
# =============================
def match(p: Dict[str, Any], f: Dict[str, Any]) -> bool:
    if f["brand"] and p["brand"] != f["brand"]:
        return False
    if f["ram"] is not None and p["ram"] != f["ram"]:
        return False
    if f["storage"] is not None and p["storage"] != f["storage"]:
        return False
    if f["price_max"] and p["price"] > f["price_max"]:
        return False
    if f["price_min"] and p["price"] < f["price_min"]:
        return False
    if f["use_case"] and p["use_case"] != f["use_case"]:
        return False
    return True

# =============================
# STREAMLIT UI
# =============================
st.set_page_config(page_title="Smart Mobile Recommender", layout="centered")
st.title("📱 Smart Mobile Recommender")

query = st.text_input(
    "Enter your requirement",
    placeholder="e.g. mobile 8gb ram 128gb storage under 30000 gaming"
)

if st.button("Recommend"):
    filters = parse_query(query)

    if not has_real_filter(filters):
        st.error("❌ No valid requirement detected. Please specify RAM, storage, price, brand or use case.")
    else:
        results = [p for p in CATALOGUE if match(p, filters)]

        if results:
            st.success(f"✅ {len(results)} product(s) found")
            st.table(results)  # includes use_case column
        else:
            st.warning("❌ No product matches ALL the conditions.")
