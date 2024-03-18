from click import command, option, pass_context, Context, Choice
from subprocess import run
from pathlib import Path
from halo import Halo
from typing import Any
from csv import DictWriter

from ...tools import DBT, DuckDB, ResourceType

from .layer import Layer


@command()
@option(
    "--lakehouse-folder", "lakehouse_folder_path", 
    type=Path, 
)
@option(
    "--dbt-target-folder", "dbt_target_folder_path",
    type=Path,
)
@option(
    "--dbt-project-folder", "dbt_project_folder_path",
    type=Path,
)
@option(
    "--dbt-log-folder", "dbt_log_folder_path",
    type=Path,
)
@option(
    "--output-folder", "output_folder_path",
)
@pass_context
def export(
    context: Context, 
    lakehouse_folder_path: Path | None, 
    dbt_project_folder_path: Path | None,
    dbt_target_folder_path: Path | None, 
    dbt_log_folder_path: Path | None,
    output_folder_path: Path | None,
):
    lakehouse_folder_path = lakehouse_folder_path or context.obj.data_folder_path / "lakehouse"
    duckdb_file_path = lakehouse_folder_path / "lakehouse.duckdb"
    dbt_project_folder_path = dbt_project_folder_path or context.obj.project_folder_path / "dbt"

    dbt_target_folder_path = dbt_target_folder_path or context.obj.data_folder_path / "dbt"
    dbt_target_folder_path.mkdir(parents=True, exist_ok=True)
    
    dbt_log_folder_path = dbt_log_folder_path or context.obj.log_folder_path / "dbt"
    dbt_log_folder_path.mkdir(parents=True, exist_ok=True)

    output_folder_path = output_folder_path or context.obj.data_folder_path / "exports"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    dbt = DBT(
        project_folder_path=dbt_project_folder_path, 
        duckdb_file_path=duckdb_file_path,
        log_folder_path=dbt_log_folder_path,
        target_folder_path=dbt_target_folder_path,
    )

    dbt.compile()
    resources = dbt.ls(resource_type=ResourceType.ANALYSIS)
    with DuckDB(duckdb_file_path) as duckdb:
        for resource in resources:
            spinner = Halo(text=f"Exporting {resource.name}... ", spinner="dots")
            spinner.start()
            sql_query = ( dbt_target_folder_path / "compiled" / "lakehouse" / resource.file_path ).read_text()
            objs = duckdb.execute(sql_query, fetch=True)
            write_to_csv(objs, output_folder_path / ( resource.file_path.stem + ".csv" ))
            spinner.stop_and_persist(symbol="✅".encode('utf-8'), text=f"Successfully exported {resource.name}! ")


def write_to_csv(objs: list[dict[str, Any]], file_path: Path) -> None:
    if len(objs) == 0:
        return None
    
    keys = objs[0].keys()
    with file_path.open("w") as file:
        dict_writer = DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(objs)