<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Mapping Eqasim activity facilities to the SUMO network

This folder contains the notebook that converts the activity facilities used
by the filtered Eqasim population into SUMO points of interest and maps them
to the road and pedestrian network.

In this context, a POI is an activity anchor used by the travel-demand
conversion. It may represent a home, workplace, education facility, leisure
location, or another activity. It is not necessarily an OpenStreetMap POI.

Only `activity.ipynb`, this README, and `.gitignore` are tracked by Git. All
generated XML and CSV files remain local and can be reproduced by executing
the notebook.

## Folder contents

```text
2-POI's/
├── README.md
├── activity.ipynb
├── activities_poi_lonlat.add.xml
├── facilities2sumo_multimode.csv
└── facilities2sumo_pedestrian_candidates.csv
```

The three files below the notebook are generated outputs and are not tracked
by Git.

## Required inputs

The notebook depends on both the filtered Eqasim outputs and the SUMO network.

| Input | Expected location | Purpose |
|---|---|---|
| `output_plans_filtered.xml.zst` | `../eqasim_output_filtered/` | Identifies the facilities referenced by the selected population plans |
| `output_facilities_filtered.xml.zst` | `../eqasim_output_filtered/` | Provides facility identifiers, activity types, and Lambert-93 coordinates |
| `cda_la_rochelle.net.xml` | `../1-network/` | Provides SUMO edges, lanes, permissions, geometry, and coordinate conversion |

The two Eqasim files originate from:

```text
1-Eqasim/output/eqasim_output_filtered/
```

They must be made available in:

```text
2-SUMO/eqasim_output_filtered/
```

The network must first be generated with
[`../1-network/network.ipynb`](../1-network/network.ipynb), following the
instructions in [`../1-network/README.md`](../1-network/README.md).

## Prerequisites

The notebook requires:

- Python and Jupyter;
- `pandas`;
- `pyproj`;
- `zstandard`;
- Eclipse SUMO and its Python library `sumolib`;
- a correctly defined `SUMO_HOME` environment variable.

An example configuration for Windows is:

```bat
setx SUMO_HOME "C:\Program Files\Eclipse\Sumo"
```

Adapt the path to the local SUMO installation, then restart VS Code. The
following folder must exist:

```text
%SUMO_HOME%\tools
```

The reference network and mappings were produced with SUMO `1.27.1`.

## Processing chain

| Activity-facility processing |
|:---:|
| **Filtered MATSim plans and facilities** |
| ↓ |
| **SUMO POIs in longitude/latitude** |
| ↓ |
| **Primary pedestrian and passenger network mappings** |
| ↓ |
| **Alternative pedestrian edge candidates** |

The notebook cells must be executed in order.

## Step 1 — Create SUMO POIs

### Inputs

```text
../eqasim_output_filtered/output_plans_filtered.xml.zst
../eqasim_output_filtered/output_facilities_filtered.xml.zst
```

The notebook first reads all facility identifiers referenced by the filtered
MATSim plans. It then streams through the filtered facilities and retains only
those identifiers.

MATSim coordinates are expressed in Lambert-93 (`EPSG:2154`). They are
converted to WGS84 longitude and latitude (`EPSG:4326`) with `pyproj`.

### Output

```text
activities_poi_lonlat.add.xml
```

This is a SUMO additional file with the following structure:

```xml
<additional>
    <poi id="home_1" lon="-1.000000" lat="46.000000" type="home"/>
</additional>
```

Each `<poi>` contains:

- the MATSim facility identifier;
- its longitude and latitude;
- its first declared activity type.

The reference output contains 15,632 POIs:

| Activity type | POIs |
|---|---:|
| `home` | 9,578 |
| `other` | 2,827 |
| `work` | 1,813 |
| `leisure` | 1,214 |
| `education` | 200 |

## Step 2 — Map every POI to the SUMO network

### Inputs

```text
activities_poi_lonlat.add.xml
../1-network/cda_la_rochelle.net.xml
```

The POI coordinates are converted from longitude and latitude to the internal
SUMO network coordinates. Each POI is then mapped independently for two SUMO
vehicle classes:

- `pedestrian`;
- `passenger`.

The search starts within 20 metres and doubles the radius until a valid lane
is found or the mode-specific maximum is reached:

| Mode | Maximum radius | Minimum edge length | Connectivity depths tested |
|---|---:|---:|---|
| `passenger` | 4,000 m | 5 m | 2, 1, then 0 |
| `pedestrian` | 8,000 m | 1 m | 1, then 0 |

Edges whose function is `internal`, `crossing`, or `walkingarea` are excluded
as activity endpoints. The pedestrian connectivity test accepts a valid
incoming or outgoing continuation, whereas the passenger test requires both
when a strict depth is used.

### Output

```text
facilities2sumo_multimode.csv
```

This comma-separated CSV contains one row per POI and mode. Its main columns
are:

| Column | Meaning |
|---|---|
| `poi_id`, `poi_type` | Facility identifier and activity type |
| `lat`, `lon`, `x`, `y` | Geographic and SUMO coordinates |
| `mode` | `pedestrian` or `passenger` |
| `edge_id`, `lane_id`, `pos` | Selected SUMO edge, lane, and longitudinal position |
| `dist_to_edge` | Distance between the facility and selected edge |
| `mapping_quality` | `strict` or relaxed `loose` mapping |
| `depth_used` | Connectivity depth that produced the result |
| `status`, `error_reason` | Mapping result and diagnostic message |

The reference output contains 31,264 rows:

| Mode | Mapped | Failed |
|---|---:|---:|
| `pedestrian` | 15,614 | 18 |
| `passenger` | 15,610 | 22 |

Among the mapped pedestrian rows, 15,612 are `strict` and two are `loose`.
All 15,610 mapped passenger rows are `strict`.

## Step 3 — Generate pedestrian endpoint candidates

### Inputs

```text
facilities2sumo_multimode.csv
../1-network/cda_la_rochelle.net.xml
```

This stage provides several possible pedestrian network anchors for each POI.
It preserves the primary pedestrian mapping as candidate rank `0`, when
available, then searches for nearby alternatives.

The main settings are:

| Parameter | Value |
|---|---:|
| Maximum candidates per POI | 8 |
| Initial search radius | 20 m |
| Maximum search radius | 800 m |
| Radius multiplier | 2 |
| Minimum edge length | 1 m |

Internal edges, crossings, and walking areas are excluded as final activity
endpoints, although SUMO may still use them within a walking route.

### Output

```text
facilities2sumo_pedestrian_candidates.csv
```

This semicolon-separated CSV contains:

- the POI type and coordinates;
- `candidate_rank`;
- candidate edge, lane, and position;
- distance to the lane;
- `source`, which is `primary`, `nearby`, or `failed`;
- edge function and length;
- mapping status and error reason.

The reference output contains 124,851 rows for 15,632 POIs:

| Result | Count |
|---|---:|
| POIs with at least one candidate | 15,614 |
| POIs with no pedestrian candidate | 18 |
| Rows from the primary mapping | 15,614 |
| Rows from nearby candidates | 109,219 |
| Failed rows | 18 |

Most successfully mapped POIs have eight candidate rows.

## Running the notebook in VS Code

1. Generate `cda_la_rochelle.net.xml` in `../1-network/`.
2. Place the two filtered Eqasim XML files in
   `../eqasim_output_filtered/`.
3. Open `activity.ipynb`.
4. Select the project Python environment.
5. verify that `SUMO_HOME` is available in the notebook environment.
6. Restart the Jupyter kernel and select **Run All**.
7. Review every warning and the final counts.

The notebook uses relative paths and must be run from `2-SUMO/2-POI's/`.

## Quality checks

Before using the mappings to generate SUMO trips:

- inspect all rows with `status == "failed"`;
- inspect `loose` mappings separately;
- check large `dist_to_edge` values;
- confirm that pedestrian and passenger endpoints are compatible with their
  intended modes;
- do not assume that the geographically nearest edge is necessarily the best
  access point.

The mapping is a geometric and connectivity-based preprocessing step. It does
not replace a visual inspection of the network or validation of access
conditions around important facilities.

## Git policy

The `.gitignore` file retains only:

- `README.md`;
- `activity.ipynb`;
- `.gitignore`.

The three generated files are excluded. After cloning the repository, you
must provide the required Eqasim outputs and SUMO network, then run the
notebook to reproduce the POI mappings.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Rattachement des lieux d'activité Eqasim au réseau SUMO

Ce dossier contient le notebook qui transforme les lieux d'activité utilisés
par la population Eqasim filtrée en points d'intérêt SUMO, puis les rattache au
réseau routier et piéton.

Dans ce contexte, un POI est un point d'ancrage d'activité utilisé pour
convertir la demande de déplacement. Il peut représenter un domicile, un lieu
de travail, un établissement d'enseignement, un lieu de loisir ou une autre
activité. Il ne s'agit pas nécessairement d'un POI OpenStreetMap.

Seuls `activity.ipynb`, ce README et `.gitignore` sont suivis par Git. Tous les
fichiers XML et CSV générés restent locaux et peuvent être reproduits en
exécutant le notebook.

## Contenu du dossier

```text
2-POI's/
├── README.md
├── activity.ipynb
├── activities_poi_lonlat.add.xml
├── facilities2sumo_multimode.csv
└── facilities2sumo_pedestrian_candidates.csv
```

Les trois fichiers situés sous le notebook sont des sorties générées et ne sont
pas suivis par Git.

## Entrées nécessaires

Le notebook dépend à la fois des sorties Eqasim filtrées et du réseau SUMO.

| Entrée | Emplacement attendu | Rôle |
|---|---|---|
| `output_plans_filtered.xml.zst` | `../eqasim_output_filtered/` | Identifie les lieux référencés par les plans de la population sélectionnée |
| `output_facilities_filtered.xml.zst` | `../eqasim_output_filtered/` | Fournit les identifiants, types d'activité et coordonnées Lambert-93 des lieux |
| `cda_la_rochelle.net.xml` | `../1-network/` | Fournit les arêtes, voies, permissions, géométries et conversions de coordonnées SUMO |

Les deux fichiers Eqasim proviennent de :

```text
1-Eqasim/output/eqasim_output_filtered/
```

Ils doivent être mis à disposition dans :

```text
2-SUMO/eqasim_output_filtered/
```

Le réseau doit d'abord être généré avec
[`../1-network/network.ipynb`](../1-network/network.ipynb), en suivant les
instructions de [`../1-network/README.md`](../1-network/README.md).

## Prérequis

Le notebook nécessite :

- Python et Jupyter ;
- `pandas` ;
- `pyproj` ;
- `zstandard` ;
- Eclipse SUMO et sa bibliothèque Python `sumolib` ;
- une variable d'environnement `SUMO_HOME` correctement définie.

Exemple de configuration sous Windows :

```bat
setx SUMO_HOME "C:\Program Files\Eclipse\Sumo"
```

Adapter ce chemin à l'installation locale de SUMO, puis redémarrer VS Code. Le
dossier suivant doit exister :

```text
%SUMO_HOME%\tools
```

Le réseau et les rattachements de référence ont été produits avec SUMO
`1.27.1`.

## Chaîne de traitement

| Traitement des lieux d'activité |
|:---:|
| **Plans et facilities MATSim filtrés** |
| ↓ |
| **POI SUMO en longitude et latitude** |
| ↓ |
| **Rattachements principaux piéton et voiture particulière** |
| ↓ |
| **Candidats alternatifs d'arêtes piétonnes** |

Les cellules du notebook doivent être exécutées dans l'ordre.

## Étape 1 — Création des POI SUMO

### Entrées

```text
../eqasim_output_filtered/output_plans_filtered.xml.zst
../eqasim_output_filtered/output_facilities_filtered.xml.zst
```

Le notebook lit d'abord tous les identifiants de facilities référencés par les
plans MATSim filtrés. Il parcourt ensuite les facilities filtrées et ne
conserve que ces identifiants.

Les coordonnées MATSim sont exprimées en Lambert-93 (`EPSG:2154`). Elles sont
converties en longitude et latitude WGS84 (`EPSG:4326`) avec `pyproj`.

### Sortie

```text
activities_poi_lonlat.add.xml
```

Il s'agit d'un fichier additionnel SUMO possédant la structure suivante :

```xml
<additional>
    <poi id="home_1" lon="-1.000000" lat="46.000000" type="home"/>
</additional>
```

Chaque élément `<poi>` contient :

- l'identifiant de la facility MATSim ;
- sa longitude et sa latitude ;
- son premier type d'activité déclaré.

La sortie de référence contient 15 632 POI :

| Type d'activité | POI |
|---|---:|
| `home` | 9 578 |
| `other` | 2 827 |
| `work` | 1 813 |
| `leisure` | 1 214 |
| `education` | 200 |

## Étape 2 — Rattachement de chaque POI au réseau SUMO

### Entrées

```text
activities_poi_lonlat.add.xml
../1-network/cda_la_rochelle.net.xml
```

Les coordonnées des POI sont converties de la longitude et latitude vers les
coordonnées internes du réseau SUMO. Chaque POI est ensuite rattaché
indépendamment pour deux classes de véhicules SUMO :

- `pedestrian` ;
- `passenger`.

La recherche commence dans un rayon de 20 mètres, puis double le rayon jusqu'à
trouver une voie valide ou atteindre le maximum propre au mode :

| Mode | Rayon maximal | Longueur minimale de l'arête | Profondeurs de connectivité testées |
|---|---:|---:|---|
| `passenger` | 4 000 m | 5 m | 2, 1, puis 0 |
| `pedestrian` | 8 000 m | 1 m | 1, puis 0 |

Les arêtes dont la fonction est `internal`, `crossing` ou `walkingarea` sont
exclues comme points terminaux d'activité. Le contrôle piéton accepte une
continuation entrante ou sortante valide, tandis que le contrôle voiture exige
les deux lorsqu'une profondeur stricte est utilisée.

### Sortie

```text
facilities2sumo_multimode.csv
```

Ce CSV séparé par des virgules contient une ligne par POI et par mode. Ses
principales colonnes sont :

| Colonne | Signification |
|---|---|
| `poi_id`, `poi_type` | Identifiant du lieu et type d'activité |
| `lat`, `lon`, `x`, `y` | Coordonnées géographiques et SUMO |
| `mode` | `pedestrian` ou `passenger` |
| `edge_id`, `lane_id`, `pos` | Arête, voie et position longitudinale SUMO retenues |
| `dist_to_edge` | Distance entre le lieu et l'arête sélectionnée |
| `mapping_quality` | Rattachement `strict` ou relâché `loose` |
| `depth_used` | Profondeur de connectivité ayant produit le résultat |
| `status`, `error_reason` | Résultat du rattachement et message de diagnostic |

La sortie de référence contient 31 264 lignes :

| Mode | Rattachés | Échecs |
|---|---:|---:|
| `pedestrian` | 15 614 | 18 |
| `passenger` | 15 610 | 22 |

Parmi les lignes piétonnes rattachées, 15 612 sont `strict` et deux sont
`loose`. Les 15 610 lignes voiture rattachées sont toutes `strict`.

## Étape 3 — Génération des candidats piétons

### Entrées

```text
facilities2sumo_multimode.csv
../1-network/cda_la_rochelle.net.xml
```

Cette étape fournit plusieurs points d'ancrage possibles sur le réseau piéton
pour chaque POI. Elle conserve le rattachement piéton principal au rang `0`,
lorsqu'il existe, puis recherche des solutions alternatives à proximité.

Les principaux paramètres sont :

| Paramètre | Valeur |
|---|---:|
| Nombre maximal de candidats par POI | 8 |
| Rayon initial | 20 m |
| Rayon maximal | 800 m |
| Multiplicateur du rayon | 2 |
| Longueur minimale de l'arête | 1 m |

Les arêtes internes, passages piétons et zones de marche sont exclus comme
points terminaux d'activité, même si SUMO peut les emprunter au sein d'un
itinéraire piéton.

### Sortie

```text
facilities2sumo_pedestrian_candidates.csv
```

Ce CSV séparé par des points-virgules contient :

- le type et les coordonnées du POI ;
- `candidate_rank` ;
- l'arête, la voie et la position candidates ;
- la distance à la voie ;
- `source`, qui vaut `primary`, `nearby` ou `failed` ;
- la fonction et la longueur de l'arête ;
- le statut et la cause d'échec.

La sortie de référence contient 124 851 lignes pour 15 632 POI :

| Résultat | Nombre |
|---|---:|
| POI possédant au moins un candidat | 15 614 |
| POI sans candidat piéton | 18 |
| Lignes issues du rattachement principal | 15 614 |
| Lignes issues des candidats voisins | 109 219 |
| Lignes en échec | 18 |

La majorité des POI correctement rattachés possèdent huit lignes candidates.

## Exécution du notebook dans VS Code

1. Générer `cda_la_rochelle.net.xml` dans `../1-network/`.
2. Placer les deux XML Eqasim filtrés dans
   `../eqasim_output_filtered/`.
3. Ouvrir `activity.ipynb`.
4. Sélectionner l'environnement Python du projet.
5. Vérifier que `SUMO_HOME` est disponible dans l'environnement du notebook.
6. Redémarrer le noyau Jupyter et sélectionner **Exécuter tout**.
7. Examiner chaque avertissement et les décomptes finaux.

Le notebook utilise des chemins relatifs et doit être exécuté depuis
`2-SUMO/2-POI's/`.

## Contrôles de qualité

Avant d'utiliser ces rattachements pour générer les déplacements SUMO :

- examiner toutes les lignes dont `status == "failed"` ;
- examiner séparément les rattachements `loose` ;
- contrôler les grandes valeurs de `dist_to_edge` ;
- vérifier que les points terminaux piétons et voiture sont compatibles avec
  les modes concernés ;
- ne pas supposer que l'arête géographiquement la plus proche constitue
  nécessairement le meilleur accès.

Le rattachement est un prétraitement géométrique fondé sur la connectivité. Il
ne remplace pas une inspection visuelle du réseau ni une validation des
conditions d'accès autour des lieux importants.

## Politique Git

Le fichier `.gitignore` conserve uniquement :

- `README.md` ;
- `activity.ipynb` ;
- `.gitignore`.

Les trois fichiers générés sont exclus. Après le clonage du dépôt, vous devrez fournir les sorties Eqasim et le réseau SUMO nécessaires,
puis exécuter le notebook pour reproduire les rattachements.
