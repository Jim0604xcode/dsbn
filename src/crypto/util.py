import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt(key, iv, plaintext, associated_data=None):
    # 自動轉 bytes
    if isinstance(key, str):
        key = base64.b64decode(key)
    if isinstance(iv, str):
        iv = base64.b64decode(iv)
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    if associated_data is None:
        associated_data = b""
    elif isinstance(associated_data, str):
        associated_data = associated_data.encode('utf-8')

    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    ).encryptor()

    encryptor.authenticate_additional_data(associated_data)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # 全部轉 base64 字串回傳
    return (
        base64.b64encode(iv).decode('utf-8'),
        base64.b64encode(ciphertext).decode('utf-8'),
        base64.b64encode(encryptor.tag).decode('utf-8')
    )


def decrypt(key, associated_data, iv, ciphertext, tag):
    # 自動轉 bytes
    if isinstance(key, str):
        key = base64.b64decode(key)
    if isinstance(iv, str):
        iv = base64.b64decode(iv)
    if isinstance(ciphertext, str):
        ciphertext = base64.b64decode(ciphertext)
    if isinstance(tag, str):
        tag = base64.b64decode(tag)
    if associated_data is None:
        associated_data = b""
    elif isinstance(associated_data, str):
        associated_data = associated_data.encode('utf-8')

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    ).decryptor()
    decryptor.authenticate_additional_data(associated_data)
    return decryptor.update(ciphertext) + decryptor.finalize()


def write_input_file_to_temp(input_file):
    """
    write input file to temp file, return temp file path
    """
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tmp_plain:
        tmp_plain.write(input_file.file.read())
        return tmp_plain.name


def generate_data_key(kms_client, master_crypto_key):
    """
    generate data key, return KMS return dict
    """
    return kms_client.generate_data_key(master_crypto_key, number_of_bytes=32)


def decode_plaintext_key(plaintext_key):
    """
    decode plaintext key to bytes
    """
    import base64
    if isinstance(plaintext_key, str):
        return base64.b64decode(plaintext_key)
    return plaintext_key


def generate_random_iv(length=12):
    """
    generate random iv
    """
    import os
    return os.urandom(length)


def read_file_bytes(file_path):
    """
    read file content to bytes
    """
    with open(file_path, 'rb') as f:
        return f.read()


def build_enc_data(iv_b64, ciphertext_b64, tag_b64, encrypted_data_key_b64, data_key_iv):
    """
    build encrypted data json structure
    """
    import base64
    return {
        'iv': iv_b64,
        'ciphertext': ciphertext_b64,
        'tag': tag_b64,
        'encrypted_data_key': encrypted_data_key_b64,
        'data_key_iv': base64.b64encode(data_key_iv).decode() if data_key_iv else None
    }


def write_json_to_file(data, file_path):
    """
    write dict to file as json
    """
    import json
    with open(file_path, 'w') as f:
        json.dump(data, f)


def write_str_to_file(data, file_path):
    """
    write string to file
    """
    with open(file_path, 'w') as f:
        f.write(data)


def remove_file(file_path):
    """
    remove file
    """
    import os
    os.remove(file_path)

