# backtest/backtester.py

import pandas as pd
from strategy.strategy_ma import moving_average_strategy
from trade.trader import PaperTrader


def run_backtest(df: pd.DataFrame, ticker: str, quantity: int = 1):
    """
    주어진 데이터프레임과 종목에 대해 백테스트를 실행합니다.

    :param df: 시세 데이터 DataFrame
    :param ticker: 종목 코드
    :param quantity: 매매 수량
    :return: 백테스트 결과 딕셔너리
    """
    trader = PaperTrader()
    buy_price = None
    daily_returns = []

    # 전체 데이터 순회하면서 전략 적용
    for i in range(30, len(df)):  # 30일 이후부터 충분한 이동평균 확보
        sample = df.iloc[:i + 1]
        signal = moving_average_strategy(sample)
        current_price = df["Close"].iloc[i]

        if signal == "BUY":
            trader.buy(ticker, current_price, quantity)
            buy_price = current_price
        elif signal == "SELL":
            trader.sell(ticker, current_price, quantity)
            buy_price = None
        # else: HOLD → 아무것도 안함

        # 누적 수익률 계산
        trader.update_total_profit()  # 총 수익 업데이트
        daily_returns.append(trader.total_profit)

    # 최종 결과 출력
    trader.status()

    result = {
        "total_profit": trader.total_profit,
        "cash": trader.cash,
        "position": trader.positions.get(ticker, 0),  # 수정: positions 딕셔너리 접근
        "returns": daily_returns,  # 📈 Streamlit용 그래프 데이터
    }
    return result