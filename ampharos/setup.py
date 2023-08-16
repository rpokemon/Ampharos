import json
from collections import namedtuple
from typing import Any, List, Tuple

import asyncpg

from .tables import ALL_TABLES, TRANSFORMERS
from .utils import get_base_dir

BASE_DIR = get_base_dir()


async def setup_ampharos(connection: asyncpg.Connection):
    """Populates the Pokemon database.

    This method should always be called on startup"""
    # Populate the tables if required
    for table in ALL_TABLES:
        # If Table is empty
        if (await table.fetch_row(connection)) is None:
            record = namedtuple("record", (column.name for column in table._columns))
            data: List[Tuple[Any, ...]] = []

            try:
                with open(BASE_DIR / f"data/{table.__name__.lower()}.json") as f:
                    for item in json.load(f):
                        for key, transformer in TRANSFORMERS.get(table, {}).items():
                            item[key] = transformer(item[key])
                        data.append(record(**item))
            except FileNotFoundError:
                print(f"Could not find Pokemon data file {table.__name__.lower()}.json")
            else:
                try:
                    await table.insert_many(connection, table._columns, *data)
                except Exception as e:
                    print(e)
