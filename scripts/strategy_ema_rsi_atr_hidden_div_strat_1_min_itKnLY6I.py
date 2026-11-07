"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, currency, high, input, low, na, plot, position, script,
    strategy, string, ta, table, time, timestamp
)
from pynecore.types import Persistent, Series, Table


@script.strategy(title='EMA RSI ATR Hidden Div Strat', shorttitle='Hidden Div Strat', overlay=True, pyramiding=0, max_bars_back=3000, calc_on_order_fills=False, commission_type=strategy.commission.percent, commission_value=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=5000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    FromMonth=input.int(defval=1, title='FromMonth', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='FromDay', minval=1, maxval=31),
    FromYear=input.int(defval=2020, title='FromYear', minval=2016),
    ToMonth=input.int(defval=1, title='ToMonth', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='ToDay', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='ToYear', minval=2017),
    len1=input.int(50, minval=1, title='EMA1'),
    len2=input.int(150, minval=1, title='EMA2'),
    periodK=input.int(3, title='K', minval=1),
    periodD=input.int(3, title='D', minval=1),
    smoothK=input.int(4, title='Smooth', minval=1),
    len=input.int(title='RSI Period', minval=1, defval=9),
    src: Series[float] = input(title='RSI Source', defval=close),
    lbR=input(title='Pivot Lookback Right', defval=0),
    lbL=input(title='Pivot Lookback Left', defval=4),
    rangeUpper=input(title='Max of Lookback Range', defval=6),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    enablelong=input(True, title='Enable long?'),
    enableshort=input(True, title='Enable short?'),
    slbuffer=input.float(title='SL Buffer', step=0.1, defval=0),
    enablelowhigh=input(False, title='Enable lowest low/ highest high exit?'),
    profitfactorlong=input.float(title='ProfitfactorLong', step=0.1, defval=2),
    loLen=input.int(title='Lowest Low Lookback', defval=60, minval=2),
    profitfactorshort=input.float(title='ProfitfactorShort', step=0.1, defval=0.5),
    highLen=input.int(title='highest high lookback', defval=50, minval=2),
    enableatr=input(True, title='Enable ATR exit?'),
    atrprofitfactorlong=input.float(title='ATR Profitfactor Long', step=0.1, defval=9),
    atrstopfactorlong=input.float(title='ATR Stopfactor Long', step=0.1, defval=5),
    atrprofitfactorshort=input.float(title='ATR Profitfactor Short', step=0.1, defval=9),
    atrstopfactorshort=input.float(title='ATR Stopfactor Short', step=0.1, defval=5),
    lengthATR=input.int(title='ATR Length', defval=11, minval=1)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    afterStartDate = True if time >= start and time <= finish else False
    emasrc = close
    ema1: Series = ta.ema(emasrc, len1)
    col1 = color.white
    ema2: Series = ta.ema(emasrc, len2)
    col2 = color.yellow
    k: Series = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d: Series = ta.sma(k, periodD)
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    osc: Series = ta.rsi(src, len)
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond: Series = priceHL and oscLL and plFound
    _inRange_2 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_2
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond: Series = priceLH and oscHH and phFound
    buyhiddenbull = hiddenBullCond[1] or hiddenBullCond[2] or hiddenBullCond[3] or hiddenBullCond[4] or hiddenBullCond[5]
    sellhiddenbear = hiddenBearCond[1] or hiddenBearCond[2] or hiddenBearCond[3] or hiddenBearCond[4] or hiddenBearCond[5]
    emalongcondition = ema1 > ema2
    closelongcondition = close > ema1 and cast_bool(ema2)
    closeshortcondition = close < ema1 and cast_bool(ema2)
    emashortcondition = ema1 < ema2
    upcondition = close[1] > ema1[1] and cast_bool(ema2[1]) and (close[2] > ema1[2]) and cast_bool(ema2[2]) and (close[3] > ema1[3]) and cast_bool(ema2[3])
    downcondition = close[2] < ema1[1] and cast_bool(ema2[1]) and (close[2] < ema1[2]) and cast_bool(ema2[2]) and (close[3] < ema1[3]) and cast_bool(ema2[3])
    crossup = k > d and k[1] <= d[1]
    crossdown = k < d and k[1] >= d[1]
    barbuy = emalongcondition and upcondition and crossup and buyhiddenbull and closelongcondition
    barsell = emashortcondition and downcondition and crossdown and sellhiddenbear and closeshortcondition
    longcondition = barbuy
    shortcondition = barsell
    if afterStartDate and enablelong == True and (strategy.opentrades < 1):
        if longcondition:
            strategy.entry('long', strategy.long)
    if afterStartDate and enableshort == True and (strategy.opentrades < 1):
        if shortcondition:
            strategy.entry('short', strategy.short)
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
    plot(profit_atr_long, title='Take Profit Long', linewidth=1, style=plot.style_linebr, color=color.new(color.green, 0))
    plot(stop_atr_long, title='Stop Loss Long', linewidth=1, style=plot.style_linebr, color=color.new(color.red, 0))
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
    plot(profit_atr_short, title='Take Profit Short', linewidth=1, style=plot.style_linebr, color=color.new(color.green, 0))
    plot(stop_atr_short, title='Stop Loss Short', linewidth=1, style=plot.style_linebr, color=color.new(color.red, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
