<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Running the SUMO/TraCI simulation

This folder contains the final SUMO configuration and an event-driven TraCI
controller for the Communauté d'Agglomération de La Rochelle scenario.

The controller monitors public transport passengers, detects cases where no
suitable future service can complete the planned ride, and applies a
documented fallback strategy after a confirmation period. SUMO simultaneously
writes mobility, traffic, route, and emission outputs.

## Files retained in the repository

```text
6-simulation/
|-- README.md
|-- sim.sumocfg
|-- edge_outputs_s0.add.xml
|-- viewsettings.xml
|-- traci.ipynb
|-- traci_controller_strategy.py
|-- pt_index_out/
|   `-- README.md
|-- outputs/
|   `-- README.md
`-- traci_strategy_event/
    `-- README.md
```

All generated indexes, logs, traces, XML results, and archives remain local.

## Required inputs

The SUMO configuration uses:

| Input | Expected location | Purpose |
|---|---|---|
| `cda_la_rochelle.net.xml` | `../1-network/` | Road, walking, bicycle, and ferry network |
| `population_all_with_vtypes.rou.xml` | `../5-vehicles/` | Converted population with HBEFA4 vehicle types |
| `activities_poi_lonlat.add.xml` | `../2-POI's/` | Activity POIs for display and reference |
| `vtypes.xml` | `../3-public_transport/` | Public transport vehicle types |
| `gtfs_pt_stops.add.xml` | `../3-public_transport/` | Public transport stops |
| `gtfs_pt_vehicles_colored.add.xml` | `../3-public_transport/` | Scheduled and coloured PT vehicles |
| `facilities2sumo_multimode.csv` | `../2-POI's/` | Destination-edge mapping used by fallback taxis |

Complete steps 1–5 before starting this folder.

## Prerequisites

- Eclipse SUMO `1.27.1` for the documented reference setup;
- Python;
- `sumolib` and `traci` from the same SUMO installation;
- `SUMO_HOME` correctly defined;
- `pandas` is not required by the controller itself, but is used in preceding
  notebooks;
- sufficient disk space: edge/lane traffic and emission outputs can reach
  several gigabytes.

Check from Command Prompt:

```bat
echo %SUMO_HOME%
sumo --version
sumo-gui --version
python -c "import traci, sumolib; print(traci.__file__); print(sumolib.__file__)"
```

The printed Python paths should correspond to the intended SUMO installation.

## SUMO scenario configuration

`sim.sumocfg` defines:

| Setting | Reference value |
|---|---|
| Simulation begin | `0` s |
| Simulation end | `108000` s (30 h) |
| Invalid-route handling | `ignore-route-errors=true` |
| Emission device | enabled for 100% of vehicles |
| GUI settings | `viewsettings.xml` |

The 30-hour horizon allows plans and public transport services extending
beyond midnight to finish.

`edge_outputs_s0.add.xml` adds 60-second aggregation for:

- traffic by edge in `outputs/edgedata_s0.xml`;
- emissions by edge in `outputs/edge_emissions_s0.xml`;
- emissions by lane in `outputs/lane_emissions_s0.xml`.

See the official
[SUMO edge/lane emission output documentation](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html)
for variable definitions and units.

## Notebook execution sequence

Open `traci.ipynb` from this folder and run its cells in order.

### Cell 1 — Build and audit public transport indexes

The first cell reads the final population, PT stops, and coloured PT vehicle
schedule. It creates chronological lookup structures for:

- every vehicle passage by `(stop, line)`;
- every valid future boarding by `(origin stop, destination stop, line)`;
- stop metadata.

It also audits every `<ride>` in the population and writes the files described
in [`pt_index_out/README.md`](pt_index_out/README.md).

Reference checks:

| Measure | Value |
|---|---:|
| Bus stops | 1,036 |
| Duplicate stop IDs | 0 |
| SUMO PT routes | 240 |
| Scheduled PT vehicles | 1,638 |
| Indexed stop-line passages | 39,776 |
| Indexed boarding alternatives | 534,257 |
| Population `<ride>` elements | 7,128 |
| Unmatched audited rides | 0 |

Repeated stop names are normal because several platforms or directions may
share the same public name. Matching and indexing use identifiers, not names
alone.

### Cell 2 — Verify required files

The second cell confirms that the PT index, final population, and SUMO
configuration exist.

### Cell 3 — Start the event-driven controller

The saved production command launches:

```bat
python traci_controller_strategy.py ^
  --sumocfg sim.sumocfg ^
  --population ..\5-vehicles\population_all_with_vtypes.rou.xml ^
  --index-dir pt_index_out ^
  --output-dir traci_strategy_event ^
  --all-persons ^
  --check-every 600 ^
  --monitor-every 60 ^
  --stranded-confirmation-time 600 ^
  --facilities-csv "..\2-POI's\facilities2sumo_multimode.csv" ^
  --sumo-binary sumo-gui ^
  --end 108000 ^
  --print-every-scan 3 ^
  --suppress-sumo-warnings ^
  --seed 1234 ^
  --close-gui-on-end
```

In the Jupyter cell, the same arguments are written using notebook shell
syntax. The command above is the equivalent multiline Command Prompt form.

## Event-driven fallback strategy

For each waiting PT passenger, the controller:

1. identifies the expected remaining ride from the original person plan;
2. queries the static PT index for a future vehicle serving the exact origin,
   destination, and line;
3. if the static timetable has no candidate, searches currently active
   vehicles for a delayed bus that can still serve the passenger;
4. records the first failed observation as a suspicion;
5. confirms the person as stranded only if the condition persists for
   `600` simulated seconds;
6. validates a direct taxi route to the next activity;
7. replaces the obsolete PT chain with a dedicated triggered taxi, a final
   walk if necessary, and the remaining original daily plan;
8. preserves the same person identifier and the original absolute activity
   end times;
9. writes detailed correction, failure, stage, and lifecycle diagnostics.

The controller removes a person only when the configured correction-failure
policy or a crash-guard rule requires it. This intervention changes the
original travel behaviour and must be described when analysing mode shares,
travel times, traffic, or emissions.

Official references:

- [TraCI overview](https://sumo.dlr.de/docs/TraCI/);
- [TraCI from Python](https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html).

## Outputs

Generated files are separated into three groups:

| Folder | Contents |
|---|---|
| [`pt_index_out/`](pt_index_out/README.md) | Reusable PT indexes and pre-simulation ride audit |
| [`outputs/`](outputs/README.md) | Standard SUMO mobility, traffic, route, and emission outputs |
| [`traci_strategy_event/`](traci_strategy_event/README.md) | Controller decisions, corrections, failures, plan traces, and SUMO logs |

Do not interpret a partially written file while SUMO or the controller is
still running. A production run is complete only after the controller exits,
SUMO closes, the XML files have closing root tags, and the error logs have
been reviewed.

## Plain SUMO run versus controlled run

For a visual or syntax check without the fallback controller:

```bat
sumo-gui -c sim.sumocfg
```

For the documented production behaviour, run `traci.ipynb` or call
`traci_controller_strategy.py` with the listed arguments. A plain SUMO run
does not execute the stranded-passenger detection or taxi correction logic
and therefore represents a different experiment.

## Reproducibility and reporting

Record at least:

- SUMO version;
- random seed;
- simulation begin and end;
- GTFS snapshot and selected service date;
- population size after trip conversion;
- vehicle-class distribution and assignment seed;
- controller thresholds and correction policy;
- counts of successful corrections, failed corrections, removals, collisions,
  deadlocks, unfinished trips, and SUMO errors.

## Git policy

The configuration, controller, notebook, view settings, READMEs, and Git
exclusion rules are retained. All generated indexes and simulation outputs
are excluded because they are large and reproducible.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Exécution de la simulation SUMO/TraCI

Ce dossier contient la configuration SUMO finale et un contrôleur TraCI
événementiel pour le scénario de la Communauté d'Agglomération de La Rochelle.

Le contrôleur surveille les passagers des transports collectifs, détecte les
cas où aucun service futur adapté ne peut terminer le trajet prévu et applique
une stratégie de repli documentée après un délai de confirmation. SUMO produit
en parallèle les sorties de mobilité, trafic, itinéraires et émissions.

## Fichiers conservés dans le dépôt

```text
6-simulation/
|-- README.md
|-- sim.sumocfg
|-- edge_outputs_s0.add.xml
|-- viewsettings.xml
|-- traci.ipynb
|-- traci_controller_strategy.py
|-- pt_index_out/
|   `-- README.md
|-- outputs/
|   `-- README.md
`-- traci_strategy_event/
    `-- README.md
```

Tous les index, journaux, traces, résultats XML et archives générés restent
locaux.

## Entrées nécessaires

La configuration SUMO utilise :

| Entrée | Emplacement attendu | Rôle |
|---|---|---|
| `cda_la_rochelle.net.xml` | `../1-network/` | Réseau routier, piéton, cyclable et ferry |
| `population_all_with_vtypes.rou.xml` | `../5-vehicles/` | Population convertie et types de véhicules HBEFA4 |
| `activities_poi_lonlat.add.xml` | `../2-POI's/` | POI d’activité pour l’affichage et le repérage |
| `vtypes.xml` | `../3-public_transport/` | Types de véhicules de transport collectif |
| `gtfs_pt_stops.add.xml` | `../3-public_transport/` | Arrêts de transport collectif |
| `gtfs_pt_vehicles_colored.add.xml` | `../3-public_transport/` | Véhicules TC programmés et colorés |
| `facilities2sumo_multimode.csv` | `../2-POI's/` | Appariement vers les arêtes utilisé par les taxis de repli |

Terminer les étapes 1 à 5 avant de commencer ce dossier.

## Prérequis

- Eclipse SUMO `1.27.1` pour reproduire la configuration de référence ;
- Python ;
- `sumolib` et `traci` provenant de la même installation SUMO ;
- `SUMO_HOME` correctement défini ;
- `pandas` n’est pas nécessaire au contrôleur lui-même, mais est utilisé dans
  les notebooks précédents ;
- suffisamment d’espace disque : les sorties par arête et voie peuvent
  atteindre plusieurs gigaoctets.

Contrôler dans l’invite de commandes :

```bat
echo %SUMO_HOME%
sumo --version
sumo-gui --version
python -c "import traci, sumolib; print(traci.__file__); print(sumolib.__file__)"
```

Les chemins Python affichés doivent correspondre à l’installation SUMO
souhaitée.

## Configuration du scénario SUMO

`sim.sumocfg` définit :

| Paramètre | Valeur de référence |
|---|---|
| Début de simulation | `0` s |
| Fin de simulation | `108000` s, soit 30 h |
| Gestion des itinéraires invalides | `ignore-route-errors=true` |
| Dispositif d’émissions | activé pour 100 % des véhicules |
| Paramètres GUI | `viewsettings.xml` |

L’horizon de 30 heures permet aux plans et services de transport collectif qui
dépassent minuit de se terminer.

`edge_outputs_s0.add.xml` ajoute une agrégation toutes les 60 secondes pour :

- le trafic par arête dans `outputs/edgedata_s0.xml` ;
- les émissions par arête dans `outputs/edge_emissions_s0.xml` ;
- les émissions par voie dans `outputs/lane_emissions_s0.xml`.

Consulter la
[documentation SUMO des émissions par arête et voie](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html)
pour les définitions et unités.

## Ordre d’exécution du notebook

Ouvrir `traci.ipynb` depuis ce dossier et exécuter ses cellules dans l’ordre.

### Cellule 1 — Construire et auditer les index TC

La première cellule lit la population finale, les arrêts TC et l’offre de
véhicules TC colorés. Elle construit des structures chronologiques pour :

- chaque passage de véhicule par couple `(arrêt, ligne)` ;
- chaque possibilité future de montée par
  `(arrêt origine, arrêt destination, ligne)` ;
- les métadonnées des arrêts.

Elle audite aussi chaque élément `<ride>` de la population et produit les
fichiers décrits dans
[`pt_index_out/README.md`](pt_index_out/README.md).

Contrôles de référence :

| Mesure | Valeur |
|---|---:|
| Arrêts de bus | 1 036 |
| Identifiants d’arrêt dupliqués | 0 |
| Itinéraires TC SUMO | 240 |
| Véhicules TC programmés | 1 638 |
| Passages arrêt-ligne indexés | 39 776 |
| Possibilités de montée indexées | 534 257 |
| Éléments `<ride>` de la population | 7 128 |
| Trajets non appariés pendant l’audit | 0 |

Les noms d’arrêt répétés sont normaux, car plusieurs quais ou directions
peuvent partager le même nom public. L’indexation utilise les identifiants, pas
uniquement les noms.

### Cellule 2 — Vérifier les fichiers nécessaires

La deuxième cellule confirme l’existence de l’index TC, de la population
finale et de la configuration SUMO.

### Cellule 3 — Démarrer le contrôleur événementiel

La commande de production enregistrée lance :

```bat
python traci_controller_strategy.py ^
  --sumocfg sim.sumocfg ^
  --population ..\5-vehicles\population_all_with_vtypes.rou.xml ^
  --index-dir pt_index_out ^
  --output-dir traci_strategy_event ^
  --all-persons ^
  --check-every 600 ^
  --monitor-every 60 ^
  --stranded-confirmation-time 600 ^
  --facilities-csv "..\2-POI's\facilities2sumo_multimode.csv" ^
  --sumo-binary sumo-gui ^
  --end 108000 ^
  --print-every-scan 3 ^
  --suppress-sumo-warnings ^
  --seed 1234 ^
  --close-gui-on-end
```

Dans la cellule Jupyter, les mêmes arguments sont écrits avec la syntaxe des
commandes de notebook. La commande ci-dessus est l’équivalent multiligne pour
l’invite de commandes Windows.

## Stratégie événementielle de repli

Pour chaque passager TC en attente, le contrôleur :

1. identifie le trajet restant attendu dans le plan initial de la personne ;
2. interroge l’index statique pour trouver un véhicule futur desservant
   exactement l’origine, la destination et la ligne ;
3. si l’offre statique n’a aucun candidat, recherche parmi les véhicules
   actifs un bus retardé qui peut encore prendre le passager ;
4. enregistre le premier échec comme une suspicion ;
5. ne confirme l’échouage que si la situation persiste pendant `600` secondes
   simulées ;
6. valide un trajet direct en taxi vers l’activité suivante ;
7. remplace la chaîne TC obsolète par un taxi déclenché dédié, une marche
   finale si nécessaire et le reste du plan journalier initial ;
8. conserve le même identifiant de personne et les heures absolues de fin des
   activités ;
9. écrit des diagnostics détaillés sur les corrections, échecs, étapes et
   événements du cycle de vie.

Le contrôleur ne supprime une personne que lorsque la politique d’échec de
correction ou une règle de protection contre un plantage l’exige. Cette
intervention modifie le comportement de déplacement initial et doit être
décrite dans l’analyse des parts modales, temps de trajet, trafics ou
émissions.

Références officielles :

- [présentation de TraCI](https://sumo.dlr.de/docs/TraCI/) ;
- [utilisation de TraCI en Python](https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html).

## Sorties

Les fichiers générés sont séparés en trois groupes :

| Dossier | Contenu |
|---|---|
| [`pt_index_out/`](pt_index_out/README.md) | Index TC réutilisables et audit des trajets avant simulation |
| [`outputs/`](outputs/README.md) | Sorties SUMO standard de mobilité, trafic, itinéraires et émissions |
| [`traci_strategy_event/`](traci_strategy_event/README.md) | Décisions du contrôleur, corrections, échecs, traces de plans et journaux SUMO |

Ne pas interpréter un fichier partiellement écrit pendant que SUMO ou le
contrôleur fonctionne. Une exécution de production n’est terminée qu’après
l’arrêt du contrôleur, la fermeture de SUMO, la présence des balises XML de
fermeture et la vérification des journaux d’erreurs.

## Exécution SUMO simple ou exécution contrôlée

Pour un contrôle visuel ou syntaxique sans contrôleur :

```bat
sumo-gui -c sim.sumocfg
```

Pour reproduire le comportement de production documenté, exécuter
`traci.ipynb` ou appeler `traci_controller_strategy.py` avec les arguments
indiqués. Une exécution SUMO simple n’applique ni la détection des passagers
échoués ni les corrections par taxi : elle constitue donc une expérience
différente.

## Reproductibilité et éléments à rapporter

Consigner au minimum :

- la version de SUMO ;
- la graine aléatoire ;
- le début et la fin de simulation ;
- l’archive GTFS et la date de service choisie ;
- la taille de population après conversion ;
- la distribution des classes de véhicules et la graine d’attribution ;
- les seuils du contrôleur et la politique de correction ;
- les nombres de corrections réussies, corrections échouées, suppressions,
  collisions, blocages, trajets inachevés et erreurs SUMO.

## Politique Git

La configuration, le contrôleur, le notebook, les paramètres d’affichage, les
README et les règles d’exclusion Git sont conservés. Tous les index et
résultats de simulation sont exclus car volumineux et reproductibles.
