"""
Enhanced Coastal Flux Uncertainty Explorer
===========================================
Comprehensive Monte Carlo analysis with:
- Prior distribution sensitivity
- Preset scenarios
- Convergence monitoring
- Detailed annotations
- Auto-generated results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import geopandas as gpd
import json
import os

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 8

BASE_DIR = r"c:\Users\syyda\Desktop\Chapter 4"
UNC_DIR = os.path.join(BASE_DIR, "05_Flux_Uncertainty")
PRIOR_SHAPE = os.path.join(UNC_DIR, "prior_shape_probs.csv")
PRIOR_POLY = os.path.join(UNC_DIR, "prior_poly_probs.csv")
LEV12_SHP = os.path.join(BASE_DIR, "BasinATLAS_v10_shp", "BasinATLAS_v10_lev12.shp")
PRESETS_FILE = os.path.join(UNC_DIR, "config_presets.json")

# Load presets
with open(PRESETS_FILE, 'r') as f:
    CONFIG = json.load(f)

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
    shape_df = shape_df.sort_values('Prob', ascending=False)
    
    poly_df = pd.read_csv(PRIOR_POLY, index_col=0, header=None, names=['Prob'])
    poly_df = poly_df[~poly_df.index.str.contains('Other', case=False, na=False)]
    poly_df = poly_df.dropna()
    poly_df = poly_df[poly_df['Prob'] > 0]
    poly_df['Prob'] = poly_df['Prob'] / poly_df['Prob'].sum()
    poly_df = poly_df.sort_values('Prob', ascending=False)
    
    return shape_df, poly_df


class EnhancedFluxSimulator:
    def __init__(self):
        shape_df, poly_df = load_priors()
        self.shape_probs_original = shape_df['Prob'].to_dict()
        self.poly_probs_original = poly_df['Prob'].to_dict()
        self.shape_probs = self.shape_probs_original.copy()
        self.poly_probs = self.poly_probs_original.copy()
        self.densities = DENSITIES
        
        gdf = gpd.read_file(LEV12_SHP)
        self.coastal_basins = gdf[gdf['COAST'] == 1].copy()
        
        # Load Flux Data
        self.item_fluxes = None
        try:
            flux_path = os.path.join(BASE_DIR, "04_Flux_Analysis", "Flux_Data_Modeling.csv")
            if os.path.exists(flux_path):
                print("Loading Flux_Data_Modeling.csv...")
                df = pd.read_csv(flux_path)
                if 'Flux_Linear' in df.columns:
                    self.item_fluxes = df['Flux_Linear'].values * 31536000
                    self.total_item_flux_yr = np.sum(self.item_fluxes)
                    print(f"Loaded Total Item Flux: {self.total_item_flux_yr:.2e} items/yr")
                else:
                    self.total_item_flux_yr = 1e15
            else:
                 self.total_item_flux_yr = 1e15
        except Exception as e:
            print(f"Error loading flux data: {e}, using default.")
            self.total_item_flux_yr = 1e15
        
        print(f"Loaded {len(self.coastal_basins)} coastal basins")
    
    def reset_priors(self):
        self.shape_probs = self.shape_probs_original.copy()
        self.poly_probs = self.poly_probs_original.copy()
    
    def adjust_prior(self, category, factor, prior_type='shape'):
        """Adjust a single category's probability by factor, renormalize"""
        if prior_type == 'shape':
            if category in self.shape_probs:
                self.shape_probs[category] *= factor
                total = sum(self.shape_probs.values())
                self.shape_probs = {k: v/total for k, v in self.shape_probs.items()}
        else:
            if category in self.poly_probs:
                self.poly_probs[category] *= factor
                total = sum(self.poly_probs.values())
                self.poly_probs = {k: v/total for k, v in self.poly_probs.items()}
    
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
    
    def run_monte_carlo_with_convergence(self, n, alpha, min_size, max_size):
        """Run MC and track convergence"""
        shapes = np.random.choice(list(self.shape_probs.keys()), size=n,
                                  p=list(self.shape_probs.values()))
        polymers = np.random.choice(list(self.poly_probs.keys()), size=n,
                                    p=list(self.poly_probs.values()))
        densities = np.array([self.densities.get(p, 1.0) for p in polymers])
        
        sizes = self.sample_sizes(n, alpha, min_size, max_size)
        volumes_um3 = self.calculate_volumes(sizes, shapes)
        volumes_cm3 = volumes_um3 * 1e-12
        masses_g = volumes_cm3 * densities
        
        # Calculate running mean for convergence
        running_mean = np.cumsum(masses_g) / np.arange(1, n+1)
        
        # Quantiles
        p5 = np.percentile(masses_g, 5)
        p50 = np.percentile(masses_g, 50)
        p95 = np.percentile(masses_g, 95)
        
        return masses_g, {'P5': p5, 'P50': p50, 'P95': p95, 'mean': np.mean(masses_g)}, running_mean
    
    def estimate_flux(self, mean_mass_g):
        total_kg_yr = self.total_item_flux_yr * mean_mass_g / 1000.0
        return total_kg_yr / 1e6


def create_enhanced_explorer():
    sim = EnhancedFluxSimulator()
    
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(5, 4, height_ratios=[0.05, 0.24, 0.28, 0.12, 0.31],
                          hspace=0.35, wspace=0.35)
    
    # Title
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, "Coastal Microplastic Flux - Comprehensive Uncertainty Explorer",
                 ha='center', va='center', fontsize=15, fontweight='bold')
    
    # Row 1: Priors + Size + Convergence
    ax_shape = fig.add_subplot(gs[1, 0])
    ax_polymer = fig.add_subplot(gs[1, 1])
    ax_size = fig.add_subplot(gs[1, 2])
    ax_convergence = fig.add_subplot(gs[1, 3])
    
    # Row 1: Priors + Size + Convergence
    ax_shape = fig.add_subplot(gs[1, 0])
    ax_polymer = fig.add_subplot(gs[1, 1])
    ax_size = fig.add_subplot(gs[1, 2])
    ax_convergence = fig.add_subplot(gs[1, 3])
    
    # Row 2: Item Flux (New) + Mass Flux + Results
    # gs has 4 columns.
    # Item Flux: Col 0
    # Mass Flux: Col 1-2
    # Results: Col 3
    ax_item = fig.add_subplot(gs[2, 0])
    ax_mass = fig.add_subplot(gs[2, 1:3])
    ax_results = fig.add_subplot(gs[2, 3])

    # Plot Item Flux
    if sim.item_fluxes is not None:
        valid_fluxes = sim.item_fluxes[sim.item_fluxes > 0]
        if len(valid_fluxes) > 0:
            ax_item.hist(np.log10(valid_fluxes), bins=40, color='purple', alpha=0.7, edgecolor='black')
            ax_item.set_title('Item Flux (Input)', fontweight='bold', fontsize=9)
            ax_item.set_xlabel('Log10(items/yr)', fontsize=8)
            ax_item.set_ylabel('Frequency', fontsize=8)
            ax_item.text(0.95, 0.95, f"Total:\\n{sim.total_item_flux_yr:.1e}", 
                         transform=ax_item.transAxes, ha='right', va='top', fontsize=7,
                         bbox=dict(fc='white', alpha=0.7, ec='none'))
        else:
             ax_item.text(0.5, 0.5, "No positive data", ha='center')
    else:
        ax_item.text(0.5, 0.5, "Data Not Loaded", ha='center')
    ax_item.grid(alpha=0.3)
    
    # Row 3: Preset buttons (dedicated row)
    ax_button_row = fig.add_subplot(gs[3, :])
    ax_button_row.axis('off')
    
    # Row 4: 3D Surfaces
    ax_surf_mean = fig.add_subplot(gs[4, :2], projection='3d')
    ax_surf_p50 = fig.add_subplot(gs[4, 2], projection='3d')
    ax_surf_range = fig.add_subplot(gs[4, 3], projection='3d')
    
    # Plot initial priors
    def plot_priors():
        ax_shape.clear()
        pd.Series(sim.shape_probs).plot(kind='bar', ax=ax_shape, color='steelblue', alpha=0.7)
        ax_shape.set_title('Shape Distribution', fontweight='bold', fontsize=9)
        ax_shape.set_ylabel('Probability', fontsize=8)
        ax_shape.tick_params(axis='x', rotation=45, labelsize=6)
        ax_shape.grid(alpha=0.3)
        # Annotation
        annot = CONFIG['plot_annotations']['shape_distribution']
        ax_shape.text(0.02, 0.98, f"{annot['what']}\n{annot['why']}",
                     transform=ax_shape.transAxes, va='top', fontsize=5.5,
                     bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.7))
        
        ax_polymer.clear()
        pd.Series(sim.poly_probs).plot(kind='bar', ax=ax_polymer, color='seagreen', alpha=0.7)
        ax_polymer.set_title('Polymer Distribution', fontweight='bold', fontsize=9)
        ax_polymer.set_ylabel('Probability', fontsize=8)
        ax_polymer.tick_params(axis='x', rotation=45, labelsize=6)
        ax_polymer.grid(alpha=0.3)
        annot = CONFIG['plot_annotations']['polymer_distribution']
        ax_polymer.text(0.02, 0.98, f"{annot['what']}\n{annot['why']}",
                       transform=ax_polymer.transAxes, va='top', fontsize=5.5,
                       bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.7))
    
    plot_priors()
    
    # Sliders (at bottom)
    slider_alpha = Slider(plt.axes([0.10, 0.015, 0.2, 0.012]), 'α',
                         1.5, 4.0, valinit=2.64)
    slider_min = Slider(plt.axes([0.38, 0.015, 0.2, 0.012]), 'Min (μm)',
                       10, 500, valinit=100, valstep=10)
    slider_n = Slider(plt.axes([0.66, 0.015, 0.2, 0.012]), 'MC Samples',
                     1000, 8000, valinit=3000, valstep=500)
    
    # Preset buttons (in dedicated row 3)
    preset_buttons = []
    button_width = 0.18
    button_height = 0.04
    button_spacing = 0.20
    button_y = 0.415  # Center of button row
    
    for idx, (key, preset) in enumerate(CONFIG['scenarios'].items()):
        x_pos = 0.05 + idx * button_spacing
        btn = Button(plt.axes([x_pos, button_y, button_width, button_height]), 
                    preset['name'], color='lightblue', hovercolor='skyblue')
        preset_buttons.append((btn, preset))
    
    # Reset button (last position)
    btn_reset = Button(plt.axes([0.65, button_y, button_width, button_height]), 
                      'Reset Priors', color='lightcoral', hovercolor='salmon')
    
    # Store surfaces (pre-computed)
    surfaces = {}
    print("Pre-computing surfaces...")
    alpha_grid = np.linspace(2.0, 3.5, 6)
    min_grid = np.linspace(60, 250, 6)
    A, M = np.meshgrid(alpha_grid, min_grid)
    Z_mean = np.zeros_like(A)
    Z_p50 = np.zeros_like(A)
    Z_range = np.zeros_like(A)
    
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            _, quants, _ = sim.run_monte_carlo_with_convergence(500, A[i,j], M[i,j], 5000)
            Z_mean[i,j] = sim.estimate_flux(quants['mean'])
            Z_p50[i,j] = sim.estimate_flux(quants['P50'])
            Z_range[i,j] = sim.estimate_flux(quants['P95']) - sim.estimate_flux(quants['P5'])
    
    surfaces = {'mean': (A, M, Z_mean), 'p50': (A, M, Z_p50), 'range': (A, M, Z_range)}
    print("Surfaces ready!")
    
    def update(val):
        alpha, min_s, n = slider_alpha.val, slider_min.val, int(slider_n.val)
        
        # Size distribution
        ax_size.clear()
        x = np.linspace(min_s, 5000, 1000)
        y = (x ** (-alpha)) / np.max(x ** (-alpha))
        ax_size.plot(x, y, 'r-', linewidth=2)
        ax_size.fill_between(x, y, alpha=0.2, color='red')
        ax_size.set_title(f'Size Distribution (α={alpha:.2f})', fontweight='bold', fontsize=9)
        ax_size.set_xlabel('μm', fontsize=8)
        ax_size.set_xscale('log')
        ax_size.grid(alpha=0.3)
        annot = CONFIG['plot_annotations']['size_distribution']
        ax_size.text(0.02, 0.98, annot['what'], transform=ax_size.transAxes,
                    va='top', fontsize=5.5, bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.7))
        
        # MC with convergence
        masses, quants, running_mean = sim.run_monte_carlo_with_convergence(n, alpha, min_s, 5000)
        
        # Convergence plot
        ax_convergence.clear()
        ax_convergence.plot(running_mean * 1000, linewidth=1.5, color='blue')
        ax_convergence.axhline(quants['mean'] * 1000, color='red', linestyle='--', label='Final Mean')
        ax_convergence.set_title('MC Convergence', fontweight='bold', fontsize=9)
        ax_convergence.set_xlabel('Iteration', fontsize=8)
        ax_convergence.set_ylabel('Running Mean (mg)', fontsize=8)
        ax_convergence.legend(fontsize=6)
        ax_convergence.grid(alpha=0.3)
        ax_convergence.text(0.02, 0.98, "Shows stability of estimate\\nwith more samples",
                           transform=ax_convergence.transAxes, va='top', fontsize=5.5,
                           bbox=dict(boxstyle='round', fc='lightyellow', alpha=0.7))
        
        # Mass distribution
        ax_mass.clear()
        ax_mass.hist(np.log10(masses * 1000 + 1e-12), bins=70,
                    color='skyblue', edgecolor='black', alpha=0.6, density=True)
        
        for q_name, q_val in quants.items():
            if q_name in ['P5', 'P50', 'P95']:
                color = {'P5': 'blue', 'P50': 'green', 'P95': 'red'}[q_name]
                ax_mass.axvline(np.log10(q_val * 1000), color=color,
                               linestyle='--', linewidth=2, label=f'{q_name}: {q_val*1000:.3f} mg')
        
        ax_mass.set_title('Particle Mass Distribution', fontweight='bold', fontsize=10)
        ax_mass.set_xlabel('Log₁₀(mg)', fontsize=8)
        ax_mass.set_ylabel('Density', fontsize=8)
        ax_mass.legend(fontsize=7, loc='upper left')
        ax_mass.grid(alpha=0.3)
        
        # Results summary
        ax_results.clear()
        ax_results.axis('off')
        
        flux_p5 = sim.estimate_flux(quants['P5'])
        flux_p50 = sim.estimate_flux(quants['P50'])
        flux_p95 = sim.estimate_flux(quants['P95'])
        flux_mean = sim.estimate_flux(quants['mean'])
        
        # Compare to literature
        lit_refs = CONFIG['reference_values']['literature_estimates']
        
        results_text = (
            f"═══ RESULTS (n={n}) ═══\\n"
            f"P5:   {flux_p5:>7.1f} kt/yr\\n"
            f"Mean: {flux_mean:>7.1f} kt/yr\\n"
            f"P50:  {flux_p50:>7.1f} kt/yr\\n"
            f"P95:  {flux_p95:>7.1f} kt/yr\\n"
            f"───────────────────\\n"
            f"Range: {flux_p95-flux_p5:.0f} kt/yr\\n"
            f"CV: {(flux_p95-flux_p5)/(2*flux_p50)*100:.1f}%\\n"
            f"\\n📚 Literature:\\n"
            f"Lebreton'17: {lit_refs['Lebreton2017']['value']} kt/yr\\n"
            f"Meijer'21: {lit_refs['Meijer2021']['value']} kt/yr"
        )
        
        ax_results.text(0.1, 0.5, results_text, transform=ax_results.transAxes,
                       va='center', fontsize=8, family='monospace',
                       bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # Update surfaces
        for ax_surf, surf_type, title, cmap in [(ax_surf_mean, 'mean', 'Mean Flux', 'viridis'),
                                                  (ax_surf_p50, 'p50', 'P50 Flux', 'Greens'),
                                                  (ax_surf_range, 'range', 'Uncertainty Range', 'Reds')]:
            ax_surf.clear()
            A, M, Z = surfaces[surf_type]
            surf = ax_surf.plot_surface(A, M, Z, cmap=cmap, alpha=0.7, edgecolor='none')
            
            idx_max = np.unravel_index(np.argmax(Z), Z.shape)
            ax_surf.scatter([A[idx_max]], [M[idx_max]], [Z[idx_max]],
                          color='red', s=80, marker='^', label=f'Max: {Z[idx_max]:.0f}')
            
            current_z = sim.estimate_flux(quants['mean' if surf_type == 'mean' else 'P50']) if surf_type != 'range' else (flux_p95 - flux_p5)
            ax_surf.scatter([alpha], [min_s], [current_z],
                          color='yellow', s=60, marker='o', edgecolors='black')
            
            ax_surf.set_xlabel('α', fontsize=7)
            ax_surf.set_ylabel('Min', fontsize=7)
            ax_surf.set_zlabel('kt/yr', fontsize=7)
            ax_surf.set_title(title, fontweight='bold', fontsize=9)
            ax_surf.legend(fontsize=6)
            ax_surf.view_init(elev=20, azim=-70)
        
        fig.canvas.draw_idle()
    
    # Preset button callbacks
    for btn, preset in preset_buttons:
        btn.on_clicked(lambda event, p=preset: apply_preset(p))
    
    def apply_preset(preset):
        params = preset['parameters']
        slider_alpha.set_val(params['alpha'])
        slider_min.set_val(params['min_size_um'])
        slider_n.set_val(params['mc_samples'])
        print(f"Applied preset: {preset['name']}")
    
    def reset_priors_callback(event):
        sim.reset_priors()
        plot_priors()
        update(None)
        fig.canvas.draw_idle()
    
    btn_reset.on_clicked(reset_priors_callback)
    slider_alpha.on_changed(update)
    slider_min.on_changed(update)
    slider_n.on_changed(update)
    
    update(None)
    plt.show()


if __name__ == "__main__":
    print("="*70)
    print("Enhanced Coastal Flux Uncertainty Explorer")
    print("Comprehensive Monte Carlo Analysis with Sensitivity & Presets")
    print("="*70)
    create_enhanced_explorer()
