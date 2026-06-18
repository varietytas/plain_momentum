from dataclasses import dataclass
import pandas as pd


@dataclass(slots=True)
class OHLCVData:
    open_:  pd.DataFrame
    high:   pd.DataFrame
    low:    pd.DataFrame
    close:  pd.DataFrame
    volume: pd.DataFrame
