"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    display, extend, fill, format, high, hlc3, input, label, line, location, low, math, na, nz,
    open, plot, plotshape, polyline, position, script, shape, size, string, syminfo, ta, table,
    text, time, volume, xloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Polyline, Series, Table
from pynecore.types.chart import ChartPoint


@udt
class ThemePalette:
    tableBg: Color = na(Color)
    tableHeader: Color = na(Color)
    tableText: Color = na(Color)
    frame: Color = na(Color)
    bull: Color = na(Color)
    bear: Color = na(Color)
    neutral: Color = na(Color)
    accentText: Color = na(Color)
    hudBg: Color = na(Color)
    hudBorder: Color = na(Color)
    hudText: Color = na(Color)


@script.indicator('Multicator Table', overlay=True, max_labels_count=300, max_lines_count=150, max_boxes_count=50, max_polylines_count=40)
def main(
    lang=input.string('EN', 'Language', options=('EN', 'TR'), group='General'),
    themeName=input.string('Dark', 'Theme', options=('Dark', 'Light'), group='General'),
    preset=input.string('Manual', 'Preset', options=('Manual', 'Scalping', 'Swing'), group='General'),
    tableMode=input.string('Desktop', 'Table', options=('Off', 'Desktop', 'Mobile'), group='Table'),
    tablePos=input.string('Top Right', 'Position', options=('Top Right', 'Bottom Right', 'Middle Right', 'Bottom Center', 'Bottom Left'), group='Table'),
    tableSize=input.string('Small', 'Size', options=('Small', 'Large', 'Normal'), group='Table'),
    showHud=input.bool(True, 'Show HUD', group='HUD'),
    hudExtra=input.bool(False, 'HUD extra osc (Stoch/CCI/MFI/%R)', group='HUD'),
    hudGap=input.int(30, 'Right gap (bars)', minval=30, maxval=80, group='HUD', tooltip='HUD starts this many bars to the right of the last candle.'),
    hudBars=input.int(40, 'HUD bars', minval=30, maxval=50, group='HUD', tooltip='HUD panel width in bars (30–50).'),
    showFib=input.bool(False, 'Show Fibonacci', group='Fibonacci'),
    fibonacciExtendRight=input.bool(True, 'Extend right', group='Fibonacci', inline='FG'),
    fibShowData=input.bool(True, 'Show labels', group='Fibonacci', inline='FG'),
    fibLookback=input.int(233, minval=8, title='Fibonacci Distance', group='Fibonacci'),
    fibColor=input.color(color.gray, 'Fibonacci Color', group='Fibonacci'),
    fib1=input.int(618, 'Fib Level 1', group='Fibonacci', maxval=1618),
    fib2=input.int(382, 'Fib Level 2', group='Fibonacci', maxval=1618),
    fib3=input.int(786, 'Fib Level 3', group='Fibonacci', maxval=1618),
    ema1=input.int(50, 'EMA 1', group='MA', inline='E1'),
    ema1Show=input.bool(False, '', group='MA', inline='E1'),
    ema1Color=input.color(color.new(color.new('#F7C948'), 0), 'EMA1 COLOR', group='MA'),
    ema2=input.int(100, 'EMA 2', group='MA', inline='E2'),
    ema2Show=input.bool(False, '', group='MA', inline='E2'),
    ema2Color=input.color(color.new(color.new('#61AFEF'), 0), 'EMA2 COLOR', group='MA'),
    ema3=input.int(200, 'EMA 3', group='MA', inline='E3'),
    ema3Show=input.bool(False, '', group='MA', inline='E3'),
    ema3Color=input.color(color.new(color.new('#C678DD'), 0), 'EMA3 COLOR', group='MA'),
    sma1=input.int(50, 'SMA 1', group='MA', inline='S1'),
    sma1Show=input.bool(False, '', group='MA', inline='S1'),
    sma1Color=input.color(color.new(color.new('#98C379'), 0), 'SMA1 COLOR', group='MA'),
    sma2=input.int(100, 'SMA 2', group='MA', inline='S2'),
    sma2Show=input.bool(False, '', group='MA', inline='S2'),
    sma2Color=input.color(color.new(color.new('#56B6C2'), 0), 'SMA2 COLOR', group='MA'),
    sma3=input.int(200, 'SMA 3', group='MA', inline='S3'),
    sma3Show=input.bool(False, '', group='MA', inline='S3'),
    sma3Color=input.color(color.new(color.new('#E06C75'), 0), 'SMA3 COLOR', group='MA'),
    rsiPeriod=input.int(14, 'RSI Period', inline='RSI', group='RSI'),
    rsiShow=input.bool(True, '', inline='RSI', group='RSI'),
    rsiColor=input.color(color.new(color.new('#C678DD'), 0), 'RSI COLOR', group='RSI'),
    rsiMaPeriod=input.int(10, 'RSI MA Period', group='RSI'),
    atrPeriod=input.int(14, 'ATR Period', inline='ATR', group='ATR'),
    atrShow=input.bool(True, '', inline='ATR', group='ATR'),
    atrColor=input.color(color.new(color.new('#E06C75'), 0), 'ATR COLOR', group='ATR'),
    momPeriod=input.int(14, 'MOM Period', inline='MOM', group='MOM'),
    momShow=input.bool(True, '', inline='MOM', group='MOM'),
    momColor=input.color(color.new(color.new('#D19A66'), 0), 'MOM COLOR', group='MOM'),
    diLen=input.int(14, 'DI Length', minval=1, maxval=50, inline='ADX', group='ADX'),
    lensig=input.int(14, 'ADX Smoothing', minval=1, maxval=50, inline='ADX', group='ADX'),
    adxShow=input.bool(True, '', inline='ADX', group='ADX'),
    adxColor=input.color(color.new(color.new('#98C379'), 0), 'ADX COLOR', group='ADX'),
    ml=input.int(12, 'Macd Line', inline='MACD', group='MACD'),
    macdShow=input.bool(True, '', inline='MACD', group='MACD'),
    sl=input.int(26, 'Signal Line', group='MACD'),
    hl=input.int(9, 'Hist Line', group='MACD'),
    macdLineColor=input.color(color.new(color.new('#61AFEF'), 0), 'MACD LINE COLOR', group='MACD'),
    macdSignalColor=input.color(color.new(color.new('#D19A66'), 0), 'MACD SIGNAL COLOR', group='MACD'),
    start=input.float(0.02, 'Start', group='P.SAR', inline='SAR'),
    sarShow=input.bool(False, '', inline='SAR', group='P.SAR'),
    increment=input.float(0.02, 'Increment', group='P.SAR'),
    maximum=input.float(0.2, 'Max Value', group='P.SAR'),
    length=input.int(20, minval=1, group='BB', inline='BB'),
    bbShow=input.bool(False, '', inline='BB', group='BB'),
    maType=input.string('SMA', 'Basis MA Type', options=('SMA', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA'), group='BB'),
    src: Series[float] = input.source(close, 'Source', group='BB'),
    mult=input.float(2.0, minval=0.001, maxval=50, title='StdDev', group='BB'),
    offset=input.int(0, 'Offset', minval=-500, maxval=500, group='BB'),
    conversionPeriods=input.int(9, minval=1, title='Conversion Line Length', group='ICHIMOKU', inline='ICHIMOKU'),
    ichShow=input.bool(False, '', group='ICHIMOKU', inline='ICHIMOKU'),
    basePeriods=input.int(26, minval=1, title='Base Line Length', group='ICHIMOKU'),
    laggingSpan2Periods=input.int(52, minval=1, title='Leading Span B Length', group='ICHIMOKU'),
    displacement=input.int(26, minval=1, title='Lagging Span', group='ICHIMOKU'),
    vwapShow=input.bool(False, 'Show VWAP', group='VWAP'),
    stShow=input.bool(False, 'Show Supertrend', group='Supertrend', inline='ST'),
    stAtrIn=input.int(10, 'ST ATR', minval=1, group='Supertrend', inline='ST'),
    stFactorIn=input.float(3.0, 'ST Factor', minval=0.1, group='Supertrend'),
    donShow=input.bool(False, 'Show Donchian', group='Donchian', inline='DON'),
    donLenIn=input.int(20, 'Donchian Length', minval=1, group='Donchian', inline='DON'),
    kelShow=input.bool(False, 'Show Keltner', group='Keltner', inline='KEL'),
    kelLenIn=input.int(20, 'Keltner Length', minval=1, group='Keltner', inline='KEL'),
    kelMultIn=input.float(1.5, 'Keltner Mult', minval=0.1, group='Keltner'),
    hvnShow=input.bool(False, 'Show HVN line', group='Volume summary'),
    hvnLook=input.int(50, 'HVN lookback', minval=10, maxval=200, group='Volume summary'),
    stochLenIn=input.int(14, 'Stoch Length', minval=1, group='Stoch'),
    cciLenIn=input.int(20, 'CCI Length', minval=1, group='CCI'),
    mfiLenIn=input.int(14, 'MFI Length', minval=1, group='MFI'),
    wprLenIn=input.int(14, 'Williams %R', minval=1, group='WPR'),
    chopLenIn=input.int(14, 'Chop Length', minval=2, group='Chop'),
    showDiv=input.bool(True, 'Show divergence', group='Divergence'),
    divLook=input.int(5, 'Div pivot L/R', minval=2, maxval=20, group='Divergence'),
    pivotShow=input.bool(False, 'PIVOT SHOW', group='PIVOT'),
    leftLenH=input.int(10, minval=1, title='Pivot High', inline='Pivot High', group='PIVOT'),
    rightLenH=input.int(10, minval=1, title='/', inline='Pivot High', group='PIVOT'),
    textColorH=input.color(color.black, title='High text', inline='PHC', group='PIVOT'),
    labelColorH=input.color(color.white, title='High fill', inline='PHC', group='PIVOT'),
    leftLenL=input.int(10, minval=1, title='Pivot Low', inline='Pivot Low', group='PIVOT'),
    rightLenL=input.int(10, minval=1, title='/', inline='Pivot Low', group='PIVOT'),
    textColorL=input.color(color.black, title='Low text', inline='PLC', group='PIVOT'),
    labelColorL=input.color(color.white, title='Low fill', inline='PLC', group='PIVOT'),
    pivotMax=input.int(24, 'Max pivot labels', minval=4, maxval=80, group='PIVOT')
):
    def themePalette(dark: bool):
        return ThemePalette(color.new(color.new('#070B14'), 8) if dark else color.new(color.new('#F4F7FB'), 0), color.new(color.new('#031018'), 0) if dark else color.new(color.new('#E4EEF5'), 0), color.new(color.new('#EAFFFF'), 0) if dark else color.new(color.new('#0B1C28'), 0), color.new(color.new('#00F3FF'), 20) if dark else color.new(color.new('#0B4F6C'), 0), color.new(color.new('#00FF9C'), 35) if dark else color.new(color.new('#C8F7D6'), 0), color.new(color.new('#FF2D6A'), 28) if dark else color.new(color.new('#FFD0D6'), 0), color.new(color.new('#0D1524'), 0) if dark else color.new(color.new('#E8EEF4'), 0), color.new(color.new('#EAFFFF'), 0) if dark else color.new(color.new('#0B1C28'), 0), color.new(color.new('#05080F'), 18) if dark else color.new(color.new('#DFE7EF'), 8), color.new(color.new('#00F3FF'), 25) if dark else color.new(color.new('#0B4F6C'), 0), color.new(color.new('#EAFFFF'), 0) if dark else color.new(color.new('#0B1C28'), 0))

    en = lang == 'EN'
    isDark = themeName == 'Dark'
    theme = themePalette(isDark)
    colEma1 = color.new(color.new('#F8FF32'), 0) if isDark else color.new(color.new('#7A5B00'), 0)
    colEma2 = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#063A8C'), 0)
    colEma3 = color.new(color.new('#FF4DFF'), 0) if isDark else color.new(color.new('#5B21B6'), 0)
    colSma1 = color.new(color.new('#00FF9C'), 0) if isDark else color.new(color.new('#14532D'), 0)
    colSma2 = color.new(color.new('#39FF14'), 0) if isDark else color.new(color.new('#0F766E'), 0)
    colSma3 = color.new(color.new('#FF2D6A'), 0) if isDark else color.new(color.new('#9F1239'), 0)
    colRsi = color.new(color.new('#BF5AF2'), 0) if isDark else color.new(color.new('#6B21A8'), 0)
    colRsiMa = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#1E3A5F'), 0)
    colAtr = color.new(color.new('#FF2D6A'), 0) if isDark else color.new(color.new('#9F1239'), 0)
    colMom = color.new(color.new('#FFB800'), 0) if isDark else color.new(color.new('#92400E'), 0)
    colAdx = color.new(color.new('#00FF9C'), 0) if isDark else color.new(color.new('#14532D'), 0)
    colMacd = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#063A8C'), 0)
    colMacdSig = color.new(color.new('#FFB800'), 0) if isDark else color.new(color.new('#92400E'), 0)
    colSar = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#063A8C'), 0)
    colBbMid = color.new(color.new('#FFB800'), 0) if isDark else color.new(color.new('#9A3412'), 0)
    colBbBand = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#063A8C'), 0)
    colIchTenkan = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#063A8C'), 0)
    colIchKijun = color.new(color.new('#FF2D6A'), 0) if isDark else color.new(color.new('#9F1239'), 0)
    colIchChikou = color.new(color.new('#00FF9C'), 0) if isDark else color.new(color.new('#14532D'), 0)
    colFib = color.new(color.new('#00F3FF'), 20) if isDark else color.new(color.new('#334155'), 0)
    colVwap = color.new(color.new('#FFB800'), 0) if isDark else color.new(color.new('#9A3412'), 0)
    colSt = color.new(color.new('#00FF9C'), 0) if isDark else color.new(color.new('#166534'), 0)
    colDon = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#1E40AF'), 0)
    colKel = color.new(color.new('#FF4DFF'), 0) if isDark else color.new(color.new('#6B21A8'), 0)
    colStoch = color.new(color.new('#39FF14'), 0) if isDark else color.new(color.new('#3F6212'), 0)
    colCci = color.new(color.new('#FFB800'), 0) if isDark else color.new(color.new('#854D0E'), 0)
    colMfi = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#0E7490'), 0)
    colWpr = color.new(color.new('#FF2D6A'), 0) if isDark else color.new(color.new('#9F1239'), 0)
    neonHeaderText = color.new(color.new('#00F3FF'), 0) if isDark else color.new(color.new('#0A6B7C'), 0)

    scalp = preset == 'Scalping'
    swing = preset == 'Swing'
    rsiLenK = 7 if scalp else 21 if swing else rsiPeriod
    macdFast = 8 if scalp else ml
    macdSlow = 17 if scalp else sl
    macdSignal = 9 if scalp else hl
    adxDiK = 10 if scalp else diLen
    stochLenK = 8 if scalp else 14 if swing else stochLenIn
    stAtrK = 7 if scalp else 10 if swing else stAtrIn
    stFactorK = 2.5 if scalp else 3.0 if swing else stFactorIn

    __block_result__ = na
    __switch__ = tablePos
    if __switch__ == 'Top Right':
        __block_result__ = position.top_right
    elif __switch__ == 'Bottom Right':
        __block_result__ = position.bottom_right
    elif __switch__ == 'Middle Right':
        __block_result__ = position.middle_right
    elif __switch__ == 'Bottom Center':
        __block_result__ = position.bottom_center
    elif __switch__ == 'Bottom Left':
        __block_result__ = position.bottom_left
    else:
        __block_result__ = position.top_right
    tablePlace = __block_result__

    __block_result_1__ = na
    __switch__ = tableSize
    if __switch__ == 'Small':
        __block_result_1__ = size.small
    elif __switch__ == 'Large':
        __block_result_1__ = size.large
    elif __switch__ == 'Normal':
        __block_result_1__ = size.normal
    else:
        __block_result_1__ = size.small
    textSz = __block_result_1__

    mobileTable: Persistent[Table] = table.new(position.bottom_right, 2, 22, border_width=1, border_color=theme.frame, frame_color=theme.frame, frame_width=2)
    deskTable: Persistent[Table] = table.new(position.top_right, 6, 10, border_width=1, border_color=theme.frame, frame_color=theme.frame, frame_width=2)

    def mapY(val: float, vmin: float, vmax: float, yBot: float, yTop: float):
        rng: float = math.max(vmax - vmin, syminfo.mintick)
        return yBot + (nz(val, vmin) - vmin) / rng * (yTop - yBot)

    def visibleRange(leftTime: int, rightTime: int):
        vh: float = high
        vl: float = low
        started: bool = False
        i: int = 0
        while i < 5000 and (not na(time[i])):
            t: int = time[i]
            if t >= leftTime and t <= rightTime:
                if not started:
                    vh = high[i]
                    vl = low[i]
                    started = True
                else:
                    vh = math.max(vh, high[i])
                    vl = math.min(vl, low[i])
            if t < leftTime:
                break
            i += 1
        return (vh, vl)

    def sparkPoints(srcVal: Series[float], len: int, x0: int, xStep: int, yBot: float, yTop: float, vmin: float, vmax: float):
        pts: list[ChartPoint] = array.new(0, NA(ChartPoint))
        for i in pine_range(0, len - 1):
            y: float = mapY(srcVal[len - 1 - i], vmin, vmax, yBot, yTop)
            array.push(pts, chart.point.from_index(x0 + i * xStep, y))
        return pts

    def hudGeometry(slot: int, slotCount: int, visTop: float, visBot: float):
        visSpan: float = math.max(visTop - visBot, syminfo.mintick)
        gapY: float = visSpan * 0.04
        n: int = math.max(slotCount, 1)
        usable: float = visSpan - gapY * (n + 1)
        h: float = usable / n
        yTop: float = visTop - gapY - slot * (h + gapY)
        yBot: float = yTop - h
        return (yTop, yBot)

    def maColor(maVal: float):
        return theme.bear if maVal > close else theme.bull

    def cell(t: Table, col: int, row: int, txt: str, bg: Color):
        return table.cell(t, col, row, txt, bgcolor=bg, text_color=theme.tableText, text_size=textSz, text_halign=text.align_center)

    def headerCell(t: Table, col: int, row: int, txt: str):
        return table.cell(t, col, row, txt, bgcolor=theme.tableHeader, text_color=neonHeaderText, text_size=textSz, text_halign=text.align_center)

    def rsiCellColor(r: float):
        return theme.bear if r >= 70 else theme.bull if r <= 30 else color.from_gradient(r, 30, 70, theme.neutral, color.new(color.new('#7C3AED'), 45 if isDark else 70))

    def chgCellColor(f: float):
        return color.from_gradient(math.min(math.abs(f), 3.0), 0.0, 3.0, theme.neutral, theme.bull) if f > 0 else color.from_gradient(math.min(math.abs(f), 3.0), 0.0, 3.0, theme.neutral, theme.bear) if f < 0 else theme.neutral

    def adxCellColor(a: float):
        return color.from_gradient(math.min(a, 50.0), 15.0, 40.0, theme.neutral, theme.bull)

    def clearHud(boxes: list[Box], polylines: list[Polyline], labels: list[Label]):
        if array.size(boxes) > 0:
            for i in pine_range(0, array.size(boxes) - 1):
                box.delete(array.get(boxes, i))
            array.clear(boxes)
        if array.size(polylines) > 0:
            for i in pine_range(0, array.size(polylines) - 1):
                polyline.delete(array.get(polylines, i))
            array.clear(polylines)
        __block_result_2__ = na
        if array.size(labels) > 0:
            for i in pine_range(0, array.size(labels) - 1):
                label.delete(array.get(labels, i))
            __block_result_2__ = array.clear(labels)
        return __block_result_2__

    def addPivot(lbls: list[Label], lbl: Label, limit: int):
        array.push(lbls, lbl)
        __block_result_3__ = na
        if array.size(lbls) > limit:
            __block_result_3__ = label.delete(array.shift(lbls))
        return __block_result_3__

    fibHigh = ta.highest(fibLookback)
    fibLow = ta.lowest(fibLookback)
    distToHigh = math.abs(ta.highestbars(fibLookback))
    distToLow = math.abs(ta.lowestbars(fibLookback))
    fibTopTxt = 'Top ( ' if en else 'Tepe ( '
    fibBotTxt = 'Bottom ( ' if en else 'Dip ( '

    ema50 = ta.ema(close, ema1)
    ema100 = ta.ema(close, ema2)
    ema200 = ta.ema(close, ema3)
    emaRegime = ta.ema(close, 200)
    sma50 = ta.sma(close, sma1)
    sma100 = ta.sma(close, sma2)
    sma200 = ta.sma(close, sma3)

    chg = ta.change(close) / close[1] * 100
    rsi: Series = ta.rsi(close, rsiLenK)
    rsiMa = ta.sma(rsi, rsiMaPeriod)
    atr = ta.atr(atrPeriod)
    mom = ta.mom(close, momPeriod)
    diplus, diminus, adx = ta.dmi(adxDiK, lensig)
    macdLine: Series
    macdLine, signalLine, histLine = ta.macd(close, macdFast, macdSlow, macdSignal)
    out = ta.sar(start, increment, maximum)
    volMa20 = ta.sma(volume, 20)
    relVol = 1.0 if volMa20 == 0 else volume / volMa20
    stochK = ta.stoch(close, high, low, stochLenK)
    stochD = ta.sma(stochK, 3)
    cci = ta.cci(hlc3, cciLenIn)
    mfi = ta.mfi(hlc3, mfiLenIn)
    wpr = ta.wpr(wprLenIn)
    obv = ta.obv
    vwapVal = ta.vwap(hlc3)
    stLine, stDir = ta.supertrend(stFactorK, stAtrK)
    donHigh = ta.highest(high, donLenIn)
    donLow = ta.lowest(low, donLenIn)
    donMid = math.avg(donHigh, donLow)
    kelBasis = ta.ema(close, kelLenIn)
    kelDev = kelMultIn * ta.atr(kelLenIn)
    kelUpper = kelBasis + kelDev
    kelLower = kelBasis - kelDev
    atr1 = ta.atr(1)
    chopNum = math.max(ta.highest(high, chopLenIn) - ta.lowest(low, chopLenIn), syminfo.mintick)
    chop = 100.0 * math.log(math.max(math.sum(atr1, chopLenIn), syminfo.mintick) / chopNum) / math.log(chopLenIn)

    hvnPrice = close
    hvnVol = volume
    for hvnI in pine_range(1, hvnLook - 1):
        if volume[hvnI] > hvnVol:
            hvnVol = volume[hvnI]
            hvnPrice = close[hvnI]

    rsiBgSeri = rsiCellColor(rsi)
    chgBgSeri = chgCellColor(chg)
    adxBgSeri = adxCellColor(adx)
    volBgSeri = theme.bull if relVol > 1.5 else theme.neutral if relVol < 0.65 else theme.tableBg
    macdLoHud = math.min(ta.lowest(macdLine, hudBars), ta.lowest(signalLine, hudBars))
    macdHiHud = math.max(ta.highest(macdLine, hudBars), ta.highest(signalLine, hudBars))
    adxHiHud = math.max(50.0, ta.highest(adx, hudBars))
    momLoHud = ta.lowest(mom, hudBars)
    momHiHud = ta.highest(mom, hudBars)
    atrLoHud = ta.lowest(atr, hudBars)
    atrHiHud = ta.highest(atr, hudBars)
    stochLoHud = ta.lowest(stochK, hudBars)
    stochHiHud = ta.highest(stochK, hudBars)
    cciLoHud = ta.lowest(cci, hudBars)
    cciHiHud = ta.highest(cci, hudBars)
    mfiLoHud: float = 0.0
    mfiHiHud: float = 100.0
    wprLoHud = -100.0
    wprHiHud: float = 0.0
    fallbackHigh = ta.highest(high, 100)
    fallbackLow = ta.lowest(low, 100)

    voteEma = 1 if close > emaRegime else 0
    voteAdx = 1 if adx > 25 else 0
    voteMacd = 1 if macdLine > signalLine else 0
    voteRsi = 1 if rsi >= 40 and rsi <= 65 else 0
    voteSt = 1 if stDir < 0 else 0
    voteStoch = 1 if stochK > 50 else 0
    voteMfi = 1 if mfi > 50 else 0
    voteVol = 1 if relVol >= 1.0 else 0
    voteDon = 1 if close > donMid else 0
    score = cast_int(math.round((voteEma + voteAdx + voteMacd + voteRsi + voteSt + voteStoch + voteMfi + voteVol + voteDon) / 9.0 * 100.0))
    regimeRange = adx < 20 or chop > 61.8
    regimeText = ('Range' if en else 'Yatay') if regimeRange else ('Trend up' if en else 'Trend yukarı') if close > emaRegime else 'Trend down' if en else 'Trend aşağı'
    scoreBg = theme.bull if score >= 66 else theme.bear if score <= 33 else theme.neutral

    bbSma = ta.sma(src, length)
    bbEma = ta.ema(src, length)
    bbRma = ta.rma(src, length)
    bbWma = ta.wma(src, length)
    bbVwma = ta.vwma(src, length)
    __block_result_4__ = na
    __switch__ = maType
    if __switch__ == 'SMA':
        __block_result_4__ = bbSma
    elif __switch__ == 'EMA':
        __block_result_4__ = bbEma
    elif __switch__ == 'SMMA (RMA)':
        __block_result_4__ = bbRma
    elif __switch__ == 'WMA':
        __block_result_4__ = bbWma
    elif __switch__ == 'VWMA':
        __block_result_4__ = bbVwma
    else:
        __block_result_4__ = bbSma
    basis = __block_result_4__
    dev = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev

    def donchian(lenDon: int):
        return math.avg(ta.lowest(lenDon), ta.highest(lenDon))

    conversionLine = donchian(conversionPeriods)
    baseLine = donchian(basePeriods)
    leadLine1 = math.avg(conversionLine, baseLine)
    leadLine2 = donchian(laggingSpan2Periods)

    plot(ema50 if ema1Show else na, color=colEma1, title='EMA1', linewidth=2)
    plot(ema100 if ema2Show else na, color=colEma2, title='EMA2', linewidth=2)
    plot(ema200 if ema3Show else na, color=colEma3, title='EMA3', linewidth=2)
    plot(sma50 if sma1Show else na, color=colSma1, title='SMA1', linewidth=2)
    plot(sma100 if sma2Show else na, color=colSma2, title='SMA2', linewidth=2)
    plot(sma200 if sma3Show else na, color=colSma3, title='SMA3', linewidth=2)
    plot(out if sarShow else na, 'ParabolicSAR', style=plot.style_cross, color=colSar, linewidth=2)
    plot(basis if bbShow else na, 'Basis', color=colBbMid, offset=offset, linewidth=2)
    p1 = plot(upper if bbShow else na, 'Upper', color=colBbBand, offset=offset, linewidth=2)
    p2 = plot(lower if bbShow else na, 'Lower', color=colBbBand, offset=offset, linewidth=2)
    fill(p1, p2, title='Background', color=(color.new(color.new('#00F3FF'), 88) if isDark else color.new(color.new('#063A8C'), 88)) if bbShow else na)
    plot(conversionLine if ichShow else na, color=colIchTenkan, title='Conversion Line', linewidth=2)
    plot(baseLine if ichShow else na, color=colIchKijun, title='Base Line', linewidth=2)
    plot(close if ichShow else na, offset=-displacement + 1, color=colIchChikou, title='Lagging Span', linewidth=2)
    p1i = plot(leadLine1 if ichShow else na, offset=displacement - 1, color=colSma1, title='Leading Span A', linewidth=2)
    p2i = plot(leadLine2 if ichShow else na, offset=displacement - 1, color=colSma3, title='Leading Span B', linewidth=2)
    plot((leadLine1 if leadLine1 > leadLine2 else leadLine2) if ichShow else na, offset=displacement - 1, title='Kumo Cloud Upper Line', display=display.none)
    plot((leadLine1 if leadLine1 < leadLine2 else leadLine2) if ichShow else na, offset=displacement - 1, title='Kumo Cloud Lower Line', display=display.none)
    fill(p1i, p2i, color=((color.new(color.new('#00FF9C'), 82) if isDark else color.new(color.new('#14532D'), 85)) if leadLine1 > leadLine2 else color.new(color.new('#FF2D6A'), 82) if isDark else color.new(color.new('#9F1239'), 85)) if ichShow else na)
    plot(vwapVal if vwapShow else na, 'VWAP', color=colVwap, linewidth=2)
    plot(stLine if stShow else na, 'Supertrend', color=colSt if stDir < 0 else colSma3, linewidth=2)
    plot(donHigh if donShow else na, 'Donchian High', color=colDon, linewidth=2)
    plot(donLow if donShow else na, 'Donchian Low', color=colDon, linewidth=2)
    plot(kelUpper if kelShow else na, 'Keltner Upper', color=colKel, linewidth=2)
    plot(kelLower if kelShow else na, 'Keltner Lower', color=colKel, linewidth=2)
    plot(kelBasis if kelShow else na, 'Keltner Basis', color=colKel, linewidth=1)

    fibLHigh: Persistent[Line] = na(Line)
    fibLLow: Persistent[Line] = na(Line)
    fibL382: Persistent[Line] = na(Line)
    fibL50: Persistent[Line] = na(Line)
    fibL618: Persistent[Line] = na(Line)
    fibL786: Persistent[Line] = na(Line)
    fibLbHigh: Persistent[Label] = na(Label)
    fibLbLow: Persistent[Label] = na(Label)
    fibLb382: Persistent[Label] = na(Label)
    fibLb50: Persistent[Label] = na(Label)
    fibLb618: Persistent[Label] = na(Label)
    fibLb786: Persistent[Label] = na(Label)
    hvnLine: Persistent[Line] = na(Line)

    def setFibLine(ln: Line, x1: int, y: float, x2: int, styleName: str):
        result: Line = ln
        if na(result):
            result = line.new(x1, y, x2, y, color=colFib, width=1, style=line.style_dashed if styleName == 'dash' else line.style_solid, extend=extend.right if fibonacciExtendRight else extend.none)
        else:
            line.set_xy1(result, x1, y)
            line.set_xy2(result, x2, y)
            line.set_color(result, colFib)
            line.set_extend(result, extend.right if fibonacciExtendRight else extend.none)
            line.set_style(result, line.style_dashed if styleName == 'dash' else line.style_solid)
        return result

    def setFibLabel(lb: Label, x: int, y: float, txt: str):
        result: Label = lb
        if na(result):
            result = label.new(x, y, txt, color=color.new(color.gray, 100), style=label.style_none, textcolor=theme.hudText)
        else:
            label.set_xy(result, x, y)
            label.set_text(result, txt)
            label.set_textcolor(result, theme.hudText)
        return result

    if barstate.islast:
        if showFib:
            fib618: float = fibHigh - (fibHigh - fibLow) * fib1 / 1000 if distToLow > distToHigh else fibLow + (fibHigh - fibLow) * fib1 / 1000
            fib50: float = fibHigh - (fibHigh - fibLow) * 500 / 1000 if distToLow > distToHigh else fibLow + (fibHigh - fibLow) * 500 / 1000
            fib382: float = fibHigh - (fibHigh - fibLow) * fib2 / 1000 if distToLow > distToHigh else fibLow + (fibHigh - fibLow) * fib2 / 1000
            fib786: float = fibHigh - (fibHigh - fibLow) * fib3 / 1000 if distToLow > distToHigh else fibLow + (fibHigh - fibLow) * fib3 / 1000
            xHigh: int = bar_index - cast_int(distToHigh)
            xLow: int = bar_index - cast_int(distToLow)
            xRight: int = bar_index + 50
            xLbl: int = bar_index + 55
            fibLHigh = setFibLine(fibLHigh, xHigh, fibHigh, xRight, 'solid')
            fibLLow = setFibLine(fibLLow, xLow, fibLow, xRight, 'solid')
            fibL382 = setFibLine(fibL382, bar_index + 10, fib382, xRight, 'dash')
            fibL50 = setFibLine(fibL50, bar_index + 10, fib50, xRight, 'dash')
            fibL618 = setFibLine(fibL618, bar_index + 10, fib618, xRight, 'dash')
            fibL786 = setFibLine(fibL786, bar_index + 10, fib786, xRight, 'dash')
            if fibShowData:
                fibLbHigh = setFibLabel(fibLbHigh, xLbl, fibHigh, fibTopTxt + string.tostring(math.round_to_mintick(fibHigh)) + ' )')
                fibLbLow = setFibLabel(fibLbLow, xLbl, fibLow, fibBotTxt + string.tostring(math.round_to_mintick(fibLow)) + ' )')
                fibLb382 = setFibLabel(fibLb382, xLbl, fib382, string.tostring(fib2 / 1000) + ' ( ' + string.tostring(math.round_to_mintick(fib382)) + ' )')
                fibLb618 = setFibLabel(fibLb618, xLbl, fib618, string.tostring(fib1 / 1000) + ' ( ' + string.tostring(math.round_to_mintick(fib618)) + ' )')
                fibLb50 = setFibLabel(fibLb50, xLbl, fib50, '% 50 ( ' + string.tostring(math.round_to_mintick(fib50)) + ' )')
                fibLb786 = setFibLabel(fibLb786, xLbl, fib786, string.tostring(fib3 / 1000) + ' ( ' + string.tostring(math.round_to_mintick(fib786)) + ' )')
            else:
                if not na(fibLbHigh):
                    label.delete(fibLbHigh)
                    fibLbHigh = na
                if not na(fibLbLow):
                    label.delete(fibLbLow)
                    fibLbLow = na
                if not na(fibLb382):
                    label.delete(fibLb382)
                    fibLb382 = na
                if not na(fibLb50):
                    label.delete(fibLb50)
                    fibLb50 = na
                if not na(fibLb618):
                    label.delete(fibLb618)
                    fibLb618 = na
                if not na(fibLb786):
                    label.delete(fibLb786)
                    fibLb786 = na
        else:
            if not na(fibLHigh):
                line.delete(fibLHigh)
                fibLHigh = na
            if not na(fibLLow):
                line.delete(fibLLow)
                fibLLow = na
            if not na(fibL382):
                line.delete(fibL382)
                fibL382 = na
            if not na(fibL50):
                line.delete(fibL50)
                fibL50 = na
            if not na(fibL618):
                line.delete(fibL618)
                fibL618 = na
            if not na(fibL786):
                line.delete(fibL786)
                fibL786 = na
            if not na(fibLbHigh):
                label.delete(fibLbHigh)
                fibLbHigh = na
            if not na(fibLbLow):
                label.delete(fibLbLow)
                fibLbLow = na
            if not na(fibLb382):
                label.delete(fibLb382)
                fibLb382 = na
            if not na(fibLb50):
                label.delete(fibLb50)
                fibLb50 = na
            if not na(fibLb618):
                label.delete(fibLb618)
                fibLb618 = na
            if not na(fibLb786):
                label.delete(fibLb786)
                fibLb786 = na
        if hvnShow:
            if na(hvnLine):
                hvnLine = line.new(bar_index - hvnLook, hvnPrice, bar_index + 10, hvnPrice, color=colMom, style=line.style_dotted, extend=extend.right)
            else:
                line.set_xy1(hvnLine, bar_index - hvnLook, hvnPrice)
                line.set_xy2(hvnLine, bar_index + 10, hvnPrice)
                line.set_color(hvnLine, colMom)
        elif not na(hvnLine):
            line.delete(hvnLine)
            hvnLine = na

    ph = ta.pivothigh(leftLenH, rightLenH)
    pl = ta.pivotlow(leftLenL, rightLenL)
    phDiv = ta.pivothigh(divLook, divLook)
    plDiv = ta.pivotlow(divLook, divLook)
    pivotLabels: Persistent[list[Label]] = array.new_label()
    lastPh: Persistent[float] = na(float)
    lastPhRsi: Persistent[float] = na(float)
    lastPhMacd: Persistent[float] = na(float)
    lastPl: Persistent[float] = na(float)
    lastPlRsi: Persistent[float] = na(float)
    lastPlMacd: Persistent[float] = na(float)
    bearRsiDiv: bool = False
    bullRsiDiv: bool = False
    bearMacdDiv: bool = False
    bullMacdDiv: bool = False
    if not na(phDiv):
        pr: float = rsi[divLook]
        pm: float = macdLine[divLook]
        if not na(lastPh):
            if phDiv > lastPh and pr < lastPhRsi:
                bearRsiDiv = True
            if phDiv > lastPh and pm < lastPhMacd:
                bearMacdDiv = True
        lastPh = phDiv
        lastPhRsi = pr
        lastPhMacd = pm
    if not na(plDiv):
        lr: float = rsi[divLook]
        lm: float = macdLine[divLook]
        if not na(lastPl):
            if plDiv < lastPl and lr > lastPlRsi:
                bullRsiDiv = True
            if plDiv < lastPl and lm > lastPlMacd:
                bullMacdDiv = True
        lastPl = plDiv
        lastPlRsi = lr
        lastPlMacd = lm

    plotshape(showDiv and bullRsiDiv, title='RSI bull div', style=shape.triangleup, location=location.belowbar, color=colSt, size=size.tiny)
    plotshape(showDiv and bearRsiDiv, title='RSI bear div', style=shape.triangledown, location=location.abovebar, color=colSma3, size=size.tiny)
    plotshape(showDiv and bullMacdDiv, title='MACD bull div', style=shape.diamond, location=location.belowbar, color=colMacd, size=size.tiny)
    plotshape(showDiv and bearMacdDiv, title='MACD bear div', style=shape.diamond, location=location.abovebar, color=colMacdSig, size=size.tiny)

    if pivotShow:
        if not na(ph):
            addPivot(pivotLabels, label.new(bar_index[rightLenH], ph, string.tostring(ph, format.mintick), style=label.style_label_down, color=theme.tableBg, textcolor=theme.tableText), pivotMax)
        if not na(pl):
            addPivot(pivotLabels, label.new(bar_index[rightLenL], pl, string.tostring(pl, format.mintick), style=label.style_label_up, color=theme.tableBg, textcolor=theme.tableText), pivotMax)

    hudBoxes: Persistent[list[Box]] = array.new_box()
    hudPolylines: Persistent[list[Polyline]] = array.new(0, NA(Polyline))
    hudLabels: Persistent[list[Label]] = array.new_label()

    def drawHud(x0: int, xStep: int, len: int, yTop: float, yBot: float, title: str, pts1: list[ChartPoint], pts2: list[ChartPoint], col1: Color, col2: Color, dual: bool):
        array.push(hudBoxes, box.new(x0, yTop, x0 + (len - 1) * xStep, yBot, border_color=theme.hudBorder, bgcolor=theme.hudBg, extend=extend.none, xloc=xloc.bar_index))
        array.push(hudPolylines, polyline.new(pts1, False, False, xloc.bar_index, col1, NA(Color), line.style_solid, 2))
        if dual:
            array.push(hudPolylines, polyline.new(pts2, False, False, xloc.bar_index, col2, NA(Color), line.style_solid, 2))
        return array.push(hudLabels, label.new(x0, yTop, title, style=label.style_none, color=color.new(color.black, 100), textcolor=theme.hudText, size=size.small, textalign=text.align_left))

    leftVisTime = chart.left_visible_bar_time
    rightVisTime = chart.right_visible_bar_time
    x0Hud = bar_index + hudGap
    xStepHud: int = 1
    lenHud = hudBars
    visTop0, visBot0 = visibleRange(leftVisTime, rightVisTime)
    visTopHud = fallbackHigh if visTop0 - visBot0 < syminfo.mintick * 2 else visTop0
    visBotHud = fallbackLow if visTop0 - visBot0 < syminfo.mintick * 2 else visBot0
    geoTop = visTopHud
    geoBot = visBotHud
    slotN = 9 if hudExtra else 5
    yT0, yB0 = hudGeometry(0, slotN, geoTop, geoBot)
    yT1, yB1 = hudGeometry(1, slotN, geoTop, geoBot)
    yT2, yB2 = hudGeometry(2, slotN, geoTop, geoBot)
    yT3, yB3 = hudGeometry(3, slotN, geoTop, geoBot)
    yT4, yB4 = hudGeometry(4, slotN, geoTop, geoBot)
    yT5, yB5 = hudGeometry(5, slotN, geoTop, geoBot)
    yT6, yB6 = hudGeometry(6, slotN, geoTop, geoBot)
    yT7, yB7 = hudGeometry(7, slotN, geoTop, geoBot)
    yT8, yB8 = hudGeometry(8, slotN, geoTop, geoBot)
    ptsRsi = sparkPoints(rsi, lenHud, x0Hud, xStepHud, yB0, yT0, 0.0, 100.0)
    ptsRsiMa = sparkPoints(rsiMa, lenHud, x0Hud, xStepHud, yB0, yT0, 0.0, 100.0)
    ptsMacd = sparkPoints(macdLine, lenHud, x0Hud, xStepHud, yB1, yT1, macdLoHud, macdHiHud)
    ptsMacdSig = sparkPoints(signalLine, lenHud, x0Hud, xStepHud, yB1, yT1, macdLoHud, macdHiHud)
    ptsAdx = sparkPoints(adx, lenHud, x0Hud, xStepHud, yB2, yT2, 0.0, adxHiHud)
    ptsMom = sparkPoints(mom, lenHud, x0Hud, xStepHud, yB3, yT3, momLoHud, momHiHud)
    ptsAtr = sparkPoints(atr, lenHud, x0Hud, xStepHud, yB4, yT4, atrLoHud, atrHiHud)
    ptsStoch = sparkPoints(stochK, lenHud, x0Hud, xStepHud, yB5, yT5, stochLoHud, stochHiHud)
    ptsStochD = sparkPoints(stochD, lenHud, x0Hud, xStepHud, yB5, yT5, stochLoHud, stochHiHud)
    ptsCci = sparkPoints(cci, lenHud, x0Hud, xStepHud, yB6, yT6, cciLoHud, cciHiHud)
    ptsMfi = sparkPoints(mfi, lenHud, x0Hud, xStepHud, yB7, yT7, mfiLoHud, mfiHiHud)
    ptsWpr = sparkPoints(wpr, lenHud, x0Hud, xStepHud, yB8, yT8, wprLoHud, wprHiHud)

    if barstate.islast:
        clearHud(hudBoxes, hudPolylines, hudLabels)
        if showHud:
            if rsiShow:
                drawHud(x0Hud, xStepHud, lenHud, yT0, yB0, 'RSI ' + string.tostring(math.round_to_mintick(rsi)), ptsRsi, ptsRsiMa, colRsi, colRsiMa, True)
            if macdShow:
                drawHud(x0Hud, xStepHud, lenHud, yT1, yB1, 'MACD ' + string.tostring(math.round(macdLine, 4)), ptsMacd, ptsMacdSig, colMacd, colMacdSig, True)
            if adxShow:
                drawHud(x0Hud, xStepHud, lenHud, yT2, yB2, 'ADX ' + string.tostring(math.round_to_mintick(adx)), ptsAdx, ptsAdx, colAdx, colAdx, False)
            if momShow:
                drawHud(x0Hud, xStepHud, lenHud, yT3, yB3, 'MOM ' + string.tostring(math.round_to_mintick(mom)), ptsMom, ptsMom, colMom, colMom, False)
            if atrShow:
                drawHud(x0Hud, xStepHud, lenHud, yT4, yB4, 'ATR ' + string.tostring(math.round_to_mintick(atr)), ptsAtr, ptsAtr, colAtr, colAtr, False)
            if hudExtra:
                drawHud(x0Hud, xStepHud, lenHud, yT5, yB5, 'Stoch ' + string.tostring(math.round_to_mintick(stochK)), ptsStoch, ptsStochD, colStoch, colMfi, True)
                drawHud(x0Hud, xStepHud, lenHud, yT6, yB6, 'CCI ' + string.tostring(math.round_to_mintick(cci)), ptsCci, ptsCci, colCci, colCci, False)
                drawHud(x0Hud, xStepHud, lenHud, yT7, yB7, 'MFI ' + string.tostring(math.round_to_mintick(mfi)), ptsMfi, ptsMfi, colMfi, colMfi, False)
                drawHud(x0Hud, xStepHud, lenHud, yT8, yB8, '%R ' + string.tostring(math.round_to_mintick(wpr)), ptsWpr, ptsWpr, colWpr, colWpr, False)

    if barstate.islast:
        table.set_position(deskTable, tablePlace)
        table.set_position(mobileTable, position.bottom_right)
        table.set_border_color(deskTable, theme.frame)
        table.set_frame_color(deskTable, theme.frame)
        table.set_border_color(mobileTable, theme.frame)
        table.set_frame_color(mobileTable, theme.frame)
        table.clear(deskTable, 0, 0, 5, 9)
        table.clear(mobileTable, 0, 0, 1, 21)

        g1: str = 'Open' if en else 'Açılış'
        g2: str = 'Close' if en else 'Kapanış'
        g3: str = 'Change' if en else 'Değişim'
        g4: str = 'RSI'
        g5: str = 'ATR'
        g6: str = 'Volume' if en else 'Hacim'
        tOpen: str = string.tostring(math.round_to_mintick(open))
        tClose: str = string.tostring(math.round_to_mintick(close))
        tChg: str = ('▲ ' if chg > 0 else '▼ ' if chg < 0 else '') + string.tostring(math.round_to_mintick(chg)) + '%'
        tRsi: str = string.tostring(math.round_to_mintick(rsi))
        tAtr: str = string.tostring(math.round_to_mintick(atr))
        tVol: str = string.tostring(volume, format.volume)
        stText: str = ('UP' if en else 'YUKARI') if stDir < 0 else 'DOWN' if en else 'AŞAĞI'

        if tableMode == 'Desktop':
            headerCell(deskTable, 0, 0, g1)
            headerCell(deskTable, 1, 0, g2)
            headerCell(deskTable, 2, 0, g3)
            headerCell(deskTable, 3, 0, g4)
            headerCell(deskTable, 4, 0, g5)
            headerCell(deskTable, 5, 0, g6)
            cell(deskTable, 0, 1, tOpen, theme.tableBg)
            cell(deskTable, 1, 1, tClose, theme.tableBg)
            cell(deskTable, 2, 1, tChg, chgBgSeri)
            cell(deskTable, 3, 1, tRsi, rsiBgSeri)
            cell(deskTable, 4, 1, tAtr, theme.tableBg)
            cell(deskTable, 5, 1, tVol, volBgSeri)
            headerCell(deskTable, 0, 2, 'SMA' + string.tostring(sma1))
            headerCell(deskTable, 1, 2, 'SMA' + string.tostring(sma2))
            headerCell(deskTable, 2, 2, 'SMA' + string.tostring(sma3))
            headerCell(deskTable, 3, 2, 'EMA' + string.tostring(ema1))
            headerCell(deskTable, 4, 2, 'EMA' + string.tostring(ema2))
            headerCell(deskTable, 5, 2, 'EMA' + string.tostring(ema3))
            cell(deskTable, 0, 3, string.tostring(math.round_to_mintick(sma50)), maColor(sma50))
            cell(deskTable, 1, 3, string.tostring(math.round_to_mintick(sma100)), maColor(sma100))
            cell(deskTable, 2, 3, string.tostring(math.round_to_mintick(sma200)), maColor(sma200))
            cell(deskTable, 3, 3, string.tostring(math.round_to_mintick(ema50)), maColor(ema50))
            cell(deskTable, 4, 3, string.tostring(math.round_to_mintick(ema100)), maColor(ema100))
            cell(deskTable, 5, 3, string.tostring(math.round_to_mintick(ema200)), maColor(ema200))
            headerCell(deskTable, 0, 4, 'ADX')
            headerCell(deskTable, 1, 4, 'MOM')
            headerCell(deskTable, 2, 4, 'MACD')
            headerCell(deskTable, 3, 4, '+DI/-DI')
            headerCell(deskTable, 4, 4, 'Score' if en else 'Skor')
            headerCell(deskTable, 5, 4, 'Regime' if en else 'Rejim')
            cell(deskTable, 0, 5, string.tostring(math.round_to_mintick(adx)), adxBgSeri)
            cell(deskTable, 1, 5, string.tostring(math.round_to_mintick(mom)), theme.bull if mom >= 0 else theme.bear)
            cell(deskTable, 2, 5, string.tostring(math.round(macdLine, 4)), theme.bull if macdLine >= signalLine else theme.bear)
            cell(deskTable, 3, 5, string.tostring(math.round_to_mintick(diplus)) + '/' + string.tostring(math.round_to_mintick(diminus)), theme.bull if diplus > diminus else theme.bear)
            cell(deskTable, 4, 5, string.tostring(score), scoreBg)
            cell(deskTable, 5, 5, regimeText, theme.neutral if regimeRange else theme.bull if close > emaRegime else theme.bear)
            headerCell(deskTable, 0, 6, 'Stoch')
            headerCell(deskTable, 1, 6, 'CCI')
            headerCell(deskTable, 2, 6, 'MFI')
            headerCell(deskTable, 3, 6, '%R')
            headerCell(deskTable, 4, 6, 'OBV')
            headerCell(deskTable, 5, 6, 'VWAP')
            cell(deskTable, 0, 7, string.tostring(math.round_to_mintick(stochK)), theme.bear if stochK > 80 else theme.bull if stochK < 20 else theme.tableBg)
            cell(deskTable, 1, 7, string.tostring(math.round_to_mintick(cci)), theme.bear if cci > 100 else theme.bull if cci < -100 else theme.tableBg)
            cell(deskTable, 2, 7, string.tostring(math.round_to_mintick(mfi)), theme.bear if mfi > 80 else theme.bull if mfi < 20 else theme.tableBg)
            cell(deskTable, 3, 7, string.tostring(math.round_to_mintick(wpr)), theme.bear if wpr > -20 else theme.bull if wpr < -80 else theme.tableBg)
            cell(deskTable, 4, 7, string.tostring(obv, format.volume), theme.tableBg)
            cell(deskTable, 5, 7, string.tostring(math.round_to_mintick(vwapVal)), theme.bull if close >= vwapVal else theme.bear)
            headerCell(deskTable, 0, 8, 'ST')
            headerCell(deskTable, 1, 8, 'RelVol')
            headerCell(deskTable, 2, 8, 'HVN')
            headerCell(deskTable, 3, 8, 'Chop')
            headerCell(deskTable, 4, 8, 'SAR')
            headerCell(deskTable, 5, 8, 'Hist')
            cell(deskTable, 0, 9, stText, theme.bull if stDir < 0 else theme.bear)
            cell(deskTable, 1, 9, string.tostring(math.round(relVol, 2)) + 'x', volBgSeri)
            cell(deskTable, 2, 9, string.tostring(math.round_to_mintick(hvnPrice)), theme.tableBg)
            cell(deskTable, 3, 9, string.tostring(math.round_to_mintick(chop)), theme.neutral if chop > 61.8 else theme.bull)
            cell(deskTable, 4, 9, string.tostring(math.round_to_mintick(out)), theme.bull if close >= out else theme.bear)
            cell(deskTable, 5, 9, string.tostring(math.round(histLine, 4)), theme.bull if histLine >= 0 else theme.bear)

        if tableMode == 'Mobile':
            headerCell(mobileTable, 0, 0, g1)
            cell(mobileTable, 1, 0, tOpen, theme.tableBg)
            headerCell(mobileTable, 0, 1, g2)
            cell(mobileTable, 1, 1, tClose, theme.tableBg)
            headerCell(mobileTable, 0, 2, g3)
            cell(mobileTable, 1, 2, tChg, chgBgSeri)
            headerCell(mobileTable, 0, 3, g4)
            cell(mobileTable, 1, 3, tRsi, rsiBgSeri)
            headerCell(mobileTable, 0, 4, 'Score' if en else 'Skor')
            cell(mobileTable, 1, 4, string.tostring(score), scoreBg)
            headerCell(mobileTable, 0, 5, 'Regime' if en else 'Rejim')
            cell(mobileTable, 1, 5, regimeText, theme.neutral if regimeRange else theme.bull if close > emaRegime else theme.bear)
            headerCell(mobileTable, 0, 6, 'SMA' + string.tostring(sma1))
            cell(mobileTable, 1, 6, string.tostring(math.round_to_mintick(sma50)), maColor(sma50))
            headerCell(mobileTable, 0, 7, 'EMA' + string.tostring(ema1))
            cell(mobileTable, 1, 7, string.tostring(math.round_to_mintick(ema50)), maColor(ema50))
            headerCell(mobileTable, 0, 8, 'ADX')
            cell(mobileTable, 1, 8, string.tostring(math.round_to_mintick(adx)), adxBgSeri)
            headerCell(mobileTable, 0, 9, 'MACD')
            cell(mobileTable, 1, 9, string.tostring(math.round(macdLine, 4)), theme.bull if macdLine >= signalLine else theme.bear)
            headerCell(mobileTable, 0, 10, 'Stoch')
            cell(mobileTable, 1, 10, string.tostring(math.round_to_mintick(stochK)), theme.bear if stochK > 80 else theme.bull if stochK < 20 else theme.tableBg)
            headerCell(mobileTable, 0, 11, 'CCI')
            cell(mobileTable, 1, 11, string.tostring(math.round_to_mintick(cci)), theme.tableBg)
            headerCell(mobileTable, 0, 12, 'MFI')
            cell(mobileTable, 1, 12, string.tostring(math.round_to_mintick(mfi)), theme.tableBg)
            headerCell(mobileTable, 0, 13, '%R')
            cell(mobileTable, 1, 13, string.tostring(math.round_to_mintick(wpr)), theme.tableBg)
            headerCell(mobileTable, 0, 14, 'VWAP')
            cell(mobileTable, 1, 14, string.tostring(math.round_to_mintick(vwapVal)), theme.bull if close >= vwapVal else theme.bear)
            headerCell(mobileTable, 0, 15, 'ST')
            cell(mobileTable, 1, 15, stText, theme.bull if stDir < 0 else theme.bear)
            headerCell(mobileTable, 0, 16, 'RelVol')
            cell(mobileTable, 1, 16, string.tostring(math.round(relVol, 2)) + 'x', volBgSeri)
            headerCell(mobileTable, 0, 17, 'HVN')
            cell(mobileTable, 1, 17, string.tostring(math.round_to_mintick(hvnPrice)), theme.tableBg)
            headerCell(mobileTable, 0, 18, 'Chop')
            cell(mobileTable, 1, 18, string.tostring(math.round_to_mintick(chop)), theme.tableBg)
            headerCell(mobileTable, 0, 19, 'OBV')
            cell(mobileTable, 1, 19, string.tostring(obv, format.volume), theme.tableBg)
            headerCell(mobileTable, 0, 20, g6)
            cell(mobileTable, 1, 20, tVol, volBgSeri)
            headerCell(mobileTable, 0, 21, 'MOM')
            cell(mobileTable, 1, 21, string.tostring(math.round_to_mintick(mom)), theme.bull if mom >= 0 else theme.bear)

    alertcondition(rsi >= 70, title='RSI >= 70', message='RSI overbought')
    alertcondition(rsi <= 30, title='RSI <= 30', message='RSI oversold')
    alertcondition(ta.crossover(macdLine, signalLine), title='MACD cross up', message='MACD bullish cross')
    alertcondition(ta.crossunder(macdLine, signalLine), title='MACD cross down', message='MACD bearish cross')
    alertcondition(ta.crossover(close, emaRegime), title='Close x EMA200 up', message='Price crossed above EMA200')
    alertcondition(ta.crossunder(close, emaRegime), title='Close x EMA200 down', message='Price crossed below EMA200')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
