"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, fill, high, hlc3, input, location, low,
    math, na, open, plot, plotshape, request, script, shape, size, syminfo, ta, timeframe
)
from pynecore.types import Series


@script.indicator(title='VuManChu Cipher A', shorttitle='VMC Cipher_A', overlay=True, na_bool=True)
def main(
    wtChannelLen=input(9, title='WT Channel Length'),
    wtAverageLen=input(13, title='WT Average Length'),
    wtMASource: Series[float] = input(hlc3, title='WT MA Source'),
    wtMALen=input(3, title='WT MA Length'),
    obLevel=input(53, title='WT Overbought Level 1'),
    obLevel2=input(60, title='WT Overbought Level 2'),
    obLevel3=input(100, title='WT Overbought Level 3'),
    osLevel=input(-53, title='WT Oversold Level 1'),
    osLevel2=input(-60, title='WT Oversold Level 2'),
    osLevel3=input(-80, title='WT Oversold Level 3'),
    showRibbon=input(True, 'Show Ribbon'),
    ema1Len=input(5, title='EMA 1 Length'),
    ema2Len=input(11, title='EMA 2 Length'),
    ema3Len=input(15, title='EMA 3 Length'),
    ema4Len=input(18, title='EMA 4 Length'),
    ema5Len=input(21, title='EMA 5 Length'),
    ema6Len=input(24, title='EMA 6 Length'),
    ema7Len=input(28, title='EMA 7 Length'),
    ema8Len=input(34, title='EMA 8 Length'),
    rsiSRC: Series[float] = input(close, title='RSI Source'),
    rsiLen=input(14, title='RSI Length'),
    rsiOversold=input.int(30, title='RSI Oversold', minval=50, maxval=100),
    rsiOverbought=input.int(60, title='RSI Overbought', minval=0, maxval=50),
    rsiMFIShow=input(True, title='Show RSI+MFI'),
    rsiMFIperiod=input(60, title='RSI+MFI Period'),
    rsiMFIMultiplier=input(150, title='RSI+MFI Area multiplier')
):
    def f_wavetrend(_src, _chlen, _avg, _malen):
        _esa = ta.ema(_src, _chlen)
        _de = ta.ema(math.abs(_src - _esa), _chlen)
        _ci = (_src - _esa) / (0.015 * _de)
        _tci = ta.ema(_ci, _avg)
        _wt1 = _tci
        _wt2 = ta.sma(_wt1, _malen)
        return (_wt1, _wt2)

    def f_emaRibbon(_src, _e1, _e2, _e3, _e4, _e5, _e6, _e7, _e8):
        _ema1 = ta.ema(_src, _e1)
        _ema2 = ta.ema(_src, _e2)
        _ema3 = ta.ema(_src, _e3)
        _ema4 = ta.ema(_src, _e4)
        _ema5 = ta.ema(_src, _e5)
        _ema6 = ta.ema(_src, _e6)
        _ema7 = ta.ema(_src, _e7)
        _ema8 = ta.ema(_src, _e8)
        return (_ema1, _ema2, _ema3, _ema4, _ema5, _ema6, _ema7, _ema8)

    def f_rsimfi(_period, _multiplier, _tf):
        return request.security(syminfo.tickerid, _tf, ta.sma((close - open) / (high - low) * _multiplier, _period))

    ema1, ema2, ema3, ema4, ema5, ema6, ema7, ema8 = f_emaRibbon(close, ema1Len, ema2Len, ema3Len, ema4Len, ema5Len, ema6Len, ema7Len, ema8Len)
    rsi = ta.rsi(rsiSRC, rsiLen)
    wt1, wt2 = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen)
    wtOverSold = wt2 <= osLevel
    wtOverBought = wt2 >= obLevel
    wtCross = ta.cross(wt1, wt2)
    wtCrossUp = wt2 - wt1 <= 0
    wtCrossDown = wt2 - wt1 >= 0
    rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    longEma = ta.crossover(ema2, ema8)
    redCross = ta.crossunder(ema1, ema2)
    blueTriangle = ta.crossover(ema2, ema3)
    redDiamond = wtCross and wtCrossDown
    yellowCross = redDiamond and wt2 < 45 and (wt2 > osLevel3) and (rsi < 30) and (rsi > 15) and (rsiMFI < -5)
    bloodDiamond = redDiamond and redCross
    bullCandle = open > ema2 and open > ema8 and (close[1] > open[1]) and (close > open) and (not redDiamond) and (not redCross)
    shortEma = ta.crossover(ema8, ema2)
    ribbonDir = ema8 < ema2
    colorEma = color.green if ribbonDir else color.red
    p1 = plot(ema1, color=(color.new('#1573D4') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 1')
    p2 = plot(ema2, color=(color.new('#3096FF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 2')
    plot(ema3, color=(color.new('#57ABFF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 3')
    plot(ema4, color=(color.new('#85C2FF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 4')
    plot(ema5, color=(color.new('#9BCDFF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 5')
    plot(ema6, color=(color.new('#B3D9FF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 6')
    plot(ema7, color=(color.new('#C9E5FF') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 7')
    plot(ema8, color=(color.new('#DFECFB') if ribbonDir else color.gray) if showRibbon else na, linewidth=2, title='EMA 8')
    p8 = plot(ema8, color=na if showRibbon else colorEma, linewidth=2, title='EMA 8')
    fill(p1, p2, color=color.new(color.new('#1573D4'), 85))
    fill(p2, p8, color=color.new(color.new('#363A45'), 85))
    plotshape(longEma, style=shape.circle, color=color.new(color.new('#00FF00'), 50), location=location.abovebar, size=size.tiny, title='Long EMA Signal')
    plotshape(shortEma, style=shape.circle, color=color.new(color.new('#FF0000'), 50), location=location.abovebar, size=size.tiny, title='Short EMA Signal')
    plotshape(redCross, style=shape.xcross, color=color.new(color.new('#FF0000'), 50), location=location.abovebar, size=size.tiny, title='Red cross')
    plotshape(blueTriangle, style=shape.triangleup, color=color.new(color.new('#0064FF'), 50), location=location.abovebar, size=size.small, title='Blue Triangle')
    plotshape(redDiamond, style=shape.diamond, color=color.new(color.new('#FF0000'), 25), location=location.abovebar, size=size.tiny, title='Red Diamond')
    plotshape(bullCandle, style=shape.diamond, color=color.new(color.yellow, 75), location=location.abovebar, size=size.tiny, title='Bull candle')
    plotshape(bloodDiamond, style=shape.diamond, color=color.new(color.new('#FF0000'), 15), location=location.abovebar, size=size.small, title='Blood Diamond')
    plotshape(yellowCross, style=shape.xcross, color=color.new(color.yellow, 25), location=location.abovebar, size=size.small, title='Yellow Cross')
    alertcondition(redDiamond != cast_bool(0), 'Red Diamond', 'Red Diamond')
    alertcondition(bloodDiamond != cast_bool(0), 'Blood Diamond', 'Blood Diamond')
    alertcondition(yellowCross != 0, 'YellowX', 'YellowX')
    alertcondition(redCross != cast_bool(0), 'RedX', 'RedX')
    alertcondition(longEma != cast_bool(0), 'Longema', 'Longema')
    alertcondition(blueTriangle != cast_bool(0), 'Bluetriangle', 'Bluetriangle')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
