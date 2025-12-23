import httpx
# import requests
import json
from src.config import D7NETWORK_API_ENDPOINT, D7NETWORK_API_KEY, D7NETWORK_API_REPORT_ENDPOINT
from src.loggerServices import log_info
async def send_sms(phone_number:str,content:str):
    # payload = json.dumps({
    #         "messages": [
    #             {
    #             "channel": "sms",
    #             "recipients": [
    #                 phone_number
    #             ],
    #             "content":content,
    #             "msg_type": "text",
    #             "data_coding": "unicode"
    #             }
    #         ],
    #         "message_globals": {
    #             "originator": "Deep Soul",
    #             "report_url": D7NETWORK_API_REPORT_ENDPOINT
    #         }
    #     },ensure_ascii=False)
    payload = {
        "messages": [
            {
                "channel": "sms",
                "recipients": [phone_number],
                "content": content,
                "msg_type": "text",
                "data_coding": "unicode"
            }
        ],
        "message_globals": {
            "originator": "Deep Soul",
            "report_url": D7NETWORK_API_REPORT_ENDPOINT
        }
    }    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {D7NETWORK_API_KEY}'
    }
    # log_info(f'start send sms request to {phone_number}')
    # log_info(f'SMS payload: {json.dumps(payload, ensure_ascii=False)}')

    async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                url=D7NETWORK_API_ENDPOINT,
                headers=headers,
                json=payload  # 自動轉 JSON
            )

    # log_info(f'SMS raw response: {response.text}')
    # log_info(f'SMS status code: {response.status_code}')

    # 檢查是否成功
    if response.status_code >= 400:
        raise Exception(f"D7 SMS API error {response.status_code}: {response.text}")
    # log_info(f'start send sms request')    
    # requests.request("POST", D7NETWORK_API_ENDPOINT, headers=headers, data=payload)
    # log_info(f'end send sms request')
    # response = await requests.request("POST", D7NETWORK_API_ENDPOINT, headers=headers, data=payload)
    # log_info(f'sms response: {response.text}')
    return
    