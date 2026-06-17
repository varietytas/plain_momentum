from src.backtest import BacktestResult
from src.metrics import BacktestMetrics

import matplotlib.pyplot as plt


def visualize(
        result: BacktestResult,
        metrics: BacktestMetrics    
    ) -> None:
    """
    Unified visualization of backtest results.
    """

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].plot(result.equity_curve, color='darkblue')
    axes[0].set_ylabel('$', fontsize=12)
    axes[0].set_title('Equity Curve', fontweight='bold')
    axes[0].grid(alpha=0.5)

    #TODO: Make metrics legend bullets of the same color
    axes[0].plot([], [], 'o', label=f'Total Return: {metrics.total_return:.2%}')
    axes[0].plot([], [], 'o', label=f'CAGR: {metrics.cagr:.2%}')
    axes[0].plot([], [], 'o', label=f'Sharpe: {metrics.sharpe:.2f}')
    axes[0].plot([], [], 'o', label=f'Volatility: {metrics.volatility:.2%}')
    axes[0].plot([], [], 'o', label=f'Max DD: {metrics.max_drawdown:.2%}')
    axes[0].plot([], [], 'o', label=f'Turnover: {metrics.yearly_turnover:.2f}')
    axes[0].legend(loc='upper left')

    axes[1].plot(result.portfolio_returns, color='darkred', linewidth=0.5)
    axes[1].set_xlabel('Year', fontsize=12)
    axes[1].set_title('Daily Returns', fontweight='bold')
    axes[1].grid(alpha=0.5)

    plt.tight_layout()
    plt.show()
