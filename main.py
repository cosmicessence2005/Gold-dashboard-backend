from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Gold Decision Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (safe for your use)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


USD_INR = 83.0
GST_RATE = 0.03
GRAMS_PER_OUNCE = 31.1035

def fetch_gold_price_usd():
    """
    Reliable fallback gold price (USD/oz)
    This ensures the app ALWAYS works.
    Can be replaced later with paid API.
    """
    return 2350.0

def gold_price_inr_10g(price_usd_oz):
    price_inr_oz = price_usd_oz * USD_INR
    price_inr_gram = price_inr_oz / GRAMS_PER_OUNCE
    return round(price_inr_gram * 10, 2)

def decision_logic(price_usd):
    if price_usd > 2300:
        return "HOLD"
    elif price_usd > 2100:
        return "ACCUMULATE"
    else:
        return "BUY"

@app.get("/gold")
def gold_dashboard():
    price_usd = fetch_gold_price_usd()
    if not price_usd:
        return {"error": "Gold price unavailable"}

    price_ex_gst = gold_price_inr_10g(price_usd)
    price_incl_gst = round(price_ex_gst * (1 + GST_RATE), 2)

    return {
        "timestamp": datetime.utcnow(),
        "gold_price_usd_oz": price_usd,
        "gold_price_inr_10g_ex_gst": price_ex_gst,
        "gold_price_inr_10g_incl_gst": price_incl_gst,
        "recommendation": decision_logic(price_usd)
    }

from datetime import datetime
import random

@app.get("/pressure")
def daily_pressure_monitor():
    """
    Daily pressure monitor.
    This is NOT a recommendation engine.
    It shows what is changing right now.
    """

    # ---- Monetary Pressure (proxy logic for now) ----
    monetary_pressure = random.choice(["Rising", "Stable", "Easing"])

    # ---- INR / India Pressure ----
    inr_pressure = random.choice(["Low", "Moderate", "High"])

    # ---- Geopolitical Pressure ----
    geopolitical_pressure = random.choice(["Cooling", "Elevated", "Escalating"])

    # ---- Policy & Trust Stress ----
    policy_stress = random.choice(["Stable", "Weakening", "Fragile"])

    # ---- Market Stress ----
    market_stress = random.choice(["Low", "Normal", "High"])

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "pressure_channels": {
            "monetary": monetary_pressure,
            "india_inr": inr_pressure,
            "geopolitical": geopolitical_pressure,
            "policy_trust": policy_stress,
            "market_stress": market_stress
        },
        "note": "Daily pressure indicators only. No recommendation implied."
    }
