<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Filtering Eqasim/MATSim outputs for the Communauté d'Agglomération de La Rochelle

This folder contains the notebook that extracts, from the scenario covering
Charente-Maritime, the population and trips required for the **Communauté
d'Agglomération de La Rochelle (CdA)** case study. Filtering reduces the
volume of data before its conversion and use in SUMO, while preserving the
relationships between persons, households, plans, and activity facilities.

The selection was designed for the **Yélo DETA** research project, which
targets an automated demand-responsive transport service in eight peri-urban
and rural municipalities of the CdA. It retains both the residents directly
concerned by the project and the wider travel demand circulating within the
CdA.

The notebook is tracked on GitHub. The files it produces are reproducible,
sometimes large, and therefore remain local.

## Selection logic

A person is retained if they satisfy at least one of the following two
criteria:

1. their household is located in one of the eight peri-urban and rural
   municipalities targeted by Yélo DETA, whose codes are listed below;
2. all their known activities are located in one of the 28 municipalities of
   the CdA.

The second criterion represents people whose simulated daily trips take place
within the CdA; technically, the notebook implements it by checking that every
known activity of the person is inside the CdA. The final selection is the
union of these two sets.

The eight Yélo DETA municipalities and the codes used by the notebook are:

```text
Bourgneuf (17059), Montroy (17245), Clavette (17109),
La Jarrie (17194), Saint-Médard-d'Aunis (17373),
Saint-Christophe (17315), Croix-Chapeau (17136),
Salles-sur-Mer (17420)
```

The 28 codes of the CdA are defined directly in the notebook so that the study
area remains explicit and reproducible.

## Why two data sources are used

The new MATSim exports provide simulated persons, activities, and plans, but
not all the municipality information required for filtering. The notebook
therefore enriches them with:

- `../17households.csv`, to associate a household with its municipality of
  residence;
- `../17activities.csv`, to associate an activity with its municipality;
- files from `../simulation_output/`, to retrieve the simulation results;
- GeoPackage files at the root of `output/`, when available.

The joins rely on person, household, and activity identifiers. The notebook
reports the number of missing matches so that they can be checked.

## Running in VS Code

Install the `pandas`, `geopandas`, and `zstandard` libraries in the Python
environment, then open `create_output_filtered.ipynb` from this folder. Select
the same Python environment as the project.

Before each complete execution:

1. restart the notebook kernel;
2. use **Run All**;
3. check the displayed summary and make sure that no error occurred.

Restarting the kernel is important: it ensures that the result depends only on
the code saved in the notebook and not on an older function still present in
memory.

The notebook uses relative paths. It must therefore remain in
`output/eqasim_output_filtered/`, alongside the folders and files described
above.

## Tabular outputs

| File | Contents |
|---|---|
| `output_persons_filtered.csv` | Selected persons |
| `output_persons_filtered_with_household_commune.csv` | Selected persons with household municipality |
| `output_activities_filtered.csv` | Activities of selected persons |
| `output_activities_filtered_with_commune.csv` | Activities with reconstructed municipality |
| `output_trips_filtered.csv` | Trips of selected persons |
| `eqasim_pt_filtered.csv` | Selected public transport legs |

## Filtered MATSim outputs

| File | Contents |
|---|---|
| `output_plans_filtered.xml.zst` | Plans of selected persons |
| `output_households_filtered.xml.zst` | Relevant households, containing only selected members |
| `output_facilities_filtered.xml.zst` | Activity facilities referenced by the filtered plans and tables |

These three files are genuinely compressed in Zstandard format. Internal
references are filtered together to prevent a household from referring to an
absent person or a plan from referring to an absent facility.

## Geographic outputs

| File | Contents |
|---|---|
| `17homes_filtered.gpkg` | Home locations of relevant households |
| `17activities_filtered.gpkg` | Activity locations of selected persons |
| `17trips_filtered.gpkg` | Trips of selected persons |
| `17commutes_filtered.gpkg` | Home-to-work or home-to-education trips |

The GeoPackage files originate from layers generated before the simulation,
whereas the `output_*` CSV and XML files describe MATSim outputs. Row counts
may therefore differ slightly between these two groups of files.

## Validation summary

At the end, the notebook displays the number of selected persons and
households, as well as the number of rows written to each table. These values
depend on the sampling rate and MATSim run; they must therefore not be
hard-coded as fixed values in subsequent processing steps.

For the 11% reference run, the validation gives:

| Element | Count |
|---|---:|
| Selected persons | 16,046 |
| Selected households | 9,591 |
| Filtered MATSim activities | 68,346 |
| Filtered MATSim trips | 52,431 |
| Public transport legs | 7,706 |

The joins from this run report 14 unmatched household municipalities and one
unmatched activity municipality. These are quality warnings to monitor, not
execution errors; their number must be reassessed if the inputs change.

Before moving to SUMO, check at least that:

- no expected file was skipped with a `[WARN]` message;
- the three `.xml.zst` files can be decompressed;
- every filtered person has a plan;
- household members and referenced facilities exist in their corresponding
  filtered files.

---

<a id="version-francaise"></a>

> **Langues :** [La version anglaise se trouve en haut de ce document.](#english-version)
> La version française commence ci-dessous.

# Filtrage des sorties Eqasim/MATSim pour la Communauté d'Agglomération de La Rochelle

Ce dossier contient le notebook qui extrait, à partir du scénario couvrant la
Charente-Maritime, la population et les déplacements utiles au cas d'étude de
la **Communauté d'Agglomération de La Rochelle (CdA)**. Le filtrage réduit le
volume des données avant leur conversion et leur utilisation dans SUMO, tout
en conservant les relations entre personnes, ménages, plans et lieux
d'activité.

La sélection a été conçue pour le projet de recherche **Yélo DETA**, qui vise
un service de transport automatisé à la demande dans huit communes
périurbaines et rurales de la CdA. Elle conserve à la fois les habitants
directement concernés par le projet et la demande de mobilité plus large
circulant dans la CdA.

Le notebook est versionné sur GitHub. Les fichiers qu'il produit sont
reproductibles, parfois volumineux, et restent donc locaux.

## Logique de sélection

Une personne est conservée si elle satisfait au moins l'un des deux critères
suivants :

1. son ménage est localisé dans l'une des huit communes périurbaines et rurales
   visées par Yélo DETA, dont les codes sont donnés ci-dessous ;
2. toutes ses activités connues sont situées dans l'une des 28 communes de la
   CdA.

Le second critère représente les personnes dont les déplacements quotidiens
simulés s'effectuent dans la CdA ; techniquement, le notebook vérifie pour cela
que toutes les activités connues de la personne se situent dans la CdA. La
sélection finale est l'union de ces deux ensembles.

Les huit communes de Yélo DETA et les codes utilisés par le notebook sont :

```text
Bourgneuf (17059), Montroy (17245), Clavette (17109),
La Jarrie (17194), Saint-Médard-d'Aunis (17373),
Saint-Christophe (17315), Croix-Chapeau (17136),
Salles-sur-Mer (17420)
```

Les 28 codes de la CdA sont définis directement dans le notebook afin que le
périmètre soit explicite et reproductible.

## Pourquoi deux sources sont utilisées

Les nouveaux exports MATSim fournissent les personnes, activités et plans
simulés, mais pas toutes les informations communales nécessaires au filtrage.
Le notebook les complète donc avec :

- `../17households.csv`, pour rattacher un ménage à sa commune de résidence ;
- `../17activities.csv`, pour rattacher une activité à sa commune ;
- les fichiers de `../simulation_output/`, pour récupérer les résultats de la
  simulation ;
- les GeoPackage présents à la racine de `output/`, lorsqu'ils sont disponibles.

Les jointures reposent sur les identifiants de personne, de ménage et
d'activité. Le notebook signale le nombre de correspondances manquantes afin
qu'elles puissent être contrôlées.

## Exécution dans VS Code

Installer dans l'environnement Python les bibliothèques `pandas`, `geopandas`
et `zstandard`, puis ouvrir `create_output_filtered.ipynb` depuis ce dossier.
Sélectionner le même environnement Python que celui du projet.

Avant chaque exécution complète :

1. redémarrer le noyau du notebook ;
2. utiliser **Exécuter tout** ;
3. vérifier le résumé affiché et l'absence d'erreur.

Le redémarrage du noyau est important : il garantit que le résultat dépend
uniquement du code enregistré dans le notebook et non d'une ancienne fonction
restée en mémoire.

Les chemins du notebook sont relatifs. Il doit donc rester dans
`output/eqasim_output_filtered/`, à côté des dossiers et fichiers décrits
ci-dessus.

## Sorties tabulaires

| Fichier | Contenu |
|---|---|
| `output_persons_filtered.csv` | Personnes sélectionnées |
| `output_persons_filtered_with_household_commune.csv` | Personnes sélectionnées avec commune du ménage |
| `output_activities_filtered.csv` | Activités des personnes sélectionnées |
| `output_activities_filtered_with_commune.csv` | Activités avec commune reconstituée |
| `output_trips_filtered.csv` | Déplacements des personnes sélectionnées |
| `eqasim_pt_filtered.csv` | Étapes de transport collectif sélectionnées |

## Sorties MATSim filtrées

| Fichier | Contenu |
|---|---|
| `output_plans_filtered.xml.zst` | Plans des personnes sélectionnées |
| `output_households_filtered.xml.zst` | Ménages concernés, avec uniquement les membres sélectionnés |
| `output_facilities_filtered.xml.zst` | Lieux d'activité référencés par les plans et tables filtrés |

Ces trois fichiers sont réellement compressés au format Zstandard. Les
références internes sont filtrées ensemble pour éviter qu'un ménage pointe vers
une personne absente ou qu'un plan pointe vers un lieu absent.

## Sorties géographiques

| Fichier | Contenu |
|---|---|
| `17homes_filtered.gpkg` | Domiciles des ménages concernés |
| `17activities_filtered.gpkg` | Lieux d'activité des personnes sélectionnées |
| `17trips_filtered.gpkg` | Déplacements des personnes sélectionnées |
| `17commutes_filtered.gpkg` | Déplacements domicile-travail ou domicile-études |

Les GeoPackage proviennent des couches générées avant la simulation, tandis que
les CSV et XML `output_*` décrivent les sorties MATSim. Le nombre de lignes
peut donc différer légèrement entre ces deux familles de fichiers.

## Résumé de contrôle

À la fin, le notebook affiche le nombre de personnes et de ménages sélectionnés
ainsi que le nombre de lignes écrit dans chaque table. Ces valeurs dépendent du
taux d'échantillonnage et de l'exécution MATSim ; elles ne doivent donc pas être
codées comme des valeurs fixes dans les traitements suivants.

Pour l'exécution de référence à 11 %, le contrôle donne :

| Élément | Nombre |
|---|---:|
| Personnes sélectionnées | 16 046 |
| Ménages sélectionnés | 9 591 |
| Activités MATSim filtrées | 68 346 |
| Déplacements MATSim filtrés | 52 431 |
| Étapes de transport collectif | 7 706 |

Les jointures de cette exécution signalent 14 communes de ménage et une commune
d'activité non retrouvées. Ce sont des avertissements de qualité à surveiller,
pas des erreurs d'exécution ; leur nombre doit être réexaminé si les entrées
changent.

Avant le passage vers SUMO, vérifier au minimum :

- qu'aucun fichier attendu n'a été ignoré avec un message `[WARN]` ;
- que les trois fichiers `.xml.zst` peuvent être décompressés ;
- que chaque personne filtrée possède un plan ;
- que les membres des ménages et les lieux référencés existent dans les
  fichiers filtrés correspondants.
