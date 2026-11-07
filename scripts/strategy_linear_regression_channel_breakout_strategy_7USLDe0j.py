"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barstate, close, color, extend, input, label, line,
    math, nz, script, size, strategy, ta
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.strategy('Linear Regression Channel Breakout Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    src: Series[float] = input(defval=close, title='Source'),
    len=input.int(defval=20, title='Length', minval=10),
    devlen=input.float(defval=2.3, title='Deviation', minval=0.1, step=0.1),
    extendit=input(defval=True, title='Extend Lines'),
    showfibo=input(defval=False, title='Show Fibonacci Levels'),
    showbroken=input.bool(defval=True, title='Show Broken Channel', inline='brk'),
    brokencol=input.color(defval=color.blue, title='', inline='brk'),
    upcol=input.color(defval=color.lime, title='Up/Down Trend Colors', inline='trcols'),
    dncol=input.color(defval=color.red, title='', inline='trcols'),
    widt=input(defval=2, title='Line Width'),
    enable_stop_loss=input.bool(False, title='Enable Stop Loss'),
    enable_take_profit=input.bool(True, title='Enable Take Profit'),
    __input_12__=input.float(10.0, title='Stop Loss %', step=0.1),
    __input_13__=input.float(11.0, title='Take Profit %', step=0.1)
):
    stop_loss_pct = __input_12__ / 100
    take_profit_pct = __input_13__ / 100
    fibo_ratios: Persistent[list[float]] = array.new_float(0)
    colors: Persistent[list[Color]] = array.new_color(2)
    if barstate.isfirst:
        array.unshift(colors, upcol)
        array.unshift(colors, dncol)
        array.push(fibo_ratios, 0.236)
        array.push(fibo_ratios, 0.382)
        array.push(fibo_ratios, 0.618)
        array.push(fibo_ratios, 0.786)
    def get_channel(src: Series, len):
        mid = math.sum(src, len) / len
        slope = ta.linreg(src, len, 0) - ta.linreg(src, len, 1)
        intercept = mid - slope * math.floor(len / 2) + (1 - len % 2) / 2 * slope
        endy = intercept + slope * (len - 1)
        dev: float = 0.0
        for x in pine_range(0, len - 1, 1):
            dev = dev + math.pow(src[x] - (slope * (len - x) + intercept), 2)
        dev = math.sqrt(dev / len)
        return (intercept, endy, dev, slope)

    slope: Series
    y1_, y2_, dev, slope = get_channel(src, len)
    outofchannel: Series = 0 if slope > 0 and close < y2_ - dev * devlen else 2 if slope < 0 and close > y2_ + dev * devlen else -1
    reglines: Persistent[list[Line]] = array.new_line(3)
    fibolines: Persistent[list[Line]] = array.new_line(4)
    for x in pine_range(0, 2, 1):
        if not showbroken or outofchannel != x or nz(outofchannel[1], -1) != -1:
            line.delete(array.get(reglines, x))
        else:
            line.set_color(array.get(reglines, x), color=brokencol)
            line.set_width(array.get(reglines, x), width=2)
            line.set_style(array.get(reglines, x), style=line.style_dotted)
            line.set_extend(array.get(reglines, x), extend=extend.none)
        array.set(reglines, x, line.new(x1=bar_index - (len - 1), y1=y1_ + dev * devlen * (x - 1), x2=bar_index, y2=y2_ + dev * devlen * (x - 1), color=array.get(colors, math.round(math.max(math.sign(slope), 0))), style=line.style_solid if x % 2 == 1 else line.style_dashed, width=widt, extend=extend.right if extendit else extend.none))
    if showfibo:
        for x in pine_range(0, 3, 1):
            line.delete(array.get(fibolines, x))
            array.set(fibolines, x, line.new(x1=bar_index - (len - 1), y1=y1_ - dev * devlen + dev * devlen * 2 * array.get(fibo_ratios, x), x2=bar_index, y2=y2_ - dev * devlen + dev * devlen * 2 * array.get(fibo_ratios, x), color=array.get(colors, math.round(math.max(math.sign(slope), 0))), style=line.style_dotted, width=widt, extend=extend.right if extendit else extend.none))
    sidelab: Persistent[Label] = label.new(x=bar_index - (len - 1), y=y1_, text='S', size=size.large)
    txt = ('⇑' if slope > slope[1] else '⇗') if slope > 0 else ('⇓' if slope < slope[1] else '⇘') if slope < 0 else '⇒'
    stl = (label.style_label_up if slope > slope[1] else label.style_label_upper_right) if slope > 0 else (label.style_label_down if slope < slope[1] else label.style_label_lower_right) if slope < 0 else label.style_label_right
    label.set_style(sidelab, stl)
    label.set_text(sidelab, txt)
    label.set_x(sidelab, bar_index - (len - 1))
    label.set_y(sidelab, y1_ - dev * devlen if slope > 0 else y1_ + dev * devlen if slope < 0 else y1_)
    label.set_color(sidelab, upcol if slope > 0 else dncol if slope < 0 else color.blue)
    longCondition = slope < 0 and close > y2_ + dev * devlen or (slope > 0 and close > y2_ + dev * devlen)
    if longCondition:
        strategy.entry('Long', strategy.long)
    if strategy.position_size > 0:
        entry_price = strategy.position_avg_price
        if enable_stop_loss:
            strategy.exit('Long Stop Loss', 'Long', stop=entry_price * (1 - stop_loss_pct))
        if enable_take_profit:
            strategy.exit('Long Take Profit', 'Long', limit=entry_price * (1 + take_profit_pct))
    shortCondition = slope > 0 and close < y2_ - dev * devlen or (slope < 0 and close < y2_ - dev * devlen)
    if shortCondition:
        strategy.entry('Short', strategy.short)
    if strategy.position_size < 0:
        entry_price = strategy.position_avg_price
        if enable_stop_loss:
            strategy.exit('Short Stop Loss', 'Short', stop=entry_price * (1 + stop_loss_pct))
        if enable_take_profit:
            strategy.exit('Short Take Profit', 'Short', limit=entry_price * (1 - take_profit_pct))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
