# plain_momentum

A compact, from-scratch framework for **learning, inspecting and backtesting
cross-sectional momentum strategies** on Nasdaq-100 equities.

It is deliberately small and readable: every step of the pipeline — signal generation,
portfolio construction, the backtest loop, and the performance metrics — lives in a
single short module so the mechanics and the math stay transparent. The point is
learning, not production trading.

**Capabilities**

- Several pluggable cross-sectional **momentum signals**
- **Equal-weighted long-only** portfolio construction from the top quantile of a signal
- **Vectorized backtest engine** with scheduled rebalancing, buy-and-hold between rebalances, and turnover-based **transaction costs**
- Standard **performance-metrics** suite (total return, CAGR, annualized volatility,
  Sharpe, max drawdown, turnover)
- **Visualization** of the results
- **Config** file of defaults

**Data** — daily OHLCV for the Nasdaq-100 universe (101 tickers) pulled from Yahoo
Finance via `yfinance` with `auto_adjust=True` (prices adjusted for splits and dividends), spanning 2015-01-02 → 2025-12-30, cached locally as Parquet.


## Features

- **Signals** — `momentum`, `riskadj_momentum`, `skipmonth_momentum`,
  `riskadj_skipmonth_momentum`. Each maps a price panel to a signal panel
- **Portfolio** — `build_long_only_portfolio`: equal weights across the top-`q` names
- **Backtest** — `run_backtest`: pandas-vectorized, returns a `BacktestResult`
  (portfolio returns, equity curve, weights, costs)
- **Costs** — linear transaction cost charged on rebalance turnover
- **Metrics** — `calculate_metrics`, a printable `BacktestMetrics`
- **Plots** — `visualize`: equity curve + daily returns
- **Config** — lookback, rebalance period, quantile, cost, risk-free rate


## Project layout

```
plain_momentum/
├── data/
│   ├── price_retrieval.py   # Download OHLCV from yfinance to Parquet
│   ├── tickers.csv          # Nasdaq-100 symbol list
│   ├── open.parquet         # Cached panels: dates × tickers
│   ├── high.parquet
│   ├── low.parquet
│   ├── close.parquet        # Adjusted close
│   └── volume.parquet
├── src/
│   ├── config.py            # Defaults
│   ├── data.py              # OHLCVData dataclass (container for the panels)
│   ├── signals.py           # Momentum signals
│   ├── portfolio.py         # Portfolio construction
│   ├── backtest.py          # run_backtest + BacktestResult
│   ├── metrics.py           # calculate_metrics + BacktestMetrics
│   └── visres.py            # visualize(result, metrics)
├── main.ipynb               # Usage example
└── requirements.txt
```

**Data contract.** The whole pipeline speaks one shape. Price panels are
`pandas.DataFrame`s indexed by date (rows) with tickers as columns. A **signal** is a
DataFrame of the same shape (one signal value per asset per day). **Weights** share that
shape too. On a single rebalance date the signal/weights collapse to a `pandas.Series`
indexed by ticker — a *cross-section*, which is what `build_long_only_portfolio`
consumes and returns.


## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) refresh the cached price data
python data/price_retrieval.py
```

```python
import pandas as pd
from src.data import OHLCVData
import src.signals as sig
import src.backtest as bt
import src.metrics as mtrc
from src.visres import visualize

# Load the adjusted-close panel (dates × tickers)
close = pd.read_parquet('data/close.parquet')
md = OHLCVData(None, None, None, close, None)

# Pick a signal, run the backtest, score it
signal  = sig.skipmonth_momentum(md.close)
result  = bt.run_backtest(md, signal)
metrics = mtrc.calculate_metrics(result)

print(metrics)
visualize(result, metrics)
```

See [`main.ipynb`](main.ipynb) for the same flow.


## Mathematical formulation

### Notation

| Symbol | Meaning |
| --- | --- |
| $N$ | number of assets in the universe; $i = 1, \dots, N$ |
| $t$ | trading-day index, $t = 0, 1, \dots, T$ |
| $P_{i,t}$ | adjusted close price of asset $i$ on day $t$ |
| $r_{i,t} = \dfrac{P_{i,t}}{P_{i,t-1}} - 1$ | daily simple return of asset $i$ |
| $L$ | lookback window, in trading days |
| $R$ | rebalance period, in trading days (default 21) |
| $S$ | skip window, in trading days (default 21) |
| $q$ | top quantile selected long |
| $\kappa$ | per-unit linear transaction cost |
| $r_f$ | annual risk-free rate |
| $\text{std}()$ | sample standard deviation, `ddof = 1` |

Annualization uses 252 trading days per year.

### Signals

Each signal is evaluated cross-sectionally for every asset $i$ at every date $t$.

**1. Plain momentum** — trailing $L$-day return.

$$M_{i,t} = \frac{P_{i,t}}{P_{i,t-L}} - 1$$

**2. Risk-adjusted momentum** — momentum scaled by its own return volatility.

$$M^{\text{ra}}_{i,t} = \frac{P_{i,t}/P_{i,t-L} - 1}{\sigma_{i,t}}, \qquad
\sigma_{i,t} = \text{std}\big(\{r_{i,s}\}_{s=t-L+1}^{t}\big)$$

**3. Skip-month momentum** — drops the most recent month ($S$ days) to sidestep
short-term reversal.

$$M^{\text{skip}}_{i,t} = \frac{P_{i,t-S}}{P_{i,t-L}} - 1$$

**4. Risk-adjusted skip-month momentum** — combines the two ideas.

$$M^{\text{ra,skip}}_{i,t} = \frac{P_{i,t-S}/P_{i,t-L} - 1}{\sigma^{\text{skip}}_{i,t}},
\qquad
\sigma^{\text{skip}}_{i,t} = \text{std}\big(\{r_{i,s}\}_{s=t-L+1}^{t-S}\big)$$

### Portfolio selection

Long-only, evaluated on each rebalance date $\tau$. Let
$A_\tau$ be the assets with a non-missing signal at $\tau$,
$N_\tau = |A_\tau|$, and let $W_\tau \subseteq A_\tau$ be
the $n_\tau$ assets with the highest signal values, where

$$n_\tau = \max\big(1,\ \lfloor N_\tau \, q \rfloor\big).$$

Each winner receives an equal weight; everything else is zero:

$$
w_{i,\tau} =
\begin{cases}
    \dfrac{1}{n_\tau} & i \in W_\tau \\
    0 & \text{otherwise}
\end{cases}
\qquad \sum_{i} w_{i,\tau} = 1.
$$

### Holding and execution lag

Weights are set only on rebalance dates ($\tau \in T$, every $R$ days) and
held constant in between (forward fill). Write $\tilde{w}_{i,t}$ for that
forward-filled weight. To prevent look-ahead bias, the held weight vector is lagged one
day before being applied, so the weight acting on day $t$ is

$$w_{i,t} = \tilde{w}_{i,\,t-1}.$$

### P&L (close-to-close)

The gross portfolio return is the weighted sum of asset returns; the net return
subtracts the day's cost:

$$r^{p}_{t} = \sum_{i=1}^{N} w_{i,t} \hspace{1mm} r_{i,t} - c_{t}.$$

> **⚠️ Limitation — close-to-close accounting.** Asset returns $r_{i,t}$ are computed
> close-to-close (`close.pct_change()`). Signals are formed at one close, the trade is
> lagged one day, and P&L is still marked close-to-close. This is a reasonable
> simplification, but optimistic: a realistic setup should **execute at the next open**
> (open-to-close on the entry day, then close-to-close while the position is held).
>
> *Minor related caveat:* the rebalance cost $c_\tau$ is charged on the rebalance date,
> while the position change it pays for only takes effect the next day (the one-day lag
> above) — a timing mismatch.

### Transaction costs

On each rebalance date $\tau$, cost is linear in turnover relative to the previous set
of target weights $w^{-}$ (initialized to zero):

$$\text{TO}_\tau = \sum_{i=1}^{N} \big\lvert w_{i,\tau} - w^{-}_{i} \big\rvert,
\qquad c_\tau = \kappa \hspace{1mm} \text{TO}_\tau,$$

with $c_t = 0$ on non-rebalance days.

### Equity curve

Compounding the net daily returns from a base of 1:

$$E_t = \prod_{s=0}^{t} \big(1 + r^{p}_{s}\big), \qquad E_{-1} \equiv 1.$$

### Performance metrics

Computed over the $T + 1$ daily return observations, with $y = \dfrac{T+1}{252}$ the
sample length in years:

$$\text{Total Return} = E_T - 1, \qquad \text{CAGR} = E_T^{1/y} - 1,$$

$$\text{Volatility} = \text{std}(r^{p}) \cdot \sqrt{252}, \qquad
\text{Sharpe} = \frac{\overline{r^{p} - r_f/252}}{\text{std}(r^{p})} \cdot \sqrt{252},$$

$$\text{MaxDD} = \min_{t} \frac{E_t - \max_{s \le t} E_s}{\max_{s \le t} E_s}.$$

Turnover summaries:

$$\text{Total TO} = \sum_{\tau \in T} \text{TO}_\tau, \qquad
\text{Yearly TO} = \frac{\text{Total TO}}{y}, \qquad
\text{Avg TO} = \frac{1}{T+1} \sum_{t} \text{TO}_t.$$

> **⚠️ Note** that **Avg TO** averages the per-day turnover series over *all* trading days
> (turnover is zero off the rebalance dates) — this is `turnover.mean()` in the code, not
> the mean taken over rebalance dates only.


## Configuration

Defaults live in [`src/config.py`](src/config.py) and can be overridden per call.

| Parameter | Symbol | Meaning |
| --- | --- | --- |
| `LOOKBACK` | $L$ | Momentum lookback window (≈ 6 months) |
| `REBALANCE` | $R$ | Days between rebalances (≈ 1 month) |
| `TOP_QUANTILE` | $q$ | Fraction of the universe held long |
| `TRANSACTION_COST` | $\kappa$ | Cost per unit of turnover (5 bps) |
| `RISK_FREE_RATE` | $r_f$ | Annual risk-free rate for Sharpe |

The skip window $S = 21$ is currently hardcoded inside the skip-month signals.


## Future work

- **More signals.**
  - *Regression momentum* — fit a trend to log-prices over the lookback and score by
    slope $\times R^2$ (trend strength weighted by fit quality).
  - *Multi-horizon / composite momentum* — blend several lookbacks into one score. Open
    question: how to weight the horizons — equal, volatility-scaled, or learned?
  - *Residual momentum* — momentum of the residuals from a factor-model regression,
    stripping out common (e.g. market) exposure.
- **Open-execution P&L.** Replace the close-to-close accounting with next-open execution
  for a more realistic fill model.
- **Parameter research.** Grid-sweep parameters into a metrics DataFrame and
  visualize (e.g. a heatmap) to study which configuration works best on this dataset.
- **Long-short portfolio.** Add `build_long_short_portfolio`: long the top quantile and
  short the bottom quantile, alongside the existing long-only mode.


## Disclaimer

This is an educational / research project for studying momentum strategies. All results
are historical backtests built on simplifying assumptions.

P.S. LaTeX in GitHub is rendered awfully...
