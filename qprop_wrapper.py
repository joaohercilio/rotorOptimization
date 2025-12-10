import subprocess

def run_qprop(qprop_path, propfile, motorfile, velocity, rpm, outfile):
    with open(outfile, 'w') as f:
        subprocess.run(
            [qprop_path, propfile, motorfile, str(velocity), str(rpm)],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )