"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    color, fill, fixnan, high, input, label, low, math, na, plot, script,
    size, ta, text, time, xloc, yloc
)
from pynecore.types import Label, Persistent


@script.indicator(title='Trend Type Indicator by BobRivera990', overlay=False, na_bool=True)
def main(
    useAtr=input(True, title='Use ATR to detect Sideways Movements'),
    atrLen=input.int(14, minval=1, title='ATR Length'),
    atrMaType=input.string('SMA', options=('SMA', 'EMA'), title='ATR Moving Average Type'),
    atrMaLen=input.int(20, minval=1, title='ATR MA Length'),
    useAdx=input(True, title='Use ADX to detect Sideways Movements'),
    adxLen=input.int(14, minval=1, maxval=50, title='ADX Smoothing'),
    diLen=input.int(14, minval=1, title='DI Length'),
    adxLim=input.int(25, minval=1, title='ADX Limit'),
    smooth=input.int(3, minval=1, maxval=5, title='Smoothing Factor'),
    lag=input.int(8, minval=0, maxval=15, title='Lag')
):
    atr = ta.atr(atrLen)
    atrMa = ta.ema(atr, atrMaLen) if atrMaType == 'EMA' else ta.sma(atr, atrMaLen)
    up = ta.change(high)
    down = -ta.change(low)
    plusDM = na if na(up) else up if up > down and up > 0 else 0
    minusDM = na if na(down) else down if down > up and down > 0 else 0
    trur = ta.rma(ta.tr, diLen)
    plus = fixnan(100 * ta.rma(plusDM, diLen) / trur)
    minus = fixnan(100 * ta.rma(minusDM, diLen) / trur)
    sum = plus + minus
    adx = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxLen)
    cndNa = na(atr) or na(adx) or na(plus) or na(minus) or na(atrMaLen)
    cndSidwayss1 = useAtr and atr <= atrMa
    cndSidwayss2 = useAdx and adx <= adxLim
    cndSidways = cndSidwayss1 or cndSidwayss2
    cndUp = plus > minus
    cndDown = minus >= plus
    trendType = na if cndNa else 0 if cndSidways else 2 if cndUp else -2
    smoothType = na if na(trendType) else math.round(ta.sma(trendType, smooth) / 2) * 2
    colGreen30 = color.new(color.green, 30)
    colGreen90 = color.new(color.green, 90)
    colGray = color.new(color.gray, 20)
    colWhite90 = color.new(color.white, 90)
    colRed30 = color.new(color.red, 30)
    colRed90 = color.new(color.red, 90)
    band3 = plot(3, title='Band_3', color=color.new(color.black, 0))
    band2 = plot(1, title='Band_2', color=color.new(color.black, 0))
    band1 = plot(-1, title='Band_1', color=color.new(color.black, 0))
    band0 = plot(-3, title='Band_0', color=color.new(color.black, 0))
    fill(band2, band3, title='Uptrend area', color=colGreen90)
    fill(band1, band2, title='Sideways area', color=colWhite90)
    fill(band0, band1, title='Downtrend area', color=colRed90)
    lblUp: Persistent[Label] = na(Label)
    label.delete(lblUp)
    lblUp = label.new(x=time, y=2, text='UP', color=color.new(color.green, 100), textcolor=color.black, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price, size=size.normal, textalign=text.align_left)
    lblSideways: Persistent[Label] = na(Label)
    label.delete(lblSideways)
    lblSideways = label.new(x=time, y=0, text='SIDEWAYS', color=color.new(color.green, 100), textcolor=color.black, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price, size=size.normal, textalign=text.align_left)
    lblDown: Persistent[Label] = na(Label)
    label.delete(lblDown)
    lblDown = label.new(x=time, y=-2, text='DOWN', color=color.new(color.green, 100), textcolor=color.black, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price, size=size.normal, textalign=text.align_left)
    lblCurrentType: Persistent[Label] = na(Label)
    label.delete(lblCurrentType)
    lblCurrentType = label.new(x=time, y=smoothType, color=color.new(color.blue, 30), style=label.style_label_right, xloc=xloc.bar_time, yloc=yloc.price, size=size.small)
    trendCol = colGreen30 if smoothType == 2 else colGray if smoothType == 0 else colRed30
    plot(smoothType, title='Trend Type Oscillator', color=trendCol, linewidth=3, offset=-lag, style=plot.style_stepline)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)