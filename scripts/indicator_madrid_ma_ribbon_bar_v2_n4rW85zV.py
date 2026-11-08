"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, ta


@script.indicator(title='Madrid MA Ribbon Bar v2', shorttitle='MMARB', precision=0)
def main(
    exponential=input(True, title='Exponential MA')
):
    src = close

    ema_1 = ta.ema(src, 5)
    sma_1 = ta.sma(src, 5)
    ma05 = ema_1 if exponential else sma_1
    ema_2 = ta.ema(src, 10)
    sma_2 = ta.sma(src, 10)
    ma10 = ema_2 if exponential else sma_2
    ema_3 = ta.ema(src, 15)
    sma_3 = ta.sma(src, 15)
    ma15 = ema_3 if exponential else sma_3
    ema_4 = ta.ema(src, 20)
    sma_4 = ta.sma(src, 20)
    ma20 = ema_4 if exponential else sma_4
    ema_5 = ta.ema(src, 25)
    sma_5 = ta.sma(src, 25)
    ma25 = ema_5 if exponential else sma_5
    ema_6 = ta.ema(src, 30)
    sma_6 = ta.sma(src, 30)
    ma30 = ema_6 if exponential else sma_6
    ema_7 = ta.ema(src, 35)
    sma_7 = ta.sma(src, 35)
    ma35 = ema_7 if exponential else sma_7
    ema_8 = ta.ema(src, 40)
    sma_8 = ta.sma(src, 40)
    ma40 = ema_8 if exponential else sma_8
    ema_9 = ta.ema(src, 45)
    sma_9 = ta.sma(src, 45)
    ma45 = ema_9 if exponential else sma_9
    ema_10 = ta.ema(src, 50)
    sma_10 = ta.sma(src, 50)
    ma50 = ema_10 if exponential else sma_10
    ema_11 = ta.ema(src, 55)
    sma_11 = ta.sma(src, 55)
    ma55 = ema_11 if exponential else sma_11
    ema_12 = ta.ema(src, 60)
    sma_12 = ta.sma(src, 60)
    ma60 = ema_12 if exponential else sma_12
    ema_13 = ta.ema(src, 65)
    sma_13 = ta.sma(src, 65)
    ma65 = ema_13 if exponential else sma_13
    ema_14 = ta.ema(src, 70)
    sma_14 = ta.sma(src, 70)
    ma70 = ema_14 if exponential else sma_14
    ema_15 = ta.ema(src, 75)
    sma_15 = ta.sma(src, 75)
    ma75 = ema_15 if exponential else sma_15
    ema_16 = ta.ema(src, 80)
    sma_16 = ta.sma(src, 80)
    ma80 = ema_16 if exponential else sma_16
    ema_17 = ta.ema(src, 85)
    sma_17 = ta.sma(src, 85)
    ma85 = ema_17 if exponential else sma_17
    ema_18 = ta.ema(src, 90)
    sma_18 = ta.sma(src, 90)
    ma90 = ema_18 if exponential else sma_18
    ema_19 = ta.ema(src, 95)
    sma_19 = ta.sma(src, 95)
    ma95 = ema_19 if exponential else sma_19
    ema_20 = ta.ema(src, 100)
    sma_20 = ta.sma(src, 100)
    ma100 = ema_20 if exponential else sma_20

    change_1 = ta.change(ma05)
    change_2 = ta.change(ma05)
    change_3 = ta.change(ma05)
    leadMAColor = color.lime if ta.change(ma05) >= 0 and ma05 > ma100 else color.maroon if change_1 < 0 and ma05 > ma100 else color.red if change_2 <= 0 and ma05 < ma100 else color.green if change_3 >= 0 and ma05 < ma100 else color.gray
    def maColor(ma, maRef):
        change1 = ta.change(ma)
        change2 = ta.change(ma)
        change3 = ta.change(ma)
        return color.lime if ta.change(ma) >= 0 and ma05 > maRef else color.maroon if change1 < 0 and ma05 > maRef else color.red if change2 <= 0 and ma05 < maRef else color.green if change3 >= 0 and ma05 < maRef else color.gray

    plot(5, color=leadMAColor, style=plot.style_columns, title='MMA05', linewidth=2, histbase=0)
    plot(10, color=maColor(ma10, ma100), style=plot.style_columns, title='MMA10', linewidth=2, histbase=5)
    plot(15, color=maColor(ma15, ma100), style=plot.style_columns, title='MMA15', linewidth=2, histbase=10)
    plot(20, color=maColor(ma20, ma100), style=plot.style_columns, title='MMA20', linewidth=2, histbase=15)
    plot(25, color=maColor(ma25, ma100), style=plot.style_columns, title='MMA25', linewidth=2, histbase=20)
    plot(30, color=maColor(ma30, ma100), style=plot.style_columns, title='MMA30', linewidth=2, histbase=25)
    plot(35, color=maColor(ma35, ma100), style=plot.style_columns, title='MMA35', linewidth=2, histbase=30)
    plot(40, color=maColor(ma40, ma100), style=plot.style_columns, title='MMA40', linewidth=2, histbase=35)
    plot(45, color=maColor(ma45, ma100), style=plot.style_columns, title='MMA45', linewidth=2, histbase=40)
    plot(50, color=maColor(ma50, ma100), style=plot.style_columns, title='MMA50', linewidth=2, histbase=45)
    plot(55, color=maColor(ma55, ma100), style=plot.style_columns, title='MMA55', linewidth=2, histbase=50)
    plot(60, color=maColor(ma60, ma100), style=plot.style_columns, title='MMA60', linewidth=2, histbase=55)
    plot(65, color=maColor(ma65, ma100), style=plot.style_columns, title='MMA65', linewidth=2, histbase=60)
    plot(70, color=maColor(ma70, ma100), style=plot.style_columns, title='MMA70', linewidth=2, histbase=65)
    plot(75, color=maColor(ma75, ma100), style=plot.style_columns, title='MMA75', linewidth=2, histbase=70)
    plot(80, color=maColor(ma80, ma100), style=plot.style_columns, title='MMA80', linewidth=2, histbase=75)
    plot(85, color=maColor(ma85, ma100), style=plot.style_columns, title='MMA85', linewidth=2, histbase=80)
    plot(90, color=maColor(ma90, ma100), style=plot.style_columns, title='MMA90', linewidth=2, histbase=85)
    plot(95, color=maColor(ma90, ma100), style=plot.style_columns, title='MMA95', linewidth=2, histbase=90)
    plot(100, color=maColor(ma90, ma100), style=plot.style_columns, title='MMA100', linewidth=2, histbase=95)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
