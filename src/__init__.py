import logging
from .settings import LOG_LEVEL

_level_from_str = dict(
    NOTSET      = logging.NOTSET,
    INFO        = logging.INFO,
    WARN        = logging.WARN,
    WARNING     = logging.WARNING,
    DEBUG       = logging.DEBUG,
    ERROR       = logging.ERROR,
    CRITICAL    = logging.CRITICAL,
)

try:
    level = _level_from_str[LOG_LEVEL]
except KeyError:
    raise EnvironmentError(f"invalid LOG_LEVEL {LOG_LEVEL!r}")

logging.basicConfig(level=level)

logging.warning(f"level: {LOG_LEVEL} {level}")
