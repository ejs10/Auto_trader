// auto_trader/app/static/main.js

async function runBacktest() {
  const ticker = document.getElementById("ticker").value;
  const period = document.getElementById("period").value;
  const strategy = document.getElementById("strategy").value;

  const payload = {
    ticker: ticker,
    period: period,
    strategy: strategy,
    params: {} // 필요시 사용자 인풋 추가 가능
  };

  const res = await fetch("/backtest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (data.error) {
    document.getElementById("resultText").innerText = "❌ 오류: " + data.error;
    return;
  }

  // 📋 텍스트 결과
  document.getElementById("resultText").innerText = `
총 수익: $${data.total_profit.toFixed(2)}
보유 현금: $${data.cash.toFixed(2)}
현재 포지션: ${data.position}
`;

  // 📊 차트 생성
  const dates = data.price_data.map(p => p.date);
  const prices = data.price_data.map(p => p.Close);

  const signalMap = {};
  data.signals.forEach(sig => {
    signalMap[sig.date] = sig.signal;
  });

  const signalColors = dates.map(date => {
    if (signalMap[date] === "BUY") return "green";
    if (signalMap[date] === "SELL") return "red";
    return "gray";
  });

  const ctx = document.getElementById("priceChart").getContext("2d");
  if (window.priceChart) window.priceChart.destroy();

  window.priceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [{
        label: "종가",
        data: prices,
        borderColor: "blue",
        pointBackgroundColor: signalColors,
        pointRadius: 4,
        fill: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            label: function(context) {
              const date = context.label;
              const signal = signalMap[date];
              return `가격: ${context.formattedValue} (${signal || 'HOLD'})`;
            }
          }
        }
      },
      scales: {
        x: { display: true },
        y: { display: true }
      }
    }
  });
}