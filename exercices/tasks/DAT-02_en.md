# **DAT-02** / Compute the NPS

## Context
The Care Team has sent surveys to various freelancers to gather satisfaction scores. They would now like to have access to the [NPS](https://www.qualtrics.com/fr/gestion-de-l-experience/client/nps/) calculated from these scores.


## Action
You should create a model that will give access to this indicator.


## Tips
1) The satisfaction score is an integer located in the `satisfaction_score` column of the [`intermediate__freelancers`](../dbt/models/intermediate/intermediate__freelancers.sql#L11)
2) You can write the model in [this file](../../dbt/models/marts/kpi/marts__kpi__nps.sql)

> 💡 Data are not versioned, so it is normal to have a single number as a result without any dimensions.
