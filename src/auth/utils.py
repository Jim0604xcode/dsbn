from sqlalchemy.orm import Session
from src.auth.models import PhoneMaster
from typing import List, Optional
from src.posts.models import PostsPermissionsGroupMembers
from sqlalchemy import func, cast, String

def extract_full_phone_number(authgear_new_user_info: dict) -> Optional[str]:
    """
    extract the full phone number (with +) from the user info returned by Authgear.
    """
    user_info = authgear_new_user_info.get('updateUser', {}).get('user', {})
    std_attrs = user_info.get('standardAttributes', {})
    phone = std_attrs.get('phone_number')
    if phone and phone.startswith('+'):
        return phone
    return None


def phone_mapping_exists(db: Session, user_id: str, full_phone_number: str) -> bool:
    """
    check if the phone_number is already in PhoneMaster.
    used to distinguish between "new user fully register" and "old user update profile".
    """
    existed = (
        db.query(PhoneMaster)
        .filter(
            PhoneMaster.user_id == user_id,
            PhoneMaster.phone_number == full_phone_number,
        )
        .first()
    )
    return existed is not None


def bind_group_members_to_user(
    db: Session, new_user_id: str, full_phone_number: str
) -> List[PostsPermissionsGroupMembers]:
    """
    bind the PostsPermissionsGroupMembers corresponding to the phone to the new user.
    only responsible for adjusting member.user_id, not commit.
    """
    members = (
        db.query(PostsPermissionsGroupMembers)
        .filter(
            func.concat(
                '+',
                cast(PostsPermissionsGroupMembers.phone_number_prefix, String),
                cast(PostsPermissionsGroupMembers.phone_number, String),
            )
            == full_phone_number
        )
        .all()
    )
    if not members:
        return []

    for member in members:
        member.user_id = new_user_id
        db.add(member)

    return members