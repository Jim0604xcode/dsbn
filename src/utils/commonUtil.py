import time

def get_unix_timestamp():
    # e.g: 1739217296
    return int(time.time())

def exclude_fields_from_model(model_obj, exclude_fields=None):
    """
    Convert a SQLAlchemy model to a dictionary excluding specified fields.
    
    Args:
        model_obj: SQLAlchemy model object
        exclude_fields: List of field names to exclude (defaults to ['id'])
    
    Returns:
        Dictionary representation of the model without excluded fields
    """
    
    # Handle case where model_obj is already a dict
    if isinstance(model_obj, dict):
        return {k: v for k, v in model_obj.items() if k not in exclude_fields}
    
    # Handle SQLAlchemy model object
    if hasattr(model_obj, '__table__'):
        return {c.name: getattr(model_obj, c.name) 
                for c in model_obj.__table__.columns 
                if c.name not in exclude_fields}
    
    # Handle any other object with __dict__
    if hasattr(model_obj, '__dict__'):
        result = model_obj.__dict__.copy()
        # Remove SQLAlchemy state management
        if '_sa_instance_state' in result:
            del result['_sa_instance_state']
        # Remove excluded fields
        for field in exclude_fields:
            if field in result:
                del result[field]
        return result
    
    # If none of the above, return the object as is
    return model_obj

def build_post_result(item, post_master, shared_to_list, download_url, user_info, item_key="item", exclude_ai_feedback=False):
    """
    Build a standardized result dictionary for post-related responses.
    Args:
        item: The main item (e.g., life_moment, message, etc.)
        post_master: The post master object
        shared_to_list: List of shared recipients
        download_url: Download URL(s) for media
        user_info: User info (e.g., POST_OWNER_IS_REQUESTER)
        item_key: The key name for the main item (default: "item")
        exclude_ai_feedback: Whether to exclude AI feedback fields (default: False)
    Returns:
        dict: Standardized result dictionary
    """
    exclude_fields = ['id']
    if exclude_ai_feedback:
        exclude_fields.extend(['ai_feedback_content', 'ai_feedback_status', 'ai_feedback_count', 'ai_feedback_hotline', 'ai_feedback_lang'])
    
    return {
        item_key: item,
        "post_master": exclude_fields_from_model(post_master, exclude_fields),
        "shared_to_list": shared_to_list,
        "download_url": download_url,
        "user_info": user_info
    }