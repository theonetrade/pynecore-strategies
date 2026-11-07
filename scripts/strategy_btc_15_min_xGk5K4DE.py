"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, fill, fixnan, high, input, low, math, na, nz, open, plot,
    request, script, strategy, syminfo, ta, time, timeframe, volume
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@script.strategy(title=' BTC 15 min', overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=20, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='all', options=('long', 'short', 'all')),
    length8=input(30, title='length of channel'),
    upmult=input.float(title='upper percent', step=0.1, defval=5),
    lowmult=input.float(title='lower percent', step=0.1, defval=5),
    fastLength=input.int(3, title='Fast filter length ', minval=1),
    slowLength=input.int(21, title='Slow filter length', minval=1),
    HTF=input.timeframe('1D'),
    tf10=input.timeframe('1', title='Timeframe', options=('1', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W')),
    length=input(50, title='Period'),
    shift=input(1, title='Shift'),
    len=input(25),
    Min=input(15),
    tp=input.float(2, 'Exit Profit %'),
    isSLl=input(True, 'buy Loss Long'),
    sl=input.float(5, ' rebuy %'),
    filter=input(True),
    risk__global__=input(100),
    leverage=input(1),
    stoploss=input.float(title=' stop loss', defval=5, minval=0.01),
    q1=input.int(title=' qty_percent1', defval=50, minval=1),
    q2=input.int(title=' qty_percent2', defval=50, minval=1),
    tp10=input.float(title=' Take profit1', defval=1, minval=0.01),
    tp20=input.float(title=' Take profit2', defval=2, minval=0.01)
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    price = close
    basis = ta.sma(close, length8)
    vup = upmult * price / 100
    vlow = lowmult * price / 100
    upper = basis + vup
    lower = basis - vlow
    plot(basis, color=color.new(color.red, 0))
    source = close
    v1 = ta.ema(source, fastLength)
    v2 = ta.ema(source, slowLength)
    leng: int = 1
    p1 = close[1]
    len55: int = 10
    ti = ta.change(time(HTF)) != 0
    T_c = fixnan(close if ti else na)
    vrsi: Series = ta.rsi(ta.cum(ta.change(T_c) * volume), leng)
    pp: Series = ta.wma(vrsi, len55)
    d = vrsi[1] - pp[1]
    len100: int = 10
    x = ta.ema(d, len100)
    zx = x / -1
    col = color.lime if zx > 0 else color.orange
    def hma(_src, _length):
        return ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))

    def hma3(_src, _length):
        p = length / 2
        return ta.wma(ta.wma(close, p / 3) * 3 - ta.wma(close, p / 2) - ta.wma(close, p), p)

    b = request.security(syminfo.tickerid, tf10, inline_series(hma3(close[1], length), shift))
    close_price = close
    linear_reg = ta.linreg(close_price, len, 0)
    buy = ta.crossover(linear_reg, b)
    crossunder_1 = ta.crossunder(close[1], upper)
    sell = ta.crossunder(linear_reg, b) or crossunder_1
    src2 = low
    src3 = high
    leni = Min / timeframe.multiplier * 7 if timeframe.isintraday and timeframe.multiplier >= 1 else 60 / timeframe.multiplier * 24 * 7 if timeframe.isintraday and timeframe.multiplier < 60 else 7
    l1 = ta.wma(src2, leni)
    h1 = ta.wma(src3, leni)
    m = (h1 + l1) / 2
    len5: int = 100
    src5 = m
    multi: int = 2
    mean = ta.ema(src5, len5)
    stddev = multi * ta.stdev(src5, len5)
    b5 = mean + stddev
    s5 = mean - stddev
    long: Persistent[bool] = na(bool)
    short: Persistent[bool] = na(bool)
    long = ta.crossover(src5, s5)
    short = ta.crossunder(src5, b5)
    last_open_long: PersistentSeries[float] = na(float)
    last_open_short: PersistentSeries[float] = na(float)
    last_open_long = close if long else nz(last_open_long[1])
    last_open_short = close if short else nz(last_open_short[1])
    entry_value = last_open_long
    entry_value1 = last_open_short
    r: int = 100
    highb = ta.highest(entry_value1, r)
    lowb = ta.lowest(entry_value, r)
    d5 = highb - lowb
    me = (highb + lowb) / 2
    h4 = highb - d5 * 0.236
    c3 = highb - d5 * 0.382
    c4 = highb - d5 * 0.618
    l4 = highb - d5 * 0.764
    col2 = color.lime if close >= me else color.red
    p5 = plot(upper, color=col2)
    p2 = plot(lower, color=col2)
    fill(p5, p2, color=col2)
    longCond = NA(bool)
    shortCond = NA(bool)
    longCond = ta.crossover(zx, 0) or buy
    shortCond = sell
    sectionLongs: Series[int] = 0
    sectionLongs = nz(sectionLongs[1])
    sectionShorts: Series[int] = 0
    sectionShorts = nz(sectionShorts[1])
    if longCond:
        sectionLongs = sectionLongs + 1
        sectionShorts = 0
    if shortCond:
        sectionLongs = 0
        sectionShorts = sectionShorts + 1
    pyrl: int = 1
    longCondition = longCond and sectionLongs <= pyrl
    shortCondition = shortCond and sectionShorts <= pyrl
    last_open_longCondition: Series = NA(float)
    last_open_shortCondition: Series = NA(float)
    last_open_longCondition = open if longCondition else nz(last_open_longCondition[1])
    last_open_shortCondition = open if shortCondition else nz(last_open_shortCondition[1])
    last_longCondition: Series = NA(float)
    last_shortCondition: Series = NA(float)
    last_longCondition = time if longCondition else nz(last_longCondition[1])
    last_shortCondition = time if shortCondition else nz(last_shortCondition[1])
    in_longCondition = last_longCondition > last_shortCondition
    in_shortCondition = last_shortCondition > last_longCondition
    isTPl: bool = True
    crossover_1 = ta.crossover(high, (1 + tp / 100) * last_open_longCondition)
    long_tp = isTPl and crossover_1 and (longCondition == cast_bool(0)) and (in_longCondition == cast_bool(1))
    sl: float = 0.0
    sl = input.float(5, ' rebuy %')
    crossunder_2 = ta.crossunder(low, (1 - sl / 100) * last_open_longCondition)
    long_sl = isSLl and crossunder_2 and (longCondition == cast_bool(0)) and (in_longCondition == cast_bool(1))
    longCond5 = NA(bool)
    shortCond5 = NA(bool)
    longCond5 = longCondition
    shortCond5 = long_tp
    sectionLongs5: Series[int] = 0
    sectionLongs5 = nz(sectionLongs5[1])
    sectionShorts5: Series[int] = 0
    sectionShorts5 = nz(sectionShorts5[1])
    if longCond5:
        sectionLongs5 = sectionLongs5 + 1
        sectionShorts5 = 0
    if shortCond5:
        sectionLongs5 = 0
        sectionShorts5 = sectionShorts5 + 1
    pyr5: int = 1
    longCondition5 = longCond5 and sectionLongs5 <= pyr5
    shortCondition5 = shortCond5 and sectionShorts5 <= pyr5
    last_open_longCondition5: Series = NA(float)
    last_open_shortCondition5: Series = NA(float)
    last_open_longCondition5 = open if longCondition5 else nz(last_open_longCondition5[1])
    last_open_shortCondition5 = open if shortCondition5 else nz(last_open_shortCondition5[1])
    last_longCondition5: Series = NA(float)
    last_shortCondition5: Series = NA(float)
    last_longCondition5 = time if longCondition5 else nz(last_longCondition5[1])
    last_shortCondition5 = time if shortCondition5 else nz(last_shortCondition5[1])
    in_longCondition5 = last_longCondition5 > last_shortCondition5
    in_shortCondition5 = last_shortCondition5 > last_longCondition5
    def g(v, p):
        return math.round(v * math.pow(10, p)) / math.pow(10, p)

    c = g(strategy.equity * leverage / open * (risk__global__ / 100), 4)
    l = (v1 > v2 or filter == False) and longCondition or long_sl
    s = shortCondition5
    if l:
        strategy.entry('buy', strategy.long, c)
    if s:
        strategy.entry('sell', strategy.short, c)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    los = per(stoploss)
    strategy.exit('x1', qty_percent=q1, profit=per(tp10), loss=los)
    strategy.exit('x2', qty_percent=q2, profit=per(tp20), loss=los)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
