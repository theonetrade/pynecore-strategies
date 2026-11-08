"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, bgcolor, close, color, high, hl2, hlc3, input, line, location,
    low, math, na, ohlc4, open, plot, plotshape, script, shape, size, ta, time, timeframe, timenow,
    volume, xloc
)
from pynecore.types import Color, Line, NA, Persistent, Series


@script.indicator('Volume Profile Free Ultra SLI by RRB', shorttitle='VolumeProfileFree_Ultra_RRB', overlay=True, na_bool=True)
def main(
    show_levels=input(True, title='Show Plot Levels'),
    show_lines=input(True, title='Show Alternate Levels'),
    show_zero=input(True, title='Show Zero Line'),
    show_poc=input(True, title='Show POC Level'),
    show_poc2=input(True, title='Show Developing POC/VWAP Level'),
    show_va=input(True, title='Show Value Area/VWAP High/Low Levels'),
    show_cover=input(True, title='Show Side Cover'),
    dim_nva_zones=input(False, title='Dim Non Value Area Zones'),
    flip_levels=input(False, title='Flip Levels Horizontally'),
    highlight_background=input(False, title='Highlight Range Background'),
    adjust_width=input(False, title='Adjust Level Width for Log Scale'),
    buy_sell_mode=input(False, title='Horizontal Buy/Sell Mode (Num Levels/2)'),
    buy_sell_sli_mode=input(False, title='Horizontal Buy/Sell SLI Mode (Master/Slave)'),
    show_max_vol_sli=input(False, title='Vertical Max Volume SLI Mode (Master Only)'),
    max_vol_sli_src: Series[float] = input(close, title='Auto Ext Max Volume Override (Vertical SLI Mode Slave Only, Close - Disabled)'),
    max_vol_sli_ext=input.float(0, minval=0, title='Manual Ext Max Volume Override (Vertical SLI Mode Slave Only, 0 - Disabled)'),
    num_levels_=input.int(100, minval=0, maxval=100, title='Num Levels [0..100]'),
    max_level=input.float(1000, minval=0, title='Max Price Level'),
    min_level=input.float(0, minval=0, title='Min Price Level'),
    spacing=input.float(10, minval=0, title='Vertical Spacing'),
    range_1=input.int(1000, minval=0, title='VP Range Length (0 - All History)'),
    start_bar=input.int(0, minval=0, title='VP Range Start Bar (0-Based)'),
    levels_mode=input.string('va', title='Value Area/VWAP Mode', options=('va', 'vwap')),
    volume_type=input.string('total', title='Volume Type Buy/Sell/Total', options=('buy', 'sell', 'total')),
    vp_src_str=input.string('close', title='Volume Profile Source', options=('open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4')),
    vwap_src_str=input.string('hlc3', title='VWAP Source', options=('open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4')),
    vwap_len=input.int(100, minval=1, title='VWAP Length'),
    stddev=input.float(2, minval=0.1, title='VWAP Standard Deviation'),
    va_percent=input.float(70, minval=0, maxval=100, title='Value Area % Of Total Volume'),
    anchor=input.string('cur bar', title='Zero Line Anchor Point', options=('cur bar', 'range start', 'range end')),
    zero_offset=input(80, title='Zero Line Offset'),
    adj_zero_offset=input(0, title='Zero Line Offset Adjustment (Depending on Scale)'),
    cover_offset=input(0, title='Cover Offset (Relative to Zero Line)'),
    poc_offset=input(-40, title='POC Line Offset (Relative to Zero Line)'),
    va_offset=input(-40, title='VA High/Low Lines Offset (Relative to Zero Line)'),
    level_shift=input.float(50, minval=0, maxval=100, title='Level Vertical Shift % (50% - middle)'),
    line_width=input(12, title='Level Width'),
    width_multiplier=input.float(200, minval=0, title='Level Width Multiplier (Log Scale)'),
    max_deviation=input.float(2, minval=0, title='Max Level Width Deviation (Log Scale)'),
    zero_width=input(2, title='Zero Line Width'),
    cover_ext_height=input(2, title='Extend Cover by N Levels Up/Down/Right'),
    level_transp=input.int(40, minval=0, maxval=100, title='Plot Level Transparency [0..100]'),
    lines_transp=input.int(40, title='Alternate Level Transparency [0..100], step 10', options=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)),
    nva_transp=input.int(20, title='Non Value Area Level Transparency [0..100], step 10', options=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)),
    lines_col_str=input.string('', title='Alternate Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    poc_col_str=input.string('', title='POC Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    poc2_col_str=input.string('', title='Developing POC Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    va_high_col_str=input.string('', title='VA High Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    va_low_col_str=input.string('', title='VA Low Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    vwap_col_str=input.string('', title='VWAP Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    vwap_high_col_str=input.string('', title='VWAP High Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange')),
    vwap_low_col_str=input.string('', title='VWAP Low Level Color', options=('', 'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange'))
):
    lines = plot.style_line
    histogram = plot.style_histogram
    area = plot.style_area
    aqua = color.aqua
    black = color.black
    blue = color.blue
    fuchsia = color.fuchsia
    gray = color.gray
    green = color.green
    lime = color.lime
    maroon = color.maroon
    navy = color.navy
    olive = color.olive
    orange = color.orange
    purple = color.purple
    red = color.red
    silver = color.silver
    teal = color.teal
    white = color.white
    yellow = color.yellow
    interval = timeframe.multiplier
    period = timeframe.period
    isintraday = timeframe.isintraday
    isdaily = timeframe.isdaily
    isweekly = timeframe.isweekly
    ismonthly = timeframe.ismonthly
    n = bar_index
    level_color: Color = color.new('#0D68AF')
    total_color = color.new(color.new('#0D68AF'), 40)
    buy_color = green
    sell_color = red
    range_bg_color = color.new(aqua, 80)
    range_bar_color = yellow
    poc_color = black
    poc2_color = silver
    va_high_color = red
    va_low_color = green
    vwap_color = orange
    vwap_high_color = fuchsia
    vwap_low_color = lime
    zero_color = black
    nva_zone_color = white
    cover_color = white
    length: int = 100
    ext_length: int = 50
    level_style = lines
    poc_text: str = '_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _'
    text_under: str = '____________________________________________________________________________________________'
    text_upper: str = '‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
    line_block: str = '.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.'
    va_high1_text = text_under
    va_low1_text = text_under
    va_high2_text = line_block + text_under
    va_low2_text = text_upper + line_block
    def to_int(val):
        k: int = 0
        p: int = 0
        d: float = 0.0
        pow: int = 1
        s = val
        for i in pine_range(0, 9, 1):
            d = s % 10
            k = -1
            for j in pine_range(0, 9, 1):
                k = k + 1
                if j == d:
                    break
            pow = 1
            if i > 0:
                for m in pine_range(0, i - 1, 1):
                    pow = 10 * pow
            p = p + k * pow
            s = math.floor(s / 10)
            if s == 0:
                break
        return p

    def get_color(str__ren__, def__ren__):
        get_color__00000040__ = black if str__ren__ == 'black' else silver if str__ren__ == 'silver' else gray if str__ren__ == 'gray' else white if str__ren__ == 'white' else maroon if str__ren__ == 'maroon' else red if str__ren__ == 'red' else purple if str__ren__ == 'purple' else fuchsia if str__ren__ == 'fuchsia' else green if str__ren__ == 'green' else lime if str__ren__ == 'lime' else olive if str__ren__ == 'olive' else yellow if str__ren__ == 'yellow' else navy if str__ren__ == 'navy' else blue if str__ren__ == 'blue' else teal if str__ren__ == 'teal' else aqua if str__ren__ == 'aqua' else orange if str__ren__ == 'orange' else def__ren__
        return get_color__00000040__

    def color_tr(col_str, transp):
        col = NA(Color)
        if col_str == 'buy':
            col = color.new(buy_color, 0) if transp == 0 else color.new(buy_color, 10) if transp == 10 else color.new(buy_color, 20) if transp == 20 else color.new(buy_color, 30) if transp == 30 else color.new(buy_color, 40) if transp == 40 else color.new(buy_color, 50) if transp == 50 else color.new(buy_color, 60) if transp == 60 else color.new(buy_color, 70) if transp == 70 else color.new(buy_color, 80) if transp == 80 else color.new(buy_color, 90) if transp == 90 else color.new(buy_color, 100) if transp == 100 else buy_color
        if col_str == 'sell':
            col = color.new(sell_color, 0) if transp == 0 else color.new(sell_color, 10) if transp == 10 else color.new(sell_color, 20) if transp == 20 else color.new(sell_color, 30) if transp == 30 else color.new(sell_color, 40) if transp == 40 else color.new(sell_color, 50) if transp == 50 else color.new(sell_color, 60) if transp == 60 else color.new(sell_color, 70) if transp == 70 else color.new(sell_color, 80) if transp == 80 else color.new(sell_color, 90) if transp == 90 else color.new(sell_color, 100) if transp == 100 else sell_color
        if col_str == 'total':
            col = color.new(total_color, 0) if transp == 0 else color.new(total_color, 10) if transp == 10 else color.new(total_color, 20) if transp == 20 else color.new(total_color, 30) if transp == 30 else color.new(total_color, 40) if transp == 40 else color.new(total_color, 50) if transp == 50 else color.new(total_color, 60) if transp == 60 else color.new(total_color, 70) if transp == 70 else color.new(total_color, 80) if transp == 80 else color.new(total_color, 90) if transp == 90 else color.new(total_color, 100) if transp == 100 else total_color
        if col_str == 'aqua':
            col = color.new(aqua, 0) if transp == 0 else color.new(aqua, 10) if transp == 10 else color.new(aqua, 20) if transp == 20 else color.new(aqua, 30) if transp == 30 else color.new(aqua, 40) if transp == 40 else color.new(aqua, 50) if transp == 50 else color.new(aqua, 60) if transp == 60 else color.new(aqua, 70) if transp == 70 else color.new(aqua, 80) if transp == 80 else color.new(aqua, 90) if transp == 90 else color.new(aqua, 100) if transp == 100 else aqua
        if col_str == 'black':
            col = color.new(black, 0) if transp == 0 else color.new(black, 10) if transp == 10 else color.new(black, 20) if transp == 20 else color.new(black, 30) if transp == 30 else color.new(black, 40) if transp == 40 else color.new(black, 50) if transp == 50 else color.new(black, 60) if transp == 60 else color.new(black, 70) if transp == 70 else color.new(black, 80) if transp == 80 else color.new(black, 90) if transp == 90 else color.new(black, 100) if transp == 100 else black
        if col_str == 'blue':
            col = color.new(blue, 0) if transp == 0 else color.new(blue, 10) if transp == 10 else color.new(blue, 20) if transp == 20 else color.new(blue, 30) if transp == 30 else color.new(blue, 40) if transp == 40 else color.new(blue, 50) if transp == 50 else color.new(blue, 60) if transp == 60 else color.new(blue, 70) if transp == 70 else color.new(blue, 80) if transp == 80 else color.new(blue, 90) if transp == 90 else color.new(blue, 100) if transp == 100 else blue
        if col_str == 'fuchsia':
            col = color.new(fuchsia, 0) if transp == 0 else color.new(fuchsia, 10) if transp == 10 else color.new(fuchsia, 20) if transp == 20 else color.new(fuchsia, 30) if transp == 30 else color.new(fuchsia, 40) if transp == 40 else color.new(fuchsia, 50) if transp == 50 else color.new(fuchsia, 60) if transp == 60 else color.new(fuchsia, 70) if transp == 70 else color.new(fuchsia, 80) if transp == 80 else color.new(fuchsia, 90) if transp == 90 else color.new(fuchsia, 100) if transp == 100 else fuchsia
        if col_str == 'gray':
            col = color.new(gray, 0) if transp == 0 else color.new(gray, 10) if transp == 10 else color.new(gray, 20) if transp == 20 else color.new(gray, 30) if transp == 30 else color.new(gray, 40) if transp == 40 else color.new(gray, 50) if transp == 50 else color.new(gray, 60) if transp == 60 else color.new(gray, 70) if transp == 70 else color.new(gray, 80) if transp == 80 else color.new(gray, 90) if transp == 90 else color.new(gray, 100) if transp == 100 else gray
        if col_str == 'green':
            col = color.new(green, 0) if transp == 0 else color.new(green, 10) if transp == 10 else color.new(green, 20) if transp == 20 else color.new(green, 30) if transp == 30 else color.new(green, 40) if transp == 40 else color.new(green, 50) if transp == 50 else color.new(green, 60) if transp == 60 else color.new(green, 70) if transp == 70 else color.new(green, 80) if transp == 80 else color.new(green, 90) if transp == 90 else color.new(green, 100) if transp == 100 else green
        if col_str == 'lime':
            col = color.new(lime, 0) if transp == 0 else color.new(lime, 10) if transp == 10 else color.new(lime, 20) if transp == 20 else color.new(lime, 30) if transp == 30 else color.new(lime, 40) if transp == 40 else color.new(lime, 50) if transp == 50 else color.new(lime, 60) if transp == 60 else color.new(lime, 70) if transp == 70 else color.new(lime, 80) if transp == 80 else color.new(lime, 90) if transp == 90 else color.new(lime, 100) if transp == 100 else lime
        if col_str == 'maroon':
            col = color.new(maroon, 0) if transp == 0 else color.new(maroon, 10) if transp == 10 else color.new(maroon, 20) if transp == 20 else color.new(maroon, 30) if transp == 30 else color.new(maroon, 40) if transp == 40 else color.new(maroon, 50) if transp == 50 else color.new(maroon, 60) if transp == 60 else color.new(maroon, 70) if transp == 70 else color.new(maroon, 80) if transp == 80 else color.new(maroon, 90) if transp == 90 else color.new(maroon, 100) if transp == 100 else maroon
        if col_str == 'navy':
            col = color.new(navy, 0) if transp == 0 else color.new(navy, 10) if transp == 10 else color.new(navy, 20) if transp == 20 else color.new(navy, 30) if transp == 30 else color.new(navy, 40) if transp == 40 else color.new(navy, 50) if transp == 50 else color.new(navy, 60) if transp == 60 else color.new(navy, 70) if transp == 70 else color.new(navy, 80) if transp == 80 else color.new(navy, 90) if transp == 90 else color.new(navy, 100) if transp == 100 else navy
        if col_str == 'olive':
            col = color.new(olive, 0) if transp == 0 else color.new(olive, 10) if transp == 10 else color.new(olive, 20) if transp == 20 else color.new(olive, 30) if transp == 30 else color.new(olive, 40) if transp == 40 else color.new(olive, 50) if transp == 50 else color.new(olive, 60) if transp == 60 else color.new(olive, 70) if transp == 70 else color.new(olive, 80) if transp == 80 else color.new(olive, 90) if transp == 90 else color.new(olive, 100) if transp == 100 else olive
        if col_str == 'orange':
            col = color.new(orange, 0) if transp == 0 else color.new(orange, 10) if transp == 10 else color.new(orange, 20) if transp == 20 else color.new(orange, 30) if transp == 30 else color.new(orange, 40) if transp == 40 else color.new(orange, 50) if transp == 50 else color.new(orange, 60) if transp == 60 else color.new(orange, 70) if transp == 70 else color.new(orange, 80) if transp == 80 else color.new(orange, 90) if transp == 90 else color.new(orange, 100) if transp == 100 else orange
        if col_str == 'purple':
            col = color.new(purple, 0) if transp == 0 else color.new(purple, 10) if transp == 10 else color.new(purple, 20) if transp == 20 else color.new(purple, 30) if transp == 30 else color.new(purple, 40) if transp == 40 else color.new(purple, 50) if transp == 50 else color.new(purple, 60) if transp == 60 else color.new(purple, 70) if transp == 70 else color.new(purple, 80) if transp == 80 else color.new(purple, 90) if transp == 90 else color.new(purple, 100) if transp == 100 else purple
        if col_str == 'red':
            col = color.new(red, 0) if transp == 0 else color.new(red, 10) if transp == 10 else color.new(red, 20) if transp == 20 else color.new(red, 30) if transp == 30 else color.new(red, 40) if transp == 40 else color.new(red, 50) if transp == 50 else color.new(red, 60) if transp == 60 else color.new(red, 70) if transp == 70 else color.new(red, 80) if transp == 80 else color.new(red, 90) if transp == 90 else color.new(red, 100) if transp == 100 else red
        if col_str == 'silver':
            col = color.new(silver, 0) if transp == 0 else color.new(silver, 10) if transp == 10 else color.new(silver, 20) if transp == 20 else color.new(silver, 30) if transp == 30 else color.new(silver, 40) if transp == 40 else color.new(silver, 50) if transp == 50 else color.new(silver, 60) if transp == 60 else color.new(silver, 70) if transp == 70 else color.new(silver, 80) if transp == 80 else color.new(silver, 90) if transp == 90 else color.new(silver, 100) if transp == 100 else silver
        if col_str == 'teal':
            col = color.new(teal, 0) if transp == 0 else color.new(teal, 10) if transp == 10 else color.new(teal, 20) if transp == 20 else color.new(teal, 30) if transp == 30 else color.new(teal, 40) if transp == 40 else color.new(teal, 50) if transp == 50 else color.new(teal, 60) if transp == 60 else color.new(teal, 70) if transp == 70 else color.new(teal, 80) if transp == 80 else color.new(teal, 90) if transp == 90 else color.new(teal, 100) if transp == 100 else teal
        if col_str == 'white':
            col = color.new(white, 0) if transp == 0 else color.new(white, 10) if transp == 10 else color.new(white, 20) if transp == 20 else color.new(white, 30) if transp == 30 else color.new(white, 40) if transp == 40 else color.new(white, 50) if transp == 50 else color.new(white, 60) if transp == 60 else color.new(white, 70) if transp == 70 else color.new(white, 80) if transp == 80 else color.new(white, 90) if transp == 90 else color.new(white, 100) if transp == 100 else white
        if col_str == 'yellow':
            col = color.new(yellow, 0) if transp == 0 else color.new(yellow, 10) if transp == 10 else color.new(yellow, 20) if transp == 20 else color.new(yellow, 30) if transp == 30 else color.new(yellow, 40) if transp == 40 else color.new(yellow, 50) if transp == 50 else color.new(yellow, 60) if transp == 60 else color.new(yellow, 70) if transp == 70 else color.new(yellow, 80) if transp == 80 else color.new(yellow, 90) if transp == 90 else color.new(yellow, 100) if transp == 100 else yellow
        return col

    def get_src(src_str):
        res = open if src_str == 'open' else high if src_str == 'high' else low if src_str == 'low' else close if src_str == 'close' else hl2 if src_str == 'hl2' else hlc3 if src_str == 'hlc3' else ohlc4 if src_str == 'ohlc4' else na
        return res

    def tf_to_mins():
        mins = interval * 1 if isintraday else 1
        days = interval * 1 * 24 * 60 if isdaily else 1
        weeks = interval * 7 * 24 * 60 if isweekly else 1
        months = interval * 30 * 24 * 60 if ismonthly else 1
        result = mins * days * weeks * months
        return result

    vp_src = get_src(vp_src_str)
    vwap_src = get_src(vwap_src_str)
    half_levels = num_levels_ if num_levels_ <= 50 else math.floor(num_levels_ / 2)
    num_levels = half_levels if buy_sell_mode else num_levels_
    max_vol_sli_mode = max_vol_sli_ext > 0 or max_vol_sli_src != close
    max_vol_sli = max_vol_sli_ext if max_vol_sli_ext > 0 else max_vol_sli_src if max_vol_sli_src != close else 0
    bar_range = 1000 * 60 * tf_to_mins()
    total_bars = to_int(n)
    range_bars = total_bars if range_1 == 0 else range_1
    first_bar = total_bars if range_1 == 0 else start_bar + range_1
    first_time = first_bar * bar_range
    last_time = start_bar * bar_range
    time_range = timenow - time
    is_after_start = time_range <= first_time or range_1 == 0
    is_before_end = time_range > last_time
    is_in_range: Series = is_after_start and is_before_end
    range_start = is_in_range and (not is_in_range[1])
    range_start_bars = ta.barssince(range_start)
    ph = max_level
    pl = min_level
    p_range = ph - pl
    h = p_range / num_levels if num_levels > 0 else 0
    is_valid_range = is_in_range and num_levels > 0 and (min_level <= max_level)
    buy_vol1: Persistent[float] = 0.0
    buy_vol2: Persistent[float] = 0.0
    buy_vol3: Persistent[float] = 0.0
    buy_vol4: Persistent[float] = 0.0
    buy_vol5: Persistent[float] = 0.0
    buy_vol6: Persistent[float] = 0.0
    buy_vol7: Persistent[float] = 0.0
    buy_vol8: Persistent[float] = 0.0
    buy_vol9: Persistent[float] = 0.0
    buy_vol10: Persistent[float] = 0.0
    buy_vol11: Persistent[float] = 0.0
    buy_vol12: Persistent[float] = 0.0
    buy_vol13: Persistent[float] = 0.0
    buy_vol14: Persistent[float] = 0.0
    buy_vol15: Persistent[float] = 0.0
    buy_vol16: Persistent[float] = 0.0
    buy_vol17: Persistent[float] = 0.0
    buy_vol18: Persistent[float] = 0.0
    buy_vol19: Persistent[float] = 0.0
    buy_vol20: Persistent[float] = 0.0
    buy_vol21: Persistent[float] = 0.0
    buy_vol22: Persistent[float] = 0.0
    buy_vol23: Persistent[float] = 0.0
    buy_vol24: Persistent[float] = 0.0
    buy_vol25: Persistent[float] = 0.0
    buy_vol26: Persistent[float] = 0.0
    buy_vol27: Persistent[float] = 0.0
    buy_vol28: Persistent[float] = 0.0
    buy_vol29: Persistent[float] = 0.0
    buy_vol30: Persistent[float] = 0.0
    buy_vol31: Persistent[float] = 0.0
    buy_vol32: Persistent[float] = 0.0
    buy_vol33: Persistent[float] = 0.0
    buy_vol34: Persistent[float] = 0.0
    buy_vol35: Persistent[float] = 0.0
    buy_vol36: Persistent[float] = 0.0
    buy_vol37: Persistent[float] = 0.0
    buy_vol38: Persistent[float] = 0.0
    buy_vol39: Persistent[float] = 0.0
    buy_vol40: Persistent[float] = 0.0
    buy_vol41: Persistent[float] = 0.0
    buy_vol42: Persistent[float] = 0.0
    buy_vol43: Persistent[float] = 0.0
    buy_vol44: Persistent[float] = 0.0
    buy_vol45: Persistent[float] = 0.0
    buy_vol46: Persistent[float] = 0.0
    buy_vol47: Persistent[float] = 0.0
    buy_vol48: Persistent[float] = 0.0
    buy_vol49: Persistent[float] = 0.0
    buy_vol50: Persistent[float] = 0.0
    buy_vol51: Persistent[float] = 0.0
    buy_vol52: Persistent[float] = 0.0
    buy_vol53: Persistent[float] = 0.0
    buy_vol54: Persistent[float] = 0.0
    buy_vol55: Persistent[float] = 0.0
    buy_vol56: Persistent[float] = 0.0
    buy_vol57: Persistent[float] = 0.0
    buy_vol58: Persistent[float] = 0.0
    buy_vol59: Persistent[float] = 0.0
    buy_vol60: Persistent[float] = 0.0
    buy_vol61: Persistent[float] = 0.0
    buy_vol62: Persistent[float] = 0.0
    buy_vol63: Persistent[float] = 0.0
    buy_vol64: Persistent[float] = 0.0
    buy_vol65: Persistent[float] = 0.0
    buy_vol66: Persistent[float] = 0.0
    buy_vol67: Persistent[float] = 0.0
    buy_vol68: Persistent[float] = 0.0
    buy_vol69: Persistent[float] = 0.0
    buy_vol70: Persistent[float] = 0.0
    buy_vol71: Persistent[float] = 0.0
    buy_vol72: Persistent[float] = 0.0
    buy_vol73: Persistent[float] = 0.0
    buy_vol74: Persistent[float] = 0.0
    buy_vol75: Persistent[float] = 0.0
    buy_vol76: Persistent[float] = 0.0
    buy_vol77: Persistent[float] = 0.0
    buy_vol78: Persistent[float] = 0.0
    buy_vol79: Persistent[float] = 0.0
    buy_vol80: Persistent[float] = 0.0
    buy_vol81: Persistent[float] = 0.0
    buy_vol82: Persistent[float] = 0.0
    buy_vol83: Persistent[float] = 0.0
    buy_vol84: Persistent[float] = 0.0
    buy_vol85: Persistent[float] = 0.0
    buy_vol86: Persistent[float] = 0.0
    buy_vol87: Persistent[float] = 0.0
    buy_vol88: Persistent[float] = 0.0
    buy_vol89: Persistent[float] = 0.0
    buy_vol90: Persistent[float] = 0.0
    buy_vol91: Persistent[float] = 0.0
    buy_vol92: Persistent[float] = 0.0
    buy_vol93: Persistent[float] = 0.0
    buy_vol94: Persistent[float] = 0.0
    buy_vol95: Persistent[float] = 0.0
    buy_vol96: Persistent[float] = 0.0
    buy_vol97: Persistent[float] = 0.0
    buy_vol98: Persistent[float] = 0.0
    buy_vol99: Persistent[float] = 0.0
    buy_vol100: Persistent[float] = 0.0
    sell_vol1: Persistent[float] = 0.0
    sell_vol2: Persistent[float] = 0.0
    sell_vol3: Persistent[float] = 0.0
    sell_vol4: Persistent[float] = 0.0
    sell_vol5: Persistent[float] = 0.0
    sell_vol6: Persistent[float] = 0.0
    sell_vol7: Persistent[float] = 0.0
    sell_vol8: Persistent[float] = 0.0
    sell_vol9: Persistent[float] = 0.0
    sell_vol10: Persistent[float] = 0.0
    sell_vol11: Persistent[float] = 0.0
    sell_vol12: Persistent[float] = 0.0
    sell_vol13: Persistent[float] = 0.0
    sell_vol14: Persistent[float] = 0.0
    sell_vol15: Persistent[float] = 0.0
    sell_vol16: Persistent[float] = 0.0
    sell_vol17: Persistent[float] = 0.0
    sell_vol18: Persistent[float] = 0.0
    sell_vol19: Persistent[float] = 0.0
    sell_vol20: Persistent[float] = 0.0
    sell_vol21: Persistent[float] = 0.0
    sell_vol22: Persistent[float] = 0.0
    sell_vol23: Persistent[float] = 0.0
    sell_vol24: Persistent[float] = 0.0
    sell_vol25: Persistent[float] = 0.0
    sell_vol26: Persistent[float] = 0.0
    sell_vol27: Persistent[float] = 0.0
    sell_vol28: Persistent[float] = 0.0
    sell_vol29: Persistent[float] = 0.0
    sell_vol30: Persistent[float] = 0.0
    sell_vol31: Persistent[float] = 0.0
    sell_vol32: Persistent[float] = 0.0
    sell_vol33: Persistent[float] = 0.0
    sell_vol34: Persistent[float] = 0.0
    sell_vol35: Persistent[float] = 0.0
    sell_vol36: Persistent[float] = 0.0
    sell_vol37: Persistent[float] = 0.0
    sell_vol38: Persistent[float] = 0.0
    sell_vol39: Persistent[float] = 0.0
    sell_vol40: Persistent[float] = 0.0
    sell_vol41: Persistent[float] = 0.0
    sell_vol42: Persistent[float] = 0.0
    sell_vol43: Persistent[float] = 0.0
    sell_vol44: Persistent[float] = 0.0
    sell_vol45: Persistent[float] = 0.0
    sell_vol46: Persistent[float] = 0.0
    sell_vol47: Persistent[float] = 0.0
    sell_vol48: Persistent[float] = 0.0
    sell_vol49: Persistent[float] = 0.0
    sell_vol50: Persistent[float] = 0.0
    sell_vol51: Persistent[float] = 0.0
    sell_vol52: Persistent[float] = 0.0
    sell_vol53: Persistent[float] = 0.0
    sell_vol54: Persistent[float] = 0.0
    sell_vol55: Persistent[float] = 0.0
    sell_vol56: Persistent[float] = 0.0
    sell_vol57: Persistent[float] = 0.0
    sell_vol58: Persistent[float] = 0.0
    sell_vol59: Persistent[float] = 0.0
    sell_vol60: Persistent[float] = 0.0
    sell_vol61: Persistent[float] = 0.0
    sell_vol62: Persistent[float] = 0.0
    sell_vol63: Persistent[float] = 0.0
    sell_vol64: Persistent[float] = 0.0
    sell_vol65: Persistent[float] = 0.0
    sell_vol66: Persistent[float] = 0.0
    sell_vol67: Persistent[float] = 0.0
    sell_vol68: Persistent[float] = 0.0
    sell_vol69: Persistent[float] = 0.0
    sell_vol70: Persistent[float] = 0.0
    sell_vol71: Persistent[float] = 0.0
    sell_vol72: Persistent[float] = 0.0
    sell_vol73: Persistent[float] = 0.0
    sell_vol74: Persistent[float] = 0.0
    sell_vol75: Persistent[float] = 0.0
    sell_vol76: Persistent[float] = 0.0
    sell_vol77: Persistent[float] = 0.0
    sell_vol78: Persistent[float] = 0.0
    sell_vol79: Persistent[float] = 0.0
    sell_vol80: Persistent[float] = 0.0
    sell_vol81: Persistent[float] = 0.0
    sell_vol82: Persistent[float] = 0.0
    sell_vol83: Persistent[float] = 0.0
    sell_vol84: Persistent[float] = 0.0
    sell_vol85: Persistent[float] = 0.0
    sell_vol86: Persistent[float] = 0.0
    sell_vol87: Persistent[float] = 0.0
    sell_vol88: Persistent[float] = 0.0
    sell_vol89: Persistent[float] = 0.0
    sell_vol90: Persistent[float] = 0.0
    sell_vol91: Persistent[float] = 0.0
    sell_vol92: Persistent[float] = 0.0
    sell_vol93: Persistent[float] = 0.0
    sell_vol94: Persistent[float] = 0.0
    sell_vol95: Persistent[float] = 0.0
    sell_vol96: Persistent[float] = 0.0
    sell_vol97: Persistent[float] = 0.0
    sell_vol98: Persistent[float] = 0.0
    sell_vol99: Persistent[float] = 0.0
    sell_vol100: Persistent[float] = 0.0
    k: int = na(int)
    if is_valid_range:
        price = vp_src
        is_valid_price = (min_level == 0 or (min_level > 0 and min_level <= price)) and (max_level == 0 or (max_level > 0 and price <= max_level))
        if is_valid_price:
            k = math.floor((price - pl) / h) + 1
        if not na(k):
            dir__000001a3__ = math.sign(close - open)
            if k == 1:
                buy_vol1 = buy_vol1 + volume if dir__000001a3__ >= 0 else buy_vol1
                sell_vol1 = sell_vol1 + volume if dir__000001a3__ < 0 else sell_vol1
            if k == 2:
                buy_vol2 = buy_vol2 + volume if dir__000001a3__ >= 0 else buy_vol2
                sell_vol2 = sell_vol2 + volume if dir__000001a3__ < 0 else sell_vol2
            if k == 3:
                buy_vol3 = buy_vol3 + volume if dir__000001a3__ >= 0 else buy_vol3
                sell_vol3 = sell_vol3 + volume if dir__000001a3__ < 0 else sell_vol3
            if k == 4:
                buy_vol4 = buy_vol4 + volume if dir__000001a3__ >= 0 else buy_vol4
                sell_vol4 = sell_vol4 + volume if dir__000001a3__ < 0 else sell_vol4
            if k == 5:
                buy_vol5 = buy_vol5 + volume if dir__000001a3__ >= 0 else buy_vol5
                sell_vol5 = sell_vol5 + volume if dir__000001a3__ < 0 else sell_vol5
            if k == 6:
                buy_vol6 = buy_vol6 + volume if dir__000001a3__ >= 0 else buy_vol6
                sell_vol6 = sell_vol6 + volume if dir__000001a3__ < 0 else sell_vol6
            if k == 7:
                buy_vol7 = buy_vol7 + volume if dir__000001a3__ >= 0 else buy_vol7
                sell_vol7 = sell_vol7 + volume if dir__000001a3__ < 0 else sell_vol7
            if k == 8:
                buy_vol8 = buy_vol8 + volume if dir__000001a3__ >= 0 else buy_vol8
                sell_vol8 = sell_vol8 + volume if dir__000001a3__ < 0 else sell_vol8
            if k == 9:
                buy_vol9 = buy_vol9 + volume if dir__000001a3__ >= 0 else buy_vol9
                sell_vol9 = sell_vol9 + volume if dir__000001a3__ < 0 else sell_vol9
            if k == 10:
                buy_vol10 = buy_vol10 + volume if dir__000001a3__ >= 0 else buy_vol10
                sell_vol10 = sell_vol10 + volume if dir__000001a3__ < 0 else sell_vol10
            if k == 11:
                buy_vol11 = buy_vol11 + volume if dir__000001a3__ >= 0 else buy_vol11
                sell_vol11 = sell_vol11 + volume if dir__000001a3__ < 0 else sell_vol11
            if k == 12:
                buy_vol12 = buy_vol12 + volume if dir__000001a3__ >= 0 else buy_vol12
                sell_vol12 = sell_vol12 + volume if dir__000001a3__ < 0 else sell_vol12
            if k == 13:
                buy_vol13 = buy_vol13 + volume if dir__000001a3__ >= 0 else buy_vol13
                sell_vol13 = sell_vol13 + volume if dir__000001a3__ < 0 else sell_vol13
            if k == 14:
                buy_vol14 = buy_vol14 + volume if dir__000001a3__ >= 0 else buy_vol14
                sell_vol14 = sell_vol14 + volume if dir__000001a3__ < 0 else sell_vol14
            if k == 15:
                buy_vol15 = buy_vol15 + volume if dir__000001a3__ >= 0 else buy_vol15
                sell_vol15 = sell_vol15 + volume if dir__000001a3__ < 0 else sell_vol15
            if k == 16:
                buy_vol16 = buy_vol16 + volume if dir__000001a3__ >= 0 else buy_vol16
                sell_vol16 = sell_vol16 + volume if dir__000001a3__ < 0 else sell_vol16
            if k == 17:
                buy_vol17 = buy_vol17 + volume if dir__000001a3__ >= 0 else buy_vol17
                sell_vol17 = sell_vol17 + volume if dir__000001a3__ < 0 else sell_vol17
            if k == 18:
                buy_vol18 = buy_vol18 + volume if dir__000001a3__ >= 0 else buy_vol18
                sell_vol18 = sell_vol18 + volume if dir__000001a3__ < 0 else sell_vol18
            if k == 19:
                buy_vol19 = buy_vol19 + volume if dir__000001a3__ >= 0 else buy_vol19
                sell_vol19 = sell_vol19 + volume if dir__000001a3__ < 0 else sell_vol19
            if k == 20:
                buy_vol20 = buy_vol20 + volume if dir__000001a3__ >= 0 else buy_vol20
                sell_vol20 = sell_vol20 + volume if dir__000001a3__ < 0 else sell_vol20
            if k == 21:
                buy_vol21 = buy_vol21 + volume if dir__000001a3__ >= 0 else buy_vol21
                sell_vol21 = sell_vol21 + volume if dir__000001a3__ < 0 else sell_vol21
            if k == 22:
                buy_vol22 = buy_vol22 + volume if dir__000001a3__ >= 0 else buy_vol22
                sell_vol22 = sell_vol22 + volume if dir__000001a3__ < 0 else sell_vol22
            if k == 23:
                buy_vol23 = buy_vol23 + volume if dir__000001a3__ >= 0 else buy_vol23
                sell_vol23 = sell_vol23 + volume if dir__000001a3__ < 0 else sell_vol23
            if k == 24:
                buy_vol24 = buy_vol24 + volume if dir__000001a3__ >= 0 else buy_vol24
                sell_vol24 = sell_vol24 + volume if dir__000001a3__ < 0 else sell_vol24
            if k == 25:
                buy_vol25 = buy_vol25 + volume if dir__000001a3__ >= 0 else buy_vol25
                sell_vol25 = sell_vol25 + volume if dir__000001a3__ < 0 else sell_vol25
            if k == 26:
                buy_vol26 = buy_vol26 + volume if dir__000001a3__ >= 0 else buy_vol26
                sell_vol26 = sell_vol26 + volume if dir__000001a3__ < 0 else sell_vol26
            if k == 27:
                buy_vol27 = buy_vol27 + volume if dir__000001a3__ >= 0 else buy_vol27
                sell_vol27 = sell_vol27 + volume if dir__000001a3__ < 0 else sell_vol27
            if k == 28:
                buy_vol28 = buy_vol28 + volume if dir__000001a3__ >= 0 else buy_vol28
                sell_vol28 = sell_vol28 + volume if dir__000001a3__ < 0 else sell_vol28
            if k == 29:
                buy_vol29 = buy_vol29 + volume if dir__000001a3__ >= 0 else buy_vol29
                sell_vol29 = sell_vol29 + volume if dir__000001a3__ < 0 else sell_vol29
            if k == 30:
                buy_vol30 = buy_vol30 + volume if dir__000001a3__ >= 0 else buy_vol30
                sell_vol30 = sell_vol30 + volume if dir__000001a3__ < 0 else sell_vol30
            if k == 31:
                buy_vol31 = buy_vol31 + volume if dir__000001a3__ >= 0 else buy_vol31
                sell_vol31 = sell_vol31 + volume if dir__000001a3__ < 0 else sell_vol31
            if k == 32:
                buy_vol32 = buy_vol32 + volume if dir__000001a3__ >= 0 else buy_vol32
                sell_vol32 = sell_vol32 + volume if dir__000001a3__ < 0 else sell_vol32
            if k == 33:
                buy_vol33 = buy_vol33 + volume if dir__000001a3__ >= 0 else buy_vol33
                sell_vol33 = sell_vol33 + volume if dir__000001a3__ < 0 else sell_vol33
            if k == 34:
                buy_vol34 = buy_vol34 + volume if dir__000001a3__ >= 0 else buy_vol34
                sell_vol34 = sell_vol34 + volume if dir__000001a3__ < 0 else sell_vol34
            if k == 35:
                buy_vol35 = buy_vol35 + volume if dir__000001a3__ >= 0 else buy_vol35
                sell_vol35 = sell_vol35 + volume if dir__000001a3__ < 0 else sell_vol35
            if k == 36:
                buy_vol36 = buy_vol36 + volume if dir__000001a3__ >= 0 else buy_vol36
                sell_vol36 = sell_vol36 + volume if dir__000001a3__ < 0 else sell_vol36
            if k == 37:
                buy_vol37 = buy_vol37 + volume if dir__000001a3__ >= 0 else buy_vol37
                sell_vol37 = sell_vol37 + volume if dir__000001a3__ < 0 else sell_vol37
            if k == 38:
                buy_vol38 = buy_vol38 + volume if dir__000001a3__ >= 0 else buy_vol38
                sell_vol38 = sell_vol38 + volume if dir__000001a3__ < 0 else sell_vol38
            if k == 39:
                buy_vol39 = buy_vol39 + volume if dir__000001a3__ >= 0 else buy_vol39
                sell_vol39 = sell_vol39 + volume if dir__000001a3__ < 0 else sell_vol39
            if k == 40:
                buy_vol40 = buy_vol40 + volume if dir__000001a3__ >= 0 else buy_vol40
                sell_vol40 = sell_vol40 + volume if dir__000001a3__ < 0 else sell_vol40
            if k == 41:
                buy_vol41 = buy_vol41 + volume if dir__000001a3__ >= 0 else buy_vol41
                sell_vol41 = sell_vol41 + volume if dir__000001a3__ < 0 else sell_vol41
            if k == 42:
                buy_vol42 = buy_vol42 + volume if dir__000001a3__ >= 0 else buy_vol42
                sell_vol42 = sell_vol42 + volume if dir__000001a3__ < 0 else sell_vol42
            if k == 43:
                buy_vol43 = buy_vol43 + volume if dir__000001a3__ >= 0 else buy_vol43
                sell_vol43 = sell_vol43 + volume if dir__000001a3__ < 0 else sell_vol43
            if k == 44:
                buy_vol44 = buy_vol44 + volume if dir__000001a3__ >= 0 else buy_vol44
                sell_vol44 = sell_vol44 + volume if dir__000001a3__ < 0 else sell_vol44
            if k == 45:
                buy_vol45 = buy_vol45 + volume if dir__000001a3__ >= 0 else buy_vol45
                sell_vol45 = sell_vol45 + volume if dir__000001a3__ < 0 else sell_vol45
            if k == 46:
                buy_vol46 = buy_vol46 + volume if dir__000001a3__ >= 0 else buy_vol46
                sell_vol46 = sell_vol46 + volume if dir__000001a3__ < 0 else sell_vol46
            if k == 47:
                buy_vol47 = buy_vol47 + volume if dir__000001a3__ >= 0 else buy_vol47
                sell_vol47 = sell_vol47 + volume if dir__000001a3__ < 0 else sell_vol47
            if k == 48:
                buy_vol48 = buy_vol48 + volume if dir__000001a3__ >= 0 else buy_vol48
                sell_vol48 = sell_vol48 + volume if dir__000001a3__ < 0 else sell_vol48
            if k == 49:
                buy_vol49 = buy_vol49 + volume if dir__000001a3__ >= 0 else buy_vol49
                sell_vol49 = sell_vol49 + volume if dir__000001a3__ < 0 else sell_vol49
            if k == 50:
                buy_vol50 = buy_vol50 + volume if dir__000001a3__ >= 0 else buy_vol50
                sell_vol50 = sell_vol50 + volume if dir__000001a3__ < 0 else sell_vol50
            if k == 51:
                buy_vol51 = buy_vol51 + volume if dir__000001a3__ >= 0 else buy_vol51
                sell_vol51 = sell_vol51 + volume if dir__000001a3__ < 0 else sell_vol51
            if k == 52:
                buy_vol52 = buy_vol52 + volume if dir__000001a3__ >= 0 else buy_vol52
                sell_vol52 = sell_vol52 + volume if dir__000001a3__ < 0 else sell_vol52
            if k == 53:
                buy_vol53 = buy_vol53 + volume if dir__000001a3__ >= 0 else buy_vol53
                sell_vol53 = sell_vol53 + volume if dir__000001a3__ < 0 else sell_vol53
            if k == 54:
                buy_vol54 = buy_vol54 + volume if dir__000001a3__ >= 0 else buy_vol54
                sell_vol54 = sell_vol54 + volume if dir__000001a3__ < 0 else sell_vol54
            if k == 55:
                buy_vol55 = buy_vol55 + volume if dir__000001a3__ >= 0 else buy_vol55
                sell_vol55 = sell_vol55 + volume if dir__000001a3__ < 0 else sell_vol55
            if k == 56:
                buy_vol56 = buy_vol56 + volume if dir__000001a3__ >= 0 else buy_vol56
                sell_vol56 = sell_vol56 + volume if dir__000001a3__ < 0 else sell_vol56
            if k == 57:
                buy_vol57 = buy_vol57 + volume if dir__000001a3__ >= 0 else buy_vol57
                sell_vol57 = sell_vol57 + volume if dir__000001a3__ < 0 else sell_vol57
            if k == 58:
                buy_vol58 = buy_vol58 + volume if dir__000001a3__ >= 0 else buy_vol58
                sell_vol58 = sell_vol58 + volume if dir__000001a3__ < 0 else sell_vol58
            if k == 59:
                buy_vol59 = buy_vol59 + volume if dir__000001a3__ >= 0 else buy_vol59
                sell_vol59 = sell_vol59 + volume if dir__000001a3__ < 0 else sell_vol59
            if k == 60:
                buy_vol60 = buy_vol60 + volume if dir__000001a3__ >= 0 else buy_vol60
                sell_vol60 = sell_vol60 + volume if dir__000001a3__ < 0 else sell_vol60
            if k == 61:
                buy_vol61 = buy_vol61 + volume if dir__000001a3__ >= 0 else buy_vol61
                sell_vol61 = sell_vol61 + volume if dir__000001a3__ < 0 else sell_vol61
            if k == 62:
                buy_vol62 = buy_vol62 + volume if dir__000001a3__ >= 0 else buy_vol62
                sell_vol62 = sell_vol62 + volume if dir__000001a3__ < 0 else sell_vol62
            if k == 63:
                buy_vol63 = buy_vol63 + volume if dir__000001a3__ >= 0 else buy_vol63
                sell_vol63 = sell_vol63 + volume if dir__000001a3__ < 0 else sell_vol63
            if k == 64:
                buy_vol64 = buy_vol64 + volume if dir__000001a3__ >= 0 else buy_vol64
                sell_vol64 = sell_vol64 + volume if dir__000001a3__ < 0 else sell_vol64
            if k == 65:
                buy_vol65 = buy_vol65 + volume if dir__000001a3__ >= 0 else buy_vol65
                sell_vol65 = sell_vol65 + volume if dir__000001a3__ < 0 else sell_vol65
            if k == 66:
                buy_vol66 = buy_vol66 + volume if dir__000001a3__ >= 0 else buy_vol66
                sell_vol66 = sell_vol66 + volume if dir__000001a3__ < 0 else sell_vol66
            if k == 67:
                buy_vol67 = buy_vol67 + volume if dir__000001a3__ >= 0 else buy_vol67
                sell_vol67 = sell_vol67 + volume if dir__000001a3__ < 0 else sell_vol67
            if k == 68:
                buy_vol68 = buy_vol68 + volume if dir__000001a3__ >= 0 else buy_vol68
                sell_vol68 = sell_vol68 + volume if dir__000001a3__ < 0 else sell_vol68
            if k == 69:
                buy_vol69 = buy_vol69 + volume if dir__000001a3__ >= 0 else buy_vol69
                sell_vol69 = sell_vol69 + volume if dir__000001a3__ < 0 else sell_vol69
            if k == 70:
                buy_vol70 = buy_vol70 + volume if dir__000001a3__ >= 0 else buy_vol70
                sell_vol70 = sell_vol70 + volume if dir__000001a3__ < 0 else sell_vol70
            if k == 71:
                buy_vol71 = buy_vol71 + volume if dir__000001a3__ >= 0 else buy_vol71
                sell_vol71 = sell_vol71 + volume if dir__000001a3__ < 0 else sell_vol71
            if k == 72:
                buy_vol72 = buy_vol72 + volume if dir__000001a3__ >= 0 else buy_vol72
                sell_vol72 = sell_vol72 + volume if dir__000001a3__ < 0 else sell_vol72
            if k == 73:
                buy_vol73 = buy_vol73 + volume if dir__000001a3__ >= 0 else buy_vol73
                sell_vol73 = sell_vol73 + volume if dir__000001a3__ < 0 else sell_vol73
            if k == 74:
                buy_vol74 = buy_vol74 + volume if dir__000001a3__ >= 0 else buy_vol74
                sell_vol74 = sell_vol74 + volume if dir__000001a3__ < 0 else sell_vol74
            if k == 75:
                buy_vol75 = buy_vol75 + volume if dir__000001a3__ >= 0 else buy_vol75
                sell_vol75 = sell_vol75 + volume if dir__000001a3__ < 0 else sell_vol75
            if k == 76:
                buy_vol76 = buy_vol76 + volume if dir__000001a3__ >= 0 else buy_vol76
                sell_vol76 = sell_vol76 + volume if dir__000001a3__ < 0 else sell_vol76
            if k == 77:
                buy_vol77 = buy_vol77 + volume if dir__000001a3__ >= 0 else buy_vol77
                sell_vol77 = sell_vol77 + volume if dir__000001a3__ < 0 else sell_vol77
            if k == 78:
                buy_vol78 = buy_vol78 + volume if dir__000001a3__ >= 0 else buy_vol78
                sell_vol78 = sell_vol78 + volume if dir__000001a3__ < 0 else sell_vol78
            if k == 79:
                buy_vol79 = buy_vol79 + volume if dir__000001a3__ >= 0 else buy_vol79
                sell_vol79 = sell_vol79 + volume if dir__000001a3__ < 0 else sell_vol79
            if k == 80:
                buy_vol80 = buy_vol80 + volume if dir__000001a3__ >= 0 else buy_vol80
                sell_vol80 = sell_vol80 + volume if dir__000001a3__ < 0 else sell_vol80
            if k == 81:
                buy_vol81 = buy_vol81 + volume if dir__000001a3__ >= 0 else buy_vol81
                sell_vol81 = sell_vol81 + volume if dir__000001a3__ < 0 else sell_vol81
            if k == 82:
                buy_vol82 = buy_vol82 + volume if dir__000001a3__ >= 0 else buy_vol82
                sell_vol82 = sell_vol82 + volume if dir__000001a3__ < 0 else sell_vol82
            if k == 83:
                buy_vol83 = buy_vol83 + volume if dir__000001a3__ >= 0 else buy_vol83
                sell_vol83 = sell_vol83 + volume if dir__000001a3__ < 0 else sell_vol83
            if k == 84:
                buy_vol84 = buy_vol84 + volume if dir__000001a3__ >= 0 else buy_vol84
                sell_vol84 = sell_vol84 + volume if dir__000001a3__ < 0 else sell_vol84
            if k == 85:
                buy_vol85 = buy_vol85 + volume if dir__000001a3__ >= 0 else buy_vol85
                sell_vol85 = sell_vol85 + volume if dir__000001a3__ < 0 else sell_vol85
            if k == 86:
                buy_vol86 = buy_vol86 + volume if dir__000001a3__ >= 0 else buy_vol86
                sell_vol86 = sell_vol86 + volume if dir__000001a3__ < 0 else sell_vol86
            if k == 87:
                buy_vol87 = buy_vol87 + volume if dir__000001a3__ >= 0 else buy_vol87
                sell_vol87 = sell_vol87 + volume if dir__000001a3__ < 0 else sell_vol87
            if k == 88:
                buy_vol88 = buy_vol88 + volume if dir__000001a3__ >= 0 else buy_vol88
                sell_vol88 = sell_vol88 + volume if dir__000001a3__ < 0 else sell_vol88
            if k == 89:
                buy_vol89 = buy_vol89 + volume if dir__000001a3__ >= 0 else buy_vol89
                sell_vol89 = sell_vol89 + volume if dir__000001a3__ < 0 else sell_vol89
            if k == 90:
                buy_vol90 = buy_vol90 + volume if dir__000001a3__ >= 0 else buy_vol90
                sell_vol90 = sell_vol90 + volume if dir__000001a3__ < 0 else sell_vol90
            if k == 91:
                buy_vol91 = buy_vol91 + volume if dir__000001a3__ >= 0 else buy_vol91
                sell_vol91 = sell_vol91 + volume if dir__000001a3__ < 0 else sell_vol91
            if k == 92:
                buy_vol92 = buy_vol92 + volume if dir__000001a3__ >= 0 else buy_vol92
                sell_vol92 = sell_vol92 + volume if dir__000001a3__ < 0 else sell_vol92
            if k == 93:
                buy_vol93 = buy_vol93 + volume if dir__000001a3__ >= 0 else buy_vol93
                sell_vol93 = sell_vol93 + volume if dir__000001a3__ < 0 else sell_vol93
            if k == 94:
                buy_vol94 = buy_vol94 + volume if dir__000001a3__ >= 0 else buy_vol94
                sell_vol94 = sell_vol94 + volume if dir__000001a3__ < 0 else sell_vol94
            if k == 95:
                buy_vol95 = buy_vol95 + volume if dir__000001a3__ >= 0 else buy_vol95
                sell_vol95 = sell_vol95 + volume if dir__000001a3__ < 0 else sell_vol95
            if k == 96:
                buy_vol96 = buy_vol96 + volume if dir__000001a3__ >= 0 else buy_vol96
                sell_vol96 = sell_vol96 + volume if dir__000001a3__ < 0 else sell_vol96
            if k == 97:
                buy_vol97 = buy_vol97 + volume if dir__000001a3__ >= 0 else buy_vol97
                sell_vol97 = sell_vol97 + volume if dir__000001a3__ < 0 else sell_vol97
            if k == 98:
                buy_vol98 = buy_vol98 + volume if dir__000001a3__ >= 0 else buy_vol98
                sell_vol98 = sell_vol98 + volume if dir__000001a3__ < 0 else sell_vol98
            if k == 99:
                buy_vol99 = buy_vol99 + volume if dir__000001a3__ >= 0 else buy_vol99
                sell_vol99 = sell_vol99 + volume if dir__000001a3__ < 0 else sell_vol99
            if k == 100:
                buy_vol100 = buy_vol100 + volume if dir__000001a3__ >= 0 else buy_vol100
                sell_vol100 = sell_vol100 + volume if dir__000001a3__ < 0 else sell_vol100
    def buy_volumes1(group):
        res = buy_vol1 if group == 1 else buy_vol2 if group == 2 else buy_vol3 if group == 3 else buy_vol4 if group == 4 else buy_vol5 if group == 5 else buy_vol6 if group == 6 else buy_vol7 if group == 7 else buy_vol8 if group == 8 else buy_vol9 if group == 9 else buy_vol10 if group == 10 else buy_vol11 if group == 11 else buy_vol12 if group == 12 else buy_vol13 if group == 13 else buy_vol14 if group == 14 else buy_vol15 if group == 15 else buy_vol16 if group == 16 else buy_vol17 if group == 17 else buy_vol18 if group == 18 else buy_vol19 if group == 19 else buy_vol20 if group == 20 else buy_vol21 if group == 21 else buy_vol22 if group == 22 else buy_vol23 if group == 23 else buy_vol24 if group == 24 else buy_vol25 if group == 25 else buy_vol26 if group == 26 else buy_vol27 if group == 27 else buy_vol28 if group == 28 else buy_vol29 if group == 29 else buy_vol30 if group == 30 else buy_vol31 if group == 31 else buy_vol32 if group == 32 else buy_vol33 if group == 33 else buy_vol34 if group == 34 else buy_vol35 if group == 35 else buy_vol36 if group == 36 else buy_vol37 if group == 37 else buy_vol38 if group == 38 else buy_vol39 if group == 39 else buy_vol40 if group == 40 else buy_vol41 if group == 41 else buy_vol42 if group == 42 else buy_vol43 if group == 43 else buy_vol44 if group == 44 else buy_vol45 if group == 45 else buy_vol46 if group == 46 else buy_vol47 if group == 47 else buy_vol48 if group == 48 else buy_vol49 if group == 49 else buy_vol50 if group == 50 else 0.0
        return res

    def buy_volumes2(group):
        res = buy_vol51 if group == 51 else buy_vol52 if group == 52 else buy_vol53 if group == 53 else buy_vol54 if group == 54 else buy_vol55 if group == 55 else buy_vol56 if group == 56 else buy_vol57 if group == 57 else buy_vol58 if group == 58 else buy_vol59 if group == 59 else buy_vol60 if group == 60 else buy_vol61 if group == 61 else buy_vol62 if group == 62 else buy_vol63 if group == 63 else buy_vol64 if group == 64 else buy_vol65 if group == 65 else buy_vol66 if group == 66 else buy_vol67 if group == 67 else buy_vol68 if group == 68 else buy_vol69 if group == 69 else buy_vol70 if group == 70 else buy_vol71 if group == 71 else buy_vol72 if group == 72 else buy_vol73 if group == 73 else buy_vol74 if group == 74 else buy_vol75 if group == 75 else buy_vol76 if group == 76 else buy_vol77 if group == 77 else buy_vol78 if group == 78 else buy_vol79 if group == 79 else buy_vol80 if group == 80 else buy_vol81 if group == 81 else buy_vol82 if group == 82 else buy_vol83 if group == 83 else buy_vol84 if group == 84 else buy_vol85 if group == 85 else buy_vol86 if group == 86 else buy_vol87 if group == 87 else buy_vol88 if group == 88 else buy_vol89 if group == 89 else buy_vol90 if group == 90 else buy_vol91 if group == 91 else buy_vol92 if group == 92 else buy_vol93 if group == 93 else buy_vol94 if group == 94 else buy_vol95 if group == 95 else buy_vol96 if group == 96 else buy_vol97 if group == 97 else buy_vol98 if group == 98 else buy_vol99 if group == 99 else buy_vol100 if group == 100 else 0.0
        return res

    def sell_volumes1(group):
        res = sell_vol1 if group == 1 else sell_vol2 if group == 2 else sell_vol3 if group == 3 else sell_vol4 if group == 4 else sell_vol5 if group == 5 else sell_vol6 if group == 6 else sell_vol7 if group == 7 else sell_vol8 if group == 8 else sell_vol9 if group == 9 else sell_vol10 if group == 10 else sell_vol11 if group == 11 else sell_vol12 if group == 12 else sell_vol13 if group == 13 else sell_vol14 if group == 14 else sell_vol15 if group == 15 else sell_vol16 if group == 16 else sell_vol17 if group == 17 else sell_vol18 if group == 18 else sell_vol19 if group == 19 else sell_vol20 if group == 20 else sell_vol21 if group == 21 else sell_vol22 if group == 22 else sell_vol23 if group == 23 else sell_vol24 if group == 24 else sell_vol25 if group == 25 else sell_vol26 if group == 26 else sell_vol27 if group == 27 else sell_vol28 if group == 28 else sell_vol29 if group == 29 else sell_vol30 if group == 30 else sell_vol31 if group == 31 else sell_vol32 if group == 32 else sell_vol33 if group == 33 else sell_vol34 if group == 34 else sell_vol35 if group == 35 else sell_vol36 if group == 36 else sell_vol37 if group == 37 else sell_vol38 if group == 38 else sell_vol39 if group == 39 else sell_vol40 if group == 40 else sell_vol41 if group == 41 else sell_vol42 if group == 42 else sell_vol43 if group == 43 else sell_vol44 if group == 44 else sell_vol45 if group == 45 else sell_vol46 if group == 46 else sell_vol47 if group == 47 else sell_vol48 if group == 48 else sell_vol49 if group == 49 else sell_vol50 if group == 50 else 0.0
        return res

    def sell_volumes2(group):
        res = sell_vol51 if group == 51 else sell_vol52 if group == 52 else sell_vol53 if group == 53 else sell_vol54 if group == 54 else sell_vol55 if group == 55 else sell_vol56 if group == 56 else sell_vol57 if group == 57 else sell_vol58 if group == 58 else sell_vol59 if group == 59 else sell_vol60 if group == 60 else sell_vol61 if group == 61 else sell_vol62 if group == 62 else sell_vol63 if group == 63 else sell_vol64 if group == 64 else sell_vol65 if group == 65 else sell_vol66 if group == 66 else sell_vol67 if group == 67 else sell_vol68 if group == 68 else sell_vol69 if group == 69 else sell_vol70 if group == 70 else sell_vol71 if group == 71 else sell_vol72 if group == 72 else sell_vol73 if group == 73 else sell_vol74 if group == 74 else sell_vol75 if group == 75 else sell_vol76 if group == 76 else sell_vol77 if group == 77 else sell_vol78 if group == 78 else sell_vol79 if group == 79 else sell_vol80 if group == 80 else sell_vol81 if group == 81 else sell_vol82 if group == 82 else sell_vol83 if group == 83 else sell_vol84 if group == 84 else sell_vol85 if group == 85 else sell_vol86 if group == 86 else sell_vol87 if group == 87 else sell_vol88 if group == 88 else sell_vol89 if group == 89 else sell_vol90 if group == 90 else sell_vol91 if group == 91 else sell_vol92 if group == 92 else sell_vol93 if group == 93 else sell_vol94 if group == 94 else sell_vol95 if group == 95 else sell_vol96 if group == 96 else sell_vol97 if group == 97 else sell_vol98 if group == 98 else sell_vol99 if group == 99 else sell_vol100 if group == 100 else 0.0
        return res

    max_vol = max_vol_sli
    max_buy_vol: float = 0.0
    max_sell_vol: float = 0.0
    max_vol2: float = 0.0
    total_vol: float = 0.0
    poc_index: int = 0
    poc2_index: int = 0
    poc_level: float = 0.0
    poc2_level: float = 0.0
    shift = level_shift / 100 * h
    if is_after_start and (not max_vol_sli_mode):
        a = 1 if volume_type == 'total' or buy_sell_sli_mode or buy_sell_mode else 1 if volume_type == 'buy' else 0 if volume_type == 'sell' else 0
        b = 1 if volume_type == 'total' or buy_sell_sli_mode or buy_sell_mode else 0 if volume_type == 'buy' else 1 if volume_type == 'sell' else 0
        for i in pine_range(1, num_levels, 1):
            bv = buy_volumes1(i) if i <= 50 else buy_volumes2(i)
            if max_buy_vol < bv:
                max_buy_vol = bv
            sv = sell_volumes1(i) if i <= 50 else sell_volumes2(i)
            if max_sell_vol < sv:
                max_sell_vol = sv
            vol = a * bv + b * sv
            total_vol = total_vol + vol
            if max_vol2 < vol:
                if max_vol < vol:
                    max_vol2 = max_vol
                    poc2_index = poc_index
                    max_vol = vol
                    poc_index = i
                else:
                    max_vol2 = vol
                    poc2_index = i
        poc_level = pl + (poc_index - 1) * h + shift
        poc2_level = pl + (poc2_index - 1) * h + shift if poc2_index > 0 else 0.0
    va_limit = total_vol * va_percent / 100
    mid_index = num_levels / 2
    va_vol = max_vol
    va_high = poc_index
    va_low = poc_index
    va_high_level: float = 0.0
    va_low_level: float = 0.0
    if is_after_start and (not max_vol_sli_mode) and (va_vol > 0):
        for i in pine_range(1, num_levels, 1):
            buy_vol_vh1 = buy_volumes1(va_high + 1) if va_high + 1 <= 50 else buy_volumes2(va_high + 1)
            buy_vol_vh2 = buy_volumes1(va_high + 2) if va_high + 2 <= 50 else buy_volumes2(va_high + 2)
            sell_vol_vh1 = sell_volumes1(va_high + 1) if va_high + 1 <= 50 else sell_volumes2(va_high + 1)
            sell_vol_vh2 = sell_volumes1(va_high + 2) if va_high + 2 <= 50 else sell_volumes2(va_high + 2)
            buy_vol_vl1 = buy_volumes1(va_low - 1) if va_low - 1 <= 50 else buy_volumes2(va_low - 1)
            buy_vol_vl2 = buy_volumes1(va_low - 2) if va_low - 2 <= 50 else buy_volumes2(va_low - 2)
            sell_vol_vl1 = sell_volumes1(va_low - 1) if va_low - 1 <= 50 else sell_volumes2(va_low - 1)
            sell_vol_vl2 = sell_volumes1(va_low - 2) if va_low - 2 <= 50 else sell_volumes2(va_low - 2)
            above_vol = buy_vol_vh1 + sell_vol_vh1 + buy_vol_vh2 + sell_vol_vh2
            below_vol = buy_vol_vl1 + sell_vol_vl1 + buy_vol_vl2 + sell_vol_vl2
            if va_high <= num_levels:
                if above_vol > below_vol or (above_vol == below_vol and math.abs(va_high + 2 - mid_index) <= math.abs(va_low - 2 - mid_index)):
                    va_high = va_high + 2
                    va_vol = va_vol + above_vol
            if va_low > 0:
                if above_vol < below_vol or (above_vol == below_vol and math.abs(va_high + 2 - mid_index) > math.abs(va_low - 2 - mid_index)):
                    va_low = va_low - 2
                    va_vol = va_vol + below_vol
            if va_vol >= va_limit or (va_low <= 0 and va_high > num_levels):
                break
        va_high = num_levels if va_high > num_levels else va_high
        va_low = 1 if va_low <= 0 else va_low
        va_high_level = pl + va_high * h - spacing
        va_low_level = pl + (va_low - 1) * h - spacing
    vwap_level = ta.vwap(vwap_src)
    vwap_stdev = ta.stdev(vwap_src, vwap_len) * stddev
    vwap_up = vwap_level + vwap_stdev
    vwap_down = vwap_level - vwap_stdev
    if levels_mode == 'vwap':
        poc2_level = vwap_level
        va_high_level = vwap_up
        va_low_level = vwap_down
    def get_len(index, buy_vol, sell_vol):
        a = 1 if volume_type == 'buy' else (1 if buy_sell_sli_mode else 0) if volume_type == 'sell' else 1 if volume_type == 'total' else 0
        b = 0 if volume_type == 'buy' else 1 if volume_type == 'sell' else 1 if volume_type == 'total' else 0
        if buy_sell_mode:
            if index <= num_levels:
                a = 1
                b = 0 if volume_type == 'sell' else 1
            if index > num_levels:
                a = 1
                b = 1 if volume_type == 'sell' else 0
        res = a * buy_vol + b * sell_vol
        len = math.round(res / max_vol * length) if max_vol > 0 else 0
        return len

    len1 = get_len(1, buy_vol1, sell_vol1)
    len2 = get_len(2, buy_vol2, sell_vol2)
    len3 = get_len(3, buy_vol3, sell_vol3)
    len4 = get_len(4, buy_vol4, sell_vol4)
    len5 = get_len(5, buy_vol5, sell_vol5)
    len6 = get_len(6, buy_vol6, sell_vol6)
    len7 = get_len(7, buy_vol7, sell_vol7)
    len8 = get_len(8, buy_vol8, sell_vol8)
    len9 = get_len(9, buy_vol9, sell_vol9)
    len10 = get_len(10, buy_vol10, sell_vol10)
    len11 = get_len(11, buy_vol11, sell_vol11)
    len12 = get_len(12, buy_vol12, sell_vol12)
    len13 = get_len(13, buy_vol13, sell_vol13)
    len14 = get_len(14, buy_vol14, sell_vol14)
    len15 = get_len(15, buy_vol15, sell_vol15)
    len16 = get_len(16, buy_vol16, sell_vol16)
    len17 = get_len(17, buy_vol17, sell_vol17)
    len18 = get_len(18, buy_vol18, sell_vol18)
    len19 = get_len(19, buy_vol19, sell_vol19)
    len20 = get_len(20, buy_vol20, sell_vol20)
    len21 = get_len(21, buy_vol21, sell_vol21)
    len22 = get_len(22, buy_vol22, sell_vol22)
    len23 = get_len(23, buy_vol23, sell_vol23)
    len24 = get_len(24, buy_vol24, sell_vol24)
    len25 = get_len(25, buy_vol25, sell_vol25)
    len26 = get_len(26, buy_vol26, sell_vol26)
    len27 = get_len(27, buy_vol27, sell_vol27)
    len28 = get_len(28, buy_vol28, sell_vol28)
    len29 = get_len(29, buy_vol29, sell_vol29)
    len30 = get_len(30, buy_vol30, sell_vol30)
    len31 = get_len(31, buy_vol31, sell_vol31)
    len32 = get_len(32, buy_vol32, sell_vol32)
    len33 = get_len(33, buy_vol33, sell_vol33)
    len34 = get_len(34, buy_vol34, sell_vol34)
    len35 = get_len(35, buy_vol35, sell_vol35)
    len36 = get_len(36, buy_vol36, sell_vol36)
    len37 = get_len(37, buy_vol37, sell_vol37)
    len38 = get_len(38, buy_vol38, sell_vol38)
    len39 = get_len(39, buy_vol39, sell_vol39)
    len40 = get_len(40, buy_vol40, sell_vol40)
    len41 = get_len(41, buy_vol41, sell_vol41)
    len42 = get_len(42, buy_vol42, sell_vol42)
    len43 = get_len(43, buy_vol43, sell_vol43)
    len44 = get_len(44, buy_vol44, sell_vol44)
    len45 = get_len(45, buy_vol45, sell_vol45)
    len46 = get_len(46, buy_vol46, sell_vol46)
    len47 = get_len(47, buy_vol47, sell_vol47)
    len48 = get_len(48, buy_vol48, sell_vol48)
    len49 = get_len(49, buy_vol49, sell_vol49)
    len50 = get_len(50, buy_vol50, sell_vol50)
    len51 = get_len(51, buy_vol51, sell_vol51) if not buy_sell_mode else get_len(51, buy_vol1, sell_vol1)
    len52 = get_len(52, buy_vol52, sell_vol52) if not buy_sell_mode else get_len(52, buy_vol2, sell_vol2)
    len53 = get_len(53, buy_vol53, sell_vol53) if not buy_sell_mode else get_len(53, buy_vol3, sell_vol3)
    len54 = get_len(54, buy_vol54, sell_vol54) if not buy_sell_mode else get_len(54, buy_vol4, sell_vol4)
    len55 = get_len(55, buy_vol55, sell_vol55) if not buy_sell_mode else get_len(55, buy_vol5, sell_vol5)
    len56 = get_len(56, buy_vol56, sell_vol56) if not buy_sell_mode else get_len(56, buy_vol6, sell_vol6)
    len57 = get_len(57, buy_vol57, sell_vol57) if not buy_sell_mode else get_len(57, buy_vol7, sell_vol7)
    len58 = get_len(58, buy_vol58, sell_vol58) if not buy_sell_mode else get_len(58, buy_vol8, sell_vol8)
    len59 = get_len(59, buy_vol59, sell_vol59) if not buy_sell_mode else get_len(59, buy_vol9, sell_vol9)
    len60 = get_len(60, buy_vol60, sell_vol60) if not buy_sell_mode else get_len(60, buy_vol10, sell_vol10)
    len61 = get_len(61, buy_vol61, sell_vol61) if not buy_sell_mode else get_len(61, buy_vol11, sell_vol11)
    len62 = get_len(62, buy_vol62, sell_vol62) if not buy_sell_mode else get_len(62, buy_vol12, sell_vol12)
    len63 = get_len(63, buy_vol63, sell_vol63) if not buy_sell_mode else get_len(63, buy_vol13, sell_vol13)
    len64 = get_len(64, buy_vol64, sell_vol64) if not buy_sell_mode else get_len(64, buy_vol14, sell_vol14)
    len65 = get_len(65, buy_vol65, sell_vol65) if not buy_sell_mode else get_len(65, buy_vol15, sell_vol15)
    len66 = get_len(66, buy_vol66, sell_vol66) if not buy_sell_mode else get_len(66, buy_vol16, sell_vol16)
    len67 = get_len(67, buy_vol67, sell_vol67) if not buy_sell_mode else get_len(67, buy_vol17, sell_vol17)
    len68 = get_len(68, buy_vol68, sell_vol68) if not buy_sell_mode else get_len(68, buy_vol18, sell_vol18)
    len69 = get_len(69, buy_vol69, sell_vol69) if not buy_sell_mode else get_len(69, buy_vol19, sell_vol19)
    len70 = get_len(70, buy_vol70, sell_vol70) if not buy_sell_mode else get_len(70, buy_vol20, sell_vol20)
    len71 = get_len(71, buy_vol71, sell_vol71) if not buy_sell_mode else get_len(71, buy_vol21, sell_vol21)
    len72 = get_len(72, buy_vol72, sell_vol72) if not buy_sell_mode else get_len(72, buy_vol22, sell_vol22)
    len73 = get_len(73, buy_vol73, sell_vol73) if not buy_sell_mode else get_len(73, buy_vol23, sell_vol23)
    len74 = get_len(74, buy_vol74, sell_vol74) if not buy_sell_mode else get_len(74, buy_vol24, sell_vol24)
    len75 = get_len(75, buy_vol75, sell_vol75) if not buy_sell_mode else get_len(75, buy_vol25, sell_vol25)
    len76 = get_len(76, buy_vol76, sell_vol76) if not buy_sell_mode else get_len(76, buy_vol26, sell_vol26)
    len77 = get_len(77, buy_vol77, sell_vol77) if not buy_sell_mode else get_len(77, buy_vol27, sell_vol27)
    len78 = get_len(78, buy_vol78, sell_vol78) if not buy_sell_mode else get_len(78, buy_vol28, sell_vol28)
    len79 = get_len(79, buy_vol79, sell_vol79) if not buy_sell_mode else get_len(79, buy_vol29, sell_vol29)
    len80 = get_len(80, buy_vol80, sell_vol80) if not buy_sell_mode else get_len(80, buy_vol30, sell_vol30)
    len81 = get_len(81, buy_vol81, sell_vol81) if not buy_sell_mode else get_len(81, buy_vol31, sell_vol31)
    len82 = get_len(82, buy_vol82, sell_vol82) if not buy_sell_mode else get_len(82, buy_vol32, sell_vol32)
    len83 = get_len(83, buy_vol83, sell_vol83) if not buy_sell_mode else get_len(83, buy_vol33, sell_vol33)
    len84 = get_len(84, buy_vol84, sell_vol84) if not buy_sell_mode else get_len(84, buy_vol34, sell_vol34)
    len85 = get_len(85, buy_vol85, sell_vol85) if not buy_sell_mode else get_len(85, buy_vol35, sell_vol35)
    len86 = get_len(86, buy_vol86, sell_vol86) if not buy_sell_mode else get_len(86, buy_vol36, sell_vol36)
    len87 = get_len(87, buy_vol87, sell_vol87) if not buy_sell_mode else get_len(87, buy_vol37, sell_vol37)
    len88 = get_len(88, buy_vol88, sell_vol88) if not buy_sell_mode else get_len(88, buy_vol38, sell_vol38)
    len89 = get_len(89, buy_vol89, sell_vol89) if not buy_sell_mode else get_len(89, buy_vol39, sell_vol39)
    len90 = get_len(90, buy_vol90, sell_vol90) if not buy_sell_mode else get_len(90, buy_vol40, sell_vol40)
    len91 = get_len(91, buy_vol91, sell_vol91) if not buy_sell_mode else get_len(91, buy_vol41, sell_vol41)
    len92 = get_len(92, buy_vol92, sell_vol92) if not buy_sell_mode else get_len(92, buy_vol42, sell_vol42)
    len93 = get_len(93, buy_vol93, sell_vol93) if not buy_sell_mode else get_len(93, buy_vol43, sell_vol43)
    len94 = get_len(94, buy_vol94, sell_vol94) if not buy_sell_mode else get_len(94, buy_vol44, sell_vol44)
    len95 = get_len(95, buy_vol95, sell_vol95) if not buy_sell_mode else get_len(95, buy_vol45, sell_vol45)
    len96 = get_len(96, buy_vol96, sell_vol96) if not buy_sell_mode else get_len(96, buy_vol46, sell_vol46)
    len97 = get_len(97, buy_vol97, sell_vol97) if not buy_sell_mode else get_len(97, buy_vol47, sell_vol47)
    len98 = get_len(98, buy_vol98, sell_vol98) if not buy_sell_mode else get_len(98, buy_vol48, sell_vol48)
    len99 = get_len(99, buy_vol99, sell_vol99) if not buy_sell_mode else get_len(99, buy_vol49, sell_vol49)
    len100 = get_len(100, buy_vol100, sell_vol100) if not buy_sell_mode else get_len(100, buy_vol50, sell_vol50)
    level1 = pl + 0 * h + shift
    level2 = pl + 1 * h + shift
    level3 = pl + 2 * h + shift
    level4 = pl + 3 * h + shift
    level5 = pl + 4 * h + shift
    level6 = pl + 5 * h + shift
    level7 = pl + 6 * h + shift
    level8 = pl + 7 * h + shift
    level9 = pl + 8 * h + shift
    level10 = pl + 9 * h + shift
    level11 = pl + 10 * h + shift
    level12 = pl + 11 * h + shift
    level13 = pl + 12 * h + shift
    level14 = pl + 13 * h + shift
    level15 = pl + 14 * h + shift
    level16 = pl + 15 * h + shift
    level17 = pl + 16 * h + shift
    level18 = pl + 17 * h + shift
    level19 = pl + 18 * h + shift
    level20 = pl + 19 * h + shift
    level21 = pl + 20 * h + shift
    level22 = pl + 21 * h + shift
    level23 = pl + 22 * h + shift
    level24 = pl + 23 * h + shift
    level25 = pl + 24 * h + shift
    level26 = pl + 25 * h + shift
    level27 = pl + 26 * h + shift
    level28 = pl + 27 * h + shift
    level29 = pl + 28 * h + shift
    level30 = pl + 29 * h + shift
    level31 = pl + 30 * h + shift
    level32 = pl + 31 * h + shift
    level33 = pl + 32 * h + shift
    level34 = pl + 33 * h + shift
    level35 = pl + 34 * h + shift
    level36 = pl + 35 * h + shift
    level37 = pl + 36 * h + shift
    level38 = pl + 37 * h + shift
    level39 = pl + 38 * h + shift
    level40 = pl + 39 * h + shift
    level41 = pl + 40 * h + shift
    level42 = pl + 41 * h + shift
    level43 = pl + 42 * h + shift
    level44 = pl + 43 * h + shift
    level45 = pl + 44 * h + shift
    level46 = pl + 45 * h + shift
    level47 = pl + 46 * h + shift
    level48 = pl + 47 * h + shift
    level49 = pl + 48 * h + shift
    level50 = pl + 49 * h + shift
    level51 = pl + 50 * h + shift
    def get_level(index):
        level = pl + (index - 1) * h + shift if not buy_sell_mode or (buy_sell_mode and index <= 50) else pl + (index - 51) * h + shift
        return level

    dir = 1 if flip_levels else -1
    first_bar_offset = total_bars if range_1 == 0 else range_start_bars
    last_bar_offset = range_start_bars - range_bars + 1 if range_start_bars >= range_bars else 0
    range_offset = 0 if anchor == 'cur bar' else last_bar_offset if anchor == 'range start' else first_bar_offset
    z_offset = zero_offset - range_offset
    l_offset = z_offset - 1 if dir == 1 else z_offset + length
    adj_z_offset = z_offset - dir * adj_zero_offset
    cover_length = length + ext_length
    c_offset = z_offset if dir == 1 else z_offset + cover_length - 1
    c_offset = c_offset - dir * cover_offset
    poc_offset = z_offset - dir * poc_offset
    va_offset = z_offset - dir * va_offset
    def get_offset(len):
        dir = 1 if flip_levels else -1
        res = l_offset + dir * len
        return res

    w = line_width * width_multiplier if adjust_width else line_width
    line_width1_ = math.abs(math.floor((1 - math.abs(math.log10(level1) / math.log10(level2))) * w)) if adjust_width else math.floor(w)
    line_width2 = math.abs(math.floor((1 - math.abs(math.log10(level2) / math.log10(level3))) * w)) if adjust_width else math.floor(w)
    line_width2_ = math.floor(line_width2 * max_deviation)
    line_width1 = line_width1_ if line_width1_ > 0 else line_width2_
    line_width3 = math.abs(math.floor((1 - math.abs(math.log10(level3) / math.log10(level4))) * w)) if adjust_width else math.floor(w)
    line_width4 = math.abs(math.floor((1 - math.abs(math.log10(level4) / math.log10(level5))) * w)) if adjust_width else math.floor(w)
    line_width5 = math.abs(math.floor((1 - math.abs(math.log10(level5) / math.log10(level6))) * w)) if adjust_width else math.floor(w)
    line_width6 = math.abs(math.floor((1 - math.abs(math.log10(level6) / math.log10(level7))) * w)) if adjust_width else math.floor(w)
    line_width7 = math.abs(math.floor((1 - math.abs(math.log10(level7) / math.log10(level8))) * w)) if adjust_width else math.floor(w)
    line_width8 = math.abs(math.floor((1 - math.abs(math.log10(level8) / math.log10(level9))) * w)) if adjust_width else math.floor(w)
    line_width9 = math.abs(math.floor((1 - math.abs(math.log10(level9) / math.log10(level10))) * w)) if adjust_width else math.floor(w)
    line_width10 = math.abs(math.floor((1 - math.abs(math.log10(level10) / math.log10(level11))) * w)) if adjust_width else math.floor(w)
    line_width11 = math.abs(math.floor((1 - math.abs(math.log10(level11) / math.log10(level12))) * w)) if adjust_width else math.floor(w)
    line_width12 = math.abs(math.floor((1 - math.abs(math.log10(level12) / math.log10(level13))) * w)) if adjust_width else math.floor(w)
    line_width13 = math.abs(math.floor((1 - math.abs(math.log10(level13) / math.log10(level14))) * w)) if adjust_width else math.floor(w)
    line_width14 = math.abs(math.floor((1 - math.abs(math.log10(level14) / math.log10(level15))) * w)) if adjust_width else math.floor(w)
    line_width15 = math.abs(math.floor((1 - math.abs(math.log10(level15) / math.log10(level16))) * w)) if adjust_width else math.floor(w)
    line_width16 = math.abs(math.floor((1 - math.abs(math.log10(level16) / math.log10(level17))) * w)) if adjust_width else math.floor(w)
    line_width17 = math.abs(math.floor((1 - math.abs(math.log10(level17) / math.log10(level18))) * w)) if adjust_width else math.floor(w)
    line_width18 = math.abs(math.floor((1 - math.abs(math.log10(level18) / math.log10(level19))) * w)) if adjust_width else math.floor(w)
    line_width19 = math.abs(math.floor((1 - math.abs(math.log10(level19) / math.log10(level20))) * w)) if adjust_width else math.floor(w)
    line_width20 = math.abs(math.floor((1 - math.abs(math.log10(level20) / math.log10(level21))) * w)) if adjust_width else math.floor(w)
    line_width21 = math.abs(math.floor((1 - math.abs(math.log10(level21) / math.log10(level22))) * w)) if adjust_width else math.floor(w)
    line_width22 = math.abs(math.floor((1 - math.abs(math.log10(level22) / math.log10(level23))) * w)) if adjust_width else math.floor(w)
    line_width23 = math.abs(math.floor((1 - math.abs(math.log10(level23) / math.log10(level24))) * w)) if adjust_width else math.floor(w)
    line_width24 = math.abs(math.floor((1 - math.abs(math.log10(level24) / math.log10(level25))) * w)) if adjust_width else math.floor(w)
    line_width25 = math.abs(math.floor((1 - math.abs(math.log10(level25) / math.log10(level26))) * w)) if adjust_width else math.floor(w)
    line_width26 = math.abs(math.floor((1 - math.abs(math.log10(level26) / math.log10(level27))) * w)) if adjust_width else math.floor(w)
    line_width27 = math.abs(math.floor((1 - math.abs(math.log10(level27) / math.log10(level28))) * w)) if adjust_width else math.floor(w)
    line_width28 = math.abs(math.floor((1 - math.abs(math.log10(level28) / math.log10(level29))) * w)) if adjust_width else math.floor(w)
    line_width29 = math.abs(math.floor((1 - math.abs(math.log10(level29) / math.log10(level30))) * w)) if adjust_width else math.floor(w)
    line_width30 = math.abs(math.floor((1 - math.abs(math.log10(level30) / math.log10(level31))) * w)) if adjust_width else math.floor(w)
    line_width31 = math.abs(math.floor((1 - math.abs(math.log10(level31) / math.log10(level32))) * w)) if adjust_width else math.floor(w)
    line_width32 = math.abs(math.floor((1 - math.abs(math.log10(level32) / math.log10(level33))) * w)) if adjust_width else math.floor(w)
    line_width33 = math.abs(math.floor((1 - math.abs(math.log10(level33) / math.log10(level34))) * w)) if adjust_width else math.floor(w)
    line_width34 = math.abs(math.floor((1 - math.abs(math.log10(level34) / math.log10(level35))) * w)) if adjust_width else math.floor(w)
    line_width35 = math.abs(math.floor((1 - math.abs(math.log10(level35) / math.log10(level36))) * w)) if adjust_width else math.floor(w)
    line_width36 = math.abs(math.floor((1 - math.abs(math.log10(level36) / math.log10(level37))) * w)) if adjust_width else math.floor(w)
    line_width37 = math.abs(math.floor((1 - math.abs(math.log10(level37) / math.log10(level38))) * w)) if adjust_width else math.floor(w)
    line_width38 = math.abs(math.floor((1 - math.abs(math.log10(level38) / math.log10(level39))) * w)) if adjust_width else math.floor(w)
    line_width39 = math.abs(math.floor((1 - math.abs(math.log10(level39) / math.log10(level40))) * w)) if adjust_width else math.floor(w)
    line_width40 = math.abs(math.floor((1 - math.abs(math.log10(level40) / math.log10(level41))) * w)) if adjust_width else math.floor(w)
    line_width41 = math.abs(math.floor((1 - math.abs(math.log10(level41) / math.log10(level42))) * w)) if adjust_width else math.floor(w)
    line_width42 = math.abs(math.floor((1 - math.abs(math.log10(level42) / math.log10(level43))) * w)) if adjust_width else math.floor(w)
    line_width43 = math.abs(math.floor((1 - math.abs(math.log10(level43) / math.log10(level44))) * w)) if adjust_width else math.floor(w)
    line_width44 = math.abs(math.floor((1 - math.abs(math.log10(level44) / math.log10(level45))) * w)) if adjust_width else math.floor(w)
    line_width45 = math.abs(math.floor((1 - math.abs(math.log10(level45) / math.log10(level46))) * w)) if adjust_width else math.floor(w)
    line_width46 = math.abs(math.floor((1 - math.abs(math.log10(level46) / math.log10(level47))) * w)) if adjust_width else math.floor(w)
    line_width47 = math.abs(math.floor((1 - math.abs(math.log10(level47) / math.log10(level48))) * w)) if adjust_width else math.floor(w)
    line_width48 = math.abs(math.floor((1 - math.abs(math.log10(level48) / math.log10(level49))) * w)) if adjust_width else math.floor(w)
    line_width49 = math.abs(math.floor((1 - math.abs(math.log10(level49) / math.log10(level50))) * w)) if adjust_width else math.floor(w)
    line_width50 = math.abs(math.floor((1 - math.abs(math.log10(level50) / math.log10(level51))) * w)) if adjust_width else math.floor(w)
    def width_ratio(level1, level2):
        res = math.abs(math.floor((1 - math.abs(math.log10(level1) / math.log10(level2))) * w)) if adjust_width else math.floor(w)
        return res

    def get_width(index):
        l1a = index
        l2a = l1a + 1
        l3a = l1a + 2
        level1a = get_level(l1a)
        level2a = get_level(l2a)
        level3a = get_level(l3a)
        width1_ = width_ratio(level1a, level2a)
        width2 = width_ratio(level2a, level3a)
        width2_ = math.floor(width2 * max_deviation)
        adj_width1 = width1_ if not na(width1_) else width2_
        adj_width2: int = 0
        if index > 50:
            l1b = index - 50
            l2b = l1b + 1
            l3b = l1b + 2
            level1b = get_level(l1b)
            level2b = get_level(l2b)
            level3b = get_level(l3b)
            if buy_sell_mode and index == 100:
                level2b = level51
            width3_ = width_ratio(level1b, level2b)
            width4 = width_ratio(level2b, level3b)
            width4_ = math.floor(width4 * max_deviation)
            adj_width2 = width3_ if not na(width3_) else width4_
        width = adj_width1 if not buy_sell_mode else adj_width2
        return width

    plot(level1 if show_levels and num_levels >= 1 else na, title='Volume 1', style=level_style, linewidth=math.max(1, line_width1), color=level_color, offset=get_offset(len1), show_last=length)
    plot(level2 if show_levels and num_levels >= 2 else na, title='Volume 2', style=level_style, linewidth=math.max(1, line_width2), color=level_color, offset=get_offset(len2), show_last=length)
    plot(level3 if show_levels and num_levels >= 3 else na, title='Volume 3', style=level_style, linewidth=math.max(1, line_width3), color=level_color, offset=get_offset(len3), show_last=length)
    plot(level4 if show_levels and num_levels >= 4 else na, title='Volume 4', style=level_style, linewidth=math.max(1, line_width4), color=level_color, offset=get_offset(len4), show_last=length)
    plot(level5 if show_levels and num_levels >= 5 else na, title='Volume 5', style=level_style, linewidth=math.max(1, line_width5), color=level_color, offset=get_offset(len5), show_last=length)
    plot(level6 if show_levels and num_levels >= 6 else na, title='Volume 6', style=level_style, linewidth=math.max(1, line_width6), color=level_color, offset=get_offset(len6), show_last=length)
    plot(level7 if show_levels and num_levels >= 7 else na, title='Volume 7', style=level_style, linewidth=math.max(1, line_width7), color=level_color, offset=get_offset(len7), show_last=length)
    plot(level8 if show_levels and num_levels >= 8 else na, title='Volume 8', style=level_style, linewidth=math.max(1, line_width8), color=level_color, offset=get_offset(len8), show_last=length)
    plot(level9 if show_levels and num_levels >= 9 else na, title='Volume 9', style=level_style, linewidth=math.max(1, line_width9), color=level_color, offset=get_offset(len9), show_last=length)
    plot(level10 if show_levels and num_levels >= 10 else na, title='Volume 10', style=level_style, linewidth=math.max(1, line_width10), color=level_color, offset=get_offset(len10), show_last=length)
    plot(level11 if show_levels and num_levels >= 11 else na, title='Volume 11', style=level_style, linewidth=math.max(1, line_width11), color=level_color, offset=get_offset(len11), show_last=length)
    plot(level12 if show_levels and num_levels >= 12 else na, title='Volume 12', style=level_style, linewidth=math.max(1, line_width12), color=level_color, offset=get_offset(len12), show_last=length)
    plot(level13 if show_levels and num_levels >= 13 else na, title='Volume 13', style=level_style, linewidth=math.max(1, line_width13), color=level_color, offset=get_offset(len13), show_last=length)
    plot(level14 if show_levels and num_levels >= 14 else na, title='Volume 14', style=level_style, linewidth=math.max(1, line_width14), color=level_color, offset=get_offset(len14), show_last=length)
    plot(level15 if show_levels and num_levels >= 15 else na, title='Volume 15', style=level_style, linewidth=math.max(1, line_width15), color=level_color, offset=get_offset(len15), show_last=length)
    plot(level16 if show_levels and num_levels >= 16 else na, title='Volume 16', style=level_style, linewidth=math.max(1, line_width16), color=level_color, offset=get_offset(len16), show_last=length)
    plot(level17 if show_levels and num_levels >= 17 else na, title='Volume 17', style=level_style, linewidth=math.max(1, line_width17), color=level_color, offset=get_offset(len17), show_last=length)
    plot(level18 if show_levels and num_levels >= 18 else na, title='Volume 18', style=level_style, linewidth=math.max(1, line_width18), color=level_color, offset=get_offset(len18), show_last=length)
    plot(level19 if show_levels and num_levels >= 19 else na, title='Volume 19', style=level_style, linewidth=math.max(1, line_width19), color=level_color, offset=get_offset(len19), show_last=length)
    plot(level20 if show_levels and num_levels >= 20 else na, title='Volume 20', style=level_style, linewidth=math.max(1, line_width20), color=level_color, offset=get_offset(len20), show_last=length)
    plot(level21 if show_levels and num_levels >= 21 else na, title='Volume 21', style=level_style, linewidth=math.max(1, line_width21), color=level_color, offset=get_offset(len21), show_last=length)
    plot(level22 if show_levels and num_levels >= 22 else na, title='Volume 22', style=level_style, linewidth=math.max(1, line_width22), color=level_color, offset=get_offset(len22), show_last=length)
    plot(level23 if show_levels and num_levels >= 23 else na, title='Volume 23', style=level_style, linewidth=math.max(1, line_width23), color=level_color, offset=get_offset(len23), show_last=length)
    plot(level24 if show_levels and num_levels >= 24 else na, title='Volume 24', style=level_style, linewidth=math.max(1, line_width24), color=level_color, offset=get_offset(len24), show_last=length)
    plot(level25 if show_levels and num_levels >= 25 else na, title='Volume 25', style=level_style, linewidth=math.max(1, line_width25), color=level_color, offset=get_offset(len25), show_last=length)
    plot(level26 if show_levels and num_levels >= 26 else na, title='Volume 26', style=level_style, linewidth=math.max(1, line_width26), color=level_color, offset=get_offset(len26), show_last=length)
    plot(level27 if show_levels and num_levels >= 27 else na, title='Volume 27', style=level_style, linewidth=math.max(1, line_width27), color=level_color, offset=get_offset(len27), show_last=length)
    plot(level28 if show_levels and num_levels >= 28 else na, title='Volume 28', style=level_style, linewidth=math.max(1, line_width28), color=level_color, offset=get_offset(len28), show_last=length)
    plot(level29 if show_levels and num_levels >= 29 else na, title='Volume 29', style=level_style, linewidth=math.max(1, line_width29), color=level_color, offset=get_offset(len29), show_last=length)
    plot(level30 if show_levels and num_levels >= 30 else na, title='Volume 30', style=level_style, linewidth=math.max(1, line_width30), color=level_color, offset=get_offset(len30), show_last=length)
    plot(level31 if show_levels and num_levels >= 31 else na, title='Volume 31', style=level_style, linewidth=math.max(1, line_width31), color=level_color, offset=get_offset(len31), show_last=length)
    plot(level32 if show_levels and num_levels >= 32 else na, title='Volume 32', style=level_style, linewidth=math.max(1, line_width32), color=level_color, offset=get_offset(len32), show_last=length)
    plot(level33 if show_levels and num_levels >= 33 else na, title='Volume 33', style=level_style, linewidth=math.max(1, line_width33), color=level_color, offset=get_offset(len33), show_last=length)
    plot(level34 if show_levels and num_levels >= 34 else na, title='Volume 34', style=level_style, linewidth=math.max(1, line_width34), color=level_color, offset=get_offset(len34), show_last=length)
    plot(level35 if show_levels and num_levels >= 35 else na, title='Volume 35', style=level_style, linewidth=math.max(1, line_width35), color=level_color, offset=get_offset(len35), show_last=length)
    plot(level36 if show_levels and num_levels >= 36 else na, title='Volume 36', style=level_style, linewidth=math.max(1, line_width36), color=level_color, offset=get_offset(len36), show_last=length)
    plot(level37 if show_levels and num_levels >= 37 else na, title='Volume 37', style=level_style, linewidth=math.max(1, line_width37), color=level_color, offset=get_offset(len37), show_last=length)
    plot(level38 if show_levels and num_levels >= 38 else na, title='Volume 38', style=level_style, linewidth=math.max(1, line_width38), color=level_color, offset=get_offset(len38), show_last=length)
    plot(level39 if show_levels and num_levels >= 39 else na, title='Volume 39', style=level_style, linewidth=math.max(1, line_width39), color=level_color, offset=get_offset(len39), show_last=length)
    plot(level40 if show_levels and num_levels >= 40 else na, title='Volume 40', style=level_style, linewidth=math.max(1, line_width40), color=level_color, offset=get_offset(len40), show_last=length)
    plot(level41 if show_levels and num_levels >= 41 else na, title='Volume 41', style=level_style, linewidth=math.max(1, line_width41), color=level_color, offset=get_offset(len41), show_last=length)
    plot(level42 if show_levels and num_levels >= 42 else na, title='Volume 42', style=level_style, linewidth=math.max(1, line_width42), color=level_color, offset=get_offset(len42), show_last=length)
    plot(level43 if show_levels and num_levels >= 43 else na, title='Volume 43', style=level_style, linewidth=math.max(1, line_width43), color=level_color, offset=get_offset(len43), show_last=length)
    plot(level44 if show_levels and num_levels >= 44 else na, title='Volume 44', style=level_style, linewidth=math.max(1, line_width44), color=level_color, offset=get_offset(len44), show_last=length)
    plot(level45 if show_levels and num_levels >= 45 else na, title='Volume 45', style=level_style, linewidth=math.max(1, line_width45), color=level_color, offset=get_offset(len45), show_last=length)
    plot(level46 if show_levels and num_levels >= 46 else na, title='Volume 46', style=level_style, linewidth=math.max(1, line_width46), color=level_color, offset=get_offset(len46), show_last=length)
    plot(level47 if show_levels and num_levels >= 47 else na, title='Volume 47', style=level_style, linewidth=math.max(1, line_width47), color=level_color, offset=get_offset(len47), show_last=length)
    plot(level48 if show_levels and num_levels >= 48 else na, title='Volume 48', style=level_style, linewidth=math.max(1, line_width48), color=level_color, offset=get_offset(len48), show_last=length)
    plot(level49 if show_levels and num_levels >= 49 else na, title='Volume 49', style=level_style, linewidth=math.max(1, line_width49), color=level_color, offset=get_offset(len49), show_last=length)
    plot(level50 if show_levels and num_levels >= 50 else na, title='Volume 50', style=level_style, linewidth=math.max(1, line_width50), color=level_color, offset=get_offset(len50), show_last=length)
    lines_col = NA(Color)
    lines_dim_col = NA(Color)
    if lines_col_str == '':
        if buy_sell_mode:
            if volume_type == 'buy':
                lines_col = color_tr('buy', lines_transp)
                lines_dim_col = color_tr('buy', 100 - nva_transp)
            else:
                lines_col = color_tr('sell', lines_transp)
                lines_dim_col = color_tr('sell', 100 - nva_transp)
        if not buy_sell_mode:
            lines_col = color_tr('total', lines_transp)
            lines_dim_col = color_tr('total', 100 - nva_transp)
    if lines_col_str != '':
        lines_col = color_tr(lines_col_str, lines_transp)
        lines_dim_col = color_tr(lines_col_str, 100 - nva_transp)
    def new_level(index, line_obj, len1, len2):
        level = get_level(index)
        line_width = get_width(index)
        offset1 = get_offset(len1)
        offset2 = get_offset(len2)
        line_ = line_obj
        line.delete(line_obj)
        line_ = na
        dir = 1 if flip_levels else -1
        m_offset = 1 if dir == 1 else -length
        x1_offset = m_offset + offset1
        x2_offset = z_offset
        if buy_sell_mode:
            if volume_type == 'total' or volume_type == 'sell':
                x2_offset = m_offset + offset2
        x1 = time + x1_offset * bar_range
        x2 = time + x2_offset * bar_range
        y1 = level
        y2 = level
        nva_cond = va_high_level > 0 and level >= va_high_level or (va_low_level > 0 and level <= va_low_level)
        col = lines_dim_col if show_va and dim_nva_zones and nva_cond else lines_col
        if na(line_) and show_lines:
            line_ = line.new(x1, y1, x2, y2, style=line.style_solid, color=col, width=line_width, xloc=xloc.bar_time)
        return line_

    line1: Persistent[Line] = na(Line)
    line2: Persistent[Line] = na(Line)
    line3: Persistent[Line] = na(Line)
    line4: Persistent[Line] = na(Line)
    line5: Persistent[Line] = na(Line)
    line6: Persistent[Line] = na(Line)
    line7: Persistent[Line] = na(Line)
    line8: Persistent[Line] = na(Line)
    line9: Persistent[Line] = na(Line)
    line10: Persistent[Line] = na(Line)
    line11: Persistent[Line] = na(Line)
    line12: Persistent[Line] = na(Line)
    line13: Persistent[Line] = na(Line)
    line14: Persistent[Line] = na(Line)
    line15: Persistent[Line] = na(Line)
    line16: Persistent[Line] = na(Line)
    line17: Persistent[Line] = na(Line)
    line18: Persistent[Line] = na(Line)
    line19: Persistent[Line] = na(Line)
    line20: Persistent[Line] = na(Line)
    line21: Persistent[Line] = na(Line)
    line22: Persistent[Line] = na(Line)
    line23: Persistent[Line] = na(Line)
    line24: Persistent[Line] = na(Line)
    line25: Persistent[Line] = na(Line)
    line26: Persistent[Line] = na(Line)
    line27: Persistent[Line] = na(Line)
    line28: Persistent[Line] = na(Line)
    line29: Persistent[Line] = na(Line)
    line30: Persistent[Line] = na(Line)
    line31: Persistent[Line] = na(Line)
    line32: Persistent[Line] = na(Line)
    line33: Persistent[Line] = na(Line)
    line34: Persistent[Line] = na(Line)
    line35: Persistent[Line] = na(Line)
    line36: Persistent[Line] = na(Line)
    line37: Persistent[Line] = na(Line)
    line38: Persistent[Line] = na(Line)
    line39: Persistent[Line] = na(Line)
    line40: Persistent[Line] = na(Line)
    line41: Persistent[Line] = na(Line)
    line42: Persistent[Line] = na(Line)
    line43: Persistent[Line] = na(Line)
    line44: Persistent[Line] = na(Line)
    line45: Persistent[Line] = na(Line)
    line46: Persistent[Line] = na(Line)
    line47: Persistent[Line] = na(Line)
    line48: Persistent[Line] = na(Line)
    line49: Persistent[Line] = na(Line)
    line50: Persistent[Line] = na(Line)
    line1 = new_level(51, line1, len51, len1)
    line2 = new_level(52, line2, len52, len2)
    line3 = new_level(53, line3, len53, len3)
    line4 = new_level(54, line4, len54, len4)
    line5 = new_level(55, line5, len55, len5)
    line6 = new_level(56, line6, len56, len6)
    line7 = new_level(57, line7, len57, len7)
    line8 = new_level(58, line8, len58, len8)
    line9 = new_level(59, line9, len59, len9)
    line10 = new_level(60, line10, len60, len10)
    line11 = new_level(61, line11, len61, len11)
    line12 = new_level(62, line12, len62, len12)
    line13 = new_level(63, line13, len63, len13)
    line14 = new_level(64, line14, len64, len14)
    line15 = new_level(65, line15, len65, len15)
    line16 = new_level(66, line16, len66, len16)
    line17 = new_level(67, line17, len67, len17)
    line18 = new_level(68, line18, len68, len18)
    line19 = new_level(69, line19, len69, len19)
    line20 = new_level(70, line20, len70, len20)
    line21 = new_level(71, line21, len71, len21)
    line22 = new_level(72, line22, len72, len22)
    line23 = new_level(73, line23, len73, len23)
    line24 = new_level(74, line24, len74, len24)
    line25 = new_level(75, line25, len75, len25)
    line26 = new_level(76, line26, len76, len26)
    line27 = new_level(77, line27, len77, len27)
    line28 = new_level(78, line28, len78, len28)
    line29 = new_level(79, line29, len79, len29)
    line30 = new_level(80, line30, len80, len30)
    line31 = new_level(81, line31, len81, len31)
    line32 = new_level(82, line32, len82, len32)
    line33 = new_level(83, line33, len83, len33)
    line34 = new_level(84, line34, len84, len34)
    line35 = new_level(85, line35, len85, len35)
    line36 = new_level(86, line36, len86, len36)
    line37 = new_level(87, line37, len87, len37)
    line38 = new_level(88, line38, len88, len38)
    line39 = new_level(89, line39, len89, len39)
    line40 = new_level(90, line40, len90, len40)
    line41 = new_level(91, line41, len91, len41)
    line42 = new_level(92, line42, len92, len42)
    line43 = new_level(93, line43, len93, len43)
    line44 = new_level(94, line44, len94, len44)
    line45 = new_level(95, line45, len95, len45)
    line46 = new_level(96, line46, len96, len46)
    line47 = new_level(97, line47, len97, len47)
    line48 = new_level(98, line48, len98, len48)
    line49 = new_level(99, line49, len99, len49)
    line50 = new_level(100, line50, len100, len50)
    c_height = h * cover_ext_height
    c_top = ph + c_height
    c_base = pl - c_height
    plot(c_top if show_cover else na, title='Side Cover', style=area, histbase=c_base, color=cover_color, offset=c_offset, show_last=cover_length)
    plot(ph if show_zero else na, title='Zero Line', style=histogram, histbase=pl, color=zero_color, linewidth=math.max(1, zero_width), offset=adj_z_offset, show_last=1)
    poc_col = get_color(poc_col_str, poc_color)
    poc2_col = get_color(poc2_col_str, poc2_color)
    if levels_mode == 'vwap':
        poc2_col = get_color(vwap_col_str, vwap_color)
    plotshape(poc_level if show_poc and poc_level > 0 else na, title='POC Level', style=shape.circle, color=poc_color, text=poc_text, textcolor=poc_col, location=location.absolute, size=size.auto, offset=poc_offset, show_last=1)
    plotshape(poc2_level if show_poc2 and poc2_level > 0 else na, title='Developing POC/VWAP Level', style=shape.circle, color=poc2_color, text=poc_text, textcolor=poc2_col, location=location.absolute, size=size.auto, offset=poc_offset, show_last=1)
    va_high_col = get_color(va_high_col_str, va_high_color)
    va_low_col = get_color(va_low_col_str, va_low_color)
    if levels_mode == 'vwap':
        va_high_col = get_color(vwap_high_col_str, vwap_high_color)
        va_low_col = get_color(vwap_low_col_str, vwap_low_color)
    va_zone_high = va_high_level + spacing
    va_zone_low = va_low_level + spacing
    plotshape(va_zone_high if show_va and dim_nva_zones and (va_high_level > 0) else na, title='Zone Above VA/VWAP High', style=shape.labeldown, color=nva_zone_color, text=va_high2_text, textcolor=nva_zone_color, location=location.absolute, size=size.auto, offset=va_offset, show_last=1)
    plotshape(va_zone_low if show_va and dim_nva_zones and (va_low_level > 0) else na, title='Zone Below VA/VWAP Low', style=shape.labelup, color=nva_zone_color, text=va_low2_text, textcolor=nva_zone_color, location=location.absolute, size=size.auto, offset=va_offset, show_last=1)
    plotshape(va_high_level if show_va and va_high_level > 0 else na, title='VA/VWAP High', style=shape.circle, color=va_high_color, text=va_high1_text, textcolor=va_high_col, location=location.absolute, size=size.auto, offset=va_offset, show_last=1)
    plotshape(va_low_level if show_va and va_low_level > 0 else na, title='VA/VWAP Low', style=shape.circle, color=va_low_color, text=va_low1_text, textcolor=va_low_col, location=location.absolute, size=size.auto, offset=va_offset, show_last=1)
    bgcolor_cond = range_bg_color if highlight_background and is_in_range else na
    bgcolor(bgcolor_cond, title='Range Background Highlight Color')
    plot(max_vol if show_max_vol_sli else na, color=color.new(red, 0), title='Max Volume For Vertical SLI Mode', show_last=1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)