"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, plot, script, strategy, ta


@script.strategy('EMA Slope Trend Follower', initial_capital=10000, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.06, slippage=2, default_qty_value=30, overlay=False, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    average=input.string(title='Source MA Type', defval='EMA', options=('EMA', 'SMA')),
    len=input.int(130, minval=1, title='Source MA Length'),
    slopeFlen=input(9, title='Fast Slope MA Length'),
    slopeSlen=input(21, title='Slow Slope MA Length'),
    trendfilter=input(True, title='Trend Filter'),
    trendfilterperiod=input(200, title='Trend Filter MA Period'),
    trendfiltertype=input.string(title='Trend Filter MA Type', defval='EMA', options=('EMA', 'SMA')),
    volatilityfilter=input(False, title='Volatility Filter'),
    volatilitystdevlength=input(20, title='Vol Filter STDev Length'),
    volatilitystdevmalength=input(30, title='Vol Filter STDev MA Length')
):
    __block_result__ = na
    if average == 'EMA':
        __block_result__ = ta.ema(close, len)
    else:
        __block_result__ = ta.sma(close, len)
    out = __block_result__
    slp = ta.change(out) / out
    emaslopeF = ta.ema(slp, slopeFlen)
    emaslopeS = ta.ema(slp, slopeSlen)
    __block_result_1__ = na
    if trendfiltertype == 'EMA':
        __block_result_1__ = close > ta.ema(close, trendfilterperiod)
    else:
        __block_result_1__ = close > ta.sma(close, trendfilterperiod)
    TrendConditionL = __block_result_1__
    __block_result_2__ = na
    if trendfiltertype == 'EMA':
        __block_result_2__ = close < ta.ema(close, trendfilterperiod)
    else:
        __block_result_2__ = close < ta.sma(close, trendfilterperiod)
    TrendConditionS = __block_result_2__
    VolatilityCondition = ta.stdev(close, volatilitystdevlength) > ta.sma(ta.stdev(close, volatilitystdevlength), volatilitystdevmalength)
    __block_result_3__ = na
    if trendfilter == True:
        __block_result_4__ = na
        if volatilityfilter == True:
            __block_result_4__ = emaslopeF > emaslopeS and TrendConditionL and VolatilityCondition
        else:
            __block_result_4__ = emaslopeF > emaslopeS and TrendConditionL
        __block_result_3__ = __block_result_4__
    else:
        __block_result_5__ = na
        if volatilityfilter == True:
            __block_result_5__ = emaslopeF > emaslopeS and VolatilityCondition
        else:
            __block_result_5__ = emaslopeF > emaslopeS
        __block_result_3__ = __block_result_5__
    ConditionEntryL = __block_result_3__
    __block_result_6__ = na
    if trendfilter == True:
        __block_result_7__ = na
        if volatilityfilter == True:
            __block_result_7__ = emaslopeF < emaslopeS and TrendConditionS and VolatilityCondition
        else:
            __block_result_7__ = emaslopeF < emaslopeS and TrendConditionS
        __block_result_6__ = __block_result_7__
    else:
        __block_result_8__ = na
        if volatilityfilter == True:
            __block_result_8__ = emaslopeF < emaslopeS and VolatilityCondition
        else:
            __block_result_8__ = emaslopeF < emaslopeS
        __block_result_6__ = __block_result_8__
    ConditionEntryS = __block_result_6__
    ConditionExitL = ta.crossunder(emaslopeF, emaslopeS)
    ConditionExitS = ta.crossover(emaslopeF, emaslopeS)
    plot(slp, color=color.new(color.white, 0))
    plot(emaslopeF, color=color.new(color.yellow, 0))
    plot(emaslopeS, color=color.new(color.red, 0))
    if ConditionExitS:
        if strategy.position_size < 0:
            strategy.close('SLPShort')
    if ConditionExitL:
        if strategy.position_size > 0:
            strategy.close('SLPLong')
    if ConditionEntryL:
        strategy.entry('SLPLong', direction=strategy.long)
    if ConditionEntryS:
        strategy.entry('SLPShort', direction=strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
