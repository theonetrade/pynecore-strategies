"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, barcolor, barstate, close, color, high, hlc3, input, low, math,
    na, nz, open, plot, position, script, size, strategy, string, syminfo, ta, table, time,
    timestamp, volume
)
from pynecore.types import IBPersistent, NA, Persistent, Series, Table


@script.strategy('Strategy Myth-Busting #2 - Braid Filter+ADX+EMA-Trend - [MYN]', max_bars_back=5000, overlay=True, pyramiding=0, initial_capital=20000, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100.0, commission_value=0.075, use_bar_magnifier=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    maType=input.string('EMA', 'MA Type', options=('EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMA', 'SMMA', 'HMA', 'LSMA', 'Kijun', 'McGinley', 'RMA'), group='Braid Filter'),
    Period1=input(3, 'Period 1'),
    Period2=input(7, 'Period 2'),
    Period3=input(14, 'Period 3'),
    PipsMinSepPercent=input(40),
    ema1=input.int(100, minval=1, maxval=300, title='EMA UpTrend', group='EMA Trend Bars'),
    shema=input(True, title='Show EMA Trend is Based On?'),
    len=input(14),
    th=input(20),
    iADXSlope=input.float(3.5, minval=0, maxval=300, title='ADX Slope', step=0.5, group='ADX and DI'),
    useStartPeriodTime=input.bool(True, 'Start', group='Date Range', inline='Start Period'),
    startPeriodTime=input.time(timestamp('1 Jan 2019'), '', group='Date Range', inline='Start Period'),
    useEndPeriodTime=input.bool(True, 'End', group='Date Range', inline='End Period'),
    endPeriodTime=input.time(timestamp('31 Dec 2030'), '', group='Date Range', inline='End Period'),
    tradeDirection=input.string('Long and Short', title='Trade Direction', options=('Long and Short', 'Long Only', 'Short Only'), group='Trade Direction'),
    tp1=input.float(title='Take Profit 1 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 1'),
    q1=input.int(title='% Of Position', defval=3, minval=0, group='Take Profit', inline='Take Profit 1'),
    tp2=input.float(title='Take Profit 2 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 2'),
    q2=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 2'),
    tp3=input.float(title='Take Profit 3 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit', inline='Take Profit 3'),
    q3=input.int(title='% Of Position', defval=100, minval=0, group='Take Profit', inline='Take Profit 3'),
    tp4=input.float(title='Take Profit 4 - Target %', defval=100, minval=0.0, step=0.5, group='Take Profit'),
    __input_22__=input.float(title='Stop Loss (%)', defval=12, minval=0.01, group='Stop Loss'),
    leverage=input.float(1, 'Leverage', step=0.5, group='Leverage'),
    alertSyntaxPrefix=input.string(defval='CRYPTANEX_99FTX_Strategy-Name-Here', title='Alert Syntax Prefix', group='ProfitView Alert Syntax'),
    showDashboard=input.bool(group='Dashboard', title='Show Dashboard', defval=True)
):
    def ma(type, src, len):
        result: float = 0
        if type == 'SMA':
            result = ta.sma(src, len)
        if type == 'EMA':
            result = ta.ema(src, len)
        if type == 'DEMA':
            e = ta.ema(src, len)
            result = 2 * e - ta.ema(e, len)
        if type == 'TEMA':
            e = ta.ema(src, len)
            result = 3 * (e - ta.ema(e, len)) + ta.ema(ta.ema(e, len), len)
        if type == 'WMA':
            result = ta.wma(src, len)
        if type == 'VWMA':
            result = ta.vwma(src, len)
        if type == 'SMMA':
            w: Series = ta.wma(src, len)
            result = ta.sma(src, len) if na(w[1]) else (w[1] * (len - 1) + src) / len
        if type == 'RMA':
            result = ta.rma(src, len)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'LSMA':
            result = ta.linreg(src, len, 0)
        if type == 'Kijun':
            kijun = math.avg(ta.lowest(len), ta.highest(len))
            result = kijun
        if type == 'McGinley':
            mg: Series[float] = 0.0
            mg = ta.ema(src, len) if na(mg[1]) else mg[1] + (src - mg[1]) / (len * math.pow(src / mg[1], 4))
            result = mg
        return result

    ma01 = ma(maType, close, Period1)
    ma02 = ma(maType, open, Period2)
    ma03 = ma(maType, close, Period3)
    max = math.max(math.max(ma01, ma02), ma03)
    min = math.min(math.min(ma01, ma02), ma03)
    dif = max - min
    filter = ta.atr(14) * PipsMinSepPercent / 100
    BraidColor = color.green if ma01 > ma02 and dif > filter else color.red if ma02 > ma01 and dif > filter else color.gray
    entryBbraidFilterGreenBar = BraidColor == color.green
    entryBraidFilterRedBar = BraidColor == color.red
    usedEma = ta.ema(close, ema1)
    def emaUpColor():
        return hlc3 >= usedEma

    def emaDownColor():
        return hlc3 < usedEma

    col = color.lime if hlc3 >= usedEma else color.red if hlc3 < usedEma else color.white
    emaDownColor_1 = emaDownColor()
    barcolor(color.lime if emaUpColor() else color.red if emaDownColor_1 else na)
    plot(usedEma if shema and cast_bool(usedEma) else na, title='EMA', style=plot.style_line, linewidth=3, color=col)
    entryPriceActionAboveEMATrend = emaUpColor()
    entryPriceActionBelowEMATrend = emaDownColor()
    TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
    DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
    DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
    SmoothedTrueRange: Series[float] = 0.0
    SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / len + TrueRange
    SmoothedDirectionalMovementPlus: Series[float] = 0.0
    SmoothedDirectionalMovementPlus = nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / len + DirectionalMovementPlus
    SmoothedDirectionalMovementMinus: Series[float] = 0.0
    SmoothedDirectionalMovementMinus = nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / len + DirectionalMovementMinus
    DIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100
    DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
    DX = math.abs(DIPlus - DIMinus) / (DIPlus + DIMinus) * 100
    ADX: Series = ta.sma(DX, len)
    entryADXAboveThreshold = ADX > th and ADX[2] + iADXSlope < ADX[1] and (ADX[1] + iADXSlope < ADX)
    longCondition = entryPriceActionAboveEMATrend and entryBbraidFilterGreenBar and entryADXAboveThreshold
    shortCondition = entryPriceActionBelowEMATrend and entryBraidFilterRedBar and entryADXAboveThreshold
    closeLongCondition: int = 0
    closeShortCondition: int = 0
    start = startPeriodTime >= time if useStartPeriodTime else False
    end = endPeriodTime <= time if useEndPeriodTime else False
    calcPeriod = not start and (not end)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    stoplossPercent = __input_22__ * 0.01
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
    def f_fillCell(_table, _column, _row, _title, _value, _bgcolor, _txtcolor):
        _cellText = _title + '\n' + _value
        return table.cell(_table, _column, _row, _cellText, bgcolor=_bgcolor, text_color=_txtcolor, text_size=size.auto)

    if showDashboard:
        bgcolor__ren__: Persistent = color.new(color.black, 0)
        newWin = strategy.wintrades > strategy.wintrades[1] and strategy.losstrades == strategy.losstrades[1] and (strategy.eventrades == strategy.eventrades[1])
        newLoss = strategy.wintrades == strategy.wintrades[1] and strategy.losstrades > strategy.losstrades[1] and (strategy.eventrades == strategy.eventrades[1])
        winRow: IBPersistent[int] = 0
        lossRow: IBPersistent[int] = 0
        maxWinRow: IBPersistent[int] = 0
        maxLossRow: IBPersistent[int] = 0
        if newWin:
            lossRow = 0
            winRow = winRow + 1
        if winRow > maxWinRow:
            maxWinRow = winRow
        if newLoss:
            winRow = 0
            lossRow = lossRow + 1
        if lossRow > maxLossRow:
            maxLossRow = lossRow
        dashTable: Persistent[Table] = table.new(position.bottom_right, 1, 15, border_width=1)
        if barstate.islastconfirmedhistory:
            dollarReturn = strategy.netprofit
            f_fillCell(dashTable, 0, 0, 'Start:', string.format('{0,date,long}', strategy.closedtrades.entry_time(0)), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 1, 'End:', string.format('{0,date,long}', strategy.opentrades.entry_time(0)), bgcolor__ren__, color.white)
            _profit = strategy.netprofit / strategy.initial_capital * 100
            f_fillCell(dashTable, 0, 2, 'Net Profit:', string.tostring(_profit, '##.##') + '%', color.green if _profit > 0 else color.red, color.white)
            _numOfDaysInStrategy = (strategy.opentrades.entry_time(0) - strategy.closedtrades.entry_time(0)) / (1000 * 3600 * 24)
            f_fillCell(dashTable, 0, 3, 'Percent Per Day', string.tostring(_profit / _numOfDaysInStrategy, '#########################.#####') + '%', color.green if _profit > 0 else color.red, color.white)
            _winRate = strategy.wintrades / strategy.closedtrades * 100
            f_fillCell(dashTable, 0, 4, 'Percent Profitable:', string.tostring(_winRate, '##.##') + '%', color.red if _winRate < 50 else color.new('#999900') if _winRate < 75 else color.green, color.white)
            f_fillCell(dashTable, 0, 5, 'Profit Factor:', string.tostring(strategy.grossprofit / strategy.grossloss, '##.###'), color.green if strategy.grossprofit > strategy.grossloss else color.red, color.white)
            f_fillCell(dashTable, 0, 6, 'Total Trades:', string.tostring(strategy.closedtrades), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 8, 'Max Wins In A Row:', string.tostring(maxWinRow, '######'), bgcolor__ren__, color.white)
            f_fillCell(dashTable, 0, 9, 'Max Losses In A Row:', string.tostring(maxLossRow, '######'), bgcolor__ren__, color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
