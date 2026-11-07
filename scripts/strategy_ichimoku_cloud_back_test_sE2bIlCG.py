"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Ichimoku Cloud', shorttitle='Ichimoku', overlay=True, commission_type=strategy.commission.percent, commission_value=0.075, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    conversionPeriods=input.int(9, minval=1, title='Conversion Line Periods'),
    basePeriods=input.int(26, minval=1, title='Base Line Periods'),
    laggingSpan2Periods=input.int(52, minval=1, title='Lagging Span 2 Periods'),
    displacement=input.int(26, minval=0, title='Displacement')
):
    def donchian(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    conversionLine = donchian(conversionPeriods)
    baseLine = donchian(basePeriods)
    leadLine1: Series = math.avg(conversionLine, baseLine)
    leadLine2: Series = donchian(laggingSpan2Periods)
    plot(conversionLine, color=color.new(color.new('#0496FF'), 0), title='Conversion Line')
    plot(baseLine, color=color.new(color.new('#991515'), 0), title='Base Line')
    plot(close, offset=-displacement, color=color.new(color.new('#459915'), 0), title='Lagging Span')
    p1 = plot(leadLine1, offset=displacement, color=color.new(color.green, 0), title='Lead 1')
    p2 = plot(leadLine2, offset=displacement, color=color.new(color.red, 0), title='Lead 2')
    fill(p1, p2, color=color.green if leadLine1 > leadLine2 else color.red)
    buy = close > leadLine1[26] and close > leadLine2[26]
    sell = close < leadLine1[26] and close < leadLine2[26]
    if buy:
        strategy.entry('Buy', strategy.long)
    if sell:
        strategy.entry('Sell', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
