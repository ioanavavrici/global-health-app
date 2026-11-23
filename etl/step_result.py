from dataclasses import dataclass
import enum


class StepStatus(str, enum.Enum):
    OK = "ok"
    FAILED = "failed"


@dataclass(frozen=True)
class StepResult:
    source: str
    item: str
    status: StepStatus
    detail: str

    @property
    def is_ok(self) -> bool:
        return self.status == StepStatus.OK

    @classmethod
    def ok(cls, source: str, item: str, detail: str) -> "StepResult":
        return cls(source=source, item=item, status=StepStatus.OK, detail=detail)

    @classmethod
    def from_error(cls, source: str, item: str, error: Exception) -> "StepResult":
        return cls(
            source=source,
            item=item,
            status=StepStatus.FAILED,
            detail=f"{type(error).__name__}: {error}",
        )
