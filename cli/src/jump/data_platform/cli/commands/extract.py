from typing import Any, Callable, TypeVar
from click import command, option, pass_context, Context, Choice
from pathlib import Path
from enum import StrEnum, auto
from textwrap import dedent
from csv import DictWriter
from halo import Halo
from dataclasses import dataclass

from ...sources.app import App
from ...sources.crm import CRM

from .source import Source


@dataclass
class Spec():

    table_name: str
    
    list_objs: Callable[[], list[Any]]

    column_names: list[str]

    transform_obj: Callable[[Any], dict[str, Any]]


@command()
@option("--source-folder", "-e", "source_folder_path", type=Path)
@option(
    "--sources", 
    "-s", 
    "sources", 
    type=Choice([source.value for source in Source]),
    callback=lambda context, param, values: [Source(value) for value in values],
    multiple=True,
    default=[source.value for source in Source]
)
@pass_context
def extract(context: Context, source_folder_path: Path | None, sources: list[Source]):
    source_folder_path = source_folder_path or context.obj.data_folder_path / "sources"
    source_folder_path.mkdir(parents=True, exist_ok=True)
    
    app = App(faker=context.obj.faker)
    users = app.list_users()
    crm = CRM(users=users, faker=context.obj.faker)

    for source in sources:
        match source:
            case Source.CRM:
                spinner = Halo(text=f"Extracting CRM table customers to CSV file... ", spinner="dots")
                spinner.start()
                write_csv_file(
                    source_folder_path / "customers.csv",
                    crm.list_customers(),
                    ["last_name", "first_name", "email", "satisfaction_score"],
                    lambda customer: {
                        "last_name": customer.last_name,
                        "first_name": customer.first_name,
                        "email": customer.email,
                        "satisfaction_score": customer.satisfaction_score,
                    }
                )
                spinner.stop_and_persist(symbol="✅".encode('utf-8'), text=f"Successfully extracted CRM table customers to CSV file! ")

            case Source.APP:
                app = App(faker=context.obj.faker)

                specs = [
                    Spec("users", lambda: app.list_users(), ["id", "first_name", "last_name", "email"], lambda user: {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                    }),
                    Spec("job_contracts", lambda: app.list_job_contracts(), ["id", "user_id", "entity", "start_date", "end_date"], lambda job_contract: {
                        "id": job_contract.id,
                        "user_id": job_contract.user.id,
                        "entity": job_contract.entity,
                        "start_date": job_contract.start_date.format("YYYY-MM-DD"),
                        "end_date": job_contract.end_date.format("YYYY-MM-DD") if ( end_date := job_contract.end_date ) else None,
                    }),
                    Spec("clients", lambda: app.list_clients(), ["id", "name"], lambda client: {
                        "id": client.id,
                        "name": client.name,
                    }),
                    Spec("invoices", lambda: app.list_invoices(), ["id", "job_contract_id", "client_id", "reference", "amount", "issue_date"], lambda invoice: {
                        "id": invoice.id,
                        "job_contract_id": invoice.job_contract.id,
                        "client_id": invoice.client.id,
                        "reference": invoice.reference,
                        "amount": invoice.amount,
                        "issue_date": invoice.issue_date.format("YYYY-MM-DD"),
                    }),
                ]

                for spec in specs:
                    spinner = Halo(text=f"Extracting App table {spec.table_name} to CSV file... ", spinner="dots")
                    spinner.start()
                    write_csv_file(
                        source_folder_path / f"{spec.table_name}.csv", 
                        spec.list_objs(), 
                        spec.column_names, 
                        spec.transform_obj,
                    )
                    spinner.stop_and_persist(symbol="✅".encode('utf-8'), text=f"Successfully extracted App table {spec.table_name} to CSV file! ")
                
            case _:
                raise Exception(f"Unknown source! ")


T = TypeVar("T")

def write_csv_file(
    file_path: Path, 
    rows: list[T], 
    column_names: list[str], 
    transform: Callable[[T], dict[str, Any]],
) -> None:
    with file_path.open("w") as f:
        writer = DictWriter(f, fieldnames=column_names)
        writer.writeheader()
        writer.writerows([transform(row) for row in rows])