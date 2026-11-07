"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, barstate, box, close, color, currency, display,
    fill, high, hlc3, input, label, line, low, math, na, plot, position, script, size, strategy,
    string, ta, table, time, timestamp, volume
)
from pynecore.types import Persistent, Series, Table

grp_bt: str = "Backtest Range"
grp_sw: str = "Swing Structure (Trigger)"
grp_dir: str = "Direction"
grp_ema: str = "EMA Filter (Structure)"
grp_chop: str = "Chop Filter"
grp_risk: str = "Risk Management"
grp_vis: str = "Visuals"


@script.strategy("Golden Trident | Swing-Anchored VWAP Trend System", shorttitle="GT_XAU", overlay=True, initial_capital=10000, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=20, commission_value=0.02, slippage=2, max_boxes_count=500, max_labels_count=500, max_lines_count=500, calc_on_every_tick=False)
def main(
    startTestTime=input.time(timestamp('2010-01-01 00:00'), "Backtest Start", group=grp_bt, tooltip="Restricts testing to a period with clean, liquid, consistently-quoted price and volume data."),
    endTestTime=input.time(timestamp('2026-12-31 23:59'), "Backtest End", group=grp_bt),
    swingLen=input.int(30, "Swing Period", minval=2, group=grp_sw, tooltip="Bars used to detect swing highs/lows. Larger values identify bigger, less frequent trend changes."),
    allowShort=input.bool(False, "Allow Short Entries?", group=grp_dir, tooltip="Off by default. The strategy is designed as long-only, stepping to the sidelines on bearish structure rather than shorting against gold's dominant long-term trend."),
    emaLen=input.int(200, "EMA Length", minval=1, group=grp_ema),
    useEMA=input.bool(True, "Require price beyond EMA?", group=grp_ema),
    useChop=input.bool(True, "Block entries during low volatility?", group=grp_chop, tooltip="Blocks new entries when recent range is too narrow relative to ATR, filtering out structure flips that occur during sideways consolidation."),
    atrChopLen=input.int(20, "ATR Length (Chop Filter)", minval=1, group=grp_chop),
    rangeMult=input.float(0.8, "Minimum Range x ATR", minval=0.1, step=0.1, group=grp_chop),
    atrStopLen=input.int(14, "ATR Length (Backstop)", minval=1, group=grp_risk),
    atrStopMult=input.float(8.0, "Backstop Distance (x ATR)", minval=1.0, step=0.5, group=grp_risk, tooltip="A wide catastrophe-only stop. The strategy is designed to exit on structure reversal well before this level is reached."),
    showTable=input.bool(True, "Show Dashboard", group=grp_vis),
    showBoxes=input.bool(True, "Show Trade Outcome Boxes", group=grp_vis),
    bullCol=input.color(color.new('#F5B942'), "Bullish Color", group=grp_vis),
    bearCol=input.color(color.new('#C0392B'), "Bearish Color", group=grp_vis)
):
    inBacktestRange = time >= startTestTime and time <= endTestTime

    b = bar_index
    ph: Persistent[float] = na(float)
    pl: Persistent[float] = na(float)
    phL: Persistent[int] = 0
    plL: Persistent[int] = 0

    ph = high if ta.highestbars(high, swingLen) == 0 else ph
    pl = low if ta.lowestbars(low, swingLen) == 0 else pl
    phL = b if ta.highestbars(high, swingLen) == 0 else phL
    plL = b if ta.lowestbars(low, swingLen) == 0 else plL

    dir: Series = 1 if phL > plL else -1

    cumPV: Persistent[float] = 0.0
    cumV: Persistent[float] = 0.0

    if dir != dir[1]:
        cumPV = hlc3 * volume
        cumV = volume
    else:
        cumPV = cumPV + hlc3 * volume
        cumV = cumV + volume

    anchoredVWAP = cumPV / cumV if cumV > 0 else hlc3

    emaTrend = ta.ema(close, emaLen)
    atrStop = ta.atr(atrStopLen)

    atrChop = ta.atr(atrChopLen)
    rangeOK = ta.highest(high, atrChopLen) - ta.lowest(low, atrChopLen) > atrChop * rangeMult if useChop else True

    trendLongOK = close > emaTrend if useEMA else True
    trendShortOK = close < emaTrend if useEMA else True

    longCond: Series = dir == 1 and trendLongOK and rangeOK and inBacktestRange
    shortCond: Series = allowShort and dir == -1 and trendShortOK and rangeOK and inBacktestRange

    longTrigger = longCond and (not longCond[1])
    shortTrigger = shortCond and (not shortCond[1])

    backstopLong: Persistent[float] = na(float)
    backstopShort: Persistent[float] = na(float)

    if longTrigger and strategy.position_size <= 0:
        backstopLong = close - atrStop * atrStopMult
        strategy.entry('Long', strategy.long, comment='XAU BUY')

    if shortTrigger and strategy.position_size >= 0:
        backstopShort = close + atrStop * atrStopMult
        strategy.entry('Short', strategy.short, comment='XAU SELL')

    if dir == -1 and strategy.position_size > 0:
        strategy.close('Long', comment='Structure Flip Exit')

    if dir == 1 and strategy.position_size < 0:
        strategy.close('Short', comment='Structure Flip Exit')

    if strategy.position_size > 0:
        strategy.exit('Long Backstop', 'Long', stop=backstopLong)

    if strategy.position_size < 0:
        strategy.exit('Short Backstop', 'Short', stop=backstopShort)

    tradeEntryPrice: Persistent[float] = na(float)
    tradeEntryBar: Persistent[int] = na(int)
    tradeDir: Persistent[str] = ""

    if strategy.position_size != 0 and strategy.position_size[1] == 0:
        tradeEntryPrice = close
        tradeEntryBar = bar_index
        tradeDir = 'long' if strategy.position_size > 0 else 'short'

    if strategy.position_size == 0 and strategy.position_size[1] != 0 and showBoxes:
        exitPrice = close
        exitBar = bar_index
        won = exitPrice > tradeEntryPrice if tradeDir == 'long' else exitPrice < tradeEntryPrice
        boxCol = bullCol if won else bearCol
        topP = math.max(tradeEntryPrice, exitPrice)
        botP = math.min(tradeEntryPrice, exitPrice)
        box.new(tradeEntryBar, topP, exitBar, botP, border_width=0, bgcolor=color.new(boxCol, 85))
        line.new(tradeEntryBar, topP, exitBar, topP, color=boxCol, width=1)
        line.new(tradeEntryBar, botP, exitBar, botP, color=boxCol, width=1)

    trendCol = bullCol if dir == 1 else bearCol

    pVWAP = plot(anchoredVWAP, 'Anchored VWAP', color=trendCol, linewidth=2)
    pClose = plot(close, display=display.none)
    fill(pVWAP, pClose, color=color.new(trendCol, 90), title='Trend Fill')

    plot(emaTrend if useEMA else na, 'EMA200', color=color.new(color.gray, 20), linewidth=1)

    if longTrigger and strategy.position_size[1] <= 0:
        label.new(bar_index, low, 'L', color=bullCol, textcolor=color.white, style=label.style_label_up, size=size.small)

    if shortTrigger and strategy.position_size[1] >= 0:
        label.new(bar_index, high, 'S', color=bearCol, textcolor=color.white, style=label.style_label_down, size=size.small)

    barcolor(bullCol if dir == 1 else bearCol)

    if showTable:
        dash: Persistent[Table] = table.new(position.top_right, 2, 5, frame_color=color.gray, frame_width=1, border_width=1, border_color=color.gray, bgcolor=color.new(color.new('#1A1A1A'), 10))
        if barstate.islast:
            table.cell(dash, 0, 0, 'GOLDEN TRIDENT', text_color=color.white, bgcolor=color.black)
            table.cell(dash, 1, 0, 'STATUS', text_color=color.white, bgcolor=color.black)

            table.cell(dash, 0, 1, 'Structure', bgcolor=color.gray, text_color=color.white)
            table.cell(dash, 1, 1, 'UPTREND' if dir == 1 else 'DOWNTREND', bgcolor=bullCol if dir == 1 else bearCol, text_color=color.white)

            table.cell(dash, 0, 2, 'Volatility', bgcolor=color.gray, text_color=color.white)
            table.cell(dash, 1, 2, 'ACTIVE' if rangeOK else 'CHOP', bgcolor=bullCol if rangeOK else color.new(color.gray, 40), text_color=color.white)

            table.cell(dash, 0, 3, 'Position Size', bgcolor=color.gray, text_color=color.white)
            table.cell(dash, 1, 3, string.tostring(strategy.position_size, '#.###'), bgcolor=color.new(color.new('#333333'), 0), text_color=color.white)

            pnlPct = ((close - strategy.position_avg_price) / strategy.position_avg_price * 100 if strategy.position_size > 0 else (strategy.position_avg_price - close) / strategy.position_avg_price * 100) if strategy.position_size != 0 else 0.0
            table.cell(dash, 0, 4, 'Open P/L', bgcolor=color.gray, text_color=color.white)
            table.cell(dash, 1, 4, string.tostring(pnlPct, '#.00') + '%' if strategy.position_size != 0 else '—', bgcolor=color.new(color.gray, 40) if strategy.position_size == 0 else bullCol if pnlPct > 0 else bearCol, text_color=color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
