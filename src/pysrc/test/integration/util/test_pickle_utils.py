import numpy as np
from pathlib import Path
from pysrc.util.pickle_utils import store_pickle, load_pickle
from pysrc.test.helpers import get_resources_path

resource_path = get_resources_path(__file__)
sample_data = np.random.rand(10, 10)


def test_store_pickle() -> None:
    store_pickle(sample_data, resource_path.joinpath("sample_data.pkl"))


def test_load_pickle() -> None:
    loaded_data = load_pickle(resource_path.joinpath("sample_data.pkl"))
    assert np.array_equal(sample_data, loaded_data)
