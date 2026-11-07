"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import color, high, input, low, na, nz, plot, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy('Pivot of Pivot Reversal Strategy [QuantNomad]', shorttitle='PoP Reversal Strategy [QN]', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    leftBars=input(4, title='PP Left Bars'),
    rightBars=input(2, title='PP Right Bars'),
    atr_length=input(14, title='ATR Length'),
    atr_mult=input(0.1, title='ATR Mult')
):
    def pivotHighSig(left, right):
        pp_ok: bool = True
        atr = ta.atr(atr_length)
        for i in pine_range(1, left, 1):
            if high[right] < high[right + i] + atr * atr_mult:
                pp_ok = False
        for i in pine_range(0, right - 1, 1):
            if high[right] < high[i] + atr * atr_mult:
                pp_ok = False
        return high[right] if pp_ok else na

    def pivotLowSig(left, right):
        pp_ok: bool = True
        atr = ta.atr(atr_length)
        for i in pine_range(1, left, 1):
            if low[right] > low[right + i] - atr * atr_mult:
                pp_ok = False
        for i in pine_range(0, right - 1, 1):
            if low[right] > low[i] - atr * atr_mult:
                pp_ok = False
        return low[right] if pp_ok else na

    swh = pivotHighSig(leftBars, rightBars)
    swl = pivotLowSig(leftBars, rightBars)
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
    ph1: Series[float] = 0.0
    ph2: Series[float] = 0.0
    ph3: Series[float] = 0.0
    pl1: Series[float] = 0.0
    pl2: Series[float] = 0.0
    pl3: Series[float] = 0.0
    pphprice: Series[float] = 0.0
    pplprice: Series[float] = 0.0
    ph3 = nz(ph2[1]) if swh_cond else nz(ph3[1])
    ph2 = nz(ph1[1]) if swh_cond else nz(ph2[1])
    ph1 = hprice if swh_cond else nz(ph1[1])
    pl3 = nz(pl2[1]) if swl_cond else nz(pl3[1])
    pl2 = nz(pl1[1]) if swl_cond else nz(pl2[1])
    pl1 = lprice if swl_cond else nz(pl1[1])
    pphprice = ph2 if swh_cond and ph2 > ph1 and (ph2 > ph3) else nz(pphprice[1])
    pplprice = pl2 if swl_cond and pl2 < pl1 and (pl2 < pl3) else nz(pplprice[1])
    if le and (not na(pphprice)) and (pphprice != 0):
        strategy.entry('PivRevLE', strategy.long, comment='PivRevLE', stop=pphprice + syminfo.mintick)
    if se and (not na(pplprice)) and (pplprice != 0):
        strategy.entry('PivRevSE', strategy.short, comment='PivRevSE', stop=pplprice - syminfo.mintick)
    plot(lprice, color=color.new(color.red, 55))
    plot(hprice, color=color.new(color.green, 55))
    plot(pplprice, color=color.new(color.red, 0), linewidth=2)
    plot(pphprice, color=color.new(color.green, 0), linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
