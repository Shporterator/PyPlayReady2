import requests
import time
from typing import List, Dict, Optional, Tuple, Union
from io import BytesIO

class MessageHeader:
    def __init__(self):
        self.headers: Dict[str, str] = {}

    def add(self, key: str, value: str):
        self.headers[key] = value

    def set_if_not_set(self, key: str, value: str):
        if key not in self.headers:
            self.headers[key] = value

    def get(self) -> Dict[str, str]:
        return self.headers

class Web:
    USER_AGENT = "Mozilla/5.0 (ADB)"
    BUFSIZE = 0x100000  # Buffer size for downloads
    TIMEOUT_VAL = 2  # Timeout in seconds

    @staticmethod
    def sleep(time_seconds: int):
        """Pauses execution for a given time in seconds."""
        time.sleep(time_seconds)

    @staticmethod
    def set_headers(session: requests.Session, headers: List[Tuple[str, str]]) -> MessageHeader:
        """Sets the headers in a session and returns a MessageHeader object."""
        msg_header = MessageHeader()
        for key, value in headers:
            msg_header.add(key, value)
        msg_header.add("User-Agent", Web.USER_AGENT)
        session.headers.update(msg_header.get())
        return msg_header

    @staticmethod
    def https_post(url: str, data: str, headers: List[Tuple[str, str]]) -> str:
        """Performs an HTTPS POST request with retries."""
        while True:
            try:
                return Web.https_post_internal(url, data, headers)
            except Exception as e:
                Web.sleep(1)

    @staticmethod
    def https_post_internal(url: str, data: str, headers: List[Tuple[str, str]]) -> str:
        """Internal method for performing an HTTPS POST request."""
        with requests.Session() as session:
            Web.set_headers(session, headers)
            session.headers.update({
                "Content-Length": str(len(data)),
                "Accept-Language": "en, *"
            })
            response = session.post(url, data=data, timeout=Web.TIMEOUT_VAL)
            response.raise_for_status()
            return response.text

    @staticmethod
    def http_get(url: str, headers: List[Tuple[str, str]], output: Union[str, BytesIO]) -> int:
        """Performs an HTTP GET request, writes the response to a file or stream, and returns the byte count."""
        while True:
            try:
                return Web.http_get_internal(url, headers, output)
            except Exception as e:
                Web.sleep(1)

    @staticmethod
    def http_get_internal(url: str, headers: List[Tuple[str, str]], output: Union[str, BytesIO]) -> int:
        """Internal method for performing an HTTP GET request and writing to an output stream."""
        with requests.Session() as session:
            Web.set_headers(session, headers)
            with session.get(url, stream=True, timeout=Web.TIMEOUT_VAL) as response:
                response.raise_for_status()
                count = 0
                if isinstance(output, str):
                    with open(output, 'wb') as file_out:
                        for chunk in response.iter_content(chunk_size=Web.BUFSIZE):
                            file_out.write(chunk)
                            count += len(chunk)
                elif isinstance(output, BytesIO):
                    for chunk in response.iter_content(chunk_size=Web.BUFSIZE):
                        output.write(chunk)
                        count += len(chunk)
                return count

    @staticmethod
    def http_get_to_file(url: str, headers: List[Tuple[str, str]], file_path: str) -> int:
        """Fetches a URL's contents and saves it to a file."""
        return Web.http_get(url, headers, file_path)
