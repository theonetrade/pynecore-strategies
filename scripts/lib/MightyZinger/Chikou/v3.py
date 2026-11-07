"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.series import inline_series
from pynecore.lib import close, color, high, input, low, na, nz, ohlc4, open, plot, script, ta
from pynecore.types import Color, NA, Persistent, Series
from typing import Protocol, Any


__all__ = ['chikou']


class _ProtocolChikou(Protocol):
    def __call__(self, src: float, len: int, _high: float, _low: float, bull_col: Color, bear_col: Color, r_col: Color) -> Any: ...


chikou: _ProtocolChikou = Exported()

SRC_Tv: str = 'Use traditional TradingView Sources '
SRC_Wc: str = '(high + low + (2 * close)) / 4'
SRC_Wo: str = 'close+high+low-2*open'
SRC_Wi: str = '(close+high+low) / 3'
SRC_Ex: str = 'close>open ? high : low'
SRC_Hc: str = 'Heikin Ashi Close'
src_grp: str = 'Source Parameters'
grp1: str = 'Chikou Parameters'


@script.library('Chikou')
def main(
    diff_src=input.string(SRC_Wi, '→ Different Sources Options', options=(SRC_Tv, SRC_Wc, SRC_Wo, SRC_Wi, SRC_Ex, SRC_Hc), group=src_grp),
    i_sourceSetup: Series[float] = input.source(close, 'Source Setup', group=src_grp),
    uha_src=input.bool(True, title='Use Heikin Ashi Candles for Different Source Calculations', group=src_grp),
    i_Symmetrical=input.bool(True, 'Apply Symmetrically Weighted Moving Average at the price source (May Result Repainting)', group=src_grp),
    c_len=input.int(26, title='Chikou Period:', group=grp1)
):
    @export
    def chikou(src: float, len: int, _high: float, _low: float, bull_col: Color, bear_col: Color, r_col: Color):
        _up: Persistent = NA(bool)
        _dn: Persistent = NA(bool)
        _re: Persistent = NA(bool)
        _clr: Persistent[Color] = color.new(na, 0)
        sig: Persistent = NA(int)
        _up = src > inline_series(ta.highest(_high, len), len)
        _dn = src < inline_series(ta.lowest(_low, len), len)
        lowest_1: Series = ta.lowest(_low, len)
        _re = src < inline_series(ta.highest(_high, len), len) and src > lowest_1[len]
        _clr = bull_col if _up else bear_col if _dn else r_col
        sig = 1 if _up else -1 if _dn else 0
        return (_clr, sig)

    h_close = ohlc4 if uha_src else close
    def f_ha_open():
        haopen: Series = NA(float)
        haopen = (open + close) / 2 if na(haopen[1]) else (nz(haopen[1]) + nz(ohlc4[1])) / 2
        return haopen

    h_open = f_ha_open() if uha_src else open
    h_high = high
    h_low = low
    src_o = (h_high + h_low + 2 * h_close) / 4 if diff_src == SRC_Wc else h_close + h_high + h_low - 2 * h_open if diff_src == SRC_Wo else (h_close + h_high + h_low) / 3 if diff_src == SRC_Wi else (h_high if h_close > h_open else h_low) if diff_src == SRC_Ex else ohlc4 if diff_src == SRC_Hc else i_sourceSetup
    src_f = ta.swma(src_o) if i_Symmetrical else src_o
    c_col, _trend = chikou(src_f, c_len, high, low, color.green, color.red, color.yellow)
    chikou_plot = plot(src_f, offset=-c_len + 1, color=c_col, title='Chikou-Span', linewidth=4)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
