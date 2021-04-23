from typing import List, Type

from donphan import Table, SQLType, Column


class Abilities(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True)
    name: SQLType.Text
    description: SQLType.Text
    introduced: SQLType.Integer


class Items(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True)
    name: SQLType.Text
    description: SQLType.Text


class Types(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True)
    name: SQLType.Text


class Moves(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True)
    type: SQLType.Text = Column(references=Types.term)
    name: SQLType.Text
    description: SQLType.Text
    pp: SQLType.SmallInt
    power: SQLType.SmallInt
    accuracy: SQLType.SmallInt
    category: SQLType.SmallInt


class Pokemon(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True)
    dex_no: SQLType.SmallInt
    classification: SQLType.Text


class PokemonNames(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    english: SQLType.Text
    japanese: SQLType.Text
    kana: SQLType.Text


class PokemonEvolutions(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    evolution: SQLType.Text = Column(primary_key=True, references=Pokemon.term)


class PokemonDexEntries(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    sun: SQLType.Text
    moon: SQLType.Text


class PokemonTypes(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    first: SQLType.Text = Column(references=Types.term)
    second: SQLType.Text = Column(references=Types.term)


class PokemonAbilities(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    first: SQLType.Text = Column(references=Abilities.term)
    second: SQLType.Text = Column(references=Abilities.term)
    hidden: SQLType.Text = Column(references=Abilities.term)


class PokemonBaseStats(Table, schema="ampharos"):  # type: ignore[call-arg]
    term: SQLType.Text = Column(primary_key=True, references=Pokemon.term)
    hp: SQLType.SmallInt
    attack: SQLType.SmallInt
    defense: SQLType.SmallInt
    special_attack: SQLType.SmallInt
    special_defense: SQLType.SmallInt
    speed: SQLType.SmallInt


ALL_TABLES: List[Type[Table]] = [
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
    PokemonBaseStats,
]
