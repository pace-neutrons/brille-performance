import os
import time

import numpy as np

from euphonic import ForceConstants, ureg
from euphonic.brille import BrilleInterpolator
from euphonic.util import mp_grid
from utils import (get_fc_path, get_create_results_path, get_fc_info,
                   fwrite, NTHREADS)

def main():
    out_dir = get_create_results_path()
    n_repeats = 3
    fc_info = get_fc_info()
    qpts = np.loadtxt('qpts_160801.txt')

    n_threads = NTHREADS

    fobj = open(os.path.join(out_dir, f'interpolate_{int(time.time())}.txt'), 'w')
    fwrite(fobj, f'n_threads={NTHREADS} --brille-npts={[fc["sbrille_npts"] for fc in fc_info]} --dipole-parameter={[fc["sdipole_parameter"] for fc in fc_info]}')

    for fc in fc_info:
        fci = ForceConstants.from_castep(str(get_fc_path(fc["filename"])))
        fwrite(fobj, f'\n\nMaterial: {fc["filename"]:10}\n')

        # Euphonic interpolate
        fwrite(fobj, f'Euphonic Interpolate\n')
        interpolate_kwargs = {'n_threads': NTHREADS, 'dipole_parameter': fc["dipole_parameter"]}
        for n in range(n_repeats):
            ti = time.time()
            modes = fci.calculate_qpoint_phonon_modes(qpts, **interpolate_kwargs)
            tf = time.time()
            fwrite(fobj, f'{tf - ti:10.3f}')

        # Brille init
        fwrite(fobj, f'\nBrille Init\n')
        for n in range(n_repeats):
            ti = time.time()
            bri = BrilleInterpolator.from_force_constants(
                fci, grid_npts=fc["brille_npts"],
                interpolation_kwargs=interpolate_kwargs)
            tf = time.time()
            fwrite(fobj, f'{tf - ti:10.3f}')
        # Brille interpolate
        fwrite(fobj, f'\nBrille Interpolate\n')
        for n in range(n_repeats):
            ti = time.time()
            bri.calculate_qpoint_phonon_modes(qpts, useparallel=True, threads=NTHREADS)
            tf = time.time()
            fwrite(fobj, f'{tf - ti:10.3f}')

        # Calculate structure factor
        fwrite(fobj, f'\nStructure Factor\n')
        dw_modes = fci.calculate_qpoint_phonon_modes(mp_grid([6, 6, 6]), **interpolate_kwargs)
        dw = dw_modes.calculate_debye_waller(temperature=5*ureg('K'))
        for n in range(n_repeats):
            ti = time.time()
            modes.calculate_structure_factor(dw=dw)
            tf = time.time()
            fwrite(fobj, f'{tf - ti:10.3f}')
    fobj.close()

if __name__ == '__main__':
    main()
