"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, close, high, input, low, math, request, script, strategy,
    syminfo, ta
)
from pynecore.types import NA


@script.strategy(title='BTC bot', overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='long', options=('long', 'short', 'all')),
    higherTF=input.timeframe('W'),
    factor=input(2),
    length=input(21),
    stoploss=input.float(title=' stop loss', defval=15, minval=0.01),
    q1=input.int(title=' qty_percent1', defval=25, minval=1),
    q2=input.int(title=' qty_percent2', defval=25, minval=1),
    q3=input.int(title=' qty_percent3', defval=25, minval=1),
    tp1=input.float(title=' Take profit1', defval=3, minval=0.01),
    tp2=input.float(title=' Take profit2', defval=5, minval=0.01),
    tp3=input.float(title=' Take profit3', defval=7, minval=0.01),
    tp4=input.float(title=' Take profit4', defval=10, minval=0.01)
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    pc = request.security(syminfo.tickerid, higherTF, close[1], lookahead=barmerge.lookahead_on)
    ph = request.security(syminfo.tickerid, higherTF, high[1], lookahead=barmerge.lookahead_on)
    pl = request.security(syminfo.tickerid, higherTF, low[1], lookahead=barmerge.lookahead_on)
    PP: float = 0.0
    R1: float = 0.0
    R2: float = 0.0
    R3: float = 0.0
    S1: float = 0.0
    S2: float = 0.0
    S3: float = 0.0
    PP = (ph + pl + pc) / 3
    R1 = PP + PP - pl
    S1 = PP - (ph - PP)
    R2 = PP + ph - pl
    S2 = PP - (ph - pl)
    R3 = ph + factor * (PP - pl)
    S3 = pl - 2 * (ph - PP)
    p = close
    vrsi = ta.rsi(p, length)
    pp = ta.ema(vrsi, length)
    d = (vrsi - pp) * 5
    cc = (vrsi + d + pp) / 2
    low1 = ta.crossover(cc, 0)
    sell = ta.crossover(close[1], R3)
    l = low1
    s = sell
    if l:
        strategy.entry('buy', strategy.long)
    if s:
        strategy.entry('sell', strategy.short)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    los = per(stoploss)
    strategy.exit('x1', qty_percent=q1, profit=per(tp1), loss=los)
    strategy.exit('x2', qty_percent=q2, profit=per(tp2), loss=los)
    strategy.exit('x3', qty_percent=q3, profit=per(tp3), loss=los)
    strategy.exit('x4', profit=per(tp4), loss=los)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
