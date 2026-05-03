import base64
import email.mime.text
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]

def get_gmail_service(token_data: dict):
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=SCOPES,
    )
    return build("gmail", "v1", credentials=creds)

def extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            result = extract_body(part)
            if result:
                return result
    data = payload.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return ""

def read_emails(token_data: dict, max_results: int = 5):
    service = get_gmail_service(token_data)
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        headers = full_msg["payload"]["headers"]
        emails.append({
            "subject": next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject"),
            "from": next((h["value"] for h in headers if h["name"] == "From"), "Unknown"),
            "date": next((h["value"] for h in headers if h["name"] == "Date"), "Unknown"),
            "body": extract_body(full_msg["payload"])[:500],
        })
    return emails

def send_email_fn(token_data: dict, to: str, subject: str, body: str):
    service = get_gmail_service(token_data)
    message = email.mime.text.MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    try:
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return "sent"
    except Exception as e:
        return f"error: {str(e)}"