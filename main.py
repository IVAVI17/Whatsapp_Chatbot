import os
import json
import datetime
import locale
from flask import Flask, request, jsonify
import requests
import gspread
from google.oauth2.service_account import Credentials
from babel.dates import format_datetime
import pytz


# ========= CONFIG =========
WHATSAPP_TOKEN = "EAAUwNVITeDIBPf7KZBnGcgzfznY1zBh6GoViwSjc4Qhq80M5mOYnq5QmBh9MTgxdMCBYXKX9BZCBiW1uSBmOltENaLqG9qZAxbrsooUd4GA5YjP4uqxqeKkAJ0VEFtlLg8CG4dLUUfploMgzzZCsrqsWR1KAycbL84xLZAwWFdXzX7jCKKj4TvuzSjbmQe9fv5hQZBzZBzE8C0ZBPmkrEGexelshXB5SyuCoZAfei"
PHONE_NUMBER_ID = "810864372104195"
VERIFY_TOKEN = "myapptoken"

SPREADSHEET_ID = "1LWhTGN3mNYqe7gtuRNAKBx8W87HtO5QmLPxv-8zWCc8"
SHEET_CALENDAR = "Calendar"
SHEET_STATE = "State"

WORKING_DAYS_TO_GENERATE = 5
START_HOUR = 10
END_HOUR = 18
LUNCH_HOUR = 13
IST = "Asia/Kolkata"
HOLIDAYS = ["2025-08-29"]

# ========= GOOGLE SHEETS =========
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)
client = gspread.authorize(creds)
ss = client.open_by_key(SPREADSHEET_ID)

def get_sheet(name):
    return ss.worksheet(name)

# ========= MESSAGES =========
TEXTS = {
    "en": {
        "greet": "👋 Welcome! Please choose your language:",
        "choose_slot": "📅 Choose your appointment slot:",
        "no_slots": "❌ No available slots right now.",
        "booked": "✅ Appointment booked for {date} at {time}.",
        "taken": "❌ Slot already taken, please pick again.",
        "start": "Please type 'hi' to start booking ✅"
    },
    "hi": {
        "greet": "👋 स्वागत है! कृपया अपनी भाषा चुनें:",
        "choose_slot": "📅 अपनी अपॉइंटमेंट स्लॉट चुनें:",
        "no_slots": "❌ अभी कोई स्लॉट उपलब्ध नहीं है।",
        "booked": "✅ आपकी अपॉइंटमेंट {date} को {time} पर बुक हो गई है।",
        "taken": "❌ यह स्लॉट पहले से बुक है, कृपया दूसरा चुनें।",
        "start": "कृपया बुकिंग शुरू करने के लिए 'hi' लिखें ✅"
    }
}

LANG_OPTIONS = [
    {"id": "LANG|en", "title": "English", "description": "Proceed in English"},
    {"id": "LANG|hi", "title": "हिन्दी", "description": "हिंदी में जारी रखें"}
]

# ========= UTILS =========
# def pretty_date(iso_str, lang="en"):
#     d = datetime.datetime.strptime(iso_str, "%Y-%m-%d")
#     if lang == "hi":
#         return d.strftime("%d %B %Y")  # हिंदी महीनों के लिए सिस्टम locale की जरूरत
#     return d.strftime("%a, %d %b %Y")
def pretty_date(iso_str, lang="en"):
    d = datetime.datetime.strptime(iso_str, "%Y-%m-%d")
    tz = pytz.timezone("Asia/Kolkata")
    d = tz.localize(d)

    if lang == "hi":
        return format_datetime(d, "EEEE, d MMMM y", locale="hi_IN")
    else:
        return format_datetime(d, "EEE, d MMM y", locale="en_IN")


# ========= SHEET HELPERS =========
def init_sheets():
    try:
        ss.worksheet(SHEET_CALENDAR)
    except:
        ss.add_worksheet(SHEET_CALENDAR, rows="100", cols="5")
        sh = get_sheet(SHEET_CALENDAR)
        sh.append_row(["Date", "Time", "Status", "Patient", "Phone"])
    try:
        ss.worksheet(SHEET_STATE)
    except:
        ss.add_worksheet(SHEET_STATE, rows="100", cols="6")
        st = get_sheet(SHEET_STATE)
        st.append_row(["Phone", "State", "Date", "Time", "Lang", "Name"])

def get_state(phone):
    st = get_sheet(SHEET_STATE)
    records = st.get_all_records()
    for idx, row in enumerate(records, start=2):
        if str(row["Phone"]) == str(phone):
            return row, idx
    st.append_row([phone, "NEW", "", "", "en", ""])
    return {"Phone": phone, "State": "NEW", "Date": "", "Time": "", "Lang": "en", "Name": ""}, st.row_count

def set_state(phone, fields):
    st = get_sheet(SHEET_STATE)
    row, idx = get_state(phone)
    for col, key in enumerate(["Phone", "State", "Date", "Time", "Lang", "Name"], start=1):
        if key in fields:
            st.update_cell(idx, col, fields[key])

def get_available_slots():
    cal = get_sheet(SHEET_CALENDAR)
    rows = cal.get_all_records()
    slots = []
    for r in rows:
        if r["Status"] == "Available":
            slots.append((r["Date"], r["Time"]))
    return slots

def book_slot(date_iso, time, patient, phone):
    cal = get_sheet(SHEET_CALENDAR)
    rows = cal.get_all_records()
    for i, r in enumerate(rows, start=2):
        if r["Date"] == date_iso and r["Time"] == time and r["Status"] == "Available":
            cal.update_cell(i, 3, "Busy")
            cal.update_cell(i, 4, patient)
            cal.update_cell(i, 5, phone)
            return True
    return False

# ========= WHATSAPP HELPERS =========
def call_whatsapp(payload):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, json=payload)
    print("WA RESPONSE:", r.text)

def send_text(to, body):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body}
    }
    call_whatsapp(payload)

def send_language_choice(to):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": TEXTS["en"]["greet"]},
            "action": {
                "button": "Choose",
                "sections": [
                    {"title": "Languages", "rows": LANG_OPTIONS}
                ]
            }
        }
    }
    call_whatsapp(payload)

def send_slots(to, lang="en"):
    slots = get_available_slots()
    if not slots:
        send_text(to, TEXTS[lang]["no_slots"])
        return


    rows = []
    for d, t in slots:
        # short_date = datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d %b")
        d_obj = datetime.datetime.strptime(d, "%Y-%m-%d")
        tz = pytz.timezone("Asia/Kolkata")
        d_obj = tz.localize(d_obj)

        if lang == "hi":
            short_date = format_datetime(d_obj, "d MMM", locale="hi_IN")
        else:
            short_date = format_datetime(d_obj, "d MMM", locale="en_IN")

        rows.append({
            "id": f"SLOT|{d}|{t}",
            "title": f"{t} {short_date}",
            "description": f"{pretty_date(d, lang)}"
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": TEXTS[lang]["choose_slot"]},
            "action": {
                "button": "Select",
                "sections": [
                    {"title": "Available Slots", "rows": rows[:10]}
                ]
            }
        }
    }
    call_whatsapp(payload)

# ========= FLASK SERVER =========
app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", json.dumps(data, indent=2))
    changes = data.get("entry", [])[0].get("changes", [])[0].get("value", {})
    messages = changes.get("messages", [])
    if not messages:
        return "ok", 200

    msg = messages[0]
    from_ = msg["from"]
    profile_name = changes.get("contacts", [{}])[0].get("profile", {}).get("name", "Unknown")

    state, _ = get_state(from_)
    lang = state.get("Lang", "en")

    if msg["type"] == "text":
        body = msg["text"]["body"].lower()
        if body in ["hi", "hello", "hey", "नमस्ते", "हाय"]:
            set_state(from_, {"State": "ASKED_LANG"})
            send_language_choice(from_)
        else:
            send_text(from_, TEXTS[lang]["start"])

    elif msg["type"] == "interactive":
        lr = msg["interactive"].get("list_reply")
        if lr and lr["id"].startswith("LANG|"):
            _, chosen_lang = lr["id"].split("|")
            set_state(from_, {"Lang": chosen_lang, "State": "ASKED_SLOT"})
            send_slots(from_, lang=chosen_lang)

        elif lr and lr["id"].startswith("SLOT|"):
            _, d, t = lr["id"].split("|")
            success = book_slot(d, t, profile_name, from_)
            if success:
                set_state(from_, {"State": "BOOKED", "Date": d, "Time": t})
                send_text(from_, TEXTS[lang]["booked"].format(date=pretty_date(d, lang), time=t))
            else:
                send_text(from_, TEXTS[lang]["taken"])
                send_slots(from_, lang=lang)

    return "ok", 200

if __name__ == "__main__":
    init_sheets()
    app.run(host="0.0.0.0", port=5000)
