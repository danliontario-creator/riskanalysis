# ==========================================================
# RiskAnalysis_Advanced.py — Portfolio Risk Analytics Engine
# ==========================================================
import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generate_report():
    # ----------------------------------------------------------
    # 1. Data Download
    # ----------------------------------------------------------
    tickers = ['AAPL', 'MSFT', 'TSLA', 'AMZN', 'JPM']
    data = yf.download(tickers, start='2020-01-01', end='2025-01-01', progress=False)['Close']

    weights = {'AAPL': 0.25, 'MSFT': 0.25, 'TSLA': 0.2, 'AMZN': 0.2, 'JPM': 0.1}

    # ----------------------------------------------------------
    # 2. Portfolio Calculations
    # ----------------------------------------------------------
    returns = data.pct_change().dropna()
    portfolio_returns = (returns * list(weights.values())).sum(axis=1)

    initial_investment = 100000
    portfolio_value = initial_investment * (1 + portfolio_returns).cumprod()
    portfolio_pnl = portfolio_value - initial_investment

    # Annualized risk metrics
    volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = ((portfolio_returns.mean() * 252) - 0.02) / volatility

    # ----------------------------------------------------------
    # 3. Beta (vs S&P 500)
    # ----------------------------------------------------------
    benchmark = yf.download('^GSPC', start='2020-01-01', end='2025-01-01', progress=False)['Close']
    benchmark_returns = benchmark.pct_change().dropna()

    aligned_portfolio, aligned_benchmark = portfolio_returns.align(benchmark_returns, join='inner')
    aligned_portfolio = aligned_portfolio.to_numpy().flatten()
    aligned_benchmark = aligned_benchmark.to_numpy().flatten()

    cov_matrix = np.cov(np.vstack([aligned_portfolio, aligned_benchmark]))
    beta = cov_matrix[0, 1] / cov_matrix[1, 1]


    # ----------------------------------------------------------
    # 4. Maximum Drawdown
    # ----------------------------------------------------------
    rolling_max = portfolio_value.cummax()
    drawdown = (portfolio_value - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # ----------------------------------------------------------
    # 5. Rolling Sharpe Ratio
    # ----------------------------------------------------------
    window = 90
    risk_free_rate_daily = 0.02 / 252
    rolling_sharpe = (
        (portfolio_returns.rolling(window).mean() - risk_free_rate_daily)
        / portfolio_returns.rolling(window).std()
    ) * np.sqrt(252)

    # ----------------------------------------------------------
    # 6. Save to Excel
    # ----------------------------------------------------------
    os.makedirs("reports", exist_ok=True)
    FILE_PATH = "reports/Portfolio_Analysis_Advanced.xlsx"

    metrics = pd.DataFrame({
        'Metric': [
            'Final Value',
            'Total PnL',
            'Annualized Return (CAGR)',
            'Volatility (Annualized)',
            'Sharpe Ratio',
            'Beta vs S&P 500',
            'Maximum Drawdown'
        ],
        'Value': [
            portfolio_value.iloc[-1],
            portfolio_pnl.iloc[-1],
            (portfolio_value.iloc[-1] / initial_investment) ** (1 / 5) - 1,
            volatility,
            sharpe_ratio,
            beta,
            max_drawdown
        ]
    })

    with pd.ExcelWriter(FILE_PATH) as writer:
        portfolio_value.to_excel(writer, sheet_name='Portfolio Value')
        returns.to_excel(writer, sheet_name='Daily Returns')
        drawdown.to_excel(writer, sheet_name='Drawdown')
        rolling_sharpe.to_excel(writer, sheet_name='Rolling Sharpe')
        data.to_excel(writer, sheet_name='Price Data')
        metrics.to_excel(writer, sheet_name='Summary Metrics', index=False)

    print(f"✅ Export complete → {FILE_PATH}")

if __name__ == "__main__":
    generate_report()
