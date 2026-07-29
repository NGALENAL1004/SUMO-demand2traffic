<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Filtered Eqasim inputs used by SUMO

This folder is a local staging area between the Eqasim and SUMO parts of the
workflow. It contains the population subset and supporting tables generated
by:

```text
1-Eqasim/output/eqasim_output_filtered/
```

The files are copied or linked here so that the SUMO notebooks can use stable
relative paths. They are generated data and are not tracked by Git.

## Expected files

| File | Used by | Purpose |
|---|---|---|
| `output_plans_filtered.xml.zst` | steps 2 and 4 | Filtered MATSim/Eqasim plans |
| `output_facilities_filtered.xml.zst` | step 2 | Facilities referenced by the filtered plans |
| `eqasim_pt_filtered.csv` | step 4 | Eqasim public-transport legs and GTFS identifiers |
| other filtered CSV/XML files | quality control | Population, household, activity, and trip diagnostics |

The authoritative description of these outputs is available in:

```text
1-Eqasim/output/eqasim_output_filtered/README.md
```

## Preparation

After completing the Eqasim filtering stage, copy the complete contents of
`1-Eqasim/output/eqasim_output_filtered/` into this folder. Keep the filenames
unchanged because the notebooks use them directly.

Before running the SUMO conversion, verify that the `.zst` files are genuine
Zstandard streams and not gzip files renamed with a `.zst` extension.

## Git policy

Only this README and `.gitignore` are retained. All staged Eqasim files must
be regenerated or copied from the Eqasim part of the project.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Entrées Eqasim filtrées utilisées par SUMO

Ce dossier sert de zone de transit locale entre les parties Eqasim et SUMO de
la chaîne. Il contient le sous-ensemble de population et les tables associées
produits dans :

```text
1-Eqasim/output/eqasim_output_filtered/
```

Les fichiers sont copiés ou liés ici afin que les notebooks SUMO utilisent
des chemins relatifs stables. Ce sont des données générées qui ne sont pas
suivies par Git.

## Fichiers attendus

| Fichier | Utilisé par | Rôle |
|---|---|---|
| `output_plans_filtered.xml.zst` | étapes 2 et 4 | Plans MATSim/Eqasim filtrés |
| `output_facilities_filtered.xml.zst` | étape 2 | Équipements référencés par les plans filtrés |
| `eqasim_pt_filtered.csv` | étape 4 | Étapes en transport collectif Eqasim et identifiants GTFS |
| autres CSV/XML filtrés | contrôle qualité | Diagnostics de population, ménages, activités et déplacements |

La description de référence de ces sorties se trouve dans :

```text
1-Eqasim/output/eqasim_output_filtered/README.md
```

## Préparation

Après le filtrage Eqasim, copier tout le contenu de
`1-Eqasim/output/eqasim_output_filtered/` dans ce dossier. Conserver les noms
de fichiers, car les notebooks les utilisent directement.

Avant la conversion SUMO, vérifier que les fichiers `.zst` sont de véritables
flux Zstandard et non des fichiers gzip simplement renommés.

## Politique Git

Seuls ce README et `.gitignore` sont conservés. Tous les fichiers Eqasim
placés ici doivent être régénérés ou recopiés depuis la partie Eqasim du
projet.
