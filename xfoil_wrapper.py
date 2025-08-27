from xfoil import XFoil
from xfoil.model import Airfoil
import numpy as np
import matplotlib.pyplot as plt

def load_airfoil_from_file(file_path):
    x_coords = []
    y_coords = []
    
    with open(file_path, 'r') as file:

        next(file)
        
        for line in file:
            x, y = map(float, line.strip().split())
            x_coords.append(x)
            y_coords.append(y)
    
    x_coords = np.array(x_coords)
    y_coords = np.array(y_coords)
    
    return x_coords, y_coords

x, y = load_airfoil_from_file("airfoils/E63.dat")

xf = XFoil()
xf.airfoil = Airfoil(x,y)
xf.repanel()
plt.plot(xf.airfoil.x, xf.airfoil.y)
plt.axis('equal')
plt.grid()
plt.show()

xf.Re = 1e6
xf.max_iter = 40
a, cl, cd, cm, cp = xf.aseq(-8, 8, 0.5)

#plt.plot(a, cl)
#plt.show()

# from xfoil.test import naca0012
# xf.airfoil = naca0012
# plt.plot(xf.airfoil.x, xf.airfoil.y)
# plt.axis('equal')
# plt.grid()
# plt.show()
