# backtest/optimizer.py

import pandas as pd
import matplotlib.pyplot as plt
from trade.trader import PaperTrader
from strategy.strategy_ma import moving_average_strategy
from config.settings import Config

def simulate_strategy(df: pd.DataFrame, short: int, long: int) -> float:
    Config.MA_SHORT = short
    Config.MA_LONG = long
    trader = PaperTrader()
    buy_price = None

    for i in range(long + 1, len(df)):
        sample = df.iloc[:i+1]
        signal = moving_average_strategy(sample)
        price = df["Close"].iloc[i]

        if signal == "BUY":
            trader.buy("SIM", price, 1)
            buy_price = price
        elif signal == "SELL":
            trader.sell("SIM", price, 1)

    profit = trader.cash - trader._initial_cash
    return profit


def optimize_ma_strategy(df: pd.DataFrame, short_range=(5, 20), long_range=(25, 60)):
    best_profit = float('-inf')
    best_params = None

    print("🔍 전략 최적화 중...")

    for short in range(*short_range):
        for long in range(*long_range):
            if short >= long:
                continue
            profit = simulate_strategy(df.copy(), short, long)
            print(f"✅ short={short}, long={long} → 수익: {profit:,.0f}원")
            if profit > best_profit:
                best_profit = profit
                best_params = (short, long)

    print(f"\n🏆 최적 전략: short={best_params[0]}, long={best_params[1]} → 수익: {best_profit:,.0f}원")
    return best_params


def plot_equity_curve(df: pd.DataFrame, short: int, long: int):
    Config.MA_SHORT = short
    Config.MA_LONG = long
    trader = PaperTrader()
    cash_history = []
    current_cash = trader.cash

    for i in range(long + 1, len(df)):
        sample = df.iloc[:i+1]
        signal = moving_average_strategy(sample)
        price = df["Close"].iloc[i]

        if signal == "BUY":
            trader.buy("SIM", price, 1)
        elif signal == "SELL":
            trader.sell("SIM", price, 1)

        cash_history.append(trader.cash)

    plt.figure(figsize=(10, 5))
    plt.plot(df.index[long + 1:], cash_history, label="Equity Curve", color='blue')
    plt.title("📈 전략 누적 수익률 (Equity Curve)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()