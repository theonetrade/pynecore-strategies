"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barstate, close, color, fill, high, input, label, low,
    math, na, nz, plot, request, script, size, string, syminfo, ta, text, timeframe, yloc
)
from pynecore.types import Label, Persistent, Series


@script.indicator(title='RS Rating', shorttitle='RS Rating', overlay=True, max_bars_back=253)
def main(
    hideRSRat=input(False, title='Hide Rating', group='RS Line'),
    ratingOnly=input(False, title='Rating Only', group='RS Line'),
    colorRS=input(color.rgb(0, 0, 255, 0), title='Color', group='RS Line', inline='a'),
    lineTicker=input('SP:SPX', title='Comparative Symbol for Line', group='Shape & Offset', tooltip='Reference ticker used for calculation of the RS Line.'),
    SpxValue=input(4200, title='Approximate Value of Comparative Symbol', group='Shape & Offset', tooltip='Used to gather a constant value'),
    offset=input.int(80, minval=0, maxval=2000, title='Offset (%)', group='Shape & Offset', tooltip='Used to display the RS Line under the price.'),
    plotNewHigh=input(True, title='Plot RS New Highs', group='RS Line New High'),
    rsNewHigh=input.string('RS New Highs', title='Type', options=('RS New Highs', 'RS New Highs Before Price', 'Historical RS New Highs', 'Historical RS New Highs  Before Price'), group='RS Line New High', inline='b'),
    blueDotCol=input(color.rgb(121, 213, 242, 62), title='Color', group='RS Line New High', inline='b'),
    lookback=input.int(250, title='Look-back', minval=1, maxval=252, group='RS Line New High', tooltip='The lookback for calculation of price and RS New Highs.', inline='b'),
    sizeLabHigh=input.string('Tiny', title='Size', options=('Tiny', 'Small', 'Normal', 'Large'), group='RS Line New High'),
    plotNewLow=input(False, title='Plot RS New Lows', group='RS Line New High'),
    rsNewLow=input.string('Historical RS New Lows', title='Type', options=('RS New Lows', 'RS New Lows Before Price', 'Historical RS New Lows', 'Historical RS New Lows  Before Price'), group='RS Line New High', inline='x'),
    redDotCol=input(color.rgb(255, 82, 82, 62), title='Color', group='RS Line New High', inline='x'),
    lookback2=input.int(250, title='Look-back', minval=1, maxval=252, group='RS Line New High', tooltip='The lookback for calculation of price and RS New Lows.', inline='x'),
    sizeLabLow=input.string('Tiny', title='Size', options=('Tiny', 'Small', 'Normal', 'Large'), group='RS Line New High'),
    boolMa=input(False, title='Display MA 1 on RS Line', group='1st MA on RS Line'),
    lenMa=input(21, title='Lenght Da', group='1st MA on RS Line', inline='c'),
    colMa=input(color.orange, title='Color', group='1st MA on RS Line', inline='c'),
    typMa=input.string('EMA', title='Type Da', options=('SMA', 'EMA'), group='1st MA on RS Line', inline='c'),
    lenMaWe=input(10, title='Lenght We', group='1st MA on RS Line', inline='c'),
    typMaWe=input.string('SMA', title='Type We', options=('SMA', 'EMA'), group='1st MA on RS Line', inline='c'),
    fillMa=input(False, title='Area Color', group='1st MA on RS Line'),
    posCol=input(color.rgb(0, 230, 119, 75), title='Positive Area', group='1st MA on RS Line', inline='d'),
    negCol=input(color.rgb(255, 82, 82, 75), title='Negative Area', group='1st MA on RS Line', inline='d'),
    boolMa2=input(False, title='Display MA 2 on RS Line', group='2nd MA on RS Line'),
    lenMa2=input(50, title='Lenght Da', group='2nd MA on RS Line', inline='c'),
    colMa2=input(color.red, title='Color', group='2nd MA on RS Line', inline='c'),
    typMa2=input.string('EMA', title='Type Da', options=('SMA', 'EMA'), group='2nd MA on RS Line', inline='c'),
    lenMa2We=input(21, title='Lenght We', group='2nd MA on RS Line', inline='c'),
    typMa2We=input.string('SMA', title='Type We', options=('SMA', 'EMA'), group='2nd MA on RS Line', inline='c'),
    allowReplay=input(False, title='Use fix values for replay mode', group='Replay mode (Approximate Method)', tooltip='Here we use constant values in order to provide the environment regardless of the date. See RSRATING ticker and report close values to have the last data.'),
    first2=input(195.93, title='For 99 stocks', group='Replay mode (Approximate Method)'),
    scnd2=input(117.11, title='For 90+ stocks', group='Replay mode (Approximate Method)'),
    thrd2=input(99.04, title='For 70+ stocks', group='Replay mode (Approximate Method)'),
    frth2=input(91.66, title='For 50+ stocks', group='Replay mode (Approximate Method)'),
    ffth2=input(80.96, title='For 30+ stocks', group='Replay mode (Approximate Method)'),
    sxth2=input(53.64, title='For 10+ stocks', group='Replay mode (Approximate Method)'),
    svth2=input(24.86, title='For 1- stocks', group='Replay mode (Approximate Method)')
):
    comparativeTickerId: str = 'SP:SPX'
    if lookback == 250 and timeframe.isweekly:
        lookback = 52
    if lookback2 == 250 and timeframe.isweekly:
        lookback2 = 52
    __block_result__ = na
    __switch__ = sizeLabHigh
    if __switch__ == 'Normal':
        __block_result__ = size.normal
    elif __switch__ == 'Tiny':
        __block_result__ = size.tiny
    elif __switch__ == 'Small':
        __block_result__ = size.small
    elif __switch__ == 'Large':
        __block_result__ = size.large
    highLabel = __block_result__
    __block_result_1__ = na
    __switch__ = sizeLabLow
    if __switch__ == 'Normal':
        __block_result_1__ = size.normal
    elif __switch__ == 'Tiny':
        __block_result_1__ = size.tiny
    elif __switch__ == 'Small':
        __block_result_1__ = size.small
    elif __switch__ == 'Large':
        __block_result_1__ = size.large
    lowLabel = __block_result_1__
    n63 = bar_index if bar_index < 63 else 63
    n126 = bar_index if bar_index < 126 else 126
    n189 = bar_index if bar_index < 189 else 189
    n252 = bar_index if bar_index < 252 else 252
    comparativeSymbol = request.security(lineTicker, timeframe.period, close)
    rsCurve = close / comparativeSymbol
    if syminfo.industry == 'Investment Trusts/Mutual Funds':
        offset = 90
    rsRatio = SpxValue * (offset - 10) / 100 if timeframe.isweekly else SpxValue * offset / 100
    rs = rsCurve * rsRatio
    prevlookback = lookback
    prevlookback2 = lookback2
    lookback = math.min(lookback - 1, bar_index)
    rsPlot = plot(rs, title='RS Line', style=plot.style_line, linewidth=1, color=colorRS)
    rsMA = ta.sma(rs, lenMa)
    if typMa == 'SMA' and (not timeframe.isweekly):
        rsMA = ta.sma(rs, lenMa)
    if typMa == 'EMA' and (not timeframe.isweekly):
        rsMA = ta.ema(rs, lenMa)
    if typMaWe == 'SMA' and timeframe.isweekly:
        rsMA = ta.sma(rs, lenMaWe)
    if typMaWe == 'EMA' and timeframe.isweekly:
        rsMA = ta.ema(rs, lenMaWe)
    maPlot = plot(rsMA if boolMa else na, color=colMa, linewidth=1)
    maPlot2 = plot(rsMA if boolMa and fillMa else na, color=color.rgb(0, 0, 0, 100), linewidth=1)
    fillCol = posCol if rs > rsMA else negCol
    fill(rsPlot, maPlot2, color=fillCol)
    rsMA2 = ta.sma(rs, lenMa2)
    if typMa2 == 'SMA' and (not timeframe.isweekly):
        rsMA2 = ta.sma(rs, lenMa2)
    if typMa2 == 'EMA' and (not timeframe.isweekly):
        rsMA2 = ta.ema(rs, lenMa2)
    if typMa2We == 'SMA' and timeframe.isweekly:
        rsMA2 = ta.sma(rs, lenMa2We)
    if typMa2We == 'EMA' and timeframe.isweekly:
        rsMA2 = ta.ema(rs, lenMa2We)
    maPlot3 = plot(rsMA2 if boolMa2 else na, color=colMa2, linewidth=1)
    newHigh: Persistent[Label] = na(Label)
    histNH = ta.highest(rs, prevlookback)
    histCl = ta.highest(high, prevlookback)
    if rsNewHigh == 'Historical RS New Highs' and plotNewHigh and (rs == histNH):
        newHigh = label.new(x=bar_index, y=rs, color=blueDotCol, style=label.style_circle, size=highLabel)
    if rsNewHigh == 'Historical RS New Highs  Before Price' and plotNewHigh and (rs == histNH) and (high < histCl):
        newHigh = label.new(x=bar_index, y=rs, color=blueDotCol, style=label.style_circle, size=highLabel)
    if barstate.islast and rsNewHigh == 'RS New Highs' and plotNewHigh and (rs == histNH):
        label.delete(newHigh)
        newHigh = label.new(x=bar_index, y=rs, color=blueDotCol, style=label.style_circle, size=highLabel)
    if barstate.islast and rsNewHigh == 'RS New Highs Before Price' and plotNewHigh and (rs == histNH) and (high < histCl):
        label.delete(newHigh)
        newHigh = label.new(x=bar_index, y=rs, color=blueDotCol, style=label.style_circle, size=highLabel)
    newLow: Persistent[Label] = na(Label)
    histNL = ta.lowest(rs, prevlookback2)
    histClL = ta.lowest(low, prevlookback2)
    if rsNewLow == 'Historical RS New Lows' and plotNewLow and (rs == histNL):
        newLow = label.new(x=bar_index, y=rs, color=redDotCol, style=label.style_circle, size=lowLabel)
    if rsNewLow == 'Historical RS New Lows  Before Price' and plotNewLow and (rs == histNL) and (low > histClL):
        newLow = label.new(x=bar_index, y=rs, color=redDotCol, style=label.style_circle, size=lowLabel)
    if barstate.islast and rsNewLow == 'RS New Lows' and plotNewLow and (rs == histNL):
        label.delete(newLow)
        newLow = label.new(x=bar_index, y=rs, color=redDotCol, style=label.style_circle, size=lowLabel)
    if barstate.islast and rsNewLow == 'RS New Lows Before Price' and plotNewLow and (rs == histNL) and (low > histClL):
        label.delete(newLow)
        newLow = label.new(x=bar_index, y=rs, color=redDotCol, style=label.style_circle, size=lowLabel)
    closeDa: Series = request.security(syminfo.tickerid, 'D', close)
    spxCloseDa: Series = request.security(comparativeTickerId, 'D', close)
    perfTicker63 = closeDa / closeDa[n63]
    perfTicker126 = closeDa / closeDa[n126]
    perfTicker189 = closeDa / closeDa[n189]
    perfTicker252 = closeDa / closeDa[n252]
    perfComp63 = spxCloseDa / spxCloseDa[n63]
    perfComp126 = spxCloseDa / spxCloseDa[n126]
    perfComp189 = spxCloseDa / spxCloseDa[n189]
    perfComp252 = spxCloseDa / spxCloseDa[n252]
    rs_stock: float = 0.4 * perfTicker63 + 0.2 * perfTicker126 + 0.2 * perfTicker189 + 0.2 * perfTicker252
    rs_ref: float = 0.4 * perfComp63 + 0.2 * perfComp126 + 0.2 * perfComp189 + 0.2 * perfComp252
    totalRsScore: float = rs_stock / rs_ref * 100
    totalRsRating: float = -1
    curveRsPerf: Series = request.seed('seed_fred6725_rs_rating', 'RSRATING', close)
    delta = ta.barssince(na(curveRsPerf) != True)
    different_values: Persistent[list[float]] = array.new_float(7)
    counter: Persistent[int] = 0
    first: float = 0
    scnd: float = 0
    thrd: float = 0
    frth: float = 0
    ffth: float = 0
    sxth: float = 0
    svth: float = 0
    if not allowReplay:
        for i in pine_range(delta, 34 + delta, 1):
            close_value = nz(curveRsPerf[i])
            if not array.includes(different_values, close_value) and counter < 7 and (close_value != 0):
                array.set(different_values, counter, close_value)
                counter = counter + 1
        first = array.get(different_values, 0)
        scnd = array.get(different_values, 1)
        thrd = array.get(different_values, 2)
        frth = array.get(different_values, 3)
        ffth = array.get(different_values, 4)
        sxth = array.get(different_values, 5)
        svth = array.get(different_values, 6)
    if allowReplay:
        first = first2
        scnd = scnd2
        thrd = thrd2
        frth = frth2
        ffth = ffth2
        sxth = sxth2
        svth = svth2
    if totalRsScore >= first:
        totalRsRating = 99
    if totalRsScore <= svth:
        totalRsRating = 1
    def f_attributePercentile(totalRsScore, tallerPerf, smallerPerf, rangeUp, rangeDn, weight):
        sum = totalRsScore + (totalRsScore - smallerPerf) * weight
        if sum > tallerPerf - 1:
            sum = tallerPerf - 1
        k1 = smallerPerf / rangeDn
        k2 = (tallerPerf - 1) / rangeUp
        k3 = (k1 - k2) / (tallerPerf - 1 - smallerPerf)
        RsRating = sum / (k1 - k3 * (totalRsScore - smallerPerf))
        if RsRating > rangeUp:
            RsRating = rangeUp
        if RsRating < rangeDn:
            RsRating = rangeDn
        return RsRating

    if totalRsScore < first and totalRsScore >= scnd:
        totalRsRating = f_attributePercentile(totalRsScore, first, scnd, 98, 90, 0.33)
    if totalRsScore < scnd and totalRsScore >= thrd:
        totalRsRating = f_attributePercentile(totalRsScore, scnd, thrd, 89, 70, 2.1)
    if totalRsScore < thrd and totalRsScore >= frth:
        totalRsRating = f_attributePercentile(totalRsScore, thrd, frth, 69, 50, 0)
    if totalRsScore < frth and totalRsScore >= ffth:
        totalRsRating = f_attributePercentile(totalRsScore, frth, ffth, 49, 30, 0)
    if totalRsScore < ffth and totalRsScore >= sxth:
        totalRsRating = f_attributePercentile(totalRsScore, ffth, sxth, 29, 10, 0)
    if totalRsScore < sxth and totalRsScore >= svth:
        totalRsRating = f_attributePercentile(totalRsScore, sxth, svth, 9, 2, 0)
    for i in pine_range(0, 6, 1):
        if nz(array.get(different_values, i)) == 0 and (not allowReplay):
            totalRsRating = -1
    isDaily = timeframe.isdaily
    labelText1: str = '                RS Rating'
    labelText2: str = ''
    if isDaily and totalRsRating != -1:
        labelText2 = '\n\n       ' + string.tostring(totalRsRating, '#0')
    if ratingOnly:
        labelText1 = ''
        labelText2 = '\n    ' + string.tostring(totalRsRating, '#0')
    label1: Series = label.new(bar_index, rs, text=labelText1, color=color.rgb(0, 0, 0, 100), size=size.normal, textcolor=colorRS, style=label.style_label_center, textalign=text.align_left, yloc=yloc.price) if hideRSRat == False and barstate.islast else na
    label2: Series = label.new(bar_index, rs, text=labelText2, color=color.rgb(0, 0, 0, 100), size=size.large, textcolor=colorRS, style=label.style_label_center, textalign=text.align_left, yloc=yloc.price) if hideRSRat == False and barstate.islast else na
    label.delete(label1[1])
    label.delete(label2[1])


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
