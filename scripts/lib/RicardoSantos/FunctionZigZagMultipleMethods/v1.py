"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import bar_index, close, high, input, low, na, nz, open, plot, script, ta, time
from pynecore.types import Persistent, PersistentSeries
from typing import Protocol, Any


__all__ = ['function', 'method__ren__']


class _ProtocolMethod(Protocol):
    def __call__(self, idx: int) -> Any: ...


class _ProtocolFunction(Protocol):
    def __call__(self, method__ren____00000046__: str, value_x: float, value_y: float) -> Any: ...


method__ren__: _ProtocolMethod = Exported()
function: _ProtocolFunction = Exported()

m_000: str = '(MANUAL) Percent price move over X * Y'
m_001: str = 'Percent price move over atr(X) * Y'
m_002: str = 'Percent price move over max(tr) * Y'
m_003: str = 'high or low pivot(X, Y)'
m_004: str = 'Price Action'


@script.library(title='FunctionZigZagMultipleMethods', na_bool=True)
def main(
    zigzag_method=input.string(defval=m_000, title='Method to use for the zigzag:', options=(m_000, m_001, m_002, m_003, m_004), group='ZigZag Options:'),
    param_x=input.float(defval=1.0, title='parameter X', group='ZigZag Options:'),
    param_y=input.float(defval=1.0, title='parameter Y', group='ZigZag Options:')
):
    @export
    def method__ren__(idx: int):
        __block_result__ = na
        __switch__ = idx
        if __switch__ == 0:
            __block_result__ = m_000
        elif __switch__ == 1:
            __block_result__ = m_001
        elif __switch__ == 2:
            __block_result__ = m_002
        elif __switch__ == 3:
            __block_result__ = m_003
        elif __switch__ == 4:
            __block_result__ = m_004
        else:
            __block_result__ = m_000
        return __block_result__

    @export
    def function(method__ren____00000046__: str, value_x: float, value_y: float):
        _percent: Persistent[float] = na(float)
        if method__ren____00000046__ == m_001:
            _percent = ta.sma(ta.tr(True), cast_int(value_x)) / open * value_y
        elif method__ren____00000046__ == m_002:
            _tr: float = ta.tr / open * value_y
            if na(_percent):
                _percent = _tr
            if _tr > _percent:
                _percent = _tr
        else:
            _percent = value_x * value_y
        _direction: Persistent[bool] = na(bool)
        _hprice: Persistent[float] = na(float)
        _lprice: Persistent[float] = na(float)
        _zz: PersistentSeries[float] = na(float)
        _tz: Persistent[int] = na(int)
        _htime: Persistent[int] = na(int)
        _ltime: Persistent[int] = na(int)
        _reverse_line: Persistent[float] = 0.0
        _reverse_range: float = 0.0
        _pivot_h = ta.pivothigh(value_x, value_y)
        _pivot_l = ta.pivotlow(value_x, value_y)
        if bar_index >= 1:
            if na(_direction):
                _direction = True
            _reverse_range = nz(_zz[1]) * _percent
            if _direction:
                _lprice = na
                _ltime = time
                if na(_hprice):
                    if high < high[1]:
                        _hprice = high[1]
                        _htime = time[1]
                    else:
                        _hprice = high
                        _htime = time
                else:
                    if high >= _hprice:
                        _hprice = high
                        _htime = time
                if method__ren____00000046__ == m_003:
                    _reverse_line = _hprice
                    if _pivot_h:
                        _zz = _hprice
                        _tz = _htime
                        _direction = False
                elif method__ren____00000046__ == m_004:
                    _reverse_line = _hprice
                    if high < high[1] and (low < low[1] or close - low < (high - low) * 0.5):
                        if low < low[1]:
                            _lprice = low
                            _ltime = time
                        else:
                            _lprice = low[1]
                            _ltime = time[1]
                        _zz = _hprice
                        _tz = _htime
                        _direction = False
                else:
                    _reverse_line = _hprice - _reverse_range
                    if close < _reverse_line:
                        _zz = _hprice
                        _tz = _htime
                        _direction = False
            else:
                _hprice = na
                _htime = na
                if na(_lprice):
                    if low > low[1]:
                        _lprice = low[1]
                        _ltime = time[1]
                    else:
                        _lprice = low
                        _ltime = time
                else:
                    if low <= _lprice:
                        _lprice = low
                        _ltime = time
                if method__ren____00000046__ == m_003:
                    _reverse_line = _lprice
                    if _pivot_l:
                        _zz = _lprice
                        _tz = _ltime
                        _direction = True
                elif method__ren____00000046__ == m_004:
                    _reverse_line = _lprice
                    if high > high[1] and (low > low[1] or close - low > (high - low) * 0.5):
                        if high > high[1]:
                            _hprice = high
                            _htime = time
                        else:
                            _hprice = high[1]
                            _htime = time[1]
                        _zz = _lprice
                        _tz = _ltime
                        _direction = True
                else:
                    _reverse_line = _lprice + _reverse_range
                    if close > _reverse_line:
                        _zz = _lprice
                        _tz = _ltime
                        _direction = True
        return (_zz, _direction, _reverse_line, _tz)

    price_a, is_up, reverse, _rl_time = function(zigzag_method, param_x, param_y)
    plot(price_a if ta.change(price_a) != 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
