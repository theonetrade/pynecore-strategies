"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, close, color, display, fill, format,
    input, na, open, plot, script, ta, volume
)
from pynecore.types import Color

g_hmz: str = 'Heatmap Threshold Multipliers'
g_color: str = 'Color settings'
chm1: Color = color.new('#FF0000')
chm2: Color = color.new('#FF7800')
chm3: Color = color.new('#FFCF03')
chm4: Color = color.new('#A0D6DC')
chm5: Color = color.new('#1F9CAC')
g_mhcolor: str = 'Heatmap colors'
g_up: str = 'Up colors'
g_down: str = 'Down colors'


@script.indicator(title='Heatmap Volume [xdecow]', shorttitle='HMV [xdecow]', format=format.volume)
def main(
    length=input.int(610, title='MA Length', minval=2, tooltip='Moving Average Length\n\n- Smaller values will respond more quickly and activate more frequently. (Best for short-term analysis)\n- Larger values will have a slower response, will be less sensitive to small volume variations, and will highlight large volumes. (Best for long-term analysis)\n\nFormula: How many stdev is the volume far from the Moving Average?'),
    slength=input.int(610, title='Standard Deviation Length', minval=2, tooltip='Standard Deviation lookback period.\n\nFormula: How many stdev is the volume far from the Moving Average?'),
    thresholdExtraHigh=input.float(4, title='Extra High Multiplier', tooltip='Volume Threshold Multiplier\neg: 4 = 400% or 4 x Stdev above the mean', group=g_hmz),
    thresholdHigh=input(2.5, title='High Multiplier', group=g_hmz),
    thresholdMedium=input.float(1, title='Medium Multiplier', group=g_hmz),
    thresholdNormal=input(-0.5, title='Normal Multiplier', group=g_hmz),
    bcolor_enabled=input(True, 'Colored bars', group=g_color),
    zmode=input.string('Backgrounds', 'Display Heatmap Zones as', options=('None', 'Lines', 'Backgrounds', 'Both'), group=g_color),
    cmode=input.string('Heatmap', 'Color Mode', options=('Heatmap', 'Up/Down'), group=g_color, tooltip='- Heatmap mode: colors based only on volume.\n- Up/Down mode: colors based on candle volume and direction.\nChange the cores below according to the selected mode.'),
    chmthresholdExtraHigh=input(chm1, 'Extra High', group=g_mhcolor),
    chmthresholdHigh=input(chm2, 'High', group=g_mhcolor),
    chmthresholdMedium=input(chm3, 'Medium', group=g_mhcolor),
    chmthresholdNormal=input(chm4, 'Normal', group=g_mhcolor),
    chmthresholdLow=input(chm5, 'Low', group=g_mhcolor),
    cupthresholdExtraHigh=input(color.new('#00FF00'), 'Extra High', group=g_up),
    cupthresholdHigh=input(color.new('#30FF30'), 'High', group=g_up),
    cupthresholdMedium=input(color.new('#60FF60'), 'Medium', group=g_up),
    cupthresholdNormal=input(color.new('#8FFF8F'), 'Normal', group=g_up),
    cupthresholdLow=input(color.new('#BFFFBF'), 'Low', group=g_up),
    cdnthresholdExtraHigh=input(color.new('#FF0000'), 'Extra High', group=g_down),
    cdnthresholdHigh=input(color.new('#FF3030'), 'High', group=g_down),
    cdnthresholdMedium=input(color.new('#FF6060'), 'Medium', group=g_down),
    cdnthresholdNormal=input(color.new('#FF8F8F'), 'Normal', group=g_down),
    cdnthresholdLow=input(color.new('#FFBFBF'), 'Low', group=g_down)
):
    cthresholdExtraHighUp = chmthresholdExtraHigh if cmode == 'Heatmap' else cupthresholdExtraHigh
    cthresholdHighUp = chmthresholdHigh if cmode == 'Heatmap' else cupthresholdHigh
    cthresholdMediumUp = chmthresholdMedium if cmode == 'Heatmap' else cupthresholdMedium
    cthresholdNormalUp = chmthresholdNormal if cmode == 'Heatmap' else cupthresholdNormal
    cthresholdLowUp = chmthresholdLow if cmode == 'Heatmap' else cupthresholdLow
    cthresholdExtraHighDn = chmthresholdExtraHigh if cmode == 'Heatmap' else cdnthresholdExtraHigh
    cthresholdHighDn = chmthresholdHigh if cmode == 'Heatmap' else cdnthresholdHigh
    cthresholdMediumDn = chmthresholdMedium if cmode == 'Heatmap' else cdnthresholdMedium
    cthresholdNormalDn = chmthresholdNormal if cmode == 'Heatmap' else cdnthresholdNormal
    cthresholdLowDn = chmthresholdLow if cmode == 'Heatmap' else cdnthresholdLow
    length = bar_index + 1 if length > bar_index + 1 else length
    slength = bar_index + 1 if slength > bar_index + 1 else slength
    dir = close > open
    mean = ta.sma(volume, length)
    std = ta.stdev(volume, slength)
    stdbar = (volume - mean) / std
    bcolor = (cthresholdExtraHighUp if dir else cthresholdExtraHighDn) if stdbar > thresholdExtraHigh else (cthresholdHighUp if dir else cthresholdHighDn) if stdbar > thresholdHigh else (cthresholdMediumUp if dir else cthresholdMediumDn) if stdbar > thresholdMedium else (cthresholdNormalUp if dir else cthresholdNormalDn) if stdbar > thresholdNormal else cthresholdLowUp if dir else cthresholdLowDn
    zshow_lines = zmode == 'Lines' or zmode == 'Both'
    zshow_backgrounds = zmode == 'Backgrounds' or zmode == 'Both'
    ts1 = std * thresholdExtraHigh + mean
    ts2 = std * thresholdHigh + mean
    ts3 = std * thresholdMedium + mean
    ts4 = std * thresholdNormal + mean
    ts0: int = 0
    tsDelta = ts1 - ts2
    tst = ts1 + tsDelta
    barcolor(bcolor if bcolor_enabled else na, editable=False)
    pt = plot(tst if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    p0 = plot(ts0 if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    p1 = plot(ts1 if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    p2 = plot(ts2 if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    p3 = plot(ts3 if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    p4 = plot(ts4 if zshow_backgrounds else na, color=na, display=display.none, editable=False)
    tpf: int = 85
    fill(pt, p1, color.new(chm1, tpf), title='Extra High heatmap zone')
    fill(p1, p2, color.new(chm2, tpf), title='High heatmap zone')
    fill(p2, p3, color.new(chm3, tpf), title='Medium heatmap zone')
    fill(p3, p4, color.new(chm4, tpf), title='Normal heatmap zone')
    fill(p4, p0, color.new(chm5, tpf), title='Low heatmap zone')
    plot(volume, color=bcolor, style=plot.style_columns, title='Volume', editable=False)
    plot(mean, color=color.new(color.new('#000000'), 0), linewidth=2, title='Moving Average', style=plot.style_line, display=display.none)
    tpp: int = 50
    plot(ts1 if zshow_lines else na, color=color.new(chm1, tpp), title='Extra High heatmap line')
    plot(ts2 if zshow_lines else na, color=color.new(chm2, tpp), title='High heatmap line')
    plot(ts3 if zshow_lines else na, color=color.new(chm3, tpp), title='Medium heatmap line')
    plot(ts4 if zshow_lines else na, color=color.new(chm4, tpp), title='Normal heatmap line')
    conditionExtraHigh = stdbar > thresholdExtraHigh
    conditionHigh = stdbar <= thresholdExtraHigh and stdbar > thresholdHigh
    conditionMedium = stdbar <= thresholdHigh and stdbar > thresholdMedium
    conditionNormal = stdbar <= thresholdMedium and stdbar > thresholdNormal
    conditionLow = stdbar <= thresholdNormal
    alertcondition(conditionExtraHigh, title='Any Extra High Vol', message='Any Bar Extra High Volume Threshold')
    alertcondition(conditionExtraHigh and open < close, title='Up Extra High', message='Up Bar Extra High Volume Threshold')
    alertcondition(conditionExtraHigh and open > close, title='Down Extra High', message='Down Bar Extra High Volume Threshold')
    alertcondition(conditionHigh, title='Any High Vol', message='Any Bar High Volume Threshold')
    alertcondition(conditionHigh and open < close, title='Up High Vol', message='Up Bar High Volume Threshold')
    alertcondition(conditionHigh and open > close, title='Down High Vol', message='Down Bar High Volume Threshold')
    alertcondition(conditionMedium, title='Any Medium Vol', message='Any Bar Medium Volume Threshold')
    alertcondition(conditionMedium and open < close, title='Up Medium Vol', message='Up Bar Medium Volume Threshold')
    alertcondition(conditionMedium and open > close, title='Down Medium Vol', message='Down Bar Medium Volume Threshold')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)