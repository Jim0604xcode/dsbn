import phonenumbers

from src.exceptions import GeneralErrorExcpetion

def split_phone_number(phone: str) -> tuple[str, str]:
    """
    將電話號碼拆分為區域代碼和本地號碼，支援所有國家/地區。
    
    Args:
        phone (str): 完整的國際電話號碼 (e.g., "+85251823007", "+12065550123")
        
    Returns:
        tuple[str, str]: (area_code, local_number) e.g., ("+852", "51823007") 或 ("+1206", "5550123")
        
    Raises:
        ValueError: 如果電話號碼格式無效或無法解析
    """
    try:
        # 解析電話號碼，自動檢測國家
        parsed_number = phonenumbers.parse(phone, None)
        
        # 獲取國家代碼（區域代碼的一部分）
        country_code = "+" + str(parsed_number.country_code)
        
        # 獲取本地號碼
        local_number = str(parsed_number.national_number)
        
        # 獲取完整的區域代碼（可能包括國家代碼和區域代碼，依賴於國家）
        # 注意：某些國家（如美國）區域代碼是 3 位，需根據國家調整
        area_code = country_code  # 基礎區域代碼為國家代碼
        if phonenumbers.region_code_for_number(parsed_number) in ["US", "CA"]:  # 美國和加拿大有 3 位區域代碼
            national_number = str(parsed_number.national_number)
            if len(national_number) >= 10:  # 確保有足夠的數字
                area_code += national_number[:3]  # e.g., "+1206" for US
                local_number = national_number[3:]
        
        return area_code, local_number
    except phonenumbers.phonenumberutil.NumberParseException as e:
        raise GeneralErrorExcpetion(f"無效的電話號碼格式: {e}")

# 測試用例
# try:
#     # 測試香港號碼
#     phone_hk = "+85251823007"
#     area_code_hk, local_number_hk = split_phone_number(phone_hk)
#     print(f"香港區域代碼: {area_code_hk}")  # 輸出: 香港區域代碼: +852
#     print(f"香港本地號碼: {local_number_hk}")  # 輸出: 香港本地號碼: 51823007

#     # 測試美國號碼
#     phone_us = "+12065550123"
#     area_code_us, local_number_us = split_phone_number(phone_us)
#     print(f"美國區域代碼: {area_code_us}")  # 輸出: 美國區域代碼: +1206
#     print(f"美國本地號碼: {local_number_us}")  # 輸出: 美國本地號碼: 5550123
# except ValueError as e:
#     print(f"錯誤: {e}")