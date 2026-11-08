"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, barcolor, close, color, high, hl2, hlc3, hlcc4, input,
    location, low, math, matrix, na, nz, ohlc4, open, plot, plotshape, request, script, shape,
    size, syminfo, ta, ticker, timeframe
)
from pynecore.types import Color, Matrix, Persistent, PersistentSeries, Series
import lib.loxx.loxxexpandedsourcetypes.v4 as loxxexpandedsourcetypes


@script.indicator('STD-Filtered, N-Pole Gaussian Filter [Loxx]', shorttitle='STDFNPGF [Loxx]', overlay=True)
def main(
    smthtype=input.string('Kaufman', 'Heiken-Ashi Better Smoothing', options=('AMA', 'T3', 'Kaufman'), group='Source Settings'),
    srcoption=input.string('Close', 'Source', group='Source Settings', options=('Close', 'Open', 'High', 'Low', 'Median', 'Typical', 'Weighted', 'Average', 'Average Median Body', 'Trend Biased', 'Trend Biased (Extreme)', 'HA Close', 'HA Open', 'HA High', 'HA Low', 'HA Median', 'HA Typical', 'HA Weighted', 'HA Average', 'HA Average Median Body', 'HA Trend Biased', 'HA Trend Biased (Extreme)', 'HAB Close', 'HAB Open', 'HAB High', 'HAB Low', 'HAB Median', 'HAB Typical', 'HAB Weighted', 'HAB Average', 'HAB Average Median Body', 'HAB Trend Biased', 'HAB Trend Biased (Extreme)')),
    period=input.int(25, 'Period', group='Basic Settings'),
    order__ren__=input.int(5, 'Order', group='Basic Settings', minval=1),
    filterop=input.string('Gaussian Filter', 'Filter Options', options=('Price', 'Gaussian Filter', 'Both', 'None'), group='Filter Settings'),
    filter=input.float(1, 'Filter Devaitions', minval=0, group='Filter Settings'),
    filterperiod=input.int(10, 'Filter Period', minval=0, group='Filter Settings'),
    colorbars=input.bool(True, 'Color bars?', group='UI Options'),
    showSigs=input.bool(True, 'Show signals?', group='UI Options'),
    kfl=input.float(0.666, title='* Kaufman\'s Adaptive MA (KAMA) Only - Fast End', group='Moving Average Inputs'),
    ksl=input.float(0.0645, title='* Kaufman\'s Adaptive MA (KAMA) Only - Slow End', group='Moving Average Inputs'),
    amafl=input.int(2, title='* Adaptive Moving Average (AMA) Only - Fast', group='Moving Average Inputs'),
    amasl=input.int(30, title='* Adaptive Moving Average (AMA) Only - Slow', group='Moving Average Inputs')
):
    greencolor: Color = color.new('#2DD204')
    redcolor: Color = color.new('#D2042D')
    def fact(n: int):
        a: float = 1
        for i in pine_range(1, n, 1):
            a = a * i
        return a

    def _alpha(period: int, poles: int):
        w = 2.0 * math.pi / period
        b: float = (1.0 - math.cos(w)) / (math.pow(1.414, 2.0 / poles) - 1.0)
        a: float = -b + math.sqrt(b * b + 2.0 * b)
        return a

    def _makeCoeffs(period: int, order__ren__: int):
        coeffs: Matrix[float] = matrix.new(order__ren__ + 1, 3, 0.0)
        a: float = _alpha(period, order__ren__)
        for r in pine_range(0, order__ren__, 1):
            out__00000013__ = nz(fact(order__ren__) / (fact(order__ren__ - r) * fact(r)), 1)
            matrix.set(coeffs, r, 0, out__00000013__)
            matrix.set(coeffs, r, 1, math.pow(a, r))
            matrix.set(coeffs, r, 2, math.pow(1.0 - a, r))
        return coeffs

    def _npolegf(src: float, period: int, order__ren__: int):
        coeffs: Persistent = _makeCoeffs(period, order__ren__)
        filt: Series[float] = src * matrix.get(coeffs, order__ren__, 1)
        sign: int = 1
        for r in pine_range(1, order__ren__, 1):
            filt = filt + sign * matrix.get(coeffs, r, 0) * matrix.get(coeffs, r, 2) * nz(filt[r])
            sign = sign * -1
        return filt

    def _filt(src: float, len: int, filter: float):
        price: Series[float] = src
        filtdev: float = filter * ta.stdev(src, len)
        price = nz(price[1]) if math.abs(price - nz(price[1])) < filtdev else price
        return price

    haclose, haopen, hahigh, halow, hamedian, hatypical, haweighted, haaverage = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, (close, open, high, low, hl2, hlc3, hlcc4, ohlc4))
    __block_result__ = na
    __switch__ = srcoption
    if __switch__ == 'Close':
        __block_result__ = loxxexpandedsourcetypes.rclose()
    elif __switch__ == 'Open':
        __block_result__ = loxxexpandedsourcetypes.ropen()
    elif __switch__ == 'High':
        __block_result__ = loxxexpandedsourcetypes.rhigh()
    elif __switch__ == 'Low':
        __block_result__ = loxxexpandedsourcetypes.rlow()
    elif __switch__ == 'Median':
        __block_result__ = loxxexpandedsourcetypes.rmedian()
    elif __switch__ == 'Typical':
        __block_result__ = loxxexpandedsourcetypes.rtypical()
    elif __switch__ == 'Weighted':
        __block_result__ = loxxexpandedsourcetypes.rweighted()
    elif __switch__ == 'Average':
        __block_result__ = loxxexpandedsourcetypes.raverage()
    elif __switch__ == 'Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.ravemedbody()
    elif __switch__ == 'Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.rtrendb()
    elif __switch__ == 'Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.rtrendbext()
    elif __switch__ == 'HA Close':
        __block_result__ = loxxexpandedsourcetypes.haclose(haclose)
    elif __switch__ == 'HA Open':
        __block_result__ = loxxexpandedsourcetypes.haopen(haopen)
    elif __switch__ == 'HA High':
        __block_result__ = loxxexpandedsourcetypes.hahigh(hahigh)
    elif __switch__ == 'HA Low':
        __block_result__ = loxxexpandedsourcetypes.halow(halow)
    elif __switch__ == 'HA Median':
        __block_result__ = loxxexpandedsourcetypes.hamedian(hamedian)
    elif __switch__ == 'HA Typical':
        __block_result__ = loxxexpandedsourcetypes.hatypical(hatypical)
    elif __switch__ == 'HA Weighted':
        __block_result__ = loxxexpandedsourcetypes.haweighted(haweighted)
    elif __switch__ == 'HA Average':
        __block_result__ = loxxexpandedsourcetypes.haaverage(haaverage)
    elif __switch__ == 'HA Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.haavemedbody(haclose, haopen)
    elif __switch__ == 'HA Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.hatrendb(haclose, haopen, hahigh, halow)
    elif __switch__ == 'HA Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.hatrendbext(haclose, haopen, hahigh, halow)
    elif __switch__ == 'HAB Close':
        __block_result__ = loxxexpandedsourcetypes.habclose(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Open':
        __block_result__ = loxxexpandedsourcetypes.habopen(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB High':
        __block_result__ = loxxexpandedsourcetypes.habhigh(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Low':
        __block_result__ = loxxexpandedsourcetypes.hablow(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Median':
        __block_result__ = loxxexpandedsourcetypes.habmedian(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Typical':
        __block_result__ = loxxexpandedsourcetypes.habtypical(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Weighted':
        __block_result__ = loxxexpandedsourcetypes.habweighted(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Average':
        __block_result__ = loxxexpandedsourcetypes.habaverage(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Average Median Body':
        __block_result__ = loxxexpandedsourcetypes.habavemedbody(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Trend Biased':
        __block_result__ = loxxexpandedsourcetypes.habtrendb(smthtype, amafl, amasl, kfl, ksl)
    elif __switch__ == 'HAB Trend Biased (Extreme)':
        __block_result__ = loxxexpandedsourcetypes.habtrendbext(smthtype, amafl, amasl, kfl, ksl)
    else:
        __block_result__ = haclose
    src: float = __block_result__
    src = _filt(src, filterperiod, filter) if filterop == 'Both' or (filterop == 'Price' and filter > 0) else src
    out: Series = _npolegf(src, period, order__ren__)
    out = _filt(out, filterperiod, filter) if filterop == 'Both' or (filterop == 'Gaussian Filter' and filter > 0) else out
    sig: Series = nz(out[1])
    state: int = 0
    if out > sig:
        state = 1
    if out < sig:
        state = -1
    pregoLong = out > sig and (nz(out[1]) < nz(sig[1]) or nz(out[1]) == nz(sig[1]))
    pregoShort = out < sig and (nz(out[1]) > nz(sig[1]) or nz(out[1]) == nz(sig[1]))
    contsw: Series[int] = 0
    contsw = nz(contsw[1])
    contsw = 1 if pregoLong else -1 if pregoShort else nz(contsw[1])
    goLong = pregoLong and nz(contsw[1]) == -1
    goShort = pregoShort and nz(contsw[1]) == 1
    colorout: PersistentSeries[Color] = na(Color)
    colorout = redcolor if state == -1 else greencolor if state == 1 else nz(colorout[1])
    plot(out, 'N-Pole GF', color=colorout, linewidth=3)
    barcolor(colorout if colorbars else na)
    plotshape(showSigs and goLong, title='Long', color=color.yellow, textcolor=color.yellow, text='L', style=shape.triangleup, location=location.belowbar, size=size.tiny)
    plotshape(showSigs and goShort, title='Short', color=color.fuchsia, textcolor=color.fuchsia, text='S', style=shape.triangledown, location=location.abovebar, size=size.tiny)
    alertcondition(goLong, title='Long', message='STD-Filtered, N-Pole Gaussian Filter [Loxx]: Long\nSymbol: {{ticker}}\nPrice: {{close}}')
    alertcondition(goShort, title='Short', message='STD-Filtered, N-Pole Gaussian Filter [Loxx]: Short\nSymbol: {{ticker}}\nPrice: {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)