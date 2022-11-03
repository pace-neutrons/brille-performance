from pathlib import Path

from euphonic import __version__ as eu_version
from brille import version as br_version


NTHREADS = 16
PLATFORM = 'windows_i711800H_32GB'


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