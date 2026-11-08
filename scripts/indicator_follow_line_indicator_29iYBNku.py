"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, na, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(shorttitle='FLI', title='Follow Line Indicator', overlay=True, na_bool=True)
def main(
    BBperiod=input.int(defval=21, title='BB Period', minval=1),
    BBdeviations=input.float(defval=1.0, title='BB Deviations', minval=0.1, step=0.05),
    UseATRfilter=input(defval=True, title='ATR Filter'),
    ATRperiod=input.int(defval=5, title='ATR Period', minval=1),
    hl=input(defval=False, title='Hide Labels')
):
    BBUpper = ta.sma(close, BBperiod) + ta.stdev(close, BBperiod) * BBdeviations
    BBLower = ta.sma(close, BBperiod) - ta.stdev(close, BBperiod) * BBdeviations
    TrendLine: Series[float] = 0.0
    iTrend: Series[float] = 0.0
    buy: float = 0.0
    sell: float = 0.0
    BBSignal = 1 if close > BBUpper else -1 if close < BBLower else 0
    if BBSignal == 1 and UseATRfilter == cast_bool(1):
        TrendLine = low - ta.atr(ATRperiod)
        if TrendLine < TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == -1 and UseATRfilter == cast_bool(1):
        TrendLine = high + ta.atr(ATRperiod)
        if TrendLine > TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == 0 and UseATRfilter == cast_bool(1):
        TrendLine = TrendLine[1]
    if BBSignal == 1 and UseATRfilter == cast_bool(0):
        TrendLine = low
        if TrendLine < TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == -1 and UseATRfilter == cast_bool(0):
        TrendLine = high
        if TrendLine > TrendLine[1]:
            TrendLine = TrendLine[1]
    if BBSignal == 0 and UseATRfilter == cast_bool(0):
        TrendLine = TrendLine[1]
    iTrend = iTrend[1]
    if TrendLine > TrendLine[1]:
        iTrend = 1
    if TrendLine < TrendLine[1]:
        iTrend = -1
    buy = 1 if iTrend[1] == -1 and iTrend == 1 else na
    sell = 1 if iTrend[1] == 1 and iTrend == -1 else na
    plot(TrendLine, color=color.blue if iTrend > 0 else color.red, style=plot.style_line, linewidth=2, title='Trend Line')
    plotshape(TrendLine - ta.atr(8) if buy == 1 and hl == False else na, text='💣', style=shape.labelup, location=location.absolute, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    plotshape(TrendLine + ta.atr(8) if sell == 1 and hl == False else na, text='🔨', style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    alertcondition(sell == 1, title='Sell', message='Sell')
    alertcondition(buy == 1, title='Buy', message='Buy')
    alertcondition(buy == 1 or sell == 1, title='Buy/Sell', message='Buy/Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
