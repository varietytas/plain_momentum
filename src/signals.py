import src.config as cfg
import pandas as pd


def momentum(
        close: pd.DataFrame,
        lookback: int = cfg.LOOKBACK
    ) -> pd.DataFrame:
    """
    Cross-sectional momentum signal.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close prices.
    lookback : int
        Lookback window in trading days.

    Returns
    -------
    pd.DataFrame
        Momentum values for every asset and date.
    """

    return close / close.shift(lookback) - 1
