"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, high, input, label, line,
    linefill, low, math, na, open, plot, script, size, ta
)
from pynecore.types import Line, Persistent, Series


@script.indicator('Best S&R Indicator With Candlestick Patterns', overlay=True, max_lines_count=500)
def main(
    Bars=input.int(10, 'Swing Lookback (Bars)', minval=5, confirm=True),
    NoOfPivots=input.int(2, 'Pivot Tests for Valid Zone', options=(2, 3, 4), confirm=True),
    ZoneExpiry=input.int(200, 'Zone Expiry (candles, 0 = never)', minval=0),
    ResColor=input.color(color.red, 'Resistance Color', group='Zone Style'),
    SupColor=input.color(color.green, 'Support Color', group='Zone Style'),
    BrokenColor=input.color(color.new(color.gray, 60), 'Broken Zone Color', group='Zone Style'),
    ZoneAlpha=input.int(80, 'Zone Fill Transparency %', minval=0, maxval=100, group='Zone Style'),
    ShowBroken=input.bool(True, 'Show Broken Zones (grayed)', group='Zone Style'),
    ShowPatterns=input.bool(True, 'Show Candle Pattern Labels', group='Patterns'),
    ProximityPct=input.float(0.3, 'Proximity % (buffer around zone)', minval=0.05, step=0.05, group='Proximity & Alerts'),
    ShowRetest=input.bool(True, 'Show Zone Retest Labels', group='Retest')
):
    ShowProximityBG: bool = False

    PivotHigh = ta.pivothigh(Bars, Bars)
    PivotLow = ta.pivotlow(Bars, Bars)

    InsideBarAtSupport: Persistent[bool] = False

    rTopLines: Persistent[list[Line]] = array.new_line()
    rBotLines: Persistent[list[Line]] = array.new_line()
    rZoneHArr: Persistent[list[float]] = array.new_float()
    rZoneLArr: Persistent[list[float]] = array.new_float()
    rZoneStart: Persistent[list[int]] = array.new_int()
    rWasAway: Persistent[list[bool]] = array.new_bool()
    RZoneH: Persistent[float] = na(float)
    RZoneL: Persistent[float] = na(float)

    sTopLines: Persistent[list[Line]] = array.new_line()
    sBotLines: Persistent[list[Line]] = array.new_line()
    sZoneHArr: Persistent[list[float]] = array.new_float()
    sZoneLArr: Persistent[list[float]] = array.new_float()
    sZoneStart: Persistent[list[int]] = array.new_int()
    sWasAway: Persistent[list[bool]] = array.new_bool()
    SZoneH: Persistent[float] = na(float)
    SZoneL: Persistent[float] = na(float)

    IndexOfPivot = ta.valuewhen(PivotHigh > 0, bar_index - Bars, 0)
    HighAtPivot = ta.valuewhen(PivotHigh > 0, high[Bars], 0)
    UpperAtPivot = ta.valuewhen(PivotHigh > 0, math.max(close[Bars], open[Bars]), 0)
    IndexOfPivot1 = ta.valuewhen(PivotHigh > 0, bar_index - Bars, 1)
    HighAtPivot1 = ta.valuewhen(PivotHigh > 0, high[Bars], 1)
    UpperAtPivot1 = ta.valuewhen(PivotHigh > 0, math.max(close[Bars], open[Bars]), 1)
    IndexOfPivot2 = ta.valuewhen(PivotHigh > 0, bar_index - Bars, 2)
    HighAtPivot2 = ta.valuewhen(PivotHigh > 0, high[Bars], 2)
    UpperAtPivot2 = ta.valuewhen(PivotHigh > 0, math.max(close[Bars], open[Bars]), 2)
    IndexOfPivot3 = ta.valuewhen(PivotHigh > 0, bar_index - Bars, 3)
    HighAtPivot3 = ta.valuewhen(PivotHigh > 0, high[Bars], 3)
    UpperAtPivot3 = ta.valuewhen(PivotHigh > 0, math.max(close[Bars], open[Bars]), 3)

    IndexOfPivotl1 = ta.valuewhen(PivotLow > 0, bar_index - Bars, 1)
    LowAtPivot = ta.valuewhen(PivotLow > 0, low[Bars], 0)
    LowerAtPivotl = ta.valuewhen(PivotLow > 0, math.min(close[Bars], open[Bars]), 1)
    LowAtPivot1 = ta.valuewhen(PivotLow > 0, low[Bars], 1)
    IndexOfPivotl2 = ta.valuewhen(PivotLow > 0, bar_index - Bars, 2)
    LowAtPivot2 = ta.valuewhen(PivotLow > 0, low[Bars], 2)
    LowerAtPivot2 = ta.valuewhen(PivotLow > 0, math.min(close[Bars], open[Bars]), 2)
    IndexOfPivotl3 = ta.valuewhen(PivotLow > 0, bar_index - Bars, 3)
    LowAtPivot3 = ta.valuewhen(PivotLow > 0, low[Bars], 3)
    LowerAtPivot3 = ta.valuewhen(PivotLow > 0, math.min(close[Bars], open[Bars]), 3)

    alertcon: bool = False
    candle: Series = math.abs(high - low)
    body: Series = math.abs(open - close)
    BodyPerc: Series = body / candle * 100

    EvnCan = body > candle * 0.6 and open > close and (body[1] < candle[1] * 0.3) and (body[2] > candle[2] * 0.6) and (open[2] < close[2])
    BInBar = high < high[1] and low > low[1] and (body[1] > candle[1] * 0.4)
    MorCan = body > candle * 0.6 and open < close and (body[1] < candle[1] * 0.3) and (body[2] > candle[2] * 0.6) and (open[2] > close[2])
    BullInBar = high < high[1] and low > low[1] and (body[1] > candle[1] * 0.4)
    bperc = (high[1] - low[1]) / 100 * 5
    bpercc = (high[1] - low[1]) / 100 * 60
    tbc = low > low[1] - bperc and low < low[1] + bperc and (close > low[1] + bpercc) and (open[1] > close[1]) and (close[1] - low[1] < bperc) and (open - low < bperc) and (BodyPerc > 60) and (BodyPerc[1] > 60)
    ttc = high > high[1] - bperc and high < high[1] + bperc and (close < high[1] - bpercc) and (open[1] < close[1]) and (high[1] - close[1] < bperc) and (high - open < bperc) and (BodyPerc > 60) and (BodyPerc[1] > 60)

    EvnCanHigh = ta.valuewhen(EvnCan, high[1], 0)
    BInBarHigh = ta.valuewhen(BInBar, high[1], 0)
    MorCanLow = ta.valuewhen(MorCan, low[1], 0)
    BullInBarLow = ta.valuewhen(BullInBar, low[1], 0)
    TTopH = ta.valuewhen(ttc, math.max(high, high[1]), 0)
    TBotL = ta.valuewhen(tbc, math.min(low, low[1]), 0)

    def addResZone(startIdx, zH, zL):
        tl = line.new(startIdx, zH, bar_index, zH, color=ResColor, width=1)
        bl = line.new(startIdx, zL, bar_index, zL, color=ResColor, width=1)
        linefill.new(tl, bl, color=color.new(ResColor, ZoneAlpha))
        array.push(rTopLines, tl)
        array.push(rBotLines, bl)
        array.push(rZoneHArr, zH)
        array.push(rZoneLArr, zL)
        array.push(rZoneStart, bar_index)
        return array.push(rWasAway, True)

    def addSupZone(startIdx, zH, zL):
        tl = line.new(startIdx, zH, bar_index, zH, color=SupColor, width=1)
        bl = line.new(startIdx, zL, bar_index, zL, color=SupColor, width=1)
        linefill.new(tl, bl, color=color.new(SupColor, ZoneAlpha))
        array.push(sTopLines, tl)
        array.push(sBotLines, bl)
        array.push(sZoneHArr, zH)
        array.push(sZoneLArr, zL)
        array.push(sZoneStart, bar_index)
        return array.push(sWasAway, True)

    if PivotHigh > 0:
        if NoOfPivots == 2 and HighAtPivot < HighAtPivot1 and (HighAtPivot > UpperAtPivot1):
            RZoneH = HighAtPivot1
            RZoneL = UpperAtPivot1
            alertcon = True
            addResZone(IndexOfPivot1, HighAtPivot1, UpperAtPivot1)
        if NoOfPivots == 3 and HighAtPivot < HighAtPivot2 and (HighAtPivot > UpperAtPivot2) and (HighAtPivot1 < HighAtPivot2) and (HighAtPivot1 > UpperAtPivot2):
            RZoneH = HighAtPivot2
            RZoneL = UpperAtPivot2
            alertcon = True
            addResZone(IndexOfPivot2, HighAtPivot2, UpperAtPivot2)
        if NoOfPivots == 4 and HighAtPivot < HighAtPivot3 and (HighAtPivot > UpperAtPivot3) and (HighAtPivot1 < HighAtPivot3) and (HighAtPivot1 > UpperAtPivot3) and (HighAtPivot2 < HighAtPivot3) and (HighAtPivot2 > UpperAtPivot3):
            RZoneH = HighAtPivot3
            RZoneL = UpperAtPivot3
            alertcon = True
            addResZone(IndexOfPivot3, HighAtPivot3, UpperAtPivot3)

    if PivotLow > 0:
        if NoOfPivots == 2 and LowAtPivot > LowAtPivot1 and (LowAtPivot < LowerAtPivotl):
            SZoneH = LowerAtPivotl
            SZoneL = LowAtPivot1
            alertcon = True
            addSupZone(IndexOfPivotl1, LowerAtPivotl, LowAtPivot1)
        if NoOfPivots == 3 and LowAtPivot > LowAtPivot2 and (LowAtPivot < LowerAtPivot2) and (LowAtPivot1 > LowAtPivot2) and (LowAtPivot1 < LowerAtPivot2):
            SZoneH = LowerAtPivot2
            SZoneL = LowAtPivot2
            alertcon = True
            addSupZone(IndexOfPivotl2, LowerAtPivot2, LowAtPivot2)
        if NoOfPivots == 4 and LowAtPivot > LowAtPivot3 and (LowAtPivot < LowerAtPivot3) and (LowAtPivot1 > LowAtPivot3) and (LowAtPivot1 < LowerAtPivot3) and (LowAtPivot2 > LowAtPivot3) and (LowAtPivot2 < LowerAtPivot3):
            SZoneH = LowerAtPivot3
            SZoneL = LowAtPivot3
            alertcon = True
            addSupZone(IndexOfPivotl3, LowerAtPivot3, LowAtPivot3)

    nearResistance: bool = False
    proxAlertRes: bool = False

    if array.size(rTopLines) > 0:
        i = array.size(rTopLines) - 1
        while i >= 0:
            zH = array.get(rZoneHArr, i)
            zL = array.get(rZoneLArr, i)
            startBar = array.get(rZoneStart, i)
            tl = array.get(rTopLines, i)
            bl = array.get(rBotLines, i)
            wasAway = array.get(rWasAway, i)
            isBroken = close > zH
            isExpired = ZoneExpiry > 0 and bar_index - startBar > ZoneExpiry

            if isBroken or isExpired:
                if ShowBroken and isBroken:
                    line.set_color(tl, BrokenColor)
                    line.set_color(bl, BrokenColor)
                array.remove(rTopLines, i)
                array.remove(rBotLines, i)
                array.remove(rZoneHArr, i)
                array.remove(rZoneLArr, i)
                array.remove(rZoneStart, i)
                array.remove(rWasAway, i)
            else:
                line.set_x2(tl, bar_index)
                line.set_x2(bl, bar_index)

                buf = zH * ProximityPct / 100
                if close > zL - buf and close < zH + buf:
                    nearResistance = True
                    proxAlertRes = True

                if close < zL:
                    array.set(rWasAway, i, True)
                if wasAway and close >= zL and (close <= zH) and (bar_index - startBar > 2):
                    if ShowRetest:
                        label.new(bar_index, high, '⟳ R Retest', color=ResColor, textcolor=color.white, style=label.style_label_down, size=size.small)
                    array.set(rWasAway, i, False)
            i -= 1

    nearSupport: bool = False
    proxAlertSup: bool = False

    if array.size(sTopLines) > 0:
        i = array.size(sTopLines) - 1
        while i >= 0:
            zH = array.get(sZoneHArr, i)
            zL = array.get(sZoneLArr, i)
            startBar = array.get(sZoneStart, i)
            tl = array.get(sTopLines, i)
            bl = array.get(sBotLines, i)
            wasAway = array.get(sWasAway, i)
            isBroken = close < zL
            isExpired = ZoneExpiry > 0 and bar_index - startBar > ZoneExpiry

            if isBroken or isExpired:
                if ShowBroken and isBroken:
                    line.set_color(tl, BrokenColor)
                    line.set_color(bl, BrokenColor)
                array.remove(sTopLines, i)
                array.remove(sBotLines, i)
                array.remove(sZoneHArr, i)
                array.remove(sZoneLArr, i)
                array.remove(sZoneStart, i)
                array.remove(sWasAway, i)
            else:
                line.set_x2(tl, bar_index)
                line.set_x2(bl, bar_index)

                buf = zH * ProximityPct / 100
                if close > zL - buf and close < zH + buf:
                    nearSupport = True
                    proxAlertSup = True

                if close > zH:
                    array.set(sWasAway, i, True)
                if wasAway and close <= zH and (close >= zL) and (bar_index - startBar > 2):
                    if ShowRetest:
                        label.new(bar_index, low, '⟳ S Retest', color=SupColor, textcolor=color.white, style=label.style_label_up, size=size.small)
                    array.set(sWasAway, i, False)
            i -= 1

    if ShowPatterns:
        rSize = array.size(rZoneHArr)
        sSize = array.size(sZoneHArr)

        if EvnCan and rSize > 0:
            patOffset1 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, rSize - 1):
                if EvnCanHigh < array.get(rZoneHArr, j) and EvnCanHigh > array.get(rZoneLArr, j):
                    label.new(bar_index[1], high[1] + patOffset1, 'Evening Star', color=color.orange, textcolor=color.white, style=label.style_label_down)
                    break

        if BInBar and rSize > 0:
            patOffset2 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, rSize - 1):
                if BInBarHigh < array.get(rZoneHArr, j) and BInBarHigh > array.get(rZoneLArr, j):
                    label.new(bar_index[1], high[1] + patOffset2, 'Inside Bar', color=color.rgb(224, 67, 5), textcolor=color.white, style=label.style_label_down)
                    break

        if ttc and rSize > 0:
            patOffset3 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, rSize - 1):
                if TTopH < array.get(rZoneHArr, j) and TTopH > array.get(rZoneLArr, j):
                    label.new(bar_index[1], high[1] + patOffset3, 'Tweezer Top', color=color.rgb(255, 0, 208), textcolor=color.white, style=label.style_label_down)
                    break

        if MorCan and sSize > 0:
            patOffset4 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, sSize - 1):
                if MorCanLow < array.get(sZoneHArr, j) and MorCanLow > array.get(sZoneLArr, j):
                    label.new(bar_index[1], low[1] - patOffset4, 'Morning Star', color=color.orange, textcolor=color.white, style=label.style_label_up)
                    break

        if BullInBar and sSize > 0:
            patOffset5 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, sSize - 1):
                if BullInBarLow < array.get(sZoneHArr, j) and BullInBarLow > array.get(sZoneLArr, j):
                    label.new(bar_index[1], low[1] - patOffset5, 'Inside Bar', color=color.rgb(255, 72, 0), textcolor=color.white, style=label.style_label_up)
                    InsideBarAtSupport = True
                    break

        if tbc and sSize > 0:
            patOffset6 = (high[1] - low[1]) * 0.6
            for j in pine_range(0, sSize - 1):
                if TBotL < array.get(sZoneHArr, j) and TBotL > array.get(sZoneLArr, j):
                    label.new(bar_index[1], low[1] - patOffset6, 'Tweezer Bottom', color=color.rgb(255, 0, 208), textcolor=color.white, style=label.style_label_up)
                    break

    plot(PivotHigh, style=plot.style_cross, linewidth=3, color=color.red, offset=-Bars)
    plot(PivotLow, style=plot.style_cross, linewidth=3, color=color.rgb(0, 208, 52), offset=-Bars)

    alertcondition(alertcon, title='New S/R Zone Detected', message='A new Support or Resistance zone has formed')
    alertcondition(proxAlertRes, title='Price Near Resistance', message='Price is approaching a Resistance zone')
    alertcondition(proxAlertSup, title='Price Near Support', message='Price is approaching a Support zone')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
