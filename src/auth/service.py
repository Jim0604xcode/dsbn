from sqlalchemy.orm import Session
from src.auth.utils import bind_group_members_to_user, extract_full_phone_number, phone_mapping_exists
from src.pushNotification.models import PushNotification
from src.exceptions import GeneralErrorExcpetion
from src.pushNotification.service import notify_user_fd_already_registered
from src.auth.models import PhoneMaster, User, UserSettings
from typing import List, Dict, Any
from src.localCache.localIUserCache import get_users_info_from_cache, set_users_info_to_cache, get_cache_stats
from src.authgear.adminApi import query_users_by_authgear_ids
from src.authgear.utils import getAutherIDByNodeID
from src.transaction import wrap_insert_mapping_func, wrap_update_func
from src.auth.schemas import LanguageBaseInputRequest, UserUpdateMobileInputRequest
from src.loggerServices import log_error, log_info
from src.posts.models import PostsPermissionsGroupMembers
from src.utils.phonenumbers import split_phone_number

def create_user(db: Session,authgear_id: int,device_uuid:str):
    #1. Check if the user already exists
    db_user = db.query(User).filter(User.authgear_id == authgear_id).first()
    if db_user:
        #1b. update push notification update at if any
        # log_info(f'device_uuid={device_uuid},userId={db_user.id}')
        wrap_update_func(PushNotification,{"user_id":db_user.id,"device_uuid":device_uuid},{},db,True)
        db.commit()
        return db_user #2. Return user if the user already exists
    new_user = User(authgear_id=authgear_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    #2. Create default user profile
    language = 'en'
    user_settings = UserSettings(user_id=new_user.id,language=language)
    db.add(user_settings)
    db.commit()
    db.refresh(user_settings)

    
    return new_user

async def get_users_info_with_cache(user_authgear_ids: List[str]) -> Dict[str, Any]:
    # log_info("=== Cache Debug ===")
    # log_info(f"[Service] get_users_info_with_cache: input_ids={user_authgear_ids}")
    cached_users = get_users_info_from_cache(user_authgear_ids) 
    # log_info(f"[Service] get_users_info_with_cache: cached_count={len(cached_users)}")
        
    missing_ids = [uid for uid in user_authgear_ids if uid not in cached_users]
    
    # log_info(f"Input user_authgear_ids: {user_authgear_ids}")
    # log_info(f"Cached users: {cached_users}")
    # log_info(f"Missing IDs: {missing_ids}")
    cache_stats = get_cache_stats()
    # log_info(f"Cache stats: {cache_stats}")
    # log_info(f"Cache size: {len(cache_stats['keys'])}")
    # log_info(f"Cache contents: {dict(zip(cache_stats['keys'], cache_stats['values']))}")
    # 2. Fetch missing from Authgear

    # log_info(f"[Service] get_users_info_with_cache: missing_ids={missing_ids}")

    if missing_ids:
        fresh_users = await query_users_by_authgear_ids(missing_ids)
        fresh_users_dict = {}
        for user in fresh_users:
            try:
                #1. check if the user is empty - deleted account will be
                if not user: continue
                node_id = user.get("id")
                if not node_id: continue
                authgear_id = getAutherIDByNodeID(node_id)
                user['authgear_id'] = authgear_id
                user.pop('id', None)
                fresh_users_dict[authgear_id] = user
            except Exception as e:
                log_error(f"Error processing user: {e}")
                continue
        if fresh_users_dict:
            set_users_info_to_cache(fresh_users_dict)
            cached_users.update(fresh_users_dict)
            cache_stats = get_cache_stats()
            # log_info(f"[Service] After cache update - Cache stats: {cache_stats}")

    return cached_users



async def edit_language_trx(user_id:str,reqBody:LanguageBaseInputRequest, db: Session):
    try:
        updates = reqBody.model_dump(include='language')
        wrap_update_func(UserSettings,{"user_id":user_id},updates,db,True)
        db.commit()
        return True
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))




def do_new_user_after_full_register(new_user_id: str, authgear_new_user_info: dict, db: Session):
    try:
        # 1. get the full phone number from authgear_new_user_info (if not or format is not correct, exit) 
        full_phone_number = extract_full_phone_number(authgear_new_user_info)
        if not full_phone_number:
            return

        # 2. two cases:
        #    - new user: the user_id + phone_number is not in PhoneMaster -> need to create mapping & send notification
        #    - update profile: the user_id + phone_number is already in PhoneMaster ->视为旧用户更新，不再通知
        if phone_mapping_exists(db, new_user_id, full_phone_number):
            return

        # 3. new user fully register: write into PhoneMaster
        insert_obj = PhoneMaster(phone_number=full_phone_number, user_id=new_user_id)
        wrap_insert_mapping_func(db, insert_obj)

        # 4. bind the PostsPermissionsGroupMembers corresponding to the phone to the new user
        members = bind_group_members_to_user(db, new_user_id, full_phone_number)
        if not members:
            return

        db.commit()

        # 5. send notification only when the new user completes the profile for the first time
        member_ids = [m.id for m in members]
        notify_user_fd_already_registered(member_ids, db)
    except Exception as e:
        db.rollback()
        log_error(f"do_new_user_after_full_register error: {str(e)}")

async def update_user_mobile_trx(reqBody: UserUpdateMobileInputRequest, db: Session):
    try:    
        old_phone_number = f"{reqBody.model_dump().get('old_phone_number')}"
        new_phone_number = f"{reqBody.model_dump().get('new_phone_number')}"
        wrap_update_func(PhoneMaster,{"phone_number":old_phone_number},{"phone_number":new_phone_number},db,db.query(PhoneMaster).filter(PhoneMaster.phone_number == old_phone_number).count() > 0)
        o_area_code, split_old_phone_number = split_phone_number(f'{old_phone_number}')
        n_area_code, split_new_phone_number = split_phone_number(f'{new_phone_number}')
        wrap_update_func(PostsPermissionsGroupMembers,{"phone_number":split_old_phone_number},{"phone_number":split_new_phone_number},db,db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.phone_number == split_old_phone_number).count() > 0)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        log_error(f"updateUserMobile: {e}")
        raise GeneralErrorExcpetion(str(e)) 
