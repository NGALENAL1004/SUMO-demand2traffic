<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# MATSim simulation outputs

This folder is created by MATSim when `run_matsim: true` is enabled in the
pipeline configuration. It contains the simulated plans, network events,
tables exported by Eqasim, and convergence indicators.

All these files are generated automatically and are not tracked on GitHub.

## Main outputs

| File | Contents |
|---|---|
| `output_events.xml.zst` | Detailed timeline of MATSim events; generally the largest file |
| `output_plans.xml.zst` | Final population plans after the last iteration |
| `output_experienced_plans.xml.zst` | Plans actually experienced during the simulation |
| `output_persons.csv.zst` | Characteristics of simulated persons |
| `output_activities.csv.zst` | Activities from the exported plans |
| `output_trips.csv.zst` | Exported trips |
| `output_legs.csv.zst` | Exported modal legs |
| `output_links.csv.zst` | Information associated with network links |
| `eqasim_activities.csv.zst` | Activities converted to tabular format by Eqasim |
| `eqasim_trips.csv.zst` | Trips converted to tabular format by Eqasim |
| `eqasim_legs.csv.zst` | Legs converted to tabular format by Eqasim |
| `eqasim_pt.csv.zst` | Public transport trip details |

The `.zst` extension denotes **Zstandard** compression. It is not
interchangeable with `.gz`. In Python, these files can be read with the
`zstandard` package; compressed CSV files can also be read with `pandas` using
`compression="zstd"`.

## Copy of the executed scenario

The following files describe the exact scenario that was executed:

- `output_config.xml` and `output_config_reduced.xml`: MATSim configuration;
- `output_network.xml.zst`: network;
- `output_facilities.xml.zst`: activity facilities;
- `output_households.xml.zst`: households;
- `output_vehicles.xml.zst` and `output_allVehicles.xml.zst`: vehicles;
- `output_transitSchedule.xml.zst` and `output_transitVehicles.xml.zst`:
  public transport supply;
- `output_counts.xml.zst`: traffic count data, when associated with the
  scenario.

Keeping this copy locally makes it easier to analyse a run because subsequent
changes to `config_17.yml` do not retroactively alter these files.

## Diagnostics and convergence

| File group | Purpose |
|---|---|
| `eqasim_termination.csv` and `.html` | Simulation stopping criterion and iteration |
| `modestats*`, `ph_modestats*`, `pkm_modestats*` | Evolution of modal shares |
| `scorestats*` | Evolution of MATSim scores |
| `traveldistancestats*` | Distribution of travelled distances |
| `travel_time_comparison.csv` and `car_travel_time_comparison.csv` | Travel-time comparison |
| `stuck_analysis.csv` | Stuck agents or vehicles |
| `stopwatch*` | Computation time |
| `modeChoiceCoverage*` | Mode-choice model coverage |
| `dmc_utilities.csv` | Utilities calculated by the discrete mode-choice model |
| `output_experienced_plans_scores.txt.zst` | Scores of experienced plans |
| `modules.dot` | Technical graph of the loaded MATSim modules |
| `logfile.log` and `logfileWarningsErrors.log` | Complete run log and warnings |

## Technical folders

`ITERS/` contains the intermediate results of each MATSim iteration. `tmp/`
contains temporary working files. They are useful for in-depth diagnostics,
but they are normally not required for the filtering intended for SUMO.

The filtering process documented in
`../eqasim_output_filtered/README.md` mainly uses the plans, persons,
activities, trips, public transport data, households, and activity facilities
from this folder.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Résultats de la simulation MATSim

Ce dossier est créé par MATSim lorsque `run_matsim: true` est activé dans la
configuration du pipeline. Il contient les plans simulés, les événements du
réseau, les tables exportées par Eqasim et les indicateurs de convergence.

L'ensemble de ces fichiers est généré automatiquement et n'est pas versionné
sur GitHub.

## Résultats principaux

| Fichier | Contenu |
|---|---|
| `output_events.xml.zst` | Chronologie détaillée des événements MATSim ; fichier généralement le plus volumineux |
| `output_plans.xml.zst` | Plans finaux de la population après la dernière itération |
| `output_experienced_plans.xml.zst` | Plans réellement expérimentés pendant la simulation |
| `output_persons.csv.zst` | Caractéristiques des personnes simulées |
| `output_activities.csv.zst` | Activités des plans exportés |
| `output_trips.csv.zst` | Déplacements exportés |
| `output_legs.csv.zst` | Étapes modales exportées |
| `output_links.csv.zst` | Informations associées aux liens du réseau |
| `eqasim_activities.csv.zst` | Activités remises au format tabulaire par Eqasim |
| `eqasim_trips.csv.zst` | Déplacements remis au format tabulaire par Eqasim |
| `eqasim_legs.csv.zst` | Étapes remises au format tabulaire par Eqasim |
| `eqasim_pt.csv.zst` | Détails des trajets en transport collectif |

L'extension `.zst` correspond à la compression **Zstandard**. Elle n'est pas
interchangeable avec `.gz`. Dans Python, ces fichiers peuvent notamment être
lus avec le paquet `zstandard`; les CSV compressés peuvent aussi être lus par
`pandas` avec `compression="zstd"`.

## Copie du scénario utilisé

Les fichiers suivants décrivent exactement le scénario exécuté :

- `output_config.xml` et `output_config_reduced.xml` : configuration MATSim ;
- `output_network.xml.zst` : réseau ;
- `output_facilities.xml.zst` : lieux d'activité ;
- `output_households.xml.zst` : ménages ;
- `output_vehicles.xml.zst` et `output_allVehicles.xml.zst` : véhicules ;
- `output_transitSchedule.xml.zst` et `output_transitVehicles.xml.zst` :
  offre de transport collectif ;
- `output_counts.xml.zst` : données de comptage éventuellement associées au
  scénario.

Conserver localement cette copie facilite l'analyse d'une exécution, car une
modification ultérieure de `config_17.yml` ne change pas rétroactivement ces
fichiers.

## Diagnostic et convergence

| Groupe de fichiers | Utilité |
|---|---|
| `eqasim_termination.csv` et `.html` | Critère et itération d'arrêt de la simulation |
| `modestats*`, `ph_modestats*`, `pkm_modestats*` | Évolution des parts modales |
| `scorestats*` | Évolution des scores MATSim |
| `traveldistancestats*` | Distribution des distances parcourues |
| `travel_time_comparison.csv` et `car_travel_time_comparison.csv` | Comparaison des temps de trajet |
| `stuck_analysis.csv` | Agents ou véhicules bloqués |
| `stopwatch*` | Temps de calcul |
| `modeChoiceCoverage*` | Couverture du modèle de choix modal |
| `dmc_utilities.csv` | Utilités calculées par le modèle discret de choix modal |
| `output_experienced_plans_scores.txt.zst` | Scores des plans expérimentés |
| `modules.dot` | Graphe technique des modules MATSim chargés |
| `logfile.log` et `logfileWarningsErrors.log` | Journal complet et avertissements de l'exécution |

## Dossiers techniques

`ITERS/` contient les résultats intermédiaires de chaque itération MATSim.
`tmp/` contient des fichiers de travail temporaires. Ils sont utiles pour un
diagnostic approfondi, mais ne sont normalement pas nécessaires au filtrage
destiné à SUMO.

Le filtrage documenté dans
`../eqasim_output_filtered/README.md` utilise principalement les plans, les
personnes, les activités, les déplacements, les transports collectifs, les
ménages et les lieux d'activité de ce dossier.
