import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from auth import router as auth_router
from routes import router as app_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(app_router)

if __name__ == "__main__":
    import uvicorn
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    uvicorn.run(app, host="0.0.0.0", port=8000)