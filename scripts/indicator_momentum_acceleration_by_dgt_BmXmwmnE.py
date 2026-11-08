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
    extend, high, input, label, last_bar_index, line, location, low, math, na, open, plot,
    plotarrow, plotshape, position, script, shape, size, string, syminfo, ta, table, text, time,
    timeframe, timenow, xloc
)
from pynecore.types import Label, Line, Persistent, PersistentSeries, Series, Table

display__ren__ = display.all - display.status_line
group_sg: str = 'Momentum Acceleration Engine'
group_ocs: str = 'Oscillator Projection View'
btGR: str = '=============   Backtest Framework   ============='


@script.indicator('Momentum Acceleration by DGT', 'SpeedyGonzales ☼☾', True, max_lines_count=500)
def main(
    s=input.string('Price', 'Data Source', options=('Price', 'On Balance Volume'), group=group_sg, display=display__ren__, tooltip='Select the data used to calculate momentum acceleration.\n\n' + '• Price → Uses market price movement\n' + '• On Balance Volume → Uses volume flow dynamics'),
    t=input.int(13, '  Acceleration Period', group=group_sg, display=display__ren__, tooltip='Controls how quickly momentum acceleration reacts to market changes.\n\n' + 'Lower values → Faster and more sensitive\n' + 'Higher values → Smoother and more stable'),
    colorup=input.color(color.new(color.aqua, 80), '  Bullish Color', inline='COL', group=group_sg, tooltip='Color used when momentum acceleration is positive.'),
    colordown=input.color(color.new(color.orange, 80), 'Bearish Color', inline='COL', group=group_sg, tooltip='Color used when momentum acceleration is negative.'),
    p=input.int(233, '  Display Length', minval=1, step=10, group=group_sg, display=display__ren__, tooltip='Number of recent bars shown for momentum arrows.'),
    price=input.bool(False, 'Show Price Acceleration', inline='price', group=group_ocs, tooltip='Projects price-based momentum acceleration onto the chart.'),
    oscColor=input.color(color.aqua, '', inline='price', group=group_ocs),
    obv=input.bool(False, 'Show OBV Acceleration', inline='obv', group=group_ocs, tooltip='Projects On Balance Volume momentum acceleration onto the chart.'),
    oscColor2=input.color(color.orange, '', inline='obv', group=group_ocs),
    __input_9__=input.int(7, '  Scale', minval=1, maxval=10, inline='AA', group=group_ocs, display=display__ren__),
    __input_10__=input.int(3, 'Offset', minval=-3, maxval=10, inline='AA', group=group_ocs, display=display__ren__, tooltip='Scale:\nControls vertical scaling of the projected oscillator.\n\nOffset:\nAdjusts vertical placement of the oscillator projection.'),
    oscPlacement=input.string('Bottom', '  Placement', options=('Top', 'Bottom'), group=group_ocs, display=display__ren__, tooltip='Select where the oscillator is drawn relative to price.'),
    isBackTest=input.bool(False, 'Enable Backtest', group=btGR, tooltip='Enable or disable the backtest framework.\n' + '• ON  → trades simulated using the rules below\n' + '• OFF → only live signals shown'),
    tradeMode=input.string('Both', 'Trade Mode', options=('Long Only', 'Short Only', 'Both'), group=btGR, display=display__ren__, tooltip='Defines which trade directions are simulated.\n\n' + '• Long Only  — enters on long signal, exits on short signal or stop loss\n' + '• Short Only — enters on short signal, exits on long signal or stop loss\n' + '• Both       — enters on either signal, optionally reverses on the opposite'),
    reverseOnSignal=input.bool(True, 'Reverse on Opposite Signal', group=btGR, tooltip='Only applies when Trade Mode is Both.\n' + 'When enabled, an opposite signal immediately closes the current trade\n' + 'and opens a new one in the other direction — always in trade once started.\n' + 'When disabled, opposite signal exits only — no new trade until next entry signal.'),
    dasCapital=input.float(1000.0, 'Initial Capital', group=btGR, display=display__ren__, tooltip='Starting capital for the simulation.\n' + 'Used to calculate compounding PnL and final equity.'),
    lenBckTst=input.float(1.0, 'Period (Years)', minval=0.0, step=0.1, group=btGR, display=display__ren__, tooltip='Lookback window for the simulation in years.\n' + 'Capped automatically if the selected timeframe has insufficient history.'),
    isStopLoss=input.bool(False, 'Apply Stop Loss', inline='sl', group=btGR, tooltip='Exits the trade if price moves against the position intrabar.\n' + 'Long SL : low  reaches entry × (1 − %)\n' + 'Short SL: high reaches entry × (1 + %)'),
    __input_18__=input.float(1.0, '  %', step=0.1, minval=0.0, inline='sl', group=btGR, display=display__ren__),
    useCandleL=input.bool(False, 'Long Candle Confirmation', group=btGR, tooltip='Long entries only taken on bullish bars (close > open).'),
    useCandleS=input.bool(False, 'Short Candle Confirmation', group=btGR, tooltip='Short entries only taken on bearish bars (close < open).'),
    isSudden=input.bool(True, 'Avoid Same-Bar Conflicts', group=btGR, tooltip='Skips entries when both long and short signals fire on the same bar.\n' + 'Reduces false entries from volatile spikes.'),
    isTest=input.bool(False, '❗ Next Bar Mode (Repaints)', group=btGR, tooltip="Uses the next bar's open for simulation instead of the confirmed bar open.\n" + 'Produces earlier entries but signals will repaint.\n' + 'For testing and comparison only — do not use for live alerts.'),
    lblInOutSL=input.bool(True, 'Show Entry / Exit Labels', group=btGR, tooltip='Displays L / S / SL / TP labels at entry and exit bars with tooltips showing direction, price, change, and capital.'),
    lblWarnings=input.bool(True, 'Show Early Warnings', group=btGR, tooltip='Shows a ⚠️ label when a signal fires but has not yet been confirmed.\n' + 'Label is deleted on the following bar regardless of outcome.'),
    lblTrdStat=input.bool(True, 'Show Trade Statistics', group=btGR, tooltip='Displays a floating label with full trade summary.\n' + 'Includes win rate, PnL, long/short breakdown, and current trade status.')
):
    def f_speedy(_d, _t):
        v = ta.sma(ta.change(_d, _t) / _t, 3)
        a = ta.change(v, _t) / _t
        return v - a

    source = close if s == 'Price' else ta.obv
    psgval: Series = f_speedy(source, t)
    plotarrow(psgval, title='Momentum Acceleration', colorup=colorup, colordown=colordown, display=display__ren__, show_last=p)
    plotshape(psgval > 0 and psgval[1] <= 0, 'Bull', shape.triangleup, location.belowbar, color.new(colorup, 25), size=size.tiny, display=display__ren__, show_last=p)
    plotshape(psgval < 0 and psgval[1] >= 0, 'Bear', shape.triangledown, location.abovebar, color.new(colordown, 25), size=size.tiny, display=display__ren__, show_last=p)

    bothAlertCondition: Series = ta.cross(psgval, 0)
    alertcondition(bothAlertCondition, 'Early Warning', 'SpeedyGonzales : Probable Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(bothAlertCondition[1], 'Trading Opportunity', 'SpeedyGonzales : Probable Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    longAlertCondition: Series = ta.crossover(psgval, 0)
    alertcondition(longAlertCondition, 'Long : Early Warning', 'SpeedyGonzales - Not Confirmed Probable Long Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(longAlertCondition[1], 'Long : Trading Opportunity', 'SpeedyGonzales - Probable Long Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    shortAlertCondition: Series = ta.crossunder(psgval, 0)
    alertcondition(shortAlertCondition, 'Short : Early Warning', 'SpeedyGonzales - Not Confirmed Probable Short Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')
    alertcondition(shortAlertCondition[1], 'Short : Trading Opportunity', 'SpeedyGonzales - Probable Short Trade Opportunity\n{{exchange}}:{{ticker}}->\nPrice = {{close}},\nTime = {{time}}')

    oscHight = 11 - __input_9__

    oscVerticalOffset = __input_10__ / 10

    oscLookbackLength = math.min(last_bar_index, p)

    a_lines: Persistent[list[Line]] = array.new_line()

    oscPrice: Series = f_speedy(close, t)
    oscObv: Series = f_speedy(ta.obv, t)
    priceHighest = ta.highest(high, oscLookbackLength)
    priceLowest = ta.lowest(low, oscLookbackLength)
    priceChangeRate = (priceHighest - priceLowest) / priceHighest
    priceLowest = priceLowest * (1 - priceChangeRate * oscVerticalOffset)
    priceHighest = priceHighest * (1 + priceChangeRate * oscVerticalOffset)
    oscHighest = ta.highest(oscPrice, oscLookbackLength)
    oscHighest2 = ta.highest(oscObv, oscLookbackLength)

    if barstate.islast:
        if array.size(a_lines) > 0:
            __loop_2__ = pine_loop(1, 1)
            while __loop_2__.step(array.size(a_lines)):
                i = __loop_2__.value
                line.delete(array.shift(a_lines))

        hight = priceChangeRate / oscHight

        if price or obv:
            midLine: int = 0
            midLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + midLine / oscHighest * hight)
            array.push(a_lines, line.new(bar_index[oscLookbackLength], midLevel, bar_index, midLevel, xloc.bar_index, extend.none, color.new(color.gray, 25), line.style_dashed, 1))

        for barIndex in pine_range(0, oscLookbackLength - 1, 1):
            if array.size(a_lines) < 498:
                if price:
                    array.push(a_lines, line.new(bar_index[barIndex], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + oscPrice[barIndex] / oscHighest * hight), bar_index[barIndex + 1], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + oscPrice[barIndex + 1] / oscHighest * hight), xloc.bar_index, extend.none, oscColor, line.style_solid, 1))
                if obv:
                    array.push(a_lines, line.new(bar_index[barIndex], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + oscObv[barIndex] / oscHighest2 * hight), bar_index[barIndex + 1], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + oscObv[barIndex + 1] / oscHighest2 * hight), xloc.bar_index, extend.none, oscColor2, line.style_solid, 1))

    bt_yAnchor = close

    stopLoss = __input_18__ / 100

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

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)