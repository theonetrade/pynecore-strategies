"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, input, math, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Dual Moving Average', initial_capital=10000, overlay=True, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    angleCriteria=input.int(title='Angle', defval=7, minval=1, maxval=13),
    i_lookback=input.int(2, 'Angle Period', minval=1),
    i_atrPeriod=input.int(10, 'ATR Period', minval=1),
    i_angleLevel=input.int(6, 'Angle Level', minval=1),
    i_maSource: Series[float] = input(close, 'MA Source')
):
    ma1 = ta.sma(close, 8)
    ma2 = ta.sma(close, 21)
    def f_angle(_src: Series, _lookback, _atrPeriod):
        rad2degree = 180 / 3.141592653589793
        ang = rad2degree * math.atan((_src - _src[_lookback]) / ta.atr(_atrPeriod) / _lookback)
        return ang

    _angle = f_angle(ma2, i_lookback, i_atrPeriod)
    plot(ma1, color=color.new(color.new('#FF0000'), 0))
    plot(ma2, color=color.new(color.new('#00FF00'), 0))
    crosso = ta.crossover(ma1, ma2)
    crossu = ta.crossunder(ma1, ma2)
    _lookback: int = 15
    def f_somethingHappened(_cond: Series, _lookback):
        _crossed: bool = False
        for i in pine_range(1, _lookback, 1):
            if _cond[i]:
                _crossed = True
        return _crossed

    longcrossed = f_somethingHappened(crosso, _lookback)
    shortcrossed = f_somethingHappened(crossu, _lookback)
    long = longcrossed and _angle > angleCriteria
    short = shortcrossed and _angle < -angleCriteria
    if long:
        strategy.entry('Long', strategy.long)
    if short:
        strategy.entry('short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
