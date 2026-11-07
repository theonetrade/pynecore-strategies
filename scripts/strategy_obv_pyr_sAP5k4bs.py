"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, syminfo, ta, volume


@script.strategy(title=' OBV Pyr', overlay=True, pyramiding=5, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=20, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='long', options=('long', 'short', 'all')),
    fastLength=input.int(250, title='Fast filter length ', minval=1),
    slowLength=input.int(500, title='Slow filter length', minval=1),
    LengthOBV=input(20),
    ProfitTarget_Percent=input(3),
    LossTarget_Percent=input(10)
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    source = close
    v1 = ta.ema(source, fastLength)
    v2 = ta.ema(source, slowLength)
    filter: bool = True
    src = close
    nv = volume if ta.change(src) > 0 else -volume if ta.change(src) < 0 else 0 * volume
    c = ta.cum(nv)
    c_tb = c - ta.sma(c, LengthOBV)
    longCond = ta.crossover(c_tb, 0)
    longsignal = (v1 > v2 or filter == False) and longCond
    Profit_Ticks = close * (ProfitTarget_Percent / 100) / syminfo.mintick
    Loss_Ticks = close * (LossTarget_Percent / 100) / syminfo.mintick
    if strategy.opentrades == 0 and longsignal:
        strategy.entry('Entry 1', strategy.long)
    if strategy.opentrades == 1 and longsignal:
        strategy.entry('Entry 2', strategy.long)
    if strategy.opentrades == 2 and longsignal:
        strategy.entry('Entry 3', strategy.long)
    if strategy.opentrades == 3 and longsignal:
        strategy.entry('Entry 4', strategy.long)
    if strategy.opentrades == 4 and longsignal:
        strategy.entry('Entry 5', strategy.long)
    if strategy.opentrades == 5 and longsignal:
        strategy.entry('Entry 6', strategy.long)
    if strategy.opentrades == 6 and longsignal:
        strategy.entry('Entry 7', strategy.long)
    if strategy.position_size > 0:
        strategy.exit(id='Exit 1', from_entry='Entry 1', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 2', from_entry='Entry 2', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 3', from_entry='Entry 3', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 4', from_entry='Entry 4', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 5', from_entry='Entry 5', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 6', from_entry='Entry 6', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 7', from_entry='Entry 7', profit=Profit_Ticks, loss=Loss_Ticks)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
