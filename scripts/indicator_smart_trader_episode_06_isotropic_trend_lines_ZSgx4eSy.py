"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    display, format, high, input, label, line, linefill, low, math, max_bars_back, na, nz, open,
    plot, position, script, string, syminfo, ta, table, text, timeframe, yloc
)
from pynecore.types import (
    Box, Color, Label, Line, LineFill, Persistent, PersistentSeries,
    Series, Table
)


@udt
class TrendResult:
    dir: int = 0
    angle: float = 0.0
    segEnd: int = 0
    chUpper: float = na(float)
    chLower: float = na(float)


@udt
class I18n:
    lbl_period: str = "period"
    lbl_trend: str = "trend"
    lbl_agreement: str = "agreement"

    dir_up: str = "UP"
    dir_dn: str = "DN"
    dir_rng: str = "RNG"

    st_bo_up: str = "Breakout Up"
    st_bo_dn: str = "Breakout Down"
    st_rt_up_broke_at: str = "Retest Up · broke at"
    st_rt_dn_broke_at: str = "Retest Down · broke at"

    st_inside: str = "Inside channel"
    st_inside_dir_ch: str = "Inside · direction changed"
    st_inside_fail_up: str = "Inside · failed breakout up"
    st_inside_fail_dn: str = "Inside · failed breakout down"

    conn_at: str = "at"
    conn_gap: str = "(gap)"
    conn_retested: str = "· retested"
    conn_now: str = "now"

    dist_above_ceiling: str = "% above ceiling"
    dist_below_floor: str = "% below floor"
    dist_from_floor: str = "% from floor"
    dist_to_ceiling: str = "% to ceiling"

    tip_header: str = "ST-EP06 — Smart Trader, Episode 06: Isotropic Trend Lines.\n\nMulti-scale trend channels in σ-normalized coordinate space (ICS). Header price is always live close (Live Exception). All other values anchor at the bar chosen via Calculation Bar — [0] in Live Bar mode, [1] in Close Bar mode."
    tip_period: str = "Block periods for the 6-scale parallel analysis.\n\nEach scale partitions history into blocks and reduces each to a log-midpoint geometric mean.\n\nThe '19' column = primary engine (uses your Period input). Others use fixed periods for cross-scale consensus."
    tip_trend: str = "Per-scale trend direction from the longest monotonic segment of block geometric means.\n\n▲ UP · ▼ DN · ◈ RNG\n\nRNG = absolute ICS angle within ±Range Threshold. Angle is arctan of σ-normalized slope, comparable across markets."
    tip_agreement: str = "Cross-scale consensus.\n\nHow many of the 6 scales agree on direction, shown with the primary channel Ch▲ (ceiling) and Ch▼ (floor).\n\n5/6 or 6/6 = structural trend visible at every temporal resolution."
    tip_narrative: str = "Breakout / Retest narrative (primary engine, scale 19).\n\nOne-line state + distance summary:\n\n• Inside — % from floor · % to ceiling (sums to 100%)\n• Breakout Up/Down — price exited channel, shown with breakout price and % beyond the boundary\n• Retest — after moving ≥1σ from the boundary, price returned to test it\n\n✓ = confirmed (retested and bounced ≥1σ).\n(gap) = price crossed the entire channel in one move.\n\nAll distances are % of channel width (scale-invariant). σ thresholds are dynamic (Yang-Zhang)."

    lbl_close: str = "Close"
    lbl_ceiling: str = "Ceiling"
    lbl_floor: str = "Floor"
    lbl_ext: str = "Extension"

    lbl_trend_tip: str = "Trend"
    lbl_angle: str = "Angle"
    lbl_blocks: str = "Blocks"

    alert_warn: str = "Alerts require Calculation Bar = Live Bar"
    alert_warn_tip: str = "Alerts are currently enabled but Calculation Bar is set to Close Bar.\n\nClose Bar mode anchors computations at the last closed bar, which is semantically incompatible with live alerts. To fire alerts without lag, open indicator settings and change Calculation Bar to Live Bar.\n\nUntil then, all alertconditions are suppressed."


MIN_SIGMA: float = 1e-10
PI: float = math.pi
GP_CALC: str = "Calculation"
GP_CH: str = "Channel Lines"
GP_PJ: str = "Projection Lines"
GP_DSP: str = "Display"
GP_FILL: str = "Channel Fill"
GP_BLK: str = "Block Visualization"
GP_ALERTS: str = "Alerts"


@script.indicator("Smart Trader, Episode 06, Isotropic Trend Lines", "ST-EP06", overlay=True, max_lines_count=50, max_labels_count=50, max_boxes_count=20)
def main(
    i_calcBar=input.string("Live Bar", "Calculation Bar", options=("Live Bar", "Close Bar"), group=GP_CALC, tooltip="Which bar anchors every structural computation — σ, blocks, channel, state machine, and dashboard narrative.\n\nLive Bar (default): anchor = bar [0]. Values update with every tick and repaint within the bar — standard TradingView behavior.\n\nClose Bar: anchor = bar [1]. Values lock on bar close and never repaint — safer for back-testing and structural analysis.\n\nDashboard header price always shows live close in both modes (Live Exception)."),
    i_period=input.int(13, "Trend Block Period", minval=5, maxval=100, group=GP_CALC, tooltip="Number of bars per structural block. Price history is partitioned into consecutive blocks of this length; each reduces to a geometric mean (log-midpoint of High/Low).\n\nLarger → captures slower structural moves.\nSmaller → faster response, may overfit noise.\n\nTotal lookback = Period × Groups.\nDrives the primary engine (scale 19). Default: 26."),
    i_groups=input.int(5, "Trend Block Groups", minval=3, maxval=5, group=GP_CALC, tooltip="Number of consecutive blocks compared for direction detection and channel fitting. All 6 scales use this same value.\n\nThe largest scale (47) consumes 47 x Groups candles. Range is capped at 5 to stay within platform limits (max 235 candles for Scale 47).\n\n3 groups = fast adaptation\n5 groups = deeper structural view\n\nTotal lookback for primary engine = Period x Groups. Default: 5."),
    i_thresh=input.float(0.5, "Range Threshold (°)", minval=0.0, maxval=45.0, step=0.1, group=GP_CALC, tooltip="ICS angle threshold in degrees. When the trend angle falls between −Threshold and +Threshold, direction is classified as FLAT (ranging) instead of UP or DOWN.\n\nHigher → wider neutral zone, filters weak trends.\nLower → more directional sensitivity.\n\nRange: 0°–45°. Default: 0.5°."),
    i_sigmaLen=input.int(20, "Yang-Zhang Sigma Length", minval=5, maxval=100, group=GP_CALC, tooltip="Lookback for the Yang-Zhang (2000) realized volatility estimator. This σ normalizes log-price into the Isotropic Coordinate System (ICS), making trend angles comparable across instruments, timeframes, and volatility regimes.\n\nShorter → faster reaction to volatility shifts.\nLonger → smoother, more stable σ.\nDefault: 20."),
    i_clrUp=input.color(color.new('#26A69A'), "Up Color", group=GP_CH, tooltip="Channel line color during an uptrend (DIR_UP)."),
    i_clrDn=input.color(color.new('#EF5350'), "Down Color", group=GP_CH, tooltip="Channel line color during a downtrend (DIR_DOWN)."),
    i_clrRng=input.color(color.new('#888888'), "Range Color", group=GP_CH, tooltip="Channel line color during a ranging market (DIR_FLAT)."),
    i_chW=input.int(2, "Line Width", minval=1, maxval=5, group=GP_CH, tooltip="Pixel width of the solid channel boundary lines (upper and lower). Projection lines have a separate width setting."),
    i_chSty=input.string("Solid", "Line Style", options=("Solid", "Dashed", "Dotted"), group=GP_CH, tooltip="Visual style of the solid channel lines. Projection lines have a separate style setting."),
    i_pjOff=input.int(7, "Projection Offset", minval=1, maxval=100, group=GP_PJ, tooltip="Bars to extend the channel forward beyond the last confirmed bar. Projection extrapolates channel slope as a visual reference for potential support/resistance.\n\nLarger → longer forward view.\nSmaller → tighter projection.\n\nNo new data consumed — purely geometric. Default: 7."),
    i_pjW=input.int(2, "Projection Width", minval=1, maxval=5, group=GP_PJ, tooltip="Pixel width of the forward projection lines."),
    i_pjSty=input.string("Dotted", "Projection Style", options=("Solid", "Dashed", "Dotted"), group=GP_PJ, tooltip="Visual style of the forward projection lines."),
    i_lang=input.string("English", "Language", options=("English", "Türkçe", "العربية", "Русский", "Italiano", "Português (BR)", "中文"), group=GP_DSP, tooltip="Dashboard display language.\n\nEN · TR · AR · RU · IT · PT-BR · ZH\n\nCJK (Chinese) renders using TradingView's default font — no special setup required."),
    i_showCh=input.bool(True, "Show Channel", group=GP_DSP, tooltip="Toggle all chart-overlay elements: channel lines, projection, fill, markers, and direction label. Dashboard is controlled separately."),
    i_showFill=input.bool(True, "Show Fill", group=GP_DSP, tooltip="Toggle the semi-transparent fill between channel boundaries. Applies to both the solid channel and the dotted projection segments."),
    i_showDash=input.bool(True, "Show Dashboard", group=GP_DSP, tooltip="Toggle the dashboard table (top-right) showing scale periods, per-scale trends, consensus, channel levels, and breakout/retest narrative."),
    i_dashSz=input.int(12, "Dashboard Font Size", minval=6, maxval=50, group=GP_DSP, tooltip="Base font size for dashboard text. Header = size − 2, detail rows = size − 4. Also affects diamond markers and direction label. Minimum effective: 6. Default: 12."),
    i_dashPos=input.string("Top Right", "Dashboard Position", options=("Top Left", "Top Center", "Top Right", "Middle Left", "Middle Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"), group=GP_DSP, tooltip="Screen position of the dashboard table."),
    i_fillUp=input.color(color.new('#26A69A'), "Fill Up Color", group=GP_FILL, tooltip="Fill color between channel boundaries during an uptrend. Independent of channel line color — allows distinct visual layering."),
    i_fillDn=input.color(color.new('#EF5350'), "Fill Down Color", group=GP_FILL, tooltip="Fill color between channel boundaries during a downtrend. Independent of channel line color."),
    i_fillRng=input.color(color.new('#888888'), "Fill Range Color", group=GP_FILL, tooltip="Fill color between channel boundaries during a ranging market. Independent of channel line color."),
    i_fillTr=input.int(85, "Fill Transparency", minval=0, maxval=100, group=GP_FILL, tooltip="Channel fill transparency.\n\n0 = fully opaque (solid color).\n100 = fully invisible.\n\nValues 80–90 provide subtle shading without obscuring price action. Default: 85."),
    i_showBlk=input.bool(False, "Show Blocks", group=GP_BLK, tooltip="Toggle block overlay: colored bands for each structural block, dashed Hi/Lo lines, geometric mean dots, and GM connection line.\n\nBlocks are the foundational units of the trend analysis. This toggle makes them visible on the chart for educational and diagnostic purposes."),
    i_blkClr1=input.color(color.new('#7F77DD'), "Block Color (Even)", group=GP_BLK, tooltip="Background color for even-numbered blocks (0, 2, 4 ...)."),
    i_blkClr2=input.color(color.new('#1D9E75'), "Block Color (Odd)", group=GP_BLK, tooltip="Background color for odd-numbered blocks (1, 3, 5 ...)."),
    i_blkTr=input.int(90, "Block Transparency", minval=50, maxval=100, group=GP_BLK, tooltip="Transparency of block background bands.\n\n90 = subtle shading.\n100 = invisible (border only).\nDefault: 90."),
    i_blkHiClr=input.color(color.new('#E24B4A'), "Block High Color", group=GP_BLK, tooltip="Color of the dashed line marking the highest High within each block."),
    i_blkLoClr=input.color(color.new('#378ADD'), "Block Low Color", group=GP_BLK, tooltip="Color of the dashed line marking the lowest Low within each block."),
    i_blkGmClr=input.color(color.new('#EF9F27'), "GM Color", group=GP_BLK, tooltip="Color of the geometric mean markers and the line connecting them across blocks.\n\nGM = exp((ln(blockHi) + ln(blockLo)) / 2)\nThe log-midpoint central tendency of each block."),
    i_showAng=input.bool(False, "Show Angle Line", group=GP_BLK, tooltip="Toggle the ICS angle reference line: a straight line from the geometric mean of the oldest block in the monotonic segment to the newest, projected forward by Projection Offset bars.\n\nThis is the line whose slope, divided by σ, produces the displayed ICS angle."),
    i_angClr=input.color(color.new('#AFA9EC'), "Angle Line Color", group=GP_BLK, tooltip="Color of the angle reference line and its forward projection."),
    i_showAngLbl=input.bool(False, "Show Angle Label", group=GP_BLK, tooltip="Toggle the direction and angle label (e.g. ▼ DN −0.8°).\n\nWhen Show Angle Line is ON the label sits at the projection end of the angle line. When Show Angle Line is OFF the label falls back to the channel midpoint."),
    i_enableAlerts=input.bool(False, "Enable Alerts", group=GP_ALERTS, tooltip="Master toggle for 19 alert conditions (D · B · R · S · A).\n\nREQUIRES Calculation Bar = Live Bar. In Close Bar mode, alerts are auto-suppressed and a warning label is shown on the chart — because alerts must react to live state, and Close Bar intentionally lags by one bar.\n\nEnable this before creating alerts in TradingView's alert dialog. Default: OFF.")
):
    DIR_UP: int = 1
    DIR_DOWN: int = -1
    DIR_FLAT: int = 0

    SCALES: Persistent[list[int]] = array.from_items(3, 7, 13, 19, 29, 47)

    ST_INSIDE: int = 0
    ST_BO_UP: int = 1
    ST_RT_UP: int = 2
    ST_BO_DN: int = -1
    ST_RT_DN: int = -2







    _anchor: Persistent[int] = 0 if i_calcBar == 'Live Bar' else 1

    _i_en: Persistent[I18n] = I18n()
    _i_tr: Persistent[I18n] = I18n(lbl_period='Periyot', lbl_trend='Trend', lbl_agreement='Uyum', dir_up='YÜK', dir_dn='DÜŞ', dir_rng='YTY', st_bo_up='Yukarı Kırılım', st_bo_dn='Aşağı Kırılım', st_rt_up_broke_at='Yukarı retest · kırılım', st_rt_dn_broke_at='Aşağı retest · kırılım', st_inside='Kanal içinde', st_inside_dir_ch='Kanal içinde · yön değişti', st_inside_fail_up='Kanal içinde · başarısız yukarı kırılım', st_inside_fail_dn='Kanal içinde · başarısız aşağı kırılım', conn_at='@', conn_gap='(sıçrama)', conn_retested='· yeniden test', conn_now='şimdi', dist_above_ceiling='% tavan üstü', dist_below_floor='% taban altı', dist_from_floor='% tabandan', dist_to_ceiling='% tavana', tip_header='ST-EP06 — Smart Trader, 6. Bölüm: İzotropik Trend Çizgileri.\n\nσ ile normalize edilmiş koordinat uzayında (ICS) çoklu ölçek trend kanalları. Başlık fiyatı her zaman canlı kapanıştır (Live Exception). Diğer tüm değerler Calculation Bar ile seçilen bara sabitlenir — Live Bar modunda [0], Close Bar modunda [1].', tip_period="6 ölçekli paralel analiz için blok periyotları.\n\nHer ölçek geçmişi bloklara böler ve her bloğu log-orta nokta geometrik ortalamasına indirir.\n\n'19' sütunu = birincil motor (Periyot girdinizi kullanır). Diğerleri ölçekler arası uzlaşı için sabit periyotlar kullanır.", tip_trend="Blok geometrik ortalamalarının en uzun monoton segmentinden ölçek başına trend yönü.\n\n▲ YÜK · ▼ DÜŞ · ◈ YTY\n\nYTY = ±Aralık Eşiği içinde mutlak ICS açısı. Açı, σ-normalize eğimin arctan'ıdır ve piyasalar arasında karşılaştırılabilirdir.", tip_agreement='Ölçekler arası uzlaşı.\n\n6 ölçekten kaçının yön üzerinde anlaştığı, birincil kanal ▲ (tavan) ve ▼ (taban) ile gösterilir.\n\n5/6 veya 6/6 = her zaman çözünürlüğünde görünen yapısal trend.', tip_narrative="Kırılım / Retest anlatımı (birincil motor, ölçek 19).\n\nTek satırlık durum + mesafe özeti:\n\n• Kanal içinde — % tabandan · % tavana (toplamı 100%)\n• Yukarı/Aşağı Kırılım — fiyat kanaldan çıktı, kırılım fiyatı ve sınırın ötesindeki % ile gösterilir\n• Retest — sınırdan ≥1σ uzaklaştıktan sonra fiyat geri dönüp sınırı test etti\n\n✓ = onaylı (retest edildi ve ≥1σ geri döndü).\n(sıçrama) = fiyat tek hamlede tüm kanalı aştı.\n\nTüm mesafeler kanal genişliğinin %'sidir (ölçekten bağımsız). σ eşikleri dinamiktir (Yang-Zhang).", lbl_close='Kapanış', lbl_ceiling='Tavan', lbl_floor='Taban', lbl_ext='Uzanım', lbl_trend_tip='Trend', lbl_angle='Açı', lbl_blocks='Blok', alert_warn='Alarmlar için Calculation Bar = Live Bar olmalı', alert_warn_tip="Alarmlar şu anda etkin ancak Calculation Bar = Close Bar.\n\nClose Bar modu hesaplamaları son kapanan bara sabitler ve bu, canlı alarmlarla anlamsal olarak bağdaşmaz. Alarmları gecikmesiz tetiklemek için gösterge ayarlarını açıp Calculation Bar değerini Live Bar olarak değiştir.\n\nO zamana kadar tüm alertcondition'lar bastırılır.")
    _i_ar: Persistent[I18n] = I18n(lbl_period='فترة', lbl_trend='اتجاه', lbl_agreement='توافق', dir_up='صعود', dir_dn='هبوط', dir_rng='عرضي', st_bo_up='اختراق صاعد', st_bo_dn='اختراق هابط', st_rt_up_broke_at='اختبار صاعد · اختراق', st_rt_dn_broke_at='اختبار هابط · اختراق', st_inside='داخل القناة', st_inside_dir_ch='داخل القناة · تغيّر الاتجاه', st_inside_fail_up='داخل القناة · اختراق صاعد فاشل', st_inside_fail_dn='داخل القناة · اختراق هابط فاشل', conn_at='@', conn_gap='(فجوة)', conn_retested='· أُعيد اختباره', conn_now='الآن', dist_above_ceiling='% فوق السقف', dist_below_floor='% تحت الأرضية', dist_from_floor='% من الأرضية', dist_to_ceiling='% إلى السقف', tip_header='ST-EP06 — Smart Trader، الحلقة 6: خطوط الاتجاه الإيزوتروبية.\n\nقنوات اتجاه متعددة المقاييس في فضاء إحداثيات معياري σ (ICS). سعر العنوان دائماً إغلاق مباشر (Live Exception). جميع القيم الأخرى مرجعها الشمعة المختارة عبر Calculation Bar — [0] في وضع Live Bar، [1] في وضع Close Bar.', tip_period="فترات الكتل للتحليل المتوازي على 6 مقاييس.\n\nكل مقياس يقسم التاريخ إلى كتل ويختزل كل كتلة إلى متوسط هندسي لنقطة منتصف السجل.\n\nعمود '19' = المحرك الأساسي (يستخدم مدخل الفترة لديك). الأخرى تستخدم فترات ثابتة للتوافق بين المقاييس.", tip_trend='اتجاه الترند لكل مقياس من أطول مقطع رتيب لمتوسطات الكتل الهندسية.\n\n▲ صعود · ▼ هبوط · ◈ عرضي\n\nعرضي = زاوية ICS المطلقة ضمن ±عتبة النطاق. الزاوية هي أركتان للميل المعياري بـσ، قابلة للمقارنة عبر الأسواق.', tip_agreement='التوافق بين المقاييس.\n\nكم عدد المقاييس الستة المتفقة على الاتجاه، معروضاً مع القناة الأساسية ▲ (السقف) و▼ (الأرضية).\n\n5/6 أو 6/6 = اتجاه هيكلي مرئي في كل دقة زمنية.', tip_narrative='سرد الاختراق / إعادة الاختبار (المحرك الأساسي، مقياس 19).\n\nسطر واحد للحالة + ملخص المسافة:\n\n• داخل القناة — % من الأرضية · % إلى السقف (المجموع 100%)\n• اختراق صاعد/هابط — السعر خرج من القناة، معروض مع سعر الاختراق و% خارج الحدود\n• إعادة الاختبار — بعد التحرك ≥1σ عن الحد، عاد السعر ليختبره\n\n✓ = مؤكّد (أُعيد اختباره وارتد ≥1σ).\n(فجوة) = السعر عبر القناة بالكامل في حركة واحدة.\n\nجميع المسافات % من عرض القناة (مستقلة عن المقياس). عتبات σ ديناميكية (يانغ-زانغ).', lbl_close='إغلاق', lbl_ceiling='السقف', lbl_floor='الأرضية', lbl_ext='امتداد', lbl_trend_tip='اتجاه', lbl_angle='زاوية', lbl_blocks='كتل', alert_warn='التنبيهات تتطلب Calculation Bar = Live Bar', alert_warn_tip='التنبيهات مفعّلة حالياً لكن Calculation Bar معيّن على Close Bar.\n\nوضع Close Bar يثبّت الحسابات على آخر شمعة مغلقة، وهذا لا يتوافق دلالياً مع التنبيهات الحيّة. لإطلاق التنبيهات دون تأخير، افتح إعدادات المؤشر وغيّر Calculation Bar إلى Live Bar.\n\nحتى ذلك الحين، تُكتم جميع alertcondition.')
    _i_ru: Persistent[I18n] = I18n(lbl_period='Период', lbl_trend='Тренд', lbl_agreement='Согласие', dir_up='РОСТ', dir_dn='СПАД', dir_rng='ФЛЭТ', st_bo_up='Пробой вверх', st_bo_dn='Пробой вниз', st_rt_up_broke_at='Ретест вверх · пробой', st_rt_dn_broke_at='Ретест вниз · пробой', st_inside='Внутри канала', st_inside_dir_ch='Внутри канала · смена направления', st_inside_fail_up='Внутри канала · неудачный пробой вверх', st_inside_fail_dn='Внутри канала · неудачный пробой вниз', conn_at='@', conn_gap='(гэп)', conn_retested='· ретест', conn_now='сейчас', dist_above_ceiling='% над потолком', dist_below_floor='% под полом', dist_from_floor='% от пола', dist_to_ceiling='% до потолка', tip_header='ST-EP06 — Smart Trader, Эпизод 6: Изотропные линии тренда.\n\nМногомасштабные трендовые каналы в σ-нормализованном координатном пространстве (ICS). Цена заголовка всегда живое закрытие (Live Exception). Все остальные значения привязаны к свече, выбранной через Calculation Bar — [0] в режиме Live Bar, [1] в режиме Close Bar.', tip_period="Периоды блоков для параллельного анализа на 6 масштабах.\n\nКаждый масштаб разбивает историю на блоки и сводит каждый блок к геометрическому среднему лог-середины.\n\nКолонка '19' = основной движок (использует ваш ввод Периода). Остальные используют фиксированные периоды для межмасштабного согласия.", tip_trend='Направление тренда по каждому масштабу из самого длинного монотонного сегмента геометрических средних блоков.\n\n▲ РОСТ · ▼ СПАД · ◈ ФЛЭТ\n\nФЛЭТ = абсолютный ICS-угол в пределах ±Порога Диапазона. Угол — арктангенс σ-нормализованного наклона, сопоставимого между рынками.', tip_agreement='Межмасштабное согласие.\n\nСколько из 6 масштабов согласны по направлению, показано с основным каналом ▲ (потолок) и ▼ (пол).\n\n5/6 или 6/6 = структурный тренд виден на каждом временном разрешении.', tip_narrative='Нарратив пробоя / ретеста (основной движок, масштаб 19).\n\nОднострочная сводка состояния + дистанции:\n\n• Внутри — % от пола · % до потолка (сумма 100%)\n• Пробой вверх/вниз — цена вышла из канала, показано с ценой пробоя и % за границей\n• Ретест — после движения ≥1σ от границы цена вернулась её проверить\n\n✓ = подтверждено (ретест и отскок ≥1σ).\n(гэп) = цена пересекла весь канал одним движением.\n\nВсе дистанции — % ширины канала (независимы от масштаба). Пороги σ динамические (Янг-Чжан).', lbl_close='Закрытие', lbl_ceiling='Потолок', lbl_floor='Пол', lbl_ext='Расширение', lbl_trend_tip='Тренд', lbl_angle='Угол', lbl_blocks='Блоки', alert_warn='Оповещениям требуется Calculation Bar = Live Bar', alert_warn_tip='Оповещения включены, но Calculation Bar установлен на Close Bar.\n\nРежим Close Bar привязывает расчёты к последней закрытой свече, что семантически несовместимо с живыми оповещениями. Чтобы оповещения срабатывали без задержки, откройте настройки индикатора и смените Calculation Bar на Live Bar.\n\nДо этого все alertcondition подавляются.')
    _i_it: Persistent[I18n] = I18n(lbl_period='Periodo', lbl_trend='Trend', lbl_agreement='Consenso', dir_up='SU', dir_dn='GIÙ', dir_rng='LAT', st_bo_up='Rottura rialzista', st_bo_dn='Rottura ribassista', st_rt_up_broke_at='Retest al rialzo · rottura', st_rt_dn_broke_at='Retest al ribasso · rottura', st_inside='Dentro il canale', st_inside_dir_ch='Dentro il canale · direzione cambiata', st_inside_fail_up='Dentro il canale · rottura rialzista fallita', st_inside_fail_dn='Dentro il canale · rottura ribassista fallita', conn_at='@', conn_gap='(gap)', conn_retested='· ritestato', conn_now='ora', dist_above_ceiling='% sopra il tetto', dist_below_floor='% sotto il pavimento', dist_from_floor='% dal pavimento', dist_to_ceiling='% al tetto', tip_header="ST-EP06 — Smart Trader, Episodio 6: Linee di Tendenza Isotropiche.\n\nCanali di tendenza multi-scala in spazio coordinate normalizzato σ (ICS). Il prezzo dell'intestazione è sempre la chiusura live (Live Exception). Tutti gli altri valori sono ancorati alla barra selezionata tramite Calculation Bar — [0] in modalità Live Bar, [1] in modalità Close Bar.", tip_period="Periodi dei blocchi per l'analisi parallela a 6 scale.\n\nOgni scala partiziona la storia in blocchi e riduce ciascuno alla media geometrica del log-midpoint.\n\nLa colonna '19' = motore primario (usa il tuo input Periodo). Le altre usano periodi fissi per il consenso tra scale.", tip_trend="Direzione di tendenza per scala dal segmento monotono più lungo delle medie geometriche dei blocchi.\n\n▲ SU · ▼ GIÙ · ◈ LAT\n\nLAT = angolo ICS assoluto entro ±Soglia di Range. L'angolo è l'arcotangente della pendenza normalizzata σ, confrontabile tra i mercati.", tip_agreement='Consenso tra scale.\n\nQuante delle 6 scale concordano sulla direzione, mostrato con il canale primario ▲ (tetto) e ▼ (pavimento).\n\n5/6 o 6/6 = tendenza strutturale visibile a ogni risoluzione temporale.', tip_narrative="Narrativa rottura / retest (motore primario, scala 19).\n\nRiassunto su una riga di stato + distanza:\n\n• Dentro — % dal pavimento · % al tetto (somma 100%)\n• Rottura su/giù — il prezzo è uscito dal canale, mostrato con prezzo di rottura e % oltre il confine\n• Retest — dopo essersi mosso ≥1σ dal confine, il prezzo è tornato a testarlo\n\n✓ = confermato (ritestato e rimbalzato ≥1σ).\n(gap) = il prezzo ha attraversato l'intero canale in un'unica mossa.\n\nTutte le distanze sono % della larghezza del canale (indipendenti dalla scala). Le soglie σ sono dinamiche (Yang-Zhang).", lbl_close='Chiusura', lbl_ceiling='Tetto', lbl_floor='Pavimento', lbl_ext='Estensione', lbl_trend_tip='Trend', lbl_angle='Angolo', lbl_blocks='Blocchi', alert_warn='Gli avvisi richiedono Calculation Bar = Live Bar', alert_warn_tip="Gli avvisi sono attualmente abilitati ma Calculation Bar è impostato su Close Bar.\n\nLa modalità Close Bar ancora i calcoli all'ultima barra chiusa, il che è semanticamente incompatibile con gli avvisi live. Per attivare gli avvisi senza ritardo, apri le impostazioni dell'indicatore e cambia Calculation Bar in Live Bar.\n\nFino ad allora, tutte le alertcondition sono soppresse.")
    _i_pt: Persistent[I18n] = I18n(lbl_period='Período', lbl_trend='Tendência', lbl_agreement='Consenso', dir_up='ALTA', dir_dn='BAIXA', dir_rng='LAT', st_bo_up='Rompimento de alta', st_bo_dn='Rompimento de baixa', st_rt_up_broke_at='Reteste de alta · rompimento', st_rt_dn_broke_at='Reteste de baixa · rompimento', st_inside='Dentro do canal', st_inside_dir_ch='Dentro do canal · direção mudou', st_inside_fail_up='Dentro do canal · rompimento de alta falhou', st_inside_fail_dn='Dentro do canal · rompimento de baixa falhou', conn_at='@', conn_gap='(gap)', conn_retested='· retestado', conn_now='agora', dist_above_ceiling='% acima do teto', dist_below_floor='% abaixo do piso', dist_from_floor='% do piso', dist_to_ceiling='% ao teto', tip_header='ST-EP06 — Smart Trader, Episódio 6: Linhas de Tendência Isotrópicas.\n\nCanais de tendência multi-escala em espaço de coordenadas normalizado por σ (ICS). O preço do cabeçalho é sempre o fechamento ao vivo (Live Exception). Todos os outros valores estão ancorados à barra selecionada via Calculation Bar — [0] no modo Live Bar, [1] no modo Close Bar.', tip_period="Períodos dos blocos para a análise paralela em 6 escalas.\n\nCada escala particiona o histórico em blocos e reduz cada um à média geométrica do log-midpoint.\n\nA coluna '19' = motor primário (usa seu input de Período). As outras usam períodos fixos para o consenso entre escalas.", tip_trend='Direção da tendência por escala do segmento monotônico mais longo das médias geométricas dos blocos.\n\n▲ ALTA · ▼ BAIXA · ◈ LAT\n\nLAT = ângulo ICS absoluto dentro de ±Limite de Range. O ângulo é o arctangente da inclinação normalizada por σ, comparável entre mercados.', tip_agreement='Consenso entre escalas.\n\nQuantas das 6 escalas concordam na direção, mostrado com o canal primário ▲ (teto) e ▼ (piso).\n\n5/6 ou 6/6 = tendência estrutural visível em toda resolução temporal.', tip_narrative='Narrativa de rompimento / reteste (motor primário, escala 19).\n\nResumo em uma linha de estado + distância:\n\n• Dentro — % do piso · % ao teto (soma 100%)\n• Rompimento de alta/baixa — o preço saiu do canal, mostrado com preço de rompimento e % além do limite\n• Reteste — após se mover ≥1σ do limite, o preço voltou para testá-lo\n\n✓ = confirmado (retestado e distanciou-se ≥1σ).\n(gap) = o preço atravessou todo o canal em um único movimento.\n\nTodas as distâncias são % da largura do canal (independentes da escala). Os limites σ são dinâmicos (Yang-Zhang).', lbl_close='Fechamento', lbl_ceiling='Teto', lbl_floor='Piso', lbl_ext='Extensão', lbl_trend_tip='Tendência', lbl_angle='Ângulo', lbl_blocks='Blocos', alert_warn='Alertas exigem Calculation Bar = Live Bar', alert_warn_tip='Os alertas estão atualmente ativados, mas Calculation Bar está definido como Close Bar.\n\nO modo Close Bar ancora os cálculos na última barra fechada, o que é semanticamente incompatível com alertas ao vivo. Para disparar alertas sem atraso, abra as configurações do indicador e altere Calculation Bar para Live Bar.\n\nAté lá, todos os alertcondition são suprimidos.')
    _i_zh: Persistent[I18n] = I18n(lbl_period='周期', lbl_trend='趋势', lbl_agreement='一致度', dir_up='上涨', dir_dn='下跌', dir_rng='横盘', st_bo_up='向上突破', st_bo_dn='向下突破', st_rt_up_broke_at='上破回踩 · 突破', st_rt_dn_broke_at='下破回踩 · 突破', st_inside='通道内', st_inside_dir_ch='通道内 · 方向改变', st_inside_fail_up='通道内 · 向上突破失败', st_inside_fail_dn='通道内 · 向下突破失败', conn_at='@', conn_gap='(跳空)', conn_retested='· 回踩', conn_now='现在', dist_above_ceiling='% 高于顶部', dist_below_floor='% 低于底部', dist_from_floor='% 距底部', dist_to_ceiling='% 距顶部', tip_header='ST-EP06 — Smart Trader 第 6 集：各向同性趋势线。\n\n基于 σ 标准化坐标空间（ICS）的多尺度趋势通道。标题价格始终为实时收盘（Live Exception）。所有其他值锚定于通过 Calculation Bar 选择的 K 线 — Live Bar 模式为 [0]，Close Bar 模式为 [1]。', tip_period="用于 6 尺度并行分析的区块周期。\n\n每个尺度将历史划分为区块，并将每个区块归约为对数中点几何平均值。\n\n'19' 列 = 主引擎（使用您的周期输入）。其他列使用固定周期以实现跨尺度共识。", tip_trend='每个尺度的趋势方向，来自区块几何平均值最长的单调段。\n\n▲ 上涨 · ▼ 下跌 · ◈ 横盘\n\n横盘 = ±范围阈值内的绝对 ICS 角度。角度是 σ 标准化斜率的反正切，可跨市场比较。', tip_agreement='跨尺度一致度。\n\n6 个尺度中有多少在方向上一致，与主通道 ▲（顶部）和 ▼（底部）一同显示。\n\n5/6 或 6/6 = 在每个时间分辨率上均可见的结构性趋势。', tip_narrative='突破 / 回踩叙述（主引擎，尺度 19）。\n\n一行状态 + 距离摘要：\n\n• 通道内 — % 距底部 · % 距顶部（总和 100%）\n• 向上/下突破 — 价格离开通道，显示突破价及超出边界的百分比\n• 回踩 — 价格从边界移动 ≥1σ 后，返回测试边界\n\n✓ = 已确认（回踩后反弹 ≥1σ）。\n(跳空) = 价格在一次移动中穿越整个通道。\n\n所有距离均为通道宽度的百分比（与尺度无关）。σ 阈值为动态（Yang-Zhang）。', lbl_close='收盘', lbl_ceiling='顶部', lbl_floor='底部', lbl_ext='延伸', lbl_trend_tip='趋势', lbl_angle='角度', lbl_blocks='区块', alert_warn='警报需要 Calculation Bar = Live Bar', alert_warn_tip='警报当前已启用，但 Calculation Bar 设置为 Close Bar。\n\nClose Bar 模式将计算锚定在最后收盘的 K 线上，这与实时警报在语义上不兼容。为了让警报无延迟触发，请打开指标设置并将 Calculation Bar 更改为 Live Bar。\n\n在此之前，所有 alertcondition 都被抑制。')

    __block_result__ = na
    __switch__ = i_lang
    if __switch__ == "Türkçe":
        __block_result__ = _i_tr
    elif __switch__ == "العربية":
        __block_result__ = _i_ar
    elif __switch__ == "Русский":
        __block_result__ = _i_ru
    elif __switch__ == "Italiano":
        __block_result__ = _i_it
    elif __switch__ == "Português (BR)":
        __block_result__ = _i_pt
    elif __switch__ == "中文":
        __block_result__ = _i_zh
    else:
        __block_result__ = _i_en
    _L: I18n = __block_result__

    def f_sty(s: str):
        __block_result_1__ = na
        __switch__ = s
        if __switch__ == "Dashed":
            __block_result_1__ = line.style_dashed
        elif __switch__ == "Dotted":
            __block_result_1__ = line.style_dotted
        else:
            __block_result_1__ = line.style_solid
        return __block_result_1__

    def f_dClr(d: int):
        return i_clrUp if d == DIR_UP else i_clrDn if d == DIR_DOWN else i_clrRng

    def f_dStr(d: int, L: I18n):
        return '▲ ' + L.dir_up if d == DIR_UP else '▼ ' + L.dir_dn if d == DIR_DOWN else '◈ ' + L.dir_rng

    def f_fClr(d: int):
        return i_fillUp if d == DIR_UP else i_fillDn if d == DIR_DOWN else i_fillRng

    def f_icsLine(p1: float, x1: int, p2: float, x2: int, targetX: int, sig: float):
        out: float = p1
        if x1 != x2 and p1 > 0 and (p2 > 0) and (sig > MIN_SIGMA):
            y1: float = math.log(p1) / sig
            y2: float = math.log(p2) / sig
            yT: float = y1 + (y2 - y1) * (targetX - x1) / (x2 - x1)
            out = math.exp(yT * sig)
        return out

    def f_icsAngle(p1: float, x1: int, p2: float, x2: int, sig: float):
        out: float = 0.0
        if x1 != x2 and p1 > 0 and (p2 > 0) and (sig > MIN_SIGMA):
            y1: float = math.log(p1) / sig
            y2: float = math.log(p2) / sig
            out = math.atan((y2 - y1) / (x2 - x1)) * 180.0 / PI
        return out

    def f_icsPos(p: float, pLo: float, pHi: float, sig: float):
        out: float = 0.5
        if p > 0 and pLo > 0 and (pHi > 0) and (pHi > pLo) and (sig > MIN_SIGMA):
            y: float = math.log(p) / sig
            yLo: float = math.log(pLo) / sig
            yHi: float = math.log(pHi) / sig
            out = (y - yLo) / (yHi - yLo)
        return out

    _yzOR: float = math.log(open[_anchor] / nz(close[_anchor + 1], open[_anchor]))
    _yzCO: float = math.log(close[_anchor] / open[_anchor])
    _yzHO: float = math.log(high[_anchor] / open[_anchor])
    _yzHC: float = math.log(high[_anchor] / close[_anchor])
    _yzLO: float = math.log(low[_anchor] / open[_anchor])
    _yzLC: float = math.log(low[_anchor] / close[_anchor])

    _sqOR: float = ta.variance(_yzOR, i_sigmaLen)
    _sqCO: float = ta.variance(_yzCO, i_sigmaLen)
    _sqRS: float = ta.sma(_yzHO * _yzHC + _yzLO * _yzLC, i_sigmaLen)

    _k: float = 0.34 / (1.34 + (i_sigmaLen + 1.0) / math.max(i_sigmaLen - 1.0, 1.0))
    _sq: float = nz(_sqOR) + _k * nz(_sqCO) + (1.0 - _k) * nz(_sqRS)
    sigma: float = math.max(math.sqrt(math.max(_sq, 0.0)), MIN_SIGMA)

    _hhS: Series[float] = ta.highest(high, i_period)
    _llS: Series[float] = ta.lowest(low, i_period)
    max_bars_back(_hhS, 2500)
    max_bars_back(_llS, 2500)

    _bGm: Persistent[list[float]] = array.new_float()
    _bHi: Persistent[list[float]] = array.new_float()
    _bLo: Persistent[list[float]] = array.new_float()
    _bCx: Persistent[list[int]] = array.new_int()

    array.clear(_bGm)
    array.clear(_bHi)
    array.clear(_bLo)
    array.clear(_bCx)

    _ok: bool = bar_index >= i_groups * i_period + _anchor

    if _ok:
        for i in pine_range(0, i_groups - 1):
            off: int = _anchor + i * i_period
            hi: float = _hhS[off]
            lo: float = _llS[off]
            array.push(_bGm, math.exp((math.log(hi) + math.log(lo)) / 2.0) if hi > 0 and lo > 0 else na)
            array.push(_bHi, hi)
            array.push(_bLo, lo)
            array.push(_bCx, bar_index - off - cast_int(i_period / 2))

    _dir: Series[int] = DIR_FLAT
    _ang: float = 0.0
    _seg: int = 0
    _chUp: float = na(float)
    _chLo: float = na(float)

    if _ok and array.size(_bGm) >= 2:
        g0: float = array.get(_bGm, 0)
        g1: float = array.get(_bGm, 1)
        if not na(g0) and (not na(g1)) and (g0 != g1):
            pd: int = DIR_UP if g0 > g1 else DIR_DOWN
            _seg = 1
            if i_groups > 2:
                for i in pine_range(1, i_groups - 2):
                    a: float = array.get(_bGm, i)
                    b: float = array.get(_bGm, i + 1)
                    if not na(a) and (not na(b)):
                        if (DIR_UP if a > b else DIR_DOWN if a < b else DIR_FLAT) == pd:
                            _seg = i + 1
                        else:
                            break
                    else:
                        break

            sig: float = math.max(nz(sigma, MIN_SIGMA), MIN_SIGMA)
            if array.size(_bGm) > _seg:
                _ang = f_icsAngle(array.get(_bGm, _seg), array.get(_bCx, _seg), array.get(_bGm, 0), array.get(_bCx, 0), sig)

            _dir = DIR_FLAT if math.abs(_ang) <= i_thresh else pd

            if _seg >= 1 and array.size(_bHi) > _seg:
                fHH: float = na(float)
                fLH: float = na(float)
                fHL: float = na(float)
                fLL: float = na(float)
                xHH: int = na(int)
                xLH: int = na(int)
                xHL: int = na(int)
                xLL: int = na(int)
                for i in pine_range(0, _seg):
                    h: float = array.get(_bHi, i)
                    l: float = array.get(_bLo, i)
                    x: int = array.get(_bCx, i)
                    if na(fHH) or h > fHH:
                        fHH = h
                        xHH = x
                    if na(fLH) or h < fLH:
                        fLH = h
                        xLH = x
                    if na(fHL) or l > fHL:
                        fHL = l
                        xHL = x
                    if na(fLL) or l < fLL:
                        fLL = l
                        xLL = x

                now: int = bar_index - _anchor
                if _dir == DIR_UP:
                    _chUp = f_icsLine(fLH, xLH, fHH, xHH, now, sig)
                    _chLo = f_icsLine(fLL, xLL, fHL, xHL, now, sig)
                elif _dir == DIR_DOWN:
                    _chUp = f_icsLine(fHH, xHH, fLH, xLH, now, sig)
                    _chLo = f_icsLine(fHL, xHL, fLL, xLL, now, sig)
                else:
                    _chUp = nz(fHH)
                    _chLo = nz(fLL)

    def f_analyze(gm: list[float], hi: list[float], lo: list[float], cx: list[int], groups: int, thresh: float, sig: float):
        d: int = DIR_FLAT
        a: float = 0.0
        se: int = 0
        cu: float = na(float)
        cd: float = na(float)
        if array.size(gm) >= 2:
            g0: float = array.get(gm, 0)
            g1: float = array.get(gm, 1)
            if not na(g0) and (not na(g1)) and (g0 != g1):
                pd: int = DIR_UP if g0 > g1 else DIR_DOWN
                se = 1
                if groups > 2:
                    for i in pine_range(1, groups - 2):
                        if i + 1 >= array.size(gm):
                            break
                        gA: float = array.get(gm, i)
                        gB: float = array.get(gm, i + 1)
                        if not na(gA) and (not na(gB)):
                            if (DIR_UP if gA > gB else DIR_DOWN if gA < gB else DIR_FLAT) == pd:
                                se = i + 1
                            else:
                                break
                        else:
                            break
                if array.size(gm) > se:
                    a = f_icsAngle(array.get(gm, se), array.get(cx, se), array.get(gm, 0), array.get(cx, 0), sig)
                d = DIR_FLAT if math.abs(a) <= thresh else pd
                if se >= 1 and array.size(hi) > se:
                    fHH: float = na(float)
                    fLH: float = na(float)
                    fHL: float = na(float)
                    fLL: float = na(float)
                    xHH: int = na(int)
                    xLH: int = na(int)
                    xHL: int = na(int)
                    xLL: int = na(int)
                    for i in pine_range(0, se):
                        _h: float = array.get(hi, i)
                        _l: float = array.get(lo, i)
                        _x: int = array.get(cx, i)
                        if na(fHH) or _h > fHH:
                            fHH = _h
                            xHH = _x
                        if na(fLH) or _h < fLH:
                            fLH = _h
                            xLH = _x
                        if na(fHL) or _l > fHL:
                            fHL = _l
                            xHL = _x
                        if na(fLL) or _l < fLL:
                            fLL = _l
                            xLL = _x
                    n: int = bar_index - _anchor
                    if d == DIR_UP:
                        cu = f_icsLine(fLH, xLH, fHH, xHH, n, sig)
                        cd = f_icsLine(fLL, xLL, fHL, xHL, n, sig)
                    elif d == DIR_DOWN:
                        cu = f_icsLine(fHH, xHH, fLH, xLH, n, sig)
                        cd = f_icsLine(fHL, xHL, fLL, xLL, n, sig)
                    else:
                        cu = nz(fHH)
                        cd = nz(fLL)
        return TrendResult(d, a, se, cu, cd)

    def f_compute(hhSer: Series[float], llSer: Series[float], per: int, grp: int, thr: float, sig: float):
        g: list[float] = array.new_float()
        h: list[float] = array.new_float()
        l: list[float] = array.new_float()
        x: list[int] = array.new_int()
        hasData: bool = bar_index >= grp * per + _anchor
        if hasData:
            for i in pine_range(0, grp - 1):
                off: int = _anchor + i * per
                hi: float = hhSer[off]
                lo: float = llSer[off]
                array.push(g, math.exp((math.log(hi) + math.log(lo)) / 2.0) if hi > 0 and lo > 0 else na)
                array.push(h, hi)
                array.push(l, lo)
                array.push(x, bar_index - off - cast_int(per / 2))
        return f_analyze(g, h, l, x, grp, thr, sig) if hasData else TrendResult()

    _hh3: float = ta.highest(high, 3)
    _ll3: float = ta.lowest(low, 3)
    _hh7: float = ta.highest(high, 7)
    _ll7: float = ta.lowest(low, 7)
    _hh13: float = ta.highest(high, 13)
    _ll13: float = ta.lowest(low, 13)
    _hh19: float = ta.highest(high, 19)
    _ll19: float = ta.lowest(low, 19)
    _hh29: float = ta.highest(high, 29)
    _ll29: float = ta.lowest(low, 29)
    _hh47: float = ta.highest(high, 47)
    _ll47: float = ta.lowest(low, 47)

    max_bars_back(_hh3, 500)
    max_bars_back(_ll3, 500)
    max_bars_back(_hh7, 500)
    max_bars_back(_ll7, 500)
    max_bars_back(_hh13, 500)
    max_bars_back(_ll13, 500)
    max_bars_back(_hh19, 500)
    max_bars_back(_ll19, 500)
    max_bars_back(_hh29, 500)
    max_bars_back(_ll29, 500)
    max_bars_back(_hh47, 500)
    max_bars_back(_ll47, 500)

    _trSig: float = math.max(nz(sigma, MIN_SIGMA), MIN_SIGMA)

    _tr3: TrendResult = f_compute(_hh3, _ll3, 3, i_groups, i_thresh, _trSig)
    _tr7: TrendResult = f_compute(_hh7, _ll7, 7, i_groups, i_thresh, _trSig)
    _tr13: TrendResult = f_compute(_hh13, _ll13, 13, i_groups, i_thresh, _trSig)
    _tr29: TrendResult = f_compute(_hh29, _ll29, 29, i_groups, i_thresh, _trSig)
    _tr47: TrendResult = f_compute(_hh47, _ll47, 47, i_groups, i_thresh, _trSig)

    _tr19: TrendResult = f_compute(_hh19, _ll19, 19, i_groups, i_thresh, _trSig)

    _trends: list[TrendResult] = array.from_items(_tr3, _tr7, _tr13, _tr19, _tr29, _tr47)

    _cUp: Series[int] = 0
    _cDn: Series[int] = 0
    _cFlat: Series[int] = 0
    for i in pine_range(0, 5):
        td: int = array.get(_trends, i).dir
        if td == DIR_UP:
            _cUp += 1
        elif td == DIR_DOWN:
            _cDn += 1
        else:
            _cFlat += 1

    _extPos: float = f_icsPos(nz(close[_anchor]), _chLo, _chUp, _trSig)

    _boState: PersistentSeries[int] = ST_INSIDE
    _boConfirm: PersistentSeries[bool] = False
    _boDistanced: Persistent[bool] = False
    _boGapped: PersistentSeries[bool] = False
    _boPrice: Persistent[float] = na(float)
    _rtPrice: Persistent[float] = na(float)
    _prevBDir: Persistent[int] = DIR_FLAT
    _retFrom: PersistentSeries[int] = 0

    _distUp: float = math.abs(math.log(nz(close[_anchor])) - math.log(_chUp)) / _trSig if not na(_chUp) and nz(close[_anchor]) > 0 and (_chUp > 0) and (_trSig > MIN_SIGMA) else 0.0
    _distDn: float = math.abs(math.log(nz(close[_anchor])) - math.log(_chLo)) / _trSig if not na(_chLo) and nz(close[_anchor]) > 0 and (_chLo > 0) and (_trSig > MIN_SIGMA) else 0.0

    _dirReset: bool = False

    if _ok and (not na(_chUp)) and (not na(_chLo)):
        _dirChg: bool = _dir != _prevBDir and _prevBDir != DIR_FLAT
        _prevBDir = _dir

        if _dirChg:
            _dirReset = True
            _boState = ST_INSIDE
            _boConfirm = False
            _boDistanced = False
            _boGapped = False
            _boPrice = na
            _rtPrice = na
            _retFrom = 0
        else:
            __switch_2__ = _boState
            if __switch_2__ == ST_INSIDE:
                if _extPos > 1.0:
                    _boState = ST_BO_UP
                    _boPrice = _chUp
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                    _rtPrice = na
                    _retFrom = 0
                elif _extPos < 0.0:
                    _boState = ST_BO_DN
                    _boPrice = _chLo
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                    _rtPrice = na
                    _retFrom = 0
            elif __switch_2__ == ST_BO_UP:
                if _distUp >= 1.0:
                    _boDistanced = True
                if _extPos < 0.0:
                    _boState = ST_BO_DN
                    _boPrice = _chLo
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = True
                    _rtPrice = na
                    _retFrom = 0
                elif _extPos <= 1.0:
                    _boState = ST_INSIDE
                    _retFrom = 1
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                elif _boDistanced and _distUp < 1.0:
                    _boState = ST_RT_UP
                    _rtPrice = nz(close[_anchor])
                    _boGapped = False
            elif __switch_2__ == ST_RT_UP:
                if _extPos < 0.0:
                    _boState = ST_BO_DN
                    _boPrice = _chLo
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = True
                    _rtPrice = na
                    _retFrom = 0
                elif _extPos <= 1.0:
                    _boState = ST_INSIDE
                    _retFrom = 1
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                elif _distUp >= 1.0:
                    _boState = ST_BO_UP
                    _boConfirm = True
                    _boDistanced = True
                    _boGapped = False
            elif __switch_2__ == ST_BO_DN:
                if _distDn >= 1.0:
                    _boDistanced = True
                if _extPos > 1.0:
                    _boState = ST_BO_UP
                    _boPrice = _chUp
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = True
                    _rtPrice = na
                    _retFrom = 0
                elif _extPos >= 0.0:
                    _boState = ST_INSIDE
                    _retFrom = -1
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                elif _boDistanced and _distDn < 1.0:
                    _boState = ST_RT_DN
                    _rtPrice = nz(close[_anchor])
                    _boGapped = False
            elif __switch_2__ == ST_RT_DN:
                if _extPos > 1.0:
                    _boState = ST_BO_UP
                    _boPrice = _chUp
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = True
                    _rtPrice = na
                    _retFrom = 0
                elif _extPos >= 0.0:
                    _boState = ST_INSIDE
                    _retFrom = -1
                    _boConfirm = False
                    _boDistanced = False
                    _boGapped = False
                elif _distDn >= 1.0:
                    _boState = ST_BO_DN
                    _boConfirm = True
                    _boDistanced = True
                    _boGapped = False

    _upLn: Persistent[Line] = na(Line)
    _loLn: Persistent[Line] = na(Line)
    _upPj: Persistent[Line] = na(Line)
    _loPj: Persistent[Line] = na(Line)
    _chFill: Persistent[LineFill] = na(LineFill)
    _pjFill: Persistent[LineFill] = na(LineFill)
    _lbl: Persistent[Label] = na(Label)
    _mkUp: Persistent[Label] = na(Label)
    _mkLo: Persistent[Label] = na(Label)
    _dash: Persistent[Table] = na(Table)

    _blkBoxes: Persistent[list[Box]] = array.new_box()
    _blkHiLns: Persistent[list[Line]] = array.new_line()
    _blkLoLns: Persistent[list[Line]] = array.new_line()
    _blkGmLbs: Persistent[list[Label]] = array.new_label()
    _blkGmLns: Persistent[list[Line]] = array.new_line()

    _angLn: Persistent[Line] = na(Line)
    _angPj: Persistent[Line] = na(Line)

    if barstate.islastconfirmedhistory or barstate.islast:
        line.delete(_upLn)
        line.delete(_loLn)
        line.delete(_upPj)
        line.delete(_loPj)
        linefill.delete(_chFill)
        linefill.delete(_pjFill)
        label.delete(_lbl)
        label.delete(_mkUp)
        label.delete(_mkLo)
        _upLn = na
        _loLn = na
        _upPj = na
        _loPj = na
        _chFill = na
        _pjFill = na
        _lbl = na
        _mkUp = na
        _mkLo = na

        line.delete(_angLn)
        line.delete(_angPj)
        _angLn = na
        _angPj = na

        for bx in _blkBoxes:
            box.delete(bx)
        array.clear(_blkBoxes)
        for ln in _blkHiLns:
            line.delete(ln)
        array.clear(_blkHiLns)
        for ln in _blkLoLns:
            line.delete(ln)
        array.clear(_blkLoLns)
        for lb in _blkGmLbs:
            label.delete(lb)
        array.clear(_blkGmLbs)
        for ln in _blkGmLns:
            line.delete(ln)
        array.clear(_blkGmLns)

        if i_showBlk and _ok and (array.size(_bGm) >= 1):
            _pvGmY: float = na(float)
            _pvGmX: int = na(int)
            _nBlk: int = math.min(i_groups, array.size(_bGm))
            for i in pine_range(0, _nBlk - 1):
                bOff: int = _anchor + i * i_period
                bRight: int = bar_index - bOff
                bLeft: int = bRight - i_period + 1
                bHi: float = array.get(_bHi, i)
                bLo: float = array.get(_bLo, i)
                bGm: float = array.get(_bGm, i)
                bCx: int = array.get(_bCx, i)

                if not na(bHi) and (not na(bLo)):
                    cBlk: Color = i_blkClr1 if i % 2 == 0 else i_blkClr2
                    array.push(_blkBoxes, box.new(bLeft, bHi, bRight, bLo, border_color=color.new(cBlk, math.max(i_blkTr - 25, 0)), bgcolor=color.new(cBlk, i_blkTr), border_width=1, border_style=line.style_dashed))
                    array.push(_blkHiLns, line.new(bLeft, bHi, bRight, bHi, color=color.new(i_blkHiClr, 40), width=1, style=line.style_dashed))
                    array.push(_blkLoLns, line.new(bLeft, bLo, bRight, bLo, color=color.new(i_blkLoClr, 40), width=1, style=line.style_dashed))

                if not na(bGm) and (not na(bCx)):
                    gmTip: str = 'Block ' + string.tostring(i) + '\nHi: ' + string.tostring(nz(bHi), format.mintick) + '\nLo: ' + string.tostring(nz(bLo), format.mintick) + '\nGM: ' + string.tostring(bGm, format.mintick) + '\nBars: ' + string.tostring(bLeft) + '..' + string.tostring(bRight)
                    array.push(_blkGmLbs, label.new(bCx, bGm, '◆', style=label.style_label_center, color=color.new(chart.bg_color, 100), textcolor=i_blkGmClr, size=math.max(i_dashSz - 2, 6), tooltip=gmTip))
                    if not na(_pvGmY) and (not na(_pvGmX)):
                        array.push(_blkGmLns, line.new(bCx, bGm, _pvGmX, _pvGmY, color=color.new(i_blkGmClr, 30), width=2, style=line.style_solid))
                    _pvGmY = bGm
                    _pvGmX = bCx

        if i_showCh and _ok and (_seg >= 1) and (array.size(_bHi) > _seg):
            hhV: float = na(float)
            lhV: float = na(float)
            hlV: float = na(float)
            llV: float = na(float)
            hhX: int = na(int)
            lhX: int = na(int)
            hlX: int = na(int)
            llX: int = na(int)
            for i in pine_range(0, _seg):
                h: float = array.get(_bHi, i)
                l: float = array.get(_bLo, i)
                x: int = array.get(_bCx, i)
                if na(hhV) or h > hhV:
                    hhV = h
                    hhX = x
                if na(lhV) or h < lhV:
                    lhV = h
                    lhX = x
                if na(hlV) or l > hlV:
                    hlV = l
                    hlX = x
                if na(llV) or l < llV:
                    llV = l
                    llX = x

            sLx: int = array.get(_bCx, _seg)
            sRx: int = array.get(_bCx, 0)
            uY1: float = na(float)
            uY2: float = na(float)
            lY1: float = na(float)
            lY2: float = na(float)

            if _dir == DIR_UP:
                uY1 = f_icsLine(lhV, lhX, hhV, hhX, sLx, _trSig)
                uY2 = f_icsLine(lhV, lhX, hhV, hhX, sRx, _trSig)
                lY1 = f_icsLine(llV, llX, hlV, hlX, sLx, _trSig)
                lY2 = f_icsLine(llV, llX, hlV, hlX, sRx, _trSig)
            elif _dir == DIR_DOWN:
                uY1 = f_icsLine(hhV, hhX, lhV, lhX, sLx, _trSig)
                uY2 = f_icsLine(hhV, hhX, lhV, lhX, sRx, _trSig)
                lY1 = f_icsLine(hlV, hlX, llV, llX, sLx, _trSig)
                lY2 = f_icsLine(hlV, hlX, llV, llX, sRx, _trSig)
            else:
                uY1 = nz(hhV)
                uY2 = nz(hhV)
                lY1 = nz(llV)
                lY2 = nz(llV)

            chClr: Color = f_dClr(_dir)
            ax: int = bar_index - _anchor
            uYa: float = f_icsLine(uY1, sLx, uY2, sRx, ax, _trSig)
            lYa: float = f_icsLine(lY1, sLx, lY2, sRx, ax, _trSig)

            _seX: int = ax
            _pjOk: bool = True
            if uY1 > lY1 and uYa <= lYa and (_trSig > MIN_SIGMA):
                _gsL: float = math.log(uY1) / _trSig - math.log(lY1) / _trSig
                _gsR: float = math.log(lYa) / _trSig - math.log(uYa) / _trSig
                _gsD: float = _gsL + _gsR
                if _gsD > 1e-10:
                    _seX = sLx + cast_int(math.round(_gsL / _gsD * (ax - sLx)))
                _pjOk = False

            _uSE: float = f_icsLine(uY1, sLx, uY2, sRx, _seX, _trSig)
            _lSE: float = f_icsLine(lY1, sLx, lY2, sRx, _seX, _trSig)

            if _seX > sLx:
                _upLn = line.new(sLx, uY1, _seX, _uSE, color=chClr, width=i_chW, style=f_sty(i_chSty))
                _loLn = line.new(sLx, lY1, _seX, _lSE, color=chClr, width=i_chW, style=f_sty(i_chSty))

            eX: int = ax + i_pjOff
            uYe: float = f_icsLine(uY1, sLx, uY2, sRx, eX, _trSig)
            lYe: float = f_icsLine(lY1, sLx, lY2, sRx, eX, _trSig)

            if _pjOk:
                if uYa > lYa and uYe < lYe and (_trSig > MIN_SIGMA):
                    _cgA: float = math.log(uYa) / _trSig - math.log(lYa) / _trSig
                    _cgE: float = math.log(uYe) / _trSig - math.log(lYe) / _trSig
                    _cgD: float = _cgA - _cgE
                    if _cgD > 1e-10:
                        eX = ax + cast_int(math.round(_cgA / _cgD * i_pjOff))
                        uYe = f_icsLine(uY1, sLx, uY2, sRx, eX, _trSig)
                        lYe = f_icsLine(lY1, sLx, lY2, sRx, eX, _trSig)

                _upPj = line.new(ax, uYa, eX, uYe, color=chClr, width=i_pjW, style=f_sty(i_pjSty))
                _loPj = line.new(ax, lYa, eX, lYe, color=chClr, width=i_pjW, style=f_sty(i_pjSty))

            if i_showFill:
                fc: Color = color.new(f_fClr(_dir), i_fillTr)
                if not na(_upLn) and (not na(_loLn)):
                    _chFill = linefill.new(_upLn, _loLn, fc)
                if not na(_upPj) and (not na(_loPj)):
                    _pjFill = linefill.new(_upPj, _loPj, fc)

            extAt1: float = f_icsPos(close[_anchor], lYa, uYa, _trSig)
            extPctTip: float = math.round(extAt1 * 100)
            extTipSign: str = '+' if extPctTip > 100 else ''
            tip: str = _L.lbl_close + '[' + string.tostring(_anchor) + ']: ' + string.tostring(close[_anchor], format.mintick) + '\n' + _L.lbl_ceiling + ' ▲: ' + string.tostring(uYa, format.mintick) + '\n' + _L.lbl_floor + ' ▼: ' + string.tostring(lYa, format.mintick) + '\n' + _L.lbl_ext + ': ' + extTipSign + string.tostring(extPctTip, '#') + '%'

            _mkUp = label.new(ax, uYa, '◆', style=label.style_label_center, color=color.new(chart.bg_color, 100), textcolor=color.new('#5B9BD5'), size=math.max(i_dashSz - 4, 6), tooltip=tip)
            _mkLo = label.new(ax, lYa, '◆', style=label.style_label_center, color=color.new(chart.bg_color, 100), textcolor=color.new('#5B9BD5'), size=math.max(i_dashSz - 4, 6), tooltip=tip)

            dTxt: str = f_dStr(_dir, _L)
            aTxt: str = ('+' if _ang >= 0 else '') + string.tostring(_ang, '#.#') + '°'

            if i_showAngLbl:
                _lblX: int = cast_int((sLx + eX) / 2)
                _lblY: float = math.sqrt(uY1 * uYe) if uY1 > 0 and uYe > 0 else (uY1 + uYe) / 2.0

                if i_showAng and array.size(_bGm) > _seg and (_seg >= 1):
                    _lblX = bar_index - _anchor + i_pjOff
                    _lblY = f_icsLine(array.get(_bGm, _seg), array.get(_bCx, _seg), array.get(_bGm, 0), array.get(_bCx, 0), _lblX, _trSig)
                _lbl = label.new(_lblX, _lblY, dTxt + ' ' + aTxt, style=label.style_label_down, textcolor=i_angClr if i_showAng else chClr, color=color.new(chart.bg_color, 60), size=math.max(i_dashSz - 2, 6), tooltip=_L.lbl_trend_tip + ': ' + dTxt + '\n' + _L.lbl_angle + ': ' + aTxt + '\n' + _L.lbl_blocks + ': ' + string.tostring(_seg + 1))

        if i_showAng and _ok and (_seg >= 1) and (array.size(_bGm) > _seg):
            _aGmOld: float = array.get(_bGm, _seg)
            _aGmNew: float = array.get(_bGm, 0)
            _aCxOld: int = array.get(_bCx, _seg)
            _aCxNew: int = array.get(_bCx, 0)
            _angLn = line.new(_aCxOld, _aGmOld, _aCxNew, _aGmNew, color=i_angClr, width=2, style=line.style_solid)
            _aPjX: int = bar_index - _anchor + i_pjOff
            _aPjY: float = f_icsLine(_aGmOld, _aCxOld, _aGmNew, _aCxNew, _aPjX, _trSig)
            _angPj = line.new(_aCxNew, _aGmNew, _aPjX, _aPjY, color=i_angClr, width=2, style=line.style_dotted)

        if not na(_dash):
            table.delete(_dash)
            _dash = na

        if i_showDash:
            sz: int = math.max(i_dashSz, 6)
            szSm: int = math.max(sz - 2, 6)
            szXs: int = math.max(sz - 4, 6)

            bg: Color = color.new(chart.bg_color, 20)
            bgHd: Color = color.new(chart.bg_color, 10)
            bdr: Color = color.new(chart.fg_color, 85)
            fg: Color = chart.fg_color
            fg2: Color = color.new(chart.fg_color, 40)

            tfS: str = 's' if timeframe.isseconds else 'm' if timeframe.isminutes else ''

            __block_result_2__ = na
            __switch_2__ = i_dashPos
            if __switch_2__ == "Top Left":
                __block_result_2__ = position.top_left
            elif __switch_2__ == "Top Center":
                __block_result_2__ = position.top_center
            elif __switch_2__ == "Middle Left":
                __block_result_2__ = position.middle_left
            elif __switch_2__ == "Middle Center":
                __block_result_2__ = position.middle_center
            elif __switch_2__ == "Middle Right":
                __block_result_2__ = position.middle_right
            elif __switch_2__ == "Bottom Left":
                __block_result_2__ = position.bottom_left
            elif __switch_2__ == "Bottom Center":
                __block_result_2__ = position.bottom_center
            elif __switch_2__ == "Bottom Right":
                __block_result_2__ = position.bottom_right
            else:
                __block_result_2__ = position.top_right
            _dPos: str = __block_result_2__
            _dash = table.new(_dPos, 7, 5, bgcolor=bg, border_color=bdr, border_width=1, frame_color=bdr, frame_width=1)

            table.cell(_dash, 0, 0, 'ST-EP06 · #' + syminfo.ticker + ' · ' + timeframe.period + tfS + '     ' + string.tostring(close, format.mintick) + ' ' + syminfo.currency, text_color=fg, text_size=szSm, bgcolor=bgHd, text_halign=text.align_left, tooltip=_L.tip_header)
            for c in pine_range(1, 6):
                table.cell(_dash, c, 0, '', bgcolor=bgHd)
            table.merge_cells(_dash, 0, 0, 6, 0)

            table.cell(_dash, 0, 1, _L.lbl_period, text_color=fg2, text_size=szXs, bgcolor=bg, text_halign=text.align_left, tooltip=_L.tip_period)
            for c in pine_range(0, 5):
                table.cell(_dash, c + 1, 1, string.tostring(array.get(SCALES, c)), text_color=color.new('#5B9BD5'), text_size=szXs, bgcolor=bg, text_halign=text.align_center)

            table.cell(_dash, 0, 2, _L.lbl_trend, text_color=fg2, text_size=szXs, bgcolor=bg, text_halign=text.align_left, tooltip=_L.tip_trend)
            for c in pine_range(0, 5):
                tr: TrendResult = array.get(_trends, c)
                table.cell(_dash, c + 1, 2, f_dStr(tr.dir, _L), text_color=f_dClr(tr.dir), text_size=szXs, bgcolor=bg, text_halign=text.align_center)

            chUpStr: str = string.tostring(_chUp, format.mintick) if not na(_chUp) else '—'
            chLoStr: str = string.tostring(_chLo, format.mintick) if not na(_chLo) else '—'
            agCnt: int = _cUp if _cUp > _cDn else _cDn if _cDn > _cUp else _cFlat
            agDir: str = _L.dir_up if _cUp > _cDn else _L.dir_dn if _cDn > _cUp else _L.dir_rng
            table.cell(_dash, 0, 3, _L.lbl_agreement + ': ' + string.tostring(agCnt) + '/6 ' + agDir + '  ▲ ' + chUpStr + '  ▼ ' + chLoStr, text_color=fg2, text_size=szXs, bgcolor=bg, text_halign=text.align_left, tooltip=_L.tip_agreement)
            for c in pine_range(1, 6):
                table.cell(_dash, c, 3, '', bgcolor=bg)
            table.merge_cells(_dash, 0, 3, 6, 3)

            stLine1: str = ""
            stLine2: str = ""
            stClr: Color = color.new(color.new('#888888'), 0)

            _flPct: float = math.round(math.max(0.0, math.min(_extPos, 1.0)) * 100)
            _clPct: float = 100.0 - _flPct
            _abPct: float = math.round((_extPos - 1.0) * 100)
            _blPct: float = math.round(math.abs(math.min(_extPos, 0.0)) * 100)

            __switch_2__ = _boState
            if __switch_2__ == ST_BO_UP:
                stClr = i_clrUp
                stLine1 = _L.st_bo_up + (' ✓' if _boConfirm else '') + (' ' + _L.conn_gap if _boGapped else '') + ' ' + _L.conn_at + ' ' + string.tostring(nz(_boPrice), format.mintick)
                if _boConfirm and (not na(_rtPrice)):
                    stLine1 = stLine1 + ' ' + _L.conn_retested + ' ' + string.tostring(nz(_rtPrice), format.mintick)
                stLine2 = string.tostring(_abPct, '#') + _L.dist_above_ceiling
            elif __switch_2__ == ST_RT_UP:
                stClr = color.new(color.new('#EF9F27'), 0)
                stLine1 = _L.st_rt_up_broke_at + ' ' + string.tostring(nz(_boPrice), format.mintick)
                stLine2 = _L.conn_now + ' ' + string.tostring(nz(close[_anchor]), format.mintick) + ' · ' + string.tostring(_abPct, '#') + _L.dist_above_ceiling
            elif __switch_2__ == ST_BO_DN:
                stClr = i_clrDn
                stLine1 = _L.st_bo_dn + (' ✓' if _boConfirm else '') + (' ' + _L.conn_gap if _boGapped else '') + ' ' + _L.conn_at + ' ' + string.tostring(nz(_boPrice), format.mintick)
                if _boConfirm and (not na(_rtPrice)):
                    stLine1 = stLine1 + ' ' + _L.conn_retested + ' ' + string.tostring(nz(_rtPrice), format.mintick)
                stLine2 = string.tostring(_blPct, '#') + _L.dist_below_floor
            elif __switch_2__ == ST_RT_DN:
                stClr = color.new(color.new('#EF9F27'), 0)
                stLine1 = _L.st_rt_dn_broke_at + ' ' + string.tostring(nz(_boPrice), format.mintick)
                stLine2 = _L.conn_now + ' ' + string.tostring(nz(close[_anchor]), format.mintick) + ' · ' + string.tostring(_blPct, '#') + _L.dist_below_floor
            else:
                stClr = color.new(color.new('#5B9BD5'), 0) if _retFrom != 0 or _dirReset else color.new(color.new('#888888'), 0)
                stLine1 = _L.st_inside_dir_ch if _dirReset else _L.st_inside_fail_up if _retFrom == 1 else _L.st_inside_fail_dn if _retFrom == -1 else _L.st_inside
                stLine2 = string.tostring(_flPct, '#') + _L.dist_from_floor + ' · ' + string.tostring(_clPct, '#') + _L.dist_to_ceiling

            table.cell(_dash, 0, 4, stLine1 + ' · ' + stLine2, text_color=stClr, text_size=szXs, bgcolor=bg, text_halign=text.align_left, tooltip=_L.tip_narrative)
            for c in pine_range(1, 6):
                table.cell(_dash, c, 4, '', bgcolor=bg)
            table.merge_cells(_dash, 0, 4, 6, 4)

    _alertsActive: bool = i_enableAlerts and _anchor == 0

    plot(_ang, 'Angle', display=display.none)
    plot(_cUp - _cDn, 'Agreement', display=display.none)
    plot(_extPos * 100, 'ChannelPos', display=display.none)

    _alertWarn: Persistent[Label] = na(Label)

    if barstate.islast:
        label.delete(_alertWarn)
        _alertWarn = na
        if i_enableAlerts and _anchor != 0:
            _alertWarn = label.new(bar_index, high, '⚠  ' + _L.alert_warn, style=label.style_label_down, color=color.new(color.new('#EF9F27'), 0), textcolor=color.white, size=math.max(i_dashSz, 6), yloc=yloc.abovebar, tooltip=_L.alert_warn_tip)

    alertcondition(_alertsActive and _dir == DIR_UP and (_dir[1] != DIR_UP), '▲ Uptrend Entry', '📈 UPTREND — trend turned UP')
    alertcondition(_alertsActive and _dir == DIR_DOWN and (_dir[1] != DIR_DOWN), '▼ Downtrend Entry', '📉 DOWNTREND — trend turned DOWN')
    alertcondition(_alertsActive and _dir == DIR_FLAT and (_dir[1] != DIR_FLAT), '◈ Range Entry', '◈ RANGE — trend went FLAT')

    alertcondition(_alertsActive and _boState == ST_BO_UP and (_boState[1] != ST_BO_UP), '▲ Breakout Up', '🟢 BO UP — price broke above ceiling')
    alertcondition(_alertsActive and _boConfirm and (not _boConfirm[1]) and (_boState == ST_BO_UP), '✓ BO Up Confirmed', '✅ BO UP CONFIRMED — retested and bounced')
    alertcondition(_alertsActive and _boState == ST_BO_DN and (_boState[1] != ST_BO_DN), '▼ Breakout Down', '🔴 BO DN — price broke below floor')
    alertcondition(_alertsActive and _boConfirm and (not _boConfirm[1]) and (_boState == ST_BO_DN), '✓ BO Down Confirmed', '✅ BO DN CONFIRMED — retested and bounced')

    alertcondition(_alertsActive and _boState == ST_RT_UP and (_boState[1] != ST_RT_UP), '↺ Retest Up', '↺ RETEST UP — price returning to ceiling')
    alertcondition(_alertsActive and _boState == ST_RT_DN and (_boState[1] != ST_RT_DN), '↺ Retest Down', '↺ RETEST DN — price returning to floor')

    alertcondition(_alertsActive and _boGapped and (not _boGapped[1]) and (_boState == ST_BO_UP), '⚡ Gap Up Through', '⚡ GAP UP — price crossed entire channel upward')
    alertcondition(_alertsActive and _boGapped and (not _boGapped[1]) and (_boState == ST_BO_DN), '⚡ Gap Down Through', '⚡ GAP DN — price crossed entire channel downward')
    alertcondition(_alertsActive and _retFrom == 1 and (_retFrom[1] != 1), '✗ Failed Breakout Up', '✗ FAILED BO UP — returned inside channel')
    alertcondition(_alertsActive and _retFrom == -1 and (_retFrom[1] != -1), '✗ Failed Breakout Down', '✗ FAILED BO DN — returned inside channel')
    alertcondition(_alertsActive and _dirReset, '↻ Direction Reset', '↻ DIR RESET — trend direction changed, state wiped')

    alertcondition(_alertsActive and _cUp == 6 and (_cUp[1] != 6), '🔵 Full Bull 6/6', '🔵 FULL BULL — all 6 scales agree UP')
    alertcondition(_alertsActive and _cUp == 5 and (_cUp[1] != 5), '🔵 Strong Bull 5/6', '🔵 STRONG BULL — 5 of 6 scales agree UP')
    alertcondition(_alertsActive and _cDn == 6 and (_cDn[1] != 6), '🔴 Full Bear 6/6', '🔴 FULL BEAR — all 6 scales agree DN')
    alertcondition(_alertsActive and _cDn == 5 and (_cDn[1] != 5), '🔴 Strong Bear 5/6', '🔴 STRONG BEAR — 5 of 6 scales agree DN')
    alertcondition(_alertsActive and _cFlat >= 4 and (_cFlat[1] < 4), '◈ Range Consensus ≥4/6', '◈ RANGE CONSENSUS — ≥4 of 6 scales in RNG')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
