from sqlalchemy.orm import Session
from src.dashscopeConfig import get_dashscope_client
from src.aligreenConfig import get_aligreen
from src.posts.models import LifeMoment, PostMaster, AIFeedbackStatusEnum, PostSourceEnum
from src.auth.models import UserSettings
from src.exceptions import BadReqExpection
from src.loggerServices import log_info, log_error
from src.ai_feedback.utils import get_ai_feedback_capability
from src.pii.service import mask_text
from src.pii.schemas import MaskRequest
from src.ai_feedback.models import AIFeedbackRequest
from src.ai_feedback.constants import (
    AI_DETECT_LANGUAGE,
    AI_FEEDBACK_ENTITY_TYPES,
    AI_FEEDBACK_PHONE_REGIONS,
    AI_FEEDBACK_MASK_CHAR,
    AI_FEEDBACK_MASK_STYLE,
    AI_FEEDBACK_PRESERVE_LENGTH,
    LANGUAGE_LOCALE_MAPPING,
    AIModelEnum,
    AI_FEEDBACK_SYSTEM_PROMPT,
)
import json

async def generate_ai_feedback(user_id: str, post_id: int, db: Session, user_info=None):
    """
    Generate AI feedback for a life moment post
    
    Args:
        post_id: The ID of the life moment post
        db: Database session
    
    Returns:
        Dict with feedback status and content
    """
    # 1. Get the complete post from life_moment table
    life_moment = db.query(LifeMoment).filter(LifeMoment.id == post_id).first()
    if not life_moment:
        raise BadReqExpection(details="Life moment post not found")
    
    # check if the life moment belongs to the user
    if life_moment.user_id != user_id:
        raise BadReqExpection(details="You do not have permission to access this post")
    
    # Get post content from post_master table
    post_master = db.query(PostMaster).filter(PostMaster.id == life_moment.post_master_id).first()
    if not post_master:
        raise BadReqExpection(details="Post master not found")

    # check if AI feedback is allowed for this post using existing utility
    can_ai_feedback = get_ai_feedback_capability(PostSourceEnum.LIFE_MOMENT, post_master)
    if not can_ai_feedback:
        log_error(f"AI feedback not allowed for post_master ID: {post_master.id}")
        return {
            # "status": "error",
            # "message": "AI feedback not allowed for this post",
            "ai_feedback_status": AIFeedbackStatusEnum.NA
        }

    # get the user_setting language
    user_setting = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    user_language = user_setting.language if user_setting else "en"

    # Update status to allowed
    post_master.ai_feedback_status = AIFeedbackStatusEnum.ALLOWED
    db.commit()
    
    try:
        # 2. Call PII service to mask the post content
        masked_content = await _mask_pii_content(post_master.content, user_language)
    except Exception as e:
        # Update status to ERROR_MASKING if PII masking fails
        post_master.ai_feedback_status = AIFeedbackStatusEnum.ERROR_MASKING
        db.commit()
        return {
            "ai_feedback_content": None,
            "ai_feedback_status": AIFeedbackStatusEnum.ERROR_MASKING
        }
    
    # print(f"***** Masked content: {masked_content}")

    # 3. Prepare AI feedback request
    ai_request = AIFeedbackRequest(
        weather=life_moment.weather,
        participants=life_moment.participants.split(',') if life_moment.participants else None,
        restaurant_name=life_moment.restaurant_name,
        food_name=life_moment.food_name,
        location=life_moment.location,
        nickname=_get_user_nickname(user_info),
        academic_work_interest=life_moment.academic_work_interest,
        school_score=life_moment.school_score,
        motion_rate=float(post_master.motion_rate) if post_master.motion_rate else None,
        content=masked_content,
        title=post_master.title,
        # lang=user_language
    )
    
    try:
        # 4. Call Alibaba Cloud AI service
        ai_feedback = await _call_alibaba_ai_service(
            ai_request, 
            AI_FEEDBACK_SYSTEM_PROMPT, 
            AIModelEnum.QWEN_PLUS_LATEST
        )
    except Exception as e:
        # Update status to ERROR_AI_FEEDBACK if AI service fails
        post_master.ai_feedback_status = AIFeedbackStatusEnum.ERROR_AI_FEEDBACK
        db.commit()
        return {
            # "status": "error",
            # "message": "Failed to generate AI feedback",
            "ai_feedback_content": None,
            "ai_feedback_status": AIFeedbackStatusEnum.ERROR_AI_FEEDBACK
        }
    
    # 5. Parse JSON response and extract feedback, hotline and detected_lang fields
    # Note: as defined in the system prompt, ai_feedback should be in json format with field "feedback", "hotline" and "detected_lang"
    try:
        ai_feedback_json = json.loads(ai_feedback)
        feedback_content = ai_feedback_json.get("feedback", "")
        hotline = bool(ai_feedback_json.get("hotline", False))
        detected_lang = ai_feedback_json.get("detected_lang", "other")
    except (json.JSONDecodeError, KeyError) as e:
        # print(f"Error parsing AI feedback JSON: {str(e)}")
        # print(f"AI feedback raw response: {ai_feedback}")
        post_master.ai_feedback_status = AIFeedbackStatusEnum.ERROR_OTHER
        db.commit()
        return {
            "ai_feedback_content": None,
            "ai_feedback_status": AIFeedbackStatusEnum.ERROR_OTHER.value
        }

    # 6. Safeguard the response
    safeguardPassed = await _safeguard_ai_response(feedback_content)
    if(not safeguardPassed):
        post_master.ai_feedback_status = AIFeedbackStatusEnum.ERROR_SAFEGUARD
        post_master.ai_feedback_content = None
        db.commit()
        return {
            "ai_feedback_content": None,
            "ai_feedback_status": AIFeedbackStatusEnum.ERROR_SAFEGUARD.value
        }
    
    # Store feedback, hotline, detected language and update status
    post_master.ai_feedback_content = feedback_content
    post_master.ai_feedback_hotline = hotline
    post_master.ai_feedback_lang = detected_lang
    post_master.ai_feedback_status = AIFeedbackStatusEnum.COMPLETED
    post_master.ai_feedback_count = (post_master.ai_feedback_count or 0) + 1
    db.commit()
    
    return {
        # "status": "success",
        # "message": "AI feedback generated successfully",
        "ai_feedback_content": feedback_content,
        "ai_feedback_hotline": hotline,
        "ai_feedback_lang": detected_lang,
        "ai_feedback_status": AIFeedbackStatusEnum.COMPLETED.value
    }

async def _mask_pii_content(content: str, user_language: str) -> str:
    """
    Call PII service to mask sensitive information in content
    
    Args:
        content: Original post content
        user_language: User's language setting
    
    Returns:
        Masked content with PII removed/replaced
    """
    locale = AI_DETECT_LANGUAGE
    
    mask_request = MaskRequest(
        text=content,
        locale=locale,
        entity_types=AI_FEEDBACK_ENTITY_TYPES,
        phone_regions=AI_FEEDBACK_PHONE_REGIONS,
        mask_char=AI_FEEDBACK_MASK_CHAR,
        mask_style=AI_FEEDBACK_MASK_STYLE,
        preserve_length=AI_FEEDBACK_PRESERVE_LENGTH
    )
    masked_text, entities = mask_text(mask_request)
    # print(f"***** Masked text preview: {masked_text}")
    #  print the entities for debugging
    # for entity in entities:
    #     print(f"Entity: {entity}")

    return masked_text

async def _call_alibaba_ai_service(ai_request: AIFeedbackRequest, system_prompt: str, model_name: AIModelEnum) -> str:
    """
    Call Alibaba Cloud AI service to generate feedback
    
    Args:
        ai_request: Structured AI feedback request
        system_prompt: System prompt for the AI model
        model_name: AI model to use for generation
    
    Returns:
        AI generated feedback
    """
    # Create OpenAI client for Alibaba Cloud DashScope
    # display the DASHSCOPE_API_KEY for debugging
    client = get_dashscope_client()
    
    # Prepare user prompt as JSON
    user_prompt = {
        "weather": ai_request.weather,
        "participants": ai_request.participants,
        "restaurant_name": ai_request.restaurant_name,
        "food_name": ai_request.food_name,
        "location": ai_request.location,
        "academic_work_interest": ai_request.academic_work_interest,
        "school_score": ai_request.school_score,
        "nickname": ai_request.nickname,
        "motion_rate": ai_request.motion_rate,
        "content": ai_request.content,
        "title": ai_request.title,
        "lang": ai_request.lang
    }

    # Base parameters for all models
    base_params = {
        "model": model_name.value,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)}
        ],
        "stream": False,
        "top_p": 0.8,
        "temperature": 0.7,
    }
    
    # Add model-specific parameters
    if model_name in [AIModelEnum.QWEN_PLUS_LATEST, AIModelEnum.QWEN_FLASH]:
        base_params["extra_body"] = {"thinking_budget": 4000}

    # Call the API
    completion = client.chat.completions.create(**base_params)
    
    # Extract the response
    response_content = completion.choices[0].message.content
    
    return response_content

def _get_user_nickname(user_info) -> str:
    """
    Extract nickname from user_info standard_attributes
    
    Args:
        user_info: TokenPayload object containing user information
    
    Returns:
        User's nickname or None if not available
    """
    if not user_info:
        # print("***** No user_info provided")
        return None
        
    try:
        standard_attributes = user_info.standard_attributes
        
        if isinstance(standard_attributes, dict):
            # Try different possible nickname fields
            nickname = (standard_attributes.get('nickname') or 
                       standard_attributes.get('given_name') or 
                       standard_attributes.get('name'))
            return nickname
        elif hasattr(standard_attributes, 'nickname'):
            nickname = standard_attributes.nickname
            return nickname
        elif hasattr(standard_attributes, 'given_name'):
            nickname = standard_attributes.given_name
            return nickname
    except (AttributeError, TypeError) as e:
        # print(f"***** Error extracting nickname: {e}")
        pass
        
    return None

async def _safeguard_ai_response(ai_response: str) -> str:
    """
    Apply safeguards to AI response to ensure appropriateness
    
    Args:
        ai_response: Raw AI response
    
    Returns:
        Safeguarded AI response
    """
    try:
        aligreen_client = get_aligreen()
        if not aligreen_client:
            log_error("***** AliGreen client not found")
            return False
        result = aligreen_client.check_text_safety(ai_response)
        if result.is_safe:
            # log_info("***** AliGreen result is safe")
            return True
        else:
            # log_info("***** AliGreen result is not safe")
            return False
    except Exception as e:
        log_error(f"***** Error checking text safety: {e}")
        return False