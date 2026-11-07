"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, high, input, location, low, math, open, plot,
    plotshape, request, script, shape, strategy, syminfo, ta
)


@script.strategy('Só Trade Top - Média de 8 - Augusto Backes', overlay=True, max_bars_back=5000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=10000, commission_type=strategy.commission.percent, process_orders_on_close=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    tipo_media=input.string(title='Tipo de Média', defval='EMA', options=('SMA', 'EMA'), inline='3', group='SETUP MÉDIA DE 8', tooltip='Média utilizada para os cálculos do Setup'),
    c_media=input.int(defval=8, title='Comprimento', inline='3', group='SETUP MÉDIA DE 8'),
    cb_raro=input.bool(True, title='Habilitar Sinal Raro', group='SETUP MÉDIA DE 8', tooltip='Sinais normais são caracterizados por Engolfos, Martelos e Preço de Fechamento de Reversão com FECHAMENTO acima da Média de 8. Sinais Raros são caracterizados pelas mesmas figuras, mas com FECHAMENTO e ABERTURA acima da média de 8. O mesmo vale para sinais de venda.')
):
    media8 = request.security(syminfo.tickerid, '1W', ta.sma(close[1], c_media)) if tipo_media == 'SMA' else request.security(syminfo.tickerid, '1W', ta.ema(close[1], c_media))
    plot(media8, title='Média', color=color.new(color.green, 0), linewidth=2)
    lookback_swing: int = 5
    candle_engolfo = close > open and close[1] < open[1] and (close >= open[1]) and (open <= close[1]) and (close > media8)
    candle_martelo = 2 * math.abs(close - open) < math.min(close, open) - low and high - math.max(close, open) < math.abs(close - open) and (close > open) and (close > media8)
    candle_fr = low < low[1] and low < low[2] and (close > close[1]) and (close > open) and (close > media8)
    compra = candle_engolfo or candle_martelo or candle_fr
    vcandle_engolfo = close < open and close[1] > open[1] and (close <= open[1]) and (open >= close[1]) and (close < media8)
    vcandle_martelo = 2 * math.abs(close - open) < high - math.max(close, open) and math.min(close, open) - low < math.abs(close - open) and (close < open) and (close < media8)
    vcandle_fr = high > high[1] and high > high[2] and (close < close[1]) and (close < open) and (close < media8)
    venda = vcandle_engolfo or vcandle_martelo or vcandle_fr
    if cb_raro:
        compra = compra and open > media8
        venda = venda and open < media8
    else:
        compra = compra
        venda = venda
    barcolor(color.green if compra and strategy.position_size == 0 else color.red if venda and strategy.position_size > 0 else color.new(color.black, 100))
    plotshape(compra and candle_engolfo and (strategy.position_size == 0), title='Engolfo de Alta', style=shape.labeldown, color=color.new(color.green, 0), text='Engolfo de Alta', textcolor=color.new(color.white, 0))
    plotshape(compra and candle_martelo and (strategy.position_size == 0), title='Martelo de Alta', style=shape.labeldown, color=color.new(color.green, 0), text='Martelo de Alta', textcolor=color.new(color.white, 0))
    plotshape(compra and candle_fr and (strategy.position_size == 0), title='PFR de Alta', style=shape.labeldown, color=color.new(color.green, 0), text='PFR de Alta', textcolor=color.new(color.white, 0))
    plotshape(venda and vcandle_engolfo and (strategy.position_size > 0), title='Engolfo de Baixa', style=shape.labelup, location=location.belowbar, color=color.new(color.red, 0), text='Engolfo de Baixa', textcolor=color.new(color.white, 0))
    plotshape(venda and vcandle_martelo and (strategy.position_size > 0), title='Martelo de Baixa', style=shape.labelup, location=location.belowbar, color=color.new(color.red, 0), text='Martelo de Baixa', textcolor=color.new(color.white, 0))
    plotshape(venda and vcandle_fr and (strategy.position_size > 0), title='PFR de Baixa', style=shape.labelup, location=location.belowbar, color=color.new(color.red, 0), text='PFR de Baixa', textcolor=color.new(color.white, 0))
    if compra:
        strategy.entry('Compra', strategy.long)
    if venda:
        strategy.close('Compra')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
