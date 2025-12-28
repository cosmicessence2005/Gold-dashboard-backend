from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Gold Dashboard Backend")

# ---- CORS (required for frontend access) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Constants ----
USD_INR = 83.0                 # temporary static value
GST_RATE = 0.03
GRAMS_PER_OUNCE = 31.1035

# ---- Gold price source (safe fallback) ----
def fetch_gold_price_usd():
    """
    Stable fallback gold price (USD per ounce).
    This will be replaced later with live data.
    """
    return 2350.0


def convert_to_inr_10g(price_usd_oz: float):
    price_inr_oz = price_usd_oz * USD_INR
    price_inr_per_gram = price_inr_oz / GRAMS_PER_OUNCE
    return round(price_inr_per_gram * 10, 2)


# ---- Health check ----
@app.get("/")
def root():
    return {"status": "backend running"}


# ---- Gold price endpoint ----
@app.get("/gold")
def gold_price():
    price_usd = fetch_gold_price_usd()

    price_inr_ex_gst = convert_to_inr_10g(price_usd)
    price_inr_incl_gst = round(price_inr_ex_gst * (1 + GST_RATE), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "gold_spot_usd_oz": price_usd,
        "india_price_10g_ex_gst": price_inr_ex_gst,
        "india_price_10g_incl_gst": price_inr_incl_gst,
        "notes": "Spot-linked estimate. Retail premiums not included."
    }
