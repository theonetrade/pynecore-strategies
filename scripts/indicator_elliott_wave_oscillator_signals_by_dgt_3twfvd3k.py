"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, close, color, display,
    extend, fill, high, input, label, line, linefill, location, low, math, na, nz, open, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, text, time, timeframe,
    timenow, xloc
)
from pynecore.types import Label, Line, LineFill, Persistent, PersistentSeries, Series, Table

display__ren__ = display.all - display.status_line
g: str = 'Elliott Wave Oscillator'
btGR: str = '=============   Backtest Framework   ============='


@script.indicator('Elliott Wave Oscillator Signals by DGT', 'EWOˢ ☼☾', True, max_labels_count=500, max_lines_count=500, max_bars_back=500)
def main(
    ew=input.bool(True, 'Elliott Wave Oscillator Signals', group=g, tooltip='Enables or disables plotting of EWOˢ signals and labels.\n' + '• Enabled → Signals and shapes are plotted on the chart.\n' + '• Disabled → Signals are hidden, but calculations remain active.'),
    e=input.string('EMA', '  Smoothing', options=('SMA', 'EMA'), group=g, display=display__ren__, tooltip='Selects the smoothing method used in the oscillator.\n' + '• EMA → Exponential Moving Average, faster response to recent price changes\n' + '• SMA → Simple Moving Average, smoother, more stable signals'),
    d=input.int(5, '  Signal Delay', minval=2, group=g, display=display__ren__, tooltip='Controls how many bars the EWO signal is delayed.\n' + '• Lower values → earlier, more reactive signals\n' + '• Higher values → slower, more confirmed signals\n' + 'Useful for filtering noise in lower timeframes.'),
    t=input.int(13, '  Signal Strength Threshold', minval=1, group=g, display=display__ren__, tooltip='Minimum oscillator strength required to validate a signal.\n' + '• Higher values → fewer but stronger signals\n' + '• Lower values → more frequent, weaker signals\n' + 'Acts as a quality filter for EWOˢ signals.'),
    h=input.bool(True, 'Show EWO Histogram', group=g, tooltip='Plots the Elliott Wave Oscillator histogram as an overlay on the price chart.\n' + 'Useful for visualizing momentum strength relative to price action and wave structure.'),
    oscPlacement=input.string('Bottom', '  Placement', options=('Top', 'Bottom'), inline='VOL', display=display__ren__, group=g),
    __input_6__=input.int(7, 'Height', minval=1, maxval=10, inline='VOL', display=display__ren__, group=g, tooltip='Histogram Placement\nDetermines where the EWO histogram is plotted.\n' + '• Top → plotted above the price bar range\n' + '• Bottom → plotted below the price bar range\n\n' + 'Histogram Height\nControls the vertical scaling of the EWO histogram overlay.\n' + '• Higher values → taller histogram bars\n' + '• Lower values → shorter histogram bars'),
    p=input.int(233, 'Plotting Length', group='Display Settings', display=display__ren__, tooltip='Specifies how many historical bars are used for plotting.\n' + '• Higher values → longer historical context\n' + '• Lower values → lighter load and cleaner display'),
    isBackTest=input.bool(False, 'Enable Backtest', group=btGR, tooltip='Enable or disable the backtest framework.\n' + '• ON  → trades simulated using the rules below\n' + '• OFF → only live signals shown'),
    tradeMode=input.string('Both', 'Trade Mode', options=('Long Only', 'Short Only', 'Both'), group=btGR, display=display__ren__, tooltip='Defines which trade directions are simulated.\n\n' + '• Long Only  — enters on long signal, exits on short signal or stop loss\n' + '• Short Only — enters on short signal, exits on long signal or stop loss\n' + '• Both       — enters on either signal, optionally reverses on the opposite'),
    reverseOnSignal=input.bool(True, 'Reverse on Opposite Signal', group=btGR, tooltip='Only applies when Trade Mode is Both.\n' + 'When enabled, an opposite signal immediately closes the current trade\n' + 'and opens a new one in the other direction — always in trade once started.\n' + 'When disabled, opposite signal exits only — no new trade until next entry signal.'),
    dasCapital=input.float(1000.0, 'Initial Capital', group=btGR, display=display__ren__, tooltip='Starting capital for the simulation.\n' + 'Used to calculate compounding PnL and final equity.'),
    lenBckTst=input.float(1.0, 'Period (Years)', minval=0.0, step=0.1, group=btGR, display=display__ren__, tooltip='Lookback window for the simulation in years.\n' + 'Capped automatically if the selected timeframe has insufficient history.'),
    isStopLoss=input.bool(False, 'Apply Stop Loss', inline='sl', group=btGR, tooltip='Exits the trade if price moves against the position intrabar.\n' + 'Long SL : low  reaches entry × (1 − %)\n' + 'Short SL: high reaches entry × (1 + %)'),
    __input_14__=input.float(1.0, '  %', step=0.1, minval=0.0, inline='sl', group=btGR, display=display__ren__),
    useCandleL=input.bool(False, 'Long Candle Confirmation', group=btGR, tooltip='Long entries only taken on bullish bars (close > open).'),
    useCandleS=input.bool(False, 'Short Candle Confirmation', group=btGR, tooltip='Short entries only taken on bearish bars (close < open).'),
    isSudden=input.bool(True, 'Avoid Same-Bar Conflicts', group=btGR, tooltip='Skips entries when both long and short signals fire on the same bar.\n' + 'Reduces false entries from volatile spikes.'),
    isTest=input.bool(False, '❗ Next Bar Mode (Repaints)', group=btGR, tooltip="Uses the next bar's open for simulation instead of the confirmed bar open.\n" + 'Produces earlier entries but signals will repaint.\n' + 'For testing and comparison only — do not use for live alerts.'),
    lblInOutSL=input.bool(True, 'Show Entry / Exit Labels', group=btGR, tooltip='Displays L / S / SL / TP labels at entry and exit bars with tooltips showing direction, price, change, and capital.'),
    lblWarnings=input.bool(True, 'Show Early Warnings', group=btGR, tooltip='Shows a ⚠️ label when a signal fires but has not yet been confirmed.\n' + 'Label is deleted on the following bar regardless of outcome.'),
    lblTrdStat=input.bool(True, 'Show Trade Statistics', group=btGR, tooltip='Displays a floating label with full trade summary.\n' + 'Includes win rate, PnL, long/short breakdown, and current trade status.'),
    k=input.bool(False, 'Display Keltner Channel\'s Clouds', group='Keltner Channels', tooltip='Toggle the visibility of Keltner Channel lines and clouds on the chart.'),
    kcSource: Series[float] = input.source(close, 'Source', inline='KC1', display=display__ren__, group='Keltner Channels'),
    kcMaType=input.string('EMA', '', options=('DEMA', 'EMA', 'HMA', 'SMA', 'WMA'), inline='KC1', display=display__ren__, group='Keltner Channels'),
    kcLength=input.int(20, '', minval=1, inline='KC1', display=display__ren__, group='Keltner Channels'),
    bandsStyle=input.string('Average True Range', 'Bands', options=('Average True Range', 'True Range', 'Range'), display=display__ren__, inline='BAND0', group='Keltner Channels', tooltip='Method used to calculate channel width.\n\n• Average True Range (ATR)\n• True Range (TR) smoothed\n• High-Low Range'),
    atrlength=input.int(10, 'ATR Length', inline='BAND0', display=display__ren__, group='Keltner Channels'),
    isBand1=input.bool(False, '1st Multiplier', inline='BAND1', group='Keltner Channels'),
    kcMult1=input.float(1.0, '', minval=1, step=0.1, inline='BAND1', display=display__ren__, group='Keltner Channels'),
    colorK1=input.color(color.silver, '', inline='BAND1', group='Keltner Channels'),
    widthK1=input.int(1, '', inline='BAND1', display=display__ren__, group='Keltner Channels'),
    isBand2=input.bool(True, '2nd Multiplier', inline='BAND2', group='Keltner Channels'),
    kcMult2=input.float(2.0, '', minval=1, step=0.1, inline='BAND2', display=display__ren__, group='Keltner Channels'),
    colorK2=input.color(color.orange, '', inline='BAND2', group='Keltner Channels'),
    widthK2=input.int(2, '', inline='BAND2', display=display__ren__, group='Keltner Channels'),
    isBand3=input.bool(True, '3rd Multiplier', inline='BAND3', group='Keltner Channels'),
    kcMult3=input.float(3.0, '', minval=1, step=0.1, inline='BAND3', display=display__ren__, group='Keltner Channels'),
    colorK3=input.color(color.red, '', inline='BAND3', group='Keltner Channels'),
    widthK3=input.int(3, '', inline='BAND3', display=display__ren__, group='Keltner Channels'),
    bandsFill=input.bool(False, 'Background Fill', group='Keltner Channels', tooltip='Fill the area between Keltner Channel bands to create cloud visuals.')
):
    oscHeight = 21 - __input_6__ * 2

    source = close

    ewo = (ta.ema(source, 5) / ta.ema(source, 34) - 1) * 100 if e == 'EMA' else (ta.sma(source, 5) / ta.sma(source, 34) - 1) * 100
    ewoSignal = ta.ema(ewo, d) if e == 'EMA' else ta.sma(ewo, d)

    plotshape(ta.crossover(ewo, ewoSignal) and ewo < -t if ew else False, 'Strong Long', shape.labelup, location.belowbar, color.new(color.new('#006400'), 0), size=size.small, display=display__ren__, show_last=p)
    plotshape(ta.crossover(ewo, ewoSignal) and ewo >= -t if ew else False, 'Long', shape.labelup, location.belowbar, color.new(color.green, 0), size=size.tiny, display=display__ren__, show_last=p)
    plotshape(ta.crossunder(ewo, ewoSignal) and ewo > t if ew else False, 'Strong Short', shape.labeldown, location.abovebar, color.new(color.new('#910000'), 0), size=size.small, display=display__ren__, show_last=p)
    plotshape(ta.crossunder(ewo, ewoSignal) and ewo <= t if ew else False, 'Short', shape.labeldown, location.abovebar, color.new(color.red, 0), size=size.tiny, display=display__ren__, show_last=p)

    lookbackLength = p

    a_lines: Persistent[list[Line]] = array.new_line()
    a_fill: Persistent[list[LineFill]] = array.new_linefill()

    priceHighest = ta.highest(high, lookbackLength)
    priceLowest = ta.lowest(low, lookbackLength)
    ewoHistograme: Series = ta.ema(source, 5) - ta.ema(source, 34) if e == 'EMA' else ta.sma(source, 5) - ta.sma(source, 34)
    ewoHighest = ta.highest(ewoHistograme, lookbackLength)

    ewoColore: Series = (color.new('#006400') if nz(ewoHistograme[1]) < ewoHistograme else color.green) if ewoHistograme >= 0 else color.red if nz(ewoHistograme[1]) < ewoHistograme else color.new('#910000')

    if barstate.islast and h:
        if array.size(a_lines) > 0:
            __loop_2__ = pine_loop(1, 1)
            while __loop_2__.step(array.size(a_lines)):
                i = __loop_2__.value
                line.delete(array.shift(a_lines))

        if array.size(a_fill) > 0:
            __loop_2__ = pine_loop(1, 1)
            while __loop_2__.step(array.size(a_fill)):
                i = __loop_2__.value
                linefill.delete(array.shift(a_fill))

        priceChangeRate = (priceHighest - priceLowest) / priceHighest / oscHeight

        for barIndex in pine_range(0, lookbackLength - 1, 1):
            array.push(a_lines, line.new(bar_index[barIndex], priceHighest if oscPlacement == 'Top' else priceLowest, bar_index[barIndex], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + ewoHistograme[barIndex] / ewoHighest * priceChangeRate), xloc.bar_index, extend.none, ewoColore[barIndex], line.style_solid, 2))

    longAlertCondition: Series = ta.crossover(ewo, ewoSignal)
    alertcondition(longAlertCondition, 'Long : Early Warning', 'EWOˢ - Probable Long Trade (Not Confirmed)\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')
    alertcondition(longAlertCondition[1], 'Long : Trading Opportunity', 'EWOˢ - Probable Long Trade Opportunity\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')

    shortAlertCondition: Series = ta.crossunder(ewo, ewoSignal)
    alertcondition(shortAlertCondition, 'Short : Early Warning', 'EWOˢ - Probable Short Trade (Not Confirmed)\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')
    alertcondition(shortAlertCondition[1], 'Short : Trading Opportunity', 'EWOˢ - Probable Short Trade Opportunity\n{{exchange}}:{{ticker}}\nPrice = {{close}}\nTime = {{time}}')

    bt_yAnchor = close

    stopLoss = __input_14__ / 100

    startBckTst = time > timenow - lenBckTst * 31556952000

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

        __block_result__ = na
        if _lbl:
            __block_result__ = label.new(bar_index, low if _d == 1 else high, text='L' if _d == 1 else 'S', tooltip='Direction .... : ' + ('Long' if _d == 1 else 'Short') + '\n' + 'Entry price .. : ' + string.tostring(open) + '\n' + 'Capital ...... : ' + string.tostring(bt_cap(), '#.##'), style=label.style_label_up if _d == 1 else label.style_label_down, color=color.teal if _d == 1 else color.red, textcolor=color.white, size=size.tiny, force_overlay=True)
        return __block_result__

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

    plot(bt_entry() if bt_dir() != 0 else bt_exit() if bt_exit() > 0 else na, 'Entry / Exit Price', color=color.teal if bt_dir() == 1 else color.red if bt_dir() == -1 else color.gray, style=plot.style_circles, display=display__ren__, editable=False, force_overlay=True)

    def f_kc(_src, _len, _mult, _maType, _style, _atrlen):
        range_1 = ta.rma(ta.tr(True), _len) if _style == 'True Range' else ta.atr(_atrlen) if _style == 'Average True Range' else ta.rma(high - low, _len) if _style == 'Range' else 0

        __block_result_1__ = na
        if _maType == 'DEMA':
            ema1 = ta.ema(_src, _len)
            ema2 = ta.ema(ema1, _len)
            __block_result_1__ = 2 * ema1 - ema2
        elif _maType == 'EMA':
            __block_result_1__ = ta.ema(_src, _len)
        elif _maType == 'HMA':
            __block_result_1__ = ta.hma(_src, _len)
        elif _maType == 'SMA':
            __block_result_1__ = ta.sma(_src, _len)
        elif _maType == 'WMA':
            __block_result_1__ = ta.wma(_src, _len)
        basis = __block_result_1__

        return (basis, basis + _mult * range_1, basis - _mult * range_1)

    middle, _, _ = f_kc(kcSource, kcLength, 0, kcMaType, '', 0)
    _, upper1, lower1 = f_kc(kcSource, kcLength, kcMult1, kcMaType, bandsStyle, atrlength)
    _, upper2, lower2 = f_kc(kcSource, kcLength, kcMult2, kcMaType, bandsStyle, atrlength)
    _, upper3, lower3 = f_kc(kcSource, kcLength, kcMult3, kcMaType, bandsStyle, atrlength)

    plot(middle if k else na, 'KC Middle', display=display__ren__, show_last=p)

    pu3 = plot(upper3 if k and isBand3 else na, 'KC Upper Band 3', color.new(colorK3, 73), math.max(1, widthK3), display=display__ren__, show_last=p)
    pu2 = plot(upper2 if k and isBand2 else na, 'KC Upper Band 2', color.new(colorK2, 73), math.max(1, widthK2), display=display__ren__, show_last=p)
    pu1 = plot(upper1 if k and isBand1 else na, 'KC Upper Band 1', color.new(colorK1, 73), math.max(1, widthK1), display=display__ren__, show_last=p)
    pl1 = plot(lower1 if k and isBand1 else na, 'KC Lower Band 1', color.new(colorK1, 73), math.max(1, widthK1), display=display__ren__, show_last=p)
    pl2 = plot(lower2 if k and isBand2 else na, 'KC Lower Band 2', color.new(colorK2, 73), math.max(1, widthK2), display=display__ren__, show_last=p)
    pl3 = plot(lower3 if k and isBand3 else na, 'KC Lower Band 3', color.new(colorK3, 73), math.max(1, widthK3), display=display__ren__, show_last=p)

    fill(pl2, pl3, color.new(color.green, 89) if bandsFill else na, 'KC Cloud Low', show_last=p)
    fill(pl1, pl2, color.new(color.new('#9EF2E8'), 89) if bandsFill else na, 'KC Cloud Lower', show_last=p)
    fill(pu1, pu2, color.new(color.new('#FA8072'), 89) if bandsFill else na, 'KC Cloud Higher', show_last=p)
    fill(pu2, pu3, color.new(color.red, 89) if bandsFill else na, 'KC Cloud High', show_last=p)

    alertcondition(ta.crossover(close, upper3), 'Crossover Upper High KC', 'Crossover Upper High KC Band\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(ta.crossover(close, upper2), 'Crossover Upper Mid KC', 'Crossover Upper Mid KC Band\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(ta.crossunder(close, lower2), 'Crossunder Lower Mid KC', 'Crossunder Lower Mid KC Band\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(ta.crossunder(close, lower3), 'Crossunder Lower Low KC', 'Crossunder Lower Low KC Band\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
