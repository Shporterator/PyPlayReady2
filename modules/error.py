import sys

class ERROR:
    @staticmethod
    def log(s: str):
        """
        Logs an error message and exits the program.
        
        Parameters:
            s (str): The error message to log.
        """
        print(f"ERROR: {s}")
        sys.exit(1)
