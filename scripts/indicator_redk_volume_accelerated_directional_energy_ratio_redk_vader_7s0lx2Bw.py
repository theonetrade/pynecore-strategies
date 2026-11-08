"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, fixnan, hline, input, math,
    na, plot, script, ta, volume
)
from pynecore.types import Color, Series


@script.indicator('RedK Volume-Accelerated Directional Energy Ratio', 'RedK VADER v4.0', precision=0, timeframe='', timeframe_gaps=False)
def main(
    length=input.int(10, minval=1),
    DER_avg=input.int(5, 'Average', minval=1, inline='DER', group='Directional Energy Ratio'),
    MA_Type=input.string('WMA', 'DER MA type', options=('WMA', 'EMA', 'SMA'), inline='DER', group='Directional Energy Ratio'),
    smooth=input.int(3, 'Smooth', minval=1, inline='DER_1', group='Directional Energy Ratio'),
    show_senti=input.bool(False, 'Sentiment', inline='DER_s', group='Directional Energy Ratio'),
    senti=input.int(20, 'Length', minval=1, inline='DER_s', group='Directional Energy Ratio'),
    v_calc=input.string('Relative', 'Calculation', options=('Relative', 'Full', 'None'), group='Volume Parameters'),
    vlookbk=input.int(20, 'Lookback (for Relative)', minval=1, group='Volume Parameters')
):
    def f_derma(_data, _len, MAOption):
        value = ta.sma(_data, _len) if MAOption == 'SMA' else ta.ema(_data, _len) if MAOption == 'EMA' else ta.wma(_data, _len)
        return value

    price = close
    v = volume
    vola = 1 if v_calc == 'None' or na(volume) else ta.stoch(v, v, v, vlookbk) / 100 if v_calc == 'Relative' else v
    R = (ta.highest(2) - ta.lowest(2)) / 2
    sr = ta.change(price) / R
    rsr = math.max(math.min(sr, 1), -1)
    c = fixnan(rsr * vola)
    c_plus = math.max(c, 0)
    c_minus = -math.min(c, 0)
    avg_vola = f_derma(vola, length, MA_Type)
    dem = f_derma(c_plus, length, MA_Type) / avg_vola
    sup = f_derma(c_minus, length, MA_Type) / avg_vola
    adp = 100 * ta.wma(dem, DER_avg)
    asp = 100 * ta.wma(sup, DER_avg)
    anp = adp - asp
    anp_s = ta.wma(anp, smooth)
    s_adp = 100 * ta.wma(dem, senti)
    s_asp = 100 * ta.wma(sup, senti)
    V_senti: Series = ta.wma(s_adp - s_asp, smooth)
    c_adp = color.new(color.aqua, 30)
    c_asp = color.new(color.orange, 30)
    c_fd = color.new(color.green, 80)
    c_fs = color.new(color.red, 80)
    c_zero = color.new(color.new('#FFEE00'), 70)
    c_up = color.new(color.new('#359BFC'), 0)
    c_dn = color.new(color.new('#F57F17'), 0)
    c_sup = color.new(color.new('#33FF00'), 80)
    c_sdn = color.new(color.new('#FF1111'), 80)
    up = anp_s >= 0
    s_up = V_senti >= 0
    hline(0, 'Zero Line', c_zero, hline.style_solid)
    c_grow_above: Color = color.new('#1B5E2080')
    c_grow_below: Color = color.new('#DC4C4A80')
    c_fall_above: Color = color.new('#66BB6A80')
    c_fall_below: Color = color.new('#EF8E9880')
    sflag_up = math.abs(V_senti) >= math.abs(V_senti[1])
    plot(V_senti if show_senti else na, 'Sentiment', style=plot.style_columns, color=(c_grow_above if sflag_up else c_fall_above) if s_up else c_grow_below if sflag_up else c_fall_below)
    s = plot(asp, 'Supply Energy', c_asp, 2, style=plot.style_circles, join=True)
    d = plot(adp, 'Demand Energy', c_adp, 2, style=plot.style_cross, join=True)
    fill(d, s, c_fd if adp > asp else c_fs)
    plot(anp, 'VADER', color.new(color.gray, 30), display=display.none)
    plot(anp_s, 'Signal', c_up if up else c_dn, 4)
    Alert_up = ta.crossover(anp_s, 0)
    Alert_dn = ta.crossunder(anp_s, 0)
    Alert_swing = ta.cross(anp_s, 0)
    alertcondition(Alert_up, '.   VADER Crossing 0 Up', 'VADER Up - Buying Energy Detected!')
    alertcondition(Alert_dn, '..  VADER Crossing 0 Down', 'VADER Down - Selling Energy Detected!')
    alertcondition(Alert_swing, '... VADER Crossing 0', 'VADER Swing - Possible Reversal')
    v_speedup = ta.crossover(anp_s, V_senti)
    v_slowdn = ta.crossunder(anp_s, V_senti)
    alertcondition(v_speedup, '*  VADER Speeding Up', 'VADER Speeding Up!')
    alertcondition(v_slowdn, '** VADER Slowing Down', 'VADER Slowing Down!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)