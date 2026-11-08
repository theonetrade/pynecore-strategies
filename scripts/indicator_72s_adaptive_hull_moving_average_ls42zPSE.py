"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, bgcolor, close, color, fill, high, input, location, low, math, na,
    plot, plotchar, script, size, string, ta, volume
)
from pynecore.types import Persistent, Series


@script.indicator('72s: Adaptive Hull Moving Average+', shorttitle='72s: Adaptive HMA+', overlay=True, na_bool=True)
def main(
    charger=input.string('Volatility', title='Choose which charger to adapt to:', options=('Volatility', 'Volume')),
    src: Series[float] = input(close, title='Source:'),
    minLength=input(172, title='Minimum period:'),
    maxLength=input(233, title='Maximum period:'),
    flat=input(17, title='Consolidation area is when slope below:'),
    showMinor=input.bool(True, title='Show minor xHMA+', group='Minor Adaptive HMA+ Period'),
    minorMin=input.int(89, title='Minimum:', group='Minor Adaptive HMA+ Period', inline='mHMA+'),
    minorMax=input.int(121, title='Maximum:', group='Minor Adaptive HMA+ Period', inline='mHMA+'),
    showZone=input.bool(False, title='Show Adaptive HMA+ Distance Zone', group='DISTANCE ZONE'),
    mult=input.float(2.7, title='Distance (Envelope) Multiplier', step=0.1, group='DISTANCE ZONE'),
    showSignals=input.bool(True, title='Show Possible Signals', group='OTHER'),
    useBg=input.bool(True, title='Background color to differentiate movement', group='OTHER')
):
    adaptPct: float = 0.03141
    highVolatility = ta.atr(14) > ta.atr(46)
    rsivol = ta.rsi(volume, 14)
    osc = ta.hma(rsivol, 10)
    volBreak = osc > 49
    dynamicLength: Persistent[float] = math.avg(minLength, maxLength)
    minorLength: Persistent[float] = math.avg(minorMin, minorMax)
    plugged = volBreak if charger == 'Volume' else highVolatility
    dynamicLength = math.max(minLength, dynamicLength * (1 - adaptPct)) if plugged else math.min(maxLength, dynamicLength * (1 + adaptPct))
    minorLength = math.max(minorMin, minorLength * (1 - adaptPct)) if plugged else math.min(minorMax, minorLength * (1 + adaptPct))
    slope_period: int = 34
    range_1: int = 25
    pi = math.atan(1) * 4
    highestHigh = ta.highest(slope_period)
    lowestLow = ta.lowest(slope_period)
    slope_range = range_1 / (highestHigh - lowestLow) * lowestLow
    def calcslope(_ma: Series):
        dt = (_ma[2] - _ma) / src * slope_range
        c = math.sqrt(1 + dt * dt)
        xAngle = math.round(180 * math.acos(1 / c) / pi)
        maAngle = -xAngle if dt > 0 else xAngle
        return maAngle

    def dynColor(_ma, _col1a, _col1b, _col2a, _col2b, _col0):
        slope = calcslope(_ma)
        return (_col1a if plugged else _col1b) if slope >= flat else _col0 if slope < flat and slope > -flat else (_col2a if plugged else _col2b) if slope <= -flat else _col0

    def xhma(_src, _length):
        _return = ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.floor(math.sqrt(_length)))
        return _return

    dynamicHMA = xhma(src, cast_int(dynamicLength))
    minorHMA = xhma(src, cast_int(minorLength))
    plot(dynamicHMA, 'Dynamic HMA+', dynColor(dynamicHMA, color.new('#6FBF73'), color.new('#C0F5AE'), color.new('#EB4D5C'), color.new('#F2B1D4'), color.yellow), 3)
    plot(minorHMA if showMinor else na, 'minor HMA+', dynColor(minorHMA, color.new('#6FBF73'), color.new('#C0F5AE'), color.new('#EB4D5C'), color.new('#F2B1D4'), color.yellow), 1)
    calcslope_1 = calcslope(dynamicHMA)
    notgreat = calcslope(dynamicHMA) < flat and calcslope_1 > -flat
    bgcolor((na if plugged else color.new('#757779') if notgreat else color.new('#AFB4B9')) if useBg else na)
    upperTL = dynamicHMA + mult * ta.atr(40)
    lowerTL = dynamicHMA - mult * ta.atr(40)
    topTL = dynamicHMA + mult * 2 * ta.atr(40)
    botTL = dynamicHMA - mult * 2 * ta.atr(40)
    stopupperTL = dynamicHMA + mult / 2 * ta.atr(40)
    stoplowerTL = dynamicHMA - mult / 2 * ta.atr(40)
    plot(upperTL if showZone else na, color=color.new(color.green, 72))
    plot(lowerTL if showZone else na, color=color.new(color.red, 72))
    plot(topTL if showZone else na, color=color.new(color.gray, 72))
    plot(botTL if showZone else na, color=color.new(color.gray, 72))
    sutl = plot(stopupperTL if showZone else na, color=color.new(color.white, 100))
    sltl = plot(stoplowerTL if showZone else na, color=color.new(color.white, 100))
    colZone = color.purple if showZone else color.new(color.white, 100)
    fill(sutl, sltl, color=color.new(colZone, 90))
    _slope = calcslope(dynamicHMA)
    _upSig: Series = _slope >= flat and plugged
    _dnSig: Series = _slope <= -flat and plugged
    buy = _upSig and (not _upSig[1])
    sell = _dnSig and (not _dnSig[1])
    _upExit: Series = _slope >= flat and (not plugged) and (close < minorHMA)
    _dnExit: Series = _slope <= -flat and (not plugged) and (close > minorHMA)
    fastExits = _upExit and (not _upExit[1]) or (_dnExit and (not _dnExit[1]))
    _topWarn: Series = high > topTL
    _botWarn: Series = low < botTL
    warningSigns = _topWarn and (not _topWarn[1]) or (_botWarn and (not _botWarn[1]))
    atrPos = 0.72 * ta.atr(5)
    plotchar(dynamicHMA - atrPos if showSignals and buy else na, color=color.new(color.green, 0), location=location.absolute, char='⬆', size=size.tiny)
    plotchar(dynamicHMA + atrPos if showSignals and sell else na, color=color.new(color.red, 0), location=location.absolute, char='⬇', size=size.tiny)
    plotchar((minorHMA + atrPos if _upExit else minorHMA - atrPos if _dnExit else na) if showSignals and fastExits else na, color=color.green if _upExit else color.red if _dnExit else na, location=location.absolute, char='ⓧ', size=size.tiny)
    plotchar((high + atrPos if _topWarn else low - atrPos if _botWarn else na) if showSignals and warningSigns else na, color=color.new(color.orange, 0), location=location.absolute, char='⚠', size=size.tiny)
    if buy:
        alert('Possible Buy Signal at' + string.tostring(close), alert.freq_once_per_bar_close)
    if sell:
        alert('Possible Sell Signal at' + string.tostring(close), alert.freq_once_per_bar_close)
    if fastExits and _upExit:
        alert('Price has just crossed down minor xHMA+ at' + string.tostring(close), alert.freq_once_per_bar_close)
    if fastExits and _dnExit:
        alert('Price has just crossed up minor xHMA+ at' + string.tostring(close), alert.freq_once_per_bar_close)
    if warningSigns and _topWarn:
        alert('Price has just crossed above top xHMA+ zone', alert.freq_once_per_bar_close)
    if warningSigns and _botWarn:
        alert('Price has just crossed below bottom xHMA+ zone', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)