"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, currency, input, na, plot, script, strategy,
    string, ta
)


@script.strategy(title='RSI of VWAP', overlay=True, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=20, initial_capital=10000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    rsiLength=input.int(14, title='RSI Length', minval=1, maxval=50),
    buyLine=input.int(70, title='RSI Buy Line', minval=30, maxval=100),
    exitLine=input.int(90, title='RSI Exit Line', minval=0, maxval=100),
    riskCapital=input.int(title='Risk % of capital', defval=10, minval=1),
    stopLoss=input.int(5, title='Stop Loss', minval=1),
    partialExit=input(True, title='Allow Partial exit / take profits')
):
    myVwap = ta.vwap
    vwapRsi = ta.rsi(ta.vwap, rsiLength)
    ema200 = ta.ema(close, 200)
    plot(ema200, title='EMA 200', color=color.new(color.orange, 25))
    plot(myVwap, title='VWAP', color=color.new(color.purple, 25))
    qty1 = strategy.equity * riskCapital / 100 / (close * stopLoss / 100)
    qty1 = strategy.equity / close if qty1 * close >= strategy.equity else qty1
    if ta.crossover(vwapRsi, buyLine) and close > ema200:
        strategy.entry(id='LE', comment='Entry', direction=strategy.long, qty=qty1)
    stopLossVal = strategy.position_avg_price * (1 - stopLoss * 0.01) if strategy.position_size >= 1 else 0.0
    plot(stopLossVal if strategy.position_size >= 1 else na, color=color.new(color.purple, 0), style=plot.style_linebr, linewidth=2, title='stop loss')
    bgcolor(color.blue if strategy.position_size >= 1 else na)
    if partialExit == True:
        if ta.crossover(vwapRsi, 99):
            strategy.close(id='LE', comment='TP points=' + string.tostring(close - strategy.position_avg_price, '####.##'), qty=strategy.position_size / 3)
    if ta.crossunder(vwapRsi, exitLine):
        strategy.close_all(comment='Exit All points=' + string.tostring(close - strategy.position_avg_price, '####.##'))
    if close < stopLossVal:
        strategy.close_all(comment='Exit points=' + string.tostring(close - strategy.position_avg_price, '####.##'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
