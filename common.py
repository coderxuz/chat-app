from securely import Auth # type: ignore

import logging
from os import getenv
from typing import Optional
from datetime import timedelta

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BLUE = "\033[94m"


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_message = super().format(record)
        level_name = record.levelname  # Log darajasini olish
        if record.levelno == logging.DEBUG:
            return f"{BLUE}[{level_name}] {log_message}{RESET}"
        elif record.levelno == logging.INFO:
            return f"{GREEN}[{level_name}] {log_message}{RESET}"
        elif record.levelno == logging.WARNING:
            return f"{YELLOW}[{level_name}] {log_message}{RESET}"
        elif record.levelno >= logging.ERROR:
            return f"{RED}[{level_name}] {log_message}{RESET}"
        return f"[{level_name}] {log_message}"


# Logger sozlash
handler = logging.StreamHandler()
handler.setFormatter(
    ColorFormatter(
        "\nTime: %(asctime)s \nFile: %(filename)s:%(lineno)d \nMessage: %(message)s"
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

SECRET_KEY: Optional[str] = getenv("SECRET_KEY")
ACCESS_EXPIRES: Optional[str] = getenv("ACCESS_TOKEN_EXPIRES")
REFRESH_EXPIRES: Optional[str] = getenv("REFRESH_TOKEN_EXPIRES")

if not SECRET_KEY:
    raise ValueError("Secret_key not found")
if not ACCESS_EXPIRES:
    raise ValueError("Access_expires not found")
if not REFRESH_EXPIRES:
    raise ValueError("Refresh_expires not found")

auth = Auth(
    secret_key=SECRET_KEY,
    access_token_expires=timedelta(days=int(ACCESS_EXPIRES)),
    refresh_token_expires=timedelta(days=int(REFRESH_EXPIRES)),
)
