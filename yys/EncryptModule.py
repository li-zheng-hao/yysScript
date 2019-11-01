# 文件加密解密模块
import json
from pathlib import Path

class EncryptUtil:

    @staticmethod
    def decrypt(encrypted: int, key_int: int) -> str:
        decrypted: int = encrypted ^ key_int
        length = (decrypted.bit_length() + 7) // 8
        decrypted_bytes: bytes = int.to_bytes(decrypted, length, 'big')
        return decrypted_bytes.decode()


    @staticmethod
    def encrypt_file(path: str, key_path=None, *, encoding='utf-8'):
        """
        文件加密
        :param path:
        :param key_path:
        :param encoding:
        :return:
        """
        path = Path(path)
        cwd = path.cwd() / path.name.split('.')[0]
        path_encrypted = cwd / path.name
        if key_path is None:
            key_path = cwd / 'key'
        if not cwd.exists():
            cwd.mkdir()
            path_encrypted.touch()
            key_path.touch()

        with path.open('rt', encoding=encoding) as f1, \
                path_encrypted.open('wt', encoding=encoding) as f2, \
                key_path.open('wt', encoding=encoding) as f3:
            encrypted, key = EncryptUtil.encrypt(f1.read())
            json.dump(encrypted, f2)
            json.dump(key, f3)

    @staticmethod
    def decrypt_file(path_encrypted: str, key_path=None, *, encoding='utf-8'):
        """
        文件解密
        :param path_encrypted:
        :param key_path:
        :param encoding:
        :return:
        """
        path_encrypted = Path(path_encrypted)
        cwd = path_encrypted.cwd()
        path_decrypted = cwd / 'decrypted'
        if not path_decrypted.exists():
            path_decrypted.mkdir()
            path_decrypted /= path_encrypted.name
            path_decrypted.touch()
        if key_path is None:
            key_path = cwd / 'key'
        with path_encrypted.open('rt', encoding=encoding) as f1, \
                key_path.open('rt', encoding=encoding) as f2, \
                path_decrypted.open('wt', encoding=encoding) as f3:
            decrypted = EncryptUtil.decrypt(json.load(f1), json.load(f2))
            #后期更改，不需要进行读入
            f3.write(decrypted)