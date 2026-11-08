"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    close, color, display, fill, high, input, low, math, open, plot,
    plotcandle, script, ta
)
from pynecore.types import Persistent, Series
import lib.TradingView.ta.v14 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@script.indicator("Different RSI", overlay=False)
def main(
    src: Series[float] = input.source(close, "Source", group="Different RSI"),
    len=input.int(45, "Lookback", minval=2, group="Different RSI"),
    sml=input.int(12, "Smoothing", minval=2, group="Different RSI")
):
    g: float = 0.0
    l: float = 0.0
    for i in pine_range(1, len - 1):
        g += math.pow(math.max(0, src - src[i]), 2)
        l += math.pow(math.abs(math.min(0, src - src[i])), 2)

    rsi = 0 if g == 0 else 100 if l == 0 else 100 - 100 / (1 + math.sqrt(g) / math.sqrt(l))
    ma = ta__ren__.ema(rsi, sml)

    trend: Persistent[int] = 0
    if rsi > 50 and rsi > ma:
        trend = 1
    if rsi < 50 and rsi < ma:
        trend = -1

    col: Persistent = color.rgb(72, 72, 72)
    colT: Persistent = color.rgb(72, 72, 72, 50)
    if trend == 1:
        col = color.rgb(0, 255, 187)
        colT = color.rgb(0, 255, 187, 50)
    if trend == -1:
        col = color.rgb(255, 0, 157)
        colT = color.rgb(255, 0, 157, 50)

    n = plot(50, title='Middle', color=color.rgb(71, 70, 70), display=display.pane, linewidth=3)
    obp = plot(80, title='OB Treshhold', color=color.rgb(0, 255, 187), display=display.pane, linewidth=3)
    osp = plot(20, title='OS Treshhold', color=color.rgb(255, 0, 157), display=display.pane, linewidth=3)

    fill(n, obp, color.rgb(0, 195, 237, 85))
    fill(n, osp, color.rgb(255, 0, 157, 85))

    plotcandle(open, high, low, close, bordercolor=col, color=col, force_overlay=True, display=display.pane)

    rsip = plot(rsi, 'Different RSI | MisinkoMaster', color=col, linewidth=2)
    plot(ma, 'MA', color=color.yellow, linewidth=1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)