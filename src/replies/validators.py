from src.exceptions import BadReqExpection

def validate_content(content: str) -> str:
    """Validate reply content"""
    if not content or not content.strip():
        raise BadReqExpection(details="Reply content cannot be empty")
    if len(content) > 1000:
        raise BadReqExpection(details="Reply content cannot exceed 1000 characters")
    return content.strip()

def validate_reply_id(reply_id: int) -> int:
    """Validate reply ID"""
    if reply_id <= 0:
        raise BadReqExpection(details="Invalid reply ID")
    return reply_id