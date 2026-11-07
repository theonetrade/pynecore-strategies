"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import close, color, hlc3, input, math, na, plot, script, strategy, ta, volume


@script.strategy(overlay=True, shorttitle='Flawless Victory Strategy', default_qty_type=strategy.percent_of_equity, initial_capital=100000, default_qty_value=100, pyramiding=0, title='Flawless Victory Strategy', currency='USD', margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    v1=input(True, title='Version 1 - Doesn\'t Use SL/TP'),
    v2=input(False, title='Version 2 - Uses SL/TP'),
    v3=input(False, title='Version 3 - Uses SL/TP'),
    __input_3__=input.float(6.604, title='Stop Loss %', minval=0.01),
    __input_4__=input.float(2.328, title='Take Profit %', minval=0.01),
    __input_5__=input.float(8.882, title='Stop Loss %', minval=0.01),
    __input_6__=input.float(2.317, title='Take Profit %', minval=0.01)
):
    v2stoploss_input = __input_3__ / 100
    v2takeprofit_input = __input_4__ / 100
    v2stoploss_level = strategy.position_avg_price * (1 - v2stoploss_input)
    v2takeprofit_level = strategy.position_avg_price * (1 + v2takeprofit_input)
    v3stoploss_input = __input_5__ / 100
    v3takeprofit_input = __input_6__ / 100
    v3stoploss_level = strategy.position_avg_price * (1 - v3stoploss_input)
    v3takeprofit_level = strategy.position_avg_price * (1 + v3takeprofit_input)
    plot(v2stoploss_level if v2 and cast_bool(v2stoploss_input) and cast_bool(v2stoploss_level) else na, color=color.new(color.red, 0), style=plot.style_linebr, linewidth=2, title='v2 Stoploss')
    plot(v2takeprofit_level if v2 and cast_bool(v2takeprofit_input) else na, color=color.new(color.green, 0), style=plot.style_linebr, linewidth=2, title='v2 Profit')
    plot(v3stoploss_level if v3 and cast_bool(v3stoploss_input) and cast_bool(v3stoploss_level) else na, color=color.new(color.red, 0), style=plot.style_linebr, linewidth=2, title='v3 Stoploss')
    plot(v3takeprofit_level if v3 and cast_bool(v3takeprofit_input) else na, color=color.new(color.green, 0), style=plot.style_linebr, linewidth=2, title='v3 Profit')
    len: int = 14
    src = close
    up = ta.rma(math.max(ta.change(src), 0), len)
    down = ta.rma(-math.min(ta.change(src), 0), len)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    MFIlength: int = 14
    MFIsrc = hlc3
    MFIupper = math.sum(volume * (0 if ta.change(MFIsrc) <= 0 else MFIsrc), MFIlength)
    MFIlower = math.sum(volume * (0 if ta.change(MFIsrc) >= 0 else MFIsrc), MFIlength)
    def _rsi(MFIupper, MFIlower):
        if MFIlower == 0:
            pass
        if MFIupper == 0:
            pass
        return 100.0 - 100.0 / (1.0 + MFIupper / MFIlower)

    mfi = _rsi(MFIupper, MFIlower)
    length1: int = 20
    src1 = close
    mult1: float = 1.0
    basis1 = ta.sma(src1, length1)
    dev1 = mult1 * ta.stdev(src1, length1)
    upper1 = basis1 + dev1
    lower1 = basis1 - dev1
    length2: int = 17
    src2 = close
    mult2: float = 1.0
    basis2 = ta.sma(src2, length2)
    dev2 = mult2 * ta.stdev(src2, length2)
    upper2 = basis2 + dev2
    lower2 = basis2 - dev2
    RSILowerLevel1: int = 42
    RSIUpperLevel1: int = 70
    BBBuyTrigger1 = src1 < lower1
    BBSellTrigger1 = src1 > upper1
    rsiBuyGuard1 = rsi > RSILowerLevel1
    rsiSellGuard1 = rsi > RSIUpperLevel1
    RSILowerLevel2: int = 42
    RSIUpperLevel2: int = 76
    BBBuyTrigger2 = src2 < lower2
    BBSellTrigger2 = src2 > upper2
    rsiBuyGuard2 = rsi > RSILowerLevel2
    rsiSellGuard2 = rsi > RSIUpperLevel2
    MFILowerLevel3: int = 60
    RSIUpperLevel3: int = 65
    MFIUpperLevel3: int = 64
    BBBuyTrigger3 = src1 < lower1
    BBSellTrigger3 = src1 > upper1
    mfiBuyGuard3 = mfi < MFILowerLevel3
    rsiSellGuard3 = rsi > RSIUpperLevel3
    mfiSellGuard3 = mfi > MFIUpperLevel3
    Buy_1 = BBBuyTrigger1 and rsiBuyGuard1
    Sell_1 = BBSellTrigger1 and rsiSellGuard1
    if v1 == True:
        if Buy_1:
            strategy.entry('Long', strategy.long, alert_message='v1 - Buy Signal!')
        if Sell_1:
            strategy.close('Long', alert_message='v1 - Sell Signal!')
    Buy_2 = BBBuyTrigger2 and rsiBuyGuard2
    Sell_2 = BBSellTrigger2 and rsiSellGuard2
    if v2 == True:
        if Buy_2:
            strategy.entry('Long', strategy.long, alert_message='v2 - Buy Signal!')
        if Sell_2:
            strategy.close('Long', alert_message='v2 - Sell Signal!')
        strategy.exit('Stoploss/TP', 'Long', stop=v2stoploss_level, limit=v2takeprofit_level)
    Buy_3 = BBBuyTrigger3 and mfiBuyGuard3
    Sell_3 = BBSellTrigger3 and rsiSellGuard3 and mfiSellGuard3
    if v3 == True:
        if Buy_3:
            strategy.entry('Long', strategy.long, alert_message='v2 - Buy Signal!')
        if Sell_3:
            strategy.close('Long', alert_message='v2 - Sell Signal!')
        strategy.exit('Stoploss/TP', 'Long', stop=v3stoploss_level, limit=v3takeprofit_level)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
