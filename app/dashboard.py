# streamlit_app.py

import streamlit as st
import pandas as pd
from backtest.optimizer import plot_equity_curve
from strategy.strategy_ma import moving_average_strategy
from strategy.strategy_rsi import rsi_strategy
from config.settings import Config
from trade.trader import PaperTrader
from data.data_loader import get_price_data  # 누락된 임포트 추가

# --- 페이지 설정 ---
st.set_page_config(page_title="📊 전략 백테스트 대시보드", layout="centered")
st.title("📈 주식 자동매매 전략 대시보드")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 설정")
ticker = st.sidebar.selectbox("📌 종목 선택", ["AAPL", "TSLA", "GOOG", "MSFT"])
period = st.sidebar.selectbox("⏳ 데이터 기간", ["3mo", "6mo", "1y"])
strategy_type = st.sidebar.selectbox("🧠 전략 선택", ["이동평균 (MA)", "RSI"])

# MA 전략 설정
if strategy_type == "이동평균 (MA)":
    short_range = st.sidebar.slider("단기 이동평균", 5, 20, 5)
    long_range = st.sidebar.slider("장기 이동평균", 25, 60, 30)
    Config.MA_SHORT = short_range
    Config.MA_LONG = long_range

elif strategy_type == "RSI":
    rsi_period = st.sidebar.slider("RSI 기간", 5, 30, 14)
    rsi_overbought = st.sidebar.slider("과매수 기준", 60, 90, 70)
    rsi_oversold = st.sidebar.slider("과매도 기준", 10, 40, 30)

# 백테스트 실행
if st.sidebar.button("🚀 백테스트 실행"):
    try:
        # 데이터 로딩
        with st.spinner("데이터 로딩 중..."):
            df = get_price_data(ticker, period=period)

            if df.empty:
                st.error(f"❌ {ticker} 데이터를 가져오지 못했습니다. 다른 종목을 시도해보세요.")
                st.stop()

        st.success(f"📥 데이터 로딩 완료: {ticker} ({period})")

        # 데이터 정보 표시
        st.subheader("📉 데이터 미리보기")
        st.dataframe(pd.concat([df.head(3), df.tail(3)]))

        # 트레이더 및 백테스트 준비
        trader = PaperTrader()
        equity_curve = []
        signal_history = []
        price_history = []

        # 충분한 데이터 확인
        min_data_needed = 30  # 최소 필요 데이터 수
        if strategy_type == "이동평균 (MA)":
            min_data_needed = max(min_data_needed, long_range + 2)
        elif strategy_type == "RSI":
            min_data_needed = max(min_data_needed, rsi_period + 10)

        if len(df) < min_data_needed:
            st.error(f"❌ 데이터가 부족합니다. 최소 {min_data_needed}개 필요, 현재 {len(df)}개.")
            st.stop()

        # 백테스트 진행
        with st.spinner("백테스트 수행 중..."):
            for i in range(min_data_needed, len(df)):
                window_df = df.iloc[:i + 1].copy()  # 명시적으로 복사본 사용
                price = float(df["Close"].iloc[i])  # float로 명시적 변환
                price_history.append(price)

                # 전략 시그널 계산
                if strategy_type == "이동평균 (MA)":
                    signal = moving_average_strategy(window_df)
                elif strategy_type == "RSI":
                    signal = rsi_strategy(
                        window_df,
                        period=rsi_period,
                        overbought=rsi_overbought,
                        oversold=rsi_oversold
                    )
                else:
                    signal = "HOLD"

                signal_history.append(signal)

                # 트레이딩 수행
                if signal == "BUY":
                    trader.buy(ticker, price, 1)
                elif signal == "SELL":
                    trader.sell(ticker, price, 1)

                # 자산기록 (현금 + 주식)
                position_value = trader.positions.get(ticker, 0) * price
                total_value = trader.cash + position_value
                equity_curve.append(total_value)

        # 결과 시각화
        st.subheader("📈 백테스트 결과")

        # 시그널 통계
        buy_signals = signal_history.count("BUY")
        sell_signals = signal_history.count("SELL")

        # 지표 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 수익", f"${trader.total_profit:.2f}")
        with col2:
            st.metric("매수 신호", f"{buy_signals}회")
        with col3:
            st.metric("매도 신호", f"{sell_signals}회")

        st.caption(f"📌 최종 잔고: ${trader.cash:.2f} / 보유 수량: {trader.position}")

        # 자산 곡선 차트
        st.subheader("💰 자산 추이")

        # 날짜와 데이터가 일치하는지 확인
        dates = df.index[min_data_needed:].tolist()
        if len(dates) == len(equity_curve):
            chart_data = pd.DataFrame({
                'Date': dates,
                'Equity': equity_curve,
                'Price': price_history
            })
            chart_data.set_index('Date', inplace=True)

            # 정규화하여 가격과 자산을 같은 차트에 표시
            if not chart_data.empty and len(chart_data) > 1:
                normalized_data = pd.DataFrame({
                    'Equity': chart_data['Equity'] / chart_data['Equity'].iloc[0] * 100,
                    'Price': chart_data['Price'] / chart_data['Price'].iloc[0] * 100
                })
                st.line_chart(normalized_data)
            else:
                st.warning("차트를 그릴 수 있는 충분한 데이터가 없습니다.")
        else:
            st.warning("날짜와 데이터 포인트 수가 일치하지 않습니다.")

        # 추가 정보 표시
        with st.expander("📊 상세 거래 내역"):
            if not trader.trade_log:
                st.info("거래 내역이 없습니다.")
            else:
                trade_df = pd.DataFrame(trader.trade_log, columns=['종목', '유형', '가격', '수량'])
                st.dataframe(trade_df)

    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        import traceback

        st.code(traceback.format_exc())