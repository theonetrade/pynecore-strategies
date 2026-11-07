"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, fill, hline, input, location, low, na,
    plot, plotshape, script, shape, strategy, ta
)
from pynecore.types import Series


@script.strategy(title='RSI W Pattern strategy', pyramiding=2, shorttitle='RSI W Pattern', overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    len=input.int(title='RSI Period', minval=1, defval=5),
    buyRsiEntry=input.int(title='look for W pattern bottom edges well below RSI level (BUY) ', minval=10, defval=65, maxval=70),
    emaL=input.int(title='Long Term EMA', minval=1, defval=50, maxval=200),
    emaS=input.int(title='Short Term EMA', minval=1, defval=20, maxval=200),
    stopLoss=input.int(title='Stop Loss %', minval=1, defval=8, maxval=10)
):
    myRsi: Series = ta.rsi(close, len)
    entryEma = ta.ema(close, 5)
    isEma20AboveEma50 = True if ta.ema(close, emaS) > ta.ema(close, emaL) else False
    rsiWp1 = myRsi > myRsi[1] and myRsi >= 30 and (myRsi[1] < myRsi[2]) and (myRsi[2] > myRsi[3]) and (myRsi[3] < myRsi[4]) and (low[1] <= low[4] or low[3] <= low[4])
    longCondition = isEma20AboveEma50 and rsiWp1 and (myRsi <= buyRsiEntry) and (myRsi >= 30)
    patternText: str = ' W '
    barcolor(color.yellow if longCondition else na)
    if longCondition:
        strategy.entry('RSI_W_LE', comment='Buy', direction=strategy.long)
    crossover_1 = ta.crossover(myRsi, 10)
    if strategy.position_size > 0 and crossover_1:
        strategy.entry('RSI_W_LE', comment='Add', direction=strategy.long)
    stopLossValue = strategy.position_avg_price - strategy.position_avg_price * stopLoss / 100
    rsiPlotColor = color.yellow if longCondition else color.purple
    plot(myRsi, title='RSI', linewidth=2, color=color.new(color.purple, 0))
    hline(40, title='Middle Line', color=color.blue, linestyle=hline.style_dashed)
    obLevel = hline(75, title='Overbought', color=color.red, linestyle=hline.style_dashed)
    osLevel = hline(30, title='Oversold', color=color.purple, linestyle=hline.style_dashed)
    fill(obLevel, osLevel, title='Background', color=color.new(color.new('#9915FF'), 90))
    plotshape(myRsi[1] if longCondition else na, offset=-1, title='W Pattern', text=patternText, style=shape.labelup, location=location.absolute, color=color.new(color.purple, 0), textcolor=color.new(color.yellow, 0))
    bgcolor(color.green if strategy.position_size > 0 else na, title='In Long Position')
    takeProfit = ta.crossover(myRsi, 75)
    if ta.crossover(myRsi, 75) and close > strategy.position_avg_price:
        strategy.close('RSI_W_LE', comment='TP Exit', qty=strategy.position_size)
    longCloseCondition = close < strategy.position_avg_price - strategy.position_avg_price * stopLoss / 100
    if longCloseCondition:
        strategy.close('RSI_W_LE', comment='SL Exit', qty=strategy.position_size)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
