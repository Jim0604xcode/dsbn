
import json
from src.config import (ALICLOUD_OSS_ACCESS_KEY_ID, ALICLOUD_OSS_ACCESS_KEY_SECRET,ALICLOUD_OSS_REGION_ID,
    ALICLOUD_OSS_DEEPSOUL_BUCKET_NAME, ALICLOUD_OSS_ENDPOINT, ENV, DKMS_OSS_SECRET, ALICLOUD_OSS_REGION, ALICLOUD_OSS_STS_ROLE_ARN,ALICLOUD_OSS_DEEPSOUL_ACCELERATE_REGION_NAME)
from src.oss.client import OSSClient
from src.loggerServices import log_error    

def get_oss():
    try:

        
        from src.kmsConfig import get_kms
        kms_client = get_kms()
        access_key_id = ALICLOUD_OSS_ACCESS_KEY_ID
        access_key_secret = ALICLOUD_OSS_ACCESS_KEY_SECRET

        if ENV in ("production", "staging"):
            secret_json = kms_client.get_secret_data(DKMS_OSS_SECRET)
            secret = json.loads(secret_json)
            access_key_id = secret['AccessKeyId']
            access_key_secret = secret['AccessKeySecret']

        client = OSSClient(access_key_id, access_key_secret, ALICLOUD_OSS_ENDPOINT, ALICLOUD_OSS_DEEPSOUL_BUCKET_NAME, ALICLOUD_OSS_REGION, ALICLOUD_OSS_STS_ROLE_ARN, ALICLOUD_OSS_DEEPSOUL_ACCELERATE_REGION_NAME,ALICLOUD_OSS_REGION_ID)
        return client
    except Exception as e:
        log_error(f"Error occurred while getting OSS client: {e}")
        

