"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, chart, close, color, dayofmonth, display, format, input,
    log, map, math, matrix, month, na, nz, plot, position, runtime, script, size, strategy, string,
    ta, table, text, time, weekofyear, year
)
from pynecore.types import Color, Matrix, NA, Persistent, Table
from typing import Protocol, Any


__all__ = ['MetricsTable', 'SeasonalData', 'SeasonalTable', 'Seasonality', 'SideStats', 'StatsData', 'StatsTable', 'getTablePos', 'init', 'update']


@udt
class SideStats:
    numOf: int = 0
    maxStreak: int = 0
    sumProfit: float = 0.0
    profitStDev: float = 0.0
    sumGain: float = 0.0
    gainStDev: float = 0.0
    avgQuantityPerc: float = 0.0
    avgCapitalRiskPerc: float = 0.0
    avgTPExecutedCount: float = 0.0
    avgRiskRewardRatio: float = 0.0
    sumFreeProfit: float = 0.0
    freeProfitStDev: float = 0.0


@udt
class StatsTable:
    table__ren__: Table = na(Table)
    rows: int = na(int)
    columns: int = na(int)


@udt
class StatsData:
    wins: 'SideStats' = _dataclass_field(default_factory=lambda: na(SideStats))
    losses: 'SideStats' = _dataclass_field(default_factory=lambda: na(SideStats))
    numOfInconclusiveExits: int = na(int)
    avgProfitStr: str = na(str)
    profitStDevStr: str = na(str)
    lossProfitStDevStr: str = na(str)
    avgFreeProfitStr: str = na(str)
    freeProfitStDevStr: str = na(str)
    lossFreeProfitStDevStr: str = na(str)


@udt
class MetricsTable:
    table__ren__: Table = na(Table)
    rows: int = na(int)
    columns: int = na(int)


class Seasonality(Enum):
    monthOfYear = 'M/Y'
    weekOfYear = 'W/Y'
    dayOfMonth = 'D/M'


@udt
class SeasonalData:
    seasonality: Seasonality = na(Seasonality)
    eonToMatrixRow: dict[int, int] = na(dict)
    numOfEons: int = na(int)
    mostRecentMatrixRow: int = na(int)
    balances: Matrix[float] = na(Matrix)
    returnPercs: Matrix[float] = na(Matrix)
    maxDDs: Matrix[float] = na(Matrix)
    eonReturnPercs: list[float] = na(list)
    eonCAGRs: list[float] = na(list)
    eonMaxDDs: list[float] = na(list)


@udt
class SeasonalTable:
    table__ren__: Table = na(Table)
    headRows: int = na(int)
    headColumns: int = na(int)
    eonRows: int = na(int)
    seasonColumns: int = na(int)
    statsRows: int = na(int)
    statsColumns: int = na(int)
    rows: int = na(int)
    columns: int = na(int)
    extended: bool = na(bool)


class _ProtocolGettablepos(Protocol):
    def __call__(self, ypos: str, xpos: str) -> Any: ...


class _ProtocolInit(Protocol):
    def __call__(self, this: StatsTable, pos: str, height: float = 0.0, width: float = 0.0, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), neutralTxtColor: Color = chart.fg_color, positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C')) -> Any: ...


class _ProtocolUpdate(Protocol):
    def __call__(self, this: StatsData, wins: SideStats, losses: SideStats, numOfInconclusiveExits: int) -> Any: ...


class _ProtocolUpdate3(Protocol):
    def __call__(self, this: StatsTable, stats: StatsData, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C')) -> Any: ...


class _ProtocolInit4(Protocol):
    def __call__(self, this: MetricsTable, pos: str, height: float = 0.0, width: float = 0.0, neutralBgColor: Color = chart.bg_color) -> Any: ...


class _ProtocolUpdate5(Protocol):
    def __call__(self, this: MetricsTable, stats: StatsData, buyAndHoldPerc: float, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C')) -> Any: ...


class _ProtocolInit6(Protocol):
    def __call__(self, this: SeasonalData, seas: Seasonality) -> Any: ...


class _ProtocolUpdate7(Protocol):
    def __call__(self, this: SeasonalData) -> Any: ...


class _ProtocolInit8(Protocol):
    def __call__(self, this: SeasonalTable, data: SeasonalData, pos: str, maxNumOfYears: int = 5, height: float = 0.0, width: float = 0.0, extended: bool = False, neutralTxtColor: Color = chart.fg_color, neutralBgColor: Color = color.new('#363A450C')) -> Any: ...


class _ProtocolUpdate9(Protocol):
    def __call__(self, this: SeasonalTable, data: SeasonalData, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), neutralTxtColor: Color = chart.fg_color, positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C'), timeBgColor: Color = color.new('#2D3864')) -> Any: ...


getTablePos: _ProtocolGettablepos = Exported()
init: _ProtocolInit = Exported()
update: _ProtocolUpdate = Exported()
update: _ProtocolUpdate3 = Exported()
init: _ProtocolInit4 = Exported()
update: _ProtocolUpdate5 = Exported()
init: _ProtocolInit6 = Exported()
update: _ProtocolUpdate7 = Exported()
init: _ProtocolInit8 = Exported()
update: _ProtocolUpdate9 = Exported()


TT_COMPUTATIONAL_HEAVY_WARNING: str = ' WARNING! Computational heavy operation. If you get a timeout error please adjust the datetime window filter or disable other computational heavy operations.'


@script.library(title='analytics_tables')
def main(
    showSeasonalTable=input.bool(defval=True, title='Show Seasonal Table⚠️🐌  ', inline='Seasonal Table', group='Analytics', display=display.data_window),
    seasonalTableExtend=input.bool(defval=True, title='Extended', tooltip='Show the table with the seasonal performance. Extend the seasonal table with additional rows and colums with statistics for each season like Avg, StDev and for each eon like CAGR and MaxDD.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Seasonal Table', group='Analytics', display=display.data_window),
    seasonalTableSeasonality=input.enum(defval=Seasonality.monthOfYear, title='  Season/Eon       ', tooltip='The season and eon of the seasonal performance table.', group='Analytics', display=display.data_window),
    seasonalTableMaxNumOfYears=input.int(defval=5, title='  Max Num of Years     ', minval=0, tooltip='The maximum number of eons to show in the seasonal performance table.', group='Analytics', display=display.data_window),
    showStatsTable=input.bool(defval=True, title='Show Stats Table⚠️🐌   ', inline='Stats Table', group='Analytics', display=display.data_window),
    statsTablePosY=input.string(defval='TOP', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('TOP', 'MIDDLE', 'BOTTOM'), inline='Stats Table', group='Analytics', display=display.data_window),
    statsTablePosX=input.string(defval='RIGHT', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('LEFT', 'RIGHT'), tooltip='Show the table with the overall trade statistics on the selected corner.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Stats Table', group='Analytics', display=display.data_window),
    showMetricsTable=input.bool(defval=True, title='Show Metrics Table⚠️🐌  ', inline='Metrics Table', group='Analytics', display=display.data_window),
    metricsTablePosY=input.string(defval='BOTTOM', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('TOP', 'MIDDLE', 'BOTTOM'), inline='Metrics Table', group='Analytics', display=display.data_window),
    metricsTablePosX=input.string(defval='RIGHT', title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', options=('LEFT', 'RIGHT'), tooltip='Show the table with the trade metrics on the selected corner.' + TT_COMPUTATIONAL_HEAVY_WARNING, inline='Metrics Table', group='Analytics', display=display.data_window)
):
    @export
    def getTablePos(ypos: str, xpos: str):
        return string.lower(ypos) + '_' + string.lower(xpos)


    @overload
    @method
    def getAvgFreeProfit(this: SideStats):
        return nz(this.sumFreeProfit / this.numOf)

    @overload
    @method
    def getAvgProfit(this: SideStats):
        return nz(this.sumProfit / this.numOf)

    @overload
    @method
    def getAvgGain(this: SideStats):
        return nz(this.sumGain / this.numOf)


    @export
    @overload
    @method
    def init(this: StatsTable, pos: str, height: float = 0.0, width: float = 0.0, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), neutralTxtColor: Color = chart.fg_color, positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C')):
        HEAD_RATIO: float = 1.5
        HEAD_ROWS: int = 1
        BODY_ROWS: int = 13
        ROWS: int = HEAD_ROWS + BODY_ROWS
        cellHeight: float = height / ((HEAD_ROWS * HEAD_RATIO + BODY_ROWS) * 1.045)
        headHeight: float = cellHeight * HEAD_RATIO
        cellTextSize: str = size.small if height == 0 else size.auto
        headTextSize: str = size.normal if height == 0 else size.auto
        HEAD_COLUMNS: int = 1
        BODY_COLUMNS: int = 3
        COLUMNS: int = HEAD_COLUMNS + BODY_COLUMNS
        cellWidth: float = width / ((HEAD_COLUMNS * HEAD_RATIO + BODY_COLUMNS) * 1.045)
        headWidth: float = cellWidth * HEAD_RATIO
        this.rows = ROWS
        this.columns = COLUMNS

        this.table__ren__ = table.new(position=pos, rows=ROWS, columns=COLUMNS, frame_color=neutralBgColor, frame_width=2, border_color=neutralBgColor, border_width=1, force_overlay=True)

        table.cell(this.table__ren__, row=0, column=0, text='❓', height=headHeight, width=headWidth, text_color=neutralTxtColor, text_halign=text.align_right, text_valign=text.align_bottom, bgcolor=neutralBgColor, tooltip='This table summarizes the overall statistics of all/winning/losing trades of the strategy. In contrast to the TV backtest engine, a trade is considered to be complete when the entire entry position was exited and not when an order is executed (e.g. a take profit price target is reached).')

        vTooltips: Persistent[list[str]] = array.from_items('All trades (winning and losing).', 'The winning trades.', 'The losing trades.')
        for j, title in enumerate(array.from_items('All', 'Wins', 'Losses')):
            table.cell(this.table__ren__, row=0, column=j + 1, text=title, height=headHeight, width=cellWidth, text_valign=text.align_bottom, text_size=headTextSize, tooltip=array.get(vTooltips, j))

        table.cell_set_text_color(this.table__ren__, row=0, column=1, text_color=neutralTxtColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=1, bgcolor=neutralBgColor)

        table.cell_set_text_color(this.table__ren__, row=0, column=2, text_color=positiveTxtColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=2, bgcolor=positiveBgColor)

        table.cell_set_text_color(this.table__ren__, row=0, column=3, text_color=negativeTxtColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=3, bgcolor=negativeBgColor)

        hTooltips: Persistent[list[str]] = array.from_items('The total number of trades and those that had a winning/losing outcome.', 'The maximum consecutive number of wins/losses in a row.', 'The percent of the wins/losses.', 'The average profit (percentagewise) per trade of all/winning/losing trades.', 'The standard deviation of all/winning/losing trade profits.', 'The average gain on account (percentagewise) per trade of all/winning/losing trades weighted by the entry quantity percentage. Thus the result is non-compounding.', 'The standard deviation of all/winning/losing trade gains.', 'The average quantity percent of all/winning/losing trades.', 'The average capital at risk of all/winning/losing trades.', 'The average number of take profit targets executed during all/winning/losing trades.', 'The average risk to reward ratio when entered all/winning/losing trades.', 'The free average profit (percentagewise) per trade of all/winning/losing trades. This is the profit you would have if you exited the entire amount at the last exit.', 'The standard deviation of all/winning/losing trade free profits.')
        for i, title in enumerate(array.from_items('Trades', 'Streak', 'Rate', 'Avg Profit', 'Profit Dev', 'Avg Gain', 'Gain Dev', 'Quantity', 'Capital Risk', 'TP Exec #', 'Risk Reward', 'Avg Free Profit', 'Free Profit Dev')):
            r: int = i + 1
            table.cell(this.table__ren__, row=r, column=0, text=title, height=cellHeight, width=headWidth, text_color=neutralTxtColor, text_halign=text.align_right, text_size=cellTextSize, bgcolor=neutralBgColor, tooltip=array.get(hTooltips, i))

            for j in pine_range(1, COLUMNS - 1):
                table.cell(this.table__ren__, row=r, column=j, height=cellHeight, width=cellWidth, text_size=cellTextSize)

            table.cell_set_text_color(this.table__ren__, row=r, column=1, text_color=neutralTxtColor)
            table.cell_set_bgcolor(this.table__ren__, row=r, column=1, bgcolor=neutralBgColor)

            table.cell_set_text_color(this.table__ren__, row=r, column=2, text_color=positiveTxtColor)
            table.cell_set_bgcolor(this.table__ren__, row=r, column=2, bgcolor=positiveBgColor)

            table.cell_set_text_color(this.table__ren__, row=r, column=3, text_color=negativeTxtColor)
            table.cell_set_bgcolor(this.table__ren__, row=r, column=3, bgcolor=negativeBgColor)

        return this


    @method
    def getNumOfTrades(this: StatsData):
        return this.wins.numOf + this.losses.numOf

    @method
    def getWinRate(this: StatsData):
        return this.wins.numOf / getNumOfTrades(this)

    @method
    def getLossRate(this: StatsData):
        return this.losses.numOf / getNumOfTrades(this)

    @overload
    @method
    def getAvgFreeProfit(this: StatsData):
        return getAvgFreeProfit(this.wins) * getWinRate(this) + getAvgFreeProfit(this.losses) * getLossRate(this)

    @method
    def getFreeProfitStDev(this: StatsData):
        return this.wins.freeProfitStDev * getWinRate(this) + this.losses.freeProfitStDev * getLossRate(this)

    @overload
    @method
    def getAvgProfit(this: StatsData):
        return getAvgProfit(this.wins) * getWinRate(this) + getAvgProfit(this.losses) * getLossRate(this)

    @method
    def getProfitStDev(this: StatsData):
        return this.wins.profitStDev * getWinRate(this) + this.losses.profitStDev * getLossRate(this)

    @overload
    @method
    def getAvgGain(this: StatsData):
        return getAvgGain(this.wins) * getWinRate(this) + getAvgGain(this.losses) * getLossRate(this)

    @method
    def getGainStDev(this: StatsData):
        return this.wins.gainStDev * getWinRate(this) + this.losses.gainStDev * getLossRate(this)

    @method
    def getAvgQuantityPerc(this: StatsData):
        return this.wins.avgQuantityPerc * getWinRate(this) + this.losses.avgQuantityPerc * getLossRate(this)

    @method
    def getAvgCapitalRiskPerc(this: StatsData):
        return this.wins.avgCapitalRiskPerc * getWinRate(this) + this.losses.avgCapitalRiskPerc * getLossRate(this)

    @method
    def getAvgTPExecutedCount(this: StatsData):
        return this.wins.avgTPExecutedCount * getWinRate(this) + this.losses.avgTPExecutedCount * getLossRate(this)

    @method
    def getAvgRiskRewardRatio(this: StatsData):
        return this.wins.avgRiskRewardRatio * getWinRate(this) + this.losses.avgRiskRewardRatio * getLossRate(this)

    @export
    @overload
    @method
    def update(this: StatsData, wins: SideStats, losses: SideStats, numOfInconclusiveExits: int):
        this.wins = wins
        this.losses = losses
        this.numOfInconclusiveExits = numOfInconclusiveExits

        avgProfit: float = getAvgProfit(this)
        this.avgProfitStr = ('+' if avgProfit >= 0.0 else '') + string.tostring(avgProfit, format.percent)
        this.profitStDevStr = '±' + string.tostring(getProfitStDev(this), format.percent)
        this.lossProfitStDevStr = '±' + string.tostring(this.losses.profitStDev, format.percent)
        avgFreeProfit: float = getAvgFreeProfit(this)
        this.avgFreeProfitStr = ('+' if avgFreeProfit >= 0.0 else '') + string.tostring(avgFreeProfit, format.percent)
        this.freeProfitStDevStr = '±' + string.tostring(getFreeProfitStDev(this), format.percent)
        this.lossFreeProfitStDevStr = '±' + string.tostring(this.losses.freeProfitStDev, format.percent)
        return this

    @export
    @overload
    @method
    def update(this: StatsTable, stats: StatsData, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C')):
        table.cell_set_bgcolor(this.table__ren__, row=2, column=1, bgcolor=negativeBgColor if stats.numOfInconclusiveExits > 0 else neutralBgColor)
        table.cell_set_tooltip(this.table__ren__, row=2, column=1, tooltip=string.format('WARNING! {0,number,integer} inconclusive exit order(s) were detected this is the {1} of all the trades. This means that orders exist were both take profit and stop loss could be reached at the same bar and exit the trade, but due to the "loss of information" in that timeframe a random exit were chosen. Please use a lower timeframe or the bar magnifier feature to have more accurate results.', stats.numOfInconclusiveExits, string.tostring(100.0 * stats.numOfInconclusiveExits / getNumOfTrades(stats), format.percent)))

        table.cell_set_text_color(this.table__ren__, row=4, column=1, text_color=positiveTxtColor if getAvgProfit(stats) > 0.0 else negativeTxtColor)

        table.cell_set_text_color(this.table__ren__, row=6, column=1, text_color=positiveTxtColor if getAvgGain(stats) > 0.0 else negativeTxtColor)

        table.cell_set_text_color(this.table__ren__, row=12, column=1, text_color=positiveTxtColor if getAvgFreeProfit(stats) > 0.0 else negativeTxtColor)

        table.cell_set_text(this.table__ren__, row=1, column=1, text=string.tostring(getNumOfTrades(stats)))
        table.cell_set_text(this.table__ren__, row=1, column=2, text=string.tostring(stats.wins.numOf))
        table.cell_set_text(this.table__ren__, row=1, column=3, text=string.tostring(stats.losses.numOf))
        table.cell_set_text(this.table__ren__, row=2, column=1, text='🚨' if stats.numOfInconclusiveExits > 0 else '')
        table.cell_set_text(this.table__ren__, row=2, column=2, text=string.tostring(stats.wins.maxStreak))
        table.cell_set_text(this.table__ren__, row=2, column=3, text=string.tostring(stats.losses.maxStreak))
        table.cell_set_text(this.table__ren__, row=3, column=1, text=string.tostring(100.0 * (getWinRate(stats) + getLossRate(stats)), format.percent))
        table.cell_set_text(this.table__ren__, row=3, column=2, text=string.tostring(100.0 * getWinRate(stats), format.percent))
        table.cell_set_text(this.table__ren__, row=3, column=3, text=string.tostring(100.0 * getLossRate(stats), format.percent))
        table.cell_set_text(this.table__ren__, row=4, column=1, text=stats.avgProfitStr)
        table.cell_set_text(this.table__ren__, row=4, column=2, text='+' + string.tostring(getAvgProfit(stats.wins), format.percent))
        table.cell_set_text(this.table__ren__, row=4, column=3, text=string.tostring(getAvgProfit(stats.losses), format.percent))
        table.cell_set_text(this.table__ren__, row=5, column=1, text=stats.profitStDevStr)
        table.cell_set_text(this.table__ren__, row=5, column=2, text='±' + string.tostring(stats.wins.profitStDev, format.percent))
        table.cell_set_text(this.table__ren__, row=5, column=3, text=stats.lossProfitStDevStr)
        avgGain: float = getAvgGain(stats)
        table.cell_set_text(this.table__ren__, row=6, column=1, text=('+' if avgGain >= 0.0 else '') + string.tostring(avgGain, format.percent))
        table.cell_set_text(this.table__ren__, row=6, column=2, text='+' + string.tostring(getAvgGain(stats.wins), format.percent))
        table.cell_set_text(this.table__ren__, row=6, column=3, text=string.tostring(getAvgGain(stats.losses), format.percent))
        table.cell_set_text(this.table__ren__, row=7, column=1, text='±' + string.tostring(getGainStDev(stats), format.percent))
        table.cell_set_text(this.table__ren__, row=7, column=2, text='±' + string.tostring(stats.wins.gainStDev, format.percent))
        table.cell_set_text(this.table__ren__, row=7, column=3, text='±' + string.tostring(stats.losses.gainStDev, format.percent))
        table.cell_set_text(this.table__ren__, row=8, column=1, text=string.tostring(getAvgQuantityPerc(stats), format.percent))
        table.cell_set_text(this.table__ren__, row=8, column=2, text=string.tostring(stats.wins.avgQuantityPerc, format.percent))
        table.cell_set_text(this.table__ren__, row=8, column=3, text=string.tostring(stats.losses.avgQuantityPerc, format.percent))
        table.cell_set_text(this.table__ren__, row=9, column=1, text=string.tostring(getAvgCapitalRiskPerc(stats), format.percent))
        table.cell_set_text(this.table__ren__, row=9, column=2, text=string.tostring(stats.wins.avgCapitalRiskPerc, format.percent))
        table.cell_set_text(this.table__ren__, row=9, column=3, text=string.tostring(stats.losses.avgCapitalRiskPerc, format.percent))
        table.cell_set_text(this.table__ren__, row=10, column=1, text=string.tostring(getAvgTPExecutedCount(stats), '#.##'))
        table.cell_set_text(this.table__ren__, row=10, column=2, text=string.tostring(stats.wins.avgTPExecutedCount, '#.##'))
        table.cell_set_text(this.table__ren__, row=10, column=3, text=string.tostring(stats.losses.avgTPExecutedCount, '#.##'))
        table.cell_set_text(this.table__ren__, row=11, column=1, text=string.tostring(getAvgRiskRewardRatio(stats), '#.##'))
        table.cell_set_text(this.table__ren__, row=11, column=2, text=string.tostring(stats.wins.avgRiskRewardRatio, '#.##'))
        table.cell_set_text(this.table__ren__, row=11, column=3, text=string.tostring(stats.losses.avgRiskRewardRatio, '#.##'))
        table.cell_set_text(this.table__ren__, row=12, column=1, text=stats.avgFreeProfitStr)
        table.cell_set_text(this.table__ren__, row=12, column=2, text='+' + string.tostring(getAvgFreeProfit(stats.wins), format.percent))
        table.cell_set_text(this.table__ren__, row=12, column=3, text=string.tostring(getAvgFreeProfit(stats.losses), format.percent))
        table.cell_set_text(this.table__ren__, row=13, column=1, text=stats.freeProfitStDevStr)
        table.cell_set_text(this.table__ren__, row=13, column=2, text='±' + string.tostring(stats.wins.freeProfitStDev, format.percent))
        return table.cell_set_text(this.table__ren__, row=13, column=3, text=stats.lossFreeProfitStDevStr)


    @export
    @overload
    @method
    def init(this: MetricsTable, pos: str, height: float = 0.0, width: float = 0.0, neutralBgColor: Color = chart.bg_color):
        ROWS: int = 2
        COLUMNS: int = 3
        cellHeight: float = height / (ROWS * 1.045)
        cellWidth: float = width / (COLUMNS * 1.045)
        cellTextSize: str = size.normal if height == 0 else size.auto
        this.rows = ROWS
        this.columns = COLUMNS

        this.table__ren__ = table.new(position=pos, rows=ROWS, columns=COLUMNS, frame_color=neutralBgColor, frame_width=2, border_color=neutralBgColor, border_width=1, force_overlay=True)

        for i in pine_range(0, ROWS - 1):
            for j in pine_range(0, COLUMNS - 1):
                table.cell(this.table__ren__, row=i, column=j, height=cellHeight, width=cellWidth, text_size=cellTextSize)

        return this

    @export
    @overload
    @method
    def update(this: MetricsTable, stats: StatsData, buyAndHoldPerc: float, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C')):
        sumProfit: float = stats.wins.sumProfit + stats.losses.sumProfit
        alpha: float = 1.0 + nz((sumProfit - buyAndHoldPerc) / math.abs(buyAndHoldPerc))
        alphaAcceptance: bool = alpha >= 1.0
        netProfitPerc: float = 100.0 * strategy.netprofit / strategy.initial_capital
        beta: float = 1.0 + nz((netProfitPerc - buyAndHoldPerc) / math.abs(buyAndHoldPerc))
        betaAcceptance: bool = beta >= 1.0
        kellyRatioPerc: float = 100.0 * (getWinRate(stats) * getAvgRiskRewardRatio(stats) - getLossRate(stats)) / getAvgRiskRewardRatio(stats)
        maxCapitalLossPerc: float = getAvgCapitalRiskPerc(stats) * stats.losses.maxStreak
        gamma: float = 1.0 + nz((kellyRatioPerc - maxCapitalLossPerc) / maxCapitalLossPerc)
        gammaAcceptance: bool = gamma >= 1.0
        buyAndHoldPercStr: str = string.tostring(buyAndHoldPerc, format.percent)

        avgFreeProfit: float = getAvgFreeProfit(stats)
        chi: float = 1.0 + nz((getAvgProfit(stats) - avgFreeProfit) / math.abs(avgFreeProfit))
        chiAcceptance: bool = chi >= 1.0
        freeProfitStDev: float = getFreeProfitStDev(stats)
        profitStDevInc: float = 1.0 + nz((getProfitStDev(stats) - freeProfitStDev) / math.abs(freeProfitStDev))
        psi: float = chi / profitStDevInc
        psiAcceptance: bool = psi >= 1.0
        lossFreeProfitStDev: float = stats.losses.freeProfitStDev
        lossProfitStDevInc: float = 1.0 + nz((stats.losses.profitStDev - lossFreeProfitStDev) / math.abs(lossFreeProfitStDev))
        zeta: float = chi / lossProfitStDevInc
        zetaAcceptance: bool = zeta >= 1.0

        table.cell_set_text(this.table__ren__, row=0, column=0, text=string.format('α: {0}', string.tostring(100.0 * alpha, format.percent)))
        table.cell_set_text(this.table__ren__, row=0, column=1, text=string.format('β: {0}', string.tostring(100.0 * beta, format.percent)))
        table.cell_set_text(this.table__ren__, row=0, column=2, text=string.format('γ: {0}', string.tostring(100.0 * gamma, format.percent)))
        table.cell_set_text(this.table__ren__, row=1, column=0, text=string.format('χ: {0}', string.tostring(100.0 * chi, format.percent)))
        table.cell_set_text(this.table__ren__, row=1, column=1, text=string.format('ψ: {0}', string.tostring(100.0 * psi, format.percent)))
        table.cell_set_text(this.table__ren__, row=1, column=2, text=string.format('ζ: {0}', string.tostring(100.0 * zeta, format.percent)))
        table.cell_set_text_color(this.table__ren__, row=0, column=0, text_color=positiveTxtColor if alphaAcceptance else negativeTxtColor)
        table.cell_set_text_color(this.table__ren__, row=0, column=1, text_color=positiveTxtColor if betaAcceptance else negativeTxtColor)
        table.cell_set_text_color(this.table__ren__, row=0, column=2, text_color=positiveTxtColor if gammaAcceptance else negativeTxtColor)
        table.cell_set_text_color(this.table__ren__, row=1, column=0, text_color=positiveTxtColor if chiAcceptance else negativeTxtColor)
        table.cell_set_text_color(this.table__ren__, row=1, column=1, text_color=positiveTxtColor if psiAcceptance else negativeTxtColor)
        table.cell_set_text_color(this.table__ren__, row=1, column=2, text_color=positiveTxtColor if zetaAcceptance else negativeTxtColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=0, bgcolor=positiveBgColor if alphaAcceptance else negativeBgColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=1, bgcolor=positiveBgColor if betaAcceptance else negativeBgColor)
        table.cell_set_bgcolor(this.table__ren__, row=0, column=2, bgcolor=positiveBgColor if gammaAcceptance else negativeBgColor)
        table.cell_set_bgcolor(this.table__ren__, row=1, column=0, bgcolor=positiveBgColor if chiAcceptance else negativeBgColor)
        table.cell_set_bgcolor(this.table__ren__, row=1, column=1, bgcolor=positiveBgColor if psiAcceptance else negativeBgColor)
        table.cell_set_bgcolor(this.table__ren__, row=1, column=2, bgcolor=positiveBgColor if zetaAcceptance else negativeBgColor)
        table.cell_set_tooltip(this.table__ren__, row=0, column=0, tooltip=string.format('This alpha metric shows how better or worst the sum of the profits/losses is ({0}) as a percentage compared to the buy and hold return ({1}). If the alpha value is less than 100% this means that the strategy performed worse than the buy and hold for the period of the backtesting.', string.tostring(sumProfit, format.percent), buyAndHoldPercStr))
        table.cell_set_tooltip(this.table__ren__, row=0, column=1, tooltip=string.format('This beta metric shows how better or worst the net profit is ({0}) as a percentage compared to the buy and hold return ({1}). If the beta value is less than 100% this means that the strategy performed worse than the buy and hold for the period of the backtesting.', string.tostring(netProfitPerc, format.percent), buyAndHoldPercStr))
        table.cell_set_tooltip(this.table__ren__, row=0, column=2, tooltip=string.format('This gamma metric shows how better or worst the maximum capital loss percent was ({0}) as a percentage compared to the Kelly ratio ({1}). If the gamma value is less than 100% and the kelly ratio is possitive this means you take too much risk on every trade for the period of the backtesting and you have to decrease the entry quantity and thus the capital at risk of each trade. An other alternative is to try to increase the kelly ratio by increasing the win rate and/or the risk to reward ratio.', string.tostring(maxCapitalLossPerc, format.percent), string.tostring(kellyRatioPerc, format.percent)))
        table.cell_set_tooltip(this.table__ren__, row=1, column=0, tooltip=string.format('This chi metric shows how better or worst the average profit is ({0}) as a percentage compared to the free profit ({1}). If the chi value is less than 100% this means that the strategy would have more profits without the take profit targets for the period of the backtesting.', stats.avgProfitStr, stats.avgFreeProfitStr))
        table.cell_set_tooltip(this.table__ren__, row=1, column=1, tooltip=string.format('This psi metric shows the ratio of the chi with the standard deviation percentage increase ({0}). That shows how better or worst the standard deviation is ({1}) as a percentage compared to the free standard deviation ({2}). If the psi value is less than 100% this means that the strategy increases the standard deviation way too much for the additional profits that returns on top of the free profit for the period of the backtesting.', string.tostring(100.0 * profitStDevInc, format.percent), stats.profitStDevStr, stats.freeProfitStDevStr))
        return table.cell_set_tooltip(this.table__ren__, row=1, column=2, tooltip=string.format('The zeta metric shows the ratio of the chi with the downside deviation percentage increase ({0}). That shows how better or worst the downwards deviation is ({1}) as a percentage compared to the free downwards deviation ({2}). If the zeta value is less than 100% this means that the strategy increases the downwards deviation way too much for the additional profits that returns on top of the free profit for the period of the backtesting.', string.tostring(100.0 * lossProfitStDevInc, format.percent), stats.lossProfitStDevStr, stats.lossFreeProfitStDevStr))



    @method
    def getEonName(this: SeasonalData, eon: int):
        __block_result__ = na
        if this.seasonality == Seasonality.dayOfMonth:
            monthNames: Persistent[list[str]] = array.from_items('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
            __block_result__ = array.get(monthNames, eon - 1)
        else:
            __block_result__ = string.tostring(eon)
        return __block_result__

    @method
    def getSeasonName(this: SeasonalData, mCol: int):
        __block_result_1__ = na
        if this.seasonality == Seasonality.monthOfYear:
            monthNames: Persistent[list[str]] = array.from_items('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
            __block_result_1__ = array.get(monthNames, mCol)
        else:
            seasonTimeframe: str = 'W' if this.seasonality == Seasonality.weekOfYear else 'D'
            __block_result_1__ = string.tostring(mCol + 1) + seasonTimeframe
        return __block_result_1__

    @method
    def getEonToMatrixRow(this: SeasonalData, eon: int):
        if not map.contains(this.eonToMatrixRow, eon):
            map.put(this.eonToMatrixRow, eon, this.numOfEons)
            matrix.add_row(this.balances)
            matrix.add_row(this.returnPercs)
            matrix.add_row(this.maxDDs)
            array.push(this.eonReturnPercs, 0.0)
            array.push(this.eonCAGRs, 0.0)
            array.push(this.eonMaxDDs, 0.0)
            this.numOfEons += 1
        this.mostRecentMatrixRow = map.get(this.eonToMatrixRow, eon)
        return this.mostRecentMatrixRow

    @method
    def getSeasonToMatrixRow(season: int):
        return season - 1

    @export
    @overload
    @method
    def init(this: SeasonalData, seas: Seasonality):
        this.seasonality = seas
        __block_result_2__ = na
        __switch__ = this.seasonality
        if __switch__ == Seasonality.monthOfYear:
            __block_result_2__ = 12
        elif __switch__ == Seasonality.weekOfYear:
            __block_result_2__ = 53
        elif __switch__ == Seasonality.dayOfMonth:
            __block_result_2__ = 31
        seasonColumns: int = __block_result_2__
        this.eonToMatrixRow = map.new()
        this.numOfEons = 0
        this.balances = matrix.new(0, seasonColumns, initial_value=NA(float))
        this.returnPercs = matrix.new(0, seasonColumns, initial_value=NA(float))
        this.maxDDs = matrix.new(0, seasonColumns, initial_value=NA(float))
        this.eonReturnPercs = array.new_float()
        this.eonCAGRs = array.new_float()
        this.eonMaxDDs = array.new_float()
        if this.seasonality == Seasonality.dayOfMonth:
            for e in pine_range(1, 12):
                getEonToMatrixRow(this, e)
        return this

    @method
    def getEonWhen(this: SeasonalData, t: int):
        __block_result_3__ = na
        __switch__ = this.seasonality
        if __switch__ == Seasonality.monthOfYear:
            __block_result_3__ = year(t)
        elif __switch__ == Seasonality.weekOfYear:
            __block_result_3__ = year(t)
        elif __switch__ == Seasonality.dayOfMonth:
            __block_result_3__ = month(t)
        else:
            runtime.error('Invalid seasonality for eon')
            __block_result_3__ = 0
        return __block_result_3__

    @method
    def getSeasonWhen(this: SeasonalData, t: int):
        __block_result_4__ = na
        __switch__ = this.seasonality
        if __switch__ == Seasonality.monthOfYear:
            __block_result_4__ = month(t)
        elif __switch__ == Seasonality.weekOfYear:
            __block_result_4__ = weekofyear(t)
        elif __switch__ == Seasonality.dayOfMonth:
            __block_result_4__ = dayofmonth(t)
        else:
            runtime.error('Invalid seasonality for season')
            __block_result_4__ = 0
        return __block_result_4__

    @export
    @overload
    @method
    def update(this: SeasonalData):
        eon: int = getEonWhen(this, time)
        season: int = getSeasonWhen(this, time)

        nextEon: int = getEonWhen(this, time(timeframe='', bars_back=-1))
        nextSeason: int = getSeasonWhen(this, time(timeframe='', bars_back=-1))

        newEonAhead: bool = eon != nextEon
        newSeasonAhead: bool = season != nextSeason

        prevEonBalance: Persistent[float] = strategy.initial_capital
        prevSeasonBalance: Persistent[float] = strategy.initial_capital

        eonMaxBalance: Persistent[float] = 0.0
        eonMaxDD: Persistent[float] = 0.0
        seasonMaxBalance: Persistent[float] = 0.0
        seasonMaxDD: Persistent[float] = 0.0

        currentBalance: float = strategy.initial_capital + strategy.netprofit

        if ta.rising(strategy.closedtrades, 1):
            eonMaxBalance = math.max(currentBalance, eonMaxBalance)
            eonMaxDD = math.max(100.0 * (eonMaxBalance - currentBalance) / eonMaxBalance, eonMaxDD)
            seasonMaxBalance = math.max(currentBalance, seasonMaxBalance)
            seasonMaxDD = math.max(100.0 * (seasonMaxBalance - currentBalance) / seasonMaxBalance, seasonMaxDD)

            mRow: int = getEonToMatrixRow(this, eon)

            array.set(this.eonReturnPercs, index=mRow, value=100.0 * (currentBalance - prevEonBalance) / prevEonBalance)
            array.set(this.eonCAGRs, index=mRow, value=100.0 * (math.pow(currentBalance / prevEonBalance, 1 / matrix.columns(this.balances)) - 1))
            array.set(this.eonMaxDDs, index=mRow, value=eonMaxDD)

            mCol: int = getSeasonToMatrixRow(season)

            matrix.set(this.balances, row=mRow, column=mCol, value=currentBalance)
            matrix.set(this.returnPercs, row=mRow, column=mCol, value=100.0 * (currentBalance - prevSeasonBalance) / prevSeasonBalance)
            matrix.set(this.maxDDs, row=mRow, column=mCol, value=seasonMaxDD)

        strategyStarted: bool = strategy.opentrades != 0 or strategy.closedtrades > 0

        if newEonAhead and strategyStarted:
            mRow: int = getEonToMatrixRow(this, eon)

            array.set(this.eonReturnPercs, index=mRow, value=100.0 * (currentBalance - prevEonBalance) / prevEonBalance)
            array.set(this.eonCAGRs, index=mRow, value=100.0 * (math.pow(currentBalance / prevEonBalance, 1 / matrix.columns(this.balances)) - 1))
            array.set(this.eonMaxDDs, index=mRow, value=eonMaxDD)

            mNextRow: int = getEonToMatrixRow(this, nextEon)
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(matrix.columns(this.balances) - 1):
                mCol = __loop_1__.value
                matrix.set(this.balances, row=mNextRow, column=mCol, value=currentBalance)
                matrix.set(this.returnPercs, row=mNextRow, column=mCol, value=0.0)
                matrix.set(this.maxDDs, row=mNextRow, column=mCol, value=0.0)
            array.set(this.eonReturnPercs, mNextRow, 0.0)
            array.set(this.eonCAGRs, mNextRow, 0.0)
            array.set(this.eonMaxDDs, mNextRow, 0.0)

            prevEonBalance = currentBalance

            eonMaxBalance = currentBalance
            eonMaxDD = 0.0

        __block_result_5__ = na
        if newSeasonAhead and strategyStarted:
            mRow: int = getEonToMatrixRow(this, eon)

            mCol: int = getSeasonToMatrixRow(season)

            matrix.set(this.balances, row=mRow, column=mCol, value=currentBalance)
            matrix.set(this.returnPercs, row=mRow, column=mCol, value=100.0 * (currentBalance - prevSeasonBalance) / prevSeasonBalance)
            matrix.set(this.maxDDs, row=mRow, column=mCol, value=seasonMaxDD)

            prevSeasonBalance = currentBalance

            seasonMaxBalance = currentBalance
            seasonMaxDD = 0.0
            __block_result_5__ = seasonMaxDD
        return __block_result_5__


    @method
    def matrixToTableRow(this: SeasonalTable, matrixRows: int, mRow: int):
        return this.headRows + this.eonRows - matrixRows + mRow

    @method
    def matrixToTableColumn(this: SeasonalTable, mCol: int):
        return mCol + this.headColumns

    @export
    @overload
    @method
    def init(this: SeasonalTable, data: SeasonalData, pos: str, maxNumOfYears: int = 5, height: float = 0.0, width: float = 0.0, extended: bool = False, neutralTxtColor: Color = chart.fg_color, neutralBgColor: Color = color.new('#363A450C')):
        HEAD_RATIO: float = 1.5
        this.extended = extended
        this.headRows = 1
        this.statsRows = 3 if this.extended else 0
        this.eonRows = data.numOfEons if maxNumOfYears <= 0 or data.seasonality == Seasonality.dayOfMonth else math.min(data.numOfEons, maxNumOfYears)
        this.rows = this.headRows + this.eonRows + this.statsRows
        cellHeight: float = height / ((this.headRows * HEAD_RATIO + this.eonRows + this.statsRows) * 1.045)
        headHeight: float = cellHeight * HEAD_RATIO
        cellTextSize: str = size.small if height == 0 else size.auto
        headTextSize: str = size.normal if height == 0 else size.auto
        this.headColumns = 1
        __block_result_6__ = na
        __switch__ = data.seasonality
        if __switch__ == Seasonality.monthOfYear:
            __block_result_6__ = 12
        elif __switch__ == Seasonality.weekOfYear:
            __block_result_6__ = 53
        elif __switch__ == Seasonality.dayOfMonth:
            __block_result_6__ = 31
        this.seasonColumns = __block_result_6__
        this.statsColumns = 3 if this.extended else 1
        this.columns = this.headColumns + this.seasonColumns + this.statsColumns
        cellWidth: float = width / ((this.headColumns * HEAD_RATIO + this.seasonColumns + this.statsColumns) * 1.045)
        headWidth: float = cellWidth * HEAD_RATIO

        this.table__ren__ = table.new(position=pos, rows=this.rows, columns=this.columns, frame_color=neutralBgColor, frame_width=2, border_color=neutralBgColor, border_width=1)

        table.cell(this.table__ren__, row=0, column=0, text='❓', height=headHeight, width=headWidth, text_color=neutralTxtColor, text_halign=text.align_right, text_valign=text.align_bottom, bgcolor=neutralBgColor, tooltip='This table summarizes the seasonal (monthly/weekly/daily) realized performance of the strategy that occured on each eon (year/month/week).')

        __loop_0__ = pine_loop(0)
        while __loop_0__.step(this.seasonColumns - 1):
            mCol = __loop_0__.value
            table.cell(this.table__ren__, row=0, column=matrixToTableColumn(this, mCol), text=getSeasonName(data, mCol), height=headHeight, width=cellWidth, text_color=neutralTxtColor, text_valign=text.align_bottom, text_size=headTextSize, bgcolor=neutralBgColor)
        if this.extended:
            for j, title in enumerate(array.from_items('P&L', 'CAGR', 'MaxDD')):
                table.cell(this.table__ren__, row=0, column=j + this.headColumns + this.seasonColumns, text=title, height=headHeight, width=cellWidth, text_color=neutralTxtColor, text_valign=text.align_bottom, text_size=headTextSize, bgcolor=neutralBgColor)
        else:
            for j, title in enumerate(array.from_items('P&L')):
                table.cell(this.table__ren__, row=0, column=j + this.headColumns + this.seasonColumns, text=title, height=headHeight, width=cellWidth, text_color=neutralTxtColor, text_valign=text.align_bottom, text_size=headTextSize, bgcolor=neutralBgColor)

        totalRows: int = this.rows - 1
        for i in pine_range(this.headRows, totalRows if totalRows >= 0 else na):
            table.cell(this.table__ren__, row=i, column=0, height=cellHeight, width=headWidth, text_color=neutralTxtColor, text_halign=text.align_right, text_size=cellTextSize, bgcolor=neutralBgColor)
            __loop_1__ = pine_loop(this.headColumns)
            while __loop_1__.step(this.columns - 1):
                j = __loop_1__.value
                table.cell(this.table__ren__, row=i, column=j, height=cellHeight, width=cellWidth, text_color=neutralTxtColor, text_size=cellTextSize, bgcolor=neutralBgColor)

        for eon, mRow in data.eonToMatrixRow.items():
            tRow: int = matrixToTableRow(this, data.numOfEons, mRow)
            if tRow < this.headRows:
                continue
            table.cell_set_text(this.table__ren__, row=tRow, column=0, text=getEonName(data, eon))

        if this.extended:
            table.cell_set_text(this.table__ren__, row=this.rows - 3, column=0, text='Avg')
            table.cell_set_text(this.table__ren__, row=this.rows - 2, column=0, text='StDev')
            table.cell_set_text(this.table__ren__, row=this.rows - 1, column=0, text='Pos%')

        return this

    @method
    def nonNA(this: list[float]):
        result: int = 0
        for item in this:
            if not na(item):
                result += 1
        return result

    @overload
    @method
    def nonZero(this: list[float]):
        result: int = 0
        for item in this:
            if not na(item) and item != 0.0:
                result += 1
        return result

    @overload
    @method
    def nonZero(this: Matrix[float], fromRow: int = 0):
        result: int = 0
        totalRows: int = matrix.rows(this) - 1
        for r in pine_range(fromRow, totalRows if totalRows > 0 else na):
            result += method_call(nonZero, matrix.row(this, r))
        return result

    @method
    def percentPositive(this: list[float]):
        nonNA__000001a8__: int = 0
        pos: int = 0
        for item in this:
            if not na(item):
                nonNA__000001a8__ += 1
                if item > 0:
                    pos += 1
        return 100.0 * pos / nonNA__000001a8__

    @export
    @overload
    @method
    def update(this: SeasonalTable, data: SeasonalData, positiveTxtColor: Color = color.new('#00D26A'), negativeTxtColor: Color = color.new('#ED2F2D'), neutralTxtColor: Color = chart.fg_color, positiveBgColor: Color = color.new('#00897B0C'), negativeBgColor: Color = color.new('#880E4F0C'), neutralBgColor: Color = color.new('#363A450C'), timeBgColor: Color = color.new('#2D3864')):
        for eon, mRow in data.eonToMatrixRow.items():
            tRow: int = matrixToTableRow(this, data.numOfEons, mRow)
            if tRow < this.headRows:
                continue
            table.cell_set_text(this.table__ren__, row=tRow, column=0, text=getEonName(data, eon))
            mostRecentEonScore: int = (mRow - data.mostRecentMatrixRow + this.eonRows - 1) % this.eonRows
            totalNonZeroSeasonsInEon: int = method_call(nonZero, matrix.row(data.returnPercs, mRow))
            nonZeroSeasonsInEonCount: int = 0
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(matrix.columns(data.returnPercs) - 1):
                mCol = __loop_1__.value
                ret__000001c4__: float = matrix.get(data.returnPercs, row=mRow, column=mCol)
                tCol__000001c4__: int = matrixToTableColumn(this, mCol)
                table.cell_set_tooltip(this.table__ren__, row=tRow, column=tCol__000001c4__, tooltip=string.format('Season/Eon: {0}/{1}\nBalance: {2}\nMaxDD: {3}', getSeasonName(data, mCol), getEonName(data, eon), string.tostring(matrix.get(data.balances, row=mRow, column=mCol), format.volume), string.tostring(matrix.get(data.maxDDs, row=mRow, column=mCol), format.percent)))
                if ret__000001c4__ != 0.0:
                    table.cell_set_text(this.table__ren__, row=tRow, column=tCol__000001c4__, text=('+' if ret__000001c4__ >= 0.0 else '') + string.tostring(ret__000001c4__, format.percent))
                    table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol__000001c4__, text_color=positiveTxtColor if ret__000001c4__ >= 0.0 else negativeTxtColor)
                    table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol__000001c4__, bgcolor=color.new(timeBgColor, 100.0 * (data.numOfEons - mostRecentEonScore - (nonZeroSeasonsInEonCount / (totalNonZeroSeasonsInEon - 1) if totalNonZeroSeasonsInEon > 1 else 0)) / data.numOfEons))
                    nonZeroSeasonsInEonCount += 1
                else:
                    table.cell_set_text(this.table__ren__, row=tRow, column=tCol__000001c4__, text='')
                    table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol__000001c4__, text_color=neutralTxtColor)
                    table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol__000001c4__, bgcolor=neutralBgColor)

            ret: float = array.get(data.eonReturnPercs, mRow)
            tCol: int = this.headColumns + this.seasonColumns
            if ret != 0.0:
                table.cell_set_text(this.table__ren__, row=tRow, column=tCol, text=('+' if ret >= 0.0 else '') + string.tostring(ret, format.percent))
                table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol, text_color=positiveTxtColor if ret >= 0.0 else negativeTxtColor)
                table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol, bgcolor=positiveBgColor if ret >= 0.0 else negativeBgColor)
            else:
                table.cell_set_text(this.table__ren__, row=tRow, column=tCol, text='')
                table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol, text_color=neutralTxtColor)
                table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol, bgcolor=neutralBgColor)

            if this.extended:
                tCol += 1
                cagr: float = array.get(data.eonCAGRs, mRow)
                table.cell_set_text(this.table__ren__, row=tRow, column=tCol, text=('+' if cagr >= 0.0 else '') + string.tostring(cagr, format.percent))
                table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol, text_color=positiveTxtColor if cagr >= 0.0 else negativeTxtColor)
                table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol, bgcolor=positiveBgColor if cagr >= 0.0 else negativeBgColor)
                tCol += 1
                table.cell_set_text(this.table__ren__, row=tRow, column=tCol, text=string.tostring(array.get(data.eonMaxDDs, mRow), format.percent))
                table.cell_set_text_color(this.table__ren__, row=tRow, column=tCol, text_color=negativeTxtColor)
                table.cell_set_bgcolor(this.table__ren__, row=tRow, column=tCol, bgcolor=negativeBgColor)

        __block_result_7__ = na
        if this.extended:
            __block_result_8__ = na
            __loop_1__ = pine_loop(this.headColumns)
            while __loop_1__.step(this.headColumns + this.seasonColumns - 1):
                tCol = __loop_1__.value
                seasonReturnPercs: list[float] = matrix.col(data.returnPercs, tCol - this.headColumns)
                ret: float = array.avg(seasonReturnPercs)
                posPerc: float = percentPositive(seasonReturnPercs)
                table.cell_set_text(this.table__ren__, row=this.rows - 3, column=tCol, text=('+' if ret >= 0.0 else '') + string.tostring(ret, format.percent))
                table.cell_set_text_color(this.table__ren__, row=this.rows - 3, column=tCol, text_color=positiveTxtColor if ret >= 0.0 else negativeTxtColor)
                table.cell_set_bgcolor(this.table__ren__, row=this.rows - 3, column=tCol, bgcolor=positiveBgColor if ret >= 0.0 else negativeBgColor)
                table.cell_set_text(this.table__ren__, row=this.rows - 2, column=tCol, text='±' + string.tostring(array.stdev(seasonReturnPercs, False), '##.##'))
                table.cell_set_text(this.table__ren__, row=this.rows - 1, column=tCol, text=string.tostring(posPerc, '##.#') + '%')
                table.cell_set_text_color(this.table__ren__, row=this.rows - 1, column=tCol, text_color=positiveTxtColor if posPerc > 50.0 else negativeTxtColor if posPerc < 50.0 else neutralTxtColor)
                __block_result_8__ = table.cell_set_bgcolor(this.table__ren__, row=this.rows - 1, column=tCol, bgcolor=positiveBgColor if posPerc > 50.0 else negativeBgColor if posPerc < 50.0 else neutralBgColor)
            __block_result_7__ = __block_result_8__
        return __block_result_7__


    fastMA: float = ta.sma(close, 21)
    slowMA: float = ta.sma(close, 49)

    longStartCondition: bool = ta.crossover(fastMA, slowMA)
    if longStartCondition:
        strategy.entry(id='Long', direction=strategy.long)

    longEndCondition: bool = ta.crossunder(fastMA, slowMA)
    if longEndCondition:
        strategy.close(id='Long')

    firstEntry: Persistent[float] = 0.0
    firstBuyInit: Persistent[bool] = False
    buyAndHoldPerc: Persistent[float] = 0.0

    if showMetricsTable and (not firstBuyInit) and (strategy.opentrades > 0):
        firstEntry = strategy.opentrades.entry_price(0)
        firstBuyInit = True

    if showMetricsTable and strategy.opentrades > 0:
        buyAndHoldPerc = 100.0 * (strategy.closedtrades.exit_price(strategy.closedtrades - 1) - firstEntry) / firstEntry

    SHOW_TABLE: bool = showStatsTable or showMetricsTable or showSeasonalTable

    if SHOW_TABLE:
        statsData: Persistent[StatsData] = StatsData(wins=SideStats(numOf=strategy.wintrades, avgQuantityPerc=strategy.avg_winning_trade), losses=SideStats(numOf=strategy.losstrades, avgQuantityPerc=strategy.avg_losing_trade))
        update(statsData, SideStats(), SideStats(), 0)
        seasonalData: Persistent[SeasonalData] = init(SeasonalData(), seasonalTableSeasonality)

        if showSeasonalTable:
            update(seasonalData)

        if barstate.islastconfirmedhistory or (barstate.isrealtime and barstate.isconfirmed):
            if showStatsTable:
                statsTable: Persistent[StatsTable] = init(StatsTable(), getTablePos(statsTablePosY, statsTablePosX))
                update(statsTable, statsData)

            if showMetricsTable:
                metricsTable: Persistent[MetricsTable] = init(MetricsTable(), getTablePos(metricsTablePosY, metricsTablePosX))
                update(metricsTable, statsData, buyAndHoldPerc)

            if showSeasonalTable:
                seasonalTable: Persistent[SeasonalTable] = init(SeasonalTable(), seasonalData, getTablePos('MIDDLE', 'CENTER'), seasonalTableMaxNumOfYears, 100.0, 100.0, seasonalTableExtend)
                update(seasonalTable, seasonalData)

    if barstate.islastconfirmedhistory:
        log.info('the position is: {0} -> {1} -> {2} -> {3}', position.bottom_center, getTablePos(statsTablePosY, statsTablePosX), getTablePos(metricsTablePosY, metricsTablePosX), getTablePos('MIDDLE', 'CENTER'))

    plot(series=fastMA, title='Fast MA', color=color.yellow, linewidth=1, style=plot.style_line, force_overlay=True)
    plot(series=slowMA, title='Slow MA', color=color.orange, linewidth=1, style=plot.style_line, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
