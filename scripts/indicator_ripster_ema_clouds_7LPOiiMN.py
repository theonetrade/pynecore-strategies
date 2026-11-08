"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, fill, hl2, input, na, plot, script, ta
from pynecore.types import Series


@script.indicator('Ripster EMA Clouds', 'Ripster EMA Clouds', overlay=True, na_bool=True)
def main(
    matype=input.string(title='MA Type', defval='EMA', options=('EMA', 'SMA')),
    ma_len1=input(title='Short EMA1 Length', defval=8),
    ma_len2=input(title='Long EMA1 Length', defval=9),
    ma_len3=input(title='Short EMA2 Length', defval=5),
    ma_len4=input(title='Long EMA2 Length', defval=12),
    ma_len5=input(title='Short EMA3 Length', defval=34),
    ma_len6=input(title='Long EMA3 Length', defval=50),
    ma_len7=input(title='Short EMA4 Length', defval=72),
    ma_len8=input(title='Long EMA4 Length', defval=89),
    ma_len9=input(title='Short EMA5 Length', defval=180),
    ma_len10=input(title='Long EMA5 Length', defval=200),
    src: Series[float] = input(title='Source', defval=hl2),
    ma_offset=input(title='Offset', defval=0),
    showlong=input(False, title='Show Long Alerts'),
    showshort=input(False, title='Show Short Alerts'),
    showLine=input(False, title='Display EMA Line'),
    ema1=input(True, title='Show EMA Cloud-1'),
    ema2=input(True, title='Show EMA Cloud-2'),
    ema3=input(True, title='Show EMA Cloud-3'),
    ema4=input(False, title='Show EMA Cloud-4'),
    ema5=input(False, title='Show EMA Cloud-5'),
    emacloudleading=input.int(0, minval=0, title='Leading Period For EMA Cloud')
):
    def f_ma(malen):
        result: float = 0
        if matype == 'EMA':
            result = ta.ema(src, malen)
        if matype == 'SMA':
            result = ta.sma(src, malen)
        return result

    htf_ma1 = f_ma(ma_len1)
    htf_ma2 = f_ma(ma_len2)
    htf_ma3 = f_ma(ma_len3)
    htf_ma4 = f_ma(ma_len4)
    htf_ma5 = f_ma(ma_len5)
    htf_ma6 = f_ma(ma_len6)
    htf_ma7 = f_ma(ma_len7)
    htf_ma8 = f_ma(ma_len8)
    htf_ma9 = f_ma(ma_len9)
    htf_ma10 = f_ma(ma_len10)
    mashort1: Series = htf_ma1
    malong1: Series = htf_ma2
    mashort2: Series = htf_ma3
    malong2: Series = htf_ma4
    mashort3: Series = htf_ma5
    malong3: Series = htf_ma6
    mashort4: Series = htf_ma7
    malong4: Series = htf_ma8
    mashort5: Series = htf_ma9
    malong5: Series = htf_ma10
    cloudcolour1 = color.new('#036103') if mashort1 >= malong1 else color.new('#880E4F')
    cloudcolour2 = color.new('#4CAF50') if mashort2 >= malong2 else color.new('#F44336')
    cloudcolour3 = color.new('#2196F3') if mashort3 >= malong3 else color.new('#FFB74D')
    cloudcolour4 = color.new('#009688') if mashort4 >= malong4 else color.new('#F06292')
    cloudcolour5 = color.new('#05BED5') if mashort5 >= malong5 else color.new('#E65100')
    mashortcolor1 = color.olive if mashort1 >= mashort1[1] else color.maroon
    mashortcolor2 = color.olive if mashort2 >= mashort2[1] else color.maroon
    mashortcolor3 = color.olive if mashort3 >= mashort3[1] else color.maroon
    mashortcolor4 = color.olive if mashort4 >= mashort4[1] else color.maroon
    mashortcolor5 = color.rgb(179, 179, 43) if mashort5 >= mashort5[1] else color.maroon
    mashortline1 = plot(mashort1 if ema1 else na, color=mashortcolor1 if showLine else na, linewidth=1, offset=emacloudleading, title='Short Leading EMA1')
    mashortline2 = plot(mashort2 if ema2 else na, color=mashortcolor2 if showLine else na, linewidth=1, offset=emacloudleading, title='Short Leading EMA2')
    mashortline3 = plot(mashort3 if ema3 else na, color=mashortcolor3 if showLine else na, linewidth=1, offset=emacloudleading, title='Short Leading EMA3')
    mashortline4 = plot(mashort4 if ema4 else na, color=mashortcolor4 if showLine else na, linewidth=1, offset=emacloudleading, title='Short Leading EMA4')
    mashortline5 = plot(mashort5 if ema5 else na, color=mashortcolor5 if showLine else na, linewidth=1, offset=emacloudleading, title='Short Leading EMA5')
    malongcolor1 = color.green if malong1 >= malong1[1] else color.red
    malongcolor2 = color.green if malong2 >= malong2[1] else color.red
    malongcolor3 = color.green if malong3 >= malong3[1] else color.red
    malongcolor4 = color.green if malong4 >= malong4[1] else color.red
    malongcolor5 = color.green if malong5 >= malong5[1] else color.red
    malongline1 = plot(malong1 if ema1 else na, color=malongcolor1 if showLine else na, linewidth=3, offset=emacloudleading, title='Long Leading EMA1')
    malongline2 = plot(malong2 if ema2 else na, color=malongcolor2 if showLine else na, linewidth=3, offset=emacloudleading, title='Long Leading EMA2')
    malongline3 = plot(malong3 if ema3 else na, color=malongcolor3 if showLine else na, linewidth=3, offset=emacloudleading, title='Long Leading EMA3')
    malongline4 = plot(malong4 if ema4 else na, color=malongcolor4 if showLine else na, linewidth=3, offset=emacloudleading, title='Long Leading EMA4')
    malongline5 = plot(malong5 if ema5 else na, color=malongcolor5 if showLine else na, linewidth=3, offset=emacloudleading, title='Long Leading EMA5')
    fill(mashortline1, malongline1, color=color.new(cloudcolour1, 45), title='MA Cloud1')
    fill(mashortline2, malongline2, color=color.new(cloudcolour2, 65), title='MA Cloud2')
    fill(mashortline3, malongline3, color=color.new(cloudcolour3, 70), title='MA Cloud3')
    fill(mashortline4, malongline4, color=color.new(cloudcolour4, 65), title='MA Cloud4')
    fill(mashortline5, malongline5, color=color.new(cloudcolour5, 65), title='MA Cloud5')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
