<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Eqasim input data — Communauté d'Agglomération de La Rochelle case study

This folder documents the raw data required for the **Eqasim–MATSim** part of
the SUMO demand-generation workflow.

> **Raw data are not distributed in this Git repository.**
> After cloning the project, each user must download the datasets from their
> official sources and recreate the local folder structure described below.

The general method can be transferred to other French territories, but the
files and data vintages specified in this guide correspond to its application
to the **Communauté d'Agglomération de La Rochelle (CdA) and its surrounding
area**.

The synthetic population is first built at the scale of the
**Charente-Maritime department (department 17)**. The area required for the
SUMO scenario is filtered in downstream steps according to the needs of the
**Yélo DETA** project. This preserves complete daily mobility chains before
combining residents of the eight project municipalities with people whose
simulated daily travel takes place within the CdA.

This folder corresponds to the following parameter in
[`config_17.yml`](../code/config_17.yml):

```yaml
data_path: ../data
```

After downloading them, archives must be kept in their original format. Unless
otherwise specified, they should not be extracted manually: the Eqasim
pipeline reads them and selects the configured territory.

## Local folder structure

```text
data/
├── ban_17/          # addresses in department 17
├── bdtopo_17/       # buildings and topographic features in department 17
├── bpe_2025/        # facilities and services
├── codes_2024/      # IRIS geographic reference tables
├── emp_2019/        # national mobility survey
├── filosofi_2021/   # income distributions
├── gtfs_17/         # Yélo public transport schedules
├── iris_2024/       # IRIS boundaries
├── osm_17/          # OpenStreetMap network
├── rp_2022/         # census and home-to-work/education flows
└── sirene/          # companies and establishments
```

With the data editions used for this case study, the complete folder
represents approximately 5 GB. This volume may change with future updates,
particularly for the SIRENE files.

## Scope and positioning

The upstream code comes from
[`eqasim-france`](https://github.com/eqasim-org/eqasim-france), a pipeline
designed to build synthetic populations for multiple French territories. The
present repository is not yet a generic ready-to-use tool for any city: its
configuration, territorial data, and some filtering steps are adapted to the
Communauté d'Agglomération de La Rochelle case study.

To transfer the workflow elsewhere, at minimum replace the departmental data,
OSM network, GTFS supply, and territorial parameters, then adapt the specific
filters and mappings used before importing the demand into SUMO.

## Expected files and role of each dataset

| Folder | File(s) used | Coverage | Role in the pipeline |
|---|---|---|---|
| `rp_2022` | `RP2022_indcvi.parquet` | France | Census microdata used to construct synthetic persons and households. |
| `rp_2022` | `base-ic-evol-struct-pop-2022_csv.zip` | France excluding Mayotte | Population totals at municipality and IRIS levels. |
| `rp_2022` | `RP2022_mobpro.parquet` | France | Flows between municipality of residence and municipality of work. |
| `rp_2022` | `RP2022_mobsco.parquet` | France | Flows between municipality of residence and municipality of education. |
| `filosofi_2021` | `indic-struct-distrib-revenu-2021-COMMUNES_XLSX.zip`, `indic-struct-distrib-revenu-2021-SUPRA_XLSX.zip` | France | Income distributions used here by the `bhepop2` assignment method. |
| `bpe_2025` | `BPE25.parquet` | France | Locations and capacities of facilities, in particular educational establishments. |
| `emp_2019` | `emp_2019_donnees_individuelles_anonymisees_novembre2024.zip` | France | Mobility survey used as the HTS to assign activity and trip schedules. |
| `iris_2024` | `CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2024-01-01.7z` | Metropolitan France | Geometries of IRIS zones in Lambert-93. |
| `codes_2024` | `reference_IRIS_geo2024.zip` | France | Mappings between IRIS zones, municipalities, departments, and regions. |
| `sirene` | `stock-stockunitelegale-parquet.parquet`, `stock-stocketablissement-parquet.parquet`, `geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet` | France | Locations and characteristics of companies and establishments used for workplaces. |
| `bdtopo_17` | `BDTOPO_3-3_TOUSTHEMES_GPKG_LAMB93_D017_2024-03-15.7z` | Charente-Maritime | Buildings and topographic features used for the spatial location of activities. |
| `ban_17` | `adresses-17.csv.gz` | Charente-Maritime | Addresses used to locate homes (`home_location_source: addresses`). |
| `osm_17` | `poitou-charentes-260317.osm.pbf` | Poitou-Charentes | OpenStreetMap extract used to build the MATSim road network. The pipeline cuts it to the scenario area. |
| `gtfs_17` | `ca_la_rochelle-aggregated-gtfs.zip` | Communauté d'Agglomération de La Rochelle | Scheduled public transport supply used to build the MATSim schedule and vehicles. |

## Data provenance

- 2022 population census:
  [geocoded individuals at canton-or-city level](https://www.insee.fr/fr/statistiques/8647104),
  [population at IRIS level](https://www.insee.fr/fr/statistiques/8647014),
  [work mobility](https://www.insee.fr/fr/statistiques/8589904), and
  [education mobility](https://www.insee.fr/fr/statistiques/8589945).
- Filosofi 2021:
  [income structure and distribution](https://www.insee.fr/fr/statistiques/7756855).
- BPE 2025:
  [geolocated facilities](https://www.insee.fr/fr/statistiques/8217525).
- EMP 2019:
  [detailed results and anonymised individual data](https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019).
- IRIS:
  [IRIS boundaries](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_CONTOURS-IRIS)
  and [geographic reference table](https://www.insee.fr/fr/information/7708995).
- SIRENE:
  [company and establishment register](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret)
  and [geolocation of SIRENE establishments](https://www.data.gouv.fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques).
- BD TOPO:
  [IGN catalogue](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-TOPO).
- BAN:
  [departmental exports](https://adresse.data.gouv.fr/data/ban/adresses/latest/csv).
- OpenStreetMap:
  [Geofabrik extracts for Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html).
- GTFS:
  [Yélo urban network](https://transport.data.gouv.fr/datasets/arrets-horaires-et-parcours-theoriques-des-reseaux-naq-lro-nva-m-1).

## Related parameters

Territory-specific paths are defined in
[`config_17.yml`](../code/config_17.yml):

```yaml
regions: []
departments: [17]
sampling_rate: 0.11
hts: emp
filter_hts: false
income_assignation_method: bhepop2
education_location_source: weighted
home_location_source: addresses

data_path: ../data
ban_path: ban_17
bdtopo_path: bdtopo_17
gtfs_path: gtfs_17
osm_path: osm_17
```

The other folders retain the default names expected by `eqasim-france`.

## GTFS time coverage

The local `ca_la_rochelle-aggregated-gtfs.zip` archive contains 24 services:

- validity start: 4 February 2026;
- validity end: 30 June 2026;
- latest calendar exceptions: 12 April 2026.

This archive represents only the Yélo urban network of the Communauté
d'Agglomération de La Rochelle. It does not constitute a complete public transport supply for the
whole Charente-Maritime department: other urban and interurban networks and
rail services are not included in this folder.

## Reproducibility and updates

Several sources are updated regularly, particularly BAN, SIRENE,
OpenStreetMap, and GTFS. To reproduce a scenario exactly:

1. retain the original archives used;
2. do not silently replace a file with a more recent edition;
3. record the download date and the GTFS validity period;
4. retain the configuration file and associated `eqasim-france` version;
5. create a new scenario or clear only the relevant caches when replacing a
   data edition.

SIRENE data may contain information relating to natural persons and must be
handled in accordance with the applicable dissemination conditions and legal
obligations. Raw data must not be redistributed with the project code without
first checking their respective licences.

## Exclusion from Git

The [`.gitignore`](.gitignore) file in this folder ignores all its contents
except this README and the `.gitignore` file itself. This prevents raw data
from being accidentally added to the repository:

```gitignore
*
!.gitignore
!README.md
```

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Données d'entrée eqasim — Communauté d'Agglomération de La Rochelle

Ce dossier documente les données brutes nécessaires à la partie
**eqasim–MATSim** du workflow de génération de demande pour SUMO.

> **Les données brutes ne sont pas distribuées dans ce dépôt Git.**
> Après avoir cloné le projet, chaque utilisateur doit télécharger les jeux de
> données depuis leurs sources officielles et recréer localement l'arborescence
> décrite ci-dessous.

La méthode générale est transférable à d'autres territoires français, mais les
fichiers et millésimes indiqués dans ce guide correspondent à son application
à la **Communauté d'Agglomération de La Rochelle (CdA) et à ses alentours**.

La population synthétique est d'abord construite à l'échelle de la
**Charente-Maritime (département 17)**. Le périmètre utile au scénario SUMO est
filtré dans les étapes situées en aval selon les besoins du projet
**Yélo DETA**. Ce choix conserve les chaînes complètes de mobilité quotidienne
avant de réunir les habitants des huit communes du projet et les personnes
dont les déplacements simulés s'effectuent dans la CdA.

Le dossier correspond au paramètre suivant de
[`config_17.yml`](../code/config_17.yml) :

```yaml
data_path: ../data
```

Après leur téléchargement, les archives doivent être conservées dans leur
format d'origine. Sauf indication contraire, elles ne doivent pas être
extraites manuellement : le pipeline eqasim se charge de les lire et de
sélectionner le territoire configuré.

## Arborescence locale à créer

```text
data/
├── ban_17/          # adresses du département 17
├── bdtopo_17/       # bâtiments et objets topographiques du département 17
├── bpe_2025/        # équipements et services
├── codes_2024/      # correspondances géographiques des IRIS
├── emp_2019/        # enquête nationale sur la mobilité
├── filosofi_2021/   # distributions de revenus
├── gtfs_17/         # horaires du réseau Yélo
├── iris_2024/       # contours des IRIS
├── osm_17/          # réseau OpenStreetMap
├── rp_2022/         # recensement et flux domicile-travail/études
└── sirene/          # entreprises et établissements
```

Avec les éditions utilisées pour ce cas d'étude, l'ensemble représente environ
5 Go. Ce volume peut évoluer lors des mises à jour, en particulier pour les
fichiers SIRENE.

## Positionnement

Le code amont provient d'[`eqasim-france`](https://github.com/eqasim-org/eqasim-france),
un pipeline conçu pour construire des populations synthétiques dans plusieurs
territoires français. Le présent dépôt n'est toutefois pas encore un outil
générique prêt à l'emploi pour n'importe quelle ville : sa configuration, ses
données territoriales et certaines étapes de filtrage sont adaptées au cas de
la Communauté d'Agglomération de La Rochelle.

Pour transposer le workflow, il faut au minimum remplacer les données
départementales, le réseau OSM, l'offre GTFS et les paramètres territoriaux,
puis adapter les filtres et correspondances spécifiques utilisés avant
l'import dans SUMO.

## Fichiers attendus et rôle des données

| Dossier | Fichier(s) utilisé(s) | Couverture | Rôle dans le pipeline |
|---|---|---|---|
| `rp_2022` | `RP2022_indcvi.parquet` | France | Microdonnées du recensement servant à construire les personnes et les ménages synthétiques. |
| `rp_2022` | `base-ic-evol-struct-pop-2022_csv.zip` | France hors Mayotte | Totaux de population aux niveaux communal et IRIS. |
| `rp_2022` | `RP2022_mobpro.parquet` | France | Flux entre commune de résidence et commune de travail. |
| `rp_2022` | `RP2022_mobsco.parquet` | France | Flux entre commune de résidence et commune de scolarisation. |
| `filosofi_2021` | `indic-struct-distrib-revenu-2021-COMMUNES_XLSX.zip`, `indic-struct-distrib-revenu-2021-SUPRA_XLSX.zip` | France | Distribution des revenus utilisée ici par la méthode d'affectation `bhepop2`. |
| `bpe_2025` | `BPE25.parquet` | France | Localisation et capacité des équipements, notamment des établissements d'enseignement. |
| `emp_2019` | `emp_2019_donnees_individuelles_anonymisees_novembre2024.zip` | France | Enquête mobilité utilisée comme HTS pour attribuer les programmes d'activités et de déplacements. |
| `iris_2024` | `CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2024-01-01.7z` | France métropolitaine | Géométries des zones IRIS en Lambert-93. |
| `codes_2024` | `reference_IRIS_geo2024.zip` | France | Correspondances entre IRIS, communes, départements et régions. |
| `sirene` | `stock-stockunitelegale-parquet.parquet`, `stock-stocketablissement-parquet.parquet`, `geoloc-geolocalisationetablissement-sirene-pour-etudes-statistiques-parquet.parquet` | France | Localisation et caractéristiques des entreprises et établissements utilisées pour les lieux de travail. |
| `bdtopo_17` | `BDTOPO_3-3_TOUSTHEMES_GPKG_LAMB93_D017_2024-03-15.7z` | Charente-Maritime | Bâtiments et objets topographiques utilisés pour la localisation spatiale des activités. |
| `ban_17` | `adresses-17.csv.gz` | Charente-Maritime | Adresses utilisées pour localiser les domiciles (`home_location_source: addresses`). |
| `osm_17` | `poitou-charentes-260317.osm.pbf` | Poitou-Charentes | Extrait OpenStreetMap à partir duquel est construit le réseau routier MATSim. Le pipeline le découpe au territoire du scénario. |
| `gtfs_17` | `ca_la_rochelle-aggregated-gtfs.zip` | Communauté d'agglomération de La Rochelle | Offre théorique de transports collectifs utilisée pour construire le calendrier et les véhicules MATSim. |

## Provenance

- Recensement de la population 2022 :
  [individus localisés au canton-ou-ville](https://www.insee.fr/fr/statistiques/8647104),
  [population à l'IRIS](https://www.insee.fr/fr/statistiques/8647014),
  [mobilités professionnelles](https://www.insee.fr/fr/statistiques/8589904) et
  [mobilités scolaires](https://www.insee.fr/fr/statistiques/8589945).
- Filosofi 2021 :
  [structure et distribution des revenus](https://www.insee.fr/fr/statistiques/7756855).
- BPE 2025 :
  [équipements géolocalisés](https://www.insee.fr/fr/statistiques/8217525).
- EMP 2019 :
  [résultats détaillés et données individuelles anonymisées](https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019).
- IRIS :
  [Contours... IRIS](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_CONTOURS-IRIS)
  et [table d'appartenance géographique](https://www.insee.fr/fr/information/7708995).
- SIRENE :
  [base des entreprises et établissements](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret)
  et [géolocalisation des établissements](https://www.data.gouv.fr/datasets/geolocalisation-des-etablissements-du-repertoire-sirene-pour-les-etudes-statistiques).
- BD TOPO :
  [catalogue IGN](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-TOPO).
- BAN :
  [exports départementaux](https://adresse.data.gouv.fr/data/ban/adresses/latest/csv).
- OpenStreetMap :
  [extraits Geofabrik de Poitou-Charentes](https://download.geofabrik.de/europe/france/poitou-charentes.html).
- GTFS :
  [réseau urbain Yélo](https://transport.data.gouv.fr/datasets/arrets-horaires-et-parcours-theoriques-des-reseaux-naq-lro-nva-m-1).

## Paramètres associés

Les chemins spécifiques au territoire sont définis dans
[`config_17.yml`](../code/config_17.yml) :

```yaml
regions: []
departments: [17]
sampling_rate: 0.11
hts: emp
filter_hts: false
income_assignation_method: bhepop2
education_location_source: weighted
home_location_source: addresses

data_path: ../data
ban_path: ban_17
bdtopo_path: bdtopo_17
gtfs_path: gtfs_17
osm_path: osm_17
```

Les autres dossiers conservent les noms attendus par défaut par
`eqasim-france`.

## Périmètre temporel du GTFS

L'archive locale `ca_la_rochelle-aggregated-gtfs.zip` contient 24 services :

- début de validité : 4 février 2026 ;
- fin de validité : 30 juin 2026 ;
- dernières exceptions calendaires : 12 avril 2026.

Cette archive représente uniquement le réseau urbain Yélo de la Communauté
d'agglomération de La Rochelle. Elle ne constitue pas une offre complète de
transport collectif pour l'ensemble de la Charente-Maritime : les autres
réseaux urbains et interurbains ainsi que les services ferroviaires ne sont pas
inclus dans ce dossier.

## Reproductibilité et mises à jour

Plusieurs sources sont mises à jour régulièrement, en particulier BAN, SIRENE,
OpenStreetMap et GTFS. Pour reproduire exactement un scénario :

1. conserver les archives originales utilisées ;
2. ne pas remplacer silencieusement un fichier par une édition plus récente ;
3. noter la date de téléchargement et la période de validité du GTFS ;
4. conserver le fichier de configuration et la version d'`eqasim-france`
   associés aux données ;
5. créer un nouveau scénario ou vider seulement les caches concernés lorsqu'un
   millésime est remplacé.

Les données SIRENE peuvent contenir des informations relatives à des personnes
physiques et doivent être manipulées conformément aux conditions de diffusion
et aux obligations applicables. Les données brutes ne doivent pas être
redistribuées avec le code du projet sans vérification préalable de leurs
licences respectives.

## Exclusion de Git

Le fichier [`.gitignore`](.gitignore) placé dans ce dossier ignore tout son
contenu à l'exception de ce README et du fichier `.gitignore` lui-même. Cette
règle évite d'ajouter accidentellement les données brutes au dépôt :

```gitignore
*
!.gitignore
!README.md
```
