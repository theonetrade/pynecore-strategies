"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_float, cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    extend, font, format, high, hl2, input, label, line, linefill, location, low, math, na, nz,
    open, order, plot, plotshape, polyline, position, script, shape, size, string, ta, table, text,
    time, timeframe, timestamp, xloc, yloc
)
from pynecore.types import (
    Box, Color, Label, Line, NA, Persistent, PersistentSeries, Polyline,
    Series
)
from pynecore.types.chart import ChartPoint

period_basicgr: str = '⚙️ Phases Master Control'
basicgr: str = '⚙️ Master Control'
plot_gr: str = 'Close Price Plot'
shade_gr: str = '── Dynamic Level Shading ──'
view_gr: str = 'Color Settings'
lastleg_gr: str = '♦︎ Last Confirmed Leg'
tp_basicgr: str = '⚙️ Trend Pivots Master Control'
tp_ch_gr: str = '📐 Trend Pivots Channel'
pc_grp_zz: str = "🌀 Phase Counter — ZigZag"
pc_grp_proj: str = "📈 Phase Counter — Adaptive Projection"
pc_grp_leg: str = "🔢 Phase Counter — Leg Numbering"


@script.indicator("CQ_(9)_Phases Counter + Auto Fibonacci + Trend Pivots v2", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=500, explicit_plot_zorder=True, max_bars_back=4000)
def main(
    period=input.int(45, "Period", minval=2, group=period_basicgr, tooltip="Swing lookback length in bars for the main zigzag (Section 1). A bar becomes a swing high when it is the highest high of the last N bars, or a swing low when it is the lowest low. Higher values give fewer, larger swings that confirm later; lower values give more, smaller swings that react faster. This zigzag also feeds the Fibonacci section: its last settled leg (P2 → P1, the leg before the one still forming) is the one the Fibonacci levels and gauge are measured on."),
    lineUpColor=input(title="Color ↑", defval=color.new('#6BA583'), inline="lines", group="♦︎ lines", tooltip="Color of bullish zigzag legs (swing low to swing high). Pairs with the ↓ color and the Width input on the same row."),
    lineDnColor=input(title="↓", defval=color.new('#D75442'), inline="lines", group="♦︎ lines", tooltip="Color of bearish zigzag legs (swing high to swing low). Pairs with the ↑ color to its left and the Width input to its right."),
    lw=input.int(2, "Width", options=(1, 2, 3, 4), inline="lines", group="♦︎ lines", tooltip="Line width in pixels (1-4) of the bullish and bearish zigzag legs. Also used for the last confirmed leg when it is restyled by the ♦︎ Last Confirmed Leg options."),
    rangeLines=input.bool(True, "Range Lines", inline='rangelines', group="♦︎ lines", tooltip="Draws thin connector lines between consecutive swing highs (high to high) and consecutive swing lows (low to low), with a faint fill between the latest pair, outlining the swing channel. Only affects lines created after the setting changes. The color is set by the swatch to its right."),
    rnglineColor=input(title="", defval=color.new('#000000'), inline="rangelines", group="♦︎ lines", tooltip="Color of the high-to-high and low-to-low range lines. Only used while Range Lines is enabled."),
    delta=input.string('Percent', '𝜟 Format', options=('Percent', 'Absolute'), group='♦︎ labels', inline='st', tooltip="How the move size is shown on each swing label and in the statistics table. Percent: the swing's change relative to the previous opposite swing (for example +12.5%). Absolute: the raw price difference (for example +4,250). Pairs with Text Size to its right."),
    txtsz=input.string("Small", title="Text Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group="♦︎ labels", inline='st', tooltip="Size (Tiny to Huge) of the swing labels that show the HH/LH/HL/LL pattern, the move size and the bar count. Pairs with Δ Format to its left."),
    cyclelab=input.bool(False, "Display Cycle", group="♦︎ labels", tooltip="Adds a second block to each swing label with the number of bars since the previous swing of the same type (the high-to-high or low-to-low cycle length), in addition to the default bar count since the opposite swing."),
    showtable=input.bool(False, 'Show Stats table', group='♦︎ statistics table', tooltip="Shows a statistics table with the geometric average price move and duration (in bars) of recent uptrend legs and downtrend legs from this zigzag. The number of legs averaged is set by Averaging below, and the price column follows Δ Format."),
    locationtable=input.string('Bottom Right', 'Location', options=('Top Right', 'Top Left', 'Bottom Right', 'Bottom Left'), group='♦︎ statistics table', inline='tbpr', tooltip="Screen corner where the statistics table is placed. Pairs with the Size input to its right."),
    sizetable=input.string('Normal', 'Size', options=('Large', 'Normal', 'Small', 'Tiny'), group='♦︎ statistics table', inline='tbpr', tooltip="Text size of the statistics table. Pairs with the Location input to its left."),
    avgln=input.int(10, "Averaging", minval=2, step=1, group='♦︎ statistics table', tooltip="Number of most recent uptrend legs and downtrend legs used for the statistics table averages (minimum 2). A geometric mean is used, so one unusually large leg skews the result less than a simple average would. Higher values give smoother, slower-changing averages."),
    show_indicator=input.bool(True, '⚡ Enable Fibonacci Gauge', group='🪙 F i b o n a c c i  R e t r a c e m e n t', tooltip="Master switch for the Fibonacci levels, extensions, gauge and their labels. When off, nothing from this section is drawn; the zigzag and the last-leg highlight are unaffected."),
    fb_invert=input.bool(False, '⇅ Invert Fibonacci Direction', group='🪙 F i b o n a c c i  R e t r a c e m e n t', tooltip="Off (default): 0% sits on the NEWEST pivot (P1) of the last settled leg and 100% on the OLDER pivot (P2), so the levels read as a retracement of that leg, and the gauge measures the current move away from P1.\nOn: 0% sits on the OLDER pivot and 100% on the NEWEST pivot, so the levels (and the 125%-200% extensions) read as a projection in the direction of the leg. The gauge and label colors are swapped to match that tendency, and the gauge is measured from the leg start with its extreme label tracking the continuation side."),
    show_close_plot=input.bool(False, 'Show Line Graph', group=plot_gr, tooltip="Plots the close price as an extra series on the chart, styled by the Color, Width and Style inputs below. Useful as a clean price trace over candles or on a line chart."),
    close_plot_color=input.color(color.blue, 'Color', inline='pltclose', group=plot_gr, tooltip="Color of the close price plot. Pairs with Width to its right."),
    close_plot_width=input.int(1, 'Width', minval=1, maxval=10, inline='pltclose', group=plot_gr, tooltip="Line width (1-10) of the close price plot. Pairs with Color to its left."),
    _close_plot_style_raw=input.string('Line', 'Style', options=('Line', 'Stepline', 'Histogram', 'Cross', 'Area', 'Columns', 'Circles'), group=plot_gr, tooltip="Plot style of the close price series: Line, Stepline, Histogram, Cross, Area, Columns or Circles."),
    fb250=input(True, '25% ', inline='fbl', group=basicgr, tooltip="Shows or hides the 25% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fb400=input(True, '40% ', inline='fbl', group=basicgr, tooltip="Shows or hides the 40% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fb500=input(True, '50% ', inline='fbl', group=basicgr, tooltip="Shows or hides the 50% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fb600=input(True, '60% ', inline='fbl', group=basicgr, tooltip="Shows or hides the 60% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fb750=input(True, '75% ', inline='fbl', group=basicgr, tooltip="Shows or hides the 75% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fb900=input(True, '90%', inline='fbl', group=basicgr, tooltip="Shows or hides the 90% level between the 0% and 100% lines of the last settled leg. A hidden level is also left out of the Dynamic Proximity Shading ranking, so the remaining levels are ranked without it."),
    fbx_m25=input(True, '-25% ', inline='fbxlo', group=basicgr, tooltip="Allows the -25% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_m50=input(True, '-50% ', inline='fbxlo', group=basicgr, tooltip="Allows the -50% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_m100=input(True, '-100% ', inline='fbxlo', group=basicgr, tooltip="Allows the -100% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_m150=input(True, '-150% ', inline='fbxlo', group=basicgr, tooltip="Allows the -150% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_m160=input(True, '-160% ', inline='fbxlo', group=basicgr, tooltip="Allows the -160% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_m200=input(True, '-200%', inline='fbxlo', group=basicgr, tooltip="Allows the -200% extension level, which lies beyond the 0% line on the side away from 100%. With Invert Fibonacci Direction off (default), 0% is the newest pivot (P1), so it extends past it in the settled leg's own direction; with Invert on, 0% is the leg start, so this level sits behind the leg. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_125=input(True, '125% ', inline='fbxhi', group=basicgr, tooltip="Allows the 125% extension level, which lies beyond the 100% line on the side away from 0%. With Invert Fibonacci Direction off (default), 100% is the leg start (P2), so this level marks a retracement that has gone past the whole settled leg; with Invert on, 100% is the newest pivot, so it projects the leg further in its own direction. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_150=input(True, '150% ', inline='fbxhi', group=basicgr, tooltip="Allows the 150% extension level, which lies beyond the 100% line on the side away from 0%. With Invert Fibonacci Direction off (default), 100% is the leg start (P2), so this level marks a retracement that has gone past the whole settled leg; with Invert on, 100% is the newest pivot, so it projects the leg further in its own direction. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_160=input(True, '160% ', inline='fbxhi', group=basicgr, tooltip="Allows the 160% extension level, which lies beyond the 100% line on the side away from 0%. With Invert Fibonacci Direction off (default), 100% is the leg start (P2), so this level marks a retracement that has gone past the whole settled leg; with Invert on, 100% is the newest pivot, so it projects the leg further in its own direction. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_200=input(True, '200%', inline='fbxhi', group=basicgr, tooltip="Allows the 200% extension level, which lies beyond the 100% line on the side away from 0%. With Invert Fibonacci Direction off (default), 100% is the leg start (P2), so this level marks a retracement that has gone past the whole settled leg; with Invert on, 100% is the newest pivot, so it projects the leg further in its own direction. When a checked level is actually drawn is controlled by Show Extensions below."),
    fbx_mode=input.string('When Reached', 'Show Extensions', options=('When Reached', 'Always', 'Never'), group=basicgr, tooltip="Controls when the checked extension levels above are drawn.\n• When Reached: a level appears only once price has pushed past the level just inside it (cascading, no gaps).\n• Always: every checked level is drawn at all times, whether or not price has reached it.\n• Never: all extension levels are hidden; only the 0%-100% retracement levels are drawn."),
    dyn_shade_enable=input.bool(True, 'Enable Dynamic Proximity Shading', group=shade_gr, tooltip="Fades each Fibonacci level's line and label based on how close that level's price sits to the current close — including the extension levels beyond 0%-100% (-200% through 200%). The 0% and 100% pivot lines/labels always stay fully opaque."),
    pct_near=input.int(100, 'Nearest Levels Opacity %', minval=0, maxval=100, group=shade_gr, tooltip='Opacity used for the level immediately above the current price and the level immediately below it.'),
    pct_mid=input.int(70, 'Next Levels Opacity %', minval=0, maxval=100, group=shade_gr, tooltip='Opacity used for the second-nearest level above the current price and the second-nearest level below it.'),
    pct_far=input.int(40, 'Remaining Levels Opacity %', minval=0, maxval=100, group=shade_gr, tooltip='Opacity used for every other level, beyond the two nearest on each side of the current price.'),
    palette=input.string('Default', '🎨 Gauge Palette', options=('Custom', 'Default', 'Classic', 'Ocean', 'Sunset', 'Neon', 'Monochrome', 'Desert', 'Oldbook', 'OldWest'), group=view_gr, tooltip="Color palette for the Fibonacci gauge theme: level lines, gauge boxes, gauge close marker and (if Use Trend Colors for Labels is on) labels. Each palette has a bullish-tendency color and a bearish-tendency color, swapped automatically by leg direction and Invert Fibonacci Direction exactly like the theme colors below. The close marker uses the active palette color at 40% transparency. Custom: uses the two theme color swatches and the two gauge highlight swatches below instead."),
    col_bull=input.color(color.rgb(255, 138, 61), 'BEARISH (▲ Now Bullish Tendency / Last Leg: BEARISH)', inline='theme', group=view_gr, tooltip="Custom bearish-tendency theme color, used only while Gauge Palette is Custom. With Invert Fibonacci Direction off (default) it is used when the last settled leg is BULLISH; with Invert on the two theme colors swap and it is used when the last settled leg is BEARISH. Pairs with the other theme color to its right."),
    col_bear=input.color(color.rgb(38, 166, 154), 'BULLISH (▼ Now Bearish Tendency / Last Leg: BULLISH)', inline='theme', group=view_gr, tooltip="Custom bullish-tendency theme color, used only while Gauge Palette is Custom. With Invert Fibonacci Direction off (default) it is used when the last settled leg is BEARISH; with Invert on the two theme colors swap and it is used when the last settled leg is BULLISH. Pairs with the other theme color to its left."),
    lbl_use_theme_color=input.bool(True, 'Use Trend Colors for Labels', inline='lblcol0', group=view_gr, tooltip="When on, the Fibonacci level labels, the gauge extreme label and the level percentages use the same theme color as the lines. Turn off to color the labels independently with the Label ▲ and Label ▼ swatches to the right."),
    lbl_col_bull=input.color(color.rgb(255, 138, 61), 'Label ▲', inline='lblcol0', group=view_gr, tooltip="Label color used when Use Trend Colors for Labels is off, in the same situations as the BEARISH (▲) theme color: last settled leg BULLISH with Invert off, or BEARISH with Invert on."),
    lbl_col_bear=input.color(color.rgb(38, 166, 154), 'Label ▼', inline='lblcol0', group=view_gr, tooltip="Label color used when Use Trend Colors for Labels is off, in the same situations as the BULLISH (▼) theme color: last settled leg BEARISH with Invert off, or BULLISH with Invert on."),
    _lbl_side_raw=input.string('Right', 'Label Side (vs Gauge)', options=('Left', 'Right'), inline='lblside0', group=view_gr, tooltip="Places the Fibonacci level labels to the Left or Right of the gauge tick marks. Left right-aligns the text so it ends at the gauge; Right left-aligns it so it starts at the gauge."),
    fb_guide_draw=input.bool(True, 'Gauge ⁞▌', inline='gauge', group=view_gr, tooltip="Draws the gauge at the right edge: an outer grey box spanning the highest and lowest price reached since the settled leg's newest pivot (P1), extended to include the gauge anchor, an inner colored bar from the anchor to the current close, a label with the extreme price and its % change, and a profit label showing close minus the 0% price. With Invert off (default), the anchor is P1 and the extreme label tracks the retracement side; with Invert on, the anchor is the leg start (P2) and it tracks the continuation side."),
    fb_guide_highlight_bull=input.color(color.rgb(38, 166, 154, 40), 'Bullish Highlight ▲', inline='gauge', group=view_gr, tooltip="Color of the close marker on the gauge's inner bar when the bullish-tendency theme color is active (last settled leg BEARISH with Invert off, or BULLISH with Invert on). Used only while Gauge Palette is Custom."),
    fb_guide_highlight_bear=input.color(color.rgb(255, 138, 61, 40), 'Bearish Highlight ▼', inline='gauge', group=view_gr, tooltip="Color of the close marker on the gauge's inner bar when the bearish-tendency theme color is active (last settled leg BULLISH with Invert off, or BEARISH with Invert on). Used only while Gauge Palette is Custom."),
    fb_gauge_position=input.int(defval=60, title='Gauge X-Offset', inline='pos', group=view_gr, tooltip="Horizontal offset in bars of the gauge, its tick marks and the level labels, measured from the current bar. Negative values move everything left; positive values move it right into the empty space past the last bar. Ignored while Gauge at Leg End is on."),
    fb_line_lenght=input.int(defval=1, minval=1, maxval=9, title='Level Tick Length (Right)', inline='pos', group=view_gr, tooltip="Length in bars (1-9) of the short tick mark drawn to the right of the gauge at each Fibonacci level."),
    fb_pivot_width=input.int(defval=3, minval=1, maxval=10, title='0% / 100% Line Width', group=view_gr, tooltip="Line width in pixels (1-10) of the 0% and 100% Fibonacci lines (the two pivot lines of the last settled leg). All other levels stay at width 1."),
    draw_simplelabel=input.bool(True, 'Show Price on Labels', inline='lbl', group=view_gr, tooltip="Adds the level's price under its percentage on each Fibonacci label. Turn off to show only the percentages."),
    _lbl_size_raw=input.string('Small', 'Label Size', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), inline='lbl', group=view_gr, tooltip="Size (Tiny to Huge) of the Fibonacci level labels, the gauge extreme label and the profit label."),
    show_evt_labels=input.bool(True, 'Show Entry / Target Labels (Left of Gauge)', group=view_gr, tooltip="Adds tiny tags on the left side of the gauge. Entries: 40% = Early Entry 1, 50% = Early Entry 2, 60% = Entry Event 1, 100% = Entry Event 2. Targets: 125% = Target 1, 160% = Target 2, 200% = Target 3. They use the same color and proximity shading as their level's label, and only appear while that level is shown (target tags follow Show Extensions). Hover a tag for its zone (up to the next tag; beyond 200% for Target 3), distance from close, whether price has reached it, and how many bars (and roughly how long) price has closed inside its zone since the leg end (P1)."),
    gauge_at_line_end=input.bool(False, 'Gauge at Leg End  (vs Current Bar)', group=view_gr, tooltip="Positions the gauge and level labels exactly at the end bar of the last settled leg (its newest pivot, P1), where the retracement begins, instead of at the current bar. The older-pivot line stops just before the gauge, while the P1 line and the inner levels run from the gauge to the current bar. While on, Gauge X-Offset is ignored."),
    dash_last_leg=input.bool(True, "Dash Last Leg", inline='lastleg1', group=lastleg_gr, tooltip="Restyles the zigzag's last settled leg (P2 → P1, the leg the Fibonacci levels are measured on) as a dashed line so it stands out. When a new leg takes over, the previous one goes back to solid."),
    mark_last_leg=input.bool(True, "Mark Start/End (Hollow Circles)", inline='lastleg1', group=lastleg_gr, tooltip="Draws hollow circle markers at the start and end pivots (P2 and P1) of the last settled leg. Their size is set by Circle Size below."),
    _lastleg_size_raw=input.string('Normal', 'Circle Size', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), group=lastleg_gr, tooltip="Size (Tiny to Huge) of the hollow circle markers at both ends of the last settled leg. Only has an effect while Mark Start/End is enabled."),
    show_trendpivots=input.bool(True, '⚡ Enable Trend Pivots', group=tp_basicgr, tooltip="Master switch for the visuals of the Trend Pivots section: arrow heads, pivot labels, center line, Bull/Bear labels, support/resistance, fractal-break arrows and the pivot channel. The TP Fractal Break alerts keep evaluating even when this is off."),
    tp_Period=input.int(defval=5, title='Pivot Point Period', minval=1, group=tp_basicgr, tooltip="Bars required on each side of a bar for it to count as a pivot high or low (ta.pivothigh / ta.pivotlow). A pivot is only confirmed this many bars after it forms, so its marker appears N bars late and is drawn back on the pivot bar. Higher values give fewer, more significant pivots. Independent of the zigzag Periods in the other sections."),
    tp_showPPA=input(defval=True, title='Show Pivot Points Arrow Heads', group=tp_basicgr, tooltip="Plots a small triangle at each confirmed pivot: red down-triangles above the bar for pivot highs (HH and LH), green up-triangles below the bar for pivot lows (HL and LL)."),
    tp_showPPL=input(defval=False, title='Show Pivot Points Labels', group=tp_basicgr, tooltip="Draws a label at each confirmed pivot classifying it as HH (higher high), LH (lower high), HL (higher low) or LL (lower low) compared with the previous pivot of the same type. Size, colors and text/arrow mode are set in the Trend Pivots Label Style group."),
    tp_showCL=input(defval=False, title='Show Pivot Points Center Line', group=tp_basicgr, tooltip="Plots a stepped center line: a weighted running average of pivot prices (2/3 previous center, 1/3 newest pivot), updated on each new pivot. It is teal while below hl2 (price above it) and red while above. The Bull/Bear labels are based on it."),
    tp_showLabels=input(defval=False, title='Show Bull/Bear Labels', group=tp_basicgr, tooltip="Shows a Bull label when the close crosses above the center line and a Bear label when it crosses below. Uses the center line calculation whether or not the line itself is displayed."),
    tp_showSR=input(defval=False, title='Show Support/Resistance Level Extensions', group=tp_basicgr, tooltip="Plots circles at the most recent pivot low (support, teal) and pivot high (resistance, orange), held until a new pivot of that type forms and shifted back by the Pivot Point Period so they line up with the pivot bars."),
    tp_showFB=input(False, title='Show Fractal Break Arrows', group=tp_basicgr, tooltip="Plots a green up-triangle when a bar opens at or below the last pivot high and closes above it, and a red down-triangle when a bar opens at or above the last pivot low and closes below it. The TP Fractal Break alerts fire on the same conditions regardless of this setting."),
    tp_ppl_sizeStr=input.string(defval='Tiny', title='Pivot Label Text Size', options=('Auto', 'Tiny', 'Small', 'Normal', 'Large', 'Huge'), group='🏷️ Trend Pivots Label Style', tooltip="Size of the HH/LH/HL/LL pivot labels. Auto lets TradingView scale them with the chart. Only used while Show Pivot Points Labels is enabled."),
    tp_useArrows=input.bool(defval=False, title='Show Directional Arrows Instead of Text (↗ ↘)', group='🏷️ Trend Pivots Label Style', tooltip="Replaces the HH/LH/HL/LL text on the pivot labels with arrows: ↗ for HH and HL, ↘ for LH and LL. Colors still follow the per-type colors below."),
    tp_col_HH=input.color(defval=color.aqua, title='HH Color (Higher High)', inline='tphh', group='🏷️ Trend Pivots Label Style', tooltip="Text color of HH (higher high) pivot labels: a pivot high above the previous pivot high."),
    tp_col_LH=input.color(defval=color.rgb(150, 235, 235), title='LH Color (Lower High)', inline='tplh', group='🏷️ Trend Pivots Label Style', tooltip="Text color of LH (lower high) pivot labels: a pivot high below the previous pivot high."),
    tp_col_LL=input.color(defval=color.red, title='LL Color (Lower Low)', inline='tpll', group='🏷️ Trend Pivots Label Style', tooltip="Text color of LL (lower low) pivot labels: a pivot low below the previous pivot low."),
    tp_col_HL=input.color(defval=color.rgb(255, 150, 150), title='HL Color (Higher Low)', inline='tphl', group='🏷️ Trend Pivots Label Style', tooltip="Text color of HL (higher low) pivot labels: a pivot low above the previous pivot low."),
    tp_ch_show=input.bool(True, 'Show Pivot Channel', group=tp_ch_gr, tooltip="Draws a channel from this section's confirmed pivots: one line through the pivot highs (red arrow heads) and one through the pivot lows (green arrow heads). Uses the Pivot Point Period above. Hidden while Enable Trend Pivots is off."),
    tp_ch_count=input.int(20, 'Pivots Back', minval=2, maxval=200, group=tp_ch_gr, tooltip="How many of the most recent pivot highs and pivot lows each channel line connects. The upper line starts at the Nth-latest pivot high, the lower line at the Nth-latest pivot low, and both run to the latest confirmed pivot of their type."),
    tp_ch_up_col=input.color(color.rgb(255, 0, 0), 'Upper ▲', inline='tpchcol', group=tp_ch_gr, tooltip="Color of the upper channel line (through the pivot highs) and the top end of the gradient shade. Pairs with the Lower color to its right."),
    tp_ch_dn_col=input.color(color.rgb(0, 255, 8), 'Lower ▼', inline='tpchcol', group=tp_ch_gr, tooltip="Color of the lower channel line (through the pivot lows) and the bottom end of the gradient shade. Pairs with the Upper color to its left."),
    tp_ch_style=input.string('Solid', 'Style', options=('Solid', 'Dashed', 'Dotted'), inline='tpchsty', group=tp_ch_gr, tooltip="Line style of both channel lines. Pairs with Width to its right."),
    tp_ch_width=input.int(1, 'Width', minval=1, maxval=5, inline='tpchsty', group=tp_ch_gr, tooltip="Line width in pixels (1-5) of both channel lines. Pairs with Style to its left."),
    tp_ch_shape=input.string('Straight', 'Line Shape', options=('Straight', 'Curved'), group=tp_ch_gr, tooltip="Straight: each channel line is a series of straight segments from pivot to pivot. Curved: each line is drawn as a smooth curve passing through the same pivots, following the direction changes between them. The gradient shade always follows the straight pivot-to-pivot path, so with Curved it can sit slightly inside or outside the curve between pivots."),
    tp_ch_fill=input.bool(False, 'Gradient Shade', inline='tpchfill', group=tp_ch_gr, tooltip="Lightly shades the inside of the channel with a vertical gradient from the Upper color (top) to the Lower color (bottom). Only covers the span where both lines exist. Opacity is set to the right."),
    tp_ch_opacity=input.int(10, 'Opacity %', minval=0, maxval=100, inline='tpchfill', group=tp_ch_gr, tooltip="Opacity of the gradient shade: 0 is invisible, 100 is solid. Low values (5-15) keep candles readable."),
    tp_ch_steps=input.int(8, 'Gradient Steps', minval=2, maxval=20, group=tp_ch_gr, tooltip="Number of color bands used to build the gradient shade. More steps give a smoother blend. Only used while Gradient Shade is on."),
    pc_period=input.int(45, 'Period', minval=10, maxval=100, group=pc_grp_zz, tooltip="ZigZag lookback length in bars. A bar becomes a pivot high (or pivot low) only when it is the highest high (or lowest low) of the last N bars, and pivots of alternating direction are connected into legs. Higher values give fewer, larger, smoother legs that confirm later; lower values give more, smaller, noisier legs that react faster. This one setting drives everything else in this section: leg drawing, phase numbering, and the Adaptive Projection averages."),
    pc_bull_color=input.color(color.rgb(0, 137, 123), 'Bullish Leg', inline='pczzcol', group=pc_grp_zz, tooltip="Color of ZigZag legs that travel upward (price ended the leg higher than it started), including the live Active leg while price is above its starting pivot. Also colors the start/end circle markers of those legs. Pairs with the Bearish Leg color to its right."),
    pc_bear_color=input.color(color.rgb(255, 153, 0), 'Bearish Leg', inline='pczzcol', group=pc_grp_zz, tooltip="Color of ZigZag legs that travel downward (price ended the leg lower than it started), including the live Active leg while price is below its starting pivot. Also colors the start/end circle markers of those legs. Pairs with the Bullish Leg color to its left."),
    pc_confirmed_style=input.string('Solid', 'Confirmed Style', options=('Solid', 'Dashed', 'Dotted'), inline='pczzstyle', group=pc_grp_zz, tooltip="Line style (Solid, Dashed or Dotted) for confirmed, fully settled ZigZag legs. The two most recent legs are styled separately: see Unconfirmed Leg Style and Active Leg Style below. Pairs with the Width input to its right."),
    pc_width=input.int(2, 'Width', minval=1, maxval=8, inline='pczzstyle', group=pc_grp_zz, tooltip="Line width in pixels (1-8) shared by every ZigZag leg: confirmed, unconfirmed and active. Pairs with the Confirmed Style input to its left."),
    pc_active_leg_style=input.string('Dotted', 'Active Leg Style', options=('Solid', 'Dashed', 'Dotted'), group=pc_grp_zz, tooltip="Line style of the Active leg: the still-forming leg drawn from the most recent pivot to the current price on the last bar. It moves with every price update until a new pivot forms and it becomes the Unconfirmed leg."),
    pc_unconfirmed_leg_style=input.string('Dashed', 'Unconfirmed Leg Style', options=('Solid', 'Dashed', 'Dotted'), group=pc_grp_zz, tooltip="Line style of the Unconfirmed leg: the most recent completed pivot-to-pivot leg. Its end pivot can still shift while price keeps making new extremes, so it is styled apart from the older, settled legs, which use the Confirmed Style."),
    pc_show_leg_markers=input.bool(True, 'Mark Active Leg Start/End', inline='pclegmark', group=pc_grp_zz, tooltip="Draws a small circle marker at both ends of the Active leg (its starting pivot and the current price), colored to match the leg's direction. The start-pivot marker size is chosen by the selector to its right; the current-price circle has its own size below."),
    pc_marker_size_choice=input.string('Small', '', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), inline='pclegmark', group=pc_grp_zz, tooltip="Size (Tiny to Huge) of the circle marker at the START pivot of the Active leg. Only has an effect while Mark Active Leg Start/End is enabled."),
    pc_live_marker_size_choice=input.string('Huge', 'Current Price Circle Size', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), group=pc_grp_zz, tooltip="Size (Tiny to Huge) of the circle drawn on the current candle's price (the END of the Active leg). Hover that circle for what is still missing to confirm a new leg / phase (trigger price, distance, how long the trigger holds, what would only stretch the current pivot) plus leg statistics. Only has an effect while Mark Active Leg Start/End is enabled."),
    pc_show_prev_leg_markers=input.bool(True, 'Mark Unconfirmed Leg Start/End', inline='pclegmark2', group=pc_grp_zz, tooltip="Draws a small circle marker at both ends of the Unconfirmed leg (the most recent completed pivot-to-pivot leg), colored to match that leg's direction. The marker size is chosen by the selector to its right."),
    pc_prev_marker_size_choice=input.string('Normal', '', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), inline='pclegmark2', group=pc_grp_zz, tooltip="Size (Tiny to Huge) of the circle markers drawn on the Unconfirmed leg. Only has an effect while Mark Unconfirmed Leg Start/End is enabled."),
    pc_show_projection=input.bool(True, "Show Projection", group=pc_grp_proj, tooltip="Master switch for the Adaptive Projection: two lines drawn forward from the current price. Segment 1 continues the current leg until it reaches the average length of past legs in the same direction (skipped if the leg is already longer than that average). Segment 2 then reverses, using the average length and average slope of past legs in the opposite direction. The averages are taken from every ZigZag leg in this section's history, so the projection adapts as more legs form. The projection never extends more than 500 bars ahead."),
    pc_proj_bull_color=input.color(color.rgb(0, 137, 123), 'Bullish Projection', inline='pcprojcol', group=pc_grp_proj, tooltip="Color of projection segments that move upward. Segment 1 uses this color when the current leg is bullish; Segment 2 uses it when the projected reversal is upward (current leg bearish). Pairs with the Bearish Projection color to its right."),
    pc_proj_bear_color=input.color(color.rgb(255, 153, 0), 'Bearish Projection', inline='pcprojcol', group=pc_grp_proj, tooltip="Color of projection segments that move downward. Segment 1 uses this color when the current leg is bearish; Segment 2 uses it when the projected reversal is downward (current leg bullish). Pairs with the Bullish Projection color to its left."),
    pc_proj_style=input.string("Dotted", "Style", options=("Solid", "Dashed", "Dotted"), inline='pcproj', group=pc_grp_proj, tooltip="Line style (Solid, Dashed or Dotted) of both projection segments. Pairs with the Width input to its right."),
    pc_proj_width=input.int(1, "Width", minval=1, maxval=5, inline='pcproj', group=pc_grp_proj, tooltip="Line width in pixels (1-5) of both projection segments. Pairs with the Style input to its left."),
    pc_anchor_time_1h=input.time(timestamp('2024-01-01 00:00'), "Pivot⚓ (1H)", group=pc_grp_leg, inline='pc1H', tooltip="Date and time of a pivot whose phase number you have verified on the 1H timeframe. When the counter seeds itself it snaps to the ZigZag pivot closest in time to this timestamp, uses it as the numbering reference, then labels every other pivot 1-5 in a repeating cycle forward and backward from it. Only used when the active anchor timeframe is 1h (set by Anchor Timeframe Selection / Anchor Timeframe (Manual)); the other timeframes' anchors are ignored. Choose a real swing pivot you can identify on the chart, and re-check it if you change this section's ZigZag Period, since a different Period may produce different pivots."),
    pc_last_verified_leg_1h=input.int(1, "", minval=1, maxval=5, group=pc_grp_leg, inline='pc1H', tooltip="Phase number (1-5) assigned to the 1H anchor pivot above. Neighboring pivots continue the repeating 1-2-3-4-5 cycle in both directions (older pivots count down, newer ones count up, wrapping from 5 back to 1), and newly confirmed pivots keep extending the count automatically. Only used when the active anchor timeframe is 1h."),
    pc_anchor_time_4h=input.time(timestamp('2026-08-01T11:00:00-0500'), "Pivot⚓ (4H)", group=pc_grp_leg, inline='pc4H', tooltip="Date and time of a pivot whose phase number you have verified on the 4H timeframe. When the counter seeds itself it snaps to the ZigZag pivot closest in time to this timestamp, uses it as the numbering reference, then labels every other pivot 1-5 in a repeating cycle forward and backward from it. Only used when the active anchor timeframe is 4h (set by Anchor Timeframe Selection / Anchor Timeframe (Manual)); the other timeframes' anchors are ignored. Choose a real swing pivot you can identify on the chart, and re-check it if you change this section's ZigZag Period, since a different Period may produce different pivots."),
    pc_last_verified_leg_4h=input.int(1, "", minval=1, maxval=5, group=pc_grp_leg, inline='pc4H', tooltip="Phase number (1-5) assigned to the 4H anchor pivot above. Neighboring pivots continue the repeating 1-2-3-4-5 cycle in both directions (older pivots count down, newer ones count up, wrapping from 5 back to 1), and newly confirmed pivots keep extending the count automatically. Only used when the active anchor timeframe is 4h."),
    pc_anchor_time_1d=input.time(timestamp('2026-05-05 19:00'), "Pivot⚓ (1D)", group=pc_grp_leg, inline='pc1D', tooltip="Date and time of a pivot whose phase number you have verified on the 1D timeframe. When the counter seeds itself it snaps to the ZigZag pivot closest in time to this timestamp, uses it as the numbering reference, then labels every other pivot 1-5 in a repeating cycle forward and backward from it. Only used when the active anchor timeframe is 1d (set by Anchor Timeframe Selection / Anchor Timeframe (Manual)); the other timeframes' anchors are ignored. Choose a real swing pivot you can identify on the chart, and re-check it if you change this section's ZigZag Period, since a different Period may produce different pivots."),
    pc_last_verified_leg_1d=input.int(5, "", minval=1, maxval=5, group=pc_grp_leg, inline='pc1D', tooltip="Phase number (1-5) assigned to the 1D anchor pivot above. Neighboring pivots continue the repeating 1-2-3-4-5 cycle in both directions (older pivots count down, newer ones count up, wrapping from 5 back to 1), and newly confirmed pivots keep extending the count automatically. Only used when the active anchor timeframe is 1d."),
    pc_anchor_time_1w=input.time(timestamp('2024-01-01 00:00'), "Pivot⚓ (1W)", group=pc_grp_leg, inline='pc1W', tooltip="Date and time of a pivot whose phase number you have verified on the 1W timeframe. When the counter seeds itself it snaps to the ZigZag pivot closest in time to this timestamp, uses it as the numbering reference, then labels every other pivot 1-5 in a repeating cycle forward and backward from it. Only used when the active anchor timeframe is 1w (set by Anchor Timeframe Selection / Anchor Timeframe (Manual)); the other timeframes' anchors are ignored. Choose a real swing pivot you can identify on the chart, and re-check it if you change this section's ZigZag Period, since a different Period may produce different pivots."),
    pc_last_verified_leg_1w=input.int(1, "", minval=1, maxval=5, group=pc_grp_leg, inline='pc1W', tooltip="Phase number (1-5) assigned to the 1W anchor pivot above. Neighboring pivots continue the repeating 1-2-3-4-5 cycle in both directions (older pivots count down, newer ones count up, wrapping from 5 back to 1), and newly confirmed pivots keep extending the count automatically. Only used when the active anchor timeframe is 1w."),
    pc_anchor_time_1m=input.time(timestamp('2024-01-01 00:00'), "Pivot⚓ (1M)", group=pc_grp_leg, inline='pc1M', tooltip="Date and time of a pivot whose phase number you have verified on the 1M timeframe. When the counter seeds itself it snaps to the ZigZag pivot closest in time to this timestamp, uses it as the numbering reference, then labels every other pivot 1-5 in a repeating cycle forward and backward from it. Only used when the active anchor timeframe is 1m (set by Anchor Timeframe Selection / Anchor Timeframe (Manual)); the other timeframes' anchors are ignored. Choose a real swing pivot you can identify on the chart, and re-check it if you change this section's ZigZag Period, since a different Period may produce different pivots."),
    pc_last_verified_leg_1m=input.int(1, "", minval=1, maxval=5, group=pc_grp_leg, inline='pc1M', tooltip="Phase number (1-5) assigned to the 1M anchor pivot above. Neighboring pivots continue the repeating 1-2-3-4-5 cycle in both directions (older pivots count down, newer ones count up, wrapping from 5 back to 1), and newly confirmed pivots keep extending the count automatically. Only used when the active anchor timeframe is 1m."),
    pc_anchor_tf_mode=input.string("Automatic", "Anchor Timeframe Selection", options=("Manual", "Automatic"), group=pc_grp_leg, tooltip="Manual: the 'Anchor Timeframe' picker below chooses which saved anchor/leg# setup is active, regardless of what timeframe the chart is actually on — this section only displays when the chart happens to match your pick. Automatic: the script detects the chart's current timeframe itself and switches to that timeframe's saved anchor/leg# automatically, so the same indicator instance keeps working as you flip between 1h/4h/1d/1w/1m charts with no manual switching. On a timeframe outside those 5 presets, Automatic has no saved anchor to use and this section stays silent, same as an unmatched Manual pick."),
    pc_anchor_tf_manual=input.string("1h", "Anchor Timeframe (Manual)", options=("1h", "4h", "1d", "1w", "1m"), group=pc_grp_leg, tooltip="Only used when Anchor Timeframe Selection above is set to Manual. The chart timeframe this anchor/leg-numbering setup was built for. Picking a timeframe here selects which anchor time above is active, and this section (labels + anchor marker) only displays when the chart is actually on this timeframe — so the same indicator instance stays silent and uncluttered on every other timeframe instead of numbering pivots that don't correspond to this setup."),
    pc_show_anchor_marker=input.bool(True, "Mark Anchor Pivot", group=pc_grp_leg, tooltip="Draws a small ⚓ marker on the pivot that was snapped to as the anchor, so you can confirm the right point was picked."),
    pc_char_style=input.string("①②③④⑤", "Numbering Style", options=("①②③④⑤", "❶❷❸❹❺", "Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ", "1️⃣2️⃣3️⃣4️⃣5️⃣", "₍₁₎ ₍₂₎ ₍₃₎ ₍₄₎ ₍₅₎", "⑴ ⑵ ⑶ ⑷ ⑸"), group=pc_grp_leg, tooltip="Glyph set used for phase numbers 1-5 on the chart labels. Some sets (especially the keycap style and the subscript / parenthesized styles) render at different sizes or shapes depending on your OS, browser and font, so pick the one that looks best on your setup."),
    pc_size_choice=input.string("Huge", "Label Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=pc_grp_leg, tooltip="Size (Tiny to Huge) of the phase-number labels drawn on the chart."),
    pc_auto_dir_color=input.bool(True, "Auto-Color by Leg Direction", group=pc_grp_leg, tooltip="When enabled, each label's background and text use the Bullish/Bearish Label colors set below, based on whether that leg's price rose or fell from the prior one (background shown faded per the Fade % below). Disable to use the custom colors below instead."),
    pc_label_bull_color=input.color(color.rgb(0, 137, 123), 'Bullish Label Color', inline='pclblcol', group=pc_grp_leg, tooltip="Color for bullish phases (legs that rise from their pivot to the next). Colors the number label text and its faded background when Auto-Color by Leg Direction is on. Pairs with the Bearish Label Color to its right."),
    pc_label_bear_color=input.color(color.rgb(255, 153, 0), 'Bearish Label Color', inline='pclblcol', group=pc_grp_leg, tooltip="Color for bearish phases (legs that fall from their pivot to the next). Colors the number label text and its faded background when Auto-Color by Leg Direction is on. Pairs with the Bullish Label Color to its left."),
    pc_manual_bg_color=input.color(color.rgb(54, 58, 69, 50), "Custom Label Background Color", group=pc_grp_leg, tooltip="Background color of the number labels when Auto-Color by Leg Direction is off. Label Background Fade % below is applied on top and overrides any transparency set in this color picker."),
    pc_manual_txt_color=input.color(color.rgb(255, 255, 255, 50), "Custom Label Text Color", group=pc_grp_leg, tooltip="Text color of the number labels when Auto-Color by Leg Direction is off. Any transparency set in this color picker is kept as-is."),
    pc_bg_fade_pct=input.int(90, "Label Background Fade %", minval=0, maxval=100, group=pc_grp_leg, tooltip="Transparency of the number label background: 0 is fully opaque, 100 is fully transparent (only the number glyph shows). Applies to both the automatic direction colors and the custom background color, overriding the transparency of the picked color."),
    pc_label_pos=input.string("Leg Midpoint", "Label Position", options=("Pivot", "Leg Midpoint"), group=pc_grp_leg, tooltip="Pivot: label sits on the pivot point itself (original behavior). Leg Midpoint: label sits halfway (in both time and price) along the leg this pivot starts — the leg connecting it to the next numbered pivot. The newest numbered label tracks the leg's live in-progress endpoint until that leg is confirmed, so it walks smoothly toward the eventual midpoint instead of jumping once the leg freezes.")
):
    ts = size.tiny if txtsz == 'Tiny' else size.small if txtsz == 'Small' else size.normal if txtsz == 'Normal' else size.large if txtsz == 'Large' else size.huge

    lastSwingType: PersistentSeries[str] = ""

    swingHighValues: Persistent[list[float]] = array.new_float(0)
    swingHighBarIndexes: Persistent[list[int]] = array.new_int(0)
    swingHighLabels: Persistent[list[Label]] = array.new_label(0)

    swingLowValues: Persistent[list[float]] = array.new_float(0)
    swingLowBarIndexes: Persistent[list[int]] = array.new_int(0)
    swingLowLabels: Persistent[list[Label]] = array.new_label(0)

    highToHighLines: Persistent[list[Line]] = array.new_line(0)
    lowToLowLines: Persistent[list[Line]] = array.new_line(0)
    bullishLines: Persistent[list[Line]] = array.new_line(0)
    bearishLines: Persistent[list[Line]] = array.new_line(0)

    highToHighPriceDiffs: Persistent[list[float]] = array.new_float(0)
    highToHighTimeDiffs: Persistent[list[int]] = array.new_int(0)
    lowToLowPriceDiffs: Persistent[list[float]] = array.new_float(0)
    lowToLowTimeDiffs: Persistent[list[int]] = array.new_int(0)

    bullishPriceDiffs: Persistent[list[float]] = array.new_float(0)
    bullishPrcDiffs: Persistent[list[float]] = array.new_float(0)
    bullishTimeDiffs: Persistent[list[int]] = array.new_int(0)
    bearishPriceDiffs: Persistent[list[float]] = array.new_float(0)
    bearishPrcDiffs: Persistent[list[float]] = array.new_float(0)
    bearishTimeDiffs: Persistent[list[int]] = array.new_int(0)

    pH = high if 0 == ta.highestbars(high, period) else na
    pL = low if 0 == ta.lowestbars(low, period) else na

    def f_addHighSwingPoint(highValue, barIndex):
        oppPriceDiff = highValue - array.get(swingLowValues, 0) if array.size(swingLowValues) > 0 else 0.0
        oppPctDiff = oppPriceDiff / array.get(swingLowValues, 0) * 100 if array.size(swingLowValues) > 0 else 0.0
        oppTimeDiff = barIndex - array.get(swingLowBarIndexes, 0) if array.size(swingLowBarIndexes) > 0 else 0
        sameTimeDiff = barIndex - array.get(swingHighBarIndexes, 0) if array.size(swingHighBarIndexes) > 0 else 0
        patternH: str = ""
        if array.size(swingHighValues) > 0:
            patternH = 'ʜʜ' if highValue > array.get(swingHighValues, 0) else 'ʟʜ'
        labelText: str = ""
        if array.size(swingLowValues) > 0:
            textx = string.tostring(oppPctDiff, format.percent) if delta == 'Percent' else string.tostring(oppPriceDiff, '#.##')
            labelText = string.tostring(patternH) + '\n+' + textx + '\n⏱' + string.tostring(oppTimeDiff)
        if array.size(swingHighValues) > 0 and cyclelab:
            labelText = labelText + '\nʜɪɢʜ ᴄʏᴄʟᴇ\n' + '⏱' + string.tostring(sameTimeDiff)

        newLabel = label.new(barIndex, highValue, labelText, textcolor=color.new('#6BA583'), style=label.style_label_down, color=color.new(color.new('#000000'), 100), size=ts, text_formatting=text.format_bold)

        array.unshift(swingHighValues, highValue)
        array.unshift(swingHighBarIndexes, barIndex)
        array.unshift(swingHighLabels, newLabel)

        if array.size(swingHighValues) > 1:
            prevBar = array.get(swingHighBarIndexes, 1)
            prevValue = array.get(swingHighValues, 1)
            newLine = line.new(prevBar, prevValue, barIndex, highValue, color=rnglineColor, width=1, style=line.style_solid) if rangeLines else na
            array.unshift(highToHighLines, newLine)

            priceDiff = highValue - prevValue
            timeDiff = barIndex - prevBar
            array.unshift(highToHighPriceDiffs, priceDiff)
            array.unshift(highToHighTimeDiffs, timeDiff)

        __block_result__ = na
        if array.size(swingLowValues) > 0 and lastSwingType != 'high':
            prevLowBar = array.get(swingLowBarIndexes, 0)
            prevLowValue = array.get(swingLowValues, 0)
            newBullishLine = line.new(prevLowBar, prevLowValue, barIndex, highValue, color=lineUpColor, width=lw, style=line.style_solid)
            array.unshift(bullishLines, newBullishLine)
            bullishPdiff = highValue - prevLowValue
            bullishTdiff = barIndex - prevLowBar
            array.unshift(bullishPriceDiffs, bullishPdiff)
            array.unshift(bullishPrcDiffs, oppPctDiff)
            __block_result__ = array.unshift(bullishTimeDiffs, bullishTdiff)
        return __block_result__

    def f_updateHighSwingPoint(highValue, barIndex):
        if highValue > array.get(swingHighValues, 0):
            array.set(swingHighValues, 0, highValue)
            array.set(swingHighBarIndexes, 0, barIndex)
            oppPriceDiff = highValue - array.get(swingLowValues, 0) if array.size(swingLowValues) > 0 else 0.0
            oppPctDiff = oppPriceDiff / array.get(swingLowValues, 0) * 100 if array.size(swingLowValues) > 0 else 0.0
            oppTimeDiff = barIndex - array.get(swingLowBarIndexes, 0) if array.size(swingLowBarIndexes) > 0 else 0
            sameTimeDiff = barIndex - array.get(swingHighBarIndexes, 1) if array.size(swingHighBarIndexes) > 1 else 0
            labelText: str = ""
            patternH: str = ""
            if array.size(swingHighValues) > 1:
                patternH = 'ʜʜ' if highValue > array.get(swingHighValues, 1) else 'ʟʜ'
            if array.size(swingLowValues) > 0:
                textx = string.tostring(oppPctDiff, format.percent) if delta == 'Percent' else string.tostring(oppPriceDiff, '#.##')
                labelText = string.tostring(patternH) + '\n+' + textx + '\n⏱' + string.tostring(oppTimeDiff)
            if array.size(swingHighValues) > 1 and cyclelab:
                labelText = labelText + '\nʜɪɢʜ ᴄʏᴄʟᴇ\n' + '⏱' + string.tostring(sameTimeDiff)

            lbl = array.get(swingHighLabels, 0)
            label.set_xy(lbl, barIndex, highValue)
            label.set_text(lbl, labelText)

            if array.size(swingHighValues) > 1 and array.size(highToHighLines) > 0:
                prevBar = array.get(swingHighBarIndexes, 1)
                prevValue = array.get(swingHighValues, 1)
                line.set_xy1(array.get(highToHighLines, 0), array.get(swingHighBarIndexes, 1), array.get(swingHighValues, 1))
                line.set_xy2(array.get(highToHighLines, 0), barIndex, highValue)

                array.set(highToHighPriceDiffs, 0, highValue - prevValue)
                array.set(highToHighTimeDiffs, 0, barIndex - prevBar)

            if array.size(swingLowValues) > 0 and array.size(bullishLines) > 0:
                prevLowBar = array.get(swingLowBarIndexes, 0)
                prevLowValue = array.get(swingLowValues, 0)
                line.set_xy1(array.get(bullishLines, 0), prevLowBar, prevLowValue)
                line.set_xy2(array.get(bullishLines, 0), barIndex, highValue)
                array.set(bullishPriceDiffs, 0, highValue - prevLowValue)
                array.set(bullishPrcDiffs, 0, (highValue - prevLowValue) / prevLowValue * 100)
                array.set(bullishTimeDiffs, 0, barIndex - prevLowBar)
        return 0.0

    def f_addLowSwingPoint(lowValue, barIndex):
        oppPriceDiff = lowValue - array.get(swingHighValues, 0) if array.size(swingHighValues) > 0 else 0.0
        oppPctDiff = oppPriceDiff / array.get(swingHighValues, 0) * 100 if array.size(swingHighValues) > 0 else 0.0
        oppTimeDiff = barIndex - array.get(swingHighBarIndexes, 0) if array.size(swingHighBarIndexes) > 0 else 0
        sameTimeDiff = barIndex - array.get(swingLowBarIndexes, 0) if array.size(swingLowBarIndexes) > 0 else 0
        labelText: str = ""
        patternL: str = ""
        if array.size(swingLowValues) > 0:
            patternL = 'ʟʟ' if lowValue < array.get(swingLowValues, 0) else 'ʜʟ'
        if array.size(swingHighValues) > 0:
            textx = string.tostring(oppPctDiff, format.percent) if delta == 'Percent' else string.tostring(oppPriceDiff, '#.##')
            labelText = string.tostring(patternL) + '\n' + textx + '\n⏱' + string.tostring(oppTimeDiff)
        if array.size(swingLowValues) > 0 and cyclelab:
            labelText = labelText + '\nʟᴏᴡ ᴄʏᴄʟᴇ\n' + '⏱' + string.tostring(sameTimeDiff)

        newLabel = label.new(barIndex, lowValue, labelText, textcolor=color.new('#D75442'), style=label.style_label_up, color=color.new(color.new('#000000'), 100), size=ts, text_formatting=text.format_bold)

        array.unshift(swingLowValues, lowValue)
        array.unshift(swingLowBarIndexes, barIndex)
        array.unshift(swingLowLabels, newLabel)

        if array.size(swingLowValues) > 1:
            prevBar = array.get(swingLowBarIndexes, 1)
            prevValue = array.get(swingLowValues, 1)
            newLine = line.new(prevBar, prevValue, barIndex, lowValue, color=rnglineColor, width=1, style=line.style_solid) if rangeLines else na
            array.unshift(lowToLowLines, newLine)

            priceDiff = lowValue - prevValue
            timeDiff = barIndex - prevBar
            array.unshift(lowToLowPriceDiffs, priceDiff)
            array.unshift(lowToLowTimeDiffs, timeDiff)

        __block_result_1__ = na
        if array.size(swingHighValues) > 0 and lastSwingType != 'low':
            prevHighBar = array.get(swingHighBarIndexes, 0)
            prevHighValue = array.get(swingHighValues, 0)
            newBearishLine = line.new(prevHighBar, prevHighValue, barIndex, lowValue, color=lineDnColor, width=lw, style=line.style_solid)
            array.unshift(bearishLines, newBearishLine)
            bearishPdiff = lowValue - prevHighValue
            bearishTdiff = barIndex - prevHighBar
            array.unshift(bearishPriceDiffs, bearishPdiff)
            array.unshift(bearishPrcDiffs, oppPctDiff)
            __block_result_1__ = array.unshift(bearishTimeDiffs, bearishTdiff)
        return __block_result_1__

    def f_updateLowSwingPoint(lowValue, barIndex):
        if lowValue < array.get(swingLowValues, 0):
            array.set(swingLowValues, 0, lowValue)
            array.set(swingLowBarIndexes, 0, barIndex)
            oppPriceDiff = lowValue - array.get(swingHighValues, 0) if array.size(swingHighValues) > 0 else 0.0
            oppPctDiff = oppPriceDiff / array.get(swingHighValues, 0) * 100 if array.size(swingHighValues) > 0 else 0.0
            oppTimeDiff = barIndex - array.get(swingHighBarIndexes, 0) if array.size(swingHighBarIndexes) > 0 else 0
            sameTimeDiff = barIndex - array.get(swingLowBarIndexes, 1) if array.size(swingLowBarIndexes) > 1 else 0
            labelText: str = ""
            patternL: str = ""
            if array.size(swingLowValues) > 1:
                patternL = 'ʟʟ' if lowValue < array.get(swingLowValues, 1) else 'ʜʟ'
            if array.size(swingHighValues) > 0:
                textx = string.tostring(oppPctDiff, format.percent) if delta == 'Percent' else string.tostring(oppPriceDiff, '#.##')
                labelText = string.tostring(patternL) + '\n' + textx + '\n⏱' + string.tostring(oppTimeDiff)
            if array.size(swingLowValues) > 1 and cyclelab:
                labelText = labelText + '\nʟᴏᴡ ᴄʏᴄʟᴇ\n' + '⏱' + string.tostring(sameTimeDiff)

            lbl = array.get(swingLowLabels, 0)
            label.set_xy(lbl, barIndex, lowValue)
            label.set_text(lbl, labelText)

            if array.size(swingLowValues) > 1 and array.size(lowToLowLines) > 0:
                prevBar = array.get(swingLowBarIndexes, 1)
                prevValue = array.get(swingLowValues, 1)
                line.set_xy1(array.get(lowToLowLines, 0), prevBar, prevValue)
                line.set_xy2(array.get(lowToLowLines, 0), barIndex, lowValue)
                array.set(lowToLowPriceDiffs, 0, lowValue - prevValue)
                array.set(lowToLowTimeDiffs, 0, barIndex - prevBar)

            if array.size(swingHighValues) > 0 and array.size(bearishLines) > 0:
                prevHighBar = array.get(swingHighBarIndexes, 0)
                prevHighValue = array.get(swingHighValues, 0)
                line.set_xy1(array.get(bearishLines, 0), prevHighBar, prevHighValue)
                line.set_xy2(array.get(bearishLines, 0), barIndex, lowValue)
                array.set(bearishPriceDiffs, 0, lowValue - prevHighValue)
                array.set(bearishPrcDiffs, 0, (lowValue - prevHighValue) / prevHighValue * 100)
                array.set(bearishTimeDiffs, 0, barIndex - prevHighBar)
        return 0.0

    if array.size(highToHighLines) > 0 and array.size(lowToLowLines) > 0:
        linefill.new(array.get(highToHighLines, 0), array.get(lowToLowLines, 0), color.rgb(0, 0, 0, 95))

    direction: Persistent[int] = 0
    direction = 1 if not na(pH) and na(pL) else -1 if not na(pL) and na(pH) else direction

    if direction == 1:
        if lastSwingType != 'high':
            f_addHighSwingPoint(pH, bar_index)
            lastSwingType = "high"
        else:
            f_updateHighSwingPoint(pH, bar_index)

    if direction == -1:
        if lastSwingType != 'low':
            f_addLowSwingPoint(pL, bar_index)
            lastSwingType = "low"
        else:
            f_updateLowSwingPoint(pL, bar_index)

    def f_geometric_avg(_source, _condition, _length):
        geom_avg: Persistent[float] = na(float)
        valuesArray: Persistent[list[float]] = array.new_float()
        if _condition:
            if _source > 0:
                array.push(valuesArray, _source)
                while array.size(valuesArray) > _length:
                    array.shift(valuesArray)
            n = array.size(valuesArray)
            if n > 0:
                logSum: float = 0.0
                for val in valuesArray:
                    logSum += math.log(val)
                geom_avg = math.exp(logSum / n)
            else:
                geom_avg = na
        return geom_avg

    sourcebull: Persistent[float] = na(float)
    sourcebear: Persistent[float] = na(float)
    sourcebullt: Persistent[int] = na(int)
    sourcebeart: Persistent[int] = na(int)

    if array.size(bullishPriceDiffs) > 0 and array.size(bullishPrcDiffs) > 0:
        sourcebull = array.get(bullishPrcDiffs, 0) if delta == 'Percent' else array.get(bullishPriceDiffs, 0)
        sourcebullt = array.get(bullishTimeDiffs, 0)
    conditionbull = lastSwingType == 'low' and lastSwingType[1] == 'high'
    rma_valuebull = f_geometric_avg(sourcebull, conditionbull, avgln)
    rma_valuebullt = f_geometric_avg(sourcebullt, conditionbull, avgln)
    if array.size(bearishPriceDiffs) > 0 and array.size(bearishPrcDiffs) > 0:
        sourcebear = array.get(bearishPrcDiffs, 0) if delta == 'Percent' else array.get(bearishPriceDiffs, 0)
        sourcebeart = array.get(bearishTimeDiffs, 0)
    conditionbear = lastSwingType == 'high' and lastSwingType[1] == 'low'
    rma_valuebear = f_geometric_avg(math.abs(sourcebear), conditionbear, avgln)
    rma_timebear = f_geometric_avg(sourcebeart, conditionbear, avgln)

    table_loc: Persistent = position.top_right if locationtable == 'Top Right' else position.bottom_right if locationtable == 'Bottom Right' else position.top_left if locationtable == 'Top Left' else position.bottom_left
    table_size: Persistent = size.large if sizetable == 'Large' else size.normal if sizetable == 'Normal' else size.small if sizetable == 'Small' else size.tiny
    table__ren__: Persistent = table.new(table_loc, 16, 16, color.new('#2A2E39'), color.new('#1E1E1E'), 2, color.new('#1F232F'), 2) if showtable else na
    def table_cell(column, row, txt):
        return table.cell(table__ren__, column, row, txt, 0, 0, color.new('#FFFFFF'), text_size=table_size)

    if barstate.islast and showtable:
        table_cell(0, 0, 'STATISTICS TABLE')
        table_cell(0, 1, 'ɢᴇᴏᴍᴇᴛʀɪᴄ\nᴀᴠᴇʀᴀɢɪɴɢ')
        table_cell(1, 1, '𝞓 ᴘʀɪᴄᴇ')
        table_cell(2, 1, '𝞓 ᴛɪᴍᴇ')
        table_cell(0, 2, 'ᴜᴘᴛʀᴇɴᴅ')
        table_cell(0, 3, 'ᴅᴏᴡɴᴛʀᴇɴᴅ')
        table_cell(1, 2, '+' + string.tostring(rma_valuebull, format.percent if delta == 'Percent' else format.mintick))
        table_cell(1, 3, '-' + string.tostring(rma_valuebear, format.percent if delta == 'Percent' else format.mintick))
        table_cell(2, 2, string.tostring(rma_valuebullt, format.mintick))
        table_cell(2, 3, string.tostring(rma_timebear, format.mintick))
        table.cell_set_text_font_family(table__ren__, 0, 0, font.family_monospace)
        table.cell_set_text_formatting(table__ren__, 1, 1, text.format_bold)
        table.cell_set_text_formatting(table__ren__, 2, 1, text.format_bold)
        table.cell_set_text_formatting(table__ren__, 0, 2, text.format_bold)
        table.cell_set_text_formatting(table__ren__, 0, 3, text.format_bold)
        table.cell_set_text_color(table__ren__, 0, 1, color.gray)
        table.cell_set_text_size(table__ren__, 0, 1, size.small)
        table.merge_cells(table__ren__, 0, 0, 2, 0)

    COLOR_TRANSP: Persistent = color.rgb(255, 255, 255, 100)

    __block_result_2__ = na
    __switch__ = _close_plot_style_raw
    if __switch__ == 'Line':
        __block_result_2__ = plot.style_line
    elif __switch__ == 'Stepline':
        __block_result_2__ = plot.style_stepline
    elif __switch__ == 'Histogram':
        __block_result_2__ = plot.style_histogram
    elif __switch__ == 'Cross':
        __block_result_2__ = plot.style_cross
    elif __switch__ == 'Area':
        __block_result_2__ = plot.style_area
    elif __switch__ == 'Columns':
        __block_result_2__ = plot.style_columns
    elif __switch__ == 'Circles':
        __block_result_2__ = plot.style_circles
    else:
        __block_result_2__ = plot.style_line
    close_plot_style = __block_result_2__

    plot(close if show_close_plot else na, title='Close', color=close_plot_color, linewidth=close_plot_width, style=close_plot_style)


    bullColI = col_bear
    bearColI = col_bull

    __block_result_3__ = na
    __switch__ = palette
    if __switch__ == "Classic":
        __block_result_3__ = color.rgb(0, 177, 171)
    elif __switch__ == "Ocean":
        __block_result_3__ = color.rgb(0, 104, 179)
    elif __switch__ == "Sunset":
        __block_result_3__ = color.rgb(180, 108, 0)
    elif __switch__ == "Neon":
        __block_result_3__ = color.rgb(0, 105, 190)
    elif __switch__ == "Monochrome":
        __block_result_3__ = color.rgb(172, 172, 172)
    elif __switch__ == "Desert":
        __block_result_3__ = color.rgb(0, 179, 161)
    elif __switch__ == "Oldbook":
        __block_result_3__ = color.rgb(139, 163, 0)
    elif __switch__ == "OldWest":
        __block_result_3__ = color.rgb(148, 182, 0)
    elif __switch__ == "Default":
        __block_result_3__ = color.rgb(0, 187, 140)
    else:
        __block_result_3__ = bullColI
    bullBase: Color = __block_result_3__

    __block_result_4__ = na
    __switch__ = palette
    if __switch__ == "Classic":
        __block_result_4__ = color.rgb(182, 0, 0)
    elif __switch__ == "Ocean":
        __block_result_4__ = color.rgb(0, 43, 185)
    elif __switch__ == "Sunset":
        __block_result_4__ = color.rgb(151, 147, 140)
    elif __switch__ == "Neon":
        __block_result_4__ = color.rgb(112, 119, 133)
    elif __switch__ == "Monochrome":
        __block_result_4__ = color.rgb(119, 116, 116)
    elif __switch__ == "Desert":
        __block_result_4__ = color.rgb(173, 104, 0)
    elif __switch__ == "Oldbook":
        __block_result_4__ = color.rgb(168, 146, 0)
    elif __switch__ == "OldWest":
        __block_result_4__ = color.rgb(165, 33, 0)
    elif __switch__ == "Default":
        __block_result_4__ = color.rgb(206, 0, 0)
    else:
        __block_result_4__ = bearColI
    bearBase: Color = __block_result_4__
    lbl_style = label.style_label_right if _lbl_side_raw == 'Left' else label.style_label_left
    lbl_align = text.align_right if _lbl_side_raw == 'Left' else text.align_left

    __block_result_5__ = na
    __switch__ = _lbl_size_raw
    if __switch__ == 'Tiny':
        __block_result_5__ = size.tiny
    elif __switch__ == 'Small':
        __block_result_5__ = size.small
    elif __switch__ == 'Normal':
        __block_result_5__ = size.normal
    elif __switch__ == 'Large':
        __block_result_5__ = size.large
    elif __switch__ == 'Huge':
        __block_result_5__ = size.huge
    else:
        __block_result_5__ = size.small
    fb_lbl_size = __block_result_5__

    __block_result_6__ = na
    __switch__ = _lastleg_size_raw
    if __switch__ == 'Tiny':
        __block_result_6__ = size.tiny
    elif __switch__ == 'Small':
        __block_result_6__ = size.small
    elif __switch__ == 'Normal':
        __block_result_6__ = size.normal
    elif __switch__ == 'Large':
        __block_result_6__ = size.large
    elif __switch__ == 'Huge':
        __block_result_6__ = size.huge
    else:
        __block_result_6__ = size.normal
    lastleg_mark_size = __block_result_6__

    fb_lineLast: Persistent[Line] = na(Line)
    fb_pLast: Persistent[float] = 0.0
    fb_iLast: Persistent[int] = 0
    fb_isHighLast: Persistent[bool] = False

    fb_new_line: bool = False

    if lastSwingType == 'high' and array.size(bearishLines) > 0:
        fb_new_line = fb_lineLast != array.get(bearishLines, 0)
        fb_lineLast = array.get(bearishLines, 0)
        fb_pLast = array.get(swingLowValues, 0)
        fb_iLast = array.get(swingLowBarIndexes, 0)
        fb_isHighLast = False

    if lastSwingType == 'low' and array.size(bullishLines) > 0:
        fb_new_line = fb_lineLast != array.get(bullishLines, 0)
        fb_lineLast = array.get(bullishLines, 0)
        fb_pLast = array.get(swingHighValues, 0)
        fb_iLast = array.get(swingHighBarIndexes, 0)
        fb_isHighLast = True

    fb_p0 = line.get_y1(fb_lineLast) if fb_invert else fb_pLast
    fb_p100 = fb_pLast if fb_invert else line.get_y1(fb_lineLast)

    hl_activeLine: Persistent[Line] = na(Line)
    hl_circleStart: Persistent[Label] = na(Label)
    hl_circleEnd: Persistent[Label] = na(Label)
    hl_visible: Persistent[bool] = False

    if (dash_last_leg or mark_last_leg) and (not na(fb_lineLast)):
        if fb_new_line and (not na(hl_activeLine)) and (hl_activeLine != fb_lineLast):
            _prevLegColor = lineDnColor if fb_isHighLast else lineUpColor
            line.set_style(hl_activeLine, line.style_solid)
            line.set_width(hl_activeLine, lw)
            line.set_color(hl_activeLine, _prevLegColor)

        _hlColor = lineUpColor if fb_isHighLast else lineDnColor

        if dash_last_leg:
            line.set_style(fb_lineLast, line.style_dashed)
            line.set_width(fb_lineLast, lw)
            line.set_color(fb_lineLast, _hlColor)

        if mark_last_leg:
            if na(hl_circleStart):
                hl_circleStart = label.new(line.get_x1(fb_lineLast), line.get_y1(fb_lineLast), '◯', style=label.style_label_center, color=color.new(color.new('#000000'), 100), textcolor=_hlColor, size=lastleg_mark_size)
                hl_circleEnd = label.new(line.get_x2(fb_lineLast), line.get_y2(fb_lineLast), '◯', style=label.style_label_center, color=color.new(color.new('#000000'), 100), textcolor=_hlColor, size=lastleg_mark_size)

            label.set_xy(hl_circleStart, line.get_x1(fb_lineLast), line.get_y1(fb_lineLast))
            label.set_textcolor(hl_circleStart, _hlColor)
            label.set_size(hl_circleStart, lastleg_mark_size)

            label.set_xy(hl_circleEnd, line.get_x2(fb_lineLast), line.get_y2(fb_lineLast))
            label.set_textcolor(hl_circleEnd, _hlColor)
            label.set_size(hl_circleEnd, lastleg_mark_size)
        elif hl_visible:
            label.delete(hl_circleStart)
            label.delete(hl_circleEnd)
            hl_circleStart = na
            hl_circleEnd = na

        hl_activeLine = fb_lineLast
        hl_visible = True

    if not (dash_last_leg or mark_last_leg) and hl_visible:
        if not na(hl_activeLine):
            _revertColor = lineUpColor if fb_isHighLast else lineDnColor
            line.set_style(hl_activeLine, line.style_solid)
            line.set_width(hl_activeLine, lw)
            line.set_color(hl_activeLine, _revertColor)
        if not na(hl_circleStart):
            label.delete(hl_circleStart)
            label.delete(hl_circleEnd)
            hl_circleStart = na
            hl_circleEnd = na
        hl_visible = False

    def f_dur(_bars):
        _s = _bars * timeframe.in_seconds()
        _d = math.floor(_s / 86400)
        _h = math.floor(_s % 86400 / 3600)
        _m = math.floor(_s % 3600 / 60)
        return string.tostring(_d) + 'd ' + string.tostring(_h) + 'h' if _d > 0 else string.tostring(_h) + 'h ' + string.tostring(_m) + 'm' if _h > 0 else string.tostring(_m) + 'm'

    def f_tagZoneHi(_lvl):
        return 0.5 if _lvl == 0.4 else 0.6 if _lvl == 0.5 else 1.0 if _lvl == 0.6 else 1.25 if _lvl == 1.0 else 1.6 if _lvl == 1.25 else 2.0 if _lvl == 1.6 else na

    def f_tagTip(_name, _lvl, _price, _legEndX):
        _den = fb_p100 - fb_p0
        _tip: str = ''
        if _den != 0:
            _zHi: float = f_tagZoneHi(_lvl)
            _n = math.min(math.max(bar_index - _legEndX, 0), 3999)
            _runMin: float = 10000000000.0
            _runMax = -10000000000.0
            _firstTouchAgo = -1
            _inZone: int = 0
            _streak: int = 0
            _lastInAgo = -1
            for i in pine_range(_n, 0):
                _tH = (high[i] - fb_p0) / _den
                _tL = (low[i] - fb_p0) / _den
                _runMin = math.min(_runMin, _tH, _tL)
                _runMax = math.max(_runMax, _tH, _tL)
                if _firstTouchAgo < 0 and _runMin <= _lvl and (_runMax >= _lvl):
                    _firstTouchAgo = i
                _tC = (close[i] - fb_p0) / _den
                _in = _tC >= _lvl if na(_zHi) else _tC >= _lvl and _tC <= _zHi
                if _in:
                    _inZone += 1
                    _streak += 1
                    _lastInAgo = i
                else:
                    _streak = 0

            _tNow = (close - fb_p0) / _den
            _dist = _price - close
            _distPct = _dist / close * 100
            _barsTotal = _n + 1
            _share = cast_float(_inZone) / _barsTotal * 100
            _zLoPx = fb_p0 + _den * _lvl
            _zoneTxt = 'beyond ' + string.tostring(_lvl * 100, '0') + '% (' + string.tostring(_zLoPx, '$0,000') + ')' if na(_zHi) else string.tostring(_lvl * 100, '0') + '% → ' + string.tostring(_zHi * 100, '0') + '%  (' + string.tostring(_zLoPx, '$0,000') + ' – ' + string.tostring(fb_p0 + _den * _zHi, '$0,000') + ')'
            _statusTxt = 'Reached · first touch ' + string.tostring(_firstTouchAgo) + ' bars ago (≈' + f_dur(_firstTouchAgo) + ')' if _firstTouchAgo >= 0 else 'Not reached yet'
            _streakTxt = 'In zone now · ' + string.tostring(_streak) + ' bars in a row (≈' + f_dur(_streak) + ')' if _streak > 0 else 'Outside zone · last close in zone ' + string.tostring(_lastInAgo) + ' bars ago' if _lastInAgo >= 0 else 'No close in this zone since P1'
            _tip = string.replace_all(_name, '\n', ' ') + ' · ' + string.tostring(_lvl * 100, '0') + '% · ' + string.tostring(_price, '$0,000') + '\nZone: ' + _zoneTxt + '\nClose ' + string.tostring(close, '$0,000') + ' · retraced ' + string.tostring(_tNow * 100, '0.0') + '% of leg' + '\nDistance: ' + ('+' if _dist >= 0 else '') + string.tostring(_dist, '$#,##0') + ' (' + ('+' if _dist >= 0 else '') + string.tostring(_distPct, '0.00') + '%) ' + ('above close' if _dist >= 0 else 'below close') + '\nStatus: ' + _statusTxt + '\nSince P1 (' + string.tostring(_barsTotal) + ' bars, ≈' + f_dur(_barsTotal) + '): ' + string.tostring(_inZone) + ' closes in zone (' + string.tostring(_share, '0') + '%)' + '\n' + _streakTxt
        return _tip

    def fb_retracement(_show, _fib_level, _switch, _shadeTrans = 0.0):
        __block_result_7__ = na
        if not show_indicator:
            __block_result_7__ = NA(bool)
        else:
            _clrHigh = not fb_isHighLast if fb_invert else fb_isHighLast
            _col = bearBase if _clrHigh else bullBase
            _lbl_col = _col if lbl_use_theme_color else lbl_col_bull if _clrHigh else lbl_col_bear
            _gauge_hl = (fb_guide_highlight_bear if _clrHigh else fb_guide_highlight_bull) if palette == 'Custom' else color.new(_col, 40)

            _price = fb_p0 + (fb_p100 - fb_p0) * _fib_level
            _position = bar_index - line.get_x2(fb_lineLast)
            _gAnchor = fb_p0
            _fbr_max_highest = math.max(ta.highest(high, nz(math.max(1, _position), 1)), fb_pLast, _gAnchor)
            _fbr_min_lowest = math.min(ta.lowest(low, nz(math.max(1, _position), 1)), fb_pLast, _gAnchor)

            _legEndX = line.get_x2(fb_lineLast)
            _gauge_x = _legEndX if gauge_at_line_end else bar_index + fb_gauge_position

            if _switch == 'auto' and (not na(fb_lineLast)):
                fibo_id_auto: Series = line.new(line.get_x2(fb_lineLast), _price, bar_index + 6, _price, style=line.style_solid, color=color.new(_col, _shadeTrans), width=1, extend=extend.none)
                fibo_id_ext_auto: Series = line.new(_gauge_x - 2, _price, _gauge_x + 1, _price, color=color.new(_col, _shadeTrans), width=1, extend=extend.none)
                fb_label_auto: Series = label.new(x=_gauge_x, y=_price, text=string.tostring(math.round(_fib_level, 2), '000%') + ('\n' + string.tostring(_price, ' $00,000') if draw_simplelabel else ''), textcolor=color.new(_lbl_col, _shadeTrans), style=lbl_style, textalign=lbl_align, color=color.new('#00000000'), size=fb_lbl_size)
                line.delete(fibo_id_auto[1])
                line.delete(fibo_id_ext_auto[1])
                label.delete(fb_label_auto[1])
                if not _show:
                    line.delete(fibo_id_auto)
                    line.delete(fibo_id_ext_auto)
                    label.delete(fb_label_auto)

                _tgtTxt = 'Event\nTarget 1' if _fib_level == 1.25 else 'Event\nTarget 2' if _fib_level == 1.6 else 'Event\nTarget 3' if _fib_level == 2.0 else ''
                if _tgtTxt != '':
                    fb_tgt_label: Persistent[Label] = na(Label)
                    if show_evt_labels and _show:
                        if na(fb_tgt_label):
                            fb_tgt_label = label.new(_gauge_x, _price, _tgtTxt, style=label.style_label_right, textalign=text.align_right, color=color.new('#00000000'), size=size.tiny)
                        label.set_xy(fb_tgt_label, _gauge_x, _price)
                        label.set_text(fb_tgt_label, _tgtTxt)
                        label.set_textcolor(fb_tgt_label, color.new(_lbl_col, _shadeTrans))
                        if barstate.islast:
                            label.set_tooltip(fb_tgt_label, f_tagTip(_tgtTxt, _fib_level, _price, _legEndX))
                    elif not na(fb_tgt_label):
                        label.delete(fb_tgt_label)
                        fb_tgt_label = na

            if _show and _switch == '':
                fibo_id: Persistent = line.new(fb_iLast, _price, bar_index, _price, color=color.new(_col, 0), width=2, extend=extend.none, style=line.style_solid)
                fibo_id_ext: Persistent = line.new(fb_iLast, _price, bar_index, _price, color=color.new(_col, 0), width=2, extend=extend.none, style=line.style_solid)
                fb_label: Persistent = label.new(x=bar_index, y=_price, text='', textcolor=COLOR_TRANSP, style=lbl_style, textalign=lbl_align, color=color.rgb(0, 0, 0, 100), size=fb_lbl_size)

                if not na(fb_lineLast):
                    _lvlTrans = 0.0 if _fib_level == 0.0 or _fib_level == 1.0 else _shadeTrans

                    _olderLvl = 0.0 if fb_invert else 1.0

                    _isPivotLvl = _fib_level == 0.0 or _fib_level == 1.0
                    _lineX1 = line.get_x1(fb_lineLast) if _fib_level == _olderLvl else _legEndX

                    _lineX2 = (math.max(_lineX1, _gauge_x - 2) if _fib_level == _olderLvl else bar_index) if gauge_at_line_end else _gauge_x - 2 if _isPivotLvl else bar_index
                    line.set_xy1(fibo_id, _lineX1, _price)
                    line.set_xy2(fibo_id, _lineX2, _price)
                    line.set_color(fibo_id, color.new(_col, _lvlTrans))
                    line.set_style(fibo_id, line.style_solid if _fib_level == 0.0 or _fib_level == 1.0 else line.style_dotted)
                    line.set_width(fibo_id, fb_pivot_width if _fib_level == 0.0 or _fib_level == 1.0 else 1)

                    line.set_xy1(fibo_id_ext, _gauge_x - 1, _price)
                    line.set_xy2(fibo_id_ext, _gauge_x + fb_line_lenght, _price)
                    line.set_color(fibo_id_ext, color.new(_col, _lvlTrans))
                    line.set_width(fibo_id_ext, 2 if _fib_level == 0.0 or _fib_level == 1.0 or _fib_level == 0.6 else 1)

                    label.set_xy(fb_label, _gauge_x, _price)
                    label.set_text(fb_label, string.tostring(math.round(_fib_level, 2), '00%') + ('\n' + string.tostring(_price, '$0,000') if draw_simplelabel else ''))
                    label.set_tooltip(fb_label, string.tostring((_price - fb_p0) / fb_p0 * 100, format.percent) + ' ' + string.tostring(math.round(_price - fb_p0, 0), '$00,000') + ' from 00% ' + string.tostring(math.round(fb_p0, 0), '$00,000'))
                    label.set_textcolor(fb_label, color.new(_lbl_col, _lvlTrans))
                    label.set_size(fb_label, fb_lbl_size)

                    _evtTxt = 'Early\nEntry 1' if _fib_level == 0.4 else 'Early\nEntry 2' if _fib_level == 0.5 else 'Entry\nEvent 1' if _fib_level == 0.6 else 'Entry\nEvent 2' if _fib_level == 1.0 else ''
                    if _evtTxt != '':
                        fb_evt_label: Persistent[Label] = na(Label)
                        if show_evt_labels:
                            if na(fb_evt_label):
                                fb_evt_label = label.new(_gauge_x, _price, _evtTxt, style=label.style_label_right, textalign=text.align_right, color=color.new('#00000000'), size=size.tiny)
                            label.set_xy(fb_evt_label, _gauge_x, _price)
                            label.set_text(fb_evt_label, _evtTxt)
                            label.set_textcolor(fb_evt_label, color.new(_lbl_col, _lvlTrans))

                            if barstate.islast:
                                label.set_tooltip(fb_evt_label, f_tagTip(_evtTxt, _fib_level, _price, _legEndX))
                        elif not na(fb_evt_label):
                            label.delete(fb_evt_label)
                            fb_evt_label = na

                    if _fib_level == 1.0:
                        fibo_box_max: Persistent[Box] = na(Box)
                        fibo_line_max: Persistent[Line] = na(Line)
                        fibo_line_min: Persistent[Line] = na(Line)
                        fibo_box_ext: Persistent[Box] = na(Box)
                        fibo_line_ext: Persistent[Line] = na(Line)
                        fibo_extreme_label: Persistent[Label] = na(Label)
                        fibo_gauge_visible: Persistent[bool] = False

                        if fb_guide_draw:
                            _extreme_price = _fbr_min_lowest if _clrHigh else _fbr_max_highest
                            _extreme_chg = (_extreme_price - _gAnchor) / _gAnchor * 100
                            _extreme_sign = '▲ ' if _extreme_chg >= 0 else '▼ '
                            _extreme_txt = _extreme_sign + string.tostring(_extreme_price, '$0,000') + '\n' + string.tostring(math.round(_extreme_chg, 2), '0.0') + '%'

                            if not fibo_gauge_visible:
                                fibo_box_max = box.new(bar_index, close, bar_index, _gAnchor, border_color=color.new(_col, 50), border_width=1, border_style=line.style_dotted, bgcolor=color.new(color.black, 80), text='AFR', text_valign=text.align_top, text_size=size.tiny, text_color=color.white)
                                fibo_line_max = line.new(bar_index, close, bar_index, _gAnchor, color=color.white, width=1)
                                fibo_line_min = line.new(bar_index, close, bar_index, _gAnchor, color=_col, width=1)

                                fibo_box_ext = box.new(bar_index, close, bar_index, _gAnchor, border_color=color.new(_col, 70), border_width=5, bgcolor=color.new(_col, 70))
                                fibo_line_ext = line.new(bar_index, close, bar_index, _gAnchor, color=_gauge_hl, width=4)
                                fibo_extreme_label = label.new(x=_gauge_x - 2, y=_extreme_price, text=_extreme_txt, textcolor=color.new(_lbl_col, 0), style=label.style_label_right, textalign=text.align_right, color=color.new(_col, 90), size=fb_lbl_size)
                                fibo_gauge_visible = True

                            box.set_lefttop(fibo_box_max, _gauge_x - 1, _fbr_max_highest)
                            box.set_rightbottom(fibo_box_max, _gauge_x + 1, _fbr_min_lowest)
                            box.set_border_color(fibo_box_max, color.rgb(73, 73, 73, 30))
                            box.set_bgcolor(fibo_box_max, color.rgb(73, 73, 73, 50))
                            box.set_text_color(fibo_box_max, color.white)
                            line.set_xy1(fibo_line_max, _gauge_x - 1, _fbr_max_highest)
                            line.set_xy2(fibo_line_max, _gauge_x + 1, _fbr_max_highest)
                            line.set_xy1(fibo_line_min, _gauge_x - 1, _fbr_min_lowest)
                            line.set_xy2(fibo_line_min, _gauge_x + 1, _fbr_min_lowest)
                            line.set_color(fibo_line_min, _col)

                            box.set_lefttop(fibo_box_ext, _gauge_x, close)
                            box.set_rightbottom(fibo_box_ext, _gauge_x, _gAnchor)
                            box.set_border_color(fibo_box_ext, color.new(_col, 50))
                            box.set_bgcolor(fibo_box_ext, color.new(_col, 70))
                            line.set_xy1(fibo_line_ext, _gauge_x, close)
                            line.set_xy2(fibo_line_ext, _gauge_x, close)
                            line.set_color(fibo_line_ext, _gauge_hl)

                            label.set_xy(fibo_extreme_label, _gauge_x - 0, _extreme_price)
                            label.set_text(fibo_extreme_label, _extreme_txt)
                            label.set_textcolor(fibo_extreme_label, color.new(_lbl_col, 0))
                            label.set_color(fibo_extreme_label, color.new(_col, 90))
                            label.set_size(fibo_extreme_label, fb_lbl_size)
                            label.set_style(fibo_extreme_label, label.style_label_right)
                            label.set_textalign(fibo_extreme_label, text.align_right)

                        if not fb_guide_draw and fibo_gauge_visible:
                            box.delete(fibo_box_max)
                            line.delete(fibo_line_max)
                            line.delete(fibo_line_min)
                            box.delete(fibo_box_ext)
                            line.delete(fibo_line_ext)
                            label.delete(fibo_extreme_label)
                            fibo_gauge_visible = False

                    if _fib_level == 0.0:
                        fibo_prof_label: Persistent[Label] = na(Label)
                        fibo_prof_visible: Persistent[bool] = False

                        if fb_guide_draw:
                            _profit_txt = string.tostring(math.round(close - fb_p0, 0), '$0,000')
                            if not fibo_prof_visible:
                                fibo_prof_label = label.new(bar_index, close, _profit_txt, size=fb_lbl_size)
                                fibo_prof_visible = True
                            label.set_xy(fibo_prof_label, _gauge_x + 4, close - 100)
                            label.set_text(fibo_prof_label, _profit_txt)
                            label.set_tooltip(fibo_prof_label, string.tostring((close - fb_p0) / fb_p0 * 100, format.percent) + ' ' + _profit_txt + ' from 00% ' + string.tostring(math.round(fb_p0, 0), '$00,000'))
                            label.set_color(fibo_prof_label, color.new(_col, 100))
                            label.set_textcolor(fibo_prof_label, color.white)
                            label.set_size(fibo_prof_label, fb_lbl_size)
                            label.set_style(fibo_prof_label, label.style_label_right)
                            label.set_textalign(fibo_prof_label, text.align_right)

                        if not fb_guide_draw and fibo_prof_visible:
                            label.delete(fibo_prof_label)
                            fibo_prof_visible = False

            __block_result_7__ = NA(bool)
        return __block_result_7__

    fb_height = fb_p100 - fb_p0
    fb_k_low_cr = ta.lowest(low, 2)
    fb_k_high_cr = ta.highest(high, 2)

    def f_ext_reached(_m, _aboveHundred):
        _lvl = fb_p0 + fb_height * _m
        _useHigh = fb_height > 0 if _aboveHundred else fb_height < 0
        return fb_k_high_cr > _lvl if _useHigh else fb_k_low_cr < _lvl

    fb_under_0 = f_ext_reached(0.0, False)
    fb_under_1000 = f_ext_reached(-0.25, False)
    fb_under_1500 = f_ext_reached(-0.5, False)
    fb_under_2000 = f_ext_reached(-1.0, False)
    fb_under_m160 = f_ext_reached(-1.5, False)
    fb_under_m1 = f_ext_reached(-1.6, False)

    fb_over_1250 = f_ext_reached(1.0, True)
    fb_over_1500 = f_ext_reached(1.25, True)
    fb_over_1600 = f_ext_reached(1.5, True)
    fb_over_2000 = f_ext_reached(1.6, True)

    fb_ext_on = fbx_mode != 'Never'
    fb_ext_always = fbx_mode == 'Always'

    fb_show_m25 = fb_ext_on and fbx_m25 and (fb_ext_always or fb_under_0)
    fb_show_m50 = fb_ext_on and fbx_m50 and (fb_ext_always or fb_under_1000)
    fb_show_m100 = fb_ext_on and fbx_m100 and (fb_ext_always or fb_under_1500)
    fb_show_m150 = fb_ext_on and fbx_m150 and (fb_ext_always or fb_under_2000)
    fb_show_m160 = fb_ext_on and fbx_m160 and (fb_ext_always or fb_under_m160)
    fb_show_m200 = fb_ext_on and fbx_m200 and (fb_ext_always or fb_under_m1)
    fb_show_125 = fb_ext_on and fbx_125 and (fb_ext_always or fb_over_1250)
    fb_show_150 = fb_ext_on and fbx_150 and (fb_ext_always or fb_over_1500)
    fb_show_160 = fb_ext_on and fbx_160 and (fb_ext_always or fb_over_1600)
    fb_show_200 = fb_ext_on and fbx_200 and (fb_ext_always or fb_over_2000)

    trans_0: float = 0.0
    trans_100: float = 0.0
    trans_25: float = 0.0
    trans_40: float = 0.0
    trans_50: float = 0.0
    trans_60: float = 0.0
    trans_75: float = 0.0
    trans_90: float = 0.0
    trans_m25: float = 0.0
    trans_m50: float = 0.0
    trans_m100: float = 0.0
    trans_m150: float = 0.0
    trans_m160: float = 0.0
    trans_m200: float = 0.0
    trans_125: float = 0.0
    trans_150: float = 0.0
    trans_160: float = 0.0
    trans_200: float = 0.0

    if dyn_shade_enable and (not na(fb_lineLast)):
        _endpoint = fb_p100
        lvl_prices: list[float] = array.new_float(0)
        lvl_slots: list[int] = array.new_int(0)

        if fb250:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.25)
            array.push(lvl_slots, 0)
        if fb400:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.4)
            array.push(lvl_slots, 1)
        if fb500:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.5)
            array.push(lvl_slots, 2)
        if fb600:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.6)
            array.push(lvl_slots, 3)
        if fb750:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.75)
            array.push(lvl_slots, 4)
        if fb900:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 0.9)
            array.push(lvl_slots, 5)

        if fb_show_m25:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -0.25)
            array.push(lvl_slots, 6)
        if fb_show_m50:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -0.5)
            array.push(lvl_slots, 7)
        if fb_show_m100:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -1.0)
            array.push(lvl_slots, 8)
        if fb_show_m150:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -1.5)
            array.push(lvl_slots, 9)
        if fb_show_m160:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -1.6)
            array.push(lvl_slots, 14)
        if fb_show_m200:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * -2.0)
            array.push(lvl_slots, 10)
        if fb_show_125:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 1.25)
            array.push(lvl_slots, 11)
        if fb_show_150:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 1.5)
            array.push(lvl_slots, 12)
        if fb_show_160:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 1.6)
            array.push(lvl_slots, 15)
        if fb_show_200:
            array.push(lvl_prices, fb_p0 + (_endpoint - fb_p0) * 2.0)
            array.push(lvl_slots, 13)

        idxAbove: list[int] = array.new_int(0)
        idxBelow: list[int] = array.new_int(0)
        pxAbove: list[float] = array.new_float(0)
        pxBelow: list[float] = array.new_float(0)
        for i in pine_range(0, array.size(lvl_prices) - 1):
            p = array.get(lvl_prices, i)
            if p >= close:
                array.push(idxAbove, i)
                array.push(pxAbove, p)
            else:
                array.push(idxBelow, i)
                array.push(pxBelow, p)

        trans_by_slot: list[float] = array.new_float(16, 100 - pct_far)

        if array.size(idxAbove) > 0:
            ordAbove = array.sort_indices(pxAbove, order.ascending)
            for r in pine_range(0, array.size(ordAbove) - 1):
                li = array.get(idxAbove, array.get(ordAbove, r))
                slot = array.get(lvl_slots, li)
                pct = pct_near if r == 0 else pct_mid if r == 1 else pct_far
                array.set(trans_by_slot, slot, 100 - pct)

        if array.size(idxBelow) > 0:
            ordBelow = array.sort_indices(pxBelow, order.descending)
            for r in pine_range(0, array.size(ordBelow) - 1):
                li = array.get(idxBelow, array.get(ordBelow, r))
                slot = array.get(lvl_slots, li)
                pct = pct_near if r == 0 else pct_mid if r == 1 else pct_far
                array.set(trans_by_slot, slot, 100 - pct)

        trans_25 = array.get(trans_by_slot, 0)
        trans_40 = array.get(trans_by_slot, 1)
        trans_50 = array.get(trans_by_slot, 2)
        trans_60 = array.get(trans_by_slot, 3)
        trans_75 = array.get(trans_by_slot, 4)
        trans_90 = array.get(trans_by_slot, 5)
        trans_m25 = array.get(trans_by_slot, 6)
        trans_m50 = array.get(trans_by_slot, 7)
        trans_m100 = array.get(trans_by_slot, 8)
        trans_m150 = array.get(trans_by_slot, 9)
        trans_m200 = array.get(trans_by_slot, 10)
        trans_125 = array.get(trans_by_slot, 11)
        trans_150 = array.get(trans_by_slot, 12)
        trans_200 = array.get(trans_by_slot, 13)
        trans_m160 = array.get(trans_by_slot, 14)
        trans_160 = array.get(trans_by_slot, 15)

    fb_retracement(fb_show_m200, -2.0, 'auto', trans_m200)
    fb_retracement(fb_show_m160, -1.6, 'auto', trans_m160)
    fb_retracement(fb_show_m150, -1.5, 'auto', trans_m150)
    fb_retracement(fb_show_m100, -1.0, 'auto', trans_m100)
    fb_retracement(fb_show_m50, -0.5, 'auto', trans_m50)
    fb_retracement(fb_show_m25, -0.25, 'auto', trans_m25)
    fb_retracement(True, 0.0, '', trans_0)
    fb_retracement(fb250, 0.25, '', trans_25)
    fb_retracement(fb400, 0.4, '', trans_40)
    fb_retracement(fb500, 0.5, '', trans_50)
    fb_retracement(fb600, 0.6, '', trans_60)
    fb_retracement(fb750, 0.75, '', trans_75)
    fb_retracement(fb900, 0.9, '', trans_90)
    fb_retracement(True, 1.0, '', trans_100)
    fb_retracement(fb_show_125, 1.25, 'auto', trans_125)
    fb_retracement(fb_show_150, 1.5, 'auto', trans_150)
    fb_retracement(fb_show_160, 1.6, 'auto', trans_160)
    fb_retracement(fb_show_200, 2.0, 'auto', trans_200)

    tp_pivotHigh: float = na(float)
    tp_pivotLow: float = na(float)
    tp_pivotHigh = ta.pivothigh(tp_Period, tp_Period)
    tp_pivotLow = ta.pivotlow(tp_Period, tp_Period)

    tp_valuewhen_1 = ta.valuewhen(cast_bool(tp_pivotHigh), high[tp_Period], 1)
    tp_valuewhen_2 = ta.valuewhen(cast_bool(tp_pivotHigh), high[tp_Period], 0)
    tp_higherhigh = na if na(tp_pivotHigh) else tp_pivotHigh if tp_valuewhen_1 < tp_valuewhen_2 else na
    tp_lowerhigh = na if na(tp_pivotHigh) else tp_pivotHigh if tp_valuewhen_1 > tp_valuewhen_2 else na
    tp_valuewhen_5 = ta.valuewhen(cast_bool(tp_pivotLow), low[tp_Period], 1)
    tp_valuewhen_6 = ta.valuewhen(cast_bool(tp_pivotLow), low[tp_Period], 0)
    tp_higherlow = na if na(tp_pivotLow) else tp_pivotLow if tp_valuewhen_5 < tp_valuewhen_6 else na
    tp_lowerlow = na if na(tp_pivotLow) else tp_pivotLow if tp_valuewhen_5 > tp_valuewhen_6 else na

    plotshape(tp_higherhigh if show_trendpivots and tp_showPPA else na, title='TP ʜʜ', style=shape.triangledown, location=location.abovebar, size=size.tiny, color=color.rgb(255, 0, 0), text='ʜʜ', textcolor=color.rgb(255, 0, 0, 100), offset=-tp_Period)
    plotshape(tp_higherlow if show_trendpivots and tp_showPPA else na, title='TP ʜʟ', style=shape.triangleup, location=location.belowbar, size=size.tiny, color=color.rgb(0, 255, 8), text='ʜʟ', textcolor=color.rgb(0, 255, 8, 100), offset=-tp_Period)
    plotshape(tp_lowerhigh if show_trendpivots and tp_showPPA else na, title='TP ʟʜ', style=shape.triangledown, location=location.abovebar, size=size.tiny, color=color.rgb(255, 0, 0), text='ʟʜ', textcolor=color.rgb(255, 0, 0, 100), offset=-tp_Period)
    plotshape(tp_lowerlow if show_trendpivots and tp_showPPA else na, title='TP ʟʟ', style=shape.triangleup, location=location.belowbar, size=size.tiny, color=color.rgb(0, 255, 8), text='ʟʟ', textcolor=color.rgb(0, 255, 8, 100), offset=-tp_Period)

    __block_result_8__ = na
    __switch__ = tp_ppl_sizeStr
    if __switch__ == 'Auto':
        __block_result_8__ = size.auto
    elif __switch__ == 'Tiny':
        __block_result_8__ = size.tiny
    elif __switch__ == 'Small':
        __block_result_8__ = size.small
    elif __switch__ == 'Normal':
        __block_result_8__ = size.normal
    elif __switch__ == 'Large':
        __block_result_8__ = size.large
    elif __switch__ == 'Huge':
        __block_result_8__ = size.huge
    else:
        __block_result_8__ = size.tiny
    tp_ppl_size = __block_result_8__

    tp_txt_HH = '↗' if tp_useArrows else 'ʜʜ'
    tp_txt_LH = '↘' if tp_useArrows else 'ʟʜ'
    tp_txt_LL = '↘' if tp_useArrows else 'ʟʟ'
    tp_txt_HL = '↗' if tp_useArrows else 'ʜʟ'

    if show_trendpivots and tp_showPPL and (not na(tp_higherhigh)):
        label.new(x=bar_index - tp_Period, y=tp_higherhigh, text=tp_txt_HH, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_none, textcolor=tp_col_HH, size=tp_ppl_size, textalign=text.align_center)

    if show_trendpivots and tp_showPPL and (not na(tp_higherlow)):
        label.new(x=bar_index - tp_Period, y=tp_higherlow, text=tp_txt_HL, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_none, textcolor=tp_col_HL, size=tp_ppl_size, textalign=text.align_center)

    if show_trendpivots and tp_showPPL and (not na(tp_lowerhigh)):
        label.new(x=bar_index - tp_Period, y=tp_lowerhigh, text=tp_txt_LH, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_none, textcolor=tp_col_LH, size=tp_ppl_size, textalign=text.align_center)

    if show_trendpivots and tp_showPPL and (not na(tp_lowerlow)):
        label.new(x=bar_index - tp_Period, y=tp_lowerlow, text=tp_txt_LL, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_none, textcolor=tp_col_LL, size=tp_ppl_size, textalign=text.align_center)

    tp_center: Series[float] = na(float)
    tp_center = tp_center[1]
    tp_lastpp: float = tp_pivotHigh if cast_bool(tp_pivotHigh) else tp_pivotLow if cast_bool(tp_pivotLow) else na
    if cast_bool(tp_lastpp):
        if na(tp_center):
            tp_center = tp_lastpp
        else:
            tp_center = (tp_center + tp_center + tp_lastpp) / 3

    plot(tp_center if show_trendpivots and tp_showCL else na, color=(color.new(color.teal, 25) if tp_center < hl2 else color.new(color.red, 25)) if show_trendpivots and tp_showCL else na, title='TP Center Line', style=plot.style_stepline, linewidth=2)

    tp_resistance: Series[float] = na(float)
    tp_support: Series[float] = na(float)
    tp_support = tp_pivotLow if cast_bool(tp_pivotLow) else tp_support[1]
    tp_resistance = tp_pivotHigh if cast_bool(tp_pivotHigh) else tp_resistance[1]

    plot(tp_support if show_trendpivots and tp_showSR and cast_bool(tp_support) else na, title='TP Support', color=color.new(color.teal, 50) if show_trendpivots and tp_showSR and cast_bool(tp_support) else na, style=plot.style_circles, offset=-tp_Period)
    plot(tp_resistance if show_trendpivots and tp_showSR and cast_bool(tp_resistance) else na, title='TP Resistance', color=color.new(color.orange, 50) if show_trendpivots and tp_showSR and cast_bool(tp_resistance) else na, style=plot.style_circles, offset=-tp_Period)

    tp_bsignal = close > tp_center[1] and close[1] < tp_center[2]
    tp_ssignal = close < tp_center[1] and close[1] > tp_center[2]
    plotshape(tp_center[1] if show_trendpivots and tp_bsignal and tp_showLabels else na, title='TP Bull', text='Bull', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 50), textcolor=color.new(color.white, 50))
    plotshape(tp_center[1] if show_trendpivots and tp_ssignal and tp_showLabels else na, title='TP Bear', text='Bear', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.orange, 50), textcolor=color.new(color.white, 50))

    tp_pvthis: Series[float] = 0.0
    tp_pvtlos: Series[float] = 0.0
    tp_pvthis = tp_pvthis[1] if na(tp_pivotHigh) else high[tp_Period]
    tp_pvtlos = tp_pvtlos[1] if na(tp_pivotLow) else low[tp_Period]

    tp_bull: bool = False
    tp_bear: bool = False
    tp_bull = close > tp_pvthis and open <= tp_pvthis
    tp_bear = close < tp_pvtlos and open >= tp_pvtlos

    plotshape(1 if show_trendpivots and tp_showFB and tp_bull else na, title='TP BUY Arrow', color=color.new(color.green, 0), style=shape.triangleup, location=location.belowbar)
    plotshape(-1 if show_trendpivots and tp_showFB and tp_bear else na, title='TP SELL Arrow', color=color.new(color.red, 0), style=shape.triangledown, location=location.abovebar)

    alertcondition(tp_bull or tp_bear, title='TP Fractal Break Arrow', message='Alert')
    alertcondition(tp_bull, title='TP Fractal Break BULL', message='BULL')
    alertcondition(tp_bear, title='TP Fractal Break BEAR', message='BEAR')

    tp_ch_hx: Persistent[list[int]] = array.new_int()
    tp_ch_hy: Persistent[list[float]] = array.new_float()
    tp_ch_lx: Persistent[list[int]] = array.new_int()
    tp_ch_ly: Persistent[list[float]] = array.new_float()

    if not na(tp_pivotHigh):
        array.push(tp_ch_hx, time[tp_Period])
        array.push(tp_ch_hy, tp_pivotHigh)
        while array.size(tp_ch_hx) > tp_ch_count:
            array.shift(tp_ch_hx)
            array.shift(tp_ch_hy)
    if not na(tp_pivotLow):
        array.push(tp_ch_lx, time[tp_Period])
        array.push(tp_ch_ly, tp_pivotLow)
        while array.size(tp_ch_lx) > tp_ch_count:
            array.shift(tp_ch_lx)
            array.shift(tp_ch_ly)

    def tp_f_interp(_xs, _ys, _x):
        _y: float = na(float)
        _n = array.size(_xs)
        if _n > 0:
            if _x <= array.get(_xs, 0):
                _y = array.get(_ys, 0)
            elif _x >= array.get(_xs, _n - 1):
                _y = array.get(_ys, _n - 1)
            else:
                for i in pine_range(1, _n - 1):
                    _xb = array.get(_xs, i)
                    if _x <= _xb:
                        _xa = array.get(_xs, i - 1)
                        _ya = array.get(_ys, i - 1)
                        _yb = array.get(_ys, i)
                        _y = _yb if _xb == _xa else _ya + (_yb - _ya) * (_x - _xa) / (_xb - _xa)
                        break
        return _y

    tp_ch_polys: Persistent[list[Polyline]] = array.new(0, NA(Polyline))
    if barstate.islast:
        while array.size(tp_ch_polys) > 0:
            polyline.delete(array.pop(tp_ch_polys))

        if show_trendpivots and tp_ch_show and (array.size(tp_ch_hx) >= 2) and (array.size(tp_ch_lx) >= 2):
            _sty = line.style_solid if tp_ch_style == 'Solid' else line.style_dashed if tp_ch_style == 'Dashed' else line.style_dotted
            _nh = array.size(tp_ch_hx)
            _nl = array.size(tp_ch_lx)

            if tp_ch_fill and tp_ch_opacity > 0:
                _x0 = math.max(array.get(tp_ch_hx, 0), array.get(tp_ch_lx, 0))
                _x1 = math.min(array.get(tp_ch_hx, _nh - 1), array.get(tp_ch_lx, _nl - 1))
                if _x1 > _x0:
                    _xs: list[int] = array.new_int()
                    array.push(_xs, _x0)
                    for _x in tp_ch_hx:
                        if _x > _x0 and _x < _x1:
                            array.push(_xs, _x)
                    for _x in tp_ch_lx:
                        if _x > _x0 and _x < _x1:
                            array.push(_xs, _x)
                    array.push(_xs, _x1)
                    array.sort(_xs, order.ascending)
                    _n = array.size(_xs)
                    for k in pine_range(0, tp_ch_steps - 1):
                        _t0 = k / cast_float(tp_ch_steps)
                        _t1 = (k + 1) / cast_float(tp_ch_steps)
                        _pts: list[ChartPoint] = array.new(0, NA(ChartPoint))
                        for j in pine_range(0, _n - 1):
                            _x = array.get(_xs, j)
                            _u = tp_f_interp(tp_ch_hx, tp_ch_hy, _x)
                            _l = tp_f_interp(tp_ch_lx, tp_ch_ly, _x)
                            array.push(_pts, chart.point.from_time(_x, _u - (_u - _l) * _t0))
                        for j in pine_range(_n - 1, 0):
                            _x = array.get(_xs, j)
                            _u = tp_f_interp(tp_ch_hx, tp_ch_hy, _x)
                            _l = tp_f_interp(tp_ch_lx, tp_ch_ly, _x)
                            array.push(_pts, chart.point.from_time(_x, _u - (_u - _l) * _t1))
                        _c = color.from_gradient((_t0 + _t1) / 2, 0, 1, tp_ch_up_col, tp_ch_dn_col)
                        array.push(tp_ch_polys, polyline.new(_pts, closed=True, xloc=xloc.bar_time, line_color=color.new(_c, 100), fill_color=color.new(_c, 100 - tp_ch_opacity)))

            _hp: list[ChartPoint] = array.new(0, NA(ChartPoint))
            for i in pine_range(0, _nh - 1):
                array.push(_hp, chart.point.from_time(array.get(tp_ch_hx, i), array.get(tp_ch_hy, i)))
            _lp: list[ChartPoint] = array.new(0, NA(ChartPoint))
            for i in pine_range(0, _nl - 1):
                array.push(_lp, chart.point.from_time(array.get(tp_ch_lx, i), array.get(tp_ch_ly, i)))
            _curved = tp_ch_shape == 'Curved'
            array.push(tp_ch_polys, polyline.new(_hp, curved=_curved, xloc=xloc.bar_time, line_color=tp_ch_up_col, line_width=tp_ch_width, line_style=_sty))
            array.push(tp_ch_polys, polyline.new(_lp, curved=_curved, xloc=xloc.bar_time, line_color=tp_ch_dn_col, line_width=tp_ch_width, line_style=_sty))

    def pc_f_drawLeg(arr, x1, y1, x2, y2, col, pw, sty):
        pc_line_style = line.style_solid if sty == 'Solid' else line.style_dashed if sty == 'Dashed' else line.style_dotted
        pc_ml = line.new(x1=x1, y1=y1, x2=x2, y2=y2, xloc=xloc.bar_time, color=col, width=pw, style=pc_line_style)
        return array.push(arr, pc_ml)

    def pc_f_labelSize(sel):
        return size.tiny if sel == 'Tiny' else size.small if sel == 'Small' else size.normal if sel == 'Normal' else size.large if sel == 'Large' else size.huge

    pc_ph: float = high if ta.highestbars(high, pc_period) == 0 else na
    pc_pl: float = low if ta.lowestbars(low, pc_period) == 0 else na

    pc_isPh = not na(pc_ph)
    pc_isPl = not na(pc_pl)

    pc_dir: Persistent[int] = 0
    pc_prev_dir = pc_dir
    pc_dir = 1 if pc_isPh and (not pc_isPl) else -1 if pc_isPl and (not pc_isPh) else pc_dir
    pc_dc = 1 if pc_dir != pc_prev_dir else 0

    pc_z: Persistent[list[float]] = array.new_float(0)

    def pc_add_to_zigzag(p, v, b):
        array.unshift(p, b)
        return array.unshift(p, v)

    def pc_update_zigzag(p, v, b, d):
        if array.size(p) == 0:
            pc_add_to_zigzag(p, v, b)
        elif d == 1 and v > array.get(p, 0) or (d == -1 and v < array.get(p, 0)):
            array.set(p, 0, v)
            array.set(p, 1, b)
        return 0.0

    if pc_isPh or pc_isPl:
        if pc_dc != 0:
            pc_add_to_zigzag(pc_z, pc_ph if pc_dir == 1 else pc_pl, time)
        elif not (pc_isPh and pc_isPl):
            pc_update_zigzag(pc_z, pc_ph if pc_dir == 1 else pc_pl, time, pc_dir)

    pc_last_pivot_bi: Persistent[int] = na(int)
    if array.size(pc_z) >= 2 and cast_int(array.get(pc_z, 1)) == time:
        pc_last_pivot_bi = bar_index
    pc_trg_lo = inline_series(ta.lowest(low, pc_period - 1), 1)
    pc_trg_hi = inline_series(ta.highest(high, pc_period - 1), 1)
    pc_trg_lo_age = 1 - inline_series(ta.lowestbars(low, pc_period - 1), 1)
    pc_trg_hi_age = 1 - inline_series(ta.highestbars(high, pc_period - 1), 1)

    pc_zigzag_lines: Persistent[list[Line]] = array.new_line()
    pc_prev_leg_markers: Persistent[list[Label]] = array.new_label()
    if array.size(pc_z) >= 4:
        while array.size(pc_zigzag_lines) > 0:
            line.delete(array.pop(pc_zigzag_lines))
        while array.size(pc_prev_leg_markers) > 0:
            label.delete(array.pop(pc_prev_leg_markers))

        pc_last_valid = array.size(pc_z) - 4
        if pc_last_valid >= 0:
            for i in pine_range(0, pc_last_valid, 2):
                pc_x1 = cast_int(array.get(pc_z, i + 1))
                pc_y1 = array.get(pc_z, i)
                pc_x2 = cast_int(array.get(pc_z, i + 3))
                pc_y2 = array.get(pc_z, i + 2)
                pc_leg_color = pc_bull_color if pc_y1 > pc_y2 else pc_bear_color
                pc_leg_style = pc_unconfirmed_leg_style if i == 0 else pc_confirmed_style
                pc_f_drawLeg(pc_zigzag_lines, pc_x1, pc_y1, pc_x2, pc_y2, pc_leg_color, pc_width, pc_leg_style)

                if i == 0 and pc_show_prev_leg_markers:
                    pc_prev_marker_size = pc_f_labelSize(pc_prev_marker_size_choice)
                    pc_prev_start_marker = label.new(pc_x1, pc_y1, '◯', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=pc_leg_color, size=pc_prev_marker_size)
                    pc_prev_end_marker = label.new(pc_x2, pc_y2, '◯', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=pc_leg_color, size=pc_prev_marker_size)
                    array.push(pc_prev_leg_markers, pc_prev_start_marker)
                    array.push(pc_prev_leg_markers, pc_prev_end_marker)

    pc_avg_bearish_length: Persistent[float] = 0.0
    pc_avg_bullish_length: Persistent[float] = 0.0
    pc_avg_bearish_slope: Persistent[float] = 0.0
    pc_avg_bullish_slope: Persistent[float] = 0.0

    if array.size(pc_z) >= 4:
        pc_bearish_lengths: list[float] = array.new_float(0)
        pc_bullish_lengths: list[float] = array.new_float(0)
        pc_bearish_slopes: list[float] = array.new_float(0)
        pc_bullish_slopes: list[float] = array.new_float(0)
        i: int = 0
        while i < array.size(pc_z) - 2:
            pc_yA = array.get(pc_z, i)
            pc_xA = array.get(pc_z, i + 1)
            pc_yB = array.get(pc_z, i + 2)
            pc_xB = array.get(pc_z, i + 3)
            if pc_xA != pc_xB:
                pc_segment_direction = 1 if pc_yA > pc_yB else -1
                pc_segment_length = math.abs(pc_yA - pc_yB)
                pc_segment_slope = (pc_yA - pc_yB) / (pc_xA - pc_xB)
                if pc_segment_direction == -1:
                    array.push(pc_bearish_lengths, pc_segment_length)
                    array.push(pc_bearish_slopes, pc_segment_slope)
                else:
                    array.push(pc_bullish_lengths, pc_segment_length)
                    array.push(pc_bullish_slopes, pc_segment_slope)
            i += 2
        pc_avg_bearish_length = array.avg(pc_bearish_lengths) if array.size(pc_bearish_lengths) > 0 else 0
        pc_avg_bullish_length = array.avg(pc_bullish_lengths) if array.size(pc_bullish_lengths) > 0 else 0
        pc_avg_bearish_slope = array.avg(pc_bearish_slopes) if array.size(pc_bearish_slopes) > 0 else 0
        pc_avg_bullish_slope = array.avg(pc_bullish_slopes) if array.size(pc_bullish_slopes) > 0 else 0

    def pc_f_tfMatches(sel):
        __block_result_9__ = na
        __switch__ = sel
        if __switch__ == "1h":
            __block_result_9__ = timeframe.isintraday and timeframe.multiplier == 60
        elif __switch__ == "4h":
            __block_result_9__ = timeframe.isintraday and timeframe.multiplier == 240
        elif __switch__ == "1d":
            __block_result_9__ = timeframe.isdaily and timeframe.multiplier == 1
        elif __switch__ == "1w":
            __block_result_9__ = timeframe.isweekly and timeframe.multiplier == 1
        elif __switch__ == "1m":
            __block_result_9__ = timeframe.ismonthly and timeframe.multiplier == 1
        else:
            __block_result_9__ = False
        return __block_result_9__

    def pc_f_detectTf():
        return '1h' if timeframe.isintraday and timeframe.multiplier == 60 else '4h' if timeframe.isintraday and timeframe.multiplier == 240 else '1d' if timeframe.isdaily and timeframe.multiplier == 1 else '1w' if timeframe.isweekly and timeframe.multiplier == 1 else '1m' if timeframe.ismonthly and timeframe.multiplier == 1 else 'none'

    pc_detected_tf = pc_f_detectTf()
    pc_anchor_tf = pc_detected_tf if pc_anchor_tf_mode == 'Automatic' else pc_anchor_tf_manual

    __block_result_10__ = na
    __switch__ = pc_anchor_tf
    if __switch__ == "1h":
        __block_result_10__ = pc_anchor_time_1h
    elif __switch__ == "4h":
        __block_result_10__ = pc_anchor_time_4h
    elif __switch__ == "1d":
        __block_result_10__ = pc_anchor_time_1d
    elif __switch__ == "1w":
        __block_result_10__ = pc_anchor_time_1w
    elif __switch__ == "1m":
        __block_result_10__ = pc_anchor_time_1m
    else:
        __block_result_10__ = pc_anchor_time_1h
    pc_anchor_time = __block_result_10__

    pc_tf_matches = pc_f_tfMatches(pc_anchor_tf)

    __block_result_11__ = na
    __switch__ = pc_anchor_tf
    if __switch__ == "1h":
        __block_result_11__ = pc_last_verified_leg_1h
    elif __switch__ == "4h":
        __block_result_11__ = pc_last_verified_leg_4h
    elif __switch__ == "1d":
        __block_result_11__ = pc_last_verified_leg_1d
    elif __switch__ == "1w":
        __block_result_11__ = pc_last_verified_leg_1w
    elif __switch__ == "1m":
        __block_result_11__ = pc_last_verified_leg_1m
    else:
        __block_result_11__ = pc_last_verified_leg_1h
    pc_last_verified_leg = __block_result_11__

    pc_lbl_size = pc_f_labelSize(pc_size_choice)

    def pc_f_legChar(num, style):
        style1: list[str] = array.from_items('①', '②', '③', '④', '⑤')
        style2: list[str] = array.from_items('❶', '❷', '❸', '❹', '❺')
        style3: list[str] = array.from_items('Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ')
        style4: list[str] = array.from_items('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣')
        style5: list[str] = array.from_items('₍₁₎', '₍₂₎', '₍₃₎', '₍₄₎', '₍₅₎')
        style6: list[str] = array.from_items('⑴', '⑵', '⑶', '⑷', '⑸')
        chosen = style1 if style == '①②③④⑤' else style2 if style == '❶❷❸❹❺' else style3 if style == 'Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ' else style4 if style == '1️⃣2️⃣3️⃣4️⃣5️⃣' else style5 if style == '₍₁₎ ₍₂₎ ₍₃₎ ₍₄₎ ₍₅₎' else style6
        return array.get(chosen, num - 1)

    pc_leg_bar_arr: Persistent[list[int]] = array.new_int(0)
    pc_leg_price_arr: Persistent[list[float]] = array.new_float(0)
    pc_leg_num_arr: Persistent[list[int]] = array.new_int(0)

    pc_seeded: Persistent[bool] = False
    pc_last_recorded_bar: Persistent[int] = na(int)
    pc_last_assigned_num: Persistent[int] = na(int)
    pc_anchor_label: Persistent[Label] = na(Label)
    pc_anchor_bar_saved: Persistent[int] = na(int)
    pc_anchor_price_saved: Persistent[float] = na(float)
    pc_anchor_is_high: Persistent[bool] = False

    if barstate.islast and (not pc_seeded) and (array.size(pc_z) >= 4):
        pc_num_pairs = cast_int(array.size(pc_z) / 2)

        pc_anchor_idx: int = 2
        pc_best_diff = NA(float)
        for i in pine_range(1, pc_num_pairs - 1):
            pc_t = array.get(pc_z, i * 2 + 1)
            pc_diff = math.abs(pc_t - pc_anchor_time)
            if na(pc_best_diff) or pc_diff < pc_best_diff:
                pc_best_diff = pc_diff
                pc_anchor_idx = i * 2

        pc_neighbor_idx = pc_anchor_idx + 2 if pc_anchor_idx + 2 <= array.size(pc_z) - 2 else pc_anchor_idx - 2 if pc_anchor_idx - 2 >= 0 else pc_anchor_idx
        pc_anchor_is_high = array.get(pc_z, pc_anchor_idx) > array.get(pc_z, pc_neighbor_idx)

        for idx in pine_range((pc_num_pairs - 1) * 2, 2, 2):
            pc_num: int = 0
            if idx > pc_anchor_idx:
                pc_step_back = cast_int((idx - pc_anchor_idx) / 2)
                pc_num = ((pc_last_verified_leg - 1 - pc_step_back) % 5 + 5) % 5 + 1
            else:
                pc_step_fwd = cast_int((pc_anchor_idx - idx) / 2)
                pc_num = (pc_last_verified_leg - 1 + pc_step_fwd) % 5 + 1
            array.push(pc_leg_bar_arr, cast_int(array.get(pc_z, idx + 1)))
            array.push(pc_leg_price_arr, array.get(pc_z, idx))
            array.push(pc_leg_num_arr, pc_num)

        pc_anchor_bar_saved = cast_int(array.get(pc_z, pc_anchor_idx + 1))
        pc_anchor_price_saved = array.get(pc_z, pc_anchor_idx)

        pc_last_recorded_bar = cast_int(array.get(pc_z, 3))
        pc_last_assigned_num = array.get(pc_leg_num_arr, array.size(pc_leg_num_arr) - 1)
        pc_seeded = True

    if pc_seeded and array.size(pc_z) >= 4:
        pc_frozen_bar = cast_int(array.get(pc_z, 3))
        if pc_frozen_bar != pc_last_recorded_bar:
            pc_frozen_px = array.get(pc_z, 2)
            pc_next_num = pc_last_assigned_num % 5 + 1
            array.push(pc_leg_bar_arr, pc_frozen_bar)
            array.push(pc_leg_price_arr, pc_frozen_px)
            array.push(pc_leg_num_arr, pc_next_num)
            pc_last_assigned_num = pc_next_num
            pc_last_recorded_bar = pc_frozen_bar

    pc_leg_labels: Persistent[list[Label]] = array.new_label()
    if barstate.islast:
        while array.size(pc_leg_labels) > 0:
            label.delete(array.pop(pc_leg_labels))
        label.delete(pc_anchor_label)
        pc_anchor_label = na

        if pc_tf_matches:
            if array.size(pc_leg_num_arr) > 0:
                pc_last_leg_i = array.size(pc_leg_num_arr) - 1
                for i in pine_range(0, pc_last_leg_i):
                    pc_bx = array.get(pc_leg_bar_arr, i)
                    pc_px = array.get(pc_leg_price_arr, i)
                    pc_num2 = array.get(pc_leg_num_arr, i)

                    pc_dir_color = pc_label_bull_color if i == pc_last_leg_i else pc_label_bull_color if array.get(pc_leg_price_arr, i + 1) > pc_px else pc_label_bear_color
                    pc_bg_col = color.new(pc_dir_color, pc_bg_fade_pct) if pc_auto_dir_color else color.new(pc_manual_bg_color, pc_bg_fade_pct)
                    pc_txt_col = pc_dir_color if pc_auto_dir_color else pc_manual_txt_color

                    pc_next_x = array.get(pc_leg_bar_arr, i + 1) if i < pc_last_leg_i else time
                    pc_next_y = array.get(pc_leg_price_arr, i + 1) if i < pc_last_leg_i else close
                    pc_lbl_x = cast_int(math.round((pc_bx + pc_next_x) / 2.0)) if pc_label_pos == 'Leg Midpoint' else pc_bx
                    pc_lbl_y = (pc_px + pc_next_y) / 2.0 if pc_label_pos == 'Leg Midpoint' else pc_px

                    pc_lbl = label.new(pc_lbl_x, pc_lbl_y, pc_f_legChar(pc_num2, pc_char_style), xloc=xloc.bar_time, style=label.style_label_center, color=pc_bg_col, textcolor=pc_txt_col, size=pc_lbl_size)
                    array.push(pc_leg_labels, pc_lbl)

            if pc_show_anchor_marker and (not na(pc_anchor_bar_saved)):
                pc_anchor_buf = ta.atr(20) * 2
                pc_anchor_y = pc_anchor_price_saved + pc_anchor_buf if pc_anchor_is_high else pc_anchor_price_saved - pc_anchor_buf
                pc_anchor_style = label.style_label_down if pc_anchor_is_high else label.style_label_up
                pc_anchor_label = label.new(pc_anchor_bar_saved, pc_anchor_y, '⚓' + string.tostring(pc_last_verified_leg) + ' ' + pc_anchor_tf, xloc=xloc.bar_time, style=pc_anchor_style, color=color.new(color.blue, 0), textcolor=color.white, size=size.small)

    def pc_f_px(_v):
        return string.tostring(_v, format.mintick)

    def pc_f_sgn(_v):
        return ('+' if _v >= 0 else '') + string.tostring(_v, format.mintick)

    def pc_f_pct(_v):
        return ('+' if _v >= 0 else '') + string.tostring(_v, '0.00') + '%'

    def pc_f_num(_v):
        return '–' if na(_v) else string.tostring(_v, '0')

    def pc_f_liveTip():
        _t: str = ''
        if array.size(pc_z) >= 4 and (not na(pc_last_pivot_bi)):
            _pvt = array.get(pc_z, 0)
            _isHigh = pc_dir == 1
            _pvtType = 'HIGH' if _isHigh else 'LOW'
            _newType = 'LOW' if _isHigh else 'HIGH'
            _barsPvt = bar_index - pc_last_pivot_bi
            _legDir = 1 if close > _pvt else -1
            _curLen = math.abs(close - _pvt)

            _trg = pc_trg_lo if _isHigh else pc_trg_hi
            _trgAge = pc_trg_lo_age if _isHigh else pc_trg_hi_age
            _hold = math.max(pc_period - 1 - _trgAge, 0)
            _ext = math.max(pc_trg_hi, _pvt) if _isHigh else math.min(pc_trg_lo, _pvt)
            _miss = _trg - close
            _barExt = low if _isHigh else high
            _nextNum = pc_last_assigned_num % 5 + 1 if pc_seeded and (not na(pc_last_assigned_num)) else NA(int)
            _phase = 'n/a (counter not seeded)' if na(_nextNum) else pc_f_legChar(_nextNum, pc_char_style) + ('' if pc_tf_matches else ' (labels hidden on this TF)')

            _msBar = timeframe.in_seconds() * 1000.0
            _nBu: int = 0
            _nBe: int = 0
            _bBu: float = 0.0
            _bBe: float = 0.0
            _bigger: int = 0
            for i in pine_range(0, array.size(pc_z) - 4, 2):
                _yA = array.get(pc_z, i)
                _yB = array.get(pc_z, i + 2)
                _bars = (array.get(pc_z, i + 1) - array.get(pc_z, i + 3)) / _msBar
                _len = math.abs(_yA - _yB)
                if _yA > _yB:
                    _nBu += 1
                    _bBu += _bars
                    if _legDir == 1 and _len > _curLen:
                        _bigger += 1
                elif _yA < _yB:
                    _nBe += 1
                    _bBe += _bars
                    if _legDir == -1 and _len > _curLen:
                        _bigger += 1
            _avgBarsBu = _bBu / _nBu if _nBu > 0 else na
            _avgBarsBe = _bBe / _nBe if _nBe > 0 else na
            _avgLenSame = pc_avg_bullish_length if _legDir == 1 else pc_avg_bearish_length
            _avgBarSame = _avgBarsBu if _legDir == 1 else _avgBarsBe
            _nSame = _nBu if _legDir == 1 else _nBe
            _pctSize = _curLen / _avgLenSame * 100 if _avgLenSame > 0 else na
            _pctTime = _barsPvt / _avgBarSame * 100 if _avgBarSame > 0 else na
            _target = _pvt + _legDir * _avgLenSame
            _dirTxt = '▲ bullish' if _legDir == 1 else '▼ bearish'

            _t = '⏳ NEW LEG / PHASE — WHAT IS MISSING' + '\nLast pivot: ' + _pvtType + ' ' + pc_f_px(_pvt) + ' · ' + string.tostring(_barsPvt) + ' bars ago (≈' + f_dur(_barsPvt) + ')' + ('\n⚠ Pivot set on this bar — can still change until the bar closes' if _barsPvt == 0 else '') + '\nActive leg: ' + _dirTxt + ' ' + pc_f_sgn(close - _pvt) + ' (' + pc_f_pct((close - _pvt) / _pvt * 100) + ')' + '\n' + '\n▶ NEW LEG needs a bar ' + ('LOW below ' if _isHigh else 'HIGH above ') + pc_f_px(_trg) + '\n   = ' + ('lowest low' if _isHigh else 'highest high') + ' of the prior ' + string.tostring(pc_period - 1) + ' bars (Period ' + string.tostring(pc_period) + ')' + '\n   Missing from close: ' + pc_f_sgn(_miss) + ' (' + pc_f_pct(_miss / close * 100) + ')' + '\n   This bar ' + ('low ' if _isHigh else 'high ') + pc_f_px(_barExt) + ' → ' + pc_f_sgn(_trg - _barExt) + ' short' + '\n   Level holds this bar + ' + string.tostring(_hold) + ' more, then eases toward price as older bars leave the window' + '\n   On trigger: ' + _pvtType + ' ' + pc_f_px(_pvt) + ' locks in as phase ' + _phase + ', the ' + _pvtType + '→' + _newType + ' leg becomes the unconfirmed leg and a new active leg starts from the new ' + _newType + '\n✕ A ' + ('HIGH above ' if _isHigh else 'LOW below ') + pc_f_px(_ext) + ' only stretches the current ' + _pvtType + ' pivot (no new phase)' + '\n✕ An outside bar doing both at once creates nothing' + '\n' + '\n📊 STATISTICS (' + string.tostring(_nBu + _nBe) + ' legs)' + '\nAvg ▲ leg: ' + pc_f_px(pc_avg_bullish_length) + ' · ≈' + pc_f_num(_avgBarsBu) + ' bars (' + string.tostring(_nBu) + ' legs)' + '\nAvg ▼ leg: ' + pc_f_px(pc_avg_bearish_length) + ' · ≈' + pc_f_num(_avgBarsBe) + ' bars (' + string.tostring(_nBe) + ' legs)' + '\nActive vs avg ' + _dirTxt + ': ' + pc_f_num(_pctSize) + '% of size · ' + pc_f_num(_pctTime) + '% of time' + '\nPast ' + _dirTxt + ' legs bigger than this one: ' + string.tostring(_bigger) + '/' + string.tostring(_nSame) + (' (' + string.tostring(cast_float(_bigger) / _nSame * 100, '0') + '%)' if _nSame > 0 else '') + '\nAvg-size target: ' + pc_f_px(_target) + ' (' + pc_f_sgn(_target - close) + ')' + (' · already exceeded' if not na(_pctSize) and _pctSize >= 100 else '')
        return _t

    pc_current_leg_lines: Persistent[list[Line]] = array.new_line()
    pc_current_leg_markers: Persistent[list[Label]] = array.new_label()
    pc_last_pivot_y: Persistent[float] = na(float)
    pc_last_pivot_x: Persistent[int] = na(int)
    if array.size(pc_z) >= 2:
        while array.size(pc_current_leg_lines) > 0:
            line.delete(array.pop(pc_current_leg_lines))
        while array.size(pc_current_leg_markers) > 0:
            label.delete(array.pop(pc_current_leg_markers))
        pc_last_pivot_y = array.get(pc_z, 0)
        pc_last_pivot_x = cast_int(array.get(pc_z, 1))
        pc_live_leg_color = pc_bull_color if close > pc_last_pivot_y else pc_bear_color
        pc_f_drawLeg(pc_current_leg_lines, pc_last_pivot_x, pc_last_pivot_y, time, close, pc_live_leg_color, pc_width, pc_active_leg_style)

        if pc_show_leg_markers:
            pc_marker_size = pc_f_labelSize(pc_marker_size_choice)
            pc_start_marker = label.new(pc_last_pivot_x, pc_last_pivot_y, '◯', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=pc_live_leg_color, size=pc_marker_size)
            pc_end_marker = label.new(time, close, '◯', xloc=xloc.bar_time, style=label.style_label_center, color=color.new(color.white, 100), textcolor=pc_live_leg_color, size=pc_f_labelSize(pc_live_marker_size_choice))
            if barstate.islast:
                label.set_tooltip(pc_end_marker, pc_f_liveTip())
            array.push(pc_current_leg_markers, pc_start_marker)
            array.push(pc_current_leg_markers, pc_end_marker)

    pc_current_direction: Persistent[int] = 0
    pc_current_length: Persistent[float] = 0.0
    pc_current_slope: Persistent[float] = 0.0
    if not na(pc_last_pivot_x):
        pc_current_direction = 1 if close > pc_last_pivot_y else -1
        pc_current_length = math.abs(close - pc_last_pivot_y)
        pc_dx = math.max(1.0, cast_float(time - pc_last_pivot_x))
        pc_current_slope = (close - pc_last_pivot_y) / pc_dx

    pc_extension_line1: Persistent[Line] = na(Line)
    pc_extension_line2: Persistent[Line] = na(Line)
    if array.size(pc_z) >= 2 and pc_show_projection and (not na(pc_current_slope)):
        line.delete(pc_extension_line1)
        line.delete(pc_extension_line2)
        pc_start_x = time
        pc_start_y = close
        pc_ms_per_bar = timeframe.in_seconds() * 1000
        pc_max_future_ms = 500 * pc_ms_per_bar
        pc_max_x = pc_start_x + pc_max_future_ms
        pc_last_zigzag_length = pc_current_length
        pc_projection_length1 = (pc_avg_bullish_length - pc_last_zigzag_length if pc_avg_bullish_length > pc_last_zigzag_length else 0) if pc_current_direction == 1 else pc_avg_bearish_length - pc_last_zigzag_length if pc_avg_bearish_length > pc_last_zigzag_length else 0
        pc_abs_slope_current = math.max(1e-10, math.abs(pc_current_slope))
        pc_proj_line_style = line.style_solid if pc_proj_style == 'Solid' else line.style_dashed if pc_proj_style == 'Dashed' else line.style_dotted
        if pc_projection_length1 > 0:
            pc_raw_dx1 = cast_int(math.round(pc_projection_length1 / pc_abs_slope_current))
            pc_dx1 = math.max(1, math.min(pc_raw_dx1, pc_max_x - pc_start_x))
            pc_end_x1 = pc_start_x + pc_dx1
            pc_end_y1 = pc_start_y + pc_current_slope * pc_dx1
            pc_seg1_color = pc_proj_bull_color if pc_current_direction == 1 else pc_proj_bear_color
            pc_extension_line1 = line.new(x1=pc_start_x, y1=pc_start_y, x2=pc_end_x1, y2=pc_end_y1, xloc=xloc.bar_time, extend=extend.none, color=pc_seg1_color, width=pc_proj_width, style=pc_proj_line_style)
            pc_projection_length2 = pc_avg_bearish_length if pc_current_direction == 1 else pc_avg_bullish_length
            pc_projection_slope2 = pc_avg_bearish_slope if pc_current_direction == 1 else pc_avg_bullish_slope
            pc_abs_slope2 = math.max(1e-10, math.abs(pc_projection_slope2))
            pc_raw_dx2 = cast_int(math.round(pc_projection_length2 / pc_abs_slope2))
            pc_dx2 = math.max(1, math.min(pc_raw_dx2, pc_max_x - pc_end_x1))
            pc_end_x2 = pc_end_x1 + pc_dx2
            pc_end_y2 = pc_end_y1 + pc_projection_slope2 * pc_dx2
            pc_seg2_color = pc_proj_bear_color if pc_current_direction == 1 else pc_proj_bull_color
            pc_extension_line2 = line.new(x1=pc_end_x1, y1=pc_end_y1, x2=pc_end_x2, y2=pc_end_y2, xloc=xloc.bar_time, extend=extend.none, color=pc_seg2_color, width=pc_proj_width, style=pc_proj_line_style)
        else:
            pc_projection_length2 = pc_avg_bearish_length if pc_current_direction == 1 else pc_avg_bullish_length
            pc_projection_slope2 = pc_avg_bearish_slope if pc_current_direction == 1 else pc_avg_bullish_slope
            pc_abs_slope2 = math.max(1e-10, math.abs(pc_projection_slope2))
            pc_raw_dx2 = cast_int(math.round(pc_projection_length2 / pc_abs_slope2))
            pc_dx2 = math.max(1, math.min(pc_raw_dx2, pc_max_x - pc_start_x))
            pc_end_x2 = pc_start_x + pc_dx2
            pc_end_y2 = pc_start_y + pc_projection_slope2 * pc_dx2
            pc_seg2_color = pc_proj_bear_color if pc_current_direction == 1 else pc_proj_bull_color
            pc_extension_line2 = line.new(x1=pc_start_x, y1=pc_start_y, x2=pc_end_x2, y2=pc_end_y2, xloc=xloc.bar_time, extend=extend.none, color=pc_seg2_color, width=pc_proj_width, style=pc_proj_line_style)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)