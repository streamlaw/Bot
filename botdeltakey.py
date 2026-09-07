import logging
import math
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# ---------------------------------------------------------
# 1. التوكنات والإعدادات
# ---------------------------------------------------------
BOT_TOKEN = "8911592812:AAGEPGiebusrnctS49zgI1Lq1WThEYuRczs"
BITLY_TOKEN = "80e33929ce3ed152548cca41c903c76ebd94d2e9"

completed_orders = 0  # العداد الحي للطلبات المكتملة

# تعريف مرحلة استقبال الرابط
WAITING_FOR_LINK = 1

# قائمة المواقع المدعومة
SUPPORTED_DOMAINS = [
    "platoboost.com", "gateway.platoboost.com", "platoboost.app", "platoboost.net",
    "linkvertise.com", "linkvertise.net", "link-to.net", "up-to-down.net", "direct-link.net", "file-link.net",
    "loot-link.com", "lootlink.org", "lootlabs.gg", "loot-labs.com", "lootdest.com", "lootdest.org",
    "workink.net", "workink.io", "work.ink", "rbx.ink", "getkey.workink.app",
    "delta.ex", "deltaexec.com", "deltagame.win", "delta-executor.com",
    "fluxus.team", "fluxteam.net", "fluxteam.org", "fluxus.mobi",
    "krnl.place", "krnl.ca", "krnl.vip", "krnl.mobi",
    "hydrogen.sh", "hydrogen.mobi", "hydrogenexec.com",
    "evon.cc", "sakuraexec.com", "trigon.apy", "trigonexec.com",
    "codex.lol", "mortalexec.com", "vegasx.net", "arceusx.com", "spdmteam.com",
    "pastebin.com", "raw.githubusercontent.com", "github.com", "rentry.co", "rentry.org",
    "controlc.com", "hastebin.com", "justpaste.it", "paste.ee", "pasteio.com",
    "scriptblox.com", "rbxscript.com", "robloxscripts.com", "cheater.fun", "rblxscripts.net",
    "v3rmillion.net", "v3rm.net", "rbxscript.hub", "roblox-scripts.com", "bloxscript.com",
    "keyrblx.com", "getkey.net", "key-system.com", "keysystem.org", "verify.key.com",
    "bitly.com", "bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "v.gd", "rebrand.ly", "t.ly", "s.id",
    "shorturl.at", "rb.gy", "rotf.lol", "zpr.io", "short.io", "cleanuri.com", "bc.vc", "shorte.st",
    "sub2get.com", "sub2unlock.com", "sub2unlock.net", "sub4unlock.com", "sub2unlock.io",
    "social-unlock.com", "unlocknow.net", "sub3unlock.com", "getlink.pro", "unlocked.gg",
    "discord.gg", "discord.com", "t.me", "telegram.me", "roblox.com", "roblox.com.ge",
    "mediafire.com", "mega.nz", "mega.co.nz", "drive.google.com", "gofile.io", "pixeldrain.com",
    "workupload.com", "anonfiles.com", "catbox.moe", "uploadhaven.com", "terabox.com", "file.io",
    "gateway.platoboost.app", "boost.platoboost.com", "api.platoboost.com", "cdn.platoboost.com",
    "linkvertise.io", "linkvertise.org", "lootlabs.io", "loot-labs.net", "workink.xyz",
    "delta.mobi", "fluxus.cc", "krnl.net", "hydrogen.gg", "evon.mobi", "arceus.x",
    "paste.ofcode.org", "pastebin.fi", "ghostbin.com", "privatebin.net", "sourcebin.dev",
    "script.google.com", "gist.github.com", "gist.githubusercontent.com", "rawtext.io",
    "sub2get.net", "sub2unlock.com", "sub4unlock.net", "unlock.net", "getscript.me",
    "getkey.me", "key.delta.mobi", "key.fluxus.mobi", "key.krnl.place", "key.evon.cc",
    "key.hydrogen.sh", "key.codex.lol", "key.spdmteam.com", "key.arceusx.com", "key.trigon.apy",
    "roblox.org", "roblox.net", "rbx.gg", "rbx.life", "rbx.club", "rbx.place",
    "script-hub.com", "scripthub.org", "scripthub.net", "rblx-scripts.com", "blox-scripts.com",
    "getscript.net", "getscript.org", "getscript.io", "paste-scripts.com", "rblx-keys.com",
    "key-center.net", "key-hub.org", "keyserver.net", "keygate.io", "keygenerator.net",
    "bypass.city", "bypass.vip", "bypass.me", "bypass.wtf", "freebypass.net",
    "roblox-executors.com", "executors.net", "executor-hub.com", "exploit-db.site", "rbx-exploits.com",
    "delta-key.mobi", "fluxus-key.mobi", "krnl-key.place", "hydrogen-key.sh", "codex-key.lol",
    "sub2get.io", "sub2unlock.io", "social-unlock.io", "unlocknow.io", "getlink.io",
    "sub4unlock.io", "sub3unlock.io", "unlocked.io", "sub2unlock.me", "sub2get.me",
    "link-center.net", "link-hub.net", "link-gate.net", "link-pass.com", "link-portal.net",
    "script-vault.net", "script-center.net", "script-portal.com", "script-gate.org", "script-box.net",
    "key-vault.net", "key-portal.com", "key-pass.org", "key-station.net", "key-box.io", "key-zone.net"
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ITEMS_PER_PAGE = 15

# ---------------------------------------------------------
# 2. نصوص اللغات وأزرار الواجهة
# ---------------------------------------------------------
TEXTS = {
    'ar': {
        'welcome': "👋 **مرحباً بك في بوت اختصار وتتبع الروابط!**\n\nاختر من القائمة أدناه:",
        'btn_shorten': "🔗 اختصار رابط ⚡️",
        'btn_supported': "🌐 المواقع المدعومة ❓",
        'btn_channel': "🎮 قناتنا الرسمية 📢",
        'btn_help': "📖 شرح البوت ⭐️",
        'btn_lang': "🌐 تغيير اللغة",
        'btn_stats': "✅ الطلبات المكتملة: ",
        'btn_back': "🔙 رجوع",
        'send_link': "📥 **أرسل الرابط المطلوب اختصاره الآن في المحادثة.**",
        'help_text': "💡 **طريقة الاستخدام:**\nاضغط على زر اختصار رابط ثم أرسل الرابط ليتم معالجته مباشرة.",
        'stats_text': "📊 **الإحصائيات الحالية:**\nتم معالجة `{}` طلب بنجاح حتى الآن!",
        'invalid_link': "⚠️ يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://",
        'processing': "⚡️ **جاري اختصار الرابط...**",
        'success': "✅ **تم اختصار الرابط بنجاح!**\n\n🔗 **الرابط المختصر:**\n`{}`\n\n📊 إجمالي الطلبات المكتملة: `{}`",
        'error': "❌ حدث خطأ أثناء الاتصال بخدمة الاختصار، حاول مرة أخرى.",
        'select_lang': "🌐 **اختر اللغة المفضلة / Select Language:**"
    },
    'en': {
        'welcome': "👋 **Welcome to Link Shortener & Tracer Bot!**\n\nSelect an option from below:",
        'btn_shorten': "🔗 Shorten Link ⚡️",
        'btn_supported': "🌐 Supported Sites ❓",
        'btn_channel': "🎮 Official Channel 📢",
        'btn_help': "📖 Help & Tutorial ⭐️",
        'btn_lang': "🌐 Change Language",
        'btn_stats': "✅ Completed Orders: ",
        'btn_back': "🔙 Back",
        'send_link': "📥 **Send the link you want to shorten now in the chat.**",
        'help_text': "💡 **How to use:**\nClick 'Shorten Link' button first, then send your link to process it.",
        'stats_text': "📊 **Current Statistics:**\n`{}` orders have been successfully processed so far!",
        'invalid_link': "⚠️ Please send a valid link starting with http://or https://",
        'processing': "⚡️ **Shortening the link...**",
        'success': "✅ **Link Shortened Successfully!**\n\n🔗 **Shortened Link:**\n`{}`\n\n📊 Total Completed Orders: `{}`",
        'error': "❌ An error occurred while connecting to the service. Try again.",
        'select_lang': "🌐 **Select Preferred Language / اختر اللغة المفضلة:**"
    }
}

def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get('lang', 'ar')

def get_main_keyboard(lang: str):
    t = TEXTS[lang]
    keyboard = [
        [InlineKeyboardButton(t['btn_shorten'], callback_data='shorten_info')],
        [InlineKeyboardButton(t['btn_supported'], callback_data='supported_page_0')],
        [InlineKeyboardButton(t['btn_channel'], url='https://t.me/Lrzz0')],
        [InlineKeyboardButton(t['btn_help'], callback_data='help')],
        [InlineKeyboardButton(t['btn_lang'], callback_data='choose_lang')],
        [InlineKeyboardButton(f"{t['btn_stats']}{completed_orders}", callback_data='stats')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(lang: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[lang]['btn_back'], callback_data='back_to_main')]])

def get_lang_keyboard(lang: str):
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data='set_lang_ar'),
            InlineKeyboardButton("🇺🇸 English", callback_data='set_lang_en')
        ],
        [InlineKeyboardButton(TEXTS[lang]['btn_back'], callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(page: int, lang: str):
    total_pages = math.ceil(len(SUPPORTED_DOMAINS) / ITEMS_PER_PAGE)
    buttons = []
    nav_row = []
    
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ السابق", callback_data=f'supported_page_{page - 1}'))
    nav_row.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data='ignore'))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("التالي ➡️", callback_data=f'supported_page_{page + 1}'))
        
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(TEXTS[lang]['btn_back'], callback_data='back_to_main')])
    return InlineKeyboardMarkup(buttons)

# ---------------------------------------------------------
# 3. دالة تتبع التحويلات للوصول للرابط الأخير
# ---------------------------------------------------------
async def get_final_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=15) as response:
                return str(response.url)
    except Exception:
        return url

# ---------------------------------------------------------
# 4. معالجة الأوامر والأزرار
# ---------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(context)
    await update.message.reply_text(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    lang = get_user_lang(context)
    t = TEXTS[lang]

    if data == 'shorten_info':
        await query.edit_message_text(t['send_link'], reply_markup=get_back_keyboard(lang), parse_mode="Markdown")
        return WAITING_FOR_LINK  # تفعيل حالة إنتظار إرسال الرابط
    
    elif data == 'choose_lang':
        await query.edit_message_text(t['select_lang'], reply_markup=get_lang_keyboard(lang), parse_mode="Markdown")
        
    elif data.startswith('set_lang_'):
        new_lang = data.replace('set_lang_', '')
        context.user_data['lang'] = new_lang
        lang = new_lang
        t = TEXTS[lang]
        await query.edit_message_text(t['welcome'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

    elif data.startswith('supported_page_'):
        page = int(data.split('_')[-1])
        start_idx = page * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_items = SUPPORTED_DOMAINS[start_idx:end_idx]
        
        domains_text = "\n".join([f"• `{d}`" for d in page_items])
        total_pages = math.ceil(len(SUPPORTED_DOMAINS) / ITEMS_PER_PAGE)
        
        header = "🌐 **قائمة المواقع المدعومة:**" if lang == 'ar' else "🌐 **Supported Sites List:**"
        page_str = f"📌 الصفحة `{page + 1}` من `{total_pages}`" if lang == 'ar' else f"📌 Page `{page + 1}` of `{total_pages}`"
        
        msg_text = f"{header}\n\n{domains_text}\n\n{page_str}"
        await query.edit_message_text(msg_text, reply_markup=get_pagination_keyboard(page, lang), parse_mode="Markdown")
        
    elif data == 'help':
        await query.edit_message_text(t['help_text'], reply_markup=get_back_keyboard(lang), parse_mode="Markdown")
    elif data == 'stats':
        await query.edit_message_text(t['stats_text'].format(completed_orders), reply_markup=get_back_keyboard(lang), parse_mode="Markdown")
    elif data == 'back_to_main':
        await query.edit_message_text(t['welcome'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")
        return ConversationHandler.END

    return ConversationHandler.END

# ---------------------------------------------------------
# 5. دالة معالجة واختصار الرابط (تعمل فقط بعد الضغط على الزر)
# ---------------------------------------------------------
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global completed_orders
    lang = get_user_lang(context)
    t = TEXTS[lang]
    url = update.message.text.strip()

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(t['invalid_link'])
        return WAITING_FOR_LINK

    status_msg = await update.message.reply_text(t['processing'], parse_mode="Markdown")
    
    final_destination = await get_final_url(url)
    
    bitly_api_url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "Authorization": f"Bearer {BITLY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "long_url": final_destination
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(bitly_api_url, json=payload, headers=headers, timeout=10) as response:
                if response.status in (200, 201):
                    data = await response.json()
                    short_url = data.get("link")
                    
                    completed_orders += 1
                    
                    await status_msg.edit_text(
                        t['success'].format(short_url, completed_orders),
                        parse_mode="Markdown"
                    )
                    return ConversationHandler.END
                else:
                    await status_msg.edit_text(t['error'])

    except Exception:
        await status_msg.edit_text(t['error'])

    return ConversationHandler.END

# ---------------------------------------------------------
# 6. تشغيل البوت
# ---------------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # إعداد ConversationHandler لضمان عدم تنفيذ الاختصار إلا بعد الضغط على الزر
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^shorten_info$')],
        states={
            WAITING_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler)]
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(button_handler)
        ]
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 البوت يعمل الآن بنجاح مع تفعيل نظام الاختصار المباشر بالضغط...")
    app.run_polling()

if __name__ == '__main__':
    main()
