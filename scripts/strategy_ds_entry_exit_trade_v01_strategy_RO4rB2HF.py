"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, close, color, fill, high, input, label, location,
    low, math, na, ohlc4, plot, plotshape, script, shape, size, strategy, string, ta, time,
    timestamp
)
from pynecore.types import Series


@script.strategy('[DS]Entry_Exit_TRADE.V01-Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    return_1=input(title='Return Candels ?', defval=190),
    _Pivots=input(title='══════ Pivots ══════', defval=False),
    leftBars=input(4),
    rightBars=input(4),
    _WilliamR=input(title='══════ William R% Mod ══════', defval=False),
    SOB_William=input(title='OverBought Area', defval=-7),
    SOS_William=input(title='OverSold Area', defval=-93),
    length_William=input.int(17, minval=1),
    _Macd=input(title='═════ Macd ══════════', defval=False),
    fast_length_Macd=input(title='Fast Length', defval=12),
    slow_length_Macd=input(title='Slow Length', defval=26),
    src_Macd: Series[float] = input(title='Source', defval=close),
    signal_length_Macd=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    _Tsi=input(title='═════ Tsi ══════════', defval=False),
    long_tsi=input(title='Long Length', defval=72),
    short_tsi=input(title='Short Length', defval=17),
    signal_tsi=input(title='Signal Length', defval=17)
):
    e1 = ta.ema(close, 8)
    e2 = ta.ema(e1, 8)
    dema08 = 2 * e1 - e2
    e1 = ta.ema(close, 17)
    e2 = ta.ema(e1, 17)
    dema17 = 2 * e1 - e2
    e1 = ta.ema(close, 34)
    e2 = ta.ema(e1, 34)
    dema34 = 2 * e1 - e2
    e1 = ta.ema(close, 72)
    e2 = ta.ema(e1, 72)
    dema72 = 2 * e1 - e2
    ema72: Series = ta.ema(close, 72)
    emaOhlc4 = ta.ema(ohlc4, 8)
    plot(dema72, title='DEMA 72', color=color.new(color.orange, 0), linewidth=2, style=plot.style_line, show_last=return_1)
    plot(emaOhlc4, title='EMA ohlc4', color=color.new(color.green, 0) if emaOhlc4 > dema72 else color.new(color.red, 0), linewidth=2, style=plot.style_line, show_last=return_1)
    barcolor(color.new(color.green, 0) if close > dema34 and close > dema72 or close > close[1] else color.new(color.red, 0), show_last=return_1)
    plot(dema72 if ta.crossover(emaOhlc4, dema72) else na, title='Cross UP', color=color.new(color.green, 0), style=plot.style_circles, linewidth=5, show_last=return_1)
    plot(dema72 if ta.crossunder(emaOhlc4, dema72) else na, title='Cross DOWN', color=color.new(color.red, 50), style=plot.style_circles, linewidth=5, show_last=return_1)
    pivotHigh = ta.pivothigh(leftBars, rightBars)
    plot(pivotHigh if pivotHigh > ema72[rightBars] else na, title='Pivot High', style=plot.style_cross, linewidth=3, color=color.new(color.purple, 50), offset=-rightBars, show_last=return_1)
    pivotLow = ta.pivotlow(leftBars, rightBars)
    plot(pivotLow if pivotLow < ema72[rightBars] else na, title='Pivot Low', style=plot.style_cross, linewidth=3, color=color.new(color.blue, 50), offset=-rightBars, show_last=return_1)
    highestHigh_William = ta.highest(length_William)
    highestLow_William = ta.lowest(length_William)
    R_William = (highestHigh_William - close) / (highestHigh_William - highestLow_William) * -100
    corTest = color.white
    colorText = color.white
    estilo = label.style_label_upper_left
    textW: str = ''
    if R_William > SOB_William:
        corTest = color.new(color.red, 0)
        estilo = label.style_label_lower_left
        textW = 'OB'
    if R_William > -30 and R_William <= SOB_William:
        corTest = color.new('#F5948E')
        estilo = label.style_label_lower_left
    if R_William > -50 and R_William <= -30:
        corTest = color.new('#F5D5D3')
        colorText = color.black
    if R_William > -70 and R_William <= -50:
        corTest = color.new('#E7F5D3')
        colorText = color.black
    if R_William >= SOS_William and R_William <= -70:
        corTest = color.lime
        estilo = label.style_label_upper_left
        colorText = color.black
    if R_William < SOS_William:
        corTest = color.new(color.green, 0)
        estilo = label.style_label_upper_left
        textW = 'OS'
    myLabel: Series = label.new(x=bar_index, y=close, style=estilo, color=corTest, text=string.tostring(R_William, '#.#') + '% ' + textW, textcolor=colorText, size=size.normal)
    labelText = label.get_text(id=myLabel)
    label.set_text(id=myLabel, text=labelText)
    label.delete(myLabel[1])
    ExtremoHigh = high + highestHigh_William - high
    ExtremoLow = low - (low - highestLow_William)
    plot(ExtremoHigh, color=color.new(color.red, 70), style=plot.style_line, linewidth=1, show_last=return_1)
    plot(ExtremoLow, color=color.new(color.green, 70), style=plot.style_line, linewidth=1, show_last=return_1)
    lH1: float = 0.0
    lHInt = close
    lL1 = close
    lLInt = close
    Vr_LinhaH: float = 0.0
    Vr_LinhaL: float = 0.0
    Vr_LinhaC: float = 0.0
    if emaOhlc4 < dema72:
        Vr_LinhaH = high + highestHigh_William - high
        lH1 = Vr_LinhaH if Vr_LinhaH > dema72 else dema72
        lHInt = dema72 if emaOhlc4 < dema72 else emaOhlc4
        lLInt = dema72 if lHInt == emaOhlc4 else emaOhlc4
        Vr_LinhaL = low - (low - highestLow_William)
        lL1 = lLInt if Vr_LinhaL > lLInt else Vr_LinhaL
    if emaOhlc4 > dema72:
        Vr_LinhaH = high + highestHigh_William - high
        lH1 = Vr_LinhaH if Vr_LinhaH > dema72 else dema72
        lHInt = dema72 if dema72 > emaOhlc4 else emaOhlc4
        lLInt = emaOhlc4 if lHInt == dema72 else dema72
        Vr_LinhaL = low - (low - highestLow_William)
        lL1 = lLInt if Vr_LinhaL > lLInt else Vr_LinhaL
    Line1 = plot(emaOhlc4, title='Dema ohlc4', color=color.new(color.white, 100), linewidth=1, show_last=return_1)
    Line2 = plot(dema72, title='Dema 72', color=color.new(color.white, 100), linewidth=1, show_last=return_1)
    fill(Line1, Line2, color=color.new(color.new(color.green, 90) if emaOhlc4 > dema72 else color.new(color.red, 90), 70), show_last=return_1)
    HighlH1 = plot(lH1, title='HighlH1', color=color.new(color.green, 90), linewidth=1, show_last=return_1, style=plot.style_linebr)
    HighlHInt = plot(lHInt, title='HighlHInt', color=color.new(color.green, 100), linewidth=1, show_last=return_1, style=plot.style_linebr)
    fill(HighlH1, HighlHInt, color=color.new(color.new(color.purple, 90), 0), show_last=return_1)
    LowlL1 = plot(lL1, title='LowlL1', color=color.new(color.red, 90), linewidth=1, show_last=return_1, style=plot.style_linebr)
    LowlLInt = plot(lLInt, title='LowlLInt', color=color.new(color.red, 100), linewidth=1, show_last=return_1, style=plot.style_linebr)
    fill(LowlL1, LowlLInt, color=color.new(color.new(color.blue, 90), 0), show_last=return_1)
    fast_ma_Macd = ta.ema(src_Macd, fast_length_Macd)
    slow_ma_Macd = ta.ema(src_Macd, slow_length_Macd)
    macd_Macd = fast_ma_Macd - slow_ma_Macd
    signal_Macd = ta.ema(macd_Macd, signal_length_Macd)
    hist_Macd = macd_Macd - signal_Macd
    MacdUp = 1 if ta.crossover(macd_Macd, signal_Macd) else 0
    MacdDown = 1 if ta.crossunder(macd_Macd, signal_Macd) else 0
    plotshape(MacdUp, text='+Md', title='(+)MACD UP', location=location.belowbar, color=color.new(color.green, 30), style=shape.triangleup, size=size.tiny, show_last=return_1)
    plotshape(MacdDown, text='-Md', title='(-)MACD DN', location=location.abovebar, color=color.new(color.red, 30), style=shape.triangledown, size=size.tiny, show_last=return_1)
    price_tsi = close
    def double_smooth(src_tsi, long_tsi, short_tsi):
        fist_smooth_tsi = ta.ema(src_tsi, long_tsi)
        return ta.ema(fist_smooth_tsi, short_tsi)

    pc_tsi = ta.change(price_tsi)
    double_smoothed_pc_tsi = double_smooth(pc_tsi, long_tsi, short_tsi)
    double_smoothed_abs_pc_tsi = double_smooth(math.abs(pc_tsi), long_tsi, short_tsi)
    tsi_value_tsi = 100 * (double_smoothed_pc_tsi / double_smoothed_abs_pc_tsi)
    TsiUp = 1 if ta.crossover(tsi_value_tsi, ta.ema(tsi_value_tsi, signal_tsi)) else 0
    TsiDown = 1 if ta.crossunder(tsi_value_tsi, ta.ema(tsi_value_tsi, signal_tsi)) else 0
    plotshape(low if TsiUp == 1 else na, text='+Tsi', title='(+)TSI Up', location=location.belowbar, color=color.new(color.green, 30), style=shape.triangleup, size=size.tiny, show_last=return_1)
    plotshape(high if TsiDown == 1 else na, text='-Tsi', title='(-)TSI DN', location=location.abovebar, color=color.new(color.red, 30), style=shape.triangledown, size=size.tiny, show_last=return_1)
    crossUP = ta.crossover(emaOhlc4, dema34)
    crossDN = ta.crossunder(emaOhlc4, dema34)
    tradeColor = color.red if crossUP else color.green if crossDN else na
    plot(dema34 if crossUP else dema34 if crossDN else na, color=tradeColor, style=plot.style_line, linewidth=4, editable=False, show_last=return_1)
    plotshape(dema34 if crossUP else na, style=shape.labelup, location=location.absolute, text='Buy', textcolor=color.new(color.white, 0), color=color.new(color.green, 0), editable=False, show_last=return_1)
    plotshape(dema34 if crossDN else na, style=shape.labeldown, location=location.absolute, text='Sell', textcolor=color.new(color.white, 0), color=color.new(color.red, 0), editable=False, show_last=return_1)
    start = timestamp(2021, 1, 1, 1, 0, 0)
    if time >= start:
        if crossUP:
            strategy.close('Short', comment='Close Sell')
            strategy.entry('Long', strategy.long, 1, comment='Open Buy')
        if crossDN:
            strategy.close('Long', comment='Close Buy')
            strategy.entry('Short', strategy.short, 1, comment='Open Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
