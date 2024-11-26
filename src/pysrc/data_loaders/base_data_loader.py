from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any, Optional

from pysrc.util.types import Asset


class BaseDataLoader(ABC):
    @abstractmethod
    def __init__(
        self,
        resource_path: Path,
        asset: Asset,
        since: date,
        until: date,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_data(self, since: date, until: date) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    def next(self) -> Any:
        raise NotImplementedError
