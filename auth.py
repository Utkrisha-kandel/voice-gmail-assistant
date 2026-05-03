import json
import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from gmail import SCOPES

router = APIRouter()
flow_store = {}
user_tokens = {}

def create_flow():
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return flow

@router.get("/login")
async def login():
    flow = create_flow()
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
    user_tokens["default"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
    }
    del flow_store[state]
    return RedirectResponse("/app")

@router.get("/check-auth")
async def check_auth():
    return JSONResponse({"authenticated": "default" in user_tokens})