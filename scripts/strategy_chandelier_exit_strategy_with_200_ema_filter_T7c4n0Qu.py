"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barstate, close, high, input, low, math, nz, script, strategy, ta
from pynecore.types import PersistentSeries, Series

calcGroup: str = 'Calculation'
visualGroup: str = 'Visuals'
alertGroup: str = 'Alerts'


@script.strategy('Chandelier Exit Strategy with 200 EMA Filter', shorttitle='CES', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    length=input.int(title='ATR Period', defval=22, group=calcGroup),
    mult=input.float(title='ATR Multiplier', step=0.1, defval=3.0, group=calcGroup),
    useClose=input.bool(title='Use Close Price for Extremums', defval=True, group=calcGroup),
    showLabels=input.bool(title='Show Buy/Sell Labels', defval=True, group=visualGroup),
    highlightState=input.bool(title='Highlight State', defval=True, group=visualGroup),
    awaitBarConfirmation=input.bool(title='Await Bar Confirmation', defval=True, group=alertGroup)
):
    atr = mult * ta.atr(length)
    ema200 = ta.ema(close, 200)
    longStop: Series = (ta.highest(close, length) if useClose else ta.highest(length)) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if close[1] > longStopPrev else longStop
    shortStop: Series = (ta.lowest(close, length) if useClose else ta.lowest(length)) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if close[1] < shortStopPrev else shortStop
    dir: PersistentSeries[int] = 1
    dir = 1 if close > shortStopPrev else -1 if close < longStopPrev else dir
    buySignal = dir == 1 and dir[1] == -1
    sellSignal = dir == -1 and dir[1] == 1
    await__ren__ = barstate.isconfirmed if awaitBarConfirmation else True
    if buySignal and await__ren__ and (close > ema200):
        strategy.entry('Long', strategy.long, stop=low - atr * 0.5)
    if sellSignal and await__ren__ and (close < ema200):
        strategy.entry('Short', strategy.short, stop=high + atr * 0.5)
    if sellSignal and await__ren__:
        strategy.close('Long')
    if buySignal and await__ren__:
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
