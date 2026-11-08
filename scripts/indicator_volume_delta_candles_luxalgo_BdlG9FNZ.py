"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, barcolor, barstate, chart, close, color, display, extend,
    format, high, input, label, line, low, math, na, open, order, plot, plotcandle, position,
    request, script, size, string, syminfo, table, timeframe, volume
)
from pynecore.types import Color, IBPersistent, Persistent, Series, Table


@udt
class bin:
    p: float = na(float)
    v: float = na(float)


@script.indicator('Volume Delta Candles [LuxAlgo]', shorttitle='LuxAlgo - Volume Delta Candles', max_labels_count=500, overlay=True)
def main(
    tick=input.string('LTF', 'Data from: ', options=('Ticks', 'LTF')),
    res=input.timeframe('1', tooltip='Data from: \'LTF\'\nAuto: \'Disabled\''),
    auto=input.bool(True, '', inline='auto'),
    mlt=input.int(1500, ' Auto   ', inline='auto', tooltip='current TF divided by x\n\nData from: \'LTF\'\nAuto: \'Enabled\''),
    prem=input.bool(False, 'Premium', tooltip='Premium Plan or higher'),
    colUp=input.color(color.new('#089981'), 'Up     ', inline='u', group='Intrabar Delta'),
    colUp_=input.color(color.new('#F23645'), 'Up -     ', inline='u', group='Intrabar Delta', tooltip='Up -\n-> bullish candle and - Delta'),
    colDn=input.color(color.new('#F23645'), 'Down', inline='d', group='Intrabar Delta'),
    colDn_=input.color(color.new('#089981'), 'Down +', inline='d', group='Intrabar Delta', tooltip='Down +\n-> bearish candle and + Delta'),
    option=input.string('full bar', 'Display', options=('half bar', 'full bar')),
    dot=input.bool(False, 'Show Previous Max Volume Price'),
    showTab=input.bool(True, 'Show TF', group='Table'),
    tabCol=input.color(color.new('#B2B5BEAA'), 'Text Color', group='Table'),
    sizeT=input.string(size.tiny, 'Size Table', group='Table', options=(size.tiny, size.small, size.normal, size.large)),
    showD=input.bool(False, 'Show details', group='Details')
):
    n = bar_index
    INV = color.new(na, na)
    CFG: Color = chart.fg_color
    isTick = tick == 'Ticks'
    isLTF = tick == 'LTF'
    volBl: IBPersistent[float] = na(float)
    volBr: IBPersistent[float] = na(float)
    volNt: IBPersistent[float] = na(float)
    maxBl: IBPersistent[bin] = bin(na, 0)
    maxBr: IBPersistent[bin] = bin(na, 0)
    vl: IBPersistent[float] = na(float)
    cl: IBPersistent[float] = na(float)
    dfP: IBPersistent[float] = na(float)
    dfV: IBPersistent[float] = na(float)
    TdfV: IBPersistent[float] = na(float)
    ticksAvailable: IBPersistent[bool] = False
    tab: Persistent[Table] = na(Table)
    if isTick:
        if barstate.isnew:
            maxBl.v = 0
            maxBr.v = 0
            cl = open
            dfP = 0
            vl = volume
            dfV = 0
            TdfV = 0
            volBl = 0
            volBr = 0
            volNt = 0
        else:
            dfP = close - cl
            dfV = volume - vl
            if dfP > 0:
                volBl = volBl + dfV
                TdfV = TdfV + dfV
                if dfV > maxBl.v:
                    maxBl.v = dfV
                    maxBl.p = close
            elif dfP < 0:
                volBr = volBr + dfV
                TdfV = TdfV + dfV
                if dfV > maxBr.v:
                    maxBr.v = dfV
                    maxBr.p = close
            cl = close
            vl = volume
    tfS = timeframe.in_seconds(res)
    tfC = timeframe.in_seconds(timeframe.period)
    rs = tfC / mlt if auto else tfS
    rs = rs if prem else math.max(60, rs)
    res = timeframe.from_seconds(math.min(tfC, rs))
    bV, sV, nV, tV, aCl = request.security_lower_tf(syminfo.tickerid, res, (volume if close > open else 0, volume if close < open else 0, volume if close == open else 0, volume, close))
    vSize = method_call('size', tV)
    maxV: float = na(float)
    bVmax: float = na(float)
    sVmax: float = na(float)
    if isLTF:
        bVmax = method_call('max', bV)
        sVmax = method_call('max', sV)
        indices = method_call('sort_indices', bV if bVmax > sVmax else sV, order.descending)
        maxV = method_call('get', aCl, method_call('first', indices)) if method_call('size', indices) > 0 else na
    else:
        if maxBl.v != 0 or maxBr.v != 0:
            maxV = maxBl.p if maxBl.v > maxBr.v else maxBr.p
    if not ticksAvailable and volBl > 0:
        ticksAvailable = True
    isAllowed: Series = ticksAvailable if isTick else method_call('size', tV) > 0
    if isAllowed and (not isAllowed[1]):
        line.new(n, close, n, close + syminfo.mintick, color=color.silver, style=line.style_dotted, extend=extend.both)
    ltf_Vup = method_call('sum', bV)
    ltf_Vdn = method_call('sum', sV)
    bullV = volBl if isTick else ltf_Vup
    bearV = volBr if isTick else ltf_Vdn
    abs = math.abs(open - close)
    min = math.min(open, close)
    max = math.max(open, close)
    avg = math.avg(open, close)
    vol = bullV + bearV
    delta = bullV - bearV
    norm = delta / volume
    aNorm = math.abs(norm)
    pos = norm >= 0
    base: float = na(float)
    value: float = na(float)
    value = avg + norm * abs / 2 if option == 'half bar' else min + aNorm * abs if pos else max - aNorm * abs
    base = avg if option == 'half bar' else min if pos else max
    css = colUp if close > open else colDn if close < open else CFG
    cssD = color.new((colUp if close > open else colDn_) if norm > 0 else colDn if close < open else colUp_, 50)
    barcolor(INV)
    plotcandle(base, base, value, value, color=cssD, wickcolor=na, bordercolor=na, display=display.all - display.status_line)
    plotcandle(open, high, low, close, color=na, wickcolor=css, bordercolor=css, display=display.all - display.status_line)
    plotcandle(maxV, maxV, maxV, maxV, color=CFG, wickcolor=na, bordercolor=CFG, display=display.all - display.status_line)
    plot(maxV if dot else na, color=CFG, style=plot.style_circles, offset=1, display=display.all - display.status_line)
    plot(bullV, display=display.data_window)
    plot(bearV, display=display.data_window)
    volu = string.tostring(vol, format.volume)
    delt = string.tostring(delta, format.volume)
    perc = string.tostring(norm * 100, format.percent)
    if isAllowed and showD:
        label.new(n, high, color=INV, textcolor=CFG, size=size.small, text=string.format('Volume: {0}\nDelta: {1}\n%: {2}', volu, delt, perc))
    if showTab and isLTF:
        if barstate.isfirst:
            tab = table.new(position.top_right, 1, 1, bgcolor=INV)
        if barstate.islast:
            table.cell(tab, 0, 0, res, text_color=tabCol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
