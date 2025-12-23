from base64 import b64encode
from src.exceptions import GeneralErrorExcpetion
import base64
from gql.transport.aiohttp import AIOHTTPTransport
from src.config import AUTHGEAR_ADMIN_API_ENDPOINT
from src.authgear.generateAuthgearJWT import generateAuthgearJWT

def getUserIDWithBase64encoded(authgear_id: str) -> str:
    base64EncodedStr = "User:" + authgear_id
    preparedUserID = base64EncodedStr.encode('utf-8')
    bytes_encode = b64encode(preparedUserID)
    encoded_str = bytes_encode.decode('utf-8').rsplit('=')
    return encoded_str[0]

def getAutherIDByNodeID(node_id: str) -> str:
    # 確保 authgear_id 是有效的字串
        if not node_id or not isinstance(node_id, str):
            raise GeneralErrorExcpetion(f"Invalid authgear_id: {node_id}")
        
        # 確保長度是 4 的倍數，若不是則補充 '='
        node_id = node_id.strip()
        padding_needed = (4 - len(node_id) % 4) % 4
        if padding_needed:
            node_id += '=' * padding_needed
            # 解碼並處理結果
            decoded = base64.b64decode(node_id.encode('utf-8'))    
        else:
            # 解碼並處理結果
            decoded = base64.b64decode(node_id.encode('utf-8'))


        return decoded.split(b"User:")[1].decode('utf-8')
        
def generate_transport():
    return AIOHTTPTransport(
            url=AUTHGEAR_ADMIN_API_ENDPOINT,
            headers={"Authorization": f"Bearer {generateAuthgearJWT()}"}
        )

