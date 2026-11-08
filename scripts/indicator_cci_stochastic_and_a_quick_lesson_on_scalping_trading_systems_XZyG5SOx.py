"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, hline, input, location, na, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('CCI Stochastic', shorttitle='CCI_S', overlay=False, na_bool=True)
def main(
    source: Series[float] = input(close),
    cci_period=input(28, 'CCI Period'),
    stoch_period=input(28, 'Stoch Period'),
    stoch_smooth_k=input(3, 'Stoch Smooth K'),
    stoch_smooth_d=input(3, 'Stoch Smooth D'),
    d_or_k=input.string(defval='D', options=('D', 'K')),
    OB=input(80, 'Overbought'),
    OS=input(20, 'Oversold'),
    showArrows=input(True, 'Show Arrows'),
    showArrowsEnter=input(True, 'Show Arrows on Enter zone'),
    showArrowsCenter=input(False, 'Show Arrows on Center zone'),
    showArrowsExit=input(True, 'Show Arrows on Exit zone')
):
    cci = ta.cci(source, cci_period)
    stoch_cci_k = ta.sma(ta.stoch(cci, cci, cci, stoch_period), stoch_smooth_k)
    stoch_cci_d = ta.sma(stoch_cci_k, stoch_smooth_d)
    ma = stoch_cci_d if d_or_k == 'D' else stoch_cci_k
    __block_result__ = na
    if showArrowsEnter:
        __block_result_1__ = na
        if ta.crossunder(ma, OS):
            __block_result_1__ = 1
        else:
            __block_result_2__ = na
            if ta.crossover(ma, OB):
                __block_result_2__ = -1
            __block_result_1__ = __block_result_2__
        __block_result__ = __block_result_1__
    trend_enter = __block_result__
    __block_result_3__ = na
    if showArrowsExit:
        __block_result_4__ = na
        if ta.crossunder(ma, OB):
            __block_result_4__ = -1
        else:
            __block_result_5__ = na
            if ta.crossover(ma, OS):
                __block_result_5__ = 1
            __block_result_4__ = __block_result_5__
        __block_result_3__ = __block_result_4__
    trend_exit = __block_result_3__
    __block_result_6__ = na
    if showArrowsCenter:
        __block_result_7__ = na
        if ta.crossunder(ma, 50):
            __block_result_7__ = -1
        else:
            __block_result_8__ = na
            if ta.crossover(ma, 50):
                __block_result_8__ = 1
            __block_result_7__ = __block_result_8__
        __block_result_6__ = __block_result_7__
    trend_center = __block_result_6__
    overbought = hline(OB, title='Upper Line', linestyle=hline.style_solid, linewidth=1, color=color.red)
    oversold = hline(OS, title='Lower Line', linestyle=hline.style_solid, linewidth=1, color=color.lime)
    band2 = hline(50, title='Mid Line', linestyle=hline.style_solid, linewidth=1, color=color.gray)
    ma_color = color.red if ma > OB else color.green if ma < OS else color.gray
    plot(ma, 'Moving Average', linewidth=3, color=ma_color)
    maxLevelPlot = hline(100, title='Max Level', linestyle=hline.style_dotted, color=color.new(color.white, 100))
    minLevelPlot = hline(0, title='Min Level', linestyle=hline.style_dotted, color=color.new(color.white, 100))
    color_fill_os = color.new(color.red, 90) if ma > OB else color.new(color.white, 100)
    color_fill_ob = color.new(color.green, 90) if ma < OS else color.new(color.white, 100)
    fill(maxLevelPlot, overbought, color=color_fill_os)
    fill(minLevelPlot, oversold, color=color_fill_ob)
    plotshape(0 if showArrows and showArrowsEnter and (trend_enter == 1) else na, color=color.new(color.green, 20), style=shape.arrowup, size=size.normal, location=location.absolute, title='Trend Enter Buy')
    plotshape(100 if showArrows and showArrowsEnter and (trend_enter == -1) else na, color=color.new(color.red, 20), style=shape.arrowdown, size=size.normal, location=location.absolute, title='Trend Enter Sell')
    plotshape(35 if showArrows and showArrowsCenter and (trend_center == 1) else na, color=color.new(color.aqua, 20), style=shape.arrowup, size=size.normal, location=location.absolute, title='Trend Center Buy')
    plotshape(65 if showArrows and showArrowsCenter and (trend_center == -1) else na, color=color.new(color.fuchsia, 20), style=shape.arrowdown, size=size.normal, location=location.absolute, title='Trend Center Sell')
    plotshape(0 if showArrows and showArrowsExit and (trend_exit == 1) else na, color=color.new(color.orange, 20), style=shape.arrowup, size=size.normal, location=location.absolute, title='Trend Exit Buy')
    plotshape(100 if showArrows and showArrowsExit and (trend_exit == -1) else na, color=color.new(color.maroon, 20), style=shape.arrowdown, size=size.normal, location=location.absolute, title='Trend Exit Sell')
    alertcondition(showArrows and showArrowsEnter and (trend_enter == 1), message='Trend Enter Buy', title='Trend Enter Buy')
    alertcondition(showArrows and showArrowsEnter and (trend_enter == -1), message='Trend Enter Sell', title='Trend Enter Sell')
    alertcondition(showArrows and showArrowsCenter and (trend_center == 1), message='Trend Center Buy', title='Trend Center Buy')
    alertcondition(showArrows and showArrowsCenter and (trend_center == -1), message='Trend Center Sell', title='Trend Center Sell')
    alertcondition(showArrows and showArrowsExit and (trend_exit == 1), message='Trend Exit Buy', title='Trend Exit Buy')
    alertcondition(showArrows and showArrowsExit and (trend_exit == -1), message='Trend Exit Sell', title='Trend Exit Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
