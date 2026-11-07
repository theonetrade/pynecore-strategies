"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, high, input, location, low, na, ohlc4, open,
    plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import NA, PersistentSeries


@script.strategy('Inside Bar Strategy w/ SL', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=10000, commission_value=0.04, calc_on_every_tick=False, slippage=0, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    direction__global__=input.int(0, title='Strategy Direction', minval=-1, maxval=1),
    title1=input(True, '-----------------Strategy Inputs-------------------'),
    i_NBars=input.int(defval=1, title='# Of Inside Bars in pattern', options=(1, 2, 3, 4)),
    i_BarsDirection=input(False, title='Only trade using complete bullish or bearish patterns'),
    i_MAFilter=input(True, title='Use MA Trend Filter'),
    i_MALen=input(65, title='MA Length'),
    title2=input(True, '-----------------General Inputs-------------------'),
    i_SL=input(True, title='Use Stop Loss and Take Profit'),
    i_SLType=input.string(defval='ATR Stop', title='Type Of Stop', options=('Strategy Stop', 'Swing Lo/Hi', 'ATR Stop')),
    i_SPL=input(defval=10, title='Swing Point Lookback'),
    __input_10__=input.float(defval=1, step=0.1, title='Swing Point SL Perc Increment'),
    i_ATR=input(14, title='ATR Length'),
    i_ATRMult=input.float(5, step=0.1, title='ATR Multiple'),
    i_TPRRR=input.float(2, step=0.1, title='Take Profit Risk Reward Ratio'),
    TS=input(False, title='Trailing Stop'),
    DPR=input(True, 'Allow Direct Position Reverse'),
    reverse=input(False, 'Reverse Trades')
):
    strategy.risk.allow_entry_in(strategy.direction.all if direction__global__ == 0 else strategy.direction.short if direction__global__ < 0 else strategy.direction.long)
    i_PercIncrement = __input_10__ * 0.01
    bought = strategy.position_size > strategy.position_size[1] or strategy.position_size < strategy.position_size[1]
    LL = ta.lowest(i_SPL) * (1 - i_PercIncrement)
    HH = ta.highest(i_SPL) * (1 + i_PercIncrement)
    LL_price = ta.valuewhen(bought, LL, 0)
    HH_price = ta.valuewhen(bought, HH, 0)
    entry_LL_price = LL_price if strategy.position_size > 0 else na
    entry_HH_price = HH_price if strategy.position_size < 0 else na
    tp = strategy.position_avg_price + (strategy.position_avg_price - entry_LL_price) * i_TPRRR
    stp = strategy.position_avg_price - (entry_HH_price - strategy.position_avg_price) * i_TPRRR
    ATR = ta.atr(i_ATR) * i_ATRMult
    ATRLong = ohlc4 - ATR
    ATRShort = ohlc4 + ATR
    ATRLongStop = ta.valuewhen(bought, ATRLong, 0)
    ATRShortStop = ta.valuewhen(bought, ATRShort, 0)
    LongSL_ATR_price = ATRLongStop if strategy.position_size > 0 else na
    ShortSL_ATR_price = ATRShortStop if strategy.position_size < 0 else na
    ATRtp = strategy.position_avg_price + (strategy.position_avg_price - LongSL_ATR_price) * i_TPRRR
    ATRstp = strategy.position_avg_price - (ShortSL_ATR_price - strategy.position_avg_price) * i_TPRRR
    LongStop: float = ta.valuewhen(bought, low[1], 0) * (1 - i_PercIncrement)
    ShortStop: float = ta.valuewhen(bought, high[1], 0) * (1 + i_PercIncrement)
    StratTP: float = na(float)
    StratSTP: float = na(float)
    MAFilter = close > ta.sma(close, i_MALen)
    plot(ta.sma(close, i_MALen) if i_MAFilter else na)
    bullBar = close > open
    bearBar = close < open
    contbullBar = ta.barssince(not bullBar) >= i_NBars + 1
    contbearBar = ta.barssince(not bearBar) >= i_NBars + 1
    def InsideBar(NBars):
        Inside1Bar = high < high[1] and low > low[1]
        Inside2Bar = high < high[2] and low > low[2] and Inside1Bar
        Inside3Bar = high < high[3] and low > low[3] and Inside1Bar and Inside2Bar
        Inside4Bar = high < high[4] and low > low[4] and Inside1Bar and Inside2Bar and Inside3Bar
        __block_result__ = na
        if NBars == 1:
            inside1Bar = Inside1Bar
            __block_result__ = (inside1Bar,)
        elif NBars == 2:
            inside2Bar = Inside2Bar
            __block_result__ = (inside2Bar,)
        elif NBars == 3:
            inside3Bar = Inside3Bar
            __block_result__ = (inside3Bar,)
        elif NBars == 4:
            inside4Bar = Inside4Bar
            __block_result__ = (inside4Bar,)
        else:
            __block_result__ = (na,)
        return __block_result__

    insideBar, = InsideBar(i_NBars)
    bullInsideBar = bar_index > 40 and insideBar and bullBar and (contbullBar if i_BarsDirection else True) and (MAFilter if i_MAFilter else True)
    bearInsideBar = bar_index > 40 and insideBar and bearBar and (contbearBar if i_BarsDirection else True) and (not MAFilter if i_MAFilter else True)
    BUY = bullInsideBar
    SELL = bearInsideBar
    plot(1 if contbullBar else 0, title='contbullBar')
    plot(1 if contbearBar else 0, title='contbearBar')
    if reverse:
        if not DPR:
            if SELL and strategy.position_size == 0:
                strategy.entry('long', strategy.long)
            if BUY and strategy.position_size == 0:
                strategy.entry('short', strategy.short)
        else:
            if SELL:
                strategy.entry('long', strategy.long)
            if BUY:
                strategy.entry('short', strategy.short)
    else:
        if not DPR:
            if BUY and strategy.position_size == 0:
                strategy.entry('long', strategy.long)
            if SELL and strategy.position_size == 0:
                strategy.entry('short', strategy.short)
        else:
            if BUY:
                strategy.entry('long', strategy.long)
            if SELL:
                strategy.entry('short', strategy.short)
    SL = entry_LL_price if i_SLType == 'Swing Lo/Hi' else LongSL_ATR_price if i_SLType == 'ATR Stop' else LongStop
    SSL = entry_HH_price if i_SLType == 'Swing Lo/Hi' else ShortSL_ATR_price if i_SLType == 'ATR Stop' else ShortStop
    TP = tp if i_SLType == 'Swing Lo/Hi' else ATRtp if i_SLType == 'ATR Stop' else StratTP
    STP = stp if i_SLType == 'Swing Lo/Hi' else ATRstp if i_SLType == 'ATR Stop' else StratSTP
    dif = ta.valuewhen(strategy.position_size > 0 and strategy.position_size[1] <= 0, high, 0) - strategy.position_avg_price
    trailOffset = strategy.position_avg_price - SL
    tstop: PersistentSeries = NA(float)
    if strategy.position_size > 0:
        tstop = high - trailOffset - dif
        if tstop < tstop[1]:
            tstop = tstop[1]
    else:
        tstop = na
    StrailOffset = SSL - strategy.position_avg_price
    Ststop: PersistentSeries = NA(float)
    Sdif = strategy.position_avg_price - ta.valuewhen(strategy.position_size < 0 and strategy.position_size[1] >= 0, low, 0)
    if strategy.position_size < 0:
        Ststop = low + StrailOffset + Sdif
        if Ststop > Ststop[1]:
            Ststop = Ststop[1]
    else:
        Ststop = na
    if i_SL:
        strategy.exit('TP & SL', 'long', limit=TP, stop=tstop if TS else SL)
    if i_SL:
        strategy.exit('TP & SL', 'short', limit=STP, stop=Ststop if TS else SSL)
    plot(SL if i_SL and strategy.position_size > 0 and (not TS) else tstop if i_SL and strategy.position_size > 0 and TS else na, title='SL', style=plot.style_cross, color=color.new(color.red, 0))
    plot(SSL if i_SL and strategy.position_size < 0 and (not TS) else Ststop if i_SL and strategy.position_size < 0 and TS else na, title='SSL', style=plot.style_cross, color=color.new(color.red, 0))
    plot(TP if i_SL and strategy.position_size > 0 else na, title='TP', style=plot.style_cross, color=color.new(color.green, 0))
    plot(STP if i_SL and strategy.position_size < 0 else na, title='STP', style=plot.style_cross, color=color.new(color.green, 0))
    plotshape(1 if BUY else na, style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), title='Bullish Setup', size=size.auto)
    plotshape(1 if SELL else na, style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), title='Bearish Setup', size=size.auto)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
