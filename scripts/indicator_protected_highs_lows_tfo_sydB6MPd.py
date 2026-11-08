"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, box, close, color, high,
    input, label, line, low, math, na, open, plot, script, ta, time, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series


@udt
class pb:
    price: float = na(float)
    idx: int = na(int)
    valid: bool = False
    bull: bool = na(bool)


@udt
class snd:
    _box: Box = na(Box)
    _30: Line = na(Line)
    _50: Line = na(Line)
    _70: Line = na(Line)


@udt
class dwg:
    _label: list[Label] = na(list)
    _phl: list[Label] = na(list)
    _line: list[Line] = na(list)
    _bull: list[bool] = na(list)


g_STR: str = 'Structure'
g_PHL: str = 'Protected Highs & Lows'
g_PB: str = 'Pullbacks'
g_RET: str = 'Retracements'


@script.indicator('Protected Highs & Lows [TFO]', 'Protected Highs & Lows [TFO]', True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, na_bool=True)
def main(
    ps=input.int(1, 'Pivot Strength', group=g_STR),
    color_trend=input.bool(True, 'Trend Candles', inline='TREND', group=g_STR),
    show_labels=input.bool(True, 'Show Structure Labels', inline='MSS', group=g_STR),
    label_type=input.string('MSS', '', options=('MSS', 'BOS', 'All'), inline='MSS', group=g_STR),
    show_phl=input.bool(True, 'Show Protected Highs & Lows', inline='PHL', group=g_PHL),
    trail_phl=input.bool(True, 'Show Protected Trail', inline='TRAIL', group=g_PHL),
    trail_width=input.int(2, '', inline='TRAIL', group=g_PHL),
    use_valid_pbs=input.bool(True, 'Use Valid Pullback Criteria', tooltip='When looking at the swing high that price must close above for a BOS/MSS, in order to form a valid protected low, price must first close below the low of the candle that made the swing high (and vice versa for protected highs)', group=g_PB),
    extra_valid_pbs=input.bool(False, 'Specific Pullback Candle Criteria', tooltip='When \'Use Valid Pullback Criteria\' is enabled, if a given swing high is formed with a down close candle, the script will look backward to find the most recent up-close candle. Using this candle, price must close below its low to validate a pullback from a swing high (and vice versa)', group=g_PB),
    ph_color=input.color(color.new('#F23645'), '', inline='PHL', group=g_PHL),
    pl_color=input.color(color.blue, '', inline='PHL', group=g_PHL),
    bull_color=input.color(color.teal, '', inline='TREND', group=g_STR),
    bear_color=input.color(color.new('#F23645'), '', inline='TREND', group=g_STR),
    show_rets=input.bool(False, 'Show Retracements', tooltip='Show retracements of the previous zone with 30, 50, and 70% retracement levels', group=g_RET),
    box_transp=input.int(85, 'Box Transparency', minval=0, maxval=100, tooltip='Larger values will make the retracement box more transparent', group=g_RET),
    line_w=input.int(1, 'Line Width', minval=0, maxval=10, group=g_RET),
    line_s=input.string('Dotted', 'Line Style', options=('Solid', 'Dashed', 'Dotted'), group=g_RET)
):
    __block_result__ = na
    __switch__ = line_s
    if __switch__ == 'Solid':
        __block_result__ = line.style_solid
    elif __switch__ == 'Dashed':
        __block_result__ = line.style_dashed
    elif __switch__ == 'Dotted':
        __block_result__ = line.style_dotted
    style: Persistent = __block_result__
    bull: Persistent[bool] = na(bool)
    trail_price: Persistent[float] = na(float)
    trail_color: Persistent[Color] = na(Color)
    ph: Persistent[list[float]] = array.new_float()
    pl: Persistent[list[float]] = array.new_float()
    pht: Persistent[list[int]] = array.new_int()
    plt: Persistent[list[int]] = array.new_int()
    last_high: Persistent[float] = na(float)
    last_low: Persistent[float] = na(float)
    last_high_idx: Persistent[int] = na(int)
    last_low_idx: Persistent[int] = na(int)
    track_high: Persistent[float] = na(float)
    track_low: Persistent[float] = na(float)
    track_high_idx: Persistent[int] = na(int)
    track_low_idx: Persistent[int] = na(int)
    @method
    def snd_add(s: snd, _high: float, _low: float, bull: bool):
        _30__00000021__ = (_high - _low) * 0.3 + _low
        _50__00000021__ = (_high - _low) * 0.5 + _low
        _70__00000021__ = (_high - _low) * 0.7 + _low
        s._box = box.new(time, _high, time, _low, xloc=xloc.bar_time, border_color=na, bgcolor=na)
        s._30 = line.new(time, _30__00000021__, time, _30__00000021__, xloc=xloc.bar_time, color=na, style=style, width=line_w)
        s._50 = line.new(time, _50__00000021__, time, _50__00000021__, xloc=xloc.bar_time, color=na, style=style, width=line_w)
        s._70 = line.new(time, _70__00000021__, time, _70__00000021__, xloc=xloc.bar_time, color=na, style=style, width=line_w)
        return s._70

    @method
    def dwg_add(d: dwg, LB: Label, PHL: Label, LN: Line, BL: bool):
        array.unshift(d._label, LB)
        array.unshift(d._phl, PHL)
        array.unshift(d._line, LN)
        return array.unshift(d._bull, BL)

    @method
    def pb_set(p: pb, P: float, I: int):
        p.price = P
        p.idx = I
        p.valid = False
        return p.valid

    def clear_all():
        array.clear(pl)
        array.clear(plt)
        array.clear(ph)
        return array.clear(pht)

    pb_from_high: Persistent[pb] = pb(bull=True)
    pb_from_low: Persistent[pb] = pb(bull=False)
    if cast_bool(ta.pivotlow(low, ps, ps)) and array.size(pl) == 0:
        array.unshift(pl, low[ps])
        array.unshift(plt, time[ps])
        if extra_valid_pbs:
            for i in pine_range(0, 3, 1):
                if close[ps + i] < open[ps + i]:
                    pb_set(pb_from_low, high[ps + i], bar_index)
                    break
        else:
            pb_set(pb_from_low, high[ps], bar_index)
        if na(last_low):
            last_low = low[ps]
            last_low_idx = bar_index - ps
        else:
            if low[ps] < last_low:
                last_low = low[ps]
                last_low_idx = bar_index - ps
    if cast_bool(ta.pivothigh(high, ps, ps)) and array.size(ph) == 0:
        array.unshift(ph, high[ps])
        array.unshift(pht, time[ps])
        if extra_valid_pbs:
            for i in pine_range(0, 3, 1):
                if close[ps + i] > open[ps + i]:
                    pb_set(pb_from_high, low[ps + i], bar_index)
                    break
        else:
            pb_set(pb_from_high, low[ps], bar_index)
        if na(last_high):
            last_high = high[ps]
            last_high_idx = bar_index - ps
        else:
            if high[ps] > last_high:
                last_high = high[ps]
                last_high_idx = bar_index - ps
    def check_pb(p: pb):
        __block_result_1__ = na
        if p.bull:
            __block_result_2__ = na
            if close < p.price and p.valid == False:
                p.valid = True
                __block_result_2__ = p.valid
            __block_result_1__ = __block_result_2__
        else:
            __block_result_3__ = na
            if close > p.price and p.valid == False:
                p.valid = True
                __block_result_3__ = p.valid
            __block_result_1__ = __block_result_3__
        return __block_result_1__

    check_pb(pb_from_high)
    check_pb(pb_from_low)
    pivothigh_1 = ta.pivothigh(high, ps, ps)
    if (high[ps] > track_high or na(track_high) or last_low_idx >= track_high_idx) and (not na(pivothigh_1)) and (pb_from_low.valid == True if use_valid_pbs else True):
        track_high = high[ps]
        track_high_idx = bar_index - ps
    pivotlow_1 = ta.pivotlow(low, ps, ps)
    if (low[ps] < track_low or na(track_low) or last_high_idx >= track_low_idx) and (not na(pivotlow_1)) and (pb_from_high.valid == True if use_valid_pbs else True):
        track_low = low[ps]
        track_low_idx = bar_index - ps
    bos_bear: Series[bool] = False
    bos_bull: Series[bool] = False
    mss_bear: Series[bool] = False
    mss_bull: Series[bool] = False
    change: Series[bool] = False
    dwgs: Persistent[dwg] = dwg(array.new_label(), array.new_label(), array.new_line(), array.new_bool())
    snd__global__: Persistent[snd] = snd()
    def maintain(s: snd):
        __block_result_4__ = na
        if not na(s._box):
            box.set_right(s._box, time)
            line.set_x2(s._30, time)
            line.set_x2(s._50, time)
            __block_result_4__ = line.set_x2(s._70, time)
        return __block_result_4__

    maintain(snd__global__)
    if array.size(ph) > 0:
        if close > array.get(ph, 0):
            _label__0000009f__: Label = na(Label)
            _phl__0000009f__: Label = na(Label)
            if show_labels:
                save: bool = False
                if label_type == 'MSS' and (not bull):
                    save = True
                elif label_type == 'BOS' and bull:
                    save = True
                elif label_type == 'All':
                    save = True
                if save:
                    _label__0000009f__ = label.new(math.floor(math.avg(time, array.get(pht, 0))), array.get(ph, 0), 'BOS' if bull else 'MSS', xloc=xloc.bar_time, style=label.style_label_down, color=color.new('#FFFFFF00'), textcolor=na)
            if bull:
                bos_bull = True
            else:
                mss_bull = True
            if show_rets and (pb_from_high.valid == True if use_valid_pbs else True):
                snd_add(snd__global__, array.get(ph, 0), track_low, True)
            _line__0000009f__ = line.new(array.get(pht, 0), array.get(ph, 0), time, array.get(ph, 0), color=na, xloc=xloc.bar_time, style=line.style_dashed)
            bull = True
            change = True
            clear_all()
            if not na(track_low):
                if show_phl:
                    _phl__0000009f__ = label.new(time[bar_index - track_low_idx], track_low, '▲', xloc=xloc.bar_time, style=label.style_label_up, textcolor=na, color=color.new('#FFFFFF00'))
                array.unshift(pl, track_low)
                array.unshift(plt, time[bar_index - track_low_idx])
                last_high = na
            dwg_add(dwgs, _label__0000009f__, _phl__0000009f__, _line__0000009f__, bull)
    if array.size(pl) > 0:
        if close < array.get(pl, 0):
            _label__000000c0__: Label = na(Label)
            _phl__000000c0__: Label = na(Label)
            if show_labels:
                save: bool = False
                if label_type == 'MSS' and bull:
                    save = True
                elif label_type == 'BOS' and (not bull):
                    save = True
                elif label_type == 'All':
                    save = True
                if save:
                    _label__000000c0__ = label.new(math.floor(math.avg(time, array.get(plt, 0))), array.get(pl, 0), 'BOS' if not bull else 'MSS', xloc=xloc.bar_time, style=label.style_label_up, color=color.new('#FFFFFF00'), textcolor=na)
            if not bull:
                bos_bear = True
            else:
                mss_bear = True
            if show_rets and (pb_from_low.valid == True if use_valid_pbs else True):
                snd_add(snd__global__, array.get(pl, 0), track_high, False)
            _line__000000c0__ = line.new(array.get(plt, 0), array.get(pl, 0), time, array.get(pl, 0), color=na, xloc=xloc.bar_time, style=line.style_dashed)
            bull = False
            change = True
            clear_all()
            if not na(track_high):
                if show_phl:
                    _phl__000000c0__ = label.new(time[bar_index - track_high_idx], track_high, '▼', xloc=xloc.bar_time, style=label.style_label_down, textcolor=na, color=color.new('#FFFFFF00'))
                array.unshift(ph, track_high)
                array.unshift(pht, time[bar_index - track_high_idx])
                last_low = na
            dwg_add(dwgs, _label__000000c0__, _phl__000000c0__, _line__000000c0__, bull)
    if change[1]:
        if bos_bear[1] or mss_bear[1]:
            trail_price = track_high
            trail_color = ph_color
        elif bos_bull[1] or mss_bull[1]:
            trail_price = track_low
            trail_color = pl_color
        _bull__000000d5__ = array.get(dwgs._bull, 0)
        method_call('set_textcolor', array.get(dwgs._label, 0), bull_color if _bull__000000d5__ else bear_color)
        method_call('set_textcolor', array.get(dwgs._phl, 0), pl_color if _bull__000000d5__ else ph_color)
        method_call('set_color', array.get(dwgs._line, 0), bull_color if _bull__000000d5__ else bear_color)
        box.set_bgcolor(snd__global__._box, color.new(bull_color if bull else bear_color, box_transp))
        line.set_color(snd__global__._30, bull_color if _bull__000000d5__ else bear_color)
        line.set_color(snd__global__._50, bull_color if _bull__000000d5__ else bear_color)
        line.set_color(snd__global__._70, bull_color if _bull__000000d5__ else bear_color)
    barcolor((bull_color if bull else bear_color) if color_trend else na)
    plot(trail_price if trail_phl else na, color=trail_color, linewidth=math.max(1, trail_width))
    alertcondition(bos_bear[1] or bos_bull[1], 'BOS Any')
    alertcondition(mss_bear[1] or mss_bull[1], 'MSS Any')
    alertcondition(bos_bear[1], 'BOS Bear')
    alertcondition(bos_bull[1], 'BOS Bull')
    alertcondition(mss_bear[1], 'MSS Bear')
    alertcondition(mss_bull[1], 'MSS Bull')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
