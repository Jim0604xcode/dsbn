
from src.loggerServices import log_error, log_info
from src.config import ENV
from src.exceptions import GeneralErrorExcpetion
from src.aligreen.client import AliGreenClient
from src.config import ALICLOUD_GREEN_ACCESS_KEY_ID, ALICLOUD_GREEN_ACCESS_KEY_SECRET, ALICLOUD_GREEN_REGION_ID, ALICLOUD_GREEN_ENDPOINT


def _create_aligreen_client():

    
    try:
        # log_info(f"Initializing AliGreen Client for environment: {ENV}")
        client = AliGreenClient(
            access_key_id=ALICLOUD_GREEN_ACCESS_KEY_ID,
            access_key_secret=ALICLOUD_GREEN_ACCESS_KEY_SECRET,
            region_id=ALICLOUD_GREEN_REGION_ID,
            endpoint=ALICLOUD_GREEN_ENDPOINT,
            connect_timeout=1000,
            read_timeout=3000
        )
        return client
    except Exception as e:
        log_error(f"Failed to initialize AliGreen client: {e}")
        log_info("Falling back to Mock AliGreen Client")
        return None


# AliGreen client instance
client = _create_aligreen_client()


def get_aligreen():
    """
    Get AliGreen client instance
    """
    try:
        return client
    except Exception as e:
        log_error(f"Error occurred while getting AliGreen client: {e}")
        raise GeneralErrorExcpetion(details="Failed to get AliGreen client")

