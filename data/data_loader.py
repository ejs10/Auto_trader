import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def get_price_data(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """
    특정 종목의 과거 시세 데이터를 가져옵니다.

    :param ticker: 티커 심볼 (예: 'AAPL', 'MSFT')
    :param period: 조회 기간 (예: '1d', '5d', '1mo', '3mo', '1y')
    :param interval: 데이터 간격 (예: '1m', '5m', '1d')
    :return: 시세 데이터 (DataFrame)
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        data.dropna(inplace=True)
        return data
    except Exception as e:
        print(f"[ERROR] 데이터 수집 실패: {e}")
        return pd.DataFrame()