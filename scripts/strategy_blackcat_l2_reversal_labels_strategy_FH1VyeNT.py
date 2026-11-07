"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, bar_index, barstate, bgcolor, close, color, display, high, input,
    label, low, na, plot, position, script, size, strategy, string, ta, table, yloc
)
from pynecore.types import Color, Persistent, Series, Table

GRP_SIG: str = 'Signal'
GRP_GOV: str = 'Signal Governance'
GRP_RSK: str = 'Risk'
GRP_VIS: str = 'Visual'


@script.strategy('[blackcat] L2 Reversal Labels Strategy V2', overlay=True, max_bars_back=5000, max_labels_count=500, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.1, slippage=2, margin_long=0, margin_short=0, default_qty_type=strategy.percent_of_equity, default_qty_value=95, process_orders_on_close=True)
def main(
    fastLen=input.int(12, 'MACD Fast Length', minval=1, group=GRP_SIG),
    slowLen=input.int(26, 'MACD Slow Length', minval=1, group=GRP_SIG),
    sigLen=input.int(9, 'MACD Signal Length', minval=1, group=GRP_SIG),
    enableShort=input.bool(True, 'Enable Short Signals', group=GRP_SIG),
    useExclusivity=input.bool(True, 'Same-bar Entry/Exit Exclusivity', group=GRP_GOV),
    cooldownBars=input.int(3, 'Cooldown Bars (0 = off)', minval=0, group=GRP_GOV),
    atrLen=input.int(14, 'ATR Length', minval=1, group=GRP_RSK),
    useTPSL=input.bool(True, 'Enable ATR Take Profit / Stop Loss', group=GRP_RSK),
    slMult=input.float(2.0, 'Stop Loss (xATR)', minval=0.5, step=0.25, group=GRP_RSK),
    tpMult=input.float(3.0, 'Take Profit (xATR)', minval=0.5, step=0.25, group=GRP_RSK),
    showBg=input.bool(True, 'Position Background', group=GRP_VIS),
    showDash=input.bool(True, 'Show Dashboard', group=GRP_VIS)
):
    diff: Series
    diff, dea, macdLine = ta.macd(close, fastLen, slowLen, sigLen)
    a1 = ta.barssince(inline_series(ta.crossover(diff, dea), 1))
    a2 = ta.barssince(inline_series(ta.crossunder(diff, dea), 1))
    diffXUp = ta.crossover(diff, dea)
    diffXDn = ta.crossunder(diff, dea)
    bottom_zone = not na(a1) and close[a1 + 1] > close and (diff > diff[a1 + 1]) and diffXUp
    top_zone = not na(a2) and close[a2 + 1] < close and (diff[a2 + 1] > diff) and diffXDn
    atrVal = ta.atr(atrLen)

    posState: Persistent[int] = 0
    lastSignalBar: Persistent[int] = na(int)
    cooldownOK = na(lastSignalBar) or bar_index - lastSignalBar > cooldownBars
    rawLongEntry = bottom_zone and posState <= 0 and cooldownOK
    rawShortEntry = top_zone and posState >= 0 and cooldownOK and enableShort
    longEntry = rawLongEntry and (not rawShortEntry)
    shortEntry = rawShortEntry and (not rawLongEntry)
    if longEntry:
        posState = 1
        lastSignalBar = bar_index
    elif shortEntry:
        posState = -1
        lastSignalBar = bar_index

    if longEntry:
        label.new(bar_index, low, 'Near Bottom', color=color.new(color.green, 50), textcolor=color.white, style=label.style_label_up, yloc=yloc.price, size=size.small)
    if shortEntry:
        label.new(bar_index, high, 'Near Top', color=color.new(color.red, 50), textcolor=color.white, style=label.style_label_down, yloc=yloc.price, size=size.small)

    if longEntry:
        alert('Bottom Reversal Soon! Long entry @ ' + string.tostring(close), alert.freq_once_per_bar_close)
    elif shortEntry:
        alert('Top Reversal Soon! Short entry @ ' + string.tostring(close), alert.freq_once_per_bar_close)

    if longEntry:
        strategy.entry('long', strategy.long)
    if shortEntry:
        strategy.entry('short', strategy.short)
    avgPrice = strategy.position_avg_price
    longStop = avgPrice - slMult * atrVal if useTPSL else na
    longLimit = avgPrice + tpMult * atrVal if useTPSL else na
    shortStop = avgPrice + slMult * atrVal if useTPSL else na
    shortLimit = avgPrice - tpMult * atrVal if useTPSL else na
    if strategy.position_size > 0:
        strategy.exit('LX', from_entry='long', stop=longStop, limit=longLimit)
    if strategy.position_size < 0:
        strategy.exit('SX', from_entry='short', stop=shortStop, limit=shortLimit)

    C_BGLONG: Color = color.new(color.green, 95)
    C_BGSHORT: Color = color.new(color.red, 95)
    bgLong = showBg and posState > 0
    bgShort = showBg and posState < 0
    bgcolor(C_BGLONG if bgLong else C_BGSHORT if bgShort else na)
    plot(diff, 'MACD Diff', color=color.blue, display=display.data_window)
    plot(dea, 'MACD DEA', color=color.orange, display=display.data_window)
    plot(posState, 'Position State', display=display.data_window)
    dash: Persistent[Table] = table.new(position.top_right, 2, 4, bgcolor=color.new(color.black, 60), border_width=1)
    if showDash and barstate.islast:
        table.cell(dash, 0, 0, 'Position', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 0, 'LONG' if posState > 0 else 'SHORT' if posState < 0 else 'FLAT', text_color=color.green if posState > 0 else color.red if posState < 0 else color.white, text_size=size.tiny)
        table.cell(dash, 0, 1, 'Last Signal', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 1, '-' if na(lastSignalBar) else string.tostring(bar_index - lastSignalBar) + ' bars ago', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 2, 'Cooldown', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 2, 'Ready' if cooldownOK else string.tostring(cooldownBars - (bar_index - lastSignalBar)) + ' left', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 0, 3, 'TP / SL', text_color=color.white, text_size=size.tiny)
        table.cell(dash, 1, 3, string.tostring(tpMult * atrVal, '#.##') + ' / ' + string.tostring(slMult * atrVal, '#.##') + ' (xATR)' if useTPSL and strategy.position_size != 0 else '-', text_color=color.white, text_size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
