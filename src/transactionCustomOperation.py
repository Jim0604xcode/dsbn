from sqlalchemy.orm import Session
from src.exceptions import GeneralErrorExcpetion
from src.posts.models import PostSharedRecipients, PostsPermissionsGroupMembers, PostUserPermissions
from src.posts.utils import new_post_permission_db_mapping
from src.constants import (TRANSACTION_CUSTOM_OPERATION_CREATE_MUTLI_RECIPIENTS,
    TRANSACTION_CUSTOM_OPERATION_DELETE_SHARED_TO_MEMBER_IN_GROUP,
    TRANSACTION_CUSTOM_OPERATION_REMOVE_ALL_POST_SHARED_TO)
from src.loggerServices import log_error


def handle_custom_operation(operation: dict, db: Session):
    """Handle custom operations that don't fit into the standard ORM pattern"""
    function_name = operation.get("function")
    params = operation.get("params", {})
    
    if function_name == TRANSACTION_CUSTOM_OPERATION_REMOVE_ALL_POST_SHARED_TO:
        # Handle permission deletion including recipients
        shared_post_id = params.get("shared_post_id")
        post_source = params.get("post_source")
        
        # First get all permission records
        permission_records = db.query(PostUserPermissions).filter(
            PostUserPermissions.shared_post_id == shared_post_id,
            PostUserPermissions.post_source == post_source
        ).all()
        
        # Delete recipients for each permission
        for permission in permission_records:
            db.query(PostSharedRecipients).filter(
                PostSharedRecipients.permission_id == permission.id
            ).delete()
        
        # Delete permissions
        db.query(PostUserPermissions).filter(
            PostUserPermissions.shared_post_id == shared_post_id,
            PostUserPermissions.post_source == post_source
        ).delete()
        
        return True
    
    elif function_name == TRANSACTION_CUSTOM_OPERATION_CREATE_MUTLI_RECIPIENTS:
        # Handle permission creation
        share_permission_obj = params.get("share_permission_obj")
        shared_post_id = params.get("shared_post_id")
        user_id = params.get("user_id")
        post_source = params.get("post_source")
        
        new_permission = new_post_permission_db_mapping(
            share_permission_obj, 
            shared_post_id, 
            user_id, 
            post_source
        )
        db.add(new_permission)
        db.flush()  # Ensure the new record is created
        
        return new_permission
    elif function_name == TRANSACTION_CUSTOM_OPERATION_DELETE_SHARED_TO_MEMBER_IN_GROUP:
        return delete_group_members(db, params.get("group_id"))
    else:
        raise GeneralErrorExcpetion(f"Unknown custom function: {function_name}")

def delete_group_members(db: Session, group_id: int):
    """
    Delete all members of a group and their related references
    """
    try:
        # 1. Find all member IDs for the group
        member_ids_query = db.query(PostsPermissionsGroupMembers.id).filter(
            PostsPermissionsGroupMembers.group_id == group_id
        )
        member_ids = [m.id for m in member_ids_query.all()]
        
        # 2. If there are any members, delete their references first
        if member_ids:
            # Find all permission IDs that reference these members
            permission_ids_query = db.query(PostSharedRecipients.permission_id).filter(
                PostSharedRecipients.shared_to.in_(member_ids)
            ).distinct()
            permission_ids = [p.permission_id for p in permission_ids_query.all()]
            
            # Delete all post_shared_recipients entries referring to these members
            db.query(PostSharedRecipients).filter(
                PostSharedRecipients.shared_to.in_(member_ids)
            ).delete(synchronize_session=False)
            
            # 3. Delete the permissions that are now orphaned
            if permission_ids:
                db.query(PostUserPermissions).filter(
                    PostUserPermissions.id.in_(permission_ids)
                ).delete(synchronize_session=False)
        
        # 4. Now delete the members themselves
        result = db.query(PostsPermissionsGroupMembers).filter(
            PostsPermissionsGroupMembers.group_id == group_id
        ).delete(synchronize_session=False)
        
        return result
    except Exception as e:
        log_error(f"Error deleting group members: {str(e)}")
    raise e