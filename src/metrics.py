import src.config as cfg
from src.backtest import BacktestResult

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class BacktestMetrics:

    total_return: float
    cagr: float
    volatility: float
    sharpe: float
    max_drawdown: float
    total_turnover: float
    yearly_turnover: float
    avg_rebalance_turnover: float

    def __str__(self) -> str:
        return (
            f'Total Return:             {self.total_return:.2%}\n'
            f'CAGR:                     {self.cagr:.2%}\n'
            f'Volatility:               {self.volatility:.2%}\n'
            f'Sharpe Ratio:             {self.sharpe:.2f}\n'
            f'Max Drawdown:             {self.max_drawdown:.2%}\n'
            f'Total Turnover:           {self.total_turnover:.2f}\n'
            f'Yearly Turnover:          {self.yearly_turnover:.2f}\n'
            f'Avg. Rebalance Turnover:  {self.avg_rebalance_turnover:.2f}'
        )


def calculate_metrics(
        result: BacktestResult,
        rf_rate: float = cfg.RISK_FREE_RATE,
        transaction_cost: float = cfg.TRANSACTION_COST
    ) -> BacktestMetrics:
    """
    Calculate common portfolio performance metrics.

    Parameters
    ----------
    result : BacktestResult
        Output of the backtester.
    risk_free_rate : float, default=0.0
        Annual risk-free rate.

    Returns
    -------
    BacktestMetrics
    """

    returns = result.portfolio_returns
    equity = result.equity_curve
    if len(returns) == 0 or len(equity) == 0:
        raise ValueError('BacktestResult contains no data.')

    # Total Return
    total_return = equity.iloc[-1] - 1.0

    # CAGR
    years = len(returns) / 252
    if years > 0:
        cagr = equity.iloc[-1] ** (1 / years) - 1
    else:
        cagr = np.nan

    # Annualized Volatility
    daily_vol = returns.std()
    volatility = daily_vol * np.sqrt(252)

    # Sharpe Ratio
    daily_rf = rf_rate / 252
    excess_returns = returns - daily_rf
    if daily_vol > 0:
        sharpe = (excess_returns.mean() / daily_vol * np.sqrt(252))
    else:
        sharpe = np.nan

    # Maximum Drawdown
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    max_drawdown = drawdown.min()

    # Turnover
    turnover = result.costs / transaction_cost
    total_turnover = turnover.sum()
    yearly_turnover = total_turnover / years
    avg_rebalance_turnover = turnover.mean()

    return BacktestMetrics(
        total_return=total_return,
        cagr=cagr,
        volatility=volatility,
        sharpe=sharpe,
        max_drawdown=max_drawdown,
        total_turnover=total_turnover,
        yearly_turnover=yearly_turnover,
        avg_rebalance_turnover=avg_rebalance_turnover
    )
