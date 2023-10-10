import pytest
from src.fronius_gen24.postgresql_tasks import PostgresTasks


# create instance postgrestasks of Class PostgresTasks
@pytest.fixture
def postgrestasks():
    return PostgresTasks()


# Caution: creates an entry in specified postgresql database
def test_insert_fronius_gen24(postgrestasks):
    id = postgrestasks.insert_fronius_gen24(
        6442.39697265625,
        5350360.6883333335,
    )
    assert isinstance(id, int) and id > 0
