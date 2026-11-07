"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, close, color, currency, high, input, location, low, plot,
    plotshape, request, script, shape, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Color, Series


@script.strategy(title='MACD EMA Strategy', shorttitle='MACD EMA STRAT', overlay=True, pyramiding=0, max_bars_back=5000, calc_on_order_fills=False, commission_type=strategy.commission.percent, commission_value=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=5000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    FromMonth=input.int(defval=1, title='FromMonth', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='FromDay', minval=1, maxval=31),
    FromYear=input.int(defval=2020, title='FromYear', minval=2016),
    ToMonth=input.int(defval=1, title='ToMonth', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='ToDay', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='ToYear', minval=2017),
    res=input.timeframe(title='EMA Timeframe', defval='15'),
    len1=input(title='EMA Length', defval=206),
    fast_length=input(title='Fast Length', defval=15),
    slow_length=input(title='Slow Length', defval=24),
    src: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input(title='Simple MA (Oscillator)', defval=True),
    sma_signal=input(title='Simple MA (Signal Line)', defval=True),
    enablelong=input(True, title='Enable long?'),
    enableshort=input(True, title='Enable short?'),
    slbuffer=input.float(title='SL Buffer', step=0.1, defval=0),
    profitfactorlong=input.float(title='ProfitfactorLong', step=0.1, defval=1.9),
    loLen=input.int(title='Lowest Low Lookback', defval=46, minval=2),
    profitfactorshort=input.float(title='ProfitfactorShort', step=0.1, defval=2.1),
    highLen=input.int(title='highest high lookback', defval=25, minval=2)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    afterStartDate = True if time >= start and time <= finish else False
    emasrc = close
    col1 = color.yellow
    ema1 = ta.ema(emasrc, len1)
    emaSmooth: Series = request.security(syminfo.tickerid, res, ema1, barmerge.gaps_off, barmerge.lookahead_off)
    plot(emaSmooth, title='EMA', linewidth=1, color=color.new(col1, 0))
    zeroline: int = 0
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    fast_ma = ta.sma(src, fast_length) if sma_source else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal else ta.ema(macd, signal_length)
    hist = macd - signal
    upcondition = close > emaSmooth and close[1] > emaSmooth[1]
    macdunderhis = macd < zeroline
    macdcrossup = ta.crossover(macd, signal)
    longcondition = upcondition and macdunderhis and macdcrossup
    if longcondition and afterStartDate and (strategy.opentrades < 1) and (enablelong == True):
        strategy.entry('long', strategy.long)
    plotshape(longcondition, style=shape.arrowup, location=location.abovebar, color=color.new(color.green, 0))
    downcondition = close < emaSmooth and close[1] < emaSmooth[1]
    macdoverhis = macd > zeroline
    macdcrosunder = ta.crossunder(macd, signal)
    shortcondition = downcondition and macdoverhis and macdcrosunder
    if shortcondition and afterStartDate and (strategy.opentrades < 1) and (enableshort == True):
        strategy.entry('short', strategy.short)
    plotshape(shortcondition, style=shape.arrowdown, location=location.belowbar, color=color.new(color.red, 0))
    bought = strategy.position_size[1] < strategy.position_size
    sold = strategy.position_size[1] > strategy.position_size
    barsbought = ta.barssince(bought)
    barssold = ta.barssince(sold)
    stop_level_long: Series = inline_series(ta.lowest(low, loLen), 1)
    if strategy.position_size > 0 and strategy.position_entry_name == 'long':
        profit_level_long = strategy.position_avg_price + (strategy.position_avg_price - stop_level_long[barsbought]) * profitfactorlong + slbuffer
        strategy.exit(id='TP/ SL', stop=stop_level_long[barsbought] - slbuffer, limit=profit_level_long)
    stop_level_short: Series = inline_series(ta.highest(high, highLen), 1)
    if strategy.position_size < 0 and strategy.position_entry_name == 'short':
        profit_level_short = strategy.position_avg_price - (stop_level_short[barssold] - strategy.position_avg_price) * profitfactorshort - slbuffer
        strategy.exit(id='TP/ SL', stop=stop_level_short[barssold] + slbuffer, limit=profit_level_short)
    plot(stop_level_long - slbuffer, title='SL Long', linewidth=1, color=color.new(color.red, 0))
    plot(stop_level_short + slbuffer, title='SL Short', linewidth=1, color=color.new(color.red, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
