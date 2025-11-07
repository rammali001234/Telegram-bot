# cb_bot_with_token_check.py
# Usage: python cb_bot_with_token_check.py
# Requires: pip install requests

import requests, time, random, json, sys

# ---------- CONFIG (you can change DEV_USERNAME) ----------
DEV_USERNAME = "@nobi4t111"
REPORT_CODES = ["H8","BULLY","V!0","S3LF","SC4M","SP4M","D8","NUD"]
TITLE_VARIANTS = [
    "CB METHOD 🫶 ❤️‍🔥",
    "CB METHOD 💀🔥",
    "CB METHOD ⚡️🩶",
    "CB METHOD ❤️‍🔥💥",
    "CB METHOD ☠️🔥"
]
# ---------- END CONFIG ----------

def ask_token():
    print("Paste your Telegram bot token (it will not be stored):")
    tok = input().strip()
    return tok

def safe_get(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        return r
    except Exception as e:
        print("Network error:", e)
        return None

def safe_post(url, data=None, json_body=None, timeout=20):
    try:
        if json_body is not None:
            r = requests.post(url, json=json_body, timeout=timeout)
        else:
            r = requests.post(url, data=data, timeout=timeout)
        return r
    except Exception as e:
        print("Network error:", e)
        return None

def validate_token(api_base):
    r = safe_get(f"{api_base}/getMe")
    if not r:
        return False, "Network error"
    try:
        j = r.json()
    except Exception:
        return False, "Invalid response"
    if j.get("ok"):
        info = j.get("result", {})
        return True, info
    return False, j.get("description", "Invalid token")

# ----- Bot send/edit helpers -----
def send_message(api_base, chat_id, text, buttons=None, reply_to=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode":"Markdown"}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    r = safe_post(f"{api_base}/sendMessage", json_body=payload)
    if not r:
        return {}
    try:
        return r.json()
    except:
        return {}

def edit_message(api_base, chat_id, message_id, text):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode":"Markdown"}
    r = safe_post(f"{api_base}/editMessageText", json_body=payload)
    if not r:
        return {}
    try:
        return r.json()
    except:
        return {}

def answer_callback(api_base, callback_query_id):
    safe_post(f"{api_base}/answerCallbackQuery", data={"callback_query_id": callback_query_id})

def send_inline_keyboard(api_base, chat_id, text, buttons):
    keyboard = {"inline_keyboard": buttons}
    payload = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps(keyboard), "parse_mode":"Markdown"}
    safe_post(f"{api_base}/sendMessage", data=payload)

# ----- Generator, loading -----
def gen_cb_text():
    title = random.choice(TITLE_VARIANTS)
    picks = random.sample(REPORT_CODES, k=3)
    if random.random() < 0.2:
        picks[random.randrange(3)] = random.choice(REPORT_CODES)
    lines = [f"{random.randint(1,5)}X {p}" for p in picks]
    if random.random() < 0.5:
        random.shuffle(lines)
    body = "\n".join(lines)
    footer = f"\n\nDEV :- {DEV_USERNAME} × /next"
    return f"{title}\n\n{body}{footer}"

def send_loading(api_base, chat_id):
    frames = ["⏳ Loading Method.", "⏳ Loading Method..", "⏳ Loading Method..."]
    res = send_message(api_base, chat_id, frames[0])
    msg_id = res.get("result", {}).get("message_id")
    if not msg_id:
        return None
    for frame in frames[1:]:
        time.sleep(0.4)
        try:
            edit_message(api_base, chat_id, msg_id, frame)
        except:
            pass
    return msg_id

# ----- Main update handler -----
def handle_update(api_base, upd, state):
    # message handlers
    if "message" in upd:
        msg = upd["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip().lower()

        if text == "/start":
            buttons = [
                [{"text": "📘 How to Use", "callback_data": "how_use"}],
                [{"text": "⚡ Commands", "callback_data": "commands"}],
                [{"text": "👑 Developer", "callback_data": "developer"}]
            ]
            send_inline_keyboard(api_base, chat_id, "🔥 *Welcome to CB METHOD BOT* 🔥\n\nUse /cb  methods.", buttons)
            return

        if text == "/menu":
            buttons = [
                [{"text": "📘 How to Use", "callback_data": "how_use"}],
                [{"text": "⚡ Commands", "callback_data": "commands"}],
                [{"text": "👑 Developer", "callback_data": "developer"}]
            ]
            send_inline_keyboard(api_base, chat_id, "💡 *Select an Option:*", buttons)
            return

        if text == "/cb":
            msg_id = send_loading(api_base, chat_id)
            time.sleep(random.uniform(0.6, 1.2))
            cb_text = gen_cb_text()
            if msg_id:
                edit_message(api_base, chat_id, msg_id, cb_text)
                state[chat_id] = {"last_msg": msg_id}
            else:
                # fallback: send as new message
                res = send_message(api_base, chat_id, cb_text)
                state[chat_id] = {"last_msg": res.get("result", {}).get("message_id")}
            return

        if text == "/next":
            st = state.get(chat_id)
            if st and st.get("last_msg"):
                try:
                    edit_message(api_base, chat_id, st["last_msg"], "(Old Method Hidden 🕶)")
                except:
                    pass
            msg_id = send_loading(api_base, chat_id)
            time.sleep(random.uniform(0.6, 1.2))
            cb_text = gen_cb_text()
            if msg_id:
                edit_message(api_base, chat_id, msg_id, cb_text)
                state[chat_id] = {"last_msg": msg_id}
            else:
                res = send_message(api_base, chat_id, cb_text)
                state[chat_id] = {"last_msg": res.get("result", {}).get("message_id")}
            return

    # callback handlers
    if "callback_query" in upd:
        cq = upd["callback_query"]
        data = cq.get("data")
        chat_id = cq["message"]["chat"]["id"]
        msgid = cq["message"]["message_id"]
        answer_callback(api_base, cq.get("id"))
        if data == "how_use":
            edit_message(api_base, chat_id, msgid,
                         "📘 *HOW TO USE BOT:*\n\n"
                         "1️⃣ Type /cb → CB METHOD.\n"
                         "2️⃣ Type /next → Hide previous & get a new one.\n"
                         "3️⃣ Type /menu → Show options anytime.\n\n🔥 Enjoy creative methods!")
        elif data == "commands":
            edit_message(api_base, chat_id, msgid,
                         "⚡ *COMMANDS:*\n\n"
                         "/cb →  CB Method\n"
                         "/next → Next Method\n"
                         "/menu → Menu Options\n"
                         "/start → Start bot")
        elif data == "developer":
            edit_message(api_base, chat_id, msgid,
                         "👑 *Developer Info:*\nCreated by @nobi4t111\n⚙️ For Educational & Creative Purpose Only 🔥")

# ----- Poll loop -----
def poll_loop(api_base):
    offset = None
    state = {}
    print("Polling started... Press Ctrl+C to stop.")
    while True:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        try:
            r = safe_get(f"{api_base}/getUpdates", params=params, timeout=40)
            if not r:
                time.sleep(1)
                continue
            data = r.json()
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                handle_update(api_base, u, state)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as e:
            print("Poll error:", e)
            time.sleep(2)

# ----- MAIN -----
def main():
    token = ask_token()
    if not token:
        print("No token provided. Exiting.")
        return
    api_base = f"https://api.telegram.org/bot{token}"
    ok, info = validate_token(api_base)
    if not ok:
        print("Token validation failed:", info)
        print("Check token and network, then try again.")
        return
    bot_user = info.get("username", "<unknown>")
    print(f"Token valid. Bot username: @{bot_user}")
    print("Starting bot polling...")
    poll_loop(api_base)

if __name__ == "__main__":
    main()
