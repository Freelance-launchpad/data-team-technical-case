# **DAT-03** / Extract turnover by month and by cohort


## Context
As part of the audit, the auditor analyzes the invoices issued by freelancers. He conducts his analysis by cohort, with the cohort being the month when the freelancer joined Jump.


## Action
He urgently requested an ad-hoc extraction to obtain the revenue of freelancers by cohort and month. He wants a table that looks like this:

| Freelancer Last Name | Freelancer First Name | Cohort | Entity | Month | Turnover (in €) |
|:-:|:-:|:-:|:-:|:-:|:-:|
| DUPOND | Albert | 2022/02 | blue | 2022/04 | 34,15 |
| ... | ... | ... | ... | ... | ... |

Note that even if a freelancer has no activity for a given month (i.e., no invoices for a given month), the auditor still wants to see `0` in the _Turnover (in €)_ column.


## Tips
1) You can rely on the [`intermediate__freelancers`](../../dbt/models/intermediate/intermediate__freelancers.sql), [`intermediate__job_contracts`](../../dbt/models/intermediate/intermediate__job_contracts.sql) and [`intermediate__invoices`](../../dbt/models/intermediate/intermediate__invoices.sql) models
2) You can write the SQL query in [this file](../../dbt/analyses/turnovers_by_cohort_for_auditor.sql)
3) The analysis will be exported as a CSV file during the export phase (which is also run within GitHub Actions)