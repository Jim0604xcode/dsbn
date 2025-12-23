from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def infer_time_dimension(time_points):
    if len(time_points) < 2:
        return 'day'  
    delta = (time_points[1] - time_points[0]).days
    if delta >= 365:
        return 'year'
    elif delta >= 28:
        return 'month'
    else:
        return 'day'

def find_time_index(date, time_points):

    time_dimension = infer_time_dimension(time_points)
    if time_dimension in ['day', 'week']:
        days_diff = (date - time_points[0]).days
        return max(0, min(len(time_points) - 1, days_diff))
    elif time_dimension == 'month':
        for i, tp in enumerate(time_points):
            if date.year == tp.year and date.month == tp.month:
                return i
        closest_index = 0
        min_diff = float('inf')
        for i, tp in enumerate(time_points):
            year_diff = abs(date.year - tp.year) * 12
            month_diff = abs(date.month - tp.month)
            total_diff = year_diff + month_diff
            if total_diff < min_diff:
                min_diff = total_diff
                closest_index = i
        return closest_index
    elif time_dimension == 'year':
        for i, tp in enumerate(time_points):
            if date.year == tp.year:
                return i
        closest_index = 0
        min_diff = float('inf')
        for i, tp in enumerate(time_points):
            diff = abs(date.year - tp.year)
            if diff < min_diff:
                min_diff = diff
                closest_index = i
        return closest_index
    return 0

def group_mood_data_by_time(mood_data, time_points):

    time_dimension = infer_time_dimension(time_points)

    timeline_data = []
    for i, time_point in enumerate(time_points):
   
        if time_dimension == 'day' or time_dimension == 'week':
            formatted_date = time_point.strftime("%Y-%m-%d")
        elif time_dimension == 'month':
            formatted_date = time_point.strftime("%Y-%m")
        else:  
            formatted_date = time_point.strftime("%Y")
        
        timeline_data.append({
            "time_index": i,
            "time_point": formatted_date,
            "average_mood": 0,
            "post_count": 0,
            "data_points": []
        })
    
    for life_moment, post_master in mood_data:
        date = post_master.start_date.date()
        time_index = find_time_index(date, time_points)
        
        if time_index < 0 or time_index >= len(timeline_data):

            continue
            
        mood_value = float(post_master.motion_rate) if post_master.motion_rate else 0
        rounded_mood = round(mood_value)
        
        existing_mood = None
        for point in timeline_data[time_index]["data_points"]:
            if point["mood_value"] == rounded_mood:
                existing_mood = point
                break
        
        if existing_mood:
            existing_mood["post_count"] += 1
            existing_mood["post_ids"].append(life_moment.id)
        else:
            timeline_data[time_index]["data_points"].append({
                "mood_value": rounded_mood,
                "post_count": 1,
                "post_ids": [life_moment.id]
            })
        
        timeline_data[time_index]["post_count"] += 1
    
    for time_point in timeline_data:
        if time_point["data_points"]:
            total_mood = sum(point["mood_value"] * point["post_count"] for point in time_point["data_points"])
            total_posts = sum(point["post_count"] for point in time_point["data_points"])
            time_point["average_mood"] = round(total_mood / total_posts, 2) if total_posts > 0 else 0
    
    return timeline_data

def calculate_mood_summary(timeline_data):
    """计算心情数据的总体摘要"""
    total_posts = 0
    total_mood = 0
    highest_mood = {"score": 0, "time_point": ""}
    lowest_mood = {"score": 5, "time_point": ""}  
    has_data = False

    for time_point in timeline_data:
        if time_point["post_count"] > 0:
            has_data = True
            
            if time_point["average_mood"] > highest_mood["score"]:
                highest_mood = {
                    "score": time_point["average_mood"],
                    "time_point": time_point["time_point"]
                }
            
            if time_point["average_mood"] < lowest_mood["score"]:
                lowest_mood = {
                    "score": time_point["average_mood"],
                    "time_point": time_point["time_point"]
                }
            
        total_posts += time_point["post_count"]
        total_mood += time_point["average_mood"] * time_point["post_count"] if time_point["post_count"] > 0 else 0
    
    if not has_data:
        lowest_mood = {"score": 0, "time_point": ""}
    
    return {
        "total_posts": total_posts,
        "average_mood": round(total_mood / total_posts, 2) if total_posts > 0 else 0,
        "highest_mood": highest_mood if has_data else None,
        "lowest_mood": lowest_mood if has_data else None
    }