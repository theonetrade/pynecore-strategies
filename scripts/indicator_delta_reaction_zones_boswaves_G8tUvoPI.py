"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, box, chart, close, color, high, input, line,
    location, low, math, na, nz, open, plotshape, script, shape, size, string, syminfo, ta, text,
    time, timeframe, volume, xloc
)
from pynecore.types import Box, Color, Line, NA, Persistent, PersistentSeries, Series


@udt
class VolumeZone:
    zone_body: Box = na(Box)
    positive_segment: Box = na(Box)
    negative_segment: Box = na(Box)
    stats_pos_box: Box = na(Box)
    stats_neg_box: Box = na(Box)
    stats_total_box: Box = na(Box)
    zone_midline: Line = na(Line)
    is_lower: bool = na(bool)
    zone_top: float = na(float)
    zone_bottom: float = na(float)
    zone_mid: float = na(float)
    positive_pct: float = na(float)
    negative_pct: float = na(float)
    net_impulse_value: float = na(float)
    creation_time: int = na(int)
    last_touch_time: int = na(int)


group_delta: str = "Delta Settings"
group_zones: str = "Zone Construction"
group_visual: str = "Visualization"
border_color: Color = color.new('#787B86')
GREEN: Color = color.new('#00FF00')
RED: Color = color.new('#FF0000')
HARD_SEG_CAP_BARS: int = 300
tt1: str = "Exponential Moving Average smoothing applied to raw delta. Higher values reduce noise but add lag. Set to 1 to disable smoothing."
tt2: str = "Number of bars used on both the left and right side to confirm a pivot. Higher values produce fewer but more significant zones."
tt3: str = "Data series used for pivot detection. Cumulative Delta uses the running delta total. Cumulative Delta RoC uses the rate of change of cumulative delta to highlight flow acceleration."
tt4: str = "Lookback length for the rate-of-change calculation when Cumulative Delta RoC is selected as the pivot source."
tt5: str = "ATR period used to adapt zone thickness to current market volatility."
tt6: str = "Multiplier applied to ATR to define the half-width of each zone around its anchor price. For lower timeframes please lower this setting, as zones can appear very large"
tt8: str = "Maximum number of zones allowed on the chart at once. Oldest zones are removed first. Broken zones are removed automatically."
tt9: str = "When enabled, overlapping zones of the same type are merged into a single broader zone."
tt10: str = "Additional merge tolerance in ticks. A value of 0 merges only true overlaps. Higher values allow merging zones that are close but not overlapping."
tt11: str = "Lookback window used to compute impulse statistics including net delta and positive versus negative flow percentages."
tt12: str = "Color used for support zones created from lower delta pivots."
tt13: str = "Color used for resistance zones created from upper delta pivots."
tt14: str = "Displays filled zone boxes. If disabled, only the dashed midline is shown for a cleaner view."
tt15: str = "Show reclaim/re-enter markers when price crosses back through a zone midline. Disable for a clean chart while keeping zones active."
tt16: str = "Extends the main zone box and pushes the stats boxes out by the same amount."
tt17: str = "Number of bars used to render the stats boxes to the right of the zone end."


@script.indicator("Delta Reaction Zones [BOSWaves]", overlay=True, max_boxes_count=500, max_lines_count=500)
def main(
    delta_smooth=input.int(3, "Delta Smoothing Length (EMA)", minval=1, group=group_delta, tooltip=tt1),
    pivot_length=input.int(12, "Pivot Length (Left/Right)", minval=2, group=group_delta, tooltip=tt2),
    pivot_source=input.string("Cumulative Delta", "Pivot Source", options=("Cumulative Delta", "Cumulative Delta RoC"), group=group_delta, tooltip=tt3),
    roc_length=input.int(12, "RoC Length (if RoC selected)", minval=2, group=group_delta, tooltip=tt4),
    impulse_window=input.int(100, "Impulse Window Length", minval=5, group=group_delta, tooltip=tt11),
    atr_length=input.int(14, "ATR Length", minval=1, group=group_zones, tooltip=tt5),
    atr_multiplier=input.float(0.35, "ATR Multiplier", minval=0.01, step=0.05, group=group_zones, tooltip=tt6),
    maximum_zones=input.int(8, "Maximum Zones Displayed", minval=5, maxval=200, group=group_zones, tooltip=tt8),
    merge_zones=input.bool(True, "Merge Overlapping Zones", group=group_zones, tooltip=tt9),
    merge_gap_ticks=input.float(20, "Merge Gap (in ticks)", minval=0.0, step=10, group=group_zones, tooltip=tt10),
    lower_zone_color=input.color(GREEN, "Support Color", group=group_visual, tooltip=tt12),
    upper_zone_color=input.color(RED, "Resistance Color", group=group_visual, tooltip=tt13),
    show_zone_boxes=input.bool(True, "Show Zone Boxes", group=group_visual, tooltip=tt14),
    show_signals=input.bool(True, "Show Signals", group=group_visual, tooltip=tt15),
    extend_bars=input.int(65, "Extend Zone (bars)", minval=0, maxval=600, group=group_zones, tooltip=tt16),
    stats_box_bars=input.int(30, "Stats Box Width (bars)", minval=1, maxval=50, group=group_visual, tooltip=tt16)
):
    def clamp_value(value, min_val, max_val):
        return math.max(min_val, math.min(value, max_val))

    tf_seconds = timeframe.in_seconds('')
    tf_milliseconds = cast_int(math.round(tf_seconds * 1000.0))

    def fmt2(v):
        return string.tostring(math.round(v * 100.0) / 100.0, '#.00')

    def delta_text(target_box, pos_pct, neg_pct):
        txt: str = 'SELL FLOW' if pos_pct >= 60 else 'BUY FLOW' if neg_pct >= 60 else 'MIXED'
        method_call('set_text', target_box, txt)
        method_call('set_text_halign', target_box, text.align_right)
        method_call('set_text_valign', target_box, text.align_center)
        method_call('set_text_color', target_box, chart.fg_color)
        return method_call('set_text_size', target_box, size.auto)

    def percent_box(target_box, pct_value):
        method_call('set_text', target_box, string.tostring(math.round(pct_value, 1)) + '%')
        method_call('set_text_halign', target_box, text.align_center)
        method_call('set_text_valign', target_box, text.align_center)
        method_call('set_text_color', target_box, chart.fg_color)
        return method_call('set_text_size', target_box, size.auto)

    def stats_total_text(target_box, total_val):
        method_call('set_text', target_box, 'Δ ' + fmt2(total_val))
        method_call('set_text_halign', target_box, text.align_center)
        method_call('set_text_valign', target_box, text.align_center)
        method_call('set_text_color', target_box, chart.fg_color)
        return method_call('set_text_size', target_box, size.auto)

    def seg_cap_bars_50_box(left_time: int, body_right: int, hardCapBars: int):
        zone_ms: int = math.max(body_right - left_time, 0)
        zone_bars: int = cast_int(math.floor(zone_ms / tf_milliseconds)) if tf_milliseconds > 0 else 0
        halfBars: int = cast_int(math.floor(zone_bars * 0.5))
        cap: int = math.min(halfBars, hardCapBars)
        return math.max(cap, 1)

    def seg_right_time(left_time: int, body_right: int, width_bars: int):
        r: int = left_time + width_bars * tf_milliseconds
        return math.min(r, body_right)

    signed_position = math.sign(close - open)
    signed_position = clamp_value(signed_position, -1.0, 1.0)

    raw_delta = signed_position * nz(volume, 0.0)
    smoothed_delta = ta.ema(raw_delta, delta_smooth) if delta_smooth > 1 else raw_delta

    cumulative_delta: PersistentSeries[float] = na(float)
    cumulative_delta = smoothed_delta if na(cumulative_delta[1]) else cumulative_delta[1] + smoothed_delta

    delta_roc = cumulative_delta - cumulative_delta[roc_length]
    pivot_input_series = delta_roc if pivot_source == 'Cumulative Delta RoC' else cumulative_delta

    pivot_high_value = ta.pivothigh(pivot_input_series, pivot_length, pivot_length)
    pivot_low_value = ta.pivotlow(pivot_input_series, pivot_length, pivot_length)
    new_upper_pivot = not na(pivot_high_value)
    new_lower_pivot = not na(pivot_low_value)

    current_zone_half_width: Series = ta.atr(atr_length) * atr_multiplier

    positive_flow = math.max(smoothed_delta, 0.0)
    negative_flow = math.max(-smoothed_delta, 0.0)

    sum_positive = math.sum(positive_flow, impulse_window)
    sum_negative = math.sum(negative_flow, impulse_window)
    total_flow = sum_positive + sum_negative

    positive_percentage: Series = sum_positive / total_flow * 100.0 if total_flow > 0 else 50.0
    negative_percentage: Series = 100.0 - positive_percentage
    net_impulse: Series = math.sum(smoothed_delta, impulse_window)

    active_zones: Persistent[list[VolumeZone]] = array.new(0, NA(VolumeZone))

    def create_zone(is_lower_zone, anchor_price, half_width, pos_pct, neg_pct, impulse_val, creation_timestamp):
        top_price: float = anchor_price + half_width
        bottom_price: float = anchor_price - half_width
        mid_price: float = math.avg(top_price, bottom_price)

        base_color: Color = lower_zone_color if is_lower_zone else upper_zone_color
        fill_color: Color = color.new(base_color, 75)

        left_time: int = creation_timestamp
        right_time: int = creation_timestamp + extend_bars * tf_milliseconds

        stats_left: int = right_time + 10 * tf_milliseconds
        stats_right_2: int = stats_left + stats_box_bars * tf_milliseconds

        zone_body_box: Box = na(Box)
        positive_segment_box: Box = na(Box)
        negative_segment_box: Box = na(Box)
        stats_pos: Box = na(Box)
        stats_neg: Box = na(Box)
        stats_total: Box = na(Box)

        if show_zone_boxes:
            zone_body_box = box.new(left_time, top_price, right_time, bottom_price, xloc=xloc.bar_time, bgcolor=fill_color, border_color=border_color, border_width=1, border_style=line.style_dotted)

            body_right: int = right_time
            cap_bars: int = seg_cap_bars_50_box(left_time, body_right, HARD_SEG_CAP_BARS)

            positive_width: int = cast_int(math.round(cap_bars * (pos_pct * 0.01)))
            negative_width: int = cast_int(math.round(cap_bars * (neg_pct * 0.01)))
            positive_width = 1 if positive_width < 1 and pos_pct > 0 else positive_width
            negative_width = 1 if negative_width < 1 and neg_pct > 0 else negative_width

            positive_right: int = seg_right_time(left_time, body_right, positive_width)
            negative_right: int = seg_right_time(left_time, body_right, negative_width)

            negative_segment_box = box.new(left_time, top_price, negative_right, mid_price, xloc=xloc.bar_time, bgcolor=color.new(upper_zone_color, 40), border_color=chart.bg_color)

            positive_segment_box = box.new(left_time, mid_price, positive_right, bottom_price, xloc=xloc.bar_time, bgcolor=color.new(lower_zone_color, 40), border_color=chart.bg_color)

            stats_neg = box.new(right_time, top_price, stats_left, mid_price, xloc=xloc.bar_time, bgcolor=color.new(upper_zone_color, 40), border_color=chart.bg_color)

            stats_pos = box.new(right_time, mid_price, stats_left, bottom_price, xloc=xloc.bar_time, bgcolor=color.new(lower_zone_color, 40), border_color=chart.bg_color)

            stats_total = box.new(stats_left, top_price, stats_right_2, bottom_price, xloc=xloc.bar_time, bgcolor=color.new(base_color, 82), border_color=border_color, border_width=1, border_style=line.style_dotted)

            percent_box(stats_pos, pos_pct)
            percent_box(stats_neg, neg_pct)
            stats_total_text(stats_total, impulse_val)
            delta_text(zone_body_box, pos_pct, neg_pct)

        midline_line: Line = line.new(left_time, mid_price, right_time, mid_price, xloc=xloc.bar_time, color=border_color, width=1, style=line.style_dashed)

        return VolumeZone(zone_body_box, positive_segment_box, negative_segment_box, stats_pos, stats_neg, stats_total, midline_line, is_lower_zone, top_price, bottom_price, mid_price, pos_pct, neg_pct, impulse_val, creation_timestamp, creation_timestamp)

    def zones_overlap_or_near(top_a, bot_a, top_b, bot_b, gap_price):
        expanded_top_a: float = top_a + gap_price
        expanded_bot_a: float = bot_a - gap_price
        expanded_top_b: float = top_b + gap_price
        expanded_bot_b: float = bot_b - gap_price
        return expanded_bot_a <= expanded_top_b and expanded_top_a >= expanded_bot_b

    def merge_zone_into_existing(new_zone):
        merged: bool = False
        if merge_zones and array.size(active_zones) > 0:
            price_gap: float = merge_gap_ticks * syminfo.mintick
            for i in pine_range(array.size(active_zones) - 1, 0):
                existing: VolumeZone = array.get(active_zones, i)
                if existing.is_lower == new_zone.is_lower:
                    if zones_overlap_or_near(existing.zone_top, existing.zone_bottom, new_zone.zone_top, new_zone.zone_bottom, price_gap):
                        existing.zone_top = math.max(existing.zone_top, new_zone.zone_top)
                        existing.zone_bottom = math.min(existing.zone_bottom, new_zone.zone_bottom)
                        existing.zone_mid = math.avg(existing.zone_top, existing.zone_bottom)

                        weight_existing: float = math.max(math.abs(existing.net_impulse_value), 1.0)
                        weight_new: float = math.max(math.abs(new_zone.net_impulse_value), 1.0)
                        existing.positive_pct = (existing.positive_pct * weight_existing + new_zone.positive_pct * weight_new) / (weight_existing + weight_new)
                        existing.negative_pct = 100.0 - existing.positive_pct
                        existing.net_impulse_value = existing.net_impulse_value + new_zone.net_impulse_value

                        existing.creation_time = math.min(existing.creation_time, new_zone.creation_time)
                        existing.last_touch_time = math.max(existing.last_touch_time, new_zone.last_touch_time)

                        left_time: int = box.get_left(existing.zone_body)
                        body_right: int = time + extend_bars * tf_milliseconds

                        if show_zone_boxes and (not na(existing.zone_body)):
                            box.set_top(existing.zone_body, existing.zone_top)
                            box.set_bottom(existing.zone_body, existing.zone_bottom)

                            box.set_right(existing.zone_body, body_right)

                            cap_bars: int = seg_cap_bars_50_box(left_time, body_right, HARD_SEG_CAP_BARS)

                            positive_width: int = cast_int(math.round(cap_bars * (existing.positive_pct * 0.01)))
                            negative_width: int = cast_int(math.round(cap_bars * (existing.negative_pct * 0.01)))
                            positive_width = 1 if positive_width < 1 and existing.positive_pct > 0 else positive_width
                            negative_width = 1 if negative_width < 1 and existing.negative_pct > 0 else negative_width

                            pos_right: int = seg_right_time(left_time, body_right, positive_width)
                            neg_right: int = seg_right_time(left_time, body_right, negative_width)

                            box.set_left(existing.positive_segment, left_time)
                            box.set_right(existing.positive_segment, pos_right)
                            box.set_left(existing.negative_segment, left_time)
                            box.set_right(existing.negative_segment, neg_right)

                            box.set_top(existing.negative_segment, existing.zone_top)
                            box.set_bottom(existing.negative_segment, existing.zone_mid)
                            box.set_top(existing.positive_segment, existing.zone_mid)
                            box.set_bottom(existing.positive_segment, existing.zone_bottom)

                            stats_left: int = body_right + 10 * tf_milliseconds
                            stats_right_2: int = stats_left + stats_box_bars * tf_milliseconds

                            box.set_left(existing.stats_neg_box, body_right)
                            box.set_right(existing.stats_neg_box, stats_left)
                            box.set_top(existing.stats_neg_box, existing.zone_top)
                            box.set_bottom(existing.stats_neg_box, existing.zone_mid)

                            box.set_left(existing.stats_pos_box, body_right)
                            box.set_right(existing.stats_pos_box, stats_left)
                            box.set_top(existing.stats_pos_box, existing.zone_mid)
                            box.set_bottom(existing.stats_pos_box, existing.zone_bottom)

                            percent_box(existing.stats_pos_box, existing.positive_pct)
                            percent_box(existing.stats_neg_box, existing.negative_pct)

                            box.set_left(existing.stats_total_box, stats_left)
                            box.set_right(existing.stats_total_box, stats_right_2)
                            box.set_top(existing.stats_total_box, existing.zone_top)
                            box.set_bottom(existing.stats_total_box, existing.zone_bottom)

                            stats_total_text(existing.stats_total_box, existing.net_impulse_value)
                            delta_text(existing.zone_body, existing.positive_pct, existing.negative_pct)

                        line.set_y1(existing.zone_midline, existing.zone_mid)
                        line.set_y2(existing.zone_midline, existing.zone_mid)
                        line.set_x1(existing.zone_midline, box.get_left(existing.zone_body))
                        line.set_x2(existing.zone_midline, body_right)

                        if not na(new_zone.zone_body):
                            box.delete(new_zone.zone_body)
                        if not na(new_zone.positive_segment):
                            box.delete(new_zone.positive_segment)
                        if not na(new_zone.negative_segment):
                            box.delete(new_zone.negative_segment)
                        if not na(new_zone.stats_pos_box):
                            box.delete(new_zone.stats_pos_box)
                        if not na(new_zone.stats_neg_box):
                            box.delete(new_zone.stats_neg_box)
                        if not na(new_zone.stats_total_box):
                            box.delete(new_zone.stats_total_box)

                        line.delete(new_zone.zone_midline)

                        array.set(active_zones, i, existing)
                        merged = True
                        break
        return merged

    if new_upper_pivot:
        anchor_price: float = high[pivot_length]
        half_width: float = current_zone_half_width[pivot_length]
        pos_pct: float = positive_percentage[pivot_length]
        neg_pct: float = negative_percentage[pivot_length]
        impulse_val: float = net_impulse[pivot_length]
        creation_timestamp: int = time[pivot_length]
        new_zone: VolumeZone = create_zone(False, anchor_price, half_width, pos_pct, neg_pct, impulse_val, creation_timestamp)
        merged: bool = merge_zone_into_existing(new_zone)
        if not merged:
            array.push(active_zones, new_zone)

    if new_lower_pivot:
        anchor_price: float = low[pivot_length]
        half_width: float = current_zone_half_width[pivot_length]
        pos_pct: float = positive_percentage[pivot_length]
        neg_pct: float = negative_percentage[pivot_length]
        impulse_val: float = net_impulse[pivot_length]
        creation_timestamp: int = time[pivot_length]
        new_zone: VolumeZone = create_zone(True, anchor_price, half_width, pos_pct, neg_pct, impulse_val, creation_timestamp)
        merged: bool = merge_zone_into_existing(new_zone)
        if not merged:
            array.push(active_zones, new_zone)

    while array.size(active_zones) > maximum_zones:
        oldest: VolumeZone = array.shift(active_zones)
        if not na(oldest.zone_body):
            box.delete(oldest.zone_body)
        if not na(oldest.positive_segment):
            box.delete(oldest.positive_segment)
        if not na(oldest.negative_segment):
            box.delete(oldest.negative_segment)
        if not na(oldest.stats_pos_box):
            box.delete(oldest.stats_pos_box)
        if not na(oldest.stats_neg_box):
            box.delete(oldest.stats_neg_box)
        if not na(oldest.stats_total_box):
            box.delete(oldest.stats_total_box)
        line.delete(oldest.zone_midline)

    zone_index: int = array.size(active_zones) - 1
    while zone_index >= 0:
        zone: VolumeZone = array.get(active_zones, zone_index)

        left_time: int = box.get_left(zone.zone_body) if not na(zone.zone_body) else zone.creation_time
        right_time: int = time + extend_bars * tf_milliseconds
        stats_left: int = right_time + 10 * tf_milliseconds
        stats_right_2: int = stats_left + stats_box_bars * tf_milliseconds

        if show_zone_boxes and (not na(zone.zone_body)):
            box.set_right(zone.zone_body, right_time)

            body_right: int = box.get_right(zone.zone_body)
            cap_bars: int = seg_cap_bars_50_box(left_time, body_right, HARD_SEG_CAP_BARS)

            positive_width: int = cast_int(math.round(cap_bars * (zone.positive_pct * 0.01)))
            negative_width: int = cast_int(math.round(cap_bars * (zone.negative_pct * 0.01)))
            positive_width = 1 if positive_width < 1 and zone.positive_pct > 0 else positive_width
            negative_width = 1 if negative_width < 1 and zone.negative_pct > 0 else negative_width

            pos_right: int = seg_right_time(left_time, body_right, positive_width)
            neg_right: int = seg_right_time(left_time, body_right, negative_width)

            box.set_left(zone.positive_segment, left_time)
            box.set_right(zone.positive_segment, pos_right)
            box.set_left(zone.negative_segment, left_time)
            box.set_right(zone.negative_segment, neg_right)

            box.set_top(zone.negative_segment, zone.zone_top)
            box.set_bottom(zone.negative_segment, zone.zone_mid)
            box.set_top(zone.positive_segment, zone.zone_mid)
            box.set_bottom(zone.positive_segment, zone.zone_bottom)

            box.set_left(zone.stats_neg_box, right_time)
            box.set_right(zone.stats_neg_box, stats_left)
            box.set_top(zone.stats_neg_box, zone.zone_top)
            box.set_bottom(zone.stats_neg_box, zone.zone_mid)

            box.set_left(zone.stats_pos_box, right_time)
            box.set_right(zone.stats_pos_box, stats_left)
            box.set_top(zone.stats_pos_box, zone.zone_mid)
            box.set_bottom(zone.stats_pos_box, zone.zone_bottom)

            percent_box(zone.stats_pos_box, zone.positive_pct)
            percent_box(zone.stats_neg_box, zone.negative_pct)

            box.set_left(zone.stats_total_box, stats_left)
            box.set_right(zone.stats_total_box, stats_right_2)
            box.set_top(zone.stats_total_box, zone.zone_top)
            box.set_bottom(zone.stats_total_box, zone.zone_bottom)

            stats_total_text(zone.stats_total_box, zone.net_impulse_value)
            delta_text(zone.zone_body, zone.positive_pct, zone.negative_pct)

        line.set_x1(zone.zone_midline, left_time)
        line.set_x2(zone.zone_midline, right_time)
        line.set_y1(zone.zone_midline, zone.zone_mid)
        line.set_y2(zone.zone_midline, zone.zone_mid)

        price_touch: bool = high >= zone.zone_bottom and low <= zone.zone_top
        if price_touch:
            zone.last_touch_time = time

        zone_breached: bool = close < zone.zone_bottom if zone.is_lower else close > zone.zone_top

        if zone_breached:
            if not na(zone.zone_body):
                box.delete(zone.zone_body)
            if not na(zone.positive_segment):
                box.delete(zone.positive_segment)
            if not na(zone.negative_segment):
                box.delete(zone.negative_segment)
            if not na(zone.stats_pos_box):
                box.delete(zone.stats_pos_box)
            if not na(zone.stats_neg_box):
                box.delete(zone.stats_neg_box)
            if not na(zone.stats_total_box):
                box.delete(zone.stats_total_box)
            line.delete(zone.zone_midline)
            array.remove(active_zones, zone_index)
        else:
            array.set(active_zones, zone_index, zone)

        zone_index -= 1

    supReclaim: Persistent[bool] = False
    resReenter: Persistent[bool] = False
    supReclaim = False
    resReenter = False

    if array.size(active_zones) > 0:
        for i in pine_range(0, array.size(active_zones) - 1):
            z: VolumeZone = array.get(active_zones, i)

            if z.is_lower:
                wasBelow: bool = close[1] < z.zone_mid
                nowCrossUp: bool = ta.crossover(close, z.zone_mid)
                supReclaim = supReclaim or (wasBelow and nowCrossUp)

            if not z.is_lower:
                wasAbove: bool = close[1] > z.zone_mid
                nowCrossDown: bool = ta.crossunder(close, z.zone_mid)
                resReenter = resReenter or (wasAbove and nowCrossDown)

    plotshape(show_signals and supReclaim, title='Support reclaim', style=shape.labelup, location=location.belowbar, color=color.new(lower_zone_color, 50), text='𝐑𝐂', size=size.small, textcolor=chart.fg_color)

    plotshape(show_signals and resReenter, title='Resistance re-enter', style=shape.labeldown, location=location.abovebar, color=color.new(upper_zone_color, 50), text='𝐑𝐄', size=size.small, textcolor=chart.fg_color)

    alertcondition(new_upper_pivot or new_lower_pivot, title='New Delta Reaction Zone', message='New Delta Reaction Zone| {{exchange}}:{{ticker}}')
    alertcondition(supReclaim, title='Support Reclaim', message='Support Reclaim | {{exchange}}:{{ticker}}')
    alertcondition(resReenter, title='Resistance Re-enter', message='Resistance Re-enter | {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
