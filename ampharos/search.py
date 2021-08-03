import difflib
import random

from typing import AsyncIterator, Optional, Type, TypeVar

import asyncpg

from donphan import Table, MaybeAcquire

from . import types, tables

__all__ = (
    "ability",
    "item",
    "move",
    "pokemon",
    "typing",
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
    table: Type[Table],
    search_term: str,
) -> Optional[asyncpg.Record]:
    async with MaybeAcquire(connection) as connection:
        records = await connection.fetch(f"SELECT term FROM {table._name}")
        matches = difflib.get_close_matches(search_term, (record["term"] for record in records))

        if not matches:
            return None

        return await table.fetch_row(connection, term=matches[0])


async def _fetch(
    connection: asyncpg.Connection,
    /,
    table: Type[Table],
    term: str,
    type: Type[T],
) -> Optional[T]:
    record = await table.fetch_row(connection, term=term)
    if record is None:
        raise RuntimeError("Term not found")
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
) -> Optional[types.Ability]:
    """Searches for a :class:`types.Ability`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Ability: The best matching ability.

    """
    async with MaybeAcquire(connection) as connection:
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
) -> Optional[types.Item]:
    """Searches for a :class:`types.Item`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Item: The best matching item.
    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(connection, tables.Items, search_term)
        if record is None:
            return None

        return await _item(connection, record)


async def _move(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Move:
    dct = dict(record.items())
    dct["type"] = await _fetch(connection, tables.Types, dct["type"], types.Typing)
    dct["category"] = types.Category(dct["category"])

    return types.Move(*dct.values())


async def move(
    connection: asyncpg.Connection,
    /,
    search_term: str,
) -> Optional[types.Move]:
    """Searches for a :class:`types.Move`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Move: The best matching move.
    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(connection, tables.Moves, search_term)
        if record is None:
            return None

        return await _move(connection, record)


async def _pokemon(
    connection: asyncpg.Connection,
    /,
    record: asyncpg.Record,
) -> types.Pokemon:
    async with MaybeAcquire(connection) as connection:
        dct = dict(record.items())
        term = dct["term"]

        # Retrieve additional objects
        dct["name"] = await _fetch(connection, tables.PokemonNames, term, types.PokemonName)
        dct["pokedex_entries"] = await _fetch(
            connection,
            tables.PokemonDexEntries,
            term,
            types.PokemonPokedexEntries,
        )

        evolutions = await tables.PokemonEvolutions.fetch(connection, term=term)
        dct["evolutions"] = [await pokemon(connection, record["evolution"]) for record in evolutions]

        dct["base_stats"] = await _fetch(connection, tables.PokemonBaseStats, term, types.PokemonBaseStats)

        typing_dct = dict((await tables.PokemonTypes.fetch_row(connection, term=term)).items())
        for key, value in typing_dct.items():
            if key == "term" or value is None:
                continue
            typing_dct[key] = await _fetch(connection, tables.Types, typing_dct[key], types.Typing)
        dct["typing"] = types.PokemonTypings(*typing_dct.values())

        abilities_dct = dict((await tables.PokemonAbilities.fetch_row(connection, term=term)).items())
        for key, value in abilities_dct.items():
            if key == "term" or value is None:
                continue
            abilities_dct[key] = await ability(connection, abilities_dct[key])
        dct["abilities"] = types.PokemonAbilities(*abilities_dct.values())

        return types.Pokemon(*dct.values())


async def pokemon(connection: asyncpg.Connection, /, search_term: str) -> Optional[types.Pokemon]:
    """Searches for a :class:`types.Pokemon`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Pokemon: The best matching Pokemon.
    """
    async with MaybeAcquire(connection) as connection:
        if search_term.isdigit():
            record = await tables.Pokemon.fetch_row(connection, dex_no=int(search_term))
        else:
            record = await _search(connection, tables.Pokemon, search_term)

        if record is None:
            return None

        return await _pokemon(connection, record)


async def _typing(connection: asyncpg.Connection, /, record: asyncpg.Record) -> types.Typing:
    return types.Typing(*record.values())


async def typing(connection: asyncpg.Connection, /, search_term: str) -> Optional[types.Typing]:
    """Searches for a :class:`types.Typing`.

    Args:
        search_term (str): The term to search for
    """
    record = await _search(connection, tables.Types, search_term)
    if record is None:
        return None

    return await _typing(connection, record)


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

    return await _ability(connection, random.choice(records))


async def random_item(connection: asyncpg.Connection, /) -> types.Item:
    """Returns a random :class:`types.Item`."""
    records = await tables.Items.fetch(connection)

    return await _item(connection, random.choice(records))


async def random_move(connection: asyncpg.Connection, /) -> types.Move:
    """Returns a random :class:`types.Move`."""
    records = await tables.Moves.fetch(connection)

    return await _move(connection, random.choice(records))


async def random_pokemon(connection: asyncpg.Connection, /) -> types.Pokemon:
    """Returns a random :class:`types.Pokemon`."""
    records = await tables.Pokemon.fetch(connection)

    return await _pokemon(connection, random.choice(records))
