"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt_copy
from pynecore.lib import (
    array, barmerge, barstate, box, chart, close, color, extend, format,
    high, input, label, line, linefill, low, map, math, matrix, na, nz, ohlc4, polyline, position,
    request, script, size, strategy, string, syminfo, ta, table, text, time, timeframe, xloc
)
from pynecore.types import (
    Box, Color, Label, Line, NA, Persistent, PersistentSeries, Polyline,
    Series
)
from pynecore.types.chart import ChartPoint
import lib.Trading_IQ.ICTlibrary.v1 as IQ


@script.strategy('ICT Master Suite [Trading IQ]', overlay=True, initial_capital=1000, process_orders_on_close=True, calc_on_every_tick=True, default_qty_type=strategy.percent_of_equity, default_qty_value=5, max_labels_count=500, max_lines_count=500, max_boxes_count=500, max_polylines_count=100, dynamic_requests=True, slippage=2, commission_type=strategy.commission.percent, commission_value=0.02, calc_bars_count=20000, backtest_fill_limits_assumption=2, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    __input_0__=input.timeframe('', title='Timeframe'),
    liteMode=input.bool(defval=False, title='Lite Mode'),
    labelLevels=input.string(defval='Inside', title='Box Label Placement', options=('Inside', 'Outside', 'None')),
    noBorders=input.bool(defval=False, title='No Borders On Levels'),
    labelSize=input.string(defval='Default', title='Label Size', options=('Default', 'Auto', 'Tiny', 'Small', 'Normal')),
    tablePlace=input.string(defval='Top Right', title='Strategy Table Location', options=('Remove Table', 'Top Right', 'Middle Right', 'Bottom Right', 'Top Left', 'Middle Left', 'Bottom Left', 'Top Center', 'Middle Center', 'Bottom Center')),
    tableTxt=input.string(defval='Normal', title='Table Size', options=('Tiny', 'Small', 'Normal')),
    showBOS=input.bool(defval=True, title='Show BoS', group='Market Structure', inline='BoS'),
    boScol=input.color(defval=color.new('#74FFBC'), title='', group='Market Structure', inline='BoS'),
    showMSS=input.bool(defval=True, title='Show MSS', group='Market Structure', inline='MSS'),
    MSScol=input.color(defval=color.rgb(255, 116, 116), title='', group='Market Structure', inline='MSS'),
    bullishOBshow=input.int(minval=0, defval=1, title='Bullish Order Blocks To Show', inline='Bullish OB', group='Blocks'),
    bullishOBcol=input.color(defval=color.new('#74FFBC'), title='', inline='Bullish OB', group='Blocks'),
    bearishOBshow=input.int(minval=0, defval=1, title='Bearish Order Blocks To Show', inline='Bearish OB', group='Blocks'),
    bearishOBcol=input.color(defval=color.rgb(255, 116, 116), title='', inline='Bearish OB', group='Blocks'),
    bullishBBshow=input.int(minval=0, defval=1, title='Bullish Breaker Blocks To Show', inline='Bullish BB', group='Blocks'),
    bullishBBcol=input.color(defval=color.new('#0072FF'), title='', inline='Bullish BB', group='Blocks'),
    bearishBBshow=input.int(minval=0, defval=1, title='Bearish Breaker Blocks To Show', inline='Bearish BB', group='Blocks'),
    bearishBBcol=input.color(defval=color.new('#FF65FB'), title='', inline='Bearish BB', group='Blocks'),
    bullishRBshow=input.int(minval=0, defval=1, title='Bullish Rejection Blocks To Show', inline='Bullish RB', group='Blocks'),
    bullishRBcol=input.color(defval=color.new('#C1FE6D'), title='', inline='Bullish RB', group='Blocks'),
    bearishRBshow=input.int(minval=0, defval=1, title='Bearish Rejection Blocks To Show', inline='Bearish RB', group='Blocks'),
    bearishRBcol=input.color(defval=color.new('#FF854F'), title='', inline='Bearish RB', group='Blocks'),
    strongHighsShow=input.int(minval=0, defval=1, title='Strong Highs To Show', inline='Strong Highs', group='Strong Levels'),
    strongHighscol=input.color(defval=color.rgb(255, 116, 116), title='', inline='Strong Highs', group='Strong Levels'),
    strongLowsShow=input.int(minval=0, defval=1, title='Strong Lows To Show', inline='Strong Lows', group='Strong Levels'),
    strongLowscol=input.color(defval=color.new('#74FFBC'), title='', inline='Strong Lows', group='Strong Levels'),
    onlyFVGliq=input.bool(defval=False, title='Only FVGs Formed After Liquidity Sweep', group='FVG'),
    FVGUpShow=input.int(minval=0, defval=1, title='FVG Up To Show', inline='FVG Up', group='FVG'),
    FVGupcol=input.color(defval=color.new('#74FFBC'), title='', inline='FVG Up', group='FVG'),
    FVGDnShow=input.int(minval=0, defval=1, title='FVG Down To Show', inline='FVG Down', group='FVG'),
    FVGdncol=input.color(defval=color.rgb(255, 116, 116), title='', inline='FVG Down', group='FVG'),
    upDispShow=input.int(minval=0, defval=0, title='Up Displacements To Show', inline='Displacement Up', group='Displacement'),
    dispUpcol=input.color(defval=color.new('#74FFBC'), title='', inline='Displacement Up', group='Displacement'),
    dnDispShow=input.int(minval=0, defval=0, title='Down Displacements To Show', inline='Displacement Down', group='Displacement'),
    dispDncol=input.color(defval=color.rgb(255, 116, 116), title='', inline='Displacement Down', group='Displacement'),
    pbTF=input.timeframe('1D', title='Previous Bar TF', group='Previous Bar Levels And Equal Levels'),
    showpbH=input.bool(defval=True, title='Previous Bar High', group='Previous Bar Levels And Equal Levels', inline='PBH'),
    pdHcol=input.color(defval=color.rgb(255, 116, 116), title='', inline='PBH', group='Previous Bar Levels And Equal Levels'),
    showpbL=input.bool(defval=True, title='Previous Bar Low', group='Previous Bar Levels And Equal Levels', inline='PBL'),
    pdLcol=input.color(defval=color.new('#74FFBC'), title='', inline='PBL', group='Previous Bar Levels And Equal Levels'),
    equalLevels=input.bool(defval=True, title='Show Equal Levels', group='Previous Bar Levels And Equal Levels'),
    equalHighsCol=input.color(defval=color.rgb(255, 116, 116), title='Equal Lows Color', group='Previous Bar Levels And Equal Levels'),
    equalLowsCol=input.color(defval=color.new('#74FFBC'), title='Equal Highs Color', group='Previous Bar Levels And Equal Levels'),
    liqShow=input.bool(defval=True, title='Show Liquidity Sweep', group='Liquidity Sweep'),
    __input_45__=input.int(defval=5, minval=2, maxval=8, title='Liquidity Sweep Aggressiveness', group='Liquidity Sweep'),
    liqText=input.bool(defval=True, title='Liquidity Sweep Text', group='Liquidity Sweep'),
    po3tf=input.timeframe('1D', 'Po3 Timeframe', inline='Po31', group='Power Of Three'),
    showpo3=input.bool(defval=True, title='', inline='Po31', group='Power Of Three'),
    po3tf2=input.timeframe('1W', 'Po3 Timeframe 2', inline='Po32', group='Power Of Three'),
    showpo32=input.bool(defval=True, title='', inline='Po32', group='Power Of Three'),
    showMacros=input.bool(defval=True, title='Show Macros', group='Macros'),
    __input_52__=input.int(defval=6, minval=2, maxval=8, title='Model 2022 Liquidity Sweep Aggressiveness', group='Model 2022'),
    model2022Long__global__=input.bool(defval=True, title='Model 2022 Long', group='Model 2022'),
    long2022nearestFib=input.float(defval=0.5, minval=0, step=0.01, maxval=1, title='Long Entry At FVG Nearest This Fib: ', group='Model 2022'),
    model2022Short__global__=input.bool(defval=True, title='Model 2022 Short', group='Model 2022'),
    short2022nearestFib=input.float(defval=0.5, minval=0, step=0.01, maxval=1, title='Short Entry At FVG Nearest This Fib: ', group='Model 2022'),
    uniLong=input.bool(defval=False, title='Unicorn Long', group='Unicorn Model'),
    uniLongTP=input.enum(IQ.unicornExits.sH, title='Unicorn Long TP', options=(IQ.unicornExits.sH, IQ.unicornExits.zero5, IQ.unicornExits.one5, IQ.unicornExits.two5), group='Unicorn Model'),
    uniLongSL=input.enum(IQ.unicornExits.sL, title='Unicorn Long SL', options=(IQ.unicornExits.sL, IQ.unicornExits.bFVG), group='Unicorn Model'),
    uniLongAdd=input.int(defval=0, title='Subtract Ticks From Long Stop Loss', group='Unicorn Model', minval=0),
    uniShort=input.bool(defval=False, title='Unicorn Short', group='Unicorn Model'),
    uniShortTP=input.enum(IQ.unicornExits.sL, title='Unicorn Short TP', options=(IQ.unicornExits.sL, IQ.unicornExits.zero5, IQ.unicornExits.one5, IQ.unicornExits.two5), group='Unicorn Model'),
    uniShortSL=input.enum(IQ.unicornExits.sH, title='Unicorn Short SL', options=(IQ.unicornExits.sH, IQ.unicornExits.tFVG), group='Unicorn Model'),
    uniShortAdd=input.int(defval=0, title='Add Ticks Short Stop Loss', group='Unicorn Model', minval=0),
    silverBulletStratLong=input.bool(defval=False, title='Silver Bullet Strategy Long', group='Silver Bullet'),
    silverBulletLongTP=input.enum(defval=IQ.silverBulletLevels.sH, title='Silver Bullet Long Strategy TP', options=(IQ.silverBulletLevels.pdH, IQ.silverBulletLevels.sH), group='Silver Bullet'),
    silverBulletLongSL=input.enum(defval=IQ.silverBulletLevels.sL, title='Silver Bullet Long Strategy SL', options=(IQ.silverBulletLevels.pdL, IQ.silverBulletLevels.sL), group='Silver Bullet'),
    silverBulletStratShort=input.bool(defval=False, title='Silver Bullet Strategy Short', group='Silver Bullet'),
    silverBulletShortTP=input.enum(defval=IQ.silverBulletLevels.sL, title='Silver Bullet Short Strategy TP', options=(IQ.silverBulletLevels.pdL, IQ.silverBulletLevels.sL), group='Silver Bullet'),
    silverBulletShortSL=input.enum(defval=IQ.silverBulletLevels.sH, title='Silver Bullet Short Strategy SL', options=(IQ.silverBulletLevels.pdH, IQ.silverBulletLevels.sH), group='Silver Bullet'),
    lRaidSessions=input.session('1330-1600', title='Session Range (New York Time)', group='Liquidity Raid'),
    longLiquidityRaid=input.bool(defval=False, title='Trade Long Liquidity Raid', group='Liquidity Raid'),
    tpLongLiquidityRaid=input.string(defval='Swing High', title='Long Liquidity Raid TP', options=('Swing High', 'Use Fib (Option Below)'), group='Liquidity Raid'),
    slLongLiquidityRaid=input.string(defval='Swing Low', title='Long Liquidity Raid SL', options=('Swing Low', 'Breakerblock Bottom', 'Use Fib (Option Below)'), group='Liquidity Raid'),
    liquidityRaidFibTP=input.float(defval=-0.5, title='Fib TP (Optional)', group='Liquidity Raid', inline='LRLfib'),
    liquidityRaidFibSL=input.float(defval=-0.5, title='Fib SL (Optional)', group='Liquidity Raid', inline='LRLfib'),
    shortLiquidityRaid=input.bool(defval=False, title='Trade Short Liquidity Raid', group='Liquidity Raid'),
    tpShortLiquidityRaid=input.string(defval='Swing Low', title='Short Liquidity Raid TP', options=('Swing Low', 'Use Fib (Option Below)'), group='Liquidity Raid'),
    slShortLiquidityRaid=input.string(defval='Swing High', title='Short Liquidity Raid SL', options=('Swing High', 'Breakerblock Top', 'Use Fib (Option Below)'), group='Liquidity Raid'),
    liquidityRaidFibTPshort=input.float(defval=-0.5, title='Fib TP (Optional)', group='Liquidity Raid', inline='LRSfib'),
    liquidityRaidFibSLshort=input.float(defval=-0.5, title='Fib SL (Optional)', group='Liquidity Raid', inline='LRSfib'),
    oteLongs=input.bool(defval=False, title='OTE Longs', group='Optimal Trade Entry'),
    longOTElevel=input.float(defval=0.79, title='Long Entry Retracement Level', options=(0.79, 0.705, 0.62), group='Optimal Trade Entry'),
    longOTEPT=input.string(defval='-0.5', title='Long TP', options=('-0.5', '-1', '-2', 'Swing High'), group='Optimal Trade Entry'),
    longOTESL=input.int(defval=0, title='How Many Ticks Below Swing Low For Stop Loss', group='Optimal Trade Entry'),
    oteShorts=input.bool(defval=False, title='OTE Shorts', group='Optimal Trade Entry'),
    shortOTElevel=input.float(defval=0.79, title='Short Entry Retracement Level', options=(0.79, 0.705, 0.62), group='Optimal Trade Entry'),
    shortOTEPT=input.string(defval='-0.5', title='Short TP', options=('-0.5', '-1', '-2', 'Swing Low'), group='Optimal Trade Entry'),
    shortOTESL=input.int(defval=0, title='How Many Ticks Above Swing Low For Stop Loss', group='Optimal Trade Entry')
):
    userTF = timeframe.in_seconds(__input_0__)
    liqSweepAgg = 10 - __input_45__
    liqSweepAgg2022 = 10 - __input_52__
    buffer: int = 0
    model2022: Persistent[bool] = False
    if model2022Long__global__ or model2022Short__global__:
        model2022 = True
        onlyFVGliq = True
        liqSweepAgg = liqSweepAgg2022
    upRejections: Persistent[list[IQ.rejectionBlocks]] = array.new(0, NA(IQ.rejectionBlocks))
    dnRejections: Persistent[list[IQ.rejectionBlocks]] = array.new(0, NA(IQ.rejectionBlocks))
    upFVGpricesSorted: Persistent[list[float]] = array.new_float()
    dnFVGpricesSorted: Persistent[list[float]] = array.new_float()
    upRejectionsPrices: Persistent[list[float]] = array.new_float()
    dnRejectionsPrices: Persistent[list[float]] = array.new_float()
    masterCoords: dict[str, float] = map.new()
    takeFVGs: Persistent[dict[str, int]] = map.new()
    if map.size(takeFVGs) == 0:
        map.put(takeFVGs, 'Up', 0)
        map.put(takeFVGs, 'Down', 0)
    future = time('', -1)
    timen5 = time('', -5)
    finalTF: Persistent = timeframe.from_seconds(math.max(timeframe.in_seconds(''), userTF))
    def getSwings(tf):
        atr = ta.atr(14)
        return (high[1], low[1], ta.pivothigh(3, 3), ta.pivotlow(3, 3), high[2], low, high, low[2], atr * 0.05, atr * 2, atr, atr * liqSweepAgg, time[3], time[1])

    pdH, pdL, getPH, getPL, H2, L, H, L2, threshold, atrTF, atrTFreg, atrLiqSweep, time3, time1 = request.security(syminfo.tickerid, finalTF, getSwings(finalTF))
    historicalData, logZ = IQ.necessaryData(atrTF)
    __block_result__ = na
    __switch__ = noBorders
    if __switch__ == True:
        __block_result__ = 100
    else:
        __block_result__ = 0
    borderTransp: Persistent = __block_result__
    def getOB():
        atr = nz(atrTFreg)
        lower: PersistentSeries[float] = 2e+21
        higher: PersistentSeries[float] = 0.0
        isRange: Persistent[bool] = False
        if lower == lower[10]:
            isRange = True
        lower = math.min(lower, low)
        higher = math.max(higher, high)
        bullishOBbox: Persistent[list[IQ.orderBlock]] = array.new(0, NA(IQ.orderBlock))
        bearishOBbox: Persistent[list[IQ.orderBlock]] = array.new(0, NA(IQ.orderBlock))
        IQ.invalidBlockCheck(bullishOBbox, bearishOBbox, userTF)
        if higher != higher[1]:
            if isRange:
                if logZ >= 2:
                    method_call('OB', bullishOBbox, historicalData.highArr, historicalData.signArr, historicalData.lowArr, historicalData.timeArr, -1)
                elif logZ <= -2:
                    method_call('OB', bullishOBbox, historicalData.highArr, historicalData.signArr, historicalData.lowArr, historicalData.timeArr, 1)
                isRange = False
            lower = low - atr
            higher = high + atr
        elif lower != lower[1]:
            if isRange:
                if logZ >= 2:
                    method_call('OB', bearishOBbox, historicalData.highArr, historicalData.signArr, historicalData.lowArr, historicalData.timeArr, -1)
                elif logZ <= -2:
                    method_call('OB', bearishOBbox, historicalData.highArr, historicalData.signArr, historicalData.lowArr, historicalData.timeArr, 1)
                isRange = False
            higher = high + atr
            lower = low - atr
        method_call('OBdraw', bullishOBbox, bullishOBshow, bearishBBshow, bullishOBcol, bearishBBcol, 'Bullish OB', 'Bearish BB', True, labelLevels, borderTransp, liteMode, timen5, masterCoords)
        method_call('OBdraw', bearishOBbox, bearishOBshow, bullishBBshow, bearishOBcol, bullishBBcol, 'Bearish OB', 'Bullish BB', False, labelLevels, borderTransp, liteMode, timen5, masterCoords)
        return (bullishOBbox, bearishOBbox)

    def zzLiq(atr: float, buffer: float, FVGarr: list[IQ.FVG]):
        __block_result_1__ = na
        if liqShow or onlyFVGliq or model2022:
            point__0000019b__: Persistent = close
            timeP: Persistent = time
            dir: Persistent[int] = 0
            cPoint__0000019b__: Persistent[ChartPoint] = na(ChartPoint)
            pPoint__0000019b__: Persistent[ChartPoint] = na(ChartPoint)
            p2Point: Persistent[ChartPoint] = na(ChartPoint)
            sweepPoint: Persistent[ChartPoint] = na(ChartPoint)
            sweepPointDn: Persistent[ChartPoint] = na(ChartPoint)
            mostRecentPoint: Persistent[float] = 0.0
            sweepPointArr: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
            upSweepArr: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
            upSweepDispose: Persistent[list[int]] = array.new_int()
            sweepPointArrDn: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
            dnSweepArr: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
            dnSweepDispose: Persistent[list[int]] = array.new_int()
            sweepUpHighPoint: Persistent[float] = 0.0
            sweepDnLowPoint: Persistent[float] = 2e+21
            sweepData__0000019b__: Persistent[IQ.sweeps] = IQ.sweeps.new(matrix.new(4, 0, initial_value=NA(float)), matrix.new(4, 0, initial_value=NA(float)), array.new_box(), array.new_box())
            if dir == 1:
                point__0000019b__ = math.max(point__0000019b__, high)
                __block_result_2__ = na
                __switch_2__ = high == point__0000019b__
                if __switch_2__ == True:
                    __block_result_2__ = time
                else:
                    __block_result_2__ = timeP
                timeP = __block_result_2__
                cPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                addition = math.abs(point__0000019b__ - pPoint__0000019b__.price) * buffer
                if low <= point__0000019b__ - atrLiqSweep - addition and high != point__0000019b__:
                    if not na(p2Point):
                        sweepPoint = udt_copy(p2Point)
                        array.push(sweepPointArr, sweepPoint)
                    if not na(sweepPointDn) and (not na(p2Point)):
                        if array.size(sweepPointArrDn) >= 2:
                            if array.size(dnSweepArr) == 0:
                                getPlow = p2Point
                                getClow = cPoint__0000019b__
                                if not array.includes(dnSweepDispose, getClow.time) and (not array.includes(dnSweepDispose, getPlow.time)):
                                    if getClow.price >= getPlow.price - atrTFreg and getClow.price <= getPlow.price + atrTFreg:
                                        sweepDnLowPoint = array.last(sweepPointArrDn).price
                                        array.push(dnSweepArr, getPlow)
                                        array.push(dnSweepArr, getClow)
                            else:
                                getClow = p2Point
                                getFirst = array.first(dnSweepArr)
                                if getClow.price >= getFirst.price - atrTFreg and getClow.price <= getFirst.price + atrTFreg:
                                    sweepDnLowPoint = math.min(array.last(sweepPointArrDn).price, sweepDnLowPoint)
                                    array.push(dnSweepArr, getClow)
                                else:
                                    array.clear(dnSweepArr)
                                    sweepDnLowPoint = 2e+21
                                    getPlow = array.get(sweepPointArrDn, array.size(sweepPointArrDn) - 2)
                                    if not array.includes(dnSweepDispose, getClow.time) and (not array.includes(dnSweepDispose, getPlow.time)):
                                        if getClow.price >= getPlow.price - atrTFreg and getClow.price <= getPlow.price + atrTFreg:
                                            sweepDnLowPoint = array.last(sweepPointArrDn).price
                                            array.push(dnSweepArr, getPlow)
                                            array.push(dnSweepArr, getClow)
                    if not na(p2Point):
                        sweepPointDn = udt_copy(p2Point)
                        array.push(sweepPointArrDn, sweepPointDn)
                    if not na(pPoint__0000019b__):
                        p2Point = udt_copy(pPoint__0000019b__)
                    pPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                    cPoint__0000019b__ = chart.point.from_time(time, low)
                    dir = -1
                    point__0000019b__ = low
                    timeP = time
            elif dir == -1:
                point__0000019b__ = math.min(low, point__0000019b__)
                __block_result_3__ = na
                __switch_2__ = low == point__0000019b__
                if __switch_2__ == True:
                    __block_result_3__ = time
                else:
                    __block_result_3__ = timeP
                timeP = __block_result_3__
                cPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                addition = math.abs(point__0000019b__ - pPoint__0000019b__.price) * buffer
                if high >= point__0000019b__ + atr + addition and low != point__0000019b__:
                    if not na(p2Point):
                        sweepPointDn = udt_copy(p2Point)
                        array.push(sweepPointArrDn, sweepPointDn)
                    if not na(sweepPoint) and (not na(p2Point)):
                        if array.size(sweepPointArr) >= 2:
                            if array.size(upSweepArr) == 0:
                                getPlow = p2Point
                                getClow = cPoint__0000019b__
                                if not array.includes(upSweepDispose, getClow.time) and (not array.includes(upSweepDispose, getPlow.time)):
                                    if getClow.price >= getPlow.price - atrTFreg and getClow.price <= getPlow.price + atrTFreg:
                                        sweepUpHighPoint = array.last(sweepPointArr).price
                                        array.push(upSweepArr, getPlow)
                                        array.push(upSweepArr, getClow)
                            else:
                                getClow = p2Point
                                getFirst = array.first(upSweepArr)
                                if getClow.price >= getFirst.price - atrTFreg and getClow.price <= getFirst.price + atrTFreg:
                                    sweepUpHighPoint = math.max(array.last(sweepPointArr).price, sweepUpHighPoint)
                                    array.push(upSweepArr, getClow)
                                else:
                                    array.clear(upSweepArr)
                                    sweepUpHighPoint = 0
                                    getPlow = array.get(sweepPointArr, array.size(sweepPointArr) - 2)
                                    if not array.includes(upSweepDispose, getClow.time) and (not array.includes(upSweepDispose, getPlow.time)):
                                        if getClow.price >= getPlow.price - atrTFreg and getClow.price <= getPlow.price + atrTFreg:
                                            sweepUpHighPoint = array.last(sweepPointArr).price
                                            array.push(upSweepArr, getPlow)
                                            array.push(upSweepArr, getClow)
                    if not na(p2Point):
                        sweepPoint = udt_copy(p2Point)
                        array.push(sweepPointArr, sweepPoint)
                    if not na(pPoint__0000019b__):
                        p2Point = udt_copy(pPoint__0000019b__)
                    pPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                    cPoint__0000019b__ = chart.point.from_time(time, high)
                    dir = 1
                    point__0000019b__ = high
                    timeP = time
            if dir == 0:
                if high >= point__0000019b__ + atr:
                    if not na(pPoint__0000019b__):
                        p2Point = udt_copy(pPoint__0000019b__)
                    pPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                    cPoint__0000019b__ = chart.point.from_time(time, high)
                    dir = 1
                    point__0000019b__ = high
                    timeP = time
                elif low <= point__0000019b__ + atr:
                    if not na(pPoint__0000019b__):
                        p2Point = udt_copy(pPoint__0000019b__)
                    pPoint__0000019b__ = chart.point.from_time(timeP, point__0000019b__)
                    cPoint__0000019b__ = chart.point.from_time(time, low)
                    dir = -1
                    point__0000019b__ = low
                    timeP = time
            if IQ.isLastBar(userTF) and liqShow:
                if array.size(upSweepArr) > 0 and sweepUpHighPoint != 0 and barstate.isconfirmed and IQ.isLastBar(userTF):
                    if close >= sweepUpHighPoint + atrTFreg:
                        topSweep: float = 0.0
                        botSweep: float = 2e+21
                        for data in upSweepArr:
                            topSweep = math.max(topSweep, data.price)
                            botSweep = math.min(botSweep, data.price)
                            array.push(upSweepDispose, data.time)
                        if not method_call('includes', method_call('row', sweepData__0000019b__.upSweeps, 0), array.first(upSweepArr).time):
                            method_call('add_col', sweepData__0000019b__.upSweeps, method_call('columns', sweepData__0000019b__.upSweeps), array.from_items(array.first(upSweepArr).time, topSweep, time, botSweep))
                            if onlyFVGliq:
                                map.put(takeFVGs, 'Up', 1)
                                for i in pine_range(method_call('indexof', historicalData.timeArr, array.last(upSweepArr).time), 1, 1):
                                    if i + 2 < method_call('size', historicalData.timeArr):
                                        getH2 = method_call('get', historicalData.highArr, i + 2)
                                        getL = method_call('get', historicalData.lowArr, i)
                                        getT = method_call('get', historicalData.timeArr, i + 1)
                                        if getH2 < getL:
                                            array.unshift(FVGarr, IQ.FVG.new(getH2, getL, 'Up', getT))
                                            array.insert(upFVGpricesSorted, array.binary_search_rightmost(upFVGpricesSorted, getH2), getH2)
                                            map.put(takeFVGs, 'Up', 2)
                            sweepUpHighPoint = 0
                            array.clear(upSweepArr)
                if array.size(dnSweepArr) > 0 and sweepDnLowPoint != 2e+21 and barstate.isconfirmed and IQ.isLastBar(userTF):
                    if close <= sweepDnLowPoint - atrTFreg:
                        topSweep: float = 0.0
                        botSweep: float = 2e+21
                        for data in dnSweepArr:
                            topSweep = math.max(topSweep, data.price)
                            botSweep = math.min(botSweep, data.price)
                            array.push(dnSweepDispose, data.time)
                        if not method_call('includes', method_call('row', sweepData__0000019b__.dnSweeps, 0), array.first(dnSweepArr).time):
                            method_call('add_col', sweepData__0000019b__.dnSweeps, method_call('columns', sweepData__0000019b__.dnSweeps), array.from_items(array.first(dnSweepArr).time, topSweep, time, botSweep))
                            if onlyFVGliq:
                                map.put(takeFVGs, 'Down', 1)
                                for i in pine_range(method_call('indexof', historicalData.timeArr, array.last(dnSweepArr).time), 1, 1):
                                    if i + 2 < method_call('size', historicalData.timeArr):
                                        getH = method_call('get', historicalData.highArr, i)
                                        getL2 = method_call('get', historicalData.lowArr, i + 2)
                                        getT = method_call('get', historicalData.timeArr, i + 1)
                                        if getL2 > getH:
                                            array.unshift(FVGarr, IQ.FVG.new(getH, getL2, 'Down', getT))
                                            array.insert(dnFVGpricesSorted, array.binary_search_rightmost(dnFVGpricesSorted, getL2), getL2)
                                            map.put(takeFVGs, 'Down', 2)
                            sweepDnLowPoint = 2e+21
                            array.clear(dnSweepArr)
            if barstate.islast:
                if method_call('size', sweepData__0000019b__.upSweepDrawings) > 0:
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(method_call('size', sweepData__0000019b__.upSweepDrawings) - 1):
                        i = __loop_3__.value
                        method_call('delete', method_call('shift', sweepData__0000019b__.upSweepDrawings))
                if method_call('size', sweepData__0000019b__.dnSweepDrawings) > 0:
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(method_call('size', sweepData__0000019b__.dnSweepDrawings) - 1):
                        i = __loop_3__.value
                        method_call('delete', method_call('shift', sweepData__0000019b__.dnSweepDrawings))
                if method_call('columns', sweepData__0000019b__.upSweeps) > 0:
                    outlineFirst: Persistent[Polyline] = na(Polyline)
                    polyline.delete(outlineFirst)
                    getCols = method_call('columns', sweepData__0000019b__.upSweeps)
                    for i in pine_range(0, getCols - 1, 1):
                        getStartTime = cast_int(method_call('get', sweepData__0000019b__.upSweeps, 0, i))
                        getTop = method_call('get', sweepData__0000019b__.upSweeps, 1, i)
                        getEndTime = cast_int(method_call('get', sweepData__0000019b__.upSweeps, 2, i))
                        getBot = method_call('get', sweepData__0000019b__.upSweeps, 3, i)
                        method_call('push', sweepData__0000019b__.upSweepDrawings, box.new(getStartTime, getTop, getEndTime, getBot, bgcolor=color.new(color.new('#6929F2'), 90), text='Liquidity Sweep' if liqText else '', text_color=chart.fg_color, text_halign=text.align_left, text_size=size.auto, text_wrap=text.wrap_auto, xloc=xloc.bar_time, border_color=color.new(color.new('#6929F2'), borderTransp)))
                        if i == getCols - 1 and (not noBorders) and (not liteMode):
                            points = array.from_items(chart.point.from_time(getStartTime, getTop), chart.point.from_time(getEndTime, getTop), chart.point.from_time(getEndTime, getBot), chart.point.from_time(getStartTime, getBot))
                            outlineFirst = polyline.new(points, closed=True, xloc=xloc.bar_time, line_width=5, line_color=color.new(color.new('#6929F2'), 80))
                if method_call('columns', sweepData__0000019b__.dnSweeps) > 0:
                    outlineFirst: Persistent[Polyline] = na(Polyline)
                    polyline.delete(outlineFirst)
                    getCols = method_call('columns', sweepData__0000019b__.dnSweeps)
                    for i in pine_range(0, getCols - 1, 1):
                        getStartTime = cast_int(method_call('get', sweepData__0000019b__.dnSweeps, 0, i))
                        getTop = method_call('get', sweepData__0000019b__.dnSweeps, 1, i)
                        getEndTime = cast_int(method_call('get', sweepData__0000019b__.dnSweeps, 2, i))
                        getBot = method_call('get', sweepData__0000019b__.dnSweeps, 3, i)
                        method_call('push', sweepData__0000019b__.dnSweepDrawings, box.new(cast_int(method_call('get', sweepData__0000019b__.dnSweeps, 0, i)), method_call('get', sweepData__0000019b__.dnSweeps, 1, i), cast_int(method_call('get', sweepData__0000019b__.dnSweeps, 2, i)), method_call('get', sweepData__0000019b__.dnSweeps, 3, i), bgcolor=color.new(color.new('#F24968'), 90), text='Liquidity Sweep' if liqText else '', text_color=chart.fg_color, text_halign=text.align_left, text_size=size.auto, text_wrap=text.wrap_auto, xloc=xloc.bar_time, border_color=color.new(color.new('#F24968'), borderTransp)))
                        if i == getCols - 1 and (not noBorders) and (not liteMode):
                            points = array.from_items(chart.point.from_time(getStartTime, getTop), chart.point.from_time(getEndTime, getTop), chart.point.from_time(getEndTime, getBot), chart.point.from_time(getStartTime, getBot))
                            outlineFirst = polyline.new(points, closed=True, xloc=xloc.bar_time, line_width=5, line_color=color.new(color.new('#F24968'), 80))
            __block_result_1__ = sweepData__0000019b__
        return __block_result_1__

    def zz(atr: float, buffer: float):
        strongHighSorted: Persistent[list[float]] = array.new_float()
        strongLowSorted: Persistent[list[float]] = array.new_float()
        point__000002a6__: Persistent = close
        pointTrail: Persistent = close
        timeP: Persistent = time
        dir: Persistent[int] = 0
        cPoint: Persistent[ChartPoint] = na(ChartPoint)
        pPoint: Persistent[ChartPoint] = na(ChartPoint)
        p2Point: Persistent[ChartPoint] = na(ChartPoint)
        bosUpL: Persistent[list[IQ.labelLine]] = array.new(0, NA(IQ.labelLine))
        choUpL: Persistent[list[IQ.labelLine]] = array.new(0, NA(IQ.labelLine))
        bosDnL: Persistent[list[IQ.labelLine]] = array.new(0, NA(IQ.labelLine))
        mssDnL: Persistent[list[IQ.labelLine]] = array.new(0, NA(IQ.labelLine))
        strongHighs: Persistent[list[IQ.strongPoints]] = array.new(0, NA(IQ.strongPoints))
        strongLows: Persistent[list[IQ.strongPoints]] = array.new(0, NA(IQ.strongPoints))
        structureDirection: Persistent[str] = ''
        mostRecentPoint: Persistent[float] = 0.0
        historicalPoints: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
        OTEstart: Persistent[ChartPoint] = chart.point.now()
        if IQ.isLastBar(userTF):
            if close > array.min(strongHighSorted) and barstate.isconfirmed and IQ.isLastBar(userTF):
                for i in pine_range(array.size(strongHighs) - 1, 0, 1):
                    data = array.get(strongHighs, i)
                    if close > data.price:
                        method_call('delete', data.strongPointLabel)
                        method_call('delete', data.strongPointLine)
                        array.remove(strongHighs, i)
                        array.remove(strongHighSorted, i)
            if close < array.max(strongLowSorted) and barstate.isconfirmed and IQ.isLastBar(userTF):
                for i in pine_range(array.size(strongLows) - 1, 0, 1):
                    data = array.get(strongLows, i)
                    if close < data.price:
                        method_call('delete', data.strongPointLabel)
                        method_call('delete', data.strongPointLine)
                        array.remove(strongLows, i)
                        array.remove(strongLowSorted, i)
        if barstate.islast:
            if array.size(strongHighs) > 0:
                for i in pine_range(0, array.size(strongHighs) - 1, 1):
                    getStrongHigh = array.get(strongHighs, i)
                    method_call('delete', getStrongHigh.strongPointLabel)
                    method_call('delete', getStrongHigh.strongPointLine)
                    if not na(getStrongHigh.overlayLine):
                        method_call('delete', getStrongHigh.overlayLine)
                        method_call('delete', getStrongHigh.overlayLine2)
                    getHighTime = getStrongHigh.timeAtprice
                    getHigh = getStrongHigh.price
                    if i < strongHighsShow:
                        getStrongHigh.strongPointLabel = label.new(getHighTime, getHigh, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=strongHighscol, text='Strong High', size=size.tiny)
                        getStrongHigh.strongPointLine = line.new(getHighTime, getHigh, timen5, getHigh, xloc=xloc.bar_time, color=strongHighscol, style=line.style_dashed)
                        if i == 0:
                            getIndex = method_call('indexof', historicalData.timeArr, getHighTime)
                            if getIndex > 150:
                                method_call('set_x', getStrongHigh.strongPointLabel, timen5)
                            if not liteMode:
                                futTime__5 = getIndex + 1 < method_call('size', historicalData.timeArr)
                                __block_result_4__ = na
                                __switch_6__ = futTime__5
                                if __switch_6__ == True:
                                    __block_result_4__ = method_call('get', historicalData.timeArr, getIndex + 1)
                                else:
                                    __block_result_4__ = time('', -1)
                                futTime = __block_result_4__
                                pTime = method_call('get', historicalData.timeArr, getIndex - 1)
                                getStrongHigh.overlayLine = line.new(pTime, getHigh, futTime, getHigh, width=2, color=strongHighscol, xloc=xloc.bar_time)
                                getStrongHigh.overlayLine2 = line.new(pTime, getHigh, futTime, getHigh, width=5, color=color.new(strongHighscol, 80), xloc=xloc.bar_time)
                    if na(map.get(masterCoords, 'Strong High')) and strongHighsShow != 0:
                        map.put(masterCoords, 'Strong High', method_call('get_y2', getStrongHigh.strongPointLine))
            if array.size(strongLows) > 0:
                for i in pine_range(0, array.size(strongLows) - 1, 1):
                    getStrongLow = array.get(strongLows, i)
                    method_call('delete', getStrongLow.strongPointLabel)
                    method_call('delete', getStrongLow.strongPointLine)
                    if not na(getStrongLow.overlayLine):
                        method_call('delete', getStrongLow.overlayLine)
                        method_call('delete', getStrongLow.overlayLine2)
                    getLowTime = getStrongLow.timeAtprice
                    getLow = getStrongLow.price
                    if i < strongLowsShow:
                        getStrongLow.strongPointLabel = label.new(getLowTime, getLow, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=strongLowscol, text='Strong Low', size=size.tiny, style=label.style_label_up)
                        getStrongLow.strongPointLine = line.new(getLowTime, getLow, timen5, getLow, xloc=xloc.bar_time, color=strongLowscol, style=line.style_dashed)
                        if i == 0:
                            getIndex = method_call('indexof', historicalData.timeArr, getLowTime)
                            if getIndex > 150:
                                method_call('set_x', getStrongLow.strongPointLabel, timen5)
                            if not liteMode:
                                futTime__7 = getIndex + 1 < method_call('size', historicalData.timeArr)
                                __block_result_5__ = na
                                __switch_6__ = futTime__7
                                if __switch_6__ == True:
                                    __block_result_5__ = method_call('get', historicalData.timeArr, getIndex + 1)
                                else:
                                    __block_result_5__ = time('', -1)
                                futTime = __block_result_5__
                                pTime = method_call('get', historicalData.timeArr, getIndex - 1)
                                getStrongLow.overlayLine = line.new(pTime, getLow, futTime, getLow, width=2, color=strongLowscol, xloc=xloc.bar_time)
                                getStrongLow.overlayLine2 = line.new(pTime, getLow, futTime, getLow, width=5, color=color.new(strongLowscol, 80), xloc=xloc.bar_time)
                    if na(map.get(masterCoords, 'Strong Low')) and strongLowsShow != 0:
                        map.put(masterCoords, 'Strong Low', method_call('get_y2', getStrongLow.strongPointLine))
        if dir == 1:
            if not na(p2Point):
                if structureDirection == 'Up':
                    if close[1] <= p2Point.price and close > p2Point.price and barstate.isconfirmed and IQ.isLastBar(userTF):
                        if p2Point.price != mostRecentPoint:
                            if array.size(bosUpL) == 0:
                                method_call('drawBos', bosUpL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, False)
                                mostRecentPoint = p2Point.price
                                startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                method_call('getStrongLow', strongLows, startIndex, historicalData.timeArr, historicalData.lowArr, strongLowSorted)
                            else:
                                if p2Point.price != method_call('get_y2', array.last(bosUpL).lin):
                                    method_call('drawBos', bosUpL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, False)
                                    mostRecentPoint = p2Point.price
                                    startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                    method_call('getStrongLow', strongLows, startIndex, historicalData.timeArr, historicalData.lowArr, strongLowSorted)
                elif structureDirection == 'Down':
                    if close[1] <= p2Point.price and close > p2Point.price:
                        if p2Point.price != mostRecentPoint:
                            if array.size(mssDnL) == 0:
                                method_call('drawMSS', mssDnL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, False, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                mostRecentPoint = p2Point.price
                                structureDirection = 'Up'
                                OTEstart = udt_copy(pPoint)
                            else:
                                if p2Point.price != method_call('get_y2', array.last(mssDnL).lin):
                                    method_call('drawMSS', mssDnL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, False, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                    mostRecentPoint = p2Point.price
                                    structureDirection = 'Up'
                                    OTEstart = udt_copy(pPoint)
            point__000002a6__ = math.max(point__000002a6__, high)
            __block_result_6__ = na
            __switch_1__ = high == point__000002a6__
            if __switch_1__ == True:
                __block_result_6__ = time
            else:
                __block_result_6__ = timeP
            timeP = __block_result_6__
            cPoint = chart.point.from_time(timeP, point__000002a6__)
            addition = math.abs(point__000002a6__ - pPoint.price) * buffer
            if low <= point__000002a6__ - atr - addition and high != point__000002a6__:
                if not na(pPoint):
                    p2Point = udt_copy(pPoint)
                    if close < p2Point.price and barstate.isconfirmed and IQ.isLastBar(userTF):
                        if structureDirection == 'Up':
                            if p2Point.price != mostRecentPoint:
                                if array.size(choUpL) == 0:
                                    method_call('drawMSS', choUpL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, True, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                    mostRecentPoint = p2Point.price
                                    structureDirection = 'Down'
                                    OTEstart = udt_copy(cPoint)
                                else:
                                    if p2Point.price != method_call('get_y2', array.last(choUpL).lin):
                                        method_call('drawMSS', choUpL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, True, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                        mostRecentPoint = p2Point.price
                                        structureDirection = 'Down'
                                        OTEstart = udt_copy(cPoint)
                        elif structureDirection == 'Down':
                            if p2Point.price != mostRecentPoint:
                                if array.size(bosDnL) == 0:
                                    method_call('drawBos', bosDnL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, True)
                                    mostRecentPoint = p2Point.price
                                    startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                    method_call('getStrongHigh', strongHighs, startIndex, historicalData.timeArr, historicalData.highArr, strongHighSorted)
                                else:
                                    if p2Point.price != method_call('get_y2', array.last(bosDnL).lin):
                                        method_call('drawBos', bosDnL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, True)
                                        mostRecentPoint = p2Point.price
                                        startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                        method_call('getStrongHigh', strongHighs, startIndex, historicalData.timeArr, historicalData.highArr, strongHighSorted)
                pPoint = chart.point.from_time(timeP, point__000002a6__)
                cPoint = chart.point.from_time(time, low)
                array.unshift(historicalPoints, pPoint)
                dir = -1
                point__000002a6__ = low
                timeP = time
        elif dir == -1:
            if not na(p2Point):
                if structureDirection == 'Up':
                    if close[1] > p2Point.price and close <= p2Point.price and barstate.isconfirmed and IQ.isLastBar(userTF):
                        if p2Point.price != mostRecentPoint:
                            if array.size(choUpL) == 0:
                                method_call('drawMSS', choUpL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, True, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                mostRecentPoint = p2Point.price
                                structureDirection = 'Down'
                                OTEstart = udt_copy(pPoint)
                            else:
                                if p2Point.price != method_call('get_y2', array.last(choUpL).lin):
                                    method_call('drawMSS', choUpL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, True, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                    mostRecentPoint = p2Point.price
                                    structureDirection = 'Down'
                                    OTEstart = udt_copy(pPoint)
                elif structureDirection == 'Down':
                    if close[1] > p2Point.price and close <= p2Point.price and barstate.isconfirmed and IQ.isLastBar(userTF):
                        if p2Point.price != mostRecentPoint:
                            if array.size(bosDnL) == 0:
                                method_call('drawBos', bosDnL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, True)
                                mostRecentPoint = p2Point.price
                                startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                method_call('getStrongHigh', strongHighs, startIndex, historicalData.timeArr, historicalData.highArr, strongHighSorted)
                            else:
                                if p2Point.price != method_call('get_y2', array.last(bosDnL).lin):
                                    method_call('drawBos', bosDnL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, True)
                                    mostRecentPoint = p2Point.price
                                    startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                    method_call('getStrongHigh', strongHighs, startIndex, historicalData.timeArr, historicalData.highArr, strongHighSorted)
            point__000002a6__ = math.min(low, point__000002a6__)
            __block_result_7__ = na
            __switch_1__ = low == point__000002a6__
            if __switch_1__ == True:
                __block_result_7__ = time
            else:
                __block_result_7__ = timeP
            timeP = __block_result_7__
            cPoint = chart.point.from_time(timeP, point__000002a6__)
            addition = math.abs(point__000002a6__ - pPoint.price) * buffer
            if high >= point__000002a6__ + atr + addition and low != point__000002a6__:
                if not na(pPoint):
                    p2Point = udt_copy(pPoint)
                    if close > p2Point.price and barstate.isconfirmed and IQ.isLastBar(userTF):
                        if structureDirection == 'Up':
                            if p2Point.price != mostRecentPoint:
                                if array.size(bosUpL) == 0:
                                    method_call('drawBos', bosUpL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, False)
                                    mostRecentPoint = p2Point.price
                                    startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                    method_call('getStrongLow', strongLows, startIndex, historicalData.timeArr, historicalData.lowArr, strongLowSorted)
                                else:
                                    if p2Point.price != method_call('get_y2', array.last(bosUpL).lin):
                                        method_call('drawBos', bosUpL, p2Point, p2Point.time, p2Point.price, boScol, showBOS, False)
                                        mostRecentPoint = p2Point.price
                                        startIndex = method_call('indexof', historicalData.timeArr, p2Point.time)
                                        method_call('getStrongLow', strongLows, startIndex, historicalData.timeArr, historicalData.lowArr, strongLowSorted)
                        elif structureDirection == 'Down':
                            if p2Point.price != mostRecentPoint:
                                if array.size(mssDnL) == 0:
                                    method_call('drawMSS', mssDnL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, False, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                    mostRecentPoint = p2Point.price
                                    structureDirection = 'Up'
                                    OTEstart = udt_copy(cPoint)
                                else:
                                    if p2Point.price != method_call('get_y2', array.last(mssDnL).lin):
                                        method_call('drawMSS', mssDnL, p2Point, p2Point.time, p2Point.price, MSScol, showMSS, False, upRejections, dnRejections, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, historicalData.closeArr, historicalData.openArr, historicalData.atrTFarr, upRejectionsPrices, dnRejectionsPrices)
                                        mostRecentPoint = p2Point.price
                                        structureDirection = 'Up'
                                        OTEstart = udt_copy(cPoint)
                pPoint = chart.point.from_time(timeP, point__000002a6__)
                cPoint = chart.point.from_time(time, high)
                array.unshift(historicalPoints, pPoint)
                dir = 1
                point__000002a6__ = high
                timeP = time
        if dir == 0:
            if high >= point__000002a6__ + atr:
                if not na(pPoint):
                    p2Point = udt_copy(pPoint)
                pPoint = chart.point.from_time(timeP, point__000002a6__)
                cPoint = chart.point.from_time(time, high)
                array.unshift(historicalPoints, pPoint)
                dir = 1
                pointTrail = point__000002a6__
                point__000002a6__ = high
                timeP = time
                structureDirection = 'Up'
            elif low <= point__000002a6__ + atr:
                if not na(pPoint):
                    p2Point = udt_copy(pPoint)
                pPoint = chart.point.from_time(timeP, point__000002a6__)
                cPoint = chart.point.from_time(time, low)
                array.unshift(historicalPoints, pPoint)
                dir = -1
                pointTrail = point__000002a6__
                point__000002a6__ = low
                timeP = time
                structureDirection = 'Down'
        return (cPoint, pPoint, p2Point, structureDirection, OTEstart, historicalPoints, dir)

    cPoint, pPoint, getKeyPoint, structureDirection, OTEstart, historicalPoints, trendDir = zz(atrTF, buffer)
    def model2022Long(sweepData__0000032f__: IQ.sweeps, FVGarr: list[IQ.FVG]):
        __block_result_8__ = na
        if model2022Long__global__:
            includesSweep: Persistent[list[int]] = array.new_int()
            trailingSweep: Persistent[int] = 0
            longFVGdrawings: Persistent[IQ.m2022] = IQ.m2022.new()
            openTrades = strategy.opentrades - 1
            closedTrades = strategy.closedtrades - 1
            getHighestHigh: Persistent[float] = 0.0
            if IQ.checkIfTraded('Long 2022 Model'):
                array.push(includesSweep, trailingSweep)
                method_call('set_right', longFVGdrawings.longFVGentryBox, time)
                if not na(longFVGdrawings.sweepData):
                    secondLow: ChartPoint = na(ChartPoint)
                    peak: ChartPoint = na(ChartPoint)
                    secondHigh: ChartPoint = na(ChartPoint)
                    startTimeIndex = method_call('binary_search_leftmost', historicalData.binaryTimeArr, cast_int(method_call('get', longFVGdrawings.sweepData, 0)))
                    startTime = method_call('get', historicalData.binaryTimeArr, startTimeIndex)
                    binaryLowArr = udt_copy(historicalData.lowArr)
                    method_call('reverse', binaryLowArr)
                    binaryHighArr = udt_copy(historicalData.highArr)
                    method_call('reverse', binaryHighArr)
                    initialLow = chart.point.from_time(startTime, method_call('get', binaryLowArr, startTimeIndex))
                    peak = chart.point.from_time(startTime, method_call('get', binaryHighArr, startTimeIndex))
                    __block_result_9__ = na
                    if method_call('get', longFVGdrawings.sweepData, 3) == initialLow.price:
                        __block_result_9__ = method_call('get', longFVGdrawings.sweepData, 1)
                    else:
                        __block_result_9__ = method_call('get', longFVGdrawings.sweepData, 3)
                    secondLowPrice = __block_result_9__
                    isActive: bool = False
                    __loop_3__ = pine_loop(startTimeIndex, 1)
                    while __loop_3__.step(method_call('size', historicalData.binaryTimeArr) - 1):
                        i = __loop_3__.value
                        getHigh = method_call('get', binaryHighArr, i)
                        getLow = method_call('get', binaryLowArr, i)
                        if getLow == secondLowPrice and (not isActive) or (isActive and getLow <= secondLowPrice):
                            getTime = method_call('get', historicalData.binaryTimeArr, i)
                            sliceHigh = method_call('slice', binaryHighArr, startTimeIndex, i + 1)
                            sliceTime = method_call('slice', historicalData.binaryTimeArr, startTimeIndex, i + 1)
                            getHighest = method_call('lastindexof', sliceHigh, method_call('max', sliceHigh))
                            peak = chart.point.from_time(method_call('get', sliceTime, getHighest), method_call('max', sliceHigh))
                            secondLow = chart.point.from_time(getTime, getLow)
                            secondHigh = chart.point.from_time(getTime, getHigh)
                            secondLowPrice = getLow
                            isActive = True
                        if not na(secondHigh):
                            if getHigh >= secondHigh.price:
                                secondHigh = chart.point.from_time(method_call('get', historicalData.binaryTimeArr, i), getHigh)
                    points = array.from_items(chart.point.from_time(cast_int(method_call('get', longFVGdrawings.sweepData, 0)), method_call('get', longFVGdrawings.sweepData, 1)), peak, secondLow, secondHigh, chart.point.from_time(time, method_call('get_top', longFVGdrawings.longFVGentryBox)))
                    polyline.new(points, xloc=xloc.bar_time, line_width=2, line_color=color.new('#74FFBC'))
                longFVGdrawings.longFVGentryBox = NA(Box)
            if IQ.checkIfClosed('Long 2022 Model'):
                longFVGdrawings.line0P = NA(Line)
                longFVGdrawings.line50P = NA(Line)
                longFVGdrawings.line100P = NA(Line)
                longFVGdrawings.label0P = NA(Label)
                longFVGdrawings.label50P = NA(Label)
                longFVGdrawings.label100P = NA(Label)
                longFVGdrawings.mEntryDistance = 2e+21
            if not na(longFVGdrawings.line0P):
                method_call('set_x2', longFVGdrawings.line0P, future)
                method_call('set_x2', longFVGdrawings.line50P, future)
                method_call('set_x2', longFVGdrawings.line100P, future)
                method_call('set_x', longFVGdrawings.label0P, future)
                method_call('set_x', longFVGdrawings.label50P, future)
                method_call('set_x', longFVGdrawings.label100P, future)
            __block_result_10__ = na
            if method_call('columns', sweepData__0000032f__.upSweeps) > 0:
                getSweepTimeUp = method_call('get', sweepData__0000032f__.upSweeps, 0, method_call('columns', sweepData__0000032f__.upSweeps) - 1)
                m2022LongLevels: IQ.m2022 = IQ.m2022.new()
                if strategy.opentrades == 0:
                    if trailingSweep != getSweepTimeUp or close >= method_call('get_y1', longFVGdrawings.line0P) + atrTFreg * 10:
                        strategy.cancel('Long 2022 Model')
                        array.push(includesSweep, cast_int(trailingSweep))
                        getHighestHigh = 0.0
                        longFVGdrawings.mEntryDistance = 2e+21
                        longFVGdrawings.mIndex = NA(int)
                        method_call('delete', longFVGdrawings.label0P)
                        method_call('delete', longFVGdrawings.label50P)
                        method_call('delete', longFVGdrawings.label100P)
                        method_call('delete', longFVGdrawings.longFVGentryBox)
                        method_call('delete', longFVGdrawings.line0P)
                        method_call('delete', longFVGdrawings.line50P)
                        method_call('delete', longFVGdrawings.line100P)
                if strategy.position_size < 0:
                    strategy.cancel('Long 2022 Model')
                    getHighestHigh = 0.0
                    longFVGdrawings.mEntryDistance = 2e+21
                    longFVGdrawings.mIndex = NA(int)
                    method_call('delete', longFVGdrawings.label0P)
                    method_call('delete', longFVGdrawings.label50P)
                    method_call('delete', longFVGdrawings.label100P)
                    method_call('delete', longFVGdrawings.longFVGentryBox)
                    method_call('delete', longFVGdrawings.line0P)
                    method_call('delete', longFVGdrawings.line50P)
                    method_call('delete', longFVGdrawings.line100P)
                if not array.includes(includesSweep, cast_int(getSweepTimeUp)) and strategy.opentrades == 0:
                    if high > getHighestHigh:
                        longFVGdrawings.mEntryDistance = 2e+21
                    getHighestHigh = math.max(high, getHighestHigh)
                    Lx = method_call('get', sweepData__0000032f__.upSweeps, 3, method_call('columns', sweepData__0000032f__.upSweeps) - 1)
                    getRange = Lx + (getHighestHigh - Lx) * long2022nearestFib
                    for i, data in enumerate(FVGarr):
                        if data.direction == 'Up':
                            if close > math.max(data.H, data.L) and math.max(data.H, data.L) >= Lx:
                                longFVGdrawings.mEntryDistance = math.min(math.abs(math.max(data.H, data.L) - getRange), longFVGdrawings.mEntryDistance)
                                if longFVGdrawings.mEntryDistance == math.abs(math.max(data.H, data.L) - getRange):
                                    m2022LongLevels.mIndex = i
                                    m2022LongLevels.mTime = data.T
                                    m2022LongLevels.mEntry = math.max(data.H, data.L)
                                    m2022LongLevels.fvgHigh = m2022LongLevels.mEntry
                                    m2022LongLevels.fvgLow = math.min(data.H, data.L)
                    if not na(m2022LongLevels.mIndex):
                        method_call('delete', longFVGdrawings.longFVGentryBox)
                        method_call('delete', longFVGdrawings.line0P)
                        method_call('delete', longFVGdrawings.line50P)
                        method_call('delete', longFVGdrawings.line100P)
                        method_call('delete', longFVGdrawings.label0P)
                        method_call('delete', longFVGdrawings.label50P)
                        method_call('delete', longFVGdrawings.label100P)
                        longFVGdrawings.longFVGentryBox = box.new(m2022LongLevels.mTime, m2022LongLevels.fvgHigh, time, m2022LongLevels.fvgLow, xloc=xloc.bar_time, bgcolor=color.new(color.new('#74FFBC'), 95), border_color=color.new(color.new('#74FFBC'), borderTransp), text='FVG', text_size=size.small, text_halign=text.align_left, text_color=chart.fg_color)
                        getLow = method_call('get', sweepData__0000032f__.upSweeps, 3, method_call('columns', sweepData__0000032f__.upSweeps) - 1)
                        longFVGdrawings.line0P = line.new(m2022LongLevels.mTime, getLow, time, getLow, xloc=xloc.bar_time, color=color.red, style=line.style_dotted)
                        longFVGdrawings.line50P = line.new(m2022LongLevels.mTime, getRange, time, getRange, xloc=xloc.bar_time, color=color.gray, style=line.style_dotted)
                        longFVGdrawings.line100P = line.new(m2022LongLevels.mTime, getHighestHigh, time, getHighestHigh, xloc=xloc.bar_time, color=color.new('#74FFBC'), style=line.style_dotted)
                        linefill.new(longFVGdrawings.line0P, longFVGdrawings.line100P, color.new(chart.fg_color, 95))
                        longFVGdrawings.label0P = label.new(time, getLow, xloc=xloc.bar_time, textcolor=color.red, size=size.small, text='0%', style=label.style_label_upper_right, color=color.new('#00000000'))
                        longFVGdrawings.label50P = label.new(time, getRange, xloc=xloc.bar_time, textcolor=color.gray, size=size.small, text=string.tostring(long2022nearestFib * 100, format.percent), style=label.style_label_left, color=color.new('#00000000'))
                        longFVGdrawings.label100P = label.new(time, getHighestHigh, xloc=xloc.bar_time, textcolor=color.new('#74FFBC'), size=size.small, text='100%', style=label.style_label_lower_right, color=color.new('#00000000'))
                        longFVGdrawings.sweepData = udt_copy(method_call('col', sweepData__0000032f__.upSweeps, method_call('columns', sweepData__0000032f__.upSweeps) - 1))
                        strategy.entry('Long 2022 Model', strategy.long, limit=m2022LongLevels.mEntry)
                        strategy.exit('L2', 'Long 2022 Model', limit=getHighestHigh, stop=getLow)
                trailingSweep = cast_int(getSweepTimeUp)
                __block_result_10__ = trailingSweep
            __block_result_8__ = __block_result_10__
        return __block_result_8__

    def model2022Short(sweepData__000003b7__: IQ.sweeps, FVGarr: list[IQ.FVG]):
        __block_result_11__ = na
        if model2022Short__global__:
            includesSweep: Persistent[list[int]] = array.new_int()
            trailingSweep: Persistent[int] = 0
            shortFVGdrawings: Persistent[IQ.m2022] = IQ.m2022.new()
            openTrades = strategy.opentrades - 1
            closedTrades = strategy.closedtrades - 1
            getLowestLow: Persistent[float] = 0.0
            if IQ.checkIfTraded('Short 2022 Model'):
                array.push(includesSweep, trailingSweep)
                method_call('set_right', shortFVGdrawings.shortFVGentryBox, time)
                if not na(shortFVGdrawings.sweepData):
                    secondHigh: ChartPoint = na(ChartPoint)
                    trough: ChartPoint = na(ChartPoint)
                    secondLow: ChartPoint = na(ChartPoint)
                    startTimeIndex = method_call('binary_search_leftmost', historicalData.binaryTimeArr, cast_int(method_call('get', shortFVGdrawings.sweepData, 0)))
                    startTime = method_call('get', historicalData.binaryTimeArr, startTimeIndex)
                    binaryLowArr = udt_copy(historicalData.lowArr)
                    method_call('reverse', binaryLowArr)
                    binaryHighArr = udt_copy(historicalData.highArr)
                    method_call('reverse', binaryHighArr)
                    initialHigh = chart.point.from_time(startTime, method_call('get', binaryHighArr, startTimeIndex))
                    trough = chart.point.from_time(startTime, method_call('get', binaryLowArr, startTimeIndex))
                    __block_result_12__ = na
                    if method_call('get', shortFVGdrawings.sweepData, 3) == initialHigh.price:
                        __block_result_12__ = method_call('get', shortFVGdrawings.sweepData, 1)
                    else:
                        __block_result_12__ = method_call('get', shortFVGdrawings.sweepData, 3)
                    secondHighPrice = __block_result_12__
                    isActive: bool = False
                    __loop_3__ = pine_loop(startTimeIndex, 1)
                    while __loop_3__.step(method_call('size', historicalData.binaryTimeArr) - 1):
                        i = __loop_3__.value
                        getHigh = method_call('get', binaryHighArr, i)
                        getLow = method_call('get', binaryLowArr, i)
                        if getHigh == secondHighPrice and (not isActive) or (isActive and getHigh >= secondHighPrice):
                            getTime = method_call('get', historicalData.binaryTimeArr, i)
                            sliceLow = method_call('slice', binaryLowArr, startTimeIndex, i + 1)
                            sliceTime = method_call('slice', historicalData.binaryTimeArr, startTimeIndex, i + 1)
                            getLowest = method_call('lastindexof', sliceLow, method_call('min', sliceLow))
                            trough = chart.point.from_time(method_call('get', sliceTime, getLowest), method_call('min', sliceLow))
                            secondHigh = chart.point.from_time(getTime, getHigh)
                            secondLow = chart.point.from_time(getTime, getLow)
                            secondHighPrice = getHigh
                            isActive = True
                        if not na(secondLow):
                            if getLow <= secondLow.price:
                                secondLow = chart.point.from_time(method_call('get', historicalData.binaryTimeArr, i), getLow)
                    points = array.from_items(chart.point.from_time(cast_int(method_call('get', shortFVGdrawings.sweepData, 0)), method_call('get', shortFVGdrawings.sweepData, 1)), trough, secondHigh, secondLow, chart.point.from_time(time, method_call('get_bottom', shortFVGdrawings.shortFVGentryBox)))
                    polyline.new(points, xloc=xloc.bar_time, line_width=2, line_color=color.new('#74FFBC'))
                shortFVGdrawings.shortFVGentryBox = NA(Box)
            if IQ.checkIfClosed('Short 2022 Model'):
                shortFVGdrawings.line0P = NA(Line)
                shortFVGdrawings.line50P = NA(Line)
                shortFVGdrawings.line100P = NA(Line)
                shortFVGdrawings.label0P = NA(Label)
                shortFVGdrawings.label50P = NA(Label)
                shortFVGdrawings.label100P = NA(Label)
                shortFVGdrawings.mEntryDistance = 2e+21
            if not na(shortFVGdrawings.line0P):
                method_call('set_x2', shortFVGdrawings.line0P, future)
                method_call('set_x2', shortFVGdrawings.line50P, future)
                method_call('set_x2', shortFVGdrawings.line100P, future)
                method_call('set_x', shortFVGdrawings.label0P, future)
                method_call('set_x', shortFVGdrawings.label50P, future)
                method_call('set_x', shortFVGdrawings.label100P, future)
            __block_result_13__ = na
            if method_call('columns', sweepData__000003b7__.dnSweeps) > 0:
                getSweepTimeDn = method_call('get', sweepData__000003b7__.dnSweeps, 0, method_call('columns', sweepData__000003b7__.dnSweeps) - 1)
                m2022ShortLevels: IQ.m2022 = IQ.m2022.new()
                if strategy.opentrades == 0:
                    if trailingSweep != getSweepTimeDn or close <= method_call('get_y1', shortFVGdrawings.line0P) - atrTFreg * 10:
                        strategy.cancel('Short 2022 Model')
                        array.push(includesSweep, cast_int(trailingSweep))
                        getLowestLow = 2e+21
                        shortFVGdrawings.mEntryDistance = 2e+21
                        shortFVGdrawings.mIndex = NA(int)
                        m2022ShortLevels.mTime = time
                        method_call('delete', shortFVGdrawings.line0P)
                        method_call('delete', shortFVGdrawings.line50P)
                        method_call('delete', shortFVGdrawings.line100P)
                        method_call('delete', shortFVGdrawings.shortFVGentryBox)
                        method_call('delete', shortFVGdrawings.label0P)
                        method_call('delete', shortFVGdrawings.label50P)
                        method_call('delete', shortFVGdrawings.label100P)
                if strategy.position_size > 0:
                    strategy.cancel('Short 2022 Model')
                    getLowestLow = 2e+21
                    shortFVGdrawings.mEntryDistance = 2e+21
                    shortFVGdrawings.mIndex = NA(int)
                    method_call('delete', shortFVGdrawings.line0P)
                    method_call('delete', shortFVGdrawings.line50P)
                    method_call('delete', shortFVGdrawings.line100P)
                    method_call('delete', shortFVGdrawings.shortFVGentryBox)
                    method_call('delete', shortFVGdrawings.label0P)
                    method_call('delete', shortFVGdrawings.label50P)
                    method_call('delete', shortFVGdrawings.label100P)
                if not array.includes(includesSweep, cast_int(getSweepTimeDn)) and strategy.opentrades == 0:
                    if low < getLowestLow:
                        shortFVGdrawings.mEntryDistance = 2e+21
                    getLowestLow = math.min(low, getLowestLow)
                    Hx = method_call('get', sweepData__000003b7__.dnSweeps, 1, method_call('columns', sweepData__000003b7__.dnSweeps) - 1)
                    getRange = Hx + (getLowestLow - Hx) * short2022nearestFib
                    for i, data in enumerate(FVGarr):
                        if data.direction == 'Down':
                            if close < math.min(data.H, data.L) and math.min(data.H, data.L) <= Hx:
                                shortFVGdrawings.mEntryDistance = math.min(math.abs(math.min(data.H, data.L) - getRange), shortFVGdrawings.mEntryDistance)
                                if shortFVGdrawings.mEntryDistance == math.abs(math.min(data.H, data.L) - getRange):
                                    m2022ShortLevels.mIndex = i
                                    m2022ShortLevels.mTime = data.T
                                    m2022ShortLevels.mEntry = math.min(data.H, data.L)
                                    m2022ShortLevels.fvgHigh = math.max(data.H, data.L)
                                    m2022ShortLevels.fvgLow = m2022ShortLevels.mEntry
                    if not na(m2022ShortLevels.mIndex):
                        method_call('delete', shortFVGdrawings.shortFVGentryBox)
                        method_call('delete', shortFVGdrawings.line0P)
                        method_call('delete', shortFVGdrawings.line50P)
                        method_call('delete', shortFVGdrawings.line100P)
                        method_call('delete', shortFVGdrawings.label0P)
                        method_call('delete', shortFVGdrawings.label50P)
                        method_call('delete', shortFVGdrawings.label100P)
                        shortFVGdrawings.shortFVGentryBox = box.new(m2022ShortLevels.mTime, m2022ShortLevels.fvgHigh, time, m2022ShortLevels.fvgLow, xloc=xloc.bar_time, bgcolor=color.new(color.red, 95), border_color=color.new(color.red, borderTransp), text='FVG', text_size=size.small, text_halign=text.align_left, text_color=chart.fg_color)
                        getHigh = method_call('get', sweepData__000003b7__.dnSweeps, 1, method_call('columns', sweepData__000003b7__.dnSweeps) - 1)
                        shortFVGdrawings.line0P = line.new(m2022ShortLevels.mTime, getHigh, time, getHigh, xloc=xloc.bar_time, color=color.red, style=line.style_dotted)
                        shortFVGdrawings.line50P = line.new(m2022ShortLevels.mTime, getRange, time, getRange, xloc=xloc.bar_time, color=color.gray, style=line.style_dotted)
                        shortFVGdrawings.line100P = line.new(m2022ShortLevels.mTime, getLowestLow, time, getLowestLow, xloc=xloc.bar_time, color=color.new('#74FFBC'), style=line.style_dotted)
                        linefill.new(shortFVGdrawings.line0P, shortFVGdrawings.line100P, color.new(chart.fg_color, 95))
                        shortFVGdrawings.label0P = label.new(time, getHigh, xloc=xloc.bar_time, textcolor=color.red, size=size.small, text='0%', style=label.style_label_lower_right, color=color.new('#00000000'))
                        shortFVGdrawings.label50P = label.new(time, getRange, xloc=xloc.bar_time, textcolor=color.gray, size=size.small, text=string.tostring(short2022nearestFib * 100, format.percent), style=label.style_label_left, color=color.new('#00000000'))
                        shortFVGdrawings.label100P = label.new(time, getLowestLow, xloc=xloc.bar_time, textcolor=color.new('#74FFBC'), size=size.small, text='100%', style=label.style_label_upper_right, color=color.new('#00000000'))
                        strategy.entry('Short 2022 Model', strategy.short, limit=m2022ShortLevels.mEntry)
                        strategy.exit('L2', 'Short 2022 Model', limit=getLowestLow, stop=getHigh)
                        shortFVGdrawings.sweepData = udt_copy(method_call('col', sweepData__000003b7__.dnSweeps, method_call('columns', sweepData__000003b7__.dnSweeps) - 1))
                trailingSweep = cast_int(getSweepTimeDn)
                __block_result_13__ = trailingSweep
            __block_result_11__ = __block_result_13__
        return __block_result_11__

    @method
    def unicornExitRemove(points: IQ.unicornModel, strategyName: str, isLong: bool):
        openTrades = strategy.opentrades - 1
        closedTrades = strategy.closedtrades - 1
        if IQ.checkIfClosed(strategyName):
            if isLong:
                switch_var_13 = strategy.closedtrades.exit_price(closedTrades) >= strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_13
                if __switch_2__ == True:
                    points.tpLine = NA(Line)
                    points.tpLabel = NA(Label)
                    method_call('delete', points.slLine)
                    method_call('delete', points.slLabel)
                else:
                    method_call('delete', points.tpLine)
                    method_call('delete', points.tpLabel)
                    points.slLine = NA(Line)
                    points.slLabel = NA(Label)
            else:
                switch_var_15 = strategy.closedtrades.exit_price(closedTrades) <= strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_15
                if __switch_2__ == True:
                    points.tpLine = NA(Line)
                    points.tpLabel = NA(Label)
                    method_call('delete', points.slLine)
                    method_call('delete', points.slLabel)
                else:
                    method_call('delete', points.tpLine)
                    method_call('delete', points.tpLabel)
                    points.slLine = NA(Line)
                    points.slLabel = NA(Label)
        return 0

    def unicorn(bearishOBbox: list[IQ.orderBlock], FVGarr: list[IQ.FVG], bullishOBbox: list[IQ.orderBlock]):
        __block_result_14__ = na
        if (uniLong or uniShort) and method_call('size', historicalPoints) >= 10:
            getPrevPoint = method_call('get', historicalPoints, 1)
            getPrevPoint2 = method_call('get', historicalPoints, 2)
            getPrevPoint3 = method_call('get', historicalPoints, 3)
            longPoints: Persistent[IQ.unicornModel] = IQ.unicornModel.new(includes=array.new_int())
            shortPoints: Persistent[IQ.unicornModel] = IQ.unicornModel.new(includes=array.new_int())
            if strategy.opentrades > 0:
                strategy.cancel('Long Unicorn')
                strategy.cancel('Short Unicorn')
            if not na(longPoints.hPoint):
                if IQ.checkIfTraded('Long Unicorn'):
                    method_call('push', longPoints.includes, getPrevPoint2.time)
                    points = array.from_items(chart.point.from_time(time, longPoints.entry))
                    for dataPoints in historicalPoints:
                        __switch_4__ = dataPoints.time >= longPoints.hPoint3.time
                        if __switch_4__ == True:
                            method_call('push', points, dataPoints)
                        else:
                            break
                    polyline.new(points, xloc=xloc.bar_time, line_color=color.new('#74FFBC'), line_width=2)
                    method_call('set_right', longPoints.breakerBlock, time)
                    method_call('set_right', longPoints.FVG, time)
                    longPoints.breakerBlock = NA(Box)
                    longPoints.FVG = NA(Box)
                    longPoints.topBlock = NA(float)
                    longPoints.botBlock = NA(float)
                    longPoints.startBlock = NA(int)
                    unicornExitRemove(longPoints, 'Long Unicorn', True)
                if not na(longPoints.tpLine):
                    method_call('set_x2', longPoints.tpLine, future)
                    method_call('set_x', longPoints.tpLabel, future)
                    method_call('set_x2', longPoints.slLine, future)
                    method_call('set_x', longPoints.slLabel, future)
                    unicornExitRemove(longPoints, 'Long Unicorn', True)
                longRange = math.abs(longPoints.hPoint.price - longPoints.hPoint2.price)
                if barstate.isconfirmed and IQ.isLastBar(userTF):
                    if low <= longPoints.hPoint.price or cPoint.price >= longPoints.hPoint2.price + longRange or method_call('first', historicalPoints).price >= longPoints.hPoint2.price + longRange:
                        strategy.cancel('Long Unicorn')
                        longPoints.hPoint = na
                        longPoints.hPoint2 = na
                        longPoints.hPoint3 = na
                        method_call('push', longPoints.includes, getPrevPoint2.time)
                        method_call('delete', longPoints.breakerBlock)
                        method_call('delete', longPoints.FVG)
                        longPoints.topBlock = NA(float)
                        longPoints.botBlock = NA(float)
                        longPoints.startBlock = NA(int)
            if not na(shortPoints.hPoint):
                if IQ.checkIfTraded('Short Unicorn'):
                    method_call('push', shortPoints.includes, getPrevPoint2.time)
                    points = array.from_items(chart.point.from_time(time, shortPoints.entry))
                    for dataPoints in historicalPoints:
                        __switch_4__ = dataPoints.time >= shortPoints.hPoint3.time
                        if __switch_4__ == True:
                            method_call('push', points, dataPoints)
                        else:
                            break
                    polyline.new(points, xloc=xloc.bar_time, line_color=color.new('#74FFBC'), line_width=2)
                    method_call('set_right', shortPoints.breakerBlock, time)
                    method_call('set_right', shortPoints.FVG, time)
                    shortPoints.breakerBlock = NA(Box)
                    shortPoints.FVG = NA(Box)
                    shortPoints.topBlock = NA(float)
                    shortPoints.botBlock = NA(float)
                    shortPoints.startBlock = NA(int)
                    unicornExitRemove(shortPoints, 'Short Unicorn', False)
                if not na(shortPoints.tpLine):
                    method_call('set_x2', shortPoints.tpLine, future)
                    method_call('set_x', shortPoints.tpLabel, future)
                    method_call('set_x2', shortPoints.slLine, future)
                    method_call('set_x', shortPoints.slLabel, future)
                    unicornExitRemove(shortPoints, 'Short Unicorn', False)
                shortRange = math.abs(shortPoints.hPoint.price - shortPoints.hPoint2.price)
                if barstate.isconfirmed and IQ.isLastBar(userTF):
                    if high >= shortPoints.hPoint.price or cPoint.price <= shortPoints.hPoint2.price - shortRange or method_call('first', historicalPoints).price <= shortPoints.hPoint2.price - shortRange:
                        strategy.cancel('Short Unicorn')
                        shortPoints.hPoint = na
                        shortPoints.hPoint2 = na
                        shortPoints.hPoint3 = na
                        method_call('delete', shortPoints.breakerBlock)
                        method_call('delete', shortPoints.FVG)
                        shortPoints.topBlock = NA(float)
                        shortPoints.botBlock = NA(float)
                        shortPoints.startBlock = NA(int)
                        method_call('push', shortPoints.includes, getPrevPoint2.time)
            __block_result_15__ = na
            if barstate.isconfirmed and IQ.isLastBar(userTF) and (strategy.opentrades == 0):
                if strategy.opentrades == 0 and (not method_call('includes', longPoints.includes, getPrevPoint2.time)) and uniLong:
                    if getPrevPoint2.price > getPrevPoint.price and close >= getPrevPoint2.price and (getPrevPoint.price < getPrevPoint3.price):
                        if array.size(bearishOBbox) > 0 and array.size(FVGarr) > 0:
                            getEntry: Persistent[float] = 0.0
                            for i, block in enumerate(bearishOBbox):
                                if block.status == 'BB':
                                    getBox = array.get(bearishOBbox, i)
                                    getStart = method_call('first', getBox.orderBlockData)
                                    if method_call('get', getBox.orderBlockData, 3) >= getPrevPoint.price and getStart >= getPrevPoint3.time:
                                        longPoints.topBlock = method_call('get', getBox.orderBlockData, 1)
                                        longPoints.botBlock = method_call('get', getBox.orderBlockData, 3)
                                        longPoints.startBlock = cast_int(getStart)
                                        break
                            for FVG__0000044f__ in FVGarr:
                                if FVG__0000044f__.direction == 'Up' and FVG__0000044f__.T >= getPrevPoint3.time:
                                    highest = math.max(FVG__0000044f__.H, FVG__0000044f__.L)
                                    lowest = math.min(FVG__0000044f__.H, FVG__0000044f__.L)
                                    if close >= highest:
                                        statusPoss = highest >= longPoints.topBlock and lowest <= longPoints.topBlock or (highest >= longPoints.botBlock and lowest <= longPoints.botBlock) or (highest >= longPoints.topBlock and lowest <= longPoints.botBlock) or (highest <= longPoints.topBlock and lowest >= longPoints.botBlock)
                                        if statusPoss:
                                            longPoints.entry = math.min(highest, longPoints.topBlock)
                                            longPoints.hPoint = getPrevPoint
                                            longPoints.hPoint2 = getPrevPoint2
                                            longPoints.hPoint3 = getPrevPoint3
                                            slTime = cast_int(longPoints.startBlock)
                                            slStr: str = 'Breakerblock SL'
                                            __block_result_16__ = na
                                            __switch_9__ = uniLongSL
                                            if __switch_9__ == IQ.unicornExits.bFVG:
                                                __block_result_16__ = math.min(lowest, longPoints.botBlock) - uniLongAdd * syminfo.mintick
                                            else:
                                                __block_result_16__ = longPoints.hPoint.price - uniLongAdd * syminfo.mintick
                                            sl = __block_result_16__
                                            if sl == lowest - uniLongAdd * syminfo.mintick:
                                                slTime = FVG__0000044f__.T
                                                slStr = 'FVG SL'
                                            if sl == longPoints.hPoint.price - uniLongAdd * syminfo.mintick:
                                                slTime = longPoints.hPoint.time
                                                slStr = 'Swing Low SL'
                                            tp = NA(float)
                                            tpTime = NA(int)
                                            tpStr = NA(str)
                                            if uniLongTP == IQ.unicornExits.sH:
                                                for data in historicalPoints:
                                                    if data.price > longPoints.entry:
                                                        tp = data.price
                                                        tpTime = data.time
                                                        tpStr = 'Swing High'
                                                        break
                                            else:
                                                getFib: float = 0.0
                                                __switch_10__ = uniLongTP
                                                if __switch_10__ == IQ.unicornExits.zero5:
                                                    getFib = -0.5
                                                    tpStr = 'Fib -0.5'
                                                elif __switch_10__ == IQ.unicornExits.one5:
                                                    getFib = -1
                                                    tpStr = 'Fib -1'
                                                else:
                                                    getFib = -2
                                                    tpStr = 'Fib -2'
                                                tpTime = method_call('first', historicalPoints).time
                                                tp = method_call('first', historicalPoints).price - (method_call('first', historicalPoints).price - longPoints.hPoint.price) * getFib
                                            if not na(tp):
                                                strategy.entry('Long Unicorn', strategy.long, limit=longPoints.entry)
                                                strategy.exit('Long Unicorn Exit', 'Long Unicorn', limit=tp, stop=sl)
                                                method_call('delete', longPoints.FVG)
                                                method_call('delete', longPoints.breakerBlock)
                                                longPoints.FVG = box.new(FVG__0000044f__.T, highest, future, lowest, border_color=color.new(color.new('#74FFBC'), borderTransp), bgcolor=color.new(color.new('#74FFBC'), 95), xloc=xloc.bar_time, text='FVG', text_color=chart.fg_color, text_size=size.small, text_halign=text.align_left)
                                                longPoints.breakerBlock = box.new(longPoints.startBlock, longPoints.topBlock, future, longPoints.botBlock, bgcolor=color.new(color.blue, 95), border_color=color.new(color.blue, borderTransp), xloc=xloc.bar_time, text='Breaker Block', text_color=chart.fg_color, text_size=size.small, text_halign=text.align_left)
                                                method_call('delete', longPoints.tpLine)
                                                method_call('delete', longPoints.tpLabel)
                                                method_call('delete', longPoints.slLine)
                                                method_call('delete', longPoints.slLabel)
                                                longPoints.tpLine = line.new(chart.point.from_time(tpTime, tp), chart.point.from_time(future, tp), xloc=xloc.bar_time, style=line.style_dotted, color=color.new('#74FFBC'))
                                                longPoints.tpLabel = label.new(future, tp, xloc=xloc.bar_time, color=color.new('#00000000'), style=label.style_label_lower_right, textcolor=color.new('#74FFBC'), size=size.small, text=tpStr)
                                                longPoints.slLine = line.new(chart.point.from_time(slTime, sl), chart.point.from_time(future, sl), xloc=xloc.bar_time, style=line.style_dotted, color=color.red)
                                                longPoints.slLabel = label.new(future, sl, xloc=xloc.bar_time, color=color.new('#00000000'), style=label.style_label_upper_right, textcolor=color.red, size=size.small, text=slStr)
                                            break
                __block_result_17__ = na
                if strategy.opentrades == 0 and (not method_call('includes', shortPoints.includes, getPrevPoint2.time)) and uniShort:
                    __block_result_18__ = na
                    if getPrevPoint2.price < getPrevPoint.price and close <= getPrevPoint2.price and (getPrevPoint.price > getPrevPoint3.price):
                        __block_result_19__ = na
                        if array.size(bullishOBbox) > 0 and array.size(FVGarr) > 0:
                            getEntry: Persistent[float] = 0.0
                            for i, block in enumerate(bullishOBbox):
                                if block.status == 'BB':
                                    getBox = array.get(bullishOBbox, i)
                                    getStart = method_call('first', getBox.orderBlockData)
                                    if method_call('get', getBox.orderBlockData, 3) <= getPrevPoint.price and getStart >= getPrevPoint3.time:
                                        shortPoints.topBlock = method_call('get', getBox.orderBlockData, 1)
                                        shortPoints.botBlock = method_call('get', getBox.orderBlockData, 3)
                                        shortPoints.startBlock = cast_int(getStart)
                                        break
                            __block_result_20__ = na
                            for FVG__0000048b__ in FVGarr:
                                __block_result_21__ = na
                                if FVG__0000048b__.direction == 'Down' and FVG__0000048b__.T >= getPrevPoint3.time:
                                    highest = math.max(FVG__0000048b__.H, FVG__0000048b__.L)
                                    lowest = math.min(FVG__0000048b__.H, FVG__0000048b__.L)
                                    __block_result_22__ = na
                                    if close <= lowest:
                                        statusPoss = highest >= shortPoints.topBlock and lowest <= shortPoints.topBlock or (highest >= shortPoints.botBlock and lowest <= shortPoints.botBlock) or (highest >= shortPoints.topBlock and lowest <= shortPoints.botBlock) or (highest <= shortPoints.topBlock and lowest >= shortPoints.botBlock)
                                        __block_result_23__ = na
                                        if statusPoss:
                                            shortPoints.entry = math.max(lowest, shortPoints.botBlock)
                                            shortPoints.hPoint = getPrevPoint
                                            shortPoints.hPoint2 = getPrevPoint2
                                            shortPoints.hPoint3 = getPrevPoint3
                                            slTime = cast_int(shortPoints.startBlock)
                                            slStr: str = 'Breakerblock SL'
                                            __block_result_24__ = na
                                            __switch_9__ = uniShortSL
                                            if __switch_9__ == IQ.unicornExits.tFVG:
                                                __block_result_24__ = math.max(highest, shortPoints.topBlock) + uniShortAdd * syminfo.mintick
                                            else:
                                                __block_result_24__ = shortPoints.hPoint.price + uniShortAdd * syminfo.mintick
                                            sl = __block_result_24__
                                            if sl == highest + uniShortAdd * syminfo.mintick:
                                                slTime = FVG__0000048b__.T
                                                slStr = 'FVG SL'
                                            if sl == shortPoints.hPoint.price + uniShortAdd * syminfo.mintick:
                                                slTime = shortPoints.hPoint.time
                                                slStr = 'Swing High SL'
                                            tp = NA(float)
                                            tpTime = NA(int)
                                            tpStr = NA(str)
                                            if uniShortTP == IQ.unicornExits.sL:
                                                for data in historicalPoints:
                                                    if data.price < shortPoints.entry:
                                                        tp = data.price
                                                        tpTime = data.time
                                                        tpStr = 'Swing Low'
                                                        break
                                            else:
                                                getFib: float = 0.0
                                                __switch_10__ = uniShortTP
                                                if __switch_10__ == IQ.unicornExits.zero5:
                                                    getFib = -0.5
                                                    tpStr = 'Fib -0.5'
                                                elif __switch_10__ == IQ.unicornExits.one5:
                                                    getFib = -1
                                                    tpStr = 'Fib -1'
                                                else:
                                                    getFib = -2
                                                    tpStr = 'Fib -2'
                                                tpTime = method_call('first', historicalPoints).time
                                                tp = method_call('first', historicalPoints).price - (method_call('first', historicalPoints).price - shortPoints.hPoint.price) * getFib
                                            if not na(tp):
                                                strategy.entry('Short Unicorn', strategy.short, limit=shortPoints.entry)
                                                strategy.exit('Short Unicorn Exit', 'Short Unicorn', limit=tp, stop=sl)
                                                method_call('delete', shortPoints.FVG)
                                                method_call('delete', shortPoints.breakerBlock)
                                                shortPoints.FVG = box.new(FVG__0000048b__.T, highest, future, lowest, border_color=color.new(color.red, borderTransp), bgcolor=color.new(color.red, 95), xloc=xloc.bar_time, text='FVG', text_color=chart.fg_color, text_size=size.small, text_halign=text.align_left)
                                                shortPoints.breakerBlock = box.new(shortPoints.startBlock, shortPoints.topBlock, future, shortPoints.botBlock, bgcolor=color.new(color.new('#6929F2'), 95), border_color=color.new(color.new('#6929F2'), borderTransp), xloc=xloc.bar_time, text='Breaker Block', text_color=chart.fg_color, text_size=size.small, text_halign=text.align_left)
                                                method_call('delete', shortPoints.tpLine)
                                                method_call('delete', shortPoints.tpLabel)
                                                method_call('delete', shortPoints.slLine)
                                                method_call('delete', shortPoints.slLabel)
                                                shortPoints.tpLine = line.new(chart.point.from_time(tpTime, tp), chart.point.from_time(future, tp), xloc=xloc.bar_time, style=line.style_dotted, color=color.new('#74FFBC'))
                                                shortPoints.tpLabel = label.new(future, tp, xloc=xloc.bar_time, color=color.new('#00000000'), style=label.style_label_upper_right, textcolor=color.new('#74FFBC'), size=size.small, text=tpStr)
                                                shortPoints.slLine = line.new(chart.point.from_time(slTime, sl), chart.point.from_time(future, sl), xloc=xloc.bar_time, style=line.style_dotted, color=color.red)
                                                shortPoints.slLabel = label.new(future, sl, xloc=xloc.bar_time, color=color.new('#00000000'), style=label.style_label_lower_right, textcolor=color.red, size=size.small, text=slStr)
                                            break
                                        __block_result_22__ = __block_result_23__
                                    __block_result_21__ = __block_result_22__
                                __block_result_20__ = __block_result_21__
                            __block_result_19__ = __block_result_20__
                        __block_result_18__ = __block_result_19__
                    __block_result_17__ = __block_result_18__
                __block_result_15__ = __block_result_17__
            __block_result_14__ = __block_result_15__
        return __block_result_14__

    def liquidityRaid(bullishOBbox: list[IQ.orderBlock], bearishOBbox: list[IQ.orderBlock], lRaidSessions: str, future: int, bearishBBcol: Color, bullishBBcol: Color, tpLongLiquidityRaid: str, slLongLiquidityRaid: str, tpShortLiquidityRaid: str, slShortLiquidityRaid: str, liquidityRaidFibTP: float, liquidityRaidFibSL: float, liquidityRaidFibTPshort: float, liquidityRaidFibSLshort: float, longLiquidityRaid: bool, shortLiquidityRaid: bool, historicalPoints: list[ChartPoint], noBorders: bool):
        keyPointsTime: Series = not na(time('', lRaidSessions, 'America/New_York'))
        highest: Persistent = NA(float)
        lowest: Persistent = NA(float)
        keyLevels: Persistent[dict[IQ.raidCoordinates, float]] = map.new()
        exitDrawings: Persistent[list[IQ.raidExitDrawings]] = array.new(0, NA(IQ.raidExitDrawings))
        includesArr: Persistent[list[int]] = array.new_int()
        openTrades = strategy.opentrades - 1
        closedTrades = strategy.closedtrades - 1
        if strategy.position_size != 0:
            strategy.cancel('Long Liquidity Raid')
            strategy.cancel('Short Liquidity Raid')
        if array.size(exitDrawings) > 0:
            if not na(array.last(exitDrawings).tpLine):
                getDrawings = array.last(exitDrawings)
                method_call('set_x2', getDrawings.tpLine, future)
                method_call('set_x', getDrawings.tpLabel, future)
                method_call('set_x2', getDrawings.slLine, future)
                method_call('set_x', getDrawings.slLabel, future)
                if IQ.checkIfClosed('Long Liquidity Raid'):
                    switch_var_23 = strategy.closedtrades.exit_price(closedTrades) > strategy.closedtrades.entry_price(closedTrades)
                    __switch_3__ = switch_var_23
                    if __switch_3__ == True:
                        method_call('delete', getDrawings.slLine)
                        method_call('delete', getDrawings.slLabel)
                        getDrawings.tpLine = NA(Line)
                        getDrawings.tpLabel = NA(Label)
                    else:
                        method_call('delete', getDrawings.tpLine)
                        method_call('delete', getDrawings.tpLabel)
                        getDrawings.slLine = NA(Line)
                        getDrawings.slLabel = NA(Label)
                if IQ.checkIfClosed('Short Liquidity Raid'):
                    switch_var_25 = strategy.closedtrades.exit_price(closedTrades) < strategy.closedtrades.entry_price(closedTrades)
                    __switch_3__ = switch_var_25
                    if __switch_3__ == True:
                        method_call('delete', getDrawings.slLine)
                        method_call('delete', getDrawings.slLabel)
                        getDrawings.tpLine = NA(Line)
                        getDrawings.tpLabel = NA(Label)
                    else:
                        method_call('delete', getDrawings.tpLine)
                        method_call('delete', getDrawings.tpLabel)
                        getDrawings.slLine = NA(Line)
                        getDrawings.slLabel = NA(Label)
        if IQ.checkIfTraded('Long Liquidity Raid'):
            points = array.from_items(chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.ET)), map.get(keyLevels, IQ.raidCoordinates.EP)), chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.LRVT)), map.get(keyLevels, IQ.raidCoordinates.LRP)), chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.HPRLRT)), map.get(keyLevels, IQ.raidCoordinates.HPRLR)), chart.point.from_time(time, map.get(keyLevels, IQ.raidCoordinates.CB)))
            polyline.new(points, xloc=xloc.bar_time, line_width=2, line_color=color.rgb(128, 116, 255))
            array.push(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))
            getStart = cast_int(map.get(keyLevels, IQ.raidCoordinates.ST))
            getEnd = cast_int(map.get(keyLevels, IQ.raidCoordinates.ET))
            getHigh = map.get(keyLevels, IQ.raidCoordinates.H)
            getLow = map.get(keyLevels, IQ.raidCoordinates.L)
            getBBstart = cast_int(map.get(keyLevels, IQ.raidCoordinates.CBS))
            box.new(getBBstart, map.get(keyLevels, IQ.raidCoordinates.CB), time, map.get(keyLevels, IQ.raidCoordinates.CBB), border_color=color.new(bearishBBcol, borderTransp), bgcolor=color.new(bearishBBcol, 95), xloc=xloc.bar_time, border_style=line.style_dashed)
            l = line.new(getStart, getHigh, getEnd, getHigh, xloc=xloc.bar_time, color=chart.fg_color)
            l1 = line.new(getStart, getLow, getEnd, getLow, xloc=xloc.bar_time, color=chart.fg_color)
            linefill.new(l, l1, color=color.new(chart.fg_color, 90))
            l2 = line.new(getEnd, getHigh, time, getHigh, xloc=xloc.bar_time, color=chart.fg_color, style=line.style_dotted)
            l3 = line.new(getEnd, getLow, time, getLow, xloc=xloc.bar_time, color=chart.fg_color, style=line.style_dotted)
            getTP = map.get(keyLevels, IQ.raidCoordinates.LTP)
            getTPtime = cast_int(map.get(keyLevels, IQ.raidCoordinates.LTPT))
            getSL = map.get(keyLevels, IQ.raidCoordinates.LSL)
            getSLtime = cast_int(map.get(keyLevels, IQ.raidCoordinates.LSLT))
            __block_result_25__ = na
            __switch_1__ = tpLongLiquidityRaid
            if __switch_1__ == 'Swing High':
                __block_result_25__ = 'Swing High TP'
            elif __switch_1__ == 'Use Fib (Option Below)':
                __block_result_25__ = 'Fib ' + string.tostring(liquidityRaidFibTP) + ' TP'
            longTPtext = __block_result_25__
            __block_result_26__ = na
            __switch_1__ = slLongLiquidityRaid
            if __switch_1__ == 'Swing Low':
                __block_result_26__ = 'Swing Low SL'
            elif __switch_1__ == 'Use Fib (Option Below)':
                __block_result_26__ = 'Fib ' + string.tostring(liquidityRaidFibSL) + ' SL'
            elif __switch_1__ == 'Breakerblock Bottom':
                __block_result_26__ = 'Breakerblock Bottom SL'
            longSLtext = __block_result_26__
            array.push(exitDrawings, IQ.raidExitDrawings.new(line.new(getTPtime, getTP, future, getTP, color=color.new('#74FFBC'), style=line.style_dotted, xloc=xloc.bar_time), label.new(future, getTP, color=color.new('#00000000'), style=label.style_label_lower_right, xloc=xloc.bar_time, textcolor=color.new('#74FFBC'), size=size.small, text=longTPtext), line.new(getSLtime, getSL, future, getSL, color=color.rgb(255, 116, 116), style=line.style_dotted, xloc=xloc.bar_time), label.new(future, getSL, color=color.new('#00000000'), style=label.style_label_upper_right, xloc=xloc.bar_time, textcolor=color.rgb(255, 116, 116), size=size.small, text=longSLtext)))
            if IQ.checkIfClosed('Long Liquidity Raid'):
                getDrawings = array.last(exitDrawings)
                switch_var_29 = strategy.closedtrades.exit_price(closedTrades) > strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_29
                if __switch_2__ == True:
                    method_call('delete', getDrawings.slLine)
                    method_call('delete', getDrawings.slLabel)
                    getDrawings.tpLine = NA(Line)
                    getDrawings.tpLabel = NA(Label)
                else:
                    method_call('delete', getDrawings.tpLine)
                    method_call('delete', getDrawings.tpLabel)
                    getDrawings.slLine = NA(Line)
                    getDrawings.slLabel = NA(Label)
            label.new(math.round(math.avg(getStart, time)), getHigh, xloc=xloc.bar_time, text='Session High', color=color.new('#00000000'), textcolor=chart.fg_color, size=size.small)
            label.new(math.round(math.avg(getStart, time)), getLow, xloc=xloc.bar_time, text='Session Low', color=color.new('#00000000'), textcolor=chart.fg_color, style=label.style_label_up, size=size.small)
            label.new(cast_int(map.get(keyLevels, IQ.raidCoordinates.LRVT)), map.get(keyLevels, IQ.raidCoordinates.LRP), text='Session Low Liquidity Raid', color=color.new('#00000000'), textcolor=chart.fg_color, style=label.style_label_upper_right, size=size.small, xloc=xloc.bar_time)
            map.put(keyLevels, IQ.raidCoordinates.CB, NA(float))
        if IQ.checkIfTraded('Short Liquidity Raid'):
            points = array.from_items(chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.ET)), map.get(keyLevels, IQ.raidCoordinates.EP)), chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.HRVT)), map.get(keyLevels, IQ.raidCoordinates.HRP)), chart.point.from_time(cast_int(map.get(keyLevels, IQ.raidCoordinates.LPRHRT)), map.get(keyLevels, IQ.raidCoordinates.LPRHR)), chart.point.from_time(time, map.get(keyLevels, IQ.raidCoordinates.CB)))
            polyline.new(points, xloc=xloc.bar_time, line_width=2, line_color=color.rgb(128, 116, 255))
            array.push(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))
            getStart = cast_int(map.get(keyLevels, IQ.raidCoordinates.ST))
            getEnd = cast_int(map.get(keyLevels, IQ.raidCoordinates.ET))
            getHigh = map.get(keyLevels, IQ.raidCoordinates.H)
            getLow = map.get(keyLevels, IQ.raidCoordinates.L)
            getBBstart = cast_int(map.get(keyLevels, IQ.raidCoordinates.CBS))
            box.new(getBBstart, map.get(keyLevels, IQ.raidCoordinates.CBT), time, map.get(keyLevels, IQ.raidCoordinates.CB), border_color=color.new(bullishBBcol, borderTransp), bgcolor=color.new(bullishBBcol, 95), xloc=xloc.bar_time, border_style=line.style_dashed)
            l = line.new(getStart, getHigh, getEnd, getHigh, xloc=xloc.bar_time, color=chart.fg_color)
            l1 = line.new(getStart, getLow, getEnd, getLow, xloc=xloc.bar_time, color=chart.fg_color)
            linefill.new(l, l1, color=color.new(chart.fg_color, 90))
            l2 = line.new(getEnd, getHigh, time, getHigh, xloc=xloc.bar_time, color=chart.fg_color, style=line.style_dotted)
            l3 = line.new(getEnd, getLow, time, getLow, xloc=xloc.bar_time, color=chart.fg_color, style=line.style_dotted)
            getTP = map.get(keyLevels, IQ.raidCoordinates.STP)
            getTPtime = cast_int(map.get(keyLevels, IQ.raidCoordinates.STPT))
            getSL = map.get(keyLevels, IQ.raidCoordinates.SSL)
            getSLtime = cast_int(map.get(keyLevels, IQ.raidCoordinates.SSLT))
            __block_result_27__ = na
            __switch_1__ = tpShortLiquidityRaid
            if __switch_1__ == 'Swing Low':
                __block_result_27__ = 'Swing Low TP'
            elif __switch_1__ == 'Use Fib (Option Below)':
                __block_result_27__ = 'Fib ' + string.tostring(liquidityRaidFibTPshort) + ' TP'
            shortTPtext = __block_result_27__
            __block_result_28__ = na
            __switch_1__ = slShortLiquidityRaid
            if __switch_1__ == 'Swing High':
                __block_result_28__ = 'Swing High SL'
            elif __switch_1__ == 'Use Fib (Option Below)':
                __block_result_28__ = 'Fib ' + string.tostring(liquidityRaidFibSLshort) + ' SL'
            elif __switch_1__ == 'Breakerblock Top':
                __block_result_28__ = 'Breakerblock Top SL'
            shortSLtext = __block_result_28__
            array.push(exitDrawings, IQ.raidExitDrawings.new(line.new(getTPtime, getTP, future, getTP, color=color.new('#74FFBC'), style=line.style_dotted, xloc=xloc.bar_time), label.new(future, getTP, color=color.new('#00000000'), style=label.style_label_upper_right, xloc=xloc.bar_time, textcolor=color.new('#74FFBC'), size=size.small, text=shortTPtext), line.new(getSLtime, getSL, future, getSL, color=color.rgb(255, 116, 116), style=line.style_dotted, xloc=xloc.bar_time), label.new(future, getSL, color=color.new('#00000000'), style=label.style_label_lower_right, xloc=xloc.bar_time, textcolor=color.rgb(255, 116, 116), size=size.small, text=shortSLtext)))
            if IQ.checkIfClosed('Short Liquidity Raid'):
                getDrawings = array.last(exitDrawings)
                switch_var_33 = strategy.closedtrades.exit_price(closedTrades) < strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_33
                if __switch_2__ == True:
                    method_call('delete', getDrawings.slLine)
                    method_call('delete', getDrawings.slLabel)
                    getDrawings.tpLine = NA(Line)
                    getDrawings.tpLabel = NA(Label)
                else:
                    method_call('delete', getDrawings.tpLine)
                    method_call('delete', getDrawings.tpLabel)
                    getDrawings.slLine = NA(Line)
                    getDrawings.slLabel = NA(Label)
            label.new(math.round(math.avg(getStart, time)), getHigh, xloc=xloc.bar_time, text='Session High', color=color.new('#00000000'), textcolor=chart.fg_color, size=size.small)
            label.new(math.round(math.avg(getStart, time)), getLow, xloc=xloc.bar_time, text='Session Low', color=color.new('#00000000'), textcolor=chart.fg_color, style=label.style_label_up, size=size.small)
            label.new(cast_int(map.get(keyLevels, IQ.raidCoordinates.HRVT)), map.get(keyLevels, IQ.raidCoordinates.HRP), text='Session High Liquidity Raid', color=color.new('#00000000'), textcolor=chart.fg_color, style=label.style_label_lower_right, size=size.small, xloc=xloc.bar_time)
            map.put(keyLevels, IQ.raidCoordinates.CB, NA(float))
        if keyPointsTime:
            if not keyPointsTime[1]:
                highest = high
                lowest = low
                map.clear(keyLevels)
                strategy.cancel('Long Liquidity Raid')
                strategy.cancel('Short Liquidity Raid')
                map.put(keyLevels, IQ.raidCoordinates.HR, 0)
                map.put(keyLevels, IQ.raidCoordinates.LR, 0)
                map.put(keyLevels, IQ.raidCoordinates.ST, time)
                map.put(keyLevels, IQ.raidCoordinates.SP, ohlc4)
                map.put(keyLevels, IQ.raidCoordinates.CB, NA(float))
            highest = math.max(high, highest)
            lowest = math.min(low, lowest)
            map.put(keyLevels, IQ.raidCoordinates.H, highest)
            map.put(keyLevels, IQ.raidCoordinates.L, lowest)
        else:
            if keyPointsTime[1]:
                map.put(keyLevels, IQ.raidCoordinates.H, highest)
                map.put(keyLevels, IQ.raidCoordinates.L, lowest)
                highest = NA(float)
                lowest = NA(float)
                map.put(keyLevels, IQ.raidCoordinates.ET, time)
                map.put(keyLevels, IQ.raidCoordinates.EP, ohlc4)
            if map.get(keyLevels, IQ.raidCoordinates.HR) == 0 and map.get(keyLevels, IQ.raidCoordinates.LR) == 0:
                if high >= map.get(keyLevels, IQ.raidCoordinates.H):
                    map.put(keyLevels, IQ.raidCoordinates.HR, 1)
                    map.put(keyLevels, IQ.raidCoordinates.HRT, time)
                    map.put(keyLevels, IQ.raidCoordinates.HRP, high)
                    map.put(keyLevels, IQ.raidCoordinates.HRVT, time)
                    map.put(keyLevels, IQ.raidCoordinates.LPRHR, low)
                    map.put(keyLevels, IQ.raidCoordinates.LPRHRT, time)
                elif low <= map.get(keyLevels, IQ.raidCoordinates.L):
                    map.put(keyLevels, IQ.raidCoordinates.LR, 1)
                    map.put(keyLevels, IQ.raidCoordinates.LRT, time)
                    map.put(keyLevels, IQ.raidCoordinates.LRP, low)
                    map.put(keyLevels, IQ.raidCoordinates.LRVT, time)
                    map.put(keyLevels, IQ.raidCoordinates.HPRLR, high)
                    map.put(keyLevels, IQ.raidCoordinates.HPRLRT, time)
            if map.get(keyLevels, IQ.raidCoordinates.LR) == 1:
                if low <= map.get(keyLevels, IQ.raidCoordinates.LRP):
                    map.put(keyLevels, IQ.raidCoordinates.LRVT, time)
                    map.put(keyLevels, IQ.raidCoordinates.LRP, low)
                if high >= map.get(keyLevels, IQ.raidCoordinates.HPRLR) and (not na(IQ.raidCoordinates.CB)):
                    map.put(keyLevels, IQ.raidCoordinates.HPRLR, high)
                    map.put(keyLevels, IQ.raidCoordinates.HPRLRT, time)
            if map.get(keyLevels, IQ.raidCoordinates.HR) == 1:
                if high >= map.get(keyLevels, IQ.raidCoordinates.HRP):
                    map.put(keyLevels, IQ.raidCoordinates.HRVT, time)
                    map.put(keyLevels, IQ.raidCoordinates.HRP, high)
                if low <= map.get(keyLevels, IQ.raidCoordinates.LPRHR) and (not na(IQ.raidCoordinates.CB)):
                    map.put(keyLevels, IQ.raidCoordinates.LPRHR, low)
                    map.put(keyLevels, IQ.raidCoordinates.LPRHRT, time)
            if map.get(keyLevels, IQ.raidCoordinates.LR) == 1 and longLiquidityRaid and (not array.includes(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))):
                closestBB: float = 0.0
                closestBBstart: int = 0
                closestBBbottom: float = 0.0
                if array.size(bearishOBbox) > 0:
                    getLowRaidTime = map.get(keyLevels, IQ.raidCoordinates.LRT)
                    getLow = map.get(keyLevels, IQ.raidCoordinates.L)
                    for i in pine_range(0, array.size(bearishOBbox) - 1, 1):
                        getOrderBlock = array.get(bearishOBbox, i)
                        getTop = method_call('get', getOrderBlock.orderBlockData, 1)
                        if method_call('first', getOrderBlock.orderBlockData) >= getLowRaidTime:
                            if getOrderBlock.status == 'BB':
                                if close > getTop and getTop > getLow:
                                    closestBB = math.max(closestBB, getTop)
                                    if closestBB == getTop:
                                        closestBBstart = cast_int(method_call('first', getOrderBlock.orderBlockData))
                                        closestBBbottom = method_call('last', getOrderBlock.orderBlockData)
                                        if na(map.get(keyLevels, IQ.raidCoordinates.CB)):
                                            map.put(keyLevels, IQ.raidCoordinates.HPRLR, high)
                                            map.put(keyLevels, IQ.raidCoordinates.HPRLRT, time)
                        else:
                            break
                    if closestBB != 0:
                        if tpLongLiquidityRaid == 'Swing High':
                            if array.size(historicalPoints) > 0:
                                for points in historicalPoints:
                                    if points.price > closestBB:
                                        map.put(keyLevels, IQ.raidCoordinates.LTP, points.price)
                                        map.put(keyLevels, IQ.raidCoordinates.LTPT, points.time)
                                        break
                        else:
                            getHighSession = map.get(keyLevels, IQ.raidCoordinates.H)
                            getLowRaid = map.get(keyLevels, IQ.raidCoordinates.LRP)
                            fib = getHighSession - (getHighSession - getLowRaid) * liquidityRaidFibTP
                            map.put(keyLevels, IQ.raidCoordinates.LTP, fib)
                            map.put(keyLevels, IQ.raidCoordinates.LTPT, map.get(keyLevels, IQ.raidCoordinates.ET))
                        __switch_4__ = slLongLiquidityRaid
                        if __switch_4__ == 'Swing Low':
                            map.put(keyLevels, IQ.raidCoordinates.LSL, map.get(keyLevels, IQ.raidCoordinates.LRP))
                            map.put(keyLevels, IQ.raidCoordinates.LSLT, map.get(keyLevels, IQ.raidCoordinates.LRVT))
                        elif __switch_4__ == 'Breakerblock Bottom':
                            map.put(keyLevels, IQ.raidCoordinates.LSL, closestBBbottom)
                            map.put(keyLevels, IQ.raidCoordinates.LSLT, closestBBstart)
                        elif __switch_4__ == 'Use Fib (Option Below)':
                            getHighSession = map.get(keyLevels, IQ.raidCoordinates.H)
                            getLowRaid = map.get(keyLevels, IQ.raidCoordinates.LRP)
                            fib = getLowRaid + (getHighSession - getLowRaid) * liquidityRaidFibTP
                            map.put(keyLevels, IQ.raidCoordinates.LSL, fib)
                            map.put(keyLevels, IQ.raidCoordinates.LSLT, map.get(keyLevels, IQ.raidCoordinates.ET))
                        if not na(map.get(keyLevels, IQ.raidCoordinates.LTP)) and (not na(map.get(keyLevels, IQ.raidCoordinates.LSL))) and (strategy.opentrades == 0) and barstate.isconfirmed and (not array.includes(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))):
                            strategy.entry('Long Liquidity Raid', strategy.long, limit=closestBB, comment='Long Liquidity Raid')
                            strategy.exit('Long Liquidity Raid Exit', 'Long Liquidity Raid', limit=map.get(keyLevels, IQ.raidCoordinates.LTP), stop=map.get(keyLevels, IQ.raidCoordinates.LSL))
                            map.put(keyLevels, IQ.raidCoordinates.CB, closestBB)
                            map.put(keyLevels, IQ.raidCoordinates.CBB, closestBBbottom)
                            map.put(keyLevels, IQ.raidCoordinates.CBS, closestBBstart)
                    if close < getLow:
                        strategy.cancel('Long Liquidity Raid')
            if map.get(keyLevels, IQ.raidCoordinates.HR) == 1 and shortLiquidityRaid and (not array.includes(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))):
                closestBB: float = 2e+21
                closestBBstart: int = 0
                closestBBtop: float = 0.0
                if array.size(bullishOBbox) > 0:
                    getHighRaidTime = map.get(keyLevels, IQ.raidCoordinates.HRT)
                    getHigh = map.get(keyLevels, IQ.raidCoordinates.H)
                    for i in pine_range(0, array.size(bullishOBbox) - 1, 1):
                        getOrderBlock = array.get(bullishOBbox, i)
                        getBot = method_call('last', getOrderBlock.orderBlockData)
                        if method_call('first', getOrderBlock.orderBlockData) >= getHighRaidTime:
                            if getOrderBlock.status == 'BB':
                                if close < getBot and getBot < getHigh:
                                    closestBB = math.min(closestBB, getBot)
                                    if closestBB == getBot:
                                        closestBBstart = cast_int(method_call('first', getOrderBlock.orderBlockData))
                                        closestBBtop = method_call('get', getOrderBlock.orderBlockData, 1)
                                        if na(map.get(keyLevels, IQ.raidCoordinates.CB)):
                                            map.put(keyLevels, IQ.raidCoordinates.LPRHR, low)
                                            map.put(keyLevels, IQ.raidCoordinates.LPRHRT, time)
                        else:
                            break
                    if closestBB != 2e+21:
                        if tpShortLiquidityRaid == 'Swing Low':
                            if array.size(historicalPoints) > 0:
                                for points in historicalPoints:
                                    if points.price < closestBB:
                                        map.put(keyLevels, IQ.raidCoordinates.STP, points.price)
                                        map.put(keyLevels, IQ.raidCoordinates.STPT, points.time)
                                        break
                        else:
                            getLowSession = map.get(keyLevels, IQ.raidCoordinates.L)
                            getHighRaid = map.get(keyLevels, IQ.raidCoordinates.HRP)
                            fib = getLowSession - (getLowSession - getHighRaid) * liquidityRaidFibTPshort
                            map.put(keyLevels, IQ.raidCoordinates.STP, fib)
                            map.put(keyLevels, IQ.raidCoordinates.STPT, map.get(keyLevels, IQ.raidCoordinates.ET))
                        __switch_4__ = slShortLiquidityRaid
                        if __switch_4__ == 'Swing High':
                            map.put(keyLevels, IQ.raidCoordinates.SSL, map.get(keyLevels, IQ.raidCoordinates.HRP))
                            map.put(keyLevels, IQ.raidCoordinates.SSLT, map.get(keyLevels, IQ.raidCoordinates.HRVT))
                        elif __switch_4__ == 'Breakerblock Top':
                            map.put(keyLevels, IQ.raidCoordinates.SSL, closestBBtop)
                            map.put(keyLevels, IQ.raidCoordinates.SSLT, closestBBstart)
                        elif __switch_4__ == 'Use Fib (Option Below)':
                            getLowSession = map.get(keyLevels, IQ.raidCoordinates.L)
                            getHighRaid = map.get(keyLevels, IQ.raidCoordinates.HRP)
                            fib = getHighRaid + (getLowSession - getHighRaid) * liquidityRaidFibTPshort
                            map.put(keyLevels, IQ.raidCoordinates.SSL, fib)
                            map.put(keyLevels, IQ.raidCoordinates.SSLT, map.get(keyLevels, IQ.raidCoordinates.ET))
                        if not na(map.get(keyLevels, IQ.raidCoordinates.STP)) and (not na(map.get(keyLevels, IQ.raidCoordinates.SSL))) and (strategy.opentrades == 0) and barstate.isconfirmed and (not array.includes(includesArr, cast_int(map.get(keyLevels, IQ.raidCoordinates.ST)))):
                            strategy.entry('Short Liquidity Raid', strategy.short, limit=closestBB, comment='Short Liquidity Raid')
                            strategy.exit('Short Liquidity Raid Exit', 'Short Liquidity Raid', limit=map.get(keyLevels, IQ.raidCoordinates.STP), stop=map.get(keyLevels, IQ.raidCoordinates.SSL))
                            map.put(keyLevels, IQ.raidCoordinates.CB, closestBB)
                            map.put(keyLevels, IQ.raidCoordinates.CBT, closestBBtop)
                            map.put(keyLevels, IQ.raidCoordinates.CBS, closestBBstart)
                    if close > getHigh:
                        strategy.cancel('Short Liquidity Raid')
        return 0

    @method
    def fairValueGap(FVGarr: list[IQ.FVG]):
        if barstate.isconfirmed and IQ.isLastBar(userTF):
            method_call('invalidFVGcheck', FVGarr, upFVGpricesSorted, dnFVGpricesSorted)
            if onlyFVGliq:
                getUpStatus = map.get(takeFVGs, 'Up')
                if getUpStatus != 0 and H2 < L:
                    if getUpStatus == 1 or array.size(FVGarr) == 0:
                        array.unshift(FVGarr, IQ.FVG.new(H2, L, 'Up', time1))
                        array.insert(upFVGpricesSorted, array.binary_search_rightmost(upFVGpricesSorted, H2), H2)
                        map.put(takeFVGs, 'Up', 2)
                    else:
                        switch_var_38 = L > array.first(FVGarr).L
                        __switch_4__ = switch_var_38
                        if __switch_4__ == True:
                            array.unshift(FVGarr, IQ.FVG.new(H2, L, 'Up', time1))
                            array.insert(upFVGpricesSorted, array.binary_search_rightmost(upFVGpricesSorted, H2), H2)
                        else:
                            map.put(takeFVGs, 'Up', 0)
                getDnStatus = map.get(takeFVGs, 'Down')
                if getDnStatus != 0 and L2 > H:
                    if getDnStatus == 1 or array.size(FVGarr) == 0:
                        array.unshift(FVGarr, IQ.FVG.new(H, L2, 'Down', time1))
                        array.insert(dnFVGpricesSorted, array.binary_search_rightmost(dnFVGpricesSorted, L2), L2)
                        map.put(takeFVGs, 'Down', 2)
                    else:
                        switch_var_40 = H < array.first(FVGarr).H
                        __switch_4__ = switch_var_40
                        if __switch_4__ == True:
                            array.unshift(FVGarr, IQ.FVG.new(H, L2, 'Down', time1))
                            array.insert(dnFVGpricesSorted, array.binary_search_rightmost(dnFVGpricesSorted, L2), L2)
                        else:
                            map.put(takeFVGs, 'Down', 0)
            else:
                if H2 < L:
                    array.unshift(FVGarr, IQ.FVG.new(H2, L, 'Up', time1))
                    array.insert(upFVGpricesSorted, array.binary_search_rightmost(upFVGpricesSorted, H2), H2)
                elif L2 > H:
                    array.unshift(FVGarr, IQ.FVG.new(H, L2, 'Down', time1))
                    array.insert(dnFVGpricesSorted, array.binary_search_rightmost(dnFVGpricesSorted, L2), L2)
        if barstate.islast:
            counter: dict[str, int] = map.new()
            map.put(counter, 'FVG Up', 0)
            map.put(counter, 'FVG Down', 0)
            if array.size(FVGarr) > 0:
                for i in pine_range(0, array.size(FVGarr) - 1, 1):
                    data = array.get(FVGarr, i)
                    method_call('delete', data.fvgBox)
                    if labelLevels == 'Outside':
                        method_call('delete', data.fvgLabel)
                    __switch_3__ = data.direction
                    if __switch_3__ == 'Up':
                        IQ.drawFVG(counter, FVGUpShow, 'FVG Up', FVGupcol, data, masterCoords, labelLevels, borderTransp, liteMode, timen5)
                    else:
                        IQ.drawFVG(counter, FVGDnShow, 'FVG Down', FVGdncol, data, masterCoords, labelLevels, borderTransp, liteMode, timen5)
        return FVGarr

    def drawRejections(upRejections: list[IQ.rejectionBlocks], dnRejections: list[IQ.rejectionBlocks]):
        if IQ.isLastBar(userTF):
            if close > array.min(upRejectionsPrices):
                for i in pine_range(array.size(upRejections) - 1, 0, 1):
                    data = array.get(upRejections, i)
                    if close > data.rejectionPoint.price:
                        if not na(data.rejectionBox):
                            method_call('delete', data.rejectionBox)
                            method_call('delete', data.rejectionLabel)
                        array.remove(upRejections, i)
                slice = array.slice(upRejectionsPrices, 0, array.binary_search_rightmost(upRejectionsPrices, close))
                method_call('clear', slice)
            if close < array.max(dnRejectionsPrices):
                for i in pine_range(array.size(dnRejections) - 1, 0, 1):
                    data = array.get(dnRejections, i)
                    if close < data.rejectionPoint.price:
                        if not na(data.rejectionBox):
                            method_call('delete', data.rejectionBox)
                            method_call('delete', data.rejectionLabel)
                        array.remove(dnRejections, i)
                getIndex = math.min(array.size(dnRejectionsPrices) - 1, array.binary_search_rightmost(dnRejectionsPrices, close))
                slice = array.slice(dnRejectionsPrices, getIndex, array.size(dnRejectionsPrices))
                method_call('clear', slice)
        method_call('lastBarRejections', upRejections, bearishRBcol, bearishRBshow, 'Up Rejection', labelLevels, borderTransp, liteMode, timen5, masterCoords)
        return method_call('lastBarRejections', dnRejections, bullishRBcol, bullishRBshow, 'Down Rejection', labelLevels, borderTransp, liteMode, timen5, masterCoords)

    def calcKeyLevels():
        swingHighs: Persistent[list[float]] = array.new_float()
        swingLows: Persistent[list[float]] = array.new_float()
        FVGarr: Persistent[list[IQ.FVG]] = array.new(0, NA(IQ.FVG))
        bullishOBbox, bearishOBbox = getOB()
        liquidityRaid(bullishOBbox, bearishOBbox, lRaidSessions, future, bearishBBcol, bullishBBcol, tpLongLiquidityRaid, slLongLiquidityRaid, tpShortLiquidityRaid, slShortLiquidityRaid, liquidityRaidFibTP, liquidityRaidFibSL, liquidityRaidFibTPshort, liquidityRaidFibSLshort, longLiquidityRaid, shortLiquidityRaid, historicalPoints, noBorders)
        IQ.OTEstrat(OTEstart, future, historicalData.closeArr, historicalData.highArr, historicalData.lowArr, historicalData.timeArr, longOTEPT, longOTESL, longOTElevel, shortOTEPT, shortOTESL, shortOTElevel, structureDirection, oteLongs, atrTF, oteShorts)
        IQ.displacement(logZ, atrTFreg, historicalData.highArr, historicalData.timeArr, historicalData.lowArr, upDispShow, dnDispShow, masterCoords, labelLevels, dispUpcol, timen5, dispDncol, noBorders)
        IQ.po3(po3tf, 70, 80, showpo3)
        IQ.po3(po3tf2, 150, 160, showpo32)
        IQ.macros(showMacros, noBorders)
        IQ.silverBullet(silverBulletStratLong, silverBulletStratShort, future, userTF, H, L, H2, L2, noBorders, silverBulletLongTP, historicalPoints, historicalData, silverBulletLongSL, silverBulletShortTP, silverBulletShortSL)
        fairValueGap(FVGarr)
        sweepData__00000793__ = zzLiq(atrLiqSweep, buffer, FVGarr)
        unicorn(bearishOBbox, FVGarr, bullishOBbox)
        drawRejections(upRejections, dnRejections)
        if IQ.isLastBar(userTF):
            if close > array.min(swingHighs):
                slice = array.slice(swingHighs, 0, array.binary_search_rightmost(swingHighs, close))
                method_call('clear', slice)
            if close < array.max(swingLows):
                slice = array.slice(swingLows, math.min(array.size(swingLows) - 1, array.binary_search_rightmost(swingLows, close)), array.size(swingLows))
                method_call('clear', slice)
            if not na(getPH):
                array.insert(swingHighs, array.binary_search_rightmost(swingHighs, getPH), getPH)
            if not na(getPL):
                array.insert(swingLows, array.binary_search_rightmost(swingLows, getPL), getPL)
        model2022Long(sweepData__00000793__, FVGarr)
        model2022Short(sweepData__00000793__, FVGarr)
        if equalLevels:
            IQ.equalLevels(historicalData.highArr, historicalData.lowArr, historicalData.timeArr, timen5, equalHighsCol, equalLowsCol, liteMode)
        if barstate.islast:
            if labelSize != 'Default':
                __block_result_29__ = na
                __switch_2__ = labelSize
                if __switch_2__ == 'Auto':
                    __block_result_29__ = size.auto
                elif __switch_2__ == 'Tiny':
                    __block_result_29__ = size.tiny
                elif __switch_2__ == 'Small':
                    __block_result_29__ = size.small
                elif __switch_2__ == 'Normal':
                    __block_result_29__ = size.normal
                sz__000006b0__: Persistent = __block_result_29__
                for lab in label.all:
                    label.set_size(lab, sz__000006b0__)
            if not na(getKeyPoint):
                tip: str = ''
                col = NA(Color)
                isActive: Persistent[bool] = False
                trailPoint: Persistent = getKeyPoint.price
                if getKeyPoint.price != trailPoint:
                    isActive = True
                    trailPoint = getKeyPoint.price
                isHigh = getKeyPoint.price > pPoint.price
                if isActive and IQ.isLastBar(userTF):
                    if close > getKeyPoint.price and isHigh:
                        isActive = False
                    if close < getKeyPoint.price and (not isHigh):
                        isActive = False
                if structureDirection == 'Up':
                    __block_result_30__ = na
                    if isHigh:
                        __block_result_30__ = 'BoS'
                    else:
                        __block_result_30__ = 'MSS'
                    tip += __block_result_30__
                    __block_result_31__ = na
                    if isHigh:
                        __block_result_31__ = color.new('#74FFBC')
                    else:
                        __block_result_31__ = color.rgb(255, 116, 116)
                    col = __block_result_31__
                else:
                    __block_result_32__ = na
                    if isHigh:
                        __block_result_32__ = 'MSS'
                    else:
                        __block_result_32__ = 'BoS'
                    tip += __block_result_32__
                    __block_result_33__ = na
                    if isHigh:
                        __block_result_33__ = color.rgb(255, 116, 116)
                    else:
                        __block_result_33__ = color.new('#74FFBC')
                    col = __block_result_33__
                lastPoint: Persistent = line.new(getKeyPoint.time, getKeyPoint.price, timen5, getKeyPoint.price, xloc=xloc.bar_time, style=line.style_dotted, color=col)
                lastPointLab: Persistent = label.new(math.round(math.avg(time, getKeyPoint.time)), getKeyPoint.price, text=tip, color=color.new('#00000000'), xloc=xloc.bar_time, size=size.small, textcolor=col)
                __switch_2__ = isActive
                if __switch_2__ == True:
                    method_call('set_first_point', lastPoint, getKeyPoint)
                    method_call('set_xy2', lastPoint, timen5, getKeyPoint.price)
                    method_call('set_xy', lastPointLab, math.round(math.avg(time, getKeyPoint.time)), getKeyPoint.price)
                    method_call('set_color', lastPoint, col)
                    method_call('set_textcolor', lastPointLab, col)
                    method_call('set_text', lastPointLab, tip)
                else:
                    method_call('set_color', lastPoint, color.new('#00000000'))
                    method_call('set_textcolor', lastPointLab, color.new('#00000000'))
            getReqTF = timeframe.from_seconds(math.max(timeframe.in_seconds(''), timeframe.in_seconds(pbTF)))
            if showpbH:
                getTFhigh = request.security(syminfo.tickerid, getReqTF, high[1], lookahead=barmerge.lookahead_on)
                __block_result_34__ = (na, na)
                __switch_2__ = liteMode
                if __switch_2__ == True:
                    __block_result_34__ = (line.style_dashed, 1)
                else:
                    __block_result_34__ = (line.style_solid, 2)
                sty, width = __block_result_34__
                pdHline: Persistent = line.new(time, getTFhigh, time('', -5), getTFhigh, color=pdHcol, xloc=xloc.bar_time, width=width, style=sty)
                pdHlab: Persistent = label.new(timen5, getTFhigh, textcolor=pdHcol, size=size.tiny, xloc=xloc.bar_time, style=label.style_label_left, color=color.new('#00000000'), text='p' + getReqTF + ' High')
                pdHlineN: Persistent = line.new(time, getTFhigh, time('', -5), getTFhigh, color=color.new(pdHcol, 80), width=5, xloc=xloc.bar_time, style=line.style_solid)
                pdHlabN: Persistent = label.new(time, getTFhigh, size=size.normal, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(pdHcol, 80), textcolor=pdHcol)
                method_call('set_xy', pdHlab, timen5, getTFhigh)
                startHigh = method_call('getTime', historicalData.highArr, getTFhigh, historicalData.timeArr)
                method_call('set_xy1', pdHline, startHigh, getTFhigh)
                method_call('set_xy2', pdHline, time('', -5), getTFhigh)
                if liteMode and (not na(pdHlabN)):
                    method_call('delete', pdHlineN)
                    method_call('delete', pdHlineN)
                    method_call('delete', pdHlabN)
                else:
                    method_call('set_xy1', pdHlineN, startHigh, getTFhigh)
                    method_call('set_xy2', pdHlineN, time('', -5), getTFhigh)
                    method_call('set_xy', pdHlabN, startHigh, getTFhigh)
                map.put(masterCoords, 'p' + getReqTF + ' High', getTFhigh)
            if showpbL:
                getTFlow = request.security(syminfo.tickerid, getReqTF, low[1], lookahead=barmerge.lookahead_on)
                __block_result_35__ = (na, na)
                __switch_2__ = liteMode
                if __switch_2__ == True:
                    __block_result_35__ = (line.style_dashed, 1)
                else:
                    __block_result_35__ = (line.style_solid, 2)
                sty, width = __block_result_35__
                pdLline: Persistent = line.new(time, getTFlow, time('', -5), getTFlow, color=pdLcol, xloc=xloc.bar_time, width=width, style=sty)
                pdLlab: Persistent = label.new(timen5, getTFlow, textcolor=pdLcol, size=size.tiny, xloc=xloc.bar_time, text='p' + getReqTF + ' Low', style=label.style_label_left, color=color.new('#00000000'))
                pdLlineN: Persistent = line.new(time, getTFlow, time('', -5), getTFlow, color=color.new(pdLcol, 80), width=5, xloc=xloc.bar_time, style=line.style_solid)
                pdLlabN: Persistent = label.new(time, getTFlow, size=size.normal, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(pdLcol, 80), textcolor=pdLcol)
                startLow = method_call('getTime', historicalData.lowArr, getTFlow, historicalData.timeArr)
                method_call('set_xy', pdLlab, timen5, getTFlow)
                method_call('set_xy1', pdLline, startLow, getTFlow)
                method_call('set_xy2', pdLline, time('', -5), getTFlow)
                if liteMode and (not na(pdLlineN)):
                    method_call('delete', pdLlineN)
                    method_call('delete', pdLlineN)
                    method_call('delete', pdLlabN)
                else:
                    method_call('set_xy1', pdLlineN, startLow, getTFlow)
                    method_call('set_xy2', pdLlineN, time('', -5), getTFlow)
                    method_call('set_xy', pdLlabN, startLow, getTFlow)
                map.put(masterCoords, 'p' + getReqTF + ' Low', getTFlow)
            swingHighDline: Persistent = NA(Line)
            swingLowDline: Persistent = NA(Line)
            method_call('delete', swingHighDline)
            method_call('delete', swingLowDline)
            swingHighDlab: Persistent = NA(Label)
            swingLowDlab: Persistent = NA(Label)
            method_call('delete', swingHighDlab)
            method_call('delete', swingLowDlab)
            if array.size(swingHighs) > 0:
                getFirst = array.first(swingHighs)
                startTime = method_call('getTime', historicalData.highArr, getFirst, historicalData.timeArr)
                swingHighDline = line.new(startTime, getFirst, time('', -5), getFirst, color=color.rgb(255, 116, 116), xloc=xloc.bar_time, style=line.style_dashed)
                sty = label.style_label_left
                swingHighDlab = label.new(time('', -5), getFirst, textcolor=color.rgb(255, 116, 116), xloc=xloc.bar_time, text='Swing High', size=size.tiny, style=sty, color=color.new('#00000000'))
                map.put(masterCoords, 'Swing High', getFirst)
            if array.size(swingLows) > 0:
                getLast = array.last(swingLows)
                startTime = method_call('getTime', historicalData.lowArr, getLast, historicalData.timeArr)
                swingLowDline = line.new(startTime, getLast, time('', -5), getLast, color=color.new('#74FFBC'), xloc=xloc.bar_time, style=line.style_dashed)
                sty = label.style_label_left
                swingLowDlab = label.new(time('', -5), getLast, textcolor=color.new('#74FFBC'), xloc=xloc.bar_time, text='Swing Low', size=size.tiny, style=sty, color=color.new('#00000000'))
                map.put(masterCoords, 'Swing Low', getLast)
        atr = ta.atr(14) / 10
        __block_result_36__ = na
        __switch__ = tablePlace
        if __switch__ == 'Top Right':
            __block_result_36__ = position.top_right
        elif __switch__ == 'Middle Right':
            __block_result_36__ = position.middle_right
        elif __switch__ == 'Bottom Right':
            __block_result_36__ = position.bottom_right
        elif __switch__ == 'Top Left':
            __block_result_36__ = position.top_left
        elif __switch__ == 'Middle Left':
            __block_result_36__ = position.middle_left
        elif __switch__ == 'Bottom Left':
            __block_result_36__ = position.bottom_left
        elif __switch__ == 'Top Center':
            __block_result_36__ = position.top_center
        elif __switch__ == 'Middle Center':
            __block_result_36__ = position.middle_center
        else:
            __block_result_36__ = position.bottom_center
        position__ren__: Persistent = __block_result_36__
        __block_result_37__ = na
        __switch__ = tableTxt
        if __switch__ == 'Tiny':
            __block_result_37__ = size.tiny
        elif __switch__ == 'Small':
            __block_result_37__ = size.small
        elif __switch__ == 'Normal':
            __block_result_37__ = size.normal
        sz: Persistent = __block_result_37__
        strategyTab: Persistent = table.new(position.top_right, 99, 99, bgcolor=color.new('#20222C'), border_color=color.new('#363843'), frame_color=color.new('#363843'), border_width=1, frame_width=1)
        strategyArr: Persistent[list[bool]] = array.from_items(model2022Long__global__, model2022Short__global__, uniLong, uniShort, longLiquidityRaid, shortLiquidityRaid, oteLongs, oteShorts, silverBulletStratLong, silverBulletStratShort)
        strategyNameArr: Persistent[list[str]] = array.from_items('Model 2022', 'Model 2022', 'Unicorn', 'Unicorn', 'Liquidity Raid', 'Liquidity Raid', 'OTE', 'OTE', 'Silver Bullet', 'Silver Bullet')
        if barstate.islastconfirmedhistory:
            method_call('cell', strategyTab, 0, 0, 'TradingIQ\n\nICT Trading Framework', text_color=color.white, text_size=sz)
            txt: str = ''
            if array.some(strategyArr):
                for i, index in enumerate(strategyArr):
                    if index:
                        append: str = array.get(strategyNameArr, i)
                        if not string.contains(txt, append):
                            __switch_5__ = txt == ''
                            if __switch_5__ == True:
                                txt = txt + append
                            else:
                                txt = txt + '\n' + append
                    method_call('cell', strategyTab, 0, 1, text='Strategies Used: ', text_color=color.white, text_size=sz)
                    method_call('cell', strategyTab, 1, 1, text=txt, text_color=color.white, text_size=sz)
                    method_call('merge_cells', strategyTab, 0, 0, 1, 0)
        __block_result_38__ = na
        if barstate.islast:
            if array.some(strategyArr):
                method_call('cell', strategyTab, 0, 2, text='Profit: ', text_color=color.white, text_size=sz)
                profColor__55 = math.sign(strategy.netprofit_percent)
                __block_result_39__ = na
                __switch_2__ = profColor__55
                if __switch_2__ == 1:
                    __block_result_39__ = color.new('#74FFBC')
                elif __switch_2__ == -1:
                    __block_result_39__ = color.rgb(255, 116, 116)
                else:
                    __block_result_39__ = color.white
                profColor = __block_result_39__
                method_call('cell', strategyTab, 1, 2, text=string.tostring(strategy.netprofit_percent, format.percent), text_color=profColor, text_size=sz)
                method_call('cell', strategyTab, 0, 3, text='Win Rate: ', text_color=color.white, text_size=sz)
                method_call('cell', strategyTab, 1, 3, text=string.tostring(strategy.wintrades / strategy.closedtrades * 100, format.percent), text_color=color.new('#74FFBC'), text_size=sz)
                if syminfo.type == 'futures':
                    if strategy.closedtrades == 0:
                        method_call('clear', strategyTab, 0, 0, 1, 3)
                        method_call('cell', strategyTab, 0, 0, text='If There Are No Trades,\n Please Try Changing The \n"Order Size" In The "Properties" Tab To "Contracts"', text_color=color.white, text_size=size.tiny)
            if tablePlace == 'Remove Table':
                method_call('clear', strategyTab, 0, 0, 1, 3)
            if not liteMode:
                gradBox: Persistent[list[Box]] = array.new_box(50)
                values = map.values(masterCoords)
                minValue = math.min(method_call('min', values), method_call('min', method_call('slice', historicalData.lowArr, 0, math.min(300, method_call('size', historicalData.lowArr) - 1)))) - atr * 10 * 4
                maxValue = math.max(method_call('max', values), method_call('max', method_call('slice', historicalData.highArr, 0, math.min(300, method_call('size', historicalData.highArr) - 1)))) + atr * 10 * 4
                Range = math.abs(maxValue - minValue) / 50
                if array.includes(gradBox, NA(Box)):
                    for i in pine_range(0, 49, 1):
                        __block_result_40__ = na
                        if i <= 24:
                            __block_result_40__ = color.from_gradient(i, 0, 24, color.new('#74FFBC'), color.new('#6929F2'))
                        else:
                            __block_result_40__ = color.from_gradient(i, 25, 49, color.new('#6929F2'), color.rgb(255, 116, 116))
                        col = __block_result_40__
                        array.set(gradBox, i, box.new(time, minValue + Range * (i + 1), timen5, minValue + Range * i, xloc=xloc.bar_time, bgcolor=color.new(col, 95), border_color=color.new('#00000000'), extend=extend.left))
                else:
                    for i, boxes in enumerate(gradBox):
                        box.set_rightbottom(boxes, timen5, minValue + Range * i)
                        box.set_top(boxes, minValue + Range * (i + 1))
            getLabSize = array.size(label.all)
            __block_result_41__ = na
            if getLabSize > 0:
                __block_result_42__ = na
                for i in pine_range(0, getLabSize - 1, 1):
                    getLabOuter = array.get(label.all, i)
                    getLabOuterY = method_call('get_y', getLabOuter)
                    __block_result_43__ = na
                    if method_call('get_x', getLabOuter) >= time:
                        __block_result_44__ = na
                        for x in pine_range(0, getLabSize - 1, 1):
                            getInnerLab = array.get(label.all, x)
                            __block_result_45__ = na
                            if method_call('get_x', getInnerLab) >= time:
                                __block_result_46__ = na
                                if getLabOuterY == method_call('get_y', array.get(label.all, x)) and getLabOuter != getInnerLab:
                                    __block_result_47__ = na
                                    if not string.contains(method_call('get_text', getLabOuter), method_call('get_text', getInnerLab)):
                                        method_call('set_text', getLabOuter, method_call('get_text', getLabOuter) + '/' + method_call('get_text', getInnerLab))
                                        method_call('set_text', getInnerLab, '')
                                        __block_result_47__ = method_call('set_xy', getInnerLab, NA(int), NA(float))
                                    __block_result_46__ = __block_result_47__
                                __block_result_45__ = __block_result_46__
                            __block_result_44__ = __block_result_45__
                        __block_result_43__ = __block_result_44__
                    __block_result_42__ = __block_result_43__
                __block_result_41__ = __block_result_42__
            __block_result_38__ = __block_result_41__
        return __block_result_38__

    calcKeyLevels()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
