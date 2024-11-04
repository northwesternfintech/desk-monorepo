from pysrc.adapters.kraken.historical.historical_data_client import HistoricalDataClient


if __name__ == "__main__":
    client = HistoricalDataClient(
        drive_auth_token="ya29.a0AeDClZBlqNGsawUEz_8mFUZTlDzGOGYs1Q6dqZS2AlwOeUh6E-xd89DbGk2wViLOuBC2SzUIP0cUY8rxQxkr4giAGJVISujoqjhiN2NwtFMBks3r6hPZwBDTOipaAw_LinTS_J8PE2pZjd31TNJShA6XJKwupziomwARnIXAaCgYKAZESARESFQHGX2Mi6It8i_z34qNg52xJwb9V1Q0175"
    )
    import time

    t0 = time.time()
    client.download("/Users/ryan/Downloads/test_2")
    print(time.time() - t0)
