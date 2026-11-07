"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, fill, input, na, plot, script, strategy,
    ta, time, timestamp
)
from pynecore.types import Persistent, Series

GRUPO_per_pruebas: str = 'Período de pruebas'
GRUPO_P: str = 'Posiciones'
GRUPO_TPSL: str = 'Stop Loss y Take Profit (ATR)'
GRUPO_BE: str = 'Break Even (ATR)'
GRUPO_general: str = 'General'
GRUPO_MAs: str = 'MAs'
GRUPO_RSI: str = 'RSI'
GRUPO_ATR: str = 'ATR'


@script.strategy('Larry Connors Strategy [JoseMetal]', shorttitle='Larry Connors Strategy [JoseMetal]', overlay=True, initial_capital=10000, pyramiding=0, default_qty_value=10, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.0, max_labels_count=500, max_bars_back=1000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    fecha_inicio=input.time(0, '• Fecha de inicio', group=GRUPO_per_pruebas, tooltip='Las fechas son inclusivas'),
    fecha_fin_usar=input.bool(False, 'Fecha de finalización', group=GRUPO_per_pruebas, inline='fecha_finalizacion'),
    fecha_fin=input.time(timestamp('1 Jan 2999'), '', group=GRUPO_per_pruebas, inline='fecha_finalizacion'),
    P_permitir_LONGS=input.bool(title='¿LONGS?', group=GRUPO_P, defval=True, inline='pos_activadas'),
    P_permitir_SHORTS=input.bool(title='¿SHORTS?', group=GRUPO_P, defval=True, inline='pos_activadas'),
    TPSL_SL_ATR_usar=input.bool(False, '¿Usar Stop Loss? / Mult. ATR', group=GRUPO_TPSL, inline='stop_loss'),
    TPSL_SL_ATR_mult=input.float(3.1, '', group=GRUPO_TPSL, minval=0.1, step=0.1, inline='stop_loss', tooltip='Si está activado, se usará el ATR multiplicado por éste valor como Stop Loss'),
    TPSL_TP_ATR_usar=input.bool(False, '¿Usar Take Profit? / Mult. ATR', group=GRUPO_TPSL, inline='take_profit'),
    TPSL_TP_ATR_mult=input.float(3.1, '', group=GRUPO_TPSL, minval=0.1, step=0.1, inline='take_profit', tooltip='Si está activado, se usará el ATR multiplicado por éste valor como Take Profit'),
    usar_be=input.bool(False, '¿Proteger posiciones? (Break Even)', group=GRUPO_BE),
    TPSL_break_even_req_mult=input.float(title='• Mult. para BREAK EVEN y STOP LOSS', group=GRUPO_BE, defval=1.0, minval=0.0, step=0.1, inline='be', tooltip='Cuando el precio avance a nuestro favor y llegue éste ATR, el Stop Loss se moverá a BREAK EVEN, de modo que la operación quede protegida.\nEl \'nivel de stop loss\' nos permite que el stop se mueva aún más a favor de nuestro precio de entrada para además asegurar ganancias'),
    TPSL_break_even_mult=input.float(title='', group=GRUPO_BE, defval=0.8, minval=0.0, step=0.1, inline='be'),
    mostrar_color_velas=input.bool(title='Colorear velas', defval=True, group=GRUPO_general),
    mostrar_color_velas_2=input.bool(title='Marcar velas neutras', defval=True, group=GRUPO_general),
    MA_SALIDA_tipo=input.string(title='• (Media de salida) Tipo / Fuente / Long.', group=GRUPO_MAs, defval='SMA', options=('SMA', 'EMA', 'WMA', 'HMA'), inline='ma_salida'),
    MA_SALIDA_fuente: Series[float] = input.source(title='', group=GRUPO_MAs, defval=close, inline='ma_salida'),
    MA_SALIDA_length=input.int(title='', group=GRUPO_MAs, defval=10, minval=1, inline='ma_salida'),
    MA_TENDENCIA_tipo=input.string(title='• (Media de tendencia) Tipo / Fuente / Long.', group=GRUPO_MAs, defval='SMA', options=('SMA', 'EMA', 'WMA', 'HMA'), inline='ma_tendencia'),
    MA_TENDENCIA_fuente: Series[float] = input.source(title='', group=GRUPO_MAs, defval=close, inline='ma_tendencia'),
    MA_TENDENCIA_length=input.int(title='', group=GRUPO_MAs, defval=200, minval=1, inline='ma_tendencia'),
    RSI_src: Series[float] = input.source(title='• Fuente / Longitud', group=GRUPO_RSI, defval=close, inline='rsi_calc'),
    RSI_length=input.int(title='', group=GRUPO_RSI, defval=2, minval=1, inline='rsi_calc'),
    RSI_nivel_os=input.int(title='• Sobreventa / Sobrecompra', group=GRUPO_RSI, defval=5, minval=0, maxval=99, inline='rsi_niveles'),
    RSI_nivel_ob=input.int(title='', group=GRUPO_RSI, defval=95, minval=1, maxval=100, inline='rsi_niveles'),
    ATR_referencia: Series[float] = input.source(title='• Referencia / Longitud', group=GRUPO_ATR, defval=close, inline='atr_calc'),
    ATR_length=input.int(title='', group=GRUPO_ATR, defval=7, minval=1, inline='atr_calc')
):
    c_blanco = color.rgb(255, 255, 255, 0)
    c_negro = color.rgb(0, 0, 0, 0)
    c_amarillo_radiactivo = color.rgb(255, 255, 0, 0)
    c_cian_radiactivo = color.rgb(0, 255, 255, 0)
    c_verde_radiactivo = color.rgb(0, 255, 0, 0)
    c_verde = color.rgb(0, 128, 0, 0)
    c_verde_oscuro = color.rgb(0, 80, 0, 0)
    c_rojo_radiactivo = color.rgb(255, 0, 0, 0)
    c_rojo = color.rgb(128, 0, 0, 0)
    c_rojo_oscuro = color.rgb(80, 0, 0, 0)
    c_naranja_oscuro = color.rgb(200, 120, 0, 0)
    noneColor = color.new(color.white, 100)
    max_float: float = 10000000000.0
    vela_en_fecha = time >= fecha_inicio and (time <= fecha_fin if fecha_fin_usar else True)
    posicion_abierta = strategy.position_size != 0
    LONG_abierto = strategy.position_size > 0
    SHORT_abierto = strategy.position_size < 0
    MA_SALIDA = ta.sma(MA_SALIDA_fuente, MA_SALIDA_length)
    MA_TENDENCIA = ta.sma(MA_TENDENCIA_fuente, MA_TENDENCIA_length)
    if MA_SALIDA_tipo == 'EMA':
        MA_SALIDA = ta.ema(MA_SALIDA_fuente, MA_SALIDA_length)
    elif MA_SALIDA_tipo == 'WMA':
        MA_SALIDA = ta.wma(MA_SALIDA_fuente, MA_SALIDA_length)
    elif MA_SALIDA_tipo == 'HMA':
        MA_SALIDA = ta.hma(MA_SALIDA_fuente, MA_SALIDA_length)
    if MA_TENDENCIA_tipo == 'EMA':
        MA_TENDENCIA = ta.ema(MA_TENDENCIA_fuente, MA_TENDENCIA_length)
    elif MA_TENDENCIA_tipo == 'WMA':
        MA_TENDENCIA = ta.wma(MA_TENDENCIA_fuente, MA_TENDENCIA_length)
    elif MA_TENDENCIA_tipo == 'HMA':
        MA_TENDENCIA = ta.hma(MA_TENDENCIA_fuente, MA_TENDENCIA_length)
    RSI = ta.rsi(RSI_src, RSI_length)
    ATR = ta.atr(ATR_length)
    ATR_sl = ATR * TPSL_SL_ATR_mult
    ATR_tp = ATR * TPSL_TP_ATR_mult
    ATR_be_req = ATR * TPSL_break_even_req_mult
    ATR_be = ATR * TPSL_break_even_mult
    ATR_LONG_sl = ATR_referencia - ATR_sl
    ATR_LONG_tp = ATR_referencia + ATR_tp
    ATR_SHORT_sl = ATR_referencia + ATR_sl
    ATR_SHORT_tp = ATR_referencia - ATR_tp
    ATR_LONG_break_even_req = ATR_referencia + ATR_be_req
    ATR_SHORT_break_even_req = ATR_referencia - ATR_be_req
    ATR_LONG_break_even = ATR_referencia + ATR_be
    ATR_SHORT_break_even = ATR_referencia - ATR_be
    cierre_sobre_MA_SALIDA = close > MA_SALIDA
    tendencia_alcista = close > MA_TENDENCIA
    RSI_en_sobreventa: Series = RSI < RSI_nivel_os
    RSI_en_sobrecompra: Series = RSI > RSI_nivel_ob
    exit_LONG_conditions = cierre_sobre_MA_SALIDA
    exit_SHORT_conditions = not cierre_sobre_MA_SALIDA
    if LONG_abierto and exit_LONG_conditions:
        strategy.close('Abrir Long')
    if SHORT_abierto and exit_SHORT_conditions:
        strategy.close('Abrir Short')
    LONG_condition_1 = tendencia_alcista
    LONG_condition_2 = not cierre_sobre_MA_SALIDA
    LONG_condition_3 = RSI_en_sobreventa[1] and (not RSI_en_sobreventa)
    all_LONG_conditions = LONG_condition_1 and LONG_condition_2 and LONG_condition_3
    entrar_en_LONG = P_permitir_LONGS and all_LONG_conditions and vela_en_fecha and (not LONG_abierto)
    SHORT_condition_1 = not tendencia_alcista
    SHORT_condition_2 = cierre_sobre_MA_SALIDA
    SHORT_condition_3 = RSI_en_sobrecompra[1] and (not RSI_en_sobrecompra)
    all_SHORT_conditions = SHORT_condition_1 and SHORT_condition_2 and SHORT_condition_3
    entrar_en_SHORT = P_permitir_SHORTS and all_SHORT_conditions and vela_en_fecha and (not SHORT_abierto)
    LONG_stop_loss: Persistent[float] = 0.0
    LONG_take_profit: Persistent = max_float
    LONG_break_even_req: Persistent[float] = 0.0
    LONG_break_even: Persistent[float] = 0.0
    SHORT_stop_loss: Persistent = max_float
    SHORT_take_profit: Persistent[float] = 0.0
    SHORT_break_even_req: Persistent[float] = 0.0
    SHORT_break_even: Persistent[float] = 0.0
    en_be: Persistent[bool] = False
    if not posicion_abierta:
        en_be = False
        LONG_stop_loss = 0.0
        LONG_take_profit = max_float
        SHORT_stop_loss = max_float
        SHORT_take_profit = 0.0
    if not posicion_abierta:
        if entrar_en_LONG:
            if TPSL_SL_ATR_usar:
                LONG_stop_loss = ATR_LONG_sl
            if TPSL_TP_ATR_usar:
                LONG_take_profit = ATR_LONG_tp
            if usar_be:
                LONG_break_even_req = ATR_LONG_break_even_req
                LONG_break_even = ATR_LONG_break_even
            strategy.entry('Abrir Long', strategy.long)
            strategy.exit('Cerrar Long', 'Abrir Long', stop=LONG_stop_loss if TPSL_SL_ATR_usar else na, limit=LONG_take_profit if TPSL_TP_ATR_usar else na)
        elif entrar_en_SHORT:
            if TPSL_SL_ATR_usar:
                SHORT_stop_loss = ATR_SHORT_sl
            if TPSL_TP_ATR_usar:
                SHORT_take_profit = ATR_SHORT_tp
            if usar_be:
                SHORT_break_even_req = ATR_SHORT_break_even_req
                SHORT_break_even = ATR_SHORT_break_even
            strategy.entry('Abrir Short', strategy.short)
            strategy.exit('Cerrar Short', 'Abrir Short', stop=SHORT_stop_loss if TPSL_SL_ATR_usar else na, limit=SHORT_take_profit if TPSL_TP_ATR_usar else na)
    if usar_be and (not en_be):
        if LONG_abierto and LONG_stop_loss < LONG_break_even and (close > LONG_break_even_req):
            LONG_stop_loss = LONG_break_even
            strategy.exit('Cerrar Long', 'Abrir Long', stop=LONG_stop_loss, limit=LONG_take_profit if TPSL_TP_ATR_usar else na)
            en_be = True
        elif SHORT_abierto and SHORT_stop_loss > SHORT_break_even and (close < SHORT_break_even_req):
            SHORT_stop_loss = SHORT_break_even
            strategy.exit('Cerrar Short', 'Abrir Short', stop=SHORT_stop_loss, limit=SHORT_take_profit if TPSL_TP_ATR_usar else na)
            en_be = True
    plot(MA_SALIDA, 'Media de salida', color=color.aqua, linewidth=2)
    plot(MA_TENDENCIA, 'Media tendencial', color=color.new('#00A800') if tendencia_alcista else color.new('#CA0000'), linewidth=4)
    bgcolor__ren__ = color.new(color.green, 85) if entrar_en_LONG else color.new(color.red, 85) if entrar_en_SHORT else color.new(color.black, 100)
    bgcolor(bgcolor__ren__)
    color_velas = (c_verde_radiactivo if RSI_en_sobreventa else c_rojo_radiactivo if RSI_en_sobrecompra else c_negro if mostrar_color_velas_2 else na) if mostrar_color_velas else na
    barcolor(color_velas)
    avg_position_price_plot = plot(strategy.position_avg_price if posicion_abierta else na, color=color.new(color.white, 25), style=plot.style_linebr, linewidth=2, title='Precio Entrada')
    break_even_req_plot = plot((LONG_break_even_req if LONG_abierto else SHORT_break_even_req) if posicion_abierta and usar_be and (not en_be) else na, color=color.new(color.blue, 25), style=plot.style_linebr, linewidth=1, title="Nivel requerido para activar 'Break Even'")
    break_even_plot = plot((LONG_break_even if LONG_abierto else SHORT_break_even) if posicion_abierta and usar_be and (not en_be) else na, color=color.new(color.aqua, 25), style=plot.style_linebr, linewidth=1, title="Nivel de 'Break Even'")
    LONG_sl_plot = plot(LONG_stop_loss if LONG_abierto and LONG_stop_loss > 0.0 else na, color=color.new(color.aqua, 25) if en_be else color.new(color.red, 25), style=plot.style_linebr, linewidth=3, title='Long Stop Loss')
    LONG_tp_plot = plot(LONG_take_profit if LONG_abierto and LONG_take_profit < max_float else na, color=color.new(color.lime, 25), style=plot.style_linebr, linewidth=3, title='LONG Take Profit')
    fill(avg_position_price_plot, LONG_sl_plot, color=color.new(color.maroon, 85))
    fill(avg_position_price_plot, LONG_tp_plot, color=color.new(color.olive, 85))
    SHORT_sl_plot = plot(SHORT_stop_loss if SHORT_abierto and SHORT_stop_loss < max_float else na, color=color.new(color.aqua, 25) if en_be else color.new(color.red, 25), style=plot.style_linebr, linewidth=3, title='Short Stop Loss')
    SHORT_tp_plot = plot(SHORT_take_profit if SHORT_abierto and SHORT_take_profit > 0.0 else na, color=color.new(color.lime, 25), style=plot.style_linebr, linewidth=3, title='SHORT Take Profit')
    fill(avg_position_price_plot, SHORT_sl_plot, color=color.new(color.maroon, 85))
    fill(avg_position_price_plot, SHORT_tp_plot, color=color.new(color.olive, 85))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
