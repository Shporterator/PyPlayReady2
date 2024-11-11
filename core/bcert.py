import os
import struct
from typing import Optional, List, Union

class BCert:
    BASE_DIR = "secrets"

    # Magic binary cert file types
    BCERT_CHAIN = 0x43484149
    BCERT_CERT = 0x43455254

    # Recognized cert attributes
    TAG_IDS = 0x00010001
    TAG_KEYINFO = 0x00010006
    TAG_SIGNATURE = 0x00010008
    TAG_NAMES = 0x00000007
    TAG_KEY = 0x00010200

    # Key types
    KEY_SIGNING = 0x0
    KEY_ENCRYPTION = 0x1

    # Lengths
    DIGEST_SIZE = 0x20
    SIGNATURE_SIZE = 0x40
    PUB_KEY_SIZE = 0x40
    BO_SIZE = 0x400

    def __init__(self, source: Optional[str] = None):
        self.source = source

    @staticmethod
    def load_file(name: str) -> Optional[bytes]:
        path = os.path.join(BCert.BASE_DIR, name)
        print(f"path {path}")
        return Utils.load_file(path)

    def save_file(self, name: str, data: bytes) -> bool:
        path = os.path.join(self.BASE_DIR, name)
        return Utils.save_file(path, data)

    @staticmethod
    def from_file(name: str) -> Union["CertificateChain", "Certificate", None]:
        data = BCert.load_file(name)
        if data:
            bi = ByteInput(name, data)
            magic = bi.peek_4()
            if magic == BCert.BCERT_CHAIN:
                return CertificateChain(bi)
            elif magic == BCert.BCERT_CERT:
                return Certificate(bi)
        return None

    class CertAttr:
        def __init__(self, bi: "ByteInput", pos: int):
            self.pos = pos
            self.tag = bi.read_4()
            self.len = bi.read_4()
            self.data = bi.read_n(self.len - 8)

        def tag(self):
            return self.tag

        def length(self):
            return self.len

        def data(self):
            return self.data

        def pos(self):
            return self.pos

        def print(self):
            pp = Shell.get_pp()
            pp.println(f"attr: {Utils.hex_value(self.tag, 8)}")
            pp.printhex("data", self.data)

    class CertificateChain(BCert):
        def __init__(self, bi: Optional["ByteInput"] = None):
            super().__init__(bi.source() if bi else None)
            self.magic = 0
            self.word1 = 0
            self.total_len = 0
            self.word3 = 0
            self.cert_cnt = 0
            self.certs = []

            if bi:
                self.magic = bi.read_4()
                self.word1 = bi.read_4()
                self.total_len = bi.read_4()
                self.word3 = bi.read_4()
                self.cert_cnt = bi.read_4()

                for _ in range(self.cert_cnt):
                    cert = Certificate(bi)
                    self.certs.append(cert)

        def cert_cnt(self):
            return self.cert_cnt

        def get(self, idx: int) -> Optional["Certificate"]:
            if idx < len(self.certs):
                return self.certs[idx]
            return None

        def add(self, cert: "Certificate"):
            self.certs.append(cert)
            self.cert_cnt += 1

        def insert(self, cert: "Certificate") -> "CertificateChain":
            chain = BCert.CertificateChain()
            chain.add(cert)
            for c in self.certs:
                chain.add(c)
            return chain

        def print(self, debug: bool):
            pp = Shell.get_pp()
            pp.println(f"CERT CHAIN: {self.source}")
            pp.pad(2, "")
            for cert in self.certs:
                cert.print()
            pp.leave()

        def body(self) -> bytes:
            bo = ByteOutput(BCert.BO_SIZE)
            total_len = sum(cert.body().length for cert in self.certs) + 5 * 4
            bo.write_4(BCert.BCERT_CHAIN)
            bo.write_4(0x00000001)
            bo.write_4(total_len)
            bo.write_4(0x00000000)
            bo.write_4(self.cert_cnt)

            for cert in self.certs:
                bo.write_n(cert.body())
            return bo.bytes()

    class Certificate(BCert):
        def __init__(self, bi: Optional["ByteInput"] = None):
            super().__init__(bi.source() if bi else None)
            self.magic = 0
            self.word1 = 0
            self.total_len = 0
            self.cert_len = 0
            self.attributes = []
            self.data = None
            self.names = None
            self.random = None
            self.seclevel = 0
            self.digest = None
            self.uniqueid = None
            self.pubkey_sign = None
            self.pubkey_enc = None
            self.signature = None
            self.signing_key = None
            self.prvkey_sign = None

            if bi:
                start_pos = bi.get_pos()
                self.magic = bi.read_4()
                self.word1 = bi.read_4()
                self.total_len = bi.read_4()
                self.cert_len = bi.read_4()
                len_remaining = self.total_len - 0x10

                while len_remaining > 0:
                    attr = BCert.CertAttr(bi, bi.get_pos() - start_pos)
                    self.attributes.append(attr)
                    len_remaining -= attr.length()

                bi.set_pos(start_pos)
                self.data = bi.read_n(bi.get_pos() - start_pos)

        def verify_signing_key(self):
            if self.prvkey_sign and self.pubkey_sign:
                k = ECC.make_bi(self.prvkey_sign, 0, 0x20)
                pub = ECC.ECPoint(self.pubkey_sign)
                genpoint = ECC.GEN().op_multiply(k)

                if not ECC.on_curve(genpoint):
                    ERR.log("Device cert signing key not on curve")
                if not genpoint.equals(pub):
                    ERR.log("Device cert prv signing key does not match public key")

        def set_names(self, names: List[str]):
            self.names = names

        def set_random(self, random: bytes):
            self.random = random

        def set_seclevel(self, seclevel: int):
            self.seclevel = seclevel

        def set_digest(self, digest: bytes):
            self.digest = digest

        def set_uniqueid(self, uniqueid: bytes):
            self.uniqueid = uniqueid

        def set_prvkey_sign(self, prvkey_sign: bytes):
            self.prvkey_sign = prvkey_sign
            self.verify_signing_key()

        def set_pubkey_sign(self, pubkey_sign: bytes):
            self.pubkey_sign = pubkey_sign
            self.verify_signing_key()

        def set_pubkey_enc(self, pubkey_enc: bytes):
            self.pubkey_enc = pubkey_enc

        def set_signature(self, signature: bytes):
            self.signature = signature

        def set_signing_key(self, signing_key: bytes):
            self.signing_key = signing_key

        def lookup_tag(self, tag: int) -> Optional["CertAttr"]:
            for attr in self.attributes:
                if attr.tag == tag:
                    return attr
            return None

        def print(self, debug: bool):
            pp = Shell.get_pp()
            pp.println("### CERT")
            if debug:
                pp.pad(2, "")
                for attr in self.attributes:
                    attr.print()
                pp.leave()

        # Additional methods (get_random, get_seclevel, get_pubkey_for_signing, etc.)
        # would follow a similar pattern, accessing or calculating attribute data as needed.

        # Placeholder for the body method, replace with the actual implementation
        def body(self) -> bytes:
            # Implement the actual logic for the body method here
            return bytes()

        # Placeholder for the get_signed_data method, replace with actual implementation
        def get_signed_data(self) -> bytes:
            # Implement the actual logic for the get_signed_data method here
            return bytes()
