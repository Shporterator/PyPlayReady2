from typing import Optional

class ByteOutput:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = bytearray(capacity)
        self.off = 0
        self.len = 0
        self.le = False  # Little-endian flag

    def in_range(self, pos: int, length: int) -> bool:
        return pos < self.capacity and (pos + length) < self.capacity

    def extend_capacity(self):
        new_capacity = 2 * self.capacity
        new_data = bytearray(new_capacity)
        new_data[:self.capacity] = self.data
        self.capacity = new_capacity
        self.data = new_data

    def check_space(self, length: int):
        while not self.in_range(self.off, length):
            self.extend_capacity()

    def set_len(self, pos: int):
        if self.off > self.len:
            self.len = self.off

    def write_1(self, val: int):
        self.check_space(1)
        self.data[self.off] = val & 0xff
        self.off += 1
        self.set_len(self.off)

    def write_2(self, val: int):
        self.check_space(2)
        b1 = (val >> 8) & 0xff
        b2 = val & 0xff
        if self.le:
            self.data[self.off:self.off + 2] = bytes([b2, b1])
        else:
            self.data[self.off:self.off + 2] = bytes([b1, b2])
        self.off += 2
        self.set_len(self.off)

    def write_3(self, val: int):
        self.check_space(3)
        b1 = (val >> 16) & 0xff
        b2 = (val >> 8) & 0xff
        b3 = val & 0xff
        if self.le:
            self.data[self.off:self.off + 3] = bytes([b3, b2, b1])
        else:
            self.data[self.off:self.off + 3] = bytes([b1, b2, b3])
        self.off += 3
        self.set_len(self.off)

    def write_4(self, val: int):
        self.check_space(4)
        b1 = (val >> 24) & 0xff
        b2 = (val >> 16) & 0xff
        b3 = (val >> 8) & 0xff
        b4 = val & 0xff
        if self.le:
            self.data[self.off:self.off + 4] = bytes([b4, b3, b2, b1])
        else:
            self.data[self.off:self.off + 4] = bytes([b1, b2, b3, b4])
        self.off += 4
        self.set_len(self.off)

    def write_8(self, val: int):
        self.check_space(8)
        b = [(val >> (8 * i)) & 0xff for i in range(8)]
        if not self.le:
            b.reverse()
        self.data[self.off:self.off + 8] = bytes(b)
        self.off += 8
        self.set_len(self.off)

    def write_n(self, bytes_data: bytes):
        n = len(bytes_data)
        self.check_space(n)
        self.data[self.off:self.off + n] = bytes_data
        self.off += n
        self.set_len(self.off)

    def write_string(self, s: str):
        self.write_n(s.encode('utf-8'))
        self.write_1(0)  # Null terminator

    def write_zero(self, count: int):
        self.check_space(count)
        for _ in range(count):
            self.write_1(0)

    def set_pos(self, new_off: int) -> int:
        old_off = self.off
        self.off = new_off
        return old_off

    def get_pos(self) -> int:
        return self.off

    def length(self) -> int:
        return self.len

    def skip(self, count: int):
        self.off += count

    def little_endian(self):
        self.le = True

    def big_endian(self):
        self.le = False

    def bytes(self) -> bytes:
        return bytes(self.data[:self.len])
