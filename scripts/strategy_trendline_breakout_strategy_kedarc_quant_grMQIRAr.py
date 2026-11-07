"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, extend, high, input,
    label, line, location, low, na, plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Label, Line, Persistent


@script.strategy("Trendline Breakout Strategy [KedArc Quant] ", overlay=True, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.01, pyramiding=0, calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main(
    pivLR=input.int(5, "Pivot left/right bars", minval=1, maxval=20),
    useMA=input.bool(True, "Use MA filter (longs only above MA; shorts only below MA)"),
    maLen=input.int(200, "MA length", minval=1),
    atrLen=input.int(14, "ATR length", minval=1),
    atrMult=input.float(2.0, "ATR stop × ATR", minval=0.1, step=0.1),
    tpR=input.float(2.0, "Take profit (R multiple of stop)", minval=0.1, step=0.1),
    longs=input.bool(True, "Enable Longs"),
    shorts=input.bool(True, "Enable Shorts"),
    showHLLH=input.bool(True, "Show HL/LH labels")
):
    labHL1: Persistent[Label] = na(Label)
    labHL2: Persistent[Label] = na(Label)
    labLH1: Persistent[Label] = na(Label)
    labLH2: Persistent[Label] = na(Label)

    ma = ta.ema(close, maLen)
    atr = ta.atr(atrLen)

    pl = ta.pivotlow(low, pivLR, pivLR)
    ph = ta.pivothigh(high, pivLR, pivLR)

    pl_x: Persistent[list[int]] = array.new_int()
    pl_y: Persistent[list[float]] = array.new_float()
    ph_x: Persistent[list[int]] = array.new_int()
    ph_y: Persistent[list[float]] = array.new_float()

    def f_trim_arrays():
        while array.size(pl_x) > 20:
            array.shift(pl_x)
            array.shift(pl_y)
        __block_result__ = na
        while array.size(ph_x) > 20:
            array.shift(ph_x)
            __block_result__ = array.shift(ph_y)
        return __block_result__

    if not na(pl):
        array.push(pl_x, bar_index - pivLR)
        array.push(pl_y, pl)
        f_trim_arrays()

    if not na(ph):
        array.push(ph_x, bar_index - pivLR)
        array.push(ph_y, ph)
        f_trim_arrays()

    upTL: Persistent[Line] = na(Line)
    downTL: Persistent[Line] = na(Line)

    def f_update_line(id: Line, x1: int, y1: float, x2: int, y2: float, isUp: bool):
        res: Line = id
        if na(res):
            res = line.new(x1, y1, x2, y2, extend=extend.right, width=2, color=color.teal if isUp else color.red)
        else:
            line.set_xy1(res, x1, y1)
            line.set_xy2(res, x2, y2)
            line.set_extend(res, extend.right)
            line.set_color(res, color.teal if isUp else color.red)
        return res

    if array.size(pl_x) >= 2:
        ux1 = array.get(pl_x, array.size(pl_x) - 2)
        uy1 = array.get(pl_y, array.size(pl_y) - 2)
        ux2 = array.get(pl_x, array.size(pl_x) - 1)
        uy2 = array.get(pl_y, array.size(pl_y) - 1)
        if uy2 > uy1 and ux2 > ux1:
            upTL = f_update_line(upTL, ux1, uy1, ux2, uy2, True)

            if showHLLH:
                if not na(labHL1):
                    label.delete(labHL1)
                if not na(labHL2):
                    label.delete(labHL2)
                labHL1 = label.new(ux1, uy1, text='HL1', style=label.style_label_up, color=color.new(color.teal, 0), textcolor=color.white, size=size.tiny)
                labHL2 = label.new(ux2, uy2, text='HL2', style=label.style_label_up, color=color.new(color.teal, 0), textcolor=color.white, size=size.tiny)

    if array.size(ph_x) >= 2:
        dx1 = array.get(ph_x, array.size(ph_x) - 2)
        dy1 = array.get(ph_y, array.size(ph_y) - 2)
        dx2 = array.get(ph_x, array.size(ph_x) - 1)
        dy2 = array.get(ph_y, array.size(ph_y) - 1)
        if dy2 < dy1 and dx2 > dx1:
            downTL = f_update_line(downTL, dx1, dy1, dx2, dy2, False)

            if showHLLH:
                if not na(labLH1):
                    label.delete(labLH1)
                if not na(labLH2):
                    label.delete(labLH2)
                labLH1 = label.new(dx1, dy1, text='LH1', style=label.style_label_down, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny)
                labLH2 = label.new(dx2, dy2, text='LH2', style=label.style_label_down, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny)

    upPrice = na if na(upTL) else line.get_price(upTL, bar_index)
    downPrice = na if na(downTL) else line.get_price(downTL, bar_index)

    crossAboveDown = ta.crossover(close, downPrice)
    crossBelowUp = ta.crossunder(close, upPrice)

    longBreak = longs and (not na(downPrice)) and crossAboveDown and (not useMA or close > ma)
    shortBreak = shorts and (not na(upPrice)) and crossBelowUp and (not useMA or close < ma)

    inLong = strategy.position_size > 0
    inShort = strategy.position_size < 0

    longStop = close - atrMult * atr
    longTP = close + tpR * atrMult * atr
    shortStop = close + atrMult * atr
    shortTP = close - tpR * atrMult * atr

    if longBreak and (not inLong):
        strategy.entry('Long', strategy.long)
        strategy.exit('Long-Exit', 'Long', stop=longStop, limit=longTP)

    if shortBreak and (not inShort):
        strategy.entry('Short', strategy.short)
        strategy.exit('Short-Exit', 'Short', stop=shortStop, limit=shortTP)

    if inLong and shortBreak:
        strategy.close('Long', comment='Opp signal')

    if inShort and longBreak:
        strategy.close('Short', comment='Opp signal')

    plot(ma if useMA else na, title='EMA', color=color.new(color.blue, 0))
    plotshape(longBreak, title='Long breakout', style=shape.triangleup, location=location.belowbar, size=size.tiny, color=color.teal, text='▲')
    plotshape(shortBreak, title='Short breakdown', style=shape.triangledown, location=location.abovebar, size=size.tiny, color=color.red, text='▼')

    alertcondition(longBreak, title='Long breakout', message='Price broke above downtrend line')
    alertcondition(shortBreak, title='Short breakdown', message='Price broke below uptrend line')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
