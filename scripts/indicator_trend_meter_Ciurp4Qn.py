"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, bar_index, close, color, fill, hlc3, hline, input, math,
    na, ohlc4, open, plot, script, ta
)
from pynecore.types import Series


@script.indicator(title='Trend Meter', na_bool=True)
def main(
    PosNegPressure=input.bool(True, 'Pos / Neg Pressure', tooltip='Positive Pressure   = RSI14 and Wave Trend Over Sold with WT Delta Pointing Up                                                               Negative Pressure = RSI14 and Wave Trend Over Bought with WT Delta Pointing Down', group='Signals'),
    TMSetups=input.bool(True, 'Trend Meter Signal', tooltip='All 3 Trend Meters Now Align', group='Signals'),
    TMSetupsANDWT=input.bool(True, 'Wave Trend Cross Aligns with Trend Meter Signal', group='Signals'),
    TrendBar1=input.string(title='Trend Meter 1', defval='MACD Crossover - Fast - 8, 21, 5', options=('MACD Crossover - 12, 26, 9', 'MACD Crossover - Fast - 8, 21, 5', 'Mom Dad Cross (Top Dog Trading)', 'RSI Signal Line Cross - RSI 13, Sig 21', 'RSI 13: > or < 50', 'RSI 5: > or < 50', 'Trend Candles', 'N/A'), group='Trend Meters'),
    TrendBar2=input.string(title='Trend Meter 2', defval='RSI 13: > or < 50', options=('MACD Crossover - 12, 26, 9', 'MACD Crossover - Fast - 8, 21, 5', 'Mom Dad Cross (Top Dog Trading)', 'RSI Signal Line Cross - RSI 13, Sig 21', 'RSI 13: > or < 50', 'RSI 5: > or < 50', 'Trend Candles', 'N/A'), group='Trend Meters'),
    TrendBar3=input.string(title='Trend Meter 3', defval='RSI 5: > or < 50', options=('MACD Crossover - 12, 26, 9', 'MACD Crossover - Fast - 8, 21, 5', 'Mom Dad Cross (Top Dog Trading)', 'RSI Signal Line Cross - RSI 13, Sig 21', 'RSI 13: > or < 50', 'RSI 5: > or < 50', 'Trend Candles', 'N/A'), group='Trend Meters'),
    ShowTrendBar1=input.bool(True, 'Trend Bar 1', group='Trend Bar 1', inline='Trend Bar 1'),
    ShowTrendBar2=input.bool(True, 'Trend Bar 2', group='Trend Bar 2', inline='Trend Bar 2'),
    TrendBar4=input.string(title='', defval='MA Crossover', options=('MA Crossover', 'MA Direction - Fast MA - TB1', 'MA Direction - Slow MA - TB1'), group='Trend Bar 1', inline='Trend Bar 1'),
    TrendBar5=input.string(title='', defval='MA Crossover', options=('MA Crossover', 'MA Direction - Fast MA - TB2', 'MA Direction - Slow MA - TB2'), group='Trend Bar 2', inline='Trend Bar 2'),
    MA1_Length=input.int(5, title='Fast MA', minval=1, group='Trend Bar 1', inline='TB1 Fast'),
    MA1_Type=input.string(title='', defval='EMA', options=('EMA', 'SMA'), group='Trend Bar 1', inline='TB1 Fast'),
    MA2_Length=input.int(11, title='Slow MA', minval=1, group='Trend Bar 1', inline='TB1 Slow'),
    MA2_Type=input.string(title='', defval='EMA', options=('EMA', 'SMA'), group='Trend Bar 1', inline='TB1 Slow'),
    MA3_Length=input.int(13, title='Fast MA', minval=1, group='Trend Bar 2', inline='TB2 Fast'),
    MA3_Type=input.string(title='', defval='EMA', options=('EMA', 'SMA'), group='Trend Bar 2', inline='TB2 Fast'),
    MA4_Length=input.int(36, title='Slow MA', minval=1, group='Trend Bar 2', inline='TB2 Slow'),
    MA4_Type=input.string(title='', defval='SMA', options=('EMA', 'SMA'), group='Trend Bar 2', inline='TB2 Slow')
):
    RSIMC = ta.rsi(close, 14)
    ap = hlc3
    n1: int = 9
    n2: int = 12
    esa = ta.ema(ap, n1)
    de = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * de)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 3)
    YellowWave: Series = wt1 - wt2
    obLevel2: int = 60
    obLevel: int = 50
    osLevel = -50
    osLevel2 = -60
    WTCross = ta.cross(wt1, wt2)
    WTCrossUp = wt2 - wt1 <= 0
    WTCrossDown = wt2 - wt1 >= 0
    WTOverSold = wt2 <= osLevel2
    WTOverBought = wt2 >= obLevel2
    Close = close
    __block_result__ = na
    if MA1_Type == 'SMA':
        __block_result__ = ta.sma(Close, MA1_Length)
    else:
        __block_result__ = ta.ema(Close, MA1_Length)
    MA1: Series = __block_result__
    __block_result_1__ = na
    if MA2_Type == 'SMA':
        __block_result_1__ = ta.sma(Close, MA2_Length)
    else:
        __block_result_1__ = ta.ema(Close, MA2_Length)
    MA2: Series = __block_result_1__
    __block_result_2__ = na
    if MA3_Type == 'SMA':
        __block_result_2__ = ta.sma(Close, MA3_Length)
    else:
        __block_result_2__ = ta.ema(Close, MA3_Length)
    MA3: Series = __block_result_2__
    __block_result_3__ = na
    if MA4_Type == 'SMA':
        __block_result_3__ = ta.sma(Close, MA4_Length)
    else:
        __block_result_3__ = ta.ema(Close, MA4_Length)
    MA4: Series = __block_result_3__
    MACrossover1 = 1 if MA1 > MA2 else 0
    MACrossover2 = 1 if MA3 > MA4 else 0
    MA1Direction: Series = 1 if MA1 > MA1[1] else 0
    MA2Direction: Series = 1 if MA2 > MA2[1] else 0
    MA3Direction: Series = 1 if MA3 > MA3[1] else 0
    MA4Direction: Series = 1 if MA4 > MA4[1] else 0
    MA1PositiveDirectionChange = 1 if cast_bool(MA1Direction) and (not MA1Direction[1]) else 0
    MA2PositiveDirectionChange = 1 if cast_bool(MA2Direction) and (not MA2Direction[1]) else 0
    MA3PositiveDirectionChange = 1 if cast_bool(MA3Direction) and (not MA3Direction[1]) else 0
    MA4PositiveDirectionChange = 1 if cast_bool(MA4Direction) and (not MA4Direction[1]) else 0
    MA1NegativeDirectionChange = 1 if not MA1Direction and cast_bool(MA1Direction[1]) else 0
    MA2NegativeDirectionChange = 1 if not MA2Direction and cast_bool(MA2Direction[1]) else 0
    MA3NegativeDirectionChange = 1 if not MA3Direction and cast_bool(MA3Direction[1]) else 0
    MA4NegativeDirectionChange = 1 if not MA4Direction and cast_bool(MA4Direction[1]) else 0
    MACDfastMA: int = 12
    MACDslowMA: int = 26
    MACDsignalSmooth: int = 9
    MACDLine = ta.ema(close, MACDfastMA) - ta.ema(close, MACDslowMA)
    SignalLine = ta.ema(MACDLine, MACDsignalSmooth)
    MACDHistogram = MACDLine - SignalLine
    MACDHistogramCross = 1 if MACDHistogram > 0 else 0
    MACDLineOverZero = 1 if MACDLine > 0 else 0
    MACDLineOverZeroandHistogramCross = 1 if cast_bool(MACDHistogramCross) and cast_bool(MACDLineOverZero) else 0
    MACDLineUnderZeroandHistogramCross = 1 if not MACDHistogramCross and (not MACDLineOverZero) else 0
    FastMACDfastMA: int = 8
    FastMACDslowMA: int = 21
    FastMACDsignalSmooth: int = 5
    FastMACDLine = ta.ema(close, FastMACDfastMA) - ta.ema(close, FastMACDslowMA)
    FastSignalLine = ta.ema(FastMACDLine, FastMACDsignalSmooth)
    FastMACDHistogram = FastMACDLine - FastSignalLine
    FastMACDHistogramCross = 1 if FastMACDHistogram > 0 else 0
    FastMACDLineOverZero = 1 if FastMACDLine > 0 else 0
    FastMACDLineOverZeroandHistogramCross = 1 if cast_bool(FastMACDHistogramCross) and cast_bool(FastMACDLineOverZero) else 0
    FastMACDLineUnderZeroandHistogramCross = 1 if not FastMACDHistogramCross and (not FastMACDLineOverZero) else 0
    TopDog_Fast_MA: int = 5
    TopDog_Slow_MA: int = 20
    TopDog_Sig: int = 30
    TopDogMom = ta.ema(close, TopDog_Fast_MA) - ta.ema(close, TopDog_Slow_MA)
    TopDogDad: Series = ta.ema(TopDogMom, TopDog_Sig)
    TopDogDadDirection = 1 if TopDogDad > TopDogDad[1] else 0
    TopDogMomOverDad = 1 if TopDogMom > TopDogDad else 0
    TopDogMomOverZero = 1 if TopDogMom > 0 else 0
    TopDogDadDirectandMomOverZero = 1 if cast_bool(TopDogDadDirection) and cast_bool(TopDogMomOverZero) else 0
    TopDogDadDirectandMomUnderZero = 1 if not TopDogDadDirection and (not TopDogMomOverZero) else 0
    haclose: Series = ohlc4
    haopen: Series[float] = 0.0
    haopen = (open + close) / 2 if na(haopen[1]) else (haopen[1] + haclose[1]) / 2
    ccolor: Series = 1 if haclose - haopen > 0 else 0
    inside6 = 1 if haopen <= math.max(haopen[6], haclose[6]) and haopen >= math.min(haopen[6], haclose[6]) and (haclose <= math.max(haopen[6], haclose[6])) and (haclose >= math.min(haopen[6], haclose[6])) else 0
    inside5 = 1 if haopen <= math.max(haopen[5], haclose[5]) and haopen >= math.min(haopen[5], haclose[5]) and (haclose <= math.max(haopen[5], haclose[5])) and (haclose >= math.min(haopen[5], haclose[5])) else 0
    inside4 = 1 if haopen <= math.max(haopen[4], haclose[4]) and haopen >= math.min(haopen[4], haclose[4]) and (haclose <= math.max(haopen[4], haclose[4])) and (haclose >= math.min(haopen[4], haclose[4])) else 0
    inside3 = 1 if haopen <= math.max(haopen[3], haclose[3]) and haopen >= math.min(haopen[3], haclose[3]) and (haclose <= math.max(haopen[3], haclose[3])) and (haclose >= math.min(haopen[3], haclose[3])) else 0
    inside2 = 1 if haopen <= math.max(haopen[2], haclose[2]) and haopen >= math.min(haopen[2], haclose[2]) and (haclose <= math.max(haopen[2], haclose[2])) and (haclose >= math.min(haopen[2], haclose[2])) else 0
    inside1 = 1 if haopen <= math.max(haopen[1], haclose[1]) and haopen >= math.min(haopen[1], haclose[1]) and (haclose <= math.max(haopen[1], haclose[1])) and (haclose >= math.min(haopen[1], haclose[1])) else 0
    colorvalue = ccolor[6] if cast_bool(inside6) else ccolor[5] if cast_bool(inside5) else ccolor[4] if cast_bool(inside4) else ccolor[3] if cast_bool(inside3) else ccolor[2] if cast_bool(inside2) else ccolor[1] if cast_bool(inside1) else ccolor
    TrendBarTrend_Candle_Color = color.new('#288A75') if cast_bool(colorvalue) else color.red
    TrendBarTrend_Candle = 1 if cast_bool(colorvalue) else 0
    RSI5 = ta.rsi(close, 5)
    RSI5Above50 = 1 if RSI5 > 50 else 0
    RSI5Color = color.new('#288A75') if cast_bool(RSI5Above50) else color.red
    TrendBarRSI5Color = color.new('#288A75') if cast_bool(RSI5Above50) else color.red
    RSI13 = ta.rsi(close, 13)
    SignalLineLength1: int = 21
    x = bar_index
    y = RSI13
    x_ = ta.sma(x, SignalLineLength1)
    y_ = ta.sma(y, SignalLineLength1)
    mx = ta.stdev(x, SignalLineLength1)
    my = ta.stdev(y, SignalLineLength1)
    c = ta.correlation(x, y, SignalLineLength1)
    slope = c * (my / mx)
    inter = y_ - slope * x_
    LinReg1: Series = x * slope + inter
    RSISigDirection = 1 if LinReg1 > LinReg1[1] else 0
    RSISigCross = 1 if RSI13 > LinReg1 else 0
    RSI13Above50 = 1 if RSI13 > 50 else 0
    RSI13Color = color.new('#288A75') if cast_bool(RSI13Above50) else color.red
    TrendBarRSI13Color = color.new('#288A75') if cast_bool(RSI13Above50) else color.red
    TrendBarRSISigCrossColor = color.new('#288A75') if cast_bool(RSISigCross) else color.red
    TrendBarMACDColor = color.new('#288A75') if cast_bool(MACDHistogramCross) else color.red
    TrendBarFastMACDColor = color.new('#288A75') if cast_bool(FastMACDHistogramCross) else color.red
    TrendBarMACrossColor = color.new('#288A75') if cast_bool(MACrossover1) else color.red
    TrendBarMomOverDadColor = color.new('#288A75') if cast_bool(TopDogMomOverDad) else color.red
    TrendBarDadDirectionColor = color.new('#288A75') if cast_bool(TopDogDadDirection) else color.red
    TrendBar1Result = MACrossover1 if TrendBar1 == 'MA Crossover' else MACDHistogramCross if TrendBar1 == 'MACD Crossover - 12, 26, 9' else FastMACDHistogramCross if TrendBar1 == 'MACD Crossover - Fast - 8, 21, 5' else TopDogMomOverDad if TrendBar1 == 'Mom Dad Cross (Top Dog Trading)' else TopDogDadDirection if TrendBar1 == 'DAD Direction (Top Dog Trading)' else RSISigCross if TrendBar1 == 'RSI Signal Line Cross - RSI 13, Sig 21' else RSI5Above50 if TrendBar1 == 'RSI 5: > or < 50' else RSI13Above50 if TrendBar1 == 'RSI 13: > or < 50' else TrendBarTrend_Candle if TrendBar1 == 'Trend Candles' else na
    TrendBar2Result = MACrossover1 if TrendBar2 == 'MA Crossover' else MACDHistogramCross if TrendBar2 == 'MACD Crossover - 12, 26, 9' else FastMACDHistogramCross if TrendBar2 == 'MACD Crossover - Fast - 8, 21, 5' else TopDogMomOverDad if TrendBar2 == 'Mom Dad Cross (Top Dog Trading)' else TopDogDadDirection if TrendBar2 == 'DAD Direction (Top Dog Trading)' else RSISigCross if TrendBar2 == 'RSI Signal Line Cross - RSI 13, Sig 21' else RSI5Above50 if TrendBar2 == 'RSI 5: > or < 50' else RSI13Above50 if TrendBar2 == 'RSI 13: > or < 50' else TrendBarTrend_Candle if TrendBar2 == 'Trend Candles' else na
    TrendBar3Result = MACrossover1 if TrendBar3 == 'MA Crossover' else MACDHistogramCross if TrendBar3 == 'MACD Crossover - 12, 26, 9' else FastMACDHistogramCross if TrendBar3 == 'MACD Crossover - Fast - 8, 21, 5' else TopDogMomOverDad if TrendBar3 == 'Mom Dad Cross (Top Dog Trading)' else TopDogDadDirection if TrendBar3 == 'DAD Direction (Top Dog Trading)' else RSISigCross if TrendBar3 == 'RSI Signal Line Cross - RSI 13, Sig 21' else RSI5Above50 if TrendBar3 == 'RSI 5: > or < 50' else RSI13Above50 if TrendBar3 == 'RSI 13: > or < 50' else TrendBarTrend_Candle if TrendBar3 == 'Trend Candles' else na
    TrendBars2Positive = 1 if cast_bool(TrendBar1Result) and cast_bool(TrendBar2Result) or (cast_bool(TrendBar1Result) and cast_bool(TrendBar3Result)) or (cast_bool(TrendBar2Result) and cast_bool(TrendBar3Result)) else 0
    TrendBars2Negative = 1 if not TrendBar1Result and (not TrendBar2Result) or (not TrendBar1Result and (not TrendBar3Result)) or (not TrendBar2Result and (not TrendBar3Result)) else 0
    TrendBars3Positive: Series = 1 if cast_bool(TrendBar1Result) and cast_bool(TrendBar2Result) and cast_bool(TrendBar3Result) else 0
    TrendBars3Negative: Series = 1 if not TrendBar1Result and (not TrendBar2Result) and (not TrendBar3Result) else 0
    PositiveWaveTrendCross = WTCross and WTCrossUp
    NegativeWaveTrendCross = WTCross and WTCrossDown
    BackgroundColorChangePositive = cast_bool(TrendBars3Positive) and (not TrendBars3Positive[1])
    BackgroundColorChangeNegative = cast_bool(TrendBars3Negative) and (not TrendBars3Negative[1])
    MSBar2Color = color.new('#288A75') if BackgroundColorChangePositive else color.red if BackgroundColorChangeNegative else na
    TrendBar1Color = na if TrendBar1 == 'N/A' else TrendBarMACDColor if TrendBar1 == 'MACD Crossover - 12, 26, 9' else TrendBarFastMACDColor if TrendBar1 == 'MACD Crossover - Fast - 8, 21, 5' else TrendBarMomOverDadColor if TrendBar1 == 'Mom Dad Cross (Top Dog Trading)' else TrendBarDadDirectionColor if TrendBar1 == 'DAD Direction (Top Dog Trading)' else TrendBarRSISigCrossColor if TrendBar1 == 'RSI Signal Line Cross - RSI 13, Sig 21' else TrendBarRSI5Color if TrendBar1 == 'RSI 5: > or < 50' else TrendBarRSI13Color if TrendBar1 == 'RSI 13: > or < 50' else TrendBarTrend_Candle_Color if TrendBar1 == 'Trend Candles' else TrendBarMACrossColor if TrendBar1 == 'MA Crossover' else na
    TrendBar2Color = na if TrendBar2 == 'N/A' else TrendBarMACDColor if TrendBar2 == 'MACD Crossover - 12, 26, 9' else TrendBarFastMACDColor if TrendBar2 == 'MACD Crossover - Fast - 8, 21, 5' else TrendBarMomOverDadColor if TrendBar2 == 'Mom Dad Cross (Top Dog Trading)' else TrendBarDadDirectionColor if TrendBar2 == 'DAD Direction (Top Dog Trading)' else TrendBarRSISigCrossColor if TrendBar2 == 'RSI Signal Line Cross - RSI 13, Sig 21' else TrendBarRSI5Color if TrendBar2 == 'RSI 5: > or < 50' else TrendBarRSI13Color if TrendBar2 == 'RSI 13: > or < 50' else TrendBarTrend_Candle_Color if TrendBar2 == 'Trend Candles' else TrendBarMACrossColor if TrendBar2 == 'MA Crossover' else na
    TrendBar3Color = na if TrendBar3 == 'N/A' else TrendBarMACDColor if TrendBar3 == 'MACD Crossover - 12, 26, 9' else TrendBarFastMACDColor if TrendBar3 == 'MACD Crossover - Fast - 8, 21, 5' else TrendBarMomOverDadColor if TrendBar3 == 'Mom Dad Cross (Top Dog Trading)' else TrendBarDadDirectionColor if TrendBar3 == 'DAD Direction (Top Dog Trading)' else TrendBarRSISigCrossColor if TrendBar3 == 'RSI Signal Line Cross - RSI 13, Sig 21' else TrendBarRSI5Color if TrendBar3 == 'RSI 5: > or < 50' else TrendBarRSI13Color if TrendBar3 == 'RSI 13: > or < 50' else TrendBarTrend_Candle_Color if TrendBar3 == 'Trend Candles' else TrendBarMACrossColor if TrendBar3 == 'MA Crossover' else na
    CrossoverType2 = TopDogDadDirection if TrendBar4 == 'DAD Direction (Top Dog Trading)' else MACDHistogramCross if TrendBar4 == 'MACD Crossover' else MA1Direction if TrendBar4 == 'MA Direction - Fast MA - TB1' else MA2Direction if TrendBar4 == 'MA Direction - Slow MA - TB1' else MACrossover1
    color_1 = color.new(color.green, 15)
    color_2 = color.new(color.red, 20)
    TrendBar4Color1 = na if TrendBar4 == 'N/A' else color_1 if cast_bool(CrossoverType2) else color_2
    CrossoverType3 = TopDogDadDirection if TrendBar5 == 'DAD Direction (Top Dog Trading)' else MACDHistogramCross if TrendBar5 == 'MACD Crossover' else MA3Direction if TrendBar5 == 'MA Direction - Fast MA - TB2' else MA4Direction if TrendBar5 == 'MA Direction - Slow MA - TB2' else MACrossover2
    color_3 = color.new(color.green, 15)
    color_4 = color.new(color.red, 20)
    TrendBar5Color1 = na if TrendBar5 == 'N/A' else color_3 if cast_bool(CrossoverType3) else color_4
    WTVOB = wt1 > 60
    WTVOS = wt1 < -60
    YellowWavePointingUp = YellowWave > YellowWave[1]
    RSI14 = ta.rsi(close, 14)
    RSI14OB: Series = 1 if RSI14 > 70 else 0
    RSI14OS: Series = 1 if RSI14 < 30 else 0
    RSI14OBOS = 1 if cast_bool(RSI14OB) or cast_bool(RSI14OS) else 0
    OBIndicatorsYellowPointingDown = (cast_bool(RSI14OB) or cast_bool(RSI14OB[1])) and WTVOB and (not YellowWavePointingUp)
    OSIndicatorsYellowPointingUp = (cast_bool(RSI14OS) or cast_bool(RSI14OS[1])) and WTVOS and YellowWavePointingUp
    plot(138.5 if PosNegPressure and OSIndicatorsYellowPointingUp else na, 'Wave Trend - Positive Pressure', color=color.new(color.new('#288A75'), 25), style=plot.style_circles, linewidth=1)
    plot(138.5 if PosNegPressure and OBIndicatorsYellowPointingDown else na, 'Wave Trend - Negative Pressure', color=color.new(color.new('#DC143C'), 32), style=plot.style_circles, linewidth=1)
    alertcondition(OBIndicatorsYellowPointingDown or OSIndicatorsYellowPointingUp, title=' -   Pos / Neg Pressure', message='Pos / Neg Pressure - Trend Meter')
    plot(134.5 if TMSetups else na, title='All 3 Trend Meters Now Align', style=plot.style_circles, color=MSBar2Color, linewidth=3)
    plot(134.5 if TMSetupsANDWT and (PositiveWaveTrendCross and cast_bool(TrendBars3Positive) or (NegativeWaveTrendCross and cast_bool(TrendBars3Negative))) else na, title='Wave Trend X & All 3 Trend Meters Now Align', style=plot.style_cross, color=MSBar2Color, linewidth=4)
    plot(128.5, title='Trend Meter 1', style=plot.style_circles, color=TrendBar1Color, linewidth=2)
    plot(122.5, title='Trend Meter 2', style=plot.style_circles, color=TrendBar2Color, linewidth=2)
    plot(116.5, title='Trend Meter 3', style=plot.style_circles, color=TrendBar3Color, linewidth=2)
    plot(110 if ShowTrendBar1 and ShowTrendBar2 else na, title='Trend Bar 1 - Thin Line', style=plot.style_line, color=TrendBar4Color1, linewidth=4)
    plot(110 if ShowTrendBar1 and (not ShowTrendBar2) else na, title='Trend Bar 1 - Thick Line', style=plot.style_line, color=TrendBar4Color1, linewidth=9)
    plot(104.5 if ShowTrendBar2 and ShowTrendBar1 else na, title='Trend Bar 2 - Thin Line', style=plot.style_line, color=TrendBar5Color1, linewidth=6)
    plot(110 if ShowTrendBar2 and (not ShowTrendBar1) else na, title='Trend Bar 2 - Thick Line', style=plot.style_line, color=TrendBar5Color1, linewidth=9)
    TrendBar3BarsSame = color.green if cast_bool(TrendBars3Positive) else color.red if cast_bool(TrendBars3Negative) else na
    TMa = hline(113.7, color=color.new(color.white, 100))
    TMb = hline(131.3, color=color.new(color.white, 100))
    fill(TMa, TMb, color=color.new(TrendBar3BarsSame, 91), title='Trend Meter Background Highlight - 3 Trend Meter Conditions Met')
    alertcondition(BackgroundColorChangePositive, title=' --  3 TMs Turn Green', message='All 3 Trend Meters Turn  Green - Trend Meter')
    alertcondition(BackgroundColorChangeNegative, title=' --  3 TMs Turn Red', message='All 3 Trend Meters Turn  Red - Trend Meter')
    alertcondition(BackgroundColorChangePositive or BackgroundColorChangeNegative, title=' -- 3 TMs Change to Same Color', message='All 3 Trend Meters Change to Same Color - Trend Meter')
    alertcondition(PositiveWaveTrendCross and cast_bool(TrendBars3Positive), title='--- 3 TMs Turn Green & WaveTrend X', message='Green - Wave Trend Signal - Aligns with 3 Trend Meters - Trend Meter')
    alertcondition(NegativeWaveTrendCross and cast_bool(TrendBars3Negative), title='--- 3 TMs Turn Red & WaveTrend X', message='Red - Wave Trend Signal - Aligns with 3 Trend Meters - Trend Meter')
    alertcondition(PositiveWaveTrendCross and cast_bool(TrendBars3Positive) or (NegativeWaveTrendCross and cast_bool(TrendBars3Negative)), title='--- 3 TMs Change to Same Color & WT X', message='Red / Green - Wave Trend Signal - Aligns with 3 Trend Meters - Trend Meter')
    TrendMetersNoLongerAlign = (not TrendBars3Positive or not TrendBars3Negative) and cast_bool(TrendBars3Positive[1]) or ((not TrendBars3Positive or not TrendBars3Negative) and cast_bool(TrendBars3Negative[1]))
    alertcondition(TrendMetersNoLongerAlign, title='---- 3 Trend Meters No Longer Align', message='3 Trend Meters No Longer Align - Trend Meter')
    RapidColorChangePositive = cast_bool(TrendBars3Positive) and (cast_bool(TrendBars3Negative[1]) or cast_bool(TrendBars3Negative[2]))
    RapidColorChangeNegative = cast_bool(TrendBars3Negative) and (cast_bool(TrendBars3Positive[1]) or cast_bool(TrendBars3Positive[2]))
    alertcondition(RapidColorChangePositive, title='All 3 TMs Rapid Change Red to Green', message='All 3 Trend Meters Rapid Change Red to Green - Trend Meter')
    alertcondition(RapidColorChangeNegative, title='All 3 TMs Rapid Change Green to Red', message='All 3 Trend Meters Rapid Change Green to Red - Trend Meter')
    alertcondition(RapidColorChangePositive or RapidColorChangeNegative, title='All 3 TMs Rapid Change to Same Color', message='All 3 Trend Meters Rapid Change to Same Color - Trend Meter')
    MaxValueMACrossUp = ta.crossover(ta.ema(Close, 5), ta.ema(Close, 11))
    MaxValueMACrossDown = ta.crossunder(ta.ema(Close, 5), ta.ema(Close, 11))
    TB1MACrossUp = ta.crossover(MA1, MA2)
    TB1MACrossDown = ta.crossunder(MA1, MA2)
    alertcondition(TB1MACrossUp, title='TB 1 Turns Green', message='Trend Bar 1 - Turns Green - Trend Meter')
    alertcondition(TB1MACrossDown, title='TB 1 Turns Red', message='Trend Bar 1 - Turns Red - Trend Meter')
    alertcondition(TB1MACrossUp or TB1MACrossDown, title='TB 1 Color Change', message='Trend Bar 1 - Color Change - Trend Meter')
    TB2MACrossUp = ta.crossover(MA3, MA4)
    TB2MACrossDown = ta.crossunder(MA3, MA4)
    alertcondition(TB2MACrossUp, title='TB 2 Turns Green', message='Trend Bar 2 - Turns Green - Trend Meter')
    alertcondition(TB2MACrossDown, title='TB 2 Turns Red', message='Trend Bar 2 - Turns Red - Trend Meter')
    alertcondition(TB2MACrossUp or TB2MACrossDown, title='TB 2 Color Change', message='Trend Bar 2 - Color Change - Trend Meter')
    TB1Green = MA1 > MA2
    TB1Red = MA1 < MA2
    TB2Green = MA3 > MA4
    TB2Red = MA3 < MA4
    TB12Green = TB1Green and TB2Green and (TB1MACrossUp or TB2MACrossUp)
    TB12Red = TB1Red and TB2Red and (TB1MACrossDown or TB2MACrossDown)
    alertcondition(TB12Green, title='TBs 1+2 Turn Green', message='Trend Bars 1+2 - Turn Green - Trend Meter')
    alertcondition(TB12Red, title='TBs 1+2 Turn Red', message='Trend Bars 1+2 - Turn Red - Trend Meter')
    alertcondition(TB12Green or TB12Red, title='TBs 1+2 Change to Same Color', message='Trend Bars 1+2 - Change to Same Color - MAs Crossing - Trend Meter')
    alertcondition(TB12Green and cast_bool(TrendBars3Positive), title='TBs 1+2 Turn Green with 3 TMs', message='Trend Bars 1+2 - Turn Green with 3 TMs - Trend Meter')
    alertcondition(TB12Red and cast_bool(TrendBars3Negative), title='TBs 1+2 Turn Red with 3 TMs', message='Trend Bars 1+2 - Turn Red with 3 TMs- Trend Meter')
    alertcondition(TB12Green and cast_bool(TrendBars3Positive) or (TB12Red and cast_bool(TrendBars3Negative)), title='TBs 1+2 Change to Same Color with 3 TMs', message='Trend Bars 1+2 - Change to Same Color with 3 TMs - Trend Meter')
    alertcondition(TB1Green and cast_bool(TrendBars3Positive), title='TB 1 Turns Green with 3 TMs', message='Trend Bar 1 - Turn Green with 3 TMs - Trend Meter')
    alertcondition(TB1Red and cast_bool(TrendBars3Negative), title='TB 1 Turns Red with 3 TMs', message='Trend Bar 1 - Turn Red with 3 TMs- Trend Meter')
    alertcondition(TB1Green and cast_bool(TrendBars3Positive) or (TB1Red and cast_bool(TrendBars3Negative)), title='TB 1 Change to Same Color with 3 TMs', message='Trend Bar 1 - Change to Same Color with 3 TMs - Trend Meter')
    alertcondition(TB2Green and cast_bool(TrendBars3Positive), title='TB 2 Turns Green with 3 TMs', message='Trend Bar 2 - Turn Green with 3 TMs - Trend Meter')
    alertcondition(TB2Red and cast_bool(TrendBars3Negative), title='TB 2 Turns Red with 3 TMs', message='Trend Bar 2 - Turn Red with 3 TMs- Trend Meter')
    alertcondition(TB2Green and cast_bool(TrendBars3Positive) or (TB2Red and cast_bool(TrendBars3Negative)), title='TB 2 Change to Same Color with 3 TMs', message='Trend Bar 2 - Change to Same Color with 3 TMs - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB1Green, title='3 TMs Turn Green with TB 1', message='All 3 Trend Meters Turn  Green with TB 1 - Trend Meter')
    alertcondition(BackgroundColorChangeNegative and TB1Red, title='3 TMs Turn Red with TB 1', message='All 3 Trend Meters Turn  Red with TB 1 - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB1Green or (BackgroundColorChangeNegative and TB1Red), title='3 TMs Change Color with TB 1', message='All 3 Trend Meters Change Color with TB 1 - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB2Green, title='3 TMs Turn Green with TB 2', message='All 3 Trend Meters Turn  Green with TB 2 - Trend Meter')
    alertcondition(BackgroundColorChangeNegative and TB2Red, title='3 TMs Turn Red with TB 2', message='All 3 Trend Meters Turn  Red with TB 2 - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB2Green or (BackgroundColorChangeNegative and TB2Red), title='3 TMs Change Color with TB 2', message='All 3 Trend Meters Change Color with TB 2 - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB1Green and TB2Green, title='3 TMs Turn Green with TBs 1+2', message='All 3 Trend Meters Turn  Green with Trend Bar 1+2 - Trend Meter')
    alertcondition(BackgroundColorChangeNegative and TB1Red and TB2Red, title='3 TMs Turn Red with TBs 1+2', message='All 3 Trend Meters Turn  Red with Trend Bar 1+2 - Trend Meter')
    alertcondition(BackgroundColorChangePositive and TB1Green and TB2Green or (BackgroundColorChangeNegative and TB1Red and TB2Red), title='3 TMs Change Color with TBs 1+2', message='All 3 Trend Meters Change Color with Trend Bar 1+2 - Trend Meter')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
