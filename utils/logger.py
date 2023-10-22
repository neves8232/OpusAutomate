import datetime
from colorama import init, Fore, Style

init(autoreset=True)  # Automatically reset to default colors after each print


class ColorLogger:
    def __init__(self):
        pass

    def _get_current_datetime(self) -> str:
        """Returns the current date-time as a string."""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def step(self, message: str) -> None:
        """Prints a step message in blue."""
        print(f"{Fore.BLUE}{self._get_current_datetime()} - STEP: {message}{Style.RESET_ALL}")

    def error(self, message: str) -> None:
        """Prints an error message in red."""
        print(f"{Fore.RED}{self._get_current_datetime()} - ERROR: {message}{Style.RESET_ALL}")



