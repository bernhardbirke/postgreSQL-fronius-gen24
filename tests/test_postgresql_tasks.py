import pytest
from src.fronius_gen24.postgresql_tasks import PostgresTasks


# create instance postgrestasks of Class PostgresTasks
@pytest.fixture
def postgrestasks():
    return PostgresTasks()


# Caution: creates an entry in specified postgresql database
def test_insert_fronius_gen24(postgrestasks):
    id = postgrestasks.insert_fronius_gen24(
        84,
        0.35999999999999999,
        232.40000000000001,
        49.969999999999999,
        1734796.1200000001,
    )
    assert isinstance(id, int) and id > 0
