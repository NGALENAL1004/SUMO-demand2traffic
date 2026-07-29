<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Eqasim and MATSim outputs

This folder gathers the results produced by the Eqasim part of the project,
from the synthetic population to the trajectories simulated by MATSim. The
`17` prefix indicates that the initial scenario covers the
**Charente-Maritime department**. A geographic filtering step then prepares
the subset required for the La Rochelle case study and its transfer to SUMO.

Output files are not tracked on GitHub: they are large and can be regenerated
from the input data and configuration documented in the `data/` and `code/`
folders. Only the README files and the filtering notebook are retained in the
repository.

## Folder organisation

| Location | Contents |
|---|---|
| Root of `output/` | Synthetic population and MATSim scenario prepared by the pipeline |
| [`analysis_population/`](analysis_population/) | Synthetic population quality indicators |
| [`simulation_output/`](simulation_output/) | Raw results of the MATSim run |
| [`eqasim_output_filtered/`](eqasim_output_filtered/) | Geographic subset prepared for the next part of the project |

## Synthetic population tables

The CSV files use a semicolon as the delimiter.

| File | Main contents |
|---|---|
| `17persons.csv` | Synthetic persons and sociodemographic characteristics |
| `17households.csv` | Households, location, income, and number of vehicles |
| `17activities.csv` | Daily activities, purposes, locations, and times |
| `17trips.csv` | Trips between two activities |
| `17legs.csv` | Modal legs composing the trips |
| `17pt_legs.csv` | Details of legs performed by public transport |
| `17vehicles.csv` | Vehicles assigned to households |
| `17vehicle_types.csv` | Vehicle types used in the scenario |

Identifiers link the tables together. For example, `person_id` links a person
to their activities and trips, while `household_id` links a person to their
household.

## Geographic layers

The GeoPackage files can be opened in QGIS.

| File | Represented geometries |
|---|---|
| `17homes.gpkg` | Household home locations |
| `17activities.gpkg` | Activity locations |
| `17trips.gpkg` | Trips |
| `17commutes.gpkg` | Home-to-work or home-to-education trips |

## MATSim scenario files

These compressed XML files constitute the simulation inputs.

| File | Purpose |
|---|---|
| `17config.xml` | MATSim configuration generated for the scenario |
| `17network.xml.gz` | Transport network |
| `17population.xml.gz` | Initial population and mobility plans |
| `17households.xml.gz` | Households and person membership |
| `17facilities.xml.gz` | MATSim activity facilities |
| `17vehicles.xml.gz` | Private vehicles |
| `17transit_schedule.xml.gz` | Public transport schedules and routes |
| `17transit_vehicles.xml.gz` | Public transport vehicles |
| `17run.jar` | Java executable assembled by the pipeline |

The `17meta.json` file retains the information needed to identify a run,
including its sampling rate, random seed, and Eqasim version.

## Documented run

The results present when this README was written correspond to the parameters
recorded in `17meta.json`:

| Parameter | Value |
|---|---|
| Sampling rate | `0.11`, or 11% |
| Mobility survey | `emp` |
| Random seed | `1234` |
| Pipeline version | `1.4.0` |
| `eqasim-france` commit | `6115005e9bfb02cbcdc909c9106b013d3198b577` |

These values describe this reference run. After a new generation,
`17meta.json` remains the authoritative source.

## Regeneration

After installing `eqasim-france` and copying the adaptations described in
`code/README.md`, run the pipeline from the working clone:

```bat
uv run -m synpp config_17.yml
```

The output path is defined by `output_path` in `config_17.yml`. Results may
change when the configuration, input data, random seed, or Eqasim version
changes.

For the role and format of the simulation or filtering outputs, refer to the
README in the corresponding subfolder.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Sorties d'Eqasim et de MATSim

Ce dossier rassemble les résultats produits par la partie Eqasim du projet,
depuis la population synthétique jusqu'aux trajectoires simulées par MATSim.
Le préfixe `17` indique que le scénario initial couvre la
**Charente-Maritime**. Un filtrage géographique prépare ensuite le sous-ensemble
utile au cas d'étude de La Rochelle et à son transfert vers SUMO.

Les fichiers de résultats ne sont pas versionnés sur GitHub : ils sont
volumineux et peuvent être régénérés à partir des données d'entrée et de la
configuration documentées dans les dossiers `data/` et `code/`. Seuls les
README et le notebook de filtrage sont conservés dans le dépôt.

## Organisation du dossier

| Emplacement | Contenu |
|---|---|
| Racine de `output/` | Population synthétique et scénario MATSim préparé par le pipeline |
| [`analysis_population/`](analysis_population/) | Indicateurs de contrôle de la population synthétique |
| [`simulation_output/`](simulation_output/) | Résultats bruts de l'exécution MATSim |
| [`eqasim_output_filtered/`](eqasim_output_filtered/) | Sous-ensemble géographique préparé pour la suite du projet |

## Fichiers tabulaires de la population synthétique

Les fichiers CSV utilisent le point-virgule comme séparateur.

| Fichier | Contenu principal |
|---|---|
| `17persons.csv` | Individus synthétiques et caractéristiques sociodémographiques |
| `17households.csv` | Ménages, localisation, revenu et nombre de véhicules |
| `17activities.csv` | Activités quotidiennes, motifs, lieux et horaires |
| `17trips.csv` | Déplacements entre deux activités |
| `17legs.csv` | Étapes modales composant les déplacements |
| `17pt_legs.csv` | Détails des étapes effectuées en transport collectif |
| `17vehicles.csv` | Véhicules attribués aux ménages |
| `17vehicle_types.csv` | Types de véhicules utilisés dans le scénario |

Les identifiants permettent de relier les tables entre elles. Par exemple,
`person_id` relie une personne à ses activités et déplacements, tandis que
`household_id` relie une personne à son ménage.

## Couches géographiques

Les fichiers GeoPackage peuvent être ouverts dans QGIS.

| Fichier | Géométries représentées |
|---|---|
| `17homes.gpkg` | Domiciles des ménages |
| `17activities.gpkg` | Lieux d'activité |
| `17trips.gpkg` | Déplacements |
| `17commutes.gpkg` | Déplacements domicile-travail ou domicile-études |

## Fichiers du scénario MATSim

Ces fichiers XML compressés constituent les entrées de la simulation.

| Fichier | Rôle |
|---|---|
| `17config.xml` | Configuration MATSim générée pour le scénario |
| `17network.xml.gz` | Réseau de transport |
| `17population.xml.gz` | Population et plans de mobilité initiaux |
| `17households.xml.gz` | Ménages et rattachement des personnes |
| `17facilities.xml.gz` | Lieux d'activité MATSim |
| `17vehicles.xml.gz` | Véhicules privés |
| `17transit_schedule.xml.gz` | Horaires et itinéraires des transports collectifs |
| `17transit_vehicles.xml.gz` | Véhicules de transport collectif |
| `17run.jar` | Exécutable Java assemblé par le pipeline |

Le fichier `17meta.json` conserve les informations permettant d'identifier une
exécution, notamment le taux d'échantillonnage, la graine aléatoire et la
version d'Eqasim utilisée.

## Exécution documentée

Les résultats présents lors de la rédaction de ce README correspondent aux
paramètres enregistrés dans `17meta.json` :

| Paramètre | Valeur |
|---|---|
| Taux d'échantillonnage | `0.11`, soit 11 % |
| Enquête mobilité | `emp` |
| Graine aléatoire | `1234` |
| Version du pipeline | `1.4.0` |
| Commit `eqasim-france` | `6115005e9bfb02cbcdc909c9106b013d3198b577` |

Ces valeurs décrivent cette exécution de référence. Après une nouvelle
génération, `17meta.json` reste la source à consulter.

## Régénération

Après avoir installé `eqasim-france` et copié les adaptations décrites dans
`code/README.md`, lancer le pipeline depuis le clone de travail :

```bat
uv run -m synpp config_17.yml
```

Le chemin de sortie est défini par `output_path` dans `config_17.yml`. Les
résultats peuvent varier si la configuration, les données d'entrée, la graine
aléatoire ou la version d'Eqasim changent.

Pour connaître le rôle et le format des résultats produits par la simulation
ou par le filtrage, consulter le README du sous-dossier correspondant.
