import os
from dotenv import load_dotenv

# .env 파일 로딩

class Config:
    # 거래 API 설정
    BROKER = os.getenv("BROKER", "ALPACA")  # 예: "KIWOOM", "ALPACA"
    API_KEY = os.getenv("API_KEY", "")
    API_SECRET = os.getenv("API_SECRET", "")
    ACCOUNT_ID = os.getenv("ACCOUNT_ID", "")

    # 거래 기본 설정
    TICKER = "AAPL"  # 예시 종목 코드 (키움은 '005930'처럼 사용)
    TRADE_QUANTITY = 10  # 한 번에 매수/매도할 수량
    TRADE_MODE = "PAPER"  # "REAL" or "PAPER" (페이퍼 트레이딩용)

    # 전략 설정
    MA_SHORT = 5  # 단기 이동평균일수
    MA_LONG = 20  # 장기 이동평균일수

    # 알림 설정
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")