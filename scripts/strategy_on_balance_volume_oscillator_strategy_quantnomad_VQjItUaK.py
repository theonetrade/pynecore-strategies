"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, na, plot, script, strategy, ta, volume
from pynecore.types import Series


@script.strategy(title='On Balance Volume Oscillator Strategy [QuantNomad]', shorttitle='OBV Str [QN]', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    obv_length=input(20, title='OBV Length'),
    obv_source: Series[float] = input(close, title='OBV Source'),
    obv_show_ema=input(True, title='Show OBV EMA'),
    obv_ema1_length=input(12, title='EMA1 Length'),
    obv_ema2_length=input(26, title='EMA2 Length')
):
    obv = math.sum(volume * math.sign(ta.change(obv_source)), obv_length)
    obv_osc = obv / math.sum(volume, obv_length)
    obv_ema1 = ta.ema(obv_osc, obv_ema1_length)
    obv_ema2 = ta.ema(obv_osc, obv_ema2_length)
    plot(0, color=color.new(color.gray, 0), title='0 line')
    plot(obv_osc, color=color.new(color.blue, 0), title='OBV Osc', linewidth=2)
    plot(obv_ema1 if obv_show_ema else na, color=color.new(color.orange, 0), title='OBV EMA1', linewidth=2)
    plot(obv_ema2 if obv_show_ema else na, color=color.new(color.green, 0), title='OBV EMA2', linewidth=2)
    if ta.crossover(obv_ema1, obv_ema2):
        strategy.entry('long', strategy.long)
    if ta.crossunder(obv_ema1, obv_ema2):
        strategy.entry('short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
