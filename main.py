from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests
import json
import os

app = FastAPI(title="Gold Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONSTANTS
# =========================

        
GST_RATE = 0.03
GRAMS_PER_OUNCE = 31.1035

PRESSURE_FILE = "pressure_history.json"
MAX_DAYS = 7

# =========================
# GOLD PRICE
# =========================

def fetch_gold_price_usd():
    return 2350.0

def convert_to_inr_10g(price_usd_oz):
    usd_inr = fetch_live_usd_inr()

    # Fallback safety (rare)
    if usd_inr is None:
        usd_inr = 83.0

    price_inr_oz = price_usd_oz * usd_inr
    price_inr_per_gram = price_inr_oz / GRAMS_PER_OUNCE
    return round(price_inr_per_gram * 10, 2)

# =========================
# PRESSURE HELPERS
# =========================

MONETARY_MAP = {
    "Weakening": -1,
    "Stable": 0,
    "Strengthening": 1
}

INR_MAP = {
    "Low": -1,
    "Moderate": 0,
    "High": 1
}

MARKET_MAP = {
    "Low": -1,
    "Normal": 0,
    "Elevated": 1
}

def load_pressure_history():
    if not os.path.exists(PRESSURE_FILE):
        return []
    with open(PRESSURE_FILE, "r") as f:
        return json.load(f)

def save_pressure_history(history):
    with open(PRESSURE_FILE, "w") as f:
        json.dump(history[-MAX_DAYS:], f)

def pressure_to_score(value, mapping):
    return mapping.get(value, 0)

# =========================
# FX FETCHERS
# =========================

def fetch_live_usd_inr():
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=INR",
            timeout=5
        )
        return r.json()["rates"]["INR"]
    except:
        return None

def fetch_usd_eur():
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=EUR", timeout=5)
        return r.json()["rates"]["EUR"]
    except:
        return None

def fetch_usd_inr():
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=INR", timeout=5)
        return r.json()["rates"]["INR"]
    except:
        return None

def classify_dollar_pressure(eur):
    if eur is None:
        return "Stable"
    if eur < 0.90:
        return "Strengthening"
    elif eur > 0.94:
        return "Weakening"
    return "Stable"

def classify_inr_pressure(inr):
    if inr is None:
        return "Moderate"
    if inr > 83.5:
        return "High"
    elif inr < 82.5:
        return "Low"
    return "Moderate"

def classify_market_stress():
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=JPY", timeout=5)
        jpy = r.json()["rates"]["JPY"]
        if jpy > 150:
            return "Elevated"
        elif jpy < 135:
            return "Low"
        return "Normal"
    except:
        return "Normal"

# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/gold")
def gold_price():
    price_usd = fetch_gold_price_usd()
    ex_gst = convert_to_inr_10g(price_usd)
    incl_gst = round(ex_gst * (1 + GST_RATE), 2)
    usd_inr = fetch_live_usd_inr()
    
    return {
    "timestamp": datetime.utcnow().isoformat(),
    "gold_spot_usd_oz": price_usd,
    "usd_inr_rate": usd_inr,
    "india_price_10g_ex_gst": ex_gst,
    "india_price_10g_incl_gst": incl_gst
}

@app.get("/pressure")
def daily_pressure():
    eur = fetch_usd_eur()
    inr = fetch_usd_inr()

    monetary = classify_dollar_pressure(eur)
    inr_level = classify_inr_pressure(inr)
    market = classify_market_stress()

    daily_score = (
        pressure_to_score(monetary, MONETARY_MAP) +
        pressure_to_score(inr_level, INR_MAP) +
        pressure_to_score(market, MARKET_MAP)
    )

    history = load_pressure_history()
    history.append({
        "date": datetime.utcnow().isoformat(),
        "score": daily_score
    })
    save_pressure_history(history)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "monetary_pressure": monetary,
        "inr_pressure": inr_level,
        "market_stress": market,
        "daily_pressure_score": daily_score
    }
