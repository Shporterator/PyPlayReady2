from typing import List, Optional, Union

class BLicense:
    MAGIC_XMR = 0x584d5200
    ATTR_HDR_SIZE = 8

    TAG_OuterContainer = 0x0001
    TAG_GlobalPolicy = 0x0002
    TAG_PlaybackPolicy = 0x0004
    TAG_PlayEnabler = 0x0036
    TAG_PlayEnablerType = 0x0039
    TAG_DomainRestriction = 0x0029
    TAG_IssueDate = 0x0013
    TAG_RevInfoVersion = 0x0032
    TAG_SecurityLevel = 0x0034
    TAG_EmbeddedLicenseSettings = 0x0033
    TAG_KeyMaterialContainer = 0x0009
    TAG_ContentKey = 0x000A
    TAG_ECCKey = 0x002A
    TAG_XMRSignature = 0x000B
    TAG_RightsSettingObject = 0x000D
    TAG_OutputProtectionLevelRestriction = 0x0005
    TAG_ExpirationRestriction = 0x0012
    TAG_RealTimeExpirationRestriction = 0x0055
    TAG_UplinkKIDObject = 0x003B
    TAG_ExplicitDigitalVideoOutputProtection = 0x0058
    TAG_DigitalVideoOutputRestriction = 0x0059
    TAG_ExplicitDigitalAudioOutputProtection = 0x002E
    TAG_DigitalAudioOutputRestriction = 0x0031
    TAG_SecureStopRestriction = 0x005A
    TAG_ExpirationAfterFirstPlayRestriction = 0x0030
    TAG_RemovalDateObject = 0x0050
    TAG_GracePeriodObject = 0x001A
    TAG_SourceIdObject = 0x0022
    TAG_MeteringRestrictionObject = 0x0016
    TAG_PolicyMetadataObject = 0x002C
    TAG_ExplicitAnalogVideoOutputProtectionContainer = 0x0007
    TAG_AnalogVideoOutputConfigurationRestriction = 0x0008
    TAG_AuxiliaryKeyObject = 0x0051
    TAG_UplinkKeyObject3 = 0x0052
    TAG_CopyObject = 0x003C
    TAG_CopyEnablerContainerObject = 0x0038
    TAG_CopyEnablerObject = 0x003A
    TAG_CopyCountRestrictionObject = 0x003D
    TAG_MoveObject = 0x0037
    TAG_ReadContainerObject = 0x0041
    TAG_ExecuteContainerObject = 0x003F
    TAG_RestrictedSourceIdObject = 0x0028
    TAG_ROOT_CONTAINER = 0x7fff

    def __init__(self, data: bytes):
        self.data = data
        self.version = 0
        self.unknown_data = None
        self.root = None

        bi = ByteInput(data)
        magic = bi.read_4()

        if magic == BLicense.MAGIC_XMR:
            self.version = bi.read_4()
            self.unknown_data = bi.read_n(0x10)
            self.root = ContainerAttr.get(BLicense.TAG_ROOT_CONTAINER, bi.remaining_data())

    @staticmethod
    def tag_name(tag: int) -> str:
        tags = {
            BLicense.TAG_OuterContainer: "OuterContainer",
            BLicense.TAG_GlobalPolicy: "GlobalPolicy",
            BLicense.TAG_PlaybackPolicy: "PlaybackPolicy",
            BLicense.TAG_PlayEnabler: "PlayEnabler",
            # Define all tag names similarly as in the Java code.
            # ... other tags
        }
        return tags.get(tag, "Unknown")

    @staticmethod
    def read_attributes(data: bytes) -> List["BLicense.Attr"]:
        attributes = []
        bi = ByteInput(data)
        len_remaining = len(data)

        while len_remaining > 0:
            bi.skip(2)
            tag = bi.peek_2()
            bi.skip(-2)

            attr = BLicense.Attr(bi)
            attributes.append(attr)

            len_remaining -= attr.len() + BLicense.ATTR_HDR_SIZE

        return attributes

    class Attr:
        def __init__(self, bi: "ByteInput"):
            self.lvl = bi.read_2()
            self.tag = bi.read_2()
            self.len = bi.read_4()
            self.data = bi.read_n(self.len - 8)
            self.name = BLicense.tag_name(self.tag)

        @staticmethod
        def parse(attr: "BLicense.Attr") -> Union["BLicense.Attr", "BLicense.SecurityLevel", "BLicense.ContentKey", "BLicense.ContainerAttr"]:
            if attr.tag == BLicense.TAG_SecurityLevel:
                return BLicense.SecurityLevel.get(attr.data)
            elif attr.tag == BLicense.TAG_ContentKey:
                return BLicense.ContentKey.get(attr.data)
            elif attr.tag in (BLicense.TAG_OuterContainer, BLicense.TAG_KeyMaterialContainer, BLicense.TAG_ExplicitAnalogVideoOutputProtectionContainer):
                return BLicense.ContainerAttr.get(attr.tag, attr.data)
            return attr

        def print(self):
            pp = Shell.get_pp()
            pp.println(f"attr: {Utils.hex_value(self.tag, 4)} {self.name}")
            if self.data:
                pp.printhex("data", self.data)

    class SecurityLevel(Attr):
        def __init__(self, data: bytes):
            super().__init__(len(data), BLicense.TAG_SecurityLevel, data)
            bi = ByteInput(data)
            self.security_level = bi.read_2()

        @staticmethod
        def get(data: bytes) -> "BLicense.SecurityLevel":
            return BLicense.SecurityLevel(data)

        def print(self):
            pp = Shell.get_pp()
            pp.println("SecurityLevel")
            pp.pad(2, "")
            pp.println(f"level: {MSPR.SL2string(self.security_level)}")
            pp.leave()

    class ContentKey(Attr):
        def __init__(self, data: bytes):
            super().__init__(len(data), BLicense.TAG_ContentKey, data)
            bi = ByteInput(data)
            self.key_id = bi.read_n(0x10)
            self.v1 = bi.read_2()
            self.v2 = bi.read_2()
            self.enc_data_len = bi.read_2()
            self.enc_data = bi.read_n(self.enc_data_len)

        @staticmethod
        def get(data: bytes) -> "BLicense.ContentKey":
            return BLicense.ContentKey(data)

        def print(self):
            pp = Shell.get_pp()
            pp.println("ContentKey")
            pp.pad(2, "")
            pp.printhex("key_id", self.key_id)
            pp.println(f"v1: {self.v1}")
            pp.println(f"v2: {self.v2}")
            pp.println(f"enc_data_len: {Utils.hex_value(self.enc_data_len, 4)}")
            pp.printhex("enc_data", self.enc_data)
            pp.leave()

    class ContainerAttr(Attr):
        def __init__(self, data: bytes, attributes: Optional[List["BLicense.Attr"]] = None):
            super().__init__(len(data), BLicense.TAG_ROOT_CONTAINER, data)
            self.attributes = attributes or []

        def add_attr(self, attr: "BLicense.Attr"):
            self.attributes.append(attr)

        def lookup_attr_by_name(self, name: str) -> Optional["BLicense.Attr"]:
            for attr in self.attributes:
                if attr.name == name:
                    return attr
            return None

        @staticmethod
        def get(tag: int, data: bytes) -> Optional[Union["BLicense.Attr", "BLicense.ContainerAttr"]]:
            attributes = BLicense.read_attributes(data)
            if len(attributes) == 1 and tag != BLicense.TAG_ROOT_CONTAINER:
                return BLicense.Attr.parse(attributes[0])
            else:
                container = BLicense.ContainerAttr(data, attributes=[])
                for attr in attributes:
                    container.add_attr(BLicense.Attr.parse(attr))
                return container

        def print(self):
            pp = Shell.get_pp()
            if self.tag != BLicense.TAG_ROOT_CONTAINER:
                pp.println(f"attr: {Utils.hex_value(self.tag, 4)} {self.name}")
            pp.pad(2, "")
            for attr in self.attributes:
                attr.print()
            pp.leave()

    @staticmethod
    def tokenize_path(path: str) -> List[str]:
        return Utils.tokenize(path, ".")

    def get_attr(self, attrpath: str) -> Optional["BLicense.Attr"]:
        path_elem = BLicense.tokenize_path(attrpath)
        curpos = self.root
        res = None

        for elem in path_elem:
            if isinstance(curpos, BLicense.ContainerAttr):
                res = curpos.lookup_attr_by_name(elem)
            if res is None:
                break
            curpos = res

        return res

    def print(self):
        pp = Shell.get_pp()
        pp.println("XMR LICENSE")
        pp.pad(1, "")
        pp.println(f"version: {self.version}")
        self.root.print()
        pp.leave()
