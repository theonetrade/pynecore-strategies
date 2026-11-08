"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, close, color, format, high,
    hl2, input, label, line, linefill, location, low, math, na, nz, plot, plotchar, plotshape,
    script, shape, size, string, ta
)
from pynecore.types import Label, Line, LineFill, Persistent, PersistentSeries, Series


@script.indicator("Trend Targets [AlgoAlpha]", "AlgoAlpha - Trend Targets", overlay=True)
def main(
    st_factor=input.float(12, title="Supertrend Factor", minval=1, step=0.5, group="Trend Settings", tooltip="Multiplier for the ATR to determine Supertrend bands width. Higher values create wider bands and fewer signals."),
    st_atr_period=input.int(90, title="Supertrend ATR Period", minval=1, group="Trend Settings", tooltip="Number of bars used to calculate the ATR for Supertrend. Longer periods create smoother, less reactive bands."),
    wma_length=input.int(40, title="WMA Length", minval=1, group="Trend Settings", tooltip="Length of the Weighted Moving Average applied to the SuperTrend. Higher values create smoother, less reactive lines."),
    ema_length=input.int(14, title="EMA Length", minval=1, group="Trend Settings", tooltip="Length of the Exponential Moving Average applied to the WMA. Controls the final smoothness of the trend line."),
    cont_factor=input.int(3, title="Confirmation count", minval=1, group="Rejection Settings", tooltip="Number of consecutive bars that must consolidate at the trend line before a rejection signal is generated. Higher values require more bars to confirm a trend."),
    shw_TP1=input.bool(True, title="Show Take Profit Levels", group="Targets", tooltip="Toggle visibility of take profit target levels on the chart."),
    atr_period=input.int(14, title="Volatility (ATR) period", minval=1, group="Targets", tooltip="Number of bars used to calculate the Average True Range for position sizing and targets."),
    sl_multiplier=input.float(5, title="Stop Loss ATR Multiplier", minval=0.1, step=0.1, group="Targets", tooltip="Multiplier applied to ATR to determine stop loss distance from entry. Higher values place stops further away."),
    tp1_multiplier=input.float(0.5, title="TP1 Multiplier", minval=0.1, step=0.1, tooltip="Multiple of SL distance for first take profit target.", group="Targets"),
    tp2_multiplier=input.float(1.0, title="TP2 Multiplier", minval=0.1, step=0.1, tooltip="Multiple of SL distance for second take profit target.", group="Targets"),
    tp3_multiplier=input.float(1.5, title="TP3 Multiplier", minval=0.1, step=0.1, tooltip="Multiple of SL distance for third take profit target.", group="Targets"),
    green=input.color(color.new('#00FFBB'), title="Bullish Color", tooltip="Color used for bullishness", group="Appearance"),
    red=input.color(color.new('#FF1100'), title="Bearish Color", tooltip="Color used for bearishness", group="Appearance")
):
    volatility = ta.atr(atr_period)

    def pine_supertrend(factor, atrPeriod):
        src = hl2
        atr = ta.atr(atrPeriod)
        upperBand: Series = src + factor * atr
        lowerBand: Series = src - factor * atr
        prevLowerBand = nz(lowerBand[1])
        prevUpperBand = nz(upperBand[1])

        lowerBand = lowerBand if lowerBand > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or close[1] > prevUpperBand else prevUpperBand

        return (lowerBand, upperBand)

    lwr, upr = pine_supertrend(st_factor, st_atr_period)
    tL: Series = ta.ema(ta.wma(math.avg(lwr, upr), wma_length), ema_length)

    trend: Persistent[int] = 0
    if ta.crossover(tL, tL[1]):
        trend = 1
    if ta.crossunder(tL, tL[1]):
        trend = -1

    rejcount: Persistent[int] = 0

    bullishrej = trend == 1 and high > tL and (low < tL)
    bearishrej = trend == -1 and high > tL and (low < tL)

    if bullishrej or bearishrej:
        rejcount += 1

    if ta.cross(trend, 0) or (not (bullishrej or bearishrej) and rejcount > 0):
        rejcount = 0

    plotchar(tL if rejcount > cont_factor and trend == 1 else na, 'Bullish Rejection', '▲', location.belowbar, green, size=size.tiny)
    plotchar(tL if rejcount > cont_factor and trend == -1 else na, 'Bearish Rejection', '▼', location.abovebar, red, size=size.tiny)

    plot(tL, 'Baseline', color=color.new(green, 50) if trend == 1 else color.new(red, 50))

    barcolor(color.new(green, 50) if trend == 1 else color.new(red, 50))

    plotshape(tL if ta.crossover(tL, tL[1]) else na, title='Bullish Trend Change', style=shape.labelup, location=location.absolute, size=size.small, color=green)
    plotshape(tL if ta.crossunder(tL, tL[1]) else na, title='Bearish Trend Change', style=shape.labeldown, location=location.absolute, size=size.small, color=red)

    longSignal = ta.crossover(trend, 0)
    shortSignal = ta.crossunder(trend, 0)
    SL: Persistent[float] = 0.0
    TP1_lvl: Persistent[float] = 0.0
    TP2_lvl: Persistent[float] = 0.0
    TP3_lvl: Persistent[float] = 0.0
    entry_line: PersistentSeries[Line] = na(Line)
    sl_line: PersistentSeries[Line] = na(Line)
    tp1_line: PersistentSeries[Line] = na(Line)
    tp2_line: PersistentSeries[Line] = na(Line)
    tp3_line: PersistentSeries[Line] = na(Line)
    entry_label: PersistentSeries[Label] = na(Label)
    sl_label: PersistentSeries[Label] = na(Label)
    tp1_label: PersistentSeries[Label] = na(Label)
    tp2_label: PersistentSeries[Label] = na(Label)
    tp3_label: PersistentSeries[Label] = na(Label)

    if longSignal and shw_TP1:
        SL = low - volatility * sl_multiplier
        TP1_lvl = close + math.abs(close - SL) * tp1_multiplier
        TP2_lvl = close + math.abs(close - SL) * tp2_multiplier
        TP3_lvl = close + math.abs(close - SL) * tp3_multiplier
        entry_line = line.new(bar_index, close, bar_index, close, color=green, width=3)
        entry_label = label.new(bar_index, close, text='Entry ▸ ' + string.tostring(close, format.mintick), style=label.style_label_left, color=green, textcolor=color.white)

        sl_line = line.new(bar_index, SL, bar_index, SL, color=color.new(red, 80), width=3)
        sl_label = label.new(bar_index, SL, text='✘ SL ▸ ' + string.tostring(SL, format.mintick), style=label.style_label_left, color=color.new(red, 80), textcolor=color.white)

        tp1_line = line.new(bar_index, TP1_lvl, bar_index, TP1_lvl, color=color.new(green, 80), width=3)
        tp1_label = label.new(bar_index, TP1_lvl, text=' ✔ TP1 ▸ ' + string.tostring(TP1_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        tp2_line = line.new(bar_index, TP2_lvl, bar_index, TP2_lvl, color=color.new(green, 80), width=3)
        tp2_label = label.new(bar_index, TP2_lvl, text=' ✔ TP2 ▸ ' + string.tostring(TP2_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        tp3_line = line.new(bar_index, TP3_lvl, bar_index, TP3_lvl, color=color.new(green, 80), width=3)
        tp3_label = label.new(bar_index, TP3_lvl, text=' ✔ TP3 ▸ ' + string.tostring(TP3_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        line.delete(entry_line[1])
        label.delete(entry_label[1])

        line.delete(sl_line[1])
        label.delete(sl_label[1])

        line.delete(tp1_line[1])
        label.delete(tp1_label[1])

        line.delete(tp2_line[1])
        label.delete(tp2_label[1])

        line.delete(tp3_line[1])
        label.delete(tp3_label[1])
    else:
        line.set_x2(entry_line, bar_index)
        label.set_x(entry_label, bar_index)

        line.set_x2(sl_line, bar_index)
        label.set_x(sl_label, bar_index)

        line.set_x2(tp1_line, bar_index)
        label.set_x(tp1_label, bar_index)

        line.set_x2(tp2_line, bar_index)
        label.set_x(tp2_label, bar_index)

        line.set_x2(tp3_line, bar_index)
        label.set_x(tp3_label, bar_index)

    if shortSignal and shw_TP1:
        SL = high + volatility * sl_multiplier
        TP1_lvl = close - math.abs(close - SL) * tp1_multiplier
        TP2_lvl = close - math.abs(close - SL) * tp2_multiplier
        TP3_lvl = close - math.abs(close - SL) * tp3_multiplier
        entry_line = line.new(bar_index, close, bar_index, close, color=red, width=3)
        entry_label = label.new(bar_index, close, text='Entry ▸ ' + string.tostring(close, format.mintick), style=label.style_label_left, color=red, textcolor=color.white)

        sl_line = line.new(bar_index, SL, bar_index, SL, color=color.new(red, 80), width=3)
        sl_label = label.new(bar_index, SL, text='✘ SL ▸ ' + string.tostring(SL, format.mintick), style=label.style_label_left, color=color.new(red, 80), textcolor=color.white)

        tp1_line = line.new(bar_index, TP1_lvl, bar_index, TP1_lvl, color=color.new(green, 80), width=3)
        tp1_label = label.new(bar_index, TP1_lvl, text=' ✔ TP1 ▸ ' + string.tostring(TP1_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        tp2_line = line.new(bar_index, TP2_lvl, bar_index, TP2_lvl, color=color.new(green, 80), width=3)
        tp2_label = label.new(bar_index, TP2_lvl, text=' ✔ TP2 ▸ ' + string.tostring(TP2_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        tp3_line = line.new(bar_index, TP3_lvl, bar_index, TP3_lvl, color=color.new(green, 80), width=3)
        tp3_label = label.new(bar_index, TP3_lvl, text=' ✔ TP3 ▸ ' + string.tostring(TP3_lvl, format.mintick), style=label.style_label_left, color=color.new(green, 80), textcolor=color.white)

        line.delete(entry_line[1])
        label.delete(entry_label[1])

        line.delete(sl_line[1])
        label.delete(sl_label[1])

        line.delete(tp1_line[1])
        label.delete(tp1_label[1])

        line.delete(tp2_line[1])
        label.delete(tp2_label[1])

        line.delete(tp3_line[1])
        label.delete(tp3_label[1])
    else:
        line.set_x2(entry_line, bar_index + 40)
        label.set_x(entry_label, bar_index + 40)

        line.set_x2(sl_line, bar_index + 40)
        label.set_x(sl_label, bar_index + 40)

        line.set_x2(tp1_line, bar_index + 40)
        label.set_x(tp1_label, bar_index + 40)

        line.set_x2(tp2_line, bar_index + 40)
        label.set_x(tp2_label, bar_index + 40)

        line.set_x2(tp3_line, bar_index + 40)
        label.set_x(tp3_label, bar_index + 40)

    liness: list[LineFill] = array.new_linefill()

    array.unshift(liness, linefill.new(entry_line, sl_line, color.new(color.red, 95)))
    array.unshift(liness, linefill.new(entry_line, tp3_line, color.new(color.green, 95)))

    alertcondition(ta.crossover(close, SL), title='Trend Change: Bullish', message='Price crossed above SL - Potential Bullish Trend')
    alertcondition(ta.crossunder(close, SL), title='Trend Change: Bearish', message='Price crossed below SL - Potential Bearish Trend')

    alertcondition(ta.crossover(high, SL) and close < SL, title='Rejection: Bearish', message='Price rejected at SL - Bearish Rejection')
    alertcondition(ta.crossunder(low, SL) and close > SL, title='Rejection: Bullish', message='Price rejected at SL - Bullish Rejection')

    alertcondition(ta.crossover(close, TP1_lvl), title='TP1 Hit', message='Price reached TP1 level')
    alertcondition(ta.crossover(close, TP2_lvl), title='TP2 Hit', message='Price reached TP2 level')
    alertcondition(ta.crossover(close, TP3_lvl), title='TP3 Hit', message='Price reached TP3 level')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
