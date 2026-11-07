"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, hline, input, low, na, plot, script, strategy, ta
from pynecore.types import Color, PersistentSeries, Series


@script.strategy('2xTP, SL to entry', overlay=False, pyramiding=0, calc_on_every_tick=False, default_qty_type=strategy.percent_of_equity, default_qty_value=25, initial_capital=1000, commission_type=strategy.commission.percent, commission_value=0.01, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    tp1=input.float(200, title='Take Profit 1'),
    tp2=input.float(500, title='Take Profit 2'),
    sl=input.float(200, title='Stop Loss'),
    stOBOS=input.bool(True, title='Use Stochastic overbought/oversold threshold')
):
    colorRed: Color = color.new('#FF2052')
    colorGreen: Color = color.new('#66FF00')
    def f_stochastic():
        stoch = ta.stoch(close, high, low, 14)
        stoch_K = ta.sma(stoch, 3)
        stoch_D = ta.sma(stoch_K, 3)
        stRD = ta.crossunder(stoch_K, stoch_D)
        stGD = ta.crossover(stoch_K, stoch_D)
        return (stoch_K, stoch_D, stRD, stGD)

    bbUpper: Series
    bbLower: Series
    bbMiddle, bbUpper, bbLower = ta.bb(close, 20, 2)
    stoch_K: Series
    stRD: Series
    stGD: Series
    stoch_K, stoch_D, stRD, stGD = f_stochastic()
    inLong = strategy.position_size > 0
    inShort = strategy.position_size < 0
    longClose = strategy.position_size < strategy.position_size[1]
    shortClose = strategy.position_size > strategy.position_size[1]
    longCondition = low[1] < bbLower[1] and stGD[1] and (stoch_K[1] < 25) if stOBOS else low[1] < bbLower[1] and stGD[1]
    shortCondition = high[1] > bbUpper[1] and stRD[1] and (stoch_K[1] > 75) if stOBOS else high[1] > bbUpper[1] and stRD[1]
    longTP1 = strategy.position_avg_price + tp1
    longTP2 = strategy.position_avg_price + tp2
    shortTP1 = strategy.position_avg_price - tp1
    shortTP2 = strategy.position_avg_price - tp2
    longSL: PersistentSeries[float] = 0.0
    shortSL: PersistentSeries[float] = 0.0
    barssince_1 = ta.barssince(longClose)
    barssince_2 = ta.barssince(longCondition)
    __block_result__ = na
    if inLong and barssince_1 < barssince_2:
        __block_result__ = strategy.position_avg_price
    elif inLong:
        __block_result__ = longSL[1]
    else:
        __block_result__ = close - sl
    longSL = __block_result__
    barssince_3 = ta.barssince(shortClose)
    barssince_4 = ta.barssince(shortCondition)
    __block_result_1__ = na
    if inShort and barssince_3 < barssince_4:
        __block_result_1__ = strategy.position_avg_price
    elif inShort:
        __block_result_1__ = shortSL[1]
    else:
        __block_result_1__ = close + sl
    shortSL = __block_result_1__
    if longCondition:
        strategy.entry('Long', strategy.long)
    strategy.exit('TP1/SL', from_entry='Long', qty_percent=50, limit=longTP1, stop=longSL)
    strategy.exit('TP2/SL', from_entry='Long', limit=longTP2, stop=longSL)
    if shortCondition:
        strategy.entry('Short', strategy.short)
    strategy.exit('TP1/SL', from_entry='Short', qty_percent=50, limit=shortTP1, stop=shortSL)
    strategy.exit('TP2/SL', from_entry='Short', limit=shortTP2, stop=shortSL)
    plot(stoch_K, color=color.blue)
    plot(stoch_D, color=color.orange)
    plot((stoch_D if stRD and stoch_K >= 75 else na) if stOBOS else stoch_D if stRD else na, color=colorRed, style=plot.style_circles, linewidth=3)
    plot((stoch_D if stGD and stoch_K <= 25 else na) if stOBOS else stoch_K if stGD else na, color=colorGreen, style=plot.style_circles, linewidth=3)
    hline(75, linestyle=hline.style_dotted)
    hline(25, linestyle=hline.style_dotted)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
