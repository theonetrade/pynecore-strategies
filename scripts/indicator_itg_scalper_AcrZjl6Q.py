"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, high, input, label,
    location, math, na, nz, plot, plotshape, request, script, shape, size, string, syminfo, ta,
    ticker, timeframe, yloc
)
from pynecore.types import Label, Persistent, Series


@script.indicator(shorttitle='ITG_Scalper', title='ITG Scalper Buy/Sell [Complector]', overlay=True, na_bool=True)
def main(
    shc=input(True, title='Plot TEMA?'),
    cc=input(True, title='Green/redshift on/off?'),
    showtext=input(True, title='Show buy/sell?'),
    uselabel=input(True, title='Use labels? (max 50)'),
    showperc=input(False, title='Show % change since last buy/sell'),
    nfilter=input(True, title='Noise filter on/off?'),
    useCurrentRes=input(True, title='Use Current Chart Resolution for filter?'),
    resCustom=input.timeframe(title='Use Different Timeframe for filter? Uncheck Box Above', defval='60'),
    len=input(14, title='TEMA period'),
    FfastLength=input.int(12, minval=1, title='Filter fast length'),
    FslowLength=input.int(26, minval=1, title='Filter slow length'),
    FsignalLength=input.int(9, minval=1, title='Filter signal length')
):
    t_id = ticker.new(syminfo.prefix, syminfo.ticker)
    realC = request.security(t_id, timeframe.period, close)
    buyprice: Series[float] = 0.0
    buyprice = nz(buyprice[1])
    sellprice: Series[float] = 0.0
    sellprice = nz(sellprice[1])
    last_tran: Series[bool] = False
    last_tran = nz(last_tran[1])
    def truncate(number, decimals):
        factor = math.pow(10, decimals)
        return cast_int(number * factor) / factor

    ema1 = ta.ema(realC, len)
    ema2 = ta.ema(ema1, len)
    ema3 = ta.ema(ema2, len)
    avg = 3 * (ema1 - ema2) + ema3
    out = avg
    out1: Series = request.security(t_id, timeframe.period, out)
    ma_up = out1 >= out1[1]
    ma_down = out1 < out1[1]
    col = (color.lime if ma_up else color.red if ma_down else color.lime) if cc else color.aqua
    t_UP = ma_up
    t_DOWN = ma_down
    t_NON = t_UP == t_DOWN
    Fsource = close
    macd_colorChange: bool = True
    Fres = timeframe.period if useCurrentRes else resCustom
    FfastMA = ta.ema(Fsource, FfastLength)
    FslowMA = ta.ema(Fsource, FslowLength)
    Fmacd = FfastMA - FslowMA
    Fsignal = ta.sma(Fmacd, FsignalLength)
    outMacD = request.security(syminfo.tickerid, Fres, Fmacd)
    outSignal = request.security(syminfo.tickerid, Fres, Fsignal)
    Fbuy = outMacD >= outSignal or not nfilter
    Fsell = outMacD < outSignal or not nfilter
    plot(out1, title='TEMA', style=plot.style_line, linewidth=2, color=col)
    long = t_UP and (not last_tran) and (not t_NON) and Fbuy and barstate.isconfirmed
    short = t_DOWN and last_tran and (not t_NON) and Fsell and barstate.isconfirmed
    if long:
        buyprice = realC
        last_tran = True
    if short:
        sellprice = realC
        last_tran = False
    PercVal = 100 * (realC - buyprice) / buyprice if last_tran else 100 * (realC - sellprice) / sellprice
    PercCol = color.lime if PercVal >= 0 else color.orange
    if showperc:
        percLab: Persistent[Label] = na(Label)
        label.delete(percLab)
        percLab = label.new(x=bar_index, y=high, yloc=yloc.abovebar, color=color.black, textcolor=PercCol, style=label.style_none)
        label.set_text(id=percLab, text=string.tostring(truncate(PercVal, 2)) + ' %')
    goodlong = long and buyprice <= sellprice
    goodshort = short and sellprice > buyprice
    txtlight_b = color.lime
    txtlight_s = color.red if goodshort else color.yellow
    buytxt = string.tostring(truncate(buyprice, 8))
    selltxt = string.tostring(truncate(sellprice, 8))
    alertcondition(long, title='Buy alert', message='Buy alert')
    alertcondition(short, title='Sell alert', message='Sell alert')
    if uselabel and long and showtext:
        label.new(bar_index, high, buytxt, yloc=yloc.belowbar, color=txtlight_b, textcolor=color.white, style=label.style_triangleup, size=size.small)
    if uselabel and short and showtext:
        label.new(bar_index, high, selltxt, yloc=yloc.abovebar, color=txtlight_s, textcolor=color.white, style=label.style_triangledown, size=size.small)
    plotshape(not uselabel and long and showtext, title='Buy alert', color=color.new(txtlight_b, 0), style=shape.triangleup, size=size.small, location=location.belowbar)
    plotshape(not uselabel and short and showtext, title='Sell alert', color=txtlight_s, style=shape.triangledown, size=size.small, location=location.abovebar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
