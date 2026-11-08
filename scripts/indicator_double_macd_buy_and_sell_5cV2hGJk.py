"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bgcolor, close, color, high, hline, input, location, low,
    math, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Series


@script.indicator(shorttitle='MACD_X', title='DOBLE MACD X', overlay=False, na_bool=True)
def main(
    vset=input(True, title='Ver Señal de Entrada de Tendencia'),
    vsct=input(False, title='Ver Señal de Contra Tendencia'),
    afa=input(True, title='Ver Zona Atlas'),
    afc=input(True, title='Ver Zona Choppiness'),
    chopi=input(50.0, title='Nivel Choppiness'),
    div_reg_al=input(True, title='Ver Divergencias Regulares Alcistas'),
    div_reg_ba=input(True, title='Ver Divergencias Regulares Bajistas'),
    div_ocu_al=input(False, title='Ver Divergencias Ocultas Alcistas'),
    div_ocu_ba=input(False, title='Ver Divergencias Ocultas Bajistas'),
    etiquetas=input(True, title='Ver Etiquetas De Divergencias')
):
    negro: Color = color.new('#000000')
    amarillo: Color = color.new('#FFFF00')
    gris: Color = color.new('#C0C0C0')
    rojo: Color = color.new('#FF0000')
    blanco: Color = color.new('#FFFFFF')
    verde_fuerte: Color = color.new('#0AAC00')
    hline(0, color=negro, linestyle=hline.style_solid, editable=False)
    L1: int = 12
    L2: int = 26
    tp = close
    m0 = ta.ema(tp, L1)
    m1 = ta.ema(tp, L2)
    macd_1: Series = m0 - m1
    plot(macd_1, title='Macd 1226', color=color.new(gris, 0), linewidth=2, style=plot.style_line)
    plot(macd_1, title='Macd 1226', color=color.new(gris, 0), linewidth=2, style=plot.style_histogram)
    L1A: int = 5
    L2A: int = 15
    tpa = close
    m0a = ta.ema(tpa, L1A)
    m1a = ta.ema(tpa, L2A)
    macd_2: Series = m0a - m1a
    plot(macd_2, title='MacD 515', color=color.new(amarillo, 0), linewidth=2, style=plot.style_line)
    plot(macd_2, title='MacD 515', color=color.new(amarillo, 0), linewidth=2, style=plot.style_histogram)
    length: int = 20
    src = close
    mult: float = 2.0
    basis = ta.sma(src, length)
    dev = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev
    dbb = math.sqrt((upper - lower) / upper) * 20
    dbbmed = ta.ema(dbb, 120)
    factor = dbbmed * 4 / 5
    atl = dbb - factor
    all = 0 if atl > 0 else 1
    bgcolor(rojo if afa and cast_bool(all) else na, title='Zona Atlas')
    length1: int = 14
    str__ren__ = math.sum(ta.tr, length1)
    ltl = ta.lowest(low if low <= close[1] else close[1], length1)
    hth = ta.highest(high if high >= close[1] else close[1], length1)
    height = hth - ltl
    chop = 100 * (math.log10(str__ren__ / height) / math.log10(length1))
    all1 = 0 if chop < chopi else 1
    bgcolor(rojo if afc and cast_bool(all1) else na, title='Zona Choppiness')
    max = ta.highest(macd_2, 100) * 1.5
    nsc = max
    nsv = max * -1
    midpoint = (nsc + nsv) / 2
    ploff = (nsc - midpoint) / 8
    def f_top_fractal(_src: Series):
        return _src[4] < _src[2] and _src[3] < _src[2] and (_src[2] > _src[1]) and (_src[2] > _src)

    def f_bot_fractal(_src: Series):
        return _src[4] > _src[2] and _src[3] > _src[2] and (_src[2] < _src[1]) and (_src[2] < _src)

    def f_fractalize(_src):
        return 1 if f_top_fractal(_src) else -1 if f_bot_fractal(_src) else 0

    fractal_top1 = macd_2[2] if f_fractalize(macd_2) > 0 else na
    fractal_bot1 = macd_2[2] if f_fractalize(macd_2) < 0 else na
    high_prev1 = inline_series(ta.valuewhen(cast_bool(fractal_top1), macd_2[2], 0), 2)
    high_price1 = inline_series(ta.valuewhen(cast_bool(fractal_top1), high[2], 0), 2)
    low_prev1 = inline_series(ta.valuewhen(cast_bool(fractal_bot1), macd_2[2], 0), 2)
    low_price1 = inline_series(ta.valuewhen(cast_bool(fractal_bot1), low[2], 0), 2)
    regular_bearish_div1 = cast_bool(fractal_top1) and high[2] > high_price1 and (macd_2[2] < high_prev1) and (div_reg_ba == True)
    hidden_bearish_div1 = cast_bool(fractal_top1) and high[2] < high_price1 and (macd_2[2] > high_prev1) and (div_ocu_ba == True)
    regular_bullish_div1 = cast_bool(fractal_bot1) and low[2] < low_price1 and (macd_2[2] > low_prev1) and (div_reg_al == True)
    hidden_bullish_div1 = cast_bool(fractal_bot1) and low[2] > low_price1 and (macd_2[2] < low_prev1) and (div_ocu_al == True)
    col1 = rojo if regular_bearish_div1 else rojo if hidden_bearish_div1 else na
    col2 = verde_fuerte if regular_bullish_div1 else verde_fuerte if hidden_bullish_div1 else na
    plot(title='Divergencias Bajistas', series=macd_2[2] if fractal_top1 else na, color=col1, linewidth=1, offset=-2)
    plot(title='Divergencias Alcistas', series=macd_2[2] if fractal_bot1 else na, color=col2, linewidth=1, offset=-2)
    plotshape(macd_2[1] + ploff * 0.5 if regular_bearish_div1 and div_reg_ba and etiquetas else na, title='Divergencia Regular Bajista', text='🐻 R', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(rojo, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(macd_2[1] + ploff * 0.5 if hidden_bearish_div1 and div_ocu_ba and etiquetas else na, title='Divergencia Oculta Bajista', text='🐻 O', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(rojo, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(macd_2[1] - ploff * 0.5 if regular_bullish_div1 and div_reg_al and etiquetas else na, title='Divergencia Regular Alcista', text='🐂 R', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(verde_fuerte, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(macd_2[1] - ploff * 0.5 if hidden_bullish_div1 and div_ocu_al and etiquetas else na, title='Divergencia Oculta Alcista', text='🐂 O', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(verde_fuerte, 0), textcolor=color.new(blanco, 0), offset=-2)
    largo = ta.crossover(macd_2, 0) and macd_1 < macd_2 and (macd_1[1] < macd_1) and (macd_1 < 0) and vset
    largo1 = ta.crossover(macd_2, macd_1) and macd_2 < 0 and vsct
    plotshape(macd_2 - ploff * 0.75 if largo else na, title='Largo Entrada de Tendencia', location=location.absolute, style=shape.triangleup, size=size.tiny, color=color.new(verde_fuerte, 0))
    plotshape(macd_2 - ploff * 0.75 if largo1 else na, title='Largo Entrada Contra Tendencia', location=location.absolute, style=shape.triangleup, size=size.tiny, color=color.new(verde_fuerte, 0))
    corto = ta.crossunder(macd_2, 0) and macd_1 > macd_2 and (macd_1[1] > macd_1) and (macd_1 > 0) and vset
    corto1 = ta.crossunder(macd_2, macd_1) and macd_2 > 0 and vsct
    plotshape(macd_2 + ploff * 0.75 if corto else na, title='Corto Entrada de Tendencia', location=location.absolute, style=shape.triangledown, size=size.tiny, color=color.new(rojo, 0))
    plotshape(macd_2 + ploff * 0.75 if corto1 else na, title='Corto Entrada Contra Tendencia', location=location.absolute, style=shape.triangledown, size=size.tiny, color=color.new(rojo, 0))
    alertcondition(largo or largo1, title='Compras')
    alertcondition(corto or corto1, title='Ventas')
    alertcondition(largo or largo1 or corto or corto1, title='Compras/Ventas')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
