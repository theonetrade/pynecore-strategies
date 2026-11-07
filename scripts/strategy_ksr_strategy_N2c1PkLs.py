"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, close, color, high, input, label, location, low, na,
    open, plot, plotshape, request, script, shape, size, strategy, string, syminfo, ta, ticker,
    yloc
)


@script.strategy('KSR Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    par1=input(10),
    par2=input(20),
    ma1_len=input.int(title='MA1', defval=8, minval=1, maxval=100, step=1),
    ma2_len=input.int(title='MA2', defval=12, minval=1, maxval=100, step=1),
    tim1=input('D', 'Short Time'),
    tim2=input('W', 'Long Time'),
    ema_p=input.int(title='EMA Period', defval=16, minval=1, maxval=100, step=1)
):
    ema1 = ta.ema(close, par1)
    ema2 = ta.ema(close, par2)
    buy = ema1 > ema2
    sell = ema2 < ema1
    iff_1 = color.blue if sell else color.red
    mycolor = color.green if buy else iff_1
    barcolor(color=mycolor)
    ema100 = ta.ema(close, 100)
    ibuy = ta.crossover(ema1, ema2)
    iSell = ta.crossunder(ema1, ema2)
    varp = string.tostring(close[1])
    plotshape(ibuy, 'Up Arrow', shape.triangleup, location.belowbar, color.new(color.green, 0), 0, 'Buy', color.green, True, size.tiny)
    plotshape(iSell, 'Down Arrow', shape.triangledown, location.abovebar, color.new(color.red, 0), 0, 'Sell', color.red, True, size.tiny)
    crossed = ta.crossover(ta.ema(close, par1), ta.ema(close, par2))
    if crossed:
        label.new(bar_index, na, string.tostring(close), color=color.green, textcolor=color.white, style=label.style_label_up, yloc=yloc.belowbar)
    crossed2 = ta.crossunder(ta.ema(close, par1), ta.ema(close, par2))
    if crossed2:
        label.new(bar_index, na, string.tostring(close), color=color.red, textcolor=color.white, style=label.style_label_down, yloc=yloc.abovebar)
    plot(ta.ema(close, par1), 'EMA Short', color=color.new(color.white, 0))
    plot(ta.ema(close, par2), 'EMA Long', color=color.new(color.orange, 0))
    longCondition = ta.crossover(ta.ema(close, par1), ta.ema(close, par2))
    if longCondition:
        strategy.entry('My Long Entry Id', strategy.long)
    shortCondition = ta.crossunder(ta.ema(close, par1), ta.ema(close, par2))
    if shortCondition:
        strategy.entry('My Short Entry Id', strategy.short)
    o = ta.ema(open, ma1_len)
    c = ta.ema(close, ma1_len)
    h = ta.ema(high, ma1_len)
    l = ta.ema(low, ma1_len)
    refma = ta.ema(close, ema_p)
    plot(refma, title='EMA', linewidth=1, color=color.orange if close < refma else color.blue)
    ha_t = ticker.heikinashi(syminfo.tickerid)
    ha_o = request.security(ha_t, tim2, o)
    ha_c = request.security(ha_t, tim2, c)
    ha_h = request.security(ha_t, tim2, h)
    ha_l = request.security(ha_t, tim2, l)
    o2 = ta.ema(ha_o, ma2_len)
    c2 = ta.ema(ha_c, ma2_len)
    h2 = ta.ema(ha_h, ma2_len)
    l2 = ta.ema(ha_l, ma2_len)
    ha_col = color.red if ha_c > ha_o else color.green
    plotshape(True, style=shape.circle, color=color.green if ha_c > ha_o else color.red, location=location.bottom)
    ha_t1 = ticker.heikinashi(syminfo.tickerid)
    ha_o1 = request.security(ha_t1, tim1, o)
    ha_c1 = request.security(ha_t1, tim1, c)
    ha_h1 = request.security(ha_t1, tim1, h)
    ha_l1 = request.security(ha_t1, tim1, l)
    o3 = ta.ema(ha_o1, ma2_len)
    c3 = ta.ema(ha_c1, ma2_len)
    h3 = ta.ema(ha_h1, ma2_len)
    l3 = ta.ema(ha_l1, ma2_len)
    ha_col1 = color.red if ha_c1 > ha_o1 else color.green
    plotshape(True, style=shape.circle, color=color.green if ha_c1 > ha_o1 else color.red, location=location.top)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
