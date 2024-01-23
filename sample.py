from cryptography.fernet import Fernet
import base64

# 鍵の生成
key = Fernet.generate_key()
cipher_suite = Fernet(key)


def encrypt_value(value):
    """ 値を暗号化して文字列に変換する関数 """
    # 値を文字列に変換
    if not isinstance(value, str):
        value = str(value)
    # 暗号化
    encrypted_value = cipher_suite.encrypt(value.encode())
    # Base64エンコードして変数名として使用可能な形式にする
    return base64.urlsafe_b64encode(encrypted_value).decode('utf-8')


def decrypt_value(encrypted_value):
    """ 暗号化された文字列を復号して元の値に戻す関数 """
    # Base64デコード
    encrypted_value = base64.urlsafe_b64decode(encrypted_value)
    # 復号
    decrypted_value = cipher_suite.decrypt(encrypted_value).decode('utf-8')
    return decrypted_value


# テスト
original_value = "Hello, world!"
encrypted = encrypt_value(original_value)
decrypted = decrypt_value(encrypted)

print("Original:", original_value)
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)
