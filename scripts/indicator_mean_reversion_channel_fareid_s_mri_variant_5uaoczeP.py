"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, display, extend, fill, format, high, hlc3,
    input, label, line, low, math, na, nz, plot, request, script, size, string, syminfo, ta, text,
    time, timeframe, xloc
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.indicator('Mean Reversion Channel - MRI Variant', shorttitle='MRC', overlay=True, format=format.inherit, na_bool=True)
def main(
    indiSet=input(False, '═════════ MRC Parameter ════════'),
    source: Series[float] = input(hlc3, title='Price Source'),
    type=input.string('SuperSmoother', title='Filter Type', options=('SuperSmoother', 'Ehlers EMA', 'Gaussian', 'Butterworth', 'BandStop', 'SMA', 'EMA', 'RMA')),
    length=input.int(200, title='Lookback Period', minval=1),
    innermult=input.float(1.0, title='Inner Channel Size Multiplier', minval=0.1),
    outermult=input.float(2.415, title='Outer Channel Size Multiplier', minval=0.1),
    ChartSet=input(False, '═════════ Chart Setting ════════'),
    drawchannel=input(True, title='Draw Channel'),
    displayzone=input(True, title='Draw Zone (With Channel)'),
    zonetransp=input.int(60, title='Zone Transparency', minval=0, maxval=100),
    displayline=input(True, title='Display Line Extension'),
    MTFSet=input(False, '═════════ MTF Setting ════════'),
    enable_mtf=input(True, title='Enable Multiple TimeFrame Analysis'),
    mtf_disp_typ=input.string('On Hover', title='MTF Display Type', options=('Always Display', 'On Hover')),
    mtf_typ=input.string('Auto', title='Multiple TimeFrame Type', options=('Auto', 'Custom')),
    mtf_lvl1=input.timeframe('D', title='Custom MTF Level 1'),
    mtf_lvl2=input.timeframe('W', title='Custom MTF Level 2')
):
    pi: Persistent = 2 * math.asin(1)
    mult: Persistent = pi * innermult
    mult2: Persistent = pi * outermult
    gradsize: Persistent[float] = 0.5
    gradtransp: Persistent = zonetransp
    def SAK_smoothing(_type, _src, _length):
        c0: float = 1.0
        c1: float = 0.0
        b0: float = 1.0
        b1: float = 0.0
        b2: float = 0.0
        a1: float = 0.0
        a2: float = 0.0
        alpha: float = 0.0
        beta: float = 0.0
        gamma: float = 0.0
        cycle = 2 * pi / _length
        if _type == 'Ehlers EMA':
            alpha = (math.cos(cycle) + math.sin(cycle) - 1) / math.cos(cycle)
            b0 = alpha
            a1 = 1 - alpha
        if _type == 'Gaussian':
            beta = 2.415 * (1 - math.cos(cycle))
            alpha = -beta + math.sqrt(beta * beta + 2 * beta)
            c0 = alpha * alpha
            a1 = 2 * (1 - alpha)
            a2 = -(1 - alpha) * (1 - alpha)
        if _type == 'Butterworth':
            beta = 2.415 * (1 - math.cos(cycle))
            alpha = -beta + math.sqrt(beta * beta + 2 * beta)
            c0 = alpha * alpha / 4
            b1 = 2
            b2 = 1
            a1 = 2 * (1 - alpha)
            a2 = -(1 - alpha) * (1 - alpha)
        if _type == 'BandStop':
            beta = math.cos(cycle)
            gamma = 1 / math.cos(cycle * 2 * 0.1)
            alpha = gamma - math.sqrt(gamma * gamma - 1)
            c0 = (1 + alpha) / 2
            b1 = -2 * beta
            b2 = 1
            a1 = beta * (1 + alpha)
            a2 = -alpha
        if _type == 'SMA':
            c1 = 1 / _length
            b0 = 1 / _length
            a1 = 1
        if _type == 'EMA':
            alpha = 2 / (_length + 1)
            b0 = alpha
            a1 = 1 - alpha
        if _type == 'RMA':
            alpha = 1 / _length
            b0 = alpha
            a1 = 1 - alpha
        _Input: Series = _src
        _Output: Series[float] = 0.0
        _Output = c0 * (b0 * _Input + b1 * nz(_Input[1]) + b2 * nz(_Input[2])) + a1 * nz(_Output[1]) + a2 * nz(_Output[2]) - c1 * nz(_Input[_length])
        return _Output

    def supersmoother(_src: Series, _length):
        s_a1 = math.exp(-math.sqrt(2) * pi / _length)
        s_b1 = 2 * s_a1 * math.cos(math.sqrt(2) * pi / _length)
        s_c3 = -math.pow(s_a1, 2)
        s_c2 = s_b1
        s_c1 = 1 - s_c2 - s_c3
        ss: Series[float] = 0.0
        ss = s_c1 * _src + s_c2 * nz(ss[1], _src[1]) + s_c3 * nz(ss[2], _src[2])
        return ss

    def f_resInMinutes():
        _resInMinutes = timeframe.multiplier * (1.0 / 60 if timeframe.isseconds else 1.0 if timeframe.isminutes else 60.0 * 24 if timeframe.isdaily else 60.0 * 24 * 7 if timeframe.isweekly else 60.0 * 24 * 30.4375 if timeframe.ismonthly else na)
        return _resInMinutes

    def get_tf(_lvl):
        y = f_resInMinutes()
        z = timeframe.period
        if mtf_typ == 'Auto':
            if y < 1:
                z = '1' if _lvl == 1 else '5' if _lvl == 2 else z
            elif y <= 3:
                z = '5' if _lvl == 1 else '15' if _lvl == 2 else z
            elif y <= 10:
                z = '15' if _lvl == 1 else '60' if _lvl == 2 else z
            elif y <= 30:
                z = '60' if _lvl == 1 else '240' if _lvl == 2 else z
            elif y <= 120:
                z = '240' if _lvl == 1 else 'D' if _lvl == 2 else z
            elif y <= 240:
                z = 'D' if _lvl == 1 else 'W' if _lvl == 2 else z
            elif y <= 1440:
                z = 'W' if _lvl == 1 else 'M' if _lvl == 2 else z
            elif y <= 10080:
                z = 'M' if _lvl == 1 else z
            else:
                z = z
        else:
            z = mtf_lvl1 if _lvl == 1 else mtf_lvl2 if _lvl == 2 else z
        return z

    def get_mrc():
        v_condition: int = 0
        v_meanline = source
        v_meanrange = supersmoother(ta.tr, length)
        if type == 'SuperSmoother':
            v_meanline = supersmoother(source, length)
        if type != 'SuperSmoother':
            v_meanline = SAK_smoothing(type, source, length)
        v_upband1 = v_meanline + v_meanrange * mult
        v_loband1 = v_meanline - v_meanrange * mult
        v_upband2 = v_meanline + v_meanrange * mult2
        v_loband2 = v_meanline - v_meanrange * mult2
        if close > v_meanline:
            v_upband2_1 = v_upband2 + v_meanrange * gradsize * 4
            v_upband2_9 = v_upband2 + v_meanrange * gradsize * -4
            if high >= v_upband2_9 and high < v_upband2:
                v_condition = 1
            elif high >= v_upband2 and high < v_upband2_1:
                v_condition = 2
            elif high >= v_upband2_1:
                v_condition = 3
            elif close <= v_meanline + v_meanrange:
                v_condition = 4
            else:
                v_condition = 5
        if close < v_meanline:
            v_loband2_1 = v_loband2 - v_meanrange * gradsize * 4
            v_loband2_9 = v_loband2 - v_meanrange * gradsize * -4
            if low <= v_loband2_9 and low > v_loband2:
                v_condition = -1
            elif low <= v_loband2 and low > v_loband2_1:
                v_condition = -2
            elif low <= v_loband2_1:
                v_condition = -3
            elif close >= v_meanline + v_meanrange:
                v_condition = -4
            else:
                v_condition = -5
        return (v_meanline, v_meanrange, v_upband1, v_loband1, v_upband2, v_loband2, v_condition)

    def get_stat(_cond):
        ret: str = 'Price at Mean Line\n'
        if _cond == 1:
            ret = 'Overbought (Weak)\n'
        elif _cond == 2:
            ret = 'Overbought\n'
        elif _cond == 3:
            ret = 'Overbought (Strong)\n'
        elif _cond == 4:
            ret = 'Price Near Mean\n'
        elif _cond == 5:
            ret = 'Price Above Mean\n'
        elif _cond == -1:
            ret = 'Oversold (Weak)\n'
        elif _cond == -2:
            ret = 'Oversold\n'
        elif _cond == -3:
            ret = 'Oversold (Strong)\n'
        elif _cond == -4:
            ret = 'Price Near Mean\n'
        elif _cond == -5:
            ret = 'Price Below Mean\n'
        return ret

    def format_price(x):
        y = string.tostring(x, '0.00000')
        if x > 10:
            y = string.tostring(x, '0.000')
        if x > 1000:
            y = string.tostring(x, '0.00')
        return y

    def f_PriceLine(_ref, linecol):
        return line.new(x1=bar_index, x2=bar_index - 1, y1=_ref, y2=_ref, extend=extend.left, color=linecol)

    def f_MTFLabel(_txt, _yloc):
        return label.new(x=time + math.round(ta.change(time) * 20), y=_yloc, xloc=xloc.bar_time, text=_txt if mtf_disp_typ == 'Always Display' else 'Check MTF', tooltip='' if mtf_disp_typ == 'Always Display' else _txt, color=color.black, textcolor=color.white, size=size.normal, style=label.style_label_lower_left if mtf_disp_typ == 'On Hover' and displayline else label.style_label_left, textalign=text.align_left)

    tf_0: Persistent = timeframe.period
    tf_1: Persistent = get_tf(1)
    tf_2: Persistent = get_tf(2)
    meanline, meanrange, upband1, loband1, upband2, loband2, condition = get_mrc()
    mtf1_meanline, mtf1_meanrange, mtf1_upband1, mtf1_loband1, mtf1_upband2, mtf1_loband2, mtf1_condition = request.security(syminfo.tickerid, tf_1, get_mrc())
    mtf2_meanline, mtf2_meanrange, mtf2_upband1, mtf2_loband1, mtf2_upband2, mtf2_loband2, mtf2_condition = request.security(syminfo.tickerid, tf_2, get_mrc())
    p_meanline: float = meanline if drawchannel else na
    p_upband1: float = upband1 if drawchannel else na
    p_loband1: float = loband1 if drawchannel else na
    p_upband2: float = upband2 if drawchannel else na
    p_loband2: float = loband2 if drawchannel else na
    z = plot(p_meanline, color=color.new(color.new('#FFCD00'), 0), style=plot.style_line, title=' Mean', linewidth=2)
    x1 = plot(p_upband1, color=color.new(color.green, 50), style=plot.style_circles, title=' R1', linewidth=1)
    x2 = plot(p_loband1, color=color.new(color.green, 50), style=plot.style_circles, title=' S1', linewidth=1)
    y1 = plot(p_upband2, color=color.new(color.red, 50), style=plot.style_line, title=' R2', linewidth=1)
    y2 = plot(p_loband2, color=color.new(color.red, 50), style=plot.style_line, title=' S2', linewidth=1)
    color1: Persistent[Color] = color.new('#FF0000')
    color2: Persistent[Color] = color.new('#FF4200')
    color3: Persistent[Color] = color.new('#FF5D00')
    color4: Persistent[Color] = color.new('#FF7400')
    color5: Persistent[Color] = color.new('#FF9700')
    color6: Persistent[Color] = color.new('#FFAE00')
    color7: Persistent[Color] = color.new('#FFC500')
    color8: Persistent[Color] = color.new('#FFCD00')
    upband2_1: float = upband2 + meanrange * gradsize * 4 if drawchannel and displayzone else na
    loband2_1: float = loband2 - meanrange * gradsize * 4 if drawchannel and displayzone else na
    upband2_2: float = upband2 + meanrange * gradsize * 3 if drawchannel and displayzone else na
    loband2_2: float = loband2 - meanrange * gradsize * 3 if drawchannel and displayzone else na
    upband2_3: float = upband2 + meanrange * gradsize * 2 if drawchannel and displayzone else na
    loband2_3: float = loband2 - meanrange * gradsize * 2 if drawchannel and displayzone else na
    upband2_4: float = upband2 + meanrange * gradsize * 1 if drawchannel and displayzone else na
    loband2_4: float = loband2 - meanrange * gradsize * 1 if drawchannel and displayzone else na
    upband2_5: float = upband2 + meanrange * gradsize * 0 if drawchannel and displayzone else na
    loband2_5: float = loband2 - meanrange * gradsize * 0 if drawchannel and displayzone else na
    upband2_6: float = upband2 + meanrange * gradsize * -1 if drawchannel and displayzone else na
    loband2_6: float = loband2 - meanrange * gradsize * -1 if drawchannel and displayzone else na
    upband2_7: float = upband2 + meanrange * gradsize * -2 if drawchannel and displayzone else na
    loband2_7: float = loband2 - meanrange * gradsize * -2 if drawchannel and displayzone else na
    upband2_8: float = upband2 + meanrange * gradsize * -3 if drawchannel and displayzone else na
    loband2_8: float = loband2 - meanrange * gradsize * -3 if drawchannel and displayzone else na
    upband2_9: float = upband2 + meanrange * gradsize * -4 if drawchannel and displayzone else na
    loband2_9: float = loband2 - meanrange * gradsize * -4 if drawchannel and displayzone else na
    plot_upband2_1 = plot(upband2_1, color=na, display=display.none)
    plot_loband2_1 = plot(loband2_1, color=na, display=display.none)
    plot_upband2_2 = plot(upband2_2, color=na, display=display.none)
    plot_loband2_2 = plot(loband2_2, color=na, display=display.none)
    plot_upband2_3 = plot(upband2_3, color=na, display=display.none)
    plot_loband2_3 = plot(loband2_3, color=na, display=display.none)
    plot_upband2_4 = plot(upband2_4, color=na, display=display.none)
    plot_loband2_4 = plot(loband2_4, color=na, display=display.none)
    plot_upband2_5 = plot(upband2_5, color=na, display=display.none)
    plot_loband2_5 = plot(loband2_5, color=na, display=display.none)
    plot_upband2_6 = plot(upband2_6, color=na, display=display.none)
    plot_loband2_6 = plot(loband2_6, color=na, display=display.none)
    plot_upband2_7 = plot(upband2_7, color=na, display=display.none)
    plot_loband2_7 = plot(loband2_7, color=na, display=display.none)
    plot_upband2_8 = plot(upband2_8, color=na, display=display.none)
    plot_loband2_8 = plot(loband2_8, color=na, display=display.none)
    plot_upband2_9 = plot(upband2_9, color=na, display=display.none)
    plot_loband2_9 = plot(loband2_9, color=na, display=display.none)
    fill(plot_upband2_1, plot_upband2_2, color=color.new(color1, gradtransp))
    fill(plot_loband2_1, plot_loband2_2, color=color.new(color1, gradtransp))
    fill(plot_upband2_2, plot_upband2_3, color=color.new(color2, gradtransp))
    fill(plot_loband2_2, plot_loband2_3, color=color.new(color2, gradtransp))
    fill(plot_upband2_3, plot_upband2_4, color=color.new(color3, gradtransp))
    fill(plot_loband2_3, plot_loband2_4, color=color.new(color3, gradtransp))
    fill(plot_upband2_4, plot_upband2_5, color=color.new(color4, gradtransp))
    fill(plot_loband2_4, plot_loband2_5, color=color.new(color4, gradtransp))
    fill(plot_upband2_5, plot_upband2_6, color=color.new(color5, gradtransp))
    fill(plot_loband2_5, plot_loband2_6, color=color.new(color5, gradtransp))
    fill(plot_upband2_6, plot_upband2_7, color=color.new(color6, gradtransp))
    fill(plot_loband2_6, plot_loband2_7, color=color.new(color6, gradtransp))
    fill(plot_upband2_7, plot_upband2_8, color=color.new(color7, gradtransp))
    fill(plot_loband2_7, plot_loband2_8, color=color.new(color7, gradtransp))
    fill(plot_upband2_8, plot_upband2_9, color=color.new(color8, gradtransp))
    fill(plot_loband2_8, plot_loband2_9, color=color.new(color8, gradtransp))
    if displayline and enable_mtf and (mtf_disp_typ == 'Always Display'):
        displayline = False
    mean: Persistent[Line] = na(Line)
    line.delete(mean)
    mean = f_PriceLine(meanline, color.new('#FFCD00')) if displayline else na
    res1: Persistent[Line] = na(Line)
    line.delete(res1)
    res1 = f_PriceLine(upband1, color.green) if displayline else na
    sup1: Persistent[Line] = na(Line)
    line.delete(sup1)
    sup1 = f_PriceLine(loband1, color.green) if displayline else na
    res2: Persistent[Line] = na(Line)
    line.delete(res2)
    res2 = f_PriceLine(upband2, color.red) if displayline else na
    sup2: Persistent[Line] = na(Line)
    line.delete(sup2)
    sup2 = f_PriceLine(loband2, color.red) if displayline else na
    brl: Persistent[str] = '\n--------------------------------------'
    dist_0 = 'Distance from Mean: ' + string.tostring((close - meanline) / close * 100, '#.##') + ' %'
    dist_1 = 'Distance from Mean: ' + string.tostring((close - mtf1_meanline) / close * 100, '#.##') + ' %'
    dist_2 = 'Distance from Mean: ' + string.tostring((close - mtf2_meanline) / close * 100, '#.##') + ' %'
    title: Persistent = 'Mean Reversion Channel\nMultiple TimeFrame Analysis' + brl
    tf0 = '\n\nTimeframe: ' + tf_0 + ' (Current)\n\nStatus: ' + get_stat(condition) + dist_0 + brl
    tf1 = '\n\nTimeframe: ' + tf_1 + '\n\nStatus: ' + get_stat(mtf1_condition) + dist_1 + brl if not timeframe.ismonthly else ''
    tf2 = '\n\nTimeframe: ' + tf_2 + '\n\nStatus: ' + get_stat(mtf2_condition) + dist_2 + brl if not timeframe.isweekly and (not timeframe.ismonthly) else ''
    mtf_lbl = title + tf0 + tf1 + tf2
    label_mtf: Persistent[Label] = na(Label)
    label.delete(label_mtf)
    label_mtf = f_MTFLabel(mtf_lbl, meanline) if enable_mtf else na


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
