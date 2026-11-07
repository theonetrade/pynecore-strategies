"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bgcolor, close, color, currency, hlc3, hline, input, na, open, plot,
    script, strategy, ta
)
from pynecore.types import Series


@script.strategy(title='VWAP and RSI strategy [EEMANI] v2', overlay=False, pyramiding=2, default_qty_type=strategy.fixed, initial_capital=10000, currency=currency.USD, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    longEMA=input.int(200, title='Long EMA', minval=1),
    shortEMA=input.int(50, title='short EMA', minval=1),
    rsi1=input.int(3, title='RSI Period', minval=1),
    rsi_buy_line=input.int(15, title='RSI Buy Line', minval=5),
    rsi_sell_line=input.int(90, title='RSI Sell Line', minval=50),
    add_on_divergence=input(True, title='Add on RSI divergence'),
    stopLoss=input.int(title='Stop Loss%', defval=5, minval=1)
):
    barCount: Series[int] = 0
    longEMAval = ta.ema(close, longEMA)
    shortEMAval = ta.ema(close, shortEMA)
    rsiVal: Series = ta.rsi(close, rsi1)
    vwapVal = ta.vwap(hlc3)
    plot_rsi = plot(rsiVal, title='RSI', color=color.new(color.purple, 0), linewidth=1)
    hline(rsi_buy_line, color=color.green, title='Buy Line', linewidth=2, linestyle=hline.style_dashed)
    hline(rsi_sell_line, color=color.purple, title='Sell Line', linewidth=2, linestyle=hline.style_dashed)
    rsiDipped: bool = False
    for i in pine_range(1, 10, 1):
        rsiDipped = rsiDipped or rsiVal[i] < rsi_buy_line
    longCondition = shortEMAval > longEMAval and close > open and (close > vwapVal) and (open > vwapVal) and rsiDipped
    if longCondition and strategy.position_size < 1:
        strategy.entry(id='VWAP_RSI LE', comment='VR LE', direction=strategy.long)
    barCount = barCount[1] + 1 if strategy.position_size > 0 else 0
    addCondition = add_on_divergence and barCount[1] > 1 and (strategy.position_size >= 1) and (close <= close[barCount[1]]) and (rsiVal > rsiVal[barCount + 1]) and (close > open) and (close > vwapVal)
    if addCondition:
        strategy.entry(id='VWAP_RSI LE', comment='Add ', direction=strategy.long)
    bgcolor(color.green if add_on_divergence and addCondition else na)
    if ta.crossunder(rsiVal, 90):
        strategy.close(id='VWAP_RSI LE', comment='TP Exit')
    stopLossVal = strategy.position_avg_price - strategy.position_avg_price * stopLoss * 0.01
    if close < stopLossVal:
        strategy.close(id='VWAP_RSI LE', comment='SL Exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
