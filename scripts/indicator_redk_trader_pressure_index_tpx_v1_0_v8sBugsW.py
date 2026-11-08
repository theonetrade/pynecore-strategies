"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, color, high, hline, input, low, math, na, nz, plot,
    script, ta
)
from pynecore.types import Color


@script.indicator('RedK Trader Pressure Index (TPX)', shorttitle='RedK_TPX v5.0', overlay=False, timeframe='', precision=1)
def main(
    length=input.int(title='Avg Length', defval=7, minval=1),
    smooth=input.int(title='Smoothing', defval=3, minval=1),
    clevel=input.int(title='Control Level', defval=30, minval=5, maxval=100),
    pre_s=input.bool(title='Pre-smoothing?', defval=False, inline='pre-smoothing'),
    pre_sv=input.int(title='', defval=3, minval=1, inline='pre-smoothing'),
    slevel_on=input.bool(title='Pressure Signal Line?', defval=False, inline='signal'),
    slevel=input.int(title='', defval=70, minval=0, maxval=100, step=5, inline='signal')
):
    R = ta.highest(2) - ta.lowest(2)
    hiup = math.max(ta.change(high), 0)
    loup = math.max(ta.change(low), 0)
    bulls = math.min((hiup + loup) / R, 1) * 100
    avgbull = ta.wma(nz(bulls), length)
    avgbulls = ta.wma(avgbull, pre_sv) if pre_s else avgbull
    hidn = math.min(ta.change(high), 0)
    lodn = math.min(ta.change(low), 0)
    bears = math.max((hidn + lodn) / R, -1) * -100
    avgbear = ta.wma(nz(bears), length)
    avgbears = ta.wma(avgbear, pre_sv) if pre_s else avgbear
    net = avgbulls - avgbears
    TPX = ta.wma(net, smooth)
    col_bulls: Color = color.new('#33FF0099')
    col_bears: Color = color.new('#FF111166')
    col_level: Color = color.new('#FFEE0070')
    col_TPXup = color.white
    col_TPXdn = color.gray
    TPXBullish = TPX > 0
    hline(0, color=col_level, linestyle=hline.style_solid, linewidth=1, editable=False)
    hline(clevel, title='Control Level', color=col_level, linestyle=hline.style_dotted, linewidth=2)
    plot(avgbulls, title='Bull Pressure', color=col_bulls, style=plot.style_area, linewidth=3)
    plot(avgbears, title='Bear Pressure', color=col_bears, style=plot.style_area, linewidth=3)
    plot(TPX, title='Net Pressure', color=col_TPXup if TPXBullish else col_TPXdn, linewidth=3)
    maxbulls = avgbulls >= clevel
    maxbears = avgbears >= clevel
    TPXswing = ta.cross(TPX, 0)
    plot(slevel if maxbears and slevel_on else na, 'Cold', style=plot.style_circles, color=color.new(color.maroon, 0), linewidth=3)
    plot(slevel if maxbulls and slevel_on else na, 'Hot', style=plot.style_cross, color=color.new(color.green, 0), linewidth=3)
    alertcondition(maxbulls, 'TPX Bulls in Control', 'TPX Bull Pressure >= Control Level')
    alertcondition(maxbears, 'TPX Bears in Control', 'TPX Bear Pressure >= Control Level')
    alertcondition(TPXswing, 'Net Pressure Swing', 'Net Pressure Swing Detected!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)