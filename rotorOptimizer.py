from qprop_writer import generate_qprop_input
from qprop_wrapper import run_qprop
from geometry_reader import read_apc_geometry

import pygad

prop = 'APC/10x45MR-PERF.PE0'

qprop_path = 'Qprop/bin/qprop'
outfile = 'out.dat'
propfile = '../../apc_prop'
motorfile = 's400-6v-dd'
vel = 10
rpm = 10000

radius, chord, twist, airfoils, thickness_ratio = read_apc_geometry(prop, n_ctrl=10, mode="nonuniform")

def fitness_func(ga_instance, solution, solution_idx):
    
    run_qprop(qprop_path, propfile, motorfile, vel, rpm, outfile)

    with open(outfile) as f:
        for line in f:
            if line.startswith('#') and 'V(m/s)' in line and 'Pshaft' in line:
                next_line = next(f).strip() 
                pshaft = float(next_line.split()[6])
                break

    return pshaft




