import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from typing import Optional

class Crypto:
    @staticmethod
    def base64_encode(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_decode(s: str) -> bytes:
        return base64.b64decode(s.encode('utf-8'))

    @staticmethod
    def SHA256(data: bytes) -> bytes:
        sha256 = hashlib.sha256()
        sha256.update(data)
        return sha256.digest()

    @staticmethod
    def MD5(data: bytes) -> bytes:
        md5 = hashlib.md5()
        md5.update(data)
        return md5.digest()

    @staticmethod
    def aes_cbc_encrypt(input_data: bytes, iv: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(input_data, AES.block_size)
        return cipher.encrypt(padded_data)

    @staticmethod
    def aes_cbc_decrypt(input_data: bytes, iv: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(input_data)
        return unpad(decrypted_data, AES.block_size)

    @staticmethod
    def aes_ctr_encrypt(input_data: bytes, iv: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv[:8])  # AES CTR requires a nonce
        return cipher.encrypt(input_data)

    @staticmethod
    def aes_ctr_decrypt(input_data: bytes, iv: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_CTR, nonce=iv[:8])
        return cipher.decrypt(input_data)

    @staticmethod
    def aes_ecb_encrypt(input_data: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_ECB)
        padded_data = pad(input_data, AES.block_size)
        return cipher.encrypt(padded_data)

    @staticmethod
    def aes_ecb_decrypt(input_data: bytes, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(input_data)
        return unpad(decrypted_data, AES.block_size)

    @staticmethod
    def xor(input1: bytes, input2: bytes) -> bytes:
        if len(input1) != len(input2):
            raise ValueError("Invalid arguments length to xor")
        return bytes(a ^ b for a, b in zip(input1, input2))

    @staticmethod
    def ecdsa(data: bytes, prvkey) -> bytes:
        digest = Crypto.SHA256(data)
        # Placeholder for ECC signature generation:
        # Replace with actual ECC signature creation method, e.g., using an ECC library.
        signature = prvkey.sign(digest)
        return signature

    @staticmethod
    def ecc_encrypt(input_data: bytes, pubkey) -> Optional[bytes]:
        if len(input_data) != 32:
            return None
        # Encrypt using ECC (implementation of ECC required here)
        plaintext = ECC.make_bi(input_data, 0, 32)
        points = ECC.encrypt(plaintext, pubkey)
        if points is None:
            return None
        p1 = points[0].bytes()
        p2 = points[1].bytes()
        return p1 + p2

    @staticmethod
    def ecc_decrypt(input_data: bytes, prvkey) -> Optional[bytes]:
        if len(input_data) != 128:
            return None
        # Decrypt using ECC (implementation of ECC required here)
        p1_data = input_data[:64]
        p2_data = input_data[64:]
        p1 = ECC.ECPoint(p1_data)
        p2 = ECC.ECPoint(p2_data)
        decrypted_point = ECC.decrypt([p1, p2], prvkey)
        return decrypted_point.bytes() if decrypted_point else None
