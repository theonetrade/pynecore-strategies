"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, close, color, fill, input, math, na, plot, script,
    strategy, syminfo, ta, time, timestamp, volume
)
from pynecore.types import Persistent, Series


@script.strategy(title='Delta-RSI Strategy with Filters', shorttitle='D-RSI with filters', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    degree=input.int(title='Polynomial Order', group='Model Parameters:', inline='linepar1', defval=3, minval=1),
    rsi_l=input.int(title='RSI Length', group='Model Parameters:', inline='linepar1', defval=21, minval=1, tooltip='The period length of RSI that is used as input.'),
    window=input.int(title='Length ( > Order)', group='Model Parameters:', inline='linepar2', defval=50, minval=2),
    signalLength=input.int(title='Signal Length', group='Model Parameters:', inline='linepar2', defval=9, tooltip='The signal line is a EMA of the D-RSI time series.'),
    islong=input.bool(title='Long', group='Allowed Entries:', inline='lineent', defval=True),
    isshort=input.bool(title='Short', group='Allowed Entries:', inline='lineent', defval=True),
    buycond=input.string(title='Buy', group='Entry and Exit Conditions:', inline='linecond', defval='Signal Line Crossing', options=('Zero-Crossing', 'Signal Line Crossing', 'Direction Change')),
    sellcond=input.string(title='Sell', group='Entry and Exit Conditions:', inline='linecond', defval='Signal Line Crossing', options=('Zero-Crossing', 'Signal Line Crossing', 'Direction Change')),
    endcond=input.string(title='Exit', group='Entry and Exit Conditions:', inline='linecond', defval='Signal Line Crossing', options=('Zero-Crossing', 'Signal Line Crossing', 'Direction Change')),
    filterlong=input.bool(title='Long Entries', inline='linefilt', group='Apply Filters to', defval=True),
    filtershort=input.bool(title='Short Enties', inline='linefilt', group='Apply Filters to', defval=True),
    filterend=input.bool(title='Exits', inline='linefilt', group='Apply Filters to', defval=True),
    usevol=input.bool(title='', inline='linefiltvol', group='Relative Volume Filter:', defval=False),
    rvol=input.int(title='Volume >', inline='linefiltvol', group='Relative Volume Filter:', defval=1),
    len_vol=input.int(title='Avg. Volume Over Period', inline='linefiltvol', group='Relative Volume Filter:', defval=30, minval=1, tooltip='The current volume must be greater than N times the M-period average volume.'),
    useatr=input.bool(title='', inline='linefiltatr', group='Volatility Filter:', defval=False),
    len_atr1=input.int(title='ATR', inline='linefiltatr', group='Volatility Filter:', defval=5, minval=1),
    len_atr2=input.int(title='> ATR', inline='linefiltatr', group='Volatility Filter:', defval=30, minval=1, tooltip='The N-period ATR must be greater than the M-period ATR.'),
    usersi=input.bool(title='', inline='linersi', group='Overbought/Oversold Filter:', defval=False),
    rsitrhs1=input.int(title='', inline='linersi', group='Overbought/Oversold Filter:', defval=0, minval=0, maxval=100),
    rsitrhs2=input.int(title='< RSI (14) <', inline='linersi', group='Overbought/Oversold Filter:', defval=100, minval=0, maxval=100, tooltip='RSI(14) must be in the range between N and M.'),
    issl=input.bool(title='SL', inline='linesl1', group='Stop Loss / Take Profit:', defval=False),
    slpercent=input.float(title=', %', inline='linesl1', group='Stop Loss / Take Profit:', defval=10, minval=0.0),
    istrailing=input.bool(title='Trailing', inline='linesl1', group='Stop Loss / Take Profit:', defval=False),
    istp=input.bool(title='TP', inline='linetp1', group='Stop Loss / Take Profit:', defval=False),
    tppercent=input.float(title=', %', inline='linetp1', group='Stop Loss / Take Profit:', defval=20),
    fixedstart=input.bool(title='', group='Fixed Backtest Period Start/End Dates:', inline='linebac1', defval=True),
    backtest_start=input.time(title='', inline='linebac1', group='Fixed Backtest Period Start/End Dates:', defval=timestamp('01 Jan 2017 13:30 +0000'), tooltip='If deactivated, backtest staring from the first available price bar.'),
    fixedend=input.bool(title='', group='Fixed Backtest Period Start/End Dates:', inline='linebac2', defval=False),
    backtest_end=input.time(title='', inline='linebac2', group='Fixed Backtest Period Start/End Dates:', defval=timestamp('30 Dec 2080 23:30 +0000'), tooltip='If deactivated, backtesting ends at the last available price bar.')
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

    def norm_rmse(_x, _xhat):
        _nrmse: float = 0.0
        if array.size(_x) != array.size(_xhat):
            _nrmse = na
        else:
            _N: int = array.size(_x)
            _mse: float = 0.0
            for i in pine_range(0, _N - 1, 1):
                _mse = _mse + math.pow(array.get(_x, i) - array.get(_xhat, i), 2) / _N
            _xmean = array.sum(_x) / _N
            _nrmse = math.sqrt(_mse) / _xmean
        return _nrmse

    def diff(_src: Series, _window, _degree):
        _J: Persistent[list[float]] = array.new_float(_window * (_degree + 1), 0)
        for i in pine_range(0, _window - 1, 1):
            for j in pine_range(0, _degree, 1):
                matrix_set(_J, math.pow(i, j), i, j, _window)
        _Y_raw: Persistent[list[float]] = array.new_float(_window, na)
        for j in pine_range(0, _window - 1, 1):
            array.set(_Y_raw, j, _src[_window - 1 - j])
        _C = pinv(_J, _window, _degree + 1)
        _a_coef = multiply(_C, _Y_raw, _degree + 1, _window, 1)
        _diff: float = 0.0
        for i in pine_range(1, _degree, 1):
            _diff = _diff + i * array.get(_a_coef, i) * math.pow(_window - 1, i - 1)
        _Y_hat = multiply(_J, _a_coef, _window, _degree + 1, 1)
        _nrmse: float = norm_rmse(_Y_raw, _Y_hat)
        return (_diff, _nrmse)

    if window < degree:
        window = degree + 1
    src = ta.rsi(close, rsi_l)
    drsi: Series
    drsi, nrmse = diff(src, window, degree)
    signalline = ta.ema(drsi, signalLength)
    dirchangeup = drsi > drsi[1] and drsi[1] < drsi[2] and (drsi[1] < 0.0)
    dirchangedw = drsi < drsi[1] and drsi[1] > drsi[2] and (drsi[1] > 0.0)
    crossup = ta.crossover(drsi, 0.0)
    crossdw = ta.crossunder(drsi, 0.0)
    crosssignalup = ta.crossover(drsi, signalline)
    crosssignaldw = ta.crossunder(drsi, signalline)
    drsilong = dirchangeup if buycond == 'Direction Change' else crossup if buycond == 'Zero-Crossing' else crosssignalup
    drsishort = dirchangedw if sellcond == 'Direction Change' else crossdw if sellcond == 'Zero-Crossing' else crosssignaldw
    drisendlong = dirchangedw if endcond == 'Direction Change' else crossdw if endcond == 'Zero-Crossing' else crosssignaldw
    drisendshort = dirchangeup if endcond == 'Direction Change' else crossup if endcond == 'Zero-Crossing' else crosssignalup
    rsifilter = ta.rsi(close, 14) > rsitrhs1 and ta.rsi(close, 14) < rsitrhs2 if usersi else True
    volatilityfilter = ta.atr(len_atr1) > ta.atr(len_atr2) if useatr else True
    volumefilter = volume > rvol * ta.sma(volume, len_vol) if usevol else True
    totalfilter = volatilityfilter and volumefilter and rsifilter
    golong = drsilong and islong and (totalfilter if filterlong else True)
    goshort = drsishort and isshort and (totalfilter if filtershort else True)
    endlong = drisendlong and (totalfilter if filterend else True)
    endshort = drisendlong and (totalfilter if filterend else True)
    isinrange = (time >= backtest_start if fixedstart else True) and (time <= backtest_end if fixedend else True)
    startprice = ta.valuewhen(condition=golong or goshort, source=close, occurrence=0)
    pm = 1 if golong else -1 if goshort else 1 / math.sign(strategy.position_size)
    takeprofit = startprice * (1 + pm * tppercent * 0.01)
    stoploss: Series = startprice * (1 - pm * slpercent * 0.01)
    if istrailing and strategy.position_size > 0:
        stoploss = math.max(close * (1 - slpercent * 0.01), stoploss[1])
    elif istrailing and strategy.position_size < 0:
        stoploss = math.min(close * (1 + slpercent * 0.01), stoploss[1])
    tpline = plot(takeprofit, color=color.new(color.blue, 100), title='TP')
    slline = plot(stoploss, color=color.new(color.red, 100), title='SL')
    p1 = plot(close, color=color.new(color.white, 100), title='Dummy Close')
    fill(p1, tpline, color=color.new(color.green, 70 if istp else 100), title='TP')
    fill(p1, slline, color=color.new(color.red, 70 if issl else 100), title='SL')
    if golong and isinrange and islong:
        strategy.entry('long', strategy.long)
        alert('D-RSI Long ' + syminfo.tickerid, alert.freq_once_per_bar_close)
    if goshort and isinrange and isshort:
        strategy.entry('short', strategy.short)
        alert('D-RSI Short ' + syminfo.tickerid, alert.freq_once_per_bar_close)
    if endlong:
        strategy.close('long', alert_message='Close Long')
        alert('D-RSI Exit Long ' + syminfo.tickerid, alert.freq_once_per_bar_close)
    if endshort:
        strategy.close('short', alert_message='Close Short')
        alert('D-RSI Exit Short ' + syminfo.tickerid, alert.freq_once_per_bar_close)
    strategy.exit(id='sl/tp long', from_entry='long', stop=stoploss if issl else na, limit=takeprofit if istp else na, alert_message='Close Long')
    strategy.exit(id='sl/tp short', from_entry='short', stop=stoploss if issl else na, limit=takeprofit if istp else na, alert_message='Stop Loss Short')
    if not isinrange:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
