import json
import os.path

from . import types, tables


async def setup():
    """Populates the Pokemon database. 

    This method should always be called on startup"""
    # Populate the tables if required
    for table in tables.tables:
        if (await table.fetchrow()) is None:
            try:
                _basedir = os.path.dirname(os.path.abspath(__file__))
                with open(f'{_basedir}/data/{table.__name__}.json') as f:
                    for item in json.load(f):

                        try:
                            await table.insert(**item)
                        except Exception as e:
                            print(e)

            except FileNotFoundError:
                print(
                    f"Could not find Pokemon data file {table.__name__}.json")
