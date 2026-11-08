"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, na, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, PersistentSeries


@script.indicator(shorttitle='FL', title='Follow Line', overlay=True)
def main(
    ATRperiod=input.int(defval=5, title='ATR Period', minval=1),
    BBperiod=input.int(defval=21, title='Bollinger Bands Period', minval=1),
    BBdeviation=input.float(defval=1.0, title='Bollinger Bands Deviation', minval=0.1, step=0.1),
    UseATRfilter=input(defval=True, title='ATR Filter On/Off'),
    showsignals=input(title='Show Signals ', defval=True)
):
    BBUpper = ta.sma(close, BBperiod) + ta.stdev(close, BBperiod) * BBdeviation
    BBLower = ta.sma(close, BBperiod) - ta.stdev(close, BBperiod) * BBdeviation
    atrValue = ta.atr(ATRperiod)
    FollowLine: PersistentSeries[float] = na(float)
    BBSignal: Persistent[int] = 0
    if close > BBUpper:
        BBSignal = 1
    elif close < BBLower:
        BBSignal = -1
    if BBSignal == 1:
        if UseATRfilter:
            FollowLine = low - atrValue
        else:
            FollowLine = low
        if FollowLine < nz(FollowLine[1]):
            FollowLine = nz(FollowLine[1])
    if BBSignal == -1:
        if UseATRfilter:
            FollowLine = high + atrValue
        else:
            FollowLine = high
        if FollowLine > nz(FollowLine[1]):
            FollowLine = nz(FollowLine[1])
    iTrend: PersistentSeries[int] = 0
    if nz(FollowLine) > nz(FollowLine[1]):
        iTrend = 1
    elif nz(FollowLine) < nz(FollowLine[1]):
        iTrend = -1
    lineColor = color.rgb(9, 98, 232) if iTrend > 0 else color.new(color.rgb(220, 20, 60), 0)
    buy: float = 0.0
    sell: float = 0.0
    buy = 1 if iTrend[1] == -1 and iTrend == 1 else na
    sell = 1 if iTrend[1] == 1 and iTrend == -1 else na
    alertcondition(sell == 1, title='Sell', message='Follow Line Sell')
    alertcondition(buy == 1, title='Buy', message='Follow Line Buy')
    alertcondition(buy == 1 or sell == 1, title='Signal', message='Follow Line Signal')
    plot(FollowLine, color=lineColor, linewidth=2, title='Follow Line')
    plotshape(FollowLine - atrValue if buy == 1 and showsignals else na, text='BUY', style=shape.labelup, location=location.absolute, color=color.blue, textcolor=color.white, offset=0, size=size.auto)
    plotshape(FollowLine + atrValue if sell == 1 and showsignals else na, text='SELL', style=shape.labeldown, location=location.absolute, color=color.rgb(102, 15, 15), textcolor=color.white, offset=0, size=size.auto)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
