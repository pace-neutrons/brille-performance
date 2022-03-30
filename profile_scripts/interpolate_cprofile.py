import os
import time

import numpy as np

from euphonic import ForceConstants, ureg
from euphonic.brille import BrilleInterpolator
from euphonic.util import mp_grid

def main():
    fc_dir = os.path.join('..', 'force_constants')
    qpts = np.loadtxt('qpts_160801.txt')

    n_threads = 30
    fc = ForceConstants.from_castep(os.path.join(fc_dir, 'quartz.castep_bin'))

    # Euphonic interpolate
    interpolate_kwargs = {'n_threads': n_threads, 'dipole_parameter': 0.75}
    modes = fc.calculate_qpoint_phonon_modes(qpts, **interpolate_kwargs)

    # Brille init
    bri = BrilleInterpolator.from_force_constants(
        fc, n_grid_points=10000,
        interpolation_kwargs=interpolate_kwargs)
    # Brille interpolate
    bri.calculate_qpoint_phonon_modes(qpts, useparallel=True, threads=n_threads)

    # Calculate structure factor
    dw_modes = fc.calculate_qpoint_phonon_modes(mp_grid([6, 6, 6]), **interpolate_kwargs)
    dw = dw_modes.calculate_debye_waller(temperature=5*ureg('K'))
    modes.calculate_structure_factor(dw=dw)

if __name__ == '__main__':
    main()
