# strategy/strategy_rsi.py

import pandas as pd
import numpy as np
from data.data_loader import get_price_data
from trade.trader import PaperTrader


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:

    series = series.copy()

    delta = series.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    avg_loss = avg_loss.replace(0, np.finfo(float).eps)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def rsi_strategy(df: pd.DataFrame, period: int = 14, overbought: int = 70, oversold: int = 30) -> str:
    if len(df) < period + 10:  # Need extra data for reliable RSI
        print(f"⚠️ 데이터가 부족합니다. 최소 {period + 10}개 필요")
        return "HOLD"

    df_copy = df.copy()

    rsi_series = calculate_rsi(df['Close'], period)

    recent_rsi = rsi_series.dropna().tail(1)

    # Make sure we have a valid RSI value
    if recent_rsi.empty:
        print("⚠️ RSI 계산 중 결측치 발생")
        return "HOLD"

    # Get current RSI value as a scalar
    current_rsi = float(recent_rsi.iloc[0])

    if current_rsi < oversold:
        return "BUY"
    elif current_rsi > overbought:
        return "SELL"
    else:
        return "HOLD"


def backtest_rsi(ticker="AAPL", period="6mo"):
    df = get_price_data(ticker, period)
    trader = PaperTrader()

    min_index = 30

    for i in range(min_index, len(df)):
        sample = df.iloc[:i+1]
        signal = rsi_strategy(sample)
        price = df['Close'].iloc[i]

        if signal == "BUY":
            trader.buy(ticker, price, 1)
        elif signal == "SELL":
            trader.sell(ticker, price, 1)
    trader.status()