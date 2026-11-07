"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, barstate, bgcolor, close, color, high, input, low, na, ohlc4,
    open, plot, position, script, size, strategy, string, syminfo, ta, table, text, time,
    timeframe, volume
)
from pynecore.types import Persistent, Series, Table
import lib.Peter_O.MTFindicators.v8 as MTFLIBRARY

tooltipValue: str = "4th field is used only if 'value' is selected in the 3rd dropdown. " + 'Otherwise it is ignored and value of indicator selected in 3rd dropdown is used. '
tooltipCustomIndicator: str = 'Custom indicator or series has to be selected here, so you can use it entry conditions dropdowns.' + 'Read this script description to see example use.'
tooltipMTF: str = 'MTF is timeframe multiplayer. ' + 'For example, it you want to use RSI from 4h chart, being on 1h chart, you should enter 4 here. ' + 'This refers to all MTF parameters in this section.'
tooltipKeltner: str = 'Keltner Channels settings: Basis Length, ATR Length, Multiplier, MTF x. Sorry, didn\'t fit in single line :)'
tooltipMACD: str = 'MACD settings: Fast Length, Slow Length, Signal Length, MTF x. Sorry, didn\'t fit in single line :)'
longEntryGroup: str = 'Long Entry - when all conditions are jointly true/skipped'
shortEntryGroup: str = 'Short Entry - when all conditions are jointly true/skipped'
CrossingUpOption: str = 'Crossing Up'
CrossingDownOption: str = 'Crossing Down'
GreaterThanOption: str = 'Greater Than'
LessThanOption: str = 'Less Than'
skipOption: str = '...SKIP...'
openOption: str = 'open'
highOption: str = 'high'
lowOption: str = 'low'
closeOption: str = 'close'
ohlc4Option: str = 'ohlc4'
valueOption: str = 'value'
rsiAOption: str = 'rsiA'
rsiBOption: str = 'rsiB'
rsiCOption: str = 'rsiC'
maAOption: str = 'maA (Moving Average A)'
maBOption: str = 'maB (Moving Average B)'
maCOption: str = 'maC (Moving Average C)'
adxOption: str = 'ADX'
diPlusOption: str = 'DI-Plus'
diMinusOption: str = 'DI-Minus'
stochKOption: str = 'Stoch%K'
stochDOption: str = 'Stoch%D'
bbBasisOption: str = 'Basis Bollinger Band'
bbUpperOption: str = 'Upper Bollinger Band'
bbLowerOption: str = 'Lower Bollinger Band'
kcUpperOption: str = 'Upper Keltner Channel Band'
kcLowerOption: str = 'Lower Keltner Channel Band'
macdOption: str = 'MACD'
macdSignalOption: str = 'MACD Signal'
macdHistOption: str = 'MACD Histogram'
volumeOption: str = 'volume'
volumeMAOption: str = 'volumeMA'
customIndicatorOption: str = 'custom indicator'
exitSettingsGroup: str = 'Exit settings'
bracketPercent: str = 'Percent'
bracketATR: str = 'ATR'
bracketPoints: str = 'Points'
timeSettingsGroup: str = 'Time Settings'
indicatorDefinitionsGroup: str = 'Indicator Definitions'
emaOption: str = 'EMA'
smaOption: str = 'SMA'
wmaOption: str = 'WMA'
vwmaOption: str = 'VWMA'
hmaOption: str = 'HMA'
rmaOption: str = 'RMA'
demaOption: str = 'DEMA'


@script.strategy('Joint Conditions Strategy Suite + TradingConnector alerts bot', shorttitle='JCSS+TradingConnector bot', overlay=True, margin_long=100, margin_short=100, close_entries_rule='ANY', default_qty_type=strategy.fixed, default_qty_value=100, commission_type=strategy.commission.cash_per_order, commission_value=0.0003, initial_capital=1000000, close_by_id=True)
def main(
    longIndicatorSelector1=input.string(defval=maBOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond1long', group=longEntryGroup),
    longConditionTrigger1=input.string(defval=CrossingUpOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond1long', group=longEntryGroup),
    longLevelSelector1=input.string(defval=maCOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond1long', group=longEntryGroup),
    longLevelValue1=input.float(defval=0.0, title='', inline='cond1long', group=longEntryGroup, tooltip=tooltipValue),
    longIndicatorSelector2=input.string(defval=macdHistOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='and', inline='cond2long', group=longEntryGroup),
    longConditionTrigger2=input.string(defval=GreaterThanOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond2long', group=longEntryGroup),
    longLevelSelector2=input.string(defval=valueOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond2long', group=longEntryGroup),
    longLevelValue2=input.float(defval=0.0, title='', inline='cond2long', group=longEntryGroup),
    longIndicatorSelector3=input.string(defval=adxOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='and', inline='cond3long', group=longEntryGroup),
    longConditionTrigger3=input.string(defval=GreaterThanOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond3long', group=longEntryGroup),
    longLevelSelector3=input.string(defval=valueOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond3long', group=longEntryGroup),
    longLevelValue3=input.float(defval=25.0, title='', inline='cond3long', group=longEntryGroup),
    shortIndicatorSelector1=input.string(defval=maBOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond1short', group=shortEntryGroup),
    shortConditionTrigger1=input.string(defval=CrossingDownOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond1short', group=shortEntryGroup),
    shortLevelSelector1=input.string(defval=maCOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond1short', group=shortEntryGroup),
    shortLevelValue1=input.float(defval=0.0, title='', inline='cond1short', group=shortEntryGroup),
    shortIndicatorSelector2=input.string(defval=macdHistOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='and', inline='cond2short', group=shortEntryGroup),
    shortConditionTrigger2=input.string(defval=LessThanOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond2short', group=shortEntryGroup),
    shortLevelSelector2=input.string(defval=valueOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond2short', group=shortEntryGroup),
    shortLevelValue2=input.float(defval=0.0, title='', inline='cond2short', group=shortEntryGroup),
    shortIndicatorSelector3=input.string(defval=adxOption, options=(skipOption, openOption, highOption, lowOption, closeOption, ohlc4Option, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='and', inline='cond3short', group=shortEntryGroup),
    shortConditionTrigger3=input.string(defval=GreaterThanOption, options=(CrossingUpOption, CrossingDownOption, GreaterThanOption, LessThanOption), title='', inline='cond3short', group=shortEntryGroup),
    shortLevelSelector3=input.string(defval=valueOption, options=(valueOption, rsiAOption, rsiBOption, rsiCOption, maAOption, maBOption, maCOption, adxOption, diPlusOption, diMinusOption, stochKOption, stochDOption, bbBasisOption, bbUpperOption, bbLowerOption, kcUpperOption, kcLowerOption, macdOption, macdSignalOption, macdHistOption, volumeOption, volumeMAOption, customIndicatorOption), title='', inline='cond3short', group=shortEntryGroup),
    shortLevelValue3=input.float(defval=25.0, title='', inline='cond3short', group=shortEntryGroup),
    tpType=input.string(title='Take profit type', defval=bracketPoints, options=(bracketPercent, bracketATR, bracketPoints), inline='takeprofit', group=exitSettingsGroup),
    tpValue=input.float(title='Take profit', step=0.1, minval=0.1, defval=100, inline='takeprofit', group=exitSettingsGroup),
    slType=input.string(title='Stop Loss type', defval=bracketPoints, options=(bracketPercent, bracketATR, bracketPoints), inline='stoploss', group=exitSettingsGroup),
    slValue=input.float(title='Stop Loss', step=0.1, minval=0.1, defval=100, inline='stoploss', group=exitSettingsGroup),
    enableTrailing=input.bool(title='Enable Trailing Stop', defval=False, inline='trailing', group=exitSettingsGroup),
    trailTriggerInput=input.int(title='  Trigger', minval=1, defval=80, inline='trailing', group=exitSettingsGroup),
    trailOffsetInput=input.int(title='Offset', minval=1, defval=10, inline='trailing', group=exitSettingsGroup),
    filterTradingTimes=input.bool(True, title='Trade Only Within Sessions', inline='times', group=timeSettingsGroup),
    tradingTimes=input.session('0900-1600', title='', inline='times', group=timeSettingsGroup),
    customIndicator: Series[float] = input.source(close, title='Custom Indicator aka Imported Source', group=indicatorDefinitionsGroup, inline='custom', tooltip=tooltipCustomIndicator),
    rsiA_source=input.string(defval=closeOption, title='rsiA', options=(openOption, highOption, lowOption, closeOption, ohlc4Option), group=indicatorDefinitionsGroup, inline='rsiA'),
    rsiA_length=input.int(defval=5, title='', group=indicatorDefinitionsGroup, inline='rsiA'),
    rsiA_mtf=input.int(defval=1, title='mtf', group=indicatorDefinitionsGroup, inline='rsiA', tooltip=tooltipMTF),
    rsiB_source=input.string(defval=closeOption, title='rsiB', options=(openOption, highOption, lowOption, closeOption, ohlc4Option), group=indicatorDefinitionsGroup, inline='rsiB'),
    rsiB_length=input.int(defval=14, title='', group=indicatorDefinitionsGroup, inline='rsiB'),
    rsiB_mtf=input.int(defval=1, title='mtf', group=indicatorDefinitionsGroup, inline='rsiB'),
    rsiC_source=input.string(defval=closeOption, title='rsiC', options=(openOption, highOption, lowOption, closeOption, ohlc4Option), group=indicatorDefinitionsGroup, inline='rsiC'),
    rsiC_length=input.int(defval=23, title='', group=indicatorDefinitionsGroup, inline='rsiC'),
    rsiC_mtf=input.int(defval=1, title='mtf', group=indicatorDefinitionsGroup, inline='rsiC'),
    maA_type=input.string(title='MaA', defval=emaOption, options=(emaOption, smaOption, wmaOption, vwmaOption, hmaOption, rmaOption, demaOption), inline='maA', group=indicatorDefinitionsGroup),
    maA_source=input.string(defval=closeOption, options=(openOption, highOption, lowOption, closeOption, ohlc4Option), title='', inline='maA', group=indicatorDefinitionsGroup),
    maA_length=input.int(defval=9, title='', inline='maA', group=indicatorDefinitionsGroup),
    maA_mtf=input.int(defval=1, title='mtf', inline='maA', group=indicatorDefinitionsGroup),
    maB_type=input.string(title='MaB', defval=emaOption, options=(emaOption, smaOption, wmaOption, vwmaOption, hmaOption, rmaOption, demaOption), inline='maB', group=indicatorDefinitionsGroup),
    maB_source=input.string(defval=closeOption, options=(openOption, highOption, lowOption, closeOption, ohlc4Option), title='', inline='maB', group=indicatorDefinitionsGroup),
    maB_length=input.int(defval=50, title='', inline='maB', group=indicatorDefinitionsGroup),
    maB_mtf=input.int(defval=1, title='mtf', inline='maB', group=indicatorDefinitionsGroup),
    maC_type=input.string(title='MaC', defval=emaOption, options=(emaOption, smaOption, wmaOption, vwmaOption, hmaOption, rmaOption, demaOption), inline='maC', group=indicatorDefinitionsGroup),
    maC_source=input.string(defval=closeOption, options=(openOption, highOption, lowOption, closeOption, ohlc4Option), title='', inline='maC', group=indicatorDefinitionsGroup),
    maC_length=input.int(defval=200, title='', inline='maC', group=indicatorDefinitionsGroup),
    maC_mtf=input.int(defval=1, title='mtf', inline='maC', group=indicatorDefinitionsGroup),
    diLength=input.int(defval=14, title='ADX-DMI', minval=1, maxval=50, inline='adx', group=indicatorDefinitionsGroup),
    adxLength=input.int(defval=14, minval=1, title='DI Length', inline='adx', group=indicatorDefinitionsGroup),
    mtf4adx=input.int(defval=1, title='mtf', inline='adx', group=indicatorDefinitionsGroup),
    periodK=input.int(defval=14, title='Stch', minval=1, inline='stoch', group=indicatorDefinitionsGroup),
    smoothK=input.int(defval=3, title='', minval=1, inline='stoch', group=indicatorDefinitionsGroup),
    periodD=input.int(defval=3, title='', minval=1, inline='stoch', group=indicatorDefinitionsGroup),
    mtf4stoch=input.int(defval=1, title='mtf', inline='stoch', group=indicatorDefinitionsGroup),
    bbLength=input.int(defval=20, minval=1, title='BB', inline='bbands', group=indicatorDefinitionsGroup),
    bbSource=input.string(defval=closeOption, options=(openOption, highOption, lowOption, closeOption, ohlc4Option), title='', inline='bbands', group=indicatorDefinitionsGroup),
    bbMult=input.float(defval=2.0, minval=0.001, maxval=50, title='σ', inline='bbands', group=indicatorDefinitionsGroup),
    mtf4bb=input.int(defval=1, title='mtf', inline='bbands', group=indicatorDefinitionsGroup),
    kcLength=input.int(defval=13, minval=1, title='KC', inline='keltner', group=indicatorDefinitionsGroup, tooltip=tooltipKeltner),
    kcAtrLength=input.int(defval=13, minval=1, title='', inline='keltner', group=indicatorDefinitionsGroup),
    kcMult=input.float(defval=1.5, minval=0.01, maxval=50, title='', inline='keltner', group=indicatorDefinitionsGroup),
    mtf4keltner=input.int(defval=1, title='', inline='keltner', group=indicatorDefinitionsGroup),
    macdFastLength=input.int(defval=12, title='MC', inline='macd', group=indicatorDefinitionsGroup, tooltip=tooltipMACD),
    macdSlowLength=input.int(defval=26, title='', inline='macd', group=indicatorDefinitionsGroup),
    macdSignalLength=input.int(defval=9, title='', minval=1, maxval=50, inline='macd', group=indicatorDefinitionsGroup),
    mtf4macd=input.int(defval=1, title='', inline='macd', group=indicatorDefinitionsGroup)
):
    trailPoints = na if enableTrailing == False else trailTriggerInput
    trailOffset = na if enableTrailing == False else trailOffsetInput
    SL = slValue * close / 100 if slType == bracketPercent else ta.atr(14) * slValue if slType == bracketATR else slValue
    TP = tpValue * close / 100 if tpType == bracketPercent else ta.atr(14) * tpValue if tpType == bracketATR else tpValue
    isTradingSession = not na(time(timeframe.period, tradingTimes)) if filterTradingTimes else True
    time_1 = time(timeframe.period, tradingTimes)
    bgcolor(color.new(color.black, 85) if filterTradingTimes and na(time_1) else na, title='Not in Trading Session')
    kcSource = close
    macdSource = close
    def convertSource(sourceInput):
        out = close if sourceInput == closeOption else open if sourceInput == openOption else high if sourceInput == highOption else low if sourceInput == lowOption else ohlc4 if sourceInput == ohlc4Option else close
        return out

    maA = MTFLIBRARY.moving_average_mtf(maA_mtf, maA_type, convertSource(maA_source), maA_length)
    maB = MTFLIBRARY.moving_average_mtf(maB_mtf, maB_type, convertSource(maB_source), maB_length)
    maC = MTFLIBRARY.moving_average_mtf(maC_mtf, maC_type, convertSource(maC_source), maC_length)
    rsiA = MTFLIBRARY.rsi_mtf(rsiA_mtf, convertSource(rsiA_source), rsiA_length)
    rsiB = MTFLIBRARY.rsi_mtf(rsiB_mtf, convertSource(rsiB_source), rsiB_length)
    rsiC = MTFLIBRARY.rsi_mtf(rsiC_mtf, convertSource(rsiC_source), rsiC_length)
    adx, diPlus, diMinus = MTFLIBRARY.adx_mtf(mtf4adx, adxLength, diLength)
    stochK, stochD = MTFLIBRARY.stoch_mtf(mtf4stoch, periodK, smoothK, periodD)
    bbBasis, bbUpper, bbLower = MTFLIBRARY.bollingerbands_mtf(mtf4bb, bbLength, convertSource(bbSource), bbMult)
    kcUpper, kcLower = MTFLIBRARY.keltnerchannels_mtf(mtf4keltner, kcSource, kcLength, kcAtrLength, kcMult)
    macd, macdSignal, macdHist = MTFLIBRARY.macd_mtf(mtf4macd, macdSource, macdFastLength, macdSlowLength, macdSignalLength)
    volumeMA = ta.ema(volume, 20)
    def getIndicator(selectionInput):
        out = open if selectionInput == openOption else high if selectionInput == highOption else low if selectionInput == lowOption else close if selectionInput == closeOption else ohlc4 if selectionInput == ohlc4Option else rsiA if selectionInput == rsiAOption else rsiB if selectionInput == rsiBOption else rsiC if selectionInput == rsiCOption else maA if selectionInput == maAOption else maB if selectionInput == maBOption else maC if selectionInput == maCOption else adx if selectionInput == adxOption else diPlus if selectionInput == diPlusOption else diMinus if selectionInput == diMinusOption else stochK if selectionInput == stochKOption else stochD if selectionInput == stochDOption else bbBasis if selectionInput == bbBasisOption else bbUpper if selectionInput == bbUpperOption else bbLower if selectionInput == bbLowerOption else kcUpper if selectionInput == kcUpperOption else kcLower if selectionInput == kcLowerOption else macd if selectionInput == macdOption else macdSignal if selectionInput == macdSignalOption else macdHist if selectionInput == macdHistOption else volume if selectionInput == volumeOption else volumeMA if selectionInput == volumeMAOption else customIndicator if selectionInput == customIndicatorOption else close
        return out

    def getIndicatorIfSelected(selectionInput, selectionValue):
        out = rsiA if selectionInput == rsiAOption else rsiB if selectionInput == rsiBOption else rsiC if selectionInput == rsiCOption else maA if selectionInput == maAOption else maB if selectionInput == maBOption else maC if selectionInput == maCOption else adx if selectionInput == adxOption else diPlus if selectionInput == diPlusOption else diMinus if selectionInput == diMinusOption else stochK if selectionInput == stochKOption else stochD if selectionInput == stochDOption else bbBasis if selectionInput == bbBasisOption else bbUpper if selectionInput == bbUpperOption else bbLower if selectionInput == bbLowerOption else kcUpper if selectionInput == kcUpperOption else kcLower if selectionInput == kcLowerOption else macd if selectionInput == macdOption else macdSignal if selectionInput == macdSignalOption else macdHist if selectionInput == macdHistOption else volume if selectionInput == volumeOption else volumeMA if selectionInput == volumeMAOption else customIndicator if selectionInput == customIndicatorOption else selectionValue
        return out

    longIndicator1 = getIndicator(longIndicatorSelector1)
    longLevel1 = getIndicatorIfSelected(longLevelSelector1, longLevelValue1)
    longIndicator2 = getIndicator(longIndicatorSelector2)
    longLevel2 = getIndicatorIfSelected(longLevelSelector2, longLevelValue2)
    longIndicator3 = getIndicator(longIndicatorSelector3)
    longLevel3 = getIndicatorIfSelected(longLevelSelector3, longLevelValue3)
    shortIndicator1 = getIndicator(shortIndicatorSelector1)
    shortLevel1 = getIndicatorIfSelected(shortLevelSelector1, shortLevelValue1)
    shortIndicator2 = getIndicator(shortIndicatorSelector2)
    shortLevel2 = getIndicatorIfSelected(shortLevelSelector2, shortLevelValue2)
    shortIndicator3 = getIndicator(shortIndicatorSelector3)
    shortLevel3 = getIndicatorIfSelected(shortLevelSelector3, shortLevelValue3)
    GoLong1 = ta.crossover(longIndicator1, longLevel1) if longConditionTrigger1 == CrossingUpOption else ta.crossunder(longIndicator1, longLevel1) if longConditionTrigger1 == CrossingDownOption else longIndicator1 > longLevel1 if longConditionTrigger1 == GreaterThanOption else longIndicator1 < longLevel1 if longConditionTrigger1 == LessThanOption else True
    GoLong2 = ta.crossover(longIndicator2, longLevel2) if longConditionTrigger2 == CrossingUpOption else ta.crossunder(longIndicator2, longLevel2) if longConditionTrigger2 == CrossingDownOption else longIndicator2 > longLevel2 if longConditionTrigger2 == GreaterThanOption else longIndicator2 < longLevel2 if longConditionTrigger2 == LessThanOption else True
    GoLong3 = ta.crossover(longIndicator3, longLevel3) if longConditionTrigger3 == CrossingUpOption else ta.crossunder(longIndicator3, longLevel3) if longConditionTrigger3 == CrossingDownOption else longIndicator3 > longLevel3 if longConditionTrigger3 == GreaterThanOption else longIndicator3 < longLevel3 if longConditionTrigger3 == LessThanOption else True
    GoShort1 = ta.crossover(shortIndicator1, shortLevel1) if shortConditionTrigger1 == CrossingUpOption else ta.crossunder(shortIndicator1, shortLevel1) if shortConditionTrigger1 == CrossingDownOption else shortIndicator1 > shortLevel1 if shortConditionTrigger1 == GreaterThanOption else shortIndicator1 < shortLevel1 if shortConditionTrigger1 == LessThanOption else True
    GoShort2 = ta.crossover(shortIndicator2, shortLevel2) if shortConditionTrigger2 == CrossingUpOption else ta.crossunder(shortIndicator2, shortLevel2) if shortConditionTrigger2 == CrossingDownOption else shortIndicator2 > shortLevel2 if shortConditionTrigger2 == GreaterThanOption else shortIndicator2 < shortLevel2 if shortConditionTrigger2 == LessThanOption else True
    GoShort3 = ta.crossover(shortIndicator3, shortLevel3) if shortConditionTrigger3 == CrossingUpOption else ta.crossunder(shortIndicator3, shortLevel3) if shortConditionTrigger3 == CrossingDownOption else shortIndicator3 > shortLevel3 if shortConditionTrigger3 == GreaterThanOption else shortIndicator3 < shortLevel3 if shortConditionTrigger3 == LessThanOption else True
    GoLong = False if longIndicatorSelector1 == skipOption and longIndicatorSelector2 == skipOption and (longIndicatorSelector3 == skipOption) else (True if longIndicatorSelector1 == skipOption else GoLong1) and (True if longIndicatorSelector2 == skipOption else GoLong2) and (True if longIndicatorSelector3 == skipOption else GoLong3)
    GoShort = False if shortIndicatorSelector1 == skipOption and shortIndicatorSelector2 == skipOption and (shortIndicatorSelector3 == skipOption) else (True if shortIndicatorSelector1 == skipOption else GoShort1) and (True if shortIndicatorSelector2 == skipOption else GoShort2) and (True if shortIndicatorSelector3 == skipOption else GoShort3)
    if GoLong and isTradingSession and (strategy.position_size <= 0):
        strategy.entry('long', strategy.long)
        alertMessage = 'long sl=' + string.tostring(SL) + ' tp=' + string.tostring(TP) + (' trail=true trailtrig=' + string.tostring(trailPoints) + ' traildist=' + string.tostring(trailOffset) if enableTrailing else '')
        alert(message=alertMessage, freq=alert.freq_once_per_bar_close)
    strategy.exit('xl', from_entry='long', loss=SL, profit=TP, trail_points=trailPoints, trail_offset=trailOffset)
    if GoShort and isTradingSession and (strategy.position_size >= 0):
        if GoShort:
            strategy.entry('short', strategy.short)
        alertMessage = 'short sl=' + string.tostring(SL) + ' tp=' + string.tostring(TP) + (' trail=true trailtrig=' + string.tostring(trailPoints) + ' traildist=' + string.tostring(trailOffset) if enableTrailing else '')
        alert(message=alertMessage, freq=alert.freq_once_per_bar_close)
    strategy.exit('xs', from_entry='short', loss=SL, profit=TP, trail_points=trailPoints, trail_offset=trailOffset)
    plot(maA, title='maA', linewidth=1, color=color.new(color.lime, 0))
    plot(maB, title='maB', linewidth=2, color=color.new(color.fuchsia, 0))
    plot(maC, title='maC', linewidth=3, color=color.new(color.orange, 0))
    atrFullChart = ta.atr(2000) / syminfo.mintick
    showWarning = SL > 0 and SL <= atrFullChart or (TP > 0 and TP <= atrFullChart) or (trailOffset > 0 and trailOffset <= atrFullChart)
    whichBracketsAreTooTight = 'StopLoss' if SL > 0 and SL <= atrFullChart and (TP == 0 or TP > atrFullChart) and (trailOffset == 0 or na(trailOffset) or trailOffset > atrFullChart) else 'StopLoss, TakeProfit' if SL > 0 and SL <= atrFullChart and (TP > 0) and (TP <= atrFullChart) and (trailOffset == 0 or na(trailOffset) or trailOffset > atrFullChart) else 'StopLoss, TakeProfit, Trail' if SL > 0 and SL <= atrFullChart and (TP > 0) and (TP <= atrFullChart) and (trailOffset > 0) and (trailOffset <= atrFullChart) else 'StopLoss, Trail' if SL > 0 and SL <= atrFullChart and (TP == 0 or TP > atrFullChart) and (trailOffset > 0) and (trailOffset <= atrFullChart) else 'TakeProfit' if (SL == 0 or SL > atrFullChart) and TP > 0 and (TP <= atrFullChart) and (trailOffset == 0 or na(trailOffset) or trailOffset > atrFullChart) else 'TakeProfit, Trail' if (SL == 0 or SL > atrFullChart) and TP > 0 and (TP <= atrFullChart) and (trailOffset > 0) and (trailOffset <= atrFullChart) else 'Trail' if (SL == 0 or SL > atrFullChart) and (TP == 0 or TP > atrFullChart) and (trailOffset > 0) and (trailOffset <= atrFullChart) else ''
    warningHeader: str = 'WARNING!'
    warningHeader2 = 'Too tight ' + whichBracketsAreTooTight
    warningText = 'Due to non-tick-data candle mechanisms here of TradingView, backtest results\nyou are seeing right now in the Strategy Tester are probably better than in reality.' + '\n\nWhy?\n\nStrategy Tester assumes that at each candle market has first moved in your\nfavor (so while in Long position market first reached HIGH of a candle, and while\nin Short position first reached LOW), and against you after that. ' + 'The suggested\nworkaround, to make backtester results more real, is to increase SL/TP/Trail,\nso they are higher than ATR for this chart (this instrument on this timeframe).' + '\n\nThat was in quick words, but you can learn more from this\nvideo: https://www.youtube.com/watch?v=uM5m_iUAP8g\n\nATR value (in ticks) for this chart is ' + string.tostring(atrFullChart)
    warningText2: str = 'You can proceed with the current settings, because you still might want to set\ntight SL/TP/Trail for alerts, but be assured that backtest results ain\'t real.'
    warningsTable: Persistent[Table] = table.new(position=position.top_right, columns=1, rows=4, border_width=1)
    if barstate.islastconfirmedhistory and showWarning:
        table.cell(warningsTable, column=0, row=0, text=warningHeader, bgcolor=na, text_color=color.orange, text_size=size.large)
        table.cell(warningsTable, column=0, row=1, text=warningHeader2, bgcolor=na, text_color=color.orange, text_size=size.large)
        table.cell(warningsTable, column=0, row=2, text=warningText, bgcolor=na, text_color=color.teal, text_size=size.normal, text_halign=text.align_right)
        table.cell(warningsTable, column=0, row=3, text=warningText2, bgcolor=na, text_color=color.teal, text_size=size.normal, text_halign=text.align_right)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
