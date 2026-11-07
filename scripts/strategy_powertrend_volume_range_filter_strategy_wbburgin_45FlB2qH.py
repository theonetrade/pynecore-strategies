"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, barcolor, close, color, fill, input, location, na, nz, plot,
    plotshape, script, shape, size, strategy, ta, volume
)
from pynecore.types import Series
import lib.wbburgin.wbburgin_utils.v2 as utils


@script.strategy('Powertrend - Volume Range Filter [wbburgin]', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_value=0.0, slippage=0, shorttitle='Powertrend [wbburgin]', margin_long=0, margin_short=0, close_by_id=True)
def main(
    l=input.int(200, 'Length', group='General'),
    useadx=input.bool(False, 'ADX Filter', group='Filters', inline='ADX'),
    lengthadx=input.int(14, title='', group='Filters', inline='ADX'),
    usehl=input.bool(False, 'Range Supertrend', group='Filters', inline='HL'),
    lengthhl=input.int(14, title='', group='Filters', inline='HL'),
    showhl=input.bool(False, 'Plot', group='Filters', inline='HL'),
    usevwma=input.bool(False, 'VWMA Filter', group='Filters', inline='VWMA'),
    lengthvwma=input.int(200, title='', group='Filters', inline='VWMA'),
    showvwma=input.bool(False, 'Plot', group='Filters', inline='VWMA'),
    highlighting=input.bool(True, 'Highlighting', group='Display'),
    barcolors=input.bool(True, 'Bar Colors', group='Display'),
    buyselllabels=input.bool(True, 'Entry-Exit Labels', group='Display')
):
    def rngfilt_volumeadj(source1: float, tethersource: Series[float], smoothrng: float):
        rngfilt: Series = source1
        if tethersource > nz(tethersource[1]):
            rngfilt = nz(rngfilt[1]) if source1 - smoothrng < nz(rngfilt[1]) else source1 - smoothrng
        else:
            rngfilt = nz(rngfilt[1]) if source1 + smoothrng > nz(rngfilt[1]) else source1 + smoothrng
        return rngfilt

    volrng = rngfilt_volumeadj(close, volume, utils.smoothrng(close, l, 3))
    smoothrng = utils.smoothrng(close, l, 3)
    basetype = volrng
    hband = basetype + smoothrng
    lowband = basetype - smoothrng
    uprng = utils.trendUp(basetype)
    x, y, adx = ta.dmi(lengthadx, lengthadx)
    adx_vwma = ta.vwma(adx, lengthadx)
    adx_filter = True if not useadx else True if adx > adx_vwma else False
    lowband_trendfollow: Series = ta.lowest(lowband, lengthhl)
    highband_trendfollow: Series = ta.highest(hband, lengthhl)
    in_general_uptrend = ta.barssince(ta.crossover(close, highband_trendfollow[1])) < ta.barssince(ta.crossunder(close, lowband_trendfollow[1]))
    igu_filter_positive = True if not usehl else True if in_general_uptrend else False
    igu_filter_negative = True if not usehl else True if not in_general_uptrend else False
    vwma = ta.vwma(volrng, lengthvwma)
    vwma_filter_positive = True if not usevwma else True if volrng > vwma else False
    crossover_1 = ta.crossover(close, hband)
    b = cast_bool(uprng) and crossover_1 and igu_filter_positive and adx_filter and vwma_filter_positive
    crossunder_1 = ta.crossunder(close, lowband)
    s = not uprng and crossunder_1 and igu_filter_negative and adx_filter
    in_b = inline_series(ta.barssince(b), 1) < inline_series(ta.barssince(s), 1)
    in_s = inline_series(ta.barssince(s), 1) < inline_series(ta.barssince(b), 1)
    if b:
        strategy.entry('Long', strategy.long)
        alert('Powertrend Entry', freq=alert.freq_once_per_bar)
    if s:
        strategy.close('Long')
        alert('Powertrend Exit', freq=alert.freq_once_per_bar)
    mp = plot(basetype, color=color.white, title='Volume Range')
    hp = plot(hband, color=na, title='High Range')
    lp = plot(lowband, color=na, title='Low Range')
    bb = plot(na if not showhl else lowband_trendfollow if in_general_uptrend else na, color=color.lime, title='Bullish Trend Follow', style=plot.style_linebr)
    uu = plot(na if not showhl else highband_trendfollow if not in_general_uptrend else na, color=color.yellow, title='Bearish Trend Follow', style=plot.style_linebr)
    plot(na if not showvwma else vwma, color=color.orange, title='VWMA')
    fill(hp, mp, color=na if not highlighting else color.new(color.lime, 88))
    fill(mp, lp, color=na if not highlighting else color.new(color.yellow, 88))
    fill(uu, hp, color=na if not highlighting else na if in_general_uptrend else color.new(color.red, 88))
    fill(bb, lp, color=na if not highlighting else na if not in_general_uptrend else color.new(color.blue, 88))
    plotshape(lowband if b and (not in_b) and buyselllabels else na, 'Buy Label', style=shape.labelup, location=location.absolute, color=color.green, textcolor=color.white, text='Buy', size=size.tiny)
    plotshape(hband if s and (not in_s) and buyselllabels else na, 'Sell Label', style=shape.labeldown, location=location.absolute, color=color.red, textcolor=color.white, text='Sell', size=size.tiny)
    barcolor((color.lime if cast_bool(uprng) else color.yellow) if barcolors else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
