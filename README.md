close.parquet
volume.parquet
        │
        ▼
Data Loader
        │
        ▼
Signal Generation
        │
        ▼
Portfolio Construction
        │
        ▼
Backtest Engine
        │
        ▼
Performance Analytics




momentum/
│
├── data/
│   ├── close.parquet
│   ├── open.parquet
│   ├── high.parquet
│   ├── low.parquet
│   ├── volume.parquet
│   └── tickers.csv
│
├── src/
│   ├── data_loader.py
│   ├── signals.py
│   ├── portfolio.py
│   ├── backtest.py
│   ├── metrics.py
│   └── config.py
│
├── notebooks/
│   └── research.ipynb
│
└── main.py

Total Return: 2571.59%
CAGR: 34.91%
Sharpe: 1.22
Volatility: 27.62%
Max DD: -37.10%