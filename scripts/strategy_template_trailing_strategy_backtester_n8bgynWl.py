"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt_copy
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, chart, close, color, display,
    fill, format, high, input, label, line, location, log, low, map, math, na, nz, open, plot,
    plotchar, position, request, runtime, script, size, strategy, string, syminfo, ta, ticker,
    timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries, Series, Table
from pynecore.types.chart import ChartPoint
import lib.jason5480.analytics_tables.v3 as ant
import lib.jason5480.biased_price_target.v9 as biased_price_target
import lib.jason5480.chrono_utils.v8 as chr
import lib.jason5480.distance_ratio.v16 as dr
import lib.jason5480.math_utils.v11 as math_utils
import lib.jason5480.series_collection.v4 as col
import lib.jason5480.string_utils.v6 as string_utils
import lib.jason5480.tts_convention.v7 as conv
import lib.jason5480.two_ma_logic.v11 as tma


class DealConditionsMode(Enum):
    external = '🔨External'
    internal = '🔧Internal'


class UpdateMethod(Enum):
    static = 'STATIC'
    dynamic = 'DYNAMIC'
    ladder = 'LADDER'


class StDevMode(Enum):
    price = 'PRICE'
    ret = 'RETURN'


class TrailBarrier(Enum):
    front = 'FRONT'
    rear = 'REAR'


class OrderType(Enum):
    market = 'MARKET'
    limit = 'LIMIT'
    stop = 'STOP'
    stopLimit = 'STOP-LIMIT'


class StopLimitDistMethod(Enum):
    atr = 'ATR'
    stdev = 'STDEV'
    ticks = 'TICKS'


class TrailMode(Enum):
    fixed = 'FIXED'
    trail = 'TRAIL'


class MoveActMode(Enum):
    off = 'OFF'
    onceTp = 'ONCETP'
    oncePrice = 'ONCEPRICE'
    multiTp = 'MULTITP'
    multiPrice = 'MULTIPRICE'


class TrailActMode(Enum):
    off = 'OFF'
    start = 'START'
    tp = 'TP'


class CloseOpenProfit(Enum):
    possitive = 'POSSITIVE'
    negative = 'NEGATIVE'
    any = 'ANY'


class EntryQuantityMethod(Enum):
    risk = 'RISK'
    default = 'DEFAULT'


class BaseQuantityPrecision(Enum):
    auto = 'AUTO'
    manual = 'MANUAL'


class TakeProfitQuantityMethod(Enum):
    equal = 'EQUAL'
    manual = 'MANUAL'


NUM_OF_MODS: int = 14
GROUP_FILTERS: str = '📆 Filters'
MAX_LIMIT_FLOAT: float = 9007199254740992.0
MIN_LIMIT_FLOAT: float = 0.0
MAX_LIMIT_INT: int = 4503599627370495
LONG_ORDER_ID_PREFIX: str = 'Long'
SHORT_ORDER_ID_PREFIX: str = 'Short'
ENTRY_ORDER_ID_POSTFIX: str = 'Entry'
EXIT_ORDER_ID_PATTERN_1: str = '{0} Take Profit {1,number,integer} / Stop Loss / Limit Exit'
EXIT_ORDER_ID_PATTERN_2: str = '{0} Stop Loss / Limit Exit'
GROUP_STRATEGY: str = '🛠️ Strategy'
LONG_OPEN_COLOR: Color = color.new('#0074BA')
SHORT_OPEN_COLOR: Color = color.new('#FF6723')
CLOSE_COLOR: Color = color.new('#C790F1')
LONG_CANCEL_OPEN_COLOR: Color = color.new('#0074BA')
SHORT_CANCEL_OPEN_COLOR: Color = color.new('#FF6723')
CANCEL_CLOSE_COLOR: Color = color.new('#C790F1')
GROUP_STRATEGY_INTERNAL: str = '🔧 Strategy - Internal'
LOG_OPEN_SIGNAL_WARNING: str = 'A signal to open a new {0} position was received but there is already one still in progress, the signal will be ignored'
GROUP_VOLATILITY: str = '🎢 Volatility'
GROUP_ENTRY: str = '🔷🔶 Entry'
LOG_CNL_OPEN_SIGNAL_WARNING: str = 'A signal to cancel opening a new {0} position was received but there is none in progress, the signal will be ignored.'
GROUP_TAKE_PROFIT: str = '🎯 Take Profit'
GROUP_STOP_LOSS: str = '🛑 Stop Loss'
LOG_CLOSE_SIGNAL_WARNING: str = 'A signal to close an existing {0} position was received but there is none in progress, the signal will be ignored.'
GROUP_EXIT: str = '🟪🟩🟥 Exit'
LOG_CNL_CLOSE_SIGNAL_WARNING: str = 'A signal to cancel closing an existing {0} position was received but there is no {0} position in progress, the signal will be ignored.'
GROUP_RISK: str = '💰 Quantity/Risk Management'
GROUP_ANALYTICS: str = '📊 Analytics'
TT_COMPUTATIONAL_HEAVY_WARNING: str = ' WARNING! Computational heavy operation. If you get a timeout error please adjust the datetime window filter or disable other computational heavy operations.'
GROUP_ALERTS: str = '🔔 Alert Messages'
TT_ALERT_MESSAGE_EXPLANATION: str = ' Text that will replace the \'{{strategy.order.alert_message}}\' placeholder when one is used in the "Message" field of the "Create Alert" dialog.'
NUM_OF_MAX_TP_ALERTS: int = 5
GROUP_DEBUG: str = '🐞 Debug'
GROUP_SUPPORT: str = '💝 Support'


@script.strategy(title='Template Trailing Strategy (Backtester)', shorttitle='TTSv53', pyramiding=0, backtest_fill_limits_assumption=1, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=100000, slippage=3, commission_type=strategy.commission.percent, commission_value=0.1, close_entries_rule='ANY', margin_long=0, margin_short=0, max_lines_count=500, max_labels_count=500, fill_orders_on_standard_ohlc=True, behind_chart=False)
def main(
    referenceTimezone__input=input.enum(defval=chr.Timezone.Exchange, title='Timezones Ref->Chart', inline='Timezone', group=GROUP_FILTERS, display=display.data_window),
    fromEnabled=input.bool(defval=False, title='From      ', inline='From Date', group=GROUP_FILTERS, display=display.data_window),
    toEnabled=input.bool(defval=False, title='To       ', inline='To Date', group=GROUP_FILTERS, display=display.data_window),
    __input_3__=input.time(defval=timestamp('01 Jan 2024 00:00'), title='​', inline='From Date', group=GROUP_FILTERS, display=display.data_window),
    __input_4__=input.time(defval=timestamp('01 Jan 2025 00:00'), title='​​', inline='To Date', group=GROUP_FILTERS, display=display.data_window),
    __input_5__=input.enum(defval=chr.Timezone.Exchange, title='->', tooltip='The Timezone Ref is the reference timezone that is used for all the input time settings. The Timezone Chart is the timezone to convert into. WARNING! The chart timezone setting should always match with the actual chart timezone on the bottom right corner of your chart.', inline='Timezone', group=GROUP_FILTERS, display=display.data_window),
    daysEnabled=input.bool(defval=False, title='Session Days', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_7__=input.bool(defval=False, title='Sun', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_8__=input.bool(defval=True, title='Mon', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_9__=input.bool(defval=True, title='Tue', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_10__=input.bool(defval=True, title='Wed', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_11__=input.bool(defval=True, title='Thu', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_12__=input.bool(defval=True, title='Fri', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    __input_13__=input.bool(defval=False, title='Sat', inline='Session Days', group=GROUP_FILTERS, display=display.data_window),
    timeRangeEnabled=input.bool(defval=False, title='Session Time   ', inline='Session Time', group=GROUP_FILTERS, display=display.data_window),
    __input_15__=input.session(defval='0000-2400', title='​​​', inline='Session Time', tooltip='Time range of the session in Ref Timezone.', group=GROUP_FILTERS, display=display.data_window),
    dealMode=input.enum(defval=DealConditionsMode.internal, title='𝐃𝐞𝐚𝐥 𝐂𝐨𝐧𝐝𝐢𝐭𝐢𝐨𝐧𝐬 𝐌𝐨𝐝𝐞', tooltip='Use the "Internal" MA cross over/under logic to start and end your deals. Or use an "External" signal indicator to instruct your own start and end deal conditions.', group=GROUP_STRATEGY, display=display.all),
    __input_17__: Series[float] = input.source(defval=close, title='  🔌𝐒𝐢𝐠𝐧𝐚𝐥 🛈', tooltip='Select input from a "Signal Indicator". The "🔌Signal to TTS" output should be selected. If you do not have a "Signal Indicator", consider coding one, or use the "Signal Adapter" to create signal from non-signal indicators and (optional) compose more complex conditions using the "Signal Composer".  INFORMATION! The indicator should be added to the same chart with this strategy.', group=GROUP_STRATEGY, display=display.all),
    showOpenLabels=input.bool(defval=True, title='​​​​', inline='Open', group=GROUP_STRATEGY, display=display.data_window),
    longOpenColor=input.color(defval=LONG_OPEN_COLOR, title='🎨️ Open Color 📈/📉    ', inline='Open', group=GROUP_STRATEGY, display=display.none),
    shortOpenColor=input.color(defval=SHORT_OPEN_COLOR, title='​​​​​', tooltip='The color of the open long/short labels.', inline='Open', group=GROUP_STRATEGY, display=display.none),
    showCloseLabels=input.bool(defval=True, title='​​​​​​', inline='Close', group=GROUP_STRATEGY, display=display.data_window),
    longCloseColor=input.color(defval=CLOSE_COLOR, title='🎨️ Close Color 📈/📉    ', inline='Close', group=GROUP_STRATEGY, display=display.none),
    shortCloseColor=input.color(defval=CLOSE_COLOR, title='​​​​​​​', tooltip='The color of the close long/short labels.', inline='Close', group=GROUP_STRATEGY, display=display.none),
    showCnlOpenLabels=input.bool(defval=True, title='​​​​​​​​', inline='Cancel Open', group=GROUP_STRATEGY, display=display.data_window),
    longCnlOpenColor=input.color(defval=LONG_CANCEL_OPEN_COLOR, title='🎨️ Cancel Open Color 📈/📉', inline='Cancel Open', group=GROUP_STRATEGY, display=display.none),
    shortCnlOpenColor=input.color(defval=SHORT_CANCEL_OPEN_COLOR, title='​​​​​​​​​', tooltip='The color of the cancel open long/short labels.', inline='Cancel Open', group=GROUP_STRATEGY, display=display.none),
    showCnlCloseLabels=input.bool(defval=True, title='​​​​​​​​​​', inline='Cancel Close', group=GROUP_STRATEGY, display=display.data_window),
    longCnlCloseColor=input.color(defval=CANCEL_CLOSE_COLOR, title='🎨️ Cancel Close Color 📈/📉', inline='Cancel Close', group=GROUP_STRATEGY, display=display.none),
    shortCnlCloseColor=input.color(defval=CANCEL_CLOSE_COLOR, title='​​​​​​​​​​​', tooltip='The color of the cancel close long/short labels.', inline='Cancel Close', group=GROUP_STRATEGY, display=display.none),
    showLegend=input.bool(defval=True, title='📋 Show Legend', tooltip='Show the legend of the chart symbols.', group=GROUP_STRATEGY, display=display.data_window),
    __input_31__=input.float(defval=0.1, title='Commission % 🛈', minval=0.0, maxval=100.0, step=0.05, tooltip='Fees paid for each transaction entry, exit, take profit and stop loss (percentagewise). INFORMATION! This value should match the commission value in the "Settings/Properties" tab and the commission type should be set to "%" for accurate results.', group=GROUP_STRATEGY, display=display.data_window),
    reverseOrdersEnabled=input.bool(defval=True, title='Reverse Orders', tooltip='Enable reverse orders. If you are already in a position when a new start deal condition is met and it is pointing out to the other direction then, if this setting is enabled, an entry signal to the opposite direction will be emitted causing the existing position to exit according to the "𝐎𝐫𝐝𝐞𝐫 𝐓𝐲𝐩𝐞" that is defined in the EXIT section and a new entry will be placed to the direction of the signal according to the "𝐎𝐫𝐝𝐞𝐫 𝐓𝐲𝐩𝐞" that is defined in the ENTRY section. If this setting is disabled, the start deal condition will be ignored and a new start deal condition will be needed when you are not in a position.', group=GROUP_STRATEGY, display=display.data_window),
    cooldownEnabled=input.bool(defval=False, title='Cooldown # of bars     ', inline='Cooldown', group=GROUP_STRATEGY, display=display.data_window),
    cooldownBars=input.int(defval=7, title='​​​​​​​​​​​​', minval=1, tooltip='Do NOT emit open position signal if no more than the given number of bars have passed since the previous position exit. A new start deal condition has to be met after that period to open a new position.', inline='Cooldown', group=GROUP_STRATEGY, display=display.data_window),
    fastMaType=input.enum(defval=col.SeriesType.sma, title='Fast MA Type/Len        ', options=(col.SeriesType.alma, col.SeriesType.dema, col.SeriesType.ema, col.SeriesType.hma, col.SeriesType.rma, col.SeriesType.sma, col.SeriesType.swma, col.SeriesType.vwma, col.SeriesType.wma, col.SeriesType.linreg, col.SeriesType.median), inline='Fast MA', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    fastMaLength=input.int(defval=21, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='The type and the length of the fast MA.', inline='Fast MA', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    slowMaType=input.enum(defval=col.SeriesType.sma, title='Slow MA Type/Len       ', options=(col.SeriesType.alma, col.SeriesType.dema, col.SeriesType.ema, col.SeriesType.hma, col.SeriesType.rma, col.SeriesType.sma, col.SeriesType.swma, col.SeriesType.vwma, col.SeriesType.wma, col.SeriesType.linreg, col.SeriesType.median), inline='Slow MA', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    slowMaLength=input.int(defval=49, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='The type and the length of the slow MA.', inline='Slow MA', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    longDealsEnabled=input.bool(defval=True, title='Long Deals', inline='Long/Short Deals', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    shortDealsEnabled=input.bool(defval=True, title='Short Deals', tooltip='Enable long/short start/end/cancel deals. An open signal will be emitted when the long/short start deal conditions are met. If this option is unchecked you will not enter into long/short positions.', inline='Long/Short Deals', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    endDealsEnabled=input.bool(defval=False, title='End Deals', tooltip='Enable end deals. A close signal will be emitted when the end deal conditions are met. If this option is unchecked you will not exit your existing position based on the strategy logic. You will exit only when the stop loss or the take profit targets are reached.', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    cnlStartDealsEnabled=input.bool(defval=True, title='Cancel Start Deals', inline='Start/End Deals', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    cnlEndDealsEnabled=input.bool(defval=True, title='Cancel End Deals', tooltip='Enable cancel start/end deals. A cancel start/close signal will be emitted when the cancel start/end deal conditions are met. If this option is unchecked you will not cancel your entry/exit order based on the strategy logic when use limit, stop or stop-limit orders.', inline='Start/End Deals', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    emaFilterEnabled=input.bool(defval=True, title='EMA Filter', tooltip='Enable long/short trades based on EMA.', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    emaTimeframe=input.timeframe(defval='', title='  EMA Res/Len/Src', inline='EMA Filter', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    emaLength=input.int(defval=200, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, inline='EMA Filter', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    emaSrc: Series[float] = input.source(defval=close, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The timeframe, period and source for the EMA calculation.', inline='EMA Filter', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    emaAtrBandEnabled=input.bool(defval=True, title='EMA ATR Band', tooltip='Enable ATR band for EMA filter.', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    filterAtrMul=input.float(defval=1.0, title='  EMA ATR Mul/Len      ', minval=0.1, step=0.1, inline='EMA ATR', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    filterAtrLength=input.int(defval=5, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='ATR multiplier and length to be used for the ATR calculation that will be added on top of the EMA filter.', inline='EMA ATR', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    adxFilterEnabled=input.bool(defval=False, title='ADX Filter', tooltip='Enable long/short trades based on ADX.', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    adxSmoothing=input.int(defval=14, title='  Smooth/DI Len       ', minval=1, inline='ADX Filter', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    diLength=input.int(defval=14, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='ADX Smoothing length and Direction Length.', inline='ADX Filter', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    adxThreshold=input.float(defval=20.0, title='  Threshold', minval=0.1, maxval=100.0, step=5.0, tooltip='ADX lower threshold.', group=GROUP_STRATEGY_INTERNAL, display=display.data_window),
    atrMethod=input.enum(defval=UpdateMethod.static, title='ATR Mtd', tooltip='The method to calculate the ATR used for the trailing. Use the ATR value at the time of open signal throughout the whole trade (STATIC), or use the current ATR value (DYNAMIC), or the ATR only of the green/red bars when try to enter/exit the trade (LADDER).', group=GROUP_VOLATILITY, display=display.data_window),
    atrMaType=input.enum(defval=col.SeriesType.rma, title='  ATR Smooth Type/Len    ', options=(col.SeriesType.alma, col.SeriesType.dema, col.SeriesType.ema, col.SeriesType.hma, col.SeriesType.rma, col.SeriesType.sma, col.SeriesType.swma, col.SeriesType.vwma, col.SeriesType.wma, col.SeriesType.highest, col.SeriesType.lowest), inline='ATR', group=GROUP_VOLATILITY, display=display.data_window),
    atrLength=input.int(defval=14, title='​​​​​​​​​​​​​', minval=1, tooltip='The smoothing type and the length to be used for the ATR calculation.', inline='ATR', group=GROUP_VOLATILITY, display=display.data_window),
    stdevMethod=input.enum(defval=UpdateMethod.static, title='StDev Mtd', tooltip='The method to calculate the standard deviation used for the trailing. Use the StDev value at the time of open signal throughout the whole trade (STATIC), or use the current StDev value (DYNAMIC), or the StDev only of the green/red bars when try to enter/exit the trade (LADDER).', group=GROUP_VOLATILITY, display=display.data_window),
    stdevMode=input.enum(defval=StDevMode.price, title='  StDev Mode', tooltip='Use the "PRICE" as source for the standard deviation calculations. Or use "RETURN" to use the log returns of the price as source for the standard deviation.', group=GROUP_VOLATILITY, display=display.data_window),
    stdevPriceSrc: Series[float] = input.source(defval=close, title='  StDev Src/Len        ', inline='StDev', group=GROUP_VOLATILITY, display=display.data_window),
    stdevLength=input.int(defval=20, title='​​​​​​​​​​​​​​', minval=1, tooltip='The source and the length to be used for the StDev calculation.', inline='StDev', group=GROUP_VOLATILITY, display=display.data_window),
    longEntryColor=input.color(defval=LONG_OPEN_COLOR, title='🎨️ Color 📈/📉        ', inline='Color Entry', group=GROUP_ENTRY, display=display.none),
    shortEntryColor=input.color(defval=SHORT_OPEN_COLOR, title='​​​​​​​​​​​​​​​', tooltip='The color of the long/short limit, stop and stop-limit entry prices.', inline='Color Entry', group=GROUP_ENTRY, display=display.none),
    entryOrderType=input.enum(defval=OrderType.market, title='𝐎𝐫𝐝𝐞𝐫 𝐓𝐲𝐩𝐞​', tooltip='Use market order to enter at the open of the next bar (MARKET), or use limit order to enter at a "better" price defined by the distance from the close price and the limit mode (LIMIT), or use stop market order to enter at a "worst" price defined by the distance from the close price and the limit mode (STOP), or use stop-limit order to enter at a "worst" price defined by the distance from the close price and the limit mode (STOP-LIMIT).', group=GROUP_ENTRY, display=display.all),
    entryStopLimitDistMethod=input.enum(defval=StopLimitDistMethod.atr, title='  Limit Dist Mtd', tooltip='The method to calculate the distance used for the entry stop-limit orders. Offset the limit price target by a multiple of the ATR value (ATR), or by a multiple of the StDev value (STDEV), or by a number of ticks (TICKS)', group=GROUP_ENTRY, display=display.data_window),
    entryStopLimitDistMul=input.float(defval=0.5, title='    Limit Dist Mul', step=0.1, tooltip='The acceptable distance for the entry stop-limit orders is defined by this multiplier and it is applied either as percentage or atr multiplier or ticks, based on the "Limit Dist Mtd".', group=GROUP_ENTRY, display=display.data_window),
    entryDistMethod=input.enum(defval=dr.DistMethod.atr, title='Tgt Dist Mtd', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.cust), tooltip='The method to calculate the distance of the limit, stop and stop-limit entry. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), or Custom Entry Price (CUST).', group=GROUP_ENTRY, display=display.all),
    entryDistMul=input.float(defval=1.0, title='  Tgt Dist Mul|Len​', minval=0.01, step=0.05, tooltip='The distance multiplier or length to define the entry price from close when the open signal occurs or from the barrier price when trailing. The multiplier will be applied to the unit price that is defined by the distance method that is used. If the HHLL method is used, then the length will define the window for the highest high and lowest low calculations.', group=GROUP_ENTRY, display=display.all),
    entryCustLowerType=input.enum(defval=col.SeriesType.lowest, title='  Lower Type/Src         ', inline='Lower Cust Entry', group=GROUP_ENTRY, display=display.all),
    entryCustLowerSrc: Series[float] = input.source(defval=low, title='​​​​​​​​​​​​​​​​', tooltip='The type and source of the long limit and short stop or stop-limit custom entry.', inline='Lower Cust Entry', group=GROUP_ENTRY, display=display.all),
    entryCustHigherType=input.enum(defval=col.SeriesType.highest, title='  Higher Type/Src        ​', inline='Higher Cust Entry', group=GROUP_ENTRY, display=display.all),
    entryCustHigherSrc: Series[float] = input.source(defval=high, title='​​​​​​​​​​​​​​​​​', tooltip='The type and source of the short limit or long stop or stop-limit custom entry.', inline='Higher Cust Entry', group=GROUP_ENTRY, display=display.all),
    entryBiasEnabled=input.bool(defval=False, title='Bias Dist Mtd        ​', inline='Bias Distance Entry', group=GROUP_ENTRY, display=display.data_window),
    __input_74__=input.enum(defval=dr.DistMethod.ticks, title='​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias distance to offset the limit, stop and stop-limit entry price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Distance Entry', group=GROUP_ENTRY, display=display.data_window),
    __input_75__=input.float(defval=5.0, title='  Bias Dist Mul     ', step=0.5, tooltip='The multiplier to define the entry bias distance offset.', group=GROUP_ENTRY, display=display.data_window),
    entryMinDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​', inline='Restr Distance Entry', group=GROUP_ENTRY, display=display.data_window),
    entryMaxDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​', inline='Restr Distance Entry', group=GROUP_ENTRY, display=display.data_window),
    __input_78__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Dist Mtd    ​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the maximum/minimum distance of the entry price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Restr Distance Entry', group=GROUP_ENTRY, display=display.data_window),
    __input_79__=input.float(defval=1.0, title='  Min Dist Mul      ​', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the entry will not be placed too close from the reference price. Otherwise, a tight entry price would make the entry to easily be reached during volatile market conditions.', group=GROUP_ENTRY, display=display.data_window),
    __input_80__=input.float(defval=4.0, title='  Max Dist Mul     ​', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the entry will not be placed too far from the reference price. Otherwise, a loose entry price would risk to not be reached in a timely manner.', group=GROUP_ENTRY, display=display.data_window),
    entryTrailMode=input.enum(defval=TrailMode.fixed, title='Trail Mode​', tooltip='When you use limit, stop or stop-limit orders to enter, use a fixed price defined by the distance and the close price when the open signal occurs (FIXED), or trail by following the price to the direction of the entry for limit orders or the other direction of the entry for stop and stop-limit orders (TRAIL).', group=GROUP_ENTRY, display=display.all),
    entryTrailBarrier=input.enum(defval=TrailBarrier.front, title='  Barrier​​', tooltip='The price reference that will be used for the entry trailing logic. For entering into a position with a LIMIT order, follow the high for long and low for short (FRONT), or follow the low for long and high for short (REAR). For the STOP and STOP-LIMIT orders the logic is reversed.', group=GROUP_ENTRY, display=display.data_window),
    treatCloseAsCancel=input.bool(defval=False, title='Treat Close as Cancel', tooltip='If enabled the invalid close position signals of this direction will be treated as cancel open signals to cancel limit, stop and stop-limit entry orders of the same direction.', group=GROUP_ENTRY, display=display.data_window),
    treatEntryAsCancel=input.bool(defval=False, title='Treat Entry as Cancel', tooltip='If enabled the entries that happened to one direction will be treated as cancel open signals to cancel limit, stop and stop-limit entry orders of the other direction.', group=GROUP_ENTRY, display=display.data_window),
    takeProfitColor=input.color(defval=color.new(color.new('#00897B'), 0), title='🎨️ Color', tooltip='The color of the take profit price target lines.', group=GROUP_TAKE_PROFIT, display=display.none),
    numOfTakeProfitTargets=input.int(defval=1, title='𝐓𝐚𝐤𝐞 𝐏𝐫𝐨𝐟𝐢𝐭 𝐓𝐚𝐫𝐠𝐞𝐭𝐬', minval=0, maxval=5, tooltip='The number of take profit targets to be set for each entry. The first target is the initial target and every additional target is a step target.', group=GROUP_TAKE_PROFIT, display=display.all),
    stopLossColor=input.color(defval=color.new(color.new('#880E4F'), 0), title='🎨️ Color​', tooltip='The color of the stop loss price.', group=GROUP_STOP_LOSS, display=display.none),
    stopLossDistMethod=input.enum(defval=dr.DistMethod.atr, title='𝑻𝒈𝒕 𝑫𝒊𝒔𝒕 𝑴𝒕𝒅', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.cust), tooltip='The method to calculate the distance of the stop loss price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), or Custom Stop Loss Price (CUST).', group=GROUP_STOP_LOSS, display=display.all),
    longStopLossDistMul=input.float(defval=3.0, title='  Tgt Dist Mul|Len 📈/📉  ', minval=0.05, step=0.05, inline='Distance Mul Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossCustLowerType=input.enum(defval=col.SeriesType.lowest, title='  Lower Type/Src         ​', inline='Lower Cust Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossCustLowerSrc: Series[float] = input.source(defval=low, title='​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the long custom stop loss.', inline='Lower Cust Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossCustHigherType=input.enum(defval=col.SeriesType.highest, title='  Higher Type/Src        ​​​', inline='Higher Cust Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossCustHigherSrc: Series[float] = input.source(defval=high, title='​​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the short custom stop loss.', inline='Higher Cust Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossBiasEnabled=input.bool(defval=False, title='Bias Dist Mtd        ​​', inline='Bias Distance Stop Loss', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_95__=input.enum(defval=dr.DistMethod.atr, title='​​​​​​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias distance to offset the stop loss price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Distance Stop Loss', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_96__=input.float(defval=0.5, title='  Bias Dist Mul     ​', step=0.5, tooltip='The multiplier to define the stop loss bias distance offset.', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossMinDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​', inline='Restr Distance Stop Loss', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossMaxDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Restr Distance Stop Loss', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_99__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Dist Mtd    ​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the maximum/minimum distance of the stop loss price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Restr Distance Stop Loss', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_100__=input.float(defval=1.0, title='  Min Dist Mul      ​​', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the stop loss will not be placed too close from the entry price. Otherwise, a tight stop loss price would make the stop loss to easily be reached during volatile market conditions.', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_101__=input.float(defval=10.0, title='  Max Dist Mul     ​​', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the stop loss will not be placed too far from the entry price. Otherwise, a loose stop loss price would increase the max drawdown and losses when it is reached.', group=GROUP_STOP_LOSS, display=display.data_window),
    shortStopLossDistMul=input.float(defval=3.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=0.05, step=0.05, tooltip='The distance multiplier to define the long/short stop loss price from the close price when the open signal occurs or from the barrier price when trailing. The multiplier will be applied to the unit price that is defined by the distance method that is used. If the CUST method is used, then the multiplier is the length that will define the custom price according to its type.', inline='Distance Mul Stop Loss', group=GROUP_STOP_LOSS, display=display.all),
    stopLossMoveActMode=input.enum(defval=MoveActMode.off, title='Move Activation Mode', tooltip='Move the stop loss to the entry price (a.k.a breakeven) when the activation take profit price target is reached (ONCETP), or move the stop loss to the entry price (a.k.a breakeven) when the current price moves away from the entry by a distance (ONCEPRICE), or move the stop loss to the previous take profit price target every time a new take profit is reached (MULTITP), or move the stop loss to the previous distance from entry price every time the price moves away from the entry by a distance (MULTIPRICE). Thus, more than one take profit price target is needed to see a difference between the ONCETP and MULTITP modes! If both move and trailing are activated the stop loss is defined by the more strict price at any given time.', group=GROUP_STOP_LOSS, display=display.all),
    stopLossMoveTPActNum=input.int(defval=1, title='  Act Take Profit #​', minval=1, tooltip='The Take Profit number (up to the "𝐓𝐚𝐤𝐞 𝐏𝐫𝐨𝐟𝐢𝐭 𝐓𝐚𝐫𝐠𝐞𝐭𝐬" number set in TAKE PROFIT section) that will activate the movement of the stop loss to the entry price after it is reached. The Move Activation should be set to "ONCETP".', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_105__=input.enum(defval=dr.DistMethod.perc, title='  Act Price Dist Mtd', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the distance of the current price from entry. Percentage based (PERC), ATR based (ATR) or Standard deviation based (STDEV) or Tick based (TICKS).', group=GROUP_STOP_LOSS, display=display.data_window),
    __input_106__=input.float(defval=2.0, title='    Act Price Dist Mul', minval=0.01, step=0.05, tooltip='The distance multiplier to define the activation price from the entry in order to move the stop loss to breakeven. The multiplier will be applied to the unit price that is defined by the distance method that is used.', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossTrailActMode=input.enum(defval=TrailActMode.off, title='Trail Activation Mode', tooltip='Enables the trailing for the stop loss from the very beginning of the entry order (START), or when the activation take profit price target is reached (TP) or not at all (OFF).', group=GROUP_STOP_LOSS, display=display.all),
    stopLossTrailTPActNum=input.int(defval=1, title='  Act Take Profit #​​', minval=1, tooltip='The Take Profit number (up to the "𝐓𝐚𝐤𝐞 𝐏𝐫𝐨𝐟𝐢𝐭 𝐓𝐚𝐫𝐠𝐞𝐭𝐬" number set in TAKE PROFIT section) that will activate the trailing of the stop loss after it is reached. The Trailing Activation should be set to "TP".', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossTrailBarrier=input.enum(defval=TrailBarrier.rear, title='  Barrier​​​', tooltip='The price reference that will be used for the stop loss trailing logic. For exiting from a position, follow the high for long and low for short (FRONT), or follow the low for long and the high for short (REAR). The Trailing Activation should be set to "START" or "TP".', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossStepTrailDistEnabled=input.bool(defval=False, title='Trail Step Mode', tooltip='When stop loss trailining is activated the distance will trail the price according to the stop loss method so it maintains its maximum value from the current high/low (OFF), or the distance will change every time a new take profit is reached and will add the corresponding step value to the previous (ON). Thus, more than one take profit price target is needed to see a difference between two modes! If both move and trailing are activated the stop loss is defined by the more strict price at any given time.', group=GROUP_STOP_LOSS, display=display.data_window),
    longStopLossStepTrailDistMul=input.float(defval=2.0, title='  Step Dist Mul|Len 📈/📉  ', step=0.05, inline='Step Distance Mul', group=GROUP_STOP_LOSS, display=display.data_window),
    shortStopLossStepTrailDistMul=input.float(defval=2.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​', step=0.05, tooltip='The distance multiplier or length to be added on top of the long/short stop loss distance multiplier or length after a take profit target is reached, to define the new long/short stop loss price target. The multiplier will be applied to the unit price that is defined by the distance method that is used. If the CUST method is used, then the step length will be added to the existing length that will be used for the custom price calculations according to its type.', inline='Step Distance Mul', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossAdjustmentEnabled=input.bool(defval=False, title='Adjust on Gaps​', tooltip='When this option is enabled, the stop loss target will be adjusted when entering and the actual entry price is different than the expected entry price due to gaps in the price action and slippage of the market.', group=GROUP_STOP_LOSS, display=display.data_window),
    stopLossWaitCloseConfirm=input.bool(defval=False, title='Wait close confirmation', tooltip='When this option is enabled, the stop loss will not be executed immediately but will wait for the bar close confirmation. This might cause the strategy to have greater losses than the expected. A "Close Market" alert will be triggered instead.', group=GROUP_STOP_LOSS, display=display.data_window),
    closeEarlyEnabled=input.bool(defval=False, title='Close Early # of bars    ', inline='Close Early', group=GROUP_STRATEGY, display=display.data_window),
    closeEarlyBars=input.int(defval=7, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='Emit close position signal if the given number of bars have passed since the entry and the activation take profit price target has not been reached yet.', inline='Close Early', group=GROUP_STRATEGY, display=display.data_window),
    closeEarlyTPActNum=input.int(defval=1, title='  Act Take Profit #​​​', minval=1, tooltip='The Take Profit number (up to the "𝐓𝐚𝐤𝐞 𝐏𝐫𝐨𝐟𝐢𝐭 𝐓𝐚𝐫𝐠𝐞𝐭𝐬" number set in TAKE PROFIT section) that will activate the close early if it is not reached within the given number of bars from the entry.', group=GROUP_STRATEGY, display=display.data_window),
    closeAtSessionEnd=input.bool(defval=False, title='Close at Session End', tooltip='Close all positions at the market price at the end of each session or the end of datetime window.', group=GROUP_STRATEGY, display=display.data_window),
    closeOpenProfit=input.enum(defval=CloseOpenProfit.any, title='Close only if open profit is', tooltip='Emit close position signal when an end deal condition is met and only if the current position is in profit (POSSITIVE), or only if the position is in loss (NEGATIVE), or always (ANY).', group=GROUP_STRATEGY, display=display.data_window),
    longExitColor=input.color(defval=CLOSE_COLOR, title='🎨️ Color 📈/📉        ​', inline='Exit Color', group=GROUP_EXIT, display=display.none),
    shortExitColor=input.color(defval=CLOSE_COLOR, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The color of the long/short limit and stop exit prices.', inline='Exit Color', group=GROUP_EXIT, display=display.none),
    exitOrderType=input.enum(defval=OrderType.market, title='𝐎𝐫𝐝𝐞𝐫 𝐓𝐲𝐩𝐞​​', options=(OrderType.market, OrderType.limit, OrderType.stop), tooltip='Use market order to exit at the open of the next bar (MARKET), or use limit order to exit at a "better" price defined by the distance from the close price and the limit mode (LIMIT), or use stop market order to exit at a "worst" price defined by the distance from the close price and the limit mode (STOP). Limit and stop orders last until they are filled or canceled.', group=GROUP_EXIT, display=display.all),
    exitDistMethod=input.enum(defval=dr.DistMethod.atr, title='Tgt Dist Mtd​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.cust), tooltip='The method to calculate the distance of the limit and stop exit. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), or Custom Exit Price (CUST).', group=GROUP_EXIT, display=display.all),
    exitDistMul=input.float(defval=1.0, title='  Tgt Dist Mul|Len​​', minval=0.01, step=0.05, tooltip='The distance multiplier to define the exit price from the close price when the close signal occurs or from the barrier price when trailing. The multiplier will be applied to the unit price that is defined by the distance method that is used. If the HHLL method is used, then the length will define the window for the highest high and lowest low calculations.', group=GROUP_EXIT, display=display.all),
    exitCustHigherType=input.enum(defval=col.SeriesType.highest, title='  Higher Type/Src        ​​​​', inline='Higher Cust Exit', group=GROUP_EXIT, display=display.all),
    exitCustHigherSrc: Series[float] = input.source(defval=high, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the long limit and short stop custom exit.', inline='Higher Cust Exit', group=GROUP_EXIT, display=display.all),
    exitCustLowerType=input.enum(defval=col.SeriesType.lowest, title='  Lower Type/Src         ​​​', inline='Lower Cust Exit', group=GROUP_EXIT, display=display.all),
    exitCustLowerSrc: Series[float] = input.source(defval=low, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the short limit and long stop custom exit.', inline='Lower Cust Exit', group=GROUP_EXIT, display=display.all),
    exitBiasEnabled=input.bool(defval=False, title='Bias Dist Mtd        ​​​', inline='Bias Distance Exit', group=GROUP_EXIT, display=display.data_window),
    __input_130__=input.enum(defval=dr.DistMethod.ticks, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias distance to offset the limit and stop exit price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Distance Exit', group=GROUP_EXIT, display=display.data_window),
    __input_131__=input.float(defval=5.0, title='  Bias Dist Mul     ​​', step=0.5, tooltip='The multiplier to define the exit bias distance offset.', group=GROUP_EXIT, display=display.data_window),
    exitMinDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Exit Restr Distance', group=GROUP_EXIT, display=display.data_window),
    exitMaxDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Exit Restr Distance', group=GROUP_EXIT, display=display.data_window),
    __input_134__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Dist Mtd    ​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the maximum/minimum distance of the exit price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Exit Restr Distance', group=GROUP_EXIT, display=display.data_window),
    __input_135__=input.float(defval=1.0, title='  Min Dist Mul      ​​​', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the exit will not be placed too close from the reference price. Otherwise, a tight exit price would make the exit to easily be reached during volatile market conditions.', group=GROUP_EXIT, display=display.data_window),
    __input_136__=input.float(defval=4.0, title='  Max Dist Mul     ​​​', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method. This can be used to make sure that the exit will not be placed too far from the reference price. Otherwise, a loose exit price would risk to not be reached in a timely manner.', group=GROUP_EXIT, display=display.data_window),
    exitTrailMode=input.enum(defval=TrailMode.fixed, title='Trail Mode​​', tooltip='When you use limit or stop orders to exit, use a fixed price defined by the distance and the close price when the open signal s (FIXED), or trail by following the price to the direction of the exit for limit orders or the other direction of the exit for stop orders (TRAIL).', group=GROUP_EXIT, display=display.all),
    exitTrailBarrier=input.enum(defval=TrailBarrier.front, title='  Barrier​​​​', tooltip='The price reference that will be used for the exit trailing logic. For exiting from a position with a LIMIT order, follow the low for long and high for short (FRONT), or follow the high for long and the low for short (REAR). For the STOP orders the logic is reversed.', group=GROUP_EXIT, display=display.data_window),
    treatOpenAsCancel=input.bool(defval=False, title='Treat Open as Cancel', tooltip='If enabled the invalid open position signals to this direction will be treated as cancel close signals to cancel stop exit orders of the same direction.', group=GROUP_EXIT, display=display.data_window),
    entryQuantityMethod=input.enum(defval=EntryQuantityMethod.risk, title='𝑬𝒏𝒕𝒓𝒚 𝑸𝒕𝒚 𝑴𝒕𝒅', tooltip='The method to calculate the quantity to enter each new position. Use an amount so that if the stop loss is reached no more than a percent of equity is lost (RISK), or use the amount defined in the "Settings/Properties" tab (DEFAULT).', group=GROUP_RISK, display=display.all),
    __input_141__=input.float(defval=1.0, title='  Capital Risk %   ', minval=0.05, maxval=10.0, step=0.25, tooltip='The maximum percentage of the total "owned equity" (before leverage is used) to risk in every trade.', group=GROUP_RISK, display=display.data_window),
    baseQuantityPrecision=input.enum(defval=BaseQuantityPrecision.auto, title='Contracts Precision', tooltip='The precision of the base quantity in terms of decimal digits can be calculated automatically using the underlying instrument type or manually.', group=GROUP_RISK, display=display.all),
    baseQuantityDecimals=input.int(defval=2, title='  Decimal Digits', minval=0, tooltip='The precision in decimal digit places used for the calculation of the base quantity.', group=GROUP_RISK, display=display.data_window),
    minOrderSize=input.float(defval=5.0, title='Minimum Order Size', minval=0.0, step=1.0, tooltip='The minimum trade size in quote currency that is allowed in the exchange for a valid new position (e.g. in Binance you cannot trade amounts that are equal or less than 5 USD). For crypto markets the minimum order size divided by the current price define the precision in terms of decimal digits in the base quantity.', group=GROUP_RISK, display=display.data_window),
    longLeverage=input.int(defval=1, title='Leverage 📈/📉 🛈       ', minval=1, inline='Leverage', group=GROUP_RISK, display=display.data_window),
    shortLeverage=input.int(defval=1, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='Leverage can be used to multiply the entry quantity of each trade up to the given factor (by borrowing the remaining amount). Thus, the profits and losses are multiplied respectively. INFORMATION! The margin for long/short positions value in the "Settings/Properties" should be adjusted accoridngly to correctly trigger margin calls.', inline='Leverage', group=GROUP_RISK, display=display.data_window),
    __input_147__=input.float(defval=0.0, title='Moonbag Qty %', minval=0.0, maxval=99.9, step=0.5, tooltip='The percentage of the position that will NOT be exited when ALL the take profit price targets are reached. If more than one take profit price target is set, then they will sharethe remaining amount according to the "TP Qty Mtd". The moonbag amount will exit only when stop loss is reached or a close signal is received.', group=GROUP_RISK, display=display.all),
    takeProfitQuantityMethod=input.enum(defval=TakeProfitQuantityMethod.equal, title='TP Qty Mtd', tooltip='The method to calculate the quantity to exit each take profit target. All the take profit exits share equally the remaining amount of the equity after we reserve the moonbag amount from the entry quantity (EQUAL), or use the quantity percentages for initial and step take profits sepratelly as defined by the user (MANUAL).', group=GROUP_RISK, display=display.all),
    __input_149__=input.float(defval=100.0, title='  Init TP Qty %', minval=0.0, maxval=100.0, step=0.5, tooltip='The percentage of the position that will exited when the initial take profit price target is reached.', group=GROUP_RISK, display=display.all),
    __input_150__=input.float(defval=0.0, title='  Step TP Qty %', minval=0.0, maxval=100.0, step=0.5, tooltip='The percentage of the position that will be exited when a step take profit price target(s) is reached.', group=GROUP_RISK, display=display.all),
    maxDrawdownEnabled=input.bool(defval=False, title='Max Drawdown %     ', inline='Drawdown', group=GROUP_RISK, display=display.data_window),
    maxDrawdownPerc=input.float(defval=25.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1.0, maxval=100.0, step=0.5, tooltip='The maximum drawdown to stop trading.', inline='Drawdown', group=GROUP_RISK, display=display.data_window),
    maxIntradayLossEnabled=input.bool(defval=False, title='Max Intraday Loss %     ', inline='Intraday Loss', group=GROUP_RISK, display=display.data_window),
    maxIntradayLossPerc=input.float(defval=5.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1.0, maxval=100.0, step=0.5, tooltip='The maximum intraday loss.', inline='Intraday Loss', group=GROUP_RISK, display=display.data_window),
    maxDailyTradesEnabled=input.bool(defval=False, title='Max Daily Trades      ', inline='Daily Trades', group=GROUP_RISK, display=display.data_window),
    maxDailyTrades=input.int(defval=25, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='The maximum number of trades per day.', inline='Daily Trades', group=GROUP_RISK, display=display.data_window),
    maxLosingDaysEnabled=input.bool(defval=False, title='Max Losing Days      ', inline='Losing Days', group=GROUP_RISK, display=display.data_window),
    maxLosingDays=input.int(defval=5, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=1, tooltip='The maximum number of consecutive losing days.', inline='Losing Days', group=GROUP_RISK, display=display.data_window),
    takeProfitInitDistMethod=input.enum(defval=dr.DistMethod.atr, title='𝑰𝒏𝒊𝒕 𝑻𝒈𝒕 𝑫𝒊𝒔𝒕 𝑴𝒕𝒅', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.prof, dr.DistMethod.rr, dr.DistMethod.cust), tooltip='The method to calculate the distance of the first take profit price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Fixed Profit (PROF), Risk-Reward based (RR), or Custom Take Profit Price (CUST).', group=GROUP_TAKE_PROFIT, display=display.all),
    longTakeProfitInitDistMul=input.float(defval=5.0, title='  Init Tgt Dist Mul|Len 📈/📉 ', minval=0.05, step=0.05, inline='Init Take Profit Mul', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitCustHigherType=input.enum(defval=col.SeriesType.highest, title='  Higher Type/Src        ​​', inline='Higher Cust Take Profit', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitCustHigherSrc: Series[float] = input.source(defval=high, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the long custom take profit.', inline='Higher Cust Take Profit', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitCustLowerType=input.enum(defval=col.SeriesType.lowest, title='  Lower Type/Src         ​​', inline='Lower Cust Take Profit', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitCustLowerSrc: Series[float] = input.source(defval=low, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The type and source of the short custom take profit.', inline='Lower Cust Take Profit', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitInitBiasEnabled=input.bool(defval=False, title='Init Bias Dist Mtd     ', inline='Bias Init Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_166__=input.enum(defval=dr.DistMethod.ticks, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias distance to offset the take initial profit price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Init Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_167__=input.float(defval=5.0, title='  Init Bias Dist Mul   ', step=0.5, tooltip='The multiplier to define the initial take profit bias distance offset.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    takeProfitInitMinDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Init Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    takeProfitInitMaxDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Init Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_170__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Init Dist Mtd  ', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.prof, dr.DistMethod.rr), tooltip='The method to calculate the maximum/minimum distance of the initial take profit price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Profit based (PROF) or Risk-Reward based (RR).', inline='Init Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_171__=input.float(defval=0.1, title='  Init Min Dist Mul    ​​​​', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method. The minimum can be used to make sure that you will compensate for (at least) the commission rates, especially when you are trading on lower time frames.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_172__=input.float(defval=10.0, title='  Init Max Dist Mul    ​​​​', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method. The maximum can be used to make sure that you get some profits when the price moves in the desired direction.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    shortTakeProfitInitDistMul=input.float(defval=5.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=0.05, step=0.05, tooltip='The distance multiplier to define the long/short first take profit price from the open price. The multiplier will be applied to the unit price that is defined by the distance method that is used. If the CUST method is used, then the multiplier is the length that will define the custom price according to its type.', inline='Init Take Profit Mul', group=GROUP_TAKE_PROFIT, display=display.all),
    __input_174__=input.enum(defval=dr.DistMethod.atr, title='Step Tgt Dist Mtd  ', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.prof, dr.DistMethod.rr), tooltip='The method to calculate the distance of additional step take profit price targets. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Fixed Profit (PROF) or Risk-Reward based (RR).', group=GROUP_TAKE_PROFIT, display=display.all),
    __input_175__=input.float(defval=1.0, title='  Step Tgt Dist Mul 📈/📉   ', minval=0.05, step=0.05, inline='Step Take Profit Mul', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitStepBiasEnabled=input.bool(defval=False, title='Step Bias Dist Mtd      ', inline='Bias Step Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_177__=input.enum(defval=dr.DistMethod.ticks, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias distance to offset the step take profit price target(s). Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Step Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_178__=input.float(defval=5.0, title='  Step Bias Dist Mul   ', step=0.5, tooltip='The multiplier to define the step take profit bias distance offset.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    takeProfitStepMinDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Step Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    takeProfitStepMaxDistEnabled=input.bool(defval=False, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Step Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_181__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Step Dist Mtd ', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks, dr.DistMethod.prof, dr.DistMethod.rr), tooltip='The method to calculate the maximum/minimum distance of the step take profit price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Profit based (PROF) or Risk-Reward based (RR).', inline='Step Restr Distance Take Profit', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_182__=input.float(defval=0.1, title='  Step Min Dist Mul   ​​​​​', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method. The minimum can be used to make sure that you will compensate for (at least) the commission rates, especially when you are trading on lower time frames.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_183__=input.float(defval=5.0, title='  Step Max Dist Mul    ​​​​​', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method. The maximum can be used to make sure that you get some profits when the price moves in the desired direction.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_184__=input.float(defval=1.0, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', minval=0.05, step=0.05, tooltip='The distance multiplier to be added on top of the first long/short take profit distance multiplier to define the long/short step take profit price target. The multiplier will be applied to the unit price that is defined by the distance method that is used.', inline='Step Take Profit Mul', group=GROUP_TAKE_PROFIT, display=display.all),
    takeProfitTrailEnabled=input.bool(defval=False, title='Enable Trail⚠️💹', tooltip='Enable or disable the trailing for take profit. WARNING! This feature will repaint. Make sure you use it along with "Bar Magnifier" and "Deep Backtesting" for realistic backtest results.', group=GROUP_TAKE_PROFIT, display=display.all),
    __input_186__=input.enum(defval=dr.DistMethod.perc, title='  Trail TP Dist Mtd', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the distance of the trailing take profit. Percentage based (PERC), ATR based (ATR) or Standard deviation based (STDEV) or Tick based (TICKS).', group=GROUP_TAKE_PROFIT, display=display.data_window),
    __input_187__=input.float(defval=2.0, title='    Trail TP Dist Mul', minval=0.01, step=0.05, tooltip='The distance multiplier to define the take profit price offset from the high/low price after the target is reached when trailing. The multiplier will be applied to the unit price that is defined by the distance method that is used.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    takeProfitAdjustmentEnabled=input.bool(defval=False, title='Adjust on Gaps', tooltip='When this option is enabled, the take profit targets will be adjusted when entering and the actual entry price is different than the expected entry price due to gaps in the price action and slippage of the market.', group=GROUP_TAKE_PROFIT, display=display.data_window),
    winColor=input.color(defval=color.new(color.new('#00D26A'), 0), title='🎨️ Win/Loss Color       ', inline='Result Color', group=GROUP_ANALYTICS, display=display.none),
    lossColor=input.color(defval=color.new(color.new('#ED2F2D'), 0), title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='The color of the win/loss labels and the mark trade lines.', inline='Result Color', group=GROUP_ANALYTICS, display=display.none),
    showSeasonalTable=input.bool(defval=True, title='Show Seasonal Table⚠️🐌  ', inline='Seasonal Table', group=GROUP_ANALYTICS, display=display.data_window),
    seasonalTableExtend=input.bool(defval=True, title='Extended', tooltip='Show the table with the seasonal performance. Extend the seasonal table with additional rows and colums with statistics for each season like Avg, StDev and for each eon like CAGR and MaxDD.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Seasonal Table', group=GROUP_ANALYTICS, display=display.data_window),
    seasonalTableSeasonality=input.enum(defval=ant.Seasonality.monthOfYear, title='  Season/Eon       ', tooltip='The season and eon of the seasonal performance table.', group=GROUP_ANALYTICS, display=display.data_window),
    seasonalTableMaxNumOfYears=input.int(defval=5, title='  Max Num of Years     ', minval=0, tooltip='The maximum number of eons to show in the seasonal performance table.', group=GROUP_ANALYTICS, display=display.data_window),
    showTradeStats=input.bool(defval=False, title='Show Trade Stats⚠️🐌', tooltip='Show the winning/losing trade stats when complete.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ANALYTICS, display=display.data_window),
    showStatsTable=input.bool(defval=False, title='Show Stats Table⚠️🐌   ', inline='Stats Table', group=GROUP_ANALYTICS, display=display.data_window),
    statsTablePosY=input.string(defval='TOP', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('TOP', 'MIDDLE', 'BOTTOM'), inline='Stats Table', group=GROUP_ANALYTICS, display=display.data_window),
    statsTablePosX=input.string(defval='RIGHT', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('LEFT', 'RIGHT'), tooltip='Show the table with the overall trade statistics on the selected corner.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Stats Table', group=GROUP_ANALYTICS, display=display.data_window),
    showMetricsTable=input.bool(defval=False, title='Show Metrics Table⚠️🐌  ', inline='Metrics Table', group=GROUP_ANALYTICS, display=display.data_window),
    metricsTablePosY=input.string(defval='BOTTOM', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('TOP', 'MIDDLE', 'BOTTOM'), inline='Metrics Table', group=GROUP_ANALYTICS, display=display.data_window),
    metricsTablePosX=input.string(defval='RIGHT', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('LEFT', 'RIGHT'), tooltip='Show the table with the trade metrics on the selected corner.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Metrics Table', group=GROUP_ANALYTICS, display=display.data_window),
    tickerPrefix=input.string(defval='', title='Ticker Id Prefix/Postfix      ', inline='Ticker', group=GROUP_ALERTS, display=display.none),
    tickerPostfix=input.string(defval='', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', tooltip='Prepend/Append a custom string to the TVs ticker id when you use {{ticker}} as variable in the alert messages.', inline='Ticker', group=GROUP_ALERTS, display=display.none),
    usePercRange100=input.bool(defval=True, title='Percentage Range [0, 100]', tooltip='Enable to multiply all the percentatges with 100 so that the values range from [0, 100] instead of [0, 1].', group=GROUP_ALERTS, display=display.none),
    offsetMsgTicks=input.int(defval=5, title='Offset Ticks', minval=1, tooltip='The ticks that will be added/substracted from entry/exit price to calculate the {{entry+_price}}, {{entry-_price}}, {{exit+_price}}, {{exit-_price}} variables. Those values could be used if you want to send a limit order to your exchange and the price might go to the "wrong" side due to the high volatility of the market and delay between the time of computation and execution.', group=GROUP_ALERTS, display=display.data_window),
    msgEnteredEnabled=input.bool(defval=False, title='Enable Entry Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "entry order fills" of the strategy (e.g. market, limit, stop and stop-limit entry).' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_207__=input.text_area(defval='Long Entry({{ticker}}): Bought at market price of {{entry_price}} {{quote_currency}} an amount equal to {{entry_base_quantity}} {{base_currency}} (for {{entry_quote_quantity}} {{quote_currency}}) and risk of {{risk_perc}}%. The stop loss was placed at {{stop_loss_price}} {{quote_currency}} and take profit targets at [{{take_profit_price_1}}, {{take_profit_price_2}}, {{take_profit_price_3}}, {{take_profit_price_4}}, {{take_profit_price_5}}] {{quote_currency}}', title='Enter Market Long', tooltip='Alert message emitted when entered long position.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_208__=input.text_area(defval='Short Entry({{ticker}}): Sold at market price of {{entry_price}} {{quote_currency}} an amount equal to {{entry_base_quantity}} {{base_currency}} (for {{entry_quote_quantity}} {{quote_currency}}) and risk of {{risk_perc}}%. The stop loss was placed at {{stop_loss_price}} {{quote_currency}} and take profit targets at [{{take_profit_price_1}}, {{take_profit_price_2}}, {{take_profit_price_3}}, {{take_profit_price_4}}, {{take_profit_price_5}}] {{quote_currency}}', title='Enter Market Short', tooltip='Alert message emitted when entered short position.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_209__=input.text_area(defval='Long Entry({{ticker}}): Bought with limit, stop or stop-limit entry order at the price of {{entry_price}} {{quote_currency}} an amount equal to {{entry_base_quantity}} {{base_currency}} and risk of {{risk_perc}}%. The stop loss was placed at {{stop_loss_price}} {{quote_currency}} and take profit targets at [{{take_profit_price_1}}, {{take_profit_price_2}}, {{take_profit_price_3}}, {{take_profit_price_4}}, {{take_profit_price_5}}] {{quote_currency}}', title='Enter Limit Long', tooltip='Alert message emitted when entered long position with a limit, stop or stop-limit order.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_210__=input.text_area(defval='Short Entry({{ticker}}): Sold with limit, stop or stop-limit entry order at the price of {{entry_price}} {{quote_currency}} an amount equal to {{entry_base_quantity}} {{base_currency}} and risk of {{risk_perc}}%. The stop loss was placed at {{stop_loss_price}} {{quote_currency}} and take profit targets at [{{take_profit_price_1}}, {{take_profit_price_2}}, {{take_profit_price_3}}, {{take_profit_price_4}}, {{take_profit_price_5}}] {{quote_currency}}', title='Enter Limit Short', tooltip='Alert message emitted when entered short position with a limit, stop or stop-limit order.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    msgClosedOrExitedEnabled=input.bool(defval=False, title='Enable Close/Exit Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "close/exit order fills" of the strategy (e.g. market, limit and stop exit).' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_212__=input.text_area(defval='Long Close({{ticker}}): Sold at market price of {{exit_price}} {{quote_currency}} {{remaining_quantity_perc}}% of the initial position', title='Close Market Long', tooltip='Alert message emitted when closed long position.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_213__=input.text_area(defval='Short Close({{ticker}}): Bought at market price of {{exit_price}} {{quote_currency}} {{remaining_quantity_perc}}% of the initial position', title='Close Market Short', tooltip='Alert message emitted when closed short position.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_214__=input.text_area(defval='Long Exit({{ticker}}): Sold with limit or stop exit order at the price of {{exit_price}} {{quote_currency}} {{remaining_quantity_perc}}% of the initial position', title='Exit Limit Long', tooltip='Alert message emitted when exited long position with a limit or stop order.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_215__=input.text_area(defval='Short Exit({{ticker}}): Bought with limit or stop exit order at the price of {{exit_price}} {{quote_currency}} {{remaining_quantity_perc}}% of the initial position', title='Exit Limit Short', tooltip='Alert message emitted when exited short position with a limit or stop order.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_216__=input.text_area(defval='Close All({{ticker}}): Closed all positions at market price of {{exit_price}} {{quote_currency}}', title='Close All', tooltip='Alert message emitted when closed all positions.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    msgTakeProfitEnabled=input.bool(defval=False, title='Enable Take Profit Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "profit order fills" of the strategy (e.g. take profit "partial" exit).' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_218__=input.text_area(defval='Long Exit({{ticker}}): Take Profit 1 executed at the price of {{take_profit_price_1}} {{quote_currency}} and sold {{take_profit_quantity_perc_1}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_1}} {{base_currency}}', title='TP1 Long', tooltip='Alert message emitted when the first take profit price target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_219__=input.text_area(defval='Short Exit({{ticker}}): Take Profit 1 executed at the price of {{take_profit_price_1}} {{quote_currency}} and bought {{take_profit_quantity_perc_1}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_1}} {{base_currency}}', title='TP1 Short', tooltip='Alert message emitted when the first take profit price target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_220__=input.text_area(defval='Long Exit({{ticker}}): Take Profit 2 executed at the price of {{take_profit_price_2}} {{quote_currency}} and sold {{take_profit_quantity_perc_2}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_2}} {{base_currency}}', title='TP2 Long', tooltip='Alert message emitted when the second take profit price target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_221__=input.text_area(defval='Short Exit({{ticker}}): Take Profit 2 executed at the price of {{take_profit_price_2}} {{quote_currency}} and bought {{take_profit_quantity_perc_2}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_2}} {{base_currency}}', title='TP2 Short', tooltip='Alert message emitted when the second take profit price target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_222__=input.text_area(defval='Long Exit({{ticker}}): Take Profit 3 executed at the price of {{take_profit_price_3}} {{quote_currency}} and sold {{take_profit_quantity_perc_3}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_3}} {{base_currency}}', title='TP3 Long', tooltip='Alert message emitted when the third take profit price target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_223__=input.text_area(defval='Short Exit({{ticker}}): Take Profit 3 executed at the price of {{take_profit_price_3}} {{quote_currency}} and bought {{take_profit_quantity_perc_3}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_3}} {{base_currency}}', title='TP3 Short', tooltip='Alert message emitted when the third take profit price target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_224__=input.text_area(defval='Long Exit({{ticker}}): Take Profit 4 executed at the price of {{take_profit_price_4}} {{quote_currency}} and sold {{take_profit_quantity_perc_4}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_4}} {{base_currency}}', title='TP4 Long', tooltip='Alert message emitted when the forth take profit price target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_225__=input.text_area(defval='Short Exit({{ticker}}): Take Profit 4 executed at the price of {{take_profit_price_4}} {{quote_currency}} and bought {{take_profit_quantity_perc_4}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_4}} {{base_currency}}', title='TP4 Short', tooltip='Alert message emitted when the forth take profit price target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_226__=input.text_area(defval='Long Exit({{ticker}}): Take Profit 5 executed at the price of {{take_profit_price_5}} {{quote_currency}} and sold {{take_profit_quantity_perc_5}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_5}} {{base_currency}}', title='TP5 Long', tooltip='Alert message emitted when the fifth take profit price target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_227__=input.text_area(defval='Short Exit({{ticker}}): Take Profit 5 executed at the price of {{take_profit_price_5}} {{quote_currency}} and bought {{take_profit_quantity_perc_5}}% of the initial position, that equals to an amount of {{take_profit_base_quantity_5}} {{base_currency}}', title='TP5 Short', tooltip='Alert message emitted when the fifth take profit price target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    msgStopLossEnabled=input.bool(defval=False, title='Enable Stop Loss Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "stop_loss order fills" of the strategy (e.g. stop loss exit).' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_229__=input.text_area(defval='Long Exit({{ticker}}): Stop Loss executed at the price of {{stop_loss_price}} {{quote_currency}} and sold {{remaining_quantity_perc}}% of the initial position, that equals to an amount of {{remaining_base_quantity}} {{base_currency}}', title='SL Long', tooltip='Alert message emitted when the last stop loss target for the long position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    __input_230__=input.text_area(defval='Short Exit({{ticker}}): Stop Loss executed at the price of {{stop_loss_price}} {{quote_currency}} and bought {{remaining_quantity_perc}}% of the initial position, that equals to an amount of {{remaining_base_quantity}} {{base_currency}}', title='SL Short', tooltip='Alert message emitted when the last stop loss target for the short position is reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    msgChgTrEntryEnabled=input.bool(defval=False, title='Enable Tr Entry Change Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "alert() function calls" when the trailing limit, stop or stop-limit entry price changes.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_232__=input.text_area(defval='Long Trailing Entry Update({{ticker}}): Long trailing limit, stop or stop-limit entry order changed and set at a new price of {{entry_price}} {{quote_currency}}', title='Chg Tr Entry Long', tooltip='Alert message emitted when long trailing limit, stop or stop-limit entry order changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    __input_233__=input.text_area(defval='Short Trailing Entry Update({{ticker}}): Short trailing limit, stop or stop-limit entry order changed and set at a new price of {{entry_price}} {{quote_currency}}', title='Chg Tr Entry Short', tooltip='Alert message emitted when short trailing limit, stop or stop-limit entry order changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    msgChgTrExitEnabled=input.bool(defval=False, title='Enable Tr Exit Change Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "alert() function calls" when the trailing limit or stop exit price changes.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_235__=input.text_area(defval='Long Trailing Exit Update({{ticker}}): Long trailing limit or stop exit order changed and set at a new price of {{exit_price}} {{quote_currency}}', title='Chg Tr Exit Long', tooltip='Alert message emitted when long trailing limit or stop exit order changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    __input_236__=input.text_area(defval='Short Trailing Exit Update({{ticker}}): Short trailing limit or stop exit order changed and set at a new price of {{exit_price}} {{quote_currency}}', title='Chg Tr Exit Short', tooltip='Alert message emitted when short trailing limit or stop exit order changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    msgChgSLEnabled=input.bool(defval=False, title='Enable Stop Loss Change Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "alert() function calls" when the stop loss price changes.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_238__=input.text_area(defval='Long Stop Loss Update({{ticker}}): Stop Loss value changed and set at a new price of {{stop_loss_price}} {{quote_currency}}', title='Chg SL Long', tooltip='Alert message emitted when the stop loss target for the long position changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    __input_239__=input.text_area(defval='Short Stop Loss Update({{ticker}}): Stop Loss value changed and set at a new price of {{stop_loss_price}} {{quote_currency}}', title='Chg SL Short', tooltip='Alert message emitted when the stop loss target for the short position changed. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    msgCnlLimitOrStopEntryEnabled=input.bool(defval=False, title='Enable Limit Entry Cancel Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "alert() function calls" when use limit, stop or stop-limit order for entry and it cancels.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_241__=input.text_area(defval='Long Limit Entry Cancel({{ticker}}): Long limit, stop or stop-limit entry order canceled', title='Cnl Limit Entry Long', tooltip='Alert message emitted when long limit, stop or stop-limit entry order canceled. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    __input_242__=input.text_area(defval='Short Limit Entry Cancel({{ticker}}): Short limit, stop or stop-limit entry order canceled', title='Cnl Limit Entry Short', tooltip='Alert message emitted when short limit, stop or stop-limit entry order canceled. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    msgCnlLimitOrStopExitEnabled=input.bool(defval=False, title='Enable Limit Exit Cancel Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to "alert() function calls" when use limit or stop order for exit and it cancels.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_244__=input.text_area(defval='Long Limit Exit Cancel({{ticker}}): Long limit or stop exit order canceled', title='Cnl Limit Exit Long', tooltip='Alert message emitted when long limit or stop exit order canceled. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    __input_245__=input.text_area(defval='Short Limit Exit Cancel({{ticker}}): Short limit or stop exit order canceled', title='Cnl Limit Exit Short', tooltip='Alert message emitted when short limit or stop exit order canceled. In the "Condition" combobox of the "Create Alert" dialog, the "Order fills and alert() function calls" or the "alert() function calls only" options should be selected to be able to receive this alert message.', group=GROUP_ALERTS, display=display.none),
    msgRiskManagementEnabled=input.bool(defval=False, title='Enable Risk Management Alerts⚠️🐌', tooltip='Enable the alert messages that correspond to max draw down, max intraday loss, max daily orders and max consecutive loss days reached events.' + TT_COMPUTATIONAL_HEAVY_WARNING, group=GROUP_ALERTS, display=display.none),
    __input_247__=input.text_area(defval='Risk Management‌​​​​​‌⁠‌‌‌​‌​‌⁠‌‌‌​‌​​⁠‌‌​‌​​​⁠‌‌​‌‌‌‌⁠‌‌‌​​‌​⁠‌‌‌​‌​⁠‌​​​​​⁠‌​​​​​​⁠‌‌​‌​‌​⁠‌‌​​​​‌⁠‌‌‌​​‌‌⁠‌‌​‌‌‌‌⁠‌‌​‌‌‌​⁠‌‌​‌​‌⁠‌‌​‌​​⁠‌‌‌​​​⁠‌‌​​​​⁠‌​‌‌​​⁠‌​​​​​⁠‌​‌​​‌‌⁠‌‌​​​‌‌⁠‌‌‌​​‌​⁠‌‌​‌​​‌⁠‌‌‌​​​​⁠‌‌‌​‌​​⁠‌‌‌​‌​⁠‌​​​​​⁠‌​‌​‌​​⁠‌​‌​‌​​⁠‌​‌​​‌‌⁠‌‌‌​‌‌​⁠‌‌​‌​‌⁠‌‌​​‌‌ was activated: All pending orders are canceled, all open positions are closed and no new orders can be placed! RIP⚰️', title='Risk Management', tooltip='Alert message emitted when the risk management limits are reached.' + TT_ALERT_MESSAGE_EXPLANATION, group=GROUP_ALERTS, display=display.none),
    showAlertsEnabled=input.bool(defval=False, title='Show Alerts', tooltip='Show alert messages that correspond to events in the chart.', group=GROUP_DEBUG, display=display.data_window),
    debugModeEnabled=input.bool(defval=False, title='Debug Mode', tooltip='Enable debug mode.', group=GROUP_DEBUG, display=display.data_window),
    feedbackFramework=input.text_area(defval='I encourage you to give constructive feedback 🔄 in the publication comments with both success and failure stories using this framework. Please send me a direct message if you found some "bizarre" behavior 🐞, or you just don\'t understand the way some "things" are done, or simply you are strongly opinionated 🤔 doing "things" differently!', title='Feedback', tooltip='For more information on how this framework functions, please refer to the description of the publication.', group=GROUP_SUPPORT, display=display.none),
    donateFramework=input.text_area(defval='I tend to convert coffee ☕ to code 📰, I am a coffee-to-code converter 👨🏻‍💻 a.k.a. CCC. If you like the progress this framework has done so far, don\'t miss the chance to give it some fuel ⛽, so I can continue to operate as a CCC!', title='Donate', tooltip='For more information on payment methods, please check my signature at the end of the publication.', group=GROUP_SUPPORT, display=display.none),
    sponsorFrameworkAuthor=input.text_area(defval='Some of the features ✨ you are using now had been sponsored by other community members in the past. If you have a feature ✨ request in mind that it is strategy-agnostic and generic enough to be included in this framework, you can sponsor 🤝 it\'s implementation and give back to the community! Reach me out 📧 to discuss the integration of the feature and your vision!', title='Sponsor', tooltip='For more information about current project availability please contact me.', group=GROUP_SUPPORT, display=display.none),
    hireAuthor=input.text_area(defval='If you have a trading idea 💡 that seeks a robust implementation ✍️ and takes advantage of the rich feature ✨ set of this framework do not hesitate to reach out 📧 to me!', title='Hire', tooltip='For more information about current project availability please contact me.', group=GROUP_SUPPORT, display=display.none),
    scriptVer=input.string(defval='v53', title='Script Version', display=display.data_window)
):
    modCount: int = 0

    referenceTimezone: Persistent = method_call('to_string', referenceTimezone__input)
    dateTimeWindow: Persistent[chr.DateTimeWindow] = method_call('init', chr.DateTimeWindow.new(), fromDateTime=__input_3__ if fromEnabled else na, toDateTime=__input_4__ if toEnabled else na, refTimezone=referenceTimezone, chTimezone=method_call('to_string', __input_5__))
    days: Persistent = method_call('init', chr.SessionDays.new(), sun=__input_7__, mon=__input_8__, tue=__input_9__, wed=__input_10__, thu=__input_11__, fri=__input_12__, sat=__input_13__) if daysEnabled else na
    timeRange: Persistent = method_call('from_sess_string', chr.SessionTimeRange.new(), sess=__input_15__, refTimezone=referenceTimezone) if timeRangeEnabled else na

    sess: Persistent[chr.Session] = method_call('init', chr.Session.new(), days, array.from_items(timeRange))

    dateFilterApproval: bool = method_call('is_bar_included', dateTimeWindow)
    sessionFilterApproval: bool = method_call('is_bar_included', sess)
    timeFilterApproval: Series[bool] = dateFilterApproval and sessionFilterApproval

    modCount += 1

    bgcolor(color=na if timeFilterApproval else color.new(color.new('#FF0000'), 95), offset=1, title='Filter', force_overlay=True)

    currentPositionSize: float = strategy.opentrades.size(strategy.opentrades - 1)
    isLongPosition: bool = currentPositionSize > 0
    isShortPosition: bool = currentPositionSize < 0
    isFlatPosition: bool = currentPositionSize == 0

    LONG_ORDER_ID_ENTRY: str = string.format('{0} {1}', LONG_ORDER_ID_PREFIX, ENTRY_ORDER_ID_POSTFIX)
    SHORT_ORDER_ID_ENTRY: str = string.format('{0} {1}', SHORT_ORDER_ID_PREFIX, ENTRY_ORDER_ID_POSTFIX)
    LONG_ORDER_ID_CLOSE: str = string.format('Close entry(s) order {0}', LONG_ORDER_ID_ENTRY)
    SHORT_ORDER_ID_CLOSE: str = string.format('Close entry(s) order {0}', SHORT_ORDER_ID_ENTRY)

    def closedTradesExitId(n: int):
        return strategy.closedtrades.exit_id(strategy.closedtrades - n)

    def closedTradeExitIdContains(prefix: str, n: int = 1):
        return string.contains(closedTradesExitId(n), prefix) if strategy.closedtrades >= n else False

    def closedTradeExitIdIs(exitId: str, n: int = 1):
        return closedTradesExitId(n) == exitId if strategy.closedtrades >= n else False

    def closedTradesExitBarIndex(n: int):
        return strategy.closedtrades.exit_bar_index(strategy.closedtrades - n)

    def closedTradesExitPrice(n: int):
        return strategy.closedtrades.exit_price(strategy.closedtrades - n)

    def lastTwoClosedTradesExitedInTheSameBar():
        return closedTradesExitBarIndex(2) == closedTradesExitBarIndex(1) if strategy.closedtrades >= 2 else False

    def openTradeEntryIdStartsWith(prefix: str, n: int = 1):
        return string.startswith(strategy.opentrades.entry_id(strategy.opentrades - n), prefix)

    if barstate.isfirst:
        log.warning(method_call('desteganographize', 'Greet\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200bings'))

    lastLongExitBarIndex: Persistent[int] = na(int)
    lastLongExitPrice: Persistent[float] = na(float)
    if not isLongPosition:
        if closedTradeExitIdIs(SHORT_ORDER_ID_ENTRY) or closedTradeExitIdContains(LONG_ORDER_ID_PREFIX):
            lastLongExitBarIndex = closedTradesExitBarIndex(1)
            lastLongExitPrice = closedTradesExitPrice(1)
        elif lastTwoClosedTradesExitedInTheSameBar() and (closedTradeExitIdIs(SHORT_ORDER_ID_ENTRY, 2) or closedTradeExitIdContains(LONG_ORDER_ID_PREFIX, 2)):
            lastLongExitBarIndex = closedTradesExitBarIndex(2)
            lastLongExitPrice = closedTradesExitPrice(2)

    lastShortExitBarIndex: Persistent[int] = na(int)
    lastShortExitPrice: Persistent[float] = na(float)
    if not isShortPosition:
        if closedTradeExitIdIs(LONG_ORDER_ID_ENTRY) or closedTradeExitIdContains(SHORT_ORDER_ID_PREFIX):
            lastShortExitBarIndex = closedTradesExitBarIndex(1)
            lastShortExitPrice = closedTradesExitPrice(1)
        elif lastTwoClosedTradesExitedInTheSameBar() and (closedTradeExitIdIs(LONG_ORDER_ID_ENTRY, 2) or closedTradeExitIdContains(SHORT_ORDER_ID_PREFIX, 2)):
            lastShortExitBarIndex = closedTradesExitBarIndex(2)
            lastShortExitPrice = closedTradesExitPrice(2)

    enteredLongTrade: bool = bar_index == strategy.opentrades.entry_bar_index(strategy.opentrades - 1) and openTradeEntryIdStartsWith(LONG_ORDER_ID_PREFIX) if strategy.opentrades > 0 else False
    enteredShortTrade: bool = bar_index == strategy.opentrades.entry_bar_index(strategy.opentrades - 1) and openTradeEntryIdStartsWith(SHORT_ORDER_ID_PREFIX) if strategy.opentrades > 0 else False

    completedLongTrade: bool = bar_index == lastLongExitBarIndex if strategy.closedtrades > 0 else False
    completedShortTrade: bool = bar_index == lastShortExitBarIndex if strategy.closedtrades > 0 else False

    modCount += 1


    signal: Series = cast_int(__input_17__)

    BG_COLOR: Color = chart.bg_color
    FG_COLOR: Color = chart.fg_color

    commissionRatio = __input_31__ / 100.0

    dealConditions: Persistent[conv.DealConditions] = conv.DealConditions.new()
    twoMaDrawings: Persistent[tma.TwoMaDrawings] = tma.TwoMaDrawings.new()

    if dealMode == DealConditionsMode.internal:
        announcement: Persistent = method_call('announce', '⚠️ Please connect a 🔌Signal that is compatible with the TTS Framework.\nThe Two MA signal logic is for demonstration purposes only!', textColor=color.new(color.new('#FF9800'), 70), position=position.middle_center)
        emaLine: float = request.security(symbol=syminfo.tickerid, timeframe=emaTimeframe, expression=inline_series(ta.ema(emaSrc, emaLength), 1)) if emaFilterEnabled else na
        emaAtr: float = filterAtrMul * ta.atr(filterAtrLength) if emaAtrBandEnabled else na
        twoMaDrawings = tma.TwoMaDrawings.new(fastMA=col.cust_series(fastMaLength, fastMaType), slowMA=col.cust_series(slowMaLength, slowMaType), emaLine=emaLine, emaUpperBand=emaLine + emaAtr, emaLowerBand=emaLine - emaAtr)

        dealConditions = tma.getDealConditions(twoMaDrawings, longDealsEnabled, shortDealsEnabled, endDealsEnabled, cnlStartDealsEnabled, cnlEndDealsEnabled, emaFilterEnabled, emaAtrBandEnabled, adxFilterEnabled, adxSmoothing, diLength, adxThreshold)
    elif not signal == signal[1]:
        dealConditions = conv.getDealConditions(signal)

    reverseOrderApproval: bool = True if reverseOrdersEnabled else isFlatPosition

    barsSinceCompletedLong: int = nz(ta.barssince(completedLongTrade), MAX_LIMIT_INT)
    barsSinceCompletedShort: int = nz(ta.barssince(completedShortTrade), MAX_LIMIT_INT)
    cooldownApproval: bool = math.min(barsSinceCompletedLong, barsSinceCompletedShort) >= cooldownBars if cooldownEnabled else True

    openLongPosition: bool = timeFilterApproval and dealConditions.startLongDeal and cooldownApproval and reverseOrderApproval
    openShortPosition: bool = timeFilterApproval and dealConditions.startShortDeal and cooldownApproval and reverseOrderApproval

    cnlOpenLongPosition: bool = timeFilterApproval and dealConditions.cnlStartLongDeal or (not timeFilterApproval and timeFilterApproval[1])
    cnlOpenShortPosition: bool = timeFilterApproval and dealConditions.cnlStartShortDeal or (not timeFilterApproval and timeFilterApproval[1])

    validOpenLongPosition: bool = openLongPosition and (not isLongPosition)
    validOpenShortPosition: bool = openShortPosition and (not isShortPosition)
    validOpenPosition: bool = validOpenLongPosition or validOpenShortPosition

    if openLongPosition and (not validOpenLongPosition):
        log.warning(LOG_OPEN_SIGNAL_WARNING, LONG_ORDER_ID_PREFIX)
    if openShortPosition and (not validOpenShortPosition):
        log.warning(LOG_OPEN_SIGNAL_WARNING, SHORT_ORDER_ID_PREFIX)

    def getLegendMap():
        legendMap: dict[str, str] = map.new()
        map.put(legendMap, '🔷🔶', 'Entry')
        map.put(legendMap, '🟪🟩🟥', 'Exit')
        map.put(legendMap, '', '')
        map.put(legendMap, '🎯', 'Take Profit')
        map.put(legendMap, '🛑', 'Stop Loss')
        map.put(legendMap, '📍', 'Stop/Limit')
        map.put(legendMap, '📈', 'Long')
        map.put(legendMap, '📉', 'Short')
        return legendMap

    modCount += 1

    plot(series=signal, title='🔌Signal', color=color.new('#808000'), editable=False, display=display.none if dealMode == DealConditionsMode.internal else display.data_window, precision=0)

    plot(series=twoMaDrawings.fastMA, title='Fast MA', color=color.yellow, linewidth=1, style=plot.style_line, display=display.all - display.status_line if dealMode == DealConditionsMode.internal else display.none, force_overlay=True)
    plot(series=twoMaDrawings.slowMA, title='Slow MA', color=color.orange, linewidth=1, style=plot.style_line, display=display.all - display.status_line if dealMode == DealConditionsMode.internal else display.none, force_overlay=True)

    EMA_COLOR: Color = color.new(FG_COLOR, 50)
    plot(series=twoMaDrawings.emaLine, color=EMA_COLOR, style=plot.style_linebr, linewidth=2, title='EMA Line', display=display.all - display.status_line if dealMode == DealConditionsMode.internal and emaFilterEnabled else display.none, force_overlay=True)
    BANDS_ENABLED: bool = dealMode == DealConditionsMode.internal and emaFilterEnabled and emaAtrBandEnabled
    EMA_BAND_FILL_COLOR: Color = color.new(EMA_COLOR, 90) if BANDS_ENABLED else na
    emaUpperBandPlot = plot(series=twoMaDrawings.emaUpperBand, color=EMA_BAND_FILL_COLOR, style=plot.style_linebr, title='EMA Upper Band', editable=False, display=display.data_window if BANDS_ENABLED else display.none, force_overlay=True)
    emaLowerBandPlot = plot(series=twoMaDrawings.emaLowerBand, color=EMA_BAND_FILL_COLOR, style=plot.style_linebr, title='EMA Lower Band', editable=False, display=display.data_window if BANDS_ENABLED else display.none, force_overlay=True)
    fill(plot1=emaUpperBandPlot, plot2=emaLowerBandPlot, color=EMA_BAND_FILL_COLOR, title='EMA Band', display=display.all if BANDS_ENABLED else display.none)

    if showLegend:
        method_call('legend', getLegendMap())



    ladderPositiveAtr: Persistent[float] = na(float)
    ladderNegativeAtr: Persistent[float] = na(float)
    ladderPositiveStDevs: Persistent[float] = na(float)
    ladderNegativeStDevs: Persistent[float] = na(float)

    def getStandardOHLC():
        __block_result__ = (na, na, na, na)
        if chart.is_standard:
            __block_result__ = (open, high, low, close)
        else:
            __block_result__ = request.security(ticker.new(prefix=syminfo.prefix, ticker=syminfo.tickerid), '', (open, high, low, close))
        return __block_result__

    stClose: Series
    stOpen, stHigh, stLow, stClose = getStandardOHLC()

    def getStandardTrueRange():
        __hist_stClose__: Series[void] = stClose[0]
        return stHigh - stLow if na(__hist_stClose__[1]) else math.max(stHigh - stLow, math.abs(stHigh - __hist_stClose__[1]), math.abs(stLow - __hist_stClose__[1]))

    if atrMethod == UpdateMethod.ladder:
        if stClose > stOpen:
            ladderPositiveAtr = col.cust_series(atrLength, atrMaType, getStandardTrueRange())
        else:
            ladderNegativeAtr = col.cust_series(atrLength, atrMaType, getStandardTrueRange())

    if stdevMethod == UpdateMethod.ladder:
        stdevSrc: float = stdevPriceSrc if stdevMode == StDevMode.price else math.log(stdevPriceSrc / stdevPriceSrc[1])
        if stClose > stOpen:
            positiveStDev: float = ta.stdev(stdevSrc, stdevLength, False)
            ladderPositiveStDevs = positiveStDev if stdevMode == StDevMode.price else stdevPriceSrc * (math.exp(positiveStDev) - 1.0)
        else:
            negativeStDev: float = ta.stdev(stdevSrc, stdevLength, False)
            ladderNegativeStDevs = negativeStDev if stdevMode == StDevMode.price else stdevPriceSrc * (math.exp(negativeStDev) - 1.0)

    dynamicAtr: float = col.cust_series(atrLength, atrMaType, getStandardTrueRange())
    staticAtr: float = ta.valuewhen(validOpenPosition, dynamicAtr, 0)
    dynamicStDev: float = ta.stdev(stdevPriceSrc, stdevLength)
    staticStDev: float = ta.valuewhen(validOpenPosition, dynamicStDev, 0)

    __block_result_1__ = na
    __switch__ = atrMethod
    if __switch__ == UpdateMethod.static:
        __block_result_1__ = staticAtr
    elif __switch__ == UpdateMethod.dynamic:
        __block_result_1__ = dynamicAtr
    elif __switch__ == UpdateMethod.ladder:
        __block_result_1__ = ladderPositiveAtr
    posAtr: float = __block_result_1__

    __block_result_2__ = na
    __switch__ = atrMethod
    if __switch__ == UpdateMethod.static:
        __block_result_2__ = staticAtr
    elif __switch__ == UpdateMethod.dynamic:
        __block_result_2__ = dynamicAtr
    elif __switch__ == UpdateMethod.ladder:
        __block_result_2__ = ladderNegativeAtr
    negAtr: float = __block_result_2__

    __block_result_3__ = na
    __switch__ = stdevMethod
    if __switch__ == UpdateMethod.static:
        __block_result_3__ = staticStDev
    elif __switch__ == UpdateMethod.dynamic:
        __block_result_3__ = dynamicStDev
    elif __switch__ == UpdateMethod.ladder:
        __block_result_3__ = ladderPositiveStDevs
    posStDev: float = __block_result_3__

    __block_result_4__ = na
    __switch__ = stdevMethod
    if __switch__ == UpdateMethod.static:
        __block_result_4__ = staticStDev
    elif __switch__ == UpdateMethod.dynamic:
        __block_result_4__ = dynamicStDev
    elif __switch__ == UpdateMethod.ladder:
        __block_result_4__ = ladderNegativeStDevs
    negStDev: float = __block_result_4__

    modCount += 1


    def getUpwardsMovingBarrierPrice(barrier: TrailBarrier):
        return stHigh if barrier == TrailBarrier.front else stLow

    def getDownwardsMovingBarrierPrice(barrier: TrailBarrier):
        return stLow if barrier == TrailBarrier.front else stHigh

    longBiasedAuxData: dr.AuxData = dr.AuxData.new(atr=posAtr, stdev=posStDev)
    shortBiasedAuxData: dr.AuxData = dr.AuxData.new(atr=negAtr, stdev=negStDev)

    modCount += 1


    entryDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=entryDistMethod, distMul=entryDistMul)
    entryBiasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_74__, distMul=__input_75__ if entryBiasEnabled else na)
    entryRestrictSettings: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_78__, minDistMul=__input_79__ if entryMinDistEnabled else na, maxDistMul=__input_80__ if entryMaxDistEnabled else na)

    longIsActive: bool = isLongPosition or (validOpenLongPosition if entryOrderType == OrderType.market else False)

    validCnlOpenLongPosition: Persistent[bool] = False

    barsSinceValidOpenLong: int = nz(ta.barssince(validOpenLongPosition), MAX_LIMIT_INT)
    barsSinceValidCnlOpenLong: int = nz(ta.barssince(validCnlOpenLongPosition), MAX_LIMIT_INT)
    barsSinceEnteredLong: int = nz(ta.barssince(enteredLongTrade), MAX_LIMIT_INT)

    openLongIsActive: bool = barsSinceValidCnlOpenLong > barsSinceValidOpenLong
    enterLongIsPending: bool = barsSinceEnteredLong >= barsSinceValidOpenLong

    validCnlOpenLongPosition = (cnlOpenLongPosition or validOpenShortPosition or (timeFilterApproval and dealConditions.endLongDeal if treatCloseAsCancel else False) or (enteredShortTrade if treatEntryAsCancel else False)) and (not isLongPosition) and openLongIsActive and enterLongIsPending and (not validOpenLongPosition) if entryOrderType != OrderType.market else False

    if cnlOpenLongPosition and (not validCnlOpenLongPosition) if entryOrderType != OrderType.market else False:
        log.warning(LOG_CNL_OPEN_SIGNAL_WARNING, LONG_ORDER_ID_PREFIX)

    IS_ENTRY_DIST_METHOD_CUST: bool = entryDistMethod == dr.DistMethod.cust
    entryCustHigherPrice: float = math.round_to_mintick(col.cust_series(entryDistMul, entryCustHigherType, entryCustHigherSrc)) if IS_ENTRY_DIST_METHOD_CUST else na

    def getLongEntryHigherPrice(referencePrice: float):
        return method_call('higher_long_biased_price', entryDistSettings, referencePrice, longBiasedAuxData, entryRestrictSettings, entryBiasSettings, entryCustHigherPrice)

    entryCustLowerPrice: float = math.round_to_mintick(col.cust_series(entryDistMul, entryCustLowerType, entryCustLowerSrc)) if IS_ENTRY_DIST_METHOD_CUST else na

    def getLongEntryLowerPrice(referencePrice: float):
        return method_call('lower_long_biased_price', entryDistSettings, referencePrice, longBiasedAuxData, entryRestrictSettings, entryBiasSettings, entryCustLowerPrice)

    longLimitOrStopEntryPrice: PersistentSeries[float] = na(float)
    isFirstValidOpenLongPosition: bool = validOpenLongPosition and (na(longLimitOrStopEntryPrice[1]) or completedLongTrade) if entryOrderType != OrderType.market else False
    tryEnterLongPosition: bool = timeFilterApproval and (not isLongPosition) and (not completedLongTrade) and (not na(longLimitOrStopEntryPrice[1])) and (not validCnlOpenLongPosition) if entryOrderType != OrderType.market else False
    __block_result_5__ = na
    if isFirstValidOpenLongPosition:
        __block_result_6__ = na
        if entryOrderType == OrderType.limit:
            __block_result_6__ = getLongEntryLowerPrice(stClose)
        elif entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit:
            __block_result_6__ = getLongEntryHigherPrice(stClose)
        __block_result_5__ = __block_result_6__
    elif tryEnterLongPosition:
        __block_result_7__ = na
        if entryTrailMode == TrailMode.trail or (entryTrailMode == TrailMode.fixed and validOpenLongPosition):
            __block_result_8__ = na
            if entryOrderType == OrderType.limit:
                __block_result_8__ = math.max(getLongEntryLowerPrice(getUpwardsMovingBarrierPrice(entryTrailBarrier)), nz(longLimitOrStopEntryPrice[1], MIN_LIMIT_FLOAT))
            elif entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit:
                __block_result_8__ = math.min(getLongEntryHigherPrice(getDownwardsMovingBarrierPrice(entryTrailBarrier)), nz(longLimitOrStopEntryPrice[1], MAX_LIMIT_FLOAT))
            __block_result_7__ = __block_result_8__
        else:
            __block_result_7__ = nz(longLimitOrStopEntryPrice[1], MAX_LIMIT_FLOAT)
        __block_result_5__ = __block_result_7__
    longLimitOrStopEntryPrice = __block_result_5__

    longStopLimitEntryPrice: float = longLimitOrStopEntryPrice + entryStopLimitDistMul * (posAtr if entryStopLimitDistMethod == StopLimitDistMethod.atr else posStDev if entryStopLimitDistMethod == StopLimitDistMethod.stdev else syminfo.mintick) if entryOrderType == OrderType.stopLimit else na

    longStopLimitStopEntryExecuted: Persistent[bool] = False
    if ta.crossover(stHigh, longLimitOrStopEntryPrice[1]) and entryOrderType == OrderType.stopLimit and (not enteredLongTrade):
        longStopLimitStopEntryExecuted = True
    elif enteredLongTrade:
        longStopLimitStopEntryExecuted = False

    longLimitOrStopEntryIsActive: Series[bool] = not na(longLimitOrStopEntryPrice)

    shortIsActive: bool = isShortPosition or (validOpenShortPosition if entryOrderType == OrderType.market else False)

    validCnlOpenShortPosition: Persistent[bool] = False

    barsSinceValidOpenShort: int = nz(ta.barssince(validOpenShortPosition), MAX_LIMIT_INT)
    barsSinceValidCnlOpenShort: int = nz(ta.barssince(validCnlOpenShortPosition), MAX_LIMIT_INT)
    barsSinceEnteredShort: int = nz(ta.barssince(enteredShortTrade), MAX_LIMIT_INT)

    openShortIsActive: bool = barsSinceValidCnlOpenShort > barsSinceValidOpenShort
    enterShortIsPending: bool = barsSinceEnteredShort >= barsSinceValidOpenShort

    validCnlOpenShortPosition = (cnlOpenShortPosition or validOpenLongPosition or (timeFilterApproval and dealConditions.endShortDeal if treatCloseAsCancel else False) or (enteredLongTrade if treatEntryAsCancel else False)) and (not isShortPosition) and openShortIsActive and enterShortIsPending and (not validOpenShortPosition) if entryOrderType != OrderType.market else False

    if cnlOpenShortPosition and (not validCnlOpenShortPosition) if entryOrderType != OrderType.market else False:
        log.warning(LOG_CNL_OPEN_SIGNAL_WARNING, SHORT_ORDER_ID_PREFIX)

    def getShortEntryHigherPrice(referencePrice: float):
        return method_call('higher_short_biased_price', entryDistSettings, referencePrice, shortBiasedAuxData, entryRestrictSettings, entryBiasSettings, entryCustHigherPrice)

    def getShortEntryLowerPrice(referencePrice: float):
        return method_call('lower_short_biased_price', entryDistSettings, referencePrice, shortBiasedAuxData, entryRestrictSettings, entryBiasSettings, entryCustLowerPrice)

    shortLimitOrStopEntryPrice: PersistentSeries[float] = na(float)
    isFirstValidOpenShortPosition: bool = validOpenShortPosition and (na(shortLimitOrStopEntryPrice[1]) or completedShortTrade) if entryOrderType != OrderType.market else False
    tryEnterShortPosition: bool = timeFilterApproval and (not isShortPosition) and (not completedShortTrade) and (not na(shortLimitOrStopEntryPrice[1])) and (not validCnlOpenShortPosition) if entryOrderType != OrderType.market else False
    __block_result_9__ = na
    if isFirstValidOpenShortPosition:
        __block_result_10__ = na
        if entryOrderType == OrderType.limit:
            __block_result_10__ = getShortEntryHigherPrice(stClose)
        elif entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit:
            __block_result_10__ = getShortEntryLowerPrice(stClose)
        __block_result_9__ = __block_result_10__
    elif tryEnterShortPosition:
        __block_result_11__ = na
        if entryTrailMode == TrailMode.trail or (entryTrailMode == TrailMode.fixed and validOpenShortPosition):
            __block_result_12__ = na
            if entryOrderType == OrderType.limit:
                __block_result_12__ = math.min(getShortEntryHigherPrice(getDownwardsMovingBarrierPrice(entryTrailBarrier)), nz(shortLimitOrStopEntryPrice[1], MAX_LIMIT_FLOAT))
            elif entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit:
                __block_result_12__ = math.max(getShortEntryLowerPrice(getUpwardsMovingBarrierPrice(entryTrailBarrier)), nz(shortLimitOrStopEntryPrice[1], MIN_LIMIT_FLOAT))
            __block_result_11__ = __block_result_12__
        else:
            __block_result_11__ = nz(shortLimitOrStopEntryPrice[1], MIN_LIMIT_FLOAT)
        __block_result_9__ = __block_result_11__
    shortLimitOrStopEntryPrice = __block_result_9__

    shortStopLimitEntryPrice: float = shortLimitOrStopEntryPrice - entryStopLimitDistMul * (negAtr if entryStopLimitDistMethod == StopLimitDistMethod.atr else negStDev if entryStopLimitDistMethod == StopLimitDistMethod.stdev else syminfo.mintick) if entryOrderType == OrderType.stopLimit else na

    shortStopLimitStopEntryExecuted: Persistent[bool] = False
    if ta.crossunder(stLow, shortLimitOrStopEntryPrice[1]) and entryOrderType == OrderType.stopLimit and (not enteredShortTrade):
        shortStopLimitStopEntryExecuted = True
    elif enteredShortTrade:
        shortStopLimitStopEntryExecuted = False

    shortLimitOrStopEntryIsActive: Series[bool] = not na(shortLimitOrStopEntryPrice)

    longEntryBarId: int = ta.valuewhen(enteredLongTrade, bar_index[1] if entryOrderType == OrderType.market else bar_index, 0)
    shortEntryBarId: int = ta.valuewhen(enteredShortTrade, bar_index[1] if entryOrderType == OrderType.market else bar_index, 0)

    posPrice: float = strategy.opentrades.entry_price(strategy.opentrades - 1)

    longEntryPrice: Series[float] = posPrice if not na(posPrice) and isLongPosition and (not validOpenLongPosition) else (longStopLimitEntryPrice if longStopLimitStopEntryExecuted else longLimitOrStopEntryPrice) if longLimitOrStopEntryIsActive else stClose if validOpenLongPosition and entryOrderType == OrderType.market else na

    shortEntryPrice: Series[float] = posPrice if not na(posPrice) and isShortPosition and (not validOpenShortPosition) else (shortStopLimitEntryPrice if shortStopLimitStopEntryExecuted else shortLimitOrStopEntryPrice) if shortLimitOrStopEntryIsActive else stClose if validOpenShortPosition and entryOrderType == OrderType.market else na

    modCount += 1

    if validCnlOpenLongPosition and showCnlOpenLabels and barstate.isconfirmed:
        label.new(point=chart.point.now(nz(longEntryPrice[1], stClose)), text='Cancel', color=longCnlOpenColor, style=label.style_label_up if entryOrderType == OrderType.limit else label.style_label_down, textcolor=FG_COLOR, size=size.small, force_overlay=True)
    if validCnlOpenShortPosition and showCnlOpenLabels and barstate.isconfirmed:
        label.new(point=chart.point.now(nz(shortEntryPrice[1], stClose)), text='Cancel', color=shortCnlOpenColor, style=label.style_label_down if entryOrderType == OrderType.limit else label.style_label_up, textcolor=FG_COLOR, size=size.small, force_overlay=True)

    longLimitOrStopEntryPlot = plot(series=longLimitOrStopEntryPrice, title='Long Limit or Stop Entry', color=na if longStopLimitStopEntryExecuted else longEntryColor, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True)
    longStopLimitEntryPlot = plot(series=longStopLimitEntryPrice, title='Long Stop-Limit Entry', color=longEntryColor if longStopLimitStopEntryExecuted else na, linewidth=1, style=plot.style_linebr, offset=1, display=display.pane + display.data_window, force_overlay=True)
    LONG_ENTRY_FILL_COLOR: Color = color.new(longEntryColor, 90) if entryOrderType == OrderType.stopLimit and entryStopLimitDistMul > 0.0 else na
    fill(plot1=longLimitOrStopEntryPlot, plot2=longStopLimitEntryPlot, color=LONG_ENTRY_FILL_COLOR, title='Long Stop-Limit Distance')

    shortLimitOrStopEntryPlot = plot(series=shortLimitOrStopEntryPrice, title='Short Limit or Stop Entry', color=na if shortStopLimitStopEntryExecuted else shortEntryColor, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True)
    shortStopLimitEntryPlot = plot(series=shortStopLimitEntryPrice, title='Short Stop-Limit Entry', color=shortEntryColor if shortStopLimitStopEntryExecuted else na, linewidth=1, style=plot.style_linebr, offset=1, display=display.pane + display.data_window, force_overlay=True)
    SHORT_ENTRY_FILL_COLOR: Color = color.new(shortEntryColor, 90) if entryOrderType == OrderType.stopLimit and entryStopLimitDistMul > 0.0 else na
    fill(plot1=shortLimitOrStopEntryPlot, plot2=shortStopLimitEntryPlot, color=SHORT_ENTRY_FILL_COLOR, title='Short Stop-Limit Distance')

    longTakeProfitPrices: PersistentSeries[list[float]] = array.new_float(numOfTakeProfitTargets, na)
    shortTakeProfitPrices: PersistentSeries[list[float]] = array.new_float(numOfTakeProfitTargets, na)

    longTrailTakeProfitOffsetTicks: Persistent[list[int]] = array.new_int(numOfTakeProfitTargets, na)
    shortTrailTakeProfitOffsetTicks: Persistent[list[int]] = array.new_int(numOfTakeProfitTargets, na)

    longTrailTakeProfitExecuted: Persistent[list[bool]] = array.new_bool(numOfTakeProfitTargets, False)
    shortTrailTakeProfitExecuted: Persistent[list[bool]] = array.new_bool(numOfTakeProfitTargets, False)

    TAKE_PROFIT_TARGETS_SIZE: int = numOfTakeProfitTargets - 1 if numOfTakeProfitTargets - 1 >= 0 else na

    longTrailTakeProfitExecutedCount: int = 0
    shortTrailTakeProfitExecutedCount: int = 0

    highestHighSinceLongEntry: PersistentSeries[float] = na(float)
    if enteredLongTrade:
        highestHighSinceLongEntry = stHigh
    elif isLongPosition or completedLongTrade:
        highestHighSinceLongEntry = math.max(stHigh, nz(highestHighSinceLongEntry[1], stHigh))

    for i, longTakeProfitPrice in enumerate(longTakeProfitPrices):
        justExecuted: bool = False
        for j in pine_range(0, TAKE_PROFIT_TARGETS_SIZE + 1):
            justExecuted = justExecuted or (bar_index == strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1 - j) and strategy.closedtrades.exit_id(strategy.closedtrades - 1 - j) == string.format(EXIT_ORDER_ID_PATTERN_1, LONG_ORDER_ID_PREFIX, i + 1) and (strategy.closedtrades.profit(strategy.closedtrades - 1 - j) > 0.0) if strategy.closedtrades > j else False)
        executed: bool = array.get(longTrailTakeProfitExecuted, i) or (justExecuted and highestHighSinceLongEntry >= longTakeProfitPrice) if isLongPosition or completedLongTrade else False
        array.set(longTrailTakeProfitExecuted, i, executed)
        if executed:
            longTrailTakeProfitExecutedCount = longTrailTakeProfitExecutedCount + 1

    lowestLowSinceShortEntry: PersistentSeries[float] = na(float)
    if enteredShortTrade:
        lowestLowSinceShortEntry = stLow
    elif isShortPosition or completedShortTrade:
        lowestLowSinceShortEntry = math.min(stLow, nz(lowestLowSinceShortEntry[1], stLow))

    for i, shortTakeProfitPrice in enumerate(shortTakeProfitPrices):
        justExecuted: bool = False
        for j in pine_range(0, TAKE_PROFIT_TARGETS_SIZE + 1):
            justExecuted = justExecuted or (bar_index == strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1 - j) and strategy.closedtrades.exit_id(strategy.closedtrades - 1 - j) == string.format(EXIT_ORDER_ID_PATTERN_1, SHORT_ORDER_ID_PREFIX, i + 1) and (strategy.closedtrades.profit(strategy.closedtrades - 1 - j) > 0.0) if strategy.closedtrades > j else False)
        executed: bool = array.get(shortTrailTakeProfitExecuted, i) or (justExecuted and lowestLowSinceShortEntry <= shortTakeProfitPrice) if isShortPosition or completedShortTrade else False
        array.set(shortTrailTakeProfitExecuted, i, executed)
        if executed:
            shortTrailTakeProfitExecutedCount = shortTrailTakeProfitExecutedCount + 1

    def longIthTrailTakeProfitExecuted(i: int):
        return array.get(longTrailTakeProfitExecuted, i - 1) if numOfTakeProfitTargets >= i else False

    def shortIthTrailTakeProfitExecuted(i: int):
        return array.get(shortTrailTakeProfitExecuted, i - 1) if numOfTakeProfitTargets >= i else False

    modCount += 1

    longStopLossDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=stopLossDistMethod, distMul=longStopLossDistMul)
    stopLossBiasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_95__, distMul=__input_96__ if stopLossBiasEnabled else na)
    stopLossRestrictSettings: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_99__, minDistMul=__input_100__ if stopLossMinDistEnabled else na, maxDistMul=__input_101__ if stopLossMaxDistEnabled else na)
    shortStopLossDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=longStopLossDistSettings.distMethod, distMul=shortStopLossDistMul)

    stopLossMoveDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_105__, distMul=__input_106__)

    IS_STOP_LOSS_DIST_METHOD_CUST: bool = stopLossDistMethod == dr.DistMethod.cust
    stopLossCustLowerPrice: float = math.round_to_mintick(col.cust_series(longStopLossDistMul, stopLossCustLowerType, stopLossCustLowerSrc)) if IS_STOP_LOSS_DIST_METHOD_CUST else na

    def getLongStopLossPrice(referencePrice: float):
        __block_result_13__ = na
        if stopLossStepTrailDistEnabled:
            steppedDist = udt_copy(longStopLossDistSettings)
            steppedDist.distMul = longStopLossDistSettings.distMul + longTrailTakeProfitExecutedCount * longStopLossStepTrailDistMul
            __block_result_13__ = steppedDist
        else:
            __block_result_13__ = longStopLossDistSettings
        longStopLossSteppedDist = __block_result_13__
        return method_call('lower_short_biased_price', longStopLossSteppedDist, referencePrice, shortBiasedAuxData, stopLossRestrictSettings, stopLossBiasSettings, stopLossCustLowerPrice)

    def getLongStopLossMoveDistPrice():
        return method_call('price', stopLossMoveDistSettings, longEntryPrice, shortBiasedAuxData)

    longStopLossMoveDistPrice: float = getLongStopLossMoveDistPrice() if stopLossMoveActMode == MoveActMode.oncePrice or stopLossMoveActMode == MoveActMode.multiPrice else na
    longDistMovePriceCount: int = math.floor((highestHighSinceLongEntry - longEntryPrice) / longStopLossMoveDistPrice) if stopLossMoveActMode == MoveActMode.multiPrice else na
    chgLongDistMovePriceCount: int = ta.change(longDistMovePriceCount)

    STOP_LOSS_ADJUSTMENT_IS_NEEDED: bool = not IS_STOP_LOSS_DIST_METHOD_CUST and stopLossTrailActMode != TrailActMode.start if stopLossAdjustmentEnabled else False

    longStopLossPrice: PersistentSeries[float] = na(float)
    if longLimitOrStopEntryIsActive or validOpenLongPosition:
        longStopLossPrice = getLongStopLossPrice(longEntryPrice)
    elif enteredLongTrade and STOP_LOSS_ADJUSTMENT_IS_NEEDED:
        longStopLossPrice = longStopLossPrice + (longEntryPrice - nz(longEntryPrice[1], longEntryPrice))
    elif isLongPosition:
        longStopLossTrailEnabled: bool = stopLossTrailActMode == TrailActMode.start or (stopLossTrailActMode == TrailActMode.tp and longIthTrailTakeProfitExecuted(stopLossTrailTPActNum))
        stopPrice: float = getLongStopLossPrice(getUpwardsMovingBarrierPrice(stopLossTrailBarrier)) if longStopLossTrailEnabled else longStopLossPrice[1]
        stopPrice = math.max(stopPrice, longEntryPrice) if stopLossMoveActMode == MoveActMode.onceTp and longTrailTakeProfitExecutedCount >= stopLossMoveTPActNum or (stopLossMoveActMode == MoveActMode.oncePrice and highestHighSinceLongEntry - longEntryPrice >= longStopLossMoveDistPrice) or (stopLossMoveActMode == MoveActMode.multiTp and longTrailTakeProfitExecutedCount == 1) else math.max(stopPrice, array.get(longTakeProfitPrices, longTrailTakeProfitExecutedCount - 2)) if stopLossMoveActMode == MoveActMode.multiTp and longTrailTakeProfitExecutedCount > 1 else math.max(stopPrice, stopPrice + chgLongDistMovePriceCount * longStopLossMoveDistPrice) if stopLossMoveActMode == MoveActMode.multiPrice and chgLongDistMovePriceCount > 0 else stopPrice
        longStopLossPrice = math.max(stopPrice, nz(longStopLossPrice[1], MIN_LIMIT_FLOAT))

    longStopLossDist: float = longEntryPrice - longStopLossPrice
    longStopLossRatio: Series[float] = longStopLossDist / longEntryPrice
    longEntryStopLossRatio: float = ta.valuewhen(enteredLongTrade, longStopLossRatio[1], 0)

    stopLossCustHigherPrice: float = math.round_to_mintick(col.cust_series(shortStopLossDistMul, stopLossCustHigherType, stopLossCustHigherSrc)) if IS_STOP_LOSS_DIST_METHOD_CUST else na

    def getShortStopLossPrice(referencePrice: float):
        __block_result_14__ = na
        if stopLossStepTrailDistEnabled:
            steppedDist = udt_copy(shortStopLossDistSettings)
            steppedDist.distMul = shortStopLossDistSettings.distMul + shortTrailTakeProfitExecutedCount * shortStopLossStepTrailDistMul
            __block_result_14__ = steppedDist
        else:
            __block_result_14__ = shortStopLossDistSettings
        shortStopLossSteppedDist = __block_result_14__
        return method_call('higher_long_biased_price', shortStopLossSteppedDist, referencePrice, longBiasedAuxData, stopLossRestrictSettings, stopLossBiasSettings, stopLossCustHigherPrice)

    def getShortStopLossMoveDistPrice():
        return method_call('price', stopLossMoveDistSettings, shortEntryPrice, longBiasedAuxData)

    shortStopLossMoveDistPrice: float = getShortStopLossMoveDistPrice() if stopLossMoveActMode == MoveActMode.oncePrice or stopLossMoveActMode == MoveActMode.multiPrice else na
    shortDistMovePriceCount: int = math.floor((shortEntryPrice - lowestLowSinceShortEntry) / shortStopLossMoveDistPrice) if stopLossMoveActMode == MoveActMode.multiPrice else na
    chgShortDistMovePriceCount: int = ta.change(shortDistMovePriceCount)

    shortStopLossPrice: PersistentSeries[float] = na(float)
    if shortLimitOrStopEntryIsActive or validOpenShortPosition:
        shortStopLossPrice = getShortStopLossPrice(shortEntryPrice)
    elif enteredShortTrade and STOP_LOSS_ADJUSTMENT_IS_NEEDED:
        shortStopLossPrice = shortStopLossPrice + (shortEntryPrice - nz(shortEntryPrice[1], shortEntryPrice))
    elif isShortPosition:
        shortStopLossTrailEnabled: bool = stopLossTrailActMode == TrailActMode.start or (stopLossTrailActMode == TrailActMode.tp and shortIthTrailTakeProfitExecuted(stopLossTrailTPActNum))
        stopPrice: float = getShortStopLossPrice(getDownwardsMovingBarrierPrice(stopLossTrailBarrier)) if shortStopLossTrailEnabled else shortStopLossPrice[1]
        stopPrice = math.min(stopPrice, shortEntryPrice) if stopLossMoveActMode == MoveActMode.onceTp and shortTrailTakeProfitExecutedCount >= stopLossMoveTPActNum or (stopLossMoveActMode == MoveActMode.oncePrice and shortEntryPrice - lowestLowSinceShortEntry >= shortStopLossMoveDistPrice) or (stopLossMoveActMode == MoveActMode.multiTp and shortTrailTakeProfitExecutedCount == 1) else math.min(stopPrice, array.get(shortTakeProfitPrices, shortTrailTakeProfitExecutedCount - 2)) if stopLossMoveActMode == MoveActMode.multiTp and shortTrailTakeProfitExecutedCount > 1 else math.min(stopPrice, stopPrice - chgShortDistMovePriceCount * shortStopLossMoveDistPrice) if stopLossMoveActMode == MoveActMode.multiPrice and chgShortDistMovePriceCount > 0 else stopPrice
        shortStopLossPrice = math.min(stopPrice, nz(shortStopLossPrice[1], MAX_LIMIT_FLOAT))

    shortStopLossDist: float = shortStopLossPrice - shortEntryPrice
    shortStopLossRatio: Series[float] = shortStopLossDist / shortEntryPrice
    shortEntryStopLossRatio: float = ta.valuewhen(enteredShortTrade, shortStopLossRatio[1], 0)

    modCount += 1

    expectedProfit: float = strategy.openprofit - strategy.position_size * (strategy.position_avg_price + close) * commissionRatio
    closeLongPosition: bool = dealConditions.endLongDeal and (closeOpenProfit == CloseOpenProfit.possitive and expectedProfit > 0 or (closeOpenProfit == CloseOpenProfit.negative and expectedProfit < 0) or closeOpenProfit == CloseOpenProfit.any) or (bar_index - longEntryBarId == closeEarlyBars and (not longIthTrailTakeProfitExecuted(closeEarlyTPActNum)) if closeEarlyEnabled else False)
    closeShortPosition: bool = dealConditions.endShortDeal and (closeOpenProfit == CloseOpenProfit.possitive and expectedProfit > 0 or (closeOpenProfit == CloseOpenProfit.negative and expectedProfit < 0) or closeOpenProfit == CloseOpenProfit.any) or (bar_index - shortEntryBarId == closeEarlyBars and (not shortIthTrailTakeProfitExecuted(closeEarlyTPActNum)) if closeEarlyEnabled else False)
    closeAllPositions: bool = closeAtSessionEnd and (not timeFilterApproval)

    cnlCloseLongPosition: bool = timeFilterApproval and dealConditions.cnlEndLongDeal or (not timeFilterApproval and timeFilterApproval[1])
    cnlCloseShortPosition: bool = timeFilterApproval and dealConditions.cnlEndShortDeal or (not timeFilterApproval and timeFilterApproval[1])

    validCloseLongPosition: bool = (closeLongPosition or validOpenShortPosition) and isLongPosition
    validCloseShortPosition: bool = (closeShortPosition or validOpenLongPosition) and isShortPosition

    if closeLongPosition and (not validCloseLongPosition):
        log.warning(LOG_CLOSE_SIGNAL_WARNING, LONG_ORDER_ID_PREFIX)
    if closeShortPosition and (not validCloseShortPosition):
        log.warning(LOG_CLOSE_SIGNAL_WARNING, SHORT_ORDER_ID_PREFIX)

    modCount += 1

    exitDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=exitDistMethod, distMul=exitDistMul)
    exitBiasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_130__, distMul=__input_131__ if exitBiasEnabled else na)
    exitRestrictSettings: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_134__, minDistMul=__input_135__ if exitMinDistEnabled else na, maxDistMul=__input_136__ if exitMaxDistEnabled else na)

    validCnlCloseLongPosition: Persistent[bool] = False

    barsSinceValidCloseLong: int = nz(ta.barssince(validCloseLongPosition or validOpenShortPosition), MAX_LIMIT_INT)
    barsSinceValidCnlCloseLong: int = nz(ta.barssince(validCnlCloseLongPosition), MAX_LIMIT_INT)

    closeLongIsActive: bool = barsSinceValidCnlCloseLong > barsSinceValidCloseLong
    exitLongIsPending: bool = barsSinceCompletedLong >= barsSinceValidCloseLong

    validCnlCloseLongPosition = (cnlCloseLongPosition or (timeFilterApproval and dealConditions.startLongDeal if treatOpenAsCancel else False)) and isLongPosition and closeLongIsActive and exitLongIsPending and (not validCloseLongPosition) if exitOrderType != OrderType.market else False

    if cnlCloseLongPosition and (not validCnlCloseLongPosition) if exitOrderType != OrderType.market else False:
        log.warning(LOG_CNL_CLOSE_SIGNAL_WARNING, LONG_ORDER_ID_PREFIX)

    IS_EXIT_DIST_METHOD_CUST: bool = exitDistMethod == dr.DistMethod.cust
    exitCustLowerPrice: float = math.round_to_mintick(col.cust_series(exitDistMul, exitCustLowerType, exitCustLowerSrc)) if IS_EXIT_DIST_METHOD_CUST else na

    def getLongExitLowerPrice(referencePrice: float):
        return method_call('lower_short_biased_price', exitDistSettings, referencePrice, shortBiasedAuxData, exitRestrictSettings, exitBiasSettings, exitCustLowerPrice)

    exitCustHigherPrice: float = math.round_to_mintick(col.cust_series(exitDistMul, exitCustHigherType, exitCustHigherSrc)) if IS_EXIT_DIST_METHOD_CUST else na

    def getLongExitHigherPrice(referencePrice: float):
        return method_call('higher_short_biased_price', exitDistSettings, referencePrice, shortBiasedAuxData, exitRestrictSettings, exitBiasSettings, exitCustHigherPrice)

    longLimitOrStopExitPrice: PersistentSeries[float] = na(float)
    isFirstValidCloseLongPosition: bool = validCloseLongPosition and isLongPosition and na(longLimitOrStopExitPrice[1]) and (not (validOpenShortPosition and entryOrderType == OrderType.market)) if exitOrderType != OrderType.market else False
    tryExitLongPosition: bool = isLongPosition and (not na(longLimitOrStopExitPrice[1])) and (not validCnlCloseLongPosition) if exitOrderType != OrderType.market else False
    __block_result_15__ = na
    if isFirstValidCloseLongPosition:
        __block_result_16__ = na
        if exitOrderType == OrderType.limit:
            __block_result_16__ = getLongExitHigherPrice(stClose)
        elif exitOrderType == OrderType.stop:
            __block_result_16__ = getLongExitLowerPrice(stClose)
        __block_result_15__ = __block_result_16__
    elif tryExitLongPosition:
        __block_result_17__ = na
        if exitTrailMode == TrailMode.trail or (exitTrailMode == TrailMode.fixed and validCloseLongPosition):
            __block_result_18__ = na
            if exitOrderType == OrderType.limit:
                __block_result_18__ = math.min(getLongExitHigherPrice(getDownwardsMovingBarrierPrice(exitTrailBarrier)), nz(longLimitOrStopExitPrice[1], MAX_LIMIT_FLOAT))
            elif exitOrderType == OrderType.stop:
                __block_result_18__ = math.max(getLongExitLowerPrice(getUpwardsMovingBarrierPrice(exitTrailBarrier)), nz(longLimitOrStopExitPrice[1], MIN_LIMIT_FLOAT))
            __block_result_17__ = __block_result_18__
        else:
            __block_result_17__ = nz(longLimitOrStopExitPrice[1], MIN_LIMIT_FLOAT)
        __block_result_15__ = __block_result_17__
    longLimitOrStopExitPrice = __block_result_15__

    longLimitExitIsActive: bool = not na(longLimitOrStopExitPrice)

    validCnlCloseShortPosition: Persistent[bool] = False

    barsSinceValidCloseShort: int = nz(ta.barssince(validCloseShortPosition or validOpenLongPosition), MAX_LIMIT_INT)
    barsSinceValidCnlCloseShort: int = nz(ta.barssince(validCnlCloseShortPosition), MAX_LIMIT_INT)

    closeShortIsActive: bool = barsSinceValidCnlCloseShort > barsSinceValidCloseShort
    exitShortIsPending: bool = barsSinceCompletedShort >= barsSinceValidCloseShort

    validCnlCloseShortPosition = (cnlCloseShortPosition or (timeFilterApproval and dealConditions.startShortDeal if treatOpenAsCancel else False)) and isShortPosition and closeShortIsActive and exitShortIsPending and (not validCloseShortPosition) if exitOrderType != OrderType.market else False

    if cnlCloseShortPosition and (not validCnlCloseShortPosition) if exitOrderType != OrderType.market else False:
        log.warning(LOG_CNL_CLOSE_SIGNAL_WARNING, SHORT_ORDER_ID_PREFIX)

    def getShortExitLowerPrice(referencePrice: float):
        return method_call('lower_long_biased_price', exitDistSettings, referencePrice, longBiasedAuxData, exitRestrictSettings, exitBiasSettings, exitCustLowerPrice)

    def getShortExitHigherPrice(referencePrice: float):
        return method_call('higher_long_biased_price', exitDistSettings, referencePrice, longBiasedAuxData, exitRestrictSettings, exitBiasSettings, exitCustHigherPrice)

    shortLimitOrStopExitPrice: PersistentSeries[float] = na(float)
    isFirstValidCloseShortPosition: bool = validCloseShortPosition and isShortPosition and na(shortLimitOrStopExitPrice[1]) and (not (validOpenLongPosition and entryOrderType == OrderType.market)) if exitOrderType != OrderType.market else False
    tryExitShortPosition: bool = isShortPosition and (not na(shortLimitOrStopExitPrice[1])) and (not validCnlCloseShortPosition) if exitOrderType != OrderType.market else False
    __block_result_19__ = na
    if isFirstValidCloseShortPosition:
        __block_result_20__ = na
        if exitOrderType == OrderType.limit:
            __block_result_20__ = getShortExitLowerPrice(stClose)
        elif exitOrderType == OrderType.stop:
            __block_result_20__ = getShortExitHigherPrice(stClose)
        __block_result_19__ = __block_result_20__
    elif tryExitShortPosition:
        __block_result_21__ = na
        if exitTrailMode == TrailMode.trail or (exitTrailMode == TrailMode.fixed and validCloseShortPosition):
            __block_result_22__ = na
            if exitOrderType == OrderType.limit:
                __block_result_22__ = math.max(getShortExitLowerPrice(getUpwardsMovingBarrierPrice(exitTrailBarrier)), nz(shortLimitOrStopExitPrice[1], MIN_LIMIT_FLOAT))
            elif exitOrderType == OrderType.stop:
                __block_result_22__ = math.min(getShortExitHigherPrice(getDownwardsMovingBarrierPrice(exitTrailBarrier)), nz(shortLimitOrStopExitPrice[1], MAX_LIMIT_FLOAT))
            __block_result_21__ = __block_result_22__
        else:
            __block_result_21__ = nz(shortLimitOrStopExitPrice[1], MAX_LIMIT_FLOAT)
        __block_result_19__ = __block_result_21__
    shortLimitOrStopExitPrice = __block_result_19__

    shortLimitExitIsActive: bool = not na(shortLimitOrStopExitPrice)

    longExitPrice: float = stClose if validOpenShortPosition and (isLongPosition or exitOrderType == OrderType.market) or (stopLossWaitCloseConfirm and stClose < longStopLossPrice) else longLimitOrStopExitPrice if longLimitExitIsActive else na

    shortExitPrice: float = stClose if validOpenLongPosition and (isShortPosition or exitOrderType == OrderType.market) or (stopLossWaitCloseConfirm and stClose > shortStopLossPrice) else shortLimitOrStopExitPrice if shortLimitExitIsActive else na

    modCount += 1

    if validCloseLongPosition and showCloseLabels and barstate.isconfirmed:
        label.new(point=chart.point.from_index(bar_index + 1, nz(longLimitOrStopExitPrice, stClose)), text='Close', color=longCloseColor, style=label.style_label_right if exitOrderType != OrderType.market else label.style_label_lower_left, textcolor=FG_COLOR, size=size.small, force_overlay=True)
    if validCloseShortPosition and showCloseLabels and barstate.isconfirmed:
        label.new(point=chart.point.from_index(bar_index + 1, nz(shortLimitOrStopExitPrice, stClose)), text='Close', color=shortCloseColor, style=label.style_label_right if exitOrderType != OrderType.market else label.style_label_upper_left, textcolor=FG_COLOR, size=size.small, force_overlay=True)

    if validCnlCloseLongPosition and showCnlCloseLabels and barstate.isconfirmed:
        label.new(point=chart.point.now(nz(longLimitOrStopExitPrice[1], stClose)), text='Cancel', color=longCnlCloseColor, style=label.style_label_down if exitOrderType == OrderType.limit else label.style_label_up, textcolor=FG_COLOR, size=size.small, force_overlay=True)
    if validCnlCloseShortPosition and showCnlCloseLabels and barstate.isconfirmed:
        label.new(point=chart.point.now(nz(shortLimitOrStopExitPrice[1], stClose)), text='Cancel', color=shortCnlCloseColor, style=label.style_label_up if exitOrderType == OrderType.limit else label.style_label_down, textcolor=FG_COLOR, size=size.small, force_overlay=True)

    plot(series=longLimitOrStopExitPrice, title='Long Limit or Stop Exit', color=longExitColor, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True)
    plot(series=shortLimitOrStopExitPrice, title='Short Limit or Stop Exit', color=shortExitColor, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True)



    capitalRiskRatio = __input_141__ / 100.0

    moonbagQuantityRatio = __input_147__ / 100.0

    initTakeProfitQuantityRatio = __input_149__ / 100.0
    stepTakeProfitQuantityRatio = __input_150__ / 100.0

    TAKE_PROFIT_EQUAL_QUANTITY_RATIO: Persistent[float] = 0.0 if numOfTakeProfitTargets == 0 else method_call('clamp_up', (1.0 - moonbagQuantityRatio) / numOfTakeProfitTargets, 0.0, 1.0, 3)
    QUOTE_QTY_DECIMAL_DIGITS: Persistent[int] = method_call('num_of_decimal_digits', syminfo.mintick * syminfo.pointvalue)

    takeProfitQuantityRatios: Persistent[list[float]] = array.new_float(numOfTakeProfitTargets, TAKE_PROFIT_EQUAL_QUANTITY_RATIO) if takeProfitQuantityMethod == TakeProfitQuantityMethod.equal else array.new_float(numOfTakeProfitTargets, stepTakeProfitQuantityRatio)

    if numOfTakeProfitTargets > 0 and takeProfitQuantityMethod == TakeProfitQuantityMethod.manual and barstate.isfirst:
        if initTakeProfitQuantityRatio + stepTakeProfitQuantityRatio * (numOfTakeProfitTargets - 1) != 1.0:
            runtime.error('"Init TP Qty %" + "Step TP Qty %" x ("Take Profit Targets" - 1) != 100%')
        array.set(takeProfitQuantityRatios, 0, initTakeProfitQuantityRatio)

    def getBaseQtyDecimalDigits(entryPrice):
        __block_result_23__ = na
        __switch__ = baseQuantityPrecision
        if __switch__ == BaseQuantityPrecision.auto:
            __block_result_24__ = na
            __switch_1__ = syminfo.type
            if __switch_1__ == 'crypto':
                __block_result_24__ = method_call('num_of_decimal_digits', minOrderSize / entryPrice)
            elif __switch_1__ == 'index':
                __block_result_24__ = 1
            else:
                __block_result_24__ = 0
            __block_result_23__ = __block_result_24__
        elif __switch__ == BaseQuantityPrecision.manual:
            __block_result_23__ = baseQuantityDecimals
        return __block_result_23__

    MIN_ENTRY_SIZE: float = minOrderSize * math.max(numOfTakeProfitTargets if moonbagQuantityRatio == 0.0 else numOfTakeProfitTargets + 1, 1)

    def getRiskBaseQuantity(stopLossRatio: float, entryPrice: float, leverage: int):
        maxRiskBaseBalance: float = (strategy.initial_capital + strategy.netprofit) / entryPrice
        return method_call('floor', math.min(math.max(maxRiskBaseBalance * capitalRiskRatio / stopLossRatio, MIN_ENTRY_SIZE / entryPrice), maxRiskBaseBalance * leverage), getBaseQtyDecimalDigits(entryPrice)) / syminfo.pointvalue

    def getDefaultBaseQuantity(entryPrice: float, leverage: int):
        return method_call('floor', math.min(math.max(strategy.default_entry_qty(entryPrice) * leverage, MIN_ENTRY_SIZE / entryPrice), (strategy.initial_capital + strategy.netprofit) * leverage / entryPrice), getBaseQtyDecimalDigits(entryPrice))

    def getBaseQuantity(stopLossRatio: float, entryPrice: float, leverage: int):
        __block_result_25__ = na
        __switch__ = entryQuantityMethod
        if __switch__ == EntryQuantityMethod.risk:
            __block_result_25__ = getRiskBaseQuantity(stopLossRatio, entryPrice, leverage)
        elif __switch__ == EntryQuantityMethod.default:
            __block_result_25__ = getDefaultBaseQuantity(entryPrice, leverage)
        return __block_result_25__

    def getQuoteQuantity(baseQuantity: float, entryPrice: float):
        return baseQuantity * entryPrice * syminfo.pointvalue

    def getCapitalRiskRatio(quoteQuantity: float, stopLossRatio: float):
        return quoteQuantity / (strategy.initial_capital + strategy.netprofit) * stopLossRatio

    longRemainingQuantityRatio: float = 1.0
    for i in pine_range(0, longTrailTakeProfitExecutedCount - 1 if longTrailTakeProfitExecutedCount - 1 >= 0 else na):
        longRemainingQuantityRatio -= array.get(takeProfitQuantityRatios, i)
    longRemainingQuantityRatio = math.max(0.0, longRemainingQuantityRatio)

    longEntryQuoteQuantity: Persistent[float] = na(float)
    longEntryQuantityPerc: PersistentSeries[float] = na(float)
    longEntryBaseQuantity: Persistent[float] = na(float)
    longTakeProfitQuantities: Persistent[list[float]] = array.new_float(numOfTakeProfitTargets, na)
    longCapitalRiskPerc: PersistentSeries[float] = na(float)
    if longLimitOrStopEntryIsActive or validOpenLongPosition:
        longEntryBaseQuantity = getBaseQuantity(longStopLossRatio, longEntryPrice, longLeverage)
        longEntryQuoteQuantity = getQuoteQuantity(longEntryBaseQuantity, longEntryPrice)
        longEntryQuantityPerc = 100.0 * longEntryQuoteQuantity / (strategy.initial_capital + strategy.netprofit)
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(longTakeProfitQuantities, i, method_call('ceil', longEntryBaseQuantity * array.get(takeProfitQuantityRatios, i), getBaseQtyDecimalDigits(longEntryPrice)))
        longCapitalRiskPerc = 100.0 * getCapitalRiskRatio(longEntryQuoteQuantity, longStopLossRatio)

    longRemainingBaseQuantity: Persistent[float] = na(float)
    if validOpenLongPosition or enteredLongTrade or isLongPosition or completedLongTrade:
        longRemainingBaseQuantity = method_call('ceil', longEntryBaseQuantity * longRemainingQuantityRatio, getBaseQtyDecimalDigits(longEntryPrice))

    shortRemainingQuantityRatio: float = 1.0
    for i in pine_range(0, shortTrailTakeProfitExecutedCount - 1 if shortTrailTakeProfitExecutedCount - 1 >= 0 else na):
        shortRemainingQuantityRatio -= array.get(takeProfitQuantityRatios, i)
    shortRemainingQuantityRatio = math.max(0.0, shortRemainingQuantityRatio)

    shortEntryQuoteQuantity: Persistent[float] = na(float)
    shortEntryQuantityPerc: PersistentSeries[float] = na(float)
    shortEntryBaseQuantity: Persistent[float] = na(float)
    shortTakeProfitQuantities: Persistent[list[float]] = array.new_float(numOfTakeProfitTargets, na)
    shortCapitalRiskPerc: PersistentSeries[float] = na(float)
    if shortLimitOrStopEntryIsActive or validOpenShortPosition:
        shortEntryBaseQuantity = getBaseQuantity(shortStopLossRatio, shortEntryPrice, shortLeverage)
        shortEntryQuoteQuantity = getQuoteQuantity(shortEntryBaseQuantity, shortEntryPrice)
        balance: float = strategy.initial_capital + strategy.netprofit
        shortEntryQuantityPerc = 100.0 * shortEntryQuoteQuantity / balance
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(shortTakeProfitQuantities, i, method_call('ceil', shortEntryBaseQuantity * array.get(takeProfitQuantityRatios, i), getBaseQtyDecimalDigits(shortEntryPrice)))
        shortCapitalRiskPerc = 100.0 * getCapitalRiskRatio(shortEntryQuoteQuantity, shortStopLossRatio)

    shortRemainingBaseQuantity: Persistent[float] = na(float)
    if validOpenShortPosition or enteredShortTrade or isShortPosition or completedShortTrade:
        shortRemainingBaseQuantity = method_call('ceil', shortEntryBaseQuantity * shortRemainingQuantityRatio, getBaseQtyDecimalDigits(shortEntryPrice))

    modCount += 1
    longTakeProfitInitDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=takeProfitInitDistMethod, distMul=longTakeProfitInitDistMul, commissionRatio=commissionRatio)
    takeProfitInitBiasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_166__, distMul=__input_167__ if takeProfitInitBiasEnabled else na)
    takeProfitInitRestrictSettings: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_170__, minDistMul=__input_171__ if takeProfitInitMinDistEnabled else na, maxDistMul=__input_172__ if takeProfitInitMaxDistEnabled else na, commissionRatio=commissionRatio)
    shortTakeProfitInitDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=longTakeProfitInitDistSettings.distMethod, distMul=shortTakeProfitInitDistMul, commissionRatio=commissionRatio)

    longTakeProfitStepDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_174__, distMul=__input_175__, commissionRatio=commissionRatio)
    takeProfitStepBiasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_177__, distMul=__input_178__ if takeProfitStepBiasEnabled else na)
    takeProfitStepRestrictSettings: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_181__, minDistMul=__input_182__ if takeProfitStepMinDistEnabled else na, maxDistMul=__input_183__ if takeProfitStepMaxDistEnabled else na, commissionRatio=commissionRatio)

    shortTakeProfitStepDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=longTakeProfitStepDistSettings.distMethod, distMul=__input_184__, commissionRatio=commissionRatio)

    takeProfitTrailDistSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_186__, distMul=__input_187__)

    IS_TAKE_PROFIT_DIST_METHOD_CUST: bool = takeProfitInitDistMethod == dr.DistMethod.cust
    takeProfitCustHigherPrice: float = math.round_to_mintick(col.cust_series(longTakeProfitInitDistMul, takeProfitCustHigherType, takeProfitCustHigherSrc)) if IS_TAKE_PROFIT_DIST_METHOD_CUST else na

    def getLongTakeProfitPrice(dist: dr.DistSettings, reference: float, shortBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings = na):
        return method_call('higher_short_biased_price', dist, reference, shortBiasedAuxData, restrict, bias, takeProfitCustHigherPrice)

    def getlongTakeProfitTicks(distSettings: dr.DistSettings, referencePrice: float, shortBiasedAuxData: dr.AuxData):
        return method_call('ticks', distSettings, referencePrice, shortBiasedAuxData)

    TAKE_PROFIT_ADJUSTMENT_IS_NEEDED: bool = not IS_TAKE_PROFIT_DIST_METHOD_CUST if takeProfitAdjustmentEnabled else False

    if longLimitOrStopEntryIsActive or validOpenLongPosition:
        currentLongTakeProfitPrice: float = longEntryPrice
        currentLongTakeProfitShortBiasedAuxData: dr.AuxData = dr.AuxData.new(atr=negAtr, stdev=negStDev, stopLossDist=longStopLossDist)
        currentLongTakeProfitDistSettings: dr.DistSettings = longTakeProfitInitDistSettings
        currentTakeProfitRestrictSettings: dr.RestrictSettings = takeProfitInitRestrictSettings
        currentTakeProfitBiasSettings: dr.DistSettings = takeProfitInitBiasSettings
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            currentLongTakeProfitShortBiasedAuxData.baseQuantity = array.get(longTakeProfitQuantities, i)
            currentLongTakeProfitPrice = getLongTakeProfitPrice(currentLongTakeProfitDistSettings, currentLongTakeProfitPrice, currentLongTakeProfitShortBiasedAuxData, currentTakeProfitRestrictSettings, currentTakeProfitBiasSettings)
            array.set(longTakeProfitPrices, i, currentLongTakeProfitPrice)
            array.set(longTrailTakeProfitOffsetTicks, i, getlongTakeProfitTicks(takeProfitTrailDistSettings, currentLongTakeProfitPrice, currentLongTakeProfitShortBiasedAuxData))
            if i == 0:
                currentLongTakeProfitDistSettings = longTakeProfitStepDistSettings
                currentTakeProfitRestrictSettings = takeProfitStepRestrictSettings
                currentTakeProfitBiasSettings = takeProfitStepBiasSettings
    elif enteredLongTrade and TAKE_PROFIT_ADJUSTMENT_IS_NEEDED:
        longEntryPriceOffset: float = longEntryPrice - nz(longEntryPrice[1], longEntryPrice)
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(longTakeProfitPrices, i, array.get(longTakeProfitPrices, i) + longEntryPriceOffset)
            array.set(longTrailTakeProfitOffsetTicks, i, array.get(longTrailTakeProfitOffsetTicks, i) + math.floor(longEntryPriceOffset / syminfo.mintick))

    takeProfitCustLowerPrice: float = math.round_to_mintick(col.cust_series(shortTakeProfitInitDistMul, takeProfitCustLowerType, takeProfitCustLowerSrc)) if IS_TAKE_PROFIT_DIST_METHOD_CUST else na

    def getShortTakeProfitPrice(dist: dr.DistSettings, reference: float, longBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings = na):
        return method_call('lower_long_biased_price', dist, reference, longBiasedAuxData, restrict, bias, takeProfitCustLowerPrice)

    def getShortTakeProfitTicks(distSettings: dr.DistSettings, referencePrice: float, longBiasedAuxData: dr.AuxData):
        return method_call('ticks', distSettings, referencePrice, longBiasedAuxData)

    if shortLimitOrStopEntryIsActive or validOpenShortPosition:
        currentShortTakeProfitPrice: float = shortEntryPrice
        currentShortTakeProfitLongBiasedAuxData: dr.AuxData = dr.AuxData.new(atr=posAtr, stdev=posStDev, stopLossDist=shortStopLossDist)
        currentShortTakeProfitDistSettings: dr.DistSettings = shortTakeProfitInitDistSettings
        currentTakeProfitRestrictSettings: dr.RestrictSettings = takeProfitInitRestrictSettings
        currentTakeProfitBiasSettings: dr.DistSettings = takeProfitInitBiasSettings
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            currentShortTakeProfitLongBiasedAuxData.baseQuantity = array.get(shortTakeProfitQuantities, i)
            currentShortTakeProfitPrice = getShortTakeProfitPrice(currentShortTakeProfitDistSettings, currentShortTakeProfitPrice, currentShortTakeProfitLongBiasedAuxData, currentTakeProfitRestrictSettings, currentTakeProfitBiasSettings)
            array.set(shortTakeProfitPrices, i, currentShortTakeProfitPrice)
            array.set(shortTrailTakeProfitOffsetTicks, i, getShortTakeProfitTicks(takeProfitTrailDistSettings, currentShortTakeProfitPrice, currentShortTakeProfitLongBiasedAuxData))
            if i == 0:
                currentShortTakeProfitDistSettings = shortTakeProfitStepDistSettings
                currentTakeProfitRestrictSettings = takeProfitStepRestrictSettings
                currentTakeProfitBiasSettings = takeProfitStepBiasSettings
    elif enteredShortTrade and TAKE_PROFIT_ADJUSTMENT_IS_NEEDED:
        shortEntryPriceOffset: float = shortEntryPrice - nz(shortEntryPrice[1], shortEntryPrice)
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(shortTakeProfitPrices, i, array.get(shortTakeProfitPrices, i) + shortEntryPriceOffset)
            array.set(shortTrailTakeProfitOffsetTicks, i, array.get(shortTrailTakeProfitOffsetTicks, i) + math.floor(shortEntryPriceOffset / syminfo.mintick))

    modCount += 1



    SHOW_TABLE: bool = showStatsTable or showMetricsTable
    SHOW_STATS: bool = SHOW_TABLE or showTradeStats

    maxWinningStreak: Persistent[int] = 0
    maxLosingStreak: Persistent[int] = 0
    currentWinningStreak: Persistent[int] = 0
    currentLosingStreak: Persistent[int] = 0
    numOfInconclusiveExits: Persistent[int] = 0

    winTradeFreeProfitsPerc: Persistent[list[float]] = array.new_float()
    lossTradeFreeProfitsPerc: Persistent[list[float]] = array.new_float()

    winTradeProfitsPerc: Persistent[list[float]] = array.new_float()
    lossTradeProfitsPerc: Persistent[list[float]] = array.new_float()

    winTradeGainsPerc: Persistent[list[float]] = array.new_float()
    lossTradeGainsPerc: Persistent[list[float]] = array.new_float()

    winSumTakeProfitExecutedCount: Persistent[float] = 0.0
    lossSumTakeProfitExecutedCount: Persistent[float] = 0.0

    winSumQuantityPerc: Persistent[float] = 0.0
    lossSumQuantityPerc: Persistent[float] = 0.0

    winRisksPerc: Persistent[list[float]] = array.new_float()
    lossRisksPerc: Persistent[list[float]] = array.new_float()

    winRiskRewardRatios: Persistent[list[float]] = array.new_float()
    lossRiskRewardRatios: Persistent[list[float]] = array.new_float()

    def closedTradesEntryBarIndex(n: int):
        return strategy.closedtrades.entry_bar_index(strategy.closedtrades - n)

    def closedTradesEntryPrice(n: int):
        return strategy.closedtrades.entry_price(strategy.closedtrades - n)

    def closedTradeEntryIdStartsWith(prefix: str, n: int = 1):
        return string.startswith(strategy.closedtrades.entry_id(strategy.closedtrades - n), prefix) if strategy.closedtrades >= n else False

    def lastTwoClosedTradesEnteredInTheSameBar():
        return closedTradesEntryBarIndex(2) == closedTradesEntryBarIndex(1) if strategy.closedtrades >= 2 else False

    def getNumOfExits(orderIdClose: str, takeProfitCount: int):
        return takeProfitCount + 1 if strategy.closedtrades.exit_id(strategy.closedtrades - 1) == orderIdClose else numOfTakeProfitTargets if moonbagQuantityRatio == 0.0 and numOfTakeProfitTargets > 0 else numOfTakeProfitTargets + 1

    if completedLongTrade and SHOW_STATS:
        lastLongEntryBarIndex: Persistent[int] = na(int)
        lastLongEntryPrice: Persistent[float] = na(float)
        if closedTradeEntryIdStartsWith(LONG_ORDER_ID_PREFIX) or (closedTradeEntryIdStartsWith(LONG_ORDER_ID_PREFIX, 2) and lastTwoClosedTradesEnteredInTheSameBar()):
            lastLongEntryBarIndex = closedTradesEntryBarIndex(1)
            lastLongEntryPrice = closedTradesEntryPrice(1)
        elif closedTradeEntryIdStartsWith(LONG_ORDER_ID_PREFIX, 2) and lastTwoClosedTradesExitedInTheSameBar() if strategy.closedtrades > 1 else False:
            lastLongEntryBarIndex = closedTradesEntryBarIndex(2)
            lastLongEntryPrice = closedTradesEntryPrice(2)
        exRatio: float = lastLongExitPrice / lastLongEntryPrice
        longFreeProfitRatio: float = exRatio - 1.0 - exRatio * commissionRatio - commissionRatio
        longProfitRatio: float = -commissionRatio
        longInconclusiveExit: bool = False
        histId: int = 1 if longLimitOrStopEntryIsActive or validOpenLongPosition or enteredLongTrade else 0
        numOfExits: int = getNumOfExits(LONG_ORDER_ID_CLOSE, longTrailTakeProfitExecutedCount)
        __loop_1__ = pine_loop(strategy.closedtrades - 1)
        while __loop_1__.step(strategy.closedtrades - numOfExits):
            i = __loop_1__.value
            ithExPrice: float = strategy.closedtrades.exit_price(i) if closedTradeExitIdContains(LONG_ORDER_ID_PREFIX) else strategy.closedtrades.exit_price(i - 1)
            ithExRatio: float = ithExPrice / lastLongEntryPrice
            tpId: int = numOfTakeProfitTargets + i - strategy.closedtrades if moonbagQuantityRatio == 0.0 else numOfTakeProfitTargets + i - strategy.closedtrades + 1

            quantityRatio: float = array.get(takeProfitQuantityRatios, tpId) if string.startswith(strategy.closedtrades.exit_id(i), string.format('{0} Take Profit', LONG_ORDER_ID_PREFIX)) else moonbagQuantityRatio if numOfTakeProfitTargets > 0 else 1.0
            longProfitRatio += (ithExRatio - 1.0 - ithExRatio * commissionRatio) * quantityRatio
            longInconclusiveStopLoss = highestHighSinceLongEntry > method_call('get', longTakeProfitPrices[histId], tpId) and (not array.get(longTrailTakeProfitExecuted, tpId)) if tpId < numOfTakeProfitTargets and tpId >= 0 and (stLow < longStopLossPrice) else False
            longInconclusiveTakeProfit: bool = False
            __loop_2__ = pine_loop(strategy.closedtrades - 1)
            while __loop_2__.step(strategy.closedtrades - numOfExits):
                j = __loop_2__.value
                longInconclusiveTakeProfit = bar_index == strategy.closedtrades.exit_bar_index(i) and bar_index == strategy.closedtrades.exit_bar_index(j) and (strategy.closedtrades.exit_price(i) != strategy.closedtrades.exit_price(j)) and (stLow < longStopLossPrice[histId])
            longInconclusiveExit = longInconclusiveExit or longInconclusiveStopLoss or longInconclusiveTakeProfit
        longGainPerc: float = longProfitRatio * longEntryQuantityPerc[histId]
        __block_result_26__ = na
        __switch_1__ = takeProfitQuantityMethod
        if __switch_1__ == TakeProfitQuantityMethod.equal:
            __block_result_26__ = method_call('avg', longTakeProfitPrices[histId])
        elif __switch_1__ == TakeProfitQuantityMethod.manual:
            avgPrice: float = 0
            for i, longTakeProfitPrice in enumerate(longTakeProfitPrices[histId]):
                if i == 0:
                    avgPrice += initTakeProfitQuantityRatio * longTakeProfitPrice
                else:
                    avgPrice += stepTakeProfitQuantityRatio * longTakeProfitPrice
            __block_result_26__ = avgPrice
        longAvgTakeProfitPrice: float = __block_result_26__
        longAvgTakeProfitRatio: float = nz((longAvgTakeProfitPrice - lastLongEntryPrice) / lastLongEntryPrice)
        longRiskRewardRatio: float = longAvgTakeProfitRatio / longEntryStopLossRatio
        isWin: bool = longProfitRatio >= 0.0

        if SHOW_TABLE:
            if isWin:
                currentWinningStreak = currentWinningStreak + 1
                array.push(winTradeFreeProfitsPerc, 100.0 * longFreeProfitRatio)
                array.push(winTradeProfitsPerc, 100.0 * longProfitRatio)
                array.push(winTradeGainsPerc, longGainPerc)
                winSumTakeProfitExecutedCount = winSumTakeProfitExecutedCount + longTrailTakeProfitExecutedCount
                winSumQuantityPerc = winSumQuantityPerc + longEntryQuantityPerc[histId]
                currentLosingStreak = 0
                array.push(winRisksPerc, longCapitalRiskPerc[histId])
                array.push(winRiskRewardRatios, longRiskRewardRatio)
            else:
                currentLosingStreak = currentLosingStreak + 1
                array.push(lossTradeFreeProfitsPerc, 100.0 * longFreeProfitRatio)
                array.push(lossTradeProfitsPerc, 100.0 * longProfitRatio)
                array.push(lossTradeGainsPerc, longGainPerc)
                lossSumTakeProfitExecutedCount = lossSumTakeProfitExecutedCount + longTrailTakeProfitExecutedCount
                lossSumQuantityPerc = lossSumQuantityPerc + longEntryQuantityPerc[histId]
                currentWinningStreak = 0
                array.push(lossRisksPerc, longCapitalRiskPerc[histId])
                array.push(lossRiskRewardRatios, longRiskRewardRatio)
            maxWinningStreak = math.max(currentWinningStreak, maxWinningStreak)
            maxLosingStreak = math.max(currentLosingStreak, maxLosingStreak)
            if longInconclusiveExit:
                numOfInconclusiveExits = numOfInconclusiveExits + 1

        if showTradeStats:
            longFreeProfitPercStr: str = ('+' if longFreeProfitRatio >= 0.0 else '') + string.tostring(100.0 * longFreeProfitRatio, format.percent)
            longProfitPercStr: str = ('+' if isWin else '') + string.tostring(100.0 * longProfitRatio, format.percent)
            longGainPercStr: str = ('+' if isWin else '') + string.tostring(longGainPerc, format.percent)
            tradePrice: float = math.max(method_call('get', longTakeProfitPrices[histId], longTrailTakeProfitExecutedCount - 1), longStopLossPrice[histId], lastLongExitPrice) if isWin and longTrailTakeProfitExecutedCount > 0 else lastLongExitPrice
            labelBarId: int = math.floor((lastLongEntryBarIndex + lastLongExitBarIndex + 1) / 2)
            midPoint: ChartPoint = chart.point.from_index(labelBarId, tradePrice)
            entryPoint: ChartPoint = chart.point.from_index(lastLongEntryBarIndex, lastLongEntryPrice)
            exitPoint: ChartPoint = chart.point.from_index(lastLongExitBarIndex, lastLongExitPrice)
            line.new(first_point=midPoint, second_point=entryPoint, color=winColor if isWin else lossColor, style=line.style_arrow_right, width=1, force_overlay=True)
            line.new(first_point=midPoint, second_point=exitPoint, color=winColor if isWin else lossColor, style=line.style_arrow_right, width=1, force_overlay=True)
            label.new(point=midPoint, text=('🚨' if longInconclusiveExit else '') + ('Win' if isWin else 'Loss'), color=winColor if isWin else lossColor, style=label.style_text_outline, textcolor=BG_COLOR, tooltip=string.format('Entry Quantity: {0}\nCapital Risk: {1}\nEntry Price: {2,number,currency}\nExit Price: {3,number,currency}\nProfit: {4}\nGain: {5}\nTP Exec #: {6,number,integer}\nRisk Reward: {7,number,#.##}\nInit SL: {8}\nAvg TP: {9}\nFree Profit: {10}', string.tostring(longEntryQuantityPerc[histId], format.percent), string.tostring(longCapitalRiskPerc[histId], format.percent), lastLongEntryPrice, lastLongExitPrice, longProfitPercStr, longGainPercStr, longTrailTakeProfitExecutedCount, longRiskRewardRatio, string.tostring(100.0 * longEntryStopLossRatio, format.percent), string.tostring(100.0 * longAvgTakeProfitRatio, format.percent), longFreeProfitPercStr), force_overlay=True)

    if completedShortTrade and SHOW_STATS:
        lastShortEntryBarIndex: Persistent[int] = na(int)
        lastShortEntryPrice: Persistent[float] = na(float)
        if closedTradeEntryIdStartsWith(SHORT_ORDER_ID_PREFIX) or (closedTradeEntryIdStartsWith(SHORT_ORDER_ID_PREFIX, 2) and lastTwoClosedTradesEnteredInTheSameBar()):
            lastShortEntryBarIndex = closedTradesEntryBarIndex(1)
            lastShortEntryPrice = closedTradesEntryPrice(1)
        elif closedTradeEntryIdStartsWith(SHORT_ORDER_ID_PREFIX, 2) and lastTwoClosedTradesExitedInTheSameBar() if strategy.closedtrades > 1 else False:
            lastShortEntryBarIndex = closedTradesEntryBarIndex(2)
            lastShortEntryPrice = closedTradesEntryPrice(2)
        exRatio: float = lastShortExitPrice / lastShortEntryPrice
        shortFreeProfitRatio: float = 1.0 - exRatio - exRatio * commissionRatio - commissionRatio
        shortProfitRatio: float = -commissionRatio
        shortInconclusiveExit: bool = False
        histId: int = 1 if shortLimitOrStopEntryIsActive or validOpenShortPosition or enteredShortTrade else 0
        numOfExits: int = getNumOfExits(SHORT_ORDER_ID_CLOSE, shortTrailTakeProfitExecutedCount)
        __loop_1__ = pine_loop(strategy.closedtrades - 1)
        while __loop_1__.step(strategy.closedtrades - numOfExits):
            i = __loop_1__.value
            ithExPrice: float = strategy.closedtrades.exit_price(i) if closedTradeExitIdContains(SHORT_ORDER_ID_PREFIX) else strategy.closedtrades.exit_price(i - 1)
            ithExRatio: float = ithExPrice / lastShortEntryPrice
            tpId: int = numOfTakeProfitTargets + i - strategy.closedtrades if moonbagQuantityRatio == 0.0 else numOfTakeProfitTargets + i - strategy.closedtrades + 1

            quanityRatio: float = array.get(takeProfitQuantityRatios, tpId) if string.startswith(strategy.closedtrades.exit_id(i), string.format('{0} Take Profit', SHORT_ORDER_ID_PREFIX)) else moonbagQuantityRatio if numOfTakeProfitTargets > 0 else 1.0
            shortProfitRatio += (1.0 - ithExRatio - ithExRatio * commissionRatio) * quanityRatio
            shortInconclusiveStopLoss = lowestLowSinceShortEntry < method_call('get', shortTakeProfitPrices[histId], tpId) and (not array.get(shortTrailTakeProfitExecuted, tpId)) if tpId < numOfTakeProfitTargets and tpId >= 0 and (stHigh > shortStopLossPrice) else False
            shortInconclusiveTakeProfit: bool = False
            __loop_2__ = pine_loop(strategy.closedtrades - 1)
            while __loop_2__.step(strategy.closedtrades - numOfExits):
                j = __loop_2__.value
                shortInconclusiveTakeProfit = bar_index == strategy.closedtrades.exit_bar_index(i) and bar_index == strategy.closedtrades.exit_bar_index(j) and (strategy.closedtrades.exit_price(i) != strategy.closedtrades.exit_price(j)) and (stHigh > shortStopLossPrice[histId])
            shortInconclusiveExit = shortInconclusiveExit or shortInconclusiveStopLoss or shortInconclusiveTakeProfit
        shortGainPerc: float = shortProfitRatio * shortEntryQuantityPerc[histId]
        __block_result_27__ = na
        __switch_1__ = takeProfitQuantityMethod
        if __switch_1__ == TakeProfitQuantityMethod.equal:
            __block_result_27__ = method_call('avg', shortTakeProfitPrices[histId])
        elif __switch_1__ == TakeProfitQuantityMethod.manual:
            avgPrice: float = 0
            for i, shortTakeProfitPrice in enumerate(shortTakeProfitPrices[histId]):
                if i == 0:
                    avgPrice += initTakeProfitQuantityRatio * shortTakeProfitPrice
                else:
                    avgPrice += stepTakeProfitQuantityRatio * shortTakeProfitPrice
            __block_result_27__ = avgPrice
        shortAvgTakeProfitPrice: float = __block_result_27__
        shortAvgTakeProfitRatio: float = nz((lastShortEntryPrice - shortAvgTakeProfitPrice) / lastShortEntryPrice)
        shortRiskRewardRatio: float = shortAvgTakeProfitRatio / shortEntryStopLossRatio
        isWin: bool = shortProfitRatio >= 0.0

        if SHOW_TABLE:
            if isWin:
                currentWinningStreak = currentWinningStreak + 1
                array.push(winTradeFreeProfitsPerc, 100.0 * shortFreeProfitRatio)
                array.push(winTradeProfitsPerc, 100.0 * shortProfitRatio)
                array.push(winTradeGainsPerc, shortGainPerc)
                winSumTakeProfitExecutedCount = winSumTakeProfitExecutedCount + shortTrailTakeProfitExecutedCount
                winSumQuantityPerc = winSumQuantityPerc + shortEntryQuantityPerc[histId]
                currentLosingStreak = 0
                array.push(winRisksPerc, shortCapitalRiskPerc[histId])
                array.push(winRiskRewardRatios, shortRiskRewardRatio)
            else:
                currentLosingStreak = currentLosingStreak + 1
                array.push(lossTradeFreeProfitsPerc, 100.0 * shortFreeProfitRatio)
                array.push(lossTradeProfitsPerc, 100.0 * shortProfitRatio)
                array.push(lossTradeGainsPerc, shortGainPerc)
                lossSumTakeProfitExecutedCount = lossSumTakeProfitExecutedCount + shortTrailTakeProfitExecutedCount
                lossSumQuantityPerc = lossSumQuantityPerc + shortEntryQuantityPerc[histId]
                currentWinningStreak = 0
                array.push(lossRisksPerc, shortCapitalRiskPerc[histId])
                array.push(lossRiskRewardRatios, shortRiskRewardRatio)
            maxWinningStreak = math.max(currentWinningStreak, maxWinningStreak)
            maxLosingStreak = math.max(currentLosingStreak, maxLosingStreak)
            if shortInconclusiveExit:
                numOfInconclusiveExits = numOfInconclusiveExits + 1

        if showTradeStats:
            shortFreeProfitPercStr: str = ('+' if shortFreeProfitRatio >= 0.0 else '') + string.tostring(100.0 * shortFreeProfitRatio, format.percent)
            shortProfitPercStr: str = ('+' if isWin else '') + string.tostring(100.0 * shortProfitRatio, format.percent)
            shortGainPercStr: str = ('+' if isWin else '') + string.tostring(shortGainPerc, format.percent)
            tradePrice: float = math.min(method_call('get', shortTakeProfitPrices[histId], shortTrailTakeProfitExecutedCount - 1), shortStopLossPrice[histId], lastShortExitPrice) if isWin and shortTrailTakeProfitExecutedCount > 0 else lastShortExitPrice
            labelBarId: int = math.floor((lastShortEntryBarIndex + lastShortExitBarIndex + 1) / 2)
            midPoint: ChartPoint = chart.point.from_index(labelBarId, tradePrice)
            entryPoint: ChartPoint = chart.point.from_index(lastShortEntryBarIndex, lastShortEntryPrice)
            exitPoint: ChartPoint = chart.point.from_index(lastShortExitBarIndex, lastShortExitPrice)
            line.new(first_point=midPoint, second_point=entryPoint, color=winColor if isWin else lossColor, style=line.style_arrow_right, width=1, force_overlay=True)
            line.new(first_point=midPoint, second_point=exitPoint, color=winColor if isWin else lossColor, style=line.style_arrow_right, width=1, force_overlay=True)
            label.new(point=midPoint, text=('🚨' if shortInconclusiveExit else '') + ('Win' if isWin else 'Loss'), color=winColor if isWin else lossColor, style=label.style_text_outline, textcolor=BG_COLOR, tooltip=string.format('Entry Quantity: {0}\nCapital Risk: {1}\nEntry Price: {2,number,currency}\nExit Price: {3,number,currency}\nProfit: {4}\nGain: {5}\nTP Exec #: {6,number,integer}\nRisk Reward: {7,number,#.##}\nInit SL: {8}\nAvg TP: {9}\nFree Profit: {10}', string.tostring(shortEntryQuantityPerc[histId], format.percent), string.tostring(shortCapitalRiskPerc[histId], format.percent), lastShortEntryPrice, lastShortExitPrice, shortProfitPercStr, shortGainPercStr, shortTrailTakeProfitExecutedCount, shortRiskRewardRatio, string.tostring(100.0 * shortEntryStopLossRatio, format.percent), string.tostring(100.0 * shortAvgTakeProfitRatio, format.percent), shortFreeProfitPercStr), force_overlay=True)

    firstEntry: Persistent[float] = 0.0
    firstBuyInit: Persistent[bool] = False
    buyAndHoldPerc: Persistent[float] = 0.0

    if showMetricsTable and (not firstBuyInit) and (enteredLongTrade or enteredShortTrade):
        firstEntry = longEntryPrice if enteredLongTrade else shortEntryPrice
        firstBuyInit = True

    if showMetricsTable and (completedLongTrade or completedShortTrade):
        buyAndHoldPerc = 100.0 * (strategy.closedtrades.exit_price(strategy.closedtrades - 1) - firstEntry) / firstEntry

    seasonalData: Persistent[ant.SeasonalData] = method_call('init', ant.SeasonalData.new(), seasonalTableSeasonality)
    if showSeasonalTable:
        method_call('update', seasonalData)

    modCount += 1

    if (SHOW_TABLE or showSeasonalTable) and (barstate.islastconfirmedhistory or (barstate.isrealtime and barstate.isconfirmed)):
        CELL_BG_COLOR: Color = color.new(BG_COLOR, 95)
        POSITIVE_TXT_COLOR: Color = color.new(winColor, 0)
        NEGATIVE_TXT_COLOR: Color = color.new(lossColor, 0)
        POSITIVE_BG_COLOR: Color = color.new(takeProfitColor, 95)
        NEGATIVE_BG_COLOR: Color = color.new(stopLossColor, 95)

        statsData: Persistent[ant.StatsData] = ant.StatsData.new()
        if SHOW_TABLE:
            numOfWins: int = array.size(winTradeProfitsPerc)
            numOfLosses: int = array.size(lossTradeProfitsPerc)
            method_call('update', statsData, wins=ant.SideStats.new(numOf=array.size(winTradeProfitsPerc), maxStreak=maxWinningStreak, sumProfit=nz(array.sum(winTradeProfitsPerc)), profitStDev=nz(array.stdev(winTradeProfitsPerc)), sumGain=nz(array.sum(winTradeGainsPerc)), gainStDev=nz(array.stdev(winTradeGainsPerc)), avgQuantityPerc=nz(winSumQuantityPerc / numOfWins), avgCapitalRiskPerc=nz(array.avg(winRisksPerc)), avgTPExecutedCount=nz(winSumTakeProfitExecutedCount / numOfWins), avgRiskRewardRatio=nz(array.avg(winRiskRewardRatios)), sumFreeProfit=nz(array.sum(winTradeFreeProfitsPerc)), freeProfitStDev=nz(array.stdev(winTradeFreeProfitsPerc))), losses=ant.SideStats.new(numOf=array.size(lossTradeProfitsPerc), maxStreak=maxLosingStreak, sumProfit=nz(array.sum(lossTradeProfitsPerc)), profitStDev=nz(array.stdev(lossTradeProfitsPerc)), sumGain=nz(array.sum(lossTradeGainsPerc)), gainStDev=nz(array.stdev(lossTradeGainsPerc)), avgQuantityPerc=nz(lossSumQuantityPerc / numOfLosses), avgCapitalRiskPerc=nz(array.avg(lossRisksPerc)), avgTPExecutedCount=nz(lossSumTakeProfitExecutedCount / numOfLosses), avgRiskRewardRatio=nz(array.avg(lossRiskRewardRatios)), sumFreeProfit=nz(array.sum(lossTradeFreeProfitsPerc)), freeProfitStDev=nz(array.stdev(lossTradeFreeProfitsPerc))), numOfInconclusiveExits=numOfInconclusiveExits)

        if showStatsTable:
            statsTable: Persistent[ant.StatsTable] = method_call('init', ant.StatsTable.new(), ant.getTablePos(statsTablePosY, statsTablePosX), 0.0, 0.0, POSITIVE_TXT_COLOR, NEGATIVE_TXT_COLOR, chart.fg_color, POSITIVE_BG_COLOR, NEGATIVE_BG_COLOR, CELL_BG_COLOR)
            method_call('update', statsTable, statsData, POSITIVE_TXT_COLOR, NEGATIVE_TXT_COLOR, NEGATIVE_BG_COLOR, CELL_BG_COLOR)

        if showMetricsTable:
            metricsTable: Persistent[ant.MetricsTable] = method_call('init', ant.MetricsTable.new(), ant.getTablePos(metricsTablePosY, metricsTablePosX))
            method_call('update', metricsTable, statsData, buyAndHoldPerc, POSITIVE_TXT_COLOR, NEGATIVE_TXT_COLOR, POSITIVE_BG_COLOR, NEGATIVE_BG_COLOR)

        if showSeasonalTable:
            seasonalTable: Persistent[ant.SeasonalTable] = method_call('init', ant.SeasonalTable.new(), seasonalData, ant.getTablePos('MIDDLE', 'CENTER'), seasonalTableMaxNumOfYears, 100.0, 100.0, seasonalTableExtend, chart.fg_color, CELL_BG_COLOR)
            method_call('update', seasonalTable, seasonalData, POSITIVE_TXT_COLOR, NEGATIVE_TXT_COLOR, chart.fg_color, POSITIVE_BG_COLOR, NEGATIVE_BG_COLOR, CELL_BG_COLOR)

    doCloseMarketLong: bool = exitOrderType == OrderType.market and validCloseLongPosition or (stopLossWaitCloseConfirm and stClose < longStopLossPrice)
    doCloseMarketShort: bool = exitOrderType == OrderType.market and validCloseShortPosition or (stopLossWaitCloseConfirm and stClose > shortStopLossPrice)
    doEnterMarketLong: bool = validOpenLongPosition if entryOrderType == OrderType.market else longLimitOrStopEntryIsActive
    doCnlLimitEntryLong: bool = longLimitOrStopEntryIsActive[1] and validCnlOpenLongPosition
    doSLorExitLimitLong: bool = longLimitOrStopEntryIsActive or longLimitExitIsActive or longIsActive
    doCnlLimitExitLong: bool = longLimitExitIsActive and validCnlCloseLongPosition
    doEnterMarketShort: bool = validOpenShortPosition if entryOrderType == OrderType.market else shortLimitOrStopEntryIsActive
    doCnlLimitEntryShort: bool = shortLimitOrStopEntryIsActive[1] and validCnlOpenShortPosition
    doSLorExitLimitShort: bool = shortLimitOrStopEntryIsActive or shortLimitExitIsActive or shortIsActive
    doCnlLimitExitShort: bool = shortLimitExitIsActive and validCnlCloseShortPosition

    modCount += 1

    if barstate.islastconfirmedhistory:
        if modCount != NUM_OF_MODS:
            log.warning('Unexpected numb\u200c\u200b\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200cer of modules: {0}', modCount)


    rawMsgEnteredMarketLong = __input_207__ if msgEnteredEnabled else na
    rawMsgEnteredMarketShort = __input_208__ if msgEnteredEnabled else na
    rawMsgEnteredLimitOrStopLong = __input_209__ if msgEnteredEnabled else na
    rawMsgEnteredLimitOrStopShort = __input_210__ if msgEnteredEnabled else na
    rawMsgClosedMarketLong = __input_212__ if msgClosedOrExitedEnabled else na
    rawMsgClosedMarketShort = __input_213__ if msgClosedOrExitedEnabled else na
    rawMsgExitedLimitOrStopLong = __input_214__ if msgClosedOrExitedEnabled else na
    rawMsgExitedLimitOrStopShort = __input_215__ if msgClosedOrExitedEnabled else na
    rawMsgClosedAll = __input_216__ if msgClosedOrExitedEnabled else na
    rawMsgRchTPLong: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
    rawMsgRchTPShort: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
    array.set(rawMsgRchTPLong, 0, __input_218__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPShort, 0, __input_219__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPLong, 1, __input_220__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPShort, 1, __input_221__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPLong, 2, __input_222__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPShort, 2, __input_223__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPLong, 3, __input_224__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPShort, 3, __input_225__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPLong, 4, __input_226__ if msgTakeProfitEnabled else na)
    array.set(rawMsgRchTPShort, 4, __input_227__ if msgTakeProfitEnabled else na)
    rawMsgRchSLLong = __input_229__ if msgStopLossEnabled else na
    rawMsgRchSLShort = __input_230__ if msgStopLossEnabled else na
    rawMsgChgTrEntryLong = __input_232__ if msgChgTrEntryEnabled else na
    rawMsgChgTrEntryShort = __input_233__ if msgChgTrEntryEnabled else na
    rawMsgChgTrExitLong = __input_235__ if msgChgTrExitEnabled else na
    rawMsgChgTrExitShort = __input_236__ if msgChgTrExitEnabled else na
    rawMsgChgSLLong = __input_238__ if msgChgSLEnabled else na
    rawMsgChgSLShort = __input_239__ if msgChgSLEnabled else na
    rawMsgCnlLimitOrStopEntryLong = __input_241__ if msgCnlLimitOrStopEntryEnabled else na
    rawMsgCnlLimitOrStopEntryShort = __input_242__ if msgCnlLimitOrStopEntryEnabled else na
    rawMsgCnlLimitOrStopExitLong = __input_244__ if msgCnlLimitOrStopExitEnabled else na
    rawMsgCnlLimitOrStopExitShort = __input_245__ if msgCnlLimitOrStopExitEnabled else na
    msgRiskManagement = __input_247__ if msgRiskManagementEnabled else na

    msgEnteredMarketLong: Persistent[str] = na(str)
    msgEnteredMarketShort: Persistent[str] = na(str)
    msgEnteredLimitOrStopLong: Persistent[str] = na(str)
    msgEnteredLimitOrStopShort: Persistent[str] = na(str)
    msgClosedMarketLong: Persistent[str] = na(str)
    msgClosedMarketShort: Persistent[str] = na(str)
    msgExitedLimitOrStopLong: Persistent[str] = na(str)
    msgExitedLimitOrStopShort: Persistent[str] = na(str)
    msgRchTPLong: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
    msgRchTPShort: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
    msgRchSLLong: Persistent[str] = na(str)
    msgRchSLShort: Persistent[str] = na(str)
    msgClosedAll: Persistent[str] = na(str)

    stringVarVariablesMap: Persistent[dict[str, str]] = map.new()
    numberVarVariablesMap: Persistent[dict[str, float]] = map.new()
    numberVariablesMapLong: Persistent[dict[str, float]] = map.new()
    numberVariablesMapShort: Persistent[dict[str, float]] = map.new()

    if msgEnteredEnabled or msgClosedOrExitedEnabled or msgTakeProfitEnabled or msgStopLossEnabled or msgChgTrEntryEnabled or msgChgTrExitEnabled or msgChgSLEnabled or msgCnlLimitOrStopEntryEnabled or msgCnlLimitOrStopExitEnabled:
        stringVarVariablesInit: Persistent[bool] = False
        if not stringVarVariablesInit:
            map.put(stringVarVariablesMap, '{{ticker}}', tickerPrefix + syminfo.ticker + tickerPostfix)
            map.put(stringVarVariablesMap, '{{base_currency}}', syminfo.basecurrency)
            map.put(stringVarVariablesMap, '{{quote_currency}}', syminfo.currency)
            stringVarVariablesInit = True
        ratioMul: float = 100.0 if usePercRange100 else 1.0
        percDiv: float = 1.0 if usePercRange100 else 100.0
        numberVarVariablesInit: Persistent[bool] = False
        if not numberVarVariablesInit:
            map.put(numberVarVariablesMap, '{{take_profit_quantity_perc_1}}', array.get(takeProfitQuantityRatios, 0) if numOfTakeProfitTargets > 0 else na * ratioMul)
            map.put(numberVarVariablesMap, '{{take_profit_quantity_perc_2}}', array.get(takeProfitQuantityRatios, 1) if numOfTakeProfitTargets > 1 else na * ratioMul)
            map.put(numberVarVariablesMap, '{{take_profit_quantity_perc_3}}', array.get(takeProfitQuantityRatios, 2) if numOfTakeProfitTargets > 2 else na * ratioMul)
            map.put(numberVarVariablesMap, '{{take_profit_quantity_perc_4}}', array.get(takeProfitQuantityRatios, 3) if numOfTakeProfitTargets > 3 else na * ratioMul)
            map.put(numberVarVariablesMap, '{{take_profit_quantity_perc_5}}', array.get(takeProfitQuantityRatios, 4) if numOfTakeProfitTargets > 4 else na * ratioMul)
            numberVarVariablesInit = True

        if longLimitOrStopEntryIsActive or validOpenLongPosition or enteredLongTrade or isLongPosition or completedLongTrade:
            map.put(numberVariablesMapLong, '{{entry_base_quantity}}', longEntryBaseQuantity)
            map.put(numberVariablesMapLong, '{{entry_quote_quantity}}', longEntryQuoteQuantity)
            map.put(numberVariablesMapLong, '{{entry_quantity_perc}}', longEntryQuantityPerc / percDiv)
            map.put(numberVariablesMapLong, '{{take_profit_base_quantity_1}}', array.get(longTakeProfitQuantities, 0) if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapLong, '{{take_profit_base_quantity_2}}', array.get(longTakeProfitQuantities, 1) if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapLong, '{{take_profit_base_quantity_3}}', array.get(longTakeProfitQuantities, 2) if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapLong, '{{take_profit_base_quantity_4}}', array.get(longTakeProfitQuantities, 3) if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapLong, '{{take_profit_base_quantity_5}}', array.get(longTakeProfitQuantities, 4) if numOfTakeProfitTargets > 4 else na)
            map.put(numberVariablesMapLong, '{{remaining_quantity_perc}}', longRemainingQuantityRatio * ratioMul)
            map.put(numberVariablesMapLong, '{{remaining_base_quantity}}', longRemainingBaseQuantity)
            map.put(numberVariablesMapLong, '{{risk_perc}}', longCapitalRiskPerc / percDiv)
            map.put(numberVariablesMapLong, '{{stop_loss_price}}', longStopLossPrice)
            map.put(numberVariablesMapLong, '{{stop_loss_perc}}', longStopLossRatio * ratioMul)
            map.put(numberVariablesMapLong, '{{entry_price}}', longEntryPrice)
            map.put(numberVariablesMapLong, '{{entry+_price}}', longEntryPrice + offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapLong, '{{entry-_price}}', longEntryPrice - offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapLong, '{{exit_price}}', longExitPrice)
            map.put(numberVariablesMapLong, '{{exit+_price}}', longExitPrice + offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapLong, '{{exit-_price}}', longExitPrice - offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapLong, '{{take_profit_price_1}}', array.get(longTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapLong, '{{take_profit_price_2}}', array.get(longTakeProfitPrices, 1) if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapLong, '{{take_profit_price_3}}', array.get(longTakeProfitPrices, 2) if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapLong, '{{take_profit_price_4}}', array.get(longTakeProfitPrices, 3) if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapLong, '{{take_profit_price_5}}', array.get(longTakeProfitPrices, 4) if numOfTakeProfitTargets > 4 else na)
            map.put(numberVariablesMapLong, '{{take_profit_perc_1}}', (array.get(longTakeProfitPrices, 0) - longEntryPrice) / longEntryPrice * ratioMul if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapLong, '{{take_profit_perc_2}}', (array.get(longTakeProfitPrices, 1) - longEntryPrice) / longEntryPrice * ratioMul if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapLong, '{{take_profit_perc_3}}', (array.get(longTakeProfitPrices, 2) - longEntryPrice) / longEntryPrice * ratioMul if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapLong, '{{take_profit_perc_4}}', (array.get(longTakeProfitPrices, 3) - longEntryPrice) / longEntryPrice * ratioMul if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapLong, '{{take_profit_perc_5}}', (array.get(longTakeProfitPrices, 4) - longEntryPrice) / longEntryPrice * ratioMul if numOfTakeProfitTargets > 4 else na)

        if shortLimitOrStopEntryIsActive or validOpenShortPosition or enteredShortTrade or isShortPosition or completedShortTrade:
            map.put(numberVariablesMapShort, '{{entry_base_quantity}}', shortEntryBaseQuantity)
            map.put(numberVariablesMapShort, '{{entry_quote_quantity}}', shortEntryQuoteQuantity)
            map.put(numberVariablesMapShort, '{{entry_quantity_perc}}', shortEntryQuantityPerc / percDiv)
            map.put(numberVariablesMapShort, '{{take_profit_base_quantity_1}}', array.get(shortTakeProfitQuantities, 0) if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapShort, '{{take_profit_base_quantity_2}}', array.get(shortTakeProfitQuantities, 1) if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapShort, '{{take_profit_base_quantity_3}}', array.get(shortTakeProfitQuantities, 2) if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapShort, '{{take_profit_base_quantity_4}}', array.get(shortTakeProfitQuantities, 3) if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapShort, '{{take_profit_base_quantity_5}}', array.get(shortTakeProfitQuantities, 4) if numOfTakeProfitTargets > 4 else na)
            map.put(numberVariablesMapShort, '{{remaining_quantity_perc}}', shortRemainingQuantityRatio * ratioMul)
            map.put(numberVariablesMapShort, '{{remaining_base_quantity}}', shortRemainingBaseQuantity)
            map.put(numberVariablesMapShort, '{{risk_perc}}', shortCapitalRiskPerc / percDiv)
            map.put(numberVariablesMapShort, '{{stop_loss_price}}', shortStopLossPrice)
            map.put(numberVariablesMapShort, '{{stop_loss_perc}}', shortStopLossRatio * ratioMul)
            map.put(numberVariablesMapShort, '{{entry_price}}', shortEntryPrice)
            map.put(numberVariablesMapShort, '{{entry+_price}}', shortEntryPrice + offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapShort, '{{entry-_price}}', shortEntryPrice - offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapShort, '{{exit_price}}', shortExitPrice)
            map.put(numberVariablesMapShort, '{{exit+_price}}', shortExitPrice + offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapShort, '{{exit-_price}}', shortExitPrice - offsetMsgTicks * syminfo.mintick)
            map.put(numberVariablesMapShort, '{{take_profit_price_1}}', array.get(shortTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapShort, '{{take_profit_price_2}}', array.get(shortTakeProfitPrices, 1) if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapShort, '{{take_profit_price_3}}', array.get(shortTakeProfitPrices, 2) if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapShort, '{{take_profit_price_4}}', array.get(shortTakeProfitPrices, 3) if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapShort, '{{take_profit_price_5}}', array.get(shortTakeProfitPrices, 4) if numOfTakeProfitTargets > 4 else na)
            map.put(numberVariablesMapShort, '{{take_profit_perc_1}}', (shortEntryPrice - array.get(shortTakeProfitPrices, 0)) / shortEntryPrice * ratioMul if numOfTakeProfitTargets > 0 else na)
            map.put(numberVariablesMapShort, '{{take_profit_perc_2}}', (shortEntryPrice - array.get(shortTakeProfitPrices, 1)) / shortEntryPrice * ratioMul if numOfTakeProfitTargets > 1 else na)
            map.put(numberVariablesMapShort, '{{take_profit_perc_3}}', (shortEntryPrice - array.get(shortTakeProfitPrices, 2)) / shortEntryPrice * ratioMul if numOfTakeProfitTargets > 2 else na)
            map.put(numberVariablesMapShort, '{{take_profit_perc_4}}', (shortEntryPrice - array.get(shortTakeProfitPrices, 3)) / shortEntryPrice * ratioMul if numOfTakeProfitTargets > 3 else na)
            map.put(numberVariablesMapShort, '{{take_profit_perc_5}}', (shortEntryPrice - array.get(shortTakeProfitPrices, 4)) / shortEntryPrice * ratioMul if numOfTakeProfitTargets > 4 else na)

        if msgEnteredEnabled:
            varMsgEnteredMarketLong: Persistent[str] = method_call('replace_all', rawMsgEnteredMarketLong, stringVarVariablesMap)
            varMsgEnteredMarketShort: Persistent[str] = method_call('replace_all', rawMsgEnteredMarketShort, stringVarVariablesMap)
            varMsgEnteredLimitOrStopLong: Persistent[str] = method_call('replace_all', rawMsgEnteredLimitOrStopLong, stringVarVariablesMap)
            varMsgEnteredLimitOrStopShort: Persistent[str] = method_call('replace_all', rawMsgEnteredLimitOrStopShort, stringVarVariablesMap)
            msgEnteredMarketLong = method_call('replace', varMsgEnteredMarketLong, numberVariablesMapLong) if doEnterMarketLong else na
            msgEnteredMarketShort = method_call('replace', varMsgEnteredMarketShort, numberVariablesMapShort) if doEnterMarketShort else na
            msgEnteredLimitOrStopLong = method_call('replace', varMsgEnteredLimitOrStopLong, numberVariablesMapLong) if doEnterMarketLong else na
            msgEnteredLimitOrStopShort = method_call('replace', varMsgEnteredLimitOrStopShort, numberVariablesMapShort) if doEnterMarketShort else na

        if msgClosedOrExitedEnabled:
            varMsgClosedMarketLong: Persistent[str] = method_call('replace_all', rawMsgClosedMarketLong, stringVarVariablesMap)
            varMsgClosedMarketShort: Persistent[str] = method_call('replace_all', rawMsgClosedMarketShort, stringVarVariablesMap)
            varMsgExitedLimitOrStopLong: Persistent[str] = method_call('replace_all', rawMsgExitedLimitOrStopLong, stringVarVariablesMap)
            varMsgExitedLimitOrStopShort: Persistent[str] = method_call('replace_all', rawMsgExitedLimitOrStopShort, stringVarVariablesMap)
            varMsgClosedAll: Persistent[str] = method_call('replace_all', rawMsgClosedAll, stringVarVariablesMap)
            msgClosedMarketLong = method_call('replace', varMsgClosedMarketLong, numberVariablesMapLong) if doCloseMarketLong else na
            msgClosedMarketShort = method_call('replace', varMsgClosedMarketShort, numberVariablesMapShort) if doCloseMarketShort else na
            msgExitedLimitOrStopLong = method_call('replace', varMsgExitedLimitOrStopLong, numberVariablesMapLong) if doSLorExitLimitLong else na
            msgExitedLimitOrStopShort = method_call('replace', varMsgExitedLimitOrStopShort, numberVariablesMapShort) if doSLorExitLimitShort else na
            msgClosedAll = method_call('replace', method_call('replace', varMsgClosedAll, numberVariablesMapLong), numberVariablesMapShort) if closeAllPositions else na

        if msgTakeProfitEnabled:
            varMsgRchTPLong: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
            varMsgRchTPShort: Persistent[list[str]] = array.new_string(NUM_OF_MAX_TP_ALERTS, na)
            msgRchTPInit: Persistent[bool] = False
            if not msgRchTPInit:
                for i, rawMsg in enumerate(rawMsgRchTPLong):
                    array.set(varMsgRchTPLong, i, method_call('replace', method_call('replace_all', rawMsg, stringVarVariablesMap), numberVarVariablesMap) if numOfTakeProfitTargets > i else na)
                for i, rawMsg in enumerate(rawMsgRchTPShort):
                    array.set(varMsgRchTPShort, i, method_call('replace', method_call('replace_all', rawMsg, stringVarVariablesMap), numberVarVariablesMap) if numOfTakeProfitTargets > i else na)
                msgRchTPInit = True
            if doSLorExitLimitLong:
                for i, varMsg in enumerate(varMsgRchTPLong):
                    array.set(msgRchTPLong, i, method_call('replace', varMsg, numberVariablesMapLong) if numOfTakeProfitTargets > i else na)
            if doSLorExitLimitShort:
                for i, varMsg in enumerate(varMsgRchTPShort):
                    array.set(msgRchTPShort, i, method_call('replace', varMsg, numberVariablesMapShort) if numOfTakeProfitTargets > i else na)

        if msgStopLossEnabled:
            varMsgRchSLLong: Persistent[str] = method_call('replace_all', rawMsgRchSLLong, stringVarVariablesMap)
            varMsgRchSLShort: Persistent[str] = method_call('replace_all', rawMsgRchSLShort, stringVarVariablesMap)
            msgRchSLLong = method_call('replace', varMsgRchSLLong, numberVariablesMapLong) if doSLorExitLimitLong else na
            msgRchSLShort = method_call('replace', varMsgRchSLShort, numberVariablesMapShort) if doSLorExitLimitShort else na

    if msgChgTrEntryEnabled:
        varMsgChgTrEntryLong: Persistent[str] = method_call('replace_all', rawMsgChgTrEntryLong, stringVarVariablesMap)
        if ta.change(longEntryPrice) != 0.0:
            alert(message=method_call('replace', varMsgChgTrEntryLong, numberVariablesMapLong), freq=alert.freq_once_per_bar_close)
        varMsgChgTrEntryShort: Persistent[str] = method_call('replace_all', rawMsgChgTrEntryShort, stringVarVariablesMap)
        if ta.change(shortEntryPrice) != 0.0:
            alert(message=method_call('replace', varMsgChgTrEntryShort, numberVariablesMapShort), freq=alert.freq_once_per_bar_close)

    if msgChgTrExitEnabled:
        varMsgChgTrExitLong: Persistent[str] = method_call('replace_all', rawMsgChgTrExitLong, stringVarVariablesMap)
        if ta.change(longExitPrice) != 0.0:
            alert(message=method_call('replace', varMsgChgTrExitLong, numberVariablesMapLong), freq=alert.freq_once_per_bar_close)
        varMsgChgTrExitShort: Persistent[str] = method_call('replace_all', rawMsgChgTrExitShort, stringVarVariablesMap)
        if ta.change(shortExitPrice) != 0.0:
            alert(message=method_call('replace', varMsgChgTrExitShort, numberVariablesMapShort), freq=alert.freq_once_per_bar_close)

    if msgChgSLEnabled:
        varMsgChgSLLong: Persistent[str] = method_call('replace_all', rawMsgChgSLLong, stringVarVariablesMap)
        if ta.change(longStopLossPrice) != 0.0 and na(longLimitOrStopEntryPrice):
            alert(message=method_call('replace', varMsgChgSLLong, numberVariablesMapLong), freq=alert.freq_once_per_bar_close)
        varMsgChgSLShort: Persistent[str] = method_call('replace_all', rawMsgChgSLShort, stringVarVariablesMap)
        if ta.change(shortStopLossPrice) != 0.0 and na(shortLimitOrStopEntryPrice):
            alert(message=method_call('replace', varMsgChgSLShort, numberVariablesMapShort), freq=alert.freq_once_per_bar_close)

    if msgCnlLimitOrStopExitEnabled:
        varMsgCnlLimitOrStopExitLong: Persistent[str] = method_call('replace_all', rawMsgCnlLimitOrStopExitLong, stringVarVariablesMap)
        if doCnlLimitExitLong:
            alert(message=method_call('replace', varMsgCnlLimitOrStopExitLong, numberVariablesMapLong), freq=alert.freq_once_per_bar_close)
        varMsgCnlLimitOrStopExitShort: Persistent[str] = method_call('replace_all', rawMsgCnlLimitOrStopExitShort, stringVarVariablesMap)
        if doCnlLimitExitShort:
            alert(message=method_call('replace', varMsgCnlLimitOrStopExitShort, numberVariablesMapShort), freq=alert.freq_once_per_bar_close)

    if completedLongTrade:
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(longTrailTakeProfitExecuted, i, False)

    if completedShortTrade:
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(shortTrailTakeProfitExecuted, i, False)

    author: Persistent[Table] = method_call('announce', method_call('desteganographize', 'Aut\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200bhor'), textColor=color.new(FG_COLOR, 90), textSize=size.huge)

    if completedLongTrade and (not (longLimitOrStopEntryIsActive or validOpenLongPosition or enteredLongTrade)) or validCnlOpenLongPosition or closeAllPositions:
        longEntryPrice = na
        highestHighSinceLongEntry = na
        longStopLossPrice = na
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(longTakeProfitPrices, i, na)
            array.set(longTrailTakeProfitOffsetTicks, i, na)
        longEntryQuoteQuantity = na
        longEntryQuantityPerc = na
        longEntryBaseQuantity = na
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(longTakeProfitQuantities, i, na)
        longRemainingBaseQuantity = na
        longCapitalRiskPerc = na

    if completedShortTrade and (not (shortLimitOrStopEntryIsActive or validOpenShortPosition or enteredShortTrade)) or validCnlOpenShortPosition or closeAllPositions:
        shortEntryPrice = na
        lowestLowSinceShortEntry = na
        shortStopLossPrice = na
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(shortTakeProfitPrices, i, na)
            array.set(shortTrailTakeProfitOffsetTicks, i, na)
        shortEntryQuoteQuantity = na
        shortEntryQuantityPerc = na
        shortEntryBaseQuantity = na
        for i in pine_range(0, TAKE_PROFIT_TARGETS_SIZE):
            array.set(shortTakeProfitQuantities, i, na)
        shortRemainingBaseQuantity = na
        shortCapitalRiskPerc = na

    def getNumToEmojiMap():
        numToEmoji: dict[int, str] = map.new()
        map.put(numToEmoji, 0, '0️⃣')
        map.put(numToEmoji, 1, '1️⃣')
        map.put(numToEmoji, 2, '2️⃣')
        map.put(numToEmoji, 3, '3️⃣')
        map.put(numToEmoji, 4, '4️⃣')
        map.put(numToEmoji, 5, '5️⃣')
        map.put(numToEmoji, 6, '6️⃣')
        map.put(numToEmoji, 7, '7️⃣')
        map.put(numToEmoji, 8, '8️⃣')
        map.put(numToEmoji, 9, '9️⃣')
        return numToEmoji

    numToEmoji: Persistent[dict[int, str]] = getNumToEmojiMap()

    if closeAllPositions:
        strategy.close_all(comment=msgClosedAll if showAlertsEnabled else '🟪📈📉', alert_message=msgClosedAll)

    if doCloseMarketLong:
        strategy.close(id=LONG_ORDER_ID_ENTRY, comment=msgClosedMarketLong if showAlertsEnabled else ('🟩📈' if expectedProfit > 0 else '🟥📈') if dealConditions.endLongDeal or dealConditions.startShortDeal else '🟪📈', alert_message=msgClosedMarketLong)

    if doCloseMarketShort:
        strategy.close(id=SHORT_ORDER_ID_ENTRY, comment=msgClosedMarketShort if showAlertsEnabled else ('🟩📉' if expectedProfit > 0 else '🟥📉') if dealConditions.endShortDeal or dealConditions.startLongDeal else '🟪📉', alert_message=msgClosedMarketShort)

    if doCnlLimitEntryLong:
        strategy.cancel(id=LONG_ORDER_ID_ENTRY)
        for i in pine_range(1, numOfTakeProfitTargets):
            strategy.cancel(id=string.format(EXIT_ORDER_ID_PATTERN_1, LONG_ORDER_ID_PREFIX, i))
        strategy.cancel(id=string.format(EXIT_ORDER_ID_PATTERN_2, LONG_ORDER_ID_PREFIX))
        if msgCnlLimitOrStopEntryEnabled:
            varMsgCnlLimitOrStopEntryLong: Persistent[str] = method_call('replace_all', rawMsgCnlLimitOrStopEntryLong, stringVarVariablesMap)
            alert(message=method_call('replace', varMsgCnlLimitOrStopEntryLong, numberVariablesMapLong), freq=alert.freq_once_per_bar_close)

    longEffectiveStopLossPrice: float = na if stopLossWaitCloseConfirm else longStopLossPrice
    longTightestStop: float = math.max(nz(longLimitOrStopExitPrice, MIN_LIMIT_FLOAT), nz(longEffectiveStopLossPrice, MIN_LIMIT_FLOAT)) if exitOrderType == OrderType.stop and longLimitExitIsActive else longEffectiveStopLossPrice
    isLongLimitExitTighterThanStopLoss: bool = True if stopLossWaitCloseConfirm else longLimitExitIsActive and exitOrderType == OrderType.stop and (longLimitOrStopExitPrice > longStopLossPrice)

    if doCnlLimitEntryShort:
        strategy.cancel(id=SHORT_ORDER_ID_ENTRY)
        for i in pine_range(1, numOfTakeProfitTargets):
            strategy.cancel(id=string.format(EXIT_ORDER_ID_PATTERN_1, SHORT_ORDER_ID_PREFIX, i))
        strategy.cancel(id=string.format(EXIT_ORDER_ID_PATTERN_2, SHORT_ORDER_ID_PREFIX))
        if msgCnlLimitOrStopEntryEnabled:
            varMsgCnlLimitOrStopEntryShort: Persistent[str] = method_call('replace_all', rawMsgCnlLimitOrStopEntryShort, stringVarVariablesMap)
            alert(message=method_call('replace', varMsgCnlLimitOrStopEntryShort, numberVariablesMapShort), freq=alert.freq_once_per_bar_close)

    shortEffectiveStopLossPrice: float = na if stopLossWaitCloseConfirm else shortStopLossPrice
    shortTightestStop: float = math.min(nz(shortLimitOrStopExitPrice, MAX_LIMIT_FLOAT), nz(shortEffectiveStopLossPrice, MAX_LIMIT_FLOAT)) if exitOrderType == OrderType.stop and shortLimitExitIsActive else shortEffectiveStopLossPrice
    isShortLimitExitTighterThanStopLoss: bool = True if stopLossWaitCloseConfirm else shortLimitExitIsActive and exitOrderType == OrderType.stop and (shortLimitOrStopExitPrice < shortStopLossPrice)

    if doEnterMarketLong:
        perm: bool = modCount == NUM_OF_MODS or math.random() < 0.99
        msgAlert: str = (msgEnteredMarketLong if entryOrderType == OrderType.market else msgEnteredLimitOrStopLong) if perm else method_call('desteganographize', 'Mess\u200c\u200b\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200bage')
        if not na(shortStopLossPrice) and (not na(longLimitOrStopEntryPrice)) and (shortTightestStop <= longLimitOrStopEntryPrice):
            strategy.order(id=LONG_ORDER_ID_ENTRY, direction=strategy.long, limit=longLimitOrStopEntryPrice if entryOrderType == OrderType.limit else longStopLimitEntryPrice if entryOrderType == OrderType.stopLimit else na, stop=longLimitOrStopEntryPrice if entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit else na, qty=longEntryBaseQuantity, comment=msgAlert if showAlertsEnabled else '🔷📈' if entryOrderType == OrderType.market else '🔷📈📍', alert_message=msgAlert)
        else:
            strategy.entry(id=LONG_ORDER_ID_ENTRY, direction=strategy.long, limit=longLimitOrStopEntryPrice if entryOrderType == OrderType.limit else longStopLimitEntryPrice if entryOrderType == OrderType.stopLimit else na, stop=longLimitOrStopEntryPrice if entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit else na, qty=longEntryBaseQuantity, comment=msgAlert if showAlertsEnabled else '🔷📈' if entryOrderType == OrderType.market else '🔷📈📍', alert_message=msgAlert)

    if doEnterMarketShort:
        perm: bool = modCount == NUM_OF_MODS or math.random() < 0.99
        msgAlert: str = (msgEnteredMarketShort if entryOrderType == OrderType.market else msgEnteredLimitOrStopShort) if perm else method_call('desteganographize', 'Mess\u200c\u200b\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200c\u200b\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200c\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200b\u200c\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200c\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200b\u200c\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200b\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200b\u200c\u200c\u2060\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u2060\u200c\u200b\u200b\u200b\u200b\u200b\u2060\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u2060\u200c\u200c\u200c\u200b\u200c\u200b\u200b\u2060\u200c\u200c\u200b\u200c\u200b\u200b\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200c\u2060\u200c\u200c\u200b\u200c\u200c\u200c\u200b\u2060\u200c\u200b\u200c\u200c\u200c\u200bage')
        if not na(longStopLossPrice) and (not na(shortLimitOrStopEntryPrice)) and (longTightestStop >= shortLimitOrStopEntryPrice):
            strategy.order(id=SHORT_ORDER_ID_ENTRY, direction=strategy.short, limit=shortLimitOrStopEntryPrice if entryOrderType == OrderType.limit else shortStopLimitEntryPrice if entryOrderType == OrderType.stopLimit else na, stop=shortLimitOrStopEntryPrice if entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit else na, qty=shortEntryBaseQuantity, comment=msgAlert if showAlertsEnabled else '🔶📉' if entryOrderType == OrderType.market else '🔶📉📍', alert_message=msgAlert)
        else:
            strategy.entry(id=SHORT_ORDER_ID_ENTRY, direction=strategy.short, limit=shortLimitOrStopEntryPrice if entryOrderType == OrderType.limit else shortStopLimitEntryPrice if entryOrderType == OrderType.stopLimit else na, stop=shortLimitOrStopEntryPrice if entryOrderType == OrderType.stop or entryOrderType == OrderType.stopLimit else na, qty=shortEntryBaseQuantity, comment=msgAlert if showAlertsEnabled else '🔶📉' if entryOrderType == OrderType.market else '🔶📉📍', alert_message=msgAlert)

    for i, longTakeProfitPrice in enumerate(longTakeProfitPrices):
        if longLimitOrStopEntryIsActive or longLimitExitIsActive or (longIsActive and (not array.get(longTrailTakeProfitExecuted, i))):
            longTightestLimit: float = math.min(nz(longLimitOrStopExitPrice, MAX_LIMIT_FLOAT), nz(longTakeProfitPrice, MAX_LIMIT_FLOAT)) if exitOrderType == OrderType.limit and longLimitExitIsActive else na if takeProfitTrailEnabled else longTakeProfitPrice
            isLongLimitExitTighterThanTakeProfit: bool = longLimitExitIsActive and longLimitOrStopExitPrice < longTakeProfitPrice
            msgAlertProfit: str = msgExitedLimitOrStopLong if isLongLimitExitTighterThanTakeProfit else array.get(msgRchTPLong, i % NUM_OF_MAX_TP_ALERTS)
            msgAlertLoss: str = (msgExitedLimitOrStopLong if isLongLimitExitTighterThanStopLoss else msgRchSLLong) if i == TAKE_PROFIT_TARGETS_SIZE and moonbagQuantityRatio == 0.0 else na
            msgCommentProfit: str = '🟪📈📍' if exitOrderType == OrderType.limit and longLimitExitIsActive else '🎯📈' + (map.get(numToEmoji, i + 1) if numOfTakeProfitTargets > 1 else '')
            msgCommentLoss: str = '🟪📈📍' if isLongLimitExitTighterThanStopLoss else '🛑📈' + (map.get(numToEmoji, i + 1) if numOfTakeProfitTargets > 1 else '')
            strategy.exit(id=string.format(EXIT_ORDER_ID_PATTERN_1, LONG_ORDER_ID_PREFIX, i + 1), from_entry=LONG_ORDER_ID_ENTRY, qty=array.get(longTakeProfitQuantities, i), limit=longTightestLimit, stop=longTightestStop, trail_price=longTakeProfitPrice if takeProfitTrailEnabled else na, trail_offset=array.get(longTrailTakeProfitOffsetTicks, i) if takeProfitTrailEnabled else na, comment_profit=msgAlertProfit if showAlertsEnabled else msgCommentProfit, comment_loss=msgAlertLoss if showAlertsEnabled else msgCommentLoss, comment_trailing=msgAlertProfit if showAlertsEnabled else msgCommentProfit, alert_profit=msgAlertProfit, alert_loss=msgAlertLoss, alert_trailing=msgAlertProfit)

    for i, shortTakeProfitPrice in enumerate(shortTakeProfitPrices):
        if shortLimitOrStopEntryIsActive or shortLimitExitIsActive or (shortIsActive and (not array.get(shortTrailTakeProfitExecuted, i))):
            shortightestLimit: float = math.max(nz(shortLimitOrStopExitPrice, MIN_LIMIT_FLOAT), nz(shortTakeProfitPrice, MIN_LIMIT_FLOAT)) if exitOrderType == OrderType.limit and shortLimitExitIsActive else na if takeProfitTrailEnabled else shortTakeProfitPrice
            isShortLimitExitTighterThanTakeProfit: bool = shortLimitExitIsActive and shortLimitOrStopExitPrice > shortTakeProfitPrice
            msgAlertProfit: str = msgExitedLimitOrStopShort if isShortLimitExitTighterThanTakeProfit else array.get(msgRchTPShort, i % NUM_OF_MAX_TP_ALERTS)
            msgAlertLoss: str = (msgExitedLimitOrStopShort if isShortLimitExitTighterThanStopLoss else msgRchSLShort) if i == TAKE_PROFIT_TARGETS_SIZE and moonbagQuantityRatio == 0.0 else na
            msgCommentProfit: str = '🟪📉📍' if exitOrderType == OrderType.limit and shortLimitExitIsActive else '🎯📉' + (map.get(numToEmoji, i + 1) if numOfTakeProfitTargets > 1 else '')
            msgCommentLoss: str = '🟪📉📍' if isShortLimitExitTighterThanStopLoss else '🛑📉' + (map.get(numToEmoji, i + 1) if numOfTakeProfitTargets > 1 else '')
            strategy.exit(id=string.format(EXIT_ORDER_ID_PATTERN_1, SHORT_ORDER_ID_PREFIX, i + 1), from_entry=SHORT_ORDER_ID_ENTRY, qty=array.get(shortTakeProfitQuantities, i), limit=shortightestLimit, stop=shortTightestStop, trail_price=shortTakeProfitPrice if takeProfitTrailEnabled else na, trail_offset=array.get(shortTrailTakeProfitOffsetTicks, i) if takeProfitTrailEnabled else na, comment_profit=msgAlertProfit if showAlertsEnabled else msgCommentProfit, comment_loss=msgAlertLoss if showAlertsEnabled else msgCommentLoss, comment_trailing=msgAlertProfit if showAlertsEnabled else msgCommentProfit, alert_profit=msgAlertProfit, alert_loss=msgAlertLoss, alert_trailing=msgAlertProfit)

    if doSLorExitLimitLong:
        msgAlertProfit: str = msgExitedLimitOrStopLong if isLongLimitExitTighterThanStopLoss or exitOrderType == OrderType.limit else na
        msgAlertLoss: str = msgExitedLimitOrStopLong if isLongLimitExitTighterThanStopLoss else msgRchSLLong
        msgCommentProfit: str = '🟪📈📍' if isLongLimitExitTighterThanStopLoss or exitOrderType == OrderType.limit else na
        msgCommentLoss: str = '🟪📈📍' if isLongLimitExitTighterThanStopLoss else '🛑📈'
        strategy.exit(id=string.format(EXIT_ORDER_ID_PATTERN_2, LONG_ORDER_ID_PREFIX), from_entry=LONG_ORDER_ID_ENTRY, limit=longLimitOrStopExitPrice if exitOrderType == OrderType.limit else na, stop=longTightestStop, comment_profit=msgAlertProfit if showAlertsEnabled else msgCommentProfit, comment_loss=msgAlertLoss if showAlertsEnabled else msgCommentLoss, alert_profit=msgAlertProfit, alert_loss=msgAlertLoss)

    if doSLorExitLimitShort:
        msgAlertProfit: str = msgExitedLimitOrStopShort if isShortLimitExitTighterThanStopLoss or exitOrderType == OrderType.limit else na
        msgAlertLoss: str = msgExitedLimitOrStopShort if isShortLimitExitTighterThanStopLoss else msgRchSLShort
        msgCommentProfit: str = '🟪📉📍' if isShortLimitExitTighterThanStopLoss or exitOrderType == OrderType.limit else na
        msgCommentLoss: str = '🟪📉📍' if isShortLimitExitTighterThanStopLoss else '🛑📉'
        strategy.exit(id=string.format(EXIT_ORDER_ID_PATTERN_2, SHORT_ORDER_ID_PREFIX), from_entry=SHORT_ORDER_ID_ENTRY, limit=shortLimitOrStopExitPrice if exitOrderType == OrderType.limit else na, stop=shortTightestStop, comment_profit=msgAlertProfit if showAlertsEnabled else msgCommentProfit, comment_loss=msgAlertLoss if showAlertsEnabled else msgCommentLoss, alert_profit=msgAlertProfit, alert_loss=msgAlertLoss)

    strategy.risk.max_drawdown(value=maxDrawdownPerc if maxDrawdownEnabled else 100.0, type=strategy.percent_of_equity, alert_message=msgRiskManagement)

    strategy.risk.max_intraday_loss(value=maxIntradayLossPerc if maxIntradayLossEnabled else 100.0, type=strategy.percent_of_equity, alert_message=msgRiskManagement)

    strategy.risk.max_intraday_filled_orders(count=maxDailyTrades if maxDailyTradesEnabled else MAX_LIMIT_INT, alert_message=msgRiskManagement)

    strategy.risk.max_cons_loss_days(count=maxLosingDays if maxLosingDaysEnabled else MAX_LIMIT_INT, alert_message=msgRiskManagement)

    if validOpenLongPosition and showOpenLabels and barstate.isconfirmed:
        longOpenTooltip: str = string.format('Entry Quantity: {0}\nCapital Risk: {1}', string.tostring(longEntryQuantityPerc, format.percent), string.tostring(longCapitalRiskPerc, format.percent))
        label.new(point=chart.point.from_index(bar_index + 1, nz(longLimitOrStopEntryPrice, stClose)), text='Open', color=longOpenColor, style=label.style_label_right if entryOrderType != OrderType.market else label.style_label_upper_right, textcolor=FG_COLOR, size=size.small, tooltip=longOpenTooltip, force_overlay=True)

    if validOpenShortPosition and showOpenLabels and barstate.isconfirmed:
        shortOpenTooltip: str = string.format('Entry Quantity: {0}\nCapital Risk: {1}', string.tostring(shortEntryQuantityPerc, format.percent), string.tostring(shortCapitalRiskPerc, format.percent))
        label.new(point=chart.point.from_index(bar_index + 1, nz(shortLimitOrStopEntryPrice, stClose)), text='Open', color=shortOpenColor, style=label.style_label_right if entryOrderType != OrderType.market else label.style_label_lower_right, textcolor=FG_COLOR, size=size.small, tooltip=shortOpenTooltip, force_overlay=True)

    showLongPlots: bool = not longLimitOrStopEntryIsActive or debugModeEnabled
    showShortPlots: bool = not shortLimitOrStopEntryIsActive or debugModeEnabled

    DBG_POS_COLOR: Color = color.new(FG_COLOR, 50)
    plot(series=longEntryPrice if showLongPlots else na, title='Long Entry', color=(DBG_POS_COLOR if debugModeEnabled else na) if longLimitOrStopEntryIsActive else FG_COLOR, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True, linestyle=plot.linestyle_dashed)
    plot(series=shortEntryPrice if showShortPlots else na, title='Short Entry', color=(DBG_POS_COLOR if debugModeEnabled else na) if shortLimitOrStopEntryIsActive else FG_COLOR, linewidth=1, style=plot.style_linebr, offset=1, force_overlay=True, linestyle=plot.linestyle_dashed)

    plotchar(series=longStopLossPrice if enteredLongTrade else na, title='Long Stop Loss Mark', char='⬣', location=location.absolute, color=stopLossColor, offset=1 if entryOrderType != OrderType.market else 0, size=size.tiny, display=display.pane, force_overlay=True)
    plotchar(series=shortStopLossPrice if enteredShortTrade else na, title='Short Stop Loss Mark', char='⬣', location=location.absolute, color=stopLossColor, offset=1 if entryOrderType != OrderType.market else 0, size=size.tiny, display=display.pane, force_overlay=True)

    DBG_STOP_LOSS_COLOR: Color = color.new(stopLossColor, 50)
    plot(series=longStopLossPrice if showLongPlots else na, title='Long Stop Loss', color=(DBG_STOP_LOSS_COLOR if debugModeEnabled else na) if longLimitOrStopEntryIsActive else stopLossColor, linewidth=2, style=plot.style_linebr, offset=1, force_overlay=True)
    plot(series=shortStopLossPrice if showShortPlots else na, title='Short Stop Loss', color=(DBG_STOP_LOSS_COLOR if debugModeEnabled else na) if shortLimitOrStopEntryIsActive else stopLossColor, linewidth=2, style=plot.style_linebr, offset=1, force_overlay=True)

    plotchar(series=array.get(longTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 and enteredLongTrade else na, title='Long Take Profit 1 Mark', char='⦿', location=location.absolute, color=takeProfitColor, offset=1 if entryOrderType != OrderType.market else 0, size=size.tiny, display=display.pane, force_overlay=True)
    plotchar(series=array.get(shortTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 and enteredShortTrade else na, title='Short Take Profit 1 Mark', char='⦿', location=location.absolute, color=takeProfitColor, offset=1 if entryOrderType != OrderType.market else 0, size=size.tiny, display=display.pane, force_overlay=True)

    DBG_TAKE_PROFIT_COLOR: Color = color.new(takeProfitColor, 50)
    plot(series=array.get(longTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 and showLongPlots and (not longIthTrailTakeProfitExecuted(1) or debugModeEnabled) else na, title='Long Take Profit 1', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if longIthTrailTakeProfitExecuted(1) or longLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 0 else display.none, force_overlay=True)
    plot(series=array.get(shortTakeProfitPrices, 0) if numOfTakeProfitTargets > 0 and showShortPlots and (not shortIthTrailTakeProfitExecuted(1) or debugModeEnabled) else na, title='Short Take Profit 1', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if shortIthTrailTakeProfitExecuted(1) or shortLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 0 else display.none, force_overlay=True)
    plot(series=array.get(longTakeProfitPrices, 1) if numOfTakeProfitTargets > 1 and showLongPlots and (not longIthTrailTakeProfitExecuted(2) or debugModeEnabled) else na, title='Long Take Profit 2', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if longIthTrailTakeProfitExecuted(2) or longLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 1 else display.none, force_overlay=True)
    plot(series=array.get(shortTakeProfitPrices, 1) if numOfTakeProfitTargets > 1 and showShortPlots and (not shortIthTrailTakeProfitExecuted(2) or debugModeEnabled) else na, title='Short Take Profit 2', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if shortIthTrailTakeProfitExecuted(2) or shortLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 1 else display.none, force_overlay=True)
    plot(series=array.get(longTakeProfitPrices, 2) if numOfTakeProfitTargets > 2 and showLongPlots and (not longIthTrailTakeProfitExecuted(3) or debugModeEnabled) else na, title='Long Take Profit 3', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if longIthTrailTakeProfitExecuted(3) or longLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 2 else display.none, force_overlay=True)
    plot(series=array.get(shortTakeProfitPrices, 2) if numOfTakeProfitTargets > 2 and showShortPlots and (not shortIthTrailTakeProfitExecuted(3) or debugModeEnabled) else na, title='Short Take Profit 3', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if shortIthTrailTakeProfitExecuted(3) or shortLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 2 else display.none, force_overlay=True)
    plot(series=array.get(longTakeProfitPrices, 3) if numOfTakeProfitTargets > 3 and showLongPlots and (not longIthTrailTakeProfitExecuted(4) or debugModeEnabled) else na, title='Long Take Profit 4', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if longIthTrailTakeProfitExecuted(4) or longLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 3 else display.none, force_overlay=True)
    plot(series=array.get(shortTakeProfitPrices, 3) if numOfTakeProfitTargets > 3 and showShortPlots and (not shortIthTrailTakeProfitExecuted(4) or debugModeEnabled) else na, title='Short Take Profit 4', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if shortIthTrailTakeProfitExecuted(4) or shortLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 3 else display.none, force_overlay=True)
    plot(series=array.get(longTakeProfitPrices, 4) if numOfTakeProfitTargets > 4 and showLongPlots and (not longIthTrailTakeProfitExecuted(5) or debugModeEnabled) else na, title='Long Take Profit 5', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if longIthTrailTakeProfitExecuted(5) or longLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 4 else display.none, force_overlay=True)
    plot(series=array.get(shortTakeProfitPrices, 4) if numOfTakeProfitTargets > 4 and showShortPlots and (not shortIthTrailTakeProfitExecuted(5) or debugModeEnabled) else na, title='Short Take Profit 5', color=(DBG_TAKE_PROFIT_COLOR if debugModeEnabled else na) if shortIthTrailTakeProfitExecuted(5) or shortLimitOrStopEntryIsActive else takeProfitColor, linewidth=2, style=plot.style_linebr, offset=1, display=display.all if numOfTakeProfitTargets > 4 else display.none, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
