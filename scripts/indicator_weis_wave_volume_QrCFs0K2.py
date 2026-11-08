"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, script, ta,
    volume
)
from pynecore.types import NA, Series


@script.indicator('Weis Wave Volume', shorttitle='WWV', overlay=False, timeframe='')
def main(
    methodtype=input.string(defval='ATR', options=('ATR', 'Traditional', 'Part of Price'), title='Renko Assignment Method'),
    methodvalue=input.float(defval=14.0, minval=0, title='Value'),
    pricesource=input.string(defval='Close', options=('Close', 'Open / Close', 'High / Low'), title='Price Source'),
    useTrueRange=input.string(defval='Auto', options=('Always', 'Auto', 'Never'), title='Use True Range instead of Volume'),
    isOscillating=input(defval=False, title='Oscillating'),
    normalize=input(defval=False, title='Normalize')
):
    useClose = pricesource == 'Close'
    useOpenClose = pricesource == 'Open / Close' or useClose
    vol: Series = ta.tr if useTrueRange == 'Always' or (useTrueRange == 'Auto' and na(volume)) else volume
    op = close if useClose else open
    hi = (close if close >= op else op) if useOpenClose else high
    lo = (close if close <= op else op) if useOpenClose else low
    if methodtype == 'ATR':
        methodvalue = ta.atr(math.round(methodvalue))
    if methodtype == 'Part of Price':
        methodvalue = close / methodvalue
    currclose: Series = NA(float)
    prevclose = nz(currclose[1])
    prevhigh = prevclose + methodvalue
    prevlow = prevclose - methodvalue
    currclose = hi if hi > prevhigh else lo if lo < prevlow else prevclose
    direction: Series = NA(int)
    direction = 1 if currclose > prevclose else -1 if currclose < prevclose else nz(direction[1])
    directionHasChanged = ta.change(direction) != 0
    directionIsUp = direction > 0
    directionIsDown = direction < 0
    barcount: Series[int] = 1
    barcount = barcount[1] + barcount if not directionHasChanged and normalize else barcount
    vol = vol[1] + vol if not directionHasChanged else vol
    res = vol / barcount if barcount > 1 else vol
    plot(-res if isOscillating and directionIsDown else res, style=plot.style_columns, color=color.new(color.green, 75) if directionIsUp else color.new(color.red, 75), linewidth=3, title='Wave Volume')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
