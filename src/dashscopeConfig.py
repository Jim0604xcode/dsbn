
import json
from src.config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL,DKMS_DASHSCOPE_API_KEY_SECRET
from src.loggerServices import log_error    
from openai import OpenAI
from src.config import ENV

def get_dashscope_client():
    try:
        from src.kmsConfig import get_kms
        kms_client = get_kms()
        api_key = DASHSCOPE_API_KEY
        
        if ENV in ("production", "staging"):
            api_key_secret = kms_client.get_secret_data(DKMS_DASHSCOPE_API_KEY_SECRET)
            if not api_key_secret:
                raise ValueError("secret_json is empty! Please check KMS configuration and permission.")
            # print(f"***** api_key_secret: {api_key_secret}")
            api_key =api_key_secret


        # print(f"***** api_key: {api_key}")
        client = OpenAI(
            # TODO get it from constants now, will change to get it from KMS later
            api_key=api_key,
            base_url=DASHSCOPE_BASE_URL,
        )
        return client

    except Exception as e:
        log_error(f"Error occurred while getting DASHSCOPE client: {e}")
        

