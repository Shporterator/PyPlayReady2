import sys
from io import TextIOWrapper
import locale

class Shell:
    # Set up encoding to support specific characters
    CODE_PAGE = "cp852"
    
    # Using the appropriate character encoding for Polish characters
    CHARSET = locale.getpreferredencoding()
    out = TextIOWrapper(sys.stdout.buffer, encoding=CODE_PAGE, write_through=True)
    
    pp = None

    @classmethod
    def get_output(cls):
        return cls.out

    @staticmethod
    def report_error(err: str):
        print(f"error: {err}", file=sys.stderr)

    @classmethod
    def print(cls, line: str):
        cls.get_output().write(line)
        cls.get_output().flush()

    @classmethod
    def println(cls, line: str):
        cls.get_output().write(line + "\n")
        cls.get_output().flush()

    @classmethod
    def get_pp(cls):
        if cls.pp is None:
            cls.pp = PaddedPrinter.getInstance()
        return cls.pp
