"""Browser automation errors."""


class BrowserError(Exception):
    """Base error for browser operations."""

    code: str = "BROWSER_ERROR"

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        if code:
            self.code = code


class NoSessionError(BrowserError):
    code = "NO_SESSION"

    def __init__(self, message: str = "No active browser session. Call browser_start first."):
        super().__init__(message, self.code)


class ElementNotFoundError(BrowserError):
    code = "ELEMENT_NOT_FOUND"

    def __init__(self, index: int, message: str | None = None):
        msg = message or f"Element index {index} not found. Call browser_get_state to refresh."
        super().__init__(msg, self.code)
        self.index = index


class NavigationError(BrowserError):
    code = "NAVIGATION_FAILED"


class MaxStepsError(BrowserError):
    code = "MAX_STEPS"
