import src.config as cfg
import pandas as pd


def build_long_only_portfolio(
        signal: pd.Series,
        top_quantile: float = cfg.TOP_QUANTILE,
    ) -> pd.Series:
    """
    Build an equal-weighted long-only portfolio from a cross-sectional signal.

    Parameters
    ----------
    signal : pd.Series
        Signal values for a single rebalance date.
    top_quantile : float
        Fraction of assets to include in the portfolio.

    Returns
    -------
    pd.Series
        Portfolio weights. Weights sum to 1.
    """

    assert 0 < top_quantile <= 1, 'Unacceptable TOP_QUANTILE.'

    signal = signal.dropna()
    if signal.empty:
        return pd.Series(dtype=float)

    signal = signal.sort_values(ascending=False)

    n_assets = max(
        1,
        int(len(signal) * top_quantile)
    )

    # Index = tickers
    winners = signal.index[:n_assets]

    weights = pd.Series(
        0.0,
        index=signal.index
    )
    weights.loc[winners] = 1.0 / n_assets
    assert abs(weights.sum() - 1.0) < 1e-9, 'Weights do not sum up to 1.'

    return weights
