"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, bar_index, barmerge, close, color, currency,
    dividends, earnings, high, hlc3, hline, input, location, low, math, na, plot, plotshape,
    request, script, shape, splits, strategy, string, syminfo, ta, time, timeframe, volume, year
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@script.strategy(title='Ultimate Bullish Divergence for RSI MFI RVSI OBV TRIXRSI w/ Buy Signals', shorttitle='Ultimate Bull Divergence Backtester', overlay=False, pyramiding=1, process_orders_on_close=True, calc_on_every_tick=True, initial_capital=1000, currency=currency.USD, default_qty_value=100, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.05, slippage=2, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    selectOsc=input.string('RSI', title='Select Oscillator', group='═════════ Oscillator settings ══════════', options=('RSI', 'OBV', 'RVSI', 'MFI', 'TRIX RSI'), tooltip='RSI = Relative Strengh Index; OBV = On Balance Volume; RVSI = Relative Volume Strengh Index; MFI Money Flow Index; TRIX RSI = Tripple Exponetial Relative Strength'),
    src: Series[float] = input.source(title='Oscillator Source', defval=low, group='═════════ Oscillator settings ══════════', tooltip='RSI, RVSI, OBV and TRIX RSI default Source: Close; MFI default Source: hlc3'),
    len=input.int(title='Oscillator Length', minval=1, defval=14, group='═════════ Oscillator settings ══════════', tooltip='RSI/MFI default Period = 14; RVSI = 10; TRIX RSI = 9; OBV has no period.'),
    seclen=input.int(9, minval=1, title='Oscillator secondary length', group='═════════ Oscillator settings ══════════', tooltip='affects only RVSI and Trix RSI. For the TRIX RSI this defines the length of the TRIX. default value = 9 and for the RVSI it defines the Volume moving average length, default value = 5'),
    emalen=input(9, 'Oscillator Moving Average Length', group='═════════ Oscillator settings ══════════', tooltip='defines the length of the of the Oscillator moving average'),
    rangeLower=input.int(title='Min Lookback Range', defval=0, group='═════ Oscillator Divergence Settings ══════', inline='Input 0'),
    rangeUpper=input.int(title='Max Lookback', defval=200, group='═════ Oscillator Divergence Settings ══════', inline='Input 0', tooltip='reduces the Lookback range that you define with Pivot Lookback Left 1-30 '),
    enableonlyOneLB=input.bool(title='Only use the first look back period', defval=False, group='═════ Oscillator Divergence Settings ══════'),
    lbL1=input.int(title='Pivot Lookback Left-1', defval=2, group='═════ Oscillator Divergence Settings ══════', inline='Input 1', tooltip='Amount of bars to look back to find pivot lows on the Oscillator and Price'),
    lbL2=input.int(title='Lookback Left-2', defval=3, group='═════ Oscillator Divergence Settings ══════', inline='Input 1'),
    lbL3=input.int(title='Pivot Lookback Left-3', defval=4, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL4=input.int(title='Lookback Left-4', defval=5, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL5=input.int(title='Pivot Lookback Left-5', defval=6, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL6=input.int(title='Lookback Left-6', defval=7, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL7=input.int(title='Pivot Lookback Left-7', defval=9, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL8=input.int(title='Lookback Left-8', defval=10, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL9=input.int(title='Pivot Lookback Left-9', defval=11, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL10=input.int(title='Lookback Left-10', defval=12, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL11=input.int(title='Pivot Lookback Left-11', defval=13, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL12=input.int(title='Lookback Left-12', defval=14, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL13=input.int(title='Pivot Lookback Left-13', defval=15, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL14=input.int(title='Lookback Left-14', defval=16, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL15=input.int(title='Pivot Lookback Left-15', defval=17, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL16=input.int(title='Lookback Left-16', defval=18, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL17=input.int(title='Pivot Lookback Left-17', defval=19, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL18=input.int(title='Lookback Left-18', defval=20, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL19=input.int(title='Pivot Lookback Left-19', defval=22, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL20=input.int(title='Lookback Left-20', defval=25, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL21=input.int(title='Pivot Lookback Left-21', defval=28, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL22=input.int(title='Lookback Left-22', defval=31, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL23=input.int(title='Pivot Lookback Left-23', defval=34, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL24=input.int(title='Lookback Left-24', defval=37, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL25=input.int(title='Pivot Lookback Left-25', defval=39, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL26=input.int(title='Lookback Left-26', defval=42, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL27=input.int(title='Pivot Lookback Left-27', defval=45, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL28=input.int(title='Lookback Left-28', defval=48, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL29=input.int(title='Pivot Lookback Left-29', defval=51, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    lbL30=input.int(title='Lookback Left-30', defval=54, group='═════ Oscillator Divergence Settings ══════', inline='Input 2'),
    plotBull=input.bool(title='Plot Bullish', defval=True, group='═════ Oscillator Divergence Settings ══════', inline='Input 4', tooltip='Price makes a lower low while the Oscillator is making a higher low'),
    plotHiddenBull=input.bool(title='Plot Hidden Bullish', defval=False, group='═════ Oscillator Divergence Settings ══════', inline='Input 4', tooltip='Price makes a higher low while Oscillator is making a lower low'),
    enablepriceBounceNeeded=input.bool(title='enable $ bounce delay', defval=False, group='═══════════ Signal Delays  ═══════════'),
    priceBounceNeeded=input.int(title='min $ bounce needed to flash buy', defval=35, group='═══════════ Signal Delays  ═══════════'),
    priceBounceNeededLbL=input.int(title='Amount of Candles until giving up', defval=3, minval=0, maxval=10, group='═══════════ Signal Delays  ═══════════'),
    lbR=input.int(title='Confirmation Time (bars) needed', minval=0, defval=0, group='Time Delay', tooltip='0 means the first candle - no candle close needed to flash a signal. Wait for a candle close to be sure (for alerts on the first cadle close set it to 0 and set the to "once per bar close")'),
    enableWaitForEmaBreak=input.bool(title='enable wait for moving average break', defval=False, group='EMA break Delay', tooltip='waits for a break of the moving average to flash a signal'),
    WaitForEmaBreakLen=input(5, 'EMA Length', group='EMA break Delay', tooltip='defines the length of the moving average which it needs to break before a signal flashes'),
    enableOscCross=input.bool(title='enable wait for Oscillator and Oscillator EMA Cross', defval=False, group='Oscillator EMA Cross Delay', tooltip=''),
    oscCrosslookback=input.int(title='Amount of Candles until giving up', defval=3, minval=0, maxval=10, group='Oscillator EMA Cross Delay'),
    enableOnlyLongUptrend=input.bool(title='only long on in an uptrend (rising moving average)', defval=False, group='═══════════ Ranges & Filter ═══════════', tooltip=''),
    OnlyLongUptrendEmaLen=input(200, 'EMA Length to determine an uptrend', group='═══════════ Ranges & Filter ═══════════', tooltip='defines the length of the of the moving average'),
    enableRsiLimit=input.bool(title='enable Oversold limits', defval=False, group='divergence below OverSold', tooltip='only works with RSI, MFI and RVSI'),
    osvalue=input.int(title='only show Signals if the Oscillator was below', defval=30, group='divergence below OverSold', inline='Input 1'),
    oslookback=input.int(title='within the last (x candles)', defval=2, group='divergence below OverSold', inline='Input 1'),
    maxBullRSI=input.int(title='only show signals if the Oscillator is', defval=35, group='divergence below OverSold'),
    enableManualbull1=input.bool(title='enable manual Bullish Range-1', defval=False, group='══════ manual Range for divergence signal'),
    manualbullHigh1=input.int(title='Range 1 - Bullish high', defval=10000000, group='══════ manual Range for divergence signal', inline='Input 0'),
    manualbullLow1=input.int(title='Range 1 - Bullish low', defval=0, group='══════ manual Range for divergence signal', inline='Input 0'),
    enableManualbull2=input.bool(title='enable manual Bullish Range-2', defval=False, group='══════ manual Range for divergence signal'),
    manualbullHigh2=input.int(title='Range 2 - Bullish high', defval=10000000, group='══════ manual Range for divergence signal', inline='Input 1'),
    manualbullLow2=input.int(title='Range 2 - Bullish low', defval=0, group='══════ manual Range for divergence signal', inline='Input 1'),
    enableManualbull3=input.bool(title='enable manual Bullish Range-1', defval=False, group='══════ manual Range for divergence signal'),
    manualbullHigh3=input.int(title='Range 3 - Bullish high', defval=10000000, group='══════ manual Range for divergence signal', inline='Input 2'),
    manualbullLow3=input.int(title='Range 3 - Bullish low', defval=0, group='══════ manual Range for divergence signal', inline='Input 2'),
    enableManualbull4=input.bool(title='enable manual Bullish Range-2', defval=False, group='══════ manual Range for divergence signal'),
    manualbullHigh4=input.int(title='Range 4 - Bullish high', defval=10000000, group='══════ manual Range for divergence signal', inline='Input 3'),
    manualbullLow4=input.int(title='Range 4 - Bullish low', defval=0, group='══════ manual Range for divergence signal', inline='Input 3'),
    enableEmaBullHigh=input.bool(title='enable EMA as High of the Long Range', defval=False, group='══════ EMA Range for divergence signal'),
    emaBullHighLen=input.int(9, minval=1, title='Length', group='══════ EMA Range for divergence signal', inline='Input 4'),
    emaBullHighSrc: Series[float] = input(close, title='Source', group='══════ EMA Range for divergence signal', inline='Input 4'),
    emaBullHighDevi=input.int(title='deviation', defval=0, minval=-500, maxval=500, group='══════ EMA Range for divergence signal', inline='Input 4'),
    enableEmaBullLow=input.bool(title='enable EMA as Low of the Long Range', defval=False, group='══════ EMA Range for divergence signal'),
    emaBullLowLen=input.int(55, minval=1, title='Length', group='══════ EMA Range for divergence signal', inline='Input 5'),
    emaBullLowSrc: Series[float] = input(close, title='Source', group='══════ EMA Range for divergence signal', inline='Input 5'),
    emaBullLowOffset=input.int(title='deviation', defval=0, minval=-500, maxval=500, group='══════ EMA Range for divergence signal', inline='Input 5'),
    enableVwapBullHigh=input.bool(title='enable VWAP as High of the Long Range', defval=False, group='════ VWAP Range for divergence signal'),
    enableVwapBullLow=input.bool(title='enable VWAP as Low of the Long Range', defval=False, group='════ VWAP Range for divergence signal'),
    enableVwapDiviBullHigh=input.bool(title='enable VWAP Upper Diviation as High of the Long Range', defval=False, group='════ VWAP Range for divergence signal'),
    enableVwapDiviBullLow=input.bool(title='enable VWAP Lower Diviation as Low of the Long Range', defval=False, group='════ VWAP Range for divergence signal'),
    anchor__input=input.string(defval='Session', title='Anchor Period', options=('Session', 'Week', 'Month', 'Quarter', 'Year', 'Decade', 'Century', 'Earnings', 'Dividends', 'Splits'), group='VWAP Settings'),
    vsrc: Series[float] = input.source(title='Source', defval=hlc3, group='VWAP Settings'),
    offset=input.int(0, title='Offset', group='VWAP Settings'),
    stdevMult=input.float(1.0, title='Bands Standard Diviation Multiplier', group='VWAP Settings'),
    enablefibbullHigh=input.bool(title='enable Auto fib as High of the Long Range', defval=False, group='════ auto fib range for divergence signal', inline='Input 0'),
    selectfibbullHigh=input.float(0.5, 'fib Level', options=(0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1), group='══ auto fib range for divergence signal'),
    fibbullHighLookback=input.int(title='Auto Fib Lookback', minval=1, defval=200, group='════ auto fib range for divergence signal', inline='Input 1'),
    enablefibbullLow=input.bool(title='enable Auto fib as Low of the Long Range', defval=False, group='════ auto fib range for divergence signal', inline='Input 2'),
    selectfibbullLow=input.float(0.886, 'fib Level', options=(0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1), group='════ auto fib range for divergence signal'),
    fibbullLowhLookback=input.int(title='Auto Fib Lookback', minval=1, defval=200, group='════ auto fib range for divergence signal', inline='Input 3'),
    enableSL=input.bool(True, title='enable Stop Loss', group='══════════ Stop Loss Settings ══════════'),
    whichSL=input.string(defval='use the low as SL', title='SL based on static % or based on the low', options=('use the low as SL', 'use the static % as SL'), group='══════════ Stop Loss Settings ══════════'),
    whichOffset=input.string(defval='use % as offset', title='choose offset from the low', options=('use $ as offset', 'use % as offset'), group='Stop Loss at the low'),
    __input_91__=input.float(0.35, title='SL Offset from the Low in %', group='Stop Loss at the low'),
    lowDBuffer=input.float(100, title='SL Offset from the Low in $', group='Stop Loss at the low'),
    SlLowLookback=input.int(title='SL lookback for Low', defval=5, minval=1, maxval=50, group='Stop Loss at the low'),
    __input_94__=input.float(0.5, title='Stop Loss in %', group='static % Stop Loss', inline='Input 1'),
    __input_95__=input.float(2, title='Take Profit in %', group='Take Profit', inline='Input 1'),
    selectalertFreq=input.string(defval='once per bar close', title='Alert Options', options=('once per bar', 'once per bar close', 'all'), group='═══════════ alert settings ═══════════'),
    BuyAlertMessage=input.string(defval='Bullish Divergence detected, put your SL @', title='Buy Alert Message', group='═══════════ alert settings ═══════════'),
    enableSlMessage=input.bool(True, title='enable Stop Loss Value at the end of "buy Alert message"', group='═══════════ alert settings ═══════════'),
    AfterSLMessage=input.string(defval='', title='Buy Alert message after SL Value', group='═══════════ alert settings ═══════════')
):
    EmaUptrend = ta.ema(src, OnlyLongUptrendEmaLen)
    isInEMAUptrend = ta.change(EmaUptrend) > 0 or not enableOnlyLongUptrend
    isWithinLongRange1 = close < manualbullHigh1 and close > manualbullLow1
    isWithinLongRange2 = close < manualbullHigh2 and close > manualbullLow2
    isWithinLongRange3 = close < manualbullHigh3 and close > manualbullLow3
    isWithinLongRange4 = close < manualbullHigh4 and close > manualbullLow4
    isWithinLongRange: bool = True
    if enableManualbull1 or enableManualbull2 or enableManualbull3 or enableManualbull4:
        isWithinLongRange = isWithinLongRange1 and enableManualbull1 or (isWithinLongRange2 and enableManualbull2) or (isWithinLongRange3 and enableManualbull3) or (isWithinLongRange4 and enableManualbull4)
    emaBullHighOut = ta.sma(emaBullHighSrc, emaBullHighLen)
    isBelowEmaBullHigh = close < emaBullHighOut or not enableEmaBullHigh
    emaBullLowOut = ta.sma(emaBullLowSrc, emaBullLowLen)
    isBelowEmaBullLow = close > emaBullLowOut or not enableEmaBullLow
    iswithinEmaRange = isBelowEmaBullHigh and isBelowEmaBullLow
    def computeVWAP(src, isNewPeriod, stDevMultiplier):
        sumSrcVol: PersistentSeries[float] = na(float)
        sumVol: PersistentSeries[float] = na(float)
        sumSrcSrcVol: PersistentSeries[float] = na(float)
        sumSrcVol = src * volume if isNewPeriod else src * volume + sumSrcVol[1]
        sumVol = volume if isNewPeriod else volume + sumVol[1]
        sumSrcSrcVol = volume * math.pow(src, 2) if isNewPeriod else volume * math.pow(src, 2) + sumSrcSrcVol[1]
        _vwap = sumSrcVol / sumVol
        variance = sumSrcSrcVol / sumVol - math.pow(_vwap, 2)
        variance = 0 if variance < 0 else variance
        stDev = math.sqrt(variance)
        lowerBand = _vwap - stDev * stDevMultiplier
        upperBand = _vwap + stDev * stDevMultiplier
        return (_vwap, lowerBand, upperBand)

    hideonDWM: bool = False
    anchor: Persistent = anchor__input
    def timeChange(period):
        return ta.change(time(period))

    new_earnings = request.earnings(syminfo.tickerid, earnings.actual, barmerge.gaps_on, barmerge.lookahead_on)
    new_dividends = request.dividends(syminfo.tickerid, dividends.gross, barmerge.gaps_on, barmerge.lookahead_on)
    new_split = request.splits(syminfo.tickerid, splits.denominator, barmerge.gaps_on, barmerge.lookahead_on)
    isNewPeriod = new_earnings if anchor == 'Earnings' else new_dividends if anchor == 'Dividends' else new_split if anchor == 'Splits' else True if na(vsrc[1]) else timeChange('D') if anchor == 'Session' else timeChange('W') if anchor == 'Week' else timeChange('M') if anchor == 'Month' else timeChange('3M') if anchor == 'Quarter' else timeChange('12M') if anchor == 'Year' else timeChange('12M') and year % 10 == 0 if anchor == 'Decade' else timeChange('12M') and year % 100 == 0 if anchor == 'Century' else False
    vwapValue: float = na(float)
    std: float = na(float)
    upperBandValue: float = na(float)
    lowerBandValue: float = na(float)
    showBands: bool = True
    if not (hideonDWM and timeframe.isdwm):
        _vwap, bottom, top = computeVWAP(vsrc, isNewPeriod, stdevMult)
        vwapValue = _vwap
        upperBandValue = top if showBands else na
        lowerBandValue = bottom if showBands else na
    isBelowVwap = vwapValue < close or not enableVwapBullHigh
    isAboveVwap = vwapValue > close or not enableVwapBullLow
    isAboveVwapLowerDivi = lowerBandValue < close or not enableVwapDiviBullLow
    isBelowVwapUpperDivi = upperBandValue > close or not enableVwapDiviBullHigh
    isWithinVwapRange = isBelowVwap and isAboveVwap and isAboveVwapLowerDivi and isBelowVwapUpperDivi
    isBelowfibbullHigh: bool = True
    isBelowfibbullLow: bool = True
    fibLowPrice: float = 0.1
    fibHighPrice: float = 0.1
    fibHighLow: float = 0.1
    fibHighHigh: float = 0.1
    fibLowHigh: float = 0.1
    fibLowLow: float = 0.1
    if enablefibbullHigh:
        fibHighHigh = ta.highest(high, fibbullHighLookback)
        fibHighLow = ta.lowest(low, fibbullHighLookback)
        fibHighPrice = (fibHighHigh - fibHighLow) * (1 - selectfibbullHigh) + fibHighLow
        isBelowfibbullHigh = fibHighPrice > ta.lowest(low, 2) or not enablefibbullHigh
    if enablefibbullLow:
        fibLowHigh = ta.highest(high, fibbullLowhLookback)
        fibLowLow = ta.lowest(low, fibbullLowhLookback)
        fibLowPrice = (fibLowHigh - fibLowLow) * (1 - selectfibbullLow) + fibLowLow
        isBelowfibbullLow = fibLowPrice < ta.highest(low, 2) or not enablefibbullLow
    isWithinFibRange = isBelowfibbullHigh and isBelowfibbullLow
    isWithinLongRanges = isWithinLongRange and iswithinEmaRange and isWithinVwapRange and isWithinFibRange and isInEMAUptrend
    bullColor = color.purple
    bullColor1 = color.aqua
    bullColor2 = color.black
    bullColor3 = color.blue
    bullColor4 = color.fuchsia
    bullColor5 = color.gray
    bullColor6 = color.green
    bullColor7 = color.lime
    bullColor8 = color.maroon
    bullColor9 = color.navy
    bullColor10 = color.olive
    bullColor11 = color.orange
    bullColor12 = color.purple
    bullColor13 = color.red
    bullColor14 = color.silver
    bullColor15 = color.teal
    bullColor16 = color.blue
    bullColor17 = color.navy
    bullColor18 = color.purple
    bullColor19 = color.purple
    bullColor20 = color.red
    bullColor21 = color.orange
    bullColor22 = color.purple
    bullColor23 = color.red
    bullColor24 = color.silver
    bullColor25 = color.teal
    bullColor26 = color.lime
    bullColor27 = color.fuchsia
    bullColor28 = color.lime
    bullColor29 = color.purple
    bullColor30 = color.red
    bullColor31 = color.aqua
    bullColor32 = color.black
    bullColor33 = color.blue
    bullColor34 = color.fuchsia
    bullColor35 = color.gray
    hiddenBullColor = color.new(color.purple, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    osc: Series = ta.rsi(src, len)
    if selectOsc == 'RSI':
        osc = ta.rsi(src, len)
    if selectOsc == 'RVSI':
        nv = ta.cum(ta.change(src) * volume)
        av = ta.ema(nv, seclen)
        RVSI = ta.rsi(av, len)
        osc = RVSI
    if selectOsc == 'OBV':
        osc = ta.obv
    if selectOsc == 'MFI':
        upper = math.sum(volume * (0 if ta.change(src) <= 0 else src), len)
        lower = math.sum(volume * (0 if ta.change(src) >= 0 else src), len)
        osc = 100.0 - 100.0 / (1.0 + upper / lower)
    if selectOsc == 'TRIX RSI':
        trix = 10000 * ta.change(ta.ema(ta.ema(ta.ema(math.log(src), seclen), seclen), seclen))
        osc = ta.rsi(trix, len)
    oscema = ta.ema(osc, emalen)
    osLowestRsi = ta.lowest(osc, oslookback)
    RSIwasBelowOS = osLowestRsi < osvalue or not enableRsiLimit
    isBelowRsiBull = osc < maxBullRSI or not enableRsiLimit
    osLevel = hline(osvalue, title='Oversold', linestyle=hline.style_dotted)
    maxRSIline = hline(maxBullRSI, title='max RSI for Bull divergence', linestyle=hline.style_dotted)
    plot(osc, title='Oscillator', linewidth=2, color=color.new(color.new('#00BCD4'), 0))
    plot(oscema, color=color.purple, title='Oscillator EMA', style=plot.style_circles)
    plFound1: Series = False if na(ta.pivotlow(osc, lbL1, lbR)) else True
    def _inRange1(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange1_1 = _inRange1(plFound1[1])
    oscHL1 = osc[lbR] > ta.valuewhen(plFound1, osc[lbR], 1) and _inRange1_1
    priceLL1 = low[lbR] < ta.valuewhen(plFound1, low[lbR], 1)
    bullCond1 = plotBull and priceLL1 and oscHL1 and plFound1 and RSIwasBelowOS and isWithinLongRanges
    plotshape(osc[lbR] if bullCond1 else na, offset=-lbR, title='Regular Bullish 1 Label', text=' B1 ', style=shape.labelup, location=location.absolute, color=bullColor1, textcolor=textColor)
    _inRange1_2 = _inRange1(plFound1[1])
    oscLL1 = osc[lbR] < ta.valuewhen(plFound1, osc[lbR], 1) and _inRange1_2
    priceHL1 = low[lbR] > ta.valuewhen(plFound1, low[lbR], 1)
    hiddenBullCond1 = plotHiddenBull and priceHL1 and oscLL1 and plFound1 and RSIwasBelowOS and isWithinLongRanges
    plotshape(osc[lbR] if hiddenBullCond1 else na, offset=-lbR, title='Hidden Bullish 1 Label', text=' H B1 ', style=shape.labelup, location=location.absolute, color=bullColor1, textcolor=textColor)
    plFound2: Series = False if na(ta.pivotlow(osc, lbL2, lbR)) else True
    def _inRange2(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange2_1 = _inRange2(plFound2[1])
    oscHL2 = osc[lbR] > ta.valuewhen(plFound2, osc[lbR], 1) and _inRange2_1
    priceLL2 = low[lbR] < ta.valuewhen(plFound2, low[lbR], 1)
    bullCond2 = plotBull and priceLL2 and oscHL2 and plFound2 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond2 else na, offset=-lbR, title='Regular Bullish 2 Label', text=' B2 ', style=shape.labelup, location=location.absolute, color=bullColor2, textcolor=textColor)
    _inRange2_2 = _inRange2(plFound2[1])
    oscLL2 = osc[lbR] < ta.valuewhen(plFound2, osc[lbR], 1) and _inRange2_2
    priceHL2 = low[lbR] > ta.valuewhen(plFound2, low[lbR], 1)
    hiddenBullCond2 = plotHiddenBull and priceHL2 and oscLL2 and plFound2 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond2 else na, offset=-lbR, title='Hidden Bullish 2 Label', text=' H B2 ', style=shape.labelup, location=location.absolute, color=bullColor2, textcolor=textColor)
    plFound3: Series = False if na(ta.pivotlow(osc, lbL3, lbR)) else True
    def _inRange3(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange3_1 = _inRange3(plFound3[1])
    oscHL3 = osc[lbR] > ta.valuewhen(plFound3, osc[lbR], 1) and _inRange3_1
    priceLL3 = low[lbR] < ta.valuewhen(plFound3, low[lbR], 1)
    bullCond3 = plotBull and priceLL3 and oscHL3 and plFound3 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond3 else na, offset=-lbR, title='Regular Bullish 3 Label', text=' B3 ', style=shape.labelup, location=location.absolute, color=bullColor3, textcolor=textColor)
    _inRange3_2 = _inRange3(plFound3[1])
    oscLL3 = osc[lbR] < ta.valuewhen(plFound3, osc[lbR], 1) and _inRange3_2
    priceHL3 = low[lbR] > ta.valuewhen(plFound3, low[lbR], 1)
    hiddenBullCond3 = plotHiddenBull and priceHL3 and oscLL3 and plFound3 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond3 else na, offset=-lbR, title='Hidden Bullish 3 Label', text=' H B3 ', style=shape.labelup, location=location.absolute, color=bullColor3, textcolor=textColor)
    plFound4: Series = False if na(ta.pivotlow(osc, lbL4, lbR)) else True
    def _inRange4(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange4_1 = _inRange4(plFound4[1])
    oscHL4 = osc[lbR] > ta.valuewhen(plFound4, osc[lbR], 1) and _inRange4_1
    priceLL4 = low[lbR] < ta.valuewhen(plFound4, low[lbR], 1)
    bullCond4 = plotBull and priceLL4 and oscHL4 and plFound4 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond4 else na, offset=-lbR, title='Regular Bullish 4 Label', text=' B4 ', style=shape.labelup, location=location.absolute, color=bullColor4, textcolor=textColor)
    _inRange4_2 = _inRange4(plFound4[1])
    oscLL4 = osc[lbR] < ta.valuewhen(plFound4, osc[lbR], 1) and _inRange4_2
    priceHL4 = low[lbR] > ta.valuewhen(plFound4, low[lbR], 1)
    hiddenBullCond4 = plotHiddenBull and priceHL4 and oscLL4 and plFound4 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond4 else na, offset=-lbR, title='Hidden Bullish 4 Label', text=' H B4 ', style=shape.labelup, location=location.absolute, color=bullColor4, textcolor=textColor)
    plFound5: Series = False if na(ta.pivotlow(osc, lbL5, lbR)) else True
    def _inRange5(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange5_1 = _inRange5(plFound5[1])
    oscHL5 = osc[lbR] > ta.valuewhen(plFound5, osc[lbR], 1) and _inRange5_1
    priceLL5 = low[lbR] < ta.valuewhen(plFound5, low[lbR], 1)
    bullCond5 = plotBull and priceLL5 and oscHL5 and plFound5 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond5 else na, offset=-lbR, title='Regular Bullish 5 Label', text=' B5 ', style=shape.labelup, location=location.absolute, color=bullColor5, textcolor=textColor)
    _inRange5_2 = _inRange5(plFound5[1])
    oscLL5 = osc[lbR] < ta.valuewhen(plFound5, osc[lbR], 1) and _inRange5_2
    priceHL5 = low[lbR] > ta.valuewhen(plFound5, low[lbR], 1)
    hiddenBullCond5 = plotHiddenBull and priceHL5 and oscLL5 and plFound5 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond5 else na, offset=-lbR, title='Hidden Bullish 5 Label', text=' H B5 ', style=shape.labelup, location=location.absolute, color=bullColor5, textcolor=textColor)
    plFound6: Series = False if na(ta.pivotlow(osc, lbL6, lbR)) else True
    def _inRange6(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange6_1 = _inRange6(plFound6[1])
    oscHL6 = osc[lbR] > ta.valuewhen(plFound6, osc[lbR], 1) and _inRange6_1
    priceLL6 = low[lbR] < ta.valuewhen(plFound6, low[lbR], 1)
    bullCond6 = plotBull and priceLL6 and oscHL6 and plFound6 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond6 else na, offset=-lbR, title='Regular Bullish 6 Label', text=' B6 ', style=shape.labelup, location=location.absolute, color=bullColor6, textcolor=textColor)
    _inRange6_2 = _inRange6(plFound6[1])
    oscLL6 = osc[lbR] < ta.valuewhen(plFound6, osc[lbR], 1) and _inRange6_2
    priceHL6 = low[lbR] > ta.valuewhen(plFound6, low[lbR], 1)
    hiddenBullCond6 = plotHiddenBull and priceHL6 and oscLL6 and plFound6 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond6 else na, offset=-lbR, title='Hidden Bullish 6 Label', text=' H B6 ', style=shape.labelup, location=location.absolute, color=bullColor6, textcolor=textColor)
    plFound7: Series = False if na(ta.pivotlow(osc, lbL7, lbR)) else True
    def _inRange7(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange7_1 = _inRange7(plFound7[1])
    oscHL7 = osc[lbR] > ta.valuewhen(plFound7, osc[lbR], 1) and _inRange7_1
    priceLL7 = low[lbR] < ta.valuewhen(plFound7, low[lbR], 1)
    bullCond7 = plotBull and priceLL7 and oscHL7 and plFound7 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond7 else na, offset=-lbR, title='Regular Bullish 7 Label', text=' B7 ', style=shape.labelup, location=location.absolute, color=bullColor7, textcolor=textColor)
    _inRange7_2 = _inRange7(plFound7[1])
    oscLL7 = osc[lbR] < ta.valuewhen(plFound7, osc[lbR], 1) and _inRange7_2
    priceHL7 = low[lbR] > ta.valuewhen(plFound7, low[lbR], 1)
    hiddenBullCond7 = plotHiddenBull and priceHL7 and oscLL7 and plFound7 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond7 else na, offset=-lbR, title='Hidden Bullish 7 Label', text=' H B7 ', style=shape.labelup, location=location.absolute, color=bullColor7, textcolor=textColor)
    plFound8: Series = False if na(ta.pivotlow(osc, lbL8, lbR)) else True
    def _inRange8(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange8_1 = _inRange8(plFound8[1])
    oscHL8 = osc[lbR] > ta.valuewhen(plFound8, osc[lbR], 1) and _inRange8_1
    priceLL8 = low[lbR] < ta.valuewhen(plFound8, low[lbR], 1)
    bullCond8 = plotBull and priceLL8 and oscHL8 and plFound8 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond8 else na, offset=-lbR, title='Regular Bullish 8 Label', text=' B8 ', style=shape.labelup, location=location.absolute, color=bullColor8, textcolor=textColor)
    _inRange8_2 = _inRange8(plFound8[1])
    oscLL8 = osc[lbR] < ta.valuewhen(plFound8, osc[lbR], 1) and _inRange8_2
    priceHL8 = low[lbR] > ta.valuewhen(plFound8, low[lbR], 1)
    hiddenBullCond8 = plotHiddenBull and priceHL8 and oscLL8 and plFound8 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond8 else na, offset=-lbR, title='Hidden Bullish 8 Label', text=' H B8 ', style=shape.labelup, location=location.absolute, color=bullColor8, textcolor=textColor)
    plFound9: Series = False if na(ta.pivotlow(osc, lbL9, lbR)) else True
    def _inRange9(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange9_1 = _inRange9(plFound9[1])
    oscHL9 = osc[lbR] > ta.valuewhen(plFound9, osc[lbR], 1) and _inRange9_1
    priceLL9 = low[lbR] < ta.valuewhen(plFound9, low[lbR], 1)
    bullCond9 = plotBull and priceLL9 and oscHL9 and plFound9 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond9 else na, offset=-lbR, title='Regular Bullish 9 Label', text=' B9 ', style=shape.labelup, location=location.absolute, color=bullColor9, textcolor=textColor)
    _inRange9_2 = _inRange9(plFound9[1])
    oscLL9 = osc[lbR] < ta.valuewhen(plFound9, osc[lbR], 1) and _inRange9_2
    priceHL9 = low[lbR] > ta.valuewhen(plFound9, low[lbR], 1)
    hiddenBullCond9 = plotHiddenBull and priceHL9 and oscLL9 and plFound9 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond9 else na, offset=-lbR, title='Hidden Bullish 9 Label', text=' H B9 ', style=shape.labelup, location=location.absolute, color=bullColor9, textcolor=textColor)
    plFound10: Series = False if na(ta.pivotlow(osc, lbL10, lbR)) else True
    def _inRange10(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange10_1 = _inRange10(plFound10[1])
    oscHL10 = osc[lbR] > ta.valuewhen(plFound10, osc[lbR], 1) and _inRange10_1
    priceLL10 = low[lbR] < ta.valuewhen(plFound10, low[lbR], 1)
    bullCond10 = plotBull and priceLL10 and oscHL10 and plFound10 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond10 else na, offset=-lbR, title='Regular Bullish 10 Label', text=' B10 ', style=shape.labelup, location=location.absolute, color=bullColor10, textcolor=textColor)
    _inRange10_2 = _inRange10(plFound10[1])
    oscLL10 = osc[lbR] < ta.valuewhen(plFound10, osc[lbR], 1) and _inRange10_2
    priceHL10 = low[lbR] > ta.valuewhen(plFound10, low[lbR], 1)
    hiddenBullCond10 = plotHiddenBull and priceHL10 and oscLL10 and plFound10 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond10 else na, offset=-lbR, title='Hidden Bullish 10 Label', text=' H B10 ', style=shape.labelup, location=location.absolute, color=bullColor10, textcolor=textColor)
    plFound11: Series = False if na(ta.pivotlow(osc, lbL11, lbR)) else True
    def _inRange11(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange11_1 = _inRange11(plFound11[1])
    oscHL11 = osc[lbR] > ta.valuewhen(plFound11, osc[lbR], 1) and _inRange11_1
    priceLL11 = low[lbR] < ta.valuewhen(plFound11, low[lbR], 1)
    bullCond11 = plotBull and priceLL11 and oscHL11 and plFound11 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond11 else na, offset=-lbR, title='Regular Bullish 11 Label', text=' B11 ', style=shape.labelup, location=location.absolute, color=bullColor11, textcolor=textColor)
    _inRange11_2 = _inRange11(plFound11[1])
    oscLL11 = osc[lbR] < ta.valuewhen(plFound11, osc[lbR], 1) and _inRange11_2
    priceHL11 = low[lbR] > ta.valuewhen(plFound11, low[lbR], 1)
    hiddenBullCond11 = plotHiddenBull and priceHL11 and oscLL11 and plFound11 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond11 else na, offset=-lbR, title='Hidden Bullish 11 Label', text=' H B11 ', style=shape.labelup, location=location.absolute, color=bullColor11, textcolor=textColor)
    plFound12: Series = False if na(ta.pivotlow(osc, lbL12, lbR)) else True
    def _inRange12(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange12_1 = _inRange12(plFound12[1])
    oscHL12 = osc[lbR] > ta.valuewhen(plFound12, osc[lbR], 1) and _inRange12_1
    priceLL12 = low[lbR] < ta.valuewhen(plFound12, low[lbR], 1)
    bullCond12 = plotBull and priceLL12 and oscHL12 and plFound12 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond12 else na, offset=-lbR, title='Regular Bullish 12 Label', text=' B12 ', style=shape.labelup, location=location.absolute, color=bullColor12, textcolor=textColor)
    _inRange12_2 = _inRange12(plFound12[1])
    oscLL12 = osc[lbR] < ta.valuewhen(plFound12, osc[lbR], 1) and _inRange12_2
    priceHL12 = low[lbR] > ta.valuewhen(plFound12, low[lbR], 1)
    hiddenBullCond12 = plotHiddenBull and priceHL12 and oscLL12 and plFound12 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond12 else na, offset=-lbR, title='Hidden Bullish 12 Label', text=' H B12 ', style=shape.labelup, location=location.absolute, color=bullColor12, textcolor=textColor)
    plFound13: Series = False if na(ta.pivotlow(osc, lbL13, lbR)) else True
    def _inRange13(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange13_1 = _inRange13(plFound13[1])
    oscHL13 = osc[lbR] > ta.valuewhen(plFound13, osc[lbR], 1) and _inRange13_1
    priceLL13 = low[lbR] < ta.valuewhen(plFound13, low[lbR], 1)
    bullCond13 = plotBull and priceLL13 and oscHL13 and plFound13 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond13 else na, offset=-lbR, title='Regular Bullish 13 Label', text=' B13 ', style=shape.labelup, location=location.absolute, color=bullColor13, textcolor=textColor)
    _inRange13_2 = _inRange13(plFound13[1])
    oscLL13 = osc[lbR] < ta.valuewhen(plFound13, osc[lbR], 1) and _inRange13_2
    priceHL13 = low[lbR] > ta.valuewhen(plFound13, low[lbR], 1)
    hiddenBullCond13 = plotHiddenBull and priceHL13 and oscLL13 and plFound13 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond13 else na, offset=-lbR, title='Hidden Bullish 13 Label', text=' H B13 ', style=shape.labelup, location=location.absolute, color=bullColor13, textcolor=textColor)
    plFound14: Series = False if na(ta.pivotlow(osc, lbL14, lbR)) else True
    def _inRange14(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange14_1 = _inRange14(plFound14[1])
    oscHL14 = osc[lbR] > ta.valuewhen(plFound14, osc[lbR], 1) and _inRange14_1
    priceLL14 = low[lbR] < ta.valuewhen(plFound14, low[lbR], 1)
    bullCond14 = plotBull and priceLL14 and oscHL14 and plFound14 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond14 else na, offset=-lbR, title='Regular Bullish 14 Label', text=' B14 ', style=shape.labelup, location=location.absolute, color=bullColor14, textcolor=textColor)
    _inRange14_2 = _inRange14(plFound14[1])
    oscLL14 = osc[lbR] < ta.valuewhen(plFound14, osc[lbR], 1) and _inRange14_2
    priceHL14 = low[lbR] > ta.valuewhen(plFound14, low[lbR], 1)
    hiddenBullCond14 = plotHiddenBull and priceHL14 and oscLL14 and plFound14 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond14 else na, offset=-lbR, title='Hidden Bullish 14 Label', text=' H B14 ', style=shape.labelup, location=location.absolute, color=bullColor14, textcolor=textColor)
    plFound15: Series = False if na(ta.pivotlow(osc, lbL15, lbR)) else True
    def _inRange15(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange15_1 = _inRange15(plFound15[1])
    oscHL15 = osc[lbR] > ta.valuewhen(plFound15, osc[lbR], 1) and _inRange15_1
    priceLL15 = low[lbR] < ta.valuewhen(plFound15, low[lbR], 1)
    bullCond15 = plotBull and priceLL15 and oscHL15 and plFound15 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond15 else na, offset=-lbR, title='Regular Bullish 15 Label', text=' B15 ', style=shape.labelup, location=location.absolute, color=bullColor15, textcolor=textColor)
    _inRange15_2 = _inRange15(plFound15[1])
    oscLL15 = osc[lbR] < ta.valuewhen(plFound15, osc[lbR], 1) and _inRange15_2
    priceHL15 = low[lbR] > ta.valuewhen(plFound15, low[lbR], 1)
    hiddenBullCond15 = plotHiddenBull and priceHL15 and oscLL15 and plFound15 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond15 else na, offset=-lbR, title='Hidden Bullish 15 Label', text=' H B15 ', style=shape.labelup, location=location.absolute, color=bullColor15, textcolor=textColor)
    plFound16: Series = False if na(ta.pivotlow(osc, lbL16, lbR)) else True
    def _inRange16(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange16_1 = _inRange16(plFound16[1])
    oscHL16 = osc[lbR] > ta.valuewhen(plFound16, osc[lbR], 1) and _inRange16_1
    priceLL16 = low[lbR] < ta.valuewhen(plFound16, low[lbR], 1)
    bullCond16 = plotBull and priceLL16 and oscHL16 and plFound16 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond16 else na, offset=-lbR, title='Regular Bullish 16 Label', text=' B16 ', style=shape.labelup, location=location.absolute, color=bullColor16, textcolor=textColor)
    _inRange16_2 = _inRange16(plFound16[1])
    oscLL16 = osc[lbR] < ta.valuewhen(plFound16, osc[lbR], 1) and _inRange16_2
    priceHL16 = low[lbR] > ta.valuewhen(plFound16, low[lbR], 1)
    hiddenBullCond16 = plotHiddenBull and priceHL16 and oscLL16 and plFound16 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond16 else na, offset=-lbR, title='Hidden Bullish 16 Label', text=' H B16 ', style=shape.labelup, location=location.absolute, color=bullColor16, textcolor=textColor)
    plFound17: Series = False if na(ta.pivotlow(osc, lbL17, lbR)) else True
    def _inRange17(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange17_1 = _inRange17(plFound17[1])
    oscHL17 = osc[lbR] > ta.valuewhen(plFound17, osc[lbR], 1) and _inRange17_1
    priceLL17 = low[lbR] < ta.valuewhen(plFound17, low[lbR], 1)
    bullCond17 = plotBull and priceLL17 and oscHL17 and plFound17 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond17 else na, offset=-lbR, title='Regular Bullish 17 Label', text=' B17 ', style=shape.labelup, location=location.absolute, color=bullColor17, textcolor=textColor)
    _inRange17_2 = _inRange17(plFound17[1])
    oscLL17 = osc[lbR] < ta.valuewhen(plFound17, osc[lbR], 1) and _inRange17_2
    priceHL17 = low[lbR] > ta.valuewhen(plFound17, low[lbR], 1)
    hiddenBullCond17 = plotHiddenBull and priceHL17 and oscLL17 and plFound17 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond17 else na, offset=-lbR, title='Hidden Bullish 17 Label', text=' H B17 ', style=shape.labelup, location=location.absolute, color=bullColor17, textcolor=textColor)
    plFound18: Series = False if na(ta.pivotlow(osc, lbL18, lbR)) else True
    def _inRange18(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange18_1 = _inRange18(plFound18[1])
    oscHL18 = osc[lbR] > ta.valuewhen(plFound18, osc[lbR], 1) and _inRange18_1
    priceLL18 = low[lbR] < ta.valuewhen(plFound18, low[lbR], 1)
    bullCond18 = plotBull and priceLL18 and oscHL18 and plFound18 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond18 else na, offset=-lbR, title='Regular Bullish 18 Label', text=' B18 ', style=shape.labelup, location=location.absolute, color=bullColor18, textcolor=textColor)
    _inRange18_2 = _inRange18(plFound18[1])
    oscLL18 = osc[lbR] < ta.valuewhen(plFound18, osc[lbR], 1) and _inRange18_2
    priceHL18 = low[lbR] > ta.valuewhen(plFound18, low[lbR], 1)
    hiddenBullCond18 = plotHiddenBull and priceHL18 and oscLL18 and plFound18 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond18 else na, offset=-lbR, title='Hidden Bullish 18 Label', text=' H B18 ', style=shape.labelup, location=location.absolute, color=bullColor18, textcolor=textColor)
    plFound19: Series = False if na(ta.pivotlow(osc, lbL19, lbR)) else True
    def _inRange19(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange19_1 = _inRange19(plFound19[1])
    oscHL19 = osc[lbR] > ta.valuewhen(plFound19, osc[lbR], 1) and _inRange19_1
    priceLL19 = low[lbR] < ta.valuewhen(plFound19, low[lbR], 1)
    bullCond19 = plotBull and priceLL19 and oscHL19 and plFound19 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond19 else na, offset=-lbR, title='Regular Bullish 19 Label', text=' B19 ', style=shape.labelup, location=location.absolute, color=bullColor19, textcolor=textColor)
    _inRange19_2 = _inRange19(plFound19[1])
    oscLL19 = osc[lbR] < ta.valuewhen(plFound19, osc[lbR], 1) and _inRange19_2
    priceHL19 = low[lbR] > ta.valuewhen(plFound19, low[lbR], 1)
    hiddenBullCond19 = plotHiddenBull and priceHL19 and oscLL19 and plFound19 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond19 else na, offset=-lbR, title='Hidden Bullish 19 Label', text=' H B19 ', style=shape.labelup, location=location.absolute, color=bullColor19, textcolor=textColor)
    plFound20: Series = False if na(ta.pivotlow(osc, lbL20, lbR)) else True
    def _inRange20(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange20_1 = _inRange20(plFound20[1])
    oscHL20 = osc[lbR] > ta.valuewhen(plFound20, osc[lbR], 1) and _inRange20_1
    priceLL20 = low[lbR] < ta.valuewhen(plFound20, low[lbR], 1)
    bullCond20 = plotBull and priceLL20 and oscHL20 and plFound20 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond20 else na, offset=-lbR, title='Regular Bullish 20 Label', text=' B20 ', style=shape.labelup, location=location.absolute, color=bullColor20, textcolor=textColor)
    _inRange20_2 = _inRange20(plFound20[1])
    oscLL20 = osc[lbR] < ta.valuewhen(plFound20, osc[lbR], 1) and _inRange20_2
    priceHL20 = low[lbR] > ta.valuewhen(plFound20, low[lbR], 1)
    hiddenBullCond20 = plotHiddenBull and priceHL20 and oscLL20 and plFound20 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond20 else na, offset=-lbR, title='Hidden Bullish 20 Label', text=' H B20 ', style=shape.labelup, location=location.absolute, color=bullColor20, textcolor=textColor)
    plFound21: Series = False if na(ta.pivotlow(osc, lbL21, lbR)) else True
    def _inRange21(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange21_1 = _inRange21(plFound21[1])
    oscHL21 = osc[lbR] > ta.valuewhen(plFound21, osc[lbR], 1) and _inRange21_1
    priceLL21 = low[lbR] < ta.valuewhen(plFound21, low[lbR], 1)
    bullCond21 = plotBull and priceLL21 and oscHL21 and plFound21 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond21 else na, offset=-lbR, title='Regular Bullish 21 Label', text=' B21 ', style=shape.labelup, location=location.absolute, color=bullColor21, textcolor=textColor)
    _inRange21_2 = _inRange21(plFound21[1])
    oscLL21 = osc[lbR] < ta.valuewhen(plFound21, osc[lbR], 1) and _inRange21_2
    priceHL21 = low[lbR] > ta.valuewhen(plFound21, low[lbR], 1)
    hiddenBullCond21 = plotHiddenBull and priceHL21 and oscLL21 and plFound21 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond21 else na, offset=-lbR, title='Hidden Bullish 21 Label', text=' H B21 ', style=shape.labelup, location=location.absolute, color=bullColor21, textcolor=textColor)
    plFound22: Series = False if na(ta.pivotlow(osc, lbL22, lbR)) else True
    def _inRange22(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange22_1 = _inRange22(plFound22[1])
    oscHL22 = osc[lbR] > ta.valuewhen(plFound22, osc[lbR], 1) and _inRange22_1
    priceLL22 = low[lbR] < ta.valuewhen(plFound22, low[lbR], 1)
    bullCond22 = plotBull and priceLL22 and oscHL22 and plFound22 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond22 else na, offset=-lbR, title='Regular Bullish 22 Label', text=' B22 ', style=shape.labelup, location=location.absolute, color=bullColor22, textcolor=textColor)
    _inRange22_2 = _inRange22(plFound22[1])
    oscLL22 = osc[lbR] < ta.valuewhen(plFound22, osc[lbR], 1) and _inRange22_2
    priceHL22 = low[lbR] > ta.valuewhen(plFound22, low[lbR], 1)
    hiddenBullCond22 = plotHiddenBull and priceHL22 and oscLL22 and plFound22 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond22 else na, offset=-lbR, title='Hidden Bullish 22 Label', text=' H B22 ', style=shape.labelup, location=location.absolute, color=bullColor22, textcolor=textColor)
    plFound23: Series = False if na(ta.pivotlow(osc, lbL23, lbR)) else True
    def _inRange23(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange23_1 = _inRange23(plFound23[1])
    oscHL23 = osc[lbR] > ta.valuewhen(plFound23, osc[lbR], 1) and _inRange23_1
    priceLL23 = low[lbR] < ta.valuewhen(plFound23, low[lbR], 1)
    bullCond23 = plotBull and priceLL23 and oscHL23 and plFound23 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond23 else na, offset=-lbR, title='Regular Bullish 23 Label', text=' B23 ', style=shape.labelup, location=location.absolute, color=bullColor23, textcolor=textColor)
    _inRange23_2 = _inRange23(plFound23[1])
    oscLL23 = osc[lbR] < ta.valuewhen(plFound23, osc[lbR], 1) and _inRange23_2
    priceHL23 = low[lbR] > ta.valuewhen(plFound23, low[lbR], 1)
    hiddenBullCond23 = plotHiddenBull and priceHL23 and oscLL23 and plFound23 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond23 else na, offset=-lbR, title='Hidden Bullish 23 Label', text=' H B23 ', style=shape.labelup, location=location.absolute, color=bullColor23, textcolor=textColor)
    plFound24: Series = False if na(ta.pivotlow(osc, lbL24, lbR)) else True
    def _inRange24(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange24_1 = _inRange24(plFound24[1])
    oscHL24 = osc[lbR] > ta.valuewhen(plFound24, osc[lbR], 1) and _inRange24_1
    priceLL24 = low[lbR] < ta.valuewhen(plFound24, low[lbR], 1)
    bullCond24 = plotBull and priceLL24 and oscHL24 and plFound24 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond24 else na, offset=-lbR, title='Regular Bullish 24 Label', text=' B24 ', style=shape.labelup, location=location.absolute, color=bullColor24, textcolor=textColor)
    _inRange24_2 = _inRange24(plFound24[1])
    oscLL24 = osc[lbR] < ta.valuewhen(plFound24, osc[lbR], 1) and _inRange24_2
    priceHL24 = low[lbR] > ta.valuewhen(plFound24, low[lbR], 1)
    hiddenBullCond24 = plotHiddenBull and priceHL24 and oscLL24 and plFound24 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond24 else na, offset=-lbR, title='Hidden Bullish 24 Label', text=' H B24 ', style=shape.labelup, location=location.absolute, color=bullColor24, textcolor=textColor)
    plFound25: Series = False if na(ta.pivotlow(osc, lbL25, lbR)) else True
    def _inRange25(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange25_1 = _inRange25(plFound25[1])
    oscHL25 = osc[lbR] > ta.valuewhen(plFound25, osc[lbR], 1) and _inRange25_1
    priceLL25 = low[lbR] < ta.valuewhen(plFound25, low[lbR], 1)
    bullCond25 = plotBull and priceLL25 and oscHL25 and plFound25 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond25 else na, offset=-lbR, title='Regular Bullish 25 Label', text=' B25 ', style=shape.labelup, location=location.absolute, color=bullColor25, textcolor=textColor)
    _inRange25_2 = _inRange25(plFound25[1])
    oscLL25 = osc[lbR] < ta.valuewhen(plFound25, osc[lbR], 1) and _inRange25_2
    priceHL25 = low[lbR] > ta.valuewhen(plFound25, low[lbR], 1)
    hiddenBullCond25 = plotHiddenBull and priceHL25 and oscLL25 and plFound25 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond25 else na, offset=-lbR, title='Hidden Bullish 25 Label', text=' H B25 ', style=shape.labelup, location=location.absolute, color=bullColor25, textcolor=textColor)
    plFound26: Series = False if na(ta.pivotlow(osc, lbL26, lbR)) else True
    def _inRange26(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange26_1 = _inRange26(plFound26[1])
    oscHL26 = osc[lbR] > ta.valuewhen(plFound26, osc[lbR], 1) and _inRange26_1
    priceLL26 = low[lbR] < ta.valuewhen(plFound26, low[lbR], 1)
    bullCond26 = plotBull and priceLL26 and oscHL26 and plFound26 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond26 else na, offset=-lbR, title='Regular Bullish 26 Label', text=' B26 ', style=shape.labelup, location=location.absolute, color=bullColor26, textcolor=textColor)
    _inRange26_2 = _inRange26(plFound26[1])
    oscLL26 = osc[lbR] < ta.valuewhen(plFound26, osc[lbR], 1) and _inRange26_2
    priceHL26 = low[lbR] > ta.valuewhen(plFound26, low[lbR], 1)
    hiddenBullCond26 = plotHiddenBull and priceHL26 and oscLL26 and plFound26 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond26 else na, offset=-lbR, title='Hidden Bullish 26 Label', text=' H B26 ', style=shape.labelup, location=location.absolute, color=bullColor26, textcolor=textColor)
    plFound27: Series = False if na(ta.pivotlow(osc, lbL27, lbR)) else True
    def _inRange27(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange27_1 = _inRange27(plFound27[1])
    oscHL27 = osc[lbR] > ta.valuewhen(plFound27, osc[lbR], 1) and _inRange27_1
    priceLL27 = low[lbR] < ta.valuewhen(plFound27, low[lbR], 1)
    bullCond27 = plotBull and priceLL27 and oscHL27 and plFound27 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond27 else na, offset=-lbR, title='Regular Bullish 27 Label ', text=' B27 ', style=shape.labelup, location=location.absolute, color=bullColor27, textcolor=textColor)
    _inRange27_2 = _inRange27(plFound27[1])
    oscLL27 = osc[lbR] < ta.valuewhen(plFound27, osc[lbR], 1) and _inRange27_2
    priceHL27 = low[lbR] > ta.valuewhen(plFound27, low[lbR], 1)
    hiddenBullCond27 = plotHiddenBull and priceHL27 and oscLL27 and plFound27 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond27 else na, offset=-lbR, title='Hidden Bullish 27 Label', text=' H B27 ', style=shape.labelup, location=location.absolute, color=bullColor27, textcolor=textColor)
    plFound28: Series = False if na(ta.pivotlow(osc, lbL28, lbR)) else True
    def _inRange28(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange28_1 = _inRange28(plFound28[1])
    oscHL28 = osc[lbR] > ta.valuewhen(plFound28, osc[lbR], 1) and _inRange28_1
    priceLL28 = low[lbR] < ta.valuewhen(plFound28, low[lbR], 1)
    bullCond28 = plotBull and priceLL28 and oscHL28 and plFound28 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond28 else na, offset=-lbR, title='Regular Bullish 28 Label ', text=' B28 ', style=shape.labelup, location=location.absolute, color=bullColor28, textcolor=textColor)
    _inRange28_2 = _inRange28(plFound28[1])
    oscLL28 = osc[lbR] < ta.valuewhen(plFound28, osc[lbR], 1) and _inRange28_2
    priceHL28 = low[lbR] > ta.valuewhen(plFound28, low[lbR], 1)
    hiddenBullCond28 = plotHiddenBull and priceHL28 and oscLL28 and plFound28 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond28 else na, offset=-lbR, title='Hidden Bullish 28 Label', text=' H B28 ', style=shape.labelup, location=location.absolute, color=bullColor28, textcolor=textColor)
    plFound29: Series = False if na(ta.pivotlow(osc, lbL29, lbR)) else True
    def _inRange29(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange29_1 = _inRange29(plFound29[1])
    oscHL29 = osc[lbR] > ta.valuewhen(plFound29, osc[lbR], 1) and _inRange29_1
    priceLL29 = low[lbR] < ta.valuewhen(plFound29, low[lbR], 1)
    bullCond29 = plotBull and priceLL29 and oscHL29 and plFound29 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond29 else na, offset=-lbR, title='Regular Bullish 29 Label ', text=' B29 ', style=shape.labelup, location=location.absolute, color=bullColor29, textcolor=textColor)
    _inRange29_2 = _inRange29(plFound29[1])
    oscLL29 = osc[lbR] < ta.valuewhen(plFound29, osc[lbR], 1) and _inRange29_2
    priceHL29 = low[lbR] > ta.valuewhen(plFound29, low[lbR], 1)
    hiddenBullCond29 = plotHiddenBull and priceHL29 and oscLL29 and plFound29 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond29 else na, offset=-lbR, title='Hidden Bullish 29 Label', text=' H B29 ', style=shape.labelup, location=location.absolute, color=bullColor29, textcolor=textColor)
    plFound30: Series = False if na(ta.pivotlow(osc, lbL30, lbR)) else True
    def _inRange30(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange30_1 = _inRange30(plFound30[1])
    oscHL30 = osc[lbR] > ta.valuewhen(plFound30, osc[lbR], 1) and _inRange30_1
    priceLL30 = low[lbR] < ta.valuewhen(plFound30, low[lbR], 1)
    bullCond30 = plotBull and priceLL30 and oscHL30 and plFound30 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if bullCond30 else na, offset=-lbR, title='Regular Bullish 30 Label ', text=' B30 ', style=shape.labelup, location=location.absolute, color=bullColor30, textcolor=textColor)
    _inRange30_2 = _inRange30(plFound30[1])
    oscLL30 = osc[lbR] < ta.valuewhen(plFound30, osc[lbR], 1) and _inRange30_2
    priceHL30 = low[lbR] > ta.valuewhen(plFound30, low[lbR], 1)
    hiddenBullCond30 = plotHiddenBull and priceHL30 and oscLL30 and plFound30 and RSIwasBelowOS and isWithinLongRanges and (not enableonlyOneLB)
    plotshape(osc[lbR] if hiddenBullCond30 else na, offset=-lbR, title='Hidden Bullish 30 Label', text=' H B30 ', style=shape.labelup, location=location.absolute, color=bullColor30, textcolor=textColor)
    combibullCond = bullCond1 or bullCond2 or bullCond3 or bullCond4 or bullCond5 or bullCond6 or bullCond7 or bullCond8 or bullCond9 or bullCond10 or bullCond11 or bullCond12 or bullCond13 or bullCond14 or bullCond15 or bullCond16 or bullCond17 or bullCond18 or bullCond19 or bullCond20 or bullCond21 or bullCond22 or bullCond23 or bullCond24 or bullCond25 or bullCond26 or bullCond27 or bullCond28 or bullCond29 or bullCond30
    combihiddenBullCond = hiddenBullCond1 or hiddenBullCond2 or hiddenBullCond3 or hiddenBullCond4 or hiddenBullCond5 or hiddenBullCond6 or hiddenBullCond7 or hiddenBullCond8 or hiddenBullCond9 or hiddenBullCond10 or hiddenBullCond11 or hiddenBullCond12 or hiddenBullCond13 or hiddenBullCond14 or hiddenBullCond15 or hiddenBullCond16 or hiddenBullCond17 or hiddenBullCond18 or hiddenBullCond19 or hiddenBullCond20 or hiddenBullCond21 or hiddenBullCond22 or hiddenBullCond23 or hiddenBullCond24 or hiddenBullCond25 or hiddenBullCond26 or hiddenBullCond27 or hiddenBullCond28 or hiddenBullCond29 or hiddenBullCond30
    barssince_1 = ta.barssince(combihiddenBullCond or combibullCond)
    oscCross = 1 < osc - oscema and barssince_1 <= oscCrosslookback or not enableOscCross
    EmaIsBroken = ta.ema(src, WaitForEmaBreakLen) < close or not enableWaitForEmaBreak
    priceBounced = priceBounceNeeded < ta.highest(high, 1) - ta.lowest(low, priceBounceNeededLbL) or not enablepriceBounceNeeded
    delaysEnabled = enablepriceBounceNeeded or enableOscCross or enableWaitForEmaBreak
    DelayState = oscCross and EmaIsBroken and priceBounced
    barssince_2 = ta.barssince(combihiddenBullCond)
    HiddenBullAndBounce0 = DelayState and barssince_2 == 0
    barssince_3 = ta.barssince(combihiddenBullCond)
    barssince_4 = ta.barssince(HiddenBullAndBounce0)
    HiddenBullAndBounce1 = DelayState and barssince_3 == 1 and (not barssince_4 < 1)
    barssince_5 = ta.barssince(combihiddenBullCond)
    barssince_6 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0)
    HiddenBullAndBounce2 = DelayState and barssince_5 == 2 and (not barssince_6 < 2)
    barssince_7 = ta.barssince(combihiddenBullCond)
    barssince_8 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2)
    HiddenBullAndBounce3 = DelayState and barssince_7 == 3 and (not barssince_8 < 3)
    barssince_9 = ta.barssince(combihiddenBullCond)
    barssince_10 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3)
    HiddenBullAndBounce4 = DelayState and barssince_9 == 4 and (not barssince_10 < 5)
    barssince_11 = ta.barssince(combihiddenBullCond)
    barssince_12 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4)
    HiddenBullAndBounce5 = DelayState and barssince_11 == 5 and (not barssince_12 < 6)
    barssince_13 = ta.barssince(combihiddenBullCond)
    barssince_14 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5)
    HiddenBullAndBounce6 = DelayState and barssince_13 == 6 and (not barssince_14 < 7)
    barssince_15 = ta.barssince(combihiddenBullCond)
    barssince_16 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5 or HiddenBullAndBounce6)
    HiddenBullAndBounce7 = DelayState and barssince_15 == 7 and (not barssince_16 < 8)
    barssince_17 = ta.barssince(combihiddenBullCond)
    barssince_18 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5 or HiddenBullAndBounce6 or HiddenBullAndBounce7)
    HiddenBullAndBounce8 = DelayState and barssince_17 == 8 and (not barssince_18 < 9)
    barssince_19 = ta.barssince(combihiddenBullCond)
    barssince_20 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5 or HiddenBullAndBounce6 or HiddenBullAndBounce7 or HiddenBullAndBounce8)
    HiddenBullAndBounce9 = DelayState and barssince_19 == 9 and (not barssince_20 < 10)
    barssince_21 = ta.barssince(combihiddenBullCond)
    barssince_22 = ta.barssince(HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5 or HiddenBullAndBounce6 or HiddenBullAndBounce7 or HiddenBullAndBounce8 or HiddenBullAndBounce9)
    HiddenBullAndBounce10 = DelayState and barssince_21 == 10 and (not barssince_22 < 11)
    FinalHiddenBullDelayAlert = delaysEnabled and (HiddenBullAndBounce1 or HiddenBullAndBounce0 or HiddenBullAndBounce2 or HiddenBullAndBounce3 or HiddenBullAndBounce4 or HiddenBullAndBounce5 or HiddenBullAndBounce6 or HiddenBullAndBounce7 or HiddenBullAndBounce8 or HiddenBullAndBounce9 or HiddenBullAndBounce10)
    FinalHiddenBullAlert: bool = False
    FinalHiddenBullAlert2: bool = False
    if delaysEnabled:
        FinalHiddenBullAlert = FinalHiddenBullDelayAlert
        FinalHiddenBullAlert2 = False
    if not delaysEnabled:
        FinalHiddenBullAlert = False
        FinalHiddenBullAlert2 = combihiddenBullCond
    barssince_23 = ta.barssince(combibullCond)
    BullAndBounce0 = DelayState and barssince_23 == 0
    barssince_24 = ta.barssince(combibullCond)
    barssince_25 = ta.barssince(BullAndBounce0)
    BullAndBounce1 = DelayState and barssince_24 == 1 and (not barssince_25 < 2)
    barssince_26 = ta.barssince(combibullCond)
    barssince_27 = ta.barssince(BullAndBounce1 or BullAndBounce0)
    BullAndBounce2 = DelayState and barssince_26 == 2 and (not barssince_27 < 3)
    barssince_28 = ta.barssince(combibullCond)
    barssince_29 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2)
    BullAndBounce3 = DelayState and barssince_28 == 3 and (not barssince_29 < 4)
    barssince_30 = ta.barssince(combibullCond)
    barssince_31 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3)
    BullAndBounce4 = DelayState and barssince_30 == 4 and (not barssince_31 < 5)
    barssince_32 = ta.barssince(combibullCond)
    barssince_33 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4)
    BullAndBounce5 = DelayState and barssince_32 == 5 and (not barssince_33 < 6)
    barssince_34 = ta.barssince(combibullCond)
    barssince_35 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5)
    BullAndBounce6 = DelayState and barssince_34 == 6 and (not barssince_35 < 7)
    barssince_36 = ta.barssince(combibullCond)
    barssince_37 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5 or BullAndBounce6)
    BullAndBounce7 = DelayState and barssince_36 == 7 and (not barssince_37 < 8)
    barssince_38 = ta.barssince(combibullCond)
    barssince_39 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5 or BullAndBounce6 or BullAndBounce7)
    BullAndBounce8 = DelayState and barssince_38 == 8 and (not barssince_39 < 9)
    barssince_40 = ta.barssince(combibullCond)
    barssince_41 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5 or BullAndBounce6 or BullAndBounce7 or BullAndBounce8)
    BullAndBounce9 = DelayState and barssince_40 == 9 and (not barssince_41 < 10)
    barssince_42 = ta.barssince(combibullCond)
    barssince_43 = ta.barssince(BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5 or BullAndBounce6 or BullAndBounce7 or BullAndBounce8 or BullAndBounce9)
    BullAndBounce10 = DelayState and barssince_42 == 10 and (not barssince_43 < 11)
    FinalBullDelayAlert = delaysEnabled and (BullAndBounce1 or BullAndBounce0 or BullAndBounce2 or BullAndBounce3 or BullAndBounce4 or BullAndBounce5 or BullAndBounce6 or BullAndBounce7 or BullAndBounce8 or BullAndBounce9 or BullAndBounce10)
    FinalBullAlert: bool = False
    FinalBullAlert2: bool = False
    if delaysEnabled:
        FinalBullAlert = FinalBullDelayAlert
        FinalBullAlert2 = False
    if not delaysEnabled:
        FinalBullAlert = False
        FinalBullAlert2 = combibullCond
    plotshape(osc if FinalBullAlert else na, offset=0, title='Buy ', text=' buy ', style=shape.labelup, location=location.absolute, color=color.lime, textcolor=textColor)
    lowPBuffer = __input_91__ / 100
    longSlLow = NA(float)
    if whichOffset == 'use % as offset' and whichSL == 'use the low as SL' and enableSL:
        longSlLow = ta.lowest(low, SlLowLookback) * (1 - lowPBuffer)
    if whichOffset == 'use $ as offset' and whichSL == 'use the low as SL' and enableSL:
        longSlLow = ta.lowest(low, SlLowLookback) - lowDBuffer
    longStopLoss = __input_94__ / 100
    longTakeProfit1 = __input_95__ / 100
    veryFinalAlert = FinalHiddenBullAlert2 or FinalHiddenBullAlert or FinalBullAlert or FinalBullAlert2
    alertFreq = alert.freq_once_per_bar if selectalertFreq == 'once per bar' else alert.freq_once_per_bar_close if selectalertFreq == 'once per bar close' else alert.freq_all if selectalertFreq == 'all' else na
    if not enableSlMessage and veryFinalAlert:
        alert(string.tostring(BuyAlertMessage), alertFreq)
    if enableSlMessage and veryFinalAlert:
        alert(string.tostring(BuyAlertMessage) + string.tostring(longSlLow) + string.tostring(AfterSLMessage), alertFreq)
    if enableSlMessage:
        alert(string.tostring(BuyAlertMessage) + string.tostring(longSlLow) + string.tostring(AfterSLMessage), alertFreq)
    alertcondition(veryFinalAlert, title='Bullish divergence', message='Bull Div {{ticker}}')
    shortTrading: bool = False
    longTrading = plotBull or plotHiddenBull
    longTP1 = strategy.position_avg_price * (1 + longTakeProfit1) if strategy.position_size > 0 else strategy.position_avg_price * (1 - longTakeProfit1) if strategy.position_size < 0 else na
    longSL = strategy.position_avg_price * (1 - longStopLoss) if strategy.position_size > 0 else strategy.position_avg_price * (1 + longStopLoss) if strategy.position_size < 0 else na
    strategy.risk.allow_entry_in(strategy.direction.all if longTrading == True and shortTrading == True else strategy.direction.long if longTrading == True else strategy.direction.short if shortTrading == True else na)
    if FinalBullAlert or FinalBullAlert2:
        strategy.entry('Bull', strategy.long, comment='B Long')
    if FinalHiddenBullAlert2 or FinalHiddenBullAlert:
        strategy.entry('Bull', strategy.long, comment='HB Long')
    if enableSL and whichSL == 'use the static % as SL':
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1, stop=longSL)
    def barsSinceLastEntry():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    barssince_44 = ta.barssince(veryFinalAlert)
    barsSinceLastEntry_1 = barsSinceLastEntry()
    if enableSL and whichSL == 'use the low as SL' and (barssince_44 < 2) and (barsSinceLastEntry_1 < 2):
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1, stop=longSlLow)
    if not enableSL:
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
