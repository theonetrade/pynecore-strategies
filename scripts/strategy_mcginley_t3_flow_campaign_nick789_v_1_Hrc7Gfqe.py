"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, barcolor, barstate, bgcolor, chart, close, color, fill,
    format, high, input, label, line, location, low, math, na, nz, plot, plotshape, position,
    script, shape, size, strategy, string, syminfo, ta, table, time, timeframe, timenow, timestamp,
    xloc
)
from pynecore.types import Color, Label, Line, Persistent, PersistentSeries, Series, Table


@udt
class FlowCampaign:
    side: int = na(int)
    startBar: int = na(int)
    finishBar: int = na(int)
    entry: float = na(float)
    t1: float = na(float)
    t2: float = na(float)
    t3: float = na(float)
    sl: float = na(float)
    active: bool = na(bool)


G_TIME: str = "01. Backtest Window"
G_ENGINE: str = "02. Signal Engine"
G_TARGET: str = "03. Targets / Stop"
G_VIS: str = "04. Visual Display"
G_COLOR: str = "05. Colours"


@script.strategy(title="McGinley T3 Flow Campaign [NICK789]", shorttitle="McG T3 Flow Campaign", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.05, initial_capital=100000, margin_long=0, margin_short=0, process_orders_on_close=True, pyramiding=0, max_lines_count=500, max_labels_count=500)
def main(
    startTime=input.time(timestamp('01 Jan 2026 00:00 +1100'), "Backtest Start", group=G_TIME),
    engineMode=input.string("McGinley Only", "Engine Mode", options=("McGinley Only", "T3 Only", "McGinley + T3 Blend"), group=G_ENGINE),
    sourcePrice: Series[float] = input.source(close, "Source", group=G_ENGINE),
    mcgLength=input.int(65, "McGinley Length", minval=1, group=G_ENGINE),
    t3Length=input.int(14, "T3 Length", minval=1, group=G_ENGINE),
    t3Volume=input.float(0.7, "T3 Smoothing Factor", minval=0.1, maxval=1.0, step=0.05, group=G_ENGINE),
    trailAtrLen=input.int(28, "ATR Trail Length", minval=1, group=G_ENGINE),
    trailAtrMult=input.float(1.2, "ATR Trail Multiplier", minval=0.05, step=0.05, group=G_ENGINE),
    useTargets=input.bool(True, "Enable Take Profit", group=G_TARGET, inline="target"),
    targetMult=input.float(1.0, "Target Distance Multiplier", minval=0.1, step=0.1, group=G_TARGET, inline="target"),
    targetMode=input.string("Flow Trail Based", "Target Mode", options=("Flow Trail Based", "ATR Baseline"), group=G_TARGET),
    tpExitMode=input.string("Scale Out TP1/TP2/TP3", "Take Profit Exit Mode", options=("TP1 Only", "TP2 Only", "TP3 Only", "Scale Out TP1/TP2/TP3"), group=G_TARGET),
    tp1Percent=input.int(30, "TP1 Size (%)", minval=1, maxval=100, group=G_TARGET),
    tp2Percent=input.int(30, "TP2 Size (%)", minval=1, maxval=100, group=G_TARGET),
    tp3Percent=input.int(40, "TP3 Size (%)", minval=1, maxval=100, group=G_TARGET),
    tp1RR=input.float(1.0, "TP1 Risk/Reward", minval=0.1, step=0.1, group=G_TARGET),
    tp2RR=input.float(2.0, "TP2 Risk/Reward", minval=0.1, step=0.1, group=G_TARGET),
    tp3RR=input.float(3.0, "TP3 Risk/Reward", minval=0.1, step=0.1, group=G_TARGET),
    stopMode=input.string("Visual Only", "Stop Mode", options=("Off", "Visual Only", "Visual + Strategy Exit"), group=G_TARGET),
    showTrail=input.bool(True, "Show ATR Signal Trail", group=G_VIS),
    showCloud=input.bool(True, "Show Signal Ribbon", group=G_VIS),
    showComponents=input.bool(False, "Show McGinley / T3 Components", group=G_VIS),
    showLevels=input.bool(True, "Show Entry / Target Lines", group=G_VIS),
    showSignals=input.bool(True, "Show Main Signal Labels", group=G_VIS),
    showFollowUps=input.bool(True, "Show Continuation Triangles", group=G_VIS),
    showPulse=input.bool(True, "Show Signal Background Pulse", group=G_VIS),
    colorCandles=input.bool(False, "Colour Candles By Trend", group=G_VIS),
    showDash=input.bool(True, "Show Dashboard", group=G_VIS),
    bullColor=input.color(color.new('#00E5A8'), "Bull Colour", group=G_COLOR),
    bearColor=input.color(color.new('#FF3D71'), "Bear Colour", group=G_COLOR),
    flatColor=input.color(color.new('#B8B8B8'), "Neutral Colour", group=G_COLOR),
    stopColor=input.color(color.orange, "Stop Colour", group=G_COLOR)
):
    @method
    def open(c: FlowCampaign, _side: int, _entry: float, _unit: float, _rr1: float, _rr2: float, _rr3: float, _hasSL: bool):
        c.side = _side
        c.startBar = bar_index
        c.finishBar = na
        c.entry = _entry
        c.t1 = _entry + _unit * _rr1 * _side
        c.t2 = _entry + _unit * _rr2 * _side
        c.t3 = _entry + _unit * _rr3 * _side
        c.sl = _entry - _unit * _rr2 * _side if _hasSL else na
        c.active = True
        return c.active

    @method
    def finish(c: FlowCampaign):
        c.finishBar = bar_index
        c.active = False
        return c.active

    def f_mcginley(_src: float, _len: int):
        mg: PersistentSeries[float] = na(float)
        previous = nz(mg[1], _src)
        ratio = _src / previous if previous != 0.0 else 1.0
        ratio = 1.0 if ratio <= 0.0 else ratio
        mg = _src if na(mg[1]) else mg[1] + (_src - mg[1]) / (_len * math.pow(ratio, 4))
        return mg

    def f_t3(_src: float, _len: int, _v: float):
        e1 = ta.ema(_src, _len)
        e2 = ta.ema(e1, _len)
        e3 = ta.ema(e2, _len)
        e4 = ta.ema(e3, _len)
        e5 = ta.ema(e4, _len)
        e6 = ta.ema(e5, _len)

        c1 = -_v * _v * _v
        c2 = 3.0 * _v * _v + 3.0 * _v * _v * _v
        c3 = -6.0 * _v * _v - 3.0 * _v - 3.0 * _v * _v * _v
        c4 = 1.0 + 3.0 * _v + _v * _v * _v + 3.0 * _v * _v

        return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    def f_json(_action: str, _portion: float, _target: float, _stop: float):
        closedTrades = strategy.closedtrades
        winRateNow = strategy.wintrades / closedTrades * 100.0 if closedTrades > 0 else 0.0
        pnlNow = strategy.netprofit_percent + strategy.openprofit_percent
        startText: str = "n/a"

        return '{"ticker":"' + syminfo.ticker + '","action":"' + _action + '","price":"' + string.tostring(close) + '","time":"' + string.format_time(timenow, 'yyyy-MM-dd HH:mm', syminfo.timezone) + '","tf":"' + timeframe.period + '","per":"' + string.tostring(_portion) + '","tp":"' + string.tostring(_target) + '","sl":"' + string.tostring(_stop) + '","TotalTrades":"' + string.tostring(closedTrades) + '","PNL":"' + string.tostring(pnlNow, '#.##') + '","WinRate":"' + string.tostring(winRateNow, '#.##') + '","MaxDraw":"' + string.tostring(strategy.max_drawdown_percent, '#.##') + '","StartDate":"' + startText + '"}'

    tradeCount = strategy.closedtrades
    winRate = strategy.wintrades / tradeCount * 100.0 if tradeCount > 0 else 0.0
    netPnl = strategy.netprofit_percent + strategy.openprofit_percent
    maxDD = strategy.max_drawdown_percent

    mcgCurve = f_mcginley(sourcePrice, mcgLength)
    t3Curve = f_t3(sourcePrice, t3Length, t3Volume)

    useMcgOnly = engineMode == 'McGinley Only'
    useT3Only = engineMode == 'T3 Only'
    useBlend = engineMode == 'McGinley + T3 Blend'

    engineBasis = mcgCurve if useMcgOnly else t3Curve if useT3Only else (mcgCurve + t3Curve) / 2.0

    engineText = 'McGinley' if useMcgOnly else 'T3' if useT3Only else 'McGinley + T3'

    trailDistance = ta.atr(trailAtrLen) * trailAtrMult

    flowTrail: Series = engineBasis
    flowTrail = nz(flowTrail[1], flowTrail)

    upperTrailLock = engineBasis + trailDistance
    lowerTrailLock = engineBasis - trailDistance

    if lowerTrailLock > flowTrail:
        flowTrail = lowerTrailLock

    if upperTrailLock < flowTrail:
        flowTrail = upperTrailLock

    longSignal = ta.crossover(flowTrail, flowTrail[2]) and barstate.isconfirmed
    shortSignal = ta.crossunder(flowTrail, flowTrail[2]) and barstate.isconfirmed

    visualTrend: Persistent[int] = 0

    if longSignal:
        visualTrend = 1

    if shortSignal:
        visualTrend = -1

    trendBull = visualTrend == 1
    trendBear = visualTrend == -1

    trailColor = bullColor if trendBull else bearColor if trendBear else flatColor

    lastSignalSide: Persistent[int] = 0

    primaryLong = longSignal and lastSignalSide != 1
    primaryShort = shortSignal and lastSignalSide != -1

    followLong = longSignal and lastSignalSide == 1
    followShort = shortSignal and lastSignalSide == -1

    if longSignal:
        lastSignalSide = 1

    if shortSignal:
        lastSignalSide = -1

    atrBase = ta.atr(200)
    flowDistance = math.abs(close - flowTrail)
    flowFloor = atrBase * 0.25

    targetUnit = math.max(flowDistance, flowFloor) if targetMode == 'Flow Trail Based' else atrBase

    campaignStep = targetUnit * targetMult

    hasStopLine = stopMode != 'Off'
    stopIsLive = stopMode == 'Visual + Strategy Exit'

    scaleOutMode = tpExitMode == 'Scale Out TP1/TP2/TP3'

    scaleTotal = math.max(cast_float(tp1Percent + tp2Percent + tp3Percent), 1.0)

    safeT1 = cast_float(tp1Percent) / scaleTotal * 100.0 if scaleOutMode else 100.0
    safeT2 = cast_float(tp2Percent) / scaleTotal * 100.0 if scaleOutMode else 100.0
    safeT3 = cast_float(tp3Percent) / scaleTotal * 100.0 if scaleOutMode else 100.0

    useTP1Exit = tpExitMode == 'TP1 Only' or scaleOutMode
    useTP2Exit = tpExitMode == 'TP2 Only' or scaleOutMode
    useTP3Exit = tpExitMode == 'TP3 Only' or scaleOutMode

    campaign: Persistent[FlowCampaign] = FlowCampaign(0, na, na, na, na, na, na, na, False)

    liveLongT1: Persistent[float] = na(float)
    liveLongT2: Persistent[float] = na(float)
    liveLongT3: Persistent[float] = na(float)
    liveShortT1: Persistent[float] = na(float)
    liveShortT2: Persistent[float] = na(float)
    liveShortT3: Persistent[float] = na(float)
    liveLongSL: Persistent[float] = na(float)
    liveShortSL: Persistent[float] = na(float)

    allowTrading = time >= startTime

    if allowTrading:
        if longSignal and strategy.position_size <= 0:
            strategy.close('Short', comment='Short Exit', alert_message=f_json('exit_sell', 100.0, na, na))
            strategy.entry('Long', strategy.long, comment='Long', alert_message=f_json('buy', 0.0, na, na))

            if useTargets:
                open(campaign, 1, close, campaignStep, tp1RR, tp2RR, tp3RR, hasStopLine)

                liveLongT1 = campaign.t1
                liveLongT2 = campaign.t2
                liveLongT3 = campaign.t3
                liveLongSL = campaign.sl

                liveShortT1 = na
                liveShortT2 = na
                liveShortT3 = na
                liveShortSL = na

        if shortSignal and strategy.position_size >= 0:
            strategy.close('Long', comment='Long Exit', alert_message=f_json('exit_buy', 100.0, na, na))
            strategy.entry('Short', strategy.short, comment='Short', alert_message=f_json('sell', 0.0, na, na))

            if useTargets:
                open(campaign, -1, close, campaignStep, tp1RR, tp2RR, tp3RR, hasStopLine)

                liveShortT1 = campaign.t1
                liveShortT2 = campaign.t2
                liveShortT3 = campaign.t3
                liveShortSL = campaign.sl

                liveLongT1 = na
                liveLongT2 = na
                liveLongT3 = na
                liveLongSL = na

        if strategy.position_size > 0:
            if stopIsLive and (not na(liveLongSL)) and (low <= liveLongSL):
                strategy.close('Long', comment='Long SL', alert_message=f_json('exit_buy', 100.0, na, liveLongSL))
                liveLongT1 = na
                liveLongT2 = na
                liveLongT3 = na
                liveLongSL = na
                finish(campaign)
            else:
                if useTargets and useTP1Exit and (not na(liveLongT1)) and (high > liveLongT1):
                    strategy.close('Long', comment='Long TP1', qty_percent=safeT1, alert_message=f_json('exit_buy', safeT1, liveLongT1, liveLongSL))

                    if scaleOutMode:
                        liveLongT1 = na
                    else:
                        liveLongT1 = na
                        liveLongT2 = na
                        liveLongT3 = na
                        liveLongSL = na
                        finish(campaign)

                if useTargets and useTP2Exit and (not na(liveLongT2)) and (high > liveLongT2):
                    strategy.close('Long', comment='Long TP2', qty_percent=safeT2, alert_message=f_json('exit_buy', safeT2, liveLongT2, liveLongSL))

                    if scaleOutMode:
                        liveLongT2 = na
                    else:
                        liveLongT1 = na
                        liveLongT2 = na
                        liveLongT3 = na
                        liveLongSL = na
                        finish(campaign)

                if useTargets and useTP3Exit and (not na(liveLongT3)) and (high > liveLongT3):
                    strategy.close('Long', comment='Long TP3', qty_percent=safeT3, alert_message=f_json('exit_buy', safeT3, liveLongT3, liveLongSL))
                    liveLongT1 = na
                    liveLongT2 = na
                    liveLongT3 = na
                    liveLongSL = na
                    finish(campaign)

        if strategy.position_size < 0:
            if stopIsLive and (not na(liveShortSL)) and (high >= liveShortSL):
                strategy.close('Short', comment='Short SL', alert_message=f_json('exit_sell', 100.0, na, liveShortSL))
                liveShortT1 = na
                liveShortT2 = na
                liveShortT3 = na
                liveShortSL = na
                finish(campaign)
            else:
                if useTargets and useTP1Exit and (not na(liveShortT1)) and (low < liveShortT1):
                    strategy.close('Short', comment='Short TP1', qty_percent=safeT1, alert_message=f_json('exit_sell', safeT1, liveShortT1, liveShortSL))

                    if scaleOutMode:
                        liveShortT1 = na
                    else:
                        liveShortT1 = na
                        liveShortT2 = na
                        liveShortT3 = na
                        liveShortSL = na
                        finish(campaign)

                if useTargets and useTP2Exit and (not na(liveShortT2)) and (low < liveShortT2):
                    strategy.close('Short', comment='Short TP2', qty_percent=safeT2, alert_message=f_json('exit_sell', safeT2, liveShortT2, liveShortSL))

                    if scaleOutMode:
                        liveShortT2 = na
                    else:
                        liveShortT1 = na
                        liveShortT2 = na
                        liveShortT3 = na
                        liveShortSL = na
                        finish(campaign)

                if useTargets and useTP3Exit and (not na(liveShortT3)) and (low < liveShortT3):
                    strategy.close('Short', comment='Short TP3', qty_percent=safeT3, alert_message=f_json('exit_sell', safeT3, liveShortT3, liveShortSL))
                    liveShortT1 = na
                    liveShortT2 = na
                    liveShortT3 = na
                    liveShortSL = na
                    finish(campaign)

    componentMcgVisible = showComponents and (not useT3Only)
    componentT3Visible = showComponents and (not useMcgOnly)

    cloudColor = color.new(bullColor, 86) if trendBull else color.new(bearColor, 86) if trendBear else color.new(flatColor, 90)

    signalRibbonColor = color.new(bullColor, 84) if trendBull else color.new(bearColor, 84) if trendBear else color.new(flatColor, 90)

    mcgPlot = plot(mcgCurve if componentMcgVisible else na, 'McGinley Component', color=color.new(bullColor, 25 if useBlend else 5), linewidth=2 if useBlend else 3)

    t3Plot = plot(t3Curve if componentT3Visible else na, 'T3 Component', color=color.new(bearColor, 25 if useBlend else 5), linewidth=2 if useBlend else 3)

    fill(mcgPlot, t3Plot, color=cloudColor if showCloud and useBlend else na, title='Engine Component Cloud')

    trailPlot = plot(flowTrail if showTrail else na, 'ATR Signal Trail', color=trailColor, linewidth=4, style=plot.style_stepline)

    basisPlot = plot(engineBasis if showCloud else na, 'Selected Engine Basis', color=color.new(chart.fg_color, 100), linewidth=1)

    fill(trailPlot, basisPlot, color=signalRibbonColor if showCloud else na, title='Signal Trail Ribbon')

    entryLine: Persistent[Line] = na(Line)
    t1Line: Persistent[Line] = na(Line)
    t2Line: Persistent[Line] = na(Line)
    t3Line: Persistent[Line] = na(Line)
    slLine: Persistent[Line] = na(Line)

    entryTag: Persistent[Label] = na(Label)
    t1Tag: Persistent[Label] = na(Label)
    t2Tag: Persistent[Label] = na(Label)
    t3Tag: Persistent[Label] = na(Label)
    slTag: Persistent[Label] = na(Label)

    campaignReady = showLevels and useTargets and (not na(campaign.startBar)) and (not na(campaign.entry))
    lineEndRaw = bar_index if campaign.active else campaign.finishBar
    lineEnd = math.max(campaign.startBar + 1, nz(lineEndRaw, bar_index)) if not na(campaign.startBar) else bar_index

    campaignColor = bullColor if campaign.side == 1 else bearColor if campaign.side == -1 else flatColor

    campaignPrefix = 'L-' if campaign.side == 1 else 'S-' if campaign.side == -1 else ''

    entryLineColor = color.new(chart.fg_color, 0)
    t1LineColor = color.new(campaignColor, 55)
    t2LineColor = color.new(campaignColor, 30)
    t3LineColor = color.new(campaignColor, 0)
    slLineColor = color.new(stopColor, 0)

    entryText = 'ENTRY\n' + string.tostring(campaign.entry, format.mintick)
    tp1Text = campaignPrefix + 'TP1\n' + string.tostring(campaign.t1, format.mintick)
    tp2Text = campaignPrefix + 'TP2\n' + string.tostring(campaign.t2, format.mintick)
    tp3Text = campaignPrefix + 'TP3\n' + string.tostring(campaign.t3, format.mintick)
    slText = campaignPrefix + 'SL\n' + string.tostring(campaign.sl, format.mintick) if not na(campaign.sl) else campaignPrefix + 'SL'

    if campaignReady:
        if na(entryLine):
            entryLine = line.new(campaign.startBar, campaign.entry, lineEnd, campaign.entry, xloc=xloc.bar_index, color=entryLineColor, width=2)
            t1Line = line.new(campaign.startBar, campaign.t1, lineEnd, campaign.t1, xloc=xloc.bar_index, color=t1LineColor, width=1)
            t2Line = line.new(campaign.startBar, campaign.t2, lineEnd, campaign.t2, xloc=xloc.bar_index, color=t2LineColor, width=1)
            t3Line = line.new(campaign.startBar, campaign.t3, lineEnd, campaign.t3, xloc=xloc.bar_index, color=t3LineColor, width=2)

            entryTag = label.new(lineEnd, campaign.entry, entryText, xloc=xloc.bar_index, style=label.style_none, textcolor=entryLineColor, color=color.new(color.black, 100), size=size.small)
            t1Tag = label.new(lineEnd, campaign.t1, tp1Text, xloc=xloc.bar_index, style=label.style_none, textcolor=t1LineColor, color=color.new(color.black, 100), size=size.small)
            t2Tag = label.new(lineEnd, campaign.t2, tp2Text, xloc=xloc.bar_index, style=label.style_none, textcolor=t2LineColor, color=color.new(color.black, 100), size=size.small)
            t3Tag = label.new(lineEnd, campaign.t3, tp3Text, xloc=xloc.bar_index, style=label.style_none, textcolor=t3LineColor, color=color.new(color.black, 100), size=size.small)
        else:
            line.set_xy1(entryLine, campaign.startBar, campaign.entry)
            line.set_xy2(entryLine, lineEnd, campaign.entry)
            line.set_color(entryLine, entryLineColor)
            line.set_width(entryLine, 2)

            line.set_xy1(t1Line, campaign.startBar, campaign.t1)
            line.set_xy2(t1Line, lineEnd, campaign.t1)
            line.set_color(t1Line, t1LineColor)
            line.set_width(t1Line, 1)

            line.set_xy1(t2Line, campaign.startBar, campaign.t2)
            line.set_xy2(t2Line, lineEnd, campaign.t2)
            line.set_color(t2Line, t2LineColor)
            line.set_width(t2Line, 1)

            line.set_xy1(t3Line, campaign.startBar, campaign.t3)
            line.set_xy2(t3Line, lineEnd, campaign.t3)
            line.set_color(t3Line, t3LineColor)
            line.set_width(t3Line, 2)

            label.set_xy(entryTag, lineEnd, campaign.entry)
            label.set_text(entryTag, entryText)
            label.set_textcolor(entryTag, entryLineColor)

            label.set_xy(t1Tag, lineEnd, campaign.t1)
            label.set_text(t1Tag, tp1Text)
            label.set_textcolor(t1Tag, t1LineColor)

            label.set_xy(t2Tag, lineEnd, campaign.t2)
            label.set_text(t2Tag, tp2Text)
            label.set_textcolor(t2Tag, t2LineColor)

            label.set_xy(t3Tag, lineEnd, campaign.t3)
            label.set_text(t3Tag, tp3Text)
            label.set_textcolor(t3Tag, t3LineColor)

        if hasStopLine and (not na(campaign.sl)):
            if na(slLine):
                slLine = line.new(campaign.startBar, campaign.sl, lineEnd, campaign.sl, xloc=xloc.bar_index, color=slLineColor, width=2, style=line.style_dashed)
                slTag = label.new(lineEnd, campaign.sl, slText, xloc=xloc.bar_index, style=label.style_none, textcolor=slLineColor, color=color.new(color.black, 100), size=size.small)
            else:
                line.set_xy1(slLine, campaign.startBar, campaign.sl)
                line.set_xy2(slLine, lineEnd, campaign.sl)
                line.set_color(slLine, slLineColor)
                line.set_style(slLine, line.style_dashed)
                line.set_width(slLine, 2)

                label.set_xy(slTag, lineEnd, campaign.sl)
                label.set_text(slTag, slText)
                label.set_textcolor(slTag, slLineColor)
        else:
            if not na(slLine):
                line.delete(slLine)
                slLine = na
            if not na(slTag):
                label.delete(slTag)
                slTag = na

    if not campaignReady:
        if not na(entryLine):
            line.delete(entryLine)
            entryLine = na
        if not na(t1Line):
            line.delete(t1Line)
            t1Line = na
        if not na(t2Line):
            line.delete(t2Line)
            t2Line = na
        if not na(t3Line):
            line.delete(t3Line)
            t3Line = na
        if not na(slLine):
            line.delete(slLine)
            slLine = na

        if not na(entryTag):
            label.delete(entryTag)
            entryTag = na
        if not na(t1Tag):
            label.delete(t1Tag)
            t1Tag = na
        if not na(t2Tag):
            label.delete(t2Tag)
            t2Tag = na
        if not na(t3Tag):
            label.delete(t3Tag)
            t3Tag = na
        if not na(slTag):
            label.delete(slTag)
            slTag = na

    plotshape(showSignals and primaryLong, title='Primary Long', style=shape.labelup, location=location.belowbar, color=bullColor, text='MG\nBUY', textcolor=color.black, size=size.small)

    plotshape(showSignals and primaryShort, title='Primary Short', style=shape.labeldown, location=location.abovebar, color=bearColor, text='MG\nSELL', textcolor=color.white, size=size.small)

    plotshape(showSignals and showFollowUps and followLong, title='Long Follow-up', style=shape.triangleup, location=location.belowbar, color=color.new(bullColor, 65), size=size.tiny)

    plotshape(showSignals and showFollowUps and followShort, title='Short Follow-up', style=shape.triangledown, location=location.abovebar, color=color.new(bearColor, 65), size=size.tiny)

    bgcolor(color.new(bullColor, 88) if showPulse and primaryLong else color.new(bearColor, 88) if showPulse and primaryShort else na, title='Signal Pulse')

    barcolor(trailColor if colorCandles else na)

    dash: Persistent[Table] = table.new(position.top_right, 2, 6, border_width=1)

    def f_dashCell(_col: int, _row: int, _txt: str, _txtCol: Color, _bgCol: Color):
        return table.cell(dash, _col, _row, _txt, text_color=_txtCol, bgcolor=_bgCol, text_size=size.small)

    stateText = 'BULL FLOW' if trendBull else 'BEAR FLOW' if trendBear else 'NEUTRAL'

    posText = 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT'

    dashBg = color.new(color.black, 15)

    if showDash:
        f_dashCell(0, 0, 'McG T3 Flow', color.white, dashBg)
        f_dashCell(1, 0, engineMode, color.white, dashBg)

        f_dashCell(0, 1, 'Target Mode', color.white, dashBg)
        f_dashCell(1, 1, targetMode, color.white, dashBg)

        f_dashCell(0, 2, 'State', color.white, dashBg)
        f_dashCell(1, 2, stateText, trailColor, dashBg)

        f_dashCell(0, 3, 'Position', color.white, dashBg)
        f_dashCell(1, 3, posText, color.white, dashBg)

        f_dashCell(0, 4, 'Win Rate', color.white, dashBg)
        f_dashCell(1, 4, string.tostring(winRate, '#.##') + '%', color.white, dashBg)

        f_dashCell(0, 5, 'PNL / DD', color.white, dashBg)
        f_dashCell(1, 5, string.tostring(netPnl, '#.##') + '% / ' + string.tostring(maxDD, '#.##') + '%', color.white, dashBg)
    else:
        table.clear(dash, 0, 0, 1, 5)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
