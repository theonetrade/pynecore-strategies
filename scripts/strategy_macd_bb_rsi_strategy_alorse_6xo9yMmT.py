"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, input, low, math, nz, script, strategy, ta
from pynecore.types import Series

txtVer: str = '1.0.1'
bbGroup: str = 'Bollindger Bands'
rsiGroup: str = 'RSI'
slGroup: str = 'Stop Loss'


@script.strategy('MACD + BB + RSI [Alorse]', shorttitle='BB + MACD + RSI [Alorse]', overlay=True, pyramiding=0, currency=currency.USD, default_qty_type=strategy.percent_of_equity, initial_capital=1000, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.01, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    version=input.string(title='Version', defval=txtVer, options=(txtVer,), tooltip='This is informational only, nothing will change.'),
    src: Series[float] = input(title='Source', defval=close),
    fast_length=input.int(title='Fast Length', defval=12, group='MACD'),
    slow_length=input.int(title='Slow Length', defval=26, group='MACD'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group='MACD'),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA'), group='MACD'),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA'), group='MACD'),
    length=input.int(20, title='Length', group=bbGroup),
    mult=input.float(2.0, title='StdDev', minval=0.001, maxval=5, group=bbGroup),
    lenRSI=input.int(14, title='Length', minval=1, group=rsiGroup),
    useSL=input.bool(False, title='╔══════   Enable   ══════╗', group=slGroup, tooltip='If you are using this strategy for Scalping or Futures market, we do not recommend using Stop Loss.'),
    SLbased=input.string(title='Based on', defval='Percent', options=('ATR', 'Percent'), group=slGroup, tooltip='ATR: Average True Range\nPercent: eg. 5%.'),
    multiATR=input.float(10.0, title='ATR   Mult', group=slGroup, inline='atr'),
    lengthATR=input.int(14, title='Length', group=slGroup, inline='atr'),
    __input_14__=input.float(10, title='Percent', group=slGroup)
):
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    basis = ta.sma(src, length)
    dev = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev
    RSI = ta.rsi(src, lenRSI)
    buy = ta.crossover(macd, signal) and RSI < 50 and (close < basis)
    sell = RSI > 70 and close > upper
    SLPercent = __input_14__ * 0.01
    longStop: Series[float] = 0.0
    shortStop: Series[float] = 0.0
    if SLbased == 'ATR':
        longStop = ta.valuewhen(buy, low, 0) - ta.valuewhen(buy, ta.rma(ta.tr(True), lengthATR), 0) * multiATR
        longStopPrev = nz(longStop[1], longStop)
        longStop = math.max(longStop, longStopPrev) if close[1] > longStopPrev else longStop
        shortStop = ta.valuewhen(sell, ta.rma(ta.tr(True), lengthATR), 0) * multiATR + ta.valuewhen(sell, high, 0)
        shortStopPrev = nz(shortStop[1], shortStop)
        shortStop = math.max(shortStop, shortStopPrev) if close[1] > shortStopPrev else shortStop
    if SLbased == 'Percent':
        longStop = strategy.position_avg_price * (1 - SLPercent)
        shortStop = strategy.position_avg_price * (1 + SLPercent)
    if buy:
        strategy.entry('Long', strategy.long)
    if sell:
        strategy.close('Long', comment='Exit')
    if useSL:
        strategy.exit('Stop Loss', 'Long', stop=longStop)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
