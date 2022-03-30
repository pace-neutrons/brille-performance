import os
import time

from euphonic.cli.powder_map import main as powder_map

def main():
    out_dir = os.path.join('..', 'profile_results', 'python', 'idaaas')
    fc_dir = os.path.join('..', 'force_constants')
    n_repeats = 3
    fcs = ['quartz.castep_bin',
           'Nb-181818-s0.5-NCP19-vib-disp.castep_bin']
    materials = ['quartz', 'Nb']

    args = ['--n-threads', '30', '-s', 'tmp.png', '--npts-density', '10000']
    sf_args = ['-w', 'coherent',
               '--grid', '6', '6', '6',
               '--temperature', '5']
    brille_npts = ['10000', '20000']
    dipole_params = ['0.75', '1.0']

    fobj = open(os.path.join(out_dir, f'powder_map_{int(time.time())}.txt'), 'w')
    fobj.write(f'{sf_args} {args} --brille-npts={brille_npts} --dipole-parameter={dipole_params}')

    for i, fc in enumerate(fcs):
        fci = os.path.join(fc_dir, fc)
        fobj.write(f'\n\nMaterial: {materials[i]:10}\n')
        # Euphonic only - DOS weighted
        eu_args = [fci, *args, '--dipole-parameter', dipole_params[i]]
        fobj.write(f'Euphonic DOS-weighted\n')
        powder_map_and_time(eu_args, fobj, n_repeats)
        # Euphonic only - Coherent SF weighted
        fobj.write(f'\nEuphonic SF-weighted\n')
        powder_map_and_time([*eu_args, *sf_args], fobj, n_repeats)

        # Brille - DOS weighted
        bri_args = [*eu_args, '--use-brille', '--brille-npts', brille_npts[i]]
        fobj.write(f'\nBrille DOS-weighted\n')
        powder_map_and_time(bri_args, fobj, n_repeats)
        # Brille - Coherent SF weighted
        fobj.write(f'\nBrille SF-weighted\n')
        powder_map_and_time([*bri_args, *sf_args], fobj, n_repeats)

    fobj.close()

def powder_map_and_time(powder_map_args, fobj, n_repeats=1):
    for n in range(n_repeats):
        ti = time.time()
        powder_map(powder_map_args)
        tf = time.time()
        fobj.write(f'{tf - ti:10.3f}')
        # Ensure profiling data so far is written even if
        # program crashes and doesn't reach fobj.close()
        fobj.flush()

if __name__ == '__main__':
    main()
