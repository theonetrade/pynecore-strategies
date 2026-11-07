"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, fill, input, math, na, plot, script, strategy,
    ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Hull Suite Strategy', overlay=True, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='long', options=('long', 'short', 'all')),
    testStartYear=input(2016, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(2030, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(30, 'Backtest Stop Day'),
    src: Series[float] = input(close, title='Source'),
    modeSwitch=input.string('Hma', title='Hull Variation', options=('Hma', 'Thma', 'Ehma')),
    length=input(55, title='Length(180-200 for floating S/R , 55 for swing entry)'),
    switchColor=input(True, 'Color Hull according to trend?'),
    candleCol=input(False, title='Color candles based on Hull\'s Trend?'),
    visualSwitch=input(True, title='Show as a Band?'),
    thicknesSwitch=input(1, title='Line Thickness'),
    transpSwitch=input.int(40, title='Band Transparency', step=5)
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    def HMA(_src, _length):
        return ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))

    def EHMA(_src, _length):
        return ta.ema(2 * ta.ema(_src, _length / 2) - ta.ema(_src, _length), math.round(math.sqrt(_length)))

    def THMA(_src, _length):
        return ta.wma(ta.wma(_src, _length / 3) * 3 - ta.wma(_src, _length / 2) - ta.wma(_src, _length), _length)

    def Mode(modeSwitch, src, len):
        return HMA(src, len) if modeSwitch == 'Hma' else EHMA(src, len) if modeSwitch == 'Ehma' else THMA(src, len / 2) if modeSwitch == 'Thma' else na

    HULL: Series = Mode(modeSwitch, src, length)
    MHULL = HULL
    SHULL = HULL[2]
    hullColor = (color.new('#00FF00') if HULL > HULL[2] else color.new('#FF0000')) if switchColor else color.new('#FF9800')
    Fi1 = plot(MHULL, title='MHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    Fi2 = plot(SHULL if visualSwitch else na, title='SHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    fill(Fi1, Fi2, title='Band Filler', color=color.new(hullColor, transpSwitch))
    barcolor(color=(hullColor if switchColor else na) if candleCol else na)
    testPeriod_1 = testPeriod()
    if HULL > HULL[2] and testPeriod_1:
        strategy.entry('buy', strategy.long)
    testPeriod_2 = testPeriod()
    if HULL < HULL[2] and testPeriod_2:
        strategy.entry('sell', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)