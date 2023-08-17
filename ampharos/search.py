import difflib
import random
from collections.abc import AsyncIterator
from typing import TypeVar

import asyncpg
from donphan import Table

from . import tables, types

__all__ = (
    "ability",
    "item",
    "move",
    "pokemon",
    "all_abilities",
    "all_items",
    "all_moves",
    "all_pokemon",
    "random_ability",
    "random_item",
    "random_move",
    "random_pokemon",
)

T = TypeVar("T")


async def _search(
    connection: asyncpg.Connection,
    /,
    table: type[Table],
    search_term: str,
) -> asyncpg.Record | None:
    records = await connection.fetch(f"SELECT term FROM {table._name}")
    matches = difflib.get_close_matches(search_term, (record["term"] for record in records))

    if not matches:
        return None

    return await table.fetch_row(connection, term=matches[0])


async def _fetch(
    connection: asyncpg.Connection,
    /,
    table: type[Table],
    term: str,
    type: type[T],
) -> T | None:
    record = await table.fetch_row(connection, term=term)
    if record is not None:
        return type(*record.values())


async def _ability(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Ability:
    return types.Ability(*record.values())


async def ability(
    connection: asyncpg.Connection,
    /,
    search_term: str,
) -> types.Ability | None:
    """Searches for a :class:`types.Ability`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Ability: The best matching ability.

    """
    record = await _search(connection, tables.Abilities, search_term)
    if record is None:
        return None

    return await _ability(connection, record)


async def _item(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Item:
    return types.Item(*record.values())


async def item(
    connection: asyncpg.Connection,
    /,
    search_term: str,
) -> types.Item | None:
    """Searches for a :class:`types.Item`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Item: The best matching item.
    """
    record = await _search(connection, tables.Items, search_term)
    if record is None:
        return None

    return await _item(connection, record)


async def _move(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Move:
    return types.Move(*record)


async def move(
    connection: asyncpg.Connection,
    /,
    search_term: str,
) -> types.Move | None:
    """Searches for a :class:`types.Move`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Move: The best matching move.
    """
    record = await _search(connection, tables.Moves, search_term)
    if record is None:
        return None

    return await _move(connection, record)


async def _pokemon(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Pokemon:
    dct = dict(record.items())
    term = dct["term"]

    # Retrieve additional objects
    dct["name"] = await _fetch(connection, tables.PokemonNames, term, types.PokemonName)
    dct["pokedex_entries"] = await _fetch(connection, tables.PokemonDexEntries, term, types.PokemonPokedexEntries)
    dct["base_stats"] = await _fetch(connection, tables.PokemonBaseStats, term, types.PokemonBaseStats)
    dct["typing"] = await _fetch(connection, tables.PokemonTypes, term, types.PokemonTypings)
    dct["abilities"] = await _fetch(connection, tables.PokemonAbilities, term, types.PokemonAbilities)

    evolutions = await tables.PokemonEvolutions.fetch(connection, term=term)
    dct["evolutions"] = [await pokemon(connection, record["evolution"]) for record in evolutions]

    return types.Pokemon(*dct.values())


async def pokemon(connection: asyncpg.Connection, /, search_term: str) -> types.Pokemon | None:
    """Searches for a :class:`types.Pokemon`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Pokemon: The best matching Pokemon.
    """
    if search_term.isdigit():
        record = await tables.Pokemon.fetch_row(connection, dex_no=int(search_term))
    else:
        record = await _search(connection, tables.Pokemon, search_term)

    if record is None:
        return None

    return await _pokemon(connection, record)


async def all_abilities(connection: asyncpg.Connection, /) -> AsyncIterator[types.Ability]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Ability` in the database."""
    for record in await tables.Abilities.fetch(connection):
        yield await _ability(connection, record)


async def all_items(connection: asyncpg.Connection, /) -> AsyncIterator[types.Item]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Item` in the database."""
    for record in await tables.Items.fetch(connection):
        yield await _item(connection, record)


async def all_moves(connection: asyncpg.Connection, /) -> AsyncIterator[types.Move]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Move` in the database."""
    for record in await tables.Moves.fetch(connection):
        yield await _move(connection, record)


async def all_pokemon(connection: asyncpg.Connection, /) -> AsyncIterator[types.Pokemon]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Pokemon` in the database."""
    for record in await tables.Pokemon.fetch(connection):
        yield await _pokemon(connection, record)


async def random_ability(connection: asyncpg.Connection, /) -> types.Ability:
    """Returns a random :class:`types.Ability`."""
    records = await tables.Abilities.fetch(connection)

    return await _ability(connection, random.choice(records))  # type: ignore


async def random_item(connection: asyncpg.Connection, /) -> types.Item:
    """Returns a random :class:`types.Item`."""
    records = await tables.Items.fetch(connection)

    return await _item(connection, random.choice(records))  # type: ignore


async def random_move(connection: asyncpg.Connection, /) -> types.Move:
    """Returns a random :class:`types.Move`."""
    records = await tables.Moves.fetch(connection)

    return await _move(connection, random.choice(records))  # type: ignore


async def random_pokemon(connection: asyncpg.Connection, /) -> types.Pokemon:
    """Returns a random :class:`types.Pokemon`."""
    records = await tables.Pokemon.fetch(connection)

    return await _pokemon(connection, random.choice(records))  # type: ignore
