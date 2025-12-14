
import sys
from datetime import datetime


class Logger:

    def __init__(self):
        self.verbose = True

    def info(self, message: str):
        if self.verbose:
            print(message)

    def error(self, message: str):
        print(f"ERROR: {message}", file=sys.stderr)

    def warning(self, message: str):
        print(f"WARNING: {message}", file=sys.stderr)

    def debug(self, message: str):
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] DEBUG: {message}")


logger = Logger()
