from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "crypto_dashboard_secret_key_2026"

# ==================== REAL DATA FETCHER ====================
def get_coin_data(coin_id="ethereum"):
    try:
        # Current data
        resp = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", timeout=10).json()
        market = resp["market_data"]
        
        return {
            "id": coin_id,
            "name": resp["name"],
            "symbol": resp["symbol"].upper(),
            "price": round(market["current_price"]["usd"], 2),
            "change_24h": round(market["price_change_percentage_24h"], 2),
            "change_7d": round(market["price_change_percentage_7d"], 2),
            "volume_24h": round(market["total_volume"]["usd"] / 1e9, 2),
            "market_cap": round(market["market_cap"]["usd"] / 1e9, 2),
            "tvl": 46.5 if coin_id == "ethereum" else 0
        }
    except:
        # Safe fallback if API fails temporarily
        fallback = {"ethereum": {"price": 2415, "change_24h": 4.5, "change_7d": 3.8, "volume_24h": 22, "market_cap": 291, "tvl": 46.5},
                    "bitcoin": {"price": 78500, "change_24h": 3.8, "change_7d": 4.2, "volume_24h": 46, "market_cap": 1550, "tvl": 0},
                    "solana": {"price": 89.5, "change_24h": 3.5, "change_7d": 6.5, "volume_24h": 5.2, "market_cap": 51, "tvl": 0}}
        d = fallback.get(coin_id, fallback["ethereum"])
        return {**d, "id": coin_id, "name": coin_id.capitalize(), "symbol": coin_id.upper()[:3]}

def get_price_chart(coin_id="ethereum"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
        data = requests.get(url, timeout=10).json()["prices"]
        return [{"date": datetime.fromtimestamp(item[0]/1000).strftime("%Y-%m-%d"), "price": item[1]} for item in data]
    except:
        return []  # fallback empty chart

def calculate_direction_score(data):
    ch24 = data.get("change_24h", 0)
    ch7 = data.get("change_7d", 0)
    score = 0
    if ch24 > 4 or ch7 > 6: score += 4
    elif ch24 > 2 or ch7 > 3: score += 3
    elif ch24 > 0 or ch7 > 0: score += 2
    if data.get("tvl", 0) > 45: score += 2
    if data.get("volume_24h", 0) > 15: score += 1
    score = max(0, min(10, score))

    if ch24 >= 2 or ch7 >= 3:
        direction = "🟢 Strong Bullish"
        outlook = "Clear uptrend. Good for long positions or accumulation."
        reversal = "Uptrend strong - hold or add on dips"
    elif ch24 <= -4 or ch7 <= -6:
        direction = "🔴 Bearish"
        outlook = "Downtrend in progress."
        reversal = "Possible reversal in 7-14 days if support holds"
    elif ch24 < 0 or ch7 < 0:
        direction = "🟠 Mild Pullback"
        outlook = "Minor correction."
        reversal = "Likely recovery in 2-5 days"
    else:
        direction = "🟡 Neutral"
        outlook = "Sideways market."
        reversal = "Wait for clear breakout"
    return score, direction, outlook, reversal

# ==================== ROUTES ====================
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    session['logged_in'] = True
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for("home"))
    coin_id = request.args.get("coin", "ethereum").lower()
    if coin_id not in ["ethereum", "bitcoin", "solana"]:
        coin_id = "ethereum"
    data = get_coin_data(coin_id)
    score, direction, outlook, reversal = calculate_direction_score(data)
    chart_data = get_price_chart(coin_id)
    return render_template("dashboard.html", coin=data, score=score, direction=direction, outlook=outlook, reversal=reversal, current_coin=coin_id, chart_data=chart_data)

@app.route("/export")
def export_data():
    coin_id = request.args.get("coin", "ethereum").lower()
    data = get_coin_data(coin_id)
    score, direction, outlook, reversal = calculate_direction_score(data)
    return jsonify({"coin": data, "score": score, "direction": direction, "outlook": outlook, "reversal": reversal})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
