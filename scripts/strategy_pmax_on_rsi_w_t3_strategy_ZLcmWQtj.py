"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, high, hl2, hline, input,
    location, low, math, na, nz, plot, plotshape, script, shape, size, strategy, ta, time,
    timestamp
)
from pynecore.types import Series


@script.strategy('PMax on Rsi w T3 Strategy', 'PmR3St.', overlay=False, precision=2, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(hl2, title='Source'),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3),
    length=input.int(8, 'Tillson T3 Length', minval=1),
    T3a1=input.float(0.7, 'TILLSON T3 Volume Factor', step=0.1),
    Periods=input(10, title='ATR Length'),
    rsilength=input.int(14, minval=1, title='RSI Length'),
    showrsi=input(title='Show RSI?', defval=True),
    showsupport=input(title='Show Moving Average?', defval=True),
    showsignalsk=input(title='Show Crossing Signals?', defval=True),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    dummy0=input(True, title='=Backtest Inputs='),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromYear=input.int(defval=2005, title='From Year', minval=2005),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToYear=input.int(defval=9999, title='To Year', minval=2006)
):
    i = close - close[1] if close >= close[1] else 0
    i2 = close[1] - close if close < close[1] else 0
    def Wwma_Func(src, rsilength):
        wwalpha = 1 / rsilength
        WWMA: Series[float] = 0.0
        WWMA = wwalpha * src + (1 - wwalpha) * nz(WWMA[1])
        return WWMA

    WWMA = Wwma_Func(src, rsilength)
    AvUp = Wwma_Func(i, rsilength)
    AvDown = Wwma_Func(i2, rsilength)
    AvgUp = ta.sma(i, rsilength)
    AvgDown = ta.sma(i2, rsilength)
    k1 = high - close[1] if high > close[1] else 0
    k2 = close[1] - high if high < close[1] else 0
    k3 = low - close[1] if low > close[1] else 0
    k4 = close[1] - low if low < close[1] else 0
    AvgUpH = (AvgUp * (rsilength - 1) + k1) / rsilength
    AvgDownH = (AvgDown * (rsilength - 1) + k2) / rsilength
    AvgUpL = (AvgUp * (rsilength - 1) + k3) / rsilength
    AvgDownL = (AvgDown * (rsilength - 1) + k4) / rsilength
    rs = AvUp / AvDown
    rsi: Series = 0 if rs == -1 else 100 - 100 / (1 + rs)
    rsh = AvgUpH / AvgDownH
    rsih = 0 if rsh == -1 else 100 - 100 / (1 + rsh)
    rsl = AvgUpL / AvgDownL
    rsil = 0 if rsl == -1 else 100 - 100 / (1 + rsl)
    TR = math.max(rsih - rsil, math.abs(rsih - rsi[1]), math.abs(rsil - rsi[1]))
    atr = ta.sma(TR, Periods)
    plot(rsi if showrsi else na, 'RSI', color=color.new(color.new('#8E1599'), 0))
    band1 = hline(70, 'Upper Band', color=color.new('#C0C0C0'))
    band0 = hline(30, 'Lower Band', color=color.new('#C0C0C0'))
    fill(band1, band0, color=color.new(color.new('#9915FF'), 90), title='Background')
    T3e1 = ta.ema(rsi, length)
    T3e2 = ta.ema(T3e1, length)
    T3e3 = ta.ema(T3e2, length)
    T3e4 = ta.ema(T3e3, length)
    T3e5 = ta.ema(T3e4, length)
    T3e6 = ta.ema(T3e5, length)
    T3c1 = -T3a1 * T3a1 * T3a1
    T3c2 = 3 * T3a1 * T3a1 + 3 * T3a1 * T3a1 * T3a1
    T3c3 = -6 * T3a1 * T3a1 - 3 * T3a1 - 3 * T3a1 * T3a1 * T3a1
    T3c4 = 1 + 3 * T3a1 + T3a1 * T3a1 * T3a1 + 3 * T3a1 * T3a1
    T3 = T3c1 * T3e6 + T3c2 * T3e5 + T3c3 * T3e4 + T3c4 * T3e3
    MAvg = T3
    def Pmax_Func(rsi, length):
        longStop: Series = MAvg - Multiplier * atr
        longStopPrev = nz(longStop[1], longStop)
        longStop = math.max(longStop, longStopPrev) if MAvg > longStopPrev else longStop
        shortStop: Series = MAvg + Multiplier * atr
        shortStopPrev = nz(shortStop[1], shortStop)
        shortStop = math.min(shortStop, shortStopPrev) if MAvg < shortStopPrev else shortStop
        dir: Series[int] = 1
        dir = nz(dir[1], dir)
        dir = 1 if dir == -1 and MAvg > shortStopPrev else -1 if dir == 1 and MAvg < longStopPrev else dir
        PMax = longStop if dir == 1 else shortStop
        return PMax

    PMax = Pmax_Func(rsi, length)
    plot(MAvg if showsupport else na, color=color.new(color.black, 0), linewidth=2, title='T3')
    pALL = plot(PMax, color=color.new(color.red, 0), linewidth=2, title='PMax')
    alertcondition(ta.cross(MAvg, PMax), title='Cross Alert', message='PMax - Moving Avg Crossing!')
    alertcondition(ta.crossover(MAvg, PMax), title='Crossover Alarm', message='Moving Avg BUY SIGNAL!')
    alertcondition(ta.crossunder(MAvg, PMax), title='Crossunder Alarm', message='Moving Avg SELL SIGNAL!')
    alertcondition(ta.cross(src, PMax), title='Price Cross Alert', message='PMax - Price Crossing!')
    alertcondition(ta.crossover(src, PMax), title='Price Crossover Alarm', message='PRICE OVER PMax - BUY SIGNAL!')
    alertcondition(ta.crossunder(src, PMax), title='Price Crossunder Alarm', message='PRICE UNDER PMax - SELL SIGNAL!')
    buySignalk = ta.crossover(MAvg, PMax)
    plotshape(PMax * 0.995 if buySignalk and showsignalsk else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallk = ta.crossunder(MAvg, PMax)
    plotshape(PMax * 1.005 if sellSignallk and showsignalsk else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    mPlot = plot(rsi, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    longFillColor = (color.green if MAvg > PMax else na) if highlighting else na
    shortFillColor = (color.red if MAvg < PMax else na) if highlighting else na
    fill(mPlot, pALL, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, pALL, title='DownTrend Highligter', color=shortFillColor)
    Start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    Finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def Timerange():
        return True if time >= Start and time <= Finish else False

    if buySignalk:
        if Timerange():
            strategy.entry('Long', strategy.long)
    if sellSignallk:
        if Timerange():
            strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
