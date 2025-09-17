import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import subprocess
import tempfile
import os

class XFoil:
    def __init__(self, airfoil1, airfoil2, reynolds = 4e5, mach=0.0):
        self.xfoil_path = 'xfoil'
        self.airfoil1 = airfoil1
        self.airfoil2 = airfoil2
        self.reynolds = reynolds
        self.mach = mach
        
    def aseq(self, alpha_start, alpha_end, alpha_step):
        commands = [
            f'LOAD {self.airfoil1}',
            'PPAR',
            'N 160',
            '',
            '',
            'OPER',
            f'VISC {self.reynolds}',
            'PACC',
            'polar.txt',
            '',
            f'ASEQ {alpha_start} {alpha_end} {alpha_step}',
            '',
            'QUIT'
        ]
        stdout, stderr = self._run_commands(commands)
        return self._parse_polar_file('polar.txt')
    
    def inte(self, frac, alpha_start, alpha_end, alpha_step, reynolds):
        commands = [
            'INTE',
            'F',
            f'{self.airfoil1}.dat',
            'F',
            f'{self.airfoil2}.dat',
            f'{frac}',
            'new',
            'PANE',
            'OPER',
            f'VISC {reynolds}',
            'PACC',
            'polar.txt',
            '',
            f'ASEQ {alpha_start} {alpha_end} {alpha_step}',
            '',
            'QUIT'
        ]
        stdout, stderr = self._run_commands(commands)
        return self._parse_polar_file('polar.txt')

    def _run_commands(self, commands):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, 'input.in')
            with open(input_file, 'w') as f:
                f.write('\n'.join(commands))
                #print('\n'.join(commands))

            result = subprocess.run(
                [self.xfoil_path],
                stdin=open(input_file, 'r'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = result.stdout, result.stderr
            
            return stdout, stderr     
           
    def _parse_polar_file(self, filename):
        data = np.loadtxt(filename, skiprows=12)
        os.remove('polar.txt')
        return {
            'alpha': data[:, 0],
            'CL': data[:, 1],
            'CD': data[:, 2],
            'CDp': data[:, 3],
            'CM': data[:, 4],
        }

def fit_qprop_parameters(results, reynolds, reexp=-0.5):
    alpha = results['alpha']
    CL = results['CL']
    CD = results['CD']

    # CL0 and CL_alpha ----
    mask = (alpha >= -2) & (alpha <= 6)
    p = np.polyfit(alpha[mask], CL[mask], 1)
    CL_alpha_per_deg = p[0]  
    CL0 = np.polyval(p, 0.0) 
    CL_alpha = CL_alpha_per_deg * (180.0 / np.pi)  

    # CLmin and CLmax ----
    CLmin = np.min(CL)
    CLmax = np.max(CL)

    # CD polar 
    idx_cdmin = np.argmin(CD)
    CLCD0 = CL[idx_cdmin]
    CD0 = CD[idx_cdmin]

    def parabola(CL, CD2):
        return CD0 + CD2 * (CL - CLCD0) ** 2

    mask_upper = CL >= CLCD0
    mask_lower = CL <= CLCD0

    CD2u, _ = curve_fit(parabola, CL[mask_upper], CD[mask_upper], p0=[0.05])
    CD2l, _ = curve_fit(parabola, CL[mask_lower], CD[mask_lower], p0=[0.05])

    # 4) Re and Reexp ----
    REref = reynolds
    REexp = reexp

    return {
        "CL0": CL0,
        "CL_a": CL_alpha,
        "CLmin": CLmin,
        "CLmax": CLmax,
        "CD0": CD0,
        "CD2u": CD2u[0],
        "CD2l": CD2l[0],
        "CLCD0": CLCD0,
        "REref": REref,
        "REexp": REexp
    }


'''
xfoil = XFoil('airfoils/NACA0012', 'airfoils/NACA2412')
results = xfoil.inte(0.5, alpha_start=-10, alpha_end=10, alpha_step=0.5, reynolds = 4e5)

plt.plot(results['alpha'], results['CL'])
plt.xlabel('Alpha')
plt.ylabel('CL')
plt.grid()
plt.show()

data = fit_qprop_parameters(results, 2.5e5)
print(
    data["CL0"],
    data["CL_a"],
    data["CLmin"],
    data["CLmax"],
    data["CD0"],
    data["CD2u"],
    data["CD2l"],
    data["CLCD0"]
)
'''
