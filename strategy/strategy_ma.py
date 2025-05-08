import pandas as pd
from config.settings import Config

def moving_average_strategy(df: pd.DataFrame) -> str :
    """
    이동평균선 전략 적용: 골든크로스 / 데드크로스 탐지

    :param df: 시세 데이터 (DataFrame, yfinance 포맷)
    :return: 'BUY', 'SELL', or 'HOLD'
    """

    short = Config.MA_SHORT
    long = Config.MA_LONG

    # 필수 컬럼 체크
    if 'Close' not in df.columns:
        print("❌ [오류] 'Close' 컬럼이 없습니다.")
        return "HOLD"

    # 충분한 데이터가 있는지 확인
    if len(df) < long + 2:
        print(f"⚠️ 데이터가 부족합니다. 최소 {long + 2}개 필요")
        return "HOLD"

    # 이동평균 계산 (복사본 사용하여 원본 보호)
    df = df.copy()
    df["MA_S"] = df["Close"].rolling(window=short).mean()
    df["MA_L"] = df["Close"].rolling(window=long).mean()

    # 최근 2일의 유효한 MA  데이터 확보
    recent = df[["MA_S", "MA_L"]].dropna().iloc[-2:]
    if len(recent) < 2:
        print("⚠️ 최근 이동평균 데이터가 부족합니다.")
        return "HOLD"

    # # 최근 2일 데이터 가져오기
    # ma_s_prev, ma_l_prev = recent.iloc[0]["MA_S"], recent.iloc[0]["MA_L"]
    # ma_s_curr, ma_l_curr = recent.iloc[1]["MA_S"], recent.iloc[1]["MA_L"]

    # 최근 2일 데이터 가져오기 - 단일 값으로 추출
    ma_s_prev = float(recent.iloc[0]["MA_S"])
    ma_l_prev = float(recent.iloc[0]["MA_L"])
    ma_s_curr = float(recent.iloc[1]["MA_S"])
    ma_l_curr = float(recent.iloc[1]["MA_L"])

    # 결측치 체크
    if pd.isna(ma_s_prev) or pd.isna(ma_l_prev) or pd.isna(ma_s_curr) or pd.isna(ma_l_curr):
        print("⚠️ 이동평균 계산 중 결측치 발생")
        return "HOLD"

    # 전략 조건 판단
    if ma_s_prev < ma_l_prev and ma_s_curr > ma_l_curr:
        return "BUY"
    elif ma_s_prev > ma_l_prev and ma_s_curr < ma_l_curr:
        return "SELL"
    else:
        return "HOLD"