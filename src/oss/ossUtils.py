from ..utils.commonUtil import get_unix_timestamp

def get_object_name(user_id: str,file_type:str,file_name: str,action_type:str) -> str:
    """
    Generate a user structure object name for the file.
    e.g
    user_id/pass_away/video/xxxxxx.MP4
    {user_id}/{Action_type}/{file_type}/{get_unix_timestamp()}{file_name}
    """
    file_path = f"{user_id}/{action_type}/{file_type}/"
    file_name = f"{get_unix_timestamp()}{file_name}"
    
    return file_path + file_name