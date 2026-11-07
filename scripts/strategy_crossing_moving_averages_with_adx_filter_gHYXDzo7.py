"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, math, na, plot, script, strategy, ta


@script.strategy("Crossing Moving Averages with ADX Filter)", overlay=True, pyramiding=0)
def main(
    fastLen=input.int(20, title="Fast MA Length"),
    slowLen=input.int(120, title="Slow MA Length"),
    maType=input.string("SMA", title="Moving Average Type", options=("SMA", "EMA", "WMA", "LMA")),
    useADX=input.bool(True, title="Enable ADX Filter"),
    adxLen=input.int(14, title="ADX Length"),
    adxThreshold=input.float(20.0, title="ADX Threshold")
):
    def ma(src, len):
        out: float = na(float)
        if maType == 'SMA':
            out = ta.sma(src, len)
        elif maType == 'EMA':
            out = ta.ema(src, len)
        elif maType == 'WMA':
            out = ta.wma(src, len)
        else:
            out = ta.rma(src, len)
        return out

    fastMA = ma(close, fastLen)
    slowMA = ma(close, slowLen)

    longBias = fastMA > slowMA
    shortBias = fastMA < slowMA

    upMove = high - high[1]
    downMove = low[1] - low

    plusDM = upMove if upMove > downMove and upMove > 0 else 0.0
    minusDM = downMove if downMove > upMove and downMove > 0 else 0.0

    trur = ta.rma(ta.tr(True), adxLen)
    plusDI = 100 * ta.rma(plusDM, adxLen) / trur
    minusDI = 100 * ta.rma(minusDM, adxLen) / trur

    dx = 100 * math.abs(plusDI - minusDI) / (plusDI + minusDI)
    adx = ta.rma(dx, adxLen)

    adxOK = not useADX or adx >= adxThreshold

    enterLong = longBias and adxOK and (strategy.position_size <= 0)
    enterShort = shortBias and adxOK and (strategy.position_size >= 0)

    if enterLong:
        strategy.entry('Long', strategy.long)

    if enterShort:
        strategy.entry('Short', strategy.short)

    plot(fastMA, 'Fast MA', color=color.blue, linewidth=1)
    plot(slowMA, 'Slow MA', color=color.orange, linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
