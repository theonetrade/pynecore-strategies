"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    chart, close, color, currency, display, fill, hline, input, location,
    math, na, nz, plot, plotshape, script, shape, strategy, ta
)
from pynecore.types import Color, Persistent, Series


@udt
class bar:
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)


@udt
class supertrend_:
    s: float = na(float)
    d: int = na(int)


g1: str = 'ENtry/Exit: SuperTrend Settings'
gu: str = 'UI Options'


@script.strategy('BBTrend w SuperTrend decision - Strategy [presentTrading]', overlay=False, precision=3, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirection=input.string('Long', 'Trading Direction', options=('Both', 'Long', 'Short')),
    shortLengthInput=input.int(20, 'Short BB Length', minval=1),
    longLengthInput=input.int(50, 'Long BB Length', minval=1),
    stdDevMultInput=input.float(2.0, 'StdDev', minval=0.001),
    TPSLCondition=input.string('None', 'TPSL Condition', options=('TP', 'SL', 'Both', 'None')),
    takeProfitPerc=input.float(30.0, title='Take Profit (%)'),
    stopLossPerc=input.float(20.0, title='Stop Loss (%)'),
    len=input.int(10, 'Length', inline='1', group=g1),
    mlt=input.float(7.0, 'Factor', minval=1, maxval=20, step=0.5, inline='1', group=g1),
    clbl=input.bool(True, 'Contrarian Signals', group=gu),
    colu=input.color(color.new('#008CFF'), 'Bull Color', group=gu),
    cold=input.color(color.new('#FF4800'), 'Bear Color', group=gu)
):
    shortMiddle, shortUpper, shortLower = ta.bb(close, shortLengthInput, stdDevMultInput)
    longMiddle, longUpper, longLower = ta.bb(close, longLengthInput, stdDevMultInput)
    BBTrend: Series = (math.abs(shortLower - longLower) - math.abs(shortUpper - longUpper)) / shortMiddle * 100
    posColorStrong = color.new(color.new('#089981'), 25)
    negColorStrong = color.new(color.new('#F23645'), 25)
    posColorWeak = color.new(color.new('#089981'), 50)
    negColorWeak = color.new(color.new('#F23645'), 50)
    __block_result__ = na
    if BBTrend > 0 and BBTrend >= BBTrend[1]:
        __block_result__ = posColorStrong
    elif BBTrend > 0 and BBTrend < BBTrend[1]:
        __block_result__ = posColorWeak
    elif BBTrend < 0 and BBTrend > BBTrend[1]:
        __block_result__ = negColorWeak
    elif BBTrend < 0 and BBTrend <= BBTrend[1]:
        __block_result__ = negColorStrong
    else:
        __block_result__ = posColorWeak
    histColor = __block_result__
    plot(BBTrend, 'BBTrend', style=plot.style_columns, color=histColor)
    hline(0, 'Zero line')
    @method
    def src(b: bar, src__00000028__: str):
        __block_result_1__ = na
        __switch__ = src__00000028__
        if __switch__ == 'oc2':
            __block_result_1__ = math.avg(b.o, b.c)
        elif __switch__ == 'hl2':
            __block_result_1__ = math.avg(b.h, b.l)
        elif __switch__ == 'hlc3':
            __block_result_1__ = math.avg(b.h, b.l, b.c)
        elif __switch__ == 'ohlc4':
            __block_result_1__ = math.avg(b.o, b.h, b.l, b.c)
        elif __switch__ == 'hlcc4':
            __block_result_1__ = math.avg(b.h, b.l, b.c, b.c)
        x: float = __block_result_1__
        return x

    @method
    def atr(b: bar, len: int):
        field_0: Series[float] = b.h
        field_1: Series[float] = b.c
        field_2: Series[float] = b.c
        tr: float = b.h - b.l if na(field_0[1]) else math.max(math.max(b.h - b.l, math.abs(b.h - field_1[1])), math.abs(b.l - field_2[1]))
        return tr if len == 1 else ta.rma(tr, len)

    @method
    def st(b: bar, factor: float, len: int):
        atr__0000004d__: Series[float] = atr(b, len)
        up: Series[float] = src(b, 'hl2') + factor * atr__0000004d__
        field_3: Series[float] = b.c
        up = up if up < nz(up[1]) or field_3[1] > nz(up[1]) else nz(up[1])
        dn: Series[float] = src(b, 'hl2') - factor * atr__0000004d__
        field_4: Series[float] = b.c
        dn = dn if dn > nz(dn[1]) or field_4[1] < nz(dn[1]) else nz(dn[1])
        st__0000004d__: Series[float] = na(float)
        dir: int = na(int)
        __block_result_2__ = na
        if na(atr__0000004d__[1]):
            __block_result_2__ = 1
        elif st__0000004d__[1] == nz(up[1]):
            dir = -1 if b.c > up else 1
            __block_result_2__ = dir
        else:
            dir = 1 if b.c < dn else -1
            __block_result_2__ = dir
        dir = __block_result_2__
        st__0000004d__ = dn if dir == -1 else up
        return supertrend_(st__0000004d__, dir)

    tp: Persistent[str] = 'Choose an indicator source of which to base the SuperTrend on.'
    src__global__: Series = BBTrend
    b: bar = bar(nz(src__global__[1]), math.max(nz(src__global__[1]), src__global__), math.min(nz(src__global__[1]), src__global__), src__global__)
    tr: float = atr(b, len)
    st__global__: supertrend_ = st(b, mlt, len)
    __block_result_3__ = na
    __switch__ = st__global__.d
    if __switch__ == 1:
        __block_result_3__ = cold
    elif __switch__ == -1:
        __block_result_3__ = colu
    cst: Color = __block_result_3__
    t = plot(st__global__.s if st__global__.d > 0 else na, 'Bear ST', cst, 1, plot.style_linebr)
    d = plot(st__global__.s if st__global__.d < 0 else na, 'Bull ST', cst, 1, plot.style_linebr)
    i = plot(st__global__.d, 'Direction', display=display.none)
    c = plot(src(b, 'oc2'), 'Filler', display=display.none)
    fill(t, c, color.new(cold, 90))
    fill(d, c, color.new(colu, 90))
    change_1 = ta.change(st__global__.d)
    scon: bool = True if clbl and math.sign(change_1) == 1 else False
    change_2 = ta.change(st__global__.d)
    bcon: bool = True if clbl and math.sign(change_2) == -1 else False
    plotshape(st__global__.s + tr / 3 if scon else na, 'Sell Signal', shape.labeldown, location.absolute, color.new(cold, 60), 0, '𝓢', chart.fg_color)
    plotshape(st__global__.s - tr / 3 if bcon else na, 'Buy Signal', shape.labelup, location.absolute, color.new(colu, 60), 0, '𝓑', chart.fg_color)
    LongEntry = st__global__.d < 0
    LongExit = st__global__.d > 0
    ShortEntry = st__global__.d > 0
    ShortExit = st__global__.d < 0
    if tradeDirection == 'Long' or tradeDirection == 'Both':
        if LongEntry:
            strategy.entry('Long Entry', strategy.long)
    if tradeDirection == 'Short' or tradeDirection == 'Both':
        if ShortEntry:
            strategy.entry('Short Entry', strategy.short)
    if tradeDirection == 'Long' or tradeDirection == 'Both':
        if LongExit:
            strategy.close('Long Entry')
    if tradeDirection == 'Short' or tradeDirection == 'Both':
        if ShortExit:
            strategy.close('Short Entry')
    if TPSLCondition == 'TP' or TPSLCondition == 'Both':
        strategy.exit('TakeProfit_Long', 'Long Entry', limit=close * (1 + takeProfitPerc / 100))
        strategy.exit('TakeProfit_Short', 'Short Entry', limit=close * (1 - takeProfitPerc / 100))
    if TPSLCondition == 'SL' or TPSLCondition == 'Both':
        strategy.exit('StopLoss_Long', 'Long Entry', stop=close * (1 - stopLossPerc / 100))
        strategy.exit('StopLoss_Short', 'Short Entry', stop=close * (1 + stopLossPerc / 100))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
