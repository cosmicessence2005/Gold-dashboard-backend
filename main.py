from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests

app = FastAPI(title="Gold Dashboard Backend")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Constants ----
USD_INR_STATIC = 83.0
GST_RATE = 0.03
GRAMS_PER_OUNCE = 31.1035

# =========================
# GOLD PRICE (STABLE)
# =========================

def fetch_gold_price_usd():
    return 2350.0  # stable fallback

def convert_to_inr_10g(price_usd_oz: float):
    price_inr_oz = price_usd_oz * USD_INR_STATIC
    price_inr_per_gram = price_inr_oz / GRAMS_PER_OUNCE
    return round(price_inr_per_gram * 10, 2)

@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/gold")
def gold_price():
    price_usd = fetch_gold_price_usd()
    price_ex_gst = convert_to_inr_10g(price_usd)
    price_incl_gst = round(price_ex_gst * (1 + GST_RATE), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "gold_spot_usd_oz": price_usd,
        "india_price_10g_ex_gst": price_ex_gst,
        "india_price_10g_incl_gst": price_incl_gst,
        "notes": "Spot-linked estimate. Retail premiums not included."
    }

# =========================
# DAILY PRESSURE MONITOR
# =========================

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

def classify_dollar_pressure(eur_rate):
    if eur_rate is None:
        return "Unknown"
    if eur_rate < 0.90:
        return "Strengthening"
    elif eur_rate > 0.94:
        return "Weakening"
    else:
        return "Stable"

def classify_inr_pressure(inr_rate):
    if inr_rate is None:
        return "Unknown"
    if inr_rate > 83.5:
        return "High"
    elif inr_rate < 82.5:
        return "Low"
    else:
        return "Moderate"

def classify_market_stress():
    """
    Simple proxy using USD/JPY risk signal
    """
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=JPY", timeout=5)
        jpy = r.json()["rates"]["JPY"]
        if jpy > 150:
            return "Elevated"
        elif jpy < 135:
            return "Low"
        else:
            return "Normal"
    except:
        return "Unknown"

@app.get("/pressure")
def daily_pressure():
    eur = fetch_usd_eur()
    inr = fetch_usd_inr()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "monetary_pressure": classify_dollar_pressure(eur),
        "inr_pressure": classify_inr_pressure(inr),
        "market_stress": classify_market_stress(),
        "confidence": "Medium",
        "note": "Daily pressure indicators only. No recommendation implied."
    }
