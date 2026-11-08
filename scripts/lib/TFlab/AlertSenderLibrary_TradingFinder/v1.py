"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import alert, na, script, string, syminfo, time, timeframe
from typing import Protocol, Any


__all__ = ['AlertSender']


class _ProtocolAlertsender(Protocol):
    def __call__(self, Condition: bool, Alert: str, AlertName: str, AlertType: str, DetectionType: str, SetupData: str, Frequncy: str, UTC: str, MoreInfo: str, Message: str, o: float, h: float, l: float, c: float, Entry: float, TP: float, SL: float, Distal: float, Proximal: float) -> Any: ...


AlertSender: _ProtocolAlertsender = Exported()


@script.library('AlertSenderLibrary_TradingFinder', overlay=True)
def main():
    @export
    def AlertSender(Condition: bool, Alert: str, AlertName: str, AlertType: str, DetectionType: str, SetupData: str, Frequncy: str, UTC: str, MoreInfo: str, Message: str, o: float, h: float, l: float, c: float, Entry: float, TP: float, SL: float, Distal: float, Proximal: float):
        condition: bool = Condition
        alert__ren__: str = Alert
        alertname: str = AlertName
        message: str = Message
        alerttype: str = AlertType
        frequncy: str = Frequncy
        detectiontype: str = DetectionType
        moreinfo: str = MoreInfo
        O: float = o
        H: float = h
        L: float = l
        C: float = c
        entry: float = Entry
        tp: float = TP
        sl: float = SL
        Time = string.format_time(time, '    yy-MM-dd \n    HH:mm:ss', UTC)
        __block_result__ = na
        if detectiontype == 'Signal' or detectiontype == 'Order Block Signal' or detectiontype == 'Setup':
            __block_result_1__ = na
            if alerttype == 'Bullish':
                __block_result_1__ = 'Long ' + detectiontype
            elif alerttype == 'Bearish':
                __block_result_1__ = 'Short ' + detectiontype
            __block_result__ = __block_result_1__
        else:
            __block_result__ = alerttype + ' ' + detectiontype
        Type: str = __block_result__
        tf = timeframe.period
        __block_result_2__ = na
        if string.contains(tf, 'S'):
            __block_result_3__ = na
            if tf == 'S':
                __block_result_3__ = ' 1 Second'
            else:
                __block_result_3__ = string.substring(tf, 0, string.length(tf) - 1) + ' Seconds'
            __block_result_2__ = __block_result_3__
        elif string.contains(tf, 'D'):
            __block_result_4__ = na
            if tf == 'D':
                __block_result_4__ = ' Daily'
            else:
                __block_result_4__ = string.substring(tf, 0, string.length(tf) - 1) + ' Days'
            __block_result_2__ = __block_result_4__
        elif string.contains(tf, 'W'):
            __block_result_5__ = na
            if tf == 'W':
                __block_result_5__ = ' Weakly'
            else:
                __block_result_5__ = string.substring(tf, 0, string.length(tf) - 1) + ' Weaks'
            __block_result_2__ = __block_result_5__
        elif string.contains(tf, 'M'):
            __block_result_6__ = na
            if tf == 'M':
                __block_result_6__ = ' Monthly'
            else:
                __block_result_6__ = string.substring(tf, 0, string.length(tf) - 1) + ' Months'
            __block_result_2__ = __block_result_6__
        elif string.contains(tf, ''):
            __block_result_7__ = na
            if string.tonumber(tf) < 60:
                __block_result_8__ = na
                if tf == '1':
                    __block_result_8__ = '1 Minute'
                else:
                    __block_result_8__ = tf + ' Minutes'
                __block_result_7__ = __block_result_8__
            elif string.tonumber(tf) >= 60:
                __block_result_9__ = na
                if tf == '60':
                    __block_result_9__ = ' 1 Hour'
                else:
                    __block_result_9__ = string.tostring(string.tonumber(tf) / 60) + ' Hours'
                __block_result_7__ = __block_result_9__
            __block_result_2__ = __block_result_7__
        tfcalculator = __block_result_2__
        __block_result_10__ = na
        if MoreInfo == 'Off':
            __block_result_10__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n📩Message: ' + message
        elif MoreInfo == 'On':
            __block_result_11__ = na
            if DetectionType == 'Order Block Signal':
                __block_result_11__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n🕘Time:' + '\n' + Time + '\n🧮Zone Price =>' + '\n     Distal:' + string.tostring(Distal) + '\n     Proximal:' + string.tostring(Proximal) + '\n📩Message: ' + message
            elif DetectionType == 'Signal':
                __block_result_11__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n🕘Time:' + '\n' + Time + '\n🧮market price =>' + '\n     Open:' + string.tostring(O) + '\n     High:' + string.tostring(H) + '\n     Low:' + string.tostring(L) + '\n     Close:' + string.tostring(C) + '\n📩Message: ' + message
            elif DetectionType == 'Setup':
                __block_result_12__ = na
                if SetupData == 'Full':
                    __block_result_12__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n🕘Time:' + '\n' + Time + '\n🧮Setup Price Data =>' + '\n     Entry:' + string.tostring(entry) + '\n     Stop Loss:' + string.tostring(sl) + '\n     Take Profit:' + string.tostring(tp) + '\n📩Message: ' + message
                elif SetupData == 'Basic':
                    __block_result_12__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n🕘Time:' + '\n' + Time + '\n🧮Setup Price Data =>' + '\n     Entry:' + string.tostring(O) + '\n📩Message: ' + message
                __block_result_11__ = __block_result_12__
            elif DetectionType == 'Analysis':
                __block_result_11__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n📩Message: ' + message
            else:
                __block_result_11__ = '⏰Alert Name: ' + alertname + '\n‼️Alert Type: ' + Type + '\n🔠Symbol: ' + syminfo.ticker + '\n📈Time Frame: ' + tfcalculator + '\n🕘Time:' + '\n' + Time + '\n📩Message: ' + message
            __block_result_10__ = __block_result_11__
        messagetext = __block_result_10__
        __block_result_13__ = na
        if alert__ren__ == 'On':
            __block_result_14__ = na
            if condition:
                if frequncy == 'All':
                    alert(messagetext, alert.freq_all)
                if frequncy == 'Once Per Bar':
                    alert(messagetext, alert.freq_once_per_bar)
                __block_result_15__ = na
                if frequncy == 'Once Per Bar Close':
                    __block_result_15__ = alert(messagetext, alert.freq_once_per_bar_close)
                __block_result_14__ = __block_result_15__
            __block_result_13__ = __block_result_14__
        return __block_result_13__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
