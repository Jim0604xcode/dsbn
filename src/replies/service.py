from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from src.replies.models import RepliesMaster
from src.posts.models import (PostUserPermissions, PostSharedRecipients, PostsPermissionsGroupMembers, PostMaster, 
                             PostSourceEnum, LifeMoment, LifeTrajectory, MessageToYou)
from src.exceptions import BadReqExpection
from src.transaction import wrap_insert_mapping_func
from src.loggerServices import log_error
from src.exceptions import GeneralErrorExcpetion
from src.pushNotification.service import send_push_by_create_reply
from src.auth.service import get_users_info_with_cache
from src.auth.models import User

async def create_reply(post_source: PostSourceEnum, shared_post_id: int, user_id: str, content: str, parent_reply_master_id: int = None, db: Session = None):
    """
    Create a reply to a post
    
    Args:
        post_source: The source type of the post (LIFE_MOMENT, LIFE_TRAJECTORY, MESSAGE_TO_YOU)
        shared_post_id: The ID of the shared post
        user_id: The ID of the user creating the reply
        content: The reply content
        parent_reply_master_id: Optional reply ID for nested replies
        db: Database session
    
    Returns:
        The created reply object
    """
    # Get the post_master_id from the specific post table
    if post_source == PostSourceEnum.LIFE_MOMENT:
        post = db.query(LifeMoment).filter(LifeMoment.id == shared_post_id).first()
    elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
        post = db.query(LifeTrajectory).filter(LifeTrajectory.id == shared_post_id).first()
    elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
        post = db.query(MessageToYou).filter(MessageToYou.id == shared_post_id).first()
    else:
        raise BadReqExpection(details="Invalid post source")
    
    if not post:
        raise BadReqExpection(details="Post not found")
    
    post_master_id = post.post_master_id
    
    # Check if user is post owner or has permission to reply
    is_owner = str(post.user_id) == user_id
    
    if not is_owner:
        permission_exists = db.query(PostUserPermissions).join(
            PostSharedRecipients, PostUserPermissions.id == PostSharedRecipients.permission_id
        ).join(
            PostsPermissionsGroupMembers, PostSharedRecipients.shared_to == PostsPermissionsGroupMembers.id
        ).filter(
            PostUserPermissions.shared_post_id == shared_post_id,
            PostUserPermissions.post_source == post_source,
            PostsPermissionsGroupMembers.user_id == user_id
        ).first()
        
        if not permission_exists:
            raise BadReqExpection(details="You don't have permission to reply to this post")
    
    # 2. If reply_master_id is provided, ensure it exists and belongs to the same post
    if parent_reply_master_id:
        parent_reply = db.query(RepliesMaster).filter(
            RepliesMaster.id == parent_reply_master_id,
            RepliesMaster.post_master_id == post_master_id,
            RepliesMaster.is_deleted == False
        ).first()
        
        if not parent_reply:
            raise BadReqExpection(details="Parent reply not found or doesn't belong to this post")
    
    # 3. Insert into replies_master
    reply_data = RepliesMaster(
        post_master_id=post_master_id,
        user_id=user_id,
        parent_reply_master_id=parent_reply_master_id,
        content=content,
        is_deleted=False
    )
    
    try:
        result = wrap_insert_mapping_func(db, reply_data)
        db.commit()
    except Exception as e:
        db.rollback()
        log_error(f"create reply: {e}")
        raise GeneralErrorExcpetion(str(e)) 
    
    # Send push notification for reply
    # Check if replying to own message - if so, don't send notification
    """
    [20251102] commented out to allow notification even when replying to own post
    should_send_notification = True
    if parent_reply_master_id:
        parent_reply = db.query(RepliesMaster).filter(RepliesMaster.id == parent_reply_master_id).first()
        if parent_reply and parent_reply.user_id == user_id:
            should_send_notification = False
    
    if should_send_notification:
        await send_push_by_create_reply(result[0]["id"], post_source, shared_post_id, user_id, db, parent_reply_master_id)
    """
    try:
        await send_push_by_create_reply(result.id, post_source, shared_post_id, user_id, db, parent_reply_master_id)
    except Exception as e:
        # Log error but don't fail the reply creation
        from src.loggerServices import log_error
        log_error(f"Error sending reply push notification: {str(e)}")
    
    # Convert SQLAlchemy object to dictionary for API response
    return {
        "reply_master_id": result.id,
        "post_master_id": result.post_master_id,
        "user_id": result.user_id,
        "parent_reply_master_id": result.parent_reply_master_id,
        "content": result.content,
        "is_deleted": result.is_deleted,
        "created_at": result.created_at,
    }

def delete_reply(reply_master_id: int, user_id: str, db: Session):
    """
    Delete a reply by marking it as deleted and clearing content
    
    Args:
        reply_master_id: The ID of the reply to delete
        user_id: The ID of the user requesting deletion
        db: Database session
    
    Returns:
        Success message
    """
    try:    
        # Check if reply exists and belongs to user
        reply = db.query(RepliesMaster).filter(
            RepliesMaster.id == reply_master_id,
            RepliesMaster.user_id == user_id,
            RepliesMaster.is_deleted == False
        ).first()
        
        if not reply:
            raise BadReqExpection(details="Reply not found or you don't have permission to delete it")
        
        # Mark as deleted and clear content
        reply.is_deleted = True
        reply.content = ""
        
        db.commit()
        return {"message": "Reply deleted successfully"}
    except Exception as e:
        db.rollback()
        log_error(f"delete_reply: {e}")
        raise GeneralErrorExcpetion(str(e)) 

def edit_reply(reply_master_id: int, content: str, user_id: str, db: Session):
    """
    Edit a reply's content
    
    Args:
        reply_master_id: The ID of the reply to edit
        content: The new content for the reply
        user_id: The ID of the user requesting the edit
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Check if reply exists and belongs to user
        reply = db.query(RepliesMaster).filter(
            RepliesMaster.id == reply_master_id,
            RepliesMaster.user_id == user_id
        ).first()
        
        if not reply:
            raise BadReqExpection(details="Reply not found or you don't have permission to edit it")
        
        if reply.is_deleted:
            raise BadReqExpection(details="Cannot edit a deleted reply")
        
        # Update content
        reply.content = content
        
        db.commit()
        return {"message": "Reply updated successfully"}
    except Exception as e:
        db.rollback()
        log_error(f"update reply: {e}")
        raise GeneralErrorExcpetion(str(e)) 

async def get_replies_only(post_source: PostSourceEnum, shared_post_id: int, user_id: str, db: Session):
    """
    Get only replies for a post, without the post data, do not return the deleted reply
    
    Args:
        post_source: The source type of the post (LIFE_MOMENT, LIFE_TRAJECTORY, MESSAGE_TO_YOU)
        shared_post_id: The ID of the shared post
        user_id: The ID of the requesting user
        db: Database session
    
    Returns:
        Dict containing only replies with user info
    """

    # Get the post first to check ownership
    if post_source == PostSourceEnum.LIFE_MOMENT:
        post = db.query(LifeMoment).filter(LifeMoment.id == shared_post_id).first()
    elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
        post = db.query(LifeTrajectory).filter(LifeTrajectory.id == shared_post_id).first()
    elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
        post = db.query(MessageToYou).filter(MessageToYou.id == shared_post_id).first()
    else:
        raise BadReqExpection(details="Invalid post source")
    
    if not post:
        raise BadReqExpection(details="Post not found")
    
    # Check if user is the post owner (user_id is in the specific post table, not PostMaster)
    is_owner = post.user_id == user_id
    
    # If not owner, check if this post is shared to this user
    if not is_owner:
        permission_exists = db.query(PostUserPermissions).join(
            PostSharedRecipients, PostUserPermissions.id == PostSharedRecipients.permission_id
        ).join(
            PostsPermissionsGroupMembers, PostSharedRecipients.shared_to == PostsPermissionsGroupMembers.id
        ).filter(
            PostUserPermissions.shared_post_id == shared_post_id,
            PostUserPermissions.post_source == post_source,
            PostsPermissionsGroupMembers.user_id == user_id
        ).first()
        
        if not permission_exists:
            raise BadReqExpection(details="You don't have permission to view replies for this post")
    
    post_master_id = post.post_master_id
    
    # Get all replies for this post
    replies = db.query(RepliesMaster).filter(
        RepliesMaster.post_master_id == post_master_id
    ).order_by(RepliesMaster.created_at).all()
    
    # Build reply tree structure
    reply_dict = {}
    root_replies = []
    
    for reply in replies:
        reply_data = {
            "reply_master_id": reply.id,
            "user_id": reply.user_id,
            "content": reply.content,
            "created_at": reply.created_at,
            "is_deleted": reply.is_deleted,
            "parent_reply_master_id": reply.parent_reply_master_id,
            "children": []
        }
        reply_dict[reply.id] = reply_data
        
        if reply.parent_reply_master_id is None:
            root_replies.append(reply_data)
        else:
            if reply.parent_reply_master_id in reply_dict:
                reply_dict[reply.parent_reply_master_id]["children"].append(reply_data)
    
    # Filter out deleted replies from the tree while preserving chain
    def filter_deleted_replies(replies_list):
        filtered = []
        for reply in replies_list:
            if not reply["is_deleted"]:
                reply["children"] = filter_deleted_replies(reply["children"])
                filtered.append(reply)
            else:
                # If reply is deleted, move its children up to this level
                filtered.extend(filter_deleted_replies(reply["children"]))
        return filtered
    
    root_replies = filter_deleted_replies(root_replies)
    
    # If user is not owner, cut the chain that involve neither the current user nor the post owner
    if not is_owner:
        def cut_chain_at_other_users(replies_list):
            filtered = []
            for reply in replies_list:
                if reply["user_id"] == user_id or reply["user_id"] == post.user_id:
                    # Keep this reply and continue processing children
                    reply["children"] = cut_chain_at_other_users(reply["children"])
                    filtered.append(reply)
                else:
                    # Cut the chain here - don't include this reply or its children
                    pass
            return filtered
        
        root_replies = cut_chain_at_other_users(root_replies)


    # Get user info for all repliers
    user_ids = list(set([reply.user_id for reply in replies]))
    user_objs = db.query(User).filter(User.id.in_(user_ids)).all()
    user_id_to_authgear_id = {str(user.id): user.authgear_id for user in user_objs if user.authgear_id}
    authgear_ids = list(user_id_to_authgear_id.values())
    
    replier_info = {}
    if authgear_ids:
        users_info = await get_users_info_with_cache(authgear_ids)
        for user_id_str, authgear_id in user_id_to_authgear_id.items():
            if authgear_id and authgear_id not in users_info:
                # Handle deleted account
                replier_info[user_id_str] = {
                    "first_name": "Deleted",
                    "last_name": "Account",
                    "picture": ""
                }
            elif authgear_id in users_info:
                user_info = users_info[authgear_id]
                standard_attrs = user_info.get("standardAttributes", {})
                replier_info[user_id_str] = {
                    "first_name": standard_attrs.get("given_name", ""),
                    "last_name": standard_attrs.get("family_name", ""),
                    "picture": standard_attrs.get("picture", "")
                }
    
    return {
        "replies": root_replies,
        "replier_info": replier_info
    }

