"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, barcolor, barstate, chart, close, color, display, fill,
    format, high, hl2, input, label, line, low, math, na, nz, open, plot, position, script, size,
    string, ta, table, text
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series

group1: str = '    Bullish Patterns               Bearish Patterns'


@script.indicator('Candlestick Structure [LuxAlgo]', shorttitle='LuxAlgo - Candlestick Structure', overlay=True, max_labels_count=500, max_lines_count=500, na_bool=True)
def main(
    hammerTog=input.bool(True, 'Hammer                ', group=group1, inline='1'),
    ihammerTog=input.bool(True, 'Inverted Hammer   ', group=group1, inline='2'),
    bulleTog=input.bool(True, 'Bullish Engulfing    ', group=group1, inline='3'),
    r3Tog=input.bool(True, 'Rising 3                  ', group=group1, inline='4'),
    twsTog=input.bool(True, '3 White Soldiers     ', group=group1, inline='5'),
    mstarTog=input.bool(True, 'Morning Star         ', group=group1, inline='6'),
    bullhTog=input.bool(True, 'Bullish Harami      ', group=group1, inline='7'),
    btmTweezTog=input.bool(True, 'Tweezer Bottom    ', group=group1, inline='8'),
    hmanTog=input.bool(True, 'Hanging Man', group=group1, inline='1'),
    sstarTog=input.bool(True, 'Shooting Star', group=group1, inline='2'),
    beareTog=input.bool(True, 'Bearish Engulfing', group=group1, inline='3'),
    f3Tog=input.bool(True, 'Falling 3', group=group1, inline='4'),
    tbcTog=input.bool(True, '3 Black Crows', group=group1, inline='5'),
    estarTog=input.bool(True, 'Evening Star', group=group1, inline='6'),
    bearhTog=input.bool(True, 'Bearish Harami', group=group1, inline='7'),
    topTweezTog=input.bool(True, 'Tweezer Top', group=group1, inline='8'),
    minorDCLength=input.int(10, title='Minor Trend Length', group='Minor Trend', tooltip='Minor Trend determined by Donchian Channels.'),
    majorTrendType=input.string('SuperTrend', title='Major Trend Method', options=('EMA', 'ChoCh', 'SuperTrend', 'Donchian Channel'), group='Major Trend'),
    majorSwingLength=input.int(20, title='Swing Length', minval=2, group='ChoCh Parameters'),
    majorEma1Length=input.int(50, title='Short EMA Length', minval=1, group='EMA Parameters'),
    majorEma2Length=input.int(200, title='Long EMA Length', minval=1, group='EMA Parameters'),
    majorSTFactor=input.float(4, title='Super Trend Factor', group='Super Trend Parameters'),
    majorSTLength=input.int(20, title='Length', group='Super Trend Parameters'),
    majorDCLength=input.int(40, title='Donchian Channel Length', group='Donchian Channel Parameters'),
    bcTog=input.bool(False, title='Color Candles', group='Style', tooltip='Color Candles to visualize minor trend.'),
    bullColor=input.color(color.new('#089981'), title='Bull Color  ', group='Style'),
    bearColor=input.color(color.new('#F23645'), title='Bear Color', group='Style'),
    showFill=input.bool(True, title='Show Gradient', group='Style'),
    txtSize=input.string('tiny', title='Label Size', options=('tiny', 'small', 'normal', 'large', 'huge', 'auto'), group='Style', inline='3'),
    showDash=input.bool(True, 'Show Dashboard', group='Dashboard'),
    dashLoc=input.string('Bottom Right', 'Location', options=('Top Right', 'Bottom Right', 'Bottom Left'), group='Dashboard'),
    __input_31__=input.string('Tiny', 'Size', options=('Tiny', 'Small', 'Normal'), group='Dashboard')
):
    hammer_tt: str = 'The Hammer pattern appears at the bottom of a downtrend. It is identified by a small upper wick (or no upper wick) with a small body, and an elongated lower wick whose length is 2X greater than the candle body’s width.'
    ihammer_tt: str = 'The Inverted Hammer pattern appears at the bottom of a downtrend. It is identified by a small lower wick (or no lower wick) with a small body, and an elongated upper wick whose length is 2X greater than the candle body’s width.'
    hman_tt: str = 'The Hanging Man pattern appears at the top of an uptrend. It is identified by a small upper wick (or no upper wick) with a small body, and an elongated lower wick whose length is 2X greater than the candle body’s width.'
    sstar_tt: str = 'The Shooting Star pattern appears at the top of an uptrend. It is identified by a small lower wick (or no lower wick) with a small body, and an elongated upper wick whose length is 2X greater than the candle body’s width.'
    bulle_tt: str = 'The Bullish Engulfing pattern appear at the bottom of a downtrend. It is a 2 bar pattern, identified by a large bullish candle body fully encapsulating (opening lower and closing higher) the previous small (bearish) candle body.'
    beare_tt: str = 'The Bearish Engulfing pattern appear at the top of a downtrend. It is a 2 bar pattern, identified by a large bearish candle body fully encapsulating (opening higher and closing lower) the previous small (bullish) candle body.'
    r3_tt: str = 'The Rising Three Method Pattern is an indicator of continuation for the current trend. It is a 5 bar pattern, identified by an initial full-bodied bullish candle, followed by 3 bearish candles who trade within the high and low of the initial candle, followed by another full-bodied bullish candle closing above the high of the initial candle.'
    f3_tt: str = 'The Falling Three Method Pattern is an indicator of continuation for the current trend. It is a 5 bar pattern, identified by an initial full-bodied bearish candle, followed by 3 bullish candles who trade within the high and low of the initial candle, followed by another full-bodied bearish candle closing below the low of the initial candle.'
    tws_tt: str = 'The Three White Soldiers Pattern appears at the bottom of a downtrend. It is identified by 3 full-bodied bullish candles, each opening within the body and closing below the high, of the previous candle.'
    tbc_tt: str = 'The Three Black Crows Pattern appears at the top of an uptrend. It is identified by 3 full-bodied bearish candles, each open within the body and closing below the low, of the previous candle.'
    mstar_tt: str = 'The Morning Star Pattern appears at the bottom of a downtrend. It is a 3 bar pattern, identified by a full-bodied bearish candle, followed by a small-bodied bearish candle, followed by a full-bodied bullish candle that closes above the halfway point of the first candle.'
    estar_tt: str = 'The Evening Star Pattern appears at the top of an uptrend. It is a 3 bar pattern, identified by a full-bodied bullish candle, followed by a small-bodied bullish candle, followed by a full-bodied bearish candle that closes below the halfway point of the first candle.'
    bullh_tt: str = 'The Bullish Harami Pattern appears at the bottom of a downtrend. It is a 2 bar pattern, identified by an initial bearish candle, followed by a small bullish candle whose range is entirely contained within the body of the initial candle.'
    bearh_tt: str = 'The Bearish Harami Pattern appears at the top of an uptrend. It is a 2 bar pattern, identified by an initial bullish candle, followed by a small bearish candle whose range is entirely contained within the body of the initial candle.'
    tweezer_top_tt: str = 'The Tweezer Top bearish reversal candlestick pattern is identified by an initial bullish candle, followed by a bearish candle, both having equal highs.'
    tweezer_btm_tt: str = 'The Tweezer Bottom bullish reversal candlestick pattern is identified by an initial bullish candle, followed by a bearish candle, both having equal lows.'
    textSize = string.lower(__input_31__)
    invis = color.new(chart.bg_color, 100)
    def count(condition, filter):
        reversals: Persistent[int] = 0
        total: Persistent[int] = 0
        reversals = reversals + (1 if condition and filter else 0)
        total = total + (1 if condition else 0)
        return (condition and filter, reversals / total * 100, total)

    def get_st(_factor, _length):
        st, s_dir = ta.supertrend(_factor, _length)
        no_data: float = na(float)
        return (st, st, s_dir * -1)

    def get_ema(_len1, _len2):
        s_ema = ta.ema(close, _len1)
        l_ema = ta.ema(close, _len2)
        s_dir: Persistent[int] = 0
        if s_ema > l_ema:
            s_dir = 1
        if s_ema < l_ema:
            s_dir = -1
        return (s_ema, l_ema, s_dir)

    def get_dc(_length):
        upper = ta.highest(_length if _length > 0 else 1)
        lower = ta.lowest(_length if _length > 0 else 1)
        s_dir: Persistent[int] = 0
        trend_line: Persistent[float] = na(float)
        if high == upper and s_dir != 1:
            s_dir = 1
        if low == lower and s_dir != -1:
            s_dir = -1
        return (lower, upper, s_dir)

    def get_choch(len):
        os: PersistentSeries[int] = 0
        upper = ta.highest(len)
        lower = ta.lowest(len)
        os = 0 if high[len] > upper else 1 if low[len] < lower else os[1]
        top = high[len] if os == 0 and os[1] != 0 else na
        btm = low[len] if os == 1 and os[1] != 1 else na
        t = not na(top)
        b = not na(btm)
        t_val: Persistent[float] = na(float)
        b_val: Persistent[float] = na(float)
        t_bar: Persistent[int] = na(int)
        b_bar: Persistent[int] = na(int)
        t_count: Persistent[int] = 1
        b_count: Persistent[int] = 1
        if t:
            t_bar = bar_index - len
            t_val = top
            t_count = 1
        if b:
            b_bar = bar_index - len
            b_val = btm
            b_count = 1
        bull_choch = ta.crossover(close, t_val) and t_count == 1
        bear_choch = ta.crossunder(close, b_val) and b_count == 1
        rev_up: bool = False
        rev_down: bool = False
        s_dir: Persistent[int] = 0
        if bull_choch and s_dir != 1:
            line.new(t_bar, t_val, bar_index, t_val, color=bullColor, style=line.style_dashed)
            label.new(cast_int(math.avg(t_bar, bar_index)), t_val, text='ChoCh', style=label.style_label_down, color=invis, textcolor=bullColor, size=size.tiny)
            t_count = 0
            s_dir = 1
            rev_up = True
        if bear_choch and s_dir != -1:
            line.new(b_bar, b_val, bar_index, b_val, color=bearColor, style=line.style_dashed)
            label.new(cast_int(math.avg(b_bar, bar_index)), b_val, text='ChoCh', style=label.style_label_up, color=invis, textcolor=bearColor, size=size.tiny)
            b_count = 0
            s_dir = -1
            rev_down = True
        no_data: float = na(float)
        return (no_data, no_data, s_dir)

    def get_trend(_type, swingLength, ema1Length, ema2Length, STFactor, STLength, DCLength):
        __block_result__ = (na, na, na)
        if _type == 'EMA':
            __block_result__ = get_ema(ema1Length, ema2Length)
        elif _type == 'ChoCh':
            __block_result__ = get_choch(swingLength)
        elif _type == 'SuperTrend':
            __block_result__ = get_st(STFactor, STLength)
        elif _type == 'Donchian Channel':
            __block_result__ = get_dc(DCLength)
        return __block_result__

    def get_pattern_data(_signal, _bias, _dir):
        same_trend: Persistent[int] = 0
        diff_trend: Persistent[int] = 0
        if _signal and _bias == _dir:
            same_trend = same_trend + 1
        if _signal and _bias != _dir:
            diff_trend = diff_trend + 1
        total = same_trend + diff_trend
        return (same_trend / total, total)

    minor_v1, minor_v2, minor_dir = get_trend('Donchian Channel', 0, 0, 0, 0, 0, minorDCLength)
    major_v1, major_v2, major_dir = get_trend(majorTrendType, majorSwingLength, majorEma1Length, majorEma2Length, majorSTFactor, majorSTLength, majorDCLength)
    minor_bear: Series = minor_dir < 0
    minor_bull: Series = minor_dir > 0
    major_bear = major_dir < 0
    major_bull = major_dir > 0
    major_color = bearColor if major_bear else bullColor if major_bull else na
    minor_color = bearColor if minor_bear else bullColor if minor_bull else na
    major_up = major_v1 if majorTrendType == 'EMA' else major_v1 if major_bull else close
    major_down = major_v2 if majorTrendType == 'EMA' else major_v2 if major_bear else close
    major_up_col = major_color if majorTrendType == 'EMA' else major_color if major_bull else invis
    major_down_col = major_color if majorTrendType == 'EMA' else major_color if major_bear else invis
    rc: Series = close < open
    gc: Series = close > open
    c_top: Series = math.max(open, close)
    c_bot: Series = math.min(open, close)
    hl_width = high - low
    bod_width: Series = c_top - c_bot
    hw_per = (high - c_top) / hl_width * 100
    lw_per = (c_bot - low) / hl_width * 100
    b_per: Series = bod_width / hl_width * 100
    doji: Series = math.round_to_mintick(close) == math.round_to_mintick(open)
    hammer, hammer_per, hammer_count = count(lw_per > b_per * 2 and b_per < 50 and (hw_per < 2) and (not doji), minor_bear)
    inv_hammer, inv_hammer_per, inv_hammer_count = count(hw_per > b_per * 2 and b_per < 50 and (lw_per < 2) and (not doji), minor_bear)
    rising_3, rising_3_per, rising_3_count = count(gc[4] and b_per[4] > 50 and rc[3] and (c_top[3] <= high[4]) and (c_bot[3] >= low[4]) and rc[2] and (c_top[2] <= high[4]) and (c_bot[2] >= low[4]) and rc[1] and (c_top[1] <= high[4]) and (c_bot[1] >= low[4]) and gc and (close > high[4]) and (b_per > 50), minor_bull[4])
    bull_engulfing, bull_engulfing_per, bull_engulfing_count = count(rc[1] and gc and (bod_width > bod_width[1] / 2) and (open < close[1]) and (c_top > c_top[1]) and (not rising_3) and (not doji[1]), minor_bear)
    soldiers, soldiers_per, soldiers_count = count(gc[2] and b_per[2] > 70 and gc[1] and (b_per[1] > 70) and (c_bot[1] >= c_bot[2]) and (c_bot[1] <= c_top[2]) and (close[1] > high[2]) and gc and (b_per > 70) and (c_bot >= c_bot[1]) and (c_bot <= c_top[1]) and (close > high[1]), minor_bear[2])
    m_star, m_star_per, m_star_count = count(rc[2] and b_per[2] > 80 and rc[1] and (bod_width[1] < bod_width[2] / 2) and (open[1] < close[2]) and gc and (close > hl2[2]), minor_bear[2])
    bull_harami, bull_harami_per, bull_harami_count = count(gc and high <= c_top[1] and (low >= c_bot[1]) and rc[1], minor_bear[1])
    tweezer_btm, tweezer_btm_per, tweezer_btm_count = count(math.round_to_mintick(low) - math.round_to_mintick(low[1]) == 0 and gc and rc[1], minor_bear[1])
    s_star, s_star_per, s_star_count = count(hw_per > b_per * 2 and b_per < 50 and (lw_per < 2) and (not doji), minor_bull)
    h_man, h_man_per, h_man_count = count(lw_per > b_per * 2 and b_per < 50 and (hw_per < 2) and (not doji), minor_bull)
    falling_3, falling_3_per, falling_3_count = count(rc[4] and b_per[4] > 50 and gc[3] and (c_top[3] <= high[4]) and (c_bot[3] >= low[4]) and gc[2] and (c_top[2] <= high[4]) and (c_bot[2] >= low[4]) and gc[1] and (c_top[1] <= high[4]) and (c_bot[1] >= low[4]) and rc and (close < low[4]) and (b_per > 50), minor_bear[4])
    bear_engulfing, bear_engulfing_per, bear_engulfing_count = count(gc[1] and rc and (bod_width > bod_width[1] / 2) and (open > close[1]) and (c_bot < c_bot[1]) and (not falling_3) and (not doji[1]), minor_bull)
    crows, crows_per, crows_count = count(rc[2] and b_per[2] > 70 and rc[1] and (b_per[1] > 70) and (c_top[1] <= c_top[2]) and (c_top[1] >= c_bot[2]) and (close[1] < low[2]) and rc and (b_per > 70) and (c_top <= c_top[1]) and (c_top >= c_bot[1]) and (close < low[1]), minor_bull[2])
    e_star, e_star_per, e_star_count = count(gc[2] and b_per[2] > 80 and gc[1] and (bod_width[1] < bod_width[2] / 2) and (open[1] > close[2]) and rc and (close < hl2[2]), minor_bull[2])
    bear_harami, bear_harami_per, bear_harami_count = count(rc and high <= c_top[1] and (low >= c_bot[1]) and gc[1], minor_bull[1])
    tweezer_top, tweezer_top_per, tweezer_top_count = count(math.round_to_mintick(high) - math.round_to_mintick(high[1]) == 0 and rc and gc[1], minor_bull[1])
    if hammer and hammerTog and major_bull:
        label.new(bar_index, low, 'H', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=hammer_tt)
    if inv_hammer and ihammerTog and major_bull:
        label.new(bar_index, low, 'IH', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=ihammer_tt)
    if rising_3 and r3Tog and major_bull:
        label.new(bar_index, low, 'R3', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=r3_tt)
    if bull_engulfing and bulleTog and major_bull:
        label.new(bar_index, low, 'EG▲', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=bulle_tt)
    if soldiers and twsTog and major_bull:
        label.new(bar_index, low, '3WS', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=tws_tt)
    if m_star and mstarTog and major_bull:
        label.new(bar_index, low, 'MS', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=mstar_tt)
    if bull_harami and bullhTog and major_bull:
        label.new(bar_index, low, 'H▲', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=bullh_tt)
    if tweezer_btm and btmTweezTog and major_bull:
        label.new(bar_index, low, 'TB', color=NA(Color), style=label.style_label_up, textcolor=bullColor, size=txtSize, tooltip=tweezer_btm_tt)
    if s_star and sstarTog and major_bear:
        label.new(bar_index, high, 'SS', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=sstar_tt)
    if h_man and hmanTog and major_bear:
        label.new(bar_index, high, 'HM', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=hman_tt)
    if falling_3 and f3Tog and major_bear:
        label.new(bar_index, high, 'F3', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=f3_tt)
    if bear_engulfing and beareTog and major_bear:
        label.new(bar_index, high, 'EG▼', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=beare_tt)
    if bear_engulfing and beareTog and major_bear:
        label.new(bar_index, high, 'EG▼', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=beare_tt)
    if crows and tbcTog and major_bear:
        label.new(bar_index, high, '3BC', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=tbc_tt)
    if e_star and estarTog and major_bear:
        label.new(bar_index, high, 'ES', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=estar_tt)
    if bear_harami and bearhTog and major_bear:
        label.new(bar_index, high, 'H▼', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=bearh_tt)
    if tweezer_top and topTweezTog and major_bear:
        label.new(bar_index, high, 'TT', color=NA(Color), style=label.style_label_down, textcolor=bearColor, size=txtSize, tooltip=tweezer_top_tt)
    table_position: Persistent = position.bottom_left if dashLoc == 'Bottom Left' else position.top_right if dashLoc == 'Top Right' else position.bottom_right
    t: Persistent = table.new(table_position, 4, 10, bgcolor=color.new('#1E222D'), border_color=color.new('#373A46'), border_width=1, frame_color=color.new('#373A46'), frame_width=1)
    if showDash:
        method_call('merge_cells', t, 0, 0, 1, 0)
        method_call('merge_cells', t, 2, 0, 3, 0)
    if barstate.islast and showDash:
        method_call('cell', t, 0, 0, 'Bullish', text_color=color.white, bgcolor=color.new(bullColor, 50), text_size=textSize)
        method_call('cell', t, 2, 0, 'Bearish', text_color=color.white, bgcolor=color.new(bearColor, 50), text_size=textSize)
        method_call('cell', t, 0, 1, 'Pattern', text_color=color.white, text_size=textSize)
        method_call('cell', t, 1, 1, 'Alignment %', text_color=color.white, text_size=textSize)
        method_call('cell', t, 2, 1, 'Pattern', text_color=color.white, text_size=textSize)
        method_call('cell', t, 3, 1, 'Alignment %', text_color=color.white, text_size=textSize)
        if hammerTog:
            method_call('cell', t, 0, 2, 'Hammer (H)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 2, string.tostring(nz(hammer_per), format.percent), tooltip='Pattern Count:' + string.tostring(hammer_count), text_color=color.white, text_size=textSize)
        if ihammerTog:
            method_call('cell', t, 0, 3, 'Inverted Hammer (IH)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 3, string.tostring(nz(inv_hammer_per), format.percent), tooltip='Pattern Count:' + string.tostring(inv_hammer_count), text_color=color.white, text_size=textSize)
        if bulleTog:
            method_call('cell', t, 0, 4, 'Bullish Engulfing (EG▲)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 4, string.tostring(nz(bull_engulfing_per), format.percent), tooltip='Pattern Count:' + string.tostring(bull_engulfing_count), text_color=color.white, text_size=textSize)
        if r3Tog:
            method_call('cell', t, 0, 5, 'Rising 3 (R3)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 5, string.tostring(nz(rising_3_per), format.percent), tooltip='Pattern Count:' + string.tostring(rising_3_count), text_color=color.white, text_size=textSize)
        if twsTog:
            method_call('cell', t, 0, 6, '3 White Soldiers (3WS)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 6, string.tostring(nz(soldiers_per), format.percent), tooltip='Pattern Count:' + string.tostring(soldiers_count), text_color=color.white, text_size=textSize)
        if mstarTog:
            method_call('cell', t, 0, 7, 'Morning Star (MS)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 7, string.tostring(nz(m_star_per), format.percent), tooltip='Pattern Count:' + string.tostring(m_star_count), text_color=color.white, text_size=textSize)
        if bullhTog:
            method_call('cell', t, 0, 8, 'Bull Harami (H▲)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 8, string.tostring(nz(bull_harami_per), format.percent), tooltip='Pattern Count:' + string.tostring(bull_harami_count), text_color=color.white, text_size=textSize)
        if btmTweezTog:
            method_call('cell', t, 0, 9, 'Tweezer Bottom (TB)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 1, 9, string.tostring(nz(tweezer_btm_per), format.percent), tooltip='Pattern Count:' + string.tostring(tweezer_btm_count), text_color=color.white, text_size=textSize)
        if hmanTog:
            method_call('cell', t, 2, 2, 'Hanging Man (HM)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 2, string.tostring(nz(h_man_per), format.percent), tooltip='Pattern Count:' + string.tostring(h_man_count), text_color=color.white, text_size=textSize)
        if sstarTog:
            method_call('cell', t, 2, 3, 'Shooting Star (SS)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 3, string.tostring(nz(s_star_per), format.percent), tooltip='Pattern Count:' + string.tostring(s_star_count), text_color=color.white, text_size=textSize)
        if beareTog:
            method_call('cell', t, 2, 4, 'Bear Engulfing (EG▼)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 4, string.tostring(nz(bear_engulfing_per), format.percent), tooltip='Pattern Count:' + string.tostring(bear_engulfing_count), text_color=color.white, text_size=textSize)
        if f3Tog:
            method_call('cell', t, 2, 5, 'Falling 3 (F3)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 5, string.tostring(nz(falling_3_per), format.percent), tooltip='Pattern Count:' + string.tostring(falling_3_count), text_color=color.white, text_size=textSize)
        if tbcTog:
            method_call('cell', t, 2, 6, '3 Black Crows (3BC)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 6, string.tostring(nz(crows_per), format.percent), tooltip='Pattern Count:' + string.tostring(crows_count), text_color=color.white, text_size=textSize)
        if estarTog:
            method_call('cell', t, 2, 7, 'Evening Star (ES)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 7, string.tostring(nz(e_star_per), format.percent), tooltip='Pattern Count:' + string.tostring(e_star_count), text_color=color.white, text_size=textSize)
        if bearhTog:
            method_call('cell', t, 2, 8, 'Bear Harami (H▼)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 8, string.tostring(nz(bear_harami_per), format.percent), tooltip='Pattern Count:' + string.tostring(bear_harami_count), text_color=color.white, text_size=textSize)
        if topTweezTog:
            method_call('cell', t, 2, 9, 'Tweezer Top (TT)', text_halign=text.align_left, text_color=color.white, text_size=textSize)
            method_call('cell', t, 3, 9, string.tostring(nz(tweezer_top_per), format.percent), tooltip='Pattern Count:' + string.tostring(tweezer_top_count), text_color=color.white, text_size=textSize)
    ma1 = plot(major_up, color=major_up_col, title='Major Uptrend', style=plot.style_linebr, editable=False)
    ma2 = plot(major_down, color=major_down_col, title='Major Downtrend', style=plot.style_linebr, editable=False)
    fill(ma1, ma2, math.max(major_up, major_down), math.min(major_up, major_down), color.new(major_color, 90) if major_bear else invis, color.new(major_color, 90) if major_bull else invis, display=display.all if showFill else display.none)
    barcolor(minor_color if bcTog else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
