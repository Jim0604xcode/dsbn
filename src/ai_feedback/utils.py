from src.posts.models import PostSourceEnum, PostMaster
from .constants import AI_FEEDBACK_MOTION_RATE_THRESHOLD

def get_ai_feedback_capability(post_source: PostSourceEnum, post_master: PostMaster) -> bool:
    """
    Determine if AI feedback can be generated for a given post
    
    Args:
        post_source: The source type of the post
        post_master: The post master object containing motion_rate
    
    Returns:
        Boolean indicating if AI feedback is available for this post
    """

    # print(f"*****Checking AI feedback capability for post_source: {post_source}, motion_rate: {post_master.motion_rate}")
    return (post_source == PostSourceEnum.LIFE_MOMENT and 
            post_master.motion_rate is not None and 
            post_master.motion_rate < AI_FEEDBACK_MOTION_RATE_THRESHOLD)