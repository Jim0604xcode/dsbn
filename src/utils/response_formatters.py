"""
Shared response formatting utilities
"""
from src.posts.response import LifeMomentResponseModel, LifeTrajectoryResponseModel, MessageToYouResponseModel, SharedLifeMomentResponseModel, SharedLifeTrajectoryResponseModel
from src.utils.pagination import paginated_object_mapping

def format_life_moments_response(paginated_results):
    """
    Format life moments data into a standardized response format
    
    Args:
        paginated_results
        
    """
    response_items = [LifeMomentResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "total_replies": result.get("total_replies", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in paginated_results["items"]]
    
    return paginated_object_mapping(paginated_results, response_items)

def format_shared_life_moments_response(paginated_results):
    """
    Format life moments data into a standardized response format
    
    Args:
        paginated_results
        
    """
    response_items = [LifeMomentResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "shared_replies_count": result.get("shared_replies_count", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in paginated_results["items"]]
    
    return paginated_object_mapping(paginated_results, response_items)


def format_shared_life_experiences_paginated_response(paginated_results):
    """
    Formatter for /get/shared_with_me/life_experiences paginated response,
    handling mixed list of LifeMoment and LifeTrajectory.
    """
    response_items = []
    for result in paginated_results["items"]:
        item_obj = result["item"]
        item_dict = getattr(item_obj, "__dict__", {}).copy()
        # Remove SQLAlchemy internal fields
        item_dict.pop("_sa_instance_state", None)

        base_payload = {
            **item_dict,
            **result["post_master"],
            "shared_to_list": result["shared_to_list"],
            "shared_replies_count": result.get("shared_replies_count", 0),
            **result["download_url"],
            "postOwner": result["user_info"],
            "is_life_moment": result.get("is_life_moment", False),
            "is_life_trajectory": result.get("is_life_trajectory", False),
        }

        if result.get("is_life_trajectory"):
            response_items.append(
                SharedLifeTrajectoryResponseModel.model_validate(base_payload)
            )
        else:
            # Default to life moment
            response_items.append(
                SharedLifeMomentResponseModel.model_validate(base_payload)
            )
    # print(response_items)
    return paginated_object_mapping(paginated_results, response_items)

def format_life_trajectories_response(paginated_results):
    """
 
    Format life trajectories data into a standardized response format
    
    Args:
        paginated_results

    """
    response_items = [LifeTrajectoryResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "total_replies": result.get("total_replies", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in paginated_results["items"]]
    
    return paginated_object_mapping(paginated_results, response_items)

def format_messages_response(paginated_results):
    """
 
    Format messages data into a standardized response format
    
    Args:
        paginated_results
        
    """
    response_items = [MessageToYouResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "total_replies": result.get("total_replies", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in paginated_results["items"]]
    
    return paginated_object_mapping(paginated_results, response_items) 

def format_shared_messages_response(paginated_results):
    """
 
    Format messages data into a standardized response format
    
    Args:
        paginated_results
        
    """
    response_items = [MessageToYouResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "shared_replies_count": result.get("shared_replies_count", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in paginated_results["items"]]
    
    return paginated_object_mapping(paginated_results, response_items) 

def format_my_life_moment_items(items):
    """
    Format my life moments data into a standardized response format
    total_replies is the total replies count for the life moment
    Args:
        paginated_results
        
    """
    response_items = [LifeMomentResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "total_replies": result.get("total_replies", 0),
        **result["download_url"],
        "postOwner": result["user_info"],
    }) for result in items]
    
    return response_items

def format_shared_life_moment_items(items):
    """
    Format shared life moments data into a standardized response format
    shared_replies_count is the number of replies between the post owner and the current user

    Args:
        paginated_results
        
    """
    response_items = [LifeMomentResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "shared_replies_count": result.get("shared_replies_count", 0),
        **result["download_url"],
        "postOwner": result["user_info"],
    }) for result in items]
    
    return response_items

def format_shared_life_trajectory_items(items):
    """
    Format shared life trajectorys data into a standardized response format
    shared_replies_count is the number of replies between the post owner and the current user

    Args:
        paginated_results
        
    """
    response_items = [LifeTrajectoryResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "shared_replies_count": result.get("shared_replies_count", 0),
        **result["download_url"],
        "postOwner": result["user_info"],
    }) for result in items]
    
    return response_items


def format_shared_life_experiences_items(items):
    """
    專門給首頁用的「sharedLifeExperiences」格式化函式。
    items 來源為 get_shared_life_experiences，內含 LifeMoment 與 LifeTrajectory 混合，
    這裡不再套用 Pydantic 模型，直接組裝為可 JSON 序列化的 dict，避免類型驗證錯誤。
    """
    formatted_items = []
    for result in items:
        item_obj = result["item"]
        item_dict = getattr(item_obj, "__dict__", {}).copy()
        # 移除 SQLAlchemy 內部欄位
        item_dict.pop("_sa_instance_state", None)

        formatted_items.append({
            **item_dict,
            **result["post_master"],
            "shared_to_list": result["shared_to_list"],
            "shared_replies_count": result.get("shared_replies_count", 0),
            **result["download_url"],
            "is_life_moment": result.get("is_life_moment", False),
            "is_life_trajectory": result.get("is_life_trajectory", False),
            "postOwner": result["user_info"],
        })

    return formatted_items

def format_message_items(items):
    """
 
    Format messages data into a standardized response format
    
    Args:
        paginated_results
        
    """
    response_items = [MessageToYouResponseModel.model_validate({
        **result["item"].__dict__,
        **result["post_master"],
        "shared_to_list": result["shared_to_list"],
        "shared_replies_count": result.get("shared_replies_count", 0),
        **result["download_url"],
        "postOwner": result["user_info"]
    }) for result in items]
    
    return response_items