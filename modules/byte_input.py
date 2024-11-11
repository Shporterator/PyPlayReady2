from typing import Optional

class ByteInput:
    def __init__(self, source: Optional[str] = None, data: Optional[bytes] = None):
        self.source = source
        self.data = data or b''
        self.off = 0
        self.le = False  # Little endian flag

    def peek_1(self) -> int:
        return self.data[self.off]

    def read_1(self) -> int:
        res = self.peek_1()
        self.off += 1
        return res

    def peek_2(self) -> int:
        v1 = self.data[self.off] & 0xff
        v2 = self.data[self.off + 1] & 0xff
        return (v2 << 8 | v1) if self.le else (v1 << 8 | v2)

    def read_2(self) -> int:
        res = self.peek_2()
        self.off += 2
        return res

    def peek_4(self) -> int:
        v1 = self.data[self.off] & 0xff
        v2 = self.data[self.off + 1] & 0xff
        v3 = self.data[self.off + 2] & 0xff
        v4 = self.data[self.off + 3] & 0xff
        return (v4 << 24 | v3 << 16 | v2 << 8 | v1) if self.le else (v1 << 24 | v2 << 16 | v3 << 8 | v4)

    def read_4(self) -> int:
        res = self.peek_4()
        self.off += 4
        return res

    def peek_3(self) -> int:
        v1 = self.data[self.off] & 0xff
        v2 = self.data[self.off + 1] & 0xff
        v3 = self.data[self.off + 2] & 0xff
        return (v3 << 16 | v2 << 8 | v1) if self.le else (v1 << 16 | v2 << 8 | v3)

    def read_3(self) -> int:
        res = self.peek_3()
        self.off += 3
        return res

    def peek_8(self) -> int:
        values = [self.data[self.off + i] & 0xff for i in range(8)]
        if self.le:
            values.reverse()
        return sum(v << (8 * i) for i, v in enumerate(reversed(values)))

    def read_8(self) -> int:
        res = self.peek_8()
        self.off += 8
        return res

    def peek_n(self, n: int) -> bytes:
        return self.data[self.off:self.off + n]

    def read_n(self, n: int) -> bytes:
        res = self.peek_n(n)
        self.off += n
        return res

    def read_string(self, maxlen: int) -> str:
        raw_data = self.read_n(maxlen)
        # Find null terminator (if present) to set the string length
        str_data = raw_data.split(b'\x00', 1)[0]
        return str_data.decode('utf-8', errors='ignore')

    def set_pos(self, new_off: int) -> int:
        old_off = self.off
        self.off = new_off
        return old_off

    def get_pos(self) -> int:
        return self.off

    def skip(self, cnt: int):
        self.off += cnt

    def little_endian(self):
        self.le = True

    def big_endian(self):
        self.le = False

    def size(self) -> int:
        return len(self.data) if self.data else 0

    def remaining(self) -> int:
        return max(0, len(self.data) - self.off)

    def remaining_data(self) -> bytes:
        return self.data[self.off:]
