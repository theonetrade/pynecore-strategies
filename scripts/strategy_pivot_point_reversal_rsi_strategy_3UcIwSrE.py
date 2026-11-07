"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, na, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy('Pivot Point Reversal + RSI Strategy', shorttitle='PP + RSI Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    leftBars=input(3, title='PP - Left Bars'),
    rightBars=input(3, title='PP - Right Bars'),
    rsi_length=input(14, title='RSI - Length'),
    rsi_long=input(70, title='RSI - Overbought level'),
    rsi_short=input(30, title='RSI - Overold level')
):
    swh = ta.pivothigh(leftBars, rightBars)
    swl = ta.pivotlow(leftBars, rightBars)
    swh_cond = not na(swh)
    hprice: Series[float] = 0.0
    hprice = swh if swh_cond else hprice[1]
    le: Series[bool] = False
    le = True if swh_cond else False if le[1] and high > hprice else le[1]
    swl_cond = not na(swl)
    lprice: Series[float] = 0.0
    lprice = swl if swl_cond else lprice[1]
    se: Series[bool] = False
    se = True if swl_cond else False if se[1] and low < lprice else se[1]
    rsi: Series = ta.rsi(close, 14)
    if le and rsi[rightBars] < rsi_long:
        strategy.entry('PivRevLE', strategy.long, comment='PivRSI Long', stop=hprice + syminfo.mintick)
    if se and rsi[rightBars] > rsi_short:
        strategy.entry('PivRevSE', strategy.short, comment='PivRSI Short', stop=lprice - syminfo.mintick)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
