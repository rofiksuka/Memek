import sys
# === MANTRA ANTI-CRASH WINDOWS ===
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import time
import json
import os
import traceback
from urllib.parse import urljoin
from datetime import datetime, timedelta

# --- LIBRARY CHROME SILUMAN (UNDETECTED) ---
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- TELEGRAM LIB ---
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# --- KONFIGURASI ---
YOUR_BOT_TOKEN = "7331162045:AAHxVfQK0HJ-2kK91a2xL9a9YBFbMCGVEmI"
ADMIN_CHAT_IDS = ["8446734557"]
INITIAL_CHAT_IDS = ["8446734557"]

USERNAME = "rofik7244@gmail.com"
PASSWORD = "GanzJB123"

# URL
LOGIN_URL = "https://www.ivasms.com/login"
BASE_URL = "https://www.ivasms.com/"
SMS_API_ENDPOINT = "https://www.ivasms.com/portal/sms/received/getsms"

# Interval 60 detik biar aman dari Cloudflare (jangan dicepetin)
POLLING_INTERVAL_SECONDS = 60
STATE_FILE = "processed_sms_ids.json" 
CHAT_IDS_FILE = "chat_ids.json"

# --- DATA NEGARA & SERVICE (FULL ORIGINAL) ---
COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩", "Angola": "🇦🇴",
    "Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺", "Austria": "🇦🇹", "Azerbaijan": "🇦🇿",
    "Bahrain": "🇧🇭", "Bangladesh": "🇧🇩", "Belarus": "🇧🇾", "Belgium": "🇧🇪", "Benin": "🇧🇯",
    "Bhutan": "🇧🇹", "Bolivia": "🇧🇴", "Brazil": "🇧🇷", "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫",
    "Cambodia": "🇰🇭", "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Chad": "🇹🇩", "Chile": "🇨 ",
    "China": "🇨🇳", "Colombia": "🇨🇴", "Congo": "🇨🇬", "Croatia": "🇭🇷", "Cuba": "🇨🇺",
    "Cyprus": "🇨🇾", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", "Egypt": "🇪🇬", "Estonia": "🇪🇪",
    "Ethiopia": "🇪🇹", "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦", "Gambia": "🇬🇲",
    "Georgia": "🇬🇪", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Greece": "🇬🇷", "Guatemala": "🇬🇹",
    "Guinea": "🇬🇳", "Haiti": "🇭🇹", "Honduras": "🇭🇳", "Hong Kong": "🇭🇰", "Hungary": "🇭🇺",
    "Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩", "Iran": "🇮🇷", "Iraq": "🇮🇶",
    "Ireland": "🇮🇪", "Israel": "🇮🇱", "Italy": "🇮🇹", "IVORY COAST": "🇨🇮", "Ivory Coast": "🇨🇮", "Jamaica": "🇯🇲",
    "Japan": "🇯🇵", "Jordan": "🇯🇴", "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪", "Kuwait": "🇰🇼",
    "Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧", "Liberia": "🇱🇷",
    "Libya": "🇱🇾", "Lithuania": "🇱🇹", "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬", "Malaysia": "🇲🇾",
    "Mali": "🇲🇱", "Malta": "🇲🇹", "Mexico": "🇲🇽", "Moldova": "🇲🇩", "Monaco": "🇲🇨",
    "Mongolia": "🇲🇳", "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿", "Myanmar": "🇲🇲",
    "Namibia": "🇳🇦", "Nepal": "🇳🇵", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nicaragua": "🇳🇮",
    "Niger": "🇳🇪", "Nigeria": "🇳🇬", "North Korea": "🇰🇵", "North Macedonia": "🇲🇰", "Norway": "🇳🇴",
    "Oman": "🇴🇲", "Pakistan": "🇵🇰", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Peru": "🇵🇪",
    "Philippines": "🇵🇭", "Poland": "🇵🇱", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Romania": "🇷🇴",
    "Russia": "🇷🇺", "Rwanda": "🇷🇼", "Saudi Arabia": "🇸🇦", "Senegal": "🇸🇳", "Serbia": "🇷🇸",
    "Sierra Leone": "🇸🇱", "Singapore": "🇸🇬", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Somalia": "🇸🇴",
    "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩",
    "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Syria": "🇸🇾", "Taiwan": "🇹🇼", "Tajikistan": "🇹🇯",
    "Tanzania": "🇹🇿", "Thailand": "🇹🇭", "TOGO": "🇹🇬", "Tunisia": "🇹🇳", "Turkey": "🇹🇷",
    "Turkmenistan": "🇹🇲", "Uganda": "🇺🇬", "Ukraine": "🇺🇦", "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧",
    "United States": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿", "Venezuela": "🇻🇪", "Vietnam": "🇻🇳",
    "Yemen": "🇾🇪", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼", "Unknown Country": "🏴‍☠️"
}

SERVICE_KEYWORDS = {
    "Facebook": ["facebook"],
    "Google": ["google", "gmail"],
    "WhatsApp": ["whatsapp"],
    "Telegram": ["telegram"],
    "Instagram": ["instagram"],
    "Amazon": ["amazon"],
    "Netflix": ["netflix"],
    "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook", "live.com"],
    "Apple": ["apple", "icloud"],
    "Twitter": ["twitter"],
    "Snapchat": ["snapchat"],
    "TikTok": ["tiktok"],
    "Discord": ["discord"],
    "Signal": ["signal"],
    "Viber": ["viber"],
    "IMO": ["imo"],
    "PayPal": ["paypal"],
    "Binance": ["binance"],
    "Uber": ["uber"],
    "Bolt": ["bolt"],
    "Airbnb": ["airbnb"],
    "Yahoo": ["yahoo"],
    "Steam": ["steam"],
    "Blizzard": ["blizzard"],
    "Foodpanda": ["foodpanda"],
    "Pathao": ["pathao"],
    "Messenger": ["messenger", "meta"],
    "Gmail": ["gmail", "google"],
    "YouTube": ["youtube", "google"],
    "X": ["x", "twitter"],
    "eBay": ["ebay"],
    "AliExpress": ["aliexpress"],
    "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"],
    "Outlook": ["outlook", "microsoft"],
    "Skype": ["skype", "microsoft"],
    "Spotify": ["spotify"],
    "iCloud": ["icloud", "apple"],
    "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"],
    "Venmo": ["venmo"],
    "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"],
    "Coinbase": ["coinbase"],
    "KuCoin": ["kucoin"],
    "Bybit": ["bybit"],
    "OKX": ["okx"],
    "Huobi": ["huobi"],
    "Kraken": ["kraken"],
    "MetaMask": ["metamask"],
    "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"],
    "Xbox": ["xbox", "microsoft"],
    "Twitch": ["twitch"],
    "Reddit": ["reddit"],
    "ProtonMail": ["protonmail", "proton"],
    "Zoho": ["zoho"],
    "Quora": ["quora"],
    "StackOverflow": ["stackoverflow"],
    "LinkedIn": ["linkedin"],
    "Indeed": ["indeed"],
    "Upwork": ["upwork"],
    "Fiverr": ["fiverr"],
    "Glassdoor": ["glassdoor"],
    "Airbnb": ["airbnb"],
    "Booking.com": ["booking.com", "booking"],
    "Careem": ["careem"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "McDonald's": ["mcdonalds", "mcdonald's"],
    "KFC": ["kfc"],
    "Nike": ["nike"],
    "Adidas": ["adidas"],
    "Shein": ["shein"],
    "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"],
    "Bumble": ["bumble"],
    "Grindr": ["grindr"],
    "Line": ["line"],
    "WeChat": ["wechat"],
    "VK": ["vk", "vkontakte"],
    "Unknown": ["unknown"]
}

SERVICE_EMOJIS = {
    "Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
    "Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦", "X": "❌",
    "TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "eBay": "📦", "AliExpress": "📦",
    "Alibaba": "🏭", "Flipkart": "📦", "Microsoft": "🪟", "Outlook": "📧", "Skype": "📞",
    "Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "iCloud": "☁️", "PayPal": "💰",
    "Stripe": "💳", "Cash App": "💵", "Venmo": "💸", "Zelle": "🏦", "Wise": "🌐",
    "Binance": "🪙", "Coinbase": "🪙", "KuCoin": "🪙", "Bybit": "📈", "OKX": "🟠",
    "Huobi": "🔥", "Kraken": "🐙", "MetaMask": "🦊", "Discord": "🗨️", "Steam": "🎮",
    "Epic Games": "🕹️", "PlayStation": "🎮", "Xbox": "🎮", "Twitch": "📺", "Reddit": "👽",
    "Yahoo": "🟣", "ProtonMail": "🔐", "Zoho": "📬", "Quora": "❓", "StackOverflow": "🧑‍💻",
    "LinkedIn": "💼", "Indeed": "📋", "Upwork": "🧑‍💻", "Fiverr": "💻", "Glassdoor": "🔎",
    "Airbnb": "🏠", "Booking.com": "🛏️", "Uber": "🚗", "Lyft": "🚕", "Bolt": "🚖",
    "Careem": "🚗", "Swiggy": "🍔", "Zomato": "🍽️", "Foodpanda": "🍱",
    "McDonald's": "🍟", "KFC": "🍗", "Nike": "👟", "Adidas": "👟", "Shein": "👗",
    "OnlyFans": "🔞", "Tinder": "🔥", "Bumble": "🐝", "Grindr": "😈", "Signal": "🔐",
    "Viber": "📞", "Line": "💬", "WeChat": "💬", "VK": "🌐", "Unknown": "❓"
}

# --- FUNCTIONS ---
def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'w') as f: json.dump(INITIAL_CHAT_IDS, f)
        return INITIAL_CHAT_IDS
    try:
        with open(CHAT_IDS_FILE, 'r') as f: return json.load(f)
    except: return INITIAL_CHAT_IDS

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f: json.dump(chat_ids, f, indent=4)

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def load_processed_ids():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, 'r') as f: return set(json.load(f))
    except: return set()

def save_processed_id(sms_id):
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    with open(STATE_FILE, 'w') as f: json.dump(list(processed_ids), f)

# --- TELEGRAM HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_CHAT_IDS:
        await update.message.reply_text(
            "Welcome Admin!\n"
            "You can use the following commands:\n"
            "/add_chat <chat_id> - Add a new chat ID\n"
            "/remove_chat <chat_id> - Remove a chat ID\n"
            "/list_chats - List all chat IDs"
        )
    else:
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    try:
        new_id = context.args[0]
        ids = load_chat_ids()
        if new_id not in ids:
            ids.append(new_id)
            save_chat_ids(ids)
            await update.message.reply_text(f"✅ Chat ID {new_id} added.")
        else: await update.message.reply_text("⚠️ Already exists.")
    except: await update.message.reply_text("❌ Use: /add_chat <id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    try:
        rem_id = context.args[0]
        ids = load_chat_ids()
        if rem_id in ids:
            ids.remove(rem_id)
            save_chat_ids(ids)
            await update.message.reply_text(f"✅ Chat ID {rem_id} removed.")
        else: await update.message.reply_text("⚠️ Not found.")
    except: await update.message.reply_text("❌ Use: /remove_chat <id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    ids = load_chat_ids()
    msg = "📜 Chat IDs:\n" + "\n".join(ids) if ids else "No IDs."
    await update.message.reply_text(msg)

# --- SCRAPING LOGIC ---
async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = datetime.utcnow()
        start_date = today - timedelta(days=1)
        from_str, to_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        
        # 1. Summary
        res1 = await client.post(SMS_API_ENDPOINT, headers=headers, data={'from': from_str, 'to': to_str, '_token': csrf_token})
        if res1.status_code != 200: return []
        
        soup = BeautifulSoup(res1.text, 'html.parser')
        group_ids = [re.search(r"getDetials\('(.+?)'\)", d.get('onclick','')).group(1) for d in soup.find_all('div', {'class': 'pointer'}) if "getDetials" in d.get('onclick','')]
        
        num_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for gid in group_ids:
            # 2. Numbers
            res2 = await client.post(num_url, headers=headers, data={'start': from_str, 'end': to_str, 'range': gid, '_token': csrf_token})
            phones = [d.text.strip() for d in BeautifulSoup(res2.text, 'html.parser').select("div[onclick*='getDetialsNumber']")]
            
            for phone in phones:
                # 3. SMS
                res3 = await client.post(sms_url, headers=headers, data={'start': from_str, 'end': to_str, 'Number': phone, 'Range': gid, '_token': csrf_token})
                for card in BeautifulSoup(res3.text, 'html.parser').find_all('div', class_='card-body'):
                    p = card.find('p', class_='mb-0')
                    if not p: continue
                    text = p.get_text(separator='\n').strip()
                    
                    # Logic
                    uid = f"{phone}-{text[:20]}"
                    service = "Unknown"
                    for s, kws in SERVICE_KEYWORDS.items():
                        if any(k in text.lower() for k in kws): service = s; break
                    
                    code = (re.search(r'(\d{3}-\d{3})', text) or re.search(r'\b(\d{4,8})\b', text)).group(1) if (re.search(r'(\d{3}-\d{3})', text) or re.search(r'\b(\d{4,8})\b', text)) else "N/A"
                    cname = re.match(r'([a-zA-Z\s]+)', gid).group(1).strip() if re.match(r'([a-zA-Z\s]+)', gid) else "Unknown"
                    flag = COUNTRY_FLAGS.get(cname, "🏴‍☠️")
                    
                    all_messages.append({"id": uid, "time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), "number": phone, "country": cname, "flag": flag, "service": service, "code": code, "full_sms": text})
        return all_messages
    except: return []

async def send_to_tele(context, chat_id, msg):
    try:
        emo = SERVICE_EMOJIS.get(msg['service'], "❓")
        txt = (f"🔔 *You have successfully received OTP*\n\n" 
               f"📞 *Number:* `{escape_markdown(msg['number'])}`\n" 
               f"🔑 *Code:* `{escape_markdown(msg['code'])}`\n" 
               f"🏆 *Service:* {emo} {escape_markdown(msg['service'])}\n" 
               f"🌎 *Country:* {escape_markdown(msg['country'])} {msg['flag']}\n" 
               f"⏳ *Time:* `{escape_markdown(msg['time'])}`\n\n" 
               f"💬 *Message:*\n```\n{msg['full_sms']}\n```")
        await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode='MarkdownV2')
    except Exception as e: print(f"❌ Send Error: {e}")

# --- LOGIN SILUMAN (UNDETECTED) ---
def login_via_uc():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-popup-blocking")
    
    # Init driver siluman
    driver = uc.Chrome(options=options, version_main=None) # Auto version

    try:
        print("ℹ️ Membuka Chrome Siluman...")
        driver.get(LOGIN_URL)
        
        # 1. ISI EMAIL
        print("⏳ Menunggu kolom Email (60 detik max)...")
        # Di sini kita kasih waktu 60 detik. Kalau Cloudflare muncul, LU KLIK MANUAL!
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "email")))
        
        print("✍️ Mengisi Email...")
        driver.find_element(By.NAME, "email").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        # 2. KLIK LOGIN
        print("🖱️ Klik Login...")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 3. TUNGGU DASHBOARD
        print("⏳ Menunggu masuk dashboard...")
        WebDriverWait(driver, 30).until(EC.url_contains("portal"))
        print("✅ Login SUKSES! Mengambil data...")

        cookies = driver.get_cookies()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        csrf = soup.find('meta', {'name': 'csrf-token'})['content']
        
        jar = httpx.Cookies()
        for c in cookies: jar.set(c['name'], c['value'], domain=c['domain'])
        
        return jar, csrf, driver.current_url

    except Exception as e:
        print(f"❌ Login Gagal/Timeout: {e}")
        return None, None, None
    finally:
        try: driver.quit()
        except: pass

# --- JOB ---
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n--- [{datetime.utcnow().strftime('%H:%M:%S')}] Checking... ---")
    
    cookies, csrf, dash_url = await asyncio.to_thread(login_via_uc)
    
    if not cookies: 
        print("❌ Login gagal. Coba lagi nanti.")
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Referer': dash_url, 'X-CSRF-TOKEN': csrf, 'X-Requested-With': 'XMLHttpRequest'}
    
    async with httpx.AsyncClient(cookies=cookies, timeout=30.0, follow_redirects=True) as client:
        msgs = await fetch_sms_from_api(client, headers, csrf)
        if not msgs: print("💤 No messages."); return
        
        processed = load_processed_ids()
        chats = load_chat_ids()
        count = 0
        for m in reversed(msgs):
            if m['id'] not in processed:
                count += 1
                print(f"🔥 OTP: {m['code']} ({m['service']})")
                for cid in chats: await send_to_tele(context, cid, m)
                save_processed_id(m['id'])
        if count: print(f"✅ Sent {count} msgs.")

def main():
    print("🚀 BOT IVAS (ANTI-CLOUDFLARE) STARTING...")
    if not ADMIN_CHAT_IDS: return
    app = Application.builder().token(YOUR_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("add_chat", add_chat_command))
    app.add_handler(CommandHandler("remove_chat", remove_chat_command))
    app.add_handler(CommandHandler("list_chats", list_chats_command))
    app.job_queue.run_repeating(check_sms_job, interval=POLLING_INTERVAL_SECONDS, first=1)
    print("🤖 Bot Online. Tunggu Chrome muncul...")
    app.run_polling()

if __name__ == "__main__":
    main()

