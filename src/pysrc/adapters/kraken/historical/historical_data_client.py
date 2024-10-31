import os
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import requests

from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide

HISTORICAL_DRIVE_FOLDER_ID = "188O9xQjZTythjyLNes_5zfMEFaMbTT22"


class HistoricalDataClient:
    def __init__(self, drive_api_key: Optional[str] = None):
        self._drive_api_key = drive_api_key

        self._np_dtype = [("time", "u8"), ("price", "f4"), ("volume", "f4")]

    def _list_drive_files(self, folder_id: str) -> list[tuple[str, str]]:
        url = "https://www.googleapis.com/drive/v3/files/"
        params = {
            "q": f"'{folder_id}' in parents",
            "fields": "files(id, name)",
        }

        headers = {"Authorization": f"Bearer {self._drive_api_key}"}

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            raise ValueError(f"Failed to list files from drive: {res.text}")

        files = []
        for f in res.json().get("files", []):
            file_name, file_id = f["name"], f["id"]
            files.append((file_name, file_id))
            break

        return files

    def _download_drive_file(self, file_id: str, download_path: str) -> None:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&acknowledgeAbuse=true"

        headers = {"Authorization": f"Bearer {self._drive_api_key}"}

        res = requests.get(url, headers=headers, stream=True)

        if res.status_code != 200:
            raise ValueError(f"Failed to download {file_id} with: {res.text}")

        with open(download_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)

    def _download_data_from_drive(
        self, download_path: str, drive_folder_id: str
    ) -> list[str]:
        downloaded_zip_paths = []
        for file_name, file_id in self._list_drive_files(drive_folder_id):
            download_file_path = os.path.join(download_path, file_name)
            self._download_drive_file(file_id, download_file_path)

            downloaded_zip_paths.append(download_file_path)

        dir_paths = []
        for zip_file_path in downloaded_zip_paths:
            dir_path = os.path.splitext(zip_file_path)[0]
            os.makedirs(dir_path)

            with zipfile.ZipFile(zip_file_path, "r") as zip_f:
                zip_f.extractall(dir_path)

            os.remove(zip_file_path)
            dir_paths.append(dir_path)

        pairs_to_file_paths = defaultdict(list)
        for path in dir_paths:
            for file_name in os.listdir(path):
                pair = os.path.splitext(file_name)[0]
                file_path = os.path.join(path, file_name)
                pairs_to_file_paths[pair].append(file_path)

        pair_dir_paths = []
        for pair, file_paths in pairs_to_file_paths.items():
            pair_dir_path = os.path.join(download_path, pair)
            pair_dir_paths.append(pair_dir_path)
            os.mkdir(pair_dir_path)

            merged_file_path = os.path.join(pair_dir_path, pair + ".csv")
            for file_path in file_paths:
                with open(file_path, "r") as f:
                    with open(merged_file_path, "a") as merged_f:
                        merged_f.write(f.read())

        for path in dir_paths:
            shutil.rmtree(path)

        return pair_dir_paths

    def _chunk_csv_by_day(self, csv_path: str) -> list[str]:
        dir_path = os.path.dirname(csv_path)
        chunk_file_paths: list[str] = []

        lines = []
        with open(csv_path) as f:
            for line in f.readlines():
                lines.append(line)

        if not lines:
            return chunk_file_paths

        lines.sort(key=lambda x: x.split(",")[0])

        first_line = lines[0]
        inital_time, _, _ = first_line.split(",")
        current_date = datetime.fromtimestamp(int(inital_time), tz=timezone.utc)

        chunk_file_path = os.path.join(
            dir_path, current_date.strftime("%m_%d_%Y") + ".csv"
        )
        chunk_file_paths.append(chunk_file_path)

        chunk_file = open(chunk_file_path, "w")
        chunk_file.write(first_line)

        for i in range(1, len(lines)):
            line = lines[i]
            line_time, _, _ = line.split(",")
            line_date = datetime.fromtimestamp(int(line_time), tz=timezone.utc)

            if line_date.date() == current_date.date():
                chunk_file.write(line)
            else:
                current_date = line_date
                chunk_file.close()

                chunk_file_path = os.path.join(
                    dir_path, current_date.strftime("%m_%d_%Y") + ".csv"
                )
                chunk_file_paths.append(chunk_file_path)

                chunk_file = open(chunk_file_path, "w")
                chunk_file.write(line)

        chunk_file.close()
        return chunk_file_paths

    def _serialize_csv(self, csv_path: str) -> str:
        arr = np.loadtxt(csv_path, delimiter=",", dtype=self._np_dtype)

        new_file_path = os.path.splitext(csv_path)[0] + ".bin"
        arr.tofile(new_file_path)
        return new_file_path

    def get_trades_from_file(self, file_path: str) -> list[TradeMessage]:
        arr = np.fromfile(file_path, dtype=self._np_dtype)
        pair = os.path.basename(os.path.dirname(file_path))

        trades = []
        for trade_data in arr:
            time, price, volume = trade_data
            trade = TradeMessage(
                time, pair, 1, price, volume, OrderSide.BID, Market.KRAKEN_SPOT
            )

            trades.append(trade)

        return trades

    def get_trades(
        self, asset: str, date: datetime, resource_path: str
    ) -> list[TradeMessage]:
        file_path = os.path.join(
            resource_path, asset, date.strftime("%m_%d_%Y") + ".bin"
        )

        if not os.path.exists(file_path):
            return []

        return self.get_trades_from_file(file_path)

    def download(
        self, download_path: str, drive_folder_id: str = HISTORICAL_DRIVE_FOLDER_ID
    ) -> None:
        if not self._drive_api_key:
            raise ValueError("Missing API key to access drive")

        if not os.path.exists(download_path):
            raise ValueError(f"Download path '{download_path}' does not exist")

        pair_dir_paths = self._download_data_from_drive(download_path, drive_folder_id)
        for dir_path in pair_dir_paths:
            pair = os.path.basename(dir_path)
            pair_csv_file = os.path.join(dir_path, pair + ".csv")

            chunked_csv_files = self._chunk_csv_by_day(pair_csv_file)
            os.remove(pair_csv_file)

            for chunked_file in chunked_csv_files:
                self._serialize_csv(chunked_file)
                os.remove(chunked_file)
