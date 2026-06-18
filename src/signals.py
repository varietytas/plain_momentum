import src.config as cfg
import pandas as pd


#TODO: close: pd.DataFrame ---> md: OHLCVData for future more sophisticated signals
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
        Signal values for every asset and date.
    """

    return close / close.shift(lookback) - 1


def riskadj_momentum(
        close: pd.DataFrame,
        lookback: int = cfg.LOOKBACK
    ) -> pd.DataFrame:
    """
    Cross-sectional risk-adjusted momentum signal.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close prices.
    lookback : int
        Lookback window in trading days.

    Returns
    -------
    pd.DataFrame
        Signal values for every asset and date.
    """

    return (close / close.shift(lookback) - 1) / close.pct_change().rolling(lookback).std()


def skipmonth_momentum(
        close: pd.DataFrame,
        lookback: int = cfg.LOOKBACK
    ) -> pd.DataFrame:
    """
    Cross-sectional momentum signal.
    Skipping the most recent month (21 day) within the lookback window.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close prices.
    lookback : int
        Lookback window in trading days.

    Returns
    -------
    pd.DataFrame
        Signal values for every asset and date.
    """

    return close.shift(21) / close.shift(lookback) - 1


def riskadj_skipmonth_momentum(
        close: pd.DataFrame,
        lookback: int = cfg.LOOKBACK
    ) -> pd.DataFrame:
    """
    Cross-sectional risk-adjusted momentum signal.
    Divide the skipmonth momentum by the volatility of returns over the (lookback - 21) window.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close prices.
    lookback : int
        Lookback window in trading days.

    Returns
    -------
    pd.DataFrame
        Signal values for every asset and date.
    """

    return (close.shift(21) / close.shift(lookback) - 1) / close.pct_change().shift(21).rolling(lookback - 21).std()
