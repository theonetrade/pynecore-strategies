"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, display,
    extend, fill, format, high, input, label, line, linefill, location, low, math, na, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, xloc
)
from pynecore.types import Label, Line, LineFill, Persistent, Series, Table

display__ren__ = display.all - display.status_line
rrsiGR: str = 'Reverse RSI Labels'
group_rsi_osc: str = 'RSI Overlay Display'


@script.indicator('RSI Support & Resistance by DGT', 'RSI S&R ☼☾', True, max_lines_count=500, max_bars_back=500)
def main(
    i_source=input.string('Price (close)', 'Source', options=('Price (close)', 'On Balance Volume (OBV)'), inline='RSI', group='RSI Settings', display=display__ren__, tooltip='Select the data source used to compute RSI.\n' + '• Price (close): Classic RSI based on price action\n' + '• OBV: Volume-weighted momentum using On Balance Volume'),
    i_length=input.int(14, '   Length', minval=1, inline='RSI', group='RSI Settings', display=display__ren__),
    i_obThreshold=input.int(70, 'Overbought', minval=50, maxval=100, inline='Thresh1', group='RSI Settings', display=display__ren__),
    i_bullZone=input.int(60, 'Bull Zone', minval=50, maxval=65, inline='Thresh1', group='RSI Settings', display=display__ren__, tooltip='Overbought:\nOverbought threshold.\n' + 'Crosses above this level may indicate exhaustion and potential resistance formation.\n\n' + 'Bull Zone:\nBullish momentum zone.\n' + 'RSI holding above this level indicates sustained bullish pressure.'),
    i_bearZone=input.int(40, 'Bear Zone ', minval=35, maxval=50, inline='Thresh2', group='RSI Settings', display=display__ren__),
    i_osThreshold=input.int(30, 'Oversold', minval=1, maxval=50, inline='Thresh2', group='RSI Settings', display=display__ren__, tooltip='Bear Zone:\nBearish momentum zone.\n' + 'RSI holding below this level indicates sustained bearish pressure.\n\n' + 'Oversold:\nOversold threshold.\n' + 'Crosses below this level may indicate capitulation and potential support formation.'),
    bullColor=input.color(color.teal, 'Bullish', inline='ob', group='RSI Settings'),
    midColor=input.color(color.gray, 'Neutral', inline='ob', group='RSI Settings'),
    bearColor=input.color(color.red, 'Bearish', inline='ob', group='RSI Settings'),
    showSR=input.bool(True, 'Show RSI S&R Zones', group='RSI S&R Zones', display=display__ren__, inline='RSI', tooltip='Displays dynamic support and resistance zones derived from RSI threshold crossings.\n\n' + 'Zones are plotted directly on price — each level marks where RSI crossed a key threshold in the past, translating oscillator conditions into actionable price levels.\n\n' + '• Overbought crossover → potential resistance zone\n' + '• Overbought exit (crossunder back below) → resistance weakening\n' + '• Bull Zone (RSI 60) cross → dynamic support in uptrends\n' + '• Bear Zone (RSI 40) cross → dynamic resistance in downtrends\n' + '• Oversold crossunder → potential support zone\n' + '• Oversold exit (crossover back above) → support strengthening'),
    i_fill=input.bool(True, 'Zone Fills', group='RSI S&R Zones', inline='RSI'),
    i_obos=input.bool(False, 'RSI Overbought/Oversold Bar Marks', group='RSI S&R Zones', tooltip='Marks price bars when RSI is in overbought or oversold conditions.'),
    showRRSI=input.bool(True, 'Reverse RSI Price Levels', group=rrsiGR, display=display__ren__, inline='REV', tooltip='Displays the price required on the current bar to push RSI to each threshold level.\n\n' + 'Complements the historical S&R zones with forward-looking price targets.\n' + 'Uses the same RSI length and source as the S&R settings above.\n\n' + '↑ = price needs to rise to reach this RSI level\n' + '↓ = price needs to fall to reach this RSI level'),
    rrsiSize=input.string('Small', '', group=rrsiGR, display=display__ren__, inline='REV', options=('Tiny', 'Small', 'Normal')),
    shRRSI=input.bool(False, 'Reverse RSI Price Bands', group=rrsiGR, display=display__ren__, tooltip='Plots the required price levels as continuous bands across the chart.\n' + 'Shows how each RSI target evolves bar by bar — useful for spotting whether a target is converging toward or diverging from current price.\n' + 'Use alongside labels for point-in-time reference at the right edge.'),
    rsi_osc=input.bool(True, 'Enable RSI Overlay', group=group_rsi_osc, tooltip='Displays RSI oscillator directly on the price chart.'),
    oscPlacement=input.string('Top', 'Placement', options=('Top', 'Bottom'), inline='VOL', group=group_rsi_osc, display=display__ren__, tooltip='Choose where the RSI overlay is projected:\n' + '• Top: Above price\n' + '• Bottom: Below price'),
    __input_17__=input.int(7, ' Height', minval=3, maxval=10, inline='VOL', group=group_rsi_osc, display=display__ren__),
    lookbackLength=input.int(200, 'Overlay Display Length', minval=10, maxval=495, group=group_rsi_osc, display=display__ren__)
):
    rrsiTxtSize = size.normal if rrsiSize == 'Normal' else size.small if rrsiSize == 'Small' else size.tiny

    oscHight = 11 - __input_17__

    def f_getPrice(_osc, _thresh, _cross):
        avgHigh = math.avg(high, close)
        avgLow = math.avg(low, close)

        return_1: Persistent[float] = 0.0

        if _cross == 'over' or _cross == 'both':
            if ta.crossover(_osc, _thresh):
                return_1 = avgHigh
        if _cross == 'under' or _cross == 'both':
            if ta.crossunder(_osc, _thresh):
                return_1 = avgLow
        return return_1

    def f_rsiComponents(_src, _len):
        _change = ta.change(_src)
        _avgGain = ta.rma(math.max(_change, 0.0), _len)
        _avgLoss = ta.rma(math.abs(math.min(_change, 0.0)), _len)
        return (_avgGain, _avgLoss)

    def f_reverseRSI(_src, _len, _target, _avgGain, _avgLoss, _rsi):
        _rs = _target / math.max(100 - _target, 0.001)
        _price: float = na(float)
        if _target > _rsi:
            _gainNew = _rs * _avgLoss * _len - _avgGain * (_len - 1)
            _price = _src + _gainNew if _gainNew > 0 else _src
        elif _target < _rsi:
            _lossNew = _avgGain / math.max(_rs, 0.0001) * _len - _avgLoss * (_len - 1)
            _price = _src - _lossNew if _lossNew > 0 else _src
        else:
            _price = _src
        return _price

    rsiSrc = close if i_source == 'Price (close)' else ta.obv
    oscillator: Series = ta.rsi(rsiSrc, i_length)

    crossover_overbought: Series = f_getPrice(oscillator, i_obThreshold, 'over')
    crossunder_overbought: Series = f_getPrice(oscillator, i_obThreshold, 'under')
    bullZone: Series = f_getPrice(oscillator, i_bullZone, 'both')
    bearZone: Series = f_getPrice(oscillator, i_bearZone, 'both')
    crossover_oversold: Series = f_getPrice(oscillator, i_osThreshold, 'over')
    crossunder_oversold: Series = f_getPrice(oscillator, i_osThreshold, 'under')

    avgGain, avgLoss = f_rsiComponents(rsiSrc, i_length)

    priceOB = f_reverseRSI(rsiSrc, i_length, i_obThreshold, avgGain, avgLoss, oscillator)
    priceBull = f_reverseRSI(rsiSrc, i_length, i_bullZone, avgGain, avgLoss, oscillator)
    priceMid = f_reverseRSI(rsiSrc, i_length, 50, avgGain, avgLoss, oscillator)
    priceBear = f_reverseRSI(rsiSrc, i_length, i_bearZone, avgGain, avgLoss, oscillator)
    priceOS = f_reverseRSI(rsiSrc, i_length, i_osThreshold, avgGain, avgLoss, oscillator)

    plot_crossover_overbought = plot(crossover_overbought if showSR and crossover_overbought > 0 else na, 'RSI Overbought Crossover Level', bullColor if crossover_overbought == crossover_overbought[1] else na, 2, display=display__ren__)
    plot_crossunder_overbought = plot(crossunder_overbought if showSR and crossunder_overbought > 0 else na, 'RSI Overbought Exit Level', bullColor if crossunder_overbought == crossunder_overbought[1] else na, 1, plot.style_cross, display=display__ren__)
    plot_bullZone = plot(bullZone if showSR and bullZone > 0 else na, 'RSI Bullish Threshold Level', bullColor if bullZone == bullZone[1] else na, 1, display=display__ren__)

    fill(plot_crossover_overbought, plot_bullZone, color.new(bullColor, 90) if i_fill else na, title='RSI Bullish Momentum Zone')
    plotshape(i_obos and oscillator > i_obThreshold, 'Price in RSI Overbought Zone', shape.triangledown, location.abovebar, color.new(bearColor, 25), size=size.tiny, display=display__ren__)

    plot_bearZone = plot(bearZone if showSR and bearZone > 0 else na, 'RSI Bearish Threshold Level', bearColor if bearZone == bearZone[1] else na, 1, display=display__ren__)
    plot_crossover_oversold = plot(crossover_oversold if showSR and crossover_oversold > 0 else na, 'RSI Oversold Rebound Level', bearColor if crossover_oversold == crossover_oversold[1] else na, 1, plot.style_cross, display=display__ren__)
    plot_crossunder_oversold = plot(crossunder_oversold if showSR and crossunder_oversold > 0 else na, 'RSI Oversold Breakdown Level', bearColor if crossunder_oversold == crossunder_oversold[1] else na, 2, display=display__ren__)

    fill(plot_crossunder_oversold, plot_bearZone, color.new(bearColor, 90) if i_fill else na, title='RSI Bearish Momentum Zone')
    plotshape(i_obos and oscillator < i_osThreshold, 'Price in RSI Oversold Zone', shape.triangleup, location.belowbar, color.new(bullColor, 25), size=size.tiny, display=display__ren__)

    alertcondition(ta.crossover(close, crossover_overbought), 'Price Crossed Above OB Level', 'RSI S&R: Price crossed above prior RSI overbought level\n{{exchange}}:{{ticker}} | Price={{close}} | {{time}}')
    alertcondition(ta.crossunder(close, crossunder_oversold), 'Price Crossed Below OS Level', 'RSI S&R: Price crossed below prior RSI oversold level\n{{exchange}}:{{ticker}} | Price={{close}} | {{time}}')

    a_lines: Persistent[list[Line]] = array.new_line()
    a_fill: Persistent[list[LineFill]] = array.new_linefill()

    priceHighest = ta.highest(high, lookbackLength)
    priceLowest = ta.lowest(low, lookbackLength)

    if barstate.islast and rsi_osc:
        if array.size(a_lines) > 0:
            while array.size(a_lines) > 0:
                line.delete(array.shift(a_lines))

        if array.size(a_fill) > 0:
            while array.size(a_fill) > 0:
                linefill.delete(array.shift(a_fill))

        priceChangeRate = (priceHighest - priceLowest) / priceHighest / oscHight / 100

        obLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (i_obThreshold if oscPlacement == 'Top' else -1 * (100 - i_obThreshold)) * priceChangeRate)
        bullLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (i_bullZone if oscPlacement == 'Top' else -1 * (100 - i_bullZone)) * priceChangeRate)
        midLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (50 if oscPlacement == 'Top' else -1 * (100 - 50)) * priceChangeRate)
        bearLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (i_bearZone if oscPlacement == 'Top' else -1 * (100 - i_bearZone)) * priceChangeRate)
        osLevel = (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (i_osThreshold if oscPlacement == 'Top' else -1 * (100 - i_osThreshold)) * priceChangeRate)

        array.push(a_lines, line.new(bar_index[lookbackLength], obLevel, bar_index, obLevel, xloc.bar_index, extend.none, bullColor, line.style_dotted, 2))
        array.push(a_lines, line.new(bar_index[lookbackLength], bullLevel, bar_index, bullLevel, xloc.bar_index, extend.none, bullColor, line.style_dotted, 1))
        array.push(a_fill, linefill.new(array.get(a_lines, 0), array.get(a_lines, 1), color.new(bullColor, 90)))

        array.push(a_lines, line.new(bar_index[lookbackLength], bearLevel, bar_index, bearLevel, xloc.bar_index, extend.none, bearColor, line.style_dotted, 1))
        array.push(a_lines, line.new(bar_index[lookbackLength], osLevel, bar_index, osLevel, xloc.bar_index, extend.none, bearColor, line.style_dotted, 2))
        array.push(a_fill, linefill.new(array.get(a_lines, 2), array.get(a_lines, 3), color.new(bearColor, 90)))

        array.push(a_lines, line.new(bar_index[lookbackLength], midLevel, bar_index, midLevel, xloc.bar_index, extend.none, midColor, line.style_dotted, 1))

        for barIndex in pine_range(0, lookbackLength - 1, 1):
            array.push(a_lines, line.new(bar_index[barIndex], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (oscillator[barIndex] if oscPlacement == 'Top' else -1 * (100 - oscillator[barIndex])) * priceChangeRate), bar_index[barIndex + 1], (priceHighest if oscPlacement == 'Top' else priceLowest) * (1 + (oscillator[barIndex + 1] if oscPlacement == 'Top' else -1 * (100 - oscillator[barIndex + 1])) * priceChangeRate), xloc.bar_index, extend.none, color.new('#7E57C2'), line.style_solid, 2))

    lbOB: Persistent[Label] = na(Label)
    lbBull: Persistent[Label] = na(Label)
    lbMid: Persistent[Label] = na(Label)
    lbBear: Persistent[Label] = na(Label)
    lbOS: Persistent[Label] = na(Label)

    def f_rrsiLabel(_lb, _price, _target, _color):
        __block_result__ = na
        if showRRSI and (not na(_price)):
            _dist = _price - close
            _distPct = math.abs(_dist / close) * 100
            _already = math.abs(_dist) < syminfo.mintick
            _dir = '✓ ' if _already else '↑ ' if _dist > 0 else '↓ '
            _tip = 'RSI target ........ : ' + string.tostring(_target) + '\n' + 'Required price .. : ' + ('Already reached' if _already else string.tostring(_price, format.mintick)) + '\n' + 'Distance .......... : ' + ('—' if _already else _dir + string.tostring(math.abs(_dist), format.mintick) + '  (' + string.tostring(_distPct, '#.##') + '%)') + '\n' + 'Current RSI ...... : ' + string.tostring(oscillator, '#.##')
            _txt = 'RSI ' + string.tostring(_target) + (' ✓' if _already else ' → ' + string.tostring(_price, format.mintick))

            __block_result_1__ = na
            if na(_lb):
                __block_result_1__ = label.new(bar_index + 2, _price, _txt, xloc.bar_index, color=color.new(_color, 80), textcolor=_color, style=label.style_label_left, size=rrsiTxtSize, tooltip=_tip)
            else:
                label.set_xy(_lb, bar_index + 2, _price)
                label.set_text(_lb, _txt)
                label.set_color(_lb, color.new(_color, 80))
                label.set_textcolor(_lb, _color)
                label.set_tooltip(_lb, _tip)
                __block_result_1__ = _lb
            __block_result__ = __block_result_1__
        else:
            __block_result__ = _lb
        return __block_result__

    if barstate.islast and i_source == 'Price (close)':
        lbOB = f_rrsiLabel(lbOB, priceOB, i_obThreshold, bullColor)
        lbBull = f_rrsiLabel(lbBull, priceBull, i_bullZone, color.new(bullColor, 40))
        lbMid = f_rrsiLabel(lbMid, priceMid, 50, color.new(midColor, 20))
        lbBear = f_rrsiLabel(lbBear, priceBear, i_bearZone, color.new(bearColor, 40))
        lbOS = f_rrsiLabel(lbOS, priceOS, i_osThreshold, bearColor)

    ob = plot(priceOB if shRRSI else na, 'RevRSI OB Level', bullColor, display=display__ren__)
    pob = plot(priceBull if shRRSI else na, 'RevRSI Bull Level', color.new(bullColor, 40), display=display__ren__)
    plot(priceMid if shRRSI else na, 'RevRSI Mid Level', color.new(midColor, 20), display=display__ren__)
    pos = plot(priceBear if shRRSI else na, 'RevRSI Bear Level', color.new(bearColor, 40), display=display__ren__)
    os = plot(priceOS if shRRSI else na, 'RevRSI OS Level', bearColor, display=display__ren__)

    fill(ob, pob, color=color.new(bullColor, 90) if shRRSI else na, title='RevRSI Bullish Zone')
    fill(pos, os, color=color.new(bearColor, 90) if shRRSI else na, title='RevRSI Bearish Zone')

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
