"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, bar_index, barcolor, chart, close, color, display, fill, format,
    high, input, label, location, low, math, na, open, plot, plotcandle, plotshape, position,
    script, shape, size, string, ta, table, text, volume
)
from pynecore.types import Color, Persistent, Series, Table


@udt
class OHLCV:
    O: float = _dataclass_field(default_factory=lambda: open)
    H: float = _dataclass_field(default_factory=lambda: high)
    L: float = _dataclass_field(default_factory=lambda: low)
    C: float = _dataclass_field(default_factory=lambda: close)
    V: float = _dataclass_field(default_factory=lambda: volume)


@udt
class VolumeData:
    buyVol: float = na(float)
    sellVol: float = na(float)
    pcBuy: float = na(float)
    pcSell: float = na(float)
    isBuyGreater: bool = na(bool)
    higherVol: float = na(float)
    lowerVol: float = na(float)
    higherCol: Color = na(Color)
    lowerCol: Color = na(Color)


FV = format.volume


@script.indicator('Volume Delta [hapharmonic]', format=FV, max_bars_back=4999, max_labels_count=500)
def main(
    usecandle=input.bool(True, title='Volume on Candles', display=display.none),
    C_Up=input.color(color.new('#12CEF8'), title='Volume Buy', inline=' ', group='Style'),
    C_Down=input.color(color.new('#FE3F00'), title='Volume Sell', inline=' ', group='Style'),
    P_=input.string(position.top_right, "Position", options=(position.top_right, position.top_center, position.middle_right, position.middle_left, position.bottom_center, position.middle_center, position.bottom_left, position.bottom_right, position.top_left), group="Style", display=display.none),
    sL=input.string(size.small, 'Size Label', options=(size.tiny, size.small, size.normal, size.large), group='Style', display=display.none),
    sT=input.string(size.normal, 'Size Table', options=(size.tiny, size.small, size.normal, size.large), group='Style', display=display.none),
    Label__ren__=input.bool(False, inline='l'),
    History=input.bool(True, inline='l'),
    MAV=input.bool(True, title='EMA', group='EMA'),
    volumeOption=input.string('Use Volume Confirmation', title='Volume Option', options=('none', 'Use Volume Confirmation'), group='EMA', display=display.none),
    emaFastLength=input(12, title='Fast EMA Length', group='EMA', display=display.none),
    emaSlowLength=input(26, title='Slow EMA Length', group='EMA', display=display.none),
    volumeConfirmationLength=input(6, title='Volume Confirmation Length', group='EMA', display=display.none),
    alert_freq=input.string(alert.freq_once_per_bar_close, title="Alert Frequency", options=(alert.freq_once_per_bar, alert.freq_once_per_bar_close), group="EMA", tooltip="If you choose once_per_bar, you will receive immediate notifications (but this may cause interference or indicator repainting).                                         \n However, if you choose once_per_bar_close, it will wait for the candle to confirm the signal before notifying.", display=display.none)
):
    FP = format.percent
    useVolumeConfirmation: bool = False if volumeOption == 'none' else True


    def calcVolumes(ohlcv: OHLCV):
        data: Persistent[VolumeData] = VolumeData()
        data.buyVol = ohlcv.V * (ohlcv.C - ohlcv.L) / (ohlcv.H - ohlcv.L)
        data.sellVol = ohlcv.V - data.buyVol
        data.pcBuy = data.buyVol / ohlcv.V * 100
        data.pcSell = 100 - data.pcBuy
        data.isBuyGreater = data.buyVol > data.sellVol
        data.higherVol = data.buyVol if data.isBuyGreater else data.sellVol
        data.lowerVol = data.sellVol if data.isBuyGreater else data.buyVol
        data.higherCol = C_Up if data.isBuyGreater else C_Down
        data.lowerCol = C_Down if data.isBuyGreater else C_Up
        return data

    ohlcv: OHLCV = OHLCV()
    volData = calcVolumes(ohlcv)

    plot(ohlcv.V, color=color.new(volData.higherCol, 90), style=plot.style_columns, title='Total', display=display.all - display.status_line)
    plot(ohlcv.V, color=volData.higherCol, style=plot.style_stepline_diamond, title='Total2', linewidth=2, display=display.pane)
    plot(volData.higherVol, color=volData.higherCol, style=plot.style_columns, title='Higher Volume', display=display.all - display.status_line)
    plot(volData.lowerVol, color=volData.lowerCol, style=plot.style_columns, title='Lower Volume', display=display.all - display.status_line)

    def S(D, F):
        return string.tostring(D, F)

    volStr = S(math.sign(ta.change(ohlcv.C)) * ohlcv.V, FV)
    buyVolStr = S(volData.buyVol, FV)
    sellVolStr = S(volData.sellVol, FV)
    buyPercentStr = S(volData.pcBuy, FP)
    sellPercentStr = S(volData.pcSell, FP)
    totalbuyPercentC_ = volData.buyVol / (volData.buyVol + volData.sellVol) * 100
    sup = not na(ohlcv.V)
    if sup:
        TC = text.align_center
        CW = color.white
        tb: Persistent[Table] = table.new(P_, 6, 6, bgcolor=na, frame_width=2, frame_color=chart.fg_color, border_width=1, border_color=CW)

        table.cell(tb, 0, 0, text='Volume Candles', text_color=color.new('#FFBF00'), bgcolor=color.new('#0E2841'), text_halign=TC, text_valign=TC, text_size=sT)
        table.merge_cells(tb, 0, 0, 5, 0)
        table.cell(tb, 0, 1, text='Current Volume', text_color=CW, bgcolor=color.new('#0B3040'), text_halign=TC, text_valign=TC, text_size=sT)
        table.merge_cells(tb, 0, 1, 1, 1)
        table.cell(tb, 0, 2, text='Buy', text_color=color.new('#000000'), bgcolor=color.new('#92D050'), text_halign=TC, text_valign=TC, text_size=sT)
        table.cell(tb, 1, 2, text='Sell', text_color=color.new('#000000'), bgcolor=color.new('#FF0000'), text_halign=TC, text_valign=TC, text_size=sT)
        table.cell(tb, 0, 3, text=buyVolStr, text_color=CW, bgcolor=color.new('#074F69'), text_halign=TC, text_valign=TC, text_size=sT)
        table.cell(tb, 1, 3, text=sellVolStr, text_color=CW, bgcolor=color.new('#074F69'), text_halign=TC, text_valign=TC, text_size=sT)
        table.cell(tb, 0, 5, text='Net: ' + volStr, text_color=CW, bgcolor=color.new('#074F69'), text_halign=TC, text_valign=TC, text_size=sT)
        table.merge_cells(tb, 0, 5, 1, 5)
        table.cell(tb, 0, 4, text=buyPercentStr, text_color=CW, bgcolor=color.new('#074F69'), text_halign=TC, text_valign=TC, text_size=sT)
        table.cell(tb, 1, 4, text=sellPercentStr, text_color=CW, bgcolor=color.new('#074F69'), text_halign=TC, text_valign=TC, text_size=sT)

        cellCount: int = 20
        filledCells: int = 0
        for r in pine_range(5, 1, 1):
            for c in pine_range(2, 5, 1):
                if filledCells < cellCount * (totalbuyPercentC_ / 100):
                    table.cell(tb, c, r, text='', bgcolor=C_Up)
                else:
                    table.cell(tb, c, r, text='', bgcolor=C_Down)
                filledCells = filledCells + 1
        if Label__ren__:
            sp: str = '               '
            l: Series = label.new(bar_index, ohlcv.V, text=string.format('Net: {0}\nBuy: {1} ({2})\nSell: {3} ({4})\n{5}/\\\n {5}l\n {5}l', volStr, buyVolStr, buyPercentStr, sellVolStr, sellPercentStr, sp), style=label.style_none, textcolor=volData.higherCol, size=sL, textalign=text.align_left)
            if not History:
                method_call('delete', l[1])

    base: float = na(float)
    value: float = na(float)
    uc: bool = usecandle and sup
    if volData.isBuyGreater:
        base = math.min(ohlcv.O, ohlcv.C)
        value = base + math.abs(ohlcv.O - ohlcv.C) * (volData.pcBuy / 100)
    else:
        base = math.max(ohlcv.O, ohlcv.C)
        value = base - math.abs(ohlcv.O - ohlcv.C) * (volData.pcSell / 100)

    barcolor(color.new(na, na) if sup else color.red if ohlcv.C < ohlcv.O else color.green, display=display.all if usecandle else display.none)
    UseC = volData.higherCol if uc else color.new(na, na)
    plotcandle(base if uc else na, base if uc else na, value if uc else na, value if uc else na, title='Body', color=UseC, bordercolor=na, wickcolor=UseC, display=display.all - display.status_line if usecandle else display.none, force_overlay=True, editable=False)
    plotcandle(ohlcv.O if uc else na, ohlcv.H if uc else na, ohlcv.L if uc else na, ohlcv.C if uc else na, title='Fill', color=color.new(UseC, 80), bordercolor=UseC, wickcolor=UseC, display=display.all - display.status_line if usecandle else display.none, force_overlay=True, editable=False)

    emaFast: float = ta.ema(ohlcv.C, emaFastLength)
    emaSlow: float = ta.ema(ohlcv.C, emaSlowLength)
    signal: bool = emaFast > emaSlow
    c_signal: Color = C_Up if signal else C_Down
    volumeMA: float = ta.sma(ohlcv.V, volumeConfirmationLength)
    crossover: bool = ta.crossover(emaFast, emaSlow)
    crossunder: bool = ta.crossunder(emaFast, emaSlow)
    def isVolumeConfirmed(source, length, ma):
        return math.sum(source if source > ma else 0, length) >= math.sum(source if source < ma else 0, length)

    ISV: bool = isVolumeConfirmed(ohlcv.V, volumeConfirmationLength, volumeMA)
    crossoverConfirmed: bool = crossover and (not useVolumeConfirmation or ISV)
    crossunderConfirmed: bool = crossunder and (not useVolumeConfirmation or ISV)
    PF = emaFast if MAV else na
    PS = emaSlow if MAV else na
    p1 = plot(PF, color=c_signal, editable=False, force_overlay=True, display=display.pane)
    plot(PF, color=color.new(c_signal, 80), linewidth=10, editable=False, force_overlay=True, display=display.pane)
    plot(PF, color=color.new(c_signal, 90), linewidth=20, editable=False, force_overlay=True, display=display.pane)
    plot(PF, color=color.new(c_signal, 95), linewidth=30, editable=False, force_overlay=True, display=display.pane)
    plot(PF, color=color.new(c_signal, 98), linewidth=45, editable=False, force_overlay=True, display=display.pane)
    p2 = plot(PS, color=c_signal, editable=False, force_overlay=True, display=display.pane)
    plot(PS, color=color.new(c_signal, 80), linewidth=10, editable=False, force_overlay=True, display=display.pane)
    plot(PS, color=color.new(c_signal, 90), linewidth=20, editable=False, force_overlay=True, display=display.pane)
    plot(PS, color=color.new(c_signal, 95), linewidth=30, editable=False, force_overlay=True, display=display.pane)
    plot(PS, color=color.new(c_signal, 98), linewidth=45, editable=False, force_overlay=True, display=display.pane)

    fill(p1, p2, top_value=emaFast if crossover else emaSlow, bottom_value=emaSlow if crossover else emaFast, top_color=color.new(c_signal, 80), bottom_color=color.new(c_signal, 95))
    plotshape(crossoverConfirmed and MAV, style=shape.triangleup, location=location.belowbar, color=C_Up, size=size.small, force_overlay=True, display=display.pane)
    plotshape(crossunderConfirmed and MAV, style=shape.triangledown, location=location.abovebar, color=C_Down, size=size.small, force_overlay=True, display=display.pane)

    msg: str = '---------\n' + 'Buy volume =' + buyVolStr + '\nBuy Percent = ' + buyPercentStr + '\nSell volume = ' + sellVolStr + '\nSell Percent = ' + sellPercentStr + '\nNet = ' + volStr + '\n---------'
    if crossoverConfirmed:
        alert('Price (' + string.tostring(close) + ') Crossed over  MA\n' + msg, alert_freq)
    if crossunderConfirmed:
        alert('Price (' + string.tostring(close) + ') Crossed under MA\n' + msg, alert_freq)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
