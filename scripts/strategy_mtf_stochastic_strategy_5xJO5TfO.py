"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, hline, input, low, plot, request, script,
    strategy, syminfo, ta, timeframe
)


@script.strategy('MTF stochastic strategy', overlay=False, pyramiding=3, default_qty_type=strategy.percent_of_equity, default_qty_value=100, currency=currency.USD, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    len=input.int(11, minval=1, title='Length for Main Stochastic'),
    smoothK=input.int(3, minval=1, title='SmoothK for Main Stochastic'),
    smoothD=input.int(3, minval=1, title='SmoothD for Main Stochastic'),
    upLine=input.int(80, minval=50, maxval=90, title='Upper Line Value?'),
    lowLine=input.int(20, minval=10, maxval=50, title='Lower Line Value?'),
    trailStep=input.int(50, minval=10, title='Trialing step value')
):
    k = ta.sma(ta.stoch(close, high, low, len), smoothK)
    d = ta.sma(k, smoothD)
    MTF_period = '5' if timeframe.period == '1' else '15' if timeframe.period == '5' else '30' if timeframe.period == '15' else '60' if timeframe.period == '30' else '240' if timeframe.period == '60' else 'D' if timeframe.period == '240' else 'W' if timeframe.period == 'D' else 'M'
    mtfK = ta.linreg(request.security(syminfo.tickerid, MTF_period, ta.sma(ta.stoch(close, high, low, len), smoothK)), len, 0)
    mtfD = ta.linreg(request.security(syminfo.tickerid, MTF_period, ta.sma(k, smoothD)), len, 0)
    plot(k, 'current TF k', color.new(color.black, 0), style=plot.style_linebr)
    plot(d, 'current TF d', color.new(color.gray, 0), style=plot.style_linebr)
    plot(mtfK, 'MTF TF k', color.new(color.red, 0), style=plot.style_line)
    plot(mtfD, 'Multi TF d', color.new(color.green, 0), style=plot.style_line)
    hline(upLine)
    hline(50)
    hline(lowLine)
    change_1 = ta.change(k, 1)
    longCondition = ta.crossover(mtfK, 50) and k > 50 and (change_1 > 0) and (k > d) and (mtfK > mtfD)
    if longCondition:
        strategy.entry('Lungo', strategy.long)
    change_2 = ta.change(k, 1)
    shortCondition = ta.crossunder(mtfD, 50) and k < 50 and (change_2 < 0) and (k < d) and (mtfK < mtfD)
    if shortCondition:
        strategy.entry('Corto', strategy.short)
    exitlong = ta.crossunder(mtfD, upLine)
    exitshort = ta.crossover(mtfK, lowLine)
    if exitlong:
        strategy.exit('Esci lungo', 'Lungo', trail_points=trailStep)
    if exitshort:
        strategy.exit('Esci corto', 'Corto', trail_points=trailStep)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
