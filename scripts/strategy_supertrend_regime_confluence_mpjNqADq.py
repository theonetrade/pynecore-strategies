"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.lib import (
    alertcondition, bar_index, barstate, bgcolor, close, color, display,
    high, hl2, input, label, low, math, na, nz, plot, script, size, strategy, string, syminfo, ta,
    time, timestamp, volume
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

GRP_ST: str = "SuperTrend"
GRP_REG: str = "Regime Detection"
GRP_SC: str = "Signal Engine"
GRP_SZ: str = "Position Sizing"
GRP_RISK: str = "Risk Management"
GRP_FLT: str = "Trade Filters"
GRP_BT: str = "Backtest"
GRP_VIS: str = "Visuals"
GRP_COL: str = "Colors"


@script.strategy("SuperTrend Regime Confluence", "ST Regime Conf", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, commission_type=strategy.commission.percent, commission_value=0.06, slippage=2, pyramiding=0, calc_on_every_tick=False, max_labels_count=500)
def main(
    i_atLen=input.int(10, "ATR Length", minval=1, maxval=50, group=GRP_ST),
    i_bMult=input.float(3.0, "Base Multiplier", minval=0.5, maxval=10.0, step=0.1, group=GRP_ST),
    i_src: Series[float] = input.source(hl2, "Source", group=GRP_ST),
    i_regLen=input.int(40, "Regime Lookback", minval=10, maxval=100, group=GRP_REG),
    i_adxLen=input.int(14, "ADX Length", minval=5, maxval=50, group=GRP_REG),
    i_adxThr=input.float(20, "ADX Trend Threshold", minval=10, maxval=40, step=1, group=GRP_REG),
    i_adapt=input.bool(True, "Adaptive Multiplier", group=GRP_REG),
    i_trendLen=input.int(50, "Trend EMA Length", minval=10, maxval=200, group=GRP_SC),
    i_volLen=input.int(20, "Volume MA Length", minval=5, maxval=50, group=GRP_SC),
    i_minSc=input.int(65, "Min Signal Score", minval=0, maxval=90, group=GRP_SC, tooltip="Only enter when the composite score meets this threshold. Higher = fewer, higher-conviction entries."),
    i_sizeMode=input.string("Risk %", "Sizing Mode", options=("Risk %", "Equity %", "Fixed Units"), group=GRP_SZ, tooltip="Risk %: size the position so the stop-loss risks a fixed % of equity (recommended). Equity %: fixed % of equity as notional. Fixed Units: constant coin/contract size."),
    i_riskPct=input.float(5.0, "Risk % per Trade", minval=0.1, maxval=10.0, step=0.1, group=GRP_SZ, tooltip="Percent of current equity risked from entry to stop. 5% sits at the conservative end of TradingView's 5-10% guidance. Lower to 3-4% if you see any margin calls across the full history."),
    i_eqPct=input.float(15.0, "Equity % (notional)", minval=1.0, maxval=100.0, step=1.0, group=GRP_SZ),
    i_fixedQty=input.float(1.0, "Fixed Units", minval=0.0, step=0.1, group=GRP_SZ),
    i_noLev=input.bool(True, "Cap at No Leverage", group=GRP_SZ, tooltip="Cap the position at 90% of equity. Leaves a margin buffer so a reversal bar cannot trigger a broker liquidation (margin call). Spot-realistic."),
    i_slMode=input.string("ATR", "Stop Loss Mode", options=("ATR", "Percent", "SuperTrend"), group=GRP_RISK, tooltip="ATR: dynamic stop from volatility. Percent: fixed %. SuperTrend: exit on trend flip."),
    i_slAtr=input.float(6.0, "SL ATR Multiplier", minval=0.5, maxval=10.0, step=0.1, group=GRP_RISK),
    i_slPct=input.float(3.0, "SL Percent", minval=0.5, maxval=15.0, step=0.1, group=GRP_RISK),
    i_tpMode=input.string("RR", "Take Profit Mode", options=("RR", "Percent", "None"), group=GRP_RISK, tooltip="RR: reward as a multiple of stop distance. Percent: fixed %. None: hold until SL or flip."),
    i_tpRR=input.float(2.5, "TP Risk:Reward", minval=0.5, maxval=10.0, step=0.1, group=GRP_RISK),
    i_tpPct=input.float(6.0, "TP Percent", minval=0.5, maxval=25.0, step=0.1, group=GRP_RISK),
    i_trail=input.bool(False, "Trailing Stop", group=GRP_RISK, tooltip="Trail the stop in the trade's direction after entry."),
    i_trailAtr=input.float(2.5, "Trail ATR Mult", minval=0.5, maxval=8.0, step=0.1, group=GRP_RISK),
    i_trendF=input.bool(True, "EMA Trend Filter", group=GRP_FLT, tooltip="Longs only above EMA, shorts only below."),
    i_regF=input.bool(True, "Skip Ranging", group=GRP_FLT, tooltip="Skip entries during the ranging regime. Reduces whipsaws."),
    i_volF=input.bool(True, "Volume Filter", group=GRP_FLT, tooltip="Only enter if volume is above its average."),
    i_sigCD=input.int(5, "Cooldown (bars)", minval=0, maxval=50, group=GRP_FLT),
    i_longs=input.bool(True, "Allow Longs", inline="dir", group=GRP_FLT),
    i_shorts=input.bool(True, "Allow Shorts", inline="dir", group=GRP_FLT),
    i_btFrom=input.time(timestamp('2015-01-01'), "From", group=GRP_BT),
    i_btTo=input.time(timestamp('2035-01-01'), "To", group=GRP_BT),
    i_sGlow=input.bool(True, "Band Glow Effect", group=GRP_VIS),
    i_sRegBg=input.bool(True, "Regime Background", group=GRP_VIS),
    i_showLbl=input.bool(True, "Show score labels", group=GRP_VIS, tooltip="The per-signal score boxes on the chart. Turn OFF to de-clutter. (The Long/Short/Margin-call ARROWS are TradingView's, not the script's — hide those via Settings -> Properties -> uncheck Signal labels.)"),
    i_cBull=input.color(color.new(color.new('#089981'), 0), "Bull", inline="c1", group=GRP_COL),
    i_cBear=input.color(color.new(color.new('#F23645'), 0), "Bear", inline="c1", group=GRP_COL)
):
    inWindow: bool = time >= i_btFrom and time <= i_btTo


    n: int = bar_index
    atr: float = ta.atr(i_atLen)
    safeAtr: float = nz(atr, 0.001)

    atrMa: float = ta.sma(atr, i_regLen)
    atrRatio: float = atr / atrMa if atrMa > 0 else 1.0

    upMove: float = high - high[1]
    dnMove: float = low[1] - low
    plusDM: float = upMove if upMove > dnMove and upMove > 0 else 0
    minusDM: float = dnMove if dnMove > upMove and dnMove > 0 else 0
    smoothTR: float = ta.rma(ta.tr, i_adxLen)
    smoothPD: float = ta.rma(plusDM, i_adxLen)
    smoothND: float = ta.rma(minusDM, i_adxLen)
    plusDI: float = 100 * smoothPD / smoothTR if smoothTR > 0 else 0
    minusDI: float = 100 * smoothND / smoothTR if smoothTR > 0 else 0
    diSum: float = plusDI + minusDI
    dx: float = 100 * math.abs(plusDI - minusDI) / diSum if diSum > 0 else 0
    adx: float = ta.rma(dx, i_adxLen)

    regime: Persistent[int] = 1
    if atrRatio > 1.4:
        regime = 2
    elif adx < i_adxThr and atrRatio < 0.9:
        regime = 0
    else:
        regime = 1

    adaptMult: float = i_bMult
    if i_adapt:
        if regime == 2:
            adaptMult = i_bMult * (1.0 + (atrRatio - 1.0) * 0.4)
        elif regime == 0:
            adaptMult = i_bMult * 0.85
    adaptMult = math.max(math.min(adaptMult, i_bMult * 2.0), i_bMult * 0.5)

    stBand: PersistentSeries[float] = na(float)
    stDir: PersistentSeries[int] = 1

    upperBase: float = i_src + adaptMult * atr
    lowerBase: float = i_src - adaptMult * atr
    prevBand: float = nz(stBand[1], lowerBase if stDir == 1 else upperBase)

    if stDir == 1:
        stBand = math.max(lowerBase, prevBand)
        if close < stBand:
            stDir = -1
            stBand = upperBase
    else:
        stBand = math.min(upperBase, prevBand)
        if close > stBand:
            stDir = 1
            stBand = lowerBase

    trendFlip: bool = stDir != stDir[1]

    trendMa: float = ta.ema(close, i_trendLen)
    trendUp: bool = close > trendMa
    trendDn: bool = close < trendMa

    volMa: float = ta.sma(volume, i_volLen)

    def scoreSignal(isBull: bool):
        __hist_stBand__: Series[float] = stBand[0]
        score: float = 0

        vRat: float = volume / volMa if volMa > 0 else 1.0
        score += 20 if vRat >= 2.5 else 14 if vRat >= 1.5 else 8 if vRat >= 1.0 else 3

        disp: float = close - stBand if isBull else stBand - close
        dispAtr: float = disp / safeAtr if safeAtr > 0 else 0
        score += 25 if dispAtr >= 1.5 else 18 if dispAtr >= 0.8 else 12 if dispAtr >= 0.3 else 5 if dispAtr > 0 else 0

        aligned: bool = isBull and trendUp or (not isBull and trendDn)
        emaDist: float = math.abs(close - trendMa) / safeAtr
        score += 20 if aligned and emaDist > 0.5 else 14 if aligned else 8 if emaDist < 0.3 else 2

        score += 15 if regime == 1 else 8 if regime == 2 else 3

        prevDist: float = math.abs(close[1] - __hist_stBand__[1]) / safeAtr if not na(__hist_stBand__[1]) else 0
        score += 20 if prevDist >= 2.0 else 14 if prevDist >= 1.0 else 8 if prevDist >= 0.5 else 3

        return cast_int(math.min(math.round(score), 100))

    def f_posQty(_stopDist: float):
        q: float = i_fixedQty
        if i_sizeMode == 'Risk %':
            riskCap: float = strategy.equity * i_riskPct / 100.0
            q = riskCap / _stopDist if _stopDist > 0 else na
        elif i_sizeMode == 'Equity %':
            q = strategy.equity * i_eqPct / 100.0 / close if close > 0 else na
        if i_noLev and (not na(q)) and (close > 0):
            q = math.min(q, 0.9 * strategy.equity / close)
        return na if na(q) or q <= 0 else q

    lastEntryBar: Persistent[int] = 0
    entryPrice: Persistent[float] = 0.0
    slPrice: Persistent[float] = 0.0
    tpPrice: Persistent[float] = 0.0
    lastSigScore: Persistent[int] = 0
    lastSigDir: Persistent[int] = 0

    longEntry: bool = False
    shortEntry: bool = False
    sigScore: int = 0

    cdOk: bool = n - lastEntryBar > i_sigCD

    if trendFlip and inWindow and cdOk and barstate.isconfirmed:
        if stDir == 1:
            sigScore = scoreSignal(True)
            passScore: bool = sigScore >= i_minSc
            passTrend: bool = not i_trendF or trendUp
            passReg: bool = not i_regF or regime != 0
            passVol: bool = not i_volF or volume > volMa
            if passScore and passTrend and passReg and passVol and i_longs:
                longEntry = True
        else:
            sigScore = scoreSignal(False)
            passScore: bool = sigScore >= i_minSc
            passTrend: bool = not i_trendF or trendDn
            passReg: bool = not i_regF or regime != 0
            passVol: bool = not i_volF or volume > volMa
            if passScore and passTrend and passReg and passVol and i_shorts:
                shortEntry = True

    slDist: float = 0.0
    if i_slMode == 'ATR':
        slDist = atr * i_slAtr
    elif i_slMode == 'Percent':
        slDist = close * i_slPct / 100
    else:
        slDist = math.abs(close - stBand)

    tpDist: float = 0.0
    if i_tpMode == 'RR':
        tpDist = slDist * i_tpRR
    elif i_tpMode == 'Percent':
        tpDist = close * i_tpPct / 100

    if longEntry:
        q: float = f_posQty(slDist)
        if not na(q):
            if strategy.position_size < 0:
                strategy.close('Short')
            entryPrice = close
            slPrice = close - slDist
            tpPrice = close + tpDist if i_tpMode != 'None' else na
            strategy.entry('Long', strategy.long, qty=q)
            if i_tpMode != 'None':
                strategy.exit('Long Exit', 'Long', stop=slPrice, limit=tpPrice, trail_points=slDist / syminfo.mintick if i_trail else na, trail_offset=atr * i_trailAtr / syminfo.mintick if i_trail else na)
            else:
                strategy.exit('Long SL', 'Long', stop=slPrice, trail_points=slDist / syminfo.mintick if i_trail else na, trail_offset=atr * i_trailAtr / syminfo.mintick if i_trail else na)
            lastEntryBar = n
            lastSigScore = sigScore
            lastSigDir = 1

    if shortEntry:
        q: float = f_posQty(slDist)
        if not na(q):
            if strategy.position_size > 0:
                strategy.close('Long')
            entryPrice = close
            slPrice = close + slDist
            tpPrice = close - tpDist if i_tpMode != 'None' else na
            strategy.entry('Short', strategy.short, qty=q)
            if i_tpMode != 'None':
                strategy.exit('Short Exit', 'Short', stop=slPrice, limit=tpPrice, trail_points=slDist / syminfo.mintick if i_trail else na, trail_offset=atr * i_trailAtr / syminfo.mintick if i_trail else na)
            else:
                strategy.exit('Short SL', 'Short', stop=slPrice, trail_points=slDist / syminfo.mintick if i_trail else na, trail_offset=atr * i_trailAtr / syminfo.mintick if i_trail else na)
            lastEntryBar = n
            lastSigScore = sigScore
            lastSigDir = -1

    if i_slMode == 'SuperTrend' and trendFlip:
        if strategy.position_size > 0 and stDir == -1:
            strategy.close('Long', comment='ST Flip')
        if strategy.position_size < 0 and stDir == 1:
            strategy.close('Short', comment='ST Flip')

    alertcondition(longEntry, 'SRC - Long Entry', 'SuperTrend Regime Confluence: LONG entry signal')
    alertcondition(shortEntry, 'SRC - Short Entry', 'SuperTrend Regime Confluence: SHORT entry signal')

    bandCore: Color = i_cBull if stDir == 1 else i_cBear
    bandColor: Color = color.new(color.new('#FFAB00'), 0) if regime == 2 else color.new(color.new('#78909C'), 20) if regime == 0 else bandCore

    plot(stBand if i_sGlow else na, 'Glow Outer', color=color.new(bandColor, 85), linewidth=6, style=plot.style_linebr)
    plot(stBand if i_sGlow else na, 'Glow Mid', color=color.new(bandColor, 70), linewidth=4, style=plot.style_linebr)

    plot(stBand if regime != 0 else na, 'Band (Solid)', color=bandColor, linewidth=2, style=plot.style_linebr)
    plot(stBand if regime == 0 else na, 'Band (Ranging)', color=bandColor, linewidth=2, style=plot.style_linebr, linestyle=plot.linestyle_dotted)

    plot(stBand if trendFlip else na, 'Flip Dot', color=bandCore, style=plot.style_circles, linewidth=5, join=False)

    bgcolor(color.new(color.new('#FFAB00'), 95) if i_sRegBg and regime == 2 else na, title='Volatile BG')
    bgcolor(color.new(color.new('#78909C'), 96) if i_sRegBg and regime == 0 else na, title='Ranging BG')

    plot(trendMa, 'Trend EMA', color=color.new(i_cBull if trendUp else i_cBear, 65), linewidth=1)

    isBright: bool = sigScore >= 70

    if longEntry and i_showLbl:
        ico: str = '*' if isBright else 'o'
        css: Color = color.new(color.new('#00E676'), 0) if isBright else color.new(color.new('#546E7A'), 0)
        label.new(n, stBand, ico + ' ' + string.tostring(sigScore), color=color.new(css, 0 if isBright else 50), textcolor=color.new('#FFFFFF'), size=size.small if isBright else size.tiny, style=label.style_label_up, tooltip='LONG | Score: ' + string.tostring(sigScore) + '\nRegime: ' + ('TRENDING' if regime == 1 else 'VOLATILE' if regime == 2 else 'RANGING') + '\nSL: ' + string.tostring(math.round(slDist / close * 100, 2)) + '%' + '\nTP: ' + (string.tostring(math.round(tpDist / close * 100, 2)) + '%' if i_tpMode != 'None' else 'None'))

    if shortEntry and i_showLbl:
        ico: str = '*' if isBright else 'o'
        css: Color = color.new(color.new('#FF5252'), 0) if isBright else color.new(color.new('#546E7A'), 0)
        label.new(n, stBand, ico + ' ' + string.tostring(sigScore), color=color.new(css, 0 if isBright else 50), textcolor=color.new('#FFFFFF'), size=size.small if isBright else size.tiny, style=label.style_label_down, tooltip='SHORT | Score: ' + string.tostring(sigScore) + '\nRegime: ' + ('TRENDING' if regime == 1 else 'VOLATILE' if regime == 2 else 'RANGING') + '\nSL: ' + string.tostring(math.round(slDist / close * 100, 2)) + '%' + '\nTP: ' + (string.tostring(math.round(tpDist / close * 100, 2)) + '%' if i_tpMode != 'None' else 'None'))

    plot(sigScore if sigScore > 0 else na, 'Signal Score', display=display.none)
    plot(adaptMult, 'Adaptive Mult', display=display.none)
    plot(adx, 'ADX', display=display.none)
    plot(cast_float(regime), 'Regime', display=display.none)
    plot(cast_float(stDir), 'Trend Direction', display=display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)