import numpy as np
import pandas as pd

def read_apc_geometry(file_path, n_points=10, mode = "nonuniform", edge_factor = 0.8):

    """
    Reads APC-prop geometry file and returns radius, chord, twist
    
    APC files have a maximum of 40 points describing their geometry
    
    Parameters
    ----------
    file_path : str
        Path to APC geometry file
    
    n_points : int
        Number of control points that shall be returned
    
    mode : str
        "uniform" or "nonuniform"
    
    edge_factor : float
        Point concentration factor for "nonuniform"
    
    Returns
    -------
    radius, chord, twist : np.ndarray
    """
    
    ####  GEOMETRY SECTION
    
    max_limit = 40
    if n_points > max_limit:
        raise ValueError(f"Number of points exceeds the maximum limit of {max_limit} on propeller geometry file")
    
    headers = ["STATION", "CHORD", "PITCH_QUOTED", "PITCH_LE_TE", "PITCH_PRATHER",
        "SWEEP", "THICKNESS_RATIO", "TWIST", "MAX_THICK", "CROSS_SECTION",
        "ZHIGH", "CGY", "CGZ"]
    
    with open(file_path) as f:
        lines = f.readlines()

    start_idx = next(i for i, line in enumerate(lines) if line.strip().startswith("STATION"))
    data_lines = lines[start_idx + 3:]
    
    data = []
    for line in data_lines:
        parts = line.split()
        if len(parts) != len(headers):
            break
        data.append([float(x) for x in parts])
    
    df = pd.DataFrame(data, columns=headers)

    if mode == "nonuniform":
        uniform = np.linspace(0, 1, n_points)
        non_uniform = 0.5 * (1 - np.cos(np.pi * uniform**edge_factor))
        non_uniform = non_uniform / non_uniform[-1]
        indices = np.round(non_uniform * (len(df) - 1))
    else:
        indices = np.linspace(0, len(df) - 1, n_points, dtype=int)
    
    df_subset = df.iloc[indices]

    radius = np.array(df_subset["STATION"])
    chord = np.array(df_subset["CHORD"])
    twist = np.array(df_subset["TWIST"])

    ####  AIRFOIL SECTION

    airfoil1_line = next((line for line in lines if line.startswith(" AIRFOIL1:")), None)
    airfoil2_line = next((line for line in lines if line.startswith(" AIRFOIL2:")), None)
    
    def parse_airfoil_line(line):
        parts = line.replace(",", "").split()
        return float(parts[1]), parts[2]

    trans1, airfoil1 = parse_airfoil_line(airfoil1_line)
    trans2, airfoil2 = parse_airfoil_line(airfoil2_line)

    return radius, chord, twist, [(trans1, airfoil1), (trans2, airfoil2)]

'''
    # TEST RUNS
    
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt

radius, chord, twist, airfoils = read_apc_geometry("APC/10x45MR-PERF.PE0", 40, "uniform")
xp = radius
yp = chord
interp = PchipInterpolator(xp, yp)
xi = np.linspace(xp[0], xp[-1], 50)
yi = interp(xi)
plt.plot(xi, yi, label = 'All points', color = 'g')

radius, chord, twist, airfoils = read_apc_geometry("APC/10x45MR-PERF.PE0", 10, "uniform")
xp = radius 
yp = chord
interp = PchipInterpolator(xp, yp)
xi = np.linspace(xp[0], xp[-1], 50)
yi = interp(xi)
plt.plot(xp, yp, 'o', color = 'b')
plt.plot(xi, yi, label = 'Uniform', color = 'b')

radius, chord, twist, airfoils = read_apc_geometry("APC/10x45MR-PERF.PE0", 10)
xp = radius
yp = chord
interp = PchipInterpolator(xp, yp)
xi = np.linspace(xp[0], xp[-1], 50)
yi = interp(xi)
plt.plot(xp, yp, 'o', color = 'r')
plt.plot(xi, yi, label = 'Non-Uniform', color = 'r')

plt.title("Chord distribution 10x45MR")
plt.xlabel("Radius (in)")
plt.ylabel("Chord (in)")
plt.legend()
plt.show()

print("Airfoils found:")
for trans, name in airfoils:
    print(f" - Transition at {trans:.2f}: {name}")
'''




