"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, math, script, strategy, syminfo, ta, volume
from pynecore.types import NA


@script.strategy(title='BTFD strategy [3min]', overlay=True, pyramiding=5, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.03, margin_long=0, margin_short=0, close_by_id=True)
def main(
    vol_sma_length=input.int(70, title='Volume lenght  ', minval=1),
    rsi_lenght=input.int(20, title='RSI lenght', minval=0),
    tp_1=input.float(0.4, '  TP 1', minval=0.1, step=0.1),
    tp_2=input.float(0.6, '  TP 2', minval=0.2, step=0.1),
    tp_3=input.float(0.8, '  TP 3', minval=0.3, step=0.1),
    tp_4=input.float(1.0, '  TP 4', minval=0.4, step=0.1),
    tp_5=input.float(1.2, '  TP 5', minval=0.5, step=0.1),
    q_1=input.int(title='  % TP 1 Q ', defval=20, minval=1, step=10),
    q_2=input.int(title='  % TP 2 Q ', defval=40, minval=1, step=10),
    q_3=input.int(title='  % TP 3 Q ', defval=60, minval=1, step=10),
    q_4=input.int(title='  % TP 4 Q ', defval=80, minval=1, step=10),
    q_5=input.int(title='  % TP 5 Q ', defval=100, minval=1, step=10),
    sl=input.float(5.0, '% Stop Loss', step=0.1)
):
    Volume_condt = volume > ta.sma(volume, vol_sma_length) * 2.5
    rsi_up = ta.rma(math.max(ta.change(close), 0), rsi_lenght)
    rsi_down = ta.rma(-math.min(ta.change(close), 0), rsi_lenght)
    rsi_value = 100 if rsi_down == 0 else 0 if rsi_up == 0 else 100 - 100 / (1 + rsi_up / rsi_down)
    rsi_overs = rsi_value <= 30
    rsi_overb = rsi_value >= 70
    long_cond = Volume_condt and rsi_overs
    def per(procent):
        return math.round(procent / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    if long_cond:
        strategy.entry('BUY', strategy.long)
    strategy.exit('TP 1', qty_percent=q_1, profit=per(tp_1), loss=per(sl))
    strategy.exit('TP 2', qty_percent=q_2, profit=per(tp_2), loss=per(sl))
    strategy.exit('TP 3', qty_percent=q_3, profit=per(tp_3), loss=per(sl))
    strategy.exit('TP 4', qty_percent=q_4, profit=per(tp_4), loss=per(sl))
    strategy.exit('TP 5', qty_percent=q_5, profit=per(tp_5), loss=per(sl))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
