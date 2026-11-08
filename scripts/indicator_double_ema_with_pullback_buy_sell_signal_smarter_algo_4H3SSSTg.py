"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, high, input, label, low, na,
    plot, script, size, ta
)
from pynecore.types import Series

gr0: str = 'Pullback'
gr1: str = 'Double EMA'
gr4: str = 'Styling'


@script.indicator('Double EMA Pullback - Buy Sell Signal', overlay=True, max_labels_count=500)
def main(
    pbStep=input(5, 'Backstep of Pullback', group=gr0),
    emaSrc: Series[float] = input.source(close, 'EMA 1 Source', group=gr1),
    emaLen=input(50, 'EMA 1 Period', group=gr1),
    emaCol=input.color(color.blue, 'EMA 1 Color', group=gr1),
    emaSrc1: Series[float] = input.source(close, 'EMA 2 Source', group=gr1),
    emaLen1=input(200, 'EMA 2 Period', group=gr1),
    emaCol1=input.color(color.red, 'EMA 2 Color', group=gr1),
    showPattern=input(True, 'Show Pattern Name', group=gr4),
    textCol=input.color(color.white, 'Text Color', group=gr4),
    bullText=input.string('Buy', 'Buy Signal', inline='ul', group=gr4),
    bullCol=input.color(color.green, '', tooltip='', inline='ul', group=gr4),
    bearText=input('Sell', 'Sell Signal', tooltip='', inline='ms', group=gr4),
    bearCol=input.color(color.red, '', tooltip='', inline='ms', group=gr4)
):
    ema1 = ta.ema(emaSrc, emaLen)
    plot(ema1, 'EMA 1', color=emaCol)
    ema2 = ta.ema(emaSrc1, emaLen1)
    plot(ema2, 'EMA 2', color=emaCol1)
    buySignal = ta.crossover(close, ema1) and ema1 > ema2 and (close[pbStep] > ema1)
    sellSignal = ta.crossunder(close, ema1) and ema1 < ema2 and (close[pbStep] < ema1)
    def fLabel(x, y):
        labelStyle = label.style_label_down if y == high else label.style_label_up
        labelCol = bearCol if y == high else bullCol
        labelText = bearText if y == high else bullText
        __block_result__ = na
        if x:
            __block_result__ = label.new(bar_index, y, labelText, style=labelStyle, color=labelCol, size=size.small, textcolor=textCol)
        return __block_result__

    fLabel(buySignal, low)
    fLabel(sellSignal, high)
    alertcondition(buySignal, 'Buy Signal', 'Buy!!')
    alertcondition(sellSignal, 'Sell Signal', 'Sell!!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
