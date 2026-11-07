"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, plot, script, strategy,
    syminfo, ta
)
from pynecore.types import Persistent, PersistentSeries


@script.strategy('Stepped trailing strategy example', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    __input_0__=input(5, title='stop loss %%'),
    __input_1__=input(5, title='take profit 1 %%'),
    __input_2__=input(10, title='take profit 2 %%'),
    __input_3__=input(15, title='take profit 3 %%'),
    activateTrailingOnThirdStep=input(False, title='activate trailing on third stage (tp3 is amount, tp2 is offset level)')
):
    if ta.crossover(ta.sma(close, 14), ta.sma(close, 28)):
        strategy.entry('My Long Entry Id', strategy.long)
    def percent2points(percent):
        return strategy.position_avg_price * percent / 100 / syminfo.mintick

    sl = percent2points(__input_0__)
    tp1 = percent2points(__input_1__)
    tp2 = percent2points(__input_2__)
    tp3 = percent2points(__input_3__)
    def curProfitInPts():
        __block_result__ = na
        if strategy.position_size > 0:
            __block_result__ = (high - strategy.position_avg_price) / syminfo.mintick
        elif strategy.position_size < 0:
            __block_result__ = (strategy.position_avg_price - low) / syminfo.mintick
        else:
            __block_result__ = 0
        return __block_result__

    def calcStopLossPrice(OffsetPts):
        __block_result_1__ = na
        if strategy.position_size > 0:
            __block_result_1__ = strategy.position_avg_price - OffsetPts * syminfo.mintick
        elif strategy.position_size < 0:
            __block_result_1__ = strategy.position_avg_price + OffsetPts * syminfo.mintick
        else:
            __block_result_1__ = na
        return __block_result_1__

    def calcProfitTrgtPrice(OffsetPts):
        return calcStopLossPrice(-OffsetPts)

    def getCurrentStage():
        stage: Persistent[int] = 0
        if strategy.position_size == 0:
            stage = 0
        curProfitInPts_1 = curProfitInPts()
        curProfitInPts_2 = curProfitInPts()
        if stage == 0 and strategy.position_size != 0:
            stage = 1
        elif stage == 1 and curProfitInPts_1 >= tp1:
            stage = 2
        elif stage == 2 and curProfitInPts_2 >= tp2:
            stage = 3
        return stage

    def calcTrailingAmountLevel(points):
        level: PersistentSeries[float] = na(float)
        level = calcProfitTrgtPrice(points)
        __block_result_2__ = na
        if not na(level):
            __block_result_3__ = na
            if strategy.position_size > 0:
                if not na(level[1]):
                    level = math.max(level[1], level)
                __block_result_4__ = na
                if not na(level):
                    level = math.max(high, level)
                    __block_result_4__ = level
                __block_result_3__ = __block_result_4__
            elif strategy.position_size < 0:
                if not na(level[1]):
                    level = math.min(level[1], level)
                __block_result_5__ = na
                if not na(level):
                    level = math.min(low, level)
                    __block_result_5__ = level
                __block_result_3__ = __block_result_5__
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def calcTrailingOffsetLevel(points, offset):
        result: float = na(float)
        amountLevel = calcTrailingAmountLevel(points)
        if strategy.position_size > 0:
            trailActiveDiff = amountLevel - calcProfitTrgtPrice(points)
            if trailActiveDiff > 0:
                result = trailActiveDiff + calcProfitTrgtPrice(offset)
        elif strategy.position_size < 0:
            trailActiveDiff = calcProfitTrgtPrice(points) - amountLevel
            if trailActiveDiff > 0:
                result = calcProfitTrgtPrice(offset) - trailActiveDiff
        return result

    stopLevel: float = na(float)
    trailOffsetLevel: float = na(float)
    profitLevel: float = calcTrailingAmountLevel(tp3) if activateTrailingOnThirdStep else calcProfitTrgtPrice(tp3)
    trailOffsetLevelTmp = calcTrailingOffsetLevel(tp3, tp2)
    curStage = getCurrentStage()
    if curStage == 1:
        stopLevel = calcStopLossPrice(sl)
        strategy.exit('x', loss=sl, profit=tp3, comment='sl or tp3')
    elif curStage == 2:
        stopLevel = calcStopLossPrice(0)
        strategy.exit('x', stop=stopLevel, profit=tp3, comment='breakeven or tp3')
    elif curStage == 3:
        stopLevel = calcStopLossPrice(-tp1)
        if activateTrailingOnThirdStep:
            trailOffsetLevel = trailOffsetLevelTmp
            strategy.exit('x', stop=stopLevel, trail_points=tp3, trail_offset=tp3 - tp2, comment='stop tp1 or trailing tp3 with offset tp2')
        else:
            strategy.exit('x', stop=stopLevel, profit=tp3, comment='tp1 or tp3')
    else:
        strategy.cancel('x')
    plot(stopLevel, style=plot.style_linebr, color=color.new(color.red, 0))
    plot(profitLevel, style=plot.style_linebr, color=color.new(color.blue, 0))
    plot(trailOffsetLevel, style=plot.style_linebr, color=color.new(color.green, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
