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
    table: Type[Table],
    search_term: str,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[asyncpg.Record]:
    async with MaybeAcquire(connection) as connection:
        records = await table.fetch_where(f"SELECT term FROM {table._name}", connection=connection)
        matches = difflib.get_close_matches(search_term, (record["term"] for record in records))

        if not matches:
            return None

        return await table.fetchrow(term=matches[0], connection=connection)


async def _fetch(
    table: Type[Table],
    term: str,
    type: Type[T],
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[T]:
    record = await table.fetchrow(connection=connection, term=term)
    return type(*record.values())


async def _ability(
    record: asyncpg.Record,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> types.Ability:
    return types.Ability(*record.values())


async def ability(
    search_term: str,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[types.Ability]:
    """Searches for a :class:`types.Ability`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Ability: The best matching ability.

    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(tables.Abilities, search_term, connection=connection)
        if record is None:
            return None

        return await _ability(record, connection=connection)


async def _item(
    record: asyncpg.Record,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> types.Item:
    return types.Item(*record.values())


async def item(
    search_term: str,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[types.Item]:
    """Searches for a :class:`types.Item`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Item: The best matching item.
    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(tables.Items, search_term, connection=connection)
        if record is None:
            return None

        return await _item(record, connection=connection)


async def _move(
    record: asyncpg.Record,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> types.Move:
    dct = dict(record.items())
    dct["type"] = await _fetch(tables.Types, dct["type"], types.Typing, connection=connection)
    dct["category"] = types.Category(dct["category"])

    return types.Move(*dct.values())


async def move(
    search_term: str,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[types.Move]:
    """Searches for a :class:`types.Move`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Move: The best matching move.
    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(tables.Moves, search_term, connection=connection)
        if record is None:
            return None

        return await _move(record, connection=connection)


async def _pokemon(
    record: asyncpg.Record,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> types.Pokemon:
    async with MaybeAcquire(connection) as connection:
        dct = dict(record.items())
        term = dct["term"]

        # Retrieve additional objects
        dct["name"] = await _fetch(tables.PokemonNames, term, types.PokemonName, connection=connection)
        dct["pokedex_entries"] = await _fetch(
            tables.PokemonDexEntries, term, types.PokemonPokedexEntries, connection=connection
        )

        evolutions = await tables.PokemonEvolutions.fetch(connection=connection, term=term)
        dct["evolutions"] = [await pokemon(record["evolution"], connection=connection) for record in evolutions]

        dct["base_stats"] = await _fetch(tables.PokemonBaseStats, term, types.PokemonBaseStats, connection=connection)

        typing_dct = dict((await tables.PokemonTypes.fetchrow(connection=connection, term=term)).items())
        for key, value in typing_dct.items():
            if key == "term" or value is None:
                continue
            typing_dct[key] = await _fetch(tables.Types, typing_dct[key], types.Typing, connection=connection)
        dct["typing"] = types.PokemonTypings(*typing_dct.values())

        abilities_dct = dict((await tables.PokemonAbilities.fetchrow(connection=connection, term=term)).items())
        for key, value in abilities_dct.items():
            if key == "term" or value is None:
                continue
            abilities_dct[key] = await ability(abilities_dct[key], connection=connection)
        dct["abilities"] = types.PokemonAbilities(*abilities_dct.values())

        return types.Pokemon(*dct.values())


async def pokemon(
    search_term: str,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> Optional[types.Pokemon]:
    """Searches for a :class:`types.Pokemon`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Pokemon: The best matching Pokemon.
    """
    async with MaybeAcquire(connection) as connection:
        if search_term.isdigit():
            record = await tables.Pokemon.fetchrow(connection=connection, dex_no=int(search_term))
        else:
            record = await _search(tables.Pokemon, search_term, connection=connection)

        if record is None:
            return None

        return await _pokemon(record, connection=connection)


async def _typing(
    record: asyncpg.Record,
    *,
    connection: Optional[asyncpg.Connection] = None,
) -> types.Typing:
    return types.Typing(*record.values())


async def typing(search_term: str, *, connection: Optional[asyncpg.Connection] = None) -> Optional[types.Typing]:
    """Searches for a :class:`types.Typing`.

    Args:
        search_term (str): The term to search for
    """
    async with MaybeAcquire(connection) as connection:
        record = await _search(tables.Types, search_term, connection=connection)
        if record is None:
            return None

        return await _typing(record, connection=connection)


async def all_abilities(*, connection: Optional[asyncpg.Connection] = None) -> AsyncIterator[types.Ability]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Ability` in the database."""
    async with MaybeAcquire(connection) as connection:
        for record in await tables.Abilities.fetchall(connection=connection):
            yield await _ability(record, connection=connection)


async def all_items(*, connection: Optional[asyncpg.Connection] = None) -> AsyncIterator[types.Item]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Item` in the database."""
    async with MaybeAcquire(connection) as connection:
        for record in await tables.Items.fetchall(connection=connection):
            yield await _item(record, connection=connection)


async def all_moves(*, connection: Optional[asyncpg.Connection] = None) -> AsyncIterator[types.Move]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Move` in the database."""
    async with MaybeAcquire() as connection:
        for record in await tables.Moves.fetchall(connection=connection):
            yield await _move(record, connection=connection)


async def all_pokemon(*, connection: Optional[asyncpg.Connection] = None) -> AsyncIterator[types.Pokemon]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Pokemon` in the database."""
    async with MaybeAcquire() as connection:
        for record in await tables.Pokemon.fetchall(connection=connection):
            yield await _pokemon(record, connection=connection)


async def random_ability(*, connection: Optional[asyncpg.Connection] = None) -> types.Ability:
    """Returns a random :class:`types.Ability`."""
    async with MaybeAcquire(connection) as connection:
        records = await tables.Abilities.fetchall(connection=connection)

        return await _ability(random.choice(records), connection=connection)


async def random_item(*, connection: Optional[asyncpg.Connection] = None) -> types.Item:
    """Returns a random :class:`types.Item`."""
    async with MaybeAcquire(connection) as connection:
        records = await tables.Items.fetchall(connection=connection)

        return await _item(random.choice(records), connection=connection)


async def random_move(*, connection: Optional[asyncpg.Connection] = None) -> types.Move:
    """Returns a random :class:`types.Move`."""
    async with MaybeAcquire(connection) as connection:
        records = await tables.Moves.fetchall(connection=connection)

        return await _move(random.choice(records), connection=connection)


async def random_pokemon(*, connection: Optional[asyncpg.Connection] = None) -> types.Pokemon:
    """Returns a random :class:`types.Pokemon`."""
    async with MaybeAcquire(connection) as connection:
        records = await tables.Pokemon.fetchall(connection=connection)

        return await _pokemon(random.choice(records), connection=connection)
