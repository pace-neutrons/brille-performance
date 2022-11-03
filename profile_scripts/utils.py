from pathlib import Path

from euphonic import __version__ as eu_version
from brille import version as br_version


NTHREADS = 16
PLATFORM = 'windows_i711800H_32GB'


def get_fc_info():
    fc_info = [create_fc_dict('quartz.castep_bin', '0.75', '10000'),
               create_fc_dict('Nb-181818-s0.5-NCP19-vib-disp.castep_bin', '1.0', '20000'),
               create_fc_dict('La2Zr2O7.castep_bin', '1.0', '5000'),
               create_fc_dict('AmSulf_298K.castep_bin', '0.4', '500')]
    return fc_info

def create_fc_dict(filename, dipole_parameter, brille_npts):
    return {'filename': filename,
            'dipole_parameter': float(dipole_parameter),
            'sdipole_parameter': str(dipole_parameter),
            'brille_npts': int(brille_npts),
            'sbrille_npts': str(brille_npts)}


def get_fc_path(fc_filename):
    """Get path to force constants dir"""
    return Path(f'../force_constants/{fc_filename}')


def get_create_results_path():
    """Get path to results dir """
    path = Path(
        f'../profile_results/{get_version_dirname()}/python/{PLATFORM}')
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_version_dirname():
    """Get results subdir name based on Brille/Euphonic versions"""
    return f'euphonic_{eu_version}_brille_{br_version}'.replace(
        '+', '_')

def fwrite(fobj, string):
    """Write to file and flush to ensure it is written in case of crash"""
    fobj.write(string)
    fobj.flush()