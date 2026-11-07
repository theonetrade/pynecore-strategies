"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, fill, format, high, input, location, low, na,
    plot, plotshape, script, shape, size, strategy, string, syminfo, ta, time, timenow, timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries


@script.strategy(title='Bollinger Bands Enhanced Strategy', shorttitle='Bollinger Bands Strategy', overlay=True, format=format.inherit, pyramiding=1, calc_on_order_fills=False, calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, default_qty_value=30, initial_capital=10000, currency=currency.NONE, commission_type=strategy.commission.percent, commission_value=0.1, slippage=5, use_bar_magnifier=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    sourceUuid=input.string(title='sourceUuid:', defval='yourBotSourceUuid', group='🤖Trading Bot Settings🤖'),
    secretToken=input.string(title='secretToken:', defval='yourBotSecretToken', group='🤖Trading Bot Settings🤖'),
    lookBackPeriodStart=input.time(title='Trade Start Date/Time', defval=timestamp('2023-01-01T00:00:00'), group='🕐Trading Period Settings🕐'),
    lookBackPeriodStop=input.time(title='Trade Stop Date/Time', defval=timestamp('2025-01-01T00:00:00'), group='🕐Trading Period Settings🕐'),
    stopLossAtrNum=input.float(defval=1.75, title='ATR stop loss', step=0.25, group='📈Strategy settings📈'),
    tralingProfitActivationNum=input.float(defval=2.25, title='ATR Traling profit activation level', step=0.25, group='📈Strategy settings📈'),
    bollingerMult=input.float(2.0, minval=0.001, maxval=50, title='StdDev', group='📈Strategy settings📈')
):
    skyrexGreen: Persistent[Color] = color.new(color.new('#2ECD99'), 0)
    skyrexGray: Persistent[Color] = color.new(color.new('#F2F2F2'), 0)
    skyrexWhite: Persistent[Color] = color.new(color.new('#FFFFFF'), 0)
    stopLossLevel: Persistent[float] = na(float)
    takeProfitLevel: PersistentSeries[float] = na(float)
    tralingProfitActivationLevel: Persistent[float] = na(float)
    basis = ta.sma(close, 20)
    dev = bollingerMult * ta.stdev(close, 20)
    upper = basis + dev
    lower = basis - dev
    ATR = ta.atr(14)
    filterEMA = ta.ema(close, 200)
    stopLossLevel = strategy.position_avg_price - stopLossAtrNum * ATR
    tralingProfitActivationLevel = strategy.position_avg_price + tralingProfitActivationNum * ATR
    barssince_1 = ta.barssince(strategy.opentrades == 1 and strategy.opentrades[1] == 0)
    crossover_1 = ta.crossover(high, tralingProfitActivationLevel)
    barssince_2 = ta.barssince(crossover_1)
    if strategy.opentrades == 0 or barssince_1 < barssince_2:
        takeProfitLevel = na
    else:
        takeProfitLevel = basis
    longCondition = low > filterEMA and low <= lower
    closeCondition = close < takeProfitLevel or low <= stopLossLevel
    if longCondition and time >= lookBackPeriodStart and (time <= lookBackPeriodStop):
        strategy.entry(id='entry1', direction=strategy.long, alert_message='{\n"base": "' + syminfo.basecurrency + '",\n"quote": "' + syminfo.currency + '",\n"position": "entry1",\n"price": "' + string.tostring(close) + '",\n"sourceUuid": "' + sourceUuid + '",\n"secretToken": "' + secretToken + '",\n"timestamp": "' + string.tostring(timenow) + '"\n}')
    if closeCondition:
        strategy.close(id='entry1', immediately=True, alert_message='{\n"base": "' + syminfo.basecurrency + '",\n"quote": "' + syminfo.currency + '",\n"position": "close",\n"price": "' + string.tostring(close) + '",\n"sourceUuid": "' + sourceUuid + '",\n"secretToken": "' + secretToken + '",\n"timestamp": "' + string.tostring(timenow) + '"\n}')
    pricePlot = plot(close, title='Price', color=color.new(color.blue, 100))
    emaPlot = plot(takeProfitLevel, title='EMA', color=skyrexGreen, style=plot.style_linebr, linewidth=3)
    plot(takeProfitLevel if not na(takeProfitLevel) and na(takeProfitLevel[1]) else na, title='EMA', color=skyrexGreen, join=False, style=plot.style_circles, linewidth=6)
    fill(pricePlot, emaPlot, color=color.new(skyrexGreen, 70))
    plotshape(True if not na(takeProfitLevel) and na(takeProfitLevel[1]) else False, text='Strong Uptrend', size=size.small, offset=0, color=color.new(skyrexGreen, 0), textcolor=skyrexWhite, style=shape.triangleup, location=location.belowbar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
