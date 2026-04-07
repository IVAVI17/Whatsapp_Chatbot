# -----------API CODE---------------------
# import requests
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Union, Dict, Any
# from datetime import datetime

# WHATSAPP_TOKEN = "EAA1u4zSZC3coBRFMuh0s7pXemBPezLhFs20EoW2PnUwmoObk8bClgYncIcoB8FGX3BkjOMC3Dhir8cBaoQ2nKPzJRrQVrTDuZBpTmSSIMjRUS3wQpayZBtZCaOJZCTEf6c7kvYe0mxMmpeeiX0cB2RjcxkzYyBnj6LAsZBTwRoN3ZASdYCnfmpc7ik16gDrsQ9DcwZDZD"
# PHONE_NUMBER_ID = "750846411455167"

# app = FastAPI()


# # ✅ FIXED MODEL (supports both positional + named params)
# class TemplateMessage(BaseModel):
#     phone_number: str
#     template_name: str
#     parameters: List[Union[str, Dict[str, Any]]]
#     expiration_time: str   # ISO format


# def send_template(phone: str, template_name: str, parameters: List[Union[str, Dict[str, Any]]]):
#     url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     components = []

#     if parameters:
#         # ✅ Named parameters (dict format)
#         if isinstance(parameters[0], dict):
#             components = [{
#                 "type": "body",
#                 "parameters": parameters
#             }]
#         else:
#             # ✅ Positional parameters (string format)
#             components = [{
#                 "type": "body",
#                 "parameters": [
#                     {"type": "text", "text": str(p)} for p in parameters
#                 ]
#             }]

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone,
#         "type": "template",
#         "template": {
#             "name": template_name,
#             "language": {
#                 "code": "en"   # ⚠️ Change to "en_US" if needed
#             },
#             "components": components
#         }
#     }

#     print("🔵 Payload being sent to WhatsApp:")
#     print(payload)

#     response = requests.post(url, headers=headers, json=payload)

#     print("🟢 WhatsApp Response:")
#     print(response.text)

#     return response.json(), response.status_code


# @app.post("/send_template_message")
# def send_message(data: TemplateMessage):

#     try:
#         now = datetime.utcnow()
#         expiry = datetime.fromisoformat(data.expiration_time)

#         if now > expiry:
#             return {
#                 "status": "expired",
#                 "message": "Template not sent because expiration time passed"
#             }

#         response, status = send_template(
#             data.phone_number,
#             data.template_name,
#             data.parameters
#         )

#         if status != 200:
#             raise HTTPException(status_code=status, detail=response)

#         return {
#             "status": "template_sent",
#             "whatsapp_response": response
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# ------------------ API CODE END --------------------------
# -----------------CRON JOB CODE------------------------
# import requests
# import mysql.connector
# import json
# import time
# import logging
# from datetime import datetime

# # ❌ REMOVE global token & phone number ID
# # WHATSAPP_TOKEN = "..."
# # PHONE_NUMBER_ID = "..."

# DB_CONFIG = {
#     "host": "localhost",
#     "port": 3307,
#     "user": "purpledocs",
#     "password": "purplebits1",
#     "database": "hospital_patient_project"
# }

# # 🧾 LOGGING
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )


# def get_db_connection():
#     return mysql.connector.connect(**DB_CONFIG)


# # ✅ UPDATED FUNCTION (takes token + phone_number_id)
# def send_template(payload, whatsapp_token, phone_number_id):
#     url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

#     headers = {
#         "Authorization": f"Bearer {whatsapp_token}",
#         "Content-Type": "application/json"
#     }

#     parameters = payload.get("parameters", [])
#     components = []

#     if parameters:
#         if isinstance(parameters[0], dict):
#             components = [{
#                 "type": "body",
#                 "parameters": parameters
#             }]
#         else:
#             components = [{
#                 "type": "body",
#                 "parameters": [
#                     {"type": "text", "text": str(p)} for p in parameters
#                 ]
#             }]

#     data = {
#         "messaging_product": "whatsapp",
#         "to": payload["phone_number"],
#         "type": "template",
#         "template": {
#             "name": payload["template_name"],
#             "language": {"code": "en_US"},  # ✅ FIXED
#             "components": components
#         }
#     }

#     logging.info(f"Sending message to {payload['phone_number']}")

#     response = requests.post(url, headers=headers, json=data)

#     return response.json(), response.status_code


# def process_messages():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         query = """
#             SELECT * FROM whatsapp_messages
#             WHERE status = 'not_sent'
#             AND expiration_time > NOW()
#             LIMIT 20
#         """

#         cursor.execute(query)
#         rows = cursor.fetchall()

#         if not rows:
#             logging.info("No pending messages")
#             return

#         logging.info(f"Processing {len(rows)} messages")

#         for row in rows:
#             try:
#                 payload = json.loads(row["payload"])

#                 # ✅ NEW: fetch from DB columns
#                 whatsapp_token = row["whatsapp_token"]
#                 phone_number_id = row["phone_number_id"]

#                 response, status_code = send_template(
#                     payload,
#                     whatsapp_token,
#                     phone_number_id
#                 )

#                 if status_code == 200:
#                     cursor.execute("""
#                         UPDATE whatsapp_messages
#                         SET status='sent',
#                             sent_time=%s,
#                             error=NULL
#                         WHERE id=%s
#                     """, (datetime.utcnow(), row["id"]))

#                     logging.info(f"Message SENT (ID: {row['id']})")

#                 else:
#                     cursor.execute("""
#                         UPDATE whatsapp_messages
#                         SET status='failed',
#                             error=%s,
#                             retry_count=retry_count+1
#                         WHERE id=%s
#                     """, (json.dumps(response), row["id"]))

#                     logging.error(f"Message FAILED (ID: {row['id']}): {response}")

#             except Exception as e:
#                 cursor.execute("""
#                     UPDATE whatsapp_messages
#                     SET status='failed',
#                         error=%s,
#                         retry_count=retry_count+1
#                     WHERE id=%s
#                 """, (str(e), row["id"]))

#                 logging.error(f"Exception for ID {row['id']}: {str(e)}")

#         conn.commit()

#     finally:
#         cursor.close()
#         conn.close()


# # 🔁 CONTINUOUS WORKER LOOP
# if __name__ == "__main__":
#     logging.info("🚀 WhatsApp Worker Started...")

#     while True:
#         try:
#             process_messages()
#         except Exception as e:
#             logging.error(f"Critical error: {str(e)}")

#         time.sleep(10)
#----------------------- CRON JOB CODE END ------------------------
#----------------------- SCHEDULER CODE --------------------------
import requests
import mysql.connector
import json
import logging
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "purpledocs",
    "password": "purplebits1",
    "database": "hospital_patient_project"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/logs/whatsapp_worker.log"),
        logging.StreamHandler()
    ]
)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def send_template(payload, whatsapp_token, phone_number_id):
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }

    parameters = payload.get("parameters", [])
    components = []

    if parameters:
        if isinstance(parameters[0], dict):
            components = [{
                "type": "body",
                "parameters": parameters
            }]
        else:
            components = [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(p)} for p in parameters
                ]
            }]

    data = {
        "messaging_product": "whatsapp",
        "to": payload["phone_number"],
        "type": "template",
        "template": {
            "name": payload["template_name"],
            "language": {"code": "en"},
            "components": components
        }
    }

    logging.info(f"Sending message to {payload['phone_number']}")
    response = requests.post(url, headers=headers, json=data)
    return response.json(), response.status_code

def process_messages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT * FROM whatsapp_messages
            WHERE status = 'not_sent'
            AND expiration_time > NOW()
            LIMIT 20
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            logging.info("No pending messages")
            return

        logging.info(f"Processing {len(rows)} messages")

        for row in rows:
            try:
                # payload no longer contains expiration_time
                payload = json.loads(row["payload"])
                whatsapp_token = row["whatsapp_token"]
                phone_number_id = row["phone_number_id"]

                response, status_code = send_template(
                    payload,
                    whatsapp_token,
                    phone_number_id
                )

                if status_code == 200:
                    cursor.execute("""
                        UPDATE whatsapp_messages
                        SET status='sent',
                            sent_time=%s,
                            error=NULL
                        WHERE id=%s
                    """, (datetime.utcnow(), row["id"]))
                    logging.info(f"Message SENT (ID: {row['id']})")
                else:
                    cursor.execute("""
                        UPDATE whatsapp_messages
                        SET status='failed',
                            error=%s,
                            retry_count=retry_count+1
                        WHERE id=%s
                    """, (json.dumps(response), row["id"]))
                    logging.error(f"Message FAILED (ID: {row['id']}): {response}")

            except Exception as e:
                cursor.execute("""
                    UPDATE whatsapp_messages
                    SET status='failed',
                        error=%s,
                        retry_count=retry_count+1
                    WHERE id=%s
                """, (str(e), row["id"]))
                logging.error(f"Exception for ID {row['id']}: {str(e)}")

        conn.commit()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    logging.info("🚀 WhatsApp Worker triggered by Task Scheduler")
    try:
        process_messages()
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
