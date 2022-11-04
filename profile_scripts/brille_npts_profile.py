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
    fc_info = get_fc_info()[-1] # AmSulf
    qpts = np.loadtxt('qpts_160801.txt')
    qpts = qpts[:10000]

    brille_npts_list = [3000, 3500, 4000, 4500, 5000, 7500, 10000]
    fobj = open(os.path.join(out_dir, f'brille_npts_{int(time.time())}.txt'), 'w')
    fwrite(fobj, f'n_threads={NTHREADS} --brille-npts={brille_npts_list} --dipole-parameter={fc_info["sdipole_parameter"]}')

    fwrite(fobj, f'\n\nMaterial: {fc_info["filename"]:10}\n')
    for brille_npts in brille_npts_list:
        fci = ForceConstants.from_castep(str(get_fc_path(fc_info["filename"])))

        interpolate_kwargs = {'n_threads': NTHREADS, 'dipole_parameter': fc_info["dipole_parameter"]}
        fwrite(fobj, f'\n\nBrille Npts: {brille_npts}\n')

        # Brille init
        fwrite(fobj, f'\nBrille Init\n')
        for n in range(n_repeats):
            ti = time.time()
            bri = BrilleInterpolator.from_force_constants(
                fci, grid_npts=brille_npts,
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

    fobj.close()

if __name__ == '__main__':
    main()
