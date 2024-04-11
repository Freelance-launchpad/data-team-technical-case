> 🇬🇧 You'll find the english version [here](./README_en.md)! 

# Data Team / Exercice technique

> 👋 Bienvenue à toi ! Tu vas trouver ici tout le contexte dont tu as besoin pour réaliser le test technique qui fait parti du processus de recrutement chez Jump. 

## Présentation

### La Data Platform
Ce dépôt contient l'ensemble du code qui constitue la Data Platform. La Data Platform constitue **l'ensemble des moyens techniques mis en oeuvre pour répondre aux besoins qui nécessitent l'exploitation de la donnée chez Jump** (rapports et dashboards, extractions ad-hoc, etc.) 

La clé de voute de la Data Platform est le Lakehouse : c'est une base de donnée analytique qui est composée de 4 couches :
* La couche Sources qui contient une copie de **l'ensemble des données brutes** issue des applications utilisées chez Jump (l'application dévelopée par les équipes Backend et Frontend, le CRM administré par l'équipe Sales, etc.)
* La couche Staging qui est très similaire à la couche précédente mais contient **quelques étapes de nettoyage, de filtrage**, etc. ;
* La couche Intermediate qui s'appuie sur la couche précédente et contient **un modèle homogène et cohérent qui couvre l'ensemble du périmètre fonctionnel** adressé par Jump (facturation, CDI des salariés portés, etc.) ;
* Le couche Marts qui contient **des modèles plus complexes mais à forte valeur ajoutée** nécessaires pour répondre à des besoins fonctionnels plus poussés. 

![Architecture](docs/architecture_fr.png)


> 💡 Bien que ce dépôt existe que dans le cadre du test technique, l'architecture que l'on a en interne est très semblable à celle décrite ici (même s'il y a plus que 2 applications à intégrer que les problématiques sont beaucoup plus larges).


### Le modèle de données

Le business de Jump est assez simple : 
* Un CDI chez Jump est materialisé par :
    * Une date de début,
    * Une date de fin,
    * Une entité (qui peut être `blue` si le freelance souscrit à Jump Blue ou `green` s'il souscrit à Jump Green) ;
* Un freelance peut avoir plusieurs CDI (à condition que les dates entre deux CDI ne se chevauchent pas) ;
* Dans le cadre de son CDI, un freelance peut facturer un client.

![Modèle de données](docs/data-model.png)


## Détails technique

### Composants

La Data Platform s'appuie sur les technologies suivantes : 
* Le Lakehouse est **une base de données [DuckDB](https://duckdb.org/)** :
    * Le fichier se trouve dans `./data/lakehouse/lakehouse.duckdb`, 
    * Chacune des couches logiques citées ci-dessus est un schéma ;
* L'ensemble des transformations est réalisé **à l'aide de [DBT](https://www.getdbt.com/)** grâce à [ce projet](./dbt/) ;
* Une [CLI](./cli) en Python qui orchestre les différentes étapes d'alimentation de la Data Platform :
    * L'étape `extract` pour extraire les données depuis les applications sous forme de fichiers CSV dans le dossier `./data/sources`, 
    * L'étape `load` pour charger les données extraites dans le schéma `sources` du Lakehouse (qui va aller se trouver dans `./data/lakehouse`), 
    * L'étape `transform` pour alimenter les schémas `staging`, `intermediate` et `marts`.

> ⚠️ Naturellement, dans le cadre du test technique, on extrait les données d'aucune application. Elles sont en réalité générées aléatoirement par la CLI ([ici](./cli/src/jump/data_platform/sources/app/app.py) et [là](./cli/src/jump/data_platform/sources/crm/crm.py)).



### Utilisation

### TL;DR...

Pour pouvoir lancer les commandes, tu auras besoin de Docker et de Make. 

Pour construire l'image Docker qui contient la Data Platform et lancer une chaine d'alimentation complète, tu as juste à lancer la commande `make` (sans argument). 

> 💥 La commande `make` seule doit fonctionner sans aucune erreur... Si tu rencontre la moindre erreur, contacte-nous : cela ne devrait pas arriver !

Si tu veux plus de détails sur les targets disponibles, tu peux lancer `make help`. 


### Et en plus long ? 

La conteneurisation est faite à l'aide de Docker et de [ce Dockerfile](./docker/Dockerfile) et toutes les commandes pour builder sont embarquées dans [ce Makefile](./Makefile).

 Les targets suivantes sont disponibles :
* `make build` : construit l'image Docker qui embarque la CLI, le projet DBT, etc.
* `make extract` : lance l'extract des données de l'application et du CRM
* `make load` : lance l'inégration des extractions dans le schéma `source` du Lakehouse
* `make transform` : transforme les données et alimente les schémas `staging`, `intermediate` et `marts` (à l'aide du [projet DBT](./dbt/))
* `make export`: exporte les analyses DBT au format CSV
* `make query` : lance le REPL de DuckDB pour requêter le lakehouse

> N'hésite pas à explorer les données en parcourant le [projet DBT](./dbt/) et en requêtant les tables avec `make query`.


A noter qu'un [workflow GitHub Action](https://github.com/Freelance-launchpad/data-team-technical-case/actions) est également présent. Il est en charge de :
* Lancer les commandes ci-dessus
* Mettre à disposition les exports des analyses DBT (au format CSV) et le Lakehouse (au format DuckDB)

> 💡 Assure-toi bien que les modifications que tu apportes au projet ne mettent pas le workflow en échec !

> ❓ Tout est clair ? Si oui, retrouve [ici](./exercices/positions/data-analyst_fr.md) les exercices à réaliser ! 
