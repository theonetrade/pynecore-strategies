"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barstate, bgcolor, close, color, fill, high, hline,
    input, low, math, na, open, plot, script, strategy, ta
)
from pynecore.types import Color, Persistent, Series

s_pmarp: str = 'Price Moving Average Ratio Percentile'
s_pmar: str = 'Price Moving Average Ratio'
s_BGR: str = 'Blue Green Red'
s_BR: str = 'Blue Red'


@script.strategy('PMAR and Madrid MA Strategy Excecuted by @CheatCode1', overlay=False, margin_long=0, margin_short=0, default_qty_type=strategy.cash, initial_capital=1000, pyramiding=0, default_qty_value=1000, max_bars_back=100, close_by_id=True)
def main(
    i_src_price: Series[float] = input.source(close, 'Price source', inline='1', group='Main Properties'),
    i_p_type_line=input.string(s_pmarp, 'Indicator....', options=(s_pmar, s_pmarp), inline='2', group='Main Properties'),
    i_ma_len=input.int(20, 'PMAR length', minval=1, inline='3', group='Main Properties'),
    i_ma_typ=input.string('VWMA', 'MA type...', options=('SMA', 'EMA', 'HMA', 'RMA', 'VWMA'), inline='3', group='Main Properties'),
    i_c_typ_line=input.string('Spectrum', 'Color type', options=('Spectrum', 'Solid'), inline='1', group='Line plot settings'),
    i_c_typ_spctrm_line=input.string(s_BGR, 'Spectrum', options=(s_BR, s_BGR), inline='1', group='Line plot settings'),
    i_c_solid_line=input.color(color.new('#FFFF00'), 'Solid color', inline='1', group='Line plot settings'),
    i_p_width_line=input.int(1, 'Line width', minval=1, maxval=4, inline='2', group='Line plot settings'),
    i_pmarp_lookback=input.int(350, 'Lookback', minval=1, maxval=1900, inline='2', group='Line plot settings'),
    i_show_signal_ma=input.bool(True, 'Signal MA', inline='0', group='Signal MA Settings'),
    i_signal_ma_Len=input.int(20, 'MA length', minval=1, inline='1', group='Signal MA Settings'),
    i_signal_ma_typ=input.string('SMA', 'MA type', options=('SMA', 'EMA', 'HMA', 'RMA', 'VWMA'), inline='1', group='Signal MA Settings'),
    i_c_typ_sig=input.string('Solid', 'Color type', options=('Spectrum', 'Solid'), inline='2', group='Signal MA Settings'),
    i_c_typ_spctrm_sig=input.string(s_BGR, 'Spectrum', options=(s_BR, s_BGR), inline='2', group='Signal MA Settings'),
    i_c_solid_sig=input.color(color.white, 'Solid color', inline='2', group='Signal MA Settings'),
    i_p_width_sig=input.int(1, 'Line width', minval=1, maxval=4, inline='3', group='Signal MA Settings'),
    i_hi_alert_pmarp=input.float(99, 'Hi PMARP alert level', minval=0.1, maxval=100, step=0.01, inline='6', group='Visual Alert Level Settings'),
    i_lo_alert_pmarp=input.float(1, 'Lo PMARP alert level', minval=0.1, maxval=100, step=0.01, inline='6', group='Visual Alert Level Settings'),
    i_hi_alert_pmar=input.float(2.7, 'Hi PMAR alert level.', minval=0.1, maxval=100, step=0.01, inline='7', group='Visual Alert Level Settings'),
    i_lo_alert_pmar=input.float(0.7, 'Lo PMAR alert level.', minval=0.1, maxval=100, step=0.01, inline='7', group='Visual Alert Level Settings'),
    i_hi_alert_line_on=input.bool(True, 'Hi alert line.', inline='8', group='Visual Alert Level Settings'),
    i_lo_alert_line_on=input.bool(True, 'Lo alert line.', inline='8', group='Visual Alert Level Settings'),
    i_bg_hi_signal_on=input.bool(True, 'Hi signal bars', inline='9', group='Visual Alert Level Settings'),
    i_bg_lo_signal_on=input.bool(True, 'Lo signal bars', inline='9', group='Visual Alert Level Settings'),
    i_exp=input(True, title='Expnential MA'),
    __input_25__=input.float(1, title='Take Profit', group='Take Profit and Stop Loss'),
    __input_26__=input.float(27.75, title='Stop Loss', group='Take Profit and Stop Loss'),
    H1=input.int(75, 'Top Line', minval=51, maxval=100, group='Top and Bottom Lines', inline='1'),
    H2=input.int(20, 'Bottom Line', minval=0, maxval=49, group='Top and Bottom Lines', inline='1'),
    H3A=input.int(5, ' Transparancy of FIll', minval=1, maxval=99, group='Top and Bottom Lines', inline='1')
):
    pmarHigh: Persistent[float] = 0.0
    c_prcntSpctrm1: Persistent[list[Color]] = array.new_color(na)
    if barstate.isfirst:
        array.push(c_prcntSpctrm1, color.new('#0000FF'))
        array.push(c_prcntSpctrm1, color.new('#000AFF'))
        array.push(c_prcntSpctrm1, color.new('#0014FF'))
        array.push(c_prcntSpctrm1, color.new('#001FFF'))
        array.push(c_prcntSpctrm1, color.new('#0029FF'))
        array.push(c_prcntSpctrm1, color.new('#0033FF'))
        array.push(c_prcntSpctrm1, color.new('#003DFF'))
        array.push(c_prcntSpctrm1, color.new('#0047FF'))
        array.push(c_prcntSpctrm1, color.new('#0052FF'))
        array.push(c_prcntSpctrm1, color.new('#005CFF'))
        array.push(c_prcntSpctrm1, color.new('#0066FF'))
        array.push(c_prcntSpctrm1, color.new('#0070FF'))
        array.push(c_prcntSpctrm1, color.new('#007AFF'))
        array.push(c_prcntSpctrm1, color.new('#0085FF'))
        array.push(c_prcntSpctrm1, color.new('#008FFF'))
        array.push(c_prcntSpctrm1, color.new('#0099FF'))
        array.push(c_prcntSpctrm1, color.new('#00A3FF'))
        array.push(c_prcntSpctrm1, color.new('#00ADFF'))
        array.push(c_prcntSpctrm1, color.new('#00B8FF'))
        array.push(c_prcntSpctrm1, color.new('#00C2FF'))
        array.push(c_prcntSpctrm1, color.new('#00CCFF'))
        array.push(c_prcntSpctrm1, color.new('#00D6FF'))
        array.push(c_prcntSpctrm1, color.new('#00E0FF'))
        array.push(c_prcntSpctrm1, color.new('#00EBFF'))
        array.push(c_prcntSpctrm1, color.new('#00F5FF'))
        array.push(c_prcntSpctrm1, color.new('#00FFFF'))
        array.push(c_prcntSpctrm1, color.new('#00FFF5'))
        array.push(c_prcntSpctrm1, color.new('#00FFEB'))
        array.push(c_prcntSpctrm1, color.new('#00FFE0'))
        array.push(c_prcntSpctrm1, color.new('#00FFD6'))
        array.push(c_prcntSpctrm1, color.new('#00FFCC'))
        array.push(c_prcntSpctrm1, color.new('#00FFC2'))
        array.push(c_prcntSpctrm1, color.new('#00FFB8'))
        array.push(c_prcntSpctrm1, color.new('#00FFAD'))
        array.push(c_prcntSpctrm1, color.new('#00FFA3'))
        array.push(c_prcntSpctrm1, color.new('#00FF99'))
        array.push(c_prcntSpctrm1, color.new('#00FF8F'))
        array.push(c_prcntSpctrm1, color.new('#00FF85'))
        array.push(c_prcntSpctrm1, color.new('#00FF7A'))
        array.push(c_prcntSpctrm1, color.new('#00FF70'))
        array.push(c_prcntSpctrm1, color.new('#00FF66'))
        array.push(c_prcntSpctrm1, color.new('#00FF5C'))
        array.push(c_prcntSpctrm1, color.new('#00FF52'))
        array.push(c_prcntSpctrm1, color.new('#00FF47'))
        array.push(c_prcntSpctrm1, color.new('#00FF3D'))
        array.push(c_prcntSpctrm1, color.new('#00FF33'))
        array.push(c_prcntSpctrm1, color.new('#00FF29'))
        array.push(c_prcntSpctrm1, color.new('#00FF1F'))
        array.push(c_prcntSpctrm1, color.new('#00FF14'))
        array.push(c_prcntSpctrm1, color.new('#00FF0A'))
        array.push(c_prcntSpctrm1, color.new('#00FF00'))
        array.push(c_prcntSpctrm1, color.new('#0AFF00'))
        array.push(c_prcntSpctrm1, color.new('#14FF00'))
        array.push(c_prcntSpctrm1, color.new('#1FFF00'))
        array.push(c_prcntSpctrm1, color.new('#29FF00'))
        array.push(c_prcntSpctrm1, color.new('#33FF00'))
        array.push(c_prcntSpctrm1, color.new('#3DFF00'))
        array.push(c_prcntSpctrm1, color.new('#47FF00'))
        array.push(c_prcntSpctrm1, color.new('#52FF00'))
        array.push(c_prcntSpctrm1, color.new('#5CFF00'))
        array.push(c_prcntSpctrm1, color.new('#66FF00'))
        array.push(c_prcntSpctrm1, color.new('#70FF00'))
        array.push(c_prcntSpctrm1, color.new('#7AFF00'))
        array.push(c_prcntSpctrm1, color.new('#85FF00'))
        array.push(c_prcntSpctrm1, color.new('#8FFF00'))
        array.push(c_prcntSpctrm1, color.new('#99FF00'))
        array.push(c_prcntSpctrm1, color.new('#A3FF00'))
        array.push(c_prcntSpctrm1, color.new('#ADFF00'))
        array.push(c_prcntSpctrm1, color.new('#B8FF00'))
        array.push(c_prcntSpctrm1, color.new('#C2FF00'))
        array.push(c_prcntSpctrm1, color.new('#CCFF00'))
        array.push(c_prcntSpctrm1, color.new('#D6FF00'))
        array.push(c_prcntSpctrm1, color.new('#E0FF00'))
        array.push(c_prcntSpctrm1, color.new('#EBFF00'))
        array.push(c_prcntSpctrm1, color.new('#F5FF00'))
        array.push(c_prcntSpctrm1, color.new('#FFFF00'))
        array.push(c_prcntSpctrm1, color.new('#FFF500'))
        array.push(c_prcntSpctrm1, color.new('#FFEB00'))
        array.push(c_prcntSpctrm1, color.new('#FFE000'))
        array.push(c_prcntSpctrm1, color.new('#FFD600'))
        array.push(c_prcntSpctrm1, color.new('#FFCC00'))
        array.push(c_prcntSpctrm1, color.new('#FFC200'))
        array.push(c_prcntSpctrm1, color.new('#FFB800'))
        array.push(c_prcntSpctrm1, color.new('#FFAD00'))
        array.push(c_prcntSpctrm1, color.new('#FFA300'))
        array.push(c_prcntSpctrm1, color.new('#FF9900'))
        array.push(c_prcntSpctrm1, color.new('#FF8F00'))
        array.push(c_prcntSpctrm1, color.new('#FF8500'))
        array.push(c_prcntSpctrm1, color.new('#FF7A00'))
        array.push(c_prcntSpctrm1, color.new('#FF7000'))
        array.push(c_prcntSpctrm1, color.new('#FF6600'))
        array.push(c_prcntSpctrm1, color.new('#FF5C00'))
        array.push(c_prcntSpctrm1, color.new('#FF5200'))
        array.push(c_prcntSpctrm1, color.new('#FF4700'))
        array.push(c_prcntSpctrm1, color.new('#FF3D00'))
        array.push(c_prcntSpctrm1, color.new('#FF3300'))
        array.push(c_prcntSpctrm1, color.new('#FF2900'))
        array.push(c_prcntSpctrm1, color.new('#FF1F00'))
        array.push(c_prcntSpctrm1, color.new('#FF1400'))
        array.push(c_prcntSpctrm1, color.new('#FF0000'))
        array.push(c_prcntSpctrm1, color.new('#FF0000'))
    c_prcntSpctrm2: Persistent[list[Color]] = array.new_color(na)
    if barstate.isfirst:
        array.push(c_prcntSpctrm2, color.new('#0000FF'))
        array.push(c_prcntSpctrm2, color.new('#0200FC'))
        array.push(c_prcntSpctrm2, color.new('#0500F9'))
        array.push(c_prcntSpctrm2, color.new('#0700F7'))
        array.push(c_prcntSpctrm2, color.new('#0A00F4'))
        array.push(c_prcntSpctrm2, color.new('#0C00F2'))
        array.push(c_prcntSpctrm2, color.new('#0F00EF'))
        array.push(c_prcntSpctrm2, color.new('#1100ED'))
        array.push(c_prcntSpctrm2, color.new('#1400EA'))
        array.push(c_prcntSpctrm2, color.new('#1600E8'))
        array.push(c_prcntSpctrm2, color.new('#1900E5'))
        array.push(c_prcntSpctrm2, color.new('#1C00E2'))
        array.push(c_prcntSpctrm2, color.new('#1E00E0'))
        array.push(c_prcntSpctrm2, color.new('#2100DD'))
        array.push(c_prcntSpctrm2, color.new('#2300DB'))
        array.push(c_prcntSpctrm2, color.new('#2600D8'))
        array.push(c_prcntSpctrm2, color.new('#2800D6'))
        array.push(c_prcntSpctrm2, color.new('#2B00D3'))
        array.push(c_prcntSpctrm2, color.new('#2D00D1'))
        array.push(c_prcntSpctrm2, color.new('#3000CE'))
        array.push(c_prcntSpctrm2, color.new('#3300CC'))
        array.push(c_prcntSpctrm2, color.new('#3500C9'))
        array.push(c_prcntSpctrm2, color.new('#3800C6'))
        array.push(c_prcntSpctrm2, color.new('#3A00C4'))
        array.push(c_prcntSpctrm2, color.new('#3D00C1'))
        array.push(c_prcntSpctrm2, color.new('#3F00BF'))
        array.push(c_prcntSpctrm2, color.new('#4200BC'))
        array.push(c_prcntSpctrm2, color.new('#4400BA'))
        array.push(c_prcntSpctrm2, color.new('#4700B7'))
        array.push(c_prcntSpctrm2, color.new('#4900B5'))
        array.push(c_prcntSpctrm2, color.new('#4C00B2'))
        array.push(c_prcntSpctrm2, color.new('#4F00AF'))
        array.push(c_prcntSpctrm2, color.new('#5100AD'))
        array.push(c_prcntSpctrm2, color.new('#5400AA'))
        array.push(c_prcntSpctrm2, color.new('#5600A8'))
        array.push(c_prcntSpctrm2, color.new('#5900A5'))
        array.push(c_prcntSpctrm2, color.new('#5B00A3'))
        array.push(c_prcntSpctrm2, color.new('#5E00A0'))
        array.push(c_prcntSpctrm2, color.new('#60009E'))
        array.push(c_prcntSpctrm2, color.new('#63009B'))
        array.push(c_prcntSpctrm2, color.new('#660099'))
        array.push(c_prcntSpctrm2, color.new('#680096'))
        array.push(c_prcntSpctrm2, color.new('#6B0093'))
        array.push(c_prcntSpctrm2, color.new('#6D0091'))
        array.push(c_prcntSpctrm2, color.new('#70008E'))
        array.push(c_prcntSpctrm2, color.new('#72008C'))
        array.push(c_prcntSpctrm2, color.new('#750089'))
        array.push(c_prcntSpctrm2, color.new('#770087'))
        array.push(c_prcntSpctrm2, color.new('#7A0084'))
        array.push(c_prcntSpctrm2, color.new('#7C0082'))
        array.push(c_prcntSpctrm2, color.new('#7F007F'))
        array.push(c_prcntSpctrm2, color.new('#82007C'))
        array.push(c_prcntSpctrm2, color.new('#84007A'))
        array.push(c_prcntSpctrm2, color.new('#870077'))
        array.push(c_prcntSpctrm2, color.new('#890075'))
        array.push(c_prcntSpctrm2, color.new('#8C0072'))
        array.push(c_prcntSpctrm2, color.new('#8E0070'))
        array.push(c_prcntSpctrm2, color.new('#91006D'))
        array.push(c_prcntSpctrm2, color.new('#93006B'))
        array.push(c_prcntSpctrm2, color.new('#960068'))
        array.push(c_prcntSpctrm2, color.new('#990066'))
        array.push(c_prcntSpctrm2, color.new('#9B0063'))
        array.push(c_prcntSpctrm2, color.new('#9E0060'))
        array.push(c_prcntSpctrm2, color.new('#A0005E'))
        array.push(c_prcntSpctrm2, color.new('#A3005B'))
        array.push(c_prcntSpctrm2, color.new('#A50059'))
        array.push(c_prcntSpctrm2, color.new('#A80056'))
        array.push(c_prcntSpctrm2, color.new('#AA0054'))
        array.push(c_prcntSpctrm2, color.new('#AD0051'))
        array.push(c_prcntSpctrm2, color.new('#AF004F'))
        array.push(c_prcntSpctrm2, color.new('#B2004C'))
        array.push(c_prcntSpctrm2, color.new('#B50049'))
        array.push(c_prcntSpctrm2, color.new('#B70047'))
        array.push(c_prcntSpctrm2, color.new('#BA0044'))
        array.push(c_prcntSpctrm2, color.new('#BC0042'))
        array.push(c_prcntSpctrm2, color.new('#BF003F'))
        array.push(c_prcntSpctrm2, color.new('#C1003D'))
        array.push(c_prcntSpctrm2, color.new('#C4003A'))
        array.push(c_prcntSpctrm2, color.new('#C60038'))
        array.push(c_prcntSpctrm2, color.new('#C90035'))
        array.push(c_prcntSpctrm2, color.new('#CC0033'))
        array.push(c_prcntSpctrm2, color.new('#CE0030'))
        array.push(c_prcntSpctrm2, color.new('#D1002D'))
        array.push(c_prcntSpctrm2, color.new('#D3002B'))
        array.push(c_prcntSpctrm2, color.new('#D60028'))
        array.push(c_prcntSpctrm2, color.new('#D80026'))
        array.push(c_prcntSpctrm2, color.new('#DB0023'))
        array.push(c_prcntSpctrm2, color.new('#DD0021'))
        array.push(c_prcntSpctrm2, color.new('#E0001E'))
        array.push(c_prcntSpctrm2, color.new('#E2001C'))
        array.push(c_prcntSpctrm2, color.new('#E50019'))
        array.push(c_prcntSpctrm2, color.new('#E80016'))
        array.push(c_prcntSpctrm2, color.new('#EA0014'))
        array.push(c_prcntSpctrm2, color.new('#ED0011'))
        array.push(c_prcntSpctrm2, color.new('#EF000F'))
        array.push(c_prcntSpctrm2, color.new('#F2000C'))
        array.push(c_prcntSpctrm2, color.new('#F4000A'))
        array.push(c_prcntSpctrm2, color.new('#F70007'))
        array.push(c_prcntSpctrm2, color.new('#F90005'))
        array.push(c_prcntSpctrm2, color.new('#FC0002'))
        array.push(c_prcntSpctrm2, color.new('#FF0000'))
    def f_prior_sum(_P: Series, _X):
        return math.sum(_P[1], _X - 1)

    def f_ma_val(_P, _typ, _len):
        return ta.sma(_P, _len) if _typ == 'SMA' else ta.ema(_P, _len) if _typ == 'EMA' else ta.rma(_P, _len) if _typ == 'RMA' else ta.hma(_P, _len) if _typ == 'HMA' else ta.vwma(_P, _len)

    def f_pmarp(_price, _pmarLen, _pmarpLen, _type):
        _pmar: Series = math.abs(_price / f_ma_val(_price, _type, _pmarLen))
        _pmarpSum: int = 0
        _len = bar_index if bar_index < _pmarpLen else _pmarpLen
        for i in pine_range(1, _len, 1):
            _pmarpSum = _pmarpSum + (0 if _pmar[i] > _pmar else 1)
        _return = _pmarpSum / _len * 100 if bar_index >= _pmarLen else na
        return _return

    def f_clrSlct(_percent, _select, _type, _solid, _array1, _array2):
        return _solid if _select == 'Solid' else array.get(_array1 if _type == 'Blue Green Red' else _array2, math.round(_percent))

    pmarpOn = i_p_type_line == 'Price Moving Average Ratio Percentile'
    ma = f_ma_val(i_src_price, i_ma_typ, i_ma_len)
    pmar = i_src_price / ma
    pmarp = f_pmarp(i_src_price, i_ma_len, i_pmarp_lookback, i_ma_typ)
    pmarHigh = pmar if pmar > pmarHigh else pmarHigh
    c_pmar = pmar / pmarHigh * 100
    plotline = pmarp if pmarpOn else pmar
    c_plotline = f_clrSlct(plotline if pmarpOn else c_pmar, i_c_typ_line, i_c_typ_spctrm_line, i_c_solid_line, c_prcntSpctrm1, c_prcntSpctrm2)
    signal_ma = f_ma_val(plotline, i_signal_ma_typ, i_signal_ma_Len)
    c_plotsig = f_clrSlct(signal_ma, i_c_typ_sig, i_c_typ_spctrm_sig, i_c_solid_sig, c_prcntSpctrm1, c_prcntSpctrm2)
    hi_alert = i_hi_alert_pmarp if pmarpOn else i_hi_alert_pmar
    lo_alert = i_lo_alert_pmarp if pmarpOn else i_lo_alert_pmar
    hi_alertc = i_hi_alert_pmarp if pmarpOn else 100 if i_hi_alert_pmar > pmarHigh else i_hi_alert_pmar / pmarHigh * 100
    c_hi_alert = f_clrSlct(hi_alertc, i_c_typ_line, i_c_typ_spctrm_sig, i_c_solid_sig, c_prcntSpctrm1, c_prcntSpctrm2)
    c_lo_alert = f_clrSlct(lo_alert, i_c_typ_line, i_c_typ_spctrm_sig, i_c_solid_sig, c_prcntSpctrm1, c_prcntSpctrm2)
    c_bg = color.new(f_clrSlct(pmarp, i_c_typ_line, i_c_typ_spctrm_line, i_c_solid_line, c_prcntSpctrm1, c_prcntSpctrm2), 50)
    p_hi_alert = plotline > hi_alert
    p_lo_alert = plotline < lo_alert
    p_scaleHi = plot(100 if pmarpOn else na, 'Scale high', color.new('#FF0000'), style=plot.style_line)
    p_midLine = plot(50 if pmarpOn else na, 'Midline', color.new('#555555'), style=plot.style_line)
    p_scaleLo = plot(0 if pmarpOn else na, 'Scale low', color.new('#0000FF'), style=plot.style_line)
    plot(plotline, 'Plot line', c_plotline, math.max(1, i_p_width_line), editable=False)
    plot(na if pmarpOn else pmarHigh, 'Historical PMAR high', f_clrSlct(100, i_c_typ_line, i_c_typ_spctrm_line, i_c_solid_line, c_prcntSpctrm1, c_prcntSpctrm2), math.max(1, i_p_width_line), editable=False)
    plot(signal_ma if i_show_signal_ma else na, 'Signal line', c_plotsig, math.max(1, i_p_width_sig), editable=False)
    plot(i_hi_alert_pmarp if i_hi_alert_line_on and pmarpOn else i_hi_alert_pmar, 'High alert level', c_hi_alert, style=plot.style_line)
    plot(i_lo_alert_pmarp if i_lo_alert_line_on and pmarpOn else i_lo_alert_pmar, 'Low alert level', c_lo_alert, style=plot.style_line)
    bgcolor(c_bg if p_hi_alert and i_hi_alert_line_on and i_bg_hi_signal_on else na)
    bgcolor(c_bg if p_lo_alert and i_lo_alert_line_on and i_bg_lo_signal_on else na)
    PHI = (1 + math.sqrt(5)) / 2
    PI = cast_int(104348 / 33215)
    BULL: int = 1
    BEAR = -1
    NONE: int = 0
    GRN01: Color = color.new('#7CFC00')
    GRN02: Color = color.new('#32CD32')
    GRN03: Color = color.new('#228B22')
    GRN04: Color = color.new('#006400')
    GRN05: Color = color.new('#008000')
    GRN06: Color = color.new('#093507')
    RED01: Color = color.new('#FF4500')
    RED02: Color = color.new('#FF0000')
    RED03: Color = color.new('#B22222')
    RED04: Color = color.new('#8B0000')
    RED05: Color = color.new('#800000')
    RED06: Color = color.new('#330D06')
    AQUA: Color = color.new('#00FFFF')
    BLACK: Color = color.new('#000000')
    BLUE: Color = color.new('#0000FF')
    FUCHSIA: Color = color.new('#FF00FF')
    GRAY: Color = color.new('#808080')
    GREEN: Color = color.new('#008000')
    LIME: Color = color.new('#00FF00')
    MAROON: Color = color.new('#800000')
    NAVY: Color = color.new('#000080')
    OLIVE: Color = color.new('#808000')
    ORANGE: Color = color.new('#FF7F00')
    PURPLE: Color = color.new('#800080')
    RUBI: Color = color.new('#FF0000')
    SILVER: Color = color.new('#C0C0C0')
    TEAL: Color = color.new('#008080')
    YELLOW: Color = color.new('#FFFF00')
    WHITE: Color = color.new('#FFFFFF')
    def maColor(_ma, _maRef):
        diffMA = ta.change(_ma)
        macol = LIME if diffMA >= 0 and _ma > _maRef else MAROON if diffMA < 0 and _ma > _maRef else RUBI if diffMA <= 0 and _ma < _maRef else GREEN if diffMA >= 0 and _ma < _maRef else GRAY
        return macol

    src = close
    ma05 = ta.ema(src, 5) if i_exp else ta.sma(src, 5)
    ma10 = ta.ema(src, 10) if i_exp else ta.sma(src, 10)
    ma15 = ta.ema(src, 15) if i_exp else ta.sma(src, 15)
    ma20 = ta.ema(src, 20) if i_exp else ta.sma(src, 20)
    ma25 = ta.ema(src, 25) if i_exp else ta.sma(src, 25)
    ma30 = ta.ema(src, 30) if i_exp else ta.sma(src, 30)
    ma35 = ta.ema(src, 35) if i_exp else ta.sma(src, 35)
    ma40 = ta.ema(src, 40) if i_exp else ta.sma(src, 40)
    ma45 = ta.ema(src, 45) if i_exp else ta.sma(src, 45)
    ma50 = ta.ema(src, 50) if i_exp else ta.sma(src, 50)
    ma55 = ta.ema(src, 55) if i_exp else ta.sma(src, 55)
    ma60 = ta.ema(src, 60) if i_exp else ta.sma(src, 60)
    ma65 = ta.ema(src, 65) if i_exp else ta.sma(src, 65)
    ma70 = ta.ema(src, 70) if i_exp else ta.sma(src, 70)
    ma75 = ta.ema(src, 75) if i_exp else ta.sma(src, 75)
    ma80 = ta.ema(src, 80) if i_exp else ta.sma(src, 80)
    ma85 = ta.ema(src, 85) if i_exp else ta.sma(src, 85)
    ma90 = ta.ema(src, 90) if i_exp else ta.sma(src, 90)
    ma100 = ta.ema(src, 100) if i_exp else ta.sma(src, 100)
    greenMA_1 = ma05 > ma100
    greenMA_2 = ma10 > ma100
    greenMA_3 = ma15 > ma100
    greenMA_4 = ma20 > ma100
    greenMA_5 = ma25 > ma100
    greenMA_6 = ma30 > ma100
    greenMA_7 = ma35 > ma100
    greenMA_8 = ma40 > ma100
    greenMA_9 = ma45 > ma100
    greenMA_10 = ma50 > ma100
    greenMA_11 = ma55 > ma100
    greenMA_12 = ma60 > ma100
    greenMA_13 = ma65 > ma100
    greenMA_14 = ma70 > ma100
    greenMA_15 = ma75 > ma100
    greenMA_16 = ma80 > ma100
    greenMA_17 = ma85 > ma100
    greenMA_18 = ma90 > ma100
    redMA_1 = ma05 < ma100
    redMA_2 = ma10 < ma100
    redMA_3 = ma15 < ma100
    redMA_4 = ma20 < ma100
    redMA_5 = ma25 < ma100
    redMA_6 = ma30 < ma100
    redMA_7 = ma35 < ma100
    redMA_8 = ma40 < ma100
    redMA_9 = ma45 < ma100
    redMA_10 = ma50 < ma100
    redMA_11 = ma55 < ma100
    redMA_12 = ma60 < ma100
    redMA_13 = ma65 < ma100
    redMA_14 = ma70 < ma100
    redMA_15 = ma75 < ma100
    redMA_16 = ma80 < ma100
    redMA_17 = ma85 < ma100
    redMA_18 = ma90 < ma100
    Diffma1 = ta.change(ma05)
    Diffma2 = ta.change(ma10)
    Diffma3 = ta.change(ma15)
    Diffma4 = ta.change(ma20)
    Diffma5 = ta.change(ma25)
    Diffma6 = ta.change(ma30)
    Diffma7 = ta.change(ma35)
    Diffma8 = ta.change(ma40)
    Diffma9 = ta.change(ma45)
    Diffma10 = ta.change(ma50)
    Diffma11 = ta.change(ma55)
    Diffma12 = ta.change(ma60)
    Diffma13 = ta.change(ma65)
    Diffma14 = ta.change(ma70)
    Diffma15 = ta.change(ma75)
    Diffma16 = ta.change(ma80)
    Diffma17 = ta.change(ma85)
    Diffma18 = ta.change(ma90)
    Diffma1P = ta.change(ma05) >= 0
    Diffma2P = ta.change(ma10) >= 0
    Diffma3P = ta.change(ma15) >= 0
    Diffma4P = ta.change(ma20) >= 0
    Diffma5P = ta.change(ma25) >= 0
    Diffma6P = ta.change(ma30) >= 0
    Diffma7P = ta.change(ma35) >= 0
    Diffma8P = ta.change(ma40) >= 0
    Diffma9P = ta.change(ma45) >= 0
    Diffma10P = ta.change(ma50) >= 0
    Diffma11P = ta.change(ma55) >= 0
    Diffma12P = ta.change(ma60) >= 0
    Diffma13P = ta.change(ma65) >= 0
    Diffma14P = ta.change(ma70) >= 0
    Diffma15P = ta.change(ma75) >= 0
    Diffma16P = ta.change(ma80) >= 0
    Diffma17P = ta.change(ma85) >= 0
    Diffma18P = ta.change(ma90) >= 0
    Diffma1N = ta.change(ma05) < 0
    Diffma2N = ta.change(ma10) < 0
    Diffma3N = ta.change(ma15) < 0
    Diffma4N = ta.change(ma20) < 0
    Diffma5N = ta.change(ma25) < 0
    Diffma6N = ta.change(ma30) < 0
    Diffma7N = ta.change(ma35) < 0
    Diffma8N = ta.change(ma40) < 0
    Diffma9N = ta.change(ma45) < 0
    Diffma10N = ta.change(ma50) < 0
    Diffma11N = ta.change(ma55) < 0
    Diffma12N = ta.change(ma60) < 0
    Diffma13N = ta.change(ma65) < 0
    Diffma14N = ta.change(ma70) < 0
    Diffma15N = ta.change(ma75) < 0
    Diffma16N = ta.change(ma80) < 0
    Diffma17N = ta.change(ma85) < 0
    Diffma18N = ta.change(ma90) < 0
    Lime1 = Diffma1P and greenMA_1
    Red1 = Diffma1N and redMA_1
    Maroon1 = Diffma1N and greenMA_1
    Green1 = Diffma1P and redMA_1
    Lime2 = Diffma2P and greenMA_2
    Red2 = Diffma2N and redMA_2
    Maroon2 = Diffma2N and greenMA_2
    Green2 = Diffma2P and redMA_2
    Lime3 = Diffma3P and greenMA_3
    Red3 = Diffma3N and redMA_3
    Maroon3 = Diffma3N and greenMA_3
    Green3 = Diffma3P and redMA_3
    Lime4 = Diffma4P and greenMA_4
    Red4 = Diffma4N and redMA_4
    Maroon4 = Diffma4N and greenMA_4
    Green4 = Diffma4P and redMA_4
    Lime5 = Diffma5P and greenMA_5
    Red5 = Diffma5N and redMA_5
    Maroon5 = Diffma5N and greenMA_5
    Green5 = Diffma5P and redMA_5
    Lime6 = Diffma6P and greenMA_6
    Red6 = Diffma6N and redMA_6
    Maroon6 = Diffma6N and greenMA_6
    Green6 = Diffma6P and redMA_6
    Lime7 = Diffma7P and greenMA_7
    Red7 = Diffma7N and redMA_7
    Maroon7 = Diffma7N and greenMA_7
    Green7 = Diffma7P and redMA_7
    Lime8 = Diffma8P and greenMA_8
    Red8 = Diffma8N and redMA_8
    Maroon8 = Diffma8N and greenMA_8
    Green8 = Diffma8P and redMA_8
    Lime9 = Diffma9P and greenMA_9
    Red9 = Diffma9N and redMA_9
    Maroon9 = Diffma9N and greenMA_9
    Green9 = Diffma9P and redMA_9
    Lime10 = Diffma10P and greenMA_10
    Red10 = Diffma10N and redMA_10
    Maroon10 = Diffma10N and greenMA_10
    Green10 = Diffma10P and redMA_10
    Lime11 = Diffma11P and greenMA_11
    Red11 = Diffma11N and redMA_11
    Maroon11 = Diffma11N and greenMA_11
    Green11 = Diffma11P and redMA_11
    Lime12 = Diffma12P and greenMA_12
    Red12 = Diffma12N and redMA_12
    Maroon12 = Diffma12N and greenMA_12
    Green12 = Diffma12P and redMA_12
    Lime13 = Diffma13P and greenMA_13
    Red13 = Diffma13N and redMA_13
    Maroon13 = Diffma13N and greenMA_13
    Green13 = Diffma13P and redMA_13
    Lime14 = Diffma14P and greenMA_14
    Red14 = Diffma14N and redMA_14
    Maroon14 = Diffma14N and greenMA_14
    Green14 = Diffma14P and redMA_14
    Lime15 = Diffma15P and greenMA_15
    Red15 = Diffma15N and redMA_15
    Maroon15 = Diffma15N and greenMA_15
    Green15 = Diffma15P and redMA_15
    Lime16 = Diffma16P and greenMA_16
    Red16 = Diffma16N and redMA_16
    Maroon16 = Diffma16N and greenMA_16
    Green16 = Diffma16P and redMA_16
    Lime17 = Diffma17P and greenMA_17
    Red17 = Diffma17N and redMA_17
    Maroon17 = Diffma17N and greenMA_17
    Green17 = Diffma17P and redMA_17
    Lime18 = Diffma18P and greenMA_18
    Red18 = Diffma18N and redMA_18
    Maroon18 = Diffma18N and greenMA_18
    Green18 = Diffma18P and redMA_18
    lime_Long = Lime1 and Lime2 and Lime3 and Lime4 and Lime5 and Lime6 and Lime7 and Lime8 and Lime9 and Lime10 and Lime11 and Lime12 and Lime13 and Lime14 and Lime15 and Lime16 and Lime17 and Lime18
    red_Short = Red1 and Red2 and Red3 and Red4 and Red5 and Red6 and Red7 and Red8 and Red9 and Red10 and Red12 and Red12 and Red13 and Red14 and Red15 and Red16 and Red17 and Red18
    maroon_Short = Maroon1 and Maroon2 and Maroon3 and Maroon4 and Maroon5 and Maroon6 and Maroon7 and Maroon8 and Maroon9 and Maroon10 and Maroon11 and Maroon12 and Maroon13 and Maroon14 and Maroon15 and Maroon16 and Maroon17 and Maroon18
    green_Long = Green1 and Green2 and Green3 and Green4 and Green5 and Green6 and Green7 and Green8 and Green9 and Green10 and Green11 and Green12 and Green13 and Green14 and Green15 and Green16 and Green17 and Green18
    r = ta.rsi(close, 14)
    s = ta.stoch(close, 14, 1, 3)
    rP = r <= 55
    rM = r >= 75
    noREL = strategy.opentrades == 0 and strategy.position_size > 0
    noRES = strategy.opentrades == 0 and strategy.position_size < 0
    noENGL = close[1] > open[1]
    if lime_Long and (not noREL) and (not noENGL) and (not rP):
        strategy.entry('Long', strategy.long)
    if red_Short and (not noRES):
        strategy.entry('Short', strategy.short)
    def entry_index():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.closedtrades + 1) if strategy.opentrades > 0 else na

    def StopLoss():
        __block_result__ = na
        if entry_index() != 0 and strategy.position_size > 0:
            __block_result__ = low[1]
        elif entry_index() != 0 and strategy.position_size < 0:
            __block_result__ = high[1]
        else:
            __block_result__ = na
        return __block_result__

    if strategy.position_size > 0 and pmarp >= 99 and (red_Short == True):
        strategy.close('Long')
    if strategy.position_size < 0 and pmarp <= 1:
        strategy.close('Short')
    takeP = __input_25__ / 100
    stopL = __input_26__ / 100
    Stop_L = strategy.position_avg_price * (1 - stopL)
    Stop_S = strategy.position_avg_price * (1 + stopL)
    Take_S = strategy.position_avg_price * (1 - takeP)
    Take_L = strategy.position_avg_price * (1 + takeP)
    if strategy.position_size > 0:
        strategy.exit('Close Long', limit=Take_L, stop=Stop_L)
    if strategy.position_size < 0:
        strategy.exit('Close Short', limit=Take_S, stop=Stop_S)
    H3B = 100 - H3A
    H1P = hline(H1, 'Top Line', color.new('#5BE14D'), hline.style_dotted, 2, True)
    H2P = hline(H2, 'Bottom Line', color.new('#E14D60'), hline.style_dotted, 2, True)
    fill(H1P, H2P, color.new(color.new('#E1CB5F'), H3B), 'Line fills', editable=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
