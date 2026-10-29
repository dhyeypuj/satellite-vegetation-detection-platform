# Satellite Vegetation Detection & Canopy Health Platform (v2.1)
### Advanced Vegetation Detection, Carbon Sequestration, Temporal Deforestation Tracking, CIR Satellite Simulation, & GIS Landscape Ecology Suite

---

## 📌 Project Overview

The **Vegetation Detection Platform (v2.1)** is an end-to-end computer vision and remote sensing platform designed to analyze high-resolution satellite imagery across visible spectral bands using pure, deterministic mathematical models and OpenCV algorithms.

Beyond basic edge detection filters (such as Sobel operators), the platform integrates multi-spectral chromaticity indices, automated real-world Ground Sampling Distance (GSD) area estimation, IPCC Tier-1 carbon biomass sequestration calculations, 3-tier physiological canopy vigor grading, landscape patch fragmentation morphology, Color-Infrared (CIR) false-color simulation, sub-quadrant ROI sector slicing, and pixel-wise temporal change tracking (deforestation and afforestation monitoring).

---

## 🔬 Scientific Methodologies & Mathematical Formulations

Standard visible-band RGB satellite imagery lacks Near-Infrared (NIR) channels required for traditional satellite NDVI ($\frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$). To resolve this, the platform utilizes chromaticity-normalized spectral indices:

$$r = \frac{R}{R + G + B}, \quad g = \frac{G}{R + G + B}, \quad b = \frac{B}{R + G + B}$$

### 1. HSV Color Space Segmentation
* **Principle**: Decouples chromaticity from illumination by transforming BGR to Hue-Saturation-Value space.
* **Spectral Range**: Green spectrum $H \in [25, 95]$ (OpenCV scale $0\text{--}180$), $S \ge 30$, $V \ge 30$.

### 2. Excess Green Index (ExG)
* **Formula**:
  $$\text{ExG} = 2g - r - b = \frac{2G - R - B}{R + G + B}$$
* **Application**: Isolates chlorophyll absorption peaks in the green channel while suppressing dark shadows and asphalt.

### 3. Excess Green Minus Excess Red (ExGR)
* **Formula**:
  $$\text{ExGR} = \text{ExG} - (1.4r - g) = 3g - 2.4r - b$$
* **Application**: Eliminates false positives from reddish-brown bare soils, sand, and dead foliage.

### 4. Visible Atmospherically Resistant Index (VARI)
* **Formula**:
  $$\text{VARI} = \frac{G - R}{G + R - B}$$
* **Application**: Formulated specifically for satellite imagery to mitigate atmospheric aerosol scattering effects in the visible spectrum.

### 5. Green Leaf Index (GLI)
* **Formula**:
  $$\text{GLI} = \frac{2G - R - B}{2G + R + B}$$
* **Application**: Normalized chlorophyll reflectance metric $[-1, 1]$ directly correlated with canopy density and Leaf Area Index (LAI).

### 6. Sobel Gradient Edge Detection (Baseline)
* **Formula**:
  $$|G| = \sqrt{G_x^2 + G_y^2} \quad \text{where } G_x = \begin{bmatrix}-1&0&1\\-2&0&2\\-1&0&1\end{bmatrix}*I, \; G_y = \begin{bmatrix}-1&-2&-1\\0&0&0\\1&2&1\end{bmatrix}*I$$
* **Application**: Serves as a baseline to demonstrate the structural limitations of texture filtering vs. true spectral segmentation.

---

## 🌟 Advanced Platform Features (100% Deterministic & Non-ML)

### 🌳 1. Carbon Stock & $CO_2$ Sequestration Calculator (IPCC Tier-1)
* **Mathematical Derivations**:
  - $\text{Aboveground Biomass (Tons)} = \text{Canopy Area (ha)} \times 140\text{ tons/ha}$
  - $\text{Carbon Stock (Tons)} = \text{Biomass} \times 0.47$ (IPCC standard carbon fraction)
  - $\text{Total } CO_2e \text{ Sequestered} = \text{Carbon Stock} \times \frac{44}{12} \approx \text{Carbon Stock} \times 3.667$
  - $\text{Annual Passenger Vehicles Offset} = \frac{tCO_2e}{4.6\text{ tCO}_2/\text{yr}}$

### 🛰️ 2. Color-Infrared (CIR False-Color) Satellite Composite Simulator
* **Pure Matrix Transformation**:
  $$\text{NIR}_{\text{estimated}} = \text{clip}(2.2G - 0.6R, 0, 255)$$
  $$\text{Red Output} \leftarrow \text{NIR}_{\text{estimated}}, \quad \text{Green Output} \leftarrow R, \quad \text{Blue Output} \leftarrow G$$
* **Application**: Standard aerospace remote sensing false-color palette where active chlorophyll reflects in vibrant ruby red, water in dark navy, and bare soil in cyan/gray.

### 🔍 3. Sub-Sector ROI Quadrant Slicer
* **Array Slicing**: Slices scene into 5 geographic sectors:
  - North-West (Top-Left), North-East (Top-Right), South-West (Bottom-Left), South-East (Bottom-Right), and Central Core Zone.
* **Output**: Instant localized canopy area ($ha$), pixel count, and coverage percentage per sector.

### 🔄 4. Temporal Change Detection & Deforestation Tracker
* **Algorithm**: Computes pixel-wise differential Boolean operations between co-registered temporal scenes ($M_1$ and $M_2$):
  - **Deforestation / Canopy Loss**: $M_1 \land \neg M_2$ $\rightarrow$ **Vibrant Red** (`#EF4444`)
  - **Reforestation / Biomass Gain**: $\neg M_1 \land M_2$ $\rightarrow$ **Vibrant Green** (`#10B981`)
  - **Persistent Canopy**: $M_1 \land M_2$ $\rightarrow$ **Deep Forest Green** (`#166534`)
  - **Persistent Non-Vegetation**: $\neg M_1 \land \neg M_2$ $\rightarrow$ Grayscale reference background
* **Output**: Quantitative net delta percentage ($\Delta\%$) and hectares lost vs. gained.

### 🌿 5. Multi-Tier Canopy Health & Physiological Vigor Classification
* **Classification Criteria**:
  - **Tier 1 (High Vigor / Dense Canopy)**: $\text{GLI} \ge 0.12$ (Deep Emerald Green)
  - **Tier 2 (Moderate Vigor / Grassland & Shrubs)**: $0.02 \le \text{GLI} < 0.12$ (Vibrant Lime Green)
  - **Tier 3 (Stressed / Dry / Senescent Canopy)**: $\text{GLI} < 0.02$ (Amber / Gold)
* **Composite Health Index**: Weighted canopy vigor score ($0\text{--}100$).

### 🧩 6. Landscape Canopy Patch & Fragmentation Analysis
* **Morphology**: Employs 8-connectivity `cv2.connectedComponentsWithStats` to identify discrete vegetation patches.
* **Metrics**: Total discrete patch count, largest continuous core cluster area, mean patch area, and perimeter-to-area fragmentation ratio.
* **Visualization**: Interactive bounding boxes and labels numbered over the top 10 largest clusters.

### 📐 7. Real-World Geographic Area Scaling (GSD Calibration)
* **Presets**: Sentinel-2 ($10\text{ m/px}$), PlanetScope ($3\text{ m/px}$), Drone UAV ($0.1\text{--}0.5\text{ m/px}$), Landsat-8 ($30\text{ m/px}$), or Custom GSD.
* **Output Units**: Exact conversion to **Square Meters ($m^2$)**, **Hectares ($ha$)**, **Square Kilometers ($km^2$)**, and **Acres**.

### 📦 8. One-Click Complete Project Export Bundle (ZIP Archive)
* Downloads a complete `.zip` package (`/api/export_zip`) containing all high-resolution masks, overlays, CIR composite, density heatmaps, and CSV tables.

---

## 🏗️ System Architecture

```
ET401 P1/
│
├── vegetation_detector.py         # Core OpenCV engine (6 methods, density map, health, patches, temporal change, carbon, CIR, quadrants)
├── app.py                        # Flask REST API server (v2.1 PRO)
├── requirements.txt              # Project dependencies
├── README.md                     # Comprehensive technical documentation
│
└── static/
    ├── index.html                # Modern 6-tab dashboard UI & report modal
    ├── style.css                 # Glassmorphic dark theme & print stylesheet
    └── app.js                    # Asynchronous client-side state engine & visualizers
```

---

## 🚀 Quick Start Guide

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Launching the Web Dashboard
```powershell
python app.py
```
Open **`http://localhost:5000`** in your browser.

### 3. Command-Line Batch Processing
```powershell
python vegetation_detector.py --image <path_to_image.jpg> --output-dir output_results
```

---

## 👤 Author & Academic Context
* **Student**: Dhyey Pujara (BT23GCS150)
* **Course**: ET401 P1 Project
* **Tech Stack**: Python, OpenCV, Flask, NumPy, Pandas, HTML5/CSS3/JavaScript
