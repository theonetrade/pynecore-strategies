"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, high, input, low, na, nz, plotchar, script, strategy, syminfo, ta,
    time, timestamp
)
from pynecore.types import Series


@script.strategy('Built-in Kelly ratio for position sizing', overlay=True, initial_capital=10000, default_qty_type=strategy.cash, default_qty_value=10000, currency='USD', commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    useKelly=input(True, 'Kelly Ratio Position Sizing'),
    i_startTime=input.time(defval=timestamp('01 Mar 1900 00:00 +0000'), title='Start Time'),
    i_endTime=input.time(defval=timestamp('01 Mar 2221 00:00 +0000'), title='End Time'),
    length=input.int(20, minval=1),
    mult=input(1.0, 'Multiplier'),
    src: Series[float] = input(close, title='Source'),
    exp=input(True, 'Use Exponential MA'),
    BandsStyle=input.string('Average True Range', options=('Average True Range', 'True Range', 'Range'), title='Bands Style'),
    atrlength=input(10, 'ATR Length'),
    usetp=input(False, 'use Take Profit'),
    usesl=input(False, 'use Stop Loss'),
    __input_11__=input(10.0, 'take profit'),
    __input_12__=input(1.0, 'stop loss')
):
    c = close
    krp = strategy.wintrades / strategy.closedtrades
    krw = strategy.grossprofit / strategy.wintrades
    krl = strategy.grossloss / strategy.losstrades
    kr = (krp - (1 - krp) / (krw / krl)) * 100 / 100
    qty: float = 10000.0
    if useKelly:
        qty = 10000.0 / c
        if kr > 0:
            qty = strategy.equity * kr / c
    inDateRange = time >= i_startTime and time <= i_endTime
    def esma(source, length):
        s = ta.sma(source, length)
        e = ta.ema(source, length)
        return e if exp else s

    ma = esma(src, length)
    rangema = ta.rma(ta.tr(True), length) if BandsStyle == 'True Range' else ta.atr(atrlength) if BandsStyle == 'Average True Range' else ta.rma(high - low, length)
    upper = ma + rangema * mult
    lower = ma - rangema * mult
    crossUpper = ta.crossover(src, upper)
    crossLower = ta.crossunder(src, lower)
    bprice: Series[float] = 0.0
    bprice = high + syminfo.mintick if crossUpper else nz(bprice[1])
    sprice: Series[float] = 0.0
    sprice = low - syminfo.mintick if crossLower else nz(sprice[1])
    crossBcond: Series[bool] = False
    crossBcond = True if crossUpper else False if na(crossBcond[1]) else crossBcond[1]
    crossScond: Series[bool] = False
    crossScond = True if crossLower else False if na(crossScond[1]) else crossScond[1]
    cancelBcond = crossBcond and (src < ma or high >= bprice)
    cancelScond = crossScond and (src > ma or low <= sprice)
    if inDateRange:
        if useKelly:
            if cancelBcond:
                strategy.cancel('Long')
            if crossUpper:
                strategy.entry('Long', strategy.long, qty, stop=bprice, comment='Long')
            if cancelScond:
                strategy.cancel('Short')
            if crossLower:
                strategy.entry('Short', strategy.short, qty, stop=sprice, comment='Short')
        else:
            if cancelBcond:
                strategy.cancel('Long')
            if crossUpper:
                strategy.entry('Long', strategy.long, stop=bprice, comment='Long')
            if cancelScond:
                strategy.cancel('Short')
            if crossLower:
                strategy.entry('Short', strategy.short, stop=sprice, comment='Short')
    tp = __input_11__ / 100
    sl = __input_12__ / 100
    avg = strategy.position_avg_price
    longprofit = avg * tp / syminfo.mintick
    longloss = avg * sl / syminfo.mintick
    shortprofit = avg * tp / syminfo.mintick
    shortloss = avg * sl / syminfo.mintick
    if usetp and (not usesl):
        strategy.exit('Long Exit', 'Long', profit=longprofit)
        strategy.exit('Short Exit', 'Short', profit=shortprofit)
    if usesl and (not usetp):
        strategy.exit('Long Exit', 'Long', loss=longloss)
        strategy.exit('Short Exit', 'Short', loss=shortloss)
    if usetp and usesl:
        strategy.exit('Long Exit', 'Long', profit=longprofit, loss=longloss)
        strategy.exit('Short Exit', 'Short', profit=shortprofit, loss=shortloss)
    plotchar(krp * 100, '% profitable', '')
    plotchar(krw, 'avg win', '')
    plotchar(krl, 'avg loss', '')
    plotchar(strategy.equity, 'Equity', '')
    plotchar(qty * c, 'Quantity', '')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
