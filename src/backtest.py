import src.config as cfg
import src.signals as sig
import src.portfolio as prtf

from dataclasses import dataclass
import pandas as pd


@dataclass(slots=True)
class BacktestResult:
    portfolio_returns: pd.Series
    equity_curve: pd.Series
    weights: pd.DataFrame
    costs: pd.Series


#TODO: Abstract away market data (maybe some MarketData class)
#TODO: Abstract away signal (signal df itself OR the choice of signal function) 
def run_backtest(
        close: pd.DataFrame,
        lookback: int = cfg.LOOKBACK,
        rebalance: int = cfg.REBALANCE,
        top_quantile: float = cfg.TOP_QUANTILE,
        transaction_cost: float = cfg.TRANSACTION_COST
    ) -> BacktestResult:

    signal = sig.skipmonth_momentum(close, lookback)

    returns = close.pct_change()

    weights = pd.DataFrame(
        index=close.index,
        columns=close.columns,
        dtype=float
    )

    rebalance_dates = close.index[::rebalance]

    # Transaction costs
    costs = pd.Series(0.0, index=close.index)
    prev_weights = pd.Series(0.0, index=close.columns)

    # Building weights for rebalance dates
    for date in rebalance_dates:
        signal_snapshot = signal.loc[date]

        weights_snapshot = prtf.build_long_only_portfolio(
            signal_snapshot,
            top_quantile
        )
        weights.loc[date, weights_snapshot.index] = weights_snapshot

        turnover = (weights_snapshot - prev_weights).abs().sum()
        costs.loc[date] = turnover * transaction_cost
        prev_weights = weights_snapshot

    # Hold portfolio between rebalance dates:
    # Forward fill for the gaps, then fill remaining NaNs with 0.0
    weights = weights.ffill().fillna(0.0)

    # Look-ahead bias protection: execution on the next day
    weights = weights.shift(1).fillna(0.0)

    portfolio_returns = (weights * returns).sum(axis=1)
    portfolio_returns -= costs
    portfolio_returns = portfolio_returns.fillna(0.0)

    equity_curve = (1 + portfolio_returns).cumprod().dropna()

    return BacktestResult(
        portfolio_returns=portfolio_returns,
        equity_curve=equity_curve,
        weights=weights,
        costs=costs
    )
