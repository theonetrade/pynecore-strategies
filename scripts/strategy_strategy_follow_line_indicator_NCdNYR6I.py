"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, currency, high, input, location, low, na, plot, plotshape,
    script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title=' Strategy Follow Line Indicator ', shorttitle='S-FLI', overlay=True, precision=8, calc_on_order_fills=True, calc_on_every_tick=True, backtest_fill_limits_assumption=0, default_qty_type=strategy.fixed, default_qty_value=2, initial_capital=10000, pyramiding=1, currency=currency.USD, linktoseries=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    backTestSectionFrom=input(title='═══════════════ From ═══════════════', defval=True),
    FromMonth=input.int(defval=1, title='Month', minval=1),
    FromDay=input.int(defval=1, title='Day', minval=1),
    FromYear=input.int(defval=2014, title='Year', minval=2000),
    backTestSectionTo=input(title='════════════════ To ════════════════', defval=True),
    ToMonth=input.int(defval=31, title='Month', minval=1),
    ToDay=input.int(defval=12, title='Day', minval=1),
    ToYear=input.int(defval=9999, title='Year', minval=2000),
    Config=input(title='══════════════ Config ══════════════', defval=True),
    BBperiod=input.int(defval=21, title='BB Period', minval=1),
    BBdeviations=input.float(defval=1.0, title='BB Deviations', minval=0.1, step=0.05),
    UseATRfilter=input(defval=True, title='ATR Filter'),
    ATRperiod=input.int(defval=5, title='ATR Period', minval=1),
    hl=input(defval=False, title='Hide Labels')
):
    def backTestPeriod():
        return time > timestamp(FromYear, FromMonth, FromDay, 0, 0) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59)

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
    if backTestPeriod():
        if buy == 1:
            strategy.entry('long', strategy.long, 1)
        if sell == 1:
            strategy.entry('short', strategy.short, 1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)