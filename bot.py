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
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# --- CONFIGURATION ---
YOUR_BOT_TOKEN = "7331162045:AAHxVfQK0HJ-2kK91a2xL9a9YBFbMCGVEmI"
ADMIN_CHAT_IDS = ["8446734557"]
INITIAL_CHAT_IDS = ["8446734557"]

USERNAME = "rofik7244@gmail.com"
PASSWORD = "GanzJB123"

# --- SYSTEM SETTINGS ---
LOGIN_URL = "https://www.ivasms.com/login"
BASE_URL = "https://www.ivasms.com/"
SMS_API_ENDPOINT = "https://www.ivasms.com/portal/sms/received/getsms"
POLLING_INTERVAL_SECONDS = 2
STATE_FILE = "processed_sms_ids.json"
CHAT_IDS_FILE = "chat_ids.json"

# --- DATA ---
COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Indonesia": "🇮🇩", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Malaysia": "🇲🇾", "Singapore": "🇸🇬", "Vietnam": "🇻🇳", "Thailand": "🇹🇭", "Philippines": "🇵🇭",
    "India": "🇮🇳", "China": "🇨🇳", "Russia": "🇷🇺", "Brazil": "🇧🇷", "Unknown Country": "🏴‍☠️"
}

SERVICE_KEYWORDS = {
    "WhatsApp": ["whatsapp"], "Telegram": ["telegram"], "Facebook": ["facebook"],
    "Google": ["google", "gmail"], "Instagram": ["instagram"], "TikTok": ["tiktok"],
    "Shopee": ["shopee"], "Dana": ["dana"], "Gojek": ["gojek"], "Grab": ["grab"],
    "Ovo": ["ovo"], "Tokopedia": ["tokopedia"], "Lazada": ["lazada"], "Bibit": ["bibit"],
    "Netflix": ["netflix"], "Twitter": ["twitter", "x code"], "Unknown": ["unknown"]
}

SERVICE_EMOJIS = {
    "WhatsApp": "🟢", "Telegram": "🔵", "Google": "🔴", "Facebook": "📘", "Unknown": "❓"
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

# --- COMMANDS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid in ADMIN_CHAT_IDS:
        await update.message.reply_text("✅ Bot Ready Bos! Monitoring Ivasms...")
    else:
        await update.message.reply_text("❌ Lu siapa? Bukan admin.")

# --- CORE LOGIC ---
async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = datetime.utcnow()
        start_date = today - timedelta(days=1)
        from_str, to_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        
        # 1. Get Summary
        first_payload = {'from': from_str, 'to': to_str, '_token': csrf_token}
        summary_res = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_res.raise_for_status()
        
        soup = BeautifulSoup(summary_res.text, 'html.parser')
        group_divs = soup.find_all('div', {'class': 'pointer'})
        if not group_divs: return []
        
        group_ids = [re.search(r"getDetials\('(.+?)'\)", d.get('onclick','')).group(1) for d in group_divs if "getDetials" in d.get('onclick','')]
        
        # 2. Loop Country Groups
        num_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for gid in group_ids:
            # Get Numbers
            num_payload = {'start': from_str, 'end': to_str, 'range': gid, '_token': csrf_token}
            num_res = await client.post(num_url, headers=headers, data=num_payload)
            num_soup = BeautifulSoup(num_res.text, 'html.parser')
            phones = [d.text.strip() for d in num_soup.select("div[onclick*='getDetialsNumber']")]
            
            for phone in phones:
                # Get SMS
                sms_payload = {'start': from_str, 'end': to_str, 'Number': phone, 'Range': gid, '_token': csrf_token}
                final_res = await client.post(sms_url, headers=headers, data=sms_payload)
                sms_cards = BeautifulSoup(final_res.text, 'html.parser').find_all('div', class_='card-body')
                
                for card in sms_cards:
                    p = card.find('p', class_='mb-0')
                    if not p: continue
                    text = p.get_text(separator='\n').strip()
                    
                    # Parsir Data
                    unique_id = f"{phone}-{text[:20]}" 
                    
                    service = "Unknown"
                    lower_text = text.lower()
                    for s_name, kws in SERVICE_KEYWORDS.items():
                        if any(k in lower_text for k in kws): 
                            service = s_name; break
                    
                    code_match = re.search(r'(\d{3}-\d{3})', text) or re.search(r'\b(\d{4,8})\b', text)
                    code = code_match.group(1) if code_match else "N/A"
                    
                    c_name = re.match(r'([a-zA-Z\s]+)', gid).group(1).strip() if re.match(r'([a-zA-Z\s]+)', gid) else "Unknown"
                    flag = COUNTRY_FLAGS.get(c_name, "🏴‍☠️")
                    
                    all_messages.append({
                        "id": unique_id, "time": datetime.utcnow().strftime('%H:%M:%S'), 
                        "number": phone, "country": c_name, "flag": flag, 
                        "service": service, "code": code, "full_sms": text
                    })
        return all_messages

    except Exception as e:
        print(f"❌ Error Fetching: {e}")
        return []

async def send_to_tele(context, chat_id, msg):
    try:
        emo = SERVICE_EMOJIS.get(msg['service'], "🔔")
        txt = (f"{emo} *OTP MASUK BOS!*\n\n"
               f"📞 *Nomor:* `{escape_markdown(msg['number'])}`\n"
               f"🔑 *Kode:* `{escape_markdown(msg['code'])}`\n"
               f"🏢 *Service:* {escape_markdown(msg['service'])}\n"
               f"🌍 *Negara:* {escape_markdown(msg['country'])} {msg['flag']}\n\n"
               f"💬 *Pesan:*\n`{escape_markdown(msg['full_sms'])}`")
        await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode='MarkdownV2')
    except Exception as e: print(f"❌ Gagal kirim ke Tele: {e}")

async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n--- [{datetime.utcnow().strftime('%H:%M:%S')}] Cek Pesan Baru... ---")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # 1. LOGIN
            login_pg = await client.get(LOGIN_URL, headers=headers)
            soup = BeautifulSoup(login_pg.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            
            data = {'email': USERNAME, 'password': PASSWORD}
            if token_input: data['_token'] = token_input['value']

            login_res = await client.post(LOGIN_URL, data=data, headers=headers)
            
            if "login" in str(login_res.url):
                print("❌ Login Gagal! Cek User/Pass.")
                return

            # 2. AMBIL CSRF TOKEN DASHBOARD
            dash_soup = BeautifulSoup(login_res.text, 'html.parser')
            meta_csrf = dash_soup.find('meta', {'name': 'csrf-token'})
            if not meta_csrf:
                print("❌ Gagal ambil Token CSRF baru.")
                return
            csrf = meta_csrf['content']
            headers['Referer'] = str(login_res.url)

            # 3. SCRAPING SMS
            msgs = await fetch_sms_from_api(client, headers, csrf)
            if not msgs:
                print("💤 Belum ada pesan baru.")
                return
            
            # 4. FILTER & KIRIM
            processed = load_processed_ids()
            chats = load_chat_ids()
            
            count = 0
            for m in reversed(msgs):
                if m['id'] not in processed:
                    count += 1
                    print(f"🔥 OTP BARU: {m['code']} ({m['service']})")
                    for cid in chats:
                        await send_to_tele(context, cid, m)
                    save_processed_id(m['id'])
            
            if count > 0: print(f"✅ Sukses kirim {count} pesan ke Telegram.")

        except Exception as e:
            print(f"❌ Error Loop: {e}")

def main():
    print(f"🚀 BOT IVAS STARTING...")
    app = Application.builder().token(YOUR_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.job_queue.run_repeating(check_sms_job, interval=POLLING_INTERVAL_SECONDS, first=1)
    print("🤖 Bot Berjalan! Tekan CTRL+C untuk stop.")
    app.run_polling()

if __name__ == "__main__":
    main()

