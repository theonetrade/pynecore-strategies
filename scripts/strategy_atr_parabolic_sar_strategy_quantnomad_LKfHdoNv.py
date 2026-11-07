"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, high, input, low, math, na, nz, open, plot,
    script, strategy, ta
)
from pynecore.types import Series


@script.strategy(title='ATR Parabolic SAR Strategy [QuantNomad]', shorttitle='ATR PSAR Strategy [QN]', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    atr_length=input(14),
    start=input(0.02),
    increment=input(0.02),
    maximum=input(0.2),
    entry_bars=input(1, title='Entry on Nth trend bar')
):
    atr = ta.atr(atr_length)
    atr = ta.tr if na(atr) else atr
    psar: Series[float] = 0.0
    af: Series[float] = 0.0
    trend_dir: Series[int] = 0
    ep: Series[float] = 0.0
    trend_bars: Series[int] = 0
    sar_long_to_short = trend_dir[1] == 1 and close <= psar[1]
    sar_short_to_long = trend_dir[1] == -1 and close >= psar[1]
    trend_change = barstate.isfirst[1] or sar_long_to_short or sar_short_to_long
    trend_dir = 1 if barstate.isfirst[1] and close[1] > open[1] else -1 if barstate.isfirst[1] and close[1] <= open[1] else -1 if sar_long_to_short else 1 if sar_short_to_long else nz(trend_dir[1])
    trend_bars = -1 if sar_long_to_short else 1 if sar_short_to_long else nz(trend_bars[1]) + 1 if trend_dir == 1 else nz(trend_bars[1]) - 1 if trend_dir == -1 else nz(trend_bars[1])
    af = start if trend_change else math.min(maximum, af[1] + increment) if trend_dir == 1 and high > ep[1] or (trend_dir == -1 and low < ep[1]) else af[1]
    ep = high if trend_change and trend_dir == 1 else low if trend_change and trend_dir == -1 else math.max(ep[1], high) if trend_dir == 1 else math.min(ep[1], low)
    psar = low[1] if barstate.isfirst[1] and close[1] > open[1] else high[1] if barstate.isfirst[1] and close[1] <= open[1] else ep[1] if trend_change else psar[1] + af * atr if trend_dir == 1 else psar[1] - af * atr
    plot(psar, style=plot.style_cross, color=color.green if trend_dir == 1 else color.red, linewidth=2)
    if trend_bars == entry_bars:
        strategy.entry('Long', strategy.long)
    if trend_bars == -entry_bars:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
