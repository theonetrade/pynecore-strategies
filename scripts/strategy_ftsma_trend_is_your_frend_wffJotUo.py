"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    close, color, currency, high, input, low, math, na, nz, plot, script,
    strategy, ta
)
from pynecore.types import Series


@script.strategy('FTSMA', overlay=True, precision=6, initial_capital=10000, calc_on_every_tick=True, pyramiding=10, default_qty_type=strategy.fixed, default_qty_value=10000, currency=currency.EUR, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(close, 'Source'),
    slowMA=input(200, 'Slow MA period'),
    mediumMA=input(20, 'Mid MA period'),
    fastMA=input(5, 'Fast MA period'),
    plotSMA=input(True, 'Use MA'),
    sin1=input.int(1, 'First sinusoid', minval=1),
    sin2=input.int(2, 'Second sinusoid', minval=1),
    sin3=input.int(3, 'Third sinusoid', minval=1),
    smoothinput=input.string('EMA', title='MA Type', options=('EMA', 'SMA', 'ALMA', 'FRAMA', 'RMA', 'SWMA', 'VWMA', 'WMA', 'LinearRegression')),
    linearReg=input(False, 'Use linear regression?'),
    linregLenght=input(13, 'Linear regression lenght'),
    linregOffset=input(0, 'Linear regression offset'),
    N=input.int(defval=64, title='Lookback Period', confirm=False, options=(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)),
    inpTakeProfit=input.int(defval=0, title='Take Profit Points', minval=0),
    inpStopLoss=input.int(defval=0, title='Stop Loss Points', minval=0),
    inpTrailStop=input.int(defval=0, title='Trailing Stop Loss Points', minval=0),
    inpTrailOffset=input.int(defval=0, title='Trailing Stop Loss Offset Points', minval=0)
):
    def ma(src, len):
        result: float = 0
        len1: int = len / 2
        frama_SC: int = 200
        frama_FC: int = 1
        e: float = 2.718281828459045
        w = math.log(cast_int(2 / (frama_SC + 1))) / math.log(e)
        H1 = ta.highest(high, len1)
        L1 = ta.lowest(low, len1)
        N1 = (H1 - L1) / len1
        H2_: Series = ta.highest(high, len1)
        H2 = H2_[len1]
        L2_: Series = ta.lowest(low, len1)
        L2 = L2_[len1]
        N2 = (H2 - L2) / len1
        H3 = ta.highest(high, len)
        L3 = ta.lowest(low, len)
        N3 = (H3 - L3) / len
        dimen1: Series = (math.log(N1 + N2) - math.log(N3)) / math.log(2)
        dimen = dimen1 if N1 > 0 and N2 > 0 and (N3 > 0) else nz(dimen1[1])
        alpha1 = math.exp(w * (dimen - 1))
        oldalpha = 1 if alpha1 > 1 else 0.01 if alpha1 < 0.01 else alpha1
        oldN = (2 - oldalpha) / oldalpha
        N = (frama_SC - frama_FC) * (oldN - 1) / (frama_SC - 1) + frama_FC
        alpha_ = 2 / (N + 1)
        alpha = cast_int(2 / (frama_SC + 1)) if alpha_ < cast_int(2 / (frama_SC + 1)) else 1 if alpha_ > 1 else alpha_
        frama: Series[float] = 0.0
        frama = (1 - alpha) * nz(frama[1]) + alpha * src
        result = frama
        return result

    def calc_ma(src, l):
        _ma = ta.sma(src, l) if smoothinput == 'SMA' else ta.ema(src, l) if smoothinput == 'EMA' else ta.wma(src, l) if smoothinput == 'WMA' else ta.linreg(src, l, 0) if smoothinput == 'LinearRegression' else ta.vwma(src, l) if smoothinput == 'VWMA' else ta.rma(src, l) if smoothinput == 'RMA' else ta.alma(src, l, 0.85, 6) if smoothinput == 'ALMA' else ta.swma(src) if smoothinput == 'SWMA' else ma(ta.sma(src, 1), l) if smoothinput == 'FRAMA' else na
        return _ma

    def f_pi(_n):
        _a = 1.0 / (4.0 * _n + 2)
        _b = 1.0 / (6.0 * _n + 3)
        _pi: float = 0.0
        for _i in pine_range(_n - 1, 0, 1):
            _a = 1 / (4.0 * _i + 2) - _a / 4.0
            _b = 1 / (6.0 * _i + 3) - _b / 9.0
        _pi = 4.0 * _a + 4.0 * _b - _pi
        return _pi

    pi = f_pi(20)
    def ReX(k):
        __hist_src__: Series = src[0]
        sum: float = 0.0
        for i in pine_range(0, N - 1, 1):
            sum = sum + __hist_src__[i] * math.cos(2 * pi * k * i / N)
        return_1 = sum
        return return_1

    def ImX(k):
        __hist_src__: Series = src[0]
        sum: float = 0.0
        for i in pine_range(0, N - 1, 1):
            sum = sum + __hist_src__[i] * math.sin(2 * pi * k * i / N)
        return_2 = -sum
        return return_2

    def ReX_(k):
        case: float = 0.0
        if k != 0 and k != N / 2:
            case = 2 * ReX(k) / N
        if k == 0:
            case = ReX(k) / N
        if k == N / 2:
            case = ReX(k) / N
        return_3 = case
        return return_3

    def ImX_(k):
        return_4 = -2 * ImX(k) / N
        return return_4

    def x(i, N):
        sum1: float = 0.0
        sum2: float = 0.0
        for k in pine_range(0, N / 2, 1):
            sum1 = sum1 + ReX_(k) * math.cos(2 * pi * k * i / N)
        for k in pine_range(0, N / 2, 1):
            sum2 = sum2 + ImX_(k) * math.sin(2 * pi * k * i / N)
        return_5 = sum1 + sum2
        return return_5

    def sx(i, k):
        sum1 = ReX_(k) * math.cos(2 * pi * k * i / N)
        sum2 = ImX_(k) * math.sin(2 * pi * k * i / N)
        return_6 = sum1 + sum2
        return return_6

    SLOWMA = calc_ma(close + sx(0, sin1), slowMA) if plotSMA else close + sx(0, sin1)
    MEDMA = calc_ma(close + sx(0, sin2), mediumMA) if plotSMA else close + sx(0, sin2)
    FASTMA = calc_ma(close + sx(0, sin3), fastMA) if plotSMA else close + sx(0, sin3)
    SLOWMA = ta.linreg(SLOWMA, linregLenght, linregOffset) if linearReg else SLOWMA
    MEDMA = ta.linreg(MEDMA, linregLenght, linregOffset) if linearReg else MEDMA
    FASTMA = ta.linreg(FASTMA, linregLenght, linregOffset) if linearReg else FASTMA
    plot(SLOWMA, color=color.new(color.green, 0))
    plot(MEDMA, color=color.new(color.red, 0))
    plot(FASTMA, color=color.new(color.blue, 0))
    useTakeProfit = inpTakeProfit if inpTakeProfit >= 1 else na
    useStopLoss = inpStopLoss if inpStopLoss >= 1 else na
    useTrailStop = inpTrailStop if inpTrailStop >= 1 else na
    useTrailOffset = inpTrailOffset if inpTrailOffset >= 1 else na
    longCondition = FASTMA > MEDMA and close > SLOWMA
    if longCondition:
        strategy.entry('Long Entry', strategy.long)
    shortCondition = FASTMA < MEDMA and close < SLOWMA
    if shortCondition:
        strategy.entry('Short Entry', strategy.short)
    strategy.exit('Exit Buy', from_entry='Long Entry', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)
    strategy.exit('Exit Sell', from_entry='Short Entry', profit=useTakeProfit, loss=useStopLoss, trail_points=useTrailStop, trail_offset=useTrailOffset)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
