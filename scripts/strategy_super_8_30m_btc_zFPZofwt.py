"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, close, color, fill, high, input, low, math, na, nz, open, plot,
    position, script, size, strategy, string, syminfo, ta, table, text, time, time_close,
    timestamp, volume
)
from pynecore.types import Persistent, Series

StartDate = timestamp('01 Jan 2000 01:00 +000')


@script.strategy('Super 8 - 30m BTCUSDT.P', shorttitle='Super 8', overlay=True, default_qty_value=0, initial_capital=10000, pyramiding=0, commission_value=0.05, commission_type=strategy.commission.percent, process_orders_on_close=True, margin_long=1.5, margin_short=1.5, use_bar_magnifier=False, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    Position=input.string('Both', 'Long / Short', options=('Long', 'Short', 'Both'), tooltip='Choose the position to take (long, short, or both)'),
    sEma_Length=input.int(500, 'Slow EMA Length', minval=0, step=25, group='EXPONENTIAL MOVING AVERAGE', tooltip='Set the length of the slow EMA'),
    fEma_Length=input.int(100, 'Fast EMA Length', minval=0, step=25, group='EXPONENTIAL MOVING AVERAGE', tooltip='Set the length of the fast EMA'),
    ADX_len=input.int(28, 'ADX Length', minval=1, group='AVERAGE DIRECTIONAL INDEX', tooltip='Set the length of the ADX'),
    ADX_smo=input.int(9, 'ADX Smoothing', minval=1, group='AVERAGE DIRECTIONAL INDEX', tooltip='Set the smoothing of the ADX'),
    th=input.float(20.5, 'ADX Threshold', minval=0, step=0.5, group='AVERAGE DIRECTIONAL INDEX', tooltip='Set the threshold for the ADX'),
    Sst=input.float(0.1, 'SAR star', minval=0.01, step=0.01, group='PARABOLIC SAR', tooltip='Set the starting value for the SAR'),
    Sinc=input.float(0.04, 'SAR inc', minval=0.01, step=0.01, group='PARABOLIC SAR', tooltip='Set the increment value for the SAR'),
    Smax=input.float(0.4, 'SAR max', minval=0.01, step=0.01, group='PARABOLIC SAR', tooltip='Set the maximum value for the SAR'),
    MACD_options=input.string('MACD', 'MACD OPTION', options=('MACD', 'MAC-Z'), group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Select the type of MACD to use. The MAC-Z is designed to reduce false signals compared to the standard MACD'),
    fastLength=input.int(24, 'MACD Fast MA Length', minval=1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Number of periods for the fast moving average.'),
    slowLength=input.int(52, 'MACD Slow MA Length', minval=1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Number of periods for the slow moving average.'),
    signalLength=input.int(11, 'MACD Signal Length', minval=1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Number of periods for the signal line.'),
    lengthz=input.int(14, 'Z-VWAP Length', minval=1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Number of periods for the Z-VWAP used in the MAC-Z calculation.'),
    lengthStdev=input.int(14, 'StDev Length', minval=1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Number of periods for the standard deviation used in the MAC-Z calculation.'),
    A=input.float(-0.2, 'MAC-Z constant A', minval=-2.0, maxval=2.0, step=0.1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Constant A used in the MAC-Z calculation.'),
    B=input.float(0.4, 'MAC-Z constant B', minval=-2.0, maxval=2.0, step=0.1, group='MOVING AVERAGE CONVERGENCE DIVERGENCE', tooltip='Constant B used in the MAC-Z calculation.'),
    volume_f=input.float(0.4, 'Volume Factor', minval=0, step=0.1, group='VOLUME CONDITION', tooltip='Factor used to determine the minimum required volume for an entry.'),
    sma_Length=input.int(55, 'SMA Volume Length', minval=1, group='VOLUME CONDITION', tooltip='Number of periods for the simple moving average used in the volume condition.'),
    BB_Length=input.int(40, 'BB Length', minval=1, group='BOLLINGER BANDS', tooltip='Length of the Bollinger Bands period'),
    BB_mult=input.float(2.2, 'BB Multiplier', minval=0.1, step=0.1, group='BOLLINGER BANDS', tooltip='Multiplier for the Bollinger Bands width'),
    bbMinWidth01=input.float(5.0, 'Min. BB Width % (New Position)', minval=0, step=0.5, group='BOLLINGER BANDS', tooltip='Minimum width of the Bollinger Bands to enter a new position'),
    bbMinWidth02=input.float(2.0, 'Min. BB Width % (Pyramiding)', minval=0, step=0.5, group='BOLLINGER BANDS', tooltip='Minimum width of the Bollinger Bands to add to an existing position'),
    TP_options=input.string('Both', 'Take Profit Option', options=('Normal', 'Donchian', 'Both'), group='TAKE PROFIT / TRAILING STOP', tooltip='Option for the take profit / trailing stop'),
    tp=input.float(1.8, 'Take Profit %', minval=0, step=0.1, group='TAKE PROFIT / TRAILING STOP', tooltip='Percentage profit target'),
    trailOffset=input.float(0.3, 'Trail offset %', minval=0, step=0.1, group='TAKE PROFIT / TRAILING STOP', tooltip='The offset percentage used for the trailing stop. If set to 0, only the Take Profit option will be used. If set to a value greater than 0, the Trailing Stop option will be used and the use_bar_magnifier parameter must also be set to true for more realistic results.'),
    DClength=input.int(55, title='Donchian Channel Period', minval=1, group='TAKE PROFIT / TRAILING STOP', tooltip='Defines the period of the Donchian Channel used for the take profit option.'),
    SL_options=input.string('Both', 'Stop Loss Option', options=('Normal', 'ATR', 'Both'), group='STOP LOSS', tooltip='Select the type of stop loss option you want to use.'),
    sl=input.float(8.0, 'Stop Loss %', minval=0, step=0.5, group='STOP LOSS', tooltip='Defines the percentage value of the stop loss.'),
    atrPeriodSl=input.int(14, title='ATR Period', minval=0, group='STOP LOSS', tooltip='Defines the period of the Average True Range used in the ATR stop loss option.'),
    multiplierPeriodSl=input.float(15, 'ATR Multiplier', minval=0, step=0.5, group='STOP LOSS', tooltip='Defines the multiplier used in the ATR stop loss option.'),
    Risk=input.float(5, 'Max. Risk %', tooltip='Set the maximum percentage of account balance you\'re willing to risk per position', minval=0, maxval=100, group='RISK'),
    Pyr=input.int(3, 'Max. Pyramiding', tooltip='Set the maximum number of trades you are willing to open within a position', minval=1, maxval=10, group='PYRAMIDING'),
    StepEntry=input.string('Incremental', 'Step Entry Mode', tooltip='Select the way you want to add new trades', options=('Normal', 'Incremental'), group='PYRAMIDING'),
    bbBetterPrice=input.float(0.7, 'Min. Better Price %', tooltip='Set the minimum better price percentage you want to get when adding new trades', minval=0.1, step=0.1, group='PYRAMIDING'),
    testPeriodStart=input.time(StartDate, 'Start of Trading', tooltip='Set the start date and time of the backtesting period', group='BACKTEST')
):
    AveragePrice: float = close
    AveragePrice = nz(strategy.position_avg_price, close)
    sEMA: Series = ta.ema(close, sEma_Length)
    fEMA = ta.ema(close, fEma_Length)
    EMA_longCond: bool = na(bool)
    EMA_shortCond: bool = na(bool)
    EMA_longCond = fEMA > sEMA and sEMA > sEMA[1]
    EMA_shortCond = fEMA < sEMA and sEMA < sEMA[1]
    EMA_color = color.new(color.green, 50) if EMA_longCond else color.new(color.red, 50) if EMA_shortCond else color.new(color.orange, 50)
    plot(sEMA, 'Slow EMA', EMA_color, 3)
    plot(fEMA, 'Fast EMA', EMA_color, 2)
    DIPlus, DIMinus, ADX = ta.dmi(ADX_len, ADX_smo)
    ADX_longCond: bool = na(bool)
    ADX_shortCond: bool = na(bool)
    ADX_longCond = DIPlus > DIMinus and ADX > th
    ADX_shortCond = DIPlus < DIMinus and ADX > th
    ADX_color = color.new(color.green, 25) if ADX_longCond else color.new(color.red, 25) if ADX_shortCond else color.new(color.orange, 25)
    barcolor(color=ADX_color, title='ADX')
    SAR = ta.sar(Sst, Sinc, Smax)
    SAR_longCond: bool = na(bool)
    SAR_shortCond: bool = na(bool)
    SAR_longCond = SAR < close
    SAR_shortCond = SAR > close
    plot(SAR, 'SAR', color.new(color.green, 50) if SAR_longCond else color.new(color.red, 50), style=plot.style_circles)
    lMACD, sMACD, hist = ta.macd(close, fastLength, slowLength, signalLength)
    def calc_zvwap(pds):
        mean = math.sum(volume * close, pds) / math.sum(volume, pds)
        vwapsd = math.sqrt(ta.sma(math.pow(close - mean, 2), pds))
        return (close - mean) / vwapsd

    zscore: float = na(float)
    fastMA: float = na(float)
    slowMA: float = na(float)
    macd: float = na(float)
    macz: float = na(float)
    signal: float = na(float)
    histmacz: float = na(float)
    zscore = calc_zvwap(lengthz)
    fastMA = ta.sma(close, fastLength)
    slowMA = ta.sma(close, slowLength)
    macd = lMACD
    macz = zscore * A + macd / (ta.stdev(close, lengthStdev) * B)
    signal = ta.sma(macz, signalLength)
    histmacz = macz - signal
    MACD_longCond: bool = na(bool)
    MACD_shortCond: bool = na(bool)
    MACD_longCond = hist > 0 if MACD_options == 'MACD' else histmacz > 0
    MACD_shortCond = hist < 0 if MACD_options == 'MACD' else histmacz < 0
    BB_middle, BB_upper, BB_lower = ta.bb(close, BB_Length, BB_mult)
    BB_width: float = na(float)
    BB_width = (BB_upper - BB_lower) / BB_middle
    BB_long01: bool = na(bool)
    crossunder_1 = ta.crossunder(low, BB_lower)
    BB_long01 = Position != 'Short' and (not ADX_shortCond) and crossunder_1 and EMA_longCond and (BB_width > bbMinWidth01 / 100)
    BB_long02: bool = na(bool)
    crossunder_2 = ta.crossunder(low, BB_lower)
    BB_long02 = Position != 'Short' and (not ADX_shortCond) and crossunder_2 and EMA_longCond and (BB_width > bbMinWidth02 / 100)
    BB_short01: bool = na(bool)
    crossover_1 = ta.crossover(high, BB_upper)
    BB_short01 = Position != 'Long' and (not ADX_longCond) and crossover_1 and EMA_shortCond and (BB_width > bbMinWidth01 / 100)
    BB_short02: bool = na(bool)
    crossover_2 = ta.crossover(high, BB_upper)
    BB_short02 = Position != 'Long' and (not ADX_longCond) and crossover_2 and EMA_shortCond and (BB_width > bbMinWidth02 / 100)
    u_BB = plot(BB_upper, 'Upper Bollinger Band', EMA_color, 2)
    l_BB = plot(BB_lower, 'Lower Bollinger Band', EMA_color, 2)
    fill(u_BB, l_BB, title='Bollinger Band Background', color=color.new(color.green, 95) if fEMA > sEMA else color.new(color.red, 95))
    VOL_longCond: bool = na(bool)
    VOL_shortCond: bool = na(bool)
    VOL_longCond = volume > ta.sma(volume, sma_Length) * volume_f
    VOL_shortCond = VOL_longCond
    longCond: bool = na(bool)
    longCond = Position != 'Short' and EMA_longCond and ADX_longCond and SAR_longCond and MACD_longCond and VOL_longCond
    shortCond: bool = na(bool)
    shortCond = Position != 'Long' and EMA_shortCond and ADX_shortCond and SAR_shortCond and MACD_shortCond and VOL_shortCond
    DClower: float = na(float)
    DCupper: float = na(float)
    DCbasis: float = na(float)
    DClower = ta.lowest(DClength)
    DCupper = ta.highest(DClength)
    DCbasis = math.avg(DCupper, DClower)
    longPriceProfit: float = na(float)
    shortPriceProfit: float = na(float)
    if TP_options == 'Both':
        longPriceProfit = math.max(DCupper, (1 + tp / 100) * AveragePrice)
        shortPriceProfit = math.min(DClower, (1 - tp / 100) * AveragePrice)
    elif TP_options == 'Normal':
        longPriceProfit = (1 + tp / 100) * AveragePrice
        shortPriceProfit = (1 - tp / 100) * AveragePrice
    elif TP_options == 'Donchian':
        longPriceProfit = math.max(DCupper, AveragePrice)
        shortPriceProfit = math.min(DClower, AveragePrice)
    plot(longPriceProfit if strategy.position_size > 0 else shortPriceProfit if strategy.position_size < 0 else na, 'Take Profit', color.new(color.blue, 30) if strategy.position_size > 0 else color.new(color.red, 30), 2, plot.style_circles)
    ATR_SL_Long: Series[float] = low - ta.atr(atrPeriodSl) * multiplierPeriodSl
    ATR_SL_Short: Series[float] = high + ta.atr(atrPeriodSl) * multiplierPeriodSl
    longStopPrev: float = nz(ATR_SL_Long[1], ATR_SL_Long)
    shortStopPrev: float = nz(ATR_SL_Short[1], ATR_SL_Short)
    ATR_SL_Long = math.max(ATR_SL_Long, longStopPrev) if open > longStopPrev else ATR_SL_Long
    ATR_SL_Short = math.min(ATR_SL_Short, shortStopPrev) if open < shortStopPrev else ATR_SL_Short
    longPriceStop: float = na(float)
    shortPriceStop: float = na(float)
    if SL_options == 'Both':
        longPriceStop = math.max(ATR_SL_Long, (1 - sl / 100) * AveragePrice)
        shortPriceStop = math.min(ATR_SL_Short, (1 + sl / 100) * AveragePrice)
    elif SL_options == 'Normal':
        longPriceStop = (1 - sl / 100) * AveragePrice
        shortPriceStop = (1 + sl / 100) * AveragePrice
    elif SL_options == 'ATR':
        longPriceStop = ATR_SL_Long
        shortPriceStop = ATR_SL_Short
    slPercentLong: float = na(float)
    slPercentLong = math.max(0, AveragePrice - longPriceStop) / AveragePrice * 100
    slPercentShort: float = na(float)
    slPercentShort = math.max(0, shortPriceStop - AveragePrice) / AveragePrice * 100
    plot(longPriceStop if strategy.position_size > 0 else shortPriceStop if strategy.position_size < 0 else na, 'Stop Loss', color.new(color.aqua, 80) if strategy.position_size > 0 else color.new(color.purple, 70), 2, plot.style_circles)
    plot(strategy.position_avg_price if cast_bool(ta.change(strategy.position_avg_price)) else na, 'Average price', color.new(color.aqua, 20) if strategy.position_size > 0 else color.new(color.yellow, 20), 2, plot.style_cross)
    Equity: float = strategy.equity
    Balance: float = strategy.initial_capital + strategy.netprofit
    RealizedPnL: float = strategy.netprofit
    Floating: float = strategy.openprofit
    PFloating: float = Floating / Balance * 100
    PRealizedPnL: float = RealizedPnL / strategy.initial_capital * 100
    URealizedPnL: float = Floating + RealizedPnL
    PURealizedPnL: float = URealizedPnL / strategy.initial_capital * 100
    ProfitFactor: float = strategy.grossprofit / strategy.grossloss
    PositionSize: float = strategy.position_size * strategy.position_avg_price
    Cash: float = Balance - nz(PositionSize) * 0.015
    Profitability: float = strategy.wintrades / (strategy.wintrades + strategy.losstrades) * 100
    LeverageParameter: float = math.abs(nz(PositionSize / Balance))
    TradingTime: int = time_close - strategy.closedtrades.entry_time(0)
    InfoPanel: Persistent = table.new(position.middle_left, 2, 10, na, color.new(color.white, 80), 1, color.new(color.white, 80), 1)
    def ftable(_table_id, _column, _row, _text, _text_color):
        return table.cell(_table_id, _column, _row, _text, 0, 0, _text_color, text.align_left, text.align_center, size.tiny, na)

    def tfString(timeInMs: int):
        s: float = timeInMs / 1000
        m: float = s / 60
        h: float = m / 60
        d: float = h / 24
        mo: float = d / 30.416
        tm: int = math.floor(m % 60)
        tr: int = math.floor(h % 24)
        td: int = math.floor(d % 30.416)
        tmo: int = math.floor(mo % 12)
        ys: int = math.floor(d / 365)
        __block_result__ = na
        if d == 30 and tr == 10 and (tm == 30):
            __block_result__ = '1M'
        elif d == 7 and tr == 0 and (tm == 0):
            __block_result__ = '1W'
        else:
            yStr: str = string.tostring(ys) + 'Y ' if cast_bool(ys) else ''
            moStr: str = string.tostring(tmo) + 'M ' if cast_bool(tmo) else ''
            dStr: str = string.tostring(td) + 'D ' if cast_bool(td) else ''
            hStr: str = string.tostring(tr) + 'H ' if cast_bool(tr) else ''
            mStr: str = string.tostring(tm) + 'min' if cast_bool(tm) else ''
            __block_result__ = yStr + moStr + dStr + hStr + mStr
        result: str = __block_result__
        return result

    ftable(InfoPanel, 0, 0, 'Equity: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 1, 'Position: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 2, 'Cash: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 3, 'Floating: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 4, 'Realized PnL: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 5, 'Unrealized PnL: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 6, 'Leverage: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 7, 'Profitability: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 8, 'Profit Factor: ', color.new(color.white, 50))
    ftable(InfoPanel, 0, 9, 'Time of Trading: ', color.new(color.white, 50))
    ftable(InfoPanel, 1, 0, string.tostring(Equity, '#.##') + ' ' + syminfo.currency, color.green if Equity >= 0 else color.red)
    ftable(InfoPanel, 1, 1, string.tostring(strategy.position_size, '#.#####') + ' ' + syminfo.basecurrency, color.green if strategy.position_size >= 0 else color.red)
    ftable(InfoPanel, 1, 2, string.tostring(Cash, '#.##') + ' ' + syminfo.currency, color.green if Cash >= 0 else color.red)
    ftable(InfoPanel, 1, 3, string.tostring(PFloating, '#.##') + ' %', color.green if PFloating >= 0 else color.red)
    ftable(InfoPanel, 1, 4, string.tostring(PRealizedPnL, '#.##') + ' %', color.green if PRealizedPnL >= 0 else color.red)
    ftable(InfoPanel, 1, 5, string.tostring(PURealizedPnL, '#.##') + ' %', color.green if PURealizedPnL >= 0 else color.red)
    ftable(InfoPanel, 1, 6, string.tostring(LeverageParameter, '#.##') + ' x', color.green if math.round(LeverageParameter, 1) <= 1 else color.red)
    ftable(InfoPanel, 1, 7, string.tostring(Profitability, '#.##') + ' %', color.green if Profitability >= 1 else color.red)
    ftable(InfoPanel, 1, 8, string.tostring(ProfitFactor, '#.###'), color.green if ProfitFactor >= 1 else color.red)
    ftable(InfoPanel, 1, 9, tfString(TradingTime), color.new(color.white, 50))
    def fSum(_Num):
        return (math.pow(_Num, 2) + _Num) / 2

    QuantityLong: float = na(float)
    QuantityShort: float = na(float)
    if StepEntry == 'Normal':
        QuantityLong = 1 / Pyr * (Balance / close) * (Risk / 100 / (slPercentLong / 100))
        QuantityShort = 1 / Pyr * (Balance / close) * (Risk / 100 / (slPercentShort / 100))
    else:
        QuantityLong = (strategy.opentrades + 1) / fSum(Pyr) * (Balance / close) * (Risk / 100 / (slPercentLong / 100))
        QuantityShort = (strategy.opentrades + 1) / fSum(Pyr) * (Balance / close) * (Risk / 100 / (slPercentShort / 100))
    LongMessage: str = na(str)
    LongMessage = '{ "id": "{{strategy.order.id}}", "action": "ENTER_LONG", "marketPosition": "{{strategy.market_position}}", "prevMarketPosition": "{{strategy.prev_market_position}}", "instrument": "{{ticker}}", "signalToken": "plqZRD/tDNWKyZKrS+mPNYGh9aCIeA3qSjTsYvPZqgbG+3Oc0oPAqCFAoIs0M8FHC/wr4zSYJhFrhbG+3hN0uA==", "timestamp": "{{timenow}}", "maxLag": "60", "investmentType": "base", "amount": "{{strategy.order.contracts}}" }'
    XLongMessage: str = na(str)
    XLongMessage = '{ "id": "{{strategy.order.id}}", "action": "EXIT_LONG", "marketPosition": "{{strategy.market_position}}", "prevMarketPosition": "{{strategy.prev_market_position}}", "instrument": "{{ticker}}", "signalToken": "plqZRD/tDNWKyZKrS+mPNYGh9aCIeA3qSjTsYvPZqgbG+3Oc0oPAqCFAoIs0M8FHC/wr4zSYJhFrhbG+3hN0uA==", "timestamp": "{{timenow}}", "maxLag": "60", "investmentType": "percentage_position", "amount": "100" }'
    ShortMessage: str = na(str)
    ShortMessage = '{ "id": "{{strategy.order.id}}", "action": "ENTER_SHORT", "marketPosition": "{{strategy.market_position}}", "prevMarketPosition": "{{strategy.prev_market_position}}", "instrument": "{{ticker}}", "signalToken": "plqZRD/tDNWKyZKrS+mPNYGh9aCIeA3qSjTsYvPZqgbG+3Oc0oPAqCFAoIs0M8FHC/wr4zSYJhFrhbG+3hN0uA==", "timestamp": "{{timenow}}", "maxLag": "60", "investmentType": "base", "amount": "{{strategy.order.contracts}}" }'
    XShortMessage: str = na(str)
    XShortMessage = '{ "id": "{{strategy.order.id}}", "action": "EXIT_SHORT", "marketPosition": "{{strategy.market_position}}", "prevMarketPosition": "{{strategy.prev_market_position}}", "instrument": "{{ticker}}", "signalToken": "plqZRD/tDNWKyZKrS+mPNYGh9aCIeA3qSjTsYvPZqgbG+3Oc0oPAqCFAoIs0M8FHC/wr4zSYJhFrhbG+3hN0uA==", "timestamp": "{{timenow}}", "maxLag": "60", "investmentType": "percentage_position", "amount": "100" }'
    if time >= testPeriodStart and strategy.opentrades < Pyr:
        if (longCond or BB_long01) and strategy.opentrades == 0 or ((longCond or BB_long01) and strategy.position_size < 0) or ((longCond or BB_long01) and close < strategy.opentrades.entry_price(strategy.opentrades - 1) * (1 - bbBetterPrice / 100)):
            strategy.order('Long', strategy.long, qty=QuantityLong, alert_message=LongMessage)
        if BB_long02 and strategy.position_size > 0 and (close < strategy.opentrades.entry_price(strategy.opentrades - 1) * (1 - bbBetterPrice / 100)):
            strategy.order('Long', strategy.long, qty=QuantityLong, alert_message=LongMessage)
    if time >= testPeriodStart and strategy.opentrades < Pyr:
        if (shortCond or BB_short01) and strategy.opentrades == 0 or ((shortCond or BB_short01) and strategy.position_size > 0) or ((shortCond or BB_short01) and close > strategy.opentrades.entry_price(strategy.opentrades - 1) * (1 + bbBetterPrice / 100)):
            strategy.order('Short', strategy.short, qty=QuantityShort, alert_message=ShortMessage)
        if BB_short02 and strategy.position_size < 0 and (close > strategy.opentrades.entry_price(strategy.opentrades - 1) * (1 + bbBetterPrice / 100)):
            strategy.order('Short', strategy.short, qty=QuantityShort, alert_message=ShortMessage)
    if trailOffset > 0:
        strategy.exit('TPl', 'Long', trail_price=longPriceProfit, trail_offset=trailOffset / 100 * high / syminfo.mintick, stop=longPriceStop, comment_profit='TPl', comment_loss='SLl', alert_message=XLongMessage)
    else:
        strategy.exit('TPl', 'Long', limit=longPriceProfit, stop=longPriceStop, comment_profit='TPl', comment_loss='SLl', alert_message=XLongMessage)
    if BB_long02 and strategy.position_size > 0:
        strategy.cancel('TPl')
    if trailOffset > 0:
        strategy.exit('TPs', 'Short', trail_price=shortPriceProfit, trail_offset=trailOffset / 100 * low / syminfo.mintick, stop=shortPriceStop, comment_profit='TPs', comment_loss='SLs', alert_message=XShortMessage)
    else:
        strategy.exit('TPs', 'Short', limit=shortPriceProfit, stop=shortPriceStop, comment_profit='TPs', comment_loss='SLs', alert_message=XShortMessage)
    if BB_short02 and strategy.position_size < 0:
        strategy.cancel('TPs')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
