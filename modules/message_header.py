from typing import Optional, Iterator, List, Dict
from io import StringIO
from collections import defaultdict
import re

class MessageHeader:
    def __init__(self, stream: Optional[StringIO] = None):
        self.keys: List[Optional[str]] = []
        self.values: List[Optional[str]] = []
        self.nkeys = 0
        if stream:
            self.parse_header(stream)

    def get_header_names_in_list(self) -> str:
        return ",".join([key for key in self.keys if key is not None])

    def reset(self):
        self.keys = []
        self.values = []
        self.nkeys = 0

    def find_value(self, key: Optional[str]) -> Optional[str]:
        if key is None:
            for i in range(self.nkeys - 1, -1, -1):
                if self.keys[i] is None:
                    return self.values[i]
        else:
            for i in range(self.nkeys - 1, -1, -1):
                if key.lower() == (self.keys[i] or "").lower():
                    return self.values[i]
        return None

    def get_key(self, key: str) -> int:
        for i in range(self.nkeys - 1, -1, -1):
            if self.keys[i] and self.keys[i].lower() == key.lower():
                return i
        return -1

    def get_key_at(self, index: int) -> Optional[str]:
        return self.keys[index] if 0 <= index < self.nkeys else None

    def get_value_at(self, index: int) -> Optional[str]:
        return self.values[index] if 0 <= index < self.nkeys else None

    def find_next_value(self, key: Optional[str], value: str) -> Optional[str]:
        found = False
        if key is None:
            for i in range(self.nkeys - 1, -1, -1):
                if self.keys[i] is None:
                    if found:
                        return self.values[i]
                    if self.values[i] == value:
                        found = True
        else:
            for i in range(self.nkeys - 1, -1, -1):
                if self.keys[i] and key.lower() == self.keys[i].lower():
                    if found:
                        return self.values[i]
                    if self.values[i] == value:
                        found = True
        return None

    def filter_ntlm_responses(self, key: str) -> bool:
        found_ntlm = any(
            key.lower() == (self.keys[i] or "").lower() and
            self.values[i] and self.values[i].startswith("NTLM ")
            for i in range(self.nkeys)
        )
        if found_ntlm:
            filtered_keys, filtered_values = [], []
            for i in range(self.nkeys):
                if not (key.lower() == (self.keys[i] or "").lower() and
                        self.values[i] in {"Negotiate", "Kerberos"}):
                    filtered_keys.append(self.keys[i])
                    filtered_values.append(self.values[i])
            self.keys = filtered_keys
            self.values = filtered_values
            self.nkeys = len(self.keys)
            return True
        return False

    def multi_value_iterator(self, key: str) -> Iterator[str]:
        return (value for i, value in enumerate(self.values)
                if self.keys[i] and self.keys[i].lower() == key.lower())

    def get_headers(self, exclude_list: Optional[List[str]] = None) -> Dict[str, List[str]]:
        return self.filter_and_add_headers(exclude_list, None)

    def filter_and_add_headers(self, exclude_list: Optional[List[str]] = None,
                               include: Optional[Dict[str, List[str]]] = None) -> Dict[str, List[str]]:
        exclude_set = {k.lower() for k in exclude_list} if exclude_list else set()
        headers = defaultdict(list)
        for i in range(self.nkeys - 1, -1, -1):
            key = self.keys[i]
            if key and key.lower() not in exclude_set:
                headers[key].append(self.values[i])

        if include:
            for k, v_list in include.items():
                headers[k].extend(v_list)

        return {k: list(set(v)) for k, v in headers.items()}

    def print(self, stream: StringIO):
        for i in range(self.nkeys):
            if self.keys[i] is not None:
                stream.write(f"{self.keys[i]}: {self.values[i]}\r\n")
        stream.write("\r\n")
        stream.flush()

    def add(self, key: Optional[str], value: Optional[str]):
        self.grow()
        self.keys.append(key)
        self.values.append(value)
        self.nkeys += 1

    def prepend(self, key: Optional[str], value: Optional[str]):
        self.grow()
        self.keys.insert(0, key)
        self.values.insert(0, value)
        self.nkeys += 1

    def set(self, index: int, key: str, value: str):
        if 0 <= index < self.nkeys:
            self.keys[index] = key
            self.values[index] = value
        else:
            self.add(key, value)

    def grow(self):
        if len(self.keys) <= self.nkeys:
            self.keys.extend([None] * 4)
            self.values.extend([None] * 4)

    def remove(self, key: Optional[str]):
        new_keys, new_values = [], []
        for i in range(self.nkeys):
            if (key is None and self.keys[i] is None) or (key and self.keys[i] and key.lower() == self.keys[i].lower()):
                continue
            new_keys.append(self.keys[i])
            new_values.append(self.values[i])
        self.keys = new_keys
        self.values = new_values
        self.nkeys = len(self.keys)

    def set_if_not_set(self, key: str, value: str):
        if self.find_value(key) is None:
            self.add(key, value)

    @staticmethod
    def canonical_id(msg_id: str) -> str:
        if msg_id is None:
            return ""
        return re.sub(r"(^[<\s]+|[>\s]+$)", "", msg_id.strip())

    def parse_header(self, stream: StringIO):
        self.nkeys = 0
        self.merge_header(stream)

    def merge_header(self, stream: StringIO):
        line = stream.readline()
        while line not in ('\n', '\r\n', ''):
            key, sep, value = line.partition(':')
            key, value = key.strip(), value.strip()
            if not sep:
                key = None
            if key or value:
                self.add(key, value)
            line = stream.readline()

    def __str__(self) -> str:
        result = f"{self.__class__.__name__}({self.nkeys} pairs): "
        result += ', '.join(f"{{'{k}': '{v}'}}" for k, v in zip(self.keys, self.values))
        return result
