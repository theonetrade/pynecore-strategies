"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, close, color, currency, high,
    input, label, line, linefill, low, math, matrix, na, plot, script, strategy, string, ta, table,
    time, timestamp
)
from pynecore.types import (
    Color, Label, Line, Matrix, NA, Persistent, PersistentSeries, Series,
    Table
)

useStratTip: str = 'Enables or disables the strategy tester allowing a change between either an indicator or a strategy.'
dLongTip: str = 'Detect long setups.'
dShortTip: str = 'Detect short setups.'
FLIPTip: str = 'Allow entry in the opposite bias while already in a position.'
startTip: str = 'Start date & time to begin backtest period. Useful for beginning new bot. eg. Set time to now to make broker emulator in a flat position with the proper starting captial before setting alerts'
endTip: str = 'End date & time to stop searching for setups for back testing.'
tolTip: str = 'The difference in height allowable for the signifcant points of the pattern expressed as a percent of the pattern height. Example: The points can vary in height by 15% of the pattern height from one another.'
lenTip: str = 'The length used to calcuate significant points to form pivots for pattern detection. Example: The highest or lowest point in 50 bars.'
fibTip: str = 'The fib target extension projected from the neckline of the pattern in the direction of the pattern bias expressed as a percent. Example: 100% is a 1:1 measurment of the height from the pattern neckline.'
stopPerTip: str = 'The fib extension of the pattern height measured from the point of invalidation. Example: 0% would be the high point of a double top. 50% would be halfway between the top and the neckline.'
offsetTip: str = 'The number of bars lines are extended into the future during an ongoing pattern.'
atrStopTip: str = 'Enables an ATR trailing stop once the target extension is breached. NOTE: This disables a take profit order in the strategy format.'
atrLenTip: str = 'The number of bars used in the ATR calculation.'
atrMultTip: str = 'The multiplier of the ATR value to subtract from the swing low or swing high point. Example: 1 is 100% of the ATR, 2 is 2x the ATR value.'
lookbackTip: str = 'The number of bars to look back to find a swing high or swing low to be used in the trailing stop calculation. Example: 1 ATR subtracted from the lowest point in 5 bars. 1 would use the lowest point within the last bar.'
tableTip: str = 'Show the data table for trade limit levels during an active trade. (table will only show when a pattern is present on the chart, or in bar replay).'
labelTip: str = 'Updates the double top/bottom label with \'Success\' or \'Failure\' and updates color based on the outcome of the pattern.'
thirdTip: str = 'Where would you like to send your alerts?'
pPhraseTip: str = 'A custom passphrase to authenticate your json message with a touch more security.'
aTronKeyTip: str = 'The name of your Alertatron API keys. (Add the ticker in brackets). Example: MyKeys(XBTUSD).'
tickerTip: str = 'The ticker to be traded when using Trading Connector'
LongTip: str = '3Commas start long deal bot keys.'
LongEndTip: str = '3Commas end long deal bot keys.'
ShortTip: str = '3Commas start short deal bot keys.'
ShortEndTip: str = '3Commas end short deal bot keys.'
S1: str = 'tiny'
P1: str = 'top'
S2: str = 'small'
P2: str = 'middle'
S3: str = 'normal'
P3: str = 'bottom'
S4: str = 'large'
P4: str = 'left'
S5: str = 'huge'
P5: str = 'center'
S6: str = 'auto'
P6: str = 'right'
A1: str = 'Custom Json'
A2: str = 'Trading Connector'
A3: str = 'Alertatron'
A4: str = '3Commas'
A5: str = 'Discord'
col1: Color = color.new(color.new('#B2B5BE'), 15)
col2: Color = color.new(color.new('#B2B5BE'), 87)
col3: Color = color.new(color.new('#FFFFFF'), 0)
col4: Color = color.new(color.new('#17FF00'), 15)
col5: Color = color.new(color.new('#FF0000'), 15)
col6: Color = color.new(color.new('#FF5252'), 0)
timeStart: int = timestamp('01 Jan 2000')
timeEnd: int = timestamp('01 Jan 2099')
GRP1: str = '════  Detection and Trade Parameters  ════'
GRP2: str = '═══════════ Time Filter ═══════════'
GRP3: str = '══════════ Trailing Stop ══════════'
GRP5: str = '════════════ Colors ════════════'
GRP6: str = '═════════  Table and Label  ═════════'
GRP7: str = '══════════ Alert Strings ══════════'


@script.strategy(title='Bjorgum Double Tap', shorttitle='Bj Double Tap', overlay=True, max_lines_count=500, max_labels_count=500, precision=3, default_qty_type=strategy.cash, commission_value=0.04, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=1000, initial_capital=1000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    useStrat=input.bool(True, 'Use Strategy', group=GRP1, tooltip=useStratTip),
    dLong=input.bool(True, 'Detect Bottoms', group=GRP1, tooltip=dLongTip),
    dShort=input.bool(True, 'Detect Tops', group=GRP1, tooltip=dShortTip),
    FLIP=input.bool(True, 'Flip Trades', group=GRP1, tooltip=FLIPTip),
    tol=input.float(15, 'Pivot Tolerance', group=GRP1, tooltip=tolTip, minval=1),
    len=input.int(50, 'Pivot Length', group=GRP1, tooltip=lenTip, minval=1),
    fib=input.float(100, 'Target Fib', group=GRP1, tooltip=fibTip, minval=0),
    stopPer=input.int(0, 'Stop Loss Fib', group=GRP1, tooltip=stopPerTip),
    offset=input.int(30, 'Line Offset', group=GRP1, tooltip=offsetTip, minval=0),
    startTime=input.time(timeStart, 'Start Filter', group=GRP2, tooltip=startTip),
    endTime=input.time(timeEnd, 'End Filter', group=GRP2, tooltip=endTip),
    atrStop=input.bool(False, 'Use Trail Stop', group=GRP3, tooltip=atrStopTip),
    atrLength=input.int(14, 'ATR Length', group=GRP3, tooltip=atrLenTip, minval=1),
    atrMult=input.float(1, 'ATR Multiplier', group=GRP3, tooltip=atrMultTip, minval=0),
    lookback=input.int(5, 'Swing Lookback', group=GRP3, tooltip=lookbackTip, minval=1),
    col=input.color(col1, 'Lines        ', group=GRP5, inline='41'),
    zCol=input.color(col3, 'Patterns       ', group=GRP5, inline='42'),
    hWidth=input.int(1, '', group=GRP5, inline='41', minval=1),
    zWidth=input.int(1, '', group=GRP5, inline='42', minval=1),
    colf=input.color(col2, 'Stop Fill', group=GRP5),
    tCol=input.color(col4, 'Target Color', group=GRP5),
    sCol=input.color(col5, 'Stop Color', group=GRP5),
    trailCol=input.color(col6, 'Trail Color', group=GRP5),
    showTable=input.bool(True, 'Show Table', group=GRP6, tooltip=tableTip),
    setLab=input.bool(True, 'Update Label', group=GRP6, tooltip=labelTip),
    labSize=input.string('small', 'Label Text Size', group=GRP6, options=(S1, S2, S3, S4, S5, S6)),
    textSize=input.string('normal', 'Table Text Size', group=GRP6, options=(S1, S2, S3, S4, S5, S6)),
    tableYpos=input.string('bottom', 'Table Position', group=GRP6, options=(P1, P2, P3)),
    tableXpos=input.string('right', '', group=GRP6, options=(P4, P5, P6)),
    thirdParty=input.string(A1, '3rd Party', group=GRP7, tooltip=thirdTip, options=(A1, A2, A3, A4, A5)),
    pPhrase=input.string('1234', 'Json Passphrase', group=GRP7, tooltip=pPhraseTip),
    aTronKey=input.string('myKeys', 'Alertatron Key', group=GRP7, tooltip=aTronKeyTip),
    tcTicker=input.string('', 'TC Ticker', group=GRP7, tooltip=tickerTip),
    c3Long=input.string('', '3Comma Long', group=GRP7, tooltip=LongTip),
    c3LongEnd=input.string('', '3Comma Long End', group=GRP7, tooltip=LongEndTip),
    c3Short=input.string('', '3Comma Short', group=GRP7, tooltip=ShortTip),
    c3ShortEnd=input.string('', '3Comma Short End', group=GRP7, tooltip=ShortEndTip)
):
    dt: str = 'Double Top'
    db: str = 'Double Bottom'
    suc: str = ' - Success'
    fail: str = ' - Failure'
    winStr: str = 'Target reached! 💰'
    loseStr: str = 'Stopped out... 🤷‍♂'
    tabPerc: str = '{0, number, #.##}\n({1, number, #.##}%)'
    tcStop: str = 'slmod slprice={0} tradeid={1}'
    dExit: str = '\'{\'"content": "```Bjorgum {0}\\n\\n\\t\'{{ticker}}\' \'{{interval}}\'\\n\\n\\t{1}```"\'}\''
    tnB: Persistent[str] = ''
    altStr: str = ''
    tUp: str = ''
    dCordWin: str = ''
    dCordLose: str = ''
    pos: float = strategy.position_size
    sync: int = bar_index
    confirm: bool = barstate.isconfirmed
    dir: PersistentSeries[int] = na(int)
    lmt: Persistent[float] = na(float)
    stp: Persistent[float] = na(float)
    altExit: str = na(str)
    FLAT: bool = pos == 0
    LONG: bool = pos > 0
    SHORT: bool = pos < 0
    tradeId: Persistent[int] = 0
    logs: Persistent[Matrix[float]] = matrix.new(5, 3, initial_value=NA(float))
    zLines: Persistent[list[Line]] = array.new_line(5)
    tLines: Persistent[list[Line]] = array.new_line(5)
    bLines: Persistent[list[Line]] = array.new_line(5)
    bullLb: Persistent[list[Label]] = array.new_label()
    bearLb: Persistent[list[Label]] = array.new_label()
    dif: bool = stopPer != 0
    set: int = sync + offset
    atr: float = ta.atr(14)
    sLow: float = ta.lowest(lookback) - atr * atrMult
    sHigh: float = ta.highest(lookback) + atr * atrMult
    pivHigh: float = ta.highest(len)
    pivLows: float = ta.lowest(len)
    hbar: float = ta.highestbars(len)
    lbar: float = ta.lowestbars(len)
    def High(m):
        result: float = high if m == 1 else low
        return result

    def Low(m):
        result: float = low if m == 1 else high
        return result

    def perD(_p):
        result: float = (_p - close) / close * 100
        return result

    def _coords(_x, _i):
        x = matrix.get(_x, _i, 0)
        y = matrix.get(_x, _i, 1)
        return (cast_int(x), y)

    def _arrayLoad(_x, _max, _val):
        array.unshift(_x, _val)
        __block_result__ = na
        if array.size(_x) > _max:
            __block_result__ = array.pop(_x)
        return __block_result__

    def _matrixPush(_mx, _max, _row):
        matrix.add_row(_mx, matrix.rows(_mx), _row)
        __block_result_1__ = na
        if matrix.rows(_mx) > _max:
            __block_result_1__ = matrix.remove_row(_mx, 0)
        return __block_result_1__

    def _mxLog(_cond, _x, _y):
        _row: list[float] = array.from_items(sync, _y, 0)
        __block_result_2__ = na
        if _cond:
            __block_result_2__ = _matrixPush(_x, 5, _row)
        return __block_result_2__

    def _mxUpdate(_cond, _dir, _x, y):
        m: int = 1 if _dir else -1
        _end: int = matrix.rows(_x) - 1
        __block_result_3__ = na
        if _cond and y * m > matrix.get(_x, _end, 1) * m:
            matrix.set(_x, _end, 0, sync)
            __block_result_3__ = matrix.set(_x, _end, 1, y)
        return __block_result_3__

    def _extend(_x, _len):
        __block_result_4__ = na
        for l in _x:
            __block_result_4__ = line.set_x2(l, _len)
        return __block_result_4__

    def _hLine(_l, x2, y2, y3, y4, y5, _t):
        l1: Line = line.new(x2, y2, set, y2, color=col, width=hWidth)
        l2: Line = line.new(x2, y4, set, y4, color=col, width=hWidth)
        array.set(_l, 3, l1)
        array.set(_l, 2, l2)
        array.set(_l, 1, line.new(x2, y3, set, y3, color=col, width=hWidth))
        array.set(_l, 0, line.new(sync - 1, _t, set, _t, color=col, width=hWidth))
        linefill.new(l1, l2, colf)
        __block_result_5__ = na
        if stopPer != 0:
            __block_result_5__ = array.set(_l, 4, line.new(sync - 1, y5, set, y5, color=col, width=hWidth))
        return __block_result_5__

    def _zLine(x1, y1, x2, y2, x3, y3, x4, y4):
        array.set(zLines, 3, line.new(x1, y1, x2, y2, color=zCol, width=zWidth))
        array.set(zLines, 2, line.new(x2, y2, x3, y3, color=zCol, width=zWidth))
        array.set(zLines, 1, line.new(x3, y3, x4, y4, color=zCol, width=zWidth))
        return array.set(zLines, 0, line.new(x4, y4, sync, close, color=zCol, width=zWidth))

    def _label(x, y, m):
        return _arrayLoad(bearLb, 1, label.new(x, y, dt, color=NA(Color), style=label.style_label_down, textcolor=col, size=labSize)) if m > 0 else _arrayLoad(bullLb, 1, label.new(x, y, db, color=NA(Color), style=label.style_label_up, textcolor=col, size=labSize))

    def _labelUpdate(_x, _y, m):
        __block_result_6__ = na
        if (_x or _y) and setLab:
            lab: Label = array.get(bearLb if m > 0 else bullLb, 0)
            oStr: str = dt if m > 0 else db
            nStr: str = oStr + (suc if _x else fail)
            label.set_text(lab, nStr)
            __block_result_6__ = label.set_textcolor(lab, tCol if _x else sCol)
        return __block_result_6__

    def _atrTrail(_cond, _lt, _s, m):
        _stop: Persistent[float] = na(float)
        _flag: Persistent[bool] = na(bool)
        _trail: Persistent[bool] = na(bool)
        _flag = _cond
        _stop = _s
        _trail = False if _flag else _trail
        if atrStop and useStrat:
            if _lt:
                _flag = False
                _trail = True
            _stop = (sLow if _lt else math.max(_stop, sLow)) if m == -1 else _stop
            _stop = (sHigh if _lt else math.min(_stop, sHigh)) if m == 1 else _stop
        if High(m) * m > _stop * m:
            _flag = True
            _trail = False
        return (_flag, _stop, _trail)

    def _inTrade(_cond, _x, _e, m):
        _flag: Persistent[bool] = na(bool)
        _stop: Persistent[float] = na(float)
        _limit: Persistent[float] = na(float)
        l1: Line = array.get(_x, 0)
        lp: float = line.get_price(l1, sync)
        l2: Line = array.get(_x, 4 if dif else 2)
        ls: float = line.get_price(l2, sync)
        win: bool = Low(m) * m <= lp * m and (not _e)
        lose: bool = High(m) * m >= ls * m and (not _e)
        _flag = _cond
        _stop = ls if _e else _stop
        _limit = lp if _e else _limit
        if win or lose:
            _flag = True
            _extend(_x, sync)
            _labelUpdate(win, lose, m)
            line.set_color(l1 if win else l2, tCol if win else sCol)
            array.fill(_x, na)
            array.fill(zLines, na)
        _f, _s, _t = _atrTrail(_flag, win, _stop, m)
        _flag = _f if atrStop else _flag
        _stop = _s if _t and _s * m < _stop * m and confirm else _stop
        return (_flag, _stop, _t, _limit)

    def _double(_cond, _l, _x, m):
        _flag: Persistent[bool] = na(bool)
        _rows: int = matrix.rows(_x)
        _flag = _cond
        if _flag:
            x1, y1 = _coords(_x, _rows - 5)
            x2, y2 = _coords(_x, _rows - 4)
            x3, y3 = _coords(_x, _rows - 3)
            x4, y4 = _coords(_x, _rows - 2)
            traded: bool = matrix.get(_x, _rows - 2, 2)
            height: float = math.avg(y2, y4) - y3
            _high: float = y2 + height * (tol / 100)
            _low: float = y2 - height * (tol / 100)
            _t: float = y3 - height * (fib / 100)
            y5: float = y2 if y2 * m < y4 * m else y4
            y6: float = y2 if y2 * m > y4 * m else y4
            y7: float = y6 - height * (stopPer / 100)
            result: bool = y1 * m < y3 * m and y4 * m <= _high * m and (y4 * m >= _low * m) and (close * m < y3 * m) and (not close[1] * m < y3 * m) and (not traded)
            if result and _flag and (dShort if m > 0 else dLong):
                _hLine(_l, x2, y5, y3, y6, y7, _t)
                _zLine(x1, y1, x2, y2, x3, y3, x4, y4)
                _label(x4, y6, m)
                matrix.set(_x, _rows - 2, 2, 1)
                _flag = False
        return _flag

    def _scan(_l, _x, m):
        _cond: PersistentSeries[bool] = True
        _cond = _double(_cond, _l, _x, m)
        enter: bool = _cond[1] and (not _cond)
        f, s, t, l = _inTrade(_cond, _l, enter, m)
        _cond = f
        _extend(_l, set)
        return (f, s, t, l)

    def _populate(_n, _x, _i, _col):
        __block_result_7__ = na
        for i, _a in enumerate(_x):
            __block_result_8__ = na
            if not na(_a):
                __block_result_8__ = table.cell(table_id=_n, column=_i, row=i, bgcolor=na, text=_a, text_color=_col, text_size=textSize)
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    dir = 1 if not hbar else 0 if not lbar else dir
    dirUp: bool = dir != dir[1] and cast_bool(dir)
    dirDn: bool = dir != dir[1] and (not dir)
    setUp: bool = not hbar and cast_bool(dir)
    setDn: bool = not lbar and (not dir)
    _mxLog(dirUp or dirDn, logs, pivHigh if dirUp else pivLows)
    _mxUpdate(setUp or setDn, dir, logs, pivHigh if setUp else pivLows)
    bear: Series
    ss: Series
    bear, ss, ts, sl = _scan(tLines, logs, 1)
    bull: Series
    ls: Series
    bull, ls, tl, ll = _scan(bLines, logs, -1)
    st: Series[bool] = ts if SHORT else False
    lt: Series[bool] = tl if LONG else False
    sell: bool = bear[1] and (not bear)
    buy: bool = bull[1] and (not bull)
    ssCol: Color = trailCol if st or st[1] else na
    lsCol: Color = trailCol if lt or lt[1] else na
    longEntry: bool = buy and (FLAT or (SHORT and FLIP))
    shortEntry: bool = sell and (FLAT or (LONG and FLIP))
    dateFilter: bool = time >= startTime and time <= endTime
    tradeId = tradeId + (1 if longEntry or shortEntry else 0)
    lmt = na if atrStop else sl if shortEntry else ll if longEntry else lmt
    stp = ss if shortEntry or (SHORT and atrStop) else ls if longEntry or (LONG and atrStop) else stp
    plot(ss if atrStop else na, 'Short Stop', ssCol, style=plot.style_linebr)
    plot(ls if atrStop else na, 'Long Stop', lsCol, style=plot.style_linebr)
    bgcolor(color.new(color.red, 80) if not dateFilter else na, title='Filter Color')
    if showTable:
        tls: str = na if bull else string.format(tabPerc, ls, perD(ls))
        tss: str = na if bear else string.format(tabPerc, ss, perD(ss))
        tll: str = na if bull else string.format(tabPerc, ll, perD(ll))
        tsl: str = na if bear else string.format(tabPerc, sl, perD(sl))
        titles: list[str] = array.from_items(na(int), na if bull else 'Bullish', na if bear else 'Bearish')
        stops: list[str] = array.from_items('Stop', tls, tss)
        limtis: list[str] = array.from_items('Target', tll, tsl)
        bjTab: Table = table.new(tableYpos + '_' + tableXpos, 3, 3, border_color=color.new(color.gray, 60), border_width=1)
        if not bear or not bull:
            _populate(bjTab, titles, 0, color.white)
            _populate(bjTab, stops, 1, color.red)
            if not (na(ll) or lt) or not (na(sl) or st):
                _populate(bjTab, limtis, 2, color.green)
    cSon: bool = thirdParty == A1
    tCon: bool = thirdParty == A2
    aTron: bool = thirdParty == A3
    c3: bool = thirdParty == A4
    dCord: bool = thirdParty == A5
    if cSon and useStrat:
        json: str = '\'{\' \n    "passphrase": "{0}", \n    "time": \'"{{timenow}}"\', \n    "ticker": \'"{{ticker}}"\', \n    "plot": \'{\' \n        "stop_price": {1, number, #.########}, \n        "limit_price": {2, number, #.########} \n    \'}\', \n    "strategy": \'{\' \n        "position_size": \'{{strategy.position_size}}\', \n        "order_action": \'"{{strategy.order.action}}"\', \n        "market_position": \'"{{strategy.market_position}}"\', \n        "market_position_size": \'{{strategy.market_position_size}}\', \n        "prev_market_position": \'"{{strategy.prev_market_position}}"\', \n        "prev_market_position_size": \'{{strategy.prev_market_position_size}}\' \n    \'}\' \n\'}\''
        altStr = string.format(json, pPhrase, stp, lmt)
    if tCon and useStrat:
        tcTrade: str = "'{{strategy.order.action}}' tradesymbol={0} tradeid={1}" + ('' if atrStop else ' tpprice={2, number, #.########}') + ' slprice={3, number, #.########}'
        altStr = string.format(tcTrade, tcTicker, tradeId, lmt, stp)
        tUp = string.format(tcStop, stp, tradeId)
    if aTron and useStrat:
        altEnt: str = aTronKey + " '{'\ncancel(which=all);\nmarket(position='{{strategy.position_size}}');\n"
        altEnd: str = '\'}\'\n#bot'
        altBrkt: str = ('stopOrder(' if atrStop else 'stopOrTakeProfit(') + ('' if atrStop else 'tp=@{0, number, #.########}, ') + ('offset=@' if atrStop else 'sl=@') + '{1, number, #.########}, position=0, reduceOnly=true' + (', tag=trail' if atrStop else '') + ');\n'
        enter: str = altEnt + altBrkt + altEnd
        exit: str = altEnt + altEnd
        altStr = string.format(enter, lmt, stp)
        altExit = exit if na(altExit) else altExit
        stopUpdate: str = aTronKey + " '{'\ncancel(which=tagged, tag=trail);\n" + altBrkt + altEnd
        tUp = string.format(stopUpdate, lmt, stp) if atrStop else tUp
    if dCord and useStrat:
        tnB = db if longEntry else dt if shortEntry else tnB
        postTrade: str = '\'{\'"content": "```🚨 Bjorgum {0} detected 🚨\\n\\n\\t\'{{ticker}}\' \'{{interval}}\'\\n\\n\\t' + ('' if atrStop else '🎯 Target: {1, number, #.########}\\n\\t') + '🛑 Stop:   {2, number, #.########}```"\'}\''
        altStr = string.format(postTrade, tnB, lmt, stp)
        dCordWin = string.format(dExit, tnB, winStr)
        dCordLose = string.format(dExit, tnB, loseStr)
    if c3 and useStrat:
        c3Long = string.format('[{0}, {1}]', c3ShortEnd, c3Long) if SHORT and buy else c3Long
        c3Short = string.format('[{0}, {1}]', c3LongEnd, c3Short) if LONG and sell else c3Short
    if useStrat and longEntry and dateFilter:
        strategy.entry('Long', strategy.long, comment='Long', alert_message=c3Long if c3 else altStr)
    if useStrat and shortEntry and dateFilter:
        strategy.entry('Short', strategy.short, comment='Short', alert_message=c3Short if c3 else altStr)
    strategy.exit('Long Exit', 'Long', stop=stp, limit=lmt, comment='L Exit', alert_message=c3LongEnd if c3 else altExit if aTron else 'closelong' if tCon else na if dCord else altStr, alert_profit=dCordWin if dCord else na, alert_loss=dCordLose if dCord else na)
    strategy.exit('Short Exit', 'Short', stop=stp, limit=lmt, comment='S Exit', alert_message=c3ShortEnd if c3 else altExit if aTron else 'closeshort' if tCon else na if dCord else altStr, alert_profit=dCordWin if dCord else na, alert_loss=dCordLose if dCord else na)
    if (lt and ls != ls[1] or (st and ss != ss[1])) and (tCon or aTron):
        alert(tUp, alert.freq_once_per_bar_close)
    if not useStrat and (buy or sell):
        alert((db if buy else dt) + ' Detected', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
