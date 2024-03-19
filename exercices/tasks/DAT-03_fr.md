# **DAT-03** / Extraire le chiffre d'affaire par mois et par cohortes


## Contexte
Dans le cadre de l'audit, le commissaire aux compte fait des analyses sur les factures réalisées par les freelances. Il réalise son analyse par cohort, la cohort étant le mois d'arrivé du freelance chez Jump.


## Action
Il a demandé en urgence une extraction ad-hoc pour avoir le chiffre d'affaire des freelances par cohorte et par mois. Il veut un tableau qui ressemble à :

| Nom du freelance | Prénom du freelance | Cohort | Entité | Mois | Chiffre d'affaire (en €) |
|:-:|:-:|:-:|:-:|:-:|:-:|
| DUPOND | Albert | 2022/02 | blue | 2022/04 | 34,15 |
| ... | ... | ... | ... | ... | ... |

A noter que même si un freelance n'a pas d'activité pour un mois donné (ie. pas de factures pour un mois donné), alors le commissaire aux comptes veut quand même voir `0` dans la colonne _Chiffre d'affaire (en €)_.


## Tips
1) Tu peux t'appuyer sur les modèles [`intermediate__freelancers`](../../dbt/models/intermediate/intermediate__freelancers.sql), [`intermediate__job_contracts`](../../dbt/models/intermediate/intermediate__job_contracts.sql) et [`intermediate__invoices`](../../dbt/models/intermediate/intermediate__invoices.sql) ;
2) Tu peux écrire la requête SQL dans [ce fichier](../../dbt/analyses/turnovers_by_cohort_for_auditor.sql)
3) L'analyse va être lancée et exportée au format CSV durant la phase d'export (qui est églament lancée par GitHub Actions)