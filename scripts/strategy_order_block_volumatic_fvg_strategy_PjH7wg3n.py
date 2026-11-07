"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, format, high,
    input, label, low, math, na, nz, open, plot, position, request, script, strategy, string,
    syminfo, ta, table, text, timeframe, volume
)
from pynecore.types import Box, NA, Persistent, Series


@udt
class VolumaticFVG:
    body: Box = na(Box)
    bull: int = na(int)
    bear: int = na(int)
    isBull: bool = na(bool)
    bullBar: Box = na(Box)
    bearBar: Box = na(Box)
    totalVol: float = na(float)
    bornBar: int = na(int)


@script.strategy("Order Block Volumatic FVG Strategy — Mitigation%, Volume & Age + SL/Trailing", overlay=True, max_boxes_count=500, max_bars_back=5000, initial_capital=100, pyramiding=0, calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    mitigationSrc=input.string("high/low", "Mitigation source", options=("close", "high/low")),
    bullGaps=input.bool(True, "Show Bullish FVG"),
    bearGaps=input.bool(True, "Show Bearish FVG"),
    volumeBars=input.bool(True, "Show Volume Bars inside FVG"),
    longThreshold=input.float(5, "Long: Mitigation % (≥)", minval=1, maxval=100, step=0.5),
    shortThreshold=input.float(5, "Short: Mitigation % (≥)", minval=1, maxval=100, step=0.5),
    useVolFilter=input.bool(True, "Filter by TOTAL FVG volume"),
    minVolLong=input.float(1000, "Long: total volume min (0 = off)", step=1),
    maxVolLong=input.float(0, "Long: total volume max (0 = off)", step=1),
    minVolShort=input.float(1000, "Short: total volume min (0 = off)", step=1),
    maxVolShort=input.float(0, "Short: total volume max (0 = off)", step=1),
    useShareFilter=input.bool(True, "Filter by Bull% / Bear% share"),
    longBullShareMin=input.float(70, "Long: Bull% min (≥)", minval=0, maxval=100, step=0.1),
    longBearShareMax=input.float(100, "Long: Bear% max (≤)", minval=0, maxval=100, step=0.1),
    shortBearShareMin=input.float(70, "Short: Bear% min (≥)", minval=0, maxval=100, step=0.1),
    shortBullShareMax=input.float(100, "Short: Bull% max (≤)", minval=0, maxval=100, step=0.1),
    useAgeFilter=input.bool(True, "Use AGE filter (bars since created)"),
    minAgeLong=input.int(40, "Long: min age (bars)", minval=0),
    minAgeShort=input.int(40, "Short: min age (bars)", minval=0),
    confirmCandle=input.bool(False, "Require candle in trade direction"),
    cooldownBars=input.int(0, "Cooldown after an entry (bars)", minval=0),
    slPercent=input.float(30, "Stop Loss %", minval=0.1, step=0.1),
    trailTriggerPct=input.float(1.5, "Activate trailing at +% profit", minval=0.1, step=0.1),
    trailDistPct=input.float(1.5, "Trailing distance (%)", minval=0.1, step=0.1),
    useAutoLTF=input.bool(False, "Auto Lower TF (TF/Divisor → 1/3/5m)"),
    ltfDivisor=input.int(10, "Divisor for Auto LTF", minval=2, maxval=60),
    ltfFixed=input.string("3", "Fixed Lower TF (minutes)", options=("1", "3", "5", "15")),
    bullColor=input.color(color.rgb(26, 194, 216, 50), "Bullish color"),
    bearColor=input.color(color.rgb(216, 118, 26, 50), "Bearish color")
):
    fvgs: Persistent[list[VolumaticFVG]] = array.new(0, NA(VolumaticFVG))
    dash: Persistent = table.new(position.top_right, 100, 100, chart.bg_color)

    diff: float = (low - high[2]) / low * 100 if close[1] > open[1] else (low[2] - high) / high * 100
    sizeFVG: float = diff / ta.percentile_nearest_rank(diff, 1000, 100) * 100
    filterFVG: bool = sizeFVG > 10
    isBull_gap: bool = high[2] < low and high[2] < high[1] and (low[2] < low) and filterFVG
    isBear_gap: bool = low[2] > high and low[2] > low[1] and (high[2] > high) and filterFVG

    def f_pick_ltf_str(_useAuto, _div, _tfMinutes):
        out: str = ltfFixed
        if _useAuto:
            target: float = math.max(1.0, math.ceil(_tfMinutes / _div))
            out = '5' if target >= 5 else '3' if target >= 3 else '1'
        return out

    tfMin: float = timeframe.in_seconds('') / 60.0
    tfLtf: str = f_pick_ltf_str(useAutoLTF, ltfDivisor, tfMin)

    bullArr: Series[list[float]] = request.security_lower_tf(syminfo.tickerid, tfLtf, volume if close > close[1] else 0)
    bearArr: Series[list[float]] = request.security_lower_tf(syminfo.tickerid, tfLtf, volume if close < close[1] else 0)

    bullNow: float = nz(array.sum(bullArr), 0)
    bearNow: float = nz(array.sum(bearArr), 0)
    bullPrev: float = nz(inline_series(array.sum(bullArr), 1), bullNow)
    bearPrev: float = nz(inline_series(array.sum(bearArr), 1), bearNow)
    totPrev: float = bullPrev + bearPrev

    if totPrev <= 0:
        tfVol: float = nz(volume[1], volume)
        hlRange: float = math.max(1e-10, high[1] - low[1])
        share: float = (close[1] - low[1]) / hlRange
        share = math.max(0.0, math.min(1.0, share))
        bullPrev = tfVol * share
        bearPrev = tfVol - bullPrev
        totPrev = tfVol

    def f_mitigation_pct(_isBull, _top, _bot):
        top: float = math.max(_top, _bot)
        bot: float = math.min(_top, _bot)
        height: float = math.max(1e-10, top - bot)
        src: float = close if mitigationSrc == 'close' else low if _isBull else high
        pct: float = 0.0
        if _isBull:
            pct = 0 if src >= top else 100 if src <= bot else (top - src) / height * 100
        else:
            pct = 0 if src <= bot else 100 if src >= top else (src - bot) / height * 100
        pct = math.max(0, math.min(100, pct))
        return pct

    def f_bar_intersects_box(_top, _bot):
        top: float = math.max(_top, _bot)
        bot: float = math.min(_top, _bot)
        return high >= bot and low <= top

    if bar_index > 100:
        if isBull_gap and bullGaps:
            body__0000006b__: Box = box.new(bar_index - 1, low, bar_index + 5, high[2], bgcolor=color.new(bullColor, 70), border_color=na)
            mid: float = math.avg(low, high[2])
            bullPct: float = bullPrev / totPrev * 100 if totPrev > 0 else 50
            bearPct: float = 100 - bullPct
            bearBar__0000006b__: Box = box.new(box.get_left(body__0000006b__), box.get_top(body__0000006b__), box.get_left(body__0000006b__), mid, bgcolor=bearColor, border_color=chart.bg_color)
            bullBar__0000006b__: Box = box.new(box.get_left(body__0000006b__), mid, box.get_left(body__0000006b__), box.get_bottom(body__0000006b__), bgcolor=bullColor, border_color=chart.bg_color)
            array.push(fvgs, VolumaticFVG(body__0000006b__, cast_int(math.round(bullPct)), cast_int(math.round(bearPct)), True, bullBar__0000006b__, bearBar__0000006b__, totPrev, bar_index))

        if isBear_gap and bearGaps:
            body__0000007d__: Box = box.new(bar_index - 1, low[2], bar_index + 5, high, bgcolor=color.new(bearColor, 70), border_color=na)
            mid: float = math.avg(low[2], high)
            bullPct: float = bullPrev / totPrev * 100 if totPrev > 0 else 50
            bearPct: float = 100 - bullPct
            bearBar__0000007d__: Box = box.new(box.get_left(body__0000007d__), box.get_top(body__0000007d__), box.get_left(body__0000007d__), mid, bgcolor=bearColor, border_color=chart.bg_color)
            bullBar__0000007d__: Box = box.new(box.get_left(body__0000007d__), mid, box.get_left(body__0000007d__), box.get_bottom(body__0000007d__), bgcolor=bullColor, border_color=chart.bg_color)
            array.push(fvgs, VolumaticFVG(body__0000007d__, cast_int(math.round(bullPct)), cast_int(math.round(bearPct)), False, bullBar__0000007d__, bearBar__0000007d__, totPrev, bar_index))

        if array.size(fvgs) > 0:
            for k in pine_range(array.size(fvgs) - 1, 0):
                fvg: VolumaticFVG = array.get(fvgs, k)
                src1: float = close if mitigationSrc == 'close' else low
                src2: float = close if mitigationSrc == 'close' else high
                crossed: bool = src1 < box.get_bottom(fvg.body) if fvg.isBull else src2 > box.get_top(fvg.body)
                if crossed:
                    box.delete(fvg.body)
                    box.delete(fvg.bullBar)
                    box.delete(fvg.bearBar)
                    array.remove(fvgs, k)
                else:
                    box.set_right(fvg.body, bar_index + 25)
                    box.set_text(fvg.body, string.tostring(nz(fvg.totalVol, 0), format.volume))
                    box.set_text_halign(fvg.body, text.align_right)
                    box.set_text_color(fvg.body, chart.bg_color)
                    if volumeBars:
                        leftI: int = box.get_left(fvg.body)
                        rightI = box.get_right(fvg.body)
                        sz: int = cast_int(rightI - leftI) / 200
                        box.set_right(fvg.bullBar, leftI + sz * fvg.bull)
                        box.set_right(fvg.bearBar, leftI + sz * fvg.bear)
                        box.set_text(fvg.bullBar, string.tostring(cast_int(fvg.bull), format.percent))
                        box.set_text(fvg.bearBar, string.tostring(cast_int(fvg.bear), format.percent))
                        box.set_text_color(fvg.bullBar, chart.fg_color)
                        box.set_text_color(fvg.bearBar, chart.fg_color)
                        box.set_text_halign(fvg.bullBar, text.align_right)
                        box.set_text_halign(fvg.bearBar, text.align_right)
                    else:
                        box.set_text(fvg.bearBar, '')
                        box.set_text(fvg.bullBar, '')

        if array.size(fvgs) > 0:
            for i in pine_range(array.size(fvgs) - 1, 0):
                fvg: VolumaticFVG = array.get(fvgs, i)
                topi: float = box.get_top(fvg.body)
                boti: float = box.get_bottom(fvg.body)
                removed: bool = False
                __loop_3__ = pine_loop(0)
                while __loop_3__.step(array.size(fvgs) - 1):
                    j = __loop_3__.value
                    if i == j:
                        continue
                    l: VolumaticFVG = array.get(fvgs, j)
                    top1: float = box.get_top(l.body)
                    bot1: float = box.get_bottom(l.body)
                    if top1 < topi and top1 > boti:
                        box.delete(fvg.body)
                        box.delete(fvg.bearBar)
                        box.delete(fvg.bullBar)
                        array.remove(fvgs, i)
                        removed = True
                        break
                if removed:
                    continue

        if array.size(fvgs) > 10:
            old: VolumaticFVG = array.shift(fvgs)
            box.delete(old.body)
            box.delete(old.bullBar)
            box.delete(old.bearBar)

        if barstate.islast:
            bullCount: int = 0
            bearCount: int = 0
            bullVolume: float = 0.0
            bearVolume: float = 0.0
            if array.size(fvgs) > 0:
                for fvg in fvgs:
                    if fvg.isBull:
                        bullCount += 1
                        bullVolume += nz(fvg.totalVol, 0)
                    else:
                        bearCount += 1
                        bearVolume += nz(fvg.totalVol, 0)
            method_call('cell', dash, 0, 0, 'FVG Type', text_color=chart.fg_color)
            method_call('cell', dash, 1, 0, 'On Chart', text_color=chart.fg_color)
            method_call('cell', dash, 2, 0, 'Total Volume', text_color=chart.fg_color)
            method_call('cell', dash, 0, 1, 'Bullish FVG', text_color=color.new(bullColor, 0))
            method_call('cell', dash, 1, 1, string.tostring(bullCount), text_color=chart.fg_color)
            method_call('cell', dash, 2, 1, string.tostring(bullVolume, format.volume), text_color=chart.fg_color)
            method_call('cell', dash, 0, 2, 'Bearish FVG', text_color=color.new(bearColor, 0))
            method_call('cell', dash, 1, 2, string.tostring(bearCount), text_color=chart.fg_color)
            method_call('cell', dash, 2, 2, string.tostring(bearVolume, format.volume), text_color=chart.fg_color)

    bestBullIdx: int = na(int)
    bestBearIdx: int = na(int)
    bestBullLeft: float = na(float)
    bestBearLeft: float = na(float)
    bullMit: float = na(float)
    bearMit: float = na(float)

    if array.size(fvgs) > 0:
        for i in pine_range(0, array.size(fvgs) - 1):
            f: VolumaticFVG = array.get(fvgs, i)
            top: float = box.get_top(f.body)
            bot: float = box.get_bottom(f.body)
            if f_bar_intersects_box(top, bot):
                m: float = f_mitigation_pct(f.isBull, top, bot)
                ageBars: int = bar_index - f.bornBar

                if f.isBull:
                    ok: bool = m >= longThreshold
                    if confirmCandle:
                        ok = ok and close > open
                    if useVolFilter:
                        volOK: bool = f.totalVol >= minVolLong and (maxVolLong == 0 or f.totalVol <= maxVolLong)
                        ok = ok and volOK
                    if useAgeFilter:
                        ok = ok and ageBars >= minAgeLong
                    if useShareFilter:
                        ok = ok and f.bull >= longBullShareMin and (f.bear <= longBearShareMax)
                    if ok:
                        leftI: int = box.get_left(f.body)
                        if na(bestBullIdx) or leftI > bestBullLeft:
                            bestBullIdx = i
                            bestBullLeft = leftI
                            bullMit = m
                else:
                    ok: bool = m >= shortThreshold
                    if confirmCandle:
                        ok = ok and close < open
                    if useVolFilter:
                        volOK: bool = f.totalVol >= minVolShort and (maxVolShort == 0 or f.totalVol <= maxVolShort)
                        ok = ok and volOK
                    if useAgeFilter:
                        ok = ok and ageBars >= minAgeShort
                    if useShareFilter:
                        ok = ok and f.bear >= shortBearShareMin and (f.bull <= shortBullShareMax)
                    if ok:
                        leftI: int = box.get_left(f.body)
                        if na(bestBearIdx) or leftI > bestBearLeft:
                            bestBearIdx = i
                            bestBearLeft = leftI
                            bearMit = m

    lastBullLeftTraded: Persistent[int] = na(int)
    lastBearLeftTraded: Persistent[int] = na(int)
    lastEntryBar: Persistent[int] = na(int)

    canEnter: bool = na(lastEntryBar) or bar_index - lastEntryBar >= cooldownBars
    flat: bool = strategy.position_size == 0

    if not na(bestBullIdx) and flat and canEnter:
        fB: VolumaticFVG = array.get(fvgs, bestBullIdx)
        leftB: int = box.get_left(fB.body)
        if na(lastBullLeftTraded) or leftB != lastBullLeftTraded:
            strategy.entry('Long', strategy.long)
            lastBullLeftTraded = leftB
            lastEntryBar = bar_index
            label.new(bar_index, low, 'Long  mit:' + string.tostring(bullMit, format.percent) + '  V:' + string.tostring(nz(fB.totalVol, 0), format.volume) + '  Bull%:' + string.tostring(fB.bull) + ' Bear%:' + string.tostring(fB.bear), style=label.style_label_up, color=color.new(color.teal, 0), textcolor=color.black)

    if not na(bestBearIdx) and flat and canEnter:
        fS: VolumaticFVG = array.get(fvgs, bestBearIdx)
        leftS: int = box.get_left(fS.body)
        if na(lastBearLeftTraded) or leftS != lastBearLeftTraded:
            strategy.entry('Short', strategy.short)
            lastBearLeftTraded = leftS
            lastEntryBar = bar_index
            label.new(bar_index, high, 'Short mit:' + string.tostring(bearMit, format.percent) + '  V:' + string.tostring(nz(fS.totalVol, 0), format.volume) + '  Bull%:' + string.tostring(fS.bull) + ' Bear%:' + string.tostring(fS.bear), style=label.style_label_down, color=color.new(color.orange, 0), textcolor=color.black)

    longTrailActive: Persistent[bool] = False
    shortTrailActive: Persistent[bool] = False
    if strategy.position_size == 0:
        longTrailActive = False
        shortTrailActive = False

    avgPrice: float = strategy.position_avg_price

    if strategy.position_size > 0:
        longStop: float = avgPrice * (1 - slPercent / 100)
        longTrigger: float = avgPrice * (1 + trailTriggerPct / 100)
        if not longTrailActive and high >= longTrigger:
            longTrailActive = True
        longTrailPts: float = avgPrice * (trailDistPct / 100) if longTrailActive else na
        strategy.exit('XL', from_entry='Long', stop=longStop, trail_points=longTrailPts)

    if strategy.position_size < 0:
        shortStop: float = avgPrice * (1 + slPercent / 100)
        shortTrigger: float = avgPrice * (1 - trailTriggerPct / 100)
        if not shortTrailActive and low <= shortTrigger:
            shortTrailActive = True
        shortTrailPts: float = avgPrice * (trailDistPct / 100) if shortTrailActive else na
        strategy.exit('XS', from_entry='Short', stop=shortStop, trail_points=shortTrailPts)

    plot(bullMit, 'Candidate Bull mitigation (%)', color=color.teal)
    plot(bearMit, 'Candidate Bear mitigation (%)', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
