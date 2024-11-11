class POCInfo:
    UUID = "(c)"
    MSG = "Proof of Concept MP4 file demonstrating weak content protection in the environment of CANAL+ (Microsoft PlayReady DRM case)"

    @staticmethod
    def replace_array_content(array: bytearray, string: str):
        """
        Replaces content of a byte array with bytes from the given string. If the string is shorter
        than the array, remaining elements in the array are set to zero. If the string is longer than 
        the array, it is truncated to fit the array's length.

        Parameters:
        - array (bytearray): The byte array to modify.
        - string (str): The string whose bytes will replace the array's contents.
        """
        # Get byte data from the string
        data = string.encode('utf-8')
        
        # Determine how much data to copy (whichever is smaller)
        slen = min(len(data), len(array))
        
        # Copy string data to array
        array[:slen] = data[:slen]
        
        # Zero out any remaining elements if data is shorter than array
        if slen < len(array):
            array[slen:] = b'\x00' * (len(array) - slen)
