from __future__ import annotations

import functools
import json
import logging
from typing import Any, Callable, Dict, Optional, List


def log_tool_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    logger = logging.getLogger(func.__module__ + "." + func.__name__)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(
            "tool_call",
            extra={
                "extra": {
                    "event": "tool_call",
                    "tool": func.__name__,
                    "args": kwargs,
                }
            },
        )
        result = func(*args, **kwargs)
        logger.info(
            "tool_result",
            extra={
                "extra": {
                    "event": "tool_result",
                    "tool": func.__name__,
                    "result_preview": str(result)[:500],
                }
            },
        )
        return result

    return wrapper




