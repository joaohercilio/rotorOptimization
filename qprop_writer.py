from geometry_reader import read_apc_geometry
import numpy as np
from scipy.interpolate import PchipInterpolator

def generate_qprop_input(input_file, output_file, n_ctrl=10, n_interp=50, mode="nonuniform"):

    """
    Creates a QProp propeller input file by selecting points from a geometry file,
    then interpolating a curve using PCHIP to obtain the radius, chord and twist distribution.
    The airfoil data for each section of the propeller is obtained with XFoil    
        
    Parameters
    ----------
    input_file: str
        Path to geometry file
    
    output_file: str
        Path to QProp geometry file

    n_ctrl : int
        Number of control points that shall be selected from the geometry file
    
    n_interp : int
        Number of interpolated points that shall be written on the QProp input file
    
    mode : str
        Chooses whether the selected points in the geometry file are picked 
        uniformly ("uniform") or non-uniformly ("nonuniform").
    """

    radius, chord, twist, airfoils = read_apc_geometry(input_file, n_ctrl, mode=mode)
    
    xp = np.array(radius , dtype = np.float64)
    xi = np.linspace(xp[0], xp[-1], n_interp)

    yp_chord = np.array(chord, dtype = np.float64)
    yp_twist= np.array(twist, dtype = np.float64)

    interp_chord = PchipInterpolator(xp, yp_chord)
    interp_twist = PchipInterpolator(xp, yp_twist)

    yi_chord = interp_chord(xi)
    yi_twist = interp_twist(xi)

    header = f"""
{input_file}  
 2           ! Nblades
    
 0.50  5.8   ! CL0     CL_a
 -0.3  1.2   ! CLmin   CLmax
    
 0.028  0.050  0.5   !  CD0    CD2    CLCD0
 70000   -0.7        !  REref  REexp
    
 0.0254  0.0254   1.0  !  Rfac   Cfac   Bfac  
 0.0     0.0      0.0  !  Radd   Cadd   Badd  
    
#  r  chord  beta  CL0  CL_a  CLmin CLmax  CD0   CD2u   CD2l   CLCD0  REref  REexp"""

    with open(output_file, "w") as f:
        f.write(header)
        for ri, ci, bi in zip(xi, yi_chord, yi_twist):
            f.write(f"\n{ri}  {ci}  {bi}")
    
    print(f"Qprop propeller input file '{output_file}' created suscessfuly from {input_file} file")

'''
    TEST RUNS
'''

generate_qprop_input("APC/10x45MR-PERF.PE0", "apc_prop")