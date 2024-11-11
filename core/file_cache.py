import os

class FileCache:
    DEFAULT_CACHE_DIR = "content"
    URL_FILE = "url.txt"
    LS_FILE = "ls.txt"
    KEY_FILE = "key.txt"
    VIDEO_DIR = "video"
    AUDIO_DIR = "audio"
    QUALITY_DIR = "q"
    DEBUG_DIR = "debug"
    TMP_DIR = "tmp"
    MANIFEST_FILE = "Manifest.ism"
    INFO_FILE = "Info.json"
    MP4_FILE = "movie.mp4"

    @staticmethod
    def content_dir() -> str:
        cache_dir = Vars.get_str("CONTENT_DIR")
        if cache_dir is None:
            cache_dir = FileCache.DEFAULT_CACHE_DIR
        return cache_dir

    @staticmethod
    def tmp_dir() -> str:
        return os.path.join(FileCache.content_dir(), FileCache.TMP_DIR)

    @staticmethod
    def asset_dir(assetname: str) -> str:
        return os.path.join(FileCache.content_dir(), assetname)

    @staticmethod
    def audio_dir(assetname: str, audioname: str = None) -> str:
        if audioname:
            return os.path.join(FileCache.asset_dir(assetname), FileCache.AUDIO_DIR, audioname)
        return os.path.join(FileCache.asset_dir(assetname), FileCache.AUDIO_DIR)

    @staticmethod
    def audio_qdir(assetname: str, audioname: str, quality: str) -> str:
        return os.path.join(FileCache.audio_dir(assetname, audioname), FileCache.QUALITY_DIR + quality)

    @staticmethod
    def debug_dir(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.DEBUG_DIR)

    @staticmethod
    def debug_file(assetname: str, debugfile: str) -> str:
        dir = FileCache.debug_dir(assetname)
        Utils.mkdir(dir)
        return os.path.join(dir, debugfile)

    @staticmethod
    def manifest_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.MANIFEST_FILE)

    @staticmethod
    def info_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.INFO_FILE)

    @staticmethod
    def url_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.URL_FILE)

    @staticmethod
    def lsurl_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.LS_FILE)

    @staticmethod
    def key_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.KEY_FILE)

    @staticmethod
    def local_license_filename(assetname: str) -> Optional[str]:
        local_license = Vars.get_str("MSPR_LOCAL_LICENSE")
        if local_license:
            return os.path.join(FileCache.asset_dir(assetname), local_license)
        return None

    @staticmethod
    def mp4_filename(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.MP4_FILE)

    @staticmethod
    def audio_filename(assetname: str, audioname: str, quality: str, idx: int) -> str:
        return os.path.join(FileCache.audio_qdir(assetname, audioname, quality), str(idx))

    @staticmethod
    def video_dir(assetname: str) -> str:
        return os.path.join(FileCache.asset_dir(assetname), FileCache.VIDEO_DIR)

    @staticmethod
    def video_qdir(assetname: str, quality: str) -> str:
        return os.path.join(FileCache.video_dir(assetname), FileCache.QUALITY_DIR + quality)

    @staticmethod
    def video_filename(assetname: str, quality: str, idx: int) -> str:
        return os.path.join(FileCache.video_qdir(assetname, quality), str(idx))

    @staticmethod
    def tmp_filename(name: str) -> str:
        return os.path.join(FileCache.tmp_dir(), name)

    @staticmethod
    def make_dirs(assetname: str, audioname: Optional[str] = None, aquality: Optional[str] = None, vquality: Optional[str] = None):
        tmpdir = FileCache.tmp_dir()
        Utils.mkdir(tmpdir)

        adir = FileCache.audio_dir(assetname)
        vdir = FileCache.video_dir(assetname)
        ddir = FileCache.debug_dir(assetname)

        Utils.mkdir(adir)
        Utils.mkdir(vdir)
        Utils.mkdir(ddir)

        if audioname and aquality:
            aqdir = FileCache.audio_qdir(assetname, audioname, aquality)
            Utils.mkdir(aqdir)

        if vquality:
            vqdir = FileCache.video_qdir(assetname, vquality)
            Utils.mkdir(vqdir)

    @staticmethod
    def fragment_exists(assetid: str, audio_name: str, audio_quality: str, video_quality: str, idx: int) -> bool:
        vfragpath = FileCache.video_filename(assetid, video_quality, idx)
        afragpath = FileCache.audio_filename(assetid, audio_name, audio_quality, idx)
        return Utils.file_exists(afragpath) and Utils.file_exists(vfragpath)
