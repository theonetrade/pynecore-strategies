"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, input, location, low, math, na, plot,
    plotshape, script, shape, size, strategy, ta
)
from pynecore.types import PersistentSeries, Series

SystemName: str = 'BEST Trailing Profit Strategy'


@script.strategy(title=SystemName, shorttitle=SystemName, overlay=True, pyramiding=0, default_qty_value=100, precision=7, currency=currency.USD, commission_value=0.2, commission_type=strategy.commission.percent, initial_capital=10000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(defval=close, title='Source'),
    slowLength=input.int(20, 'Fast Length', minval=2, step=1),
    fastLength=input.int(50, 'Fast Length', minval=2, step=1),
    useTP=input(True, 'Use take profit'),
    __input_4__=input.float(1.0, 'Trailing Profit (%)', minval=0, step=0.5),
    use_TP_Trigger=input(True, 'Use Take Profit Trigger'),
    __input_6__=input.float(3.0, 'Take Profit Trigger (%)', minval=0, step=0.5)
):
    TradeId: str = 'BEST'
    InitCapital: int = 1000000
    InitPosition: int = 100
    InitCommission: float = 0.075
    InitPyramidMax: int = 1
    CalcOnorderFills: bool = True
    CalcOnTick: bool = True
    DefaultQtyType = strategy.fixed
    DefaultQtyValue = strategy.fixed
    Precision: int = 2
    Overlay: bool = True
    fastSMA = ta.sma(src, slowLength)
    slowSMA = ta.sma(src, fastLength)
    enterLong = ta.crossover(fastSMA, slowSMA)
    enterShort = ta.crossunder(fastSMA, slowSMA)
    since_buy = ta.barssince(enterLong)
    since_sell = ta.barssince(enterShort)
    buy_trend: Series = since_sell > since_buy
    sell_trend: Series = since_sell < since_buy
    change_trend = buy_trend and sell_trend[1] or (sell_trend and buy_trend[1])
    entry_price = ta.valuewhen(enterLong or enterShort, src, 0)
    plot(series=fastSMA, color=color.new(color.teal, 0))
    plot(series=slowSMA, color=color.new(color.orange, 0))
    plotshape(enterLong, style=shape.circle, location=location.belowbar, color=color.new(color.green, 0), size=size.small)
    plotshape(enterShort, style=shape.circle, location=location.abovebar, color=color.new(color.red, 0), size=size.small)
    ProfitTrailPerc = __input_4__ * 0.01
    takeProfitTrigger = __input_6__ * 0.01
    takeprofitPriceTrigger: float = 0.0
    __block_result__ = na
    if use_TP_Trigger:
        __block_result_1__ = na
        if buy_trend:
            __block_result_1__ = entry_price * (1 + takeProfitTrigger)
        else:
            __block_result_1__ = entry_price * (1 - takeProfitTrigger)
        __block_result__ = __block_result_1__
    else:
        __block_result__ = -1
    takeprofitPriceTrigger = __block_result__
    TP_Trigger_Long_HIT: PersistentSeries[bool] = False
    TP_Trigger_Long_HIT = True if useTP and use_TP_Trigger and buy_trend and (high >= takeprofitPriceTrigger) else TP_Trigger_Long_HIT[1]
    TP_Trigger_Short_HIT: PersistentSeries[bool] = False
    TP_Trigger_Short_HIT = True if useTP and use_TP_Trigger and sell_trend and (low <= takeprofitPriceTrigger) else TP_Trigger_Short_HIT[1]
    display_long_TP_trigger = useTP and buy_trend and (TP_Trigger_Long_HIT == False) and (takeprofitPriceTrigger != -1)
    display_short_TP_trigger = useTP and sell_trend and (TP_Trigger_Short_HIT == False) and (takeprofitPriceTrigger != -1)
    display_TP_trigger = display_long_TP_trigger or display_short_TP_trigger
    plot(takeprofitPriceTrigger if display_TP_trigger else na, title='takeprofitPriceTrigger', color=color.new(color.orange, 0), style=plot.style_cross, linewidth=3)
    longTrailTP: Series[float] = 0.0
    shortTrailTP: Series[float] = 0.0
    __block_result_2__ = na
    if useTP and buy_trend:
        tpValue = high * (1 + ProfitTrailPerc)
        __block_result_2__ = math.max(tpValue, longTrailTP[1])
    else:
        __block_result_2__ = 0
    longTrailTP = __block_result_2__
    __block_result_3__ = na
    if useTP and sell_trend:
        tpValue = low * (1 - ProfitTrailPerc)
        __block_result_3__ = math.min(tpValue, shortTrailTP[1])
    else:
        __block_result_3__ = 999999
    shortTrailTP = __block_result_3__
    crossover_1 = ta.crossover(high, longTrailTP[1])
    cond_long_trail_tp_hit = useTP and buy_trend and crossover_1 and (TP_Trigger_Long_HIT or use_TP_Trigger == False)
    crossunder_1 = ta.crossunder(low, shortTrailTP[1])
    cond_short_trail_tp_hit = useTP and sell_trend and crossunder_1 and (TP_Trigger_Short_HIT or use_TP_Trigger == False)
    plot(series=longTrailTP if useTP and buy_trend and (high <= longTrailTP) and (TP_Trigger_Long_HIT or use_TP_Trigger == False) else na, color=color.new(color.aqua, 0), style=plot.style_circles, linewidth=2, title='Long Trail TP')
    plot(series=shortTrailTP if useTP and sell_trend and (low >= shortTrailTP) and (TP_Trigger_Short_HIT or use_TP_Trigger == False) else na, color=color.new(color.aqua, 0), style=plot.style_circles, linewidth=2, title='Short Trail TP')
    close_long = cond_long_trail_tp_hit
    close_short = cond_short_trail_tp_hit
    if enterLong:
        strategy.entry(TradeId + ' L', direction=strategy.long)
    if close_long:
        strategy.close(TradeId + ' L')
    if enterShort:
        strategy.entry(TradeId + ' S', direction=strategy.short)
    if close_short:
        strategy.close(TradeId + ' S')
    if change_trend:
        TP_Trigger_Long_HIT = False
        TP_Trigger_Short_HIT = False


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
