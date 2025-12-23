import sys
from cachetools import TTLCache
from typing import Any, Dict, List, Optional
from src.loggerServices import log_error

# Global TTLCache instance for user info
user_info_cache: TTLCache = TTLCache(maxsize=10000, ttl=900)

def get_user_info_from_cache(user_id: str) -> Optional[Any]:
    try:
        result = user_info_cache.get(user_id)
        # log_info(f"[Cache] get_user_info_from_cache: user_id={user_id}, hit={result is not None}, cache_size={len(user_info_cache)}")
        return result
    except Exception as e:
        log_error(f"Error getting user info from cache: {e}")
        return None

def set_user_info_to_cache(user_id: str, user_info: Any):
    try:
        size = sys.getsizeof(user_info)
        # log_info(f"[Cache] set_user_info_to_cache: user_id={user_id}, size={size}, cache_size={len(user_info_cache)}")
        user_info_cache[user_id] = user_info
    except Exception as e:
        log_error(f"Error setting user info to cache: {e}")

def get_users_info_from_cache(user_ids: List[str]) -> Dict[str, Any]:
    try:
        result = {uid: user_info_cache[uid] for uid in user_ids if uid in user_info_cache}
        # log_info(f"[Cache] get_users_info_from_cache: user_ids={user_ids}, hit_count={len(result)}, cache_size={len(user_info_cache)}")
        return result
    except Exception as e:
        log_error(f"Error getting users info from cache: {e}")
        return {}

def set_users_info_to_cache(user_infos: Dict[str, Any]):
    try:
        for uid, info in user_infos.items():
            size = sys.getsizeof(info)
            # log_info(f"[Cache] set_users_info_to_cache: user_id={uid}, size={size}, cache_size={len(user_info_cache)}")
            user_info_cache[uid] = info
    except Exception as e:
        log_error(f"Error setting users info to cache: {e}")

def get_cache_stats() -> Dict[str, Any]:
    """Get current cache statistics"""
    try:
        return {
            'size': len(user_info_cache),
            'keys': list(user_info_cache.keys()),
            'values': list(user_info_cache.values())
        }
    except Exception as e:
        log_error(f"Error getting cache stats: {e}")
        return {'size': 0, 'keys': [], 'values': []}