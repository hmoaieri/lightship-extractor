import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import simps
from scipy.signal import savgol_filter
import json

class LightshipWeightExtractor:
    """
    Reverse-engineers lightship weight distribution from loading manual data.
    """
    
    def __init__(self, rho=1.025, g=9.81):
        """
        Args:
            rho: Water density (tonnes/m^3). Default: 1.025 (sea water).
            g: Gravitational acceleration (m/s^2). Default: 9.81.
        """
        self.rho = rho
        self.g = g
        self.x = None
        self.S = None
        self.A = None
        self.deadweight_data = None
        
    def set_shear_force_data(self, x, S):
        """Set shear force distribution."""
        self.x = np.array(x, dtype=float)
        self.S = np.array(S, dtype=float)
        
    def set_hull_section_data(self, A):
        """Set submerged cross-sectional areas at each station."""
        if self.x is None:
            raise ValueError("Must set shear force data first to define station grid.")
        if len(A) != len(self.x):
            raise ValueError("Length of section area array must match station grid.")
        self.A = np.array(A, dtype=float)
        
    def set_deadweight_data(self, compartments):
        """
        Set deadweight distribution from compartment data.
        
        Args:
            compartments: List of dicts with keys:
                - 'start': start position (m)
                - 'end': end position (m)
                - 'density': density of contents (tonnes/m^3)
                - 'total_weight': optional total weight (tonnes) for uniform distribution
        """
        self.deadweight_data = compartments
        
    def _calculate_buoyancy(self):
        """Calculate buoyancy distribution (kN/m)."""
        if self.A is None:
            raise ValueError("Hull section data not set.")
        return self.rho * self.g * self.A
    
    def _calculate_load(self, method='central'):
        """
        Differentiate shear force to obtain load distribution (kN/m).
        
        Args:
            method: 'central', 'forward', or 'backward' difference.
        """
        if self.S is None:
            raise ValueError("Shear force data not set.")
        n = len(self.S)
        p = np.zeros(n)
        dx = self.x[1] - self.x[0]
        
        if method == 'central':
            for i in range(1, n-1):
                p[i] = -(self.S[i+1] - self.S[i-1]) / (2 * dx)
            p[0] = -(-3*self.S[0] + 4*self.S[1] - self.S[2]) / (2 * dx)
            p[-1] = -(self.S[-3] - 4*self.S[-2] + 3*self.S[-1]) / (2 * dx)
        elif method == 'forward':
            for i in range(n-1):
                p[i] = -(self.S[i+1] - self.S[i]) / dx
            p[-1] = p[-2]
        elif method == 'backward':
            for i in range(1, n):
                p[i] = -(self.S[i] - self.S[i-1]) / dx
            p[0] = p[1]
        else:
            raise ValueError("method must be 'central', 'forward', or 'backward'.")
        return p
    
    def _calculate_deadweight(self):
        """Calculate deadweight distribution (kN/m)."""
        if self.deadweight_data is None:
            raise ValueError("Deadweight data not set.")
        n = len(self.x)
        w_dead = np.zeros(n)
        
        for comp in self.deadweight_data:
            start = comp['start']
            end = comp['end']
            density = comp.get('density', 0) * self.g  # Convert to kN/m^3
            mask = (self.x >= start) & (self.x <= end)
            if not np.any(mask):
                continue
            if 'total_weight' in comp and comp['total_weight'] > 0:
                # Uniform distribution
                total_weight = comp['total_weight'] * self.g  # kN
                comp_length = end - start
                if comp_length > 0:
                    w_dead[mask] += total_weight / comp_length
            else:
                # Distribution based on density (requires 'area' data per station, simplified here)
                # For this implementation, we assume uniform distribution if no area data
                comp_length = end - start
                if comp_length > 0 and density > 0:
                    # Estimate volume from a default cross-section area (needs refinement)
                    # In practice, use compartment geometry data
                    # This is a placeholder; actual implementation requires area data
                    pass
        return w_dead
    
    def extract_lightship_weight(self, method='central', smooth=True, smooth_window=7):
        """
        Main method to extract lightship weight distribution.
        
        Returns:
            w_ls: Array of lightship weight per unit length (kN/m).
            results: Dict with validation metrics.
        """
        # Step 1: Buoyancy
        b = self._calculate_buoyancy()
        
        # Step 2: Load from shear force
        p = self._calculate_load(method)
        
        # Step 3: Total weight
        w_total = b - p
        
        # Step 4: Deadweight
        w_dead = self._calculate_deadweight()
        
        # Step 5: Lightship weight
        w_ls = w_total - w_dead
        
        # Smoothing
        if smooth and len(w_ls) > smooth_window:
            w_ls = savgol_filter(w_ls, window_length=smooth_window, polyorder=3)
        
        # Validation
        results = self._validate(w_ls, w_total, w_dead, b, p)
        return w_ls, results
    
    def _validate(self, w_ls, w_total, w_dead, b, p):
        """Compute validation metrics."""
        dx = self.x[1] - self.x[0]
        W_ls = simps(w_ls, self.x)
        W_total = simps(w_total, self.x)
        W_dead = simps(w_dead, self.x)
        W_b = simps(b, self.x)
        
        LCG_ls = simps(self.x * w_ls, self.x) / W_ls if W_ls > 0 else 0
        LCG_total = simps(self.x * w_total, self.x) / W_total if W_total > 0 else 0
        
        return {
            'W_lightship': W_ls,
            'W_total': W_total,
            'W_deadweight': W_dead,
            'W_buoyancy': W_b,
            'LCG_lightship': LCG_ls,
            'LCG_total': LCG_total,
            'error_percent': abs(W_ls + W_dead - W_b) / W_b * 100 if W_b > 0 else 0
        }
    
    def plot_results(self, w_ls, results, save_path=None):
        """Generate diagnostic plots."""
        import matplotlib.pyplot as plt
        b = self._calculate_buoyancy()
        p = self._calculate_load()
        w_dead = self._calculate_deadweight()
        w_total = b - p
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].plot(self.x, w_total, 'b-', label='Total Weight', lw=2)
        axes[0, 0].plot(self.x, b, 'g-', label='Buoyancy', lw=2)
        axes[0, 0].plot(self.x, w_ls, 'r-', label='Lightship Weight', lw=2)
        axes[0, 0].plot(self.x, w_dead, 'm--', label='Deadweight', lw=1.5)
        axes[0, 0].set_xlabel('Position (m)')
        axes[0, 0].set_ylabel('kN/m')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_title('Weight and Buoyancy Distribution')
        
        axes[0, 1].plot(self.x, p, 'r-', lw=2)
        axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[0, 1].fill_between(self.x, 0, p, alpha=0.2, color='red')
        axes[0, 1].set_xlabel('Position (m)')
        axes[0, 1].set_ylabel('Net Load (kN/m)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_title('Net Load Distribution')
        
        axes[1, 0].plot(self.x, self.S, 'b-', lw=2)
        axes[1, 0].set_xlabel('Position (m)')
        axes[1, 0].set_ylabel('Shear Force (kN)')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_title('Shear Force (Input)')
        
        weights = [results['W_lightship'], results['W_deadweight'], results['W_buoyancy']]
        labels = ['Lightship', 'Deadweight', 'Buoyancy']
        colors = ['red', 'purple', 'green']
        axes[1, 1].bar(labels, weights, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('Total Force (kN)')
        axes[1, 1].set_title('Validation: Weight Components')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].text(0.5, 0.95, f'Error: {results["error_percent"]:.2f}%', 
                       transform=axes[1, 1].transAxes, ha='center', va='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        return fig
