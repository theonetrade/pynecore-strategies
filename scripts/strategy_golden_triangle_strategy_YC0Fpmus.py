"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, bgcolor, close, color, currency, high, input, line, low, math,
    na, nz, open, plot, script, strategy, string, ta
)
from pynecore.types import Persistent, Series


@script.strategy(title='Golden Triangle Strategy', overlay=True, pyramiding=2, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, currency=currency.USD, max_bars_back=200, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    smaLength=input(50, title='SMA Length'),
    lookBackPds=input(200, title='Look Back periods'),
    riskCapital=input.int(title='Risk % of capital', defval=10, minval=1),
    stopLoss=input.int(title='Stop Loss%', defval=6, minval=1),
    changeBarColor=input(True, title='chage bar color'),
    showAllTriangles=input(False, title='show Triangles even after Long position is taken'),
    pivotPeriod=input.int(defval=5, title='Pivot Point Period', minval=1, maxval=50),
    atrFactor=input.float(defval=3, title='ATR Factor', minval=1, step=0.1),
    atrPeriod=input.int(defval=50, title='ATR Period', minval=1)
):
    triangleFound: Persistent[bool] = False
    windupPrice: Persistent[float] = 0.0
    stopLossVal: Persistent[float] = 0.0
    def findIndexForWhiteSpace(smaLength1, lookbackPds1):
        prev_index: int = 0
        smaVal1: Series = ta.sma(close, smaLength1)
        for i in pine_range(1, lookbackPds1, 1):
            if low[i] < smaVal1[i] and close[i] > smaVal1[i]:
                prev_index = i
                break
            if open[i] < smaVal1[1] and high[i] < smaVal1[i]:
                prev_index = 0
                break
        return prev_index

    def index_HH(pds):
        tHH: float = 0.0
        HH_index: int = 1
        for i in pine_range(1, pds, 1):
            if high[i] > tHH:
                tHH = high[i]
                HH_index = i
        return HH_index

    def index_LL(pds):
        tLL = low
        LL_index: int = 1
        for i in pine_range(1, pds, 1):
            if low[i] < tLL:
                tLL = low[i]
                LL_index = i
        return LL_index

    smaVal = ta.sma(close, smaLength)
    plot(smaVal, color=color.new(color.green, 0), linewidth=1)
    isPriceAbove50: bool = True
    for i in pine_range(1, 10, 1):
        if not (high[i] > smaVal and low[i] > smaVal):
            isPriceAbove50 = False
            break
    longCondition = isPriceAbove50 and high > smaVal and (low < smaVal)
    lastIndex = findIndexForWhiteSpace(smaLength, lookBackPds)
    HH_index = index_HH(lastIndex)
    drawCondition = longCondition and lastIndex > 1 if showAllTriangles == True else longCondition and lastIndex > 1 and (strategy.position_size < 1)
    if drawCondition:
        line.new(x1=bar_index[lastIndex], y1=low[lastIndex], x2=bar_index[HH_index], y2=high[HH_index], color=color.red, width=2)
        line.new(x1=bar_index[HH_index], y1=high[HH_index], x2=bar_index, y2=close, color=color.green, width=2)
        line.new(x1=bar_index[lastIndex], y1=low[lastIndex], x2=bar_index, y2=close, color=color.blue, width=2)
        triangleFound = True
        windupPrice = low[lastIndex]
    vwapVal = ta.vwap
    pvtHigh: float = na(float)
    pvtLow: float = na(float)
    pvtHigh = ta.pivothigh(pivotPeriod, pivotPeriod)
    pvtLow = ta.pivotlow(pivotPeriod, pivotPeriod)
    center: Series[float] = na(float)
    center = center[1]
    lastpp: float = pvtHigh if cast_bool(pvtHigh) else pvtLow if cast_bool(pvtLow) else na
    if cast_bool(lastpp):
        if na(center):
            center = lastpp
        else:
            center = (center * 2 + lastpp) / 3
    Up = center - atrFactor * ta.atr(atrPeriod)
    Dn = center + atrFactor * ta.atr(atrPeriod)
    TUp: Series[float] = na(float)
    TDown: Series[float] = na(float)
    Trend: Series[int] = 0
    TUp = math.max(Up, TUp[1]) if close[1] > TUp[1] else Up
    TDown = math.min(Dn, TDown[1]) if close[1] < TDown[1] else Dn
    Trend = 1 if close > TDown[1] else -1 if close < TUp[1] else nz(Trend[1], 1)
    Trailingstop = TUp if Trend == 1 else TDown
    tslColor = color.lime if Trend == 1 and nz(Trend[1]) == 1 else color.red if Trend == -1 and nz(Trend[1]) == -1 else na
    plot(TUp if Trend == 1 else na, color=tslColor, linewidth=2, title='Pivot Trailing Stop')
    qty1 = strategy.equity * riskCapital / 100 / (close * stopLoss / 100)
    qty1 = strategy.equity / close if qty1 * close >= strategy.equity else qty1
    crossover_1 = ta.crossover(close, vwapVal)
    if triangleFound and Trend == 1 and crossover_1:
        strategy.entry(id='GT LE', comment='GT LE SL=' + string.tostring(close * (1 - stopLoss * 0.01), '####.##'), direction=strategy.long, qty=qty1)
    triangleFound = False if strategy.position_size >= 1 else triangleFound
    stopLossVal = strategy.position_avg_price * (1 - stopLoss * 0.01) if strategy.position_size >= 1 else 0.0
    takeProfitVal = strategy.position_avg_price * (1 + 2 * 0.01) if strategy.position_size >= 1 else 0.0
    plot(stopLossVal if strategy.position_size >= 1 else na, color=color.new(color.purple, 0), style=plot.style_linebr, linewidth=2, title='stop loss')
    bgcolor(color.blue if strategy.position_size >= 1 else na)
    crossunder_1 = ta.crossunder(vwapVal, smaVal)
    if close > strategy.position_avg_price and crossunder_1:
        strategy.close(id='GT LE', comment='GTVW Exit  points=' + string.tostring(close - strategy.position_avg_price, '###.##'))
    if ta.crossunder(close, stopLossVal):
        strategy.close(id='GT LE', comment='SL Exit points=' + string.tostring(close - strategy.position_avg_price, '###.##'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
