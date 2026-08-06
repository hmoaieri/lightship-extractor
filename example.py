import numpy as np
from src.lightship_extractor import LightshipWeightExtractor

# Generate synthetic data for demonstration
def generate_sample_data():
    L = 100
    n = 21
    x = np.linspace(0, L, n)
    
    # True lightship weight (hypothetical)
    w_ls_true = 1.5 * np.sin(np.pi * x / L) + 0.5 * np.sin(2 * np.pi * x / L) + 1.0
    w_ls_true = w_ls_true / np.mean(w_ls_true) * 100  # kN/m
    
    # Deadweight (tanks)
    w_dead = np.zeros(n)
    for i, xi in enumerate(x):
        if 20 <= xi <= 40:
            w_dead[i] = 50
        elif 60 <= xi <= 80:
            w_dead[i] = 70
    
    # Buoyancy from a hypothetical hull
    A = 100 * np.sin(np.pi * x / L) + 20 * np.sin(2 * np.pi * x / L) + 200  # m^2
    rho, g = 1.025, 9.81
    b = rho * g * A / 1000  # kN/m
    
    # Total weight and shear force
    w_total = w_ls_true + w_dead
    p = w_total - b
    S = np.cumsum(p) * (x[1] - x[0])
    S = S - S[0] - (S[-1] - S[0]) * x / L  # Zero at ends
    
    compartments = [
        {'start': 20, 'end': 40, 'total_weight': 1400},
        {'start': 60, 'end': 80, 'total_weight': 1400}
    ]
    return {'x': x, 'S': S, 'A': A, 'compartments': compartments}

if __name__ == "__main__":
    data = generate_sample_data()
    
    extractor = LightshipWeightExtractor()
    extractor.set_shear_force_data(data['x'], data['S'])
    extractor.set_hull_section_data(data['A'])
    extractor.set_deadweight_data(data['compartments'])
    
    w_ls, results = extractor.extract_lightship_weight(method='central', smooth=True)
    
    print("===== Extraction Results =====")
    print(f"Lightship Weight: {results['W_lightship']:.2f} kN")
    print(f"LCG: {results['LCG_lightship']:.2f} m")
    print(f"Error: {results['error_percent']:.3f}%")
    
    extractor.plot_results(w_ls, results, save_path='distribution_plot.png')
