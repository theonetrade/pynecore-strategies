"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, low, math, na, nz, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='KAMA Strategy - Kaufman\'s Adaptive Moving Average', shorttitle='KAMA Strategy', overlay=True, default_qty_value=100, default_qty_type=strategy.percent_of_equity, initial_capital=10000, max_bars_back=1000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    src: Series[float] = input(title='Source', defval=close),
    KAMA1SL=input(title='KAMA 1 Stop Loss', defval=True),
    ATRTSL=input(title='ATR Trailing Stop Loss', defval=False),
    PSARSL=input(title='PSAR Stop Loss', defval=False),
    length1=input(title='KAMA 1: Length', defval=14),
    fastLength1=input(title='KAMA 1: Fast KAMA Length', defval=2),
    slowLength1=input(title='KAMA 1: Slow KAMA Length', defval=20),
    length2=input(title='KAMA 2: Length 2', defval=15),
    fastLength2=input(title='KAMA 2: Fast KAMA Length', defval=3),
    slowLength2=input(title='KAMA 2: Slow KAMA Length', defval=22),
    length3=input(title='KAMA 3: Length 3', defval=16),
    fastLength3=input(title='KAMA 3: Fast KAMA Length', defval=4),
    slowLength3=input(title='KAMA 3: Slow KAMA Length', defval=24),
    length4=input(title='KAMA 4: Length', defval=17),
    fastLength4=input(title='KAMA 4: Fast KAMA Length', defval=5),
    slowLength4=input(title='KAMA 4: Slow KAMA Length', defval=26),
    length5=input(title='KAMA 5: Length', defval=18),
    fastLength5=input(title='KAMA 5: Fast KAMA Length', defval=6),
    slowLength5=input(title='KAMA 5: Slow KAMA Length', defval=28),
    length6=input(title='KAMA 6: Length', defval=19),
    fastLength6=input(title='KAMA 6: Fast KAMA Length', defval=7),
    slowLength6=input(title='KAMA 6: Slow KAMA Length', defval=30),
    length7=input(title='KAMA 7: Length', defval=20),
    fastLength7=input(title='KAMA 7: Fast KAMA Length', defval=8),
    slowLength7=input(title='KAMA 7: Slow KAMA Length', defval=32),
    length8=input(title='KAMA 8: Length', defval=21),
    fastLength8=input(title='KAMA 8: Fast KAMA Length', defval=9),
    slowLength8=input(title='KAMA 8: Slow KAMA Length', defval=34),
    entryFilter=input.float(title='KAMA Entry Filter', defval=1, minval=0.01),
    exitFilter=input.float(title='KAMA Exit Filter', defval=0.5, minval=0.01),
    atrLookback=input(defval=14, title='Trailing ATR Lookback Period'),
    multiplier=input.float(defval=3, title='Trailing ATR Multiplier', step=0.1, minval=0.5, maxval=4),
    trailMode=input.string(title='Trail Mode', defval='Trailing', options=('Running', 'Trailing')),
    trigInput=input.string(title='Trigger Trailing Stop On', defval='Wick', options=('Close', 'Wick')),
    start=input(0.02, 'PSAR Start'),
    increment=input(0.02, 'PSAR Increment'),
    maximum=input(0.2, 'PSAR Max Value')
):
    def getKAMA(src, length1, fastLength1, slowLength1):
        mom = math.abs(ta.change(src, length1))
        volatility = math.sum(math.abs(ta.change(src)), length1)
        er = mom / volatility if volatility != 0 else 0
        fastAlpha = 2 / (fastLength1 + 1)
        slowAlpha = 2 / (slowLength1 + 1)
        sc = math.pow(er * (fastAlpha - slowAlpha) + slowAlpha, 2)
        kama: Series[float] = 0.0
        kama = sc * src + (1 - sc) * nz(kama[1])
        return kama

    kama1: Series = getKAMA(src, length1, fastLength1, slowLength1)
    kama2 = getKAMA(src, length2, fastLength2, slowLength2)
    kama3: Series = getKAMA(src, length3, fastLength3, slowLength3)
    kama4 = getKAMA(src, length4, fastLength4, slowLength4)
    kama5 = getKAMA(src, length5, fastLength5, slowLength5)
    kama6 = getKAMA(src, length6, fastLength6, slowLength6)
    kama7 = getKAMA(src, length7, fastLength7, slowLength7)
    kama8: Series = getKAMA(src, length8, fastLength8, slowLength8)
    kama1delta = kama1 - kama1[1]
    kama3delta = kama3 - kama3[1]
    kama8delta = kama8 - kama8[1]
    plot(kama1, title='KAMA 1', color=color.new(color.new('#E91E63'), 0), display=display.all, linewidth=2)
    plot(kama2, title='KAMA 2', color=color.new(color.red, 0), display=display.all)
    plot(kama3, title='KAMA 3', color=color.new(color.red, 0), display=display.all)
    plot(kama4, title='KAMA 4', color=color.new(color.orange, 0), display=display.all)
    plot(kama5, title='KAMA 5', color=color.new(color.orange, 0), display=display.all)
    plot(kama6, title='KAMA 6', color=color.new(color.yellow, 0), display=display.all)
    plot(kama7, title='KAMA 7', color=color.new(color.yellow, 0), display=display.all)
    plot(kama8, title='KAMA 8', color=color.new(color.white, 0), display=display.all)
    entryMAAF = entryFilter * ta.stdev(kama1delta, length1)
    exitMAAF = exitFilter * ta.stdev(kama1delta, length1)
    srcEma = ta.ema(src, length1)
    atrValue = ta.atr(atrLookback)
    atrMultiplied = atrValue * multiplier
    atrLow = low - atrMultiplied
    trailAtrLow: Series = atrLow
    trailAtrLow = trailAtrLow if na(trailAtrLow[1]) else atrLow if atrLow >= trailAtrLow[1] else trailAtrLow[1]
    trigSupport = close if trigInput == 'Close' else low if trigInput == 'Wick' else na
    supportHit = trigSupport <= trailAtrLow
    trailAtrLow = atrLow if supportHit else trailAtrLow
    plotLow = trailAtrLow if ATRTSL else na
    plot(plotLow, title='ATR Low', color=color.new(color.white, 50), style=plot.style_linebr, linewidth=1, display=display.all)
    psar = ta.sar(start, increment, maximum)
    psarPlot = psar if PSARSL else na
    plot(psarPlot, 'Parabolic SAR', style=plot.style_cross, color=color.new(color.new('#3A6CA8'), 0), display=display.all)
    long = kama1delta > 0 and kama1delta > entryMAAF
    if long:
        strategy.entry('Buy', strategy.long)
    longClose = (ta.crossunder(close, psar) if PSARSL else False) or (kama1delta < 0 and math.abs(kama1delta) > exitMAAF if KAMA1SL else na) or (supportHit if ATRTSL else False)
    if longClose:
        strategy.close('Buy', comment='Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
