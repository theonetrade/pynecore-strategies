"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, barstate, bgcolor, close, color, fill, high, input, location, low,
    math, na, open, plot, plotchar, script, size, strategy, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series

g_trades: str = '     Trade Parameters'
g_volatility: str = '     Volatility Filters'
g_MABB: str = '     Moving Average & Bollinger Bands'
g_RSI: str = '     Relative Strength Index'
g_datetime: str = '     Date & Time Filters'
g_messages: str = '     Alert Messages'


@script.strategy('MA Bollinger Bands + RSI (Strategy)', shorttitle='MABB+RSI (Strat)', calc_on_order_fills=True, overlay=True, initial_capital=10000, default_qty_type=strategy.cash, default_qty_value=10000, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    longTradesON=input.bool(title='Long trades', defval=True, group=g_trades, inline='a', tooltip=''),
    shortTradesON=input.bool(title='Short trades', defval=True, group=g_trades, inline='a', tooltip='Switch on/off long and short trades'),
    useTP=input.bool(title='Use Take Profit', defval=False, group=g_trades, inline='', tooltip='Fixed Take Profit value'),
    useSL=input.bool(title='Use Stop Loss', defval=False, group=g_trades, inline='', tooltip='Fixed Stop Loss value'),
    useTSL=input.bool(title='Use Trailing Stop', defval=True, group=g_trades, inline='', tooltip='ATR Trailing Stop Loss value '),
    reEnterAfterSLTP=input.bool(title='Re-Entry after SL/TP', defval=True, group=g_trades, inline='', tooltip='Allows to re-enter trades in the same direction as previous trade if previous trade\'s stop loss or take profit was hit'),
    TSLlookback=input.int(title='Trailing lookback', defval=2, group=g_trades, inline='', tooltip='How many bars back will trailing stops look for a swing low (longs) or sing high (short) to get a starting point', minval=0, maxval=1000, step=1),
    atrMult=input.float(title='ATR Mult', defval=9.0, group=g_trades, inline='', tooltip='Increase/decrease to set stops and/or targets further/closer to trade entry price', minval=0.1),
    atrLen=input.int(title='ATR Length', defval=14, group=g_trades, inline='', tooltip='Average of the \'True Range\' over x past bars', minval=0),
    rr=input.float(title='Risk:Reward', defval=1, group=g_trades, inline='', tooltip='Multiplies the take profit distance by this number ', minval=0, maxval=100, step=0.1),
    UseVolHigh=input.bool(title='High Volatility', defval=True, group=g_volatility, inline='b', tooltip=''),
    UseVolLow=input.bool(title='Low Volatility', defval=True, group=g_volatility, inline='b', tooltip='Filters out trade signals during high volatility / low volatility or both.'),
    BBvolX=input.float(title='Volatility Factor', defval=5.0, group=g_volatility, inline='', tooltip='Lower this number to filter out more trades when volatility at extremes', maxval=10, minval=0.1, step=0.1),
    AddVol=input.bool(title='Volatility Visuals', defval=False, group=g_volatility, inline='', tooltip='Plots additionnal graphs on the chart to illustrate how extreme levels of volatility are defined (how Bollinger Bands are colored)'),
    MAtype=input.string(title='MA Type', defval='SMA', group=g_MABB, inline='c', tooltip='Type of moving average used for standard deviation', options=('SMA', 'EMA', 'WMA', 'VWMA', 'HMA')),
    MAlen=input.int(title='MA Length', defval=200, group=g_MABB, inline='c', tooltip='Moving average lookback'),
    BBX=input.float(title=' BB Mult', defval=2.0, group=g_MABB, inline='d', tooltip='Set upper & lower bands closer / appart', step=0.01, minval=0.001),
    BBlen=input.int(title='BB Length', defval=200, group=g_MABB, inline='d', tooltip='Bollinger bands, standard deviation lookback'),
    RSINlen=input.int(title='RSI Cross Loockback ', defval=10, group=g_RSI, tooltip='How many bars back (from price crossing-over lower bound or crossing-under upper bound) to look for corresponding RSI neutral crossover/under', minval=0, maxval=1000),
    RSIN=input.int(title='RSI Neutral', defval=50, group=g_RSI, tooltip='Defines the value at wich RSI neutral crossover or crossunder occurs'),
    RSIlen=input.int(title='RSI Length', defval=6, group=g_RSI, tooltip='Relative Strenght Index lookback'),
    UseDateFilter=input.bool(title='Enable Date Filter', defval=False, group=g_datetime, tooltip='Turns on/off date filter'),
    StartDate=input.time(title='Start Date Filter', defval=timestamp('1 Jan 2022 00:00 +0000'), group=g_datetime, tooltip='Date & time to start excluding trades'),
    EndDate=input.time(title='End Date Filter', defval=timestamp('1 Jan 2023 00:00 +0000'), group=g_datetime, tooltip='Date & time to stop excluding trades'),
    UseTimeFilter=input.bool(title='Enable Session Filter', defval=False, group=g_datetime, tooltip='Turns on/off time session filter'),
    TradingSession=input.session(title='Trading Session', defval='1000-2200:1234567', group=g_datetime, tooltip='No trades will be taken outside of this range'),
    openLongAlertMessage=input.string(title='Open Long', defval='', group=g_messages, inline='e', tooltip='If you use 3 Commas, Paste \'\'Message for deal start signal\'\' (in Open Long) & \'\'Message to close order at Market Price\'\' (in Close Long) from your 3Commas long bot. \n\nOtherwise, you can dynamically change the alert text you wrote here by using Pinescript {{placeholders}} (Google: \'\'variables in alerts tradingview\'\' for more details)'),
    closeLongAlertMessage=input.string(title='Close Long', defval='', group=g_messages, inline='e', tooltip=''),
    openShortAlertMessage=input.string(title='Open Short', defval='', group=g_messages, inline='f', tooltip='If you use 3 Commas, Paste \'\'Message for deal start signal\'\' (in Open Short) & \'\'Message to close order at Market Price\'\' (in Close Short) from your 3Commas short bot. \n\nOtherwise, you can dynamically change the alert text you wrote here by using Pinescript {{placeholders}} (Google: \'\'variables in alerts tradingview\'\' for more details)'),
    closeShortAlertMessage=input.string(title='Close Short', defval='', group=g_messages, inline='f', tooltip='')
):
    BBdev = ta.stdev(close, BBlen) * BBX
    MA = ta.sma(close, MAlen)
    if MAtype == 'HMA':
        MA = ta.hma(close, MAlen)
    if MAtype == 'WMA':
        MA = ta.wma(close, MAlen)
    if MAtype == 'EMA':
        MA = ta.ema(close, MAlen)
    if MAtype == 'VWMA':
        MA = ta.vwma(close, MAlen)
    BBupper = MA + BBdev
    BBlower = MA - BBdev
    BBbull = open < BBlower and close > BBlower
    BBbear = open > BBupper and close < BBupper
    RSI = ta.rsi(close, RSIlen)
    RSIcrossover: Series = ta.crossover(RSI, RSIN)
    RSIcrossunder: Series = ta.crossunder(RSI, RSIN)
    RSIbull: bool = False
    for i in pine_range(0, RSINlen, 1):
        if RSIcrossover[i] == True:
            RSIbull = True
    RSIbear: bool = False
    for i in pine_range(0, RSINlen, 1):
        if RSIcrossunder[i] == True:
            RSIbear = True
    BBvol: Series = BBupper - BBlower
    SignalLine = ta.sma(BBvol, 50)
    BaseLine = ta.sma(BBvol, 2000)
    HighVolLvl = BaseLine + BaseLine * BBvolX / 10
    LowVolLvl = BaseLine - BaseLine * BBvolX / 10
    volExtrmHigh: Persistent[bool] = False
    if BBvol > HighVolLvl and UseVolHigh:
        volExtrmHigh = True
    else:
        volExtrmHigh = False
    volExtrmLow: Persistent[bool] = False
    if BBvol < LowVolLvl and UseVolLow:
        volExtrmLow = True
    else:
        volExtrmLow = False
    def In(t):
        return na(time(timeframe.period, t)) == False

    In_1 = In(TradingSession)
    TimeFilter = UseTimeFilter and (not In_1) or not UseTimeFilter
    DateFilter = time >= StartDate and time <= EndDate
    In_2 = In(TradingSession)
    DateTime = (not DateFilter if UseDateFilter else True) and (In_2 if UseTimeFilter else True)
    validLong = BBbull and RSIbull and (not volExtrmHigh) and (not volExtrmLow) and DateTime and barstate.isconfirmed
    validShort = BBbear and RSIbear and (not volExtrmHigh) and (not volExtrmLow) and DateTime and barstate.isconfirmed
    lastsignalislong: PersistentSeries[bool] = False
    lastsignalisshort: PersistentSeries[bool] = False
    newTradeDirection: Persistent[bool] = False
    if validLong:
        lastsignalislong = True
        lastsignalisshort = False
    if validShort:
        lastsignalislong = False
        lastsignalisshort = True
    if lastsignalislong == True and lastsignalislong[1] == False or (lastsignalisshort == True and lastsignalisshort[1] == False):
        newTradeDirection = True
    else:
        newTradeDirection = False
    SPS: Series = strategy.position_size
    atr = ta.atr(atrLen)
    SLsaved: PersistentSeries[float] = 0.0
    TPsaved: PersistentSeries[float] = 0.0
    TSLsaved: PersistentSeries[float] = na(float)
    entryPrice: Persistent[float] = na(float)
    SLdist = atr * atrMult
    longSL = close - SLdist
    longSLDist = close - longSL
    longTP = close + longSLDist * rr
    shortSL = close + SLdist
    shortSLDist = shortSL - close
    shortTP = close - shortSLDist * rr
    if validLong and SPS[1] <= 0 or (validShort and SPS[1] >= 0) or ((validLong or validShort) and SPS[1] == 0 and reEnterAfterSLTP):
        SLsaved = longSL if validLong else shortSL if validShort else na
        TPsaved = longTP if validLong else shortTP if validShort else na
    longTrailStart = ta.lowest(low, TSLlookback) - atr * atrMult
    shortTrailStart = ta.highest(high, TSLlookback) + atr * atrMult
    if validLong and SPS[1] <= 0 or (validShort and SPS[1] >= 0) or ((validLong or validShort) and SPS[1] == 0 and reEnterAfterSLTP):
        TSLsaved = longTrailStart if validLong else shortTrailStart if validShort else na
        entryPrice = close
    if SPS > 0:
        TSLsaved = math.max(longTrailStart, TSLsaved, TSLsaved[1])
    if SPS < 0:
        TSLsaved = math.min(shortTrailStart, TSLsaved, TSLsaved[1])
    if SPS[1] != 0 and SPS == 0:
        TSLsaved = na
    longSLTPhit: Persistent[bool] = False
    if SPS[1] > 0 and ((high >= TPsaved[1] if useTP else False) or (low <= SLsaved[1] if useSL else False) or (low <= TSLsaved[1] if useTSL else False)):
        longSLTPhit = True
    else:
        longSLTPhit = False
    shortSLTPhit: Persistent[bool] = False
    if SPS[1] < 0 and ((low <= TPsaved[1] if useTP else False) or (high >= SLsaved[1] if useSL else False) or (high >= TSLsaved[1] if useTSL else False)):
        shortSLTPhit = True
    else:
        shortSLTPhit = False
    plotchar(validLong, title='Long Signal', char='⬆', location=location.belowbar, size=size.tiny, color=color.new(color.new('#3064FC'), 0))
    plotchar(validShort, title='Short Signal', char='⬇', location=location.abovebar, size=size.tiny, color=color.new(color.new('#FC1049'), 0))
    plot(TPsaved if useTP and SPS != 0 and (not newTradeDirection) else na, color=color.new(color.green, 0), style=plot.style_linebr)
    plot(SLsaved if useSL and SPS != 0 and (not newTradeDirection) else na, color=color.new(color.red, 0), style=plot.style_linebr)
    TSLcolor = color.red if SPS > 0 and entryPrice > TSLsaved else color.green if SPS > 0 and entryPrice < TSLsaved else color.red if SPS < 0 and entryPrice < TSLsaved else color.green if SPS < 0 and entryPrice > TSLsaved else na
    plot(TSLsaved if useTSL and SPS != 0 and (not newTradeDirection) else na, color=TSLcolor, style=plot.style_linebr)
    plot(MA, title='Moving Average', color=color.new(color.white, 50))
    PriceUpperLine = plot(BBupper, title='BBprice Upper', color=color.new(color.gray, transp=60))
    PriceLowerLine = plot(BBlower, title='BBprice Lower', color=color.new(color.gray, transp=60))
    fill(PriceUpperLine, PriceLowerLine, title='BBprice Fill', color=color.new(color.new('#FF1010'), 70) if volExtrmHigh and BBvol > BBvol[1] else color.new(color.new('#FF1010'), 75) if volExtrmHigh and BBvol < BBvol[1] else color.new(color.new('#10FF10'), 70) if volExtrmLow and BBvol < BBvol[1] else color.new(color.new('#10FF10'), 75) if volExtrmLow and BBvol > BBvol[1] else color.new(color.white, 90))
    plot(BBvol if (UseVolHigh or UseVolLow) and AddVol else na, title='BBvol', color=color.new(color.blue, 10))
    plot(SignalLine if (UseVolHigh or UseVolLow) and AddVol else na, title='Signal Line', color=color.new(color.fuchsia, 10))
    plot(BaseLine if (UseVolHigh or UseVolLow) and AddVol else na, title='Base Line', color=color.new(color.yellow, 10))
    VolUpperLine = plot(HighVolLvl if (UseVolHigh or UseVolLow) and AddVol else na, title='BBvol Upper', color=color.new(color.yellow, 70))
    VolLowerLine = plot(LowVolLvl if (UseVolHigh or UseVolLow) and AddVol else na, title='BBvol Lower', color=color.new(color.yellow, 70))
    fill(VolUpperLine, VolLowerLine, title='BBvol Fill', color=color.new(color.yellow, 98))
    bgcolor(color.rgb(255, 70, 70, 85) if DateFilter and UseDateFilter else na, title='Date Filter')
    bgcolor(color.rgb(255, 70, 70, 85) if TimeFilter and UseTimeFilter else na, title='Time Filter')
    if longTradesON and validLong and newTradeDirection or (longTradesON and validLong and (SPS[1] == 0) and reEnterAfterSLTP and (not (validLong and longSLTPhit))):
        strategy.entry(id='Long', direction=strategy.long)
        alert(openLongAlertMessage, alert.freq_once_per_bar_close)
    if SPS > 0:
        strategy.exit(id='Long exit', from_entry='Long', stop=SLsaved if useSL else TSLsaved if useTSL else BBupper if newTradeDirection else na, limit=TPsaved if useTP else na)
    if longSLTPhit or (shortTradesON and validShort and newTradeDirection):
        alert(closeLongAlertMessage, alert.freq_once_per_bar)
    if shortTradesON and validShort and newTradeDirection or (shortTradesON and validShort and (SPS[1] == 0) and reEnterAfterSLTP and (not (validShort and shortSLTPhit))):
        strategy.entry(id='Short', direction=strategy.short)
        alert(openShortAlertMessage, alert.freq_once_per_bar_close)
    if SPS < 0:
        strategy.exit(id='Short exit', from_entry='Short', stop=SLsaved if useSL else TSLsaved if useTSL else BBlower if newTradeDirection else na, limit=TPsaved if useTP else na)
    if shortSLTPhit or (longTradesON and validLong and newTradeDirection):
        alert(closeShortAlertMessage, alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
