"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import barstate, math, na, nz, runtime, script, ta, volume
from pynecore.types import Persistent, Series
from typing import Protocol, Any


__all__ = ['getOnBalanceVolumeFilter']


class _ProtocolGetonbalancevolumefilter(Protocol):
    def __call__(self, source: Series[float], maType: str, fastMaLength: int, slowMaLength: int) -> Any: ...


getOnBalanceVolumeFilter: _ProtocolGetonbalancevolumefilter = Exported()


@script.library('obvFilter')
def main():
    def getMovingAverage(type: str, source: Series[float], length: int):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'EMA':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'RMA':
            __block_result__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(source, length)
        else:
            __block_result__ = na
        ma = __block_result__
        return ma

    @export
    def getOnBalanceVolumeFilter(source: Series[float], maType: str, fastMaLength: int, slowMaLength: int):
        cumVol: Persistent[float] = 0.0
        cumVol = cumVol + nz(volume)
        if barstate.islast and cumVol == 0:
            runtime.error('No volume is provided by the data vendor.')
        obv = ta.cum(math.sign(ta.change(source)) * volume)
        fastObvMa = getMovingAverage(maType, obv, fastMaLength)
        slowObvMa = getMovingAverage(maType, obv, slowMaLength)
        return (obv, fastObvMa, slowObvMa)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
