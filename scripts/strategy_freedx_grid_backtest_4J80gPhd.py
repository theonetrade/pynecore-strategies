"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.lib import (
    array, close, color, font, input, label, last_bar_time, line, math, na,
    position, script, size, strategy, string, syminfo, table, text, time, timeframe, timestamp,
    xloc
)
from pynecore.types import NA, Persistent, Table


@script.strategy('FreedX Grid Backtest', shorttitle='FreedX Grid Backtest', overlay=True, calc_on_order_fills=False, commission_value=0.04, initial_capital=10000, default_qty_value=100, default_qty_type=strategy.percent_of_equity, slippage=10, use_bar_magnifier=False, fill_orders_on_standard_ohlc=True, pyramiding=1000, max_lines_count=500, max_labels_count=500, close_entries_rule='ANY', margin_long=0, margin_short=0, close_by_id=True)
def main(
    activate_ranges=input.bool(title='📅 Backtest Range', defval=False),
    __input_1__=input.time(timestamp('1 Jan 2024'), title='      ‣   From'),
    __input_2__=input.time(timestamp('04 Feb 2024'), title='      ‣   To'),
    investment=input.float(title='💰 Investment', defval=10000, minval=1, group='Investment Settings', tooltip='📜 The amount of money you want to invest in dollars.'),
    leverage=input.int(title='⏫ Leverage', defval=1, minval=1, group='Investment Settings', tooltip='📜 Multiplies your investment amount using leverage. This feature is for the futures market.'),
    order_size=input.string(title='🔄 Method', defval='Auto', options=('Auto', 'Compound', '📑 Fixed'), group='Investment Settings', tooltip='📜 Auto: Select the closest integer quantity for parities.\n\n📜 Compound: Turns on the compounding effect for grid quantities. If the trade is profitable, it uses more quantity in the next trades. If the trade is not profitable, it uses less quantity for the next trades.\n\n📜 Fixed: The quantity will be determined in the section below, named "Fixed Contracts." All grid levels will use this size for orders.'),
    fix_cl_per_level=input.float(title='📑 Fixed Contracts', defval=1, minval=0, group='Investment Settings', tooltip='📜 The method should be fixed!\n\n📜 0 = Auto.\n\n📜 Exchanges have minimum required contract limits for grid levels. They are assigned automatically according to the investment and levels. Users can manually input that contract size for testing.'),
    gridLevels=input.int(title='📌 Number Of Grids', defval=10, minval=2, group='Grid Settings', tooltip='📜 Sets the number of grid levels. It divides the investment across these grid levels. Each grid level will have the same order quantity.'),
    distributionType=input.string(title='📐 Distribution Type', defval='Arithmetic', options=('Arithmetic', 'Geometric'), group='Grid Settings', tooltip='📜 Changes how grid levels are determined. Levels can be set using either arithmetic or geometric methods.'),
    mode=input.string(title='⚙️ Mode', defval='Neutral', options=('Neutral', 'Long', 'Short'), group='Grid Settings', tooltip='📜 Neutral: Uses both Long and Short orders.\n\n📈 Long: Uses only Long orders.\n\n📉 Short: Uses only Short orders.'),
    entry_condition=input.string(title='➡️ Condition', defval='Crossing', options=('Crossing', 'Pullback'), group='Grid Settings', tooltip='📜 Pullback: No initial positions when a bot starts. Levels must be reached by a pullback to open new positions.\n\n📜 When the bot starts, levels that have already been crossed will open positions at the start of the bot, thus giving the bot initial positions. After new levels are reached, positions will be added or removed according to the behavior of the reached levels.'),
    grid_calculation=input.string(title='📏 Target Method', defval='Exchange', options=('Exchange', 'Increased Average Tp'), group='Grid Settings', tooltip='📜 Exchange: Sets take-profit targets based on exchange behavior.\n\n📜 Increased Average Take-profit Targets: Uses the average of the next two levels as a profit target.\n\n📜 Info: If "Recalculate: After order is filled" is enabled in the properties, the grid calculates more accurately on higher timeframes.'),
    enable_levels=input.bool(title='📊 Manual Levels', defval=False, group='Level Settings', tooltip='📜 Turns off auto mode. You must set your own levels to define the grid range. Think of the reference as the price at which you start grid trading.'),
    topLevel_raw__input=input.price(title='      ‣   📈 Top Range', defval=44000, group='Level Settings', tooltip='📜 The top range of the grid area.\n\n✏️ Users can adjust the levels directly on the chart by clicking and dragging. To do this, click and hold the level while the crosshair is positioned in the middle of the chart.'),
    referencePrice__input=input.price(title='      ‣   ↔️ Reference', defval=41500, group='Level Settings', tooltip='📜 The middle range of the grid area.\n\n✏️ Users can adjust the levels directly on the chart by clicking and dragging. To do this, click and hold the level while the crosshair is positioned in the middle of the chart.'),
    bottomLevel_raw__input=input.price(title='      ‣   📉 Bottom Range', defval=39000, group='Level Settings', tooltip='📜 The bottom range of the grid area.\n\n✏️ Users can adjust the levels directly on the chart by clicking and dragging. To do this, click and hold the level while the crosshair is positioned in the middle of the chart.'),
    enable_tp_sl=input.bool(title='⭕ Stop Triggers', defval=False, group='Stopper Settings', tooltip='📜 Enables stop triggers, which can stop the trading process when certain limits are reached.'),
    stop_mode=input.string(title='      ‣   Behavior', defval='Close All', options=('Close All', 'Terminate'), group='Stopper Settings', tooltip='📜 Close All: This mode closes all trades if a stop trigger is hit. If the price enters the grid range again, trading will continue.\n\n📜 Terminate: Closes all positions when a stop trigger price is hit, and no more trades will open in terminate mode.'),
    upperLimit=input.price(title='      ‣   Upper Limit', defval=50000, group='Stopper Settings', tooltip='📜 The upper limit for the stop trigger.\n\n✏️ Users can adjust the levels directly on the chart by clicking and dragging. To do this, click and hold the level while the crosshair is positioned in the middle of the chart.'),
    lowerLimit=input.price(title='      ‣   Lower Limit', defval=32000, group='Stopper Settings', tooltip='📜 The lower limit for the stop trigger.\n\n✏️ Users can adjust the levels directly on the chart by clicking and dragging. To do this, click and hold the level while the crosshair is positioned in the middle of the chart.')
):
    start: int = 0
    finish: int = 0
    if activate_ranges:
        start = __input_1__
        finish = __input_2__
    else:
        sec_to_milisec: int = 1000
        auto_test_last_bar_count: int = 100
        start = last_bar_time - timeframe.in_seconds(timeframe.period) * sec_to_milisec * auto_test_last_bar_count
        finish = last_bar_time + timeframe.in_seconds(timeframe.period) * sec_to_milisec
    def window():
        return True if time >= start and time <= finish else False

    def truncate_to_symbol_decimals(value):
        decimals = math.ceil(-math.log10(syminfo.mintick))
        multiplier = math.pow(10, decimals)
        truncatedValue = math.floor(value * multiplier) / multiplier
        return truncatedValue

    def symbol_min_move():
        min_move_decimals = math.ceil(-math.log10(syminfo.mintick))
        return min_move_decimals

    def symbol_decimal_str(number):
        result: str = ''
        for i in pine_range(0, number - 1, 1):
            result = result + '0'
        return result

    topLevel_raw: Persistent = topLevel_raw__input
    referencePrice: Persistent = referencePrice__input
    bottomLevel_raw: Persistent = bottomLevel_raw__input
    if not enable_levels and time >= start and (time[1] < start):
        referencePrice = close
        topLevel_raw = referencePrice * 1.2
        bottomLevel_raw = referencePrice * 0.8
    mode = 'Long' if topLevel_raw < referencePrice else mode
    mode = 'Short' if bottomLevel_raw > referencePrice else mode
    topLevel = referencePrice if mode == 'Long' else topLevel_raw
    bottomLevel = referencePrice if mode == 'Short' else bottomLevel_raw
    def closeAllPositions():
        if strategy.position_size > 0:
            strategy.cancel_all()
            strategy.close_all(comment=stop_mode + '-Long Stop', immediately=True)
        __block_result__ = na
        if strategy.position_size < 0:
            strategy.cancel_all()
            __block_result__ = strategy.close_all(comment=stop_mode + '-Short Stop', immediately=True)
        return __block_result__

    one_time_trigger: Persistent[bool] = False
    def priceHitsLimits():
        hit = False if one_time_trigger == False else True
        window_1 = window()
        if (close >= upperLimit or close <= lowerLimit) and enable_tp_sl and window_1:
            strategy.cancel_all()
            closeAllPositions()
            hit = True
        return hit

    priceHitsLimits_1 = priceHitsLimits()
    if stop_mode == 'Terminate' and priceHitsLimits_1 and (one_time_trigger == False):
        one_time_trigger = True
    def calcGridLevels(top, bottom, ref, gridCount, distributionType):
        levels: list[float] = array.new_float()
        count = gridCount + (2 if mode == 'Neutral' else 1)
        if distributionType == 'Arithmetic':
            aboveRefRatio = (top - ref) / (top - bottom)
            belowRefRatio = 1 - aboveRefRatio
            aboveCount = math.ceil(count * aboveRefRatio)
            belowCount = count - aboveCount
            aboveStep = (top - ref) / (aboveCount - 1)
            belowStep = (ref - bottom) / (belowCount - 1)
            for i in pine_range(0, belowCount - 1, 1):
                level = ref - belowStep * i
                array.push(levels, level)
            for i in pine_range(1, aboveCount - 1, 1):
                level = ref + aboveStep * i
                array.push(levels, level)
        elif distributionType == 'Geometric':
            aboveRefRatio = (top - ref) / (top - bottom)
            belowRefRatio = 1 - aboveRefRatio
            aboveCount = math.ceil(count * aboveRefRatio)
            belowCount = count - aboveCount
            aboveRatio = math.pow(top / ref, 1 / (aboveCount - 1))
            belowRatio = math.pow(ref / bottom, 1 / (belowCount - 1))
            for i in pine_range(0, belowCount - 1, 1):
                level = ref * math.pow(belowRatio, -i)
                array.push(levels, level)
            for i in pine_range(1, aboveCount - 1, 1):
                level = ref * math.pow(aboveRatio, i)
                array.push(levels, level)
        return levels

    startBarTime: Persistent[int] = na(int)
    finishBarTime: Persistent[int] = finish
    gridLevelsArray: Persistent[list[float]] = array.new_float()
    longLevelsArray: Persistent[list[float]] = array.new_float()
    shortLevelsArray: Persistent[list[float]] = array.new_float()
    first_qty: Persistent = cast_float(0)
    is_first_grid_calculation_completed: Persistent[bool] = False
    if time >= start and time[1] < start:
        startBarTime = time
        first_qty = investment * leverage / close
    window_1 = window()
    if is_first_grid_calculation_completed == False and window_1:
        gridLevelsArray = calcGridLevels(topLevel, bottomLevel, referencePrice, gridLevels, distributionType)
        for i in pine_range(0, array.size(gridLevelsArray) - 1, 1):
            level = array.get(gridLevelsArray, i)
            if mode == 'Neutral' or mode == 'Long':
                if level < referencePrice:
                    array.push(longLevelsArray, level)
            if mode == 'Neutral' or mode == 'Short':
                if level > referencePrice:
                    array.push(shortLevelsArray, level)
        is_first_grid_calculation_completed = True
    def levelHasOpenTrade(level_comment):
        hasTrade: bool = False
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.opentrades - 1):
            tradeId = __loop_0__.value
            if strategy.opentrades.entry_comment(tradeId) == level_comment:
                hasTrade = True
                break
        return hasTrade

    priceHitsLimits_2 = priceHitsLimits()
    if window() and (not priceHitsLimits_2):
        exchange_style = grid_calculation == 'Exchange'
        quote_qty = strategy.equity if order_size == 'Compound' else investment
        grid_count = array.size(longLevelsArray) if mode == 'Long' else array.size(shortLevelsArray) if mode == 'Short' else array.size(longLevelsArray) + array.size(shortLevelsArray)
        quote_per_grid = quote_qty / grid_count
        qty = quote_per_grid / close * leverage
        qty = (cast_int(first_qty / grid_count) if first_qty / grid_count > 1 else first_qty / grid_count) if order_size == 'Auto' else qty
        qty = fix_cl_per_level if fix_cl_per_level != 0 and order_size == '📑 Fixed' else qty
        if mode == 'Neutral' or mode == 'Long':
            for i in pine_range(0, array.size(longLevelsArray) - 1, 1):
                level = truncate_to_symbol_decimals(array.get(longLevelsArray, i))
                level_str = string.tostring(level)
                entry_level_comment = 'Long @' + string.tostring(i + 1)
                exit_level_comment = 'TP @' + string.tostring(i + 1)
                condition = close > level if entry_condition == 'Pullback' else True
                levelHasOpenTrade_1 = levelHasOpenTrade(entry_level_comment)
                if condition and (not levelHasOpenTrade_1):
                    tp_level = NA(float)
                    if i > 1:
                        nextLevel = array.get(longLevelsArray, i - 1)
                        nextNextLevel = array.get(longLevelsArray, i - 2)
                        tp_level = nextLevel if exchange_style else (nextLevel + nextNextLevel) / 2
                    elif i == 1:
                        highestLongLevel = array.get(longLevelsArray, i - 1)
                        tp_level = highestLongLevel if exchange_style else (highestLongLevel + referencePrice) / 2
                    elif i == 0 and mode == 'Neutral':
                        tp_level = referencePrice if exchange_style else (referencePrice + array.get(shortLevelsArray, 0)) / 2
                    elif i == 0 and mode == 'Long':
                        highestLongLevel = array.get(longLevelsArray, i)
                        last_dff = referencePrice - (highestLongLevel + referencePrice) / 2
                        tp_level = referencePrice if exchange_style else referencePrice + last_dff
                    if not na(tp_level):
                        strategy.entry(id='Buy@' + level_str, direction=strategy.long, qty=qty, comment=entry_level_comment, limit=level)
                        strategy.exit(id='TP@' + level_str, from_entry='Buy@' + level_str, comment=exit_level_comment, limit=tp_level)
        if mode == 'Neutral' or mode == 'Short':
            for i in pine_range(0, array.size(shortLevelsArray) - 1, 1):
                level = truncate_to_symbol_decimals(array.get(shortLevelsArray, i))
                level_str = string.tostring(level)
                entry_level_comment = 'Short @' + string.tostring(i + 1)
                exit_level_comment = 'TP @' + string.tostring(i + 1)
                condition = close < level if entry_condition == 'Pullback' else True
                levelHasOpenTrade_1 = levelHasOpenTrade(entry_level_comment)
                if condition and (not levelHasOpenTrade_1):
                    tp_level = NA(float)
                    if i > 1:
                        prevLevel = array.get(shortLevelsArray, i - 1)
                        prevPrevLevel = array.get(shortLevelsArray, i - 2)
                        tp_level = prevLevel if exchange_style else (prevLevel + prevPrevLevel) / 2
                    elif i == 1:
                        lowestShortLevel = array.get(shortLevelsArray, i - 1)
                        tp_level = lowestShortLevel if exchange_style else (lowestShortLevel + referencePrice) / 2
                    elif i == 0 and mode == 'Neutral':
                        tp_level = referencePrice if exchange_style else (referencePrice + array.get(longLevelsArray, 0)) / 2
                    elif i == 0 and mode == 'Short':
                        lowestShortLevel = array.get(shortLevelsArray, i)
                        last_dff = (lowestShortLevel + referencePrice) / 2 - referencePrice
                        tp_level = referencePrice if exchange_style else referencePrice - last_dff
                    if not na(tp_level):
                        strategy.entry(id='Sell@' + level_str, direction=strategy.short, qty=qty, comment=entry_level_comment, limit=level)
                        strategy.exit(id='TP@' + level_str, from_entry='Sell@' + level_str, comment=exit_level_comment, limit=tp_level)
    else:
        if not window():
            strategy.cancel_all()
            strategy.close_all(comment='Closed All - End Of Backtest', immediately=True)
    bar_before_last = last_bar_time - timeframe.in_seconds(timeframe.period) * 1000
    if time == bar_before_last:
        if mode == 'Neutral' or mode == 'Long':
            for i in pine_range(0, array.size(longLevelsArray) - 1, 1):
                style_decision = line.style_solid if i == array.size(longLevelsArray) - 1 else line.style_dotted
                level = truncate_to_symbol_decimals(array.get(longLevelsArray, i))
                decimals_to_show = '0.' + symbol_decimal_str(symbol_min_move())
                line.new(x1=startBarTime, y1=level, x2=finishBarTime, y2=level, xloc=xloc.bar_time, width=1, color=color.blue, style=style_decision)
                label.new(x=startBarTime, y=level, xloc=xloc.bar_time, text=string.tostring(i + 1, '#.##'), style=label.style_label_center, color=color.blue, size=size.small, textcolor=color.white)
                label.new(x=finishBarTime, y=level, xloc=xloc.bar_time, text=string.tostring(level, decimals_to_show), style=label.style_label_center, color=color.blue, size=size.small, textcolor=color.white)
                if mode == 'Long' and i == 0 and (grid_calculation != 'Exchange'):
                    new_trigger_line = (3 * referencePrice - level) / 2
                    line.new(x1=startBarTime, y1=new_trigger_line, x2=finishBarTime, y2=new_trigger_line, xloc=xloc.bar_time, width=1, color=color.rgb(255, 153, 0), style=style_decision)
                    label.new(x=startBarTime, y=new_trigger_line, xloc=xloc.bar_time, text=string.tostring(i, '#.##'), style=label.style_label_center, color=color.rgb(255, 153, 0, 77), size=size.tiny, textcolor=color.white)
                    label.new(x=finishBarTime, y=new_trigger_line, xloc=xloc.bar_time, text=string.tostring(new_trigger_line, decimals_to_show), style=label.style_label_center, color=color.rgb(255, 153, 0, 77), size=size.tiny, textcolor=color.white)
        if mode == 'Neutral' or mode == 'Short':
            for i in pine_range(0, array.size(shortLevelsArray) - 1, 1):
                style_decision = line.style_solid if i == array.size(shortLevelsArray) - 1 else line.style_dotted
                level = truncate_to_symbol_decimals(array.get(shortLevelsArray, i))
                decimals_to_show = '0.' + symbol_decimal_str(symbol_min_move())
                line.new(x1=startBarTime, y1=level, x2=finishBarTime, y2=level, xloc=xloc.bar_time, width=1, color=color.red, style=style_decision)
                label.new(x=finishBarTime, y=level, xloc=xloc.bar_time, text=string.tostring(level, decimals_to_show), style=label.style_label_center, color=color.red, size=size.small, textcolor=color.white)
                label.new(x=startBarTime, y=level, xloc=xloc.bar_time, text=string.tostring(i + 1, '#.##'), style=label.style_label_center, color=color.red, size=size.small, textcolor=color.white)
                if mode == 'Short' and i == 0 and (grid_calculation != 'Exchange'):
                    new_trigger_line = (3 * referencePrice - level) / 2
                    line.new(x1=startBarTime, y1=new_trigger_line, x2=finishBarTime, y2=new_trigger_line, xloc=xloc.bar_time, width=1, color=color.rgb(255, 153, 0), style=style_decision)
                    label.new(x=finishBarTime, y=new_trigger_line, xloc=xloc.bar_time, text=string.tostring(new_trigger_line, decimals_to_show), style=label.style_label_center, color=color.rgb(255, 153, 0, 77), size=size.tiny, textcolor=color.white)
                    label.new(x=startBarTime, y=new_trigger_line, xloc=xloc.bar_time, text=string.tostring(i, '#.##'), style=label.style_label_center, color=color.rgb(255, 153, 0, 77), size=size.tiny, textcolor=color.white)
        line.new(x1=startBarTime, y1=referencePrice, x2=finishBarTime, y2=referencePrice, xloc=xloc.bar_time, width=2, color=color.white)
        label.new(x=finishBarTime, y=referencePrice, xloc=xloc.bar_time, text='Reference', style=label.style_label_center, color=color.white, textcolor=color.rgb(0, 0, 0), size=size.tiny)
        label.new(x=startBarTime, y=referencePrice, xloc=xloc.bar_time, text='Reference', style=label.style_label_center, color=color.white, textcolor=color.rgb(0, 0, 0), size=size.tiny)
        if enable_tp_sl:
            if mode == 'Neutral':
                line.new(x1=startBarTime, y1=upperLimit, x2=finishBarTime, y2=upperLimit, xloc=xloc.bar_time, width=3, color=color.rgb(255, 72, 0, 44), style=line.style_solid)
                line.new(x1=startBarTime, y1=lowerLimit, x2=finishBarTime, y2=lowerLimit, xloc=xloc.bar_time, width=3, color=color.rgb(255, 72, 0, 44), style=line.style_solid)
                label.new(x=finishBarTime, y=upperLimit, xloc=xloc.bar_time, text='Stop-Loss Price', style=label.style_label_left, color=color.rgb(255, 72, 0, 44), textcolor=color.white, size=size.small)
                label.new(x=finishBarTime, y=lowerLimit, xloc=xloc.bar_time, text='Stop-Loss Price', style=label.style_label_left, color=color.rgb(255, 72, 0, 44), textcolor=color.white, size=size.small)
            elif mode == 'Long':
                line.new(x1=startBarTime, y1=upperLimit, x2=finishBarTime, y2=upperLimit, xloc=xloc.bar_time, width=2, color=color.lime, style=line.style_solid)
                line.new(x1=startBarTime, y1=lowerLimit, x2=finishBarTime, y2=lowerLimit, xloc=xloc.bar_time, width=2, color=color.red, style=line.style_solid)
                label.new(x=finishBarTime, y=upperLimit, xloc=xloc.bar_time, text='Take-Profit Price', style=label.style_label_left, color=color.lime, textcolor=color.black, size=size.small)
                label.new(x=finishBarTime, y=lowerLimit, xloc=xloc.bar_time, text='Stop-Loss Price', style=label.style_label_left, color=color.red, textcolor=color.white, size=size.small)
            elif mode == 'Short':
                line.new(x1=startBarTime, y1=upperLimit, x2=finishBarTime, y2=upperLimit, xloc=xloc.bar_time, width=2, color=color.red, style=line.style_solid)
                line.new(x1=startBarTime, y1=lowerLimit, x2=finishBarTime, y2=lowerLimit, xloc=xloc.bar_time, width=2, color=color.lime, style=line.style_solid)
                label.new(x=finishBarTime, y=upperLimit, xloc=xloc.bar_time, text='Stop-Loss Price', style=label.style_label_left, color=color.red, textcolor=color.white, size=size.small)
                label.new(x=finishBarTime, y=lowerLimit, xloc=xloc.bar_time, text='Take-Profit Price', style=label.style_label_left, color=color.lime, textcolor=color.black, size=size.small)
    report_table: Persistent[Table] = na(Table)
    level_count = array.size(longLevelsArray) if mode == 'Long' else array.size(shortLevelsArray) if mode == 'Short' else array.size(longLevelsArray) + array.size(shortLevelsArray)
    qty_failed = first_qty / level_count < 0.002 and order_size == 'Auto'
    order_failed = strategy.opentrades == 0 and strategy.closedtrades == 0 and (first_qty / level_count < 1)
    if strategy.initial_capital != investment or qty_failed or order_failed:
        text1: str = '-----------------------------------------------------\n\n'
        text2 = '' if strategy.initial_capital == investment else '⛔️ Investment is not equal to initial capital.\n\n'
        text3 = '' if strategy.initial_capital == investment else '⛔️ Max Drawdown calculation will be wrong.\n\n'
        text4 = '' if strategy.initial_capital == investment else '⛔️ Settings ▶ Properties ▶ (Initial Capital = ' + string.tostring(investment) + '✅)\n\n'
        text5 = '' if not qty_failed else '⛔️ Investment is not enough for starting grid bot.\n\n'
        text6 = '' if not order_failed else '⛔️ Order quantity is too small for that symbol.\n\n'
        text7 = '' if not order_failed else '⛔️ Increase capital. ( Quantity = ' + string.tostring(math.round(first_qty / level_count, 5)) + ' ) < 1 \n\n'
        text8: str = '-----------------------------------------------------'
        texts = text1 + text2 + text3 + text4 + text5 + text6 + text7 + text8
        report_table = table.new(position=position.bottom_right, columns=1, rows=1, border_width=1, border_color=color.white, bgcolor=color.new(color.purple, 90))
        table.cell(table_id=report_table, column=0, row=0, text=texts, bgcolor=color.rgb(155, 39, 176, 83), text_color=color.white, text_size=size.normal, text_halign=text.align_left, text_font_family=font.family_monospace)
    elif not na(report_table):
        table.delete(report_table)
        report_table = na


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
