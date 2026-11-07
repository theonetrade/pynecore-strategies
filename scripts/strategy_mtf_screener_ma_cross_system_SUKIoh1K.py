"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barmerge, close, color, display, fill, input, label,
    math, na, nz, plot, position, request, script, size, strategy, string, syminfo, ta, table,
    text
)
from pynecore.types import Color, Persistent, Table

uiGroup: str = "UI CONFIGURATION"
maGroup: str = "MOVING AVERAGE SETTINGS"
crossGroup: str = "CROSS MODE SETTINGS"
htfGroup: str = "HIGHER TIMEFRAME FILTER"
tmGroup: str = "TRADE MANAGEMENT"
riskGroup: str = "RISK SETTINGS"
gr_sy: str = "Multi Symbol Screener"


@script.strategy("MTF Screener MA Cross System", shorttitle='MTF Screener MA Cross System [yigdeli] 1.0.2', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main(
    tablePosInput=input.string("Middle Right", "Table Position", options=("Top Right", "Middle Right", "Bottom Right", "Top Left", "Middle Left", "Bottom Left"), group=uiGroup, tooltip="EN: Defines where the table will appear on the chart.\nTR: Tablonun grafikte hangi konumda görüneceğini belirler."),
    tableSize=input.string("Normal", "Table Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=uiGroup, tooltip="EN: Adjusts the table text size.\nTR: Tablodaki yazı boyutunu ayarlar."),
    fastLen=input.int(9, "Fast MA Length     ", group=maGroup, inline="fast", tooltip="EN: Short-term momentum moving average.\nTR: Kısa vadeli momentum ortalaması."),
    fastBullColorInput=input.color(color.new(color.new('#005446'), 70), "", group=maGroup, inline="fast"),
    fastBearColorInput=input.color(color.new(color.new('#FF4D6D'), 70), "", group=maGroup, inline="fast"),
    mediumLen=input.int(27, "Medium MA Length", group=maGroup, inline="medium", tooltip="EN: Medium-term trend filter.\nTR: Orta vadeli trend filtresi."),
    mediumBullColorInput=input.color(color.new(color.new('#005446'), 70), "", group=maGroup, inline="medium"),
    mediumBearColorInput=input.color(color.new(color.new('#FF4D6D'), 70), "", group=maGroup, inline="medium"),
    slowLen=input.int(200, "Slow MA Length     ", group=maGroup, inline="slow", tooltip="EN: Primary structural trend moving average.\nTR: Ana yapısal trend ortalaması."),
    slowBullColorInput=input.color(color.new(color.new('#005446'), 70), "", group=maGroup, inline="slow"),
    slowBearColorInput=input.color(color.new(color.new('#FF4D6D'), 70), "", group=maGroup, inline="slow"),
    crossMode=input.string("Fast", "Cross Mode", options=("Fast", "Medium", "Slow"), group=crossGroup, tooltip="Fast: Fast vs Medium\nMedium: Fast vs Slow\nSlow: Medium vs Slow"),
    bullBase=input.color(color.new(color.new('#00FF88'), 10), "Bull Gradient ", group=crossGroup, inline="bullg"),
    bearBase=input.color(color.new(color.new('#FF3366'), 10), "Bear Gradient", group=crossGroup, inline="bearg"),
    blueLight=input.color(color.new(color.new('#0D47A1'), 10), "Neutral Gradient", group=crossGroup, inline="bullg"),
    blueDark=input.color(color.new(color.new('#0D47A1'), 10), "Neutral Gradient", group=crossGroup, inline="bearg"),
    htfTF=input.timeframe("240", "Higher Timeframe", group=htfGroup, tooltip="EN: Higher timeframe used for trend confirmation.\nTR: Trend doğrulaması için kullanılacak üst zaman dilimi."),
    htfLen=input.int(200, "HTF Slow Length", group=htfGroup, tooltip="EN: Period of the main trend moving average on the higher timeframe.\nTR: Üst zaman dilimindeki ana trend ortalaması periyodu."),
    managementMode=input.string("Basic", "Trade Management Mode", options=("Basic", "BreakEven", "Partial + BE", "Advanced"), group=tmGroup, tooltip="EN: Basic: Fixed SL/TP.\nBreakEven: Moves stop to entry when RR is reached.\nPartial + BE: Partial close with break-even.\nAdvanced: Partial + break-even + trailing stop.\nTR: Basic: Sabit SL/TP.\nBreakEven: RR ulaşıldığında stop girişe taşınır.\nPartial + BE: Kısmi kapama + BE.\nAdvanced: Kısmi + BE + trailing stop."),
    beRR=input.float(1.0, "BreakEven RR Trigger", step=0.1, group=tmGroup, tooltip="EN: Risk/Reward level that triggers break-even adjustment.\nTR: BreakEven tetikleme risk/ödül oranı."),
    partialRR=input.float(1.5, "Partial Close RR Trigger", step=0.1, group=tmGroup, tooltip="EN: Risk/Reward level that triggers partial position close.\nTR: Kısmi pozisyon kapama tetikleme RR değeri."),
    partialPercent=input.float(50, "Partial Close %", step=1, group=tmGroup, tooltip="EN: Percentage of position size to close during partial exit.\nTR: Kısmi kapamada kapanacak pozisyon yüzdesi."),
    trailATRmult=input.float(1.0, "Trailing ATR Multiplier", step=0.1, group=tmGroup, tooltip="EN: ATR multiplier used for trailing stop in Advanced mode.\nTR: Advanced modda trailing stop için ATR çarpanı."),
    riskMode=input.string("Percent", "Risk Mode", options=("Percent", "ATR"), group=riskGroup, tooltip="EN: Method used to calculate Stop Loss and Take Profit levels.\nATR: Volatility-based calculation.\nPercent: Fixed percentage-based calculation.\nTR: Stop ve Take Profit hesaplama yöntemi.\nATR: Volatilite bazlı.\nPercent: Sabit yüzde bazlı."),
    userSLpct=input.float(2.0, "Stop %", step=0.1, group=riskGroup, tooltip="EN: Stop percentage used when Percent mode is active.\nTR: Percent modu aktifken kullanılacak stop yüzdesi."),
    userTPpct=input.float(4.0, "Take Profit %", step=0.1, group=riskGroup, tooltip="EN: Take profit percentage used when Percent mode is active.\nTR: Percent modu aktifken kullanılacak kar alma yüzdesi."),
    atrLen=input.int(14, "ATR Length", group=riskGroup, tooltip="EN: ATR period used for volatility calculation.\nTR: ATR periyodu. Volatilite hesaplamasında kullanılır."),
    riskRR=input.float(2.0, "Risk Reward", group=riskGroup, tooltip="EN: Risk/Reward ratio used in ATR mode.\nTR: ATR modunda risk/ödül oranı."),
    atrMult=input.float(1.5, "ATR Stop Multiplier", group=riskGroup, tooltip="EN: Multiplier that defines stop distance in ATR mode.\nTR: ATR modunda stop mesafesini belirleyen çarpan."),
    sh01=input.bool(True, "01", group=gr_sy, inline="01"),
    sh02=input.bool(True, "02", group=gr_sy, inline="02"),
    sh03=input.bool(True, "03", group=gr_sy, inline="03"),
    sh04=input.bool(True, "04", group=gr_sy, inline="04"),
    sh05=input.bool(True, "05", group=gr_sy, inline="05"),
    sh06=input.bool(True, "06", group=gr_sy, inline="06"),
    sh07=input.bool(True, "07", group=gr_sy, inline="07"),
    sh08=input.bool(True, "08", group=gr_sy, inline="08"),
    sh09=input.bool(True, "09", group=gr_sy, inline="09"),
    sh10=input.bool(True, "10", group=gr_sy, inline="10"),
    tf01=input.timeframe("60", "", group=gr_sy, inline="01"),
    tf02=input.timeframe("60", "", group=gr_sy, inline="02"),
    tf03=input.timeframe("60", "", group=gr_sy, inline="03"),
    tf04=input.timeframe("60", "", group=gr_sy, inline="04"),
    tf05=input.timeframe("60", "", group=gr_sy, inline="05"),
    tf06=input.timeframe("60", "", group=gr_sy, inline="06"),
    tf07=input.timeframe("60", "", group=gr_sy, inline="07"),
    tf08=input.timeframe("60", "", group=gr_sy, inline="08"),
    tf09=input.timeframe("60", "", group=gr_sy, inline="09"),
    tf10=input.timeframe("60", "", group=gr_sy, inline="10"),
    s01=input.symbol("BIST:ASELS", "", group=gr_sy, inline="01"),
    s02=input.symbol("BIST:THYAO", "", group=gr_sy, inline="02"),
    s03=input.symbol("BINANCE:BTCUSDT.P", "", group=gr_sy, inline="03"),
    s04=input.symbol("BINANCE:ETHUSDT.P", "", group=gr_sy, inline="04"),
    s05=input.symbol("BINANCE:XRPUSDT.P", "", group=gr_sy, inline="05"),
    s06=input.symbol("BINANCE:DOGEUSDT.P", "", group=gr_sy, inline="06"),
    s07=input.symbol("BINANCE:AVAXUSDT.P", "", group=gr_sy, inline="07"),
    s08=input.symbol("NASDAQ:TSLA", "", group=gr_sy, inline="08"),
    s09=input.symbol("BIST:PGSUS", "", group=gr_sy, inline="09"),
    s10=input.symbol("BINANCE:USDTTRY", "", group=gr_sy, inline="10")
):
    txtSize = size.tiny if tableSize == 'Tiny' else size.small if tableSize == 'Small' else size.large if tableSize == 'Large' else size.huge if tableSize == 'Huge' else size.normal

    tablePos = position.top_right if tablePosInput == 'Top Right' else position.middle_right if tablePosInput == 'Middle Right' else position.bottom_right if tablePosInput == 'Bottom Right' else position.top_left if tablePosInput == 'Top Left' else position.middle_left if tablePosInput == 'Middle Left' else position.bottom_left




    fastMA = ta.ema(close, fastLen)
    mediumMA = ta.ema(close, mediumLen)
    slowMA = ta.hma(close, slowLen)

    __block_result__ = na
    __switch__ = crossMode
    if __switch__ == "Fast":
        __block_result__ = fastMA
    elif __switch__ == "Medium":
        __block_result__ = fastMA
    elif __switch__ == "Slow":
        __block_result__ = mediumMA
    shortMA = __block_result__

    __block_result_1__ = na
    __switch__ = crossMode
    if __switch__ == "Fast":
        __block_result_1__ = mediumMA
    elif __switch__ == "Medium":
        __block_result_1__ = slowMA
    elif __switch__ == "Slow":
        __block_result_1__ = slowMA
    longMA = __block_result_1__

    golden = ta.crossover(shortMA, longMA)
    death = ta.crossunder(shortMA, longMA)

    fastActive: bool = crossMode == 'Fast' or crossMode == 'Medium'
    mediumActive: bool = crossMode == 'Fast' or crossMode == 'Slow'
    slowActive: bool = crossMode == 'Medium' or crossMode == 'Slow'

    bull: bool = shortMA > longMA

    bullStrong: Color = fastBullColorInput
    bullMid: Color = mediumBullColorInput
    bullSoft: Color = slowBullColorInput

    bearStrong: Color = fastBearColorInput
    bearMid: Color = mediumBearColorInput
    bearSoft: Color = slowBearColorInput

    plot(fastMA, color=(bullStrong if bull else bearStrong) if fastActive else bullSoft if bull else bearSoft, linewidth=1)

    plot(mediumMA, color=(bullMid if bull else bearMid) if mediumActive else bullSoft if bull else bearSoft, linewidth=1)

    plot(slowMA, color=(bullMid if bull else bearMid) if slowActive else bullSoft if bull else bearSoft, linewidth=1)

    htfSlowMA = request.security(syminfo.tickerid, htfTF, ta.hma(close, htfLen), lookahead=barmerge.lookahead_off)

    trendBull = close > htfSlowMA
    trendBear = close < htfSlowMA

    longCondition = golden and trendBull
    shortCondition = death and trendBear

    if longCondition:
        strategy.entry('Long', strategy.long)

    if shortCondition:
        strategy.entry('Short', strategy.short)

    atr = ta.atr(atrLen)

    longSL = strategy.position_avg_price - atr * atrMult if riskMode == 'ATR' else strategy.position_avg_price * (1 - userSLpct / 100)

    longTP = strategy.position_avg_price + atr * atrMult * riskRR if riskMode == 'ATR' else strategy.position_avg_price * (1 + userTPpct / 100)

    shortSL = strategy.position_avg_price + atr * atrMult if riskMode == 'ATR' else strategy.position_avg_price * (1 + userSLpct / 100)

    shortTP = strategy.position_avg_price - atr * atrMult * riskRR if riskMode == 'ATR' else strategy.position_avg_price * (1 - userTPpct / 100)

    entryPrice = strategy.position_avg_price
    posSize = strategy.position_size

    breakEvenActivated: Persistent[bool] = False
    partialTaken: Persistent[bool] = False

    longRisk = nz(entryPrice - longSL, 0.0)
    shortRisk = nz(shortSL - entryPrice, 0.0)

    denLong = math.max(longRisk, syminfo.mintick)
    denShort = math.max(shortRisk, syminfo.mintick)

    currentRR = (close - entryPrice) / denLong if posSize > 0 else (entryPrice - close) / denShort if posSize < 0 else 0

    if strategy.position_size == 0:
        breakEvenActivated = False
        partialTaken = False

    if managementMode == 'Basic':
        if posSize > 0:
            strategy.exit('Long Exit', from_entry='Long', stop=longSL, limit=longTP)
        if posSize < 0:
            strategy.exit('Short Exit', from_entry='Short', stop=shortSL, limit=shortTP)

    if managementMode == 'BreakEven':
        if not breakEvenActivated and currentRR >= beRR:
            breakEvenActivated = True

        beStopLong = entryPrice if breakEvenActivated else longSL
        beStopShort = entryPrice if breakEvenActivated else shortSL

        if posSize > 0:
            strategy.exit('Long Exit', from_entry='Long', stop=beStopLong, limit=longTP)
        if posSize < 0:
            strategy.exit('Short Exit', from_entry='Short', stop=beStopShort, limit=shortTP)

    if managementMode == 'Partial + BE':
        if not partialTaken and currentRR >= partialRR:
            strategy.close('Long', qty_percent=partialPercent)
            strategy.close('Short', qty_percent=partialPercent)
            partialTaken = True
            breakEvenActivated = True

        beStopLong = entryPrice if breakEvenActivated else longSL
        beStopShort = entryPrice if breakEvenActivated else shortSL

        if posSize > 0:
            strategy.exit('Long Exit', from_entry='Long', stop=beStopLong, limit=longTP)
        if posSize < 0:
            strategy.exit('Short Exit', from_entry='Short', stop=beStopShort, limit=shortTP)

    if managementMode == 'Advanced':
        if not partialTaken and currentRR >= partialRR:
            strategy.close('Long', qty_percent=partialPercent)
            strategy.close('Short', qty_percent=partialPercent)
            partialTaken = True
            breakEvenActivated = True

        trailLong = close - atr * trailATRmult
        trailShort = close + atr * trailATRmult

        finalStopLong = math.max(entryPrice, trailLong) if breakEvenActivated else longSL
        finalStopShort = math.min(entryPrice, trailShort) if breakEvenActivated else shortSL

        if posSize > 0:
            strategy.exit('Long Exit', from_entry='Long', stop=finalStopLong, limit=longTP)

        if posSize < 0:
            strategy.exit('Short Exit', from_entry='Short', stop=finalStopShort, limit=shortTP)

    if golden:
        label.new(bar_index, shortMA, '▲', style=label.style_label_up, color=color.new(color.new('#089981'), 40), textcolor=color.new('#00FFD5'))

    if death:
        label.new(bar_index, shortMA, '▼', style=label.style_label_down, color=color.new(color.new('#F23645'), 40), textcolor=color.new('#FD5F5F'))

    def f_screener(_enabled):
        __block_result_2__ = (na, na, na, na, na)
        if not _enabled:
            __block_result_2__ = (na, na, na, na, color.gray)
        else:
            fastMA_l = ta.ema(close, fastLen)
            mediumMA_l = ta.ema(close, mediumLen)
            slowMA_l = ta.hma(close, slowLen)

            __block_result_3__ = na
            __switch_1__ = crossMode
            if __switch_1__ == "Fast":
                __block_result_3__ = fastMA_l
            elif __switch_1__ == "Medium":
                __block_result_3__ = fastMA_l
            elif __switch_1__ == "Slow":
                __block_result_3__ = mediumMA_l
            short_l = __block_result_3__

            __block_result_4__ = na
            __switch_1__ = crossMode
            if __switch_1__ == "Fast":
                __block_result_4__ = mediumMA_l
            elif __switch_1__ == "Medium":
                __block_result_4__ = slowMA_l
            elif __switch_1__ == "Slow":
                __block_result_4__ = slowMA_l
            long_l = __block_result_4__

            golden__00000095__ = ta.crossover(short_l, long_l)
            death__00000095__ = ta.crossunder(short_l, long_l)

            lg = ta.barssince(golden__00000095__)
            ld = ta.barssince(death__00000095__)

            trend = 1 if lg < ld else -1 if ld < lg else 0
            bars = lg if trend == 1 else ld if trend == -1 else na

            atr_l = ta.atr(14)
            strength = math.abs(short_l - long_l) / atr_l
            dailyPct = (close / close[1] - 1) * 100

            col = color.new('#00C3A3') if trend == 1 else color.new('#F23645') if trend == -1 else color.silver

            __block_result_2__ = (trend, bars, strength, dailyPct, col)
        return __block_result_2__

    a01, b01, s01p, d01, c01 = request.security(s01, tf01, f_screener(sh01))
    a02, b02, s02p, d02, c02 = request.security(s02, tf02, f_screener(sh02))
    a03, b03, s03p, d03, c03 = request.security(s03, tf03, f_screener(sh03))
    a04, b04, s04p, d04, c04 = request.security(s04, tf04, f_screener(sh04))
    a05, b05, s05p, d05, c05 = request.security(s05, tf05, f_screener(sh05))
    a06, b06, s06p, d06, c06 = request.security(s06, tf06, f_screener(sh06))
    a07, b07, s07p, d07, c07 = request.security(s07, tf07, f_screener(sh07))
    a08, b08, s08p, d08, c08 = request.security(s08, tf08, f_screener(sh08))
    a09, b09, s09p, d09, c09 = request.security(s09, tf09, f_screener(sh09))
    a10, b10, s10p, d10, c10 = request.security(s10, tf10, f_screener(sh10))

    screener: Persistent[Table] = table.new(tablePos, 6, 30, border_width=3)

    bullCount: int = 0
    totalCount: int = 0

    for i in pine_range(0, 9):
        sh = sh01 if i == 0 else sh02 if i == 1 else sh03 if i == 2 else sh04 if i == 3 else sh05 if i == 4 else sh06 if i == 5 else sh07 if i == 6 else sh08 if i == 7 else sh09 if i == 8 else sh10
        if sh:
            tr = a01 if i == 0 else a02 if i == 1 else a03 if i == 2 else a04 if i == 3 else a05 if i == 4 else a06 if i == 5 else a07 if i == 6 else a08 if i == 7 else a09 if i == 8 else a10
            if tr == 1:
                bullCount += 1
            totalCount += 1

    alignScore = bullCount / totalCount * 100 if totalCount > 0 else 0
    filledBlocks = math.round(alignScore / 10)
    heatBar: str = ""
    for i in pine_range(0, 9):
        heatBar += '█' if i < filledBlocks else '░'

    activeText = string.tostring(bullCount) + ' / ' + string.tostring(totalCount)
    headerBlue = color.new(color.rgb(25, 55, 110), 40)

    table.cell(screener, 0, 1, 'SYMBOL', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 1, 1, 'TF', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 2, 1, '▲|▼', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 3, 1, 'BARS', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 4, 1, 'STRENGTH', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 5, 1, 'DAILY %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)

    row_index: int = 2

    for i in pine_range(0, 9):
        sh = sh01 if i == 0 else sh02 if i == 1 else sh03 if i == 2 else sh04 if i == 3 else sh05 if i == 4 else sh06 if i == 5 else sh07 if i == 6 else sh08 if i == 7 else sh09 if i == 8 else sh10
        tfv = tf01 if i == 0 else tf02 if i == 1 else tf03 if i == 2 else tf04 if i == 3 else tf05 if i == 4 else tf06 if i == 5 else tf07 if i == 6 else tf08 if i == 7 else tf09 if i == 8 else tf10
        sym = s01 if i == 0 else s02 if i == 1 else s03 if i == 2 else s04 if i == 3 else s05 if i == 4 else s06 if i == 5 else s07 if i == 6 else s08 if i == 7 else s09 if i == 8 else s10
        val = a01 if i == 0 else a02 if i == 1 else a03 if i == 2 else a04 if i == 3 else a05 if i == 4 else a06 if i == 5 else a07 if i == 6 else a08 if i == 7 else a09 if i == 8 else a10
        bars = b01 if i == 0 else b02 if i == 1 else b03 if i == 2 else b04 if i == 3 else b05 if i == 4 else b06 if i == 5 else b07 if i == 6 else b08 if i == 7 else b09 if i == 8 else b10
        strn = s01p if i == 0 else s02p if i == 1 else s03p if i == 2 else s04p if i == 3 else s05p if i == 4 else s06p if i == 5 else s07p if i == 6 else s08p if i == 7 else s09p if i == 8 else s10p
        dly = d01 if i == 0 else d02 if i == 1 else d03 if i == 2 else d04 if i == 3 else d05 if i == 4 else d06 if i == 5 else d07 if i == 6 else d08 if i == 7 else d09 if i == 8 else d10

        if sh:
            parts = string.split(sym, ':')
            shortSym = array.get(parts, array.size(parts) - 1)
            partsDot = string.split(shortSym, '.')
            shortSym = array.get(partsDot, 0)

            trendBg = color.new(color.new('#089981'), 75) if val == 1 else color.new(color.new('#F23645'), 75) if val == -1 else color.new(color.gray, 85)

            trendText = color.new('#00C3A3') if val == 1 else color.new('#F23645') if val == -1 else color.white

            dailyBg = color.new(color.new('#089981'), 70) if dly >= 0 else color.new(color.new('#F23645'), 70)

            dailyText = color.new('#00C3A3') if dly >= 0 else color.new('#F23645')

            table.cell(screener, 0, row_index, shortSym, bgcolor=color.new(color.blue, 80), text_color=color.blue, text_size=txtSize)
            table.cell(screener, 1, row_index, tfv, bgcolor=trendBg, text_color=trendText, text_size=txtSize)
            table.cell(screener, 2, row_index, '▲' if val == 1 else '▼' if val == -1 else 'NEUTRAL', bgcolor=trendBg, text_color=trendText, text_size=txtSize)
            table.cell(screener, 3, row_index, string.tostring(bars), bgcolor=trendBg, text_color=trendText, text_size=txtSize)
            table.cell(screener, 4, row_index, string.tostring(math.round(strn, 2)), bgcolor=trendBg, text_color=trendText, text_size=txtSize)
            table.cell(screener, 5, row_index, string.tostring(math.round(dly, 2)) + '%', bgcolor=dailyBg, text_color=dailyText, text_size=txtSize)

            row_index += 1

    biasTextColor = color.new('#00C3A3') if bullCount > totalCount / 2 else color.new('#F23645') if bullCount < totalCount / 2 else color.yellow

    lastRow = row_index

    biasText = 'Market Bias   ' + heatBar
    alignText = 'Score ' + string.tostring(math.round(alignScore)) + ' % | ' + activeText

    table.cell(screener, 0, lastRow, biasText, bgcolor=headerBlue, text_color=biasTextColor, text_size=txtSize)
    table.merge_cells(screener, 0, lastRow, 3, lastRow)

    table.cell(screener, 4, lastRow, alignText, bgcolor=headerBlue, text_color=biasTextColor, text_size=txtSize)
    table.merge_cells(screener, 4, lastRow, 5, lastRow)

    openPct = (close - entryPrice) / entryPrice * 100 if posSize > 0 else (entryPrice - close) / entryPrice * 100 if posSize < 0 else na

    riskPct = math.abs(entryPrice - (longSL if posSize > 0 else shortSL)) / entryPrice * 100 if posSize != 0 else na

    slDistPct = (close - longSL) / close * 100 if posSize > 0 else (shortSL - close) / close * 100 if posSize < 0 else na

    tpPrice = longTP if posSize > 0 else shortTP

    rrProgress = (close - entryPrice) / (tpPrice - entryPrice) * 100 if posSize > 0 else (entryPrice - close) / (entryPrice - tpPrice) * 100 if posSize < 0 else na

    riskHeaderRow = lastRow + 1
    riskValueRow = lastRow + 2

    def f_getScaleColor(_value):
        _v = math.max(math.min(_value, 100), 0)
        colorOut = color.new('#00FF88') if _v >= 90 else color.new('#00DD77') if _v >= 80 else color.new('#22CC66') if _v >= 70 else color.new('#55BB55') if _v >= 60 else color.new('#88AA44') if _v >= 50 else color.new('#CC9933') if _v >= 40 else color.new('#DD7722') if _v >= 30 else color.new('#EE5511') if _v >= 20 else color.new('#FF3300') if _v >= 10 else color.new('#990000')
        return colorOut

    rrNorm = math.min(math.max(rrProgress, 0), 100) if posSize != 0 else 0
    rrScaled = math.round(rrNorm / 10) * 10
    rrColor = f_getScaleColor(rrScaled)

    slNorm = math.min(slDistPct / riskPct * 100, 100) if posSize != 0 and riskPct > 0 else 0
    slScaled = math.round(slNorm / 10) * 10
    slColor = f_getScaleColor(slScaled)

    riskNorm = math.max(100 - riskPct * 12, 0) if posSize != 0 else 0
    riskScaled = math.round(riskNorm / 10) * 10
    riskColor = f_getScaleColor(riskScaled)

    alignScorePart = math.min(alignScore, 100) * 0.4

    strengthNorm = math.min(math.abs(shortMA - longMA) / atr, 2)
    strengthPart = math.min(strengthNorm / 2 * 25, 25)

    rrPart = rrNorm * 0.25 if posSize != 0 else 0
    riskPenalty = math.min(riskPct * 5, 20) if posSize != 0 else 0

    edgeRaw = alignScorePart + strengthPart + rrPart - riskPenalty
    edgeScore = math.max(math.min(edgeRaw, 100), 0)
    edgeScaled = math.round(edgeScore / 10) * 10
    edgeColor = f_getScaleColor(edgeScaled)

    table.cell(screener, 0, riskHeaderRow, 'POSITION', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 1, riskHeaderRow, 'OPEN %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 2, riskHeaderRow, 'RISK %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 3, riskHeaderRow, 'SL DIST', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 4, riskHeaderRow, 'RR %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 5, riskHeaderRow, 'EDGE', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)

    posText = 'LONG' if posSize > 0 else 'SHORT' if posSize < 0 else 'FLAT'

    posColor = color.new('#00C3A3') if posSize > 0 else color.new('#F23645') if posSize < 0 else color.gray

    table.cell(screener, 0, riskValueRow, posText, bgcolor=color.new(posColor, 80), text_color=posColor, text_size=txtSize)

    table.cell(screener, 1, riskValueRow, string.tostring(math.round(openPct, 2)) + '%' if posSize != 0 else '—', bgcolor=color.new(color.new('#089981') if openPct >= 0 else color.new('#F23645'), 80) if posSize != 0 else headerBlue, text_color=posColor, text_size=txtSize)

    table.cell(screener, 2, riskValueRow, string.tostring(math.round(riskPct, 2)) + '%' if posSize != 0 else '—', bgcolor=color.new(riskColor, 70), text_color=posColor, text_size=txtSize)

    table.cell(screener, 3, riskValueRow, string.tostring(math.round(slDistPct, 2)) + '%' if posSize != 0 else '—', bgcolor=color.new(slColor, 70), text_color=posColor, text_size=txtSize)

    table.cell(screener, 4, riskValueRow, string.tostring(math.round(rrProgress, 1)) + '%' if posSize != 0 else '—', bgcolor=color.new(rrColor, 70), text_color=posColor, text_size=txtSize)

    table.cell(screener, 5, riskValueRow, string.tostring(edgeScaled) + '%', bgcolor=color.new(edgeColor, 70), text_color=posColor, text_size=txtSize)

    perfTitleRow = riskValueRow + 2
    perfHeaderRow = riskValueRow + 3
    perfValueRow = riskValueRow + 4

    table.cell(screener, 0, perfTitleRow, 'STRATEGY PERFORMANCE DASHBOARD', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize, text_halign=text.align_center)

    table.merge_cells(screener, 0, perfTitleRow, 5, perfTitleRow)

    netProfitPct = strategy.netprofit / strategy.initial_capital * 100
    winRate = strategy.wintrades / strategy.closedtrades * 100 if strategy.closedtrades > 0 else 0
    totalTrades = strategy.closedtrades
    profitFactor = strategy.grossprofit / math.abs(strategy.grossloss) if strategy.grossloss != 0 else 0
    maxDDpct = strategy.max_drawdown / strategy.initial_capital * 100

    avgWin = strategy.grossprofit / strategy.wintrades if strategy.wintrades > 0 else 0

    avgLoss = math.abs(strategy.grossloss) / strategy.losstrades if strategy.losstrades > 0 else 0

    lossRate = 100 - winRate

    expectancy = winRate / 100 * avgWin - lossRate / 100 * avgLoss

    expectancyPct = expectancy / strategy.initial_capital * 100 if strategy.initial_capital != 0 else 0

    table.cell(screener, 0, perfHeaderRow, 'NET %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 1, perfHeaderRow, 'WIN %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 2, perfHeaderRow, 'TRADES', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 3, perfHeaderRow, 'PF', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 4, perfHeaderRow, 'MAX DD %', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)
    table.cell(screener, 5, perfHeaderRow, 'EXP', bgcolor=headerBlue, text_color=color.blue, text_size=txtSize)

    table.cell(screener, 0, perfValueRow, string.tostring(math.round(netProfitPct, 2)) + '%', bgcolor=color.new(color.new('#00C3A3') if netProfitPct >= 0 else color.new('#F23645'), 80), text_color=color.new('#00C3A3') if netProfitPct >= 0 else color.new('#F23645'), text_size=txtSize)

    table.cell(screener, 1, perfValueRow, string.tostring(math.round(winRate, 1)) + '%', bgcolor=color.new(color.new('#00C3A3') if winRate >= 50 else color.new('#F23645'), 80), text_color=color.new('#00C3A3') if winRate >= 50 else color.new('#F23645'), text_size=txtSize)

    table.cell(screener, 2, perfValueRow, string.tostring(totalTrades), bgcolor=color.new(color.new('#00C3A3'), 85), text_color=color.new('#00C3A3'), text_size=txtSize)

    table.cell(screener, 3, perfValueRow, string.tostring(math.round(profitFactor, 2)), bgcolor=color.new(color.new('#00C3A3') if profitFactor >= 1 else color.new('#F23645'), 80), text_color=color.new('#00C3A3') if profitFactor >= 1 else color.new('#F23645'), text_size=txtSize)

    table.cell(screener, 4, perfValueRow, string.tostring(math.round(maxDDpct, 2)) + '%', bgcolor=color.new(color.new('#F23645'), 70), text_color=color.new('#F23645'), text_size=txtSize)

    table.cell(screener, 5, perfValueRow, string.tostring(math.round(expectancyPct, 3)) + '%', bgcolor=color.new(color.new('#00C3A3') if expectancyPct >= 0 else color.new('#F23645'), 80), text_color=color.new('#00C3A3') if expectancyPct >= 0 else color.new('#F23645'), text_size=txtSize)

    steps: int = 10

    minMA: float = math.min(fastMA, math.min(mediumMA, slowMA))
    maxMA: float = math.max(fastMA, math.max(mediumMA, slowMA))
    midMA: float = fastMA + mediumMA + slowMA - minMA - maxMA

    activeLower: bool = crossMode == 'Fast' and (fastMA == minMA and mediumMA == midMA or (mediumMA == minMA and fastMA == midMA)) or (crossMode == 'Medium' and (fastMA == minMA and slowMA == midMA or (slowMA == minMA and fastMA == midMA))) or (crossMode == 'Slow' and (mediumMA == minMA and slowMA == midMA or (slowMA == minMA and mediumMA == midMA)))

    l0 = plot(minMA, display=display.none)
    l1 = plot(minMA + (midMA - minMA) * 0.1, display=display.none)
    l2 = plot(minMA + (midMA - minMA) * 0.2, display=display.none)
    l3 = plot(minMA + (midMA - minMA) * 0.3, display=display.none)
    l4 = plot(minMA + (midMA - minMA) * 0.4, display=display.none)
    l5 = plot(minMA + (midMA - minMA) * 0.5, display=display.none)
    l6 = plot(minMA + (midMA - minMA) * 0.6, display=display.none)
    l7 = plot(minMA + (midMA - minMA) * 0.7, display=display.none)
    l8 = plot(minMA + (midMA - minMA) * 0.8, display=display.none)
    l9 = plot(minMA + (midMA - minMA) * 0.9, display=display.none)
    l10 = plot(midMA, display=display.none)

    u0 = plot(midMA, display=display.none)
    u1 = plot(midMA + (maxMA - midMA) * 0.1, display=display.none)
    u2 = plot(midMA + (maxMA - midMA) * 0.2, display=display.none)
    u3 = plot(midMA + (maxMA - midMA) * 0.3, display=display.none)
    u4 = plot(midMA + (maxMA - midMA) * 0.4, display=display.none)
    u5 = plot(midMA + (maxMA - midMA) * 0.5, display=display.none)
    u6 = plot(midMA + (maxMA - midMA) * 0.6, display=display.none)
    u7 = plot(midMA + (maxMA - midMA) * 0.7, display=display.none)
    u8 = plot(midMA + (maxMA - midMA) * 0.8, display=display.none)
    u9 = plot(midMA + (maxMA - midMA) * 0.9, display=display.none)
    u10 = plot(maxMA, display=display.none)

    fill(l0, l1, color.new(bullBase if bull else bearBase, 70) if activeLower else color.new(blueLight if bull else blueDark, 80))
    fill(l1, l2, color.new(bullBase if bull else bearBase, 73) if activeLower else color.new(blueLight if bull else blueDark, 83))
    fill(l2, l3, color.new(bullBase if bull else bearBase, 76) if activeLower else color.new(blueLight if bull else blueDark, 86))
    fill(l3, l4, color.new(bullBase if bull else bearBase, 79) if activeLower else color.new(blueLight if bull else blueDark, 89))
    fill(l4, l5, color.new(bullBase if bull else bearBase, 82) if activeLower else color.new(blueLight if bull else blueDark, 92))
    fill(l5, l6, color.new(bullBase if bull else bearBase, 85) if activeLower else color.new(blueLight if bull else blueDark, 95))
    fill(l6, l7, color.new(bullBase if bull else bearBase, 88) if activeLower else color.new(blueLight if bull else blueDark, 97))
    fill(l7, l8, color.new(bullBase if bull else bearBase, 91) if activeLower else color.new(blueLight if bull else blueDark, 98))
    fill(l8, l9, color.new(bullBase if bull else bearBase, 94) if activeLower else color.new(blueLight if bull else blueDark, 99))
    fill(l9, l10, color.new(bullBase if bull else bearBase, 99) if activeLower else color.new(blueLight if bull else blueDark, 99))

    fill(u0, u1, color.new(blueLight if bull else blueDark, 80) if activeLower else color.new(bullBase if bull else bearBase, 70))
    fill(u1, u2, color.new(blueLight if bull else blueDark, 83) if activeLower else color.new(bullBase if bull else bearBase, 73))
    fill(u2, u3, color.new(blueLight if bull else blueDark, 86) if activeLower else color.new(bullBase if bull else bearBase, 76))
    fill(u3, u4, color.new(blueLight if bull else blueDark, 89) if activeLower else color.new(bullBase if bull else bearBase, 79))
    fill(u4, u5, color.new(blueLight if bull else blueDark, 92) if activeLower else color.new(bullBase if bull else bearBase, 82))
    fill(u5, u6, color.new(blueLight if bull else blueDark, 95) if activeLower else color.new(bullBase if bull else bearBase, 85))
    fill(u6, u7, color.new(blueLight if bull else blueDark, 97) if activeLower else color.new(bullBase if bull else bearBase, 88))
    fill(u7, u8, color.new(blueLight if bull else blueDark, 98) if activeLower else color.new(bullBase if bull else bearBase, 91))
    fill(u8, u9, color.new(blueLight if bull else blueDark, 99) if activeLower else color.new(bullBase if bull else bearBase, 94))
    fill(u9, u10, color.new(blueLight if bull else blueDark, 99) if activeLower else color.new(bullBase if bull else bearBase, 99))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
