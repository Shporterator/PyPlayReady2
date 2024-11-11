from typing import Optional

class Asset:
    def __init__(self, id: str, sd=None, td=None):
        self.id = id
        self.url = None
        self.ls_url = None
        self.sd = sd  # MP4Builder.StreamsDesc
        self.td = td  # MP4Builder.TimeDesc
        self.ism = None  # ISMManifest
        self.license = None  # License
        
        dir_path = FileCache.asset_dir(id)
        if not Utils.file_exists(dir_path):
            FileCache.make_dirs(id)

    def load_url(self):
        urlfile = FileCache.url_filename(self.id)
        data = Utils.load_file(urlfile)
        if data:
            self.url = data.decode().strip()

    def load_ls_url(self):
        lsurlfile = FileCache.lsurl_filename(self.id)
        data = Utils.load_file(lsurlfile)
        if data:
            self.ls_url = data.decode().strip()

    def get_url(self) -> Optional[str]:
        if self.url is None:
            self.load_url()
        return self.url

    def get_ls_url(self) -> Optional[str]:
        if self.ls_url is None:
            self.load_ls_url()
        return self.ls_url

    def get_manifest(self):
        if self.ism is None:
            manpath = FileCache.manifest_filename(self.id)
            if not Utils.file_exists(manpath):
                curdev = Device.cur_device()
                Shell.println("- downloading manifest")
                CDN.download_content(curdev.get_serial(), self.get_url(), manpath)
            else:
                Shell.println("- loading cached manifest")

            self.ism = ISMManifest.from_file(manpath)
        return self.ism

    def cache_key(self, content_key: bytes):
        keyfile = FileCache.key_filename(self.id)
        keydata = Utils.construct_hex_string(content_key)
        Utils.save_file(keyfile, keydata.encode())

    def get_license(self) -> Optional[License]:
        if self.license is None:
            license_file = FileCache.local_license_filename(self.id)
            if license_file and Utils.file_exists(license_file):
                Shell.println(f"- using local license [{license_file}]")
                license_xml = Utils.load_file(license_file)
                self.license = License(license_xml)
            else:
                curdev = Device.cur_device()
                ism = self.get_manifest()

                if ism:
                    Shell.println("- generating license req")
                    wrmhdr = ism.get_wrmhdr_data()
                    req = MSPR.get_license_request(curdev, wrmhdr)
                    debugfile = FileCache.debug_file(self.id, "lic_req.txt")
                    Utils.save_file(debugfile, req.encode())

                    ls_url = self.get_ls_url()
                    if ls_url:
                        Shell.println(f"- sending license req to: {ls_url}")
                        resp = LS.send_license_req(ls_url, curdev, req)
                        license_xml = resp.encode()
                        debugfile = FileCache.debug_file(self.id, "lic_resp.txt")
                        Utils.save_file(debugfile, license_xml)

                        try:
                            self.license = License(license_xml)
                        except Exception as e:
                            Shell.report_error(f"Cannot parse license, see [{debugfile}] for details: {e}")
                            self.license = None

                        if self.license is None:
                            Shell.report_error(f"Cannot get license, see [{debugfile}] for details")
                else:
                    manpath = FileCache.manifest_filename(self.id)
                    Shell.report_error(f"Invalid asset id or Manifest not present [{manpath}]")

        if self.license is not None:
            self.cache_key(self.license.get_content_key())
        
        return self.license
