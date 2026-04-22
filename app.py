from flask import Flask
import requests

app = Flask(__name__)


# ----------------------------
# MARKET DATA
# ----------------------------
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

    btc_data = None
    eth_data = None

    for c in data:
        name = c.get("name")
        symbol = c.get("symbol", "").upper()
        price = c.get("current_price", 0)
        change = c.get("price_change_percentage_24h", 0) or 0

        total_change += change

        if symbol == "BTC":
            btc_data = change
        if symbol == "ETH":
            eth_data = change

        coins.append({
            "name": name,
            "symbol": symbol,
            "price": price,
            "change": change
        })

    return coins, total_change, btc_data, eth_data


# ----------------------------
# DAILY PRICE DATA
# ----------------------------
def get_daily(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency": "usd", "days": 1}

    data = requests.get(url, params=params).json()
    prices = data.get("prices", [])

    return [p[1] for p in prices]


# ----------------------------
# EMA TREND
# ----------------------------
def ema(values):
    if not values:
        return 0

    k = 2 / (len(values) + 1)
    ema_val = values[0]

    for v in values[1:]:
        ema_val = v * k + ema_val * (1 - k)

    return ema_val


# ----------------------------
# MAIN DASHBOARD
# ----------------------------
@app.route("/")
def home():

    coins, market_total, btc_24h, eth_24h = get_market()

    btc_1d = get_daily("bitcoin")
    eth_1d = get_daily("ethereum")

    btc_price = btc_1d[-1] if btc_1d else 0
    eth_price = eth_1d[-1] if eth_1d else 0

    btc_ema = ema(btc_1d)
    eth_ema = ema(eth_1d)

    # ----------------------------
    # MARKET INTELLIGENCE ENGINE
    # ----------------------------
    score = 0

    # Market bias
    if market_total > 0:
        score += 10
    else:
        score -= 10

    # BTC strength
    if btc_24h:
        score += btc_24h * 1.5

    # ETH strength (higher weight = focus asset)
    if eth_24h:
        score += eth_24h * 2.5

    # ETH vs BTC dominance comparison
    if eth_24h and btc_24h:
        if eth_24h > btc_24h:
            dominance = "ETH LEADING 🟢"
            score += 10
        else:
            dominance = "BTC LEADING 🔴"
            score -= 5
    else:
        dominance = "UNCLEAR ⚠️"

    # EMA confirmation
    if btc_price > btc_ema:
        score += 5
    else:
        score -= 5

    if eth_price > eth_ema:
        score += 10
    else:
        score -= 10

    # ----------------------------
    # MARKET STATE
    # ----------------------------
    if score > 20:
        state = "🟢 BULLISH MARKET (ETH/BTC MOMENTUM UP)"
        color = "#0ecb81"
        advice = "Risk-on environment"
    elif score < -20:
        state = "🔴 BEARISH MARKET (WEAK STRUCTURE)"
        color = "#f6465d"
        advice = "Risk-off environment"
    else:
        state = "⚠️ CHOPPY / NO CLEAR DIRECTION"
        color = "#f0b90b"
        advice = "Wait for confirmation"

    risk = abs(score)

    # ----------------------------
    # UI
    # ----------------------------
    html = f"""
    <html>
    <head>
        <title>Market Intelligence Pro</title>

        <style>
            body {{
                margin:0;
                font-family:Arial;
                background:#0b0e11;
                color:#eaecef;
            }}

            .header {{
                position:fixed;
                top:0;
                width:100%;
                background:#11161c;
                padding:15px;
                text-align:center;
                color:#f0b90b;
                font-size:18px;
            }}

            .container {{
                margin-top:70px;
                max-width:900px;
                margin:auto;
                padding:20px;
            }}

            .card {{
                background:#161a1e;
                padding:12px;
                margin:10px 0;
                border-radius:8px;
                display:flex;
                justify-content:space-between;
            }}

            .state {{
                text-align:center;
                font-size:20px;
                margin:20px 0;
            }}

            .info {{
                text-align:center;
                margin-bottom:20px;
            }}
        </style>
    </head>

    <body>

    <div class="header">
        🧠 MARKET INTELLIGENCE PRO DASHBOARD
    </div>

    <div class="container">

        <div class="state" style="color:{color};">
            {state}
        </div>

        <div class="info">
            Dominance: <b>{dominance}</b><br>
            Risk Score: <b>{round(risk,2)}</b><br>
            Advice: <b>{advice}</b>
        </div>
    """

    for c in coins:
        html += f"""
        <div class="card">
            <div>{c['name']} ({c['symbol']})</div>
            <div>
                ${c['price']} |
                <span style="color:{'#0ecb81' if c['change'] > 0 else '#f6465d'};">
                    {round(c['change'],2)}%
                </span>
            </div>
        </div>
        """

    html += """
    </div>

    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)