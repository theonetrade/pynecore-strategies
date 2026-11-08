"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, extend, high, hl2, input, line,
    location, low, math, na, open, plot, plotshape, script, shape, size, ta, xloc
)
from pynecore.types import NA, Persistent, PersistentSeries

g1: str = "Macro Trend"
g2: str = "Micro Trend"
g3: str = "Signals"
g4: str = "Supertrend"


@script.indicator("Auto Trend Lines + Signals", overlay=True, max_lines_count=500)
def main(
    macro_on=input.bool(True, "═══════════ Macro Trend ═══════════", group=g1),
    macro_lft=input.int(10, "Length: Left", minval=1, group=g1, inline="ml"),
    macro_rgt=input.int(5, "Right", minval=1, group=g1, inline="ml"),
    macro_ext=input.int(10, "Extension", minval=0, group=g1),
    macro_wick=input.bool(True, "Draw lines from wicks (uncheck for bodies)", group=g1),
    macro_filt=input.bool(True, "Display only falling High and rising Low trendlines", group=g1),
    macro_log=input.bool(True, "Log scale?", group=g1),
    macro_cbull=input.color(color.new(color.green, 0), "Colors", group=g1, inline="mc"),
    macro_cbear=input.color(color.new(color.red, 0), "", group=g1, inline="mc"),
    macro_sty=input.string("Solid", "Style", options=("Solid", "Dashed", "Dotted"), group=g1, inline="ms"),
    macro_wid=input.int(1, "Width", minval=1, maxval=4, group=g1, inline="ms"),
    micro_on=input.bool(True, "═══════════ Micro Trend ═══════════", group=g2),
    micro_lft=input.int(4, "Length: Left", minval=1, group=g2, inline="ul"),
    micro_rgt=input.int(2, "Right", minval=1, group=g2, inline="ul"),
    micro_ext=input.int(4, "Extension", minval=0, group=g2),
    micro_wick=input.bool(True, "Draw lines from wicks (uncheck for bodies)", group=g2),
    micro_filt=input.bool(True, "Display only falling High and rising Low trendlines", group=g2),
    micro_log=input.bool(True, "Log scale?", group=g2),
    micro_cbull=input.color(color.new(color.green, 0), "Colors", group=g2, inline="uc"),
    micro_cbear=input.color(color.new(color.red, 0), "", group=g2, inline="uc"),
    micro_sty=input.string("Dotted", "Style", options=("Solid", "Dashed", "Dotted"), group=g2, inline="us"),
    micro_wid=input.int(1, "Width", minval=1, maxval=4, group=g2, inline="us"),
    sig_on=input.bool(True, "Show Signals", group=g3),
    sig_sbuy_col=input.color(color.new(color.new('#00E5FF'), 0), "Strong Buy", group=g3, inline="ss"),
    sig_ssell_col=input.color(color.new(color.new('#FF1744'), 0), "Strong Sell", group=g3, inline="ss"),
    sig_wbuy_col=input.color(color.new(color.new('#69F0AE'), 0), "Weak Buy", group=g3, inline="sw"),
    sig_wsell_col=input.color(color.new(color.new('#FF6D00'), 0), "Weak Sell", group=g3, inline="sw"),
    st_on=input.bool(True, "═══════════ Supertrend ═══════════", group=g4),
    st_atr=input.int(10, "ATR Period", minval=1, group=g4, inline="st"),
    st_mult=input.float(3.0, "Multiplier", minval=0.1, step=0.1, group=g4, inline="st"),
    st_bull_col=input.color(color.new(color.new('#00E5FF'), 0), "Bull / Bear", group=g4, inline="stc"),
    st_bear_col=input.color(color.new(color.new('#FF1744'), 0), "", group=g4, inline="stc"),
    st_wid=input.int(2, "Width", minval=1, maxval=4, group=g4, inline="stw"),
    st_signals=input.bool(True, "Show Supertrend flip signals", group=g4),
    st_buy_col=input.color(color.new(color.new('#00E5FF'), 0), "ST Buy", group=g4, inline="stsc"),
    st_sell_col=input.color(color.new(color.new('#FF1744'), 0), "ST Sell", group=g4, inline="stsc")
):
    def to_style(s):
        return line.style_dashed if s == 'Dashed' else line.style_dotted if s == 'Dotted' else line.style_solid

    def project(p1, p2, b1, b2, b_end, use_log):
        lp1 = math.log(p1) if use_log else p1
        lp2 = math.log(p2) if use_log else p2
        slope = (lp2 - lp1) / (b2 - b1) if b2 - b1 != 0 else 0
        lp_end = lp2 + slope * (b_end - b2)
        return math.exp(lp_end) if use_log else lp_end

    def draw_tl(b1, p1, b2, p2, ext, use_log, col, sty, wid):
        b_end = b2 + ext
        p_end = project(p1, p2, b1, b2, b_end, use_log)
        return line.new(b1, p1, b_end, p_end, xloc=xloc.bar_index, extend=extend.none, color=col, style=sty, width=wid)

    body_high = math.max(open, close)
    body_low = math.min(open, close)

    mh_src = high if macro_wick else body_high
    ml_src = low if macro_wick else body_low
    uh_src = high if micro_wick else body_high
    ul_src = low if micro_wick else body_low

    macro_ph = ta.pivothigh(mh_src, macro_lft, macro_rgt)
    macro_pl = ta.pivotlow(ml_src, macro_lft, macro_rgt)
    micro_ph = ta.pivothigh(uh_src, micro_lft, micro_rgt)
    micro_pl = ta.pivotlow(ul_src, micro_lft, micro_rgt)

    mh_p: Persistent[float] = na(float)
    mh_b: Persistent[int] = na(float)
    ml_p: Persistent[float] = na(float)
    ml_b: Persistent[int] = na(float)
    uh_p: Persistent[float] = na(float)
    uh_b: Persistent[int] = na(float)
    ul_p: Persistent[float] = na(float)
    ul_b: Persistent[int] = na(float)

    mh_sp: Persistent[float] = na(float)
    mh_sb: Persistent[int] = na(float)
    mh_ssl: Persistent[float] = na(float)
    mh_slog: Persistent[bool] = False
    ml_sp: Persistent[float] = na(float)
    ml_sb: Persistent[int] = na(float)
    ml_ssl: Persistent[float] = na(float)
    ml_slog: Persistent[bool] = False
    uh_sp: Persistent[float] = na(float)
    uh_sb: Persistent[int] = na(float)
    uh_ssl: Persistent[float] = na(float)
    uh_slog: Persistent[bool] = False
    ul_sp: Persistent[float] = na(float)
    ul_sb: Persistent[int] = na(float)
    ul_ssl: Persistent[float] = na(float)
    ul_slog: Persistent[bool] = False

    if macro_on and (not na(macro_ph)):
        cur_b = bar_index - macro_rgt
        if not na(mh_b):
            if not macro_filt or macro_ph < mh_p:
                draw_tl(mh_b, mh_p, cur_b, macro_ph, macro_ext, macro_log, macro_cbear, to_style(macro_sty), macro_wid)
                lp1 = math.log(mh_p) if macro_log else mh_p
                lp2 = math.log(macro_ph) if macro_log else macro_ph
                db = cur_b - mh_b
                mh_sp = macro_ph
                mh_sb = cur_b
                mh_ssl = (lp2 - lp1) / db if db != 0 else 0.0
                mh_slog = macro_log
        mh_p = macro_ph
        mh_b = bar_index - macro_rgt

    if macro_on and (not na(macro_pl)):
        cur_b = bar_index - macro_rgt
        if not na(ml_b):
            if not macro_filt or macro_pl > ml_p:
                draw_tl(ml_b, ml_p, cur_b, macro_pl, macro_ext, macro_log, macro_cbull, to_style(macro_sty), macro_wid)
                lp1 = math.log(ml_p) if macro_log else ml_p
                lp2 = math.log(macro_pl) if macro_log else macro_pl
                db = cur_b - ml_b
                ml_sp = macro_pl
                ml_sb = cur_b
                ml_ssl = (lp2 - lp1) / db if db != 0 else 0.0
                ml_slog = macro_log
        ml_p = macro_pl
        ml_b = bar_index - macro_rgt

    if micro_on and (not na(micro_ph)):
        cur_b = bar_index - micro_rgt
        if not na(uh_b):
            if not micro_filt or micro_ph < uh_p:
                draw_tl(uh_b, uh_p, cur_b, micro_ph, micro_ext, micro_log, micro_cbear, to_style(micro_sty), micro_wid)
                lp1 = math.log(uh_p) if micro_log else uh_p
                lp2 = math.log(micro_ph) if micro_log else micro_ph
                db = cur_b - uh_b
                uh_sp = micro_ph
                uh_sb = cur_b
                uh_ssl = (lp2 - lp1) / db if db != 0 else 0.0
                uh_slog = micro_log
        uh_p = micro_ph
        uh_b = bar_index - micro_rgt

    if micro_on and (not na(micro_pl)):
        cur_b = bar_index - micro_rgt
        if not na(ul_b):
            if not micro_filt or micro_pl > ul_p:
                draw_tl(ul_b, ul_p, cur_b, micro_pl, micro_ext, micro_log, micro_cbull, to_style(micro_sty), micro_wid)
                lp1 = math.log(ul_p) if micro_log else ul_p
                lp2 = math.log(micro_pl) if micro_log else micro_pl
                db = cur_b - ul_b
                ul_sp = micro_pl
                ul_sb = cur_b
                ul_ssl = (lp2 - lp1) / db if db != 0 else 0.0
                ul_slog = micro_log
        ul_p = micro_pl
        ul_b = bar_index - micro_rgt

    def line_val(ap, ab, sl, ul):
        __block_result__ = na
        if na(ap) or na(ab):
            __block_result__ = NA(float)
        else:
            lp = math.log(ap) if ul else ap
            v = lp + sl * (bar_index - ab)
            __block_result__ = math.exp(v) if ul else v
        return __block_result__

    mh_val = line_val(mh_sp, mh_sb, mh_ssl, mh_slog)
    ml_val = line_val(ml_sp, ml_sb, ml_ssl, ml_slog)
    uh_val = line_val(uh_sp, uh_sb, uh_ssl, uh_slog)
    ul_val = line_val(ul_sp, ul_sb, ul_ssl, ul_slog)

    strong_buy = sig_on and macro_on and (not na(mh_val)) and ta.crossover(close, mh_val)
    strong_sell = sig_on and macro_on and (not na(ml_val)) and ta.crossunder(close, ml_val)
    weak_buy = sig_on and micro_on and (not na(uh_val)) and ta.crossover(close, uh_val)
    weak_sell = sig_on and micro_on and (not na(ul_val)) and ta.crossunder(close, ul_val)

    plotshape(strong_buy, title='Strong Buy', style=shape.triangleup, location=location.belowbar, color=sig_sbuy_col, textcolor=sig_sbuy_col, text='B', size=size.normal)
    plotshape(strong_sell, title='Strong Sell', style=shape.triangledown, location=location.abovebar, color=sig_ssell_col, textcolor=sig_ssell_col, text='S', size=size.normal)
    plotshape(weak_buy, title='Weak Buy', style=shape.triangleup, location=location.belowbar, color=sig_wbuy_col, textcolor=sig_wbuy_col, text='b', size=size.small)
    plotshape(weak_sell, title='Weak Sell', style=shape.triangledown, location=location.abovebar, color=sig_wsell_col, textcolor=sig_wsell_col, text='s', size=size.small)

    st_atr_val = ta.atr(st_atr)
    st_upper_basic = hl2 + st_mult * st_atr_val
    st_lower_basic = hl2 - st_mult * st_atr_val

    st_upper: PersistentSeries[float] = na(float)
    st_lower: PersistentSeries[float] = na(float)
    st_dir: PersistentSeries[int] = 1

    st_upper = st_upper_basic if na(st_upper[1]) else st_upper_basic if st_upper_basic < st_upper[1] or close[1] > st_upper[1] else st_upper[1]

    st_lower = st_lower_basic if na(st_lower[1]) else st_lower_basic if st_lower_basic > st_lower[1] or close[1] < st_lower[1] else st_lower[1]

    st_dir = 1 if na(st_dir[1]) else (1 if close > st_upper[1] else -1) if st_dir[1] == -1 else -1 if close < st_lower[1] else 1

    st_line = st_lower if st_dir == 1 else st_upper

    plot(st_line if st_on else na, title='Supertrend', color=st_bull_col if st_dir == 1 else st_bear_col, linewidth=st_wid)

    st_flip_buy = st_on and st_signals and (st_dir == 1) and (st_dir[1] == -1)
    st_flip_sell = st_on and st_signals and (st_dir == -1) and (st_dir[1] == 1)

    plotshape(st_flip_buy, title='ST Buy', style=shape.circle, location=location.belowbar, color=st_buy_col, size=size.small)
    plotshape(st_flip_sell, title='ST Sell', style=shape.circle, location=location.abovebar, color=st_sell_col, size=size.small)

    alertcondition(strong_buy, title='Strong Buy', message='Auto TL — Strong Buy')
    alertcondition(strong_sell, title='Strong Sell', message='Auto TL — Strong Sell')
    alertcondition(weak_buy, title='Weak Buy', message='Auto TL — Weak Buy')
    alertcondition(weak_sell, title='Weak Sell', message='Auto TL — Weak Sell')
    alertcondition(strong_buy or strong_sell or weak_buy or weak_sell, title='Any TL Signal', message='Auto TL — сигнал пересечения линии тренда')
    alertcondition(st_flip_buy, title='ST Buy', message='Auto TL — Supertrend Buy')
    alertcondition(st_flip_sell, title='ST Sell', message='Auto TL — Supertrend Sell')
    alertcondition(st_flip_buy or st_flip_sell, title='Any ST Signal', message='Auto TL — Supertrend смена тренда')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)