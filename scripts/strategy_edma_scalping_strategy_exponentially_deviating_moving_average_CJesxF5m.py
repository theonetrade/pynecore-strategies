"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, close, color, fill, high, input, low, math, na, nz, ohlc4, open,
    plot, script, strategy, ta
)
from pynecore.types import NA, Persistent, PersistentSeries, Series
import lib.MightyZinger.Chikou.v3 as filter

SRC_Tv: str = 'Use traditional TradingView Sources '
SRC_Wc: str = '(open+close+3(high+low))/8'
SRC_Wo: str = 'close+high+low-2*open'
SRC_Wu: str = '(close+5(high+low)-7(open))/4'
SRC_Wi: str = '(open+close+5(high+low))/12'
SRC_Exi: str = 'close>open ? high : low'
SRC_Exj: str = 'Heiken-ashi(close>open) ? high : low'
src_grp: str = 'Source Parameters'
grp1: str = 'MA Parameters'
grp2: str = 'Chikou Filter Parameters'
grp3: str = 'EMA Color Settings'
grp4: str = 'ETrade Parameters'


@script.strategy('EDMA Scalping Strategy (Exponentially Deviating Moving Average)', shorttitle='MZ EDMA Strategy', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, calc_on_every_tick=False, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True)
def main(
    diff_src=input.string(SRC_Exi, '→ Different Sources Options', options=(SRC_Tv, SRC_Wc, SRC_Wo, SRC_Wu, SRC_Wi, SRC_Exi, SRC_Exj), group=src_grp),
    i_sourceSetup: Series[float] = input.source(close, 'Tradingview Source Setup', group=src_grp),
    i_Sym=input.bool(True, 'Apply Symmetrically Weighted Moving Average at the price source (May Result Repainting)', group=src_grp),
    edma_Length=input.int(20, title='MA Length:', group=grp1),
    i_Symmetrical=input(True, '‍ Apply Symmetrically Weighted Moving Average at EDMA'),
    ema1_Length=input.int(20, title='EMA 1 Length:', group=grp1),
    show_ema1=input(True, '‍ Show EMA 1'),
    ema2_Length=input.int(40, title='EMA 2 Length:', group=grp1),
    show_ema2=input(False, '‍ Show EMA 2'),
    c_len=input.int(25, title='Chikou Period (Displaced Source)', group=grp2),
    c_bull_col=input.color(color.green, 'Bull Color  ', group=grp2, inline='c_col'),
    c_bear_col=input.color(color.red, 'Bear Color  ', group=grp2, inline='c_col'),
    c_rvsl_col=input.color(color.yellow, 'Consollidation/Reversal Color  ', group=grp2, inline='c_col'),
    ema1_col=input.color(color.new('#2962FF'), 'EMA 1 Color  ', group=grp3, inline='e_col'),
    ema2_col=input.color(color.new('#FF6D00'), 'EMA 2 Color  ', group=grp3, inline='e_col'),
    showSignals=input.bool(True, title='Show Cross Alerts', group=grp4),
    conf_chk=input.bool(False, title='Use Chikou Filter for Confirmation', group=grp4)
):
    def f_ha_open():
        haopen: Series = NA(float)
        haopen = (open + close) / 2 if na(haopen[1]) else (nz(haopen[1]) + nz(ohlc4[1])) / 2
        return haopen

    h_open = f_ha_open()
    src_o = (open + close + 3 * (high + low)) / 8 if diff_src == SRC_Wc else close + high + low - 2 * open if diff_src == SRC_Wo else (close + 5 * (high + low) - 7 * open) / 4 if diff_src == SRC_Wu else (open + close + 5 * (high + low)) / 12 if diff_src == SRC_Wi else (high if close > open else low) if diff_src == SRC_Exi else (high if ohlc4 > h_open else low) if diff_src == SRC_Exj else i_sourceSetup
    src_f = ta.swma(src_o) if i_Sym else src_o
    def f_edma(src, len):
        hexp: PersistentSeries = NA(float)
        lexp: PersistentSeries = NA(float)
        _hma: Persistent = NA(float)
        _edma: Persistent = NA(float)
        smoothness: float = 1.0
        h_len = cast_int(len / 1.5)
        hexp = src if na(hexp[1]) else src if src >= hexp[1] else hexp[1] + (src - hexp[1]) * (smoothness / (len + 1))
        lexp = hexp if na(lexp[1]) else hexp if src <= lexp[1] else lexp[1] + (src - lexp[1]) * (smoothness / (len + 1))
        _hma = ta.wma(2 * ta.wma(lexp, h_len / 2) - ta.wma(lexp, h_len), math.round(math.sqrt(h_len)))
        _edma = _hma
        return _edma

    edma = ta.swma(f_edma(src_f, edma_Length)) if i_Symmetrical else f_edma(src_f, edma_Length)
    ema1 = ta.ema(src_f, ema1_Length)
    ema2 = ta.ema(src_f, ema2_Length)
    edma_col, _trend = filter.chikou(src_f, c_len, high, low, c_bull_col, c_bear_col, c_rvsl_col)
    edma_plot = plot(edma, title='EDMA', color=edma_col, linewidth=4)
    ema1_plot = plot(ema1 if show_ema1 else na, title='EMA 1', color=ema1_col, linewidth=3)
    ema2_plot = plot(ema2 if show_ema2 else na, title='EMA 2', color=ema2_col, linewidth=3)
    fill(ema1_plot, edma_plot, title='Background', color=color.new(edma_col, 70))
    L1 = ema2 > edma
    L2 = ema1 > edma
    L3 = _trend == 1
    S1 = ema2 < edma
    S2 = ema1 < edma
    S3 = _trend == -1
    weak_up = L1 and L3 if conf_chk else L1
    strong_up = L2 and L3 if conf_chk else L2
    weak_dn = S1 and S3 if conf_chk else S1
    strong_dn = S2 and S3 if conf_chk else S2
    signal_a: list[bool] = array.from_items(weak_up, strong_up, weak_dn, strong_dn)
    swing_a: Persistent[list[int]] = array.new_int(2)
    def f_signal():
        __block_result__ = na
        for i in pine_range(0, 1, 1):
            sig: Persistent[int] = 0
            if array.get(signal_a, i) and sig <= 0:
                sig = 1
            if array.get(signal_a, i + 2) and sig >= 0:
                sig = -1
            __block_result__ = array.set(swing_a, i, sig)
        return __block_result__

    f_signal()
    buy_weak = array.get(swing_a, 0) == 1 and inline_series(array.get(swing_a, 0), 1) != 1
    buy_strong = array.get(swing_a, 1) == 1 and inline_series(array.get(swing_a, 1), 1) != 1
    sell_weak = array.get(swing_a, 0) == -1 and inline_series(array.get(swing_a, 0), 1) != -1
    sell_strong = array.get(swing_a, 1) == -1 and inline_series(array.get(swing_a, 1), 1) != -1
    if buy_strong:
        strategy.close('sell')
    if buy_strong:
        strategy.entry('buy', strategy.long)
    if sell_strong:
        strategy.close('buy')
    if sell_strong:
        strategy.entry('sell', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
