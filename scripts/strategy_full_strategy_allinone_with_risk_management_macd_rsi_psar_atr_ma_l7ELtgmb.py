"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, high, input, low, math, na, script, strategy,
    string, ta, time, timeframe, timestamp
)
from pynecore.types import Color, Persistent, Series


@script.strategy('EURUSD 1min strat RISK %% ', overlay=False, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=6, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2020, title='From Year', minval=1970),
    toDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=12, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2020, title='To Year', minval=1970),
    length=input(5),
    overSold=input(23),
    overBought=input(72),
    fast_length_macd=input(title='Fast Length', defval=12),
    slow_length_macd=input(title='Slow Length', defval=26),
    src_macd: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input(title='Simple MA(Oscillator)', defval=True),
    sma_signal=input(title='Simple MA(Signal Line)', defval=True),
    start=input(0.02),
    increment=input(0.02),
    maximum=input(0.2),
    length_bb=input.int(17, minval=1),
    src_bb: Series[float] = input(close, title='Source'),
    mult_bb=input.float(2.0, minval=0.001, maxval=50, title='StdDev'),
    offset=input.int(0, 'Offset', minval=-500, maxval=500),
    len_ema=input.int(10, minval=1, title='Length'),
    src_ema: Series[float] = input(close, title='Source'),
    offset_ema=input.int(title='Offset', defval=0, minval=-500, maxval=500),
    atr_period=input(14, 'Average True Range Period'),
    __input_26__=input.float(2, title='Risk %'),
    isTwoDigit=input(False, 'Is this a 2 digit pair? (JPY, XAU, XPD...'),
    __input_28__=input.float(1, title='Equity Protection %'),
    __input_29__=input.float(2, title='Equity TP %'),
    multtp=input.float(5, title='multi atr tp'),
    multsl=input.float(5, title='multi atr sl'),
    __input_32__=input(1, 'SL X'),
    __input_33__=input(1, 'TP X')
):
    DST: int = 1
    London = '0000-0900' if DST == 0 else '0100-1000'
    NewYork = '0400-1500' if DST == 0 else '0500-1600'
    Sydney = '1300-2200' if DST == 0 else '1400-2300'
    Tokyo = '1500-2400' if DST == 0 else '1600-0100'
    def timeinrange(res, sess):
        return time(res, sess if sess == '' else sess + ('23456' if string.endswith(sess, ':') else '' if string.contains(sess, ':') else ':23456')) != 0

    london = timeinrange(timeframe.period, London)
    newyork = timeinrange(timeframe.period, NewYork)
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate and (london or newyork)
    price = close
    vrsi = ta.rsi(price, length)
    co = ta.crossover(vrsi, overSold)
    cu = ta.crossunder(vrsi, overBought)
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    fast_ma = ta.sma(src_macd, fast_length_macd) if sma_source else ta.ema(src_macd, fast_length_macd)
    slow_ma = ta.sma(src_macd, slow_length_macd) if sma_source else ta.ema(src_macd, slow_length_macd)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal else ta.ema(macd, signal_length)
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
    basis_bb = ta.sma(src_bb, length_bb)
    dev_bb = mult_bb * ta.stdev(src_bb, length_bb)
    upper_bb = basis_bb + dev_bb
    lower_bb = basis_bb - dev_bb
    out_ema = ta.ema(src_ema, len_ema)
    ema_1 = ta.ema(src_ema, len_ema)
    sma_1 = ta.sma(src_bb, length_bb)
    crossunder_1 = ta.crossunder(ema_1, sma_1)
    shortCondition = uptrend == False and crossunder_1 and (hist < 0) and (vrsi < overSold)
    ema_2 = ta.ema(src_ema, len_ema)
    sma_2 = ta.sma(src_bb, length_bb)
    crossover_1 = ta.crossover(ema_2, sma_2)
    longCondition = uptrend == True and crossover_1 and (hist > 0) and (vrsi > overBought)
    atr = ta.atr(atr_period)
    balance = strategy.netprofit + strategy.initial_capital
    floating = strategy.openprofit
    risk = __input_26__ / 100
    equity_protector = __input_28__ / 100
    equity_protectorTP = __input_29__ / 100
    stop = atr * 100000 * __input_32__ * multsl
    if isTwoDigit:
        stop = stop / 100
    target = atr * 100000 * __input_33__ * multtp
    equity_stopout: bool = False
    if floating < 0 and math.abs(floating / balance) > equity_protector:
        equity_stopout = True
    equity_stopout2: bool = False
    if floating > 0 and math.abs(floating / balance) > equity_protectorTP:
        equity_stopout2 = True
    temp01 = balance * risk
    temp02 = temp01 / stop
    temp03 = temp02 * 100000
    size__ren__ = temp03 - temp03 % 1000
    if size__ren__ < 10000:
        size__ren__ = 10000
    if equity_stopout:
        strategy.close_all(comment='equity sl', alert_message='equity_sl')
    is_open = strategy.opentrades > 0
    if longCondition and (not is_open):
        strategy.entry('long', strategy.long, size__ren__, oca_name='a', oca_type=strategy.oca.cancel)
    if shortCondition and (not is_open):
        strategy.entry('short', strategy.short, size__ren__, oca_name='a', oca_type=strategy.oca.cancel)
    strategy.exit('exit_long', 'long', loss=stop, profit=target)
    if shortCondition:
        strategy.close('long')
    strategy.exit('exit_short', 'short', loss=stop, profit=target)
    if longCondition:
        strategy.close('short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
