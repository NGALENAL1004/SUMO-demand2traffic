<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Importing Yélo public transport into SUMO

This folder creates the SUMO public transport supply used by the La Rochelle
scenario. It maps a dated Yélo GTFS timetable to the SUMO network, generates
stops and scheduled vehicles, and adds the official line colours for
visualisation.

The workflow follows the official
[SUMO GTFS tutorial](https://sumo.dlr.de/docs/Tutorials/GTFS.html) and uses the
SUMO `gtfs2pt.py` tool.

## Files retained in the repository

```text
3-public_transport/
|-- README.md
|-- 1-generate_stops.bat
|-- 2-generate_pt_from_gtfs.bat
|-- 3-pt.ipynb
|-- gtfs2pt.py
|-- gtfs2fcd.py
|-- gtfs2osm.py
|-- pt.sumocfg
`-- input/
    `-- README.md
```

The three `gtfs2*.py` files come from Eclipse SUMO and retain their original
copyright and licence headers (`EPL-2.0 OR GPL-2.0-or-later`).

## Required inputs

| Input | Expected location | Purpose |
|---|---|---|
| `cda_la_rochelle.osm` | `../1-network/` | OSM study-area extract used to rebuild the PT-ready network and extract stops |
| `ca_la_rochelle-aggregated-gtfs.zip` | `input/` | Yélo routes, stops, trips, schedules, and shapes |

The reference timetable date selected in
`2-generate_pt_from_gtfs.bat` is:

```text
20260317
```

The selected date is part of the scenario definition. A replacement GTFS
archive must cover this date, or `GTFS_DATE` must be changed to a valid date
inside the new feed.

Download and snapshot information for the GTFS file is provided in
[`input/README.md`](input/README.md).

## Prerequisites

- Eclipse SUMO `1.27.1` for the documented reference outputs;
- Python and `pandas`;
- Java when the optional FCD mapping library is used;
- `SUMO_HOME` pointing to the SUMO installation;
- SUMO's `bin` directory available in the Windows `PATH`.

In Command Prompt, check:

```bat
echo %SUMO_HOME%
netconvert --version
python --version
```

The Python scripts import tools from `%SUMO_HOME%\tools`.

## Processing sequence

Run all commands from the `3-public_transport` directory.

### Step 1 — Generate a PT-ready network and candidate stops

Execute:

```bat
1-generate_stops.bat
```

The batch file reads:

```text
../1-network/cda_la_rochelle.osm
```

It calls `netconvert` with guessed sidewalks, crossings, walking areas, and
OSM stop extraction. It writes:

| Output | Description |
|---|---|
| `cda_la_rochelle.net.xml` | Local network used during GTFS mapping |
| `busstop.add.xml` | Candidate public transport stops extracted from OSM |

This local network is generated from the same OSM extract and pedestrian
options as the network in `1-network`. The final simulation nevertheless uses
`../1-network/cda_la_rochelle.net.xml`; therefore, the same SUMO version and
network-conversion settings must be used in both steps so that edge and lane
identifiers remain compatible.

### Step 2 — Map the GTFS timetable to the network

Execute:

```bat
2-generate_pt_from_gtfs.bat
```

The batch file runs:

```bat
python gtfs2pt.py --network "cda_la_rochelle.net.xml" --gtfs "input\ca_la_rochelle-aggregated-gtfs.zip" --date 20260317 --stops "busstop.add.xml"
```

This operation may take several hours and can remain silent for long periods.
The main outputs are:

| Output | Description |
|---|---|
| `vtypes.xml` | SUMO vehicle types for buses and ferries |
| `gtfs_pt_stops.add.xml` | Mapped public transport stops and access information |
| `gtfs_pt_vehicles.add.xml` | Routes and scheduled vehicles for the selected date |
| `fcd/gtfs/` | Intermediate floating-car-data traces |
| `resources/gtfs/` | Intermediate mode-specific networks used for map matching |

The intermediate directories and all generated XML files remain local.

### Step 3 — Apply GTFS route colours

Open `3-pt.ipynb` in VS Code and run its only cell. The notebook reads:

- `input/ca_la_rochelle-aggregated-gtfs.zip`, especially `routes.txt` and
  `trips.txt`;
- `gtfs_pt_vehicles.add.xml`.

It converts each hexadecimal GTFS `route_color` into an RGB SUMO colour and
writes:

| Output | Description |
|---|---|
| `gtfs_pt_vehicles_colored.add.xml` | PT vehicle file used by the final simulation |
| `trip_to_route_color.csv` | Diagnostic mapping between GTFS trips, routes, and colours |

## Reference run checks

The saved notebook output reports:

- 1,638 scheduled vehicles;
- 1,638 vehicles successfully coloured;
- no missing line identifier;
- no unknown trip-to-route mapping;
- no missing or invalid route colour.

The GTFS mapping produced 240 SUMO route identifiers. These values are useful
as regression checks but may change with another timetable snapshot, date, or
SUMO version.

## Optional visual check

`pt.sumocfg` can be opened with:

```bat
sumo-gui -c pt.sumocfg
```

It loads the canonical network from `1-network`, the generated stops, vehicle
types, and coloured PT vehicles. Check that:

- stops lie on valid network lanes;
- buses and ferries appear at plausible times and places;
- line colours are present;
- the console does not report systematic invalid edge or stop identifiers.

## Generated files and Git

Raw GTFS data, networks, stops, vehicles, mapping intermediates, cache folders,
and debug CSV files are excluded from Git. They can be regenerated from the
tracked scripts, notebook, configuration, and input documentation.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Import des transports collectifs Yélo dans SUMO

Ce dossier construit l’offre de transport collectif SUMO utilisée dans le
scénario de La Rochelle. Il apparie une offre GTFS datée de Yélo au réseau
SUMO, génère les arrêts et véhicules programmés, puis ajoute les couleurs
officielles des lignes pour la visualisation.

La chaîne suit le
[tutoriel GTFS officiel de SUMO](https://sumo.dlr.de/docs/Tutorials/GTFS.html)
et utilise l’outil SUMO `gtfs2pt.py`.

## Fichiers conservés dans le dépôt

```text
3-public_transport/
|-- README.md
|-- 1-generate_stops.bat
|-- 2-generate_pt_from_gtfs.bat
|-- 3-pt.ipynb
|-- gtfs2pt.py
|-- gtfs2fcd.py
|-- gtfs2osm.py
|-- pt.sumocfg
`-- input/
    `-- README.md
```

Les trois fichiers `gtfs2*.py` proviennent d’Eclipse SUMO et conservent leurs
en-têtes d’auteur et de licence d’origine
(`EPL-2.0 OR GPL-2.0-or-later`).

## Entrées nécessaires

| Entrée | Emplacement attendu | Rôle |
|---|---|---|
| `cda_la_rochelle.osm` | `../1-network/` | Extrait OSM de la zone d’étude utilisé pour reconstruire le réseau TC et extraire les arrêts |
| `ca_la_rochelle-aggregated-gtfs.zip` | `input/` | Lignes, arrêts, courses, horaires et tracés Yélo |

La date de référence sélectionnée dans
`2-generate_pt_from_gtfs.bat` est :

```text
20260317
```

Cette date fait partie de la définition du scénario. Une nouvelle archive GTFS
doit couvrir cette date ; sinon, `GTFS_DATE` doit être remplacée par une date
valide de la nouvelle offre.

Les informations de téléchargement et d’identification du fichier GTFS sont
fournies dans [`input/README.md`](input/README.md).

## Prérequis

- Eclipse SUMO `1.27.1` pour reproduire les sorties de référence ;
- Python et `pandas` ;
- Java lorsque la bibliothèque optionnelle d’appariement FCD est utilisée ;
- `SUMO_HOME` pointant vers l’installation de SUMO ;
- le dossier `bin` de SUMO disponible dans le `PATH` Windows.

Dans l’invite de commandes :

```bat
echo %SUMO_HOME%
netconvert --version
python --version
```

Les scripts Python importent des outils depuis `%SUMO_HOME%\tools`.

## Ordre de traitement

Exécuter toutes les commandes depuis le dossier `3-public_transport`.

### Étape 1 — Générer un réseau adapté aux TC et les arrêts candidats

Exécuter :

```bat
1-generate_stops.bat
```

Le fichier batch lit :

```text
../1-network/cda_la_rochelle.osm
```

Il appelle `netconvert` en activant l’estimation des trottoirs, passages
piétons et zones de marche, ainsi que l’extraction des arrêts OSM. Il produit :

| Sortie | Description |
|---|---|
| `cda_la_rochelle.net.xml` | Réseau local utilisé pendant l’appariement GTFS |
| `busstop.add.xml` | Arrêts de transport collectif candidats extraits d’OSM |

Ce réseau local est généré depuis le même extrait OSM et les mêmes options
piétonnes que celui de `1-network`. La simulation finale utilise néanmoins
`../1-network/cda_la_rochelle.net.xml`. Il faut donc employer la même version
de SUMO et les mêmes paramètres de conversion dans les deux étapes afin de
conserver des identifiants d’arêtes et de voies compatibles.

### Étape 2 — Apparier l’offre GTFS au réseau

Exécuter :

```bat
2-generate_pt_from_gtfs.bat
```

Le fichier batch lance :

```bat
python gtfs2pt.py --network "cda_la_rochelle.net.xml" --gtfs "input\ca_la_rochelle-aggregated-gtfs.zip" --date 20260317 --stops "busstop.add.xml"
```

L’opération peut durer plusieurs heures et rester silencieuse pendant de
longues périodes. Les principales sorties sont :

| Sortie | Description |
|---|---|
| `vtypes.xml` | Types de véhicules SUMO pour les bus et ferries |
| `gtfs_pt_stops.add.xml` | Arrêts de transport collectif appariés et accès associés |
| `gtfs_pt_vehicles.add.xml` | Itinéraires et véhicules programmés pour la date choisie |
| `fcd/gtfs/` | Traces FCD intermédiaires |
| `resources/gtfs/` | Réseaux intermédiaires par mode utilisés pour l’appariement |

Les dossiers intermédiaires et tous les XML générés restent locaux.

### Étape 3 — Appliquer les couleurs GTFS

Ouvrir `3-pt.ipynb` dans VS Code et exécuter son unique cellule. Le notebook
lit :

- `input/ca_la_rochelle-aggregated-gtfs.zip`, notamment `routes.txt` et
  `trips.txt` ;
- `gtfs_pt_vehicles.add.xml`.

Il convertit chaque couleur hexadécimale GTFS `route_color` en couleur RGB
SUMO et produit :

| Sortie | Description |
|---|---|
| `gtfs_pt_vehicles_colored.add.xml` | Fichier de véhicules TC utilisé par la simulation finale |
| `trip_to_route_color.csv` | Table de diagnostic entre courses, lignes et couleurs GTFS |

## Contrôles de l’exécution de référence

La sortie enregistrée dans le notebook indique :

- 1 638 véhicules programmés ;
- 1 638 véhicules correctement colorés ;
- aucun identifiant de ligne manquant ;
- aucun appariement course-ligne inconnu ;
- aucune couleur de ligne absente ou invalide.

L’import GTFS a produit 240 identifiants d’itinéraires SUMO. Ces valeurs sont
des contrôles de non-régression ; elles peuvent changer avec une autre archive
GTFS, une autre date ou une autre version de SUMO.

## Contrôle visuel facultatif

Ouvrir `pt.sumocfg` avec :

```bat
sumo-gui -c pt.sumocfg
```

Cette configuration charge le réseau de référence de `1-network`, les arrêts,
les types de véhicules et les véhicules TC colorés. Vérifier que :

- les arrêts se trouvent sur des voies valides ;
- les bus et ferries apparaissent à des horaires et emplacements plausibles ;
- les couleurs de ligne sont présentes ;
- la console ne signale pas systématiquement des arêtes ou arrêts invalides.

## Fichiers générés et Git

Les données GTFS brutes, réseaux, arrêts, véhicules, intermédiaires
d’appariement, caches et CSV de diagnostic sont exclus de Git. Ils peuvent
être régénérés à partir des scripts, du notebook, de la configuration et de
la documentation d’entrée conservés.
