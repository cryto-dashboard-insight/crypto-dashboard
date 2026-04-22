from flask import Flask
import requests

app = Flask(__name__)

def get_market():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": "false"
    }

    data = requests.get(url, params=params).json()

    coins = []
    total_change = 0

    btc = 0
    eth = 0

    for c in data:
        change = c.get("price_change_percentage_24h", 0) or 0
        price = c.get("current_price", 0)
        symbol = c.get("symbol", "").upper()

        total_change += change

        if symbol == "BTC":
            btc = change
        if symbol == "ETH":
            eth = change

        coins.append({
            "name": c.get("name"),
            "symbol": symbol,
            "price": price,
            "change": change
        })

    return coins, total_change, btc, eth


@app.route("/")
def home():
    coins, total, btc, eth = get_market()

    if total > 0:
        market = "🟢 BULLISH"
        color = "#0ecb81"
    else:
        market = "🔴 BEARISH"
        color = "#f6465d"

    if eth > btc:
        dominance = "ETH LEADING 🟢"
    else:
        dominance = "BTC LEADING 🔴"

    html = f"""
    <html>
    <head>
        <title>Market Intelligence Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background: #0b0e11;
                color: white;
                text-align: center;
            }}
            .card {{
                background:#161a1e;
                margin:10px;
                padding:10px;
                border-radius:8px;
            }}
        </style>
    </head>
    <body>

    <h1 style="color:#f0b90b;">📊 Market Intelligence Dashboard</h1>

    <h2 style="color:{color};">{market}</h2>

    <p>Dominance: <b>{dominance}</b></p>

    """

    for c in coins:
        html += f"""
        <div class="card">
            {c['name']} ({c['symbol']}) — ${c['price']} |
            <span style="color:{'#0ecb81' if c['change'] > 0 else '#f6465d'};">
                {round(c['change'],2)}%
            </span>
        </div>
        """

    html += "</body></html>"

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
