"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, barstate, bgcolor, box, close, color, high, input, label,
    line, low, math, na, plot, position, script, size, strategy, string, ta, table, text, volume
)
from pynecore.types import Color, Persistent, Series, Table

G_SMC: str = "Market Structure (MSS/BOS/CHoCH)"
G_OB_FVG: str = "Order Blocks & FVGs"
G_PD: str = "Premium & Discount Zones"
G_FILT: str = "Confirmation Filters"
G_RANK: str = "Signal Ranking & Volume"
G_RISK: str = "Risk Management"
G_STYLE: str = "Visual Settings & Colors"


@script.strategy("LuxAlgo SMC Pro Ultimate", overlay=True, margin_long=100, margin_short=100, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main(
    structureMode=input.string("All", "Structure Mode", options=("Internal", "Swing", "All"), group=G_SMC),
    internalLookback=input.int(9, "Internal Lookback", minval=2, group=G_SMC),
    swingLookback=input.int(50, "Swing Lookback", minval=2, group=G_SMC),
    tradeDirection=input.string("Both", "Trade Direction", options=("Both", "Long Only", "Short Only"), group=G_SMC),
    useFVGConfluence=input.bool(True, "Require FVG Presence", group=G_OB_FVG),
    showSMCZones=input.bool(True, "Visualize Trigger OB/FVG", group=G_OB_FVG),
    requirePDZone=input.bool(True, "Only Buy in Discount / Sell in Premium", group=G_PD),
    pdLookback=input.int(100, "PD Range Lookback", minval=10, group=G_PD),
    useDivFilter=input.bool(False, "Use Reversal Divergence Filter", group=G_FILT),
    useBBFilter=input.bool(False, "Use Bollinger Band Filter", group=G_FILT),
    volMult=input.float(1.2, "Volume Strength Multiplier", group=G_RANK),
    volCandles=input.int(3, "Volume Momentum Check", minval=1, group=G_RANK),
    tp1RR=input.float(1.5, "TP1 Risk:Reward", group=G_RISK),
    atrMult=input.float(3.0, "ATR Stop Multiplier", group=G_RISK),
    atrLen=input.int(9, "ATR Length", group=G_RISK),
    decayRate=input.int(2, "Signal Decay Speed", minval=1, maxval=10, group=G_RISK),
    labelSize=input.string(size.small, "Label Size", options=(size.tiny, size.small, size.normal, size.large, size.huge), group=G_STYLE),
    bullColor=input.color(color.new('#089981'), "Bullish Signals (Long)", group=G_STYLE, inline="C1"),
    bearColor=input.color(color.new('#F23645'), "Bearish Signals (Short)", group=G_STYLE, inline="C1"),
    slColor=input.color(color.new('#F23645'), "Stop Loss Line", group=G_STYLE, inline="C2"),
    tpColor=input.color(color.new('#089981'), "Take Profit Line", group=G_STYLE, inline="C2"),
    hudBgColor=input.color(color.new(color.new('#131722'), 10), "Dashboard Background", group=G_STYLE, inline="C3"),
    hudTextColor=input.color(color.white, "Dashboard Text", group=G_STYLE, inline="C3"),
    bgTransp=input.int(95, "Position BG Transparency", minval=0, maxval=100, group=G_STYLE, tooltip="Transparency for the bullish/bearish background highlight.")
):
    atr: float = ta.atr(atrLen)
    volAvg: float = ta.sma(volume, 20)
    rsi: Series[float] = ta.rsi(close, 14)
    ema200: float = ta.ema(close, 200)
    bbMid, _, _ = ta.bb(close, 20, 2.0)

    rangeHigh: float = ta.highest(high, pdLookback)
    rangeLow: float = ta.lowest(low, pdLookback)
    equilibrium: float = (rangeHigh + rangeLow) / 2
    inDiscount: bool = close < equilibrium
    inPremium: bool = close > equilibrium

    bFVG: Series[bool] = low > high[2] and close[1] > high[2]
    sFVG: Series[bool] = high < low[2] and close[1] < low[2]

    volIncreasing: bool = True
    if volCandles > 0:
        for i in pine_range(0, volCandles - 1):
            if volume[i] < volume[i + 1]:
                volIncreasing = False
                break

    iSH: bool = high[internalLookback] == ta.highest(high, internalLookback * 2 + 1)
    iSL: bool = low[internalLookback] == ta.lowest(low, internalLookback * 2 + 1)
    lastISH: Persistent[float] = na(float)
    lastISL: Persistent[float] = na(float)
    if iSH:
        lastISH = high[internalLookback]
    if iSL:
        lastISL = low[internalLookback]

    sSH: bool = high[swingLookback] == ta.highest(high, swingLookback * 2 + 1)
    sSL: bool = low[swingLookback] == ta.lowest(low, swingLookback * 2 + 1)
    lastSSH: Persistent[float] = na(float)
    lastSSL: Persistent[float] = na(float)
    if sSH:
        lastSSH = high[swingLookback]
    if sSL:
        lastSSL = low[swingLookback]

    xoI: bool = ta.crossover(close, lastISH)
    xuI: bool = ta.crossunder(close, lastISL)
    xoS: bool = ta.crossover(close, lastSSH)
    xuS: bool = ta.crossunder(close, lastSSL)

    mssL: bool = structureMode == 'Internal' and xoI or (structureMode == 'Swing' and xoS) or (structureMode == 'All' and (xoI or xoS))
    mssS: bool = structureMode == 'Internal' and xuI or (structureMode == 'Swing' and xuS) or (structureMode == 'All' and (xuI or xuS))

    bullDiv: bool = rsi > rsi[1] and low < low[1]
    bearDiv: bool = rsi < rsi[1] and high > high[1]

    bTrigger: bool = mssL and (not requirePDZone or inDiscount) and (not useFVGConfluence or bFVG[1] or bFVG) and (not useDivFilter or bullDiv) and (not useBBFilter or close > bbMid)
    sTrigger: bool = mssS and (not requirePDZone or inPremium) and (not useFVGConfluence or sFVG[1] or sFVG) and (not useDivFilter or bearDiv) and (not useBBFilter or close < bbMid)

    sl: Persistent[float] = na(float)
    tp1: Persistent[float] = na(float)
    tp1Hit: Persistent[bool] = False
    entryBar: Persistent[int] = 0
    isStrong: bool = volume > volAvg * volMult and volIncreasing

    if bTrigger and strategy.position_size == 0 and (tradeDirection == 'Both' or tradeDirection == 'Long Only'):
        sl = low - atr * atrMult
        tp1 = close + (close - sl) * tp1RR
        tp1Hit = False
        entryBar = bar_index
        msg: str = ('STRONG SMC BUY' if isStrong else 'SMC BUY') + '\n[MSS + DISCOUNT]'
        strategy.entry('Long', strategy.long, comment=msg)
        label.new(bar_index, low, msg + '\nSL: ' + string.tostring(sl, '#.##') + '\nTP1: ' + string.tostring(tp1, '#.##'), color=bullColor, textcolor=color.white, style=label.style_label_up, size=labelSize)
        if showSMCZones:
            box.new(bar_index - 2, high[2], bar_index, low, color.new(bullColor, 80), 1, line.style_dotted, bgcolor=color.new(bullColor, 80), text='Trigger Area', text_size=size.tiny, text_color=color.white)

    if sTrigger and strategy.position_size == 0 and (tradeDirection == 'Both' or tradeDirection == 'Short Only'):
        sl = high + atr * atrMult
        tp1 = close - (sl - close) * tp1RR
        tp1Hit = False
        entryBar = bar_index
        msg: str = ('STRONG SMC SELL' if isStrong else 'SMC SELL') + '\n[MSS + PREMIUM]'
        strategy.entry('Short', strategy.short, comment=msg)
        label.new(bar_index, high, msg + '\nSL: ' + string.tostring(sl, '#.##') + '\nTP1: ' + string.tostring(tp1, '#.##'), color=bearColor, textcolor=color.white, style=label.style_label_down, size=labelSize)
        if showSMCZones:
            box.new(bar_index - 2, low[2], bar_index, high, color.new(bearColor, 80), 1, line.style_dotted, bgcolor=color.new(bearColor, 80), text='Trigger Area', text_size=size.tiny, text_color=color.white)

    if strategy.position_size > 0:
        if not tp1Hit and high >= tp1:
            strategy.exit('TP1_L', 'Long', qty_percent=50, limit=tp1, comment='TP1 Hit')
            tp1Hit = True
            sl = strategy.position_avg_price
        trail: float = low - atr * atrMult
        if trail > sl:
            sl = trail
        strategy.exit('Exit_L', 'Long', stop=sl, comment='SL/Trail')

    if strategy.position_size < 0:
        if not tp1Hit and low <= tp1:
            strategy.exit('TP1_S', 'Short', qty_percent=50, limit=tp1, comment='TP1 Hit')
            tp1Hit = True
            sl = strategy.position_avg_price
        trail: float = high + atr * atrMult
        if trail < sl:
            sl = trail
        strategy.exit('Exit_S', 'Short', stop=sl, comment='SL/Trail')

    confScore: float = 0.0
    if strategy.position_size != 0:
        isLong: bool = strategy.position_size > 0
        tS: float = 30 if (close > ema200 if isLong else close < ema200) else 0
        mS: float = 30 if (rsi < 70 if isLong else rsi > 30) else 0
        vS: float = 20 if (close > bbMid if isLong else close < bbMid) else 0
        confScore = tS + mS + vS + math.max(0, 20 - (bar_index - entryBar) * decayRate)

    plot(sl if strategy.position_size != 0 else na, 'Stop Loss', slColor, 2, style=plot.style_linebr)
    plot(tp1 if strategy.position_size != 0 and (not tp1Hit) else na, 'TP Target', tpColor, 1, style=plot.style_linebr)
    bgcolor(color.new(bullColor, bgTransp) if strategy.position_size > 0 else color.new(bearColor, bgTransp) if strategy.position_size < 0 else na)

    HUD: Persistent[Table] = table.new(position.top_right, 2, 7, bgcolor=hudBgColor, border_width=1, border_color=hudTextColor)
    if barstate.islast:
        wR: float = strategy.wintrades / strategy.closedtrades * 100 if strategy.closedtrades > 0 else 0
        mC: Color = bullColor if confScore > 75 else color.orange if confScore > 40 else bearColor
        table.cell(HUD, 0, 0, 'SMC Pro HUD', text_color=hudTextColor, text_size=size.small)
        table.cell(HUD, 1, 0, structureMode, text_color=hudTextColor)
        table.cell(HUD, 0, 1, 'Win Rate', text_color=hudTextColor, text_halign=text.align_left)
        table.cell(HUD, 1, 1, string.tostring(wR, '#.##') + '%', text_color=bullColor if wR >= 50 else bearColor)
        table.cell(HUD, 0, 2, 'Net Profit', text_color=hudTextColor, text_halign=text.align_left)
        table.cell(HUD, 1, 2, string.tostring(strategy.netprofit, '#.##'), text_color=bullColor if strategy.netprofit >= 0 else bearColor)
        table.cell(HUD, 0, 3, 'PD Status', text_color=hudTextColor, text_halign=text.align_left)
        table.cell(HUD, 1, 3, 'DISCOUNT' if inDiscount else 'PREMIUM' if inPremium else 'EQ', text_color=bullColor if inDiscount else bearColor if inPremium else hudTextColor)
        table.cell(HUD, 0, 4, 'Position', text_color=hudTextColor, text_halign=text.align_left)
        table.cell(HUD, 1, 4, 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT', text_color=bullColor if strategy.position_size > 0 else bearColor if strategy.position_size < 0 else hudTextColor)
        table.cell(HUD, 0, 5, 'Confluence', text_color=hudTextColor, text_halign=text.align_left)
        table.cell(HUD, 1, 5, string.tostring(confScore, '#') + '%' if strategy.position_size != 0 else 'N/A', bgcolor=color.new(mC, 70) if strategy.position_size != 0 else na, text_color=color.white if strategy.position_size != 0 else hudTextColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
