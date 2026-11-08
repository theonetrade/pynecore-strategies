"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, bgcolor, close, color,
    display, high, hl2, input, label, low, math, na, open, plot, position, script, size, string,
    syminfo, ta, table, text, time, timeframe, timenow, xloc
)
from pynecore.types import Label, Persistent, PersistentSeries, Series, Table

display__ren__ = display.all - display.status_line
btGR: str = '=============   Backtest Framework   ============='


@script.indicator('Logistic RSI, STOCH, ROC, AO, ... by DGT', 'LOGISTIC ☼☾', max_labels_count=500)
def main(
    ti=input.string('Logistic Dominance', 'Select Indicator', display=display__ren__, options=('Awesome Oscillator (AO)', 'Logistic Dominance', 'Rate of Change (ROC)', 'Relative Strength Index (RSI)', 'Stochastic (STOCH)'), tooltip='Select the base oscillator used as the input for the Logistic Map transformation.\n\n' + 'Available sources:\n' + '• AO – momentum derived from Awesome Oscillator\n' + '• Logistic Dominance – custom price-based dominance metric\n' + '• ROC – Rate of Change momentum\n' + '• RSI – Relative Strength Index\n' + '• STOCH – Stochastic oscillator\n\n' + 'The selected oscillator is transformed through a Logistic Map iteration process to highlight nonlinear momentum dynamics.'),
    source: Series[float] = input.source(close, 'Source', group='Logistic Settings', display=display__ren__),
    length=input.int(13, 'Logistic Map Length', minval=1, group='Logistic Settings', display=display__ren__, tooltip='Lookback period used when normalizing the input signal before applying the Logistic Map transformation.\n\n' + '• Higher values → smoother and more stable behavior\n' + '• Lower values → more reactive but noisier output\n\n' + 'Controls how sensitive the chaotic iterations are to short-term price changes.'),
    lenLD=input.int(5, 'Length : Logistic Dominance', minval=1, group='Optimization / Customization Metrics', display=display__ren__, tooltip='Lookback period used when the Logistic Dominance mode is selected as the base oscillator.\n\n' + 'Controls how price dominance and directional pressure are measured before the Logistic Map transformation.'),
    lenROC=input.int(9, 'Length : Rate of Change (ROC)', minval=1, group='Optimization / Customization Metrics', display=display__ren__, tooltip='Lookback period used for the Rate of Change oscillator.\n\n' + 'Only applied when ROC is selected as the base indicator.\n\n' + 'Higher values emphasize broader momentum trends, while lower values respond faster to short-term moves.'),
    lenRSI=input.int(14, 'Length : Relative Strength Index (RSI)', minval=1, group='Optimization / Customization Metrics', display=display__ren__, tooltip='Lookback period used for the RSI calculation.\n\n' + 'Only affects the indicator when RSI is selected as the base oscillator for the Logistic Map.'),
    lenSTO=input.int(14, 'Length : Stochastic (STOCH)', minval=1, group='Optimization / Customization Metrics', display=display__ren__, tooltip='Lookback period used for the Stochastic oscillator.\n\n' + 'Only applied when STOCH is selected in the "Select Indicator" setting.'),
    style=input.string('Cross', 'Style', group='Display Settings', display=display__ren__, options=('Cross', 'Line', 'StepLine'), tooltip='Visualization style for the Logistic Map iterations.\n\n' + '• Cross → discrete markers for each iteration\n' + '• Line → continuous line connecting iterations\n' + '• StepLine → stepped representation emphasizing\n' + '  discrete iteration levels.'),
    uC=input.color(color.teal, 'Colors : Bullish', inline='PLOT', group='Display Settings'),
    dC=input.color(color.red, 'Bearish', inline='PLOT', group='Display Settings'),
    d=input.bool(False, 'Standard Deviation Line Alone', group='Display Settings', tooltip='Display only the aggregated standard deviation\n' + 'of all Logistic Map iterations.\n\n' + '• ON → hides individual iterations and shows\n' + '  only the summarized volatility/momentum signal\n' + '• OFF → displays all Logistic Map iterations.'),
    isBackTest=input.bool(False, 'Enable Backtest', group=btGR, tooltip='Enable or disable the backtest framework.\n' + '• ON  → trades simulated using the rules below\n' + '• OFF → only live signals shown'),
    tradeMode=input.string('Both', 'Trade Mode', options=('Long Only', 'Short Only', 'Both'), group=btGR, display=display__ren__, tooltip='Defines which trade directions are simulated.\n\n' + '• Long Only  — enters on long signal, exits on short signal or stop loss\n' + '• Short Only — enters on short signal, exits on long signal or stop loss\n' + '• Both       — enters on either signal, optionally reverses on the opposite'),
    reverseOnSignal=input.bool(True, 'Reverse on Opposite Signal', group=btGR, tooltip='Only applies when Trade Mode is Both.\n' + 'When enabled, an opposite signal immediately closes the current trade\n' + 'and opens a new one in the other direction — always in trade once started.\n' + 'When disabled, opposite signal exits only — no new trade until next entry signal.'),
    dasCapital=input.float(1000.0, 'Initial Capital', group=btGR, display=display__ren__, tooltip='Starting capital for the simulation.\n' + 'Used to calculate compounding PnL and final equity.'),
    lenBckTst=input.float(1.0, 'Period (Years)', minval=0.0, step=0.1, group=btGR, display=display__ren__, tooltip='Lookback window for the simulation in years.\n' + 'Capped automatically if the selected timeframe has insufficient history.'),
    isStopLoss=input.bool(False, 'Apply Stop Loss', inline='sl', group=btGR, tooltip='Exits the trade if price moves against the position intrabar.\n' + 'Long SL : low  reaches entry × (1 − %)\n' + 'Short SL: high reaches entry × (1 + %)'),
    __input_17__=input.float(1.0, '  %', step=0.1, minval=0.0, inline='sl', group=btGR, display=display__ren__),
    useCandleL=input.bool(False, 'Long Candle Confirmation', group=btGR, tooltip='Long entries only taken on bullish bars (close > open).'),
    useCandleS=input.bool(False, 'Short Candle Confirmation', group=btGR, tooltip='Short entries only taken on bearish bars (close < open).'),
    isSudden=input.bool(True, 'Avoid Same-Bar Conflicts', group=btGR, tooltip='Skips entries when both long and short signals fire on the same bar.\n' + 'Reduces false entries from volatile spikes.'),
    isTest=input.bool(False, '❗ Next Bar Mode (Repaints)', group=btGR, tooltip="Uses the next bar's open for simulation instead of the confirmed bar open.\n" + 'Produces earlier entries but signals will repaint.\n' + 'For testing and comparison only — do not use for live alerts.'),
    lblInOutSL=input.bool(True, 'Show Entry / Exit Labels', group=btGR, tooltip='Displays L / S / SL / TP labels at entry and exit bars with tooltips showing direction, price, change, and capital.'),
    lblWarnings=input.bool(True, 'Show Early Warnings', group=btGR, tooltip='Shows a ⚠️ label when a signal fires but has not yet been confirmed.\n' + 'Label is deleted on the following bar regardless of outcome.'),
    lblTrdStat=input.bool(True, 'Show Trade Statistics', group=btGR, tooltip='Displays a floating label with full trade summary.\n' + 'Includes win rate, PnL, long/short breakdown, and current trade status.')
):
    def f_logmap(_s, _r, _l):
        return _r * _s / ta.highest(_l) * (1 - _s / ta.highest(_l))

    def f_map(_s, _r, _v):
        mapeq: Series = f_logmap(_s, _r, length)
        lmap = mapeq
        for i in pine_range(0, 29, 1):
            array.push(_v, lmap)
            lmap = _r * math.abs(mapeq[i]) * (1 - mapeq[i])
        return lmap

    __block_result__ = na
    if ti == 'Awesome Oscillator (AO)':
        __block_result__ = ta.sma(hl2, 5) / ta.sma(hl2, 34) - 1
    elif ti == 'Logistic Dominance':
        __block_result__ = -f_logmap(-source, ta.change(source, lenLD) / source[lenLD], lenLD) - f_logmap(source, ta.change(source, lenLD) / source[lenLD], lenLD)
    elif ti == 'Rate of Change (ROC)':
        __block_result__ = ta.change(source, lenROC) / source[lenROC]
    elif ti == 'Relative Strength Index (RSI)':
        __block_result__ = ta.rsi(source, lenRSI) / 100 - 0.5
    elif ti == 'Stochastic (STOCH)':
        __block_result__ = ta.stoch(source, high, low, lenSTO) / 100 - 0.5
    r = __block_result__

    v: Persistent[list[float]] = array.new_float(0)

    val = f_map(source, r, v)
    s = plot.style_cross if style == 'Cross' else plot.style_line if style == 'Line' else plot.style_stepline

    plot(na if d else val, 'Last Iteration', uC if val >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 1), '2nd Iteration', uC if array.get(v, 1) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 2), '3rd Iteration', uC if array.get(v, 2) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 3), '4th Iteration', uC if array.get(v, 3) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 4), '5th Iteration', uC if array.get(v, 4) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 5), '6th Iteration', uC if array.get(v, 5) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 6), '7th Iteration', uC if array.get(v, 6) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 7), '8th Iteration', uC if array.get(v, 7) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 8), '9th Iteration', uC if array.get(v, 8) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 9), '10th Iteration', uC if array.get(v, 9) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 10), '11th Iteration', uC if array.get(v, 10) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 11), '12th Iteration', uC if array.get(v, 11) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 12), '13th Iteration', uC if array.get(v, 12) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 13), '14th Iteration', uC if array.get(v, 13) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 14), '15th Iteration', uC if array.get(v, 14) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 15), '16th Iteration', uC if array.get(v, 15) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 16), '17th Iteration', uC if array.get(v, 16) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 17), '18th Iteration', uC if array.get(v, 17) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 18), '19th Iteration', uC if array.get(v, 18) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 19), '20th Iteration', uC if array.get(v, 19) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 20), '21st Iteration', uC if array.get(v, 20) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 21), '22nd Iteration', uC if array.get(v, 21) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 22), '23rd Iteration', uC if array.get(v, 22) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 23), '24th Iteration', uC if array.get(v, 23) >= 0 else dC, 1, s, display=display__ren__)
    plot(na if d else array.get(v, 24), '25th Iteration', uC if array.get(v, 24) >= 0 else dC, 1, s, display=display__ren__)

    plot(na if d else array.get(v, 26), '27th Iteration', uC if array.get(v, 26) >= 0 else dC, 1, s, display=display__ren__)

    plot(na if d else array.get(v, 28), '29th Iteration', uC if array.get(v, 28) >= 0 else dC, 1, s, display=display__ren__)

    array.remove(v, 0)
    aStDev = math.sign(array.avg(v)) * array.stdev(v)
    plot(aStDev, "Standard Deviation of Array's Elements", color.new('#26C6DA') if array.avg(v) >= 0 else color.new('#FFA726'), 2, display=display__ren__)
    array.clear(v)

    longAlertCondition: Series = ta.crossover(aStDev, 0)
    alertcondition(longAlertCondition, 'Long : Early Warning', 'LOGISTIC - Not Confirmed Probable Long Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(longAlertCondition[1], 'Long : Trading Opportunity', 'LOGISTIC - Probable Long Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    shortAlertCondition: Series = ta.crossunder(aStDev, 0)
    alertcondition(shortAlertCondition, 'Short : Early Warning', 'LOGISTIC - Not Confirmed Probable Short Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(shortAlertCondition[1], 'Short : Trading Opportunity', 'LOGISTIC - Probable Short Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    bt_yAnchor = close

    stopLoss = __input_17__ / 100

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

        __block_result_1__ = na
        if _lbl:
            __block_result_1__ = label.new(bar_index, low if _d == 1 else high, text='L' if _d == 1 else 'S', tooltip='Direction .... : ' + ('Long' if _d == 1 else 'Short') + '\n' + 'Entry price .. : ' + string.tostring(open) + '\n' + 'Capital ...... : ' + string.tostring(bt_cap(), '#.##'), style=label.style_label_up if _d == 1 else label.style_label_down, color=color.teal if _d == 1 else color.red, textcolor=color.white, size=size.tiny, force_overlay=True)
        return __block_result_1__

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