import math

def paginate(query, page: int, page_size: int): 
    total_items = query.count()
    total_pages = math.ceil(total_items / page_size)
    offset = max((page - 1) * page_size, 0)
    items = query.offset(offset).limit(page_size).all()
    
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "items": items
    }

def paginated_object_mapping(paginated_result,items):
 return {
        "total_items": paginated_result["total_items"],
        "total_pages": paginated_result["total_pages"],
        "current_page": paginated_result["current_page"],
        "page_size": paginated_result["page_size"],
        "items": items
    }

def build_empty_post_paginated_results(page: int = 1, page_size: int = 10) -> dict:
    return {
        "total_items": 0,
        "total_pages": 0,
        "current_page": page,
        "page_size": page_size,
        "items": []
    }