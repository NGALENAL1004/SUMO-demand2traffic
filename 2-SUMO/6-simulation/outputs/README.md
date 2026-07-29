<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Standard SUMO simulation outputs

This folder receives the outputs configured in `../sim.sumocfg` and
`../edge_outputs_s0.add.xml`.

## Mobility and route outputs

| File | Main contents |
|---|---|
| `tripinfo_s0.xml` | Per-vehicle departure, arrival, delay, duration, distance, waiting, time loss, and device results |
| `personinfo_s0.xml` | Per-person stage and trip information |
| `vehroute_s0.xml` | Routes actually travelled by vehicles, including unfinished vehicles |
| `personroute_s0.xml` | Person stages and routes |
| `stops_s0.xml` | Vehicle-stop, boarding, alighting, and unfinished-stop information |
| `summary_s0.xml` | Network-wide simulation state every 60 seconds |
| `statistics_s0.xml` | Final global statistics and embedded run configuration |
| `collisions_s0.xml` | Recorded collisions |
| `deadlocks_s0.xml` | Recorded deadlocks or blocking events |

Official SUMO documentation:

- [TripInfo output](https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html);
- [vehicle routes output](https://sumo.dlr.de/docs/Simulation/Output/VehRoutes.html);
- [simulation outputs index](https://sumo.dlr.de/docs/Simulation/Output/).

## Traffic and emission outputs

| File | Main contents |
|---|---|
| `edgedata_s0.xml` | Traffic indicators by edge and 60-second interval |
| `edge_emissions_s0.xml` | Pollutants, fuel/electricity, and traffic indicators by edge and interval |
| `lane_emissions_s0.xml` | The same emission family at lane level |

These files may be extremely large. Check free disk space before a run and do
not open multi-gigabyte XML files directly in a text editor. Use streaming XML
parsers or SUMO analysis tools.

`output_edge_emissions_s0.zip` and `outputs_s0_sumo.zip`, when present, are
post-run convenience archives. They are not directly produced by the current
SUMO configuration and their creation procedure should be documented with any
published archive.

## Completion checks

Wait until SUMO and the TraCI controller have stopped, then:

1. check that every XML document has its closing root tag;
2. inspect `statistics_s0.xml`;
3. count collisions and deadlocks;
4. identify unfinished and undeparted trips;
5. compare completed persons and vehicles with the input population;
6. verify that emission outputs contain the expected intervals and HBEFA4
   classes;
7. inspect the controller logs in `../traci_strategy_event/`.

The files are generated and not tracked by Git. Only this README and
`.gitignore` are retained.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Sorties standard de la simulation SUMO

Ce dossier reçoit les sorties configurées dans `../sim.sumocfg` et
`../edge_outputs_s0.add.xml`.

## Sorties de mobilité et d’itinéraires

| Fichier | Contenu principal |
|---|---|
| `tripinfo_s0.xml` | Départ, arrivée, retard, durée, distance, attente, perte de temps et dispositifs par véhicule |
| `personinfo_s0.xml` | Informations sur les étapes et déplacements de chaque personne |
| `vehroute_s0.xml` | Itinéraires réellement parcourus, y compris les véhicules inachevés |
| `personroute_s0.xml` | Étapes et itinéraires des personnes |
| `stops_s0.xml` | Arrêts de véhicules, montées, descentes et arrêts inachevés |
| `summary_s0.xml` | État global du réseau toutes les 60 secondes |
| `statistics_s0.xml` | Statistiques finales et configuration embarquée de l’exécution |
| `collisions_s0.xml` | Collisions enregistrées |
| `deadlocks_s0.xml` | Blocages ou interblocages enregistrés |

Documentation officielle SUMO :

- [sortie TripInfo](https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html) ;
- [sortie des itinéraires de véhicules](https://sumo.dlr.de/docs/Simulation/Output/VehRoutes.html) ;
- [index des sorties de simulation](https://sumo.dlr.de/docs/Simulation/Output/).

## Sorties de trafic et d’émissions

| Fichier | Contenu principal |
|---|---|
| `edgedata_s0.xml` | Indicateurs de trafic par arête et intervalle de 60 secondes |
| `edge_emissions_s0.xml` | Polluants, carburant/électricité et trafic par arête et intervalle |
| `lane_emissions_s0.xml` | Même famille d’indicateurs d’émissions au niveau des voies |

Ces fichiers peuvent être extrêmement volumineux. Vérifier l’espace disque
avant une exécution et ne pas ouvrir directement un XML de plusieurs
gigaoctets dans un éditeur. Utiliser un parseur XML en flux ou les outils
d’analyse de SUMO.

`output_edge_emissions_s0.zip` et `outputs_s0_sumo.zip`, lorsqu’ils existent,
sont des archives pratiques créées après l’exécution. La configuration SUMO
actuelle ne les produit pas directement ; leur méthode de création doit être
documentée avec toute archive publiée.

## Contrôles de fin d’exécution

Attendre l’arrêt de SUMO et du contrôleur TraCI, puis :

1. vérifier la présence de la balise racine fermante de chaque XML ;
2. inspecter `statistics_s0.xml` ;
3. compter les collisions et blocages ;
4. identifier les trajets inachevés et non partis ;
5. comparer les personnes et véhicules terminés à la population d’entrée ;
6. vérifier que les sorties d’émissions contiennent les intervalles et classes
   HBEFA4 attendus ;
7. inspecter les journaux du contrôleur dans `../traci_strategy_event/`.

Les fichiers sont générés et ne sont pas suivis par Git. Seuls ce README et
`.gitignore` sont conservés.
