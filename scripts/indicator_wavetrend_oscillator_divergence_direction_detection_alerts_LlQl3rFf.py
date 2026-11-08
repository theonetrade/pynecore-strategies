"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, color, fill, high, hlc3, input, location, low,
    math, na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Series


@script.indicator(shorttitle='WT_X', title='Oscilador WaveTrend', overlay=False, na_bool=True)
def main(
    n1=input(10, 'Longitud Del Canal'),
    n2=input(21, 'Periodo Movil'),
    reaction_wt=input.int(defval=1, title='Reaccion En Cambio De Direccion', minval=1),
    nsc=input.float(53, 'Nivel Sobre Compra', minval=0.0),
    nsv=input.float(-53, 'Nivel Sobre Venta', maxval=-0.0),
    ventas_en_sobre_compra=input(True, title='Solo Ventas en Sobre Compra'),
    compras_en_sobre_venta=input(True, title='Solo Compras en Sobre Venta'),
    histograma=input(True, title='Ver Histograma'),
    senal=input(False, title='Ver Media de Señal'),
    barras=input(True, title='Pintar Barras'),
    div_reg_al=input(False, title='Ver Divergencias Regulares Alcistas'),
    div_reg_ba=input(False, title='Ver Divergencias Regulares Bajistas'),
    div_ocu_al=input(False, title='Ver Divergencias Ocultas Alcistas'),
    div_ocu_ba=input(False, title='Ver Divergencias Ocultas Bajistas'),
    etiquetas=input(True, title='Ver Etiquetas De Divergencias'),
    amme=input(False, title='Activar media movil Extra para WT'),
    ma_type=input.string(defval='EMA', title='MA Extra Tipo: ', options=('SMA', 'EMA', 'WMA', 'VWMA', 'SMMA', 'DEMA', 'TEMA', 'HullMA', 'ZEMA', 'TMA', 'SSMA')),
    ma_len=input.int(defval=200, title='MA Extra Periodo', minval=1),
    reaction=input.int(defval=1, title='MA Extra Reaccion', minval=1)
):
    nsc1 = nsc
    nsc2 = nsc + 5
    nsc3 = nsc + 10
    nsc4 = nsc + 15
    nsc5 = nsc + 20
    nsc6 = nsc + 25
    nsc7 = nsc + 30
    nsc8 = nsc + 35
    nsv1 = nsv - 5
    nsv2 = nsv - 10
    nsv3 = nsv - 15
    nsv4 = nsv - 20
    nsv5 = nsv - 25
    nsv6 = nsv - 30
    nsv7 = nsv - 35
    nsv8 = nsv - 40
    blanco: Color = color.new('#FDFEFE')
    negro: Color = color.new('#000000')
    rojo: Color = color.new('#FF0000')
    verde: Color = color.new('#00FF13')
    verde_fuerte: Color = color.new('#0AAC00')
    verde_1: Color = color.new('#00FF00')
    celeste: Color = color.new('#00D4FF')
    celeste_1: Color = color.new('#009BBA')
    naranja: Color = color.new('#FF8B00')
    amarillo: Color = color.new('#FFFB00')
    azul: Color = color.new('#0066FF')
    rosa: Color = color.new('#FF33CC')
    ap = hlc3
    esa = ta.ema(ap, n1)
    d = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1: Series = tci
    wt2: Series = ta.sma(wt1, 4)
    direction: Series[int] = 0
    direction = 1 if ta.rising(wt1, reaction_wt) else -1 if ta.falling(wt1, reaction_wt) else nz(direction[1])
    cambio_direccion = ta.change(direction, 1)
    pcol = verde_fuerte if direction > 0 else rojo if direction < 0 else na
    plot(wt1, title='Media WT', color=pcol, linewidth=1, style=plot.style_line)
    plot(wt2 if senal else na, style=plot.style_line, color=color.new(naranja, 0), linewidth=1, title='Media Señal')
    plot(0, title='Nivel 0', color=color.new(negro, 50), linewidth=1, style=plot.style_line)
    pnsc1 = plot(nsc1, title='Nivel 1 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc2 = plot(nsc2, title='Nivel 2 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc3 = plot(nsc3, title='Nivel 3 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc4 = plot(nsc4, title='Nivel 4 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc5 = plot(nsc5, title='Nivel 5 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc6 = plot(nsc6, title='Nivel 6 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc7 = plot(nsc7, title='Nivel 7 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    pnsc8 = plot(nsc8, title='Nivel 8 Sobre Compra', color=color.new(rojo, 100), linewidth=1, style=plot.style_line)
    fill(pnsc1, pnsc2, color=color.new(rojo, 75))
    fill(pnsc2, pnsc3, color=color.new(rojo, 70))
    fill(pnsc3, pnsc4, color=color.new(rojo, 65))
    fill(pnsc4, pnsc5, color=color.new(rojo, 60))
    fill(pnsc5, pnsc6, color=color.new(rojo, 55))
    fill(pnsc6, pnsc7, color=color.new(rojo, 50))
    fill(pnsc7, pnsc8, color=color.new(rojo, 45))
    pnsv1 = plot(nsv1, title='Nivel 1 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv2 = plot(nsv2, title='Nivel 2 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv3 = plot(nsv3, title='Nivel 3 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv4 = plot(nsv4, title='Nivel 4 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv5 = plot(nsv5, title='Nivel 5 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv6 = plot(nsv6, title='Nivel 6 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv7 = plot(nsv7, title='Nivel 7 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    pnsv8 = plot(nsv8, title='Nivel 8 Sobre Venta', color=color.new(verde, 100), linewidth=1, style=plot.style_line)
    fill(pnsv1, pnsv2, color=color.new(verde, 75))
    fill(pnsv2, pnsv3, color=color.new(verde, 70))
    fill(pnsv3, pnsv4, color=color.new(verde, 65))
    fill(pnsv4, pnsv5, color=color.new(verde, 60))
    fill(pnsv5, pnsv6, color=color.new(verde, 55))
    fill(pnsv6, pnsv7, color=color.new(verde, 50))
    fill(pnsv7, pnsv8, color=color.new(verde, 45))
    midpoint = (nsc + nsv) / 2
    ploff = (nsc - midpoint) / 8
    venta = ta.crossunder(wt1, wt2) and wt1 >= nsc and (ventas_en_sobre_compra == True)
    venta_1 = ta.crossunder(wt1, wt2) and ventas_en_sobre_compra == False
    compra = ta.crossover(wt1, wt2) and wt1 <= nsv and (compras_en_sobre_venta == True)
    compra_1 = ta.crossover(wt1, wt2) and compras_en_sobre_venta == False
    plot(wt2[1] + ploff if venta else na, style=plot.style_circles, color=color.new(rojo, 0), linewidth=3, title='Ventas En Sobre Compra')
    plot(wt2[1] + ploff if venta_1 else na, style=plot.style_circles, color=color.new(rojo, 0), linewidth=3, title='Todas Las Ventas')
    plot(wt2[1] - ploff if compra else na, style=plot.style_circles, color=color.new(verde_fuerte, 0), linewidth=3, title='Compras En Sobre Venta')
    plot(wt2[1] - ploff if compra_1 else na, style=plot.style_circles, color=color.new(verde_fuerte, 0), linewidth=3, title='Todas Las Compras')
    plot(wt1 - wt2 if histograma else na, style=plot.style_area, color=color.new(celeste_1, 80), linewidth=1, title='Histograma')
    barcolor(verde_1 if barras == True and compra == True or (barras == True and compra_1 == True) else na)
    barcolor(rojo if barras == True and venta == True or (barras == True and venta_1 == True) else na)
    def f_top_fractal(_src: Series):
        return _src[4] < _src[2] and _src[3] < _src[2] and (_src[2] > _src[1]) and (_src[2] > _src)

    def f_bot_fractal(_src: Series):
        return _src[4] > _src[2] and _src[3] > _src[2] and (_src[2] < _src[1]) and (_src[2] < _src)

    def f_fractalize(_src):
        return 1 if f_top_fractal(_src) else -1 if f_bot_fractal(_src) else 0

    fractal_top1 = wt1[2] if f_fractalize(wt1) > 0 else na
    fractal_bot1 = wt1[2] if f_fractalize(wt1) < 0 else na
    high_prev1 = inline_series(ta.valuewhen(cast_bool(fractal_top1), wt1[2], 0), 2)
    high_price1 = inline_series(ta.valuewhen(cast_bool(fractal_top1), high[2], 0), 2)
    low_prev1 = inline_series(ta.valuewhen(cast_bool(fractal_bot1), wt1[2], 0), 2)
    low_price1 = inline_series(ta.valuewhen(cast_bool(fractal_bot1), low[2], 0), 2)
    regular_bearish_div1 = cast_bool(fractal_top1) and high[2] > high_price1 and (wt1[2] < high_prev1) and (div_reg_ba == True)
    hidden_bearish_div1 = cast_bool(fractal_top1) and high[2] < high_price1 and (wt1[2] > high_prev1) and (div_ocu_ba == True)
    regular_bullish_div1 = cast_bool(fractal_bot1) and low[2] < low_price1 and (wt1[2] > low_prev1) and (div_reg_al == True)
    hidden_bullish_div1 = cast_bool(fractal_bot1) and low[2] > low_price1 and (wt1[2] < low_prev1) and (div_ocu_al == True)
    col1 = rojo if regular_bearish_div1 else rojo if hidden_bearish_div1 else na
    col2 = verde_fuerte if regular_bullish_div1 else verde_fuerte if hidden_bullish_div1 else na
    plot(title='Divergencias Bajistas', series=wt1[2] if fractal_top1 else na, color=col1, linewidth=2, offset=-2)
    plot(title='Divergencias Alcistas', series=wt1[2] if fractal_bot1 else na, color=col2, linewidth=2, offset=-2)
    plotshape(wt1[1] + ploff * 1 if regular_bearish_div1 and div_reg_ba and etiquetas else na, title='Divergencia Regular Bajista', text='🐻 R', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(rojo, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(wt1[1] + ploff * 1 if hidden_bearish_div1 and div_ocu_ba and etiquetas else na, title='Divergencia Oculta Bajista', text='🐻 O', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(rojo, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(wt1[1] - ploff * 1 if regular_bullish_div1 and div_reg_al and etiquetas else na, title='Divergencia Regular Alcista', text='🐂 R', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(verde_fuerte, 0), textcolor=color.new(blanco, 0), offset=-2)
    plotshape(wt1[1] - ploff * 1 if hidden_bullish_div1 and div_ocu_al and etiquetas else na, title='Divergencia Oculta Alcista', text='🐂 O', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(verde_fuerte, 0), textcolor=color.new(blanco, 0), offset=-2)
    ma_src = wt1
    def variant_supersmoother(src: Series, len):
        a1 = math.exp(-1.414 * 3.14159 / len)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / len)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        v9: Series[float] = 0.0
        v9 = c1 * (src + nz(src[1])) / 2 + c2 * nz(v9[1]) + c3 * nz(v9[2])
        return v9

    def variant_smoothed(src, len):
        v5: Series[float] = 0.0
        sma_1 = ta.sma(src, len)
        v5 = sma_1 if na(v5[1]) else (v5[1] * (len - 1) + src) / len
        return v5

    def variant_zerolagema(src, len):
        ema1 = ta.ema(src, len)
        ema2 = ta.ema(ema1, len)
        v10 = ema1 + ema1 - ema2
        return v10

    def variant_doubleema(src, len):
        v2 = ta.ema(src, len)
        v6 = 2 * v2 - ta.ema(v2, len)
        return v6

    def variant_tripleema(src, len):
        v2 = ta.ema(src, len)
        v7 = 3 * (v2 - ta.ema(v2, len)) + ta.ema(ta.ema(v2, len), len)
        return v7

    def variant(type, src, len):
        ema_1 = ta.ema(src, len)
        wma_1 = ta.wma(src, len)
        vwma_1 = ta.vwma(src, len)
        variant_smoothed__1 = variant_smoothed(src, len)
        variant_doubleema__1 = variant_doubleema(src, len)
        variant_tripleema__1 = variant_tripleema(src, len)
        wma_2 = ta.wma(src, len / 2)
        wma_3 = ta.wma(src, len)
        wma_4 = ta.wma(2 * wma_2 - wma_3, math.round(math.sqrt(len)))
        variant_supersmoother__1 = variant_supersmoother(src, len)
        variant_zerolagema__1 = variant_zerolagema(src, len)
        sma_1 = ta.sma(src, len)
        sma_2 = ta.sma(sma_1, len)
        sma_3 = ta.sma(src, len)
        return ema_1 if type == 'EMA' else wma_1 if type == 'WMA' else vwma_1 if type == 'VWMA' else variant_smoothed__1 if type == 'SMMA' else variant_doubleema__1 if type == 'DEMA' else variant_tripleema__1 if type == 'TEMA' else wma_4 if type == 'HullMA' else variant_supersmoother__1 if type == 'SSMA' else variant_zerolagema__1 if type == 'ZEMA' else sma_2 if type == 'TMA' else sma_3

    ma_series = variant(ma_type, ma_src, ma_len)
    direction_a: Series[int] = 0
    falling_1 = ta.falling(ma_series, reaction)
    direction_a = 1 if ta.rising(ma_series, reaction) else -1 if falling_1 else nz(direction_a[1])
    change_direction = ta.change(direction_a, 1)
    pcol_a = color.new('#2E8B57') if direction_a > 0 else color.new('#FF4500') if direction_a < 0 else na
    plot(ma_series if amme else na, color=pcol_a, style=plot.style_line, join=True, linewidth=3, title='MA PLOT')
    alertcondition(venta, title='Ventas en Sobre Compra')
    alertcondition(venta_1, title='Todas las Ventas')
    alertcondition(compra, title='Compras en Sobre Venta')
    alertcondition(compra_1, title='Todas las Compras')
    alertcondition(venta or compra, title='Compras/Ventas en Sobre Compra/Venta')
    alertcondition(venta_1 or compra_1, title='Todas las Ventas/Compras')
    alertcondition(cast_bool(cambio_direccion), title='Cambio Direccion WT')
    alertcondition(venta, title='Overbought Sales')
    alertcondition(venta_1, title='All Sales')
    alertcondition(compra, title='Oversold Buys')
    alertcondition(compra_1, title='All Buys')
    alertcondition(venta or compra, title='Buys/Sales Overbought/Oversold')
    alertcondition(venta_1 or compra_1, title='All Sales/Buys')
    alertcondition(cast_bool(cambio_direccion), title='WT Direction Change')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
