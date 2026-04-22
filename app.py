from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Crypto Dashboard is Live 🚀</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
