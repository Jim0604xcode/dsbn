from sqlalchemy.orm import Session
from src.replies.models import RepliesMaster
from src.posts.models import PostUserPermissions, PostSharedRecipients, PostsPermissionsGroupMembers, PostSourceEnum
from src.exceptions import BadReqExpection

def check_reply_permission(post_source: PostSourceEnum, shared_post_id: int, user_id: str, db: Session) -> bool:
    """
    Check if user has permission to reply to a post
    
    Args:
        post_source: The source type of the post
        shared_post_id: The ID of the shared post
        user_id: The ID of the user
        db: Database session
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    permission_exists = db.query(PostUserPermissions).join(
        PostSharedRecipients, PostUserPermissions.id == PostSharedRecipients.permission_id
    ).join(
        PostsPermissionsGroupMembers, PostSharedRecipients.shared_to == PostsPermissionsGroupMembers.id
    ).filter(
        PostUserPermissions.shared_post_id == shared_post_id,
        PostUserPermissions.post_source == post_source,
        PostsPermissionsGroupMembers.user_id == user_id
    ).first()
    
    return permission_exists is not None

def validate_parent_reply(parent_reply_id: int, post_master_id: int, db: Session) -> RepliesMaster:
    """
    Validate that parent reply exists and belongs to the same post
    
    Args:
        parent_reply_id: The ID of the parent reply
        post_master_id: The ID of the post master
        db: Database session
    
    Returns:
        RepliesMaster: The parent reply object
    
    Raises:
        BadReqExpection: If parent reply is not found or doesn't belong to the post
    """
    parent_reply = db.query(RepliesMaster).filter(
        RepliesMaster.id == parent_reply_id,
        RepliesMaster.post_master_id == post_master_id,
        RepliesMaster.is_deleted == False
    ).first()
    
    if not parent_reply:
        raise BadReqExpection(details="Parent reply not found or doesn't belong to this post")
    
    return parent_reply