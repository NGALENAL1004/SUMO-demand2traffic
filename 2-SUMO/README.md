<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# From Eqasim travel demand to a SUMO simulation

This directory contains the reproducible workflow used to transform the
filtered Eqasim demand for the **Communauté d'Agglomération de La Rochelle
(CdA)** case study, defined in the context of **Yélo DETA**, into a multimodal
SUMO scenario. The workflow builds the network, locates activities, imports the
Yélo public transport timetable, converts daily plans, assigns vehicle
emission classes, and runs the final simulation.

The implementation is organised as a sequence of numbered folders. Large
source data and generated results are not intended to be committed to Git.
Each step contains its own bilingual README describing how to obtain or
regenerate them.

## Workflow overview

| Step | Main purpose | Main generated output |
|---|---|---|
| [`1-network/`](1-network/README.md) | Build the road and pedestrian network from OpenStreetMap | `cda_la_rochelle.net.xml` |
| [`2-POI's/`](2-POI's/README.md) | Map Eqasim activity facilities to SUMO edges and lanes | `facilities2sumo_multimode.csv` |
| [`3-public_transport/`](3-public_transport/README.md) | Import the Yélo GTFS timetable into SUMO | `gtfs_pt_stops.add.xml`, `gtfs_pt_vehicles_colored.add.xml` |
| [`4-convert_trips/`](4-convert_trips/README.md) | Convert filtered Eqasim daily plans into SUMO person plans | `population_all.rou.xml` |
| [`5-vehicles/`](5-vehicles/README.md) | Assign HBEFA4 emission classes to car users | `population_all_with_vtypes.rou.xml` |
| [`6-simulation/`](6-simulation/README.md) | Build PT indexes and run SUMO through the TraCI controller | simulation and diagnostic outputs |

The filtered Eqasim files required by steps 2 and 4 are staged in
[`eqasim_output_filtered/`](eqasim_output_filtered/README.md).

## Data flow

| Reproducible processing chain |
|:---:|
| **Filtered Eqasim population and plans** |
| ↓ |
| **SUMO network + activity locations + Yélo timetable** |
| ↓ |
| **SUMO multimodal population plans** |
| ↓ |
| **Vehicle fleet and HBEFA4 classes** |
| ↓ |
| **SUMO/TraCI simulation and traffic-emission outputs** |

## Recommended execution order

Open the project in VS Code, then execute the steps from their respective
directories:

1. run `1-network/network.ipynb`;
2. run `2-POI's/activity.ipynb`;
3. run the two batch files and then
   `3-public_transport/3-pt.ipynb`;
4. run both cells of `4-convert_trips/trips.ipynb`;
5. run `5-vehicles/vehicles.ipynb`;
6. run `6-simulation/traci.ipynb`.

Do not start a later stage before all of its documented inputs exist.
Notebooks use relative paths, so their current working directory must be the
folder containing the notebook.

## Main software requirements

The reference workflow was run on Windows with VS Code and Command Prompt. It
requires:

- Python and Jupyter;
- Eclipse SUMO, including `netconvert`, `polyconvert`, `sumolib`, and `traci`;
- a valid `SUMO_HOME` environment variable;
- Osmium Tool;
- the Python packages listed in the individual step READMEs.

The documented reference outputs were generated with SUMO `1.27.1`. Using
another SUMO version may change network conversion, route mapping, emissions,
or XML output.

Official SUMO resources:

- [Eclipse SUMO](https://eclipse.dev/sumo/);
- [SUMO documentation](https://sumo.dlr.de/docs/);
- [GTFS import tutorial](https://sumo.dlr.de/docs/Tutorials/GTFS.html);
- [TraCI documentation](https://sumo.dlr.de/docs/TraCI/);
- [SUMO emission models](https://sumo.dlr.de/docs/Models/Emissions.html).

## Reproducibility principles

- Raw downloads and generated files remain local.
- Each data-input README provides the official source, expected filename, and,
  when available, the checksum of the reference snapshot.
- Diagnostic CSV and JSON files are kept locally and should be inspected
  before accepting a run.
- A fixed random seed is used where the workflow explicitly performs a
  stochastic or pseudo-random assignment.
- The date selected for the public transport timetable is part of the
  scenario definition and must be reported with the results.

## Associated publication

This workflow is described in the following preprint. If you reuse the
methodology or code, please cite:

> Ngari Lendoye, A., Graindorge, T., Fèvre, C., & Bouju, A. (2026).
> *Integrating Synthetic Populations and Activity Chains for Individual
> Emission Assessment in SUMO* (v1) [Preprint]. Zenodo.
> [https://doi.org/10.5281/zenodo.21676913](https://doi.org/10.5281/zenodo.21676913)

**DOI:** [`10.5281/zenodo.21676913`](https://doi.org/10.5281/zenodo.21676913)  
**Zenodo record:** [zenodo.org/records/21676913](https://zenodo.org/records/21676913)

## Scope and interpretation

This directory documents a reusable Eqasim-to-SUMO conversion workflow, with
the Communauté d'Agglomération de La Rochelle as its application case. Paths,
municipality codes, the GTFS feed, matching rules, vehicle-fleet proportions,
and simulation parameters are case-study settings and must be adapted before
applying the code to another territory or scenario.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# De la demande Eqasim à une simulation SUMO

Ce dossier contient la chaîne reproductible utilisée pour transformer la
demande Eqasim filtrée du cas d'étude de la **Communauté d'Agglomération de La
Rochelle (CdA)**, défini dans le contexte de **Yélo DETA**, en un scénario SUMO
multimodal. Elle construit le réseau, localise les activités, importe les
horaires du réseau Yélo, convertit les plans journaliers, attribue les classes
d’émissions des véhicules et exécute la simulation finale.

L’implémentation est organisée en dossiers numérotés. Les données sources
volumineuses et les résultats générés n’ont pas vocation à être déposés sur
Git. Chaque étape possède son propre README bilingue expliquant comment les
obtenir ou les régénérer.

## Vue d’ensemble de la chaîne

| Étape | Rôle principal | Sortie principale générée |
|---|---|---|
| [`1-network/`](1-network/README.md) | Construire le réseau routier et piéton depuis OpenStreetMap | `cda_la_rochelle.net.xml` |
| [`2-POI's/`](2-POI's/README.md) | Rattacher les lieux d’activité Eqasim aux arêtes et voies SUMO | `facilities2sumo_multimode.csv` |
| [`3-public_transport/`](3-public_transport/README.md) | Importer les horaires GTFS de Yélo dans SUMO | `gtfs_pt_stops.add.xml`, `gtfs_pt_vehicles_colored.add.xml` |
| [`4-convert_trips/`](4-convert_trips/README.md) | Convertir les plans journaliers Eqasim en plans de personnes SUMO | `population_all.rou.xml` |
| [`5-vehicles/`](5-vehicles/README.md) | Attribuer des classes d’émissions HBEFA4 aux usagers de la voiture | `population_all_with_vtypes.rou.xml` |
| [`6-simulation/`](6-simulation/README.md) | Construire les index TC et exécuter SUMO avec le contrôleur TraCI | résultats de simulation et diagnostics |

Les fichiers Eqasim filtrés nécessaires aux étapes 2 et 4 sont placés dans
[`eqasim_output_filtered/`](eqasim_output_filtered/README.md).

## Flux de données

| Chaîne de traitement reproductible |
|:---:|
| **Population et plans Eqasim filtrés** |
| ↓ |
| **Réseau SUMO + lieux d’activité + horaires Yélo** |
| ↓ |
| **Plans de population multimodaux SUMO** |
| ↓ |
| **Parc de véhicules et classes HBEFA4** |
| ↓ |
| **Simulation SUMO/TraCI et sorties trafic-émissions** |

## Ordre d’exécution recommandé

Ouvrir le projet dans VS Code, puis exécuter les étapes depuis leurs dossiers
respectifs :

1. exécuter `1-network/network.ipynb` ;
2. exécuter `2-POI's/activity.ipynb` ;
3. exécuter les deux fichiers batch, puis
   `3-public_transport/3-pt.ipynb` ;
4. exécuter les deux cellules de `4-convert_trips/trips.ipynb` ;
5. exécuter `5-vehicles/vehicles.ipynb` ;
6. exécuter `6-simulation/traci.ipynb`.

Ne pas commencer une étape tant que toutes ses entrées documentées ne sont
pas disponibles. Les notebooks utilisent des chemins relatifs : leur dossier
de travail doit donc être le dossier qui contient le notebook.

## Principaux logiciels nécessaires

La chaîne de référence a été exécutée sous Windows avec VS Code et l’invite de
commandes. Elle nécessite :

- Python et Jupyter ;
- Eclipse SUMO, notamment `netconvert`, `polyconvert`, `sumolib` et `traci` ;
- une variable d’environnement `SUMO_HOME` correctement définie ;
- Osmium Tool ;
- les bibliothèques Python précisées dans les README de chaque étape.

Les sorties de référence documentées ont été produites avec SUMO `1.27.1`.
Une autre version peut modifier la conversion du réseau, l’appariement des
itinéraires, les émissions ou les sorties XML.

Ressources officielles SUMO :

- [Eclipse SUMO](https://eclipse.dev/sumo/) ;
- [documentation SUMO](https://sumo.dlr.de/docs/) ;
- [tutoriel d’import GTFS](https://sumo.dlr.de/docs/Tutorials/GTFS.html) ;
- [documentation TraCI](https://sumo.dlr.de/docs/TraCI/) ;
- [modèles d’émissions SUMO](https://sumo.dlr.de/docs/Models/Emissions.html).

## Principes de reproductibilité

- Les téléchargements bruts et les fichiers générés restent locaux.
- Chaque README de données d’entrée fournit la source officielle, le nom
  attendu et, lorsque cela est possible, l’empreinte du fichier de référence.
- Les CSV et JSON de diagnostic restent locaux et doivent être inspectés
  avant de valider une exécution.
- Une graine fixe est utilisée lorsque la chaîne effectue explicitement une
  attribution stochastique ou pseudo-aléatoire.
- La date choisie pour l’offre de transport collectif fait partie de la
  définition du scénario et doit être mentionnée avec les résultats.

## Publication associée

Cette chaîne est décrite dans le preprint suivant. En cas de réutilisation de
la méthode ou du code, merci de citer :

> Ngari Lendoye, A., Graindorge, T., Fèvre, C., & Bouju, A. (2026).
> *Integrating Synthetic Populations and Activity Chains for Individual
> Emission Assessment in SUMO* (v1) [Preprint]. Zenodo.
> [https://doi.org/10.5281/zenodo.21676913](https://doi.org/10.5281/zenodo.21676913)

**DOI :** [`10.5281/zenodo.21676913`](https://doi.org/10.5281/zenodo.21676913)  
**Notice Zenodo :** [zenodo.org/records/21676913](https://zenodo.org/records/21676913)

## Portée et interprétation

Ce dossier documente une méthode réutilisable de conversion d'Eqasim vers
SUMO, appliquée ici à la Communauté d'Agglomération de La Rochelle. Les
chemins, codes de communes, données GTFS, règles d'appariement, proportions du
parc automobile et paramètres de simulation sont propres au cas d'étude. Ils
doivent être adaptés avant d'utiliser le code sur un autre territoire ou pour
un autre scénario.
