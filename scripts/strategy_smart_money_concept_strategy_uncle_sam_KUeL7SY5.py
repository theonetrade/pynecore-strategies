"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, close, color, display, fixnan, high, input, label,
    line, low, math, na, open, plot, script, size, strategy, syminfo, ta, volume, yloc
)
from pynecore.types import Color, Label, Persistent, Series


@udt
class Vol:
    Total: list[float] = na(list)
    Green: list[float] = na(list)
    Red: list[float] = na(list)
    SCR: list[float] = na(list)


@script.strategy('Smart Money Concept - Uncle Sam', shorttitle='Smart Money Concept - Uncle Sam', overlay=True, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=1000, commission_type=strategy.commission.percent, commission_value=0.0, process_orders_on_close=True, use_bar_magnifier=False, margin_long=0, margin_short=0, close_by_id=True)
def main(
    enable_long_strategy=input.bool(True, title='Enable Long Strategy', inline='1'),
    long_stoploss_value=input.float(defval=1, title='Long SL %', minval=0.1, inline='2'),
    long_takeprofit_value=input.float(defval=1.5, title='Long TP %', minval=0.1, inline='2'),
    enable_short_strategy=input.bool(True, title='Enable Short Strategy', inline='3'),
    short_stoploss_value=input.float(defval=1, title='Short SL %', minval=0.1, inline='4'),
    short_takeprofit_value=input.float(defval=1.5, title='Short TP %', minval=0.1, inline='4'),
    period=input.int(20, 'Length', group='SMart Money Concept'),
    enable_strategy_2=input.bool(defval=False, title='Enable MA Trend', group='MA Trend'),
    maSourceInput: Series[float] = input.source(close, 'Source', group='MA Trend'),
    maTypeInput=input.string('SMA', title='MA Type', options=('SMA', 'HMA', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA'), group='MA Trend', display=display.all),
    maLengthInput=input.int(200, title='MA Length', group='MA Trend', display=display.all)
):
    long_stoploss_percentage = close * (long_stoploss_value / 100) / syminfo.mintick
    long_takeprofit_percentage = close * (long_takeprofit_value / 100) / syminfo.mintick
    short_stoploss_percentage = close * (short_stoploss_value / 100) / syminfo.mintick
    short_takeprofit_percentage = close * (short_takeprofit_value / 100) / syminfo.mintick
    long_stoploss_price = strategy.position_avg_price * (1 - long_stoploss_value / 100)
    long_takeprofit_price = strategy.position_avg_price * (1 + long_takeprofit_value / 100)
    short_stoploss_price = strategy.position_avg_price * (1 + short_stoploss_value / 100)
    short_takeprofit_price = strategy.position_avg_price * (1 - short_takeprofit_value / 100)

    GREEN: Color = color.rgb(2, 133, 69)
    TAIL: Color = color.rgb(20, 141, 154)
    RED: Color = color.rgb(246, 7, 7)
    _Green: Color = color.rgb(2, 106, 89)
    OFF: Color = color.new(color.red, 100)
    UpdatedHigh: Persistent[float] = na(float)
    UpdatedLow: Persistent[float] = na(float)
    HighIndex: Persistent[int] = na(int)
    phActive: Persistent[bool] = False
    plActive: Persistent[bool] = False
    LowIndex: Persistent[int] = na(int)
    HBreak: Persistent[bool] = False
    LAB: Persistent[Label] = na(Label)
    Sync: int = bar_index
    BUY: bool = False
    SELL: bool = False
    Volume: Vol = Vol(array.new_float(), array.new_float(), array.new_float(), array.new_float())
    CandleType: bool = 'Wicks' == 'Wicks'
    Linestyle: str = 'Dotted'
    Bull: Color = color.white
    Bear: Color = color.white
    __block_result__ = na
    __switch__ = Linestyle
    if __switch__ == 'Dashed':
        __block_result__ = line.style_dashed
    elif __switch__ == 'Dotted':
        __block_result__ = line.style_dotted
    else:
        __block_result__ = line.style_solid
    StyleSwitch = __block_result__
    @method
    def volAdj(len: int):
        return inline_series(math.min(ta.atr(len) * 0.3, close * (0.3 / 100)), 20) / 2

    Adj = volAdj(30)
    def VolCal(Index, Sync):
        Bars = math.abs(Index - Sync)
        for i in pine_range(0, Bars - 1, 1):
            array.push(Volume.SCR, close[i])
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(array.size(Volume.SCR) - 1):
            i = __loop_0__.value
            if array.get(Volume.SCR, i) > open[i]:
                array.push(Volume.Green, volume[i])
            if array.get(Volume.SCR, i) < open[i]:
                array.push(Volume.Red, volume[i])
            array.push(Volume.Total, volume[i])
        GreenRatio = math.round(array.sum(Volume.Green) / array.sum(Volume.Total) * 100, 2)
        RedRatio = math.round(array.sum(Volume.Red) / array.sum(Volume.Total) * 100, 2)
        Out = ' ' if GreenRatio > 55 else ' ' if RedRatio > 55 else ' '
        return Out

    PH = ta.pivothigh(high, period, period)
    PL = ta.pivotlow(low, period, period)
    ScrHigh = high if CandleType else close
    ScrLow = low if CandleType else close
    if ta.change(fixnan(PH)) != 0:
        UpdatedHigh = PH
        phActive = True
        HighIndex = Sync - period
    if ta.change(fixnan(PL)) != 0:
        UpdatedLow = PL
        plActive = True
        LowIndex = Sync - period
    if ScrHigh > UpdatedHigh and phActive:
        BUY = True
        phActive = False
    if ScrLow < UpdatedLow and plActive:
        SELL = True
        plActive = False
    if BUY:
        sign = VolCal(HighIndex, Sync)
        line.new(HighIndex, UpdatedHigh, Sync, UpdatedHigh, color=Bull, style=StyleSwitch, width=1)
        label.new(math.floor(Sync - (Sync - HighIndex) / 2), UpdatedHigh, ' ' + sign if not HBreak else ' ' + sign, color=OFF, textcolor=color.white, size=size.tiny)
        label.new(Sync, low, '', yloc=yloc.belowbar, color=color.lime, size=size.small, style=label.style_triangleup)
        HBreak = True
    if SELL:
        sign = VolCal(LowIndex, Sync)
        line.new(LowIndex, UpdatedLow, Sync, UpdatedLow, color=Bear, style=StyleSwitch, width=1)
        label.new(math.floor(Sync - (Sync - LowIndex) / 2), UpdatedLow, ' ' + sign if HBreak else ' ' + sign, color=OFF, textcolor=color.white, style=label.style_label_up, size=size.tiny)
        label.new(Sync, low, '', yloc=yloc.abovebar, color=RED, size=size.small, style=label.style_triangledown)
        HBreak = False
    LongSMB = BUY
    ShortSMB = SELL
    def ma(source, length, type):
        __block_result_1__ = na
        __switch__ = type
        if __switch__ == 'SMA':
            __block_result_1__ = ta.sma(source, length)
        elif __switch__ == 'HMA':
            __block_result_1__ = ta.hma(source, length)
        elif __switch__ == 'EMA':
            __block_result_1__ = ta.ema(source, length)
        elif __switch__ == 'SMMA (RMA)':
            __block_result_1__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result_1__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result_1__ = ta.vwma(source, length)
        return __block_result_1__

    MAT = ma(maSourceInput, maLengthInput, maTypeInput)
    plot(MAT, 'MA', color=color.yellow)
    long_MA = close > MAT if enable_strategy_2 else True
    short_MA = close < MAT if enable_strategy_2 else True
    longCondition_2 = long_MA
    shortCondition_2 = short_MA
    co2: Persistent[int] = 0
    if longCondition_2:
        co2 = 1
    if shortCondition_2:
        co2 = -1
    long_2 = co2 == 1 if enable_strategy_2 else True
    short_2 = co2 == -1 if enable_strategy_2 else True
    longCondition = strategy.position_size <= 1 and long_2
    shortCondition = strategy.position_size >= -1 and short_2
    if LongSMB and longCondition and enable_long_strategy and ((strategy.position_size <= 1) == True):
        strategy.entry('Long', strategy.long, alert_message='Long Entry')
        strategy.exit('Long', from_entry='Long', loss=long_stoploss_percentage, profit=long_takeprofit_percentage, alert_loss='Long SL', alert_profit='Long TP', comment_loss='Long SL', comment_profit='Long TP')
    if ShortSMB and shortCondition and enable_short_strategy and ((strategy.position_size >= -1) == True):
        strategy.entry('Short', strategy.short, alert_message='Short Entry')
        strategy.exit('Short', from_entry='Short', loss=short_stoploss_percentage, profit=short_takeprofit_percentage, alert_loss='Short SL', alert_profit='Short TP', comment_loss='Short SL', comment_profit='Short TP')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
