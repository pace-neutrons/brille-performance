import time

from pathlib import Path

from euphonic.cli.powder_map import main as powder_map
from utils import (get_fc_path, get_create_results_path, get_fc_info,
                   fwrite, NTHREADS)


def main():
    out_dir = get_create_results_path()
    n_repeats = 3
    fc_info = get_fc_info()

    args = ['--n-threads', str(NTHREADS), '-s', 'tmp.png', '--npts-density', '10000']
    sf_args = ['-w', 'coherent',
               '--grid', '6', '6', '6',
               '--temperature', '5']

    fobj = open(Path(f'{out_dir}/powder_map_{int(time.time())}.txt'), 'w')
    fwrite(fobj, f'{sf_args} {args} --brille-npts={[fc["sbrille_npts"] for fc in fc_info]} --dipole-parameter={[fc["sdipole_parameter"] for fc in fc_info]}')

    for fc in fc_info:
        fcfile = str(get_fc_path(fc["filename"]))
        fwrite(fobj, f'\n\nMaterial: {fc["filename"]:20}\n')
        # Euphonic only - DOS weighted
        eu_args = [fcfile, *args, '--dipole-parameter', fc["sdipole_parameter"]]
        fwrite(fobj, f'Euphonic DOS-weighted\n')
        powder_map_and_time(eu_args, fobj, n_repeats)
        # Euphonic only - Coherent SF weighted
        fwrite(fobj, f'\nEuphonic SF-weighted\n')
        powder_map_and_time([*eu_args, *sf_args], fobj, n_repeats)

        # Brille - DOS weighted
        bri_args = [*eu_args, '--use-brille', '--brille-npts', fc["sbrille_npts"]]
        fwrite(fobj, f'\nBrille DOS-weighted\n')
        powder_map_and_time(bri_args, fobj, n_repeats)
        # Brille - Coherent SF weighted
        fwrite(fobj, f'\nBrille SF-weighted\n')
        powder_map_and_time([*bri_args, *sf_args], fobj, n_repeats)

    fobj.close()

def powder_map_and_time(powder_map_args, fobj, n_repeats=1):
    for n in range(n_repeats):
        ti = time.time()
        powder_map(powder_map_args)
        tf = time.time()
        fwrite(fobj, f'{tf - ti:10.3f}')
        # Ensure profiling data so far is written even if
        # program crashes and doesn't reach fobj.close()
        fobj.flush()

if __name__ == '__main__':
    main()
