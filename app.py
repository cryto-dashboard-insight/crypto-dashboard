from flask import Flask, render_template, jsonify
import requests
import time

app = Flask(__name__)

cache = {"data": None, "time": 0}
CACHE_SECONDS = 15


def fetch_data():
    # use cache first
    if cache["data"] and time.time() - cache["time"] < CACHE_SECONDS:
        return cache["data"]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        data = requests.get(url, params=params, timeout=8).json()
        cache["data"] = data
        cache["time"] = time.time()
        return data
    except:
        return cache["data"] or {
            "bitcoin": {"usd": 0, "usd_24h_change": 0},
            "ethereum": {"usd": 0, "usd_24h_change": 0},
            "solana": {"usd": 0, "usd_24h_change": 0}
        }


def safe(x):
    return x if x is not None else 0


def market_state(avg):
    if avg > 2:
        return "Risk-On 🟢"
    elif avg > -2:
        return "Neutral ⚪"
    return "Risk-Off 🔴"


def decision(avg):
    if avg > 2:
        return "WATCH"
    elif avg > 0:
        return "MONITOR"
    elif avg > -2:
        return "CAUTION"
    return "WAIT"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data")
def api():
    data = fetch_data()

    coins = {}
    changes = []

    for key in ["bitcoin", "ethereum", "solana"]:
        c = data.get(key, {})
        change = safe(c.get("usd_24h_change", 0))
        changes.append(change)

        coins[key] = {
            "price": c.get("usd", 0),
            "change": change
        }

    avg = sum(changes) / len(changes)

    return jsonify({
        "coins": coins,
        "market_state": market_state(avg),
        "decision": decision(avg),
        "avg_change": avg
    })


if __name__ == "__main__":
    app.run(debug=True)
