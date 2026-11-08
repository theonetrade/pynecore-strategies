"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, color, high, input, low, math, nz, plot, script, ta
from pynecore.types import Series


@script.indicator('Beardy Squeeze Pro', shorttitle='Squeeze', overlay=False, precision=2, na_bool=True)
def main(
    length=input.int(20, 'TTM Squeeze Length'),
    BB_mult=input.float(2.0, 'Bollinger Band STD Multiplier'),
    KC_mult_high=input.float(1.0, 'Keltner Channel #1'),
    KC_mult_mid=input.float(1.5, 'Keltner Channel #2'),
    KC_mult_low=input.float(2.0, 'Keltner Channel #3'),
    Detect_Sqz_Start=input.bool(True, 'Alert Price Action Squeeze'),
    Detect_Sqz_Fire=input.bool(True, 'Alert Squeeze Firing')
):
    BB_basis = ta.sma(close, length)
    dev = BB_mult * ta.stdev(close, length)
    BB_upper = BB_basis + dev
    BB_lower = BB_basis - dev
    KC_basis = ta.sma(close, length)
    devKC = ta.sma(ta.tr, length)
    KC_upper_high = KC_basis + devKC * KC_mult_high
    KC_lower_high = KC_basis - devKC * KC_mult_high
    KC_upper_mid = KC_basis + devKC * KC_mult_mid
    KC_lower_mid = KC_basis - devKC * KC_mult_mid
    KC_upper_low = KC_basis + devKC * KC_mult_low
    KC_lower_low = KC_basis - devKC * KC_mult_low
    NoSqz: Series = BB_lower < KC_lower_low or BB_upper > KC_upper_low
    LowSqz = BB_lower >= KC_lower_low or BB_upper <= KC_upper_low
    MidSqz = BB_lower >= KC_lower_mid or BB_upper <= KC_upper_mid
    HighSqz = BB_lower >= KC_lower_high or BB_upper <= KC_upper_high
    mom: Series = ta.linreg(close - math.avg(math.avg(ta.highest(high, length), ta.lowest(low, length)), ta.sma(close, length)), length, 0)
    iff_1 = color.new(color.aqua, 0) if mom > nz(mom[1]) else color.new(color.new('#2962FF'), 0)
    iff_2 = color.new(color.red, 0) if mom < nz(mom[1]) else color.new(color.yellow, 0)
    mom_color = iff_1 if mom > 0 else iff_2
    sq_color = color.new(color.orange, 0) if HighSqz else color.new(color.red, 0) if MidSqz else color.new(color.black, 0) if LowSqz else color.new(color.green, 0)
    if Detect_Sqz_Start and NoSqz[1] and (not NoSqz):
        alert('Squeeze Started')
    elif Detect_Sqz_Fire and NoSqz and (not NoSqz[1]):
        alert('Squeeze Fired')
    plot(mom, title='MOM', color=mom_color, style=plot.style_columns, linewidth=2)
    plot(0, title='SQZ', color=sq_color, style=plot.style_circles, linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
