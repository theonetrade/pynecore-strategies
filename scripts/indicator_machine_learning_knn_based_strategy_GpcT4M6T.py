"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    alertcondition, array, close, color, format, high, input, location, low,
    math, na, nz, plot, plotshape, script, shape, size, ta, time, timestamp, volume
)
from pynecore.types import Persistent, PersistentSeries

startdate: int = timestamp('01 Jan 2000 00:00:00 GMT+10')
stopdate: int = timestamp('31 Dec 2025 23:45:00 GMT+10')


@script.indicator('Machine Learning: kNN-based Strategy', 'ML-kNN', True, max_labels_count=300, format=format.price, precision=2, timeframe='', timeframe_gaps=True)
def main(
    StartDate=input.time(startdate, 'Start Date'),
    StopDate=input.time(stopdate, 'Stop Date'),
    Indicator=input.string('All', 'Indicator', options=('RSI', 'ROC', 'CCI', 'Volume', 'All')),
    ShortWinow=input.int(14, 'Short Period [1..n]', minval=1),
    LongWindow=input.int(28, 'Long Period [2..n]', minval=2),
    BaseK=input.int(252, 'Base No. of Neighbours (K) [5..n]', minval=5),
    Filter=input.bool(False, 'Volatility Filter'),
    Bars=input.int(300, 'Bar Threshold [2..5000]', minval=2, maxval=5000)
):
    BUY: Persistent[int] = 1
    SELL: Persistent[int] = -1
    CLEAR: Persistent[int] = 0
    k: Persistent[int] = math.floor(math.sqrt(BaseK))
    feature1: Persistent[list[float]] = array.new_float(0)
    feature2: Persistent[list[float]] = array.new_float(0)
    directions: Persistent[list[int]] = array.new_int(0)
    predictions: Persistent[list[int]] = array.new_int(0)
    prediction: Persistent[float] = 0.0
    bars: Persistent[list[int]] = array.new_int(1, 0)
    signal: PersistentSeries[int] = CLEAR
    def minimax(x: float, p: int, min: float, max: float):
        hi: float = ta.highest(x, p)
        lo: float = ta.lowest(x, p)
        return (max - min) * (x - lo) / (hi - lo) + min

    def cAqua(g: int):
        return color.new('#0080FF') if g > 9 else color.new('#0080FFE5') if g > 8 else color.new('#0080FFCC') if g > 7 else color.new('#0080FFB2') if g > 6 else color.new('#0080FF99') if g > 5 else color.new('#0080FF7F') if g > 4 else color.new('#0080FF66') if g > 3 else color.new('#0080FF4C') if g > 2 else color.new('#0080FF33') if g > 1 else color.new('#00C0FF19')

    def cPink(g: int):
        return color.new('#FF0080') if g > 9 else color.new('#FF0080E5') if g > 8 else color.new('#FF0080CC') if g > 7 else color.new('#FF0080B2') if g > 6 else color.new('#FF008099') if g > 5 else color.new('#FF00807F') if g > 4 else color.new('#FF008066') if g > 3 else color.new('#FF00804C') if g > 2 else color.new('#FF008033') if g > 1 else color.new('#FF008019')

    def inside_window(start: float, stop: float):
        return True if time >= start and time <= stop else False

    window: bool = inside_window(StartDate, StopDate)
    rs: float = ta.rsi(close, LongWindow)
    rf: float = ta.rsi(close, ShortWinow)
    cs: float = ta.cci(close, LongWindow)
    cf: float = ta.cci(close, ShortWinow)
    os: float = ta.roc(close, LongWindow)
    of: float = ta.roc(close, ShortWinow)
    vs: float = minimax(volume, LongWindow, 0, 99)
    vf: float = minimax(volume, ShortWinow, 0, 99)
    __block_result__ = na
    __switch__ = Indicator
    if __switch__ == 'RSI':
        __block_result__ = rs
    elif __switch__ == 'CCI':
        __block_result__ = cs
    elif __switch__ == 'ROC':
        __block_result__ = os
    elif __switch__ == 'Volume':
        __block_result__ = vs
    else:
        __block_result__ = math.avg(rs, cs, os, vs)
    f1: float = __block_result__
    __block_result_1__ = na
    __switch__ = Indicator
    if __switch__ == 'RSI':
        __block_result_1__ = rf
    elif __switch__ == 'CCI':
        __block_result_1__ = cf
    elif __switch__ == 'ROC':
        __block_result_1__ = of
    elif __switch__ == 'Volume':
        __block_result_1__ = vf
    else:
        __block_result_1__ = math.avg(rf, cf, of, vf)
    f2: float = __block_result_1__
    class_label: int = cast_int(math.sign(close[1] - close))
    if window:
        array.push(feature1, f1)
        array.push(feature2, f2)
        array.push(directions, class_label)
    size__ren__: int = array.size(directions)
    maxdist: float = -999.0
    for i in pine_range(0, size__ren__ - 1, 1):
        d: float = math.sqrt(math.pow(f1 - array.get(feature1, i), 2) + math.pow(f2 - array.get(feature2, i), 2))
        if d > maxdist:
            maxdist = d
            if array.size(predictions) >= k:
                array.shift(predictions)
            array.push(predictions, array.get(directions, i))
    prediction = array.sum(predictions)
    filter: bool = ta.atr(10) > ta.atr(40) if Filter else True
    long: bool = prediction > 0 and filter
    short: bool = prediction < 0 and filter
    clear: bool = not (long and short)
    if array.get(bars, 0) == Bars:
        signal = CLEAR
        array.set(bars, 0, 0)
    else:
        array.set(bars, 0, array.get(bars, 0) + 1)
    signal = BUY if long else SELL if short else CLEAR if clear else nz(signal[1])
    changed: int = ta.change(signal)
    startLongTrade: bool = cast_bool(changed) and signal == BUY
    startShortTrade: bool = cast_bool(changed) and signal == SELL
    clear_condition: bool = cast_bool(changed) and signal == CLEAR
    maxpos: float = ta.highest(high, 10)
    minpos: float = ta.lowest(low, 10)
    plotshape(minpos if startLongTrade else na, 'Buy', shape.labelup, location.belowbar, cAqua(cast_int(prediction * 5)), size=size.small)
    plotshape(maxpos if startShortTrade else na, 'Sell', shape.labeldown, location.abovebar, cPink(cast_int(-prediction * 5)), size=size.small)
    plot(close if clear_condition else na, 'ClearPos', color.yellow, 4, plot.style_cross)
    alertcondition(startLongTrade, 'Buy', 'Go long!')
    alertcondition(startShortTrade, 'Sell', 'Go short!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)