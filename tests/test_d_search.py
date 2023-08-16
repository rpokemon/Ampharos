from unittest import TestCase

from ampharos import pokemon

from .utils import async_test, with_connection


class SearchTest(TestCase):
    @async_test
    @with_connection
    async def test_search_pokemon(self, connection):
        record = await pokemon(connection, "pikachew")

        assert record is not None
        assert record._term == "pikachu"
