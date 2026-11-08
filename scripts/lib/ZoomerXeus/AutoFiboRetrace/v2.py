"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import script, ta
from typing import Protocol, Any


__all__ = ['original', 'renderOnly']


class _ProtocolOriginal(Protocol):
    def __call__(self, FPeriod: int, sourceLow: float, sourceHigh: float) -> Any: ...


class _ProtocolRenderonly(Protocol):
    def __call__(self, sourceLow: float, sourceHigh: float) -> Any: ...


original: _ProtocolOriginal = Exported()
renderOnly: _ProtocolRenderonly = Exported()


@script.library('AutoFiboRetrace')
def main():
    @export
    def original(FPeriod: int, sourceLow: float, sourceHigh: float):
        Fhigh = ta.highest(sourceHigh, FPeriod)
        Flow = ta.lowest(sourceLow, FPeriod)
        FL236M = Flow - (Fhigh - Flow) * 0.236
        FL382M = Flow - (Fhigh - Flow) * 0.382
        FL500M = Flow - (Fhigh - Flow) * 0.5
        FL618M = Flow - (Fhigh - Flow) * 0.618
        FL786M = Flow - (Fhigh - Flow) * 0.786
        FL0 = Flow
        FL236 = (Fhigh - Flow) * 0.236 + Flow
        FL382 = (Fhigh - Flow) * 0.382 + Flow
        FL500 = (Fhigh - Flow) * 0.5 + Flow
        FL618 = (Fhigh - Flow) * 0.618 + Flow
        FL786 = (Fhigh - Flow) * 0.786 + Flow
        FL1000 = (Fhigh - Flow) * 1.0 + Flow
        FL1236 = (Fhigh - Flow) * 1.236 + Flow
        FL1382 = (Fhigh - Flow) * 1.382 + Flow
        FL1500 = (Fhigh - Flow) * 1.5 + Flow
        FL1618 = (Fhigh - Flow) * 1.618 + Flow
        FL1786 = (Fhigh - Flow) * 1.786 + Flow
        FL2 = (Fhigh - Flow) * 2 + Flow
        return (FL236M, FL382M, FL500M, FL618M, FL786M, FL0, FL236, FL382, FL500, FL618, FL786, FL1000, FL1236, FL1382, FL1500, FL1618, FL1786, FL2)

    @export
    def renderOnly(sourceLow: float, sourceHigh: float):
        Fhigh = sourceHigh
        Flow = sourceLow
        FL236M = Flow - (Fhigh - Flow) * 0.236
        FL382M = Flow - (Fhigh - Flow) * 0.382
        FL500M = Flow - (Fhigh - Flow) * 0.5
        FL618M = Flow - (Fhigh - Flow) * 0.618
        FL786M = Flow - (Fhigh - Flow) * 0.786
        FL0 = Flow
        FL236 = (Fhigh - Flow) * 0.236 + Flow
        FL382 = (Fhigh - Flow) * 0.382 + Flow
        FL500 = (Fhigh - Flow) * 0.5 + Flow
        FL618 = (Fhigh - Flow) * 0.618 + Flow
        FL786 = (Fhigh - Flow) * 0.786 + Flow
        FL1000 = (Fhigh - Flow) * 1.0 + Flow
        FL1236 = (Fhigh - Flow) * 1.236 + Flow
        FL1382 = (Fhigh - Flow) * 1.382 + Flow
        FL1500 = (Fhigh - Flow) * 1.5 + Flow
        FL1618 = (Fhigh - Flow) * 1.618 + Flow
        FL1786 = (Fhigh - Flow) * 1.786 + Flow
        FL2 = (Fhigh - Flow) * 2 + Flow
        return (FL236M, FL382M, FL500M, FL618M, FL786M, FL0, FL236, FL382, FL500, FL618, FL786, FL1000, FL1236, FL1382, FL1500, FL1618, FL1786, FL2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
