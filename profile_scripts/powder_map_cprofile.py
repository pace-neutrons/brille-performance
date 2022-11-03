import os
import time
import cProfile
import pstats
import io
import inspect

from euphonic.cli.powder_map import main as powder_map
from utils import get_fc_path, get_create_results_path, NTHREADS

def main(use_brille=False):
    fc = str(get_fc_path('AmSulf_298K.castep_bin'))

    args = [fc,
            '--n-threads', str(NTHREADS),
            '-s', 'tmp.png',
            '--npts-density', '10000',
            '--dipole-parameter', '0.75',
            '-w', 'coherent',
            '--grid', '6', '6', '6',
            '--temperature', '5']

    if use_brille:
        args += ['--use-brille', '--brille-npts', '10000']

    powder_map(args)

if __name__ == '__main__':
    use_brille_opts = [False, True]
    out_file = f'{get_create_results_path()}/powder_map_cprofile_{int(time.time())}.txt'
    for use_brille in use_brille_opts:
        pr = cProfile.Profile()
        pr.enable()
        main(use_brille=use_brille)
        pr.disable()

        strio = io.StringIO()
        stats = pstats.Stats(pr, stream=strio).sort_stats('tottime')
        stats.print_stats()

        with open(out_file, 'a') as f:
            f.write(f'use_brille={use_brille}\n')
            f.write(strio.getvalue())

    with open(out_file, 'a') as f:
        f.write(inspect.getsource(inspect.getmodule(inspect.currentframe())))