"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, high, hl2, hlc3, hlcc4, low, math, na, nz, ohlc4, open, plot,
    script, ta
)
from pynecore.types import Series
from typing import Protocol, Any


__all__ = ['haavemedbody', 'haaverage', 'habavemedbody', 'habaverage', 'habclose', 'habhigh', 'hablow', 'habmedian', 'habopen', 'habtrendb', 'habtrendbext', 'habtypical', 'habweighted', 'haclose', 'hahigh', 'halow', 'hamedian', 'haopen', 'hatrendb', 'hatrendbext', 'hatypical', 'haweighted', 'ravemedbody', 'raverage', 'rclose', 'rhigh', 'rlow', 'rmedian', 'ropen', 'rtrendb', 'rtrendbext', 'rtypical', 'rweighted']


class _ProtocolRclose(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRopen(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRhigh(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRlow(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRmedian(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRtypical(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRweighted(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRaverage(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRavemedbody(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRtrendb(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRtrendbext(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolHaclose(Protocol):
    def __call__(self, haclose__00000039__: float) -> Any: ...


class _ProtocolHaopen(Protocol):
    def __call__(self, haopen__0000003a__: float) -> Any: ...


class _ProtocolHahigh(Protocol):
    def __call__(self, hahigh__0000003b__: float) -> Any: ...


class _ProtocolHalow(Protocol):
    def __call__(self, halow__0000003c__: float) -> Any: ...


class _ProtocolHamedian(Protocol):
    def __call__(self, hamedian__0000003d__: float) -> Any: ...


class _ProtocolHatypical(Protocol):
    def __call__(self, hatypical__0000003e__: float) -> Any: ...


class _ProtocolHaweighted(Protocol):
    def __call__(self, haweighted__0000003f__: float) -> Any: ...


class _ProtocolHaaverage(Protocol):
    def __call__(self, haweighted__00000040__: float) -> Any: ...


class _ProtocolHaavemedbody(Protocol):
    def __call__(self, haclose__00000043__: float, haopen__00000043__: float) -> Any: ...


class _ProtocolHatrendb(Protocol):
    def __call__(self, haclose__00000049__: float, haopen__00000049__: float, hahigh__00000049__: float, halow__00000049__: float) -> Any: ...


class _ProtocolHatrendbext(Protocol):
    def __call__(self, haclose__0000004f__: float, haopen__0000004f__: float, hahigh__0000004f__: float, halow__0000004f__: float) -> Any: ...


class _ProtocolHabclose(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabopen(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabhigh(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHablow(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabmedian(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabtypical(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabweighted(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabaverage(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabavemedbody(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabtrendb(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


class _ProtocolHabtrendbext(Protocol):
    def __call__(self, smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float) -> Any: ...


rclose: _ProtocolRclose = Exported()
ropen: _ProtocolRopen = Exported()
rhigh: _ProtocolRhigh = Exported()
rlow: _ProtocolRlow = Exported()
rmedian: _ProtocolRmedian = Exported()
rtypical: _ProtocolRtypical = Exported()
rweighted: _ProtocolRweighted = Exported()
raverage: _ProtocolRaverage = Exported()
ravemedbody: _ProtocolRavemedbody = Exported()
rtrendb: _ProtocolRtrendb = Exported()
rtrendbext: _ProtocolRtrendbext = Exported()
haclose: _ProtocolHaclose = Exported()
haopen: _ProtocolHaopen = Exported()
hahigh: _ProtocolHahigh = Exported()
halow: _ProtocolHalow = Exported()
hamedian: _ProtocolHamedian = Exported()
hatypical: _ProtocolHatypical = Exported()
haweighted: _ProtocolHaweighted = Exported()
haaverage: _ProtocolHaaverage = Exported()
haavemedbody: _ProtocolHaavemedbody = Exported()
hatrendb: _ProtocolHatrendb = Exported()
hatrendbext: _ProtocolHatrendbext = Exported()
habclose: _ProtocolHabclose = Exported()
habopen: _ProtocolHabopen = Exported()
habhigh: _ProtocolHabhigh = Exported()
hablow: _ProtocolHablow = Exported()
habmedian: _ProtocolHabmedian = Exported()
habtypical: _ProtocolHabtypical = Exported()
habweighted: _ProtocolHabweighted = Exported()
habaverage: _ProtocolHabaverage = Exported()
habavemedbody: _ProtocolHabavemedbody = Exported()
habtrendb: _ProtocolHabtrendb = Exported()
habtrendbext: _ProtocolHabtrendbext = Exported()


@script.library('loxxexpandedsourcetypes', overlay=True)
def main():
    def _ama(src, len, fl, sl):
        flout = 2 / (fl + 1)
        slout = 2 / (sl + 1)
        hh = ta.highest(len + 1)
        ll = ta.lowest(len + 1)
        mltp = math.abs(2 * src - ll - hh) / (hh - ll) if hh - ll != 0 else 0
        ssc = mltp * (flout - slout) + slout
        ama: Series[float] = 0.0
        ama = nz(ama[1]) + math.pow(ssc, 2) * (src - nz(ama[1]))
        return ama

    def _t3(src, len):
        xe1_1 = ta.ema(src, len)
        xe2_1 = ta.ema(xe1_1, len)
        xe3_1 = ta.ema(xe2_1, len)
        xe4_1 = ta.ema(xe3_1, len)
        xe5_1 = ta.ema(xe4_1, len)
        xe6_1 = ta.ema(xe5_1, len)
        b_1: float = 0.7
        c1_1 = -b_1 * b_1 * b_1
        c2_1 = 3 * b_1 * b_1 + 3 * b_1 * b_1 * b_1
        c3_1 = -6 * b_1 * b_1 - 3 * b_1 - 3 * b_1 * b_1 * b_1
        c4_1 = 1 + 3 * b_1 + b_1 * b_1 * b_1 + 3 * b_1 * b_1
        nT3Average = c1_1 * xe6_1 + c2_1 * xe5_1 + c3_1 * xe4_1 + c4_1 * xe3_1
        return nT3Average

    def _kama(src: Series, len, kama_fastend, kama_slowend):
        xvnoise = math.abs(src - src[1])
        nfastend = kama_fastend
        nslowend = kama_slowend
        nsignal = math.abs(src - src[len])
        nnoise = math.sum(xvnoise, len)
        nefratio = nsignal / nnoise if nnoise != 0 else 0
        nsmooth = math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)
        nAMA: Series[float] = 0.0
        nAMA = nz(nAMA[1]) + nsmooth * (src - nz(nAMA[1]))
        return nAMA

    def _trendreg(o, h, l, c):
        compute: float = 0.0
        if c > o:
            compute = (h + c) / 2.0
        else:
            compute = (l + c) / 2.0
        return compute

    def _trendext(o, h, l, c):
        compute: float = 0.0
        if c > o:
            compute = h
        elif c < o:
            compute = l
        else:
            compute = c
        return compute

    @export
    def rclose():
        return close

    @export
    def ropen():
        return open

    @export
    def rhigh():
        return high

    @export
    def rlow():
        return low

    @export
    def rmedian():
        return hl2

    @export
    def rtypical():
        return hlc3

    @export
    def rweighted():
        return hlcc4

    @export
    def raverage():
        return ohlc4

    @export
    def ravemedbody():
        return (open + close) / 2

    @export
    def rtrendb():
        return _trendreg(ropen(), rhigh(), rlow(), rclose())

    @export
    def rtrendbext():
        return _trendext(ropen(), rhigh(), rlow(), rclose())

    @export
    def haclose(haclose__00000039__: float):
        return haclose__00000039__

    @export
    def haopen(haopen__0000003a__: float):
        return haopen__0000003a__

    @export
    def hahigh(hahigh__0000003b__: float):
        return hahigh__0000003b__

    @export
    def halow(halow__0000003c__: float):
        return halow__0000003c__

    @export
    def hamedian(hamedian__0000003d__: float):
        return hamedian__0000003d__

    @export
    def hatypical(hatypical__0000003e__: float):
        return hatypical__0000003e__

    @export
    def haweighted(haweighted__0000003f__: float):
        return haweighted__0000003f__

    @export
    def haaverage(haweighted__00000040__: float):
        return haweighted__00000040__

    @export
    def haavemedbody(haclose__00000043__: float, haopen__00000043__: float):
        return (haopen(haopen__00000043__) + haclose(haclose__00000043__)) / 2

    @export
    def hatrendb(haclose__00000049__: float, haopen__00000049__: float, hahigh__00000049__: float, halow__00000049__: float):
        return _trendreg(haopen(haopen__00000049__), hahigh(hahigh__00000049__), halow(halow__00000049__), haclose(haclose__00000049__))

    @export
    def hatrendbext(haclose__0000004f__: float, haopen__0000004f__: float, hahigh__0000004f__: float, halow__0000004f__: float):
        return _trendext(haopen(haopen__0000004f__), hahigh(hahigh__0000004f__), halow(halow__0000004f__), haclose(haclose__0000004f__))

    def _habingest():
        out = (ropen() + rclose()) / 2 + (rclose() - ropen()) / (rhigh() - rlow()) * math.abs((rclose() - ropen()) / 2)
        out = rclose() if na(out) else out
        return out

    @export
    def habclose(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        amaout = _ama(_habingest(), 2, amafl, amasl)
        t3out = _t3(_habingest(), 3)
        kamaout = _kama(_habingest(), 2, kfl, ksl)
        return amaout if smthtype == 'AMA' else t3out if smthtype == 'T3' else kamaout

    @export
    def habopen(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        habopen__0000006e__: Series[float] = 0.0
        habopen__0000006e__ = (nz(habopen__0000006e__) + nz(inline_series(habclose(smthtype, amafl, amasl, kfl, ksl), 1))) / 2 if na(habopen__0000006e__[1]) else (nz(habopen__0000006e__[1]) + nz(inline_series(habclose(smthtype, amafl, amasl, kfl, ksl), 1))) / 2
        return habopen__0000006e__

    @export
    def habhigh(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return math.max(rhigh(), habopen(smthtype, amafl, amasl, kfl, ksl), habclose(smthtype, amafl, amasl, kfl, ksl))

    @export
    def hablow(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return math.min(rlow(), habopen(smthtype, amafl, amasl, kfl, ksl), habclose(smthtype, amafl, amasl, kfl, ksl))

    @export
    def habmedian(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return (habhigh(smthtype, amafl, amasl, kfl, ksl) + hablow(smthtype, amafl, amasl, kfl, ksl)) / 2

    @export
    def habtypical(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return (habhigh(smthtype, amafl, amasl, kfl, ksl) + hablow(smthtype, amafl, amasl, kfl, ksl) + habclose(smthtype, amafl, amasl, kfl, ksl)) / 3

    @export
    def habweighted(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return (habhigh(smthtype, amafl, amasl, kfl, ksl) + hablow(smthtype, amafl, amasl, kfl, ksl) + habclose(smthtype, amafl, amasl, kfl, ksl) + habclose(smthtype, amafl, amasl, kfl, ksl)) / 4

    @export
    def habaverage(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return (habopen(smthtype, amafl, amasl, kfl, ksl) + habhigh(smthtype, amafl, amasl, kfl, ksl) + hablow(smthtype, amafl, amasl, kfl, ksl) + habclose(smthtype, amafl, amasl, kfl, ksl)) / 4

    @export
    def habavemedbody(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return (habopen(smthtype, amafl, amasl, kfl, ksl) + habclose(smthtype, amafl, amasl, kfl, ksl)) / 2

    @export
    def habtrendb(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return _trendreg(habopen(smthtype, amafl, amasl, kfl, ksl), habhigh(smthtype, amafl, amasl, kfl, ksl), hablow(smthtype, amafl, amasl, kfl, ksl), habclose(smthtype, amafl, amasl, kfl, ksl))

    @export
    def habtrendbext(smthtype: str, amafl: int, amasl: int, kfl: float, ksl: float):
        return _trendext(habopen(smthtype, amafl, amasl, kfl, ksl), habhigh(smthtype, amafl, amasl, kfl, ksl), hablow(smthtype, amafl, amasl, kfl, ksl), habclose(smthtype, amafl, amasl, kfl, ksl))

    habcloser = habclose('AMA', 6, 20, 5, 25)
    plot(habcloser)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
