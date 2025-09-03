import numpy as np
import matplotlib.pyplot as plt
import subprocess
import tempfile
import os

class XFoil:
    def __init__(self, airfoil_file, reynolds = 1e5, mach=0.0):
        self.xfoil_path = 'xfoil'
        self.airfoil_file = airfoil_file
        self.reynolds = reynolds
        self.mach = mach
        
    def aseq(self, alpha_start, alpha_end, alpha_step):
        commands = [
            f'LOAD {self.airfoil_file}',
            'PPAR',
            'N 160',
            '',
            '',
            'OPER',
            #f'RE {self.reynolds}'
            'PACC',
            'polar.txt',
            '',
            f'ASEQ {alpha_start} {alpha_end} {alpha_step}',
            'QUIT'
        ]
        stdout, stderr = self._run_commands(commands)
        return self._parse_polar_file('polar.txt')
    
    def _run_commands(self, commands):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, 'input.in')
            with open(input_file, 'w') as f:
                f.write('\n'.join(commands))
            
            result = subprocess.run(
                [self.xfoil_path],
                stdin=open(input_file, 'r'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout, result.stderr     
           
    def _parse_polar_file(self, filename):
        data = np.loadtxt(filename, skiprows=12)
        return {
            'alpha': data[:, 0],
            'CL': data[:, 1],
            'CD': data[:, 2],
            'CDp': data[:, 3],
            'CM': data[:, 4],
        }

xfoil = XFoil('airfoils/NACA0012.dat')
results = xfoil.aseq(alpha_start=-12, alpha_end=12, alpha_step=0.5)

plt.plot(results['alpha'], results['CL'])
plt.xlabel('Alpha')
plt.ylabel('CL')
plt.grid()
plt.show()