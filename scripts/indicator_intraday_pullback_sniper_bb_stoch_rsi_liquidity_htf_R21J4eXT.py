"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, bgcolor,
    box, close, color, display, fill, format, high, input, label, line, location, low, math, na,
    nz, open, order, plot, plotshape, position, request, script, shape, size, string, syminfo, ta,
    table, text, time, timeframe, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table


@udt
class LiqSet:
    hiS: list[float] = na(list)
    hiSt: list[int] = na(list)
    hiN: list[float] = na(list)
    hiNt: list[int] = na(list)
    loS: list[float] = na(list)
    loSt: list[int] = na(list)
    loN: list[float] = na(list)
    loNt: list[int] = na(list)


g0: str = "0 · Read me first"
g1: str = "1 · Timeframes"
g2: str = "2 · Market Bias"
g3: str = "3 · Bollinger Bands (setup TF)"
g4: str = "4 · Stoch RSI (setup TF)"
g5: str = "5 · Swing Engine (feeds structure, labels and liquidity)"
g6: str = "6 · Entry timing"
g7: str = "7 · HTF Liquidity"
g8: str = "8 · Market Structure (display only)"
g9: str = "9 · Sessions"
g10: str = "10 · Timing"
g11: str = "11 · Signal markers"
g12: str = "12 · Status Table"
g13: str = "13 · Oscillator Pane"
g14: str = "14 · Liquidity Distance Band"


@script.indicator("Intraday Pullback Sniper (BB, Stoch RSI, Liquidity, HTF, Structure, Sessions)", "Pullback Sniper", overlay=False, max_lines_count=500, max_labels_count=500, max_boxes_count=250)
def main(
    note1=input.string("Put the chart on 5 minutes", "Chart timeframe", options=("Put the chart on 5 minutes",), group=g0, tooltip="The chart MUST run on the Setup Timeframe set below, which is 5 minutes by default.\n\nBollinger Bands, Stoch RSI and the setup detection are calculated on the chart timeframe. The entry structure is pulled from real lower-timeframe candles inside each chart candle, and the bias is pulled from above, so you see all three levels at once without switching charts.\n\nOther combinations are fine as long as you keep the rule: chart = setup timeframe, entry timeframe below it. For example a 15m chart with a 1H bias and 5m entry structure."),
    note2=input.string("Signal only, no trade management", "Scope", options=("Signal only, no trade management",), group=g0, tooltip="This indicator marks setups and entry signals. It deliberately does not draw stops, targets or risk-reward levels, and it does not simulate a position.\n\nSignals appear at the close of a chart candle, never intrabar. That is what keeps them free of repainting.\n\nThe script itself sits in its own pane below the chart, which is where the Stoch RSI is plotted. Everything that belongs to price is drawn onto the chart from there. One consequence is worth knowing: TradingView ties a table to the pane its script runs in, so the status table appears in the lower pane, not on the chart. Drag the divider between the two panes if it needs more room."),
    note3=input.string("What the labels on the chart mean", "Glossary", options=("What the labels on the chart mean",), group=g0, tooltip="SWING LABELS\nHH Higher High - a high above the previous high.\nHL Higher Low - a low above the previous low. HH plus HL is a rising structure.\nLH Lower High, LL Lower Low - the mirror image, a falling structure.\n\nSTRUCTURE BREAKS\nA break is a close beyond the last confirmed swing point.\nBOS Break of Structure - the break continues the direction that was already in place.\nCHOCH Change of Character - the break goes against it and is the first hint of a turn.\nMSB Market Structure Break - the umbrella term; every BOS and every CHOCH is one.\nThe timeframe is always appended, for example 'MSB BOS 1H'.\n\nLIQUIDITY LEVELS\nThe name has three parts: source, side, rank.\nPDH and PDL are yesterday's high and low.\nOtherwise the timeframe comes first, then the side, then the rank counted outwards from price.\nBSL, buy-side liquidity, sits above old highs: the buy orders of everyone who is short, plus the stops above.\nSSL, sell-side liquidity, sits below old lows.\n'15m BSL2' is therefore the second-nearest untaken buy-side pool of the 15-minute chart above the current price.\nWhen the same level is found on several enabled timeframes at once, they are merged into one line and the name lists every timeframe that produced it, for example '15m+1H BSL2' - the rank then counts across all timeframes together, not per timeframe.\n\nSIGNIFICANT AND SIMPLE\nUpper-case names on a thicker line are SIGNIFICANT levels: the market has already proven it had to respect them. For a low that means the high it came from was later exceeded by a higher high - buyers pushed past the previous peak, so the low behind them held. Mirrored for a high.\nLower-case names on a thinner line are SIMPLE levels: real turning points, but ones the market has not yet had to defend. They can still be hit, they just carry less weight.\nThe two are counted separately, so BSL1 and bsl1 can both exist at the same time.\nThe short form H2 and L2 can be chosen instead in the liquidity settings.\nRanking is by distance, not by age, so a level can move from H2 to H1 when the one in front of it is cleared.\n'swept' behind the name means price ran through the level and closed back on the old side - the orders resting there have been taken. Once a level has been swept it is kept on the chart for good, dimmed or in its side colour depending on the display settings, even if a nearer level would otherwise have pushed it out of the ranking.\n\nCONFLUENCE COUNTER\nThe seven abbreviations in the status table, and what each of them stands for.\nBIAS the higher-timeframe direction agrees.\nRSI the Stoch RSI was at its extreme within its lookback.\nBB the candle touched a band and closed back inside the half that faces it.\nSTR the structure of the entry timeframe has confirmed - Higher Low plus Higher High for a long, Lower High plus Lower Low for a short.\nLIQ a liquidity level was swept recently.\nOB price is sitting inside an order block or breaker of that side.\nSES one of the enabled sessions is open.\nOf these, BB and STR together with a running setup are the ones a signal actually requires. The other five are support: they can all be missing and a signal still appears, or all be present without one, because a signal also needs its conditions in the right order.\n\nMARKERS\nA small dot below or above a candle marks an armed setup. A larger dot marks a candle where every enabled condition was met. Below the candle means a long context, above it a short one.\nThere is deliberately no written buy or sell instruction: the dot tells you a condition is complete, not that this is the moment to enter."),
    note4=input.string("How to set up alerts", "Alerts", options=("How to set up alerts",), group=g0, tooltip="HOW TO SET AN ALERT\nRight-click the chart, Add alert, and under Condition pick this indicator by name. The second dropdown then lists everything it can fire on.\n\nFOR THE SIGNAL - the large dot\nPick 'Any alert() function call' and set the trigger to 'Once Per Bar Close'. One alert covers long and short, and the message is written by the indicator: symbol, direction, price, bias, setup direction, state of the entry structure, whether a sweep was present, and the session.\n\nIf you would rather have them apart, pick 'SNIPER LONG' or 'SNIPER SHORT' instead and create two alerts. The text is then fixed and short, but you can route each direction differently.\n\nEVERYTHING ELSE ON THE LIST\nLong Setup and Short Setup fire on the small dot. They come far more often than signals - set them separately or not at all, otherwise the one that matters drowns in the noise.\nBullish and Bearish Liquidity Sweep fire when a level is taken.\nBullish and Bearish BOS, CHOCH and MSB fire on structure breaks of the chart timeframe.\n\nALWAYS USE 'ONCE PER BAR CLOSE'\nThe indicator only evaluates at the close of a candle, so any other trigger cannot make an alert arrive earlier - it would only check more often for nothing. This is also what keeps the alert consistent with what you see on the chart."),
    biasTF=input.timeframe("15", "Bias Timeframe", group=g1, tooltip="Higher timeframe used only to decide the overall market direction. Nothing here triggers a signal by itself; it decides which direction is allowed when Strict Bias is on.\n\nRule of thumb: about three times the setup timeframe. On a 5m chart that is 15m."),
    setupTF=input.timeframe("5", "Setup Timeframe (must equal chart TF)", group=g1, tooltip="The timeframe the Bollinger Bands and the Stoch RSI are calculated on. Put your chart on this timeframe; the status table tells you if it does not match."),
    entryTF=input.timeframe("1", "Entry Timeframe (structure)", group=g1, tooltip="The lower timeframe whose swing structure times the entry. Its candles are read from inside each chart candle, so you get the finer structure without leaving the chart.\n\nIt must be lower than the chart timeframe. On a 5m chart 1m is the natural choice."),
    emaLen=input.int(200, "EMA Length", minval=1, group=g2, tooltip="Number of candles the average is built from, calculated on the bias timeframe. Price above it counts as bullish, below it as bearish.\n\n200 is the classic long-term setting and reacts slowly. Shorter values such as 50 flip more often and give the bias a shorter memory."),
    biasSrc=input.string("Both", "Bias source", options=("Both", "Structure", "EMA"), group=g2, tooltip="What decides whether the market counts as bullish or bearish.\n\nEMA: price above or below the moving average of the bias timeframe. Calm and slow, but an average is not a trend definition - after a sharp sell-off price needs a long time to climb back above it, so the turn is long over while this still says bearish.\n\nStructure: the trend state of the market structure on the bias timeframe - higher highs and higher lows against lower highs and lower lows. It flips at the CHOCH, which is what a change of character means. Turns early, but changes its mind more often in sideways phases.\n\nBoth: the two are combined and a third state appears when they disagree - the structure has already turned while price is still on the wrong side of the average. That state is shown separately instead of being hidden behind one of the two colours, so you do not go hunting for shorts in a market that has already turned up."),
    transMode=input.string("Offensive", "While the sources disagree", options=("Offensive", "Conservative"), group=g2, tooltip="What may be traded while the two sources disagree.\n\nOffensive: the direction the structure has turned to is allowed, the old one is blocked. This is where the early trades of a reversal sit, often the best ones of a move.\n\nConservative: both directions are blocked until the two agree again. Fewer signals, and you miss the turn itself.\n\nOnly has an effect with Strict HTF Bias switched on and the source set to Both."),
    strictBias=input.bool(True, "Strict HTF Bias (trade with bias only)", group=g2, tooltip="ON: long signals only in a bullish bias, short signals only in a bearish one. This is the safer setting and the default.\n\nOFF: the bias becomes information only and counter-trend signals are allowed."),
    showEma=input.bool(True, "Plot EMA", group=g2, inline="ema", tooltip="Draws the bias EMA on your chart.\n\nThis row: the checkbox switches the line on, the colour field sets its colour, the number its thickness in pixels."),
    emaCol=input.color(color.yellow, "", group=g2, inline="ema", tooltip="Draws the bias EMA on your chart.\n\nThis row: the checkbox switches the line on, the colour field sets its colour, the number its thickness in pixels."),
    emaWidth=input.int(2, "Width", minval=1, maxval=5, group=g2, inline="ema", tooltip="Draws the bias EMA on your chart.\n\nThis row: the checkbox switches the line on, the colour field sets its colour, the number its thickness in pixels."),
    bbLen=input.int(20, "Length", minval=2, group=g3, tooltip="Number of candles the middle line of the bands is averaged over.\n\nShorter values make the bands hug price and react quickly, longer ones make them smoother and slower. 20 is the standard setting."),
    bbMult=input.float(2.0, "Deviation", step=0.1, group=g3, tooltip="How far the outer bands sit from the middle line, measured in standard deviations of price.\n\nHigher values widen the bands, so price touches them less often and you get fewer but more extreme setups. 2.0 is the standard and covers roughly 95 percent of all candles."),
    bbSrc: Series[float] = input.source(close, "Source", group=g3, tooltip="Which price of each candle the bands are calculated from. Close is the standard and what almost every chart uses; the other options are for special cases."),
    rejZone=input.float(50, "Entry zone (% of band width)", minval=5, maxval=100, step=5, group=g3, tooltip="How far into the bands the candle may close and still count as a rejection, measured from the band it touched as a percentage of the full band width.\n\n50 means a long may only close in the lower half. Without this, one large candle that wicks the lower band and closes at the upper band would qualify as a long - entering at the top of the move.\n\n100 switches the limit off and restores the plain rule from the specification."),
    bbShow=input.bool(True, "Draw the bands", group=g3, tooltip="Switches the three band lines and the shading off without touching the logic.\n\nSetups, signals and the entry zone keep working exactly as before - the bands are simply not drawn. Useful once you rely on the markers and want the chart free of lines."),
    bbColBand=input.color(color.new(color.teal, 20), "Bands", group=g3, inline="bb1", tooltip="Appearance of the bands.\n\nThis row: colour of the outer bands, colour of the middle band, and line thickness in pixels."),
    bbColMid=input.color(color.new(color.orange, 20), "Middle", group=g3, inline="bb1", tooltip="Appearance of the bands.\n\nThis row: colour of the outer bands, colour of the middle band, and line thickness in pixels."),
    bbWidth=input.int(1, "Width", minval=1, maxval=5, group=g3, inline="bb1", tooltip="Appearance of the bands.\n\nThis row: colour of the outer bands, colour of the middle band, and line thickness in pixels."),
    bbShowFill=input.bool(True, "Fill", group=g3, inline="bb2", tooltip="Shades the area between the outer bands.\n\nThis row: the checkbox switches the shading on, the colour field sets its colour and transparency."),
    bbColFill=input.color(color.new(color.teal, 94), "", group=g3, inline="bb2", tooltip="Shades the area between the outer bands.\n\nThis row: the checkbox switches the shading on, the colour field sets its colour and transparency."),
    rsiLen=input.int(14, "RSI Length", minval=1, group=g4, tooltip="Number of candles the RSI is calculated over. The Stochastic is then applied on top of that RSI.\n\n14 is the standard. Shorter reacts faster and reaches the extremes more often, longer is calmer."),
    stoLen=input.int(14, "Stoch Length", minval=1, group=g4, tooltip="How far back the Stochastic looks to place the current RSI value on a scale from 0 to 100.\n\n0 means the RSI is at the lowest point of that window, 100 at the highest. This is what turns the RSI into an oscillator with clear extremes."),
    kSm=input.int(3, "K Smoothing", minval=1, group=g4, tooltip="Smoothing of the fast K line, in candles. K is the line the setup logic actually works with.\n\nHigher values give a calmer line and later signals, 1 switches the smoothing off and makes it jumpy."),
    dSm=input.int(3, "D Smoothing", minval=1, group=g4, tooltip="Smoothing of the slow D line, in candles. D is K smoothed once more and lags behind it.\n\nIt is not used by the setup logic. It only serves the eye: the pane shades the area between the two, so you can see the momentum direction at a glance."),
    osLvl=input.float(20, "Oversold", group=g4, tooltip="Below this level the market counts as oversold, which is one of the conditions for a long setup.\n\nLower values mean a deeper drop is required, so fewer but more extreme setups. 20 is the standard."),
    obLvl=input.float(80, "Overbought", group=g4, tooltip="Above this level the market counts as overbought, which is one of the conditions for a short setup.\n\nKeep it symmetrical to the oversold level unless you want one direction to be harder to reach than the other. 80 is the standard."),
    stochLB=input.int(5, "Extreme Lookback (bars)", minval=1, group=g4, tooltip="How many candles back the Stoch RSI may have reached its extreme. With 5 the oversold reading may be up to five candles old and the long setup still counts.\n\nHigher values give more setups because the rejection no longer has to happen right at the extreme."),
    swInt=input.int(2, "Internal lookback", minval=1, maxval=49, group=g5, tooltip="Lookback for the SHORT-term swing points, in candles to each side. This is the fast structure used for entry timing and for the internal structure labels.\n\n2 is the classic fractal: a high with two lower highs to its left and two to its right. It is the finest reading of a swing that still deserves the name, and it is the standard value for the short degree."),
    swMain=input.int(10, "Swing lookback", minval=2, maxval=100, group=g5, tooltip="Lookback for the LONG-term swing points, in candles to each side. This is the structure that drives the HH/HL/LH/LL labels and the main BOS/CHOCH labels.\n\n10 is the standard value for pivot detection and marks the turning points that shape the larger move, while the short degree above catches the detail inside it. Two degrees of movement is the oldest idea in chart analysis and predates every modern indicator.\n\nA swing is only confirmed this many candles after it formed, so the last 10 candles can never carry a label yet. That delay is the price of never repainting."),
    swDevMode=input.string("Off", "Deviation filter", options=("Off", "ATR", "Percent"), group=g5, tooltip="Optional extra filter: a minimum size a new leg must have before a swing point is accepted.\n\nOff by default, and deliberately so. The lookback and the backstep already define what counts as a swing, and there is no established value for this threshold - whatever number were put here would be invented rather than derived. Leave it off unless the chart tells you otherwise.\n\nATR: the minimum move measured in average true range, so it scales with the instrument and with volatility. Use this if a quiet sideways phase still produces more turning points than you want.\n\nPercent: the same idea measured in percent of price."),
    swDevVal=input.float(0.5, "Deviation value", minval=0.0, step=0.1, group=g5, tooltip="Only used when the deviation filter above is switched on: multiples of ATR in ATR mode, percent of price in Percent mode. 0.5 ATR keeps swings worth roughly half an average candle range.\n\nThis is a tuning knob for your own chart, not a standard value."),
    swBack=input.int(2, "Backstep (bars)", minval=0, maxval=50, group=g5, tooltip="Minimum number of candles between two accepted swing points.\n\nWithout it, two turning points can sit right next to each other and the structure becomes a zigzag of tiny steps. 2 is the classic value."),
    swAtrLen=input.int(14, "ATR Length", minval=1, group=g5, tooltip="Number of candles the Average True Range is measured over. The ATR is the average distance a candle travels, and it is used here as a yardstick that adapts to the instrument.\n\nIt feeds the optional deviation filter above and the spacing that keeps labels off the markers."),
    use1M=input.bool(True, "Use entry-timeframe structure", group=g6, tooltip="ON: the structure of the entry timeframe must confirm before a signal is given.\n\nOFF: only the Bollinger rejection on the setup timeframe is required, which gives many more but weaker signals."),
    entryMode=input.string("HH/HL + BB Rejection", "Entry Mode", options=("Structure Break", "HH/HL + BB Rejection", "Both"), group=g6, tooltip="Structure Break: signal as soon as price closes beyond the last confirmed swing high (long) or swing low (short) of the entry timeframe.\n\nHH/HL + BB Rejection: signal after a Higher Low plus Higher High (long) or Lower High plus Lower Low (short), followed by a fresh band touch that closes back inside. This is the main variant.\n\nBoth: demands the sequence AND the break AND the rejection. Very few signals, for testing only."),
    strLead=input.int(0, "Structure lead time (entry-TF bars)", minval=0, maxval=120, group=g6, tooltip="0 = strictly as specified: the HH/HL or LH/LL sequence must form AFTER the setup appears.\n\nAbove 0: a sequence that completed up to this many entry-timeframe candles before the setup is accepted as well. In practice the structure often forms while price is still approaching the band.\n\nThe order is preserved either way: a signal never comes before its structure is confirmed."),
    reqSweep=input.bool(False, "Require HTF liquidity sweep", group=g7, tooltip="OFF: sweeps are drawn and alerted but are not required for a signal. This is the default so the effect of the filter can be measured separately.\n\nON: a signal additionally requires price to have run through a higher-timeframe level and closed back on the other side."),
    liqKind=input.string("Significant and simple", "Liquidity kind", options=("Significant and simple", "Significant only"), group=g7, tooltip="Which of the two kinds of liquidity is drawn.\n\nA level is significant once the market has proven it was defended: for a low, the high it came from was later exceeded by a higher high - buyers pushed past the previous peak, so the low behind them had to hold. Mirrored for a high. Those are the pools that get hunted, and they are drawn with the thicker line and an upper-case name.\n\nA simple level is a genuine turning point the market has not yet had to defend. Thinner line, lower-case name.\n\nSignificant only is the default: fewer lines, and the ones that remain carry weight. Switch to both while you are studying how the two behave."),
    liqDepth=input.string("Only major swings", "Liquidity detail", options=("Only major swings", "Also smaller swings"), group=g7, tooltip="How closely the swing detection looks - this is about the SIZE of a turning point, not about its importance. Importance is the separate setting above.\n\nOnly major swings: a wick becomes a level only if it is the extreme of the whole window set below. Where several spikes sit close together, the deepest swallows its neighbours. Few, heavy levels.\n\nAlso smaller swings: every wick that reaches past the one candle either side of it becomes a level too. Nothing is swallowed any more, so the small wicks appear as well - stops rest at those too. Busier chart, more complete picture.\n\nBoth modes show untaken levels only, and only the nearest few per timeframe.\n\nThe numeric lookback below stays available for anyone who wants to sit between the two."),
    liqLen=input.int(10, "Liquidity lookback", minval=2, maxval=100, group=g7, tooltip="Lookback for the swing points that become liquidity levels, in candles to each side of the pivot. Same symmetric pivot rule as the structure, kept as its own setting so the two can be tuned apart: structure may stay coarse to keep the chart readable, while liquidity is allowed to be finer, because stop orders rest at every swing a trader can see - not only at the largest ones.\n\nApplied to every enabled timeframe, so 10 on the 15m chart means two and a half hours to each side there.\n\nOnly used while Liquidity detail above is set to 'Only major swings'. The 'Also smaller swings' mode ignores this value and uses the finest possible setting."),
    useChart=input.bool(True, "Chart TF Swings", group=g7, tooltip="Swing highs and lows of the timeframe you are looking at. Labelled with the chart timeframe as prefix, for example '5m BSL1' above price and '5m SSL1' below it.\n\nWithout this source the nearest levels are always at least one timeframe away, and the significant highs and lows of your own chart carry no marking at all.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    usePD=input.bool(True, "Previous Day High/Low", group=g7, tooltip="Yesterday's high and low as liquidity levels. Among the most watched levels in the market, and unlike the swing levels they are kept even after price trades beyond them, because they stay a daily reference.\n\nEach line starts at the candle that actually made that high or low, not at the start of the day."),
    use15m=input.bool(True, "15m Swings", group=g7, tooltip="Swing highs and lows of the 15-minute chart. This is the range that matters for a trade running over a handful of chart candles: close enough to be reached inside a session, far enough to hold real stop orders.\n\nLabelled with the prefix 15m, so '15m BSL1' is the nearest untaken buy-side pool of the 15-minute chart above price.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    use30m=input.bool(False, "30m Swings", group=g7, tooltip="Swing highs and lows of the 30-minute chart. A step coarser than 15m, reached less often but with more weight behind it.\n\nLabelled with the prefix 30m, so '30m BSL1' is the nearest untaken buy-side pool of the 30-minute chart above price.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    use1H=input.bool(True, "1H Swings", group=g7, tooltip="Swing highs and lows of the 1-hour chart.\n\nLabelled with the prefix 1H, so '1H BSL1' is the nearest untaken buy-side pool of the 1-hour chart above price.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    use4H=input.bool(False, "4H Swings", group=g7, tooltip="Swing highs and lows of the 4-hour chart. Big targets that are hit rarely, mostly useful as context.\n\nLabelled with the prefix 4H, so '4H BSL1' is the nearest untaken buy-side pool of the 4-hour chart above price.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    use1D=input.bool(False, "1D Swings", group=g7, tooltip="Swing highs and lows of the daily chart. The largest and least frequent levels this indicator offers, held over many sessions.\n\nLabelled with the prefix 1D, so '1D BSL1' is the nearest untaken buy-side pool of the daily chart above price. Different from Previous Day High/Low above: that setting is always exactly yesterday's high and low, this one is genuine swing pivots of the daily chart which can be many days old.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    use1W=input.bool(False, "1W Swings", group=g7, tooltip="Swing highs and lows of the weekly chart. The broadest context this indicator offers, months old in most cases.\n\nLabelled with the prefix 1W, so '1W BSL1' is the nearest untaken buy-side pool of the weekly chart above price.\n\nBSL means buy-side liquidity and sits ABOVE old highs - the buy orders of everyone who is short, plus the stops above. SSL means sell-side liquidity and sits BELOW old lows. The short form H and L can be chosen instead under Level naming."),
    lvlNaming=input.string("Buy-side / Sell-side", "Level naming", options=("Buy-side / Sell-side", "High / Low"), group=g7, tooltip="How the levels are named on the chart.\n\nBuy-side / Sell-side: the established terms. Liquidity resting above highs is buy-side liquidity, because it is the buy orders of everyone who is short plus the stops above. Below lows it is sell-side liquidity. '15m BSL2' is therefore the second-nearest untaken buy-side pool of the 15-minute chart.\n\nHigh / Low: the shorter form, '15m H2' and '15m L2'. Compact, but an H alone reads as 'high' and does not say that liquidity is sitting there.\n\nPDH and PDL keep their names either way, they are the standard abbreviations for yesterday's high and low."),
    nLvl=input.int(3, "Levels per direction (1-5)", minval=1, maxval=5, group=g7, tooltip="How many levels per direction are kept, counted outwards from price - and counted separately for each kind. With both kinds shown, 5 can therefore mean ten lines per direction.\n\nThe number appears in the label: BSL1 is the nearest untaken significant pool above price, BSL2 the next behind it. Lower-case bsl1 and ssl1 are the simple ones, numbered in their own series.\n\nThe rank goes by distance, not by age, so a level moves up once the one in front of it is cleared. When the same level shows up on several enabled timeframes at once they count as ONE level for this limit, not one per timeframe.\n\nThe cap of 5 exists to keep the total number of drawings under the limit TradingView allows per script."),
    sweepLB=input.int(10, "Sweep validity (chart bars)", minval=1, group=g7, tooltip="A sweep is price running through a level and closing back on the side it came from - a stop hunt rather than a real break.\n\nThis setting is how long a sweep counts as RECENT for the entry condition: with 10, price may have pierced the level up to ten candles ago and the sweep still counts towards a signal. A stop hunt from two hours ago says nothing about the current candle.\n\nIt does not affect the display. Once a level has been swept it keeps the word 'swept' in its label and stays on the chart for good, because the orders resting there have been taken and that does not undo itself when price walks away again - it no longer needs to stay inside the top ranking to remain visible."),
    liqPrice=input.string("Swept only", "Price in the label", options=("Off", "Swept only", "All levels"), group=g7, tooltip="Adds the price of the level behind its name.\n\nSwept only: just the levels that have already been swept. Those are the ones you tend to look up afterwards - where exactly was the stop hunt - while the untested levels stay short and readable.\n\nAll levels: every line carries its price. Useful when you are working the numbers, but it makes the labels noticeably wider, so they will step aside from each other more often.\n\nOff: names only."),
    sigGap=input.int(12, "Gap width (bars)", minval=4, maxval=60, group=g7, inline="sig", tooltip="Breaks the line of a significant level open near its origin and writes 'significant liquidity' into the gap, so the text sits on the line instead of next to it.\n\nThis row: the checkbox, and how wide the gap is in candles. Pine cannot measure how much room a text needs - it depends on your zoom - so the gap is set by hand. Too narrow and the text spills over the line ends, too wide and the line looks cut in half.\n\nOn a level that is still too short for a break, the line stays whole and the text is left out.\n\nSimple levels are never broken; the thinner line without text is what tells them apart."),
    sigLabel=input.bool(True, "Label significant levels", group=g7, inline="sig", tooltip="Breaks the line of a significant level open near its origin and writes 'significant liquidity' into the gap, so the text sits on the line instead of next to it.\n\nThis row: the checkbox, and how wide the gap is in candles. Pine cannot measure how much room a text needs - it depends on your zoom - so the gap is set by hand. Too narrow and the text spills over the line ends, too wide and the line looks cut in half.\n\nOn a level that is still too short for a break, the line stays whole and the text is left out.\n\nSimple levels are never broken; the thinner line without text is what tells them apart."),
    liqLblGap=input.float(0.3, "Min. label spacing (x ATR)", minval=0.0, maxval=3.0, step=0.1, group=g7, tooltip="Two levels can sit so close together that their names would be printed on top of each other. When the vertical gap between them is smaller than this, the second name is moved to the left along its own line instead, so both stay readable.\n\nMeasured in ATR so it scales with the instrument. Raise it if names still collide, lower it if they are pushed apart too eagerly."),
    showLiq=input.bool(True, "Draw liquidity levels", group=g7, tooltip="Draws the levels as horizontal lines, each labelled with source, direction and rank - for example '1H SSL1' for the nearest untaken sell-side pool of the 1-hour chart, or 'PDH' for yesterday's high.\n\nEach line starts at the candle whose high or low created the level and runs to the current candle, so you see where it came from and how long it has been holding."),
    sweptShow=input.bool(True, "Show swept levels", group=g7, inline="lqsw1", tooltip="What happens to a level after price has swept it - each part is set on its own, so any combination is possible.\n\nShow: the swept level stays on the chart for good, independent of whether it would still make the current ranking. Off hides it entirely.\n\nColour: Dimmed uses the muted colour next to it, Side colour keeps the pink or turquoise of its side. Dimmed together with a dotted style is the quiet variant - still there, no longer competing for attention."),
    sweptCol=input.string("Side colour", "Colour", options=("Side colour", "Dimmed"), group=g7, inline="lqsw1", tooltip="What happens to a level after price has swept it - each part is set on its own, so any combination is possible.\n\nShow: the swept level stays on the chart for good, independent of whether it would still make the current ranking. Off hides it entirely.\n\nColour: Dimmed uses the muted colour next to it, Side colour keeps the pink or turquoise of its side. Dimmed together with a dotted style is the quiet variant - still there, no longer competing for attention."),
    sweptEnd=input.string("Stop at the sweep", "Line ends", options=("Stop at the sweep", "Extend to now"), group=g7, tooltip="Where the line of a swept level stops.\n\nStop at the sweep: the line ends on the candle that took the level. It documents what happened without running on through the rest of the chart.\n\nExtend to now: the line keeps running to the current candle like an untaken level."),
    liqColHigh=input.color(color.new('#EF5350'), "High", group=g7, inline="lq1", tooltip="Colours of the liquidity levels.\n\nThis row: an untested pool ABOVE price, an untested pool BELOW price, and the colour a level takes once it has been swept.\n\nAbove price the pool is buy-side liquidity, labelled BSL: the buy orders of everyone who is short, plus the stops above old highs. Below price it is sell-side liquidity, labelled SSL. Under Level naming you can switch to the short form H and L instead.\n\nPine only accepts whole pixels for line thickness, so if the untested lines are still too heavy, reduce them through the transparency slider in these colour pickers rather than the width."),
    liqColLow=input.color(color.new('#26A69A'), "Low", group=g7, inline="lq1", tooltip="Colours of the liquidity levels.\n\nThis row: an untested pool ABOVE price, an untested pool BELOW price, and the colour a level takes once it has been swept.\n\nAbove price the pool is buy-side liquidity, labelled BSL: the buy orders of everyone who is short, plus the stops above old highs. Below price it is sell-side liquidity, labelled SSL. Under Level naming you can switch to the short form H and L instead.\n\nPine only accepts whole pixels for line thickness, so if the untested lines are still too heavy, reduce them through the transparency slider in these colour pickers rather than the width."),
    liqColSwept=input.color(color.new(color.gray, 35), "Swept", group=g7, inline="lq1", tooltip="Colours of the liquidity levels.\n\nThis row: an untested pool ABOVE price, an untested pool BELOW price, and the colour a level takes once it has been swept.\n\nAbove price the pool is buy-side liquidity, labelled BSL: the buy orders of everyone who is short, plus the stops above old highs. Below price it is sell-side liquidity, labelled SSL. Under Level naming you can switch to the short form H and L instead.\n\nPine only accepts whole pixels for line thickness, so if the untested lines are still too heavy, reduce them through the transparency slider in these colour pickers rather than the width."),
    liqStyleOpen=input.string("Solid", "Style untested", options=("Solid", "Dashed", "Dotted"), group=g7, inline="lq2", tooltip="Line style of a level that has not been swept yet. Solid stands out most, dotted stays quiet.\n\nThe style of a swept level is set separately below, so the two states can be told apart at a glance."),
    liqStyleSw=input.string("Dotted", "Style swept", options=("Solid", "Dashed", "Dotted"), group=g7, inline="lqsw2", tooltip="Appearance of a swept level.\n\nThis row: line style and line thickness. Dotted at one pixel with the dimmed colour is the most discreet combination; solid and thicker turns it into a marker you cannot miss."),
    sweptWidth=input.int(1, "Width swept", minval=1, maxval=5, group=g7, inline="lqsw2", tooltip="Appearance of a swept level.\n\nThis row: line style and line thickness. Dotted at one pixel with the dimmed colour is the most discreet combination; solid and thicker turns it into a marker you cannot miss."),
    sigWidth=input.int(2, "Width significant", minval=1, maxval=5, group=g7, inline="lqw", tooltip="Line thickness of the two kinds of liquidity.\n\nThis row: significant levels first, simple ones second. The difference in thickness is what tells them apart at a glance, so keep at least one pixel between the two values.\n\nPine only accepts whole pixels; if the lines are still too heavy, reduce them through the transparency of their colours instead."),
    liqWidth=input.int(1, "simple", minval=1, maxval=5, group=g7, inline="lqw", tooltip="Line thickness of the two kinds of liquidity.\n\nThis row: significant levels first, simple ones second. The difference in thickness is what tells them apart at a glance, so keep at least one pixel between the two values.\n\nPine only accepts whole pixels; if the lines are still too heavy, reduce them through the transparency of their colours instead."),
    liqTextSize=input.string("Normal", "Text size", options=("Tiny", "Small", "Normal", "Large"), group=g7, inline="lq3", tooltip="Size of the liquidity display.\n\nThis row: line thickness in whole pixels - Pine has no half steps - and the font size of the level names."),
    msOn=input.bool(True, "Show market structure", group=g8, tooltip="Master switch for the structure display. Each break is drawn as a horizontal line at the swing level that was broken, starting at the candle that formed it, with the text at the far end.\n\nThis is information only: it never triggers or blocks a signal.\n\nOnly timeframes equal to or higher than the chart are drawn. A smaller one would produce several breaks inside a single chart candle and they would stack into an unreadable pile."),
    msInternal=input.bool(False, "Show internal structure", group=g8, tooltip="Draws the breaks of the SHORT-term structure as well, using the internal lookback from the swing engine. Dashed by convention, so the fast rhythm inside the larger moves stays distinguishable.\n\nOff by default: on a choppy chart it roughly doubles the number of labels and they start overlapping. Switch it on when you are zoomed into a single move."),
    ms1On=input.bool(False, "Entry TF", group=g8, inline="tf1", tooltip="Structure breaks of the entry timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms1ColB=input.color(color.new('#80CBC4'), "", group=g8, inline="tf1", tooltip="Structure breaks of the entry timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms1ColS=input.color(color.new('#EF9A9A'), "", group=g8, inline="tf1", tooltip="Structure breaks of the entry timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms5On=input.bool(True, "Chart TF", group=g8, inline="tf5", tooltip="Structure breaks of the chart timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms5ColB=input.color(color.new('#26A69A'), "", group=g8, inline="tf5", tooltip="Structure breaks of the chart timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms5ColS=input.color(color.new('#EF5350'), "", group=g8, inline="tf5", tooltip="Structure breaks of the chart timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms15On=input.bool(False, "15m", group=g8, inline="tf15", tooltip="Structure breaks of the 15-minute timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms15ColB=input.color(color.new('#00BFA5'), "", group=g8, inline="tf15", tooltip="Structure breaks of the 15-minute timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms15ColS=input.color(color.new('#E53935'), "", group=g8, inline="tf15", tooltip="Structure breaks of the 15-minute timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break.\n\nOnly drawn while this timeframe is equal to or higher than the chart timeframe."),
    ms60On=input.bool(True, "1H", group=g8, inline="tf60", tooltip="Structure breaks of the 1-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms60ColB=input.color(color.new('#00E676'), "", group=g8, inline="tf60", tooltip="Structure breaks of the 1-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms60ColS=input.color(color.new('#FF1744'), "", group=g8, inline="tf60", tooltip="Structure breaks of the 1-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms240On=input.bool(True, "4H", group=g8, inline="tf240", tooltip="Structure breaks of the 4-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms240ColB=input.color(color.new('#00C853'), "", group=g8, inline="tf240", tooltip="Structure breaks of the 4-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    ms240ColS=input.color(color.new('#D50000'), "", group=g8, inline="tf240", tooltip="Structure breaks of the 4-hour timeframe.\n\nThis row: the checkbox switches them on, then the colour of a bullish and of a bearish break."),
    msShowIdle=input.bool(False, "Show structure while still neutral", group=g8, tooltip="ON: a break appears immediately in the neutral colour and switches to its timeframe colour once it supports an active setup.\n\nOFF: nothing is drawn while a break is still neutral; it only becomes visible when a setup in the same direction appears."),
    msColIdle=input.color(color.gray, "Colour while not relevant", group=g8, tooltip="Every structure break starts in this colour and only takes its timeframe colour once it supports the direction of an active setup."),
    msLblMode=input.string("MSB + type", "Label text", options=("MSB only", "BOS / CHOCH", "MSB + type"), group=g8, tooltip="What the text next to each structure line says.\n\nMSB stands for Market Structure Break and is the umbrella term: price closed beyond the last confirmed swing point.\n\nBOS, Break of Structure, means the break continued the direction that was already in place - a trend confirming itself.\n\nCHOCH, Change of Character, means it went the other way and is the first hint that control may be changing hands.\n\nMSB only: everything is labelled MSB.\nBOS / CHOCH: only the type.\nMSB + type: both, for example 'MSB CHOCH'.\n\nThe timeframe is always appended, so you can tell a 1H break from a 5m one at a glance."),
    msWidth=input.int(1, "Width", minval=1, maxval=5, group=g8, inline="ms2", tooltip="Appearance of the structure lines.\n\nThis row: line thickness, line style of the main structure, and font size of the text. The text sits on the chart background without a label box."),
    msStyle=input.string("Solid", "Style", options=("Solid", "Dashed", "Dotted"), group=g8, inline="ms2", tooltip="Appearance of the structure lines.\n\nThis row: line thickness, line style of the main structure, and font size of the text. The text sits on the chart background without a label box."),
    msTextSize=input.string("Normal", "Text size", options=("Tiny", "Small", "Normal", "Large"), group=g8, inline="ms2", tooltip="Appearance of the structure lines.\n\nThis row: line thickness, line style of the main structure, and font size of the text. The text sits on the chart background without a label box."),
    msExtend=input.int(5, "Extend line (bars)", minval=0, maxval=100, group=g8, tooltip="How many candles the structure line runs on past the candle that caused the break. The text sits at that end.\n\nLonger means the line stays visible while price moves on, but it also reaches further into recent candles."),
    msMax=input.int(60, "Max. structure drawings", minval=5, maxval=250, group=g8, tooltip="How many structure lines stay on the chart at once. When the limit is reached, the oldest one is removed.\n\nLower values keep the chart clean, higher ones let you scroll back through the history of breaks."),
    msPending=input.int(20, "Remove unused structure after (bars)", minval=0, maxval=500, group=g8, tooltip="A break that never became relevant to a setup is deleted after this many candles, because price has moved past it and it can no longer matter.\n\n0 keeps everything, including breaks that were never used - the chart fills up accordingly."),
    swDegree=input.string("Swing", "Label degree", options=("Swing", "Internal"), group=g8, tooltip="Which of the two degrees the HH/HL/LH/LL labels are taken from.\n\nInternal: the short lookback from group 5, 2 by default. Every turning point that stands out against the one candle either side of it gets a label, so you see the fine zigzag inside the larger move.\n\nSwing: the long lookback, 10 by default. Only the turning points that shape the bigger picture are labelled, the same ones the main structure lines are built on.\n\nThe structure lines are unaffected either way - this only changes which swings carry a text. Reading a chart in two degrees of movement is the point of having both."),
    obOn=input.bool(True, "Show order blocks", group=g8, tooltip="Marks the candle a structure break came from - the order block.\n\nWhen price closes beyond the last confirmed swing, the move that did it started somewhere. The last candle against that direction before the move is where the orders were placed: for an upward break the last down-close candle, for a downward break the last up-close one. The box spans that candle from wick to wick.\n\nIt keeps the size the candle gave it and never grows. Only the right edge runs on into the future, because the block stays a reference until price comes back to it.\n\nOrder blocks are drawn from the structure of the chart timeframe, using the same swing engine as everything else."),
    obColBull=input.color(color.new(color.new('#26A69A'), 85), "Bullish", group=g8, inline="ob1", tooltip="Colours of the order blocks.\n\nThis row: bullish blocks - the down-close candle an upward break came from - then bearish ones, then the border width.\n\nKept transparent by default: the block is a zone to watch, not a wall."),
    obColBear=input.color(color.new(color.new('#EF5350'), 85), "Bearish", group=g8, inline="ob1", tooltip="Colours of the order blocks.\n\nThis row: bullish blocks - the down-close candle an upward break came from - then bearish ones, then the border width.\n\nKept transparent by default: the block is a zone to watch, not a wall."),
    obBordW=input.int(1, "Border", minval=0, maxval=5, group=g8, inline="ob1", tooltip="Colours of the order blocks.\n\nThis row: bullish blocks - the down-close candle an upward break came from - then bearish ones, then the border width.\n\nKept transparent by default: the block is a zone to watch, not a wall."),
    obSource=input.string("Every break", "Blocks from", options=("Every break", "CHOCH only", "Defended breaks only"), group=g8, tooltip="Which structure breaks are allowed to leave an order block behind.\n\nEvery break: each BOS and each CHOCH produces one. Most blocks, most noise.\n\nCHOCH only: just the breaks that go against the prevailing direction - a change of character rather than a trend simply continuing.\n\nDefended breaks only: the swing that was broken had itself been confirmed earlier, by the same rule the liquidity levels use - the market had already shown it respected that level. This is the strictest filter and the closest equivalent to the significant liquidity."),
    obDisp=input.float(1.0, "Min. displacement (x ATR)", minval=0.0, maxval=10.0, step=0.1, group=g8, tooltip="How impulsive the move away from the block has to be, measured from the block to the close of the breaking candle in ATR.\n\nA break that crawls past a level says little; one that leaves it behind in a single stretch is what the concept means by displacement. 1.0 asks for roughly one average candle range.\n\n0 switches the filter off and lets every break through."),
    obBreaker=input.string("Turn into breaker", "When price closes through", options=("Turn into breaker", "Delete"), group=g8, tooltip="What happens when price closes through a block.\n\nTurn into breaker: the block changes sides instead of disappearing. A bullish block that failed to hold becomes a bearish zone - the buyers who entered there are now in the red and tend to sell at their entry when price returns. Size and position stay, only the colour changes. The breaker is removed once price closes through it as well.\n\nDelete: the block is simply gone once it has been used, which leaves only the untouched ones on the chart."),
    obColBullB=input.color(color.new(color.new('#42A5F5'), 85), "Breaker bull", group=g8, inline="ob3", tooltip="Colours of the breaker blocks.\n\nThis row: a bullish breaker - a failed bearish block - then a bearish one. Worth keeping them clearly apart from the order block colours above, since the whole point is that the zone has switched sides."),
    obColBearB=input.color(color.new(color.new('#FFA726'), 85), "bear", group=g8, inline="ob3", tooltip="Colours of the breaker blocks.\n\nThis row: a bullish breaker - a failed bearish block - then a bearish one. Worth keeping them clearly apart from the order block colours above, since the whole point is that the zone has switched sides."),
    obNameOn=input.bool(True, "Name the blocks", group=g8, inline="ob4", tooltip="Writes OB bull or OB bear into every order block, and Breaker bull or Breaker bear into every block that has changed sides, in the upper left corner inside the box.\n\nThe direction on a breaker is the one it works in NOW, after the switch: a bullish breaker is a zone to look for buyers in, a bearish one a zone to look for sellers in - the opposite of what the block was before it failed.\n\nWithout it the four states are told apart by colour alone, and a breaker looks like a fresh order block of the opposite direction - although they mean different things: one is an untouched zone, the other a failed one where somebody is sitting in the red.\n\nThe corner is the upper left so the text keeps clear of the opening range names, which sit at the left edge as well.\n\nThis row: the checkbox and the font size."),
    obNameSz=input.string("Small", "", options=("Tiny", "Small", "Normal", "Large"), group=g8, inline="ob4", tooltip="Writes OB bull or OB bear into every order block, and Breaker bull or Breaker bear into every block that has changed sides, in the upper left corner inside the box.\n\nThe direction on a breaker is the one it works in NOW, after the switch: a bullish breaker is a zone to look for buyers in, a bearish one a zone to look for sellers in - the opposite of what the block was before it failed.\n\nWithout it the four states are told apart by colour alone, and a breaker looks like a fresh order block of the opposite direction - although they mean different things: one is an untouched zone, the other a failed one where somebody is sitting in the red.\n\nThe corner is the upper left so the text keeps clear of the opening range names, which sit at the left edge as well.\n\nThis row: the checkbox and the font size."),
    obLook=input.int(10, "Search back (bars)", minval=1, maxval=40, group=g8, inline="ob2", tooltip="How the blocks are found and how many stay.\n\nThis row: how far back the search for the origin candle reaches, and how many blocks are kept before the oldest is removed.\n\nA short search finds only blocks close to the break, which is the strict reading. A longer one also catches breaks that took a while to build."),
    obKeep=input.int(8, "Keep blocks", minval=1, maxval=30, group=g8, inline="ob2", tooltip="How the blocks are found and how many stay.\n\nThis row: how far back the search for the origin candle reaches, and how many blocks are kept before the oldest is removed.\n\nA short search finds only blocks close to the break, which is the strict reading. A longer one also catches breaks that took a while to build."),
    swOn=input.bool(True, "Label swings (HH/HL/LH/LL)", group=g8, tooltip="Marks the confirmed swing points of the chart timeframe.\n\nHH, Higher High: a high above the previous high.\nHL, Higher Low: a low above the previous low. HH together with HL is a rising structure.\nLH, Lower High and LL, Lower Low: the mirror image, a falling structure.\n\nEach point is compared with the previous point of the same kind, so a high is measured against the last high and a low against the last low. Rising structure takes the up colour, falling structure the down colour.\n\nHighs and lows strictly alternate. A second high before the next low does not become its own point - it replaces the current one if it is more extreme, otherwise it is dropped. That is why not every visible turning point carries a label; which ones do depends on the degree set above."),
    swColUp=input.color(color.lime, "Higher", group=g8, inline="sw1", tooltip="Colours of the swing labels.\n\nThis row: Higher High and Higher Low, then Lower High and Lower Low. The colour follows the structure itself."),
    swColDn=input.color(color.red, "Lower", group=g8, inline="sw1", tooltip="Colours of the swing labels.\n\nThis row: Higher High and Higher Low, then Lower High and Lower Low. The colour follows the structure itself."),
    swTextSize=input.string("Normal", "Text size", options=("Tiny", "Small", "Normal", "Large"), group=g8, inline="sw2", tooltip="Size and amount of the swing labels.\n\nThis row: font size of the HH/HL/LH/LL text, and how many of these labels stay on the chart before the oldest are removed."),
    maxSwLbl=input.int(40, "Max. swing labels", minval=5, maxval=200, group=g8, inline="sw2", tooltip="Size and amount of the swing labels.\n\nThis row: font size of the HH/HL/LH/LL text, and how many of these labels stay on the chart before the oldest are removed."),
    useLDN=input.bool(True, "London", group=g9, inline="s1", tooltip="London session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in Europe/London local time. The default is the real exchange session, 08:00 to 16:30, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    sLDN=input.session("0800-1630:23456", "", group=g9, inline="s1", tooltip="London session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in Europe/London local time. The default is the real exchange session, 08:00 to 16:30, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    useNY=input.bool(True, "New York", group=g9, inline="s2", tooltip="New York session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in America/New_York local time. The default is the real exchange session, 09:30 to 16:00, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    sNY=input.session("0930-1600:23456", "", group=g9, inline="s2", tooltip="New York session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in America/New_York local time. The default is the real exchange session, 09:30 to 16:00, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    useAsia=input.bool(False, "Tokyo", group=g9, inline="s3", tooltip="Tokyo session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in Asia/Tokyo local time. The default is the real exchange session, 09:00 to 15:00, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    sAsia=input.session("0900-1500:23456", "", group=g9, inline="s3", tooltip="Tokyo session.\n\nThis row: the checkbox allows signals inside the window, the field defines it in Asia/Tokyo local time. The default is the real exchange session, 09:00 to 15:00, with the day mask 23456 limiting it to Monday through Friday.\n\nThat is a long stretch to trade. Rather than shortening it here, use Max. trading hours below - it cuts every session down to its opening hours at once."),
    maxHoursOn=input.bool(False, "Max. trading hours", group=g9, inline="mh", tooltip="Cuts every enabled session down to its first hours instead of you editing each window by hand.\n\nThe session fields below now hold the real exchange hours, which run far longer than most people want to trade. With this on, only the opening stretch counts - the part with the volume and the moves, before the midday lull.\n\nThis row: the checkbox, and how many hours from each session start are allowed. 2 keeps roughly the first two hours after the open. Fractions work, 1.5 gives ninety minutes.\n\nIt applies to the signal filter and to the session boxes alike, so what you see is what is allowed."),
    maxHours=input.float(2.0, "", minval=0.25, maxval=24.0, step=0.25, group=g9, inline="mh", tooltip="Cuts every enabled session down to its first hours instead of you editing each window by hand.\n\nThe session fields below now hold the real exchange hours, which run far longer than most people want to trade. With this on, only the opening stretch counts - the part with the volume and the moves, before the midday lull.\n\nThis row: the checkbox, and how many hours from each session start are allowed. 2 keeps roughly the first two hours after the open. Fractions work, 1.5 gives ninety minutes.\n\nIt applies to the signal filter and to the session boxes alike, so what you see is what is allowed."),
    sessNameOn=input.bool(True, "Name the boxes", group=g9, inline="sn", tooltip="Writes the name of the session into the bottom right corner of its box, so a box is identifiable without counting hours or checking the clock.\n\nThe name follows the lower right corner while the session runs, which means it also marks the lowest point the session has made so far.\n\nThis row: the checkbox and the font size."),
    sessNameSz=input.string("Small", "", options=("Tiny", "Small", "Normal", "Large"), group=g9, inline="sn", tooltip="Writes the name of the session into the bottom right corner of its box, so a box is identifiable without counting hours or checking the clock.\n\nThe name follows the lower right corner while the session runs, which means it also marks the lowest point the session has made so far.\n\nThis row: the checkbox and the font size."),
    sessBoxSpan=input.string("Tradeable window", "Boxes span", options=("Tradeable window", "Full session"), group=g9, tooltip="What the session boxes are drawn around.\n\nTradeable window: only the part that Max. trading hours leaves open. The frame then shows exactly where a signal may appear.\n\nFull session: the complete exchange hours from the fields above, regardless of the limiter. The frame becomes pure context - you see the whole session and its high and low, while signals are still restricted to the opening hours.\n\nThe signal filter itself is not affected by this setting, only the drawing."),
    sessShow=input.bool(False, "Show sessions in chart", group=g9, tooltip="Draws each enabled session as a box on the price chart, from its first candle to its last, sized to the high and low the session made.\n\nThat frame is worth having on its own: the high and low of a session are among the most watched levels of the day, and you can see at a glance whether the current move is still inside the range of its session or has already left it."),
    sessColL=input.color(color.new('#2962FF'), "London", group=g9, inline="sb1", tooltip="Colour of each session box.\n\nThis row: London, New York, Tokyo. The transparency of the fill and of the border is set separately below, so the same hue can be used quietly in the background and clearly on the frame."),
    sessColN=input.color(color.new('#FF9800'), "New York", group=g9, inline="sb1", tooltip="Colour of each session box.\n\nThis row: London, New York, Tokyo. The transparency of the fill and of the border is set separately below, so the same hue can be used quietly in the background and clearly on the frame."),
    sessColA=input.color(color.new('#AB47BC'), "Tokyo", group=g9, inline="sb1", tooltip="Colour of each session box.\n\nThis row: London, New York, Tokyo. The transparency of the fill and of the border is set separately below, so the same hue can be used quietly in the background and clearly on the frame."),
    sessFillTr=input.int(86, "Fill transp.", minval=0, maxval=100, group=g9, inline="sb2", tooltip="How present the session boxes are.\n\nThis row: transparency of the fill and of the border, each from 0 for solid to 100 for invisible.\n\nThe session box is deliberately the stronger of the two frames. What should catch the eye first is the range the session traded in; the opening ranges inside it are the second layer and are set fainter. If you turn these values down further, lift the ORB colours with them or the two will compete."),
    sessLineTr=input.int(45, "Border transp.", minval=0, maxval=100, group=g9, inline="sb2", tooltip="How present the session boxes are.\n\nThis row: transparency of the fill and of the border, each from 0 for solid to 100 for invisible.\n\nThe session box is deliberately the stronger of the two frames. What should catch the eye first is the range the session traded in; the opening ranges inside it are the second layer and are set fainter. If you turn these values down further, lift the ORB colours with them or the two will compete."),
    sessBordW=input.int(1, "Border width", minval=1, maxval=5, group=g9, inline="sb3", tooltip="Appearance and amount of the boxes.\n\nThis row: thickness of the border in pixels, and how many past sessions stay on the chart per session. Older boxes are removed automatically."),
    sessKeep=input.int(5, "Keep sessions", minval=1, maxval=20, group=g9, inline="sb3", tooltip="Appearance and amount of the boxes.\n\nThis row: thickness of the border in pixels, and how many past sessions stay on the chart per session. Older boxes are removed automatically."),
    orbOn=input.bool(False, "Paint 5m- and 15m-ORB (Opening-Range-Breakout-Block) at session start", group=g9, tooltip="Draws the opening range of each enabled session: a box from the top wick to the bottom wick of the first five minutes after the open, and a second one covering the first fifteen minutes. Both grow to the right for as long as the session runs.\n\nThe opening range is where the session decides its direction. Price leaving it is the classic breakout trigger, and the two boxes let you see the fast and the slower version of that range at once.\n\nAlways good to wait for volume to build and for confirmation before entering a trade.\n\nThe height of each box is fixed once its minutes are over - a box shows the range of the opening candles and nothing else. The full range of the whole session is what the session box already shows.\n\nThe ranges are measured in real minutes, so they stay correct on any chart timeframe.\n\nThe boxes run to the right until the session ends, or until the Max. trading hours window closes if that limiter is switched on."),
    orbLDN=input.bool(True, "London", group=g9, inline="orb1", tooltip="Which sessions get an opening range box.\n\nThis row: London, New York, Tokyo. Each can be switched on its own, so you can watch the open you actually trade without the others cluttering the chart.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbNY=input.bool(True, "New York", group=g9, inline="orb1", tooltip="Which sessions get an opening range box.\n\nThis row: London, New York, Tokyo. Each can be switched on its own, so you can watch the open you actually trade without the others cluttering the chart.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbAsia=input.bool(True, "Tokyo", group=g9, inline="orb1", tooltip="Which sessions get an opening range box.\n\nThis row: London, New York, Tokyo. Each can be switched on its own, so you can watch the open you actually trade without the others cluttering the chart.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orb5On=input.bool(True, "5m box", group=g9, inline="orbb", tooltip="Which of the two opening ranges is drawn.\n\nThis row: the five minute range and the fifteen minute one, each on its own. The 5m box is the tighter one and the more common breakout trigger; the 15m box gives the wider frame the session opened in.\n\nWith only one of them switched on, its name moves to the lower left corner of its own box - there is nothing left to avoid.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orb15On=input.bool(True, "15m box", group=g9, inline="orbb", tooltip="Which of the two opening ranges is drawn.\n\nThis row: the five minute range and the fifteen minute one, each on its own. The 5m box is the tighter one and the more common breakout trigger; the 15m box gives the wider frame the session opened in.\n\nWith only one of them switched on, its name moves to the lower left corner of its own box - there is nothing left to avoid.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbCol5=input.color(color.new(color.new('#FFFFFF'), 90), "5m", group=g9, inline="orb2", tooltip="Colours of the two opening range boxes.\n\nThis row: the five minute range first, the fifteen minute one second, then the border width.\n\nBoth are set fainter than the session box on purpose. The session range should register first, the opening ranges inside it second - they answer a different question: not where the session traded, but where it started.\n\nThe defaults are neutral greys rather than a colour. An opening range is drawn INSIDE a session box, and the three sessions carry three different hues - any coloured default would clash with one of them. Neutral reads as an overlay over blue, orange and purple alike. The border is derived from the fill, so it stays a step behind the session frame.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbCol15=input.color(color.new(color.new('#B0BEC5'), 93), "15m", group=g9, inline="orb2", tooltip="Colours of the two opening range boxes.\n\nThis row: the five minute range first, the fifteen minute one second, then the border width.\n\nBoth are set fainter than the session box on purpose. The session range should register first, the opening ranges inside it second - they answer a different question: not where the session traded, but where it started.\n\nThe defaults are neutral greys rather than a colour. An opening range is drawn INSIDE a session box, and the three sessions carry three different hues - any coloured default would clash with one of them. Neutral reads as an overlay over blue, orange and purple alike. The border is derived from the fill, so it stays a step behind the session frame.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbNameOn=input.bool(True, "Name the ORB boxes", group=g9, inline="orb3", tooltip="Writes 5m-ORB and 15m-ORB into each opening range box, one candle inside the left border and clear of the top and bottom ones.\n\nThe 15m range contains the 5m one, so both names would land in the same corner. The 15m name goes into whichever strip of its box the 5m box leaves free - above it or below it, whichever is taller - and the 5m name to the opposite end of its own box, so the two never overwrite each other.\n\nThis row: the checkbox and the font size.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbNameSz=input.string("Small", "", options=("Tiny", "Small", "Normal", "Large"), group=g9, inline="orb3", tooltip="Writes 5m-ORB and 15m-ORB into each opening range box, one candle inside the left border and clear of the top and bottom ones.\n\nThe 15m range contains the 5m one, so both names would land in the same corner. The 15m name goes into whichever strip of its box the 5m box leaves free - above it or below it, whichever is taller - and the 5m name to the opposite end of its own box, so the two never overwrite each other.\n\nThis row: the checkbox and the font size.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    orbBordW=input.int(1, "Border", minval=0, maxval=5, group=g9, inline="orb2", tooltip="Colours of the two opening range boxes.\n\nThis row: the five minute range first, the fifteen minute one second, then the border width.\n\nBoth are set fainter than the session box on purpose. The session range should register first, the opening ranges inside it second - they answer a different question: not where the session traded, but where it started.\n\nThe defaults are neutral greys rather than a colour. An opening range is drawn INSIDE a session box, and the three sessions carry three different hues - any coloured default would clash with one of them. Neutral reads as an overlay over blue, orange and purple alike. The border is derived from the fill, so it stays a step behind the session frame.\n\nAlways good to wait for volume to build and for confirmation before entering a trade."),
    setupExp=input.int(30, "Setup expiration (entry-TF bars)", minval=1, group=g10, tooltip="How long a setup stays valid while waiting for its signal. Converted into chart bars: 30 / 5 = 6 chart bars, and since the signal is only checked from the bar after the setup, 5 of them are usable.\n\nThe specification says 5, which is a single chart bar and expires before anything can be evaluated."),
    cooldown=input.int(3, "Cooldown after a signal (entry-TF bars)", minval=0, group=g10, tooltip="Pause after a signal before the next one may be given, counted in candles of the entry timeframe.\n\nWithout it, a single move can produce several signals in a row, because the conditions often stay true for a few candles. 0 switches the pause off."),
    markerWhen=input.string("At candle close", "Markers appear", options=("At candle close", "While the candle forms"), group=g11, tooltip="When a marker is allowed to appear.\n\nAt candle close: the marker is drawn once the candle is finished, which is the only moment the condition can actually be judged - the setup needs a CLOSE back inside the band, and there is no close before the candle ends. This is also the moment the alert fires, so chart and alert agree.\n\nWhile the candle forms: the marker already appears as soon as the current price would satisfy the condition. That gives you up to a full candle of warning, but it is provisional - if price moves back to the band before the close, the marker disappears again and there was no signal. Nothing is faster this way, only earlier and less certain.\n\nOn historical candles both settings look identical. The difference only exists on the candle that is still running."),
    zoneOn=input.bool(False, "Setups only in a zone of interest", group=g11, tooltip="Only arms a setup when it happens somewhere that gives it a reason beyond the band touch itself.\n\nWithout this, every band rejection with an oversold or overbought reading arms a setup, wherever it happens. With it, the candle additionally has to sit in one of the zones ticked below.\n\nThis is the strongest filter in the whole indicator - it removes setups, and with them the signals that would have followed. Switch it on once you have seen how many setups you get without it, so you can judge what it takes away."),
    zoneOB=input.bool(True, "Order block", group=g11, inline="zn", tooltip="The zones a setup may sit in. They work as OR - one of them is enough, so more ticks mean MORE setups, not fewer. Untick everything here and in the row below and nothing gets through at all.\n\nThis row: Order block - price is inside an untouched block of that side, the classic place to expect a bounce. Breaker - price is inside a block that changed sides, and the setup points the way the breaker now works: long in a bullish breaker, short in a bearish one. Significant sweep - a level the market had already defended was just run through and reclaimed; simple levels do not count, they are taken too often to mean much."),
    zoneBrk=input.bool(True, "Breaker", group=g11, inline="zn", tooltip="The zones a setup may sit in. They work as OR - one of them is enough, so more ticks mean MORE setups, not fewer. Untick everything here and in the row below and nothing gets through at all.\n\nThis row: Order block - price is inside an untouched block of that side, the classic place to expect a bounce. Breaker - price is inside a block that changed sides, and the setup points the way the breaker now works: long in a bullish breaker, short in a bearish one. Significant sweep - a level the market had already defended was just run through and reclaimed; simple levels do not count, they are taken too often to mean much."),
    zoneSweep=input.bool(True, "Significant sweep", group=g11, inline="zn", tooltip="The zones a setup may sit in. They work as OR - one of them is enough, so more ticks mean MORE setups, not fewer. Untick everything here and in the row below and nothing gets through at all.\n\nThis row: Order block - price is inside an untouched block of that side, the classic place to expect a bounce. Breaker - price is inside a block that changed sides, and the setup points the way the breaker now works: long in a bullish breaker, short in a bearish one. Significant sweep - a level the market had already defended was just run through and reclaimed; simple levels do not count, they are taken too often to mean much."),
    zoneStr=input.bool(True, "Fresh break", group=g11, inline="zn2", tooltip="Three more zones, on the same OR basis as the row above.\n\nThis row: Fresh break - a structure break of the chart timeframe happened within the last few candles and points the same way, so this is the pullback to a level that has just given way. Session high/low - the candle touches the extreme the running session has made so far. Opening range - the candle touches an edge of the 5m or 15m opening range of an enabled session; those ranges are measured whether or not the boxes are drawn."),
    zoneSess=input.bool(True, "Session high/low", group=g11, inline="zn2", tooltip="Three more zones, on the same OR basis as the row above.\n\nThis row: Fresh break - a structure break of the chart timeframe happened within the last few candles and points the same way, so this is the pullback to a level that has just given way. Session high/low - the candle touches the extreme the running session has made so far. Opening range - the candle touches an edge of the 5m or 15m opening range of an enabled session; those ranges are measured whether or not the boxes are drawn."),
    zoneORB=input.bool(False, "Opening range", group=g11, inline="zn2", tooltip="Three more zones, on the same OR basis as the row above.\n\nThis row: Fresh break - a structure break of the chart timeframe happened within the last few candles and points the same way, so this is the pullback to a level that has just given way. Session high/low - the candle touches the extreme the running session has made so far. Opening range - the candle touches an edge of the 5m or 15m opening range of an enabled session; those ranges are measured whether or not the boxes are drawn."),
    zoneTol=input.float(0.3, "Zone tolerance (x ATR)", minval=0.0, maxval=3.0, step=0.1, group=g11, inline="zn3", tooltip="How close the candle has to come to a level for it to count as touched, in ATR.\n\nApplies to the session extreme and to the opening range edges - a level is rarely hit to the tick, and demanding that would make those two zones almost never fire.\n\nThis row: the tolerance, and how many candles a structure break stays fresh for."),
    zoneStrBars=input.int(10, "Break stays fresh (bars)", minval=1, maxval=100, group=g11, inline="zn3", tooltip="How close the candle has to come to a level for it to count as touched, in ATR.\n\nApplies to the session extreme and to the opening range edges - a level is rarely hit to the tick, and demanding that would make those two zones almost never fire.\n\nThis row: the tolerance, and how many candles a structure break stays fresh for."),
    zoneBB=input.bool(False, "Bollinger band alone", group=g11, tooltip="Lets the Bollinger band alone count as a zone.\n\nEvery setup already requires a band touch, so ticking this makes the filter let everything through again. It is there to park the filter without unticking the six zones above."),
    showSetup=input.bool(True, "Draw setup markers", group=g11, inline="st1", tooltip="Circles marking every candle where a setup was armed, even if no signal followed.\n\nThis row: the checkbox switches them on, then the colour of the long marker below the candle and of the short marker above it."),
    setupColL=input.color(color.new(color.green, 40), "", group=g11, inline="st1", tooltip="Circles marking every candle where a setup was armed, even if no signal followed.\n\nThis row: the checkbox switches them on, then the colour of the long marker below the candle and of the short marker above it."),
    setupColS=input.color(color.new(color.red, 40), "", group=g11, inline="st1", tooltip="Circles marking every candle where a setup was armed, even if no signal followed.\n\nThis row: the checkbox switches them on, then the colour of the long marker below the candle and of the short marker above it."),
    showSniper=input.bool(True, "Draw signal markers", group=g11, inline="sn1", tooltip="The dot that appears once every enabled condition is met. It sits below the candle for a long context and above it for a short one, and it is drawn slightly larger than the setup dot.\n\nDeliberately a dot and not the word LONG or SHORT: a written instruction invites an immediate market order, while price may well keep running the other way first. The dot says a condition is complete, not that you should press the button.\n\nThis row: the checkbox switches the dots on, then the colour of each."),
    sniperColL=input.color(color.lime, "", group=g11, inline="sn1", tooltip="The dot that appears once every enabled condition is met. It sits below the candle for a long context and above it for a short one, and it is drawn slightly larger than the setup dot.\n\nDeliberately a dot and not the word LONG or SHORT: a written instruction invites an immediate market order, while price may well keep running the other way first. The dot says a condition is complete, not that you should press the button.\n\nThis row: the checkbox switches the dots on, then the colour of each."),
    sniperColS=input.color(color.red, "", group=g11, inline="sn1", tooltip="The dot that appears once every enabled condition is met. It sits below the candle for a long context and above it for a short one, and it is drawn slightly larger than the setup dot.\n\nDeliberately a dot and not the word LONG or SHORT: a written instruction invites an immediate market order, while price may well keep running the other way first. The dot says a condition is complete, not that you should press the button.\n\nThis row: the checkbox switches the dots on, then the colour of each."),
    priceMode=input.string("Signals only", "Price next to the markers", options=("Off", "Signals only", "Setups and signals"), group=g11, inline="px1", tooltip="Writes the price next to a marker: the close of the candle on which the conditions were complete. That is the level the marker refers to, and it saves reading it off the axis afterwards.\n\nSignals only: just the larger dots. This is the default, because setups appear far more often and a price on every one of them fills the chart quickly.\n\nSetups and signals: every dot gets its price.\n\nOff: no prices at all.\n\nThe number is the close of that candle, not a suggested entry - price can and often does move on before you act."),
    priceSize=input.string("Small", "Size", options=("Tiny", "Small", "Normal", "Large"), group=g11, inline="px1", tooltip="Writes the price next to a marker: the close of the candle on which the conditions were complete. That is the level the marker refers to, and it saves reading it off the axis afterwards.\n\nSignals only: just the larger dots. This is the default, because setups appear far more often and a price on every one of them fills the chart quickly.\n\nSetups and signals: every dot gets its price.\n\nOff: no prices at all.\n\nThe number is the close of that candle, not a suggested entry - price can and often does move on before you act."),
    lblGap=input.bool(True, "Keep text clear of the markers", group=g11, tooltip="When a candle carries a marker, any text on that same candle is lifted above or below it instead of overlapping. Several texts stack in a fixed order: marker, signal text, swing label."),
    lblGapAtr=input.float(0.4, "Spacing (x ATR)", minval=0.1, maxval=3.0, step=0.1, group=g11, tooltip="Size of the gap between a marker and the text next to it, measured in ATR so it scales with the instrument and with volatility.\n\nRaise it if text still sits on top of a marker, lower it if the text drifts too far from the candle."),
    tblMode=input.string("Compact", "Detail", options=("Compact", "Full"), group=g12, tooltip="How much the table shows.\n\nCompact: five rows. Bias, setup including its band rejection, entry structure together with the liquidity requirement, session with the current Stoch RSI reading, and the signal state. This is the default because the table lives in the oscillator pane, and a pane at its usual height cuts a nine-row table off at the top.\n\nFull: every condition on its own row, and the chart timeframe check as well. Use it while you are learning which condition blocks a signal - and drag the divider between the panes upwards, otherwise the first rows are cut off. Pine cannot set the pane height itself."),
    cfOn=input.bool(True, "Show confluence counter", group=g12, tooltip="Counts how many of the seven arguments currently point the same way and shows the stronger side with their abbreviations, direction and count on the first line, the abbreviations on the second.\n\nBIAS the higher-timeframe direction, RSI the Stoch RSI extreme within its lookback, BB a band touch with a rejection on this candle, STR the confirmed entry structure, LIQ a recent liquidity sweep, OB price sitting inside an order block or breaker of that side, SES an open session.\n\nIt is a reading aid, not a signal. A signal needs the specific conditions in their specific order - seven ticks with the setup missing is still no entry. What the counter is good for is the opposite case: seeing at a glance that an entry has everything behind it, or that only two arguments carry it."),
    showTable=input.bool(True, "Show status table", group=g12, tooltip="A small table with the current state of every condition, so you can see at a glance what is still missing for a signal.\n\nIt appears in this lower pane, not on the price chart - TradingView ties a table to the pane of its script."),
    tblPos=input.string("Bottom Right", "Position", options=("Top Right", "Middle Right", "Bottom Right", "Top Left", "Middle Left", "Bottom Left"), group=g12, inline="tb1", tooltip="Placement of the table.\n\nThis row: which corner it sits in, and the font size inside it.\n\nThe table belongs to the pane the script runs in, so it appears in the lower pane next to the oscillator, not on the price chart - TradingView offers no way to move a table across panes. On the right it sits clear of the level names along the left edge. If it crowds the oscillator, drag the divider between the two panes."),
    tblSize=input.string("Small", "Text size", options=("Tiny", "Small", "Normal", "Large"), group=g12, inline="tb1", tooltip="Placement of the table.\n\nThis row: which corner it sits in, and the font size inside it.\n\nThe table belongs to the pane the script runs in, so it appears in the lower pane next to the oscillator, not on the price chart - TradingView offers no way to move a table across panes. On the right it sits clear of the level names along the left edge. If it crowds the oscillator, drag the divider between the two panes."),
    tblBg=input.color(color.new(color.black, 80), "Background", group=g12, inline="tb2", tooltip="Basic colours of the table.\n\nThis row: background colour and transparency of the cells, and the colour of the left column."),
    tblLabel=input.color(color.silver, "Labels", group=g12, inline="tb2", tooltip="Basic colours of the table.\n\nThis row: background colour and transparency of the cells, and the colour of the left column."),
    tblColB=input.color(color.lime, "Bullish", group=g12, inline="tb3", tooltip="Colours for the values inside the table.\n\nThis row: anything currently bullish, anything currently bearish, and conditions switched off or not met yet."),
    tblColS=input.color(color.red, "Bearish", group=g12, inline="tb3", tooltip="Colours for the values inside the table.\n\nThis row: anything currently bullish, anything currently bearish, and conditions switched off or not met yet."),
    tblColIdle=input.color(color.gray, "Neutral", group=g12, inline="tb3", tooltip="Colours for the values inside the table.\n\nThis row: anything currently bullish, anything currently bearish, and conditions switched off or not met yet."),
    oscK=input.bool(True, "K line", group=g13, inline="os1", tooltip="The two Stoch RSI lines, drawn with the settings from group 4.\n\nThis row: K is the fast line the setup logic actually works on, D is its smoothing. Their colours follow."),
    oscColK=input.color(color.new('#2962FF'), "", group=g13, inline="os1", tooltip="The two Stoch RSI lines, drawn with the settings from group 4.\n\nThis row: K is the fast line the setup logic actually works on, D is its smoothing. Their colours follow."),
    oscD=input.bool(True, "D line", group=g13, inline="os1", tooltip="The two Stoch RSI lines, drawn with the settings from group 4.\n\nThis row: K is the fast line the setup logic actually works on, D is its smoothing. Their colours follow."),
    oscColD=input.color(color.new('#FF6D00'), "", group=g13, inline="os1", tooltip="The two Stoch RSI lines, drawn with the settings from group 4.\n\nThis row: K is the fast line the setup logic actually works on, D is its smoothing. Their colours follow."),
    oscFill=input.bool(True, "Fill between K and D", group=g13, inline="os2", tooltip="Shades the area between the two lines: one colour while K is above D, the other while it is below.\n\nThat is the momentum direction at a glance - the same idea the well-known all-in-one oscillators use for their stochastic section, but built from the lines we already calculate rather than from an extra formula.\n\nThis row: the checkbox, then the colour for K above D and for K below D."),
    oscFillUp=input.color(color.new(color.new('#26A69A'), 65), "", group=g13, inline="os2", tooltip="Shades the area between the two lines: one colour while K is above D, the other while it is below.\n\nThat is the momentum direction at a glance - the same idea the well-known all-in-one oscillators use for their stochastic section, but built from the lines we already calculate rather than from an extra formula.\n\nThis row: the checkbox, then the colour for K above D and for K below D."),
    oscFillDn=input.color(color.new(color.new('#EF5350'), 65), "", group=g13, inline="os2", tooltip="Shades the area between the two lines: one colour while K is above D, the other while it is below.\n\nThat is the momentum direction at a glance - the same idea the well-known all-in-one oscillators use for their stochastic section, but built from the lines we already calculate rather than from an extra formula.\n\nThis row: the checkbox, then the colour for K above D and for K below D."),
    oscLines=input.bool(True, "Show levels", group=g13, tooltip="Draws your oversold and overbought levels from group 4 as horizontal lines, plus the 50 line in the middle.\n\nUseful for judging whether the thresholds fit the instrument: if the oscillator barely ever reaches them, they are too extreme for this market."),
    oscDots=input.bool(True, "Extreme dots", group=g13, inline="os3", tooltip="A dot at the top of the pane while K is at or above the overbought level, and one at the bottom while it is at or below the oversold level.\n\nThese mark the condition itself, not a signal. A setup additionally needs the band touch and the rejection candle.\n\nThis row: the checkbox, then the colour of the overbought and of the oversold dot."),
    oscDotOb=input.color(color.red, "", group=g13, inline="os3", tooltip="A dot at the top of the pane while K is at or above the overbought level, and one at the bottom while it is at or below the oversold level.\n\nThese mark the condition itself, not a signal. A setup additionally needs the band touch and the rejection candle.\n\nThis row: the checkbox, then the colour of the overbought and of the oversold dot."),
    oscDotOs=input.color(color.lime, "", group=g13, inline="os3", tooltip="A dot at the top of the pane while K is at or above the overbought level, and one at the bottom while it is at or below the oversold level.\n\nThese mark the condition itself, not a signal. A setup additionally needs the band touch and the rejection candle.\n\nThis row: the checkbox, then the colour of the overbought and of the oversold dot."),
    oscBias=input.bool(True, "Bias as background", group=g13, inline="os4", tooltip="Tints the whole pane with the bias, using the source chosen in group 2.\n\nThis answers the same question a money-flow background answers in the all-in-one oscillators - who is in control of the bigger picture - but from data we already have rather than from volume, which is unreliable on CFD and forex feeds anyway.\n\nThe third colour marks the state where structure and average disagree: the structure has already turned while price is still on the wrong side of the average. With Strict Bias on, that is when the old direction stops producing signals.\n\nThis row: the checkbox, then the bullish tint, the bearish tint and the tint while they disagree."),
    oscBiasUp=input.color(color.new(color.new('#26A69A'), 65), "", group=g13, inline="os4", tooltip="Tints the whole pane with the bias, using the source chosen in group 2.\n\nThis answers the same question a money-flow background answers in the all-in-one oscillators - who is in control of the bigger picture - but from data we already have rather than from volume, which is unreliable on CFD and forex feeds anyway.\n\nThe third colour marks the state where structure and average disagree: the structure has already turned while price is still on the wrong side of the average. With Strict Bias on, that is when the old direction stops producing signals.\n\nThis row: the checkbox, then the bullish tint, the bearish tint and the tint while they disagree."),
    oscBiasTr=input.color(color.new(color.new('#FFA726'), 65), "", group=g13, inline="os4", tooltip="Tints the whole pane with the bias, using the source chosen in group 2.\n\nThis answers the same question a money-flow background answers in the all-in-one oscillators - who is in control of the bigger picture - but from data we already have rather than from volume, which is unreliable on CFD and forex feeds anyway.\n\nThe third colour marks the state where structure and average disagree: the structure has already turned while price is still on the wrong side of the average. With Strict Bias on, that is when the old direction stops producing signals.\n\nThis row: the checkbox, then the bullish tint, the bearish tint and the tint while they disagree."),
    oscBiasDn=input.color(color.new(color.new('#EF5350'), 65), "", group=g13, inline="os4", tooltip="Tints the whole pane with the bias, using the source chosen in group 2.\n\nThis answers the same question a money-flow background answers in the all-in-one oscillators - who is in control of the bigger picture - but from data we already have rather than from volume, which is unreliable on CFD and forex feeds anyway.\n\nThe third colour marks the state where structure and average disagree: the structure has already turned while price is still on the wrong side of the average. With Strict Bias on, that is when the old direction stops producing signals.\n\nThis row: the checkbox, then the bullish tint, the bearish tint and the tint while they disagree."),
    oscSignal=input.bool(True, "Repeat signal markers here", group=g13, tooltip="Repeats the signal marker from the price chart inside this pane, drawn on the K line at the moment every enabled condition is met.\n\nWhile you are trading you often watch the oscillator rather than the candles, and a signal that only appears up on the chart is easy to miss. It is deliberately larger than the extreme dots at the edges - those mark a condition, this one marks a complete signal."),
    oscStrip=input.bool(True, "Setup strip at the bottom", group=g13, tooltip="A coloured strip along the bottom edge of the pane for as long as a setup is armed and waiting for its entry, green for long and red for short.\n\nIt starts on the same candle as the small dot on the chart, so the beginning tells you nothing new. The value is in the length and the end: the strip is the countdown of the setup.\n\nEnds together with a large dot - the setup converted into a signal. Ends without one - it expired unused, and the conditions have to build up again from scratch. Runs unusually long - price keeps rejecting at the band and re-arming the setup."),
    ldbOn=input.bool(True, "Show liquidity distance band", group=g14, tooltip="Two boxes running live at the current price, out to the right where the liquidity lines end: one from price up to the nearest untaken liquidity above it, one from price down to the nearest untaken liquidity below it.\n\nBoth are rebuilt on every tick, so their edges move as price moves and jump the moment a nearer level takes over - for example the instant a level gets swept and the next one behind it becomes the nearest.\n\nIndependent of 'Draw liquidity levels' above: the band uses whichever levels are currently enabled as sources, whether or not their own lines are shown."),
    ldbShowPx=input.bool(True, "Price units", group=g14, inline="ldbu", tooltip="Which measurements are shown on each box. Any combination, or all three together.\n\nPrice units and Pips sit at the outer edge, next to each other - price units is the plain price distance from the current close to that level, pips is the same distance divided by the instrument's minimum tick, so it reads as a plain point/pip count instead of a price.\n\nPercent sits on its own, centred inside the box: the share of the whole open range between the two levels, so the upside and downside figures always add up to 100% - how the current price sits between them, not a percentage of price itself."),
    ldbShowPips=input.bool(True, "Pips", group=g14, inline="ldbu", tooltip="Which measurements are shown on each box. Any combination, or all three together.\n\nPrice units and Pips sit at the outer edge, next to each other - price units is the plain price distance from the current close to that level, pips is the same distance divided by the instrument's minimum tick, so it reads as a plain point/pip count instead of a price.\n\nPercent sits on its own, centred inside the box: the share of the whole open range between the two levels, so the upside and downside figures always add up to 100% - how the current price sits between them, not a percentage of price itself."),
    ldbShowPct=input.bool(True, "Percent", group=g14, inline="ldbu", tooltip="Which measurements are shown on each box. Any combination, or all three together.\n\nPrice units and Pips sit at the outer edge, next to each other - price units is the plain price distance from the current close to that level, pips is the same distance divided by the instrument's minimum tick, so it reads as a plain point/pip count instead of a price.\n\nPercent sits on its own, centred inside the box: the share of the whole open range between the two levels, so the upside and downside figures always add up to 100% - how the current price sits between them, not a percentage of price itself."),
    ldbColUp=input.color(color.new(color.red, 55), "To upside liquidity", group=g14, inline="ldb1", tooltip="Colour of each box - the one running up to the nearest liquidity above price, and the one running down to the nearest liquidity below it - used both for the border and, more transparently, for the fill. The border width applies to both."),
    ldbColDn=input.color(color.new(color.lime, 55), "To downside liquidity", group=g14, inline="ldb2", tooltip="Colour of each box - the one running up to the nearest liquidity above price, and the one running down to the nearest liquidity below it - used both for the border and, more transparently, for the fill. The border width applies to both."),
    ldbWidth=input.int(1, "Border width", minval=1, maxval=5, group=g14, inline="ldb2", tooltip="Colour of each box - the one running up to the nearest liquidity above price, and the one running down to the nearest liquidity below it - used both for the border and, more transparently, for the fill. The border width applies to both."),
    ldbBoxW=input.int(8, "Box width (bars)", minval=1, maxval=100, group=g14, tooltip="How wide the two boxes are, measured in chart bars - not their border thickness, which is set above, but how far the box stretches horizontally.\n\nBoth boxes share this width and sit at the same fixed distance to the right of price, past where the liquidity lines and their labels end.")
):
    def f_size(s: str):
        return size.tiny if s == 'Tiny' else size.small if s == 'Small' else size.normal if s == 'Normal' else size.large

    def f_lstyle(s: str):
        return line.style_dashed if s == 'Dashed' else line.style_dotted if s == 'Dotted' else line.style_solid

    def f_tfLabel(tf: str):
        v: float = string.tonumber(tf)
        r: str = tf
        if not na(v):
            if v >= 1440:
                r = string.tostring(v / 1440, '#.##') + 'D'
            elif v >= 60:
                r = string.tostring(v / 60, '#.##') + 'H'
            else:
                r = string.tostring(v, '#') + 'm'
        return r

    biasLbl = f_tfLabel(biasTF)
    entryLbl = f_tfLabel(entryTF)
    setupLbl = f_tfLabel(setupTF)

    chartSec = timeframe.in_seconds(timeframe.period)
    chartMin = math.max(1.0, chartSec / 60.0)
    expBars = math.max(1, cast_int(math.ceil(setupExp / chartMin)))
    cdBars = cast_int(math.ceil(cooldown / chartMin))
    tfMatch = timeframe.period == setupTF

    def f_swings(len: int, devMode: str, devVal: float, backstep: int, atrLen: int):
        ph: float = ta.pivothigh(high, len, len)
        pl: float = ta.pivotlow(low, len, len)
        atr: float = ta.atr(atrLen)
        zt: Persistent[int] = 0
        zp: Persistent[float] = na(float)
        zb: Persistent[int] = na(int)
        pHi: Persistent[float] = na(float)
        pLo: Persistent[float] = na(float)
        cHi: Persistent[float] = na(float)
        cLo: Persistent[float] = na(float)
        evt: bool = False
        isHi: bool = False
        repl: bool = False
        px: float = na(float)
        tm: int = na(int)
        ref: float = na(float)
        minMove: float = devVal * atr if devMode == 'ATR' else close * devVal / 100.0 if devMode == 'Percent' else 0.0
        pbar: int = bar_index - len

        if not na(ph):
            if zt == 1:
                if ph > zp:
                    zp = ph
                    zb = pbar
                    cHi = ph
                    evt = True
                    isHi = True
                    repl = True
                    px = ph
                    tm = time[len]
                    ref = pHi
            elif zt == 0 or (ph - zp >= minMove and pbar - nz(zb, pbar) >= backstep):
                zt = 1
                zp = ph
                zb = pbar
                pHi = cHi
                cHi = ph
                evt = True
                isHi = True
                px = ph
                tm = time[len]
                ref = pHi
        if not na(pl):
            if zt == -1:
                if pl < zp:
                    zp = pl
                    zb = pbar
                    cLo = pl
                    evt = True
                    repl = True
                    px = pl
                    tm = time[len]
                    ref = pLo
            elif zt == 0 or (zp - pl >= minMove and pbar - nz(zb, pbar) >= backstep):
                zt = -1
                zp = pl
                zb = pbar
                pLo = cLo
                cLo = pl
                evt = True
                px = pl
                tm = time[len]
                ref = pLo
        return (evt, isHi, px, tm, repl, ref)

    def f_structure(len: int, devMode: str, devVal: float, backstep: int, atrLen: int):
        evt, isHi, px, tm, repl, ref = f_swings(len, devMode, devVal, backstep, atrLen)
        lastHi: Persistent[float] = na(float)
        lastHiT: Persistent[int] = na(int)
        hiSig: Persistent[bool] = False
        lastLo: Persistent[float] = na(float)
        lastLoT: Persistent[int] = na(int)
        loSig: Persistent[bool] = False
        tr: Persistent[int] = 0
        bos: bool = False
        choch: bool = False
        dir: int = 0
        lvl: float = na(float)
        lvlT: int = na(int)

        if evt:
            if isHi:
                lastHi = px
                lastHiT = tm
                hiSig = False
                if not na(ref) and px > ref:
                    loSig = True
            else:
                lastLo = px
                lastLoT = tm
                loSig = False
                if not na(ref) and px < ref:
                    hiSig = True
        sig: bool = False
        if not na(lastHi) and close > lastHi:
            lvl = lastHi
            lvlT = lastHiT
            sig = hiSig
            dir = 1
            if tr >= 0:
                bos = True
            else:
                choch = True
            tr = 1
            lastHi = na
        elif not na(lastLo) and close < lastLo:
            lvl = lastLo
            lvlT = lastLoT
            sig = loSig
            dir = -1
            if tr <= 0:
                bos = True
            else:
                choch = True
            tr = -1
            lastLo = na
        return (bos, choch, dir, lvl, lvlT, tr, sig)


    def f_liquidity(len: int, devMode: str, devVal: float, backstep: int, atrLen: int):
        evt, isHi, px, tm, repl, ref = f_swings(len, devMode, devVal, backstep, atrLen)
        ah: Persistent[list[float]] = array.new_float()
        aht: Persistent[list[int]] = array.new_int()
        ahs: Persistent[list[int]] = array.new_int()
        al: Persistent[list[float]] = array.new_float()
        alt: Persistent[list[int]] = array.new_int()
        als: Persistent[list[int]] = array.new_int()

        lastHiPx: Persistent[float] = na(float)
        lastLoPx: Persistent[float] = na(float)
        if evt:
            if isHi:
                if repl and array.size(ah) > 0:
                    array.pop(ah)
                    array.pop(aht)
                    array.pop(ahs)
                array.push(ah, px)
                array.push(aht, tm)
                array.push(ahs, 0)

                if not na(ref) and px > ref and (not na(lastLoPx)):
                    ixl: int = array.lastindexof(al, lastLoPx)
                    if ixl >= 0:
                        array.set(als, ixl, 1)
                lastHiPx = px
            else:
                if repl and array.size(al) > 0:
                    array.pop(al)
                    array.pop(alt)
                    array.pop(als)
                array.push(al, px)
                array.push(alt, tm)
                array.push(als, 0)

                if not na(ref) and px < ref and (not na(lastHiPx)):
                    ixh: int = array.lastindexof(ah, lastHiPx)
                    if ixh >= 0:
                        array.set(ahs, ixh, 1)
                lastLoPx = px

        if array.size(ah) > 0:
            for i in pine_range(array.size(ah) - 1, 0):
                if close > array.get(ah, i):
                    array.remove(ah, i)
                    array.remove(aht, i)
                    array.remove(ahs, i)
        if array.size(al) > 0:
            for i in pine_range(array.size(al) - 1, 0):
                if close < array.get(al, i):
                    array.remove(al, i)
                    array.remove(alt, i)
                    array.remove(als, i)
        if array.size(ah) > 60:
            array.shift(ah)
            array.shift(aht)
            array.shift(ahs)
        if array.size(al) > 60:
            array.shift(al)
            array.shift(alt)
            array.shift(als)

        sh: list[float] = array.copy(ah)
        sl: list[float] = array.copy(al)
        array.sort(sh, order.ascending)
        array.sort(sl, order.descending)
        r: LiqSet = LiqSet(array.new_float(), array.new_int(), array.new_float(), array.new_int(), array.new_float(), array.new_int(), array.new_float(), array.new_int())
        if array.size(sh) > 0:
            for i in pine_range(0, array.size(sh) - 1):
                v: float = array.get(sh, i)
                ix: int = array.indexof(ah, v)
                if ix >= 0:
                    if array.get(ahs, ix) == 1:
                        if array.size(r.hiS) < 5:
                            array.push(r.hiS, v)
                            array.push(r.hiSt, array.get(aht, ix))
                    else:
                        if array.size(r.hiN) < 5:
                            array.push(r.hiN, v)
                            array.push(r.hiNt, array.get(aht, ix))
        if array.size(sl) > 0:
            for i in pine_range(0, array.size(sl) - 1):
                v2: float = array.get(sl, i)
                iy: int = array.indexof(al, v2)
                if iy >= 0:
                    if array.get(als, iy) == 1:
                        if array.size(r.loS) < 5:
                            array.push(r.loS, v2)
                            array.push(r.loSt, array.get(alt, iy))
                    else:
                        if array.size(r.loN) < 5:
                            array.push(r.loN, v2)
                            array.push(r.loNt, array.get(alt, iy))
        return r

    biasClose = request.security(syminfo.tickerid, biasTF, close[1], lookahead=barmerge.lookahead_off)
    biasEmaV = request.security(syminfo.tickerid, biasTF, inline_series(ta.ema(close, emaLen), 1), lookahead=barmerge.lookahead_off)
    emaBull = not na(biasEmaV) and biasClose > biasEmaV
    emaBear = not na(biasEmaV) and biasClose < biasEmaV

    bosB, chB, dirB, lvlB, lvlTB, trBraw, sigB = request.security(syminfo.tickerid, biasTF, f_structure(swMain, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    tBias: Series = request.security(syminfo.tickerid, biasTF, time, lookahead=barmerge.lookahead_off)
    newBiasBar = tBias != tBias[1]
    trBias: Persistent[int] = 0
    if newBiasBar:
        trBias = trBraw
    strBull = trBias == 1
    strBear = trBias == -1

    biasBull: bool = False
    biasBear: bool = False
    biasTrans: bool = False
    if biasSrc == 'EMA':
        biasBull = emaBull
        biasBear = emaBear
    elif biasSrc == 'Structure':
        biasBull = strBull
        biasBear = strBear
    else:
        if emaBull and strBear or (emaBear and strBull):
            biasTrans = True
        else:
            biasBull = emaBull and (not strBear)
            biasBear = emaBear and (not strBull)
    transBull = biasTrans and strBull
    transBear = biasTrans and strBear

    bbBasis = ta.sma(bbSrc, bbLen)
    bbDevV = bbMult * ta.stdev(bbSrc, bbLen)
    bbUpper = bbBasis + bbDevV
    bbLower = bbBasis - bbDevV

    rsiV = ta.rsi(close, rsiLen)
    stoV = ta.stoch(rsiV, rsiV, rsiV, stoLen)
    kV = ta.sma(stoV, kSm)
    dV = ta.sma(kV, dSm)
    stochWasOS = ta.lowest(kV, stochLB) <= osLvl
    stochWasOB = ta.highest(kV, stochLB) >= obLvl

    def f_sessLimit(raw: Series[bool]):
        startT: Persistent[int] = na(int)
        if raw and (not raw[1]):
            startT = time
        ok: bool = raw
        if raw and maxHoursOn and (not na(startT)):
            ok = time - startT <= cast_int(maxHours * 3600000)
        return ok

    rawLDN = useLDN and (not na(time(timeframe.period, sLDN, 'Europe/London')))
    rawNY = useNY and (not na(time(timeframe.period, sNY, 'America/New_York')))
    rawAsia = useAsia and (not na(time(timeframe.period, sAsia, 'Asia/Tokyo')))
    inLDN = f_sessLimit(rawLDN)
    inNY = f_sessLimit(rawNY)
    inAsia = f_sessLimit(rawAsia)
    anySess = useLDN or useNY or useAsia
    inSession: Series = inLDN or inNY or inAsia if anySess else True
    sessName = 'London' if inLDN else 'New York' if inNY else 'Tokyo' if inAsia else '-'

    atrV: Series = ta.atr(swAtrLen)

    newDay = time('D') != inline_series(time('D'), 1)
    curDH: Persistent[float] = na(float)
    curDL: Persistent[float] = na(float)
    curDHt: Persistent[int] = na(int)
    curDLt: Persistent[int] = na(int)
    pdH: Persistent[float] = na(float)
    pdL: Persistent[float] = na(float)
    pdHt: Persistent[int] = na(int)
    pdLt: Persistent[int] = na(int)
    if newDay:
        pdH = curDH
        pdL = curDL
        pdHt = curDHt
        pdLt = curDLt
        curDH = high
        curDL = low
        curDHt = time
        curDLt = time
    else:
        if na(curDH) or high > curDH:
            curDH = high
            curDHt = time
        if na(curDL) or low < curDL:
            curDL = low
            curDLt = time

    liqLenEff = 1 if liqDepth == 'Also smaller swings' else liqLen

    lq15: LiqSet = request.security(syminfo.tickerid, '15', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    lq30: LiqSet = request.security(syminfo.tickerid, '30', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    lq60: LiqSet = request.security(syminfo.tickerid, '60', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    lq240: LiqSet = request.security(syminfo.tickerid, '240', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    lq1D: LiqSet = request.security(syminfo.tickerid, 'D', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    lq1W: LiqSet = request.security(syminfo.tickerid, 'W', f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)

    lqC: LiqSet = f_liquidity(liqLenEff, swDevMode, swDevVal, swBack, swAtrLen)

    hLow: Persistent[list[float]] = array.new_float()
    hHigh: Persistent[list[float]] = array.new_float()
    hTime: Persistent[list[int]] = array.new_int()
    if barstate.isconfirmed:
        array.push(hLow, low)
        array.push(hHigh, high)
        array.push(hTime, time)
        if array.size(hLow) > 500:
            array.shift(hLow)
            array.shift(hHigh)
            array.shift(hTime)

    def f_exactLow(lv: float, fb: int):
        r: int = fb
        if array.size(hLow) > 0 and (not na(fb)):
            for i in pine_range(0, array.size(hLow) - 1):
                if array.get(hTime, i) >= fb and math.abs(array.get(hLow, i) - lv) <= syminfo.mintick * 0.5:
                    r = array.get(hTime, i)
                    break
        return r

    def f_exactHigh(lv: float, fb: int):
        r: int = fb
        if array.size(hHigh) > 0 and (not na(fb)):
            for i in pine_range(0, array.size(hHigh) - 1):
                if array.get(hTime, i) >= fb and math.abs(array.get(hHigh, i) - lv) <= syminfo.mintick * 0.5:
                    r = array.get(hTime, i)
                    break
        return r

    lowestN = ta.lowest(low, sweepLB)
    highestN = ta.highest(high, sweepLB)
    def f_sweptLow(lv: float):
        return not na(lv) and lowestN < lv and (close > lv)

    def f_sweptHigh(lv: float):
        return not na(lv) and highestN > lv and (close < lv)

    candHiPx: list[float] = array.new_float()
    candHiTm: list[int] = array.new_int()
    candHiSg: list[int] = array.new_int()
    candHiTf: list[str] = array.new_string()
    candLoPx: list[float] = array.new_float()
    candLoTm: list[int] = array.new_int()
    candLoSg: list[int] = array.new_int()
    candLoTf: list[str] = array.new_string()

    def f_collect(L: LiqSet, tf: str):
        __block_result__ = na
        if not na(L):
            nhs: int = math.min(array.size(L.hiS), array.size(L.hiSt))
            if nhs > 0:
                for i in pine_range(0, nhs - 1):
                    array.push(candHiPx, array.get(L.hiS, i))
                    array.push(candHiTm, array.get(L.hiSt, i))
                    array.push(candHiSg, 1)
                    array.push(candHiTf, tf)
            nls: int = math.min(array.size(L.loS), array.size(L.loSt))
            if nls > 0:
                for i in pine_range(0, nls - 1):
                    array.push(candLoPx, array.get(L.loS, i))
                    array.push(candLoTm, array.get(L.loSt, i))
                    array.push(candLoSg, 1)
                    array.push(candLoTf, tf)
            __block_result_1__ = na
            if liqKind == 'Significant and simple':
                nhn: int = math.min(array.size(L.hiN), array.size(L.hiNt))
                if nhn > 0:
                    for i in pine_range(0, nhn - 1):
                        array.push(candHiPx, array.get(L.hiN, i))
                        array.push(candHiTm, array.get(L.hiNt, i))
                        array.push(candHiSg, 0)
                        array.push(candHiTf, tf)
                nln: int = math.min(array.size(L.loN), array.size(L.loNt))
                __block_result_2__ = na
                if nln > 0:
                    __block_result_3__ = na
                    for i in pine_range(0, nln - 1):
                        array.push(candLoPx, array.get(L.loN, i))
                        array.push(candLoTm, array.get(L.loNt, i))
                        array.push(candLoSg, 0)
                        __block_result_3__ = array.push(candLoTf, tf)
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    if useChart:
        f_collect(lqC, setupLbl)
    if use15m:
        f_collect(lq15, '15m')
    if use30m:
        f_collect(lq30, '30m')
    if use1H:
        f_collect(lq60, '1H')
    if use4H:
        f_collect(lq240, '4H')
    if use1D:
        f_collect(lq1D, '1D')
    if use1W:
        f_collect(lq1W, '1W')

    def f_mergeSide(px: list[float], tm: list[int], sg: list[int], tf: list[str]):
        mPx: list[float] = array.new_float()
        mTm: list[int] = array.new_int()
        mSg: list[int] = array.new_int()
        mTf: list[str] = array.new_string()

        n: int = array.size(px)
        n = math.min(n, array.size(tm))
        n = math.min(n, array.size(sg))
        n = math.min(n, array.size(tf))
        used: list[bool] = array.new_bool(n, False)
        tol: float = syminfo.mintick * 0.5
        if n > 0:
            for i in pine_range(0, n - 1):
                if not array.get(used, i):
                    p0: float = array.get(px, i)
                    t0: int = array.get(tm, i)
                    s0: int = array.get(sg, i)
                    tfList: str = array.get(tf, i)
                    array.set(used, i, True)

                    if i < n - 1:
                        for j in pine_range(i + 1, n - 1):
                            if not array.get(used, j) and math.abs(array.get(px, j) - p0) <= tol:
                                array.set(used, j, True)
                                t0 = math.min(t0, array.get(tm, j))
                                s0 = math.max(s0, array.get(sg, j))
                                tfList = tfList + '+' + array.get(tf, j)
                    array.push(mPx, p0)
                    array.push(mTm, t0)
                    array.push(mSg, s0)
                    array.push(mTf, tfList)
        return (mPx, mTm, mSg, mTf)

    def f_finalizeSide(mPx: list[float], mTm: list[int], mSg: list[int], mTf: list[str], isHigh: bool, tok: str):
        fPx: list[float] = array.new_float()
        fTm: list[int] = array.new_int()
        fSg: list[int] = array.new_int()
        fNm: list[str] = array.new_string()
        n: int = array.size(mPx)
        if n > 0:
            idxArr: list[int] = array.new_int()
            for i in pine_range(0, n - 1):
                array.push(idxArr, i)

            if n > 1:
                for a in pine_range(0, n - 2):
                    best: int = a
                    for b in pine_range(a + 1, n - 1):
                        pb: float = array.get(mPx, array.get(idxArr, b))
                        pBest: float = array.get(mPx, array.get(idxArr, best))
                        better: bool = pb < pBest if isHigh else pb > pBest
                        if better:
                            best = b
                    if best != a:
                        tmp: int = array.get(idxArr, a)
                        array.set(idxArr, a, array.get(idxArr, best))
                        array.set(idxArr, best, tmp)
            rankSig: int = 0
            rankSim: int = 0
            for k in pine_range(0, n - 1):
                ix: int = array.get(idxArr, k)
                sgv: int = array.get(mSg, ix)
                if sgv == 1:
                    if rankSig < nLvl:
                        rankSig += 1
                        array.push(fPx, array.get(mPx, ix))
                        array.push(fTm, array.get(mTm, ix))
                        array.push(fSg, 1)
                        array.push(fNm, array.get(mTf, ix) + tok + string.tostring(rankSig))
                else:
                    if rankSim < nLvl:
                        rankSim += 1
                        array.push(fPx, array.get(mPx, ix))
                        array.push(fTm, array.get(mTm, ix))
                        array.push(fSg, 0)
                        array.push(fNm, array.get(mTf, ix) + string.lower(tok) + string.tostring(rankSim))
        return (fPx, fTm, fSg, fNm)

    hTok = ' H' if lvlNaming == 'High / Low' else ' BSL'
    lTok = ' L' if lvlNaming == 'High / Low' else ' SSL'

    hPxM, hTmM, hSgM, hTfM = f_mergeSide(candHiPx, candHiTm, candHiSg, candHiTf)
    lPxM, lTmM, lSgM, lTfM = f_mergeSide(candLoPx, candLoTm, candLoSg, candLoTf)
    fHiPx, fHiTm, fHiSg, fHiNm = f_finalizeSide(hPxM, hTmM, hSgM, hTfM, True, hTok)
    fLoPx, fLoTm, fLoSg, fLoNm = f_finalizeSide(lPxM, lTmM, lSgM, lTfM, False, lTok)

    highLv = fHiPx
    highTm = fHiTm
    highSg = fHiSg
    highNm = fHiNm
    lowLv = fLoPx
    lowTm = fLoTm
    lowSg = fLoSg
    lowNm = fLoNm

    if usePD:
        array.push(highLv, pdH)
        array.push(highNm, 'PDH')
        array.push(highTm, pdHt)
        array.push(highSg, 1)
        array.push(lowLv, pdL)
        array.push(lowNm, 'PDL')
        array.push(lowTm, pdLt)
        array.push(lowSg, 1)

    sweptArchHiPx: Persistent[list[float]] = array.new_float()
    sweptArchHiOT: Persistent[list[int]] = array.new_int()
    sweptArchHiNm: Persistent[list[str]] = array.new_string()
    sweptArchHiSg: Persistent[list[int]] = array.new_int()
    sweptArchLoPx: Persistent[list[float]] = array.new_float()
    sweptArchLoOT: Persistent[list[int]] = array.new_int()
    sweptArchLoNm: Persistent[list[str]] = array.new_string()
    sweptArchLoSg: Persistent[list[int]] = array.new_int()

    def f_archiveHigh(lv: float, ot: int, nm: str, sg: int):
        __block_result_4__ = na
        if array.indexof(sweptArchHiPx, lv) < 0:
            array.push(sweptArchHiPx, lv)
            array.push(sweptArchHiOT, ot)
            array.push(sweptArchHiNm, nm)
            array.push(sweptArchHiSg, sg)
            __block_result_5__ = na
            if array.size(sweptArchHiPx) > 40:
                array.shift(sweptArchHiPx)
                array.shift(sweptArchHiOT)
                array.shift(sweptArchHiNm)
                __block_result_5__ = array.shift(sweptArchHiSg)
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    def f_archiveLow(lv: float, ot: int, nm: str, sg: int):
        __block_result_6__ = na
        if array.indexof(sweptArchLoPx, lv) < 0:
            array.push(sweptArchLoPx, lv)
            array.push(sweptArchLoOT, ot)
            array.push(sweptArchLoNm, nm)
            array.push(sweptArchLoSg, sg)
            __block_result_7__ = na
            if array.size(sweptArchLoPx) > 40:
                array.shift(sweptArchLoPx)
                array.shift(sweptArchLoOT)
                array.shift(sweptArchLoNm)
                __block_result_7__ = array.shift(sweptArchLoSg)
            __block_result_6__ = __block_result_7__
        return __block_result_6__

    sweptLoMem: Persistent[list[float]] = array.new_float()
    sweptLoTm: Persistent[list[int]] = array.new_int()
    sweptHiMem: Persistent[list[float]] = array.new_float()
    sweptHiTm: Persistent[list[int]] = array.new_int()

    def f_wasSweptLow(lv: float, ot: int, nm: str, sg: int):
        if f_sweptLow(lv) and array.indexof(sweptLoMem, lv) < 0:
            array.push(sweptLoMem, lv)
            array.push(sweptLoTm, time)
            if array.size(sweptLoMem) > 60:
                array.shift(sweptLoMem)
                array.shift(sweptLoTm)
            f_archiveLow(lv, ot, nm, sg)
        return array.indexof(sweptLoMem, lv) >= 0

    def f_wasSweptHigh(lv: float, ot: int, nm: str, sg: int):
        if f_sweptHigh(lv) and array.indexof(sweptHiMem, lv) < 0:
            array.push(sweptHiMem, lv)
            array.push(sweptHiTm, time)
            if array.size(sweptHiMem) > 60:
                array.shift(sweptHiMem)
                array.shift(sweptHiTm)
            f_archiveHigh(lv, ot, nm, sg)
        return array.indexof(sweptHiMem, lv) >= 0

    def f_sweepTimeLow(lv: float):
        ix: int = array.indexof(sweptLoMem, lv)
        return array.get(sweptLoTm, ix) if ix >= 0 else na

    def f_sweepTimeHigh(lv: float):
        ix: int = array.indexof(sweptHiMem, lv)
        return array.get(sweptHiTm, ix) if ix >= 0 else na

    bullSweep: Series[bool] = False
    bearSweep: Series[bool] = False
    bullSweepSig: bool = False
    bearSweepSig: bool = False
    bullSweepNm: str = ""
    bearSweepNm: str = ""
    if array.size(lowLv) > 0:
        for i in pine_range(0, array.size(lowLv) - 1):
            lvl: float = array.get(lowLv, i)
            mem: bool = f_wasSweptLow(lvl, array.get(lowTm, i), array.get(lowNm, i), array.get(lowSg, i))
            if f_sweptLow(lvl):
                bullSweep = True
                if array.get(lowSg, i) == 1:
                    bullSweepSig = True
                bullSweepNm = array.get(lowNm, i) if bullSweepNm == '' else bullSweepNm
    if array.size(highLv) > 0:
        for i in pine_range(0, array.size(highLv) - 1):
            lvh: float = array.get(highLv, i)
            memh: bool = f_wasSweptHigh(lvh, array.get(highTm, i), array.get(highNm, i), array.get(highSg, i))
            if f_sweptHigh(lvh):
                bearSweep = True
                if array.get(highSg, i) == 1:
                    bearSweepSig = True
                bearSweepNm = array.get(highNm, i) if bearSweepNm == '' else bearSweepNm

    def f_mergeArchiveHigh():
        __block_result_8__ = na
        if sweptShow and array.size(sweptArchHiPx) > 0:
            tol: float = syminfo.mintick * 0.5
            __block_result_9__ = na
            for i in pine_range(0, array.size(sweptArchHiPx) - 1):
                av: float = array.get(sweptArchHiPx, i)
                present: bool = False
                if array.size(highLv) > 0:
                    for j in pine_range(0, array.size(highLv) - 1):
                        if math.abs(array.get(highLv, j) - av) <= tol:
                            present = True
                __block_result_10__ = na
                if not present:
                    array.push(highLv, av)
                    array.push(highNm, array.get(sweptArchHiNm, i))
                    array.push(highTm, array.get(sweptArchHiOT, i))
                    __block_result_10__ = array.push(highSg, array.get(sweptArchHiSg, i))
                __block_result_9__ = __block_result_10__
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    def f_mergeArchiveLow():
        __block_result_11__ = na
        if sweptShow and array.size(sweptArchLoPx) > 0:
            tol: float = syminfo.mintick * 0.5
            __block_result_12__ = na
            for i in pine_range(0, array.size(sweptArchLoPx) - 1):
                av: float = array.get(sweptArchLoPx, i)
                present: bool = False
                if array.size(lowLv) > 0:
                    for j in pine_range(0, array.size(lowLv) - 1):
                        if math.abs(array.get(lowLv, j) - av) <= tol:
                            present = True
                __block_result_13__ = na
                if not present:
                    array.push(lowLv, av)
                    array.push(lowNm, array.get(sweptArchLoNm, i))
                    array.push(lowTm, array.get(sweptArchLoOT, i))
                    __block_result_13__ = array.push(lowSg, array.get(sweptArchLoSg, i))
                __block_result_12__ = __block_result_13__
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    f_mergeArchiveHigh()
    f_mergeArchiveLow()

    useLTF = timeframe.in_seconds(entryTF) < chartSec
    aH = request.security_lower_tf(syminfo.tickerid, entryTF, high)
    aL = request.security_lower_tf(syminfo.tickerid, entryTF, low)
    aC = request.security_lower_tf(syminfo.tickerid, entryTF, close)
    aT = request.security_lower_tf(syminfo.tickerid, entryTF, time)

    bufH: Persistent[list[float]] = array.new_float()
    bufL: Persistent[list[float]] = array.new_float()
    bufC: Persistent[list[float]] = array.new_float()
    bufT: Persistent[list[int]] = array.new_int()

    def f_isPH(a: list[float], idx: int, l: int, r: int):
        v: float = array.get(a, idx)
        ok: bool = True
        for i in pine_range(1, l):
            if array.get(a, idx - i) >= v:
                ok = False
                break
        if ok:
            for j in pine_range(1, r):
                if array.get(a, idx + j) >= v:
                    ok = False
                    break
        return ok

    def f_isPL(a: list[float], idx: int, l: int, r: int):
        v: float = array.get(a, idx)
        ok: bool = True
        for i in pine_range(1, l):
            if array.get(a, idx - i) <= v:
                ok = False
                break
        if ok:
            for j in pine_range(1, r):
                if array.get(a, idx + j) <= v:
                    ok = False
                    break
        return ok

    lastPH1: Persistent[float] = na(float)
    lastPL1: Persistent[float] = na(float)
    ms1H: Persistent[float] = na(float)
    ms1L: Persistent[float] = na(float)
    ms1Ht: Persistent[int] = na(int)
    ms1Lt: Persistent[int] = na(int)
    ms1Tr: Persistent[int] = 0
    z1t: Persistent[int] = 0
    z1p: Persistent[float] = na(float)
    z1b: Persistent[int] = na(int)
    cHi1: Persistent[float] = na(float)
    pHi1: Persistent[float] = na(float)
    cLo1: Persistent[float] = na(float)
    pLo1: Persistent[float] = na(float)
    oneCount: Persistent[int] = 0

    pendHL: Persistent[bool] = False
    pendHLpx: Persistent[float] = na(float)
    pendLH: Persistent[bool] = False
    pendLHpx: Persistent[float] = na(float)
    seqBull: Persistent[bool] = False
    seqBullCnt: Persistent[int] = na(int)
    seqBear: Persistent[bool] = False
    seqBearCnt: Persistent[int] = na(int)

    hlOK: Persistent[bool] = False
    hhOK: Persistent[bool] = False
    lhOK: Persistent[bool] = False
    llOK: Persistent[bool] = False

    longSetup: Persistent[bool] = False
    shortSetup: Persistent[bool] = False
    longSetupBar: Persistent[int] = na(int)
    shortSetupBar: Persistent[int] = na(int)
    longSetupCnt: Persistent[int] = na(int)
    shortSetupCnt: Persistent[int] = na(int)
    lastSigBar: Persistent[int] = na(int)

    phBefore: float = lastPH1
    plBefore: float = lastPL1
    hlBefore: bool = hlOK
    hhBefore: bool = hhOK
    lhBefore: bool = lhOK
    llBefore: bool = llOK

    sessHi: Persistent[float] = na(float)
    sessLo: Persistent[float] = na(float)
    if inSession and (not inSession[1]):
        sessHi = high
        sessLo = low
    elif inSession:
        sessHi = math.max(sessHi, high)
        sessLo = math.min(sessLo, low)

    def f_orbRange(active: Series[bool]):
        t0: Persistent[int] = na(int)
        h5: Persistent[float] = na(float)
        l5: Persistent[float] = na(float)
        h15: Persistent[float] = na(float)
        l15: Persistent[float] = na(float)
        if active and (not active[1]):
            t0 = time
            h5 = high
            l5 = low
            h15 = high
            l15 = low
        elif active and (not na(t0)):
            el: int = time - t0
            if el < 5 * 60000:
                h5 = math.max(h5, high)
                l5 = math.min(l5, low)
            if el < 15 * 60000:
                h15 = math.max(h15, high)
                l15 = math.min(l15, low)
        return (h5, l5, h15, l15)

    zh5L, zl5L, zh15L, zl15L = f_orbRange(inLDN)
    zh5N, zl5N, zh15N, zl15N = f_orbRange(inNY)
    zh5A, zl5A, zh15A, zl15A = f_orbRange(inAsia)

    def f_nearLvl(e: float):
        return not na(e) and low <= e + zoneTol * atrV and (high >= e - zoneTol * atrV)

    lastBrkBar: Persistent[int] = na(int)
    lastBrkDir: Persistent[int] = 0

    obBoxes: Persistent[list[Box]] = array.new_box()
    obLbls: Persistent[list[Label]] = array.new_label()
    obDir: Persistent[list[int]] = array.new_int()
    obState: Persistent[list[int]] = array.new_int()
    obTop: Persistent[list[float]] = array.new_float()
    obBot: Persistent[list[float]] = array.new_float()

    inObBull: bool = False
    inObBear: bool = False
    inBrkBull: bool = False
    inBrkBear: bool = False
    if array.size(obBoxes) > 0:
        for i in pine_range(0, array.size(obBoxes) - 1):
            if close <= array.get(obTop, i) and close >= array.get(obBot, i):
                isBrk: bool = array.get(obState, i) == 1
                if array.get(obDir, i) == 1:
                    if isBrk:
                        inBrkBull = True
                    else:
                        inObBull = True
                else:
                    if isBrk:
                        inBrkBear = True
                    else:
                        inObBear = True

    freshBrk = not na(lastBrkBar) and bar_index - lastBrkBar <= zoneStrBars
    atSessLo = f_nearLvl(sessLo)
    atSessHi = f_nearLvl(sessHi)
    atORB = orbLDN and (f_nearLvl(zh5L) or f_nearLvl(zl5L) or f_nearLvl(zh15L) or f_nearLvl(zl15L)) or (orbNY and (f_nearLvl(zh5N) or f_nearLvl(zl5N) or f_nearLvl(zh15N) or f_nearLvl(zl15N))) or (orbAsia and (f_nearLvl(zh5A) or f_nearLvl(zl5A) or f_nearLvl(zh15A) or f_nearLvl(zl15A)))

    zoneBull = zoneOB and inObBull or (zoneBrk and inBrkBull) or (zoneSweep and bullSweepSig) or (zoneStr and freshBrk and (lastBrkDir == 1)) or (zoneSess and atSessLo) or (zoneORB and atORB) or zoneBB
    zoneBear = zoneOB and inObBear or (zoneBrk and inBrkBear) or (zoneSweep and bearSweepSig) or (zoneStr and freshBrk and (lastBrkDir == -1)) or (zoneSess and atSessHi) or (zoneORB and atORB) or zoneBB
    zoneOKLong = not zoneOn or zoneBull
    zoneOKShort = not zoneOn or zoneBear

    if longSetup and (not na(longSetupBar)) and (bar_index - longSetupBar >= expBars):
        longSetup = False
    if shortSetup and (not na(shortSetupBar)) and (bar_index - shortSetupBar >= expBars):
        shortSetup = False
    if not longSetup:
        hlOK = False
        hhOK = False
    if not shortSetup:
        lhOK = False
        llOK = False

    bbZone = (bbUpper - bbLower) * rejZone / 100.0
    bbTouchLong = low <= bbLower
    bbRejLong = close > bbLower and close <= bbLower + bbZone
    bbTouchShort = high >= bbUpper
    bbRejShort = close < bbUpper and close >= bbUpper - bbZone

    brkLong = not na(phBefore) and close > phBefore
    brkShort = not na(plBefore) and close < plBefore

    structLong = True if not use1M else brkLong if entryMode == 'Structure Break' else hlBefore and hhBefore if entryMode == 'HH/HL + BB Rejection' else hlBefore and hhBefore and brkLong
    structShort = True if not use1M else brkShort if entryMode == 'Structure Break' else lhBefore and llBefore if entryMode == 'HH/HL + BB Rejection' else lhBefore and llBefore and brkShort

    needBBRej = not (use1M and entryMode == 'Structure Break')
    rejLongOK = bbTouchLong and bbRejLong if needBBRej else True
    rejShortOK = bbTouchShort and bbRejShort if needBBRej else True

    biasOKLong = not strictBias or biasBull or (transBull and transMode == 'Offensive')
    biasOKShort = not strictBias or biasBear or (transBear and transMode == 'Offensive')
    sweepOKLong = not reqSweep or bullSweep
    sweepOKShort = not reqSweep or bearSweep
    cooldownOK = na(lastSigBar) or bar_index - lastSigBar > cdBars

    sniperLong: Series = longSetup and structLong and rejLongOK and biasOKLong and sweepOKLong and inSession and cooldownOK
    sniperShort: Series = shortSetup and structShort and rejShortOK and biasOKShort and sweepOKShort and inSession and cooldownOK
    if sniperLong and sniperShort:
        sniperShort = False
    if sniperLong or sniperShort:
        lastSigBar = bar_index
        longSetup = False
        shortSetup = False

    newLongSetup: Series = bbTouchLong and bbRejLong and stochWasOS and biasOKLong and zoneOKLong
    newShortSetup: Series = bbTouchShort and bbRejShort and stochWasOB and biasOKShort and zoneOKShort
    if newLongSetup:
        if not longSetup:
            hlOK = False
            hhOK = False
        longSetup = True
        longSetupBar = bar_index
        longSetupCnt = oneCount
    if newShortSetup:
        if not shortSetup:
            lhOK = False
            llOK = False
        shortSetup = True
        shortSetupBar = bar_index
        shortSetupCnt = oneCount

    ev1mBOSup: bool = False
    ev1mBOSdn: bool = False
    ev1mCHup: bool = False
    ev1mCHdn: bool = False
    ev1mUpLvl: float = na(float)
    ev1mUpT: int = na(int)
    ev1mDnLvl: float = na(float)
    ev1mDnT: int = na(int)

    if barstate.isconfirmed:
        n: int = 0
        if useLTF:
            if not na(aH):
                n = array.size(aH)
        else:
            n = 1
        if n > 0:
            for bi in pine_range(0, n - 1):
                h1: float = array.get(aH, bi) if useLTF else high
                l1: float = array.get(aL, bi) if useLTF else low
                c1: float = array.get(aC, bi) if useLTF else close
                t1: int = array.get(aT, bi) if useLTF else time
                oneCount = oneCount + 1
                array.push(bufH, h1)
                array.push(bufL, l1)
                array.push(bufC, c1)
                array.push(bufT, t1)
                if array.size(bufH) > 400:
                    array.shift(bufH)
                    array.shift(bufL)
                    array.shift(bufC)
                    array.shift(bufT)
                sz: int = array.size(bufH)

                min1: float = 0.0
                if swDevMode == 'ATR' and sz >= 14:
                    rsum: float = 0.0
                    for k in pine_range(0, 13):
                        rsum += array.get(bufH, sz - 1 - k) - array.get(bufL, sz - 1 - k)
                    min1 = swDevVal * rsum / 14.0
                elif swDevMode == 'Percent':
                    min1 = c1 * swDevVal / 100.0
                p: int = sz - 1 - swInt
                if p >= swInt:
                    if f_isPH(bufH, p, swInt, swInt):
                        pv: float = array.get(bufH, p)
                        pt: int = array.get(bufT, p)
                        pb: int = oneCount - 1 - swInt
                        repl: bool = z1t == 1
                        take: bool = pv > z1p if repl else z1t == 0 or (pv - z1p >= min1 and pb - nz(z1b, pb) >= swBack)
                        if take:
                            if not repl:
                                pHi1 = cHi1
                            cHi1 = pv
                            z1t = 1
                            z1p = pv
                            z1b = pb
                            lastPH1 = pv
                            ms1H = pv
                            ms1Ht = pt
                        isHH: bool = take and (not na(pHi1)) and (pv > pHi1)
                        isLH: bool = take and (not na(pHi1)) and (pv <= pHi1)
                        if isHH:
                            if pendHL:
                                seqBull = True
                                seqBullCnt = oneCount
                            pendLH = False
                            seqBear = False
                        if isLH:
                            pendLH = True
                            pendLHpx = pv
                    if f_isPL(bufL, p, swInt, swInt):
                        pv2: float = array.get(bufL, p)
                        pt2: int = array.get(bufT, p)
                        pb2: int = oneCount - 1 - swInt
                        repl2: bool = z1t == -1
                        take2: bool = pv2 < z1p if repl2 else z1t == 0 or (z1p - pv2 >= min1 and pb2 - nz(z1b, pb2) >= swBack)
                        if take2:
                            if not repl2:
                                pLo1 = cLo1
                            cLo1 = pv2
                            z1t = -1
                            z1p = pv2
                            z1b = pb2
                            lastPL1 = pv2
                            ms1L = pv2
                            ms1Lt = pt2
                        isHL: bool = take2 and (not na(pLo1)) and (pv2 > pLo1)
                        isLL: bool = take2 and (not na(pLo1)) and (pv2 <= pLo1)
                        if isHL:
                            pendHL = True
                            pendHLpx = pv2
                        if isLL:
                            if pendLH:
                                seqBear = True
                                seqBearCnt = oneCount
                            pendHL = False
                            seqBull = False
                if not na(ms1H) and c1 > ms1H:
                    if ms1Tr >= 0:
                        ev1mBOSup = True
                    else:
                        ev1mCHup = True
                    ev1mUpLvl = ms1H
                    ev1mUpT = ms1Ht
                    ms1Tr = 1
                    ms1H = na
                elif not na(ms1L) and c1 < ms1L:
                    if ms1Tr <= 0:
                        ev1mBOSdn = True
                    else:
                        ev1mCHdn = True
                    ev1mDnLvl = ms1L
                    ev1mDnT = ms1Lt
                    ms1Tr = -1
                    ms1L = na

    if longSetup and seqBull and (not (hlOK and hhOK)) and (not na(longSetupCnt)):
        if seqBullCnt >= longSetupCnt - strLead:
            hlOK = True
            hhOK = True
    if shortSetup and seqBear and (not (lhOK and llOK)) and (not na(shortSetupCnt)):
        if seqBearCnt >= shortSetupCnt - strLead:
            lhOK = True
            llOK = True

    def f_stackUp(off: int):
        __hist_sniperShort__: Series = sniperShort[0]
        __hist_atrV__: Series = atrV[0]
        __hist_newShortSetup__: Series = newShortSetup[0]
        g: float = 0.0
        if lblGap:
            if showSetup and __hist_newShortSetup__[off]:
                g += lblGapAtr * __hist_atrV__[off]
            if showSniper and __hist_sniperShort__[off]:
                g += lblGapAtr * __hist_atrV__[off]
        return g

    def f_stackDn(off: int):
        __hist_sniperLong__: Series = sniperLong[0]
        __hist_atrV__: Series = atrV[0]
        __hist_newLongSetup__: Series = newLongSetup[0]
        g: float = 0.0
        if lblGap:
            if showSetup and __hist_newLongSetup__[off]:
                g += lblGapAtr * __hist_atrV__[off]
            if showSniper and __hist_sniperLong__[off]:
                g += lblGapAtr * __hist_atrV__[off]
        return g

    swLblLen = swMain if swDegree == 'Swing' else swInt
    swEvt, swIsHi, swPx, swTm, swRepl, swRef = f_swings(swLblLen, swDevMode, swDevVal, swBack, swAtrLen)
    swLbls: Persistent[list[Label]] = array.new_label()
    swLast: Persistent[Label] = na(Label)

    if swEvt and swOn:
        if swRepl and (not na(swLast)):
            label.delete(swLast)
            if array.size(swLbls) > 0:
                array.pop(swLbls)
        lb: Label = na(Label)
        if not na(swRef):
            higher: bool = swPx > swRef
            txt: str = ('HH' if higher else 'LH') if swIsHi else 'HL' if higher else 'LL'
            y: float = swPx + f_stackUp(swLblLen) if swIsHi else swPx - f_stackDn(swLblLen)
            lb = label.new(bar_index - swLblLen, y, txt, style=label.style_label_down if swIsHi else label.style_label_up, color=color.new(color.white, 100), textcolor=swColUp if higher else swColDn, size=f_size(swTextSize), force_overlay=True)
            array.push(swLbls, lb)
            if array.size(swLbls) > maxSwLbl:
                label.delete(array.shift(swLbls))
        swLast = lb

    bosM5, chM5, dirM5, lvlM5, lvlTM5, trM5, sigM5 = f_structure(swMain, swDevMode, swDevVal, swBack, swAtrLen)
    bosI5, chI5, dirI5, lvlI5, lvlTI5, trI5, sigI5 = f_structure(swInt, swDevMode, swDevVal, swBack, swAtrLen)

    bosM15, chM15, dirM15, lvlM15, lvlTM15, trM15, sigM15 = request.security(syminfo.tickerid, '15', f_structure(swMain, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    bosM60, chM60, dirM60, lvlM60, lvlTM60, trM60, sigM60 = request.security(syminfo.tickerid, '60', f_structure(swMain, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)
    bosM240, chM240, dirM240, lvlM240, lvlTM240, trM240, sigM240 = request.security(syminfo.tickerid, '240', f_structure(swMain, swDevMode, swDevVal, swBack, swAtrLen), lookahead=barmerge.lookahead_off)

    t15: Series = request.security(syminfo.tickerid, '15', time, lookahead=barmerge.lookahead_off)
    t60: Series = request.security(syminfo.tickerid, '60', time, lookahead=barmerge.lookahead_off)
    t240: Series = request.security(syminfo.tickerid, '240', time, lookahead=barmerge.lookahead_off)
    new15 = t15 != t15[1]
    new60 = t60 != t60[1]
    new240 = t240 != t240[1]

    msAllow1 = timeframe.in_seconds(entryTF) >= chartSec
    msAllow15 = timeframe.in_seconds('15') >= chartSec
    msAllow60 = timeframe.in_seconds('60') >= chartSec
    msAllow240 = timeframe.in_seconds('240') >= chartSec

    msLines: Persistent[list[Line]] = array.new_line()
    msLbls: Persistent[list[Label]] = array.new_label()
    msDir: Persistent[list[int]] = array.new_int()
    msAct: Persistent[list[int]] = array.new_int()
    msBar: Persistent[list[int]] = array.new_int()
    msCol: Persistent[list[Color]] = array.new_color()

    msX1: Persistent[list[int]] = array.new_int()
    msX2: Persistent[list[int]] = array.new_int()
    msY: Persistent[list[float]] = array.new_float()
    msTxt: Persistent[list[str]] = array.new_string()
    msInt: Persistent[list[int]] = array.new_int()

    def f_msDrop(i: int):
        line.delete(array.get(msLines, i))
        label.delete(array.get(msLbls, i))
        array.remove(msLines, i)
        array.remove(msLbls, i)
        array.remove(msDir, i)
        array.remove(msAct, i)
        array.remove(msBar, i)
        array.remove(msCol, i)
        array.remove(msX1, i)
        array.remove(msX2, i)
        array.remove(msY, i)
        array.remove(msTxt, i)
        return array.remove(msInt, i)

    def drawMS(ev: bool, dr: int, lvl: float, lvlT: int, tf: str, isChoch: bool, on: bool, colBull: Color, colBear: Color, internal: bool):
        __block_result_14__ = na
        if ev and on and msOn and barstate.isconfirmed and (not na(lvl)) and (not na(lvlT)):
            active: bool = dr == 1 and longSetup or (dr == -1 and shortSetup)
            colOn: Color = colBull if dr == 1 else colBear
            col: Color = colOn if active else msColIdle if msShowIdle else color.new(color.gray, 100)
            kind: str = 'CHOCH' if isChoch else 'BOS'
            txt: str = 'MSB' if msLblMode == 'MSB only' else kind if msLblMode == 'BOS / CHOCH' else 'MSB ' + kind
            txt = txt + ' ' + tf
            xEnd: int = time + msExtend * chartSec * 1000
            ln: Line = line.new(lvlT, lvl, xEnd, lvl, xloc=xloc.bar_time, color=col, width=1 if internal else msWidth, style=line.style_dashed if internal else f_lstyle(msStyle), force_overlay=True)
            lb: Label = label.new(xEnd, lvl, txt, xloc=xloc.bar_time, style=label.style_none, textcolor=col, size=size.tiny if internal else f_size(msTextSize), force_overlay=True)
            array.push(msLines, ln)
            array.push(msLbls, lb)
            array.push(msDir, dr)
            array.push(msAct, 1 if active else 0)
            array.push(msBar, bar_index)
            array.push(msCol, colOn)
            array.push(msX1, lvlT)
            array.push(msX2, xEnd)
            array.push(msY, lvl)
            array.push(msTxt, txt)
            array.push(msInt, 1 if internal else 0)
            __block_result_15__ = na
            if array.size(msLines) > msMax:
                __block_result_15__ = f_msDrop(0)
            __block_result_14__ = __block_result_15__
        return __block_result_14__

    drawMS(bosM5, dirM5, lvlM5, lvlTM5, setupLbl, False, ms5On, ms5ColB, ms5ColS, False)
    drawMS(chM5, dirM5, lvlM5, lvlTM5, setupLbl, True, ms5On, ms5ColB, ms5ColS, False)
    drawMS(bosI5, dirI5, lvlI5, lvlTI5, setupLbl, False, ms5On and msInternal, ms5ColB, ms5ColS, True)
    drawMS(chI5, dirI5, lvlI5, lvlTI5, setupLbl, True, ms5On and msInternal, ms5ColB, ms5ColS, True)
    drawMS(bosM15 and new15, dirM15, lvlM15, lvlTM15, '15m', False, ms15On and msAllow15, ms15ColB, ms15ColS, False)
    drawMS(chM15 and new15, dirM15, lvlM15, lvlTM15, '15m', True, ms15On and msAllow15, ms15ColB, ms15ColS, False)
    drawMS(bosM60 and new60, dirM60, lvlM60, lvlTM60, '1H', False, ms60On and msAllow60, ms60ColB, ms60ColS, False)
    drawMS(chM60 and new60, dirM60, lvlM60, lvlTM60, '1H', True, ms60On and msAllow60, ms60ColB, ms60ColS, False)
    drawMS(bosM240 and new240, dirM240, lvlM240, lvlTM240, '4H', False, ms240On and msAllow240, ms240ColB, ms240ColS, False)
    drawMS(chM240 and new240, dirM240, lvlM240, lvlTM240, '4H', True, ms240On and msAllow240, ms240ColB, ms240ColS, False)
    drawMS(ev1mBOSup, 1, ev1mUpLvl, ev1mUpT, entryLbl, False, ms1On and msAllow1, ms1ColB, ms1ColS, True)
    drawMS(ev1mCHup, 1, ev1mUpLvl, ev1mUpT, entryLbl, True, ms1On and msAllow1, ms1ColB, ms1ColS, True)
    drawMS(ev1mBOSdn, -1, ev1mDnLvl, ev1mDnT, entryLbl, False, ms1On and msAllow1, ms1ColB, ms1ColS, True)
    drawMS(ev1mCHdn, -1, ev1mDnLvl, ev1mDnT, entryLbl, True, ms1On and msAllow1, ms1ColB, ms1ColS, True)

    if (bosM5 or chM5) and dirM5 != 0 and barstate.isconfirmed:
        lastBrkBar = bar_index
        lastBrkDir = dirM5

    if array.size(msLines) > 0:
        for i in pine_range(array.size(msLines) - 1, 0):
            if array.get(msAct, i) == 0:
                dr: int = array.get(msDir, i)
                if dr == 1 and longSetup or (dr == -1 and shortSetup):
                    array.set(msAct, i, 1)
                    line.set_color(array.get(msLines, i), array.get(msCol, i))
                    label.set_textcolor(array.get(msLbls, i), array.get(msCol, i))
                elif msPending > 0 and bar_index - array.get(msBar, i) > msPending:
                    f_msDrop(i)

    def f_obDrop(i: int):
        box.delete(array.get(obBoxes, i))
        label.delete(array.get(obLbls, i))
        array.remove(obBoxes, i)
        array.remove(obLbls, i)
        array.remove(obDir, i)
        array.remove(obState, i)
        array.remove(obTop, i)
        return array.remove(obBot, i)

    def f_obFind(up: bool):
        idx: int = -1
        for i in pine_range(0, obLook):
            if close[i] < open[i] if up else close[i] > open[i]:
                idx = i
                break
        return idx

    obSrcOK = chM5 if obSource == 'CHOCH only' else (bosM5 or chM5) and sigM5 if obSource == 'Defended breaks only' else bosM5 or chM5

    if obOn and barstate.isconfirmed and obSrcOK and (dirM5 != 0):
        up: bool = dirM5 == 1
        k: int = f_obFind(up)
        if k >= 0:
            move: float = close - low[k] if up else high[k] - close
            if obDisp <= 0 or move >= obDisp * atrV:
                cb: Color = obColBull if up else obColBear
                ob: Box = box.new(bar_index - k, high[k], bar_index + 3, low[k], border_color=color.new(cb, math.max(0, color.t(cb) - 35)), border_width=obBordW, bgcolor=cb, force_overlay=True)
                obl: Label = na(Label)
                if obNameOn:
                    obl = label.new(bar_index - k, high[k], 'OB bull' if up else 'OB bear', xloc=xloc.bar_index, style=label.style_label_left, color=color.new(color.white, 100), textcolor=color.new(cb, 0), size=f_size(obNameSz), force_overlay=True)
                array.push(obBoxes, ob)
                array.push(obLbls, obl)
                array.push(obDir, 1 if up else -1)
                array.push(obState, 0)
                array.push(obTop, high[k])
                array.push(obBot, low[k])
                if array.size(obBoxes) > obKeep:
                    f_obDrop(0)

    if array.size(obBoxes) > 0:
        if obOn:
            for i in pine_range(array.size(obBoxes) - 1, 0):
                dr: int = array.get(obDir, i)
                st__000004b5__: int = array.get(obState, i)
                tp: float = array.get(obTop, i)
                bt: float = array.get(obBot, i)
                through: bool = close < bt if dr == 1 else close > tp
                if through and barstate.isconfirmed:
                    if st__000004b5__ == 0 and obBreaker == 'Turn into breaker':
                        cn: Color = obColBearB if dr == 1 else obColBullB
                        array.set(obState, i, 1)
                        array.set(obDir, i, -dr)
                        box.set_bgcolor(array.get(obBoxes, i), cn)
                        box.set_border_color(array.get(obBoxes, i), color.new(cn, math.max(0, color.t(cn) - 35)))
                        box.set_right(array.get(obBoxes, i), bar_index + 3)

                        if not na(array.get(obLbls, i)):
                            label.set_text(array.get(obLbls, i), 'Breaker bear' if dr == 1 else 'Breaker bull')
                            label.set_textcolor(array.get(obLbls, i), color.new(cn, 0))
                            label.set_y(array.get(obLbls, i), tp - atrV * lblGapAtr)
                    else:
                        f_obDrop(i)
                else:
                    box.set_right(array.get(obBoxes, i), bar_index + 3)

                    if not na(array.get(obLbls, i)):
                        label.set_y(array.get(obLbls, i), tp - atrV * lblGapAtr)
        else:
            for i in pine_range(array.size(obBoxes) - 1, 0):
                f_obDrop(i)
    if not obNameOn and array.size(obLbls) > 0:
        for i in pine_range(0, array.size(obLbls) - 1):
            label.delete(array.get(obLbls, i))
            array.set(obLbls, i, na)

    def f_cf(bias: bool, rsi: bool, bb: bool, stc: bool, liq: bool, ob: bool, ses: bool):
        n: int = (1 if bias else 0) + (1 if rsi else 0) + (1 if bb else 0) + (1 if stc else 0) + (1 if liq else 0) + (1 if ob else 0) + (1 if ses else 0)
        t: str = ('BIAS ' if bias else '') + ('RSI ' if rsi else '') + ('BB ' if bb else '') + ('STR ' if stc else '') + ('LIQ ' if liq else '') + ('OB ' if ob else '') + ('SES' if ses else '')
        return (n, t)

    cfLongN, cfLongT = f_cf(biasBull or transBull, stochWasOS, bbTouchLong and bbRejLong, hlOK and hhOK, bullSweep, inObBull or inBrkBull, inSession)
    cfShortN, cfShortT = f_cf(biasBear or transBear, stochWasOB, bbTouchShort and bbRejShort, lhOK and llOK, bearSweep, inObBear or inBrkBear, inSession)
    cfLong = cfLongN >= cfShortN
    cfN = cfLongN if cfLong else cfShortN
    cfTxt = cfLongT if cfLong else cfShortT

    cfLabel = '-' if cfN == 0 else ('LONG ' if cfLong else 'SHORT ') + string.tostring(cfN) + '/7\n' + cfTxt

    pU = plot(bbUpper if bbShow else na, 'BB Upper', color=bbColBand, linewidth=bbWidth, force_overlay=True)
    pB = plot(bbBasis if bbShow else na, 'BB Basis', color=bbColMid, linewidth=bbWidth, force_overlay=True)
    pL = plot(bbLower if bbShow else na, 'BB Lower', color=bbColBand, linewidth=bbWidth, force_overlay=True)

    fill(pU, pL, color=bbColFill if bbShow and bbShowFill else color.new(color.white, 100), title='BB Fill')
    plot(biasEmaV if showEma else na, 'HTF EMA', color=emaCol, linewidth=emaWidth, force_overlay=True)

    markerOK = markerWhen == 'While the candle forms' or barstate.isconfirmed

    plotshape(showSetup and markerOK and newLongSetup, 'Long Setup', location=location.belowbar, style=shape.circle, size=size.tiny, color=setupColL, force_overlay=True)
    plotshape(showSetup and markerOK and newShortSetup, 'Short Setup', location=location.abovebar, style=shape.circle, size=size.tiny, color=setupColS, force_overlay=True)

    plotshape(showSniper and markerOK and sniperLong, 'Signal Long', location=location.belowbar, style=shape.circle, size=size.small, color=sniperColL, force_overlay=True)
    plotshape(showSniper and markerOK and sniperShort, 'Signal Short', location=location.abovebar, style=shape.circle, size=size.small, color=sniperColS, force_overlay=True)

    pxLbls: Persistent[list[Label]] = array.new_label()

    def f_pxLabel(cond: bool, up: bool, col: Color):
        __block_result_16__ = na
        if cond:
            y: float = high + f_stackUp(0) if up else low - f_stackDn(0)
            lb: Label = label.new(bar_index, y, string.tostring(close, format.mintick), style=label.style_label_down if up else label.style_label_up, color=color.new(color.white, 100), textcolor=col, size=f_size(priceSize), force_overlay=True)
            array.push(pxLbls, lb)
            __block_result_17__ = na
            if array.size(pxLbls) > 60:
                __block_result_17__ = label.delete(array.shift(pxLbls))
            __block_result_16__ = __block_result_17__
        return __block_result_16__

    pxSignals = priceMode != 'Off'
    pxSetups = priceMode == 'Setups and signals'
    f_pxLabel(showSniper and markerOK and pxSignals and sniperLong, False, sniperColL)
    f_pxLabel(showSniper and markerOK and pxSignals and sniperShort, True, sniperColS)
    f_pxLabel(showSetup and markerOK and pxSetups and newLongSetup and (not sniperLong), False, setupColL)
    f_pxLabel(showSetup and markerOK and pxSetups and newShortSetup and (not sniperShort), True, setupColS)

    def f_sessBox(active: Series[bool], colHue: Color, nm: str):
        b: Persistent[Box] = na(Box)
        bl: Persistent[Label] = na(Label)
        hist: Persistent[list[Box]] = array.new_box()
        lhist: Persistent[list[Label]] = array.new_label()
        if sessShow and active and (not active[1]):
            b = box.new(bar_index, high, bar_index, low, border_color=color.new(colHue, sessLineTr), border_width=sessBordW, bgcolor=color.new(colHue, sessFillTr), force_overlay=True)
            array.push(hist, b)
            if array.size(hist) > sessKeep:
                box.delete(array.shift(hist))
            bl = na
            if sessNameOn:
                bl = label.new(bar_index, low + atrV * lblGapAtr, nm, style=label.style_label_right, color=color.new(color.white, 100), textcolor=colHue, size=f_size(sessNameSz), force_overlay=True)
                array.push(lhist, bl)
                if array.size(lhist) > sessKeep:
                    label.delete(array.shift(lhist))
        elif sessShow and active and (not na(b)):
            box.set_right(b, bar_index)
            box.set_top(b, math.max(box.get_top(b), high))
            box.set_bottom(b, math.min(box.get_bottom(b), low))

            if not na(bl):
                label.set_xy(bl, math.max(box.get_left(b) + 1, bar_index - 1), box.get_bottom(b) + atrV * lblGapAtr)
        if not sessShow and array.size(hist) > 0:
            for i in pine_range(array.size(hist) - 1, 0):
                box.delete(array.get(hist, i))
                array.remove(hist, i)
        __block_result_18__ = na
        if (not sessShow or not sessNameOn) and array.size(lhist) > 0:
            __block_result_19__ = na
            for i in pine_range(array.size(lhist) - 1, 0):
                label.delete(array.get(lhist, i))
                __block_result_19__ = array.remove(lhist, i)
            __block_result_18__ = __block_result_19__
        return __block_result_18__

    def f_orb(active: Series[bool], on: bool, c5: Color, c15: Color):
        t0: Persistent[int] = na(int)
        b5: Persistent[Box] = na(Box)
        b15: Persistent[Box] = na(Box)
        l5: Persistent[Label] = na(Label)
        l15: Persistent[Label] = na(Label)
        hist: Persistent[list[Box]] = array.new_box()
        lhist: Persistent[list[Label]] = array.new_label()
        live: bool = orbOn and on
        if live and active and (not active[1]):
            t0 = time
            b5 = na
            b15 = na
            if orb5On:
                b5 = box.new(bar_index, high, bar_index, low, border_color=color.new(c5, math.max(0, color.t(c5) - 35)), border_width=orbBordW, bgcolor=c5, force_overlay=True)
                array.push(hist, b5)
            if orb15On:
                b15 = box.new(bar_index, high, bar_index, low, border_color=color.new(c15, math.max(0, color.t(c15) - 35)), border_width=orbBordW, bgcolor=c15, force_overlay=True)
                array.push(hist, b15)
            if array.size(hist) > sessKeep * 2:
                box.delete(array.shift(hist))
            l5 = na
            l15 = na
            if orbNameOn:
                if not na(b5):
                    l5 = label.new(bar_index, low, '5m-ORB', style=label.style_label_left, color=color.new(color.white, 100), textcolor=color.new(c5, 0), size=f_size(orbNameSz), force_overlay=True)
                    array.push(lhist, l5)
                if not na(b15):
                    l15 = label.new(bar_index, low, '15m-ORB', style=label.style_label_left, color=color.new(color.white, 100), textcolor=color.new(c15, 0), size=f_size(orbNameSz), force_overlay=True)
                    array.push(lhist, l15)
                if array.size(lhist) > sessKeep * 2:
                    label.delete(array.shift(lhist))
        elif live and active and (not na(t0)):
            el: int = time - t0
            if el < 5 * 60000 and (not na(b5)):
                box.set_top(b5, math.max(box.get_top(b5), high))
                box.set_bottom(b5, math.min(box.get_bottom(b5), low))
            if el < 15 * 60000 and (not na(b15)):
                box.set_top(b15, math.max(box.get_top(b15), high))
                box.set_bottom(b15, math.min(box.get_bottom(b15), low))

            if not na(b5):
                box.set_right(b5, bar_index)
            if not na(b15):
                box.set_right(b15, bar_index)

            off: float = atrV * lblGapAtr
            if not na(l5) and (not na(l15)) and (not na(b5)) and (not na(b15)):
                roomUp: float = box.get_top(b15) - box.get_top(b5)
                roomDn: float = box.get_bottom(b5) - box.get_bottom(b15)
                xl: int = box.get_left(b15) + 1
                if roomUp >= roomDn:
                    label.set_xy(l15, xl, box.get_top(b15) - off)
                    label.set_xy(l5, xl, box.get_bottom(b5) + off)
                else:
                    label.set_xy(l15, xl, box.get_bottom(b15) + off)
                    label.set_xy(l5, xl, box.get_top(b5) - off)
            else:
                if not na(l5) and (not na(b5)):
                    label.set_xy(l5, box.get_left(b5) + 1, box.get_bottom(b5) + off)
                if not na(l15) and (not na(b15)):
                    label.set_xy(l15, box.get_left(b15) + 1, box.get_bottom(b15) + off)
        if not live and array.size(hist) > 0:
            for i in pine_range(array.size(hist) - 1, 0):
                box.delete(array.get(hist, i))
                array.remove(hist, i)
        __block_result_20__ = na
        if (not live or not orbNameOn) and array.size(lhist) > 0:
            __block_result_21__ = na
            for i in pine_range(array.size(lhist) - 1, 0):
                label.delete(array.get(lhist, i))
                __block_result_21__ = array.remove(lhist, i)
            __block_result_20__ = __block_result_21__
        return __block_result_20__

    boxFull = sessBoxSpan == 'Full session'
    f_sessBox(rawLDN if boxFull else inLDN, sessColL, 'London Session')
    f_sessBox(rawNY if boxFull else inNY, sessColN, 'New York Session')
    f_sessBox(rawAsia if boxFull else inAsia, sessColA, 'Tokyo Session')

    f_orb(inLDN, orbLDN, orbCol5, orbCol15)
    f_orb(inNY, orbNY, orbCol5, orbCol15)
    f_orb(inAsia, orbAsia, orbCol5, orbCol15)

    liqLines: Persistent[list[Line]] = array.new_line()
    liqLbls: Persistent[list[Label]] = array.new_label()

    liqPx: Persistent[list[float]] = array.new_float()
    liqA: Persistent[list[int]] = array.new_int()
    liqB: Persistent[list[int]] = array.new_int()

    def f_liqLine(x1: int, x2: int, y: float, col: Color, sty: str, wd: int, sig: bool, txt: str):
        stub: int = 2 * chartSec * 1000
        gap: int = sigGap * chartSec * 1000
        __block_result_22__ = na
        if sig and sigLabel and (x2 - x1 > stub + gap + 4 * chartSec * 1000):
            l1: Line = line.new(x1, y, x1 + stub, y, xloc=xloc.bar_time, color=col, style=sty, width=wd, force_overlay=True)
            l2: Line = line.new(x1 + stub + gap, y, x2, y, xloc=xloc.bar_time, color=col, style=sty, width=wd, force_overlay=True)
            lt: Label = label.new(x1 + stub + gap / 2, y, txt, xloc=xloc.bar_time, style=label.style_none, textcolor=col, size=f_size(liqTextSize), force_overlay=True)
            array.push(liqLines, l1)
            array.push(liqLines, l2)
            __block_result_22__ = array.push(liqLbls, lt)
        else:
            l0: Line = line.new(x1, y, x2, y, xloc=xloc.bar_time, color=col, style=sty, width=wd, force_overlay=True)
            __block_result_22__ = array.push(liqLines, l0)
        return __block_result_22__

    if barstate.islast:
        if array.size(liqLines) > 0:
            for i in pine_range(0, array.size(liqLines) - 1):
                line.delete(array.get(liqLines, i))
            array.clear(liqLines)
        if array.size(liqLbls) > 0:
            for i in pine_range(0, array.size(liqLbls) - 1):
                label.delete(array.get(liqLbls, i))
            array.clear(liqLbls)
        array.clear(liqPx)
        array.clear(liqA)
        array.clear(liqB)
        if showLiq:
            xR: int = time + 12 * chartSec * 1000

            nmPx: list[float] = array.new_float()
            nmTm: list[int] = array.new_int()
            nmEd: list[int] = array.new_int()
            nmSg: list[int] = array.new_int()
            nmHi: list[int] = array.new_int()
            nmTx: list[str] = array.new_string()
            nmCo: list[Color] = array.new_color()
            if array.size(highLv) > 0:
                for i in pine_range(0, array.size(highLv) - 1):
                    lv: float = array.get(highLv, i)
                    tm: int = f_exactHigh(lv, array.get(highTm, i))
                    if not na(lv) and (not na(tm)):
                        sw: bool = f_wasSweptHigh(lv, array.get(highTm, i), array.get(highNm, i), array.get(highSg, i))
                        sg: bool = array.get(highSg, i) == 1
                        if not sw or sweptShow:
                            col: Color = (liqColHigh if sweptCol == 'Side colour' else liqColSwept) if sw else liqColHigh
                            wd: int = sweptWidth if sw else sigWidth if sg else liqWidth
                            xe: int = xR
                            if sw and sweptEnd == 'Stop at the sweep':
                                st__000005c3__: int = f_sweepTimeHigh(lv)
                                xe = xR if na(st__000005c3__) else math.max(st__000005c3__, tm)
                            f_liqLine(tm, xe, lv, col, f_lstyle(liqStyleSw) if sw else f_lstyle(liqStyleOpen), wd, sg, 'significant liquidity')
                            array.push(liqPx, lv)
                            array.push(liqA, tm)
                            array.push(liqB, xR)
                            array.push(nmPx, lv)
                            array.push(nmTm, tm)
                            array.push(nmEd, xe)
                            array.push(nmSg, 1 if sg else 0)
                            array.push(nmHi, 1)
                            array.push(nmTx, array.get(highNm, i) + (' swept' if sw else '') + ('  ' + string.tostring(lv, format.mintick) if liqPrice == 'All levels' or (liqPrice == 'Swept only' and sw) else ''))
                            array.push(nmCo, col)
            if array.size(lowLv) > 0:
                for i in pine_range(0, array.size(lowLv) - 1):
                    lv2: float = array.get(lowLv, i)
                    tm2: int = f_exactLow(lv2, array.get(lowTm, i))
                    if not na(lv2) and (not na(tm2)):
                        sw2: bool = f_wasSweptLow(lv2, array.get(lowTm, i), array.get(lowNm, i), array.get(lowSg, i))
                        sg2: bool = array.get(lowSg, i) == 1
                        if not sw2 or sweptShow:
                            col2: Color = (liqColLow if sweptCol == 'Side colour' else liqColSwept) if sw2 else liqColLow
                            wd2: int = sweptWidth if sw2 else sigWidth if sg2 else liqWidth
                            xe2: int = xR
                            if sw2 and sweptEnd == 'Stop at the sweep':
                                st2: int = f_sweepTimeLow(lv2)
                                xe2 = xR if na(st2) else math.max(st2, tm2)
                            f_liqLine(tm2, xe2, lv2, col2, f_lstyle(liqStyleSw) if sw2 else f_lstyle(liqStyleOpen), wd2, sg2, 'significant liquidity')
                            array.push(liqPx, lv2)
                            array.push(liqA, tm2)
                            array.push(liqB, xR)
                            array.push(nmPx, lv2)
                            array.push(nmTm, tm2)
                            array.push(nmEd, xe2)
                            array.push(nmSg, 1 if sg2 else 0)
                            array.push(nmHi, 0)
                            array.push(nmTx, array.get(lowNm, i) + (' swept' if sw2 else '') + ('  ' + string.tostring(lv2, format.mintick) if liqPrice == 'All levels' or (liqPrice == 'Swept only' and sw2) else ''))
                            array.push(nmCo, col2)

            cnt: int = array.size(nmPx)
            if cnt > 0:
                done: list[bool] = array.new_bool(cnt, False)
                minGap: float = liqLblGap * atrV
                prevPx: float = na(float)
                slot: int = 0
                for k in pine_range(0, cnt - 1):
                    best: int = -1
                    bestPx: float = na(float)
                    for j in pine_range(0, cnt - 1):
                        if not array.get(done, j):
                            pj: float = array.get(nmPx, j)
                            if na(bestPx) or pj < bestPx:
                                bestPx = pj
                                best = j
                    if best >= 0:
                        array.set(done, best, True)
                        slot = slot + 1 if not na(prevPx) and bestPx - prevPx < minGap else 0
                        prevPx = bestPx
                        x: int = array.get(nmEd, best) - slot * 9 * chartSec * 1000
                        xMin: int = array.get(nmTm, best)
                        lb: Label = label.new(math.max(x, xMin), bestPx, array.get(nmTx, best), xloc=xloc.bar_time, style=label.style_none, textcolor=array.get(nmCo, best), size=f_size(liqTextSize), force_overlay=True)
                        array.push(liqLbls, lb)

    ldbBoxUp: Persistent[Box] = na(Box)
    ldbBoxDn: Persistent[Box] = na(Box)
    ldbLblUp: Persistent[Label] = na(Label)
    ldbLblDn: Persistent[Label] = na(Label)
    ldbPctUp: Persistent[Label] = na(Label)
    ldbPctDn: Persistent[Label] = na(Label)

    def f_ldbText(dist: float):
        out: str = ""
        if ldbShowPx:
            out = string.tostring(dist, format.mintick)
        if ldbShowPips:
            p: str = string.tostring(math.round(dist / syminfo.mintick), '#') + ' pips'
            out = p if out == '' else out + '  ·  ' + p
        return out

    if barstate.islast:
        if not na(ldbBoxUp):
            box.delete(ldbBoxUp)
            ldbBoxUp = na
        if not na(ldbBoxDn):
            box.delete(ldbBoxDn)
            ldbBoxDn = na
        if not na(ldbLblUp):
            label.delete(ldbLblUp)
            ldbLblUp = na
        if not na(ldbLblDn):
            label.delete(ldbLblDn)
            ldbLblDn = na
        if not na(ldbPctUp):
            label.delete(ldbPctUp)
            ldbPctUp = na
        if not na(ldbPctDn):
            label.delete(ldbPctDn)
            ldbPctDn = na
        if ldbOn:
            ldbUp: float = na(float)
            ldbDn: float = na(float)

            if array.size(highLv) > 0:
                for i in pine_range(0, array.size(highLv) - 1):
                    v: float = array.get(highLv, i)
                    if v > close and array.indexof(sweptHiMem, v) < 0 and (na(ldbUp) or v < ldbUp):
                        ldbUp = v
            if array.size(lowLv) > 0:
                for i in pine_range(0, array.size(lowLv) - 1):
                    v2: float = array.get(lowLv, i)
                    if v2 < close and array.indexof(sweptLoMem, v2) < 0 and (na(ldbDn) or v2 > ldbDn):
                        ldbDn = v2

            xL4: int = time + 14 * chartSec * 1000
            xR4: int = xL4 + ldbBoxW * chartSec * 1000
            xMid: int = xL4 + (xR4 - xL4) / 2

            ldbSpan: float = ldbUp - ldbDn if not na(ldbUp) and (not na(ldbDn)) else na
            if not na(ldbUp):
                dUp: float = ldbUp - close
                pUp: float = dUp / ldbSpan * 100 if not na(ldbSpan) and ldbSpan != 0 else na
                ldbBoxUp = box.new(xL4, ldbUp, xR4, close, xloc=xloc.bar_time, border_color=ldbColUp, border_width=ldbWidth, bgcolor=color.new(ldbColUp, 78), force_overlay=True)
                ldbLblUp = label.new(xR4, ldbUp, f_ldbText(dUp), xloc=xloc.bar_time, style=label.style_label_left, color=color.new(color.white, 100), textcolor=ldbColUp, size=f_size(liqTextSize), force_overlay=True)
                if ldbShowPct and (not na(pUp)):
                    ldbPctUp = label.new(xMid, (ldbUp + close) / 2, string.tostring(pUp, '#.##') + '%', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=ldbColUp, size=f_size(liqTextSize), force_overlay=True)
            if not na(ldbDn):
                dDn: float = close - ldbDn
                pDn: float = dDn / ldbSpan * 100 if not na(ldbSpan) and ldbSpan != 0 else na
                ldbBoxDn = box.new(xL4, close, xR4, ldbDn, xloc=xloc.bar_time, border_color=ldbColDn, border_width=ldbWidth, bgcolor=color.new(ldbColDn, 78), force_overlay=True)
                ldbLblDn = label.new(xR4, ldbDn, f_ldbText(dDn), xloc=xloc.bar_time, style=label.style_label_left, color=color.new(color.white, 100), textcolor=ldbColDn, size=f_size(liqTextSize), force_overlay=True)
                if ldbShowPct and (not na(pDn)):
                    ldbPctDn = label.new(xMid, (close + ldbDn) / 2, string.tostring(pDn, '#.##') + '%', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=ldbColDn, size=f_size(liqTextSize), force_overlay=True)

    if barstate.islast and msOn and (array.size(msLines) > 0) and (array.size(liqPx) > 0):
        tol: float = atrV * 0.05
        for i in pine_range(0, array.size(msLines) - 1):
            y: float = array.get(msY, i)
            xa: int = array.get(msX1, i)
            xb: int = array.get(msX2, i)
            buried: bool = False
            for j in pine_range(0, array.size(liqPx) - 1):
                if math.abs(array.get(liqPx, j) - y) <= tol and array.get(liqB, j) - array.get(liqA, j) > xb - xa:
                    buried = True
            if buried:
                intern: bool = array.get(msInt, i) == 1
                active: bool = array.get(msAct, i) == 1
                col: Color = array.get(msCol, i) if active else msColIdle if msShowIdle else color.new(color.gray, 100)
                line.delete(array.get(msLines, i))
                label.delete(array.get(msLbls, i))
                ln: Line = line.new(xa, y, xb, y, xloc=xloc.bar_time, color=col, width=1 if intern else msWidth, style=line.style_dashed if intern else f_lstyle(msStyle), force_overlay=True)
                lb: Label = label.new(xb, y, array.get(msTxt, i), xloc=xloc.bar_time, style=label.style_none, textcolor=col, size=size.tiny if intern else f_size(msTextSize), force_overlay=True)
                array.set(msLines, i, ln)
                array.set(msLbls, i, lb)

    st: Persistent[Table] = table.new(position.top_right if tblPos == 'Top Right' else position.middle_right if tblPos == 'Middle Right' else position.bottom_right if tblPos == 'Bottom Right' else position.top_left if tblPos == 'Top Left' else position.middle_left if tblPos == 'Middle Left' else position.bottom_left, 2, 10, border_width=1)

    def f_cell(col: int, row: int, txt: str, tc: Color):
        return table.cell(st, col, row, txt, text_color=tc, text_size=f_size(tblSize), bgcolor=tblBg, text_halign=text.align_left)

    if showTable and barstate.islast:
        sBias: str = 'BULLISH' if biasBull else 'BEARISH' if biasBear else 'TURNING UP' if transBull else 'TURNING DOWN' if transBear else '-'
        cBias: Color = tblColB if biasBull else tblColS if biasBear else color.orange if biasTrans else tblColIdle
        sSetup: str = 'LONG' if longSetup else 'SHORT' if shortSetup else '-'
        cSetup: Color = tblColB if longSetup else tblColS if shortSetup else tblColIdle
        sStruct: str = ('HL' if hlOK else '-') + ' + ' + ('HH' if hhOK else '-') if longSetup else ('LH' if lhOK else '-') + ' + ' + ('LL' if llOK else '-') if shortSetup else '-'
        cStruct: Color = tblColB if hlOK and hhOK else tblColS if lhOK and llOK else tblColIdle
        sLiq: str = 'not chosen' if not reqSweep else 'SWEPT ' + bullSweepNm if bullSweep else 'SWEPT ' + bearSweepNm if bearSweep else 'WAITING'
        cLiq: Color = tblColIdle if not reqSweep else tblColB if bullSweep or bearSweep else color.orange
        readyL: bool = longSetup and structLong and biasOKLong and sweepOKLong and inSession and cooldownOK
        readyS: bool = shortSetup and structShort and biasOKShort and sweepOKShort and inSession and cooldownOK
        sReady: str = 'READY LONG' if readyL else 'READY SHORT' if readyS else 'WAITING' if longSetup or shortSetup else '-'
        cReady: Color = tblColB if readyL else tblColS if readyS else color.orange

        if tblMode == 'Full':
            f_cell(0, 0, 'Chart TF', tblLabel)
            f_cell(1, 0, timeframe.period + ' OK' if tfMatch else 'set Setup TF to ' + timeframe.period, color.silver if tfMatch else color.orange)
            f_cell(0, 1, biasLbl + ' Bias', tblLabel)
            f_cell(1, 1, sBias, cBias)
            f_cell(0, 2, setupLbl + ' Setup', tblLabel)
            f_cell(1, 2, sSetup, cSetup)
            f_cell(0, 3, setupLbl + ' BB', tblLabel)
            f_cell(1, 3, 'REJECTED (long)' if bbTouchLong and bbRejLong else 'REJECTED (short)' if bbTouchShort and bbRejShort else '-', tblColB if bbTouchLong and bbRejLong else tblColS if bbTouchShort and bbRejShort else tblColIdle)
            f_cell(0, 4, entryLbl + ' Structure', tblLabel)
            f_cell(1, 4, sStruct if use1M else 'OFF', cStruct if use1M else tblColIdle)
            f_cell(0, 5, 'Liquidity', tblLabel)
            f_cell(1, 5, sLiq, cLiq)
            f_cell(0, 6, 'Session', tblLabel)
            f_cell(1, 6, sessName if inSession else 'outside', tblColB if inSession else tblColIdle)
            f_cell(0, 7, 'Stoch RSI K', tblLabel)
            f_cell(1, 7, string.tostring(kV, '#.0'), tblColS if kV >= obLvl else tblColB if kV <= osLvl else color.silver)
            f_cell(0, 8, 'Signal', tblLabel)
            f_cell(1, 8, sReady, cReady)
            if cfOn:
                f_cell(0, 9, 'Confluence', tblLabel)
                f_cell(1, 9, cfLabel, tblColIdle if cfN == 0 else tblColB if cfLong else tblColS)
        else:
            rej: bool = bbTouchLong and bbRejLong or (bbTouchShort and bbRejShort)
            f_cell(0, 0, 'Bias', tblLabel)
            f_cell(1, 0, sBias if tfMatch else sBias + '  · set Setup TF to ' + timeframe.period, cBias if tfMatch else color.orange)
            f_cell(0, 1, 'Setup', tblLabel)
            f_cell(1, 1, sSetup + ('  · BB ok' if rej else ''), cSetup)
            f_cell(0, 2, 'Structure', tblLabel)
            f_cell(1, 2, (sStruct if use1M else 'OFF') + '  · Liq ' + ('not chosen' if not reqSweep else 'ok' if bullSweep or bearSweep else 'wait'), cStruct if use1M else tblColIdle)
            f_cell(0, 3, 'Session', tblLabel)
            f_cell(1, 3, (sessName if inSession else 'outside') + '  · RSI ' + string.tostring(kV, '#.0'), tblColB if inSession else tblColIdle)
            f_cell(0, 4, 'Signal', tblLabel)
            f_cell(1, 4, sReady, cReady)
            if cfOn:
                f_cell(0, 5, 'Confluence', tblLabel)
                f_cell(1, 5, cfLabel, tblColIdle if cfN == 0 else tblColB if cfLong else tblColS)

    pK = plot(kV if oscK else na, 'Stoch RSI K', color=oscColK, linewidth=2)
    pD = plot(dV if oscD else na, 'Stoch RSI D', color=oscColD, linewidth=1)
    fill(pK, pD, color=(oscFillUp if kV >= dV else oscFillDn) if oscFill else color.new(color.white, 100), title='K/D Fill')

    plot(obLvl if oscLines else na, 'Overbought level', color=color.new(oscDotOb, 55), style=plot.style_line, linewidth=1)
    plot(osLvl if oscLines else na, 'Oversold level', color=color.new(oscDotOs, 55), style=plot.style_line, linewidth=1)
    plot(50 if oscLines else na, 'Mid line', color=color.new(color.gray, 70), style=plot.style_line, linewidth=1)

    plotshape(oscDots and kV >= obLvl, 'Overbought', location=location.top, style=shape.circle, size=size.tiny, color=oscDotOb)

    plotshape(kV if oscSignal and markerOK and sniperLong else na, 'Signal long (pane)', location=location.absolute, style=shape.circle, size=size.normal, color=sniperColL)
    plotshape(kV if oscSignal and markerOK and sniperShort else na, 'Signal short (pane)', location=location.absolute, style=shape.circle, size=size.normal, color=sniperColS)
    plotshape(oscDots and kV <= osLvl, 'Oversold', location=location.bottom, style=shape.circle, size=size.tiny, color=oscDotOs)

    bgcolor((oscBiasUp if biasBull else oscBiasDn if biasBear else oscBiasTr if biasTrans else na) if oscBias else na, title='Bias background')

    sTop = plot(4 if oscStrip else na, 'Strip top', display=display.none)
    sBot = plot(0 if oscStrip else na, 'Strip bottom', display=display.none)
    fill(sTop, sBot, color=color.new(oscDotOs, 20) if oscStrip and longSetup else color.new(oscDotOb, 20) if oscStrip and shortSetup else color.new(color.white, 100), title='Setup strip')

    alertcondition(newLongSetup, 'Long Setup', 'Long setup active')
    alertcondition(newShortSetup, 'Short Setup', 'Short setup active')
    alertcondition(bullSweep and (not bullSweep[1]), 'Bullish Liquidity Sweep', 'Bullish liquidity sweep')
    alertcondition(bearSweep and (not bearSweep[1]), 'Bearish Liquidity Sweep', 'Bearish liquidity sweep')
    alertcondition(bosM5 and dirM5 == 1, 'Bullish BOS', 'Bullish BOS (chart TF)')
    alertcondition(bosM5 and dirM5 == -1, 'Bearish BOS', 'Bearish BOS (chart TF)')
    alertcondition(chM5 and dirM5 == 1, 'Bullish CHOCH', 'Bullish CHOCH (chart TF)')
    alertcondition(chM5 and dirM5 == -1, 'Bearish CHOCH', 'Bearish CHOCH (chart TF)')
    alertcondition((bosM5 or chM5) and dirM5 == 1, 'Bullish MSB', 'Bullish MSB (chart TF)')
    alertcondition((bosM5 or chM5) and dirM5 == -1, 'Bearish MSB', 'Bearish MSB (chart TF)')
    alertcondition(sniperLong, 'SNIPER LONG', 'SNIPER LONG')
    alertcondition(sniperShort, 'SNIPER SHORT', 'SNIPER SHORT')

    if sniperLong or sniperShort:
        dirTxt: str = 'SNIPER LONG' if sniperLong else 'SNIPER SHORT'
        strTxt: str = ('HL' if hlBefore else '-') + ' + ' + ('HH' if hhBefore else '-') if sniperLong else ('LH' if lhBefore else '-') + ' + ' + ('LL' if llBefore else '-')
        msg: str = syminfo.ticker + '\n' + dirTxt + '\n\n' + 'Price: ' + string.tostring(close, format.mintick) + '\n\n' + biasLbl + ' Bias: ' + ('Bullish' if biasBull else 'Bearish' if biasBear else 'Turning up' if transBull else 'Turning down' if transBear else 'Neutral') + '\n' + 'Setup: ' + ('Long' if sniperLong else 'Short') + '\n' + entryLbl + ' Structure: ' + (strTxt if use1M else 'OFF') + '\n' + 'Liquidity Sweep: ' + ('not required' if not reqSweep else ('Yes (' + bullSweepNm + ')' if bullSweep else 'No') if sniperLong else 'Yes (' + bearSweepNm + ')' if bearSweep else 'No') + '\n' + 'Session: ' + sessName
        alert(msg, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)