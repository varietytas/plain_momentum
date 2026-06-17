from os import path
from pathlib import Path

import pandas as pd
import yfinance as yf


BASE_DIR = Path(__file__).resolve().parents[1]
TICKERS_FILE = path.join(BASE_DIR, 'data', 'tickers.csv')
START_DATE = '2015-01-01'
END_DATE = '2025-12-31'


tickers = pd.read_csv(TICKERS_FILE)['Symbol'].tolist()

print(f'[✅] Loaded {len(tickers)} tickers.')

data = yf.download(
    tickers=tickers,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,   # Adjusts prices for splits and dividends
    group_by='column',
    threads=True
)

open_p = data['Open']
high   = data['High']
low    = data['Low']
close  = data['Close']
volume = data['Volume']

open_p_nan_cnt = open_p.isna().sum().sum()
high_nan_cnt   = high.isna().sum().sum()
low_nan_cnt    = low.isna().sum().sum()
close_nan_cnt  = close.isna().sum().sum()
volume_nan_cnt = volume.isna().sum().sum()

if open_p_nan_cnt + high_nan_cnt + low_nan_cnt + close_nan_cnt + volume_nan_cnt == 0:
    print('[✅] No missing values found.')
else:
    years = range(
        close.index.min().year,
        close.index.max().year + 1
    )
    tickers_nan = [tk for tk, x in close.isna().sum().items() if x > 0]

    print(
        '[🟡] Missing values detected.\n'
        f'\tIn {len(tickers_nan)} columns (judging by Close):\n'
        f'\t\t{', '.join(tickers_nan)}\n'
        '\tTickers with history by years (only full year counts):'
    )
    for y in years:
        year_close = close[close.index.year == y]
        eligible_stocks = len(tickers) - len([tk for tk, x in year_close.isna().sum().items() if x > 0])

        print(f'\t\t{y} -> {eligible_stocks} ({(eligible_stocks/len(tickers))*100:.1f}%)')

    del years, tickers_nan, eligible_stocks, year_close


if open_p.columns.equals(volume.columns) and \
    high.columns.equals(volume.columns) and \
    low.columns.equals(volume.columns) and \
    close.columns.equals(volume.columns):

    print('[✅] All columns are aligned.')
else:
    print('[❌] Columns are not aligned. Inspection required.')
    exit(1)

# -------------- Save --------------

open_p.to_parquet(
    path.join(BASE_DIR, 'data', 'open.parquet'),
    engine='pyarrow'
)
high.to_parquet(
    path.join(BASE_DIR, 'data', 'high.parquet'),
    engine='pyarrow'
)
low.to_parquet(
    path.join(BASE_DIR, 'data', 'low.parquet'),
    engine='pyarrow'
)
close.to_parquet(
    path.join(BASE_DIR, 'data', 'close.parquet'),
    engine='pyarrow'
)
volume.to_parquet(
    path.join(BASE_DIR, 'data', 'volume.parquet'),
    engine='pyarrow'
)

print('[✅] Saved.')
