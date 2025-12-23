from fastapi import UploadFile
import requests

# import aiohttp
from sqlalchemy.orm import Session
# from src.auth.models import PhoneMaster
from src.loggerServices import log_error, log_info
from gql import Client, gql
from src.authgear.utils import generate_transport, getUserIDWithBase64encoded
from src.authgear.generateAuthgearJWT import generateAuthgearJWT
from src.authgear.service import get_presigned_upload_url, upload_image_to_presigned_url
from src.utils.imageUtil import checkImageConditions
from src.exceptions import BadReqExpection
from src.auth.schemas import UserUpdateMobileInputRequest, UserUpdateMobileVerifyInputRequest
from src.config import AUTHGEAR_ENDPOINT
from src.transaction import wrap_update_func
async def get_authgear_jwt():
    return generateAuthgearJWT()

async def verify_otp(state_token: str,otp_code:str):
    url = f"{AUTHGEAR_ENDPOINT}/api/v1/authentication_flows/states/input"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "state_token": state_token,
        "input": {
            "authentication": "secondary_oob_otp_sms",
            "otp_form": "code",
            "code": otp_code,
            "index": 0  # 添加 index 字段，指定 options 中的第一個選項
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    # log_info(f'verify otp ------> {response}')
    if response.status_code == 200:
        result = response.json()["result"]
        
        return result
        # if result["action"]["type"] == "complete":
        #     print("OTP 驗證成功！手機號碼已驗證")
        #     return result
        # else:
        #     raise Exception(f"OTP 驗證未完成: {result}")
    else:
        raise Exception(f"OTP 驗證失敗: {response.text}")

async def submit_password(state_token: str, password: str):
    url = f"{AUTHGEAR_ENDPOINT}/api/v1/authentication_flows/states/input"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "state_token": state_token,
        "input": {
            "authentication": "primary_password",
            "password": password
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        result = response.json()["result"]
        # log_info(f"密碼驗證回應: {result}")
        return result
        # if result["action"]["type"] == "authenticate" and "data" in result["action"]:
        #     return result  # 返回新的 state_token 或下一步數據
        # else:
        #     raise Exception(f"密碼驗證未完成: {result}")
    else:
        raise Exception(f"密碼驗證失敗: {response.text}")
    

async def submit_phone_for_verification(state_token: str, phone_number: str):
    url = f"{AUTHGEAR_ENDPOINT}/api/v1/authentication_flows/states/input"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "state_token": state_token,
        "input": {
            "identification": "phone",
            "login_id": phone_number
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        raise Exception(f"提交手機號碼失敗: {response.text}")

async def start_verification_flow():
    url = f"{AUTHGEAR_ENDPOINT}/api/v1/authentication_flows"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "type": "login",  # 或 "promote" 用於更新手機號碼
        "name": "default"
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        raise Exception(f"啟動驗證流程失敗: {response.text}")
async def verification_flow(phone_number:str,otp_code:str,password:str):
    r1 = await start_verification_flow()
    # log_info(f'step1----------------->{r1}')
    r2 = await submit_phone_for_verification(r1["state_token"],phone_number)
    # log_info(f'step2----------------->{r2}')
    r3 = await submit_password(r2["state_token"], password)  # 提交密碼
    # log_info(f'step3----------------->{r3}')
    r4 = await verify_otp(r3["state_token"], otp_code)      # 提交 OTP
    # log_info(f'step4----------------->{r4}')
    

async def send_otp(phone_number:str):
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            mutation ($target: String!) {
                generateOOBOTPCode(input: { target: $target }) {
                code
                }
            }
        """)  
        variables = {
            "target": phone_number
        }   
        result = await client.execute_async(query,variable_values=variables)
        return result
    except Exception as e:
        log_error(f"send_otp: {e}")
        raise                         
async def create_2fa(authgear_id:str,phone_number:str):
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            mutation CreateAuthenticator($input: CreateAuthenticatorInput!) {
                createAuthenticator(input: $input) {
                    authenticator {
                        id
                    }
                }
            }
        """)         
        variables = {
            "input": {
                "userID": getUserIDWithBase64encoded(authgear_id),
                "definition": {
                    "kind": "SECONDARY",            # Adjusted to likely valid enum value
                    "type": "OOB_OTP_SMS",          # Adjusted to likely valid enum value
                    "oobOtpSMS": {            # 新增必要的 oobOtpSMS 字段
                        "phone": phone_number  # 電話號碼
                    }
                }
                
            }
        }   
        result = await client.execute_async(query,variable_values=variables)
        return result
    except Exception as e:
        log_error(f"create_2fa: {e}")
        raise     
async def remove_2fa(authenticatorID:str):
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            mutation DeleteAuthenticator($input: DeleteAuthenticatorInput!) {
                deleteAuthenticator(input: $input) {
                    user {
                        id
                    }
                }
            }
        """)
        variables = {
            "input": {
                "authenticatorID": authenticatorID  # 2FA ID，从查询获取
            }
        }
        result = await client.execute_async(query,variable_values=variables)
        return result
    except Exception as e:
        log_error(f"query user by ID: {e}")
        raise     
async def query_user_by_authgear_id(authgear_id: str) -> dict:
    """
    Query user by authgear ID.
    """
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        # t = generateAuthgearJWT()
        # log_info(t)
        # query = gql("""
        #     {
        #         __type(name: "AuthenticatorType") {
        #             enumValues {
        #             name
        #             }
        #         }    
        #     }
        # """)    
                
        query = gql("""
            query ($id: String!){
            users(searchKeyword:$id) {
                edges {
                node {
                    authenticators{
                        edges {
                            node {
                                id
                                type
                                claims
                            }
                        }
                    }
                    identities{
                                edges {
                                    node {
                                        id
                                        type
                                        claims  # 直接查詢 claims
                                    }
                                }
                            }
                    id
                    standardAttributes
                    customAttributes
                }
                }
            }
            }
        """)
        variables = {
            "id": authgear_id,
        }
        result = await client.execute_async(query,variable_values=variables)
        
        if not result["users"]['edges']:
            return None
        return result["users"]['edges']
        
    except Exception as e:
        log_error(f"query user by ID: {e}")
        raise  


async def query_user_by_search_keyword(search_keyword: str) -> dict:
    """
    Verify the user by search keyword.
    """
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            query ($searchKeyword: String!){
                users(searchKeyword:$searchKeyword) {
                    edges {
                        node {
                            id
                            standardAttributes
                        }
                    }
                }
            }
                    
        """)
        variables = {
            "searchKeyword": search_keyword,
        }
        result = await client.execute_async(query, variable_values=variables)

        # 檢查是否有用戶
        if not result["users"]['edges']:
            return False
        return result["users"]['edges']
        # return result
    except Exception as e:
        log_error(f"query user by search keyword: {e}")
        raise
           
async def query_user_by_phone_number(phone_number: str) -> dict:
    """
    Verify the user by phone number.
    """
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            query ($phone: String!){
            users(searchKeyword:$phone) {
                edges {
                node {
                    id
                    standardAttributes
                }
                }
            }
            }
        """)
        variables = {
            "phone": phone_number,
        }
        result = await client.execute_async(query, variable_values=variables)
        
        # 檢查是否有用戶
        if not result["users"]['edges']:
            return False
        return result["users"]['edges']
        # return result
    except Exception as e:
        log_error(f"query user by phone: {e}")
        raise     
async def update_user_profile_picture(authgear_id: str, file: UploadFile) -> str: 
    """
    Main function to update the user's profile picture.
    """
    try:
        # Step 1: check the image conditions
        await checkImageConditions(file)

        # Step 2: Get the pre-signed upload URL
        upload_url =  get_presigned_upload_url()

        # Step 3: Upload the image file to the pre-signed URL
        result_url =  upload_image_to_presigned_url(upload_url, file, authgear_id)
        
        return result_url
    except BadReqExpection as e:
        log_error(f"update_user_profile_picture: {e}")
        raise 
    except Exception as e:
        log_error(f"update_user_profile_picture: {e}")
        raise BadReqExpection(details="Unexpected error during profile picture update", code="INTERNAL_SERVER_ERROR")


async def updateUserInformation(authgear_id: str, standardAttributes: dict, customAttributes: dict):
    try:
        # Remove 'picture' key if its value is '' or None
        if standardAttributes.get("picture") in ['', None]:
            standardAttributes.pop("picture", None)
        if standardAttributes.get("phone_number") in ['', None]:
            standardAttributes.pop("phone_number", None)    
        if standardAttributes.get("phone_number_verified") in ['', None]:
            standardAttributes.pop("phone_number_verified", None)  
        if standardAttributes.get("nickname") in ['', None]:
            standardAttributes.pop("nickname", None)
            
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            mutation ($userID: ID!, $standardAttributes: UserStandardAttributes, $customAttributes: UserCustomAttributes) {
                updateUser(
                    input: {standardAttributes: $standardAttributes, userID: $userID, customAttributes: $customAttributes}
                ) {
                    user {
                        id
                        standardAttributes
                        customAttributes
                    }
                }
            }
        """)
        variables = {
            "userID": getUserIDWithBase64encoded(authgear_id),
            "standardAttributes": standardAttributes,
            "customAttributes": customAttributes
        }
        result = await client.execute_async(query, variable_values=variables)
        return result

    except Exception as e:
        log_error(f"updateUserInformation: {e}")
        raise 





async def delete_identity(identity_id: str) -> dict:
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        mutation = gql("""
            mutation DeleteIdentity($input: DeleteIdentityInput!) {
                deleteIdentity(input: $input) {
                    user {
                        id
                    }
                }
            }
        """)
        variables = {
            "input": {
                "identityID":identity_id
            }
        }
        await client.execute_async(mutation, variable_values=variables)
        return
    
    except Exception as e:
        log_error(f"Delete identity error: {e}")
        raise        




async def update_identity(authgear_id: str, phone_number: str,identity_id: str):
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
        mutation UpdateIdentity($input: UpdateIdentityInput!) {
            updateIdentity(input: $input) {
                identity {
                    id
                    type
                    claims
                }
            }
        }
        """)
        variables = {
            "input": {
                "identityID":identity_id,
                "userID": getUserIDWithBase64encoded(authgear_id),
                "definition": {
                    "loginID": {
                        "key": "phone",
                        "value": phone_number
                    }
                }
            }
        }
        await client.execute_async(query, variable_values=variables)
        return
    
    except Exception as e:
        log_error(f"Update identity error: {e}")
        raise



async def create_identity(authgear_id: str,phone_number:str):
    try:
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
        mutation CreateIdentity($input: CreateIdentityInput!) {
            createIdentity(input: $input) {
                identity {
                    id
                    type
                    claims
                }
            }
        }
        """)
        variables = {
            "input": {
                "userID": getUserIDWithBase64encoded(authgear_id),
                "definition": {
                    "loginID": {
                    "key": "phone",  # Use 'phone' as the login ID key
                    "value": phone_number  # Correct nested structure
                    }
                }
            }
        }
        await client.execute_async(query, variable_values=variables)
        return
    
    except Exception as e:
        log_error(f"Delete identity error: {e}")
        raise  


# async def update_mobile_verify_flow(authgear_id: str, reqBody: UserUpdateMobileVerifyInputRequest,db:Session):
#     try:
#         otp_code = reqBody.model_dump().get('otp_code')
#         password = reqBody.model_dump().get('password')
#         new_phone_number = reqBody.model_dump().get('new_phone_number')
#         await verification_flow(new_phone_number,otp_code,password)
#         # 驗證成功後，remove old identity and 2fa and update DB
#         r = await query_user_by_authgear_id(authgear_id)
        
        
#         customAttributes = r[0].get("node", {}).get("customAttributes", {})
#         standardAttributes = r[0].get("node", {}).get("standardAttributes", {})
#         old_phone_number = standardAttributes['phone_number']
#         standardAttributes['phone_number'] = new_phone_number
#         for user in r:
#             identities = user.get("node", {}).get("identities", {}).get("edges", [])
#             authenticators = user.get("node", {}).get("authenticators",{}).get("edges", [])
#             for identity in identities:
#                 node = identity.get("node", {})
#                 claims = node.get("claims", {})
#                 identity_type = node.get("type")
#                 login_id_type = claims.get("https://authgear.com/claims/login_id/type")
#                 existing_phone = claims.get("phone_number")

#                 # 僅檢查 type = "LOGIN_ID" 且 login_id_type = "phone" 的身份
#                 if identity_type == "LOGIN_ID" and login_id_type == "phone" and existing_phone != new_phone_number:
#                     await delete_identity(node.get("id"))
#             for authen in authenticators:
#                 node = authen.get("node", {})
#                 claims = node.get("claims", {})
#                 authen_type = node.get("type")
#                 if authen_type == "OOB_OTP_SMS":
#                     await remove_2fa(node.get("id"))
        
#         client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        
#         query = gql("""
#             mutation ($userID: ID!, $standardAttributes: UserStandardAttributes, $customAttributes: UserCustomAttributes) {
#                 updateUser(
#                     input: {standardAttributes: $standardAttributes, userID: $userID, customAttributes: $customAttributes}
#                 ) {
#                     user {
#                         id
#                         standardAttributes
#                         customAttributes
#                     }
#                 }
#             }
#         """)
        
#         variables = {
#             "userID": getUserIDWithBase64encoded(authgear_id),
#             "standardAttributes": standardAttributes,
#             "customAttributes": customAttributes
#         }
#         # log_info(variables)
#         result = await client.execute_async(query, variable_values=variables)                    
#         wrap_update_func(PhoneMaster,{"phone":old_phone_number},{"phone":new_phone_number},db,db.query(PhoneMaster).filter(PhoneMaster.phone_number == old_phone_number).count() > 0)
#         db.commit()
#         return result
#     except Exception as e:
#         db.rollback()
#         log_error(f"updateUserMobile: {e}")
#         raise ValueError(str(e))     

async def init_custom_authen_flow(authgear_id: str, reqBody: UserUpdateMobileInputRequest):
    try:
        phone_number = f"{reqBody.model_dump().get('phone_number_prefix')}{reqBody.model_dump().get('phone_number')}"
        phone_number_is_exist = query_user_by_phone_number(phone_number)
        if phone_number_is_exist:
            raise ValueError(f"電話號碼 {phone_number} 已存在")
        await create_identity(authgear_id,phone_number)
        await create_2fa(authgear_id,phone_number)
        result = await send_otp('+85251823007')

        return result

    except Exception as e:
        log_error(f"updateUserMobile: {e}")
        raise ValueError(str(e)) 
    
# async def updateUserMobile_old(authgear_id: str, reqBody: UserUpdateMobileInputRequest, db: Session):
#     try:
#         phone_number = f"{reqBody.model_dump().get('phone_number_prefix')}{reqBody.model_dump().get('phone_number')}"
#         phone_number_is_exist = query_user_by_phone_number(phone_number)
#         if phone_number_is_exist:
#             raise ValueError(f"電話號碼 {phone_number} 已存在")
#         r = await query_user_by_authgear_id(authgear_id)    
#         # 檢查 identities 中的 phone_number 是否已存在
        
#         phone_identities = []
#         phone_authenticators = []
#         customAttributes = r[0].get("node", {}).get("customAttributes", {})
#         standardAttributes = r[0].get("node", {}).get("standardAttributes", {})
#         old_phone_number = standardAttributes['phone_number']
#         standardAttributes['phone_number'] = phone_number
#         for user in r:
#             identities = user.get("node", {}).get("identities", {}).get("edges", [])
#             authenticators = user.get("node", {}).get("authenticators",{}).get("edges", [])
#             for identity in identities:
#                 node = identity.get("node", {})
#                 claims = node.get("claims", {})
#                 identity_type = node.get("type")
#                 login_id_type = claims.get("https://authgear.com/claims/login_id/type")
#                 existing_phone = claims.get("phone_number")

#                 # 僅檢查 type = "LOGIN_ID" 且 login_id_type = "phone" 的身份
#                 if identity_type == "LOGIN_ID" and login_id_type == "phone":
#                     phone_identities.append({
#                         "id": node.get("id"),
#                         "phone_number": existing_phone
#                     })
#             for authen in authenticators:
#                 node = authen.get("node", {})
#                 claims = node.get("claims", {})
#                 authen_type = node.get("type")
#                 if authen_type == "OOB_OTP_SMS":
#                     phone_authenticators.append({
#                         "id":node.get("id"),
#                     })


#         # 檢查是否有一個符合條件的身份
#         if len(phone_identities) > 0:
#             # 刪除身份
#             for identity in phone_identities:
#                 await delete_identity(identity["id"])
#         # 檢查是否有一個符合條件的Authen
#         if len(phone_authenticators) > 0:
#             # 刪除Authen
#             for authen in phone_authenticators:
#                 await remove_2fa(authen["id"])

#             # identity_id = phone_identities[0]["id"]    
#             # if phone_identities[0]["phone_number"] == phone_number:
#             #     log_error(f"電話號碼 {phone_number} 已存在於身份中")
#             #     # raise Exception(f"電話號碼 {phone_number} 已存在")    
#             #     raise ValueError(f"電話號碼 {phone_number} 已存在")
#         # elif len(phone_identities) == 1:
#         #     # 只有一個身份，檢查電話號碼是否匹配
#         #     identity_id = phone_identities[0]["id"]
#         #     if phone_identities[0]["phone_number"] == phone_number:
#         #         log_error(f"電話號碼 {phone_number} 已存在於身份中")
#         #         # raise Exception(f"電話號碼 {phone_number} 已存在")    
#         #         raise ValueError(f"電話號碼 {phone_number} 已存在")
#         # else:
#         #     # 沒有符合條件的身份
#         #     log_error("未找到符合條件的身份")
#         #     raise ValueError("未找到符合條件的身份")
                    
#         # 如果電話號碼不存在，繼續更新身份
#         # if identity_id:
#         #     await update_identity(authgear_id,phone_number,identity_id)    
#         await create_identity(authgear_id,phone_number)
#         await create_2fa(authgear_id,phone_number)
        
#         client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        
#         query = gql("""
#             mutation ($userID: ID!, $standardAttributes: UserStandardAttributes, $customAttributes: UserCustomAttributes) {
#                 updateUser(
#                     input: {standardAttributes: $standardAttributes, userID: $userID, customAttributes: $customAttributes}
#                 ) {
#                     user {
#                         id
#                         standardAttributes
#                         customAttributes
#                     }
#                 }
#             }
#         """)
        
#         variables = {
#             "userID": getUserIDWithBase64encoded(authgear_id),
#             "standardAttributes": standardAttributes,
#             "customAttributes": customAttributes
#         }
#         # log_info(variables)
#         result = await client.execute_async(query, variable_values=variables)
        
#         # 新功能：更新成功後，使用 Authgear API 發送 OTP
#         # otp_session = await send_authgear_otp(phone_number)
#         # if otp_session:
#         #     # 返回結果，提示前端輸入 OTP（前端需調用另一個 verify API）
#         #     return {
#         #         **result,
#         #         "otp_sent": True,
#         #         "message": "電話號碼更新成功，驗證碼已發送到您的手機，請輸入驗證"
#         #     }
#         # else:
#         #     raise ValueError("OTP 發送失敗，請重試")
#         wrap_update_func(PhoneMaster,{"phone":old_phone_number},{"phone":phone_number},db,db.query(PhoneMaster).filter(PhoneMaster.phone_number == phone_number).count() > 0)
#         db.commit()
#         return result

    # except Exception as e:
    #     db.rollback()
    #     log_error(f"updateUserMobile: {e}")
    #     raise ValueError(str(e)) 

async def query_users_by_authgear_ids(authgear_ids: list) -> dict:
    """
    Query multiple users by a list of authgear IDs.
    """
    try:
        array_base64_endcoded_ids = [getUserIDWithBase64encoded(authgear_id) for authgear_id in authgear_ids]
        # log_info(array_base64_endcoded_ids)
        client = Client(transport=generate_transport(), fetch_schema_from_transport=False)
        query = gql("""
            query GetUsersByIds($ids: [ID!]!) {
              nodes(ids: $ids) {
                ... on User {
                  id
                  standardAttributes
                  formattedName
                }
              }
            }
        """)
        variables = {
            "ids": array_base64_endcoded_ids,
        }
        result = await client.execute_async(query, variable_values=variables)
        return result['nodes']
    except Exception as e:
        log_error(f"query users by IDs: {e}")
        raise 



