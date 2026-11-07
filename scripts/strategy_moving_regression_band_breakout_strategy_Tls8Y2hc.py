"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, close, color, fill, high, input, location, low, math, na,
    open, plot, plotshape, script, shape, size, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Color, Persistent, Series


@script.strategy('Moving Regression Band Breakout strategy', shorttitle='MRBand Strat', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input.source(title='Source', defval=close, group='Model Parameters:'),
    degree=input.int(title='Local Polynomial Degree', defval=2, minval=0, group='Model Parameters:'),
    window=input.int(title='Length (must be larger than degree)', defval=80, minval=2, group='Model Parameters:'),
    mult=input.float(title='Multiplier', defval=2.0, minval=0.0, group='Model Parameters:', tooltip='Defines the Band Width.'),
    doLong=input.bool(title='Allow Long Entries', defval=True, inline='linealwd', group='Allowed Entries:'),
    doShort=input.bool(title='Allow Short Entries', defval=False, inline='linealwd', group='Allowed Entries:'),
    stoplong=input.string(title='Exit Long At', defval='Lower Band - ATR', options=('Lower Band', 'Lower Band - ATR', 'Central Line'), inline='lineexit', group='Exit Conditions:'),
    stopshort=input.string(title='Exit Short At', defval='Central Line', options=('Upper Band', 'Upper Band + ATR', 'Central Line'), inline='lineexit', group='Exit Conditions:'),
    fixedstart=input.bool(title='', group='Fixed Backtest Period Start/End Dates:', inline='linebac1', defval=True),
    backtest_start=input.time(title='', inline='linebac1', group='Fixed Backtest Period Start/End Dates:', defval=timestamp('01 Jan 2017 13:30 +0000'), tooltip='If deactivated, backtest staring from the first available price bar.'),
    fixedend=input.bool(title='', group='Fixed Backtest Period Start/End Dates:', inline='linebac2', defval=False),
    backtest_end=input.time(title='', inline='linebac2', group='Fixed Backtest Period Start/End Dates:', defval=timestamp('30 Dec 2080 23:30 +0000'), tooltip='If deactivated, backtesting ends at the last available price bar.'),
    istoploss=input.bool(title='Show Stop-Loss Line', defval=True, group='Additional Options'),
    slopefilter=input.bool(title='Enter Only When MR Slope is Positive/Negative', defval=False, group='Additional Options'),
    issignal=input.bool(title='Show Breakout Signals Labels', defval=False, group='Additional Options'),
    clinetype=input.string(title='Show Central Line As', defval='Previous-Period MR Prediction', options=('Ribbon', 'MR', 'Previous-Period MR Prediction'), group='Additional Options')
):
    def matrix_get(_A, _i, _j, _nrows):
        return array.get(_A, _i + _nrows * _j)

    def matrix_set(_A, _value, _i, _j, _nrows):
        return array.set(_A, _i + _nrows * _j, _value)

    def transpose(_A, _nrows, _ncolumns):
        _AT: Persistent[list[float]] = array.new_float(_nrows * _ncolumns, 0)
        for i in pine_range(0, _nrows - 1, 1):
            for j in pine_range(0, _ncolumns - 1, 1):
                matrix_set(_AT, matrix_get(_A, i, j, _nrows), j, i, _ncolumns)
        return _AT

    def multiply(_A, _B, _nrowsA, _ncolumnsA, _ncolumnsB):
        _C: Persistent[list[float]] = array.new_float(_nrowsA * _ncolumnsB, 0)
        _nrowsB: int = _ncolumnsA
        elementC: float = 0.0
        for i in pine_range(0, _nrowsA - 1, 1):
            for j in pine_range(0, _ncolumnsB - 1, 1):
                elementC = 0
                for k in pine_range(0, _ncolumnsA - 1, 1):
                    elementC = elementC + matrix_get(_A, i, k, _nrowsA) * matrix_get(_B, k, j, _nrowsB)
                matrix_set(_C, elementC, i, j, _nrowsA)
        return _C

    def vnorm(_X, _n):
        _norm: float = 0.0
        for i in pine_range(0, _n - 1, 1):
            _norm = _norm + math.pow(array.get(_X, i), 2)
        return math.sqrt(_norm)

    def qr_diag(_A, _nrows, _ncolumns):
        _Q: Persistent[list[float]] = array.new_float(_nrows * _ncolumns, 0)
        _R: Persistent[list[float]] = array.new_float(_ncolumns * _ncolumns, 0)
        _a: Persistent[list[float]] = array.new_float(_nrows, 0)
        _q: Persistent[list[float]] = array.new_float(_nrows, 0)
        _r: float = 0.0
        _aux: float = 0.0
        for i in pine_range(0, _nrows - 1, 1):
            array.set(_a, i, matrix_get(_A, i, 0, _nrows))
        _r = vnorm(_a, _nrows)
        matrix_set(_R, _r, 0, 0, _ncolumns)
        for i in pine_range(0, _nrows - 1, 1):
            matrix_set(_Q, array.get(_a, i) / _r, i, 0, _nrows)
        if _ncolumns != 1:
            for k in pine_range(1, _ncolumns - 1, 1):
                for i in pine_range(0, _nrows - 1, 1):
                    array.set(_a, i, matrix_get(_A, i, k, _nrows))
                for j in pine_range(0, k - 1, 1):
                    _r = 0
                    for i in pine_range(0, _nrows - 1, 1):
                        _r = _r + matrix_get(_Q, i, j, _nrows) * array.get(_a, i)
                    matrix_set(_R, _r, j, k, _ncolumns)
                    for i in pine_range(0, _nrows - 1, 1):
                        _aux = array.get(_a, i) - _r * matrix_get(_Q, i, j, _nrows)
                        array.set(_a, i, _aux)
                _r = vnorm(_a, _nrows)
                matrix_set(_R, _r, k, k, _ncolumns)
                for i in pine_range(0, _nrows - 1, 1):
                    matrix_set(_Q, array.get(_a, i) / _r, i, k, _nrows)
        return (_Q, _R)

    def pinv(_A, _nrows, _ncolumns):
        _Q, _R = qr_diag(_A, _nrows, _ncolumns)
        _QT = transpose(_Q, _nrows, _ncolumns)
        _Rinv: Persistent[list[float]] = array.new_float(_ncolumns * _ncolumns, 0)
        _r: float = 0.0
        matrix_set(_Rinv, 1 / matrix_get(_R, 0, 0, _ncolumns), 0, 0, _ncolumns)
        if _ncolumns != 1:
            for j in pine_range(1, _ncolumns - 1, 1):
                for i in pine_range(0, j - 1, 1):
                    _r = 0.0
                    for k in pine_range(i, j - 1, 1):
                        _r = _r + matrix_get(_Rinv, i, k, _ncolumns) * matrix_get(_R, k, j, _ncolumns)
                    matrix_set(_Rinv, _r, i, j, _ncolumns)
                for k in pine_range(0, j - 1, 1):
                    matrix_set(_Rinv, -matrix_get(_Rinv, k, j, _ncolumns) / matrix_get(_R, j, j, _ncolumns), k, j, _ncolumns)
                matrix_set(_Rinv, 1 / matrix_get(_R, j, j, _ncolumns), j, j, _ncolumns)
        _Ainv = multiply(_Rinv, _QT, _ncolumns, _ncolumns, _nrows)
        return _Ainv

    def mae(_x, _xhat):
        _mae: float = 0.0
        if array.size(_x) != array.size(_xhat):
            _mae = na
        else:
            _N = array.size(_x)
            for i in pine_range(0, _N - 1, 1):
                _mae = _mae + math.abs(array.get(_x, i) - array.get(_xhat, i)) / _N
        return _mae

    def mr(_src: Series, _window, _degree):
        _J: Persistent[list[float]] = array.new_float(_window * (_degree + 1), 0)
        for i in pine_range(0, _window - 1, 1):
            for j in pine_range(0, _degree, 1):
                matrix_set(_J, math.pow(i, j), i, j, _window)
        _Y_raw: Persistent[list[float]] = array.new_float(_window, na)
        for j in pine_range(0, _window - 1, 1):
            array.set(_Y_raw, j, _src[_window - 1 - j])
        _C = pinv(_J, _window, _degree + 1)
        _a_coef = multiply(_C, _Y_raw, _degree + 1, _window, 1)
        _Y: float = 0.0
        for i in pine_range(0, _degree, 1):
            _Y = _Y + array.get(_a_coef, i) * math.pow(_window - 1, i)
        _Y_f: float = 0.0
        for i in pine_range(0, _degree, 1):
            _Y_f = _Y_f + array.get(_a_coef, i) * math.pow(_window, i)
        _Y_hat = multiply(_J, _a_coef, _window, _degree + 1, 1)
        _err: float = mae(_Y_raw, _Y_hat)
        return (_Y, _Y_f, _err)

    MR: Series
    MR_f: Series
    div: Series
    MR, MR_f, div = mr(src, window, degree)
    div = div * mult
    highband = MR_f[1] + div[1]
    lowband = MR_f[1] - div[1]
    centralline = MR_f[1]
    hbplt = plot(highband, title='Upper Band', color=color.new(color.new('#3C94B8'), 40), linewidth=2)
    lbplt = plot(lowband, title='Lower Band', color=color.new(color.new('#B83C94'), 40), linewidth=2)
    fill(hbplt, lbplt, color=color.new(color.new('#3C94B8'), 90))
    plt_color: Persistent[Color] = color.new('#3C94B8')
    if MR_f[1] < MR and clinetype == 'Ribbon':
        plt_color = color.new('#94B83C')
    elif MR_f[1] > MR and clinetype == 'Ribbon':
        plt_color = color.new('#B83C71')
    mrplt = plot(MR, title='MR', color=plt_color, linewidth=1)
    mrfplt = plot(centralline, title='MR Prediction', color=plt_color, linewidth=1)
    fill(mrplt, mrfplt, color=color.new(plt_color, 100 if clinetype != 'Ribbon' else 20))
    ATR = ta.atr(14)
    Breakout = ta.crossover(src, highband)
    Breakdown = ta.crossunder(src, lowband)
    ATRBreakout = ta.crossover(src, highband + ATR)
    ATRBreakdown = ta.crossunder(src, lowband - ATR)
    MRSlopesUp = MR > MR[1]
    MRSlopesDw = MR < MR[1]
    plotshape(high if Breakout and issignal else na, location=location.abovebar, style=shape.triangleup, color=color.new(color.new('#88D4CA'), 0), size=size.tiny, title='Breakout')
    plotshape(low if Breakdown and issignal else na, location=location.belowbar, style=shape.triangledown, color=color.new(color.new('#F67E7D'), 0), size=size.tiny, title='Breakdown')
    goLong: Series = Breakout and (MRSlopesUp if slopefilter else True)
    goShort: Series = Breakdown and (MRSlopesDw if slopefilter else True)
    trailinglong = centralline if stoplong == 'Central Line' else lowband if stoplong == 'Lower Band' else lowband - ATR
    trailingshort = centralline if stopshort == 'Central Line' else highband if stopshort == 'Upper Band' else highband + ATR
    opprice: Persistent[float] = 0.0
    stoploss: Persistent[float] = 0.0
    if (strategy.position_entry_name[1] == 'short' or strategy.position_size[1] == 0) and goLong[1]:
        opprice = open
        stoploss = trailinglong
    elif (strategy.position_entry_name[1] == 'long' or strategy.position_size[1] == 0) and goShort[1]:
        opprice = open
        stoploss = trailingshort
    crossover_1 = ta.crossover(trailinglong, opprice)
    crossunder_1 = ta.crossunder(trailingshort, opprice)
    if strategy.position_entry_name == 'long' and crossover_1 or (strategy.position_entry_name == 'short' and crossunder_1):
        stoploss = opprice
    stoplosscolor = color.new('#B83C94') if strategy.position_entry_name == 'long' else color.new('#3C94B8') if strategy.position_entry_name == 'short' else color.silver
    plot(stoploss if istoploss else na, title='sl', color=stoplosscolor, linewidth=1)
    endLong = ta.crossunder(src, trailinglong)
    endShort = ta.crossover(src, trailingshort)
    isinrange = (time >= backtest_start if fixedstart else True) and (time <= backtest_end if fixedend else True)
    if goLong and isinrange and doLong:
        strategy.entry('long', strategy.long)
        alert(syminfo.tickerid + ' Long Signal Triggered', alert.freq_once_per_bar_close)
    if goShort and isinrange and doShort:
        strategy.entry('short', strategy.short)
        alert(syminfo.tickerid + ' Short Signal Triggered', alert.freq_once_per_bar_close)
    crossunder_2 = ta.crossunder(src, stoploss)
    if endLong or crossunder_2:
        strategy.close('long')
        alert(syminfo.tickerid + ' Exit Signal Triggered for Long Position', alert.freq_once_per_bar_close)
    crossover_2 = ta.crossover(src, stoploss)
    if endShort or crossover_2:
        strategy.close('short')
        alert(syminfo.tickerid + ' Exit Signal Triggered for Short Position', alert.freq_once_per_bar_close)
    if not isinrange:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
