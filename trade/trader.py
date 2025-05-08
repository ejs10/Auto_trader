# trade/trader.py

class PaperTrader:
    def __init__(self, initial_cash: float = 10_000_000):
        self._initial_cash = initial_cash  # 초기 투자금 추적
        self.cash = initial_cash
        self.positions = {}  # 종목: 수량
        self.trade_log = []  # 매매 내역 기록
        self.total_profit = 0.0
        self.position = 0  # 현재 포지션 수량 (dashboard.py에서 참조)

    def buy(self, ticker: str, price: float, quantity: int):
        """
        주식을 매수하는 함수

        :param ticker: 종목 심볼
        :param price: 주당 가격
        :param quantity: 매수 수량
        """
        # 타입 검사 및 변환
        price = float(price)
        quantity = int(quantity)

        total_cost = price * quantity

        if self.cash >= total_cost:
            self.cash -= total_cost
            self.positions[ticker] = self.positions.get(ticker, 0) + quantity
            self.position = self.positions.get(ticker, 0)  # 현재 포지션 업데이트
            self.trade_log.append((ticker, "BUY", price, quantity))
            print(f"✅ 매수: {ticker} {quantity}주 @ {price:.2f} | 잔고: {self.cash:,.0f}원")
        else:
            print("❌ 매수 실패: 잔고 부족")

    def sell(self, ticker: str, price: float, quantity: int):
        """
        주식을 매도하는 함수

        :param ticker: 종목 심볼
        :param price: 주당 가격
        :param quantity: 매도 수량
        """
        # 타입 검사 및 변환
        price = float(price)
        quantity = int(quantity)

        holding_qty = self.positions.get(ticker, 0)

        if holding_qty >= quantity:
            self.positions[ticker] = holding_qty - quantity
            self.position = self.positions.get(ticker, 0)  # 현재 포지션 업데이트
            sell_value = price * quantity
            self.cash += sell_value

            # 수익 계산 (단순화된 버전)
            # 실제로는 매수 가격을 기준으로 계산해야 함
            self.total_profit += sell_value - (self._initial_cash - self.cash)

            self.trade_log.append((ticker, "SELL", price, quantity))
            print(f"✅ 매도: {ticker} {quantity}주 @ {price:.2f} | 잔고: {self.cash:,.0f}원")
        else:
            print("❌ 매도 실패: 보유 수량 부족")

    def status(self):
        """현재 트레이딩 상태를 출력"""
        print("\n📊 현재 상태")
        print(f"💰 잔고: {self.cash:,.0f}원")
        print("📦 보유 종목:")
        for ticker, qty in self.positions.items():
            if qty > 0:
                print(f"   - {ticker}: {qty}주")
        print("📝 최근 거래:")
        for log in self.trade_log[-5:]:
            print(f"   {log[1]} {log[0]} {log[3]}주 @ {log[2]:.2f}")