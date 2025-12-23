from src.kmsConfig import get_kms, get_master_crypto_key
import tempfile
import base64
import json
from src.loggerServices import log_error
from .util import (
    write_input_file_to_temp,
    generate_data_key,
    decode_plaintext_key,
    generate_random_iv,
    read_file_bytes,
    encrypt,
    build_enc_data,
    write_json_to_file,
    write_str_to_file,
    remove_file,
    decrypt
)
kms_client = get_kms() 
master_crypto_key = get_master_crypto_key()

# Encrypt a file for OSS upload, return paths to .enc and .key temp files

def encrypt_file_for_oss(input_file):
    """
    Encrypt a file for OSS upload. Returns (enc_path, key_path).
    input_file: UploadFile or file-like object
    kms_client: KMSClient instance
    master_crypto_key: KMS Master key for encrypt and decrypt use
    """
    # 1. get tmp file path
    tmp_plain_path = write_input_file_to_temp(input_file)
    # 2. generate data key
    key_info = generate_data_key(kms_client, master_crypto_key)
    # 3. get plaintext key/ciphertext blob/iv
    plaintext_key = key_info['Plaintext']
    ciphertext_blob = key_info['CiphertextBlob']
    data_key_iv = key_info.get('Iv')
    # 4. decode plaintext key to bytes
    plaintext_key_bytes = decode_plaintext_key(plaintext_key)
    # 5. generate random iv
    iv = generate_random_iv(12)
    # 6. read file content to bytes
    data = read_file_bytes(tmp_plain_path)
    # 7. encrypt data
    associated_data = b""
    iv_b64, ciphertext_b64, tag_b64 = encrypt(plaintext_key_bytes, iv, data, associated_data)
    # 8. encode encrypted data key
    encrypted_data_key_b64 = base64.b64encode(ciphertext_blob).decode('utf-8') if isinstance(ciphertext_blob, bytes) else ciphertext_blob
    # 9. build encrypted data json structure
    enc_data = build_enc_data(iv_b64, ciphertext_b64, tag_b64, encrypted_data_key_b64, data_key_iv)
    # 10. write .enc file
    enc_path = tmp_plain_path + '.enc'
    write_json_to_file(enc_data, enc_path)
    # 11. write .key file
    key_path = tmp_plain_path + '.key'
    write_str_to_file(encrypted_data_key_b64, key_path)
    # 12. remove tmp file
    remove_file(tmp_plain_path)
    return enc_path, key_path

# Decrypt a file from OSS .enc/.key files, return path to decrypted temp file

def decrypt_file_from_oss(enc_file_content, key_file_content):
    """
    Decrypt a file from OSS .enc/.key file contents. Returns path to decrypted temp file.
    enc_file_content: bytes (JSON content of .enc file)
    key_file_content: str (ciphertext blob)
    kms_client: KMSClient instance
    """
    try:
        # 1. parse encrypted file content (json)
        enc_data = json.loads(enc_file_content.decode('utf-8')) if isinstance(enc_file_content, bytes) else json.loads(enc_file_content)
        # 2. extract iv, ciphertext, tag, data_key_iv
        iv_b64 = enc_data['iv']
        ciphertext_b64 = enc_data['ciphertext']
        tag_b64 = enc_data['tag']
        data_key_iv = base64.b64decode(enc_data['data_key_iv']) if enc_data.get('data_key_iv') else None
        # 3. decrypt data key using kms_client
        key_info = kms_client.decrypt(key_file_content, data_key_iv)
        # 4. decode plaintext key to bytes
        plaintext_key = key_info['Plaintext']
        plaintext_key_bytes = decode_plaintext_key(plaintext_key)
        # 5. decrypt file content
        associated_data = b""
        decrypted_content = decrypt(plaintext_key_bytes, associated_data, iv_b64, ciphertext_b64, tag_b64)
        # 6. write decrypted content to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_plain:
            tmp_plain.write(decrypted_content)
            plain_path = tmp_plain.name
        return plain_path
    except Exception as e:
        log_error(f"Decryption process failed: {e}")
        raise

def encrypt_plan_text(plain_text: str) -> str:
    """
    encrypt plain text, return base64 string
    """
    if plain_text is None:
        return None  # Return None as-is if input is None
    if isinstance(plain_text, str) and len(plain_text) == 0:
        return plain_text
    # 1. generate data key
    key_info = generate_data_key(kms_client, master_crypto_key)
    plaintext_key = key_info['Plaintext']
    ciphertext_blob = key_info['CiphertextBlob']
    data_key_iv = key_info.get('Iv')
    # 2. decode plaintext key
    plaintext_key_bytes = decode_plaintext_key(plaintext_key)
    # 3. generate iv
    iv = generate_random_iv(12)
    # 4. encrypt plain text
    associated_data = b""
    iv_b64, ciphertext_b64, tag_b64 = encrypt(plaintext_key_bytes, iv, plain_text, associated_data)
    # 5. encrypted data key base64
    encrypted_data_key_b64 = base64.b64encode(ciphertext_blob).decode('utf-8') if isinstance(ciphertext_blob, bytes) else ciphertext_blob
    # 6. build enc dict
    enc_dict = {
        'iv': iv_b64,
        'ciphertext': ciphertext_b64,
        'tag': tag_b64,
        'encrypted_data_key': encrypted_data_key_b64,
        'data_key_iv': base64.b64encode(data_key_iv).decode() if data_key_iv else None
    }
    # 7. dict to json string then to base64
    json_str = json.dumps(enc_dict)
    b64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    return b64_str


def decrypt_plan_text(enc_b64_str: str) -> str:
    """
    decrypt base64 string, return plain text
    """
    try:
        if enc_b64_str is None:
            return None  # Return None as-is if input is None
        if isinstance(enc_b64_str, str) and len(enc_b64_str) == 0:
            return enc_b64_str
        json_str = base64.b64decode(enc_b64_str).decode('utf-8')
        enc_dict = json.loads(json_str)
        iv_b64 = enc_dict['iv']
        ciphertext_b64 = enc_dict['ciphertext']
        tag_b64 = enc_dict['tag']
        encrypted_data_key_b64 = enc_dict['encrypted_data_key']
        data_key_iv = base64.b64decode(enc_dict['data_key_iv']) if enc_dict.get('data_key_iv') else None
        # 1. decrypt data key
        key_info = kms_client.decrypt(encrypted_data_key_b64, data_key_iv)
        plaintext_key = key_info['Plaintext']
        plaintext_key_bytes = decode_plaintext_key(plaintext_key)
        # 2. decrypt content
        associated_data = b""
        decrypted_bytes = decrypt(plaintext_key_bytes, associated_data, iv_b64, ciphertext_b64, tag_b64)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        log_error(f"Decrypt plan text failed: {e}")
        raise