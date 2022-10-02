import pytest
from store import Store


@pytest.fixture(autouse=True)
def redis_init(tmpdir):
    store = Store()
    yield store
    store._store.close()


def test_get_unknown_key(redis_init):
    assert redis_init.get("1") is None


def test_readwrite(redis_init):
    redis_init.cache_set("key", 42, 60)
    assert redis_init.get("key") == 42


if __name__ == "__main__":
    pytest.main()
