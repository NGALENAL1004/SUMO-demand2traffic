<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# OpenStreetMap input data

This folder receives the regional OpenStreetMap extract used to construct the
SUMO network for the La Rochelle case study.

The `.osm.pbf` file is not distributed in this Git repository. It is too large
for standard GitHub storage and is updated regularly by its provider. Each
user must download it locally.

## Data source

The input comes from
[Geofabrik](https://download.geofabrik.de/europe/france.html), which provides
OpenStreetMap extracts for France and its subregions. The French download page
uses the former regional division and includes a dedicated
[Poitou-Charentes page](https://download.geofabrik.de/europe/france/poitou-charentes.html).

The file required here is:

- [`poitou-charentes-latest.osm.pbf`](https://download.geofabrik.de/europe/france/poitou-charentes-latest.osm.pbf)

The `.osm.pbf` format is the binary OpenStreetMap format used by the Osmium
extraction step. Do not download the shapefile or GeoPackage edition for this
notebook.

## Download procedure

1. Open the [Geofabrik page for France](https://download.geofabrik.de/europe/france.html).
2. In **Sub Regions**, select
   [Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html).
3. Download `poitou-charentes-latest.osm.pbf`.
4. Move the downloaded file into:

   ```text
   2-SUMO/1-network/input/
   ```

5. Either rename the file to the name expected by `network.ipynb`, or update
   the `INPUT_FILE` variable in the notebook.

The reference notebook currently expects:

```python
INPUT_FILE = Path("input/poitou-charentes-260317.osm.pbf")
```

To run the notebook without changing this line:

```bat
ren "poitou-charentes-latest.osm.pbf" "poitou-charentes-260317.osm.pbf"
```

For a new scientific run, it is preferable to replace `260317` with the actual
snapshot date and update `INPUT_FILE` accordingly. Renaming a new download
with an old date would make the provenance ambiguous.

## Reference input

The file used for the documented network generation is:

| Property | Value |
|---|---|
| Local filename | `poitou-charentes-260317.osm.pbf` |
| Size | 228,212,202 bytes, approximately 217.6 MiB |
| SHA-256 | `B9FCC26A1837937DA21E2CC15B2290378F147B54B754499667A782F467C31DDE` |
| Provider | Geofabrik |
| Data project | OpenStreetMap |

The `latest` link does not identify a permanent snapshot: its contents change
as OpenStreetMap is updated. To reproduce a network exactly, retain the
downloaded file locally and record its date, size, and checksum.

The checksum can be calculated in Windows Command Prompt with:

```bat
certutil -hashfile "poitou-charentes-260317.osm.pbf" SHA256
```

## Licence and attribution

The extract is prepared by Geofabrik from data created by
[OpenStreetMap contributors](https://www.openstreetmap.org/). OpenStreetMap
data are made available under the
[Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Any use or redistribution must comply with the applicable licence and
attribution requirements.

## Git exclusion

The `.gitignore` file in this folder excludes all downloaded data while
retaining this README and `.gitignore`. After cloning the repository, the
`input/` folder therefore exists but does not contain the `.osm.pbf` file.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Données d'entrée OpenStreetMap

Ce dossier reçoit l'extrait régional OpenStreetMap utilisé pour construire le
réseau SUMO du cas d'étude de La Rochelle.

Le fichier `.osm.pbf` n'est pas distribué dans ce dépôt Git. Il est trop
volumineux pour un stockage GitHub standard et il est régulièrement mis à jour
par son fournisseur. Chaque utilisateur doit donc le télécharger localement.

## Source des données

La donnée provient de
[Geofabrik](https://download.geofabrik.de/europe/france.html), qui propose des
extraits OpenStreetMap pour la France et ses sous-régions. La page française
utilise l'ancien découpage régional et comprend une page consacrée au
[Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html).

Le fichier nécessaire ici est :

- [`poitou-charentes-latest.osm.pbf`](https://download.geofabrik.de/europe/france/poitou-charentes-latest.osm.pbf)

Le format `.osm.pbf` est le format binaire OpenStreetMap utilisé par l'étape
d'extraction Osmium. Il ne faut pas télécharger la version shapefile ou
GeoPackage pour ce notebook.

## Procédure de téléchargement

1. Ouvrir la [page Geofabrik de la France](https://download.geofabrik.de/europe/france.html).
2. Dans **Sub Regions**, sélectionner
   [Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html).
3. Télécharger `poitou-charentes-latest.osm.pbf`.
4. Déplacer le fichier téléchargé dans :

   ```text
   2-SUMO/1-network/input/
   ```

5. Renommer le fichier selon le nom attendu par `network.ipynb`, ou modifier la
   variable `INPUT_FILE` dans le notebook.

Le notebook de référence attend actuellement :

```python
INPUT_FILE = Path("input/poitou-charentes-260317.osm.pbf")
```

Pour exécuter le notebook sans modifier cette ligne :

```bat
ren "poitou-charentes-latest.osm.pbf" "poitou-charentes-260317.osm.pbf"
```

Pour une nouvelle exécution scientifique, il est préférable de remplacer
`260317` par la date réelle de l'extrait et de mettre `INPUT_FILE` à jour.
Renommer un nouveau téléchargement avec une ancienne date rendrait sa
provenance ambiguë.

## Entrée de référence

Le fichier utilisé pour la génération documentée du réseau est :

| Propriété | Valeur |
|---|---|
| Nom local | `poitou-charentes-260317.osm.pbf` |
| Taille | 228 212 202 octets, soit environ 217,6 Mio |
| SHA-256 | `B9FCC26A1837937DA21E2CC15B2290378F147B54B754499667A782F467C31DDE` |
| Fournisseur | Geofabrik |
| Projet de données | OpenStreetMap |

Le lien `latest` ne désigne pas un instantané permanent : son contenu évolue
avec les mises à jour d'OpenStreetMap. Pour reproduire exactement un réseau,
conserver localement le fichier téléchargé et noter sa date, sa taille et son
empreinte.

L'empreinte peut être calculée dans l'invite de commandes Windows avec :

```bat
certutil -hashfile "poitou-charentes-260317.osm.pbf" SHA256
```

## Licence et attribution

L'extrait est préparé par Geofabrik à partir des données créées par les
[contributeurs OpenStreetMap](https://www.openstreetmap.org/). Les données
OpenStreetMap sont mises à disposition sous
[Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Toute utilisation ou redistribution doit respecter les obligations de licence
et d'attribution applicables.

## Exclusion de Git

Le fichier `.gitignore` de ce dossier exclut toutes les données téléchargées
tout en conservant ce README et `.gitignore`. Après le clonage du dépôt, le
dossier `input/` existe donc, mais ne contient pas le fichier `.osm.pbf`.
