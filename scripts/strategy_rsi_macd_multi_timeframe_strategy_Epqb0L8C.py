"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, hline, input, na, plot, request, script, strategy, syminfo,
    ta
)

group1: str = "Plotting Options"
group2: str = "Relative Strength Index"
group3: str = "Moving Average Convergence/Divergence"


@script.strategy("RSI + MACD Multi-Timeframe Strategy", overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    plotChoice=input.string("RSI", title="Plot Selector", options=("RSI", "MACD"), group=group1),
    RSI_TIME=input.timeframe("1D", "RSI Timeframe", group=group2),
    rsiLength=input.int(14, "RSI Length", group=group2),
    rsiOB=input.int(70, "RSI Overbought Level", group=group2),
    rsiOS=input.int(30, "RSI Oversold Level", group=group2),
    MACD_TIME=input.timeframe("240", "MACD Timeframe", group=group3),
    macdFast=input.int(12, "MACD Fast Length", group=group3),
    macdSlow=input.int(26, "MACD Slow Length", group=group3),
    macdSignal=input.int(9, "MACD Signal Smoothing", group=group3)
):
    rsi1D = request.security(syminfo.tickerid, RSI_TIME, ta.rsi(close, rsiLength))
    isOB = rsi1D > rsiOB
    isOS = rsi1D < rsiOS

    macdLine, signalLine, _ = request.security(syminfo.tickerid, MACD_TIME, ta.macd(close, macdFast, macdSlow, macdSignal))
    macdCrossOver = ta.crossover(macdLine, signalLine)
    macdCrossUnder = ta.crossunder(macdLine, signalLine)

    longCondition = isOS and macdCrossOver
    if longCondition:
        strategy.entry('Long', strategy.long)

    longExit = isOB and macdCrossUnder
    if longExit:
        strategy.close('Long')

    showRSI = plotChoice == 'RSI'
    showMACD = plotChoice == 'MACD'

    plot(rsi1D if showRSI else na, title='RSI (1D)', color=color.blue)
    hline(rsiOB if showRSI else na, 'Overbought', color=color.red)
    hline(rsiOS if showRSI else na, 'Oversold', color=color.green)

    plot(macdLine if showMACD else na, title='MACD Line (4H)', color=color.orange)
    plot(signalLine if showMACD else na, title='Signal Line (4H)', color=color.purple)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
