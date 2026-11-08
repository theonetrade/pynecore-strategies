"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, bgcolor, close, color, input, location, na,
    open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, Series


@script.indicator('[@btc_charlie] Trader XO Macro Trend Scanner', overlay=True, na_bool=True)
def main(
    src: Series[float] = input(close, title='OHLC Type'),
    i_fastEMA=input(12, title='Fast EMA'),
    i_slowEMA=input(25, title='Slow EMA'),
    i_defEMA=input(25, title='Consolidated EMA'),
    i_bothEMAs=input(title='Show Both EMAs', defval=True),
    smoothK=input.int(3, 'K', minval=1),
    smoothD=input.int(3, 'D', minval=1),
    lengthRSI=input.int(14, 'RSI Length', minval=1),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1),
    bandno0=input.int(80, minval=1, title='Upper Band', group='Bands (change this instead of length in Style for Stoch RSI colour to work properly)'),
    bandno2=input.int(50, minval=1, title='Middle Band', group='Bands (change this instead of length in Style for Stoch RSI colour to work properly)'),
    bandno1=input.int(20, minval=1, title='Lower Band', group='Bands (change this instead of length in Style for Stoch RSI colour to work properly)'),
    crossoverAlertBgColourMidOnOff=input.bool(title='Crossover Alert Background Colour (Middle Level) [ON/OFF]', group='Crossover Alerts', defval=False),
    crossoverAlertBgColourOBOSOnOff=input.bool(title='Crossover Alert Background Colour (OB/OS Level) [ON/OFF]', group='Crossover Alerts', defval=False),
    crossoverAlertBgColourGreaterThanOnOff=input.bool(title='Crossover Alert >input [ON/OFF]', group='Crossover Alerts', defval=False),
    crossoverAlertBgColourLessThanOnOff=input.bool(title='Crossover Alert <input [ON/OFF]', group='Crossover Alerts', defval=False),
    maTypeChoice=input.string('EMA', title='MA Type', group='Moving Average', options=('EMA', 'WMA', 'SMA', 'None')),
    maSrc: Series[float] = input.source(close, title='MA Source', group='Moving Average'),
    maLen=input.int(200, minval=1, title='MA Length', group='Moving Average')
):
    ok: Persistent[int] = 0
    countBuy: Persistent[int] = 0
    countSell: Persistent[int] = 0
    v_fastEMA = ta.ema(src, i_fastEMA)
    v_slowEMA = ta.ema(src, i_slowEMA)
    v_biasEMA = ta.ema(src, i_defEMA)
    emaColor = color.green if v_fastEMA > v_slowEMA else color.red if v_fastEMA < v_slowEMA else color.new('#FF530D')
    plot(na if i_bothEMAs else v_biasEMA, color=emaColor, linewidth=3, title='Consolidated EMA')
    plot(v_fastEMA if i_bothEMAs else na, title='Fast EMA', color=emaColor)
    plot(v_slowEMA if i_bothEMAs else na, title='Slow EMA', color=emaColor)
    buy: Series = v_fastEMA > v_slowEMA
    sell: Series = v_fastEMA < v_slowEMA
    if buy:
        countBuy = countBuy + 1
    if buy:
        countSell = 0
    if sell:
        countSell = countSell + 1
    if sell:
        countBuy = 0
    buysignal = countBuy < 2 and countBuy > 0 and (countSell < 1) and buy and (not buy[1])
    sellsignal = countSell > 0 and countSell < 2 and (countBuy < 1) and sell and (not sell[1])
    barcolor(color.green if buysignal else na)
    barcolor(color.red if sellsignal else na)
    plotshape(buysignal, title='Bull', text='Bull', style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.black, 0), size=size.tiny)
    plotshape(sellsignal, title='Bear', text='Bear', style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.black, 0), size=size.tiny)
    bull = countBuy > 1
    bear = countSell > 1
    barcolor(color.green if bull else na)
    barcolor(color.red if bear else na)
    alertcondition(ta.crossover(v_fastEMA, v_slowEMA), title='Bullish EMA Cross', message='Bullish EMA crossover')
    alertcondition(ta.crossunder(v_fastEMA, v_slowEMA), title='Bearish EMA Cross', message='Bearish EMA Crossover')
    rsi1 = ta.rsi(src, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    __block_result__ = na
    if maTypeChoice == 'EMA':
        __block_result__ = ta.ema(maSrc, maLen)
    elif maTypeChoice == 'WMA':
        __block_result__ = ta.wma(maSrc, maLen)
    elif maTypeChoice == 'SMA':
        __block_result__ = ta.sma(maSrc, maLen)
    else:
        __block_result__ = 0
    maValue = __block_result__
    crossupCHECK = maTypeChoice == 'None' or (open > maValue and maTypeChoice != 'None')
    crossdownCHECK = maTypeChoice == 'None' or (open < maValue and maTypeChoice != 'None')
    crossover_1 = ta.crossover(k, d)
    crossupalert = crossupCHECK and crossover_1 and (k < bandno2 or d < bandno2)
    crossunder_1 = ta.crossunder(k, d)
    crossdownalert = crossdownCHECK and crossunder_1 and (k > bandno2 or d > bandno2)
    crossover_2 = ta.crossover(k, d)
    crossupOSalert = crossupCHECK and crossover_2 and (k < bandno1 or d < bandno1)
    crossunder_2 = ta.crossunder(k, d)
    crossdownOBalert = crossdownCHECK and crossunder_2 and (k > bandno0 or d > bandno0)
    aboveBandalert = ta.crossunder(k, bandno0)
    belowBandalert = ta.crossover(k, bandno1)
    bgcolor(color=color.new('#4CAF50') if crossupalert and crossoverAlertBgColourMidOnOff else color.new('#FF0000') if crossdownalert and crossoverAlertBgColourMidOnOff else na, title='Crossover Alert Background Colour (Middle Level)')
    bgcolor(color=color.new('#FBC02D') if crossupOSalert and crossoverAlertBgColourOBOSOnOff else color.new('#000000') if crossdownOBalert and crossoverAlertBgColourOBOSOnOff else na, title='Crossover Alert Background Colour (OB/OS Level)')
    bgcolor(color=color.new('#FF0014') if aboveBandalert and crossoverAlertBgColourGreaterThanOnOff else color.new('#FF0000') if crossdownalert and crossoverAlertBgColourMidOnOff else na, title='Crossover Alert - K > Upper level')
    bgcolor(color=color.new('#4CAF50') if belowBandalert and crossoverAlertBgColourLessThanOnOff else color.new('#FF0000') if crossdownalert and crossoverAlertBgColourMidOnOff else na, title='Crossover Alert - K < Lower level')
    alertcondition(crossupalert or crossdownalert, title='Stoch RSI Crossover', message='STOCH RSI CROSSOVER')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
