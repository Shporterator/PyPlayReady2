from modules.xml_utils import XmlUtils
from modules.crypto import Crypto
from modules.padded_printer import PaddedPrinter
from core.blicense import BLicense
from core.device import Device
from io import ByteArrayInputStream


class License:
    def __init__(self, xml_data):
        self.data = xml_data
        self.license_data = None
        self.custom_data = None
        self.content_key = None
        self.UserToken = None
        self.BrandGuid = None
        self.ClientId = None
        self.LicenseType = None
        self.BeginDate = None
        self.ExpirationDate = None
        self.ErrorCode = None
        self.TransactionId = None
        self.blicense = None

        # Parse the main XML data
        self.root = XmlUtils.parse_xml(ByteArrayInputStream(xml_data))
        licresp_node = XmlUtils.select_first(
            self.root,
            "soap:Envelope.soap:Body.AcquireLicenseResponse.AcquireLicenseResult.Response.LicenseResponse"
        )

        if licresp_node is not None:
            license = XmlUtils.get_value(licresp_node, "Licenses.License")
            custom = XmlUtils.get_value(licresp_node, "CustomData")

            try:
                self.license_data = Crypto.base64_decode(license)
                self.custom_data = Crypto.base64_decode(custom)
                self.parse_customdata()
                self.parse_license()
            except Exception as e:
                print(f"Error decoding license data: {e}")

    def parse_customdata(self):
        """Parse custom data fields if custom data is available."""
        if self.custom_data is not None:
            self.custom_root = XmlUtils.parse_xml(ByteArrayInputStream(self.custom_data))
            licresp_cdata_node = XmlUtils.select_first(self.custom_root, "LicenseResponseCustomData")

            if licresp_cdata_node is not None:
                self.UserToken = XmlUtils.get_value(self.custom_root, "UserToken")
                self.BrandGuid = XmlUtils.get_value(self.custom_root, "BrandGuid")
                self.ClientId = XmlUtils.get_value(self.custom_root, "ClientId")
                self.LicenseType = XmlUtils.get_value(self.custom_root, "LicenseType")
                self.BeginDate = XmlUtils.get_value(self.custom_root, "BeginDate")
                self.ExpirationDate = XmlUtils.get_value(self.custom_root, "ExpirationDate")
                self.ErrorCode = XmlUtils.get_value(self.custom_root, "ErrorCode")
                self.TransactionId = XmlUtils.get_value(self.custom_root, "TransactionId")

    def parse_license(self):
        """Initialize BLicense from license data if available."""
        if self.license_data is not None:
            self.blicense = BLicense(self.license_data)

    def get_key_id(self):
        """Retrieve the key ID from the license's content key."""
        ck = self.blicense.get_attr("OuterContainer.KeyMaterialContainer.ContentKey")
        if isinstance(ck, BLicense.ContentKey):
            return ck.key_id()
        return None

    def get_encrypted_data(self):
        """Retrieve the encrypted data from the license's content key."""
        ck = self.blicense.get_attr("OuterContainer.KeyMaterialContainer.ContentKey")
        if isinstance(ck, BLicense.ContentKey):
            return ck.enc_data()
        return None

    def get_content_key(self):
        """Decrypt and return the content key if not already retrieved."""
        if self.content_key is None:
            encrypted_data = self.get_encrypted_data()
            if encrypted_data:
                cur_dev = Device.cur_device()
                plaintext = Crypto.ecc_decrypt(encrypted_data, cur_dev.enc_key().prv())
                self.content_key = plaintext[0x10:0x20]
        return self.content_key

    def print(self):
        """Display the license data."""
        pp = PaddedPrinter(Shell.get_pp())

        pp.println("LICENSE")
        pp.pad(2, "")
        pp.println("CUSTOM DATA")
        pp.pad(2, "")
        pp.println(f"UserToken:       {self.UserToken}")
        pp.println(f"BrandGuid:       {self.BrandGuid}")
        pp.println(f"LicenseType:     {self.LicenseType}")
        pp.println(f"BeginDate:       {self.BeginDate}")
        pp.println(f"ExpirationDate:  {self.ExpirationDate}")
        pp.println(f"ErrorCode:       {self.ErrorCode}")
        pp.println(f"TransactionId:   {self.TransactionId}")
        pp.leave()

        if self.blicense is not None:
            self.blicense.print()

        pp.printhex("content_key", self.get_content_key())
        pp.leave()
