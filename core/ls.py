from modules.web import Web
from core.mspr import Device

class LS:
    @staticmethod
    def get_reqprops(dev):
        return [
            "Content-type", "text/xml; charset=utf-8",
            "Mac", dev.get_mac(),
            "Soapaction", "http://schemas.microsoft.com/DRM/2007/03/protocols/AcquireLicense"
        ]

    @staticmethod
    def send_license_req(ls_url, dev, msg):
        return Web.https_post(ls_url, msg, LS.get_reqprops(dev))
