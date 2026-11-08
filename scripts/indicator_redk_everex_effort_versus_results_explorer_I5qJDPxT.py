"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, high, hline, input, location, low,
    math, na, open, plot, plotcandle, plotchar, plotshape, script, shape, size, string, ta, volume
)
from pynecore.types import Persistent

grp_1: str = 'Rate of FLow (RoF)'
grp_2: str = 'Lookback Parameters'
grp_3: str = 'Bias / Sentiment'
grp_4: str = 'EVEREX Bands'


@script.indicator('RedK Effort Versus Results Explorer v3.0', 'RedK EVEREX v3.0', precision=0, timeframe='', timeframe_gaps=False, explicit_plot_zorder=True)
def main(
    length=input.int(10, minval=1, inline='ROF', group=grp_1),
    MA_Type=input.string(defval='WMA', title='MA type', options=('WMA', 'EMA', 'SMA', 'HMA', 'RMA'), inline='ROF', group=grp_1),
    smooth=input.int(defval=3, title='Smooth', minval=1, inline='ROF', group=grp_1),
    sig_length=input.int(5, 'Signal Length', minval=1, inline='Signal', group=grp_1),
    S_Type=input.string(defval='WMA', title='Signal Type', options=('WMA', 'EMA', 'SMA', 'HMA', 'RMA'), inline='Signal', group=grp_1),
    lookback=input.int(defval=20, title='Length', minval=1, inline='Lookback', group=grp_2),
    lkbk_Calc=input.string(defval='Simple', title='Averaging', options=('Simple', 'Same as RRoF'), inline='Lookback', group=grp_2),
    showBias=input.bool(defval=False, title='Bias Plot ? -- ', inline='Bias', group=grp_3),
    B_Length=input.int(defval=30, title='Length', minval=1, inline='Bias', group=grp_3),
    B_Type=input.string(defval='WMA', title='MA type', options=('WMA', 'EMA', 'SMA', 'HMA', 'RMA'), inline='Bias', group=grp_3),
    showEVEREX=input.bool(True, 'Show EVEREX Bands ? -- ', inline='EVEREX', group=grp_4),
    __input_11__=input.string('100', title='Band Scale', options=('100', '200', '400'), inline='EVEREX', group=grp_4),
    Eq_band_option=input.string('Joint', title='Band Option', options=('Joint', 'Separate'), group=grp_4),
    showMarkers__input=input.bool(True, 'Show EVEREX Markers ?'),
    ShowLevels=input(True, "Show Control Levels", inline="control"),
    ctr_level__input=input(25, "     Level", inline="control")
):
    def GetAverage(_data, _len, MAOption):
        __block_result__ = na
        __switch__ = MAOption
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

    def Normalize(_Value, _Avg):
        _X = _Value / _Avg

        _Nor = 1.0 if _X > 1.5 else 0.9 if _X > 1.2 else 0.8 if _X > 1.0 else 0.7 if _X > 0.8 else 0.6 if _X > 0.6 else 0.5 if _X > 0.4 else 0.25 if _X > 0.2 else 0.1

        return _Nor


    bandscale = string.tonumber(__input_11__)

    DispBias = display.pane if showBias else display.none
    DispBands = display.pane if showEVEREX else display.none
    showhlines = display.all if showEVEREX else display.none

    Disp_vals = display.status_line + display.data_window

    v = 1 if na(volume) else volume
    NoVol_Flag = True if na(volume) else False

    lkbk_MA_Type = 'SMA' if lkbk_Calc == 'Simple' else MA_Type

    Vola = GetAverage(v, lookback, lkbk_MA_Type)
    Vola_n_pre = Normalize(v, Vola) * 100

    Vola_n = 100 if NoVol_Flag else Vola_n_pre

    BarSpread = close - open
    BarRange = high - low
    R2 = ta.highest(2) - ta.lowest(2)
    SrcShift = ta.change(close)

    sign_shift = math.sign(SrcShift)
    sign_spread = math.sign(BarSpread)

    barclosing = 2 * (close - low) / BarRange * 100 - 100

    s2r = BarSpread / BarRange * 100

    BarSpread_abs = math.abs(BarSpread)
    BarSpread_avg = GetAverage(BarSpread_abs, lookback, lkbk_MA_Type)
    BarSpread_ratio_n = Normalize(BarSpread_abs, BarSpread_avg) * 100 * sign_spread

    barclosing_2 = 2 * (close - ta.lowest(2)) / R2 * 100 - 100

    Shift2Bar_toR2 = SrcShift / R2 * 100

    SrcShift_abs = math.abs(SrcShift)
    srcshift_avg = GetAverage(SrcShift_abs, lookback, lkbk_MA_Type)
    srcshift_ratio_n = Normalize(SrcShift_abs, srcshift_avg) * 100 * sign_shift

    Pricea_n = (barclosing + s2r + BarSpread_ratio_n + barclosing_2 + Shift2Bar_toR2 + srcshift_ratio_n) / 6

    bar_flow = Pricea_n * Vola_n / 100

    bulls = math.max(bar_flow, 0)
    bears = -1 * math.min(bar_flow, 0)

    bulls_avg = GetAverage(bulls, length, MA_Type)
    bears_avg = GetAverage(bears, length, MA_Type)

    dx = bulls_avg / bears_avg
    RROF = 2 * (100 - 100 / (1 + dx)) - 100
    RROF_s = ta.wma(RROF, smooth)

    Signal = GetAverage(RROF_s, sig_length, S_Type)

    dx_b = GetAverage(bulls, B_Length, B_Type) / GetAverage(bears, B_Length, B_Type)
    RROF_b = 2 * (100 - 100 / (1 + dx_b)) - 100
    RROF_bs = ta.wma(RROF_b, smooth)

    c_zero = color.new(color.new('#1163F6'), 25)
    c_band = color.new(color.yellow, 40)

    c_up = color.aqua
    c_dn = color.orange

    c_sup = color.new(color.new('#00AA00'), 70)
    c_sdn = color.new(color.new('#FF180B'), 70)

    up = RROF_s >= 0
    s_up = RROF_bs >= 0

    hline(0, 'Zero Line', c_zero, linestyle=hline.style_solid)

    hline(0.25 * bandscale, title='1/4 Level', color=c_band, linestyle=hline.style_dotted, display=showhlines)
    hline(0.5 * bandscale, title='2/4 Level', color=c_band, linestyle=hline.style_dotted, display=showhlines)
    hline(0.75 * bandscale, title='3/4 Level', color=c_band, linestyle=hline.style_dotted, display=showhlines)
    hline(bandscale, title='4/4 Level', color=c_band, linestyle=hline.style_dotted, display=showhlines)

    plot(ta.wma(bulls_avg, smooth), 'Bulls', color=color.new('#11FF20'), linewidth=2, display=display.none)
    plot(ta.wma(bears_avg, smooth), 'Bears', color=color.new('#D5180B'), linewidth=2, display=display.none)

    plot(RROF_bs, 'Bias / Sentiment', style=plot.style_area, color=c_sup if s_up else c_sdn, linewidth=4, display=DispBias)

    nPrice = math.max(math.min(Pricea_n, 100), -100)
    nVol = math.max(math.min(Vola_n, 100), -100)

    bar = bar_flow

    c_vol_grn = color.new(color.new('#26A69A'), 75)
    c_vol_red = color.new(color.new('#EF5350'), 75)

    cb_vol_grn = color.new(color.new('#26A69A'), 20)
    cb_vol_red = color.new(color.new('#EF5350'), 20)

    c_vol = c_vol_grn if bar > 0 else c_vol_red
    cb_vol = cb_vol_grn if bar > 0 else cb_vol_red

    vc_lo: int = 0
    vc_hi = nVol * bandscale / 100 / 2

    plotcandle(vc_lo, vc_hi, vc_lo, vc_hi, 'Volume Band', c_vol, c_vol, bordercolor=cb_vol, display=DispBands)

    c_pri_grn = color.new(color.new('#3ED73E'), 75)
    c_pri_red = color.new(color.new('#FF870A'), 75)

    cb_pri_grn = color.new(color.new('#3ED73E'), 20)
    cb_pri_red = color.new(color.new('#FF870A'), 20)

    c_pri = c_pri_grn if bar > 0 else c_pri_red
    cb_pri = cb_pri_grn if bar > 0 else cb_pri_red

    pc_lo_base = vc_hi if Eq_band_option == 'Joint' else 0.5 * bandscale

    pc_lo = pc_lo_base
    pc_hi = pc_lo_base + math.abs(nPrice) * bandscale / 100 / 2

    plotcandle(pc_lo, pc_hi, pc_lo, pc_hi, 'Price Band', c_pri, c_pri, bordercolor=cb_pri, display=DispBands)

    plotchar(nVol, 'Normalized Vol', char='', color=c_vol, editable=False, display=Disp_vals)
    plotchar(nPrice, 'Normalized Price', char='', color=c_pri, editable=False, display=Disp_vals)

    plot(RROF, 'RROF Raw', color.new(color.new('#2470F0'), 9), display=display.none)
    plot(Signal, 'Signal Line', color=color.new(color.new('#B8B8B8'), 33), linewidth=2)
    plot(RROF_s, 'RROF Smooth', color=c_up if up else c_dn, linewidth=3)

    Alert_up = ta.crossover(RROF_s, 0)
    Alert_dn = ta.crossunder(RROF_s, 0)
    Alert_swing = ta.cross(RROF_s, 0)

    alertcondition(Alert_up, '.   RROF Crossing 0 Up', 'RROF Up - Buying Action Detected!')
    alertcondition(Alert_dn, '..  RROF Crossing 0 Down', 'RROF Down - Selling Action Detected!')
    alertcondition(Alert_swing, '... RROF Crossing 0', 'RROF Swing - Possible Reversal')

    nPrice_abs = math.abs(nPrice)

    EV_Ratio = 100 * nPrice_abs / nVol

    is_positive = nPrice > 0

    is_MegaBar = nPrice_abs >= 80 and nVol >= 80

    is_Compression = EV_Ratio <= 50

    is_EoM = EV_Ratio >= 120 and (not is_MegaBar)

    showMarkers: Persistent = showMarkers__input

    mrk_EoM_up: Persistent = shape.triangleup
    mrk_EoM_dn: Persistent = shape.triangledown

    mrk_Mega_up: Persistent = shape.arrowup
    mrk_Mega_dn: Persistent = shape.arrowdown

    mrk_Comp: Persistent = shape.circle

    plotshape(0 if showMarkers and is_EoM and is_positive else na, 'EoM +ve', style=mrk_EoM_up, color=color.green, location=location.absolute, size=size.auto, editable=False, display=display.pane)

    plotshape(0 if showMarkers and is_EoM and (not is_positive) else na, 'EoM -ve', style=mrk_EoM_dn, color=color.red, location=location.absolute, size=size.auto, editable=False, display=display.pane)

    plotshape(0 if showMarkers and is_Compression and is_positive else na, 'Compression +ve', style=mrk_Comp, color=color.green, location=location.absolute, size=size.auto, editable=False, display=display.pane)

    plotshape(0 if showMarkers and is_Compression and (not is_positive) else na, 'Compression -ve', style=mrk_Comp, color=color.red, location=location.absolute, size=size.auto, editable=False, display=display.pane)

    plotshape(0 if showMarkers and is_MegaBar and is_positive else na, 'MegaBar +ve', style=mrk_Mega_up, color=color.green, location=location.absolute, size=size.auto, editable=False, display=display.pane)

    plotshape(0 if showMarkers and is_MegaBar and (not is_positive) else na, 'MegaBar -ve', style=mrk_Mega_dn, color=color.red, location=location.absolute, size=size.auto, editable=False, display=display.pane)
    ctr_level: Persistent = ctr_level__input

    ctr_color: Persistent = color.new(color.new('#FFEE58'), 30)

    hline(ctr_level if ShowLevels else na, color=ctr_color, linestyle=hline.style_dashed, linewidth=2)
    hline(-ctr_level if ShowLevels else na, color=ctr_color, linestyle=hline.style_dashed, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)