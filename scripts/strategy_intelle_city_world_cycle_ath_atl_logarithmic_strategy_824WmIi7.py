"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, bgcolor, close, color, input, location, na, plot,
    plotshape, request, script, shape, size, strategy, syminfo, ta
)


@script.strategy('INTELLECT_city - World Cycle - ATH & ATL - Timeframe 1D and 1W - Logarithmic - Strategy.', shorttitle='INTELLECT_city - World Cycle - ATH & ATL - Timeframe 1D and 1W - Logarithmic - Strategy.', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    resolution=input('D', title='Time interval'),
    is_show_ma=input(True, title='Show Moving Averages ?'),
    is_alert=input(True, title='Send an alert on Pi Cycle Top?'),
    show_signals=input(True, title='Show Signals?'),
    len_ma_long_ath=input.int(350, minval=1, title='ATH Long Moving Average'),
    len_ma_short_ath=input.int(111, minval=1, title='ATH Short Moving Average'),
    len_ma_long_atl=input.int(471, minval=1, title='ATL Long Moving Average'),
    len_ma_short_atl=input.int(150, minval=1, title='ATL Short Moving Average')
):
    ma_long_ath = request.security(syminfo.tickerid, resolution, ta.sma(close, len_ma_long_ath) * 2)
    ma_short_ath = request.security(syminfo.tickerid, resolution, ta.sma(close, len_ma_short_ath))
    ma_long_atl = request.security(syminfo.tickerid, resolution, ta.sma(close, len_ma_long_atl) * 0.745)
    ma_short_atl = request.security(syminfo.tickerid, resolution, ta.ema(close, len_ma_short_atl))
    src = request.security(syminfo.tickerid, resolution, close)
    PiCycleTop_ATH = ta.crossunder(ma_long_ath, ma_short_ath)
    plot(ma_long_ath if is_show_ma else na, color=color.new(color.blue, 0), title='ATH Long MA')
    plot(ma_short_ath if is_show_ma else na, color=color.new(color.blue, 0), title='ATH Short MA')
    plotshape(show_signals and PiCycleTop_ATH, style=shape.diamond, size=size.normal, text='ATH LINE CROSSING IN A CYCLE \n Selling Accuracy \n SELL', color=color.new(color.blue, 0), textcolor=color.new(color.blue, 0), location=location.abovebar)
    alertcondition(condition=PiCycleTop_ATH, title='INTELLECT_city - ATH', message='SELL')
    bgcolor(color.blue if PiCycleTop_ATH else na)
    if PiCycleTop_ATH:
        strategy.entry('Sell', strategy.short)
        if is_alert:
            alert('INTELLECT_city World Cycle ATH - SELL', alert.freq_once_per_bar)
    PiCycleTop_ATL = ta.crossover(ma_long_atl, ma_short_atl)
    plot(ma_long_atl if is_show_ma else na, color=color.new(color.green, 0), title='ATL Long MA')
    plot(ma_short_atl if is_show_ma else na, color=color.new(color.green, 0), title='ATL Short MA')
    plotshape(show_signals and PiCycleTop_ATL, style=shape.diamond, size=size.normal, text='ATL CROSSING LINES IN A CYCLE \n Purchase Accuracy \n BUY', color=color.new(color.green, 0), textcolor=color.new(color.green, 0), location=location.belowbar)
    alertcondition(condition=PiCycleTop_ATL, title='INTELLECT_city - ATL', message='BUY')
    bgcolor(color.green if PiCycleTop_ATL else na)
    if PiCycleTop_ATL:
        strategy.entry('Buy', strategy.long)
        if is_alert:
            alert('INTELLECT_city World Cycle ATL - BUY', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
