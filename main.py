# main.py

import os
import sys
import subprocess

from data.data_loader import get_price_data
from strategy.strategy_ma import moving_average_strategy
from strategy.strategy_rsi import rsi_strategy
from trade.trader import PaperTrader
from config.settings import Config


def run_backtest(df, strategy_fn, ticker="AAPL", quantity=1):
    trader = PaperTrader()
    for i in range(30, len(df)):
        sample = df.iloc[:i + 1]
        signal = strategy_fn(sample)
        price = df["Close"].iloc[i]

        if signal == "BUY":
            trader.buy(ticker, price, quantity)
        elif signal == "SELL":
            trader.sell(ticker, price, quantity)

    trader.status()

def start_streamlit():
    print("🌐 Streamlit 대시보드를 실행합니다...")
    subprocess.run(["streamlit", "run", "app/dashboard.py"])


def start_flask_server():
    print("🌐 Flask 서버를 실행합니다...")
    from app.web import server
    server.app.run(host="0.0.0.0", port=5000, debug=True)

def cli_backtest():
    print("📈 자동매매 전략 백테스트 시스템")

    ticker = input("종목을 입력하세요 (예: AAPL): ").upper()
    period = input("기간을 입력하세요 (예: 6mo): ")

    print("\n[전략 선택]")
    print("1: 이동평균(MA)")
    print("2: RSI")
    strategy_choice = input("전략 번호 선택: ")

    if strategy_choice == "1":
        strategy_fn = moving_average_strategy
        print("✅ 이동평균 전략 선택됨")
    elif strategy_choice == "2":
        strategy_fn = rsi_strategy
        print("✅ RSI 전략 선택됨")
    else:
        print("❌ 잘못된 입력입니다.")
        return

    df = get_price_data(ticker, period=period)
    run_backtest(df, strategy_fn, ticker)

def main():
    print("🔧 실행 모드를 선택하세요:")
    print("1: CLI 백테스트")
    print("2: Streamlit 웹 대시보드")
    print("3: Flask API 서버")

    mode = input("모드 번호 입력: ").strip()

    if mode == "1":
        cli_backtest()
    elif mode == "2":
        start_streamlit()
    elif mode == "3":
        start_flask_server()
    else:
        print("❌ 잘못된 모드 선택입니다.")


if __name__ == "__main__":
    main()
