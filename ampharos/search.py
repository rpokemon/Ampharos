import difflib
import random

from typing import AsyncGenerator

import asyncpg

from donphan import Table, MaybeAcquire

from . import types, tables

__all__ = (
    'ability',
    'item',
    'move',
    'pokemon',
    'typing',
    'all_abilities',
    'all_items',
    'all_moves',
    'all_pokemon',
    'random_ability',
    'random_item',
    'random_move',
    'random_pokemon',
)


async def _search(table: Table, search_term: str) -> asyncpg.Record:
    async with MaybeAcquire() as connection:
        matches = difflib.get_close_matches(search_term, (record['term'] for record in (await connection.fetch(f"SELECT term from {table._name}"))))

    if not matches:
        return None

    return await table.fetchrow(term=matches[0])


async def _fetch(table, search_term, new):
    record = await table.fetchrow(term=search_term)
    return new(*record.values())


async def ability(search_term: str) -> types.Ability:
    """Searches for a :class:`types.Ability`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Ability: The best matching ability.

    """
    record = await _search(tables.Abilities, search_term)
    if record is None:
        return None

    return types.Ability(*record.values())


async def item(search_term: str) -> types.Item:
    """Searches for a :class:`types.Item`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Item: The best matching item.
    """
    record = await _search(tables.Items, search_term)
    if record is None:
        return None

    return types.Item(*record.values())


async def move(search_term: str) -> types.Move:
    """Searches for a :class:`types.Move`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Move: The best matching move.
    """
    record = await _search(tables.Moves, search_term)
    if record is None:
        return None

    # Substitue terms for related objects
    dct = dict(record.items())
    dct['type'] = await _fetch(tables.Types, dct['type'], types.Typing)
    dct['category'] = types.Category(dct['category'])

    return types.Move(*dct.values())


async def pokemon(search_term: str) -> types.Pokemon:
    """Searches for a :class:`types.Pokemon`.

    Args:
        search_term (str): The term to search for
    Returns:
        types.Pokemon: The best matching Pokemon.
    """
    try:
        record = await tables.Pokemon.fetchrow(dex_no=int(search_term))
    except ValueError:
        record = await _search(tables.Pokemon, search_term)

    if record is None:
        return None

    dct = dict(record.items())
    term = dct['term']

    # Retrive additional objects
    dct['name'] = await _fetch(tables.PokemonNames, term, types.PokemonName)
    dct['pokedex_entries'] = await _fetch(tables.PokemonDexEntries, term, types.PokemonPokedexEntries)

    evolutions = await tables.PokemonEvolutions.fetch(term=term)
    dct['evolutions'] = [await pokemon(record['evolution']) for record in evolutions]

    dct['base_stats'] = await _fetch(tables.PokemonBaseStats, term, types.PokemonBaseStats)

    typing_dct = dict((await tables.PokemonTypes.fetchrow(term=term)).items())
    for key in typing_dct:
        if key == 'term' or typing_dct[key] is None:
            continue
        typing_dct[key] = await _fetch(tables.Types, typing_dct[key], types.Typing)
    dct['typing'] = types.PokemonTypings(*typing_dct.values())

    abilities_dct = dict((await tables.PokemonAbilities.fetchrow(term=term)).items())
    for key in abilities_dct:
        if key == 'term' or abilities_dct[key] is None:
            continue
        abilities_dct[key] = await ability(abilities_dct[key])
    dct['abilities'] = types.PokemonAbilities(*abilities_dct.values())

    return types.Pokemon(*dct.values())


async def typing(search_term: str) -> types.Typing:
    """Searches for a :class:`types.Typing`.

    Args:
        search_term (str): The term to search for
    """
    record = await _search(tables.Types, search_term)
    if record is None:
        return None

    return types.Typing(*record.values())


async def all_abilities() -> AsyncGenerator[types.Ability, str]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Ability` in the database.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Abilities._name}")

    for term in terms:
        yield await ability(term['term'])


async def all_items() -> AsyncGenerator[types.Item, str]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Item` in the database.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Items._name}")

    for term in terms:
        yield await item(term['term'])


async def all_moves() -> AsyncGenerator[types.Move, str]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Move` in the database.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Moves._name}")

    for term in terms:
        yield await move(term['term'])


async def all_pokemon() -> AsyncGenerator[types.Pokemon, str]:
    """Returns an :class:`AsyncGenerator` of all :class:`types.Pokemon` in the database.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Pokemon._name}")

    for term in terms:
        yield await pokemon(term['term'])


async def random_ability() -> types.Ability:
    """Returns a random :class:`types.Ability`.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Abilities._name}")

    return await ability(random.choice(terms)['term'])


async def random_item() -> types.Item:
    """Returns a random :class:`types.Item`.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Items._name}")

    return await item(random.choice(terms)['term'])


async def random_move() -> types.Move:
    """Returns a random :class:`types.Move`.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Moves._name}")

    return await move(random.choice(terms)['term'])


async def random_pokemon() -> types.Pokemon:
    """Returns a random :class:`types.Pokemon`.

    """
    async with MaybeAcquire() as connection:
        terms = await connection.fetch(f"SELECT term from {tables.Pokemon._name}")

    return await pokemon(random.choice(terms)['term'])
