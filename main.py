from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests

app = FastAPI(title="Gold Intelligence Dashboard")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# CONSTANTS
# -----------------------------
GRAMS_PER_OUNCE = 31.1035
GST_RATE = 0.03

# -----------------------------
# LIVE DATA FETCHERS
# -----------------------------

def fetch_gold_spot_usd():
    """
    Live Gold Spot Price (XAU/USD)
    Source: metals.live
    """
    r = requests.get("https://api.metals.live/v1/spot/gold", timeout=5)
    data = r.json()
    return float(data[0][1])


def fetch_fx_rate(base, target):
    """
    Live FX rates
    Source: exchangerate.host (ECB-backed)
    """
    r = requests.get(
        f"https://api.exchangerate.host/latest?base={base}&symbols={target}",
        timeout=5
    )
    data = r.json()
    return float(data["rates"][target])


# -----------------------------
# PRICE CALCULATION
# -----------------------------

def gold_price_inr_10g(usd_per_oz, usd_inr):
    inr_per_oz = usd_per_oz * usd_inr
    inr_per_gram = inr_per_oz / GRAMS_PER_OUNCE
    return round(inr_per_gram * 10, 2)


# -----------------------------
# CLASSIFICATION HELPERS
# -----------------------------

def classify_usd_pressure(eur_usd):
    # EUR down = USD strong
    if eur_usd < 1.05:
        return "High"
    elif eur_usd > 1.10:
        return "Low"
    return "Moderate"


def classify_inr_pressure(usd_inr):
    if usd_inr > 88.5:
        return "High"
    elif usd_inr < 85.0:
        return "Low"
    return "Moderate"


def classify_gold_momentum(gold_usd):
    if gold_usd > 2350:
        return "Positive"
    elif gold_usd < 2200:
        return "Negative"
    return "Neutral"


def classify_risk_stress(usd_jpy):
    if usd_jpy > 150:
        return "High"
    elif usd_jpy < 135:
        return "Low"
    return "Moderate"


# -----------------------------
# ENDPOINTS
# -----------------------------

@app.get("/")
def root():
    return {"status": "LIVE backend running"}


@app.get("/gold")
def gold_live():
    gold_usd = fetch_gold_spot_usd()
    usd_inr = fetch_fx_rate("USD", "INR")
    eur_usd = fetch_fx_rate("EUR", "USD")

    price_10g_ex_gst = gold_price_inr_10g(gold_usd, usd_inr)
    price_10g_incl_gst = round(price_10g_ex_gst * (1 + GST_RATE), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "gold_spot_usd_oz": gold_usd,
        "usd_inr": usd_inr,
        "eur_usd": eur_usd,
        "india_gold_10g_ex_gst": price_10g_ex_gst,
        "india_gold_10g_incl_gst": price_10g_incl_gst,
        "data_sources": {
            "gold": "metals.live",
            "fx": "exchangerate.host (ECB)"
        }
    }


@app.get("/pressure")
def pressure_live():
    gold_usd = fetch_gold_spot_usd()
    usd_inr = fetch_fx_rate("USD", "INR")
    eur_usd = fetch_fx_rate("EUR", "USD")
    usd_jpy = fetch_fx_rate("USD", "JPY")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "usd_pressure": classify_usd_pressure(eur_usd),
        "inr_pressure": classify_inr_pressure(usd_inr),
        "gold_momentum": classify_gold_momentum(gold_usd),
        "risk_stress": classify_risk_stress(usd_jpy),
        "live_inputs": {
            "gold_usd": gold_usd,
            "usd_inr": usd_inr,
            "eur_usd": eur_usd,
            "usd_jpy": usd_jpy
        },
        "note": "All indicators derived from LIVE market data. No static values."
    }
