from click import group, version_option, Context, option, pass_context
from types import SimpleNamespace
from faker import Faker
from pathlib import Path

from ..version import __version__

from .commands import extract, load, transform, export


@group(chain=True)
@version_option(version=__version__)
@option("--random-seed", "-r", "random_seed", type=int, default=42)
@option("--project-folder", "-p", "project_folder_path", type=Path, default=Path("/usr/local/lib/data-platform"))
@option("--data-folder", "-d", "data_folder_path", type=Path, default=Path("/var/local/lib/data-platform"))
@option("--log-folder", "-l", "log_folder_path", type=Path, default=Path("/var/log/data-platform"))
@pass_context
def app(context: Context, random_seed: int, project_folder_path: Path, data_folder_path: Path, log_folder_path: Path):
    context.obj = SimpleNamespace()
    context.obj.random_seed = random_seed
    context.obj.faker = Faker()
    Faker.seed(random_seed)
    context.obj.project_folder_path = project_folder_path
    context.obj.data_folder_path = data_folder_path
    context.obj.log_folder_path = log_folder_path


for command in [extract, load, transform, export]:
    app.add_command(command)