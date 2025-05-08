# server.py
from datetime import date

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from data.data_loader import get_price_data
from strategy.strategy_ma import moving_average_strategy
from strategy.strategy_rsi import rsi_strategy
from trade.trader import PaperTrader
from config.settings import Config


app = Flask(__name__)
CORS(app)  # 프론트엔드와 CORS 허용

@app.route("/")  # 라우트 데코레이터 추가
def index():
    return render_template("index.html")


@app.route("/backtest", methods=["POST"])
def backtest():
    try:
        data = request.json
        ticker = data["ticker"]
        period = data["period"]
        strategy = data["strategy"]
        params = data.get("params", {})

        df = get_price_data(ticker, period=period)
        trader = PaperTrader()

        signals = []  # 📌 시그널 히스토리 저장
        for i in range(30, len(df)):
            sample = df.iloc[:i+1]

            if strategy == "ma":
                Config.MA_SHORT = int(params.get("short", 5))
                Config.MA_LONG = int(params.get("long", 30))
                signal = moving_average_strategy(sample)
            elif strategy == "rsi":
                signal = rsi_strategy(
                    sample,
                    period=int(params.get("rsi_period", 14)),
                    overbought=int(params.get("overbought", 70)),
                    oversold=int(params.get("oversold", 30))
                )
            else:
                signal = "HOLD"

            price = df["Close"].iloc[i]
            date_str = df.index[i].strftime("%Y-%m-%d")  # 변수명 수정

            #트레이딩 수행
            if signal == "BUY":
                trader.buy(ticker, price, 1)
            elif signal == "SELL":
                trader.sell(ticker, price, 1)

            #시그널 저장
            signals.append({
                "date": date_str,  # 변수명 수정
                "price": price,
                "signal": signal
            })

        result = {
            "total_profit": trader.total_profit,
            "cash": trader.cash,
            "position": trader.positions.get(ticker, 0),  # 수정: position 대신 positions 딕셔너리 사용
            "signals": signals,
            "price_data": df["Close"].reset_index().rename(columns={"index": "date"}).to_dict(orient="records")
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)