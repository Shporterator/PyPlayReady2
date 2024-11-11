import os
from typing import Optional

class Device:
    DEFAULT_SL = MSPR.SL2000
    UNIQUEID_SIZE = 0x10
    MAC_SIZE = 0x06

    group_key = ECC.ECKey.from_file(os.path.join(BCert.BASE_DIR, "z1"))
    curdev = None
    group_cert = None

    def __init__(self, serial: str, mac: str, uniqueid: Optional[bytes] = None):
        self.serial = serial
        self.mac = mac
        self.uniqueid = uniqueid

        if MSPR.fixed_identity():
            self.sign_key = ECC.ECKey(Utils.parse_hex_string("f105e249363781a7c24ebd0bc1ba66642194f26ef2614998932b9bb67fef1337"))
            self.enc_key = ECC.ECKey(Utils.parse_hex_string("d59e783a81ec4159a5089bfa735245421d4847eb4376c297112451a35b3e179d"))
        else:
            self.sign_key = ECC.ECKey()
            self.enc_key = ECC.ECKey()

    @staticmethod
    def revert_serial(serial: str, revert_pos: int) -> str:
        return serial[:revert_pos] + serial[revert_pos:][::-1]

    def get_serial(self) -> str:
        return self.serial

    def get_reverted_serial(self) -> str:
        return self.revert_serial(self.serial, 4)

    def get_mac(self) -> str:
        return self.mac

    def setup_uniqueid(self):
        if len(self.mac) != 2 * self.MAC_SIZE:
            ERR.log(f"Invalid MAC addr length: {len(self.mac)}")
        if len(self.serial) < self.UNIQUEID_SIZE:
            ERR.log(f"Invalid SERIAL length: {len(self.serial)}")

        serial_bytes = self.serial.encode()
        mac_bytes = Utils.parse_hex_string(self.mac)

        tmp = bytearray(self.UNIQUEID_SIZE)
        tmp[:self.UNIQUEID_SIZE] = serial_bytes[:self.UNIQUEID_SIZE]

        for i in range(self.MAC_SIZE):
            tmp[i] ^= mac_bytes[i]

        self.uniqueid = bytearray(self.UNIQUEID_SIZE)
        pos = 0
        self.uniqueid[pos:pos+4] = tmp[:4]
        pos += 4
        self.uniqueid[pos] = ord('C')
        pos += 1
        self.uniqueid[pos:pos+4] = tmp[4:8]
        pos += 4
        self.uniqueid[pos] = ord('A')
        pos += 1
        self.uniqueid[pos:pos+4] = tmp[8:12]
        pos += 4
        self.uniqueid[pos] = ord('D')
        pos += 1
        self.uniqueid[pos] = tmp[12]

    def get_uniqueid(self) -> bytes:
        if self.uniqueid is None:
            self.setup_uniqueid()
        return bytes(self.uniqueid)

    def sign_key(self) -> ECC.ECKey:
        return self.sign_key

    def enc_key(self) -> ECC.ECKey:
        return self.enc_key

    def print(self):
        pp = Shell.get_pp()
        pp.println("Device")
        pp.pad(2, "")
        pp.println(f"serial: {self.get_serial()}")
        pp.println(f"mac:    {self.get_mac()}")
        pp.printhex("uniqueid", self.get_uniqueid())
        self.sign_key.print("sign key")
        self.enc_key.print("enc key")
        pp.leave()

    @staticmethod
    def gen_fake_group_cert():
        root_sign_key = ECC.ECKey()
        for i in range(Device.group_cert.cert_cnt() - 1, -1, -1):
            cert = Device.group_cert.get(i)
            cert_sign_key = ECC.ECKey()
            cert.sign(root_sign_key, cert_sign_key)
            root_sign_key = cert_sign_key
        Device.group_key = root_sign_key

    @staticmethod
    def get_group_cert() -> BCert.CertificateChain:
        print("Device.get_group_cert")
        if Device.group_cert is None:
            Device.group_cert = BCert.from_file("g1")
            if Vars.get_int("MSPR_FAKE_ROOT") == 1:
                Device.gen_fake_group_cert()
                Device.group_cert.save("fakechain")
        return Device.group_cert

    @staticmethod
    def get_group_prvkey() -> int:
        return Device.group_key.prv()

    @staticmethod
    def get_group_pubkey() -> ECC.ECPoint:
        return Device.group_key.pub()

    @staticmethod
    def changed() -> bool:
        serial = Vars.get_str("SERIAL")
        mac = Vars.get_str("MAC")
        if Device.curdev:
            if Device.curdev.get_serial() != serial or Device.curdev.get_mac() != mac:
                return True
        else:
            return True
        return False

    def get_cert(self) -> BCert.Certificate:
        if (self.cert is None or self.changed() or
           (self.cert is not None and self.cert.get_seclevel() != self.cur_SL())):
            self.cert = BCert.Certificate()
            Shell.out.println("generating new cert, device changed or not initialized")
            if MSPR.fixed_identity():
                random = Utils.parse_hex_string("bee27cbf64aac0c94cd60ff28a05e1b4")
            else:
                random = ECC.bi_bytes(ECC.random(128))
            self.cert.set_random(random)
            self.cert.set_seclevel(self.cur_SL())
            self.cert.set_uniqueid(self.get_uniqueid())
            self.cert.set_prvkey_sign(self.sign_key.prv_bytes())
            self.cert.set_pubkey_sign(self.sign_key.pub_bytes())
            self.cert.set_pubkey_enc(self.enc_key.pub_bytes())
        return self.cert

    def get_cert_chain(self) -> BCert.CertificateChain:
        print("Device.get_cert_chain")
        if (self.cert_chain is None or self.changed() or
           (self.cert is not None and self.cert.get_seclevel() != self.cur_SL())):
            if MSPR.fixed_identity():
                r = ECC.make_bi(Utils.reverse_hex_string("062dd035241da79eedbc2abc9d99ab5b159788bb78d56aedcc3b603018ec02f7"))
                ECC.set_random(r)
            gcert = self.get_group_cert()
            print(f"gcert {gcert}")
            self.cert_chain = gcert.insert(self.get_cert())
            self.cert_chain.save("genchain")
        return self.cert_chain

    @staticmethod
    def cur_device() -> "Device":
        if Device.changed() or (Device.curdev and Device.curdev.get_cert().get_seclevel() != Device.cur_SL()):
            serial = Vars.get_str("SERIAL")
            mac = Vars.get_str("MAC")
            Device.curdev = Device(serial, mac)
        return Device.curdev
