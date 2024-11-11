from io import ByteArrayInputStream
from modules.crypto import Crypto
from modules.xml_utils import XmlUtils
from modules.padded_printer import PaddedPrinter
from modules.shell import Shell

class WRMHeader:
    def __init__(self, data: bytes) -> None:
        """
        Initialize WRMHeader with data, parsing XML to retrieve values.

        Parameters:
        - data (bytes): The WRMHeader XML data in bytes.
        """
        self.data = data
        self.root = XmlUtils.parse_xml(ByteArrayInputStream(data))

        # Initialize fields
        self.keylen = XmlUtils.get_value(self.root, "WRMHEADER.DATA.PROTECTINFO.KEYLEN") or None
        self.algid = XmlUtils.get_value(self.root, "WRMHEADER.DATA.PROTECTINFO.ALGID") or None

        kid_val = XmlUtils.get_value(self.root, "WRMHEADER.DATA.KID")
        self.kid = Crypto.base64_decode(kid_val) if kid_val else None

        self.la_url = XmlUtils.get_value(self.root, "WRMHEADER.DATA.LA_URL") or None

        ds_id_val = XmlUtils.get_value(self.root, "WRMHEADER.DATA.DS_ID")
        self.ds_id = Crypto.base64_decode(ds_id_val) if ds_id_val else None

    def keylen(self) -> str:
        return self.keylen

    def algid(self) -> str:
        return self.algid

    def kid(self) -> bytes:
        return self.kid

    def la_url(self) -> str:
        return self.la_url

    def ds_id(self) -> bytes:
        return self.ds_id

    def print(self) -> None:
        """
        Prints the WRMHeader's parsed information.
        """
        pp = Shell.get_pp()
        pp.println("WRMHEADER")
        pp.pad(2, "")

        pp.println(f"keylen: {self.keylen}")
        pp.println(f"algid:  {self.algid}")
        pp.printhex("kid", self.kid)
        pp.println(f"la_url: {self.la_url}")
        pp.printhex("ds_id: ", self.ds_id)

        pp.leave()
