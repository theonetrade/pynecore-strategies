"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    adjustment, close, color, currency, high, input, low, math, plot,
    request, script, session, strategy, ta, ticker, timeframe
)
from pynecore.types import Series

initialBalance: int = 100000


@script.strategy('Crypto momentum strategy', overlay=False, pyramiding=0, default_qty_value=100, default_qty_type=strategy.percent_of_equity, precision=7, currency=currency.AUD, commission_value=0.1, commission_type=strategy.commission.percent, initial_capital=initialBalance, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    length=input(20, title='BB Length'),
    mult=input(2.0, title='BB MultFactor'),
    lengthKC=input(20, title='KC Length'),
    multKC=input(1.5, title='KC MultFactor'),
    emaPeriods=input(50, title='EMA periods'),
    useTrueRange=input(True, title='Use TrueRange (KC)'),
    considerMarket=input(True, title='Consider crypto market behavior')
):
    marketTicker = ticker.new('CRYPTOCAP', 'TOTAL', session.regular, adjustment.splits)
    market = request.security(marketTicker, timeframe.period, close, True)
    marketEma: Series = ta.ema(market, emaPeriods)
    marketEmaSlope = marketEma - marketEma[1]
    source = close
    basis = ta.sma(source, length)
    ema: Series = ta.ema(source, emaPeriods)
    dev = multKC * ta.stdev(source, length)
    upperBB = basis + dev
    lowerBB = basis - dev
    ma = ta.sma(source, lengthKC)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.sma(range_1, lengthKC)
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC
    sqzOn = lowerBB > lowerKC and upperBB < upperKC
    sqzOff = lowerBB < lowerKC and upperBB > upperKC
    noSqz = sqzOn == False and sqzOff == False
    val: Series = ta.linreg(source - math.avg(math.avg(ta.highest(high, lengthKC), ta.lowest(low, lengthKC)), ta.sma(close, lengthKC)), lengthKC, 0)
    slope = val - val[2]
    emaSlope = ema - ema[1]
    bcolor = color.lime if slope > 0 else color.red
    scolor = color.green if noSqz else color.black if sqzOn else color.green
    squeeze = 0 if noSqz else 1 if sqzOn else 0
    plot(val, color=color.new(color.gray, 0), style=plot.style_line, linewidth=1, title='momentum')
    plot(slope, color=bcolor, style=plot.style_circles, linewidth=2, title='slope')
    plot(0, color=scolor, style=plot.style_line, linewidth=2, title='squeeze-zero')
    co = ta.crossover(slope / math.abs(slope), 0)
    cu = ta.crossunder(slope / math.abs(slope), 0)
    if co and source > ema and (emaSlope > 0) and (not considerMarket or (market > marketEma and marketEmaSlope > 0)):
        strategy.entry('long', strategy.long, comment='long')
    if cu:
        strategy.close('long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
