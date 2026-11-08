"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, display, fill, high, hl2, input, location, low,
    na, open, plot, plotcandle, plotshape, script, shape, size, ta
)
from pynecore.types import NA, Series

grp: str = "MA Shift Oscillator"


@script.indicator("Moving Average Shift [ChartPrime]", "MA Shift [ChartPrime]", overlay=False)
def main(
    type_ma=input.string("SMA", "Type", options=("SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"), group="MA"),
    length=input.int(40, "Length", inline="ma", group="MA"),
    source: Series[float] = input.source(hl2, "", inline="ma", group="MA"),
    osc_len=input.int(15, "Length", group=grp, inline="osc"),
    osc_threshold=input.float(0.5, "", step=0.1, group=grp, inline="osc"),
    osc_cross=input.bool(True, "⯁", group=grp, inline="osc"),
    osc_col_up1=input.color(color.new('#1DD1C2'), "", inline="c", group="color"),
    osc_col_up2=input.color(color.new('#17A297'), "", inline="c", group="color"),
    osc_col_dn1=input.color(color.yellow, "", inline="c", group="color"),
    osc_col_dn2=input.color(color.orange, "", inline="c", group="color")
):
    def ma(source, length, MAtype):
        __block_result__ = na
        __switch__ = MAtype
        if __switch__ == "SMA":
            __block_result__ = ta.sma(source, length)
        elif __switch__ == "EMA":
            __block_result__ = ta.ema(source, length)
        elif __switch__ == "SMMA (RMA)":
            __block_result__ = ta.rma(source, length)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(source, length)
        elif __switch__ == "VWMA":
            __block_result__ = ta.vwma(source, length)
        return __block_result__

    MA = ma(source, length, type_ma)
    color__ren__ = osc_col_up2 if source >= MA else osc_col_dn2

    diff = source - MA
    perc_r = ta.percentile_linear_interpolation(diff, 1000, 99)

    osc: Series = ta.hma(ta.change(diff / perc_r, osc_len), 10)
    osc_col = (osc_col_up1 if osc > osc[1] else osc_col_up2) if osc > 0 else osc_col_dn1 if osc < osc[1] else osc_col_dn2

    plot(MA, 'SMA-based MA', color=color__ren__, force_overlay=True, linewidth=2)
    plot(MA, 'SMA-based MA', color=color.new(color__ren__, 80), force_overlay=True, linewidth=7)

    barcolor(color__ren__)
    plotcandle(open, high, low, close, title='Title', color=color__ren__, wickcolor=color__ren__, bordercolor=color__ren__, force_overlay=True)

    top = osc_threshold
    bot = -top
    plot(osc, style=plot.style_columns, color=osc_col)
    p1 = plot(top, display=display.none, editable=False)
    p0 = plot(0, display=display.none, editable=False)
    p2 = plot(bot, display=display.none, editable=False)

    fill(p1, p0, top, 0, color.new(osc_col, 70), color.new(osc_col, 100))
    fill(p2, p0, 0, bot, color.new(osc_col, 100), color.new(osc_col, 80))

    sig_up: bool = ta.crossover(osc, osc[2]) and osc < -osc_threshold if osc_cross else NA(bool)
    sig_dn: bool = ta.crossunder(osc, osc[2]) and osc > osc_threshold if osc_cross else NA(bool)

    plotshape(sig_up, 'Up', shape.diamond, location.belowbar, osc_col_up1, force_overlay=True, size=size.tiny)
    plotshape(sig_dn, 'Dn', shape.diamond, location.abovebar, osc_col_dn1, force_overlay=True, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
