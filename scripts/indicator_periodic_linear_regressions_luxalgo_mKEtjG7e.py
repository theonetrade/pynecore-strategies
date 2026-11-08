"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, close, color, fill, input, last_bar_index,
    line, math, na, plot, script, string, table, timeframe
)
from pynecore.types import Color, Line, NA, Persistent, Series


@script.indicator('Periodic Linear Regressions [LuxAlgo]', shorttitle='LuxAlgo - Periodic Linear Regressions', max_lines_count=500, overlay=True)
def main(
    choice=input.string('Rolling', 'Method', options=('Static', 'Rolling')),
    anchor=input.string('Periodic', 'Anchor Type', options=('Periodic', 'First Bar'), tooltip='\'First Bar\' -> Choice: \'Rolling\' '),
    res=input.timeframe('W', 'Anchor Period'),
    src: Series[float] = input.source(close, 'Source'),
    mult=input.float(1, 'Multiple', step=0.1, minval=0.1),
    bands=input.bool(True, 'Show Extremities'),
    col=input.color(color.new('#FF5D00'), 'Mono color          ', group='Color Settings', inline='1'),
    bicolor=input.bool(True, 'Bicolor        ', group='Color Settings', inline='a'),
    colA=input.color(color.new('#089981'), '', group='Color Settings', inline='a'),
    colB=input.color(color.new('#F23645'), '', group='Color Settings', inline='a'),
    grad=input.bool(True, 'Gradient', group='Color Settings', inline='c'),
    grade=input.int(15, '    ', minval=0, maxval=50, group='Color Settings', inline='c'),
    showDash=input.bool(True, 'Show Dashboard', group='Dashboard'),
    __input_13__=input.string('Top Right', 'Location', options=('Top Right', 'Bottom Right', 'Bottom Left'), group='Dashboard'),
    __input_14__=input.string('Normal', 'Size', options=('Tiny', 'Small', 'Normal'), group='Dashboard')
):
    dashLoc = string.replace(string.lower(__input_13__), ' ', '_')
    textSize = string.lower(__input_14__)
    tb: Persistent = table.new(dashLoc, 2, 3, bgcolor=color.new('#1E222D'), border_color=color.new('#373A46'), border_width=1, frame_color=color.new('#373A46'), frame_width=1)
    lbi = last_bar_index
    n = bar_index
    INV = NA(Color)
    def draw(res, src, choice, anchor, bands, col, idx):
        yMx: float = na(float)
        dist: float = na(float)
        ch = timeframe.change(res)
        ln: Persistent[Line] = na(Line)
        lnU: Persistent[Line] = na(Line)
        lnD: Persistent[Line] = na(Line)
        aX: Persistent[list[int]] = array.new_int()
        aY: Persistent[list[float]] = array.new_float()
        Ex: Persistent[float] = 0.0
        Ey: Persistent[float] = 0.0
        Ex2: Persistent[float] = 0.0
        Exy: Persistent[float] = 0.0
        N: Persistent[int] = 0
        Ex = Ex + n
        Ey = Ey + src
        Ex2 = Ex2 + math.pow(n, 2)
        Exy = Exy + n * src
        N = N + 1
        array.unshift(aX, n)
        array.unshift(aY, src)
        cov = array.covariance(aY, aX)
        x_var = array.variance(aX)
        a_ = cov / x_var
        b_ = array.avg(aY) - a_ * array.avg(aX)
        r2 = math.pow(cov / (array.stdev(aY) * array.stdev(aX)), 2)
        rss = array.variance(aY) - r2 * array.variance(aY)
        dist = math.sqrt(rss) * mult
        m = (N * Exy - Ex * Ey) / (N * Ex2 - math.pow(Ex, 2))
        b = (Ey - m * Ex) / N
        yMx = m * n + b
        if choice == 'Static':
            cl = (colA if line.get_y2(ln) > line.get_y1(ln) else colB) if bicolor else col
            x1 = line.get_x1(ln)
            line.set_xy2(ln, n, yMx)
            line.set_y1(ln, m * x1 + b)
            if bicolor:
                line.set_color(ln, cl)
            if bands:
                line.set_xy2(lnU, n, yMx + dist)
                line.set_y1(lnU, m * x1 + b + dist)
                line.set_color(lnU, cl)
                line.set_xy2(lnD, n, yMx - dist)
                line.set_y1(lnD, m * x1 + b - dist)
                line.set_color(lnD, cl)
        if ch:
            if anchor == 'Periodic' or choice == 'Static':
                Ex = 0.0
                Ey = 0.0
                Ex2 = 0.0
                Exy = 0.0
                array.clear(aX)
                array.clear(aY)
            N = 0
            if choice == 'Static':
                ln = line.new(n, src, n, src, color=col)
                if bands:
                    lnU = line.new(n, src + dist, n, src + dist, color=col)
                    lnD = line.new(n, src - dist, n, src - dist, color=col)
        R = cov / (array.stdev(aX) * array.stdev(aY))
        return (yMx if choice == 'Rolling' else na, yMx + dist if choice == 'Rolling' and bands else na, yMx - dist if choice == 'Rolling' and bands else na, R)

    yMx, yMx_pos, yMx_min, R = draw(res, src, choice, anchor, bands, col, 0)
    rolling = bicolor and choice == 'Rolling'
    m = plot(yMx, color=color.from_gradient(R, -1, 1, colB, colA) if rolling else col, style=plot.style_linebr)
    b = plot(yMx_min, color=NA(Color) if rolling else col, style=plot.style_linebr)
    t = plot(yMx_pos, color=NA(Color) if rolling else col, style=plot.style_linebr)
    fill(m, t, yMx, yMx_pos, color.new(color.from_gradient(R, -1, 1, colB, colA), 100) if grad else na, color.new(color.from_gradient(R, -1, 1, colB, colA), 100 - grade) if grad else na)
    fill(m, b, yMx, yMx_min, color.new(color.from_gradient(R, -1, 1, colB, colA), 100) if grad else na, color.new(color.from_gradient(R, -1, 1, colB, colA), 100 - grade) if grad else na)
    if barstate.islast:
        if showDash:
            method_call('cell', tb, 0, 0, 'HTF', text_color=color.white, text_size=textSize)
            method_call('cell', tb, 1, 0, string.tostring(res), text_color=color.white, text_size=textSize)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)