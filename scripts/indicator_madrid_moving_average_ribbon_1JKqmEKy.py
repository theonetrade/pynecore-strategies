"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import close, color, input, math, plot, script, ta
from pynecore.types import Color


@script.indicator('Madrid Moving Average Ribbon', shorttitle='Madrid Ribbon', overlay=True, na_bool=True)
def main(
    _10=input(False, '───────────[ Madrid Ribbon]───────────'),
    i_exp=input(True, title='Expnential MA')
):
    PHI = (1 + math.sqrt(5)) / 2
    PI = cast_int(104348 / 33215)
    BULL: int = 1
    BEAR = -1
    NONE: int = 0
    GRN01: Color = color.new('#7CFC00')
    GRN02: Color = color.new('#32CD32')
    GRN03: Color = color.new('#228B22')
    GRN04: Color = color.new('#006400')
    GRN05: Color = color.new('#008000')
    GRN06: Color = color.new('#093507')
    RED01: Color = color.new('#FF4500')
    RED02: Color = color.new('#FF0000')
    RED03: Color = color.new('#B22222')
    RED04: Color = color.new('#8B0000')
    RED05: Color = color.new('#800000')
    RED06: Color = color.new('#330D06')
    AQUA: Color = color.new('#00FFFF')
    BLACK: Color = color.new('#000000')
    BLUE: Color = color.new('#0000FF')
    FUCHSIA: Color = color.new('#FF00FF')
    GRAY: Color = color.new('#808080')
    GREEN: Color = color.new('#008000')
    LIME: Color = color.new('#00FF00')
    MAROON: Color = color.new('#800000')
    NAVY: Color = color.new('#000080')
    OLIVE: Color = color.new('#808000')
    ORANGE: Color = color.new('#FF7F00')
    PURPLE: Color = color.new('#800080')
    RUBI: Color = color.new('#FF0000')
    SILVER: Color = color.new('#C0C0C0')
    TEAL: Color = color.new('#008080')
    YELLOW: Color = color.new('#FFFF00')
    WHITE: Color = color.new('#FFFFFF')
    def maColor(_ma, _maRef):
        diffMA = ta.change(_ma)
        macol = LIME if diffMA >= 0 and _ma > _maRef else MAROON if diffMA < 0 and _ma > _maRef else RUBI if diffMA <= 0 and _ma < _maRef else GREEN if diffMA >= 0 and _ma < _maRef else GRAY
        return macol

    src = close
    ma05 = ta.ema(src, 5) if i_exp else ta.sma(src, 5)
    ma10 = ta.ema(src, 10) if i_exp else ta.sma(src, 10)
    ma15 = ta.ema(src, 15) if i_exp else ta.sma(src, 15)
    ma20 = ta.ema(src, 20) if i_exp else ta.sma(src, 20)
    ma25 = ta.ema(src, 25) if i_exp else ta.sma(src, 25)
    ma30 = ta.ema(src, 30) if i_exp else ta.sma(src, 30)
    ma35 = ta.ema(src, 35) if i_exp else ta.sma(src, 35)
    ma40 = ta.ema(src, 40) if i_exp else ta.sma(src, 40)
    ma45 = ta.ema(src, 45) if i_exp else ta.sma(src, 45)
    ma50 = ta.ema(src, 50) if i_exp else ta.sma(src, 50)
    ma55 = ta.ema(src, 55) if i_exp else ta.sma(src, 55)
    ma60 = ta.ema(src, 60) if i_exp else ta.sma(src, 60)
    ma65 = ta.ema(src, 65) if i_exp else ta.sma(src, 65)
    ma70 = ta.ema(src, 70) if i_exp else ta.sma(src, 70)
    ma75 = ta.ema(src, 75) if i_exp else ta.sma(src, 75)
    ma80 = ta.ema(src, 80) if i_exp else ta.sma(src, 80)
    ma85 = ta.ema(src, 85) if i_exp else ta.sma(src, 85)
    ma90 = ta.ema(src, 90) if i_exp else ta.sma(src, 90)
    ma100 = ta.ema(src, 100) if i_exp else ta.sma(src, 100)
    plot(ma05, color=maColor(ma05, ma100), style=plot.style_line, title='MMA05', linewidth=3)
    plot(ma10, color=maColor(ma10, ma100), style=plot.style_line, title='MMA10', linewidth=1)
    plot(ma15, color=maColor(ma15, ma100), style=plot.style_line, title='MMA15', linewidth=1)
    plot(ma20, color=maColor(ma20, ma100), style=plot.style_line, title='MMA20', linewidth=1)
    plot(ma25, color=maColor(ma25, ma100), style=plot.style_line, title='MMA25', linewidth=1)
    plot(ma30, color=maColor(ma30, ma100), style=plot.style_line, title='MMA30', linewidth=1)
    plot(ma35, color=maColor(ma35, ma100), style=plot.style_line, title='MMA35', linewidth=1)
    plot(ma40, color=maColor(ma40, ma100), style=plot.style_line, title='MMA40', linewidth=1)
    plot(ma45, color=maColor(ma45, ma100), style=plot.style_line, title='MMA45', linewidth=1)
    plot(ma50, color=maColor(ma50, ma100), style=plot.style_line, title='MMA50', linewidth=1)
    plot(ma55, color=maColor(ma55, ma100), style=plot.style_line, title='MMA55', linewidth=1)
    plot(ma60, color=maColor(ma60, ma100), style=plot.style_line, title='MMA60', linewidth=1)
    plot(ma65, color=maColor(ma65, ma100), style=plot.style_line, title='MMA65', linewidth=1)
    plot(ma70, color=maColor(ma70, ma100), style=plot.style_line, title='MMA70', linewidth=1)
    plot(ma75, color=maColor(ma75, ma100), style=plot.style_line, title='MMA75', linewidth=1)
    plot(ma80, color=maColor(ma80, ma100), style=plot.style_line, title='MMA80', linewidth=1)
    plot(ma85, color=maColor(ma85, ma100), style=plot.style_line, title='MMA85', linewidth=1)
    plot(ma90, color=maColor(ma90, ma100), style=plot.style_line, title='MMA90', linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
