<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Building the SUMO network for La Rochelle

This folder contains the reproducible workflow used to create the SUMO road
and pedestrian network for the La Rochelle case study from OpenStreetMap data.

The workflow is implemented in `network.ipynb`. The regional OpenStreetMap
extract and all generated network files remain local because of their size.
Only the notebook, documentation, and Git exclusion rules are retained in the
repository.

## Folder contents

```text
1-network/
├── README.md
├── network.ipynb
├── input/
│   ├── README.md
│   └── poitou-charentes-260317.osm.pbf  # local, not tracked by Git
├── cda_la_rochelle.osm                  # generated, not tracked by Git
├── cda_la_rochelle.net.xml              # generated, not tracked by Git
└── cda_la_rochelle.poly.xml             # generated, not tracked by Git
```

## Input data

The notebook uses the Poitou-Charentes regional OpenStreetMap extract supplied
by Geofabrik:

- [France download page](https://download.geofabrik.de/europe/france.html);
- [Poitou-Charentes download page](https://download.geofabrik.de/europe/france/poitou-charentes.html);
- [direct `.osm.pbf` download](https://download.geofabrik.de/europe/france/poitou-charentes-latest.osm.pbf).

Download instructions, naming conventions, the checksum of the reference file,
and licence information are provided in [`input/README.md`](input/README.md).

The notebook currently reads:

```text
input/poitou-charentes-260317.osm.pbf
```

## Prerequisites

The reference network was generated on Windows with:

- Python and Jupyter, used to run `network.ipynb`;
- [Osmium Tool](https://osmcode.org/osmium-tool/), for extracting the study
  area from the regional `.osm.pbf` file;
- [Eclipse SUMO](https://eclipse.dev/sumo/), providing `netconvert` and
  `polyconvert`;
- SUMO `1.27.1` for the documented outputs.

The following commands must work from the environment used by the notebook:

```bat
osmium --version
netconvert --version
polyconvert --version
```

If a command is not found, add the corresponding executable folder to the
Windows `PATH`, then restart VS Code before running the notebook.

## Processing chain

| Network construction |
|:---:|
| **Regional input: `poitou-charentes-260317.osm.pbf`** |
| ↓ `osmium extract` |
| **Study-area extract: `cda_la_rochelle.osm`** |
| ↓ `netconvert` |
| **SUMO network: `cda_la_rochelle.net.xml`** |
| ↓ `polyconvert`, using both the OSM extract and network |
| **Display polygons: `cda_la_rochelle.poly.xml`** |

The notebook cells must be executed in order.

## Step 1 — Extract the study area with Osmium

### Input

```text
input/poitou-charentes-260317.osm.pbf
```

### Spatial extent

The notebook uses the following bounding box, expressed as
`longitude_min, latitude_min, longitude_max, latitude_max`:

```text
-1.571,45.800,-0.533,46.353
```

### Equivalent command

```bat
osmium extract -b -1.571,45.800,-0.533,46.353 input\poitou-charentes-260317.osm.pbf -o cda_la_rochelle.osm
```

### Output

`cda_la_rochelle.osm` is an OpenStreetMap XML extract containing the objects
required for the rectangular study area. Osmium may retain nodes just outside
the bounding box when they are needed to preserve complete OSM ways or
relations.

The bounding box is a processing extent, not the exact administrative boundary
of the La Rochelle urban community.

## Step 2 — Convert the OSM extract into a SUMO network

### Input

```text
cda_la_rochelle.osm
```

### Equivalent command

```bat
netconvert --osm-files cda_la_rochelle.osm -o cda_la_rochelle.net.xml --sidewalks.guess true --sidewalks.guess.from-permissions true --crossings.guess true --walkingareas true --ignore-errors true --ignore-errors.edge-type true
```

### Main options

| Option | Purpose |
|---|---|
| `--sidewalks.guess true` | Generates sidewalks when they can be inferred from OSM information |
| `--sidewalks.guess.from-permissions true` | Also infers sidewalks from lane permissions |
| `--crossings.guess true` | Generates pedestrian crossings |
| `--walkingareas true` | Creates pedestrian walking areas at junctions |
| `--ignore-errors true` | Allows conversion to continue despite non-blocking OSM inconsistencies |
| `--ignore-errors.edge-type true` | Ignores unsupported or inconsistent edge-type definitions |

### Output

`cda_la_rochelle.net.xml` is the SUMO network. It contains edges, lanes,
junctions, connections, traffic permissions, and the pedestrian infrastructure
inferred by `netconvert`. The generated file uses the UTM projection selected
automatically by SUMO for the study area.

Using `--ignore-errors` prevents minor OSM problems from stopping the
conversion, but does not guarantee that the resulting network is free of
topological or traffic-rule errors. Warnings from `netconvert` should be
reviewed before using the network for a calibrated simulation.

## Step 3 — Generate the polygon layer

### Inputs

```text
cda_la_rochelle.osm
cda_la_rochelle.net.xml
```

### Equivalent command

```bat
polyconvert --osm-files cda_la_rochelle.osm --net-file cda_la_rochelle.net.xml -o cda_la_rochelle.poly.xml
```

### Output

`cda_la_rochelle.poly.xml` contains polygons and points of interest derived
from OpenStreetMap and projected consistently with the SUMO network. It is
mainly used to display buildings, land use, and other geographic objects in
SUMO-GUI. It does not define the road graph itself.

## Generated files

The sizes below correspond to the documented reference run:

| File | Role | Reference size | Tracked by Git |
|---|---|---:|---|
| `input/poitou-charentes-260317.osm.pbf` | Regional OSM source | 228,212,202 bytes | No |
| `cda_la_rochelle.osm` | OSM study-area extract | 818,386,071 bytes | No |
| `cda_la_rochelle.net.xml` | SUMO road and pedestrian network | 1,038,156,324 bytes | No |
| `cda_la_rochelle.poly.xml` | Display polygons and geographic objects | 193,530,547 bytes | No |
| `network.ipynb` | Reproducible construction code | — | Yes |

## Running the notebook in VS Code

1. Open `network.ipynb` from `2-SUMO/1-network/`.
2. Select a Python environment in which Jupyter is available.
3. Verify that Osmium, `netconvert`, and `polyconvert` are accessible.
4. Check that the filename in `INPUT_FILE` matches the downloaded input.
5. Restart the kernel and select **Run All**.
6. Confirm that every cell ends with an `[OK]` message.

The notebook uses relative paths and must be run with `1-network/` as its
working directory.

## Reproducibility

The direct Geofabrik link contains `latest` and therefore changes over time.
Two users downloading it on different dates may generate different networks.
For a reproducible scenario, retain:

- the original `.osm.pbf` file and its SHA-256 checksum;
- the bounding box;
- `network.ipynb`;
- the SUMO and Osmium versions;
- the warnings produced by `netconvert`;
- the generated network used by subsequent simulations.

Changing the OSM snapshot, bounding box, SUMO version, or conversion options
requires regenerating all three output files.

## Git policy

The `.gitignore` rules keep only:

- `README.md`;
- `network.ipynb`;
- the documented `input/` folder;
- the `.gitignore` files.

The PBF input and the three generated files are excluded. A user who clones
the repository must first follow [`input/README.md`](input/README.md), then run
the notebook to recreate the network.

## Data licence

The source data are created by
[OpenStreetMap contributors](https://www.openstreetmap.org/) and distributed
by Geofabrik under the
[Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Generated network products must retain the required OpenStreetMap attribution
and comply with the applicable licence conditions.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Construction du réseau SUMO de La Rochelle

Ce dossier contient le workflow reproductible utilisé pour construire le
réseau routier et piéton SUMO du cas d'étude de La Rochelle à partir des
données OpenStreetMap.

Le traitement est implémenté dans `network.ipynb`. L'extrait régional
OpenStreetMap et tous les fichiers réseau générés restent locaux en raison de
leur taille. Seuls le notebook, la documentation et les règles d'exclusion Git
sont conservés dans le dépôt.

## Contenu du dossier

```text
1-network/
├── README.md
├── network.ipynb
├── input/
│   ├── README.md
│   └── poitou-charentes-260317.osm.pbf  # local, non suivi par Git
├── cda_la_rochelle.osm                  # généré, non suivi par Git
├── cda_la_rochelle.net.xml              # généré, non suivi par Git
└── cda_la_rochelle.poly.xml             # généré, non suivi par Git
```

## Données d'entrée

Le notebook utilise l'extrait régional OpenStreetMap du Poitou-Charentes fourni
par Geofabrik :

- [page de téléchargement de la France](https://download.geofabrik.de/europe/france.html) ;
- [page de téléchargement du Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html) ;
- [téléchargement direct du `.osm.pbf`](https://download.geofabrik.de/europe/france/poitou-charentes-latest.osm.pbf).

La procédure de téléchargement, la convention de nommage, l'empreinte du
fichier de référence et les informations de licence sont données dans
[`input/README.md`](input/README.md).

Le notebook lit actuellement :

```text
input/poitou-charentes-260317.osm.pbf
```

## Prérequis

Le réseau de référence a été généré sous Windows avec :

- Python et Jupyter, pour exécuter `network.ipynb` ;
- [Osmium Tool](https://osmcode.org/osmium-tool/), pour extraire le périmètre
  d'étude depuis le fichier régional `.osm.pbf` ;
- [Eclipse SUMO](https://eclipse.dev/sumo/), qui fournit `netconvert` et
  `polyconvert` ;
- SUMO `1.27.1` pour les sorties documentées.

Les commandes suivantes doivent fonctionner depuis l'environnement utilisé par
le notebook :

```bat
osmium --version
netconvert --version
polyconvert --version
```

Si une commande n'est pas reconnue, ajouter le dossier de l'exécutable
correspondant au `PATH` de Windows, puis redémarrer VS Code avant d'exécuter le
notebook.

## Chaîne de traitement

| Construction du réseau |
|:---:|
| **Entrée régionale : `poitou-charentes-260317.osm.pbf`** |
| ↓ `osmium extract` |
| **Extrait du périmètre : `cda_la_rochelle.osm`** |
| ↓ `netconvert` |
| **Réseau SUMO : `cda_la_rochelle.net.xml`** |
| ↓ `polyconvert`, avec l'extrait OSM et le réseau |
| **Polygones d'affichage : `cda_la_rochelle.poly.xml`** |

Les cellules du notebook doivent être exécutées dans l'ordre.

## Étape 1 — Extraction du périmètre avec Osmium

### Entrée

```text
input/poitou-charentes-260317.osm.pbf
```

### Emprise géographique

Le notebook utilise la bounding box suivante, exprimée dans l'ordre
`longitude_min, latitude_min, longitude_max, latitude_max` :

```text
-1.571,45.800,-0.533,46.353
```

### Commande équivalente

```bat
osmium extract -b -1.571,45.800,-0.533,46.353 input\poitou-charentes-260317.osm.pbf -o cda_la_rochelle.osm
```

### Sortie

`cda_la_rochelle.osm` est un extrait OpenStreetMap au format XML contenant les
objets nécessaires pour l'emprise rectangulaire. Osmium peut conserver des
nœuds légèrement situés en dehors de la bounding box lorsqu'ils sont
nécessaires pour préserver des chemins ou relations OSM complets.

La bounding box est une emprise de traitement, et non la limite administrative
exacte de la Communauté d'agglomération de La Rochelle.

## Étape 2 — Conversion de l'extrait OSM en réseau SUMO

### Entrée

```text
cda_la_rochelle.osm
```

### Commande équivalente

```bat
netconvert --osm-files cda_la_rochelle.osm -o cda_la_rochelle.net.xml --sidewalks.guess true --sidewalks.guess.from-permissions true --crossings.guess true --walkingareas true --ignore-errors true --ignore-errors.edge-type true
```

### Principales options

| Option | Rôle |
|---|---|
| `--sidewalks.guess true` | Génère des trottoirs lorsqu'ils peuvent être déduits des informations OSM |
| `--sidewalks.guess.from-permissions true` | Déduit également les trottoirs à partir des permissions des voies |
| `--crossings.guess true` | Génère des passages piétons |
| `--walkingareas true` | Crée des zones de marche piétonnes aux intersections |
| `--ignore-errors true` | Permet à la conversion de continuer malgré des incohérences OSM non bloquantes |
| `--ignore-errors.edge-type true` | Ignore les définitions de types d'arêtes non prises en charge ou incohérentes |

### Sortie

`cda_la_rochelle.net.xml` est le réseau SUMO. Il contient les arêtes, les voies,
les intersections, les connexions, les permissions de circulation et les
infrastructures piétonnes déduites par `netconvert`. Le fichier généré utilise
la projection UTM sélectionnée automatiquement par SUMO pour le territoire.

L'utilisation de `--ignore-errors` empêche des problèmes OSM mineurs de bloquer
la conversion, mais elle ne garantit pas que le réseau obtenu soit exempt
d'erreurs topologiques ou de règles de circulation. Les avertissements de
`netconvert` doivent être examinés avant d'utiliser ce réseau pour une
simulation calibrée.

## Étape 3 — Génération de la couche de polygones

### Entrées

```text
cda_la_rochelle.osm
cda_la_rochelle.net.xml
```

### Commande équivalente

```bat
polyconvert --osm-files cda_la_rochelle.osm --net-file cda_la_rochelle.net.xml -o cda_la_rochelle.poly.xml
```

### Sortie

`cda_la_rochelle.poly.xml` contient les polygones et points d'intérêt dérivés
d'OpenStreetMap et projetés de manière cohérente avec le réseau SUMO. Il sert
principalement à afficher les bâtiments, l'occupation du sol et d'autres
objets géographiques dans SUMO-GUI. Il ne définit pas lui-même le graphe
routier.

## Fichiers générés

Les tailles ci-dessous correspondent à l'exécution de référence documentée :

| Fichier | Rôle | Taille de référence | Suivi par Git |
|---|---|---:|---|
| `input/poitou-charentes-260317.osm.pbf` | Source OSM régionale | 228 212 202 octets | Non |
| `cda_la_rochelle.osm` | Extrait OSM du périmètre d'étude | 818 386 071 octets | Non |
| `cda_la_rochelle.net.xml` | Réseau routier et piéton SUMO | 1 038 156 324 octets | Non |
| `cda_la_rochelle.poly.xml` | Polygones d'affichage et objets géographiques | 193 530 547 octets | Non |
| `network.ipynb` | Code reproductible de construction | — | Oui |

## Exécution du notebook dans VS Code

1. Ouvrir `network.ipynb` depuis `2-SUMO/1-network/`.
2. Sélectionner un environnement Python dans lequel Jupyter est disponible.
3. Vérifier qu'Osmium, `netconvert` et `polyconvert` sont accessibles.
4. Vérifier que le nom défini dans `INPUT_FILE` correspond au fichier
   téléchargé.
5. Redémarrer le noyau et sélectionner **Exécuter tout**.
6. Vérifier que chaque cellule se termine par un message `[OK]`.

Le notebook utilise des chemins relatifs et doit être exécuté avec
`1-network/` comme dossier de travail.

## Reproductibilité

Le lien direct de Geofabrik contient `latest` et évolue donc dans le temps.
Deux utilisateurs qui le téléchargent à des dates différentes peuvent générer
des réseaux différents. Pour rendre un scénario reproductible, conserver :

- le fichier `.osm.pbf` original et son empreinte SHA-256 ;
- la bounding box ;
- `network.ipynb` ;
- les versions de SUMO et d'Osmium ;
- les avertissements produits par `netconvert` ;
- le réseau généré utilisé par les simulations suivantes.

Une modification de l'instantané OSM, de la bounding box, de la version de
SUMO ou des options de conversion impose de régénérer les trois fichiers de
sortie.

## Politique Git

Les règles `.gitignore` conservent uniquement :

- `README.md` ;
- `network.ipynb` ;
- le dossier `input/` documenté ;
- les fichiers `.gitignore`.

L'entrée PBF et les trois fichiers générés sont exclus. Un utilisateur qui
clone le dépôt doit d'abord suivre [`input/README.md`](input/README.md), puis
exécuter le notebook pour reconstruire le réseau.

## Licence des données

Les données sources sont créées par les
[contributeurs OpenStreetMap](https://www.openstreetmap.org/) et distribuées
par Geofabrik sous
[Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Les produits réseau générés doivent conserver l'attribution OpenStreetMap
requise et respecter les conditions de licence applicables.
