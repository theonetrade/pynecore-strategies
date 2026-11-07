"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    barcolor, close, color, high, input, location, low, math, na, nz, open,
    plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series


@script.strategy('Chandelier Exit ZLSMA Strategy', shorttitle='CE_ZLSMA', overlay=True, initial_capital=1000, default_qty_value=10, default_qty_type=strategy.percent_of_equity, calc_on_every_tick=False, process_orders_on_close=True, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    length=input(title='ATR Period', defval=1),
    mult=input.float(title='ATR Multiplier', step=0.1, defval=2),
    showLabels=input(title='Show Buy/Sell Labels ?', tooltip='Created by Chandelier Exit (CE)', defval=False),
    isSignalLabelEnabled=input(title='Show Signal Labels ?', defval=True),
    useClose=input(title='Use Close Price for Extrema ?', defval=True),
    zcolorchange=input(title='Enable Rising/Decreasing Highlightning', defval=False),
    zlsmaLength=input(title='ZLSMA Length', defval=50),
    offset=input(title='Offset', defval=0)
):
    maximumYellowRed: Color = color.rgb(255, 203, 98)
    rajah: Color = color.rgb(242, 166, 84)
    magicMint: Color = color.rgb(171, 237, 198)
    languidLavender: Color = color.rgb(232, 215, 255)
    maximumBluePurple: Color = color.rgb(181, 161, 226)
    skyBlue: Color = color.rgb(144, 226, 244)
    lightGray: Color = color.rgb(214, 214, 214)
    quickSilver: Color = color.rgb(163, 163, 163)
    mediumAquamarine: Color = color.rgb(104, 223, 153)
    carrotOrange: Color = color.rgb(239, 146, 46)
    haClose: float = cast_float(1) / 4 * (open + high + low + close)
    atr = mult * ta.atr(length)
    longStop: Series = (ta.highest(haClose, length) if useClose else ta.highest(haClose, length)) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if haClose > longStopPrev else longStop
    shortStop: Series = (ta.lowest(haClose, length) if useClose else ta.lowest(haClose, length)) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if haClose < shortStopPrev else shortStop
    dir: PersistentSeries[int] = 1
    dir = 1 if haClose > shortStopPrev else -1 if haClose < longStopPrev else dir
    buySignal = dir == 1 and dir[1] == -1
    plotshape(longStop if buySignal and showLabels else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=mediumAquamarine, textcolor=color.white)
    sellSignal = dir == -1 and dir[1] == 1
    plotshape(shortStop if sellSignal and showLabels else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=carrotOrange, textcolor=color.white)
    changeCond = dir != dir[1]
    lsma = ta.linreg(haClose, zlsmaLength, offset)
    lsma2 = ta.linreg(lsma, zlsmaLength, offset)
    eq = lsma - lsma2
    zlsma: Series = lsma + eq
    zColor = (magicMint if zlsma > zlsma[1] else rajah) if zcolorchange else languidLavender
    plot(zlsma, title='ZLSMA', linewidth=2, color=zColor)
    isTradeOpen: Persistent[str] = ''
    signalCache: Persistent[str] = ''
    crossover_1 = ta.crossover(haClose, zlsma)
    enterLong: bool = buySignal and crossover_1
    exitLong: bool = ta.crossunder(haClose, zlsma)
    crossunder_1 = ta.crossunder(haClose, zlsma)
    enterShort: bool = sellSignal and crossunder_1
    exitShort: bool = ta.crossover(haClose, zlsma)
    if signalCache == 'long entry':
        signalCache = ''
        enterLong = True
    elif signalCache == 'short entry':
        signalCache = ''
        enterShort = True
    if isTradeOpen == '':
        if exitShort and (not enterLong):
            exitShort = False
        if exitLong and (not enterShort):
            exitLong = False
        if enterLong and exitShort:
            isTradeOpen = 'long'
            exitShort = False
        elif enterShort and exitLong:
            isTradeOpen = 'short'
            exitLong = False
        elif enterLong:
            isTradeOpen = 'long'
        elif enterShort:
            isTradeOpen = 'short'
    elif isTradeOpen == 'long':
        if exitShort:
            exitShort = False
        if enterLong:
            enterLong = False
        if enterShort and exitLong:
            enterShort = False
            signalCache = 'short entry'
        if exitLong:
            isTradeOpen = ''
    elif isTradeOpen == 'short':
        if exitLong:
            exitLong = False
        if enterShort:
            enterShort = False
        if enterLong and exitShort:
            enterLong = False
            signalCache = 'long entry'
        if exitShort:
            isTradeOpen = ''
    plotshape(zlsma if isSignalLabelEnabled and enterLong else na, title='LONG', text='L', style=shape.labelup, color=mediumAquamarine, textcolor=color.white, size=size.tiny, location=location.absolute)
    plotshape(zlsma if isSignalLabelEnabled and enterShort else na, title='SHORT', text='S', style=shape.labeldown, color=carrotOrange, textcolor=color.white, size=size.tiny, location=location.absolute)
    plotshape(zlsma if isSignalLabelEnabled and exitLong else na, title='LONG EXIT', style=shape.circle, color=magicMint, size=size.tiny, location=location.absolute)
    plotshape(zlsma if isSignalLabelEnabled and exitShort else na, title='SHORT EXIT', style=shape.circle, color=rajah, size=size.tiny, location=location.absolute)
    barcolor(color=mediumAquamarine if isTradeOpen == 'long' else carrotOrange if isTradeOpen == 'short' else na)
    if exitLong and strategy.position_size > 0:
        strategy.close('long', comment='EXIT_LONG')
    if exitShort and strategy.position_size < 0:
        strategy.close('short', comment='EXIT_SHORT')
    if enterLong:
        strategy.entry('long', strategy.long, comment='ENTER_LONG')
    if enterShort:
        strategy.entry('short', strategy.short, comment='ENTER_SHORT')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
