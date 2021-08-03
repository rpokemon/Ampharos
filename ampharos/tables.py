from typing import List, Type

from donphan import Table, SQLType, Column


class Abilities(Table, _name="abilities", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    name: Column[SQLType.Text]
    description: Column[SQLType.Text]
    introduced: Column[SQLType.Integer]


class Items(Table, _name="items", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    name: Column[SQLType.Text]
    description: Column[SQLType.Text]


class Types(Table, _name="types", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    name: Column[SQLType.Text]


class Moves(Table, _name="moves", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    type: Column[SQLType.Text] = Column(references=Types.term)
    name: Column[SQLType.Text]
    description: Column[SQLType.Text]
    pp: Column[SQLType.SmallInt]
    power: Column[SQLType.SmallInt]
    accuracy: Column[SQLType.SmallInt]
    category: Column[SQLType.SmallInt]


class Pokemon(Table, _name="pokemon", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True)
    dex_no: Column[SQLType.SmallInt]
    classification: Column[SQLType.Text]


class PokemonNames(Table, _name="pokemonnames", schema="ampharos"):
    term: Column[SQLType.Text] = Column(primary_key=True, references=Pokemon.term)
    english: Column[SQLType.Text]
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
    first: Column[SQLType.Text] = Column(references=Types.term)
    second: Column[SQLType.Text] = Column(references=Types.term)


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
