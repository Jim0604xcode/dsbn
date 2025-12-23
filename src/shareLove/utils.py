from src.config import D7NETWORK_API_ULINK_ENDPOINT
from src.authgear.adminApi import query_user_by_authgear_id
from src.auth.models import User
from sqlalchemy.orm import Session
from src.loggerServices import log_info
from src.utils.jwtUtil import create_jwt

async def build_inheritor_ulink(uid: int) -> str:
    """
    Build the ulink for the inheritor
    """
    return f'{D7NETWORK_API_ULINK_ENDPOINT}?af_xp=custom&pid=inheritor_accept&c=DC&af_dp=deepsoul:///?deep_link_value={uid}&af_force_deeplink=true&action=inheritor_accept'

async def get_sender_name_by_user_id(user_id: str, db: Session) -> str:
    """
    Get the sender name by the user id
    Priority use the standardAttributes: family_name + given_name
    If not found, return empty string, let the frontend fallback.
    """
    try:
        row = db.query(User).filter(User.id == user_id).first()
        if not row or not row.authgear_id:
            return ""
        edges = await query_user_by_authgear_id(row.authgear_id)
        if not edges:
            return ""
        node = edges[0]["node"]
        std = node.get("standardAttributes") or {}
        family_name = std.get("family_name") or ""
        given_name = std.get("given_name") or ""
        name = f"{family_name} {given_name}".strip()
        return name
    except Exception as e:
        log_info(f"get_sender_name_by_user_id error: {str(e)}")
        return ""

def create_inheritor_jwt(user_id:str,phone_number:str,uid:int) -> str:
    return create_jwt({'userId':user_id, 'phone':phone_number,'uid':uid},3600 * 24 * 7)  # 7 days duration
