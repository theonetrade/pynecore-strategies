"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, barstate, color, fill, fixnan, format, high,
    hline, input, location, low, math, na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Series


@script.indicator(title='ADX Di+ Di- [Gu5]', shorttitle='ADX', overlay=False, format=format.price, precision=2, timeframe='', na_bool=True)
def main(
    i_sigLen=input.int(14, 'ADX Smoothing'),
    i_diLen=input.int(14, 'DI Length'),
    i_hlRange=input.int(20, 'Level Range'),
    i_hlTrend=input.int(35, 'Level Trend'),
    i_alertOn=input.bool(True, '■ Alert On/Off'),
    i_barColOn=input.bool(True, '■ Bar Color On/Off')
):
    C_GREEN: Color = color.new('#006400')
    C_GREENLIGHT: Color = color.new('#388E3C')
    C_RED: Color = color.new('#8B0000')
    C_REDLIGHT: Color = color.new('#B71C1C')
    def f_dirMov(_len):
        _up = ta.change(high)
        _down = -ta.change(low)
        _plusDM = na if na(_up) else _up if _up > _down and _up > 0 else 0
        _minusDM = na if na(_down) else _down if _down > _up and _down > 0 else 0
        _trueRange = ta.rma(ta.tr, _len)
        _plus = fixnan(100 * ta.rma(_plusDM, _len) / _trueRange)
        _minus = fixnan(100 * ta.rma(_minusDM, _len) / _trueRange)
        return (_plus, _minus)

    def f_sig(_diLen, _sigLen):
        _plus, _minus = f_dirMov(_diLen)
        _sum = _plus + _minus
        _sig = 100 * ta.rma(math.abs(_plus - _minus) / (1 if _sum == 0 else _sum), _sigLen)
        return (_sig,)

    condition: Series[float] = 0.0
    sig: Series
    sig, = f_sig(i_diLen, i_sigLen)
    diPlus, _ = f_dirMov(i_diLen)
    _, diMinus = f_dirMov(i_diLen)
    hlRange: Series = sig <= i_hlRange
    diUp: Series = diPlus >= diMinus
    diUpUp = diPlus >= i_hlTrend
    diDn: Series = diMinus > diPlus
    diDnDn = diMinus > i_hlTrend
    crossDi = ta.cross(diPlus, diMinus)
    sigUp = sig > sig[1]
    sigDir = 1 if sig > sig[1] and diUp and (not hlRange) else -1 if sig > sig[1] and diDn and (not hlRange) else 0
    entryLong = not hlRange and diUp and sigUp and (not diUp[1]) or (not hlRange and diUp and sigUp and (sig > i_hlRange) and hlRange[1])
    entryShort = not hlRange and diDn and sigUp and (not diDn[1]) or (not hlRange and diDn and sigUp and (sig > i_hlRange) and hlRange[1])
    entryLongStr = not hlRange and diUp and sigUp and diUpUp
    entryShortSt = not hlRange and diDn and sigUp and diDnDn
    exitLong = crossDi and diUp[1] or (hlRange and (not hlRange[1]))
    exitShort = crossDi and diDn[1] or (hlRange and (not hlRange[1]))
    condition = 1 if condition[1] != 1 and entryLongStr else -1 if condition[1] != -1 and entryShortSt else 0.5 if condition[1] != 0.5 and entryLong else -0.5 if condition[1] != -0.5 and entryShort else 0 if condition[1] != 0 and exitLong else 0 if condition[1] != 0 and exitShort else nz(condition[1])
    longE = barstate.isconfirmed and condition[1] != 0.5 and (condition == 0.5)
    shortE = barstate.isconfirmed and condition[1] != -0.5 and (condition == -0.5)
    longEStr = barstate.isconfirmed and condition[1] != 1 and (condition == 1)
    shortEStr = barstate.isconfirmed and condition[1] != -1 and (condition == -1)
    longX = barstate.isconfirmed and (condition[1] == 0.5 and condition == 0 or (condition[1] == 1 and condition == 0))
    shortX = barstate.isconfirmed and (condition[1] == -0.5 and condition == 0 or (condition[1] == -1 and condition == 0))
    c_sig = color.orange if hlRange else color.new(C_GREEN, 0) if sigUp and diUp else color.new(C_GREENLIGHT, 0) if not sigUp and diUp else color.new(C_RED, 0) if sigUp and diDn else color.new(C_REDLIGHT, 0) if not sigUp and diDn else na
    c_fillAdx = color.new(color.orange, 90) if hlRange else color.new(C_GREEN, 90) if not hlRange and diUp and diUpUp else color.new(C_GREENLIGHT, 90) if not hlRange and diUp and (not diUpUp) else color.new(C_RED, 90) if not hlRange and diDn and diDnDn else color.new(C_REDLIGHT, 90) if not hlRange and diDn and (not diDnDn) else na
    plot(sig, title='ADX', color=c_sig, linewidth=3)
    p_diPlus = plot(diPlus, title='+DI', color=C_GREEN)
    p_diMinus = plot(diMinus, title='-DI', color=C_RED)
    fill(p_diPlus, p_diMinus, title='Fill ADX ', color=c_fillAdx)
    plot(diPlus if crossDi else na, title='Cross Di', color=color.new('#00000000'), style=plot.style_circles, linewidth=2)
    hline(i_hlRange, title='Level Range', color=color.gray, linestyle=hline.style_dotted, linewidth=1)
    hline(i_hlTrend, title='Level Trend', color=color.gray, linestyle=hline.style_dotted, linewidth=1)
    barcolor(c_sig if i_barColOn else na)
    plotshape(i_hlTrend + 10 if i_alertOn and longE else na, title='Bullish\nTrend', color=C_GREEN, style=shape.triangleup, size=size.tiny, location=location.absolute)
    plotshape(i_hlTrend + 10 if i_alertOn and shortE else na, title='Bearish\nTrend', color=C_RED, style=shape.triangledown, size=size.tiny, location=location.absolute)
    plotshape(i_hlTrend + 10 if i_alertOn and longEStr else na, title='Strong\nBullish\nTrend', color=C_GREEN, style=shape.triangleup, size=size.small, location=location.absolute)
    plotshape(i_hlTrend + 10 if i_alertOn and shortEStr else na, title='Strong\nBearish\nTrend', color=C_RED, style=shape.triangledown, size=size.small, location=location.absolute)
    plotshape(i_hlTrend + 10 if i_alertOn and (longX or shortX) else na, title='End\nTrend', color=color.new(color.orange, 0), style=shape.xcross, size=size.small, location=location.absolute)
    alertcondition(longE or shortE or longEStr or shortEStr or longX or shortX, title='Any Alert', message='Any Alert')
    alertcondition(longE, title='Buy Weak Alert', message='Buy Weak Alert')
    alertcondition(shortE, title='Sell Weak Alert', message='Sell Weak Alert')
    alertcondition(longEStr, title='Buy Strong Alert', message='Buy Strong Alert')
    alertcondition(shortEStr, title='Sell Strong Alert', message='Sell Strong Alert')
    alertcondition(longX, title='Buy Close Alert', message='Buy Close Alert')
    alertcondition(shortX, title='Sell Close Alert', message='Sell Close Alert')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
