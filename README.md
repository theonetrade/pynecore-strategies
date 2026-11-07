# pynecore-strategies

Trading strategies and indicators written as [PyneCore](https://pynecore.org) (Pyne) scripts.

## Layout

```
.pyne                 workdir marker
scripts/              Pyne scripts (*.py) and their generated settings (*.toml)
scripts/lib/          shared Pyne libraries
data/                 OHLCV data (*.ohlcv, ignored by git) and symbol info (*.toml)
config/               plugin and API config (keys are git-ignored)
output/               backtest results: <script>.csv, <script>_strat.csv, <script>_trade.csv
assets/               original Pine sources from the Pyne in the Wild corpus (strategy/, indicator/), see assets/README.md
```

## Setup

Requires [uv](https://docs.astral.sh/uv/). Python 3.13 and PyneCore are installed into `.venv`:

```bash
uv sync
```

## Run

```bash
# demo indicator on the bundled synthetic data
PYNE_NO_LOGO=1 .venv/bin/pyne run demo demo

# EMA crossover strategy with ATR stop/target
PYNE_NO_LOGO=1 .venv/bin/pyne run ema_cross demo

# recreate demo data if data/demo.ohlcv is missing
.venv/bin/pyne --recreate-demo plugin list

# download real candles
.venv/bin/pyne data download ccxt:BYBIT:BTC/USDT:USDT@1D
```

Inputs and strategy settings live in `scripts/<name>.toml`, written on the first run.
