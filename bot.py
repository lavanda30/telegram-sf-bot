import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# ДАНІ ПРАЙСУ
# ============================================================
BRANDS = {
    "GRANDDESIGN": {
        "note": "Прайс від 23.09.2024 · Знижка 10% від 20м",
        "emoji": "🏭",
        "columns": ["Артикул", "Висота", "Склад", "Ціна відріз", "Примітки"],
        "price_idx": [3],
        "items": [
            ["B241253",300,"100% PES","11$",""],["B241118",300,"100% PES","12,75$",""],
            ["B120890",300,"100% PES","8,9$",""],["BLCK 0644",300,"100% PES","14$",""],
            ["BLCK 0634",300,"100% PES","—","РОЗПРОДАЖ"],["DT 3446",300,"100% PES","15,5$","Зниження ціни"],
            ["FAB 0658",320,"96% PES/4% LINEN","12$",""],["FAB 0576",315,"100% PES","6,5$",""],
            ["JM 1112",300,"100% PES","7$",""],["JM 1114",320,"87% PES/12% Acry","9$",""],
            ["KDR 496S",320,"100% PES","9$","РОЗПРОДАЖ"],["L 205",300,"100% PES","6$","РОЗПРОДАЖ"],
            ["L 208",300,"100% PES","10,5$",""],["L 131",310,"100% PES","9$",""],
            ["MUZ 0562",300,"100% PES","11$",""],["TDB 4898",320,"100% PES","8,5$",""],
            ["TDB S004",300,"100% PES","6$",""],["TDB S02S",300,"100% PES","13$",""],
            ["TDB S030",300,"100% PES","5$",""],["TDB S031",300,"100% PES","6,35$","РОЗПРОДАЖ"],
            ["TDB S095",300,"100% PES","2$","РОЗПРОДАЖ"],["33165",305,"100% PES","7,5$",""],
            ["33166",305,"100% PES","9$",""],["33167",305,"100% PES","9$",""],
            ["0443",305,"100% PES","9$","РОЗПРОДАЖ"],["6036",300,"100% PES","12$",""],
            ["3904",305,"80% PES/20% LINEN","9$",""],["ELIZ",295,"80% PES/20% LINEN","10$",""],
            ["HARMONY",310,"100% PES","10,5$",""],["RIGA",320,"80% PES/20% LINEN","18$",""],
            ["MANUBA",310,"66% ACR/26% COT/8% LIN","24$",""],["NABIL",310,"66% ACR/26% COT/8% LIN","24$",""],
            ["SILYANA",300,"64% VIS/36% ACR","25$",""],["MIRAY",320,"100% PES","14,5$","Зниження ціни"],
            ["NESTA (АНТИКІГОТЬ)",300,"100% PES","8$","Зниження ціни"],
            ["EA 2400",340,"100% PES","9,5$",""],["A 1096",350,"100% PES","6,5$",""],
            ["AA 1106",350,"100% PES","9,5$",""],["5400 (BLACKOUT)",320,"100% PES","14,5$",""],
            ["ESRA",310,"100% PES","8,5$","РОЗПРОДАЖ"],["FEBRERO",320,"100% PES","7,5$",""],
            ["SEREN",300,"100% PES","9$","Зниження ціни"],["CHANEL BLACKOUT",295,"100% PES","20$","Зниження ціни"],
            ["ZAHA",310,"100% PES","18,5$","Зниження ціни"],["NEOLA",310,"100% PES","18,5$","Зниження ціни"],
            ["HATAY",305,"100% PES","18$","Зниження ціни"],["AYLIN (двохстор.)",320,"100% PES","15,5$","НОВИНКА"],
            ["VAZO",300,"100% PES","15,5$","НОВИНКА"],["ALBA",300,"100% PES","7,2$","НОВИНКА"],
            ["LUTON",300,"100% PES","7$","НОВИНКА"],["WOODY",300,"100% PES","13,5$","НОВИНКА"],
            ["AZZARO (двохстор.)",300,"51% PES/41% VIS","28$","Під замовлення"],
            ["AZUR",300,"51% PES/41% VIS","28$","Під замовлення"],
        ]
    },
    "SAVAHOME": {
        "note": "Штори та тюль · ОПТ USD",
        "emoji": "🏠",
        "columns": ["Назва","Статус","Категорія","Тип","Склад","Висота","Відріз","Роздріб"],
        "price_idx": [6, 7],
        "items": [
            ["FA-7309","В наявності","Штори","Мікровелюр","100% PES",300,"6,5$","10,4$"],
            ["BARKHAT","В наявності","Штори","Оксамит","100% PES",300,"9,5$","16$"],
            ["Yaldiz","В наявності","Штори","Шиніл-рогожка","100% PES",300,"19$","32$"],
            ["Sultan","В наявності","Штори","Льон-мікровелюр","100% PES",300,"11$","18,7$"],
            ["Rafayella (atlas)","В наявності","Штори","Катоній шиніл","100% PES",300,"13$","22,1$"],
            ["Design 375468","В наявності","Штори","—","100% PES",300,"14,5$","25$"],
            ["Kasmir","В наявності","Штори","Шеніл-льон двосторон.","100% PES",310,"17$","29$"],
            ["California","РОЗПРОДАЖ","Штори","Мікровелюр-льон","100% PES",300,"9,8$","17$"],
            ["Sandy velvet","В наявності","Штори","Нубук","100% PES",300,"10$","16$"],
            ["Blackout 20846","РОЗПРОДАЖ","Штори","Сатін дімаут","100% PES",310,"9,5$","16$"],
            ["BALAT","В наявності","Штори","Льон + дімаут","20% LIN/80% POL",280,"13,5$","23$"],
            ["Keten Blackout","РОЗПРОДАЖ","Штори","Блекаут","100% PES",300,"8,5$","15,3$"],
            ["FJ-S825","В наявності","Штори","Льон мармор ялинка","100% PES",300,"11$","24$"],
            ["FLAT Blackout","РОЗПРОДАЖ","Штори","Матовий блекаут","100% PES",295,"16$","40$"],
            ["DSN-BLCK0813","РОЗПРОДАЖ","Штори","Шиніл блекаут","100% PES",300,"14,8$","22,6$"],
            ["CUPRA Blackout","РОЗПРОДАЖ","Штори","Двосторон. блекаут","PES",310,"19$","35$"],
            ["Soni FA7360","В наявності","Штори","100% блекаут","100% PES",320,"17$","29$"],
            ["Ultra Blackout","В наявності","Штори","Матовий блекаут","100% PES",320,"4$","7$"],
            ["Crep","В наявності","Тюль","Креп-тюль","100% PES",320,"4$","6,5$"],
            ["Bambu","В наявності","Тюль","Бамбук 17 ниток","100% PES",320,"2,7$","5$"],
            ["Grek","В наявності","Тюль","Грек-сітка","100% PES",310,"5,5$","10$"],
            ["Foldet (льон)","В наявності","Тюль","Ефект льону","100% PES",320,"5,6$","12$"],
            ["Silk crep fa7351","В наявності","Тюль","Крепт-тюк","100% PES",320,"4,6$","9$"],
            ["Sofi","В наявності","Тюль","Ялинка бамбук","100% PES",310,"3,3$","8$"],
            ["King bambu","В наявності","Тюль","Бамбук 24 нитки","100% PES",300,"4,5$","10$"],
            ["Liman 2","В наявності","Тюль","Підпорваний льон","100% PES",330,"3,5$","7$"],
            ["Tergal (шифон)","В наявності","Тюль","Шифон-вуаль","100% PES",300,"5,8$","11$"],
            ["Liman-crep","В наявності","Тюль","Креп-льон","100% PES",320,"7,8$","13$"],
            ["BONA","В наявності","Тюль","Антивандальний","100% PES",330,"6,5$","12$"],
            ["Mabel 7308","В наявності","Тюль","Стіка-вуаль","100% PES",300,"7$","16$"],
            ["ZETA","В наявності","Тюль","Льон з ялинкою","90% PES/10% LIN",310,"9$","8$"],
            ["ARO3104","В наявності","Тюль","Льон-батист","80% PES/20% LIN",310,"4,5$","10$"],
            ["AT02851 foldet","В наявності","Тюль","Стіка-вуаль","100% PES",300,"5,5$","9$"],
            ["ARO3018","В наявності","Тюль","Матовий шовк","100% PES",320,"5$","13$"],
            ["LEXSI crep","В наявності","Тюль","Крепт-шовк","100% PES",320,"5,5$","7$"],
            ["CHIOS crep","В наявності","Тюль","Стіка верт. полоса","100% PES",300,"2,7$","4$"],
            ["Briz","РОЗПРОДАЖ","Тюль","ПД льон сніжок","100% PES",300,"4$","7$"],
            ["Snow","РОЗПРОДАЖ","Тюль","—","100% PES",300,"4$","7$"],
        ]
    },
    "ELIZABETH Тюль": {
        "note": "Тюль BOOK · грн/м · рулон / відріз",
        "emoji": "🪟",
        "columns": ["Артикул","Рулон (грн)","Відріз (грн)"],
        "price_idx": [1, 2],
        "items": [
            ["FA1106/99","6,50","8,50"],["AA1053/05","6,00","7,80"],["FA3005/99","5,80","7,20"],
            ["FA3013/05","5,80","7,50"],["FA3017/01","5,20","7,00"],["FA3009/05","5,20","6,80"],
            ["FA3007/05","5,00","6,50"],["FA3006/05","5,20","6,80"],["FA3000/01","4,50","5,80"],
            ["FA3019/01","5,00","6,50"],["FA3020/01","5,40","7,00"],["FA3014/89","6,20","7,90"],
            ["AA0311/29","5,40","7,00"],["FA3011/29","4,60","6,00"],["FA1451/S7","7,00","9,00"],
            ["FA7077/S7","7,20","9,40"],["AA1949/S7","7,00","9,00"],["AA2377/S4","5,40","7,00"],
            ["FA3001/01","5,00","6,50"],["FA3002/01","5,20","6,60"],["FA7079 (h300–320)","4,00","5,20"],
            ["FA7079 (h340)","4,20","5,50"],["FA7045/05","5,00","6,50"],["FA7044/05","4,20","5,50"],
            ["FA7049/05","4,20","5,50"],["FA7076/05*","4,20","5,00"],["FA7075/05*","4,20","5,00"],
            ["FA2245/05*","3,90","5,00"],["FA1662/D3","4,10","5,30"],["FA2128/D3","3,80","5,00"],
            ["FA3010/01","4,40","5,80"],["FA3015/01","4,60","6,00"],["FA3016/01","4,60","6,00"],
            ["FA3003/01","4,20","5,50"],["FA0300/02*","4,00","5,20"],["FA3008/01 (h300–320)","4,60","6,00"],
            ["FA3008/01 (h340)","4,80","6,30"],["FA3012/01","4,60","6,00"],["FA3004/01","4,20","5,50"],
            ["FA1015/01/А без тяг.","3,00","4,00"],["FA1015/01/В з тяг.","3,50","4,50"],
            ["JN6259/01","5,00","6,50"],["JN6269/01","5,00","6,50"],["JN6267/01","5,00","6,50"],
            ["JN6270/01","5,00","6,50"],["JN6273/01","5,00","9,50"],["FA5071(DUZ)/69","2,50","3,30"],
            ["FA5071(PILISELI)/69","6,50","8,50"],["FA5071(TASLI)/69","6,10","8,00"],
            ["FA7123/99","6,00","7,80"],["FA7125/05","5,40","7,00"],["FA7129/S7","7,00","9,00"],
            ["FA7169/05","5,20","6,80"],
        ]
    },
    "ELIZABETH Штори": {
        "note": "Портьєри · взірці 2021 · грн/м",
        "emoji": "🎭",
        "columns": ["Артикул","Примітка","Рулон (грн)","Відріз (грн)"],
        "price_idx": [2, 3],
        "items": [
            ["FB7168","—","12,00","14,40"],["FB7201","—","10,70","12,90"],
            ["FB7089","—","8,20","10,60"],["FB7091","—","6,70","8,70"],
            ["FA2247/G7*","—","7,30","9,50"],["FA2432 (ARO1760)* нубук","Нубук","8,30","9,50"],
            ["FA7104","Кипет","8,70","10,40"],["FA2250/G7*","Совпадає","8,00","10,30"],
            ["FA2181/14*","Двусторон.-сорт","7,40","8,50"],["FA7041","13,6 у Liberta Crystall","9,40","11,30"],
            ["FJ5680","—","8,30","10,80"],["FA7074","—","8,60","11,20"],
            ["FJ5689","13,5 у Liberta мурей","12,50","15,00"],["FJ5688","—","12,50","15,00"],
            ["FJ5709","—","11,70","14,00"],["FJ5697","—","8,80","11,40"],
            ["FJ5704","—","8,80","11,40"],["FJ5712","—","9,60","12,50"],
            ["FJ5713","—","9,60","12,50"],["FJ5710","—","11,00","14,40"],
            ["FB7204","—","8,10","10,60"],["FB7206","—","7,70","9,50"],
            ["FB7207","—","8,50","10,50"],["FB7220","—","6,50","8,50"],
            ["FB7144","—","14,60","18,00"],["FB7146","—","15,40","18,50"],
            ["FA7081","—","9,60","12,50"],["FA7084","13,6 Vegas у Liberta","9,60","12,50"],
            ["FJ5725","—","9,10","11,00"],["FB7225","—","8,50","11,00"],
            ["FB7123* (еа24714)","—","4,40","5,60"],
        ]
    },
    "ELIZABETH Оксамит": {
        "note": "Оксамит · Однотон 2022 · Каталоги",
        "emoji": "🎨",
        "columns": ["Артикул","Категорія","Рулон (грн)","Відріз (грн)","Примітки"],
        "price_idx": [2, 3],
        "items": [
            ["VELVET FD2153 (300)","Оксамит","—","—",""],
            ["FYJ3 (FD2154)","Оксамит","10,00","13,00",""],
            ["369-9 (FD2155)","Оксамит","12,00","15,00",""],
            ["ZFLY-A рубчик","Оксамит","12,00","15,00",""],
            ["ZFYJ мрамор","Оксамит","10,00","13,00",""],
            ["Kafkas FA7182","Однотон 2022","9,00","12,00",""],
            ["California FA7163","Однотон 2022","9,00","12,00",""],
            ["Wool FA7151","Однотон 2022","10,00","13,50",""],
            ["Wool рубчик FA7156","Однотон 2022","10,00","13,50",""],
            ["FA2432 (ARO1760)*","Каталог однотон","8,70","10,40",""],
            ["FA2452 (ARO1771)","Каталог однотон","5,00","6,50","Знято"],
            ["FA2321/G7","Каталог однотон","5,00","6,50","Знято"],
            ["FA2181/14*","Каталог однотон","7,40","8,50",""],
            ["FA2251/G7*","Каталог однотон","9,00","10,50",""],
            ["FA2247/G7*","Каталог однотон","8,30","9,50",""],
            ["FA2248/G7","Каталог однотон","4,50","6,00","Знято"],
            ["FA2249/G7*","Каталог однотон","8,00","9,50",""],
            ["FA2250/G7*","Каталог однотон","8,30","10,00",""],
        ]
    },
    "ЛАСП": {
        "note": "Ширина 140см · грн/м · прайс 01.08.2024",
        "emoji": "🧵",
        "columns": ["Найменування","Опис","Рулон (грн)","Відріз (грн)","Примітки"],
        "price_idx": [2, 3],
        "items": [
            ["1414 (Arenas/Casablanka...)","велюр","16,80","17,80","Велюр з тисненням"],
            ["ADA / АДА","велюр","5,50","7,50","велюр «соти»"],
            ["AFRODIT","сатен","6,00","6,00","класичний вензель"],
            ["ALA","принт","6,00","6,00","ПРИНТ квіти"],
            ["ALBATROS","велюр","8,00","9,50","Велюр матовий"],
            ["ALINA / АЛІНА","шеніл","11,90","13,90","*** ізіклін ***"],
            ["ALMOND","жаккард","6,00","6,00","квітковий вензель"],
            ["AMORE / АМОРЕ","велюр","8,60","9,90","Велюр матовий"],
            ["AMOUR / АМУР","рогожа","6,50","7,50","букля"],
            ["ANTARA","шт.замша","10,90","11,80","водовідштовхувальна"],
            ["ARENAS, 1414","велюр","16,80","17,80","тиснений велюр"],
            ["ARMAS","шенилл","10,50","11,50",""],
            ["ASRIN A","печворк/рог","8,00","9,00","рогожа в стилі печворк"],
            ["ASRIN C","рогожа","8,00","9,00","рогожа"],
            ["BARRAKAN","шеніл","11,90","12,90","кольорова абстракція"],
            ["BASIC SATEN","сатен","10,90","11,90","гладкий шовк без малюнку"],
            ["BLOCCO / БЛОККО","шеніл","10,20","11,90","тертий шеніл"],
            ["BORJA / БОРДЖА","шеніл","17,80","18,80","малюнок «Версачі»"],
            ["BUFFALO / БАФФАЛО","шт.замша","9,00","9,90","імітація шкіри бізона"],
            ["CAGDAS / КАГДАС","велюр","4,00","5,00","тканий велюр"],
            ["CABARE 4174-1 V-1","велюр","23,00","23,00","подвійний принт"],
            ["CALIFORNIA","оксамит","10,50","11,50",""],
            ["CALIFORNIA BLOCKS","оксамит","12,90","13,90","Термостьобка"],
            ["CALISTA","вулична","9,90","10,90","ДЛЯ ВУЛИЧНИХ МЕБЛІВ"],
            ["CAREL","сатен","5,00","5,80","для дитячих меблів"],
            ["CASABLANKA, 1414","велюр","16,80","17,80","Велюр з тисненням"],
            ["CHOPIN","сатен","11,00","11,90","в т.ч. HORECA"],
            ["CITA","шеніл","6,80","6,80","малюнок «тигр»"],
            ["DARA","букля","9,50","10,50","букля однотонна"],
            ["DENIM / ДЕНІМ","жаккард","6,50","7,50","джинсовий малюнок"],
            ["DENIM (комп LESI, LINDA)","рогожа","9,50","10,90",""],
            ["DIAMOND / ДІАМОНД","велюр","5,50","7,50",""],
            ["DORA","букля","13,00","14,00","букля з геометрич. малюнком"],
            ["DUBAI","букля","9,90","10,90",""],
            ["ELENA","шеніл","20,90","22,90","вензель+компаньйони"],
            ["EMILYA","жаккард","11,80","12,90","класичний вензель"],
            ["EMILYA DUZ","жаккард","10,80","11,90","однотон"],
            ["ENDOS / ЕНДОС","рогожа","5,50","6,50","етно"],
            ["FETTAN / ФЕТТАХ","рогожа","6,50","7,50","букля"],
        ]
    }
}

PAGE_SIZE = 10

# ============================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================

def format_item(brand_name, item):
    brand = BRANDS[brand_name]
    cols = brand["columns"]
    price_idx = brand["price_idx"]
    lines = []

    name = str(item[0])
    lines.append(f"📌 *{name}*")

    for i, col in enumerate(cols):
        if i == 0:
            continue
        val = str(item[i]) if i < len(item) else "—"
        if not val or val == "—" or val == "":
            continue
        if i in price_idx:
            lines.append(f"💰 {col}: *{val}*")
        else:
            lines.append(f"   {col}: {val}")

    return "\n".join(lines)


def get_tag(item, brand_name):
    brand = BRANDS[brand_name]
    # Check last column for tags like РОЗПРОДАЖ, НОВИНКА etc.
    for val in item[1:]:
        v = str(val).upper()
        if "РОЗПРОДАЖ" in v:
            return "🔴"
        if "НОВИНКА" in v:
            return "🟢"
        if "ЗНИЖЕННЯ" in v:
            return "🟡"
        if "ПІД ЗАМОВЛЕННЯ" in v or "ЗАМОВЛЕННЯ" in v:
            return "📦"
    status_idx = None
    cols = brand["columns"]
    for i, c in enumerate(cols):
        if c in ["Статус"]:
            status_idx = i
            break
    if status_idx and status_idx < len(item):
        v = str(item[status_idx]).upper()
        if "РОЗПРОДАЖ" in v:
            return "🔴"
    return ""


def build_brand_list_text(brand_name, items, page):
    brand = BRANDS[brand_name]
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(items))
    total = len(items)

    text = f"{brand['emoji']} *{brand_name}*\n"
    text += f"_{brand['note']}_\n"
    text += f"Показано {start+1}–{end} з {total}\n\n"

    for item in items[start:end]:
        tag = get_tag(item, brand_name)
        name = str(item[0])
        price_idx = brand["price_idx"]
        prices = []
        for pi in price_idx:
            if pi < len(item):
                p = str(item[pi])
                if p and p != "—":
                    prices.append(p)
        price_str = " / ".join(prices) if prices else "—"
        text += f"{tag} `{name}` — *{price_str}*\n"

    return text


def build_brand_keyboard(brand_name, items, page):
    total_pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
    btns = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page:{brand_name}:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Далі ▶️", callback_data=f"page:{brand_name}:{page+1}"))
    if nav:
        btns.append(nav)
    btns.append([InlineKeyboardButton("🔍 Пошук", callback_data="search"),
                 InlineKeyboardButton("🏠 Головна", callback_data="main")])
    return InlineKeyboardMarkup(btns)


def build_main_keyboard():
    rows = []
    brand_list = list(BRANDS.keys())
    for i in range(0, len(brand_list), 2):
        row = []
        for brand in brand_list[i:i+2]:
            b = BRANDS[brand]
            row.append(InlineKeyboardButton(
                f"{b['emoji']} {brand}",
                callback_data=f"brand:{brand}:0"
            ))
        rows.append(row)
    rows.append([InlineKeyboardButton("🔍 Пошук по всіх брендах", callback_data="search")])
    return InlineKeyboardMarkup(rows)


# ============================================================
# HANDLERS
# ============================================================

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    total = sum(len(b["items"]) for b in BRANDS.values())
    text = (
        "🛍 *Прайс Штори та Тюль*\n\n"
        f"В базі: *{total} позицій* · {len(BRANDS)} брендів\n\n"
        "Оберіть бренд або скористайтесь пошуком:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=build_main_keyboard())


async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main":
        total = sum(len(b["items"]) for b in BRANDS.values())
        text = (
            "🛍 *Прайс Штори та Тюль*\n\n"
            f"В базі: *{total} позицій* · {len(BRANDS)} брендів\n\n"
            "Оберіть бренд або скористайтесь пошуком:"
        )
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=build_main_keyboard())

    elif data.startswith("brand:") or data.startswith("page:"):
        parts = data.split(":")
        brand_name = parts[1]
        page = int(parts[2])
        brand = BRANDS.get(brand_name)
        if not brand:
            await q.edit_message_text("Бренд не знайдено")
            return
        items = brand["items"]
        text = build_brand_list_text(brand_name, items, page)
        kb = build_brand_keyboard(brand_name, items, page)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "search":
        ctx.user_data["waiting_search"] = True
        await q.edit_message_text(
            "🔍 *Введіть назву або артикул* для пошуку по всіх брендах:\n\n"
            "Наприклад: `HARMONY`, `FA3005`, `блекаут`, `оксамит`",
            parse_mode="Markdown"
        )


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Always search when text is received
    query = text.lower()
    results = []

    for brand_name, brand in BRANDS.items():
        for item in brand["items"]:
            if any(query in str(v).lower() for v in item):
                results.append((brand_name, item))

    ctx.user_data["waiting_search"] = False

    if not results:
        await update.message.reply_text(
            f"❌ По запиту *{text}* нічого не знайдено\n\nСпробуйте інший запит:",
            parse_mode="Markdown",
            reply_markup=build_main_keyboard()
        )
        return

    # Build result message
    msg = f"🔍 Знайдено *{len(results)}* результатів по «{text}»:\n\n"
    shown = results[:15]

    for brand_name, item in shown:
        brand = BRANDS[brand_name]
        tag = get_tag(item, brand_name)
        name = str(item[0])
        price_idx = brand["price_idx"]
        prices = [str(item[pi]) for pi in price_idx if pi < len(item) and str(item[pi]) not in ("—","")]
        price_str = " / ".join(prices) if prices else "—"
        msg += f"{tag} [{brand_name}] `{name}` — *{price_str}*\n"

    if len(results) > 15:
        msg += f"\n_...і ще {len(results)-15} результатів. Уточніть запит._"

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔍 Новий пошук", callback_data="search"),
        InlineKeyboardButton("🏠 Головна", callback_data="main")
    ]])
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)


async def search_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.args:
        # search immediately
        update.message.text = " ".join(ctx.args)
        await on_text(update, ctx)
    else:
        ctx.user_data["waiting_search"] = True
        await update.message.reply_text(
            "🔍 Введіть назву або артикул для пошуку:",
            parse_mode="Markdown"
        )


# ============================================================
# MAIN
# ============================================================

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable not set!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    logger.info("Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
