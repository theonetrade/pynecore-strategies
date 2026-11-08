"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barcolor, close, color, high, input, low, na, plot, script, ta


@script.indicator('Stochastic Heat Map', shorttitle='SHM', overlay=False, na_bool=True)
def main(
    MA=input.string(title='MA', options=('SMA', 'EMA', 'WMA'), defval='EMA'),
    Theme=input.string(title='Theme', options=('Theme 1', 'Theme 2', 'Theme 3'), defval='Theme 3'),
    inc=input(title='Increment', defval=10),
    smooth=input(title='Smooth Fast', defval=2),
    smoothSlow=input(title='Smooth Slow', defval=21),
    plotNumber=input.int(title='Plot Number', defval=28, minval=1, maxval=28),
    PaintBars=input(title='Paint Bars', defval=True),
    IncType=input(title='Waves', defval=False)
):
    _source = close
    trans: int = 0
    cp1 = color.new(color.new('#01FF00'), trans)
    cp2 = color.new(color.new('#05D904'), trans)
    cp3 = color.new(color.new('#04B504'), trans)
    cp4 = color.new(color.new('#039103'), trans)
    cp5 = color.new(color.new('#027502'), trans)
    cn1 = color.new(color.new('#FF0505'), trans)
    cn2 = color.new(color.new('#D60606'), trans)
    cn3 = color.new(color.new('#B80606'), trans)
    cn4 = color.new(color.new('#910303'), trans)
    cn5 = color.new(color.new('#750202'), trans)
    cp6 = color.new(color.new('#00DDFF'), trans)
    cp7 = color.new(color.new('#04BCD9'), trans)
    cp8 = color.new(color.new('#049CB3'), trans)
    cp9 = color.new(color.new('#047F91'), trans)
    cp10 = color.new(color.new('#046775'), trans)
    cn6 = color.new(color.new('#D800FF'), trans)
    cn7 = color.new(color.new('#BB04DB'), trans)
    cn8 = color.new(color.new('#9B05B5'), trans)
    cn9 = color.new(color.new('#7B038F'), trans)
    cn10 = color.new(color.new('#640275'), trans)
    cp11 = color.new(color.new('#CF0000'), trans)
    cp12 = color.new(color.new('#F25811'), trans)
    cp13 = color.new(color.new('#F29811'), trans)
    cp14 = color.new(color.new('#EEF211'), trans)
    cp15 = color.new(color.new('#3AF211'), trans)
    cn11 = color.new(color.new('#02269E'), trans)
    cn12 = color.new(color.new('#0F44F5'), trans)
    cn13 = color.new(color.new('#1176F2'), trans)
    cn14 = color.new(color.new('#0093C9'), trans)
    cn15 = color.new(color.new('#11E7F2'), trans)
    fc1 = color.new(color.white, 0)
    sc1 = color.new(color.silver, 0)
    fc2 = color.new(color.white, 0)
    sc2 = color.new(color.blue, 0)
    fc3 = color.new(color.white, 0)
    sc3 = color.new(color.orange, 0)
    fastColour = fc1 if Theme == 'Theme 1' else fc2 if Theme == 'Theme 2' else fc3
    slowColour = sc1 if Theme == 'Theme 1' else sc2 if Theme == 'Theme 2' else sc3
    pColour1 = cp1 if Theme == 'Theme 1' else cp6 if Theme == 'Theme 2' else cp11
    pColour2 = cp2 if Theme == 'Theme 1' else cp7 if Theme == 'Theme 2' else cp12
    pColour3 = cp3 if Theme == 'Theme 1' else cp8 if Theme == 'Theme 2' else cp13
    pColour4 = cp4 if Theme == 'Theme 1' else cp9 if Theme == 'Theme 2' else cp14
    pColour5 = cp5 if Theme == 'Theme 1' else cp10 if Theme == 'Theme 2' else cp15
    nColour1 = cn1 if Theme == 'Theme 1' else cn6 if Theme == 'Theme 2' else cn11
    nColour2 = cn2 if Theme == 'Theme 1' else cn7 if Theme == 'Theme 2' else cn12
    nColour3 = cn3 if Theme == 'Theme 1' else cn8 if Theme == 'Theme 2' else cn13
    nColour4 = cn4 if Theme == 'Theme 1' else cn9 if Theme == 'Theme 2' else cn14
    nColour5 = cn5 if Theme == 'Theme 1' else cn10 if Theme == 'Theme 2' else cn15
    def getColour(a):
        __block_result__ = na
        if a >= 90:
            __block_result__ = pColour1
        else:
            __block_result_1__ = na
            if a >= 80:
                __block_result_1__ = pColour2
            else:
                __block_result_2__ = na
                if a >= 70:
                    __block_result_2__ = pColour3
                else:
                    __block_result_3__ = na
                    if a >= 60:
                        __block_result_3__ = pColour4
                    else:
                        __block_result_4__ = na
                        if a >= 50:
                            __block_result_4__ = pColour5
                        else:
                            __block_result_5__ = na
                            if a >= 40:
                                __block_result_5__ = nColour5
                            else:
                                __block_result_6__ = na
                                if a >= 30:
                                    __block_result_6__ = nColour4
                                else:
                                    __block_result_7__ = na
                                    if a >= 20:
                                        __block_result_7__ = nColour3
                                    else:
                                        __block_result_8__ = na
                                        if a >= 10:
                                            __block_result_8__ = nColour2
                                        else:
                                            __block_result_9__ = na
                                            if a >= 0:
                                                __block_result_9__ = nColour1
                                            __block_result_8__ = __block_result_9__
                                        __block_result_7__ = __block_result_8__
                                    __block_result_6__ = __block_result_7__
                                __block_result_5__ = __block_result_6__
                            __block_result_4__ = __block_result_5__
                        __block_result_3__ = __block_result_4__
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def getStoch(i, incr):
        c = i * inc
        s = smooth + incr
        __block_result_10__ = na
        if MA == 'SMA':
            __block_result_10__ = ta.sma(ta.stoch(_source, high, low, c), s)
        else:
            __block_result_11__ = na
            if MA == 'EMA':
                __block_result_11__ = ta.ema(ta.stoch(_source, high, low, c), s)
            else:
                __block_result_12__ = na
                if MA == 'WMA':
                    __block_result_12__ = ta.wma(ta.stoch(_source, high, low, c), s)
                __block_result_11__ = __block_result_12__
            __block_result_10__ = __block_result_11__
        return __block_result_10__

    stoch1 = getStoch(1 if IncType else 1, 1 if IncType else 0) if plotNumber > 0 else 0
    stoch2 = getStoch(2 if IncType else 2, 2 if IncType else 0) if plotNumber > 1 else 0
    stoch3 = getStoch(3 if IncType else 3, 3 if IncType else 0) if plotNumber > 2 else 0
    stoch4 = getStoch(4 if IncType else 4, 4 if IncType else 0) if plotNumber > 3 else 0
    stoch5 = getStoch(5 if IncType else 5, 5 if IncType else 0) if plotNumber > 4 else 0
    stoch6 = getStoch(6 if IncType else 6, 6 if IncType else 0) if plotNumber > 5 else 0
    stoch7 = getStoch(7 if IncType else 7, 7 if IncType else 0) if plotNumber > 6 else 0
    stoch8 = getStoch(8 if IncType else 8, 8 if IncType else 0) if plotNumber > 7 else 0
    stoch9 = getStoch(9 if IncType else 9, 9 if IncType else 0) if plotNumber > 8 else 0
    stoch10 = getStoch(10 if IncType else 10, 10 if IncType else 0) if plotNumber > 9 else 0
    stoch11 = getStoch(15 if IncType else 11, 11 if IncType else 0) if plotNumber > 10 else 0
    stoch12 = getStoch(20 if IncType else 12, 12 if IncType else 0) if plotNumber > 11 else 0
    stoch13 = getStoch(25 if IncType else 13, 13 if IncType else 0) if plotNumber > 12 else 0
    stoch14 = getStoch(30 if IncType else 14, 14 if IncType else 0) if plotNumber > 13 else 0
    stoch15 = getStoch(35 if IncType else 15, 15 if IncType else 0) if plotNumber > 14 else 0
    stoch16 = getStoch(40 if IncType else 16, 16 if IncType else 0) if plotNumber > 15 else 0
    stoch17 = getStoch(45 if IncType else 17, 17 if IncType else 0) if plotNumber > 16 else 0
    stoch18 = getStoch(50 if IncType else 18, 18 if IncType else 0) if plotNumber > 17 else 0
    stoch19 = getStoch(55 if IncType else 19, 19 if IncType else 0) if plotNumber > 18 else 0
    stoch20 = getStoch(60 if IncType else 20, 20 if IncType else 0) if plotNumber > 19 else 0
    stoch21 = getStoch(70 if IncType else 21, 21 if IncType else 0) if plotNumber > 20 else 0
    stoch22 = getStoch(80 if IncType else 22, 22 if IncType else 0) if plotNumber > 21 else 0
    stoch23 = getStoch(90 if IncType else 23, 23 if IncType else 0) if plotNumber > 22 else 0
    stoch24 = getStoch(100 if IncType else 24, 24 if IncType else 0) if plotNumber > 23 else 0
    stoch25 = getStoch(110 if IncType else 25, 25 if IncType else 0) if plotNumber > 24 else 0
    stoch26 = getStoch(120 if IncType else 26, 26 if IncType else 0) if plotNumber > 25 else 0
    stoch27 = getStoch(140 if IncType else 27, 27 if IncType else 0) if plotNumber > 26 else 0
    stoch28 = getStoch(160 if IncType else 28, 28 if IncType else 0) if plotNumber > 27 else 0
    colour1 = getColour(stoch1)
    colour2 = getColour(stoch2)
    colour3 = getColour(stoch3)
    colour4 = getColour(stoch4)
    colour5 = getColour(stoch5)
    colour6 = getColour(stoch6)
    colour7 = getColour(stoch7)
    colour8 = getColour(stoch8)
    colour9 = getColour(stoch9)
    colour10 = getColour(stoch10)
    colour11 = getColour(stoch11)
    colour12 = getColour(stoch12)
    colour13 = getColour(stoch13)
    colour14 = getColour(stoch14)
    colour15 = getColour(stoch15)
    colour16 = getColour(stoch16)
    colour17 = getColour(stoch17)
    colour18 = getColour(stoch18)
    colour19 = getColour(stoch19)
    colour20 = getColour(stoch20)
    colour21 = getColour(stoch21)
    colour22 = getColour(stoch22)
    colour23 = getColour(stoch23)
    colour24 = getColour(stoch24)
    colour25 = getColour(stoch25)
    colour26 = getColour(stoch26)
    colour27 = getColour(stoch27)
    colour28 = getColour(stoch28)
    getAverage = (stoch1 + stoch2 + stoch3 + stoch4 + stoch5 + stoch6 + stoch7 + stoch8 + stoch9 + stoch10 + stoch11 + stoch12 + stoch13 + stoch14 + stoch15 + stoch16 + stoch17 + stoch18 + stoch19 + stoch20 + stoch21 + stoch22 + stoch23 + stoch24 + stoch25 + stoch26 + stoch27 + stoch28) / plotNumber
    fast = getAverage / 100 * plotNumber
    slow = ta.sma(fast, smoothSlow) if MA == 'SMA' else ta.ema(fast, smoothSlow) if MA == 'EMA' else ta.wma(fast, smoothSlow)
    barColour = getColour(getAverage)
    plot1 = plot(0 if plotNumber > 0 else na, color=colour1, linewidth=1)
    plot2 = plot(1 if plotNumber > 1 else na, color=colour2, linewidth=1)
    plot3 = plot(2 if plotNumber > 2 else na, color=colour3, linewidth=1)
    plot4 = plot(3 if plotNumber > 3 else na, color=colour4, linewidth=1)
    plot5 = plot(4 if plotNumber > 4 else na, color=colour5, linewidth=1)
    plot6 = plot(5 if plotNumber > 5 else na, color=colour6, linewidth=1)
    plot7 = plot(6 if plotNumber > 6 else na, color=colour7, linewidth=1)
    plot8 = plot(7 if plotNumber > 7 else na, color=colour8, linewidth=1)
    plot9 = plot(8 if plotNumber > 8 else na, color=colour9, linewidth=1)
    plot10 = plot(9 if plotNumber > 9 else na, color=colour10, linewidth=1)
    plot11 = plot(10 if plotNumber > 10 else na, color=colour11, linewidth=1)
    plot12 = plot(11 if plotNumber > 11 else na, color=colour12, linewidth=1)
    plot13 = plot(12 if plotNumber > 12 else na, color=colour13, linewidth=1)
    plot14 = plot(13 if plotNumber > 13 else na, color=colour14, linewidth=1)
    plot15 = plot(14 if plotNumber > 14 else na, color=colour15, linewidth=1)
    plot16 = plot(15 if plotNumber > 15 else na, color=colour16, linewidth=1)
    plot17 = plot(16 if plotNumber > 16 else na, color=colour17, linewidth=1)
    plot18 = plot(17 if plotNumber > 17 else na, color=colour18, linewidth=1)
    plot19 = plot(18 if plotNumber > 18 else na, color=colour19, linewidth=1)
    plot20 = plot(19 if plotNumber > 19 else na, color=colour20, linewidth=1)
    plot21 = plot(20 if plotNumber > 20 else na, color=colour21, linewidth=1)
    plot22 = plot(21 if plotNumber > 21 else na, color=colour22, linewidth=1)
    plot23 = plot(22 if plotNumber > 22 else na, color=colour23, linewidth=1)
    plot24 = plot(23 if plotNumber > 23 else na, color=colour24, linewidth=1)
    plot25 = plot(24 if plotNumber > 24 else na, color=colour25, linewidth=1)
    plot26 = plot(25 if plotNumber > 25 else na, color=colour26, linewidth=1)
    plot27 = plot(26 if plotNumber > 26 else na, color=colour27, linewidth=1)
    plot28 = plot(27 if plotNumber > 27 else na, color=colour28, linewidth=1)
    plot29 = plot(plotNumber, color=colour28, linewidth=1)
    plot(slow, color=slowColour, linewidth=1, style=plot.style_line)
    plot(fast, color=fastColour, linewidth=1, style=plot.style_line)
    barcolor(barColour if PaintBars else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)