import json
from contextlib import closing
from urllib.request import urlopen
from src.exceptions import GeneralErrorExcpetion
from ..config import AUTHGEAR_ADMIN_PORTAL_ENDPOINT
from jwt import PyJWKClient, decode as jwt_decode
import json
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
    
def parse_header_admin_portal(authz_header):
    parts = authz_header.split(" ")
    if len(parts) != 2:
        return

    scheme = parts[0]
    if scheme.lower() != "bearer":
        return

    return parts[1]

def getJWTUserInfo_admin_portal(token):
    # fetch jwks_uri from the Authgear Discovery Endpoint
    jwks_uri = fetch_jwks_uri(AUTHGEAR_ADMIN_PORTAL_ENDPOINT)
    # Reuse PyJWKClient for better performance
    jwks_client = PyJWKClient(jwks_uri)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    user_info =  jwt_decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=AUTHGEAR_ADMIN_PORTAL_ENDPOINT,
        options={"verify_exp": True},
    )
    return user_info



