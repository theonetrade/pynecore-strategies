"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, extend, high, input,
    line, low, na, script, strategy, ta, volume
)
from pynecore.types import Line, Persistent, Series


@script.strategy("Reversal Trading Bot Strategy [BullByte] Final Version", overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=30, calc_on_every_tick=False, process_orders_on_close=True, max_lines_count=500, max_labels_count=500)
def main(
    rsiLength=input.int(8, "RSI Length", tooltip="Number of bars used to calculate the Relative Strength Index (RSI)."),
    fastRsiLength=input.int(14, "Fast RSI Length", tooltip="Number of bars for fast RSI crossover confirmation."),
    slowRsiLength=input.int(21, "Slow RSI Length", tooltip="Number of bars for slow RSI crossover confirmation."),
    bbLength=input.int(20, "BB Length", tooltip="Number of bars used to calculate Bollinger Bands (BB)."),
    adxThreshold=input.int(20, "ADX Threshold", tooltip="Minimum ADX value to confirm trend strength."),
    divLookback=input.int(5, "Divergence Lookback", tooltip="Number of past bars to analyze for RSI divergence."),
    volumeFilter=input.bool(False, "Volume ≥ 2× SMA", tooltip="If enabled, requires volume to be at least twice its 20-bar SMA."),
    adxFilter=input.bool(False, "ADX Strength & Alignment", tooltip="If enabled, requires ADX above threshold and DI+ > DI- for longs, DI- > DI+ for shorts."),
    bbFilter=input.bool(False, "BB Close Confirmation", tooltip="If enabled, requires close below lower BB for longs, above upper BB for shorts."),
    rsiCrossFilter=input.bool(False, "RSI Crossover Confirmation", tooltip="If enabled, requires fast RSI to cross over slow RSI for longs, cross under for shorts."),
    __input_10__=input.float(1.0, "Stop-Loss %", step=0.1, tooltip="Percentage below/above entry price for stop-loss."),
    __input_11__=input.float(2.0, "Take-Profit %", step=0.1, tooltip="Percentage above/below entry price for take-profit.")
):
    stopLossPct = __input_10__ / 100
    takeProfitPct = __input_11__ / 100

    rsi = inline_series(ta.rsi(close, rsiLength), 1)
    diP_raw: Series
    diM_raw: Series
    adx_raw: Series
    diP_raw, diM_raw, adx_raw = ta.dmi(14, 14)
    diP = diP_raw[1]
    diM = diM_raw[1]
    adx = adx_raw[1]
    ub: Series
    mb: Series
    lb: Series
    ub, mb, lb = ta.bb(close, bbLength, 2)
    upperBB = ub[1]
    midBB = mb[1]
    lowerBB = lb[1]
    volSma = inline_series(ta.sma(volume, 20), 1)

    efastRSI = inline_series(ta.rsi(close, fastRsiLength), 1)
    eslowRSI = inline_series(ta.rsi(close, slowRsiLength), 1)
    fastCrossUp = ta.crossover(efastRSI, eslowRSI)
    fastCrossDown = ta.crossunder(efastRSI, eslowRSI)
    rsiCrossOKBull = not rsiCrossFilter or fastCrossUp
    rsiCrossOKBear = not rsiCrossFilter or fastCrossDown

    prevLow = inline_series(ta.lowest(low, divLookback), 1)
    prevLow_1 = inline_series(ta.lowest(low, divLookback), 2)
    prevRsi = inline_series(ta.lowest(rsi, divLookback), 1)
    prevRsi_1 = inline_series(ta.lowest(rsi, divLookback), 2)
    bullDiv = prevLow < prevLow_1 and prevRsi > prevRsi_1

    prevHigh = inline_series(ta.highest(high, divLookback), 1)
    prevHigh_1 = inline_series(ta.highest(high, divLookback), 2)
    prevRsiH = inline_series(ta.highest(rsi, divLookback), 1)
    prevRsiH_1 = inline_series(ta.highest(rsi, divLookback), 2)
    bearDiv = prevHigh > prevHigh_1 and prevRsiH < prevRsiH_1

    volOKBull = not volumeFilter or volume[1] >= 2 * volSma
    adxOKBull = not adxFilter or (adx > adxThreshold and diP > diM)
    bbOKBull = not bbFilter or close[1] <= lowerBB

    volOKBear = not volumeFilter or volume[1] >= 2 * volSma
    adxOKBear = not adxFilter or (adx > adxThreshold and diM > diP)
    bbOKBear = not bbFilter or close[1] >= upperBB

    bullEntry = bullDiv and volOKBull and adxOKBull and bbOKBull and rsiCrossOKBull
    bearEntry = bearDiv and volOKBear and adxOKBear and bbOKBear and rsiCrossOKBear

    tpLine: Persistent[Line] = na(Line)
    slLine: Persistent[Line] = na(Line)
    prevPosSize: Persistent[float] = 0.0
    tpPrice: Persistent[float] = na(float)
    slPrice: Persistent[float] = na(float)

    if barstate.isconfirmed:
        if bullEntry:
            strategy.entry('Long', strategy.long)
        if bearEntry:
            strategy.entry('Short', strategy.short)

        if strategy.position_size > 0:
            strategy.exit('Long Exit', from_entry='Long', stop=strategy.position_avg_price * (1 - stopLossPct), limit=strategy.position_avg_price * (1 + takeProfitPct))
        if strategy.position_size < 0:
            strategy.exit('Short Exit', from_entry='Short', stop=strategy.position_avg_price * (1 + stopLossPct), limit=strategy.position_avg_price * (1 - takeProfitPct))

        if strategy.position_size != prevPosSize and strategy.position_size != 0:
            line.delete(tpLine)
            line.delete(slLine)
            entryPrice = strategy.opentrades.entry_price(0)
            if strategy.position_size > 0:
                tpPrice = entryPrice * (1 + takeProfitPct)
                slPrice = entryPrice * (1 - stopLossPct)
            else:
                tpPrice = entryPrice * (1 - takeProfitPct)
                slPrice = entryPrice * (1 + stopLossPct)
            tpLine = line.new(bar_index, tpPrice, bar_index + 1, tpPrice, extend=extend.right, style=line.style_dashed, color=color.green)
            slLine = line.new(bar_index, slPrice, bar_index + 1, slPrice, extend=extend.right, style=line.style_dashed, color=color.red)

        if strategy.position_size == 0 and prevPosSize != 0:
            line.delete(tpLine)
            line.delete(slLine)
            tpLine = na
            slLine = na
            tpPrice = na
            slPrice = na

        prevPosSize = strategy.position_size

    alertcondition(bullEntry, title='BullByte Long Entry', message='Long entry signal detected at {{close}}')
    alertcondition(bearEntry, title='BullByte Short Entry', message='Short entry signal detected at {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
