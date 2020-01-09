import json
import os.path

from donphan import MaybeAcquire

from . import tables


async def setup():
    """Populates the Pokemon database. 

    This method should always be called on startup"""
    async with MaybeAcquire() as connection:

        # Populate the tables if required
        for table in tables.tables:
            if (await table.fetchrow(connection=connection)) is None:
                try:
                    _basedir = os.path.dirname(os.path.abspath(__file__))
                    with open(f'{_basedir}/data/{table.__name__.lower()}.json') as f:
                        for item in json.load(f):

                            try:
                                await table.insert(connection, **item)
                            except Exception as e:
                                print(e)

                except FileNotFoundError:
                    print(
                        f"Could not find Pokemon data file {table.__name__.lower()}.json")
