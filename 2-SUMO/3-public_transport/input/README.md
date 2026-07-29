<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Yélo GTFS input

This folder locally stores the static GTFS timetable for the Yélo public
transport network of the Communauté d’agglomération de La Rochelle.

The data are published by Nouvelle-Aquitaine Mobilités and produced by Yélo
on the French National Access Point:

- [Yélo dataset page](https://transport.data.gouv.fr/datasets/arrets-horaires-et-parcours-theoriques-des-reseaux-naq-lro-nva-m-1);
- [GTFS resource information](https://transport.data.gouv.fr/resources/82350).

The resource page also provides historical versions. To reproduce the
reference scenario, select a GTFS version covering **17 March 2026**.

## Expected filename

Download the GTFS ZIP archive and save or rename it as:

```text
ca_la_rochelle-aggregated-gtfs.zip
```

Do not extract it: the scripts and notebooks read the tables directly from
the ZIP archive.

## Reference snapshot

| Property | Value |
|---|---|
| Filename | `ca_la_rochelle-aggregated-gtfs.zip` |
| Size | 1,618,296 bytes |
| SHA-256 | `79E76B6F2D8D59D77436F3D7F2647FF6EBDA9B336B52FE3907A11FF36EF89D45` |
| Operator in `agency.txt` | Yélo |
| Scenario date | `20260317` |

The archive contains `agency.txt`, `routes.txt`, `trips.txt`, `stops.txt`,
`stop_times.txt`, `shapes.txt`, `calendar.txt`, and `calendar_dates.txt`.

If the checksum differs, record the download date and the GTFS validity period
because public transport data are updated over time. A newer archive is not
necessarily compatible with the reference scenario date or the Eqasim transit
identifiers.

## Licence and attribution

Use the licence and reuse conditions displayed on the National Access Point
for the selected resource version. Cite Nouvelle-Aquitaine Mobilités and Yélo
with any published results derived from the feed.

## Git policy

The GTFS ZIP is not committed. Only this README and `.gitignore` are retained
in the repository.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Entrée GTFS de Yélo

Ce dossier contient localement l’offre GTFS statique du réseau de transport
collectif Yélo de la Communauté d’agglomération de La Rochelle.

Les données sont diffusées par Nouvelle-Aquitaine Mobilités, produites par
Yélo et publiées sur le Point d’accès national français :

- [page du jeu de données Yélo](https://transport.data.gouv.fr/datasets/arrets-horaires-et-parcours-theoriques-des-reseaux-naq-lro-nva-m-1) ;
- [informations sur la ressource GTFS](https://transport.data.gouv.fr/resources/82350).

La page de la ressource donne également accès aux versions historiques. Pour
reproduire le scénario de référence, choisir une version GTFS couvrant le
**17 mars 2026**.

## Nom de fichier attendu

Télécharger l’archive ZIP GTFS et l’enregistrer ou la renommer ainsi :

```text
ca_la_rochelle-aggregated-gtfs.zip
```

Ne pas l’extraire : les scripts et notebooks lisent directement les tables
dans l’archive ZIP.

## Archive de référence

| Propriété | Valeur |
|---|---|
| Nom | `ca_la_rochelle-aggregated-gtfs.zip` |
| Taille | 1 618 296 octets |
| SHA-256 | `79E76B6F2D8D59D77436F3D7F2647FF6EBDA9B336B52FE3907A11FF36EF89D45` |
| Exploitant dans `agency.txt` | Yélo |
| Date du scénario | `20260317` |

L’archive contient `agency.txt`, `routes.txt`, `trips.txt`, `stops.txt`,
`stop_times.txt`, `shapes.txt`, `calendar.txt` et `calendar_dates.txt`.

Si l’empreinte diffère, consigner la date de téléchargement et la période de
validité du GTFS, car l’offre est régulièrement mise à jour. Une version plus
récente n’est pas nécessairement compatible avec la date du scénario de
référence ni avec les identifiants de transport Eqasim.

## Licence et attribution

Respecter la licence et les conditions de réutilisation affichées sur le Point
d’accès national pour la version choisie. Citer Nouvelle-Aquitaine Mobilités
et Yélo dans toute publication issue de ces données.

## Politique Git

L’archive GTFS n’est pas déposée. Seuls ce README et `.gitignore` sont
conservés dans le dépôt.
