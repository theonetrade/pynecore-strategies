"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, high, input, low, math, na, script, strategy, syminfo, ta
from pynecore.types import Persistent, Series


@script.strategy(title='Crypto Scalper', overlay=True, pyramiding=1, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.03, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    len=input.int(60, minval=1, title='Length EMA'),
    src: Series[float] = input(close, title='Source'),
    fast_length=input(title='Fast Length MACD', defval=12),
    slow_length=input(title='Slow Length MACD', defval=26),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input.string(title='Oscillator MA Type MACD', defval='EMA', options=('SMA', 'EMA')),
    sma_signal=input.string(title='Signal Line MA Type MACD', defval='EMA', options=('SMA', 'EMA')),
    start=input(0.02),
    increment=input(0.02),
    maximum=input(0.2),
    tplong=input.float(0.245, step=0.005),
    sllong=input.float(1.0, step=0.005),
    tpshort=input.float(0.055, step=0.005),
    slshort=input.float(0.03, step=0.005)
):
    out = ta.ema(src, len)
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    hist = macd - signal
    uptrend: Persistent[bool] = na(bool)
    EP: Persistent[float] = na(float)
    SAR: Persistent[float] = na(float)
    AF: Persistent[float] = start
    nextBarSAR: Persistent[float] = na(float)
    if bar_index > 0:
        firstTrendBar: bool = False
        SAR = nextBarSAR
        if bar_index == 1:
            prevSAR: float = na(float)
            prevEP: float = na(float)
            lowPrev = low[1]
            highPrev = high[1]
            closeCur = close
            closePrev = close[1]
            if closeCur > closePrev:
                uptrend = True
                EP = high
                prevSAR = lowPrev
                prevEP = high
            else:
                uptrend = False
                EP = low
                prevSAR = highPrev
                prevEP = low
            firstTrendBar = True
            SAR = prevSAR + start * (prevEP - prevSAR)
        if uptrend:
            if SAR > low:
                firstTrendBar = True
                uptrend = False
                SAR = math.max(EP, high)
                EP = low
                AF = start
        else:
            if SAR < high:
                firstTrendBar = True
                uptrend = True
                SAR = math.min(EP, low)
                EP = high
                AF = start
        if not firstTrendBar:
            if uptrend:
                if high > EP:
                    EP = high
                    AF = math.min(AF + increment, maximum)
            else:
                if low < EP:
                    EP = low
                    AF = math.min(AF + increment, maximum)
        if uptrend:
            SAR = math.min(SAR, low[1])
            if bar_index > 1:
                SAR = math.min(SAR, low[2])
        else:
            SAR = math.max(SAR, high[1])
            if bar_index > 1:
                SAR = math.max(SAR, high[2])
        nextBarSAR = SAR + AF * (EP - SAR)
    if uptrend and hist > 0 and (close < out):
        strategy.entry('short', strategy.short, stop=nextBarSAR, comment='short')
        strategy.exit('short_tp/sl', 'short', profit=close * tpshort / syminfo.mintick, loss=close * slshort / syminfo.mintick, comment='SHORT EXIT', alert_message='closeshort')
    if not uptrend and hist < 0 and (close > out):
        strategy.entry('long', strategy.long, stop=nextBarSAR, comment='long')
        strategy.exit('short_tp/sl', 'long', profit=close * tplong / syminfo.mintick, loss=close * sllong / syminfo.mintick, comment='LONG EXIT', alert_message='closelong')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
