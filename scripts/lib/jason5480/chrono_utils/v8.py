"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, bgcolor, box, chart, close, color,
    dayofmonth, dayofweek, display, high, hour, input, line, location, log, low, map, math, minute,
    month, na, open, plotchar, position, runtime, script, second, size, string, syminfo, table,
    text, time, time_close, timeframe, timestamp, year
)
from pynecore.types import Box, Color, Line, NA, Persistent, PersistentSeries, Series
from pynecore.types.chart import ChartPoint
from typing import Protocol, Any


__all__ = ['DateTimeWindow', 'Session', 'SessionDays', 'SessionTime', 'SessionTimeRange', 'SessionView', 'Timezone', 'ViewMode', 'barInMilliseconds', 'draw', 'draw_bars', 'draw_boxes', 'draw_candles', 'from_sess_string', 'get_ms_in_day', 'get_sec_in_day', 'get_size_in_bars', 'get_size_in_secs', 'init', 'is_bar_included', 'is_day_included', 'monthInDays', 'monthInMilliseconds', 'nameOfDay', 'nextDayAfter', 'next_day', 'normalize', 'normalizeHour', 'normalizeMinute', 'nthDayAfter', 'nthDayBefore', 'nth_day_after', 'nth_day_before', 'prevDayBefore', 'previous_day', 'to_sess_string', 'to_sess_strings', 'to_string', 'today', 'tomorrow']


class Timezone(Enum):
    Utc = 'UTC'
    Exchange = 'Exchange'
    Honolulu = '(UTC-10) Honolulu'
    Anchorage = '(UTC-9/-8) Anchorage'
    Juneau = '(UTC-9/-8) Juneau'
    Los_Angeles = '(UTC-8/-7) Los Angeles'
    Vancouver = '(UTC-8/-7) Vancouver'
    Denver = '(UTC-7/-6) Denver'
    Phoenix = '(UTC-7) Phoenix'
    Chicago = '(UTC-6/-5) Chicago'
    Mexico_City = '(UTC-6) Mexico City'
    San_Salvador = '(UTC-6) San Salvador'
    Bogota = '(UTC-5) Bogota'
    Lima = '(UTC-5) Lima'
    New_York = '(UTC-5/-4) New York'
    Toronto = '(UTC-5/-4) Toronto'
    Caracas = '(UTC-4) Caracas'
    Santiago = '(UTC-4/-3) Santiago'
    Buenos_Aires = '(UTC-3) Buenos Aires'
    Sao_Palo = '(UTC-3) Sao Paulo'
    Azores = '(UTC-1/+0) Azores'
    Dublin = '(UTC+0/+1) Dublin'
    Lisbon = '(UTC+0/+1) Lisbon'
    London = '(UTC+0/+1) London'
    Reykjavik = '(UTC) Reykjavik'
    Amsterdam = '(UTC+1/+2) Amsterdam'
    Belgrade = '(UTC+1/+2) Belgrade'
    Berlin = '(UTC+1/+2) Berlin'
    Bratislava = '(UTC+1/+2) Bratislava'
    Brussels = '(UTC+1/+2) Brussels'
    Budapest = '(UTC+1/+2) Budapest'
    Casablanca = '(UTC+1/+0) Casablanca'
    Copenhagen = '(UTC+1/+2) Copenhagen'
    Lagos = '(UTC+1) Lagos'
    Luxembourg = '(UTC+1/+2) Luxembourg'
    Madrid = '(UTC+1/+2) Madrid'
    Malta = '(UTC+1/+2) Malta'
    Oslo = '(UTC+1/+2) Oslo'
    Paris = '(UTC+1/+2) Paris'
    Prague = '(UTC+1/+2) Prague'
    Rome = '(UTC+1/+2) Rome'
    Stockholm = '(UTC+1/+2) Stockholm'
    Tunis = '(UTC+1) Tunis'
    Vienna = '(UTC+1/+2) Vienna'
    Warsaw = '(UTC+1/+2) Warsaw'
    Zurich = '(UTC+1/+2) Zurich'
    Athens = '(UTC+2/+3) Athens'
    Bucharest = '(UTC+2/+3) Bucharest'
    Cairo = '(UTC+2/+3) Cairo'
    Helsinki = '(UTC+2/+3) Helsinki'
    Jerusalem = '(UTC+2/+3) Jerusalem'
    Johannesburg = '(UTC+2) Johannesburg'
    Nicosia = '(UTC+2/+3) Nicosia'
    Riga = '(UTC+2/+3) Riga'
    Tallinn = '(UTC+2/+3) Tallinn'
    Vilnius = '(UTC+2/+3) Vilnius'
    Bahrain = '(UTC+3) Bahrain'
    Istanbul = '(UTC+3) Istanbul'
    Kuwait = '(UTC+3) Kuwait'
    Moscow = '(UTC+3) Moscow'
    Nairobi = '(UTC+3) Nairobi'
    Qatar = '(UTC+3) Qatar'
    Riyadh = '(UTC+3) Riyadh'
    Tehran = '(UTC+3:30) Tehran'
    Dubai = '(UTC+4) Dubai'
    Muscat = '(UTC+4) Muscat'
    Kabul = '(UTC+4:30) Kabul'
    Ashgabat = '(UTC+5) Ashgabat'
    Astana = '(UTC+5) Astana'
    Karachi = '(UTC+5) Karachi'
    Colombo = '(UTC+5:30) Colombo'
    Kolkata = '(UTC+5:30) Kolkata'
    Kathmandu = '(UTC+5:45) Kathmandu'
    Dhaka = '(UTC+6) Dhaka'
    Yangon = '(UTC+6:30) Yangon'
    Bangkok = '(UTC+7) Bangkok'
    Ho_Chi_Minh = '(UTC+7) Ho Chi Minh'
    Jakarta = '(UTC+7) Jakarta'
    Chongqing = '(UTC+8) Chongqing'
    Hong_Kong = '(UTC+8) Hong Kong'
    Kuala_Lumpur = '(UTC+8) Kuala Lumpur'
    Manila = '(UTC+8) Manila'
    Perth = '(UTC+8) Perth'
    Shanghai = '(UTC+8) Shanghai'
    Singapore = '(UTC+8) Singapore'
    Taipei = '(UTC+8) Taipei'
    Seoul = '(UTC+9) Seoul'
    Tokyo = '(UTC+9) Tokyo'
    Adelaide = '(UTC+9:30/+10:30) Adelaide'
    Brisbane = '(UTC+10) Brisbane'
    Sydney = '(UTC+10/+11) Sydney'
    Norfolk_Island = '(UTC+11/+12) Norfolk Island'
    New_Zealand = '(UTC+12/+13) New Zealand'
    Chatham_Islands = '(UTC+12:45/+13:45) Chatham Islands'
    Tokelau = '(UTC+13) Tokelau'


@udt
class Bar:
    openUnixTime: int = na(int)
    closeUnixTime: int = na(int)


@udt
class DateTimeWindow:
    fromDateTime: int = na(int)
    toDateTime: int = na(int)


@udt
class SessionDays:
    days: dict[int, bool] = na(dict)


@udt
class SessionTime:
    hourInDay: int = 0
    minuteInHour: int = 0
    minuteInDay: int = 0


@udt
class SessionTimeRange:
    startTime: 'SessionTime' = _dataclass_field(default_factory=lambda: na(SessionTime))
    endTime: 'SessionTime' = _dataclass_field(default_factory=lambda: na(SessionTime))
    isOvernight: bool = na(bool)


@udt
class Session:
    days: 'SessionDays' = _dataclass_field(default_factory=lambda: na(SessionDays))
    timeRanges: 'list[SessionTimeRange]' = na(list)


@udt
class SessionView:
    sess: 'Session' = _dataclass_field(default_factory=lambda: na(Session))
    names: list[str] = na(list)
    colors: list[Color] = na(list)


class ViewMode(Enum):
    Boxes = 'Boxes'
    Candles = 'Candles'
    Bars = 'Bars'


class _ProtocolToString(Protocol):
    def __call__(self, timezone: Timezone) -> Any: ...


class _ProtocolNameofday(Protocol):
    def __call__(self, day: int) -> Any: ...


class _ProtocolToday(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolNthdayafter(Protocol):
    def __call__(self, day: int, n: int) -> Any: ...


class _ProtocolNextdayafter(Protocol):
    def __call__(self, day: int) -> Any: ...


class _ProtocolNthdaybefore(Protocol):
    def __call__(self, day: int, n: int = 1) -> Any: ...


class _ProtocolPrevdaybefore(Protocol):
    def __call__(self, day: int) -> Any: ...


class _ProtocolTomorrow(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolNormalize(Protocol):
    def __call__(self, num: int, min: int, max: int) -> Any: ...


class _ProtocolNormalizehour(Protocol):
    def __call__(self, hourInDay: int) -> Any: ...


class _ProtocolNormalizeminute(Protocol):
    def __call__(self, minuteInHour: int) -> Any: ...


class _ProtocolMonthindays(Protocol):
    def __call__(self, mon: int, yer: int, rolloverMonths: bool = False) -> Any: ...


class _ProtocolMonthinmilliseconds(Protocol):
    def __call__(self, mon: int, yer: int, rolloverMonths: bool = True) -> Any: ...


class _ProtocolMonthinmilliseconds13(Protocol):
    def __call__(self, mon: int) -> Any: ...


class _ProtocolBarinmilliseconds(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolInit(Protocol):
    def __call__(self, this: DateTimeWindow, fromDateTime: int, toDateTime: int) -> Any: ...


class _ProtocolInit16(Protocol):
    def __call__(self, this: DateTimeWindow, refTimezone: str, chTimezone: str, fromDateTime: int, toDateTime: int) -> Any: ...


class _ProtocolToString17(Protocol):
    def __call__(self, this: DateTimeWindow) -> Any: ...


class _ProtocolGetSizeInSecs(Protocol):
    def __call__(self, this: DateTimeWindow) -> Any: ...


class _ProtocolGetSizeInBars(Protocol):
    def __call__(self, this: DateTimeWindow) -> Any: ...


class _ProtocolIsBarIncluded(Protocol):
    def __call__(self, this: DateTimeWindow, offset_forward: int = 1) -> Any: ...


class _ProtocolInit21(Protocol):
    def __call__(self, this: SessionDays, sun: bool = True, mon: bool = True, tue: bool = True, wed: bool = True, thu: bool = True, fri: bool = True, sat: bool = True) -> Any: ...


class _ProtocolToSessString(Protocol):
    def __call__(self, this: SessionDays) -> Any: ...


class _ProtocolFromSessString(Protocol):
    def __call__(self, this: SessionDays, sess: str) -> Any: ...


class _ProtocolToString24(Protocol):
    def __call__(self, this: SessionDays) -> Any: ...


class _ProtocolNthDayAfter(Protocol):
    def __call__(self, this: SessionDays, day: int, n: int) -> Any: ...


class _ProtocolNthDayBefore(Protocol):
    def __call__(self, this: SessionDays, day: int, n: int) -> Any: ...


class _ProtocolNextDay(Protocol):
    def __call__(self, this: SessionDays) -> Any: ...


class _ProtocolPreviousDay(Protocol):
    def __call__(self, this: SessionDays) -> Any: ...


class _ProtocolInit29(Protocol):
    def __call__(self, this: SessionTime, unixTime: int) -> Any: ...


class _ProtocolInit30(Protocol):
    def __call__(self, this: SessionTime, hourInDay: int, minuteInHour: int) -> Any: ...


class _ProtocolInit31(Protocol):
    def __call__(self, this: SessionTime, hourInDay: int, minuteInHour: int, refTimezone: str) -> Any: ...


class _ProtocolToSessString32(Protocol):
    def __call__(self, this: SessionTime) -> Any: ...


class _ProtocolFromSessString33(Protocol):
    def __call__(self, this: SessionTime, sess: str) -> Any: ...


class _ProtocolFromSessString34(Protocol):
    def __call__(self, this: SessionTime, sess: str, refTimezone: str) -> Any: ...


class _ProtocolToString35(Protocol):
    def __call__(self, this: SessionTime) -> Any: ...


class _ProtocolGetSecInDay(Protocol):
    def __call__(self, this: SessionTime) -> Any: ...


class _ProtocolGetMsInDay(Protocol):
    def __call__(self, this: SessionTime) -> Any: ...


class _ProtocolInit38(Protocol):
    def __call__(self, this: SessionTimeRange, startTime: SessionTime = na, endTime: SessionTime = na) -> Any: ...


class _ProtocolInit39(Protocol):
    def __call__(self, this: SessionTimeRange, startTimeHour: int, startTimeMinute: int, endTimeHour: int, endTimeMinute: int, refTimezone: str) -> Any: ...


class _ProtocolToSessString40(Protocol):
    def __call__(self, this: SessionTimeRange) -> Any: ...


class _ProtocolFromSessString41(Protocol):
    def __call__(self, this: SessionTimeRange, sess: str) -> Any: ...


class _ProtocolFromSessString42(Protocol):
    def __call__(self, this: SessionTimeRange, sess: str, refTimezone: str) -> Any: ...


class _ProtocolToString43(Protocol):
    def __call__(self, this: SessionTimeRange) -> Any: ...


class _ProtocolGetSizeInSecs44(Protocol):
    def __call__(self, this: SessionTimeRange) -> Any: ...


class _ProtocolGetSizeInBars45(Protocol):
    def __call__(self, this: SessionTimeRange) -> Any: ...


class _ProtocolInit46(Protocol):
    def __call__(self, this: Session, days__000001af__: SessionDays, timeRanges__000001af__: list[SessionTimeRange]) -> Any: ...


class _ProtocolToSessString47(Protocol):
    def __call__(self, this: Session) -> Any: ...


class _ProtocolToSessStrings(Protocol):
    def __call__(self, this: Session) -> Any: ...


class _ProtocolFromSessString49(Protocol):
    def __call__(self, this: Session, sess: str) -> Any: ...


class _ProtocolFromSessString50(Protocol):
    def __call__(self, this: Session, sess: str, refTimezone: str) -> Any: ...


class _ProtocolToString51(Protocol):
    def __call__(self, this: Session) -> Any: ...


class _ProtocolIsDayIncluded(Protocol):
    def __call__(self, this: SessionDays, day: int) -> Any: ...


class _ProtocolIsBarIncluded53(Protocol):
    def __call__(self, this: Session, offset_forward: int = 1) -> Any: ...


class _ProtocolInit54(Protocol):
    def __call__(self, this: SessionView, days__00000227__: SessionDays, timeRanges__00000227__: list[SessionTimeRange], names__00000227__: list[str], colors__00000227__: list[Color]) -> Any: ...


class _ProtocolDrawBoxes(Protocol):
    def __call__(self, this: SessionView) -> Any: ...


class _ProtocolDrawCandles(Protocol):
    def __call__(self, this: SessionView) -> Any: ...


class _ProtocolDrawBars(Protocol):
    def __call__(self, this: SessionView) -> Any: ...


class _ProtocolDraw(Protocol):
    def __call__(self, this: SessionView, viewMode: ViewMode = ViewMode.Boxes) -> Any: ...


to_string: _ProtocolToString = Exported()
nameOfDay: _ProtocolNameofday = Exported()
today: _ProtocolToday = Exported()
nthDayAfter: _ProtocolNthdayafter = Exported()
nextDayAfter: _ProtocolNextdayafter = Exported()
nthDayBefore: _ProtocolNthdaybefore = Exported()
prevDayBefore: _ProtocolPrevdaybefore = Exported()
tomorrow: _ProtocolTomorrow = Exported()
normalize: _ProtocolNormalize = Exported()
normalizeHour: _ProtocolNormalizehour = Exported()
normalizeMinute: _ProtocolNormalizeminute = Exported()
monthInDays: _ProtocolMonthindays = Exported()
monthInMilliseconds: _ProtocolMonthinmilliseconds = Exported()
monthInMilliseconds: _ProtocolMonthinmilliseconds13 = Exported()
barInMilliseconds: _ProtocolBarinmilliseconds = Exported()
init: _ProtocolInit = Exported()
init: _ProtocolInit16 = Exported()
to_string: _ProtocolToString17 = Exported()
get_size_in_secs: _ProtocolGetSizeInSecs = Exported()
get_size_in_bars: _ProtocolGetSizeInBars = Exported()
is_bar_included: _ProtocolIsBarIncluded = Exported()
init: _ProtocolInit21 = Exported()
to_sess_string: _ProtocolToSessString = Exported()
from_sess_string: _ProtocolFromSessString = Exported()
to_string: _ProtocolToString24 = Exported()
nth_day_after: _ProtocolNthDayAfter = Exported()
nth_day_before: _ProtocolNthDayBefore = Exported()
next_day: _ProtocolNextDay = Exported()
previous_day: _ProtocolPreviousDay = Exported()
init: _ProtocolInit29 = Exported()
init: _ProtocolInit30 = Exported()
init: _ProtocolInit31 = Exported()
to_sess_string: _ProtocolToSessString32 = Exported()
from_sess_string: _ProtocolFromSessString33 = Exported()
from_sess_string: _ProtocolFromSessString34 = Exported()
to_string: _ProtocolToString35 = Exported()
get_sec_in_day: _ProtocolGetSecInDay = Exported()
get_ms_in_day: _ProtocolGetMsInDay = Exported()
init: _ProtocolInit38 = Exported()
init: _ProtocolInit39 = Exported()
to_sess_string: _ProtocolToSessString40 = Exported()
from_sess_string: _ProtocolFromSessString41 = Exported()
from_sess_string: _ProtocolFromSessString42 = Exported()
to_string: _ProtocolToString43 = Exported()
get_size_in_secs: _ProtocolGetSizeInSecs44 = Exported()
get_size_in_bars: _ProtocolGetSizeInBars45 = Exported()
init: _ProtocolInit46 = Exported()
to_sess_string: _ProtocolToSessString47 = Exported()
to_sess_strings: _ProtocolToSessStrings = Exported()
from_sess_string: _ProtocolFromSessString49 = Exported()
from_sess_string: _ProtocolFromSessString50 = Exported()
to_string: _ProtocolToString51 = Exported()
is_day_included: _ProtocolIsDayIncluded = Exported()
is_bar_included: _ProtocolIsBarIncluded53 = Exported()
init: _ProtocolInit54 = Exported()
draw_boxes: _ProtocolDrawBoxes = Exported()
draw_candles: _ProtocolDrawCandles = Exported()
draw_bars: _ProtocolDrawBars = Exported()
draw: _ProtocolDraw = Exported()


MS_PER_DAY: int = 86400000
GENERAL_GROUP_NAME: str = 'General'
WINDOW_GROUP_NAME: str = 'Window'
SESSION_GROUP_NAME: str = 'Session'
TEST_GROUP_NAME: str = 'Test'


@script.library(title='chrono_utils')
def main(
    offset_forward=input.int(defval=1, title='Offset Bars Forward', minval=0, step=1, tooltip='The number of future bar to predict from the current bar. The higher the offset number is, the more error prone the prediction due to holydays and data anomalies.', group=GENERAL_GROUP_NAME, display=display.data_window),
    referenceTimezone__input=input.enum(defval=Timezone.Exchange, title='Timezones Ref->Chart', inline='Timezone', group=WINDOW_GROUP_NAME, display=display.data_window),
    fromEnabled=input.bool(defval=False, title='From      ', inline='From Date', group=WINDOW_GROUP_NAME, display=display.data_window),
    toEnabled=input.bool(defval=False, title='To       ', inline='To Date', group=WINDOW_GROUP_NAME, display=display.data_window),
    __input_4__=input.time(defval=timestamp('01 Jan 2024 00:00'), title='', inline='From Date', group=WINDOW_GROUP_NAME, display=display.data_window),
    __input_5__=input.time(defval=timestamp('01 Jan 2025 00:00'), title='', inline='To Date', group=WINDOW_GROUP_NAME, display=display.data_window),
    __input_6__=input.enum(defval=Timezone.Exchange, title='->', tooltip='The Timezone Ref is the reference timezone that is used for the "From" and "To" datetime window settings. The Timezone Chart is the timezone to convert into. WARNING! The chart timezone setting should always match with the actual chart timezone on the bottom right corner of your chart.', inline='Timezone', group=WINDOW_GROUP_NAME, display=display.data_window),
    daysEnabled=input.bool(defval=True, title='Session Days', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_8__=input.bool(defval=False, title='Sun', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_9__=input.bool(defval=True, title='Mon', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_10__=input.bool(defval=True, title='Tue', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_11__=input.bool(defval=True, title='Wed', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_12__=input.bool(defval=True, title='Thu', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_13__=input.bool(defval=True, title='Fri', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_14__=input.bool(defval=False, title='Sat', inline='Session Days', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionEnabled1=input.bool(defval=True, title='', inline='Session 1', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionName1=input.string(defval='Tokyo', title='', inline='Session 1', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionColor1=input.color(defval=color.yellow, title='', inline='Session 1', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_18__=input.session(defval='0000-0900', title='   ', inline='Session Range 1', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_19__=input.enum(defval=Timezone.Utc, title='', inline='Session Range 1', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionEnabled2=input.bool(defval=True, title='', inline='Session 2', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionName2=input.string(defval='London', title='', inline='Session 2', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionColor2=input.color(defval=color.blue, title='', inline='Session 2', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_23__=input.session(defval='0800-1600', title='   ', inline='Session Range 2', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_24__=input.enum(Timezone.Utc, title='', inline='Session Range 2', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionEnabled3=input.bool(defval=True, title='', inline='Session 3', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionName3=input.string(defval='New York', title='', inline='Session 3', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionColor3=input.color(defval=color.orange, title='', inline='Session 3', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_28__=input.session(defval='1300-2200', title='   ', inline='Session Range 3', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_29__=input.enum(defval=Timezone.Utc, title='', inline='Session Range 3', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionEnabled4=input.bool(defval=True, title='', inline='Session 4', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionName4=input.string(defval='Sydney', title='', inline='Session 4', group=SESSION_GROUP_NAME, display=display.data_window),
    sessionColor4=input.color(defval=color.red, title='', inline='Session 4', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_33__=input.session(defval='2000-0500', title='   ', inline='Session Range 4', group=SESSION_GROUP_NAME, display=display.data_window),
    __input_34__=input.enum(defval=Timezone.Utc, title='', inline='Session Range 4', group=SESSION_GROUP_NAME, display=display.data_window),
    viewMode=input.enum(defval=ViewMode.Boxes, title='View Mode', tooltip='The method to visualize the session using either boxes, candles or bars', group='Visual'),
    anomalyDetectionEnabled=input.bool(defval=True, title='Data anomaly detection', tooltip='Test if the session prediction for the current bar is correct. If not log an error.', group=TEST_GROUP_NAME),
    debugEnabled=input.bool(defval=False, title='Debug', tooltip='Add additional drawings and logs for debug purposes.', group=TEST_GROUP_NAME)
):
    @export
    @overload
    @method
    def to_string(timezone: Timezone):
        __block_result__ = na
        __switch__ = timezone
        if __switch__ == Timezone.Utc:
            __block_result__ = "Etc/UTC"
        elif __switch__ == Timezone.Exchange:
            __block_result__ = syminfo.timezone
        elif __switch__ == Timezone.Honolulu:
            __block_result__ = "Pacific/Honolulu"
        elif __switch__ == Timezone.Anchorage:
            __block_result__ = "America/Anchorage"
        elif __switch__ == Timezone.Juneau:
            __block_result__ = "America/Juneau"
        elif __switch__ == Timezone.Los_Angeles:
            __block_result__ = "America/Los_Angeles"
        elif __switch__ == Timezone.Vancouver:
            __block_result__ = "America/Vancouver"
        elif __switch__ == Timezone.Denver:
            __block_result__ = "America/Denver"
        elif __switch__ == Timezone.Phoenix:
            __block_result__ = "America/Phoenix"
        elif __switch__ == Timezone.Chicago:
            __block_result__ = "America/Chicago"
        elif __switch__ == Timezone.Mexico_City:
            __block_result__ = "America/Mexico_City"
        elif __switch__ == Timezone.San_Salvador:
            __block_result__ = "America/El_Salvador"
        elif __switch__ == Timezone.Bogota:
            __block_result__ = "America/Bogota"
        elif __switch__ == Timezone.Lima:
            __block_result__ = "America/Lima"
        elif __switch__ == Timezone.New_York:
            __block_result__ = "America/New_York"
        elif __switch__ == Timezone.Toronto:
            __block_result__ = "America/Toronto"
        elif __switch__ == Timezone.Caracas:
            __block_result__ = "America/Caracas"
        elif __switch__ == Timezone.Santiago:
            __block_result__ = "America/Santiago"
        elif __switch__ == Timezone.Buenos_Aires:
            __block_result__ = "America/Argentina/Buenos_Aires"
        elif __switch__ == Timezone.Sao_Palo:
            __block_result__ = "America/Sao_Paulo"
        elif __switch__ == Timezone.Azores:
            __block_result__ = "Atlantic/Azores"
        elif __switch__ == Timezone.Dublin:
            __block_result__ = "Europe/Dublin"
        elif __switch__ == Timezone.Lisbon:
            __block_result__ = "Europe/Lisbon"
        elif __switch__ == Timezone.London:
            __block_result__ = "Europe/London"
        elif __switch__ == Timezone.Reykjavik:
            __block_result__ = "Atlantic/Reykjavik"
        elif __switch__ == Timezone.Amsterdam:
            __block_result__ = "Europe/Amsterdam"
        elif __switch__ == Timezone.Belgrade:
            __block_result__ = "Europe/Belgrade"
        elif __switch__ == Timezone.Berlin:
            __block_result__ = "Europe/Berlin"
        elif __switch__ == Timezone.Bratislava:
            __block_result__ = "Europe/Bratislava"
        elif __switch__ == Timezone.Brussels:
            __block_result__ = "Europe/Brussels"
        elif __switch__ == Timezone.Budapest:
            __block_result__ = "Europe/Budapest"
        elif __switch__ == Timezone.Casablanca:
            __block_result__ = "Africa/Casablanca"
        elif __switch__ == Timezone.Copenhagen:
            __block_result__ = "Europe/Copenhagen"
        elif __switch__ == Timezone.Lagos:
            __block_result__ = "Africa/Lagos"
        elif __switch__ == Timezone.Luxembourg:
            __block_result__ = "Europe/Luxembourg"
        elif __switch__ == Timezone.Madrid:
            __block_result__ = "Europe/Madrid"
        elif __switch__ == Timezone.Malta:
            __block_result__ = "Europe/Malta"
        elif __switch__ == Timezone.Oslo:
            __block_result__ = "Europe/Oslo"
        elif __switch__ == Timezone.Paris:
            __block_result__ = "Europe/Paris"
        elif __switch__ == Timezone.Prague:
            __block_result__ = "Europe/Prague"
        elif __switch__ == Timezone.Rome:
            __block_result__ = "Europe/Rome"
        elif __switch__ == Timezone.Stockholm:
            __block_result__ = "Europe/Stockholm"
        elif __switch__ == Timezone.Tunis:
            __block_result__ = "Africa/Tunis"
        elif __switch__ == Timezone.Vienna:
            __block_result__ = "Europe/Vienna"
        elif __switch__ == Timezone.Warsaw:
            __block_result__ = "Europe/Warsaw"
        elif __switch__ == Timezone.Zurich:
            __block_result__ = "Europe/Zurich"
        elif __switch__ == Timezone.Athens:
            __block_result__ = "Europe/Athens"
        elif __switch__ == Timezone.Bucharest:
            __block_result__ = "Europe/Bucharest"
        elif __switch__ == Timezone.Cairo:
            __block_result__ = "Africa/Cairo"
        elif __switch__ == Timezone.Helsinki:
            __block_result__ = "Europe/Helsinki"
        elif __switch__ == Timezone.Jerusalem:
            __block_result__ = "Asia/Jerusalem"
        elif __switch__ == Timezone.Johannesburg:
            __block_result__ = "Africa/Johannesburg"
        elif __switch__ == Timezone.Nicosia:
            __block_result__ = "Asia/Nicosia"
        elif __switch__ == Timezone.Riga:
            __block_result__ = "Europe/Riga"
        elif __switch__ == Timezone.Tallinn:
            __block_result__ = "Europe/Tallinn"
        elif __switch__ == Timezone.Vilnius:
            __block_result__ = "Europe/Vilnius"
        elif __switch__ == Timezone.Bahrain:
            __block_result__ = "Asia/Bahrain"
        elif __switch__ == Timezone.Istanbul:
            __block_result__ = "Europe/Istanbul"
        elif __switch__ == Timezone.Kuwait:
            __block_result__ = "Asia/Kuwait"
        elif __switch__ == Timezone.Moscow:
            __block_result__ = "Europe/Moscow"
        elif __switch__ == Timezone.Nairobi:
            __block_result__ = "Africa/Nairobi"
        elif __switch__ == Timezone.Qatar:
            __block_result__ = "Asia/Qatar"
        elif __switch__ == Timezone.Riyadh:
            __block_result__ = "Asia/Riyadh"
        elif __switch__ == Timezone.Tehran:
            __block_result__ = "Asia/Tehran"
        elif __switch__ == Timezone.Dubai:
            __block_result__ = "Asia/Dubai"
        elif __switch__ == Timezone.Muscat:
            __block_result__ = "Asia/Muscat"
        elif __switch__ == Timezone.Kabul:
            __block_result__ = "Asia/Kabul"
        elif __switch__ == Timezone.Ashgabat:
            __block_result__ = "Asia/Ashgabat"
        elif __switch__ == Timezone.Astana:
            __block_result__ = "Asia/Almaty"
        elif __switch__ == Timezone.Karachi:
            __block_result__ = "Asia/Karachi"
        elif __switch__ == Timezone.Colombo:
            __block_result__ = "Asia/Colombo"
        elif __switch__ == Timezone.Kolkata:
            __block_result__ = "Asia/Kolkata"
        elif __switch__ == Timezone.Kathmandu:
            __block_result__ = "Asia/Kathmandu"
        elif __switch__ == Timezone.Dhaka:
            __block_result__ = "Asia/Dhaka"
        elif __switch__ == Timezone.Yangon:
            __block_result__ = "Asia/Yangon"
        elif __switch__ == Timezone.Bangkok:
            __block_result__ = "Asia/Bangkok"
        elif __switch__ == Timezone.Ho_Chi_Minh:
            __block_result__ = "Asia/Ho_Chi_Minh"
        elif __switch__ == Timezone.Jakarta:
            __block_result__ = "Asia/Jakarta"
        elif __switch__ == Timezone.Chongqing:
            __block_result__ = "Asia/Chongqing"
        elif __switch__ == Timezone.Hong_Kong:
            __block_result__ = "Asia/Hong_Kong"
        elif __switch__ == Timezone.Kuala_Lumpur:
            __block_result__ = "Asia/Kuala_Lumpur"
        elif __switch__ == Timezone.Manila:
            __block_result__ = "Asia/Manila"
        elif __switch__ == Timezone.Perth:
            __block_result__ = "Australia/Perth"
        elif __switch__ == Timezone.Shanghai:
            __block_result__ = "Asia/Shanghai"
        elif __switch__ == Timezone.Singapore:
            __block_result__ = "Asia/Singapore"
        elif __switch__ == Timezone.Taipei:
            __block_result__ = "Asia/Taipei"
        elif __switch__ == Timezone.Seoul:
            __block_result__ = "Asia/Seoul"
        elif __switch__ == Timezone.Tokyo:
            __block_result__ = "Asia/Tokyo"
        elif __switch__ == Timezone.Adelaide:
            __block_result__ = "Australia/Adelaide"
        elif __switch__ == Timezone.Brisbane:
            __block_result__ = "Australia/Brisbane"
        elif __switch__ == Timezone.Sydney:
            __block_result__ = "Australia/Sydney"
        elif __switch__ == Timezone.Norfolk_Island:
            __block_result__ = "Pacific/Norfolk"
        elif __switch__ == Timezone.New_Zealand:
            __block_result__ = "Pacific/Auckland"
        elif __switch__ == Timezone.Chatham_Islands:
            __block_result__ = "Pacific/Chatham"
        elif __switch__ == Timezone.Tokelau:
            __block_result__ = "Pacific/Fakaofo"
        return __block_result__

    @export
    def nameOfDay(day: int):
        __block_result_1__ = na
        __switch__ = day
        if __switch__ == dayofweek.sunday:
            __block_result_1__ = 'Sun'
        elif __switch__ == dayofweek.monday:
            __block_result_1__ = 'Mon'
        elif __switch__ == dayofweek.tuesday:
            __block_result_1__ = 'Tue'
        elif __switch__ == dayofweek.wednesday:
            __block_result_1__ = 'Wed'
        elif __switch__ == dayofweek.thursday:
            __block_result_1__ = 'Thu'
        elif __switch__ == dayofweek.friday:
            __block_result_1__ = 'Fri'
        elif __switch__ == dayofweek.saturday:
            __block_result_1__ = 'Sat'
        else:
            __block_result_1__ = 'NaN'
        return __block_result_1__

    @export
    def today():
        return dayofweek

    @export
    def nthDayAfter(day: int, n: int):
        return (day - 1 + n) % 7 + 1

    @export
    def nextDayAfter(day: int):
        return nthDayAfter(day, 1)

    @export
    def nthDayBefore(day: int, n: int = 1):
        return (day - 1 + (7 - n)) % 7 + 1

    @export
    def prevDayBefore(day: int):
        return nthDayBefore(day, 1)

    @export
    def tomorrow():
        return nextDayAfter(today())

    @export
    def normalize(num: int, min: int, max: int):
        normalizedNum: int = num
        while normalizedNum < min:
            normalizedNum = normalizedNum + max
        while normalizedNum > max:
            normalizedNum = normalizedNum - max
        return normalizedNum

    @export
    def normalizeHour(hourInDay: int):
        return normalize(hourInDay, 0, 24)

    @export
    def normalizeMinute(minuteInHour: int):
        return normalize(minuteInHour, 0, 60)

    @export
    def monthInDays(mon: int, yer: int, rolloverMonths: bool = False):
        __block_result_2__ = na
        if rolloverMonths:
            normalizedMonth: int = mon
            while normalizedMonth <= 0:
                normalizedMonth += 12
            __block_result_2__ = (normalizedMonth - 1) % 12 + 1
        else:
            __block_result_2__ = math.min(math.max(mon, 1), 12)
        m: int = __block_result_2__

        isLeapYear: bool = (yer + math.floor(mon / 12)) % 4 == 0
        extraDays: int = (m + math.floor(m / 8)) % 2 + 2 % m + 2 * math.floor(1 / m)
        return 28 + (1 if m == 2 and isLeapYear else 0) + extraDays


    @export
    @overload
    def monthInMilliseconds(mon: int, yer: int, rolloverMonths: bool = True):
        return monthInDays(mon, yer, rolloverMonths) * MS_PER_DAY

    @export
    @overload
    def monthInMilliseconds(mon: int):
        __block_result_3__ = na
        __switch__ = mon
        if __switch__ == 2:
            __block_result_3__ = 28
        elif __switch__ == 4:
            __block_result_3__ = 30
        elif __switch__ == 6:
            __block_result_3__ = 30
        elif __switch__ == 9:
            __block_result_3__ = 30
        elif __switch__ == 11:
            __block_result_3__ = 30
        else:
            __block_result_3__ = 31
        daysInMonth: int = __block_result_3__
        return daysInMonth * MS_PER_DAY

    @export
    def barInMilliseconds():
        __block_result_4__ = na
        if timeframe.ismonthly:
            __block_result_4__ = monthInMilliseconds(month, year, False)
        else:
            __block_result_4__ = 1000 * timeframe.in_seconds()
        return __block_result_4__


    @overload
    @method
    def to_string(this: Bar):
        return string.format('[open = {0}, close = {1}]', string.format_time(this.openUnixTime, 'HH:mm d/M/yyyy (z)'), string.format_time(this.closeUnixTime, 'HH:mm d/M/yyyy (z)'))

    @method
    def eq(this: Bar, other: Bar):
        return this.openUnixTime == other.openUnixTime and this.closeUnixTime == other.closeUnixTime

    def getCurrentBar():
        return Bar(time, time_close)

    def getNextBar(offset_forward: int = 1):
        openUnixTime: int = time(timeframe.period, -1 * offset_forward)
        return Bar(openUnixTime, time_close(timeframe.period, -1 * offset_forward))


    @export
    @overload
    @method
    def init(this: DateTimeWindow, fromDateTime: int, toDateTime: int):
        this.fromDateTime = na if na(fromDateTime) else timestamp(year(fromDateTime), month(fromDateTime), dayofmonth(fromDateTime), hour(fromDateTime), minute(fromDateTime), second(fromDateTime))
        this.toDateTime = na if na(toDateTime) else timestamp(year(toDateTime), month(toDateTime), dayofmonth(toDateTime), hour(toDateTime), minute(toDateTime), second(toDateTime))
        return this

    @export
    @overload
    @method
    def init(this: DateTimeWindow, refTimezone: str, chTimezone: str, fromDateTime: int, toDateTime: int):
        this.fromDateTime = na if na(fromDateTime) else timestamp(refTimezone, year(fromDateTime, chTimezone), month(fromDateTime, chTimezone), dayofmonth(fromDateTime, chTimezone), hour(fromDateTime, chTimezone), minute(fromDateTime, chTimezone), second(fromDateTime, chTimezone))
        this.toDateTime = na if na(toDateTime) else timestamp(refTimezone, year(toDateTime, chTimezone), month(toDateTime, chTimezone), dayofmonth(toDateTime, chTimezone), hour(toDateTime, chTimezone), minute(toDateTime, chTimezone), second(toDateTime, chTimezone))
        return this

    @export
    @overload
    @method
    def to_string(this: DateTimeWindow):
        return string.format('[{0} - {1}]', string.format_time(0 if na(this.fromDateTime) else this.fromDateTime, 'HH:mm d/M/yyyy (z)'), string.format_time(time_close if na(this.toDateTime) else this.toDateTime, 'HH:mm d/M/yyyy (z)'))

    @export
    @overload
    @method
    def get_size_in_secs(this: DateTimeWindow):
        return math.abs((0 if na(this.fromDateTime) else this.fromDateTime) - (time_close if na(this.toDateTime) else this.toDateTime)) / 1000

    @export
    @overload
    @method
    def get_size_in_bars(this: DateTimeWindow):
        return math.floor(get_size_in_secs(this) / timeframe.in_seconds())

    @export
    @overload
    @method
    def is_bar_included(this: DateTimeWindow, offset_forward: int = 1):
        nextBar: Bar = getNextBar(offset_forward)
        return (True if na(this.fromDateTime) else nextBar.openUnixTime >= this.fromDateTime) and (True if na(this.toDateTime) else nextBar.closeUnixTime <= this.toDateTime)


    @export
    @overload
    @method
    def init(this: SessionDays, sun: bool = True, mon: bool = True, tue: bool = True, wed: bool = True, thu: bool = True, fri: bool = True, sat: bool = True):
        this.days = map.new()
        map.put(this.days, dayofweek.sunday, sun)
        map.put(this.days, dayofweek.monday, mon)
        map.put(this.days, dayofweek.tuesday, tue)
        map.put(this.days, dayofweek.wednesday, wed)
        map.put(this.days, dayofweek.thursday, thu)
        map.put(this.days, dayofweek.friday, fri)
        map.put(this.days, dayofweek.saturday, sat)
        return this

    @export
    @overload
    @method
    def to_sess_string(this: SessionDays):
        sess: str = ''
        for day, isSession in this.days.items():
            if isSession:
                sess += string.tostring(day)
        return sess

    @export
    @overload
    @method
    def from_sess_string(this: SessionDays, sess: str):
        if na(string.tonumber(sess)):
            runtime.error(string.format('Invalid days session string {0}', sess))
        this.days = map.new()
        for i in pine_range(1, 7):
            map.put(this.days, i, string.contains(sess, string.tostring(i)))
        return this

    @export
    @overload
    @method
    def to_string(this: SessionDays):
        s: str = ''
        comma: str = ''
        for day, isSession in this.days.items():
            if isSession:
                s += comma + nameOfDay(day)
                comma = ','
        return '[' + string.substring(s, 0, string.length(s)) + ']'

    @export
    @method
    def nth_day_after(this: SessionDays, day: int, n: int):
        nthSessionDay: int = day
        count: int = n
        i: int = 1
        while count > 0 and i <= 7:
            nthDay: int = nthDayAfter(day, i)
            if map.get(this.days, nthDay):
                count -= 1
                nthSessionDay = nthDay
            i += 1
        return nthSessionDay

    @export
    @method
    def nth_day_before(this: SessionDays, day: int, n: int):
        nthSessionDay: int = day
        count: int = n
        i: int = 1
        while count > 0 and i <= 7:
            nthDay: int = nthDayBefore(day, i)
            if map.get(this.days, nthDay):
                count -= 1
                nthSessionDay = nthDay
            i += 1
        return nthSessionDay

    @export
    @method
    def next_day(this: SessionDays):
        return nth_day_after(this, today(), 1)

    @export
    @method
    def previous_day(this: SessionDays):
        return nth_day_before(this, today(), 1)


    @export
    @overload
    @method
    def init(this: SessionTime, unixTime: int):
        this.hourInDay = 0 if na(unixTime) else hour(unixTime)
        this.minuteInHour = 0 if na(unixTime) else minute(unixTime)
        this.minuteInDay = 60 * this.hourInDay + this.minuteInHour
        return this

    @export
    @overload
    @method
    def init(this: SessionTime, hourInDay: int, minuteInHour: int):
        if hourInDay > 24 or minuteInHour > 60 or hourInDay < 0 or (minuteInHour < 0):
            runtime.error('Invalid hour or day values passed: ' + string.tostring(hourInDay) + ', ' + string.tostring(minuteInHour))
        this.hourInDay = 0 if na(hourInDay) else hourInDay
        this.minuteInHour = 0 if na(minuteInHour) else minuteInHour
        this.minuteInDay = 60 * hourInDay + minuteInHour
        return this

    @export
    @overload
    @method
    def init(this: SessionTime, hourInDay: int, minuteInHour: int, refTimezone: str):
        return init(this, normalizeHour(hourInDay + hour - hour(time, refTimezone)), normalizeMinute(minuteInHour + minute - minute(time, refTimezone)))

    @export
    @overload
    @method
    def to_sess_string(this: SessionTime):
        return string.format('{0, number,00}{1, number,00}', this.hourInDay, this.minuteInHour)

    @export
    @overload
    @method
    def from_sess_string(this: SessionTime, sess: str):
        if string.length(sess) != 4:
            runtime.error(string.format('Invalid time session string {0}', sess))
        return init(this, cast_int(string.tonumber(string.substring(sess, 0, 2))), cast_int(string.tonumber(string.substring(sess, 2))))

    @export
    @overload
    @method
    def from_sess_string(this: SessionTime, sess: str, refTimezone: str):
        if string.length(sess) != 4:
            runtime.error(string.format('Invalid time session string {0}', sess))
        return init(this, cast_int(string.tonumber(string.substring(sess, 0, 2))), cast_int(string.tonumber(string.substring(sess, 2))), refTimezone)

    @export
    @overload
    @method
    def to_string(this: SessionTime):
        return string.format('{0, number,00}:{1, number,00}', this.hourInDay, this.minuteInHour)

    @export
    @method
    def get_sec_in_day(this: SessionTime):
        return 60 * this.minuteInDay

    @export
    @method
    def get_ms_in_day(this: SessionTime):
        return 1000 * get_sec_in_day(this)

    @method
    def get_open_time(this: Bar):
        return init(SessionTime(), this.openUnixTime)

    @method
    def get_close_time(this: Bar):
        closeBarTime: SessionTime = init(SessionTime(), this.closeUnixTime)
        if closeBarTime.minuteInDay == 0:
            closeBarTime = init(SessionTime(), 24, 0)
        return closeBarTime


    @export
    @overload
    @method
    def init(this: SessionTimeRange, startTime: SessionTime = na, endTime: SessionTime = na):
        this.startTime = init(SessionTime(), 0, 0) if na(startTime) else startTime
        this.endTime = init(SessionTime(), 24, 0) if na(endTime) else endTime
        this.isOvernight = this.startTime.minuteInDay >= this.endTime.minuteInDay if timeframe.isintraday else False
        return this

    @export
    @overload
    @method
    def init(this: SessionTimeRange, startTimeHour: int, startTimeMinute: int, endTimeHour: int, endTimeMinute: int, refTimezone: str):
        return init(this, init(SessionTime(), 0, 0, refTimezone) if na(startTimeHour) or na(startTimeMinute) else init(SessionTime(), startTimeHour, startTimeMinute, refTimezone), init(SessionTime(), 24, 0, refTimezone) if na(endTimeHour) or na(endTimeMinute) else init(SessionTime(), endTimeHour, endTimeMinute, refTimezone))

    @export
    @overload
    @method
    def to_sess_string(this: SessionTimeRange):
        return string.format('{0}-{1}', to_sess_string(init(SessionTime(), 0, 0) if na(this.startTime) else this.startTime), to_sess_string(init(SessionTime(), 24, 0) if na(this.endTime) else this.endTime))

    @export
    @overload
    @method
    def from_sess_string(this: SessionTimeRange, sess: str):
        sessParts: list[str] = string.split(sess, '-')
        if array.size(sessParts) != 2:
            runtime.error(string.format('Invalid time range session string {0}', sess))
        return init(this, from_sess_string(SessionTime(), array.get(sessParts, 0)), from_sess_string(SessionTime(), array.get(sessParts, 1)))

    @export
    @overload
    @method
    def from_sess_string(this: SessionTimeRange, sess: str, refTimezone: str):
        sessParts: list[str] = string.split(sess, '-')
        if array.size(sessParts) != 2:
            runtime.error(string.format('Invalid time range session string {0}', sess))
        return init(this, from_sess_string(SessionTime(), array.get(sessParts, 0), refTimezone), from_sess_string(SessionTime(), array.get(sessParts, 1), refTimezone))

    @export
    @overload
    @method
    def to_string(this: SessionTimeRange):
        return string.format('[{0} - {1}]{2}', to_string(init(SessionTime(), 0, 0) if na(this.startTime) else this.startTime), to_string(init(SessionTime(), 24, 0) if na(this.endTime) else this.endTime), ' (over)' if this.isOvernight else '')

    @export
    @overload
    @method
    def get_size_in_secs(this: SessionTimeRange):
        secs: int = get_sec_in_day(init(SessionTime(), 24, 0) if na(this.endTime) else this.endTime) - get_sec_in_day(init(SessionTime(), 0, 0) if na(this.startTime) else this.startTime)
        if secs <= 0:
            secs += 86400
        return secs

    @export
    @overload
    @method
    def get_size_in_bars(this: SessionTimeRange):
        return math.floor(get_size_in_secs(this) / timeframe.in_seconds())

    @overload
    @method
    def is_bar_included(this: SessionTimeRange, bar: Bar):
        barOpenTime: SessionTime = get_open_time(bar)
        barCloseTime: SessionTime = get_close_time(bar)
        return barCloseTime.minuteInDay <= this.endTime.minuteInDay or this.startTime.minuteInDay <= barOpenTime.minuteInDay if this.isOvernight else this.startTime.minuteInDay <= barOpenTime.minuteInDay and barCloseTime.minuteInDay <= this.endTime.minuteInDay

    @method
    def get_time_range(this: Bar):
        return init(SessionTimeRange(), get_open_time(this), get_close_time(this))

    @method
    def get_trading_day(this: SessionTimeRange, bar: Bar):
        barOpenTime: SessionTime = get_open_time(bar)
        return nextDayAfter(dayofweek(bar.openUnixTime)) if (barOpenTime.minuteInDay >= this.startTime.minuteInDay if this.isOvernight else False) else dayofweek(bar.openUnixTime)


    @export
    @overload
    @method
    def init(this: Session, days__000001af__: SessionDays, timeRanges__000001af__: list[SessionTimeRange]):
        this.days = init(SessionDays()) if na(days__000001af__) else days__000001af__
        if na(timeRanges__000001af__):
            this.timeRanges = array.from_items(init(SessionTimeRange()))
        else:
            for i in pine_range(array.size(timeRanges__000001af__) - 1, 0):
                if na(array.get(timeRanges__000001af__, i)):
                    array.remove(timeRanges__000001af__, i)

            if array.size(timeRanges__000001af__) == 0:
                array.push(timeRanges__000001af__, init(SessionTimeRange()))
            this.timeRanges = timeRanges__000001af__
        return this

    @export
    @overload
    @method
    def to_sess_string(this: Session):
        daysSessStr: str = to_sess_string(init(SessionDays()) if na(this.days) else this.days)
        delim: str = '' if daysSessStr == '' else ':'
        sessTimeRanges: str = ''
        comma: str = ''
        for timeRange in this.timeRanges:
            sessTimeRanges += comma + to_sess_string(timeRange)
            comma = ','
        return string.format('{0}{1}{2}', sessTimeRanges, delim, daysSessStr)

    @export
    @method
    def to_sess_strings(this: Session):
        daysSessStr: str = to_sess_string(init(SessionDays()) if na(this.days) else this.days)
        delim: str = '' if daysSessStr == '' else ':'
        sessTimeRanges: list[str] = array.new_string(array.size(this.timeRanges), '')
        for i, timeRange in enumerate(this.timeRanges):
            array.set(sessTimeRanges, i, string.format('{0}{1}{2}', to_sess_string(timeRange), delim, daysSessStr))
        return sessTimeRanges

    @export
    @overload
    @method
    def from_sess_string(this: Session, sess: str):
        sessParts: list[str] = string.split(sess, ':')
        sessTimeRangeParts: list[str] = string.split(array.get(sessParts, 0), ',')
        timeRanges__000001d3__: list[SessionTimeRange] = array.new(0, NA(SessionTimeRange))
        for sessTimeRange in sessTimeRangeParts:
            array.push(timeRanges__000001d3__, from_sess_string(SessionTimeRange(), sessTimeRange))
        this.timeRanges = timeRanges__000001d3__
        if array.size(sessParts) > 1:
            this.days = from_sess_string(SessionDays(), array.get(sessParts, 1))
        else:
            this.days = init(SessionDays())
        return this

    @export
    @overload
    @method
    def from_sess_string(this: Session, sess: str, refTimezone: str):
        sessParts: list[str] = string.split(sess, ':')
        sessTimeRangeParts: list[str] = string.split(array.get(sessParts, 0), ',')
        timeRanges__000001e4__: list[SessionTimeRange] = array.new(0, NA(SessionTimeRange))
        for sessTimeRange in sessTimeRangeParts:
            array.push(timeRanges__000001e4__, from_sess_string(SessionTimeRange(), sessTimeRange, refTimezone))
        this.timeRanges = timeRanges__000001e4__
        if array.size(sessParts) > 1:
            this.days = from_sess_string(SessionDays(), array.get(sessParts, 1))
        else:
            this.days = init(SessionDays())
        return this

    @export
    @overload
    @method
    def to_string(this: Session):
        sessTimeRanges: str = ''
        comma: str = ''
        for timeRange in this.timeRanges:
            sessTimeRanges += comma + to_string(timeRange)
            comma = ','
        return string.format('{0} -> {1}', to_string(init(SessionDays()) if na(this.days) else this.days), sessTimeRanges)

    @export
    @method
    def is_day_included(this: SessionDays, day: int):
        __block_result_5__ = na
        if timeframe.isintraday or timeframe.isdaily:
            __block_result_5__ = map.get(this.days, day)
        elif timeframe.isweekly:
            closeDay: int = dayofweek(time_close)
            inDaysApproval: bool = map.get(this.days, day)
            nextDay: int = nextDayAfter(day)
            while inDaysApproval and nextDay != closeDay:
                inDaysApproval = map.get(this.days, nextDay)
                nextDay = nextDayAfter(nextDay)
            __block_result_5__ = inDaysApproval
        else:
            __block_result_5__ = method_call('indexof', map.values(this.days), False) == -1
        return __block_result_5__

    @export
    @overload
    @method
    def is_bar_included(this: Session, offset_forward: int = 1):
        nextBar: Bar = getNextBar(offset_forward)
        inSessApproval: bool = na(this.days) and na(this.timeRanges)
        if not na(this.timeRanges):
            for timeRange in this.timeRanges:
                inSessApproval = not na(timeRange) and is_bar_included(timeRange, nextBar) and (True if na(this.days) else is_day_included(this.days, get_trading_day(timeRange, nextBar)))
                if inSessApproval:
                    break
        elif not na(this.days):
            inSessApproval = is_day_included(this.days, dayofweek(nextBar.openUnixTime))
        return inSessApproval


    @export
    @overload
    @method
    def init(this: SessionView, days__00000227__: SessionDays, timeRanges__00000227__: list[SessionTimeRange], names__00000227__: list[str], colors__00000227__: list[Color]):
        this.sess = Session(init(SessionDays()) if na(days__00000227__) else days__00000227__, na)
        if na(timeRanges__00000227__):
            this.sess.timeRanges = array.from_items(init(SessionTimeRange()))
            this.names = array.from_items('Session')
            this.colors = array.from_items(color.green)
        else:
            for i in pine_range(array.size(timeRanges__00000227__) - 1, 0):
                if na(array.get(timeRanges__00000227__, i)):
                    array.remove(timeRanges__00000227__, i)
                    array.remove(names__00000227__, i)
                    array.remove(colors__00000227__, i)

            if array.size(timeRanges__00000227__) == 0:
                array.push(timeRanges__00000227__, init(SessionTimeRange()))
                array.push(names__00000227__, 'Session')
                array.push(colors__00000227__, color.green)
            this.sess.timeRanges = timeRanges__00000227__
            this.names = names__00000227__
            this.colors = colors__00000227__
        return this

    @export
    @method
    def draw_boxes(this: SessionView):
        approvals: PersistentSeries[list[bool]] = array.new_bool(array.size(this.sess.timeRanges))
        highestHighs: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        lowestLows: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        opens: Persistent[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        boxes: Persistent[list[Box]] = array.new_box(array.size(this.sess.timeRanges))

        currentBar: Bar = getCurrentBar()
        __block_result_6__ = na
        for i, timeRange in enumerate(this.sess.timeRanges):
            inSessApproval: bool = not na(timeRange) and is_bar_included(timeRange, currentBar) and (True if na(this.sess.days) else is_day_included(this.sess.days, get_trading_day(timeRange, currentBar)))
            array.set(approvals, i, inSessApproval)

            if inSessApproval and (bar_index == 1 or (bar_index > 1 and (not method_call('get', approvals[1], i)))):
                array.set(highestHighs, i, high)
                array.set(lowestLows, i, low)
                array.set(opens, i, open)
                array.set(boxes, i, box.new(top_left=chart.point.from_index(bar_index, high), bottom_right=chart.point.from_index(bar_index, low), border_color=array.get(this.colors, i), bgcolor=color.new(color.teal, 80) if close > open else color.new(color.red, 80), text=array.get(this.names, i), text_size=size.tiny, text_color=array.get(this.colors, i), text_halign=text.align_left, text_valign=text.align_top, force_overlay=True))
            elif inSessApproval and bar_index > 1:
                array.set(highestHighs, i, math.max(high, method_call('get', highestHighs[1], i)))
                array.set(lowestLows, i, math.min(low, method_call('get', lowestLows[1], i)))

            __block_result_7__ = na
            if inSessApproval and bar_index > 1:
                method_call('set_top', array.get(boxes, i), array.get(highestHighs, i))
                method_call('set_bottom', array.get(boxes, i), array.get(lowestLows, i))
                method_call('set_right', array.get(boxes, i), bar_index)
                __block_result_7__ = method_call('set_bgcolor', array.get(boxes, i), color.new(color.teal, 80) if close > array.get(opens, i) else color.new(color.red, 80))
            __block_result_6__ = __block_result_7__
        return __block_result_6__

    @export
    @method
    def draw_candles(this: SessionView):
        approvals: PersistentSeries[list[bool]] = array.new_bool(array.size(this.sess.timeRanges))
        highestHighs: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        lowestLows: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        opens: Persistent[list[ChartPoint]] = array.new(array.size(this.sess.timeRanges), NA(ChartPoint))
        bodies: Persistent[list[Box]] = array.new_box(array.size(this.sess.timeRanges))
        upWicks: Persistent[list[Line]] = array.new_line(array.size(this.sess.timeRanges))
        downWicks: Persistent[list[Line]] = array.new_line(array.size(this.sess.timeRanges))

        currentBar: Bar = getCurrentBar()
        __block_result_8__ = na
        for i, timeRange in enumerate(this.sess.timeRanges):
            inSessApproval: bool = not na(timeRange) and is_bar_included(timeRange, currentBar) and (True if na(this.sess.days) else is_day_included(this.sess.days, get_trading_day(timeRange, currentBar)))
            array.set(approvals, i, inSessApproval)

            if inSessApproval and (bar_index == 1 or (bar_index > 1 and (not method_call('get', approvals[1], i)))):
                array.set(highestHighs, i, high)
                array.set(lowestLows, i, low)
                array.set(opens, i, chart.point.now(open))
                array.set(bodies, i, box.new(top_left=chart.point.from_index(bar_index, open), bottom_right=chart.point.from_index(bar_index, close), border_color=array.get(this.colors, i), bgcolor=color.new(color.teal, 80) if close > open else color.new(color.red, 80), text=array.get(this.names, i), text_size=size.tiny, text_color=array.get(this.colors, i), text_halign=text.align_left, text_valign=text.align_top, force_overlay=True))
                array.set(upWicks, i, line.new(first_point=chart.point.from_index(bar_index, math.max(open, close)), second_point=chart.point.from_index(bar_index, array.get(highestHighs, i)), color=array.get(this.colors, i), force_overlay=True))
                array.set(downWicks, i, line.new(first_point=chart.point.from_index(bar_index, math.min(open, close)), second_point=chart.point.from_index(bar_index, array.get(lowestLows, i)), color=array.get(this.colors, i), force_overlay=True))
            elif inSessApproval and bar_index > 1:
                array.set(highestHighs, i, math.max(high, method_call('get', highestHighs[1], i)))
                array.set(lowestLows, i, math.min(low, method_call('get', lowestLows[1], i)))

            __block_result_9__ = na
            if inSessApproval and bar_index > 1:
                method_call('set_bottom', array.get(bodies, i), close)
                method_call('set_right', array.get(bodies, i), bar_index)
                method_call('set_bgcolor', array.get(bodies, i), color.new(color.teal, 80) if close > array.get(opens, i).price else color.new(color.red, 80))
                method_call('set_y1', array.get(upWicks, i), math.max(array.get(opens, i).price, close))
                method_call('set_y2', array.get(upWicks, i), array.get(highestHighs, i))
                method_call('set_y1', array.get(downWicks, i), math.min(array.get(opens, i).price, close))
                method_call('set_y2', array.get(downWicks, i), array.get(lowestLows, i))
                avgBarId: int = (array.get(opens, i).index + bar_index) / 2
                method_call('set_x1', array.get(upWicks, i), avgBarId)
                method_call('set_x2', array.get(upWicks, i), avgBarId)
                method_call('set_x1', array.get(downWicks, i), avgBarId)
                __block_result_9__ = method_call('set_x2', array.get(downWicks, i), avgBarId)
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    @export
    @method
    def draw_bars(this: SessionView):
        approvals: PersistentSeries[list[bool]] = array.new_bool(array.size(this.sess.timeRanges))
        highestHighs: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        lowestLows: PersistentSeries[list[float]] = array.new_float(array.size(this.sess.timeRanges))
        opens: Persistent[list[ChartPoint]] = array.new(array.size(this.sess.timeRanges), NA(ChartPoint))
        bodies: Persistent[list[Line]] = array.new_line(array.size(this.sess.timeRanges))
        openWicks: Persistent[list[Line]] = array.new_line(array.size(this.sess.timeRanges))
        closeWicks: Persistent[list[Line]] = array.new_line(array.size(this.sess.timeRanges))

        currentBar: Bar = getCurrentBar()
        __block_result_10__ = na
        for i, timeRange in enumerate(this.sess.timeRanges):
            inSessApproval: bool = not na(timeRange) and is_bar_included(timeRange, currentBar) and (True if na(this.sess.days) else is_day_included(this.sess.days, get_trading_day(timeRange, currentBar)))
            array.set(approvals, i, inSessApproval)

            if inSessApproval and (bar_index == 1 or (bar_index > 1 and (not method_call('get', approvals[1], i)))):
                array.set(highestHighs, i, high)
                array.set(lowestLows, i, low)
                array.set(opens, i, chart.point.now(open))
                array.set(bodies, i, line.new(first_point=chart.point.from_index(bar_index, array.get(lowestLows, i)), second_point=chart.point.from_index(bar_index, array.get(highestHighs, i)), color=array.get(this.colors, i), force_overlay=True))
                array.set(openWicks, i, line.new(first_point=chart.point.from_index(bar_index, array.get(opens, i).price), second_point=chart.point.from_index(bar_index, array.get(opens, i).price), color=array.get(this.colors, i), force_overlay=True))
                array.set(closeWicks, i, line.new(first_point=chart.point.from_index(bar_index, close), second_point=chart.point.from_index(bar_index, close), color=array.get(this.colors, i), force_overlay=True))
            elif inSessApproval and bar_index > 1:
                array.set(highestHighs, i, math.max(high, method_call('get', highestHighs[1], i)))
                array.set(lowestLows, i, math.min(low, method_call('get', lowestLows[1], i)))

            __block_result_11__ = na
            if inSessApproval and bar_index > 1:
                method_call('set_y1', array.get(bodies, i), array.get(lowestLows, i))
                method_call('set_y2', array.get(bodies, i), array.get(highestHighs, i))
                avgBarId: int = (array.get(opens, i).index + bar_index) / 2
                method_call('set_x1', array.get(bodies, i), avgBarId)
                method_call('set_x2', array.get(bodies, i), avgBarId)
                method_call('set_x2', array.get(openWicks, i), avgBarId)
                method_call('set_y1', array.get(closeWicks, i), close)
                method_call('set_y2', array.get(closeWicks, i), close)
                method_call('set_x1', array.get(closeWicks, i), avgBarId)
                __block_result_11__ = method_call('set_x2', array.get(closeWicks, i), bar_index)
            __block_result_10__ = __block_result_11__
        return __block_result_10__


    @export
    @method
    def draw(this: SessionView, viewMode: ViewMode = ViewMode.Boxes):
        __block_result_12__ = na
        __switch__ = viewMode
        if __switch__ == ViewMode.Candles:
            __block_result_12__ = draw_candles(this)
        elif __switch__ == ViewMode.Bars:
            __block_result_12__ = draw_bars(this)
        else:
            __block_result_12__ = draw_boxes(this)
        return __block_result_12__


    referenceTimezone: Persistent = method_call(to_string, referenceTimezone__input)
    dateTimeWindow: Persistent[DateTimeWindow] = init(DateTimeWindow(), fromDateTime=__input_4__ if fromEnabled else na, toDateTime=__input_5__ if toEnabled else na, refTimezone=referenceTimezone, chTimezone=method_call(to_string, __input_6__))

    dateFilterApproval: Series[bool] = is_bar_included(dateTimeWindow, offset_forward)

    bgcolor(color=na if dateFilterApproval else color.new(color.fuchsia, 90), offset=offset_forward, title='Datetime Window Filter', force_overlay=True)

    days__global__: Persistent = init(SessionDays(), sun=__input_8__, mon=__input_9__, tue=__input_10__, wed=__input_11__, thu=__input_12__, fri=__input_13__, sat=__input_14__) if daysEnabled else na
    sessionTimeRange1: Persistent = from_sess_string(SessionTimeRange(), sess=__input_18__, refTimezone=method_call(to_string, __input_19__)) if sessionEnabled1 else na
    sessionTimeRange2: Persistent = from_sess_string(SessionTimeRange(), sess=__input_23__, refTimezone=method_call(to_string, __input_24__)) if sessionEnabled2 else na
    sessionTimeRange3: Persistent = from_sess_string(SessionTimeRange(), sess=__input_28__, refTimezone=method_call(to_string, __input_29__)) if sessionEnabled3 else na
    sessionTimeRange4: Persistent = from_sess_string(SessionTimeRange(), sess=__input_33__, refTimezone=method_call(to_string, __input_34__)) if sessionEnabled4 else na

    view: Persistent[SessionView] = init(SessionView(), days__global__, array.from_items(sessionTimeRange1, sessionTimeRange2, sessionTimeRange3, sessionTimeRange4), array.from_items(sessionName1, sessionName2, sessionName3, sessionName4), array.from_items(sessionColor1, sessionColor2, sessionColor3, sessionColor4))

    sessionFilterApproval: Series[bool] = is_bar_included(view.sess, offset_forward)

    draw(view, viewMode)

    bgcolor(color=na if sessionFilterApproval else color.new(color.new('#FF0000'), 90), offset=offset_forward, title='Session Filter', force_overlay=True)
    sessTable: Persistent = table.new(position=position.top_right, columns=1, rows=2, bgcolor=color.new(chart.bg_color, 90), force_overlay=True)
    sessStr: Persistent = to_sess_string(view.sess)
    if barstate.islastconfirmedhistory:
        table.cell(table_id=sessTable, column=0, row=0, text='Session', text_color=chart.fg_color)
        table.cell(table_id=sessTable, column=0, row=1, text=sessStr, text_color=chart.fg_color)

    if anomalyDetectionEnabled or debugEnabled:
        currentBar: Bar = getCurrentBar()
        nextBar: Series[Bar] = getNextBar(offset_forward)
        predictedCurrentBar: Bar = nextBar[offset_forward]
        anomalyDetected: bool = not eq(predictedCurrentBar, currentBar) if bar_index > offset_forward else False
        if anomalyDetectionEnabled and anomalyDetected:
            log.error('Data anomaly detected in bar {0}! In the previous {1} bar(s) the predicted bar was {2}', to_string(currentBar), offset_forward, to_string(predictedCurrentBar))

        predictedDateFilterApproval: bool = dateFilterApproval[offset_forward]
        currentDateFilterApproval: bool = (True if na(dateTimeWindow.fromDateTime) else time >= dateTimeWindow.fromDateTime) and (True if na(dateTimeWindow.toDateTime) else time_close <= dateTimeWindow.toDateTime)
        if debugEnabled and predictedDateFilterApproval != currentDateFilterApproval and (not anomalyDetected):
            log.error('DateTime window filter value of bar {0} is {1}! In the previous {2} bar(s) the predicted filter value was {3}', to_string(predictedCurrentBar), currentDateFilterApproval, offset_forward, predictedDateFilterApproval)

        predictedSessionFilterApproval: bool = sessionFilterApproval[offset_forward]

        sessStrs: list[str] = to_sess_strings(view.sess)
        currentSessionFilterApproval: bool = False
        for sessString in sessStrs:
            currentSessionFilterApproval = currentSessionFilterApproval or not na(time(timeframe.period, sessString))
        if debugEnabled and predictedSessionFilterApproval != currentSessionFilterApproval and (not anomalyDetected):
            log.error('Session filter value of bar {0} is {1}! In the previous {2} bar(s) the predicted filter value was {3}', to_string(predictedCurrentBar), currentSessionFilterApproval, offset_forward, predictedSessionFilterApproval)

        if barstate.islastconfirmedhistory:
            log.warning('The session is {0} -> {1}', to_string(view.sess), sessStr)
            log.warning('The size of the DateTime window {0} is: {1, number, integer} secs or {2, number, integer} bars', to_string(dateTimeWindow), get_size_in_secs(dateTimeWindow), get_size_in_bars(dateTimeWindow))
            log.warning('The size of the session {0} is: {1, number, integer} secs or {2, number, integer} bars', sessStr, get_size_in_secs(array.get(view.sess.timeRanges, 0)), get_size_in_bars(array.get(view.sess.timeRanges, 0)))

    plotchar(series=dateFilterApproval if debugEnabled else False, title='DateTime Filter', char='*', location=location.belowbar, display=display.pane + display.data_window, force_overlay=True)
    plotchar(series=sessionFilterApproval if debugEnabled else False, title='Session Filter', char='^', location=location.abovebar, display=display.pane + display.data_window, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
