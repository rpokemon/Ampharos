from unittest import TestCase

from ampharos import setup_ampharos

from .utils import async_test, with_connection


class CreateTest(TestCase):
    @async_test
    @with_connection
    async def test_setup_ampharos(self, connection):
        await setup_ampharos(connection)
