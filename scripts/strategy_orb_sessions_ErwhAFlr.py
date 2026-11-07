"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, close, color, currency, dayofmonth,
    dayofweek, display, high, hour, input, label, line, location, low, math, minute, month, na, nz,
    plot, plotshape, position, script, shape, size, strategy, string, syminfo, table, time,
    timeframe, xloc, year
)
from pynecore.types import Label, Line, NA, Persistent, PersistentSeries, Series, Table


@udt
class orbData:
    hi: float = na(float)
    lo: float = na(float)
    mid: float = na(float)
    startBar: int = na(int)
    hiBar: int = na(int)
    loBar: int = na(int)
    endBar: int = na(int)
    startTime: int = na(int)
    hiTime: int = na(int)
    loTime: int = na(int)
    endTime: int = na(int)
    hiLine: Line = na(Line)
    loLine: Line = na(Line)
    midLine: Line = na(Line)
    hiLabel: Label = na(Label)
    loLabel: Label = na(Label)
    midLabel: Label = na(Label)


grpGlobal: str = "Global Settings"
grpAdaptive: str = "Adaptive Position Sizing"
grpAdaptTP: str = "Adaptive Take Profit"
grpFlat: str = "Prop Firm Flat Window"
grpNY: str = "Session 1: New York ORB"
grpAS: str = "Session 2: Asia ORB"
grpLN: str = "Session 3: London ORB"
grpDashColors: str = "Dashboard Colors"
grpStyle: str = "Style"
grpLines: str = "SL/TP Lines"
grpPnlDash: str = "P&L Dashboard"


@script.strategy("ADAPTIVE ORB SESSIONS ", overlay=True, initial_capital=50000, currency=currency.USD, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, commission_type=strategy.commission.cash_per_contract, commission_value=1.2, slippage=2, margin_long=1, margin_short=1, calc_on_every_tick=False, calc_on_order_fills=False, use_bar_magnifier=True, process_orders_on_close=True, backtest_fill_limits_assumption=0, fill_orders_on_standard_ohlc=False, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    i_daysToShow=input.int(10, "Days to Show", minval=1, maxval=50, group=grpGlobal, tooltip="Number of historical days of ORB levels, SL/TP lines, and trade events to display on the chart."),
    i_timezone=input.string("America/Los_Angeles", "Timezone", options=("America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London", "Asia/Tokyo", "Asia/Hong_Kong", "Asia/Singapore", "Australia/Sydney", "UTC"), tooltip="All session times are interpreted in this timezone.", group=grpGlobal),
    i_adaptEnable=input.bool(True, "Enable Adaptive Sizing", group=grpAdaptive, tooltip="When enabled, contract size is calculated dynamically based on ORB range and your max dollar risk per trade. When disabled, uses the fixed Contracts input per session."),
    i_adaptMaxRisk=input.float(500.0, "Max Dollar Risk Per Trade", minval=10.0, step=10.0, group=grpAdaptive, tooltip="Maximum dollar amount you are willing to risk on a single trade. The engine calculates contracts so that (contracts × risk-per-contract) stays at or below this value."),
    i_adaptMaxQty=input.int(9, "Max Contracts", minval=1, maxval=50, group=grpAdaptive, tooltip="Upper limit on contracts regardless of how small the ORB range is."),
    i_adaptMinQty=input.int(1, "Min Contracts", minval=1, maxval=10, group=grpAdaptive, tooltip="Lower limit on contracts. The engine will always trade at least this many, even if the range exceeds your risk budget."),
    i_adaptTPEnable=input.bool(True, "Enable Adaptive TP", group=grpAdaptTP, tooltip="When enabled, TP R:R multipliers scale based on the current ORB range vs the rolling average range for that session. Wider-than-average range = tighter TPs. Narrower-than-average = wider TPs."),
    i_adaptTPLookback=input.int(20, "Lookback Sessions", minval=3, maxval=100, group=grpAdaptTP, tooltip="Number of recent completed ORBs to average for the baseline. Each session (NY/AS/LDN) tracks its own rolling average independently."),
    i_adaptTPMin=input.float(0.4, "TP Compression Min", minval=0.1, maxval=1.0, step=0.05, group=grpAdaptTP, tooltip="Minimum TP multiplier when range is much wider than average. 0.4 means TPs compress to 40% of their set R:R."),
    i_adaptTPMax=input.float(1.8, "TP Stretch Max", minval=1.0, maxval=5.0, step=0.1, group=grpAdaptTP, tooltip="Maximum TP multiplier when range is much tighter than average. 1.8 means TPs stretch to 180% of their set R:R."),
    i_flatWindowEnable=input.bool(False, "Enable Flat Window", tooltip="Flatten all positions and block new entries during this time window.", group=grpFlat),
    i_flatWindowStart=input.string("1300", "Flat Start (HHMM)", group=grpFlat, inline="flat", tooltip="Start of the flat window."),
    i_flatWindowEnd=input.string("1500", "Flat End (HHMM)", group=grpFlat, inline="flat", tooltip="End of the flat window."),
    i_nyEnable=input.bool(True, "Enable NY Session", group=grpNY, tooltip="Enable trading during the New York session."),
    i_nyContracts=input.int(3, "Contracts", minval=1, maxval=100, group=grpNY, tooltip="Contracts per trade entry."),
    i_nyDirection=input.string("Both", "Direction", options=("Long Only", "Short Only", "Both"), group=grpNY, tooltip="Only take long, short, or both directions for NY session entries."),
    i_nyORBStart=input.string("0630", "ORB Start (HHMM)", group=grpNY, tooltip="Time the Opening Range begins building (24h format, in your selected timezone)."),
    i_nyORBDur=input.string("15 Min", "ORB Duration", options=("5 Min", "15 Min", "30 Min", "1 Hour", "Custom"), group=grpNY, tooltip="How long the Opening Range builds before completing. Candles during this window define the high/low of the ORB."),
    i_nyORBEnd=input.string("0645", "ORB Custom End (HHMM)", tooltip="Only used when Duration = Custom", group=grpNY, display=display.none),
    i_nySessEnd=input.string("1300", "Session End (HHMM)", tooltip="Go flat and reset at this time.", group=grpNY),
    i_nyFlattenEOD=input.bool(True, "Flatten at Session End", group=grpNY, tooltip="Force close all positions when this session ends using a hard market order (EOS)."),
    i_nyEntryMode=input.string("Breakout", "Entry Mode", options=("Breakout", "Retest Zone", "Retest Midpoint"), group=grpNY, tooltip="Breakout: enter on candle close through level.\\nRetest Zone: wait for wick back to broken level.\\nRetest Midpoint: wait for wick back to ORB midpoint."),
    i_nyEntryBuffer=input.int(0, "Entry Buffer (ticks)", minval=0, maxval=50, group=grpNY, tooltip="Ticks beyond ORB level for entry trigger."),
    i_nyRetestTimeout=input.int(20, "Retest Timeout (bars)", minval=3, maxval=100, group=grpNY, display=display.none, tooltip="Bars to wait for retest before signal expires."),
    i_nySLMethod=input.string("Opposite Side", "Stop Loss", options=("Midpoint", "Opposite Side", "Fixed Points"), group=grpNY, tooltip="Where to place the stop loss. Midpoint = ORB mid. Opposite Side = other ORB boundary. Fixed Points = custom distance."),
    i_nySLPoints=input.float(20.0, "SL Fixed Points", minval=0.25, step=0.25, group=grpNY, display=display.none, tooltip="Distance in points for stop loss when using Fixed Points mode."),
    i_nyTP1RR=input.float(1.0, "TP1 R:R", minval=0.1, step=0.1, group=grpNY, inline="nytp1", tooltip="Take Profit 1 as a multiple of the risk (distance to stop loss)."),
    i_nyTP1Qty=input.int(1, "Qty", minval=1, maxval=100, group=grpNY, inline="nytp1", tooltip="Contracts to exit at TP1."),
    i_nyTP2RR=input.float(2.0, "TP2 R:R", minval=0.1, step=0.1, group=grpNY, inline="nytp2", tooltip="Take Profit 2 as a multiple of the risk. Set Qty to 0 to disable."),
    i_nyTP2Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpNY, inline="nytp2", tooltip="Contracts to exit at TP2. 0 = disabled, remainder goes to TP3."),
    i_nyTP3RR=input.float(3.0, "TP3 R:R", minval=0.1, step=0.1, group=grpNY, inline="nytp3", tooltip="Take Profit 3 as a multiple of the risk. Set Qty to 0 to disable."),
    i_nyTP3Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpNY, inline="nytp3", tooltip="Contracts to exit at TP3. 0 = auto-assign remaining contracts."),
    i_nyTrailEnable=input.bool(True, "Enable Staircase Stop", group=grpNY, tooltip="Staircase SL: TP1->entry, TP2->TP1, TP3->TP2."),
    i_nyTrailShowLine=input.bool(True, "Show Staircase Line", group=grpNY, display=display.none, tooltip="Display staircase stop line on chart."),
    i_nyRearmEnable=input.bool(False, "Enable Re-Arm", group=grpNY, tooltip="Re-arm for new entries after trade closes."),
    i_nyRearmMaxTrades=input.int(2, "Max Trades", minval=1, maxval=20, group=grpNY, display=display.none, tooltip="Max entries per session including re-arms."),
    i_nyRearmAfter=input.string("SL Only", "Re-Arm After", options=("SL Only", "TP Only", "Both"), group=grpNY, display=display.none, tooltip="Which exits allow re-arming."),
    i_nyRearmDirection=input.string("Both Directions", "Re-Arm Direction", options=("Same Direction", "Opposite Direction", "Both Directions"), group=grpNY, display=display.none, tooltip="Direction filter for re-arm entries."),
    i_nyRearmGate=input.string("Inside ORB", "Re-Arm Gate", options=("Immediate", "Inside ORB", "Touch Midpoint", "Touch Opposite Side"), group=grpNY, display=display.none, tooltip="Price gate for re-arm."),
    i_nyRearmCooldown=input.int(0, "Cooldown Bars", minval=0, maxval=50, group=grpNY, display=display.none, tooltip="Bars to wait after trade closes before re-arm."),
    i_nyRearmBars=input.int(0, "Bars Inside ORB", minval=0, maxval=50, group=grpNY, display=display.none, tooltip="Bars with close inside ORB before re-arming."),
    i_nySun=input.bool(False, "Sun", group=grpNY, inline="nydays0", tooltip="Allow NY trades on Sunday."),
    i_nyMon=input.bool(True, "Mon", group=grpNY, inline="nydays0", tooltip="Allow NY trades on Monday."),
    i_nyTue=input.bool(False, "Tue", group=grpNY, inline="nydays0", tooltip="Allow NY trades on Tuesday."),
    i_nyWed=input.bool(True, "Wed", group=grpNY, inline="nydays1", tooltip="Allow NY trades on Wednesday."),
    i_nyThu=input.bool(True, "Thu", group=grpNY, inline="nydays1", tooltip="Allow NY trades on Thursday."),
    i_nyFri=input.bool(True, "Fri", group=grpNY, inline="nydays1", tooltip="Allow NY trades on Friday."),
    i_nySat=input.bool(False, "Sat", group=grpNY, inline="nydays2", tooltip="Allow NY trades on Saturday."),
    i_nyHighColor=input.color(color.new(color.new('#9900FF'), 0), "High Color", group=grpNY, display=display.none, tooltip="Color of the ORB high boundary line."),
    i_nyLowColor=input.color(color.new(color.new('#9900FF'), 0), "Low Color", group=grpNY, display=display.none, tooltip="Color of the ORB low boundary line."),
    i_nyMidColor=input.color(color.new(color.new('#9900FF'), 50), "Midline Color", group=grpNY, display=display.none, tooltip="Color of the ORB midline."),
    i_nyLineWidth=input.int(3, "Line Thickness", minval=1, maxval=5, group=grpNY, display=display.none, tooltip="Width of the ORB boundary lines."),
    i_nyShowMid=input.bool(True, "Show Midline", group=grpNY, display=display.none, tooltip="Display the midpoint line between ORB high and low."),
    i_nyShowEntry=input.bool(True, "Show Entry Arrows", group=grpNY, display=display.none, tooltip="Display entry signal arrows."),
    i_nyShowSLTP=input.bool(True, "Show SL/TP Lines", group=grpNY, display=display.none, tooltip="Display SL/TP lines on chart."),
    i_nyPDColor=input.color(color.new(color.new('#9900FF'), 0), "Prev Day H/L Color", group=grpNY, display=display.none, tooltip="Color for previous day session high/low lines."),
    i_nyPDStyle=input.string("Dashed", "Prev Day Line Style", options=("Solid", "Dashed", "Dotted"), group=grpNY, display=display.none, tooltip="Line style for previous day session high/low lines."),
    i_nyPDWidth=input.int(1, "Prev Day Line Width", minval=1, maxval=5, group=grpNY, display=display.none, tooltip="Thickness of previous day session high/low lines."),
    i_nyShowPD=input.bool(True, "Show Prev Day H/L", group=grpNY, display=display.none, tooltip="Display previous day session high and low levels."),
    i_asEnable=input.bool(True, "Enable Asia Session", group=grpAS, tooltip="Enable trading during the Asia session."),
    i_asContracts=input.int(3, "Contracts", minval=1, maxval=100, group=grpAS, tooltip="Contracts per trade entry."),
    i_asDirection=input.string("Both", "Direction", options=("Long Only", "Short Only", "Both"), group=grpAS, tooltip="Only take long, short, or both directions for Asia session entries."),
    i_asORBStart=input.string("1500", "ORB Start (HHMM)", group=grpAS, tooltip="Time the Opening Range begins building (24h format, in your selected timezone)."),
    i_asORBDur=input.string("15 Min", "ORB Duration", options=("5 Min", "15 Min", "30 Min", "1 Hour", "Custom"), group=grpAS, tooltip="How long the Opening Range builds before completing. Candles during this window define the high/low of the ORB."),
    i_asORBEnd=input.string("1515", "ORB Custom End (HHMM)", tooltip="Only used when Duration = Custom", group=grpAS, display=display.none),
    i_asSessEnd=input.string("0000", "Session End (HHMM)", tooltip="Go flat and reset at this time.", group=grpAS),
    i_asFlattenEOD=input.bool(True, "Flatten at Session End", group=grpAS, tooltip="Force close all positions when this session ends using a hard market order (EOS)."),
    i_asEntryMode=input.string("Breakout", "Entry Mode", options=("Breakout", "Retest Zone", "Retest Midpoint"), group=grpAS, tooltip="Breakout: enter on candle close through level.\\nRetest Zone: wait for wick back to broken level.\\nRetest Midpoint: wait for wick back to ORB midpoint."),
    i_asEntryBuffer=input.int(0, "Entry Buffer (ticks)", minval=0, maxval=50, group=grpAS, tooltip="Ticks beyond ORB level for entry trigger."),
    i_asRetestTimeout=input.int(20, "Retest Timeout (bars)", minval=3, maxval=100, group=grpAS, display=display.none, tooltip="Bars to wait for retest before signal expires."),
    i_asSLMethod=input.string("Opposite Side", "Stop Loss", options=("Midpoint", "Opposite Side", "Fixed Points"), group=grpAS, tooltip="Where to place the stop loss. Midpoint = ORB mid. Opposite Side = other ORB boundary. Fixed Points = custom distance."),
    i_asSLPoints=input.float(20.0, "SL Fixed Points", minval=0.25, step=0.25, group=grpAS, display=display.none, tooltip="Distance in points for stop loss when using Fixed Points mode."),
    i_asTP1RR=input.float(0.5, "TP1 R:R", minval=0.1, step=0.1, group=grpAS, inline="astp1", tooltip="Take Profit 1 as a multiple of the risk (distance to stop loss)."),
    i_asTP1Qty=input.int(1, "Qty", minval=1, maxval=100, group=grpAS, inline="astp1", tooltip="Contracts to exit at TP1."),
    i_asTP2RR=input.float(1.0, "TP2 R:R", minval=0.1, step=0.1, group=grpAS, inline="astp2", tooltip="Take Profit 2 as a multiple of the risk. Set Qty to 0 to disable."),
    i_asTP2Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpAS, inline="astp2", tooltip="Contracts to exit at TP2. 0 = disabled, remainder goes to TP3."),
    i_asTP3RR=input.float(1.5, "TP3 R:R", minval=0.1, step=0.1, group=grpAS, inline="astp3", tooltip="Take Profit 3 as a multiple of the risk. Set Qty to 0 to disable."),
    i_asTP3Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpAS, inline="astp3", tooltip="Contracts to exit at TP3. 0 = auto-assign remaining contracts."),
    i_asTrailEnable=input.bool(True, "Enable Staircase Stop", group=grpAS, tooltip="Staircase SL: TP1->entry, TP2->TP1, TP3->TP2."),
    i_asTrailShowLine=input.bool(True, "Show Staircase Line", group=grpAS, display=display.none, tooltip="Display staircase stop line on chart."),
    i_asRearmEnable=input.bool(False, "Enable Re-Arm", group=grpAS, tooltip="Re-arm for new entries after trade closes."),
    i_asRearmMaxTrades=input.int(2, "Max Trades", minval=1, maxval=20, group=grpAS, display=display.none, tooltip="Max entries per session including re-arms."),
    i_asRearmAfter=input.string("SL Only", "Re-Arm After", options=("SL Only", "TP Only", "Both"), group=grpAS, display=display.none, tooltip="Which exits allow re-arming."),
    i_asRearmDirection=input.string("Both Directions", "Re-Arm Direction", options=("Same Direction", "Opposite Direction", "Both Directions"), group=grpAS, display=display.none, tooltip="Direction filter for re-arm entries."),
    i_asRearmGate=input.string("Inside ORB", "Re-Arm Gate", options=("Immediate", "Inside ORB", "Touch Midpoint", "Touch Opposite Side"), group=grpAS, display=display.none, tooltip="Price gate for re-arm."),
    i_asRearmCooldown=input.int(0, "Cooldown Bars", minval=0, maxval=50, group=grpAS, display=display.none, tooltip="Bars to wait after trade closes before re-arm."),
    i_asRearmBars=input.int(0, "Bars Inside ORB", minval=0, maxval=50, group=grpAS, display=display.none, tooltip="Bars with close inside ORB before re-arming."),
    i_asSun=input.bool(True, "Sun", group=grpAS, inline="asdays0", tooltip="Allow Asia trades on Sunday."),
    i_asMon=input.bool(False, "Mon", group=grpAS, inline="asdays0", tooltip="Allow Asia trades on Monday."),
    i_asTue=input.bool(False, "Tue", group=grpAS, inline="asdays0", tooltip="Allow Asia trades on Tuesday."),
    i_asWed=input.bool(False, "Wed", group=grpAS, inline="asdays1", tooltip="Allow Asia trades on Wednesday."),
    i_asThu=input.bool(True, "Thu", group=grpAS, inline="asdays1", tooltip="Allow Asia trades on Thursday."),
    i_asFri=input.bool(False, "Fri", group=grpAS, inline="asdays1", tooltip="Allow Asia trades on Friday."),
    i_asSat=input.bool(False, "Sat", group=grpAS, inline="asdays2", tooltip="Allow Asia trades on Saturday."),
    i_asHighColor=input.color(color.new(color.new('#CC0000'), 0), "High Color", group=grpAS, display=display.none, tooltip="Color of the ORB high boundary line."),
    i_asLowColor=input.color(color.new(color.new('#CC0000'), 0), "Low Color", group=grpAS, display=display.none, tooltip="Color of the ORB low boundary line."),
    i_asMidColor=input.color(color.new(color.new('#CC0000'), 50), "Midline Color", group=grpAS, display=display.none, tooltip="Color of the ORB midline."),
    i_asLineWidth=input.int(3, "Line Thickness", minval=1, maxval=5, group=grpAS, display=display.none, tooltip="Width of the ORB boundary lines."),
    i_asShowMid=input.bool(True, "Show Midline", group=grpAS, display=display.none, tooltip="Display the midpoint line between ORB high and low."),
    i_asShowEntry=input.bool(True, "Show Entry Arrows", group=grpAS, display=display.none, tooltip="Display entry signal arrows."),
    i_asShowSLTP=input.bool(True, "Show SL/TP Lines", group=grpAS, display=display.none, tooltip="Display SL/TP lines on chart."),
    i_asPDColor=input.color(color.new(color.new('#CC0000'), 0), "Prev Day H/L Color", group=grpAS, display=display.none, tooltip="Color for previous day session high/low lines."),
    i_asPDStyle=input.string("Dashed", "Prev Day Line Style", options=("Solid", "Dashed", "Dotted"), group=grpAS, display=display.none, tooltip="Line style for previous day session high/low lines."),
    i_asPDWidth=input.int(1, "Prev Day Line Width", minval=1, maxval=5, group=grpAS, display=display.none, tooltip="Thickness of previous day session high/low lines."),
    i_asShowPD=input.bool(True, "Show Prev Day H/L", group=grpAS, display=display.none, tooltip="Display previous day session high and low levels."),
    i_lnEnable=input.bool(True, "Enable London Session", group=grpLN, tooltip="Enable trading during the London session."),
    i_lnContracts=input.int(3, "Contracts", minval=1, maxval=100, group=grpLN, tooltip="Contracts per trade entry."),
    i_lnDirection=input.string("Short Only", "Direction", options=("Long Only", "Short Only", "Both"), group=grpLN, tooltip="Only take long, short, or both directions for London session entries."),
    i_lnORBStart=input.string("0000", "ORB Start (HHMM)", group=grpLN, tooltip="Time the Opening Range begins building (24h format, in your selected timezone)."),
    i_lnORBDur=input.string("15 Min", "ORB Duration", options=("5 Min", "15 Min", "30 Min", "1 Hour", "Custom"), group=grpLN, tooltip="How long the Opening Range builds before completing. Candles during this window define the high/low of the ORB."),
    i_lnORBEnd=input.string("0015", "ORB Custom End (HHMM)", tooltip="Only used when Duration = Custom", group=grpLN, display=display.none),
    i_lnSessEnd=input.string("0630", "Session End (HHMM)", tooltip="Go flat and reset at this time.", group=grpLN),
    i_lnFlattenEOD=input.bool(True, "Flatten at Session End", group=grpLN, tooltip="Force close all positions when this session ends using a hard market order (EOS)."),
    i_lnEntryMode=input.string("Breakout", "Entry Mode", options=("Breakout", "Retest Zone", "Retest Midpoint"), group=grpLN, tooltip="Breakout: enter on candle close through level.\\nRetest Zone: wait for wick back to broken level.\\nRetest Midpoint: wait for wick back to ORB midpoint."),
    i_lnEntryBuffer=input.int(0, "Entry Buffer (ticks)", minval=0, maxval=50, group=grpLN, tooltip="Ticks beyond ORB level for entry trigger."),
    i_lnRetestTimeout=input.int(20, "Retest Timeout (bars)", minval=3, maxval=100, group=grpLN, display=display.none, tooltip="Bars to wait for retest before signal expires."),
    i_lnSLMethod=input.string("Opposite Side", "Stop Loss", options=("Midpoint", "Opposite Side", "Fixed Points"), group=grpLN, tooltip="Where to place the stop loss. Midpoint = ORB mid. Opposite Side = other ORB boundary. Fixed Points = custom distance."),
    i_lnSLPoints=input.float(20.0, "SL Fixed Points", minval=0.25, step=0.25, group=grpLN, display=display.none, tooltip="Distance in points for stop loss when using Fixed Points mode."),
    i_lnTP1RR=input.float(0.5, "TP1 R:R", minval=0.1, step=0.1, group=grpLN, inline="lntp1", tooltip="Take Profit 1 as a multiple of the risk (distance to stop loss)."),
    i_lnTP1Qty=input.int(1, "Qty", minval=1, maxval=100, group=grpLN, inline="lntp1", tooltip="Contracts to exit at TP1."),
    i_lnTP2RR=input.float(1.0, "TP2 R:R", minval=0.1, step=0.1, group=grpLN, inline="lntp2", tooltip="Take Profit 2 as a multiple of the risk. Set Qty to 0 to disable."),
    i_lnTP2Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpLN, inline="lntp2", tooltip="Contracts to exit at TP2. 0 = disabled, remainder goes to TP3."),
    i_lnTP3RR=input.float(1.5, "TP3 R:R", minval=0.1, step=0.1, group=grpLN, inline="lntp3", tooltip="Take Profit 3 as a multiple of the risk. Set Qty to 0 to disable."),
    i_lnTP3Qty=input.int(1, "Qty", minval=0, maxval=100, group=grpLN, inline="lntp3", tooltip="Contracts to exit at TP3. 0 = auto-assign remaining contracts."),
    i_lnTrailEnable=input.bool(True, "Enable Staircase Stop", group=grpLN, tooltip="Staircase SL: TP1->entry, TP2->TP1, TP3->TP2."),
    i_lnTrailShowLine=input.bool(True, "Show Staircase Line", group=grpLN, display=display.none, tooltip="Display staircase stop line on chart."),
    i_lnRearmEnable=input.bool(False, "Enable Re-Arm", group=grpLN, tooltip="Re-arm for new entries after trade closes."),
    i_lnRearmMaxTrades=input.int(3, "Max Trades", minval=1, maxval=20, group=grpLN, display=display.none, tooltip="Max entries per session including re-arms."),
    i_lnRearmAfter=input.string("SL Only", "Re-Arm After", options=("SL Only", "TP Only", "Both"), group=grpLN, display=display.none, tooltip="Which exits allow re-arming."),
    i_lnRearmDirection=input.string("Both Directions", "Re-Arm Direction", options=("Same Direction", "Opposite Direction", "Both Directions"), group=grpLN, display=display.none, tooltip="Direction filter for re-arm entries."),
    i_lnRearmGate=input.string("Inside ORB", "Re-Arm Gate", options=("Immediate", "Inside ORB", "Touch Midpoint", "Touch Opposite Side"), group=grpLN, display=display.none, tooltip="Price gate for re-arm."),
    i_lnRearmCooldown=input.int(0, "Cooldown Bars", minval=0, maxval=50, group=grpLN, display=display.none, tooltip="Bars to wait after trade closes before re-arm."),
    i_lnRearmBars=input.int(0, "Bars Inside ORB", minval=0, maxval=50, group=grpLN, display=display.none, tooltip="Bars with close inside ORB before re-arming."),
    i_lnSun=input.bool(False, "Sun", group=grpLN, inline="lndays0", tooltip="Allow London trades on Sunday."),
    i_lnMon=input.bool(True, "Mon", group=grpLN, inline="lndays0", tooltip="Allow London trades on Monday."),
    i_lnTue=input.bool(False, "Tue", group=grpLN, inline="lndays0", tooltip="Allow London trades on Tuesday."),
    i_lnWed=input.bool(False, "Wed", group=grpLN, inline="lndays1", tooltip="Allow London trades on Wednesday."),
    i_lnThu=input.bool(True, "Thu", group=grpLN, inline="lndays1", tooltip="Allow London trades on Thursday."),
    i_lnFri=input.bool(True, "Fri", group=grpLN, inline="lndays1", tooltip="Allow London trades on Friday."),
    i_lnSat=input.bool(False, "Sat", group=grpLN, inline="lndays2", tooltip="Allow London trades on Saturday."),
    i_lnHighColor=input.color(color.new(color.new('#FF6600'), 0), "High Color", group=grpLN, display=display.none, tooltip="Color of the ORB high boundary line."),
    i_lnLowColor=input.color(color.new(color.new('#FF6600'), 0), "Low Color", group=grpLN, display=display.none, tooltip="Color of the ORB low boundary line."),
    i_lnMidColor=input.color(color.new(color.new('#FF6600'), 50), "Midline Color", group=grpLN, display=display.none, tooltip="Color of the ORB midline."),
    i_lnLineWidth=input.int(3, "Line Thickness", minval=1, maxval=5, group=grpLN, display=display.none, tooltip="Width of the ORB boundary lines."),
    i_lnShowMid=input.bool(True, "Show Midline", group=grpLN, display=display.none, tooltip="Display the midpoint line between ORB high and low."),
    i_lnShowEntry=input.bool(True, "Show Entry Arrows", group=grpLN, display=display.none, tooltip="Display entry signal arrows."),
    i_lnShowSLTP=input.bool(True, "Show SL/TP Lines", group=grpLN, display=display.none, tooltip="Display SL/TP lines on chart."),
    i_lnPDColor=input.color(color.new(color.new('#FF6600'), 0), "Prev Day H/L Color", group=grpLN, display=display.none, tooltip="Color for previous day session high/low lines."),
    i_lnPDStyle=input.string("Dashed", "Prev Day Line Style", options=("Solid", "Dashed", "Dotted"), group=grpLN, display=display.none, tooltip="Line style for previous day session high/low lines."),
    i_lnPDWidth=input.int(1, "Prev Day Line Width", minval=1, maxval=5, group=grpLN, display=display.none, tooltip="Thickness of previous day session high/low lines."),
    i_lnShowPD=input.bool(True, "Show Prev Day H/L", group=grpLN, display=display.none, tooltip="Display previous day session high and low levels."),
    dashBgColor=input.color(color.new(color.new('#0D1117'), 10), "Background", group=grpDashColors, display=display.none, tooltip="Dashboard background color."),
    dashBorderColor=input.color(color.new(color.gray, 70), "Border", group=grpDashColors, display=display.none, tooltip="Dashboard border color."),
    dashHeaderBg=input.color(color.new(color.new('#2962FF'), 70), "Header Background", group=grpDashColors, display=display.none, tooltip="Dashboard header row background color."),
    dashHeaderText=input.color(color.white, "Header Text", group=grpDashColors, display=display.none, tooltip="Dashboard header text color."),
    dashLabelColor=input.color(color.gray, "Labels", group=grpDashColors, display=display.none, tooltip="Dashboard label text color."),
    dashBullColor=input.color(color.green, "Bullish", group=grpDashColors, display=display.none, tooltip="Color for bullish values in the dashboard."),
    dashBearColor=input.color(color.red, "Bearish", group=grpDashColors, display=display.none, tooltip="Color for bearish values in the dashboard."),
    lineStyle=input.string("Solid", "Line Style", options=("Solid", "Dashed", "Dotted"), group=grpStyle, display=display.none, tooltip="Style for SL/TP lines (Solid, Dashed, or Dotted)."),
    showLabels=input.bool(True, "Show Labels", group=grpStyle, display=display.none, tooltip="Display text labels on SL/TP lines."),
    labelSize=input.string("Tiny", "Label Size", options=("Tiny", "Small", "Normal"), group=grpStyle, display=display.none, tooltip="Size of the SL/TP labels."),
    i_slLineColor=input.color(color.red, "SL Color", group=grpLines, inline="sl", tooltip="Color of the stop loss line."),
    i_slLineStyle=input.string("Dashed", "Style", options=("Solid", "Dashed", "Dotted"), group=grpLines, inline="sl", tooltip="Line style (Solid, Dashed, or Dotted)."),
    i_slLineWidth=input.int(1, "Width", minval=1, maxval=5, group=grpLines, inline="sl", tooltip="Line width in pixels."),
    i_tpLineColor=input.color(color.lime, "TP Color", group=grpLines, inline="tp", tooltip="Color of the take profit lines."),
    i_tpLineStyle=input.string("Dashed", "Style", options=("Solid", "Dashed", "Dotted"), group=grpLines, inline="tp", tooltip="Line style (Solid, Dashed, or Dotted)."),
    i_tpLineWidth=input.int(2, "Width", minval=1, maxval=5, group=grpLines, inline="tp", tooltip="Line width in pixels."),
    i_trailColor=input.color(color.yellow, "Trail Color", group=grpLines, inline="trail", tooltip="Color of the staircase trailing stop line."),
    i_trailStyle=input.string("Dotted", "Style", options=("Solid", "Dashed", "Dotted"), group=grpLines, inline="trail", tooltip="Line style for the trailing stop."),
    i_trailWidth=input.int(2, "Width", minval=1, maxval=5, group=grpLines, inline="trail", tooltip="Line width for the trailing stop."),
    showPnlDash=input.bool(True, "Show P&L Dashboard", group=grpPnlDash, tooltip="Display the session P&L dashboard on the chart."),
    pnlDashPosition=input.string("Bottom Right", "P&L Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=grpPnlDash, display=display.none, tooltip="Corner of the chart to place the P&L dashboard."),
    pnlDashMode=input.string("Today", "P&L Mode", options=("Today", "All Time"), group=grpPnlDash, display=display.none, tooltip="Today: reset each trading day. All Time: cumulative since strategy start.")
):
    def f_dayKey(_t, _tz):
        return year(_t, _tz) * 10000 + month(_t, _tz) * 100 + dayofmonth(_t, _tz)


    def f_adaptiveQty(_riskDistance, _fallbackQty):
        __block_result__ = na
        if not i_adaptEnable or _riskDistance <= 0:
            __block_result__ = cast_int(math.max(1, _fallbackQty))
        else:
            _riskPerContract: float = _riskDistance * syminfo.pointvalue
            _rawQty: int = cast_int(math.floor(i_adaptMaxRisk / _riskPerContract))
            __block_result__ = cast_int(math.max(i_adaptMinQty, math.min(i_adaptMaxQty, _rawQty)))
        return __block_result__

    def f_adaptiveTpSplit(_totalQty, _tp2RR, _tp3RR, _tp2Enabled, _tp3Enabled):
        total: int = cast_int(math.max(1, _totalQty))
        use2: bool = _tp2Enabled and _tp2RR > 0
        use3: bool = _tp3Enabled and _tp3RR > 0
        activeTPs: int = 1 + (1 if use2 else 0) + (1 if use3 else 0)
        base: int = cast_int(math.floor(total / activeTPs))
        rem: int = total - base * activeTPs
        q1: int = base + (1 if rem > 0 else 0)
        q2: int = base + (1 if rem > 1 else 0) if use2 else 0
        q3: int = base + (1 if rem > 2 else 0) if use3 else 0

        if q1 + q2 + q3 != total:
            q1 = total - q2 - q3
        return (q1, q2, q3)


    nyRangeHistory: Persistent[list[float]] = array.new_float(0)
    asRangeHistory: Persistent[list[float]] = array.new_float(0)
    lnRangeHistory: Persistent[list[float]] = array.new_float(0)
    nyRangeAvg: Persistent[float] = 0.0
    asRangeAvg: Persistent[float] = 0.0
    lnRangeAvg: Persistent[float] = 0.0

    def f_updateRangeAvg(_arr, _newRange, _lookback):
        if _newRange > 0:
            array.push(_arr, _newRange)
            if array.size(_arr) > _lookback:
                array.shift(_arr)
        _avg: float = 0.0
        if array.size(_arr) > 0:
            _sum: float = 0.0
            for i in pine_range(0, array.size(_arr) - 1):
                _sum += array.get(_arr, i)
            _avg = _sum / array.size(_arr)
        return _avg

    def f_adaptTPFactor(_orbRange, _avgRange):
        __block_result_1__ = na
        if not i_adaptTPEnable or _orbRange <= 0 or _avgRange <= 0:
            __block_result_1__ = 1.0
        else:
            _ratio: float = _orbRange / _avgRange
            _rawFactor: float = 1.0 / _ratio
            __block_result_1__ = math.max(i_adaptTPMin, math.min(i_adaptTPMax, _rawFactor))
        return __block_result_1__

    def f_adaptTP(_baseRR, _orbRange, _avgRange):
        _factor: float = f_adaptTPFactor(_orbRange, _avgRange)
        return _baseRR * _factor

    def f_tpQty(_total, _p1, _p2, _p3):
        total: int = math.max(0, cast_int(math.round(_total)))
        p1: float = math.max(0.0, _p1)
        p2: float = math.max(0.0, _p2)
        p3: float = math.max(0.0, _p3)
        a1: bool = p1 > 0
        a2: bool = p2 > 0
        a3: bool = p3 > 0
        active: int = (1 if a1 else 0) + (1 if a2 else 0) + (1 if a3 else 0)
        __block_result_2__ = (na, na, na)
        if total == 0:
            __block_result_2__ = (0, 0, 0)
        elif active == 0:
            __block_result_2__ = (total, 0, 0)
        else:
            q1: int = cast_int(math.floor(total * (p1 / 100.0))) if a1 else 0
            q2: int = cast_int(math.floor(total * (p2 / 100.0))) if a2 else 0
            q3: int = cast_int(math.floor(total * (p3 / 100.0))) if a3 else 0

            if total >= active:
                if a1 and q1 == 0:
                    q1 = 1
                if a2 and q2 == 0:
                    q2 = 1
                if a3 and q3 == 0:
                    q3 = 1
            else:
                q1 = 1 if a1 else 0
                q2 = 0
                q3 = 0
                if q1 == 0 and a2:
                    q2 = 1
                if q1 == 0 and q2 == 0 and a3:
                    q3 = 1

            sumQ: int = q1 + q2 + q3

            while sumQ > total:
                if q3 > 0:
                    q3 -= 1
                elif q2 > 0:
                    q2 -= 1
                elif q1 > 0:
                    q1 -= 1
                sumQ = q1 + q2 + q3

            rem: int = total - sumQ
            while rem > 0:
                if a1:
                    q1 += 1
                    rem -= 1
                if rem > 0 and a2:
                    q2 += 1
                    rem -= 1
                if rem > 0 and a3:
                    q3 += 1
                    rem -= 1

            __block_result_2__ = (q1, q2, q3)
        return __block_result_2__


    def f_dayAllowed(_sun, _mon, _tue, _wed, _thu, _fri, _sat):
        dow: int = dayofweek(time, i_timezone)
        return _sun if dow == dayofweek.sunday else _mon if dow == dayofweek.monday else _tue if dow == dayofweek.tuesday else _wed if dow == dayofweek.wednesday else _thu if dow == dayofweek.thursday else _fri if dow == dayofweek.friday else _sat if dow == dayofweek.saturday else False

    _flatStartH = math.floor(string.tonumber(i_flatWindowStart) / 100)
    _flatStartM = string.tonumber(i_flatWindowStart) % 100
    _flatEndH = math.floor(string.tonumber(i_flatWindowEnd) / 100)
    _flatEndM = string.tonumber(i_flatWindowEnd) % 100
    _curH = hour(time, i_timezone)
    _curM = minute(time, i_timezone)
    _curTime = _curH * 60 + _curM
    _flatStart = _flatStartH * 60 + _flatStartM
    _flatEnd = _flatEndH * 60 + _flatEndM
    inFlatWindow: Series = i_flatWindowEnable and (_curTime >= _flatStart and _curTime < _flatEnd if _flatStart < _flatEnd else _curTime >= _flatStart or _curTime < _flatEnd)
    flatWindowJustStarted = inFlatWindow and (not inFlatWindow[1])



    nyDayAllowed = f_dayAllowed(i_nySun, i_nyMon, i_nyTue, i_nyWed, i_nyThu, i_nyFri, i_nySat)
    asDayAllowed = f_dayAllowed(i_asSun, i_asMon, i_asTue, i_asWed, i_asThu, i_asFri, i_asSat)
    lnDayAllowed = f_dayAllowed(i_lnSun, i_lnMon, i_lnTue, i_lnWed, i_lnThu, i_lnFri, i_lnSat)


    nySessionJustEnded: PersistentSeries[bool] = False
    asSessionJustEnded: PersistentSeries[bool] = False
    lnSessionJustEnded: PersistentSeries[bool] = False
    activeSession: Persistent[int] = 0
    if nySessionJustEnded[1]:
        nySessionJustEnded = False
    if asSessionJustEnded[1]:
        asSessionJustEnded = False
    if lnSessionJustEnded[1]:
        lnSessionJustEnded = False
    nyEntryBuf = i_nyEntryBuffer * syminfo.mintick
    nyRearmEntryBuf = i_nyEntryBuffer * syminfo.mintick
    asEntryBuf = i_asEntryBuffer * syminfo.mintick
    asRearmEntryBuf = i_asEntryBuffer * syminfo.mintick
    lnEntryBuf = i_lnEntryBuffer * syminfo.mintick
    lnRearmEntryBuf = i_lnEntryBuffer * syminfo.mintick

    def f_exitQualifies(wasSL: bool, rearmAfter: str):
        return rearmAfter == 'Both' or (rearmAfter == 'SL Only' and wasSL) or (rearmAfter == 'TP Only' and (not wasSL))

    def f_dirAllowed(lastDir: int, rearmDir: str):
        aL: bool = True
        aS: bool = True
        if rearmDir == 'Same Direction':
            aL = lastDir == 1
            aS = lastDir == -1
        elif rearmDir == 'Opposite Direction':
            aL = lastDir == -1
            aS = lastDir == 1
        return (aL, aS)

    def calcEndTime(startTime: str, duration: str):
        startHour = math.floor(string.tonumber(string.substring(startTime, 0, 2)))
        startMin = math.floor(string.tonumber(string.substring(startTime, 2, 4)))
        __block_result_3__ = na
        __switch__ = duration
        if __switch__ == "5 Min":
            __block_result_3__ = 5
        elif __switch__ == "15 Min":
            __block_result_3__ = 15
        elif __switch__ == "30 Min":
            __block_result_3__ = 30
        elif __switch__ == "1 Hour":
            __block_result_3__ = 60
        else:
            __block_result_3__ = 0
        addMins = __block_result_3__
        totalMins = startMin + addMins
        endHour = (startHour + math.floor(totalMins / 60)) % 24
        endMin = totalMins % 60
        endHourStr = '0' + string.tostring(endHour) if endHour < 10 else string.tostring(endHour)
        endMinStr = '0' + string.tostring(endMin) if endMin < 10 else string.tostring(endMin)
        return endHourStr + endMinStr

    def getLineStyle():
        __block_result_4__ = na
        __switch__ = lineStyle
        if __switch__ == "Solid":
            __block_result_4__ = line.style_solid
        elif __switch__ == "Dashed":
            __block_result_4__ = line.style_dashed
        elif __switch__ == "Dotted":
            __block_result_4__ = line.style_dotted
        return __block_result_4__

    def getLabelSize():
        __block_result_5__ = na
        __switch__ = labelSize
        if __switch__ == "Tiny":
            __block_result_5__ = size.tiny
        elif __switch__ == "Small":
            __block_result_5__ = size.small
        elif __switch__ == "Normal":
            __block_result_5__ = size.normal
        return __block_result_5__

    def getDashSize():
        return size.tiny


    nyORBEndTime = i_nyORBEnd if i_nyORBDur == 'Custom' else calcEndTime(i_nyORBStart, i_nyORBDur)
    nyORBSession = i_nyORBStart + '-' + nyORBEndTime
    nyTradeSession = i_nyORBStart + '-' + i_nySessEnd

    asORBEndTime = i_asORBEnd if i_asORBDur == 'Custom' else calcEndTime(i_asORBStart, i_asORBDur)
    asORBSession = i_asORBStart + '-' + asORBEndTime
    asTradeSession = i_asORBStart + '-' + i_asSessEnd

    lnORBEndTime = i_lnORBEnd if i_lnORBDur == 'Custom' else calcEndTime(i_lnORBStart, i_lnORBDur)
    lnORBSession = i_lnORBStart + '-' + lnORBEndTime
    lnTradeSession = i_lnORBStart + '-' + i_lnSessEnd

    inNYORB = not na(time(timeframe.period, nyORBSession, i_timezone))
    inNYTrade: Series = not na(time(timeframe.period, nyTradeSession, i_timezone))
    inAsORB = not na(time(timeframe.period, asORBSession, i_timezone))
    inAsTrade: Series = not na(time(timeframe.period, asTradeSession, i_timezone))
    inLnORB = not na(time(timeframe.period, lnORBSession, i_timezone))
    inLnTrade: Series = not na(time(timeframe.period, lnTradeSession, i_timezone))

    nyAdaptQty: Persistent[int] = 0
    asAdaptQty: Persistent[int] = 0
    lnAdaptQty: Persistent[int] = 0
    _nyTp1Qty: Persistent[int] = 0
    _nyTp2Qty: Persistent[int] = 0
    _nyTp3Qty: Persistent[int] = 0
    _asTp1Qty: Persistent[int] = 0
    _asTp2Qty: Persistent[int] = 0
    _asTp3Qty: Persistent[int] = 0
    _lnTp1Qty: Persistent[int] = 0
    _lnTp2Qty: Persistent[int] = 0
    _lnTp3Qty: Persistent[int] = 0

    def f_pdLineStyle(_style):
        return line.style_solid if _style == 'Solid' else line.style_dotted if _style == 'Dotted' else line.style_dashed

    def calcTrail(dir: int, curTrail: float, entry: float, tp1: float, tp2: float, tp3: float, origSL: float, trailEnabled: bool):
        newTrail: float = curTrail
        if trailEnabled and dir != 0:
            if dir == 1:
                if not na(tp3) and high >= tp3:
                    newTrail = math.max(newTrail, tp2)
                elif not na(tp2) and high >= tp2:
                    newTrail = math.max(newTrail, tp1)
                elif not na(tp1) and high >= tp1:
                    newTrail = math.max(newTrail, entry)
            else:
                if not na(tp3) and low <= tp3:
                    newTrail = math.min(newTrail, tp2)
                elif not na(tp2) and low <= tp2:
                    newTrail = math.min(newTrail, tp1)
                elif not na(tp1) and low <= tp1:
                    newTrail = math.min(newTrail, entry)
        return newTrail


    def f_lineStyle(s: str):
        return line.style_solid if s == 'Solid' else line.style_dotted if s == 'Dotted' else line.style_dashed

    slStyle = f_lineStyle(i_slLineStyle)
    tpStyle = f_lineStyle(i_tpLineStyle)
    trailLineStyle = f_lineStyle(i_trailStyle)

    _jsonBuy = '{"ticker": "' + syminfo.ticker + '", "action": "buy", "quantity": ' + string.tostring(i_nyContracts) + ', "signalPrice": ' + string.tostring(close) + '}'
    _jsonSell = '{"ticker": "' + syminfo.ticker + '", "action": "sell", "quantity": ' + string.tostring(i_nyContracts) + ', "signalPrice": ' + string.tostring(close) + '}'
    _jsonExit = '{"ticker": "' + syminfo.ticker + '", "action": "exit", "signalPrice": ' + string.tostring(close) + '}'

    nyOrbArray: Persistent[list[orbData]] = array.new(0, NA(orbData))
    nyORBHigh: Persistent[float] = na(float)
    nyORBLow: Persistent[float] = na(float)
    nyORBMid: Persistent[float] = na(float)
    nyOrbStartBar: Persistent[int] = na(int)
    nyOrbHighBar: Persistent[int] = na(int)
    nyOrbLowBar: Persistent[int] = na(int)
    nyOrbStartTime: Persistent[int] = na(int)
    nyOrbHighTime: Persistent[int] = na(int)
    nyOrbLowTime: Persistent[int] = na(int)
    nyOrbBuilding: Persistent[bool] = False
    nyOrbComplete: Persistent[bool] = False
    nySigFired: Persistent[bool] = False
    nyBrkPending: Persistent[bool] = False
    nyRetestDone: Persistent[bool] = False
    nyBrkDir: Persistent[int] = 0
    nyBrkBar: Persistent[int] = 0
    nySigEntry: Persistent[float] = na(float)
    nySigSL: Persistent[float] = na(float)
    nySigTP1: Persistent[float] = na(float)
    nySigTP2: Persistent[float] = na(float)
    nySigTP3: Persistent[float] = na(float)
    nySigDir: Persistent[int] = 0
    nyTP1Hit: Persistent[bool] = False
    nyTP2Hit: Persistent[bool] = False
    nyTP3Hit: Persistent[bool] = False
    nySLHit: Persistent[bool] = False
    nySLLine: Persistent[Line] = na(Line)
    nyTP1Line: Persistent[Line] = na(Line)
    nyTP2Line: Persistent[Line] = na(Line)
    nyTP3Line: Persistent[Line] = na(Line)
    nySLLabel: Persistent[Label] = na(Label)
    nyTP1Label: Persistent[Label] = na(Label)
    nyTP2Label: Persistent[Label] = na(Label)
    nyTP3Label: Persistent[Label] = na(Label)
    nyTrailSL: Persistent[float] = na(float)
    nyTrailLine: Persistent[Line] = na(Line)
    nyTrailLabel: Persistent[Label] = na(Label)
    nyFlattenDone: Persistent[bool] = False
    nyTradeCount: Persistent[int] = 0
    nyInsideBars: Persistent[int] = 0
    nyLastWasSL: Persistent[bool] = False
    nyLastDir: Persistent[int] = 0
    nyExitBar: Persistent[int] = 0
    nyCooldownDone: Persistent[bool] = False
    nyInsideStarted: Persistent[bool] = False

    nyDay: Series = f_dayKey(time, i_timezone)
    nyNewDay = nyDay != nz(nyDay[1], nyDay)
    nySessionStart = inNYTrade and (not inNYTrade[1]) or (inNYTrade and nyNewDay)
    if nySessionStart:
        nyFlattenDone = False
        nyTradeCount = 0
        nyInsideBars = 0
        nyLastWasSL = False
        nyLastDir = 0
        nyExitBar = 0
        nyCooldownDone = False
        nyInsideStarted = False
        nyORBHigh = na
        nyORBLow = na
        nyORBMid = na
        nyOrbBuilding = False
        nyOrbComplete = False
        nyOrbStartBar = na
        nyOrbHighBar = na
        nyOrbLowBar = na
        nyOrbStartTime = na
        nyOrbHighTime = na
        nyOrbLowTime = na
        nySigFired = False
        nyBrkPending = False
        nyRetestDone = False
        nyBrkDir = 0
        nyBrkBar = 0
        if strategy.position_size == 0:
            nySigDir = 0
        nyTP1Hit = False
        nyTP2Hit = False
        nyTP3Hit = False
        nySLHit = False
        nySigEntry = na
        nySigSL = na
        nySigTP1 = na
        nySigTP2 = na
        nySigTP3 = na
        nyTrailSL = na

        nySLLine = na
        nyTP1Line = na
        nyTP2Line = na
        nyTP3Line = na
        nySLLabel = na
        nyTP1Label = na
        nyTP2Label = na
        nyTP3Label = na
        nyTrailLine = na
        nyTrailLabel = na

    nySessionEnd = not inNYTrade and inNYTrade[1]
    if nySessionEnd and i_nyEnable:
        if array.size(nyOrbArray) > 0:
            for j in pine_range(0, array.size(nyOrbArray) - 1):
                _o = array.get(nyOrbArray, j)
                if na(_o.endBar):
                    _o.endBar = bar_index[1]
                    _o.endTime = time[1]
                    array.set(nyOrbArray, j, _o)

        if not na(nySLLine):
            line.set_x2(nySLLine, time)
        if not na(nyTP1Line):
            line.set_x2(nyTP1Line, time)
        if not na(nyTP2Line):
            line.set_x2(nyTP2Line, time)
        if not na(nyTP3Line):
            line.set_x2(nyTP3Line, time)
        nySLLine = na
        nyTP1Line = na
        nyTP2Line = na
        nyTP3Line = na
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        elif strategy.position_size < 0:
            strategy.order('EOS', strategy.long, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        nySessionJustEnded = True
        activeSession = 0
        nySigDir = 0

    if i_nyEnable and inNYORB and (not nyOrbComplete):
        if not nyOrbBuilding:
            nyOrbStartBar = bar_index
            nyOrbStartTime = time
            nyOrbBuilding = True
        if na(nyORBHigh) or high > nyORBHigh:
            nyORBHigh = high
            nyOrbHighBar = bar_index
            nyOrbHighTime = time
        if na(nyORBLow) or low < nyORBLow:
            nyORBLow = low
            nyOrbLowBar = bar_index
            nyOrbLowTime = time

    if i_nyEnable and (not inNYORB) and nyOrbBuilding and (not nyOrbComplete) and (not na(nyORBHigh)):
        nyOrbComplete = True
        nyORBMid = (nyORBHigh + nyORBLow) / 2

        nyRangeAvg = f_updateRangeAvg(nyRangeHistory, nyORBHigh - nyORBLow, i_adaptTPLookback)
        hiLine__000001a2__ = line.new(nyOrbHighTime, nyORBHigh, time, nyORBHigh, xloc=xloc.bar_time, color=i_nyHighColor, style=getLineStyle(), width=i_nyLineWidth)
        loLine__000001a2__ = line.new(nyOrbLowTime, nyORBLow, time, nyORBLow, xloc=xloc.bar_time, color=i_nyLowColor, style=getLineStyle(), width=i_nyLineWidth)
        midLine__000001a2__ = line.new(nyOrbStartTime, nyORBMid, time, nyORBMid, xloc=xloc.bar_time, color=i_nyMidColor, style=line.style_dotted, width=math.max(1, i_nyLineWidth - 1)) if i_nyShowMid else na
        hiLabel__000001a2__ = label.new(time, nyORBHigh, 'NY ORB H', xloc=xloc.bar_time, style=label.style_none, textcolor=i_nyHighColor, size=getLabelSize()) if showLabels else na
        loLabel__000001a2__ = label.new(time, nyORBLow, 'NY ORB L', xloc=xloc.bar_time, style=label.style_none, textcolor=i_nyLowColor, size=getLabelSize()) if showLabels else na
        midLabel__000001a2__ = label.new(time, nyORBMid, 'NY ORB M', xloc=xloc.bar_time, style=label.style_none, textcolor=i_nyMidColor, size=getLabelSize()) if showLabels and i_nyShowMid else na
        newOrb: orbData = orbData(nyORBHigh, nyORBLow, nyORBMid, nyOrbStartBar, nyOrbHighBar, nyOrbLowBar, na, nyOrbStartTime, nyOrbHighTime, nyOrbLowTime, na, hiLine__000001a2__, loLine__000001a2__, midLine__000001a2__, hiLabel__000001a2__, loLabel__000001a2__, midLabel__000001a2__)
        array.unshift(nyOrbArray, newOrb)
        if array.size(nyOrbArray) > i_daysToShow:
            old = array.pop(nyOrbArray)
            method_call('delete', old.hiLine)
            method_call('delete', old.loLine)
            method_call('delete', old.midLine)
            method_call('delete', old.hiLabel)
            method_call('delete', old.loLabel)
            method_call('delete', old.midLabel)

    if array.size(nyOrbArray) > 0:
        for i in pine_range(0, array.size(nyOrbArray) - 1):
            cur = array.get(nyOrbArray, i)
            _t2: int = time if na(cur.endTime) else cur.endTime

            method_call('set_x1', cur.hiLine, cur.hiTime)
            method_call('set_x2', cur.hiLine, _t2)
            method_call('set_x1', cur.loLine, cur.loTime)
            method_call('set_x2', cur.loLine, _t2)
            if i_nyShowMid and (not na(cur.midLine)):
                method_call('set_x1', cur.midLine, cur.startTime)
                method_call('set_x2', cur.midLine, _t2)

            if i == 0 and showLabels:
                method_call('set_x', cur.hiLabel, _t2)
                method_call('set_x', cur.loLabel, _t2)
                if i_nyShowMid and (not na(cur.midLabel)):
                    method_call('set_x', cur.midLabel, _t2)
            else:
                method_call('delete', cur.hiLabel)
                method_call('delete', cur.loLabel)
                if not na(cur.midLabel):
                    method_call('delete', cur.midLabel)
                cur.hiLabel = na
                cur.loLabel = na
                cur.midLabel = na

    _nyBuf = nyRearmEntryBuf if nyTradeCount > 0 and i_nyRearmEnable else nyEntryBuf
    nyCrossUp = close > nyORBHigh + _nyBuf and close[1] <= nyORBHigh + _nyBuf
    nyHighBreak = nyOrbComplete and inNYTrade and nyCrossUp
    nyCrossDn = close < nyORBLow - _nyBuf and close[1] >= nyORBLow - _nyBuf
    nyLowBreak = nyOrbComplete and inNYTrade and nyCrossDn
    nyLongSig: bool = False
    nyShortSig: bool = False

    if i_nyEnable and nyBrkPending and (bar_index > nyBrkBar) and (not nySigFired):
        _isMidRetest = i_nyEntryMode == 'Retest Midpoint'
        _retestLvl = nyORBMid if _isMidRetest else nyORBHigh if nyBrkDir == 1 else nyORBLow
        if nyBrkDir == 1:
            if not nyRetestDone and low <= _retestLvl:
                nyRetestDone = True
            if nyRetestDone and close > nyORBHigh + _nyBuf:
                nyLongSig = True
                nyBrkPending = False
                nyRetestDone = False
            elif _isMidRetest and close < nyORBLow:
                nyBrkPending = False
                nyRetestDone = False
            elif not _isMidRetest and close <= nyORBHigh:
                nyBrkPending = False
        elif nyBrkDir == -1:
            if not nyRetestDone and high >= _retestLvl:
                nyRetestDone = True
            if nyRetestDone and close < nyORBLow - _nyBuf:
                nyShortSig = True
                nyBrkPending = False
                nyRetestDone = False
            elif _isMidRetest and close > nyORBHigh:
                nyBrkPending = False
                nyRetestDone = False
            elif not _isMidRetest and close >= nyORBLow:
                nyBrkPending = False
        if nyBrkPending and bar_index - nyBrkBar >= i_nyRetestTimeout:
            nyBrkPending = False
            nyRetestDone = False

    if i_nyEnable and nyOrbComplete and inNYTrade and (not nySigFired) and (nyTradeCount < i_nyRearmMaxTrades or not i_nyRearmEnable):
        if nyHighBreak and (not nyBrkPending):
            if i_nyEntryMode == 'Breakout':
                nyLongSig = True
            else:
                nyBrkPending = True
                nyBrkDir = 1
                nyBrkBar = bar_index
        elif nyLowBreak and (not nyBrkPending):
            if i_nyEntryMode == 'Breakout':
                nyShortSig = True
            else:
                nyBrkPending = True
                nyBrkDir = -1
                nyBrkBar = bar_index

    if i_nyRearmEnable and nyTradeCount > 0 and (nyLastDir != 0):
        nyAllowL, nyAllowS = f_dirAllowed(nyLastDir, i_nyRearmDirection)
        if nyLongSig and (not nyAllowL):
            nyLongSig = False
        if nyShortSig and (not nyAllowS):
            nyShortSig = False

    if barstate.isconfirmed and nyLongSig and nyDayAllowed and (not inFlatWindow) and (i_nyDirection != 'Short Only') and (not nySessionJustEnded):
        nySigFired = True
        nySigEntry = close
        nySigDir = 1
        activeSession = 1
        nyTradeCount += 1
        nySigSL = nyORBMid if i_nySLMethod == 'Midpoint' else nyORBLow if i_nySLMethod == 'Opposite Side' else close - i_nySLPoints
        _risk = math.abs(nySigEntry - nySigSL)
        _nyOrbRange = nyORBHigh - nyORBLow if not na(nyORBHigh) and (not na(nyORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_nyTP1RR, _nyOrbRange, nyRangeAvg)
            _tp2rr: float = f_adaptTP(i_nyTP2RR, _nyOrbRange, nyRangeAvg)
            _tp3rr: float = f_adaptTP(i_nyTP3RR, _nyOrbRange, nyRangeAvg)
            nySigTP1 = nySigEntry + _risk * _tp1rr
            nySigTP2 = nySigEntry + _risk * _tp2rr
            nySigTP3 = nySigEntry + _risk * _tp3rr
        nyTrailSL = nySigSL

        nyAdaptQty = f_adaptiveQty(_risk, i_nyContracts)
        _tp2on: bool = i_nyTP2Qty > 0 and i_nyTP2RR > 0
        _tp3on: bool = i_nyTP3Qty > 0 and i_nyTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(nyAdaptQty, i_nyTP2RR, i_nyTP3RR, _tp2on, _tp3on)
            _nyTp1Qty = _q1
            _nyTp2Qty = _q2
            _nyTp3Qty = _q3
        else:
            _nyTp1Qty = math.min(i_nyTP1Qty, i_nyContracts)
            _nyTp2Qty = math.min(i_nyTP2Qty, i_nyContracts - _nyTp1Qty) if i_nyTP2Qty > 0 else 0
            _nyTp3Qty = math.min(i_nyTP3Qty, i_nyContracts - _nyTp1Qty - _nyTp2Qty) if i_nyTP3Qty > 0 else i_nyContracts - _nyTp1Qty - _nyTp2Qty
        _nyEntryQty = nyAdaptQty if i_adaptEnable else i_nyContracts
        _jsonBuyDyn = '{"ticker": "' + syminfo.ticker + '", "action": "buy", "quantity": ' + string.tostring(_nyEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('NY Long', strategy.long, qty=_nyEntryQty, alert_message=_jsonBuyDyn)
        if _risk > 0:
            strategy.exit('NY TP1', from_entry='NY Long', qty=_nyTp1Qty, limit=nySigTP1, stop=nySigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _nyTp2Qty > 0:
                strategy.exit('NY TP2', from_entry='NY Long', qty=_nyTp2Qty, limit=nySigTP2, stop=nySigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _nyTp3Qty > 0:
                strategy.exit('NY TP3', from_entry='NY Long', qty=_nyTp3Qty, limit=nySigTP3, stop=nySigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('NY SL', from_entry='NY Long', stop=nySigSL, alert_message=_jsonExit)
        if i_nyShowSLTP:
            nySLLine = line.new(time, nySigSL, time, nySigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            nySLLabel = label.new(time, nySigSL, 'SL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_slLineColor, size=getLabelSize()) if showLabels else na
            if not na(nySigTP1):
                nyTP1Line = line.new(time, nySigTP1, time, nySigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
                nyTP1Label = label.new(time, nySigTP1, 'TP1', xloc=xloc.bar_time, style=label.style_none, textcolor=i_tpLineColor, size=getLabelSize()) if showLabels else na
            if not na(nySigTP2) and _nyTp2Qty > 0:
                nyTP2Line = line.new(time, nySigTP2, time, nySigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
                nyTP2Label = label.new(time, nySigTP2, 'TP2', xloc=xloc.bar_time, style=label.style_none, textcolor=i_tpLineColor, size=getLabelSize()) if showLabels else na
            if not na(nySigTP3) and _nyTp3Qty > 0:
                nyTP3Line = line.new(time, nySigTP3, time, nySigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
                nyTP3Label = label.new(time, nySigTP3, 'TP3', xloc=xloc.bar_time, style=label.style_none, textcolor=i_tpLineColor, size=getLabelSize()) if showLabels else na

    if barstate.isconfirmed and nyShortSig and nyDayAllowed and (not inFlatWindow) and (i_nyDirection != 'Long Only') and (not nySessionJustEnded):
        nySigFired = True
        nySigEntry = close
        nySigDir = -1
        activeSession = 1
        nyTradeCount += 1
        nySigSL = nyORBMid if i_nySLMethod == 'Midpoint' else nyORBHigh if i_nySLMethod == 'Opposite Side' else close + i_nySLPoints
        _risk = math.abs(nySigSL - nySigEntry)
        _nyOrbRange = nyORBHigh - nyORBLow if not na(nyORBHigh) and (not na(nyORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_nyTP1RR, _nyOrbRange, nyRangeAvg)
            _tp2rr: float = f_adaptTP(i_nyTP2RR, _nyOrbRange, nyRangeAvg)
            _tp3rr: float = f_adaptTP(i_nyTP3RR, _nyOrbRange, nyRangeAvg)
            nySigTP1 = nySigEntry - _risk * _tp1rr
            nySigTP2 = nySigEntry - _risk * _tp2rr
            nySigTP3 = nySigEntry - _risk * _tp3rr
        nyTrailSL = nySigSL

        nyAdaptQty = f_adaptiveQty(_risk, i_nyContracts)
        _tp2on: bool = i_nyTP2Qty > 0 and i_nyTP2RR > 0
        _tp3on: bool = i_nyTP3Qty > 0 and i_nyTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(nyAdaptQty, i_nyTP2RR, i_nyTP3RR, _tp2on, _tp3on)
            _nyTp1Qty = _q1
            _nyTp2Qty = _q2
            _nyTp3Qty = _q3
        else:
            _nyTp1Qty = math.min(i_nyTP1Qty, i_nyContracts)
            _nyTp2Qty = math.min(i_nyTP2Qty, i_nyContracts - _nyTp1Qty) if i_nyTP2Qty > 0 else 0
            _nyTp3Qty = math.min(i_nyTP3Qty, i_nyContracts - _nyTp1Qty - _nyTp2Qty) if i_nyTP3Qty > 0 else i_nyContracts - _nyTp1Qty - _nyTp2Qty
        _nyEntryQty = nyAdaptQty if i_adaptEnable else i_nyContracts
        _jsonSellDyn = '{"ticker": "' + syminfo.ticker + '", "action": "sell", "quantity": ' + string.tostring(_nyEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('NY Short', strategy.short, qty=_nyEntryQty, alert_message=_jsonSellDyn)
        if _risk > 0:
            strategy.exit('NY TP1', from_entry='NY Short', qty=_nyTp1Qty, limit=nySigTP1, stop=nySigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _nyTp2Qty > 0:
                strategy.exit('NY TP2', from_entry='NY Short', qty=_nyTp2Qty, limit=nySigTP2, stop=nySigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _nyTp3Qty > 0:
                strategy.exit('NY TP3', from_entry='NY Short', qty=_nyTp3Qty, limit=nySigTP3, stop=nySigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('NY SL', from_entry='NY Short', stop=nySigSL, alert_message=_jsonExit)
        if i_nyShowSLTP:
            nySLLine = line.new(time, nySigSL, time, nySigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            if not na(nySigTP1):
                nyTP1Line = line.new(time, nySigTP1, time, nySigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
            if not na(nySigTP2) and _nyTp2Qty > 0:
                nyTP2Line = line.new(time, nySigTP2, time, nySigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
            if not na(nySigTP3) and _nyTp3Qty > 0:
                nyTP3Line = line.new(time, nySigTP3, time, nySigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))

    if i_nyTrailEnable and nySigDir != 0 and (not nySLHit) and (strategy.position_size != 0):
        _prevTrail = nyTrailSL
        nyTrailSL = calcTrail(nySigDir, nyTrailSL, nySigEntry, nySigTP1, nySigTP2, nySigTP3, nySigSL, i_nyTrailEnable)
        if nyTrailSL != _prevTrail:
            if nySigDir == 1:
                strategy.exit('NY TP1', from_entry='NY Long', qty=_nyTp1Qty, limit=nySigTP1, stop=nyTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _nyTp2Qty > 0:
                    strategy.exit('NY TP2', from_entry='NY Long', qty=_nyTp2Qty, limit=nySigTP2, stop=nyTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _nyTp3Qty > 0:
                    strategy.exit('NY TP3', from_entry='NY Long', qty=_nyTp3Qty, limit=nySigTP3, stop=nyTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
            else:
                strategy.exit('NY TP1', from_entry='NY Short', qty=_nyTp1Qty, limit=nySigTP1, stop=nyTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _nyTp2Qty > 0:
                    strategy.exit('NY TP2', from_entry='NY Short', qty=_nyTp2Qty, limit=nySigTP2, stop=nyTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _nyTp3Qty > 0:
                    strategy.exit('NY TP3', from_entry='NY Short', qty=_nyTp3Qty, limit=nySigTP3, stop=nyTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)

        if i_nyTrailShowLine and nyTrailSL != nySigSL:
            nyTrailLine = line.new(time[1], nyTrailSL, time, nyTrailSL, xloc=xloc.bar_time, color=i_trailColor, style=trailLineStyle, width=i_trailWidth)
            if na(nyTrailLabel):
                nyTrailLabel = label.new(time, nyTrailSL, 'TRAIL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_trailColor, size=getLabelSize()) if showLabels else na
            else:
                label.set_y(nyTrailLabel, nyTrailSL)

    if nySigDir != 0 and i_nyShowSLTP:
        if not na(nySLLine):
            line.set_x2(nySLLine, time)
        if not na(nySLLabel):
            label.set_x(nySLLabel, time)
        if not na(nyTP1Line):
            line.set_x2(nyTP1Line, time)
        if not na(nyTP1Label):
            label.set_x(nyTP1Label, time)
        if not na(nyTP2Line):
            line.set_x2(nyTP2Line, time)
        if not na(nyTP2Label):
            label.set_x(nyTP2Label, time)
        if not na(nyTP3Line):
            line.set_x2(nyTP3Line, time)
        if not na(nyTP3Label):
            label.set_x(nyTP3Label, time)

        if not na(nyTrailLine):
            line.set_x2(nyTrailLine, time)
        if not na(nyTrailLabel):
            label.set_x(nyTrailLabel, time)

    if i_nyEnable and nySigDir != 0 and (not nySLHit):
        if nySigDir == 1:
            if low <= nyTrailSL:
                nySLHit = True
                nyLastWasSL = True
                nyLastDir = nySigDir
                nyExitBar = bar_index
                nyCooldownDone = False
                nyInsideStarted = False
                nyInsideBars = 0
                nySigDir = 0

                if not na(nySLLine):
                    line.set_x2(nySLLine, time)
                if not na(nyTP1Line):
                    line.set_x2(nyTP1Line, time)
                if not na(nyTP2Line):
                    line.set_x2(nyTP2Line, time)
                if not na(nyTP3Line):
                    line.set_x2(nyTP3Line, time)
                nySLLine = na
                nyTP1Line = na
                nyTP2Line = na
                nyTP3Line = na
            else:
                if not nyTP1Hit and high >= nySigTP1:
                    nyTP1Hit = True
                if not nyTP2Hit and high >= nySigTP2:
                    nyTP2Hit = True
                if not nyTP3Hit and high >= nySigTP3:
                    nyTP3Hit = True
        elif nySigDir == -1:
            if high >= nyTrailSL:
                nySLHit = True
                nyLastWasSL = True
                nyLastDir = nySigDir
                nyExitBar = bar_index
                nyCooldownDone = False
                nyInsideStarted = False
                nyInsideBars = 0
                nySigDir = 0
                if not na(nySLLine):
                    line.set_x2(nySLLine, time)
                if not na(nyTP1Line):
                    line.set_x2(nyTP1Line, time)
                if not na(nyTP2Line):
                    line.set_x2(nyTP2Line, time)
                if not na(nyTP3Line):
                    line.set_x2(nyTP3Line, time)
                nySLLine = na
                nyTP1Line = na
                nyTP2Line = na
                nyTP3Line = na
            else:
                if not nyTP1Hit and low <= nySigTP1:
                    nyTP1Hit = True
                if not nyTP2Hit and low <= nySigTP2:
                    nyTP2Hit = True
                if not nyTP3Hit and low <= nySigTP3:
                    nyTP3Hit = True

    if i_nyEnable and nySigFired and (nySigDir != 0) and (strategy.position_size == 0) and (strategy.position_size[1] != 0) and (not nySLHit):
        nyLastWasSL = False
        nyLastDir = nySigDir
        nyExitBar = bar_index
        nyCooldownDone = False
        nyInsideStarted = False
        nyInsideBars = 0
        nySigDir = 0

        if not na(nySLLine):
            line.set_x2(nySLLine, time)
        if not na(nyTP1Line):
            line.set_x2(nyTP1Line, time)
        if not na(nyTP2Line):
            line.set_x2(nyTP2Line, time)
        if not na(nyTP3Line):
            line.set_x2(nyTP3Line, time)
        nySLLine = na
        nyTP1Line = na
        nyTP2Line = na
        nyTP3Line = na

    plotshape(i_nyShowEntry and nyLongSig and nyDayAllowed and (not inFlatWindow) and (i_nyDirection != 'Short Only') and (not nySessionJustEnded), title='NY Long', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, text='NY LONG')
    plotshape(i_nyShowEntry and nyShortSig and nyDayAllowed and (not inFlatWindow) and (i_nyDirection != 'Long Only') and (not nySessionJustEnded), title='NY Short', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, text='NY SHORT')

    asOrbArray: Persistent[list[orbData]] = array.new(0, NA(orbData))
    asORBHigh: Persistent[float] = na(float)
    asORBLow: Persistent[float] = na(float)
    asORBMid: Persistent[float] = na(float)
    asOrbStartBar: Persistent[int] = na(int)
    asOrbHighBar: Persistent[int] = na(int)
    asOrbLowBar: Persistent[int] = na(int)
    asOrbStartTime: Persistent[int] = na(int)
    asOrbHighTime: Persistent[int] = na(int)
    asOrbLowTime: Persistent[int] = na(int)
    asOrbBuilding: Persistent[bool] = False
    asOrbComplete: Persistent[bool] = False
    asSigFired: Persistent[bool] = False
    asBrkPending: Persistent[bool] = False
    asRetestDone: Persistent[bool] = False
    asBrkDir: Persistent[int] = 0
    asBrkBar: Persistent[int] = 0
    asSigEntry: Persistent[float] = na(float)
    asSigSL: Persistent[float] = na(float)
    asSigTP1: Persistent[float] = na(float)
    asSigTP2: Persistent[float] = na(float)
    asSigTP3: Persistent[float] = na(float)
    asSigDir: Persistent[int] = 0
    asTP1Hit: Persistent[bool] = False
    asTP2Hit: Persistent[bool] = False
    asTP3Hit: Persistent[bool] = False
    asSLHit: Persistent[bool] = False
    asSLLine: Persistent[Line] = na(Line)
    asTP1Line: Persistent[Line] = na(Line)
    asTP2Line: Persistent[Line] = na(Line)
    asTP3Line: Persistent[Line] = na(Line)
    asSLLabel: Persistent[Label] = na(Label)
    asTP1Label: Persistent[Label] = na(Label)
    asTP2Label: Persistent[Label] = na(Label)
    asTP3Label: Persistent[Label] = na(Label)
    asTrailSL: Persistent[float] = na(float)
    asTrailLine: Persistent[Line] = na(Line)
    asTrailLabel: Persistent[Label] = na(Label)
    asFlattenDone: Persistent[bool] = False
    asTradeCount: Persistent[int] = 0
    asInsideBars: Persistent[int] = 0
    asLastWasSL: Persistent[bool] = False
    asLastDir: Persistent[int] = 0
    asExitBar: Persistent[int] = 0
    asCooldownDone: Persistent[bool] = False
    asInsideStarted: Persistent[bool] = False

    asDay: Series = f_dayKey(time, i_timezone)
    asNewDay = asDay != nz(asDay[1], asDay)
    asSessionStart = inAsTrade and (not inAsTrade[1]) or (inAsTrade and asNewDay)
    if asSessionStart:
        asFlattenDone = False
        asTradeCount = 0
        asInsideBars = 0
        asLastWasSL = False
        asLastDir = 0
        asExitBar = 0
        asCooldownDone = False
        asInsideStarted = False
        asORBHigh = na
        asORBLow = na
        asORBMid = na
        asOrbBuilding = False
        asOrbComplete = False
        asOrbStartBar = na
        asOrbHighBar = na
        asOrbLowBar = na
        asOrbStartTime = na
        asOrbHighTime = na
        asOrbLowTime = na
        asSigFired = False
        asBrkPending = False
        asRetestDone = False
        asBrkDir = 0
        asBrkBar = 0
        if strategy.position_size == 0:
            asSigDir = 0
        asTP1Hit = False
        asTP2Hit = False
        asTP3Hit = False
        asSLHit = False
        asSigEntry = na
        asSigSL = na
        asSigTP1 = na
        asSigTP2 = na
        asSigTP3 = na
        asTrailSL = na

        asSLLine = na
        asTP1Line = na
        asTP2Line = na
        asTP3Line = na
        asSLLabel = na
        asTP1Label = na
        asTP2Label = na
        asTP3Label = na
        asTrailLine = na
        asTrailLabel = na

    asSessionEnd = not inAsTrade and inAsTrade[1]
    if asSessionEnd and i_asEnable:
        if array.size(asOrbArray) > 0:
            for j in pine_range(0, array.size(asOrbArray) - 1):
                _o = array.get(asOrbArray, j)
                if na(_o.endBar):
                    _o.endBar = bar_index[1]
                    _o.endTime = time[1]
                    array.set(asOrbArray, j, _o)

        if not na(asSLLine):
            line.set_x2(asSLLine, time)
        if not na(asTP1Line):
            line.set_x2(asTP1Line, time)
        if not na(asTP2Line):
            line.set_x2(asTP2Line, time)
        if not na(asTP3Line):
            line.set_x2(asTP3Line, time)
        asSLLine = na
        asTP1Line = na
        asTP2Line = na
        asTP3Line = na
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        elif strategy.position_size < 0:
            strategy.order('EOS', strategy.long, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        asSessionJustEnded = True
        activeSession = 0
        asSigDir = 0
    if i_asEnable and inAsORB and (not asOrbComplete):
        if not asOrbBuilding:
            asOrbStartBar = bar_index
            asOrbStartTime = time
            asOrbBuilding = True
        if na(asORBHigh) or high > asORBHigh:
            asORBHigh = high
            asOrbHighBar = bar_index
            asOrbHighTime = time
        if na(asORBLow) or low < asORBLow:
            asORBLow = low
            asOrbLowBar = bar_index
            asOrbLowTime = time

    if i_asEnable and (not inAsORB) and asOrbBuilding and (not asOrbComplete) and (not na(asORBHigh)):
        asOrbComplete = True
        asORBMid = (asORBHigh + asORBLow) / 2

        asRangeAvg = f_updateRangeAvg(asRangeHistory, asORBHigh - asORBLow, i_adaptTPLookback)
        hiLine__000002dd__ = line.new(asOrbHighTime, asORBHigh, time, asORBHigh, xloc=xloc.bar_time, color=i_asHighColor, style=getLineStyle(), width=i_asLineWidth)
        loLine__000002dd__ = line.new(asOrbLowTime, asORBLow, time, asORBLow, xloc=xloc.bar_time, color=i_asLowColor, style=getLineStyle(), width=i_asLineWidth)
        midLine__000002dd__ = line.new(asOrbStartTime, asORBMid, time, asORBMid, xloc=xloc.bar_time, color=i_asMidColor, style=line.style_dotted, width=math.max(1, i_asLineWidth - 1)) if i_asShowMid else na
        hiLabel__000002dd__ = label.new(time, asORBHigh, 'ASIA ORB H', xloc=xloc.bar_time, style=label.style_none, textcolor=i_asHighColor, size=getLabelSize()) if showLabels else na
        loLabel__000002dd__ = label.new(time, asORBLow, 'ASIA ORB L', xloc=xloc.bar_time, style=label.style_none, textcolor=i_asLowColor, size=getLabelSize()) if showLabels else na
        midLabel__000002dd__ = label.new(time, asORBMid, 'ASIA ORB M', xloc=xloc.bar_time, style=label.style_none, textcolor=i_asMidColor, size=getLabelSize()) if showLabels and i_asShowMid else na
        newOrb: orbData = orbData(asORBHigh, asORBLow, asORBMid, asOrbStartBar, asOrbHighBar, asOrbLowBar, na, asOrbStartTime, asOrbHighTime, asOrbLowTime, na, hiLine__000002dd__, loLine__000002dd__, midLine__000002dd__, hiLabel__000002dd__, loLabel__000002dd__, midLabel__000002dd__)
        array.unshift(asOrbArray, newOrb)
        if array.size(asOrbArray) > i_daysToShow:
            old = array.pop(asOrbArray)
            method_call('delete', old.hiLine)
            method_call('delete', old.loLine)
            method_call('delete', old.midLine)
            method_call('delete', old.hiLabel)
            method_call('delete', old.loLabel)
            method_call('delete', old.midLabel)

    if array.size(asOrbArray) > 0:
        for i in pine_range(0, array.size(asOrbArray) - 1):
            cur = array.get(asOrbArray, i)
            _t2: int = time if na(cur.endTime) else cur.endTime

            method_call('set_x1', cur.hiLine, cur.hiTime)
            method_call('set_x2', cur.hiLine, _t2)
            method_call('set_x1', cur.loLine, cur.loTime)
            method_call('set_x2', cur.loLine, _t2)
            if i_asShowMid and (not na(cur.midLine)):
                method_call('set_x1', cur.midLine, cur.startTime)
                method_call('set_x2', cur.midLine, _t2)

            if i == 0 and showLabels:
                method_call('set_x', cur.hiLabel, _t2)
                method_call('set_x', cur.loLabel, _t2)
                if i_asShowMid and (not na(cur.midLabel)):
                    method_call('set_x', cur.midLabel, _t2)
            else:
                method_call('delete', cur.hiLabel)
                method_call('delete', cur.loLabel)
                if not na(cur.midLabel):
                    method_call('delete', cur.midLabel)
                cur.hiLabel = na
                cur.loLabel = na
                cur.midLabel = na

    _asBuf = asRearmEntryBuf if asTradeCount > 0 and i_asRearmEnable else asEntryBuf
    asCrossUp = close > asORBHigh + _asBuf and close[1] <= asORBHigh + _asBuf
    asHighBreak = asOrbComplete and inAsTrade and asCrossUp
    asCrossDn = close < asORBLow - _asBuf and close[1] >= asORBLow - _asBuf
    asLowBreak = asOrbComplete and inAsTrade and asCrossDn
    asLongSig: bool = False
    asShortSig: bool = False

    if i_asEnable and asBrkPending and (bar_index > asBrkBar) and (not asSigFired):
        _isMidRetest = i_asEntryMode == 'Retest Midpoint'
        _retestLvl = asORBMid if _isMidRetest else asORBHigh if asBrkDir == 1 else asORBLow
        if asBrkDir == 1:
            if not asRetestDone and low <= _retestLvl:
                asRetestDone = True
            if asRetestDone and close > asORBHigh + _asBuf:
                asLongSig = True
                asBrkPending = False
                asRetestDone = False
            elif _isMidRetest and close < asORBLow:
                asBrkPending = False
                asRetestDone = False
            elif not _isMidRetest and close <= asORBHigh:
                asBrkPending = False
        elif asBrkDir == -1:
            if not asRetestDone and high >= _retestLvl:
                asRetestDone = True
            if asRetestDone and close < asORBLow - _asBuf:
                asShortSig = True
                asBrkPending = False
                asRetestDone = False
            elif _isMidRetest and close > asORBHigh:
                asBrkPending = False
                asRetestDone = False
            elif not _isMidRetest and close >= asORBLow:
                asBrkPending = False
        if asBrkPending and bar_index - asBrkBar >= i_asRetestTimeout:
            asBrkPending = False
            asRetestDone = False

    if i_asEnable and asOrbComplete and inAsTrade and (not asSigFired) and (asTradeCount < i_asRearmMaxTrades or not i_asRearmEnable):
        if asHighBreak and (not asBrkPending):
            if i_asEntryMode == 'Breakout':
                asLongSig = True
            else:
                asBrkPending = True
                asBrkDir = 1
                asBrkBar = bar_index
        elif asLowBreak and (not asBrkPending):
            if i_asEntryMode == 'Breakout':
                asShortSig = True
            else:
                asBrkPending = True
                asBrkDir = -1
                asBrkBar = bar_index

    if i_asRearmEnable and asTradeCount > 0 and (asLastDir != 0):
        asAllowL, asAllowS = f_dirAllowed(asLastDir, i_asRearmDirection)
        if asLongSig and (not asAllowL):
            asLongSig = False
        if asShortSig and (not asAllowS):
            asShortSig = False

    if barstate.isconfirmed and asLongSig and asDayAllowed and (not inFlatWindow) and (i_asDirection != 'Short Only') and (not asSessionJustEnded):
        asSigFired = True
        asSigEntry = close
        asSigDir = 1
        activeSession = 2
        asTradeCount += 1
        asSigSL = asORBMid if i_asSLMethod == 'Midpoint' else asORBLow if i_asSLMethod == 'Opposite Side' else close - i_asSLPoints
        _risk = math.abs(asSigEntry - asSigSL)
        _asOrbRange = asORBHigh - asORBLow if not na(asORBHigh) and (not na(asORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_asTP1RR, _asOrbRange, asRangeAvg)
            _tp2rr: float = f_adaptTP(i_asTP2RR, _asOrbRange, asRangeAvg)
            _tp3rr: float = f_adaptTP(i_asTP3RR, _asOrbRange, asRangeAvg)
            asSigTP1 = asSigEntry + _risk * _tp1rr
            asSigTP2 = asSigEntry + _risk * _tp2rr
            asSigTP3 = asSigEntry + _risk * _tp3rr
        asTrailSL = asSigSL

        asAdaptQty = f_adaptiveQty(_risk, i_asContracts)
        _tp2on: bool = i_asTP2Qty > 0 and i_asTP2RR > 0
        _tp3on: bool = i_asTP3Qty > 0 and i_asTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(asAdaptQty, i_asTP2RR, i_asTP3RR, _tp2on, _tp3on)
            _asTp1Qty = _q1
            _asTp2Qty = _q2
            _asTp3Qty = _q3
        else:
            _asTp1Qty = math.min(i_asTP1Qty, i_asContracts)
            _asTp2Qty = math.min(i_asTP2Qty, i_asContracts - _asTp1Qty) if i_asTP2Qty > 0 else 0
            _asTp3Qty = math.min(i_asTP3Qty, i_asContracts - _asTp1Qty - _asTp2Qty) if i_asTP3Qty > 0 else i_asContracts - _asTp1Qty - _asTp2Qty
        _asEntryQty = asAdaptQty if i_adaptEnable else i_asContracts
        _jsonBuyDyn = '{"ticker": "' + syminfo.ticker + '", "action": "buy", "quantity": ' + string.tostring(_asEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('AS Long', strategy.long, qty=_asEntryQty, alert_message=_jsonBuyDyn)
        if _risk > 0:
            strategy.exit('AS TP1', from_entry='AS Long', qty=_asTp1Qty, limit=asSigTP1, stop=asSigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _asTp2Qty > 0:
                strategy.exit('AS TP2', from_entry='AS Long', qty=_asTp2Qty, limit=asSigTP2, stop=asSigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _asTp3Qty > 0:
                strategy.exit('AS TP3', from_entry='AS Long', qty=_asTp3Qty, limit=asSigTP3, stop=asSigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('AS SL', from_entry='AS Long', stop=asSigSL, alert_message=_jsonExit)
        if i_asShowSLTP:
            asSLLine = line.new(time, asSigSL, time, asSigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            if not na(asSigTP1):
                asTP1Line = line.new(time, asSigTP1, time, asSigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
            if not na(asSigTP2) and _asTp2Qty > 0:
                asTP2Line = line.new(time, asSigTP2, time, asSigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
            if not na(asSigTP3) and _asTp3Qty > 0:
                asTP3Line = line.new(time, asSigTP3, time, asSigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))

    if barstate.isconfirmed and asShortSig and asDayAllowed and (not inFlatWindow) and (i_asDirection != 'Long Only') and (not asSessionJustEnded):
        asSigFired = True
        asSigEntry = close
        asSigDir = -1
        activeSession = 2
        asTradeCount += 1
        asSigSL = asORBMid if i_asSLMethod == 'Midpoint' else asORBHigh if i_asSLMethod == 'Opposite Side' else close + i_asSLPoints
        _risk = math.abs(asSigSL - asSigEntry)
        _asOrbRange = asORBHigh - asORBLow if not na(asORBHigh) and (not na(asORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_asTP1RR, _asOrbRange, asRangeAvg)
            _tp2rr: float = f_adaptTP(i_asTP2RR, _asOrbRange, asRangeAvg)
            _tp3rr: float = f_adaptTP(i_asTP3RR, _asOrbRange, asRangeAvg)
            asSigTP1 = asSigEntry - _risk * _tp1rr
            asSigTP2 = asSigEntry - _risk * _tp2rr
            asSigTP3 = asSigEntry - _risk * _tp3rr
        asTrailSL = asSigSL

        asAdaptQty = f_adaptiveQty(_risk, i_asContracts)
        _tp2on: bool = i_asTP2Qty > 0 and i_asTP2RR > 0
        _tp3on: bool = i_asTP3Qty > 0 and i_asTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(asAdaptQty, i_asTP2RR, i_asTP3RR, _tp2on, _tp3on)
            _asTp1Qty = _q1
            _asTp2Qty = _q2
            _asTp3Qty = _q3
        else:
            _asTp1Qty = math.min(i_asTP1Qty, i_asContracts)
            _asTp2Qty = math.min(i_asTP2Qty, i_asContracts - _asTp1Qty) if i_asTP2Qty > 0 else 0
            _asTp3Qty = math.min(i_asTP3Qty, i_asContracts - _asTp1Qty - _asTp2Qty) if i_asTP3Qty > 0 else i_asContracts - _asTp1Qty - _asTp2Qty
        _asEntryQty = asAdaptQty if i_adaptEnable else i_asContracts
        _jsonSellDyn = '{"ticker": "' + syminfo.ticker + '", "action": "sell", "quantity": ' + string.tostring(_asEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('AS Short', strategy.short, qty=_asEntryQty, alert_message=_jsonSellDyn)
        if _risk > 0:
            strategy.exit('AS TP1', from_entry='AS Short', qty=_asTp1Qty, limit=asSigTP1, stop=asSigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _asTp2Qty > 0:
                strategy.exit('AS TP2', from_entry='AS Short', qty=_asTp2Qty, limit=asSigTP2, stop=asSigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _asTp3Qty > 0:
                strategy.exit('AS TP3', from_entry='AS Short', qty=_asTp3Qty, limit=asSigTP3, stop=asSigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('AS SL', from_entry='AS Short', stop=asSigSL, alert_message=_jsonExit)
        if i_asShowSLTP:
            asSLLine = line.new(time, asSigSL, time, asSigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            if not na(asSigTP1):
                asTP1Line = line.new(time, asSigTP1, time, asSigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
            if not na(asSigTP2) and _asTp2Qty > 0:
                asTP2Line = line.new(time, asSigTP2, time, asSigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
            if not na(asSigTP3) and _asTp3Qty > 0:
                asTP3Line = line.new(time, asSigTP3, time, asSigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))

    if i_asTrailEnable and asSigDir != 0 and (not asSLHit) and (strategy.position_size != 0):
        _prevTrail = asTrailSL
        asTrailSL = calcTrail(asSigDir, asTrailSL, asSigEntry, asSigTP1, asSigTP2, asSigTP3, asSigSL, i_asTrailEnable)
        if asTrailSL != _prevTrail:
            if asSigDir == 1:
                strategy.exit('AS TP1', from_entry='AS Long', qty=_asTp1Qty, limit=asSigTP1, stop=asTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _asTp2Qty > 0:
                    strategy.exit('AS TP2', from_entry='AS Long', qty=_asTp2Qty, limit=asSigTP2, stop=asTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _asTp3Qty > 0:
                    strategy.exit('AS TP3', from_entry='AS Long', qty=_asTp3Qty, limit=asSigTP3, stop=asTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
            else:
                strategy.exit('AS TP1', from_entry='AS Short', qty=_asTp1Qty, limit=asSigTP1, stop=asTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _asTp2Qty > 0:
                    strategy.exit('AS TP2', from_entry='AS Short', qty=_asTp2Qty, limit=asSigTP2, stop=asTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _asTp3Qty > 0:
                    strategy.exit('AS TP3', from_entry='AS Short', qty=_asTp3Qty, limit=asSigTP3, stop=asTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        if i_asTrailShowLine and asTrailSL != asSigSL:
            asTrailLine = line.new(time[1], asTrailSL, time, asTrailSL, xloc=xloc.bar_time, color=i_trailColor, style=trailLineStyle, width=i_trailWidth)
            if na(asTrailLabel):
                asTrailLabel = label.new(time, asTrailSL, 'TRAIL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_trailColor, size=getLabelSize()) if showLabels else na
            else:
                label.set_y(asTrailLabel, asTrailSL)

    if asSigDir != 0 and i_asShowSLTP:
        if not na(asSLLine):
            line.set_x2(asSLLine, time)
        if not na(asSLLabel):
            label.set_x(asSLLabel, time)
        if not na(asTP1Line):
            line.set_x2(asTP1Line, time)
        if not na(asTP1Label):
            label.set_x(asTP1Label, time)
        if not na(asTP2Line):
            line.set_x2(asTP2Line, time)
        if not na(asTP2Label):
            label.set_x(asTP2Label, time)
        if not na(asTP3Line):
            line.set_x2(asTP3Line, time)
        if not na(asTP3Label):
            label.set_x(asTP3Label, time)

        if not na(asTrailLine):
            line.set_x2(asTrailLine, time)
        if not na(asTrailLabel):
            label.set_x(asTrailLabel, time)

    if i_asEnable and asSigDir != 0 and (not asSLHit):
        if asSigDir == 1:
            if low <= asTrailSL:
                asSLHit = True
                asLastWasSL = True
                asLastDir = asSigDir
                asExitBar = bar_index
                asCooldownDone = False
                asInsideStarted = False
                asInsideBars = 0
                asSigDir = 0
                if not na(asSLLine):
                    line.set_x2(asSLLine, time)
                if not na(asTP1Line):
                    line.set_x2(asTP1Line, time)
                if not na(asTP2Line):
                    line.set_x2(asTP2Line, time)
                if not na(asTP3Line):
                    line.set_x2(asTP3Line, time)
                asSLLine = na
                asTP1Line = na
                asTP2Line = na
                asTP3Line = na
            else:
                if not asTP1Hit and high >= asSigTP1:
                    asTP1Hit = True
                if not asTP2Hit and high >= asSigTP2:
                    asTP2Hit = True
                if not asTP3Hit and high >= asSigTP3:
                    asTP3Hit = True
        elif asSigDir == -1:
            if high >= asTrailSL:
                asSLHit = True
                asLastWasSL = True
                asLastDir = asSigDir
                asExitBar = bar_index
                asCooldownDone = False
                asInsideStarted = False
                asInsideBars = 0
                asSigDir = 0
                if not na(asSLLine):
                    line.set_x2(asSLLine, time)
                if not na(asTP1Line):
                    line.set_x2(asTP1Line, time)
                if not na(asTP2Line):
                    line.set_x2(asTP2Line, time)
                if not na(asTP3Line):
                    line.set_x2(asTP3Line, time)
                asSLLine = na
                asTP1Line = na
                asTP2Line = na
                asTP3Line = na
            else:
                if not asTP1Hit and low <= asSigTP1:
                    asTP1Hit = True
                if not asTP2Hit and low <= asSigTP2:
                    asTP2Hit = True
                if not asTP3Hit and low <= asSigTP3:
                    asTP3Hit = True

    if i_asEnable and asSigFired and (asSigDir != 0) and (strategy.position_size == 0) and (strategy.position_size[1] != 0) and (not asSLHit):
        asLastWasSL = False
        asLastDir = asSigDir
        asExitBar = bar_index
        asCooldownDone = False
        asInsideStarted = False
        asInsideBars = 0
        asSigDir = 0
        if not na(asSLLine):
            line.set_x2(asSLLine, time)
        if not na(asTP1Line):
            line.set_x2(asTP1Line, time)
        if not na(asTP2Line):
            line.set_x2(asTP2Line, time)
        if not na(asTP3Line):
            line.set_x2(asTP3Line, time)
        asSLLine = na
        asTP1Line = na
        asTP2Line = na
        asTP3Line = na

    plotshape(i_asShowEntry and asLongSig and asDayAllowed and (not inFlatWindow) and (i_asDirection != 'Short Only') and (not asSessionJustEnded), title='AS Long', style=shape.triangleup, location=location.belowbar, color=color.new('#E040FB'), size=size.small, text='AS LONG')
    plotshape(i_asShowEntry and asShortSig and asDayAllowed and (not inFlatWindow) and (i_asDirection != 'Long Only') and (not asSessionJustEnded), title='AS Short', style=shape.triangledown, location=location.abovebar, color=color.new('#E040FB'), size=size.small, text='AS SHORT')

    lnOrbArray: Persistent[list[orbData]] = array.new(0, NA(orbData))
    lnORBHigh: Persistent[float] = na(float)
    lnORBLow: Persistent[float] = na(float)
    lnORBMid: Persistent[float] = na(float)
    lnOrbStartBar: Persistent[int] = na(int)
    lnOrbHighBar: Persistent[int] = na(int)
    lnOrbLowBar: Persistent[int] = na(int)
    lnOrbStartTime: Persistent[int] = na(int)
    lnOrbHighTime: Persistent[int] = na(int)
    lnOrbLowTime: Persistent[int] = na(int)
    lnOrbBuilding: Persistent[bool] = False
    lnOrbComplete: Persistent[bool] = False
    lnSigFired: Persistent[bool] = False
    lnBrkPending: Persistent[bool] = False
    lnRetestDone: Persistent[bool] = False
    lnBrkDir: Persistent[int] = 0
    lnBrkBar: Persistent[int] = 0
    lnSigEntry: Persistent[float] = na(float)
    lnSigSL: Persistent[float] = na(float)
    lnSigTP1: Persistent[float] = na(float)
    lnSigTP2: Persistent[float] = na(float)
    lnSigTP3: Persistent[float] = na(float)
    lnSigDir: Persistent[int] = 0
    lnTP1Hit: Persistent[bool] = False
    lnTP2Hit: Persistent[bool] = False
    lnTP3Hit: Persistent[bool] = False
    lnSLHit: Persistent[bool] = False
    lnSLLine: Persistent[Line] = na(Line)
    lnTP1Line: Persistent[Line] = na(Line)
    lnTP2Line: Persistent[Line] = na(Line)
    lnTP3Line: Persistent[Line] = na(Line)
    lnSLLabel: Persistent[Label] = na(Label)
    lnTP1Label: Persistent[Label] = na(Label)
    lnTP2Label: Persistent[Label] = na(Label)
    lnTP3Label: Persistent[Label] = na(Label)
    lnTrailSL: Persistent[float] = na(float)
    lnTrailLine: Persistent[Line] = na(Line)
    lnTrailLabel: Persistent[Label] = na(Label)
    lnFlattenDone: Persistent[bool] = False
    lnTradeCount: Persistent[int] = 0
    lnInsideBars: Persistent[int] = 0
    lnLastWasSL: Persistent[bool] = False
    lnLastDir: Persistent[int] = 0
    lnExitBar: Persistent[int] = 0
    lnCooldownDone: Persistent[bool] = False
    lnInsideStarted: Persistent[bool] = False

    lnDay: Series = f_dayKey(time, i_timezone)
    lnNewDay = lnDay != nz(lnDay[1], lnDay)
    lnSessionStart = inLnTrade and (not inLnTrade[1]) or (inLnTrade and lnNewDay)
    if lnSessionStart:
        lnFlattenDone = False
        lnTradeCount = 0
        lnInsideBars = 0
        lnLastWasSL = False
        lnLastDir = 0
        lnExitBar = 0
        lnCooldownDone = False
        lnInsideStarted = False
        lnORBHigh = na
        lnORBLow = na
        lnORBMid = na
        lnOrbBuilding = False
        lnOrbComplete = False
        lnOrbStartBar = na
        lnOrbHighBar = na
        lnOrbLowBar = na
        lnOrbStartTime = na
        lnOrbHighTime = na
        lnOrbLowTime = na
        lnSigFired = False
        lnBrkPending = False
        lnRetestDone = False
        lnBrkDir = 0
        lnBrkBar = 0
        if strategy.position_size == 0:
            lnSigDir = 0
        lnTP1Hit = False
        lnTP2Hit = False
        lnTP3Hit = False
        lnSLHit = False
        lnSigEntry = na
        lnSigSL = na
        lnSigTP1 = na
        lnSigTP2 = na
        lnSigTP3 = na
        lnTrailSL = na

        lnSLLine = na
        lnTP1Line = na
        lnTP2Line = na
        lnTP3Line = na
        lnSLLabel = na
        lnTP1Label = na
        lnTP2Label = na
        lnTP3Label = na
        lnTrailLine = na
        lnTrailLabel = na

    lnSessionEnd = not inLnTrade and inLnTrade[1]
    if lnSessionEnd and i_lnEnable:
        if array.size(lnOrbArray) > 0:
            for j in pine_range(0, array.size(lnOrbArray) - 1):
                _o = array.get(lnOrbArray, j)
                if na(_o.endBar):
                    _o.endBar = bar_index[1]
                    _o.endTime = time[1]
                    array.set(lnOrbArray, j, _o)

        if not na(lnSLLine):
            line.set_x2(lnSLLine, time)
        if not na(lnTP1Line):
            line.set_x2(lnTP1Line, time)
        if not na(lnTP2Line):
            line.set_x2(lnTP2Line, time)
        if not na(lnTP3Line):
            line.set_x2(lnTP3Line, time)
        lnSLLine = na
        lnTP1Line = na
        lnTP2Line = na
        lnTP3Line = na
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        elif strategy.position_size < 0:
            strategy.order('EOS', strategy.long, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        lnSessionJustEnded = True
        activeSession = 0
        lnSigDir = 0
    if i_lnEnable and inLnORB and (not lnOrbComplete):
        if not lnOrbBuilding:
            lnOrbStartBar = bar_index
            lnOrbStartTime = time
            lnOrbBuilding = True
        if na(lnORBHigh) or high > lnORBHigh:
            lnORBHigh = high
            lnOrbHighBar = bar_index
            lnOrbHighTime = time
        if na(lnORBLow) or low < lnORBLow:
            lnORBLow = low
            lnOrbLowBar = bar_index
            lnOrbLowTime = time

    if i_lnEnable and (not inLnORB) and lnOrbBuilding and (not lnOrbComplete) and (not na(lnORBHigh)):
        lnOrbComplete = True
        lnORBMid = (lnORBHigh + lnORBLow) / 2

        lnRangeAvg = f_updateRangeAvg(lnRangeHistory, lnORBHigh - lnORBLow, i_adaptTPLookback)
        hiLine__00000410__ = line.new(lnOrbHighTime, lnORBHigh, time, lnORBHigh, xloc=xloc.bar_time, color=i_lnHighColor, style=getLineStyle(), width=i_lnLineWidth)
        loLine__00000410__ = line.new(lnOrbLowTime, lnORBLow, time, lnORBLow, xloc=xloc.bar_time, color=i_lnLowColor, style=getLineStyle(), width=i_lnLineWidth)
        midLine__00000410__ = line.new(lnOrbStartTime, lnORBMid, time, lnORBMid, xloc=xloc.bar_time, color=i_lnMidColor, style=line.style_dotted, width=math.max(1, i_lnLineWidth - 1)) if i_lnShowMid else na
        hiLabel__00000410__ = label.new(time, lnORBHigh, 'LDN ORB H', xloc=xloc.bar_time, style=label.style_none, textcolor=i_lnHighColor, size=getLabelSize()) if showLabels else na
        loLabel__00000410__ = label.new(time, lnORBLow, 'LDN ORB L', xloc=xloc.bar_time, style=label.style_none, textcolor=i_lnLowColor, size=getLabelSize()) if showLabels else na
        midLabel__00000410__ = label.new(time, lnORBMid, 'LDN ORB M', xloc=xloc.bar_time, style=label.style_none, textcolor=i_lnMidColor, size=getLabelSize()) if showLabels and i_lnShowMid else na
        newOrb: orbData = orbData(lnORBHigh, lnORBLow, lnORBMid, lnOrbStartBar, lnOrbHighBar, lnOrbLowBar, na, lnOrbStartTime, lnOrbHighTime, lnOrbLowTime, na, hiLine__00000410__, loLine__00000410__, midLine__00000410__, hiLabel__00000410__, loLabel__00000410__, midLabel__00000410__)
        array.unshift(lnOrbArray, newOrb)
        if array.size(lnOrbArray) > i_daysToShow:
            old = array.pop(lnOrbArray)
            method_call('delete', old.hiLine)
            method_call('delete', old.loLine)
            method_call('delete', old.midLine)
            method_call('delete', old.hiLabel)
            method_call('delete', old.loLabel)
            method_call('delete', old.midLabel)

    if array.size(lnOrbArray) > 0:
        for i in pine_range(0, array.size(lnOrbArray) - 1):
            cur = array.get(lnOrbArray, i)
            _t2: int = time if na(cur.endTime) else cur.endTime

            method_call('set_x1', cur.hiLine, cur.hiTime)
            method_call('set_x2', cur.hiLine, _t2)
            method_call('set_x1', cur.loLine, cur.loTime)
            method_call('set_x2', cur.loLine, _t2)
            if i_lnShowMid and (not na(cur.midLine)):
                method_call('set_x1', cur.midLine, cur.startTime)
                method_call('set_x2', cur.midLine, _t2)

            if i == 0 and showLabels:
                method_call('set_x', cur.hiLabel, _t2)
                method_call('set_x', cur.loLabel, _t2)
                if i_lnShowMid and (not na(cur.midLabel)):
                    method_call('set_x', cur.midLabel, _t2)
            else:
                method_call('delete', cur.hiLabel)
                method_call('delete', cur.loLabel)
                if not na(cur.midLabel):
                    method_call('delete', cur.midLabel)
                cur.hiLabel = na
                cur.loLabel = na
                cur.midLabel = na

    _lnBuf = lnRearmEntryBuf if lnTradeCount > 0 and i_lnRearmEnable else lnEntryBuf
    lnCrossUp = close > lnORBHigh + _lnBuf and close[1] <= lnORBHigh + _lnBuf
    lnHighBreak = lnOrbComplete and inLnTrade and lnCrossUp
    lnCrossDn = close < lnORBLow - _lnBuf and close[1] >= lnORBLow - _lnBuf
    lnLowBreak = lnOrbComplete and inLnTrade and lnCrossDn
    lnLongSig: bool = False
    lnShortSig: bool = False

    if i_lnEnable and lnBrkPending and (bar_index > lnBrkBar) and (not lnSigFired):
        _isMidRetest = i_lnEntryMode == 'Retest Midpoint'
        _retestLvl = lnORBMid if _isMidRetest else lnORBHigh if lnBrkDir == 1 else lnORBLow
        if lnBrkDir == 1:
            if not lnRetestDone and low <= _retestLvl:
                lnRetestDone = True
            if lnRetestDone and close > lnORBHigh + _lnBuf:
                lnLongSig = True
                lnBrkPending = False
                lnRetestDone = False
            elif _isMidRetest and close < lnORBLow:
                lnBrkPending = False
                lnRetestDone = False
            elif not _isMidRetest and close <= lnORBHigh:
                lnBrkPending = False
        elif lnBrkDir == -1:
            if not lnRetestDone and high >= _retestLvl:
                lnRetestDone = True
            if lnRetestDone and close < lnORBLow - _lnBuf:
                lnShortSig = True
                lnBrkPending = False
                lnRetestDone = False
            elif _isMidRetest and close > lnORBHigh:
                lnBrkPending = False
                lnRetestDone = False
            elif not _isMidRetest and close >= lnORBLow:
                lnBrkPending = False
        if lnBrkPending and bar_index - lnBrkBar >= i_lnRetestTimeout:
            lnBrkPending = False
            lnRetestDone = False

    if i_lnEnable and lnOrbComplete and inLnTrade and (not lnSigFired) and (lnTradeCount < i_lnRearmMaxTrades or not i_lnRearmEnable):
        if lnHighBreak and (not lnBrkPending):
            if i_lnEntryMode == 'Breakout':
                lnLongSig = True
            else:
                lnBrkPending = True
                lnBrkDir = 1
                lnBrkBar = bar_index
        elif lnLowBreak and (not lnBrkPending):
            if i_lnEntryMode == 'Breakout':
                lnShortSig = True
            else:
                lnBrkPending = True
                lnBrkDir = -1
                lnBrkBar = bar_index

    if i_lnRearmEnable and lnTradeCount > 0 and (lnLastDir != 0):
        lnAllowL, lnAllowS = f_dirAllowed(lnLastDir, i_lnRearmDirection)
        if lnLongSig and (not lnAllowL):
            lnLongSig = False
        if lnShortSig and (not lnAllowS):
            lnShortSig = False

    if barstate.isconfirmed and lnLongSig and lnDayAllowed and (not inFlatWindow) and (i_lnDirection != 'Short Only') and (not lnSessionJustEnded):
        lnSigFired = True
        lnSigEntry = close
        lnSigDir = 1
        activeSession = 3
        lnTradeCount += 1
        lnSigSL = lnORBMid if i_lnSLMethod == 'Midpoint' else lnORBLow if i_lnSLMethod == 'Opposite Side' else close - i_lnSLPoints
        _risk = math.abs(lnSigEntry - lnSigSL)
        _lnOrbRange = lnORBHigh - lnORBLow if not na(lnORBHigh) and (not na(lnORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_lnTP1RR, _lnOrbRange, lnRangeAvg)
            _tp2rr: float = f_adaptTP(i_lnTP2RR, _lnOrbRange, lnRangeAvg)
            _tp3rr: float = f_adaptTP(i_lnTP3RR, _lnOrbRange, lnRangeAvg)
            lnSigTP1 = lnSigEntry + _risk * _tp1rr
            lnSigTP2 = lnSigEntry + _risk * _tp2rr
            lnSigTP3 = lnSigEntry + _risk * _tp3rr
        lnTrailSL = lnSigSL

        lnAdaptQty = f_adaptiveQty(_risk, i_lnContracts)
        _tp2on: bool = i_lnTP2Qty > 0 and i_lnTP2RR > 0
        _tp3on: bool = i_lnTP3Qty > 0 and i_lnTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(lnAdaptQty, i_lnTP2RR, i_lnTP3RR, _tp2on, _tp3on)
            _lnTp1Qty = _q1
            _lnTp2Qty = _q2
            _lnTp3Qty = _q3
        else:
            _lnTp1Qty = math.min(i_lnTP1Qty, i_lnContracts)
            _lnTp2Qty = math.min(i_lnTP2Qty, i_lnContracts - _lnTp1Qty) if i_lnTP2Qty > 0 else 0
            _lnTp3Qty = math.min(i_lnTP3Qty, i_lnContracts - _lnTp1Qty - _lnTp2Qty) if i_lnTP3Qty > 0 else i_lnContracts - _lnTp1Qty - _lnTp2Qty
        _lnEntryQty = lnAdaptQty if i_adaptEnable else i_lnContracts
        _jsonBuyDyn = '{"ticker": "' + syminfo.ticker + '", "action": "buy", "quantity": ' + string.tostring(_lnEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('LDN Long', strategy.long, qty=_lnEntryQty, alert_message=_jsonBuyDyn)
        if _risk > 0:
            strategy.exit('LDN TP1', from_entry='LDN Long', qty=_lnTp1Qty, limit=lnSigTP1, stop=lnSigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _lnTp2Qty > 0:
                strategy.exit('LDN TP2', from_entry='LDN Long', qty=_lnTp2Qty, limit=lnSigTP2, stop=lnSigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _lnTp3Qty > 0:
                strategy.exit('LDN TP3', from_entry='LDN Long', qty=_lnTp3Qty, limit=lnSigTP3, stop=lnSigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('LDN SL', from_entry='LDN Long', stop=lnSigSL, alert_message=_jsonExit)
        if i_lnShowSLTP:
            lnSLLine = line.new(time, lnSigSL, time, lnSigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            if not na(lnSigTP1):
                lnTP1Line = line.new(time, lnSigTP1, time, lnSigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
            if not na(lnSigTP2) and _lnTp2Qty > 0:
                lnTP2Line = line.new(time, lnSigTP2, time, lnSigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
            if not na(lnSigTP3) and _lnTp3Qty > 0:
                lnTP3Line = line.new(time, lnSigTP3, time, lnSigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))

    if barstate.isconfirmed and lnShortSig and lnDayAllowed and (not inFlatWindow) and (i_lnDirection != 'Long Only') and (not lnSessionJustEnded):
        lnSigFired = True
        lnSigEntry = close
        lnSigDir = -1
        activeSession = 3
        lnTradeCount += 1
        lnSigSL = lnORBMid if i_lnSLMethod == 'Midpoint' else lnORBHigh if i_lnSLMethod == 'Opposite Side' else close + i_lnSLPoints
        _risk = math.abs(lnSigSL - lnSigEntry)
        _lnOrbRange = lnORBHigh - lnORBLow if not na(lnORBHigh) and (not na(lnORBLow)) else 0.0
        if _risk > 0:
            _tp1rr: float = f_adaptTP(i_lnTP1RR, _lnOrbRange, lnRangeAvg)
            _tp2rr: float = f_adaptTP(i_lnTP2RR, _lnOrbRange, lnRangeAvg)
            _tp3rr: float = f_adaptTP(i_lnTP3RR, _lnOrbRange, lnRangeAvg)
            lnSigTP1 = lnSigEntry - _risk * _tp1rr
            lnSigTP2 = lnSigEntry - _risk * _tp2rr
            lnSigTP3 = lnSigEntry - _risk * _tp3rr
        lnTrailSL = lnSigSL

        lnAdaptQty = f_adaptiveQty(_risk, i_lnContracts)
        _tp2on: bool = i_lnTP2Qty > 0 and i_lnTP2RR > 0
        _tp3on: bool = i_lnTP3Qty > 0 and i_lnTP3RR > 0
        if i_adaptEnable:
            _q1, _q2, _q3 = f_adaptiveTpSplit(lnAdaptQty, i_lnTP2RR, i_lnTP3RR, _tp2on, _tp3on)
            _lnTp1Qty = _q1
            _lnTp2Qty = _q2
            _lnTp3Qty = _q3
        else:
            _lnTp1Qty = math.min(i_lnTP1Qty, i_lnContracts)
            _lnTp2Qty = math.min(i_lnTP2Qty, i_lnContracts - _lnTp1Qty) if i_lnTP2Qty > 0 else 0
            _lnTp3Qty = math.min(i_lnTP3Qty, i_lnContracts - _lnTp1Qty - _lnTp2Qty) if i_lnTP3Qty > 0 else i_lnContracts - _lnTp1Qty - _lnTp2Qty
        _lnEntryQty = lnAdaptQty if i_adaptEnable else i_lnContracts
        _jsonSellDyn = '{"ticker": "' + syminfo.ticker + '", "action": "sell", "quantity": ' + string.tostring(_lnEntryQty) + ', "signalPrice": ' + string.tostring(close) + '}'
        strategy.entry('LDN Short', strategy.short, qty=_lnEntryQty, alert_message=_jsonSellDyn)
        if _risk > 0:
            strategy.exit('LDN TP1', from_entry='LDN Short', qty=_lnTp1Qty, limit=lnSigTP1, stop=lnSigSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
            if _lnTp2Qty > 0:
                strategy.exit('LDN TP2', from_entry='LDN Short', qty=_lnTp2Qty, limit=lnSigTP2, stop=lnSigSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
            if _lnTp3Qty > 0:
                strategy.exit('LDN TP3', from_entry='LDN Short', qty=_lnTp3Qty, limit=lnSigTP3, stop=lnSigSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        else:
            strategy.exit('LDN SL', from_entry='LDN Short', stop=lnSigSL, alert_message=_jsonExit)
        if i_lnShowSLTP:
            lnSLLine = line.new(time, lnSigSL, time, lnSigSL, xloc=xloc.bar_time, color=i_slLineColor, style=slStyle, width=i_slLineWidth)
            if not na(lnSigTP1):
                lnTP1Line = line.new(time, lnSigTP1, time, lnSigTP1, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=i_tpLineWidth)
            if not na(lnSigTP2) and _lnTp2Qty > 0:
                lnTP2Line = line.new(time, lnSigTP2, time, lnSigTP2, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))
            if not na(lnSigTP3) and _lnTp3Qty > 0:
                lnTP3Line = line.new(time, lnSigTP3, time, lnSigTP3, xloc=xloc.bar_time, color=i_tpLineColor, style=tpStyle, width=math.max(1, i_tpLineWidth - 1))

    if i_lnTrailEnable and lnSigDir != 0 and (not lnSLHit) and (strategy.position_size != 0):
        _prevTrail = lnTrailSL
        lnTrailSL = calcTrail(lnSigDir, lnTrailSL, lnSigEntry, lnSigTP1, lnSigTP2, lnSigTP3, lnSigSL, i_lnTrailEnable)
        if lnTrailSL != _prevTrail:
            if lnSigDir == 1:
                strategy.exit('LDN TP1', from_entry='LDN Long', qty=_lnTp1Qty, limit=lnSigTP1, stop=lnTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _lnTp2Qty > 0:
                    strategy.exit('LDN TP2', from_entry='LDN Long', qty=_lnTp2Qty, limit=lnSigTP2, stop=lnTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _lnTp3Qty > 0:
                    strategy.exit('LDN TP3', from_entry='LDN Long', qty=_lnTp3Qty, limit=lnSigTP3, stop=lnTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
            else:
                strategy.exit('LDN TP1', from_entry='LDN Short', qty=_lnTp1Qty, limit=lnSigTP1, stop=lnTrailSL, comment_profit='TP1', comment_loss='SL', alert_message=_jsonExit)
                if _lnTp2Qty > 0:
                    strategy.exit('LDN TP2', from_entry='LDN Short', qty=_lnTp2Qty, limit=lnSigTP2, stop=lnTrailSL, comment_profit='TP2', comment_loss='SL', alert_message=_jsonExit)
                if _lnTp3Qty > 0:
                    strategy.exit('LDN TP3', from_entry='LDN Short', qty=_lnTp3Qty, limit=lnSigTP3, stop=lnTrailSL, comment_profit='TP3', comment_loss='SL', alert_message=_jsonExit)
        if i_lnTrailShowLine and lnTrailSL != lnSigSL:
            lnTrailLine = line.new(time[1], lnTrailSL, time, lnTrailSL, xloc=xloc.bar_time, color=i_trailColor, style=trailLineStyle, width=i_trailWidth)
            if na(lnTrailLabel):
                lnTrailLabel = label.new(time, lnTrailSL, 'TRAIL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_trailColor, size=getLabelSize()) if showLabels else na
            else:
                label.set_y(lnTrailLabel, lnTrailSL)

    if lnSigDir != 0 and i_lnShowSLTP:
        if not na(lnSLLine):
            line.set_x2(lnSLLine, time)
        if not na(lnSLLabel):
            label.set_x(lnSLLabel, time)
        if not na(lnTP1Line):
            line.set_x2(lnTP1Line, time)
        if not na(lnTP1Label):
            label.set_x(lnTP1Label, time)
        if not na(lnTP2Line):
            line.set_x2(lnTP2Line, time)
        if not na(lnTP2Label):
            label.set_x(lnTP2Label, time)
        if not na(lnTP3Line):
            line.set_x2(lnTP3Line, time)
        if not na(lnTP3Label):
            label.set_x(lnTP3Label, time)

        if not na(lnTrailLine):
            line.set_x2(lnTrailLine, time)
        if not na(lnTrailLabel):
            label.set_x(lnTrailLabel, time)

    if i_lnEnable and lnSigDir != 0 and (not lnSLHit):
        if lnSigDir == 1:
            if low <= lnTrailSL:
                lnSLHit = True
                lnLastWasSL = True
                lnLastDir = lnSigDir
                lnExitBar = bar_index
                lnCooldownDone = False
                lnInsideStarted = False
                lnInsideBars = 0
                lnSigDir = 0
                if not na(lnSLLine):
                    line.set_x2(lnSLLine, time)
                if not na(lnTP1Line):
                    line.set_x2(lnTP1Line, time)
                if not na(lnTP2Line):
                    line.set_x2(lnTP2Line, time)
                if not na(lnTP3Line):
                    line.set_x2(lnTP3Line, time)
                lnSLLine = na
                lnTP1Line = na
                lnTP2Line = na
                lnTP3Line = na
            else:
                if not lnTP1Hit and high >= lnSigTP1:
                    lnTP1Hit = True
                if not lnTP2Hit and high >= lnSigTP2:
                    lnTP2Hit = True
                if not lnTP3Hit and high >= lnSigTP3:
                    lnTP3Hit = True
        elif lnSigDir == -1:
            if high >= lnTrailSL:
                lnSLHit = True
                lnLastWasSL = True
                lnLastDir = lnSigDir
                lnExitBar = bar_index
                lnCooldownDone = False
                lnInsideStarted = False
                lnInsideBars = 0
                lnSigDir = 0
                if not na(lnSLLine):
                    line.set_x2(lnSLLine, time)
                if not na(lnTP1Line):
                    line.set_x2(lnTP1Line, time)
                if not na(lnTP2Line):
                    line.set_x2(lnTP2Line, time)
                if not na(lnTP3Line):
                    line.set_x2(lnTP3Line, time)
                lnSLLine = na
                lnTP1Line = na
                lnTP2Line = na
                lnTP3Line = na
            else:
                if not lnTP1Hit and low <= lnSigTP1:
                    lnTP1Hit = True
                if not lnTP2Hit and low <= lnSigTP2:
                    lnTP2Hit = True
                if not lnTP3Hit and low <= lnSigTP3:
                    lnTP3Hit = True

    if i_lnEnable and lnSigFired and (lnSigDir != 0) and (strategy.position_size == 0) and (strategy.position_size[1] != 0) and (not lnSLHit):
        lnLastWasSL = False
        lnLastDir = lnSigDir
        lnExitBar = bar_index
        lnCooldownDone = False
        lnInsideStarted = False
        lnInsideBars = 0
        lnSigDir = 0
        if not na(lnSLLine):
            line.set_x2(lnSLLine, time)
        if not na(lnTP1Line):
            line.set_x2(lnTP1Line, time)
        if not na(lnTP2Line):
            line.set_x2(lnTP2Line, time)
        if not na(lnTP3Line):
            line.set_x2(lnTP3Line, time)
        lnSLLine = na
        lnTP1Line = na
        lnTP2Line = na
        lnTP3Line = na

    plotshape(i_lnShowEntry and lnLongSig and lnDayAllowed and (not inFlatWindow) and (i_lnDirection != 'Short Only') and (not lnSessionJustEnded), title='LN Long', style=shape.triangleup, location=location.belowbar, color=color.new('#00FF00'), size=size.small, text='LDN LONG')
    plotshape(i_lnShowEntry and lnShortSig and lnDayAllowed and (not inFlatWindow) and (i_lnDirection != 'Long Only') and (not lnSessionJustEnded), title='LN Short', style=shape.triangledown, location=location.abovebar, color=color.new('#CC0000'), size=size.small, text='LDN SHORT')

    if flatWindowJustStarted and strategy.position_size != 0:
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('FLAT WINDOW', strategy.short, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        elif strategy.position_size < 0:
            strategy.order('FLAT WINDOW', strategy.long, qty=math.abs(strategy.position_size), alert_message=_jsonExit)
        nySessionJustEnded = True
        asSessionJustEnded = True
        lnSessionJustEnded = True
        activeSession = 0
        if not na(nySLLine):
            line.set_x2(nySLLine, time)
        if not na(nyTP1Line):
            line.set_x2(nyTP1Line, time)
        if not na(nyTP2Line):
            line.set_x2(nyTP2Line, time)
        if not na(nyTP3Line):
            line.set_x2(nyTP3Line, time)
        nySLLine = na
        nyTP1Line = na
        nyTP2Line = na
        nyTP3Line = na
        nySigDir = 0
        if not na(asSLLine):
            line.set_x2(asSLLine, time)
        if not na(asTP1Line):
            line.set_x2(asTP1Line, time)
        if not na(asTP2Line):
            line.set_x2(asTP2Line, time)
        if not na(asTP3Line):
            line.set_x2(asTP3Line, time)
        asSLLine = na
        asTP1Line = na
        asTP2Line = na
        asTP3Line = na
        asSigDir = 0
        if not na(lnSLLine):
            line.set_x2(lnSLLine, time)
        if not na(lnTP1Line):
            line.set_x2(lnTP1Line, time)
        if not na(lnTP2Line):
            line.set_x2(lnTP2Line, time)
        if not na(lnTP3Line):
            line.set_x2(lnTP3Line, time)
        lnSLLine = na
        lnTP1Line = na
        lnTP2Line = na
        lnTP3Line = na
        lnSigDir = 0

    _nyTPplot = nySigTP1 if i_nyEnable and nySigDir != 0 and i_lnShowSLTP else na
    _nySLplot = nySigSL if i_nyEnable and nySigDir != 0 and i_lnShowSLTP else na
    _asTPplot = asSigTP1 if i_asEnable and asSigDir != 0 and i_lnShowSLTP else na
    _asSLplot = asSigSL if i_asEnable and asSigDir != 0 and i_lnShowSLTP else na
    _lnTPplot = lnSigTP1 if i_lnEnable and lnSigDir != 0 and i_lnShowSLTP else na
    _lnSLplot = lnSigSL if i_lnEnable and lnSigDir != 0 and i_lnShowSLTP else na

    plot(_nyTPplot, 'NY TP', color=i_tpLineColor, style=plot.style_linebr, linewidth=2)
    plot(_nySLplot, 'NY SL', color=i_slLineColor, style=plot.style_linebr, linewidth=1)
    plot(_asTPplot, 'AS TP', color=i_tpLineColor, style=plot.style_linebr, linewidth=2)
    plot(_asSLplot, 'AS SL', color=i_slLineColor, style=plot.style_linebr, linewidth=1)
    plot(_lnTPplot, 'LN TP', color=i_tpLineColor, style=plot.style_linebr, linewidth=2)
    plot(_lnSLplot, 'LN SL', color=i_slLineColor, style=plot.style_linebr, linewidth=1)

    nySessHigh: Persistent[float] = na(float)
    nySessLow: Persistent[float] = na(float)
    nyPDH: Persistent[float] = na(float)
    nyPDL: Persistent[float] = na(float)
    nyPDHLine: Persistent[Line] = na(Line)
    nyPDLLine: Persistent[Line] = na(Line)
    nyPDHLabel: Persistent[Label] = na(Label)
    nyPDLLabel: Persistent[Label] = na(Label)

    if inNYTrade:
        if na(nySessHigh) or high > nySessHigh:
            nySessHigh = high
        if na(nySessLow) or low < nySessLow:
            nySessLow = low
    if nySessionEnd:
        nyPDH = nySessHigh
        nyPDL = nySessLow
        nySessHigh = na
        nySessLow = na
        if i_nyEnable and i_nyShowPD:
            if not na(nyPDHLine):
                line.delete(nyPDHLine)
                line.delete(nyPDLLine)
            if not na(nyPDHLabel):
                label.delete(nyPDHLabel)
                label.delete(nyPDLLabel)
            nyPDHLine = line.new(time, nyPDH, time, nyPDH, xloc=xloc.bar_time, color=i_nyPDColor, style=f_pdLineStyle(i_nyPDStyle), width=i_nyPDWidth)
            nyPDLLine = line.new(time, nyPDL, time, nyPDL, xloc=xloc.bar_time, color=i_nyPDColor, style=f_pdLineStyle(i_nyPDStyle), width=i_nyPDWidth)
            nyPDHLabel = label.new(time, nyPDH, 'NY PDH', xloc=xloc.bar_time, style=label.style_none, textcolor=i_nyPDColor, size=getLabelSize())
            nyPDLLabel = label.new(time, nyPDL, 'NY PDL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_nyPDColor, size=getLabelSize())
    if not na(nyPDHLine):
        line.set_x2(nyPDHLine, time)
        line.set_x2(nyPDLLine, time)
        label.set_x(nyPDHLabel, time)
        label.set_x(nyPDLLabel, time)

    asSessHigh: Persistent[float] = na(float)
    asSessLow: Persistent[float] = na(float)
    asPDH: Persistent[float] = na(float)
    asPDL: Persistent[float] = na(float)
    asPDHLine: Persistent[Line] = na(Line)
    asPDLLine: Persistent[Line] = na(Line)
    asPDHLabel: Persistent[Label] = na(Label)
    asPDLLabel: Persistent[Label] = na(Label)

    if inAsTrade:
        if na(asSessHigh) or high > asSessHigh:
            asSessHigh = high
        if na(asSessLow) or low < asSessLow:
            asSessLow = low
    if asSessionEnd:
        asPDH = asSessHigh
        asPDL = asSessLow
        asSessHigh = na
        asSessLow = na
        if i_asEnable and i_asShowPD:
            if not na(asPDHLine):
                line.delete(asPDHLine)
                line.delete(asPDLLine)
            if not na(asPDHLabel):
                label.delete(asPDHLabel)
                label.delete(asPDLLabel)
            asPDHLine = line.new(time, asPDH, time, asPDH, xloc=xloc.bar_time, color=i_asPDColor, style=f_pdLineStyle(i_asPDStyle), width=i_asPDWidth)
            asPDLLine = line.new(time, asPDL, time, asPDL, xloc=xloc.bar_time, color=i_asPDColor, style=f_pdLineStyle(i_asPDStyle), width=i_asPDWidth)
            asPDHLabel = label.new(time, asPDH, 'AS PDH', xloc=xloc.bar_time, style=label.style_none, textcolor=i_asPDColor, size=getLabelSize())
            asPDLLabel = label.new(time, asPDL, 'AS PDL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_asPDColor, size=getLabelSize())
    if not na(asPDHLine):
        line.set_x2(asPDHLine, time)
        line.set_x2(asPDLLine, time)
        label.set_x(asPDHLabel, time)
        label.set_x(asPDLLabel, time)

    lnSessHigh: Persistent[float] = na(float)
    lnSessLow: Persistent[float] = na(float)
    lnPDH: Persistent[float] = na(float)
    lnPDL: Persistent[float] = na(float)
    lnPDHLine: Persistent[Line] = na(Line)
    lnPDLLine: Persistent[Line] = na(Line)
    lnPDHLabel: Persistent[Label] = na(Label)
    lnPDLLabel: Persistent[Label] = na(Label)

    if inLnTrade:
        if na(lnSessHigh) or high > lnSessHigh:
            lnSessHigh = high
        if na(lnSessLow) or low < lnSessLow:
            lnSessLow = low
    if lnSessionEnd:
        lnPDH = lnSessHigh
        lnPDL = lnSessLow
        lnSessHigh = na
        lnSessLow = na
        if i_lnEnable and i_lnShowPD:
            if not na(lnPDHLine):
                line.delete(lnPDHLine)
                line.delete(lnPDLLine)
            if not na(lnPDHLabel):
                label.delete(lnPDHLabel)
                label.delete(lnPDLLabel)
            lnPDHLine = line.new(time, lnPDH, time, lnPDH, xloc=xloc.bar_time, color=i_lnPDColor, style=f_pdLineStyle(i_lnPDStyle), width=i_lnPDWidth)
            lnPDLLine = line.new(time, lnPDL, time, lnPDL, xloc=xloc.bar_time, color=i_lnPDColor, style=f_pdLineStyle(i_lnPDStyle), width=i_lnPDWidth)
            lnPDHLabel = label.new(time, lnPDH, 'LN PDH', xloc=xloc.bar_time, style=label.style_none, textcolor=i_lnPDColor, size=getLabelSize())
            lnPDLLabel = label.new(time, lnPDL, 'LN PDL', xloc=xloc.bar_time, style=label.style_none, textcolor=i_lnPDColor, size=getLabelSize())
    if not na(lnPDHLine):
        line.set_x2(lnPDHLine, time)
        line.set_x2(lnPDLLine, time)
        label.set_x(lnPDHLabel, time)
        label.set_x(lnPDLLabel, time)

    if i_nyRearmEnable and i_nyEnable and nyOrbComplete and inNYTrade and nySigFired and (nySigDir == 0) and (strategy.position_size == 0) and (nyTradeCount < i_nyRearmMaxTrades):
        if f_exitQualifies(nyLastWasSL, i_nyRearmAfter):
            if not nyCooldownDone:
                if bar_index - nyExitBar >= i_nyRearmCooldown:
                    nyCooldownDone = True

            if nyCooldownDone:
                if i_nyRearmBars == 0:
                    nySigFired = False
                    nyBrkPending = False
                    nyTP1Hit = False
                    nyTP2Hit = False
                    nyTP3Hit = False
                    nySLHit = False

                    if close > nyORBHigh + nyRearmEntryBuf:
                        nyCrossUp = True
                    if close < nyORBLow - nyRearmEntryBuf:
                        nyCrossDn = True
                else:
                    _nyGateMet: bool = False
                    if i_nyRearmGate == 'Inside ORB':
                        _nyGateMet = close >= nyORBLow + nyRearmEntryBuf and close <= nyORBHigh - nyRearmEntryBuf
                    elif i_nyRearmGate == 'Touch Midpoint':
                        _nyGateMet = low <= nyORBMid and high >= nyORBMid
                    elif i_nyRearmGate == 'Touch Opposite Side':
                        _nyGateMet = low <= nyORBLow or high >= nyORBHigh
                    else:
                        _nyGateMet = True
                    if not nyInsideStarted:
                        if _nyGateMet:
                            nyInsideStarted = True
                            nyInsideBars = 1
                    else:
                        nyInsideBars += 1
                    if nyInsideStarted and nyInsideBars >= i_nyRearmBars:
                        nySigFired = False
                        nyBrkPending = False
                        nyInsideBars = 0
                        nyInsideStarted = False
                        nyTP1Hit = False
                        nyTP2Hit = False
                        nyTP3Hit = False
                        nySLHit = False

    if i_asRearmEnable and i_asEnable and asOrbComplete and inAsTrade and asSigFired and (asSigDir == 0) and (strategy.position_size == 0) and (asTradeCount < i_asRearmMaxTrades):
        if f_exitQualifies(asLastWasSL, i_asRearmAfter):
            if not asCooldownDone:
                if bar_index - asExitBar >= i_asRearmCooldown:
                    asCooldownDone = True
            if asCooldownDone:
                if i_asRearmBars == 0:
                    asSigFired = False
                    asBrkPending = False
                    asTP1Hit = False
                    asTP2Hit = False
                    asTP3Hit = False
                    asSLHit = False
                    if close > asORBHigh + asRearmEntryBuf:
                        asCrossUp = True
                    if close < asORBLow - asRearmEntryBuf:
                        asCrossDn = True
                else:
                    _asGateMet: bool = False
                    if i_asRearmGate == 'Inside ORB':
                        _asGateMet = close >= asORBLow + asRearmEntryBuf and close <= asORBHigh - asRearmEntryBuf
                    elif i_asRearmGate == 'Touch Midpoint':
                        _asGateMet = low <= asORBMid and high >= asORBMid
                    elif i_asRearmGate == 'Touch Opposite Side':
                        _asGateMet = low <= asORBLow or high >= asORBHigh
                    else:
                        _asGateMet = True
                    if not asInsideStarted:
                        if _asGateMet:
                            asInsideStarted = True
                            asInsideBars = 1
                    else:
                        asInsideBars += 1
                    if asInsideStarted and asInsideBars >= i_asRearmBars:
                        asSigFired = False
                        asBrkPending = False
                        asInsideBars = 0
                        asInsideStarted = False
                        asTP1Hit = False
                        asTP2Hit = False
                        asTP3Hit = False
                        asSLHit = False

    if i_lnRearmEnable and i_lnEnable and lnOrbComplete and inLnTrade and lnSigFired and (lnSigDir == 0) and (strategy.position_size == 0) and (lnTradeCount < i_lnRearmMaxTrades):
        if f_exitQualifies(lnLastWasSL, i_lnRearmAfter):
            if not lnCooldownDone:
                if bar_index - lnExitBar >= i_lnRearmCooldown:
                    lnCooldownDone = True
            if lnCooldownDone:
                if i_lnRearmBars == 0:
                    lnSigFired = False
                    lnBrkPending = False
                    lnTP1Hit = False
                    lnTP2Hit = False
                    lnTP3Hit = False
                    lnSLHit = False
                    if close > lnORBHigh + lnRearmEntryBuf:
                        lnCrossUp = True
                    if close < lnORBLow - lnRearmEntryBuf:
                        lnCrossDn = True
                else:
                    _lnGateMet: bool = False
                    if i_lnRearmGate == 'Inside ORB':
                        _lnGateMet = close >= lnORBLow + lnRearmEntryBuf and close <= lnORBHigh - lnRearmEntryBuf
                    elif i_lnRearmGate == 'Touch Midpoint':
                        _lnGateMet = low <= lnORBMid and high >= lnORBMid
                    elif i_lnRearmGate == 'Touch Opposite Side':
                        _lnGateMet = low <= lnORBLow or high >= lnORBHigh
                    else:
                        _lnGateMet = True
                    if not lnInsideStarted:
                        if _lnGateMet:
                            lnInsideStarted = True
                            lnInsideBars = 1
                    else:
                        lnInsideBars += 1
                    if lnInsideStarted and lnInsideBars >= i_lnRearmBars:
                        lnSigFired = False
                        lnBrkPending = False
                        lnInsideBars = 0
                        lnInsideStarted = False
                        lnTP1Hit = False
                        lnTP2Hit = False
                        lnTP3Hit = False
                        lnSLHit = False

    _flatQty = math.abs(strategy.position_size)
    if i_nyEnable and i_nyFlattenEOD and (not inNYTrade) and (activeSession == 1) and (strategy.position_size != 0):
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=_flatQty, alert_message=_jsonExit)
        else:
            strategy.order('EOS', strategy.long, qty=_flatQty, alert_message=_jsonExit)
        nySessionJustEnded = True
        activeSession = 0
        nySigDir = 0
    if i_asEnable and i_asFlattenEOD and (not inAsTrade) and (activeSession == 2) and (strategy.position_size != 0):
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=_flatQty, alert_message=_jsonExit)
        else:
            strategy.order('EOS', strategy.long, qty=_flatQty, alert_message=_jsonExit)
        asSessionJustEnded = True
        activeSession = 0
        asSigDir = 0
    if i_lnEnable and i_lnFlattenEOD and (not inLnTrade) and (activeSession == 3) and (strategy.position_size != 0):
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=_flatQty, alert_message=_jsonExit)
        else:
            strategy.order('EOS', strategy.long, qty=_flatQty, alert_message=_jsonExit)
        nySessionJustEnded = True
        activeSession = 0
        lnSigDir = 0
    if strategy.position_size != 0 and (not inNYTrade) and (not inAsTrade) and (not inLnTrade):
        strategy.cancel_all()
        if strategy.position_size > 0:
            strategy.order('EOS', strategy.short, qty=_flatQty, alert_message=_jsonExit)
        else:
            strategy.order('EOS', strategy.long, qty=_flatQty, alert_message=_jsonExit)
        nySessionJustEnded = True
        activeSession = 0
        nySigDir = 0
        asSigDir = 0
        lnSigDir = 0

    _todayKey: PersistentSeries[int] = 0
    _currentKey = f_dayKey(time, i_timezone)
    _newDay = _currentKey != _todayKey
    if _newDay:
        _todayKey = _currentKey

    def f_sessionPnL(_prefix):
        _total: float = 0.0
        _wins: int = 0
        _count: int = 0
        _numTrades: int = strategy.closedtrades
        if _numTrades > 0:
            for i in pine_range(0, _numTrades - 1):
                _id: str = strategy.closedtrades.entry_id(i)
                if string.startswith(_id, _prefix):
                    _total += strategy.closedtrades.profit(i) + strategy.closedtrades.commission(i)
                    _count += 1
                    if strategy.closedtrades.profit(i) > 0:
                        _wins += 1
        return (_total, _count, _wins)

    def f_sessionPnLToday(_prefix, _dayKey):
        _total: float = 0.0
        _wins: int = 0
        _count: int = 0
        _numTrades: int = strategy.closedtrades
        if _numTrades > 0:
            for i in pine_range(0, _numTrades - 1):
                _id: str = strategy.closedtrades.entry_id(i)
                if string.startswith(_id, _prefix):
                    _exitTime: int = strategy.closedtrades.exit_time(i)
                    _exitDay: int = f_dayKey(_exitTime, i_timezone)
                    if _exitDay == _dayKey:
                        _total += strategy.closedtrades.profit(i) + strategy.closedtrades.commission(i)
                        _count += 1
                        if strategy.closedtrades.profit(i) > 0:
                            _wins += 1
        return (_total, _count, _wins)

    _prevDayKey: Persistent[int] = 0
    if _newDay:
        _prevDayKey = nz(_todayKey[1], 0)

    nyPnL, nyCount, nyWins = f_sessionPnL('NY')
    asPnL, asCount, asWins = f_sessionPnL('AS')
    lnPnL, lnCount, lnWins = f_sessionPnL('LDN')

    nyPnLT, nyCountT, nyWinsT = f_sessionPnLToday('NY', _todayKey)
    asPnLT, asCountT, asWinsT = f_sessionPnLToday('AS', _todayKey)
    lnPnLT, lnCountT, lnWinsT = f_sessionPnLToday('LDN', _todayKey)

    nyPnLY, nyCountY, nyWinsY = f_sessionPnLToday('NY', _prevDayKey)
    asPnLY, asCountY, asWinsY = f_sessionPnLToday('AS', _prevDayKey)
    lnPnLY, lnCountY, lnWinsY = f_sessionPnLToday('LDN', _prevDayKey)

    _isToday: bool = pnlDashMode == 'Today'
    _nyP: float = nyPnLT if _isToday else nyPnL
    _nyC: int = nyCountT if _isToday else nyCount
    _nyW: int = nyWinsT if _isToday else nyWins
    _asP: float = asPnLT if _isToday else asPnL
    _asC: int = asCountT if _isToday else asCount
    _asW: int = asWinsT if _isToday else asWins
    _lnP: float = lnPnLT if _isToday else lnPnL
    _lnC: int = lnCountT if _isToday else lnCount
    _lnW: int = lnWinsT if _isToday else lnWins
    _totalP: float = _nyP + _asP + _lnP
    _totalC: int = _nyC + _asC + _lnC
    _totalW: int = _nyW + _asW + _lnW

    _nyPY: float = nyPnLY
    _asPY: float = asPnLY
    _lnPY: float = lnPnLY
    _totalPY: float = _nyPY + _asPY + _lnPY

    _openPnL: float = strategy.openprofit

    def f_pnlStr(_val):
        _sign: str = '+' if _val >= 0 else ''
        return _sign + string.tostring(_val, '#,##0.00')

    def f_wrStr(_wins, _count):
        return string.tostring(math.round(_wins / _count * 100)) + '%' if _count > 0 else '—'

    if showPnlDash:
        __block_result_6__ = na
        __switch_1__ = pnlDashPosition
        if __switch_1__ == "Top Right":
            __block_result_6__ = position.top_right
        elif __switch_1__ == "Top Left":
            __block_result_6__ = position.top_left
        elif __switch_1__ == "Bottom Right":
            __block_result_6__ = position.bottom_right
        else:
            __block_result_6__ = position.bottom_left
        pnlPos = __block_result_6__
        pnlDash: Persistent[Table] = table.new(pnlPos, 3, 7, bgcolor=dashBgColor, border_width=1, border_color=dashBorderColor)
        if barstate.islast:
            _modeLabel: str = 'TODAY' if _isToday else 'ALL TIME'

            table.cell(pnlDash, 0, 0, '', text_color=dashHeaderText, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 1, 0, _modeLabel, text_color=dashHeaderText, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 2, 0, 'PREV DAY', text_color=dashHeaderText, text_size=getDashSize(), bgcolor=dashHeaderBg)

            table.cell(pnlDash, 0, 1, 'NY', text_color=i_nyHighColor, text_size=getDashSize())
            table.cell(pnlDash, 1, 1, f_pnlStr(_nyP), text_color=dashBullColor if _nyP >= 0 else dashBearColor, text_size=getDashSize())
            table.cell(pnlDash, 2, 1, f_pnlStr(_nyPY), text_color=dashBullColor if _nyPY >= 0 else dashBearColor, text_size=getDashSize())

            table.cell(pnlDash, 0, 2, 'ASIA', text_color=i_asHighColor, text_size=getDashSize())
            table.cell(pnlDash, 1, 2, f_pnlStr(_asP), text_color=dashBullColor if _asP >= 0 else dashBearColor, text_size=getDashSize())
            table.cell(pnlDash, 2, 2, f_pnlStr(_asPY), text_color=dashBullColor if _asPY >= 0 else dashBearColor, text_size=getDashSize())

            table.cell(pnlDash, 0, 3, 'LDN', text_color=i_lnHighColor, text_size=getDashSize())
            table.cell(pnlDash, 1, 3, f_pnlStr(_lnP), text_color=dashBullColor if _lnP >= 0 else dashBearColor, text_size=getDashSize())
            table.cell(pnlDash, 2, 3, f_pnlStr(_lnPY), text_color=dashBullColor if _lnPY >= 0 else dashBearColor, text_size=getDashSize())

            table.cell(pnlDash, 0, 4, 'OPEN', text_color=dashLabelColor, text_size=getDashSize())
            table.cell(pnlDash, 1, 4, f_pnlStr(_openPnL), text_color=dashBullColor if _openPnL >= 0 else dashBearColor, text_size=getDashSize())
            table.cell(pnlDash, 2, 4, '', text_size=getDashSize())

            table.cell(pnlDash, 0, 5, 'REALIZED', text_color=dashLabelColor, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 1, 5, f_pnlStr(_totalP), text_color=dashBullColor if _totalP >= 0 else dashBearColor, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 2, 5, f_pnlStr(_totalPY), text_color=dashBullColor if _totalPY >= 0 else dashBearColor, text_size=getDashSize(), bgcolor=dashHeaderBg)

            _netAll: float = _totalP + _openPnL
            table.cell(pnlDash, 0, 6, 'NET', text_color=dashLabelColor, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 1, 6, f_pnlStr(_netAll), text_color=dashBullColor if _netAll >= 0 else dashBearColor, text_size=getDashSize(), bgcolor=dashHeaderBg)
            table.cell(pnlDash, 2, 6, '', text_size=getDashSize(), bgcolor=dashHeaderBg)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
