"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, display, extend,
    fill, high, hlc3, input, label, line, location, low, math, na, nz, plot, plotshape, polyline,
    request, scale, script, shape, size, string, syminfo, ta, ticker, timeframe, xloc
)
from pynecore.types import (
    Box, Color, Label, Line, NA, Persistent, PersistentSeries, Polyline,
    Series
)
from pynecore.types.chart import ChartPoint


@udt
class panel:
    tiValues: list[Box] = na(list)
    tiTitles: list[Label] = na(list)


display__ren__ = display.all - display.status_line
genericGroup: str = 'Generic Settings'
tfTTip: str = 'This option is utilized to calculate technical indicators for higher timeframes. If a timeframe lower than the chart\'s timeframe is selected, calculations will be based on the chart\'s timeframe.'
panel_Group: str = 'Indicators Sentiment Panel'
mrktOsc_Group: str = 'Market Sentiment Oscillator'
rsi_Group: str = 'Relative Strength Index Settings'
stoch_Group: str = 'Stochastic %K Settings'
stochRSI_Group: str = 'Stochastic RSI Fast Settings'
cci_Group: str = 'Commodity Channel Index Settings'
bbp_Group: str = 'Bull Bear Power Settings'
ma_Group: str = 'MA Settings'
vwap_Group: str = 'VWAP Settings'
bb_Group: str = 'Bollinger Bands Settings'
st_Group: str = 'Supertrend Settings'
lr_Group: str = 'Linear Regression Settings'
ms_Group: str = 'Market Structure Settings'
norm_Group: str = 'Normalization Settings - Trend Indicators'


@script.indicator('Market Sentiment Technicals [LuxAlgo]', 'LuxAlgo - Market Sentiment Technicals', True, scale=scale.none, na_bool=True)
def main(
    indi_tf=input.string('Chart', 'Timeframe', options=('Chart', '5 Minutes', '15 Minutes', '1 Hour', '4 Hours', '1 Day', '1 Week', '1 Month'), group=genericGroup, display=display__ren__, tooltip=tfTTip),
    hOffset=input.int(17, 'Horizontal Offset', minval=10, maxval=360, group=genericGroup, display=display__ren__),
    bullColor=input.color(color.new('#085DEF'), 'Gradient Colors: Bullish', inline='CSS', group=genericGroup),
    bearColor=input.color(color.new('#F10707'), 'Bearish', inline='CSS', group=genericGroup),
    panel_Show=input.bool(True, 'Indicators Sentiment Panel', group=panel_Group),
    panel_Height=input.int(3, '  Panel Height', minval=2, maxval=7, group=panel_Group, display=display__ren__),
    mrktMtr_Show=input.bool(True, 'Market Sentiment Meter', group='Market Sentiment Meter'),
    mrktOsc_Show=input.bool(True, 'Market Sentiment Oscillator', group=mrktOsc_Group),
    mrktOsc_Divergence=input.string('None', '  Show Divergence', options=('Regular', 'Hidden', 'All', 'None'), group=mrktOsc_Group, display=display__ren__),
    mrktOsc_lnWidth=input.int(1, '  Oscillator Line Width', minval=1, group=mrktOsc_Group, display=display__ren__),
    mrktOsc_height=input.float(3.5, '  Oscillator Height', minval=0, step=0.5, group=mrktOsc_Group, display=display__ren__),
    rsi_Source: Series[float] = input.source(close, '  Source', group=rsi_Group, display=display__ren__),
    rsi_Length=input.int(14, '  Length', minval=1, group=rsi_Group, display=display__ren__),
    stoch_LengthK=input.int(14, '  Stochastic %K Length', minval=1, group=stoch_Group, display=display__ren__),
    stoch_SmoothK=input.int(3, '  %K Smoothing', minval=1, group=stoch_Group, display=display__ren__),
    stochRSI_LengthK=input.int(14, '  Stochastic Length', minval=1, group=stochRSI_Group, display=display__ren__),
    stochRSI_SmoothK=input.int(3, '  %K Smoothing', minval=1, group=stochRSI_Group, display=display__ren__),
    stochRSI_SourceRSI: Series[float] = input.source(close, '  RSI Source', group=stochRSI_Group, display=display__ren__),
    stochRSI_LengthRSI=input.int(14, '  RSI Length', minval=1, group=stochRSI_Group, display=display__ren__),
    cci_Source: Series[float] = input.source(hlc3, '  Source', group=cci_Group, display=display__ren__),
    cci_Length=input.int(20, '  Length', minval=1, group=cci_Group, display=display__ren__),
    bbp_Length=input.int(13, '  Length', minval=1, group=bbp_Group, display=display__ren__),
    maType=input.string('SMA', '  Type', options=('SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'), group=ma_Group, display=display__ren__),
    maLength=input.int(20, '  Length', minval=1, group=ma_Group, display=display__ren__),
    vwapAnchor=input.string('Auto', '  Anchor', options=('Auto', 'Day', 'Week', 'Month', 'Quarter', 'Year'), group=vwap_Group, display=display__ren__),
    vwapStDev=input.float(2, '  StdDev', minval=1, group=vwap_Group, display=display__ren__),
    bb_Type=input.string('SMA', '  Basis Type', options=('SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA'), group=bb_Group, display=display__ren__),
    bb_Source: Series[float] = input.source(close, '  Source', group=bb_Group, display=display__ren__),
    bb_Length=input.int(20, '  Length', minval=1, group=bb_Group, display=display__ren__),
    bb_Mult=input.float(2.0, '  StdDev', minval=0.01, maxval=50, group=bb_Group, display=display__ren__),
    st_Period=input.int(10, '  ATR Length', minval=1, group=st_Group, display=display__ren__),
    st_Factor=input.float(3, '  Factor', minval=2, step=0.1, group=st_Group, display=display__ren__),
    lr_Source: Series[float] = input.source(close, '  Source', group=lr_Group, display=display__ren__),
    lr_Length=input.int(25, '  Length', minval=1, group=lr_Group, display=display__ren__),
    ms_Length=input.int(5, '  Length', minval=1, group=ms_Group, display=display__ren__),
    norm_Smooth=input.int(3, '  Smoothing', minval=1, group=norm_Group, display=display__ren__)
):
    meterLines: Persistent[list[Line]] = array.new_line()
    circulus: list[ChartPoint] = array.new(0, NA(ChartPoint))
    meterLabels: Persistent[list[Label]] = array.new_label()
    def timeframe__global__(timeframe__ren__):
        chartTFinM: float = timeframe.in_seconds() / 60
        __block_result__ = na
        if timeframe__ren__ == '5 Minutes' and chartTFinM <= 5:
            __block_result__ = '5'
        elif timeframe__ren__ == '15 Minutes' and chartTFinM <= 15:
            __block_result__ = '15'
        elif timeframe__ren__ == '1 Hour' and chartTFinM <= 60:
            __block_result__ = '60'
        elif timeframe__ren__ == '4 Hours' and chartTFinM <= 240:
            __block_result__ = '240'
        elif timeframe__ren__ == '1 Day' and timeframe.isintraday:
            __block_result__ = 'D'
        elif timeframe__ren__ == '1 Week' and (timeframe.isdaily or timeframe.isintraday):
            __block_result__ = 'W'
        elif timeframe__ren__ == '1 Month' and (timeframe.isweekly or timeframe.isdaily or timeframe.isintraday):
            __block_result__ = 'M'
        else:
            __block_result__ = timeframe.period
        return __block_result__

    def timeframeText(timeframe__ren__):
        timeframeX = timeframe__global__(timeframe__ren__)
        __block_result_1__ = na
        if not string.contains(timeframeX, 'D') and (not string.contains(timeframeX, 'W')) and (not string.contains(timeframeX, 'M')) and (not string.contains(timeframeX, 'S')):
            TFinNUM = string.tonumber(timeframeX)
            __block_result_2__ = na
            if TFinNUM < 60:
                __block_result_2__ = timeframeX + 'm'
            else:
                __block_result_2__ = string.tostring(TFinNUM / 60) + 'H'
            __block_result_1__ = __block_result_2__
        else:
            __block_result_1__ = timeframeX
        return __block_result_1__

    def autoAnchor(anchor):
        __block_result_3__ = na
        if anchor == 'Auto':
            __block_result_4__ = na
            if timeframe.isintraday:
                __block_result_4__ = 'D' if timeframe.multiplier <= 15 else 'W'
            elif timeframe.isdaily:
                __block_result_4__ = 'M'
            elif timeframe.isweekly:
                __block_result_4__ = '3M'
            elif timeframe.ismonthly:
                __block_result_4__ = '12M'
            __block_result_3__ = __block_result_4__
        elif anchor == 'Day':
            __block_result_3__ = 'D'
        elif anchor == 'Week':
            __block_result_3__ = 'W'
        elif anchor == 'Month':
            __block_result_3__ = 'M'
        elif anchor == 'Quarter':
            __block_result_3__ = '3M'
        elif anchor == 'Year':
            __block_result_3__ = '12M'
        return __block_result_3__

    def syminfo__global__(symbol):
        return string.substring(ticker.standard(symbol), string.pos(ticker.standard(symbol), ':') + 1) if symbol != '' else syminfo.ticker

    def interpolate(value, valueHigh, valueLow, rangeHigh, rangeLow):
        return rangeLow + (value - valueLow) * (rangeHigh - rangeLow) / (valueHigh - valueLow)

    def normalize(buy, sell, smooth):
        os: PersistentSeries[int] = 0
        max: Persistent[float] = na(float)
        min: Persistent[float] = na(float)
        os = 1 if buy else -1 if sell else os
        max = close if os > os[1] else max if os < os[1] else math.max(close, max)
        min = close if os < os[1] else min if os > os[1] else math.min(close, min)
        return ta.sma((close - min) / (max - min), smooth) * 100

    def movingAverageValue(source, length, maType):
        __block_result_5__ = na
        __switch__ = maType
        if __switch__ == 'SMA':
            __block_result_5__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result_5__ = ta.ema(source, length)
        elif __switch__ == 'HMA':
            __block_result_5__ = ta.hma(source, length)
        elif __switch__ == 'RMA':
            __block_result_5__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result_5__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result_5__ = ta.vwma(source, length)
        return __block_result_5__

    def rsi(source, length):
        rsi__0000006f__ = ta.rsi(source, length)
        __block_result_6__ = na
        if rsi__0000006f__ > 70:
            __block_result_6__ = interpolate(rsi__0000006f__, 100, 70, 100, 75)
        elif rsi__0000006f__ > 50:
            __block_result_6__ = interpolate(rsi__0000006f__, 70, 50, 75, 50)
        elif rsi__0000006f__ > 30:
            __block_result_6__ = interpolate(rsi__0000006f__, 50, 30, 50, 25)
        elif rsi__0000006f__ >= 0:
            __block_result_6__ = interpolate(rsi__0000006f__, 30, 0, 25, 0)
        return __block_result_6__

    @overload
    def stochastic(lengthK, smoothK):
        stoch = ta.sma(ta.stoch(close, high, low, lengthK), smoothK)
        __block_result_7__ = na
        if stoch > 80:
            __block_result_7__ = interpolate(stoch, 100, 80, 100, 75)
        elif stoch > 50:
            __block_result_7__ = interpolate(stoch, 80, 50, 75, 50)
        elif stoch > 20:
            __block_result_7__ = interpolate(stoch, 50, 20, 50, 25)
        elif stoch >= 0:
            __block_result_7__ = interpolate(stoch, 20, 0, 25, 0)
        return __block_result_7__

    @overload
    def stochastic(rsiSource, rsiLength, stochLengthK, stochSmoothK):
        rsi__00000086__ = ta.rsi(rsiSource, rsiLength)
        stoch = ta.sma(ta.stoch(rsi__00000086__, rsi__00000086__, rsi__00000086__, stochLengthK), stochSmoothK)
        __block_result_8__ = na
        if stoch > 80:
            __block_result_8__ = interpolate(stoch, 100, 80, 100, 75)
        elif stoch > 50:
            __block_result_8__ = interpolate(stoch, 80, 50, 75, 50)
        elif stoch > 20:
            __block_result_8__ = interpolate(stoch, 50, 20, 50, 25)
        elif stoch >= 0:
            __block_result_8__ = interpolate(stoch, 20, 0, 25, 0)
        return __block_result_8__

    def cci(source, length):
        ma = ta.sma(source, length)
        cci__00000091__ = (source - ma) / (0.015 * ta.dev(source, length))
        __block_result_9__ = na
        if cci__00000091__ > 100:
            __block_result_9__ = 100 if cci__00000091__ > 300 else interpolate(cci__00000091__, 300, 100, 100, 75)
        elif cci__00000091__ >= 0:
            __block_result_9__ = interpolate(cci__00000091__, 100, 0, 75, 50)
        elif cci__00000091__ < -100:
            __block_result_9__ = 0 if cci__00000091__ < -300 else interpolate(cci__00000091__, -100, -300, 25, 0)
        elif cci__00000091__ < 0:
            __block_result_9__ = interpolate(cci__00000091__, 0, -100, 50, 25)
        return __block_result_9__

    def bullBearPower(length):
        bbp = high + low - 2 * movingAverageValue(close, length, 'EMA')
        _, upper, lower = ta.bb(bbp, 100, 2)
        __block_result_10__ = na
        if bbp > upper:
            __block_result_10__ = 100 if bbp > 1.5 * upper else interpolate(bbp, 1.5 * upper, upper, 100, 75)
        elif bbp > 0:
            __block_result_10__ = interpolate(bbp, upper, 0, 75, 50)
        elif bbp < lower:
            __block_result_10__ = 0 if bbp < 1.5 * lower else interpolate(bbp, lower, 1.5 * lower, 25, 0)
        elif bbp < 0:
            __block_result_10__ = interpolate(bbp, 0, lower, 50, 25)
        return __block_result_10__

    def movingAverage(source, length, maType):
        basis = movingAverageValue(source, length, maType)
        return normalize(close > basis, close < basis, norm_Smooth)

    def bollingerBands(source, length, multiplier, maType):
        basis = movingAverageValue(source, length, maType)
        deviation = multiplier * ta.stdev(source, length)
        return normalize(close > basis + deviation, close < basis - deviation, norm_Smooth)

    def supertrend(factor, period):
        supertrend1, direction1 = ta.supertrend(factor, period)
        return normalize(close > supertrend1, close < supertrend1, norm_Smooth)

    def vwapBands(source, anchor, stdev):
        _, upper, lower = ta.vwap(source, timeframe.change(autoAnchor(anchor)), stdev)
        return normalize(close > upper, close < lower, norm_Smooth)

    def linearRegression(source, length):
        return 50 * ta.correlation(source, bar_index, length) + 50

    def marketStructure(length):
        ph_y: Persistent[float] = na(float)
        pl_y: Persistent[float] = na(float)
        ph_cross: Persistent[bool] = False
        pl_cross: Persistent[bool] = False
        bull: bool = False
        bear: bool = False
        ph = ta.pivothigh(length, length)
        pl = ta.pivotlow(length, length)
        if not na(ph):
            ph_y = ph
            ph_cross = False
        if not na(pl):
            pl_y = pl
            pl_cross = False
        if close > ph_y and (not ph_cross):
            ph_cross = True
            bull = True
        if close < pl_y and (not pl_cross):
            pl_cross = True
            bear = True
        return normalize(bull, bear, norm_Smooth)

    def collectData(timeframe__ren__):
        return request.security(syminfo.tickerid, timeframe__ren__, (close, rsi(rsi_Source, rsi_Length), stochastic(stoch_LengthK, stoch_SmoothK), stochastic(stochRSI_SourceRSI, stochRSI_LengthRSI, stochRSI_LengthK, stochRSI_SmoothK), cci(cci_Source, cci_Length), bullBearPower(bbp_Length), movingAverage(close, maLength, maType), vwapBands(close, vwapAnchor, vwapStDev), bollingerBands(bb_Source, bb_Length, bb_Mult, bb_Type), supertrend(st_Factor, st_Period), linearRegression(lr_Source, lr_Length), marketStructure(ms_Length)))

    def processData(show, timeframe__ren__, closeValue, rsiValue, stochValue, stochRSIValue, cciValue, bbpValue, maValue, vwapValue, bbValue, stValue, regValue, msValue, sentiment, offset, size__ren__):
        __block_result_11__ = na
        if show:
            tiPanel: Persistent[panel] = panel(array.new_box(na), array.new_label(na))
            if array.size(tiPanel.tiValues) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(tiPanel.tiValues) - 1):
                    i = __loop_2__.value
                    box.delete(array.shift(tiPanel.tiValues))
            if array.size(tiPanel.tiTitles) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(tiPanel.tiTitles) - 1):
                    i = __loop_2__.value
                    label.delete(array.shift(tiPanel.tiTitles))
            oscIndies = array.from_items(rsiValue, stochValue, stochRSIValue, cciValue, bbpValue)
            oscNames: list[str] = array.from_items('R\nS\nI', '%\nK', 'S\nT\nR\nS\nI', 'C\nC\nI', 'B\nB\nP')
            oscTitles: list[str] = array.from_items('Relative Strength Index (RSI)', 'Stochastic %K', 'Stochastic RSI %K', 'Commodity Channel Index', 'Bull Bear Power')
            trendIndies = array.from_items(maValue, vwapValue, bbValue, stValue, regValue, msValue)
            trendNames: list[str] = array.from_items('M\nA', 'V\nW\nA\nP', 'B\nB', 'S\nT', 'R\nE\nG', 'M\nS')
            trendTitles: list[str] = array.from_items(string.format('Moving Average ({0} {1})', maType, maLength), 'Volume Weighted Average Price', 'Bollinger Bands', 'Supertrend', 'Linear Regression', 'Market Structure')
            pSize = method_call('size', oscIndies) + method_call('size', trendIndies)
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + cast_int((3 * (pSize + 1) - 1) / 2), size__ren__ + offset + 0.5, syminfo__global__(syminfo.tickerid) + ' (' + string.tostring(closeValue) + ') · ' + timeframeText(timeframe__ren__), color=NA(Color), style=label.style_label_down, textcolor=chart.fg_color))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index, interpolate(75, 100, 0, size__ren__, 0) + offset, 'Overbought', color=NA(Color), style=label.style_label_right, textcolor=bullColor))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index, interpolate(50, 100, 0, size__ren__, 0) + offset, 'Neutral', color=NA(Color), style=label.style_label_right, textcolor=color.new('#787B86')))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index, interpolate(25, 100, 0, size__ren__, 0) + offset, 'Oversold', color=NA(Color), style=label.style_label_right, textcolor=bearColor))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + 3 * (pSize + 1), interpolate(75, 100, 0, size__ren__, 0) + offset, 'Strong Bullish Trend', color=NA(Color), style=label.style_label_left, textcolor=bullColor))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + 3 * (pSize + 1), interpolate(50, 100, 0, size__ren__, 0) + offset, 'Trendless', color=NA(Color), style=label.style_label_left, textcolor=color.new('#787B86')))
            array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + 3 * (pSize + 1), interpolate(25, 100, 0, size__ren__, 0) + offset, 'Strong Bearish Trend', color=NA(Color), style=label.style_label_left, textcolor=bearColor))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index - 1, offset + interpolate(75, 100, 0, size__ren__, 0), hOffset + bar_index + 3 * (pSize + 1), offset + interpolate(75, 100, 0, size__ren__, 0), color.new(bullColor, 50), bgcolor=bullColor))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index - 1, offset + interpolate(50, 100, 0, size__ren__, 0), hOffset + bar_index + 3 * (pSize + 1), offset + interpolate(50, 100, 0, size__ren__, 0), color.new(color.new('#787B86'), 50), bgcolor=color.new('#787B86')))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index - 1, offset + interpolate(25, 100, 0, size__ren__, 0), hOffset + bar_index + 3 * (pSize + 1), offset + interpolate(25, 100, 0, size__ren__, 0), color.new(bearColor, 50), bgcolor=bearColor))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index, offset + size__ren__ + 0.5, hOffset + bar_index + 3 * (pSize + 1) - 1, offset + size__ren__ + 0.25, color.new(color.new('#787B86'), 73), bgcolor=color.new(color.new('#787B86'), 83)))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index, offset + size__ren__ + 0.5, hOffset + bar_index + math.round((3 * (pSize + 1) - 1) * sentiment / 100), offset + size__ren__ + 0.25, color.new(chart.fg_color, 73), bgcolor=color.from_gradient(sentiment, 0, 100, bearColor, bullColor)))
            array.push(tiPanel.tiValues, box.new(hOffset + bar_index + 3 + 3 * method_call('size', oscIndies) - 2, offset + size__ren__ * 0.85, hOffset + bar_index + 3 + 3 * method_call('size', oscIndies) - 2, offset + size__ren__ * -0.2, color.new(color.new('#787B86'), 75), bgcolor=NA(Color)))
            for index, element in enumerate(oscIndies):
                array.push(tiPanel.tiValues, box.new(hOffset + bar_index + 3 * index, offset + interpolate(size__ren__ * 0.5, 1, 0, 1, 0), hOffset + bar_index + 3 * index + 2, offset + interpolate(size__ren__ * element, 100, 0, 1, 0), NA(Color), bgcolor=color.from_gradient(element, 0, 100, bearColor, bullColor)))
                array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + 3 * index + 1, offset, array.get(oscNames, index), color=NA(Color), size=size.tiny, style=label.style_label_up, textcolor=chart.fg_color, tooltip=array.get(oscTitles, index) + '\n Calculated Score: ' + string.tostring(element, '#.##')))
            __block_result_12__ = na
            for index, element in enumerate(trendIndies):
                array.push(tiPanel.tiValues, box.new(hOffset + bar_index + 3 + 3 * (method_call('size', oscIndies) + index), offset + size__ren__ * 0.5, hOffset + bar_index + 3 + 3 * (method_call('size', oscIndies) + index) + 2, offset + size__ren__ * (element - 0) / 100, NA(Color), bgcolor=color.from_gradient(element, 0, 100, bearColor, bullColor)))
                __block_result_12__ = array.push(tiPanel.tiTitles, label.new(hOffset + bar_index + 3 + 3 * (method_call('size', oscIndies) + index) + 1, offset, array.get(trendNames, index), color=NA(Color), size=size.tiny, style=label.style_label_up, textcolor=chart.fg_color, tooltip=array.get(trendTitles, index) + '\n Calculated Score: ' + string.tostring(element, '#.##')))
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    def scoreLeft(value):
        __block_result_13__ = na
        if value >= 48.5:
            __block_result_13__ = 13
        elif value >= 45.3:
            __block_result_13__ = 12
        elif value >= 45:
            __block_result_13__ = 11
        elif value >= 42:
            __block_result_13__ = 10
        elif value >= 38.63:
            __block_result_13__ = 9
        elif value >= 35.2:
            __block_result_13__ = 8
        elif value >= 33.3:
            __block_result_13__ = 7
        elif value >= 31.5:
            __block_result_13__ = 6
        elif value >= 27.5:
            __block_result_13__ = 5
        elif value >= 23.1:
            __block_result_13__ = 4
        elif value >= 20:
            __block_result_13__ = 3
        elif value >= 15.5:
            __block_result_13__ = 2
        elif value >= 0:
            __block_result_13__ = 1
        return __block_result_13__

    def scoreRight(value):
        __block_result_14__ = na
        if value < 51.6:
            __block_result_14__ = 0
        elif value < 54.75:
            __block_result_14__ = 1
        elif value < 55.5:
            __block_result_14__ = 2
        elif value < 58.1:
            __block_result_14__ = 3
        elif value < 61.39:
            __block_result_14__ = 4
        elif value < 64.8:
            __block_result_14__ = 5
        elif value < 66.5:
            __block_result_14__ = 6
        elif value < 68.6:
            __block_result_14__ = 7
        elif value < 72.53:
            __block_result_14__ = 8
        elif value < 76.3:
            __block_result_14__ = 9
        elif value < 78.8:
            __block_result_14__ = 10
        elif value < 82.5:
            __block_result_14__ = 11
        elif value < 90:
            __block_result_14__ = 12
        elif value <= 100:
            __block_result_14__ = 13
        return __block_result_14__

    def processMeter(show, sentiment):
        __block_result_15__ = na
        if show:
            radius: int = 13
            coefficient: float = 0.15
            base: float = 1.1
            index = bar_index
            degrees = -(sentiment - 100) * 9 / 5
            polylines: list[Polyline] = polyline.all
            if array.size(polylines) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(polylines) - 1):
                    i = __loop_2__.value
                    polyline.delete(array.shift(polylines))
            if array.size(meterLines) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(meterLines) - 1):
                    i = __loop_2__.value
                    line.delete(array.shift(meterLines))
            if array.size(meterLabels) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(meterLabels) - 1):
                    i = __loop_2__.value
                    label.delete(array.shift(meterLabels))
            for segment in pine_range(radius, 0, 1):
                array.push(circulus, chart.point.from_index(index - segment + hOffset + 17, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(segment, 2))))
                scoreLeft_1 = scoreLeft(sentiment)
                if sentiment >= 50 or radius - segment <= scoreLeft_1:
                    array.push(meterLines, line.new(index - segment + hOffset + 17, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(segment, 2)), index - segment + hOffset + 16, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(segment + 1, 2)), xloc.bar_index, extend.none, color.from_gradient(radius - segment, 0, 26, bearColor, bullColor), line.style_solid, 5))
            for segment in pine_range(radius, 0, 1):
                array.push(circulus, chart.point.from_index(index + radius - segment + hOffset + 17, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(radius - segment, 2))))
                scoreRight_1 = scoreRight(sentiment)
                if sentiment > 50 and radius - segment < scoreRight_1:
                    array.push(meterLines, line.new(index - segment + radius + hOffset + 17, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(radius - segment, 2)), index - segment + radius + hOffset + 18, base + coefficient * math.sqrt(math.pow(radius, 2) - math.pow(radius - segment + 1, 2)), xloc.bar_index, extend.none, color.from_gradient(2 * radius - segment - 1, 0, 26, bearColor, bullColor), line.style_solid, 5))
            polyline.new(circulus, False, False, line_color=color.new(chart.fg_color, 73), line_width=5)
            array.push(meterLines, line.new(index + hOffset + 17, base + coefficient, index + hOffset + 17 + math.round((radius - 3) * math.cos(math.toradians(degrees))), base + coefficient * (radius - 3) * math.sin(math.toradians(degrees)), xloc.bar_index, extend.none, color.new(chart.fg_color, 50), line.style_solid, 3))
            array.push(meterLines, line.new(index + hOffset + 17, base + coefficient, index + hOffset + 17 + math.round((radius - 3) * math.cos(math.toradians(degrees))), base + coefficient * (radius - 3) * math.sin(math.toradians(degrees)), xloc.bar_index, extend.none, color.new(chart.fg_color, 15), line.style_arrow_right, 1))
            array.push(meterLabels, label.new(index + hOffset + 17, base + coefficient, '', color=color.new(chart.fg_color, 15), style=label.style_circle, size=size.auto, tooltip=string.tostring(sentiment, '#.#')))
            array.push(meterLabels, label.new(index + hOffset + 17 + math.round(radius * math.cos(math.toradians(160))), base + coefficient * radius * math.sin(math.toradians(160)), 'Strong\nBearish', color=NA(Color), style=label.style_label_right, textcolor=bearColor if sentiment <= 20 else color.new('#787B86')))
            array.push(meterLabels, label.new(index + hOffset + 17 + math.round(radius * math.cos(math.toradians(130))), base + coefficient * radius * math.sin(math.toradians(130)), 'Bearish', color=NA(Color), style=label.style_label_lower_right, textcolor=bearColor if sentiment > 20 and sentiment <= 40 else color.new('#787B86')))
            array.push(meterLabels, label.new(index + hOffset + 17 + math.round(radius * math.cos(math.toradians(90))), base + coefficient * radius * math.sin(math.toradians(90)), 'Neutral', color=NA(Color), style=label.style_label_down, textcolor=chart.fg_color if sentiment > 40 and sentiment <= 60 else color.new('#787B86')))
            array.push(meterLabels, label.new(index + hOffset + 17 + math.round(radius * math.cos(math.toradians(50))), base + coefficient * radius * math.sin(math.toradians(50)), 'Bullish', color=NA(Color), style=label.style_label_lower_left, textcolor=bullColor if sentiment > 60 and sentiment <= 80 else color.new('#787B86')))
            __block_result_15__ = array.push(meterLabels, label.new(index + hOffset + 17 + math.round(radius * math.cos(math.toradians(20))), base + coefficient * radius * math.sin(math.toradians(20)), 'Strong\nBullish', color=NA(Color), style=label.style_label_left, textcolor=bullColor if sentiment > 80 else color.new('#787B86')))
        return __block_result_15__

    closeValue, rsiValue, stochValue, stochRSIValue, cciValue, bbpValue, maValue, vwapValue, bbValue, stValue, regValue, msValue = collectData(timeframe__global__(indi_tf))
    sentiment = math.avg(rsiValue, stochValue, stochRSIValue, cciValue, bbpValue, maValue, nz(vwapValue, 50), bbValue, stValue, regValue, msValue)
    if barstate.islast:
        processData(panel_Show, indi_tf, closeValue, rsiValue, stochValue, stochRSIValue, cciValue, bbpValue, maValue, nz(vwapValue, 50), bbValue, stValue, regValue, msValue, sentiment, 5.25 + panel_Height, panel_Height)
    processMeter(mrktMtr_Show and barstate.islast, sentiment)
    tiRank = plot(mrktOsc_height * sentiment / 100 if mrktOsc_Show else na, 'Oscillator', color.from_gradient(mrktOsc_height * sentiment, 0, mrktOsc_height * 100, bearColor, bullColor), math.max(1, mrktOsc_lnWidth), display=display__ren__)
    upperBand = plot(mrktOsc_height * 0.75 if mrktOsc_Show else na, 'Overbought Level', color.new(color.new('#787B86'), 63), display=display__ren__)
    midLine = plot(mrktOsc_height * 0.5 if mrktOsc_Show else na, 'Equilibrium Level', color.new(color.new('#787B86'), 63), display=display__ren__)
    lowerBand = plot(mrktOsc_height * 0.25 if mrktOsc_Show else na, 'Oversold Level', color.new(color.new('#787B86'), 63), display=display__ren__)
    fill(tiRank, midLine, mrktOsc_height * 1, mrktOsc_height * 0.5, top_color=color.new(bullColor, 0), bottom_color=color.new(bullColor, 100), title='Bullish Gradient Fill')
    fill(tiRank, midLine, mrktOsc_height * 0.5, mrktOsc_height * 0, top_color=color.new(bearColor, 100), bottom_color=color.new(bearColor, 0), title='Bearish Gradient Fill')
    __block_result_16__ = (na, na)
    __switch__ = mrktOsc_Divergence
    if __switch__ == 'All':
        __block_result_16__ = (True, True)
    elif __switch__ == 'Regular':
        __block_result_16__ = (True, False)
    elif __switch__ == 'Hidden':
        __block_result_16__ = (False, True)
    else:
        __block_result_16__ = (False, False)
    isRegular, isHidden = __block_result_16__
    osc: Series = mrktOsc_height * sentiment / 100
    lbR: int = 5
    lbL: int = 5
    rUpper: int = 60
    rLower: int = 5
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rLower <= bars and bars <= rUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = mrktOsc_Show and isRegular and priceLL and oscHL and plFound
    plot(osc[lbR] if plFound else na, 'Regular Bullish', bullColor if bullCond else NA(Color), 2, offset=-lbR, display=display__ren__)
    plotshape(osc[lbR] if bullCond else na, 'Regular Bullish Label', shape.labelup, location.absolute, color.new(bullColor, 0), -lbR, display=display__ren__)
    _inRange_2 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = mrktOsc_Show and isHidden and priceHL and oscLL and plFound
    plot(osc[lbR] if plFound else na, 'Hidden Bullish', color.new(bullColor, 73) if hiddenBullCond else NA(Color), 2, offset=-lbR, display=display__ren__)
    plotshape(osc[lbR] if hiddenBullCond else na, 'Hidden Bullish Label', shape.labelup, location.absolute, color.new(bullColor, 73), -lbR, display=display__ren__)
    _inRange_3 = _inRange(phFound[1])
    oscLH = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = mrktOsc_Show and isRegular and priceHH and oscLH and phFound
    plot(osc[lbR] if phFound else na, 'Regular Bearish', bearColor if bearCond else NA(Color), 2, offset=-lbR, display=display__ren__)
    plotshape(osc[lbR] if bearCond else na, 'Regular Bearish Label', shape.labeldown, location.absolute, color.new(bearColor, 0), -lbR, display=display__ren__)
    _inRange_4 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = mrktOsc_Show and isHidden and priceLH and oscHH and phFound
    plot(osc[lbR] if phFound else na, 'Hidden Bearish', color.new(bearColor, 73) if hiddenBearCond else NA(Color), 2, offset=-lbR, display=display__ren__)
    plotshape(osc[lbR] if hiddenBearCond else na, 'Hidden Bearish Label', shape.labeldown, location.absolute, color.new(bearColor, 73), -lbR, display=display__ren__)
    plot(5.25 + panel_Height + panel_Height + 0.5, color=na, editable=False)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
