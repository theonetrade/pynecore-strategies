"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_string
from pynecore.lib import (
    array, barcolor, barstate, bgcolor, box, chart, close, color, format,
    high, hline, input, line, linefill, low, math, matrix, na, nz, open, plot, plotcandle,
    position, request, script, string, syminfo, ta, table, text, time, timeframe, volume, xloc
)
from pynecore.types import Box, Line, Matrix, NA, Persistent, Series

g2: str = 'Thresholds'
g3: str = 'Additional Settings'
g5: str = 'Screener'
g4: str = 'Distribution profile '
g6: str = 'Data Sources and Aggregation'


@script.indicator('Open Interest Suite [Aggregated] - By Leviathan', format=format.volume, na_bool=True)
def main(
    maindisp=input.string('Open Interest', 'Display', options=('Open Interest', 'Open Interest Delta', 'OIΔ x rVOL', 'Open Interest RSI')),
    quotecur=input.string('USD', 'Quoted in', options=('USD', 'COIN')),
    upcol=input.color(color.new('#D1D4DC'), 'Color                ▲', inline='udcol'),
    downcol=input.color(color.new('#9598A1F6'), '▼', inline='udcol'),
    binance=input.bool(True, 'Binance USDT.P_OI', inline='src', group=g6),
    binance2=input.bool(True, 'Binance USD.P_OI', inline='src', group=g6),
    binance3=input.bool(True, 'Binance BUSD.P_OI', inline='src2', group=g6),
    bitmex=input.bool(True, 'BitMEX USD.P_OI', inline='src2', group=g6),
    bitmex2=input.bool(True, 'BitMEX USDT.P_OI ', inline='src3', group=g6),
    kraken=input.bool(True, 'Kraken USD.P_OI', inline='src3', group=g6),
    d_mult=input.float(5, 'Threshold Multiplier', step=0.1, group=g2),
    show_loi=input.bool(False, 'Highlight Large OI Increase ', inline='loi', group=g2),
    show_lod=input.bool(False, 'Highlight Large OI Decrease', inline='lod', group=g2),
    upoicol=input.color(color.new('#A5D6A7'), '', inline='loi', group=g2),
    dwoicol=input.color(color.new('#FE5F6D'), '', inline='lod', group=g2),
    col_cha=input.bool(False, 'Color Chart Bars', group=g2),
    col_bg=input.bool(False, 'Color Background', group=g2),
    show_thresh=input.bool(False, 'Show Thresholds', group=g2),
    show_ema=input.bool(False, 'OI EMA', group=g3, inline='ema'),
    ema_len=input.int(50, '', group=g3, inline='ema'),
    ema_col=input.color(color.gray, '', group=g3, inline='ema'),
    rsi_len=input.int(20, 'OI RSI      ', group=g3, inline='rsi'),
    rsi_col=input.color(color.gray, '', inline='rsi', group=g3),
    lookback=input.int(200, 'Lookback (bars)', group=g5),
    show_screener=input.bool(False, 'Show Screener', group=g5),
    show_OI=input.bool(True, ' ● Open Interest', group=g5),
    show_rekt=input.bool(True, ' ● Rekt Longs & Shorts', group=g5),
    show_agg=input.bool(True, ' ● Aggressive Longs & Shorts', group=g5),
    prof=input.bool(False, 'Generate a profile', group=g4),
    vapct=input.float(70, 'Value Area %', minval=5, maxval=95, group=g4),
    profSize=input.int(2, 'Node Size', minval=1, group=g4),
    __input_31__=input.int(40, 'Rows', minval=6, maxval=500, step=25, group=g4),
    vancol=input.color(color.new(color.blue, 75), 'Node Colors         ', group=g4, inline='nc'),
    nvancol=input.color(color.new(color.gray, 75), '━', group=g4, inline='nc'),
    poc=input.bool(False, 'POC', group=g4, inline='POC'),
    poccol=input.color(color.new(color.red, 50), '            ', group=g4, inline='POC'),
    val=input.bool(False, 'VA', group=g4, inline='VA'),
    vafill=input.color(color.new(color.blue, 95), '             ', group=g4, inline='VA')
):
    g1: str = 'General'
    rows = __input_31__ - 1
    pc = maindisp == 'Open Interest'
    pd = maindisp == 'Open Interest Delta'
    prdv = maindisp == 'OIΔ x rVOL'
    poir = maindisp == 'Open Interest RSI'
    ori: str = 'Left'
    mex = 'XBT' if syminfo.basecurrency == 'BTC' else cast_string(syminfo.basecurrency)
    oid1, oic1, oio1, oih1, oil1 = request.security('BINANCE' + ':' + cast_string(syminfo.basecurrency) + 'USDT.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    oid2, oic2, oio2, oih2, oil2 = request.security('BINANCE' + ':' + cast_string(syminfo.basecurrency) + 'USD.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    oid3, oic3, oio3, oih3, oil3 = request.security('BINANCE' + ':' + cast_string(syminfo.basecurrency) + 'BUSD.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    oid4, oic4, oio4, oih4, oil4 = request.security('BITMEX' + ':' + mex + 'USD.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    oid5, oic5, oio5, oih5, oil5 = request.security('BITMEX' + ':' + mex + 'USDT.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    oid6, oic6, oio6, oih6, oil6 = request.security('KRAKEN' + ':' + cast_string(syminfo.basecurrency) + 'USD.P_OI', timeframe.period, (close - close[1], close, open, high, low), ignore_invalid_symbol=True)
    deltaOI: Series = (nz(oid1, 0) if binance else 0) + (nz(oid2, 0) / close if binance2 else 0) + (nz(oid3, 0) if binance3 else 0) + (nz(oid4, 0) / close if bitmex else 0) + (nz(oid5, 0) / close if bitmex2 else 0) + (nz(oid6, 0) / close if kraken else 0)
    p_delta_thresh = ta.sma(deltaOI if deltaOI > 0 else 0, 300) * d_mult
    n_delta_thresh = ta.sma(deltaOI if deltaOI < 0 else 0, 300) * d_mult
    large_oi_up: Series = deltaOI > p_delta_thresh
    large_oi_dw: Series = deltaOI < n_delta_thresh
    O = (nz(oio1, 0) if binance else 0) + (nz(oio2 / close, 0) if binance2 else 0) + (nz(oio3, 0) if binance3 else 0) + (nz(oio4 / close, 0) if bitmex else 0) + (nz(oio5 / close, 0) if bitmex2 else 0) + (nz(oio6 / close, 0) if kraken else 0)
    H = (nz(oih1, 0) if binance else 0) + (nz(oih2 / close, 0) if binance2 else 0) + (nz(oih3, 0) if binance3 else 0) + (nz(oih4 / close, 0) if bitmex else 0) + (nz(oih5 / close, 0) if bitmex2 else 0) + (nz(oih6 / close, 0) if kraken else 0)
    L = (nz(oil1, 0) if binance else 0) + (nz(oil2 / close, 0) if binance2 else 0) + (nz(oil3, 0) if binance3 else 0) + (nz(oil4 / close, 0) if bitmex else 0) + (nz(oil5 / close, 0) if bitmex2 else 0) + (nz(oil6 / close, 0) if kraken else 0)
    C = (nz(oic1, 0) if binance else 0) + (nz(oic2 / close, 0) if binance2 else 0) + (nz(oic3, 0) if binance3 else 0) + (nz(oic4 / close, 0) if bitmex else 0) + (nz(oic5 / close, 0) if bitmex2 else 0) + (nz(oic6 / close, 0) if kraken else 0)
    O_ = O if quotecur == 'COIN' else O * close
    H_ = H if quotecur == 'COIN' else H * close
    L_ = L if quotecur == 'COIN' else L * close
    C_: Series = C if quotecur == 'COIN' else C * close
    rvol = volume / ta.sma(volume, 20)
    if prdv:
        deltaOI = deltaOI * rvol
        pd = True
    pccol = upcol if C_ > O_ else downcol
    pdcol = upcol if deltaOI > 0 else downcol
    if show_loi and large_oi_up:
        pccol = upoicol
        pdcol = upoicol
    if show_lod and large_oi_dw:
        pccol = dwoicol
        pdcol = dwoicol
    plotcandle(C_[1] if pc else na, H_ if pc else na, L_ if pc else na, C_ if pc else na, color=pccol, wickcolor=pccol, bordercolor=pccol, title='Open Interest Candles', editable=False)
    plot(deltaOI if pd else na, style=plot.style_columns, color=pdcol, title='Open Interest Delta')
    plot(ta.ema(C_, ema_len) if show_ema and pc else na, color=ema_col, editable=False)
    plot(ta.rsi(C, rsi_len) if poir else na, color=rsi_col, editable=False)
    hline(30 if poir else na, editable=False)
    hline(70 if poir else na, editable=False)
    hline(50 if poir else na, editable=False)
    bgcolor(color.new(pdcol, 85) if col_bg and show_loi and large_oi_up else na, editable=False)
    bgcolor(color.new(pdcol, 85) if col_bg and show_lod and large_oi_dw else na, editable=False)
    barcolor(color.new(pdcol, 0) if col_cha and show_loi and large_oi_up else na, editable=False)
    barcolor(color.new(pdcol, 0) if col_cha and show_lod and large_oi_dw else na, editable=False)
    plot(p_delta_thresh if show_thresh else na, color=color.gray, editable=False)
    plot(n_delta_thresh if show_thresh else na, color=color.gray, editable=False)
    srcp = C_
    timeArray: Persistent[list[int]] = array.new_int()
    dist: Persistent[list[float]] = array.new_float()
    x2: Persistent[list[int]] = array.new_int(rows + 1, 5)
    vh: Persistent[Matrix[float]] = matrix.new(1, 1, initial_value=NA(float))
    array.unshift(timeArray, math.round(time))
    if prof and (poir or pc) and (time >= chart.left_visible_bar_time) and (time <= chart.right_visible_bar_time):
        matrix.add_col(vh)
        matrix.set(vh, 0, matrix.columns(vh) - 1, srcp)
    if prof and (poir or pc) and barstate.islast:
        __block_result__ = (na, na)
        __switch_1__ = ori
        if __switch_1__ == 'Left':
            __block_result__ = (chart.left_visible_bar_time, array.indexof(timeArray, chart.left_visible_bar_time))
        else:
            __block_result__ = (chart.right_visible_bar_time, array.indexof(timeArray, chart.right_visible_bar_time))
        pos, n = __block_result__
        calc = (matrix.max(vh) - matrix.min(vh)) / (rows + 1)
        for i in pine_range(0, rows, 1):
            array.push(dist, matrix.min(vh) + i * calc)
        for i in pine_range(1, matrix.columns(vh) - 1, 1):
            for x in pine_range(0, array.size(dist) - 1, 1):
                if matrix.get(vh, 0, i) >= matrix.get(vh, 0, i - 1):
                    if array.get(dist, x) >= matrix.get(vh, 0, i - 1) and array.get(dist, x) <= matrix.get(vh, 0, i):
                        array.set(x2, x, array.get(x2, x) + profSize)
                else:
                    if array.get(dist, x) >= matrix.get(vh, 0, i) and array.get(dist, x) <= matrix.get(vh, 0, i - 1):
                        array.set(x2, x, array.get(x2, x) + profSize)
        boc: list[Box] = array.new_box()
        for i in pine_range(1, rows, 1):
            right = array.get(timeArray, n + array.get(x2, i))
            if ori == 'Left':
                switch_var_1 = math.sign(n - array.get(x2, i))
                __switch_3__ = switch_var_1
                if __switch_3__ == -1:
                    right = chart.right_visible_bar_time
                else:
                    right = array.get(timeArray, n - array.get(x2, i))
            array.push(boc, box.new(pos, array.get(dist, i - 1), right, array.get(dist, i), xloc=xloc.bar_time, border_color=nvancol, bgcolor=nvancol))
            if i == rows:
                array.push(boc, box.new(pos, array.get(dist, array.size(dist) - 1), right, array.get(dist, array.size(dist) - 1) + calc, xloc=xloc.bar_time, border_color=nvancol, bgcolor=nvancol))
        array.shift(x2)
        nx = array.indexof(x2, array.max(x2))
        nz__ren__ = nx - 1
        nz2: int = 0
        nz3: int = 0
        nz4: int = 0
        for i in pine_range(0, array.size(x2) - 1, 1):
            if nz__ren__ > -1 and nx <= array.size(x2) - 1:
                switch_var_3 = array.get(x2, nx) >= array.get(x2, nz__ren__)
                __switch_3__ = switch_var_3
                if __switch_3__ == True:
                    nz2 = nz2 + array.get(x2, nx)
                    nx = nx + 1
                else:
                    nz2 = nz2 + array.get(x2, nz__ren__)
                    nz__ren__ = nz__ren__ - 1
            elif nz__ren__ <= -1:
                nz2 = nz2 + array.get(x2, nx)
                nx = nx + 1
            elif nx >= array.size(x2):
                nz2 = nz2 + array.get(x2, nz__ren__)
                nz__ren__ = nz__ren__ - 1
            if nz2 >= array.sum(x2) * (vapct / 100):
                nz3 = nx if nx <= array.size(x2) - 1 else array.size(x2) - 1
                nz4 = 0 if nz__ren__ <= -1 else nz__ren__
                break
        for i in pine_range(nz3, nz4, 1):
            box.set_border_color(array.get(boc, i), vancol)
            box.set_bgcolor(array.get(boc, i), vancol)
        if poc:
            pocL: Persistent = NA(Line)
            y = math.avg(box.get_top(array.get(boc, array.indexof(x2, array.max(x2)))), box.get_bottom(array.get(boc, array.indexof(x2, array.max(x2)))))
            if na(pocL):
                pocL = line.new(chart.left_visible_bar_time, y, chart.right_visible_bar_time, y, xloc=xloc.bar_time, color=poccol, width=1)
            else:
                line.set_xy1(pocL, chart.left_visible_bar_time, y)
                line.set_xy2(pocL, chart.right_visible_bar_time, y)
        if val:
            vaup: Persistent = NA(Line)
            vadn: Persistent = NA(Line)
            ydn = box.get_bottom(array.get(boc, nz3))
            yup = box.get_top(array.get(boc, nz4))
            if na(vaup):
                vadn = line.new(chart.left_visible_bar_time, ydn, chart.right_visible_bar_time, ydn, xloc=xloc.bar_time, color=vancol, width=1)
                vaup = line.new(chart.left_visible_bar_time, yup, chart.right_visible_bar_time, yup, xloc=xloc.bar_time, color=vancol, width=1)
            else:
                line.set_xy1(vadn, chart.left_visible_bar_time, ydn)
                line.set_xy2(vadn, chart.right_visible_bar_time, ydn)
                line.set_xy1(vaup, chart.left_visible_bar_time, yup)
                line.set_xy2(vaup, chart.right_visible_bar_time, yup)
            linefill.new(vadn, vaup, vafill)
    if show_screener:
        table__ren__ = table.new(position.top_right, 2, 6, color.rgb(120, 123, 134, 82))
        rekt_longs: float = 0
        rekt_shorts: float = 0
        aggressive_longs: float = 0
        aggressive_shorts: float = 0
        for i in pine_range(0, lookback - 1, 1):
            if large_oi_dw[i] and close[i] < open[i]:
                rekt_longs = rekt_longs + math.abs(deltaOI[i] * close[i])
            if large_oi_dw[i] and close[i] > open[i]:
                rekt_shorts = rekt_shorts + math.abs(deltaOI[i] * close[i])
            if large_oi_up[i] and close[i] > open[i]:
                aggressive_longs = aggressive_longs + math.abs(deltaOI[i] * close[i])
            if large_oi_up[i] and close[i] < open[i]:
                aggressive_shorts = aggressive_shorts + math.abs(deltaOI[i] * close[i])
        if show_OI:
            table.cell(table__ren__, 0, 0, 'Open Interest:', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 1, 0, (string.tostring(C, format.volume) + ' BTC' if quotecur == 'COIN' else '$' + string.tostring(C * close, format.volume)) + ' ', text_halign=text.align_left, text_color=chart.fg_color)
        if show_rekt:
            table.cell(table__ren__, 0, 2, 'Rekt Longs:', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 0, 3, 'Rekt Shorts:', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 1, 2, '$' + string.tostring(rekt_longs, format.volume) + ' ', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 1, 3, '$' + string.tostring(rekt_shorts, format.volume) + ' ', text_halign=text.align_left, text_color=chart.fg_color)
        if show_agg:
            table.cell(table__ren__, 0, 4, 'Aggressive Longs:', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 0, 5, 'Aggressive Shorts:', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 1, 4, '$' + string.tostring(aggressive_longs, format.volume) + ' ', text_halign=text.align_left, text_color=chart.fg_color)
            table.cell(table__ren__, 1, 5, '$' + string.tostring(aggressive_shorts, format.volume) + ' ', text_halign=text.align_left, text_color=chart.fg_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
