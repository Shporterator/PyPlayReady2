import sys
from modules.utils import Utils
from collections import deque

class PaddedPrinter:
    class PrintLevel:
        def __init__(self, pad: int, header: str, prefix: str):
            """
            Initializes a PrintLevel instance.

            Parameters:
                pad (int): Padding level.
                header (str): Header text to print.
                prefix (str): Prefix for each printed line.
            """
            self._pad = pad
            self._header = header
            self._prefix = prefix

        def pad(self) -> int:
            return self._pad

        def header(self) -> str:
            return self._header

        def prefix(self) -> str:
            return self._prefix

    levels = deque()  # Using a deque as a stack for levels

    def __init__(self):
        self.lvl = 0
        self.pad = 0

    def pad(self, cnt: int, header: str = "", prefix: str = ""):
        """
        Adds padding and optionally prints a header.

        Parameters:
            cnt (int): Amount of padding to add.
            header (str): Optional header text to print.
            prefix (str): Optional prefix to add to the next printed lines.
        """
        self.pad += cnt
        level = self.PrintLevel(self.pad, header, prefix)
        self.levels.append(level)
        self.lvl += 1

        if header:
            line = Utils.pad(self.pad) + header
            Utils.outputln(line)

    def leave(self) -> 'PaddedPrinter.PrintLevel':
        """
        Removes the last padding level and returns it.
        
        Returns:
            PrintLevel: The last PrintLevel instance.
        """
        level = self.levels.pop()
        if self.levels:
            self.pad = self.levels[-1].pad()
        else:
            self.pad = 0
        self.lvl -= 1
        return level

    def peek(self) -> 'PaddedPrinter.PrintLevel':
        """
        Returns the current padding level without removing it.
        
        Returns:
            PrintLevel: The current PrintLevel instance.
        """
        return self.levels[-1]

    @staticmethod
    def getInstance() -> 'PaddedPrinter':
        """
        Returns an instance of PaddedPrinter with default padding.
        
        Returns:
            PaddedPrinter: A new PaddedPrinter instance.
        """
        pp = PaddedPrinter()
        pp.pad(0, "", "")
        return pp

    def println(self, s: str):
        """
        Prints a line with the current padding and prefix.

        Parameters:
            s (str): The string to print.
        """
        level = self.peek()
        line = Utils.pad(level.pad()) + level.prefix() + s
        Utils.outputln(line)

    def printhex(self, s: str, data: bytes):
        """
        Prints hexadecimal data with the specified padding and label.

        Parameters:
            s (str): Label for the hexadecimal data.
            data (bytes): Byte data to print in hexadecimal.
        """
        level = self.peek()
        Utils.print_buf(level.pad(), s, data)
