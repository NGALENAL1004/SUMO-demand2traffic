<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Assigning vehicle emission classes

This folder estimates the local passenger-car fleet composition and assigns a
SUMO HBEFA4 emission class to each person who uses a car in the converted
population.

The complete workflow is implemented in `vehicles.ipynb`.

## Files retained in the repository

```text
5-vehicles/
|-- README.md
|-- vehicles.ipynb
|-- input/
|   `-- README.md
`-- output_tools/
    `-- README.md
```

The large national fleet table, reference PDFs, generated route file, and
person-level assignment table remain local.

## Required inputs

| Input | Expected location | Purpose |
|---|---|---|
| `Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2025-09.csv` | `input/` | Commune-level fleet by fuel, Crit'Air class, user status, and vehicle category |
| `document-travail-67-methodologie-rsvero-mars2024.pdf` | `input/` | RSVERO methodological reference |
| `Tableau de classification - voitures particulières.pdf` | `input/` | Official Crit'Air classification reference |
| `population_all.rou.xml` | `../4-convert_trips/` | Converted SUMO person plans |

Download instructions, authoritative links, and reference checksums are
provided in [`input/README.md`](input/README.md).

## Prerequisites

- Python and Jupyter;
- `pandas`;
- `matplotlib`;
- enough memory to process the national CSV in chunks.

No SUMO Python import is required by this notebook, but the assigned
`emissionClass` identifiers must exist in the SUMO version used for the final
simulation.

## Part 1 — Analyse the passenger-car fleet

The notebook reads the national CSV in chunks of 200,000 rows and retains:

- the 28 INSEE municipality codes of the Communauté d’agglomération de La
  Rochelle;
- vehicle category `VP` (passenger cars);
- the `PARC_2022` fleet-count column.

It aggregates vehicles by `CARBURANT` and `CRIT_AIR`, plots the distribution,
and maps each observed combination to one approximate SUMO HBEFA4 class.

### Reference analysis

The saved execution reports:

- 863 filtered source rows;
- 19 observed fuel/Crit'Air combinations;
- 108,142 passenger cars in `PARC_2022`.

The Crit'Air-to-Euro and fuel-to-HBEFA4 conversion is a modelling
approximation. In particular:

- Crit'Air 1 is represented by a recent Euro proxy;
- non-rechargeable hybrids are approximated by conventional fuel classes;
- gas vehicles are assumed to use an LPG class;
- unknown or unclassified vehicles use conservative fallback classes.

These assumptions must be reported and reviewed if the emission analysis is a
central scientific result.

## Part 2 — Assign exact quotas to SUMO car users

The last notebook cell reads:

```text
../4-convert_trips/population_all.rou.xml
```

It then:

1. identifies every person with at least one `personTrip` whose `modes`
   contains `car`;
2. creates one SUMO `<vType>` for each configured HBEFA4 class;
3. calculates exact integer quotas with the largest-remainder method;
4. uses SHA-256 and the fixed seed `fleet_exact_v1` to produce a stable
   person ordering;
5. gives each car user one emission class;
6. writes the corresponding `vTypes` attribute to all of that person's car
   trips;
7. exports the modified population and the person-to-class table.

### Important configuration point

The assignment cell uses the manually defined `DIST` list. It does **not**
automatically reuse the `df_prop` proportions calculated in the analysis
cells above.

Before every production run, compare `DIST` with the intended reference
distribution and update it if necessary. The percentages must sum to exactly
100%. Changing `SEED` changes the individual allocation while preserving the
class quotas.

The `DIST` currently saved in the notebook is:

| HBEFA4 class | Share (%) |
|---|---:|
| `HBEFA4/PC_petrol_Euro-6ab` | 26.99 |
| `HBEFA4/PC_diesel_Euro-6ab` | 32.15 |
| `HBEFA4/PC_diesel_Euro-4` | 15.23 |
| `HBEFA4/PC_petrol_Euro-4` | 5.92 |
| `HBEFA4/PC_petrol_Euro-3` | 6.43 |
| `HBEFA4/PC_diesel_Euro-3` | 6.66 |
| `HBEFA4/PC_BEV` | 1.33 |
| `HBEFA4/PC_petrol_Euro-1` | 1.89 |
| `HBEFA4/PC_PHEV_petrol_Euro-6ab_(P)` | 0.62 |
| `HBEFA4/PC_LPG_petrol_Euro-6_(LPG)` | 0.61 |
| `HBEFA4/PC_diesel_Euro-2` | 1.41 |
| `HBEFA4/PC_diesel_Euro-1` | 0.76 |

## Outputs

| Output | Description |
|---|---|
| `population_all_with_vtypes.rou.xml` | SUMO population with HBEFA4 `<vType>` definitions and `vTypes` references |
| `output_tools/person_to_emissionClass.csv` | Person ID, emission class, and SUMO vehicle-type ID |

The reference run found 10,569 car users and inserted 12 vehicle types.
Because exact integer quotas are used, the number assigned to every class can
be reproduced from the population size, `DIST`, and the seed.

## Quality checks

Before the simulation:

- verify that `DIST` sums to 100%;
- compare the configured distribution with the computed local fleet table;
- confirm that every car user appears once in
  `person_to_emissionClass.csv`;
- confirm that every car `personTrip` has a valid `vTypes` reference;
- check that all referenced `vType` identifiers are defined at the start of
  the XML;
- validate the HBEFA4 identifiers with the installed SUMO version.

See the official
[SUMO emissions documentation](https://sumo.dlr.de/docs/Models/Emissions.html)
for model coverage and output units.

## Git policy

Only the notebook, bilingual documentation, and Git exclusion rules are
retained. Source datasets and generated files are documented but not
committed.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Attribution des classes d’émissions des véhicules

Ce dossier estime la composition locale du parc de voitures particulières et
attribue une classe d’émissions HBEFA4 de SUMO à chaque personne utilisant une
voiture dans la population convertie.

La chaîne complète se trouve dans `vehicles.ipynb`.

## Fichiers conservés dans le dépôt

```text
5-vehicles/
|-- README.md
|-- vehicles.ipynb
|-- input/
|   `-- README.md
`-- output_tools/
    `-- README.md
```

La grande table nationale, les PDF de référence, le fichier d’itinéraires
généré et la table d’attribution individuelle restent locaux.

## Entrées nécessaires

| Entrée | Emplacement attendu | Rôle |
|---|---|---|
| `Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2025-09.csv` | `input/` | Parc communal par carburant, classe Crit'Air, statut d’utilisateur et catégorie |
| `document-travail-67-methodologie-rsvero-mars2024.pdf` | `input/` | Référence méthodologique RSVERO |
| `Tableau de classification - voitures particulières.pdf` | `input/` | Référence officielle de classification Crit'Air |
| `population_all.rou.xml` | `../4-convert_trips/` | Plans de personnes SUMO convertis |

Les consignes de téléchargement, liens officiels et empreintes de référence
sont fournis dans [`input/README.md`](input/README.md).

## Prérequis

- Python et Jupyter ;
- `pandas` ;
- `matplotlib` ;
- suffisamment de mémoire pour traiter le CSV national par blocs.

Le notebook n’importe pas directement les bibliothèques Python de SUMO, mais
les identifiants `emissionClass` attribués doivent exister dans la version de
SUMO utilisée pour la simulation finale.

## Partie 1 — Analyser le parc de voitures particulières

Le notebook lit le CSV national par blocs de 200 000 lignes et conserve :

- les 28 codes INSEE des communes de la Communauté d’agglomération de La
  Rochelle ;
- la catégorie `VP`, correspondant aux voitures particulières ;
- la colonne d’effectif `PARC_2022`.

Il agrège les véhicules par `CARBURANT` et `CRIT_AIR`, représente leur
distribution et associe chaque combinaison observée à une classe HBEFA4 SUMO
approximative.

### Analyse de référence

L’exécution enregistrée indique :

- 863 lignes sources filtrées ;
- 19 combinaisons carburant/Crit'Air observées ;
- 108 142 voitures particulières dans `PARC_2022`.

La conversion de Crit'Air et des carburants vers HBEFA4 est une approximation
de modélisation. En particulier :

- Crit'Air 1 est représentée par une classe Euro récente approchée ;
- les hybrides non rechargeables sont assimilés à des motorisations
  conventionnelles ;
- les véhicules gaz sont supposés relever d’une classe GPL ;
- les véhicules inconnus ou non classés utilisent des classes de repli
  prudentes.

Ces hypothèses doivent être mentionnées et réévaluées si l’analyse des
émissions constitue un résultat scientifique central.

## Partie 2 — Attribuer des quotas exacts aux automobilistes SUMO

La dernière cellule lit :

```text
../4-convert_trips/population_all.rou.xml
```

Elle :

1. identifie chaque personne ayant au moins un `personTrip` dont `modes`
   contient `car` ;
2. crée un `<vType>` SUMO pour chaque classe HBEFA4 configurée ;
3. calcule des quotas entiers exacts par la méthode des plus forts restes ;
4. utilise SHA-256 et la graine fixe `fleet_exact_v1` pour produire un ordre
   stable des personnes ;
5. attribue une classe d’émissions à chaque automobiliste ;
6. ajoute l’attribut `vTypes` à tous les trajets en voiture de cette personne ;
7. exporte la population modifiée et la table personne-classe.

### Point de configuration important

La cellule d’attribution utilise la liste `DIST` définie manuellement. Elle ne
réutilise **pas automatiquement** les proportions `df_prop` calculées dans les
cellules d’analyse précédentes.

Avant chaque exécution de production, comparer `DIST` à la distribution de
référence souhaitée et la mettre à jour si nécessaire. Les pourcentages
doivent totaliser exactement 100 %. Modifier `SEED` change l’attribution
individuelle tout en conservant les quotas de classes.

La liste `DIST` actuellement enregistrée est :

| Classe HBEFA4 | Part (%) |
|---|---:|
| `HBEFA4/PC_petrol_Euro-6ab` | 26,99 |
| `HBEFA4/PC_diesel_Euro-6ab` | 32,15 |
| `HBEFA4/PC_diesel_Euro-4` | 15,23 |
| `HBEFA4/PC_petrol_Euro-4` | 5,92 |
| `HBEFA4/PC_petrol_Euro-3` | 6,43 |
| `HBEFA4/PC_diesel_Euro-3` | 6,66 |
| `HBEFA4/PC_BEV` | 1,33 |
| `HBEFA4/PC_petrol_Euro-1` | 1,89 |
| `HBEFA4/PC_PHEV_petrol_Euro-6ab_(P)` | 0,62 |
| `HBEFA4/PC_LPG_petrol_Euro-6_(LPG)` | 0,61 |
| `HBEFA4/PC_diesel_Euro-2` | 1,41 |
| `HBEFA4/PC_diesel_Euro-1` | 0,76 |

## Sorties

| Sortie | Description |
|---|---|
| `population_all_with_vtypes.rou.xml` | Population SUMO avec définitions HBEFA4 `<vType>` et références `vTypes` |
| `output_tools/person_to_emissionClass.csv` | Identifiant de personne, classe d’émissions et identifiant du type SUMO |

L’exécution de référence a trouvé 10 569 automobilistes et inséré 12 types de
véhicules. Grâce aux quotas entiers, l’effectif attribué à chaque classe peut
être reproduit à partir de la taille de population, de `DIST` et de la graine.

## Contrôles qualité

Avant la simulation :

- vérifier que `DIST` totalise 100 % ;
- comparer la distribution configurée à celle du parc local calculé ;
- confirmer que chaque automobiliste apparaît une fois dans
  `person_to_emissionClass.csv` ;
- confirmer que chaque `personTrip` en voiture possède une référence `vTypes`
  valide ;
- vérifier que tous les identifiants `vType` référencés sont définis au début
  du XML ;
- valider les identifiants HBEFA4 avec la version de SUMO installée.

Consulter la
[documentation SUMO sur les émissions](https://sumo.dlr.de/docs/Models/Emissions.html)
pour la couverture des modèles et les unités de sortie.

## Politique Git

Seuls le notebook, la documentation bilingue et les règles d’exclusion Git
sont conservés. Les données sources et fichiers générés sont documentés mais
ne sont pas déposés.
