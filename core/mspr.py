import base64
import time
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Util.Padding import pad, unpad
from modules.utils import Utils
from modules.error import ERR
from modules.crypto import Crypto
from modules.padded_printer import PaddedPrinter
from modules.shell import Shell
from modules.vars import Vars
from core.device import Device
from core.bcert import BCert

class MSPR:
    WMRMECC256PubKey = "C8B6AF16EE941AADAA5389B4AF2C10E356BE42AF175EF3FACE93254E7B0B3D9B982B27B5CB2341326E56AA857DBFD5C634CE2CF9EA74FCA8F2AF5957EFEEA562"

    # Security levels for devices/content access
    SL150 = 150
    SL2000 = 2000
    SL3000 = 3000

    GROUP_CERT = "g1"
    GROUP_CERT_PRV_KEY = "z1"

    AES_KEY_SIZE = 16
    NONCE_SIZE = 16

    xmlkey = None
    WMRMpubkey = ECC.construct(curve="P-256", point_x=int(WMRMECC256PubKey[:64], 16), point_y=int(WMRMECC256PubKey[64:], 16))

    @staticmethod
    def fixed_identity():
        return Vars.get_int("MSPR_DEBUG") == 1

    @staticmethod
    def SL2string(level):
        return {MSPR.SL150: "SL150", MSPR.SL2000: "SL2000", MSPR.SL3000: "SL3000"}.get(level, str(level))

    @staticmethod
    def string2SL(s):
        return {"SL150": MSPR.SL150, "SL2000": MSPR.SL2000, "SL3000": MSPR.SL3000}.get(s, -1)

    class XmlKey:
        def __init__(self):
            self.shared_point = ECC.generate(curve="P-256")
            self.shared_key = self.shared_point.pointQ.x
            self.aes_iv = None
            self.aes_key = None

        def pub(self):
            return self.shared_point.public_key().export_key(format="DER")

        def prv(self):
            return self.shared_point.d

        def setup_aes_key(self):
            shared_data = self.shared_key.to_bytes(32, 'big')
            self.aes_iv = shared_data[:MSPR.AES_KEY_SIZE]
            self.aes_key = shared_data[MSPR.AES_KEY_SIZE:MSPR.AES_KEY_SIZE * 2]

        def set_aes_iv(self, iv):
            if len(iv) != MSPR.AES_KEY_SIZE:
                ERR.log("Invalid AES IV length")
            self.aes_iv = iv

        def set_aes_key(self, key):
            if len(key) != MSPR.AES_KEY_SIZE:
                ERR.log("Invalid AES key length")
            self.aes_key = key

        def aes_iv(self):
            if self.aes_iv is None:
                self.setup_aes_key()
            return self.aes_iv

        def aes_key(self):
            if self.aes_key is None:
                self.setup_aes_key()
            return self.aes_key

        def print(self):
            pp = Shell.get_pp()
            pp.println("XML key (AES/CBC)")
            pp.pad(2, "")
            pp.printhex("iv ", self.aes_iv)
            pp.printhex("key", self.aes_key)
            pp.leave()

        def bytes(self):
            return self.aes_iv + self.aes_key

    @staticmethod
    def getXmlKey():
        if MSPR.xmlkey is None:
            MSPR.xmlkey = MSPR.XmlKey()
        return MSPR.xmlkey

    @staticmethod
    def XML_HEADER_START():
        return (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        )

    @staticmethod
    def SOAP_BODY_START():
        return "<soap:Body>"

    @staticmethod
    def ACQUIRE_LICENSE_HEADER_START():
        return (
            '<AcquireLicense xmlns="http://schemas.microsoft.com/DRM/2007/03/protocols">'
            '<challenge><Challenge xmlns="http://schemas.microsoft.com/DRM/2007/03/protocols/messages">'
        )

    @staticmethod
    def LA_HEADER_START():
        return (
            '<LA xmlns="http://schemas.microsoft.com/DRM/2007/03/protocols" Id="SignedData" xml:space="preserve">'
            '<Version>1</Version>'
        )

    @staticmethod
    def CONTENT_HEADER(wrmheader):
        return f"<ContentHeader>{wrmheader}</ContentHeader>"

    @staticmethod
    def CLIENT_INFO():
        return (
            "<CLIENTINFO><CLIENTVERSION>10.0.16384.10011</CLIENTVERSION></CLIENTINFO>"
            "<RevocationLists>"
            "<RevListInfo><ListID>ioydTlK2p0WXkWklprR5Hw==</ListID><Version>0</Version></RevListInfo>"
            "<RevListInfo><ListID>gC4IKKPHsUCCVhnlttibJw==</ListID><Version>0</Version></RevListInfo>"
            "<RevListInfo><ListID>Ef/RUojT3U6Ct2jqTCChbA==</ListID><Version>0</Version></RevListInfo>"
            "<RevListInfo><ListID>BOZ1zT1UnEqfCf5tJOi/kA==</ListID><Version>0</Version></RevListInfo>"
            "</RevocationLists>"
        )

    @staticmethod
    def LICENSE_NONCE(nonce):
        return f"<LicenseNonce>{nonce}</LicenseNonce><ClientTime>{int(time.time())}</ClientTime>"

    @staticmethod
    def ENCRYPTED_DATA_START():
        return (
            '<EncryptedData xmlns="http://www.w3.org/2001/04/xmlenc#" Type="http://www.w3.org/2001/04/xmlenc#Element">'
            '<EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes128-cbc"></EncryptionMethod>'
        )

    @staticmethod
    def KEY_INFO(keydata):
        return (
            '<KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">'
            '<EncryptedKey xmlns="http://www.w3.org/2001/04/xmlenc#">'
            '<EncryptionMethod Algorithm="http://schemas.microsoft.com/DRM/2007/03/protocols#ecc256"></EncryptionMethod>'
            '<KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><KeyName>WMRMServer</KeyName></KeyInfo>'
            '<CipherData><CipherValue>'
            f'{keydata}'
            '</CipherValue></CipherData></EncryptedKey></KeyInfo>'
        )

    @staticmethod
    def CIPHER_DATA(cipherdata):
        return f"<CipherData><CipherValue>{cipherdata}</CipherValue></CipherData>"

    @staticmethod
    def build_digest_content(wrmheader, nonce, keydata, cipherdata):
        return (
            MSPR.LA_HEADER_START()
            + MSPR.CONTENT_HEADER(wrmheader)
            + MSPR.CLIENT_INFO()
            + MSPR.LICENSE_NONCE(nonce)
            + MSPR.ENCRYPTED_DATA_START()
            + MSPR.KEY_INFO(keydata)
            + MSPR.CIPHER_DATA(cipherdata)
            + MSPR.ENCRYPTED_DATA_END()
            + MSPR.LA_HEADER_END()
        )

    @staticmethod
    def SIGNATURE_START():
        return '<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">'

    @staticmethod
    def SIGNATURE(signature):
        return f"<SignatureValue>{signature}</SignatureValue>"

    @staticmethod
    def PUBLIC_KEY(pubkey):
        return (
            '<KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">'
            '<KeyValue><ECCKeyValue><PublicKey>'
            f'{pubkey}'
            '</PublicKey></ECCKeyValue></KeyValue></KeyInfo>'
        )

    @staticmethod
    def SIGNATURE_END():
        return "</Signature>"

    @staticmethod
    def ENCRYPTED_DATA_END():
        return "</EncryptedData>"

    @staticmethod
    def build_signature(dev, data):
        pp = Shell.get_pp()
        cert = dev.get_cert()
        prvkey_sign = cert.get_prvkey_for_signing()
        signature_bytes = Crypto.ecdsa(data.encode(), prvkey_sign)
        signature = base64.b64encode(signature_bytes).decode()
        pubkey_sign = cert.get_pubkey_for_signing()
        pubkey = base64.b64encode(pubkey_sign).decode()
        pp.println("XML SIGNATURE")
        pp.pad(2, "")
        pp.println(signature)
        pp.leave()
        pp.println("PUBKEY")
        pp.pad(2, "")
        pp.println(pubkey)
        pp.leave()
        return MSPR.SIGNATURE(signature) + MSPR.PUBLIC_KEY(pubkey) + MSPR.SIGNATURE_END()

    # Additional methods and internal methods for handling cryptographic operations...
