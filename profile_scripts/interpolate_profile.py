import os
import time

import numpy as np

from euphonic import ForceConstants, ureg
from euphonic.brille import BrilleInterpolator
from euphonic.util import mp_grid

def main():
    out_dir = os.path.join('..', 'profile_results', 'python', 'idaaas')
    fc_dir = os.path.join('..', 'force_constants')
    n_repeats = 3
    fcs = ['quartz.castep_bin',
           'La2Zr2O7.castep_bin',
           'Nb-181818-s0.5-NCP19-vib-disp.castep_bin']
    materials = ['quartz', 'La2Zr2O7', 'Nb']
    qpts = np.loadtxt('qpts_160801.txt')

    n_threads = 30
    brille_npts = [10000, 5000, 20000]
    dipole_params = [0.75, 1.0, 1.0]

    fobj = open(os.path.join(out_dir, f'interpolate_{int(time.time())}.txt'), 'w')
    fobj.write(f'n_threads={n_threads} brille_npts={brille_npts} dipole_parameter={dipole_params}')

    for i, fc in enumerate(fcs):
        fci = ForceConstants.from_castep(os.path.join(fc_dir, fc))
        fobj.write(f'\n\nMaterial: {materials[i]:10}\n')

        # Euphonic interpolate
        fobj.write(f'Euphonic Interpolate\n')
        interpolate_kwargs = {'n_threads': n_threads, 'dipole_parameter': dipole_params[i]}
        for n in range(n_repeats):
            ti = time.time()
            modes = fci.calculate_qpoint_phonon_modes(qpts, **interpolate_kwargs)
            tf = time.time()
            fobj.write(f'{tf - ti:10.3f}')

        # Brille init
        fobj.write(f'\nBrille Init\n')
        for n in range(n_repeats):
            ti = time.time()
            bri = BrilleInterpolator.from_force_constants(
                fci, grid_npts=brille_npts[i],
                interpolation_kwargs=interpolate_kwargs)
            tf = time.time()
            fobj.write(f'{tf - ti:10.3f}')
        # Brille interpolate
        fobj.write(f'\nBrille Interpolate\n')
        for n in range(n_repeats):
            ti = time.time()
            bri.calculate_qpoint_phonon_modes(qpts, useparallel=True, threads=n_threads)
            tf = time.time()
            fobj.write(f'{tf - ti:10.3f}')

        # Calculate structure factor
        fobj.write(f'\nStructure Factor\n')
        dw_modes = fci.calculate_qpoint_phonon_modes(mp_grid([6, 6, 6]), **interpolate_kwargs)
        dw = dw_modes.calculate_debye_waller(temperature=5*ureg('K'))
        for n in range(n_repeats):
            ti = time.time()
            modes.calculate_structure_factor(dw=dw)
            tf = time.time()
            fobj.write(f'{tf - ti:10.3f}')

        # Ensure profiling data so far is written even if
        # program crashes and doesn't reach fobj.close()
        fobj.flush()
    fobj.close()

if __name__ == '__main__':
    main()
