# Demonstration Satellite Imagery Catalog & Source Attribution

**Project:** Intelligent Vegetation & Canopy Detection Platform (ET401 P1)
**Author:** Dhyey Pujara (BT23GCS150)
**Purpose:** Live project demonstration using 100% raw, unanalyzed true-color satellite imagery.

---

## Summary of Demonstration Dataset

This directory contains **16 raw, authentic satellite scenes** captured by **Copernicus Sentinel-2** (ESA) and **USGS/NASA Landsat 7 & 8** satellites. None of these images contain pre-baked annotations, false-color overlays, or text watermarks, ensuring that all canopy detection, spatial density convolution, chlorophyll health classification, CIR false-color simulation, and temporal change matrices are computed in real time by the platform.

| # | File Name | Feature Demonstrated | Satellite Sensor | Ground Resolution | License | Source / Attribution |
|---|-----------|----------------------|------------------|-------------------|---------|----------------------|
| 01 | `01_puglia_agricultural_patchwork.jpg` | Canopy Segmentation & GSD Area Scaling | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:Earth_from_Space-_Agricultural_patchwork_ESA524165.jpg) |
| 02 | `02_san_francisco_bay_agriculture.jpg` | Canopy Segmentation & GSD Area Scaling | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY 2.0 | [Copernicus Sentinel Data (Processed by Pierre Markuse)](https://commons.wikimedia.org/wiki/File:San_Francisco_Bay_Agriculture_(52242205086).png) |
| 03 | `03_nile_delta_natural_color.jpg` | Canopy Segmentation & GSD Area Scaling | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel Data](https://commons.wikimedia.org/wiki/File:Nile_Delta.jpg) |
| 04 | `04_kansas_center_pivot_irrigation.jpg` | Kernel Density Heatmaps & Connected Components | NASA / USGS Landsat 8 | 30m GSD / True Color RGB | Public Domain (NASA / USGS) | [NASA Earth Observatory / USGS Landsat](https://commons.wikimedia.org/wiki/File:Landsat_sees_crops_in_Kansas.jpg) |
| 05 | `05_yuma_checkerboard_fields.jpg` | Kernel Density Heatmaps & Connected Components | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:Yuma_chequerboard_ESA357473.jpg) |
| 06 | `06_morocco_semi_arid_patchwork.jpg` | Kernel Density Heatmaps & Connected Components | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Union, Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:The_effects_of_the_drought_on_vegetation_in_Morocco.jpg) |
| 07 | `07_sundarbans_mangrove_canopy.jpg` | 3-Tier Chlorophyll Health Classification | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:Sundarbans_National_Park.jpg) |
| 08 | `08_amazon_rainforest_primary_canopy.jpg` | 3-Tier Chlorophyll Health Classification | Copernicus Sentinel-2 (ESA) | 10m GSD / True Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:Amazon_River,_Sentinel-2.jpg) |
| 09 | `09_rwandan_highland_agriculture.jpg` | 3-Tier Chlorophyll Health Classification | NASA / USGS Landsat 8 & 9 Composite | 30m GSD / True Color RGB | Public Domain (NASA) | [NASA Scientific Visualization Studio / USGS Landsat](https://commons.wikimedia.org/wiki/File:Landsat_8_and_9_Composite_of_Rwanda_(SVS31242).png) |
| 10 | `10_singapore_urban_and_nature_reserves.jpg` | CIR False-Color Simulation & Urban Canopy | NASA / USGS Landsat 7 | 30m GSD / Natural Color RGB | Public Domain (NASA / USGS) | [NASA Earth Observatory / USGS](https://commons.wikimedia.org/wiki/File:Satellite_image_of_Singapore_(Landsat_7)_-_20000428.jpg) |
| 11 | `11_tokyo_metropolitan_green_spaces.jpg` | CIR False-Color Simulation & Urban Canopy | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY 2.0 | [Copernicus Sentinel Data / Pierre Markuse](https://commons.wikimedia.org/wiki/File:Tokyo_by_Sentinel-2,_2018-10-30.jpg) |
| 12 | `12_koukdjuak_tundra_wetlands.jpg` | CIR False-Color Simulation & Urban Canopy | Copernicus Sentinel-2 (ESA) | 10m GSD / Highlight-Optimized Natural Color | CC BY 2.0 | [Copernicus Sentinel Data / Pierre Markuse](https://commons.wikimedia.org/wiki/File:Koukdjuak_River_2019-08-19_Sentinel-2_L2A_Highlight_Optimized_Natural_Color(2).jpg) |
| 13 | `temporal_pair1_rondonia_deforestation_2014.jpg` | Temporal Delta Matrix (Before Baseline - June 2014) | NASA / USGS Landsat 8 (OLI) | 30m GSD / Natural Color RGB | CC BY 2.0 | [USGS / NASA Landsat (Processed by Pierre Markuse)](https://commons.wikimedia.org/wiki/File:Rond%C3%B4nia_Deforestation_(18_June_2014),_Brazil_(34722156551).jpg) |
| 14 | `temporal_pair1_rondonia_deforestation_2016.jpg` | Temporal Delta Matrix (After Follow-up - July 2016) | NASA / USGS Landsat 8 (OLI) | 30m GSD / Natural Color RGB | CC BY 2.0 | [USGS / NASA Landsat (Processed by Pierre Markuse)](https://commons.wikimedia.org/wiki/File:Rond%C3%B4nia_Deforestation_(25_July_2016),_Brazil_(34296310700).jpg) |
| 15 | `temporal_pair2_agricultural_dormant_baseline.jpg` | Temporal Delta Matrix (Before Baseline - Dry Season / Pre-Emergence) | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Union, Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:The_effects_of_the_drought_on_vegetation_in_Morocco.jpg) |
| 16 | `temporal_pair2_agricultural_peak_canopy.jpg` | Temporal Delta Matrix (After Follow-up - Peak Canopy Growth) | Copernicus Sentinel-2 (ESA) | 10m GSD / Natural Color RGB | CC BY-SA 3.0 IGO | [European Space Agency (ESA) / Copernicus Sentinel-2](https://commons.wikimedia.org/wiki/File:Earth_from_Space-_Agricultural_patchwork_ESA524165.jpg) |

---

## Detailed Imagery Information & Live Demonstration Guide

### 1. Multi-Spectral Canopy Detection & GSD Scaling

#### `01_puglia_agricultural_patchwork.jpg` — Agricultural Patchwork in Puglia, Italy
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Canopy Segmentation & GSD Area Scaling
- **Description:** Raw, unannotated true-color satellite capture of southern Italian olive groves, wheat parcels, and rural farmland. Ideal for testing multi-spectral green canopy masking and ground area scaling.
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Earth_from_Space-_Agricultural_patchwork_ESA524165.jpg)

#### `02_san_francisco_bay_agriculture.jpg` — San Francisco Bay Agricultural Valleys, California
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Canopy Segmentation & GSD Area Scaling
- **Description:** Clean, unannotated true-color satellite scene showing coastal agricultural valley fields and surrounding hills with distinct canopy boundaries.
- **Credit & Attribution:** Copernicus Sentinel Data (Processed by Pierre Markuse)
- **License:** CC BY 2.0
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:San_Francisco_Bay_Agriculture_(52242205086).png)

#### `03_nile_delta_natural_color.jpg` — Nile River Delta Natural Color Corridor, Egypt
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Canopy Segmentation & GSD Area Scaling
- **Description:** Pristine overhead natural color satellite capture of the vibrant green Nile River floodplain against high-contrast arid desert terrain.
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel Data
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Nile_Delta.jpg)

### 2. Spatial Density & Patch Fragmentation

#### `04_kansas_center_pivot_irrigation.jpg` — Center-Pivot Circular Crop Fields, Kansas
- **Satellite & Sensor:** NASA / USGS Landsat 8
- **Spatial Resolution:** 30m GSD / True Color RGB
- **Feature Demonstrated:** Kernel Density Heatmaps & Connected Components
- **Description:** Pure aerial satellite view of discrete circular center-pivot irrigated crops. Perfect for demonstrating patch clustering, connected component isolation, and fragmentation indexing.
- **Credit & Attribution:** NASA Earth Observatory / USGS Landsat
- **License:** Public Domain (NASA / USGS)
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Landsat_sees_crops_in_Kansas.jpg)

#### `05_yuma_checkerboard_fields.jpg` — Yuma Checkerboard Crop Fields, USA/Mexico
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Kernel Density Heatmaps & Connected Components
- **Description:** Orthogonal checkerboard agricultural grid in the Colorado River basin. Ideal for evaluating 2D Gaussian kernel density convolution and spatial clustering.
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Yuma_chequerboard_ESA357473.jpg)

#### `06_morocco_semi_arid_patchwork.jpg` — Semi-Arid Fragmented Vegetation, Morocco
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Kernel Density Heatmaps & Connected Components
- **Description:** Clean overhead satellite view of fragmented scrubland and small agricultural plots in semi-arid terrain.
- **Credit & Attribution:** European Union, Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:The_effects_of_the_drought_on_vegetation_in_Morocco.jpg)

### 3. Canopy Health & Chlorophyll Vigor

#### `07_sundarbans_mangrove_canopy.jpg` — Sundarbans Coastal Mangrove Canopy, India/Bangladesh
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** 3-Tier Chlorophyll Health Classification
- **Description:** Dense, pristine mangrove canopy showing high chlorophyll concentration for testing Tier 1 (High Vigor) Green Leaf Index (GLI > 0.35).
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Sundarbans_National_Park.jpg)

#### `08_amazon_rainforest_primary_canopy.jpg` — Amazon River Basin Broadleaf Rainforest, Brazil
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / True Color RGB
- **Feature Demonstrated:** 3-Tier Chlorophyll Health Classification
- **Description:** Continuous primary tropical rainforest canopy providing maximum biomass and high chlorophyll greenness response for health histogram validation.
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Amazon_River,_Sentinel-2.jpg)

#### `09_rwandan_highland_agriculture.jpg` — Rwandan Highland Canopy & Cropland, East Africa
- **Satellite & Sensor:** NASA / USGS Landsat 8 & 9 Composite
- **Spatial Resolution:** 30m GSD / True Color RGB
- **Feature Demonstrated:** 3-Tier Chlorophyll Health Classification
- **Description:** High-altitude terraced farming and montane forest canopy in the Thousand Hills region with varied health distributions across altitude gradients.
- **Credit & Attribution:** NASA Scientific Visualization Studio / USGS Landsat
- **License:** Public Domain (NASA)
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Landsat_8_and_9_Composite_of_Rwanda_(SVS31242).png)

### 4. CIR Simulation & Urban Canopy Boundary

#### `10_singapore_urban_and_nature_reserves.jpg` — Singapore Island Urban Matrix & Nature Reserves
- **Satellite & Sensor:** NASA / USGS Landsat 7
- **Spatial Resolution:** 30m GSD / Natural Color RGB
- **Feature Demonstrated:** CIR False-Color Simulation & Urban Canopy
- **Description:** Clean overhead satellite capture showing dense urban infrastructure, shipping straits, and Central Catchment Nature Reserve forest.
- **Credit & Attribution:** NASA Earth Observatory / USGS
- **License:** Public Domain (NASA / USGS)
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Satellite_image_of_Singapore_(Landsat_7)_-_20000428.jpg)

#### `11_tokyo_metropolitan_green_spaces.jpg` — Tokyo Metropolitan Green Spaces & Bay, Japan
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** CIR False-Color Simulation & Urban Canopy
- **Description:** Metropolitan cityscape featuring Imperial Palace gardens, Shinjuku Gyoen, and Tama hills. Demonstrates live CIR false-color synthesis on raw RGB.
- **Credit & Attribution:** Copernicus Sentinel Data / Pierre Markuse
- **License:** CC BY 2.0
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Tokyo_by_Sentinel-2,_2018-10-30.jpg)

#### `12_koukdjuak_tundra_wetlands.jpg` — Koukdjuak River Tundra Wetlands, Arctic Canada
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Highlight-Optimized Natural Color
- **Feature Demonstrated:** CIR False-Color Simulation & Urban Canopy
- **Description:** Natural color tundra vegetation and braided stream channels, testing sub-quadrant ROI sector slicing and gradient mapping.
- **Credit & Attribution:** Copernicus Sentinel Data / Pierre Markuse
- **License:** CC BY 2.0
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Koukdjuak_River_2019-08-19_Sentinel-2_L2A_Highlight_Optimized_Natural_Color(2).jpg)

### 5. Temporal Change Detection (Pair 1 - Amazon Deforestation)

#### `temporal_pair1_rondonia_deforestation_2014.jpg` — Rondônia Amazon Rainforest Baseline (18 June 2014)
- **Satellite & Sensor:** NASA / USGS Landsat 8 (OLI)
- **Spatial Resolution:** 30m GSD / Natural Color RGB
- **Feature Demonstrated:** Temporal Delta Matrix (Before Baseline - June 2014)
- **Description:** Exact geographic satellite capture of Rondônia, Brazil in June 2014 with intact forest blocks between feeder roads. Pairs directly with the 2016 follow-up scene.
- **Credit & Attribution:** USGS / NASA Landsat (Processed by Pierre Markuse)
- **License:** CC BY 2.0
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Rond%C3%B4nia_Deforestation_(18_June_2014),_Brazil_(34722156551).jpg)

#### `temporal_pair1_rondonia_deforestation_2016.jpg` — Rondônia Amazon Rainforest Follow-up (25 July 2016)
- **Satellite & Sensor:** NASA / USGS Landsat 8 (OLI)
- **Spatial Resolution:** 30m GSD / Natural Color RGB
- **Feature Demonstrated:** Temporal Delta Matrix (After Follow-up - July 2016)
- **Description:** Identical coordinate framing 2 years later showing clear fishbone clearings and canopy removal (detected as Red Deforestation Loss).
- **Credit & Attribution:** USGS / NASA Landsat (Processed by Pierre Markuse)
- **License:** CC BY 2.0
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Rond%C3%B4nia_Deforestation_(25_July_2016),_Brazil_(34296310700).jpg)

### 5. Temporal Change Detection (Pair 2 - Agricultural Greening)

#### `temporal_pair2_agricultural_dormant_baseline.jpg` — Agricultural Basin Baseline (Dry / Pre-Season)
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Temporal Delta Matrix (Before Baseline - Dry Season / Pre-Emergence)
- **Description:** Dry, low-chlorophyll dormant agricultural terrain prior to seasonal crop emergence.
- **Credit & Attribution:** European Union, Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:The_effects_of_the_drought_on_vegetation_in_Morocco.jpg)

#### `temporal_pair2_agricultural_peak_canopy.jpg` — Agricultural Basin Follow-up (Peak Vegetative Bloom)
- **Satellite & Sensor:** Copernicus Sentinel-2 (ESA)
- **Spatial Resolution:** 10m GSD / Natural Color RGB
- **Feature Demonstrated:** Temporal Delta Matrix (After Follow-up - Peak Canopy Growth)
- **Description:** Vigorous green crop growth across agricultural parcels (detected as Green Afforestation/Growth Gain).
- **Credit & Attribution:** European Space Agency (ESA) / Copernicus Sentinel-2
- **License:** CC BY-SA 3.0 IGO
- **Source URL:** [Wikimedia Commons Archive](https://commons.wikimedia.org/wiki/File:Earth_from_Space-_Agricultural_patchwork_ESA524165.jpg)
