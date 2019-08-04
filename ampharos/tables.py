from dataclasses import dataclass
from typing import Dict, List, Union

from donphan import Table, Column


class Abilities(Table, schema="pokemon"):
    term: str = Column(primary_key=True)
    name: str
    description: str
    introduced: int


class Items(Table, schema="pokemon"):
    term: str = Column(primary_key=True)
    name: str
    description: str


class Types(Table, schema="pokemon"):
    term: str = Column(primary_key=True)
    name: str


class Moves(Table, schema="pokemon"):
    term: str = Column(primary_key=True)
    type: str = Column(references=Types.term)
    name: str
    description: str
    pp: int
    power: int
    accuracy: int
    category: int


class Pokemon(Table, schema="pokemon"):
    term: str = Column(primary_key=True)
    dex_no: int
    classification: str


class PokemonNames(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    english: str
    japanese: str
    kana: str


class PokemonEvolutions(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    evolution: str = Column(primary_key=True, references=Pokemon.term)


class PokemonDexEntries(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    sun: str
    moon: str


class PokemonTypes(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    first: str = Column(references=Types.term)
    second: str = Column(references=Types.term)


class PokemonAbilities(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    first: str = Column(references=Abilities.term)
    second: str = Column(references=Abilities.term)
    hidden: str = Column(references=Abilities.term)


class PokemonBaseStats(Table, schema="pokemon"):
    term: str = Column(primary_key=True, references=Pokemon.term)
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int


tables = [
    Abilities,
    Items,
    Types,
    Moves,
    Pokemon,
    PokemonEvolutions,
    PokemonDexEntries,
    PokemonNames,
    PokemonTypes,
    PokemonAbilities,
    PokemonBaseStats
]
