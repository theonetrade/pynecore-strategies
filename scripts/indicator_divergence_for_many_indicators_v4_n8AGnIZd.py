"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, high, input,
    label, line, location, low, math, na, nz, plot, plotshape, script, shape, string, ta, volume
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.indicator('Divergence for Many Indicators v4', overlay=True, max_bars_back=1000, max_lines_count=400, max_labels_count=400, na_bool=True)
def main(
    prd=input.int(defval=5, title='Pivot Period', minval=1, maxval=50),
    source=input.string(defval='Close', title='Source for Pivot Points', options=('Close', 'High/Low')),
    searchdiv=input.string(defval='Regular', title='Divergence Type', options=('Regular', 'Hidden', 'Regular/Hidden')),
    showindis=input.string(defval='Full', title='Show Indicator Names', options=('Full', 'First Letter', 'Don\'t Show')),
    showlimit=input.int(1, title='Minimum Number of Divergence', minval=1, maxval=11),
    maxpp=input.int(defval=10, title='Maximum Pivot Points to Check', minval=1, maxval=20),
    maxbars=input.int(defval=100, title='Maximum Bars to Check', minval=30, maxval=200),
    shownum=input(defval=True, title='Show Divergence Number'),
    showlast=input(defval=False, title='Show Only Last Divergence'),
    dontconfirm=input(defval=False, title='Don\'t Wait for Confirmation'),
    showlines=input(defval=True, title='Show Divergence Lines'),
    showpivot=input(defval=False, title='Show Pivot Points'),
    calcmacd=input(defval=True, title='MACD'),
    calcmacda=input(defval=True, title='MACD Histogram'),
    calcrsi=input(defval=True, title='RSI'),
    calcstoc=input(defval=True, title='Stochastic'),
    calccci=input(defval=True, title='CCI'),
    calcmom=input(defval=True, title='Momentum'),
    calcobv=input(defval=True, title='OBV'),
    calcvwmacd=input(True, title='VWmacd'),
    calccmf=input(True, title='Chaikin Money Flow'),
    calcmfi=input(True, title='Money Flow Index'),
    calcext=input(False, title='Check External Indicator'),
    externalindi: Series[float] = input(defval=close, title='External Indicator'),
    pos_reg_div_col=input(defval=color.yellow, title='Positive Regular Divergence'),
    neg_reg_div_col=input(defval=color.navy, title='Negative Regular Divergence'),
    pos_hid_div_col=input(defval=color.lime, title='Positive Hidden Divergence'),
    neg_hid_div_col=input(defval=color.red, title='Negative Hidden Divergence'),
    pos_div_text_col=input(defval=color.black, title='Positive Divergence Text Color'),
    neg_div_text_col=input(defval=color.white, title='Negative Divergence Text Color'),
    reg_div_l_style_=input.string(defval='Solid', title='Regular Divergence Line Style', options=('Solid', 'Dashed', 'Dotted')),
    hid_div_l_style_=input.string(defval='Dashed', title='Hdden Divergence Line Style', options=('Solid', 'Dashed', 'Dotted')),
    reg_div_l_width=input.int(defval=2, title='Regular Divergence Line Width', minval=1, maxval=5),
    hid_div_l_width=input.int(defval=1, title='Hidden Divergence Line Width', minval=1, maxval=5),
    showmas=input.bool(defval=False, title='Show MAs 50 & 200', inline='ma12'),
    cma1col=input.color(defval=color.lime, title='', inline='ma12'),
    cma2col=input.color(defval=color.red, title='', inline='ma12')
):
    plot(ta.sma(close, 50) if showmas else na, color=cma1col if showmas else na)
    plot(ta.sma(close, 200) if showmas else na, color=cma2col if showmas else na)
    reg_div_l_style: Persistent = line.style_solid if reg_div_l_style_ == 'Solid' else line.style_dashed if reg_div_l_style_ == 'Dashed' else line.style_dotted
    hid_div_l_style: Persistent = line.style_solid if hid_div_l_style_ == 'Solid' else line.style_dashed if hid_div_l_style_ == 'Dashed' else line.style_dotted
    rsi = ta.rsi(close, 14)
    macd, signal, deltamacd = ta.macd(close, 12, 26, 9)
    moment = ta.mom(close, 10)
    cci = ta.cci(close, 10)
    Obv = ta.obv
    stk = ta.sma(ta.stoch(close, high, low, 14), 3)
    maFast = ta.vwma(close, 12)
    maSlow = ta.vwma(close, 26)
    vwmacd = maFast - maSlow
    Cmfm = (close - low - (high - close)) / (high - low)
    Cmfv = Cmfm * volume
    cmf = ta.sma(Cmfv, 21) / ta.sma(volume, 21)
    Mfi = ta.mfi(close, 14)
    indicators_name: Persistent[list[str]] = array.new_string(11)
    div_colors: Persistent[list[Color]] = array.new_color(4)
    if barstate.isfirst:
        array.set(indicators_name, 0, 'MACD' if showindis == 'Full' else 'M')
        array.set(indicators_name, 1, 'Hist' if showindis == 'Full' else 'H')
        array.set(indicators_name, 2, 'RSI' if showindis == 'Full' else 'E')
        array.set(indicators_name, 3, 'Stoch' if showindis == 'Full' else 'S')
        array.set(indicators_name, 4, 'CCI' if showindis == 'Full' else 'C')
        array.set(indicators_name, 5, 'MOM' if showindis == 'Full' else 'M')
        array.set(indicators_name, 6, 'OBV' if showindis == 'Full' else 'O')
        array.set(indicators_name, 7, 'VWMACD' if showindis == 'Full' else 'V')
        array.set(indicators_name, 8, 'CMF' if showindis == 'Full' else 'C')
        array.set(indicators_name, 9, 'MFI' if showindis == 'Full' else 'M')
        array.set(indicators_name, 10, 'Extrn' if showindis == 'Full' else 'X')
        array.set(div_colors, 0, pos_reg_div_col)
        array.set(div_colors, 1, neg_reg_div_col)
        array.set(div_colors, 2, pos_hid_div_col)
        array.set(div_colors, 3, neg_hid_div_col)
    ph: float = ta.pivothigh(close if source == 'Close' else high, prd, prd)
    pl: float = ta.pivotlow(close if source == 'Close' else low, prd, prd)
    plotshape(cast_bool(ph) and showpivot, text='H', style=shape.labeldown, color=color.new(color.white, 100), textcolor=color.new(color.red, 0), location=location.abovebar, offset=-prd)
    plotshape(cast_bool(pl) and showpivot, text='L', style=shape.labelup, color=color.new(color.white, 100), textcolor=color.new(color.lime, 0), location=location.belowbar, offset=-prd)
    maxarraysize: Persistent[int] = 20
    ph_positions: Persistent[list[int]] = array.new_int(maxarraysize, 0)
    pl_positions: Persistent[list[int]] = array.new_int(maxarraysize, 0)
    ph_vals: Persistent[list[float]] = array.new_float(maxarraysize, 0.0)
    pl_vals: Persistent[list[float]] = array.new_float(maxarraysize, 0.0)
    if cast_bool(ph):
        array.unshift(ph_positions, bar_index)
        array.unshift(ph_vals, ph)
        if array.size(ph_positions) > maxarraysize:
            array.pop(ph_positions)
            array.pop(ph_vals)
    if cast_bool(pl):
        array.unshift(pl_positions, bar_index)
        array.unshift(pl_vals, pl)
        if array.size(pl_positions) > maxarraysize:
            array.pop(pl_positions)
            array.pop(pl_vals)
    def positive_regular_positive_hidden_divergence(src: Series, cond):
        divlen: int = 0
        prsc: Series = close if source == 'Close' else low
        if dontconfirm or src > src[1] or close > close[1]:
            startpoint__0000007f__ = 0 if dontconfirm else 1
            for x in pine_range(0, maxpp - 1, 1):
                len = bar_index - array.get(pl_positions, x) + prd
                if array.get(pl_positions, x) == 0 or len > maxbars:
                    break
                if len > 5 and (cond == 1 and src[startpoint__0000007f__] > src[len] and (prsc[startpoint__0000007f__] < nz(array.get(pl_vals, x))) or (cond == 2 and src[startpoint__0000007f__] < src[len] and (prsc[startpoint__0000007f__] > nz(array.get(pl_vals, x))))):
                    slope1 = (src[startpoint__0000007f__] - src[len]) / (len - startpoint__0000007f__)
                    virtual_line1 = src[startpoint__0000007f__] - slope1
                    slope2 = (close[startpoint__0000007f__] - close[len]) / (len - startpoint__0000007f__)
                    virtual_line2 = close[startpoint__0000007f__] - slope2
                    arrived: bool = True
                    for y in pine_range(1 + startpoint__0000007f__, len - 1, 1):
                        if src[y] < virtual_line1 or nz(close[y]) < virtual_line2:
                            arrived = False
                            break
                        virtual_line1 = virtual_line1 - slope1
                        virtual_line2 = virtual_line2 - slope2
                    if arrived:
                        divlen = len
                        break
        return divlen

    def negative_regular_negative_hidden_divergence(src: Series, cond):
        divlen: int = 0
        prsc: Series = close if source == 'Close' else high
        if dontconfirm or src < src[1] or close < close[1]:
            startpoint__0000009f__ = 0 if dontconfirm else 1
            for x in pine_range(0, maxpp - 1, 1):
                len = bar_index - array.get(ph_positions, x) + prd
                if array.get(ph_positions, x) == 0 or len > maxbars:
                    break
                if len > 5 and (cond == 1 and src[startpoint__0000009f__] < src[len] and (prsc[startpoint__0000009f__] > nz(array.get(ph_vals, x))) or (cond == 2 and src[startpoint__0000009f__] > src[len] and (prsc[startpoint__0000009f__] < nz(array.get(ph_vals, x))))):
                    slope1 = (src[startpoint__0000009f__] - src[len]) / (len - startpoint__0000009f__)
                    virtual_line1 = src[startpoint__0000009f__] - slope1
                    slope2 = (close[startpoint__0000009f__] - nz(close[len])) / (len - startpoint__0000009f__)
                    virtual_line2 = close[startpoint__0000009f__] - slope2
                    arrived: bool = True
                    for y in pine_range(1 + startpoint__0000009f__, len - 1, 1):
                        if src[y] > virtual_line1 or nz(close[y]) > virtual_line2:
                            arrived = False
                            break
                        virtual_line1 = virtual_line1 - slope1
                        virtual_line2 = virtual_line2 - slope2
                    if arrived:
                        divlen = len
                        break
        return divlen

    def calculate_divs(cond, indicator_1):
        divs: list[int] = array.new_int(4, 0)
        array.set(divs, 0, positive_regular_positive_hidden_divergence(indicator_1, 1) if cond and (searchdiv == 'Regular' or searchdiv == 'Regular/Hidden') else 0)
        array.set(divs, 1, negative_regular_negative_hidden_divergence(indicator_1, 1) if cond and (searchdiv == 'Regular' or searchdiv == 'Regular/Hidden') else 0)
        array.set(divs, 2, positive_regular_positive_hidden_divergence(indicator_1, 2) if cond and (searchdiv == 'Hidden' or searchdiv == 'Regular/Hidden') else 0)
        array.set(divs, 3, negative_regular_negative_hidden_divergence(indicator_1, 2) if cond and (searchdiv == 'Hidden' or searchdiv == 'Regular/Hidden') else 0)
        return divs

    all_divergences: Persistent[list[int]] = array.new_int(44)
    def array_set_divs(div_pointer, index):
        __block_result__ = na
        for x in pine_range(0, 3, 1):
            __block_result__ = array.set(all_divergences, index * 4 + x, array.get(div_pointer, x))
        return __block_result__

    array_set_divs(calculate_divs(calcmacd, macd), 0)
    array_set_divs(calculate_divs(calcmacda, deltamacd), 1)
    array_set_divs(calculate_divs(calcrsi, rsi), 2)
    array_set_divs(calculate_divs(calcstoc, stk), 3)
    array_set_divs(calculate_divs(calccci, cci), 4)
    array_set_divs(calculate_divs(calcmom, moment), 5)
    array_set_divs(calculate_divs(calcobv, Obv), 6)
    array_set_divs(calculate_divs(calcvwmacd, vwmacd), 7)
    array_set_divs(calculate_divs(calccmf, cmf), 8)
    array_set_divs(calculate_divs(calcmfi, Mfi), 9)
    array_set_divs(calculate_divs(calcext, externalindi), 10)
    total_div: int = 0
    for x in pine_range(0, array.size(all_divergences) - 1, 1):
        total_div = total_div + math.round(math.sign(array.get(all_divergences, x)))
    if total_div < showlimit:
        array.fill(all_divergences, 0)
    pos_div_lines: Persistent[list[Line]] = array.new_line(0)
    neg_div_lines: Persistent[list[Line]] = array.new_line(0)
    pos_div_labels: Persistent[list[Label]] = array.new_label(0)
    neg_div_labels: Persistent[list[Label]] = array.new_label(0)
    def delete_old_pos_div_lines():
        __block_result_1__ = na
        if array.size(pos_div_lines) > 0:
            for j in pine_range(0, array.size(pos_div_lines) - 1, 1):
                line.delete(array.get(pos_div_lines, j))
            __block_result_1__ = array.clear(pos_div_lines)
        return __block_result_1__

    def delete_old_neg_div_lines():
        __block_result_2__ = na
        if array.size(neg_div_lines) > 0:
            for j in pine_range(0, array.size(neg_div_lines) - 1, 1):
                line.delete(array.get(neg_div_lines, j))
            __block_result_2__ = array.clear(neg_div_lines)
        return __block_result_2__

    def delete_old_pos_div_labels():
        __block_result_3__ = na
        if array.size(pos_div_labels) > 0:
            for j in pine_range(0, array.size(pos_div_labels) - 1, 1):
                label.delete(array.get(pos_div_labels, j))
            __block_result_3__ = array.clear(pos_div_labels)
        return __block_result_3__

    def delete_old_neg_div_labels():
        __block_result_4__ = na
        if array.size(neg_div_labels) > 0:
            for j in pine_range(0, array.size(neg_div_labels) - 1, 1):
                label.delete(array.get(neg_div_labels, j))
            __block_result_4__ = array.clear(neg_div_labels)
        return __block_result_4__

    def delete_last_pos_div_lines_label(n):
        __block_result_5__ = na
        if n > 0 and array.size(pos_div_lines) >= n:
            asz = array.size(pos_div_lines)
            for j in pine_range(1, n, 1):
                line.delete(array.get(pos_div_lines, asz - j))
                array.pop(pos_div_lines)
            __block_result_6__ = na
            if array.size(pos_div_labels) > 0:
                label.delete(array.get(pos_div_labels, array.size(pos_div_labels) - 1))
                __block_result_6__ = array.pop(pos_div_labels)
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    def delete_last_neg_div_lines_label(n):
        __block_result_7__ = na
        if n > 0 and array.size(neg_div_lines) >= n:
            asz = array.size(neg_div_lines)
            for j in pine_range(1, n, 1):
                line.delete(array.get(neg_div_lines, asz - j))
                array.pop(neg_div_lines)
            __block_result_8__ = na
            if array.size(neg_div_labels) > 0:
                label.delete(array.get(neg_div_labels, array.size(neg_div_labels) - 1))
                __block_result_8__ = array.pop(neg_div_labels)
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    pos_reg_div_detected: bool = False
    neg_reg_div_detected: bool = False
    pos_hid_div_detected: bool = False
    neg_hid_div_detected: bool = False
    last_pos_div_lines: Persistent[int] = 0
    last_neg_div_lines: Persistent[int] = 0
    remove_last_pos_divs: Persistent[bool] = False
    remove_last_neg_divs: Persistent[bool] = False
    if cast_bool(pl):
        remove_last_pos_divs = False
        last_pos_div_lines = 0
    if cast_bool(ph):
        remove_last_neg_divs = False
        last_neg_div_lines = 0
    divergence_text_top: str = ''
    divergence_text_bottom: str = ''
    distances: list[int] = array.new_int(0)
    dnumdiv_top: int = 0
    dnumdiv_bottom: int = 0
    top_label_col = color.white
    bottom_label_col = color.white
    old_pos_divs_can_be_removed: bool = True
    old_neg_divs_can_be_removed: bool = True
    startpoint = 0 if dontconfirm else 1
    for x in pine_range(0, 10, 1):
        div_type = -1
        for y in pine_range(0, 3, 1):
            if array.get(all_divergences, x * 4 + y) > 0:
                div_type = y
                if y % 2 == 1:
                    dnumdiv_top = dnumdiv_top + 1
                    top_label_col = array.get(div_colors, y)
                if y % 2 == 0:
                    dnumdiv_bottom = dnumdiv_bottom + 1
                    bottom_label_col = array.get(div_colors, y)
                if not array.includes(distances, array.get(all_divergences, x * 4 + y)):
                    array.push(distances, array.get(all_divergences, x * 4 + y))
                    new_line = line.new(x1=bar_index - array.get(all_divergences, x * 4 + y), y1=close[array.get(all_divergences, x * 4 + y)] if source == 'Close' else low[array.get(all_divergences, x * 4 + y)] if y % 2 == 0 else high[array.get(all_divergences, x * 4 + y)], x2=bar_index - startpoint, y2=close[startpoint] if source == 'Close' else low[startpoint] if y % 2 == 0 else high[startpoint], color=array.get(div_colors, y), style=reg_div_l_style if y < 2 else hid_div_l_style, width=reg_div_l_width if y < 2 else hid_div_l_width) if showlines else na
                    if y % 2 == 0:
                        if old_pos_divs_can_be_removed:
                            old_pos_divs_can_be_removed = False
                            if not showlast and remove_last_pos_divs:
                                delete_last_pos_div_lines_label(last_pos_div_lines)
                                last_pos_div_lines = 0
                            if showlast:
                                delete_old_pos_div_lines()
                        array.push(pos_div_lines, new_line)
                        last_pos_div_lines = last_pos_div_lines + 1
                        remove_last_pos_divs = True
                    if y % 2 == 1:
                        if old_neg_divs_can_be_removed:
                            old_neg_divs_can_be_removed = False
                            if not showlast and remove_last_neg_divs:
                                delete_last_neg_div_lines_label(last_neg_div_lines)
                                last_neg_div_lines = 0
                            if showlast:
                                delete_old_neg_div_lines()
                        array.push(neg_div_lines, new_line)
                        last_neg_div_lines = last_neg_div_lines + 1
                        remove_last_neg_divs = True
                if y == 0:
                    pos_reg_div_detected = True
                if y == 1:
                    neg_reg_div_detected = True
                if y == 2:
                    pos_hid_div_detected = True
                if y == 3:
                    neg_hid_div_detected = True
        if div_type >= 0:
            divergence_text_top = divergence_text_top + ((array.get(indicators_name, x) + '\n' if showindis != "Don't Show" else '') if div_type % 2 == 1 else '')
            divergence_text_bottom = divergence_text_bottom + ((array.get(indicators_name, x) + '\n' if showindis != "Don't Show" else '') if div_type % 2 == 0 else '')
    if showindis != "Don't Show" or shownum:
        if shownum and dnumdiv_top > 0:
            divergence_text_top = divergence_text_top + string.tostring(dnumdiv_top)
        if shownum and dnumdiv_bottom > 0:
            divergence_text_bottom = divergence_text_bottom + string.tostring(dnumdiv_bottom)
        if divergence_text_top != '':
            if showlast:
                delete_old_neg_div_labels()
            array.push(neg_div_labels, label.new(x=bar_index, y=math.max(high, high[1]), text=divergence_text_top, color=top_label_col, textcolor=neg_div_text_col, style=label.style_label_down))
        if divergence_text_bottom != '':
            if showlast:
                delete_old_pos_div_labels()
            array.push(pos_div_labels, label.new(x=bar_index, y=math.min(low, low[1]), text=divergence_text_bottom, color=bottom_label_col, textcolor=pos_div_text_col, style=label.style_label_up))
    alertcondition(pos_reg_div_detected, title='Positive Regular Divergence Detected', message='Positive Regular Divergence Detected')
    alertcondition(neg_reg_div_detected, title='Negative Regular Divergence Detected', message='Negative Regular Divergence Detected')
    alertcondition(pos_hid_div_detected, title='Positive Hidden Divergence Detected', message='Positive Hidden Divergence Detected')
    alertcondition(neg_hid_div_detected, title='Negative Hidden Divergence Detected', message='Negative Hidden Divergence Detected')
    alertcondition(pos_reg_div_detected or pos_hid_div_detected, title='Positive Divergence Detected', message='Positive Divergence Detected')
    alertcondition(neg_reg_div_detected or neg_hid_div_detected, title='Negative Divergence Detected', message='Negative Divergence Detected')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)