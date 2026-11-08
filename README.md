<p align="center">
  <img src="./assets/images/logo.png" height="115px" alt="pynecore-strategies" />
</p>

<p align="center">
  <strong>TradingView community strategies, running offline in Python</strong><br>
  449 strategies, 471 indicators and 85 libraries compiled from Pine Script to PyneCore.<br>
  No TradingView account, no browser, no chart.
</p>

## Why

Public trading strategies exist mostly as Pine Script, so their backtests run only inside a
TradingView chart. This repository collects the open-source Pine strategies and indicators that
PyneSys verified against TradingView and compiles them into [PyneCore](https://pynecore.org)
scripts. PyneCore executes Pine-style code bar by bar in Python, with the same series history,
`na` handling, broker emulator and drawing objects, so every strategy becomes a command that
backtests on any candles you have and writes its trades and statistics to CSV files.

The scripts can be backtested on any market, including exchanges that TradingView does not list,
batch-tested from Python, or fed to a feature pipeline or an LLM agent. The repository is part of
the open-source tooling of [TheOneTrade](https://theonetrade.github.io).

## What is inside

| | Bit-exact | Verified | Total | Compiled to |
|---|---|---|---|---|
| Strategies | 384 | 65 | 449 | `scripts/strategy_<name>.py` |
| Indicators | 458 | 13 | 471 | `scripts/indicator_<name>.py` |
| Pine libraries they import | | | 85 | `scripts/lib/<Publisher>/<Name>/v<N>.py` |

The sources come from [Pyne in the Wild](https://wild.pynesys.io/#scripts), PyneSys' verification
report on the 1,000 most-liked open-source Pine scripts on TradingView. Two of its categories were
taken:

- **Bit-exact**: on every compared bar PyneCore produced the same IEEE-754 double as TradingView.
- **Verified**: the output matched TradingView bar by bar and trade by trade within the published
  tolerance band.

Each original Pine source is kept in [`assets/`](assets/) next to its compiled script, byte for
byte as TradingView's *Source code* tab serves it. 25 publications listed in the report had been
removed from TradingView by their authors before the download (22 strategies, 3 indicators);
they are listed in `assets/<type>/<category>/unavailable.txt`. The download and verification
procedure is described in [`assets/README.md`](assets/README.md).

The corpus mixes Pine versions: 295 sources are v4, 327 v5, 293 v6 and 5 older. PyneComp converts
v4 and v5 to v6 before compiling and keeps the settings those versions defaulted to (for example
`margin_long=0` and `close_by_id=True` in the strategy decorator).

## Finding a script

A file name is the TradingView title in snake_case followed by the 8-character TradingView script id:

```
assets/strategy/verified/macd_reloaded_strategy_VO6DY8s1.pine     original Pine Script
scripts/strategy_macd_reloaded_strategy_VO6DY8s1.py               compiled PyneCore strategy
https://www.tradingview.com/script/VO6DY8s1/                      the publication
```

Libraries keep the path of their Pine import, with `-` in the publisher replaced by `_`:
`import Trading-IQ/ICTlibrary/1` is `assets/lib/Trading-IQ/ICTlibrary/v1.pine` and compiles to
`scripts/lib/Trading_IQ/ICTlibrary/v1.py`. [`assets/lib/index.tsv`](assets/lib/index.tsv) records
where each library was found on TradingView.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/theonetrade/pynecore-strategies.git
cd pynecore-strategies
uv sync --python 3.13          # installs pynesys-pynecore[cli,ccxt] into .venv
```

Download candles once. The `.ohlcv` file in `data/` is a cache: later downloads append only new
bars, and every run reads the file offline.

```bash
uv run pyne data download ccxt:GATE:BTC/USDT@60 --from 2025-09-25
```

Any exchange supported by [CCXT](https://github.com/ccxt/ccxt) works: `ccxt:BINANCE:BTC/USDT@60`,
`ccxt:BYBIT:BTC/USDT:USDT@1D`, and so on. Gate.io serves only the most recent 10,000 candles per
timeframe, which is about one week of 1-minute candles and 14 months of 1-hour candles. A download
that ends at "now" also stores the candle that is still forming.

Backtest a strategy or run an indicator:

```bash
export PYNE_NO_LOGO=1
uv run pyne run strategy_macd_reloaded_strategy_VO6DY8s1 ccxt_GATE_BTC_USDT_60
uv run pyne run indicator_supertrend_r6dAP7yi ccxt_GATE_BTC_USDT_60
uv run pyne run strategy_macd_reloaded_strategy_VO6DY8s1 ccxt_GATE_BTC_USDT_60 --from 2026-08-07 --to 2026-11-07
```

### Higher and lower timeframes

Scripts that call `request.security` need a data file for every timeframe they request. List what
a script needs, download it and pass it with `--security`:

```bash
uv run pyne run strategy_ict_master_suite_trading_iq_ABYnIcdl ccxt_GATE_BTC_USDT_60 --list-data
uv run pyne data download ccxt:GATE:BTC/USDT@1D --from 2021-01-01
uv run pyne run strategy_ict_master_suite_trading_iq_ABYnIcdl ccxt_GATE_BTC_USDT_60 --security "1D=ccxt_GATE_BTC_USDT_1D"
```

A key is a timeframe (`1D`, `D`, `60`, `1W`) or a symbol, and the option can be repeated.

### Libraries

Scripts that import a Pine library load it from `scripts/lib/`, which `pyne run` puts on the import
path. 55 scripts use libraries (26 strategies and 29 indicators). No extra step is needed: the
compiled libraries are in the repository.

## Outputs

| File | Contents |
|------|----------|
| `output/<script>_trade.csv` | Every entry and exit: time, price, contracts, profit, run-up and drawdown |
| `output/<script>_strat.csv` | Strategy statistics: net profit, drawdown, profit factor, win rate, long/short split |
| `output/<script>.csv` | One row per bar: time, OHLCV and the value of every `plot()` |
| `output/<script>_viz.ndjson` | With `--viz`: plot styles and drawing objects |
| `scripts/<script>.toml` | Every input and strategy setting. Uncomment `value = ...` to change one without editing code |

Strategy settings such as `commission_value`, `initial_capital` or `default_qty_value` can be
overridden in the `.toml` file in the same way as inputs. The scripts keep the costs and position
sizes their authors set, which differ from script to script.

## Test run

Software: PyneCore 6.12.1, Python 3.13, every script compiled by PyneComp v6.0.79.

**Compilation.** All 1,005 sources compiled, and every compiled file passed a Python syntax check.

**Strategies.** Each strategy was backtested on Gate.io BTC/USDT from 2026-08-07 to 2026-11-07
(8,833 bars at 15m, 2,209 at 1h, 553 at 4h, no gaps), with daily and weekly files supplied for
`request.security`.

| Result | Strategies |
|--------|------------|
| Completed on all three timeframes | 418 |
| Completed on some timeframes | 1 |
| Need data that Gate.io cannot provide for the period: 1, 3 or 5-minute candles | 18 |
| Need other timeframes that were not downloaded (monthly, 25m, 30m, 2h, 6h, 8h, 12h) | 10 |
| Stop with `IndexError` inside the script | 2 |

**Libraries.** 23 of the 26 strategies that import libraries completed; the other three request
5-minute or monthly data.

**Indicators.** All 471 compiled; they were not run in bulk.

The PyneSys report compared these scripts with TradingView. This repository did not repeat that
comparison, and the backtests above were run only to check that the scripts execute.

## Recompiling from Pine Script

`pyne compile` sends a source to the PyneSys cloud compiler. It needs an API key from
[pynesys.io](https://pynesys.io), passed with `--api-key`, set in `PYNESYS_API_KEY`, or stored in
`config/api.toml`. Git ignores the `config/` folder, so the key is not committed.

```bash
uv run pyne compile assets/strategy/verified/macd_reloaded_strategy_VO6DY8s1.pine -o scripts/strategy_macd_reloaded_strategy_VO6DY8s1.py --force
uv run pyne compile            # without a script: shows your API usage and key expiry
```

[`tools/compile_assets.py`](tools/compile_assets.py) compiles the whole of `assets/` into
`scripts/` with the naming above. The API allows a fixed number of compilations per hour and per
day; the tool stops when the quota runs out and continues from the same place on the next run.
Progress is kept in [`assets/compile_state.json`](assets/compile_state.json), keyed by the SHA-256
of each source, so only new or edited sources are compiled again.

```bash
uv run python tools/compile_assets.py --status     # progress and quota, uses no quota
uv run python tools/compile_assets.py              # compile until done or out of quota
```

## Layout

```
assets/
  strategy/<category>/     original Pine sources of the strategies, links.txt, unavailable.txt
  indicator/<category>/    original Pine sources of the indicators
  lib/                     Pine libraries the scripts import, index.tsv
  compile_state.json       compilation progress
  images/logo.png
scripts/
  strategy_*.py            compiled strategies and their input .toml files
  indicator_*.py           compiled indicators
  lib/                     compiled libraries
  constructor.py           a strategy whose regime filter, entry and exit are chosen by inputs
tools/compile_assets.py    batch compiler for assets/
data/                      candle cache (.ohlcv ignored by git, .toml symbol info kept)
config/                    api.toml and plugin settings (ignored by git: may hold keys)
output/                    run results (ignored by git)
.pyne                      PyneCore workdir marker
pyproject.toml             uv project depending on pynesys-pynecore[cli,ccxt]
```

## Working with AI agents

The project was built with [pynecore-skills](https://github.com/theonetrade/pynecore-skills), agent
skills that teach Claude Code, Cursor and Codex the PyneCore language, the `pyne` CLI and the data
workflow:

```bash
npx skills add theonetrade/pynecore-skills
```

## Disclaimer

These are research and analysis tools, not trading advice. Past performance does not predict
future returns.
