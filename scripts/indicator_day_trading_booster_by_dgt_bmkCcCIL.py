"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barcolor, barstate, box, chart, close, color,
    dayofmonth, dayofweek, display, extend, fill, format, high, hlc3, input, label, last_bar_index,
    line, linefill, log, low, math, month, na, nz, open, plot, polyline, position, request, script,
    size, string, syminfo, ta, table, text, time, timeframe, timenow, timestamp, volume, xloc,
    year, yloc
)
from pynecore.types import (
    Box, Color, Label, Line, LineFill, NA, Persistent, PersistentSeries,
    Polyline, Series, Table
)
from pynecore.types.chart import ChartPoint


class utcOffsets(Enum):
    EXCHANGE = 'Exchange'
    UTCm5_New_York = 'America/New_York'
    UTC0_London = 'Europe/London'
    UTCp9_Tokyo = 'Asia/Tokyo'
    UTCp10_Sydney = 'Australia/Sydney'
    UTCp4_Dubai = 'Asia/Dubai'
    UTCp1_Berlin = 'Europe/Berlin'
    UTCp1_Paris = 'Europe/Paris'
    UTCp3_Istanbul = 'Europe/Istanbul'
    UTCm6_Chicago = 'America/Chicago'
    UTCm8_Los_Angeles = 'America/Los_Angeles'
    UTCp8_Singapore = 'Asia/Singapore'
    UTCp8_Shanghai = 'Asia/Shanghai'
    UTCp9_Seoul = 'Asia/Seoul'
    UTCp5p30_Kolkata = 'Asia/Kolkata'
    UTCm5_Toronto = 'America/Toronto'
    UTCm8_Vancouver = 'America/Vancouver'
    UTCm8_Tijuana = 'America/Tijuana'
    UTCm7_Denver = 'America/Denver'
    UTCm7_Edmonton = 'America/Edmonton'
    UTCm7_Ciudad_Juarez = 'America/Ciudad_Juarez'
    UTCm6_Mexico_City = 'America/Mexico_City'
    UTCm6_Winnipeg = 'America/Winnipeg'
    UTCm6_Costa_Rica = 'America/Costa_Rica'
    UTCm5_Lima = 'America/Lima'
    UTCm5_Bogota = 'America/Bogota'
    UTCm5_Jamaica = 'America/Jamaica'
    UTCm4p30_Caracas = 'America/Caracas'
    UTCm4_Santiago = 'America/Santiago'
    UTCm4_Manaus = 'America/Manaus'
    UTCm4_La_Paz = 'America/La_Paz'
    UTCm4_Santo_Domingo = 'America/Santo_Domingo'
    UTCm3p30_St_Johns = 'America/St_Johns'
    UTCm3_Sao_Paulo = 'America/Sao_Paulo'
    UTCm3_Buenos_Aires = 'America/Argentina/Buenos_Aires'
    UTCm3_Montevideo = 'America/Montevideo'
    UTCm9_Anchorage = 'America/Anchorage'
    UTCm10_Honolulu = 'Pacific/Honolulu'
    UTCm11_Pago_Pago = 'Pacific/Pago_Pago'
    UTC0_Lisbon = 'Europe/Lisbon'
    UTCp1_Madrid = 'Europe/Madrid'
    UTCp1_Warsaw = 'Europe/Warsaw'
    UTCp2_Kyiv = 'Europe/Kyiv'
    UTCp2_Athens = 'Europe/Athens'
    UTCp3_Moscow = 'Europe/Moscow'
    UTCp4_Samara = 'Europe/Samara'
    UTCp3_Riyadh = 'Asia/Riyadh'
    UTCp3_Baghdad = 'Asia/Baghdad'
    UTCp3p30_Tehran = 'Asia/Tehran'
    UTCp4_Baku = 'Asia/Baku'
    UTCp4_Yerevan = 'Asia/Yerevan'
    UTCp4p30_Kabul = 'Asia/Kabul'
    UTCp2_Jerusalem = 'Asia/Jerusalem'
    UTCp5_Karachi = 'Asia/Karachi'
    UTCp5_Tashkent = 'Asia/Tashkent'
    UTCp5_Yekaterinburg = 'Asia/Yekaterinburg'
    UTCp5p30_Colombo = 'Asia/Colombo'
    UTCp5p45_Kathmandu = 'Asia/Kathmandu'
    UTCp6_Dhaka = 'Asia/Dhaka'
    UTCp6_Almaty = 'Asia/Almaty'
    UTCp6_Omsk = 'Asia/Omsk'
    UTCp6p30_Yangon = 'Asia/Yangon'
    UTCp7_Jakarta = 'Asia/Jakarta'
    UTCp7_Bangkok = 'Asia/Bangkok'
    UTCp7_Krasnoyarsk = 'Asia/Krasnoyarsk'
    UTCp8_Taipei = 'Asia/Taipei'
    UTCp8_Kuala_Lumpur = 'Asia/Kuala_Lumpur'
    UTCp8_Manila = 'Asia/Manila'
    UTCp9_Pyongyang = 'Asia/Pyongyang'
    UTCp9_Yakutsk = 'Asia/Yakutsk'
    UTCp10_Vladivostok = 'Asia/Vladivostok'
    UTCp11_Magadan = 'Asia/Magadan'
    UTCp12_Kamchatka = 'Asia/Kamchatka'
    UTCp9p30_Adelaide = 'Australia/Adelaide'
    UTCp8_Perth = 'Australia/Perth'
    UTCp10_Port_Moresby = 'Pacific/Port_Moresby'
    UTCp11_Noumea = 'Pacific/Noumea'
    UTCp12_Auckland = 'Pacific/Auckland'
    UTCp12_Fiji = 'Pacific/Fiji'
    UTCp13_Tongatapu = 'Pacific/Tongatapu'
    UTCp14_Kiritimati = 'Pacific/Kiritimati'
    UTC0_Accra = 'Africa/Accra'
    UTC0_Casablanca = 'Africa/Casablanca'
    UTCp1_Lagos = 'Africa/Lagos'
    UTCp1_Algiers = 'Africa/Algiers'
    UTCp2_Cairo = 'Africa/Cairo'
    UTCp2_Johannesburg = 'Africa/Johannesburg'
    UTCp3_Addis_Ababa = 'Africa/Addis_Ababa'


class rangeOption(Enum):
    non = 'None'
    or1 = '1m Opening Range'
    or3 = '3m Opening Range'
    or5 = '5m Opening Range'
    or10 = '10m Opening Range'
    or15 = '15m Opening Range'
    or30 = '30m Opening Range'
    or60 = '60m Opening Range'
    rnge = 'Full Range'


@udt
class LEVEL:
    ln: Line = na(Line)
    lb: Label = na(Label)


@udt
class RANGE:
    rHigh: float = na(float)
    rLow: float = na(float)
    bxTxtBg: Box = na(Box)
    lbTop: Label = na(Label)
    lbAvg: Label = na(Label)
    lbBtm: Label = na(Label)
    lnTop: Line = na(Line)
    lnAvg: Line = na(Line)
    lnBtm: Line = na(Line)
    topBrk: bool = na(bool)
    btmBrk: bool = na(bool)


@udt
class VWAP:
    points: list[ChartPoint] = na(list)
    lines: Polyline = na(Polyline)
    labels: Label = na(Label)


display__ren__ = display.all - display.status_line
utcTip: str = 'Market session defaults are calibrated to the America/New_York timezone.\n\nIf you change the Indicator Timezone, session times must be adjusted accordingly to maintain alignment with actual market hours.'
fxGroupChannels: str = 'Asian & European Openning Channels'
fxGroupSydney: str = 'Sydney Market'
fxGroupTokyo: str = 'Tokyo Market'
fxGroupFrankfurt: str = 'Frankfurt Market'
London: str = 'London Market'
fxGroupNewYork: str = 'New York Market'
group_htf: str = 'Trading Day Levels'
dayRefTip = 'Reference Levels estimate potential support and resistance using volatility-based models.\n\n' + '• Average True Range (ATR): Adapts dynamically to recent volatility\n' + '• Previous Day Range (PDH–PDL): Derived from prior session expansion\n\n' + 'These levels help anticipate breakout phases, expansion targets, and mean-reversion zones.'
group_htf2: str = 'Institutional Reference Levels'
group_vwap: str = 'VWAP Framework'
ttip_vwap = 'The Volume Weighted Average Price (VWAP) calculates the average price weighted by traded volume.\n\n' + 'It helps assess whether price is trading at a premium or discount relative to value, ' + 'providing insight into intraday sentiment, trend positioning, and institutional bias.'
ttip_vwapAnchor = 'Anchor Modes:\n\n' + '• Auto:\n' + '  Automatically adapts anchor timeframe based on chart resolution:\n' + '  - ≤ 15m → Daily\n' + '  - > 15m intraday → Weekly\n' + '  - Daily → Monthly\n' + '  - Weekly → Quarterly\n' + '  - Monthly → Yearly\n\n' + '• Interactive:\n' + '  Allows manual placement of the anchor point directly on the chart.\n' + '  Use “Reset points” from the indicator menu to reposition.\n\n' + '• Manual:\n' + '  Uses a fixed higher timeframe anchor independent of chart timeframe.'
ttip_vwapHL = 'High/Low VWAPs compute separate VWAP curves using the highest and lowest prices within the selected anchor period.\n\n' + 'These act as dynamic support and resistance zones and help define value extremes across the anchor timeframe.'
groupPvt: str = 'Pivot & Market Structure Engine'
tooltip_pvt = 'The Pivot Engine identifies potential reversal zones and developing swing structures.\n\n' + 'Core Capabilities:\n' + '• Detects standard Pivot Highs/Lows using user-defined left/right lengths\n' + '• Detects short-term pivots (3-bar logic) for early structure awareness\n' + '• Analyzes price movement and cumulative traded volume between pivot points\n\n' + 'Alert Mode:\n' + 'Enables early notifications for temporary swing points detected after three bars. ' + 'These are developing pivots and may repaint. Use them as preparation signals, not confirmation triggers.'
msTip = 'Automatically detects real-time market structure shifts, including higher highs/lows and lower highs/lows.\n\n' + 'Helps identify trend transitions, continuation phases, and structural breaks across timeframes.'
groupMA: str = 'Moving Average Cloud'
ttip_ma = 'The Moving Average Cloud provides visual guidance on trend direction, momentum shifts, and dynamic support/resistance zones.\n\n' + 'The relationship between the two averages helps identify structural transitions, including bullish and bearish crossover events.'
groupVWCB: str = 'Volume-Weighted Candle Intelligence'
eventsGroup: str = 'Forex Market Events & Volume Trends'
ttip_events = 'This module provides a graphical representation* of typical trading volume behavior**, real-time volume bars, and major Forex market opening/closing events***.\n\n' + '* Displayed on 1-hour and lower timeframes.\n' + '** Typical volume patterns are modeled using the two most actively traded currencies (USD & EUR). Volume dynamics may differ for other currency groups, particularly Asian sessions.\n' + '*** Event schedule does not account for daylight saving adjustments and may show minor timing deviations during seasonal transitions.'
tabularGroup: str = 'Market Sessions — Tabular View'
groupTZ: str = 'Exchange Timezone Settings'


@script.indicator('Day Trading Booster by DGT', 'DDAY ☼☾', True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, max_bars_back=5000, dynamic_requests=True)
def main(
    __input_0__=input.enum(utcOffsets.UTCm5_New_York, 'Indicator Timezone', tooltip=utcTip, inline='inline', display=display__ren__),
    asianShow=input.bool(True, '', inline='Asian', group=fxGroupChannels),
    asianName=input.string('Asian', '', inline='Asian', group=fxGroupChannels, display=display__ren__),
    asianRange=input.session('1900-2000', '', inline='Asian', group=fxGroupChannels, display=display__ren__),
    asianColor=input.color(color.gray, '', inline='Asian', group=fxGroupChannels),
    europeanShow=input.bool(False, '', inline='European', group=fxGroupChannels),
    europeanName=input.string('European', '', inline='European', group=fxGroupChannels, display=display__ren__),
    europeanRange=input.session('0200-0300', '', inline='European', group=fxGroupChannels, display=display__ren__),
    europeanColor=input.color(color.gray, '', inline='European', group=fxGroupChannels),
    sydneyName=input.string('Sydney', '', inline='sydney', group=fxGroupSydney, display=display__ren__),
    sydneyRange=input.session('1700-0200', '', inline='sydney', group=fxGroupSydney, display=display__ren__),
    sydneyColor=input.color(color.new('#556080'), '', inline='sydney', group=fxGroupSydney),
    __input_12__=input.enum(rangeOption.non, ' Session Range', inline='SY', group=fxGroupSydney, display=display__ren__),
    sydneyLast=input.int(1, ' Show Recent', minval=1, inline='SY', group=fxGroupSydney, display=display__ren__),
    tokyoName=input.string('Tokyo', '', inline='tokyo', group=fxGroupTokyo, display=display__ren__),
    tokyoRange=input.session('1900-0400', '', inline='tokyo', group=fxGroupTokyo, display=display__ren__),
    tokyoColor=input.color(color.new('#C080C0'), '', inline='tokyo', group=fxGroupTokyo),
    __input_17__=input.enum(rangeOption.non, ' Session Range', inline='tk', group=fxGroupTokyo, display=display__ren__),
    tokyoLast=input.int(1, ' Show Recent', inline='tk', minval=1, group=fxGroupTokyo, display=display__ren__),
    frankfurtName=input.string('Frankfurt', '', inline='frankfurt', group=fxGroupFrankfurt, display=display__ren__),
    frankfurtRange=input.session('0200-1000', '', inline='frankfurt', group=fxGroupFrankfurt, display=display__ren__),
    frankfurtColor=input.color(color.new('#E6D76A'), '', inline='frankfurt', group=fxGroupFrankfurt),
    __input_22__=input.enum(rangeOption.or1, ' Session Range', inline='fr', group=fxGroupFrankfurt, display=display__ren__),
    frankfurtLast=input.int(1, ' Show Recent', inline='fr', minval=1, group=fxGroupFrankfurt, display=display__ren__),
    londonName=input.string('London', '', inline='london', group=London, display=display__ren__),
    londonRange=input.session('0300-1200', '', inline='london', group=London, display=display__ren__),
    londonColor=input.color(color.new('#7DA3E0'), '', inline='london', group=London),
    __input_27__=input.enum(rangeOption.non, ' Session Range', inline='ln', group=London, display=display__ren__),
    londonLast=input.int(1, ' Show Recent', inline='ln', minval=1, group=London, display=display__ren__),
    newYorkName=input.string('New York', '', inline='newYork', group=fxGroupNewYork, display=display__ren__),
    newYorkRange=input.session('0800-1700', '', inline='newYork', group=fxGroupNewYork, display=display__ren__),
    newYorkColor=input.color(color.new('#7CC58C'), '', inline='newYork', group=fxGroupNewYork),
    __input_32__=input.enum(rangeOption.or5, ' Session Range', inline='ny', group=fxGroupNewYork, display=display__ren__),
    newYorkLast=input.int(1, ' Show Recent', inline='ny', minval=1, group=fxGroupNewYork, display=display__ren__),
    dayOpen=input.string('Open', 'Trading Day', options=('None', 'Open', '1m Opening Range', '3m Opening Range', '5m Opening Range', '10m Opening Range', '15m Opening Range', '30m Opening Range', '60m Opening Range'), inline='DO', group=group_htf, display=display__ren__),
    dayLast=input.int(1, 'Show Recent', minval=1, inline='DO', group=group_htf, display=display__ren__),
    dayColor=input.color(color.new('#90BFF9'), '', inline='DO', group=group_htf),
    dayCandle=input.bool(True, 'Trading Day Candle | Offset', inline='dc', group=group_htf, tooltip='Displays the current trading day candle with optional horizontal offset for improved visual separation.'),
    dayOffset=input.int(33, '', minval=1, inline='dc', group=group_htf, display=display__ren__),
    dayColorUp=input.color(color.new('#089981'), '', inline='dc', group=group_htf),
    dayColorDn=input.color(color.new('#F23645'), '', inline='dc', group=group_htf),
    dayRefLevels=input.string('Previous Day Range (PDH - PDL)', 'Day Reference Levels', options=('None', 'Average True Range (ATR)', 'Previous Day Range (PDH - PDL)'), inline='REFL', group=group_htf, tooltip=dayRefTip, display=display__ren__),
    dayRefColor=input.color(color.new('#E39A5B'), '', inline='REFL', group=group_htf),
    refAlert=input.bool(False, 'Alerts', inline='REFL', group=group_htf),
    dayATRLength=input.int(5, '  ATR Length', minval=1, group=group_htf, tooltip='Period used for ATR calculation when ATR-based reference levels are selected.', display=display__ren__),
    dayRefLevel1=input.float(0.5, '  Level Multiplier #1', minval=0, step=0.1, inline='Ref', group=group_htf, display=display__ren__),
    dayRefLevel2=input.float(1.0, '#2', minval=0, step=0.1, inline='Ref', group=group_htf, display=display__ren__),
    refLast=input.int(1, '  Show Recent Levels', minval=1, group=group_htf, display=display__ren__),
    pdCShow=input.bool(False, 'Previous Day Close', inline='pd', group=group_htf, tooltip='Previous Day Close\n' + 'Plots the prior trading day’s closing price.\n' + '• Combine with the current day’s Open to visualize the New Day Opening Gap (NDOG).\n' + '• Helps identify early-session support/resistance levels and potential breakout zones.\n' + '• Useful for anticipating intraday trend direction and initial liquidity zones.\n\n' + 'Previous Day High / Low\n' + 'Plots the prior trading day’s High and Low levels.\n' + 'Commonly used as liquidity references and breakout confirmation zones.'),
    pdCColor=input.color(color.new('#90BFF9'), '', inline='pd', group=group_htf),
    pdHLShow=input.bool(True, 'Previous Day High / Low', inline='pd', group=group_htf),
    pdHLColor=input.color(color.new('#90BFF9'), '', inline='pd', group=group_htf),
    monHLShow=input.bool(True, 'Weekly Initial Balance (WIB)', inline='pd2', group=group_htf2, tooltip='Tracks the High, Low, and Midpoint formed during Monday’s trading session.\n\n' + 'These levels define the early-week price discovery range and are widely used to identify liquidity zones, breakout potential, and directional bias for the remainder of the week.'),
    monHLColor=input.color(color.new('#5B9CF6'), '', inline='pd2', group=group_htf2),
    weekOpen=input.bool(True, 'Weekly Open', inline='pd3', group=group_htf2),
    weekColor=input.color(color.new('#5B9CF6'), '', inline='pd3', group=group_htf2),
    weeklyClose=input.bool(True, 'Weekly Close', inline='pd3', group=group_htf2, tooltip='Weekly Open\nPlots the opening price of the current trading week.\n\n' + 'Often used as a directional benchmark and equilibrium reference for weekly price action.\n\n' + 'Weekly Close\nDisplays the official weekly closing price, typically defined by Friday’s session close.\n\n' + 'This level often acts as a key institutional reference for positioning, weekend sentiment, and potential gap reactions at the next week’s open.\n\n' + 'The price difference between the previous week’s close and the new week’s open represents New Week Opening Gap (NWOG)\n\n' + '• Highlights potential liquidity zones where stop orders may cluster.\n' + '• Acts as early-week support/resistance, providing clues for trend continuation or reversal.\n' + '• Gauges market sentiment at weekly open: bullish if gap up, bearish if gap down.'),
    weeklyCColor=input.color(color.new('#5B9CF6'), '', inline='pd3', group=group_htf2),
    nwog=input.bool(False, 'Gap Fill', inline='pd3', group=group_htf2),
    weekHL=input.bool(False, 'Weekly Range (High / Mid / Low)', inline='WO', group=group_htf2, tooltip='Displays the current week’s High, Low, and Midpoint levels.\n\n' + 'These boundaries help identify expansion phases, range compression, and key liquidity zones within the weekly structure.'),
    weekHLColor=input.color(color.new('#5B9CF6'), '', inline='WO', group=group_htf2),
    monthOpen=input.bool(False, 'Monthly Open', inline='MO', group=group_htf2, tooltip='Plots the opening price of the current month.\n\n' + 'Commonly used as a higher-timeframe bias reference and macro equilibrium level.'),
    monthColor=input.color(color.new('#3179F5'), '', inline='MO', group=group_htf2),
    monthHL=input.bool(False, 'Monthly Range (High / Mid / Low)', inline='MO2', group=group_htf2, tooltip='Displays the current month’s High, Low, and Midpoint levels.\n\n' + 'These levels define macro range boundaries, liquidity pools, and potential expansion zones.'),
    monthHLColor=input.color(color.new('#3179F5'), '', inline='MO2', group=group_htf2),
    isVwap=input.bool(False, 'Volume Weighted Average Price (VWAP)', group=group_vwap, tooltip=ttip_vwap),
    htf_tf=input.string('Auto', '  Anchor Mode', options=('Auto', 'Interactive', '15 Minutes', '1 Hour', '4 Hours', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'), inline='vwap', group=group_vwap, tooltip=ttip_vwapAnchor, display=display__ren__),
    vwapSource: Series[float] = input.source(hlc3, 'Source', inline='vwap', group=group_vwap, display=display__ren__),
    startDate=input.time(timestamp('1 Mar 2026'), '  Interactive Anchor', inline='inn', group=group_vwap, display=display__ren__),
    vwapBand1=input.bool(False, 'Band #1', inline='B1', group=group_vwap),
    stdevMult1=input.float(1, '', step=0.1, inline='B1', group=group_vwap, display=display__ren__),
    vwapBand2=input.bool(True, 'Band #2', inline='B1', group=group_vwap),
    stdevMult2=input.float(2, '', step=0.1, inline='B1', group=group_vwap, display=display__ren__),
    isVwapHL=input.bool(False, 'High/Low VWAPs', inline='B1H', group=group_vwap, tooltip=ttip_vwapHL),
    vwapShowHL=input.string('High/Low of Week', '', options=('High/Low of Day', 'High/Low of Week', 'High/Low of Month'), inline='B1H', group=group_vwap, display=display__ren__),
    vwapColorH=input.color(color.new('#F23645'), '', inline='B1H', group=group_vwap),
    vwapColorL=input.color(color.new('#089981'), '', inline='B1H', group=group_vwap),
    dispPVT=input.bool(True, 'Pivot Detection | Enable Alerts', inline='MS', group=groupPvt, tooltip=tooltip_pvt),
    pvtAlert=input.bool(False, '', inline='MS', group=groupPvt),
    marketS=input.bool(False, 'Market Structure Shifts | Enable Alerts', inline='MS2', group=groupPvt, tooltip=msTip),
    msAlert=input.bool(False, '', inline='MS2', group=groupPvt),
    pvtLength=input.int(20, '  Pivot Left/Right Length', minval=1, group=groupPvt, display=display__ren__),
    pvtText=input.string('Small', '  Label Text', options=('Tiny', 'Small', 'Normal'), inline='Levels', group=groupPvt, display=display__ren__),
    pvtPrice=input.bool(False, 'Price', inline='Levels', group=groupPvt),
    pvtChange=input.bool(False, 'Change', inline='Levels', group=groupPvt),
    pvtVolume=input.bool(False, 'Volume', inline='Levels', group=groupPvt),
    maDisplay=input.bool(True, 'Moving Average Cloud | Enable Alerts', inline='MAA', group=groupMA, tooltip=ttip_ma),
    maAlert=input.bool(False, '', inline='MAA', group=groupMA),
    maType1=input.string('EMA', ' ', options=('SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'), inline='MA', group=groupMA, display=display__ren__),
    maSource1: Series[float] = input.source(close, '', inline='MA', group=groupMA, display=display__ren__),
    maLength1=input.int(50, '', minval=1, inline='MA', group=groupMA, display=display__ren__),
    maColor1=input.color(color.new('#089981'), '', inline='MA', group=groupMA),
    maType2=input.string('EMA', ' ', options=('SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'), inline='MA2', group=groupMA, display=display__ren__),
    maSource2: Series[float] = input.source(close, '', inline='MA2', group=groupMA, display=display__ren__),
    maLength2=input.int(200, '', minval=1, inline='MA2', group=groupMA, display=display__ren__),
    maColor2=input.color(color.new('#F23645'), '', inline='MA2', group=groupMA),
    vwcb=input.bool(True, 'Volume-Weighted Coloring | Enable Alerts', inline='VAlrt', group=groupVWCB, tooltip='Colors price bars based on current volume relative to its moving average.\n\n' + 'Highlights conviction-driven activity and abnormal participation shifts.'),
    volAlert=input.bool(False, '', inline='VAlrt', group=groupVWCB),
    vwcbLen=input.int(21, '  Volume MA Length', group=groupVWCB, display=display__ren__),
    hThresh=input.float(1.618, '  High Thresh', minval=1.0, step=0.1, inline='dummy1', group=groupVWCB, display=display__ren__),
    lThresh=input.float(0.618, 'Low Thresh', minval=0.1, step=0.1, inline='dummy1', group=groupVWCB, display=display__ren__),
    forexEvents=input.bool(True, 'Forex Market Events & Volume Trends', group=eventsGroup, tooltip=ttip_events),
    __input_102__=input.int(0, '  Vertical Offset', minval=-3, maxval=10, inline='evt', group=eventsGroup, display=display__ren__),
    __input_103__=input.int(7, 'Height', minval=1, maxval=10, inline='evt', group=eventsGroup, display=display__ren__),
    tabularShow=input.bool(True, 'Market Sessions Table', group=tabularGroup, tooltip='Displays a structured session overview panel including:\n\n' + '• Current date & time\n' + '• Active session status\n' + '• Countdown to next session open/close\n\n' + 'Designed to provide a quick executive summary of global session activity.'),
    tabularSize=input.string('Small', '  Display Size', options=('Tiny', 'Small', 'Normal'), inline='STAT', group=tabularGroup, display=display__ren__),
    statPos=input.string('Top Right', 'Position', options=('Top Left', 'Top Center', 'Top Right', 'Middle Right', 'Bottom Left', 'Bottom Center'), inline='STAT', group=tabularGroup, display=display__ren__),
    hideIfNot=input.bool(False, 'Hide on Non-Forex Instruments', group=tabularGroup, tooltip='Automatically hides the session table when the selected symbol is not a Forex instrument.'),
    __input_108__=input.enum(utcOffsets.UTCp10_Sydney, '  Sydney TZ ', inline='TZ1', group=groupTZ, display=display__ren__),
    __input_109__=input.enum(utcOffsets.UTCp9_Tokyo, 'Tokyo TZ ', inline='TZ1', group=groupTZ, display=display__ren__),
    __input_110__=input.enum(utcOffsets.UTCp1_Berlin, '  Frankfurt TZ', group=groupTZ, inline='TZ2', display=display__ren__),
    __input_111__=input.enum(utcOffsets.UTC0_London, 'London TZ', group=groupTZ, inline='TZ2', display=display__ren__),
    __input_112__=input.enum(utcOffsets.UTCm5_New_York, '        New York TZ', group=groupTZ, inline='TZ3', display=display__ren__)
):
    utcOffsetIn = string.tostring(__input_0__)

    sydneyShow = string.tostring(__input_12__)

    tokyoShow = string.tostring(__input_17__)

    frankfurtShow = string.tostring(__input_22__)

    londonShow = string.tostring(__input_27__)

    newYorkShow = string.tostring(__input_32__)



    vwapAnchor = '15' if htf_tf == '15 Minutes' else '60' if htf_tf == '1 Hour' else '240' if htf_tf == '4 Hours' else 'D' if htf_tf == 'Daily' else 'W' if htf_tf == 'Weekly' else 'M' if htf_tf == 'Monthly' else '3M' if htf_tf == 'Quarterly' else '12M' if htf_tf == 'Yearly' else 'D' if timeframe.isintraday and (timeframe.period == '1' or timeframe.period == '3' or timeframe.period == '5' or (timeframe.period == '15')) else 'W' if timeframe.isintraday and (timeframe.period == '30' or timeframe.period == '45' or timeframe.period == '60' or (timeframe.period == '120') or (timeframe.period == '180') or (timeframe.period == '240')) else 'M' if timeframe.isdaily else '3M' if timeframe.isweekly else '12M' if timeframe.ismonthly else '3M'


    pvtTextSize = size.small if pvtText == 'Small' else size.normal if pvtText == 'Normal' else size.tiny



    oscVO = __input_102__ / 10
    oscHight = 11 - __input_103__

    textSize2 = size.small if tabularSize == 'Small' else size.normal if tabularSize == 'Normal' else size.tiny

    sydneyLocal = string.tostring(__input_108__)
    tokyoLocal = string.tostring(__input_109__)
    frankfurtLocal = string.tostring(__input_110__)
    londonLocal = string.tostring(__input_111__)
    newYorkLocal = string.tostring(__input_112__)

    utcOffset = syminfo.timezone if utcOffsetIn == 'Exchange' else utcOffsetIn

    noColor: Color = color.new('#00000000')

    dayChange = timeframe.change('D')
    fxChartTF = timeframe.in_seconds() / 60 <= 60 and (not timeframe.isseconds)
    dayChartTF = timeframe.in_seconds() / 60 <= 240 and (not timeframe.isseconds)
    nzVolume = nz(volume)
    isVoly = ta.cum(nzVolume) > 0

    def lnStyle(style):
        __block_result__ = na
        __switch__ = style
        if __switch__ == 'Solid':
            __block_result__ = line.style_solid
        elif __switch__ == 'Dashed':
            __block_result__ = line.style_dashed
        elif __switch__ == 'Dotted':
            __block_result__ = line.style_dotted
        return __block_result__

    def timeInRange(sessRange, utc):
        return True if not na(time('1', sessRange, utc)) else False

    @overload
    def timeRange(opt, sessRange):
        __block_result_1__ = na
        if opt == 'Full Range':
            __block_result_1__ = sessRange
        elif string.contains(opt, 'Opening Range'):
            srOH = cast_int(string.tonumber(string.substring(sessRange, 0, 2)))
            srOM = cast_int(string.tonumber(string.substring(sessRange, 2, 4)))

            n = string.tonumber(string.substring(opt, 0, string.pos(opt, 'm ')))
            cH = srOH if (srOM + n) % 60 == srOM + n else (srOH + 1) % 24
            cM = (srOM + n) % 60

            __block_result_1__ = string.substring(sessRange, 0, 2) + string.substring(sessRange, 2, 5) + ('0' if cH < 10 else '') + string.tostring(cH) + ('0' if cM < 10 else '') + string.tostring(cM)
        return __block_result_1__

    @overload
    def timeRange(opt, startTime, utc):
        sessRange = string.format_time(startTime, 'HHmm', utc)

        srOH = cast_int(string.tonumber(string.substring(sessRange, 0, 2)))
        srOM = cast_int(string.tonumber(string.substring(sessRange, 2, 4)))
        srOH = (srOH + 1) % 24 if string.contains(syminfo.prefix, 'BIST') else srOH
        srOM = 0 if string.contains(syminfo.prefix, 'BIST') else srOM - srOM % 5

        n = string.tonumber(string.substring(opt, 0, string.pos(opt, 'm ')))
        cH = srOH if (srOM + n) % 60 == srOM + n else (srOH + 1) % 24
        cM = (srOM + n) % 60

        return ('0' if srOH < 10 else '') + string.tostring(srOH) + ('0' if srOM < 10 else '') + string.tostring(srOM) + '-' + ('0' if cH < 10 else '') + string.tostring(cH) + ('0' if cM < 10 else '') + string.tostring(cM)



    @overload
    @method
    def updateRange(this: RANGE, H, L, name):
        line.set_y1(this.lnTop, H)
        line.set_xy2(this.lnTop, bar_index, H)
        line.set_y1(this.lnAvg, math.avg(H, L))
        line.set_xy2(this.lnAvg, bar_index, math.avg(H, L))
        line.set_y1(this.lnBtm, L)
        line.set_xy2(this.lnBtm, bar_index, L)

        box.set_top(this.bxTxtBg, H)
        box.set_rightbottom(this.bxTxtBg, bar_index, L)

        label.set_xy(this.lbTop, bar_index, H)
        label.set_tooltip(this.lbTop, name + ' High · ' + string.tostring(H, format.mintick))
        label.set_xy(this.lbAvg, bar_index, math.avg(H, L))
        label.set_tooltip(this.lbAvg, name + ' Mean · ' + string.tostring(math.avg(H, L), format.mintick))
        label.set_xy(this.lbBtm, bar_index, L)
        return label.set_tooltip(this.lbBtm, name + ' Low · ' + string.tostring(L, format.mintick))

    ltf = '15S' if timeframe.isminutes and timeframe.multiplier == 1 else '1S' if timeframe.isseconds else '1'

    def renderRange(show, name, sessRange, color__ren__, last, utc, sessFull):
        __block_result_2__ = na
        if show != 'None':
            rngArray: Persistent[list[RANGE]] = array.new(0, NA(RANGE))

            if array.size(rngArray) > last:
                lastRNG = array.pop(rngArray)
                method_call('delete', lastRNG.bxTxtBg)
                method_call('delete', lastRNG.lbTop)
                method_call('delete', lastRNG.lbAvg)
                method_call('delete', lastRNG.lbBtm)
                method_call('delete', lastRNG.lnTop)
                method_call('delete', lastRNG.lnAvg)
                method_call('delete', lastRNG.lnBtm)

            processRange: Persistent[bool] = False
            barIndex: Persistent[int] = na(int)
            extend__ren__ = show != 'Full Range'

            ltfSession, ltfSessionFull, ltfHigh, ltfLow = request.security_lower_tf(syminfo.tickerid, ltf, (timeInRange(sessRange, utc), timeInRange(sessFull, utc), high, low))

            if method_call('some', ltfSession) and (not processRange):
                barIndex = bar_index

                sliceHigh = method_call('slice', ltfHigh, method_call('indexof', ltfSession, True), method_call('lastindexof', ltfSession, True) + 1)
                rangeHigh = method_call('max', sliceHigh)
                sliceLow = method_call('slice', ltfLow, method_call('indexof', ltfSession, True), method_call('lastindexof', ltfSession, True) + 1)
                rangeLow = method_call('min', sliceLow)

                if method_call('size', ltfHigh) == method_call('lastindexof', ltfSession, True) + 1:
                    processRange = True

                array.unshift(rngArray, RANGE(rangeHigh, rangeLow, box.new(bar_index, rangeHigh, bar_index, rangeLow, na, bgcolor=color.new(color__ren__, 69) if extend__ren__ else color.new(color__ren__, 89), text='' if extend__ren__ and show != 'Channel' else name, text_size=size.tiny, text_color=color__ren__, text_halign=text.align_left, text_valign=text.align_top), label.new(bar_index, rangeHigh, name + ' High', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small, tooltip=name + ' ' + show + ' High · ' + string.tostring(rangeHigh, format.mintick)), label.new(bar_index, math.avg(rangeHigh, rangeLow), name + ' Mean', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small, tooltip=name + ' ' + show + ' Mean · ' + string.tostring(math.avg(rangeHigh, rangeLow), format.mintick)), label.new(bar_index, rangeLow, name + ' Low', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small, tooltip=name + ' ' + show + ' Low · ' + string.tostring(rangeLow, format.mintick)), line.new(bar_index, rangeHigh, bar_index, rangeHigh, color=color__ren__), line.new(bar_index, math.avg(rangeHigh, rangeLow), bar_index, math.avg(rangeHigh, rangeLow), color=color__ren__, style=line.style_dotted), line.new(bar_index, rangeLow, bar_index, rangeLow, color=color__ren__), False, False))

                if name == 'Day':
                    linefill.new(array.first(rngArray).lnTop, array.first(rngArray).lnBtm, color.new(color__ren__, 95))

            __block_result_3__ = na
            if array.size(rngArray) > 0 and bar_index > barIndex:
                first = array.first(rngArray)

                __block_result_4__ = na
                if processRange:
                    if method_call('every', ltfSession):
                        first.rHigh = math.max(first.rHigh, method_call('max', ltfHigh))
                        first.rLow = math.min(first.rLow, method_call('min', ltfLow))
                    elif method_call('some', ltfSession):
                        sliceHigh = method_call('slice', ltfHigh, 0, method_call('lastindexof', ltfSession, True) + 1)
                        first.rHigh = math.max(first.rHigh, method_call('max', sliceHigh))
                        sliceLow = method_call('slice', ltfLow, 0, method_call('lastindexof', ltfSession, True) + 1)
                        first.rLow = math.min(first.rLow, method_call('min', sliceLow))

                    if method_call('size', ltfSession) > 0:
                        if not method_call('last', ltfSession):
                            processRange = False
                        else:
                            updateRange(first, first.rHigh, first.rLow, name + ' ' + show)

                    __block_result_4__ = True
                else:
                    if extend__ren__:
                        if method_call('size', ltfSessionFull) > 0:
                            sessionActive = method_call('last', ltfSessionFull)
                            if sessionActive or name == 'Day' or name == 'Asian' or (name == 'European'):
                                method_call('set_x2', first.lnTop, bar_index + 1)
                                method_call('set_x', first.lbTop, bar_index + 1)

                                method_call('set_x2', first.lnAvg, bar_index + 1)
                                method_call('set_x', first.lbAvg, bar_index + 1)

                                method_call('set_x2', first.lnBtm, bar_index + 1)
                                method_call('set_x', first.lbBtm, bar_index + 1)
                    else:
                        if not first.topBrk:
                            if high > first.rHigh:
                                first.topBrk = True
                            method_call('set_x2', first.lnTop, bar_index)
                            method_call('set_x', first.lbTop, bar_index)

                        if not first.btmBrk:
                            if low < first.rLow:
                                first.btmBrk = True
                            method_call('set_x2', first.lnBtm, bar_index)
                            method_call('set_x', first.lbBtm, bar_index)
                    __block_result_4__ = True
                __block_result_3__ = __block_result_4__
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    if fxChartTF and syminfo.type != 'stock' and (syminfo.type != 'bond') and (syminfo.type != 'fund'):
        renderRange('Channel' if asianShow else 'None', asianName, asianRange, asianColor, 1, utcOffset, asianRange)
        renderRange('Channel' if europeanShow else 'None', europeanName, europeanRange, europeanColor, 1, utcOffset, europeanRange)

        renderRange(sydneyShow, sydneyName, timeRange(sydneyShow, sydneyRange), sydneyColor, sydneyLast, utcOffset, sydneyRange)
        renderRange(tokyoShow, tokyoName, timeRange(tokyoShow, tokyoRange), tokyoColor, tokyoLast, utcOffset, tokyoRange)
        renderRange(frankfurtShow, frankfurtName, timeRange(frankfurtShow, frankfurtRange), frankfurtColor, frankfurtLast, utcOffset, frankfurtRange)
        renderRange(londonShow, londonName, timeRange(londonShow, londonRange), londonColor, londonLast, utcOffset, londonRange)
        renderRange(newYorkShow, newYorkName, timeRange(newYorkShow, newYorkRange), newYorkColor, newYorkLast, utcOffset, newYorkRange)

    def renderLevel(name, start, end, value, color__ren__, style, width, last, tip):
        levelArray: Persistent[list[LEVEL]] = array.new(0, LEVEL())

        if array.size(levelArray) > last - 1:
            lastLVL = array.pop(levelArray)
            method_call('delete', lastLVL.ln)
            method_call('delete', lastLVL.lb)

        if array.size(levelArray) > 0:
            for i in pine_range(0, array.size(levelArray) - 1):
                method_call('set_textcolor', array.get(levelArray, i).lb, noColor)

        return array.unshift(levelArray, LEVEL(line.new(start, value, end, value, xloc.bar_time, color=color__ren__, style=style, width=width), label.new(end, value, name + ' · ' + string.tostring(value, format.mintick), xloc.bar_time, color=noColor, style=label.style_label_left, textcolor=color__ren__, size=size.small, tooltip=tip + ' · ' + string.tostring(value, format.mintick))))

    def previousPriceRange(htf):
        htf_h: Persistent[float] = na(float)
        htf_l: Persistent[float] = na(float)
        htf_hx: Persistent[float] = na(float)
        htf_lx: Persistent[float] = na(float)
        htf_ht: Persistent[int] = na(int)
        htf_lt: Persistent[int] = na(int)
        htf_hxt: Persistent[int] = na(int)
        htf_lxt: Persistent[int] = na(int)

        if timeframe.change(htf):
            htf_hx = htf_h
            htf_h = high
            htf_lx = htf_l
            htf_l = low
            htf_hxt = htf_ht
            htf_ht = time
            htf_lxt = htf_lt
            htf_lt = time
        else:
            if high > htf_h:
                htf_h = high
                htf_ht = time

            if low < htf_l:
                htf_l = low
                htf_lt = time

        return (htf_hx, htf_hxt, htf_lx, htf_lxt)

    @method
    def updateLevel(this: LEVEL, newPeriod: bool, src: Series, idx, col: Color, name: str, tName: str):
        rightEdge = bar_index + 5

        __block_result_5__ = na
        if newPeriod:
            if not na(this.ln):
                line.delete(this.ln)
                label.delete(this.lb)

            this.ln = line.new(bar_index[idx], src[idx], rightEdge, src[idx], color=col)
            this.lb = label.new(rightEdge, src[idx], name + ' · ' + string.tostring(src[idx], format.mintick), color=noColor, textcolor=col, style=label.style_label_left, size=size.small, textalign=text.align_left, tooltip=tName + ' : ≅' + string.format_time(time[idx], "dd-MM-yyyy HH:mm 'UTC'Z"))
            __block_result_5__ = True
        else:
            line.set_x2(this.ln, rightEdge)
            label.set_x(this.lb, rightEdge)
            __block_result_5__ = True
        return __block_result_5__

    def refAlers(s, r, l):
        if high > r and close[1] < r:
            alert('Price (' + string.tostring(close, format.mintick) + ')' + (' has crossed above the R' if close > r else ' has touched the R') + l + ' Reference Level(' + string.tostring(r, format.mintick) + '). Price interactions at resistance can indicate potential trend continuation or reversal. Use this as an early signal and seek further confirmation before acting.', alert.freq_once_per_bar_close)

        __block_result_6__ = na
        if low < s and close[1] > s:
            __block_result_6__ = alert('Price (' + string.tostring(close, format.mintick) + ')' + (' has dropped below the S' if close < s else ' has touched the S') + l + ' Reference Level(' + string.tostring(s, format.mintick) + '). Dropping below support can suggest a potential trend change or false breakdown. Treat this as an early signal and confirm with other indicators.', alert.freq_once_per_bar_close)
        return __block_result_6__

    H1, HT1, L1, LT1 = previousPriceRange('D')
    atr = ta.atr(dayATRLength)

    if dayChange and (dayOpen == 'Open' or dayRefLevels != 'None' or pdHLShow) and dayChartTF:
        dayStart = time
        dayEnd = time + 3600000 * 24
        O0 = open

        if dayOpen == 'Open':
            renderLevel('DO', dayStart, dayEnd, O0, dayColor, line.style_solid, 1, dayLast, 'Trading Day Open')

        if dayRefLevels != 'None':
            atrRange = request.security(syminfo.tickerid, 'D', atr)
            refRange = atrRange if dayRefLevels == 'Average True Range (ATR)' else H1 - L1

            renderLevel('R1', dayStart, dayEnd, O0 + refRange * dayRefLevel1, dayRefColor, line.style_dotted, 2, refLast, 'Reference Model: ' + dayRefLevels + '\nFirst Reference Level')
            renderLevel('S1', dayStart, dayEnd, O0 - refRange * dayRefLevel1, dayRefColor, line.style_dotted, 2, refLast, 'Reference Model: ' + dayRefLevels + '\nFirst Reference Level')

            if refAlert:
                refAlers(O0 - refRange * dayRefLevel1, O0 + refRange * dayRefLevel1, '1')

            if dayRefLevel2 > dayRefLevel1:
                renderLevel('R2', dayStart, dayEnd, O0 + refRange * dayRefLevel2, dayRefColor, line.style_dotted, 2, refLast, 'Reference Model: ' + dayRefLevels + '\nSecond Reference Level')
                renderLevel('S2', dayStart, dayEnd, O0 - refRange * dayRefLevel2, dayRefColor, line.style_dotted, 2, refLast, 'Reference Model: ' + dayRefLevels + '\nSecond Reference Level')

                if refAlert:
                    refAlers(O0 - refRange * dayRefLevel2, O0 + refRange * dayRefLevel2, '2')

        if pdHLShow:
            renderLevel('PDH', HT1, dayEnd, H1, pdHLColor, line.style_solid, 1, 1, 'Previous Trading Day High\n ≅' + string.format_time(HT1, "dd-MM-yyyy HH:mm 'UTC'Z"))
            renderLevel('PDL', LT1, dayEnd, L1, pdHLColor, line.style_solid, 1, 1, 'Previous Trading Day Low\n ≅' + string.format_time(LT1, "dd-MM-yyyy HH:mm 'UTC'Z"))

    daySession: Persistent[str] = na(str)

    if string.contains(dayOpen, 'Opening Range') and dayChartTF:
        if dayChange:
            daySession = timeRange(dayOpen, time, utcOffset)

        renderRange(dayOpen, 'Day', daySession, dayColor, dayLast, utcOffset, daySession)

    if dayCandle and dayChartTF:
        cndlBody: Persistent[Box] = box.new(na, na, na, na, noColor, bgcolor=noColor)
        lnDHL: Persistent[Line] = line.new(na, na, na, na, xloc.bar_index, extend.none, noColor, line.style_solid, 2)
        lbDO: Persistent[Label] = label.new(na, na, 'Day Open', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small)
        lbDH: Persistent[Label] = label.new(na, na, 'Day High', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small)
        lbDL: Persistent[Label] = label.new(na, na, 'Day Low', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small)
        lbDC: Persistent[Label] = label.new(na, na, 'Day Close', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small)

        if dayChange:
            barColor = dayColorDn if open > close else dayColorUp
            box.set_bgcolor(cndlBody, barColor)
            box.set_rightbottom(cndlBody, last_bar_index + dayOffset + 5, open)
            box.set_lefttop(cndlBody, last_bar_index + dayOffset - 5, close)
            line.set_color(lnDHL, barColor)
            line.set_xy1(lnDHL, last_bar_index + dayOffset, high)
            line.set_xy2(lnDHL, last_bar_index + dayOffset, low)
            label.set_xy(lbDO, last_bar_index + dayOffset, open)
            label.set_tooltip(lbDO, 'Day Open · ' + string.tostring(open, format.mintick))
            label.set_xy(lbDH, last_bar_index + dayOffset, high)
            label.set_tooltip(lbDH, 'Day High · ' + string.tostring(high, format.mintick))
            label.set_xy(lbDL, last_bar_index + dayOffset, low)
            label.set_tooltip(lbDL, 'Day Low · ' + string.tostring(low, format.mintick))
            label.set_xy(lbDC, last_bar_index + dayOffset, close)
            label.set_tooltip(lbDC, 'Day Close · ' + string.tostring(close, format.mintick))
        else:
            barColor = dayColorDn if box.get_bottom(cndlBody) > close else dayColorUp
            box.set_bgcolor(cndlBody, barColor)
            box.set_right(cndlBody, last_bar_index + dayOffset + 5)
            box.set_lefttop(cndlBody, last_bar_index + dayOffset - 5, close)
            dHigh = math.max(high, line.get_y1(lnDHL))
            dLow = math.min(low, line.get_y2(lnDHL))
            line.set_color(lnDHL, barColor)
            line.set_xy1(lnDHL, last_bar_index + dayOffset, dHigh)
            line.set_xy2(lnDHL, last_bar_index + dayOffset, dLow)
            label.set_x(lbDO, last_bar_index + dayOffset)
            label.set_xy(lbDH, last_bar_index + dayOffset, dHigh)
            label.set_tooltip(lbDH, 'Day High · ' + string.tostring(dHigh, format.mintick))
            label.set_xy(lbDL, last_bar_index + dayOffset, dLow)
            label.set_tooltip(lbDL, 'Day Low · ' + string.tostring(dLow, format.mintick))
            label.set_xy(lbDC, last_bar_index + dayOffset, close)
            label.set_tooltip(lbDC, 'Day Close · ' + string.tostring(close, format.mintick))

    pdC: Persistent[LEVEL] = LEVEL()

    if pdCShow and timeframe.isintraday:
        updateLevel(pdC, dayChange, close, 1, pdCColor, 'PDC', 'Previous Trading Day Close')

    @overload
    @method
    def updateRange(this: RANGE, newPeriod: bool, col: Color, name: str, tName: str, update: bool):
        rightEdge = bar_index + 5
        mid: float = (this.rHigh + this.rLow) * 0.5

        __block_result_7__ = na
        if newPeriod:
            this.rHigh = high
            this.rLow = low
            mid = (this.rHigh + this.rLow) * 0.5

            if not na(this.lnTop):
                line.delete(this.lnTop)
                line.delete(this.lnBtm)
                line.delete(this.lnAvg)
                label.delete(this.lbTop)
                label.delete(this.lbBtm)
                label.delete(this.lbAvg)

            this.lnTop = line.new(bar_index, this.rHigh, rightEdge, this.rHigh, color=col)
            this.lnAvg = line.new(bar_index, mid, rightEdge, mid, color=col, style=line.style_dotted)
            this.lnBtm = line.new(bar_index, this.rLow, rightEdge, this.rLow, color=col)

            this.lbTop = label.new(rightEdge, this.rHigh, name + 'H · ' + string.tostring(this.rHigh, format.mintick), color=noColor, textcolor=col, style=label.style_label_left, size=size.small, textalign=text.align_left, tooltip=tName + ' High: ≅' + string.format_time(time, "dd-MM-yyyy HH:mm 'UTC'Z"))
            this.lbAvg = label.new(rightEdge, mid, name + 'M · ' + string.tostring(mid, format.mintick), color=noColor, textcolor=col, style=label.style_label_left, size=size.small, textalign=text.align_left, tooltip=tName + ' Midpoint (Equilibrium)')
            this.lbBtm = label.new(rightEdge, this.rLow, name + 'L · ' + string.tostring(this.rLow, format.mintick), color=noColor, textcolor=col, style=label.style_label_left, size=size.small, textalign=text.align_left, tooltip=tName + ' Low: ≅' + string.format_time(time, "dd-MM-yyyy HH:mm 'UTC'Z"))
            __block_result_7__ = True
        else:
            newHigh: bool = high > this.rHigh
            newLow: bool = low < this.rLow

            if newHigh and update:
                this.rHigh = high
                line.set_xy1(this.lnTop, bar_index, this.rHigh)
                label.set_text(this.lbTop, name + 'H · ' + string.tostring(this.rHigh, format.mintick))
                label.set_tooltip(this.lbTop, tName + ' High: ≅' + string.format_time(time, "dd-MM-yyyy HH:mm 'UTC'Z"))

            if newLow and update:
                this.rLow = low
                line.set_xy1(this.lnBtm, bar_index, this.rLow)
                label.set_text(this.lbBtm, name + 'L · ' + string.tostring(this.rLow, format.mintick))
                label.set_tooltip(this.lbBtm, tName + ' Low: ≅' + string.format_time(time, "dd-MM-yyyy HH:mm 'UTC'Z"))

            mid = (this.rHigh + this.rLow) * 0.5

            if not na(this.lnTop):
                line.set_xy2(this.lnTop, rightEdge, this.rHigh)
                line.set_xy2(this.lnBtm, rightEdge, this.rLow)
                line.set_y1(this.lnAvg, mid)
                line.set_xy2(this.lnAvg, rightEdge, mid)

                label.set_xy(this.lbTop, rightEdge, this.rHigh)
                label.set_xy(this.lbBtm, rightEdge, this.rLow)
                label.set_xy(this.lbAvg, rightEdge, mid)
                label.set_text(this.lbAvg, name + 'M · ' + string.tostring(mid, format.mintick))
            __block_result_7__ = True
        return __block_result_7__

    weekChange = timeframe.change('W')

    weekOpenn: Persistent[LEVEL] = LEVEL()
    weekRange: Persistent[RANGE] = RANGE()

    if (weekHL or weekOpen) and timeframe.isintraday:
        if weekHL:
            updateRange(weekRange, weekChange, weekHLColor, 'W', 'Week', True)
        if weekOpen:
            updateLevel(weekOpenn, weekChange, open, 0, weekHLColor, 'WO', 'Weekly Open')

    weekClose: Persistent[LEVEL] = LEVEL()

    if weeklyClose and timeframe.isintraday and (syminfo.type == 'forex' or syminfo.type == 'stock'):
        updateLevel(weekClose, weekChange, close, 1, weeklyCColor, 'WC', 'Weekly Close')

    nwogMid: Persistent[LEVEL] = LEVEL()

    if nwog:
        linefill.new(weekOpenn.ln, weekClose.ln, color.new(color.new('#5BC58C'), 89) if line.get_y1(weekOpenn.ln) > line.get_y1(weekClose.ln) else color.new(color.new('#F26D5C'), 89))
        updateLevel(nwogMid, weekChange and (not na(weekOpenn.ln)) and (not na(weekClose.ln)), math.avg(line.get_y1(weekOpenn.ln), line.get_y1(weekClose.ln)), 0, color.new(color.new('#5BC58C'), 50) if line.get_y1(weekOpenn.ln) > line.get_y1(weekClose.ln) else color.new(color.new('#F26D5C'), 50), 'WOG M', 'Week Opening Gap Mid')

    mondayRange: Persistent[RANGE] = RANGE()

    isMondayStart = weekChange and dayChange
    processMonday: Persistent[bool] = False

    if isMondayStart:
        processMonday = True
    elif dayChange and (not isMondayStart):
        processMonday = False

    if monHLShow and timeframe.isintraday:
        updateRange(mondayRange, isMondayStart, monHLColor, 'WIB ', 'Weekly Initial Balance (WIB)\nMonaday', processMonday)

    monthChange = timeframe.change('M')

    monthRange: Persistent[RANGE] = RANGE()
    monthOpenn: Persistent[LEVEL] = LEVEL()

    if (monthHL or monthOpen) and (timeframe.isintraday or timeframe.isdaily):
        if monthHL:
            updateRange(monthRange, monthChange, monthHLColor, 'M', 'Monthly', True)
        if monthOpen:
            updateLevel(monthOpenn, monthChange, open, 0, monthHLColor, 'MO', 'Monthly Open')

    def renderPolyline(source, anchor, color__ren__, style, txt, width):
        vwap: Persistent[VWAP] = VWAP(array.new(na(list[ChartPoint]), NA(ChartPoint)))

        if anchor:
            array.clear(vwap.points)
            array.push(vwap.points, chart.point.from_index(bar_index, source))
        else:
            array.push(vwap.points, chart.point.from_index(bar_index, source))

            if array.size(vwap.points) == 2002:
                array.remove(vwap.points, 1)

        __block_result_8__ = na
        if barstate.islast and array.size(vwap.points) > 0:
            polyline.delete(vwap.lines)
            vwap.lines = polyline.new(vwap.points, False, False, line_color=color__ren__, line_style=lnStyle(style), line_width=width)
            label.delete(vwap.labels)
            vwap.labels = label.new(array.last(vwap.points), 'hidden', color=noColor, style=label.style_label_left, textcolor=noColor, size=size.small, tooltip=txt + ' · ' + string.tostring(array.last(vwap.points).price, format.mintick))
            __block_result_8__ = vwap.labels
        return __block_result_8__

    if isVwap:
        autoAnchor = timeframe.change(vwapAnchor)
        interAnchor = startDate == time
        anchor = interAnchor if htf_tf == 'Interactive' else autoAnchor
        vwap, upper, lower = ta.vwap(vwapSource, anchor, stdevMult1)

        if isVoly:
            renderPolyline(vwap, anchor, color.new('#0496FF'), 'Solid', 'VWAP(' + ('Interactive' if htf_tf == 'Interactive' else vwapAnchor) + ')', 1)

            if vwapBand1:
                renderPolyline(upper, anchor, color.new('#4CAF50'), 'Dotted', 'VWAP(' + ('Interactive' if htf_tf == 'Interactive' else vwapAnchor) + ') Upper Band #1', 2)
                renderPolyline(lower, anchor, color.new('#4CAF50'), 'Dotted', 'VWAP(' + ('Interactive' if htf_tf == 'Interactive' else vwapAnchor) + ') Lower Band #1', 2)

            if vwapBand2:
                renderPolyline(vwap + (upper - vwap) / stdevMult1 * stdevMult2, anchor, color.new('#808000'), 'Dotted', 'VWAP(' + ('Interactive' if htf_tf == 'Interactive' else vwapAnchor) + ') Upper Band #2', 2)
                renderPolyline(vwap - (vwap - lower) / stdevMult1 * stdevMult2, anchor, color.new('#808000'), 'Dotted', 'VWAP(' + ('Interactive' if htf_tf == 'Interactive' else vwapAnchor) + ') Lower Band #2', 2)

    if isVwapHL:
        highOf: Persistent[float] = na(float)
        lowOf: Persistent[float] = na(float)

        __block_result_9__ = na
        __switch_1__ = vwapShowHL
        if __switch_1__ == 'High/Low of Day':
            __block_result_9__ = dayChange
        elif __switch_1__ == 'High/Low of Week':
            __block_result_9__ = weekChange
        elif __switch_1__ == 'High/Low of Month':
            __block_result_9__ = monthChange
        xChange = __block_result_9__

        if xChange:
            highOf = high
            lowOf = low
        else:
            highOf = math.max(high, highOf)
            lowOf = math.min(low, lowOf)

        vwaph = ta.vwap(high, highOf == high)
        if isVoly:
            renderPolyline(vwaph, highOf == high, vwapColorH, 'Solid', string.replace(vwapShowHL, '/Low', '', 0) + ' VWAP', 1)

        vwapl = ta.vwap(low, lowOf == low)
        if isVoly:
            renderPolyline(vwapl, lowOf == low, vwapColorL, 'Solid', string.replace(vwapShowHL, 'High/', '', 0) + ' VWAP', 1)

    def f_drawOnlyLabelX(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip):
        return label.new(_x, _y, _text, _xloc, _yloc, _color, _style, _textcolor, _size, _textalign, _tooltip)

    def tradedVolume(_len, _calc, _offset):
        __block_result_10__ = na
        if _calc and isVoly:
            vol: float = 0.0
            for x in pine_range(0, _len - 1, 1):
                vol = vol + volume[_offset + x]
            __block_result_10__ = vol
        return __block_result_10__

    pvtHigh = ta.pivothigh(pvtLength, pvtLength)
    pvtLow = ta.pivotlow(pvtLength, pvtLength)

    if dispPVT:
        proceed = not na(pvtHigh) or not na(pvtLow)

        pvtLengthTemp: int = 3
        pvtHighTemp = ta.pivothigh(pvtLengthTemp, pvtLengthTemp)
        pvtLowTemp = ta.pivotlow(pvtLengthTemp, pvtLengthTemp)
        proceedTemp = not na(pvtHighTemp) or not na(pvtLowTemp)

        x1: Persistent[int] = 0
        x2: Persistent[int] = 0
        x2Temp: Persistent[int] = 0
        pvtHigh1: Persistent[float] = 0.0
        pvtLow1: Persistent[float] = 0.0
        pvtHigh1Temp: Persistent[float] = 0.0
        pvtLow1Temp: Persistent[float] = 0.0

        if proceed:
            x1 = x2
            x2 = bar_index

        if proceedTemp:
            x2Temp = bar_index

        profileLength = x2 - x1
        profileLengthTemp = x2Temp - pvtLengthTemp - x2 + pvtLength

        tempHigh: PersistentSeries[Label] = na(Label)
        tempLow: PersistentSeries[Label] = na(Label)

        if not na(pvtHigh):
            tradedVolume__00000263__ = tradedVolume(profileLength, proceed, pvtLength)
            TX = ' · Higher High' if pvtHigh > pvtHigh1 else ' · Lower High'
            none = not pvtPrice and (not pvtChange) and (not pvtVolume or not isVoly)
            pvtDispText = '▼' if none else (string.tostring(pvtHigh, format.mintick) if pvtPrice else '') + ((' ↑ %' if pvtPrice else '↑ %') + string.tostring((pvtHigh - pvtLow1) * 100 / pvtLow1, '#.##') if pvtChange else '') + (('\n' if pvtPrice or pvtChange else '') + string.tostring(tradedVolume__00000263__, format.volume) if pvtVolume and isVoly else '')
            f_drawOnlyLabelX(bar_index[pvtLength], pvtHigh, pvtDispText, xloc.bar_index, yloc.price, noColor if none else color.new('#E8BCBC'), label.style_label_down, color.new('#E8BCBC') if none else color.black, pvtTextSize, text.align_center, 'Pivot High · ' + string.tostring(pvtHigh, format.mintick) + TX + '\n -Price Change: ↑ %' + string.tostring((pvtHigh - pvtLow1) * 100 / pvtLow1, '#.##') + ('\n -Traded Volume: ' + string.tostring(tradedVolume__00000263__, format.volume) + ' (' + string.tostring(profileLength - 1) + ' bars)\n      *Average Volume/Bar: ' + string.tostring(tradedVolume__00000263__ / (profileLength - 1), format.volume) if isVoly else '') + '\n\nNumber of Bars: ' + string.tostring(profileLength))
            pvtHigh1 = pvtHigh
            label.delete(tempHigh[1])
            if x2 - pvtLength > x2Temp - pvtLengthTemp:
                label.delete(tempLow[1])

        if not na(pvtLow):
            tradedVolume__00000276__ = tradedVolume(profileLength, proceed, pvtLength)
            TX = ' · Lower Low' if pvtLow < pvtLow1 else ' · Higher Low'
            none = not pvtPrice and (not pvtChange) and (not pvtVolume or not isVoly)
            pvtDispText = '▲' if none else (string.tostring(pvtLow, format.mintick) if pvtPrice else '') + ((' ↓ %' if pvtPrice else '↓ %') + string.tostring((pvtHigh1 - pvtLow) * 100 / pvtHigh1, '#.##') if pvtChange else '') + (('\n' if pvtPrice or pvtChange else '') + string.tostring(tradedVolume__00000276__, format.volume) if pvtVolume and isVoly else '')
            f_drawOnlyLabelX(bar_index[pvtLength], pvtLow, pvtDispText, xloc.bar_index, yloc.price, noColor if none else color.new('#B3C9F5'), label.style_label_up, color.new('#B3C9F5') if none else color.black, pvtTextSize, text.align_center, 'Pivot Low · ' + string.tostring(pvtLow, format.mintick) + TX + '\n -Price Change: ↓ %' + string.tostring((pvtHigh1 - pvtLow) * 100 / pvtHigh1, '#.##') + ('\n -Traded Volume: ' + string.tostring(tradedVolume__00000276__, format.volume) + ' (' + string.tostring(profileLength - 1) + ' bars)\n      *Average Volume/Bar: ' + string.tostring(tradedVolume__00000276__ / (profileLength - 1), format.volume) if isVoly else '') + '\n\nNumber of Bars: ' + string.tostring(profileLength))
            pvtLow1 = pvtLow
            label.delete(tempLow[1])
            if x2 - pvtLength > x2Temp - pvtLengthTemp:
                label.delete(tempHigh[1])

        if not na(pvtHighTemp):
            if pvtHighTemp > pvtHigh1Temp:
                label.delete(tempHigh[1])
                none = not pvtPrice and (not pvtChange) and (not pvtVolume or not isVoly)
                tradedVolume__0000028a__ = tradedVolume(profileLengthTemp, proceedTemp, pvtLengthTemp)
                tempHigh = label.new(bar_index[pvtLengthTemp], pvtHighTemp, ('●\n▼' if none else '●\n') + (string.tostring(pvtHighTemp, format.mintick) if pvtPrice else '') + ((' ↑ %' if pvtPrice else '↑ %') + string.tostring((pvtHighTemp - pvtLow1) * 100 / pvtLow1, '#.##') if pvtChange else '') + (('\n' if pvtPrice or pvtChange else '') + string.tostring(tradedVolume__0000028a__, format.volume) if pvtVolume and isVoly else ''), xloc.bar_index, yloc.price, noColor if none else color.new('#284AA9'), label.style_label_down, color.new('#284AA9') if none else color.new('#E0E0E0'), size.small if none else pvtTextSize, text.align_center, 'Temporary Pivot High · ' + string.tostring(pvtHighTemp, format.mintick) + '\n -Price Change: ↑ %' + string.tostring((pvtHighTemp - pvtLow1) * 100 / pvtLow1, '#.##') + ('\n -Traded Volume: ' + string.tostring(tradedVolume__0000028a__, format.volume) + ' (' + string.tostring(profileLengthTemp - 1) + ' bars)\n      *Average Volume/Bar: ' + string.tostring(tradedVolume__0000028a__ / (profileLengthTemp - 1), format.volume) if isVoly else '') + '\n\nNumber of bars since last confirmed Pivot High/Low: ' + string.tostring(profileLengthTemp) + '\n\n⚠ Provisional level\n' + 'Subject to repaint until structure confirms')

                if pvtAlert:
                    alert('Temporary Pivot High' + (' (Higher High)' if pvtHighTemp > pvtHigh1 else ' (Lower High)') + ' detected at (' + string.tostring(pvtHighTemp, format.mintick) + ')\n⚠ Caution: These alerts highlight potential market pivots but are not definitive signals. Use them as early indications of possible movement and seek further confirmation before making trading decisions. ⚠\nCurrent price · ' + string.tostring(close, format.mintick), alert.freq_once_per_bar)

            pvtHigh1Temp = pvtHighTemp

        if high > pvtHigh1Temp:
            label.delete(tempHigh[1])

        if not na(pvtLowTemp):
            if pvtLowTemp < pvtLow1Temp:
                label.delete(tempLow[1])
                tradedVolume__000002a2__ = tradedVolume(profileLengthTemp, proceedTemp, pvtLengthTemp)
                none = not pvtPrice and (not pvtChange) and (not pvtVolume or not isVoly)
                tempLow = label.new(bar_index[pvtLengthTemp], pvtLowTemp, ('▲\n●' if none else '●\n') + (string.tostring(pvtLowTemp, format.mintick) if pvtPrice else '') + ((' ↓ %' if pvtPrice else '↓ %') + string.tostring((pvtHigh1 - pvtLowTemp) * 100 / pvtLowTemp, '#.##') if pvtChange else '') + (('\n' if pvtPrice or pvtChange else '') + string.tostring(tradedVolume__000002a2__, format.volume) if pvtVolume and isVoly else ''), xloc.bar_index, yloc.price, noColor if none else color.new('#284AA9'), label.style_label_up, color.new('#284AA9') if none else color.new('#E0E0E0'), size.small if none else pvtTextSize, text.align_center, 'Temporary Pivot Low · ' + string.tostring(pvtLowTemp, format.mintick) + '\n -Price Change: ↓ %' + string.tostring((pvtHigh1 - pvtLowTemp) * 100 / pvtHigh1, '#.##') + ('\n -Traded Volume: ' + string.tostring(tradedVolume__000002a2__, format.volume) + ' (' + string.tostring(profileLengthTemp - 1) + ' bars)\n      *Average Volume/Bar: ' + string.tostring(tradedVolume__000002a2__ / (profileLengthTemp - 1), format.volume) if isVoly else '') + '\n\nNumber of bars since last confirmed Pivot High/Low: ' + string.tostring(profileLengthTemp) + '\n\n⚠ Provisional level\n' + 'Subject to repaint until structure confirms')

                if pvtAlert:
                    alert('Temporary Pivot Low' + (' (Lower Low)' if pvtLowTemp < pvtLow1 else ' (Higher Low)') + ' detected at (' + string.tostring(pvtLowTemp, format.mintick) + ')\n⚠ Caution: These alerts highlight potential market pivots but are not definitive signals. Use them as early indications of possible movement and seek further confirmation before making trading decisions. ⚠\nCurrent price · ' + string.tostring(close, format.mintick), alert.freq_once_per_bar)

            pvtLow1Temp = pvtLowTemp

        if low < pvtLow1Temp:
            label.delete(tempLow[1])

    if marketS:
        pHigh: Persistent[float] = na(float)
        iHigh: Persistent[int] = na(int)
        xHigh: Persistent[bool] = False
        pLow: Persistent[float] = na(float)
        iLow: Persistent[int] = na(int)
        xLow: Persistent[bool] = False

        bias: Persistent[int] = 0

        if not na(pvtHigh):
            pHigh = pvtHigh
            iHigh = bar_index - pvtLength
            xHigh = False

        if not na(pvtLow):
            pLow = pvtLow
            iLow = bar_index - pvtLength
            xLow = False

        if close > pHigh and (not xHigh):
            xHigh = True
            line.new(iHigh, pHigh, bar_index, pHigh, color=color.new('#089981'), style=line.style_solid if bias == -1 else line.style_dotted, width=1)
            box.new(iHigh, pHigh, bar_index, pHigh, noColor, bgcolor=noColor, text='CHoCH' if bias == -1 else 'BoS', text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_bottom, text_color=color.new(color.new('#089981'), 25))

            if msAlert:
                alert(('Bullish CHoCH Detected.\nThis suggests a market change from one structural pattern, such as a trending market, to another, like a ranging or consolidating market. It may indicate a potential trend reversal.' if bias == -1 else 'Bullish BoS Detected.\nThis indicates that price has broken through a significant level, which may signify a continuation of the current trend or a liquidity sweep. Monitor for further confirmation of this movement.') + '\nCurrent price · ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)

            bias = 1

        if close < pLow and (not xLow):
            xLow = True
            line.new(iLow, pLow, bar_index, pLow, color=color.new('#F23645'), style=line.style_solid if bias == 1 else line.style_dotted, width=1)
            box.new(iLow, pLow, bar_index, pLow, noColor, bgcolor=noColor, text='CHoCH' if bias == 1 else 'BoS', text_size=size.tiny, text_halign=text.align_left, text_valign=text.align_top, text_color=color.new(color.new('#F23645'), 25))

            if msAlert:
                alert(('Bearish CHoCH Detected.\nThis suggests a market change from one structural pattern, such as a trending market, to another, like a ranging or consolidating market. It may indicate a potential trend reversal.' if bias == 1 else 'Bearish BoS Detected.\nThis indicates that price has broken through a significant level, which may signify a continuation of the current trend or a liquidity sweep. Monitor for further confirmation of this movement.') + '\nCurrent price · ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)

            bias = -1

    def movingAverage(source, length, maType):
        __block_result_11__ = na
        __switch__ = maType
        if __switch__ == 'SMA':
            __block_result_11__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result_11__ = ta.ema(source, length)
        elif __switch__ == 'HMA':
            __block_result_11__ = ta.hma(source, length)
        elif __switch__ == 'RMA':
            __block_result_11__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result_11__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result_11__ = ta.vwma(source, length)
        return __block_result_11__

    maFast = movingAverage(maSource1, maLength1, maType1) if maDisplay else na
    maSlow = movingAverage(maSource2, maLength2, maType2) if maDisplay else na

    maColor = maColor1 if maFast > maSlow else maColor2
    ma1 = plot(maFast if maDisplay else na, 'Moving Average #1', color.new(maColor, 91), 1, plot.style_linebr, display=display__ren__, editable=False)
    ma2 = plot(maSlow if maDisplay else na, 'Moving Average #2', color.new(maColor, 81), 2, plot.style_linebr, display=display__ren__, editable=False)

    fill(ma1, ma2, math.max(maFast, maSlow), math.min(maFast, maSlow), color.new(maColor, 99 if maFast > maSlow else 81), color.new(maColor, 81 if maFast > maSlow else 99))

    if maAlert:
        if ta.cross(maFast, maSlow):
            alert(('Bullish' if maFast > maSlow else 'Bearish') + ' Moving Average Cross Detected\nThis signals potential ' + ('bullish' if maFast > maSlow else 'bearish') + ' momentum.\nCurrent price · ' + string.tostring(close, format.mintick), alert.freq_once_per_bar)

        if ta.cross(close, maSlow):
            alert('Price (' + string.tostring(close, format.mintick) + ')' + (' crossed above ' if close > maSlow else ' dropped below ') + maType2 + string.tostring(maLength2) + ' (' + string.tostring(maSlow, format.mintick) + ')', alert.freq_once_per_bar_close)

    volMa = ta.sma(nzVolume, vwcbLen)
    if volAlert and nzVolume > volMa * 4.669:
        alert('Volume SPIKE Detected.\nCurrent price · ' + string.tostring(close, format.mintick))

    isHV = nzVolume >= hThresh * volMa
    isLV = nzVolume <= lThresh * volMa

    barcolor(((color.new('#006400') if open < close else color.new('#910000')) if isHV else (color.new('#7FFFD4') if open < close else color.new('#FF9800')) if isLV else na) if vwcb and isVoly else na, title='Volume Weighted Colored Bars', editable=False)

    def sessionBegins(sess):
        t: Series = time('', sess)
        return timeframe.isintraday and (not barstate.isfirst) and na(t[1]) and (not na(t))

    def cellInfo(sessRange, utc, utcLocal):
        dateTime = string.format_time(timenow, "dd-MM-yyyy HH:mm:ss 'UTC'Z", utcLocal)

        srOH = cast_int(string.tonumber(string.substring(sessRange, 0, 2)))
        srOM = cast_int(string.tonumber(string.substring(sessRange, 2, 4)))
        srCH = cast_int(string.tonumber(string.substring(sessRange, 5, 7)))
        srCM = cast_int(string.tonumber(string.substring(sessRange, 7, 9)))

        endTime = timestamp(utc, year, month, dayofmonth, srCH, srCM, 0)
        startTime = timestamp(utc, year, month, dayofmonth, srOH, srOM, 0)

        closesIn = string.format_time(endTime - timenow, "'Closes in 'HH:mm:ss", 'Etc/UTC')
        opensIn = string.format_time(startTime - timenow, "'Opens in 'HH:mm:ss", 'Etc/UTC')

        if string.contains(closesIn, 'in 00:'):
            closesIn = ' 🟢 ' + closesIn if timenow % 2 == 0 else ' 🔴 ' + closesIn
        else:
            closesIn = ' 🟢 ' + closesIn

        if string.contains(opensIn, 'in 00:'):
            opensIn = ' 🟢 ' + opensIn if timenow % 2 == 0 else ' 🔴 ' + opensIn
        else:
            opensIn = ' 🔴 ' + opensIn

        A = dayofweek(timenow, utcLocal)

        log.info('yaz_kizim {0} {1} {2} {3}', utcLocal, string.format_time(time, "dd-MM-yyyy HH:mm:ss 'UTC'Z"), string.format_time(timestamp('Etc/UTC', year, month, dayofmonth, srCH if srOH < srCH else srCH + 24, srCM, 0), "dd-MM-yyyy HH:mm:ss 'UTC'Z"), string.format_time(time, "dd-MM-yyyy HH:mm:ss 'UTC'Z"))

        __block_result_12__ = na
        if A != 1 and A != 7:
            ltfSession = request.security_lower_tf(syminfo.tickerid, ltf, timeInRange(sessRange, utc), calc_bars_count=60)

            __block_result_13__ = na
            if method_call('size', ltfSession) > 0:
                __block_result_14__ = na
                if method_call('last', ltfSession):
                    __block_result_14__ = dateTime + closesIn
                else:
                    __block_result_15__ = na
                    if A == 6 and time >= (3600000 * 24 + timestamp('Etc/UTC', year, month, dayofmonth, srCH, srCM, 0) if srOH > srCH else timestamp('Etc/UTC', year, month, dayofmonth, srCH, srCM, 0)):
                        __block_result_15__ = dateTime + ' 🟠 Weekend'
                    else:
                        __block_result_15__ = dateTime + opensIn
                    __block_result_14__ = __block_result_15__
                __block_result_13__ = __block_result_14__
            __block_result_12__ = __block_result_13__
        else:
            __block_result_12__ = dateTime + ' 🟠 Weekend'
        return __block_result_12__

    hide = (True if syminfo.type == 'forex' or syminfo.type == 'cfd' else False) if hideIfNot else True

    if barstate.islast and tabularShow and hide and fxChartTF:
        __block_result_16__ = na
        __switch_1__ = statPos
        if __switch_1__ == 'Top Left':
            __block_result_16__ = position.top_left
        elif __switch_1__ == 'Top Center':
            __block_result_16__ = position.top_center
        elif __switch_1__ == 'Top Right':
            __block_result_16__ = position.top_right
        elif __switch_1__ == 'Middle Right':
            __block_result_16__ = position.middle_right
        elif __switch_1__ == 'Bottom Left':
            __block_result_16__ = position.bottom_left
        elif __switch_1__ == 'Bottom Center':
            __block_result_16__ = position.bottom_center
        statPosition = __block_result_16__

        clock: Table = table.new(statPosition, 3, 6, border_width=3)
        offset = string.format_time(time, "' in UTC'Z", utcOffset)

        market = cellInfo(sydneyRange, utcOffset, sydneyLocal)
        marketColor = color.new('#089981') if string.contains(market, 'Closes') else color.new('#F23645')
        table.cell(clock, 0, 1, '█', text_size=textSize2, text_color=sydneyColor)
        table.cell(clock, 1, 1, string.upper(sydneyName), text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_left, text_size=textSize2, tooltip='Session Range ' + sydneyRange + offset)
        table.cell(clock, 2, 1, market, text_color=marketColor, bgcolor=color.new(marketColor, 89), text_halign=text.align_left, text_size=textSize2)

        market = cellInfo(tokyoRange, utcOffset, tokyoLocal)
        marketColor = color.new('#089981') if string.contains(market, 'Closes') else color.new('#F23645')
        table.cell(clock, 0, 2, '█', text_size=textSize2, text_color=tokyoColor)
        table.cell(clock, 1, 2, string.upper(tokyoName), text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_left, text_size=textSize2, tooltip='Session Range ' + tokyoRange + offset)
        table.cell(clock, 2, 2, market, text_color=marketColor, bgcolor=color.new(marketColor, 89), text_halign=text.align_left, text_size=textSize2)

        market = cellInfo(frankfurtRange, utcOffset, frankfurtLocal)
        marketColor = color.new('#089981') if string.contains(market, 'Closes') else color.new('#F23645')
        table.cell(clock, 0, 3, '█', text_size=textSize2, text_color=frankfurtColor)
        table.cell(clock, 1, 3, string.upper(frankfurtName), text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_left, text_size=textSize2, tooltip='Session Range ' + frankfurtRange + offset)
        table.cell(clock, 2, 3, market, text_color=marketColor, bgcolor=color.new(marketColor, 89), text_halign=text.align_left, text_size=textSize2)

        market = cellInfo(londonRange, utcOffset, londonLocal)
        marketColor = color.new('#089981') if string.contains(market, 'Closes') else color.new('#F23645')
        table.cell(clock, 0, 4, '█', text_size=textSize2, text_color=londonColor)
        table.cell(clock, 1, 4, string.upper(londonName), text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_left, text_size=textSize2, tooltip='Session Range ' + londonRange + offset)
        table.cell(clock, 2, 4, market, text_color=marketColor, bgcolor=color.new(marketColor, 89), text_halign=text.align_left, text_size=textSize2)

        market = cellInfo(newYorkRange, utcOffset, newYorkLocal)
        marketColor = color.new('#089981') if string.contains(market, 'Closes') else color.new('#F23645')
        table.cell(clock, 0, 5, '█', text_size=textSize2, text_color=newYorkColor)
        table.cell(clock, 1, 5, string.upper(newYorkName), text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_left, text_size=textSize2, tooltip='Session Range ' + newYorkRange + offset)
        table.cell(clock, 2, 5, market, text_color=marketColor, bgcolor=color.new(marketColor, 89), text_halign=text.align_left, text_size=textSize2)

        market = 'EXCHANGE' if utcOffsetIn == 'Exchange' else string.upper(string.replace(string.substring(utcOffsetIn, string.pos(utcOffsetIn, '/') + 1), '_', ' ', 0))
        sTime = string.format_time(timenow, "dd-MM-yyyy HH:mm:ss 'UTC'Z", syminfo.timezone) if utcOffsetIn == 'Exchange' else string.format_time(timenow, "dd-MM-yyyy HH:mm:ss 'UTC'Z", utcOffsetIn)
        table.cell(clock, 2, 0, market + '\n' + sTime, text_color=color.blue, bgcolor=color.new(color.blue, 89), text_halign=text.align_center, text_size=textSize2, tooltip='Selected Timezone')

    if forexEvents and fxChartTF and (syminfo.type == 'forex'):
        meEvents: Persistent[list[str]] = array.new_string()
        meVolume: Persistent[list[float]] = array.new_float()

        if barstate.isfirst:
            array.push(meVolume, 0.7)
            array.push(meEvents, 'Lowest\nNew trading day begins · Institutional reset\n')

            array.push(meVolume, 1)
            array.push(meEvents, 'Very Low\nBooks balancing · Spread stabilization\n')

            array.push(meVolume, 1.7)
            array.push(meEvents, 'Low, slightly increasing\nEarly positioning activity\n')

            array.push(meVolume, 3.9)
            array.push(meEvents, 'Low and Increasing\nRegional participation expanding\n')

            array.push(meVolume, 2.9)
            array.push(meEvents, 'Low\nActive participation building\n')

            array.push(meVolume, 2)
            array.push(meEvents, 'Low and Decreasing\nTemporary liquidity contraction\n')

            array.push(meVolume, 1.7)
            array.push(meEvents, 'Low\nPre-expansion transition phase\n')

            array.push(meVolume, 2.0)
            array.push(meEvents, 'Low and Increasing\nEarly European flows entering\n')

            array.push(meVolume, 2.7)
            array.push(meEvents, 'Increasing\nLiquidity building\n')

            array.push(meVolume, 3.7)
            array.push(meEvents, 'Medium\nParticipation accelerating\n')

            array.push(meVolume, 4.1)
            array.push(meEvents, 'High and Increasing\nMajor liquidity expansion\n')

            array.push(meVolume, 3.6)
            array.push(meEvents, 'High\nBroad institutional activity\n')

            array.push(meVolume, 3.2)
            array.push(meEvents, 'High\nPosition adjustments before next expansion\n')

            array.push(meVolume, 2.5)
            array.push(meEvents, 'High\nSustained participation\n')

            array.push(meVolume, 3.5)
            array.push(meEvents, 'High and Increasing\nCross-region flows increasing\n')

            array.push(meVolume, 5.7)
            array.push(meEvents, 'Higher\nPeak volatility window beginning\n')

            array.push(meVolume, 7.5)
            array.push(meEvents, 'Higher\nStrong multi-region participation\n')

            array.push(meVolume, 8.5)
            array.push(meEvents, 'Highest\nMaximum institutional engagement\n')

            array.push(meVolume, 7.7)
            array.push(meEvents, 'Higher and Decreasing\nProfit-taking and rebalancing\n')

            array.push(meVolume, 5.3)
            array.push(meEvents, 'Medium and Decreasing\nDominant regional control\n')

            array.push(meVolume, 3.1)
            array.push(meEvents, 'Low and Decreasing\nActivity cooling\n')

            array.push(meVolume, 2)
            array.push(meEvents, 'Low\nNew York afternoon · Participation fading\n')

            array.push(meVolume, 1.4)
            array.push(meEvents, 'Very Low\nPre-rollover positioning · Liquidity withdrawal\n')

            array.push(meVolume, 1.1)
            array.push(meEvents, 'Lowest\nEnd-cycle positioning\n')

            array.push(meVolume, 1)
            array.push(meEvents, '\n')

        blabla: Persistent[int] = 0
        events: Persistent[Label] = na(Label)
        meLines: Persistent[list[Line]] = array.new_line()
        meLabels: Persistent[list[Label]] = array.new_label()
        meFills: Persistent[list[LineFill]] = array.new_linefill()
        a_hist: Persistent[list[Box]] = array.new_box()
        vHST: Persistent[float] = na(float)
        prL: Persistent[float] = na(float)
        prC: Persistent[float] = na(float)

        meLN = cast_int(1440 / timeframe.multiplier)
        pHST = ta.highest(high, meLN)
        pLST: Series = ta.lowest(low, meLN)
        volH = ta.highest(nzVolume, meLN)
        pCHR = (pHST - pLST) / pHST
        pLST = pLST * (1 - pCHR * oscVO)
        oHST: int = 13
        hight = pCHR / oscHight
        bullCandle = close > open

        vST = '\n\nReal-Time Activity: HIGH' if isHV else '\n\nReal-Time Activity: LOW' if isLV else '\n\nReal-Time Activity: NORMAL'

        if dayChange:
            vHST = volH
            prL = pLST
            prC = pCHR
            if array.size(meLines) > 0:
                for i in pine_range(array.size(meLines), 1):
                    line.delete(array.shift(meLines))

            if array.size(meLabels) > 0:
                for i in pine_range(array.size(meLabels), 1):
                    label.delete(array.shift(meLabels))

            if array.size(meFills) > 0:
                for i in pine_range(array.size(meFills), 1):
                    linefill.delete(array.shift(meFills))

            if array.size(a_hist) > 0:
                for i in pine_range(array.size(a_hist), 1):
                    box.delete(array.shift(a_hist))

            hourInMS = 60 * 60 * 1000

            for index in pine_range(0, 23):
                array.push(meLines, line.new(time + index * hourInMS, pLST * (1 - (oHST - array.get(meVolume, index)) * hight / oHST), time + (index + 1) * hourInMS, pLST * (1 - (oHST - array.get(meVolume, index + 1)) * hight / oHST), xloc.bar_time, extend.none, noColor, line.style_solid, 1))
                array.push(meLines, line.new(time + index * hourInMS, pLST * (1 - hight), time + (index + 1) * hourInMS, pLST * (1 - hight), xloc.bar_time, extend.none, noColor, line.style_solid, 1))

                array.push(meFills, linefill.new(array.get(meLines, 2 * index), array.get(meLines, 2 * index + 1), color.new(color.from_gradient(array.get(meVolume, index), 1, 5.7, color.new('#F23645'), color.new('#089981')), 73)))

                array.push(meLabels, label.new(time + index * hourInMS, pLST * (1 - (oHST - array.get(meVolume, index)) * hight / oHST), '', xloc.bar_time, yloc.price, noColor, label.style_circle, noColor, size.tiny, text.align_left, 'At this time of day\nTrading Volume is typically ' + array.get(meEvents, index)))
                array.push(meLabels, label.new(time + index * hourInMS, pLST * (1 - (oHST - array.get(meVolume, index)) * hight / oHST), '', xloc.bar_time, yloc.price, color.from_gradient(array.get(meVolume, index), 1, 6, color.new('#F23645'), color.new('#089981')), label.style_circle, noColor, size.auto, text.align_left, ''))

            array.push(meLabels, label.new(time + 24 * hourInMS, pLST * (1 - (oHST - array.get(meVolume, 0)) * hight / oHST), '', xloc.bar_time, yloc.price, noColor, label.style_circle, noColor, size.tiny, text.align_left, 'At this time of day\nTrading Volume is typically Lowest\nMarket reset\n'))
            array.push(meLabels, label.new(time + 24 * hourInMS, pLST * (1 - (oHST - array.get(meVolume, 0)) * hight / oHST), '', xloc.bar_time, yloc.price, color.from_gradient(array.get(meVolume, 0), 1, 6, color.new('#F23645'), color.new('#089981')), label.style_circle, noColor, size.auto, text.align_left, ''))

            if not na(events):
                label.delete(events)
            blabla = 0
            events = label.new(time, pLST * (1 - hight), '', xloc.bar_time, yloc.price, color.new(color.from_gradient(nzVolume, 0.618 * volMa, 1.618 * volMa, color.new('#F23645'), color.new('#089981')), 50), label.style_label_up, color.white, size.tiny, text.align_left, 'At this time of day\nTrading Volume is typically ' + array.get(meEvents, blabla))

        array.push(a_hist, box.new(time, prL * (1 - prC / oscHight) * (1 + nzVolume / vHST * prC / oscHight), time, prL * (1 - prC / oscHight), color.new(color.teal, 65) if bullCandle else color.new(color.red, 65), 2, xloc=xloc.bar_time, bgcolor=noColor))

        if ta.change(pLST) < 0 and (not dayChange):
            for barIndex in pine_range(0, array.size(meLines) - 1):
                line.set_y1(array.get(meLines, barIndex), line.get_y1(array.get(meLines, barIndex)) - pLST[1] + pLST)
                line.set_y2(array.get(meLines, barIndex), line.get_y2(array.get(meLines, barIndex)) - pLST[1] + pLST)

            for barIndex in pine_range(0, array.size(meLabels) - 1):
                label.set_y(array.get(meLabels, barIndex), label.get_y(array.get(meLabels, barIndex)) - pLST[1] + pLST)

            label.set_y(events, label.get_y(events) - pLST[1] + pLST)

            prL = (box.get_bottom(array.get(a_hist, 0)) - pLST[1] + pLST) / (1 - prC / oscHight)

            for barIndex in pine_range(array.size(a_hist) - 1, 0):
                box.set_top(array.get(a_hist, barIndex), box.get_top(array.get(a_hist, barIndex)) - pLST[1] + pLST)
                box.set_bottom(array.get(a_hist, barIndex), box.get_bottom(array.get(a_hist, barIndex)) - pLST[1] + pLST)

        inSydney = not na(time(timeframe.period, sydneyRange, utcOffset))
        inTokyo = not na(time(timeframe.period, tokyoRange, utcOffset))
        inFrankfurt = not na(time(timeframe.period, frankfurtRange, utcOffset))
        inLondon = not na(time(timeframe.period, londonRange, utcOffset))
        inNewYork = not na(time(timeframe.period, newYorkRange, utcOffset))

        sessTxt: str = ''

        sessTxt += '\nSydney · Active' if inSydney else ''
        sessTxt += '\nTokyo · Active' if inTokyo else ''
        sessTxt += '\nFrankfurt · Active' if inFrankfurt else ''
        sessTxt += '\nLondon · Active' if inLondon else ''
        sessTxt += '\nNew York · Active' if inNewYork else ''

        sessTxt = 'Interbank transition' if sessTxt == '' else sessTxt

        liqDesc = '\n\nPeak liquidity (London–New York overlap)' if inLondon and inNewYork else '\n\nHigh liquidity (European overlap)' if inLondon and inFrankfurt else '\n\nModerate liquidity (Asia–Europe transition)' if inTokyo and inFrankfurt else '\n\nModerate liquidity (Asia overlap)' if inTokyo and inSydney else '\n\nHigh liquidity (London session)' if inLondon else '\n\nHigh liquidity (New York session)' if inNewYork else '\n\nModerate liquidity (Frankfurt session)' if inFrankfurt else '\n\nModerate liquidity (Tokyo session)' if inTokyo else '\n\nLow liquidity (Sydney session)' if inSydney else '\n\nVery low liquidity'

        if timeframe.change('60') and (not dayChange):
            blabla = blabla + 1

        if not na(events) and blabla < array.size(meEvents):
            label.set_tooltip(events, 'At this time of day\nTrading Volume is typically ' + array.get(meEvents, blabla) + sessTxt + liqDesc + vST)
            label.set_color(events, color.new(color.from_gradient(nzVolume, 0.618 * volMa, 1.618 * volMa, color.new('#F23645'), color.new('#089981')), 50))
            label.set_x(events, time)

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)