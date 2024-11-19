from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Generator
from datetime import datetime
from pysrc.adapters.messages import TradeMessage, SnapshotMessage


class BaseDataHandler(ABC):
    @abstractmethod
    def __init__(self, resource_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_file(self, input_path: Path) -> list[TradeMessage] | list[SnapshotMessage]:
        raise NotImplementedError

    @abstractmethod
    def write_to_file(self, output_path: Path, data: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def stream_data(
        self, asset: str, since: datetime, until: Optional[datetime]
    ) -> Generator[TradeMessage | SnapshotMessage, None, None]:
        raise NotImplementedError
