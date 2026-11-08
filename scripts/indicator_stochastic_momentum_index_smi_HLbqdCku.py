"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, fill, high, hline, input, low, plot, script, ta


@script.indicator('Stochastics Momentum Index', shorttitle='Stoch_MTM')
def main(
    a=input.int(10, 'Percent K Length', minval=1),
    b=input.int(3, 'Percent D Length', minval=1),
    c=input.int(10, 'EMA Signal Length', minval=1),
    smooth_period=input.int(5, 'Smoothing Period', minval=1),
    ob=input.float(40, 'Overbought', minval=-100, maxval=100),
    os=input.float(-40, 'Oversold', minval=-100, maxval=100)
):
    ll = ta.lowest(low, a)
    hh = ta.highest(high, a)
    diff = hh - ll
    rdiff = close - (hh + ll) / 2
    avgrel = ta.ema(rdiff, b)
    avgdiff = ta.ema(diff, b)
    SMI = avgrel / (avgdiff / 2) * 100 if avgdiff != 0 else 0.0
    SMI_smoothed = ta.sma(SMI, smooth_period)
    SMIsignal = ta.ema(SMI_smoothed, b)
    emasignal = ta.ema(SMI_smoothed, c)
    plot(SMI_smoothed, 'Stochastic', color=color.black)
    plot(emasignal, 'EMA', color=color.red)
    h0 = hline(ob, 'Overbought', color=color.gray)
    h1 = hline(os, 'Oversold', color=color.gray)
    level_ob = ob
    level_obsmi = SMI_smoothed if SMI_smoothed > level_ob else level_ob
    level_os = os
    level_ossmi = SMI_smoothed if SMI_smoothed < level_os else level_os
    p1 = plot(level_ob, display=display.none)
    p2 = plot(level_obsmi, display=display.none)
    p3 = plot(level_os, display=display.none)
    p4 = plot(level_ossmi, display=display.none)
    fill(p1, p2, color=color.new(color.red, 60), title='OverBought')
    fill(p3, p4, color=color.new(color.green, 60), title='OverSold')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
