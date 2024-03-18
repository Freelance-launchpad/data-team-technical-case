from pathlib import Path
from subprocess import run, CompletedProcess
from tempfile import TemporaryDirectory
import yaml
from os import environ
from enum import StrEnum, auto
from dataclasses import dataclass
import json

class ResourceType(StrEnum):

    ANALYSIS = auto()


@dataclass
class Resource():

    name: str

    file_path: Path


class DBT:

    def __init__(self, project_folder_path: Path, duckdb_file_path: Path, log_folder_path: Path, target_folder_path: Path):
        self._project_folder_path = project_folder_path
        self._duckdb_file_path = duckdb_file_path
        self._log_folder_path = log_folder_path
        self._target_folder_path = target_folder_path

    def build(self, /, *, 
        selector: str | None = None,
        select: str | list[str] | None
    ) -> None:
        selector_args = [f"--selector={selector}"] if selector else []

        match select:
            case None:
                select_args = []
            case str():
                select_args = [f"--select={select}"]
            case list():
                select_args = [f"--select={value}" for value in select]

        self._execute(["build"] + selector_args + select_args)

    def compile(self) -> None:
        self._execute(["compile"])

    def ls(self, /, *, resource_type: ResourceType | None) -> list[Resource]:
        resource_type_args = [f"--resource-type={resource_type}"] if resource_type else []
        process = self._execute(["ls"] + resource_type_args + ["--output=json", "--quiet"], capture_output=True, text=True)
        stdout = process.stdout
        lines = stdout.splitlines()
        objs = [json.loads(line) for line in lines]
        resources = [Resource(name=obj["name"], file_path=Path(obj["original_file_path"])) for obj in objs]
        return resources
        
    def _execute(self, other_args: list[str], **run_kwargs) -> CompletedProcess:
        profile_args = ["--profile=transient", "--target=transient"]
        
        command = ["dbt"] + other_args + profile_args

        with TemporaryDirectory(prefix="dbt_") as temp_folder_path_str:
            temp_folder_path = Path(temp_folder_path_str)

            profiles = {
                "transient": {
                    "outputs": {
                        "transient": {
                            "type": "duckdb",
                            "path": f"{self._duckdb_file_path.absolute()}",
                        }
                    },
                    "target": "transient",
                },
            }
            with ( temp_folder_path / "profiles.yml" ).open("w") as stream:
                yaml.dump(profiles, stream)

            run(
                ["dbt", "deps"], 
                env=environ | {
                    "DBT_PROJECT_DIR": f"{self._project_folder_path}",
                    "DBT_PROFILES_DIR": f"{temp_folder_path}",
                    "DBT_TARGET_PATH": f"{self._target_folder_path}",
                    "DBT_LOG_PATH": f"{self._log_folder_path}",
                },
                check=True
            )

            process = run(
                command, 
                env=environ | {
                    "DBT_PROJECT_DIR": f"{self._project_folder_path}",
                    "DBT_PROFILES_DIR": f"{temp_folder_path}",
                    "DBT_TARGET_PATH": f"{self._target_folder_path}",
                    "DBT_LOG_PATH": f"{self._log_folder_path}",
                }, 
                check=True, 
                **run_kwargs,
            )

            return process