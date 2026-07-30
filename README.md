<a id="english-version"></a>

<p align="center">
  <img src="assets/sumo-demand2traffic-banner.png" alt="SUMO-demand2traffic — from synthetic travel demand to microscopic traffic simulation" width="100%">
</p>

> **Languages:** The English version is presented first.
> [La version française est disponible plus bas.](#version-francaise)

# SUMO-demand2traffic

[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21680614.svg)](https://doi.org/10.5281/zenodo.21680614)

`SUMO-demand2traffic` is a reproducible workflow for converting a synthetic
population and its daily activity chains into a multimodal microscopic traffic
scenario for [Eclipse SUMO](https://eclipse.dev/sumo/).

The project connects three complementary modelling environments:

- [Eqasim](https://eqasim.org/) for population synthesis and travel-demand
  modelling;
- [MATSim](https://matsim.org/) for the simulation of daily mobility plans;
- [Eclipse SUMO](https://eclipse.dev/sumo/) for multimodal microscopic traffic
  simulation and individual emission assessment.

The workflow is intended to be reusable for other territories when suitable
demographic, geographic, mobility, public-transport, and road-network data are
available. The configuration and reference results supplied here correspond to
an application to **Charente-Maritime and the Communauté d'Agglomération de La
Rochelle (CdA), France**.

> This repository documents a research workflow and adaptations of upstream
> open-source projects. It is not an official Eqasim, MATSim, or SUMO
> distribution.

## Objectives

The main objective is to preserve the link between people, households,
activities, trips, transport modes, vehicles, and emissions throughout the
modelling chain. The repository makes it possible to:

- generate a spatially explicit synthetic population;
- construct daily activity and travel plans;
- simulate mode choice and mobility with Eqasim and MATSim;
- extract a geographical study population without discarding relevant
  boundary-crossing trips;
- build a multimodal SUMO network from OpenStreetMap;
- map activity locations to the SUMO network;
- import a GTFS public-transport service;
- convert MATSim plans into SUMO person plans;
- assign HBEFA4 emission classes to private vehicles;
- run the final SUMO simulation and produce person-, vehicle-, traffic-, and
  emission-related outputs.

The resulting scenario can support research on travel demand, traffic,
individual exposure and emissions, as well as autonomous demand-responsive
transport.

## Processing chain

| Stage | Main process | Main result |
|---:|---|---|
| 1 | Download and prepare demographic, geographic, mobility, and transport data | Reproducible local input dataset |
| 2 | Generate persons, households, activities, and locations with Eqasim | Spatial synthetic population |
| 3 | Run the Eqasim–MATSim scenario | Simulated daily mobility plans |
| 4 | Filter the CdA study population after simulation | Persons, households, activities, and trips required by SUMO |
| 5 | Convert OpenStreetMap data and position activities | SUMO multimodal network and network-linked facilities |
| 6 | Import the Yélo GTFS service | SUMO public-transport stops, routes, and vehicles |
| 7 | Convert individual plans and assign HBEFA4 vehicle types | SUMO population and vehicle demand |
| 8 | Run the TraCI-controlled SUMO scenario | Traffic, mobility, diagnostic, and emission outputs |

The two major parts of this chain are documented independently:

1. [`1-Eqasim/`](1-Eqasim/README.md): synthetic population, Eqasim–MATSim
   simulation, and study-area filtering;
2. [`2-SUMO/`](2-SUMO/README.md): network construction, activity placement,
   public transport, trip conversion, vehicles, and microscopic simulation.

## Reference application: Communauté d'Agglomération de La Rochelle

The reference territory is the **Communauté d'Agglomération de La Rochelle
(CdA)**. The synthetic population
is first generated for **Charente-Maritime (department 17)** using an
**11% population sample** and the 2019 French mobility survey selected for the
project. Filtering is performed only after the MATSim simulation so that
complete daily mobility chains are available before the study population is
selected.

The selection was designed for the **Yélo DETA** research project. It combines
residents of the eight peri-urban and rural municipalities targeted by the
project with people whose simulated daily travel takes place within the
28 municipalities of the CdA. In the filtering notebook, the second group is
identified by requiring all known activities of a person to be located inside
the CdA.

The filtered reference dataset contains:

| Element | Count |
|---|---:|
| Persons | 16,046 |
| Households | 9,591 |
| Activities | 68,346 |
| Trips | 52,431 |
| Public-transport legs | 7,706 |

The reference SUMO conversion writes 15,371 persons. The conversion log
documents 675 persons that could not be transferred, mainly because a route or
network access could not be constructed. These counts are reference controls,
not values hard-coded into the method.

## Repository structure

```text
SUMO-demand2traffic/
|-- README.md
|-- LICENSE
|-- THIRD_PARTY_LICENSES.md
|-- LICENSES/
|   `-- GPL-2.0-only.txt
|-- CITATION.cff
|-- assets/
|   `-- sumo-demand2traffic-banner.png
|-- 1-Eqasim/
|   |-- data/
|   |-- code/
|   `-- output/
`-- 2-SUMO/
    |-- 1-network/
    |-- 2-POI's/
    |-- 3-public_transport/
    |-- 4-convert_trips/
    |-- 5-vehicles/
    `-- 6-simulation/
```

| Path | Purpose |
|---|---|
| [`1-Eqasim/data/`](1-Eqasim/data/README.md) | Required Eqasim data sources and download instructions |
| [`1-Eqasim/code/`](1-Eqasim/code/README.md) | Case-study configuration and project-specific Eqasim adaptations |
| [`1-Eqasim/output/`](1-Eqasim/output/README.md) | Description of the synthetic-population and MATSim outputs |
| [`2-SUMO/1-network/`](2-SUMO/1-network/README.md) | OpenStreetMap extraction and SUMO network construction |
| [`2-SUMO/2-POI's/`](2-SUMO/2-POI's/README.md) | Activity-facility mapping to SUMO edges and lanes |
| [`2-SUMO/3-public_transport/`](2-SUMO/3-public_transport/README.md) | Yélo GTFS conversion and public-transport verification |
| [`2-SUMO/4-convert_trips/`](2-SUMO/4-convert_trips/README.md) | Conversion of Eqasim plans into SUMO person plans |
| [`2-SUMO/5-vehicles/`](2-SUMO/5-vehicles/README.md) | Vehicle-fleet and HBEFA4 emission-class assignment |
| [`2-SUMO/6-simulation/`](2-SUMO/6-simulation/README.md) | Final SUMO/TraCI simulation and diagnostic outputs |

Each subfolder README describes its inputs, processing steps, outputs, quality
checks, and known limitations.

## Data availability and Git policy

Raw input data, complete upstream source-code clones, caches, and large
generated outputs are **not distributed through this repository**. This avoids
redistributing restricted or versioned datasets and keeps the repository
lightweight.

The documentation instead provides:

- the official source of each external dataset;
- the expected filename and local directory;
- the relevant date, release, or version when available;
- the procedure required to regenerate intermediate and final results.

Users must download the required data themselves and comply with each data
producer's licence and conditions of use. Start with:

- [`1-Eqasim/data/README.md`](1-Eqasim/data/README.md) for population and
  Eqasim–MATSim inputs;
- [`2-SUMO/1-network/input/README.md`](2-SUMO/1-network/input/README.md) for
  the Geofabrik OpenStreetMap extract;
- the input sections of the other [`2-SUMO`](2-SUMO/README.md) step READMEs.

## Software requirements

The reference workflow was executed on **Windows**, using **Command Prompt**
and **Visual Studio Code**. Its main requirements are:

- Git and [uv](https://docs.astral.sh/uv/);
- Python and Jupyter;
- Java and Maven;
- Eclipse SUMO, including `netconvert`, `polyconvert`, `sumolib`, and `traci`;
- Osmium Tool;
- sufficient memory and disk space for the Eqasim, MATSim, and SUMO outputs.

The documented reference environment used Python 3.13, Java 25, and SUMO
1.27.1. Exact upstream versions and commits are recorded in the component
READMEs. Different software or data versions may produce different results.

## Reproducing the workflow

### 1. Obtain the repository

```bat
git clone https://github.com/NGALENAL1004/SUMO-demand2traffic.git
cd SUMO-demand2traffic
```

### 2. Generate and simulate the synthetic population

Follow [`1-Eqasim/README.md`](1-Eqasim/README.md) and
[`1-Eqasim/code/README.md`](1-Eqasim/code/README.md). The latter explains how
to retrieve the tested `eqasim-france` commit, copy the three project-specific
files into the local clone, install its dependencies, and run:

```bat
uv run -m synpp config_17.yml
```

The raw data must first be placed according to
[`1-Eqasim/data/README.md`](1-Eqasim/data/README.md). After the MATSim run,
execute the documented filtering notebook to prepare the files consumed by
SUMO.

### 3. Build and run the SUMO scenario

Follow [`2-SUMO/README.md`](2-SUMO/README.md) in numerical order:

1. build the network;
2. map the activity locations;
3. import and verify public transport;
4. convert the individual trips;
5. assign vehicle and emission classes;
6. run the final SUMO/TraCI simulation.

Notebooks use relative paths. Run each notebook from the directory in which it
is located and verify the documented outputs before moving to the next stage.

## Reproducibility and quality control

For a scientifically traceable experiment:

- record the Git commit of this repository and of each upstream project;
- retain the configuration files, random seed, sampling rate, data release
  dates, and selected GTFS service date;
- archive pipeline logs and counts at every interface;
- compare generated counts with the reference controls in the READMEs;
- report all people, activities, facilities, routes, or public-transport legs
  rejected during conversion;
- document any manual adjustment to the vehicle distribution or simulation
  controller.

The reference pipeline uses a random seed of `1234`. Some results may still
vary with dependency versions, operating systems, input releases, or changes
to external services.

## Important limitations

- The reference scenario represents a sample rather than the complete
  population.
- Synthetic attributes and activity chains inherit the assumptions and
  limitations of the demographic sources, mobility survey, Eqasim, and MATSim.
- Spatial joins and network mapping can reject facilities located just outside
  a polygon or without a usable nearby edge.
- The current public-transport scenario represents the GTFS service selected
  for the reference simulation date.
- The HBEFA4 vehicle distribution must be checked against the fleet data used
  for each experiment.
- The TraCI controller can apply a documented fallback service to stranded
  public-transport users. This changes their simulated travel behaviour and
  must be reported when the mechanism is enabled.

The detailed logs and step-specific READMEs remain the authoritative place for
diagnosing these cases.

## Associated publication and citation

The methodology and its application are described in:

> Ngari Lendoye, A., Graindorge, T., Fèvre, C., & Bouju, A. (2026).
> *Integrating Synthetic Populations and Activity Chains for Individual
> Emission Assessment in SUMO*. Zenodo. SUMO Conference 2026,
> Berlin-Adlershof, Germany.
> [https://doi.org/10.5281/zenodo.21676913](https://doi.org/10.5281/zenodo.21676913)

If you use this software, please cite both the software and the associated
publication where appropriate. Machine-readable citation metadata are
provided in [`CITATION.cff`](CITATION.cff).

- Software version `v1.0.0`:
  [10.5281/zenodo.21680615](https://doi.org/10.5281/zenodo.21680615)
- All software versions:
  [10.5281/zenodo.21680614](https://doi.org/10.5281/zenodo.21680614)

## Licence

Unless stated otherwise, the project-original software and documentation are
distributed under the **GNU General Public License version 3 only**
(`GPL-3.0-only`). The complete licence text is provided in
[`LICENSE`](LICENSE).

This licence does not replace the terms attached to third-party or adapted
files. In particular, the Eqasim-derived files remain under `GPL-2.0-only`,
and the copied SUMO utilities retain `EPL-2.0 OR GPL-2.0-or-later`. Their
scope, attribution, and accompanying licence text are documented in
[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) and [`LICENSES/`](LICENSES/).
Input datasets are not covered by the software licence.

## Project origin and supervision

This research workflow was designed and implemented by **Alix NGARI LENDOYE**,
affiliated with **EIGSI – École d'ingénieurs en génie des systèmes
industriels** and **La Rochelle Université – Laboratoire Informatique, Image
et Interaction (L3i)**, as part of his doctoral research on autonomous
demand-responsive transport.

The doctoral research is supervised by **Tatiana Graindorge**,
**Corwin Fèvre**, and **Alain Bouju**. Their scientific guidance contributes
to the research framework, methodological choices, and development of this
project.

The workflow builds on and adapts open-source components, particularly Eqasim,
MATSim, and Eclipse SUMO. These components remain credited to their respective
projects and contributors.

## Official resources and acknowledgements

- Eqasim website: <https://eqasim.org/>
- `eqasim-france` repository:
  <https://github.com/eqasim-org/eqasim-france>
- `eqasim-java` repository: <https://github.com/eqasim-org/eqasim-java>
- `eqasim-france` documentation:
  <https://eqasim-org.github.io/eqasim-france/>
- MATSim: <https://matsim.org/>
- Eclipse SUMO: <https://eclipse.dev/sumo/>
- SUMO documentation: <https://sumo.dlr.de/docs/>
- OpenStreetMap: <https://www.openstreetmap.org/>
- Geofabrik downloads: <https://download.geofabrik.de/>
- Yélo DETA / Yélo'Flex project:
  <https://www.agglo-larochelle.fr/-/yelo-deta-le-transport-automatise>

Project-specific adaptations of upstream files remain subject to their
original licences. OpenStreetMap data are distributed under the ODbL, and
other input datasets remain subject to the terms of their respective
producers. Consult the notices in each component and data source before reuse.

---

<a id="version-francaise"></a>

> **Langues :** la version française est présentée ci-dessous.
> [The English version is available above.](#english-version)

# SUMO-demand2traffic

[![DOI du logiciel](https://zenodo.org/badge/DOI/10.5281/zenodo.21680614.svg)](https://doi.org/10.5281/zenodo.21680614)

`SUMO-demand2traffic` est une chaîne de traitement reproductible permettant de
convertir une population synthétique et ses chaînes d'activités quotidiennes
en un scénario multimodal de simulation microscopique pour
[Eclipse SUMO](https://eclipse.dev/sumo/).

Le projet relie trois environnements de modélisation complémentaires :

- [Eqasim](https://eqasim.org/) pour la synthèse de population et la
  modélisation de la demande de mobilité ;
- [MATSim](https://matsim.org/) pour la simulation des plans de mobilité
  quotidiens ;
- [Eclipse SUMO](https://eclipse.dev/sumo/) pour la simulation microscopique
  multimodale du trafic et l'évaluation individuelle des émissions.

La méthode est conçue pour être réutilisable sur d'autres territoires lorsque
les données démographiques, géographiques, de mobilité, de transport public et
de réseau routier nécessaires sont disponibles. La configuration et les
résultats de référence fournis ici correspondent à une application à la
**Charente-Maritime et à la Communauté d'Agglomération de La Rochelle (CdA),
en France**.

> Ce dépôt documente une chaîne de traitement scientifique et des adaptations
> de projets open source existants. Il ne constitue pas une distribution
> officielle d'Eqasim, de MATSim ou de SUMO.

## Objectifs

L'objectif principal est de préserver le lien entre les personnes, les
ménages, les activités, les déplacements, les modes de transport, les
véhicules et les émissions tout au long de la chaîne de modélisation. Le dépôt
permet de :

- générer une population synthétique spatialement explicite ;
- construire les programmes d'activités et les déplacements quotidiens ;
- simuler le choix modal et la mobilité avec Eqasim et MATSim ;
- extraire une population d'étude sans supprimer les déplacements pertinents
  qui franchissent les limites du territoire ;
- construire un réseau SUMO multimodal à partir d'OpenStreetMap ;
- rattacher les lieux d'activité au réseau SUMO ;
- importer une offre de transport public au format GTFS ;
- convertir les plans MATSim en plans de personnes SUMO ;
- attribuer des classes d'émission HBEFA4 aux véhicules particuliers ;
- exécuter la simulation SUMO finale et produire des sorties relatives aux
  personnes, aux véhicules, au trafic et aux émissions.

Le scénario obtenu peut servir à des recherches sur la demande de mobilité, le
trafic, l'exposition et les émissions individuelles, ainsi que sur le transport
autonome à la demande.

## Chaîne de traitement

| Étape | Traitement principal | Résultat principal |
|---:|---|---|
| 1 | Télécharger et préparer les données démographiques, géographiques, de mobilité et de transport | Jeu local de données d'entrée reproductible |
| 2 | Générer les personnes, ménages, activités et localisations avec Eqasim | Population synthétique spatialisée |
| 3 | Exécuter le scénario Eqasim–MATSim | Plans de mobilité quotidiens simulés |
| 4 | Filtrer la population d'étude de la CdA après la simulation | Personnes, ménages, activités et déplacements nécessaires à SUMO |
| 5 | Convertir OpenStreetMap et positionner les activités | Réseau SUMO multimodal et équipements rattachés au réseau |
| 6 | Importer l'offre GTFS Yélo | Arrêts, lignes et véhicules de transport public dans SUMO |
| 7 | Convertir les plans individuels et attribuer les types de véhicules HBEFA4 | Population et demande automobile SUMO |
| 8 | Exécuter le scénario SUMO contrôlé par TraCI | Sorties de trafic, de mobilité, de diagnostic et d'émissions |

Les deux grandes parties de cette chaîne sont documentées séparément :

1. [`1-Eqasim/`](1-Eqasim/README.md) : population synthétique, simulation
   Eqasim–MATSim et filtrage du territoire d'étude ;
2. [`2-SUMO/`](2-SUMO/README.md) : construction du réseau, positionnement des
   activités, transport public, conversion des déplacements, véhicules et
   simulation microscopique.

## Application de référence : Communauté d'Agglomération de La Rochelle

Le territoire de référence est la **Communauté d'Agglomération de La Rochelle
(CdA)**, et non la seule commune de La Rochelle. La population synthétique est
d'abord générée pour la **Charente-Maritime (département 17)**, avec un
**échantillon de population de 11 %** et l'enquête française de mobilité 2019
retenue pour le projet. Le filtrage intervient seulement après la simulation
MATSim afin de disposer des chaînes complètes de mobilité quotidienne avant de
sélectionner la population d'étude.

Cette sélection a été définie pour le projet de recherche **Yélo DETA**. Elle
réunit les habitants des huit communes périurbaines et rurales visées par le
projet et les personnes dont les déplacements quotidiens simulés s'effectuent
dans les 28 communes de la CdA. Dans le notebook de filtrage, ce second groupe
est identifié en vérifiant que toutes les activités connues d'une personne
sont localisées dans la CdA.

Le jeu de données filtré de référence contient :

| Élément | Nombre |
|---|---:|
| Personnes | 16 046 |
| Ménages | 9 591 |
| Activités | 68 346 |
| Déplacements | 52 431 |
| Trajets en transport public | 7 706 |

La conversion SUMO de référence écrit 15 371 personnes. Le journal de
conversion documente 675 personnes qui n'ont pas pu être transférées,
principalement parce qu'un itinéraire ou un accès au réseau ne pouvait pas
être construit. Ces valeurs sont des contrôles de référence et non des
paramètres imposés par la méthode.

## Organisation du dépôt

```text
SUMO-demand2traffic/
|-- README.md
|-- LICENSE
|-- THIRD_PARTY_LICENSES.md
|-- LICENSES/
|   `-- GPL-2.0-only.txt
|-- CITATION.cff
|-- assets/
|   `-- sumo-demand2traffic-banner.png
|-- 1-Eqasim/
|   |-- data/
|   |-- code/
|   `-- output/
`-- 2-SUMO/
    |-- 1-network/
    |-- 2-POI's/
    |-- 3-public_transport/
    |-- 4-convert_trips/
    |-- 5-vehicles/
    `-- 6-simulation/
```

| Chemin | Rôle |
|---|---|
| [`1-Eqasim/data/`](1-Eqasim/data/README.md) | Sources des données Eqasim requises et instructions de téléchargement |
| [`1-Eqasim/code/`](1-Eqasim/code/README.md) | Configuration du cas d'étude et adaptations spécifiques d'Eqasim |
| [`1-Eqasim/output/`](1-Eqasim/output/README.md) | Description des sorties de population synthétique et de MATSim |
| [`2-SUMO/1-network/`](2-SUMO/1-network/README.md) | Extraction OpenStreetMap et construction du réseau SUMO |
| [`2-SUMO/2-POI's/`](2-SUMO/2-POI's/README.md) | Rattachement des lieux d'activité aux arêtes et voies SUMO |
| [`2-SUMO/3-public_transport/`](2-SUMO/3-public_transport/README.md) | Conversion du GTFS Yélo et vérification du transport public |
| [`2-SUMO/4-convert_trips/`](2-SUMO/4-convert_trips/README.md) | Conversion des plans Eqasim en plans de personnes SUMO |
| [`2-SUMO/5-vehicles/`](2-SUMO/5-vehicles/README.md) | Affectation de la flotte et des classes d'émission HBEFA4 |
| [`2-SUMO/6-simulation/`](2-SUMO/6-simulation/README.md) | Simulation SUMO/TraCI finale et sorties de diagnostic |

Le README de chaque sous-dossier décrit ses entrées, ses traitements, ses
sorties, ses contrôles de qualité et ses limites connues.

## Disponibilité des données et politique Git

Les données d'entrée brutes, les clones complets des codes sources amont, les
caches et les sorties volumineuses générées ne sont **pas distribués dans ce
dépôt**. Cela évite de redistribuer des jeux de données restreints ou versionnés
et permet de conserver un dépôt léger.

La documentation fournit à la place :

- la source officielle de chaque jeu de données externe ;
- le nom de fichier attendu et son dossier local ;
- la date, la version ou la livraison pertinente lorsqu'elle est connue ;
- la procédure permettant de régénérer les résultats intermédiaires et finaux.

Chaque utilisateur doit télécharger lui-même les données nécessaires et
respecter la licence et les conditions d'utilisation de chaque producteur.
Commencez par :

- [`1-Eqasim/data/README.md`](1-Eqasim/data/README.md) pour les entrées de la
  population et d'Eqasim–MATSim ;
- [`2-SUMO/1-network/input/README.md`](2-SUMO/1-network/input/README.md) pour
  l'extrait OpenStreetMap de Geofabrik ;
- les sections consacrées aux entrées dans les autres README des étapes
  [`2-SUMO`](2-SUMO/README.md).

## Logiciels requis

La chaîne de référence a été exécutée sous **Windows**, avec **l'invite de
commandes** et **Visual Studio Code**. Ses principaux prérequis sont :

- Git et [uv](https://docs.astral.sh/uv/) ;
- Python et Jupyter ;
- Java et Maven ;
- Eclipse SUMO, notamment `netconvert`, `polyconvert`, `sumolib` et `traci` ;
- Osmium Tool ;
- suffisamment de mémoire et d'espace disque pour les sorties d'Eqasim, de
  MATSim et de SUMO.

L'environnement de référence documenté utilisait Python 3.13, Java 25 et SUMO
1.27.1. Les versions et commits amont exacts sont indiqués dans les README des
composants. L'utilisation d'autres versions des logiciels ou des données peut
modifier les résultats.

## Reproduction de la chaîne de traitement

### 1. Récupérer le dépôt

```bat
git clone https://github.com/NGALENAL1004/SUMO-demand2traffic.git
cd SUMO-demand2traffic
```

### 2. Générer et simuler la population synthétique

Suivez [`1-Eqasim/README.md`](1-Eqasim/README.md) et
[`1-Eqasim/code/README.md`](1-Eqasim/code/README.md). Le second explique
comment récupérer le commit testé d'`eqasim-france`, copier les trois fichiers
propres au projet dans le clone local, installer les dépendances et exécuter :

```bat
uv run -m synpp config_17.yml
```

Les données brutes doivent d'abord être placées conformément à
[`1-Eqasim/data/README.md`](1-Eqasim/data/README.md). Après la simulation
MATSim, exécutez le notebook de filtrage documenté afin de préparer les
fichiers utilisés par SUMO.

### 3. Construire et exécuter le scénario SUMO

Suivez [`2-SUMO/README.md`](2-SUMO/README.md) dans l'ordre numérique :

1. construire le réseau ;
2. rattacher les lieux d'activité ;
3. importer et vérifier le transport public ;
4. convertir les déplacements individuels ;
5. attribuer les véhicules et les classes d'émission ;
6. exécuter la simulation SUMO/TraCI finale.

Les notebooks utilisent des chemins relatifs. Exécutez chaque notebook depuis
le dossier qui le contient et vérifiez les sorties documentées avant de passer
à l'étape suivante.

## Reproductibilité et contrôle qualité

Pour une expérience scientifiquement traçable :

- consignez le commit Git de ce dépôt et de chaque projet amont ;
- conservez les fichiers de configuration, la graine aléatoire, le taux
  d'échantillonnage, les versions des données et la date de service GTFS
  sélectionnée ;
- archivez les journaux d'exécution et les effectifs à chaque interface ;
- comparez les effectifs générés aux contrôles de référence des README ;
- signalez toutes les personnes, activités, équipements, routes ou étapes de
  transport public rejetés pendant la conversion ;
- documentez toute modification manuelle de la distribution des véhicules ou
  du contrôleur de simulation.

La chaîne de référence utilise la graine aléatoire `1234`. Certains résultats
peuvent néanmoins varier selon les versions des dépendances, le système
d'exploitation, les livraisons des données ou l'évolution de services
externes.

## Limites importantes

- Le scénario de référence représente un échantillon et non la population
  complète.
- Les attributs synthétiques et les chaînes d'activités héritent des hypothèses
  et limites des sources démographiques, de l'enquête de mobilité, d'Eqasim et
  de MATSim.
- Les jointures spatiales et le rattachement au réseau peuvent rejeter des
  équipements situés juste à l'extérieur d'un polygone ou sans arête
  accessible à proximité.
- Le scénario de transport public actuel représente le service GTFS retenu
  pour la date de simulation de référence.
- La distribution des véhicules HBEFA4 doit être vérifiée par rapport aux
  données de parc utilisées pour chaque expérience.
- Le contrôleur TraCI peut appliquer un service de remplacement documenté aux
  usagers du transport public bloqués. Cela modifie leur comportement de
  déplacement simulé et doit être signalé lorsque ce mécanisme est activé.

Les journaux détaillés et les README propres à chaque étape constituent la
référence pour diagnostiquer ces cas.

## Publication associée et citation

La méthode et son application sont décrites dans :

> Ngari Lendoye, A., Graindorge, T., Fèvre, C., & Bouju, A. (2026).
> *Integrating Synthetic Populations and Activity Chains for Individual
> Emission Assessment in SUMO*. Zenodo. SUMO Conference 2026,
> Berlin-Adlershof, Allemagne.
> [https://doi.org/10.5281/zenodo.21676913](https://doi.org/10.5281/zenodo.21676913)

Si vous utilisez ce logiciel, veuillez citer le logiciel et la publication
associée lorsque cela est pertinent. Les métadonnées de citation lisibles par
machine se trouvent dans [`CITATION.cff`](CITATION.cff).

- Version `v1.0.0` du logiciel :
  [10.5281/zenodo.21680615](https://doi.org/10.5281/zenodo.21680615)
- Ensemble des versions du logiciel :
  [10.5281/zenodo.21680614](https://doi.org/10.5281/zenodo.21680614)

## Licence

Sauf mention contraire, les logiciels et la documentation propres au projet
sont distribués sous la **GNU General Public License version 3 uniquement**
(`GPL-3.0-only`). Le texte complet de la licence est fourni dans
[`LICENSE`](LICENSE).

Cette licence ne remplace pas les conditions applicables aux fichiers tiers ou
adaptés. Les fichiers issus d'Eqasim restent notamment sous `GPL-2.0-only`,
tandis que les utilitaires SUMO copiés conservent
`EPL-2.0 OR GPL-2.0-or-later`. Leur périmètre, leur attribution et les textes
de licence associés sont documentés dans
[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) et [`LICENSES/`](LICENSES/).
Les données d'entrée ne sont pas couvertes par la licence du logiciel.

## Origine et encadrement du projet

Cette chaîne de traitement scientifique a été conçue et mise en œuvre par
**Alix NGARI LENDOYE**, affilié à **l'EIGSI – École d'ingénieurs en génie des
systèmes industriels** et à **La Rochelle Université – Laboratoire
Informatique, Image et Interaction (L3i)**, dans le cadre de ses recherches
doctorales sur le transport autonome à la demande.

Ces travaux de doctorat sont encadrés par **Tatiana Graindorge**,
**Corwin Fèvre** et **Alain Bouju**. Leur accompagnement scientifique contribue
au cadre de recherche, aux choix méthodologiques et au développement de ce
projet.

La chaîne de traitement s'appuie sur et adapte des composants open source,
notamment Eqasim, MATSim et Eclipse SUMO. Ces composants restent attribués à
leurs projets et contributeurs respectifs.

## Ressources officielles et remerciements

- Site d'Eqasim : <https://eqasim.org/>
- Dépôt `eqasim-france` :
  <https://github.com/eqasim-org/eqasim-france>
- Dépôt `eqasim-java` : <https://github.com/eqasim-org/eqasim-java>
- Documentation d'`eqasim-france` :
  <https://eqasim-org.github.io/eqasim-france/>
- MATSim : <https://matsim.org/>
- Eclipse SUMO : <https://eclipse.dev/sumo/>
- Documentation SUMO : <https://sumo.dlr.de/docs/>
- OpenStreetMap : <https://www.openstreetmap.org/>
- Téléchargements Geofabrik : <https://download.geofabrik.de/>
- Projet Yélo DETA / Yélo'Flex :
  <https://www.agglo-larochelle.fr/-/yelo-deta-le-transport-automatise>

Les adaptations de fichiers amont propres au projet restent soumises à leurs
licences d'origine. Les données OpenStreetMap sont distribuées sous licence
ODbL et les autres données d'entrée restent soumises aux conditions de leurs
producteurs respectifs. Consultez les mentions de chaque composant et de
chaque source de données avant toute réutilisation.
