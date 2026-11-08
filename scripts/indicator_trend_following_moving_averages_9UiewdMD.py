"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, na, plot, script, ta


@script.indicator('Trend Following Moving Averages', overlay=True, na_bool=True)
def main(
    matype=input.string('EMA', title='MA Type', options=('EMA', 'SMA', 'RMA', 'WMA', 'VWMA')),
    prd=input.int(20, title='Period to Check Trend', minval=5),
    rateinp=input.float(1, title='Trend Channel Rate %', minval=0.1, step=0.1),
    ulinreg=input(True, title='Use Linear Regression'),
    linprd=input.int(10, title='Linear Regression Period', minval=2)
):
    rate = rateinp / 100
    pricerange = ta.highest(280) - ta.lowest(280)
    chan = pricerange * rate
    def gettrend(len):
        masrc = ta.ema(close, len) if matype == 'EMA' else ta.rma(close, len) if matype == 'RMA' else ta.vwma(close, len) if matype == 'VWMA' else ta.wma(close, len) if matype == 'WMA' else ta.sma(close, len)
        ma = ta.linreg(masrc, linprd, 0) if ulinreg else masrc
        hh = ta.highest(ma, prd)
        ll = ta.lowest(ma, prd)
        diff = math.abs(hh - ll)
        iff_1 = -1 if ma < hh - chan else 0
        iff_2 = 1 if ma > ll + chan else iff_1
        trend = iff_2 if diff > chan else 0
        _ret = trend * diff / chan
        return _ret

    def getcol(trend):
        _ret = color.new('#00FF00') if trend >= 10.0 else color.new('#00FF00EF') if trend >= 9.0 else color.new('#00FF00DF') if trend >= 8.0 else color.new('#00FF00CF') if trend >= 7.0 else color.new('#00FF00BF') if trend >= 6.0 else color.new('#00FF00AF') if trend >= 5.0 else color.new('#00FF009F') if trend >= 4.0 else color.new('#00FF008F') if trend >= 3.0 else color.new('#00FF007F') if trend >= 2.0 else color.new('#00FF006F') if trend >= 1.0 else color.new('#FF0000') if trend <= -10.0 else color.new('#FF0000EF') if trend <= -9.0 else color.new('#FF0000DF') if trend <= -8.0 else color.new('#FF0000CF') if trend <= -7.0 else color.new('#FF0000BF') if trend <= -6.0 else color.new('#FF0000AF') if trend <= -5.0 else color.new('#FF00009F') if trend <= -4.0 else color.new('#FF00008F') if trend <= -3.0 else color.new('#FF00007F') if trend <= -2.0 else color.new('#FF00006F') if trend <= -1.0 else na
        return _ret

    def getma(lngth):
        _ret = ta.ema(close, lngth) if matype == 'EMA' else ta.rma(close, lngth) if matype == 'RMA' else ta.vwma(close, lngth) if matype == 'VWMA' else ta.wma(close, lngth) if matype == 'WMA' else ta.sma(close, lngth)
        return _ret

    plot(getma(5), color=getcol(gettrend(5)))
    plot(getma(10), color=getcol(gettrend(10)))
    plot(getma(15), color=getcol(gettrend(15)))
    plot(getma(20), color=getcol(gettrend(20)))
    plot(getma(25), color=getcol(gettrend(25)))
    plot(getma(30), color=getcol(gettrend(30)))
    plot(getma(35), color=getcol(gettrend(35)))
    plot(getma(40), color=getcol(gettrend(40)))
    plot(getma(45), color=getcol(gettrend(45)))
    plot(getma(50), color=getcol(gettrend(50)))
    plot(getma(55), color=getcol(gettrend(55)))
    plot(getma(60), color=getcol(gettrend(60)))
    plot(getma(65), color=getcol(gettrend(65)))
    plot(getma(70), color=getcol(gettrend(70)))
    plot(getma(75), color=getcol(gettrend(75)))
    plot(getma(80), color=getcol(gettrend(80)))
    plot(getma(85), color=getcol(gettrend(85)))
    plot(getma(90), color=getcol(gettrend(90)))
    plot(getma(95), color=getcol(gettrend(95)))
    plot(getma(100), color=getcol(gettrend(100)))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)