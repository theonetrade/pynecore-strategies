"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, na, plot, script, strategy, syminfo, ta


@script.strategy('Stop loss and Take Profit in $$ example', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    __input_0__=input(200, title='Take Profit $$'),
    __input_1__=input(100, title='Stop Loss $$')
):
    longCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))
    if longCondition:
        strategy.entry('My Long Entry Id', strategy.long)
    shortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))
    if shortCondition:
        strategy.entry('My Short Entry Id', strategy.short)
    def moneyToSLPoints(money):
        return money / syminfo.pointvalue / math.abs(strategy.position_size) / syminfo.mintick if strategy.position_size != 0 else na

    p = moneyToSLPoints(__input_0__)
    l = moneyToSLPoints(__input_1__)
    strategy.exit('x', profit=p, loss=l)
    def pointsToPrice(pp):
        return na if na(pp) else strategy.position_avg_price + pp * math.sign(strategy.position_size) * syminfo.mintick

    pp = plot(pointsToPrice(p), style=plot.style_linebr)
    lp = plot(pointsToPrice(-l), style=plot.style_linebr)
    avg = plot(strategy.position_avg_price, style=plot.style_linebr)
    fill(pp, avg, color=color.new(color.green, 90))
    fill(avg, lp, color=color.new(color.red, 90))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
