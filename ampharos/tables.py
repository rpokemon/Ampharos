from collections import defaultdict
from collections.abc import Callable
from typing import Any

from donphan import Column, Enum, SQLType, Table


class Category(Enum):
    """An enumeration of Pokemon :class:`types.Move` categories."""

    PHYSICAL = 1
    SPECIAL = 2
    STATUS = 3
    VARIES = 4


class Typing(Enum):
    """An enumeration of types."""

    NORMAL = 1
    FIGHTING = 2
    FLYING = 3
    POISON = 4
    GROUND = 5
    ROCK = 6
    BUG = 7
    GHOST = 8
    STEEL = 9
    FIRE = 10
    WATER = 11
    GRASS = 12
    ELECTRIC = 13
    PSYCHIC = 14
    ICE = 15
    DRAGON = 16
    DARK = 17
    FAIRY = 18


class Abilities(Table, _name="abilities", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    name: Column[SQLType.Text] = Column(nullable=False)
    description: Column[SQLType.Text]
    introduced: Column[SQLType.Integer]


class Items(Table, _name="items", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    name: Column[SQLType.Text] = Column(nullable=False)
    description: Column[SQLType.Text]


class Moves(Table, _name="moves", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    type: Column[Typing] = Column(nullable=False)
    name: Column[SQLType.Text] = Column(nullable=False)
    description: Column[SQLType.Text]
    pp: Column[SQLType.SmallInt]
    power: Column[SQLType.SmallInt]
    accuracy: Column[SQLType.SmallInt]
    category: Column[Category]


class Pokemon(Table, _name="pokemon", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    dex_no: Column[SQLType.SmallInt] = Column(nullable=False)
    classification: Column[SQLType.Text]


class PokemonNames(Table, _name="pokemonnames", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    english: Column[SQLType.Text] = Column(nullable=False)
    japanese: Column[SQLType.Text]
    kana: Column[SQLType.Text]


class PokemonEvolutions(Table, _name="pokemonevolutions", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    evolution: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)


class PokemonDexEntries(Table, _name="pokemondexentries", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    sun: Column[SQLType.Text]
    moon: Column[SQLType.Text]


class PokemonTypes(Table, _name="pokemontypes", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    first: Column[Typing] = Column(nullable=False)
    second: Column[Typing]


class PokemonAbilities(Table, _name="pokemonabilities", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    first: Column[SQLType.Text] = Column(references=Abilities.term)
    second: Column[SQLType.Text] = Column(references=Abilities.term)
    hidden: Column[SQLType.Text] = Column(references=Abilities.term)


class PokemonBaseStats(Table, _name="pokemonbasestats", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    hp: Column[SQLType.SmallInt]
    attack: Column[SQLType.SmallInt]
    defense: Column[SQLType.SmallInt]
    special_attack: Column[SQLType.SmallInt]
    special_defense: Column[SQLType.SmallInt]
    speed: Column[SQLType.SmallInt]


ALL_TABLES: list[type[Table]] = [
    Abilities,
    Items,
    Moves,
    Pokemon,
    PokemonEvolutions,
    PokemonDexEntries,
    PokemonNames,
    PokemonTypes,
    PokemonAbilities,
    PokemonBaseStats,
]

TRANSFORMERS: dict[type[Table], dict[str, Callable[[Any], Any]]] = defaultdict(dict)

for table in ALL_TABLES:
    for column in Table._columns:
        if issubclass(column.py_type, Enum):
            TRANSFORMERS[table][column.name] = lambda x: column.py_type[x]
