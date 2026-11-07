"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, fill, format, high, hlc3, input, location, low,
    na, plot, plotshape, script, shape, size, strategy, string, syminfo, ta, time, timenow,
    timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries


@script.strategy(title="Triple CCI Strategy MFI Confirmed [Skyrexio]", shorttitle="Triple CCI", overlay=True, format=format.inherit, pyramiding=1, calc_on_order_fills=False, calc_on_every_tick=False, default_qty_type=strategy.percent_of_equity, default_qty_value=50, initial_capital=10000, currency=currency.NONE, commission_type=strategy.commission.percent, commission_value=0.1, slippage=5, use_bar_magnifier=True)
def main(
    sourceUuid=input.string(title="sourceUuid:", defval="yourBotSourceUuid", group="🤖Trading Bot Settings🤖"),
    secretToken=input.string(title="secretToken:", defval="yourBotSecretToken", group="🤖Trading Bot Settings🤖"),
    lookBackPeriodStart=input.time(title="Trade Start Date/Time", defval=timestamp('2023-01-01T00:00:00'), group="🕐Trading Period Settings🕐"),
    lookBackPeriodStop=input.time(title="Trade Stop Date/Time", defval=timestamp('2025-01-01T00:00:00'), group="🕐Trading Period Settings🕐"),
    stopLossAtrNum=input.float(defval=1.75, title="ATR Stop Loss", step=0.25, group="📈Strategy settings📈"),
    tralingProfitActivationNum=input.float(defval=2.25, title="ATR Traling Profit Activation Level", step=0.25, group="📈Strategy settings📈"),
    cciFastPeriod=input.int(title="CCI Fast Length", defval=14, minval=1, group="📈Strategy settings📈"),
    cciMiddlePeriod=input.int(title="CCI Middle Length", defval=25, minval=1, group="📈Strategy settings📈"),
    cciSlowPeriod=input.int(title="CCI Slow Length", defval=50, minval=1, group="📈Strategy settings📈"),
    MFIlength=input.int(title="MFI Length", defval=14, minval=1, maxval=2000, group="📈Strategy settings📈"),
    EMaLength=input.int(50, minval=10, title="EMA Length", group="📈Strategy settings📈"),
    trailingEmaLength=input.int(20, minval=10, title="Trailing EMA Length", group="📈Strategy settings📈")
):
    skyrexGreen: Persistent[Color] = color.new(color.new('#2ECD99'), 0)
    skyrexGray: Persistent[Color] = color.new(color.new('#F2F2F2'), 0)
    skyrexWhite: Persistent[Color] = color.new(color.new('#FFFFFF'), 0)

    stopLossLevel: Persistent[float] = na(float)
    takeProfitLevel: PersistentSeries[float] = na(float)
    tralingProfitActivationLevel: PersistentSeries[float] = na(float)

    fastCci = ta.cci(hlc3, cciFastPeriod)
    middleCci = ta.cci(hlc3, cciMiddlePeriod)
    slowCci = ta.cci(hlc3, cciSlowPeriod)

    mfi = ta.mfi(hlc3, MFIlength)

    ATR = ta.atr(14)

    trailingEma = ta.ema(close, trailingEmaLength)

    ema = ta.ema(close, EMaLength)

    stopLossLevel = strategy.position_avg_price - stopLossAtrNum * ATR

    tralingProfitActivationLevel = strategy.position_avg_price + tralingProfitActivationNum * ATR

    condition1 = ta.barssince(strategy.opentrades == 1 and strategy.opentrades[1] == 0) < ta.barssince((high[1] < tralingProfitActivationLevel[1] or na(tralingProfitActivationLevel[1])) and high > tralingProfitActivationLevel)
    condition2 = na(ta.barssince((high[1] < tralingProfitActivationLevel[1] or na(tralingProfitActivationLevel[1])) and high > tralingProfitActivationLevel))
    if strategy.opentrades == 0 or condition1 or condition2:
        takeProfitLevel = na
    else:
        takeProfitLevel = trailingEma

    longCondition = ta.crossover(fastCci, 0) and close > ema and (middleCci > 0) and (slowCci > 0) and (mfi > 50)

    closeCondition = close < takeProfitLevel or low <= stopLossLevel

    if longCondition and time >= lookBackPeriodStart and (time <= lookBackPeriodStop):
        strategy.entry(id='entry1', direction=strategy.long, alert_message='{\n"base": "' + syminfo.basecurrency + '",\n"quote": "' + syminfo.currency + '",\n"position": "entry1",\n"price": "' + string.tostring(close) + '",\n"sourceUuid": "' + sourceUuid + '",\n"secretToken": "' + secretToken + '",\n"timestamp": "' + string.tostring(timenow) + '"\n}')

    if closeCondition:
        strategy.close(id='entry1', immediately=True, alert_message='{\n"base": "' + syminfo.basecurrency + '",\n"quote": "' + syminfo.currency + '",\n"position": "close",\n"price": "' + string.tostring(close) + '",\n"sourceUuid": "' + sourceUuid + '",\n"secretToken": "' + secretToken + '",\n"timestamp": "' + string.tostring(timenow) + '"\n}')

    pricePlot = plot(close, title='Price', color=color.new(color.blue, 100))
    emaPlot = plot(takeProfitLevel, title='EMA', color=skyrexGreen, style=plot.style_linebr, linewidth=3)
    plot(takeProfitLevel if not na(takeProfitLevel) and na(takeProfitLevel[1]) else na, title='EMA', color=skyrexGreen, join=False, style=plot.style_circles, linewidth=6)
    fill(pricePlot, emaPlot, color=color.new(skyrexGreen, 70))
    plotshape(True if not na(takeProfitLevel) and na(takeProfitLevel[1]) else False, text='Trailing Activated', size=size.small, offset=0, color=color.new(skyrexGreen, 0), textcolor=skyrexWhite, style=shape.triangleup, location=location.belowbar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
