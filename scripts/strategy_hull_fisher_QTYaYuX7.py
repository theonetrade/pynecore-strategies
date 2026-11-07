"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, fill, input, math, na, nz, open, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Hull Fisher', currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.25, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    period=input.int(title='HullMA Length', defval=14, minval=2),
    length=input.int(9, minval=1, title='Signal Length'),
    line1=input.int(5, minval=2, title='Top Line'),
    line5=input.int(-5, maxval=-2, title='Bottom Line'),
    price: Series[float] = input(open, title='Price data'),
    entry1=input(True, title='Open when HullFisher crossover outside Lines'),
    entry2=input(True, title='Open when HullFisher past zero'),
    useHMA=input(True, title='Include Hull_moving_average'),
    useCCI=input(True, title='Include Commodity_channel_index'),
    fishclose=input(True, title='Close order when Fisher crossover'),
    HMAclose=input(True, title='Close order when Hull crossover')
):
    HMA: Series = ta.hma(price, period)
    HMA2 = HMA[1]
    high_ = ta.highest(HMA, length)
    low_ = ta.lowest(HMA, length)
    def round_(val):
        return 0.999 if val > 0.99 else -0.999 if val < -0.99 else val

    value: Series[float] = 0.0
    value = round_(0.66 * ((HMA - low_) / math.max(high_ - low_, 0.001) - 0.5) + 0.67 * nz(value[1]))
    value1: Series[float] = 0.0
    value1 = 0.5 * math.log((1 + value) / math.max(1 - value, 0.001)) + 0.5 * nz(value1[1])
    value2 = value1[1]
    CCI1: Series = ta.cci(price, period)
    CCI2 = CCI1[1]
    line2 = line1 / 2
    line4 = line5 / 2
    colorchange1 = color.lime if CCI1 > CCI2 else color.red
    colorchange2 = color.lime if value1 > value2 else color.red
    a = plot(line1, style=plot.style_line, color=color.new(color.red, 50), linewidth=2, title='Top Line')
    b = plot(line2, style=plot.style_line, color=color.new(color.red, 50), linewidth=2, title='Upper Line')
    c = plot(0, style=plot.style_line, color=color.new(color.black, 50), linewidth=2, title='Middle Line')
    d = plot(line4, style=plot.style_line, color=color.new(color.lime, 50), linewidth=2, title='Lower Line')
    e = plot(line5, style=plot.style_line, color=color.new(color.lime, 50), linewidth=2, title='Bottom Line')
    f = plot(value1, color=color.new(color.black, 50), linewidth=2, title='Value 1')
    g = plot(value2, color=color.new(color.black, 50), linewidth=2, title='Value 2')
    h = plot(CCI1 / 50, style=plot.style_area, color=colorchange1, linewidth=2, title='CCI')
    fill(f, g, color=color.new(colorchange2, 20), title='Color fill')
    plot(value1 if ta.cross(value1, value2) else na, style=plot.style_circles, color=color.new(color.black, 0), linewidth=10)
    plot(value1 if ta.cross(value1, value2) else na, style=plot.style_circles, color=color.new(color.white, 0), linewidth=8)
    plot(value1 if ta.cross(value1, value2) else na, style=plot.style_circles, color=colorchange2, linewidth=5)
    LongCondition1 = value1 > value2 and value1 < line5 and entry1 and (not useCCI) and (not useHMA)
    ShortCondition1 = value1 < value2 and value1 > line1 and entry1 and (not useCCI) and (not useHMA)
    LongCondition2 = value1 > value2 and value1 > 0 and entry2 and (not useCCI) and (not useHMA)
    ShortCondition2 = value1 < value2 and value1 < 0 and entry2 and (not useCCI) and (not useHMA)
    LongCondition3 = value1 > value2 and value1 < line5 and (CCI1 > CCI2) and entry1 and useCCI and (not useHMA)
    ShortCondition3 = value1 < value2 and value1 > line1 and (CCI1 < CCI2) and entry1 and useCCI and (not useHMA)
    LongCondition4 = value1 > value2 and value1 > 0 and (CCI1 > CCI2) and entry2 and useCCI and (not useHMA)
    ShortCondition4 = value1 < value2 and value1 < 0 and (CCI1 < CCI2) and entry2 and useCCI and (not useHMA)
    LongCondition5 = value1 > value2 and value1 < line5 and (CCI1 > CCI2) and (HMA > HMA2) and entry1 and (not useCCI) and useHMA
    ShortCondition5 = value1 < value2 and value1 > line1 and (CCI1 < CCI2) and (HMA < HMA2) and entry1 and (not useCCI) and useHMA
    LongCondition6 = value1 > value2 and value1 > 0 and (CCI1 > CCI2) and (HMA > HMA2) and entry2 and (not useCCI) and useHMA
    ShortCondition6 = value1 < value2 and value1 < 0 and (CCI1 < CCI2) and (HMA < HMA2) and entry2 and (not useCCI) and useHMA
    LongCondition7 = value1 > value2 and value1 < line5 and (CCI1 > CCI2) and (HMA > HMA2) and entry1 and useCCI and useHMA
    ShortCondition7 = value1 < value2 and value1 > line1 and (CCI1 < CCI2) and (HMA < HMA2) and entry1 and useCCI and useHMA
    LongCondition8 = value1 > value2 and value1 > 0 and (CCI1 > CCI2) and (HMA > HMA2) and entry2 and useCCI and useHMA
    ShortCondition8 = value1 < value2 and value1 < 0 and (CCI1 < CCI2) and (HMA < HMA2) and entry2 and useCCI and useHMA
    if HMAclose and fishclose and (value1 < value2) and (HMA < HMA2):
        strategy.close('BUY')
    if HMAclose and fishclose and (value1 > value2) and (HMA > HMA2):
        strategy.close('SELL')
    if HMAclose and HMA < HMA2:
        strategy.close('BUY')
    if HMAclose and HMA > HMA2:
        strategy.close('SELL')
    if fishclose and value1 < value2:
        strategy.close('BUY')
    if fishclose and value1 > value2:
        strategy.close('SELL')
    if LongCondition1 or LongCondition2 or LongCondition3 or LongCondition4 or LongCondition5 or LongCondition6 or LongCondition7 or LongCondition8:
        strategy.entry('BUY', strategy.long)
    if ShortCondition1 or ShortCondition2 or ShortCondition3 or ShortCondition4 or ShortCondition5 or ShortCondition6 or ShortCondition7 or ShortCondition8:
        strategy.entry('SELL', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
