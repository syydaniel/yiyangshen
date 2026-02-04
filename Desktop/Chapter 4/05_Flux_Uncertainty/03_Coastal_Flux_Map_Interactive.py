"""
Interactive Coastal Flux Map Visualization
- Shows Level 12 coastal basins (COAST==1) on world map
- Dynamic flux calculation based on adjustable parameters
- Real-time map updates
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec
import geopandas as gpd
import os

plt.style.use('seaborn-v0_8-whitegrid')

BASE_DIR = r"c:\Users\syyda\Desktop\Chapter 4"
UNC_DIR = os.path.join(BASE_DIR, "05_Flux_Uncertainty")
PRIOR_SHAPE = os.path.join(UNC_DIR, "prior_shape_probs.csv")
PRIOR_POLY = os.path.join(UNC_DIR, "prior_poly_probs.csv")
LEV12_SHP = os.path.join(BASE_DIR, "BasinATLAS_v10_shp", "BasinATLAS_v10_lev12.shp")

DENSITIES = {
    'Poly_PE': 0.95, 'Poly_PP': 0.91, 'Poly_PS': 1.05,
    'Poly_PET': 1.38, 'Poly_PVC': 1.38, 'Poly_PA': 1.15,
    'Poly_PC': 1.20, 'Poly_PU': 1.20, 'Poly_PMMA': 1.18,
    'Poly_EPS': 0.05, 'Poly_Rayon': 1.50, 'Poly_CA': 1.30, 'Poly_XPS': 0.05
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


class FluxCalculator:
    def __init__(self):
        self.shape_probs, self.poly_probs = load_priors()
        self.densities = DENSITIES
    
    def sample_sizes(self, n, alpha, min_um, max_um):
        u = np.random.random(n)
        if abs(alpha - 1.0) < 0.01:
            return min_um * (max_um / min_um) ** u
        term1 = max_um ** (1 - alpha)
        term2 = min_um ** (1 - alpha)
        return ((term1 - term2) * u + term2) ** (1 / (1 - alpha))
    
    def calculate_volumes(self, sizes_um, shapes):
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
    
    def estimate_mean_mass(self, n, alpha, min_size, max_size):
        shapes = np.random.choice(list(self.shape_probs.keys()), size=n,
                                  p=list(self.shape_probs.values()))
        polymers = np.random.choice(list(self.poly_probs.keys()), size=n,
                                    p=list(self.poly_probs.values()))
        densities = np.array([self.densities.get(p, 1.0) for p in polymers])
        
        sizes = self.sample_sizes(n, alpha, min_size, max_size)
        volumes_um3 = self.calculate_volumes(sizes, shapes)
        volumes_cm3 = volumes_um3 * 1e-12
        masses_g = volumes_cm3 * densities
        
        return np.mean(masses_g)


def create_map_visualization():
    print("Loading coastal basins...")
    gdf = gpd.read_file(LEV12_SHP)
    coastal = gdf[gdf['COAST'] == 1].copy()
    print(f"Found {len(coastal)} coastal basins")
    
    # Use discharge as proxy for item flux (proportional distribution)
    total_discharge = coastal['dis_m3_pyr'].sum()
    coastal['flux_fraction'] = coastal['dis_m3_pyr'] / total_discharge
    
    # Total item flux placeholder
    TOTAL_ITEMS = 1e15  # items/yr
    coastal['item_flux'] = coastal['flux_fraction'] * TOTAL_ITEMS
    
    calc = FluxCalculator()
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[0.85, 0.15], hspace=0.3)
    
    ax_map = fig.add_subplot(gs[0, 0])
    ax_controls = fig.add_subplot(gs[1, 0])
    ax_controls.axis('off')
    
    # Load world background
    try:
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world.plot(ax=ax_map, color='lightgray', edgecolor='white', linewidth=0.5)
    except:
        print("World basemap not available, showing basins only")
    
    # Sliders
    slider_alpha = Slider(plt.axes([0.15, 0.10, 0.25, 0.02]), 'Size α',
                         1.5, 4.0, valinit=2.64)
    slider_min = Slider(plt.axes([0.15, 0.06, 0.25, 0.02]), 'Min Size (μm)',
                       10, 500, valinit=100, valstep=10)
    slider_max = Slider(plt.axes([0.15, 0.02, 0.25, 0.02]), 'Max Size (μm)',
                       500, 10000, valinit=5000, valstep=100)
    slider_n = Slider(plt.axes([0.55, 0.06, 0.25, 0.02]), 'MC Samples',
                     200, 3000, valinit=1000, valstep=100)
    
    # Color scheme slider (optional: for different quantiles)
    slider_quantile = Slider(plt.axes([0.55, 0.02, 0.25, 0.02]), 'Quantile',
                            0.05, 0.95, valinit=0.50, valstep=0.05)
    
    def update(val):
        alpha = slider_alpha.val
        min_s = slider_min.val
        max_s = slider_max.val
        n = int(slider_n.val)
        quantile = slider_quantile.val
        
        # Calculate mean mass for this parameter set
        print(f"Recalculating flux (α={alpha:.2f}, n={n})...")
        mean_mass = calc.estimate_mean_mass(n, alpha, min_s, max_s)
        
        # Calculate flux for each basin (kt/yr)
        coastal['mass_flux_kt'] = (coastal['item_flux'] * mean_mass / 1000.0) / 1e6
        
        # Clear and redraw
        ax_map.clear()
        
        # Background
        try:
            world.plot(ax=ax_map, color='lightgray', edgecolor='white', linewidth=0.5, alpha=0.3)
        except:
            pass
        
        # Plot coastal basins with flux-based colors
        coastal.plot(ax=ax_map, column='mass_flux_kt', cmap='YlOrRd',
                    legend=True, legend_kwds={'label': 'Flux (kt/yr)', 'shrink': 0.6},
                    edgecolor='black', linewidth=0.3, alpha=0.8)
        
        ax_map.set_xlim(-180, 180)
        ax_map.set_ylim(-60, 85)
        ax_map.set_title(f'Coastal Basin Flux Distribution | α={alpha:.2f}, Mean Mass={mean_mass*1000:.4f} mg',
                        fontsize=14, fontweight='bold')
        ax_map.set_xlabel('Longitude', fontsize=10)
        ax_map.set_ylabel('Latitude', fontsize=10)
        ax_map.grid(alpha=0.3)
        
        # Summary stats
        total_flux = coastal['mass_flux_kt'].sum()
        max_flux_basin = coastal.loc[coastal['mass_flux_kt'].idxmax()]
        
        stats_text = (
            f"Total Coastal Flux: {total_flux:.1f} kt/yr\\n"
            f"Max Basin Flux: {coastal['mass_flux_kt'].max():.2f} kt/yr (HYBAS_ID: {int(max_flux_basin['HYBAS_ID'])})\\n"
            f"Basins: {len(coastal)} | Quantile: P{int(quantile*100)}"
        )
        
        ax_map.text(0.02, 0.98, stats_text, transform=ax_map.transAxes,
                   va='top', ha='left', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))
        
        fig.canvas.draw_idle()
    
    # Connect sliders
    slider_alpha.on_changed(update)
    slider_min.on_changed(update)
    slider_max.on_changed(update)
    slider_n.on_changed(update)
    slider_quantile.on_changed(update)
    
    # Initial plot
    update(None)
    
    plt.show()


if __name__ == "__main__":
    print("="*60)
    print("Interactive Coastal Flux Map Visualization")
    print("="*60)
    create_map_visualization()
