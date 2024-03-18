from pathlib import Path
import duckdb
from textwrap import dedent
from typing import overload, Literal, Any


class DuckDB:

    def __init__(self, file_path: Path):
        self._file_path = file_path

    def __enter__(self):
        self._connection = duckdb.connect(database=f"{self._file_path}")
        return self
    
    def __exit__(self, *args, **kwargs):
        self._connection.close()
        self._connection = None

    def create_schema(self, schema: str) -> None:
        if ( connection := self._connection ):
            connection.execute(
                dedent("""\
                    CREATE SCHEMA IF NOT EXISTS 
                        {schema}
                """).format(schema=schema)
            )

    @overload
    def execute(self, sql: str, *, fetch: Literal[False]) -> None:
        ...

    @overload
    def execute(self, sql: str, *, fetch: Literal[True]) -> list[dict[str, Any]]:
        ...

    def execute(self, sql: str, fetch: bool = False) -> None | list[dict[str, Any]]:
        if ( connection := self._connection ):
            connection = connection.execute(sql)
            if fetch:
                column_names = [column[0] for column in connection.description]
                return [dict(zip(column_names, row)) for row in connection.fetchall()]
        return None