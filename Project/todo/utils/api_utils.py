import logging
import os
import requests

from todo.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

# Integer‐endpoint template; override via env if you like
RANDOM_ORG_INTEGER_URL = os.getenv(
    "RANDOM_ORG_INTEGER_URL",
    "https://www.random.org/integers/?num=1&min=1&max={max}&col=1&base=10&format=plain&rnd=new"
)


def get_random(n: int) -> int:
    """
    Fetches a cryptographically-strong random integer in [1..n] from random.org.

    Args:
        n (int): Upper bound (inclusive) for the random integer.

    Returns:
        int: A random integer between 1 and n.

    Raises:
        ValueError: If the response cannot be parsed as an integer.
        RuntimeError: On network errors or non-2xx status codes.
    """
    url = RANDOM_ORG_INTEGER_URL.format(max=n)
    logger.info(f"Fetching random integer from {url}")

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        text = resp.text.strip()

        try:
            val = int(text)
        except ValueError:
            logger.error(f"Invalid response from random.org: {text!r}")
            raise ValueError(f"Invalid response from random.org: {text!r}")

        logger.debug(f"Received random integer: {val}")
        return val

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
