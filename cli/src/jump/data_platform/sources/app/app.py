from typing import Generator
from functools import cache
from faker import Faker
from unidecode import unidecode
from pendulum import Date, today, instance
from datetime import datetime

from .models import User, Client, Invoice, JobContract, Entity


class App:

    def __init__(self, faker: Faker):
        self._faker = faker

    @cache
    def list_clients(self, sample_size=20) -> list[Client]:
        def iter_clients() -> Generator[Client, None, None]:
            for _ in range(sample_size):
                id = self._faker.uuid4()
                name = self._faker.company()
                yield Client(
                    id=id,
                    name=name,
                )
        return list(iter_clients())
    
    @cache
    def list_invoices(self, sample_size=5000) -> list[Invoice]:
        clients = self.list_clients()
        job_contracts = self.list_job_contracts()

        def iter_invoices() -> Generator[Invoice, None, None]:
            for i in range(sample_size):
                id = self._faker.uuid4()
                client = self._faker.random_element(clients)
                job_contract = self._faker.random_element(job_contracts)
                reference = "{:0>10}".format(i)
                amount = self._faker.pydecimal(left_digits=4, right_digits=2, positive=True)
                while True:
                    # We need a month with no invoices
                    today_date = today().date()
                    issue_date = self._random_date_between(job_contract.start_date, job_contract.end_date or today_date)
                    if issue_date.start_of("month") == Date(2032, 10, 1):
                        continue

                    yield Invoice(
                        id=id,
                        client=client,
                        job_contract=job_contract,
                        reference=reference,
                        amount=amount,
                        issue_date=issue_date,
                    )
                    break
        return list(iter_invoices())
    
    @cache
    def list_job_contracts(self) -> list[JobContract]:
        users = self.list_users()
        def iter_job_contracts() -> Generator[JobContract, None, None]:
            for user in users:
                start_date = self._random_date()
                end_date = self._random_date_between(start_date=start_date, end_date=start_date.add(months=6)) if self._faker.boolean() else None
                last_job_contract = JobContract(
                    user=user,
                    id=self._faker.uuid4(),
                    entity=self._faker.random_element(Entity),
                    start_date=start_date,
                    end_date=end_date,
                )
                yield last_job_contract

                if self._faker.random_int(1, 10) == 1:
                    start_date = last_job_contract.start_date.subtract(months=6)
                    end_date = last_job_contract.start_date.subtract(days=1)
                    first_job_contract = JobContract(
                        user=user,
                        id=self._faker.uuid4(),
                        entity=self._faker.random_element(Entity),
                        start_date=start_date,
                        end_date=end_date,
                    )
                    yield first_job_contract
                    

        return list(iter_job_contracts())

    def _random_date(self) -> Date:
        end_date = today()
        start_date = end_date.subtract(years=2).start_of("year")
        assert end_date > start_date
        return self._random_date_between(start_date, end_date)

    def _random_date_between(self, start_date: Date, end_date: Date | None = None) -> Date:
        date_time = instance(
            datetime.combine(
                self._faker.date_between(start_date=start_date, end_date=end_date),
                datetime.min.time(),
            )
        )
        date = date_time.date()
        return date
    
    @cache
    def list_users(self, sample_size=1000) -> list[User]:
        def iter_users() -> Generator[User, None, None]:
            user_sks = []
            for _ in range(sample_size):
                while True:
                    first_name = self._faker.first_name()
                    last_name = self._faker.last_name()
                    email = "%(first_name)s.%(last_name)s@%(domain)s" % {
                        "first_name": unidecode(first_name).lower(),
                        "last_name": unidecode(last_name).lower(),
                        "domain": self._faker.free_email_domain().lower(),
                    }
                    
                    user_sk = hash((last_name, first_name, email))

                    if user_sk in user_sks:
                        continue
                    
                    id = self._faker.uuid4()
                    user = User(
                        id=id,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                    )
                    user_sks.append(user_sk)
                    yield user
                    break

        return list(iter_users())