"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, close, color, fill, high, hline, input, low, open, plot, script,
    strategy, string, syminfo, ta, year
)
from pynecore.types import Persistent


@script.strategy(title='TradingView Alerts to MT4 MT5 - Forex, indices, commodities, stocks, crypto', commission_type=strategy.commission.cash_per_contract, commission_value=3e-05, overlay=False, default_qty_value=20000, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    TakeProfitLevel=input(400),
    TakePartialProfitLevel=input(150),
    periodK=input.int(13, title='K', minval=1),
    periodD=input.int(3, title='D', minval=1),
    smoothK=input.int(4, title='Smooth', minval=1)
):
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    plot(k, title='%K', color=color.new(color.blue, 0))
    plot(d, title='%D', color=color.new(color.orange, 0))
    h0 = hline(80)
    h1 = hline(20)
    fill(h0, h1, color=color.new(color.purple, 75))
    GoLong = ta.crossover(k, d) and k < 80 and (year > 2009)
    GoShort = ta.crossunder(k, d) and k > 20 and (year > 2009)
    AlertTest = open > close or open < close or open == close
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
    trade_id: Persistent[int] = 0
    if GoLong or GoShort:
        trade_id = trade_id + 1
    valuewhen_1 = ta.valuewhen(GoLong, close, 0)
    crossover_1 = ta.crossover(high, valuewhen_1 + TakePartialProfitLevel * syminfo.mintick)
    TakePartialProfitLong = ta.barssince(GoLong) < ta.barssince(GoShort) and crossover_1
    valuewhen_2 = ta.valuewhen(GoShort, close, 0)
    crossunder_1 = ta.crossunder(low, valuewhen_2 - TakePartialProfitLevel * syminfo.mintick)
    TakePartialProfitShort = ta.barssince(GoLong) > ta.barssince(GoShort) and crossunder_1
    if GoLong:
        strategy.entry('Long', strategy.long)
    strategy.exit('XPartLong', from_entry='Long', qty_percent=50, profit=TakePartialProfitLevel)
    strategy.exit('XLong', from_entry='Long', stop=stoploss_long, profit=TakeProfitLevel)
    if GoShort:
        strategy.entry('Short', strategy.short)
    strategy.exit('XPartShort', from_entry='Short', qty_percent=50, profit=TakePartialProfitLevel)
    strategy.exit('XShort', from_entry='Short', stop=stoploss_short, profit=TakeProfitLevel)
    if GoLong:
        alertsyntax_golong = 'long slprice=' + string.tostring(stoploss_long) + ' tradeid=' + string.tostring(trade_id) + ' tp=' + string.tostring(TakeProfitLevel)
        alert(message=alertsyntax_golong, freq=alert.freq_once_per_bar_close)
    if GoShort:
        alertsyntax_goshort = 'short slprice=' + string.tostring(stoploss_short) + ' tradeid=' + string.tostring(trade_id) + ' tp=' + string.tostring(TakeProfitLevel)
        alert(message=alertsyntax_goshort, freq=alert.freq_once_per_bar_close)
    if TakePartialProfitLong:
        alertsyntax_closepartlong = 'closepart tradeid=' + string.tostring(trade_id) + ' part=0.5'
        alert(message=alertsyntax_closepartlong, freq=alert.freq_once_per_bar_close)
    if TakePartialProfitShort:
        alertsyntax_closepartshort = 'closepart tradeid=' + string.tostring(trade_id) + ' part=0.5'
        alert(message=alertsyntax_closepartshort, freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
