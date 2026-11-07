"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, high, input, low, na, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy('Pivot Reversal Strategy + alerts via TradingConnector to indices', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    leftBars=input(4),
    rightBars=input(2)
):
    swh = ta.pivothigh(leftBars, rightBars)
    swl = ta.pivotlow(leftBars, rightBars)
    swh_cond = not na(swh)
    hprice: Series[float] = 0.0
    hprice = swh if swh_cond else hprice[1]
    le: Series[bool] = False
    le = True if swh_cond else False if le[1] and high > hprice else le[1]
    if le:
        strategy.entry('PivRevLE', strategy.long, comment='PivRevLE', stop=hprice + syminfo.mintick)
        alert(message='long', freq=alert.freq_once_per_bar_close)
    swl_cond = not na(swl)
    lprice: Series[float] = 0.0
    lprice = swl if swl_cond else lprice[1]
    se: Series[bool] = False
    se = True if swl_cond else False if se[1] and low < lprice else se[1]
    if se:
        strategy.entry('PivRevSE', strategy.short, comment='PivRevSE', stop=lprice - syminfo.mintick)
        alert(message='short', freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
