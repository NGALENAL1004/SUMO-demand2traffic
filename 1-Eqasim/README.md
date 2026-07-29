<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Synthetic travel demand generation with Eqasim and MATSim

This folder is the first part of the `SUMO-demand2traffic` project. It builds a
synthetic population, simulates its travel behaviour with MATSim, and then
extracts the persons and mobility plans required for a SUMO simulation.

The method is based on the open-source
[`eqasim-france`](https://github.com/eqasim-org/eqasim-france) pipeline. It can
be transferred to other French territories, but the configuration, local
data, and filtering process provided here correspond to its application to
**Charente-Maritime and the La Rochelle case study**.

The population is first generated for the whole department 17. The study area
is filtered only after the MATSim simulation in order to preserve trips that
cross the boundaries of the La Rochelle urban community.

> This repository is not an official Eqasim distribution. It documents a
> reproducible adaptation of `eqasim-france` for the needs of this project.

## Official resources

| Resource | Link |
|---|---|
| Eqasim project website | <https://eqasim.org/> |
| Python pipeline for France | <https://github.com/eqasim-org/eqasim-france> |
| Java components and MATSim extensions | <https://github.com/eqasim-org/eqasim-java> |
| `eqasim-france` documentation | <https://eqasim-org.github.io/eqasim-france/> |
| Synthetic population tutorial | <https://eqasim-org.github.io/eqasim-france/population/population_summary.html> |
| MATSim simulation tutorial | <https://eqasim-org.github.io/eqasim-france/simulation/simulation_summary.html> |
| MATSim website | <https://matsim.org/> |

## Overview

| Processing chain |
|:---:|
| **1. Public and local data** |
| ↓ |
| **2. Synthetic population of Charente-Maritime** |
| ↓ |
| **3. Eqasim–MATSim simulation** |
| ↓ |
| **4. Filtering for the La Rochelle case study** |
| ↓ |
| **5. Demand preparation for SUMO** |

The workflow consists of five main stages:

1. download the demographic, geographic, and mobility data;
2. synthesise persons and households for department 17;
3. assign activity schedules, locations, and transport modes;
4. generate and run the MATSim scenario;
5. filter the results required for the next part of the project in SUMO.

## Organisation

```text
1-Eqasim/
├── README.md
├── data/
│   └── README.md
├── code/
│   ├── README.md
│   ├── config_17.yml
│   ├── matsim/simulation/full_run.py
│   └── synthesis/population/matched.py
├── cache/
└── output/
    ├── README.md
    ├── analysis_population/
    │   └── README.md
    ├── simulation_output/
    │   └── README.md
    └── eqasim_output_filtered/
        ├── README.md
        └── create_output_filtered.ipynb
```

| Folder | Purpose | Included on GitHub |
|---|---|---|
| [`data/`](data/) | Required raw data and download guide | README only |
| [`code/`](code/) | Configuration and adaptations made to `eqasim-france` | Yes, only project-specific files |
| `cache/` | SynPP intermediate results | No |
| [`output/`](output/) | Population, scenario, and MATSim results | README files only |
| [`output/eqasim_output_filtered/`](output/eqasim_output_filtered/) | Filtering for the next part of the project | README and notebook only |

The input data, complete `eqasim-france` clone, caches, and results are not
distributed on GitHub. They must be downloaded or generated locally.

## Reference scenario configuration

The [`code/config_17.yml`](code/config_17.yml) file contains the main
configuration.

| Parameter | Value | Meaning |
|---|---|---|
| `departments` | `[17]` | Population of Charente-Maritime |
| `sampling_rate` | `0.11` | 11% population sample |
| `random_seed` | `1234` | Seed used for reproducibility |
| `hts` | `emp` | 2019 French national mobility survey |
| `filter_hts` | `false` | Retention of the complete EMP data prepared by the pipeline |
| `income_assignation_method` | `bhepop2` | Household income assignment |
| `education_location_source` | `weighted` | Weighted assignment of education locations |
| `home_location_source` | `addresses` | Home locations derived from BAN addresses |
| `mode_choice` | `true` | Eqasim mode-choice model enabled |
| `run_matsim` | `true` | MATSim execution enabled |
| `write_jar` | `true` | Generation of the scenario Java executable |
| `processes` | `4` | Number of parallel processes |
| `java_memory` | `14G` | Maximum memory allocated to Java |

The `run` block currently requests:

- generation of the synthetic population outputs;
- execution of the complete MATSim simulation;
- generation of the synthetic population quality indicators.

## Versions used

The reference run was produced with the following versions:

| Component | Version or reference |
|---|---|
| `eqasim-france` | commit `6115005e9bfb02cbcdc909c9106b013d3198b577` |
| Pipeline version recorded in `17meta.json` | `1.4.0` |
| `eqasim-java` | version `2.2.0`, commit `fc85693` |
| Python | 3.13 or the compatible version specified by the upstream project |
| Java | 25 |

For an exact reproduction, use the complete commit hash rather than the
`main` branch. The `output/17meta.json` file generated by the pipeline also
records the version, random seed, and sampling rate of each generation.

## Prerequisites on Windows

The workflow was run on Windows using Command Prompt and VS Code. It requires:

- [Git](https://git-scm.com/download/win);
- [VS Code](https://code.visualstudio.com/);
- [`uv`](https://docs.astral.sh/uv/) for the Python environment;
- Python 3.13 or the version required by the selected `eqasim-france` commit;
- Java 25;
- Maven;
- the data described in [`data/README.md`](data/README.md).

The configuration allows Java to use up to 14 GB of memory. The computer must
have additional physical memory available for Windows and other processes.
Several gigabytes of storage are also required for the data, caches, and
MATSim results.

The executables must be available from Command Prompt:

```bat
git --version
uv --version
java --version
mvn --version
```

## Installation

### 1. Download the data

Create the local `data/` structure and download each dataset from its official
source:

```text
1-Eqasim/data/
```

Archive names, data vintages, their purpose, and download links are detailed
in [`data/README.md`](data/README.md).

### 2. Retrieve the Eqasim version

From the `1-Eqasim` folder:

```bat
git clone https://github.com/eqasim-org/eqasim-france.git eqasim-france
cd eqasim-france
git checkout 6115005e9bfb02cbcdc909c9106b013d3198b577
cd ..
```

If Windows reports an error related to path length, the following command may
be required before cloning:

```bat
git config --global core.longpaths true
```

### 3. Copy the project adaptations

Still from `1-Eqasim`:

```bat
copy /Y "code\config_17.yml" "eqasim-france\config_17.yml"
copy /Y "code\matsim\simulation\full_run.py" "eqasim-france\matsim\simulation\full_run.py"
copy /Y "code\synthesis\population\matched.py" "eqasim-france\synthesis\population\matched.py"
```

These files make two changes to the upstream code:

- more detailed age groups for matching with the EMP survey;
- support for the Zstandard
  `simulation_output/output_events.xml.zst` file produced by the recent MATSim
  version.

The changes and clone verification procedure are described in
[`code/README.md`](code/README.md).

### 4. Install the environment

```bat
cd eqasim-france
uv sync
```

`uv` creates the Python environment and installs the dependencies declared by
the selected `eqasim-france` version.

## Running the pipeline

From `1-Eqasim\eqasim-france`:

```bat
uv run -m synpp config_17.yml
```

SynPP resolves the dependencies between stages and writes:

- intermediate computations to `../cache`;
- the synthetic population to `../output`;
- MATSim results to `../output/simulation_output`.

A complete run may take a long time. Its duration depends on the sampling
rate, computer, transport network, and number of MATSim iterations.

### Generate only the population

To stop the workflow before the complete simulation, temporarily remove or
comment out this line from the `run` block:

```yaml
- matsim.simulation.full_run
```

Keep `synthesis.output` to produce the population and
`analysis.synthesis.population` to generate the associated quality checks.

### Also run MATSim

For the complete execution used in this project, the block contains:

```yaml
run:
  - synthesis.output
  - matsim.simulation.full_run
  - analysis.synthesis.population
```

and the following parameters remain enabled:

```yaml
run_matsim: true
write_jar: true
```

## Generated outputs

The root of `output/` contains, among other files:

- synthetic persons and households;
- activities, trips, and modal legs;
- geographic GeoPackage layers;
- the MATSim network, plans, facilities, and vehicles;
- the run configuration and metadata.

`output/simulation_output/` contains the final plans, MATSim events,
Zstandard-compressed Eqasim tables, and convergence indicators.

Each file is described in [`output/README.md`](output/README.md) and
[`output/simulation_output/README.md`](output/simulation_output/README.md).

## Filtering for the La Rochelle case study

The
[`output/eqasim_output_filtered/create_output_filtered.ipynb`](output/eqasim_output_filtered/create_output_filtered.ipynb)
notebook reduces the departmental outputs before they are used in the next
part of the project.

A person is retained if:

- their household is located in one of the eight selected peri-urban
  municipalities; or
- all their activities are located in the 28 municipalities of the La
  Rochelle urban community.

The union of these two sets retains both a targeted resident population and
persons whose entire activity schedule concerns the urban community.

For the 11% reference run, the filter retains:

| Element | Count |
|---|---:|
| Persons | 16,046 |
| Households | 9,591 |
| MATSim activities | 68,346 |
| MATSim trips | 52,431 |
| Public transport legs | 7,706 |

The notebook and all its outputs are described in
[`output/eqasim_output_filtered/README.md`](output/eqasim_output_filtered/README.md).

## Quality control

The files in `output/analysis_population/` compare the synthetic population
with the reference data for several dimensions: age, driving licence
ownership, vehicle ownership, distances, and travel behaviour. They support
the validation of the synthesis but do not replace a local MATSim calibration.

Two minor limitations were identified during filtering:

- 14 households have no municipality in `17households.csv` because their
  activity schedule from the EMP survey contains no `home` activity. Their
  location nevertheless exists in Eqasim's internal stages;
- one SIRENE workplace is located approximately 10 metres outside its IRIS
  polygon, which prevents the strict spatial join.

The selection was recalculated using the known locations: these two cases do
not change the 16,046 persons retained in the reference run.

## Reproducibility

To compare two scenarios:

1. retain the same data archives;
2. retain `config_17.yml`;
3. retain the random seed;
4. use the same `eqasim-france` commit and `eqasim-java` version;
5. archive the generated `17meta.json` file;
6. execute the filtering notebook in a restarted Jupyter kernel.

BAN, SIRENE, OpenStreetMap, and GTFS sources are updated regularly. A newer
archive may change locations, the network, or the public transport supply,
even when the code and random seed remain unchanged.

## Contents retained on GitHub

The repository retains:

- the README files;
- `code/config_17.yml`;
- the two modified Eqasim files;
- the filtering notebook.

It excludes:

- raw data from `data/`;
- the complete `eqasim-france` clone;
- Python environments;
- `cache/`;
- populations, networks, and results from `output/`.

This separation documents and reproduces the workflow without redistributing
several gigabytes of data or sources governed by their own terms of use.

## Reference publications

The following three publications describe the Eqasim framework and the
synthetic population used as the methodological model for this project:

1. Hörl, S. and Balac, M. (2021).
   [*Introducing the eqasim pipeline: From raw data to agent-based transport simulation*](https://doi.org/10.1016/j.procs.2021.03.089).
   *Procedia Computer Science*, **184**, 712–719.
   This article presents the reproducible workflow from raw data to
   multi-agent transport simulation.

2. Hörl, S. and Balac, M. (2021).
   [*Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data*](https://doi.org/10.1016/j.trc.2021.103291).
   *Transportation Research Part C: Emerging Technologies*, **130**, 103291.
   This article details the method for generating synthetic population and
   travel demand from French open data.

3. Hörl, S. and Balac, M. (2021).
   [*Open synthetic travel demand for Paris and Île-de-France: Inputs and output data*](https://doi.org/10.1016/j.dib.2021.107622).
   *Data in Brief*, **39**, 107622.
   This article describes the pipeline's input data, processing steps, and
   output structure.

For a scientific publication using this adaptation, cite the relevant
references above and explicitly describe the data, configuration, and changes
specific to the La Rochelle case study.

## Licence and attribution

`eqasim-france` and `eqasim-java` are distributed under the GNU General Public
License version 2. The `matched.py` and `full_run.py` files in this project are
adaptations of files from `eqasim-france`. Their redistribution must retain
attribution to the Eqasim project, identify the changes made, and comply with
the requirements of GPL v2.

Input data remain subject to the licences and dissemination conditions of
their respective producers. They are not covered by the code licence and are
not redistributed in this repository.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Génération de la demande synthétique avec Eqasim et MATSim

Ce dossier constitue la première partie du projet `SUMO-demand2traffic`. Il
permet de construire une population synthétique, de simuler ses déplacements
avec MATSim, puis d'extraire les personnes et les plans de mobilité utiles à
une simulation SUMO.

La méthode repose sur le pipeline open source
[`eqasim-france`](https://github.com/eqasim-org/eqasim-france). Elle est
transférable à d'autres territoires français, mais la configuration, les
données locales et le filtrage fournis ici correspondent à son application à
la **Charente-Maritime et au cas d'étude de La Rochelle**.

La population est d'abord générée à l'échelle du département 17. Le périmètre
d'étude est seulement filtré après la simulation MATSim afin de conserver les
déplacements qui franchissent les limites de l'agglomération rochelaise.

> Ce dépôt n'est pas une distribution officielle d'Eqasim. Il documente une
> adaptation reproductible d'`eqasim-france` pour les besoins de ce projet.

## Ressources officielles

| Ressource | Lien |
|---|---|
| Site du projet Eqasim | <https://eqasim.org/> |
| Pipeline Python pour la France | <https://github.com/eqasim-org/eqasim-france> |
| Composants Java et extensions MATSim | <https://github.com/eqasim-org/eqasim-java> |
| Documentation d'`eqasim-france` | <https://eqasim-org.github.io/eqasim-france/> |
| Tutoriel de génération d'une population | <https://eqasim-org.github.io/eqasim-france/population/population_summary.html> |
| Tutoriel de simulation MATSim | <https://eqasim-org.github.io/eqasim-france/simulation/simulation_summary.html> |
| Site de MATSim | <https://matsim.org/> |

## Vue d'ensemble

| Chaîne de traitement |
|:---:|
| **1. Données publiques et données locales** |
| ↓ |
| **2. Population synthétique de Charente-Maritime** |
| ↓ |
| **3. Simulation Eqasim–MATSim** |
| ↓ |
| **4. Filtrage du cas d'étude de La Rochelle** |
| ↓ |
| **5. Préparation de la demande pour SUMO** |

Le workflow comprend cinq grandes étapes :

1. télécharger les données démographiques, géographiques et de mobilité ;
2. synthétiser les personnes et les ménages du département 17 ;
3. attribuer les programmes d'activités, les lieux et les modes de transport ;
4. générer puis exécuter le scénario MATSim ;
5. filtrer les résultats nécessaires à la suite du projet dans SUMO.

## Organisation

```text
1-Eqasim/
├── README.md
├── data/
│   └── README.md
├── code/
│   ├── README.md
│   ├── config_17.yml
│   ├── matsim/simulation/full_run.py
│   └── synthesis/population/matched.py
├── cache/
└── output/
    ├── README.md
    ├── analysis_population/
    │   └── README.md
    ├── simulation_output/
    │   └── README.md
    └── eqasim_output_filtered/
        ├── README.md
        └── create_output_filtered.ipynb
```

| Dossier | Fonction | Présence sur GitHub |
|---|---|---|
| [`data/`](data/) | Données brutes nécessaires et guide de téléchargement | README uniquement |
| [`code/`](code/) | Configuration et adaptations apportées à `eqasim-france` | Oui, seulement les fichiers propres au projet |
| `cache/` | Résultats intermédiaires de SynPP | Non |
| [`output/`](output/) | Population, scénario et résultats MATSim | README uniquement |
| [`output/eqasim_output_filtered/`](output/eqasim_output_filtered/) | Filtrage destiné à la suite du projet | README et notebook uniquement |

Les données d'entrée, le clone complet d'`eqasim-france`, les caches et les
résultats ne sont pas distribués sur GitHub. Ils doivent être téléchargés ou
générés localement.

## Configuration du scénario de référence

Le fichier [`code/config_17.yml`](code/config_17.yml) contient la configuration
principale.

| Paramètre | Valeur | Signification |
|---|---|---|
| `departments` | `[17]` | Population de la Charente-Maritime |
| `sampling_rate` | `0.11` | Échantillon de 11 % de la population |
| `random_seed` | `1234` | Graine utilisée pour la reproductibilité |
| `hts` | `emp` | Enquête mobilité des personnes 2019 |
| `filter_hts` | `false` | Conservation de l'ensemble de l'EMP préparée par le pipeline |
| `income_assignation_method` | `bhepop2` | Affectation des revenus des ménages |
| `education_location_source` | `weighted` | Affectation pondérée des lieux d'enseignement |
| `home_location_source` | `addresses` | Localisation des domiciles à partir de la BAN |
| `mode_choice` | `true` | Activation du modèle de choix modal Eqasim |
| `run_matsim` | `true` | Exécution de MATSim |
| `write_jar` | `true` | Création de l'exécutable Java du scénario |
| `processes` | `4` | Nombre de processus parallèles |
| `java_memory` | `14G` | Mémoire maximale réservée à Java |

Le bloc `run` demande actuellement :

- la génération des sorties de la population synthétique ;
- l'exécution complète de MATSim ;
- la production des indicateurs de contrôle de la population.

## Versions utilisées

L'exécution de référence a été produite avec les versions suivantes :

| Composant | Version ou référence |
|---|---|
| `eqasim-france` | commit `6115005e9bfb02cbcdc909c9106b013d3198b577` |
| Version du pipeline enregistrée dans `17meta.json` | `1.4.0` |
| `eqasim-java` | version `2.2.0`, commit `fc85693` |
| Python | 3.13 ou version compatible indiquée par le projet amont |
| Java | 25 |

Pour une reproduction exacte, utiliser le commit complet plutôt que la branche
`main`. Le fichier `output/17meta.json`, créé par le pipeline, enregistre
également la version, la graine aléatoire et le taux d'échantillonnage de
chaque génération.

## Prérequis sous Windows

Le workflow a été exécuté sous Windows avec l'invite de commandes et VS Code.
Il nécessite :

- [Git](https://git-scm.com/download/win) ;
- [VS Code](https://code.visualstudio.com/) ;
- [`uv`](https://docs.astral.sh/uv/) pour l'environnement Python ;
- Python 3.13 ou la version demandée par le commit d'`eqasim-france` ;
- Java 25 ;
- Maven ;
- les données décrites dans [`data/README.md`](data/README.md).

La configuration autorise Java à utiliser jusqu'à 14 Go de mémoire. La machine
doit disposer de davantage de mémoire physique pour laisser de la place à
Windows et aux autres processus. Il faut également prévoir plusieurs
gigaoctets pour les données, les caches et les résultats MATSim.

Les exécutables doivent être accessibles depuis l'invite de commandes :

```bat
git --version
uv --version
java --version
mvn --version
```

## Installation

### 1. Télécharger les données

Créer l'arborescence locale de `data/` et télécharger chaque jeu de données
depuis sa source officielle :

```text
1-Eqasim/data/
```

Les noms des archives, leurs millésimes, leur rôle et leurs liens de
téléchargement sont détaillés dans [`data/README.md`](data/README.md).

### 2. Récupérer la version d'Eqasim

Depuis le dossier `1-Eqasim` :

```bat
git clone https://github.com/eqasim-org/eqasim-france.git eqasim-france
cd eqasim-france
git checkout 6115005e9bfb02cbcdc909c9106b013d3198b577
cd ..
```

En cas d'erreur liée à la longueur des chemins Windows, la commande suivante
peut être nécessaire avant le clonage :

```bat
git config --global core.longpaths true
```

### 3. Copier les adaptations du projet

Toujours depuis `1-Eqasim` :

```bat
copy /Y "code\config_17.yml" "eqasim-france\config_17.yml"
copy /Y "code\matsim\simulation\full_run.py" "eqasim-france\matsim\simulation\full_run.py"
copy /Y "code\synthesis\population\matched.py" "eqasim-france\synthesis\population\matched.py"
```

Ces fichiers apportent deux modifications au code amont :

- des classes d'âge plus détaillées pour le matching avec l'EMP ;
- la prise en compte du format Zstandard
  `simulation_output/output_events.xml.zst` produit par la version récente de
  MATSim.

Le détail des modifications et la vérification du clone sont présentés dans
[`code/README.md`](code/README.md).

### 4. Installer l'environnement

```bat
cd eqasim-france
uv sync
```

`uv` crée l'environnement Python et installe les dépendances déclarées par la
version sélectionnée d'`eqasim-france`.

## Exécution du pipeline

Depuis `1-Eqasim\eqasim-france` :

```bat
uv run -m synpp config_17.yml
```

SynPP résout les dépendances entre les étapes et écrit :

- les calculs intermédiaires dans `../cache` ;
- la population synthétique dans `../output` ;
- les résultats de MATSim dans `../output/simulation_output`.

L'exécution complète peut être longue. Sa durée dépend du taux
d'échantillonnage, de la machine, du réseau de transport et du nombre
d'itérations MATSim.

### Générer uniquement la population

Pour arrêter le workflow avant la simulation complète, retirer ou commenter
temporairement cette ligne du bloc `run` :

```yaml
- matsim.simulation.full_run
```

Conserver `synthesis.output` pour produire la population et
`analysis.synthesis.population` pour générer les contrôles associés.

### Lancer également MATSim

Pour l'exécution complète utilisée dans ce projet, le bloc contient :

```yaml
run:
  - synthesis.output
  - matsim.simulation.full_run
  - analysis.synthesis.population
```

et les paramètres suivants restent activés :

```yaml
run_matsim: true
write_jar: true
```

## Résultats produits

La racine de `output/` contient notamment :

- les personnes et ménages synthétiques ;
- les activités, déplacements et étapes modales ;
- les couches géographiques GeoPackage ;
- le réseau, les plans, les lieux et les véhicules MATSim ;
- la configuration et les métadonnées de l'exécution.

`output/simulation_output/` contient les plans finaux, les événements MATSim,
les tables Eqasim compressées en Zstandard et les indicateurs de convergence.

La description de chaque fichier est disponible dans
[`output/README.md`](output/README.md) et
[`output/simulation_output/README.md`](output/simulation_output/README.md).

## Filtrage pour le cas d'étude de La Rochelle

Le notebook
[`output/eqasim_output_filtered/create_output_filtered.ipynb`](output/eqasim_output_filtered/create_output_filtered.ipynb)
réduit les sorties départementales avant leur utilisation dans la suite du
projet.

Une personne est conservée si :

- son ménage est localisé dans l'une des huit communes périurbaines retenues ;
  ou
- toutes ses activités sont situées dans les 28 communes de la Communauté
  d'agglomération de La Rochelle.

L'union de ces deux ensembles permet de conserver à la fois une population
résidente ciblée et les personnes dont le programme d'activités concerne
entièrement l'agglomération.

Pour l'exécution de référence à 11 %, le filtre conserve :

| Élément | Nombre |
|---|---:|
| Personnes | 16 046 |
| Ménages | 9 591 |
| Activités MATSim | 68 346 |
| Déplacements MATSim | 52 431 |
| Étapes de transport collectif | 7 706 |

Le notebook et tous ses fichiers de sortie sont décrits dans
[`output/eqasim_output_filtered/README.md`](output/eqasim_output_filtered/README.md).

## Contrôle de qualité

Les fichiers de `output/analysis_population/` comparent la population
synthétique aux données de référence pour plusieurs dimensions : âge,
possession du permis, motorisation, distances et comportements de déplacement.
Ils servent à contrôler la synthèse, mais ne remplacent pas une calibration
locale de MATSim.

Deux limites mineures ont été identifiées lors du filtrage :

- 14 ménages n'ont pas de commune dans `17households.csv`, car leur programme
  d'activités issu de l'EMP ne contient aucune activité `home`. Leur
  localisation existe néanmoins dans les étapes internes d'Eqasim ;
- un lieu de travail SIRENE se trouve environ 10 mètres à l'extérieur de son
  polygone IRIS, ce qui empêche la jointure spatiale stricte.

La sélection a été recalculée avec les localisations connues : ces deux cas ne
changent pas les 16 046 personnes retenues pour l'exécution de référence.

## Reproductibilité

Pour pouvoir comparer deux scénarios :

1. conserver les mêmes archives de données ;
2. conserver `config_17.yml` ;
3. conserver la graine aléatoire ;
4. utiliser le même commit d'`eqasim-france` et la même version
   d'`eqasim-java` ;
5. archiver le fichier `17meta.json` produit ;
6. exécuter le notebook de filtrage dans un noyau Jupyter redémarré.

Les sources BAN, SIRENE, OpenStreetMap et GTFS évoluent régulièrement. Une
archive plus récente peut modifier les localisations, le réseau ou l'offre de
transport, même si le code et la graine restent identiques.

## Contenu conservé sur GitHub

Le dépôt conserve :

- les README ;
- `code/config_17.yml` ;
- les deux fichiers Eqasim modifiés ;
- le notebook de filtrage.

Il exclut :

- les données brutes de `data/` ;
- le clone complet d'`eqasim-france` ;
- les environnements Python ;
- `cache/` ;
- les populations, réseaux et résultats de `output/`.

Cette séparation permet de documenter et reproduire le workflow sans
redistribuer plusieurs gigaoctets de données ni des sources soumises à leurs
propres conditions d'utilisation.

## Publications de référence

Les trois publications suivantes décrivent le cadre Eqasim et la population
synthétique qui sert de modèle méthodologique à ce projet :

1. Hörl, S. et Balac, M. (2021).
   [*Introducing the eqasim pipeline: From raw data to agent-based transport simulation*](https://doi.org/10.1016/j.procs.2021.03.089).
   *Procedia Computer Science*, **184**, 712–719.
   Cet article présente la chaîne reproductible allant des données brutes à la
   simulation de transport multi-agent.

2. Hörl, S. et Balac, M. (2021).
   [*Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data*](https://doi.org/10.1016/j.trc.2021.103291).
   *Transportation Research Part C: Emerging Technologies*, **130**, 103291.
   Cet article détaille la méthode de génération de population et de demande
   synthétiques fondée sur les données françaises ouvertes.

3. Hörl, S. et Balac, M. (2021).
   [*Open synthetic travel demand for Paris and Île-de-France: Inputs and output data*](https://doi.org/10.1016/j.dib.2021.107622).
   *Data in Brief*, **39**, 107622.
   Cet article décrit les données d'entrée, les traitements et la structure des
   sorties du pipeline.

Pour une publication scientifique utilisant cette adaptation, citer les
références pertinentes ci-dessus, puis décrire explicitement les données, la
configuration et les modifications propres au cas de La Rochelle.

## Licence et attribution

`eqasim-france` et `eqasim-java` sont distribués sous la GNU General Public
License version 2. Les fichiers `matched.py` et `full_run.py` présents dans ce
projet sont des adaptations de fichiers d'`eqasim-france`. Leur redistribution
doit conserver l'attribution au projet Eqasim, signaler les modifications et
respecter les obligations de la GPL v2.

Les données d'entrée restent soumises aux licences et conditions de diffusion
de leurs producteurs respectifs. Elles ne sont pas couvertes par la licence du
code et ne sont pas redistribuées dans ce dépôt.
