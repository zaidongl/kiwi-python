from enum import Enum
from typing import Any

class StepResultStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class StepResult:
    def __init__(self, status: StepResultStatus, message: str = "", data: Any = None):
        self.status = status
        self.message = message
        self.data = data