# Trading Strategy Optimiser

A lightweight framework for **walk-forward optimisation** of algorithmic trading strategies.

Define your strategy with a simple `on_tick` callback. The optimiser then finds parameters on successive in-sample windows and evaluates them out-of-sample, helping reduce overfitting.

## Features

- Walk-forward optimisation using SciPy’s Differential Evolution
- Fast backtesting engine powered by Sparse Tables (O(1) range max/min)
- Custom indicators support (SMA included)
- Flexible trade model with stop-loss / take-profit
- Equity curve plotting
- Candle data visualisation with Plotly
- Ready-to-use data downloader (Dukascopy)

## Project Structure

```
├── candle_data.py      # Core data structure + fast strategy runner
├── optimiser.py        # Walk-forward optimisation loop
├── trade.py            # Trade class
├── indicators.py       # Technical indicators
├── sparse_table.py     # Sparse Table for range queries
├── plot_equity.py      # Equity curve visualisation
├── download.py         # Example data downloader
├── template.ipynb      # Starter notebook
└── README.md
```

## Installation

```bash
git clone https://github.com/anuragskadam/trading-strategy-optimiser.git
cd trading-strategy-optimiser

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install numpy pandas scipy matplotlib plotly dukascopy-python
```

## How it Works

The optimiser performs rolling walk-forward analysis:

1. Optimise parameters on an **in-sample** window
2. Apply the best parameters on the following **out-of-sample** window
3. Advance the window and repeat

This gives a more realistic estimate of strategy performance on unseen data.

## Core Components

- **CandleData**: Loads OHLCV data and runs strategies extremely fast using Sparse Tables for stop-loss / take-profit hits.
- **Trade**: Simple long/short trade object with stop-loss and target.
- **SparseTable**: O(1) range minimum / maximum queries.

## Notes

- Differential Evolution settings (`maxiter=5, popsize=2`) are intentionally light for fast iteration. Increase them for serious runs.
- CSV files are ignored by git.
- Use `template.ipynb` to get started.

## License

MIT
