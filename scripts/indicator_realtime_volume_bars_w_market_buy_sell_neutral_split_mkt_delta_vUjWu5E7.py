"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, barstate, close, color, extend, input, label, line, nz, open,
    plot, script, size, string, ta, volume, yloc
)
from pynecore.types import IBPersistent, IBPersistentSeries, Persistent


@script.indicator('Volume with Market Buy/Sell and Neutral Volume Split for Realtime Bars', shorttitle='VolMarketBuySellNeutral_MW', overlay=False, max_labels_count=500)
def main(
    isMode=input.string('Up/Down/Neutral', 'Mode', options=('Up/Down/Neutral', 'Up/Down')),
    isDisplaySplit=input(True, 'Show Split'),
    isDisplayStartLine=input.bool(True, 'Show Start Line', tooltip='Realtime data starts from the bar to the right of this line'),
    isDisplayVolumeMA=input.bool(False, 'Show MA |', inline='MA'),
    volumeMAPeriod=input.int(20, 'MA Period', inline='MA', minval=1, maxval=100),
    isDisplayMarketDelta=input(True, 'Show Net Delta Vol Above Bar'),
    colorDeltaVolUpVal=input.color(color.green, 'Net Delta +ve', inline='DeltaNumColor'),
    colorDeltaVolDnVal=input.color(color.red, 'Net Delta -ve', inline='DeltaNumColor'),
    colorDeltaVolNtVal=input.color(color.gray, 'Net Delta 0', inline='DeltaNumColor'),
    scaleDownFactor=input.int(1, 'Scale Down Factor', options=(1, 10, 100, 1000, 10000), tooltip='Display the net delta value scaled down for better readability'),
    fontSizeUI=input.string('Medium', 'Font Size', options=('Auto', 'Tiny', 'Small', 'Medium', 'Large', 'Huge'))
):
    UPDOWNNEUTRAL_MODE: int = 1
    UPDOWN_MODE: int = 2

    iMode = UPDOWNNEUTRAL_MODE if isMode == 'Up/Down/Neutral' else UPDOWN_MODE
    fontSize = size.auto if fontSizeUI == 'Auto' else size.tiny if fontSizeUI == 'Tiny' else size.small if fontSizeUI == 'Small' else size.normal if fontSizeUI == 'Medium' else size.large if fontSizeUI == 'Large' else size.huge

    def f_upDnNtVolume(_mode):
        _prevClose: IBPersistent[float] = open
        _prevVolume: IBPersistent[float] = 0.0
        _newVolume: IBPersistent[float] = 0.0
        _volUp: IBPersistent[float] = 0.0
        _volDn: IBPersistent[float] = 0.0
        _volNt: IBPersistent[float] = 0.0
        _prevPolarity: IBPersistentSeries[int] = 0

        if barstate.isnew:
            _volUp = 0.0
            _volDn = 0.0
            _volNt = 0.0
            _prevClose = nz(close[1])
            _prevVolume = 0.0
            _prevPolarity = nz(_prevPolarity[1])

        _newVolume = volume - _prevVolume

        if close > _prevClose:
            _prevPolarity = 1
            _volUp = _volUp + _newVolume
        elif close < _prevClose:
            _prevPolarity = -1
            _volDn = _volDn + _newVolume
        else:
            if _mode == UPDOWN_MODE:
                if _prevPolarity == 1:
                    _volUp = _volUp + _newVolume
                elif _prevPolarity == -1:
                    _volDn = _volDn + _newVolume
                else:
                    _volNt = _volNt + _newVolume
            else:
                _volNt = _volNt + _newVolume

        _prevClose = close
        _prevVolume = volume
        return (_volUp, _volDn, _volNt)

    isbarConsidered: Persistent[bool] = False
    firstBar: Persistent[bool] = True
    volUp, volDn, volNt = f_upDnNtVolume(iMode)
    deltaVol = volUp - volDn
    totVol = volUp + volDn + volNt

    isbarConsidered = True if barstate.isrealtime else isbarConsidered

    baseSeriesColor = color.blue if close > open else color.black if close < open else color.gray
    baseSeries = volume if not isbarConsidered else volume if not isDisplaySplit else 0
    buySeries = 0 if not isbarConsidered else volume if isDisplaySplit else 0
    sellSeries = 0 if not isbarConsidered else volDn + volNt if isDisplaySplit else 0
    neutralSeries = 0 if not isbarConsidered else volNt if isDisplaySplit else 0

    plot(baseSeries, 'Historic Volume', color=baseSeriesColor, style=plot.style_columns)
    plot(buySeries, 'Volume Up', color=color.new(color.green, 0), style=plot.style_columns)
    plot(sellSeries, 'Volume Down', color=color.new(color.red, 0), style=plot.style_columns)
    plot(volNt, 'Volume Neutral', color=color.new(color.gray, 0), style=plot.style_columns)
    plot(ta.ema(volume, volumeMAPeriod) if isDisplayVolumeMA else 0, 'Volume MA', color=color.new(color.black, 0), style=plot.style_line)

    if isbarConsidered:
        if firstBar:
            if isDisplayStartLine:
                line.new(bar_index, volume + 5, bar_index, volume + 6, extend=extend.right, color=color.black, style=line.style_dashed)
            firstBar = False
        if isDisplayMarketDelta:
            text_color = colorDeltaVolUpVal if volUp - volDn > 0 else colorDeltaVolDnVal if volUp - volDn < 0 else colorDeltaVolNtVal
            label.new(x=bar_index, y=volume, yloc=yloc.price, textcolor=text_color, style=label.style_none, size=fontSize, text=string.tostring(cast_int((volUp - volDn) / scaleDownFactor)))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
