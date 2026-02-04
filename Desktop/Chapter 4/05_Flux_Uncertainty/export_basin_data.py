"""
Export Level 12 coastal basin data to JSON for HTML map visualization
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import json
import os

BASE_DIR = r"c:\Users\syyda\Desktop\Chapter 4"
UNC_DIR = os.path.join(BASE_DIR, "05_Flux_Uncertainty")
LEV12_SHP = os.path.join(BASE_DIR, "BasinATLAS_v10_shp", "BasinATLAS_v10_lev12.shp")
PRIOR_SHAPE = os.path.join(UNC_DIR, "prior_shape_probs.csv")
PRIOR_POLY = os.path.join(UNC_DIR, "prior_poly_probs.csv")

DENSITIES = {
    'Poly_PE': 0.95, 'Poly_PP': 0.91, 'Poly_PS': 1.05,
    'Poly_PET': 1.38, 'Poly_PVC': 1.38, 'Poly_PA': 1.15,
}

def load_priors():
    shape_df = pd.read_csv(PRIOR_SHAPE, index_col=0, header=None, names=['Prob'])
    shape_df = shape_df[~shape_df.index.str.contains('Other', case=False, na=False)]
    shape_df = shape_df[shape_df['Prob'] > 0]
    shape_df['Prob'] = shape_df['Prob'] / shape_df['Prob'].sum()
    
    poly_df = pd.read_csv(PRIOR_POLY, index_col=0, header=None, names=['Prob'])
    poly_df = poly_df[~poly_df.index.str.contains('Other', case=False, na=False)]
    poly_df = poly_df.dropna()
    poly_df = poly_df[poly_df['Prob'] > 0]
    poly_df['Prob'] = poly_df['Prob'] / poly_df['Prob'].sum()
    
    return shape_df['Prob'].to_dict(), poly_df['Prob'].to_dict()

def sample_sizes(n, alpha, min_um, max_um):
    u = np.random.random(n)
    if abs(alpha - 1.0) < 0.01:
        return min_um * (max_um / min_um) ** u
    term1 = max_um ** (1 - alpha)
    term2 = min_um ** (1 - alpha)
    return ((term1 - term2) * u + term2) ** (1 / (1 - alpha))

def calculate_volumes(sizes_um, shapes):
    volumes = np.zeros_like(sizes_um)
    mask_fiber = (shapes == 'Shape_Fiber')
    L = sizes_um[mask_fiber]
    D = L / 10.0
    volumes[mask_fiber] = np.pi * (D/2)**2 * L
    
    mask_sphere = np.isin(shapes, ['Shape_Fragment', 'Shape_Pellet'])
    D = sizes_um[mask_sphere]
    volumes[mask_sphere] = (4/3) * np.pi * (D/2)**3
    
    mask_film = (shapes == 'Shape_Film')
    D = sizes_um[mask_film]
    volumes[mask_film] = D**2 * 20.0
    
    return volumes

def estimate_mean_mass(shape_probs, poly_probs, n, alpha, min_size, max_size):
    shapes = np.random.choice(list(shape_probs.keys()), size=n, p=list(shape_probs.values()))
    polymers = np.random.choice(list(poly_probs.keys()), size=n, p=list(poly_probs.values()))
    densities = np.array([DENSITIES.get(p, 1.0) for p in polymers])
    
    sizes = sample_sizes(n, alpha, min_size, max_size)
    volumes_um3 = calculate_volumes(sizes, shapes)
    volumes_cm3 = volumes_um3 * 1e-12
    masses_g = volumes_cm3 * densities
    
    return np.mean(masses_g)

def export_coastal_data():
    print("Loading Level 12 coastal basins...")
    gdf = gpd.read_file(LEV12_SHP)
    
    # 1. Filter for Coastal Basins (COAST == 1)
    coastal = gdf[gdf['COAST'] == 1].copy()
    print(f"Found {len(coastal)} coastal basins in shapefile.")
    
    # 2. Load Filter/Data from Flux_Data_Modeling.csv
    flux_file = os.path.join(BASE_DIR, "04_Flux_Analysis", "Flux_Data_Modeling.csv")
    if not os.path.exists(flux_file):
        print(f"Error: Modeling file not found: {flux_file}")
        return

    print("Loading Flux_Data_Modeling.csv...")
    try:
        # Load specific columns to save memory
        model_df = pd.read_csv(flux_file, usecols=['HYBAS_ID', 'Flux_Linear', 'Natural_Discharge_Upstream', 'Conc_Linear'])
        
        # Ensure ID is correct type for merging
        model_df['HYBAS_ID'] = model_df['HYBAS_ID'].astype(int)
        
        # Filter coastal basins to keep ONLY those present in the modeling file
        # Inner join will drop any shapefile basins not in the model file
        merged = coastal.merge(model_df, on='HYBAS_ID', how='inner')
        print(f"Filtered to {len(merged)} basins matching Flux_Data_Modeling.csv whitelist.")
        
        # 3. Prepare Data for Export
        # Calculate Mean Mass per Particle (g) based on Priors (Default Alpha=2.64)
        shape_probs, poly_probs = load_priors()
        print("Calculating mean particle mass (α=2.64) for mass conversion...")
        mean_mass_g = estimate_mean_mass(shape_probs, poly_probs, 5000, 2.64, 100, 5000)
        print(f"Mean particle mass: {mean_mass_g:.6e} g")

        # Convert Flux_Linear (items/s) to Mass Flux (kt/yr)
        # 1. items/s -> items/yr
        # 2. items/yr * g/item = g/yr
        # 3. g/yr / 1e9 = kt/yr
        SECONDS_PER_YEAR = 31536000.0
        
        merged['items_per_sec'] = merged['Flux_Linear']
        merged['items_per_yr'] = merged['items_per_sec'] * SECONDS_PER_YEAR
        merged['flux_kt'] = (merged['items_per_yr'] * mean_mass_g) / 1e9
        
        # Low flux filtration (optional, but keeps file size down if needed)
        # merged = merged[merged['flux_kt'] > 1e-6] 

        # Discharge: Natural_Discharge_Upstream is likely m3/s. 
        # Convert to m3/yr for display
        merged['discharge_m3yr'] = merged['Natural_Discharge_Upstream'] * SECONDS_PER_YEAR
        
        # Geometry
        merged['centroid'] = merged.geometry.centroid
        merged['lon'] = merged['centroid'].x
        merged['lat'] = merged['centroid'].y
        
        # Export List
        basin_data = []
        for idx, row in merged.iterrows():
            basin_data.append({
                'id': int(row['HYBAS_ID']),
                'lat': round(float(row['lat']), 4),
                'lon': round(float(row['lon']), 4),
                'discharge': float(row['discharge_m3yr']), # m3/yr
                'flux_baseline': float(row['flux_kt']),    # kt/yr (Corrected Mass)
                'flux_items': float(row['items_per_yr'])   # items/yr (Raw Count)
            })
            
        total_flux_kt = sum(b['flux_baseline'] for b in basin_data)
        total_items = sum(b['flux_items'] for b in basin_data)
        total_discharge = sum(b['discharge'] for b in basin_data)
        
        output_file = os.path.join(UNC_DIR, 'coastal_data.js')
        
        data_dict = {
            'total_basins': len(basin_data),
            'total_discharge': total_discharge,
            'total_flux_kt': total_flux_kt, 
            'total_items_yr': total_items,
            'source': "Flux_Data_Modeling.csv (filtered) converted to Mass",
            'basins': basin_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"window.COASTAL_DATA = {json.dumps(data_dict)};")
        
        print(f"\\nExported {len(basin_data)} basins to {output_file}")
        print(f"Total Flux: {total_flux_kt:.2f} kt/yr")
        print(f"Total Items: {total_items:.2e} items/yr")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_coastal_data()
