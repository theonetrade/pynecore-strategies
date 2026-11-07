"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, bar_index, close, color, dayofmonth, high, hour,
    input, last_bar_index, location, low, na, plot, plotshape, position, script, shape, strategy,
    string, ta, table, volume
)
from pynecore.types import Persistent, Table


@script.strategy("ThinkTech AI Signals", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    riskRewardRatio=input.float(title="Risk/Reward Ratio", defval=2.0, minval=1.0, step=0.1),
    liquidity_period=input.int(20, title="Liquidity Base Period"),
    atr_length=input.int(14, title="ATR Length"),
    atr_threshold=input.float(0.3, title="ATR Breakout Threshold"),
    take_profit_mult=input.float(0.25, title="Take-Profit Multiplier"),
    stop_loss_mult=input.float(0.75, title="Stop-Loss Multiplier"),
    vol_filter=input.bool(True, title="Enable Volume Filter"),
    session_filter=input.bool(True, title="Limit to Trading Session"),
    atrMultiplier=input.float(title="ATR Multiplier for Stop Loss", defval=1.5, minval=0.1, step=0.1),
    retestCushionLong=input.float(title="Retest Cushion Factor for BUY", defval=1.0, minval=1.0, step=0.001),
    retestCushionShort=input.float(title="Retest Cushion Factor for SELL", defval=1.0, minval=0.0, maxval=1.0, step=0.001),
    useTrendFilter=input.bool(title="Use 50 EMA Trend Filter", defval=True),
    useRSIFilter=input.bool(title="Use RSI Filter", defval=False),
    rsiPeriod=input.int(title="RSI Period", defval=14, minval=1),
    rsiOversold=input.float(title="RSI Oversold Level", defval=30.0, minval=1, maxval=50),
    rsiOverbought=input.float(title="RSI Overbought Level", defval=70.0, minval=50, maxval=100),
    showLiquidityLines=input.bool(True, title="Show Liquidity Lines"),
    showFirstCandleLines=input.bool(True, title="Show First Candle Level Lines")
):
    price = close
    atr = ta.atr(atr_length)
    vol_condition = volume > ta.sma(volume, 20)

    liquidity_base = ta.lowest(low, liquidity_period)
    apex = ta.highest(high, liquidity_period)

    hh = ta.highest(high, 30)
    ll = ta.lowest(low, 30)

    take_profit: Persistent[float] = na(float)
    stop_loss: Persistent[float] = na(float)
    in_trade: Persistent[bool] = False
    win_count: Persistent[int] = 0
    loss_count: Persistent[int] = 0

    breakout_up = price > liquidity_base + atr * atr_threshold
    point_of_release = ta.crossover(price, liquidity_base) and breakout_up
    retest_buy = price > liquidity_base and price < hh and (not in_trade)

    session_condition = hour >= 9 and hour <= 12 or not session_filter

    if (point_of_release or retest_buy) and (vol_condition or not vol_filter) and session_condition:
        strategy.entry('Buy', strategy.long)
        take_profit = price + atr * take_profit_mult
        stop_loss = liquidity_base - atr * stop_loss_mult
        in_trade = True
        alert('Buy Signal - Price: ' + string.tostring(price), alert.freq_once_per_bar)

    breakout_down = price < apex - atr * atr_threshold
    clean_break = ta.crossunder(price, apex) and breakout_down
    retest_sell = price < apex and price > ll and (not in_trade)

    if (clean_break or retest_sell) and (vol_condition or not vol_filter) and session_condition:
        strategy.entry('Sell', strategy.short)
        take_profit = price - atr * take_profit_mult
        stop_loss = apex + atr * stop_loss_mult
        in_trade = True
        alert('Sell Signal - Price: ' + string.tostring(price), alert.freq_once_per_bar)

    if strategy.position_size > 0:
        if price >= take_profit:
            strategy.close('Buy', comment='Take Profit')
            win_count += 1
            in_trade = False
        if price <= stop_loss:
            strategy.close('Buy', comment='Stop Loss')
            loss_count += 1
            in_trade = False

    if strategy.position_size < 0:
        if price <= take_profit:
            strategy.close('Sell', comment='Take Profit')
            win_count += 1
            in_trade = False
        if price >= stop_loss:
            strategy.close('Sell', comment='Stop Loss')
            loss_count += 1
            in_trade = False

    plot(liquidity_base if showLiquidityLines else na, color=color.green, title='Liquidity Base (Support)')
    plot(apex if showLiquidityLines else na, color=color.red, title='Apex (Resistance)')

    plotshape(series=point_of_release, location=location.belowbar, color=color.green, style=shape.triangleup, title='Buy Signal')
    plotshape(series=clean_break, location=location.abovebar, color=color.red, style=shape.triangledown, title='Sell Signal')

    t: Persistent[Table] = table.new(position.top_right, 1, 2)
    if bar_index == last_bar_index:
        table.cell(t, 0, 0, 'Wins: ' + string.tostring(win_count), bgcolor=color.new(color.green, 80))
        table.cell(t, 0, 1, 'Losses: ' + string.tostring(loss_count), bgcolor=color.new(color.red, 80))

    alertcondition(point_of_release, title='Buy Alert', message='Buy Signal Triggered')
    alertcondition(clean_break, title='Sell Alert', message='Sell Signal Triggered')
    lastClosedTrades: Persistent[int] = 0
    exitSignal: Persistent[bool] = False
    if strategy.closedtrades > lastClosedTrades:
        exitSignal = True
        lastClosedTrades = strategy.closedtrades
    alertcondition(exitSignal, title='EXIT Signal', message='EXIT signal triggered: Trade has closed (TP or SL reached).')

    newDay = dayofmonth != dayofmonth[1]
    fHigh: Persistent[float] = na(float)
    fLow: Persistent[float] = na(float)
    firstCandleCaptured: Persistent[bool] = False
    if newDay:
        fHigh = high
        fLow = low
        firstCandleCaptured = True

    ema50 = ta.ema(close, 50)
    longFilter = not useTrendFilter or close > ema50
    shortFilter = not useTrendFilter or close < ema50

    atrValue = ta.atr(14)
    stopLossBuffer = atrValue * atrMultiplier

    rsiValue = ta.rsi(close, rsiPeriod)

    buyBreakout = firstCandleCaptured and ta.crossover(close, fHigh)
    sellBreakdown = firstCandleCaptured and ta.crossunder(close, fLow)

    buyRetest = firstCandleCaptured and low <= fHigh and (close > fHigh)
    sellRetest = firstCandleCaptured and high >= fLow and (close < fLow)

    buySignal = buyBreakout and buyRetest and longFilter and (strategy.position_size == 0) and (not useRSIFilter or rsiValue < rsiOversold)
    sellSignal = sellBreakdown and sellRetest and shortFilter and (strategy.position_size == 0) and (not useRSIFilter or rsiValue > rsiOverbought)

    candleRange = fHigh - fLow
    stopLossBuy = fLow - stopLossBuffer
    takeProfitBuy = fHigh + candleRange * riskRewardRatio
    stopLossSell = fHigh + stopLossBuffer
    takeProfitSell = fLow - candleRange * riskRewardRatio

    if buySignal:
        strategy.entry('BUY', strategy.long)
        strategy.exit('TP/SL BUY', 'BUY', stop=stopLossBuy, limit=takeProfitBuy)

    if sellSignal:
        strategy.entry('SELL', strategy.short)
        strategy.exit('TP/SL SELL', 'SELL', stop=stopLossSell, limit=takeProfitSell)

    plot(fHigh if showFirstCandleLines and firstCandleCaptured else na, title='First Candle High', color=color.blue, linewidth=2)
    plot(fLow if showFirstCandleLines and firstCandleCaptured else na, title='First Candle Low', color=color.red, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
