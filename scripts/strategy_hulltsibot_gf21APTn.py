"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, fill, input, math, open, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='TSIHULLBOT', shorttitle='TSICCIHULL', default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    long=input(title='Long Length', defval=50),
    short=input(title='Short Length', defval=50),
    signal=input(title='Signal Length', defval=7),
    price: Series[float] = input(title='Source', defval=open),
    lineupper=input(title='Upper Line', defval=250),
    linelower=input(title='Lower Line', defval=-250)
):
    def double_smooth(price, long, short):
        fist_smooth = ta.hma(price, long)
        return ta.hma(fist_smooth, short)

    pc = ta.change(price)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(math.abs(pc), long, short)
    tsi_value: Series = 100 * (double_smoothed_pc / double_smoothed_abs_pc) * 5
    tsihmaline: Series = ta.hma(tsi_value, signal) * 5
    clr = color.red if tsihmaline < tsi_value else color.lime
    clr2 = color.red if tsi_value < tsi_value[1] else color.lime
    i1 = plot(lineupper + 3, color=color.new(color.black, 0), linewidth=3)
    i2 = plot(linelower + 3, color=color.new(color.black, 0), linewidth=3)
    i3 = plot(lineupper, color=clr)
    i4 = plot(linelower, color=clr)
    trendv = tsihmaline / 5.6
    plot(trendv, linewidth=7, color=color.new(color.black, 0))
    plot(trendv, linewidth=4, color=color.new(color.yellow, 0))
    j1 = plot(tsi_value, linewidth=5, color=color.new(color.black, 0))
    j2 = plot(tsi_value[1], linewidth=5, color=color.new(color.black, 0))
    j3 = plot(tsi_value, color=clr2)
    j4 = plot(tsi_value[1], color=clr2)
    fill(i3, i4, color=color.new(clr, 90))
    fill(j3, j4, color=color.new(clr2, 15))
    longCondition = tsihmaline > tsihmaline[1] and price > price[1]
    if longCondition:
        strategy.entry('Buy ⤴️', strategy.long)
    shortCondition = tsihmaline < tsihmaline[1] and price < price[1]
    if shortCondition:
        strategy.entry('Sell ⤵️', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
