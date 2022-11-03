import os
import time
import cProfile
import pstats
import io
import inspect

import numpy as np

from euphonic import ForceConstants, ureg
from euphonic.brille import BrilleInterpolator
from euphonic.util import mp_grid
from utils import get_fc_path, get_create_results_path, get_fc_info, NTHREADS

def main():
    fc_info = get_fc_info()
    fci = fc_info[3] # 3 = AmSulf
    fc_file = str(get_fc_path(fci['filename']))
    qpts = np.loadtxt('qpts_160801.txt')
    qpts = qpts[:10000] # Using all qpts runs out of memory with AmSulf
    fc = ForceConstants.from_castep(fc_file)

    # Euphonic interpolate
    interpolate_kwargs = {'n_threads': NTHREADS, 'dipole_parameter': fci["dipole_parameter"]}
    modes = fc.calculate_qpoint_phonon_modes(qpts, **interpolate_kwargs)
    # Euphonic interpolate - frequencies only
    fc.calculate_qpoint_frequencies(qpts, **interpolate_kwargs)

    # Brille init
    bri = BrilleInterpolator.from_force_constants(
        fc, grid_npts=fci["brille_npts"],
        interpolation_kwargs=interpolate_kwargs)
    # Brille interpolate
    bri.calculate_qpoint_phonon_modes(qpts, useparallel=True, threads=NTHREADS)
    # Brille interpolate - frequencies only
    bri.calculate_qpoint_frequencies(qpts, useparallel=True, threads=NTHREADS)

    # Calculate structure factor
    dw_modes = fc.calculate_qpoint_phonon_modes(mp_grid([6, 6, 6]), **interpolate_kwargs)
    dw = dw_modes.calculate_debye_waller(temperature=5*ureg('K'))
    modes.calculate_structure_factor(dw=dw)

if __name__ == '__main__':
    out_file = f'{get_create_results_path()}/interpolate_cprofile_{int(time.time())}.txt'
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()

    strio = io.StringIO()
    stats = pstats.Stats(pr, stream=strio).sort_stats('cumtime')
    stats.print_stats()

    with open(out_file, 'a') as f:
        f.write(strio.getvalue())

    with open(out_file, 'a') as f:
        f.write(inspect.getsource(inspect.getmodule(inspect.currentframe())))
