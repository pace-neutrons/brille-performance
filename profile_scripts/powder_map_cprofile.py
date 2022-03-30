import os
import time

from euphonic.cli.powder_map import main as powder_map

def main():
    fc_dir = os.path.join('..', 'force_constants')
    fc = os.path.join(fc_dir, 'quartz.castep_bin')

    args = [fc,
            '--n-threads', '30',
            '-s', 'tmp.png',
            '--npts-density', '10000',
            '--dipole-parameter', '0.75',
            '-w', 'coherent',
            '--grid', '6', '6', '6',
            '--temperature', '5']

    # Euphonic only - Coherent SF weighted
    powder_map(args)

    # Brille - Coherent SF weighted
    bri_args = [*args, '--use-brille', '--brille-npts', '10000']
    powder_map(bri_args)

if __name__ == '__main__':
    main()
