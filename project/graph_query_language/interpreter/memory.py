from typing import List, Dict

from project.graph_query_language.interpreter.gql_exceptions import (
    VariableNotFoundException,
)
from project.graph_query_language.interpreter.gql_types.base_type import BaseType


class Memory:
    def __init__(self):
        self.tables: List[Dict[str:BaseType]] = [{}]

    def create_next_scope(self):
        new_table = Memory()
        new_table.tables = self.tables.copy()
        new_table.tables.append({})
        return new_table

    def remove_last_scope(self):
        new_table = Memory()
        new_table.tables = self.tables.copy()
        new_table.tables = new_table.tables[:-1]
        return new_table

    def add_variable(self, name: str, value: BaseType, level: int = -1):
        if level >= len(self.tables):
            for _ in range(level - len(self.tables) + 1):
                self.tables.append({})

        self.tables[level][name] = value

    def find_variable(self, name: str):
        scope_level = len(self.tables) - 1
        while scope_level >= 0:
            value = self.tables[scope_level].get(name)
            if value is not None:
                return value
            scope_level -= 1
        raise VariableNotFoundException(name=name)
