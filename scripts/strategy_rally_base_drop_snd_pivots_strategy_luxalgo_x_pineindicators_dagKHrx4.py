"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, box, close, color, extend, format, high, input, label,
    line, low, math, na, open, script, size, strategy, string, ta, yloc
)
from pynecore.types import Label, Line, Persistent, Series


@udt
class pb:
    price: float = na(float)
    bar: int = na(int)


@script.strategy("Rally Base Drop SND Pivots Strategy [LuxAlgo X PineIndicators]", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, max_boxes_count=500, max_labels_count=500, max_lines_count=500, commission_value=0.01, process_orders_on_close=True, margin_long=20, margin_short=20, slippage=2)
def main(
    tradeMode=input.string("Long & Short", "Trade Mode", options=("Long Only", "Short Only", "Long & Short")),
    reverseConditions=input.bool(False, "Reverse Long/Short Conditions"),
    mult=input(1.0, "ATR Exit Multiplier"),
    rr=input(6.0, "Risk Reward Ratio"),
    len=input.int(3, title="Length"),
    rallyCol=input.color(color.new(color.new('#089981'), 50), title="Rally Color"),
    dropCol=input.color(color.new(color.new('#F23645'), 50), title="Drop Color"),
    hideLen=input.int(0, title="Historical Lookback", minval=0, tooltip="Hide levels further back than this number of bars.\n\nNote: 0 = Show All")
):
    gc: Series = close > open
    rc: Series = close < open
    rally = gc and gc[1]
    drop = rc and rc[1]
    base = not rally and (not drop)

    def check_rb_piv(_len):
        __hist_gc__: Series = gc[0]
        __hist_rc__: Series = rc[0]
        piv_hi: Persistent[pb] = pb(na, na)
        piv_lo: Persistent[pb] = pb(na, na)
        hst: Series = ta.highest(math.max(close, open), _len)
        lst: Series = ta.lowest(math.min(close, open), _len)
        for i in pine_range(0, len - 1):
            if not __hist_gc__[i] or not __hist_rc__[len + i]:
                piv_lo = pb(na, na)
                break
            if i == len - 1 and close > open[len + i] and (close[len] < close[len + i]):
                piv_lo = pb(low[i], bar_index[i])
                box.new(bar_index[len + i], hst[len], bar_index[len], lst[len], bgcolor=dropCol, border_color=dropCol)
                box.new(bar_index[i], hst, bar_index, lst, bgcolor=rallyCol, border_color=rallyCol)
        for i in pine_range(0, len - 1):
            if not __hist_rc__[i] or not __hist_gc__[len + i]:
                piv_hi = pb(na, na)
                break
            if i == len - 1 and close < open[len + i] and (close[len] > close[len + i]):
                piv_hi = pb(high[i], bar_index[i])
                box.new(bar_index[len + i], hst[len], bar_index[len], lst[len], bgcolor=rallyCol, border_color=rallyCol)
                box.new(bar_index[i], hst, bar_index, lst, bgcolor=dropCol, border_color=dropCol)
        return (piv_hi, piv_lo)

    up: Persistent[float] = na(float)
    down: Persistent[float] = na(float)
    lastEntryLevel: Persistent[float] = na(float)
    lastShortEntryLevel: Persistent[float] = na(float)
    lastLongEntryPrice: Persistent[float] = na(float)
    lastLongEntryATR: Persistent[float] = na(float)
    lastShortEntryPrice: Persistent[float] = na(float)
    lastShortEntryATR: Persistent[float] = na(float)

    entryLine: Persistent[Line] = na(Line)
    profitLine: Persistent[Line] = na(Line)
    lossLine: Persistent[Line] = na(Line)

    entryLabel: Persistent[Label] = na(Label)
    slLabel: Persistent[Label] = na(Label)
    tpLabel: Persistent[Label] = na(Label)

    atrValue = ta.atr(14)

    if bar_index >= math.max(len * 2, 14) and (not na(atrValue)):
        ph, pl = check_rb_piv(len)

        his: Persistent[list[Line]] = array.new_line(na)
        los: Persistent[list[Line]] = array.new_line(na)

        if not na(ph.price):
            array.push(his, line.new(ph.bar, ph.price, bar_index, ph.price, color=dropCol))
            up = ph.price
        if not na(pl.price):
            array.push(los, line.new(pl.bar, pl.price, bar_index, pl.price, color=rallyCol))
            down = pl.price

        for i, ln in enumerate(los):
            if close[1] < line.get_y1(ln):
                array.remove(los, i)
                continue
            line.set_x2(ln, bar_index)
        for i, ln in enumerate(his):
            if close[1] > line.get_y1(ln):
                array.remove(his, i)
                continue
            line.set_x2(ln, bar_index)

        if hideLen > 0:
            for bx in box.all:
                if box.get_right(bx) < bar_index - (hideLen + len * 2):
                    box.delete(bx)
            for ln in line.all:
                if line.get_x1(ln) < bar_index - (hideLen + len * 2):
                    line.delete(ln)

        if not reverseConditions:
            if (tradeMode == 'Long Only' or tradeMode == 'Long & Short') and (not na(up)) and ta.crossover(close, up) and (na(lastEntryLevel) or lastEntryLevel != up):
                strategy.entry('L', strategy.long)
                lastEntryLevel = up
                lastLongEntryPrice = close
                lastLongEntryATR = atrValue
            if (tradeMode == 'Short Only' or tradeMode == 'Long & Short') and (not na(down)) and ta.crossunder(close, down) and (na(lastShortEntryLevel) or lastShortEntryLevel != down):
                strategy.entry('S', strategy.short)
                lastShortEntryLevel = down
                lastShortEntryPrice = close
                lastShortEntryATR = atrValue
        else:
            if (tradeMode == 'Long Only' or tradeMode == 'Long & Short') and (not na(down)) and ta.crossunder(close, down) and (na(lastEntryLevel) or lastEntryLevel != down):
                strategy.entry('L', strategy.long)
                lastEntryLevel = down
                lastLongEntryPrice = close
                lastLongEntryATR = atrValue
            if (tradeMode == 'Short Only' or tradeMode == 'Long & Short') and (not na(up)) and ta.crossover(close, up) and (na(lastShortEntryLevel) or lastShortEntryLevel != up):
                strategy.entry('S', strategy.short)
                lastShortEntryLevel = up
                lastShortEntryPrice = close
                lastShortEntryATR = atrValue

        longProfit: Persistent[float] = na(float)
        longStop: Persistent[float] = na(float)
        shortProfit: Persistent[float] = na(float)
        shortStop: Persistent[float] = na(float)
        if strategy.position_size > 0 and (not na(lastLongEntryPrice)) and (not na(lastLongEntryATR)):
            longProfit = lastLongEntryPrice + lastLongEntryATR * mult * rr
            longStop = lastLongEntryPrice - lastLongEntryATR * mult
            strategy.exit('L Exit', 'L', limit=longProfit, stop=longStop)
        if strategy.position_size < 0 and (not na(lastShortEntryPrice)) and (not na(lastShortEntryATR)):
            shortProfit = lastShortEntryPrice - lastShortEntryATR * mult * rr
            shortStop = lastShortEntryPrice + lastShortEntryATR * mult
            strategy.exit('S Exit', 'S', limit=shortProfit, stop=shortStop)

        if strategy.position_size != 0:
            if na(entryLine):
                if strategy.position_size > 0:
                    entryLine = line.new(bar_index, lastLongEntryPrice, bar_index, lastLongEntryPrice, extend=extend.none, color=color.white, width=2)
                    profitLine = line.new(bar_index, longProfit, bar_index, longProfit, extend=extend.none, color=rallyCol, width=2)
                    lossLine = line.new(bar_index, longStop, bar_index, longStop, extend=extend.none, color=dropCol, width=2)
                    entryLabel = label.new(bar_index, lastLongEntryPrice, 'ENTRY: ' + string.tostring(lastLongEntryPrice, format.mintick), style=label.style_label_left, size=size.tiny, color=color.white, textcolor=color.black, yloc=yloc.price)
                    slLabel = label.new(bar_index, longStop, 'SL: ' + string.tostring(longStop, format.mintick), style=label.style_label_left, size=size.tiny, color=dropCol, textcolor=color.white, yloc=yloc.price)
                    tpLabel = label.new(bar_index, longProfit, 'TP: ' + string.tostring(longProfit, format.mintick), style=label.style_label_left, size=size.tiny, color=rallyCol, textcolor=color.white, yloc=yloc.price)
                elif strategy.position_size < 0:
                    entryLine = line.new(bar_index, lastShortEntryPrice, bar_index, lastShortEntryPrice, extend=extend.none, color=color.white, width=2)
                    profitLine = line.new(bar_index, shortProfit, bar_index, shortProfit, extend=extend.none, color=dropCol, width=2)
                    lossLine = line.new(bar_index, shortStop, bar_index, shortStop, extend=extend.none, color=rallyCol, width=2)
                    entryLabel = label.new(bar_index, lastShortEntryPrice, 'ENTRY: ' + string.tostring(lastShortEntryPrice, format.mintick), style=label.style_label_left, size=size.tiny, color=color.white, textcolor=color.black, yloc=yloc.price)
                    slLabel = label.new(bar_index, shortStop, 'SL: ' + string.tostring(shortStop, format.mintick), style=label.style_label_left, size=size.tiny, color=rallyCol, textcolor=color.white, yloc=yloc.price)
                    tpLabel = label.new(bar_index, shortProfit, 'TP: ' + string.tostring(shortProfit, format.mintick), style=label.style_label_left, size=size.tiny, color=dropCol, textcolor=color.white, yloc=yloc.price)
            else:
                line.set_x2(entryLine, bar_index)
                line.set_x2(profitLine, bar_index)
                line.set_x2(lossLine, bar_index)
                if strategy.position_size > 0:
                    label.set_xy(entryLabel, bar_index + 1, lastLongEntryPrice)
                    label.set_xy(slLabel, bar_index + 1, longStop)
                    label.set_xy(tpLabel, bar_index + 1, longProfit)
                elif strategy.position_size < 0:
                    label.set_xy(entryLabel, bar_index + 1, lastShortEntryPrice)
                    label.set_xy(slLabel, bar_index + 1, shortStop)
                    label.set_xy(tpLabel, bar_index + 1, shortProfit)
        elif strategy.position_size == 0 and (not na(strategy.position_size[1])) and (strategy.position_size[1] != 0):
            if not na(entryLine):
                line.set_x2(entryLine, bar_index)
                line.set_x2(profitLine, bar_index)
                line.set_x2(lossLine, bar_index)
                entryLine = na
                profitLine = na
                lossLine = na
                entryLabel = na
                slLabel = na
                tpLabel = na


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
