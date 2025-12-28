from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI(title="Gold Decision Dashboard")

USD_INR = 83.0
GST_RATE = 0.03
GRAMS_PER_OUNCE = 31.1035

def fetch_gold_price_usd():
    url = "https://api.metals.live/v1/spot/gold"
    try:
        data = requests.get(url, timeout=5).json()
        return float(data[0][1])
    except:
        return None

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
