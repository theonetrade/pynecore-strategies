"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, close, color, display, format, high, input,
    label, line, linefill, low, math, na, nz, plot, script, size, string, ta
)
from pynecore.types import Color, Label, Line, LineFill, NA, Persistent, PersistentSeries


@udt
class Swing:
    isHigh: bool = na(bool)
    price: float = na(float)
    bar: int = na(int)
    confirmBar: int = na(int)
    tag: str = na(str)
    tagLabel: Label = na(Label)
    legLine: Line = na(Line)


@udt
class Fib:
    dir: int = na(int)
    hiPrice: float = na(float)
    hiBar: int = na(int)
    loPrice: float = na(float)
    loBar: int = na(int)
    level0382: float = na(float)
    level05: float = na(float)
    level0618: float = na(float)
    level086: float = na(float)
    confirmPrice: float = na(float)
    createdBar: int = na(int)
    retraceExtreme: float = na(float)
    confirmBar: int = na(int)
    line0: Line = na(Line)
    line0382: Line = na(Line)
    line05: Line = na(Line)
    line0618: Line = na(Line)
    line086: Line = na(Line)
    line1: Line = na(Line)
    label0: Label = na(Label)
    label0382: Label = na(Label)
    label05: Label = na(Label)
    label0618: Label = na(Label)
    label086: Label = na(Label)
    label1: Label = na(Label)
    goldZone: LineFill = na(LineFill)


@udt
class ChainMove:
    dir: int = na(int)
    anchor: float = na(float)
    anchorBar: int = na(int)
    extreme: float = na(float)
    extremeBar: int = na(int)
    mustBeat: float = na(float)


GRP_SWING: str = "Structure Detection"
GRP_STYLE: str = "Fibonacci Appearance"
GRP_ZONE: str = "Gold Zone (0.5 – 0.618)"
METHOD_ATR: str = "ATR ZigZag"
METHOD_CHAIN: str = "Retracement Chain"


@script.indicator("Auto Structure Fibonacci", shorttitle="Auto Fib", overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    methodInput=input.string(METHOD_ATR, "Structure Method", options=(METHOD_ATR, METHOD_CHAIN), group=GRP_SWING, tooltip="ATR ZigZag: Fibonacci over each HH/LL leg between ATR-confirmed swings.\nRetracement Chain: each Fibonacci is anchored at the pull-back extreme after the previous Fibonacci in the same direction, must extend beyond that Fibonacci's 0, and flips direction when price breaks the last Fibonacci's 1."),
    atrConfirmInput=input.float(0.5, "Confirmation Level (ATR ZigZag)", minval=0.1, maxval=1.0, step=0.001, group=GRP_SWING, tooltip="Retracement a leg must reach before its Fibonacci is drawn."),
    chainConfirmInput=input.float(0.382, "Confirmation Level (Retracement Chain)", minval=0.1, maxval=1.0, step=0.001, group=GRP_SWING, tooltip="Retracement a move must reach before its Fibonacci is drawn."),
    atrLengthInput=input.int(14, "ATR Length", minval=1, group=GRP_SWING),
    atrMultInput=input.float(2.6, "ATR Reversal Multiplier", minval=0.1, step=0.1, group=GRP_SWING, tooltip="ATR ZigZag: a swing is confirmed once price reverses from it by ATR × this multiplier. Higher = fewer, larger swings."),
    minFibSizeInput=input.float(0.0, "Minimum Fibonacci Size (× ATR)", minval=0.0, step=0.5, group=GRP_SWING, tooltip="A move must be at least ATR × this value tall (from its 1 to its 0) to be drawn. Filters out Fibonaccis on small moves. Applies to both methods; in Retracement Chain a smaller move still counts as a link in the chain, it just isn't drawn. 0 = off."),
    minBreakInput=input.float(0.0, "Minimum Break (× ATR)", minval=0.0, step=0.05, group=GRP_SWING, tooltip="A new high only counts as a Higher High (and a new low as a Lower Low) if it beats the previous one by at least ATR × this value. Smaller breaks are treated as Equal Highs/Lows, so no leg is created — this filters double tops/bottoms and ranges. In Retracement Chain, a continuation must also beat the previous Fibonacci's 0 by this much. 0 = off."),
    showSwingsInput=input.bool(False, "Show Swing Structure", group=GRP_SWING, tooltip="Grey zigzag joining the detected ATR swings, plus a dashed line for the leg still forming. Shows the most recent 50 swings, whichever method is selected."),
    showSwingTagsInput=input.bool(False, "Show Swing Labels", group=GRP_SWING, tooltip="HH/HL/LH/LL/EQH/EQL labels on the detected ATR swings (hover for price and confirmation delay). Independent of Show Swing Structure."),
    atrDisplayInput=input.string("Off", "ATR Display", options=("Off", "Reversal Level", "ATR Bands"), group=GRP_SWING, tooltip="Reversal Level: the price the current leg must reverse to for its swing to be confirmed (leg extreme ∓ ATR × multiplier). Below price in a rising leg, above it in a falling leg; it flips side when a swing is confirmed.\nATR Bands: close ± ATR × multiplier, for reference.\nWhen on, the ATR and reversal threshold values are also shown in the Data Window."),
    maxFibsInput=input.int(10, "Maximum Historical Fibonacci Structures", minval=1, maxval=50, group=GRP_STYLE, tooltip="Total confirmed Fibonaccis kept on the chart (bullish and bearish combined). When exceeded, the oldest is removed."),
    showBullInput=input.bool(True, "Show Bullish Structures", group=GRP_STYLE),
    showBearInput=input.bool(True, "Show Bearish Structures", group=GRP_STYLE),
    showLabelsInput=input.bool(True, "Show Level Values", group=GRP_STYLE, tooltip="Level (0, 0.382, 0.5, 0.618, 0.86, 1) at the right-hand end of each line, in the line's colour."),
    showPricesInput=input.bool(False, "Show Prices in Level Values", group=GRP_STYLE, tooltip="Adds the price after each level, e.g. 0.618 (1.27450)."),
    extensionInput=input.int(30, "Fibonacci Extension Bars", minval=0, maxval=400, group=GRP_STYLE, tooltip="How far the levels extend to the right of the bar where the Fibonacci was confirmed."),
    lineWidthInput=input.int(1, "Line Width", minval=1, maxval=4, group=GRP_STYLE),
    lineStyleInput=input.string("Solid", "Line Style", options=("Solid", "Dashed", "Dotted"), group=GRP_STYLE),
    labelSizeInput=input.string("Small", "Level Value Size", options=("Tiny", "Small", "Normal"), group=GRP_STYLE),
    colLevel0Input=input.color(color.new('#787B86'), "Level 0 Colour", group=GRP_STYLE),
    show0382Input=input.bool(True, "Show 0.382 Level", group=GRP_STYLE),
    colLevel0382Input=input.color(color.new('#5B9CF6'), "Level 0.382 Colour", group=GRP_STYLE),
    colLevel05Input=input.color(color.new('#F5B400'), "Level 0.5 Colour", group=GRP_STYLE),
    colLevel0618Input=input.color(color.new('#F5B400'), "Level 0.618 Colour", group=GRP_STYLE),
    show086Input=input.bool(True, "Show 0.86 Level", group=GRP_STYLE, tooltip="Reference level only; it does not affect when Fibonaccis are drawn."),
    colLevel086Input=input.color(color.new('#F23645'), "Level 0.86 Colour", group=GRP_STYLE),
    colLevel1Input=input.color(color.new('#787B86'), "Level 1 Colour", group=GRP_STYLE),
    showGoldZoneInput=input.bool(True, "Show Gold Zone", group=GRP_ZONE),
    colGoldZoneInput=input.color(color.new(color.new('#F5B400'), 85), "Gold Zone Fill", group=GRP_ZONE)
):
    MAX_SWINGS: int = 50

    DIR_BULL: int = 1
    DIR_BEAR: int = -1

    COL_BULL: Color = color.new('#26A69A')
    COL_BEAR: Color = color.new('#EF5350')
    COL_MUTED: Color = color.new('#787B86')




    swings: Persistent[list[Swing]] = array.new(0, NA(Swing))

    drawnFibs: Persistent[list[Fib]] = array.new(0, NA(Fib))

    atrValue: float = ta.atr(atrLengthInput)

    isAtrMethod: bool = methodInput == METHOD_ATR

    def structureTag(isHigh: bool, price: float, prevSameTypePrice: float, minBreak: float):
        tag: str = 'H' if isHigh else 'L'
        if not na(prevSameTypePrice):
            if isHigh:
                tag = 'HH' if price > prevSameTypePrice + minBreak else 'EQH' if price >= prevSameTypePrice else 'LH'
            else:
                tag = 'LL' if price < prevSameTypePrice - minBreak else 'EQL' if price <= prevSameTypePrice else 'HL'
        return tag

    @method
    def drawStructure(this: Swing, prev: Swing):
        if showSwingTagsInput:
            tagCol: Color = COL_BULL if this.tag == 'HH' or this.tag == 'HL' else COL_BEAR if this.tag == 'LH' or this.tag == 'LL' else COL_MUTED
            tip: str = this.tag + '  ' + string.tostring(this.price, format.mintick) + '\nconfirmed ' + string.tostring(this.confirmBar - this.bar) + ' bars later'
            this.tagLabel = label.new(this.bar, this.price, this.tag, style=label.style_label_down if this.isHigh else label.style_label_up, color=color.new(tagCol, 20), textcolor=color.white, size=size.small, tooltip=tip)
        if showSwingsInput and (not na(prev)):
            this.legLine = line.new(prev.bar, prev.price, this.bar, this.price, color=color.new(COL_MUTED, 20), width=1)
        return this

    def recordSwing(isHigh: bool, price: float, bar: int):
        n: int = array.size(swings)
        prevSame: float = na(float)
        prevLeg: Swing = na(Swing)
        if n >= 2:
            prevSame = array.get(swings, n - 2).price
        if n >= 1:
            prevLeg = array.get(swings, n - 1)
        s: Swing = Swing(isHigh, price, bar, bar_index, structureTag(isHigh, price, prevSame, nz(atrValue) * minBreakInput))
        array.push(swings, s)
        drawStructure(s, prevLeg)
        if array.size(swings) > MAX_SWINGS:
            oldest: Swing = array.shift(swings)
            label.delete(oldest.tagLabel)
            line.delete(oldest.legLine)
        return s

    def fibLevel(dir: int, hiPrice: float, loPrice: float, ratio: float):
        legRange: float = hiPrice - loPrice
        return hiPrice - legRange * ratio if dir == DIR_BULL else loPrice + legRange * ratio

    def bigEnough(hi: float, lo: float):
        return hi - lo >= minFibSizeInput * nz(atrValue)

    def isBullishLeg(start: Swing, end: Swing):
        return end.tag == 'HH' and (start.tag == 'LL' or start.tag == 'HL' or start.tag == 'EQL')

    def isBearishLeg(start: Swing, end: Swing):
        return end.tag == 'LL' and (start.tag == 'HH' or start.tag == 'LH' or start.tag == 'EQH')

    def newFib(dir: int, hi: float, hiBar: int, lo: float, loBar: int, confirmRatio: float, retraceSoFar: float):
        return Fib(dir=dir, hiPrice=hi, hiBar=hiBar, loPrice=lo, loBar=loBar, level0382=fibLevel(dir, hi, lo, 0.382), level05=fibLevel(dir, hi, lo, 0.5), level0618=fibLevel(dir, hi, lo, 0.618), level086=fibLevel(dir, hi, lo, 0.86), confirmPrice=fibLevel(dir, hi, lo, confirmRatio), createdBar=bar_index, retraceExtreme=retraceSoFar)

    def createFib(dir: int, start: Swing, end: Swing, retraceSoFar: float):
        hi: float = end.price if dir == DIR_BULL else start.price
        lo: float = start.price if dir == DIR_BULL else end.price
        hiBar: int = end.bar if dir == DIR_BULL else start.bar
        loBar: int = start.bar if dir == DIR_BULL else end.bar
        return newFib(dir, hi, hiBar, lo, loBar, atrConfirmInput, retraceSoFar)

    @method
    def step(this: Fib):
        bull: bool = this.dir == DIR_BULL
        status: int = 0

        if bar_index > this.createdBar:
            if high > this.hiPrice if bull else low < this.loPrice:
                status = -1
            else:
                this.retraceExtreme = math.min(this.retraceExtreme, low) if bull else math.max(this.retraceExtreme, high)
        if status == 0 and (this.retraceExtreme <= this.confirmPrice if bull else this.retraceExtreme >= this.confirmPrice):
            status = 1
        return status

    def levelLabel(x: int, price: float, levelText: str, textCol: Color):
        labelSize: str = size.tiny if labelSizeInput == 'Tiny' else size.normal if labelSizeInput == 'Normal' else size.small
        labelText: str = levelText + ' (' + string.tostring(price, format.mintick) + ')' if showPricesInput else levelText
        return label.new(x, price, labelText, style=label.style_label_left, color=NA(Color), textcolor=textCol, size=labelSize)

    def levelLine(x1: int, x2: int, price: float, lineCol: Color):
        style: str = line.style_dashed if lineStyleInput == 'Dashed' else line.style_dotted if lineStyleInput == 'Dotted' else line.style_solid
        return line.new(x1, price, x2, price, color=lineCol, style=style, width=lineWidthInput)

    @method
    def drawFib(this: Fib):
        bull: bool = this.dir == DIR_BULL
        level0: float = this.hiPrice if bull else this.loPrice
        level1: float = this.loPrice if bull else this.hiPrice
        x1: int = math.min(this.hiBar, this.loBar)
        x2: int = this.confirmBar + extensionInput
        this.line0 = levelLine(x1, x2, level0, colLevel0Input)
        if show0382Input:
            this.line0382 = levelLine(x1, x2, this.level0382, colLevel0382Input)
        this.line05 = levelLine(x1, x2, this.level05, colLevel05Input)
        this.line0618 = levelLine(x1, x2, this.level0618, colLevel0618Input)
        if show086Input:
            this.line086 = levelLine(x1, x2, this.level086, colLevel086Input)
        this.line1 = levelLine(x1, x2, level1, colLevel1Input)
        if showGoldZoneInput:
            this.goldZone = linefill.new(this.line05, this.line0618, colGoldZoneInput)
        if showLabelsInput:
            this.label0 = levelLabel(x2, level0, '0', colLevel0Input)
            if show0382Input:
                this.label0382 = levelLabel(x2, this.level0382, '0.382', colLevel0382Input)
            this.label05 = levelLabel(x2, this.level05, '0.5', colLevel05Input)
            this.label0618 = levelLabel(x2, this.level0618, '0.618', colLevel0618Input)
            if show086Input:
                this.label086 = levelLabel(x2, this.level086, '0.86', colLevel086Input)
            this.label1 = levelLabel(x2, level1, '1', colLevel1Input)
        return this

    @method
    def deleteDrawing(this: Fib):
        linefill.delete(this.goldZone)
        line.delete(this.line0)
        line.delete(this.line0382)
        line.delete(this.line05)
        line.delete(this.line0618)
        line.delete(this.line086)
        line.delete(this.line1)
        label.delete(this.label0)
        label.delete(this.label0382)
        label.delete(this.label05)
        label.delete(this.label0618)
        label.delete(this.label086)
        label.delete(this.label1)
        return this

    def storeFib(confirmed: Fib):
        array.push(drawnFibs, confirmed)
        __block_result__ = na
        while array.size(drawnFibs) > maxFibsInput:
            __block_result__ = method_call(deleteDrawing, array.shift(drawnFibs))
        return __block_result__

    lastFibEndBar: Persistent[list[int]] = array.new_int(1, na)

    def publishFib(confirmed: Fib, visible: bool):
        confirmed.confirmBar = bar_index
        startBar: int = math.min(confirmed.hiBar, confirmed.loBar)
        endBar: int = math.max(confirmed.hiBar, confirmed.loBar) if isAtrMethod else bar_index
        prevEnd: int = array.get(lastFibEndBar, 0)
        noOverlap: bool = na(prevEnd) or startBar >= prevEnd
        if noOverlap:
            array.set(lastFibEndBar, 0, endBar)
            if visible and (showBullInput if confirmed.dir == DIR_BULL else showBearInput):
                drawFib(confirmed)
                storeFib(confirmed)
        return confirmed

    def resolvePending(pending: Fib):
        result: Fib = pending
        if not na(pending):
            status: int = step(pending)
            if status == 1:
                publishFib(pending, True)
                result = na
            elif status == -1:
                result = na
        return result

    zzDir: PersistentSeries[int] = 0
    zzExtreme: Persistent[float] = na(float)
    zzExtremeBar: Persistent[int] = na(int)
    zzCounter: Persistent[float] = na(float)
    zzCounterBar: Persistent[int] = na(int)

    pendingBull: Persistent[Fib] = na(Fib)
    pendingBear: Persistent[Fib] = na(Fib)

    if barstate.isconfirmed:
        if zzDir == 0:
            zzDir = 1
            zzExtreme = high
            zzExtremeBar = bar_index
        else:
            up: bool = zzDir == 1
            pushSrc: float = high if up else low
            pullSrc: float = low if up else high
            if pushSrc > zzExtreme if up else pushSrc < zzExtreme:
                zzExtreme = pushSrc
                zzExtremeBar = bar_index
                zzCounter = na
                zzCounterBar = na
            else:
                if na(zzCounter) or (pullSrc < zzCounter if up else pullSrc > zzCounter):
                    zzCounter = pullSrc
                    zzCounterBar = bar_index
                if math.abs(zzExtreme - zzCounter) >= atrValue * atrMultInput:
                    newSwing: Swing = recordSwing(up, zzExtreme, zzExtremeBar)
                    retraceSoFar: float = zzCounter
                    zzDir = -zzDir
                    zzExtreme = zzCounter
                    zzExtremeBar = zzCounterBar
                    zzCounter = na
                    zzCounterBar = na

                    n: int = array.size(swings)
                    if isAtrMethod and n >= 2:
                        legStart: Swing = array.get(swings, n - 2)
                        legSized: bool = bigEnough(math.max(legStart.price, newSwing.price), math.min(legStart.price, newSwing.price))
                        if legSized and showBullInput and newSwing.isHigh and isBullishLeg(legStart, newSwing):
                            pendingBull = createFib(DIR_BULL, legStart, newSwing, retraceSoFar)
                        elif legSized and showBearInput and (not newSwing.isHigh) and isBearishLeg(legStart, newSwing):
                            pendingBear = createFib(DIR_BEAR, legStart, newSwing, retraceSoFar)

        pendingBull = resolvePending(pendingBull)
        pendingBear = resolvePending(pendingBear)

    @method
    def advance(this: ChainMove):
        bull: bool = this.dir == DIR_BULL
        pushSrc: float = high if bull else low
        pullSrc: float = low if bull else high
        formed: bool = False
        if not na(this.extreme) and (pushSrc <= this.extreme if bull else pushSrc >= this.extreme):
            minBreak: float = nz(atrValue) * minBreakInput
            beyondPrev: bool = na(this.mustBeat) or (this.extreme > this.mustBeat + minBreak if bull else this.extreme < this.mustBeat - minBreak)
            hi: float = this.extreme if bull else this.anchor
            lo: float = this.anchor if bull else this.extreme
            confirmPrice: float = fibLevel(this.dir, hi, lo, chainConfirmInput)
            formed = beyondPrev and (pullSrc <= confirmPrice if bull else pullSrc >= confirmPrice)
        if not formed:
            if pullSrc < this.anchor if bull else pullSrc > this.anchor:
                this.anchor = pullSrc
                this.anchorBar = bar_index
                this.extreme = na
                this.extremeBar = na
            elif na(this.extreme) or (pushSrc > this.extreme if bull else pushSrc < this.extreme):
                this.extreme = pushSrc
                this.extremeBar = bar_index
        return formed

    @method
    def toFib(this: ChainMove):
        bull: bool = this.dir == DIR_BULL
        return newFib(this.dir, this.extreme if bull else this.anchor, this.extremeBar if bull else this.anchorBar, this.anchor if bull else this.extreme, this.anchorBar if bull else this.extremeBar, chainConfirmInput, na)

    chainDir: Persistent[int] = 0
    chainBull: Persistent[ChainMove] = na(ChainMove)
    chainBear: Persistent[ChainMove] = na(ChainMove)
    chainLastFib: Persistent[Fib] = na(Fib)
    chainSinceExtreme: Persistent[float] = na(float)
    chainSinceExtremeBar: Persistent[int] = na(int)

    if barstate.isconfirmed and (not isAtrMethod):
        if na(chainBull):
            chainBull = ChainMove(DIR_BULL, low, bar_index, na, na, na)
            chainBear = ChainMove(DIR_BEAR, high, bar_index, na, na, na)
        else:
            bullFormed: bool = chainDir != DIR_BEAR and advance(chainBull)
            bearFormed: bool = chainDir != DIR_BULL and advance(chainBear)

            if bullFormed and bearFormed:
                if chainBull.extremeBar >= chainBear.extremeBar:
                    bearFormed = False
                else:
                    bullFormed = False

            if bullFormed or bearFormed:
                move: ChainMove = chainBull if bullFormed else chainBear
                bull: bool = move.dir == DIR_BULL
                f: Fib = toFib(move)

                publishFib(f, bigEnough(f.hiPrice, f.loPrice))
                chainLastFib = f
                chainDir = move.dir

                chainSinceExtreme = high if bull else low
                chainSinceExtremeBar = bar_index

                next: ChainMove = ChainMove(move.dir, low if bull else high, bar_index, na, na, f.hiPrice if bull else f.loPrice)
                if bull:
                    chainBull = next
                else:
                    chainBear = next
            elif chainDir != 0:
                bull: bool = chainDir == DIR_BULL
                if high > chainSinceExtreme if bull else low < chainSinceExtreme:
                    chainSinceExtreme = high if bull else low
                    chainSinceExtremeBar = bar_index

                lastFib1: float = chainLastFib.loPrice if bull else chainLastFib.hiPrice
                if low < lastFib1 if bull else high > lastFib1:
                    chainDir = 0
                    if bull:
                        chainBear = ChainMove(DIR_BEAR, chainSinceExtreme, chainSinceExtremeBar, low, bar_index, na)
                        chainBull = ChainMove(DIR_BULL, low, bar_index, na, na, na)
                    else:
                        chainBull = ChainMove(DIR_BULL, chainSinceExtreme, chainSinceExtremeBar, high, bar_index, na)
                        chainBear = ChainMove(DIR_BEAR, high, bar_index, na, na, na)

    formingLegLine: Persistent[Line] = na(Line)
    if barstate.islast and showSwingsInput:
        line.delete(formingLegLine)
        n: int = array.size(swings)
        if n > 0 and (not na(zzExtremeBar)):
            lastSwing: Swing = array.get(swings, n - 1)
            formingLegLine = line.new(lastSwing.bar, lastSwing.price, zzExtremeBar, zzExtreme, color=COL_MUTED, style=line.style_dashed, width=1)

    reversalThreshold: float = atrValue * atrMultInput

    reversalLevel: float = zzExtreme - reversalThreshold if zzDir == 1 else zzExtreme + reversalThreshold if zzDir == -1 else na
    legFlipped: bool = zzDir != zzDir[1]

    showReversal: bool = atrDisplayInput == 'Reversal Level'
    showBands: bool = atrDisplayInput == 'ATR Bands'

    plot(na if legFlipped else reversalLevel, 'Reversal Level', color=COL_BULL if zzDir == 1 else COL_BEAR, style=plot.style_linebr, display=display.all if showReversal else display.none)
    plot(close + reversalThreshold, 'Upper ATR Band', color=COL_MUTED, display=display.all if showBands else display.none)
    plot(close - reversalThreshold, 'Lower ATR Band', color=COL_MUTED, display=display.all if showBands else display.none)
    plot(atrValue, 'ATR', color=COL_MUTED, display=display.data_window if atrDisplayInput != 'Off' else display.none)
    plot(reversalThreshold, 'Reversal Threshold', color=COL_MUTED, display=display.data_window if atrDisplayInput != 'Off' else display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)