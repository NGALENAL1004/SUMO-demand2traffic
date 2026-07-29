<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Configuration and customised `eqasim-france` files

This folder deliberately does **not contain a complete copy of the
`eqasim-france` source code**. It contains only the case-study configuration
and the upstream files modified for this project.

To run the pipeline:

1. clone the exact `eqasim-france` version;
2. copy the files from this folder into the clone while preserving their
   directory structure;
3. download the data described in [`../data/README.md`](../data/README.md)
   separately;
4. install the dependencies and run SynPP.

## Folder contents

```text
code/
├── README.md
├── config_17.yml
├── matsim/
│   └── simulation/
│       └── full_run.py
└── synthesis/
    └── population/
        └── matched.py
```

The complete code required for execution is retrieved directly from the
official `eqasim-france` repository during installation.

## Upstream version

The customised files were developed and tested with:

| Component | Version or reference |
|---|---|
| `eqasim-france` | commit `6115005e9bfb02cbcdc909c9106b013d3198b577` dated 21 July 2026 |
| Upstream repository | <https://github.com/eqasim-org/eqasim-france> |
| Official documentation | <https://eqasim-org.github.io/eqasim-france/> |
| Python | version 3.13 or later |
| `eqasim-java` | version `2.2.0`, commit `fc85693`, downloaded and compiled automatically |
| Java | version 25 for the `eqasim-java` version used |

Using the complete commit hash instead of the `main` branch prevents a future
repository update from silently changing the results or making the customised
files incompatible.

## Changes made

### Age groups used for matching

File:
[`synthesis/population/matched.py`](synthesis/population/matched.py)

The upstream definition:

```python
AGE_BOUNDARIES = [14, 29, 44, 59, 74, 1000]
```

is replaced with:

```python
AGE_BOUNDARIES = [12, 18, 29, 44, 59, 74, 1000]
```

The matching procedure therefore distinguishes the following groups:

```text
0–12, 13–18, 19–29, 30–44, 45–59, 60–74, 75 years or older
```

This adaptation provides a clearer distinction between children, adolescents,
and adults in the EMP 2019 mobility survey.

### MATSim event format

File:
[`matsim/simulation/full_run.py`](matsim/simulation/full_run.py)

The end-of-simulation check previously looked for:

```text
simulation_output/output_events.xml.gz
```

The recent MATSim version writes the Zstandard-compressed file:

```text
simulation_output/output_events.xml.zst
```

The two file-existence checks in `full_run.py` were therefore changed from
`.xml.gz` to `.xml.zst`. This change does not alter the simulation contents; it
only enables the pipeline to recognise a completed run correctly.

### Case-study configuration

The [`config_17.yml`](config_17.yml) file configures, among other elements:

- Charente-Maritime (`departments: [17]`);
- an 11% population sample;
- EMP 2019 as the mobility survey;
- income assignment with `bhepop2`;
- home locations based on BAN addresses;
- weighted education facilities based on BPE;
- paths to the BAN, BD TOPO, OSM, and GTFS data for the case study;
- scenario generation and execution of the MATSim simulation.

The `../data`, `../cache`, and `../output` paths assume that the working
`eqasim-france` clone is placed directly inside `1-Eqasim/`.

## Reconstructing the working folder on Windows

Run the following commands from the project's `1-Eqasim` folder. The complete
clone is placed in `eqasim-france/`, which remains local and is ignored by Git.

```bat
git config --global core.longpaths true

git clone https://github.com/eqasim-org/eqasim-france.git eqasim-france
cd eqasim-france
git checkout 6115005e9bfb02cbcdc909c9106b013d3198b577
cd ..

copy /Y "code\config_17.yml" "eqasim-france\config_17.yml"
copy /Y "code\matsim\simulation\full_run.py" "eqasim-france\matsim\simulation\full_run.py"
copy /Y "code\synthesis\population\matched.py" "eqasim-france\synthesis\population\matched.py"
```

The following command should then display the two modified files and the added
configuration:

```bat
git -C eqasim-france status --short
```

Expected output:

```text
 M matsim/simulation/full_run.py
 M synthesis/population/matched.py
?? config_17.yml
```

## Installation and execution

Prerequisites:

- Git;
- [`uv`](https://docs.astral.sh/uv/);
- Java 25;
- Maven;
- the data downloaded into `../data`.

From the working clone:

```bat
cd eqasim-france
uv sync
uv run -m synpp config_17.yml
```

The current configuration requests four processes and reserves a maximum Java
heap of 14 GB. The pipeline writes:

- temporary files to `../cache`;
- the synthetic population, MATSim scenario, and results to `../output`.

The `run` block in `config_17.yml` currently contains
`matsim.simulation.full_run`, so a complete execution may take a long time. To
generate only the population, temporarily comment out this stage before
running SynPP.

## Licence and attribution

The `full_run.py` and `matched.py` files are adaptations of files from
`eqasim-france`, which is distributed under the **GNU General Public License,
version 2**. Any redistribution of these files must clearly attribute
`eqasim-org/eqasim-france`, identify the changes made, and include the GPL v2
licence text.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Configuration et fichiers personnalisés d'`eqasim-france`

Ce dossier ne contient volontairement **pas une copie complète du code
source d'`eqasim-france`**. Il contient uniquement la configuration du cas
d'étude et les fichiers amont qui ont été modifiés pour ce projet.

Pour exécuter le pipeline, il faut :

1. cloner la version exacte d'`eqasim-france` ;
2. copier les fichiers de ce dossier dans le clone en conservant leur
   arborescence ;
3. télécharger séparément les données décrites dans
   [`../data/README.md`](../data/README.md) ;
4. installer les dépendances, puis lancer SynPP.

## Contenu du dossier

```text
code/
├── README.md
├── config_17.yml
├── matsim/
│   └── simulation/
│       └── full_run.py
└── synthesis/
    └── population/
        └── matched.py
```

Le code complet nécessaire à l'exécution sera récupéré directement depuis le
dépôt officiel d'`eqasim-france` au cours de l'installation.

## Version amont

Les fichiers personnalisés ont été développés et testés avec :

| Composant | Version ou référence |
|---|---|
| `eqasim-france` | commit `6115005e9bfb02cbcdc909c9106b013d3198b577` du 21 juillet 2026 |
| Dépôt amont | <https://github.com/eqasim-org/eqasim-france> |
| Documentation officielle | <https://eqasim-org.github.io/eqasim-france/> |
| Python | version 3.13 ou ultérieure |
| `eqasim-java` | version `2.2.0`, commit `fc85693`, téléchargée et compilée automatiquement |
| Java | version 25 pour la version d'`eqasim-java` utilisée |

Utiliser le commit complet, plutôt que la branche `main`, évite qu'une mise à
jour ultérieure du dépôt modifie silencieusement les résultats ou rende les
fichiers personnalisés incompatibles.

## Modifications apportées

### Classes d'âge pour le matching

Fichier :
[`synthesis/population/matched.py`](synthesis/population/matched.py)

La définition amont :

```python
AGE_BOUNDARIES = [14, 29, 44, 59, 74, 1000]
```

est remplacée par :

```python
AGE_BOUNDARIES = [12, 18, 29, 44, 59, 74, 1000]
```

Le matching distingue ainsi les classes suivantes :

```text
0–12, 13–18, 19–29, 30–44, 45–59, 60–74, 75 ans ou plus
```

Cette adaptation permet de mieux séparer les enfants, les adolescents et les
adultes dans l'EMP 2019 utilisée comme enquête de mobilité.

### Format des événements MATSim

Fichier :
[`matsim/simulation/full_run.py`](matsim/simulation/full_run.py)

Le contrôle de fin de simulation recherchait auparavant :

```text
simulation_output/output_events.xml.gz
```

La version récente de MATSim produit le fichier compressé avec Zstandard :

```text
simulation_output/output_events.xml.zst
```

Les deux contrôles d'existence de `full_run.py` ont donc été adaptés de
`.xml.gz` vers `.xml.zst`. Cette modification ne change pas le contenu de la
simulation ; elle permet seulement au pipeline de reconnaître correctement une
exécution terminée.

### Configuration du cas d'étude

Le fichier [`config_17.yml`](config_17.yml) configure notamment :

- la Charente-Maritime (`departments: [17]`) ;
- un échantillon de population de 11 % ;
- l'EMP 2019 comme enquête de mobilité ;
- l'affectation des revenus avec `bhepop2` ;
- les domiciles à partir de la BAN ;
- les établissements d'enseignement pondérés à partir de la BPE ;
- les chemins vers les données BAN, BD TOPO, OSM et GTFS du cas d'étude ;
- la génération du scénario et l'exécution de la simulation MATSim.

Les chemins `../data`, `../cache` et `../output` supposent que le clone de
travail d'`eqasim-france` est placé directement dans `1-Eqasim/`.

## Reconstruction du dossier de travail sous Windows

Les commandes suivantes sont à exécuter depuis le dossier `1-Eqasim` du projet.
Le clone complet est placé dans `eqasim-france/`, qui reste local et est ignoré
par Git.

```bat
git config --global core.longpaths true

git clone https://github.com/eqasim-org/eqasim-france.git eqasim-france
cd eqasim-france
git checkout 6115005e9bfb02cbcdc909c9106b013d3198b577
cd ..

copy /Y "code\config_17.yml" "eqasim-france\config_17.yml"
copy /Y "code\matsim\simulation\full_run.py" "eqasim-france\matsim\simulation\full_run.py"
copy /Y "code\synthesis\population\matched.py" "eqasim-france\synthesis\population\matched.py"
```

La commande suivante doit alors afficher les deux fichiers modifiés et la
configuration ajoutée :

```bat
git -C eqasim-france status --short
```

Résultat attendu :

```text
 M matsim/simulation/full_run.py
 M synthesis/population/matched.py
?? config_17.yml
```

## Installation et exécution

Prérequis :

- Git ;
- [`uv`](https://docs.astral.sh/uv/) ;
- Java 25 ;
- Maven ;
- les données téléchargées dans `../data`.

Depuis le clone de travail :

```bat
cd eqasim-france
uv sync
uv run -m synpp config_17.yml
```

La configuration actuelle demande quatre processus et réserve une mémoire Java
maximale de 14 Go. Le pipeline écrit :

- ses fichiers temporaires dans `../cache` ;
- la population synthétique, le scénario MATSim et les résultats dans
  `../output`.

Le bloc `run` de `config_17.yml` contient actuellement
`matsim.simulation.full_run`. Une exécution complète peut donc être longue.
Pour ne générer que la population, il faut commenter temporairement cette étape
avant de lancer SynPP.

## Licence et attribution

Les fichiers `full_run.py` et `matched.py` sont des adaptations de fichiers
issus d'`eqasim-france`, distribué sous la **GNU General Public License,
version 2**. Toute redistribution de ces fichiers doit conserver une
attribution claire à `eqasim-org/eqasim-france`, indiquer les modifications
apportées et inclure le texte de la GPL v2.
