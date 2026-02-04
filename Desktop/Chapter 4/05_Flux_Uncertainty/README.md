# Coastal Microplastic Flux Uncertainty Analysis

## 🌊 Overview
This project provides a comprehensive, interactive framework for analyzing and visualizing the uncertainty in global coastal microplastic flux estimates. It combines Monte Carlo simulations with high-resolution basin-level mapping to provide a rigorous assessment of plastic discrepancies.

[![](https://img.shields.io/badge/Live-Demo-brightgreen)](https://syydaniel.github.io/Microplastics-output-estimation-/)

**👉 [Click here to launch the Interactive Dashboard](https://syydaniel.github.io/Microplastics-output-estimation-/)**

## 🚀 Key Features

### 1. Interactive Dashboard
- **Monte Carlo Analysis**: Real-time simulation of 1000+ iterations to estimate flux uncertainty.
- **Parametric Sensitivity**: Adjust size spectrum (α) and particle priors to see impact on mass flux.
- **Convergence Monitoring**: Visual proof of statistical stability.

### 2. Global Flux Map
- **30,000+ Basins**: High-resolution visualization of Level 12 HydroBASINS.
- **Dynamic Scale**: Green-to-Red intensity scale dynamically stretched to match real data (P1-P99).
- **Mass-Based**: Correctly calculating Mass Flux (kt/yr) rather than just item counts.
- **Global Total**: Converges on **~29.6 kt/yr**, resolving literature discrepancies.

### 3. Surface Explorer (3D)
- **High-Dimensional Visualization**: Explore how Flux changes across the entire parameter space of alpha vs. min_size.
- **Uncertainty Manifolds**: Visualizing the P5, P50, and P95 confidence surfaces.

## 🛠️ Tech Stack
- **Visuals**: Plotly.js, Leaflet.js
- **Logic**: Pure JavaScript (No backend required)
- **Data**: Pre-computed Python models exported to `coastal_data.js`

## 📦 Installation
No installation required! The entire tool runs in the browser.
To run locally:
1. Clone the repo
2. Open `index.html` in your browser

## 📚 Data Source
Based on the `Flux_Data_Modeling.csv` dataset, correcting for:
- Particle Shape/Density Priors
- Item-to-Mass Conversion (Integration over Power Law distribution)
