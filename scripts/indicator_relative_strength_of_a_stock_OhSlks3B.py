"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, dayofmonth, input,
    label, math, month, na, plot, request, script, string, syminfo, ta, time, timeframe, year,
    yloc
)
from pynecore.types import Series


@script.indicator('Relative Strength', shorttitle='Relative Strength')
def main(
    source: Series[float] = input(title='Source', defval=close),
    comparativeTickerId=input.symbol('NSE:NIFTY', title='Comparative Symbol'),
    length=input.int(123, minval=1, title='Period'),
    showZeroLine=input(defval=True, title='Show Zero Line'),
    showRefDateLbl=input(defval=True, title='Show Reference Label'),
    toggleRSColor=input(defval=True, title='Toggle RS color on crossovers'),
    showRSTrend=input.bool(defval=False, title='RS Trend,', group='RS Trend', inline='RS Trend'),
    base=input.int(title='Range', minval=1, defval=5, group='RS Trend', inline='RS Trend'),
    showMA=input.bool(defval=False, title='', group='RS Mean', inline='RS Mean'),
    lengthRSMA=input.int(50, minval=1, title='Period', group='RS Mean', inline='RS Mean'),
    showMAColor=input.bool(defval=True, title='Trend Color', group='RS Mean', inline='RS Mean'),
    showBubbles=input.bool(defval=True, title='', group='Price Confirmation', inline='Color'),
    lengthPriceSMA=input.int(50, minval=1, title='Period', group='Price Confirmation', inline='Color'),
    bullishColor=input.color(color.new(color.green, 85), title='+ve', group='Price Confirmation', inline='Color'),
    bearishColor=input.color(color.new(color.red, 85), title='-ve', group='Price Confirmation', inline='Color')
):
    baseSymbol: Series = request.security(syminfo.tickerid, timeframe.period, source)
    comparativeSymbol: Series = request.security(comparativeTickerId, timeframe.period, source)

    res: Series = baseSymbol / baseSymbol[length] / (comparativeSymbol / comparativeSymbol[length]) - 1
    resColor = (color.green if res > 0 else color.red) if toggleRSColor else color.blue
    refDay = dayofmonth(time[length]) if showRefDateLbl and barstate.islast else na
    refMonth = month(time[length]) if showRefDateLbl and barstate.islast else na
    refYear = year(time[length]) if showRefDateLbl and barstate.islast else na
    refLabelStyle = label.style_label_up if res[length] > 0 else label.style_label_down
    refDateLabel = label.new(bar_index - length, 0, text='RS-' + string.tostring(length) + ' reference, ' + string.tostring(refDay) + '-' + string.tostring(refMonth) + '-' + string.tostring(refYear), color=color.blue, style=refLabelStyle, yloc=yloc.price) if showRefDateLbl and barstate.islast else na
    y0 = res - res[base]
    angle0 = math.atan(y0 / base)
    zeroLineColor = (color.green if angle0 > 0.0 else color.maroon) if showRSTrend else color.maroon
    sma_res = ta.sma(res, lengthRSMA)

    sma_symb = ta.sma(baseSymbol, lengthPriceSMA)
    pos_div = ta.rising(sma_symb, 3) and baseSymbol >= sma_symb
    neg_div = ta.falling(sma_symb, 3) and baseSymbol < sma_symb
    div_started = pos_div or neg_div
    div_color = (bullishColor if pos_div else bearishColor if neg_div else na) if div_started else na
    ma_rising = ta.rising(sma_res, 3)
    ma_falling = ta.falling(sma_res, 3)
    ma_color = color.green if showMAColor and ma_rising else color.red if showMAColor and ma_falling else color.gray

    plot(0 if showZeroLine else na, linewidth=2, color=zeroLineColor, title='Zero Line / RS Trend')
    plot(res, title='RS', linewidth=3, color=resColor)
    plot(sma_res if showMA else na, color=ma_color, title='MA', linewidth=2)
    plot(res if showBubbles and div_started else na, 'Confirmation Bubbles', div_color, 10, plot.style_circles)

    alertcondition(ma_rising, 'Rising Strength', 'Rising Strength')
    alertcondition(ma_falling, 'Declining Strength', 'Declining Strength')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
