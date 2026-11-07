"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, close, color, fill, high, input, location, low, math,
    na, plot, plotchar, request, script, size, strategy, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Top 40 High Low Strategy', overlay=True, pyramiding=0, initial_capital=5000, commission_type=strategy.commission.cash_per_contract, commission_value=0.09, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    startY=input(title='Start Year', defval=2011, group='Trading window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Trading window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Trading window'),
    finishY=input(title='Finish Year', defval=2050, group='Trading window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Trading window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Trading window'),
    isSPY=input.bool(defval=True, title='Options trading only', group='Trading Options'),
    SPY_option=input.int(defval=10, title='# of options per trade', group='Trading Options'),
    reinvest=input.bool(defval=False, title='Reinvest profit?', group='Trading Options'),
    trade_trailing=input.bool(defval=True, title='Trade Trailing SL after PT', group='Trading Options'),
    trade_earlyExit=input.bool(defval=True, title='Take Profit early based on Top 40 overbought/oversold', group='Trading Options'),
    trade_expiry=input.bool(defval=True, title='Trade same/1 day expiry, exits EOD Mon/Wed/Fri; exits 1/2 Tues/Thurs', group='Trading Options'),
    atrlen=input.int(14, minval=1, title='ATR period', group='ATR'),
    iPercent=input.float(130, minval=0, step=10, title='% ATR to use for SL / PT', group='ATR'),
    fast_length=input(title='Fast Length', defval=12, group='MACD'),
    slow_length=input(title='Slow Length', defval=26, group='MACD'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group='MACD'),
    sma_source=input.string(title='Oscillator MA Type', defval='SMA', options=('SMA', 'EMA'), group='MACD'),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA'), group='MACD'),
    clen=input.int(defval=48, minval=1, title='Linear Regression Period', group='Linear Regression'),
    slen=input.int(defval=5, minval=1, title='LR Slope Period', group='Linear Regression'),
    glen=input.int(defval=14, minval=1, title='LR Signal Period', group='Linear Regression'),
    LR_thres=input.float(18.8, minval=0, step=0.1, title='LR Threshold for Ranging vs Trending', group='Linear Regression'),
    smoothK=input.int(3, minval=1, title='Stoch K', group='Stochastic RSI'),
    smoothD=input.int(3, minval=1, title='Stoch D', group='Stochastic RSI'),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group='Stochastic RSI'),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group='Stochastic RSI'),
    timeFrame=input.timeframe(defval='5', title='Time Frame', group='High Low Index'),
    length=input.int(defval=15, title='Length', minval=1, group='High Low Index'),
    source=input.string(defval='High/Low', title='Source', options=('High/Low', 'Close'), group='High Low Index'),
    smoothLength=input.int(defval=10, title='Smoothing Length', minval=1, group='High Low Index'),
    emaLength=input.int(defval=9, title='EMA Length', minval=1, group='High Low Index'),
    symbol1=input.symbol(defval='AAPL', group='Symbols'),
    symbol2=input.symbol(defval='MSFT', group='Symbols'),
    symbol3=input.symbol(defval='AMZN', group='Symbols'),
    symbol4=input.symbol(defval='GOOG', group='Symbols'),
    symbol5=input.symbol(defval='FB', group='Symbols'),
    symbol6=input.symbol(defval='TSLA', group='Symbols'),
    symbol7=input.symbol(defval='NVDA', group='Symbols'),
    symbol8=input.symbol(defval='BRK.B', group='Symbols'),
    symbol9=input.symbol(defval='JPM', group='Symbols'),
    symbol10=input.symbol(defval='UNH', group='Symbols'),
    symbol11=input.symbol(defval='JNJ', group='Symbols'),
    symbol12=input.symbol(defval='HD', group='Symbols'),
    symbol13=input.symbol(defval='PG', group='Symbols'),
    symbol14=input.symbol(defval='V', group='Symbols'),
    symbol15=input.symbol(defval='PFE', group='Symbols'),
    symbol16=input.symbol(defval='BAC', group='Symbols'),
    symbol17=input.symbol(defval='MA', group='Symbols'),
    symbol18=input.symbol(defval='ADBE', group='Symbols'),
    symbol19=input.symbol(defval='DIS', group='Symbols'),
    symbol20=input.symbol(defval='NFLX', group='Symbols'),
    symbol21=input.symbol(defval='TMO', group='Symbols'),
    symbol22=input.symbol(defval='XOM', group='Symbols'),
    symbol23=input.symbol(defval='CRM', group='Symbols'),
    symbol24=input.symbol(defval='CSCO', group='Symbols'),
    symbol25=input.symbol(defval='COST', group='Symbols'),
    symbol26=input.symbol(defval='ABT', group='Symbols'),
    symbol27=input.symbol(defval='PEP', group='Symbols'),
    symbol28=input.symbol(defval='ABBV', group='Symbols'),
    symbol29=input.symbol(defval='KO', group='Symbols'),
    symbol30=input.symbol(defval='PYPL', group='Symbols'),
    symbol31=input.symbol(defval='CVX', group='Symbols'),
    symbol32=input.symbol(defval='CMCSA', group='Symbols'),
    symbol33=input.symbol(defval='LLY', group='Symbols'),
    symbol34=input.symbol(defval='QCOM', group='Symbols'),
    symbol35=input.symbol(defval='NKE', group='Symbols'),
    symbol36=input.symbol(defval='VZ', group='Symbols'),
    symbol37=input.symbol(defval='WMT', group='Symbols'),
    symbol38=input.symbol(defval='INTC', group='Symbols'),
    symbol39=input.symbol(defval='ACN', group='Symbols'),
    symbol40=input.symbol(defval='AVGO', group='Symbols'),
    RR=input.float(2.0, minval=1, step=0.1, title='Reward to Risk Ratio', group='Trading Options'),
    SL_offset=input.int(15, minval=-100, maxval=100, title='% Stop loss reduction(+ve)/increase(-ve)', group='Trading Options'),
    no_longat10=input.bool(True, title='No entry between 10:05 - 10:20 (Statistically bad trades)', group='Trading Options'),
    option_multiplier=input.float(0.007, title='Multiplier for trading options (adjust to approx. options P&L)', step=0.001, group='Trading Options')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    t1 = time(timeframe.period, '0930-1500:23456')
    t2 = time(timeframe.period, '0930-1600:23456')
    window = True if time >= timestart and time <= timefinish and cast_bool(t1) else False
    window2 = True if time >= timestart and time <= timefinish and cast_bool(t2) else False
    trailing_stop: bool = False
    TS: Series[int] = 0
    src = close
    percentage = iPercent * 0.01
    atr = ta.rma(ta.tr, atrlen)
    datrp = atr * percentage
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    hist: Series = macd - signal
    macd_bull = hist > hist[1]
    macd_bear = hist < hist[1]
    macd_cross = ta.cross(macd, signal)
    lrc: Series = ta.linreg(src, clen, 0)
    lrs = (lrc - lrc[1]) / 1
    slrs: Series = ta.ema(lrs, slen)
    alrs = ta.sma(slrs, glen)
    up_accel = lrs > alrs and lrs > 0
    down_accel = lrs < alrs and lrs < 0
    zero_accel = not up_accel and (not down_accel)
    LR_upTrend = slrs > 0
    LR_downTrend = slrs < 0
    LR_ranging = math.abs(slrs) * 100 <= LR_thres
    LR_trending: Series = math.abs(slrs) * 100 > LR_thres
    LR_bull = slrs > slrs[1]
    LR_bear = slrs < slrs[1]
    plotchar(not LR_trending[1] and LR_trending and LR_upTrend, char='⇗', color=color.green, location=location.belowbar, size=size.small)
    plotchar(not LR_trending[1] and LR_trending and LR_downTrend, char='⇘', color=color.red, location=location.abovebar, size=size.small)
    plotchar(LR_trending[1] and (not LR_trending), char='⇒', color=color.gray, location=location.abovebar, size=size.small)
    rsi: Series = ta.rsi(src, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi, rsi, rsi, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    stoch_long = k < 10
    stoch_short = k > 90
    stoch_bottom = k[2] >= k[1] and k > k[1]
    stoch_top = k[2] <= k[1] and k < k[1]
    rsi_bull = rsi > rsi[1]
    rsi_bear = rsi < rsi[1]
    HighsLows: list[int] = array.new_int(40, 0)
    def getHighLow(length):
        highest_ = inline_series(ta.highest(length), 1)
        lowest_ = inline_series(ta.lowest(length), 1)
        ret: int = 0
        if na(highest_):
            ret = 2
        else:
            h_: bool = (high if source == 'High/Low' else close) > highest_
            l_: bool = (low if source == 'High/Low' else close) < lowest_
            ret = 1 if h_ else -1 if l_ else 0
        return ret

    def getHLindexForTheSymbol(symbol, timeFrame, length, index):
        highlow = request.security(symbol, timeFrame, getHighLow(length))
        return array.set(HighsLows, index, 2 if na(highlow) else highlow)

    getHLindexForTheSymbol(symbol1, timeFrame, length, 0)
    getHLindexForTheSymbol(symbol2, timeFrame, length, 1)
    getHLindexForTheSymbol(symbol3, timeFrame, length, 2)
    getHLindexForTheSymbol(symbol4, timeFrame, length, 3)
    getHLindexForTheSymbol(symbol5, timeFrame, length, 4)
    getHLindexForTheSymbol(symbol6, timeFrame, length, 5)
    getHLindexForTheSymbol(symbol7, timeFrame, length, 6)
    getHLindexForTheSymbol(symbol8, timeFrame, length, 7)
    getHLindexForTheSymbol(symbol9, timeFrame, length, 8)
    getHLindexForTheSymbol(symbol10, timeFrame, length, 9)
    getHLindexForTheSymbol(symbol11, timeFrame, length, 10)
    getHLindexForTheSymbol(symbol12, timeFrame, length, 11)
    getHLindexForTheSymbol(symbol13, timeFrame, length, 12)
    getHLindexForTheSymbol(symbol14, timeFrame, length, 13)
    getHLindexForTheSymbol(symbol15, timeFrame, length, 14)
    getHLindexForTheSymbol(symbol16, timeFrame, length, 15)
    getHLindexForTheSymbol(symbol17, timeFrame, length, 16)
    getHLindexForTheSymbol(symbol18, timeFrame, length, 17)
    getHLindexForTheSymbol(symbol19, timeFrame, length, 18)
    getHLindexForTheSymbol(symbol20, timeFrame, length, 19)
    getHLindexForTheSymbol(symbol21, timeFrame, length, 20)
    getHLindexForTheSymbol(symbol22, timeFrame, length, 21)
    getHLindexForTheSymbol(symbol23, timeFrame, length, 22)
    getHLindexForTheSymbol(symbol24, timeFrame, length, 23)
    getHLindexForTheSymbol(symbol25, timeFrame, length, 24)
    getHLindexForTheSymbol(symbol26, timeFrame, length, 25)
    getHLindexForTheSymbol(symbol27, timeFrame, length, 26)
    getHLindexForTheSymbol(symbol28, timeFrame, length, 27)
    getHLindexForTheSymbol(symbol29, timeFrame, length, 28)
    getHLindexForTheSymbol(symbol30, timeFrame, length, 29)
    getHLindexForTheSymbol(symbol31, timeFrame, length, 30)
    getHLindexForTheSymbol(symbol32, timeFrame, length, 31)
    getHLindexForTheSymbol(symbol33, timeFrame, length, 32)
    getHLindexForTheSymbol(symbol34, timeFrame, length, 33)
    getHLindexForTheSymbol(symbol35, timeFrame, length, 34)
    getHLindexForTheSymbol(symbol36, timeFrame, length, 35)
    getHLindexForTheSymbol(symbol37, timeFrame, length, 36)
    getHLindexForTheSymbol(symbol38, timeFrame, length, 37)
    getHLindexForTheSymbol(symbol39, timeFrame, length, 38)
    getHLindexForTheSymbol(symbol40, timeFrame, length, 39)
    highs: int = 0
    total: int = 0
    for x in pine_range(0, 39, 1):
        highs = highs + (1 if array.get(HighsLows, x) == 1 else 0)
        total = total + (1 if array.get(HighsLows, x) == 1 or array.get(HighsLows, x) == -1 else 0)
    RecordHighPercent: Persistent[float] = 50
    RecordHighPercent = RecordHighPercent if total == 0 else 100 * highs / total
    HighLowIndex: Series = ta.sma(RecordHighPercent, smoothLength)
    HLIma = ta.ema(HighLowIndex, emaLength)
    peak = HighLowIndex[2] <= HighLowIndex[1] and HighLowIndex < HighLowIndex[1]
    dip = HighLowIndex[2] >= HighLowIndex[1] and HighLowIndex > HighLowIndex[1]
    HL_bull = HighLowIndex > HighLowIndex[1]
    HL_bear = HighLowIndex < HighLowIndex[1]
    HLma_bull = ta.crossover(HLIma, 50) and HL_bull
    HLma_bear = ta.crossunder(HLIma, 50) and HL_bear
    HL_cross = ta.cross(HighLowIndex, HLIma)
    def barsSinceLastEntry():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    inLong: bool = False
    inShort: bool = False
    last_high = high[1]
    last_low = low[1]
    long_SL: Series = last_low - datrp
    short_SL: Series = last_high + datrp
    long_PT = last_high + math.abs(high[1] - low[1])
    short_PT = last_low - math.abs(high[1] - low[1])
    long_CT_PT = long_PT
    short_CT_PT = short_PT
    last_entry = strategy.opentrades.entry_price(strategy.opentrades - 1)
    L_risk = last_entry - long_SL
    S_risk = short_SL - last_entry
    if strategy.opentrades > 0 and (not trailing_stop):
        long_SL = math.min(long_SL[barsSinceLastEntry()], last_low)
        short_SL = math.max(short_SL[barsSinceLastEntry()], last_high)
        L_risk = last_entry - long_SL
        S_risk = short_SL - last_entry
        long_PT = last_entry + (last_entry - long_SL) * RR
        short_PT = last_entry - (short_SL - last_entry) * RR
        long_CT_PT = last_entry + (last_entry - long_SL) * (RR / 3)
        short_CT_PT = last_entry - (short_SL - last_entry) * (RR / 3)
        long_SL = long_SL + L_risk * SL_offset * 0.01
        short_SL = short_SL - S_risk * SL_offset * 0.01
        barsSinceLastEntry_1 = barsSinceLastEntry()
        barsSinceLastEntry_2 = barsSinceLastEntry()
        if strategy.opentrades.size(0) > 0 and barsSinceLastEntry_1 > 0:
            inLong = True
        elif strategy.opentrades.size(0) < 0 and barsSinceLastEntry_2 > 0:
            inShort = True
    else:
        long_PT = last_high + math.abs(high - long_SL)
        short_PT = last_low - math.abs(short_SL - low)
    trade_pause: bool = False
    trade_pause2: bool = False
    time_1 = time(timeframe.period, '1000-1030:23456')
    if no_longat10 and cast_bool(time_1):
        trade_pause2 = True
    else:
        trade_pause2 = False
    L_entry1 = macd_bull and HL_bull and LR_trending and up_accel and (HighLowIndex < 96)
    S_entry1 = macd_bear and HL_bear and LR_trending and down_accel and (HighLowIndex > 4)
    exit0: bool = True
    L_exit1 = HighLowIndex[1] > 99 and HighLowIndex < 99
    S_exit1 = HighLowIndex[1] < 1 and HighLowIndex > 1
    L_exit2 = S_entry1
    S_exit2 = L_entry1
    profit = strategy.netprofit
    trade_amount = math.floor(strategy.initial_capital / close)
    if isSPY:
        if strategy.netprofit > 0 and reinvest and (strategy.closedtrades.profit(strategy.closedtrades - 1) > 0):
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * (SPY_option + math.floor(profit / strategy.initial_capital * 10))
        else:
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * SPY_option
    if not trade_pause and (not trade_pause2) and (strategy.opentrades == 0):
        if L_entry1 and window:
            strategy.entry('Long', strategy.long, trade_amount, comment='Long')
        if S_entry1 and window:
            strategy.entry('Short', strategy.short, trade_amount, comment='Short')
    if not trade_trailing and window:
        strategy.exit('Exit', 'Long', stop=long_SL, limit=long_PT, comment='Exit Long SL/PT hit')
        strategy.exit('Exit', 'Short', stop=short_SL, limit=short_PT, comment='Exit Short SL/PT hit')
    if strategy.opentrades.profit(strategy.opentrades - 1) > 0 and trade_earlyExit:
        if L_exit1 or L_exit2:
            strategy.close('Long', comment='Exit - Take profit')
        if S_exit1 or S_exit2:
            strategy.close('Short', comment='Exit - Take profit')
    if trade_trailing and (high > long_PT or TS[1] == 1) and window2:
        long_SL = math.max(long_SL[1], low - datrp)
        trailing_stop = True
        if exit0 and window2:
            strategy.exit('Exit', 'Long', stop=long_SL, comment='Exit Long Trailing SL')
    if trade_trailing and (not trailing_stop) and window:
        strategy.exit('Exit', 'Long', stop=long_SL, comment='Exit Long SL/PT hit')
    if trade_trailing and (low < short_PT or TS[1] == 1) and window2:
        short_SL = math.min(short_SL[1], high + datrp)
        trailing_stop = True
        if exit0 and window2:
            strategy.exit('Exit', 'Short', stop=short_SL, comment='Exit Short Trailing SL')
    if trade_trailing and (not trailing_stop) and window:
        strategy.exit('Exit', 'Short', stop=short_SL, comment='Exit Short SL/PT hit')
    if trade_expiry:
        if cast_bool(time(timeframe.period, '1550-1555:246')):
            strategy.close_all()
        if cast_bool(time(timeframe.period, '1550-1555:35')):
            strategy.close('Long', qty_percent=50, comment='Close 1/2 EOD')
            strategy.close('Short', qty_percent=50, comment='Close 1/2 EOD')
    if cast_bool(time(timeframe.period, '1555-1600:23456')):
        strategy.cancel_all()
    if strategy.opentrades == 0:
        trailing_stop = False
    TS = 1 if trailing_stop else 0
    SSL = plot(short_SL, title='Short SL', color=color.red if inShort else color.new(color.red, 100), linewidth=3)
    LSL = plot(long_SL, title='Long SL', color=color.red if inLong else color.new(color.red, 100), linewidth=3)
    LPT = plot(long_PT, title='Long PT', color=color.green if inLong else color.new(color.green, 100), linewidth=3)
    SPT = plot(short_PT, title='Short PT', color=color.green if inShort else color.new(color.green, 100), linewidth=3)
    LE = plot(last_entry, title='Last entry', color=color.gray if strategy.opentrades > 0 else color.new(color.gray, 100))
    fill(LPT, LE, color=color.new(color.green, 90) if strategy.opentrades.size(0) > 0 else na)
    fill(LE, LSL, color=color.new(color.red, 90) if strategy.opentrades.size(0) > 0 else na)
    fill(SPT, LE, color=color.new(color.green, 90) if strategy.opentrades.size(0) < 0 else na)
    fill(LE, SSL, color=color.new(color.red, 90) if strategy.opentrades.size(0) < 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
