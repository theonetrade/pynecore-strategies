"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import close, color, fill, hline, input, math, na, nz, plot, script, strategy, ta
from pynecore.types import NA, Series


@script.strategy('Dynamic RSI Momentum', 'DRM Strategy', process_orders_on_close=True, default_qty_type=strategy.percent_of_equity, default_qty_value=50, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    len=input.int(10, 'Momentum Length', minval=1, group='Dynamic RSI Momentum'),
    src: Series[float] = input.source(close, 'Source', group='Dynamic RSI Momentum'),
    min_rsi=input.int(20, 'Min RSI', group='Dynamic RSI Momentum'),
    max_rsi=input.int(50, 'Max RSI', group='Dynamic RSI Momentum'),
    upLvl=input.float(70, 'OverBought', minval=0, maxval=100, group='Dynamic RSI Momentum'),
    dnLvl=input.float(30, 'OverSold', minval=0, maxval=100, group='Dynamic RSI Momentum')
):
    def rmaFun(src, len):
        sma = ta.sma(src, len)
        alpha = 1 / len
        sum: Series[float] = 0.0
        sum = sma if na(sum[1]) else alpha * src + (1 - alpha) * nz(sum[1])
        return sum

    def rsiFun(src: Series, len):
        return 100 - 100 / (1 + rmaFun(src - src[1] if src - src[1] > 0 else 0, len) / rmaFun(src[1] - src if src[1] - src > 0 else 0, len))

    momVal = src - src[len]
    corr = ta.correlation(src, momVal, len)
    corr = NA(float) if corr > 1 or corr < -1 else corr
    rsiLen: int = 0
    rsiLen = cast_int(min_rsi + nz(math.round((1 - corr) * (max_rsi - min_rsi) / 2, 0), 0))
    rsiMom = rsiFun(src, rsiLen)
    long = ta.crossover(rsiMom, dnLvl)
    short = ta.crossunder(rsiMom, upLvl)
    if long and (not na(rsiMom)):
        strategy.entry('Long', strategy.long)
    if short and (not na(rsiMom)):
        strategy.entry('Short', strategy.short)
    plot(rsiMom, 'Dynamic RSI Momentum', color.green if rsiMom < dnLvl else color.red if rsiMom > upLvl else color.yellow)
    hline(50, 'Mid Line', color.gray)
    upperLine = hline(upLvl, 'Upper Line', color.gray)
    lowerLine = hline(dnLvl, 'Lower Line', color.gray)
    fill(upperLine, lowerLine, color.new(color.purple, 90), 'Background Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)