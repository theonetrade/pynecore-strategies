"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, format, hline, input, location, math, na, plot,
    plotshape, script, shape, strategy, ta
)
from pynecore.types import Series


@script.strategy(title='Bollinger Band with RSI', shorttitle='BB&RSI', format=format.price, precision=2, pyramiding=50, initial_capital=10000, calc_on_order_fills=False, calc_on_every_tick=True, default_qty_type=strategy.cash, default_qty_value=1000, currency='USD', margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    len=input.int(14, minval=1, title='Length'),
    src: Series[float] = input(close, 'Source'),
    length_bb=input.int(20, title='BB Length', minval=1),
    mult=input.float(2.0, minval=0.001, maxval=50, title='BB StdDev'),
    offset=input.int(0, 'BB Offset', minval=-500, maxval=500),
    Plot_PnL=input(title='Plot Cummulative PnL', defval=False),
    Plot_Pos=input(title='Plot Current Position Size', defval=False),
    __input_7__=input.float(10, title='Long Take Profit %', step=0.1),
    __input_8__=input.float(25, title='Long Stop Loss %', step=0.1)
):
    up = ta.rma(math.max(ta.change(src), 0), len)
    down = ta.rma(-math.min(ta.change(src), 0), len)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    plot(rsi, 'RSI', color=color.new(color.new('#8E1599'), 0))
    band1 = hline(70, 'Upper Band', color=color.new('#C0C0C0'))
    band0 = hline(30, 'Lower Band', color=color.new('#C0C0C0'))
    fill(band1, band0, color=color.new(color.new('#9915FF'), 90), title='Background')
    basis = ta.sma(src, length_bb)
    dev = mult * ta.stdev(src, length_bb)
    upper = basis + dev
    lower = basis - dev
    long_tp_inp = __input_7__ / 100
    long_sl_inp = __input_8__ / 100
    long_take_level = strategy.position_avg_price * (1 + long_tp_inp)
    long_stop_level = strategy.position_avg_price * (1 - long_sl_inp)
    entry_long = rsi < 30 and src < lower
    exit_long = rsi > 70
    plotshape(entry_long, style=shape.labelup, color=color.new(color.green, 0), location=location.bottom, text='L', textcolor=color.new(color.white, 0), title='LONG_ORDER')
    plotshape(exit_long, style=shape.labeldown, color=color.new(color.red, 0), location=location.top, text='S', textcolor=color.new(color.white, 0), title='SHORT_ORDER')
    if entry_long:
        strategy.entry('Long', strategy.long)
    strategy.exit('TP/SL', 'Long', limit=long_take_level, stop=long_stop_level)
    if exit_long:
        strategy.close('Long', comment='Exit')
    plot(strategy.equity - strategy.initial_capital if Plot_PnL else na, title='PnL', color=color.new(color.red, 0))
    plot(strategy.position_size if Plot_Pos else na, title='open_position', color=color.new(color.fuchsia, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
