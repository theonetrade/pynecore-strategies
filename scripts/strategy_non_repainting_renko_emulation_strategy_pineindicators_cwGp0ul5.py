"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import bar_index, barstate, box, close, color, input, math, na, script, strategy
from pynecore.types import Persistent, PersistentSeries


@script.strategy('Non-Repainting Renko Emulation Strategy [PineIndicators]', overlay=True, calc_on_every_tick=False, max_boxes_count=500, max_labels_count=500, max_lines_count=500, initial_capital=10000, default_qty_value=100, default_qty_type=strategy.percent_of_equity, commission_value=0.01, slippage=2, margin_long=0, margin_short=0, close_by_id=True)
def main(
    brickSize=input.float(3.0, 'Brick Size', step=0.1)
):
    renkoPrice: PersistentSeries[float] = na(float)
    prevRenkoPrice: Persistent[float] = na(float)
    brickDir: PersistentSeries[int] = 0
    newBrick: Persistent[bool] = False
    brickStart: Persistent[int] = bar_index
    if barstate.isconfirmed:
        newBrick = False
        if na(renkoPrice):
            renkoPrice = close
            brickStart = bar_index
        diff = close - renkoPrice
        if math.abs(diff) >= brickSize:
            numBricks = math.floor(math.abs(diff) / brickSize)
            prevRenkoPrice = renkoPrice
            renkoPrice = renkoPrice + numBricks * brickSize * math.sign(diff)
            brickDir = cast_int(math.sign(diff))
            newBrick = True
            lowLevel = prevRenkoPrice if brickDir == 1 else renkoPrice
            highLevel = renkoPrice if brickDir == 1 else prevRenkoPrice
            box.new(brickStart, highLevel, bar_index, lowLevel, border_width=1, border_color=color.green if brickDir == 1 else color.red, bgcolor=color.new(color.green, 70) if brickDir == 1 else color.new(color.red, 70))
            brickStart = bar_index
    if barstate.isconfirmed and newBrick:
        if brickDir[brickSize] < brickDir and renkoPrice[brickSize] < renkoPrice[brickSize * 2] and (renkoPrice < renkoPrice[brickSize]) and (renkoPrice[brickSize * 2] < renkoPrice[brickSize * 3]) and (strategy.position_size <= 0):
            strategy.entry('Long', strategy.long)
        elif brickDir[brickSize] > brickDir and renkoPrice[brickSize] > renkoPrice[brickSize * 2] and (renkoPrice > renkoPrice[brickSize]) and (renkoPrice[brickSize * 2] > renkoPrice[brickSize * 3]) and (strategy.position_size >= 0):
            strategy.entry('Short', strategy.short)
    if barstate.isconfirmed and newBrick:
        if brickDir[brickSize] < brickDir:
            strategy.close('Short')
        elif brickDir[brickSize] > brickDir:
            strategy.close('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
