import os
import time
import cProfile
import pstats
import io
import inspect

from euphonic.cli.powder_map import main as powder_map
from utils import get_fc_path, get_create_results_path, get_fc_info, NTHREADS

def main(use_brille=False):
    fc_info = get_fc_info()
    fc = fc_info[3] # 3 = AmSulf
    fc_file = str(get_fc_path(fc['filename']))

    args = [fc_file,
            '--n-threads', str(NTHREADS),
            '-s', 'tmp.png',
            '--npts-density', '10000',
            '--dipole-parameter', fc['sdipole_parameter'],
            '-w', 'coherent',
            '--grid', '6', '6', '6',
            '--temperature', '5']

    if use_brille:
        args += ['--use-brille', '--brille-npts', fc['sbrille_npts']]

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
        stats = pstats.Stats(pr, stream=strio).sort_stats('cumtime')
        stats.print_stats()

        with open(out_file, 'a') as f:
            f.write(f'use_brille={use_brille}\n')
            f.write(strio.getvalue())

    with open(out_file, 'a') as f:
        f.write(inspect.getsource(inspect.getmodule(inspect.currentframe())))