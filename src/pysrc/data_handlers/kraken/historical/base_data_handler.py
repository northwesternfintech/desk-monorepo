from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generator
from pysrc.adapters.messages import TradeMessage, SnapshotMessage


class BaseDataHandler(ABC):
    @abstractmethod
    def __init__(self, write_size: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self, input_path: Path) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    def write(self, output_path: Path, data: list[Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def stream_read(
        self, input_path: Path
    ) -> Generator[TradeMessage | SnapshotMessage, None, None]:
        raise NotImplementedError
