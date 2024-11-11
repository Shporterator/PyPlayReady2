import os
import sys
import binascii
import datetime
from typing import List, Optional

class Utils:
    LINESIZE = 16
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890!@#$%^&*()_+-={}[]|:\";',.<>?/"

    @staticmethod
    def parse_hex_value(s: str) -> int:
        try:
            return int(s, 16)
        except ValueError:
            return -1

    @staticmethod
    def int_value(s: str) -> int:
        try:
            return int(s)
        except ValueError:
            return -1

    @staticmethod
    def long_value(s: str) -> int:
        try:
            return int(s)
        except ValueError:
            return -1

    @staticmethod
    def hex_value(val: int, max_len: int) -> str:
        hex_str = hex(val)[2:].zfill(max_len)
        return hex_str[-max_len:]

    @staticmethod
    def char_value(c: str) -> str:
        return c if c in Utils.allowed_chars else "."

    @staticmethod
    def padded_int(val: int, max_len: int) -> str:
        return str(val).zfill(max_len)[-max_len:]

    @staticmethod
    def padded_string(s: str, space: int) -> str:
        return s.ljust(space) if len(s) < space else s[-space:]

    @staticmethod
    def pad(cnt: int, ch: str = " ") -> str:
        return ch * cnt

    @staticmethod
    def padded_string_left(s: str, space: int) -> str:
        return s.rjust(space) if len(s) < space else s[-space:]

    @staticmethod
    def parse_hex_string(s: str) -> bytes:
        s = s.zfill(len(s) + len(s) % 2)  # Ensure even length
        try:
            return bytes.fromhex(s)
        except ValueError:
            return b""

    @staticmethod
    def construct_hex_string(buf: bytes) -> str:
        return ''.join(f'{b:02x}' for b in buf)

    @staticmethod
    def outputln(line: str):
        Shell.println(line)  # Assuming Shell class is defined elsewhere

    @staticmethod
    def output_buf(s: Optional[str], data: bytes):
        if s:
            Shell.print(f"{s}: ")
        for byte in data:
            Shell.print(f"{Utils.hex_value(byte & 0xff, 2)} ")
        Shell.println("")

    @staticmethod
    def print_line(pad: int, addr: int, tab: bytes, pos: int):
        line = Utils.pad(pad) + Utils.hex_value(addr + pos, 4) + ": "
        size = min(len(tab) - pos, Utils.LINESIZE)
        
        # Hex display
        line += " ".join(Utils.hex_value(tab[i] & 0xff, 2) for i in range(pos, pos + size))
        line += "   " * (Utils.LINESIZE - size) + "  "
        
        # ASCII display
        line += ''.join(Utils.char_value(chr(tab[i])) for i in range(pos, pos + size))
        
        Utils.outputln(line)

    @staticmethod
    def print_mem(pad: int, addr: int, tab: bytes):
        pos = 0
        while pos < len(tab):
            Utils.print_line(pad, addr, tab, pos)
            pos += Utils.LINESIZE

    @staticmethod
    def print_buf(pad: int, s: str, tab: bytes):
        Utils.outputln(Utils.pad(pad) + s)
        Utils.print_mem(pad + 2, 0, tab)

    @staticmethod
    def tokenize(s: str, token: str) -> List[str]:
        return s.strip().split(token)

    @staticmethod
    def reverse(data: bytes) -> bytes:
        return data[::-1]

    @staticmethod
    def reverse_hex_string(s: str) -> str:
        data = Utils.parse_hex_string(s)
        return Utils.construct_hex_string(Utils.reverse(data))

    @staticmethod
    def load_file(path: str) -> Optional[bytes]:
        try:
            with open(path, 'rb') as f:
                return f.read()
        except (IOError, FileNotFoundError):
            return None

    @staticmethod
    def load_text_file(path: str) -> Optional[str]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().replace('\n', '')
        except (IOError, FileNotFoundError):
            return None

    @staticmethod
    def save_file(path: str, data: bytes) -> bool:
        try:
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except IOError:
            return False

    @staticmethod
    def long2date(val: int) -> str:
        try:
            base_date = datetime.datetime(1904, 1, 1, tzinfo=datetime.timezone.utc)
            date = base_date + datetime.timedelta(seconds=val)
            return date.strftime('%Y/%m/%d %I:%M %p')
        except Exception:
            return ""

    @staticmethod
    def date2long(sdate: str) -> int:
        try:
            base_date = datetime.datetime(1904, 1, 1, tzinfo=datetime.timezone.utc)
            date = datetime.datetime.strptime(sdate, '%Y/%m/%d %I:%M:%S %p').replace(tzinfo=datetime.timezone.utc)
            return int((date - base_date).total_seconds())
        except Exception:
            return -1

    @staticmethod
    def current_date() -> int:
        try:
            base_date = datetime.datetime(1904, 1, 1, tzinfo=datetime.timezone.utc)
            current_date = datetime.datetime.now(datetime.timezone.utc)
            return int((current_date - base_date).total_seconds())
        except Exception:
            return -1

    @staticmethod
    def mkdir(dir_path: str) -> bool:
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def file_exists(filename: str) -> bool:
        return os.path.isfile(filename)
