"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, barcolor, barstate, close, color, display, input, location, math,
    nz, plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title='UT Bot v2 — ATR Trailing Stop', shorttitle="UT Bot v2", overlay=True)
def main(
    mult=input.float(1, title='Multipier', minval=0.1, step=0.1, tooltip='Controls the distance of the trailing stop. Higher values create wider stops and fewer trend flips.', group="Config"),
    atr_len=input.int(10, title='ATR Period', minval=1, tooltip='Number of bars used to calculate ATR volatility.', group="Config"),
    source: Series[float] = input.source(close, title="Source", tooltip='Price source used for trailing stop calculations.', group="Config"),
    use_date_filter=input.bool(True, "Use Backtest Date Range", group="Backtesting Range"),
    start_time=input.time(timestamp('2020-01-01 00:00'), "Start Date", group="Backtesting Range"),
    end_time=input.time(timestamp('2030-01-01 00:00'), "End Date", group="Backtesting Range"),
    show_signals=input.bool(True, 'Show Buy/Sell Signals', group="Display"),
    color_bars=input.bool(False, 'Color Bars by Trend', group="Display"),
    show_tsl=input.bool(True, 'Show Trailing Stop Line', group="Display")
):
    atr = ta.atr(atr_len)
    sl_value = mult * atr

    tsl_price: Series[float] = 0.0
    tsl_price = math.max(nz(tsl_price[1]), source - sl_value) if source > tsl_price[1] and source[1] > tsl_price[1] else math.min(nz(tsl_price[1]), source + sl_value) if source < tsl_price[1] and source[1] < tsl_price[1] else source - sl_value if source > tsl_price[1] else source + sl_value

    in_date_range = not use_date_filter or (time >= start_time and time <= end_time)

    buy = ta.crossover(source, tsl_price) and barstate.isconfirmed
    sell = ta.crossover(tsl_price, source) and barstate.isconfirmed

    bull_color = color.new(color.green, 0)
    bear_color = color.new(color.red, 0)

    tsl_color: Series = bull_color
    tsl_color = bear_color if sell else bull_color if buy else tsl_color[1]

    barcolor(tsl_color, display=display.all if color_bars else display.none)

    plot(tsl_price, color=tsl_color, linewidth=2, display=display.all if show_tsl else display.none)

    plotshape(buy, title='Buy', text='Buy', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all if show_signals else display.none)

    plotshape(sell, title='Sell', text='Sell', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny, display=display.all if show_signals else display.none)

    if buy:
        alert('UT Bot Buy', alert.freq_once_per_bar_close)

    if sell:
        alert('UT Bot Sell', alert.freq_once_per_bar_close)

    if buy and in_date_range:
        strategy.entry('Long', strategy.long)

    if sell and in_date_range:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
