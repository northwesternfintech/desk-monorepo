
from typing import Optional

from pysrc.adapters.messages import TradeMessage


HISTORICAL_DRIVE_FOLDER_ID = "188O9xQjZTythjyLNes_5zfMEFaMbTT22"


class HistoricalDataClient:
    def __init__(
            self,
            drive_api_key: Optional[str] = None
        ):
        self._drive_api_key = drive_api_key

    def _download_zips_from_drive(
            self
    ) -> list[str]:
        pass

    def _chunk_csv_by_day(
            self,
            csv_path: str
    ) -> list[str]:
        pass

    def _serialize_csv(
            self,
            csv_path: str
    ) -> str:
        pass

    def to_trades(
            self,
            file_path: str
    ) -> list[TradeMessage]:
        # deserialize the serialized files to trade message
        pass

    def download(
            self,
            download_path: str,
    ) -> None:
        # list the zips in the drive folder
        # unzip each zip
        # chunk each csv into daily csv chunks
        # serialize each daily csv
        return