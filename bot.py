#!/usr/bin/env python3
"""
IVASMS Auto Forwarding Bot
Automatically forwards SMS from ivasms.com to Telegram

Version: 1.0.0
Developer: Samuels Ramon
Company: E.U.W IT GROUP LTD.
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Samuels Ramon"
__company__ = "E.U.W IT GROUP LTD."
__license__ = "MIT"

import os, time, asyncio, html, logging, re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# ======= CONFIG =======
BOT_TOKEN = "7331162045:AAHxVfQK0HJ-2kK91a2xL9a9YBFbMCGVEmI"     # Your Telegram bot token # Get from @BotFather   
ADMIN_ID = 8446734557                                            # Your Telegram user ID
CHAT_ID = -1003594038682                                         # Your channel/group ID

# Login credentials
EMAIL = "rofik7244@gmail.com"             # Your ivasms.com email
PASSWORD = "GanzJB123"                     # Your ivasms.com password

HEADLESS = False  # Set True to hide browser

os.makedirs("downloads", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_auto.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fix emoji display on Windows console
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

driver = None

# ---------- BROWSER & LOGIN ----------
def init_browser():
    global driver
    try:
        logger.info("🌐 Opening Chrome browser...")
        options = uc.ChromeOptions()
        if HEADLESS:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        # On Windows, detect installed Chrome major version and pass to UC
        version_main = None
        try:
            if os.name == 'nt':
                # Read Chrome version from Windows Registry
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Google\\Chrome\\BLBeacon") as key:
                        ver, _ = winreg.QueryValueEx(key, "version")
                        version_main = int(str(ver).split('.')[0])
                except Exception:
                    pass
            
            if version_main:
                logger.info(f"🧩 Detected Chrome major version: {version_main}")
                driver = uc.Chrome(options=options, version_main=version_main, use_subprocess=True)
            else:
                logger.info("🧩 Could not detect Chrome version, letting UC auto-select driver")
                driver = uc.Chrome(options=options, use_subprocess=True)
        except Exception as e:
            logger.error(f"❌ Primary Chrome start failed: {e}")
            # If error mentions current browser version, retry with that version
            try:
                msg = str(e)
                m = re.search(r"Current browser version is\s+(\d+)", msg)
                if m:
                    detected = int(m.group(1))
                    logger.info(f"🔁 Retrying with detected Chrome major version: {detected}")
                    driver = uc.Chrome(options=options, version_main=detected, use_subprocess=True)
                else:
                    raise RuntimeError("No version hint in error")
            except Exception as e_retry:
                logger.warning(f"⚠️ Version retry failed: {e_retry}")
                # Final fallback attempts
                try:
                    driver = uc.Chrome(options=options)
                except Exception as e2:
                    logger.error(f"❌ Fallback Chrome start failed: {e2}")
                    raise

        logger.info("✅ Browser opened")
        return True
    except Exception as e:
        logger.error(f"❌ Browser error: {e}")
        return False

def auto_login():
    """Automatic login to ivasms.com"""
    global driver
    
    try:
        logger.info("🔐 Logging in to ivasms.com...")
        
        # Go to login page
        driver.get("https://www.ivasms.com/login")
        time.sleep(4)
        
        # Check if already logged in
        if "portal" in driver.current_url:
            logger.info("✅ Already logged in!")
            return True
        
        # Enter email
        logger.info("📧 Entering email...")
        try:
            email_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
        except:
            # Try alternate selector
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
        
        email_field.clear()
        time.sleep(0.5)
        
        # Type email character by character (more human-like)
        for char in EMAIL:
            email_field.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Enter password
        logger.info("🔑 Entering password...")
        try:
            password_field = driver.find_element(By.NAME, "password")
        except:
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        password_field.clear()
        time.sleep(0.5)
        
        # Type password character by character
        for char in PASSWORD:
            password_field.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Click login button
        logger.info("👆 Clicking login button...")
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]")
        
        login_btn.click()
        
        # Wait for redirect
        logger.info("⏳ Waiting for login redirect...")
        time.sleep(8)
        
        # Check if logged in
        current_url = driver.current_url
        if "portal" in current_url or "dashboard" in current_url:
            logger.info("✅ Login successful!")
            return True
        else:
            logger.error(f"❌ Login failed! Current URL: {current_url}")
            # Take screenshot for debugging
            try:
                driver.save_screenshot("login_failed.png")
                logger.info("📸 Screenshot saved: login_failed.png")
            except:
                pass
            return False
            
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        try:
            driver.save_screenshot("login_error.png")
        except:
            pass
        return False

def get_sms_data():
    """Get SMS data from page"""
    global driver
    
    try:
        # Navigate to live SMS page
        target_url = "https://www.ivasms.com/portal/live/my_sms"
        
        if driver.current_url != target_url:
            logger.info(f"📱 Navigating to SMS page...")
            driver.get(target_url)
            time.sleep(5)  # Wait longer for page load
        
        # Wait for data to load with explicit wait
        logger.info("⏳ Waiting for SMS data to load...")
        try:
            # Wait for table rows with actual content (not empty)
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr td")) > 0
            )
            logger.info("✅ Table elements found")
            time.sleep(2)  # Extra wait for content to populate
        except Exception as e:
            logger.warning(f"⚠️ Timeout waiting for table content: {e}")
            time.sleep(5)  # Fallback wait
        
        # Try to get data via AJAX
        logger.info("🔍 Fetching SMS data...")
        
        script = """
        var callback = arguments[arguments.length - 1];
        
        // Make AJAX request
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/portal/live/my_sms', true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    callback({success: true, data: data});
                } catch(e) {
                    // If not JSON, try parsing HTML
                    callback({success: false, html: xhr.responseText.substring(0, 500)});
                }
            } else {
                callback({success: false, error: xhr.status});
            }
        };
        xhr.onerror = function() {
            callback({success: false, error: 'Network error'});
        };
        xhr.send();
        """
        
        driver.set_script_timeout(15)
        result = driver.execute_async_script(script)
        
        if result and result.get('success'):
            logger.info("✅ Got SMS data from API")
            return result.get('data')
        
        # Fallback: Parse HTML table
        logger.info("📋 Parsing HTML table...")
        sms_list = []
        
        # Take screenshot for debugging
        try:
            driver.save_screenshot("sms_page_debug.png")
            logger.info("📸 Screenshot saved: sms_page_debug.png")
        except:
            pass
        
        # Check page source for debugging
        try:
            page_source = driver.page_source
            if "No SMS" in page_source or "no sms" in page_source.lower():
                logger.info("ℹ️ Page says 'No SMS'")
            if "my_sms" in page_source.lower():
                logger.info("✅ 'my_sms' found in page source")
            
            # Save page HTML for inspection
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            logger.info("📄 Page source saved: page_source.html")
        except:
            pass
        
        # Try to find table rows
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            logger.info(f"Found {len(rows)} table rows")
            
            for idx, row in enumerate(rows):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_text = row.text.strip()
                    
                    # Debug: Print each cell content
                    cell_contents = [f"Cell{i}: '{cell.text[:20]}'" for i, cell in enumerate(cells)]
                    logger.info(f"Row {idx}: {len(cells)} cells, text: '{row_text[:50]}'")
                    logger.info(f"  Cells: {', '.join(cell_contents)}")
                    
                    # Skip if not enough cells
                    if len(cells) < 2:
                        logger.info(f"  Skipped: Not enough cells")
                        continue
                    
                    # Skip headers
                    if "SID" in row_text or "Limit" in row_text or "Message" in row_text:
                        logger.info(f"  Skipped: Header row")
                        continue
                    
                    # Skip empty rows
                    if not row_text or len(row_text) < 5:
                        logger.info(f"  Skipped: Empty row")
                        continue
                    
                    # Extract data from cells
                    phone = cells[0].text.strip() if len(cells) > 0 else "Unknown"
                    sid = cells[1].text.strip() if len(cells) > 1 else str(abs(hash(row_text)))
                    
                    # Message is usually in last cell or cell 4
                    if len(cells) > 4:
                        message = cells[4].text.strip()
                    else:
                        message = cells[-1].text.strip()
                    
                    # Skip if message is empty
                    if not message or len(message) < 2:
                        logger.info(f"  Skipped: No message content")
                        continue
                    
                    # Extract OTP
                    otp_matches = re.findall(r'\b\d{4,8}\b', message)
                    otp = otp_matches[0] if otp_matches else "N/A"
                    
                    sms_data = {
                        "id": sid if sid else str(abs(hash(row_text))),
                        "to": phone,
                        "message": message,
                        "otp": otp
                    }
                    
                    sms_list.append(sms_data)
                    logger.info(f"  ✅ Extracted SMS: {phone} - {message[:30]}...")
                    
                except Exception as e:
                    logger.error(f"  Error processing row {idx}: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"Error parsing table: {e}")
        
        if sms_list:
            logger.info(f"✅ Found {len(sms_list)} SMS")
            return {"sms_list": sms_list}
        else:
            logger.info("ℹ️ No SMS found")
            return {"sms_list": []}
        
    except Exception as e:
        logger.error(f"❌ Error getting SMS: {e}")
        return None

# ---------- TELEGRAM ----------
def format_sms_message(phone, sid, otp, message, timestamp):
    """Format SMS for Telegram"""
    if len(message) > 200:
        message = message[:200] + "..."
    
    return (
        f"<b>🔔 NEW SMS RECEIVED</b>\n"
        f"<pre>╭━━━━━━━━━━━━━━━━━━━━━━━╮</pre>\n"
        f"<b>📱 Phone Number:</b>\n"
        f"<code>{phone}</code>\n\n"
        f"<b>🆔 Service ID:</b>\n"
        f"<code>{sid}</code>\n\n"
        f"<b>💬 Message Content:</b>\n"
        f"<pre>{html.escape(message)}</pre>\n\n"
        f"<b>🔑 OTP Code:</b>\n"
        f"<code>{otp}</code>\n\n"
        f"<b>⏰ Received At:</b>\n"
        f"<code>{timestamp}</code>\n"
        f"<pre>╰━━━━━━━━━━━━━━━━━━━━━━━╯</pre>\n"
        f"<i>⚡ Powered by: <b>Samuels Ramon</b></i>\n"
        f"<i>🏢 <b>EUW IT GROUP</b></i>"
    )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ <b>IVA SMS Bot Running!</b>\n\n"
        "🤖 Auto-login enabled\n"
        "📱 Monitoring SMS\n"
        "📨 Forwarding to Telegram",
        parse_mode="HTML"
    )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    status = "🟢 Running" if driver else "🔴 Stopped"
    await update.message.reply_text(
        f"<b>🤖 IVASMS Auto Bot Status</b>\n\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Version:</b> {__version__}\n"
        f"<b>Email:</b> {EMAIL}\n"
        f"<b>Mode:</b> Automatic\n\n"
        f"<i>👨‍💻 {__author__}</i>\n"
        f"<i>🏢 {__company__}</i>",
        parse_mode="HTML"
    )

# ---------- MONITOR ----------
async def monitor_sms(app):
    global driver
    
    logger.info("🚀 Starting IVA SMS Monitor...")
    
    # Initialize browser
    if not init_browser():
        logger.error("❌ Failed to start browser")
        return
    
    # Auto-login
    if not auto_login():
        logger.error("❌ Failed to login")
        try:
            await app.bot.send_message(
                chat_id=ADMIN_ID,
                text="❌ <b>Login Failed!</b>\n\nCheck bot_auto.log for details",
                parse_mode="HTML"
            )
        except:
            pass
        return
    
    # Notify start
    try:
        await app.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "✅ <b>Bot Started Successfully!</b>\n\n"
                "🌐 Browser: Running\n"
                "🔐 Login: Success\n"
                "📱 Monitoring: Active\n\n"
                f"Email: {EMAIL}"
            ),
            parse_mode="HTML"
        )
    except:
        pass
    
    seen_sms = set()
    error_count = 0
    
    logger.info("👀 Monitoring for SMS...")
    
    while True:
        try:
            # Get SMS data
            data = get_sms_data()
            
            if not data:
                error_count += 1
                logger.warning(f"⚠️ Failed to get data (errors: {error_count})")
                
                # Re-login after 5 errors
                if error_count >= 5:
                    logger.info("🔄 Too many errors, re-logging in...")
                    if auto_login():
                        error_count = 0
                        logger.info("✅ Re-login successful")
                    else:
                        logger.error("❌ Re-login failed")
                
                await asyncio.sleep(15)
                continue
            
            error_count = 0
            sms_list = data.get("sms_list", [])
            
            # Process each SMS
            for sms in sms_list:
                sms_id = sms.get("id")
                
                # Skip if already seen
                if sms_id in seen_sms:
                    continue
                
                seen_sms.add(sms_id)
                
                # Keep set size manageable
                if len(seen_sms) > 1000:
                    seen_sms = set(list(seen_sms)[-500:])
                
                # Extract data
                phone = sms.get("to", "Unknown")
                message = sms.get("message", "")
                otp = sms.get("otp", "N/A")
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                
                # Format message
                msg = format_sms_message(phone, sms_id, otp, message, timestamp)
                
                # Send to Telegram
                try:
                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text=msg,
                        parse_mode="HTML"
                    )
                    logger.info(f"✅ Forwarded SMS {sms_id} to Telegram")
                except Exception as e:
                    logger.error(f"❌ Failed to send to Telegram: {e}")
            
            # Wait before next check
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
            error_count += 1
            await asyncio.sleep(10)

# ---------- MAIN ----------
async def post_init(app):
    asyncio.create_task(monitor_sms(app))

def main():
    global driver
    
    try:
        print("\n" + "="*60)
        print("╔════════════════════════════════════════════════════════╗")
        print("║                                                        ║")
        print("║          🔥 IVASMS AUTO FORWARDING BOT 🔥             ║")
        print("║                                                        ║")
        print("║         ⚡ Powered by Selenium & EUW IT GROUP ⚡       ║")
        print("║                                                        ║")
        print("╠════════════════════════════════════════════════════════╣")
        print("║                                                        ║")
        print("║   👨‍💻 Developer: Samuels Ramon                          ║")
        print("║   🏢 Company: EUW IT GROUP                             ║")
        print("║   📧 Email: saemuelsrom@gmail.com                      ║")
        print("║   🌐 Auto-Login: ✅ Enabled                            ║")
        print("║   📱 SMS Monitoring: ✅ Active                         ║")
        print("║   📨 Telegram Forward: ✅ Active                       ║")
        print("║                                                        ║")
        print("╚════════════════════════════════════════════════════════╝")
        print("="*60 + "\n")
        
        logger.info("🚀 Welcome to IVASMS AUTO BOT - STARTING...")
        logger.info("👨‍💻 Developer: Samuels Ramon (EUW IT GROUP)")
        
        app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
        app.add_handler(CommandHandler("start", start_cmd))
        app.add_handler(CommandHandler("status", status_cmd))
        
        logger.info("🤖 Bot running...")
        app.run_polling()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        if driver:
            logger.info("🔒 Closing browser...")
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()

