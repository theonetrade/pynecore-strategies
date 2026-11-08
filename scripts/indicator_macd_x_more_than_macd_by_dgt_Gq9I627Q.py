"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, bgcolor,
    close, color, display, fill, format, high, hlc3, input, label, location, low, math, na, nz,
    open, plot, plotshape, position, script, shape, size, string, syminfo, ta, table, text, time,
    timeframe, timenow, volume, xloc
)
from pynecore.types import Label, Persistent, PersistentSeries, Series, Table

display__ren__ = display.all - display.status_line
sqzGR: str = 'Add-Ons'
btGR: str = '=============   Backtest Framework   ============='


@script.indicator('MACD-X, More Than MACD by DGT', 'MACD-X ☼☾')
def main(
    macdType=input.string('MACD-SOURCE', 'MACD Calculation Mode', display=display__ren__, options=('MACD-TRADITIONAL', 'MACD-HISTOGRAM', 'MACD-LEADER', 'MACD-SOURCE', 'MACD-TRIX'), tooltip='Select the internal MACD-X calculation engine:\n\n' + '• MACD-TRADITIONAL → Classic fast/slow EMA MACD\n' + '• MACD-HISTOGRAM   → Momentum derived from histogram slope\n' + '• MACD-LEADER      → Early bias detection model\n' + '• MACD-SOURCE      → Source-smoothed adaptive variant\n' + '• MACD-TRIX        → Triple EMA momentum oscillator\n\n' + 'Each mode alters signal responsiveness and structure.'),
    sourceType=input.string('Close', '  Source', display=display__ren__, options=('Close', 'HLC3 (High + Low + Close) / 3', 'On Balance Volume (OBV)', 'Accumulation / Distribution', 'Price Volume Trend (PVT)'), tooltip='Select the data source used for MACD calculation.\n\n' + '• Close → Standard price-based MACD\n' + '• HLC3 → Smoothed price averaging\n' + '• OBV / AD / PVT → Volume-derived momentum engines\n\n' + 'Using volume-based sources transforms MACD into a flow oscillator.'),
    fast_length=input(12, '  Fast Length', display=display__ren__),
    slow_length=input(26, '  Slow Length', display=display__ren__),
    signal_length=input.int(9, '  Signal Smoothing', minval=1, maxval=50, display=display__ren__),
    macdTrdDisp=input(False, 'Show Traditional MACD', tooltip='Displays classic MACD alongside MACD-X.\n\n' + 'When enabled, MACD-X will auto-highlight to visually separate the two engines.'),
    hstThesh=input.bool(False, 'Enable Histogram Threshold Bands', tooltip='Plots deviation-based bands around the MACD histogram.\n\n' + 'Used to identify extreme momentum expansion and statistically stretched conditions.'),
    stDevL=input.float(1.75, '  Lower Deviation Multiplier', minval=0.0, maxval=5.0, step=0.25, display=display__ren__, tooltip='Lower statistical deviation threshold.\n\n' + 'Defines moderate momentum expansion zone.'),
    stDevH=input.float(2.25, '  Higher Deviation Multiplier', minval=0.0, maxval=5.0, step=0.25, display=display__ren__, tooltip='Higher statistical deviation threshold.\n\n' + 'Defines extreme momentum expansion zone.\n\n' + 'Values above this level suggest exhaustion risk.'),
    exponential=input(True, 'Use Exponential Moving Average', tooltip='Switch between EMA and SMA for internal smoothing.\n\n' + '• ON  → Faster reaction, more responsive signals\n' + '• OFF → Smoother, slower structure'),
    highlight__input=input(False, 'Highlight MACD-X / Signal-X Area', tooltip='Fills the area between MACD-X and Signal-X.\n' + 'Helps visualize momentum expansion and compression phases.'),
    dispLabel=input(False, 'Display Live Value Label'),
    histLabel=input.int(0, '  Historical Label Readings', minval=0, display=display__ren__),
    dispSqueeze=input.bool(False, 'Enable Squeeze', group=sqzGR, tooltip='Activates volatility compression detection\n' + 'based on Bollinger Bands and Keltner Channels.\n\n' + '• Compression → BB inside KC\n' + '• Release     → BB expanding outside KC\n\n' + 'MACD-X acts as momentum confirmation.'),
    bbkcLength=input.int(20, '  Squeeze Length', minval=1, group=sqzGR, display=display__ren__, tooltip='Lookback period used for both:\n' + '• Bollinger Bands\n' + '• Keltner Channels\n\n' + 'Higher values → Broader compression cycles.'),
    bbMult=input.float(2.0, '  Bollinger Band Multiplier', step=0.25, group=sqzGR, display=display__ren__, tooltip='Standard deviation multiplier for\n' + 'Bollinger Bands width.\n\n' + 'Higher → Wider bands\n' + 'Lower  → More frequent compression'),
    kcMult=input.float(1.25, '  Keltner Channel Multiplier', step=0.25, group=sqzGR, display=display__ren__, tooltip='ATR-based multiplier for Keltner Channel width.\n\n' + 'Controls how tight the squeeze detection is.\n\n' + 'Lower values → Easier compression trigger.'),
    colorRsi=input.bool(False, 'Enable RSI-Based MACD Coloring', group=sqzGR, tooltip='Changes MACD-X color when RSI reaches\n' + 'extreme zones.\n\n' + '• Above Overbought → Bearish highlight\n' + '• Below Oversold   → Bullish highlight\n\n' + 'Useful for detecting exhaustion conditions.'),
    rsiLength=input.int(14, '  RSI Length', minval=1, group=sqzGR, display=display__ren__, tooltip='Lookback period for RSI calculation.\n\n' + 'Lower values → More reactive\n' + 'Higher values → Smoother structure'),
    rsiOverBought=input.int(70, '  RSI Overbought Level', minval=51, maxval=99, group=sqzGR, display=display__ren__, tooltip='Upper RSI threshold.\n\n' + 'When RSI exceeds this level, MACD-X will shift to bearish emphasis.'),
    rsiOverSold=input.int(30, '  RSI Oversold Level', minval=1, maxval=49, group=sqzGR, display=display__ren__, tooltip='Lower RSI threshold.\n\n' + 'When RSI drops below this level, MACD-X will shift to bullish emphasis.'),
    vbcb=input.bool(True, 'Enable Volume-Weighted Price Bars', group=sqzGR),
    vwcbLen=input.int(21, '  Volume MA Length', minval=1, group=sqzGR, display=display__ren__),
    vwcbUpper=input.float(1.618, '  Upper Threshold', minval=0.1, step=0.1, group=sqzGR, display=display__ren__),
    vwcbLower=input.float(0.618, '  Lower Threshold', minval=0.1, step=0.1, group=sqzGR, display=display__ren__),
    isBackTest=input.bool(False, 'Enable Backtest', group=btGR, tooltip='Enable or disable the backtest framework.'),
    tradeMode=input.string('Both', 'Trade Mode', options=('Long Only', 'Short Only', 'Both'), group=btGR, display=display__ren__, tooltip='Defines which trade directions are simulated.\n\n' + '• Long Only  — enters on long signal, exits on short signal or stop loss\n' + '• Short Only — enters on short signal, exits on long signal or stop loss\n' + '• Both       — enters on either signal, optionally reverses on the opposite'),
    reverseOnSignal=input.bool(True, 'Reverse on Opposite Signal', group=btGR, tooltip='Only applies when Trade Mode is Both.\n' + 'When enabled, an opposite signal immediately closes the current trade\n' + 'and opens a new one in the other direction — always in trade once started.\n' + 'When disabled, opposite signal exits only — no new trade until next entry signal.'),
    dasCapital=input.float(1000.0, 'Initial Capital', group=btGR, display=display__ren__, tooltip='Starting capital for the simulation.\n' + 'Used to calculate compounding PnL and final equity.'),
    lenBckTst=input.float(1.0, 'Period (Years)', minval=0.0, step=0.1, group=btGR, display=display__ren__, tooltip='Lookback window for the simulation in years.\n' + 'Capped automatically if the selected timeframe has insufficient history.'),
    isStopLoss=input.bool(False, 'Apply Stop Loss', inline='sl', group=btGR, tooltip='Exits the trade if price moves against the position intrabar.\n' + 'Long SL : low  reaches entry × (1 − %)\n' + 'Short SL: high reaches entry × (1 + %)'),
    __input_31__=input.float(1.0, '  %', step=0.1, minval=0.0, inline='sl', group=btGR, display=display__ren__),
    useCandleL=input.bool(False, 'Long Candle Confirmation', group=btGR, tooltip='Long entries only taken on bullish bars (close > open).'),
    useCandleS=input.bool(False, 'Short Candle Confirmation', group=btGR, tooltip='Short entries only taken on bearish bars (close < open).'),
    isSudden=input.bool(True, 'Avoid Same-Bar Conflicts', group=btGR, tooltip='Skips entries when both long and short signals fire on the same bar.\n' + 'Reduces false entries from volatile spikes.'),
    isTest=input.bool(False, '❗ Next Bar Mode (Repaints)', group=btGR, tooltip="Uses the next bar's open for simulation instead of the confirmed bar open.\n" + 'Produces earlier entries but signals will repaint.\n' + 'For testing and comparison only — do not use for live alerts.'),
    lblInOutSL=input.bool(True, 'Show Entry / Exit Labels', group=btGR, tooltip='Displays L / S / SL / TP labels at entry and exit bars with tooltips showing direction, price, change, and capital.'),
    lblWarnings=input.bool(True, 'Show Early Warnings', group=btGR, tooltip='Shows a ⚠️ label when a signal fires but has not yet been confirmed.\n' + 'Label is deleted on the following bar regardless of outcome.'),
    lblTrdStat=input.bool(True, 'Show Trade Statistics', group=btGR, tooltip='Displays a floating label with full trade summary.\n' + 'Includes win rate, PnL, long/short breakdown, and current trade status.')
):
    highlight: Persistent = highlight__input


    def ma(s, l):
        return ta.ema(s, l) if exponential else ta.sma(s, l)

    __block_result__ = na
    __switch__ = sourceType
    if __switch__ == 'Close':
        __block_result__ = close
    elif __switch__ == 'HLC3 (High + Low + Close) / 3':
        __block_result__ = hlc3
    elif __switch__ == 'On Balance Volume (OBV)':
        __block_result__ = ta.obv
    elif __switch__ == 'Accumulation / Distribution':
        __block_result__ = ta.accdist
    elif __switch__ == 'Price Volume Trend (PVT)':
        __block_result__ = ta.pvt
    source = __block_result__

    fast_ma = ma(source, fast_length)
    slow_ma = ma(source, slow_length)

    macd = fast_ma - slow_ma

    __block_result_1__ = na
    if macdType == 'MACD-TRADITIONAL':
        __block_result_1__ = macd
    elif macdType == 'MACD-HISTOGRAM':
        __block_result_1__ = macd - ma(macd, signal_length)
    elif macdType == 'MACD-LEADER':
        __block_result_1__ = macd + ma(source - fast_ma, fast_length) - ma(source - slow_ma, slow_length)
    elif macdType == 'MACD-SOURCE':
        __block_result_1__ = ma(source - math.avg(fast_ma, slow_ma), signal_length)
    elif macdType == 'MACD-TRIX':
        __block_result_1__ = 10000 * ta.change(ta.ema(ta.ema(ta.ema(math.log(source), signal_length * 2), signal_length * 2), signal_length * 2))
    macdx = __block_result_1__

    signal = ma(macd, signal_length)
    signalx = ma(macdx, signal_length)
    histx: Series = macdx - signalx

    highlight = macdTrdDisp or highlight

    rsiValue = ta.rsi(source, rsiLength) if colorRsi else na

    inSqz: Persistent[bool] = False
    noSqz: Persistent[bool] = False
    unSqz: Persistent[bool] = False
    if dispSqueeze:
        _, bbUpper, bbLower = ta.bb(close, bbkcLength, bbMult)
        _, kcUpper, kcLower = ta.kc(close, bbkcLength, kcMult, True)

        inSqz = bbLower > kcLower and bbUpper < kcUpper
        noSqz = bbLower < kcLower and bbUpper > kcUpper
        unSqz = inSqz == False and noSqz == False

    __block_result_2__ = (na, na, na)
    if hstThesh:
        __block_result_2__ = ta.bb(histx, 233, stDevL)
    _, upperL, lowerL = __block_result_2__
    __block_result_3__ = (na, na, na)
    if hstThesh:
        __block_result_3__ = ta.bb(histx, 233, stDevH)
    _, upperH, lowerH = __block_result_3__

    mean = ta.sma(volume, vwcbLen)

    __block_result_4__ = (na, na)
    if close < open:
        __block_result_5__ = (na, na)
        if volume > mean * vwcbUpper:
            __block_result_5__ = (color.new('#910000'), 'High Volume')
        elif volume >= mean * vwcbLower and volume <= mean * vwcbUpper:
            __block_result_5__ = (color.red, 'Average Volume')
        else:
            __block_result_5__ = (color.orange, 'Low Volume')
        __block_result_4__ = __block_result_5__
    else:
        __block_result_6__ = (na, na)
        if volume > mean * vwcbUpper:
            __block_result_6__ = (color.new('#006400'), 'High Volume')
        elif volume >= mean * vwcbLower and volume <= mean * vwcbUpper:
            __block_result_6__ = (color.teal, 'Average Volume')
        else:
            __block_result_6__ = (color.new('#7FFFD4'), 'Low Volume')
        __block_result_4__ = __block_result_6__
    vbcbColor, vbcbTxt = __block_result_4__

    isGrowing = histx > histx[1]
    isBullish = histx >= 0

    histColor = (color.new('#006400') if isGrowing else color.green) if isBullish else color.red if isGrowing else color.new('#910000')

    status = '\n\nHistorical Bar Readings - ' + string.tostring(histLabel) + ' bar(s) earlier' if histLabel > 0 else '\n\nCurrent Bar Readings'

    lastCrossIndex = ta.valuewhen(ta.cross(macdx, signalx), bar_index, 0)
    msCross = na if na(lastCrossIndex) else bar_index - lastCrossIndex

    macdMom = 'Falling - Last Signal Cross ' if ta.change(histx) <= 0 else 'Growing - Last Signal Cross '
    macdText: Series = 'Method : ' + macdType + '\nSource : ' + sourceType + status + '\nMACD\t: ' + macdMom + string.tostring(msCross) + ' bar(s)'

    rsiState = 'OverBought Zone' if rsiValue >= rsiOverBought else 'OverSold Zone' if rsiValue <= rsiOverSold else 'Bullish Zone' if rsiValue > 60 else 'Bearish Zone' if rsiValue < 40 else 'Neutral Zone'
    rsiText: Series = '\nRSI\t: Value ' + string.tostring(rsiValue, '#.#') + ' - ' + rsiState

    sqzText: Series = ('\nSQZ  : Compression Phase (No Trade Zone)' if inSqz else '\nSQZ  : Release Phase' if unSqz else '\nSQZ  : Bullish Momentum' if histx >= 0 else '\nSQZ  : Bearish Momentum') if dispSqueeze else na

    vbcbText: Series = '\nVolume : ' + vbcbTxt + ' (' + string.tostring(volume, format.volume) + ')' if cast_bool(nz(volume)) and vbcb else na

    plot(histx, 'Histogram-X', color=histColor, style=plot.style_columns, display=display__ren__)
    p1 = plot(macdx, 'MACD-X', color=color.new('#910000') if rsiValue > rsiOverBought else color.new('#006400') if rsiValue < rsiOverSold else color.new('#0094FF'), editable=False, display=display__ren__)
    p2 = plot(signalx, 'Signal-X', color=color.new(color.new('#FF6A00'), 0), display=display__ren__)

    plot(macd if macdTrdDisp else na, 'MACD', color=color.new(color.new('#0094FF'), 0), display=display__ren__)
    plot(signal if macdTrdDisp else na, 'Signal', color=color.new(color.new('#FF6A00'), 0), display=display__ren__)

    fill(p1, p2, color=((color.new(color.new('#910000'), 66) if rsiValue > rsiOverBought else color.new(color.new('#006400'), 66) if rsiValue < rsiOverSold else color.new(color.new('#0094FF'), 66)) if macdx > signalx else color.new(color.new('#910000'), 66) if rsiValue > rsiOverBought else color.new(color.new('#006400'), 66) if rsiValue < rsiOverSold else color.new(color.new('#FF6A00'), 66)) if highlight else na, editable=False)

    plotshape((True if unSqz or inSqz else False) if dispSqueeze else False, style=shape.diamond, location=location.top, color=color.new(color.gray, 0), title='In Squeeze', display=display__ren__)
    plotshape((True if noSqz and histx >= 0 else False) if dispSqueeze else False, style=shape.triangleup, location=location.top, color=color.new(color.teal, 0), title='Squeeze Release', display=display__ren__)
    plotshape((True if noSqz and histx < 0 else False) if dispSqueeze else False, style=shape.triangledown, location=location.top, color=color.new(color.red, 0), title='Squeeze Release', display=display__ren__)

    if dispLabel and (not isBackTest):
        macdLabel: Series[Label] = label.new(time, 0, text=macdText[histLabel] + rsiText[histLabel] + sqzText[histLabel] + vbcbText[histLabel], tooltip='evaluation given herein does not constitute professional and/or financial advice', color=color.new('#0094FF'), xloc=xloc.bar_time, style=label.style_label_left, textcolor=color.white, textalign=text.align_left)

        label.set_x(macdLabel, label.get_x(macdLabel) + math.round(ta.change(time) * 3))

        label.delete(macdLabel[1])

    bu2 = plot(upperL, 'Overbought Lower Band', display=display.none, editable=False)
    bu3 = plot(upperH, 'Overbought Upper Band', display=display.none, editable=False)
    fill(bu2, bu3, color=color.new(color.red, 75), title='Overbought Zone')

    bl2 = plot(lowerL, 'Oversold Upper Band', display=display.none, editable=False)
    bl3 = plot(lowerH, 'Oversold Lower Band', display=display.none, editable=False)
    fill(bl2, bl3, color=color.new(color.teal, 75), title='Oversold Zone')

    barcolor(vbcbColor if cast_bool(nz(volume)) and vbcb else na, title='Volume-Weighted Price Bars', editable=False)

    alarm: Series = ta.cross(macdx, signalx)
    alertcondition(alarm[1] if barstate.islast else alarm, title='MACD-X : Trading Signal', message='MACD-X Trading Signal Detected\n{{exchange}}:{{ticker}}\nPrice: {{close}}\nTime: {{time}}')

    longAlertCondition: Series = ta.crossover(macdx, signalx)
    alertcondition(longAlertCondition, 'Long : Early Warning', 'MACD-X - Early Long Signal\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')
    alertcondition(longAlertCondition[1], 'Long : Confirmed', 'MACD-X - Confirmed Long Signal\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')

    shortAlertCondition: Series = ta.crossunder(macdx, signalx)
    alertcondition(shortAlertCondition, 'Short : Early Warning', 'MACD-X - Early Short Signal\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')
    alertcondition(shortAlertCondition[1], 'Short : Confirmed', 'MACD-X - Confirmed Short Signal\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')

    bt_yAnchor = close

    stopLoss = __input_31__ / 100

    startBckTst: Series = time > timenow - lenBckTst * 31556952000

    _dir: Persistent[list[int]] = array.new_int(1, 0)
    _entry: Persistent[list[float]] = array.new_float(1, 0.0)
    _exit: Persistent[list[float]] = array.new_float(1, 0.0)
    _cap: Persistent[list[float]] = array.new_float(1, dasCapital)
    _trades: Persistent[list[int]] = array.new_int(1, 0)
    _winL: Persistent[list[int]] = array.new_int(1, 0)
    _lossL: Persistent[list[int]] = array.new_int(1, 0)
    _winS: Persistent[list[int]] = array.new_int(1, 0)
    _lossS: Persistent[list[int]] = array.new_int(1, 0)

    def bt_dir():
        return array.get(_dir, 0)

    def bt_entry():
        return array.get(_entry, 0)

    def bt_exit():
        return array.get(_exit, 0)

    def bt_cap():
        return array.get(_cap, 0)

    def bt_trades():
        return array.get(_trades, 0)

    def bt_winL():
        return array.get(_winL, 0)

    def bt_lossL():
        return array.get(_lossL, 0)

    def bt_winS():
        return array.get(_winS, 0)

    def bt_lossS():
        return array.get(_lossS, 0)

    def f_open(_d, _lbl):
        array.set(_entry, 0, open)
        array.set(_dir, 0, _d)
        array.set(_trades, 0, bt_trades() + 1)

        __block_result_7__ = na
        if _lbl:
            __block_result_7__ = label.new(bar_index, low if _d == 1 else high, text='L' if _d == 1 else 'S', tooltip='Direction .... : ' + ('Long' if _d == 1 else 'Short') + '\n' + 'Entry price .. : ' + string.tostring(open) + '\n' + 'Capital ...... : ' + string.tostring(bt_cap(), '#.##'), style=label.style_label_up if _d == 1 else label.style_label_down, color=color.teal if _d == 1 else color.red, textcolor=color.white, size=size.tiny, force_overlay=True)
        return __block_result_7__

    def f_close(_isSL, _lbl):
        _d = bt_dir()
        _ep = bt_entry()
        _xp = close if _isSL else open

        array.set(_exit, 0, _xp)

        _entrySafe = math.max(_ep, syminfo.mintick)
        _exitSafe = math.max(_xp, syminfo.mintick)

        _pnl = _exitSafe / _entrySafe if _d == 1 else _entrySafe / _exitSafe

        _newCap = bt_cap() * _pnl
        _profit = _pnl > 1.0

        array.set(_cap, 0, _newCap)

        if _d == 1:
            array.set(_winL, 0, bt_winL() + (1 if _profit else 0))
            array.set(_lossL, 0, bt_lossL() + (0 if _profit else 1))
        else:
            array.set(_winS, 0, bt_winS() + (1 if _profit else 0))
            array.set(_lossS, 0, bt_lossS() + (0 if _profit else 1))

        if _lbl:
            label.new(bar_index, high if _d == 1 else low, text='SL' if _isSL else 'TP', tooltip='Exit type .... : ' + ('Stop Loss' if _isSL else 'Take Profit') + '\n' + 'Direction .... : ' + ('Long' if _d == 1 else 'Short') + '\n' + 'Entry / Exit . : ' + string.tostring(_ep) + ' / ' + string.tostring(_xp) + '\n' + 'Change ....... : ' + string.tostring((_pnl - 1) * 100, '#.##') + '%\n' + 'Capital ...... : ' + string.tostring(_newCap, '#.##'), style=label.style_label_down if _d == 1 else label.style_label_up, color=color.teal if _profit else color.red, textcolor=color.white, size=size.tiny, force_overlay=True)

        return array.set(_dir, 0, 0)

    if isBackTest:
        sigL = longAlertCondition[1] if isTest else longAlertCondition[2]
        sigS = shortAlertCondition[1] if isTest else shortAlertCondition[2]

        candleRef = 0 if isTest else 1
        conflict = longAlertCondition[candleRef] and shortAlertCondition[candleRef]

        okL = (not useCandleL or close[candleRef] > open[candleRef]) and (not isSudden or not conflict)
        okS = (not useCandleS or close[candleRef] < open[candleRef]) and (not isSudden or not conflict)

        longCond = sigL and okL
        shortCond = sigS and okS

        canLong = tradeMode != 'Short Only'
        canShort = tradeMode != 'Long Only'

        slL = isStopLoss and bt_dir() == 1 and (low <= bt_entry() * (1 - stopLoss))
        slS = isStopLoss and bt_dir() == -1 and (high >= bt_entry() * (1 + stopLoss))
        slHit = slL or slS

        if startBckTst:
            _reversed: Persistent[bool] = False
            _reversed = False

            if reverseOnSignal and tradeMode == 'Both':
                if bt_dir() == 1 and shortCond:
                    f_close(False, lblInOutSL)
                    if canShort:
                        f_open(-1, lblInOutSL)
                    _reversed = True
                elif bt_dir() == -1 and longCond:
                    f_close(False, lblInOutSL)
                    if canLong:
                        f_open(1, lblInOutSL)
                    _reversed = True

            if not _reversed:
                exitL = bt_dir() == 1 and (shortCond or slHit)
                exitS = bt_dir() == -1 and (longCond or slHit)

                if exitL or exitS:
                    f_close(slHit, lblInOutSL)

            if bt_dir() == 0:
                if longCond and canLong:
                    f_open(1, lblInOutSL)
                    alert('Long entry — ' + syminfo.tickerid + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar)

                if shortCond and canShort:
                    f_open(-1, lblInOutSL)
                    alert('Short entry — ' + syminfo.tickerid + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar)

            if slHit:
                alert('Stop loss — ' + syminfo.tickerid + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar)

        wLabel: PersistentSeries[Label] = na(Label)

        if lblWarnings:
            if canLong and bt_dir() != 1 and longAlertCondition[1] and (not shortAlertCondition):
                wLabel = label.new(bar_index, low, '⚠️', tooltip='Probable long entry — awaiting confirmation\n' + 'If confirmed, trade executes at next bar open.', color=color.teal, style=label.style_none, textcolor=color.white, size=size.large, force_overlay=True)
                label.delete(wLabel[1])
                alert('Long early warning — ' + syminfo.tickerid + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar)

            if canShort and bt_dir() != -1 and shortAlertCondition[1] and (not longAlertCondition):
                wLabel = label.new(bar_index, high, '⚠️', tooltip='Probable short entry — awaiting confirmation\n' + 'If confirmed, trade executes at next bar open.', color=color.red, style=label.style_none, textcolor=color.white, size=size.large, force_overlay=True)
                label.delete(wLabel[1])
                alert('Short early warning — ' + syminfo.tickerid + ' | Price: ' + string.tostring(close), alert.freq_once_per_bar)

            if cast_bool(ta.change(time)):
                label.delete(wLabel[1])

        if lblTrdStat:
            years: Persistent[float] = (timenow - time) / 31556952000
            perTxt: Persistent[str] = ''
            statLbl: Persistent[Label] = na(Label)

            totalTrades = bt_trades()
            totalWin = bt_winL() + bt_winS()
            totalLoss = bt_lossL() + bt_lossS()

            estimated = bt_cap() * (close / bt_entry()) if bt_dir() == 1 else bt_cap() * (bt_entry() / close) if bt_dir() == -1 else bt_cap()

            winRate = totalWin / totalTrades * 100 if totalTrades > 0 else 0.0
            gainPct = (estimated / dasCapital - 1) * 100
            tradeDirTxt = 'Long' if bt_dir() == 1 else 'Short' if bt_dir() == -1 else 'Flat'

            if years < lenBckTst:
                perTxt = string.tostring(lenBckTst, '#.##') + ' Yrs *** (' + string.tostring(bar_index) + ' bars max)'
            else:
                perTxt = string.tostring(lenBckTst, '#.##') + ' Year(s)'

            _slTxt = string.tostring(stopLoss * 100, '#.#') + '% — level: ' + string.tostring(bt_entry() * (1 - stopLoss) if bt_dir() == 1 else bt_entry() * (1 + stopLoss) if bt_dir() == -1 else 0.0, '#.##') if isStopLoss else 'Off'

            _sep: str = '\n═════════════════════════════════════'

            _txt = '☼☾ Trade Statistics | ' + timeframe.period + ' | ' + perTxt + ' | Trade Mode : ' + tradeMode + _sep + '\nWin Rate : ' + string.tostring(winRate, '#.#') + '%' + ' | Trades : ' + string.tostring(totalTrades) + '\nWin/Loss : ' + string.tostring(totalWin) + '/' + string.tostring(totalLoss) + ' | Long  W/L : ' + string.tostring(bt_winL()) + '/' + string.tostring(bt_lossL()) + ' | Short W/L : ' + string.tostring(bt_winS()) + '/' + string.tostring(bt_lossS()) + _sep + '\nGain/Loss : ' + string.tostring(gainPct, '#.##') + '%' + ' | Initial/Final Capital : ' + string.tostring(dasCapital, '#.##') + '/' + string.tostring(estimated, '#.##') + _sep + '\nStatus : ' + tradeDirTxt + (' | Entry Price : ' + string.tostring(bt_entry()) + ' | Unrealized : ' + string.tostring((estimated / bt_cap() - 1) * 100, '#.##') + '%' + '\nStop Loss : ' + _slTxt if bt_dir() != 0 else '') + ('\n*** max available history for this timeframe' if years < lenBckTst else '')

            _statCol = color.teal if gainPct > 0 else color.red if gainPct < 0 else color.gray

            label.delete(statLbl)
            statLbl = label.new(bar_index + 5, bt_yAnchor, _txt, color=_statCol, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, textalign=text.align_left, size=size.small, force_overlay=True)

    bgcolor((color.new(color.gray, 90) if startBckTst != startBckTst[1] else color.new(color.teal, 92) if bt_dir() == 1 else color.new(color.red, 92) if bt_dir() == -1 else na) if isBackTest and startBckTst else na, title='Backtest Background', editable=False)

    plot(bt_entry() if bt_dir() != 0 else bt_exit() if bt_exit() > 0 else na, 'Entry / Exit Price', color=color.teal if bt_dir() == 1 else color.red if bt_dir() == -1 else color.gray, style=plot.style_circles, display=display__ren__, editable=False, force_overlay=True)

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    logo2: Persistent[Table] = table.new(position.bottom_right, 1, 1, force_overlay=True)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')
        table.cell(logo2, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
