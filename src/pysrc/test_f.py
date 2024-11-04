from pysrc.adapters.kraken.historical.historical_data_client import HistoricalDataClient

if __name__ == "__main__":
    client = HistoricalDataClient(
        drive_auth_token="ya29.a0AeDClZDMyTKeZBjsIz_aogu9FMSO5MtLRezNy2Vnstdh2XHhQH1Tna3iwD5xel1tAMSiQPrUAtXAqFxN-GTKTNGGhOwa11w7ttrGQE3capd5J0pqCAlXoRNM1_hAMu3Zf8m00fn_JWdDo3aVMYB0geVcI2v_Ve0hvIjCR2h0owaCgYKARkSARESFQHGX2Mit8dXIe8tZbVLu8gAssqZfg0177"
    )
    client.download("/Users/ryan/Downloads/test_3")
