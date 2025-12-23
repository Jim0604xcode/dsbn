import jwt
from datetime import datetime, timedelta
from src.config import AUTHGEAR_ADMIN_API_KEY_PATH,AUTHGEAR_PROJECT_ID,AUTHGEAR_KEY_ID
from zoneinfo import ZoneInfo

def generateAuthgearJWT():
    private_key = open(AUTHGEAR_ADMIN_API_KEY_PATH, "r").read()

    # Replace "myapp" with your project ID here. 
    # It is the first part of your Authgear endpoint. 
    # e.g. The project ID is "myapp" for "https://myapp.authgear.cloud"
    PROJECT_ID = AUTHGEAR_PROJECT_ID

    # Replace "mykid" with the key ID you see in the portal.
    KEY_ID = AUTHGEAR_KEY_ID

    now = datetime.now(ZoneInfo("Asia/Hong_Kong"))

    payload = {
        "aud": [PROJECT_ID],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }

    token = jwt.encode(
        payload,
        private_key,
        "RS256",
        headers={
            "kid": KEY_ID,
        },
    )

    return token