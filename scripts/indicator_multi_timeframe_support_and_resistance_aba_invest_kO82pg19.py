"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, fixnan, high, input, low, math, na, nz, plot, request,
    script, syminfo, ta
)
from pynecore.types import Series


@script.indicator(title='Multi Timeframe Support and Resistance [ABA Invest]', shorttitle='MTF SnR [ABA Invest]', overlay=True)
def main(
    bars=input.int(15, title='Pivot'),
    tipe=input.string('Body', title='Type', options=('Wick', 'Body')),
    show_c=input.bool(True, title='Current Timeframe', group='Timeframes'),
    show_5m=input.bool(False, title='M5', group='Timeframes'),
    show_15m=input.bool(False, title='M15', group='Timeframes'),
    show_30m=input.bool(False, title='M30', group='Timeframes'),
    show_1h=input.bool(False, title='H1', group='Timeframes'),
    show_4h=input.bool(False, title='H4', group='Timeframes'),
    show_d=input.bool(False, title='Daily', group='Timeframes'),
    show_w=input.bool(False, title='Weekly', group='Timeframes'),
    plot_ama=input.bool(False, title='Adaptive Moving Average'),
    ama_length=input.int(15, title='Line Length')
):
    pivot_high_5m = fixnan(request.security(syminfo.tickerid, '5', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_15m = fixnan(request.security(syminfo.tickerid, '15', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_30m = fixnan(request.security(syminfo.tickerid, '30', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_1h = fixnan(request.security(syminfo.tickerid, '60', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_4h = fixnan(request.security(syminfo.tickerid, '240', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_d = fixnan(request.security(syminfo.tickerid, 'D', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_w = fixnan(request.security(syminfo.tickerid, 'W', inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_high_c = fixnan(inline_series(ta.pivothigh(high if tipe == 'Wick' else close, bars, bars), 1))
    pivot_low_5m = fixnan(request.security(syminfo.tickerid, '5', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_15m = fixnan(request.security(syminfo.tickerid, '15', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_30m = fixnan(request.security(syminfo.tickerid, '30', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_1h = fixnan(request.security(syminfo.tickerid, '60', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_4h = fixnan(request.security(syminfo.tickerid, '240', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_d = fixnan(request.security(syminfo.tickerid, 'D', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_w = fixnan(request.security(syminfo.tickerid, 'W', inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1)))
    pivot_low_c = fixnan(inline_series(ta.pivotlow(low if tipe == 'Wick' else close, bars, bars), 1))
    resistance_high_5m = plot(pivot_high_5m if show_5m else na, color=na if cast_bool(ta.change(pivot_high_5m)) else color.new('#00AEFF'), offset=-bars - 1, linewidth=2, title='Resistance M5')
    resistance_low_5m = plot(pivot_low_5m if show_5m else na, color=na if cast_bool(ta.change(pivot_low_5m)) else color.new('#FFBF00'), offset=-bars - 1, linewidth=2, title='Support M5')
    resistance_high_15m = plot(pivot_high_15m if show_15m else na, color=na if cast_bool(ta.change(pivot_high_15m)) else color.new('#00AEFFDD'), offset=-bars - 1, linewidth=2, title='Resistance M15')
    resistance_low_15m = plot(pivot_low_15m if show_15m else na, color=na if cast_bool(ta.change(pivot_low_15m)) else color.new('#FFBF00DD'), offset=-bars - 1, linewidth=2, title='Support M15')
    resistance_high_30m = plot(pivot_high_30m if show_30m else na, color=na if cast_bool(ta.change(pivot_high_30m)) else color.new('#00AEFFBB'), offset=-bars - 1, linewidth=2, title='Resistance M30')
    resistance_low_30m = plot(pivot_low_30m if show_30m else na, color=na if cast_bool(ta.change(pivot_low_30m)) else color.new('#FFBF00BB'), offset=-bars - 1, linewidth=2, title='Support M30')
    resistance_high_1h = plot(pivot_high_1h if show_1h else na, color=na if cast_bool(ta.change(pivot_high_1h)) else color.new('#00AEFF90'), offset=-bars - 1, linewidth=2, title='Resistance H1')
    resistance_low_1h = plot(pivot_low_1h if show_1h else na, color=na if cast_bool(ta.change(pivot_low_1h)) else color.new('#FFBF0090'), offset=-bars - 1, linewidth=2, title='Support H1')
    resistance_high_4h = plot(pivot_high_4h if show_4h else na, color=na if cast_bool(ta.change(pivot_high_4h)) else color.new('#00AEFF70'), offset=-bars - 1, linewidth=2, title='Resistance H4')
    resistance_low_4h = plot(pivot_low_4h if show_4h else na, color=na if cast_bool(ta.change(pivot_low_4h)) else color.new('#FFBF0070'), offset=-bars - 1, linewidth=2, title='Support H4')
    resistance_high_d = plot(pivot_high_d if show_d else na, color=na if cast_bool(ta.change(pivot_high_d)) else color.new('#00AEFF50'), offset=-bars - 1, linewidth=2, title='Resistance Daily')
    resistance_low_d = plot(pivot_low_d if show_d else na, color=na if cast_bool(ta.change(pivot_low_d)) else color.new('#FFBF0050'), offset=-bars - 1, linewidth=2, title='Support Daily')
    resistance_high_w = plot(pivot_high_w if show_w else na, color=na if cast_bool(ta.change(pivot_high_w)) else color.new('#00AEFF30'), offset=-bars - 1, linewidth=2, title='Resistance Weekly')
    resistance_low_w = plot(pivot_low_w if show_w else na, color=na if cast_bool(ta.change(pivot_low_w)) else color.new('#FFBF0030'), offset=-bars - 1, linewidth=2, title='Support Weekly')
    resistance_high_c = plot(pivot_high_c if show_c else na, color=na if cast_bool(ta.change(pivot_high_c)) else color.new('#FF0040'), offset=-bars - 1, linewidth=2, title='Resistance Current Timeframe')
    resistance_low_c = plot(pivot_low_c if show_c else na, color=na if cast_bool(ta.change(pivot_low_c)) else color.new('#6AFF00'), offset=-bars - 1, linewidth=2, title='Support Current Timeframe')
    amarc = close
    ama: Series[float] = 0
    hh = math.max(math.sign(ta.change(ta.highest(ama_length))), 0)
    ll = math.max(math.sign(ta.change(ta.lowest(ama_length)) * -1), 0)
    tc = math.pow(ta.sma(1 if cast_bool(hh) or cast_bool(ll) else 0, ama_length), 2)
    ama = nz(ama[1] + tc * (amarc - ama[1]), amarc)
    garis_ama = plot(ama if plot_ama else na, 'Adaptive Moving Average', color.new('#FFFFFF'), 2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
