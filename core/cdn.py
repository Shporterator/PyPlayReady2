import time
from modules.crpto import Crypto
from core.ecc import ecc
from modules.vars import Vars
from modules.utils import Utils
from modules.web import Web

class CDN:
    secret = Vars.get_str("VOD_SECRET")

    @staticmethod
    def no_auth() -> bool:
        """
        Check if authentication should be bypassed based on the `CDN_NOAUTH` variable.
        
        Returns:
            bool: True if CDN authentication is disabled, False otherwise.
        """
        return Vars.get_int("CDN_NOAUTH") == 1

    @staticmethod
    def get_secret() -> str:
        """
        Retrieve the secret for generating authorization codes.

        Returns:
            str: The secret key.
        """
        return CDN.secret

    @staticmethod
    def get_time() -> str:
        """
        Get the current Unix time in seconds.

        Returns:
            str: The current time as a string.
        """
        unix_time = int(time.time())
        return str(unix_time)

    @staticmethod
    def get_nbox_code(serial: str, time: str) -> str:
        """
        Generate an nBox authorization code using the serial number, time, and secret.

        Parameters:
            serial (str): The serial number.
            time (str): The current time as a string.

        Returns:
            str: The nBox authorization code.
        """
        magic = f"{serial};{time};{CDN.get_secret()}"
        digest = Crypto.MD5(magic.encode())

        nbox_code = Utils.construct_hex_string(digest)

        if CDN.no_auth():
            # Use a random value for nBox code if no authentication is required
            random = ECC.bi_bytes(ECC.random(128))
            nbox_code = Utils.construct_hex_string(random)

        return nbox_code

    @staticmethod
    def get_reqprops(serial: str) -> list:
        """
        Generate required properties for the request headers.

        Parameters:
            serial (str): The serial number.

        Returns:
            list: A list of key-value pairs for request headers.
        """
        time_value = CDN.get_time()
        return [
            "FriendlyName.dlna.org", "nBox",
            "Range", "bytes=0-",
            "X-nBox-Code", CDN.get_nbox_code(serial, time_value),
            "X-nBox-SerialNumber", serial,
            "X-nBox-Time", time_value
        ]

    @staticmethod
    def download_content(serial: str, url: str, outfile: str) -> int:
        """
        Download content from a URL and save it to a specified file.

        Parameters:
            serial (str): The serial number.
            url (str): The URL of the content.
            outfile (str): The output file path.

        Returns:
            int: The size of the downloaded content.
        """
        return Web.http_get_to_file(url, CDN.get_reqprops(serial), outfile)

    # Uncommented methods below would need definitions in `Web` to function in Python
    # @staticmethod
    # def get_pathinfo(serial: str, url: str) -> Web.PathInfo:
    #     """
    #     Get path information for a URL with request properties.
    #     """
    #     return Web.PathInfo.for_url(url, CDN.get_reqprops(serial))

    # @staticmethod
    # def check_content(serial: str, url: str, outfile: str) -> int:
    #     """
    #     Check content existence by making a HEAD request.
    #     """
    #     return Web.http_head(url, CDN.get_reqprops(serial), outfile)
