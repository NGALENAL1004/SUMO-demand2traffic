<a id="english-version"></a>

> **Languages:** The English version is presented first.
> [The French version is available below.](#version-francaise)

# Vehicle-fleet input data and methodological references

This folder locally stores the data used to construct the passenger-car
emission-class distribution.

## 1. Commune-level road-vehicle fleet

Official dataset:

- [Road vehicle fleet — data.gouv.fr](https://www.data.gouv.fr/datasets/parc-de-vehicules-routiers).

Download the commune-level CSV containing fuel, Crit'Air, user status,
vehicle category, and annual fleet counts. The notebook currently expects:

```text
Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2025-09.csv
```

Reference snapshot:

| Property | Value |
|---|---|
| Size | 222,726,771 bytes |
| SHA-256 | `E037C7F7F5B6510A72C3ACF5A6E6A3F558DB61209EAD0AC4888A2AE0E8C6DC17` |
| Separator | semicolon |
| Fleet column used | `PARC_2022` |
| Vehicle category used | `VP` |

The official dataset is updated and recent years may be revised. If a newer
file is used, update `INPUT_CSV`, verify the column names, choose the intended
fleet year explicitly, and report the dataset version.

## 2. RSVERO methodology

Official methodological page:

- [Methodology for estimating vehicle fleets and distances travelled](https://www.statistiques.developpement-durable.gouv.fr/methodologie-pour-lestimation-des-parcs-de-vehicules-et-des-distances-parcourues).

Reference local filename and checksum:

```text
document-travail-67-methodologie-rsvero-mars2024.pdf
SHA-256: F53D0890FE3255158A6AF4E178FD655294CC0D88D0D157C530E963C60E4ED161
```

The methodology explains the statistical road-vehicle register (RSVERO), its
administrative sources, scope, estimation, and revisions.

## 3. Crit'Air passenger-car classification

Official reference:

- [Crit'Air passenger-car classification table](https://www.certificat-air.gouv.fr/files/CQA_classementVoitureParticuliere.pdf);
- [official Crit'Air website](https://www.certificat-air.gouv.fr/).

Reference local filename and checksum:

```text
Tableau de classification - voitures particulières.pdf
SHA-256: 79F3AB2C441CCFA67FCB3A3DE68ABE8A054DFD8A36786FB5790A450D3B160896
```

The table links vehicle energy source, Euro standard or first registration
date, and Crit'Air class. The subsequent conversion from those categories to
SUMO HBEFA4 classes remains a modelling choice documented in the parent
README.

## Git policy

The CSV and PDFs are not committed. Only this README and `.gitignore` are
retained. Users download the official sources and record the exact versions
used.

<a id="version-francaise"></a>

---

> **Langues :** la version française est présentée ci-dessous.
> [La version anglaise se trouve plus haut.](#english-version)

# Données du parc automobile et références méthodologiques

Ce dossier contient localement les données utilisées pour construire la
distribution des classes d’émissions des voitures particulières.

## 1. Parc de véhicules routiers au niveau communal

Jeu de données officiel :

- [Parc de véhicules routiers — data.gouv.fr](https://www.data.gouv.fr/datasets/parc-de-vehicules-routiers).

Télécharger le CSV communal contenant le carburant, Crit'Air, le statut de
l’utilisateur, la catégorie du véhicule et les effectifs annuels. Le notebook
attend actuellement :

```text
Donnees-sur-le-parc-de-vehicules-au-niveau-communal.2025-09.csv
```

Archive de référence :

| Propriété | Valeur |
|---|---|
| Taille | 222 726 771 octets |
| SHA-256 | `E037C7F7F5B6510A72C3ACF5A6E6A3F558DB61209EAD0AC4888A2AE0E8C6DC17` |
| Séparateur | point-virgule |
| Colonne d’effectif utilisée | `PARC_2022` |
| Catégorie utilisée | `VP` |

Le jeu officiel est mis à jour et les années récentes peuvent être révisées.
Avec un nouveau fichier, modifier `INPUT_CSV`, vérifier les noms de colonnes,
choisir explicitement l’année de parc souhaitée et consigner la version des
données.

## 2. Méthodologie RSVERO

Page méthodologique officielle :

- [Méthodologie pour l’estimation des parcs de véhicules et des distances parcourues](https://www.statistiques.developpement-durable.gouv.fr/methodologie-pour-lestimation-des-parcs-de-vehicules-et-des-distances-parcourues).

Nom local et empreinte de référence :

```text
document-travail-67-methodologie-rsvero-mars2024.pdf
SHA-256: F53D0890FE3255158A6AF4E178FD655294CC0D88D0D157C530E963C60E4ED161
```

Cette publication explique le répertoire statistique des véhicules routiers
RSVERO, ses sources administratives, son champ, ses estimations et révisions.

## 3. Classification Crit'Air des voitures particulières

Références officielles :

- [tableau de classement Crit'Air des voitures particulières](https://www.certificat-air.gouv.fr/files/CQA_classementVoitureParticuliere.pdf) ;
- [site officiel Crit'Air](https://www.certificat-air.gouv.fr/).

Nom local et empreinte de référence :

```text
Tableau de classification - voitures particulières.pdf
SHA-256: 79F3AB2C441CCFA67FCB3A3DE68ABE8A054DFD8A36786FB5790A450D3B160896
```

Le tableau relie la source d’énergie, la norme Euro ou la date de première
immatriculation et la classe Crit'Air. La conversion ultérieure de ces
catégories vers HBEFA4 dans SUMO reste un choix de modélisation documenté dans
le README parent.

## Politique Git

Le CSV et les PDF ne sont pas déposés. Seuls ce README et `.gitignore` sont
conservés. Les utilisateurs téléchargent les sources officielles et consignent
les versions exactes employées.
