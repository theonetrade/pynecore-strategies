"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, box,
    close, color, dayofweek, high, hlc3, hour, input, label, line, low, math, minute, na, open,
    plot, position, request, script, size, strategy, string, syminfo, ta, table, time, timeframe,
    timenow, volume, xloc
)
from pynecore.types import Label, Line, NA, Persistent, Series, Table


@udt
class lvl_group:
    level: float = na(float)
    txt: str = na(str)
    x: int = na(int)


grp1: str = "Two-Bar Setup"
grp2: str = "VWAP Trend Filter"
grp3: str = "Volume"
grp6: str = "Display"
g_SETTINGS: str = "ICT Settings"
g_VISUALS: str = "ICT Visual Settings"
g_LABELS: str = "ICT Label Settings"
g_DAYOPEN: str = "True Day Open (6 PM)"
g_WEEKLEVELS: str = "Previous Week Levels"
g_DAYLEVELS: str = "Previous Day Levels"
g_SESSIONS: str = "Session Levels"


@script.strategy("Two-Bar Fib Retrace Strategy [Futures]", overlay=True, max_labels_count=500, max_lines_count=500, default_qty_type=strategy.fixed, default_qty_value=1, initial_capital=100000, commission_type=strategy.commission.cash_per_contract, commission_value=2.5, slippage=1)
def main(
    bodyPctMin=input.float(0.5, "Min Body % of Range", minval=0.3, maxval=1.0, step=0.05, group=grp1),
    slOffset=input.float(1.0, "SL Offset Beyond Bar 2 Wick (points)", minval=0.25, step=0.25, group=grp1),
    showSL=input.bool(True, "Show SL Line", group=grp1),
    showZone=input.bool(True, "Show 50-61.8% Retrace Zone", group=grp1),
    useVWAP=input.bool(True, "Enable VWAP Trend Filter", group=grp2),
    showVWAP=input.bool(True, "Show VWAP Line", group=grp2),
    volMaLen=input.int(20, "Volume MA Length", group=grp3),
    atrLen=input.int(14, "ATR Length", group=grp3),
    showLabels=input.bool(True, "Show Signal Labels", group=grp6),
    showDashboard=input.bool(True, "Show Dashboard", group=grp6),
    bullCol=input.color(color.new(color.new('#00E676'), 0), "Bull Color", group=grp6),
    bearCol=input.color(color.new(color.new('#FF1744'), 0), "Bear Color", group=grp6),
    lookbackSetting=input.string("1 Week", "Lookback Period", options=("1 Day", "1 Week", "1 Month", "Max"), group=g_SETTINGS),
    tf_limit=input.timeframe("30", "Timeframe Limit", tooltip="Drawings will not appear on timeframes >= this", group=g_SETTINGS),
    level_line_color=input.color(color.black, "Level Line Color", group=g_VISUALS),
    label_color=input.color(color.black, "Label Color", group=g_VISUALS),
    label_size_str=input.string("Small", "Label Size", options=("Tiny", "Small", "Normal", "Large"), group=g_LABELS),
    show_ict_labels=input.bool(True, "Show Labels", group=g_LABELS),
    show_levels=input.bool(True, "Show Session High/Low Levels", group=g_LABELS),
    show_mitigated=input.bool(False, "Show Mitigated Levels", group=g_LABELS),
    combine_labels=input.bool(True, "Combine Overlapping Labels", group=g_LABELS),
    show_dayopen=input.bool(True, "Show True Day Open Line", group=g_DAYOPEN),
    dayopen_color=input.color(color.black, "True Day Open Color", group=g_DAYOPEN),
    show_weeklevels=input.bool(True, "Show Prev Week High/Low", group=g_WEEKLEVELS),
    weeklevels_color=input.color(color.black, "Prev Week Color", group=g_WEEKLEVELS),
    weeklevels_style_str=input.string("Dotted", "Prev Week Style", options=("Solid", "Dashed", "Dotted"), group=g_WEEKLEVELS),
    show_pdlevels=input.bool(True, "Show Previous Day H/L", group=g_DAYLEVELS),
    show_wed_levels=input.bool(False, "Show Wednesday Levels", group=g_DAYLEVELS),
    show_tue_levels=input.bool(False, "Show Tuesday Levels", group=g_DAYLEVELS),
    show_mon_levels=input.bool(False, "Show Monday Levels", group=g_DAYLEVELS),
    daylevels_color=input.color(color.black, "Day Levels Color", group=g_DAYLEVELS),
    daylevels_style_str=input.string("Dotted", "Day Levels Style", options=("Solid", "Dashed", "Dotted"), group=g_DAYLEVELS),
    use_asia=input.bool(True, "Asia (8pm-12am ET)", group=g_SESSIONS),
    use_london=input.bool(True, "London (2am-5am ET)", group=g_SESSIONS),
    use_nyam=input.bool(True, "NY AM (8:30am-11:30am ET)", group=g_SESSIONS),
    use_nylu=input.bool(True, "NY Lunch (12pm-1pm ET)", group=g_SESSIONS),
    use_nypm=input.bool(True, "NY PM (1:30pm-6pm ET)", group=g_SESSIONS)
):
    __block_result__ = na
    __switch__ = lookbackSetting
    if __switch__ == "1 Day":
        __block_result__ = 86400000
    elif __switch__ == "1 Week":
        __block_result__ = 604800000
    elif __switch__ == "1 Month":
        __block_result__ = 2592000000
    else:
        __block_result__ = 0
    lookback_ms = __block_result__
    inLookback = lookbackSetting == 'Max' or time >= timenow - lookback_ms

    label_bg_transp: Persistent[int] = 100

    __block_result_1__ = na
    __switch__ = label_size_str
    if __switch__ == "Tiny":
        __block_result_1__ = size.tiny
    elif __switch__ == "Small":
        __block_result_1__ = size.small
    elif __switch__ == "Large":
        __block_result_1__ = size.large
    else:
        __block_result_1__ = size.normal
    label_size_setting = __block_result_1__

    __block_result_2__ = na
    __switch__ = weeklevels_style_str
    if __switch__ == "Solid":
        __block_result_2__ = line.style_solid
    elif __switch__ == "Dashed":
        __block_result_2__ = line.style_dashed
    else:
        __block_result_2__ = line.style_dotted
    weeklevels_style_lookup = __block_result_2__

    __block_result_3__ = na
    __switch__ = daylevels_style_str
    if __switch__ == "Solid":
        __block_result_3__ = line.style_solid
    elif __switch__ == "Dashed":
        __block_result_3__ = line.style_dashed
    else:
        __block_result_3__ = line.style_dotted
    daylevels_style_lookup = __block_result_3__

    asia_high_text: str = "ASIA.H"
    asia_low_text: str = "ASIA.L"
    london_high_text: str = "LON.H"
    london_low_text: str = "LON.L"
    nyam_high_text: str = "NYAM.H"
    nyam_low_text: str = "NYAM.L"
    nylu_high_text: str = "NYLU.H"
    nylu_low_text: str = "NYLU.L"
    nypm_high_text: str = "NYPM.H"
    nypm_low_text: str = "NYPM.L"

    gmt_tz: str = "America/New_York"

    atr = ta.atr(atrLen)
    volMA = ta.sma(volume, volMaLen)
    vwap = ta.vwap(hlc3)

    aboveVWAP = close > vwap
    belowVWAP = close < vwap
    trendBull = aboveVWAP if useVWAP else True
    trendBear = belowVWAP if useVWAP else True

    b1o = open[2]
    b1c = close[2]
    b1h = high[2]
    b1l = low[2]
    b1range = b1h - b1l
    b1body = math.abs(b1c - b1o)
    b1bodyPct = b1body / b1range if b1range != 0 else 0.0
    b1bull = b1c > b1o
    b1bear = b1c < b1o
    b1full = b1bodyPct >= bodyPctMin

    b2o = open[1]
    b2c = close[1]
    b2h = high[1]
    b2l = low[1]
    b2range = b2h - b2l
    b2body = math.abs(b2c - b2o)
    b2bodyPct = b2body / b2range if b2range != 0 else 0.0
    b2bull = b2c > b2o
    b2bear = b2c < b2o
    b2full = b2bodyPct >= bodyPctMin

    volConfirm = volume[1] > volume[2]

    impulseBullSame = b1bull and b2bull and b1full and b2full and volConfirm
    impulseBearSame = b1bear and b2bear and b1full and b2full and volConfirm
    impulseBullMixed = not (b1bull and b2bull) and b2c > b1h and b1full and b2full and volConfirm
    impulseBearMixed = not (b1bear and b2bear) and b2c < b1l and b1full and b2full and volConfirm

    impulseBull: Series = (impulseBullSame or impulseBullMixed) and trendBull
    impulseBear: Series = (impulseBearSame or impulseBearMixed) and trendBear

    bull_zone_top = b2h - b2range * 0.5
    bull_zone_bot = b2h - b2range * 0.618
    bear_zone_top = b2l + b2range * 0.618
    bear_zone_bot = b2l + b2range * 0.5

    bullWickInZone = low <= bull_zone_top and low >= bull_zone_bot
    bearWickInZone = high >= bear_zone_bot and high <= bear_zone_top

    bullSignal = impulseBull and bullWickInZone
    bearSignal = impulseBear and bearWickInZone

    sl_bull = b2l - slOffset
    sl_bear = b2h + slOffset

    if bullSignal:
        strategy.entry('Long', strategy.long, qty=1)
        strategy.exit('L-SL', from_entry='Long', stop=sl_bull)

    if bearSignal:
        strategy.entry('Short', strategy.short, qty=1)
        strategy.exit('S-SL', from_entry='Short', stop=sl_bear)

    if showZone and impulseBull and (not impulseBull[1]):
        box.new(bar_index - 1, bull_zone_top, bar_index + 8, bull_zone_bot, border_color=color.new(bullCol, 20), bgcolor=color.new(bullCol, 85), text='50-61.8%', text_color=bullCol, text_size=size.tiny)

    if showZone and impulseBear and (not impulseBear[1]):
        box.new(bar_index - 1, bear_zone_top, bar_index + 8, bear_zone_bot, border_color=color.new(bearCol, 20), bgcolor=color.new(bearCol, 85), text='50-61.8%', text_color=bearCol, text_size=size.tiny)

    if bullSignal and showSL:
        line.new(bar_index, sl_bull, bar_index + 10, sl_bull, color=color.new(bearCol, 20), width=2, style=line.style_dashed)

    if bearSignal and showSL:
        line.new(bar_index, sl_bear, bar_index + 10, sl_bear, color=color.new(bullCol, 20), width=2, style=line.style_dashed)

    impulseType = ' [Match]' if impulseBullSame or impulseBearSame else ' [Mixed]'

    if bullSignal and showLabels:
        label.new(bar_index, low - atr * 0.4, '▲ LONG' + impulseType + '\nSL: ' + string.tostring(math.round(sl_bull, 2)) + '\nVWAP: ' + string.tostring(math.round(vwap, 2)), style=label.style_label_up, color=color.new(bullCol, 10), textcolor=color.white, size=size.small)

    if bearSignal and showLabels:
        label.new(bar_index, high + atr * 0.4, '▼ SHORT' + impulseType + '\nSL: ' + string.tostring(math.round(sl_bear, 2)) + '\nVWAP: ' + string.tostring(math.round(vwap, 2)), style=label.style_label_down, color=color.new(bearCol, 10), textcolor=color.white, size=size.small)

    barcolor(bullCol if bullSignal else bearCol if bearSignal else na)

    plot(vwap if showVWAP else na, 'VWAP', color=color.new(color.aqua, 0), linewidth=2)

    high_lines: Persistent[list[Line]] = array.new_line()
    low_lines: Persistent[list[Line]] = array.new_line()
    high_levels: Persistent[list[float]] = array.new_float()
    low_levels: Persistent[list[float]] = array.new_float()
    high_labels: Persistent[list[Label]] = array.new_label()
    low_labels: Persistent[list[Label]] = array.new_label()
    high_texts: Persistent[list[str]] = array.new_string()
    low_texts: Persistent[list[str]] = array.new_string()
    mitigated_hi_labels: Persistent[list[Label]] = array.new_label()
    mitigated_lo_labels: Persistent[list[Label]] = array.new_label()
    combined_labels_arr: Persistent[list[Label]] = array.new_label()
    used_label_x: Persistent[list[int]] = array.new_int()
    used_label_y: Persistent[list[float]] = array.new_float()

    _groups: Persistent[list[lvl_group]] = array.new(0, NA(lvl_group))

    def add_group(price: float, token: str, xloc_idx: int):
        tick_idx: int = cast_int(math.round(price / syminfo.mintick))
        found: int = -1
        if array.size(_groups) > 0:
            for gi in pine_range(0, array.size(_groups) - 1):
                g = array.get(_groups, gi)
                if cast_int(math.round(g.level / syminfo.mintick)) == tick_idx:
                    found = gi
                    break
        __block_result_4__ = na
        if found >= 0:
            g = array.get(_groups, found)
            has: bool = g.txt == token or string.contains(g.txt, token + ' +') or string.contains(g.txt, '+ ' + token)
            g.txt = g.txt if has else g.txt + ' + ' + token
            g.x = math.min(g.x, xloc_idx)
            __block_result_4__ = array.set(_groups, found, g)
        else:
            __block_result_4__ = array.push(_groups, lvl_group(tick_idx * syminfo.mintick, token, xloc_idx))
        return __block_result_4__

    def drawSessionLevels(level_price: float, level_idx: int, level_text: str, is_high: bool):
        __block_result_5__ = na
        if not na(level_price) and (not na(level_idx)):
            dx: int = math.max(0, bar_index - level_idx)
            dx_c: int = math.min(dx, 10000)
            x1_time: int = time if na(time[dx_c]) else time[dx_c]
            line_id = line.new(x1_time, level_price, time, level_price, xloc=xloc.bar_time, color=level_line_color, style=line.style_solid)
            label_id = label.new(x1_time, level_price, level_text, xloc=xloc.bar_time, color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_down if is_high else label.style_label_up, size=label_size_setting)
            __block_result_6__ = na
            if is_high:
                array.push(high_lines, line_id)
                array.push(high_levels, level_price)
                array.push(high_labels, label_id)
                __block_result_6__ = array.push(high_texts, level_text)
            else:
                array.push(low_lines, line_id)
                array.push(low_levels, level_price)
                array.push(low_labels, label_id)
                __block_result_6__ = array.push(low_texts, level_text)
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    def updateLines():
        enforce: bool = lookbackSetting != 'Max'
        cutoff: int = timenow - lookback_ms

        if array.size(high_lines) > 0:
            for i in pine_range(array.size(high_lines) - 1, 0):
                ln = array.get(high_lines, i)
                level = array.get(high_levels, i)
                lbl = array.get(high_labels, i) if array.size(high_labels) > i else na
                txt = array.get(high_texts, i) if array.size(high_texts) > i else 'LEVEL'

                if enforce and line.get_x1(ln) < cutoff:
                    line.delete(ln)
                    if not na(lbl):
                        label.delete(lbl)
                    array.remove(high_lines, i)
                    array.remove(high_levels, i)
                    if array.size(high_labels) > i:
                        array.remove(high_labels, i)
                    if array.size(high_texts) > i:
                        array.remove(high_texts, i)
                elif high > level:
                    if not show_mitigated:
                        line.delete(ln)
                        if not na(lbl):
                            label.delete(lbl)
                        array.remove(high_lines, i)
                        array.remove(high_levels, i)
                        if array.size(high_labels) > i:
                            array.remove(high_labels, i)
                        if array.size(high_texts) > i:
                            array.remove(high_texts, i)
                    else:
                        line.set_x2(ln, bar_index)
                        x1t: int = line.get_x1(ln)
                        dxm: int = math.min(math.max(0, bar_index - x1t), 10000)
                        xtm: int = time if na(time[dxm]) else time[dxm]
                        if not na(lbl):
                            label.delete(lbl)
                        new_lbl = label.new(xtm, level, txt, xloc=xloc.bar_time, color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_right, size=label_size_setting)
                        array.push(mitigated_hi_labels, new_lbl)
                        array.remove(high_lines, i)
                        array.remove(high_levels, i)
                        if array.size(high_labels) > i:
                            array.remove(high_labels, i)
                        if array.size(high_texts) > i:
                            array.remove(high_texts, i)
                else:
                    line.set_x2(ln, time)
                    if not combine_labels and (not na(lbl)):
                        label.set_x(lbl, time)
                        label.set_y(lbl, level)
                        label.set_style(lbl, label.style_label_left)

        __block_result_7__ = na
        if array.size(low_lines) > 0:
            __block_result_8__ = na
            for i in pine_range(array.size(low_lines) - 1, 0):
                ln = array.get(low_lines, i)
                level = array.get(low_levels, i)
                lbl = array.get(low_labels, i) if array.size(low_labels) > i else na
                txt = array.get(low_texts, i) if array.size(low_texts) > i else 'LEVEL'

                __block_result_9__ = na
                if enforce and line.get_x1(ln) < cutoff:
                    line.delete(ln)
                    if not na(lbl):
                        label.delete(lbl)
                    array.remove(low_lines, i)
                    array.remove(low_levels, i)
                    if array.size(low_labels) > i:
                        array.remove(low_labels, i)
                    if array.size(low_texts) > i:
                        array.remove(low_texts, i)
                    __block_result_9__ = NA(Label)
                elif low < level:
                    __block_result_10__ = na
                    if not show_mitigated:
                        line.delete(ln)
                        if not na(lbl):
                            label.delete(lbl)
                        array.remove(low_lines, i)
                        array.remove(low_levels, i)
                        if array.size(low_labels) > i:
                            array.remove(low_labels, i)
                        if array.size(low_texts) > i:
                            array.remove(low_texts, i)
                        __block_result_10__ = NA(Label)
                    else:
                        line.set_x2(ln, bar_index)
                        x1t: int = line.get_x1(ln)
                        dxm: int = math.min(math.max(0, bar_index - x1t), 10000)
                        xtm: int = time if na(time[dxm]) else time[dxm]
                        if not na(lbl):
                            label.delete(lbl)
                        new_lbl = label.new(xtm, level, txt, xloc=xloc.bar_time, color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_right, size=label_size_setting)
                        array.push(mitigated_lo_labels, new_lbl)
                        array.remove(low_lines, i)
                        array.remove(low_levels, i)
                        if array.size(low_labels) > i:
                            array.remove(low_labels, i)
                        if array.size(low_texts) > i:
                            array.remove(low_texts, i)
                        __block_result_10__ = NA(Label)
                    __block_result_9__ = __block_result_10__
                else:
                    line.set_x2(ln, time)
                    if not combine_labels and (not na(lbl)):
                        label.set_x(lbl, time)
                        label.set_y(lbl, level)
                        label.set_style(lbl, label.style_label_left)
                    __block_result_9__ = NA(Label)
                __block_result_8__ = __block_result_9__
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    def updateSessionLevels(curr_high: float, curr_low: float, curr_hi_idx: int, curr_lo_idx: int, in_session: bool):
        new_high: float = curr_high
        new_low: float = curr_low
        new_hi_idx: int = curr_hi_idx
        new_lo_idx: int = curr_lo_idx
        if in_session:
            if na(curr_high) or high > curr_high:
                new_high = high
                new_hi_idx = bar_index
            if na(curr_low) or low < curr_low:
                new_low = low
                new_lo_idx = bar_index
        return (new_high, new_low, new_hi_idx, new_lo_idx)

    asia_high: Persistent[float] = na(float)
    asia_low: Persistent[float] = na(float)
    asia_hi_idx: Persistent[int] = na(int)
    asia_lo_idx: Persistent[int] = na(int)

    lon_high: Persistent[float] = na(float)
    lon_low: Persistent[float] = na(float)
    lon_hi_idx: Persistent[int] = na(int)
    lon_lo_idx: Persistent[int] = na(int)

    nyam_high: Persistent[float] = na(float)
    nyam_low: Persistent[float] = na(float)
    nyam_hi_idx: Persistent[int] = na(int)
    nyam_lo_idx: Persistent[int] = na(int)

    nylu_high: Persistent[float] = na(float)
    nylu_low: Persistent[float] = na(float)
    nylu_hi_idx: Persistent[int] = na(int)
    nylu_lo_idx: Persistent[int] = na(int)

    nypm_high: Persistent[float] = na(float)
    nypm_low: Persistent[float] = na(float)
    nypm_hi_idx: Persistent[int] = na(int)
    nypm_lo_idx: Persistent[int] = na(int)

    dayopen_price: Persistent[float] = na(float)
    dayopen_line: Persistent[Line] = na(Line)
    dayopen_label_obj: Persistent[Label] = na(Label)

    is_dayopen = hour(time, gmt_tz) == 18 and minute(time, gmt_tz) == 0

    if is_dayopen:
        dayopen_price = open
        if not na(dayopen_line):
            line.delete(dayopen_line)
        if not na(dayopen_label_obj):
            label.delete(dayopen_label_obj)
        if show_dayopen and timeframe.in_seconds('') <= timeframe.in_seconds(tf_limit):
            dayopen_line = line.new(bar_index, dayopen_price, bar_index + 1, dayopen_price, color=dayopen_color, style=line.style_dotted)

    if not na(dayopen_line) and (not na(dayopen_price)):
        line.set_x2(dayopen_line, bar_index)
        if not na(dayopen_label_obj):
            label.delete(dayopen_label_obj)
        if not combine_labels:
            dayopen_label_obj = label.new(bar_index, dayopen_price, 'True Day Open', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    prev_week_high, prev_week_low = request.security(syminfo.tickerid, 'W', (high, low), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    week_high: Persistent[float] = na(float)
    week_low: Persistent[float] = na(float)
    week_hi_line: Persistent[Line] = na(Line)
    week_lo_line: Persistent[Line] = na(Line)
    week_hi_label: Persistent[Label] = na(Label)
    week_lo_label: Persistent[Label] = na(Label)

    is_newweek = dayofweek == dayofweek.monday and hour(time, gmt_tz) == 0 and (minute(time, gmt_tz) == 0)

    if is_newweek:
        week_high = prev_week_high
        week_low = prev_week_low
        if not na(week_hi_line):
            line.delete(week_hi_line)
        if not na(week_lo_line):
            line.delete(week_lo_line)
        if not na(week_hi_label):
            label.delete(week_hi_label)
        if not na(week_lo_label):
            label.delete(week_lo_label)
        if inLookback and show_weeklevels and (timeframe.in_seconds('') <= timeframe.in_seconds(tf_limit)):
            week_hi_line = line.new(bar_index, week_high, bar_index + 1, week_high, color=weeklevels_color, style=weeklevels_style_lookup)
            week_lo_line = line.new(bar_index, week_low, bar_index + 1, week_low, color=weeklevels_color, style=weeklevels_style_lookup)

    if inLookback and (not na(week_hi_line)):
        line.set_x2(week_hi_line, bar_index)
        if not na(week_hi_label):
            label.delete(week_hi_label)
        if not combine_labels:
            week_hi_label = label.new(bar_index, week_high, 'PWH', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    if inLookback and (not na(week_lo_line)):
        line.set_x2(week_lo_line, bar_index)
        if not na(week_lo_label):
            label.delete(week_lo_label)
        if not combine_labels:
            week_lo_label = label.new(bar_index, week_low, 'PWL', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    d1h, d1l, d2h, d2l, d3h, d3l, d4h, d4l = request.security(syminfo.tickerid, 'D', (high, low, high[1], low[1], high[2], low[2], high[3], low[3]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    pd_high: Persistent[float] = na(float)
    pd_low: Persistent[float] = na(float)
    wed_high: Persistent[float] = na(float)
    wed_low: Persistent[float] = na(float)
    tue_high: Persistent[float] = na(float)
    tue_low: Persistent[float] = na(float)
    mon_high: Persistent[float] = na(float)
    mon_low: Persistent[float] = na(float)

    pd_hi_line: Persistent[Line] = na(Line)
    pd_lo_line: Persistent[Line] = na(Line)
    wed_hi_line: Persistent[Line] = na(Line)
    wed_lo_line: Persistent[Line] = na(Line)
    tue_hi_line: Persistent[Line] = na(Line)
    tue_lo_line: Persistent[Line] = na(Line)
    mon_hi_line: Persistent[Line] = na(Line)
    mon_lo_line: Persistent[Line] = na(Line)

    pd_hi_label: Persistent[Label] = na(Label)
    pd_lo_label: Persistent[Label] = na(Label)
    wed_hi_label: Persistent[Label] = na(Label)
    wed_lo_label: Persistent[Label] = na(Label)
    tue_hi_label: Persistent[Label] = na(Label)
    tue_lo_label: Persistent[Label] = na(Label)
    mon_hi_label: Persistent[Label] = na(Label)
    mon_lo_label: Persistent[Label] = na(Label)

    is_newday = hour(time, gmt_tz) == 0 and minute(time, gmt_tz) == 0

    if is_newday:
        pd_high = d1h
        pd_low = d1l
        wed_high = d2h
        wed_low = d2l
        tue_high = d3h
        tue_low = d3l
        mon_high = d4h
        mon_low = d4l

        if not na(pd_hi_line):
            line.delete(pd_hi_line)
            line.delete(pd_lo_line)
            label.delete(pd_hi_label)
            label.delete(pd_lo_label)
        if not na(wed_hi_line):
            line.delete(wed_hi_line)
            line.delete(wed_lo_line)
            label.delete(wed_hi_label)
            label.delete(wed_lo_label)
        if not na(tue_hi_line):
            line.delete(tue_hi_line)
            line.delete(tue_lo_line)
            label.delete(tue_hi_label)
            label.delete(tue_lo_label)
        if not na(mon_hi_line):
            line.delete(mon_hi_line)
            line.delete(mon_lo_line)
            label.delete(mon_hi_label)
            label.delete(mon_lo_label)

        if inLookback and timeframe.in_seconds('') <= timeframe.in_seconds(tf_limit):
            if show_pdlevels:
                pd_hi_line = line.new(bar_index, pd_high, bar_index + 1, pd_high, color=daylevels_color, style=daylevels_style_lookup)
                pd_lo_line = line.new(bar_index, pd_low, bar_index + 1, pd_low, color=daylevels_color, style=daylevels_style_lookup)
            if show_wed_levels:
                wed_hi_line = line.new(bar_index, wed_high, bar_index + 1, wed_high, color=daylevels_color, style=daylevels_style_lookup)
                wed_lo_line = line.new(bar_index, wed_low, bar_index + 1, wed_low, color=daylevels_color, style=daylevels_style_lookup)
            if show_tue_levels:
                tue_hi_line = line.new(bar_index, tue_high, bar_index + 1, tue_high, color=daylevels_color, style=daylevels_style_lookup)
                tue_lo_line = line.new(bar_index, tue_low, bar_index + 1, tue_low, color=daylevels_color, style=daylevels_style_lookup)
            if show_mon_levels:
                mon_hi_line = line.new(bar_index, mon_high, bar_index + 1, mon_high, color=daylevels_color, style=daylevels_style_lookup)
                mon_lo_line = line.new(bar_index, mon_low, bar_index + 1, mon_low, color=daylevels_color, style=daylevels_style_lookup)

    if inLookback and (not na(pd_hi_line)):
        line.set_x2(pd_hi_line, bar_index)
        line.set_x2(pd_lo_line, bar_index)
        if not na(pd_hi_label):
            label.delete(pd_hi_label)
        if not na(pd_lo_label):
            label.delete(pd_lo_label)
        if not combine_labels:
            pd_hi_label = label.new(bar_index, pd_high, 'PDH', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)
            pd_lo_label = label.new(bar_index, pd_low, 'PDL', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    if inLookback and (not na(wed_hi_line)):
        line.set_x2(wed_hi_line, bar_index)
        line.set_x2(wed_lo_line, bar_index)
        if not na(wed_hi_label):
            label.delete(wed_hi_label)
        if not na(wed_lo_label):
            label.delete(wed_lo_label)
        if not combine_labels:
            wed_hi_label = label.new(bar_index, wed_high, 'WED.H', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)
            wed_lo_label = label.new(bar_index, wed_low, 'WED.L', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    if inLookback and (not na(tue_hi_line)):
        line.set_x2(tue_hi_line, bar_index)
        line.set_x2(tue_lo_line, bar_index)
        if not na(tue_hi_label):
            label.delete(tue_hi_label)
        if not na(tue_lo_label):
            label.delete(tue_lo_label)
        if not combine_labels:
            tue_hi_label = label.new(bar_index, tue_high, 'TUE.H', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)
            tue_lo_label = label.new(bar_index, tue_low, 'TUE.L', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    if inLookback and (not na(mon_hi_line)):
        line.set_x2(mon_hi_line, bar_index)
        line.set_x2(mon_lo_line, bar_index)
        if not na(mon_hi_label):
            label.delete(mon_hi_label)
        if not na(mon_lo_label):
            label.delete(mon_lo_label)
        if not combine_labels:
            mon_hi_label = label.new(bar_index, mon_high, 'MON.H', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)
            mon_lo_label = label.new(bar_index, mon_low, 'MON.L', color=color.new(color.black, label_bg_transp), textcolor=label_color, style=label.style_label_left, size=label_size_setting, xloc=xloc.bar_index)

    if timeframe.in_seconds('') <= timeframe.in_seconds(tf_limit):
        if use_asia:
            asia_sess: Series = time(timeframe.period, '2000-0000', gmt_tz)
            in_asia = not na(asia_sess)
            nh, nl, nhi, nli = updateSessionLevels(asia_high, asia_low, asia_hi_idx, asia_lo_idx, in_asia)
            asia_high = nh
            asia_low = nl
            asia_hi_idx = nhi
            asia_lo_idx = nli
            if inLookback and na(asia_sess) and (not na(asia_sess[1])) and show_levels:
                drawSessionLevels(asia_high, asia_hi_idx, asia_high_text, True)
                drawSessionLevels(asia_low, asia_lo_idx, asia_low_text, False)
                asia_high = na
                asia_low = na
                asia_hi_idx = na
                asia_lo_idx = na

        if use_london:
            lon_sess: Series = time(timeframe.period, '0200-0500', gmt_tz)
            in_london = not na(lon_sess)
            nh, nl, nhi, nli = updateSessionLevels(lon_high, lon_low, lon_hi_idx, lon_lo_idx, in_london)
            lon_high = nh
            lon_low = nl
            lon_hi_idx = nhi
            lon_lo_idx = nli
            if inLookback and na(lon_sess) and (not na(lon_sess[1])) and show_levels:
                drawSessionLevels(lon_high, lon_hi_idx, london_high_text, True)
                drawSessionLevels(lon_low, lon_lo_idx, london_low_text, False)
                lon_high = na
                lon_low = na
                lon_hi_idx = na
                lon_lo_idx = na

        if use_nyam:
            nyam_sess: Series = time(timeframe.period, '0830-1130', gmt_tz)
            in_nyam = not na(nyam_sess)
            nh, nl, nhi, nli = updateSessionLevels(nyam_high, nyam_low, nyam_hi_idx, nyam_lo_idx, in_nyam)
            nyam_high = nh
            nyam_low = nl
            nyam_hi_idx = nhi
            nyam_lo_idx = nli
            if inLookback and na(nyam_sess) and (not na(nyam_sess[1])) and show_levels:
                drawSessionLevels(nyam_high, nyam_hi_idx, nyam_high_text, True)
                drawSessionLevels(nyam_low, nyam_lo_idx, nyam_low_text, False)
                nyam_high = na
                nyam_low = na
                nyam_hi_idx = na
                nyam_lo_idx = na

        if use_nylu:
            nylu_sess: Series = time(timeframe.period, '1200-1300', gmt_tz)
            in_nylu = not na(nylu_sess)
            nh, nl, nhi, nli = updateSessionLevels(nylu_high, nylu_low, nylu_hi_idx, nylu_lo_idx, in_nylu)
            nylu_high = nh
            nylu_low = nl
            nylu_hi_idx = nhi
            nylu_lo_idx = nli
            if inLookback and na(nylu_sess) and (not na(nylu_sess[1])) and show_levels:
                drawSessionLevels(nylu_high, nylu_hi_idx, nylu_high_text, True)
                drawSessionLevels(nylu_low, nylu_lo_idx, nylu_low_text, False)
                nylu_high = na
                nylu_low = na
                nylu_hi_idx = na
                nylu_lo_idx = na

        if use_nypm:
            nypm_sess: Series = time(timeframe.period, '1330-1800', gmt_tz)
            in_nypm = not na(nypm_sess)
            nh, nl, nhi, nli = updateSessionLevels(nypm_high, nypm_low, nypm_hi_idx, nypm_lo_idx, in_nypm)
            nypm_high = nh
            nypm_low = nl
            nypm_hi_idx = nhi
            nypm_lo_idx = nli
            if inLookback and na(nypm_sess) and (not na(nypm_sess[1])) and show_levels:
                drawSessionLevels(nypm_high, nypm_hi_idx, nypm_high_text, True)
                drawSessionLevels(nypm_low, nypm_lo_idx, nypm_low_text, False)
                nypm_high = na
                nypm_low = na
                nypm_hi_idx = na
                nypm_lo_idx = na

        updateLines()

    if show_ict_labels and combine_labels and (timeframe.in_seconds('') <= timeframe.in_seconds(tf_limit)):
        if array.size(high_labels) > 0:
            for lb in high_labels:
                label.delete(lb)
            array.clear(high_labels)
        if array.size(low_labels) > 0:
            for lb in low_labels:
                label.delete(lb)
            array.clear(low_labels)

        if not na(week_hi_label):
            label.delete(week_hi_label)
            week_hi_label = na
        if not na(week_lo_label):
            label.delete(week_lo_label)
            week_lo_label = na
        if not na(pd_hi_label):
            label.delete(pd_hi_label)
            pd_hi_label = na
        if not na(pd_lo_label):
            label.delete(pd_lo_label)
            pd_lo_label = na
        if not na(wed_hi_label):
            label.delete(wed_hi_label)
            wed_hi_label = na
        if not na(wed_lo_label):
            label.delete(wed_lo_label)
            wed_lo_label = na
        if not na(tue_hi_label):
            label.delete(tue_hi_label)
            tue_hi_label = na
        if not na(tue_lo_label):
            label.delete(tue_lo_label)
            tue_lo_label = na
        if not na(mon_hi_label):
            label.delete(mon_hi_label)
            mon_hi_label = na
        if not na(mon_lo_label):
            label.delete(mon_lo_label)
            mon_lo_label = na
        if not na(dayopen_label_obj):
            label.delete(dayopen_label_obj)
            dayopen_label_obj = na

        if array.size(combined_labels_arr) > 0:
            for cl in combined_labels_arr:
                label.delete(cl)
            array.clear(combined_labels_arr)
        array.clear(used_label_x)
        array.clear(used_label_y)
        array.clear(_groups)

        if array.size(high_lines) > 0:
            for i in pine_range(0, array.size(high_lines) - 1):
                ln = array.get(high_lines, i)
                price = line.get_y1(ln)
                token = array.get(high_texts, i) if array.size(high_texts) > i else 'HIGH'
                add_group(price, token, bar_index)
        if array.size(low_lines) > 0:
            for i in pine_range(0, array.size(low_lines) - 1):
                ln = array.get(low_lines, i)
                price = line.get_y1(ln)
                token = array.get(low_texts, i) if array.size(low_texts) > i else 'LOW'
                add_group(price, token, bar_index)

        if show_weeklevels:
            if not na(week_hi_line) and (not na(week_high)):
                add_group(week_high, 'PWH', bar_index)
            if not na(week_lo_line) and (not na(week_low)):
                add_group(week_low, 'PWL', bar_index)

        if show_pdlevels and (not na(pd_hi_line)):
            add_group(pd_high, 'PDH', bar_index)
            add_group(pd_low, 'PDL', bar_index)
        if show_wed_levels and (not na(wed_hi_line)):
            add_group(wed_high, 'WED.H', bar_index)
            add_group(wed_low, 'WED.L', bar_index)
        if show_tue_levels and (not na(tue_hi_line)):
            add_group(tue_high, 'TUE.H', bar_index)
            add_group(tue_low, 'TUE.L', bar_index)
        if show_mon_levels and (not na(mon_hi_line)):
            add_group(mon_high, 'MON.H', bar_index)
            add_group(mon_low, 'MON.L', bar_index)

        if show_dayopen and (not na(dayopen_line)) and (not na(dayopen_price)):
            add_group(dayopen_price, 'True Day Open', bar_index)

        if array.size(_groups) > 0:
            sep: float = syminfo.mintick * 6.0
            for g in _groups:
                lx: int = bar_index
                ly: float = g.level
                safety: int = 0
                clash: bool = True
                while clash and safety < 8:
                    clash = False
                    if array.size(used_label_x) > 0 and array.size(used_label_y) > 0:
                        cnt = math.min(array.size(used_label_x), array.size(used_label_y))
                        for j in pine_range(0, cnt - 1):
                            if array.get(used_label_x, j) == lx and math.abs(ly - array.get(used_label_y, j)) < sep:
                                ly += sep
                                clash = True
                                break
                    safety += 1
                new_lbl = label.new(lx, ly, g.txt, xloc=xloc.bar_index, style=label.style_label_left, color=color.new(color.white, 100), textcolor=label_color, size=label_size_setting)
                array.push(combined_labels_arr, new_lbl)
                array.push(used_label_x, lx)
                array.push(used_label_y, ly)

    def inSession(sess):
        return not na(time(timeframe.period, sess, gmt_tz))

    inAsia = inSession('2000-0000')
    inLondon = inSession('0200-0500')
    inNY = inSession('0800-1100')
    inLondonClose = inSession('1000-1200')

    dash: Persistent[Table] = table.new(position.top_right, 2, 10, bgcolor=color.new(color.black, 60), border_color=color.new(color.gray, 50), border_width=1, frame_color=color.new(color.gray, 30), frame_width=1)

    vwapDir = '▲ Above VWAP' if close > vwap else '▼ Below VWAP'
    vwapDirCol = bullCol if close > vwap else bearCol
    volRatio = math.round(volume / volMA, 2)
    volRatioCol = bullCol if volRatio >= 1.2 else color.gray
    volRising = volume[1] > volume[2]
    kzName = '🟢 New York' if inNY else '🔵 London' if inLondon else '🟠 Ldn Close' if inLondonClose else '🟣 Asia' if inAsia else 'Off-Session'
    lastSig = '▲ LONG' if bullSignal else '▼ SHORT' if bearSignal else 'None'
    lastSigCol = bullCol if bullSignal else bearCol if bearSignal else color.gray
    impulseStr = '▲ Bull Match' if impulseBullSame else '▲ Bull Mixed' if impulseBullMixed else '▼ Bear Match' if impulseBearSame else '▼ Bear Mixed' if impulseBearMixed else '–'
    impulseCol = bullCol if impulseBull else bearCol if impulseBear else color.gray
    b1BodyStr = string.tostring(math.round(b1bodyPct * 100, 0)) + '%'
    b2BodyStr = string.tostring(math.round(b2bodyPct * 100, 0)) + '%'
    b2VolStr = '✔ Rising' if volConfirm else '✘ Flat'
    b2VolCol = bullCol if volConfirm else bearCol

    nearPDH = not na(pd_high) and math.abs(close - pd_high) < atr * 0.5
    nearPDL = not na(pd_low) and math.abs(close - pd_low) < atr * 0.5
    nearPWH = not na(week_high) and math.abs(close - week_high) < atr * 0.5
    nearPWL = not na(week_low) and math.abs(close - week_low) < atr * 0.5
    ictProx = '⚡ PDH' if nearPDH else '⚡ PDL' if nearPDL else '⚡ PWH' if nearPWH else '⚡ PWL' if nearPWL else '–'
    ictProxCol = color.yellow if nearPDH or nearPDL or nearPWH or nearPWL else color.gray

    if showDashboard and barstate.islast:
        table.cell(dash, 0, 0, 'TWO-BAR FIB RETRACE', text_color=color.white, bgcolor=color.new(color.blue, 40), text_size=size.small)
        table.cell(dash, 1, 0, '[FUTURES ET]', text_color=color.white, bgcolor=color.new(color.blue, 40), text_size=size.small)
        table.cell(dash, 0, 1, 'Killzone', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 1, kzName, text_color=color.white, text_size=size.small)
        table.cell(dash, 0, 2, 'VWAP', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 2, vwapDir, text_color=vwapDirCol, text_size=size.small)
        table.cell(dash, 0, 3, 'Vol Ratio', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 3, string.tostring(volRatio) + 'x', text_color=volRatioCol, text_size=size.small)
        table.cell(dash, 0, 4, 'Bar2 Vol Rising', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 4, b2VolStr, text_color=b2VolCol, text_size=size.small)
        table.cell(dash, 0, 5, 'Bar1 Body', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 5, b1BodyStr, text_color=color.white, text_size=size.small)
        table.cell(dash, 0, 6, 'Bar2 Body', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 6, b2BodyStr, text_color=color.white, text_size=size.small)
        table.cell(dash, 0, 7, 'Impulse', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 7, impulseStr, text_color=impulseCol, text_size=size.small)
        table.cell(dash, 0, 8, 'ICT Level', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 8, ictProx, text_color=ictProxCol, text_size=size.small)
        table.cell(dash, 0, 9, 'Last Signal', text_color=color.gray, text_size=size.small)
        table.cell(dash, 1, 9, lastSig, text_color=lastSigCol, text_size=size.small)

    alertcondition(bullSignal, 'LONG Signal', 'Two-Bar: LONG — wick into retrace zone above VWAP')
    alertcondition(bearSignal, 'SHORT Signal', 'Two-Bar: SHORT — wick into retrace zone below VWAP')
    alertcondition(bullSignal and inNY, 'LONG in NY', 'Two-Bar: LONG during NY Killzone')
    alertcondition(bearSignal and inNY, 'SHORT in NY', 'Two-Bar: SHORT during NY Killzone')
    alertcondition(bullSignal and inLondon, 'LONG in London', 'Two-Bar: LONG during London Killzone')
    alertcondition(bearSignal and inLondon, 'SHORT in London', 'Two-Bar: SHORT during London Killzone')
    alertcondition(bullSignal or bearSignal, 'Any Signal', 'Two-Bar: New signal detected')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
