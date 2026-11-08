"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, barcolor, close, color, display, format, high, hlc3, input, low,
    math, na, open, plot, plotcandle, request, script, syminfo, ta, timeframe, volume
)
from pynecore.types import Color, Series

g2: str = 'Large Change Thresholds'
g3: str = 'Volume-Price Imbalances'
g5: str = 'Additional Settings'
g4: str = 'Display Settings'
g6: str = 'Moving Averages'


@script.indicator('Volume Suite - By Leviathan', overlay=False, format=format.volume)
def main(
    disp=input.string('Relative Volume', 'Display', options=('Relative Volume', 'CRVOL (Cumulative Relative Volume)', 'Volume', 'Buy/Sell Volume', 'Volume Delta', 'CVD (Cumulative Volume Delta)')),
    upcol=input.color(color.new('#D1D4DC'), 'Primary Colors              ▲', inline='udcol'),
    downcol=input.color(color.new('#9598A1F6'), '▼', inline='udcol'),
    show_mult1=input.bool(True, '', inline='mult1', group=g2),
    mult=input.float(1.5, '>', inline='mult1', group=g2, step=0.1),
    upcol_mult1=input.color(color.new('#C8E6C9'), '     ▲', inline='mult1', group=g2),
    downcol_mult1=input.color(color.new('#FAA1A4'), '▼', inline='mult1', group=g2),
    show_mult2=input.bool(True, '', inline='mult2', group=g2),
    mult2=input.float(2.5, '>', inline='mult2', group=g2, step=0.1),
    upcol_mult2=input.color(color.new('#A5D6A7'), '     ▲', inline='mult2', group=g2),
    downcol_mult2=input.color(color.new('#F77C80'), '▼', inline='mult2', group=g2),
    show_mult3=input.bool(True, '', inline='mult3', group=g2),
    mult3=input.float(3.5, '>', inline='mult3', group=g2, step=0.1),
    upcol_mult3=input.color(color.new('#66BB6A'), '     ▲', inline='mult3', group=g2),
    downcol_mult3=input.color(color.new('#F7525F'), '▼', inline='mult3', group=g2),
    show_imb1=input.bool(False, 'High Volume + Small Price Change', group=g3, inline='imb1'),
    imb1_col=input.color(color.orange, '', group=g3, inline='imb1'),
    vimb1=input.float(1, 'V >', group=g3, inline='imb11', step=0.1),
    pimb1=input.float(0, 'P <', group=g3, inline='imb11', step=0.1),
    show_imb2=input.bool(False, 'Low Volume + Large Price Change', group=g3, inline='imb2'),
    imb2_col=input.color(color.blue, '', group=g3, inline='imb2'),
    vimb2=input.float(0, 'V <', group=g3, inline='imb22', step=0.1),
    pimb2=input.float(1, 'P >', group=g3, inline='imb22', step=0.1),
    showPlot1=input.bool(False, '', inline='pl1', group=g6),
    showPlot2=input.bool(False, '', inline='pl2', group=g6),
    showPlot3=input.bool(False, '', inline='pl3', group=g6),
    showPlot4=input.bool(False, '', inline='pl4', group=g6),
    showPlot5=input.bool(False, '', inline='pl5', group=g6),
    plot1=input.string('SMA', '', options=('SMA', 'EMA', 'VWMA'), inline='pl1', group=g6),
    plot2=input.string('EMA', '', options=('SMA', 'EMA', 'VWMA'), inline='pl2', group=g6),
    plot3=input.string('VWMA', '', options=('SMA', 'EMA', 'VWMA'), inline='pl3', group=g6),
    plot4=input.string('SMA', '', options=('SMA', 'EMA', 'VWMA'), inline='pl4', group=g6),
    plot5=input.string('VWAP', '', options=('VWAP', 'VWAP & STDEV'), inline='pl5', group=g6),
    len1=input.int(50, '', inline='pl1', group=g6),
    len2=input.int(50, '', inline='pl2', group=g6),
    len3=input.int(50, '', inline='pl3', group=g6),
    len4=input.int(50, '', inline='pl4', group=g6),
    len5=input.timeframe('D', '', inline='pl5', group=g6),
    plot1Col=input.color(color.gray, '', inline='pl1', group=g6),
    plot2Col=input.color(color.gray, '', inline='pl2', group=g6),
    plot3Col=input.color(color.gray, '', inline='pl3', group=g6),
    plot4Col=input.color(color.gray, '', inline='pl4', group=g6),
    plot5Col=input.color(color.gray, '', inline='pl5', group=g6),
    color_candles=input.bool(False, 'Color Candles', group=g5),
    gradient=input.bool(False, 'Gradient Coloring', inline='g', group=g5),
    gr1=input.color(color.new('#F7525F'), '', inline='g', group=g5),
    gr2=input.color(color.new('#FFE0B2'), '', inline='g', group=g5),
    tf=input.timeframe('1', 'LTF Timeframe', group=g5),
    threshtype=input.string('RELATIVE', 'Threshold Calculation Type', options=('SMA', 'RELATIVE', 'Z-SCORE'), group=g5),
    zlen=input.int(50, 'Z Length', group=g5),
    smalen=input.int(300, 'SMA Length', group=g5),
    rellen=input.int(20, 'Relative Length', group=g5),
    vwapstd=input.int(1, 'VWAP SD Multiplier', group=g5),
    rv_disp=input.string('Columns', 'Relative Volume', options=('Columns', 'Histogram', 'Line'), group=g4),
    crv_disp=input.string('Candles', 'Cumulative Relative Volume', options=('Candles', 'Line'), group=g4),
    bsv_disp=input.string('Columns', 'Buy/Sell Volume', options=('Columns', 'Histogram', 'Line'), group=g4),
    vd_disp=input.string('Columns', 'Volume Delta', options=('Columns', 'Histogram', 'Line'), group=g4),
    cvd_disp=input.string('Candles', 'CVD', options=('Candles', 'Line'), group=g4)
):
    g1: str = 'General'
    def disp_type(x):
        __block_result__ = na
        __switch__ = x
        if __switch__ == 'Columns':
            __block_result__ = plot.style_columns
        elif __switch__ == 'Histogram':
            __block_result__ = plot.style_histogram
        elif __switch__ == 'Line':
            __block_result__ = plot.style_line
        return __block_result__

    def f_mult1(src):
        return ta.sma(src, smalen) * (mult + 1)

    def f_mult2(src):
        return ta.sma(src, smalen) * (mult2 + 1)

    def f_mult3(src):
        return ta.sma(src, smalen) * (mult3 + 1)

    def f_relative(src):
        return src / ta.sma(src, rellen)

    def f_zscore(src):
        mean = ta.sma(src, zlen)
        std = ta.stdev(src, zlen)
        z_score = (src - mean) / std
        return z_score

    vol = volume
    vol_sma = f_mult1(vol)
    vol_sma2 = f_mult2(vol)
    vol_sma3 = f_mult3(vol)
    rvol = f_relative(volume)
    rvol_sma = f_mult1(rvol)
    rvol_sma2 = f_mult2(rvol)
    rvol_sma3 = f_mult3(rvol)
    obv: Series = ta.cum(rvol if close > open else -rvol)
    buy_volume, sell_volume = request.security_lower_tf(syminfo.tickerid, tf, (volume if close > open else 0, volume if close < open else 0))
    buy_vol = array.sum(buy_volume)
    sell_vol = array.sum(sell_volume)
    delta_vol = buy_vol - sell_vol
    cum_delta_vol: Series = ta.cum(delta_vol)
    delta_abs = math.abs(delta_vol)
    rposdelta = f_relative(delta_vol if delta_vol > 0 else 0)
    rnegdelta = f_relative(delta_vol if delta_vol < 0 else 0)
    vdp_sma = f_mult1(delta_vol if delta_vol > 0 else 0) * 2
    vdp_sma2 = f_mult2(delta_vol if delta_vol > 0 else 0) * 3
    vdp_sma3 = f_mult3(delta_vol if delta_vol > 0 else 0) * 7
    vdn_sma = f_mult1(delta_vol if delta_vol < 0 else 0) * 2
    vdn_sma2 = f_mult2(delta_vol if delta_vol < 0 else 0) * 3
    vdn_sma3 = f_mult3(delta_vol if delta_vol < 0 else 0) * 7
    bvl_sma = f_mult1(buy_vol)
    bvl2_sma = f_mult2(buy_vol)
    bvl3_sma = f_mult3(buy_vol)
    svl_sma = f_mult1(sell_vol)
    svl2_sma = f_mult2(sell_vol)
    svl3_sma = f_mult3(sell_vol)
    V_COL = upcol if close > open else downcol
    VD_COL = upcol if delta_vol > 0 else downcol
    CRV_COL = upcol if close > open else downcol
    BV_COL = upcol
    SV_COL = downcol
    bar_col: Color = color.rgb(0, 0, 0, 100)
    if threshtype == 'SMA':
        if disp == 'Volume':
            if show_mult1 and vol >= vol_sma:
                V_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = V_COL
            if show_mult2 and vol >= vol_sma2:
                V_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = V_COL
            if show_mult3 and vol >= vol_sma3:
                V_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = V_COL
        if disp == 'CRVOL (Cumulative Relative Volume)' or disp == 'Relative Volume':
            if show_mult1 and rvol >= rvol_sma:
                CRV_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = CRV_COL
            if show_mult2 and rvol >= rvol_sma2:
                CRV_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = CRV_COL
            if show_mult3 and rvol >= rvol_sma3:
                CRV_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = CRV_COL
        if disp == 'Volume Delta' or disp == 'CVD (Cumulative Volume Delta)':
            if show_mult1 and delta_vol > 0 and (delta_vol > vdp_sma):
                VD_COL = upcol_mult1
                bar_col = VD_COL
            if show_mult2 and delta_vol > 0 and (delta_vol > vdp_sma2):
                VD_COL = upcol_mult2
                bar_col = VD_COL
            if show_mult3 and delta_vol > 0 and (delta_vol > vdp_sma3):
                VD_COL = upcol_mult3
                bar_col = VD_COL
            if show_mult1 and delta_vol < 0 and (delta_vol < vdn_sma):
                VD_COL = downcol_mult1
                bar_col = VD_COL
            if show_mult2 and delta_vol < 0 and (delta_vol < vdn_sma2):
                VD_COL = downcol_mult2
                bar_col = VD_COL
            if show_mult3 and delta_vol < 0 and (delta_vol < vdn_sma3):
                VD_COL = downcol_mult3
                bar_col = VD_COL
        if disp == 'Buy/Sell Volume':
            if show_mult1 and buy_vol > bvl_sma:
                BV_COL = upcol_mult1
                bar_col = BV_COL
            if show_mult2 and buy_vol > bvl2_sma:
                BV_COL = upcol_mult2
                bar_col = BV_COL
            if show_mult3 and buy_vol > bvl3_sma:
                BV_COL = upcol_mult3
                bar_col = BV_COL
            if show_mult1 and sell_vol > svl_sma:
                SV_COL = downcol_mult1
                bar_col = SV_COL
            if show_mult2 and sell_vol > svl2_sma:
                SV_COL = downcol_mult2
                bar_col = SV_COL
            if show_mult3 and sell_vol > svl3_sma:
                SV_COL = downcol_mult3
                bar_col = SV_COL
    if threshtype == 'RELATIVE':
        if disp == 'Volume':
            f_relative_1 = f_relative(vol)
            if show_mult1 and f_relative_1 > mult:
                V_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = V_COL
            f_relative_2 = f_relative(vol)
            if show_mult2 and f_relative_2 > mult2:
                V_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = V_COL
            f_relative_3 = f_relative(vol)
            if show_mult3 and f_relative_3 > mult3:
                V_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = V_COL
        if disp == 'CRVOL (Cumulative Relative Volume)' or disp == 'Relative Volume':
            if show_mult1 and rvol >= mult:
                CRV_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = CRV_COL
            if show_mult2 and rvol >= mult2:
                CRV_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = CRV_COL
            if show_mult3 and rvol >= mult3:
                CRV_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = CRV_COL
        if disp == 'Volume Delta' or disp == 'CVD (Cumulative Volume Delta)':
            if show_mult1 and delta_vol > 0 and (rposdelta > mult * 1.5):
                VD_COL = upcol_mult1
                bar_col = VD_COL
            if show_mult2 and delta_vol > 0 and (rposdelta > mult2 * 1.5):
                VD_COL = upcol_mult2
                bar_col = VD_COL
            if show_mult3 and delta_vol > 0 and (rposdelta > mult3 * 1.5):
                VD_COL = upcol_mult3
                bar_col = VD_COL
            if show_mult1 and delta_vol < 0 and (-rnegdelta < -mult * 1.5):
                VD_COL = downcol_mult1
                bar_col = VD_COL
            if show_mult2 and delta_vol < 0 and (-rnegdelta < -mult2 * 1.5):
                VD_COL = downcol_mult2
                bar_col = VD_COL
            if show_mult3 and delta_vol < 0 and (-rnegdelta < -mult3 * 1.5):
                VD_COL = downcol_mult3
                bar_col = VD_COL
        if disp == 'Buy/Sell Volume':
            f_relative_1 = f_relative(buy_vol)
            if show_mult1 and f_relative_1 > mult:
                BV_COL = upcol_mult1
                bar_col = BV_COL
            f_relative_2 = f_relative(buy_vol)
            if show_mult2 and f_relative_2 > mult2:
                BV_COL = upcol_mult2
                bar_col = BV_COL
            f_relative_3 = f_relative(buy_vol)
            if show_mult3 and f_relative_3 > mult3:
                BV_COL = upcol_mult3
                bar_col = BV_COL
            f_relative_4 = f_relative(sell_vol)
            if show_mult1 and f_relative_4 >= mult:
                SV_COL = downcol_mult1
                bar_col = SV_COL
            f_relative_5 = f_relative(sell_vol)
            if show_mult2 and f_relative_5 >= mult2:
                SV_COL = downcol_mult2
                bar_col = SV_COL
            f_relative_6 = f_relative(sell_vol)
            if show_mult3 and f_relative_6 >= mult3:
                SV_COL = downcol_mult3
                bar_col = SV_COL
    if threshtype == 'Z-SCORE':
        if disp == 'Volume':
            f_zscore_1__000000a4__ = f_zscore(vol)
            if show_mult1 and f_zscore_1__000000a4__ >= mult:
                V_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = V_COL
            f_zscore_2__000000a4__ = f_zscore(vol)
            if show_mult2 and f_zscore_2__000000a4__ >= mult2:
                V_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = V_COL
            f_zscore_3__000000a4__ = f_zscore(vol)
            if show_mult3 and f_zscore_3__000000a4__ >= mult3:
                V_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = V_COL
        if disp == 'CRVOL (Cumulative Relative Volume)' or disp == 'Relative Volume':
            f_zscore_1__000000ab__ = f_zscore(rvol)
            if show_mult1 and f_zscore_1__000000ab__ >= mult:
                CRV_COL = upcol_mult1 if close > open else downcol_mult1
                bar_col = CRV_COL
            f_zscore_2__000000ab__ = f_zscore(rvol)
            if show_mult2 and f_zscore_2__000000ab__ >= mult2:
                CRV_COL = upcol_mult2 if close > open else downcol_mult2
                bar_col = CRV_COL
            f_zscore_3__000000ab__ = f_zscore(rvol)
            if show_mult3 and f_zscore_3__000000ab__ >= mult3:
                CRV_COL = upcol_mult3 if close > open else downcol_mult3
                bar_col = CRV_COL
        if disp == 'Volume Delta' or disp == 'CVD (Cumulative Volume Delta)':
            f_zscore_1__000000b8__ = f_zscore(rposdelta)
            if show_mult1 and delta_vol > 0 and (f_zscore_1__000000b8__ >= mult):
                VD_COL = upcol_mult1
                bar_col = VD_COL
            f_zscore_2__000000b8__ = f_zscore(rposdelta)
            if show_mult2 and delta_vol > 0 and (f_zscore_2__000000b8__ >= mult2):
                VD_COL = upcol_mult2
                bar_col = VD_COL
            f_zscore_3__000000b8__ = f_zscore(rposdelta)
            if show_mult3 and delta_vol > 0 and (f_zscore_3__000000b8__ >= mult3):
                VD_COL = upcol_mult3
                bar_col = VD_COL
            f_zscore_4__000000b8__ = f_zscore(rnegdelta)
            if show_mult1 and delta_vol < 0 and (f_zscore_4__000000b8__ >= mult):
                VD_COL = downcol_mult1
                bar_col = VD_COL
            f_zscore_5 = f_zscore(rnegdelta)
            if show_mult2 and delta_vol < 0 and (f_zscore_5 >= mult2):
                VD_COL = downcol_mult2
                bar_col = VD_COL
            f_zscore_6 = f_zscore(rnegdelta)
            if show_mult3 and delta_vol < 0 and (f_zscore_6 >= mult3):
                VD_COL = downcol_mult3
                bar_col = VD_COL
        if disp == 'Buy/Sell Volume':
            f_zscore_1__000000c5__ = f_zscore(buy_vol)
            if show_mult1 and f_zscore_1__000000c5__ >= mult:
                BV_COL = upcol_mult1
                bar_col = BV_COL
            f_zscore_2__000000c5__ = f_zscore(buy_vol)
            if show_mult2 and f_zscore_2__000000c5__ >= mult2:
                BV_COL = upcol_mult2
                bar_col = BV_COL
            f_zscore_3__000000c5__ = f_zscore(buy_vol)
            if show_mult3 and f_zscore_3__000000c5__ >= mult3:
                BV_COL = upcol_mult3
                bar_col = BV_COL
            f_zscore_4__000000c5__ = f_zscore(sell_vol)
            if show_mult1 and f_zscore_4__000000c5__ >= mult:
                SV_COL = downcol_mult1
                bar_col = SV_COL
            f_zscore_5 = f_zscore(sell_vol)
            if show_mult2 and f_zscore_5 >= mult2:
                SV_COL = downcol_mult2
                bar_col = SV_COL
            f_zscore_6 = f_zscore(sell_vol)
            if show_mult3 and f_zscore_6 >= mult3:
                SV_COL = downcol_mult3
                bar_col = SV_COL
    def switch_src(disp):
        __block_result_1__ = na
        __switch__ = disp
        if __switch__ == 'Volume':
            __block_result_1__ = vol
        elif __switch__ == 'Relative Volume':
            __block_result_1__ = rvol
        elif __switch__ == 'CRVOL (Cumulative Relative Volume)':
            __block_result_1__ = rvol
        elif __switch__ == 'Volume Delta':
            __block_result_1__ = math.abs(delta_vol)
        elif __switch__ == 'CVD (Cumulative Volume Delta)':
            __block_result_1__ = math.abs(delta_vol)
        elif __switch__ == 'Buy/Sell Volume':
            __block_result_1__ = math.abs(delta_vol)
        return __block_result_1__

    switch_src_1 = switch_src(disp)
    f_zscore_1 = f_zscore(switch_src_1)
    f_zscore_2 = f_zscore(high - low)
    if show_imb1 and f_zscore_1 > vimb1 and (f_zscore_2 < pimb1):
        V_COL = imb1_col
        CRV_COL = imb1_col
        VD_COL = imb1_col
        BV_COL = imb1_col if buy_vol > sell_vol else na
        SV_COL = imb1_col if sell_vol > buy_vol else na
        bar_col = imb1_col
    switch_src_2 = switch_src(disp)
    f_zscore_3 = f_zscore(switch_src_2)
    f_zscore_4 = f_zscore(high - low)
    if show_imb2 and f_zscore_3 < vimb2 and (f_zscore_4 > pimb2):
        V_COL = imb2_col
        CRV_COL = imb2_col
        VD_COL = imb2_col
        BV_COL = imb2_col if buy_vol < sell_vol else na
        SV_COL = imb2_col if sell_vol < buy_vol else na
        bar_col = imb2_col
    if gradient:
        glen: int = 50
        V_COL = color.from_gradient(vol, 0, ta.highest(vol, glen), gr2, gr1)
        CRV_COL = color.from_gradient(rvol, 0, ta.highest(rvol, glen), gr2, gr1)
        VD_COL = color.from_gradient(delta_vol, ta.lowest(delta_vol, glen), ta.highest(delta_vol, glen), gr2, gr1)
        BV_COL = color.from_gradient(buy_vol, 0, ta.highest(buy_vol, glen), gr2, gr1)
        SV_COL = color.from_gradient(sell_vol, 0, ta.highest(sell_vol, glen), gr2, gr1)
    o_ = obv[1] if disp == 'CRVOL (Cumulative Relative Volume)' else cum_delta_vol[1]
    h_ = obv if disp == 'CRVOL (Cumulative Relative Volume)' else cum_delta_vol
    l_ = obv if disp == 'CRVOL (Cumulative Relative Volume)' else cum_delta_vol
    c_ = obv if disp == 'CRVOL (Cumulative Relative Volume)' else cum_delta_vol
    crv_cond = disp == 'CRVOL (Cumulative Relative Volume)' and crv_disp == 'Candles'
    plotcandle(o_ if crv_cond else na, h_ if crv_cond else na, l_ if crv_cond else na, c_ if crv_cond else na, color=CRV_COL, wickcolor=CRV_COL, bordercolor=CRV_COL, title='CRVOL', editable=False)
    plot(obv if disp == 'CRVOL (Cumulative Relative Volume)' and crv_disp == 'Line' else na, color=CRV_COL, title='CRVOL', editable=False)
    cvd_cond = disp == 'CVD (Cumulative Volume Delta)' and cvd_disp == 'Candles'
    plotcandle(o_ if cvd_cond else na, h_ if cvd_cond else na, l_ if cvd_cond else na, c_ if cvd_cond else na, color=VD_COL, wickcolor=VD_COL, bordercolor=VD_COL, title='CVD', editable=False)
    plot(cum_delta_vol if disp == 'CVD (Cumulative Volume Delta)' and cvd_disp == 'Line' else na, color=VD_COL, title='CVD', editable=False)
    plot(rvol if disp == 'Relative Volume' else na, style=disp_type(rv_disp), color=CRV_COL, title='RVOL', editable=False)
    plot(volume if disp == 'Volume' else na, style=plot.style_columns, color=V_COL, title='VOL', editable=False)
    plot(buy_vol if disp == 'Buy/Sell Volume' else na, style=disp_type(bsv_disp), color=BV_COL, title='Buy Volume', editable=False)
    plot(-sell_vol if disp == 'Buy/Sell Volume' else na, style=disp_type(bsv_disp), color=SV_COL, title='Sell Volume', editable=False)
    plot(delta_vol if disp == 'Volume Delta' else na, style=disp_type(vd_disp), color=VD_COL, title='Volume Delta', editable=False)
    barcolor(bar_col if color_candles and bar_col != color.rgb(0, 0, 0, 100) else na)
    def f_plots(x, l):
        __block_result_2__ = na
        __switch__ = x
        if __switch__ == 'SMA':
            __block_result_2__ = ta.sma(close, l)
        elif __switch__ == 'EMA':
            __block_result_2__ = ta.ema(close, l)
        elif __switch__ == 'VWMA':
            __block_result_2__ = ta.vwma(close, l)
        return __block_result_2__

    vwap, vwapSDu, vwapSDl = ta.vwap(hlc3, timeframe.change(len5), vwapstd)
    vwapSDbu = vwap + vwapSDu - vwap
    vwapSDbl = vwap - (vwapSDu - vwap)
    plot(f_plots(plot1, len1) if showPlot1 else na, 'Plot 1', force_overlay=True, color=plot1Col, display=display.pane)
    plot(f_plots(plot2, len2) if showPlot2 else na, 'Plot 2', force_overlay=True, color=plot2Col, display=display.pane)
    plot(f_plots(plot3, len3) if showPlot3 else na, 'Plot 3', force_overlay=True, color=plot3Col, display=display.pane)
    plot(f_plots(plot4, len4) if showPlot4 else na, 'Plot 4', force_overlay=True, color=plot4Col, display=display.pane)
    plot(vwap if showPlot5 else na, 'VWAP', force_overlay=True, color=na if timeframe.change(len5) else plot5Col, display=display.pane)
    plot(vwapSDbu if showPlot5 and plot5 == 'VWAP & STDEV' else na, 'VWAP +SD', force_overlay=True, color=na if timeframe.change(len5) else plot5Col, display=display.pane)
    plot(vwapSDbl if showPlot5 and plot5 == 'VWAP & STDEV' else na, 'VWAP -SD', force_overlay=True, color=na if timeframe.change(len5) else plot5Col, display=display.pane)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
