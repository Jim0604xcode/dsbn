import json
from contextlib import closing
from urllib.request import urlopen
from src.exceptions import GeneralErrorExcpetion
from ..config import AUTHGEAR_ENDPOINT
from jwt import PyJWKClient, PyJWTError, decode as jwt_decode
import hmac
import hashlib
import json
import time
from typing import TypedDict
from src.exceptions import BadReqExpection
from src.config import SIGNATURE_SECRET
import base64
def fetch_jwks_uri(base_address):
    doc_url = base_address + "/.well-known/openid-configuration"
    try:
        with closing(urlopen(doc_url)) as f:
            doc = json.load(f)
        jwks_uri = doc["jwks_uri"]
        if not jwks_uri:
            raise GeneralErrorExcpetion( details='Failed to fetch jwks uri.')
        return jwks_uri
    except Exception as e:
        raise GeneralErrorExcpetion( details='Failed to fetch jwks uri. Error: '+str(e))
    
def parse_header(authz_header):
    parts = authz_header.split(" ")
    if len(parts) != 2:
        return

    scheme = parts[0]
    if scheme.lower() != "bearer":
        return

    return parts[1]

def getJWTUserInfo(token):
    # fetch jwks_uri from the Authgear Discovery Endpoint
    jwks_uri = fetch_jwks_uri(AUTHGEAR_ENDPOINT)
    # Reuse PyJWKClient for better performance
    jwks_client = PyJWKClient(jwks_uri)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    user_info =  jwt_decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=AUTHGEAR_ENDPOINT,
        options={"verify_exp": True},
    )
    return user_info

def decode_apple_jwt(token: str) -> dict:

    return jwt_decode(token, options={"verify_signature": False, "verify_aud": False, "verify_iss": False})


# Define JWT structure
class JWT(TypedDict):
    usersId: str
    inheritor_user_id: str
    exp: int

def base64_encode_hook(text: str) -> str:
    """Encode string to base64 URL-safe format"""
    # Convert string to bytes and encode to base64
    encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # Replace URL-unsafe characters
    encoded = encoded.replace('+', '-')
    encoded = encoded.replace('/', '_')
    encoded = encoded.replace('=', '')
    return encoded

def base64_decode(text: str) -> str:
    """Decode base64 URL-safe string"""
    # Add padding if needed
    text += '=' * (4 - len(text) % 4 if len(text) % 4 else 0)
    # Replace URL-safe characters back to standard base64
    text = text.replace('-', '+')
    text = text.replace('_', '/')
    return base64.b64decode(text).decode('utf-8')

def create_jwt(obj:dict, duration: int) -> str:
    """Create a JWT token"""
    # Create header
    header = json.dumps({
        'typ': 'JWT',
        'alg': 'HS384'
    })
    
    # Calculate expiration time
    now = int(time.time())
    exp = now + duration
    merged_dict = {**obj,**{'exp':exp}}
    # Create payload
    payload = json.dumps(merged_dict)
    
    # Encode header and payload
    base64_url_header = base64_encode_hook(header)
    base64_url_payload = base64_encode_hook(payload)
    
    # Create signature
    message = f"{base64_url_header}.{base64_url_payload}"
    signature = hmac.new(
        SIGNATURE_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha384
    ).digest()
    base64_url_signature = base64_encode_hook(signature.decode('latin-1'))
    
    # Combine all parts
    jwt = f"{base64_url_header}.{base64_url_payload}.{base64_url_signature}"
    return jwt

def verify_jwt(jwt: str) -> JWT:
    """Verify a JWT token and return its payload"""
    try:
        # Split token into parts
        token_parts = jwt.split('.')
        if len(token_parts) != 3:
            raise BadReqExpection(details="Invalid JWT format")
            
        header = base64_decode(token_parts[0])
        payload = base64_decode(token_parts[1])
        signature_provided = token_parts[2]
        
        # Check expiration
        payload_dict = json.loads(payload)
        now = int(time.time())
        if now > payload_dict['exp']:
            raise BadReqExpection(details="Token is expired")
        
        # Verify signature
        base64_url_header = base64_encode_hook(header)
        base64_url_payload = base64_encode_hook(payload)
        message = f"{base64_url_header}.{base64_url_payload}"
        
        signature = hmac.new(
            SIGNATURE_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).digest()
        base64_url_signature = base64_encode_hook(signature.decode('latin-1'))
        
        if base64_url_signature != signature_provided:
            raise BadReqExpection(details="Signature does not match")
            
        return payload_dict
        
    except Exception as e:
        raise BadReqExpection(details=f"Token verification failed: {str(e)}")