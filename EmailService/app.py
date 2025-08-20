from __future__ import annotations
import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # EmailStr
from mangum import Mangum

# ---- Load ../.env if present ----
try:
    from dotenv import load_dotenv, find_dotenv
    parent_env = Path(__file__).resolve().parent.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env)
    else:
        load_dotenv(find_dotenv())
except Exception:
    pass  # Optional; IAM role or ~/.aws works too

from sns_manager import newsletter

APP_NAME = os.getenv("APP_NAME", "newsletter-api")

app = FastAPI(title=APP_NAME, version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fastaiconsulting-net.github.io",  # Base domain
        "https://fastaiconsulting-net.github.io/",  # With trailing slash
        "https://fastaiconsulting-net.github.io/younews",  # Your specific path
        "https://fastaiconsulting-net.github.io/younews/",  # Your specific path with slash
        # "http://localhost:8000",  # Local development
        # "*"  # Temporarily
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ----- Schemas -----
class SubscriptionBody(BaseModel):
    email: str

class UnsubscriptionBody(BaseModel):
    subscription_arn: str

# ----- Routes -----
@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": APP_NAME}

@app.get("/subscriptions/{email}")
def get_subscription(email: str):
    """Get subscription status for an email address"""
    subscription = newsletter.get_subscription_by_email(email)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@app.post("/subscriptions/subscribe")
def subscribe_route(body: SubscriptionBody):
    """Subscribe an email address (will send confirmation email)"""
    result = newsletter.subscribe(str(body.email))
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/subscriptions/unsubscribe")
def unsubscribe_route(body: UnsubscriptionBody):
    """Unsubscribe using subscription ARN"""
    result = newsletter.unsubscribe(body.subscription_arn)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/subscriptions")
def get_subscriptions():
    """Get all confirmed subscriptions"""
    return {"subscriptions": newsletter.get_subscriptions()}


# ----- Lambda adapter -----
handler = Mangum(app)


def lambda_handler(event, context):
    return handler(event, context)


# ----- Local run -----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)