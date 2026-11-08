"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barmerge, barstate, close, color,
    high, hl2, input, low, math, na, nz, open, plot, request, script, syminfo, ta
)
from pynecore.types import NA, Series


@script.indicator('Bjorgum MTF MA', 'Bj Multi-MA', overlay=True, precision=3, na_bool=True)
def main(
    smooth=input.bool(True, 'Smooth', group='General Settings'),
    bar=input.bool(True, 'Bar Color', group='General Settings'),
    bartype=input.string('MA 1', 'Bar Color Type', group='General Settings', options=('MA 1', 'MA 2', 'MA 3', 'RSI 1', 'RSI 2', 'RSI 3'), tooltip='This selects what your bar color is based on'),
    maType1=input.string('EMA', 'MA Type #1', group='MA Type', options=('EMA', 'HEMA', 'SMA', 'HMA', 'WMA', 'DEMA', 'VWMA', 'VWAP', 'T3', 'IT')),
    maType2=input.string('EMA', 'MA Type #2', group='MA Type', options=('EMA', 'HEMA', 'SMA', 'HMA', 'WMA', 'DEMA', 'VWMA', 'VWAP', 'T3', 'IT')),
    maType3=input.string('EMA', 'MA Type #3', group='MA Type', options=('EMA', 'HEMA', 'SMA', 'HMA', 'WMA', 'DEMA', 'VWMA', 'VWAP', 'T3', 'IT')),
    maLength1=input.int(50, 'MA Length #1', group='MA Settings', minval=1),
    maLength2=input.int(0, 'MA Length #2', group='MA Settings', tooltip='Setting to zero disables the MA. Use 1,2 or 3 MA\'s'),
    maLength3=input.int(0, 'MA Length #3', group='MA Settings', tooltip='Setting to zero disables the MA. Use 1,2 or 3 MA\'s'),
    inp: Series[float] = input.source(hl2, 'Source', group='IT Trendline', tooltip='These two are inputs strcity pertaining to Ehlers Instantaneous Trendline (IT)'),
    alpha=input.float(0.07, 'Alpha', group='IT Trendline', minval=0.01),
    tf1=input.timeframe('', 'Timeframe 1', group='Resolution', tooltip='Go multi-time frame with each MA individually! This effects which time frame the RSI color is based from aswell'),
    tf2=input.timeframe('', 'Timeframe 2', group='Resolution', tooltip='Go multi-time frame with each MA individually! This effects which time frame the RSI color is based from aswell'),
    tf3=input.timeframe('', 'Timeframe 3', group='Resolution', tooltip='Go multi-time frame with each MA individually! This effects which time frame the RSI color is based from aswell'),
    rsiLen=input.int(14, 'RSI Length', group='Momentum', tooltip='RSI input is used for momrntum color schemes. Gievs a visual of momentum along with your trend'),
    colType1=input.string('MA', 'Color Type 1', group='MA Color Type', options=('RSI', 'MA'), tooltip='Choose color scheme. One is based on RSI value, the other a rising or falling MA'),
    colType2=input.string('MA', 'Color Type 2', group='MA Color Type', options=('RSI', 'MA'), tooltip='Choose color scheme. One is based on RSI value, the other a rising or falling MA'),
    colType3=input.string('MA', 'Color Type 3', group='MA Color Type', options=('RSI', 'MA'), tooltip='Choose color scheme. One is based on RSI value, the other a rising or falling MA'),
    maBull1=input.color(color.new('#64B5F6'), '', inline='1', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    maBear1=input.color(color.new('#EF5350'), '', inline='1', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    maBull2=input.color(color.new('#64B5F6'), '', inline='2', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    maBear2=input.color(color.new('#EF5350'), '', inline='2', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    maBull3=input.color(color.new('#64B5F6'), '', inline='3', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    maBear3=input.color(color.new('#EF5350'), '', inline='3', group='MA Color/ Transp/ Linewidth', tooltip='These select MA color if you\'ve chosen rising/ falling scheme'),
    transp1=input.int(0, '', inline='1', group='MA Color/ Transp/ Linewidth'),
    transp2=input.int(0, '', inline='2', group='MA Color/ Transp/ Linewidth'),
    transp3=input.int(0, '', inline='3', group='MA Color/ Transp/ Linewidth'),
    lineW1=input.int(1, '', inline='1', group='MA Color/ Transp/ Linewidth'),
    lineW2=input.int(1, '', inline='2', group='MA Color/ Transp/ Linewidth'),
    lineW3=input.int(1, '', inline='3', group='MA Color/ Transp/ Linewidth'),
    rsiBull1=input.color(color.new('#0000FF'), '', inline='a', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme'),
    rsiBear1=input.color(color.new('#FF0000'), '', inline='a', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme'),
    rsiBull2=input.color(color.new('#0000FF'), '', inline='b', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme'),
    rsiBear2=input.color(color.new('#FF0000'), '', inline='b', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme'),
    rsiBull3=input.color(color.new('#0000FF'), '', inline='c', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme'),
    rsiBear3=input.color(color.new('#FF0000'), '', inline='c', group='RSI Based Colors - Bull/ Bear', tooltip='These select MA color if you\'ve chosen momentum based scheme')
):
    def _haOpen():
        haClose: Series = (open + high + low + close) / 4
        haOpen: Series = NA(float)
        haOpen = (open + close) / 2 if na(haOpen[1]) else (nz(haOpen[1]) + nz(haClose[1])) / 2
        return haOpen

    def _NRP(tf, src: Series):
        return inline_series(request.security(syminfo.tickerid, tf, src[1 if barstate.isrealtime else 0], barmerge.gaps_on), 0 if barstate.isrealtime else 1)

    def _NRPrt(tf, src: Series):
        return inline_series(request.security(syminfo.tickerid, tf, src[1 if barstate.isrealtime else 0], barmerge.gaps_off), 0 if barstate.isrealtime else 1)

    def _itrend():
        __hist_inp__: Series[float] = inp[0]
        trend: Series[float] = 0.0
        trend = (inp + 2 * nz(__hist_inp__[1]) + nz(__hist_inp__[2])) / 4 if bar_index < 7 else (alpha - math.pow(alpha, 2) / 4) * inp + 0.5 * math.pow(alpha, 2) * nz(__hist_inp__[1]) - (alpha - 0.75 * math.pow(alpha, 2)) * nz(__hist_inp__[2]) + 2 * (1 - alpha) * nz(trend[1]) - math.pow(1 - alpha, 2) * nz(trend[2])
        trigger_ = 2 * trend - nz(trend[2])
        return (trend, trigger_)

    itrend, trigger = _itrend()
    HaOpen = _haOpen()
    def getMA(type, length):
        maPrice = ta.ema(close, length)
        if type == 'HEMA':
            maPrice = ta.ema(HaOpen, length)
        if type == 'SMA':
            maPrice = ta.sma(close, length)
        if type == 'HMA':
            maPrice = ta.hma(close, length)
        if type == 'WMA':
            maPrice = ta.wma(close, length)
        if type == 'VWMA':
            maPrice = ta.vwma(close, length)
        if type == 'VWAP':
            maPrice = ta.vwap
        if type == 'DEMA':
            e1 = ta.ema(close, length)
            e2 = ta.ema(e1, length)
            maPrice = 2 * e1 - e2
        if type == 'T3':
            axe1 = ta.ema(close, length)
            axe2 = ta.ema(axe1, length)
            axe3 = ta.ema(axe2, length)
            axe4 = ta.ema(axe3, length)
            axe5 = ta.ema(axe4, length)
            axe6 = ta.ema(axe5, length)
            ab: float = 0.7
            ac1 = -ab * ab * ab
            ac2 = 3 * ab * ab + 3 * ab * ab * ab
            ac3 = -6 * ab * ab - 3 * ab - 3 * ab * ab * ab
            ac4 = 1 + 3 * ab + ab * ab * ab + 3 * ab * ab
            maPrice = ac1 * axe6 + ac2 * axe5 + ac3 * axe4 + ac4 * axe3
        if type == 'IT':
            maPrice = itrend
        return maPrice

    rsi = ta.rsi(close, rsiLen)
    ma1: Series = getMA(maType1, maLength1)
    ma2: Series = getMA(maType2, 1 if maLength2 == 0 else maLength2)
    ma3: Series = getMA(maType3, 1 if maLength3 == 0 else maLength3)
    ma1step = _NRPrt(tf1, ma1)
    ma2step = _NRPrt(tf2, ma2)
    ma3step = _NRPrt(tf3, ma3)
    ma1smooth = _NRP(tf1, ma1)
    ma2smooth = _NRP(tf2, ma2)
    ma3smooth = _NRP(tf3, ma3)
    rsiMtf1 = _NRPrt(tf1, rsi)
    rsiMtf2 = _NRPrt(tf2, rsi)
    rsiMtf3 = _NRPrt(tf3, rsi)
    ma1Direc = ma1 >= ma1[1]
    ma2Direc = ma2 >= ma2[1]
    ma3Direc = ma3 >= ma3[1]
    ma1MtfDirec = _NRPrt(tf1, ma1Direc)
    ma2MtfDirec = _NRPrt(tf2, ma2Direc)
    ma3MtfDirec = _NRPrt(tf3, ma3Direc)
    ma1Con = ma1Direc if tf1 == '' else ma1MtfDirec
    ma2Con = ma2Direc if tf2 == '' else ma2MtfDirec
    ma3Con = ma3Direc if tf3 == '' else ma3MtfDirec
    maMtf1 = ma1smooth if smooth else ma1step
    maMtf2 = ma2smooth if smooth else ma2step
    maMtf3 = ma3smooth if smooth else ma3step
    plotMa1 = ma1 if tf1 == '' else maMtf1
    plotMa2 = ma2 if tf2 == '' else maMtf2
    plotMa3 = ma3 if tf3 == '' else maMtf3
    rsi1 = rsi if tf1 == '' else rsiMtf1
    rsi2 = rsi if tf2 == '' else rsiMtf2
    rsi3 = rsi if tf3 == '' else rsiMtf3
    ma1Bar = close >= plotMa1 if tf1 == '' else close >= ma1step
    ma2Bar = close >= plotMa2 if tf2 == '' else close >= ma2step
    ma3Bar = close >= plotMa3 if tf3 == '' else close >= ma3step
    rsi1col = color.from_gradient(rsi1, 30, 70, rsiBear1, rsiBull1)
    rsi2col = color.from_gradient(rsi2, 30, 70, rsiBear2, rsiBull2)
    rsi3col = color.from_gradient(rsi3, 30, 70, rsiBear3, rsiBull3)
    ma1Col = (maBull1 if ma1Con else maBear1) if colType1 == 'MA' else rsi1col
    ma2Col = (maBull2 if ma2Con else maBear2) if colType2 == 'MA' else rsi2col
    ma3Col = (maBull3 if ma3Con else maBear3) if colType3 == 'MA' else rsi3col
    barColor = (maBull1 if ma1Bar else maBear1) if bartype == 'MA 1' else (maBull2 if ma2Bar else maBear2) if bartype == 'MA 2' else (maBull3 if ma3Bar else maBear3) if bartype == 'MA 3' else rsi1col if bartype == 'RSI 1' else rsi2col if bartype == 'RSI 2' else rsi3col if bartype == 'RSI 3' else na
    plotMA2 = plotMa2 if maType2 == 'IT' else na if maLength2 == 0 else plotMa2
    plotMA3 = plotMa3 if maType3 == 'IT' else na if maLength3 == 0 else plotMa3
    barcolor(barColor if bar else na)
    plot(plotMa1, 'Moving Average #1', color.new(ma1Col, transp1), linewidth=math.max(1, lineW1))
    plot(plotMA2, 'Moving Average #2', color.new(ma2Col, transp2), linewidth=math.max(1, lineW2))
    plot(plotMA3, 'Moving Average #3', color.new(ma3Col, transp3), linewidth=math.max(1, lineW3))
    maSig1 = ma1 if tf1 == '' else ma1step
    maSig2 = ma2 if tf2 == '' else ma2step
    maSig3 = ma3 if tf3 == '' else ma3step
    maCrossUp1 = ta.crossover(close, maSig1)
    maCrossDn1 = ta.crossunder(close, maSig1)
    maCrossUp2 = ta.crossover(close, maSig2)
    maCrossDn2 = ta.crossunder(close, maSig2)
    maCrossUp3 = ta.crossover(close, maSig3)
    maCrossDn3 = ta.crossunder(close, maSig3)
    ma1CrossUp2 = ta.crossover(maSig1, maSig2)
    ma1CrossDn2 = ta.crossunder(maSig1, maSig2)
    ma1CrossUp3 = ta.crossover(maSig1, maSig3)
    ma1CrossDn3 = ta.crossunder(maSig1, maSig3)
    ma2CrossUp3 = ta.crossover(maSig2, maSig3)
    ma2CrossDn3 = ta.crossunder(maSig2, maSig3)
    alertcondition(maCrossUp1, 'Close crossed above MA 1', 'Close crossed above MA 1 on {{interval}} chart. Price is {{close}}')
    alertcondition(maCrossDn1, 'Close crossed below MA 1', 'Close crossed below MA 1 on {{interval}} chart. Price is {{close}}')
    alertcondition(maCrossUp2, 'Close crossed above MA 2', 'Close crossed above MA 2 on {{interval}} chart. Price is {{close}}')
    alertcondition(maCrossDn2, 'Close crossed below MA 2', 'Close crossed below MA 2 on {{interval}} chart. Price is {{close}}')
    alertcondition(maCrossUp3, 'Close crossed above MA 3', 'Close crossed above MA 3 on {{interval}} chart. Price is {{close}}')
    alertcondition(maCrossDn3, 'Close crossed below MA 3', 'Close crossed below MA 3 on {{interval}} chart. Price is {{close}}')
    alertcondition(ma1CrossUp2, 'MA 1 crossed above MA 2', "MA 1 crossed above MA 2 on {{interval}} chart. Price is {{close}}'")
    alertcondition(ma1CrossDn2, 'MA 1 crossed below MA 2', "MA 1 crossed below MA 2 on {{interval}} chart. Price is {{close}}'")
    alertcondition(ma1CrossUp3, 'MA 1 crossed above MA 3', "MA 1 crossed above MA 3 on {{interval}} chart. Price is {{close}}'")
    alertcondition(ma1CrossDn3, 'MA 1 crossed below MA 3', "MA 1 crossed below MA 3 on {{interval}} chart. Price is {{close}}'")
    alertcondition(ma2CrossUp3, 'MA 2 crossed above MA 3', "MA 2 crossed above MA 3 on {{interval}} chart. Price is {{close}}'")
    alertcondition(ma2CrossDn3, 'MA 2 crossed below MA 3', "MA 2 crossed below MA 3 on {{interval}} chart. Price is {{close}}'")


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
