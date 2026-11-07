"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barstate, bgcolor, close, color, high, hline, input, location,
    low, math, na, plot, plotshape, request, script, shape, size, strategy, syminfo, ta, time,
    time_tradingday, timeframe, timestamp
)
from pynecore.types import Series


@script.strategy('TICK strategy for SPY', overlay=False, pyramiding=3, initial_capital=5000, commission_type=strategy.commission.cash_per_contract, commission_value=0.0625, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    startY=input(title='Start Year', defval=2011, group='Trading window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Trading window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Trading window'),
    finishY=input(title='Finish Year', defval=2050, group='Trading window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Trading window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Trading window'),
    trade_options=input.bool(defval=True, title='Trading Options only', group='Trading Options'),
    option_amt=input.int(defval=10, title='# of options per trade', group='Trading Options'),
    option_multiplier=input.float(0.007, title='Multiplier for trading options (adjust to approx. options P&L)', step=0.001, group='Trading Options'),
    reinvest=input.bool(defval=False, title='Reinvest profit', group='Trading Options'),
    reinvest_percent=input.float(defval=20, title='Reinvest percentage', group='Trading Options'),
    daily_max=input.float(1200, title='Stop trading after Max daily profit', group='Trading Options'),
    atrlen=input.int(14, minval=1, title='ATR period', group='Daily ATR'),
    iPercent=input.float(5, minval=1, maxval=100, step=0.1, title='% ATR to use for SL / PT', group='Daily ATR'),
    vix_thres=input.float(20.0, 'VIX Threshold for entry', step=0.5, group='VIX Volatility Index'),
    malen1=input.int(5, title='Fast EMA period', group='TICK Indicator'),
    malen2=input.int(21, title='Slow EMA period', group='TICK Indicator'),
    malen3=input.int(21, title='Hull MA period', group='TICK Indicator'),
    malen4=input.int(5, title='Hull MA Smoothing', group='TICK Indicator'),
    lbR=input(title='Pivot Lookback Right', defval=0, group='TICK Divergence'),
    lbL=input(title='Pivot Lookback Left', defval=2, group='TICK Divergence'),
    rangeUpper=input(title='Max of Lookback Range', defval=60, group='TICK Divergence'),
    rangeLower=input(title='Min of Lookback Range', defval=5, group='TICK Divergence'),
    plotBull=input(title='Plot Bullish', defval=True, group='TICK Divergence'),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=True, group='TICK Divergence'),
    plotBear=input(title='Plot Bearish', defval=True, group='TICK Divergence'),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False, group='TICK Divergence'),
    rsi_len=input.int(14, minval=1, title='RSI Length', group='RSI'),
    rsi_ma_len=input.int(1, minval=1, title='RSI Signal Length', group='RSI'),
    rsi_thres=input.int(20, 'RSI Overbought/Oversold levels +/- from 50', group='RSI'),
    emalen1=input.int(8, minval=1, title='Fast EMA', group='Moving Averages'),
    min_hold=input.int(6, 'Minimum bars to hold order', group='Trading Options')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    t1 = time(timeframe.period, '0945-1545:23456')
    window = True if time >= timestart and time <= timefinish and cast_bool(t1) else False
    t2 = time(timeframe.period, '0930-1555:23456')
    window2 = True if time >= timestart and time <= timefinish and cast_bool(t2) else False
    percentage = iPercent * 0.01
    datr = request.security(syminfo.tickerid, '1D', ta.rma(ta.tr, atrlen))
    datrp = datr * percentage
    VIX = request.security('VIX', timeframe.period, close)
    tickC: Series = request.security('USI:TICK', timeframe.period, close)
    tickAVG: Series = ta.ema(tickC, malen1)
    tickAVG_L = ta.ema(tickC, malen2)
    def f_hma(_src, _length):
        _return = ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))
        return _return

    tickHMA: Series = f_hma(tickC, malen3)
    tickHMA_MA = ta.ema(tickHMA, malen4)
    tick_bull = tickAVG > tickAVG[1]
    tick_bear = tickAVG < tickAVG[1]
    plot(tickC, title='TICK', color=color.new(color.white, 30), style=plot.style_line, linewidth=1)
    plot(tickAVG, title='TICK 9 EMA', color=color.yellow, style=plot.style_line, linewidth=1)
    plot(tickAVG_L, title='TICK 21 EMA', color=color.new(color.red, 70), style=plot.style_line, linewidth=1)
    plot(tickHMA, title='TICK 21 HMA', color=color.blue, style=plot.style_line, linewidth=2)
    plot(tickHMA_MA, title='TICK HMA Smoothed', color=color.purple, style=plot.style_line, linewidth=2)
    hline(0, color=color.white, linewidth=1, linestyle=hline.style_solid)
    hline(1000, color=color.green, linestyle=hline.style_solid, linewidth=2)
    hline(500, color=color.gray, linestyle=hline.style_dashed)
    hline(-1000, color=color.red, linestyle=hline.style_solid, linewidth=2)
    hline(-500, color=color.gray, linestyle=hline.style_dashed)
    plotshape(ta.crossunder(tickHMA, tickHMA_MA), 'Cross down', color=color.red, style=shape.triangledown, location=location.top, size=size.small)
    plotshape(ta.crossover(tickHMA, tickHMA_MA), 'Cross up', color=color.green, style=shape.triangleup, location=location.bottom, size=size.small)
    tick_revUp = tickHMA[2] >= tickHMA[1] and tickHMA > tickHMA[1]
    tick_revDown = tickHMA[2] <= tickHMA[1] and tickHMA < tickHMA[1]
    plotshape(tick_revDown, 'Cross down', color=color.orange, style=shape.triangledown, location=location.top, size=size.tiny)
    plotshape(tick_revUp, 'Cross up', color=color.blue, style=shape.triangleup, location=location.bottom, size=size.tiny)
    bgcolor(color.green if tickAVG_L > 0 else color.red)
    bgcolor(color.green if tickC > 499 else na)
    bgcolor(color.red if tickC < -499 else na)
    bgcolor(color.green if tickC > 999 else na)
    bgcolor(color.red if tickC < -999 else na)
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    plFound: Series = False if na(ta.pivotlow(tickC, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(tickC, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = tickC[lbR] > ta.valuewhen(plFound, tickC[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound
    plot(tickC[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(tickC[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = tickC[lbR] < ta.valuewhen(plFound, tickC[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound
    plot(tickC[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(tickC[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    oscLH = tickC[lbR] < ta.valuewhen(phFound, tickC[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound
    plot(tickC[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(tickC[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = tickC[lbR] > ta.valuewhen(phFound, tickC[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound
    plot(tickC[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(tickC[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    src = close
    rsi_up = ta.rma(math.max(ta.change(src), 0), rsi_len)
    rsi_down = ta.rma(-math.min(ta.change(src), 0), rsi_len)
    rsi = 100 if rsi_down == 0 else 0 if rsi_up == 0 else 100 - 100 / (1 + rsi_up / rsi_down)
    rsi_ma = ta.sma(rsi, rsi_ma_len)
    rsi_avg: Series = math.avg(rsi, rsi_ma)
    rsi_bull = rsi_avg > rsi_avg[1]
    rsi_bear = rsi_avg < rsi_avg[1]
    ema1 = ta.ema(src, emalen1)
    profit = strategy.netprofit
    trade_amount = math.floor(strategy.initial_capital / close)
    def BSLE():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    if trade_options:
        if strategy.netprofit > 0 and reinvest:
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * (option_amt + math.floor(profit * reinvest_percent * 0.01 / strategy.initial_capital * 10))
        else:
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * option_amt
    daily_profit: float = 0.0
    __loop_0__ = pine_loop(0, 1)
    while __loop_0__.step(strategy.closedtrades - 1):
        i = __loop_0__.value
        if strategy.closedtrades.exit_time(i) > time_tradingday:
            daily_profit = daily_profit + strategy.closedtrades.profit(i)
    pause_trade1 = daily_profit > daily_max
    trade_amount = 1 if pause_trade1 else trade_amount
    L_entry0 = ta.crossover(tickHMA, tickHMA_MA) and rsi_avg > 50 and (rsi < 50 + rsi_thres) and (VIX > vix_thres) and (tickAVG > 0)
    S_entry0 = ta.crossunder(tickHMA, tickHMA_MA) and rsi_avg < 50 and (rsi > 50 - rsi_thres) and (VIX > vix_thres) and (tickAVG < 0)
    L_entry1 = L_entry0 and close > ema1
    S_entry1 = S_entry0 and close < ema1
    barssince_1 = ta.barssince(L_entry0)
    L_entry2 = strategy.opentrades == 0 and barssince_1 < 2 and (close > ema1)
    barssince_2 = ta.barssince(S_entry0)
    S_entry2 = strategy.opentrades == 0 and barssince_2 < 2 and (close < ema1)
    long_SL: Series = low[1] - datrp
    short_SL: Series = high[1] + datrp
    if strategy.opentrades > 0:
        long_SL = math.min(long_SL[BSLE()], low[1] - datrp)
        short_SL = math.max(short_SL[BSLE()], high[1] + datrp)
    L_exit1 = tickHMA < tickHMA_MA and rsi_bear
    S_exit1 = tickHMA > tickHMA_MA and rsi_bull
    L_exit2 = bearCond
    S_exit2 = bullCond
    trade_amount_long = trade_amount
    trade_amount_short = trade_amount
    if L_entry1 and window and barstate.isconfirmed:
        strategy.entry('Long', strategy.long, trade_amount_long)
    if S_entry1 and window and barstate.isconfirmed:
        strategy.entry('Short', strategy.short, trade_amount_short)
    if L_entry2 and (not L_entry1) and window and barstate.isconfirmed:
        strategy.entry('Long2', strategy.long, trade_amount_long, comment='Long 2')
    if S_entry2 and (not S_entry2) and window and barstate.isconfirmed:
        strategy.entry('Short2', strategy.short, trade_amount_short, comment='Short 2')
    if BSLE() > min_hold and window2 and barstate.isconfirmed:
        strategy.exit('Exit', 'Long', stop=long_SL, comment='Stopped out')
        strategy.exit('Exit', 'Short', stop=short_SL, comment='Stopped out')
        if L_exit1 or L_exit2:
            strategy.close('Long')
        if S_exit1 or S_exit2:
            strategy.close('Short')
    if window2 and barstate.isconfirmed:
        strategy.exit('Exit2', 'Long2', stop=long_SL, comment='Stopped out')
        strategy.exit('Exit2', 'Short2', stop=short_SL, comment='Stopped out')
        if L_exit1 or L_exit2:
            strategy.close('Long2')
        if S_exit1 or S_exit2:
            strategy.close('Short2')
    if cast_bool(time(timeframe.period, '1550-1600:23456')):
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
