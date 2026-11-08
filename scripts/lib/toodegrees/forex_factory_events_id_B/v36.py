"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import na, script
from typing import Protocol, Any


__all__ = ['ff_titleB']


class _ProtocolFfTitleb(Protocol):
    def __call__(self, ID: str) -> Any: ...


ff_titleB: _ProtocolFfTitleb = Exported()


@script.library("forex_factory_events_id_B")
def main():
    @export
    def ff_titleB(ID: str):
        __block_result__ = na
        __switch__ = ID
        if __switch__ == "499":
            __block_result__ = "RBA Gov Stevens Speaks"
        elif __switch__ == "500":
            __block_result__ = "RBA Monetary Policy Statement"
        elif __switch__ == "501":
            __block_result__ = "RBA Press Conference"
        elif __switch__ == "502":
            __block_result__ = "RBA Rate Statement"
        elif __switch__ == "503":
            __block_result__ = "RBNZ Assist Gov McDermott Speaks"
        elif __switch__ == "504":
            __block_result__ = "RBNZ Financial Stability Report"
        elif __switch__ == "505":
            __block_result__ = "RBNZ Gov Bollard Speaks"
        elif __switch__ == "506":
            __block_result__ = "RBNZ Gov Orr Speaks"
        elif __switch__ == "507":
            __block_result__ = "RBNZ Gov Spencer Speaks"
        elif __switch__ == "508":
            __block_result__ = "RBNZ Gov Wheeler Speaks"
        elif __switch__ == "509":
            __block_result__ = "RBNZ Monetary Policy Statement"
        elif __switch__ == "510":
            __block_result__ = "RBNZ Press Conference"
        elif __switch__ == "511":
            __block_result__ = "RBNZ Rate Statement"
        elif __switch__ == "512":
            __block_result__ = "RBNZ Statement of Intent"
        elif __switch__ == "513":
            __block_result__ = "RCM/TIPP Economic Optimism"
        elif __switch__ == "514":
            __block_result__ = "REINZ HPI m/m"
        elif __switch__ == "515":
            __block_result__ = "RICS House Price Balance"
        elif __switch__ == "516":
            __block_result__ = "RMPI m/m"
        elif __switch__ == "517":
            __block_result__ = "RPI y/y"
        elif __switch__ == "518":
            __block_result__ = "Retail PMI"
        elif __switch__ == "519":
            __block_result__ = "Retail Sales m/m"
        elif __switch__ == "520":
            __block_result__ = "Retail Sales q/q"
        elif __switch__ == "521":
            __block_result__ = "Retail Sales y/y"
        elif __switch__ == "522":
            __block_result__ = "Revised Business Investment q/q"
        elif __switch__ == "523":
            __block_result__ = "Revised GDP q/q"
        elif __switch__ == "524":
            __block_result__ = "Revised Industrial Production m/m"
        elif __switch__ == "525":
            __block_result__ = "Revised Nonfarm Productivity q/q"
        elif __switch__ == "526":
            __block_result__ = "Revised Unit Labor Costs q/q"
        elif __switch__ == "527":
            __block_result__ = "Revised UoM Consumer Sentiment"
        elif __switch__ == "528":
            __block_result__ = "Revised UoM Inflation Expectations"
        elif __switch__ == "529":
            __block_result__ = "Richmond Manufacturing Index"
        elif __switch__ == "530":
            __block_result__ = "Rightmove HPI m/m"
        elif __switch__ == "531":
            __block_result__ = "S&P/CS Composite-20 HPI y/y"
        elif __switch__ == "532":
            __block_result__ = "SECO Consumer Climate"
        elif __switch__ == "533":
            __block_result__ = "SECO Economic Forecasts"
        elif __switch__ == "534":
            __block_result__ = "SNB Chairman Hildebrand Speaks"
        elif __switch__ == "535":
            __block_result__ = "SNB Chairman Jordan Speaks"
        elif __switch__ == "536":
            __block_result__ = "SNB Chairman Roth Speaks"
        elif __switch__ == "537":
            __block_result__ = "SNB Financial Stability Report"
        elif __switch__ == "538":
            __block_result__ = "SNB Monetary Policy Assessment"
        elif __switch__ == "539":
            __block_result__ = "SNB Policy Rate"
        elif __switch__ == "540":
            __block_result__ = "SNB Press Conference"
        elif __switch__ == "541":
            __block_result__ = "SNB Quarterly Bulletin"
        elif __switch__ == "542":
            __block_result__ = "SPPI y/y"
        elif __switch__ == "543":
            __block_result__ = "Second Estimate GDP q/q"
        elif __switch__ == "544":
            __block_result__ = "Sentix Investor Confidence"
        elif __switch__ == "545":
            __block_result__ = "Spanish 10-y Bond Auction"
        elif __switch__ == "546":
            __block_result__ = "Spanish Flash CPI y/y"
        elif __switch__ == "547":
            __block_result__ = "Spanish Flash GDP q/q"
        elif __switch__ == "548":
            __block_result__ = "Spanish Manufacturing PMI"
        elif __switch__ == "549":
            __block_result__ = "Spanish Parliamentary Election"
        elif __switch__ == "550":
            __block_result__ = "Spanish Services PMI"
        elif __switch__ == "551":
            __block_result__ = "Spanish Unemployment Change"
        elif __switch__ == "552":
            __block_result__ = "Spanish Unemployment Rate"
        elif __switch__ == "553":
            __block_result__ = "Stimulus Package Announcement"
        elif __switch__ == "554":
            __block_result__ = "TIC Long-Term Purchases"
        elif __switch__ == "555":
            __block_result__ = "Tankan Manufacturing Index"
        elif __switch__ == "556":
            __block_result__ = "Tankan Non-Manufacturing Index"
        elif __switch__ == "557":
            __block_result__ = "Tertiary Industry Activity m/m"
        elif __switch__ == "558":
            __block_result__ = "Tokyo Core CPI y/y"
        elif __switch__ == "559":
            __block_result__ = "Total Vehicle Sales"
        elif __switch__ == "560":
            __block_result__ = "Trade Balance"
        elif __switch__ == "561":
            __block_result__ = "Treasury Currency Report"
        elif __switch__ == "562":
            __block_result__ = "Treasury Sec Geithner Speaks"
        elif __switch__ == "563":
            __block_result__ = "Treasury Sec Lew Speaks"
        elif __switch__ == "564":
            __block_result__ = "Treasury Sec Mnuchin Speaks"
        elif __switch__ == "565":
            __block_result__ = "Treasury Sec Paulson Speaks"
        elif __switch__ == "566":
            __block_result__ = "Treasury Sec Yellen Speaks"
        elif __switch__ == "567":
            __block_result__ = "Trimmed CPI y/y"
        elif __switch__ == "568":
            __block_result__ = "Trimmed Mean CPI q/q"
        elif __switch__ == "569":
            __block_result__ = "UBS Consumption Indicator"
        elif __switch__ == "570":
            __block_result__ = "UBS Economic Expectations"
        elif __switch__ == "571":
            __block_result__ = "USD-Denominated Trade Balance"
        elif __switch__ == "572":
            __block_result__ = "Unconditional Basic Income Vote"
        elif __switch__ == "573":
            __block_result__ = "Unemployment Claims"
        elif __switch__ == "574":
            __block_result__ = "Unemployment Rate"
        elif __switch__ == "575":
            __block_result__ = "Upper House Elections"
        elif __switch__ == "576":
            __block_result__ = "Visitor Arrivals m/m"
        elif __switch__ == "577":
            __block_result__ = "WEF Annual Meetings"
        elif __switch__ == "578":
            __block_result__ = "Wage Price Index q/q"
        elif __switch__ == "579":
            __block_result__ = "Wards Total Vehicle Sales"
        elif __switch__ == "580":
            __block_result__ = "Westpac Consumer Sentiment"
        elif __switch__ == "581":
            __block_result__ = "Wholesale Sales m/m"
        elif __switch__ == "582":
            __block_result__ = "ZEW Economic Sentiment"
        elif __switch__ == "583":
            __block_result__ = "FOMC Member Hammack Speaks"
        elif __switch__ == "584":
            __block_result__ = "SNB Chairman Schlegel Speaks"
        elif __switch__ == "585":
            __block_result__ = "FOMC Member Schmid Speaks"
        elif __switch__ == "586":
            __block_result__ = "Gov Board Member Tschudin Speaks"
        elif __switch__ == "587":
            __block_result__ = "MPC Member Lombardelli Speaks"
        elif __switch__ == "588":
            __block_result__ = "MPC Member Taylor Speaks"
        elif __switch__ == "589":
            __block_result__ = "API Weekly Statistical Bulletin"
        elif __switch__ == "590":
            __block_result__ = "RBNZ Gov Hawkesby Speaks"
        elif __switch__ == "591":
            __block_result__ = "RatingDog Manufacturing PMI"
        elif __switch__ == "592":
            __block_result__ = "RatingDog Services PMI"
        elif __switch__ == "593":
            __block_result__ = "RBA Assist Gov Jones Speaks"
        elif __switch__ == "594":
            __block_result__ = "FOMC Member Miran Speaks"
        elif __switch__ == "595":
            __block_result__ = "Household Spending m/m"
        elif __switch__ == "596":
            __block_result__ = "FOMC Member Paulson Speaks"
        elif __switch__ == "597":
            __block_result__ = "Summary of Monetary Policy Discussions"
        elif __switch__ == "599":
            __block_result__ = "RBNZ Gov Breman Speaks"
        elif __switch__ == "600":
            __block_result__ = "ADP Weekly Employment Change"
        elif __switch__ == "601":
            __block_result__ = "Trimmed Mean CPI m/m"
        elif __switch__ == "602":
            __block_result__ = "Fed Chair-Designate Warsh Testifies"
        elif __switch__ == "603":
            __block_result__ = "Fed Chair-Designate Warsh Testifies"
        elif __switch__ == "604":
            __block_result__ = "Gov Council Member Alexopoulos Speaks"
        elif __switch__ == "605":
            __block_result__ = "Treasury Sec Bessent Speaks"
        elif __switch__ == "606":
            __block_result__ = "Fed Chairman Warsh Testifies"
        elif __switch__ == "607":
            __block_result__ = "Omdia Total Vehicle Sales"
        elif __switch__ == "608":
            __block_result__ = "Lloyds HPI m/m"
        elif __switch__ == "609":
            __block_result__ = "Fed Chairman Warsh Speaks"
        elif __switch__ == "610":
            __block_result__ = "Prelim Benchmark Payrolls Revision"
        else:
            __block_result__ = "Check forexfactory.com for more information!"
        return __block_result__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
