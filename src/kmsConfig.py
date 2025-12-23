from src.loggerServices import log_error
from .config import (DKMS_CLIENT_END_POINT, DKMS_CLIENT_KEY_FILE,
    DKMS_CLIENT_KEY_PASSWORD, DKMS_INSTANCE_ID, ENV, DKMS_MASTER_CRYPTO_KEY)
from src.exceptions import GeneralErrorExcpetion
from .kms.client import KMSClient
from .kms.mock_client import MockKMSClient


# Determine which client to use based on environment
def _create_kms_client():
    """Create the appropriate KMS client based on environment and availability."""

    # Use mock client for local development
    if ENV == 'local.Docker' or ENV == 'local':
        # log_info(" Mock KMS Client for local development")
        return MockKMSClient("mock", "mock", "mock","mock")
    
    dkms_client = KMSClient(
        dkms_instance_id=DKMS_INSTANCE_ID,
        client_key_file=DKMS_CLIENT_KEY_FILE,
        client_key_password=DKMS_CLIENT_KEY_PASSWORD,
        dkms_client_end_point=DKMS_CLIENT_END_POINT
    )
    return dkms_client

client = _create_kms_client()

def get_kms():
    try:
        return client
    except Exception as e:
        log_error(f"Error occurred while getting KMS client: {e}")
        raise GeneralErrorExcpetion(details="Failed to get KMS client")

def get_master_crypto_key():
    return DKMS_MASTER_CRYPTO_KEY

def is_mock_kms():
    """Check if we're using the mock KMS client."""
    return isinstance(client, MockKMSClient)
