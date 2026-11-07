"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, hl2, input, location, math, na, nz, plot, plotshape,
    script, shape, strategy, ta
)
from pynecore.types import Series


@script.strategy('Pivot Point SuperTrend [Backtest]', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    prd=input.int(defval=2, title='Pivot Point Period', minval=1, maxval=50),
    Factor=input.float(defval=3, title='ATR Factor', minval=1, step=0.1),
    Pd=input.int(defval=10, title='ATR Period', minval=1),
    minrateu=input.float(defval=1.0, title='Min profit Rate if Center Line Used', minval=0),
    usecenter=input(defval=False, title='Use Center Line to Close Entry for 50%'),
    showpivot=input(defval=False, title='Show Pivot Points'),
    showcl=input(defval=False, title='Show PP Center Line'),
    onlylong=input(defval=False, title='Enter Only Long Position')
):
    minrate: float = minrateu / 100
    ph: float = na(float)
    pl: float = na(float)
    ph = ta.pivothigh(prd, prd)
    pl = ta.pivotlow(prd, prd)
    plotshape(cast_bool(ph) and showpivot, text='H', style=shape.labeldown, color=na, textcolor=color.new(color.red, 0), location=location.abovebar, offset=-prd)
    plotshape(cast_bool(pl) and showpivot, text='L', style=shape.labeldown, color=na, textcolor=color.new(color.lime, 0), location=location.belowbar, offset=-prd)
    center: Series[float] = na(float)
    center = center[1]
    lastpp: float = ph if cast_bool(ph) else pl if cast_bool(pl) else na
    if cast_bool(lastpp):
        if na(center):
            center = lastpp
        else:
            center = (center * 2 + lastpp) / 3
    Up = center - Factor * ta.atr(Pd)
    Dn = center + Factor * ta.atr(Pd)
    TUp: Series[float] = na(float)
    TDown: Series[float] = na(float)
    Trend: Series[int] = 0
    TUp = math.max(Up, TUp[1]) if close[1] > TUp[1] else Up
    TDown = math.min(Dn, TDown[1]) if close[1] < TDown[1] else Dn
    Trend = 1 if close > TDown[1] else -1 if close < TUp[1] else nz(Trend[1], 1)
    Trailingsl = TUp if Trend == 1 else TDown
    linecolor = color.lime if Trend == 1 and nz(Trend[1]) == 1 else color.red if Trend == -1 and nz(Trend[1]) == -1 else na
    plot(Trailingsl, color=linecolor, linewidth=2, title='PP SuperTrend')
    plot(center if showcl else na, color=(color.blue if center < hl2 else color.red) if showcl else na)
    bsignal = Trend == 1 and Trend[1] == -1
    ssignal = Trend == -1 and Trend[1] == 1
    halfexited: Series[bool] = False
    halfexited = nz(halfexited[1], False)
    if cast_bool(ta.change(Trend)):
        strategy.close_all()
    if bsignal:
        strategy.entry('Buy', strategy.long, comment='Buy')
    if ssignal and (not onlylong):
        strategy.entry('Sell', strategy.short, comment='Sell')
    cpsize = ta.change(strategy.position_size)
    if cast_bool(ta.change(strategy.position_size)):
        if cpsize > 0 and strategy.position_size > 0 or (cpsize < 0 and strategy.position_size < 0):
            halfexited = False
    if strategy.position_size > 0 and center > hl2 and usecenter and (not halfexited) and (close > strategy.position_avg_price * (1 + minrate)):
        strategy.close('Buy', qty_percent=50, comment='close buy for 50%')
        halfexited = True
    if strategy.position_size < 0 and center < hl2 and usecenter and (not halfexited) and (close < strategy.position_avg_price * (1 + minrate)):
        strategy.close('Sell', qty_percent=50, comment='close sell for 50%')
        halfexited = True


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
