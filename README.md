11.06.2026 Nasdaq-100 tickers list.

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
