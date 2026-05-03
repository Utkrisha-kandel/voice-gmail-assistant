import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from gmail import SCOPES

router = APIRouter()
flow_store = {}
user_tokens = {}

REDIRECT_URI = "http://localhost:8000/callback"  # update for production

@router.get("/login")
async def login():
    flow = Flow.from_client_secrets_file("credentials.json", scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
    flow_store[state] = flow
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    state = request.query_params.get("state")
    flow = flow_store.get(state)
    if not flow:
        return JSONResponse({"error": "Session expired. Please login again."}, status_code=400)
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    with open("credentials.json") as f:
        client_info = json.load(f)
    client_info = client_info.get("installed") or client_info.get("web")
    user_tokens["default"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": client_info["client_id"],
        "client_secret": client_info["client_secret"],
    }
    del flow_store[state]
    return RedirectResponse("/app")

@router.get("/check-auth")
async def check_auth():
    return JSONResponse({"authenticated": "default" in user_tokens})