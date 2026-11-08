"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, plotcandle,
    script, ta
)
from pynecore.types import Series
from typing import Protocol, Any


__all__ = ['calc', 'calcFor', 'calcFor_v1']


class _ProtocolCalc(Protocol):
    def __call__(self, _o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4') -> Any: ...


class _ProtocolCalcfor(Protocol):
    def __call__(self, _o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 1) -> Any: ...


class _ProtocolCalcforV1(Protocol):
    def __call__(self, _o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 1) -> Any: ...


calc: _ProtocolCalc = Exported()
calcFor: _ProtocolCalcfor = Exported()
calcFor_v1: _ProtocolCalcforV1 = Exported()


@script.library('Heikinashi', overlay=True)
def main(
    length=input.int(2, minval=1, maxval=10),
    close_type=input.string('ohlc4', options=('ohlc4', 'ohlc4-s2', 'ohlc4-s3', 'ohlc4-s4', 'ohlc4-s5', 'hlc3', 'oc2', 'hl2', 'close'))
):
    def close_calc(_type, _o, _h, _l, _c):
        __block_result__ = na
        __switch__ = _type
        if __switch__ == 'ohlc4':
            __block_result__ = math.avg(_o, _h, _l, _c)
        elif __switch__ == 'ohlc4-s2':
            __block_result__ = math.avg(_o, ta.sma(_h, 2), ta.sma(_l, 2), _c)
        elif __switch__ == 'ohlc4-s3':
            __block_result__ = math.avg(_o, ta.sma(_h, 3), ta.sma(_l, 3), _c)
        elif __switch__ == 'ohlc4-s4':
            __block_result__ = math.avg(_o, ta.sma(_h, 4), ta.sma(_l, 4), _c)
        elif __switch__ == 'ohlc4-s5':
            __block_result__ = math.avg(_o, ta.sma(_h, 5), ta.sma(_l, 5), _c)
        elif __switch__ == 'hlc3':
            __block_result__ = math.avg(_h, _l, _c)
        elif __switch__ == 'oc2':
            __block_result__ = math.avg(_o, _c)
        elif __switch__ == 'hl2':
            __block_result__ = math.avg(_l, _l)
        elif __switch__ == 'close':
            __block_result__ = _c
        else:
            __block_result__ = math.avg(_o, _h, _l, _c)
        return __block_result__

    def heikinashi(_o: Series[float], _h: Series[float], _l: Series[float], _c: Series[float], _close_type: str = 'ohlc4'):
        _hclose: Series = close_calc(_close_type, _o, _h, _l, _c)
        _hopen: Series = math.avg(_o[1], _h[1], _l[1], _c[1])
        if not na(_hopen[1]):
            _hopen = math.avg(nz(_hopen[1]), nz(_hclose[1]))
        return (_hopen, _h, _l, _hclose)

    def heikinashi_2_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_3_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_2_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_4_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_3_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_5_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_4_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_6_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_5_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_7_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_6_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_8_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_7_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_9_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_8_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_10_times(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        _open, _, _, _close = heikinashi_9_times(_o, _h, _l, _c, _close_type)
        return heikinashi(_open, _h, _l, _close, _close_type)

    def heikinashi_for(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 2):
        times = math.min(math.max(_times, 1), 10)
        __block_result_1__ = (na, na, na, na)
        __switch__ = times
        if __switch__ == 2:
            __block_result_1__ = heikinashi_2_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 3:
            __block_result_1__ = heikinashi_3_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 4:
            __block_result_1__ = heikinashi_4_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 5:
            __block_result_1__ = heikinashi_5_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 6:
            __block_result_1__ = heikinashi_6_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 7:
            __block_result_1__ = heikinashi_7_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 8:
            __block_result_1__ = heikinashi_8_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 9:
            __block_result_1__ = heikinashi_9_times(_o, _h, _l, _c, _close_type)
        elif __switch__ == 10:
            __block_result_1__ = heikinashi_10_times(_o, _h, _l, _c, _close_type)
        else:
            __block_result_1__ = heikinashi(_o, _h, _l, _c, _close_type)
        return __block_result_1__

    def heikinashi_for_v1(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 2):
        times = math.min(math.max(_times, 1), 10)
        _open1, _, _, _close1 = heikinashi(_o, _h, _l, _c, _close_type)
        _open2, _, _, _close2 = heikinashi(_open1, _h, _l, _close1, _close_type)
        _open3, _, _, _close3 = heikinashi(_open2, _h, _l, _close2, _close_type)
        _open4, _, _, _close4 = heikinashi(_open3, _h, _l, _close3, _close_type)
        _open5, _, _, _close5 = heikinashi(_open4, _h, _l, _close4, _close_type)
        _open6, _, _, _close6 = heikinashi(_open5, _h, _l, _close5, _close_type)
        _open7, _, _, _close7 = heikinashi(_open6, _h, _l, _close6, _close_type)
        _open8, _, _, _close8 = heikinashi(_open7, _h, _l, _close7, _close_type)
        _open9, _, _, _close9 = heikinashi(_open8, _h, _l, _close8, _close_type)
        _open10, _, _, _close10 = heikinashi(_open9, _h, _l, _close9, _close_type)
        __block_result_2__ = (na, na, na, na)
        __switch__ = times
        if __switch__ == 1:
            __block_result_2__ = (_open1, high, low, _close1)
        elif __switch__ == 2:
            __block_result_2__ = (_open2, high, low, _close2)
        elif __switch__ == 3:
            __block_result_2__ = (_open3, high, low, _close3)
        elif __switch__ == 4:
            __block_result_2__ = (_open4, high, low, _close4)
        elif __switch__ == 5:
            __block_result_2__ = (_open5, high, low, _close5)
        elif __switch__ == 6:
            __block_result_2__ = (_open6, high, low, _close6)
        elif __switch__ == 7:
            __block_result_2__ = (_open7, high, low, _close7)
        elif __switch__ == 8:
            __block_result_2__ = (_open8, high, low, _close8)
        elif __switch__ == 9:
            __block_result_2__ = (_open9, high, low, _close9)
        elif __switch__ == 10:
            __block_result_2__ = (_open10, high, low, _close10)
        return __block_result_2__

    @export
    def calc(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4'):
        return heikinashi(_o, _h, _l, _c, _close_type)

    @export
    def calcFor(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 1):
        return heikinashi_for(_o, _h, _l, _c, _close_type, _times)

    @export
    def calcFor_v1(_o: float, _h: float, _l: float, _c: float, _close_type: str = 'ohlc4', _times: int = 1):
        return heikinashi_for_v1(_o, _h, _l, _c, _close_type, _times)

    plot_open, _, _, plot_close = heikinashi_for(open, high, low, close, close_type, length)
    c = color.red if plot_open > plot_close else color.green
    plotcandle(plot_open, high, low, plot_close, 'Heikinashi 2', color=c, wickcolor=c, bordercolor=c)
    plot(ta.ema(math.avg(plot_open, plot_close), 50))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
