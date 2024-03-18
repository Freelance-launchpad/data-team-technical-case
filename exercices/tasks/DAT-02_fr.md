# **DAT-02** / Calculer le NPS

## Contexte
L'équipe de support a envoyé des sondages aux différents freelances pour recueillir un score de satisfaction. 
Ils aimeraient à présent avoir accès au [NPS](https://www.qualtrics.com/fr/gestion-de-l-experience/client/nps/) calculé à partir de ce score.


## Action
Tu dois créer un model qui permet d'avoir accès à cet indicateur.


## Tips
1) Le score de satisfaction est un entier qui se trouve dans la colonne `satisfaction_score` du modèle [`intermediate__freelancers`](../dbt/models/intermediate/intermediate__freelancers.sql#L11)
2) Tu peux écrire le model dans [ce fichier](../../dbt/models/marts/kpi/marts__kpi__nps.sql)

> 💡 Les données ne sont pas historisées, c'est donc normal que tu n'aies en résultat qu'un nombre seul, sans aucune dimension.
