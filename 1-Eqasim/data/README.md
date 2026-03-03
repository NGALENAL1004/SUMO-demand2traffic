# `data/` — Input datasets for the Eqasim France population pipeline

This folder contains **all raw input datasets** required to run the Eqasim France synthetic population pipeline.
It follows the directory layout described in the official Eqasim documentation (“Gathering the data”).

**Reference:** Eqasim documentation — *Gathering the data*  
https://eqasim-org.github.io/eqasim-france/population/population_data.html 

## Scope and principles

- This repository keeps **code and data separated**. Do **not** place large raw datasets inside the cloned code repository by default. :contentReference[oaicite:2]{index=2}
- Most datasets are **national** (download once; the pipeline filters later).
- Some datasets are **department-split** (download only the departments covering your study area). :contentReference[oaicite:3]{index=3}

## Required datasets (Eqasim reference)

Eqasim lists the following inputs and where they should be stored: :contentReference[oaicite:4]{index=4}

- Census microdata (RP 2022) → `data/rp_2022/`
- Population totals (RP 2022) → `data/rp_2022/`
- OD data (RP-MOBPRO / RP-MOBSCO 2022) → `data/rp_2022/`
- Income tax data (Filosofi 2021) → `data/filosofi_2021/`
- Services/facilities census (BPE 2024) → `data/bpe_2024/`
- National household travel survey (ENTD 2008) → `data/entd_2008/`
- (Optional) National Person Mobility Survey (EMP 2019) → `data/emp_2019/`
- IRIS zoning (2024) → `data/iris_2024/`
- Zoning registry / code tables (2024 edition) → `data/codes_2024/`
- Enterprise census (SIRENE + geolocated establishments) → `data/sirene/`
- Buildings database (IGN BD TOPO, department split) → `data/bdtopo_<area>/`
- Addresses database (BAN, department split) → `data/ban_<area>/` :contentReference[oaicite:5]{index=5}

## Recommended folder structure

Create the following subfolders under `data/` (names can be adapted, but must match your pipeline config):

```text
data/
├── rp_2022/
├── filosofi_2021/
├── bpe_2024/
├── entd_2008/
├── emp_2019/          # optional
├── iris_2024/
├── codes_2024/
├── sirene/
├── bdtopo_<area>/     # department-split
└── ban_<area>/        # department-split

```

## Study-area downloads (important)

For **department-split datasets** (e.g., **IGN BD TOPO** buildings, **BAN** addresses), download **only** the department(s) covering your study area.

**Reference:** Eqasim documentation — *Gathering the data*  
https://eqasim-org.github.io/eqasim-france/population/population_data.html 

**Example — Charente-Maritime (department 17):**
- Download **BD TOPO** for **D017** and place it in:
  - `data/bdtopo_17/`
- Download **BAN** file `adresses-17.csv.gz` and place it in:
  - `data/ban_17/`

## Quick checklist (minimum expected files)

Eqasim provides an **“Overview”** list of example filenames to verify that the `data/` folder is complete.  
Your folder should contain **equivalent files**, including **department-specific variants** where applicable.

