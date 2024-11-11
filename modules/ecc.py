from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import random
import hashlib
from typing import Optional, Tuple
from math import isqrt

# Class to handle ECC operations for NIST P-256 Curve
class ECC:
    # NIST P-256 parameters for curve setup
    P = int("ffffffff00000001000000000000000000000000ffffffffffffffffffffffff", 16)
    A = int("ffffffff00000001000000000000000000000000fffffffffffffffffffffffc", 16)
    B = int("5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b", 16)
    GX = int("6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296", 16)
    GY = int("4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5", 16)
    ORDER = int("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 16)
    MOD_BITS = 256
    MOD_FACTOR_256 = 2 ** MOD_BITS % P

    @staticmethod
    def int_to_bytes(val: int) -> bytes:
        """Converts an integer to bytes."""
        return val.to_bytes((val.bit_length() + 7) // 8, 'big')

    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Converts bytes to an integer."""
        return int.from_bytes(data, 'big')

    @staticmethod
    def sha256(data: bytes) -> bytes:
        """Generates SHA-256 hash."""
        return hashlib.sha256(data).digest()

    class ECPoint:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

        def __eq__(self, other):
            return isinstance(other, ECC.ECPoint) and self.x == other.x and self.y == other.y

        def add(self, other: 'ECC.ECPoint') -> 'ECC.ECPoint':
            # Implement point addition using P-256 rules
            if self == other:  # Point doubling
                return self.double()
            else:  # Point addition
                return ECC.point_addition(self, other)

        def double(self) -> 'ECC.ECPoint':
            # Implement point doubling using curve parameters
            return ECC.point_double(self)

        def multiply(self, k: int) -> 'ECC.ECPoint':
            # Implement scalar multiplication using double-and-add
            result = ECC.INFINITY
            addend = self

            while k:
                if k & 1:
                    result = result.add(addend)
                addend = addend.double()
                k >>= 1

            return result

    @staticmethod
    def point_addition(p: 'ECC.ECPoint', q: 'ECC.ECPoint') -> 'ECC.ECPoint':
        """Adds two points on the elliptic curve."""
        if p == ECC.INFINITY:
            return q
        if q == ECC.INFINITY:
            return p
        if p == q:
            return ECC.point_double(p)

        # Lambda for addition of different points
        m = ((q.y - p.y) * pow(q.x - p.x, -1, ECC.P)) % ECC.P
        x_r = (m * m - p.x - q.x) % ECC.P
        y_r = (m * (p.x - x_r) - p.y) % ECC.P
        return ECC.ECPoint(x_r, y_r)

    @staticmethod
    def point_double(p: 'ECC.ECPoint') -> 'ECC.ECPoint':
        """Doubles a point on the elliptic curve."""
        if p == ECC.INFINITY:
            return ECC.INFINITY

        # Lambda for point doubling
        m = ((3 * p.x * p.x + ECC.A) * pow(2 * p.y, -1, ECC.P)) % ECC.P
        x_r = (m * m - 2 * p.x) % ECC.P
        y_r = (m * (p.x - x_r) - p.y) % ECC.P
        return ECC.ECPoint(x_r, y_r)

    # Generator point on the curve
    G = ECPoint(GX, GY)
    INFINITY = ECPoint(0, 0)

    @staticmethod
    def verify_modular_params():
        """Verifies if modular curve parameters are correct."""
        a_res = (ECC.A * ECC.MOD_FACTOR_256) % ECC.P
        b_res = (ECC.B * ECC.MOD_FACTOR_256) % ECC.P
        if a_res != ECC.A or b_res != ECC.B:
            raise ValueError("Invalid modular curve parameters")

    @staticmethod
    def point_from_x(x: int) -> Optional['ECC.ECPoint']:
        """Finds the corresponding point on the curve given x."""
        y_squared = (x * x * x + ECC.A * x + ECC.B) % ECC.P
        y = pow(y_squared, (ECC.P + 1) // 4, ECC.P)
        return ECC.ECPoint(x, y) if y_squared == (y * y) % ECC.P else None

    @staticmethod
    def encrypt(plaintext: bytes, pubkey: 'ECC.ECPoint') -> Tuple['ECC.ECPoint', 'ECC.ECPoint']:
        k = random.randint(1, ECC.ORDER - 1)
        point1 = ECC.G.multiply(k)
        point2 = pubkey.multiply(k).add(ECC.point_from_x(ECC.bytes_to_int(plaintext)))
        return point1, point2

    @staticmethod
    def decrypt(ciphertext: Tuple['ECC.ECPoint', 'ECC.ECPoint'], prvkey: int) -> bytes:
        point1, point2 = ciphertext
        neg_point1 = point1.multiply(prvkey).negate()
        plaintext_point = point2.add(neg_point1)
        return ECC.int_to_bytes(plaintext_point.x)

# ECC Class instantiation with curve checks
ecc = ECC()
ecc.verify_modular_params()
