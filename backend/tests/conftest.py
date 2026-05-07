import pytest

from app.core import database


@pytest.fixture(autouse=True)
def reset_pool():
    """Reset the pool reference before each test.

    With asyncio_default_fixture_loop_scope="function", each test runs in its
    own event loop. Setting _pool=None forces a fresh pool to be created inside
    that loop, preventing asyncpg Futures from being attached to the wrong loop.
    """
    database._pool = None
    yield
    database._pool = None
