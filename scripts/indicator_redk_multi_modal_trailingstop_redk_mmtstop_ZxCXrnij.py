"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barmerge, barstate, close, color, display,
    fill, high, hl2, input, label, location, low, math, na, nz, plot, plotshape, position, request,
    script, shape, size, string, syminfo, ta, table, timeframe
)
from pynecore.types import Persistent, PersistentSeries, Series, Table

grpMethod: str = "Trailing Stop Calculation Method"
grpATR: str = "ATR / Supertrend"
grpStyles: str = "Visuals and Other Settings"
disnon = display.none


@script.indicator("RedK Multi-Modal TrailingStop v1.0", shorttitle="RedK MMTStop v1.0", overlay=True)
def main(
    TStop_mode=input.string("ATR / Supertrend", "Trailing method", options=("ATR / Supertrend", "Chandelier", "Donchian", "StdDev Channel", "Fixed %"), group=grpMethod, tooltip='ATR/Supertrend: trails an ATR-based (volatility) distance from price.\n     \nChandelier: hangs an ATR distance off the recent swing high/low.\n     \nDonchian: trails to the recent swing low/high (Turtle-style).\n     \nStdDev Channel: trails a statistical (Bollinger-band style) distance.\n     \nFixed %: trails a set percentage of price.'),
    anchorSrc: Series[float] = input.source(hl2, "Anchor price source", group=grpMethod, display=disnon, tooltip='Reference price the ATR / StdDev / Fixed % distance is measured from.\n     \nChandelier and Donchian use swing highs/lows instead and ignore this.'),
    atrLen=input.int(10, "ATR length", minval=1, inline=grpATR, group=grpATR, display=disnon),
    atrMult=input.float(3.0, "Multiplier", step=0.1, minval=0.1, inline=grpATR, group=grpATR, display=disnon),
    useMTF=input.bool(False, "Use HTF ATR", inline='ATR HTF', group=grpATR, display=disnon),
    atrTF=input.timeframe("240", "⠀⠀⠀⠀⠀⠀⠀HTF timeframe", inline='ATR HTF', group=grpATR, display=disnon, tooltip="Pick a timeframe higher than the chart's."),
    chLen=input.int(22, "Chandelier Lookback", minval=1, group="Chandelier", display=disnon, tooltip="Bars used to find the swing high/low the stop hangs from."),
    chAtrLen=input.int(14, "Chandelier ATR length", minval=1, inline='chandatr', group="Chandelier", display=disnon),
    chMult=input.float(3.0, "Multiplier", step=0.1, minval=0.1, inline='chandatr', group="Chandelier", display=disnon),
    dcLen=input.int(20, "Donchian Lookback", minval=1, group="Donchian", display=disnon, tooltip="Bars used for the swing low (long) / swing high (short) the stop trails to."),
    sdLen=input.int(20, "StdDev Length", minval=2, inline='stddiv', group="StdDev Channel", display=disnon),
    sdMult=input.float(2.0, "⠀⠀⠀⠀⠀Multiplier", step=0.1, minval=0.2, inline='stddiv', group="StdDev Channel", display=disnon),
    pctOff=input.float(5.0, "Fixed Trail %", step=0.5, minval=0.1, group="Fixed %", display=disnon),
    showBands=input.bool(True, "Show colored safe zone⠀⠀⠀⠀⠀", inline="bands", group=grpStyles, display=disnon),
    showBBs=input.bool(True, "Show band borders", inline="bands", group=grpStyles, display=disnon, tooltip='Show shaded safe zone & its band border.' + '\nDefaults are 🔴 RED nearest the stop (Critical), 🟡 AMBER mid-zone (Watch), 🟢 GREEN farthest (Safe).'),
    critAtrLen=input.int(14, "Safe Zone's ATR Length", minval=1, group=grpStyles, inline="sz1", display=disnon),
    safeZone=input.float(2.0, " ATR Multiplier", step=0.1, minval=0.5, group=grpStyles, inline="sz1", display=disnon, tooltip='ATR Length & Multiplier used only to calculate the Trailing Stop Safe Zone bands.\n     \nAt or above these bands = Safe.\nBetween this and half its value = Watch.\nBelow half = Critical.\n     \nExample: multiplier = 2.00 means: Safe ≥ 2.00x ATR, Watch 1.00–2.00x ATR, Critical < 1.00x ATR.'),
    safeCol=input.color(color.new(color.new('#33AA00'), 50), "Safe band", group=grpStyles, inline="sz2"),
    watchCol=input.color(color.new(color.new('#FDD835'), 70), "Watch band", group=grpStyles, inline="sz2"),
    critCol=input.color(color.new(color.new('#FF1111'), 60), "Critical band", group=grpStyles, inline="sz2"),
    upColor=input.color(color.teal, "Uptrend Stop Line", inline='style', group=grpStyles),
    dnColor=input.color(color.orange, "⠀⠀⠀⠀⠀⠀⠀⠀Downtrend Stop Line", inline='style', group=grpStyles),
    showFlips=input.bool(True, "Show flip markers", group=grpStyles),
    tblSizeOpt=input.string("Small", "Table text size", options=("Small", "Normal", "Large"), group=grpStyles, inline='tbl', tooltip="Text size of the on-chart info table.", display=disnon),
    tblPosOpt=input.string("Top Right", "⠀⠀⠀⠀Table position", options=("Top Right", "Middle Right", "Bottom Right"), group=grpStyles, inline='tbl', tooltip="Position of the info table.", display=disnon)
):
    def fixtick(_value):
        return string.tostring(math.round_to_mintick(_value), '#,###.######')


    isATR = TStop_mode == 'ATR / Supertrend'
    isChan = TStop_mode == 'Chandelier'
    isDonc = TStop_mode == 'Donchian'
    isSD = TStop_mode == 'StdDev Channel'
    isPct = TStop_mode == 'Fixed %'

    usesAnchor = isATR or isSD or isPct

    htfInvalid = useMTF and timeframe.in_seconds(atrTF) < timeframe.in_seconds()

    atrMTF = request.security(syminfo.tickerid, atrTF, inline_series(ta.atr(atrLen), 1), lookahead=barmerge.lookahead_off)
    atrVal = atrMTF if useMTF else ta.atr(atrLen)

    distATR = atrVal * atrMult
    distSD = ta.stdev(anchorSrc, sdLen) * sdMult
    distPct = anchorSrc * pctOff / 100

    chAtr = ta.atr(chAtrLen)
    chHi = ta.highest(high, chLen)
    chLo = ta.lowest(low, chLen)
    chLoStop = chHi - chAtr * chMult
    chHiStop = chLo + chAtr * chMult

    dcLo = ta.lowest(low, dcLen)
    dcHi = ta.highest(high, dcLen)

    loStop = chLoStop if isChan else dcLo if isDonc else anchorSrc - distSD if isSD else anchorSrc - distPct if isPct else anchorSrc - distATR

    hiStop = chHiStop if isChan else dcHi if isDonc else anchorSrc + distSD if isSD else anchorSrc + distPct if isPct else anchorSrc + distATR

    isEstimate = isChan or isDonc

    upTr: Series = loStop
    upTr = math.max(loStop, nz(upTr[1])) if close[1] > nz(upTr[1]) else loStop

    dnTr: Series = hiStop
    dnTr = math.min(hiStop, nz(dnTr[1])) if close[1] < nz(dnTr[1]) else hiStop

    trend: PersistentSeries[int] = 1
    trend = 1 if close > nz(dnTr[1], dnTr) else -1 if close < nz(upTr[1], upTr) else nz(trend[1], 1)

    stopLine = upTr if trend == 1 else dnTr

    critAtr = ta.atr(critAtrLen)
    gapATR = math.abs(close - stopLine) / critAtr if critAtr > 0 else na
    watchZone = safeZone / 2.0
    critZone: Series = 'safe' if na(gapATR) else 'safe' if gapATR >= safeZone else 'watch' if gapATR >= watchZone else 'critical'
    critOrb = '🟢' if critZone == 'safe' else '🟡' if critZone == 'watch' else '🔴'
    critWord = 'Safe' if critZone == 'safe' else 'Watch' if critZone == 'watch' else 'Critical'
    critColor = color.green if critZone == 'safe' else color.yellow if critZone == 'watch' else color.red

    dir = 1.0 if trend == 1 else -1.0
    critBound = stopLine + dir * watchZone * critAtr
    safeBound = stopLine + dir * safeZone * critAtr

    flipUp = trend == 1 and trend[1] == -1
    flipDn = trend == -1 and trend[1] == 1

    showViz = not htfInvalid

    hiddenCol = color.new(color.gray, 100)
    bbCol = color.new(color.new('#787B86'), 40)
    dspFill = display.all if showBands else display.none
    disBBs = display.pane + display.price_scale if showBBs else disnon

    pStop = plot(stopLine if showViz else na, 'band: stop', color=hiddenCol, display=disnon)

    pCrit = plot(critBound if showViz else na, 'band: critical', color=bbCol if showBBs else hiddenCol, display=disBBs)

    pSafe = plot(safeBound if showViz else na, 'band: safe', color=bbCol if showBBs else hiddenCol, display=disBBs)

    fill(pStop, pCrit, top_value=stopLine, bottom_value=critBound, top_color=critCol, bottom_color=watchCol, title='Critical band fill', display=dspFill)

    fill(pCrit, pSafe, top_value=critBound, bottom_value=safeBound, top_color=watchCol, bottom_color=safeCol, title='Watch band fill', display=dspFill)

    plot(stopLine if showViz else na, 'Trail Stop', color=upColor if trend == 1 else dnColor, linewidth=3, style=plot.style_linebr)

    plotshape(stopLine - critAtr if showViz and showFlips and flipUp else na, 'Flip UP', shape.triangleup, location.absolute, upColor, size=size.small, text='FLIP', textcolor=upColor, display=display.pane)

    plotshape(stopLine + critAtr if showViz and showFlips and flipDn else na, 'Flip DOWN', shape.triangledown, location.absolute, dnColor, size=size.small, text='\nFLIP', textcolor=dnColor, display=display.pane)

    if htfInvalid and barstate.islast:
        label.new(bar_index, high, '⚠ HTF ATR timeframe (' + atrTF + ") is LOWER than the chart.\n\nPick a higher timeframe, or turn off 'Use HTF ATR'.", color=color.new(color.new('#830E2A'), 0), textcolor=color.white, style=label.style_label_down, size=size.large)

    methodLabel = 'Chandelier · ' + string.tostring(chMult, '#.00') + 'x ATR(' + string.tostring(chAtrLen) + ')' if isChan else 'Donchian · ' + string.tostring(dcLen) + ' bars' if isDonc else 'StdDev · ' + string.tostring(sdMult, '#.00') + 'x' if isSD else 'Fixed% · ' + string.tostring(pctOff, '#.00') + '%' if isPct else 'ATR / SuperTrend · ' + string.tostring(atrMult, '#.00') + 'x ATR(' + string.tostring(atrLen) + ')'
    titleText = methodLabel

    distNow = math.abs(close - stopLine)

    distText = string.tostring(pctOff, '#.00') + '% (setting)' if isPct else fixtick(distNow) + ' ' + syminfo.currency + ' (estimate)' if isEstimate else fixtick(distNow) + ' ' + syminfo.currency + ' (current)'

    sideText = 'from Long side' if trend == 1 else 'from Short side'

    safeAtrExpr = string.tostring(safeZone, '#.00') + 'x ATR(' + string.tostring(critAtrLen) + ')'

    tblSize = size.large if tblSizeOpt == 'Large' else size.normal if tblSizeOpt == 'Normal' else size.small

    tblPos = position.top_right if tblPosOpt == 'Top Right' else position.middle_right if tblPosOpt == 'Middle Right' else position.bottom_right

    flipSignal = 1 if flipUp else -1 if flipDn else 0
    plot(flipSignal, 'Flip signal', color=hiddenCol, display=display.data_window)

    info: Persistent[Table] = table.new(tblPos, 1, 8, bgcolor=color.new(color.black, 80))
    if barstate.islast and showViz:
        table.cell(info, 0, 0, '───────  RedK MMTStop  ───────', text_color=upColor if trend == 1 else dnColor, text_size=tblSize)
        table.cell(info, 0, 1, titleText, text_color=color.white, text_size=tblSize)
        table.cell(info, 0, 2, ('▲ Long stop: ' if trend == 1 else '▼ Short stop: ') + fixtick(stopLine), text_color=upColor if trend == 1 else dnColor, text_size=tblSize)
        table.cell(info, 0, 3, 'Dist: ' + distText, text_color=color.white, text_size=tblSize)
        table.cell(info, 0, 4, sideText, text_color=color.white, text_size=tblSize)
        table.cell(info, 0, 5, critOrb + ' ' + critWord + ' → ' + string.tostring(gapATR, '#.00') + 'x ATR(' + string.tostring(critAtrLen) + ') to stop', text_color=critColor, text_size=tblSize)
        table.cell(info, 0, 6, '🔴→🟡 at ' + fixtick(critBound), text_color=color.new(color.yellow, 0), text_size=tblSize)
        table.cell(info, 0, 7, '🟡→🟢 at ' + fixtick(safeBound), text_color=color.new(color.green, 0), text_size=tblSize)

    alertcondition(flipUp, 'Trailing flip UP', 'RedK MMTStop: trend flipped UP — stop now trails price from below')
    alertcondition(flipDn, 'Trailing flip DOWN', 'RedK MMTStop: trend flipped DOWN — stop now sits overhead')
    alertcondition(ta.crossunder(close, stopLine), 'Close under stop', 'RedK MMTStop: close crossed BELOW the trailing stop')
    alertcondition(ta.crossover(close, stopLine), 'Close over stop', 'RedK MMTStop: close crossed ABOVE the trailing stop')
    alertcondition(critZone == 'critical' and critZone[1] != 'critical', 'Entered CRITICAL zone', 'RedK MMTStop: price entered the CRITICAL zone. Buffer under 0.5x safe distance. Consider closing manually.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
