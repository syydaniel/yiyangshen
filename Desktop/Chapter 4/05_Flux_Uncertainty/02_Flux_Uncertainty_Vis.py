"""
Interactive Microplastic Flux Uncertainty Visualization - Enhanced Version
- Level 12 HydroBasin coastal basins
- Monte Carlo quantile analysis (P5, P50, P95)
- 3D parameter space surface visualization
- Extrema identification
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import geopandas as gpd
import os

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 9

BASE_DIR = r"c:\Users\syyda\Desktop\Chapter 4"
UNC_DIR = os.path.join(BASE_DIR, "05_Flux_Uncertainty")
PRIOR_SHAPE = os.path.join(UNC_DIR, "prior_shape_probs.csv")
PRIOR_POLY = os.path.join(UNC_DIR, "prior_poly_probs.csv")
LEV12_SHP = os.path.join(BASE_DIR, "BasinATLAS_v10_shp", "BasinATLAS_v10_lev12.shp")

DENSITIES = {
    'Poly_PE': 0.95, 'Poly_PP': 0.91, 'Poly_PS': 1.05,
    'Poly_PET': 1.38, 'Poly_PVC': 1.38, 'Poly_PA': 1.15,
    'Poly_PC': 1.20, 'Poly_PU': 1.20, 'Poly_PMMA': 1.18,
    'Poly_EPS': 0.05, 'Poly_Rayon': 1.50, 'Poly_CA': 1.30,
    'Poly_XPS': 0.05
}

def load_and_filter_priors():
    shape_df = pd.read_csv(PRIOR_SHAPE, index_col=0, header=None, names=['Prob'])
    shape_df = shape_df[~shape_df.index.str.contains('Other', case=False, na=False)]
    shape_df = shape_df[shape_df['Prob'] > 0]  # Remove zeros
    shape_df['Prob'] = shape_df['Prob'] / shape_df['Prob'].sum()
    shape_df = shape_df.sort_values('Prob', ascending=False)  # Sort descending
    
    poly_df = pd.read_csv(PRIOR_POLY, index_col=0, header=None, names=['Prob'])
    poly_df = poly_df[~poly_df.index.str.contains('Other', case=False, na=False)]
    poly_df = poly_df.dropna()
    poly_df = poly_df[poly_df['Prob'] > 0]
    poly_df['Prob'] = poly_df['Prob'] / poly_df['Prob'].sum()
    poly_df = poly_df.sort_values('Prob', ascending=False)
    
    return shape_df, poly_df


class CoastalFluxSimulator:
    def __init__(self):
        shape_df, poly_df = load_and_filter_priors()
        self.shape_probs = shape_df['Prob'].to_dict()
        self.poly_probs = poly_df['Prob'].to_dict()
        self.densities = DENSITIES
        
        print("Loading Level 12 HydroBasin...")
        gdf = gpd.read_file(LEV12_SHP)
        self.coastal_basins = gdf[gdf['COAST'] == 1].copy()
        print(f"Found {len(self.coastal_basins)} river mouths")
        
        # Load Flux Data from Modeling File
        self.item_fluxes = None
        try:
            flux_path = os.path.join(BASE_DIR, "04_Flux_Analysis", "Flux_Data_Modeling.csv")
            if os.path.exists(flux_path):
                print("Loading Flux_Data_Modeling.csv...")
                df = pd.read_csv(flux_path)
                if 'Flux_Linear' in df.columns:
                    # Flux_Linear is likely items/sec (need to verify unit based on context, 
                    # usually river flux models are m3/s or items/s or items/day). 
                    # Assuming items/sec -> items/year: * 31536000
                    # Based on previous tasks it was implicitly items/s
                    self.item_fluxes = df['Flux_Linear'].values * 31536000
                    self.total_item_flux_yr = np.sum(self.item_fluxes)
                    print(f"Loaded Total Item Flux: {self.total_item_flux_yr:.2e} items/yr")
                else:
                    print("Column 'Flux_Linear' not found. Using default.")
                    self.total_item_flux_yr = 1e15
            else:
                 print(f"File not found: {flux_path}. Using default.")
                 self.total_item_flux_yr = 1e15
        except Exception as e:
            print(f"Error loading flux data: {e}, using default.")
            self.total_item_flux_yr = 1e15
    
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
    
    def run_monte_carlo(self, n, alpha, min_size, max_size):
        shapes = np.random.choice(list(self.shape_probs.keys()), size=n,
                                  p=list(self.shape_probs.values()))
        polymers = np.random.choice(list(self.poly_probs.keys()), size=n,
                                    p=list(self.poly_probs.values()))
        densities = np.array([self.densities.get(p, 1.0) for p in polymers])
        
        sizes = self.sample_sizes(n, alpha, min_size, max_size)
        volumes_um3 = self.calculate_volumes(sizes, shapes)
        volumes_cm3 = volumes_um3 * 1e-12
        masses_g = volumes_cm3 * densities
        
        # Calculate quantiles
        p5 = np.percentile(masses_g, 5)
        p50 = np.percentile(masses_g, 50)
        p95 = np.percentile(masses_g, 95)
        
        return masses_g, {'P5': p5, 'P50': p50, 'P95': p95}
    
    def estimate_flux(self, mean_mass_g):
        total_kg_yr = self.total_item_flux_yr * mean_mass_g / 1000.0
        return total_kg_yr / 1e6  # Kilotons/yr
    
    def compute_surface(self, alpha_range, min_range, quantile_func):
        """Compute flux surface for given parameter ranges and quantile"""
        A, M = np.meshgrid(alpha_range, min_range)
        Z = np.zeros_like(A)
        
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                _, quants = self.run_monte_carlo(500, A[i,j], M[i,j], 5000)
                Z[i,j] = self.estimate_flux(quantile_func(quants))
        
        return A, M, Z


def create_interactive_vis():
    sim = CoastalFluxSimulator()
    
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(4, 3, height_ratios=[0.08, 0.25, 0.35, 0.32],
                          hspace=0.4, wspace=0.35)
    
    # Title
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5,
                 f"Flux Uncertainty (Level 12) | {len(sim.coastal_basins)} Mouths | Quantile Analysis",
                 ha='center', va='center', fontsize=13, fontweight='bold')
    
    # Row 1: Priors
    ax_shape = fig.add_subplot(gs[1, 0])
    ax_polymer = fig.add_subplot(gs[1, 1])
    ax_size = fig.add_subplot(gs[1, 2])
    
    # Row 2: Item Flux (New) + Mass Flux + Results
    ax_item = fig.add_subplot(gs[2, 0])
    ax_mass = fig.add_subplot(gs[2, 1]) # Reduced span
    ax_results = fig.add_subplot(gs[2, 2])
    
    plt.subplots_adjust(top=0.9) # Adjust spacing

    # Plot Item Flux Histogram (Static Input)
    if sim.item_fluxes is not None:
        valid_fluxes = sim.item_fluxes[sim.item_fluxes > 0]
        if len(valid_fluxes) > 0:
            ax_item.hist(np.log10(valid_fluxes), bins=40, color='purple', alpha=0.7, edgecolor='black')
            ax_item.set_title('Global Item Flux (Input)', fontweight='bold', fontsize=10)
            ax_item.set_xlabel('Log10(items/yr)', fontsize=8)
            ax_item.set_ylabel('Basin Count', fontsize=8)
            
            # Show Total Sum
            ax_item.text(0.95, 0.95, f"Total:\\n{sim.total_item_flux_yr:.1e}\\nitems/yr", 
                         transform=ax_item.transAxes, ha='right', va='top', fontsize=8,
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, ec='none'))
        else:
             ax_item.text(0.5, 0.5, "No positive flux data", ha='center', fontsize=9)
    else:
        ax_item.text(0.5, 0.5, "Item Data Not Loaded", ha='center', fontsize=9)
    ax_item.grid(alpha=0.3)
    
    # Row 3: 3D Surfaces (P5, P50, P95)
    ax_surf_p5 = fig.add_subplot(gs[3, 0], projection='3d')
    ax_surf_p50 = fig.add_subplot(gs[3, 1], projection='3d')
    ax_surf_p95 = fig.add_subplot(gs[3, 2], projection='3d')
    
    # Plot sorted priors
    shape_series = pd.Series(sim.shape_probs)
    shape_series.plot(kind='bar', ax=ax_shape, color='steelblue', alpha=0.7)
    ax_shape.set_title('Shape (sorted)', fontweight='bold', fontsize=10)
    ax_shape.tick_params(axis='x', rotation=45, labelsize=7)
    ax_shape.set_ylabel('Probability', fontsize=8)
    
    poly_series = pd.Series(sim.poly_probs)
    poly_series.plot(kind='bar', ax=ax_polymer, color='seagreen', alpha=0.7)
    ax_polymer.set_title('Polymer (sorted)', fontweight='bold', fontsize=10)
    ax_polymer.tick_params(axis='x', rotation=45, labelsize=7)
    ax_polymer.set_ylabel('Probability', fontsize=8)
    
    # Sliders
    slider_alpha = Slider(plt.axes([0.15, 0.04, 0.25, 0.015]), 'α',
                         1.5, 4.0, valinit=2.64)
    slider_min = Slider(plt.axes([0.15, 0.02, 0.25, 0.015]), 'Min μm',
                       10, 500, valinit=100, valstep=10)
    slider_n = Slider(plt.axes([0.55, 0.03, 0.25, 0.015]), 'Samples',
                     1000, 10000, valinit=3000, valstep=500)
    
    # Pre-compute surfaces (this takes time, do once)
    print("Computing parameter surfaces...")
    alpha_grid = np.linspace(2.0, 3.5, 8)
    min_grid = np.linspace(50, 300, 8)
    
    surfaces = {}
    for q_name, q_func in [('P5', lambda q: q['P5']), 
                           ('P50', lambda q: q['P50']), 
                           ('P95', lambda q: q['P95'])]:
        print(f"  Computing {q_name} surface...")
        A, M, Z = sim.compute_surface(alpha_grid, min_grid, q_func)
        surfaces[q_name] = (A, M, Z)
    
    def update(val):
        alpha, min_s, n = slider_alpha.val, slider_min.val, int(slider_n.val)
        
        # Size distribution
        ax_size.clear()
        x = np.linspace(min_s, 5000, 1000)
        y = (x ** (-alpha)) / np.max(x ** (-alpha))
        ax_size.plot(x, y, 'r-', linewidth=2)
        ax_size.fill_between(x, y, alpha=0.2, color='red')
        ax_size.set_title(f'Size (α={alpha:.2f})', fontweight='bold', fontsize=10)
        ax_size.set_xlabel('μm', fontsize=8)
        ax_size.set_xscale('log')
        ax_size.grid(alpha=0.3)
        
        # Monte Carlo with quantiles
        masses, quants = sim.run_monte_carlo(n, alpha, min_s, 5000)
        
        # Mass distribution
        ax_mass.clear()
        ax_mass.hist(np.log10(masses * 1000 + 1e-12), bins=60,
                    color='skyblue', edgecolor='black', alpha=0.6, density=True)
        
        # Add quantile lines
        for q_name, q_val in quants.items():
            color = {'P5': 'blue', 'P50': 'green', 'P95': 'red'}[q_name]
            ax_mass.axvline(np.log10(q_val * 1000), color=color,
                           linestyle='--', linewidth=1.5, label=f'{q_name}: {q_val*1000:.4f} mg')
        
        ax_mass.set_title('Particle Mass Distribution', fontweight='bold', fontsize=10)
        ax_mass.set_xlabel('Log₁₀(mg)', fontsize=8)
        ax_mass.set_ylabel('Density', fontsize=8)
        ax_mass.legend(fontsize=7, loc='upper left')
        ax_mass.grid(alpha=0.3)
        
        # Results table
        ax_results.clear()
        ax_results.axis('off')
        
        flux_p5 = sim.estimate_flux(quants['P5'])
        flux_p50 = sim.estimate_flux(quants['P50'])
        flux_p95 = sim.estimate_flux(quants['P95'])
        
        results_text = (
            f"Quantile Analysis (n={n})\\n"
            f"{'='*30}\\n"
            f"P5  (5%):  {flux_p5:>8.1f} kt/yr\\n"
            f"P50 (50%): {flux_p50:>8.1f} kt/yr\\n"
            f"P95 (95%): {flux_p95:>8.1f} kt/yr\\n"
            f"{'='*30}\\n"
            f"Range: {flux_p95-flux_p5:.1f} kt/yr\\n"
            f"Ratio: {flux_p95/flux_p5:.2f}x"
        )
        
        ax_results.text(0.1, 0.5, results_text, transform=ax_results.transAxes,
                       va='center', fontsize=9, family='monospace',
                       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # Update surfaces
        for ax_surf, q_name, color in [(ax_surf_p5, 'P5', 'Blues'),
                                       (ax_surf_p50, 'P50', 'Greens'),
                                       (ax_surf_p95, 'P95', 'Reds')]:
            ax_surf.clear()
            A, M, Z = surfaces[q_name]
            
            surf = ax_surf.plot_surface(A, M, Z, cmap=color, alpha=0.7,
                                       edgecolor='none', antialiased=True)
            
            # Find extrema
            idx_min = np.unravel_index(np.argmin(Z), Z.shape)
            idx_max = np.unravel_index(np.argmax(Z), Z.shape)
            
            # Mark extrema
            ax_surf.scatter([A[idx_max]], [M[idx_max]], [Z[idx_max]],
                          color='red', s=100, marker='^', label=f'Max: {Z[idx_max]:.0f}')
            ax_surf.scatter([A[idx_min]], [M[idx_min]], [Z[idx_min]],
                          color='blue', s=100, marker='v', label=f'Min: {Z[idx_min]:.0f}')
            
            # Mark current point
            current_flux = sim.estimate_flux(quants[q_name])
            ax_surf.scatter([alpha], [min_s], [current_flux],
                          color='yellow', s=80, marker='o', edgecolors='black', linewidths=2, label='Current')

            
            ax_surf.set_xlabel('α', fontsize=8)
            ax_surf.set_ylabel('Min (μm)', fontsize=8)
            ax_surf.set_zlabel('kt/yr', fontsize=8)
            ax_surf.set_title(f'{q_name} Surface', fontweight='bold', fontsize=10)
            ax_surf.legend(fontsize=6, loc='upper left')
            ax_surf.view_init(elev=25, azim=-60)
        
        fig.canvas.draw_idle()
    
    slider_alpha.on_changed(update)
    slider_min.on_changed(update)
    slider_n.on_changed(update)
    
    update(None)
    plt.show()


if __name__ == "__main__":
    print("="*60)
    print("Enhanced Flux Visualization | Quantile + Surface Analysis")
    print("="*60)
    create_interactive_vis()
