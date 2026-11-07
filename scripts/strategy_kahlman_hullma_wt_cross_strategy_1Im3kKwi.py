"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, fill, fixnan, high, hl2, hlc3, hlcc4, input, low, math, na,
    nz, ohlc4, open, plot, script, strategy, ta, time, timeframe, timestamp, volume
)
from pynecore.types import Persistent, Series

tp2L: str = 'tp2L'
tp3L: str = 'tp3L'
tp2S: str = 'tp2S'
tp3S: str = 'tp3S'
wunder: str = 'Wunderbit Comments'
rangeL: str = 'LONG'
rangeS: str = 'SHORT'


@script.strategy('Kahlman HullMA / WT Cross Strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100, margin_long=0, margin_short=0, close_by_id=True)
def main(
    _1=input(False, '|| LONG TP SETTINGS ||'),
    long=input(True, 'Long On'),
    LongprofitPercent=input.float(10, 'TP1 Profit Percent', minval=0, maxval=100, step=5, tooltip='Percentage of balance to be taken for take profit 1-2.'),
    LongprofitPercent2=input.float(15, 'TP2 Profit Percent', minval=0, maxval=100, step=5, tooltip='Percentage of balance to be taken for take profit 1-2.'),
    __input_4__=input.float(8.9, 'Long Take Profit 1', minval=0.1, step=0.1, tooltip='Long take profit 1 percent setting'),
    __input_5__=input.float(13.6, 'Long Take Profit 2', minval=0.1, step=0.1, tooltip='Long take profit 2 percent setting. / Close TP2', inline=tp2L),
    tp2OnOffL=input(True, 'On', inline=tp2L),
    __input_7__=input.float(13.6, 'Long Take Profit 3', minval=0.1, step=0.1, tooltip='Long take profit 3 percent setting. / Close TP3', inline=tp3L),
    tp3OnOffL=input(False, 'On', inline=tp3L),
    src_long=input.string(title='Long TP1 Source', defval='hc2', options=('hc2', 'co2', 'hco3', 'hlo3', 'ho2', 'lo2', 'open', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high'), tooltip='TP1 up or down control. Close process if selected \'source\' is less than TP1'),
    src_long2=input.string(title='Long TP2 Source', defval='hc2', options=('hc2', 'co2', 'hco3', 'hlo3', 'ho2', 'lo2', 'open', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high'), tooltip='TP2 up or down control. Close process if selected \'source\' is less than TP2'),
    _2=input(False, '|| SHORT TP SETTINGS ||'),
    short=input(True, 'Short On'),
    ShortprofitPercent=input.float(50, 'TP1 Profit Percent', minval=0, maxval=100, step=5, tooltip='Percentage of balance to be taken for take profit 1-2.'),
    ShortprofitPercent2=input.float(70, 'TP2 Profit Percent', minval=0, maxval=100, step=5, tooltip='Percentage of balance to be taken for take profit 1-2.'),
    __input_15__=input.float(8.2, 'Short Take Profit 1', minval=0.1, step=0.1, tooltip='Short take profit 1 percent setting'),
    __input_16__=input.float(13.4, 'Short Take Profit 2', minval=0.1, step=0.1, tooltip='Short take profit 2 percent setting. / Close TP3', inline=tp2S),
    tp2OnOffS=input(True, 'On', inline=tp2S),
    __input_18__=input.float(13.9, 'Short Take Profit 3', minval=0.1, step=0.1, tooltip='Short take profit 3 percent setting. / Close TP3', inline=tp3S),
    tp3OnOffS=input(False, 'On', inline=tp3S),
    src_short=input.string(title='Short TP1 Source', defval='lc2', options=('lc2', 'lco3', 'hco3', 'hc2', 'co2', 'hlo3', 'lo2', 'ho2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open'), tooltip='TP1 up or down control. Close process if selected \'source\' is greater than TP1'),
    src_short2=input.string(title='Short TP2 Source', defval='lco3', options=('lc2', 'lco3', 'hco3', 'hc2', 'co2', 'hlo3', 'lo2', 'ho2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open'), tooltip='TP2 up or down control. Close process if selected \'source\' is greater than TP2'),
    _3=input(False, '|| STOP LOSS SETTINGS ||'),
    __input_23__=input.float(7.1, 'Long', minval=0.1, step=0.1, tooltip='Stop loss percent(Red line)'),
    __input_24__=input.float(7.9, 'Short', minval=0.1, step=0.1),
    _4=input(False, '|| TRAILING STOP SETTINGS ||'),
    trailingSLOnOff=input(True, 'Long Trailing SL On', tooltip='Trailing stop loss mode.'),
    trailingStopChangeL=input(True, 'Change Line', tooltip='On: If price is greater than TP1. Off: If price is greater than Long Position Check.'),
    __input_28__=input.float(3.6, 'Long', minval=0.1, step=0.1, tooltip='Trailing stop loss percent. Note: Activated if greater than TP1. Otherwise, the stop level is the value on a bottom line.(Yellow dot line)'),
    trailingSLOnOff2=input(False, 'Short Trailing SL On', tooltip='Trailing stop loss mode.'),
    trailingStopChangeS=input(True, 'Change Line', tooltip='On: If price is greater than TP1. Off: If price is greater than Short Position Check.'),
    __input_31__=input.float(3.4, 'Short', minval=0.1, step=0.1, tooltip='Trailing stop loss percent. Note: Activated if greater than TP1. Otherwise, the stop level is the value on a bottom line.(Yellow dot line)'),
    _5=input(False, '|| POSITION CHECK SETTINGS ||'),
    LongpositionCheckOnOff=input(True, 'Long Position Check On', tooltip='Long Position check mode. Depends on TP1 percentage. It works as a \'%X\' / \'Senstive Value\'.'),
    src_LongpositionCheck=input.string(title='Source', defval='co2', options=('hco3', 'lco3', 'hc2', 'lc2', 'co2', 'ho2', 'lo2', 'hlo3', 'close', 'open', 'hl2', 'hlc3', 'ohlc4', 'hlcc4', 'low', 'high'), tooltip='Long check senstive up or down control. Close process if selected \'source\' is less than Position Check Line(Yellow solid line)'),
    LongpositionCheck=input.float(1.7, 'Senstive', minval=1, step=0.01),
    ShortpositionCheckOnOff=input(True, 'Short Position Check On', tooltip='Short Position check mode. It works as a \'%X\' / \'Senstive Value\'.'),
    src_ShortpositionCheck=input.string(title='Source', defval='low', options=('lco3', 'hco3', 'lc2', 'hc2', 'co2', 'lo2', 'ho2', 'hlo3', 'close', 'open', 'hl2', 'hlc3', 'ohlc4', 'hlcc4', 'low', 'high'), tooltip='Short check senstive up or down control. Close process if selected \'source\' is greater than Position Check Line(Yellow solid line)'),
    ShortpositionCheck=input.float(1.4, 'Senstive', minval=1, step=0.01),
    _6=input(False, '|| WT CROSS SETTINGS ||'),
    n1L=input(6, 'Channel Length'),
    n2L=input(23, 'Average Length'),
    apL=input.string(title='Source', defval='hlc3', options=('hc2', 'hco3', 'lc2', 'lco3', 'co2', 'hlo3', 'lo2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open')),
    n1S=input(8, 'Channel Length'),
    n2S=input(19, 'Average Length'),
    apS=input.string(title='Source', defval='hlc3', options=('hc2', 'hco3', 'lc2', 'lco3', 'co2', 'hlo3', 'lo2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open')),
    _7=input(False, '|| HULLMA SETTINGS ||'),
    hull_source=input.string(title='Source', defval='hl2', options=('hc2', 'hco3', 'lc2', 'lco3', 'co2', 'hlo3', 'lo2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open')),
    lengthhull=input(24, 'Lookback'),
    gain=input(10000, 'Gain'),
    _8=input(False, '|| STOCH RSI SETTINGS ||'),
    rsistochOnOff=input(True, 'Stoch RSI', tooltip='Stoch RSI On/Off'),
    smoothK=input.int(2, 'K', minval=1),
    smoothD=input.int(3, 'D', minval=1),
    lengthRSI=input.int(13, 'RSI Length', minval=1),
    lengthStoch=input.int(13, 'Stochastic Length', minval=1),
    src=input.string(title='RSI Source', defval='hl2', options=('hc2', 'hco3', 'lc2', 'lco3', 'co2', 'hlo3', 'lo2', 'close', 'hlc3', 'hl2', 'ohlc4', 'hlcc4', 'low', 'high', 'open')),
    _15=input(False, '|| VOLUME SETTINGS ||'),
    volumeonoff=input(True, 'On/Off'),
    volume_f=input.float(0.6, title='Mult.', minval=0, step=0.1),
    sma_length=input.int(3, title='Sma volume lenght', minval=1),
    vwma_length=input.int(3, title='Vwma volume lenght', minval=1),
    wma_length=input.int(4, title='Wma volume lenght', minval=1),
    _16=input(False, '|| ADX SETTINGS ||'),
    adxon=input(False, 'On'),
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Length'),
    adxBuyLevel=input(20, title='Buy Level'),
    _9=input(False, '|| WUNDERBIT SETTINGS ||'),
    longentryComment=input('ENTER-LONG', title='Long Entry Comment', group=wunder),
    longexitComment=input('EXIT-LONG', title='Long Exit Comment', group=wunder),
    shortentryComment=input('ENTER-SHORT', title='Short Entry Comment', group=wunder),
    shortexitComment=input('EXIT-SHORT', title='Short Exit Comment', group=wunder),
    _10=input(False, '|| DATE & DATE RANGE SETTINGS ||'),
    startDate=input.time(timestamp('1 Jan 2020 00:00 +0000'), 'Start Date'),
    endDate=input.time(timestamp('1 Jan 9999 03:00 +0000'), 'End Date'),
    sessionOnOff=input(True, 'Long/Time Range & Weekdays On/Off', tooltip='Start Date and End Date not inclueded', group=rangeL),
    timeSession=input.session('0000-0000', 'Time Range', group=rangeL),
    d_monday=input.bool(title='Monday', defval=True, inline='D1', group=rangeL),
    d_tuesday=input.bool(title='Tuesday', defval=True, inline='D1', group=rangeL),
    d_wednesday=input.bool(title='Wednesday', defval=True, inline='D1', group=rangeL),
    d_thursday=input.bool(title='Thursday', defval=True, inline='D2', group=rangeL),
    d_friday=input.bool(title='Friday', defval=True, inline='D2', group=rangeL),
    d_saturday=input.bool(title='Saturday', defval=False, inline='D2', group=rangeL),
    d_sunday=input.bool(title='Sunday', defval=True, tooltip='Trade days?', inline='D2', group=rangeL),
    sessionOnOff2=input(False, 'Short/Time Range & Weekdays On/Off', tooltip='Start Date and End Date not inclueded', group=rangeS),
    timeSession2=input.session('0300-0300', 'Time Range', group=rangeS),
    d_monday2=input.bool(title='Monday', defval=True, inline='D3', group=rangeS),
    d_tuesday2=input.bool(title='Tuesday', defval=True, inline='D3', group=rangeS),
    d_wednesday2=input.bool(title='Wednesday', defval=True, inline='D3', group=rangeS),
    d_thursday2=input.bool(title='Thursday', defval=True, inline='D4', group=rangeS),
    d_friday2=input.bool(title='Friday', defval=True, inline='D4', group=rangeS),
    d_saturday2=input.bool(title='Saturday', defval=True, inline='D4', group=rangeS),
    d_sunday2=input.bool(title='Sunday', defval=True, tooltip='Trade days?', inline='D4', group=rangeS)
):
    takeprofitLong = __input_4__ / 100
    takeprofit2Long = __input_5__ / 100
    takeprofit3Long = __input_7__ / 100
    takeprofitShort = __input_15__ / 100
    takeprofit2Short = __input_16__ / 100
    takeprofit3Short = __input_18__ / 100
    stoplossLong = __input_23__ / 100
    stoplossShort = __input_24__ / 100
    trailingPercent = __input_28__ / 100
    trailingPercent2 = __input_31__ / 100
    __block_result__ = na
    __switch__ = src_long
    if __switch__ == 'hc2':
        __block_result__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result__ = (high + close + open) / 3
    elif __switch__ == 'co2':
        __block_result__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result__ = (open + high + low) / 3
    elif __switch__ == 'ho2':
        __block_result__ = (open + high) / 2
    elif __switch__ == 'lo2':
        __block_result__ = (low + open) / 2
    elif __switch__ == 'lc2':
        __block_result__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result__ = (low + close + open) / 3
    elif __switch__ == 'open':
        __block_result__ = open
    elif __switch__ == 'close':
        __block_result__ = close
    elif __switch__ == 'hlc3':
        __block_result__ = hlc3
    elif __switch__ == 'hl2':
        __block_result__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result__ = hlcc4
    elif __switch__ == 'low':
        __block_result__ = low
    elif __switch__ == 'high':
        __block_result__ = high
    source_long: float = __block_result__
    __block_result_1__ = na
    __switch__ = src_long2
    if __switch__ == 'hc2':
        __block_result_1__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_1__ = (high + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_1__ = (open + close) / 2
    elif __switch__ == 'lc2':
        __block_result_1__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_1__ = (low + close + open) / 3
    elif __switch__ == 'hlo3':
        __block_result_1__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_1__ = (open + low) / 2
    elif __switch__ == 'ho2':
        __block_result_1__ = (high + open) / 2
    elif __switch__ == 'open':
        __block_result_1__ = open
    elif __switch__ == 'close':
        __block_result_1__ = close
    elif __switch__ == 'hlc3':
        __block_result_1__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_1__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_1__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_1__ = hlcc4
    elif __switch__ == 'low':
        __block_result_1__ = low
    elif __switch__ == 'high':
        __block_result_1__ = high
    source_long2: float = __block_result_1__
    __block_result_2__ = na
    __switch__ = src_short
    if __switch__ == 'lc2':
        __block_result_2__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_2__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_2__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_2__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_2__ = (open + low) / 2
    elif __switch__ == 'ho2':
        __block_result_2__ = (high + open) / 2
    elif __switch__ == 'hc2':
        __block_result_2__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_2__ = (high + close + open) / 3
    elif __switch__ == 'close':
        __block_result_2__ = close
    elif __switch__ == 'hlc3':
        __block_result_2__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_2__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_2__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_2__ = hlcc4
    elif __switch__ == 'low':
        __block_result_2__ = low
    elif __switch__ == 'high':
        __block_result_2__ = high
    elif __switch__ == 'open':
        __block_result_2__ = open
    source_short: float = __block_result_2__
    __block_result_3__ = na
    __switch__ = src_short2
    if __switch__ == 'lc2':
        __block_result_3__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_3__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_3__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_3__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_3__ = (open + low) / 2
    elif __switch__ == 'ho2':
        __block_result_3__ = (high + open) / 2
    elif __switch__ == 'hc2':
        __block_result_3__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_3__ = (high + close + open) / 3
    elif __switch__ == 'close':
        __block_result_3__ = close
    elif __switch__ == 'hlc3':
        __block_result_3__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_3__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_3__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_3__ = hlcc4
    elif __switch__ == 'low':
        __block_result_3__ = low
    elif __switch__ == 'high':
        __block_result_3__ = high
    elif __switch__ == 'open':
        __block_result_3__ = open
    source_short2: float = __block_result_3__
    __block_result_4__ = na
    __switch__ = src_LongpositionCheck
    if __switch__ == 'hco3':
        __block_result_4__ = (high + close + open) / 3
    elif __switch__ == 'lco3':
        __block_result_4__ = (low + close + open) / 3
    elif __switch__ == 'hc2':
        __block_result_4__ = (high + close) / 2
    elif __switch__ == 'lc2':
        __block_result_4__ = (low + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_4__ = (open + high + low) / 3
    elif __switch__ == 'co2':
        __block_result_4__ = (open + close) / 2
    elif __switch__ == 'ho2':
        __block_result_4__ = (open + high) / 2
    elif __switch__ == 'lo2':
        __block_result_4__ = (low + open) / 2
    elif __switch__ == 'close':
        __block_result_4__ = close
    elif __switch__ == 'hl2':
        __block_result_4__ = hl2
    elif __switch__ == 'hlc3':
        __block_result_4__ = hlc3
    elif __switch__ == 'ohlc4':
        __block_result_4__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_4__ = hlcc4
    elif __switch__ == 'low':
        __block_result_4__ = low
    elif __switch__ == 'high':
        __block_result_4__ = high
    elif __switch__ == 'open':
        __block_result_4__ = open
    source_CheckLong: float = __block_result_4__
    __block_result_5__ = na
    __switch__ = src_ShortpositionCheck
    if __switch__ == 'lco3':
        __block_result_5__ = (low + close + open) / 3
    elif __switch__ == 'hco3':
        __block_result_5__ = (high + close + open) / 3
    elif __switch__ == 'lc2':
        __block_result_5__ = (low + close) / 2
    elif __switch__ == 'hc2':
        __block_result_5__ = (high + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_5__ = (open + high + low) / 3
    elif __switch__ == 'co2':
        __block_result_5__ = (open + close) / 2
    elif __switch__ == 'lo2':
        __block_result_5__ = (open + low) / 2
    elif __switch__ == 'ho2':
        __block_result_5__ = (high + open) / 2
    elif __switch__ == 'close':
        __block_result_5__ = close
    elif __switch__ == 'hl2':
        __block_result_5__ = hl2
    elif __switch__ == 'hlc3':
        __block_result_5__ = hlc3
    elif __switch__ == 'ohlc4':
        __block_result_5__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_5__ = hlcc4
    elif __switch__ == 'high':
        __block_result_5__ = high
    elif __switch__ == 'open':
        __block_result_5__ = open
    elif __switch__ == 'low':
        __block_result_5__ = low
    source_CheckShort: float = __block_result_5__
    wtlong: Persistent[str] = 'WT LONG'
    __block_result_6__ = na
    __switch__ = apL
    if __switch__ == 'hc2':
        __block_result_6__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_6__ = (high + close + open) / 3
    elif __switch__ == 'lc2':
        __block_result_6__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_6__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_6__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_6__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_6__ = (open + low) / 2
    elif __switch__ == 'close':
        __block_result_6__ = close
    elif __switch__ == 'hlc3':
        __block_result_6__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_6__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_6__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_6__ = hlcc4
    elif __switch__ == 'low':
        __block_result_6__ = low
    elif __switch__ == 'high':
        __block_result_6__ = high
    elif __switch__ == 'open':
        __block_result_6__ = open
    apL_src: float = __block_result_6__
    esaL = ta.ema(apL_src, n1L)
    rL = ta.ema(math.abs(apL_src - esaL), n1L)
    ciL = (apL_src - esaL) / (0.015 * rL)
    tciL = ta.ema(ciL, n2L)
    wt1L: Series = tciL
    wt2L: Series = ta.sma(wt1L, 4)
    wtshort: Persistent[str] = 'WT SHORT'
    __block_result_7__ = na
    __switch__ = apS
    if __switch__ == 'hc2':
        __block_result_7__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_7__ = (high + close + open) / 3
    elif __switch__ == 'lc2':
        __block_result_7__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_7__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_7__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_7__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_7__ = (open + low) / 2
    elif __switch__ == 'close':
        __block_result_7__ = close
    elif __switch__ == 'hlc3':
        __block_result_7__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_7__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_7__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_7__ = hlcc4
    elif __switch__ == 'low':
        __block_result_7__ = low
    elif __switch__ == 'high':
        __block_result_7__ = high
    elif __switch__ == 'open':
        __block_result_7__ = open
    apS_src: float = __block_result_7__
    esaS = ta.ema(apS_src, n1S)
    rS = ta.ema(math.abs(apS_src - esaS), n1S)
    ciS = (apS_src - esaS) / (0.015 * rS)
    tciS = ta.ema(ciS, n2S)
    wt1S = tciS
    wt2S = ta.sma(wt1S, 4)
    __block_result_8__ = na
    __switch__ = hull_source
    if __switch__ == 'hc2':
        __block_result_8__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_8__ = (high + close + open) / 3
    elif __switch__ == 'lc2':
        __block_result_8__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_8__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_8__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_8__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_8__ = (open + low) / 2
    elif __switch__ == 'close':
        __block_result_8__ = close
    elif __switch__ == 'hlc3':
        __block_result_8__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_8__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_8__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_8__ = hlcc4
    elif __switch__ == 'low':
        __block_result_8__ = low
    elif __switch__ == 'high':
        __block_result_8__ = high
    elif __switch__ == 'open':
        __block_result_8__ = open
    hull_src: float = __block_result_8__
    def hma(_hull_src, _lengthhull):
        return ta.wma(2 * ta.wma(_hull_src, _lengthhull / 2) - ta.wma(_hull_src, _lengthhull), math.round(math.sqrt(_lengthhull)))

    def hma3(_hull_src, _lengthhull):
        p = lengthhull / 2
        return ta.wma(ta.wma(close, p / 3) * 3 - ta.wma(close, p / 2) - ta.wma(close, p), p)

    def kahlman(x, g):
        kf: Series[float] = 0.0
        dk = x - nz(kf[1], x)
        smooth = nz(kf[1], x) + dk * math.sqrt(g / 10000 * 2)
        velo: Series[float] = 0.0
        velo = nz(velo[1], 0) + g / 10000 * dk
        kf = smooth + velo
        return kf

    a: Series = kahlman(hma(hull_src, lengthhull), gain)
    b: Series = kahlman(hma3(hull_src, lengthhull), gain)
    c = color.lime if b > a else color.red
    crossdn = a > b and a[1] < b[1]
    crossup = b > a and b[1] < a[1]
    p1hma = plot(a, color=color.new(c, 75), linewidth=1, title='Long Plot')
    p2hma = plot(b, color=color.new(c, 75), linewidth=1, title='Short Plot')
    fill(p1hma, p2hma, color=color.new(c, 75), title='Fill')
    __block_result_9__ = na
    __switch__ = src
    if __switch__ == 'hc2':
        __block_result_9__ = (high + close) / 2
    elif __switch__ == 'hco3':
        __block_result_9__ = (high + close + open) / 3
    elif __switch__ == 'lc2':
        __block_result_9__ = (low + close) / 2
    elif __switch__ == 'lco3':
        __block_result_9__ = (low + close + open) / 3
    elif __switch__ == 'co2':
        __block_result_9__ = (open + close) / 2
    elif __switch__ == 'hlo3':
        __block_result_9__ = (open + high + low) / 3
    elif __switch__ == 'lo2':
        __block_result_9__ = (open + low) / 2
    elif __switch__ == 'close':
        __block_result_9__ = close
    elif __switch__ == 'hlc3':
        __block_result_9__ = hlc3
    elif __switch__ == 'hl2':
        __block_result_9__ = hl2
    elif __switch__ == 'ohlc4':
        __block_result_9__ = ohlc4
    elif __switch__ == 'hlcc4':
        __block_result_9__ = hlcc4
    elif __switch__ == 'low':
        __block_result_9__ = low
    elif __switch__ == 'high':
        __block_result_9__ = high
    elif __switch__ == 'open':
        __block_result_9__ = open
    src_src: float = __block_result_9__
    rsi1 = ta.rsi(src_src, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    LStoch = k > d if rsistochOnOff else cast_bool(close)
    SStoch = k < d if rsistochOnOff else cast_bool(close)
    vol = (ta.sma(volume, sma_length) + ta.vwma(volume, vwma_length) + ta.wma(volume, wma_length)) / 3 * volume_f
    volEntry = volume > vol if volumeonoff else cast_bool(volume)
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(plusDM, len) / truerange)
        minus = fixnan(100 * ta.rma(minusDM, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__00000121__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000121__

    sig = adx(dilen, adxlen)
    __block_result_10__ = na
    if adxon:
        __block_result_10__ = sig > adxBuyLevel
    else:
        __block_result_10__ = sig < 100
    ADXEntry = __block_result_10__
    days = '1' if d_sunday else ''
    days = days + ('2' if d_monday else '')
    days = days + ('3' if d_tuesday else '')
    days = days + ('4' if d_wednesday else '')
    days = days + ('5' if d_thursday else '')
    days = days + ('6' if d_friday else '')
    days = days + ('7' if d_saturday else '')
    strategyTime = True if time >= startDate and time <= endDate else False
    def inSession(session__ren__):
        __block_result_11__ = na
        if sessionOnOff:
            __block_result_11__ = na(time(timeframe.period, session__ren__ + ':' + days)) == False and strategyTime
        else:
            __block_result_11__ = strategyTime
        return __block_result_11__

    days2 = '1' if d_sunday2 else ''
    days2 = days2 + ('2' if d_monday2 else '')
    days2 = days2 + ('3' if d_tuesday2 else '')
    days2 = days2 + ('4' if d_wednesday2 else '')
    days2 = days2 + ('5' if d_thursday2 else '')
    days2 = days2 + ('6' if d_friday2 else '')
    days2 = days2 + ('7' if d_saturday2 else '')
    def inSession2(session2):
        __block_result_12__ = na
        if sessionOnOff2:
            __block_result_12__ = na(time(timeframe.period, session2 + ':' + days2)) == False and time >= startDate and (time <= endDate)
        else:
            __block_result_12__ = True if time >= startDate and time <= endDate else False
        return __block_result_12__

    longConditionDirection = strategy.position_size >= 0
    shortConditionDirection = strategy.position_size <= 0
    __block_result_13__ = na
    if longConditionDirection:
        __block_result_13__ = strategy.position_avg_price * (1 - stoplossLong)
    else:
        __block_result_13__ = strategy.position_avg_price * (1 + stoplossShort)
    exitSL = __block_result_13__
    __block_result_14__ = na
    if longConditionDirection:
        __block_result_14__ = strategy.position_avg_price * (1 + takeprofitLong)
    else:
        __block_result_14__ = strategy.position_avg_price * (1 - takeprofitShort)
    exitTP = __block_result_14__
    __block_result_15__ = na
    if longConditionDirection:
        __block_result_15__ = strategy.position_avg_price * (1 + takeprofit2Long)
    else:
        __block_result_15__ = strategy.position_avg_price * (1 - takeprofit2Short)
    exitTP2 = __block_result_15__
    __block_result_16__ = na
    if longConditionDirection:
        __block_result_16__ = strategy.position_avg_price * (1 + takeprofit3Long)
    else:
        __block_result_16__ = strategy.position_avg_price * (1 - takeprofit3Short)
    exitTP3 = __block_result_16__
    __block_result_17__ = na
    if LongpositionCheckOnOff:
        __block_result_17__ = strategy.position_avg_price * (1 + takeprofitLong / LongpositionCheck) if longConditionDirection else na
    positionCheckLong = __block_result_17__
    __block_result_18__ = na
    if ShortpositionCheckOnOff:
        __block_result_18__ = strategy.position_avg_price * (1 - takeprofitShort / ShortpositionCheck) if shortConditionDirection else na
    positionCheckShort = __block_result_18__
    crossover_1 = ta.crossover(wt1L, wt2L)
    crossover_2 = ta.crossover(wt1L[1], wt2L[1])
    crossover_3 = ta.crossover(wt1L[2], wt2L)
    longCondition = crossup and crossover_1 and LStoch or (crossup and crossover_2 and LStoch) or (crossup and crossover_3 and LStoch)
    crossunder_1 = ta.crossunder(wt1S, wt2S)
    shortCondition = crossdn and crossunder_1 and SStoch
    trailingStopChangeL1 = high >= exitTP or high[1] >= exitTP if trailingStopChangeL else high >= positionCheckLong or high[1] >= positionCheckLong
    priceStopL: Series[float] = 0.0
    __block_result_19__ = na
    if longConditionDirection and trailingStopChangeL1 and trailingSLOnOff:
        stopMeasure = close * (1 - trailingPercent)
        __block_result_19__ = math.max(stopMeasure, priceStopL[1])
    elif longConditionDirection:
        __block_result_19__ = exitSL
    priceStopL = __block_result_19__
    trailingStopChangeS1 = low <= exitTP or low[1] <= exitTP if trailingStopChangeS else low <= positionCheckShort or low[1] <= positionCheckShort
    priceStopS: Series[float] = 0.0
    __block_result_20__ = na
    if shortConditionDirection and trailingStopChangeS1 and trailingSLOnOff2:
        stopMeasure = close * (1 + trailingPercent2)
        __block_result_20__ = math.min(stopMeasure, priceStopS[1])
    elif shortConditionDirection:
        __block_result_20__ = exitSL
    priceStopS = __block_result_20__
    crossunder_2 = ta.crossunder(wt1L, wt2L)
    crossunder_3 = ta.crossunder(wt1S, wt2S)
    positionCheckLong2 = high >= positionCheckLong and crossunder_2 and (source_CheckLong < positionCheckLong) or (high >= positionCheckLong and crossunder_3 and (source_CheckLong < positionCheckLong)) or (high >= positionCheckLong and a > b and (source_CheckLong < positionCheckLong) and (wt1L < wt2L) and (not volEntry)) or (high >= positionCheckLong and a > b and (source_CheckLong < positionCheckLong) and (wt1S < wt2S) and (not volEntry)) or (high >= positionCheckLong and crossdn and (source_CheckLong < positionCheckLong))
    crossover_4 = ta.crossover(wt1S, wt2S)
    crossover_5 = ta.crossover(wt1L, wt2L)
    positionCheckShort2 = low <= positionCheckShort and crossover_4 and (source_CheckShort > positionCheckShort) or (low <= positionCheckShort and crossover_5 and (source_CheckShort > positionCheckShort)) or (low <= positionCheckShort and a < b and (source_CheckShort > positionCheckShort) and (wt1S > wt2S) and (not volEntry)) or (low <= positionCheckShort and a < b and (source_CheckShort > positionCheckShort) and (wt1L > wt2L) and (not volEntry)) or (low <= positionCheckShort and crossup and (source_CheckShort > positionCheckShort))
    longTStop = high >= exitTP and source_long <= exitTP or (high >= exitTP2 and source_long2 <= exitTP2) or (high >= exitTP2 and a > b)
    shortTStop = low <= exitTP and source_short >= exitTP or (low <= exitTP2 and source_short2 >= exitTP2) or (low <= exitTP2 and a < b)
    __block_result_21__ = na
    if high <= strategy.position_avg_price or high >= positionCheckLong:
        __block_result_21__ = shortCondition or positionCheckLong2
    longConditionExit = __block_result_21__
    __block_result_22__ = na
    if low >= strategy.position_avg_price or low <= positionCheckShort:
        __block_result_22__ = longCondition or positionCheckShort2
    shortConditionExit = __block_result_22__
    if strategyTime:
        if longConditionDirection and longCondition and long and volEntry and ADXEntry:
            if inSession(timeSession if sessionOnOff else na):
                strategy.entry('LONG', strategy.long, comment=longentryComment)
        strategy.exit('LONG', stop=priceStopL, qty_percent=LongprofitPercent if tp2OnOffL else 100, limit=exitTP, comment=longexitComment)
        if tp2OnOffL:
            strategy.exit('LONG1', stop=priceStopL, qty_percent=LongprofitPercent2 if tp3OnOffL else 100, limit=exitTP2, comment=longexitComment)
        if tp3OnOffL:
            strategy.exit('LONG2', stop=priceStopL, qty_percent=100, limit=exitTP3, comment=longexitComment)
        if longConditionExit or longTStop:
            strategy.close('LONG', comment=longexitComment)
        if shortConditionDirection and shortCondition and short and volEntry and ADXEntry:
            if inSession2(timeSession2 if sessionOnOff2 else na):
                strategy.entry('SHORT', strategy.short, comment=shortentryComment)
        strategy.exit('SHORT', stop=priceStopS, qty_percent=ShortprofitPercent if tp2OnOffS else 100, limit=exitTP, comment=shortexitComment)
        if tp2OnOffS:
            strategy.exit('SHORT1', stop=priceStopS, qty_percent=ShortprofitPercent2 if tp3OnOffS else 100, limit=exitTP2, comment=shortexitComment)
        if tp3OnOffS:
            strategy.exit('SHORT2', stop=priceStopS, qty_percent=100, limit=exitTP3, comment=shortexitComment)
        if shortConditionExit or shortTStop:
            strategy.close('SHORT', comment=shortexitComment)
    LSTP2Lines = (exitTP2 if tp2OnOffL else na) if longConditionDirection else (exitTP2 if tp2OnOffS else na) if shortConditionDirection else na
    LSTP3Lines = ((exitTP3 if tp2OnOffL else na) if tp3OnOffL else na) if longConditionDirection else ((exitTP3 if tp2OnOffS else na) if tp3OnOffS else na) if shortConditionDirection else na
    plot(exitTP, title='Long/Short TP1', color=color.lime, style=plot.style_linebr, linewidth=1)
    plot(LSTP2Lines, title='Long/Short TP2', color=color.lime, style=plot.style_linebr, linewidth=1)
    plot(LSTP3Lines, title='Long/Short TP3', color=color.lime, style=plot.style_linebr, linewidth=1)
    plot(exitSL, title='Long/Short SL', color=color.red, style=plot.style_linebr, linewidth=1)
    PositionCheckColors = color.yellow if LongpositionCheckOnOff and cast_bool(positionCheckLong) else color.yellow if ShortpositionCheckOnOff and cast_bool(positionCheckShort) else na
    PositionCheckLines = positionCheckLong if LongpositionCheckOnOff and longConditionDirection else positionCheckShort if ShortpositionCheckOnOff and shortConditionDirection else na
    plot(PositionCheckLines, title='Long/Short Position Check', color=PositionCheckColors, style=plot.style_linebr, linewidth=1)
    TrailingStopLines = (priceStopL if longConditionDirection and trailingStopChangeL1 else na) if trailingSLOnOff else na
    TrailingStopLines2 = (priceStopS if shortConditionDirection and trailingStopChangeS1 else na) if trailingSLOnOff2 else na
    plot(TrailingStopLines, title='Long Trailing Stop', color=color.yellow, style=plot.style_circles, linewidth=1)
    plot(TrailingStopLines2, title='Short Trailing Stop', color=color.yellow, style=plot.style_circles, linewidth=1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
