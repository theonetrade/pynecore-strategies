"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, bar_index, barmerge, barstate, bgcolor, close,
    color, display, fill, format, high, hline, input, label, low, math, na, nz, open, plot,
    plotcandle, position, request, script, size, string, syminfo, ta, table, volume, yloc
)
from pynecore.types import Color, NA, Persistent, Series, Table

GRP_OSC: str = 'Oscillator Settings'
GRP_SIG: str = 'Signal Governance'
GRP_FLT: str = 'Signal Filters'
GRP_RSK: str = 'Risk Management'
GRP_VIS: str = 'Visual'
GRP_ALR: str = 'Alerts'


@script.indicator('[blackcat] L3 Banker Fund Flow Trend Oscillator V2', overlay=False, max_labels_count=500)
def main(
    rawLen=input.int(27, 'Raw Stochastic Length', minval=2, group=GRP_OSC, tooltip='Lowest/Highest lookback of the raw stochastic. V1 hard-coded 27'),
    smoothFastLen=input.int(5, 'Fast Smoothing Length', minval=1, group=GRP_OSC, tooltip='First weighted smoothing length. V1 hard-coded 5'),
    smoothSlowLen=input.int(3, 'Slow Smoothing Length', minval=1, group=GRP_OSC, tooltip='Second weighted smoothing length. V1 hard-coded 3'),
    smoothWeight=input.float(1.0, 'Smoothing Weight', minval=0.0, step=0.5, group=GRP_OSC, tooltip='Weight of the weighted simple average. V1 hard-coded 1'),
    bandLen=input.int(34, 'Bull/Bear Band Length', minval=2, group=GRP_OSC, tooltip='Mid-term Fibonacci band length. V1 hard-coded 34'),
    bullBearEmaLen=input.int(13, 'Bull/Bear EMA Length', minval=1, group=GRP_OSC, tooltip='EMA length of the bull/bear line. V1 hard-coded 13'),
    declineRatio=input.float(0.95, 'Pullback Ratio', minval=0.5, maxval=1.0, step=0.01, group=GRP_OSC, tooltip='White candle prints when trend < previous trend * ratio. V1 hard-coded 0.95'),
    entryZone=input.float(25, 'Entry Zone Threshold', minval=0, maxval=100, group=GRP_OSC, tooltip='Bull/bear line must be below this for the banker entry signal. V1 hard-coded 25'),
    exitZone=input.float(75, 'Exit Zone Threshold', minval=0, maxval=100, group=GRP_OSC, tooltip='V2 new: mirror of the entry zone for the governed exit signal'),
    obLevel=input.float(80, 'Overbought Level', minval=50, maxval=100, group=GRP_OSC),
    strongLevel=input.float(90, 'Strong Level', minval=50, maxval=100, group=GRP_OSC),
    osLevel=input.float(20, 'Oversold Level', minval=0, maxval=50, group=GRP_OSC),
    weakLevel=input.float(10, 'Weak Level', minval=0, maxval=50, group=GRP_OSC),
    useExitSignal=input.bool(True, 'Enable Governed Exit Signal', group=GRP_SIG, tooltip='Mirror cross exit channel for long positions (trend crosses under the bull/bear line in the exit zone)'),
    useShortEntry=input.bool(True, 'Enable Short Entry Signals', group=GRP_SIG, tooltip='Adds the mirrored short side: SI entry, SO exit, RS re-entry. Channel toggles below are shared between long exits and short entries'),
    allowReverse=input.bool(True, 'Allow Reverse Entry (SAR)', group=GRP_SIG, tooltip='An opposite-direction signal while holding a position closes it and opens the reverse side (stop-and-reverse). When disabled, the opposite signal only closes the current position'),
    cooldownBars=input.int(3, 'Cooldown Bars', minval=0, group=GRP_SIG, tooltip='Minimum bars between governed signals (including RL/RS re-entries). 0 disables the cooldown'),
    useZoneEntry=input.bool(True, 'Zone Breakout Entry', group=GRP_SIG, tooltip='Long: bull/bear line crosses up through the entry zone. Short: bull/bear line crosses down through the exit zone'),
    useOsRecovery=input.bool(True, 'Oversold Recovery Entry', group=GRP_SIG, tooltip='Long: trend crosses up through the oversold level. Short exit uses the same upward event'),
    useObRollExit=input.bool(True, 'Overbought Rollover Exit', group=GRP_SIG, tooltip='Long exit: trend crosses down through the overbought level. Short entry uses the same downward event'),
    useFlipExit=input.bool(False, 'Trend-Line Flip Exit', group=GRP_SIG, tooltip='Trend crosses under the bull/bear line with no zone condition (frequent, enable with care)'),
    useVolFilter=input.bool(True, 'Require Volume Confirmation', group=GRP_FLT, tooltip='Entries (long and short) only when volume is above its SMA x multiplier: banker accumulation needs volume'),
    volLen=input.int(20, 'Volume SMA Length', minval=1, group=GRP_FLT),
    volMult=input.float(1.0, 'Volume Multiplier', minval=0.1, step=0.1, group=GRP_FLT),
    useStrengthFilter=input.bool(True, 'Require Trend Alignment on Entry', group=GRP_FLT, tooltip='Long entries only when the trend is rising, short entries only when the trend is falling'),
    useHtfFilter=input.bool(False, 'Higher-Timeframe Trend Filter', group=GRP_FLT, tooltip='Long entries only when HTF close is above HTF EMA, short entries only when below. Uses confirmed HTF values only (no repaint)'),
    htfTf=input.timeframe('240', 'Filter Timeframe', group=GRP_FLT),
    htfLen=input.int(50, 'HTF EMA Length', minval=1, group=GRP_FLT),
    useNoiseFilter=input.bool(False, 'Skip Wide-Range Bars', group=GRP_FLT, tooltip='Skip entries when the bar range exceeds ATR x multiplier (volatility spike)'),
    maxRangeMult=input.float(2.5, 'Max Range x ATR', minval=0.5, step=0.5, group=GRP_FLT),
    hysteresis=input.float(0.0, 'Cross Hysteresis (points)', minval=0, maxval=25, step=0.5, group=GRP_FLT, tooltip='Trend must exceed the bull/bear line by this margin for the cross entry/exit. 0 disables'),
    noiseSmoothLen=input.int(1, 'Extra Smoothing Length', minval=1, group=GRP_FLT, tooltip='Extra EMA smoothing applied to the trend before all signals and visuals. 1 disables (V1 behavior)'),
    useAtrStops=input.bool(True, 'Enable ATR Take-Profit/Stop-Loss', group=GRP_RSK, tooltip='On governed entry, locks ATR-based TP and SL levels shown on the price chart'),
    atrLen=input.int(14, 'ATR Length', minval=1, group=GRP_RSK),
    tpMult=input.float(3.0, 'Take Profit x ATR', minval=0.5, step=0.5, group=GRP_RSK),
    slMult=input.float(1.5, 'Stop Loss x ATR', minval=0.5, step=0.5, group=GRP_RSK),
    showDash=input.bool(True, 'Show Status Dashboard', group=GRP_VIS),
    showBg=input.bool(True, 'Show Bull/Bear Background', group=GRP_VIS),
    showLabels=input.bool(True, 'Show Entry/Exit Labels', group=GRP_VIS),
    showTrendLine=input.bool(True, 'Show Trend Line', group=GRP_VIS),
    showTpSl=input.bool(True, 'Show Entry/TP/SL on Price Chart', group=GRP_VIS),
    showSignalLabels=input.bool(True, 'Show Signal Labels (IN/OUT/TP/SL)', group=GRP_VIS, tooltip='Governed signals as text labels: IN/OUT on the oscillator, TP/SL on the price chart, with trigger-channel abbreviations in the text and tooltip'),
    enableAlerts=input.bool(True, 'Enable alert() Messages', group=GRP_ALR)
):
    def find_recent_value(values: Series, length):
        recent_value = NA(float)
        if length >= 1:
            for i in pine_range(0, length, 1):
                if na(recent_value) or not na(values[i]):
                    recent_value = values[i]
        return recent_value

    def calculate_weighted_simple_average(src: Series, length, weight):
        sum_float: Series[float] = 0.0
        moving_average: float = 0.0
        output: Series[float] = 0.0
        sum_float = nz(sum_float[1]) - nz(src[length]) + src
        moving_average = na if na(src[length]) else sum_float / length
        output = moving_average if na(output[1]) else (src * weight + output[1] * (length - weight)) / length
        return output

    def calculate_banker_fund_flow(close, low, high, open):
        typical_price = (2 * close + high + low + open) / 5

        lowest_low = ta.lowest(low, bandLen)
        highest_high = ta.highest(high, bandLen)

        raw_low = ta.lowest(low, rawLen)
        raw_high = ta.highest(high, rawLen)
        raw_range = raw_high - raw_low
        raw_stoch = NA(float) if raw_range == 0 else (close - raw_low) / raw_range * 100

        fast_smooth = calculate_weighted_simple_average(raw_stoch, smoothFastLen, smoothWeight)
        slow_smooth = calculate_weighted_simple_average(fast_smooth, smoothSlowLen, smoothWeight)
        fund_flow_trend = (3 * fast_smooth - 2 * slow_smooth - 50) * 1.032 + 50

        band_range = highest_high - lowest_low
        bull_bear_line = ta.ema(NA(float) if band_range == 0 else (typical_price - lowest_low) / band_range * 100, bullBearEmaLen)

        banker_entry_signal = ta.crossover(fund_flow_trend, bull_bear_line) and bull_bear_line < entryZone
        banker_exit_signal = ta.crossunder(fund_flow_trend, bull_bear_line) and bull_bear_line > exitZone

        return (fund_flow_trend, bull_bear_line, banker_entry_signal, banker_exit_signal)

    fund_flow_trend: Series
    fund_flow_trend, bull_bear_line, banker_entry_signal, banker_exit_signal = calculate_banker_fund_flow(close, low, high, open)

    fund_flow_trend = ta.ema(fund_flow_trend, noiseSmoothLen)
    banker_entry_signal = ta.crossover(fund_flow_trend, bull_bear_line) and bull_bear_line < entryZone
    banker_exit_signal = ta.crossunder(fund_flow_trend, bull_bear_line) and bull_bear_line > exitZone

    atrVal: float = ta.atr(atrLen)
    volSma: float = ta.sma(volume, volLen)
    crossLevel: float = bull_bear_line + hysteresis

    htfClose, htfEma = request.security(syminfo.tickerid, htfTf, (close[1], inline_series(ta.ema(close, htfLen), 1)), lookahead=barmerge.lookahead_off)
    htfBull: bool = htfClose > htfEma

    volOK: bool = not useVolFilter or volume > volSma * volMult
    strengthLongOK: bool = not useStrengthFilter or fund_flow_trend > fund_flow_trend[1]
    strengthShortOK: bool = not useStrengthFilter or fund_flow_trend < fund_flow_trend[1]
    noiseOK: bool = not useNoiseFilter or high - low < atrVal * maxRangeMult
    htfBullOK: bool = not useHtfFilter or htfBull
    htfBearOK: bool = not useHtfFilter or not htfBull
    confirmGateLong: bool = volOK and strengthLongOK and noiseOK and htfBullOK
    confirmGateShort: bool = volOK and strengthShortOK and noiseOK and htfBearOK

    crossEntry: bool = ta.crossover(fund_flow_trend, crossLevel) and bull_bear_line < entryZone
    zoneEntryCross: bool = ta.crossover(bull_bear_line, entryZone)
    osRecoverCross: bool = ta.crossover(fund_flow_trend, osLevel)

    mirrorExitCross: bool = ta.crossunder(fund_flow_trend, crossLevel)
    obRollCross: bool = ta.crossunder(fund_flow_trend, obLevel)
    flipCross: bool = ta.crossunder(fund_flow_trend, bull_bear_line)
    zoneShortCross: bool = ta.crossunder(bull_bear_line, exitZone)

    zoneEntry: bool = useZoneEntry and zoneEntryCross
    osRecoverEntry: bool = useOsRecovery and osRecoverCross
    anyEntry: bool = crossEntry or zoneEntry or osRecoverEntry

    mirrorExit: bool = useExitSignal and mirrorExitCross and (bull_bear_line > exitZone)
    obRollExit: bool = useObRollExit and obRollCross
    flipExit: bool = useFlipExit and flipCross
    anyExit: bool = mirrorExit or obRollExit or flipExit

    shortCross: bool = mirrorExitCross and bull_bear_line > exitZone
    shortZone: bool = useZoneEntry and zoneShortCross
    shortObRoll: bool = useObRollExit and obRollCross
    shortFlip: bool = useFlipExit and flipCross
    anyShortEntry: bool = useShortEntry and (shortCross or shortZone or shortObRoll or shortFlip)

    posState: Persistent[int] = 0
    lastSignalBar: Persistent[int] = -1
    entryCount: Persistent[int] = 0
    exitCount: Persistent[int] = 0
    reLongCount: Persistent[int] = 0
    reShortCount: Persistent[int] = 0
    entryPrice: Persistent[float] = na(float)
    tpPrice: Persistent[float] = na(float)
    slPrice: Persistent[float] = na(float)
    cooldownOK: bool = lastSignalBar < 0 or bar_index - lastSignalBar > cooldownBars
    longEntryOK: bool = anyEntry and confirmGateLong
    shortEntryOK: bool = anyShortEntry and confirmGateShort
    longEvt: bool = longEntryOK and cooldownOK
    shortEvt: bool = shortEntryOK and cooldownOK
    longExitEvt: bool = anyEntry and cooldownOK
    shortExitEvt: bool = (anyExit or anyShortEntry) and cooldownOK
    govEntry: bool = False
    govExit: bool = False
    govShortEntry: bool = False
    govShortExit: bool = False
    govReLong: bool = False
    govReShort: bool = False
    reversedToLong: bool = False
    reversedToShort: bool = False
    if cooldownOK:
        if posState == 0:
            if longEvt:
                govEntry = True
            elif shortEvt:
                govShortEntry = True
        elif posState == 1:
            if longEvt:
                govReLong = True
            elif shortExitEvt:
                if allowReverse and shortEntryOK:
                    govShortEntry = True
                    reversedToShort = True
                else:
                    govExit = True
        else:
            if shortEvt:
                govReShort = True
            elif longExitEvt:
                if allowReverse and longEntryOK:
                    govEntry = True
                    reversedToLong = True
                else:
                    govShortExit = True

    if govEntry:
        posState = 1
        lastSignalBar = bar_index
        entryCount += 1
        if reversedToLong:
            exitCount += 1
        if useAtrStops:
            entryPrice = close
            tpPrice = close + atrVal * tpMult
            slPrice = close - atrVal * slMult
    if govShortEntry:
        posState = -1
        lastSignalBar = bar_index
        entryCount += 1
        if reversedToShort:
            exitCount += 1
        if useAtrStops:
            entryPrice = close
            tpPrice = close - atrVal * tpMult
            slPrice = close + atrVal * slMult
    if govReLong:
        lastSignalBar = bar_index
        reLongCount += 1
        if useAtrStops:
            entryPrice = close
            tpPrice = close + atrVal * tpMult
            slPrice = close - atrVal * slMult
    if govReShort:
        lastSignalBar = bar_index
        reShortCount += 1
        if useAtrStops:
            entryPrice = close
            tpPrice = close - atrVal * tpMult
            slPrice = close + atrVal * slMult
    if govExit or govShortExit:
        posState = 0
        lastSignalBar = bar_index
        exitCount += 1
        entryPrice = na
        tpPrice = na
        slPrice = na

    tpHit: bool = useAtrStops and (not na(tpPrice)) and (posState == 1 and high >= tpPrice or (posState == -1 and low <= tpPrice))
    slHit: bool = useAtrStops and (not na(slPrice)) and (posState == 1 and low <= slPrice or (posState == -1 and high >= slPrice))
    if tpHit or slHit:
        posState = 0
        lastSignalBar = bar_index
        exitCount += 1
        entryPrice = na
        tpPrice = na
        slPrice = na

    pullbackRef: float = find_recent_value(fund_flow_trend * declineRatio, 1)
    isYellow: bool = banker_entry_signal
    isGreen: bool = fund_flow_trend > bull_bear_line
    isWhite: bool = fund_flow_trend < pullbackRef
    isRed: bool = fund_flow_trend < bull_bear_line
    isBlue: bool = fund_flow_trend < bull_bear_line and fund_flow_trend > pullbackRef

    plotcandle(0, 50, 0, 50, title='Banker Entry', color=color.new(color.yellow, 0) if isYellow else na, bordercolor=na)

    plotcandle(fund_flow_trend, bull_bear_line, fund_flow_trend, bull_bear_line, title='Banker Increase', color=color.new(color.green, 0) if isGreen else na, bordercolor=na)

    plotcandle(fund_flow_trend, bull_bear_line, fund_flow_trend, bull_bear_line, title='Banker Decrease', color=color.new(color.white, 0) if isWhite else na, bordercolor=na)

    plotcandle(fund_flow_trend, bull_bear_line, fund_flow_trend, bull_bear_line, title='Banker Exit', color=color.new(color.red, 0) if isRed else na, bordercolor=na)

    plotcandle(fund_flow_trend, bull_bear_line, fund_flow_trend, bull_bear_line, title='Banker Rebound', color=color.new(color.blue, 0) if isBlue else na, bordercolor=na)

    plot(fund_flow_trend if showTrendLine else na, 'Fund Flow Trend Line', color=color.new(color.yellow, 0) if isYellow else color.new(color.green, 0) if isGreen else color.new(color.white, 0) if isWhite else color.new(color.red, 0) if isRed else color.new(color.blue, 0), linewidth=2)

    plot(entryPrice if showTpSl and useAtrStops else na, 'Entry Price', color=color.new(color.gray, 0), style=plot.style_linebr, force_overlay=True)
    plot(tpPrice if showTpSl and useAtrStops else na, 'Take Profit', color=color.new(color.teal, 0), style=plot.style_linebr, force_overlay=True)
    plot(slPrice if showTpSl and useAtrStops else na, 'Stop Loss', color=color.new(color.maroon, 0), style=plot.style_linebr, force_overlay=True)

    overbought_threshold = hline(obLevel, title='Overbought', color=color.red, linestyle=hline.style_dotted)
    oversold_threshold = hline(osLevel, title='Oversold', color=color.yellow, linestyle=hline.style_dotted)
    weak_threshold = hline(weakLevel, title='Weak', color=color.lime, linestyle=hline.style_dotted)
    strong_threshold = hline(strongLevel, title='Strong', color=color.fuchsia, linestyle=hline.style_dotted)
    fill(oversold_threshold, weak_threshold, color=color.new(color.yellow, 70))
    fill(overbought_threshold, strong_threshold, color=color.new(color.fuchsia, 70))

    bgcolor((color.new(color.green, 92) if isGreen else color.new(color.red, 92) if isRed else na) if showBg else na, title='Bull/Bear Background')

    if showLabels and banker_entry_signal:
        label.new(bar_index, fund_flow_trend, 'Banker In', style=label.style_label_up, color=color.new(color.yellow, 10), textcolor=color.black, size=size.small)

    if showSignalLabels and govEntry:
        entryLbl: str = ('IN ·R' if reversedToLong else 'IN') + (' ·XB' if crossEntry else '') + (' ·ZB' if zoneEntry else '') + (' ·OSR' if osRecoverEntry else '')
        label.new(bar_index, fund_flow_trend, entryLbl, style=label.style_label_up, color=color.new(color.lime, 10), textcolor=color.black, size=size.small, tooltip=('Reverse: close short, open long\n' if reversedToLong else '') + 'Governed long entry @ ' + string.tostring(close, format.mintick) + ('\nTP ' + string.tostring(tpPrice, format.mintick) + ' | SL ' + string.tostring(slPrice, format.mintick) if useAtrStops else ''))
    if showSignalLabels and govExit:
        exitLbl: str = 'OUT' + (' ·MX' if mirrorExit else '') + (' ·OBR' if obRollExit else '') + (' ·FL' if flipExit else '')
        label.new(bar_index, fund_flow_trend, exitLbl, style=label.style_label_down, color=color.new(color.orange, 10), textcolor=color.white, size=size.small)
    if showSignalLabels and govShortEntry:
        shortLbl: str = ('SI ·R' if reversedToShort else 'SI') + (' ·MX' if shortCross else '') + (' ·ZD' if shortZone else '') + (' ·OBR' if shortObRoll else '') + (' ·FL' if shortFlip else '')
        label.new(bar_index, fund_flow_trend, shortLbl, style=label.style_label_down, color=color.new(color.fuchsia, 10), textcolor=color.white, size=size.small, tooltip=('Reverse: close long, open short\n' if reversedToShort else '') + 'Governed short entry @ ' + string.tostring(close, format.mintick) + ('\nTP ' + string.tostring(tpPrice, format.mintick) + ' | SL ' + string.tostring(slPrice, format.mintick) if useAtrStops else ''))
    if showSignalLabels and govShortExit:
        shortExitLbl: str = 'SO' + (' ·XB' if crossEntry else '') + (' ·ZB' if zoneEntry else '') + (' ·OSR' if osRecoverEntry else '')
        label.new(bar_index, fund_flow_trend, shortExitLbl, style=label.style_label_up, color=color.new(color.blue, 10), textcolor=color.white, size=size.small)
    if showSignalLabels and govReLong:
        reLongLbl: str = 'RL' + (' ·XB' if crossEntry else '') + (' ·ZB' if zoneEntry else '') + (' ·OSR' if osRecoverEntry else '')
        label.new(bar_index, fund_flow_trend, reLongLbl, style=label.style_label_up, color=color.new(color.teal, 10), textcolor=color.white, size=size.small, tooltip='Re-entry long: levels refreshed @ ' + string.tostring(close, format.mintick) + ('\nTP ' + string.tostring(tpPrice, format.mintick) + ' | SL ' + string.tostring(slPrice, format.mintick) if useAtrStops else ''))
    if showSignalLabels and govReShort:
        reShortLbl: str = 'RS' + (' ·MX' if shortCross else '') + (' ·ZD' if shortZone else '') + (' ·OBR' if shortObRoll else '') + (' ·FL' if shortFlip else '')
        label.new(bar_index, fund_flow_trend, reShortLbl, style=label.style_label_down, color=color.new(color.purple, 10), textcolor=color.white, size=size.small, tooltip='Re-entry short: levels refreshed @ ' + string.tostring(close, format.mintick) + ('\nTP ' + string.tostring(tpPrice, format.mintick) + ' | SL ' + string.tostring(slPrice, format.mintick) if useAtrStops else ''))
    if showSignalLabels and tpHit:
        label.new(bar_index, na, 'TP', yloc=yloc.abovebar, style=label.style_label_down, color=color.new(color.teal, 0), textcolor=color.white, size=size.small, force_overlay=True)
    if showSignalLabels and slHit:
        label.new(bar_index, na, 'SL', yloc=yloc.belowbar, style=label.style_label_up, color=color.new(color.maroon, 0), textcolor=color.white, size=size.small, force_overlay=True)

    plot(posState, 'Governed Position State', display=display.data_window)

    dash: Persistent[Table] = table.new(position.top_right, 2, 10, bgcolor=color.new(color.black, 60), border_width=1)
    if showDash and barstate.islast:
        stateTxt: str = 'Increase (Green)' if isGreen else 'Decrease (White)' if isWhite else 'Weak Rebound (Blue)' if isBlue else 'Exit (Red)'
        stateColor: Color = color.green if isGreen else color.red if isRed else color.yellow if isYellow else color.blue
        posTxt: str = 'LONG #' + string.tostring(entryCount) if posState == 1 else 'SHORT #' + string.tostring(entryCount) if posState == -1 else 'FLAT'
        posColor: Color = color.lime if posState == 1 else color.fuchsia if posState == -1 else color.white
        entryTxt: str = string.tostring(entryPrice, format.mintick) if not na(entryPrice) else '-'
        tpTxt: str = string.tostring(tpPrice, format.mintick) if not na(tpPrice) else '-'
        slTxt: str = string.tostring(slPrice, format.mintick) if not na(slPrice) else '-'
        distTxt: str = string.tostring(math.abs(tpPrice - close) / close * 100, '#.##') + '% / ' + string.tostring(math.abs(slPrice - close) / close * 100, '#.##') + '%' if not na(tpPrice) else '-'
        pnlTxt: str = string.tostring((close - entryPrice) / entryPrice * 100, '#.##') + '%' if posState == 1 and (not na(entryPrice)) else string.tostring((entryPrice - close) / entryPrice * 100, '#.##') + '%' if posState == -1 and (not na(entryPrice)) else '-'
        filterTxt: str = ('Vol+ ' if volOK else 'Vol- ') + ('StrL+ ' if strengthLongOK else 'StrL- ') + ('StrS+ ' if strengthShortOK else 'StrS- ') + ('Rng+ ' if noiseOK else 'Rng- ') + ('HTF+' if htfBullOK else 'HTF-')
        sigTxt: str = ('Ready' if cooldownOK else 'Wait') + ' | In ' + string.tostring(entryCount) + ' Out ' + string.tostring(exitCount) + ' | RL ' + string.tostring(reLongCount) + ' RS ' + string.tostring(reShortCount)
        table.cell(dash, 0, 0, 'Fund Flow Trend', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 0, string.tostring(fund_flow_trend, '#.##'), text_color=stateColor, text_size=size.tiny)
        table.cell(dash, 0, 1, 'Bull/Bear Line', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 1, string.tostring(bull_bear_line, '#.##'), text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 2, 'Candle State', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 2, stateTxt, text_color=stateColor, text_size=size.tiny)
        table.cell(dash, 0, 3, 'Governed Position', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 3, posTxt, text_color=posColor, text_size=size.tiny)
        table.cell(dash, 0, 4, 'Entry Price', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 4, entryTxt, text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 5, 'TP / SL', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 5, tpTxt + ' / ' + slTxt, text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 6, 'TP/SL Distance', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 6, distTxt, text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 7, 'Open P&L', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 7, pnlTxt, text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 8, 'Entry Filters', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 8, filterTxt, text_color=color.lime if confirmGateLong or confirmGateShort else color.orange, text_size=size.tiny)
        table.cell(dash, 0, 9, 'Cooldown | Signals', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 9, sigTxt, text_color=color.white, text_size=size.tiny)

    alertcondition(banker_entry_signal, title='Alert on Yellow Candle', message='Yellow Candle!')
    alertcondition(fund_flow_trend > bull_bear_line, title='Alert on Green Candle', message='Green Candle!')
    alertcondition(fund_flow_trend < pullbackRef, title='Alert on White Candle', message='White Candle!')
    alertcondition(fund_flow_trend < bull_bear_line, title='Alert on Red Candle', message='Red Candle!')
    alertcondition(fund_flow_trend < bull_bear_line and fund_flow_trend > pullbackRef, title='Alert on Blue Candle', message='Blue Candle!')

    alertcondition(govEntry, title='Governed Banker Entry', message='Long entry: confirmed by filters and governance')
    alertcondition(govExit, title='Governed Banker Exit', message='Long exit: trend crossed under bull/bear line in exit zone')
    alertcondition(govShortEntry, title='Governed Short Entry', message='Short entry: confirmed by filters and governance')
    alertcondition(govShortExit, title='Governed Short Exit', message='Short exit: upward cross closed the short side')
    alertcondition(govReLong, title='Re-entry Long', message='Re-entry long: long signal re-fired while long, levels refreshed')
    alertcondition(govReShort, title='Re-entry Short', message='Re-entry short: short signal re-fired while short, levels refreshed')
    alertcondition(tpHit, title='Take Profit Hit', message='TP hit: price reached the ATR take-profit level')
    alertcondition(slHit, title='Stop Loss Hit', message='SL hit: price reached the ATR stop-loss level')
    if enableAlerts and govEntry:
        alert(('Reverse to long' if reversedToLong else 'Long entry') + ' @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and govExit:
        alert('Long exit @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and govShortEntry:
        alert(('Reverse to short' if reversedToShort else 'Short entry') + ' @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and govShortExit:
        alert('Short exit @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and govReLong:
        alert('Re-entry long @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and govReShort:
        alert('Re-entry short @ ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and tpHit:
        alert('TP hit @ ' + string.tostring(tpPrice, format.mintick), alert.freq_once_per_bar_close)
    if enableAlerts and slHit:
        alert('SL hit @ ' + string.tostring(slPrice, format.mintick), alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
