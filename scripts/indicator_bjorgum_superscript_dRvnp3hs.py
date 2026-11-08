"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, array, barcolor, close, color, display, fill,
    high, hl2, input, location, low, math, na, nz, open, plot, plotbar, plotcandle, plotshape,
    script, shape, string, ta, table, timeframe
)
from pynecore.types import Color, NA, Persistent, Series


@script.indicator('Bjorgum SuperScript', 'Bj SuperScript', True, precision=3)
def main(
    strat=input.string('Bj Reversal', 'Select a Strategy', group='Strategy Selector', options=('Bj Reversal', 'MA', 'TRM', 'RSI Color')),
    source: Series[float] = input.source(close, 'MA source', group='Strategy Selector'),
    alphaInput=input.float(0.7, 'T3 Alpha', group='Strategy Selector'),
    t3vis=input.bool(False, 'Show Tilson MA\'s', group='Strategy Overides'),
    hemavis=input.bool(False, 'Show HEMA MA\'s', group='Strategy Overides'),
    psarvis=input.bool(False, 'Show PSAR', group='Strategy Overides'),
    arrowvis=input.bool(False, 'Show Arrows', group='Strategy Overides'),
    showTable=input.bool(False, 'Show Bjorgum Buy Rating', group='Strategy Overides'),
    disable=input.bool(False, 'Disable Current MA', group='Strategy Overides'),
    tsistrat=input.string('Fast', 'TRM Speed Control', group='Select a Speed', options=('Fast', 'Slow')),
    rsistrat=input.string('Slow', 'RSI Bar Color Speed Control', group='Select a Speed', options=('Slow', 'Fast')),
    type=input.string('Hollow', 'Candle Type', group='Heikin-Ashi Overlay', options=('Hollow', 'Bars', 'Candles')),
    haover=input.bool(False, 'Overlays HA Plotcandle', group='Heikin-Ashi Overlay', tooltip='(Must \'mute\' main candle series while in use. Toggle \'👁\' symbol next to ticker name to hide candles)'),
    rPrice=input.bool(False, 'Actual Close Value', group='Heikin-Ashi Overlay', tooltip='Displays real close value - useful when using HA overlay'),
    i_alert_mode=input.string(alert.freq_once_per_bar_close, 'Alerts Mode', group='Variable Alerts', options=(alert.freq_once_per_bar, alert.freq_once_per_bar_close), tooltip='Using the alert() function call will allow use of only one alert for any of the following selected. Any current settings in the script will be what is saved at the time the alert is set'),
    BUY4=input.bool(False, 'TRM Buy', group='Variable Alerts'),
    SELL4=input.bool(False, 'TRM Sell', group='Variable Alerts'),
    REVUP=input.bool(False, 'Reversal Up', group='Variable Alerts'),
    REVDWN=input.bool(False, 'Reversal Down', group='Variable Alerts'),
    HCROSSUP=input.bool(False, 'MA Cross Up', group='Variable Alerts'),
    HCROSSDWN=input.bool(False, 'MA Cross Down', group='Variable Alerts'),
    RSIUP=input.bool(False, 'RSI Cross Up 50', group='Variable Alerts'),
    RSIDWN=input.bool(False, 'RSI Cross Down 50', group='Variable Alerts'),
    RSIOB=input.bool(False, 'RSI Cross Up 70', group='Variable Alerts'),
    RSIOS=input.bool(False, 'RSI Cross Down 30', group='Variable Alerts'),
    RSICD=input.bool(False, 'RSI Cross Down 70', group='Variable Alerts'),
    RSICU=input.bool(False, 'RSI Cross Up 30', group='Variable Alerts'),
    DATA=input.bool(False, 'TSI Curl Up', group='Variable Alerts'),
    DTAT=input.bool(False, 'TSI Curl Down', group='Variable Alerts'),
    SARUP=input.bool(False, 'Sar Up', group='Variable Alerts'),
    SARDWN=input.bool(False, 'Sar Down', group='Variable Alerts'),
    textSize=input.string('small', 'Text Size', group='Table', options=('tiny', 'small', 'normal', 'large', 'huge', 'auto')),
    tableYpos=input.string('bottom', 'Position', group='Table', options=('top', 'middle', 'bottom')),
    tableXpos=input.string('right', '', group='Table', options=('left', 'center', 'right')),
    bullRev5=input.color(color.new(color.new('#64B5F6'), 0), '', inline='1', group='T3 MA (Bull, Bear, Fill, Length)'),
    bearRev5=input.color(color.new(color.new('#EF5350'), 0), '', inline='1', group='T3 MA (Bull, Bear, Fill, Length)'),
    bullRev8=input.color(color.new(color.new('#64B5F6'), 0), '', inline='2', group='T3 MA (Bull, Bear, Fill, Length)'),
    bearRev8=input.color(color.new(color.new('#EF5350'), 0), '', inline='2', group='T3 MA (Bull, Bear, Fill, Length)'),
    bullRevF=input.color(color.new(color.new('#64B5F6'), 80), '', inline='1', group='T3 MA (Bull, Bear, Fill, Length)'),
    bearRevF=input.color(color.new(color.new('#EF5350'), 80), '', inline='2', group='T3 MA (Bull, Bear, Fill, Length)'),
    bullHema1=input.color(color.new(color.new('#64B5F6'), 55), '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema1=input.color(color.new(color.new('#D32F2F'), 55), '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullHema2=input.color(color.new(color.new('#64B5F6'), 45), '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema2=input.color(color.new(color.new('#D32F2F'), 45), '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullHema3=input.color(color.new(color.new('#64B5F6'), 35), '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema3=input.color(color.new(color.new('#D32F2F'), 35), '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullHema1F=input.color(color.new(color.new('#64B5F6'), 85), '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema1F=input.color(color.new(color.new('#D32F2F'), 85), '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullHema2F=input.color(color.new(color.new('#64B5F6'), 80), '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema2F=input.color(color.new(color.new('#D32F2F'), 80), '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullHema3F=input.color(color.new(color.new('#64B5F6'), 75), '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)'),
    bearHema3F=input.color(color.new(color.new('#D32F2F'), 75), '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)'),
    bullSar=input.color(color.new(color.new('#64B5F6'), 0), '', inline='7', group='SAR (Bull, Bear)'),
    bearSar=input.color(color.new(color.new('#EF5350'), 0), '', inline='7', group='SAR (Bull, Bear)'),
    aLength=input.int(5, '', inline='1', group='T3 MA (Bull, Bear, Fill, Length)'),
    Length=input.int(8, '', inline='2', group='T3 MA (Bull, Bear, Fill, Length)'),
    hemaslow=input.int(5, '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)'),
    hemaslow2=input.int(9, '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)'),
    hemaslow3=input.int(21, '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)'),
    maType1=input.string('HEMA', '', inline='4', group='MA (Bull, Bear, Fill, Length, Type)', options=('SMA', 'EMA', 'HEMA', 'T3', 'DEMA', 'TEMA', 'HMA', 'WMA', 'VWMA', 'SWMA', 'VWAP')),
    maType2=input.string('HEMA', '', inline='5', group='MA (Bull, Bear, Fill, Length, Type)', options=('SMA', 'EMA', 'HEMA', 'T3', 'DEMA', 'TEMA', 'HMA', 'WMA', 'VWMA', 'SWMA', 'VWAP')),
    maType3=input.string('HEMA', '', inline='6', group='MA (Bull, Bear, Fill, Length, Type)', options=('SMA', 'EMA', 'HEMA', 'T3', 'DEMA', 'TEMA', 'HMA', 'WMA', 'VWMA', 'SWMA', 'VWAP')),
    bullcol=input.color(color.new('#64B5F6'), 'Bull Trend Color', group='Bar Color'),
    bearcol=input.color(color.new('#EF5350'), 'Bear Trend Color', group='Bar Color'),
    bullrev=input.color(color.new('#FFF176'), 'Bullish Reversal Color', group='Bar Color'),
    bearrev=input.color(color.new('#FFF176'), 'Bearish Reversal Color', group='Bar Color'),
    hemabull=input.color(color.new('#64B5F6'), 'MA Bull Color', group='Bar Color'),
    hemabear=input.color(color.new('#E91E63'), 'MA Bear Color', group='Bar Color'),
    hemahold=input.color(color.new('#B2B5BE'), 'MA Hold Color', group='Bar Color'),
    trmbull=input.color(color.new('#3BB3E4'), 'TRM Buy', group='Bar Color'),
    trmbear=input.color(color.new('#FFEB3B'), 'TRM Sell', group='Bar Color'),
    trmhold=input.color(color.new('#B2B5BE'), 'TRM Hold', group='Bar Color'),
    rsi5=input.color(color.new('#17FF00'), 'RSI 0-5', group='Bar Color'),
    rsi10=input.color(color.new('#17FF00'), 'RSI 5-10', group='Bar Color'),
    rsi15=input.color(color.new('#FFFFFF'), 'RSI 10-15', group='Bar Color'),
    rsi20=input.color(color.new('#FFFFFF'), 'RSI 15-20', group='Bar Color'),
    rsi25=input.color(color.new('#FFFFFF'), 'RSI 20-25', group='Bar Color'),
    rsi30=input.color(color.new('#FFFFFF'), 'RSI 25-30', group='Bar Color'),
    rsi35=input.color(color.new('#FFFFFF'), 'RSI 30-35', group='Bar Color'),
    rsi40=input.color(color.new('#FFFFFF'), 'RSI 35-40', group='Bar Color'),
    rsi45=input.color(color.new('#FFFFFF'), 'RSI 40-45', group='Bar Color'),
    rsi50=input.color(color.new('#FFFFFF'), 'RSI 45-50', group='Bar Color'),
    rsi55=input.color(color.new('#2196F3'), 'RSI 50-55', group='Bar Color'),
    rsi60=input.color(color.new('#2196F3'), 'RSI 55-60', group='Bar Color'),
    rsi65=input.color(color.new('#2196F3'), 'RSI 60-65', group='Bar Color'),
    rsi70=input.color(color.new('#2196F3'), 'RSI 65-70', group='Bar Color'),
    rsi75=input.color(color.new('#2196F3'), 'RSI 70-75', group='Bar Color'),
    rsi80=input.color(color.new('#2196F3'), 'RSI 75-80', group='Bar Color'),
    rsi85=input.color(color.new('#9C27B0'), 'RSI 80-85', group='Bar Color'),
    rsi90=input.color(color.new('#9C27B0'), 'RSI 85-90', group='Bar Color'),
    rsi95=input.color(color.new('#FF0000'), 'RSI 90-95', group='Bar Color'),
    rsi100=input.color(color.new('#FF0000'), 'RSI 95-100', group='Bar Color'),
    longf=input.int(25, 'Long Length', group='TSI Fast Settings'),
    shortf=input.int(5, 'Short Length', group='TSI Fast Settings'),
    signalf=input.int(14, 'Signal Length', group='TSI Fast Settings'),
    lenf=input.int(5, 'RSI Length', group='TSI Fast Settings'),
    longs=input.int(25, 'Long Length', group='TSI Slow Settings'),
    shorts=input.int(13, 'Short Length', group='TSI Slow Settings'),
    signals=input.int(13, 'Signal Length', group='TSI Slow Settings'),
    lens=input.int(14, 'RSI Length', group='TSI Slow Settings'),
    start=input.float(0.043, 'Start', group='PSAR'),
    inc=input.float(0.043, 'Increment', group='PSAR'),
    max=input.float(0.34, 'Max', group='PSAR')
):
    cell1 = color.new(color.silver, 80)
    bjrev = strat == 'Bj Reversal'
    hema = strat == 'MA'
    trm = strat == 'TRM'
    rsicol = strat == 'RSI Color'
    tsifast = tsistrat == 'Fast'
    tsislow = tsistrat == 'Slow'
    rsifast = rsistrat == 'Fast'
    rsislow = rsistrat == 'Slow'
    hollow = type == 'Hollow'
    bars = type == 'Bars'
    candle = type == 'Candles'
    shortvar = shortf if tsifast else shorts
    longvar = longf if tsifast else longs
    signalvar = signalf if tsifast else signals
    len = lenf if tsifast else lens if tsislow else lenf if rsifast else lens if rsislow else lens
    def _gd(src, length, alpha):
        result: float = ta.ema(src, length) * (1 + alpha) - ta.ema(ta.ema(src, length), length) * alpha
        return result

    def _t3(src, length, alpha = 0.7):
        result: float = _gd(_gd(_gd(src, length, alpha), length, alpha), length, alpha)
        return result

    def _dema(src, length):
        ema1: float = ta.ema(src, length)
        ema2: float = ta.ema(ema1, length)
        result: float = 2 * ema1 - ema2
        return result

    def _tema(src, length):
        ema1: float = ta.ema(src, length)
        ema2: float = ta.ema(ema1, length)
        ema3: float = ta.ema(ema2, length)
        result: float = 3 * (ema1 - ema2) + ema3
        return result

    def _haVal():
        _c: Series[float] = (open + high + low + close) / 4
        _o: Series[float] = NA(float)
        _o = (open + close) / 2 if na(_o[1]) else (nz(_o[1]) + nz(_c[1])) / 2
        _h: float = math.max(high, math.max(_o, _c))
        _l: float = math.min(low, math.min(_o, _c))
        return (_o, _h, _l, _c)

    o_, h_, l_, c_ = _haVal()
    def _ma(src, type, length):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'EMA':
            __block_result__ = ta.ema(src, length)
        elif __switch__ == 'HEMA':
            __block_result__ = ta.ema(o_, length)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(src, length)
        elif __switch__ == 'HMA':
            __block_result__ = ta.hma(src, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(src, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(src, length)
        elif __switch__ == 'DEMA':
            __block_result__ = _dema(src, length)
        elif __switch__ == 'TEMA':
            __block_result__ = _tema(src, length)
        elif __switch__ == 'T3':
            __block_result__ = _t3(src, length, alphaInput)
        elif __switch__ == 'SWMA':
            __block_result__ = ta.swma(src)
        elif __switch__ == 'VWAP':
            __block_result__ = ta.vwap(src)
        result: float = __block_result__
        return result

    def _alert(cond, txt):
        __block_result_1__ = na
        if cond:
            __block_result_1__ = alert(txt + timeframe.period + ' chart. Price is ' + string.tostring(close), i_alert_mode)
        return __block_result_1__

    def _triGrad(src, min, max, midCol, bearCol, bullCol):
        center: float = min + (max - min) / 2
        result: Color = color.from_gradient(src, center, max, midCol, bullCol) if src >= center else color.from_gradient(src, min, center, bearCol, midCol)
        return result

    def _populate(id, names, syms, col1, col2):
        __block_result_2__ = na
        if showTable:
            __block_result_3__ = na
            for i, a in enumerate(names):
                s = array.get(syms, i)
                table.cell(table_id=id, column=0, row=i, bgcolor=cell1, text=a, text_color=col1, text_size=textSize)
                __block_result_3__ = table.cell(table_id=id, column=1, row=i, bgcolor=NA(Color), text=s, text_color=col2, text_size=textSize)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    tsi: Series = ta.tsi(close, shortvar, longvar)
    tsl = ta.ema(tsi, signalvar)
    rsi = ta.rsi(close, len)
    anT3Average: Series = _t3(source, aLength, alphaInput)
    nT3Average: Series = _t3(source, Length, alphaInput)
    bjhemaslow: Series = _ma(source, maType1, hemaslow)
    bjhemaslow2: Series = _ma(source, maType2, hemaslow2)
    bjhemaslow3: Series = _ma(source, maType3, hemaslow3)
    bjhemafast = ta.ema(hl2, 1)
    sar = ta.sar(start, inc, max)
    hadu = c_ >= o_
    buy1 = ta.crossover(tsi, tsl) and rsi > 50
    buy2 = ta.crossover(rsi, 50) and tsi > tsl
    crossover_1 = ta.crossover(rsi, 50)
    buy3 = ta.crossover(tsi, tsl) and crossover_1
    sell1 = ta.crossunder(tsi, tsl) and rsi < 50
    sell2 = ta.crossunder(rsi, 50) and tsi < tsl
    crossunder_1 = ta.crossunder(rsi, 50)
    sell3 = ta.crossunder(tsi, tsl) and crossunder_1
    rsicross = ta.cross(rsi, 50)
    rsiup = ta.crossover(rsi, 50)
    rsidwn = ta.crossunder(rsi, 50)
    rsiob = ta.crossover(rsi, 70)
    rsios = ta.crossunder(rsi, 30)
    rsicd = ta.crossunder(rsi, 70)
    rsicu = ta.crossover(rsi, 30)
    revbar = ta.cross(close, nT3Average)
    trendbar = ta.cross(nT3Average, anT3Average)
    revup = ta.crossover(close, nT3Average)
    revdwn = ta.crossunder(close, nT3Average)
    cross_1 = ta.cross(close, bjhemaslow2)
    emasig = ta.cross(close, bjhemaslow) and cross_1
    hemauc = close > bjhemaslow and close > bjhemaslow2
    hemadc = close < bjhemaslow and close < bjhemaslow2
    crossup1 = ta.crossover(close, bjhemaslow) and close > bjhemaslow2
    crossup2 = ta.crossover(close, bjhemaslow2) and close > bjhemaslow
    crossover_2 = ta.crossover(close, bjhemaslow)
    crossup3 = ta.crossover(close, bjhemaslow2) and crossover_2
    crossdown1 = ta.crossunder(close, bjhemaslow) and close < bjhemaslow2
    crossdown2 = ta.crossunder(close, bjhemaslow2) and close < bjhemaslow
    crossunder_2 = ta.crossunder(close, bjhemaslow)
    crossdown3 = ta.crossunder(close, bjhemaslow2) and crossunder_2
    sarup = ta.crossover(close, sar)
    sardwn = ta.crossunder(close, sar)
    Hcrossup = crossup1 or crossup2 or crossup3
    Hcrossdwn = crossdown1 or crossdown2 or crossdown3
    buy4 = buy1 or buy2 or buy3
    sell4 = sell1 or sell2 or sell3
    buy = tsi > tsl and rsi > 50
    sell = tsi < tsl and rsi < 50
    data = tsi < tsl and tsi > tsi[1]
    dtat = tsi > tsl and tsi < tsi[1]
    colOne = anT3Average > anT3Average[1]
    upCol = nT3Average > nT3Average[1]
    fillData = anT3Average > nT3Average
    uc = anT3Average >= nT3Average and close > nT3Average
    dc = anT3Average <= nT3Average and close < nT3Average
    dr = anT3Average >= nT3Average and close < nT3Average
    ur = anT3Average <= nT3Average and close > nT3Average
    hauc = anT3Average >= nT3Average and c_ > nT3Average
    hadc = anT3Average <= nT3Average and c_ < nT3Average
    hadr = anT3Average >= nT3Average and c_ < nT3Average
    haur = anT3Average <= nT3Average and c_ > nT3Average
    up = bjhemaslow > bjhemaslow[1]
    up2 = bjhemaslow2 > bjhemaslow2[1]
    up3 = bjhemaslow3 > bjhemaslow3[1]
    hfillData = bjhemaslow < bjhemafast
    hfillDtat = bjhemaslow2 < bjhemaslow
    hfillDat = bjhemaslow3 < bjhemaslow2
    ema1 = bjhemaslow < close
    ema2 = bjhemaslow2 < close
    ema3 = bjhemaslow3 < close
    sarUp = close >= sar
    rsiUp = rsi > 50
    tsiUp = tsi > tsl
    rsiH = rsi >= 90 or rsi <= 10
    names: list[str] = array.from_items('TRM', 'Rev', 'Curl', 'RSI', 'TSI', string.format('{0} {1}', maType1, hemaslow), string.format('{0} {1}', maType2, hemaslow2), string.format('{0} {1}', maType3, hemaslow3), 'SAR')
    syms = array.from_items('✅' if buy else '❌' if sell else '➖', '✅' if uc else '❌' if dc else '🔸', '✅' if data else '❌' if dtat else '➖', '🔥' if rsiH else '✅' if rsiUp else '❌', '✅' if tsiUp else '❌', '✅' if ema1 else '❌', '✅' if ema2 else '❌', '✅' if ema3 else '❌', '✅' if sarUp else '❌')
    sigs = array.from_items(1 if buy else -1 if sell else 0, 1 if uc else -1 if dc else 0, 1 if data else -1 if dtat else 0, 1 if rsiUp else -1, 1 if tsiUp else -1, 1 if ema1 else -1, 1 if ema2 else -1, 1 if ema3 else -1, 1 if sarUp else -1)
    sigSum = array.sum(sigs)
    tabCol = _triGrad(sigSum, -6, 6, color.gray, color.new('#FF0000'), color.green)
    stats: Persistent = table.new(position=tableYpos + '_' + tableXpos, columns=2, rows=9, border_color=color.new(color.gray, 60), border_width=1)
    _populate(stats, names, syms, tabCol, tabCol)
    color2 = bullRev5 if colOne else bearRev5
    myColor = bullRev8 if upCol else bearRev8
    revFillCol = bullRevF if fillData else bearRevF
    hfillCol1 = bullHema1F if hfillData else bearHema1F
    hfillCol2 = bullHema2F if hfillDtat else bearHema2F
    hfillCol3 = bullHema3F if hfillDat else bearHema3F
    mycolor = bullHema1 if up else bearHema1
    mycolor2 = bullHema2 if up2 else bearHema2
    mycolor3 = bullHema3 if up3 else bearHema3
    colUp = bullSar if sarUp else bearSar
    hadefval = bullcol if hadu else bearcol
    trmcolor = trmbull if buy else trmbear if sell else trmhold
    hemabar = hemabull if hemauc else hemabear if hemadc else hemahold
    rsicon = rsi5 if rsi > 0 and rsi <= 5 else rsi10 if rsi > 5 and rsi <= 10 else rsi15 if rsi > 10 and rsi <= 15 else rsi20 if rsi > 15 and rsi <= 20 else rsi25 if rsi > 20 and rsi <= 25 else rsi30 if rsi > 25 and rsi <= 30 else rsi35 if rsi > 30 and rsi <= 35 else rsi40 if rsi > 35 and rsi <= 40 else rsi45 if rsi > 40 and rsi <= 45 else rsi50 if rsi > 45 and rsi <= 50 else rsi55 if rsi > 50 and rsi <= 55 else rsi60 if rsi > 55 and rsi <= 60 else rsi65 if rsi > 60 and rsi <= 65 else rsi70 if rsi > 65 and rsi <= 70 else rsi75 if rsi > 70 and rsi <= 75 else rsi80 if rsi > 75 and rsi <= 80 else rsi85 if rsi > 80 and rsi <= 85 else rsi90 if rsi > 85 and rsi <= 90 else rsi95 if rsi > 90 and rsi <= 95 else rsi100 if rsi > 95 and rsi <= 100 else hadefval
    bjrevcol = bullcol if uc else bearcol if dc else bearrev if dr else bullrev if ur else na
    habjrevcol = bullcol if hauc else bearcol if hadc else bearrev if hadr else bullrev if haur else hadefval
    barColor = trmcolor if trm else bjrevcol if bjrev else rsicon if rsicol else hemabar if hema else na
    habarColor = trmcolor if trm else habjrevcol if bjrev else rsicon if rsicol else hemabar if hema else na
    p2 = plot(anT3Average if t3vis or (not disable and bjrev) else na, 'T3 Fast', color2)
    p1 = plot(nT3Average if t3vis or (not disable and bjrev) else na, 'T3 Slow', myColor)
    hemaslowplot = plot(bjhemaslow if hemavis or (not disable and hema) else na, 'EMA 5', mycolor)
    hemaslowplot2 = plot(bjhemaslow2 if hemavis or (not disable and hema) else na, 'EMA 9', mycolor2)
    hemaslowplot3 = plot(bjhemaslow3 if hemavis or (not disable and hema) else na, 'EMA 21', mycolor3)
    hemafastplot = plot(bjhemafast, 'EMA fast', color.new('#FF000000'), display=display.none, editable=False)
    fill(hemaslowplot, hemafastplot, color=hfillCol1 if hemavis or hema else na, title='5 - Plot Fill')
    fill(hemaslowplot, hemaslowplot2, color=hfillCol2 if hemavis or hema else na, title='5 - 9 Fill')
    fill(hemaslowplot2, hemaslowplot3, color=hfillCol3 if hemavis or hema else na, title='9 - 21 Fill')
    fill(p1, p2, color=revFillCol if t3vis or bjrev else na, title='T3 Fill')
    plotshape(data if arrowvis else False, style=shape.triangleup, location=location.belowbar, color=color.new('#17FF00'), title='Curl Up')
    plotshape(dtat if arrowvis else False, style=shape.triangledown, location=location.abovebar, color=color.new('#FFEB3B'), title='Curl Down')
    plot(sar if psarvis else na, 'SAR', colUp, style=plot.style_circles, linewidth=1)
    plot(close if rPrice else na, 'Real Close', habarColor, trackprice=True, offset=-9999, editable=False)
    candleCol = (habarColor if c_ < o_ else na) if haover and hollow else habarColor if haover and candle else na
    wickCol = color.new('#B2B5BE') if (hollow or candle) and haover else na
    borderCol = habarColor if (hollow or candle) and haover else na
    barCol = habarColor if haover and bars else na
    plotcandle(o_, h_, l_, c_, 'Hollow Candles', candleCol, wickCol, bordercolor=borderCol)
    plotbar(o_, h_, l_, c_, 'Heikin-Ashi', barCol)
    barcolor(color=barColor)
    alertcondition(buy4, 'TRM Buy', 'TRM Buy on {{interval}} chart. Price is {{close}}')
    alertcondition(sell4, 'TRM Sell', 'TRM Sell on {{interval}} chart. Price is {{close}}')
    alertcondition(revbar, 'Bj Reversal', 'Reversal candle is forming on {{interval}} chart. Price is {{close}}')
    alertcondition(trendbar, 'T3 Crossing T3', 'A new trend may be forming on {{interval}} chart. Price is {{close}}')
    alertcondition(revup, 'Reversal Up', 'Reversal up on {{interval}} chart. Price is {{close}}')
    alertcondition(revdwn, 'Reversal Down', 'Reversal down on {{interval}} chart. Price is {{close}}')
    alertcondition(emasig, 'MA Alert', 'Price is crossing MAs on {{interval}} chart. Price is {{close}}')
    alertcondition(Hcrossup, 'MA Cross Up', 'MA crossed up on {{interval}} chart. Price is {{close}}')
    alertcondition(Hcrossdwn, 'MA Cross Down', 'MA crossed down on {{interval}} chart. Price is {{close}}')
    alertcondition(rsicross, 'RSI Signal', 'RSI crossed 50 on {{interval}} chart. Price is {{close}}')
    alertcondition(rsiup, 'RSI Cross Up', 'RSI crossed up 50 on {{interval}} chart. Price is {{close}}')
    alertcondition(rsidwn, 'RSI Cross Down', 'RSI crossed down 50 on {{interval}} chart. Price is {{close}}')
    alertcondition(rsiob, 'RSI Overbought', 'RSI crossed overbought on {{interval}} chart. Price is {{close}}')
    alertcondition(rsios, 'RSI Oversold', 'RSI crossed oversold on {{interval}} chart. Price is {{close}}')
    alertcondition(rsicd, 'RSI momo down', 'RSI crossed down 70 on {{interval}} chart. Price is {{close}}')
    alertcondition(rsicu, 'RSI momo up', 'RSI crossed up 30 on {{interval}} chart. Price is {{close}}')
    alertcondition(data, 'TSI Curl Up', 'TSI curled up on {{interval}} chart. Price is {{close}}')
    alertcondition(dtat, 'TSI Curl Down', 'TSI curled down on {{interval}} chart. Price is {{close}}')
    alertcondition(sarup, 'Sar Up', 'SAR triggered up {{interval}} chart. Price is {{close}}')
    alertcondition(sardwn, 'Sar Down', 'SAR triggered down {{interval}} chart. Price is {{close}}')
    _alert(buy4 and BUY4, 'TRM Buy on ')
    _alert(sell4 and SELL4, 'TRM Sell on ')
    _alert(revup and REVUP, 'Reversal up on ')
    _alert(revdwn and REVDWN, 'Reversal down on ')
    _alert(Hcrossup and HCROSSUP, 'MA crossed up on ')
    _alert(Hcrossdwn and HCROSSDWN, 'MA crossed down on ')
    _alert(rsiup and RSIUP, 'RSI crossed up 50 on ')
    _alert(rsidwn and RSIDWN, 'RSI crossed down 50 on ')
    _alert(rsiob and RSIOB, 'RSI crossed up 70 on ')
    _alert(rsios and RSIOS, 'RSI crossed down 30 on ')
    _alert(rsicd and RSICD, 'RSI crossed down 70 on ')
    _alert(rsicu and RSICU, 'RSI crossed up 30 on ')
    _alert(data and DATA, 'TSI curled up on ')
    _alert(dtat and DTAT, 'TSI curled down on ')
    _alert(sarup and SARUP, 'SAR triggered up ')
    _alert(sardwn and SARDWN, 'SAR triggered down ')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
