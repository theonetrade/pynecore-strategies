"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, barstate, close, color, fill, high, hline, input, low, plot,
    position, script, strategy, string, syminfo, ta, table
)
from pynecore.types import Persistent, Table


@script.strategy(title='TradingView Alerts to MT4 MT5 Strategy example', commission_type=strategy.commission.cash_per_order, commission_value=3e-05, overlay=False, default_qty_value=100000, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    periodK=input.int(13, title='K', minval=1, inline='stoch', group='Stochastic'),
    periodD=input.int(3, title='D', minval=1, inline='stoch', group='Stochastic'),
    smoothK=input.int(4, title='Smooth', minval=1, inline='stoch', group='Stochastic'),
    TP_type=input.string('pips', options=('percent', 'pips'), title='TakeProfit Type'),
    TakePartialProfitDistance=input.float(150, title='Partial TakeProfit Value'),
    TakeProfitDistance=input.float(400, title='TakeProfit Value')
):
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    plot(k, title='%K', color=color.new(color.blue, 0))
    plot(d, title='%D', color=color.new(color.orange, 0))
    h0 = hline(80)
    h1 = hline(20)
    fill(h0, h1, color=color.new(color.purple, 75))
    GoLong = ta.crossover(k, d) and k < 80
    GoShort = ta.crossunder(k, d) and k > 20
    piv_high = ta.pivothigh(high, 1, 1)
    piv_low = ta.pivotlow(low, 1, 1)
    stoploss_long: Persistent[float] = low
    stoploss_short: Persistent[float] = high
    pl = ta.valuewhen(cast_bool(piv_low), piv_low, 0)
    ph = ta.valuewhen(cast_bool(piv_high), piv_high, 0)
    if GoLong:
        stoploss_long = low if low < pl else pl
    if GoShort:
        stoploss_short = high if high > ph else ph
    TakePartialProfitDistance_Long = TakePartialProfitDistance / 100 / syminfo.mintick if TP_type == 'percent' else TakePartialProfitDistance
    TakeProfitDistance_Long = TakeProfitDistance / 100 / syminfo.mintick if TP_type == 'percent' else TakeProfitDistance
    TakePartialProfitDistance_Short = TakePartialProfitDistance / 100 / syminfo.mintick if TP_type == 'percent' else TakePartialProfitDistance
    TakeProfitDistance_Short = TakeProfitDistance / 100 / syminfo.mintick if TP_type == 'percent' else TakeProfitDistance
    if GoLong:
        strategy.entry('Long', strategy.long)
    strategy.exit('XPartLong', from_entry='Long', qty_percent=50, profit=TakePartialProfitDistance_Long)
    strategy.exit('XLong', from_entry='Long', stop=stoploss_long, profit=TakeProfitDistance_Long)
    if GoShort:
        strategy.entry('Short', strategy.short)
    strategy.exit('XPartShort', from_entry='Short', qty_percent=50, profit=TakePartialProfitDistance_Long)
    strategy.exit('XShort', from_entry='Short', stop=stoploss_short, profit=TakeProfitDistance_Long)
    string_tp1_type = ' tp1perc=' if TP_type == 'percent' else ' tp1='
    string_tp_type = ' tpperc=' if TP_type == 'percent' else ' tp='
    alertsyntax_golong = 'long slprice=' + string.tostring(stoploss_long) + string_tp1_type + string.tostring(TakePartialProfitDistance) + ' part1=0.5' + string_tp_type + string.tostring(TakeProfitDistance)
    alertsyntax_goshort = 'short slprice=' + string.tostring(stoploss_short) + string_tp1_type + string.tostring(TakePartialProfitDistance) + ' part1=0.5' + string_tp_type + string.tostring(TakeProfitDistance)
    if GoLong:
        alert(message=alertsyntax_golong, freq=alert.freq_once_per_bar_close)
    if GoShort:
        alert(message=alertsyntax_goshort, freq=alert.freq_once_per_bar_close)
    alertsDisplayTable: Persistent[Table] = table.new(position.top_right, 1, 5, color.black)
    if barstate.islastconfirmedhistory:
        table.cell(alertsDisplayTable, 0, 0, 'Alert sent at Long Entry:  ' + alertsyntax_golong, text_color=color.white)
        table.cell(alertsDisplayTable, 0, 1, 'Alert sent at Short Entry:  ' + alertsyntax_goshort, text_color=color.white)
        table.cell(alertsDisplayTable, 0, 2, ' ')
        table.cell(alertsDisplayTable, 0, 3, 'In this use-case exit alerts are not needed, because exit brackets are set already with the entry alert.', text_color=color.white)
        table.cell(alertsDisplayTable, 0, 4, "Also, with TradingConnector's default settings, LONG entry alert will automatically close SHORT position and vice-versa.", text_color=color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
