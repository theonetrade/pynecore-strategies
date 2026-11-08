"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, open, plot,
    plotshape, script, shape, ta
)


@script.indicator('SWING CALLS', shorttitle='SWING CALL', precision=1, overlay=True, na_bool=True)
def main(
    ema_value=input(5),
    sma_value=input(50),
    hl=input.int(80, title='Overbought limit of RSI', step=1),
    ll=input.int(20, title='Oversold limit of RSI', step=1)
):
    ema1 = ta.ema(close, ema_value)
    sma2 = ta.sma(close, sma_value)
    rs = ta.rsi(close, 14)
    iff_1 = color.red if high < sma2 else color.yellow
    iff_2 = color.lime if low > sma2 else iff_1
    mycolor = color.yellow if rs >= 85 or rs <= 15 else iff_2
    buyexit = ta.crossunder(rs, hl)
    sellexit = ta.crossover(rs, ll)
    plot(sma2, title='Long SMA', color=mycolor, linewidth=2)
    plotshape(buyexit, title='RSI alert Bearish', style=shape.triangledown, location=location.abovebar, color=color.new(color.teal, 0), text='↓\n ↓')
    plotshape(sellexit, title='RSI alert Bullish', style=shape.triangleup, location=location.belowbar, color=color.new(color.teal, 0), text='↑ \n ↑')
    sellcall = ta.crossover(sma2, ema1) and open > close
    buycall = ta.crossunder(sma2, ema1) and high > sma2
    plotshape(buycall, title='BuyShape', style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 0), text='B', textcolor=color.new(color.white, 0))
    plotshape(sellcall, title='SellShape', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 20), text='S', textcolor=color.new(color.black, 20))
    alertcondition(buyexit or sellexit, title='Reversal', message='Possible Reversal on Swing Signal Alert')
    alertcondition(buycall or sellcall, title='Buy/Sale Swing Signal', message='Swing Signal Entry Alert')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
