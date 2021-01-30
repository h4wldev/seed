import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

from seed.setting import setting


class AESCipher:
    key: str = setting.secret_key.aes_secret_key

    def __init__(self, bs: int = 16) -> None:
        self.bs: int = bs
        self.key: str = self._hashing(self.key)

    def encrypt(self, message: str) -> str:
        iv: bytes = Random.new().read(AES.block_size)
        cipher: 'AES' = AES.new(self.key, AES.MODE_CBC, iv)

        encrypted: str = cipher.encrypt(self._pad(message).encode())
        encoded: str = base64.b64encode(iv + encrypted)

        return encoded.decode('utf-8')

    def decrypt(self, message: str) -> str:
        decoded: str = base64.b64decode(message)

        iv: bytes = decoded[:AES.block_size]
        cipher: 'AES' = AES.new(self.key, AES.MODE_CBC, iv)

        decrypted: str = cipher.decrypt(decoded[AES.block_size:])

        return self._unpad(decrypted).decode('utf-8')

    def _hashing(self, message: str) -> str:
        return hashlib.sha256(message.encode('utf-8')).digest()

    def _pad(self, s: str) -> str:
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s: str) -> str:
        return s[:-ord(s[len(s) - 1:])]
