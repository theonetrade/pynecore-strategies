"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, bgcolor, box, close, color,
    display, fill, format, high, hlc3, hline, input, label, line, low, math, na, open, plot,
    position, script, size, string, syminfo, ta, table, text, xloc, yloc
)
from pynecore.types import Box, Line, Persistent, Series, Table

groupRsi: str = "⚙️ RSI Engine"
groupLevels: str = "📊 RSI Levels"
groupTrade: str = "🎯 Trade Projection"
groupVisual: str = "🎨 Visual Settings"
groupAlerts: str = "🔔 Alerts"


@script.indicator("RSI Entry Engine [trade_w_samet]", shorttitle="RSI Entry Engine [trade_w_samet]", overlay=False, max_labels_count=500, max_boxes_count=500, max_lines_count=500)
def main(
    rsiSource: Series[float] = input.source(close, "📌 RSI Source", group=groupRsi, tooltip="Selects the price source used to calculate the RSI engine. Close is the default and most common choice.", display=display.none),
    rsiLength=input.int(14, "📏 RSI Length", minval=1, group=groupRsi, tooltip="Controls the base RSI calculation length. Lower values react faster, while higher values create smoother RSI behavior.", display=display.none),
    smoothMode=input.string("EMA", "〰️ RSI Smoothing", options=("None", "EMA", "SMA", "RMA"), group=groupRsi, tooltip="Applies optional smoothing to the raw RSI value. EMA is responsive, SMA is simpler, and RMA is smoother.", display=display.none),
    smoothLen=input.int(5, "🔧 Smoothing Length", minval=1, group=groupRsi, tooltip="Controls how much smoothing is applied to the RSI line. Higher values reduce noise but may delay signals.", display=display.none),
    signalLen=input.int(9, "📐 Signal Length", minval=1, group=groupRsi, tooltip="Length used for the RSI signal line. This helps compare RSI momentum against its own smoothed signal.", display=display.none),
    signalMode=input.string("EMA", "📡 Signal Smoothing", options=("EMA", "SMA", "RMA"), group=groupRsi, tooltip="Smoothing method used for the RSI signal line. EMA is the default balanced option.", display=display.none),
    overbought=input.int(70, "🔴 Overbought", minval=50, maxval=100, group=groupLevels, tooltip="Defines the standard overbought zone. RSI values above this level indicate stronger bullish pressure or potential exhaustion.", display=display.none),
    oversold=input.int(30, "🟢 Oversold", minval=0, maxval=50, group=groupLevels, tooltip="Defines the standard oversold zone. RSI values below this level indicate stronger bearish pressure or potential exhaustion.", display=display.none),
    extremeHigh=input.int(80, "🚨 Extreme High", minval=60, maxval=100, group=groupLevels, tooltip="Defines the upper extreme zone. Short-side rejection signals are generated when RSI crosses back down from this area.", display=display.none),
    extremeLow=input.int(20, "✅ Extreme Low", minval=0, maxval=40, group=groupLevels, tooltip="Defines the lower extreme zone. Long-side reclaim signals are generated when RSI crosses back up from this area.", display=display.none),
    showTradeBoxes=input.bool(True, "📦 Show TP / SL Boxes On Main Chart", group=groupTrade, tooltip="Shows projected entry, take-profit, and stop-loss boxes on the main price chart when a confirmed RSI signal appears.", display=display.none),
    entryMode=input.string("Close", "🎯 Entry Price", options=("Close", "Open", "HLC3"), group=groupTrade, tooltip="Selects which price is used as the projected entry level after a confirmed RSI signal.", display=display.none),
    slMode=input.string("ATR", "🛡️ Stop Loss Mode", options=("Signal Candle", "ATR", "Percent"), group=groupTrade, tooltip="Controls how the projected stop-loss is calculated. ATR adapts to volatility, Signal Candle uses the signal candle, and Percent uses fixed percentage distance.", display=display.none),
    rrTarget=input.float(5.0, "💎 Risk / Reward", minval=0.1, step=0.1, group=groupTrade, tooltip="Sets the projected take-profit distance based on risk. Example: 5.0 means TP is placed at 5R.", display=display.none),
    atrLen=input.int(14, "📏 ATR Length", minval=1, group=groupTrade, tooltip="ATR length used when Stop Loss Mode is set to ATR. Higher values create smoother volatility measurement.", display=display.none),
    atrMult=input.float(1.0, "⚡ ATR Multiplier", minval=0.1, step=0.1, group=groupTrade, tooltip="Multiplier applied to ATR when calculating the projected stop-loss distance.", display=display.none),
    percentSL=input.float(0.5, "📉 Percent Stop Loss", minval=0.01, step=0.01, group=groupTrade, tooltip="Fixed percentage stop-loss distance used only when Stop Loss Mode is set to Percent.", display=display.none),
    sameBarPriority=input.string("SL", "⚖️ Same-Bar TP / SL Priority", options=("SL", "TP"), group=groupTrade, tooltip="Chooses which result is counted first if TP and SL are both touched on the same candle. SL is more conservative.", display=display.none),
    maxStoredTrades=input.int(20, "🗂️ Max Stored Trade Projections", minval=1, maxval=100, group=groupTrade, tooltip="Limits how many historical trade projection objects remain visible on the chart.", display=display.none),
    showBgExtreme=input.bool(True, "🌈 Highlight Extreme Background", group=groupVisual, tooltip="Highlights the RSI pane background when RSI enters extreme high or extreme low zones.", display=display.none),
    showPanel=input.bool(True, "📋 Show Status Panel", group=groupVisual, tooltip="Shows or hides the compact RSI status panel.", display=display.none),
    panelPosition=input.string("Top Right", "📍 Panel Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=groupVisual, tooltip="Controls where the RSI status panel is displayed on the chart.", display=display.none),
    panelTextSize=input.string("Small", "🔤 Panel Text Size", options=("Tiny", "Small", "Normal"), group=groupVisual, tooltip="Controls the text size of the RSI status panel.", display=display.none),
    labelTextSize=input.string("Normal", "🏷️ Label Text Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=groupVisual, tooltip="Controls the size of all chart labels including UP, DOWN, BUY, SELL, TP HIT, and SL HIT labels.", display=display.none),
    enableCrossAlerts=input.bool(True, "🔁 Enable RSI / Signal Cross Alerts", group=groupAlerts, tooltip="Enables alerts when RSI crosses above or below its signal line.", display=display.none),
    enableZoneAlerts=input.bool(True, "📊 Enable Overbought / Oversold Reclaim Alerts", group=groupAlerts, tooltip="Enables alerts when RSI reclaims oversold or rejects from overbought areas.", display=display.none),
    enableCenterAlerts=input.bool(True, "⚖️ Enable Centerline Alerts", group=groupAlerts, tooltip="Enables alerts when RSI crosses the 50 centerline.", display=display.none),
    enableSignalAlerts=input.bool(True, "🚀 Enable Entry Signal Alerts", group=groupAlerts, tooltip="Enables alerts for confirmed long and short RSI entry signals.", display=display.none),
    enableTradeAlerts=input.bool(True, "🎯 Enable TP / SL Hit Alerts", group=groupAlerts, tooltip="Enables alerts when projected TP or SL levels are reached.", display=display.none)
):
    clrBg = color.rgb(13, 17, 23)
    clrHeader = color.rgb(31, 41, 55)
    clrBorder = color.rgb(48, 54, 61)
    clrText = color.rgb(255, 255, 255)
    clrMuted = color.rgb(139, 148, 158)
    clrBlue = color.rgb(88, 166, 255)
    clrGreen = color.rgb(34, 197, 94)
    clrRed = color.rgb(239, 68, 68)
    clrCardA = color.rgb(22, 27, 34)
    clrCardB = color.rgb(18, 22, 28)
    clrLineDark = color.rgb(20, 20, 20)

    def getTablePosition(_pos):
        __block_result__ = na
        __switch__ = _pos
        if __switch__ == "Top Left":
            __block_result__ = position.top_left
        elif __switch__ == "Bottom Right":
            __block_result__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result__ = position.bottom_left
        else:
            __block_result__ = position.top_right
        return __block_result__

    def getTableTextSize(_size):
        __block_result_1__ = na
        __switch__ = _size
        if __switch__ == "Tiny":
            __block_result_1__ = size.tiny
        elif __switch__ == "Normal":
            __block_result_1__ = size.normal
        else:
            __block_result_1__ = size.small
        return __block_result_1__

    def getLabelTextSize(_size):
        __block_result_2__ = na
        __switch__ = _size
        if __switch__ == "Tiny":
            __block_result_2__ = size.tiny
        elif __switch__ == "Small":
            __block_result_2__ = size.small
        elif __switch__ == "Large":
            __block_result_2__ = size.large
        elif __switch__ == "Huge":
            __block_result_2__ = size.huge
        else:
            __block_result_2__ = size.normal
        return __block_result_2__

    def ma(_src, _len, _mode):
        return ta.ema(_src, _len) if _mode == 'EMA' else ta.sma(_src, _len) if _mode == 'SMA' else ta.rma(_src, _len) if _mode == 'RMA' else _src

    def getEntryPrice(_mode):
        return open if _mode == 'Open' else hlc3 if _mode == 'HLC3' else close

    def formatPrice(_price):
        return string.tostring(_price, format.mintick)

    def formatRsi(_value):
        return string.tostring(_value, '#.##')

    chartLabelSize = getLabelTextSize(labelTextSize)
    labelTextFormat = text.format_bold + text.format_italic

    txtUp: str = "𝙐𝙋"
    txtDown: str = "𝘿𝙊𝙒𝙉"
    txtBuy: str = "𝘽𝙐𝙔"
    txtSell: str = "𝙎𝙀𝙇𝙇"
    txtTpHit: str = "𝙏𝙋 𝙃𝙄𝙏"
    txtSlHit: str = "𝙎𝙇 𝙃𝙄𝙏"

    rsiRaw = ta.rsi(rsiSource, rsiLength)
    rsiSmooth: Series = rsiRaw if smoothMode == 'None' else ma(rsiRaw, smoothLen, smoothMode)
    signal = ma(rsiSmooth, signalLen, signalMode)
    spread = rsiSmooth - signal
    delta = rsiSmooth - rsiSmooth[1]
    atrValue = ta.atr(atrLen)

    isExtremeHigh = rsiSmooth >= extremeHigh
    isOverbought = rsiSmooth >= overbought
    isBullish = rsiSmooth > 50 and rsiSmooth < overbought
    isNeutral = rsiSmooth >= 45 and rsiSmooth <= 55
    isBearish = rsiSmooth < 50 and rsiSmooth > oversold
    isOversold = rsiSmooth <= oversold
    isExtremeLow = rsiSmooth <= extremeLow

    rsiColor = clrRed if isExtremeHigh else clrGreen if isExtremeLow else clrBlue

    h100 = hline(100, '100', color=color.new(clrMuted, 100))
    h0 = hline(0, '0', color=color.new(clrMuted, 100))
    h50 = hline(50, 'Center', color=color.new(clrMuted, 60), linestyle=hline.style_dotted)
    hOB = hline(overbought, 'Overbought', color=color.new(clrRed, 30), linestyle=hline.style_dashed)
    hOS = hline(oversold, 'Oversold', color=color.new(clrGreen, 30), linestyle=hline.style_dashed)
    hEH = hline(extremeHigh, 'Extreme High', color=color.new(clrRed, 55), linestyle=hline.style_dotted)
    hEL = hline(extremeLow, 'Extreme Low', color=color.new(clrGreen, 55), linestyle=hline.style_dotted)

    fill(hOB, h100, color=color.new(clrRed, 70), title='Overbought Zone')
    fill(hOS, h0, color=color.new(clrGreen, 70), title='Oversold Zone')

    bgcolor(color.new(clrRed, 80) if showBgExtreme and isExtremeHigh else na)
    bgcolor(color.new(clrGreen, 80) if showBgExtreme and isExtremeLow else na)

    plot(rsiSmooth, 'RSI', color=rsiColor, linewidth=3)
    plot(signal, 'Signal', color=color.new(clrText, 35), linewidth=2)

    upSignal = ta.crossover(rsiSmooth, extremeLow) and barstate.isconfirmed
    downSignal = ta.crossunder(rsiSmooth, extremeHigh) and barstate.isconfirmed

    if upSignal:
        label.new(x=bar_index, y=rsiSmooth, text=txtUp, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(clrGreen, 0), textcolor=clrText, size=chartLabelSize, text_formatting=labelTextFormat, tooltip='RSI Extreme Low Reclaim\n\nRSI crossed back above the Extreme Low level after reaching a deep oversold area.\n\nRSI: ' + formatRsi(rsiSmooth) + '\nExtreme Low: ' + string.tostring(extremeLow) + '\nSignal Line: ' + formatRsi(signal) + '\n\nThis is a confirmed bar-close analytical long signal.')

    if downSignal:
        label.new(x=bar_index, y=rsiSmooth, text=txtDown, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(clrRed, 0), textcolor=clrText, size=chartLabelSize, text_formatting=labelTextFormat, tooltip='RSI Extreme High Rejection\n\nRSI crossed back below the Extreme High level after reaching a deep overbought area.\n\nRSI: ' + formatRsi(rsiSmooth) + '\nExtreme High: ' + string.tostring(extremeHigh) + '\nSignal Line: ' + formatRsi(signal) + '\n\nThis is a confirmed bar-close analytical short signal.')

    tpBoxes: Persistent[list[Box]] = array.new_box()
    slBoxes: Persistent[list[Box]] = array.new_box()
    entryLines: Persistent[list[Line]] = array.new_line()
    entries: Persistent[list[float]] = array.new_float()
    tps: Persistent[list[float]] = array.new_float()
    sls: Persistent[list[float]] = array.new_float()
    dirs: Persistent[list[int]] = array.new_int()
    startBars: Persistent[list[int]] = array.new_int()
    actives: Persistent[list[bool]] = array.new_bool()

    entryBase = getEntryPrice(entryMode)

    if showTradeBoxes and upSignal:
        longEntry = entryBase
        longSlRaw = low if slMode == 'Signal Candle' else longEntry - atrValue * atrMult if slMode == 'ATR' else longEntry * (1.0 - percentSL / 100.0)
        longSl = math.min(longSlRaw, longEntry - syminfo.mintick)
        longRisk = longEntry - longSl

        if longRisk > 0:
            longTp = longEntry + longRisk * rrTarget

            tpBox = box.new(left=bar_index, top=longTp, right=bar_index + 1, bottom=longEntry, xloc=xloc.bar_index, border_color=color.new(clrGreen, 0), border_width=1, bgcolor=color.new(clrGreen, 65), force_overlay=True)

            slBox = box.new(left=bar_index, top=longEntry, right=bar_index + 1, bottom=longSl, xloc=xloc.bar_index, border_color=color.new(clrRed, 0), border_width=1, bgcolor=color.new(clrRed, 55), force_overlay=True)

            eLine = line.new(x1=bar_index, y1=longEntry, x2=bar_index + 1, y2=longEntry, xloc=xloc.bar_index, color=clrLineDark, width=2, force_overlay=True)

            label.new(x=bar_index, y=longEntry, text=txtBuy, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(clrGreen, 0), textcolor=clrText, size=chartLabelSize, force_overlay=True, text_formatting=labelTextFormat, tooltip='Projected Long Trade\n\nEntry: ' + formatPrice(longEntry) + '\nStop Loss: ' + formatPrice(longSl) + '\nTake Profit: ' + formatPrice(longTp) + '\nRisk / Reward: ' + string.tostring(rrTarget, '#.##') + 'R\nSL Mode: ' + slMode + '\n\nThis projection is created from a confirmed RSI Extreme Low reclaim signal.')

            array.push(tpBoxes, tpBox)
            array.push(slBoxes, slBox)
            array.push(entryLines, eLine)
            array.push(entries, longEntry)
            array.push(tps, longTp)
            array.push(sls, longSl)
            array.push(dirs, 1)
            array.push(startBars, bar_index)
            array.push(actives, True)

    if showTradeBoxes and downSignal:
        shortEntry = entryBase
        shortSlRaw = high if slMode == 'Signal Candle' else shortEntry + atrValue * atrMult if slMode == 'ATR' else shortEntry * (1.0 + percentSL / 100.0)
        shortSl = math.max(shortSlRaw, shortEntry + syminfo.mintick)
        shortRisk = shortSl - shortEntry

        if shortRisk > 0:
            shortTp = shortEntry - shortRisk * rrTarget

            tpBox = box.new(left=bar_index, top=shortEntry, right=bar_index + 1, bottom=shortTp, xloc=xloc.bar_index, border_color=color.new(clrGreen, 0), border_width=1, bgcolor=color.new(clrGreen, 65), force_overlay=True)

            slBox = box.new(left=bar_index, top=shortSl, right=bar_index + 1, bottom=shortEntry, xloc=xloc.bar_index, border_color=color.new(clrRed, 0), border_width=1, bgcolor=color.new(clrRed, 55), force_overlay=True)

            eLine = line.new(x1=bar_index, y1=shortEntry, x2=bar_index + 1, y2=shortEntry, xloc=xloc.bar_index, color=clrLineDark, width=2, force_overlay=True)

            label.new(x=bar_index, y=shortEntry, text=txtSell, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(clrRed, 0), textcolor=clrText, size=chartLabelSize, force_overlay=True, text_formatting=labelTextFormat, tooltip='Projected Short Trade\n\nEntry: ' + formatPrice(shortEntry) + '\nStop Loss: ' + formatPrice(shortSl) + '\nTake Profit: ' + formatPrice(shortTp) + '\nRisk / Reward: ' + string.tostring(rrTarget, '#.##') + 'R\nSL Mode: ' + slMode + '\n\nThis projection is created from a confirmed RSI Extreme High rejection signal.')

            array.push(tpBoxes, tpBox)
            array.push(slBoxes, slBox)
            array.push(entryLines, eLine)
            array.push(entries, shortEntry)
            array.push(tps, shortTp)
            array.push(sls, shortSl)
            array.push(dirs, -1)
            array.push(startBars, bar_index)
            array.push(actives, True)

    while array.size(tpBoxes) > maxStoredTrades:
        oldTpBox = array.shift(tpBoxes)
        oldSlBox = array.shift(slBoxes)
        oldELine = array.shift(entryLines)
        array.shift(entries)
        array.shift(tps)
        array.shift(sls)
        array.shift(dirs)
        array.shift(startBars)
        array.shift(actives)
        box.delete(oldTpBox)
        box.delete(oldSlBox)
        line.delete(oldELine)

    tradeCount = array.size(tpBoxes)

    longTpHitBar: bool = False
    longSlHitBar: bool = False
    shortTpHitBar: bool = False
    shortSlHitBar: bool = False

    if tradeCount > 0:
        for i in pine_range(0, tradeCount - 1):
            isActive = array.get(actives, i)

            if isActive:
                tpBox = array.get(tpBoxes, i)
                slBox = array.get(slBoxes, i)
                eLine = array.get(entryLines, i)
                tpPx = array.get(tps, i)
                slPx = array.get(sls, i)
                dir = array.get(dirs, i)
                startBar = array.get(startBars, i)

                box.set_right(tpBox, bar_index)
                box.set_right(slBox, bar_index)
                line.set_x2(eLine, bar_index)

                tpHit: bool = False
                slHit: bool = False
                canCheck = bar_index > startBar

                if canCheck:
                    if dir == 1:
                        tpHit = high >= tpPx
                        slHit = low <= slPx
                    else:
                        tpHit = low <= tpPx
                        slHit = high >= slPx

                if tpHit and slHit:
                    if sameBarPriority == 'SL':
                        tpHit = False
                    else:
                        slHit = False

                if tpHit or slHit:
                    array.set(actives, i, False)

                    if tpHit:
                        if dir == 1:
                            longTpHitBar = True
                        else:
                            shortTpHitBar = True

                        label.new(x=bar_index, y=tpPx, text=txtTpHit, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(clrGreen, 0), textcolor=clrText, size=chartLabelSize, force_overlay=True, text_formatting=labelTextFormat, tooltip='Take Profit Reached\n\nProjected TP level was reached on this candle.\n\nTP Price: ' + formatPrice(tpPx) + '\nDirection: ' + ('Long' if dir == 1 else 'Short') + '\n\nThis is based on the projected trade model, not an automated execution result.')
                    else:
                        if dir == 1:
                            longSlHitBar = True
                        else:
                            shortSlHitBar = True

                        label.new(x=bar_index, y=slPx, text=txtSlHit, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(clrRed, 0), textcolor=clrText, size=chartLabelSize, force_overlay=True, text_formatting=labelTextFormat, tooltip='Stop Loss Reached\n\nProjected SL level was reached on this candle.\n\nSL Price: ' + formatPrice(slPx) + '\nDirection: ' + ('Long' if dir == 1 else 'Short') + '\n\nThis is based on the projected trade model, not an automated execution result.')

    statusText = 'Extreme High' if isExtremeHigh else 'Overbought' if isOverbought else 'Bullish' if isBullish else 'Neutral' if isNeutral else 'Bearish' if isBearish else 'Oversold' if isOversold else 'Extreme Low'

    momentumText = 'Strong Up' if delta >= 1.5 else 'Up' if delta > 0 else 'Strong Down' if delta <= -1.5 else 'Down' if delta < 0 else 'Flat'

    crossState = 'RSI > Signal' if spread > 0 else 'RSI < Signal' if spread < 0 else 'At Signal'

    panelPos = getTablePosition(panelPosition)
    panelSize = getTableTextSize(panelTextSize)

    panel: Persistent[Table] = table.new(panelPos, 2, 6, border_width=1, frame_color=clrBorder, border_color=clrBorder)

    if barstate.islast:
        if showPanel:
            table.cell(panel, 0, 0, '𝙍𝙎𝙄 𝙋𝘼𝙉𝙀𝙇', text_color=clrText, text_size=panelSize, bgcolor=clrHeader, text_formatting=labelTextFormat)
            table.cell(panel, 1, 0, '𝙑𝘼𝙇𝙐𝙀', text_color=clrText, text_size=panelSize, bgcolor=clrHeader, text_formatting=labelTextFormat)

            table.cell(panel, 0, 1, '𝙍𝙎𝙄', text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)
            table.cell(panel, 1, 1, string.tostring(rsiSmooth, '#.##'), text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)

            table.cell(panel, 0, 2, '𝙎𝙞𝙜𝙣𝙖𝙡', text_color=clrText, text_size=panelSize, bgcolor=clrCardB, text_formatting=labelTextFormat)
            table.cell(panel, 1, 2, string.tostring(signal, '#.##'), text_color=clrText, text_size=panelSize, bgcolor=clrCardB, text_formatting=labelTextFormat)

            table.cell(panel, 0, 3, '𝙎𝙩𝙖𝙩𝙪𝙨', text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)
            table.cell(panel, 1, 3, statusText, text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)

            table.cell(panel, 0, 4, '𝙈𝙤𝙢𝙚𝙣𝙩𝙪𝙢', text_color=clrText, text_size=panelSize, bgcolor=clrCardB, text_formatting=labelTextFormat)
            table.cell(panel, 1, 4, momentumText, text_color=clrText, text_size=panelSize, bgcolor=clrCardB, text_formatting=labelTextFormat)

            table.cell(panel, 0, 5, '𝙎𝙩𝙧𝙪𝙘𝙩𝙪𝙧𝙚', text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)
            table.cell(panel, 1, 5, crossState, text_color=clrText, text_size=panelSize, bgcolor=clrCardA, text_formatting=labelTextFormat)
        else:
            for row in pine_range(0, 5):
                table.cell(panel, 0, row, '', bgcolor=color.new(clrBg, 100))
                table.cell(panel, 1, row, '', bgcolor=color.new(clrBg, 100))

    bullCross = ta.crossover(rsiSmooth, signal)
    bearCross = ta.crossunder(rsiSmooth, signal)
    bullReclaim = ta.crossover(rsiSmooth, oversold)
    bearReject = ta.crossunder(rsiSmooth, overbought)
    centerBull = ta.crossover(rsiSmooth, 50)
    centerBear = ta.crossunder(rsiSmooth, 50)

    alertcondition(enableCrossAlerts and bullCross, title='RSI Bullish Cross', message='RSI crossed above Signal')
    alertcondition(enableCrossAlerts and bearCross, title='RSI Bearish Cross', message='RSI crossed below Signal')
    alertcondition(enableZoneAlerts and bullReclaim, title='RSI Oversold Reclaim', message='RSI reclaimed above Oversold')
    alertcondition(enableZoneAlerts and bearReject, title='RSI Overbought Reject', message='RSI crossed below Overbought')
    alertcondition(enableCenterAlerts and centerBull, title='RSI Centerline Bullish', message='RSI crossed above 50')
    alertcondition(enableCenterAlerts and centerBear, title='RSI Centerline Bearish', message='RSI crossed below 50')

    alertcondition(enableSignalAlerts and upSignal, title='Long Entry Signal', message='Long entry signal confirmed')
    alertcondition(enableSignalAlerts and downSignal, title='Short Entry Signal', message='Short entry signal confirmed')

    alertcondition(enableTradeAlerts and longTpHitBar, title='Long TP Hit', message='Long projected take-profit reached')
    alertcondition(enableTradeAlerts and longSlHitBar, title='Long SL Hit', message='Long projected stop-loss reached')
    alertcondition(enableTradeAlerts and shortTpHitBar, title='Short TP Hit', message='Short projected take-profit reached')
    alertcondition(enableTradeAlerts and shortSlHitBar, title='Short SL Hit', message='Short projected stop-loss reached')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
