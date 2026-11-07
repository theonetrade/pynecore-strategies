"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, close, color, currency, high, hlc3, input, location, low, math,
    open, plot, plotshape, position, request, script, shape, strategy, string, syminfo, ta, table,
    time, timeframe, timestamp
)
from pynecore.types import Persistent, Series, Table


@script.strategy(title='TradePro\'s Trading Idea Cipher B+ Divergence EMA Pullback Strategy', shorttitle='WT MFI RSI EMA PB STRAT', overlay=True, pyramiding=0, max_bars_back=5000, calc_on_order_fills=False, commission_type=strategy.commission.percent, commission_value=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=5000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    FromMonth=input.int(defval=1, title='FromMonth', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='FromDay', minval=1, maxval=31),
    FromYear=input.int(defval=2020, title='FromYear', minval=2016),
    ToMonth=input.int(defval=1, title='ToMonth', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='ToDay', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='ToYear', minval=2017),
    cl=input(14, 'Channel Length'),
    al=input(10, 'Average Length'),
    overbought=input(53, title='WT Overbought Level 1'),
    oversold=input(-60, title='WT Oversold Level 1'),
    rsiMFIPosY=input(1.5, title='MFI Area Y Pos'),
    rsiMFIperiod=input(71, title='MFI Period'),
    rsiMFIMultiplier=input.float(200, title='MFI Area multiplier'),
    res=input.timeframe(title='EMA Timeframe', defval='30'),
    len1=input(title='EMA1 Length', defval=150),
    len2=input(title='EMA2 Length', defval=50),
    enablelong=input(True, title='Enable long?'),
    enableshort=input(True, title='Enable short?'),
    slbuffer=input.float(title='SL Buffer', step=0.1, defval=0),
    enablelowhigh=input(False, title='Enable lowest low/ highest high exit?'),
    profitfactorlong=input.float(title='ProfitfactorLong', step=0.1, defval=2),
    loLen=input.int(title='Lowest Low Lookback', defval=60, minval=2),
    profitfactorshort=input.float(title='ProfitfactorShort', step=0.1, defval=0.5),
    highLen=input.int(title='highest high lookback', defval=50, minval=2),
    enableatr=input(True, title='Enable ATR exit?'),
    atrprofitfactorlong=input.float(title='ATR Profitfactor Long', step=0.1, defval=2),
    atrstopfactorlong=input.float(title='ATR Stopfactor Long', step=0.1, defval=4),
    atrprofitfactorshort=input.float(title='ATR Profitfactor Short', step=0.1, defval=2),
    atrstopfactorshort=input.float(title='ATR Stopfactor Short', step=0.1, defval=4),
    lengthATR=input.int(title='ATR Length', defval=11, minval=1)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    afterStartDate = True if time >= start and time <= finish else False
    zeroline: int = 0
    ap = hlc3
    esa = ta.ema(ap, cl)
    d = ta.ema(math.abs(ap - esa), cl)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, al)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)
    wtOs = wt2 <= oversold
    wtOb = wt2 >= overbought
    wtX = ta.cross(wt1, wt2)
    wtUp = wt2 - wt1 <= 0
    wtDown = wt2 - wt1 >= 0
    buySignal = wtX and wtOs and wtUp
    sellSignal = wtX and wtOb and wtDown
    def f_rsimfi(_period, _multiplier, _tf):
        return request.security(syminfo.tickerid, _tf, ta.sma((close - open) / (high - low) * _multiplier, _period) - rsiMFIPosY)

    rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    emasrc = close
    col1 = color.yellow
    col2 = color.blue
    ema1 = ta.ema(emasrc, len1)
    emaSmooth1 = request.security(syminfo.tickerid, res, ema1, barmerge.gaps_off, barmerge.lookahead_off)
    ema2 = ta.ema(emasrc, len2)
    emaSmooth2: Series = request.security(syminfo.tickerid, res, ema2, barmerge.gaps_off, barmerge.lookahead_off)
    plot(emaSmooth1, title='EMA1', linewidth=1, color=color.new(col1, 0))
    plot(emaSmooth2, title='EMA2', linewidth=1, color=color.new(col2, 0))
    upcondition = close > emaSmooth1
    wavetrendlong = cast_bool(wt1) and wt2 < zeroline
    mfilong = rsiMFI > 0
    emapblong1 = close > emaSmooth2 and close[1] < emaSmooth2[1]
    emapblong2 = close[2] > emaSmooth2[2] and close[3] > emaSmooth2[3] and (close[4] > emaSmooth2[4]) or (close[5] > emaSmooth2[5] and close[6] > emaSmooth2[6] and (close[7] > emaSmooth2[7])) or (close[8] > emaSmooth2[8] and close[9] > emaSmooth2[9] and (close[10] > emaSmooth2[10]))
    longcondition = upcondition and wavetrendlong and buySignal and mfilong and emapblong1 and emapblong2
    if longcondition and afterStartDate and (strategy.opentrades < 1) and (enablelong == True):
        strategy.entry('long', strategy.long)
    plotshape(longcondition, style=shape.arrowup, location=location.abovebar, color=color.new(color.green, 0))
    downcondition = close < emaSmooth1
    wavetrendshort = cast_bool(wt1) and wt2 > zeroline
    mfishort = rsiMFI < 0
    emapbshort1 = close < emaSmooth2 and close[1] > emaSmooth2[1]
    emapbshort2 = close[2] < emaSmooth2[2] and close[3] < emaSmooth2[3] and (close[4] < emaSmooth2[4]) or (close[5] < emaSmooth2[5] and close[6] < emaSmooth2[6] and (close[7] < emaSmooth2[7])) or (close[8] < emaSmooth2[8] and close[9] < emaSmooth2[9] and (close[10] < emaSmooth2[10]))
    shortcondition = downcondition and wavetrendshort and sellSignal and mfishort and emapbshort1 and emapbshort2
    if shortcondition and afterStartDate and (strategy.opentrades < 1) and (enableshort == True):
        strategy.entry('short', strategy.short)
    plotshape(shortcondition, style=shape.arrowdown, location=location.belowbar, color=color.new(color.red, 0))
    bought = strategy.position_size[1] < strategy.position_size
    sold = strategy.position_size[1] > strategy.position_size
    barsbought = ta.barssince(bought)
    barssold = ta.barssince(sold)
    exittable: Persistent[Table] = table.new(position.top_right, 4, 3, bgcolor=color.gray, frame_width=2, frame_color=color.black)
    stop_level_long: Series = inline_series(ta.lowest(low, loLen), 1)
    if enablelowhigh == True and strategy.position_size > 0 and (strategy.position_entry_name == 'long'):
        profit_level = strategy.position_avg_price + (strategy.position_avg_price - stop_level_long[barsbought]) * profitfactorlong + slbuffer
        table.cell(exittable, 0, 0, 'SL Long')
        table.cell(exittable, 0, 1, 'TP Long')
        table.cell(exittable, 1, 0, string.tostring(stop_level_long[barsbought]))
        table.cell(exittable, 1, 1, string.tostring(profit_level))
        strategy.exit(id='TP/ SL', stop=stop_level_long[barsbought] - slbuffer, limit=profit_level)
    stop_level_short: Series = inline_series(ta.highest(high, highLen), 1)
    if enablelowhigh == True and strategy.position_size < 0 and (strategy.position_entry_name == 'short'):
        profit_level = strategy.position_avg_price - (stop_level_short[barssold] - strategy.position_avg_price) * profitfactorshort - slbuffer
        table.cell(exittable, 2, 0, 'SL Short')
        table.cell(exittable, 2, 1, 'TP Long')
        table.cell(exittable, 3, 0, string.tostring(stop_level_short[barsbought]))
        table.cell(exittable, 3, 1, string.tostring(profit_level))
        strategy.exit(id='TP/ SL', stop=stop_level_short[barssold] + slbuffer, limit=profit_level)
    atr = ta.atr(lengthATR)
    if afterStartDate and enableatr == True and (strategy.opentrades > 0) and (strategy.position_entry_name == 'long'):
        profit_level: Series = strategy.position_avg_price + atr * atrprofitfactorlong
        stop_level: Series = strategy.position_avg_price - atr * atrstopfactorlong
        table.cell(exittable, 0, 0, 'SL Long')
        table.cell(exittable, 0, 1, 'TP Long')
        table.cell(exittable, 0, 2, 'Last Long Position')
        table.cell(exittable, 1, 0, string.tostring(stop_level[barsbought]))
        table.cell(exittable, 1, 1, string.tostring(profit_level[barsbought]))
        table.cell(exittable, 1, 2, string.tostring(strategy.position_avg_price))
        strategy.exit('Take Profit/ Stop Loss', 'long', stop=stop_level[barsbought], limit=profit_level[barsbought])
    profit_level_atr_long: Series = strategy.position_avg_price + atr * atrprofitfactorlong
    stop_level_atr_long: Series = strategy.position_avg_price - atr * atrstopfactorlong
    stop_atr_long = stop_level_atr_long[barsbought]
    profit_atr_long = profit_level_atr_long[barsbought]
    plot(profit_atr_long, title='Take Profit Long', linewidth=1, color=color.new(color.green, 0))
    plot(stop_atr_long, title='Stop Loss Long', linewidth=1, color=color.new(color.red, 0))
    if afterStartDate and enableatr == True and (strategy.opentrades > 0) and (strategy.position_entry_name == 'short'):
        profit_level: Series = strategy.position_avg_price - atr * atrprofitfactorshort
        stop_level: Series = strategy.position_avg_price + atr * atrstopfactorshort
        table.cell(exittable, 2, 0, 'SL Short')
        table.cell(exittable, 2, 1, 'TP Short')
        table.cell(exittable, 2, 2, 'Last Short Position')
        table.cell(exittable, 3, 0, string.tostring(stop_level[barssold]))
        table.cell(exittable, 3, 1, string.tostring(profit_level[barssold]))
        table.cell(exittable, 3, 2, string.tostring(strategy.position_avg_price))
        strategy.exit('Take Profit/ Stop Loss', 'short', stop=stop_level[barssold], limit=profit_level[barssold])
    profit_level_atr_short: Series = strategy.position_avg_price - atr * atrprofitfactorshort
    stop_level_atr_short: Series = strategy.position_avg_price + atr * atrstopfactorshort
    stop_atr_short = stop_level_atr_short[barssold]
    profit_atr_short = profit_level_atr_short[barssold]
    plot(profit_atr_short, title='Take Profit Short', linewidth=1, color=color.new(color.green, 0))
    plot(stop_atr_short, title='Stop Loss Short', linewidth=1, color=color.new(color.red, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
