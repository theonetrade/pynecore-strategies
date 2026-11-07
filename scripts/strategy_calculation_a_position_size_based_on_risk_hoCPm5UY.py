"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, currency, input, na, script, strategy, syminfo


@script.strategy('Сalculation a position size based on risk', overlay=True, margin_long=10, margin_short=10, currency=currency.NONE, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    slPcnt=input(10, title='Stop Loss %%'),
    riskValue=input.int(2, title='Risk ', inline='risk', tooltip='Max risk for position'),
    riskType=input.string('% from equity', title='', options=('% from equity', '$$'), inline='risk')
):
    def percent2points(percent):
        return strategy.position_avg_price * percent / 100 / syminfo.mintick if strategy.position_size != 0 else na

    def percent2money(price, percent):
        return price * percent / 100 * syminfo.pointvalue

    def calcPositionSize(entryPrice, slPercent):
        __block_result__ = na
        if riskType == '% from equity':
            __block_result__ = strategy.equity * riskValue / 100
        else:
            __block_result__ = riskValue
        risk = __block_result__
        return risk / percent2money(entryPrice, slPercent)

    qty = calcPositionSize(close, slPcnt)
    longCondition = bar_index % 333 == 0
    if longCondition:
        strategy.entry('My Long Entry Id', strategy.long, qty=qty)
    shortCondition = bar_index % 444 == 0
    if shortCondition:
        strategy.entry('My Short Entry Id', strategy.short, qty=qty)
    slPts = percent2points(slPcnt)
    strategy.exit('x', loss=slPts)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
