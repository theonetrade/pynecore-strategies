"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    barstate, close, map, na, nz, plot, request, runtime, script, string,
    syminfo, ta, timeframe
)
from pynecore.types import Persistent
from typing import Protocol, Any


__all__ = ['COTTickerid', 'convertRootToCOTCode', 'requestCommitmentOfTraders']


class _ProtocolConvertroottocotcode(Protocol):
    def __call__(self, mode: str, convertToCOT: bool = True) -> Any: ...


class _ProtocolCottickerid(Protocol):
    def __call__(self, COTType: str, CFTCCode: str, includeOptions: bool, metricName: str, metricDirection: str, metricType: str) -> Any: ...


class _ProtocolRequestcommitmentoftraders(Protocol):
    def __call__(self, COTType: str, CFTCCode: str, includeOptions: bool, metricName: str, metricDirection: str, metricType: str) -> Any: ...


convertRootToCOTCode: _ProtocolConvertroottocotcode = Exported()
COTTickerid: _ProtocolCottickerid = Exported()
requestCommitmentOfTraders: _ProtocolRequestcommitmentoftraders = Exported()


@script.library('LibraryCOT', overlay=False, dynamic_requests=True)
def main():
    def isNotEmpty(str__ren__: str):
        result: bool = str__ren__ != ''
        return result

    def createRootCodeMap():
        rootCodeMap: dict[str, str] = map.new()
        map.put(rootCodeMap, 'AMB1', '1450E1')
        map.put(rootCodeMap, 'AMT1', '1450E4')
        map.put(rootCodeMap, 'VM', '1170E8')
        map.put(rootCodeMap, 'VXM', '1170E8')
        map.put(rootCodeMap, 'IBHY', '2520E1')
        map.put(rootCodeMap, 'IBIG', '2520E2')
        map.put(rootCodeMap, 'VX', '1170E1')
        map.put(rootCodeMap, 'VX10', '117E10')
        map.put(rootCodeMap, 'VX11', '117E11')
        map.put(rootCodeMap, 'VX13', '117E13')
        map.put(rootCodeMap, 'VX14', '117E14')
        map.put(rootCodeMap, 'VX15', '117E15')
        map.put(rootCodeMap, 'VX17', '117E17')
        map.put(rootCodeMap, 'VX18', '117E18')
        map.put(rootCodeMap, 'VX19', '117E19')
        map.put(rootCodeMap, 'VX21', '117E21')
        map.put(rootCodeMap, 'VX22', '117E22')
        map.put(rootCodeMap, 'VX23', '117E23')
        map.put(rootCodeMap, 'VX24', '117E24')
        map.put(rootCodeMap, 'VX26', '117E26')
        map.put(rootCodeMap, 'VX27', '117E27')
        map.put(rootCodeMap, 'VX28', '117E28')
        map.put(rootCodeMap, 'VX30', '117E30')
        map.put(rootCodeMap, 'VX31', '117E31')
        map.put(rootCodeMap, 'VX32', '117E32')
        map.put(rootCodeMap, 'VX34', '117E34')
        map.put(rootCodeMap, 'VX35', '117E35')
        map.put(rootCodeMap, 'VX36', '117E36')
        map.put(rootCodeMap, 'VX37', '117E37')
        map.put(rootCodeMap, 'VX39', '117E39')
        map.put(rootCodeMap, 'VX40', '117E40')
        map.put(rootCodeMap, 'VX41', '117E41')
        map.put(rootCodeMap, 'VX43', '117E43')
        map.put(rootCodeMap, 'VX09', '117E09')
        map.put(rootCodeMap, 'YIA', '342602')
        map.put(rootCodeMap, 'YIY', '343603')
        map.put(rootCodeMap, 'N1S', '343604')
        map.put(rootCodeMap, 'YIT', '342603')
        map.put(rootCodeMap, 'TWE', '020605')
        map.put(rootCodeMap, 'YIC', '344606')
        map.put(rootCodeMap, 'YIE', '320604')
        map.put(rootCodeMap, '25U', '046603')
        map.put(rootCodeMap, '30U', '046604')
        map.put(rootCodeMap, '35U', '046605')
        map.put(rootCodeMap, '40U', '046606')
        map.put(rootCodeMap, '45U', '046607')
        map.put(rootCodeMap, '50U', '046608')
        map.put(rootCodeMap, '55U', '046609')
        map.put(rootCodeMap, '60U', '046610')
        map.put(rootCodeMap, 'YID', '344604')
        map.put(rootCodeMap, 'YIW', '344605')
        map.put(rootCodeMap, 'F1S', '344615')
        map.put(rootCodeMap, 'YIB', '344607')
        map.put(rootCodeMap, 'BWF', '00160F')
        map.put(rootCodeMap, 'AW', '221602')
        map.put(rootCodeMap, 'DRS', '221604')
        map.put(rootCodeMap, 'CWR', '00160D')
        map.put(rootCodeMap, 'ZC', '002602')
        map.put(rootCodeMap, 'DFN', '251605')
        map.put(rootCodeMap, 'YM', '124603')
        map.put(rootCodeMap, 'RX', '124606')
        map.put(rootCodeMap, 'SAS', '005609')
        map.put(rootCodeMap, '10Y', '04360Y')
        map.put(rootCodeMap, '2YY', '04260Y')
        map.put(rootCodeMap, '30Y', '02060Y')
        map.put(rootCodeMap, '5YY', '04460Y')
        map.put(rootCodeMap, 'MYM', '124608')
        map.put(rootCodeMap, 'XC', '002603')
        map.put(rootCodeMap, 'XK', '005603')
        map.put(rootCodeMap, 'XW', '001603')
        map.put(rootCodeMap, 'ZO', '004603')
        map.put(rootCodeMap, 'ZR', '039601')
        map.put(rootCodeMap, 'ZM', '026603')
        map.put(rootCodeMap, 'ZL', '007601')
        map.put(rootCodeMap, 'ZS', '005602')
        map.put(rootCodeMap, 'ZB', '020601')
        map.put(rootCodeMap, 'UNO', '251609')
        map.put(rootCodeMap, 'TN', '043607')
        map.put(rootCodeMap, 'UB', '020604')
        map.put(rootCodeMap, 'UFB', '251604')
        map.put(rootCodeMap, 'UFE', '251606')
        map.put(rootCodeMap, 'UME', '251603')
        map.put(rootCodeMap, 'UFV', '251607')
        map.put(rootCodeMap, 'ZW', '001602')
        map.put(rootCodeMap, 'ZQ', '045601')
        map.put(rootCodeMap, 'ZN', '043602')
        map.put(rootCodeMap, 'ZF', '044601')
        map.put(rootCodeMap, 'Z3N', '038601')
        map.put(rootCodeMap, 'KE', '001612')
        map.put(rootCodeMap, 'ZT', '042601')
        map.put(rootCodeMap, 'SR1', '134742')
        map.put(rootCodeMap, 'SR3', '134741')
        map.put(rootCodeMap, 'AQR', '209748')
        map.put(rootCodeMap, 'A2R', '239749')
        map.put(rootCodeMap, 'ASR', '13874W')
        map.put(rootCodeMap, 'D2', '17564H')
        map.put(rootCodeMap, 'D2X', '16S063')
        map.put(rootCodeMap, 'K1', '16064C')
        map.put(rootCodeMap, 'H1', '16064H')
        map.put(rootCodeMap, 'K1K', '16S023')
        map.put(rootCodeMap, 'H1X', '16S056')
        map.put(rootCodeMap, 'ACD', '432741')
        map.put(rootCodeMap, 'AJY', '632741')
        map.put(rootCodeMap, 'ANE', '532741')
        map.put(rootCodeMap, '6A', '232741')
        map.put(rootCodeMap, 'BTC', '133741')
        map.put(rootCodeMap, 'BLK', '063643')
        map.put(rootCodeMap, 'KW', '17064C')
        map.put(rootCodeMap, 'HWX', '16S061')
        map.put(rootCodeMap, '6L', '102741')
        map.put(rootCodeMap, '6B', '096742')
        map.put(rootCodeMap, '6C', '090741')
        map.put(rootCodeMap, 'CJY', '190741')
        map.put(rootCodeMap, 'CB', '050642')
        map.put(rootCodeMap, 'CSC', '063642')
        map.put(rootCodeMap, 'K2N', '16S183')
        map.put(rootCodeMap, 'K2K', '16S186')
        map.put(rootCodeMap, 'K2', '16164C')
        map.put(rootCodeMap, 'H2', '16164H')
        map.put(rootCodeMap, 'H2X', '16S042')
        map.put(rootCodeMap, 'CHP', '279742')
        map.put(rootCodeMap, 'K3', '16364C')
        map.put(rootCodeMap, 'K3K', '16364D')
        map.put(rootCodeMap, 'K3N', '163K3N')
        map.put(rootCodeMap, 'H3', '16364H')
        map.put(rootCodeMap, 'H3Z', '16S002')
        map.put(rootCodeMap, 'H3X', '16S050')
        map.put(rootCodeMap, 'GDK', '052644')
        map.put(rootCodeMap, 'BOS', '20074A')
        map.put(rootCodeMap, 'CHI', '20074B')
        map.put(rootCodeMap, 'CUS', '20074K')
        map.put(rootCodeMap, 'DEN', '20074C')
        map.put(rootCodeMap, 'LAV', '20074D')
        map.put(rootCodeMap, 'LAX', '20074E')
        map.put(rootCodeMap, 'MIA', '20074F')
        map.put(rootCodeMap, 'NYM', '20074G')
        map.put(rootCodeMap, 'SDG', '20074H')
        map.put(rootCodeMap, 'SFR', '20074I')
        map.put(rootCodeMap, 'WDC', '20074J')
        map.put(rootCodeMap, 'CZK', '275741')
        map.put(rootCodeMap, 'K5', '16464C')
        map.put(rootCodeMap, 'H5', '16464H')
        map.put(rootCodeMap, 'K5N', '16S045')
        map.put(rootCodeMap, 'K5K', '16S016')
        map.put(rootCodeMap, 'H5X', '16S053')
        map.put(rootCodeMap, 'DY', '052645')
        map.put(rootCodeMap, 'M6A', '232742')
        map.put(rootCodeMap, 'M6B', '096746')
        map.put(rootCodeMap, 'MCD', '090744')
        map.put(rootCodeMap, 'M6E', '099743')
        map.put(rootCodeMap, 'MSF', '092744')
        map.put(rootCodeMap, 'M6J', '097745')
        map.put(rootCodeMap, 'M6C', '090747')
        map.put(rootCodeMap, 'M6S', '092748')
        map.put(rootCodeMap, 'E7', '099742')
        map.put(rootCodeMap, 'IPO', '164741')
        map.put(rootCodeMap, 'J7', '097744')
        map.put(rootCodeMap, 'NIY', '240745')
        map.put(rootCodeMap, 'SOX', '13874Y')
        map.put(rootCodeMap, 'RSV', '239744')
        map.put(rootCodeMap, 'RSG', '239745')
        map.put(rootCodeMap, 'RS1', '239743')
        map.put(rootCodeMap, 'R2V', '239746')
        map.put(rootCodeMap, 'R2G', '239748')
        map.put(rootCodeMap, 'RTY', '239742')
        map.put(rootCodeMap, 'EMD', '33874A')
        map.put(rootCodeMap, 'ESG', '13874S')
        map.put(rootCodeMap, 'ES', '13874A')
        map.put(rootCodeMap, 'SXT', '13874Z')
        map.put(rootCodeMap, 'E3G', '13874X')
        map.put(rootCodeMap, 'SXO', '138743')
        map.put(rootCodeMap, 'XAR', '13874R')
        map.put(rootCodeMap, 'SXB', '138752')
        map.put(rootCodeMap, 'SXR', '138751')
        map.put(rootCodeMap, 'XAZ', '13874P')
        map.put(rootCodeMap, 'XAY', '138747')
        map.put(rootCodeMap, 'XAP', '138748')
        map.put(rootCodeMap, 'XAE', '138749')
        map.put(rootCodeMap, 'XAF', '13874C')
        map.put(rootCodeMap, 'XAV', '13874E')
        map.put(rootCodeMap, 'XAI', '13874F')
        map.put(rootCodeMap, 'SXI', '138753')
        map.put(rootCodeMap, 'XAB', '13874H')
        map.put(rootCodeMap, 'XAK', '13874I')
        map.put(rootCodeMap, 'XAU', '13874J')
        map.put(rootCodeMap, 'SMC', '338742')
        map.put(rootCodeMap, 'D4X', '16042I')
        map.put(rootCodeMap, 'EBR', '133744')
        map.put(rootCodeMap, 'ETH', '146021')
        map.put(rootCodeMap, 'EAD', '199741')
        map.put(rootCodeMap, 'ECD', '699741')
        map.put(rootCodeMap, 'RY', '399741')
        map.put(rootCodeMap, 'ENK', '799741')
        map.put(rootCodeMap, 'ESK', '899741')
        map.put(rootCodeMap, 'RF', '499741')
        map.put(rootCodeMap, '6E', '099741')
        map.put(rootCodeMap, 'RP', '299741')
        map.put(rootCodeMap, 'ESR', '047745')
        map.put(rootCodeMap, 'EUS', '598742')
        map.put(rootCodeMap, 'ECK', '275742')
        map.put(rootCodeMap, 'EPZ', '277742')
        map.put(rootCodeMap, 'GF', '061641')
        map.put(rootCodeMap, 'HUF', '274741')
        map.put(rootCodeMap, 'EHF', '274743')
        map.put(rootCodeMap, 'SIR', '131741')
        map.put(rootCodeMap, 'MIR', '131742')
        map.put(rootCodeMap, 'ISL', '278741')
        map.put(rootCodeMap, '6J', '097741')
        map.put(rootCodeMap, 'KRW', '086741')
        map.put(rootCodeMap, 'K0', '16964C')
        map.put(rootCodeMap, 'H0', '16964H')
        map.put(rootCodeMap, 'K0K', '16S025')
        map.put(rootCodeMap, 'H0X', '16S189')
        map.put(rootCodeMap, 'HE', '054642')
        map.put(rootCodeMap, 'LE', '057642')
        map.put(rootCodeMap, 'D0X', '16S039')
        map.put(rootCodeMap, 'LBR', '058644')
        map.put(rootCodeMap, 'TIE', '134743')
        map.put(rootCodeMap, '6M', '095741')
        map.put(rootCodeMap, 'MBT', '133742')
        map.put(rootCodeMap, 'MNQ', '209747')
        map.put(rootCodeMap, 'M2K', '239747')
        map.put(rootCodeMap, 'MMC', '33874B')
        map.put(rootCodeMap, 'MES', '13874U')
        map.put(rootCodeMap, 'MSC', '338744')
        map.put(rootCodeMap, 'MET', '146022')
        map.put(rootCodeMap, 'DC', '052641')
        map.put(rootCodeMap, 'JQ', '052648')
        map.put(rootCodeMap, 'KQK', '17364D')
        map.put(rootCodeMap, 'HQX', '16S052')
        map.put(rootCodeMap, 'BIO', '209744')
        map.put(rootCodeMap, 'H2O', '147641')
        map.put(rootCodeMap, 'NDA', '438741')
        map.put(rootCodeMap, 'NQ', '209742')
        map.put(rootCodeMap, 'VLQ', '117742')
        map.put(rootCodeMap, 'K4', '16264C')
        map.put(rootCodeMap, 'H4', '16264H')
        map.put(rootCodeMap, 'H4Z', '16S003')
        map.put(rootCodeMap, 'K4N', '16S181')
        map.put(rootCodeMap, 'K4K', '16S018')
        map.put(rootCodeMap, 'H4X', '16S041')
        map.put(rootCodeMap, '6N', '112741')
        map.put(rootCodeMap, 'NKD', '240741')
        map.put(rootCodeMap, 'ENY', '240743')
        map.put(rootCodeMap, 'GNF', '052642')
        map.put(rootCodeMap, 'NOK', '273741')
        map.put(rootCodeMap, 'K6', '16564C')
        map.put(rootCodeMap, 'H6Z', '16S168')
        map.put(rootCodeMap, 'PLN', '277741')
        map.put(rootCodeMap, 'PRK', '054643')
        map.put(rootCodeMap, 'K7K', '16S185')
        map.put(rootCodeMap, 'K7', '16664C')
        map.put(rootCodeMap, 'H7X', '16S059')
        map.put(rootCodeMap, 'PSF', '296741')
        map.put(rootCodeMap, 'PJY', '396741')
        map.put(rootCodeMap, 'SON', '047743')
        map.put(rootCodeMap, 'RDA', '239750')
        map.put(rootCodeMap, 'SDA', '43874A')
        map.put(rootCodeMap, 'SDI', '43874Q')
        map.put(rootCodeMap, 'TRI', '13874N')
        map.put(rootCodeMap, 'GD', '256741')
        map.put(rootCodeMap, 'GIE', '256742')
        map.put(rootCodeMap, 'KS', '17464C')
        map.put(rootCodeMap, 'KSN', '16S187')
        map.put(rootCodeMap, 'HSX', '16S188')
        map.put(rootCodeMap, '6Z', '122741')
        map.put(rootCodeMap, 'ZAR', '122742')
        map.put(rootCodeMap, 'SEK', '264741')
        map.put(rootCodeMap, '6S', '092741')
        map.put(rootCodeMap, 'SJY', '192741')
        map.put(rootCodeMap, 'BSB', '157741')
        map.put(rootCodeMap, 'TPD', '241740')
        map.put(rootCodeMap, 'TRL', '019743')
        map.put(rootCodeMap, 'IBV', '130741')
        map.put(rootCodeMap, 'CPO', '037021')
        map.put(rootCodeMap, 'RMB', '082744')
        map.put(rootCodeMap, 'TPY', '243742')
        map.put(rootCodeMap, 'ALA', '191698')
        map.put(rootCodeMap, 'EDP', '191696')
        map.put(rootCodeMap, 'AEP', '191694')
        map.put(rootCodeMap, 'MJP', '191695')
        map.put(rootCodeMap, 'ALI', '191691')
        map.put(rootCodeMap, 'AUP', '191693')
        map.put(rootCodeMap, 'COB', '188691')
        map.put(rootCodeMap, 'HG', '085692')
        map.put(rootCodeMap, 'HGS', '085695')
        map.put(rootCodeMap, 'QC', '085693')
        map.put(rootCodeMap, 'GC', '088691')
        map.put(rootCodeMap, 'FSF', '257651')
        map.put(rootCodeMap, 'TIO', '195651')
        map.put(rootCodeMap, 'PAC', '195656')
        map.put(rootCodeMap, 'LTC', '189692')
        map.put(rootCodeMap, 'LTH', '189691')
        map.put(rootCodeMap, 'MHG', '085699')
        map.put(rootCodeMap, 'MGC', '088695')
        map.put(rootCodeMap, 'SIL', '084694')
        map.put(rootCodeMap, 'QO', '088692')
        map.put(rootCodeMap, 'QI', '084692')
        map.put(rootCodeMap, 'MOX', '192656')
        map.put(rootCodeMap, 'EHR', '192691')
        map.put(rootCodeMap, 'SGC', '088698')
        map.put(rootCodeMap, 'SGU', '088697')
        map.put(rootCodeMap, 'SI', '084691')
        map.put(rootCodeMap, 'BUS', '257652')
        map.put(rootCodeMap, 'HRC', '192651')
        map.put(rootCodeMap, 'HDG', '192692')
        map.put(rootCodeMap, 'UX', '016651')
        map.put(rootCodeMap, 'BTI', '133LM2')
        map.put(rootCodeMap, 'ETI', '146LM2')
        map.put(rootCodeMap, 'OIL', '067LM1')
        map.put(rootCodeMap, 'BIT', '133LM1')
        map.put(rootCodeMap, 'ET', '146LM1')
        map.put(rootCodeMap, 'BMC', '133SG2')
        map.put(rootCodeMap, 'SDX', '098SG1')
        map.put(rootCodeMap, 'TM', '067SG1')
        map.put(rootCodeMap, 'SR1', '134731')
        map.put(rootCodeMap, 'SR3', '134730')
        map.put(rootCodeMap, '30C', '203061')
        map.put(rootCodeMap, 'AS', '232663')
        map.put(rootCodeMap, 'YA', '332661')
        map.put(rootCodeMap, 'AR', '432661')
        map.put(rootCodeMap, 'AWN', '24478F')
        map.put(rootCodeMap, 'BTM', '133732')
        map.put(rootCodeMap, 'QA', '232662')
        map.put(rootCodeMap, 'PC', '090663')
        map.put(rootCodeMap, 'GN', '112662')
        map.put(rootCodeMap, 'PK', '273661')
        map.put(rootCodeMap, 'PS', '264661')
        map.put(rootCodeMap, 'KSV', '090771')
        map.put(rootCodeMap, 'HY', '090661')
        map.put(rootCodeMap, 'CC', '073732')
        map.put(rootCodeMap, 'KC', '083731')
        map.put(rootCodeMap, 'CT', '033661')
        map.put(rootCodeMap, 'VC', '275663')
        map.put(rootCodeMap, 'YZ', '122662')
        map.put(rootCodeMap, 'EZ', '275662')
        map.put(rootCodeMap, 'HR', '274662')
        map.put(rootCodeMap, 'OJ', '040701')
        map.put(rootCodeMap, 'VU', '274663')
        map.put(rootCodeMap, 'IUS', '224770')
        map.put(rootCodeMap, 'ILS', '278661')
        map.put(rootCodeMap, 'SY', '296661')
        map.put(rootCodeMap, 'KSN', '097771')
        map.put(rootCodeMap, 'MMW', '24477M')
        map.put(rootCodeMap, 'ASN', '24477G')
        map.put(rootCodeMap, 'MLE', '24477F')
        map.put(rootCodeMap, 'MUN', '244043')
        map.put(rootCodeMap, 'MWL', '244051')
        map.put(rootCodeMap, 'ASI', '244061')
        map.put(rootCodeMap, 'MTO', '24478L')
        map.put(rootCodeMap, 'LFG', '244781')
        map.put(rootCodeMap, 'MTN', '24478K')
        map.put(rootCodeMap, 'MFS', '244041')
        map.put(rootCodeMap, 'MVU', '244786')
        map.put(rootCodeMap, 'MTL', '24478J')
        map.put(rootCodeMap, 'MMC', '244784')
        map.put(rootCodeMap, 'MMM', '24477X')
        map.put(rootCodeMap, 'LFM', '24477Z')
        map.put(rootCodeMap, 'MME', '244042')
        map.put(rootCodeMap, 'MML', '24477J')
        map.put(rootCodeMap, 'MMN', '24477R')
        map.put(rootCodeMap, 'MMR', '24478H')
        map.put(rootCodeMap, 'MVT', '244788')
        map.put(rootCodeMap, 'LFU', '244782')
        map.put(rootCodeMap, 'EU9', '24477V')
        map.put(rootCodeMap, 'MVV', '24478G')
        map.put(rootCodeMap, 'MIN', '24477P')
        map.put(rootCodeMap, 'JPP', '244771')
        map.put(rootCodeMap, 'PAC', '24478B')
        map.put(rootCodeMap, 'MPA', '24477U')
        map.put(rootCodeMap, 'MVS', '244787')
        map.put(rootCodeMap, 'LFA', '24477Y')
        map.put(rootCodeMap, 'USS', '244062')
        map.put(rootCodeMap, 'USC', '24478E')
        map.put(rootCodeMap, 'WOW', '244789')
        map.put(rootCodeMap, 'MVR', '244785')
        map.put(rootCodeMap, 'LFW', '24404G')
        map.put(rootCodeMap, 'MWS', '24477T')
        map.put(rootCodeMap, 'KAU', '232666')
        map.put(rootCodeMap, 'KEO', '116667')
        map.put(rootCodeMap, 'KRA', '099663')
        map.put(rootCodeMap, 'KGB', '599663')
        map.put(rootCodeMap, 'KEP', '699663')
        map.put(rootCodeMap, 'KEJ', '299663')
        map.put(rootCodeMap, 'KRK', '399664')
        map.put(rootCodeMap, 'KRZ', '499663')
        map.put(rootCodeMap, 'KOL', '799662')
        map.put(rootCodeMap, 'KZY', '492662')
        map.put(rootCodeMap, 'KZX', '112665')
        map.put(rootCodeMap, 'ZJ', '112663')
        map.put(rootCodeMap, 'NT', '116665')
        map.put(rootCodeMap, 'KY', '273662')
        map.put(rootCodeMap, 'NJ', '276661')
        map.put(rootCodeMap, 'FNG', '223772')
        map.put(rootCodeMap, 'PLN', '277661')
        map.put(rootCodeMap, 'PLE', '277662')
        map.put(rootCodeMap, 'HIO', '084043')
        map.put(rootCodeMap, 'SB', '080732')
        map.put(rootCodeMap, 'SF', '080737')
        map.put(rootCodeMap, 'KJ', '264662')
        map.put(rootCodeMap, 'SS', '196661')
        map.put(rootCodeMap, 'KMF', '092661')
        map.put(rootCodeMap, 'TRM', '019661')
        map.put(rootCodeMap, 'MP', '096773')
        map.put(rootCodeMap, 'ZR', '122661')
        map.put(rootCodeMap, 'KX', '264663')
        map.put(rootCodeMap, 'DX', '098662')
        map.put(rootCodeMap, 'KMP', '095661')
        map.put(rootCodeMap, 'AFI', '86565D')
        map.put(rootCodeMap, 'BOO', '86565G')
        map.put(rootCodeMap, 'FO', '86565C')
        map.put(rootCodeMap, 'BEF', '066A28')
        map.put(rootCodeMap, 'AE5', '067A31')
        map.put(rootCodeMap, 'A7E', '06665B')
        map.put(rootCodeMap, '22', '066A09')
        map.put(rootCodeMap, 'A91', '066A07')
        map.put(rootCodeMap, '3NA', '066A27')
        map.put(rootCodeMap, 'A9N', '06665A')
        map.put(rootCodeMap, 'ANT', '067A85')
        map.put(rootCodeMap, 'BKT', '067A88')
        map.put(rootCodeMap, 'CY', '06765N')
        map.put(rootCodeMap, 'AJ9', '067A25')
        map.put(rootCodeMap, 'BZ', '06765T')
        map.put(rootCodeMap, 'ADB', '06765O')
        map.put(rootCodeMap, 'CGO', '006NLK')
        map.put(rootCodeMap, 'GEO', '006NJZ')
        map.put(rootCodeMap, 'NGO', '00665T')
        map.put(rootCodeMap, 'CU', '025651')
        map.put(rootCodeMap, 'A5C', '022A56')
        map.put(rootCodeMap, 'MTF', '024656')
        map.put(rootCodeMap, 'MFF', '024658')
        map.put(rootCodeMap, 'CS4', '2616AC')
        map.put(rootCodeMap, 'A8M', '06665V')
        map.put(rootCodeMap, 'CBB', '066A16')
        map.put(rootCodeMap, 'A8L', '06665U')
        map.put(rootCodeMap, 'CGB', '066A15')
        map.put(rootCodeMap, 'A8K', '06665T')
        map.put(rootCodeMap, 'CPB', '066A14')
        map.put(rootCodeMap, 'CL', '067651')
        map.put(rootCodeMap, '26', '067A37')
        map.put(rootCodeMap, 'AFY', '06765M')
        map.put(rootCodeMap, 'DCB', '06765G')
        map.put(rootCodeMap, 'TFU', '023C06')
        map.put(rootCodeMap, 'TTF', '023B98')
        map.put(rootCodeMap, 'TTG', '023C08')
        map.put(rootCodeMap, 'QM', '067655')
        map.put(rootCodeMap, 'QU', '11165M')
        map.put(rootCodeMap, 'QH', '022656')
        map.put(rootCodeMap, 'QG', '023655')
        map.put(rootCodeMap, 'EWG', '111A50')
        map.put(rootCodeMap, 'EWN', '03265H')
        map.put(rootCodeMap, 'AA5', '022A57')
        map.put(rootCodeMap, 'AZ1', '025608')
        map.put(rootCodeMap, 'Z1B', '025659')
        map.put(rootCodeMap, 'AKR', '02165O')
        map.put(rootCodeMap, 'UV', '02165E')
        map.put(rootCodeMap, 'AGT', '02265X')
        map.put(rootCodeMap, 'AET', '02265P')
        map.put(rootCodeMap, 'R5F', '021A70')
        map.put(rootCodeMap, 'GZ', '86765C')
        map.put(rootCodeMap, '7F', '022A69')
        map.put(rootCodeMap, 'AGX', '02265V')
        map.put(rootCodeMap, 'A43', '03265G')
        map.put(rootCodeMap, 'AKZ', '03265E')
        map.put(rootCodeMap, 'UN', '03265A')
        map.put(rootCodeMap, 'EN', '86665A')
        map.put(rootCodeMap, 'APS', '066652')
        map.put(rootCodeMap, 'A32', '066A06')
        map.put(rootCodeMap, 'EPN', '066A22')
        map.put(rootCodeMap, 'FLJ', '2616A8')
        map.put(rootCodeMap, 'TM', '261654')
        map.put(rootCodeMap, 'TH', '261653')
        map.put(rootCodeMap, 'T2D', '26165V')
        map.put(rootCodeMap, 'TL', '261655')
        map.put(rootCodeMap, 'EVC', '021A56')
        map.put(rootCodeMap, 'AQA', '022A24')
        map.put(rootCodeMap, 'AVL', '022A25')
        map.put(rootCodeMap, 'A8B', '111A62')
        map.put(rootCodeMap, 'AA8', '111A08')
        map.put(rootCodeMap, 'AA6', '022A60')
        map.put(rootCodeMap, 'AB6', '022B22')
        map.put(rootCodeMap, 'BCR', '111A61')
        map.put(rootCodeMap, 'CRB', '111A34')
        map.put(rootCodeMap, 'GFC', '86565H')
        map.put(rootCodeMap, 'ME', '86465A')
        map.put(rootCodeMap, 'GCI', '86565N')
        map.put(rootCodeMap, 'GCU', '021A28')
        map.put(rootCodeMap, 'ALY', '022A05')
        map.put(rootCodeMap, 'GBB', '111A55')
        map.put(rootCodeMap, 'A1G', '022A61')
        map.put(rootCodeMap, 'ABH', '022657')
        map.put(rootCodeMap, 'HOB', '867652')
        map.put(rootCodeMap, 'NN', '03565B')
        map.put(rootCodeMap, 'HH', '023A55')
        map.put(rootCodeMap, 'HP', '023A56')
        map.put(rootCodeMap, 'NPG', '03565C')
        map.put(rootCodeMap, 'JA', '03265C')
        map.put(rootCodeMap, 'AJB', '86665B')
        map.put(rootCodeMap, 'E6', '03265F')
        map.put(rootCodeMap, 'HJC', '86465D')
        map.put(rootCodeMap, 'A1M', '86465K')
        map.put(rootCodeMap, 'AWJ', '067A07')
        map.put(rootCodeMap, 'BL2', '2616AA')
        map.put(rootCodeMap, 'JKM', '86665H')
        map.put(rootCodeMap, 'NWM', '023C07')
        map.put(rootCodeMap, 'AKL', '022A21')
        map.put(rootCodeMap, 'AJL', '11165W')
        map.put(rootCodeMap, 'AJS', '86465G')
        map.put(rootCodeMap, 'MQA', '022B23')
        map.put(rootCodeMap, 'FLP', '26165T')
        map.put(rootCodeMap, 'AYV', '067A16')
        map.put(rootCodeMap, 'CMS', '407653')
        map.put(rootCodeMap, 'MT2', '407651')
        map.put(rootCodeMap, 'MEF', '021A62')
        map.put(rootCodeMap, 'R5O', '021A66')
        map.put(rootCodeMap, 'M1B', '022B21')
        map.put(rootCodeMap, 'MHO', '022B24')
        map.put(rootCodeMap, 'MRB', '111660')
        map.put(rootCodeMap, 'S5O', '021A72')
        map.put(rootCodeMap, 'MAF', '021A61')
        map.put(rootCodeMap, 'MCL', '067A55')
        map.put(rootCodeMap, 'MAA', '066A26')
        map.put(rootCodeMap, 'MAE', '066A21')
        map.put(rootCodeMap, 'MAS', '066A20')
        map.put(rootCodeMap, 'MBC', '0676A4')
        map.put(rootCodeMap, 'A0D', '021A17')
        map.put(rootCodeMap, 'MUD', '022A99')
        map.put(rootCodeMap, 'R5M', '021A68')
        map.put(rootCodeMap, 'RBM', '021A80')
        map.put(rootCodeMap, 'MJC', '86465P')
        map.put(rootCodeMap, 'MEE', '86665G')
        map.put(rootCodeMap, 'MNC', '03265J')
        map.put(rootCodeMap, 'MPS', '066A25')
        map.put(rootCodeMap, 'MEO', '111A47')
        map.put(rootCodeMap, 'MEB', '111A52')
        map.put(rootCodeMap, 'MJN', '86665E')
        map.put(rootCodeMap, 'E6M', '86665F')
        map.put(rootCodeMap, 'MXB', '111A54')
        map.put(rootCodeMap, 'MXR', '111A53')
        map.put(rootCodeMap, 'MTS', '021A35')
        map.put(rootCodeMap, 'S5M', '021A65')
        map.put(rootCodeMap, 'SBM', '021A77')
        map.put(rootCodeMap, '5L', '021A20')
        map.put(rootCodeMap, 'A0F', '021A19')
        map.put(rootCodeMap, 'MSG', '022B09')
        map.put(rootCodeMap, 'A8C', '06665Y')
        map.put(rootCodeMap, 'A8O', '06665W')
        map.put(rootCodeMap, '51', '066A05')
        map.put(rootCodeMap, 'PMF', '066A30')
        map.put(rootCodeMap, 'AR0', '06665X')
        map.put(rootCodeMap, 'A8J', '06665Z')
        map.put(rootCodeMap, 'MBR', '405652')
        map.put(rootCodeMap, 'MBL', '066A23')
        map.put(rootCodeMap, 'A81', '066A10')
        map.put(rootCodeMap, 'MBE', '405654')
        map.put(rootCodeMap, 'AC0', '06665P')
        map.put(rootCodeMap, 'B0', '06665O')
        map.put(rootCodeMap, 'A7Q', '06665R')
        map.put(rootCodeMap, 'A8I', '06665S')
        map.put(rootCodeMap, 'AD0', '06665Q')
        map.put(rootCodeMap, 'NOO', '86665C')
        map.put(rootCodeMap, 'NG', '023651')
        map.put(rootCodeMap, 'JCC', '023C04')
        map.put(rootCodeMap, 'AEZ', '025652')
        map.put(rootCodeMap, 'A7Y', '022A66')
        map.put(rootCodeMap, 'HO', '022651')
        map.put(rootCodeMap, 'JET', '86465S')
        map.put(rootCodeMap, 'JTB', '86465T')
        map.put(rootCodeMap, 'MPX', '02265A')
        map.put(rootCodeMap, 'MM', '02165B')
        map.put(rootCodeMap, 'AHL', '86765A')
        map.put(rootCodeMap, 'ULB', '022A97')
        map.put(rootCodeMap, 'PA', '075651')
        map.put(rootCodeMap, 'PGG', '406651')
        map.put(rootCodeMap, 'AL1', '064A58')
        map.put(rootCodeMap, 'JDL', '064659')
        map.put(rootCodeMap, 'PL', '076651')
        map.put(rootCodeMap, 'A3G', '111A02')
        map.put(rootCodeMap, 'A1R', '06665G')
        map.put(rootCodeMap, '1S', '06665H')
        map.put(rootCodeMap, 'RLX', '11165K')
        map.put(rootCodeMap, 'ZXY', '967652')
        map.put(rootCodeMap, '1E', '96765F')
        map.put(rootCodeMap, 'A1D', '111A09')
        map.put(rootCodeMap, 'RLX', '11165J')
        map.put(rootCodeMap, 'RBB', '111A41')
        map.put(rootCodeMap, 'EXR', '111A45')
        map.put(rootCodeMap, 'ARY', '86265C')
        map.put(rootCodeMap, 'RB', '111659')
        map.put(rootCodeMap, 'ABS', '02165M')
        map.put(rootCodeMap, 'SD', '02165J')
        map.put(rootCodeMap, 'S5F', '021A71')
        map.put(rootCodeMap, 'S5B', '021A82')
        map.put(rootCodeMap, 'S53', '021A73')
        map.put(rootCodeMap, 'SR5', '021A83')
        map.put(rootCodeMap, 'UA', '02165G')
        map.put(rootCodeMap, 'SE', '02165K')
        map.put(rootCodeMap, 'SF3', '86565P')
        map.put(rootCodeMap, 'SGB', '02265J')
        map.put(rootCodeMap, 'AVU', '022A22')
        map.put(rootCodeMap, 'AGA', '02265T')
        map.put(rootCodeMap, 'RKA', '86465C')
        map.put(rootCodeMap, 'D1N', '111A46')
        map.put(rootCodeMap, 'N1B', '111A11')
        map.put(rootCodeMap, 'A1P', '111A12')
        map.put(rootCodeMap, 'ATP', '022A32')
        map.put(rootCodeMap, 'A1L', '022A62')
        map.put(rootCodeMap, 'LT', '022A13')
        map.put(rootCodeMap, 'H5F', '021A76')
        map.put(rootCodeMap, 'A42', '067A45')
        map.put(rootCodeMap, 'CSX', '06765A')
        map.put(rootCodeMap, 'HTT', '0676A5')
        map.put(rootCodeMap, 'AFF', '067A69')
        map.put(rootCodeMap, 'WTT', '067A71')
        map.put(rootCodeMap, 'BK', '06765L')
        map.put(rootCodeMap, 'WTL', '067A86')
        map.put(rootCodeMap, 'AFH', '067A24')
        map.put(rootCodeMap, 'QMW', '001626')
        return rootCodeMap

    def getRootCodeMap():
        rootCodeMap: Persistent[dict[str, str]] = createRootCodeMap()
        return rootCodeMap

    def rootToCFTCCode(root: str):
        code: str = method_call('get', getRootCodeMap(), root)
        return '' if na(code) else code

    def currencyToCFTCCode(currency__ren__: str):
        __block_result__ = na
        __switch__ = currency__ren__
        if __switch__ == 'BTC':
            __block_result__ = '133741'
        elif __switch__ == 'USD':
            __block_result__ = '098662'
        elif __switch__ == 'EUR':
            __block_result__ = '099741'
        elif __switch__ == 'JPY':
            __block_result__ = '097741'
        elif __switch__ == 'MXN':
            __block_result__ = '095741'
        elif __switch__ == 'CHF':
            __block_result__ = '092741'
        elif __switch__ == 'RUB':
            __block_result__ = '089741'
        elif __switch__ == 'CAD':
            __block_result__ = '090741'
        elif __switch__ == 'NZD':
            __block_result__ = '112741'
        elif __switch__ == 'GBP':
            __block_result__ = '096742'
        elif __switch__ == 'BRL':
            __block_result__ = '102741'
        elif __switch__ == 'ZAR':
            __block_result__ = '122741'
        elif __switch__ == 'AUD':
            __block_result__ = '232741'
        elif __switch__ == 'ETH':
            __block_result__ = '146021'
        else:
            __block_result__ = ''
        code: str = __block_result__
        return code

    def optionsToTicker(includeOptions: bool):
        return 'FO' if includeOptions else 'F'

    def metricNameAndDirectionToTicker(metricName: str, metricDirection: str):
        __block_result_1__ = na
        __switch__ = metricName
        if __switch__ == 'Asset Manager Positions':
            __block_result_1__ = 'AMP'
        elif __switch__ == 'Commercial Positions':
            __block_result_1__ = 'CP'
        elif __switch__ == 'Concentration Gross LE 4 TDR':
            __block_result_1__ = 'CON_GROSS_LE_4'
        elif __switch__ == 'Concentration Gross LE 8 TDR':
            __block_result_1__ = 'CON_GROSS_LE_8'
        elif __switch__ == 'Concentration Gross LT 4 TDR':
            __block_result_1__ = 'CON_GROSS_LT_4'
        elif __switch__ == 'Concentration Gross LT 8 TDR':
            __block_result_1__ = 'CON_GROSS_LT_8'
        elif __switch__ == 'Concentration Net LE 4 TDR':
            __block_result_1__ = 'CON_NET_LE_4'
        elif __switch__ == 'Concentration Net LE 8 TDR':
            __block_result_1__ = 'CON_NET_LE_8'
        elif __switch__ == 'Concentration Net LT 4 TDR':
            __block_result_1__ = 'CON_NET_LT_4'
        elif __switch__ == 'Concentration Net LT 8 TDR':
            __block_result_1__ = 'CON_NET_LT_8'
        elif __switch__ == 'Dealer Positions':
            __block_result_1__ = 'DP'
        elif __switch__ == 'Leveraged Funds Positions':
            __block_result_1__ = 'LMP'
        elif __switch__ == 'Managed Money Positions':
            __block_result_1__ = 'MMP'
        elif __switch__ == 'Noncommercial Positions':
            __block_result_1__ = 'NCP'
        elif __switch__ == 'Nonreportable Positions':
            __block_result_1__ = 'NRP'
        elif __switch__ == 'Open Interest':
            __block_result_1__ = 'OI'
        elif __switch__ == 'Other Reportable Positions':
            __block_result_1__ = 'ORP'
        elif __switch__ == 'Producer Merchant Positions':
            __block_result_1__ = 'PMR'
        elif __switch__ == 'Swap Positions':
            __block_result_1__ = 'SP'
        elif __switch__ == 'Total Reportable Positions':
            __block_result_1__ = 'TRP'
        elif __switch__ == 'Traders Asset Manager':
            __block_result_1__ = 'TAM'
        elif __switch__ == 'Traders Commercial':
            __block_result_1__ = 'TC'
        elif __switch__ == 'Traders Dealer':
            __block_result_1__ = 'TD'
        elif __switch__ == 'Traders Leveraged Funds':
            __block_result_1__ = 'TLM'
        elif __switch__ == 'Traders Managed Money':
            __block_result_1__ = 'TMM'
        elif __switch__ == 'Traders Noncommercial':
            __block_result_1__ = 'TNC'
        elif __switch__ == 'Traders Other Reportable':
            __block_result_1__ = 'TOR'
        elif __switch__ == 'Traders Producer Merchant':
            __block_result_1__ = 'TPM'
        elif __switch__ == 'Traders Swap':
            __block_result_1__ = 'TS'
        elif __switch__ == 'Traders Total':
            __block_result_1__ = 'TT'
        elif __switch__ == 'Traders Total Reportable':
            __block_result_1__ = 'TTR'
        else:
            runtime.error(string.format('Invalid metric name: {1}{0}{1}. See the library{1}s documentation or source code for all valid  metric names.', metricName, "'"))
            __block_result_1__ = na
        metricCode: str = __block_result_1__
        __block_result_2__ = na
        __switch__ = metricDirection
        if __switch__ == 'Long':
            __block_result_2__ = '_L'
        elif __switch__ == 'Short':
            __block_result_2__ = '_S'
        elif __switch__ == 'Spreading':
            __block_result_2__ = '_SPREAD'
        elif __switch__ == 'No direction':
            __block_result_2__ = ''
        else:
            runtime.error(string.format('{1}{0}{1} is not a valid `metricDirection` argument. Possible values:  {1}Long{1}, {1}Short{1}, {1}Spreading{1}, {1}No direction{1}', metricDirection, "'"))
            __block_result_2__ = na
        directionCode: str = __block_result_2__
        if metricDirection == 'No direction':
            if metricName != 'Open Interest' and metricName != 'Traders Total':
                runtime.error(string.format('{2}{0}{2} does not apply to the {2}{1}{2} metric.', metricDirection, metricName, "'"))
        elif metricDirection == 'Spreading':
            __block_result_3__ = na
            __switch_1__ = metricName
            if __switch_1__ == 'Commercial Positions':
                __block_result_3__ = True
            elif __switch_1__ == 'Total Reportable Positions':
                __block_result_3__ = True
            elif __switch_1__ == 'Nonreportable Positions':
                __block_result_3__ = True
            elif __switch_1__ == 'Traders Commercial':
                __block_result_3__ = True
            elif __switch_1__ == 'Traders Total Reportable':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Gross LT 4 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Gross LT 8 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Net LT 4 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Net LT 8 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Gross LE 4 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Gross LE 8 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Net LE 4 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Concentration Net LE 8 TDR':
                __block_result_3__ = True
            elif __switch_1__ == 'Producer Merchant Positions':
                __block_result_3__ = True
            elif __switch_1__ == 'Traders Producer Merchant':
                __block_result_3__ = True
            else:
                __block_result_3__ = False
            isIncorrect = __block_result_3__
            if isIncorrect:
                runtime.error(string.format('The {2}{0}{2} direction does not apply to the {2}{1}{2} metric.', metricDirection, metricName, "'"))
        elif metricName == 'Open Interest' or metricName == 'Traders Total':
            runtime.error(string.format('The {2}{0}{2} direction does not apply to the {2}{1}{2} metric.', metricDirection, metricName, "'"))
        return metricCode + directionCode

    def typeToTicker(metricType: str):
        __block_result_4__ = na
        __switch__ = metricType
        if __switch__ == 'All':
            __block_result_4__ = ''
        elif __switch__ == 'Old':
            __block_result_4__ = '_OLD'
        elif __switch__ == 'Other':
            __block_result_4__ = '_OTHER'
        else:
            runtime.error(string.format('{1}{0}{1} is not a valid `metricType` argument. Possible values: {1}All{1}, {1}Old{1}, {1}Other{1}', metricType, "'"))
            __block_result_4__ = na
        result: str = __block_result_4__
        return result

    @export
    def convertRootToCOTCode(mode: str, convertToCOT: bool = True):
        hasRoot: bool = syminfo.root != syminfo.ticker
        root: str = rootToCFTCCode(syminfo.root)
        baseCurrency: str = currencyToCFTCCode(syminfo.basecurrency)
        mainCurrency: str = currencyToCFTCCode(syminfo.currency)
        __block_result_5__ = na
        __switch__ = mode
        if __switch__ == 'Auto':
            isNotEmpty_1 = isNotEmpty(root)
            __block_result_6__ = na
            if hasRoot and isNotEmpty_1:
                __block_result_6__ = root if convertToCOT else syminfo.root
            elif isNotEmpty(baseCurrency):
                __block_result_6__ = baseCurrency if convertToCOT else syminfo.basecurrency
            elif isNotEmpty(mainCurrency):
                __block_result_6__ = mainCurrency if convertToCOT else syminfo.currency
            else:
                __block_result_6__ = ''
            __block_result_5__ = __block_result_6__
        elif __switch__ == 'Root':
            __block_result_5__ = root if convertToCOT else syminfo.root
        elif __switch__ == 'Base currency':
            __block_result_5__ = baseCurrency if convertToCOT else syminfo.basecurrency
        elif __switch__ == 'Currency':
            __block_result_5__ = mainCurrency if convertToCOT else syminfo.currency
        else:
            runtime.error(string.format('{1}{0}{1} is not a valid `mode` argument. Possible values:  {1}Root{1}, {1}Base currency{1}, {1}Currency{1}, {1}Auto{1}', mode, "'"))
            __block_result_5__ = ''
        result: str = __block_result_5__
        if result == '':
            runtime.error(string.format('No {0}{1} found for the current symbol.', string.replace(string.lower(mode), 'auto', 'root or currency'), ' CFTC code' if convertToCOT else ''))
        return result

    @export
    def COTTickerid(COTType: str, CFTCCode: str, includeOptions: bool, metricName: str, metricDirection: str, metricType: str):
        __block_result_7__ = na
        __switch__ = COTType
        if __switch__ == 'Legacy':
            __block_result_7__ = ''
        elif __switch__ == 'Disaggregated':
            __block_result_7__ = '2'
        elif __switch__ == 'Financial':
            __block_result_7__ = '3'
        else:
            runtime.error(string.format('{1}{0}{1} is not a valid `COTType` argument. Possible values:  {1}Legacy{1}, {1}Disaggregated{1}, {1}Financial{1}', COTType, "'"))
            __block_result_7__ = na
        typeCode: str = __block_result_7__
        __block_result_8__ = na
        if COTType == 'Legacy':
            __block_result_9__ = na
            __switch_1__ = metricName
            if __switch_1__ == 'Open Interest':
                __block_result_9__ = False
            elif __switch_1__ == 'Noncommercial Positions':
                __block_result_9__ = False
            elif __switch_1__ == 'Commercial Positions':
                __block_result_9__ = False
            elif __switch_1__ == 'Total Reportable Positions':
                __block_result_9__ = False
            elif __switch_1__ == 'Nonreportable Positions':
                __block_result_9__ = False
            elif __switch_1__ == 'Traders Total':
                __block_result_9__ = False
            elif __switch_1__ == 'Traders Noncommercial':
                __block_result_9__ = False
            elif __switch_1__ == 'Traders Commercial':
                __block_result_9__ = False
            elif __switch_1__ == 'Traders Total Reportable':
                __block_result_9__ = False
            elif __switch_1__ == 'Concentration Gross LT 4 TDR':
                __block_result_9__ = False
            elif __switch_1__ == 'Concentration Gross LT 8 TDR':
                __block_result_9__ = False
            elif __switch_1__ == 'Concentration Net LT 4 TDR':
                __block_result_9__ = False
            elif __switch_1__ == 'Concentration Net LT 8 TDR':
                __block_result_9__ = False
            else:
                __block_result_9__ = True
            __block_result_8__ = __block_result_9__
        elif COTType == 'Disaggregated':
            __block_result_10__ = na
            __switch_1__ = metricName
            if __switch_1__ == 'Open Interest':
                __block_result_10__ = False
            elif __switch_1__ == 'Producer Merchant Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Swap Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Managed Money Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Other Reportable Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Total Reportable Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Nonreportable Positions':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Total':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Producer Merchant':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Swap':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Managed Money':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Other Reportable':
                __block_result_10__ = False
            elif __switch_1__ == 'Traders Total Reportable':
                __block_result_10__ = False
            elif __switch_1__ == 'Concentration Gross LE 4 TDR':
                __block_result_10__ = False
            elif __switch_1__ == 'Concentration Gross LE 8 TDR':
                __block_result_10__ = False
            elif __switch_1__ == 'Concentration Net LE 4 TDR':
                __block_result_10__ = False
            elif __switch_1__ == 'Concentration Net LE 8 TDR':
                __block_result_10__ = False
            else:
                __block_result_10__ = True
            __block_result_8__ = __block_result_10__
        elif COTType == 'Financial':
            __block_result_11__ = na
            __switch_1__ = metricName
            if __switch_1__ == 'Open Interest':
                __block_result_11__ = False
            elif __switch_1__ == 'Dealer Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Asset Manager Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Leveraged Funds Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Other Reportable Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Total Reportable Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Nonreportable Positions':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Total':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Dealer':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Asset Manager':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Leveraged Funds':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Other Reportable':
                __block_result_11__ = False
            elif __switch_1__ == 'Traders Total Reportable':
                __block_result_11__ = False
            elif __switch_1__ == 'Concentration Gross LE 4 TDR':
                __block_result_11__ = False
            elif __switch_1__ == 'Concentration Gross LE 8 TDR':
                __block_result_11__ = False
            elif __switch_1__ == 'Concentration Net LE 4 TDR':
                __block_result_11__ = False
            elif __switch_1__ == 'Concentration Net LE 8 TDR':
                __block_result_11__ = False
            else:
                __block_result_11__ = True
            __block_result_8__ = __block_result_11__
        invalidType: bool = __block_result_8__
        if invalidType:
            runtime.error(string.format('{2}{0}{2} is not a valid {1} COT metric. See the library{2}s documentation or code for all valid {1}  metric names.', metricName, COTType, "'"))
        result: str = string.format('COT{0}:{1}_{2}_{3}{4}', typeCode, CFTCCode, optionsToTicker(includeOptions), metricNameAndDirectionToTicker(metricName, metricDirection), typeToTicker(metricType))
        return result

    @export
    def requestCommitmentOfTraders(COTType: str, CFTCCode: str, includeOptions: bool, metricName: str, metricDirection: str, metricType: str):
        t: str = COTTickerid(COTType, CFTCCode, includeOptions, metricName, metricDirection, metricType)
        tf: str = timeframe.period if timeframe.isdwm else '1D'
        data: float = request.security(t, tf, close, ignore_invalid_symbol=True)
        if ta.cum(nz(data)) == 0 and barstate.islastconfirmedhistory:
            runtime.error('The requested COT data is unavailable. Please ensure the report type, CFTC code, and additional  settings represent a valid metric request.')
        return data

    COTdataseries: float = requestCommitmentOfTraders(COTType='Legacy', CFTCCode=convertRootToCOTCode('Auto'), includeOptions=False, metricName='Open Interest', metricDirection='No direction', metricType='All')
    plot(COTdataseries, style=plot.style_stepline_diamond)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
