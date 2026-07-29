<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Converting Eqasim daily plans to SUMO person plans

This folder converts the filtered Eqasim population into a multimodal SUMO
route file. The conversion preserves activity sequences and times, maps
facilities to the network, translates public transport legs to the dated Yélo
supply, and checks network connectivity before writing each person.

The complete workflow is implemented in `trips.ipynb`, which contains two
code cells that must be executed in order.

## Files retained in the repository

```text
4-convert_trips/
|-- README.md
|-- trips.ipynb
`-- output_tools/
    `-- README.md
```

The generated route file, cache, mappings, and logs remain local.

## Required inputs

| Input | Expected location | Purpose |
|---|---|---|
| `output_plans_filtered.xml.zst` | `../eqasim_output_filtered/` | Selected Eqasim plans |
| `eqasim_pt_filtered.csv` | `../eqasim_output_filtered/` | Detailed Eqasim PT legs |
| `facilities2sumo_multimode.csv` | `../2-POI's/` | Primary pedestrian and passenger mappings |
| `facilities2sumo_pedestrian_candidates.csv` | `../2-POI's/` | Alternative pedestrian mappings |
| `cda_la_rochelle.net.xml` | `../1-network/` | SUMO road, bicycle, and pedestrian graph |
| `gtfs_pt_stops.add.xml` | `../3-public_transport/` | SUMO public transport stops |
| `gtfs_pt_vehicles.add.xml` | `../3-public_transport/` | SUMO PT routes and scheduled vehicles |
| `ca_la_rochelle-aggregated-gtfs.zip` | `../3-public_transport/input/` | GTFS identifiers, names, stops, and trip metadata |

All preceding workflow stages must be completed first.

## Prerequisites

- Python and Jupyter;
- `pandas`;
- `zstandard` for current Eqasim `.zst` files;
- Eclipse SUMO and `sumolib`;
- `SUMO_HOME` correctly defined;
- sufficient memory to load the 1 GB network.

## Reading the compressed plans

Current Eqasim outputs use real Zstandard compression and must be opened with
`zstandard`, for example:

```python
import zstandard as zstd

with zstd.open(POP_PATH, "rb") as stream:
    ...
```

Copy `output_plans_filtered.xml.zst` from
`1-Eqasim/output/eqasim_output_filtered/` to
`2-SUMO/eqasim_output_filtered/` before running the notebook, keeping the
filename unchanged.

## Cell 1 — Match Eqasim PT legs to SUMO lines

The first cell links each Eqasim public transport leg to a route identifier
available in `gtfs_pt_vehicles.add.xml`.

### Matching logic

1. Attempt a direct match using the Eqasim `transit_route_id` and the SUMO
   vehicle identifier convention.
2. If the direct target is unavailable, identify SUMO candidates sharing the
   commercial route name.
3. Score candidates using GTFS route, direction, headsign, shape, and stop
   sequence information.
4. Export both the operational mapping and detailed diagnostics.

### Outputs

| Output | Description |
|---|---|
| `output_tools/eqasim_pt_sumo_line_mapping.csv` | Compact many-to-one mapping used by cell 2 |
| `output_tools/eqasim_pt_sumo_line_mapping_debug.csv` | Matching method, score, reasons, and metadata |
| `output_tools/eqasim_pt_sumo_line_mapping_unmatched.csv` | PT legs for which no SUMO line could be selected |

### Reference checks

The saved execution reports:

- 7,706 Eqasim PT-leg rows;
- 838 unique `(transit_line_id, transit_route_id)` pairs;
- 7,637 matched rows;
- 69 unmatched rows:
  - 37 target GTFS trips absent from the selected feed;
  - 32 cases without a candidate SUMO line for the route name.

Unmatched rows are not silently discarded: cell 2 explicitly identifies them
and attempts a car-passenger fallback.

## Cell 2 — Write the complete SUMO population

The second cell:

- streams the selected Eqasim plans;
- keeps the selected daily plan for each person;
- removes interaction activities from the final activity sequence;
- merges consecutive activities at the same facility;
- maps activity positions to pedestrian or passenger-compatible edges;
- converts walk, bicycle, car, car-passenger, and PT legs;
- resolves boarding, alighting, and transfer stops for mapped PT chains;
- converts explicitly unmatched PT trips to a car-passenger fallback;
- tests the required network connections before writing the person;
- tries alternative pedestrian candidates when the primary mapping is not
  connected;
- logs every person that cannot be converted.

The last activity is forced to an end time of `86400` seconds by the current
configuration. The shortest-path cache is persistent and deterministic for a
given network and set of parameters.

### Outputs

| Output | Description |
|---|---|
| `population_all.rou.xml` | Converted SUMO persons, activities, walks, rides, and person trips |
| `output_tools/population_all.log.csv` | One status and diagnostic reason per Eqasim person |
| `shortest_path_cache_s0_new_network_v3.pkl` | Reusable shortest-path query cache |

## Reference conversion results

The saved run processed 16,046 filtered Eqasim persons:

| Status | Persons |
|---|---:|
| Written to `population_all.rou.xml` | 15,371 |
| Skipped: no valid network route or access | 564 |
| Skipped: PT mapping/stop/transfer problem | 93 |
| Skipped: other conversion error | 17 |
| Skipped: invalid/NaN mapping | 1 |
| **Total skipped** | **675** |

The cache contained 40,764 shortest-path entries at the end of the run.

These skipped persons reduce the simulated population and must be reported in
scientific analyses. Inspect the detailed log rather than treating every skip
as the same error.

## Running in VS Code

1. Open `trips.ipynb`.
2. Select the Python environment containing SUMO's Python tools and the
   required packages.
3. Confirm that the notebook working directory is `4-convert_trips`.
4. Run cell 1 and inspect the three PT mapping CSV files.
5. Confirm that the staged plans file is genuine Zstandard and that the
   reader uses `zstd.open`.
6. Run cell 2.
7. Inspect `population_all.log.csv` and validate
   `population_all.rou.xml` before continuing.

An optional SUMO syntax check is:

```bat
sumo -n ..\1-network\cda_la_rochelle.net.xml -r population_all.rou.xml --begin 0 --end 1
```

This short check does not validate the complete daily scenario, but it helps
detect malformed XML and immediately invalid references.

## Git policy

Only the notebook, READMEs, and Git exclusion rules are retained. The route
file, PT mappings, logs, and binary cache are reproducible outputs and are not
committed.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Conversion des plans journaliers Eqasim en plans SUMO

Ce dossier convertit la population Eqasim filtrée en un fichier d’itinéraires
SUMO multimodal. La conversion conserve les activités et leurs horaires,
rattache les équipements au réseau, traduit les étapes en transport collectif
vers l’offre Yélo datée et contrôle la connectivité avant d’écrire chaque
personne.

La chaîne complète se trouve dans `trips.ipynb`, qui contient deux cellules de
code à exécuter dans l’ordre.

## Fichiers conservés dans le dépôt

```text
4-convert_trips/
|-- README.md
|-- trips.ipynb
`-- output_tools/
    `-- README.md
```

Le fichier d’itinéraires, le cache, les tables d’appariement et les journaux
générés restent locaux.

## Entrées nécessaires

| Entrée | Emplacement attendu | Rôle |
|---|---|---|
| `output_plans_filtered.xml.zst` | `../eqasim_output_filtered/` | Plans Eqasim sélectionnés |
| `eqasim_pt_filtered.csv` | `../eqasim_output_filtered/` | Étapes TC Eqasim détaillées |
| `facilities2sumo_multimode.csv` | `../2-POI's/` | Appariements principaux piéton et voiture |
| `facilities2sumo_pedestrian_candidates.csv` | `../2-POI's/` | Appariements piétons alternatifs |
| `cda_la_rochelle.net.xml` | `../1-network/` | Graphe SUMO routier, cyclable et piéton |
| `gtfs_pt_stops.add.xml` | `../3-public_transport/` | Arrêts de transport collectif SUMO |
| `gtfs_pt_vehicles.add.xml` | `../3-public_transport/` | Itinéraires et véhicules TC programmés |
| `ca_la_rochelle-aggregated-gtfs.zip` | `../3-public_transport/input/` | Identifiants, noms, arrêts et courses GTFS |

Toutes les étapes précédentes doivent être terminées.

## Prérequis

- Python et Jupyter ;
- `pandas` ;
- `zstandard` pour les fichiers Eqasim `.zst` actuels ;
- Eclipse SUMO et `sumolib` ;
- `SUMO_HOME` correctement défini ;
- suffisamment de mémoire pour charger le réseau d’environ 1 Go.

## Lecture des plans compressés

Les sorties Eqasim actuelles utilisent réellement la compression Zstandard et
doivent être ouvertes avec `zstandard`, par exemple :

```python
import zstandard as zstd

with zstd.open(POP_PATH, "rb") as stream:
    ...
```

Copier `output_plans_filtered.xml.zst` depuis
`1-Eqasim/output/eqasim_output_filtered/` vers
`2-SUMO/eqasim_output_filtered/` avant d’exécuter le notebook, sans modifier
son nom.

## Cellule 1 — Apparier les étapes TC Eqasim aux lignes SUMO

La première cellule rattache chaque étape de transport collectif Eqasim à un
identifiant d’itinéraire présent dans `gtfs_pt_vehicles.add.xml`.

### Logique d’appariement

1. Tenter une correspondance directe à partir du `transit_route_id` Eqasim et
   de la convention d’identifiant des véhicules SUMO.
2. Si la course directe n’est pas disponible, chercher les candidats SUMO qui
   partagent le nom commercial de la ligne.
3. Noter les candidats à partir de la ligne, de la direction, de la
   destination, du tracé et de la séquence d’arrêts GTFS.
4. Exporter à la fois la table opérationnelle et les diagnostics détaillés.

### Sorties

| Sortie | Description |
|---|---|
| `output_tools/eqasim_pt_sumo_line_mapping.csv` | Appariement compact utilisé par la cellule 2 |
| `output_tools/eqasim_pt_sumo_line_mapping_debug.csv` | Méthode, score, raisons et métadonnées de l’appariement |
| `output_tools/eqasim_pt_sumo_line_mapping_unmatched.csv` | Étapes TC sans ligne SUMO sélectionnée |

### Contrôles de référence

L’exécution enregistrée indique :

- 7 706 lignes d’étapes TC Eqasim ;
- 838 couples uniques `(transit_line_id, transit_route_id)` ;
- 7 637 lignes appariées ;
- 69 lignes non appariées :
  - 37 courses cibles absentes du GTFS sélectionné ;
  - 32 cas sans ligne SUMO candidate pour le nom de ligne.

Les lignes non appariées ne sont pas supprimées silencieusement : la cellule 2
les identifie explicitement et tente un remplacement en voiture passager.

## Cellule 2 — Écrire toute la population SUMO

La deuxième cellule :

- lit les plans Eqasim sélectionnés en flux ;
- conserve le plan journalier sélectionné de chaque personne ;
- retire les activités d’interaction de la séquence finale ;
- fusionne les activités consécutives situées dans le même équipement ;
- rattache les activités à des arêtes accessibles aux piétons ou voitures ;
- convertit les étapes à pied, vélo, voiture, passager et TC ;
- détermine les arrêts de montée, descente et correspondance des chaînes TC ;
- convertit les trajets TC explicitement non appariés en voiture passager ;
- contrôle les connexions nécessaires avant d’écrire la personne ;
- essaie des candidats piétons alternatifs lorsque l’appariement principal
  n’est pas connecté ;
- journalise toute personne qui ne peut pas être convertie.

L’activité finale est forcée à `86400` secondes dans la configuration actuelle.
Le cache de plus courts chemins est persistant et déterministe pour un réseau
et des paramètres donnés.

### Sorties

| Sortie | Description |
|---|---|
| `population_all.rou.xml` | Personnes, activités, marches, trajets et déplacements SUMO convertis |
| `output_tools/population_all.log.csv` | Statut et motif de diagnostic pour chaque personne Eqasim |
| `shortest_path_cache_s0_new_network_v3.pkl` | Cache réutilisable des requêtes de plus court chemin |

## Résultats de la conversion de référence

L’exécution enregistrée a traité 16 046 personnes Eqasim filtrées :

| Statut | Personnes |
|---|---:|
| Écrites dans `population_all.rou.xml` | 15 371 |
| Exclues : absence d’itinéraire ou d’accès valide | 564 |
| Exclues : problème TC d’appariement, d’arrêt ou de correspondance | 93 |
| Exclues : autre erreur de conversion | 17 |
| Exclues : appariement invalide/NaN | 1 |
| **Total exclu** | **675** |

Le cache contenait 40 764 entrées de plus court chemin à la fin de
l’exécution.

Ces personnes exclues réduisent la population simulée et doivent être
mentionnées dans les analyses scientifiques. Il faut consulter le journal
détaillé plutôt que d’interpréter toutes les exclusions comme une seule
erreur.

## Exécution dans VS Code

1. Ouvrir `trips.ipynb`.
2. Choisir l’environnement Python contenant les outils SUMO et les
   bibliothèques requises.
3. Vérifier que le dossier de travail est `4-convert_trips`.
4. Exécuter la cellule 1 et inspecter les trois CSV d’appariement TC.
5. Vérifier que le fichier de plans copié est un véritable Zstandard et que
   le lecteur utilise `zstd.open`.
6. Exécuter la cellule 2.
7. Inspecter `population_all.log.csv` et valider
   `population_all.rou.xml` avant de poursuivre.

Un contrôle syntaxique SUMO facultatif est :

```bat
sumo -n ..\1-network\cda_la_rochelle.net.xml -r population_all.rou.xml --begin 0 --end 1
```

Ce contrôle court ne valide pas toute la journée simulée, mais aide à détecter
un XML mal formé ou des références immédiatement invalides.

## Politique Git

Seuls le notebook, les README et les règles d’exclusion Git sont conservés.
Le fichier d’itinéraires, les tables TC, les journaux et le cache binaire sont
des sorties reproductibles qui ne sont pas déposées.
