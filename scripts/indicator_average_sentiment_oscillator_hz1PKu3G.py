"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, open, plot, script, ta


@script.indicator('Average Sentiment Oscillator', shorttitle='ASO', na_bool=True)
def main(
    length=input.int(10, 'Period?', minval=1, maxval=100),
    mode=input.int(0, 'Calculation Method:', minval=0, maxval=2)
):
    intrarange = high - low
    grouplow = ta.lowest(low, length)
    grouphigh = ta.highest(high, length)
    groupopen = open[length - 1]
    grouprange = grouphigh - grouplow
    K1 = 1 if intrarange == 0 else intrarange
    K2 = 1 if grouprange == 0 else grouprange
    intrabarbulls = (close - low + high - open) / 2 * 100 / K1
    groupbulls = (close - grouplow + grouphigh - groupopen) / 2 * 100 / K2
    intrabarbears = (high - close + open - low) / 2 * 100 / K1
    groupbears = (grouphigh - close + groupopen - grouplow) / 2 * 100 / K2
    TempBufferBulls = (intrabarbulls + groupbulls) / 2 if mode == 0 else intrabarbulls if mode == 1 else groupbulls
    TempBufferBears = (intrabarbears + groupbears) / 2 if mode == 0 else intrabarbears if mode == 1 else groupbears
    ASOBulls = ta.sma(TempBufferBulls, length)
    ASOBears = ta.sma(TempBufferBears, length)
    plot(ASOBulls, color=color.new(color.blue, 0), linewidth=2)
    plot(ASOBears, color=color.new(color.red, 0), linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)