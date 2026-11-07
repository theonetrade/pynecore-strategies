"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    alert, alertcondition, barcolor, barmerge, close, color, fill, high,
    input, low, math, na, nz, open, plot, request, script, strategy, string, syminfo, ta, ticker,
    time, timeframe, timestamp, volume
)
from pynecore.types import NA, PersistentSeries, Series


@script.strategy('Strategy Myth-Busting #1 - UT Bot+STC+Hull+ [MYN]', max_bars_back=5000, overlay=True, pyramiding=0, initial_capital=500, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=1.0, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    a=input(2, title='Key Vaule. \'This changes the sensitivity\''),
    c=input(6, title='ATR Period'),
    h=input(False, title='Signals from Heikin Ashi Candles'),
    STCDivider=input(False, '░░░░░░░░░░░░░░░░░░░░░░░░░'),
    EEEEEE=input(80, 'Length'),
    BBBB=input(27, 'FastLength'),
    BBBBB=input(50, 'SlowLength'),
    __input_7__=input(0.5),
    HullDivider=input(False, '░░░░░░░░░░░░░░░░░░░░░░░░░'),
    srcHull: Series[float] = input(close, title='Source'),
    modeSwitch=input.string('Hma', title='Hull Variation', options=('Hma', 'Thma', 'Ehma')),
    length=input(55, title='Length(180-200 for floating S/R , 55 for swing entry)'),
    lengthMult=input(1.0, title='Length multiplier (Used to view higher timeframes with straight band)'),
    useHtf=input(False, title='Show Hull MA from X timeframe? (good for scalping)'),
    htf=input.timeframe('240', title='Higher timeframe'),
    switchColor=input(True, 'Color Hull according to trend?'),
    candleCol=input(False, title='Color candles based on Hull\'s Trend?'),
    visualSwitch=input(True, title='Show as a Band?'),
    thicknesSwitch=input(1, title='Line Thickness'),
    transpSwitch=input.int(40, title='Band Transparency', step=5),
    useStartPeriodTime=input.bool(True, 'Start', group='Date Range', inline='Start Period'),
    startPeriodTime=input.time(timestamp('1 Jan 2019'), '', group='Date Range', inline='Start Period'),
    useEndPeriodTime=input.bool(True, 'End', group='Date Range', inline='End Period'),
    endPeriodTime=input.time(timestamp('31 Dec 2030'), '', group='Date Range', inline='End Period'),
    tradeDirection=input.string('Long and Short', title='Trade Direction', options=('Long and Short', 'Long Only', 'Short Only'), group='Trade Direction'),
    tp1=input.float(title='Take Profit 1 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 1'),
    q1=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 1'),
    tp2=input.float(title='Take Profit 2 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 2'),
    q2=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 2'),
    tp3=input.float(title='Take Profit 3 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 3'),
    q3=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 3'),
    tp4=input.float(title='Take Profit 4 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit'),
    __input_32__=input.float(title='Stop Loss (%)', defval=15, minval=0.01, group='Stop Loss'),
    leverage=input.float(1, 'Leverage', step=0.5, group='Leverage'),
    alertSyntaxPrefix=input.string(defval='PV-AccountNameHere_Strategy-Name-Here', title='Alert Syntax Prefix', group='ProfitView Alert Syntax')
):
    xATR = ta.atr(c)
    nLoss = a * xATR
    src: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close, lookahead=barmerge.lookahead_off) if h else close
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = src - nLoss if src > nz(xATRTrailingStop[1], 0) else src + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), src + nLoss) if src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), src - nLoss) if src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0) else iff_2
    pos: Series[int] = 0
    iff_3 = -1 if src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0) else iff_3
    xcolor = color.red if pos == -1 else color.green if pos == 1 else color.blue
    ema = ta.ema(src, 1)
    above = ta.crossover(ema, xATRTrailingStop)
    below = ta.crossover(xATRTrailingStop, ema)
    buy = src > xATRTrailingStop and above
    sell = src < xATRTrailingStop and below
    barbuy = src > xATRTrailingStop
    barsell = src < xATRTrailingStop
    barcolor(color.green if barbuy else na)
    barcolor(color.red if barsell else na)
    alertcondition(buy, 'UT Long', 'UT Long')
    alertcondition(sell, 'UT Short', 'UT Short')
    last_longCondition: Series = NA(float)
    last_shortCondition: Series = NA(float)
    last_longCondition = time if buy else nz(last_longCondition[1])
    last_shortCondition = time if sell else nz(last_shortCondition[1])
    in_longCondition = last_longCondition > last_shortCondition
    in_shortCondition = last_shortCondition > last_longCondition
    UTBotBuyZone = in_longCondition
    UTBotSellZone = in_shortCondition
    def AAAA(BBB, BBBB, BBBBB):
        fastMA = ta.ema(BBB, BBBB)
        slowMA = ta.ema(BBB, BBBBB)
        AAAA__00000037__ = fastMA - slowMA
        return AAAA__00000037__

    def AAAAA(EEEEEE, BBBB, BBBBB):
        AAA = __input_7__
        CCCCC: PersistentSeries[float] = 0.0
        DDD: PersistentSeries[float] = 0.0
        DDDDDD: PersistentSeries[float] = 0.0
        EEEEE: PersistentSeries[float] = 0.0
        BBBBBB = AAAA(close, BBBB, BBBBB)
        CCC = ta.lowest(BBBBBB, EEEEEE)
        CCCC = ta.highest(BBBBBB, EEEEEE) - CCC
        CCCCC = (BBBBBB - CCC) / CCCC * 100 if CCCC > 0 else nz(CCCCC[1])
        DDD = CCCCC if na(DDD[1]) else DDD[1] + AAA * (CCCCC - DDD[1])
        DDDD = ta.lowest(DDD, EEEEEE)
        DDDDD = ta.highest(DDD, EEEEEE) - DDDD
        DDDDDD = (DDD - DDDD) / DDDDD * 100 if DDDDD > 0 else nz(DDDDDD[1])
        EEEEE = DDDDDD if na(EEEEE[1]) else EEEEE[1] + AAA * (DDDDDD - EEEEE[1])
        return EEEEE

    mAAAAA: Series = AAAAA(EEEEEE, BBBB, BBBBB)
    mColor = color.new(color.green, 20) if mAAAAA > mAAAAA[1] else color.new(color.red, 20)
    if mAAAAA[3] <= mAAAAA[2] and mAAAAA[2] > mAAAAA[1] and (mAAAAA > 75):
        alert('Red', alert.freq_once_per_bar)
    if mAAAAA[3] >= mAAAAA[2] and mAAAAA[2] < mAAAAA[1] and (mAAAAA < 25):
        alert('Green', alert.freq_once_per_bar)
    STCGreenAndBelow25AndRising = mAAAAA > mAAAAA[1] and mAAAAA < 25
    STCRedAndAndAbove75AndFalling = mAAAAA < mAAAAA[1] and mAAAAA > 75
    def HMA(_src, _length):
        return ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))

    def EHMA(_src, _length):
        return ta.ema(2 * ta.ema(_src, _length / 2) - ta.ema(_src, _length), math.round(math.sqrt(_length)))

    def THMA(_src, _length):
        return ta.wma(ta.wma(_src, _length / 3) * 3 - ta.wma(_src, _length / 2) - ta.wma(_src, _length), _length)

    def Mode(modeSwitch, src, len):
        return HMA(src, len) if modeSwitch == 'Hma' else EHMA(src, len) if modeSwitch == 'Ehma' else THMA(src, len / 2) if modeSwitch == 'Thma' else na

    _hull = Mode(modeSwitch, srcHull, cast_int(length * lengthMult))
    HULL: Series = request.security(syminfo.ticker, htf, _hull) if useHtf else _hull
    MHULL = HULL
    SHULL = HULL[2]
    hullColor = (color.new('#00FF00') if HULL > HULL[2] else color.new('#FF0000')) if switchColor else color.new('#FF9800')
    Fi1 = plot(MHULL, title='MHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    Fi2 = plot(SHULL if visualSwitch else na, title='SHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    alertcondition(ta.crossover(MHULL, SHULL), title='Hull trending up.', message='Hull trending up.')
    alertcondition(ta.crossover(SHULL, MHULL), title='Hull trending down.', message='Hull trending down.')
    fill(Fi1, Fi2, title='Band Filler', color=hullColor)
    barcolor(color=(hullColor if switchColor else na) if candleCol else na)
    HullGreen = hullColor == color.new('#00FF00')
    HullRed = hullColor == color.new('#FF0000')
    longCondition = STCGreenAndBelow25AndRising and HullGreen and UTBotBuyZone
    shortCondition = STCRedAndAndAbove75AndFalling and HullRed and UTBotSellZone
    closeLongCondition: int = 0
    closeShortCondition: int = 0
    start = startPeriodTime >= time if useStartPeriodTime else False
    end = endPeriodTime <= time if useEndPeriodTime else False
    calcPeriod = not start and (not end)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    stoplossPercent = __input_32__ * 0.01
    slLongClose = close < strategy.position_avg_price * (1 - stoplossPercent)
    slShortClose = close > strategy.position_avg_price * (1 + stoplossPercent)
    contracts = math.min(math.max(1e-06, strategy.equity / close * leverage), 1000000000)
    isInLongPosition = strategy.position_size > 0
    isInShortPosition = strategy.position_size < 0
    alertSyntaxBase = alertSyntaxPrefix + '\n#' + string.tostring(open) + ',' + string.tostring(high) + ',' + string.tostring(low) + ',' + string.tostring(close) + ',' + string.tostring(volume) + ','
    if calcPeriod:
        if longCondition and tradeDirection != 'Short Only' and (isInLongPosition == False):
            strategy.entry('Long', strategy.long, qty=contracts)
            alert(message=alertSyntaxBase + 'side:long', freq=alert.freq_once_per_bar_close)
        if shortCondition and tradeDirection != 'Long Only' and (isInShortPosition == False):
            strategy.entry('Short', strategy.short, qty=contracts)
            alert(message=alertSyntaxBase + 'side:short', freq=alert.freq_once_per_bar_close)
        strategy.exit('TP1', qty_percent=q1, profit=per(tp1))
        strategy.exit('TP2', qty_percent=q2, profit=per(tp2))
        strategy.exit('TP3', qty_percent=q3, profit=per(tp3))
        strategy.exit('TP4', profit=per(tp4))
        if slLongClose:
            strategy.close('Long', qty_percent=100, comment='SL Long')
        if slShortClose:
            strategy.close('Short', qty_percent=100, comment='SL Short')
        if cast_bool(closeLongCondition) or cast_bool(closeShortCondition):
            strategy.close_all(comment='Close Postion')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
