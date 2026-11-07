"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    bar_index, barstate, color, dayofmonth, high, hour, input, label, line,
    math, minute, month, na, open, script, second, size, string, syminfo, ta, table, time,
    time_close, timeframe, timenow, timestamp, xloc, year, yloc
)
from pynecore.types import Color, IBPersistent, Label, NA, Persistent, Series, Table
from typing import Protocol, Any


__all__ = ['formattedDate', 'formattedDay', 'formattedNoOfPeriods', 'formattedTime', 'secondsSince', 'secondsToTfString', 'timeFrom']


class _ProtocolFormattedtime(Protocol):
    def __call__(self, timeInMs: Series[float], format__ren__: Series[str] = 'HH:mm:ss') -> Any: ...


class _ProtocolFormatteddate(Protocol):
    def __call__(self, timeInMs: Series[float], format__ren__: Series[str] = 'yyyy-MM-dd') -> Any: ...


class _ProtocolFormattedday(Protocol):
    def __call__(self, timeInMs: Series[float], format__ren__: Series[str] = 'EEEE') -> Any: ...


class _ProtocolSecondssince(Protocol):
    def __call__(self, cond: Series[bool], resetCond: Series[bool] = barstate.isnew) -> Any: ...


class _ProtocolTimefrom(Protocol):
    def __call__(self, from__ren__: Series[str] = 'bar', qty: Series[int] = ..., units: Series[str] = ...) -> Any: ...


class _ProtocolFormattednoofperiods(Protocol):
    def __call__(self, ms: Series[int], unit: Series[str] = na) -> Any: ...


class _ProtocolSecondstotfstring(Protocol):
    def __call__(self, tfInSeconds: int, mult: float = 1.0) -> Any: ...


formattedTime: _ProtocolFormattedtime = Exported()
formattedDate: _ProtocolFormatteddate = Exported()
formattedDay: _ProtocolFormattedday = Exported()
secondsSince: _ProtocolSecondssince = Exported()
timeFrom: _ProtocolTimefrom = Exported()
formattedNoOfPeriods: _ProtocolFormattednoofperiods = Exported()
secondsToTfString: _ProtocolSecondstotfstring = Exported()

SI1: str = 'tiny'
TP1: str = 'top'
SI2: str = 'small'
TP2: str = 'middle'
SI3: str = 'normal'
TP3: str = 'bottom'
SI4: str = 'large'
TP4: str = 'left'
SI5: str = 'huge'
TP5: str = 'center'
SI6: str = 'auto'
TP6: str = 'right'
TU1: str = 'chart'
OF1: str = 'Bar\'s Open Time'
TU2: str = 'seconds'
OF2: str = 'Bar\'s Close Time'
TU3: str = 'minutes'
OF3: str = 'Current Time'
TU4: str = 'hours'
TU5: str = 'days'
TU6: str = 'weeks'
TU7: str = 'months'
TU8: str = 'years'
N_TT: str = 'Number of time units to calculate the line offset. Example: 20 hours.'
UNITS_TT: str = 'Unit of time to calculate the offset for lines in.'
FROM_TT: str = 'Starting time from where the offset for lines is calculated.'
TICKS_TT: str = 'The number of ticks between the open and the high to trigger the alert. Once the value is exceeded the timer will start.'
SEC_TT: str = 'Seconds for which the condition must be continuously true before the alert triggers.'
RESET_TT: str = 'When checked, the duration will reset every time a new realtime bar begins.'
INPUT_TT: str = 'When checked, will measure the length of the lines in the following units of time, otherwise will select a unit of time automatically.'
TIME_TT: str = 'Units to measure the length of the lines in.'
MULT_TT: str = 'Multiplier for the chart timeframe string. \nExample: 1 will display the current time, 2 will display 2 times the chart time, etc.'
SIZE_TT: str = 'Changes the size of the display table.'
POS_TT: str = 'Changes the position of the display table on the screen.'
GRP1: str = '══════════ Seconds since ══════════'
GRP2: str = '═══════════   Time from   ═══════════'
GRP3: str = '════ Formatted number of periods ════'
GRP4: str = '════════   Seconds to string   ════════'


@script.library('Time', True)
def main(
    ticksInput=input.int(0, 'Number Of Ticks From Open', group=GRP1, tooltip=TICKS_TT),
    secondsInput=input.int(20, 'Seconds condition must last', group=GRP1, tooltip=SEC_TT, minval=1),
    resetInput=input.bool(True, 'Reset timing on new bar', group=GRP1, tooltip=RESET_TT),
    nInput=input.int(20, 'Lines End At Offset n (+/-)', group=GRP2, tooltip=N_TT),
    unitsInput=input.string(TU1, 'Offset Units', group=GRP2, tooltip=UNITS_TT, options=(TU1, TU2, TU3, TU4, TU5, TU7, TU8)),
    fromInput=input.string(OF1, 'Calculated from', group=GRP2, tooltip=FROM_TT, options=(OF1, OF2, OF3)),
    useTimeInput=input.bool(False, 'Use Input Time', group=GRP3, tooltip=INPUT_TT),
    timeInput=input.string('seconds', 'Unit of Time', group=GRP3, tooltip=TIME_TT, options=(TU2, TU3, TU4, TU5, TU6, TU7)),
    tfMultInput=input.float(1.0, 'Timeframe Multiplier', group=GRP4, tooltip=MULT_TT),
    textSizeInput=input.string('large', 'Text size', group=GRP4, tooltip=SIZE_TT, options=(SI1, SI2, SI3, SI4, SI5, SI6)),
    tableYposInput=input.string('bottom', 'Position  ', group=GRP4, tooltip=POS_TT, options=(TP1, TP2, TP3), inline='41'),
    tableXposInput=input.string('right', '', group=GRP4, options=(TP4, TP5, TP6), inline='41')
):
    @export
    def formattedTime(timeInMs: Series[float], format__ren__: Series[str] = 'HH:mm:ss'):
        result: str = string.format('{0,time,' + format__ren__ + '}', cast_int(timeInMs))
        return result

    @export
    def formattedDate(timeInMs: Series[float], format__ren__: Series[str] = 'yyyy-MM-dd'):
        result: str = string.format('{0,date,' + format__ren__ + '}', cast_int(timeInMs))
        return result

    @export
    def formattedDay(timeInMs: Series[float], format__ren__: Series[str] = 'EEEE'):
        result: str = string.format('{0,time,' + format__ren__ + '}', cast_int(timeInMs))
        return result

    @export
    def secondsSince(cond: Series[bool], resetCond: Series[bool] = barstate.isnew):
        timeBegin: IBPersistent[int] = na(int)
        lastCond: IBPersistent[bool] = False
        if resetCond:
            timeBegin = timenow if cond else na
        elif cond:
            if not lastCond:
                timeBegin = timenow
        else:
            timeBegin = na
        lastCond = cond
        result: int = (timenow - timeBegin) / 1000
        return result

    @export
    def timeFrom(from__ren__: Series[str] = 'bar', qty: Series[int] = na, units: Series[str] = na):
        result: int = na(int)
        unit: str = string.match(units, '.*[^s]')
        t: int = time if from__ren__ == 'bar' else time_close if from__ren__ == 'close' else timenow
        if units == 'chart':
            result = cast_int(t + timeframe.in_seconds() * 1000 * qty)
        else:
            y: int = year(t) + (qty if unit == 'year' else 0)
            m: int = month(t) + (qty if unit == 'month' else 0)
            d: int = dayofmonth(t) + (qty if unit == 'day' else 0)
            hr: int = hour(t) + (qty if unit == 'hour' else 0)
            min: int = minute(t) + (qty if unit == 'minute' else 0)
            sec: int = second(t) + (qty if unit == 'second' else 0)
            result = timestamp(y, m, d, hr, min, sec)
        return result

    @export
    def formattedNoOfPeriods(ms: Series[int], unit: Series[str] = na):
        __block_result__ = (na, na)
        if na(unit):
            __block_result_1__ = (na, na)
            if ms < 60000:
                __block_result_1__ = ('seconds', 1000)
            elif ms < 3600000:
                __block_result_1__ = ('minutes', 60000)
            elif ms < 86400000:
                __block_result_1__ = ('hours', 3600000)
            elif ms < 604800000:
                __block_result_1__ = ('days', 86400000)
            elif ms < 2628003000:
                __block_result_1__ = ('weeks', 604800000)
            else:
                __block_result_1__ = ('months', 2628003000)
            __block_result__ = __block_result_1__
        else:
            __block_result_2__ = (na, na)
            __switch_1__ = unit
            if __switch_1__ == 'seconds':
                __block_result_2__ = (unit, 1000)
            elif __switch_1__ == 'minutes':
                __block_result_2__ = (unit, 60000)
            elif __switch_1__ == 'hours':
                __block_result_2__ = (unit, 3600000)
            elif __switch_1__ == 'days':
                __block_result_2__ = (unit, 86400000)
            elif __switch_1__ == 'weeks':
                __block_result_2__ = (unit, 604800000)
            else:
                __block_result_2__ = (unit, 2628003000)
            __block_result__ = __block_result_2__
        tf, denominator = __block_result__
        qty: float = math.round(ms / denominator, 2)
        unitString: str = tf if qty > 2 else string.match(tf, '.*[^s]')
        result: str = string.tostring(qty) + ' ' + unitString
        return result

    @export
    def secondsToTfString(tfInSeconds: int, mult: float = 1.0):
        tfInMin: float = tfInSeconds / 60 * math.max(mult, 1)
        __block_result_3__ = na
        if tfInMin <= 0.017:
            __block_result_3__ = '1S'
        elif tfInMin <= 0.084:
            __block_result_3__ = '5S'
        elif tfInMin <= 0.251:
            __block_result_3__ = '15S'
        elif tfInMin <= 0.501:
            __block_result_3__ = '30S'
        elif tfInMin < 1440:
            __block_result_3__ = string.tostring(math.round(tfInMin))
        elif tfInMin % 10080 == 0:
            __block_result_3__ = string.tostring(tfInMin / 10080) + 'W'
        elif tfInMin % 43800 == 0:
            __block_result_3__ = string.tostring(tfInMin / 43800) + 'M'
        elif tfInMin <= 43800:
            __block_result_3__ = string.tostring(math.round(math.min(tfInMin / 1440, 365))) + 'D'
        else:
            __block_result_3__ = string.tostring(math.round(math.min(tfInMin / 43800, 12))) + 'M'
        result: str = __block_result_3__
        return result

    LEFT_BARS: int = 20
    RIGHT_BARS: int = 20
    pivotHi: float = ta.pivothigh(LEFT_BARS, RIGHT_BARS)
    pivotLo: float = ta.pivotlow(LEFT_BARS, RIGHT_BARS)
    __block_result_4__ = na
    __switch__ = fromInput
    if __switch__ == OF1:
        __block_result_4__ = 'bar'
    elif __switch__ == OF2:
        __block_result_4__ = 'close'
    else:
        __block_result_4__ = 'now'
    from__ren__: Persistent[str] = __block_result_4__
    timeTo: Series[int] = timeFrom(from__ren__, nInput, unitsInput)
    pivotTime: int = time[RIGHT_BARS]
    offsetTime: int = timeTo[RIGHT_BARS]
    timeUnit: Persistent[str] = timeInput if useTimeInput else na
    if not na(pivotHi):
        line.new(pivotTime, pivotHi, offsetTime, pivotHi, xloc.bar_time, color=color.fuchsia, style=line.style_arrow_right, width=2)
        label.new(pivotTime, pivotHi, formattedDate(pivotTime, 'full'), xloc.bar_time, color=color.new(color.gray, 85), style=label.style_label_down, textcolor=color.lime)
        label.new(time, pivotHi, formattedNoOfPeriods(offsetTime - pivotTime, timeUnit), xloc.bar_time, color=NA(Color), style=label.style_label_up, textcolor=color.fuchsia, size=size.small)
    if not na(pivotLo):
        line.new(pivotTime, pivotLo, offsetTime, pivotLo, xloc.bar_time, color=color.gray, style=line.style_arrow_right, width=2)
        label.new(pivotTime, pivotLo, formattedDay(pivotTime, "yyyy.MM.dd G 'at' hh:mm:ss z"), xloc.bar_time, color=color.new(color.gray, 85), style=label.style_label_up, textcolor=color.fuchsia)
        label.new(time, pivotLo, formattedNoOfPeriods(offsetTime - pivotTime, timeUnit), xloc.bar_time, color=NA(Color), style=label.style_label_down, textcolor=color.gray, size=size.small)
    cond: bool = math.abs(high - open) > syminfo.mintick * ticksInput
    secFromOpen: int = secondsSince(cond, resetInput and barstate.isnew)
    timeAlert: bool = secFromOpen > secondsInput
    alertTime: str = formattedTime(secFromOpen * 1000, 'mm:ss')
    __block_result_5__ = na
    if timeAlert:
        __block_result_5__ = 'Timed Alert Triggered\n\n' + alertTime
    elif cond:
        __block_result_5__ = 'Condition Detected...\n\nTimer count\n' + alertTime
    else:
        __block_result_5__ = 'Waiting for condition...'
    alertString: str = __block_result_5__
    if barstate.islast:
        condTime: Persistent[Label] = label.new(na, na, yloc=yloc.abovebar, style=label.style_label_lower_left, textcolor=color.white)
        label.set_x(condTime, bar_index)
        label.set_text(condTime, alertString)
        label.set_color(condTime, color.new(color.green, 50) if timeAlert else color.new(color.orange, 0) if cond else color.new(color.red, 50))
        tfDisplay: Persistent[Table] = table.new(tableYposInput + '_' + tableXposInput, 1, 1)
        table.cell(tfDisplay, 0, 0, secondsToTfString(timeframe.in_seconds(), tfMultInput), bgcolor=color.yellow, text_color=color.black, text_size=textSizeInput)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
