"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, location, open, plot, plotshape, script, shape, strategy, ta


@script.strategy('Gold Scalping Strategy with Precise Entries', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main():
    ema50 = ta.ema(close, 50)
    ema200 = ta.ema(close, 200)
    atr = ta.atr(14)
    rsi = ta.rsi(close, 14)
    pip_target = 20 * 0.1
    bullish_engulfing = close > open and close[1] < open[1] and (close > close[1]) and (open < close[1])
    bearish_engulfing = close < open and close[1] > open[1] and (close < close[1]) and (open > close[1])
    longCondition = ema50 > ema200 and rsi >= 45 and (rsi <= 55) and bullish_engulfing and (close > ema50)
    shortCondition = ema50 < ema200 and rsi >= 45 and (rsi <= 55) and bearish_engulfing and (close < ema50)
    longStopLoss = close - atr
    shortStopLoss = close + atr
    if longCondition:
        strategy.entry('Long', strategy.long)
        strategy.exit('Take Profit/Stop Loss', 'Long', limit=close + pip_target, stop=longStopLoss)
    if shortCondition:
        strategy.entry('Short', strategy.short)
        strategy.exit('Take Profit/Stop Loss', 'Short', limit=close - pip_target, stop=shortStopLoss)
    plot(ema50, color=color.green, title='50 EMA')
    plot(ema200, color=color.red, title='200 EMA')
    plotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title='Buy Signal', text='BUY')
    plotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title='Sell Signal', text='SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
