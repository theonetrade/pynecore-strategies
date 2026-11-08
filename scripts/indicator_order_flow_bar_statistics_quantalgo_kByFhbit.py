"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barmerge, barstate, bgcolor, close,
    color, display, footprint, format, high, input, label, last_bar_index, low, math, na, nz, plot,
    request, script, size, string, syminfo, ta, time, timeframe, volume, xloc
)
from pynecore.types import Color, Footprint, Label, Persistent, Series

volume_settings: str = '════════ Volume & Delta ════════'
liq_settings: str = '════════ Liquidations ════════'
interest_settings: str = '═════ Open Interest & Positioning ═════'
funding_settings: str = '════════ Funding & Price ════════'
source_settings: str = '════════ Data Source ════════'
number_settings: str = '════════ Number Format ════════'
layout_settings: str = '════════ Layout ════════'
visual_settings: str = '════════ Visual Settings ════════'
tooltip_buy_vol: str = 'Aggressive buy volume: the share of the bar that traded into the offer, where the buyer crossed the spread to get filled. This comes from volume footprint data, so it reflects which side initiated each trade rather than being inferred from the bar range. Reading footprint data requires a Premium or Ultimate plan. On charts carrying a lot of history it can also lead to a memory limit error in Bar Replay, since footprint data loads across the full chart and cannot be capped by bar count.\n\nHow to read it: rising buy volume alongside rising price is participation confirming the move. Heavy buy volume against a price that will not advance is absorption, buyers are being met by resting supply, and that often precedes a stall.\n\nIf cells read as unavailable, bid/ask data is not being served for those bars. Delta Engine under Data Source controls what happens in that case.'
tooltip_sell_vol: str = 'Aggressive sell volume: the share of the bar that traded into the bid, where the seller crossed the spread to get filled.\n\nHow to read it: buy and sell volume always sum to total volume, so read them as a pair. A bar split close to evenly is a balanced auction. A lopsided split shows one side doing the work, and the direction of price against that split tells you whether they are being rewarded or absorbed.\n\nIf cells read as unavailable, bid/ask data is not being served for those bars.'
tooltip_total_vol: str = 'Total traded volume for the bar, read directly from the charted contract.\n\nHow to read it: volume is conviction. A breakout on expanding volume carries weight, the same move on thin volume is far easier to reverse. Turn on Tint Total By Delta under Visual Settings and this row is colored by which side dominated, so magnitude and direction read together in one cell.\n\nBlank cells mean the symbol reports no volume at all, which is uncommon outside index and synthetic tickers.'
tooltip_delta_vol: str = 'Net delta: aggressive buy volume minus aggressive sell volume. Positive means buyers lifted more than sellers hit.\n\nHow to read it: divergence between delta and price is the tell worth waiting for. Price making a new high while delta shrinks means the push is being sold into. A large delta that fails to move price means the aggressor is being absorbed by resting orders, which frequently marks the turn.\n\nBlank cells mean the buy and sell split was unavailable for that bar, so the subtraction has no inputs.'
tooltip_pct_delta: str = 'Delta as a percentage of classified volume, so bars of very different size stay directly comparable.\n\nHow to read it: this normalizes conviction. Forty percent on a quiet bar is a more one-sided tape than a larger raw delta on a heavy bar. Clusters of same-sign readings across consecutive bars mark sustained pressure rather than a single aggressive print.\n\nBlank cells mean the buy and sell split was unavailable for that bar.'
tooltip_liq_naming: str = 'Sets which side a liquidation row is named after. The two conventions are mirror images, because a long being closed out fires a market sell and a short being closed out fires a market buy.\n\nLiquidated position side: a long being wiped out counts as a BUY liquidation, since buyers were the side liquidated. This is how most order-flow desks read it and is the default.\n\nResulting order side: the same event counts as a SELL, since a market sell hit the book.\n\nThe underlying data is identical either way. Only the labels swap.'
tooltip_buy_liq: str = 'Forced closure of long positions, sized in contract units. Under the default naming, buyers are the side being liquidated.\n\nHow to read it: liquidations are leverage being flushed, and they arrive as forced market selling. Clusters print at local lows and frequently mark exhaustion, because once the leveraged longs are gone there is nobody left to force out. Size matters far more than frequency, one large liquidation moves price more than many small ones.\n\nValues may arrive in base or quote currency depending on the venue, so read magnitudes against the past behavior of this symbol rather than comparing them across exchanges. A 0 means the feed is live and nothing was liquidated in that bar. Cells reading unavailable mean this data is not available for the charted ticker.'
tooltip_sell_liq: str = 'Forced closure of short positions, sized in contract units. Under the default naming, sellers are the side being liquidated.\n\nHow to read it: this is squeeze fuel. Short liquidations arrive as forced market buying, so a cascade here accelerates upside moves and often produces the vertical segment of a rally. Pair it with open interest, a squeeze that drops open interest is covering rather than fresh buying, and tends to fade.\n\nA 0 means the feed is live and nothing was liquidated. Unavailable means this data is not available for the charted ticker.'
tooltip_total_liq: str = 'Combined liquidation volume for the bar, both sides together.\n\nHow to read it: this is a pure stress gauge for when magnitude matters more than direction. Spikes mark the moments the market forced positions out, which are the bars worth revisiting when you review a session. Read it against the delta liquidation row to see which side wore the damage.\n\nA 0 means the feed is live and nothing was liquidated. Unavailable means this data is not available for the charted ticker.'
tooltip_delta_liq: str = 'Net liquidation pressure: buy liquidations minus sell liquidations.\n\nHow to read it: when both sides are firing at once, this isolates who is actually being hurt. A large positive reading is longs being flushed, negative is shorts being squeezed. A sign flip mid-trend often marks the handover from one side capitulating to the other.\n\nA 0 means the feed is live and the two sides cancelled out. Unavailable means this data is not available for the charted ticker.'
tooltip_oi: str = 'Bar-over-bar change in open interest, the total number of contracts outstanding.\n\nHow to read it: this separates new money from unwinding, and it is the single most useful row to pair with price. Price up with open interest up is fresh longs. Price up with open interest down is shorts covering, which is less durable. Price down with open interest up is fresh shorts. Price down with open interest down is longs closing out.\n\nCells reading unavailable mean this data is not available for the charted ticker.'
tooltip_net_long: str = 'Net long participation for the bar, derived from delta and the change in open interest together.\n\nHow to read it: delta alone tells you who was aggressive, open interest alone tells you whether positions grew. Combining them separates aggressive buying that opened new longs from aggressive buying that merely closed shorts. A strongly positive reading is fresh long exposure entering.\n\nThis row needs both delta and open interest. If either is unavailable for the symbol the row reads unavailable rather than defaulting to zero, since a missing input is not the same as a zero result.'
tooltip_net_short: str = 'Net short participation for the bar, derived from delta and the change in open interest together.\n\nHow to read it: net long plus net short always reconciles to delta, and net long minus net short reconciles to the open interest change, so the pair ties back to both inputs and can be checked against the rows above. Read the two together, both positive means both sides added exposure into the bar.\n\nThis row needs both delta and open interest. If either is unavailable the row reads unavailable rather than zero.'
tooltip_funding: str = 'The funding rate in force during the bar, shown as a percentage. Funding is the periodic payment between longs and shorts that keeps a perpetual contract tethered to spot.\n\nHow to read it: positive funding means longs are paying shorts, so the crowd sits long and pays to stay there. Persistently elevated funding is a crowded trade and raises the odds of a long squeeze. Negative funding flips the payment and often marks pessimistic positioning near lows. Funding settles on the exchange interval, usually every eight hours, so the row holds flat between settlements by design.\n\nCells reading unavailable mean this data is not available for the charted ticker.'
tooltip_close: str = 'The closing price of the charted contract for each bar, read straight from the chart.\n\nHow to read it: this keeps the table self-contained. You can scan a full bar of order flow with its price in the same row of cells, without moving your eye back to the candles above. The cell is colored by the bar-over-bar change, so the row doubles as a compact price direction strip running beneath the statistics.'
tooltip_fr_scale: str = 'Unit conversion applied to the funding feed.\n\nDecimal to percent: the feed publishes a decimal fraction, so 0.0001 displays as 0.0100%. This is correct for the major perpetual venues and is the right choice for virtually every symbol.\n\nAuto: sorts every bar in the history into a magnitude bucket and applies whichever scale fits the majority, so one unusual bar cannot skew the whole chart.\n\nAlready percent and Basis points cover venues that publish on a different unit. If the funding row looks off by a factor of 100 or 10000, this is the setting to change.'
tooltip_fr_heat: str = 'Controls what the funding cell color is measured against.\n\nLevel: colors each cell by the funding rate itself. When funding sits pinned at one value the row becomes a flat saturated band, and that flatness is the signal, it tells you at a glance that funding has been one-sided across the whole window.\n\nDeviation from average: colors against the rolling average instead, which surfaces the individual bars where funding ran rich or cheap relative to its recent norm. Use this when funding rarely moves and you want the exceptions to stand out.'
tooltip_display: str = 'Coin reports volume, delta, liquidations and open interest in base units of the contract, which is how the exchange publishes them.\n\nQuote currency multiplies those rows by price to give notional value in whatever the contract settles in, so readings are comparable across assets and across time as price moves. Useful when watching several symbols side by side, or when comparing current activity against a period where price was far lower. A dollar sign is added when the symbol settles in a dollar unit.\n\nFunding stays a percentage and the closing price stays a price under both settings.'
tooltip_heat_len: str = 'Lookback used to scale cell intensity. Each cell is shaded against the largest absolute value its own row produced across this window, so color always reads relative to recent conditions rather than a fixed scale that would go dark on quiet symbols.\n\nHow to choose it: shorter windows make the table reactive, so ordinary bars still show color and you can read rhythm. Longer windows reserve full saturation for genuine outliers, so the table stays dark until something unusual happens. 50 suits intraday work, 200 or more suits scanning for extremes.'
tooltip_ticks_row: str = 'Price granularity the bid/ask engine uses when dissecting each bar internally, measured in ticks per price level.\n\nThis table reads bar totals only, never individual price levels, so this setting has no effect on any number you see. It is a performance control. A small value makes the engine build dozens of price levels per bar; a large value builds one or two and does the same job here. Leave it high.'
tooltip_engine: str = 'Sets where the buy and sell split comes from.\n\nThe indicator reads volume footprint data, which requires a Premium or Ultimate plan. That data loads before any setting is read, so the requirement applies to the whole script regardless of the mode selected here.\n\nBid/ask engine: reads TradingView bid and ask data to show which side initiated each trade. Bars it cannot serve read as unavailable.\n\nBid/ask engine with estimate: the same, but bars the engine cannot serve fall back to a range-based approximation so the row stays continuous. Estimated cells are flagged with a tilde on the row tag.\n\nEstimate from bar range: approximates the split from where each bar closed within its range. Useful on symbols or periods where bid and ask data is thin.\n\nOff: leaves the four delta rows out entirely. Use this if you want a clean ten-row table of liquidations, open interest, funding and volume.'
tooltip_net_mode: str = 'Sets how net long and net short are derived.\n\nDelta and OI split: net long is half the sum of delta and the open interest change, net short is half the difference. Both rows carry a value every bar and always reconcile back to delta and open interest, which makes them checkable against the rows above.\n\nPrice and OI quadrant: assigns the whole bar to a single side based on whether price and open interest rose or fell together. Reads more cleanly on trending charts, at the cost of leaving one of the two rows empty each bar.'
tooltip_swap: str = 'Swaps the two raw liquidation feeds before anything else is applied. Only needed on the rare venue that publishes them inverted, which you would spot as liquidation clusters appearing on the wrong side of a sharp move.\n\nThis is separate from Liquidation Naming, which relabels the rows without touching the underlying data.'
tooltip_abbrev: str = 'Abbreviates thousands and millions so cells stay narrow enough to scan at a glance.\n\nThis is not rounding. The abbreviated figure carries its decimals through, so 73950.12 reads 73.95K rather than 74K, and you keep the precision while gaining the space. Switch it off to print every figure in full, which suits wide panes and fewer columns.'
tooltip_decimals: str = 'Precision applied to every printed figure.\n\nAuto keeps two decimals at or above 1 and six below it, then drops trailing zeros. A whole number stays whole, a fractional one keeps its digits, and small liquidation sizes stay readable instead of collapsing to 0.\n\nA fixed count overrides that when you want every cell aligned to identical precision, which reads more evenly in screenshots.'
tooltip_na_text: str = 'Text printed when a feed does not exist for the symbol, or has no data for that bar.\n\nA genuine zero still prints as 0, so an empty reading and a missing reading are never confused with each other. Hover the row tag of any row showing this text for the specific reason it is unavailable.'
tooltip_show_names: str = 'Shows the row name tags down the right side of the table.\n\nEach tag carries a tooltip explaining what that row measures, how to interpret it, and what it means if the cells are blank. Rows without data are dimmed and marked so you can see at a glance which statistics the current symbol supports.'
tooltip_name_style: str = 'Short keeps the tag column narrow, which matters when the pane is short or you are running many rows. Full spells every row name out, which reads better in screenshots and when sharing setups with someone who has not used the table before.'
tooltip_name_gap: str = 'Distance between the right edge of the last cell and the row name tags, measured in bars. Zero sits the tags flush against the table. Increase it if the tags crowd the final column of figures.'
tooltip_show_values: str = 'Prints the numeric value inside each cell on recent bars.\n\nTurn it off for a pure heat map. Color spans the full chart history, so with numbers off you can zoom out and read weeks or months of order flow as a single pattern, which is the fastest way to spot regime changes in funding, open interest and liquidation activity.'
tooltip_max_cols: str = 'Upper bound on how many recent bars carry printed figures.\n\nColor spans the full chart history regardless. Text is drawn with label objects and the platform caps those at 500 per script, shared across every enabled row, so the real ceiling is 500 minus one tag per row divided by the row count. With every row enabled that is 34 columns, and raising this beyond 34 has no effect. Switch rows off to buy more columns, at seven rows the ceiling is 70.\n\nLabels are the most memory-hungry object a script can create, so keep this only as high as you actually read.'
tooltip_colors: str = 'Pre-configured color schemes for the heat cells. Custom allows full control using the two color inputs below. Classic uses traditional green and red. Aqua provides ocean-inspired tones. Cosmic offers futuristic cyan and purple. Cyber features warm orange against cool cyan. Neon delivers high-contrast yellow and magenta for maximum visibility.\n\nText color inside every cell is calculated automatically from the cell shade, so figures stay legible on any scheme you pick.'
tooltip_bullish: str = 'Color applied to positive readings, at full saturation for the strongest value in the lookback window. Only applies when Color Preset is set to Custom.'
tooltip_bearish: str = 'Color applied to negative readings, at full saturation for the strongest value in the lookback window. Only applies when Color Preset is set to Custom.'
tooltip_zero: str = 'Color applied to cells at or near zero. Every cell is painted on every bar, so this is what an inactive row looks like rather than an empty gap, which keeps the table reading as a solid grid.'
tooltip_gamma: str = 'Curve applied to cell intensity.\n\nValues below 1 lift the mid-range so moderate activity still shows color and the table reads as a continuous gradient. Values above 1 suppress the mid-range so only genuine extremes light up and everything else stays dark. Lower it for rhythm, raise it for outlier hunting.'
tooltip_text_size: str = 'Size of the printed figures inside each cell. Reduce it when running many rows in a short pane, or when you have raised Max Numbered Bars and the columns have narrowed.'
tooltip_tint_total: str = 'Colors the total volume row by the sign of delta rather than by magnitude alone, so a heavy bar immediately reads as buyer or seller dominated and you get two pieces of information from one cell.'
tooltip_pane_bg: str = 'Background color of the indicator pane behind the table.'
tooltip_name_bg: str = 'Background color of the row name tags. Tags for rows without data are automatically dimmed toward the pane background, and their text color is calculated to stay legible against whichever shade you pick.'


@script.indicator('Order Flow Bar Statistics [QuantAlgo]', overlay=False, max_labels_count=500, explicit_plot_zorder=True)
def main(
    show_buy_vol=input.bool(True, 'Buy Volume', group=volume_settings, tooltip=tooltip_buy_vol),
    show_sell_vol=input.bool(True, 'Sell Volume', group=volume_settings, tooltip=tooltip_sell_vol),
    show_total_vol=input.bool(True, 'Total Volume', group=volume_settings, tooltip=tooltip_total_vol),
    show_delta_vol=input.bool(True, 'Delta Volume', group=volume_settings, tooltip=tooltip_delta_vol),
    show_pct_delta=input.bool(True, 'Percent Delta', group=volume_settings, tooltip=tooltip_pct_delta),
    liq_naming=input.string('Liquidated position side', 'Liquidation Naming', options=('Liquidated position side', 'Resulting order side'), group=liq_settings, tooltip=tooltip_liq_naming),
    show_buy_liq=input.bool(True, 'Buy Liquidations', group=liq_settings, tooltip=tooltip_buy_liq),
    show_sell_liq=input.bool(True, 'Sell Liquidations', group=liq_settings, tooltip=tooltip_sell_liq),
    show_total_liq=input.bool(True, 'Total Liquidations', group=liq_settings, tooltip=tooltip_total_liq),
    show_delta_liq=input.bool(True, 'Delta Liquidations', group=liq_settings, tooltip=tooltip_delta_liq),
    show_oi=input.bool(True, 'Open Interest', group=interest_settings, tooltip=tooltip_oi),
    show_net_long=input.bool(True, 'Net Long', group=interest_settings, tooltip=tooltip_net_long),
    show_net_short=input.bool(True, 'Net Short', group=interest_settings, tooltip=tooltip_net_short),
    net_mode=input.string('Delta and OI split', 'Positioning Method', options=('Delta and OI split', 'Price and OI quadrant'), group=interest_settings, tooltip=tooltip_net_mode),
    show_funding=input.bool(True, 'Funding Rate', group=funding_settings, tooltip=tooltip_funding),
    show_close=input.bool(True, 'Close Price', group=funding_settings, tooltip=tooltip_close),
    fr_scale=input.string('Decimal to percent', 'Funding Scale', options=('Decimal to percent', 'Auto', 'Already percent', 'Basis points'), group=funding_settings, tooltip=tooltip_fr_scale),
    fr_heat_mode=input.string('Level', 'Funding Heat', options=('Level', 'Deviation from average'), group=funding_settings, tooltip=tooltip_fr_heat),
    display_mode=input.string('Coin', 'Display Mode', options=('Coin', 'Quote currency'), group=source_settings, tooltip=tooltip_display),
    heat_length=input.int(50, 'Heat Lookback', minval=5, maxval=500, group=source_settings, tooltip=tooltip_heat_len),
    ticks_per_row=input.int(5000, 'Footprint Row Size', minval=1, group=source_settings, tooltip=tooltip_ticks_row),
    delta_engine=input.string('Bid/ask engine', 'Delta Engine', options=('Bid/ask engine', 'Bid/ask engine with estimate', 'Estimate from bar range', 'Off'), group=source_settings, tooltip=tooltip_engine),
    swap_feeds=input.bool(False, 'Swap Liquidation Feeds', group=source_settings, tooltip=tooltip_swap),
    abbreviate=input.bool(True, 'Abbreviate Thousands', group=number_settings, tooltip=tooltip_abbrev),
    decimal_mode=input.string('Auto', 'Decimals', options=('Auto', '0', '1', '2', '3', '4', '6'), group=number_settings, tooltip=tooltip_decimals),
    na_text=input.string('N/A', 'Missing Data Text', group=number_settings, tooltip=tooltip_na_text),
    show_names=input.bool(True, 'Show Row Names', group=layout_settings, tooltip=tooltip_show_names),
    name_style=input.string('Full', 'Row Name Style', options=('Short', 'Full'), group=layout_settings, tooltip=tooltip_name_style),
    name_gap=input.float(0.15, 'Row Name Gap', minval=0.0, maxval=4.0, step=0.05, group=layout_settings, tooltip=tooltip_name_gap),
    show_values=input.bool(True, 'Show Numbers', group=layout_settings, tooltip=tooltip_show_values),
    max_columns=input.int(30, 'Max Numbered Bars', minval=1, maxval=100, group=layout_settings, tooltip=tooltip_max_cols),
    color_preset=input.string('Custom', 'Color Preset', options=('Custom', 'Classic', 'Aqua', 'Cosmic', 'Cyber', 'Neon'), group=visual_settings, tooltip=tooltip_colors),
    bullish_input=input.color(color.new('#00FFAA'), 'Bullish Color', group=visual_settings, tooltip=tooltip_bullish),
    bearish_input=input.color(color.new('#FF0000'), 'Bearish Color', group=visual_settings, tooltip=tooltip_bearish),
    zero_color=input.color(color.new('#141414'), 'Zero Color', group=visual_settings, tooltip=tooltip_zero),
    heat_gamma=input.float(0.55, 'Intensity Gamma', minval=0.2, maxval=1.5, step=0.05, group=visual_settings, tooltip=tooltip_gamma),
    text_size_in=input.string('Small', 'Cell Text Size', options=('Tiny', 'Small', 'Normal'), group=visual_settings, tooltip=tooltip_text_size),
    tint_by_delta=input.bool(True, 'Tint Total By Delta', group=visual_settings, tooltip=tooltip_tint_total),
    pane_bg=input.color(color.new('#000000'), 'Pane Background', group=visual_settings, tooltip=tooltip_pane_bg),
    name_bg=input.color(color.new('#2A2A2A'), 'Row Name Background', group=visual_settings, tooltip=tooltip_name_bg)
):
    __block_result__ = (na, na)
    __switch__ = color_preset
    if __switch__ == 'Classic':
        __block_result__ = (color.new('#00FF00'), color.new('#FF0000'))
    elif __switch__ == 'Aqua':
        __block_result__ = (color.new('#00D4FF'), color.new('#FF8C00'))
    elif __switch__ == 'Cosmic':
        __block_result__ = (color.new('#49FFCE'), color.new('#9932CC'))
    elif __switch__ == 'Cyber':
        __block_result__ = (color.new('#00CCCC'), color.new('#FF6600'))
    elif __switch__ == 'Neon':
        __block_result__ = (color.new('#FFFF00'), color.new('#FF00FF'))
    else:
        __block_result__ = (bullish_input, bearish_input)
    bullish_color, bearish_color = __block_result__

    as_quote = display_mode == 'Quote currency'
    name_by_pos = liq_naming == 'Liquidated position side'
    short_names = name_style == 'Short'
    name_bg_off = color.from_gradient(0.6, 0.0, 1.0, name_bg, pane_bg)

    def cell_size():
        __block_result_1__ = na
        __switch__ = text_size_in
        if __switch__ == 'Small':
            __block_result_1__ = size.small
        elif __switch__ == 'Normal':
            __block_result_1__ = size.normal
        else:
            __block_result_1__ = size.tiny
        return __block_result_1__

    def decimal_pattern(magnitude: float):
        __block_result_2__ = na
        __switch__ = decimal_mode
        if __switch__ == '0':
            __block_result_2__ = 0
        elif __switch__ == '1':
            __block_result_2__ = 1
        elif __switch__ == '2':
            __block_result_2__ = 2
        elif __switch__ == '3':
            __block_result_2__ = 3
        elif __switch__ == '4':
            __block_result_2__ = 4
        elif __switch__ == '6':
            __block_result_2__ = 6
        else:
            __block_result_2__ = 2 if magnitude >= 1.0 else 6
        places: int = __block_result_2__
        __block_result_3__ = na
        __switch__ = places
        if __switch__ == 0:
            __block_result_3__ = '0'
        elif __switch__ == 1:
            __block_result_3__ = '0.#'
        elif __switch__ == 2:
            __block_result_3__ = '0.##'
        elif __switch__ == 3:
            __block_result_3__ = '0.###'
        elif __switch__ == 4:
            __block_result_3__ = '0.####'
        else:
            __block_result_3__ = '0.######'
        return __block_result_3__

    def format_value(value: float, as_quote: bool):
        out: str = na_text
        if not na(value):
            magnitude: float = math.abs(value)
            sign: str = '-' if value < 0 else ''
            unit: str = '$' if as_quote and string.startswith(syminfo.currency, 'USD') else ''
            if magnitude == 0.0:
                out = '0'
            elif abbreviate and magnitude >= 1000000.0:
                scaled: float = magnitude / 1000000.0
                out = sign + unit + string.tostring(scaled, decimal_pattern(scaled)) + 'M'
            elif abbreviate and magnitude >= 1000.0:
                scaled: float = magnitude / 1000.0
                out = sign + unit + string.tostring(scaled, decimal_pattern(scaled)) + 'K'
            else:
                out = sign + unit + string.tostring(magnitude, decimal_pattern(magnitude))
        return out

    def format_percent(value: float):
        return na_text if na(value) else string.tostring(value, decimal_pattern(math.abs(value))) + '%'

    def format_price(value: float):
        return na_text if na(value) else string.tostring(value, format.mintick)

    def format_rate(value: float, multiplier: float):
        return na_text if na(value) else string.tostring(value * multiplier, '0.0000') + '%'

    def heat(source_value: float, extreme: float, sign_by: float):
        reading: float = nz(source_value)
        reference: float = nz(extreme)
        magnitude: float = 0.0 if reference <= 0.0 else math.min(1.0, math.pow(math.abs(reading) / reference, heat_gamma))
        return color.from_gradient(magnitude, 0.0, 1.0, zero_color, bullish_color if nz(sign_by) >= 0.0 else bearish_color)

    def srgb_channel(channel: float):
        unit: float = channel / 255.0
        return unit / 12.92 if unit <= 0.03928 else math.pow((unit + 0.055) / 1.055, 2.4)

    def relative_luminance(shade: Color):
        return 0.2126 * srgb_channel(color.r(shade)) + 0.7152 * srgb_channel(color.g(shade)) + 0.0722 * srgb_channel(color.b(shade))

    def readable_text(background: Color):
        luminance: float = relative_luminance(background)
        versus_dark: float = (luminance + 0.05) / 0.05
        versus_light: float = 1.05 / (luminance + 0.05)
        return color.black if versus_dark >= versus_light else color.white

    def muted_text(background: Color):
        return color.new(readable_text(background), 35)

    def highest_abs(source_value: float, length: int):
        return ta.highest(math.abs(nz(source_value)), length)

    def rising(source_value: Series[float]):
        return not na(source_value) and (not na(source_value[1])) and (source_value > source_value[1])

    def falling(source_value: Series[float]):
        return not na(source_value) and (not na(source_value[1])) and (source_value < source_value[1])

    def turns_positive(source_value: Series[float]):
        return not na(source_value) and (not na(source_value[1])) and (source_value > 0) and (source_value[1] <= 0)

    def turns_negative(source_value: Series[float]):
        return not na(source_value) and (not na(source_value[1])) and (source_value < 0) and (source_value[1] >= 0)

    feed_id = syminfo.prefix + ':' + syminfo.ticker
    lq_buy_id = feed_id + '_LQBUY'
    lq_sell_id = feed_id + '_LQSELL'
    oi_id = feed_id + '_OI'
    fr_id = feed_id + '_FR'

    query_engine: bool = delta_engine == 'Bid/ask engine' or delta_engine == 'Bid/ask engine with estimate'
    allow_estimate: bool = delta_engine == 'Bid/ask engine with estimate' or delta_engine == 'Estimate from bar range'

    bar_print: Footprint = na(Footprint)
    if query_engine:
        bar_print = request.footprint(ticks_per_row)
    print_ok: bool = not na(bar_print)

    print_ever: Persistent[bool] = False
    if print_ok:
        print_ever = True

    delta_live: bool = print_ever or allow_estimate

    bar_span: float = high - low
    estimate_buy: float = nz(volume) * 0.5 if bar_span == 0.0 else nz(volume) * (close - low) / bar_span
    estimate_sell: float = nz(volume) * 0.5 if bar_span == 0.0 else nz(volume) * (high - close) / bar_span

    buy_volume: float = na(float)
    sell_volume: float = na(float)
    if print_ok:
        buy_volume = footprint.buy_volume(bar_print)
        sell_volume = footprint.sell_volume(bar_print)
    elif allow_estimate:
        buy_volume = estimate_buy
        sell_volume = estimate_sell

    total_volume: float = volume
    delta_volume: float = buy_volume - sell_volume
    classified: float = buy_volume + sell_volume
    percent_delta: float = na if na(classified) or classified == 0.0 else 100.0 * delta_volume / classified

    shown_buy: float = buy_volume * close if as_quote else buy_volume
    shown_sell: float = sell_volume * close if as_quote else sell_volume
    shown_total: float = total_volume * close if as_quote else total_volume
    shown_delta: float = delta_volume * close if as_quote else delta_volume

    need_liq: bool = show_buy_liq or show_sell_liq or show_total_liq or show_delta_liq
    need_oi: bool = show_oi or show_net_long or show_net_short

    lq_buy_raw: float = na(float)
    lq_sell_raw: float = na(float)
    oi_series: float = na(float)
    fr_raw: float = na(float)

    if need_liq:
        lq_buy_raw = request.security(lq_buy_id, timeframe.period, volume, gaps=barmerge.gaps_on, ignore_invalid_symbol=True)
        lq_sell_raw = request.security(lq_sell_id, timeframe.period, volume, gaps=barmerge.gaps_on, ignore_invalid_symbol=True)
    if need_oi:
        oi_series = request.security(oi_id, timeframe.period, close, ignore_invalid_symbol=True)
    if show_funding:
        fr_raw = request.security(fr_id, timeframe.period, close, ignore_invalid_symbol=True)

    liq_ok: Persistent[bool] = False
    oi_ok: Persistent[bool] = False
    fr_ok: Persistent[bool] = False
    if not na(lq_buy_raw) or not na(lq_sell_raw):
        liq_ok = True
    if not na(oi_series):
        oi_ok = True
    if not na(fr_raw):
        fr_ok = True

    order_buy: float = nz(lq_sell_raw) if swap_feeds else nz(lq_buy_raw)
    order_sell: float = nz(lq_buy_raw) if swap_feeds else nz(lq_sell_raw)

    buy_liq: float = (order_sell if name_by_pos else order_buy) if liq_ok else na
    sell_liq: float = (order_buy if name_by_pos else order_sell) if liq_ok else na
    total_liq: float = buy_liq + sell_liq if liq_ok else na
    delta_liq: float = buy_liq - sell_liq if liq_ok else na

    oi_change: float = nz(ta.change(oi_series)) if oi_ok else na
    shown_oi: float = oi_change * close if as_quote else oi_change

    net_ok: bool = oi_ok and (not na(delta_volume))
    net_live: bool = oi_ok and delta_live
    net_long: float = na(float)
    net_short: float = na(float)
    if net_ok:
        if net_mode == 'Price and OI quadrant':
            price_change: float = close - close[1]
            net_long = 0.0
            net_short = 0.0
            if price_change > 0.0 and oi_change > 0.0:
                net_long = oi_change
            elif price_change < 0.0 and oi_change < 0.0:
                net_long = oi_change
            elif price_change < 0.0 and oi_change > 0.0:
                net_short = oi_change
            elif price_change > 0.0 and oi_change < 0.0:
                net_short = oi_change
        else:
            net_long = (delta_volume + oi_change) / 2.0
            net_short = (delta_volume - oi_change) / 2.0
    shown_long: float = net_long * close if as_quote else net_long
    shown_short: float = net_short * close if as_quote else net_short

    close_price: float = close
    close_change: float = nz(ta.change(close_price))

    rate_tiny: Persistent[int] = 0
    rate_dec: Persistent[int] = 0
    rate_pct: Persistent[int] = 0
    if not na(fr_raw) and fr_raw != 0.0:
        rate_size: float = math.abs(fr_raw)
        if rate_size < 5e-05:
            rate_tiny += 1
        elif rate_size < 0.05:
            rate_dec += 1
        else:
            rate_pct += 1
    rate_auto: float = 100.0 if rate_dec >= rate_tiny and rate_dec >= rate_pct else 10000.0 if rate_tiny >= rate_pct else 1.0

    __block_result_4__ = na
    __switch__ = fr_scale
    if __switch__ == 'Already percent':
        __block_result_4__ = 1.0
    elif __switch__ == 'Basis points':
        __block_result_4__ = 10000.0
    elif __switch__ == 'Auto':
        __block_result_4__ = rate_auto
    else:
        __block_result_4__ = 100.0
    rate_multiplier: float = __block_result_4__

    rate_average: float = ta.sma(nz(fr_raw), heat_length)
    rate_heat: float = na if not fr_ok else fr_raw if fr_heat_mode == 'Level' else fr_raw - nz(rate_average)

    hi_buy: float = highest_abs(shown_buy, heat_length)
    hi_sell: float = highest_abs(shown_sell, heat_length)
    hi_total: float = highest_abs(shown_total, heat_length)
    hi_delta: float = highest_abs(shown_delta, heat_length)
    hi_percent: float = highest_abs(percent_delta, heat_length)
    hi_buy_liq: float = highest_abs(buy_liq, heat_length)
    hi_sell_liq: float = highest_abs(sell_liq, heat_length)
    hi_total_liq: float = highest_abs(total_liq, heat_length)
    hi_delta_liq: float = highest_abs(delta_liq, heat_length)
    hi_oi: float = highest_abs(shown_oi, heat_length)
    hi_long: float = highest_abs(shown_long, heat_length)
    hi_short: float = highest_abs(shown_short, heat_length)
    hi_rate: float = highest_abs(rate_heat, heat_length)
    hi_close: float = highest_abs(close_change, heat_length)

    tint_buy: Color = heat(shown_buy, hi_buy, 1.0)
    tint_sell: Color = heat(shown_sell, hi_sell, -1.0)
    tint_total: Color = heat(shown_total, hi_total, shown_delta if tint_by_delta else 1.0)
    tint_delta: Color = heat(shown_delta, hi_delta, shown_delta)
    tint_percent: Color = heat(percent_delta, hi_percent, percent_delta)
    tint_buy_liq: Color = heat(buy_liq, hi_buy_liq, 1.0)
    tint_sell_liq: Color = heat(sell_liq, hi_sell_liq, -1.0)
    tint_total_liq: Color = heat(total_liq, hi_total_liq, 1.0)
    tint_delta_liq: Color = heat(delta_liq, hi_delta_liq, delta_liq)
    tint_oi: Color = heat(shown_oi, hi_oi, shown_oi)
    tint_long: Color = heat(shown_long, hi_long, shown_long)
    tint_short: Color = heat(shown_short, hi_short, -shown_short)
    tint_rate: Color = heat(rate_heat, hi_rate, rate_heat)
    tint_close: Color = heat(close_change, hi_close, close_change)

    row_count: int = (1 if show_buy_vol else 0) + (1 if show_sell_vol else 0) + (1 if show_total_vol else 0) + (1 if show_delta_vol else 0) + (1 if show_pct_delta else 0) + (1 if show_buy_liq else 0) + (1 if show_sell_liq else 0) + (1 if show_total_liq else 0) + (1 if show_delta_liq else 0) + (1 if show_oi else 0) + (1 if show_net_long else 0) + (1 if show_net_short else 0) + (1 if show_funding else 0) + (1 if show_close else 0)

    top_01: float = row_count
    top_02: float = top_01 - (1 if show_buy_vol else 0)
    top_03: float = top_02 - (1 if show_sell_vol else 0)
    top_04: float = top_03 - (1 if show_total_vol else 0)
    top_05: float = top_04 - (1 if show_delta_vol else 0)
    top_06: float = top_05 - (1 if show_pct_delta else 0)
    top_07: float = top_06 - (1 if show_buy_liq else 0)
    top_08: float = top_07 - (1 if show_sell_liq else 0)
    top_09: float = top_08 - (1 if show_total_liq else 0)
    top_10: float = top_09 - (1 if show_delta_liq else 0)
    top_11: float = top_10 - (1 if show_oi else 0)
    top_12: float = top_11 - (1 if show_net_long else 0)
    top_13: float = top_12 - (1 if show_net_short else 0)
    top_14: float = top_13 - (1 if show_funding else 0)

    reserved_labels: int = row_count if show_names else 0
    column_cap: int = cast_int((500 - reserved_labels) / row_count) if row_count > 0 else 1
    numbered_bars: int = math.max(1, math.min(column_cap, max_columns))

    bgcolor(pane_bg, title='Pane Background')

    plot(top_01 if show_buy_vol else na, 'Buy Volume', color=tint_buy, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_02 if show_sell_vol else na, 'Sell Volume', color=tint_sell, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_03 if show_total_vol else na, 'Total Volume', color=tint_total, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_04 if show_delta_vol else na, 'Delta Volume', color=tint_delta, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_05 if show_pct_delta else na, 'Percent Delta', color=tint_percent, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_06 if show_buy_liq else na, 'Buy Liquidations', color=tint_buy_liq, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_07 if show_sell_liq else na, 'Sell Liquidations', color=tint_sell_liq, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_08 if show_total_liq else na, 'Total Liquidations', color=tint_total_liq, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_09 if show_delta_liq else na, 'Delta Liquidations', color=tint_delta_liq, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_10 if show_oi else na, 'Open Interest', color=tint_oi, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_11 if show_net_long else na, 'Net Long', color=tint_long, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_12 if show_net_short else na, 'Net Short', color=tint_short, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_13 if show_funding else na, 'Funding Rate', color=tint_rate, style=plot.style_columns, histbase=0, display=display.pane, editable=False)
    plot(top_14 if show_close else na, 'Close Price', color=tint_close, style=plot.style_columns, histbase=0, display=display.pane, editable=False)

    plot(0.0, 'Scale Floor', color=color.new(color.black, 100), display=display.pane, editable=False)
    plot(math.max(row_count, 1), 'Scale Ceiling', color=color.new(color.black, 100), display=display.pane, editable=False)

    column_bar: Persistent[list[int]] = array.new_int()
    cell_text: Persistent[list[str]] = array.new_string()
    cell_tint: Persistent[list[Color]] = array.new_color()

    in_window: bool = show_values and row_count > 0 and (last_bar_index - bar_index < numbered_bars)

    if in_window:
        logged: int = array.get(column_bar, array.size(column_bar) - 1) if array.size(column_bar) > 0 else -1
        if bar_index != logged:
            array.push(column_bar, bar_index)
            for slot in pine_range(0, row_count - 1):
                array.push(cell_text, '')
                array.push(cell_tint, zero_color)
            while array.size(column_bar) > numbered_bars:
                array.shift(column_bar)
                for slot in pine_range(0, row_count - 1):
                    array.shift(cell_text)
                    array.shift(cell_tint)
        cursor: int = array.size(cell_text) - row_count
        if show_buy_vol:
            array.set(cell_text, cursor, format_value(shown_buy, as_quote))
            array.set(cell_tint, cursor, tint_buy)
            cursor += 1
        if show_sell_vol:
            array.set(cell_text, cursor, format_value(shown_sell, as_quote))
            array.set(cell_tint, cursor, tint_sell)
            cursor += 1
        if show_total_vol:
            array.set(cell_text, cursor, format_value(shown_total, as_quote))
            array.set(cell_tint, cursor, tint_total)
            cursor += 1
        if show_delta_vol:
            array.set(cell_text, cursor, format_value(shown_delta, as_quote))
            array.set(cell_tint, cursor, tint_delta)
            cursor += 1
        if show_pct_delta:
            array.set(cell_text, cursor, format_percent(percent_delta))
            array.set(cell_tint, cursor, tint_percent)
            cursor += 1
        if show_buy_liq:
            array.set(cell_text, cursor, format_value(buy_liq, False))
            array.set(cell_tint, cursor, tint_buy_liq)
            cursor += 1
        if show_sell_liq:
            array.set(cell_text, cursor, format_value(sell_liq, False))
            array.set(cell_tint, cursor, tint_sell_liq)
            cursor += 1
        if show_total_liq:
            array.set(cell_text, cursor, format_value(total_liq, False))
            array.set(cell_tint, cursor, tint_total_liq)
            cursor += 1
        if show_delta_liq:
            array.set(cell_text, cursor, format_value(delta_liq, False))
            array.set(cell_tint, cursor, tint_delta_liq)
            cursor += 1
        if show_oi:
            array.set(cell_text, cursor, format_value(shown_oi, as_quote))
            array.set(cell_tint, cursor, tint_oi)
            cursor += 1
        if show_net_long:
            array.set(cell_text, cursor, format_value(shown_long, as_quote))
            array.set(cell_tint, cursor, tint_long)
            cursor += 1
        if show_net_short:
            array.set(cell_text, cursor, format_value(shown_short, as_quote))
            array.set(cell_tint, cursor, tint_short)
            cursor += 1
        if show_funding:
            array.set(cell_text, cursor, format_rate(fr_raw, rate_multiplier))
            array.set(cell_tint, cursor, tint_rate)
            cursor += 1
        if show_close:
            array.set(cell_text, cursor, format_price(close_price))
            array.set(cell_tint, cursor, tint_close)
            cursor += 1

    cell_pool: Persistent[list[Label]] = array.new_label()

    if barstate.islast:
        if show_values and row_count > 0 and (array.size(column_bar) > 0):
            pool_size: int = array.size(column_bar) * row_count
            if array.size(cell_pool) != pool_size:
                for old_cell in cell_pool:
                    label.delete(old_cell)
                array.clear(cell_pool)
                for slot in pine_range(0, pool_size - 1):
                    array.push(cell_pool, label.new(bar_index, 0.0, '', xloc=xloc.bar_index, style=label.style_none, size=cell_size()))
            for column in pine_range(0, array.size(column_bar) - 1):
                anchor: int = array.get(column_bar, column)
                for row in pine_range(0, row_count - 1):
                    slot: int = column * row_count + row
                    cell: Label = array.get(cell_pool, slot)
                    reading: str = array.get(cell_text, slot)
                    shade: Color = array.get(cell_tint, slot)
                    label.set_xy(cell, anchor, row_count - row - 0.5)
                    label.set_text(cell, reading)
                    label.set_textcolor(cell, muted_text(shade) if reading == na_text else readable_text(shade))
        else:
            for old_cell in cell_pool:
                label.delete(old_cell)
            array.clear(cell_pool)

    name_pool: Persistent[list[Label]] = array.new_label()
    row_names: Persistent[list[str]] = array.new_string()
    row_tips: Persistent[list[str]] = array.new_string()
    row_live: Persistent[list[bool]] = array.new_bool()

    if barstate.islast:
        if show_names and row_count > 0:
            tip_print: str = 'Aggressor side read from bid/ask data, showing which side crossed the spread on each trade. Buy plus sell always reconciles to total volume.' + (' Bars the engine cannot serve fall back to a range-based approximation, marked with a tilde on this tag.' if allow_estimate else ' Bars marked ' + na_text + ' have no bid/ask data for that period.') if print_ever else 'Approximated from where each bar closed within its range, marked with a tilde on this tag. The direction is the more dependable part of the reading, the magnitude is indicative. Set Delta Engine to Bid/ask engine to read TradingView bid and ask data instead.' if allow_estimate else 'Delta rows are switched off. Set Delta Engine under Data Source to Bid/ask engine to read TradingView bid and ask data, or to Estimate from bar range to approximate the split.'
            tip_volume: str = 'Total traded volume for the bar, read directly from the charted contract. Available on every symbol that reports volume.'
            tip_liq: str = 'Forced position closures, split by the side that was liquidated. A 0 means the feed is live and nothing was liquidated in that bar, which is different from ' + na_text + '.' if liq_ok else 'Liquidation data is not available for this ticker.'
            tip_oi: str = 'Bar-over-bar change in the total contracts outstanding. Rising means new positions opened, falling means positions closed or were forced out. Read it against price to tell fresh money from unwinding.' if oi_ok else 'Open interest data is not available for this ticker.'
            tip_net: str = 'Net long plus net short reconciles to delta, and net long minus net short reconciles to the open interest change, so the pair always ties back to both inputs and can be checked against the rows above.' if net_live else 'Needs both delta and open interest. One of the two is unavailable on this symbol, so the row cannot be calculated. That is not the same as a zero result.'
            tip_rate: str = 'Funding rate in force during the bar. Positive means longs pay shorts and the crowd sits long. It settles on the exchange interval, usually every eight hours, so the row holds flat between settlements by design.' if fr_ok else 'Funding data is not available for this ticker.'
            tip_close: str = 'Closing price of the charted contract for each bar, colored by the bar-over-bar change so the row reads as a price direction strip beneath the statistics.'

            approx: str = '' if print_ever or not allow_estimate else ' ~'

            array.clear(row_names)
            array.clear(row_tips)
            array.clear(row_live)

            if show_buy_vol:
                array.push(row_names, ('Buy vol' if short_names else 'Buy Volume') + approx)
                array.push(row_tips, tip_print)
                array.push(row_live, delta_live)
            if show_sell_vol:
                array.push(row_names, ('Sell vol' if short_names else 'Sell Volume') + approx)
                array.push(row_tips, tip_print)
                array.push(row_live, delta_live)
            if show_total_vol:
                array.push(row_names, 'Total vol' if short_names else 'Total Volume')
                array.push(row_tips, tip_volume)
                array.push(row_live, not na(volume))
            if show_delta_vol:
                array.push(row_names, ('Delta vol' if short_names else 'Delta Volume') + approx)
                array.push(row_tips, tip_print)
                array.push(row_live, delta_live)
            if show_pct_delta:
                array.push(row_names, ('% Delta' if short_names else 'Percent Delta') + approx)
                array.push(row_tips, tip_print)
                array.push(row_live, delta_live)
            if show_buy_liq:
                array.push(row_names, 'Buy liq' if short_names else 'Buy Liquidations')
                array.push(row_tips, tip_liq)
                array.push(row_live, liq_ok)
            if show_sell_liq:
                array.push(row_names, 'Sell liq' if short_names else 'Sell Liquidations')
                array.push(row_tips, tip_liq)
                array.push(row_live, liq_ok)
            if show_total_liq:
                array.push(row_names, 'Total liq' if short_names else 'Total Liquidations')
                array.push(row_tips, tip_liq)
                array.push(row_live, liq_ok)
            if show_delta_liq:
                array.push(row_names, 'Delta liq' if short_names else 'Delta Liquidations')
                array.push(row_tips, tip_liq)
                array.push(row_live, liq_ok)
            if show_oi:
                array.push(row_names, 'OI Δ' if short_names else 'Open Interest')
                array.push(row_tips, tip_oi)
                array.push(row_live, oi_ok)
            if show_net_long:
                array.push(row_names, 'Net L' if short_names else 'Net Long')
                array.push(row_tips, tip_net)
                array.push(row_live, net_live)
            if show_net_short:
                array.push(row_names, 'Net S' if short_names else 'Net Short')
                array.push(row_tips, tip_net)
                array.push(row_live, net_live)
            if show_funding:
                array.push(row_names, 'Funding' if short_names else 'Funding Rate')
                array.push(row_tips, tip_rate)
                array.push(row_live, fr_ok)
            if show_close:
                array.push(row_names, 'Close' if short_names else 'Close Price')
                array.push(row_tips, tip_close)
                array.push(row_live, True)

            name_anchor: int = time + cast_int(timeframe.in_seconds() * 1000.0 * (0.5 + name_gap))
            if array.size(name_pool) != array.size(row_names):
                for old_name in name_pool:
                    label.delete(old_name)
                array.clear(name_pool)
                for slot in pine_range(0, array.size(row_names) - 1):
                    array.push(name_pool, label.new(name_anchor, 0.0, '', xloc=xloc.bar_time, style=label.style_label_left, size=size.small))
            for slot in pine_range(0, array.size(row_names) - 1):
                tag: Label = array.get(name_pool, slot)
                live: bool = array.get(row_live, slot)
                face: Color = name_bg if live else name_bg_off
                label.set_xy(tag, name_anchor, row_count - slot - 0.5)
                label.set_text(tag, '  ' + array.get(row_names, slot) + ('' if live else '  ' + na_text) + '  ')
                label.set_color(tag, face)
                label.set_textcolor(tag, readable_text(face) if live else muted_text(face))
                label.set_tooltip(tag, array.get(row_names, slot) + '\n\n' + array.get(row_tips, slot))
        else:
            for old_name in name_pool:
                label.delete(old_name)
            array.clear(name_pool)

    buy_volume_up = rising(shown_buy)
    buy_volume_down = falling(shown_buy)
    sell_volume_up = rising(shown_sell)
    sell_volume_down = falling(shown_sell)
    total_volume_up = rising(shown_total)
    total_volume_down = falling(shown_total)
    delta_volume_positive = turns_positive(shown_delta)
    delta_volume_negative = turns_negative(shown_delta)
    percent_delta_up = rising(percent_delta)
    percent_delta_down = falling(percent_delta)
    buy_liquidations_up = rising(buy_liq)
    buy_liquidations_down = falling(buy_liq)
    sell_liquidations_up = rising(sell_liq)
    sell_liquidations_down = falling(sell_liq)
    total_liquidations_up = rising(total_liq)
    total_liquidations_down = falling(total_liq)
    delta_liquidations_positive = turns_positive(delta_liq)
    delta_liquidations_negative = turns_negative(delta_liq)
    open_interest_positive = turns_positive(shown_oi)
    open_interest_negative = turns_negative(shown_oi)
    net_long_positive = turns_positive(shown_long)
    net_long_negative = turns_negative(shown_long)
    net_short_positive = turns_positive(shown_short)
    net_short_negative = turns_negative(shown_short)
    funding_rate_up = rising(fr_raw)
    funding_rate_down = falling(fr_raw)
    close_price_up = rising(close_price)
    close_price_down = falling(close_price)

    alertcondition(buy_volume_up, title='Buy Volume Rising', message='Bar Statistics: buy volume rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(buy_volume_down, title='Buy Volume Falling', message='Bar Statistics: buy volume fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(sell_volume_up, title='Sell Volume Rising', message='Bar Statistics: sell volume rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(sell_volume_down, title='Sell Volume Falling', message='Bar Statistics: sell volume fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(total_volume_up, title='Total Volume Rising', message='Bar Statistics: total volume rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(total_volume_down, title='Total Volume Falling', message='Bar Statistics: total volume fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(delta_volume_positive, title='Delta Volume Turns Positive', message='Bar Statistics: delta volume turned positive, buyers took control on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(delta_volume_negative, title='Delta Volume Turns Negative', message='Bar Statistics: delta volume turned negative, sellers took control on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(percent_delta_up, title='Percent Delta Rising', message='Bar Statistics: percent delta rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(percent_delta_down, title='Percent Delta Falling', message='Bar Statistics: percent delta fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(buy_liquidations_up, title='Buy Liquidations Rising', message='Bar Statistics: buy liquidations rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(buy_liquidations_down, title='Buy Liquidations Falling', message='Bar Statistics: buy liquidations fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(sell_liquidations_up, title='Sell Liquidations Rising', message='Bar Statistics: sell liquidations rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(sell_liquidations_down, title='Sell Liquidations Falling', message='Bar Statistics: sell liquidations fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(total_liquidations_up, title='Total Liquidations Rising', message='Bar Statistics: total liquidations rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(total_liquidations_down, title='Total Liquidations Falling', message='Bar Statistics: total liquidations fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(delta_liquidations_positive, title='Delta Liquidations Turns Positive', message='Bar Statistics: liquidation delta turned positive on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(delta_liquidations_negative, title='Delta Liquidations Turns Negative', message='Bar Statistics: liquidation delta turned negative on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(open_interest_positive, title='Open Interest Turns Positive', message='Bar Statistics: open interest turned positive, positions building on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(open_interest_negative, title='Open Interest Turns Negative', message='Bar Statistics: open interest turned negative, positions unwinding on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(net_long_positive, title='Net Long Turns Positive', message='Bar Statistics: net long turned positive on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(net_long_negative, title='Net Long Turns Negative', message='Bar Statistics: net long turned negative on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(net_short_positive, title='Net Short Turns Positive', message='Bar Statistics: net short turned positive on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(net_short_negative, title='Net Short Turns Negative', message='Bar Statistics: net short turned negative on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(funding_rate_up, title='Funding Rate Rising', message='Bar Statistics: funding rate rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(funding_rate_down, title='Funding Rate Falling', message='Bar Statistics: funding rate fell on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(close_price_up, title='Close Price Rising', message='Bar Statistics: close rose on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(close_price_down, title='Close Price Falling', message='Bar Statistics: close fell on {{exchange}}:{{ticker}} - {{interval}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
