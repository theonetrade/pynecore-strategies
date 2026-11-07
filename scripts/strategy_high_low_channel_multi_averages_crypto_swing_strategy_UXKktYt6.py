"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, plot, script, strategy, syminfo, ta,
    time, timestamp
)


@script.strategy(title='High/Low channel swing', shorttitle='Multi MA swing', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2000, title='From Year', minval=1970),
    toDay=input.int(defval=31, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=12, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2021, title='To Year', minval=1970),
    length_ma=input.int(defval=12, title='Length Moving averages', minval=1),
    tplong=input.float(0.06, title='TP Long', step=0.01),
    sllong=input.float(0.05, title='SL Long', step=0.01),
    tpshort=input.float(0.045, title='TP Short', step=0.01),
    slshort=input.float(0.05, title='SL Short', step=0.01)
):
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate
    sma_high = ta.sma(high, length_ma)
    ema_high = ta.ema(high, length_ma)
    wma_high = ta.wma(high, length_ma)
    alma_high = ta.alma(high, length_ma, 0.85, 6)
    smma_high = ta.rma(high, length_ma)
    lsma_high = ta.linreg(high, length_ma, 0)
    vwma_high = ta.vwma(high, length_ma)
    avg_high = (sma_high + ema_high + wma_high + alma_high + smma_high + lsma_high + vwma_high) / 7
    sma_low = ta.sma(low, length_ma)
    ema_low = ta.ema(low, length_ma)
    wma_low = ta.wma(low, length_ma)
    alma_low = ta.alma(low, length_ma, 0.85, 6)
    smma_low = ta.rma(low, length_ma)
    lsma_low = ta.linreg(low, length_ma, 0)
    vwma_low = ta.vwma(low, length_ma)
    avg_low = (sma_low + ema_low + wma_low + alma_low + smma_low + lsma_low + vwma_low) / 7
    plot(avg_high, title='avg', color=color.new(color.green, 0), linewidth=4)
    plot(avg_low, title='avg', color=color.new(color.red, 0), linewidth=4)
    long = close > avg_high
    short = close < avg_low
    if time_cond:
        if long:
            strategy.entry('long', strategy.long)
        strategy.exit('closelong', 'long', profit=close * tplong / syminfo.mintick, loss=close * sllong / syminfo.mintick, alert_message='closelong')
        if ta.crossunder(low, avg_low):
            strategy.close('long')
        if short:
            strategy.entry('short', strategy.short)
        strategy.exit('closeshort', 'short', profit=close * tpshort / syminfo.mintick, loss=close * slshort / syminfo.mintick, alert_message='closeshort')
        if ta.crossover(high, avg_high):
            strategy.close('short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
