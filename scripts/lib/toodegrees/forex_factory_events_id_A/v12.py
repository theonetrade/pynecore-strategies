"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import na, script
from typing import Protocol, Any


__all__ = ['ff_titleA']


class _ProtocolFfTitlea(Protocol):
    def __call__(self, ID: str) -> Any: ...


ff_titleA: _ProtocolFfTitlea = Exported()


@script.library("forex_factory_events_id_A")
def main():
    @export
    def ff_titleA(ID: str):
        __block_result__ = na
        __switch__ = ID
        if __switch__ == "1":
            __block_result__ = "1-y Loan Prime Rate"
        elif __switch__ == "2":
            __block_result__ = "10-y Bond Auction"
        elif __switch__ == "3":
            __block_result__ = "30-y Bond Auction"
        elif __switch__ == "4":
            __block_result__ = "5-y Loan Prime Rate"
        elif __switch__ == "5":
            __block_result__ = "ADP Non-Farm Employment Change"
        elif __switch__ == "6":
            __block_result__ = "AIG Construction Index"
        elif __switch__ == "7":
            __block_result__ = "AIG Manufacturing Index"
        elif __switch__ == "8":
            __block_result__ = "AIG Services Index"
        elif __switch__ == "9":
            __block_result__ = "ANZ Business Confidence"
        elif __switch__ == "10":
            __block_result__ = "ANZ Commodity Prices m/m"
        elif __switch__ == "11":
            __block_result__ = "ANZ Job Advertisements m/m"
        elif __switch__ == "12":
            __block_result__ = "Advance GDP Price Index q/q"
        elif __switch__ == "13":
            __block_result__ = "Advance GDP q/q"
        elif __switch__ == "14":
            __block_result__ = "All Industries Activity m/m"
        elif __switch__ == "15":
            __block_result__ = "Annual Budget Release"
        elif __switch__ == "16":
            __block_result__ = "Annual Pre-Budget Report"
        elif __switch__ == "17":
            __block_result__ = "Asset Purchase Facility"
        elif __switch__ == "18":
            __block_result__ = "Assist Treasury Sec Kashkari Speaks"
        elif __switch__ == "19":
            __block_result__ = "Autumn Forecast Statement"
        elif __switch__ == "20":
            __block_result__ = "Average Cash Earnings y/y"
        elif __switch__ == "21":
            __block_result__ = "Average Earnings Index 3m/y"
        elif __switch__ == "22":
            __block_result__ = "Average Hourly Earnings m/m"
        elif __switch__ == "23":
            __block_result__ = "BOC Business Outlook Survey"
        elif __switch__ == "24":
            __block_result__ = "BOC Financial System Review"
        elif __switch__ == "25":
            __block_result__ = "BOC Gov Carney Speaks"
        elif __switch__ == "26":
            __block_result__ = "BOC Gov Macklem Speaks"
        elif __switch__ == "27":
            __block_result__ = "BOC Gov Poloz Speaks"
        elif __switch__ == "28":
            __block_result__ = "BOC Monetary Policy Report"
        elif __switch__ == "29":
            __block_result__ = "BOC Press Conference"
        elif __switch__ == "30":
            __block_result__ = "BOC Rate Statement"
        elif __switch__ == "31":
            __block_result__ = "BOC Review"
        elif __switch__ == "32":
            __block_result__ = "BOC Summary of Deliberations"
        elif __switch__ == "33":
            __block_result__ = "BOE Credit Conditions Survey"
        elif __switch__ == "34":
            __block_result__ = "BOE Financial Stability Report"
        elif __switch__ == "35":
            __block_result__ = "BOE Gov Bailey Speaks"
        elif __switch__ == "36":
            __block_result__ = "BOE Gov Carney Speaks"
        elif __switch__ == "37":
            __block_result__ = "BOE Gov King Speaks"
        elif __switch__ == "38":
            __block_result__ = "BOE Inflation Letter"
        elif __switch__ == "39":
            __block_result__ = "BOE Monetary Policy Report"
        elif __switch__ == "40":
            __block_result__ = "BOE Quarterly Bulletin"
        elif __switch__ == "41":
            __block_result__ = "BOJ Core CPI y/y"
        elif __switch__ == "42":
            __block_result__ = "BOJ Gov Kuroda Speaks"
        elif __switch__ == "43":
            __block_result__ = "BOJ Gov Shirakawa Speaks"
        elif __switch__ == "44":
            __block_result__ = "BOJ Gov Ueda Speaks"
        elif __switch__ == "45":
            __block_result__ = "BOJ Monthly Report"
        elif __switch__ == "46":
            __block_result__ = "BOJ Outlook Report"
        elif __switch__ == "47":
            __block_result__ = "BOJ Policy Rate"
        elif __switch__ == "48":
            __block_result__ = "BOJ Press Conference"
        elif __switch__ == "49":
            __block_result__ = "BOJ Summary of Opinions"
        elif __switch__ == "50":
            __block_result__ = "BRC Retail Sales Monitor y/y"
        elif __switch__ == "51":
            __block_result__ = "BRC Shop Price Index y/y"
        elif __switch__ == "52":
            __block_result__ = "BRICS Summit"
        elif __switch__ == "53":
            __block_result__ = "BSI Manufacturing Index"
        elif __switch__ == "54":
            __block_result__ = "Bank Holiday"
        elif __switch__ == "55":
            __block_result__ = "Bank Lending y/y"
        elif __switch__ == "56":
            __block_result__ = "Bank Stress Test Results"
        elif __switch__ == "57":
            __block_result__ = "Beige Book"
        elif __switch__ == "58":
            __block_result__ = "Belgian NBB Business Climate"
        elif __switch__ == "59":
            __block_result__ = "Building Approvals m/m"
        elif __switch__ == "60":
            __block_result__ = "Building Consents m/m"
        elif __switch__ == "61":
            __block_result__ = "Building Permits"
        elif __switch__ == "62":
            __block_result__ = "Building Permits m/m"
        elif __switch__ == "63":
            __block_result__ = "Business Inventories m/m"
        elif __switch__ == "64":
            __block_result__ = "BusinessNZ Manufacturing Index"
        elif __switch__ == "65":
            __block_result__ = "BusinessNZ Services Index"
        elif __switch__ == "66":
            __block_result__ = "CB Consumer Confidence"
        elif __switch__ == "67":
            __block_result__ = "CB Leading Index m/m"
        elif __switch__ == "68":
            __block_result__ = "CBI Industrial Order Expectations"
        elif __switch__ == "69":
            __block_result__ = "CBI Realized Sales"
        elif __switch__ == "70":
            __block_result__ = "CPI Flash Estimate y/y"
        elif __switch__ == "71":
            __block_result__ = "CPI m/m"
        elif __switch__ == "72":
            __block_result__ = "CPI q/q"
        elif __switch__ == "73":
            __block_result__ = "CPI y/y"
        elif __switch__ == "74":
            __block_result__ = "Caixin Flash Manufacturing PMI"
        elif __switch__ == "75":
            __block_result__ = "Caixin Manufacturing PMI"
        elif __switch__ == "76":
            __block_result__ = "Caixin Services PMI"
        elif __switch__ == "77":
            __block_result__ = "Capacity Utilization Rate"
        elif __switch__ == "78":
            __block_result__ = "Capital Spending q/y"
        elif __switch__ == "79":
            __block_result__ = "Cash Rate"
        elif __switch__ == "80":
            __block_result__ = "Challenger Job Cuts y/y"
        elif __switch__ == "81":
            __block_result__ = "Chancellor Darling Speaks"
        elif __switch__ == "82":
            __block_result__ = "Chancellor Osborne Speaks"
        elif __switch__ == "83":
            __block_result__ = "Chicago PMI"
        elif __switch__ == "84":
            __block_result__ = "Claimant Count Change"
        elif __switch__ == "85":
            __block_result__ = "Cleveland Fed Inflation Expectations"
        elif __switch__ == "86":
            __block_result__ = "Commodity Prices y/y"
        elif __switch__ == "87":
            __block_result__ = "Common CPI y/y"
        elif __switch__ == "88":
            __block_result__ = "Company Operating Profits q/q"
        elif __switch__ == "89":
            __block_result__ = "Congressional Elections"
        elif __switch__ == "90":
            __block_result__ = "Construction Output m/m"
        elif __switch__ == "91":
            __block_result__ = "Construction PMI"
        elif __switch__ == "92":
            __block_result__ = "Construction Spending m/m"
        elif __switch__ == "93":
            __block_result__ = "Construction Work Done q/q"
        elif __switch__ == "94":
            __block_result__ = "Consumer Confidence"
        elif __switch__ == "95":
            __block_result__ = "Consumer Credit m/m"
        elif __switch__ == "96":
            __block_result__ = "Consumer Inflation Expectations"
        elif __switch__ == "97":
            __block_result__ = "Core CPI Flash Estimate y/y"
        elif __switch__ == "98":
            __block_result__ = "Core CPI m/m"
        elif __switch__ == "99":
            __block_result__ = "Core CPI y/y"
        elif __switch__ == "100":
            __block_result__ = "Core Durable Goods Orders m/m"
        elif __switch__ == "101":
            __block_result__ = "Core Machinery Orders m/m"
        elif __switch__ == "102":
            __block_result__ = "Core PCE Price Index m/m"
        elif __switch__ == "103":
            __block_result__ = "Core PPI m/m"
        elif __switch__ == "104":
            __block_result__ = "Core Retail Sales m/m"
        elif __switch__ == "105":
            __block_result__ = "Core Retail Sales q/q"
        elif __switch__ == "106":
            __block_result__ = "Corporate Profits q/q"
        elif __switch__ == "107":
            __block_result__ = "Credit Card Spending y/y"
        elif __switch__ == "108":
            __block_result__ = "Crude Oil Inventories"
        elif __switch__ == "109":
            __block_result__ = "Current Account"
        elif __switch__ == "110":
            __block_result__ = "Daylight Saving Time Shift"
        elif __switch__ == "111":
            __block_result__ = "Doha Oil Summit"
        elif __switch__ == "112":
            __block_result__ = "Durable Goods Orders m/m"
        elif __switch__ == "113":
            __block_result__ = "Dutch Parliamentary Election"
        elif __switch__ == "114":
            __block_result__ = "EBA Bank Stress Test Results"
        elif __switch__ == "115":
            __block_result__ = "ECB Economic Bulletin"
        elif __switch__ == "116":
            __block_result__ = "ECB Financial Stability Review"
        elif __switch__ == "117":
            __block_result__ = "ECB Monetary Policy Meeting Accounts"
        elif __switch__ == "118":
            __block_result__ = "ECB Monthly Bulletin"
        elif __switch__ == "119":
            __block_result__ = "ECB President Draghi Speaks"
        elif __switch__ == "120":
            __block_result__ = "ECB President Lagarde Speaks"
        elif __switch__ == "121":
            __block_result__ = "ECB President Trichet Speaks"
        elif __switch__ == "122":
            __block_result__ = "ECB Press Conference"
        elif __switch__ == "123":
            __block_result__ = "ECOFIN Meetings"
        elif __switch__ == "124":
            __block_result__ = "EU Economic Forecasts"
        elif __switch__ == "125":
            __block_result__ = "EU Economic Summit"
        elif __switch__ == "126":
            __block_result__ = "EU Membership Court Ruling"
        elif __switch__ == "127":
            __block_result__ = "EU Membership Vote"
        elif __switch__ == "128":
            __block_result__ = "Economic Stabilization Bill Vote"
        elif __switch__ == "129":
            __block_result__ = "Economy Watchers Sentiment"
        elif __switch__ == "130":
            __block_result__ = "Empire State Manufacturing Index"
        elif __switch__ == "131":
            __block_result__ = "Employment Change"
        elif __switch__ == "132":
            __block_result__ = "Employment Change q/q"
        elif __switch__ == "133":
            __block_result__ = "Employment Cost Index q/q"
        elif __switch__ == "134":
            __block_result__ = "Employment Level"
        elif __switch__ == "135":
            __block_result__ = "Euro Summit"
        elif __switch__ == "136":
            __block_result__ = "Eurogroup Meetings"
        elif __switch__ == "137":
            __block_result__ = "European Court of Justice Ruling"
        elif __switch__ == "138":
            __block_result__ = "European Parliamentary Elections"
        elif __switch__ == "139":
            __block_result__ = "Existing Home Sales"
        elif __switch__ == "140":
            __block_result__ = "FOMC Economic Projections"
        elif __switch__ == "141":
            __block_result__ = "FOMC Financial Stability Report"
        elif __switch__ == "142":
            __block_result__ = "FOMC Meeting Minutes"
        elif __switch__ == "143":
            __block_result__ = "FOMC Member Barkin Speaks"
        elif __switch__ == "144":
            __block_result__ = "FOMC Member Barr Speaks"
        elif __switch__ == "145":
            __block_result__ = "FOMC Member Bostic Speaks"
        elif __switch__ == "146":
            __block_result__ = "FOMC Member Bowman Speaks"
        elif __switch__ == "147":
            __block_result__ = "FOMC Member Brainard Speaks"
        elif __switch__ == "148":
            __block_result__ = "FOMC Member Bullard Speaks"
        elif __switch__ == "149":
            __block_result__ = "FOMC Member Clarida Speaks"
        elif __switch__ == "150":
            __block_result__ = "FOMC Member Collins Speaks"
        elif __switch__ == "151":
            __block_result__ = "FOMC Member Cook Speaks"
        elif __switch__ == "152":
            __block_result__ = "FOMC Member Daly Speaks"
        elif __switch__ == "153":
            __block_result__ = "FOMC Member Dudley Speaks"
        elif __switch__ == "154":
            __block_result__ = "FOMC Member Duke Speaks"
        elif __switch__ == "155":
            __block_result__ = "FOMC Member Evans Speaks"
        elif __switch__ == "156":
            __block_result__ = "FOMC Member Fischer Speaks"
        elif __switch__ == "157":
            __block_result__ = "FOMC Member Fisher Speaks"
        elif __switch__ == "158":
            __block_result__ = "FOMC Member Geithner Speaks"
        elif __switch__ == "159":
            __block_result__ = "FOMC Member George Speaks"
        elif __switch__ == "160":
            __block_result__ = "FOMC Member Goolsbee Speaks"
        elif __switch__ == "161":
            __block_result__ = "FOMC Member Harker Speaks"
        elif __switch__ == "162":
            __block_result__ = "FOMC Member Hoenig Speaks"
        elif __switch__ == "163":
            __block_result__ = "FOMC Member Jefferson Speaks"
        elif __switch__ == "164":
            __block_result__ = "FOMC Member Kaplan Speaks"
        elif __switch__ == "165":
            __block_result__ = "FOMC Member Kashkari Speaks"
        elif __switch__ == "166":
            __block_result__ = "FOMC Member Kocherlakota Speaks"
        elif __switch__ == "167":
            __block_result__ = "FOMC Member Kohn Speaks"
        elif __switch__ == "168":
            __block_result__ = "FOMC Member Kroszner Speaks"
        elif __switch__ == "169":
            __block_result__ = "FOMC Member Kugler Speaks"
        elif __switch__ == "170":
            __block_result__ = "FOMC Member Lacker Speaks"
        elif __switch__ == "171":
            __block_result__ = "FOMC Member Lockhart Speaks"
        elif __switch__ == "172":
            __block_result__ = "FOMC Member Logan Speaks"
        elif __switch__ == "173":
            __block_result__ = "FOMC Member Mester Speaks"
        elif __switch__ == "174":
            __block_result__ = "FOMC Member Mishkin Speaks"
        elif __switch__ == "175":
            __block_result__ = "FOMC Member Musalem Speaks"
        elif __switch__ == "176":
            __block_result__ = "FOMC Member Pianalto Speaks"
        elif __switch__ == "177":
            __block_result__ = "FOMC Member Plosser Speaks"
        elif __switch__ == "178":
            __block_result__ = "FOMC Member Powell Speaks"
        elif __switch__ == "179":
            __block_result__ = "FOMC Member Quarles Speaks"
        elif __switch__ == "180":
            __block_result__ = "FOMC Member Raskin Speaks"
        elif __switch__ == "181":
            __block_result__ = "FOMC Member Rosengren Speaks"
        elif __switch__ == "182":
            __block_result__ = "FOMC Member Stein Speaks"
        elif __switch__ == "183":
            __block_result__ = "FOMC Member Stern Speaks"
        elif __switch__ == "184":
            __block_result__ = "FOMC Member Tarullo Speaks"
        elif __switch__ == "185":
            __block_result__ = "FOMC Member Waller Speaks"
        elif __switch__ == "186":
            __block_result__ = "FOMC Member Warsh Speaks"
        elif __switch__ == "187":
            __block_result__ = "FOMC Member Williams Speaks"
        elif __switch__ == "188":
            __block_result__ = "FOMC Member Yellen Speaks"
        elif __switch__ == "189":
            __block_result__ = "FOMC Press Conference"
        elif __switch__ == "190":
            __block_result__ = "FOMC Statement"
        elif __switch__ == "191":
            __block_result__ = "FPC Meeting Minutes"
        elif __switch__ == "192":
            __block_result__ = "FPC Statement"
        elif __switch__ == "193":
            __block_result__ = "FPI m/m"
        elif __switch__ == "194":
            __block_result__ = "Factory Orders m/m"
        elif __switch__ == "195":
            __block_result__ = "Fed Announcement"
        elif __switch__ == "196":
            __block_result__ = "Fed Chair Powell Speaks"
        elif __switch__ == "197":
            __block_result__ = "Fed Chair Powell Testifies"
        elif __switch__ == "198":
            __block_result__ = "Fed Chair Yellen Speaks"
        elif __switch__ == "199":
            __block_result__ = "Fed Chair Yellen Testifies"
        elif __switch__ == "200":
            __block_result__ = "Fed Chairman Bernanke Speaks"
        elif __switch__ == "201":
            __block_result__ = "Fed Chairman Bernanke Testifies"
        elif __switch__ == "202":
            __block_result__ = "Fed Chairman Nomination Vote"
        elif __switch__ == "203":
            __block_result__ = "Fed Gov Nomination Hearings"
        elif __switch__ == "204":
            __block_result__ = "Fed Monetary Policy Report"
        elif __switch__ == "205":
            __block_result__ = "Federal Budget Balance"
        elif __switch__ == "206":
            __block_result__ = "Federal Election"
        elif __switch__ == "207":
            __block_result__ = "Federal Funds Rate"
        elif __switch__ == "208":
            __block_result__ = "Final CPI y/y"
        elif __switch__ == "209":
            __block_result__ = "Final Core CPI y/y"
        elif __switch__ == "210":
            __block_result__ = "Final Employment Change q/q"
        elif __switch__ == "211":
            __block_result__ = "Final GDP Price Index q/q"
        elif __switch__ == "212":
            __block_result__ = "Final GDP Price Index y/y"
        elif __switch__ == "213":
            __block_result__ = "Final GDP q/q"
        elif __switch__ == "214":
            __block_result__ = "Final Manufacturing PMI"
        elif __switch__ == "215":
            __block_result__ = "Final Services PMI"
        elif __switch__ == "216":
            __block_result__ = "Final Wholesale Inventories m/m"
        elif __switch__ == "217":
            __block_result__ = "Fixed Asset Investment ytd/y"
        elif __switch__ == "218":
            __block_result__ = "Flash Employment Change q/q"
        elif __switch__ == "219":
            __block_result__ = "Flash GDP q/q"
        elif __switch__ == "220":
            __block_result__ = "Flash Manufacturing PMI"
        elif __switch__ == "221":
            __block_result__ = "Flash Services PMI"
        elif __switch__ == "222":
            __block_result__ = "Foreign Currency Reserves"
        elif __switch__ == "223":
            __block_result__ = "Foreign Direct Investment ytd/y"
        elif __switch__ == "224":
            __block_result__ = "Foreign Securities Purchases"
        elif __switch__ == "225":
            __block_result__ = "French 10-y Bond Auction"
        elif __switch__ == "226":
            __block_result__ = "French Bank Holiday"
        elif __switch__ == "227":
            __block_result__ = "French Consumer Spending m/m"
        elif __switch__ == "228":
            __block_result__ = "French Final CPI m/m"
        elif __switch__ == "229":
            __block_result__ = "French Final Manufacturing PMI"
        elif __switch__ == "230":
            __block_result__ = "French Final Private Payrolls q/q"
        elif __switch__ == "231":
            __block_result__ = "French Final Services PMI"
        elif __switch__ == "232":
            __block_result__ = "French Flash GDP q/q"
        elif __switch__ == "233":
            __block_result__ = "French Flash Manufacturing PMI"
        elif __switch__ == "234":
            __block_result__ = "French Flash Services PMI"
        elif __switch__ == "235":
            __block_result__ = "French Gov Budget Balance"
        elif __switch__ == "236":
            __block_result__ = "French Industrial Production m/m"
        elif __switch__ == "237":
            __block_result__ = "French Parliamentary Elections"
        elif __switch__ == "238":
            __block_result__ = "French Prelim CPI m/m"
        elif __switch__ == "239":
            __block_result__ = "French Prelim GDP q/q"
        elif __switch__ == "240":
            __block_result__ = "French Prelim Private Payrolls q/q"
        elif __switch__ == "241":
            __block_result__ = "French Presidential Election"
        elif __switch__ == "242":
            __block_result__ = "French Trade Balance"
        elif __switch__ == "243":
            __block_result__ = "G20 Meetings"
        elif __switch__ == "244":
            __block_result__ = "G7 Meetings"
        elif __switch__ == "245":
            __block_result__ = "G8 Meetings"
        elif __switch__ == "246":
            __block_result__ = "GDP m/m"
        elif __switch__ == "247":
            __block_result__ = "GDP q/q"
        elif __switch__ == "248":
            __block_result__ = "GDP q/y"
        elif __switch__ == "249":
            __block_result__ = "GDT Price Index"
        elif __switch__ == "250":
            __block_result__ = "German 10-y Bond Auction"
        elif __switch__ == "251":
            __block_result__ = "German 30-y Bond Auction"
        elif __switch__ == "252":
            __block_result__ = "German Bank Holiday"
        elif __switch__ == "253":
            __block_result__ = "German Buba Monthly Report"
        elif __switch__ == "254":
            __block_result__ = "German Buba President Nagel Speaks"
        elif __switch__ == "255":
            __block_result__ = "German Buba President Weber Speaks"
        elif __switch__ == "256":
            __block_result__ = "German Buba President Weidmann Speaks"
        elif __switch__ == "257":
            __block_result__ = "German Constitutional Court Ruling"
        elif __switch__ == "258":
            __block_result__ = "German Factory Orders m/m"
        elif __switch__ == "259":
            __block_result__ = "German Federal Elections"
        elif __switch__ == "260":
            __block_result__ = "German Final CPI m/m"
        elif __switch__ == "261":
            __block_result__ = "German Final GDP q/q"
        elif __switch__ == "262":
            __block_result__ = "German Final Manufacturing PMI"
        elif __switch__ == "263":
            __block_result__ = "German Final Services PMI"
        elif __switch__ == "264":
            __block_result__ = "German Flash Manufacturing PMI"
        elif __switch__ == "265":
            __block_result__ = "German Flash Services PMI"
        elif __switch__ == "266":
            __block_result__ = "German GfK Consumer Climate"
        elif __switch__ == "267":
            __block_result__ = "German Import Prices m/m"
        elif __switch__ == "268":
            __block_result__ = "German Industrial Production m/m"
        elif __switch__ == "269":
            __block_result__ = "German PPI m/m"
        elif __switch__ == "270":
            __block_result__ = "German Prelim CPI m/m"
        elif __switch__ == "271":
            __block_result__ = "German Prelim GDP q/q"
        elif __switch__ == "272":
            __block_result__ = "German Retail Sales m/m"
        elif __switch__ == "273":
            __block_result__ = "German Trade Balance"
        elif __switch__ == "274":
            __block_result__ = "German Unemployment Change"
        elif __switch__ == "275":
            __block_result__ = "German WPI m/m"
        elif __switch__ == "276":
            __block_result__ = "German ZEW Economic Sentiment"
        elif __switch__ == "277":
            __block_result__ = "German ifo Business Climate"
        elif __switch__ == "278":
            __block_result__ = "GfK Consumer Confidence"
        elif __switch__ == "279":
            __block_result__ = "Goods Trade Balance"
        elif __switch__ == "280":
            __block_result__ = "Gov Board Member Danthine Speaks"
        elif __switch__ == "281":
            __block_result__ = "Gov Board Member Hildebrand Speaks"
        elif __switch__ == "282":
            __block_result__ = "Gov Board Member Jordan Speaks"
        elif __switch__ == "283":
            __block_result__ = "Gov Board Member Maechler Speaks"
        elif __switch__ == "284":
            __block_result__ = "Gov Board Member Martin Speaks"
        elif __switch__ == "285":
            __block_result__ = "Gov Board Member Schlegel Speaks"
        elif __switch__ == "286":
            __block_result__ = "Gov Board Member Zurbrugg Speaks"
        elif __switch__ == "287":
            __block_result__ = "Gov Council Member Beaudry Speaks"
        elif __switch__ == "288":
            __block_result__ = "Gov Council Member Boivin Speaks"
        elif __switch__ == "289":
            __block_result__ = "Gov Council Member Cote Speaks"
        elif __switch__ == "290":
            __block_result__ = "Gov Council Member Duguay Speaks"
        elif __switch__ == "291":
            __block_result__ = "Gov Council Member Gravelle Speaks"
        elif __switch__ == "292":
            __block_result__ = "Gov Council Member Jenkins Speaks"
        elif __switch__ == "293":
            __block_result__ = "Gov Council Member Kennedy Speaks"
        elif __switch__ == "294":
            __block_result__ = "Gov Council Member Kozicki Speaks"
        elif __switch__ == "295":
            __block_result__ = "Gov Council Member Lane Speaks"
        elif __switch__ == "296":
            __block_result__ = "Gov Council Member Leduc Speaks"
        elif __switch__ == "297":
            __block_result__ = "Gov Council Member Longworth Speaks"
        elif __switch__ == "298":
            __block_result__ = "Gov Council Member Macklem Speaks"
        elif __switch__ == "299":
            __block_result__ = "Gov Council Member Mendes Speaks"
        elif __switch__ == "300":
            __block_result__ = "Gov Council Member Murray Speaks"
        elif __switch__ == "301":
            __block_result__ = "Gov Council Member Patterson Speaks"
        elif __switch__ == "302":
            __block_result__ = "Gov Council Member Rogers Speaks"
        elif __switch__ == "303":
            __block_result__ = "Gov Council Member Schembri Speaks"
        elif __switch__ == "304":
            __block_result__ = "Gov Council Member Vincent Speaks"
        elif __switch__ == "305":
            __block_result__ = "Gov Council Member Wilkins Speaks"
        elif __switch__ == "306":
            __block_result__ = "Government Spending Review"
        elif __switch__ == "307":
            __block_result__ = "Govt Confidence Vote"
        elif __switch__ == "308":
            __block_result__ = "Greek Bailout Vote"
        elif __switch__ == "309":
            __block_result__ = "Greek Gov Debt Crisis Vote"
        elif __switch__ == "310":
            __block_result__ = "Greek Parliamentary Election"
        elif __switch__ == "311":
            __block_result__ = "Greek Presidential Elections"
        elif __switch__ == "312":
            __block_result__ = "HIA New Home Sales m/m"
        elif __switch__ == "313":
            __block_result__ = "HPI m/m"
        elif __switch__ == "314":
            __block_result__ = "HPI q/q"
        elif __switch__ == "315":
            __block_result__ = "HPI y/y"
        elif __switch__ == "316":
            __block_result__ = "Halifax HPI m/m"
        elif __switch__ == "317":
            __block_result__ = "High Street Lending"
        elif __switch__ == "318":
            __block_result__ = "Home Loans m/m"
        elif __switch__ == "319":
            __block_result__ = "Household Spending y/y"
        elif __switch__ == "320":
            __block_result__ = "Housing Equity Withdrawal q/q"
        elif __switch__ == "321":
            __block_result__ = "Housing Starts"
        elif __switch__ == "322":
            __block_result__ = "Housing Starts q/q"
        elif __switch__ == "323":
            __block_result__ = "Housing Starts y/y"
        elif __switch__ == "324":
            __block_result__ = "IMF Meetings"
        elif __switch__ == "325":
            __block_result__ = "IPPI m/m"
        elif __switch__ == "326":
            __block_result__ = "ISM Manufacturing PMI"
        elif __switch__ == "327":
            __block_result__ = "ISM Manufacturing Prices"
        elif __switch__ == "328":
            __block_result__ = "ISM Services PMI"
        elif __switch__ == "329":
            __block_result__ = "Import Prices m/m"
        elif __switch__ == "330":
            __block_result__ = "Import Prices q/q"
        elif __switch__ == "331":
            __block_result__ = "Index of Services 3m/3m"
        elif __switch__ == "332":
            __block_result__ = "Industrial New Orders m/m"
        elif __switch__ == "333":
            __block_result__ = "Industrial Production m/m"
        elif __switch__ == "334":
            __block_result__ = "Industrial Production q/q"
        elif __switch__ == "335":
            __block_result__ = "Industrial Production y/y"
        elif __switch__ == "336":
            __block_result__ = "Inflation Expectations q/q"
        elif __switch__ == "337":
            __block_result__ = "Irish Lisbon Treaty Vote"
        elif __switch__ == "338":
            __block_result__ = "Irish Stability Treaty Vote"
        elif __switch__ == "339":
            __block_result__ = "Italian 10-y Bond Auction"
        elif __switch__ == "340":
            __block_result__ = "Italian Bank Holiday"
        elif __switch__ == "341":
            __block_result__ = "Italian Constitution Amendment Vote"
        elif __switch__ == "342":
            __block_result__ = "Italian Industrial Production m/m"
        elif __switch__ == "343":
            __block_result__ = "Italian Manufacturing PMI"
        elif __switch__ == "344":
            __block_result__ = "Italian Monthly Unemployment Rate"
        elif __switch__ == "345":
            __block_result__ = "Italian Parliamentary Election"
        elif __switch__ == "346":
            __block_result__ = "Italian Prelim CPI m/m"
        elif __switch__ == "347":
            __block_result__ = "Italian Prelim GDP q/q"
        elif __switch__ == "348":
            __block_result__ = "Italian Quarterly Unemployment Rate"
        elif __switch__ == "349":
            __block_result__ = "Italian Retail Sales m/m"
        elif __switch__ == "350":
            __block_result__ = "Italian Services PMI"
        elif __switch__ == "351":
            __block_result__ = "Italian Trade Balance"
        elif __switch__ == "352":
            __block_result__ = "Ivey PMI"
        elif __switch__ == "353":
            __block_result__ = "JOLTS Job Openings"
        elif __switch__ == "354":
            __block_result__ = "Jackson Hole Symposium"
        elif __switch__ == "355":
            __block_result__ = "Jeddah Oil Summit"
        elif __switch__ == "356":
            __block_result__ = "KOF Economic Barometer"
        elif __switch__ == "357":
            __block_result__ = "Labor Cost Index q/q"
        elif __switch__ == "358":
            __block_result__ = "Labor Market Conditions Index m/m"
        elif __switch__ == "359":
            __block_result__ = "Labor Productivity q/q"
        elif __switch__ == "360":
            __block_result__ = "Leading Index m/m"
        elif __switch__ == "361":
            __block_result__ = "Leading Indicators"
        elif __switch__ == "362":
            __block_result__ = "Libor Rate"
        elif __switch__ == "363":
            __block_result__ = "Loan Officer Survey"
        elif __switch__ == "364":
            __block_result__ = "Long Term Refinancing Operation"
        elif __switch__ == "365":
            __block_result__ = "Lower House Elections"
        elif __switch__ == "366":
            __block_result__ = "M2 Money Stock y/y"
        elif __switch__ == "367":
            __block_result__ = "M2 Money Supply y/y"
        elif __switch__ == "368":
            __block_result__ = "M3 Money Supply y/y"
        elif __switch__ == "369":
            __block_result__ = "M4 Money Supply m/m"
        elif __switch__ == "370":
            __block_result__ = "MI Inflation Expectations"
        elif __switch__ == "371":
            __block_result__ = "MI Inflation Gauge m/m"
        elif __switch__ == "372":
            __block_result__ = "MI Leading Index m/m"
        elif __switch__ == "373":
            __block_result__ = "MPC Asset Purchase Facility Votes"
        elif __switch__ == "374":
            __block_result__ = "MPC Member Barker Speaks"
        elif __switch__ == "375":
            __block_result__ = "MPC Member Bean Speaks"
        elif __switch__ == "376":
            __block_result__ = "MPC Member Besley Speaks"
        elif __switch__ == "377":
            __block_result__ = "MPC Member Blanchflower Speaks"
        elif __switch__ == "378":
            __block_result__ = "MPC Member Breeden Speaks"
        elif __switch__ == "379":
            __block_result__ = "MPC Member Broadbent Speaks"
        elif __switch__ == "380":
            __block_result__ = "MPC Member Cunliffe Speaks"
        elif __switch__ == "381":
            __block_result__ = "MPC Member Dale Speaks"
        elif __switch__ == "382":
            __block_result__ = "MPC Member Dhingra Speaks"
        elif __switch__ == "383":
            __block_result__ = "MPC Member Fisher Speaks"
        elif __switch__ == "384":
            __block_result__ = "MPC Member Forbes Speaks"
        elif __switch__ == "385":
            __block_result__ = "MPC Member Gieve Speaks"
        elif __switch__ == "386":
            __block_result__ = "MPC Member Greene Speaks"
        elif __switch__ == "387":
            __block_result__ = "MPC Member Haldane Speaks"
        elif __switch__ == "388":
            __block_result__ = "MPC Member Haskel Speaks"
        elif __switch__ == "389":
            __block_result__ = "MPC Member Hogg Speaks"
        elif __switch__ == "390":
            __block_result__ = "MPC Member Mann Speaks"
        elif __switch__ == "391":
            __block_result__ = "MPC Member McCafferty Speaks"
        elif __switch__ == "392":
            __block_result__ = "MPC Member Miles Speaks"
        elif __switch__ == "393":
            __block_result__ = "MPC Member Pill Speaks"
        elif __switch__ == "394":
            __block_result__ = "MPC Member Posen Speaks"
        elif __switch__ == "395":
            __block_result__ = "MPC Member Ramsden Speaks"
        elif __switch__ == "396":
            __block_result__ = "MPC Member Saunders Speaks"
        elif __switch__ == "397":
            __block_result__ = "MPC Member Sentance Speaks"
        elif __switch__ == "398":
            __block_result__ = "MPC Member Shafik Speaks"
        elif __switch__ == "399":
            __block_result__ = "MPC Member Tenreyro Speaks"
        elif __switch__ == "400":
            __block_result__ = "MPC Member Tucker Speaks"
        elif __switch__ == "401":
            __block_result__ = "MPC Member Vlieghe Speaks"
        elif __switch__ == "402":
            __block_result__ = "MPC Member Weale Speaks"
        elif __switch__ == "403":
            __block_result__ = "MPC Official Bank Rate Votes"
        elif __switch__ == "404":
            __block_result__ = "MPC Rate Statement"
        elif __switch__ == "405":
            __block_result__ = "Main Refinancing Rate"
        elif __switch__ == "406":
            __block_result__ = "Manufacturing PMI"
        elif __switch__ == "407":
            __block_result__ = "Manufacturing Production m/m"
        elif __switch__ == "408":
            __block_result__ = "Manufacturing Sales m/m"
        elif __switch__ == "409":
            __block_result__ = "Manufacturing Sales q/q"
        elif __switch__ == "410":
            __block_result__ = "Median CPI y/y"
        elif __switch__ == "411":
            __block_result__ = "Mid-Year Economic and Fiscal Outlook"
        elif __switch__ == "412":
            __block_result__ = "Monetary Base y/y"
        elif __switch__ == "413":
            __block_result__ = "Monetary Policy Meeting Minutes"
        elif __switch__ == "414":
            __block_result__ = "Monetary Policy Report Hearings"
        elif __switch__ == "415":
            __block_result__ = "Monetary Policy Statement"
        elif __switch__ == "416":
            __block_result__ = "Monetary Policy Summary"
        elif __switch__ == "417":
            __block_result__ = "Mortgage Approvals"
        elif __switch__ == "418":
            __block_result__ = "Mortgage Delinquencies"
        elif __switch__ == "419":
            __block_result__ = "NAB Business Confidence"
        elif __switch__ == "420":
            __block_result__ = "NAB Quarterly Business Confidence"
        elif __switch__ == "421":
            __block_result__ = "NAHB Housing Market Index"
        elif __switch__ == "422":
            __block_result__ = "NBS Press Conference"
        elif __switch__ == "423":
            __block_result__ = "NFIB Small Business Index"
        elif __switch__ == "424":
            __block_result__ = "NHPI m/m"
        elif __switch__ == "425":
            __block_result__ = "NIESR GDP Estimate"
        elif __switch__ == "426":
            __block_result__ = "NZIER Business Confidence"
        elif __switch__ == "427":
            __block_result__ = "National Core CPI y/y"
        elif __switch__ == "428":
            __block_result__ = "Nationwide Consumer Confidence"
        elif __switch__ == "429":
            __block_result__ = "Nationwide HPI m/m"
        elif __switch__ == "430":
            __block_result__ = "Natural Gas Storage"
        elif __switch__ == "431":
            __block_result__ = "Net Lending to Individuals m/m"
        elif __switch__ == "432":
            __block_result__ = "New Home Prices m/m"
        elif __switch__ == "433":
            __block_result__ = "New Home Sales"
        elif __switch__ == "434":
            __block_result__ = "New Loans"
        elif __switch__ == "435":
            __block_result__ = "New Motor Vehicle Sales m/m"
        elif __switch__ == "436":
            __block_result__ = "Non-Farm Employment Change"
        elif __switch__ == "437":
            __block_result__ = "Non-Manufacturing PMI"
        elif __switch__ == "438":
            __block_result__ = "ONS HPI y/y"
        elif __switch__ == "439":
            __block_result__ = "OPEC Meetings"
        elif __switch__ == "440":
            __block_result__ = "OPEC-JMMC Meetings"
        elif __switch__ == "441":
            __block_result__ = "Official Bank Rate"
        elif __switch__ == "442":
            __block_result__ = "Official Cash Rate"
        elif __switch__ == "443":
            __block_result__ = "Overnight Call Rate"
        elif __switch__ == "444":
            __block_result__ = "Overnight Rate"
        elif __switch__ == "445":
            __block_result__ = "Overseas Trade Index q/q"
        elif __switch__ == "446":
            __block_result__ = "PPI Input m/m"
        elif __switch__ == "447":
            __block_result__ = "PPI Input q/q"
        elif __switch__ == "448":
            __block_result__ = "PPI Output m/m"
        elif __switch__ == "449":
            __block_result__ = "PPI Output q/q"
        elif __switch__ == "450":
            __block_result__ = "PPI m/m"
        elif __switch__ == "451":
            __block_result__ = "PPI q/q"
        elif __switch__ == "452":
            __block_result__ = "PPI y/y"
        elif __switch__ == "453":
            __block_result__ = "Parliament Brexit Vote"
        elif __switch__ == "454":
            __block_result__ = "Parliamentary Elections"
        elif __switch__ == "455":
            __block_result__ = "Pending Home Sales m/m"
        elif __switch__ == "456":
            __block_result__ = "Personal Income m/m"
        elif __switch__ == "457":
            __block_result__ = "Personal Spending m/m"
        elif __switch__ == "458":
            __block_result__ = "Philly Fed Manufacturing Index"
        elif __switch__ == "459":
            __block_result__ = "Prelim ANZ Business Confidence"
        elif __switch__ == "460":
            __block_result__ = "Prelim Business Investment q/q"
        elif __switch__ == "461":
            __block_result__ = "Prelim Flash GDP q/q"
        elif __switch__ == "462":
            __block_result__ = "Prelim GDP Price Index q/q"
        elif __switch__ == "463":
            __block_result__ = "Prelim GDP Price Index y/y"
        elif __switch__ == "464":
            __block_result__ = "Prelim GDP q/q"
        elif __switch__ == "465":
            __block_result__ = "Prelim Industrial Production m/m"
        elif __switch__ == "466":
            __block_result__ = "Prelim Machine Tool Orders y/y"
        elif __switch__ == "467":
            __block_result__ = "Prelim Mortgage Approvals"
        elif __switch__ == "468":
            __block_result__ = "Prelim Nonfarm Productivity q/q"
        elif __switch__ == "469":
            __block_result__ = "Prelim Unit Labor Costs q/q"
        elif __switch__ == "470":
            __block_result__ = "Prelim UoM Consumer Sentiment"
        elif __switch__ == "471":
            __block_result__ = "Prelim UoM Inflation Expectations"
        elif __switch__ == "472":
            __block_result__ = "Prelim Wholesale Inventories m/m"
        elif __switch__ == "473":
            __block_result__ = "President Biden Speaks"
        elif __switch__ == "474":
            __block_result__ = "President Bush Speaks"
        elif __switch__ == "475":
            __block_result__ = "President Obama Speaks"
        elif __switch__ == "476":
            __block_result__ = "President Trump Speaks"
        elif __switch__ == "477":
            __block_result__ = "Presidential Election"
        elif __switch__ == "478":
            __block_result__ = "Prime Minister Johnson Speaks"
        elif __switch__ == "479":
            __block_result__ = "Prime Minister May Speaks"
        elif __switch__ == "480":
            __block_result__ = "Prime Minister Truss Speaks"
        elif __switch__ == "481":
            __block_result__ = "Private Capital Expenditure q/q"
        elif __switch__ == "482":
            __block_result__ = "Private Loans y/y"
        elif __switch__ == "483":
            __block_result__ = "Private Sector Credit m/m"
        elif __switch__ == "484":
            __block_result__ = "Public Sector Net Borrowing"
        elif __switch__ == "485":
            __block_result__ = "Quarterly Retail Sales q/q"
        elif __switch__ == "486":
            __block_result__ = "RBA Annual Report"
        elif __switch__ == "487":
            __block_result__ = "RBA Assist Gov Edey Speaks"
        elif __switch__ == "488":
            __block_result__ = "RBA Assist Gov Ellis Speaks"
        elif __switch__ == "489":
            __block_result__ = "RBA Assist Gov Hunter Speaks"
        elif __switch__ == "490":
            __block_result__ = "RBA Assist Gov Kent Speaks"
        elif __switch__ == "491":
            __block_result__ = "RBA Bulletin"
        elif __switch__ == "492":
            __block_result__ = "RBA Deputy Gov Battellino Speaks"
        elif __switch__ == "493":
            __block_result__ = "RBA Deputy Gov Debelle Speaks"
        elif __switch__ == "494":
            __block_result__ = "RBA Deputy Gov Hauser Speaks"
        elif __switch__ == "495":
            __block_result__ = "RBA Deputy Gov Lowe Speaks"
        elif __switch__ == "496":
            __block_result__ = "RBA Financial Stability Review"
        elif __switch__ == "497":
            __block_result__ = "RBA Gov Bullock Speaks"
        elif __switch__ == "498":
            __block_result__ = "RBA Gov Lowe Speaks"
        TITLE = __block_result__
        return TITLE


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
