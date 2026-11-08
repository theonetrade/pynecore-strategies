"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, bgcolor, close, color, input, location, math, na, plot, plotshape,
    script, shape, size, string, ta
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator(title='Ichimoku Oscillator', shorttitle='IO', explicit_plot_zorder=True, na_bool=True)
def main(
    conversionPeriods=input.int(8, minval=1, title='Conversion Line Length', group='Setup'),
    basePeriods=input.int(13, minval=1, title='Base Line Length', group='Setup'),
    laggingSpan2Periods=input.int(26, minval=1, title='Leading Span B Length', group='Setup'),
    displacement=input.int(13, minval=1, title='Lagging Span', group='Setup'),
    useatr=input.bool(defval=True, title='Use ATR', tooltip='Protection from Whipsaw', group='Setup'),
    atrlen=input.int(defval=9, title=' Length', minval=1, group='Setup'),
    atrmul=input.float(defval=2.0, title=' Mult', minval=0.1, step=0.1, group='Setup'),
    bounceoff=input.bool(defval=False, title='Bounce Off Support/Resistance', tooltip='Enables the Additional Entries when price bounce off Support/Resistance Zone', group='Setup'),
    useema=input.bool(defval=True, title='Show EMA', group='Setup'),
    emalen=input.int(defval=9, title=' Length', minval=1, group='Setup'),
    emacol=input.color(defval=color.new('#D1C4E9'), title=' Color', group='Setup'),
    emawd=input.int(defval=1, title=' Width', minval=1, maxval=5, group='Setup'),
    ematkpartprft=input.bool(defval=True, title='Take Partial Profit by EMA'),
    entexlongcol=input.color(defval=color.white, title='Entry/Exit Colors', inline='entcol', group='Colors'),
    entexshortcol=input.color(defval=color.yellow, title='', inline='entcol', group='Colors'),
    coloredbg=input.bool(defval=True, title='Colored Background', group='Colors'),
    bgcolupI=input.string(defval='Green', title=' Uptrend', options=('Green', 'Red', 'Blue'), group='Colors'),
    bgcoldnI=input.string(defval='Blue', title=' Downtrend', options=('Green', 'Red', 'Blue'), group='Colors'),
    bgtransp=input.int(defval=60, title=' Transparency', step=10, minval=0, maxval=100, group='Colors'),
    upcol1=input.color(defval=color.rgb(0, 250, 0, 0), title='Uptrend Colors', inline='upcols', group='Colors'),
    upcol2=input.color(defval=color.rgb(0, 190, 0, 0), title='', inline='upcols', group='Colors'),
    upcol3=input.color(defval=color.rgb(0, 130, 0, 0), title='', inline='upcols', group='Colors'),
    upcol4=input.color(defval=color.rgb(0, 70, 0, 0), title='', inline='upcols', group='Colors'),
    dbcol1=input.color(defval=color.rgb(250, 0, 0, 0), title='Downtrend Colors', inline='dbcols', group='Colors'),
    dbcol2=input.color(defval=color.rgb(190, 0, 0, 0), title='', inline='dbcols', group='Colors'),
    dbcol3=input.color(defval=color.rgb(130, 0, 0, 0), title='', inline='dbcols', group='Colors'),
    dbcol4=input.color(defval=color.rgb(70, 0, 0, 0), title='', inline='dbcols', group='Colors'),
    inSRcolor=input.color(defval=color.new('#D1D4DC'), title='In Support/Resistance Zone', group='Colors'),
    mainalert=input.bool(defval=True, title='Main Buy/Sell Alert', group='Alerts'),
    addalert=input.bool(defval=True, title='Additional Buy/Sell Alert', group='Alerts'),
    alertlongmsg=input.string(defval='Buy / Main, Close = close', title=' Long message', group='Alerts'),
    alertshortmsg=input.string(defval='Sell / Main, Close = close', title=' Short message', group='Alerts'),
    alertaddlongmsg=input.string(defval='Buy / Additonal, Close = close', title=' Long message', group='Alerts'),
    alertaddshortmsg=input.string(defval='Sell / Additonal, Close = close', title=' Short message', group='Alerts'),
    mainfrequency=input.string(defval=alert.freq_once_per_bar_close, title=' Frequency', options=(alert.freq_once_per_bar_close, alert.freq_once_per_bar), group='Alerts'),
    closealert=input.bool(defval=True, title='Close Position Alert', group='Alerts'),
    closepartalert=input.bool(defval=True, title='Take Partial Profit Alert', group='Alerts'),
    closemainmsg=input.string(defval='Close Position, Close = close', title=' Close Position Message', group='Alerts'),
    closepartmsg=input.string(defval='Take Partial Profit, Close = close', title=' Take Partial Profit Message', group='Alerts'),
    closefrequency=input.string(defval=alert.freq_once_per_bar, title=' Frequency', options=(alert.freq_once_per_bar_close, alert.freq_once_per_bar), group='Alerts')
):
    def donchian(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    conversionLine = donchian(conversionPeriods)
    baseLine = donchian(basePeriods)
    leadLine1: Series = math.avg(conversionLine, baseLine)
    leadLine2: Series = donchian(laggingSpan2Periods)
    mtrend: PersistentSeries[int] = 0
    trend: PersistentSeries[int] = 0
    cloudup = leadLine1 >= leadLine2
    clouddn = leadLine1 <= leadLine2
    CloudMin: Series = math.min(leadLine1[displacement - 1], leadLine2[displacement - 1])
    CloudMax: Series = math.max(leadLine1[displacement - 1], leadLine2[displacement - 1])
    inthecloud: Series = close >= CloudMin and close <= CloudMax
    mtrend = 1 if close > CloudMax else -1 if close < CloudMin else mtrend
    Oscline = close - CloudMin if mtrend == 1 else close - CloudMax
    Osccolor = inSRcolor if inthecloud else upcol1 if close > CloudMax else dbcol1
    Lagging = Oscline + (math.max(close - CloudMax[displacement - 1], 0) if mtrend == 1 else math.min(close - CloudMin[displacement - 1], 0))
    ConvBase = Lagging + (math.max(conversionLine - baseLine, 0) if mtrend == 1 else math.min(conversionLine - baseLine, 0))
    ConvBaseColor = upcol3 if conversionLine >= baseLine else dbcol3
    cloud = ConvBase + (math.max(leadLine1 - leadLine2, 0) if mtrend == 1 else math.min(leadLine1 - leadLine2, 0))
    change_1 = ta.change(baseLine)
    anyofthemrising = ta.change(conversionLine) > 0 or change_1 > 0
    change_2 = ta.change(baseLine)
    anyofthemfalling = ta.change(conversionLine) < 0 or change_2 < 0
    convoverbase = conversionLine >= baseLine
    baseoverconv = conversionLine <= baseLine
    tole = ta.atr(atrlen) * atrmul if useatr else 0
    entrylevel: Persistent[float] = na(float)
    if mtrend == 1:
        trend = 0 if mtrend[1] == -1 else trend
        if trend < 4 and close > CloudMax:
            trend = (1 if Lagging > Oscline else 0) + (1 if convoverbase and anyofthemrising else 0) + (1 if cloudup else 0) + 1
            if trend == 4:
                entrylevel = close
        else:
            trend = 0 if conversionLine < baseLine - tole else trend
    elif mtrend == -1:
        trend = 0 if mtrend[1] == 1 else trend
        if trend > -4 and close < CloudMin:
            trend = (-1 if Lagging < Oscline else 0) - (1 if baseoverconv and anyofthemfalling else 0) - (1 if clouddn else 0) - 1
            if trend == -4:
                entrylevel = close
        else:
            trend = 0 if conversionLine > baseLine + tole else trend
    uptmult = 159 + math.pow(trend, 3)
    dntmult = 159 - math.pow(trend, 3)
    bgcolup = color.rgb(uptmult if bgcolupI == 'Red' else 0, uptmult if bgcolupI == 'Green' else 0, uptmult if bgcolupI == 'Blue' else 0, bgtransp)
    bgcoldn = color.rgb(dntmult if bgcoldnI == 'Red' else 0, dntmult if bgcoldnI == 'Green' else 0, dntmult if bgcoldnI == 'Blue' else 0, bgtransp)
    bgcolor(color=(bgcolup if trend > 0 else bgcoldn if trend < 0 else inSRcolor) if coloredbg else na)
    plot(cloud, color=upcol4 if mtrend == 1 else dbcol4, style=plot.style_area)
    plot(ConvBase, color=ConvBaseColor, style=plot.style_area)
    plot(Lagging, color=upcol2 if close > CloudMax else dbcol2 if close < CloudMin else color.new(color.white, 100), style=plot.style_area)
    plot(Oscline, color=Osccolor, style=plot.style_area)
    def getClose(message):
        return string.replace(message, 'close', string.tostring(close))

    closetrade = ta.change(trend) != 0 and math.abs(trend[1]) == 4
    plotshape(cloud, color=(entexlongcol if trend[1] > 0 else entexshortcol) if closetrade else color.new(color.white, 100), style=shape.xcross, size=size.small, location=location.absolute)
    if closetrade and closealert:
        alert(getClose(closemainmsg), closefrequency)
    change_3 = ta.change(trend)
    uptrend = trend == 4 and change_3 != 0
    plotshape(0, color=entexlongcol if uptrend else color.new(color.white, 100), style=shape.triangleup, size=size.small, location=location.absolute)
    bouncbackup = bounceoff and trend == 4 and (close > CloudMax) and inthecloud[1]
    plotshape(0, color=entexlongcol if bouncbackup else color.new(color.white, 100), style=shape.triangleup, size=size.tiny, location=location.absolute)
    if trend == 4:
        if uptrend and mainalert:
            alert(getClose(alertlongmsg), mainfrequency)
        if bouncbackup and addalert:
            alert(getClose(alertaddlongmsg), mainfrequency)
    change_4 = ta.change(trend)
    downtrend = trend == -4 and change_4 != 0
    plotshape(0, color=entexshortcol if downtrend else color.new(color.white, 100), style=shape.triangledown, size=size.small, location=location.absolute)
    bouncbackdn = bounceoff and trend == -4 and (close < CloudMin) and inthecloud[1]
    plotshape(0, color=entexshortcol if bouncbackdn else color.new(color.white, 100), style=shape.triangledown, size=size.tiny, location=location.absolute)
    if trend == -4:
        if downtrend and mainalert:
            alert(getClose(alertshortmsg), mainfrequency)
        if bouncbackdn and addalert:
            alert(getClose(alertaddshortmsg), mainfrequency)
    emaline = ta.ema(cloud, emalen)
    plot(emaline, linewidth=math.max(1, emawd), color=emacol if useema else color.new(color.white, 100))
    convcrossbase = ta.crossover(conversionLine, baseLine)
    basecrosscons = ta.crossover(baseLine, conversionLine)
    emacrosscloud = ta.crossover(emaline, cloud)
    cloudcrossema = ta.crossover(cloud, emaline)
    profitable = trend == 4 and close > entrylevel or (trend == -4 and close < entrylevel)
    posexitcol = (entexlongcol if trend == 4 and basecrosscons else emacol if trend == 4 and emacrosscloud and ematkpartprft else entexshortcol if trend == -4 and convcrossbase else emacol if trend == -4 and cloudcrossema and ematkpartprft else color.new(color.white, 100)) if profitable else color.new(color.white, 100)
    plotshape(cloud, color=posexitcol, location=location.absolute, style=shape.xcross, size=size.tiny)
    partclose = trend == 4 and basecrosscons or (trend == 4 and emacrosscloud and ematkpartprft) or (trend == -4 and convcrossbase) or (trend == -4 and cloudcrossema and ematkpartprft)
    if partclose and closepartalert:
        alert(getClose(closepartmsg), closefrequency)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)