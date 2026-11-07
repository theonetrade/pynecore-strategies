"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, location, math, na, plot, plotshape, script, shape,
    size, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('B-Xtrender [Backtest Edition] @QuantTherapy', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    i_fromMonth=input.int(defval=1, title='[Backtest] From Month', minval=1, maxval=12),
    i_fromDay=input.int(defval=1, title='[Backtest] From Day', minval=1, maxval=31),
    i_fromYear=input.int(defval=2010, title='[Backtest] From Year', minval=1970),
    i_thruMonth=input.int(defval=1, title='[Backtest] Thru Month', minval=1, maxval=12),
    i_thruDay=input.int(defval=1, title='[Backtest] Thru Day', minval=1, maxval=31),
    i_thruYear=input.int(defval=2345, title='[Backtest] Thru Year', minval=1970),
    i_tradeDirection=input(title='[Backtest] Trade Direction', defval=strategy.direction.all, options=(strategy.direction.all, strategy.direction.long, strategy.direction.short)),
    i_short_l1=input(5, title='[Short] L1'),
    i_short_l2=input(20, title='[Short] L2'),
    i_short_l3=input(15, title='[Short] L3'),
    i_long_l1=input(20, title='[Long] L1'),
    i_long_l2=input(15, title='[Long] L2'),
    i_ma_use=input(True, title='[MA Filter] Yes/No'),
    i_ma_len=input(200, title='[MA Filter] length'),
    i_ma_type=input.string('EMA', title='[MA Filter] type', options=('SMA', 'EMA')),
    i_perc=input.float(defval=20.0, title='[TSL-%] Percent', minval=0.1)
):
    def f_isDate():
        start = timestamp(i_fromYear, i_fromMonth, i_fromDay, 0, 0)
        finish = timestamp(i_thruYear, i_thruMonth, i_thruDay, 23, 59)
        isDate = time >= start and time <= finish
        return isDate

    strategy.risk.allow_entry_in(i_tradeDirection)
    shortTermXtrender: Series = ta.rsi(ta.ema(close, i_short_l1) - ta.ema(close, i_short_l2), i_short_l3) - 50
    longTermXtrender: Series = ta.rsi(ta.ema(close, i_long_l1), i_long_l2) - 50
    shortXtrenderCol = (color.lime if shortTermXtrender > shortTermXtrender[1] else color.new('#228B22')) if shortTermXtrender > 0 else color.red if shortTermXtrender > shortTermXtrender[1] else color.new('#8B0000')
    plot(shortTermXtrender, color=shortXtrenderCol, style=plot.style_columns, linewidth=1, title='B-Xtrender Osc. - Histogram')
    longXtrenderCol = (color.lime if longTermXtrender > longTermXtrender[1] else color.new('#228B22')) if longTermXtrender > 0 else color.red if longTermXtrender > longTermXtrender[1] else color.new('#8B0000')
    macollongXtrenderCol = color.lime if longTermXtrender > longTermXtrender[1] else color.red
    plot(longTermXtrender, color=longXtrenderCol, style=plot.style_columns, linewidth=2, title='B-Xtrender Trend - Histogram')
    plot(longTermXtrender, color=color.new(color.new('#000000'), 100), style=plot.style_line, linewidth=5, title='B-Xtrender Trend - Line')
    plot(longTermXtrender, color=macollongXtrenderCol, style=plot.style_line, linewidth=3, title='B-Xtrender Trend - Line')
    ma = ta.ema(close, i_ma_len) if i_ma_type == 'EMA' else ta.sma(close, i_ma_len)
    maFilterLong: bool = True
    maFilterShort: bool = True
    if i_ma_use:
        maFilterLong = True if close > ma else False
        maFilterShort = True if close < ma else False
    long: Series = shortTermXtrender > 0 and longTermXtrender > 0 and maFilterLong
    closeLong: Series = shortTermXtrender < 0 or longTermXtrender < 0
    short: Series = shortTermXtrender < 0 and longTermXtrender < 0 and maFilterShort
    closeShort: Series = shortTermXtrender > 0 or longTermXtrender > 0
    plotshape(0 if long[1] == True and long[2] == False else na, location=location.absolute, style=shape.labelup, color=color.new(color.lime, 10), size=size.small)
    plotshape(0 if short[1] == True and short[2] == False else na, location=location.absolute, style=shape.labeldown, color=color.new(color.red, 10), size=size.small)
    plotshape(0 if closeLong[1] == True and closeLong[2] == False or (closeShort[1] == True and closeShort[2] == False) else na, location=location.absolute, style=shape.circle, color=color.new(color.orange, 0), size=size.small)
    i_src = close
    sl_val = i_src * i_perc / 100
    f_isDate_1 = f_isDate()
    toLong = long and f_isDate_1
    f_isDate_2 = f_isDate()
    toShort = short and f_isDate_2
    if not f_isDate() and strategy.position_size != 0:
        strategy.close_all()
    if toLong:
        strategy.entry('Long', strategy.long)
    if closeLong:
        strategy.close('Long')
    if toShort:
        strategy.entry('Short', strategy.short)
    if closeShort:
        strategy.close('Short')
    longStopPrice: Series[float] = 0.0
    shortStopPrice: Series[float] = 0.0
    __block_result__ = na
    if strategy.position_size > 0:
        stopValue = close - sl_val
        __block_result__ = math.max(stopValue, longStopPrice[1])
    else:
        __block_result__ = 0
    longStopPrice = __block_result__
    __block_result_1__ = na
    if strategy.position_size < 0:
        stopValue = close + sl_val
        __block_result_1__ = math.min(stopValue, shortStopPrice[1])
    else:
        __block_result_1__ = syminfo.mintick * 1000000
    shortStopPrice = __block_result_1__
    if strategy.position_size > 0:
        strategy.exit(id='TSL Long', stop=longStopPrice)
    if strategy.position_size < 0:
        strategy.exit(id='TSL Short', stop=shortStopPrice)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
