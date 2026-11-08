"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, format, high, hline, input,
    location, low, math, na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='MOST on RSI', shorttitle='MOSTRSI', format=format.price, precision=2, timeframe='', timeframe_gaps=True, na_bool=True)
def main(
    rsiLengthInput=input.int(14, minval=1, title='RSI Length', group='RSI Settings'),
    rsiSourceInput: Series[float] = input.source(close, 'Source', group='RSI Settings'),
    maTypeInput=input.string('VAR', title='MA Type', options=('SMA', 'Bollinger Bands', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA', 'VAR'), group='MOST Settings'),
    maLengthInput=input.int(5, title='MA Length', group='MOST Settings'),
    percent=input.float(9.0, 'STOP LOSS Percent', step=0.1, minval=0, group='MOST Settings'),
    bbMultInput=input.float(2.0, minval=0.001, maxval=50, title='BB StdDev', group='MOST Settings', display=display.data_window),
    showDivergence=input.bool(True, title='Show Divergence', group='RSI Settings', display=display.data_window),
    showsignalsk=input(title='Show Signals?', defval=False)
):
    def Var_Func(source: Series, length):
        valpha = 2 / (length + 1)
        vud1 = source - source[1] if source > source[1] else 0
        vdd1 = source[1] - source if source < source[1] else 0
        vUD = math.sum(vud1, 9)
        vDD = math.sum(vdd1, 9)
        vCMO = nz((vUD - vDD) / (vUD + vDD))
        VAR: Series[float] = 0.0
        VAR = nz(valpha * math.abs(vCMO) * source) + (1 - valpha * math.abs(vCMO)) * nz(VAR[1])
        return VAR

    def ma(source, length, type):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'Bollinger Bands':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'SMMA (RMA)':
            __block_result__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(source, length)
        elif __switch__ == 'VAR':
            __block_result__ = Var_Func(source, length)
        return __block_result__

    up = ta.rma(math.max(ta.change(rsiSourceInput), 0), rsiLengthInput)
    down = ta.rma(-math.min(ta.change(rsiSourceInput), 0), rsiLengthInput)
    rsi: Series = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    rsiMA = ma(rsi, maLengthInput, maTypeInput)
    isBB = maTypeInput == 'Bollinger Bands'
    exMov = rsiMA
    fark = exMov * percent * 0.01
    longStop: Series = exMov - fark
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if exMov > longStopPrev else longStop
    shortStop: Series = exMov + fark
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if exMov < shortStopPrev else shortStop
    dir: Series[int] = 1
    dir = nz(dir[1], dir)
    dir = 1 if dir == -1 and exMov > shortStopPrev else -1 if dir == 1 and exMov < longStopPrev else dir
    MOST = longStop if dir == 1 else shortStop
    cro = ta.crossover(exMov, MOST)
    cru = ta.crossunder(exMov, MOST)
    direction: Series[int] = 0
    direction = 1 if cro else -1 if cru else direction[1]
    plot(MOST, color=color.new(color.maroon, 0), linewidth=3, title='MOST')
    plotshape(cro and showsignalsk, title='BUY', text='BUY', location=location.bottom, style=shape.labelup, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    plotshape(cru and showsignalsk, title='SELL', text='SELL', location=location.top, style=shape.labeldown, size=size.tiny, color=color.new(color.new('#0F18BF'), 0), textcolor=color.new(color.white, 0))
    alertcondition(cro, title='BUY', message='BUY SIGNAL!')
    alertcondition(cru, title='SELL', message='SELL SIGNAL!')
    rsiPlot = plot(rsi, 'RSI', color=color.new('#7E57C2'))
    plot(rsiMA, 'RSI-based MA', color=color.yellow)
    rsiUpperBand = hline(70, 'RSI Upper Band', color=color.new('#787B86'))
    midline = hline(50, 'RSI Middle Band', color=color.new(color.new('#787B86'), 50))
    rsiLowerBand = hline(30, 'RSI Lower Band', color=color.new('#787B86'))
    fill(rsiUpperBand, rsiLowerBand, color=color.rgb(126, 87, 194, 90), title='RSI Background Fill')
    bbUpperBand = plot(rsiMA + ta.stdev(rsi, maLengthInput) * bbMultInput if isBB else na, title='Upper Bollinger Band', color=color.green)
    bbLowerBand = plot(rsiMA - ta.stdev(rsi, maLengthInput) * bbMultInput if isBB else na, title='Lower Bollinger Band', color=color.green)
    fill(bbUpperBand, bbLowerBand, color=color.new(color.green, 90) if isBB else na, title='Bollinger Bands Background Fill')
    midLinePlot = plot(50, color=na, editable=False, display=display.none)
    fill(rsiPlot, midLinePlot, 100, 70, top_color=color.new(color.green, 0), bottom_color=color.new(color.green, 100), title='Overbought Gradient Fill')
    fill(rsiPlot, midLinePlot, 30, 0, top_color=color.new(color.red, 100), bottom_color=color.new(color.red, 0), title='Oversold Gradient Fill')
    lookbackRight: int = 5
    lookbackLeft: int = 5
    rangeUpper: int = 60
    rangeLower: int = 5
    bearColor = color.red
    bullColor = color.green
    textColor = color.white
    noneColor = color.new(color.white, 100)
    plFound: Series = False if na(ta.pivotlow(rsi, lookbackLeft, lookbackRight)) else True
    phFound: Series = False if na(ta.pivothigh(rsi, lookbackLeft, lookbackRight)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    rsiHL = rsi[lookbackRight] > ta.valuewhen(plFound, rsi[lookbackRight], 1) and _inRange_1
    priceLL = low[lookbackRight] < ta.valuewhen(plFound, low[lookbackRight], 1)
    bullCondAlert = priceLL and rsiHL and plFound
    bullCond = showDivergence and bullCondAlert
    plot(rsi[lookbackRight] if plFound else na, offset=-lookbackRight, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(rsi[lookbackRight] if bullCond else na, offset=-lookbackRight, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=bullColor, textcolor=textColor)
    _inRange_2 = _inRange(phFound[1])
    rsiLH = rsi[lookbackRight] < ta.valuewhen(phFound, rsi[lookbackRight], 1) and _inRange_2
    priceHH = high[lookbackRight] > ta.valuewhen(phFound, high[lookbackRight], 1)
    bearCondAlert = priceHH and rsiLH and phFound
    bearCond = showDivergence and bearCondAlert
    plot(rsi[lookbackRight] if phFound else na, offset=-lookbackRight, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(rsi[lookbackRight] if bearCond else na, offset=-lookbackRight, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=bearColor, textcolor=textColor)
    alertcondition(bullCondAlert, title='Regular Bullish Divergence', message='Found a new Regular Bullish Divergence, `Pivot Lookback Right` number of bars to the left of the current bar.')
    alertcondition(bearCondAlert, title='Regular Bearish Divergence', message='Found a new Regular Bearish Divergence, `Pivot Lookback Right` number of bars to the left of the current bar.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
