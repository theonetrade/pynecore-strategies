"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, array, close, color, display, high, input, low,
    math, nz, open, plot, script, ta
)
from pynecore.types import Persistent, PersistentSeries, Series
import lib.HeWhoMustNotBeNamed.arrayutils.v10 as pa


@script.indicator('Supertrend - Ladder ATR - 1909Capital [Trendoscope®]', "SLA [Trendoscope®]", overlay=True)
def main(
    matype=input.string('hma', title='Moving Average  ', group='Supertrend', options=('sma', 'ema', 'rma', 'wma', 'hma'), inline='ma'),
    malength=input.int(7, title='', group='Supertrend', inline='ma'),
    multiplier=input.int(4, 'ATR Multiplier', step=1, group='Supertrend'),
    waitForClose=input.bool(False, 'Wait For Close', group='Supertrend'),
    delayed=input.bool(False, 'Delayed/Sticky', group='Supertrend')
):
    def supertrend_atr(positiveAtr: float, negativeAtr: float, multiplier: float, waitForClose: bool = False, delayed: bool = False):
        dir: Persistent[int] = 1
        lowSource = low
        highSource = high
        source = close
        buyStopDiff: Series = negativeAtr * multiplier
        sellStopDiff: Series = positiveAtr * multiplier
        buyStopDiff = math.min(buyStopDiff, nz(buyStopDiff[1], buyStopDiff)) if dir == 1 else buyStopDiff
        sellStopDiff = math.min(sellStopDiff, nz(sellStopDiff[1], sellStopDiff)) if dir == -1 else sellStopDiff
        buyStop: PersistentSeries = lowSource - buyStopDiff
        sellStop: PersistentSeries = highSource + sellStopDiff

        buyStopCurrent = lowSource - buyStopDiff
        sellStopCurrent = highSource + sellStopDiff

        buyStopInverse = lowSource - buyStopDiff / 2
        sellStopInverse = highSource + sellStopDiff / 2

        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        targetReached = dir == 1 and nz(highConfirmation[1]) >= nz(sellStop[1]) or (dir == -1 and nz(lowConfirmation[1]) <= nz(buyStop[1])) or (not delayed)
        buyStop = (math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if targetReached else buyStop) if dir == 1 else buyStopCurrent if targetReached else math.max(nz(buyStop, buyStopInverse), buyStopInverse)
        sellStop = (math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if targetReached else sellStop) if dir == -1 else sellStopCurrent if targetReached else math.min(nz(sellStop, sellStopInverse), sellStopInverse)
        return (dir, buyStop if dir > 0 else sellStop)

    positiveTrArray: Persistent[list[float]] = array.new_float()
    negativeTrArray: Persistent[list[float]] = array.new_float()

    if open < close:
        pa.push(positiveTrArray, ta.tr, malength)
    else:
        pa.push(negativeTrArray, ta.tr, malength)

    positiveAtr = pa.ma(positiveTrArray, matype, malength)
    negativeAtr = pa.ma(negativeTrArray, matype, malength)

    dir, supertrend = supertrend_atr(positiveAtr, negativeAtr, multiplier, waitForClose, delayed)
    alertcondition(ta.change(dir) > 0, 'Supertrend Bullish Alert')
    alertcondition(ta.change(dir) < 0, 'Supertrend Bearish Alert')

    directionChange = ta.change(dir)
    alertMessage = 'Supertrend Bullish' if directionChange > 0 else 'Supertrend Bearish' if directionChange < 0 else 'na'
    if directionChange != 0:
        alert(alertMessage, alert.freq_once_per_bar_close)

    plot(supertrend, color=color.rgb(83, 195, 189) if dir > 0 else color.fuchsia, title='Supertrend Stop')
    plot(dir, 'Direction', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)