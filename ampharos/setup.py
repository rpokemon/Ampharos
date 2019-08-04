import json

from . import types, tables

DATA_DIRECTORY = 'data'


async def setup():
    """Populates the Pokemon database. 

    This method should always be called on startup"""
    # Populate the tables if required
    for table in tables.tables:
        if (await table.fetchrow()) is None:
            try:

                with open(f'{DATA_DIRECTORY}/{table.__table_name__}.json') as f:
                    for item in json.load(f):

                        try:
                            await table.insert(**item)
                        except Exception as e:
                            print(e)

            except FileNotFoundError:
                print(
                    f"Could not find Pokemon data file {table.__table_name__}.json")
