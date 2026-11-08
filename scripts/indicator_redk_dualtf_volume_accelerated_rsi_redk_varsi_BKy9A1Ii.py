"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, barmerge, barstate, close, color, display, fill, hline,
    input, location, math, na, plot, plotshape, request, script, shape, size, syminfo, ta,
    time_close, timeframe, volume
)
from pynecore.types import Persistent, Series

grpC: str = "Current Timeframe RSI"
grpH: str = "Context Timeframe RSI"
grpsig: str = "Signal Line"
grplvl: str = "Levels"
disnon = display.none


@script.indicator("RedK DualTF Volume-Accelerated RSI", shorttitle='RedK_VARSI v1.2', overlay=False, precision=1)
def main(
    rsiLen=input.int(14, minval=1, title="RSI Length", inline="rsi", group=grpC),
    avg_type=input.string('RMA', title="Averaging", options=('EMA', 'HMA', 'RMA', 'SMA', 'WMA'), inline="rsi", group=grpC, tooltip="Averaging method for the current-TF RSI.\nRMA reproduces Wilder's classic RSI." + '\nSet Length=14, Averaging=RMA, Smoothing=1, Volume Weighted=off to exactly match a standard RSI.'),
    VolWeighted=input.bool(True, "Volume Weighted", group=grpC, tooltip='When on, each bar\'s price change is weighted by that bar\'s volume before averaging. This\n  emphasises moves that happen on higher participation.\n  \nTurn off for a pure price-based RSI.'),
    smooth=input.int(3, minval=1, title="Smoothing", inline="smooth", group=grpC, display=disnon),
    smth_type=input.string('WMA', title="Averaging", options=('EMA', 'HMA', 'RMA', 'SMA', 'WMA'), display=disnon, inline="smooth", group=grpC, tooltip='Optional smoothing to apply to Current TF RSI.' + '\nHelps remove noise but introduces lag. Keep to small values or disable.'),
    col_rsi_long=input.color(color.aqua, title="Bullish", inline="rsi_c", group=grpC),
    col_rsi_short=input.color(color.new('#F57F17'), title="Bearish", inline="rsi_c", group=grpC),
    signal_len=input.int(5, "Length", minval=1, inline="sig", group=grpsig, display=disnon),
    sig_avg_type=input.string('EMA', title="  Averaging", options=('EMA', 'HMA', 'RMA', 'SMA', 'WMA'), display=disnon, inline="sig", group=grpsig, tooltip="Length and Averaging method for the RSI Signal Line."),
    col_signal=input.color(color.blue, title="Signal Line Color", inline="sig_c", group=grpsig),
    show_htf=input.bool(True, "Show Context RSI", group=grpH, display=disnon, tooltip='Disabling this turns VARSI into a single TF volume-weighted RSI, and hides the Context TF Plot.\n' + 'Also turns off the Alignment Markers & related alerts.'),
    htf_mult=input.int(5, "Context Multiplier (× chart TF)", minval=2, maxval=60, group=grpH, display=disnon, tooltip="Context TF = this many times the current chart timeframe. e.g. 5 on a 1H chart ≈ 5H"),
    htf_update=input.string('Live Update', "Context Update", options=('Live Update', 'Last Closed Bar'), group=grpH, display=disnon, tooltip='Live Update (default): the Context RSI updates as the higher-TF bar develops — most responsive. ' + 'Last Closed Bar: the Context RSI only changes when the higher-TF bar closes — steadier, no intrabar movement. ' + 'Has no effect when the Context TF equals the chart TF.'),
    col_rsiH_long=input.color(color.new('#33AA00'), title="Bullish", inline="htf_c", group=grpH),
    col_rsiH_short=input.color(color.new('#FF1111'), title="Bearish", inline="htf_c", group=grpH),
    show_align=input.bool(True, "Show Alignment Markers", group=grplvl, tooltip="Plot a marker when the Current TF RSI and the Context RSI agree on direction (both above / both below 50)."),
    dbg=input.bool(False, "Debug: quick method to show selected Context TF in Data Window", group=grpH, tooltip="Will display as minutes, then hours if > 60, then days if > 1,440.")
):
    def f_getMA(_data, _len, MAtype):
        __block_result__ = na
        __switch__ = MAtype
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(_data, _len)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(_data, _len)
        elif __switch__ == 'HMA':
            __block_result__ = ta.hma(_data, _len)
        elif __switch__ == 'RMA':
            __block_result__ = ta.rma(_data, _len)
        else:
            __block_result__ = ta.wma(_data, _len)
        value = __block_result__
        return value

    def f_CalcVW_Rsi(_len: int, avg_type: str, _volWeighted: bool):
        _vol = 1.0 if na(volume) or not _volWeighted else volume
        chg = ta.change(close) * _vol
        up = f_getMA(math.max(chg, 0), _len, avg_type)
        down = f_getMA(-math.min(chg, 0), _len, avg_type)
        rsiraw = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
        return rsiraw


    midline: int = 50
    ob_level: int = 70
    os_level: int = 30

    rsiCTF_raw = f_CalcVW_Rsi(rsiLen, avg_type, VolWeighted)
    rsiCTF = f_getMA(rsiCTF_raw, smooth, smth_type) if smooth > 1 else rsiCTF_raw

    rsi_sig = f_getMA(rsiCTF, signal_len, sig_avg_type) if signal_len > 1 else rsiCTF

    htf_tf = timeframe.from_seconds(cast_int(timeframe.in_seconds(timeframe.period) * htf_mult))

    htf_secs = timeframe.in_seconds(htf_tf)
    chart_secs = timeframe.in_seconds(timeframe.period)

    htf_invalid = htf_secs < chart_secs
    htf_is_higher = htf_secs > chart_secs
    use_last_closed = htf_update == 'Last Closed Bar' and htf_is_higher

    rsiHi_live = request.security(syminfo.tickerid, htf_tf, f_CalcVW_Rsi(rsiLen, avg_type, VolWeighted), lookahead=barmerge.lookahead_off)

    htf_bar_closes = time_close == time_close(htf_tf)
    rsiHi_closed: Persistent[float] = na(float)

    if htf_bar_closes and barstate.isconfirmed:
        rsiHi_closed = rsiHi_live

    rsiHi = na if htf_invalid or not show_htf else rsiHi_closed if use_last_closed else rsiHi_live

    ctf_up = rsiCTF > midline
    htf_up = rsiHi > midline
    aligned_up: Series = show_htf and (not htf_invalid) and ctf_up and htf_up
    aligned_down: Series = show_htf and (not htf_invalid) and (not ctf_up) and (not htf_up)

    dw = display.data_window
    d_sl = display.status_line
    dsp_dp_dw = display.pane + display.data_window

    dsp_htf = dsp_dp_dw + d_sl if show_htf else disnon
    dsp_htf_am = dsp_dp_dw if show_htf else disnon

    hline(midline, title='Midline', color=color.new(color.yellow, 50), linestyle=hline.style_dotted)
    hline(ob_level, title='Overbought', color=color.new(color.green, 30), linestyle=hline.style_dashed)
    hline(os_level, title='Oversold', color=color.new(color.red, 30), linestyle=hline.style_dashed)

    p1 = plot(rsiCTF, title='Current RSI', color=col_rsi_long if ctf_up else col_rsi_short, linewidth=3)

    ps = plot(rsi_sig, title='RSI Signal', color=col_signal, linewidth=1, display=d_sl + dsp_dp_dw)

    p2 = plot(rsiHi, title='Higher TF RSI', color=col_rsiH_long if htf_up else col_rsiH_short, linewidth=1, display=dsp_htf)

    pl_midline = plot(midline, 'midline ref', color=color.new(color.white, 100), editable=False, display=display.none)

    fill(p2, pl_midline, top_value=100, bottom_value=50, top_color=color.new(col_rsiH_long, 20), bottom_color=color.new(col_rsiH_long, 90))
    fill(pl_midline, p2, top_value=50, bottom_value=0, top_color=color.new(col_rsiH_short, 90), bottom_color=color.new(col_rsiH_short, 20))

    plotshape(show_align and aligned_up and (not aligned_up[1]), title='Bull Alignment', display=disnon if not show_align else dsp_htf_am, style=shape.triangleup, location=location.bottom, color=col_rsiH_long, size=size.small)
    plotshape(show_align and aligned_down and (not aligned_down[1]), title='Bear Alignment', display=disnon if not show_align else dsp_htf_am, style=shape.triangledown, location=location.top, color=col_rsiH_short, size=size.small)

    alertcondition(ta.crossover(rsiCTF, midline), title='VARSI crosses above midline (Bullish)', message='{{ticker}} — VARSI crossed ABOVE the midline (bullish)')
    alertcondition(ta.crossunder(rsiCTF, midline), title='VARSI crosses below midline (Bearish)', message='{{ticker}} — VARSI crossed BELOW the midline (bearish)')
    alertcondition(ta.cross(rsiCTF, midline), title='VARSI swings around midline (Up or Down)', message='{{ticker}} — VARSI crossed the midline')

    alertcondition(ta.crossover(rsiCTF, ob_level), title='VARSI enters Overbought zone', message='{{ticker}} — VARSI entered the Overbought zone')
    alertcondition(ta.crossunder(rsiCTF, os_level), title='VARSI enters Oversold zone', message='{{ticker}} — VARSI entered the Oversold zone')

    htf_mins = htf_secs / 60.0

    plot(htf_mins if dbg and htf_mins <= 60 else na, 'Context TF (mins)', display=dw if dbg and show_htf else disnon)
    plot(htf_mins / 60.0 if dbg and htf_mins > 60 and (htf_mins <= 1440) else na, 'Context TF (hrs)', display=dw if dbg and show_htf else disnon)
    plot(htf_mins / 1440.0 if dbg and htf_mins > 1440 else na, 'Context TF (days)', display=dw if dbg and show_htf else disnon)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)