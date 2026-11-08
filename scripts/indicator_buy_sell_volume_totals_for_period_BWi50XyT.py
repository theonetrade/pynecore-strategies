"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, format, high, input, location, low, plot,
    plotchar, script, time, timestamp, volume
)
from pynecore.types import Persistent


@script.indicator('Buy/Sell Volume Totals for Period', format=format.volume, precision=3, na_bool=True)
def main(
    startTime=input.time(defval=timestamp('10 Dec 2021'), title='Start Time'),
    useEndTime=input(defval=False, title='Use End Time?'),
    endTime=input.time(defval=timestamp('04 Jan 2022'), title='End Time')
):
    inDateRange = time >= startTime and time <= endTime if useEndTime else time >= startTime
    totalBuyVolume: Persistent[float] = 0.0
    totalSellVolume: Persistent[float] = 0.0
    if not inDateRange:
        totalBuyVolume = 0.0
        totalSellVolume = 0.0
    buyVolume = 0 if high == low else volume * (close - low) / (high - low)
    sellVolume = 0 if high == low else volume * (high - close) / (high - low)
    if inDateRange:
        totalBuyVolume = totalBuyVolume + buyVolume
        totalSellVolume = totalSellVolume + sellVolume
    totalBuySellRatio = totalBuyVolume / totalSellVolume if totalSellVolume > 0.0 else 0.0
    isAccumulation = totalBuyVolume > totalSellVolume
    isDistribution = not isAccumulation
    plotchar(totalBuyVolume, 'Total Buy Volume', '', location.top, color=color.new(color.green, 0))
    plotchar(totalSellVolume, 'Total Sell Volume', '', location.top, color=color.new(color.red, 0))
    plotchar(totalBuySellRatio, 'Total Buy/Sell Ratio', '', location.top, color=color.new(color.yellow, 0))
    plot(volume, style=plot.style_columns, color=color.new(color.red, 0), title='BUY+SELL V')
    plot(buyVolume, style=plot.style_columns, color=color.new(color.teal, 0), title='BUY V')
    accDistrColor = color.green if isAccumulation else color.red
    bgcolor(color.new(accDistrColor, 70 if inDateRange else 100))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
