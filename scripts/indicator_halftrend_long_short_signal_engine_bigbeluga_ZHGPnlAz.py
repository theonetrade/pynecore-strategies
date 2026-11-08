"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, chart, close, color, fill, high, input, label,
    location, low, math, na, nz, plot, plotshape, position, request, script, shape, size, string,
    ta, table, text, timeframe
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Table

grp_ht: str = "HalfTrend Settings"
grp_risk: str = "Risk Management"
grp_dash: str = "Multi-Asset Scanner"
grp_style: str = "Style & Colors"


@script.indicator("HalfTrend Long/Short Signal Engine [BigBeluga]", overlay=True, max_labels_count=500)
def main(
    amplitude=input.int(20, "Amplitude", minval=1, group=grp_ht, tooltip="Determines the lookback period for highest highs and lowest lows used in the trend calculation."),
    channelDeviation=input.float(2.0, "Channel Deviation", minval=0.1, step=0.1, group=grp_ht, tooltip="Multiplier for the Average True Range (ATR) to establish the upper and lower channel bands."),
    baseRiskMult=input.float(3, "Base Risk", step=0.1, group=grp_risk, tooltip="Sets SL distance from HalfTrend line, and TP1 distance from entry. TP2 is 2x, TP3 is 3x."),
    sym1=input.symbol("BINANCE:BTCUSD", "Symbol 1", group=grp_dash, tooltip="First symbol tracked in the multi-asset dashboard."),
    sym2=input.symbol("BINANCE:ETHUSD", "Symbol 2", group=grp_dash, tooltip="Second symbol tracked in the multi-asset dashboard."),
    sym3=input.symbol("BINANCE:SOLUSD", "Symbol 3", group=grp_dash, tooltip="Third symbol tracked in the multi-asset dashboard."),
    sym4=input.symbol("OANDA:EURUSD", "Symbol 4", group=grp_dash, tooltip="Fourth symbol tracked in the multi-asset dashboard."),
    sym5=input.symbol("OANDA:XAUUSD", "Symbol 5", group=grp_dash, tooltip="Fifth symbol tracked in the multi-asset dashboard."),
    channelDeviationUp=input.int(70, "Channel Deviation Transparency", group=grp_style, minval=0, maxval=100),
    colorBull=input.color(color.lime, "Bullish", inline="trend", group=grp_style, tooltip=""),
    colorBear=input.color(color.red, "Bearish", inline="trend", group=grp_style, tooltip="Primary color for bullish trends, target lines, and dashboard highlights.\nPrimary color for bearish trends and channel bands."),
    colorEntry=input.color(color.white, "Entry", inline="trade", group=grp_style, tooltip=""),
    colorTP=input.color(color.teal, "Take Profit", inline="trade", group=grp_style, tooltip=""),
    colorSL=input.color(color.red, "Stop Loss", inline="trade", group=grp_style, tooltip="Color used to mark the active trade entry price.\nColor used for the Take Profit target lines.\nColor used for stop loss lines and short trade text."),
    colorFillTP=input.color(color.new(color.teal, 80), "TP Fill", inline="fills", group=grp_style, tooltip=""),
    colorFillSL=input.color(color.new(color.red, 60), "SL Fill", inline="fills", group=grp_style, tooltip="Base color for the Take Profit zone gradient fills.\nBase color for the Stop Loss zone gradient fills."),
    colorText=input.color(color.white, "Text Color", group=grp_style, tooltip="Base color for labels and dashboard text."),
    colorDashBg=input.color(color.new(color.black, 20), "Dashboard Background", group=grp_style, tooltip="Background color for the dashboard tables."),
    colorDashHd=input.color(color.new(color.gray, 40), "Dashboard Header", group=grp_style, tooltip="Background color for the header rows in the dashboards."),
    colorWin=input.color(color.green, "Win Rate High Color", group=grp_style, tooltip="Text color when the win rate is 50% or above."),
    colorLoss=input.color(color.orange, "Win Rate Low Color", group=grp_style, tooltip="Text color when the win rate falls below 50%.")
):
    trend: PersistentSeries[int] = 0
    nextTrend: Persistent[int] = 0
    maxLowPrice: Persistent[float] = low
    minHighPrice: Persistent[float] = high
    up: PersistentSeries[float] = 0.0
    down: PersistentSeries[float] = 0.0

    atrHigh: float = 0.0
    atrLow: float = 0.0
    arrowUp: float = na(float)
    arrowDown: float = na(float)

    atr2: float = ta.atr(100) / 2
    dev: float = channelDeviation * atr2

    highPrice: float = high[math.abs(ta.highestbars(high, amplitude))]
    lowPrice: float = low[math.abs(ta.lowestbars(low, amplitude))]

    highma: float = ta.sma(high, amplitude)
    lowma: float = ta.sma(low, amplitude)

    if nextTrend == 1:
        maxLowPrice = math.max(lowPrice, maxLowPrice)
        if highma < maxLowPrice and close < nz(low[1], low):
            trend = 1
            nextTrend = 0
            minHighPrice = highPrice
    else:
        minHighPrice = math.min(highPrice, minHighPrice)
        if lowma > minHighPrice and close > nz(high[1], high):
            trend = 0
            nextTrend = 1
            maxLowPrice = lowPrice

    if trend == 0:
        if not na(trend[1]) and trend[1] != 0:
            up = down if na(down[1]) else down[1]
            arrowUp = up - atr2
        else:
            up = maxLowPrice if na(up[1]) else math.max(maxLowPrice, up[1])
        atrHigh = up + dev
        atrLow = up - dev
    else:
        if not na(trend[1]) and trend[1] != 1:
            down = up if na(up[1]) else up[1]
            arrowDown = down + atr2
        else:
            down = minHighPrice if na(down[1]) else math.min(minHighPrice, down[1])
        atrHigh = down + dev
        atrLow = down - dev

    htLine: float = up if trend == 0 else down

    buySignal: bool = trend == 0 and trend[1] == 1 and barstate.isconfirmed
    sellSignal: bool = trend == 1 and trend[1] == 0 and barstate.isconfirmed

    activeSL: Persistent[float] = na(float)
    activeTP1: Persistent[float] = na(float)
    activeTP2: Persistent[float] = na(float)
    activeTP3: Persistent[float] = na(float)

    tradeState: Persistent[int] = 0
    entryPx: Persistent[float] = na(float)
    wins: Persistent[int] = 0
    losses: Persistent[int] = 0

    longTPHit: bool = False
    shortTPHit: bool = False
    longTPHit1: Persistent[bool] = False
    shortTPHit1: Persistent[bool] = False

    if tradeState == 1:
        if not na(activeSL):
            if high >= activeTP1:
                wins += 1
                activeTP1 = na
                longTPHit = True
                longTPHit1 = True
            elif high >= activeTP2:
                wins += 1
                activeTP2 = na
                longTPHit = True
            elif high >= activeTP3:
                wins += 1
                activeTP3 = na
                longTPHit = True
                tradeState = 0
                activeSL = na

        if low <= activeSL:
            losses += 1

            tradeState = 0
            activeSL = na

            if longTPHit1:
                wins -= 1
                losses -= 1
    elif tradeState == -1:
        if not na(activeSL):
            if low <= activeTP1:
                wins += 1
                activeTP1 = na
                shortTPHit = True
                shortTPHit1 = True
            elif low <= activeTP2:
                wins += 1
                activeTP2 = na
                shortTPHit = True
            elif low <= activeTP3:
                wins += 1
                activeTP3 = na
                shortTPHit = True
                tradeState = 0
                activeSL = na

        if high >= activeSL:
            losses += 1
            tradeState = 0
            activeSL = na
            if shortTPHit1:
                wins -= 1
                losses -= 1

    if buySignal:
        longTPHit1 = False
        dist: float = atr2 * baseRiskMult
        activeSL = close - dist
        activeTP1 = close + dist
        activeTP2 = close + dist * 2
        activeTP3 = close + dist * 3
        tradeState = 1
        entryPx = close
    elif sellSignal:
        shortTPHit1 = False
        dist: float = atr2 * baseRiskMult
        activeSL = close + dist
        activeTP1 = close - dist
        activeTP2 = close - dist * 2
        activeTP3 = close - dist * 3
        tradeState = -1
        entryPx = close

    currentDistPct: float = 0.0
    if tradeState == 1:
        currentDistPct = (close - entryPx) / entryPx * 100
    elif tradeState == -1:
        currentDistPct = (entryPx - close) / entryPx * 100

    totalTrades: int = wins + losses
    winRate: float = wins / totalTrades * 100 if totalTrades > 0 else 0.0

    t1 = request.security(sym1, timeframe.period, trend)
    t2 = request.security(sym2, timeframe.period, trend)
    t3 = request.security(sym3, timeframe.period, trend)
    t4 = request.security(sym4, timeframe.period, trend)
    t5 = request.security(sym5, timeframe.period, trend)

    htColor: Color = colorBull if trend == 0 else colorBear
    plot(htLine, 'HalfTrend', color=htColor, linewidth=3)
    plot(atrHigh, 'ATR High Band', color=color.new(colorBear, channelDeviationUp))
    plot(atrLow, 'ATR Low Band', color=color.new(colorBull, channelDeviationUp))

    plotshape(buySignal, 'Long Label', style=shape.labelup, location=location.belowbar, color=colorBull, text='LONG', textcolor=colorText, size=size.normal)
    plotshape(sellSignal, 'Short Label', style=shape.labeldown, location=location.abovebar, color=colorBear, text='SHORT', textcolor=colorText, size=size.normal)

    p_bull_sl = plot(activeSL if trend == 0 and tradeState != 0 and (not na(activeTP3)) else na, 'Bull SL', color=color.new(colorSL, 40), style=plot.style_linebr, linewidth=1)
    p_bear_sl = plot(activeSL if trend == 1 and tradeState != 0 and (not na(activeTP3)) else na, 'Bear SL', color=color.new(colorSL, 40), style=plot.style_linebr, linewidth=1)

    p_entry = plot(entryPx if tradeState != 0 and (not na(activeTP3)) and (not na(activeSL)) else na, 'Trade Entry', color=color.new(colorEntry, 0), style=plot.style_linebr, linewidth=1)

    plot(activeTP1 if trend == 0 and tradeState != 0 and (not na(activeSL)) else na, 'Bull TP1', color=color.new(colorTP, 30), style=plot.style_linebr, linewidth=1)
    plot(activeTP2 if trend == 0 and tradeState != 0 and (not na(activeSL)) else na, 'Bull TP2', color=color.new(colorTP, 15), style=plot.style_linebr, linewidth=1)
    p_bull_tp3 = plot(activeTP3 if trend == 0 and tradeState != 0 and (not na(activeSL)) else na, 'Bull TP3', color=color.new(colorTP, 0), style=plot.style_linebr, linewidth=1)

    plot(activeTP1 if trend == 1 and tradeState != 0 and (not na(activeSL)) else na, 'Bear TP1', color=color.new(colorTP, 30), style=plot.style_linebr, linewidth=1)
    plot(activeTP2 if trend == 1 and tradeState != 0 and (not na(activeSL)) else na, 'Bear TP2', color=color.new(colorTP, 15), style=plot.style_linebr, linewidth=1)
    p_bear_tp3 = plot(activeTP3 if trend == 1 and tradeState != 0 and (not na(activeSL)) else na, 'Bear TP3', color=color.new(colorTP, 0), style=plot.style_linebr, linewidth=1)

    count: Persistent[int] = 0

    if trend != trend[1]:
        count = 0

    if longTPHit:
        count += 1
        label.new(bar_index, high, '✓' + string.tostring(count), style=label.style_label_down, textcolor=colorTP, color=NA(Color))
        if count == 3:
            count = 0

    if shortTPHit:
        count += 1
        label.new(bar_index, low, '✓' + string.tostring(count), style=label.style_label_up, textcolor=colorTP, color=NA(Color))
        if count == 3:
            count = 0

    fill(plot1=p_bull_tp3, plot2=p_entry, top_value=activeTP3, bottom_value=entryPx, top_color=colorFillTP, bottom_color=color.new(colorFillTP, 95), title='Bull TP Gradient')
    fill(plot1=p_entry, plot2=p_bull_sl, top_value=entryPx, bottom_value=activeSL, top_color=color.new(colorFillSL, 95), bottom_color=colorFillSL, title='Bull SL Gradient')

    fill(plot1=p_entry, plot2=p_bear_tp3, top_value=entryPx, bottom_value=activeTP3, top_color=color.new(colorFillTP, 95), bottom_color=colorFillTP, title='Bear TP Gradient')
    fill(plot1=p_bear_sl, plot2=p_entry, top_value=activeSL, bottom_value=entryPx, top_color=colorFillSL, bottom_color=color.new(colorFillSL, 95), title='Bear SL Gradient')

    dashMain: Persistent[Table] = na(Table)
    dashMulti: Persistent[Table] = na(Table)

    if barstate.islast:
        dashMain = table.new(position.bottom_right, 2, 5, bgcolor=colorDashBg, border_color=chart.bg_color, border_width=2)

        table.cell(dashMain, 0, 0, 'PERFORMANCE', text_color=colorText, bgcolor=colorDashHd, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMain, 1, 0, 'DATA', text_color=colorText, bgcolor=colorDashHd, text_size=size.normal)

        table.cell(dashMain, 0, 1, 'Win Rate', text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMain, 1, 1, string.tostring(winRate, '#.##') + '% (' + string.tostring(wins) + 'W | ' + string.tostring(losses) + 'L)', text_color=colorWin if winRate >= 50 else colorLoss, text_size=size.normal, tooltip='Win Rate (Wins/ Losses)')

        table.cell(dashMain, 0, 2, 'Target R:R', text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMain, 1, 2, '1 : 3', text_color=colorText, text_size=size.normal)

        tradeTxt: str = 'LONG' if tradeState == 1 else 'SHORT' if tradeState == -1 else 'NONE'
        tradeCol: Color = colorBull if tradeState == 1 else colorSL if tradeState == -1 else colorText
        distTxt: str = ' (' + ('+' if currentDistPct > 0 else '') + string.tostring(currentDistPct, '#.##') + '%)' if tradeState != 0 else ''

        table.cell(dashMain, 0, 4, 'Current Trade', text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMain, 1, 4, tradeTxt + distTxt, text_color=tradeCol, text_size=size.normal, bgcolor=color.new(tradeCol, 85))

        dashMulti = table.new(position.top_right, 2, 6, bgcolor=colorDashBg, border_color=chart.bg_color, border_width=2)

        table.cell(dashMulti, 0, 0, 'MULTI-ASSET', text_color=colorText, bgcolor=colorDashHd, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 0, 'TRADE', text_color=colorText, bgcolor=colorDashHd, text_size=size.normal)

        table.cell(dashMulti, 0, 1, sym1, text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 1, 'LONG' if t1 == 0 else 'SHORT', text_color=colorBull if t1 == 0 else colorSL, text_size=size.normal, bgcolor=color.new(colorBull, 85) if t1 == 0 else color.new(colorBear, 85))

        table.cell(dashMulti, 0, 2, sym2, text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 2, 'LONG' if t2 == 0 else 'SHORT', text_color=colorBull if t2 == 0 else colorSL, text_size=size.normal, bgcolor=color.new(colorBull, 85) if t2 == 0 else color.new(colorBear, 85))

        table.cell(dashMulti, 0, 3, sym3, text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 3, 'LONG' if t3 == 0 else 'SHORT', text_color=colorBull if t3 == 0 else colorSL, text_size=size.normal, bgcolor=color.new(colorBull, 85) if t3 == 0 else color.new(colorBear, 85))

        table.cell(dashMulti, 0, 4, sym4, text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 4, 'LONG' if t4 == 0 else 'SHORT', text_color=colorBull if t4 == 0 else colorSL, text_size=size.normal, bgcolor=color.new(colorBull, 85) if t4 == 0 else color.new(colorBear, 85))

        table.cell(dashMulti, 0, 5, sym5, text_color=colorText, text_size=size.normal, text_halign=text.align_left)
        table.cell(dashMulti, 1, 5, 'LONG' if t5 == 0 else 'SHORT', text_color=colorBull if t5 == 0 else colorSL, text_size=size.normal, bgcolor=color.new(colorBull, 85) if t5 == 0 else color.new(colorBear, 85))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
