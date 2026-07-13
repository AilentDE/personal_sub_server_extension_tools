import logging

from sqlalchemy.exc import DBAPIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def log_before_retry(retry_state):
    exception = retry_state.outcome.exception()
    if isinstance(exception, DBAPIError):
        error_message = str(exception.orig)
    else:
        error_message = str(exception)

    logger.warning(
        "Retrying %s after attempt %d in %.1f seconds due to %s: %s",
        retry_state.fn.__qualname__,
        retry_state.attempt_number,
        retry_state.next_action.sleep,
        type(exception).__name__,
        error_message,
    )


retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    before_sleep=log_before_retry,
    reraise=True,
)
